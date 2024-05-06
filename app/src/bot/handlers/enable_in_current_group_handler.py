from app.tao.bot.tao_bot.tao_bot_update import TaoBotUpdate

from app.tao.tao_config import TaoConfig


def get_enable_in_group_handler(config: TaoConfig):
    def handler(update: TaoBotUpdate) -> str:
        config.enable_for_chat(update.chat_id())
        return f'Enabled for chat {update.chat_name()} (id={update.chat_id()})'
    return handler


def get_disable_in_group_handler(config: TaoConfig):
    def handler(update: TaoBotUpdate) -> str:
        config.disable_for_chat(update.chat_id())
        return f'Disabled for chat {update.chat_name()} (id={update.chat_id()})'
    return handler
