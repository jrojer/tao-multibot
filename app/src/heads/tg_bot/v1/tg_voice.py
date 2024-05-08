from typing import Optional

import telegram

from app.src.heads.tg_bot.v1.tg_bot_wrapper import TgBotWrapper
from app.src.internal.audio.audio_file import AudioFile
from app.src.internal.audio.audio_transcriptor import AudioTranscriptor
from app.src.internal.audio.ogg_wav_converter import OggWavConverter
from app.src.butter.checks import check_required
from app.src.heads.tg_bot.v1.tg_voice_downloader import TgVoiceDownloader
from app.src.internal.audio.voice import Voice


class TgVoice(Voice):
    # TODO: revise the design to remove the bot dependency
    def __init__(self, bot: TgBotWrapper, file_info: Optional[telegram.Voice]):
        self._bot: TgBotWrapper = check_required(bot, "bot", TgBotWrapper)
        self._file_info = check_required(file_info, "file_info")

    async def transcribe(self) -> str:
        ogg_file: AudioFile = await TgVoiceDownloader(self._bot).download(
            self._file_info.file_id
        )
        wav_file: AudioFile = await OggWavConverter().convert(ogg_file)
        transcription: str = await AudioTranscriptor(self._bot.token()).transcribe(wav_file)
        return transcription
