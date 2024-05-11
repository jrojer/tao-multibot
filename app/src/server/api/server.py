from aiohttp import web

from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from app.src.server.api.resource import Resource
from app.src.server.api.resources.disable_for_username_resource import (
    DisableForUsernameResource,
)
from app.src.server.api.resources.disable_for_group_resource import (
    DisableForGroupResource,
)
from app.src.server.api.resources.enable_for_username_resource import (
    EnableForUsernameResource,
)
from app.src.server.api.resources.enable_for_group_resource import (
    EnableForGroupResource,
)
from app.src.server.api.resources.get_bot_conf_resource import GetBotConfResource
from app.src.server.api.resources.set_number_of_message_for_completion_resource import (
    SetNumberOfMessagesForCompletionResource,
)
from app.src.server.api.resources.stop_bot_resource import StopBotResource
from app.src.server.master_config.master_config import MasterConfig
from app.src.server.runtime_manager import RuntimeManager
import multiprocessing

logger = Logger(__name__)


def route(resource: Resource) -> web.RouteDef:
    if resource.method() == "GET":
        return web.get(resource.path(), resource.handler())
    elif resource.method() == "POST":
        return web.post(resource.path(), resource.handler())
    else:
        raise ValueError(f"Unsupported method {resource.method()}")


class Server:
    def __init__(
        self, port: int, master_conf: MasterConfig, runtime_manager: RuntimeManager
    ):
        self._port: int = check_required(port, "port", int)
        self._app: web.Application = web.Application()
        modifier = master_conf.modifier()
        self._app.add_routes(
            [
                route(StopBotResource(runtime_manager)),
                route(GetBotConfResource(master_conf)),
                route(EnableForGroupResource(modifier)),
                route(DisableForGroupResource(modifier)),
                route(EnableForUsernameResource(modifier)),
                route(DisableForUsernameResource(modifier)),
                route(SetNumberOfMessagesForCompletionResource(modifier)),
            ]
        )

    def start(self) -> multiprocessing.Process:
        def target():
            web.run_app(self._app, port=int(self._port))  # type: ignore
        process = multiprocessing.Process(target=target)
        process.start()
        return process
