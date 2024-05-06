from abc import ABC, abstractmethod


class Voice(ABC):
    @abstractmethod
    async def transcribe(self) -> str:
        pass
