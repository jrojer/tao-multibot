from abc import ABC, abstractmethod


class Tokeniser(ABC):
    @abstractmethod
    def num_tokens(self, text: str) -> int:
        pass
