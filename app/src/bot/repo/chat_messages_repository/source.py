import enum

class Source(enum.Enum):
    TELEGRAM = 'telegram'
    WHATSAPP = 'whatsapp'

    @staticmethod
    def from_str(label: str) -> "Source":
        return Source[label.upper()]
