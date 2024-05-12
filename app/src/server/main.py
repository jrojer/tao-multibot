import asyncio
from app.src.observability.logger import Logger
from app.src.server.api.server import Server
from app.src.server.master_config.master_config import MasterConfig
from app.src.server.runtime_manager import RuntimeManager
import signal
from app.src import env

logger = Logger(__name__)


def main():
    server_port = int(env.SERVER_PORT)
    master_config = MasterConfig(env.MAIN_CONFIG)
    runtime_manager = RuntimeManager(server_port, master_config)
    resources = Server(server_port, master_config, runtime_manager)

    def handler(signum, frame):  # type: ignore
        logger.info("Stopping all bots")
        runtime_manager.stop_all()

    signal.signal(signal.SIGINT, handler)  # type: ignore

    async def start_server():
        await resources.start()
    
    async def start_bots():
        runtime_manager.start_all()
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(start_server())
    loop.run_until_complete(start_bots())
    loop.run_forever()
