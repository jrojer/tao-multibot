import aiohttp
from app.src.internal.audio.audio_file import AudioFile
from app.src.butter.checks import check_required


class TgVoiceDownloader:
    def __init__(self, bot) -> None:
        self._bot = check_required(bot, "bot")

    async def download(self, file_id: str) -> AudioFile:
        # Download the voice message
        file = await self._bot.get_file(file_id)
        url = file.file_path

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.read()
                return AudioFile.from_bytes(data, ".ogg")
