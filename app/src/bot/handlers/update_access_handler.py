import re
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.server.api.conf_client import ConfClient


def get_update_access_handler(client: ConfClient):
    def handler(update: TaoBotUpdate) -> str:
        enabled_for: list[str] = []
        disabled_for: list[str] = []
        for username in re.findall(r"\+(\w+)", update.content()):
            client.enable_for_username(username)
            enabled_for.append(username)
        for username in re.findall(r"\-(\w+)", update.content()):
            client.disable_for_username(username)
            disabled_for.append(username)
        return f"Enabled for [{enabled_for}], disabled for [{disabled_for}]"

    return handler
