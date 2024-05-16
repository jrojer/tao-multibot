from typing import Any
import aiohttp
import requests
from app.src.internal.audio.audio_file import OGA, AudioFile
from app.src.butter.checks import check_required
from app.src.internal.common.content_downloader import ContentDownloader
from app.src.internal.image.image import Image

_URL = "https://api.telegram.org/bot{bot_token}/getFile?file_id={ref}"
_DOWNLOAD_URL = "https://api.telegram.org/file/bot{bot_token}/{file_path}"


class TgContentDownloader(ContentDownloader):
    def __init__(self, tg_token: str):
        self._tg_token = check_required(tg_token, "tg_token", str)

    def _get_file_path(self, ref: str) -> str:
        url = _URL.format(bot_token=self._tg_token, ref=ref)
        response = requests.get(url)
        data = response.json()
        return data["result"]["file_path"]
    
    @staticmethod
    def _construct_object(data: Any, url: str) -> Any:
        if url.endswith(".jpg"):
            return Image.from_bytes(data, ".jpg")
        if url.endswith(OGA):
            return AudioFile.from_bytes(data, OGA)
        raise ValueError(f"Unsupported file type")

    def download(self, ref: str) -> Any:
        file_path = self._get_file_path(ref)
        download_url = _DOWNLOAD_URL.format(
            bot_token=self._tg_token, file_path=file_path
        )
        data = requests.get(download_url).content
        return self._construct_object(data, download_url)

    async def _aget_file_path(self, ref: str) -> str:
        url = _URL.format(bot_token=self._tg_token, ref=ref)
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                return data["result"]["file_path"]

    async def adownload(self, ref: str) -> Any:
        file_path = await self._aget_file_path(ref)
        download_url = _DOWNLOAD_URL.format(
            bot_token=self._tg_token, file_path=file_path
        )
        async with aiohttp.ClientSession() as session:
            async with session.get(download_url) as response:
                data = await response.read()
                return self._construct_object(data, download_url)
