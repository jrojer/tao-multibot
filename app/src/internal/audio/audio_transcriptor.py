import aiohttp
from app.src.internal.audio.audio_file import AudioFile
from app.src.butter.checks import check_required, check_that
from app.src.observability.logger import Logger


logger = Logger(__name__)

# This prompt is used to guide whisper to find proper punctuation.
AUDIO_INITIAL_PROMPT = ""


class AudioTranscriptor:
    def __init__(self, token: str):
        self._token = check_required(token, "token", str)

    async def transcribe(self, audio_file: AudioFile, prompt: str = "") -> str:
        check_that(audio_file.is_wav(), "Audio file must be in wav format")
        if prompt == "":
            prompt = AUDIO_INITIAL_PROMPT
        logger.info(f"Transcribing audio {audio_file}")
        return await self._transcribe_audio(audio_file, prompt)

    async def _transcribe_audio(self, audio_file: AudioFile, prompt: str = "") -> str:
        url = "https://api.openai.com/v1/audio/transcriptions"
        headers = {"Authorization": f"Bearer {self._token}"}
        data = aiohttp.FormData()
        data.add_field(
            "file",
            audio_file.bytes(),
            filename=audio_file.name(),
            content_type="multipart/form-data",
        )
        data.add_field("model", "whisper-1")
        data.add_field("prompt", prompt)

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=data) as response:
                response_data = await response.json()
                return response_data.get("text")
