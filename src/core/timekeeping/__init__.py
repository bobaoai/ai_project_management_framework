"""Timekeeping authority — repo-wide enforcement of the_timestamp_semantic.md.

Phase 1: typed wrappers (InstantUtc / SessionDate* / CalendarDayUtc), 9-role × 5-storage
parser, role-aware comparison, per-class matrix registry. No storage migration yet —
that is Phase 3. Scanner is Phase 2.
"""

from .exceptions import (
    TimestampError,
    TimestampSemanticsMismatch,
    UnauthorizedTimestampField,
    MissingRequiredTimestamp,
    MalformedTimestampFieldName,
)
from .roles import Role, Storage, ALLOWED_COMBOS, POINT_ROLES, INTERVAL_ROLES, DATE_ROLES
from .instants import InstantUtc
from .sessions import SessionDateEt, SessionDateCt, SessionDateMarket
from .calendar_dates import CalendarDayUtc
from .parse import parse_field, split_field_name
from .compare import assert_compatible, gt, lt, eq
from .registry import (
    PER_CLASS_MATRIX,
    Tristate,
    REQ,
    OPT,
    FORBIDDEN,
    validate_object,
)

__all__ = [
    "TimestampError",
    "TimestampSemanticsMismatch",
    "UnauthorizedTimestampField",
    "MissingRequiredTimestamp",
    "MalformedTimestampFieldName",
    "Role",
    "Storage",
    "ALLOWED_COMBOS",
    "POINT_ROLES",
    "INTERVAL_ROLES",
    "DATE_ROLES",
    "InstantUtc",
    "SessionDateEt",
    "SessionDateCt",
    "SessionDateMarket",
    "CalendarDayUtc",
    "parse_field",
    "split_field_name",
    "assert_compatible",
    "gt",
    "lt",
    "eq",
    "PER_CLASS_MATRIX",
    "Tristate",
    "REQ",
    "OPT",
    "FORBIDDEN",
    "validate_object",
]
