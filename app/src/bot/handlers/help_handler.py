from app.tao.bot.tao_bot.tao_bot_update import TaoBotUpdate

from app.tao.ui_text import cfg_message
from app.tao.tao_config import TaoConfig


def get_help_command_hadler(config: TaoConfig):
    def handler(update: TaoBotUpdate) -> str:
        return cfg_message(config.cfg)
    return handler
