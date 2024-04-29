import logging
# TODO: use http API instead of python client
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from app.src import env

from app.src.observability.metrics_client.metrics_client import MetricsClient

logger = logging.getLogger(__name__)

token = env.INFLUXDB_TOKEN
org = "org"
# TODO change to env variable
url = "http://influxdb:8086"
bucket = "bucket"


class InfluxDbMetricsClient(MetricsClient):
    def __init__(self) -> None:
        self.client = InfluxDBClient(url=url, token=token, org=org)
        self.write_api = self.client.write_api(write_options=SYNCHRONOUS)

    def write(self, measurement: str, tags: dict, fields: dict):
        point = Point(measurement)
        for tag, value in tags.items():
            point.tag(tag, value)
        for field, value in fields.items():
            point.field(field, value)

        self.write_api.write(bucket, org, point)

    def close(self):
        self.client.close()
