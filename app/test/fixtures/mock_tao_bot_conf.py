from typing import Any
from app.src.bot.tao_bot.tao_bot_conf import TaoBotConf


class MockTaoBotConf(TaoBotConf):
    def __init__(self):
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def username(self) -> str:
        self.calls.append(("username", {}))
        return "mock_bot"

    def chats(self) -> list[str]:
        self.calls.append(("chats", {}))
        return ["chat1", "chat2"]

    def admins(self) -> list[str]:
        self.calls.append(("admins", {}))
        return ["admin1", "admin2"]

    def users(self) -> list[str]:
        self.calls.append(("users", {}))
        return ["user1", "user2"]

    def control_chat_id(self) -> str:
        self.calls.append(("control_chat_id", {}))
        return "control_chat"

    def system_prompt(self) -> str:
        self.calls.append(("system_prompt", {}))
        return "You are a helpful assistant."

    def number_of_messages_per_completion(self) -> int:
        self.calls.append(("number_of_messages_per_completion", {}))
        return 5

    def bot_mention_names(self) -> list[str]:
        self.calls.append(("bot_mention_names", {}))
        return ["mockbot", "mock_bot"]

    def plugins(self) -> list[str]:
        self.calls.append(("plugins", {}))
        return ["plugin1", "plugin2"]
