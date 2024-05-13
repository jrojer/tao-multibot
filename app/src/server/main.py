import time
from app.src.observability.logger import Logger
from app.src.server.api.server import Server
from app.src.server.master_config.master_config import MasterConfig
from app.src.server.runtime_manager import RuntimeManager
import signal
from app.src import env

logger = Logger(__name__)


def main():
    master_config = MasterConfig(env.MASTER_CONFIG_PATH())
    server_port = env.SERVER_PORT()
    runtime_manager = RuntimeManager(server_port, master_config)
    resources = Server(server_port, master_config, runtime_manager)

    def handler(signum, frame):  # type: ignore
        logger.info("Stopping all bots")
        runtime_manager.stop_all()

    signal.signal(signal.SIGINT, handler)  # type: ignore

    p = resources.start()
    time.sleep(5)
    runtime_manager.start_all()
    p.join()
