from typing import Optional
from app.src.bot.repo.chat_messages_repository.chat_message import ChatMessage
from app.src.bot.repo.chat_messages_repository.chat_messages_repository import (
    ChatMessagesRepository,
)
from app.src.bot.repo.chat_messages_repository.content_type import (
    ContentType as RepoContentType,
)
from app.src.bot.tao_bot.content_type import ContentType as TaoContentType
from app.src.bot.repo.chat_messages_repository.role import Role
from app.src.bot.repo.chat_messages_repository.source import Source
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_response import TaoBotResponse, reply
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.butter.checks import check_required, check_that
from app.src.gpt.chatform import Chatform
from app.src.gpt.chatform_message import (
    ChatformMessage,
    assistant_message,
    function_call_message,
    function_result_message,
    image_message,
    user_message,
)
from app.src.gpt.gpt_gateway import GptGateway
from app.src.gpt.plugin import Plugin
from app.src.internal.common.content_downloader import ContentDownloader
from app.src.internal.common.message_sender import MessageSender
from app.src.internal.image.image import Image
from app.src.observability.logger import Logger
from app.src.observability.metrics_client.influxdb_metrics_client import MetricsReporter
from app.src.plugins.code_executor.code_executor_plugin import CodeExecutorPlugin
from app.src.plugins.database_manager.remote_storage_app_plugin import (
    RemoteStorageAppPlugin,
)


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
    ) and (update.content_type() == TaoContentType.TEXT)


def _a_chat_messasge_from(update: TaoBotUpdate, bot_username: str) -> ChatMessage:
    content_type = RepoContentType.TEXT
    if update.content_type() == TaoContentType.IMAGE:
        content_type = RepoContentType.IMAGE

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


ATTACHMENT_TEMPLATE = """\
{sys_prompt}

{attachment}
"""


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

    async def with_attachments(self, chat_id: str, system_prompt: str) -> str:
        for plugin_name in self._conf.plugins():
            if plugin_name == RemoteStorageAppPlugin.name():
                attachment = await RemoteStorageAppPlugin(
                    chat_id
                ).system_prompt_attachment()
                if attachment is not None:
                    system_prompt = ATTACHMENT_TEMPLATE.format(
                        sys_prompt=system_prompt, attachment=attachment
                    )
        return system_prompt

    async def _build_chatform(self, chat_id: str) -> Chatform:
        system_prompt = await self.with_attachments(chat_id, self._conf.system_prompt())
        chatform = Chatform(system_prompt)
        # TODO: this should be modified to enable other bots messages visibility.
        #       Beware to exclude other bots function calls
        messages = self._messages_repo.fetch_last_messages_by_chat_and_adder(
            chat_id, self.bot_username(), self._conf.number_of_messages_per_completion()
        )
        for m in messages:
            # TODO: this should be rewriten with use of dedicated converter method or class. Repo message -> Chatform message
            content = m.content()

            reply_to = m.reply_to()
            if reply_to is not None and content is not None:
                content = f"(Referring to previous message: \"{reply_to.replace("\n","\\n")}\")\n\n{content}"

            if m.content_type() in [RepoContentType.FUNCTION_CALL, RepoContentType.FUNCTION_RESULT]:
                if m.user() != self.bot_username():
                    continue
                if m.content_type() == RepoContentType.FUNCTION_CALL:
                    f_name = check_required(m.function_name(), "function_name", str)
                    f_args = check_required(m.function_args(), "function_args", str)
                    chatform.add_message(function_call_message(f_name, f_args))
                else:
                    content = check_required(content, "content", str)
                    chatform.add_message(function_result_message(m.user(), content))
            elif m.user() == self.bot_username():
                chatform.add_message(
                    assistant_message(check_required(content, "content", str))
                )
            elif m.content_type() == RepoContentType.IMAGE:
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

            async def send_message(message: str):
                await self._message_sender.send_text(
                    update.chat_id(), message, username="function"
                )

            plugins: list[Plugin] = []
            for plugin_name in self._conf.plugins():
                if plugin_name == RemoteStorageAppPlugin.name():
                    plugins.append(RemoteStorageAppPlugin(update.chat_id()))
                if plugin_name == CodeExecutorPlugin.name():
                    plugins.append(CodeExecutorPlugin(on_success=send_message))

            reply_messages: list[ChatformMessage] = await self._gateway.forward(
                chatform,
                plugins,
            )

            self._report_usage(
                reply_messages,
                update,
            )

            # fmt: off
            logger.info("Replying %s@%s-%s: %s", self.bot_username(), update.chat_name(), update.chat_id(), reply_messages[-1].content())
            # fmt: on

            for reply_message in reply_messages:
                self._messages_repo.add(
                    _chat_message(reply_message, update.chat_id(), self.bot_username())
                )

            return reply_messages[-1]

        return reply(reply_action, postreply_action)


def _chat_message(
    chatform_message: ChatformMessage, chat_id: str, bot_username: str
) -> ChatMessage:

    role = Role.ASSISTANT
    f_name: Optional[str] = None
    f_args: Optional[str] = None
    content: Optional[str] = None
    content_type: RepoContentType = RepoContentType.TEXT
    if chatform_message.is_function_call_result():
        user = check_required(chatform_message.name(), "name", str)
        content = check_required(chatform_message.content(), "content", str)
        role = Role.FUNCTION
        content_type = RepoContentType.FUNCTION_RESULT
    elif chatform_message.is_function_call():
        user = bot_username
        fc: ChatformMessage.FunctionCall = check_required(
            chatform_message.function_call(),
            "function_call",
            ChatformMessage.FunctionCall,
        )
        # TODO: consider putting GPT-instructing text into a separate module. It may affect the behavior as does prompting.
        content = None
        f_name = fc.name()
        f_args = fc.arguments()
        content_type = RepoContentType.FUNCTION_CALL
    else:
        user = bot_username
        content = check_required(chatform_message.content(), "content", str)

    return (
        ChatMessage.new()
        .content(content)
        .content_type(content_type)
        .user(user)
        .chat(chat_id)
        .source(Source.TELEGRAM)
        .role(role)
        .added_by(bot_username)
        .function_name(f_name)
        .function_args(f_args)
        .build()
    )
