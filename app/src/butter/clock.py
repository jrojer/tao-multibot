import datetime

_mode = [0]


def clock_test_mode(on: bool):
    _mode[0] = on


def timestamp_now():
    if _mode[0]:
        return 123456789
    return int(datetime.datetime.now(datetime.timezone.utc).timestamp())


def timestamp_to_readable_datetime(
    timestamp: int, tz: datetime.timezone = datetime.timezone.utc
) -> str:
    return datetime.datetime.fromtimestamp(timestamp, tz=tz).strftime(
        "%Y-%m-%d %H:%M:%S"
    )
