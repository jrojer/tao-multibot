from pathlib import Path
from typing import List
from uuid import uuid4

from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.butter.checks import check_range, check_required
from app.src.third_party.flyway.postgres_migrator import PostgresMigrator

import psycopg2


'''
reference:


def from_record(r):
    return (
        ChatMessage.new()
        .chat_id(r[0])
        .username(r[1])
        .post(r[2])
        .timestamp(r[3])
        .build()
    )


def to_record(m: ChatMessage, id: str):
    return (m.chat_id, m.username, m.post, m.timestamp, id)


class SqliteChatMessagesRepository:
    def __init__(self, db_path: str):
        check_file_exists(db_path)
        self.conn = sqlite3.connect(db_path)

    def update_by_id(self, message: ChatMessage, id: str) -> None:
        cursor = self.conn.cursor()
        sql = f"""
            UPDATE messages
            SET chat_id = ?, username = ?, post = ?, timestamp = ?
            WHERE id = ?;
        """
        cursor.execute(sql, to_record(message, id))
        self.conn.commit()

    def add(self, message: ChatMessage) -> str:
        cursor = self.conn.cursor()
        sql = f"""
            INSERT INTO messages (chat_id, username, post, timestamp, id)
            VALUES (?, ?, ?, ?, ?);
        """
        new_id = str(uuid4())
        cursor.execute(sql, to_record(message, new_id))
        self.conn.commit()
        return new_id

    def delete_by_chat_id(self, chat_id: str) -> None:
        cursor = self.conn.cursor()
        sql = f"""
            DELETE FROM messages
            WHERE chat_id = ?;
        """
        cursor.execute(sql, (chat_id,))
        self.conn.commit()

    def fetch_last_messages_by_chat_id(
        self, chat_id: str, limit: int = 1000
    ) -> List[ChatMessage]:
        check_required(limit, "limit", int)
        check_range(limit, "limit", 1, 1000)
        cursor = self.conn.cursor()
        sql = f"""
            SELECT chat_id, username, post, timestamp
            FROM messages
            WHERE chat_id = ?
            ORDER BY timestamp DESC
            LIMIT {limit};
        """
        cursor.execute(sql, (chat_id,))
        records = cursor.fetchall()
        self.conn.commit()
        return [from_record(r) for r in records][::-1]

        

-- Postgres SQL

CREATE TABLE chat_messages (
    id TEXT PRIMARY KEY,
    timestamp INT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT NOT NULL,
    username TEXT NOT NULL, 
    chat TEXT NOT NULL,
    messenger TEXT NOT NULL,
    role TEXT NOT NULL,
    bot TEXT NOT NULL
);

'''


DB_NAME = "chat_messages"


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
        migrator = PostgresMigrator(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            schemas=self._schemas,
        )
        migrator.migrate(DB_NAME, str(Path(__file__).parent / "migrations"))

    def add(self, message: ChatMessage) -> str:
        cursor = self._conn.cursor()
        sql = f"""
            INSERT INTO messages (id, timestamp, content, content_type, user, chat, messenger, role, created_by)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ;
        """
        new_id = str(uuid4())
        cursor.execute(
            sql,
            (
                new_id,
                message.timestamp(),
                message.content(),
                message.content_type(),
                message.user(),
                message.chat(),
                message.messenger(),
                message.role(),
                message.created_by(),
            ),
        )
        self._conn.commit()
        return new_id

    def fetch_last_messages_by_chat_id(
        self, chat_id: str, limit: int = 1000
    ) -> List[ChatMessage]:
        raise NotImplementedError()
