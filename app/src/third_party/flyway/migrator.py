from abc import ABC, abstractmethod


class Migrator(ABC):
    @abstractmethod
    def migrate(self, db_name: str, dir: str) -> None:
        pass
