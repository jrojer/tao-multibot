import enum


class ContentType(enum.Enum):
    FUNCTION = "function"
    TEXT = "text"
    VOICE = "voice"
    IMAGE = "image"
    VIDEO = "video"
    AUDIO = "audio"
    DOCUMENT = "document"

    @staticmethod
    def from_str(label: str) -> "ContentType":
        # NOTE: this is a migration code for backwards compatibility
        if label == "jpg":
            return ContentType.IMAGE
        return ContentType[label.upper()]
