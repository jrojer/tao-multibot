from app.src.heads.tg_bot.v1.tg_bot_wrapper import TgBotWrapper
from app.src.internal.audio.audio_file import AudioFile
from app.src.internal.audio.audio_transcriptor import AudioTranscriptor
from app.src.internal.audio.ogg_wav_converter import OggWavConverter
from app.src.butter.checks import check_required
from app.src.internal.audio.voice import Voice


class TgVoice(Voice):
    # TODO: revise the design to remove the bot dependency
    def __init__(self, bot: TgBotWrapper, audio_transcriptor: AudioTranscriptor, ogg_converter: OggWavConverter):
        self._bot: TgBotWrapper = check_required(bot, "bot", TgBotWrapper)
        self._audio_transcriptor: AudioTranscriptor = check_required(audio_transcriptor, "audio_transcriptor", AudioTranscriptor)
        self._ogg_converter: OggWavConverter = check_required(ogg_converter, "ogg_converter", OggWavConverter)

    async def transcribe(self, ogg_file: AudioFile) -> str:
        wav_file: AudioFile = await self._ogg_converter.convert(ogg_file)
        transcription: str = await self._audio_transcriptor.transcribe(wav_file)
        return transcription
