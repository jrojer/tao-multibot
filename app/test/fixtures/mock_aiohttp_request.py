from typing import Any


class MockAioHttpRequest:
    class MockMatchInfo:
        def __init__(self, chat_id: str):
            self.chat_id = chat_id

        def get(self, key) -> str:  # type: ignore
            return self.chat_id

    def __init__(self, chat_id: str, json_data: dict[str, Any]):
        self.match_info = MockAioHttpRequest.MockMatchInfo(chat_id)
        self.json_data = json_data

    async def json(self):
        return self.json_data
