import enum


class ContentType(enum.Enum):
    TEXT = "text"
    VOICE = "voice"
    JPG = "jpg"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

    @staticmethod
    def from_str(label: str) -> "ContentType":
        return ContentType[label.upper()]
