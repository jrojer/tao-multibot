import http
import json
from typing import Any, Optional
from app.src.butter.checks import check_required, check_that
from app.src.gpt.plugin import Plugin
from app.src.observability.logger import Logger
import aiohttp

logger = Logger(__name__)

_PLUGIN_SEVER_PORT = 8999


class RemoteStorageAppPlugin(Plugin):
    def __init__(self, chat_id: str):
        self._chat_id: str = check_required(chat_id, "chat_id", str)

    def functions(self) -> list[dict[str, Any]]:
        return [
            {
                "manifest": {
                    "name": "sql",
                    "description": "Executes SQL.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "sql": {
                                "type": "string",
                                "description": "SQL query to execute.",
                            },
                        },
                        "required": ["sql"],
                    },
                }
            }
        ]

    def is_delegate(self) -> bool:
        return False

    def system_prompt_attachment(self) -> Optional[str]:
        # TODO: here goes the description of existing tables
        return None

    async def call(self, name: str, args: str) -> str:
        logger.info("Calling function %s with args %s", name, args)

        deserialised: dict[str, Any] = json.loads(args)
        check_that("sql" in deserialised, f'"sql" field not found in args: {args}')

        url: str = (
            f"http://localhost:{_PLUGIN_SEVER_PORT}/api/{self._chat_id}/sql"
        )
        status, text = await _send_post_request(url, deserialised)
        if status != http.HTTPStatus.OK:
            logger.error(f"Failed to execute SQL. Status code: {status}, response: {text}, args: {args}")
            # TODO: this error could potentially be shown to the user and disclose server internal information
            return str({
                "status": "error",
                "error": f"Failed to execute SQL. Status code: {status}, response: {text[:100]}" + "..." if len(text) > 100 else text,
            })
        return text


async def _send_post_request(url: str, data: dict[str, Any]) -> tuple[int, str]:
    async with aiohttp.ClientSession() as session:
        try:
            async with session.post(url, json=data) as response:
                response_data = await response.text()
                return response.status, response_data
        except Exception as e:
            return http.HTTPStatus.INTERNAL_SERVER_ERROR, str(e)
