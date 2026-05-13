"""Session-date wrappers — XNYS ET, CMES CT, and per-asset market session (contract §5)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime

from .exceptions import TimestampSemanticsMismatch


def _coerce_date(value, owner: str) -> date:
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError as exc:
            raise TimestampSemanticsMismatch(
                f"{owner} requires YYYY-MM-DD; cannot parse {value!r}: {exc}"
            ) from exc
    raise TimestampSemanticsMismatch(
        f"{owner} requires date or YYYY-MM-DD str; got {type(value).__name__}"
    )


def _ordering_guard(self, other, kind: str) -> None:
    if type(self) is not type(other):
        raise TimestampSemanticsMismatch(
            f"cannot {kind} {type(self).__name__} with {type(other).__name__}"
        )


@dataclass(frozen=True)
class SessionDateEt:
    """XNYS ET market-session day."""

    date: date

    def __post_init__(self) -> None:
        object.__setattr__(self, "date", _coerce_date(self.date, "SessionDateEt"))

    def to_iso(self) -> str:
        return self.date.isoformat()

    def __lt__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date < other.date

    def __le__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date <= other.date

    def __gt__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date > other.date

    def __ge__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date >= other.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SessionDateEt):
            return False
        return self.date == other.date

    def __hash__(self) -> int:
        return hash(("session_date_et", self.date))


@dataclass(frozen=True)
class SessionDateCt:
    """CMES CT trading day."""

    date: date

    def __post_init__(self) -> None:
        object.__setattr__(self, "date", _coerce_date(self.date, "SessionDateCt"))

    def to_iso(self) -> str:
        return self.date.isoformat()

    def __lt__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date < other.date

    def __le__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date <= other.date

    def __gt__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date > other.date

    def __ge__(self, other: object) -> bool:
        _ordering_guard(self, other, "compare")
        return self.date >= other.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SessionDateCt):
            return False
        return self.date == other.date

    def __hash__(self) -> int:
        return hash(("session_date_ct", self.date))


@dataclass(frozen=True)
class SessionDateMarket:
    """Generic per-asset session day. `market_tz` is required sibling per §5."""

    date: date
    market_tz: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "date", _coerce_date(self.date, "SessionDateMarket"))
        if not isinstance(self.market_tz, str) or not self.market_tz:
            raise TimestampSemanticsMismatch(
                "SessionDateMarket requires non-empty IANA market_tz sibling"
            )

    def to_iso(self) -> str:
        return self.date.isoformat()

    def _guard(self, other: object) -> None:
        if not isinstance(other, SessionDateMarket):
            raise TimestampSemanticsMismatch(
                f"cannot compare SessionDateMarket with {type(other).__name__}"
            )
        if self.market_tz != other.market_tz:
            raise TimestampSemanticsMismatch(
                f"SessionDateMarket tz mismatch: {self.market_tz} vs {other.market_tz}"
            )

    def __lt__(self, other: object) -> bool:
        self._guard(other)
        return self.date < other.date

    def __le__(self, other: object) -> bool:
        self._guard(other)
        return self.date <= other.date

    def __gt__(self, other: object) -> bool:
        self._guard(other)
        return self.date > other.date

    def __ge__(self, other: object) -> bool:
        self._guard(other)
        return self.date >= other.date

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, SessionDateMarket):
            return False
        return self.date == other.date and self.market_tz == other.market_tz

    def __hash__(self) -> int:
        return hash(("session_date_market", self.date, self.market_tz))
