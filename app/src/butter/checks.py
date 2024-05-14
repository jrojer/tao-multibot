import json
from typing import Any, List, Union

numeric = Union[int, float]


def is_empty_string(value: Any) -> bool:
    return isinstance(value, str) and len(value.strip()) == 0


def check_optional(value: Any, name: str, t: type) -> Any:
    if value is not None and not isinstance(value, t):
        raise TypeError(
            f"{name} should be {t.__name__}, but it is {value.__class__.__name__}"
        )
    return value


def check_required(value: Any, name: str, t:type=object) -> Any:
    if value is None or is_empty_string(value):
        raise ValueError(f"{name} is required")
    if t is not object:
        check_optional(value, name, t)
    return value


def check_any_present(values: List[Any], names: List[str]) -> List[Any]:
    if not any([value is not None for value in values]):
        raise ValueError(f"at least one of {names} should be present")
    return values


def check_one_of(value: Any, name: str, values: List[Any]) -> Any:
    check_required(value, name)
    if value not in values:
        raise ValueError(f"{name} should be one of {values}, but it is {value}")
    return value


def check_range(value: numeric, name: str, min: numeric, max: numeric) -> numeric:
    if value < min or value > max:
        raise ValueError(f"{name} should be in range [{min}, {max}], but it is {value}")
    return value


def check_that(predicate: bool, messsage: str) -> None:
    if not predicate:
        raise ValueError(messsage)


def is_json(value: str) -> bool:
    try:
        json.loads(value)
    except ValueError:
        return False
    return True


def check_json(value: str, name: str) -> str:
    check_optional(value, name, str)
    if not is_json(value):
        raise ValueError(f"{name} should be a valid json")
    return value


def check_file_exists(file_path: str) -> bool:
    try:
        with open(file_path) as _:
            return True
    except FileNotFoundError:
        return False
