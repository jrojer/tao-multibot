from abc import ABC, abstractmethod


class MetricsClient(ABC):

    @abstractmethod
    def write(self, measurement: str, tags: dict, fields: dict) -> None:
        pass

    @abstractmethod
    def close(self):
        pass
