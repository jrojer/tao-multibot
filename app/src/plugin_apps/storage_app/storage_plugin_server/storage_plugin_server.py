import multiprocessing
from app.src.butter.checks import check_required
from aiohttp import web

from app.src.observability.logger import Logger
from app.src.plugin_apps.storage_app.storage_plugin_server.resources.execute_sql_resource import (
    ExecuteSqlResource,
)
from app.src.plugin_apps.storage_app.storage_plugin_server.resource import Resource


logger = Logger(__name__)


class StoragePluginServer:
    def __init__(self, port: int):
        self._port: int = check_required(port, "port", int)
        self._app: web.Application = web.Application()
        self._app.add_routes([_route(ExecuteSqlResource())])
        self._process: multiprocessing.Process

    async def _start(self):
        runner = web.AppRunner(self._app)
        await runner.setup()
        await web.TCPSite(runner, port=self._port).start()

    def start(self) -> None:
        def target():
            import asyncio

            loop = asyncio.get_event_loop()
            loop.run_until_complete(self._start())
            loop.run_forever()

        self._process = multiprocessing.Process(
            target=target, name="storage_plugin_server"
        )
        self._process.start()
        logger.info(
            f"StoragePluginServer (pid {self._process.pid}) started on port {self._port}"
        )

    def stop(self) -> None:
        self._process.terminate()

    def join(self) -> None:
        self._process.join()


def _route(resource: Resource) -> web.RouteDef:
    if resource.method() == "GET":
        return web.get(resource.path(), resource.handler())
    elif resource.method() == "POST":
        return web.post(resource.path(), resource.handler())
    else:
        raise ValueError(f"Unsupported method {resource.method()}")
