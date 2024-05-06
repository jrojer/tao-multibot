from typing import List
from uuid import uuid4

from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import ChatMessagesRepository
from app.src.butter.checks import check_range, check_required


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


'''
reference:


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

'''

class PostgresChatMessagesRepository(ChatMessagesRepository):
    def __init__(self, db: Database):
        self.db = db

    def update_by_id(self, message: ChatMessage, id: str) -> None:
        sql = """
            UPDATE messages
            SET chat_id = $1, username = $2, post = $3, timestamp = $4
            WHERE id = $5;
        """
        self.db.execute(sql, to_record(message, id))

    def add(self, message: ChatMessage) -> str:
        sql = """
            INSERT INTO messages (chat_id, username, post, timestamp, id)
            VALUES ($1, $2, $3, $4, $5)
            RETURNING id;
        """
        return self.db.execute(sql, to_record(message, str(uuid4())))[0][0]

    def delete_by_chat_id(self, chat_id: str) -> None:
        sql = """
            DELETE FROM messages
            WHERE chat_id = $1;
        """
        self.db.execute(sql, (chat_id,))

    def fetch_last_messages_by_chat_id(
        self, chat_id: str, limit: int = 1000
    ) -> List[ChatMessage]:
        check_required(limit, "limit", int)
        check_range(limit, "limit", 1, 1000)
        sql = """
            SELECT chat_id, username, post, timestamp
            FROM messages
            WHERE chat_id = $1
            ORDER BY timestamp DESC
            LIMIT $2;
        """
        records = self.db.execute(sql, (chat_id, limit))
        return [from_record(r) for r in records][::-1]

