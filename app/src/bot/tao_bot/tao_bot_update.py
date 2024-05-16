from typing import Optional
from app.src.internal.audio.voice import Voice
from app.src.butter.checks import check_required, check_that, check_optional


class TaoBotUpdate:
    class Builder:
        def __init__(self):
            self._chat_id = None
            self._from_user = None
            self._content = None
            self._content_type = None
            self._post_mentioned = None
            self._voice = None
            self._chat_name = None
            self._timestamp = None
            self._is_reply_to_bot = False
            self._is_dm_to_bot = False
            self._is_chat_mention_of_bot = False
            self._ref = None

        def chat_id(self, chat_id: str):
            self._chat_id = chat_id
            return self

        def from_user(self, from_user: str):
            self._from_user = from_user
            return self

        def content(self, post: str):
            self._content = post
            return self

        # TODO: make enum
        def content_type(self, content_type: str):
            self._content_type = content_type
            return self

        def post_mentioned(self, post_mentioned: Optional[str]):
            self._post_mentioned = post_mentioned
            return self

        def voice(self, voice: Voice) -> "TaoBotUpdate.Builder":
            self._voice = voice
            return self

        def chat_name(self, chat_name: Optional[str]):
            self._chat_name = chat_name
            return self

        def timestamp(self, timestamp: int):
            self._timestamp = timestamp
            return self

        def is_reply_to_bot(self, is_reply_to_bot: bool):
            self._is_reply_to_bot = is_reply_to_bot
            return self

        def is_dm_to_bot(self, is_dm_to_bot: bool):
            self._is_dm_to_bot = is_dm_to_bot
            return self

        def is_chat_mention_of_bot(self, is_chat_mention_of_bot: bool):
            self._is_chat_mention_of_bot = is_chat_mention_of_bot
            return self

        def ref(self, ref: Optional[str]):
            self._ref = ref
            return self

        def build(self):
            return TaoBotUpdate(self)

    def __init__(self, builder: Builder):
        self._chat_id = check_required(builder._chat_id, "chat_id", str)  # type: ignore
        self._from_user = check_required(builder._from_user, "from_user", str)  # type: ignore
        self._content = check_required(builder._content, "post", str)  # type: ignore
        self._content_type = check_required(builder._content_type, "content_type", str)  # type: ignore
        self._post_mentioned = check_optional(builder._post_mentioned, "post_mentioned", str)  # type: ignore
        self._voice = check_optional(builder._voice, "voice", Voice)  # type: ignore
        check_that(
            builder._content is not None or builder._voice is not None,  # type: ignore
            "Tao update must contain a post or a voice",
        )
        self._chat_name = check_required(builder._chat_name, "chat_name", str)  # type: ignore
        self._timestamp = check_required(builder._timestamp, "timestamp", int)  # type: ignore
        self._is_reply_to_bot = check_required(
            builder._is_reply_to_bot, "is_reply_to_bot", bool  # type: ignore
        )
        self._is_dm_to_bot = check_required(builder._is_dm_to_bot, "is_dm_to_bot", bool)  # type: ignore
        self._is_chat_mention_of_bot = check_required(
            builder._is_chat_mention_of_bot, "is_chat_mention_of_bot", bool  # type: ignore
        )
        self._ref = check_optional(builder._ref, "ref", str)  # type: ignore

    @staticmethod
    def new() -> "TaoBotUpdate.Builder":
        return TaoBotUpdate.Builder()

    def chat_id(self) -> str:
        return self._chat_id

    def from_user(self) -> str:
        return self._from_user

    def content(self) -> str:
        return self._content

    def content_type(self) -> Optional[str]:
        return self._content_type

    def post_mentioned(self) -> Optional[str]:
        return self._post_mentioned

    def voice(self) -> Optional[Voice]:
        return self._voice

    def chat_name(self) -> str:
        return self._chat_name

    def timestamp(self) -> int:
        return self._timestamp

    def is_reply_to_bot(self) -> bool:
        return self._is_reply_to_bot

    def is_dm_to_bot(self) -> bool:
        return self._is_dm_to_bot

    def is_chat_mention_of_bot(self) -> bool:
        return self._is_chat_mention_of_bot

    def ref(self) -> Optional[str]:
        return self._ref
