"""Freeze the reviewed code and declared commands as one Runtime resource file.

An implementation review gives the Reviewer the exact changed files on both
sides of the commit, the exact diff and any explicitly requested unchanged
files, all read from Git objects, never from the working tree. Declared
commands become the Runtime commands of the same review, so the Reviewer input
and what Runtime can execute come from one declaration. Runtime validates the
resource file against its own rules when the review starts.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path, PurePosixPath
import stat
from typing import Mapping, Sequence

from software_delivery.engineering_review_input import _run_git


_REGULAR_MODES = frozenset({"100644", "100755"})


def _require_regular_mode(path: str, mode: str) -> None:
    if mode not in _REGULAR_MODES:
        raise ValueError(f"Cannot freeze {path}: unsupported Git mode {mode}; "
                         "only regular files (100644, 100755) are supported")


def _relative(value: str) -> str:
    path = PurePosixPath(value)
    if (not value or "\\" in value or "\x00" in value or path.is_absolute()
            or any(part in {"", ".", ".."} for part in value.split("/"))):
        raise ValueError(f"--read path must be a normalized repository-relative path: {value!r}")
    return value


def _tree(root: Path, revision: str) -> tuple[dict[str, str], tuple[bytes, ...]]:
    """Map each UTF-8 leaf path to its Git mode; list the other paths as bytes.

    Only selected paths must be UTF-8: changed paths already are (the review
    subject requires it), and a --read selection that contains another path is
    refused. Keep symlinks and gitlinks in the inventory so selection can reject
    them explicitly. Unselected paths never block the review.
    """
    rows = _run_git(root, "ls-tree", "-r", "-z", "--full-tree", revision).split(b"\0")
    entries, undecodable = {}, []
    for row in rows:
        if not row:
            continue
        meta, path = row.split(b"\t", 1)
        mode, _kind, _oid = meta.decode("ascii").split(" ")
        try:
            entries[path.decode("utf-8")] = mode
        except UnicodeDecodeError:
            undecodable.append(path)
    return entries, tuple(undecodable)


def _write(root: Path, revision: str, path: str, target: Path, mode: str) -> bytes:
    """Write one Git blob with the permission its Git mode states; Runtime checks both."""
    body = _run_git(root, "show", f"{revision}:{path}")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(body)
    target.chmod(0o755 if mode == "100755" else 0o644)
    return body


def _object_id(root: Path, target: Path) -> str:
    return _run_git(root, "hash-object", "--no-filters", "--", str(target)).decode("ascii").strip()


def verify_materials(root: Path, subject: Mapping[str, object], materials: Path, read_files: Sequence[str]) -> None:
    """Check every frozen file against the review subject or its Git object; raise ValueError on any mismatch.

    added/modified commit-side files and deleted parent-side files must match
    the subject's content_sha256; modified parent-side files and --read files
    have no SHA-256 in the subject and must match their Git object ID.
    Selected Git entries and frozen leaves must be regular files, with the
    executable state preserved independently of the content hash.
    """
    commit, parent = subject["commit_ref"], subject["parent_ref"]
    trees = {"commit": _tree(root, commit)[0], "parent": _tree(root, parent)[0]}

    def checked_path(side, path):
        relative = f"{side}/{path}"
        mode = trees[side][path]
        _require_regular_mode(relative, mode)
        target = materials / relative
        actual = target.lstat().st_mode
        if not stat.S_ISREG(actual) or bool(actual & 0o111) != (mode == "100755"):
            raise ValueError(f"frozen file type or executable mode differs from Git: {relative}")
        return target

    for row in subject["paths"]:
        path, state = row["path"], row["state"]
        side = "parent" if state == "deleted" else "commit"
        if hashlib.sha256(checked_path(side, path).read_bytes()).hexdigest() != row["content_sha256"]:
            raise ValueError(f"frozen {side} file differs from the review subject: {path}")
        if state == "modified":
            expected = _run_git(root, "rev-parse", f"{parent}:{path}").decode("ascii").strip()
            if _object_id(root, checked_path("parent", path)) != expected:
                raise ValueError(f"frozen parent file differs from its Git object: {path}")
    for path in read_files:
        expected = _run_git(root, "rev-parse", f"{commit}:{path}").decode("ascii").strip()
        if _object_id(root, checked_path("commit", path)) != expected:
            raise ValueError(f"frozen --read file differs from its Git object: {path}")
    diff = (materials / "candidate.diff").read_bytes()
    if hashlib.sha256(diff).hexdigest() != subject["diff_sha256"]:
        raise ValueError("frozen diff differs from the review subject")


def write_review_resources(*, payload: Mapping[str, object], repository_root: Path | None,
                           read_paths: Sequence[str], commands: Sequence[Mapping[str, object]],
                           dependencies: Sequence[Path], target: Path) -> Path | None:
    """Write the Runtime resource file for one Engineering review under target; return its path.

    Returns None when there is nothing to provide: a plan review without
    declared commands. --read needs an implementation review. Each command's
    command_id, argv, cwd and timeout_seconds are copied unchanged.
    Selected entries must be regular Git files (100644 or 100755). Other modes,
    including symlinks and submodules, are refused before any materials are
    written; the Runtime resource format cannot preserve their semantics.
    """
    implementation = payload["review_purpose"] == "implementation"
    if read_paths and not implementation:
        raise ValueError("--read provides code from the reviewed commit and needs an implementation review")
    if not implementation and not commands and not dependencies:
        return None
    materials = Path(target) / "materials"
    files: dict[str, str] = {}
    read_files: list[str] = []
    if implementation:
        root = Path(repository_root).resolve(strict=True)
        subject = payload["subject"]
        commit, parent = subject["commit_ref"], subject["parent_ref"]
        (commit_tree, commit_undecodable), (parent_tree, _) = _tree(root, commit), _tree(root, parent)
        changed = set()
        for row in subject["paths"]:
            path, state = row["path"], row["state"]
            changed.add(path)
            if state in {"added", "modified"}:
                files["commit/" + path] = commit_tree[path]
            if state in {"modified", "deleted"}:
                files["parent/" + path] = parent_tree[path]
        for value in read_paths:
            path = _relative(value)
            prefix = path.encode("utf-8")
            if any(item == prefix or item.startswith(prefix + b"/") for item in commit_undecodable):
                raise ValueError(f"--read selection contains a path that is not UTF-8: {path}")
            selected = [item for item in commit_tree if item == path or item.startswith(path + "/")]
            if not selected:
                raise ValueError(f"--read path is not in the reviewed commit: {path}")
            for item in selected:
                if item in changed or "commit/" + item in files:
                    continue
                files["commit/" + item] = commit_tree[item]
                read_files.append(item)
        for path, mode in files.items():
            _require_regular_mode(path, mode)
        materials.mkdir(parents=True)
        for relative, mode in files.items():
            side, path = relative.split("/", 1)
            _write(root, commit if side == "commit" else parent, path, materials / relative, mode)
        diff = _run_git(root, "diff", "--binary", "--no-ext-diff", "--no-renames", parent, commit, "--")
        (materials / "candidate.diff").write_bytes(diff)
        files["candidate.diff"] = "100644"
        verify_materials(root, subject, materials, read_files)
    else:
        materials.mkdir(parents=True)
    resource = {
        "material_root": "materials" if files else None,
        "material_files": [{"relative_path": path,
                            "sha256": hashlib.sha256((materials / path).read_bytes()).hexdigest(),
                            "executable": files[path] == "100755"} for path in sorted(files)],
        "read_only_dependencies": [str(Path(item)) for item in dependencies],
        "commands": [{key: row[key] for key in ("command_id", "argv", "cwd", "timeout_seconds")} for row in commands],
    }
    path = Path(target) / "resources.json"
    path.write_text(json.dumps(resource, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return path


__all__ = ["verify_materials", "write_review_resources"]
