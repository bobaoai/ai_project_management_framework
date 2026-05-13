"""Per-class matrix from contract §4.2 + validate_object().

Each class declares one of three states per role:
    REQ — must appear (any storage allowed by §5.1)
    OPT — may appear; if it does, role × storage must obey §5.1
    FORBIDDEN — must not appear; appearance triggers UnauthorizedTimestampField

Matrix is hardcoded from §4.2. New class entries here MUST be added in lockstep with
the contract — R2 says "未登记 class 不允许写入任何 schema".
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Mapping

from .exceptions import (
    MalformedTimestampFieldName,
    MissingRequiredTimestamp,
    UnauthorizedTimestampField,
)
from .parse import split_field_name
from .roles import Role


class Tristate(str, Enum):
    REQ = "REQ"
    OPT = "OPT"
    FORBIDDEN = "—"


REQ = Tristate.REQ
OPT = Tristate.OPT
FORBIDDEN = Tristate.FORBIDDEN


def _row(**overrides: Tristate) -> Mapping[Role, Tristate]:
    """Build a matrix row defaulting every role to FORBIDDEN unless overridden."""
    row = {role: FORBIDDEN for role in Role}
    for canonical, state in overrides.items():
        # Accept canonical names like 'observed_at' / 'horizon_date' for readability.
        role = _canonical_lookup(canonical)
        row[role] = state
    return row


def _canonical_lookup(canonical: str) -> Role:
    for role in Role:
        if role.canonical == canonical:
            return role
    raise KeyError(f"unknown role canonical name: {canonical!r}")


# §4.2 Archive layer — updated_at must remain FORBIDDEN (R4).
PER_CLASS_MATRIX: Mapping[str, Mapping[Role, Tristate]] = {
    "tick": _row(observed_at=REQ, recorded_at=REQ),
    "kbar_*": _row(period_start_at=REQ, period_end_at=REQ, recorded_at=REQ),
    "fundamentals_snapshot": _row(
        period_start_at=REQ, period_end_at=REQ, recorded_at=REQ
    ),
    "fed_statement": _row(
        observed_at=REQ, effective_at=OPT, recorded_at=REQ, horizon_date=REQ
    ),
    "fed_speech": _row(observed_at=REQ, recorded_at=REQ, horizon_date=OPT),
    "fomc_vote": _row(observed_at=REQ, effective_at=REQ, recorded_at=REQ),
    "fomc_meeting": _row(
        observed_at=OPT, period_start_at=REQ, period_end_at=REQ, recorded_at=REQ
    ),
    "fed_appointment.term": _row(
        effective_at=REQ, expiry_date=REQ, recorded_at=REQ
    ),
    "research_note": _row(observed_at=REQ, recorded_at=REQ, horizon_date=OPT),
    "archive_message": _row(observed_at=OPT, recorded_at=REQ),
    "source_read_content": _row(recorded_at=REQ),
    "image_review": _row(recorded_at=REQ, horizon_date=OPT),
    "freshness_event": _row(recorded_at=REQ),
    "perplexity_log": _row(observed_at=OPT, recorded_at=REQ),
    # §4.2 Overlay layer — updated_at REQ or OPT.
    "path_observation": _row(
        observed_at=REQ, recorded_at=REQ, updated_at=REQ, scheduled_for_at=OPT
    ),
    "evidence_record": _row(observed_at=OPT, recorded_at=REQ, updated_at=REQ),
    "thesis_note": _row(
        recorded_at=REQ, updated_at=REQ, horizon_date=REQ, scheduled_for_at=REQ
    ),
    "scenario_note": _row(
        recorded_at=REQ, updated_at=REQ, horizon_date=REQ, scheduled_for_at=REQ
    ),
    "theme.metadata": _row(
        recorded_at=REQ, updated_at=REQ, horizon_date=OPT, scheduled_for_at=REQ
    ),
    "theme_report": _row(
        period_start_at=OPT,
        period_end_at=OPT,
        recorded_at=REQ,
        updated_at=OPT,
        horizon_date=OPT,
    ),
    "portfolio_decision": _row(recorded_at=REQ),
    "asset_technical_packet": _row(recorded_at=REQ),
    "asset_technical_report": _row(recorded_at=REQ),
    "writer_package": _row(
        period_start_at=OPT,
        period_end_at=OPT,
        recorded_at=REQ,
        horizon_date=OPT,
    ),
}


def validate_object(obj: Mapping[str, Any], class_name: str) -> None:
    """Validate `obj`'s timestamp fields against the §4 matrix row for `class_name`.

    Raises:
        KeyError: class_name not registered (R2).
        MalformedTimestampFieldName: a candidate field has bad name shape.
        UnauthorizedTimestampField: field role is FORBIDDEN for this class.
        MissingRequiredTimestamp: a REQ role has no field in `obj`.

    Only top-level keys are inspected; nested objects must be validated separately
    by their own class_name (per §4.3 dot-path registration).
    """
    if class_name not in PER_CLASS_MATRIX:
        raise KeyError(
            f"class {class_name!r} not registered in §4 matrix; "
            "R2 requires registration before any schema/object writes"
        )
    row = PER_CLASS_MATRIX[class_name]

    seen_roles: set = set()
    for field_name in obj.keys():
        # Heuristic: only fields ending in a known storage suffix are timestamp fields.
        if not _looks_like_timestamp_field(field_name):
            continue
        try:
            role, _storage = split_field_name(field_name)
        except MalformedTimestampFieldName:
            raise
        state = row[role]
        if state is FORBIDDEN:
            raise UnauthorizedTimestampField(
                f"{class_name!r} forbids role {role.canonical} but field "
                f"{field_name!r} present"
            )
        seen_roles.add(role)

    for role, state in row.items():
        if state is REQ and role not in seen_roles:
            raise MissingRequiredTimestamp(
                f"{class_name!r} requires role {role.canonical} but no matching "
                "field present"
            )


_KNOWN_SUFFIXES = (
    "_at_utc",
    "_calendar_day_utc",
    "_session_date_et",
    "_session_date_ct",
    "_session_date_market",
)


def _looks_like_timestamp_field(field_name: str) -> bool:
    return any(field_name.endswith(s) for s in _KNOWN_SUFFIXES)
