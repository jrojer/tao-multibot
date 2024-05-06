import asyncio
from contextlib import contextmanager
from typing import Generator
import telegram
from app.src.observability.logger import Logger

logger = Logger(__name__)


class TypingAction:
    def __init__(self, bot, chat_id: str) -> None:
        self.should_stop = False
        self.bot = bot
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

        # TODO: is it ok to recreate future like this ?
        loop = asyncio.get_event_loop()
        asyncio.ensure_future(run_until_stopped(), loop=loop)
        return self

    @contextmanager
    @staticmethod
    def show_typing(bot, chat_id: str) -> Generator[None, None, None]:
        typing_action = TypingAction(bot, chat_id)
        try:
            typing_action.show()
            yield
        finally:
            typing_action.stop()
