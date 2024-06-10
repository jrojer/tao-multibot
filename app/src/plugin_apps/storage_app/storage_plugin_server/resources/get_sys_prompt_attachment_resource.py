import http
from typing import Any
from app.src.butter.checks import check_required
from app.src.observability.logger import Logger
from aiohttp import web

from app.src.plugin_apps.storage_app.storage_plugin_server.resource import (
    Handler,
    Resource,
)
from app.src.plugin_apps.storage_app.table_manager import TableManager


logger = Logger(__name__)


class GetSysPromptAttachmentResource(Resource):
    def __init__(self):
        pass

    @staticmethod
    def path() -> str:
        return "/api/{chat_id}/sysprompt"

    @staticmethod
    def method() -> str:
        return "GET"

    def handler(self) -> Handler:
        async def handler(request: web.Request) -> web.Response:
            chat_id: str = check_required(
                request.match_info.get("chat_id"), "chat_id", str
            )
            result: dict[str, list[dict[str, Any]]] = TableManager().get_tables(chat_id)

            if len(result) == 0:
                return web.Response(status=http.HTTPStatus.NO_CONTENT)

            response = "Use SQLite syntax. Available tables:\n\n"
            for table_name, columns in result.items():
                response += _generate_create_table_sql(table_name, columns) + "\n\n"

            return web.Response(
                text=response, content_type="text/plain", status=http.HTTPStatus.OK
            )

        return handler


def _generate_create_table_sql(table_name: str, columns: list[dict[str, Any]]) -> str:
    column_definitions: list[str] = []
    for column in columns:
        column_def = f"{column['name']} {column['type']}"
        if column["notnull"]:
            column_def += " NOT NULL"
        if column["dflt_value"] is not None:
            column_def += f" DEFAULT {column['default']}"
        if column["pk"]:
            column_def += " PRIMARY KEY"
        column_definitions.append(column_def)

    columns_sql = "\n  " + ",\n  ".join(column_definitions) + "\n"
    create_table_sql = f"CREATE TABLE {table_name} ({columns_sql});"

    return create_table_sql
