import http

import pandas as pd
from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from aiohttp import web
from app.src import env

from app.src.plugin_apps.storage_app.storage_plugin_server.resource import (
    Handler,
    Resource,
)
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.operational_error import OperationalError
from app.src.plugin_apps.storage_app.storage_plugin_server.sql_executor.sql_executor import (
    SqlExecutor,
)


logger = Logger(__name__)


class ExecuteSqlResource(Resource):
    def __init__(self):
        pass

    @staticmethod
    def path() -> str:
        return "/api/{chat_id}/sql"

    @staticmethod
    def method() -> str:
        return "POST"

    def handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            chat_id: str = check_required(
                request.match_info.get("chat_id"), "chat_id", str
            )
            sql: str = check_required((await request.json())["sql"], "sql", str)
            logger.info(f"Executing SQL: {sql} for chat_id: {chat_id}")

            db_path = env.DATA_DIR() / f"{chat_id}.db"
            try:
                executor = SqlExecutor(db_path)
                result: list[dict[str, str]] = executor.execute(sql)
                tables = executor.get_tables()
                for table_name in tables:
                    if table_name in sql:
                        df_dir = env.DATA_DIR() / chat_id
                        df_dir.mkdir(parents=True, exist_ok=True)
                        data = executor.execute(f"SELECT * FROM {table_name}")
                        pd.DataFrame(data).to_csv(df_dir / f"{table_name}.tsv", sep="\t", index=False)
            except Exception as e:
                if isinstance(e, OperationalError):
                    return web.json_response(
                        {"status": "error", "message": str(e)},
                        status=http.HTTPStatus.BAD_REQUEST,
                    )
                return web.json_response(
                    {"status": "error", "message": str(e)},
                    status=http.HTTPStatus.INTERNAL_SERVER_ERROR,
                )

            return web.json_response({"status": "success", "result": result})

        return handler
