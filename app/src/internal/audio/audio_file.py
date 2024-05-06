from uuid import uuid4
from pathlib import Path

from app.src import env
from app.src.butter.checks import check_required, check_that


class AudioFile:
    @staticmethod
    def from_bytes(data: bytes, ext: str) -> "AudioFile":
        check_required(data, "data", bytes)
        check_that(ext in [".ogg", ".wav"], f"ext is not .ogg or .wav")
        new_audio_file = AudioFile()
        new_audio_file._path = Path(env.TMP_BINARY_STORAGE_PATH) / "{name}{ext}".format(
            name=uuid4(),
            ext=ext,
        )
        new_audio_file._path.parent.mkdir(parents=True, exist_ok=True)
        with open(new_audio_file._path, "wb") as f:
            f.write(data)
        return new_audio_file

    @staticmethod
    def from_path(path: Path) -> "AudioFile":
        check_required(path, "path", Path)
        check_that(path.exists(), f"file {path} does not exist")
        check_that(path.stat().st_size > 0, f"file {path} is empty")
        check_that(path.suffix in [".ogg", ".wav"], f"file {path} is not ogg or wav")
        new_audio_file = AudioFile()
        new_audio_file._path = path
        return new_audio_file

    @staticmethod
    def create_empty_file(ext: str) -> Path:
        check_that(ext in [".ogg", ".wav"], f"ext is not .ogg or .wav")
        path = Path(env.TMP_BINARY_STORAGE_PATH) / "{name}{ext}".format(
            name=uuid4(),
            ext=ext,
        )
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "wb") as f:
            f.write(b"")
        return path

    def __init__(self) -> None:
        self._path: Path = None

    def is_wav(self) -> bool:
        return self._path.suffix == ".wav"

    def is_ogg(self) -> bool:
        return self._path.suffix == ".ogg"

    def path(self) -> Path:
        return self._path
    
    def name(self) -> str:
        return self._path.name

    def bytes(self):
        with open(self._path, "rb") as f:
            return f.read()

    def __del__(self) -> None:
        if self._path is not None:
            self._path.unlink()

    def __str__(self) -> str:
        return self._path.name
    
    def __repr__(self) -> str:
        return self._path.name
