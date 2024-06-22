from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine
from aiohttp import web


Handler = Callable[[web.Request], Coroutine[Any, Any, web.Response]]

class Resource(ABC):
    @staticmethod
    @abstractmethod
    def method() -> str:
        pass

    @staticmethod
    @abstractmethod
    def path() -> str:
        pass

    @abstractmethod
    def handler(self) -> Handler:
        pass
