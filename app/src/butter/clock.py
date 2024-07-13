import datetime
import enum

_mode = [0]


def clock_test_mode(on: bool):
    _mode[0] = on


class Precision(enum.Enum):
    SECOND = "s"
    MILLISECOND = "ms"
    MICROSECOND = "us"
    NANOSECOND = "ns"


_d = {
    "s": 1,
    "ms": 1000,
    "us": 1000000,
    "ns": 1000000000,
}


def timestamp_now(precision: Precision = Precision.NANOSECOND) -> int:
    if _mode[0]:
        return 123456789
    coef = _d[precision.value]
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp() * coef)


def timestamp_to_readable_datetime(
    timestamp: int, tz: datetime.timezone = datetime.timezone.utc
) -> str:
    return datetime.datetime.fromtimestamp(timestamp, tz=tz).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
