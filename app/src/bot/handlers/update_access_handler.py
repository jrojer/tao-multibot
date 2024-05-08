import re
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.server.api.api_client import ApiClient


def get_update_access_handler(client: ApiClient):
    def handler(update: TaoBotUpdate) -> str:
        enabled_for: list[str] = []
        disabled_for: list[str] = []
        for username in re.findall(r'\+(\w+)', update.post()):
            client.enable_for_username(username)
            enabled_for.append(username)
        for username in re.findall(r'\-(\w+)', update.post()):
            client.disable_for_username(username)
            disabled_for.append(username)
        return f'Enabled for {enabled_for}, disabled for {disabled_for}'
    return handler
