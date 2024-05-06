from abc import ABC, abstractmethod
from app.src.server.master_config.bot_conf import BotConf


class TgBotConf(BotConf, ABC):
    @abstractmethod
    def token(self) -> str:
        pass
