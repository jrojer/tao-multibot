import re
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate

from app.src.tao_config import TaoConfig


def get_update_access_handler(config: TaoConfig):
    def handler(update: TaoBotUpdate) -> str:
        enabled_for = []
        disabled_for = []
        for username in re.findall(r'\+(\w+)', update.post()):
            config.enable_for_username(username)
            enabled_for.append(username)
        for username in re.findall(r'\-(\w+)', update.post()):
            config.disable_for_username(username)
            disabled_for.append(username)
        return f'Enabled for {enabled_for}, disabled for {disabled_for}'
    return handler
