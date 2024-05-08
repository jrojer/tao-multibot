
from typing import Any
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.gpt.gpt_conf import GptConf
from app.src.server.master_config.openai_conf_view import GptConfView
from app.src.server.master_config.tao_bot_conf_view import TaoBotConfView
from app.src.server.master_config.tg_bot_conf import TgBotConf


class TgBotConfView(TgBotConf):
    def __init__(self, mem: list[dict[str, Any]], bot_id: str):
        self._mem = mem
        self._bot_id = bot_id
        self._tao_bot_conf: TaoBotConf = TaoBotConfView(mem, bot_id)
        self._openai_conf: GptConf = GptConfView(mem, bot_id)

    def bot_id(self) -> str:
        return self._bot_id

    def token(self) -> str:
        return self._mem[0][self._bot_id]["tg_bot"]["token"]
    
    def tao_bot_conf(self) -> TaoBotConf:
        return self._tao_bot_conf
    
    def openai_conf(self) -> GptConf:
        return self._openai_conf
