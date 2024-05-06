from typing import Optional
from telegram.ext import Application, MessageHandler, filters
from telegram.ext import ContextTypes
from telegram import Update, Message
from telegram.error import BadRequest
from app.src.bot.tao_bot.tao_bot import TaoBot
from app.src.bot.tao_bot.tao_bot_commands import TaoBotCommands, TaoBotResponse
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.butter.checks import check_required
from app.src.butter.clock import timestamp_now
from app.src.butter.functional import first_present
from app.src.observability.logger import Logger
from app.src.heads.tg_bot.v1.tg_voice import TgVoice
from app.src.heads.tg_bot.v1.typing_action import TypingAction
from app import env

logger = Logger(__name__)


def extract_username(update: Update):
    message: Message = update.message
    return first_present(
        [
            lambda: message.chat.username,
            lambda: (
                message.forward_from.username
                if message.forward_from is not None
                else None
            ),
            lambda: message.forward_sender_name,
            lambda: message.from_user.username,
        ]
    )


def extract_chat_id(update: Update) -> str:
    topic_id = ""
    if (
        update.message.is_topic_message is not None
        and update.message.is_topic_message == True
        and update.message.message_thread_id is not None
    ):
        topic_id = "/" + str(update.message.message_thread_id)
    return str(update.message.chat_id) + topic_id


def is_direct_message(message: Message):
    return message.chat.first_name is not None


def is_reply_to_bot(message: Message, bot_username: str):
    return (
        message.reply_to_message is not None
        and message.reply_to_message.from_user.username == bot_username
    )


def is_chat_mention_of_bot(message: Message, bot_username: str):
    return f"@{bot_username}" in message.text


def contains_bot_name(text: str) -> bool:
    if text is None:
        return False

    def capitalised(name: str):
        return name[0].upper() + name[1:]

    return any(
        (name in text or capitalised(name) in text) for name in env.BOT_NAME_LIST
    )


async def safe_reply_markdown(update: Update, post: str) -> None:
    try:
        await update.message.reply_markdown(post)
    except BadRequest:
        # TODO: find out why bot generated post is not accepted. This leads to ugly messages sometimes.
        await update.message.reply_text(post)


class TgApplication:
    def __init__(self, bot: TaoBot, bot_commands: TaoBotCommands, tg_token: str):
        self.bot = check_required(bot, "bot", TaoBot)
        self.commands = check_required(bot_commands, "bot_commands", TaoBotCommands)
        self.application = Application.builder().token(tg_token).build()
        self.application.add_handler(
            MessageHandler(filters.TEXT | filters.VOICE, self.create_handler())
        )
        self.tg_bot = self.application.bot

    def to_tao_update(
        self, update: Update, transcription: Optional[str] = None
    ) -> TaoBotUpdate:
        check_required(update.message, "update.message")
        username = extract_username(update)
        if username is None:
            logger.error("Could not extract username from update: %s", update)
            username = "unknown"
        return (
            TaoBotUpdate.new()
            .chat_id(extract_chat_id(update))
            .from_user(username)
            .chat_name(update.message.chat.effective_name)
            .post(update.message.text if transcription is None else f"{transcription}")
            .timestamp(timestamp_now())
            .is_reply_to_bot(is_reply_to_bot(update.message, self.bot.bot_username()))
            .is_dm_to_bot(is_direct_message(update.message))
            .is_chat_mention_of_bot(
                is_chat_mention_of_bot(update.message, self.bot.bot_username())
                or contains_bot_name(transcription)
            )
            .build()
        )

    def start(self):
        # Run the bot until the user presses Ctrl-C
        self.application.run_polling()

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

            if not self.bot.is_authorised(
                extract_username(update), extract_chat_id(update)
            ):
                return

            if update.message.voice is not None:
                transcription = await TgVoice(
                    self.tg_bot, update.message.voice
                ).transcribe()
                tao_update = self.to_tao_update(update, transcription)
            else:
                tao_update = self.to_tao_update(update)

            commands_response = self.commands.handle_command(
                self.bot.bot_username(), tao_update
            )
            if not commands_response.no_reply():
                post: str = await commands_response.reply_action()
                await safe_reply_markdown(update, post)
                return

            bot_response: TaoBotResponse = await self.bot.process_incoming_update(
                tao_update
            )

            # TODO: change to has_reply()
            if not bot_response.no_reply():
                with TypingAction.show_typing(self.tg_bot, tao_update.chat_id()):
                    post: str = await bot_response.reply_action()

                if post is not None:
                    await safe_reply_markdown(update, post)

            # TODO: rename postreply to something more suitable
            if bot_response.has_postreply():
                await bot_response.postreply_action()

        return async_handle
