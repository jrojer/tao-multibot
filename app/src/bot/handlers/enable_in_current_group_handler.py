from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.server.api.conf_client import ConfClient


def get_enable_in_group_handler(client: ConfClient):
    def handler(update: TaoBotUpdate) -> str:
        client.enable_for_group(update.chat_id())
        return f'Enabled for chat "{update.chat_name()}"'

    return handler


def get_disable_in_group_handler(client: ConfClient):
    def handler(update: TaoBotUpdate) -> str:
        client.disable_for_group(update.chat_id())
        return f'Disabled for chat "{update.chat_name()}"'

    return handler
