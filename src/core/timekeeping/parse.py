"""Field-name parsing per contract §2 / §5.

`parse_field(field_name, value)` →
    (Role, Storage, typed_wrapper)

Splits longest-matching storage suffix off the right; what remains must be a known
Role token; the role × storage combo must be allowed by §5.1.

`split_field_name(field_name)` returns just (Role, Storage), no value parsing —
useful for schema linters and tests that only care about the name shape.
"""

from __future__ import annotations

from typing import Any, Optional, Tuple

from .calendar_dates import CalendarDayUtc
from .exceptions import MalformedTimestampFieldName, TimestampSemanticsMismatch
from .instants import InstantUtc
from .roles import ALLOWED_COMBOS, Role, Storage
from .sessions import SessionDateCt, SessionDateEt, SessionDateMarket

# Order matters: try longest suffix first so `_session_date_market` doesn't get
# misread as `_session_date_*`.
_STORAGE_SUFFIXES_ORDERED = [
    Storage.SESSION_DATE_MARKET,
    Storage.SESSION_DATE_ET,
    Storage.SESSION_DATE_CT,
    Storage.CALENDAR_DAY_UTC,
    Storage.AT_UTC,
]


def split_field_name(field_name: str) -> Tuple[Role, Storage]:
    if not isinstance(field_name, str) or not field_name:
        raise MalformedTimestampFieldName(
            f"field name must be non-empty str; got {field_name!r}"
        )

    matched_storage: Optional[Storage] = None
    role_token: Optional[str] = None
    for storage in _STORAGE_SUFFIXES_ORDERED:
        suffix = "_" + storage.value
        if field_name.endswith(suffix):
            prefix = field_name[: -len(suffix)]
            if prefix:
                matched_storage = storage
                role_token = prefix
                break

    if matched_storage is None or role_token is None:
        raise MalformedTimestampFieldName(
            f"field {field_name!r} does not match `<role>_<storage>` form; "
            f"valid storages: {[s.value for s in _STORAGE_SUFFIXES_ORDERED]}"
        )

    try:
        role = Role(role_token)
    except ValueError as exc:
        raise MalformedTimestampFieldName(
            f"field {field_name!r} has unknown role token {role_token!r}; "
            f"valid roles: {[r.value for r in Role]}"
        ) from exc

    if matched_storage not in ALLOWED_COMBOS[role]:
        raise MalformedTimestampFieldName(
            f"field {field_name!r}: role {role.canonical} cannot use storage "
            f"{matched_storage.value} per §5.1; allowed: "
            f"{sorted(s.value for s in ALLOWED_COMBOS[role])}"
        )

    return role, matched_storage


def parse_field(
    field_name: str,
    value: Any,
    *,
    market_tz: Optional[str] = None,
) -> Tuple[Role, Storage, Any]:
    role, storage = split_field_name(field_name)
    typed = _parse_value(storage, value, market_tz=market_tz, field_name=field_name)
    return role, storage, typed


def _parse_value(
    storage: Storage,
    value: Any,
    *,
    market_tz: Optional[str],
    field_name: str,
) -> Any:
    if storage is Storage.AT_UTC:
        return InstantUtc.parse(value) if isinstance(value, str) else InstantUtc(value)
    if storage is Storage.CALENDAR_DAY_UTC:
        return CalendarDayUtc(value)
    if storage is Storage.SESSION_DATE_ET:
        return SessionDateEt(value)
    if storage is Storage.SESSION_DATE_CT:
        return SessionDateCt(value)
    if storage is Storage.SESSION_DATE_MARKET:
        if not market_tz:
            raise TimestampSemanticsMismatch(
                f"field {field_name!r} uses session_date_market storage but no "
                "market_tz sibling supplied"
            )
        return SessionDateMarket(value, market_tz=market_tz)
    raise MalformedTimestampFieldName(
        f"unhandled storage {storage!r} for field {field_name!r}"
    )
