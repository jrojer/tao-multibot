from logging import Handler, getLevelName
from app.src.observability.metrics_client.influxdb_metrics_client import InfluxDbMetricsClient


class InfluxDbLoggerHandler(Handler):
    """
    A handler class which writes formatted logging records to influx db.
    """

    def __init__(self):
        Handler.__init__(self)
        self.metrics_client = InfluxDbMetricsClient()

    def close(self):
        self.metrics_client.close()

    def emit(self, record):
        msg = self.format(record)
        try:
            self.metrics_client.write("logs",
                                    {
                                        # TODO: add bot name and other context
                                        "level": record.levelname,
                                        "package": record.name
                                    },
                                    {
                                        "message": msg
                                    })
        except Exception:
            self.handleError(record)

    def __repr__(self):
        level = getLevelName(self.level)
        return '<%s %s (%s)>' % (self.__class__.__name__, self.baseFilename, level)
