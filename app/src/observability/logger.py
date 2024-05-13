import logging
from pathlib import Path
import threading
from typing import Any
from app.src import env
from app.src.observability.influxdb_logger_handler import InfluxDbLoggerHandler

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.FileHandler(Path(env.LOG_DIR()) / (threading.current_thread().name + ".log")),
        InfluxDbLoggerHandler(),
    ],
)


# NOTE: this is a workaround to reconfigure logging after forking
# TODO: think about a better way to reconfigure logging
def reconfigure_logging():
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        handlers=[
            logging.FileHandler(
                Path(env.LOG_DIR()) / (threading.current_thread().name + ".log")
            ),
            InfluxDbLoggerHandler(),
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
