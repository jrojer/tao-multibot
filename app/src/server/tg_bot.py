from app.src.butter.checks import check_required
from app.src.bot.tao_bot.tao_bot_conf import TgBotConf
from app.src.observability.logger import Logger


logger = Logger(__name__)


class TgBot:
    def __init__(self, conf: TgBotConf):
        self._conf = check_required(conf, "conf", TgBotConf)

    def start(self, conf: TgBotConf):
        logger.info(f"Starting bot {self._conf.bot_id()}, {conf.username()}")

    def stop(self):
        logger.info(f"Stopping bot {self._conf.bot_id()}")
