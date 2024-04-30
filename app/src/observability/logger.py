import logging
from app.src import env
from app.src.observability.influxdb_logger_handler import InfluxDbLoggerHandler

# Enable logging
logging.basicConfig(
    format="%(threadName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(env.LOG_PATH),
        InfluxDbLoggerHandler()
    ]
)


class Logger:
    def __init__(self, package_name: str) -> None:
        self.package_name = package_name
        self.logger = logging.getLogger(package_name)

    def warning(self, msg, *args, **kwargs):
        self.logger.warning(msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        self.logger.debug(msg, *args, **kwargs)

    def error(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
