from app.src.butter.checks import check_that
from app.src.third_party.flyway.migrator import Migrator
from app.src.internal.shell.command import Command


class PostgresMigrator(Migrator):
    def __init__(self, host: str, port: int, user: str, password: str, schemas: str):
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._schemas = schemas

    def migrate(self, db_name: str, dir: str) -> None:
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
