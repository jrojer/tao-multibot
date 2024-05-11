from typing import Any, Callable, Coroutine, Optional
from aiohttp import web

from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.runtime_manager import RuntimeManager
from app.src import env

logger = Logger(__name__)


Handler = Callable[[web.Request], Coroutine[Any, Any, web.Response]]


# TODO: add get method to return fresh json object for given bot_id
class Resources:
    def __init__(self, runtime_manager: RuntimeManager):
        self._app: web.Application = web.Application()
        self._app.add_routes([web.get("/stop/{bot_name}", self.stop_handler())])
        self._runtime_manager: RuntimeManager = check_required(
            runtime_manager, "runtime_manager", RuntimeManager
        )

    def start(self):
        web.run_app(self._app, port=int(env.SERVER_PORT))  # type: ignore

    def stop_handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            bot_name: Optional[str] = request.match_info.get("bot_name")
            logger.info(f"Stopping bot {bot_name}")
            self._runtime_manager.stop(bot_name)
            return web.Response(status=200)

        return handler
