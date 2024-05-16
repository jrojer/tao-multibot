from typing import Any, Optional
from app.src.bot.repo.chat_messages_repository.content_type import ContentType
from app.src.bot.repo.chat_messages_repository.role import Role
from app.src.bot.repo.chat_messages_repository.source import Source
from app.src.butter.checks import check_required, check_optional
from app.src.butter.clock import timestamp_now, timestamp_to_readable_datetime
from app.src.butter.functional import or_else

from uuid import uuid4


class ChatMessage:
    class Builder:
        def __init__(self):
            self._id = None
            self._timestamp = None
            self._content = None
            self._content_type = None
            self._user = None
            self._chat = None
            self._source = None
            self._role = None
            self._added_by = None
            self._reply_to = None

        def id(self, id: str) -> "ChatMessage.Builder":
            self._id = id
            return self

        def timestamp(self, timestamp: int) -> "ChatMessage.Builder":
            self._timestamp = timestamp
            return self

        def content(self, content: str) -> "ChatMessage.Builder":
            self._content = content
            return self

        def content_type(self, content_type: ContentType) -> "ChatMessage.Builder":
            self._content_type = content_type.value
            return self

        def user(self, user: str) -> "ChatMessage.Builder":
            self._user = user
            return self

        def chat(self, chat: str) -> "ChatMessage.Builder":
            self._chat = chat
            return self

        def source(self, source: Source) -> "ChatMessage.Builder":
            self._source = source.value
            return self

        def role(self, role: Role) -> "ChatMessage.Builder":
            self._role = role.value
            return self

        def added_by(self, added_by: str) -> "ChatMessage.Builder":
            self._added_by = added_by
            return self

        def reply_to(self, reply_to: Optional[str]) -> "ChatMessage.Builder":
            self._reply_to = reply_to
            return self
        
        def build(self):
            return ChatMessage(self)

    @staticmethod
    def new():
        return ChatMessage.Builder()

    def __init__(self, builder: Builder):
        self._id = or_else(builder._id, lambda: str(uuid4()))  # type: ignore
        self._timestamp = or_else(
            check_optional(builder._timestamp, "timestamp", int), timestamp_now  # type: ignore
        )
        self._content = check_required(builder._content, "content", str)  # type: ignore
        self._content_type = check_required(builder._content_type, "content_type", str)  # type: ignore
        self._user = check_required(builder._user, "user", str)  # type: ignore
        self._chat = check_required(builder._chat, "chat", str)  # type: ignore
        self._source = check_required(builder._source, "messenger", str)  # type: ignore
        self._role = check_required(builder._role, "role", str)  # type: ignore
        self._added_by = check_required(builder._added_by, "added_by", str)  # type: ignore
        self._reply_to = check_optional(builder._reply_to, "reply_to", str)  # type: ignore

    def id(self) -> str:
        return self._id

    def timestamp(self) -> int:
        return self._timestamp

    def content(self) -> str:
        return self._content

    def content_type(self) -> ContentType:
        return ContentType.from_str(self._content_type)

    def user(self) -> str:
        return self._user

    def chat(self) -> str:
        return self._chat

    def source(self) -> Source:
        return Source.from_str(self._source)

    def role(self) -> Role:
        return Role.from_str(self._role)

    def added_by(self) -> str:
        return self._added_by

    def reply_to(self) -> Optional[str]:
        return self._reply_to
    
    def __repr__(self) -> str:
        return f"{timestamp_to_readable_datetime(self._timestamp)} {self._user}: {self._content}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self._id,
            "timestamp": self._timestamp,
            "content": self._content,
            "content_type": self._content_type,
            "chat": self._chat,
            "user": self._user,
            "source": self._source,
            "role": self._role,
            "added_by": self._added_by,
        }

    # NOTE: no id in the comparison
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, ChatMessage):
            return False
        return (
            self._timestamp == other.timestamp()
            and self._content == other.content()
            and self._content_type == other.content_type()
            and self._user == other.user()
            and self._chat == other.chat()
            and self._source == other.source()
            and self._role == other.role()
            and self._added_by == other.added_by()
            and self._reply_to == other.reply_to()
        )
