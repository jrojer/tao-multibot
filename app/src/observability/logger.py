import logging
from pathlib import Path
import threading
from typing import Any
from app.src import env
from app.src.observability.influxdb_logger_handler import InfluxDbLoggerHandler


class NoiseRecordsFilter(logging.Filter):
    def filter(self, record: logging.LogRecord):
        return not (
            record.name in ["aiohttp.access", "httpx"] and record.levelname == "INFO"
        )


def configure_logging():
    _fileHandler = logging.FileHandler(
        Path(env.LOG_DIR()) / (threading.current_thread().name + ".log")
    )
    _fileHandler.addFilter(NoiseRecordsFilter())

    _influxDbLoggerHandler = InfluxDbLoggerHandler()
    _influxDbLoggerHandler.addFilter(NoiseRecordsFilter())

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            _fileHandler,
            _influxDbLoggerHandler,
        ],
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


configure_logging()
