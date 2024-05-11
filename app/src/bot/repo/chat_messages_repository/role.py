import enum


class Role(enum.Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

    @staticmethod
    def from_str(label: str) -> "Role":
        return Role[label.upper()]
