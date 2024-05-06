from abc import ABC, abstractmethod

class ApiClient(ABC):
    @abstractmethod
    def enable_in_group(self, chat_id: str):
        pass

    @abstractmethod
    def disable_for_group(self, chat_id: str):
        pass

    @abstractmethod
    def enable_for_username(self, username: str):
        pass

    @abstractmethod
    def disable_for_username(self, username: str):
        pass

    @abstractmethod
    def set_number_of_messages_per_completion(self, value: int):
        pass
