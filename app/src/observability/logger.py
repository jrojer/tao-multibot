import logging
from typing import Any
from app.src import env
from app.src.observability.influxdb_logger_handler import InfluxDbLoggerHandler

logging.basicConfig(
    format="%(threadName)s - %(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.FileHandler(env.LOG_PATH), InfluxDbLoggerHandler()],
)


class Logger:
    def __init__(self, package_name: str):
        self.package_name = package_name
        self.logger = logging.getLogger(package_name)

    def warning(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.warning(msg, *args, **kwargs)

    def info(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.info(msg, *args, **kwargs)

    def debug(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.debug(msg, *args, **kwargs)

    def error(self, msg: str, *args: Any, **kwargs: Any):
        self.logger.error(msg, *args, **kwargs)
