from app.src.internal.audio.audio_file import AudioFile
from app.src.internal.audio.audio_transcriptor import AudioTranscriptor
from app.src.internal.audio.ogg_wav_converter import OgaWavConverter
from app.src.butter.checks import check_required
from app.src.internal.audio.voice import Voice


class TgVoice(Voice):
    def __init__(self, audio_transcriptor: AudioTranscriptor, ogg_converter: OgaWavConverter):
        self._audio_transcriptor: AudioTranscriptor = check_required(audio_transcriptor, "audio_transcriptor", AudioTranscriptor)
        self._ogg_converter: OgaWavConverter = check_required(ogg_converter, "ogg_converter", OgaWavConverter)

    async def transcribe(self, ogg_file: AudioFile) -> str:
        wav_file: AudioFile = await self._ogg_converter.convert(ogg_file)
        transcription: str = await self._audio_transcriptor.transcribe(wav_file)
        return transcription
