import enum


class ContentType(enum.Enum):
    FUNCTION_CALL = "function"
    TEXT = "text"
    IMAGE = "image"

    @staticmethod
    def from_str(label: str) -> "ContentType":
        return ContentType[label.upper()]
