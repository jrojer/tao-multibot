from typing import Any
from app.src.butter.checks import check_required, check_type
from app.src.butter.clock import timestamp_now, timestamp_to_readable_datetime
from app.src.butter.functional import or_else

from uuid import uuid4


class ChatMessage:
    class Builder:
        def __init__(self):
            self._id = None
            self._chat_id = None
            self._username = None
            self._post = None
            self._timestamp_value = None

        def id(self, id: str) -> "ChatMessage.Builder":
            self._id = id
            return self

        def chat_id(self, chat_id: str) -> "ChatMessage.Builder":
            self._chat_id = chat_id
            return self

        def username(self, username: str) -> "ChatMessage.Builder":
            self._username = username
            return self

        def post(self, post: str) -> "ChatMessage.Builder":
            self._post = post
            return self

        def timestamp(self, timestamp: int) -> "ChatMessage.Builder":
            self._timestamp_value = timestamp
            return self

        def build(self):
            return ChatMessage(self)

    @staticmethod
    def new():
        return ChatMessage.Builder()

    def __init__(self, builder: Builder):
        self._id = or_else(builder._id, lambda: str(uuid4())) # type: ignore
        self._chat_id = check_required(builder._chat_id, "chat_id", str) # type: ignore
        self._username = check_required(builder._username, "username", str) # type: ignore
        self._post = check_required(builder._post, "post", str) # type: ignore
        self._timestamp = or_else(
            check_type(builder._timestamp_value, "timestamp", int), timestamp_now # type: ignore
        ) 

    def id(self) -> str:
        return self._id

    def chat_id(self) -> str:
        return self._chat_id

    def username(self) -> str:
        return self._username

    def post(self) -> str:
        return self._post

    def timestamp(self) -> int:
        return self._timestamp

    def __repr__(self) -> str:
        return f"{timestamp_to_readable_datetime(self._timestamp)} {self._username}: {self._post}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "chat_id": self._chat_id,
            "username": self._username,
            "post": self._post,
            "timestamp": self._timestamp,
        }

    # NOTE: no id in the comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChatMessage):
            return False
        return (
            self._chat_id == other._chat_id
            and self._username == other._username
            and self._post == other._post
            and self._timestamp == other._timestamp
        )
