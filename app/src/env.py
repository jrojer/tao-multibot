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


def _getListOrThrow(env_var: str) -> str:
    value = _getOrThrow(env_var)
    return [s.strip() for s in value.split(",")]


def _get_bool_or_throw(env_var: str) -> bool:
    value = _getOrThrow(env_var)
    assert value in [
        "true",
        "false",
    ], f"Environment variable {env_var} is not a boolean"
    return value == "true"


__test_mode = [False]

LOG_PATH = _getPathOrThrow("LOG_PATH")
INFLUXDB_TOKEN = _getOrThrow("INFLUXDB_TOKEN")
TMP_BINARY_STORAGE_PATH = _getPathOrThrow("TMP_BINARY_STORAGE_PATH")


def assume_test_mode():
    __test_mode[0] = True


def in_test_mode() -> bool:
    return __test_mode[0]
