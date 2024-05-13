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
