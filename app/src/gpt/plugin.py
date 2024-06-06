from abc import ABC, abstractmethod
from typing import Any, Optional


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

    @abstractmethod
    async def system_prompt_attachment(self) -> Optional[str]:
        pass
