import os
from dotenv import find_dotenv, load_dotenv
from pathlib import Path

load_dotenv()


def _getOrThrow(env_var: str) -> str:
    value = os.getenv(env_var)
    assert value is not None, f"Environment variable {env_var} is not set"
    return value


def _getPathOrThrow(env_var: str) -> str:
    path = _getOrThrow(env_var)
    path_to_dotenv = find_dotenv()
    # if the path is relative append it to path_to_dotenv using Path
    if not Path(path).is_absolute():
        path = Path(path_to_dotenv).parent / path
    return str(path)


def create_if_not_exists(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True)
    return path


INFLUXDB_TOKEN = _getOrThrow("INFLUXDB_TOKEN")
RUNTIME_DATA_DIR = _getPathOrThrow("RUNTIME_DATA_DIR")

LOG_DIR = create_if_not_exists(Path(RUNTIME_DATA_DIR) / "log")
TMP_DIR = create_if_not_exists(Path(RUNTIME_DATA_DIR) / "tmp")
MAIN_CONFIG_DIR = create_if_not_exists(Path(RUNTIME_DATA_DIR) / "config")

LOG_PATH = LOG_DIR / "app.log"
MAIN_CONFIG = MAIN_CONFIG_DIR / "master.json"


__test_mode = [False]


def assume_test_mode():
    __test_mode[0] = True


def in_test_mode() -> bool:
    return __test_mode[0]
