import base64
from pathlib import Path


class Image:
    def __init__(self):
        self._image_data: bytes
        self._extension: str

    @staticmethod
    def from_path(path: str | Path) -> "Image":
        newImage = Image()
        with open(path, "rb") as image_file:
            newImage._image_data = image_file.read()
        return newImage

    @staticmethod
    def from_bytes(buffer: bytes, extension: str) -> "Image":
        newImage = Image()
        newImage._image_data = buffer
        newImage._extension = extension
        return newImage

    def as_base64(self) -> str:
        return base64.b64encode(self._image_data).decode("utf-8")
