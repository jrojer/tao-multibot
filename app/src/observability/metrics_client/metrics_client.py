from abc import ABC, abstractmethod


class MetricsClient(ABC):

    @abstractmethod
    def write(self, measurement: str, tags: dict[str, str], fields: dict[str, str]) -> None:
        pass

    @abstractmethod
    def close(self):
        pass
