from typing import Any
from app.src.gpt.gpt_conf import GptConf


class GptConfView(GptConf):
    def __init__(self, mem: list[dict[dict[str, Any]]], bot_id: str):
        self._mem = mem
        self._bot_id = bot_id

    def _conf(self):
        return self._mem[0][self._bot_id]["openai"]

    def token(self) -> str:
        return self._conf()["token"]

    def model(self) -> str:
        return self._conf()["model"]

    def temperature(self) -> float:
        return self._conf()["temperature"]

    def max_tokens(self) -> int:
        return self._conf()["max_tokens"]
    
    def top_p(self) -> float:
        return self._conf()["top_p"]
    
    def frequency_penalty(self) -> float:
        return self._conf()["frequency_penalty"]
    
    def presence_penalty(self) -> float:
        return self._conf()["presence_penalty"]
    
