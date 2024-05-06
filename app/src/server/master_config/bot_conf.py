from abc import ABC, abstractmethod
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.gpt.gpt_conf import GptConf


class BotConf(ABC):
    @abstractmethod
    def bot_id(self) -> str:
        pass

    @abstractmethod
    def tao_bot_conf(self) -> TaoBotConf:
        pass

    @abstractmethod
    def openai_conf(self) -> GptConf:
        pass
