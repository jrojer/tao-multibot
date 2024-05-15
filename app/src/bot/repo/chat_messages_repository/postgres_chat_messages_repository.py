from pathlib import Path
from typing import Any, List, Optional
from uuid import uuid4

from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.content_type import ContentType
from app.src.bot.repo.chat_messages_repository.role import Role
from app.src.bot.repo.chat_messages_repository.source import Source
from app.src.butter.checks import check_required
from app.src.third_party.flyway.postgres_migrator import PostgresMigrator

import psycopg2


DB_NAME = "platform"
TABLE_NAME = "chat_messages"


class PostgresChatMessagesRepository(ChatMessagesRepository):
    def __init__(self, host: str, port: int, user: str, password: str, schemas: str):
        self._host: str = check_required(host, "host", str)
        self._port: int = check_required(port, "port", int)
        self._user: str = check_required(user, "user", str)
        self._password: str = check_required(password, "password", str)
        self._schemas: str = check_required(schemas, "schemas", str)

        self._conn = psycopg2.connect(
            database=DB_NAME,
            user=self._user,
            password=self._password,
            host=self._host,
            port=self._port,
        )

    def migrate(self) -> None:
        PostgresMigrator(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            schemas=self._schemas,
        ).migrate(DB_NAME, str(Path(__file__).parent / "migrations"))

    def add(self, message: ChatMessage) -> str:
        cursor = self._conn.cursor()
        sql = f"""
            INSERT INTO {TABLE_NAME} ("id", "timestamp", "content", "content_type", "user", "chat", "source", "role", "added_by", "reply_to", "ref")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ;
        """
        new_id = str(uuid4())
        cursor.execute(
            sql,
            _to_record(
                message,
                new_id,
            ),
        )
        self._conn.commit()
        return new_id

    def fetch_last_messages_by_chat_and_adder(
        self, chat: str, adder: str, limit: int = 1000
    ) -> List[ChatMessage]:
        cursor = self._conn.cursor()
        sql = f"""
            SELECT "id", "timestamp", "content", "content_type", "user", "chat", "source", "role", "added_by", "reply_to", "ref"
            FROM {TABLE_NAME}
            WHERE "chat" = %s and "added_by" = %s
            ORDER BY "timestamp" DESC
            LIMIT %s;
        """
        cursor.execute(sql, (chat, adder, limit))
        records = cursor.fetchall()
        return [_from_record(r) for r in reversed(records)]


def _from_record(r: tuple[Any, ...]) -> ChatMessage:
    return (
        ChatMessage.new()
        .id(r[0])
        .timestamp(r[1])
        .content(r[2])
        .content_type(ContentType.from_str(r[3]))
        .user(r[4])
        .chat(r[5])
        .source(Source.from_str(r[6]))
        .role(Role.from_str(r[7]))
        .added_by(r[8])
        .reply_to(r[9])
        .ref(r[10])
        .build()
    )


def _to_record(m: ChatMessage, id: str) -> tuple[Optional[str], ...]:
    return (
        id,
        str(m.timestamp()),
        m.content(),
        m.content_type().value,
        m.user(),
        m.chat(),
        m.source().value,
        m.role().value,
        m.added_by(),
        m.reply_to(),
        m.ref(),
    )
