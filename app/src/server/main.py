import multiprocessing
from app.src.observability.logger import Logger
from app.src.server.api.resources import Resources
from app.src.server.master_config.master_config import MasterConfig
from app.src.server.runtime_manager import RuntimeManager
import signal

logger = Logger(__name__)


def main():
    multiprocessing.set_start_method("fork")
    master_config = MasterConfig()
    runtime_manager = RuntimeManager(master_config)

    def handler(signum, frame):  # type: ignore
        logger.info("Stopping all bots")
        runtime_manager.stop_all()

    signal.signal(signal.SIGINT, handler)  # type: ignore
    runtime_manager.start_all()
    resources = Resources(runtime_manager)
    resources.start()
