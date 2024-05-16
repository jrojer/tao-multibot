from abc import ABC, abstractmethod
from typing import Any


class Plugin(ABC):
    @abstractmethod
    def functions(self) -> list[dict[str, Any]]:
        pass

    @abstractmethod
    async def call(self, name: str, args: str) -> str:
        pass

    @abstractmethod
    def is_delegate(self) -> bool:
        pass
