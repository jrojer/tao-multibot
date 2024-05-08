from abc import ABC, abstractmethod

from app.src.internal.audio.audio_file import AudioFile


class Voice(ABC):
    @abstractmethod
    async def transcribe(self, ogg_file: AudioFile) -> str:
        pass
