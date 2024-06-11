from pathlib import Path
from typing import Any
import json


from app.src.butter.checks import check_required, check_that


_vars: dict[str, Any] = {}


def set_var(name: str, value: Any):
    _vars[name] = value


def _create_if_not_exists(path: Path) -> Path:
    if not path.exists():
        path.mkdir(parents=True)
    return path


def VAR_DIR() -> Path:
    p = Path(_vars["VAR_DIR"])
    check_that(p.exists(), f"VAR_DIR {p} does not exist")
    return p


def TMP_DIR():
    return _create_if_not_exists(VAR_DIR() / "tmp")


def LOG_DIR() -> Path:
    return _create_if_not_exists(VAR_DIR() / "logs")


def DATA_DIR() -> Path:
    return _create_if_not_exists(VAR_DIR() / "data")


def SERVER_PORT() -> int:
    return int(_vars["SERVER_PORT"])


def DEBUG() -> bool:
    return check_required(_vars["DEBUG"], "DEBUG", bool)


def MASTER_CONFIG_PATH() -> Path:
    p = Path(_vars["MASTER_CONFIG_PATH"])
    check_that(p.exists(), f"master config at {p} does not exist")
    check_that(p.is_file(), f"master config at {p} is not a file")
    check_that(p.suffix == ".json", f"master config at {p} is not a json file")
    return p


def IMAGES_DIR() -> Path:
    return _create_if_not_exists(VAR_DIR() / "images")


# TODO: consider reading system prompt for the path provided in the master config
def SYSTEM_PROMPT_PATH(bot_id: str) -> Path:
    p = _create_if_not_exists(VAR_DIR() / "system_prompts") / (bot_id + ".txt")
    p.touch()
    return p


def SYSTEM_PROMPT_FOR(bot_id: str) -> str:
    p = SYSTEM_PROMPT_PATH(bot_id)
    with open(p, "r") as f:
        txt = f.read()
    if len(txt) == 0:
        txt = "You are an assistant."
        with open(p, "w") as f:
            f.write(txt)
    return txt


# INFLUXDB


def INFLUXDB_ENABLED() -> bool:
    return check_required(_vars["INFLUXDB"]["enabled"], "INFLUXDB_ENABLED", bool)


def INFLUXDB_URL() -> str:
    return _vars["INFLUXDB"]["url"]


def INFLUXDB_TOKEN() -> str:
    return _vars["INFLUXDB"]["token"]


def INFLUXDB_ORG() -> str:
    return _vars["INFLUXDB"]["org"]


def INFLUXDB_BUCKET() -> str:
    return _vars["INFLUXDB"]["bucket"]


# POSTGRES


def POSTGRES_ENABLED() -> bool:
    return check_required(_vars["POSTGRES"]["enabled"], "POSTGRES_ENABLED", bool)


def POSTGRES_HOST() -> str:
    return _vars["POSTGRES"]["host"]


def POSTGRES_PORT() -> int:
    return int(_vars["POSTGRES"]["port"])


def POSTGRES_USER() -> str:
    return _vars["POSTGRES"]["user"]


def POSTGRES_PASSWORD() -> str:
    return _vars["POSTGRES"]["password"]


def POSTGRES_SCHEMAS() -> str:
    return _vars["POSTGRES"]["schemas"]


# TABLE_PLUGIN


def STREAMLIT_TOKEN() -> str:
    return _vars["TABLE_PLUGIN"]["web_auth_token"]


def STREAMLIT_TTL_SECONDS() -> int:
    return int(_vars["TABLE_PLUGIN"]["web_auth_token_ttl_seconds"])


def TABLE_PLUGIN_SERVER_PORT() -> int:
    return int(_vars["TABLE_PLUGIN"]["plugin_server_port"])


def TABLE_PLUGIN_STREAMLIT_PORT() -> int:
    return int(_vars["TABLE_PLUGIN"]["web_port"])


def TABLE_PLUGIN_WEB_PREFIX() -> str:
    return _vars["TABLE_PLUGIN"]["web_prefix"]

def STREAMLIT_EXECUTABLE() -> str:
    return _vars["TABLE_PLUGIN"]["streamlit_executable"]

# TEST MODE

__test_mode = [False]


def assume_test_mode():
    __test_mode[0] = True


def in_test_mode() -> bool:
    return __test_mode[0]


def init_env(master_conf_path: str, var_dir_path: str):
    set_var("MASTER_CONFIG_PATH", master_conf_path)
    set_var("VAR_DIR", var_dir_path)

    with open(MASTER_CONFIG_PATH()) as f:
        infra = json.load(f)["infra"]

    set_var("POSTGRES", infra["postgres"])
    set_var("INFLUXDB", infra["influxdb"])
    set_var("SERVER_PORT", infra["server"]["port"])
    set_var("DEBUG", infra["debug"])
    set_var("TABLE_PLUGIN", infra["table_plugin"])


init_env("./master.json", "./var")
