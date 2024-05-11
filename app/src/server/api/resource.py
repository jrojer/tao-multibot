from abc import ABC, abstractmethod
from typing import Any, Callable, Coroutine
from aiohttp import web


Handler = Callable[[web.Request], Coroutine[Any, Any, web.Response]]

class Resource(ABC):
    @abstractmethod
    def method(self) -> str:
        pass

    @abstractmethod
    def path(self) -> str:
        pass

    @abstractmethod
    def handler(self) -> Handler:
        pass
