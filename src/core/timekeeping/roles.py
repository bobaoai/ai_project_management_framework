"""9-role × 5-storage taxonomy from contract §3 / §5.

Field name pattern: `<role_token>_<storage_suffix>`. Role token drops the canonical
`_at` / `_date` tail because the storage suffix carries that semantics
(e.g. `observed_at_utc` = role token `observed` + storage suffix `at_utc`).
"""

from __future__ import annotations

from enum import Enum
from typing import Mapping, Set


class Role(str, Enum):
    """9 roles per contract §3. Value = field-name token (no `_at` / `_date` tail)."""

    OBSERVED = "observed"
    PERIOD_START = "period_start"
    PERIOD_END = "period_end"
    EFFECTIVE = "effective"
    EXPIRY = "expiry"
    RECORDED = "recorded"
    UPDATED = "updated"
    HORIZON = "horizon"
    SCHEDULED_FOR = "scheduled_for"

    @property
    def canonical(self) -> str:
        """Canonical taxonomy name as used in §4 matrix headers."""
        return _ROLE_CANONICAL[self]


class Storage(str, Enum):
    """5 storage suffixes per contract §5. Value = suffix without leading underscore."""

    AT_UTC = "at_utc"
    CALENDAR_DAY_UTC = "calendar_day_utc"
    SESSION_DATE_ET = "session_date_et"
    SESSION_DATE_CT = "session_date_ct"
    SESSION_DATE_MARKET = "session_date_market"


_ROLE_CANONICAL: Mapping[Role, str] = {
    Role.OBSERVED: "observed_at",
    Role.PERIOD_START: "period_start_at",
    Role.PERIOD_END: "period_end_at",
    Role.EFFECTIVE: "effective_at",
    Role.EXPIRY: "expiry_date",
    Role.RECORDED: "recorded_at",
    Role.UPDATED: "updated_at",
    Role.HORIZON: "horizon_date",
    Role.SCHEDULED_FOR: "scheduled_for_at",
}

POINT_ROLES: Set[Role] = {Role.OBSERVED, Role.RECORDED, Role.UPDATED, Role.SCHEDULED_FOR}
INTERVAL_ROLES: Set[Role] = {Role.PERIOD_START, Role.PERIOD_END}
DATE_ROLES: Set[Role] = {Role.EFFECTIVE, Role.EXPIRY, Role.HORIZON}

_SESSION_STORAGES: Set[Storage] = {
    Storage.SESSION_DATE_ET,
    Storage.SESSION_DATE_CT,
    Storage.SESSION_DATE_MARKET,
}

# §5.1 — point/interval roles primarily _at_utc, also session storages.
# Date roles use calendar_day_utc / session_date_*; only `effective` additionally
# accepts `_at_utc` per §5: "精确到点用 `effective_at_utc`".
ALLOWED_COMBOS: Mapping[Role, Set[Storage]] = {
    Role.OBSERVED: {Storage.AT_UTC, *_SESSION_STORAGES},
    Role.RECORDED: {Storage.AT_UTC, *_SESSION_STORAGES},
    Role.UPDATED: {Storage.AT_UTC, *_SESSION_STORAGES},
    Role.SCHEDULED_FOR: {Storage.AT_UTC, *_SESSION_STORAGES},
    Role.PERIOD_START: {Storage.AT_UTC, *_SESSION_STORAGES},
    Role.PERIOD_END: {Storage.AT_UTC, *_SESSION_STORAGES},
    Role.EFFECTIVE: {Storage.AT_UTC, Storage.CALENDAR_DAY_UTC, *_SESSION_STORAGES},
    Role.EXPIRY: {Storage.CALENDAR_DAY_UTC, *_SESSION_STORAGES},
    Role.HORIZON: {Storage.CALENDAR_DAY_UTC, *_SESSION_STORAGES},
}


def canonical_to_role(canonical_name: str) -> Role:
    """Map a canonical role name (§4 matrix header form) back to the Role enum."""
    for role, name in _ROLE_CANONICAL.items():
        if name == canonical_name:
            return role
    raise KeyError(f"unknown canonical role name: {canonical_name!r}")
