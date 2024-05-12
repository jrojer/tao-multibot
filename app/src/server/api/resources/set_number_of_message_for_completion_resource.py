from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.api.resource import Handler, Resource
from app.src.server.master_config.master_config import MasterConfig
from aiohttp import web


logger = Logger(__name__)


class SetNumberOfMessagesForCompletionResource(Resource):
    def __init__(self, modifier: MasterConfig.Modifier):
        self._modifier: MasterConfig.Modifier = check_required(
            modifier, "modifier", MasterConfig.Modifier
        )

    @staticmethod
    def path() -> str:
        return "/api/bots/{bot_name}/conf/messages_per_completion"

    @staticmethod
    def method() -> str:
        return "POST"

    def handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            bot_name: str = check_required(
                request.match_info.get("bot_name"), "bot_name", str
            )
            value: int = check_required((await request.json())["value"], "value", int)
            self._modifier.set_number_of_messages_per_completion(bot_name, value)
            return web.Response(status=200)

        return handler
