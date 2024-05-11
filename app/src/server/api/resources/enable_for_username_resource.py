from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.api.resource import Handler, Resource
from app.src.server.master_config.master_config import MasterConfig
from aiohttp import web


logger = Logger(__name__)


class EnableForUsernameResource(Resource):
    def __init__(self, modifier: MasterConfig.Modifier):
        self._modifier: MasterConfig.Modifier = check_required(
            modifier, "modifier", MasterConfig.Modifier
        )

    def path(self) -> str:
        return "/api/bots/{bot_name}/users/{user_name}/enable"

    def method(self) -> str:
        return "POST"

    def handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            bot_name: str = check_required(
                request.match_info.get("bot_name"), "bot_name", str
            )
            user_name: str = check_required(
                request.match_info.get("user_name"), "user_name", str
            )
            self._modifier.enable_for_username(bot_name, user_name)
            return web.Response(status=200)

        return handler
