from typing import Optional
from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.api.resource import Handler, Resource
from app.src.server.runtime_manager import RuntimeManager
from aiohttp import web


logger = Logger(__name__)


class StopBotResource(Resource):
    def __init__(self, runtime_manager: RuntimeManager):
        self._runtime_manager = check_required(runtime_manager, "runtime_manager", RuntimeManager)

    @staticmethod
    def path() -> str:
        return "/api/bots/{bot_name}/stop"
    
    @staticmethod
    def method() -> str:
        return "POST"

    def handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            bot_name: Optional[str] = request.match_info.get("bot_name")
            logger.info(f"Stopping bot {bot_name}")
            self._runtime_manager.stop(bot_name)
            return web.Response(status=200)

        return handler
