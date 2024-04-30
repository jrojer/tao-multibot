from app.src.butter.checks import check_required
from app.src.server.bot_conf import TgBotConf
from app.src.observability.logger import Logger


logger = Logger(__name__)


class TgBot:
    def __init__(self, conf: TgBotConf):
        self._conf = check_required(conf, "conf", TgBotConf)

    def start(self):
        logger.info(f"Starting bot {self._conf.bot_id()}")

    def stop(self):
        logger.info(f"Stopping bot {self._conf.bot_id()}")
        