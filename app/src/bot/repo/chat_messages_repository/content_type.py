import enum


class ContentType(enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

    @staticmethod
    def from_str(label: str) -> "ContentType":
        return ContentType[label.upper()]
