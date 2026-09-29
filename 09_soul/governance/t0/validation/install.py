"""Copy Portable Governance into a new or explicitly updated directory.

This is a filesystem installation, not release admission or project bootstrap.
Only trusted local source checkouts are supported: existing validators may load
the package's registered Python adapters. Invalid packages remain inspectable.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import hashlib
import importlib.util
import json
from pathlib import Path
import sys


def _load(stem):
    name = f"{__name__}_{stem}"
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(stem + ".py"))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


t0 = _load("t0_release")
skills = _load("skill_release")
PACKAGE = Path("09_soul/governance")
MANIFESTS = (t0.MANIFEST_RELATIVE_PATH, skills.MANIFEST_RELATIVE_PATH)
# The fresh-install entry names this default orchestration method when the package ships it.
ORCHESTRATION_SKILL_ID = "paseo-orchestrator"


def _package_files(root):
    folder = t0._resolve_without_symlink_escape(root, PACKAGE.as_posix())
    paths = set()
    for path in folder.rglob("*"):
        relative = path.relative_to(root)
        if {"__pycache__", ".pytest_cache"}.intersection(relative.parts):
            continue
        if path.is_symlink():
            raise ValueError(f"package symlink is not supported: {relative}")
        if path.is_file():
            paths.add(relative.as_posix())
        elif not path.is_dir():
            raise ValueError(f"package member is not a regular file or directory: {relative}")
    return paths


def _check_update_targets(target: Path, paths) -> None:
    """Check only selected copy paths before overwriting an existing installation."""
    for relative in paths:
        output = t0._resolve_without_symlink_escape(target, relative)
        if output.is_symlink() or (output.exists() and not output.is_file()):
            raise ValueError(f"copy target is not a regular file: {relative}")
        for parent in output.parents:
            if parent == target:
                break
            if parent.is_symlink() or (parent.exists() and not parent.is_dir()):
                raise ValueError(f"copy target parent is not a directory: {relative}")


def install_governance(source_root: Path, target_root: Path, *, update: bool = False) -> dict:
    """Copy the captured package, declared dependencies and projections.

    source_root supplies trusted local Portable files and their existing manifests.
    target_root must be new by default; update=True requires an existing directory.
    Update replaces only selected Portable files, preserves host entry/configuration
    files, and uses the existing Skill projector to retain registered local addenda.
    Selected target paths are checked before overwrite; individual file replacement
    is atomic, but a later failure may leave a partially updated installation.
    Fix the reported problem and repeat with the same source to finish copying.

    Returns the existing installation/check report. file_count counts selected copy
    and projection paths, excluding preserved host entries during update. Raises
    ValueError or OSError for invalid inputs, paths, copying or projection failures.
    Never repairs manifests, deletes stale files, registers Runtime objects or
    accesses a database/provider. Package check failures remain visible in the report.
    """
    source = Path(source_root).resolve()
    target = Path(target_root)
    if update:
        if target.is_symlink() or not target.is_dir():
            raise ValueError("update target must be an existing directory")
    elif target.exists() or target.is_symlink():
        raise ValueError("target must be a new directory")
    target = target.resolve()
    if not target.parent.is_dir():
        raise ValueError("target parent directory must already exist")
    if target == source or target.is_relative_to(source / "09_soul"):
        raise ValueError("target must not modify the source package")

    manifest_bytes = {
        p.as_posix(): t0._resolve_without_symlink_escape(source, p.as_posix()).read_bytes()
        for p in MANIFESTS
    }
    tm = t0.load_governance_t0_manifest(source)
    sm = skills.load_governance_skill_manifest(source)
    projections = [(row.source, row.target) for row in tm.portable_t0_contracts]
    skill_targets = set()
    dependencies = {r.source for r in sm.instruction_resources}
    for skill in sm.portable_governance_skills:
        for identity in skill.required_soul_resource_ids:
            dependencies.add(skills.SOUL_RESOURCE_PATHS[identity].as_posix())
        for item in skill.package_files:
            dependencies.add(item.source)
            projections.extend((item.source, p.target) for p in item.projections)
            skill_targets.update(p.target for p in item.projections)
    dependencies.update(row.source for row in tm.portable_t0_contracts)
    for row in tm.artifact_contracts:
        dependencies.update((row.source, row.adapter))

    package_files = _package_files(source)
    paths = package_files | dependencies
    captured = {
        path: t0._resolve_without_symlink_escape(source, path).read_bytes()
        for path in sorted(paths)
    }
    if any(captured[path] != body for path, body in manifest_bytes.items()):
        raise ValueError("source manifests changed while preparing installation")
    if _package_files(source) != package_files or any(
        t0._resolve_without_symlink_escape(source, path).read_bytes() != body
        for path, body in captured.items()
    ):
        raise ValueError("source changed while preparing installation")

    payloads = dict(captured)
    for source_path, target_path in projections:
        if target_path in payloads:
            raise ValueError(f"installation paths overlap: {target_path}")
        payloads[target_path] = captured[source_path]
    routing = next((r.target for r in tm.portable_t0_contracts if r.t0_layer_id == "the_task_routing"), None)
    entry = "# Portable Governance\n\n先读取 `09_soul/governance/README.md`，按包内规则处理任务。\n"
    if routing:
        entry += f"新任务的工作入口由 `{routing}` 与相应 Skill 说明。\n"
    orchestration = next((s for s in sm.portable_governance_skills if s.skill_id == ORCHESTRATION_SKILL_ID), None)
    if orchestration:
        # Only the package-root SKILL.md is the entry; a nested references/SKILL.md is an ordinary resource.
        root_skill = (skills.SOURCE_PREFIX / orchestration.skill_id / "SKILL.md").as_posix()
        hosts = {p.host_id: p.target for f in orchestration.package_files
                 if f.source == root_skill for p in f.projections}
        name = orchestration.skill_id
        entry += (
            f"\n直接承接用户完整项目任务的 Primary Agent 按默认编排方法统筹委派："
            f"Claude Code 读 [{name}]({hosts['claude']})，Codex 读 [{name}]({hosts['codex']})。\n"
            "受委派执行任务的会话直接完成交给它的任务，不再委派。\n"
        )
    if not update:
        payloads["CLAUDE.md"] = entry.encode("utf-8")
        payloads["AGENTS.md"] = b"Read and follow CLAUDE.md first.\n"

    hashes = {path: hashlib.sha256(body).hexdigest() for path, body in captured.items()}
    source_hash = hashlib.sha256(json.dumps(hashes, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    if update:
        _check_update_targets(target, payloads)
    else:
        target.mkdir()  # Fails if another process created the destination; no exist_ok.
    for path, body in payloads.items():
        if update and path in skill_targets:
            continue  # The existing projector composes target-local addenda below.
        output = t0._resolve_without_symlink_escape(target, path)
        if update:
            skills._write_bytes_atomically(output, body)
        else:
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("xb") as stream:
                stream.write(body)
    if update:
        skills.apply_governance_skill_release(target)

    checks = {}
    project_requirements = []
    for label, check in (("t0", t0.check_governance_t0_release), ("skill", skills.check_governance_skill_release)):
        try:
            result = check(target)
            issues = []
            for issue in result.issues:
                if label == "t0" and issue.code == "project_charter_missing":
                    project_requirements.append(asdict(issue))
                else:
                    issues.append(asdict(issue))
            checks[label] = {"passed": not issues, "issues": issues}
        except (OSError, ValueError) as exc:
            checks[label] = {"passed": False, "error": str(exc)}
    return {
        "installed": True, "target_root": str(target), "source_sha256": source_hash,
        "file_count": len(payloads), "t0_count": len(tm.portable_t0_contracts),
        "skill_count": len(sm.portable_governance_skills), "checks": checks,
        "package_checks_passed": all(c["passed"] for c in checks.values()),
        "project_requirements": project_requirements,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="复制可信 Portable Governance；默认安装到新目录，--update 更新已有目录。不初始化 Runtime。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "示例（使用项目配置的 Python）：\n"
            "  安装到新目录，来源默认是本脚本所在工作区：\n"
            "    python -B 09_soul/governance/t0/validation/install.py --target-root /path/to/new-workspace\n"
            "  从指定来源更新已有目录：\n"
            "    python -B 09_soul/governance/t0/validation/install.py --source-root /path/to/source --target-root /path/to/existing-workspace --update\n"
            "\n范围：\n"
            "  源与目标须不同；目标不能位于来源的 09_soul 内。\n"
            "  更新保留宿主 CLAUDE.md、AGENTS.md、Charter、配置、业务文件和 .runtime，\n"
            "  并保留已声明的 Skill 本地附加说明；不删除旧文件、不补写 manifest。\n"
            "  只复制和检查文件，不注册 Runtime 对象，不连接数据库或调用模型。\n"
            "\n退出码：\n"
            "  0  复制和包检查均通过。\n"
            "  1  复制完成，但包检查未通过；查看 JSON 中的 checks。\n"
            "  2  参数、来源、路径、复制或投影失败；目标可能已部分写入。\n"
            "\n失败恢复：\n"
            "  先根据错误修正来源或目标问题。目标已产生部分文件时，\n"
            "  使用同一 source-root 和 target-root 加 --update 重试；不会自动回滚。"
        ),
    )
    parser.add_argument("--source-root", type=Path, default=Path(__file__).resolve().parents[4], help="包含 09_soul/governance 的目录；省略时使用本脚本所在工作区，不是当前工作目录")
    parser.add_argument("--target-root", type=Path, required=True, help="目标目录；默认须不存在且父目录存在，--update 时须为已有目录")
    parser.add_argument("--update", action="store_true", help="覆盖选定 Portable 文件，保留宿主入口和配置；不删除旧文件")
    args = parser.parse_args(argv)
    try:
        report = install_governance(args.source_root, args.target_root, update=args.update)
    except (OSError, ValueError, KeyError) as exc:
        print(json.dumps({"installed": False, "target_root": str(args.target_root), "error": str(exc),
                          "message": "复制未完成；目标可能已部分写入，保留供诊断。修正问题后可用同一来源重试，不自动删除或回滚。"}, ensure_ascii=False))
        return 2
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["package_checks_passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
