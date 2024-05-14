from app.src.butter.checks import check_that
from app.src.observability.logger import Logger
from app.src.third_party.flyway.migrator import Migrator
from app.src.internal.shell.command import Command

logger = Logger(__name__)


class PostgresMigrator(Migrator):
    def __init__(self, host: str, port: int, user: str, password: str, schemas: str):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._schemas = schemas

    def migrate(self, db_name: str, dir: str) -> None:
        logger.info("Migrating database %s with Flyway", db_name)
        cmd = Command(
            [
                "flyway",
                f"-user={self._user}",
                f"-password={self._password}",
                f"-schemas={self._schemas}",
                f"-url=jdbc:postgresql://{self._host}:{self._port}/{db_name}",
                "migrate",
                "-locations=filesystem:" + dir,
            ]
        ).exec()
        check_that(cmd.returncode() == 0, f"Flyway migration failed: {cmd.stderr()}")
