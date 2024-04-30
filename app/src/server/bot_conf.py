from abc import ABC


class BotConf(ABC):
    def bot_id(self) -> str:
        pass


class TgBotConf(BotConf):
    def username(self) -> str:
        pass

    def chats(self) -> list[str]:
        pass

    def admins(self) -> list[str]:
        pass

    def users(self) -> list[str]:
        pass

    def token(self) -> str:
        pass
