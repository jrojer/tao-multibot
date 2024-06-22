import time
from app.src.bot.repo.chat_messages_repository.postgres_chat_messages_repository import (
    PostgresChatMessagesRepository,
)
from app.src.observability.logger import Logger
from app.src.plugin_apps.storage_app.storage_app import StorageApp
from app.src.server.api.server import Server
from app.src.server.master_config.master_config import MasterConfig
from app.src.server.runtime_manager import RuntimeManager
import signal
from app.src import env

logger = Logger(__name__)


def main():
    if env.POSTGRES_ENABLED():
        PostgresChatMessagesRepository(
            host=env.POSTGRES_HOST(),
            port=env.POSTGRES_PORT(),
            user=env.POSTGRES_USER(),
            password=env.POSTGRES_PASSWORD(),
            schemas=env.POSTGRES_SCHEMAS(),
        ).migrate()
    master_config = MasterConfig(env.MASTER_CONFIG_PATH())
    server_port = env.SERVER_PORT()
    runtime_manager = RuntimeManager(server_port, master_config)
    resources = Server(server_port, master_config, runtime_manager)

    # TODO: consider manage Server startup and shutdown in RuntimeManager
    # TODO: consider managing process object in the class itself
    p = resources.start()

    storage_app = StorageApp()
    storage_app.start()

    def handler(signum, frame):  # type: ignore
        logger.info("Stopping all bots")
        runtime_manager.stop_all()
        time.sleep(5)
        logger.info("All bots are stopped")
        p.terminate()
        storage_app.stop()
        exit(0)

    signal.signal(signal.SIGINT, handler)  # type: ignore

    # wait for the server to start
    time.sleep(5)

    runtime_manager.start_all()

    p.join()
