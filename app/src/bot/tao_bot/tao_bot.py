from typing import Optional
from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_response import TaoBotResponse, reply
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.butter.checks import check_required, check_that
from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import assistant_message, user_message
from app.src.gpt.gpt_conf import GptConf
from app.src.gpt.gpt_gateway import GptGateway
from app.src.observability.logger import Logger


logger = Logger(__name__)


def _log_update(update: TaoBotUpdate, text: str, cf_size=0):
    logger.info(
        text + " %s@%s-%s[%s]: %s",
        update.from_user(),
        update.chat_name(),
        update.chat_id(),
        cf_size,
        update.post(),
    )


def _should_reply(update: TaoBotUpdate):
    return (
        update.is_reply_to_bot()
        or update.is_dm_to_bot()
        or update.is_chat_mention_of_bot()
    )


def _a_chat_messasge_from(update: TaoBotUpdate) -> ChatMessage:
    message = (
        ChatMessage.new()
        .chat_id(update.chat_id())
        .username(update.from_user())
        .post(update.post())
        .timestamp(update.timestamp())
        .build()
    )
    return message


class TaoBot:
    def __init__(
        self,
        messages_repo: ChatMessagesRepository,
        gateway: GptGateway,
        config: TaoBotConf,
        gpt_config: GptConf,
    ) -> None:
        self.messages_repo = check_required(
            messages_repo, "messages_repo", ChatMessagesRepository
        )
        self.gateway = check_required(gateway, "gateway", GptGateway)
        self.conf = check_required(config, "config", TaoBotConf)
        self.gpt_config = check_required(gpt_config, "gpt_config", GptConf)

    def bot_username(self):
        return self.conf.username()

    def is_authorised(self, from_user: str, chat_id: Optional[str]):
        cfg = self.conf
        authorised = (
            chat_id is not None
            and chat_id == cfg.control_chat_id()
            or chat_id in cfg.chats()
            or from_user in cfg.users()
            or from_user in cfg.admins()
        )
        if not authorised:
            logger.warning(
                "Not enabled chat. Chat id: %s. From user: %s.", chat_id, from_user
            )
        return authorised

    def _build_chatform(self, chat_id: str) -> Chatform:
        system_prompt = self.conf.system_prompt()
        chatform = Chatform(system_prompt)
        messages = self.messages_repo.fetch_last_messages_by_chat_id(
            chat_id, self.conf.number_of_messages_for_completion()
        )
        for m in reversed(messages):
            if m.username == self.bot_username():
                chatform.add_message(assistant_message(m.post))
            else:
                chatform.add_message(user_message(m.post, m.username))
        return chatform

    async def process_incoming_update(self, update: TaoBotUpdate) -> TaoBotResponse:
        check_that(
            self.is_authorised(update.from_user(), update.chat_id()),
            "tao update must be authorised",
        )

        _log_update(update, "Noted")

        # TODO: consider adding a separate layer class that manages db, summariser, etc. and calls tao-bot process function
        self.messages_repo.add(_a_chat_messasge_from(update))

        async def postreply_action():
            pass

        if not _should_reply(update):
            return reply(None, postreply_action)

        chatform: Chatform = self._build_chatform(update.chat_id())

        # TODO: as process_incoming_update became async, consider simplifying this nested async
        async def reply_action():
            _log_update(update, "Processing")

            reply_text = await self.gateway.forward(
                chatform,
                self.gpt_config,
                [],
            )
            if reply_text is None:
                return None

            bot_message = (
                ChatMessage.new()
                .chat_id(update.chat_id())
                .username(self.bot_username())
                .post(reply_text)
                .build()
            )

            # fmt: off
            logger.info("Replying %s@%s-%s: %s", self.bot_username(), update.chat_name(), update.chat_id(), reply_text)
            # fmt: on

            self.messages_repo.add(bot_message)
            return reply_text

        return reply(reply_action, postreply_action)
