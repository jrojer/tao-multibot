from app.src import env
from app.src.observability.metrics_client.influxdb_client import InfluxdbClient


class MetricsReporter:
    def __init__(self):
        if env.INFLUXDB_ENABLED():
            self._client = InfluxdbClient(
                url=env.INFLUXDB_URL(),
                token=env.INFLUXDB_TOKEN(),
                org=env.INFLUXDB_ORG(),
                bucket=env.INFLUXDB_BUCKET(),
            )

    def write(
        self, measurement: str, tags: dict[str, str], fields: dict[str, str]
    ):
        try:
            if env.INFLUXDB_ENABLED():
                self._client.write(measurement, tags, fields)
        except Exception as e:
            raise e
