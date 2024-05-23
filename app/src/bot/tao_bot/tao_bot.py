from typing import Optional
from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.content_type import ContentType
from app.src.bot.repo.chat_messages_repository.role import Role
from app.src.bot.repo.chat_messages_repository.source import Source
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_response import TaoBotResponse, reply
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.butter.checks import check_required, check_that
from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import (
    ChatformMessage,
    assistant_message,
    image_message,
    user_message,
)
from app.src.gpt.gpt_gateway import GptGateway
from app.src.internal.common.content_downloader import ContentDownloader
from app.src.internal.common.message_sender import MessageSender
from app.src.internal.image.image import Image
from app.src.observability.logger import Logger
from app.src.observability.metrics_client.influxdb_metrics_client import MetricsReporter
# from app.src.plugins.code_executor.code_executor_plugin import CodeExecutorPlugin


logger = Logger(__name__)
metrics = MetricsReporter()


def _log_update(update: TaoBotUpdate, text: str, cf_size: int = 0):
    logger.info(
        text + " %s@%s-%s[%s]: %s",
        update.from_user(),
        update.chat_name(),
        update.chat_id(),
        cf_size,
        update.content(),
    )


def _should_reply(update: TaoBotUpdate):
    return (
        update.is_reply_to_bot()
        or update.is_dm_to_bot()
        or update.is_chat_mention_of_bot()
    ) and (update.content_type() == "text")


def _a_chat_messasge_from(update: TaoBotUpdate, bot_username: str) -> ChatMessage:
    content_type = ContentType.TEXT
    if update.content_type() == "jpg":
        content_type = ContentType.JPG

    message = (
        ChatMessage.new()
        .timestamp(update.timestamp())
        .content(update.content())
        .content_type(content_type)
        .user(update.from_user())
        .chat(update.chat_id())
        .source(Source.TELEGRAM)
        .role(Role.USER)
        .added_by(bot_username)
        .reply_to(update.post_mentioned())
        .ref(update.ref())
        .build()
    )
    return message


class TaoBot:
    def __init__(
        self,
        messages_repo: ChatMessagesRepository,
        gateway: GptGateway,
        config: TaoBotConf,
        # TODO: revise dependencies
        content_downloader: ContentDownloader,
        message_sender: MessageSender,
    ) -> None:
        self._messages_repo: ChatMessagesRepository = check_required(
            messages_repo, "chat_messages_repo", ChatMessagesRepository
        )
        self._gateway: GptGateway = check_required(gateway, "gpt_gateway", GptGateway)
        self._conf: TaoBotConf = check_required(config, "config", TaoBotConf)
        self._content_downloader: ContentDownloader = check_required(
            content_downloader, "content_downloader", ContentDownloader
        )
        self._message_sender: MessageSender = check_required(
            message_sender, "message_sender", MessageSender
        )

    def bot_username(self) -> str:
        return self._conf.username()

    def bot_mention_names(self) -> list[str]:
        return self._conf.bot_mention_names()

    def is_authorised(self, from_user: str, chat_id: Optional[str]):
        cfg = self._conf
        authorised = (
            (chat_id is not None and chat_id == cfg.control_chat_id())
            or chat_id in cfg.chats()
            or from_user in cfg.users()
            or from_user in cfg.admins()
        )
        if not authorised:
            logger.warning(
                "Not enabled chat. Chat id: %s. From user: %s.", chat_id, from_user
            )
        return authorised

    async def _build_chatform(self, chat_id: str) -> Chatform:
        system_prompt = self._conf.system_prompt()
        chatform = Chatform(system_prompt)
        messages = self._messages_repo.fetch_last_messages_by_chat_and_adder(
            chat_id, self.bot_username(), self._conf.number_of_messages_per_completion()
        )
        for m in messages:
            content = m.content()

            if m.reply_to() is not None and content is not None:
                content = f"{content} (Ref.: {m.reply_to()})"

            if m.user() == self.bot_username():
                chatform.add_message(
                    assistant_message(check_required(content, "content", str))
                )
            elif m.content_type() == ContentType.JPG:
                # TODO: consider decreasing image resolution for old images (more than 1 hour old)
                image: Image = await self._content_downloader.download(
                    check_required(m.ref(), "ref", str)
                )
                chatform.add_message(
                    image_message(
                        image_url=f"data:image/jpeg;base64,{image.as_base64()}",
                        name=m.user(),
                    )
                )
                if content is not None:
                    chatform.add_message(user_message(content, m.user()))
            else:
                chatform.add_message(
                    user_message(check_required(content, "content", str), m.user())
                )
        return chatform

    def _report_usage(self, messages: list[ChatformMessage], update: TaoBotUpdate):
        for message in messages:
            usage = message.usage()
            if usage is None:
                return
            metrics.write(
                measurement="usage",
                tags={
                    "bot": self.bot_username(),
                    "chat": update.chat_name(),
                    "chat_id": update.chat_id(),
                    "user": update.from_user(),
                },
                fields={
                    "usage": str(usage.completion_tokens() + usage.prompt_tokens())
                },
            )

    async def process_incoming_update(self, update: TaoBotUpdate) -> TaoBotResponse:
        check_that(
            self.is_authorised(update.from_user(), update.chat_id()),
            "tao update must be authorised",
        )

        _log_update(update, "Noted")

        # TODO: consider adding a separate layer class that manages db, summariser, etc. and calls tao-bot process function
        self._messages_repo.add(_a_chat_messasge_from(update, self.bot_username()))

        async def postreply_action():
            pass

        if not _should_reply(update):
            return reply(None, postreply_action)

        chatform: Chatform = await self._build_chatform(update.chat_id())

        # TODO: as process_incoming_update became async, consider simplifying this nested async
        async def reply_action() -> ChatformMessage:
            _log_update(update, "Processing")

            # async def send_message(message: str):
                # await self._message_sender.send_text(update.chat_id(), message, username="function")

            reply_messages: list[ChatformMessage] = await self._gateway.forward(
                chatform,
                # [CodeExecutorPlugin(on_success=send_message)],
                [],
            )

            self._report_usage(
                reply_messages,
                update,
            )

            reply_message = reply_messages[-1]

            bot_message = (
                ChatMessage.new()
                .content(check_required(reply_message.content(), "content", str))
                .content_type(ContentType.TEXT)
                .user(self.bot_username())
                .chat(update.chat_id())
                .source(Source.TELEGRAM)
                .role(Role.ASSISTANT)
                .added_by(self.bot_username())
                .build()
            )

            # fmt: off
            logger.info("Replying %s@%s-%s: %s", self.bot_username(), update.chat_name(), update.chat_id(), reply_message.content())
            # fmt: on

            self._messages_repo.add(bot_message)
            return reply_message

        return reply(reply_action, postreply_action)
