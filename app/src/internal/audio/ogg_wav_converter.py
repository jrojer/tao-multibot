import asyncio
import os
from app.tao.audio.audio_file import AudioFile
from app.tao.butter.checks import check_that
from app.tao.observability.logger import Logger

logger = Logger(__name__)


class OggWavConverter:
    def __init__(self):
        pass

    async def convert(self, audio_file: AudioFile) -> AudioFile:
        check_that(audio_file.is_ogg(), "Audio file must be in ogg format")
        new_file_path = AudioFile.create_empty_file(".wav")
        logger.info(f"Converting {audio_file}")
        proc = await asyncio.create_subprocess_shell(
            f"ffmpeg -y -i {audio_file.path().absolute()} -acodec pcm_s16le -ac 1 -ar 16000 {new_file_path.absolute()}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        logger.info(stderr.decode())
        return AudioFile.from_path(new_file_path)
