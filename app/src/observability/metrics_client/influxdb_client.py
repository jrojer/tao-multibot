from typing import Optional
import requests

from app.src.butter.checks import check_required
from app.src.butter.clock import (
    Precision,
    timestamp_now,
    timestamp_to_readable_datetime,
)
from app.src import env

_ESCAPE_MEASUREMENT = str.maketrans(
    {
        ",": r"\,",
        " ": r"\ ",
        "\n": r"\n",
        "\t": r"\t",
        "\r": r"\r",
    }
)

_ESCAPE_KEY = str.maketrans(
    {
        ",": r"\,",
        "=": r"\=",
        " ": r"\ ",
        "\n": r"\n",
        "\t": r"\t",
        "\r": r"\r",
    }
)

_ESCAPE_STRING = str.maketrans(
    {
        '"': r"\"",
        "\\": r"\\",
    }
)


def _escape_key(tag: str, escape_list: Optional[dict[int, str]] = None) -> str:
    if escape_list is None:
        escape_list = _ESCAPE_KEY
    return str(tag).translate(escape_list)


def _escape_tag_value(value: str) -> str:
    ret = _escape_key(value)
    if ret.endswith("\\"):
        ret += " "
    return ret


def _escape_string(value: str) -> str:
    return str(value).translate(_ESCAPE_STRING)


def _escape_tags(tags: dict[str, str]) -> dict[str, str]:
    return {_escape_key(k): _escape_tag_value(v) for k, v in tags.items()}


def _escape_fields(fields: dict[str, str]) -> dict[str, str]:
    return {_escape_key(k): f'"{_escape_string(v)}"' for k, v in fields.items()}


def _comma_separated(d: dict[str, str]) -> str:
    return ",".join(f"{k}={v}" for k, v in d.items())


def _to_line_protocol(
    measurement: str, tags: dict[str, str], fields: dict[str, str], timestamp: int
) -> bytes:
    measurement = _escape_key(measurement, _ESCAPE_MEASUREMENT)
    tags = _escape_tags(tags)
    fields = _escape_fields(fields)
    return f"{measurement},{_comma_separated(tags)} {_comma_separated(fields)} {timestamp}".encode(
        "utf-8"
    )


class InfluxdbClient:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self._url: str = check_required(url, "url", str)
        self._token: str = check_required(token, "token", str)
        self._org: str = check_required(org, "org", str)
        self._bucket: str = check_required(bucket, "bucket", str)

    def write(self, measurement: str, tags: dict[str, str], fields: dict[str, str]):
        check_required(measurement, "measurement", str)
        check_required(tags, "tags", dict)
        check_required(fields, "fields", dict)
        url = f"{self._url}/api/v2/write?org={self._org}&bucket={self._bucket}&precision=ns"
        headers = {
            "Authorization": f"Token {self._token}",
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/json",
        }

        data = _to_line_protocol(
            measurement, tags, fields, timestamp_now(precision=Precision.NANOSECOND)
        )

        res = requests.post(url, headers=headers, data=data)
        if res.status_code != 204:
            with open(env.LOG_DIR() / "influxdb.log", "a") as f:
                f.write(
                    f"{timestamp_to_readable_datetime(timestamp_now())} - {res.status_code} - {res.text} - {data}\n"
                )


"""
reference: https://docs.influxdata.com/influxdb/cloud/write-data/developer-tools/api/

curl --request POST \
"http://localhost:8086/api/v2/write?org=YOUR_ORG&bucket=YOUR_BUCKET&precision=ns" \
  --header "Authorization: Token YOUR_API_TOKEN" \
  --header "Content-Type: text/plain; charset=utf-8" \
  --header "Accept: application/json" \
  --data-binary '
    airSensors,sensor_id=TLM0201 temperature=73.97038159354763,humidity=35.23103248356096,co=0.48445310567793615 1630424257000000000
    airSensors,sensor_id=TLM0202 temperature=75.30007505999716,humidity=35.651929918691714,co=0.5141876544505826 1630424257000000000
    '
"""
