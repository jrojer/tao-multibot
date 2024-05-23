from typing import Any, Optional
from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.content_type import ContentType
from app.src.bot.repo.chat_messages_repository.role import Role
from app.src.bot.repo.chat_messages_repository.source import Source
from app.src.butter.checks import check_required
from app.src.internal.common.message_sender import MessageSender
from app.src.observability.logger import Logger
from urllib.parse import quote_plus
import aiohttp

logger = Logger(__name__)


class TgBotMessageSender(MessageSender):
    def __init__(self, tg_bot_token: str, repo: ChatMessagesRepository) -> None:
        self._token: str = check_required(tg_bot_token, "token", str)
        self._repo: ChatMessagesRepository = check_required(
            repo, "repo", ChatMessagesRepository
        )

    async def send_text(self, chat_id: str, message: str, username: Optional[str] = None) -> None:
        await _get(
            f"https://api.telegram.org/bot{self._token}/sendMessage?chat_id={chat_id}&text={_url_encode(message)}"
        )
        if username is None:
            username = await _get_tg_bot_username(self._token)
            role = Role.ASSISTANT
        else:
            role = Role.USER
        self._repo.add(
            ChatMessage.new()
            .content(message)
            .content_type(ContentType.TEXT)
            .user(username)
            .chat(chat_id)
            .source(Source.TELEGRAM)
            .role(role)
            .added_by(username)
            .build()
        )
        logger.info(f"Sent message to {chat_id}: {message}")


async def _get(url: str) -> dict[str, Any]:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()


def _url_encode(text: str) -> str:
    text = text.replace("\\", "\\\\")
    return quote_plus(text)


async def _get_tg_bot_username(token: str) -> str:
    id_object = await _get(f"https://api.telegram.org/bot{token}/getMe")
    return id_object["result"]["username"]
