from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf
from app.src.bot.tao_bot.tao_bot_update import TaoBotUpdate
from app.src.bot.tao_bot.ui_text import cfg_message
from app.src.gpt.gpt_conf import GptConf


def get_help_command_handler(tao_bot_conf: TaoBotConf, gpt_conf: GptConf):
    def handler(update: TaoBotUpdate) -> str:
        return cfg_message(tao_bot_conf, gpt_conf)
    return handler
