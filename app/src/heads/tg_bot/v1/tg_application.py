from typing import Optional
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update, Message
from telegram.error import BadRequest
from app.src.bot.tao_bot.tao_bot import TaoBot
from app.src.bot.tao_bot.tao_bot_commands import TaoBotCommands
from app.src.bot.tao_bot.tao_bot_commands_response import TaoBotCommandsResponse
from app.src.bot.tao_bot.tao_bot_response import TaoBotResponse
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.butter.checks import check_required
from app.src.butter.clock import timestamp_now
from app.src.butter.functional import first_present
from app.src.gpt.chatform_message import ChatformMessage
# from app.src.gpt.simple_image_text_completer import SimpleImageTextCompleter
from app.src.heads.tg_bot.v1.error_handler import error_handler
from app.src.heads.tg_bot.v1.tg_bot_wrapper import TgBotWrapper
from app.src.heads.tg_bot.v1.tg_content_downloader import TgContentDownloader
from app.src.internal.audio.audio_file import AudioFile
from app.src.internal.audio.audio_transcriptor import AudioTranscriptor
from app.src.internal.audio.ogg_wav_converter import OgaWavConverter
# from app.src.internal.image.image import Image
from app.src.observability.logger import Logger
from app.src.heads.tg_bot.v1.tg_voice import TgVoice
from app.src.heads.tg_bot.v1.typing_action import TypingAction

logger = Logger(__name__)


def extract_username(update: Update) -> str:
    username = "unknown"
    message: Optional[Message] = update.message
    if message is None:
        return username

    username = first_present(
        [
            lambda: message.chat.username,
            lambda: (
                message.from_user.username if message.from_user is not None else None
            ),
        ]
    )
    if username is None:
        logger.error("Could not extract username from update: %s", update)
    return username


def extract_chat_id(update: Update) -> str:
    topic_id = ""
    message: Message = check_required(update.message, "update.message", Message)
    if (
        message.is_topic_message is not None
        and message.is_topic_message == True
        and message.message_thread_id is not None
    ):
        topic_id = "/" + str(message.message_thread_id)
    return str(message.chat_id) + topic_id


def is_direct_message(message: Message) -> bool:
    return message.chat.first_name is not None


def is_reply_to_bot(message: Message, bot_username: str) -> bool:
    return (
        message.reply_to_message is not None
        and message.reply_to_message.from_user is not None
        and message.reply_to_message.from_user.username == bot_username
    )


def is_chat_mention_of_bot(message: Message, bot_username: str) -> bool:
    return message.text is not None and f"@{bot_username}" in message.text


def contains_bot_name(text: Optional[str], name_list: list[str]) -> bool:
    if text is None:
        return False

    def capitalised(name: str) -> str:
        return name[0].upper() + name[1:]

    return any((name in text or capitalised(name) in text) for name in name_list)


def _post_mentioned(message: Message) -> Optional[str]:
    PREVIEW_LENGTH = 65
    reply = message.reply_to_message
    if reply is not None and reply.text is not None:
        return reply.text[:PREVIEW_LENGTH]


async def safe_reply_markdown(update: Update, post: str) -> None:
    message: Message = check_required(update.message, "update.message", Message)
    try:
        await message.reply_markdown(post)
    except BadRequest:
        # TODO: find out why bot generated post is not accepted. This leads to ugly messages sometimes.
        logger.warning("Failed to reply markdown, trying plain text.\n'''%s\n'''", post)
        await message.reply_text(post)


class TgApplication:
    def __init__(
        self,
        bot: TaoBot,
        bot_commands: TaoBotCommands,
        tg_token: str,
        openai_token: str,
    ):
        self._bot: TaoBot = check_required(bot, "bot", TaoBot)
        self._commands: TaoBotCommands = check_required(
            bot_commands, "bot_commands", TaoBotCommands
        )
        self._application = Application.builder().token(tg_token).build()
        self._application.add_handler(
            MessageHandler(
                filters.TEXT | filters.VOICE | filters.PHOTO, self.create_handler()
            )
        )
        self._application.add_error_handler(error_handler)
        self._tg_bot: TgBotWrapper = TgBotWrapper(self._application.bot)
        self._openai_token = check_required(openai_token, "openai_token", str)

    def to_tao_update(
        self,
        update: Update,
    ) -> TaoBotUpdate.Builder:
        message: Message = check_required(update.message, "update.message", Message)
        username = extract_username(update)

        return (
            TaoBotUpdate.new()
            .chat_id(extract_chat_id(update))
            .from_user(username)
            .chat_name(message.chat.effective_name)
            .content(message.text)  # type: ignore
            .content_type("text")
            .post_mentioned(_post_mentioned(message))
            .timestamp(timestamp_now())
            .is_reply_to_bot(is_reply_to_bot(message, self._bot.bot_username()))
            .is_dm_to_bot(is_direct_message(message))
            .is_chat_mention_of_bot(
                is_chat_mention_of_bot(message, self._bot.bot_username())
            )
        )

    def start(self):
        self._application.run_polling()

    def stop(self):
        self._application.stop_running()

    def create_handler(self):
        async def async_handle(
            update: Update, context: ContextTypes.DEFAULT_TYPE
        ) -> None:
            if update.message is None:
                if update.edited_message is not None:
                    logger.info("Skipping edited message")
                    return
                logger.error("Received unexpected update without a message: %s", update)
                return

            if not self._bot.is_authorised(
                extract_username(update), extract_chat_id(update)
            ):
                return

            # TODO: move the downloading/trascription logic to the TaoBot
            #       and just pass the update containing content_type and url to the bot
            if update.message.voice is not None:
                ogg_file: AudioFile = await TgContentDownloader(
                    self._tg_bot.token()
                ).download(update.message.voice.file_id)
                transcription = await TgVoice(
                    AudioTranscriptor(self._openai_token), OgaWavConverter()
                ).transcribe(ogg_file)
                tao_update = (
                    self.to_tao_update(update)
                    .content(transcription)
                    .is_chat_mention_of_bot(
                        contains_bot_name(transcription, self._bot.bot_mention_names())
                    )
                    .build()
                )
            elif len(update.message.photo) > 0:
                image_ref = update.message.photo[-1].file_id
                # TODO: consider making content field optional or putting ref in the content field
                description = "An image"
                tao_update = (
                    self.to_tao_update(update)
                    .content(description)
                    .ref(image_ref)
                    .content_type("jpg")
                    .build()
                )
            else:
                tao_update = self.to_tao_update(update).build()

            commands_response: TaoBotCommandsResponse = self._commands.handle_command(
                self._bot.bot_username(), tao_update
            )
            if commands_response.reply_action is not None:
                command_response: str = await commands_response.reply_action()
                await safe_reply_markdown(update, command_response)
                return

            bot_response: TaoBotResponse = await self._bot.process_incoming_update(
                tao_update
            )

            if bot_response.reply_action is not None:
                with TypingAction.show_typing(self._tg_bot, tao_update.chat_id()):
                    chat_message: ChatformMessage = await bot_response.reply_action()
                    await safe_reply_markdown(
                        update, check_required(chat_message.content(), "content", str)
                    )

            if bot_response.postreply_action is not None:
                await bot_response.postreply_action()

        return async_handle
