from abc import ABC, abstractmethod


class GptConf(ABC):
    @abstractmethod
    def model(self) -> str:
        pass

    @abstractmethod
    def temperature(self) -> float:
        pass

    @abstractmethod
    def max_tokens(self) -> int:
        pass

    @abstractmethod
    def top_p(self) -> float:
        pass

    @abstractmethod
    def presence_penalty(self) -> float:
        pass

    @abstractmethod
    def frequency_penalty(self) -> float:
        pass

    # TODO: decide should we provide tokens in conf for GPT and telegram
    @abstractmethod
    def token(self) -> str:
        pass

    @abstractmethod
    def url(self) -> str:
        pass
