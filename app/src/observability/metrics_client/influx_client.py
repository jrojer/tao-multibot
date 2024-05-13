import aiohttp

from app.src.butter.checks import check_required
from app.src.butter.clock import Precision, timestamp_now
from app.src.observability.logger import Logger


logger = Logger(__name__)


class InfluxdbClient:
    def __init__(self, url: str, token: str, org: str, bucket: str):
        self._url: str = check_required(url, "url", str)
        self._token: str = check_required(token, "token", str)
        self._org: str = check_required(org, "org", str)
        self._bucket: str = check_required(bucket, "bucket", str)

    async def write(
        self, measurement: str, tags: dict[str, str], fields: dict[str, str]
    ):
        check_required(measurement, "measurement", str)
        check_required(tags, "tags", dict)
        check_required(fields, "fields", dict)
        url = f"{self._url}/api/v2/write?org={self._org}&bucket={self._bucket}&precision=ns"
        headers = {
            "Authorization": f"Token {self._token}",
            "Content-Type": "text/plain; charset=utf-8",
            "Accept": "application/json",
        }

        def pairs(d: dict[str, str]) -> str:
            return ",".join(f'{k}="{d[k]}"' for k in d)

        data = f"{measurement},{pairs(tags)} {pairs(fields)} {timestamp_now(precision=Precision.NANOSECOND)}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                if response.status != 204:
                    text = await response.text()
                    logger.error(
                        "Failed to write to influxdb: %s. %s", response.status, text
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
