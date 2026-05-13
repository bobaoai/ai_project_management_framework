"""Exceptions defined by the_timestamp_semantic.md §0 R3 / R4 / charter §IV."""


class TimestampError(Exception):
    """Base for all timekeeping contract violations."""


class TimestampSemanticsMismatch(TimestampError):
    """Two timestamps with incompatible role/storage compared or operated on.

    Charter §IV fail-loud: cross-role / cross-storage comparison must raise, never
    silently coerce.
    """


class UnauthorizedTimestampField(TimestampError):
    """Field present in schema/object but §4 matrix marks the role as forbidden (—)."""


class MissingRequiredTimestamp(TimestampError):
    """Field marked REQ in §4 matrix but missing from schema/object."""


class MalformedTimestampFieldName(TimestampError):
    """Field name does not match `<role>_<storage>` naming convention.

    Triggered for bare names (`report_date`, `as_of`, `timestamp`), unknown role
    tokens, unknown storage suffixes, or role/storage combos that §5.1 forbids
    (e.g. `expiry_at_utc`, `horizon_at_utc`).
    """
