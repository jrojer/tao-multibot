from typing import Any
from app.src.gpt.gpt_conf import GptConf


class MockGptConf(GptConf):
    def __init__(self):
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def model(self) -> str:
        self.calls.append(("model", {}))
        return "gpt-3.5-turbo"

    def temperature(self) -> float:
        self.calls.append(("temperature", {}))
        return 0.7

    def max_tokens(self) -> int:
        self.calls.append(("max_tokens", {}))
        return 150

    def top_p(self) -> float:
        self.calls.append(("top_p", {}))
        return 1.0

    def presence_penalty(self) -> float:
        self.calls.append(("presence_penalty", {}))
        return 0.0

    def frequency_penalty(self) -> float:
        self.calls.append(("frequency_penalty", {}))
        return 0.0

    def token(self) -> str:
        self.calls.append(("token", {}))
        return "test-token"

    def url(self) -> str:
        self.calls.append(("url", {}))
        return "https://api.openai.com/v1/chat/completions"
