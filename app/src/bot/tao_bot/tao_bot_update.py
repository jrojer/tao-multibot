from typing import Optional
from app.src.internal.audio.voice import Voice
from app.src.butter.checks import check_required, check_that, check_type


class TaoBotUpdate:
    class Builder:
        def __init__(self):
            # TODO consider adding a reference to a message being replied to
            self._chat_id: str = None
            self._from_user: str = None
            self._post: str = None
            self._voice: Voice = None
            self._chat_name: str = None
            self._timestamp: int = None
            self._is_reply_to_bot: bool = False
            self._is_dm_to_bot: bool = False
            self._is_chat_mention_of_bot: bool = False

        def chat_id(self, chat_id):
            self._chat_id = chat_id
            return self

        def from_user(self, from_user):
            self._from_user = from_user
            return self

        def post(self, post):
            self._post = post
            return self

        def voice(self, voice: Voice) -> "TaoBotUpdate.Builder":
            self._voice = voice
            return self

        def chat_name(self, chat_name):
            self._chat_name = chat_name
            return self

        def timestamp(self, timestamp):
            self._timestamp = timestamp
            return self

        def is_reply_to_bot(self, is_reply_to_bot):
            self._is_reply_to_bot = is_reply_to_bot
            return self

        def is_dm_to_bot(self, is_dm_to_bot):
            self._is_dm_to_bot = is_dm_to_bot
            return self

        def is_chat_mention_of_bot(self, is_chat_mention_of_bot: bool):
            self._is_chat_mention_of_bot = is_chat_mention_of_bot
            return self

        def build(self):
            return TaoBotUpdate(self)

    def __init__(self, builder: Builder):
        self._chat_id = check_required(builder._chat_id, "chat_id", str)
        self._from_user = check_required(builder._from_user, "from_user", str)
        self._post = check_type(builder._post, "post", str)
        self._voice = check_type(builder._voice, "voice", Voice)
        check_that(
            builder._post is not None or builder._voice is not None,
            "Tao update must contain a post or a voice",
        )
        self._chat_name = check_required(builder._chat_name, "chat_name", str)
        self._timestamp = check_required(builder._timestamp, "timestamp", int)
        self._is_reply_to_bot = check_type(
            builder._is_reply_to_bot, "is_reply_to_bot", bool
        )
        self._is_dm_to_bot = check_type(builder._is_dm_to_bot, "is_dm_to_bot", bool)
        self._is_chat_mention_of_bot = check_type(
            builder._is_chat_mention_of_bot, "is_chat_mention_of_bot", bool
        )

    @staticmethod
    def new() -> "TaoBotUpdate.Builder":
        return TaoBotUpdate.Builder()

    def chat_id(self) -> str:
        return self._chat_id

    def from_user(self) -> str:
        return self._from_user

    def post(self):
        return self._post

    def voice(self) -> Optional[Voice]:
        return self._voice

    def chat_name(self):
        return self._chat_name

    def timestamp(self) -> int:
        return self._timestamp

    def is_reply_to_bot(self):
        return self._is_reply_to_bot

    def is_dm_to_bot(self):
        return self._is_dm_to_bot

    def is_chat_mention_of_bot(self):
        return self._is_chat_mention_of_bot
