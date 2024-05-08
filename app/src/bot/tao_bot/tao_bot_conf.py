from abc import ABC, abstractmethod

class TaoBotConf(ABC):
    @abstractmethod
    def username(self) -> str:
        pass

    @abstractmethod
    def chats(self) -> list[str]:
        pass

    @abstractmethod
    def admins(self) -> list[str]:
        pass

    @abstractmethod
    def users(self) -> list[str]:
        pass

    @abstractmethod
    def control_chat_id(self) -> str:
        pass

    @abstractmethod
    def system_prompt(self) -> str:
        pass

    @abstractmethod
    def number_of_messages_per_completion(self) -> int:
        pass

    @abstractmethod
    def bot_mention_names(self) -> list[str]:
        pass
