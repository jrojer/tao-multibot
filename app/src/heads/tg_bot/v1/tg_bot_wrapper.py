from app.src.butter.checks import check_required


class TgBotWrapper:
    def __init__(self, bot): # type: ignore
        self.bot = check_required(bot, "bot")

    async def send_chat_action(self, chat_id: str, action: str) -> None:
        await self.bot.send_chat_action(chat_id, action)

    async def get_file(self, file_id: str):
        return await self.bot.get_file(file_id)
    
    def token(self) -> str:
        return self.bot.token
