from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.server.api.api_client import ApiClient


def get_enable_in_group_handler(client: ApiClient):
    def handler(update: TaoBotUpdate) -> str:
        client.enable_in_group(update.chat_id())
        return f'Enabled for chat {update.chat_name()} (id={update.chat_id()})'
    return handler


def get_disable_in_group_handler(client: ApiClient):
    def handler(update: TaoBotUpdate) -> str:
        client.disable_for_group(update.chat_id())
        return f'Disabled for chat {update.chat_name()} (id={update.chat_id()})'
    return handler
