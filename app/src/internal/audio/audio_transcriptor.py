import aiohttp
from app.tao.audio.audio_file import AudioFile
from app.infra import env
from app.tao.butter.checks import check_that
from app.tao.observability.logger import Logger


logger = Logger(__name__)

# This prompt is used to guide whisper to find proper punctuation.
AUDIO_INITIAL_PROMPT = ""


async def transcribe_audio(audio_file: AudioFile, prompt: str = "") -> str:
    url = "https://api.openai.com/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {env.OPENAI_API_KEY}"}
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


class AudioTranscriptor:
    def __init__(self):
        pass

    async def transcribe(self, audio_file: AudioFile, prompt: str = "") -> str:
        check_that(audio_file.is_wav(), "Audio file must be in wav format")
        if prompt == "":
            prompt = AUDIO_INITIAL_PROMPT
        logger.info(f"Transcribing audio {audio_file}")
        return await transcribe_audio(audio_file, prompt)
