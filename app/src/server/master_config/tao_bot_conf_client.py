
from typing import Any
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.butter.checks import check_required
from app.src.server.api.conf_client import ConfClient


class TaoBotConfClient(TaoBotConf):
    def __init__(self, api_client: ConfClient, bot_id: str):
        self._conf_client: ConfClient = check_required(api_client, "conf_client", ConfClient)
        self._bot_id: str = check_required(bot_id, "bot_id", str)

    def _conf(self) -> dict[str, Any]:
        return self._conf_client.get_bot_conf()["tao_bot"]

    def bot_id(self) -> str:
        return self._bot_id

    def username(self) -> str:
        return self._conf()["username"]

    def chats(self) -> list[str]:
        return self._conf()["chats"]

    def admins(self) -> list[str]:
        return self._conf()["admins"]

    def users(self) -> list[str]:
        return self._conf()["users"]
    
    def control_chat_id(self) -> str:
        return self._conf()["control_chat_id"]
    
    def system_prompt(self) -> str:
        # TODO: return actual system prompt according to the bot's configuration
        return self._conf()["system_prompt"]
    
    def number_of_messages_per_completion(self) -> int:
        return self._conf()["messages_per_completion"]
    
    def bot_mention_names(self) -> list[str]:
        return self._conf()["bot_mention_names"]
