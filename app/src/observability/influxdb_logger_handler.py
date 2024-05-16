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

        message = record.message
        traceback = None
        if record.levelname == "ERROR":
            if "traceback: " in record.message:
                split = record.message.split("traceback: ")
                message = split[0]
                traceback = split[1]
        try:
            self.metrics_client.write(
                "logs",
                {
                    # TODO: add bot name and other context
                    "level": record.levelname,
                    "package": record.name,
                    "process": record.processName,
                    "traceback": traceback,
                },
                {"message": message},
            )
        except Exception:
            return

    def __repr__(self):
        level = getLevelName(self.level)
        return "<%s %s (%s)>" % (self.__class__.__name__, self.baseFilename, level)
