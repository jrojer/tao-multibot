from app.tao.bot.tao_bot.tao_bot_update import TaoBotUpdate

from app.tao.ui_text import START_MESSAGE


def get_start_handler():
    def handler(update: TaoBotUpdate) -> str:
        return START_MESSAGE
    return handler
