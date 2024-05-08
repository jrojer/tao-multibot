import asyncio
from contextlib import contextmanager
from typing import Generator
import telegram
from app.src.heads.tg_bot.v1.tg_bot_wrapper import TgBotWrapper
from app.src.observability.logger import Logger

logger = Logger(__name__)


class TypingAction:
    def __init__(self, bot: TgBotWrapper , chat_id: str):
        self.should_stop = False
        self.bot: TgBotWrapper = bot
        self.chat_id = chat_id

    def stop(self) -> None:
        self.should_stop = True

    def show(self) -> "TypingAction":
        async def run_until_stopped():
            MAX_ITERATIONS = 12
            for _ in range(MAX_ITERATIONS):
                if self.should_stop:
                    break
                await self.bot.send_chat_action(
                    chat_id=self.chat_id,
                    action=telegram.constants.ChatAction.TYPING,
                )
                await asyncio.sleep(5)
            else:
                logger.error(
                    "TypingAction.show() failed to stop after %s iterations",
                    MAX_ITERATIONS,
                )

        # TODO: find out is it ok to recreate future like this
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(run_until_stopped(), loop=loop)
        return self

    @contextmanager
    @staticmethod
    def show_typing(bot: TgBotWrapper, chat_id: str) -> Generator[None, None, None]:
        typing_action = TypingAction(bot, chat_id)
        try:
            typing_action.show()
            yield
        finally:
            typing_action.stop()
