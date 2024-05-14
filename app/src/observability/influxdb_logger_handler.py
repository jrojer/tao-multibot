# type: ignore
from logging import Handler, getLevelName
from app.src.observability.metrics_client.influxdb_metrics_client import (
    MetricsReporter,
)
from app.src import env

class InfluxDbLoggerHandler(Handler):
    """
    A handler class which writes formatted logging records to influx db.
    """

    def __init__(self):
        Handler.__init__(self)
        self.metrics_client = MetricsReporter()

    def emit(self, record):
        if not env.INFLUXDB_ENABLED():
            return
        # TODO: consider adding tags and the message separately, the formatting can be done on the frontend
        msg = self.format(record)
        try:
            self.metrics_client.write(
                "logs",
                {
                    # TODO: add bot name and other context
                    "level": record.levelname,
                    "package": record.name,
                    "thread": record.threadName,
                },
                {"message": msg},
            )
        except Exception:
            return

    def __repr__(self):
        level = getLevelName(self.level)
        return "<%s %s (%s)>" % (self.__class__.__name__, self.baseFilename, level)
