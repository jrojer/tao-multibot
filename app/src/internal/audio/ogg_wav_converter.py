from app.src.internal.audio.audio_file import WAV, AudioFile
from app.src.butter.checks import check_that
from app.src.observability.logger import Logger
from app.src.internal.shell.command import Command

logger = Logger(__name__)


class OgaWavConverter:
    def __init__(self):
        pass

    async def convert(self, audio_file: AudioFile) -> AudioFile:
        check_that(audio_file.is_ogg(), "Audio file must be in oga format")
        new_file_path = AudioFile.create_empty_file(WAV)
        logger.info(f"Converting {audio_file}")
        cmd = await Command([
            "ffmpeg",
            "-y",
            "-i",
            str(audio_file.path().absolute()),
            "-acodec",
            "pcm_s16le",
            "-ac",
            "1",
            "-ar",
            "16000",
            str(new_file_path.absolute()),
        ]).aexec()
        logger.info(cmd.stderr())
        return AudioFile.from_path(new_file_path)
