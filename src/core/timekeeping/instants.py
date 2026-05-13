"""InstantUtc — typed wrapper for `_at_utc` storage (contract §5)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .exceptions import TimestampSemanticsMismatch


@dataclass(frozen=True)
class InstantUtc:
    """Wall-clock instant in UTC. Pairs with any role using `_at_utc` storage."""

    dt: datetime

    def __post_init__(self) -> None:
        if self.dt.tzinfo is None:
            raise TimestampSemanticsMismatch(
                "InstantUtc requires tz-aware datetime; got naive"
            )
        if self.dt.utcoffset() != timedelta(0):
            raise TimestampSemanticsMismatch(
                f"InstantUtc must be in UTC; got offset {self.dt.utcoffset()}"
            )

    @classmethod
    def parse(cls, value: str) -> "InstantUtc":
        if not isinstance(value, str):
            raise TimestampSemanticsMismatch(
                f"InstantUtc.parse expects str, got {type(value).__name__}"
            )
        s = value
        if s.endswith("Z"):
            s = s[:-1] + "+00:00"
        try:
            dt = datetime.fromisoformat(s)
        except ValueError as exc:
            raise TimestampSemanticsMismatch(
                f"InstantUtc.parse cannot decode {value!r}: {exc}"
            ) from exc
        if dt.tzinfo is None:
            raise TimestampSemanticsMismatch(
                f"InstantUtc.parse requires tz-aware ISO 8601; got naive {value!r}"
            )
        return cls(dt.astimezone(timezone.utc))

    def to_iso(self) -> str:
        return self.dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, InstantUtc):
            raise TimestampSemanticsMismatch(
                f"cannot compare InstantUtc with {type(other).__name__}"
            )
        return self.dt < other.dt

    def __le__(self, other: object) -> bool:
        if not isinstance(other, InstantUtc):
            raise TimestampSemanticsMismatch(
                f"cannot compare InstantUtc with {type(other).__name__}"
            )
        return self.dt <= other.dt

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, InstantUtc):
            raise TimestampSemanticsMismatch(
                f"cannot compare InstantUtc with {type(other).__name__}"
            )
        return self.dt > other.dt

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, InstantUtc):
            raise TimestampSemanticsMismatch(
                f"cannot compare InstantUtc with {type(other).__name__}"
            )
        return self.dt >= other.dt

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, InstantUtc):
            return False
        return self.dt == other.dt

    def __hash__(self) -> int:
        return hash(self.dt)
