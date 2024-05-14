from typing import Any
from app.src.butter.checks import check_required
from app.src.gpt.gpt_conf import GptConf
from app.src.server.api.conf_client import ConfClient


class GptConfClient(GptConf):
    def __init__(self, api_client: ConfClient, bot_id: str):
        self._conf_client: ConfClient = check_required(
            api_client, "conf_client", ConfClient
        )
        self._bot_id: str = bot_id

    def _conf(self) -> dict[str, Any]:
        return self._conf_client.get_bot_conf()["gpt"]

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
