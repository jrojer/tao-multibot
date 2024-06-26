from abc import ABC, abstractmethod
from typing import Any


class ContentDownloader(ABC):
    @abstractmethod
    async def download(self, ref: str) -> Any:
        pass
