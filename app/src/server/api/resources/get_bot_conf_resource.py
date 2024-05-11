from typing import Any
from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.api.resource import Handler, Resource
from app.src.server.master_config.master_config import MasterConfig
from aiohttp import web


logger = Logger(__name__)


class GetBotConfResource(Resource):
    def __init__(self, master_conf: MasterConfig):
        self._master_conf: MasterConfig = check_required(
            master_conf, "master_conf", MasterConfig
        )

    def path(self) -> str:
        return "/api/bots/{bot_name}/conf"
    
    def method(self) -> str:
        return "GET"

    def handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            bot_name: str = check_required(request.match_info.get("bot_name"), "bot_name", str)
            logger.info(f"Stopping bot {bot_name}")
            conf: dict[str, Any] = self._master_conf.bot_conf(bot_name)
            return web.json_response(conf)

        return handler
