import json


def is_empty_string(value):
    return isinstance(value, str) and len(value.strip()) == 0


def check_type(value, name, type):
    if value is not None and not isinstance(value, type):
        raise TypeError(
            f"{name} should be {type.__name__}, but it is {value.__class__.__name__}"
        )
    return value


def check_required(value, name, type=None):
    if value is None or is_empty_string(value):
        raise ValueError(f"{name} is required")
    if type is not None:
        check_type(value, name, type)
    return value


def check_any_present(values, names):
    if not any([value is not None for value in values]):
        raise ValueError(f"at least one of {names} should be present")
    return values


def check_one_of(value, name, values):
    check_required(value, name)
    if value not in values:
        raise ValueError(f"{name} should be one of {values}, but it is {value}")
    return value


def check_range(value, name, min, max):
    if value < min or value > max:
        raise ValueError(f"{name} should be in range [{min}, {max}], but it is {value}")
    return value


def check_that(predicate, messsage):
    if not predicate:
        raise ValueError(messsage)


def is_json(value):
    try:
        json.loads(value)
    except ValueError:
        return False
    return True


def check_json(value, name):
    check_type(value, name, str)
    if not is_json(value):
        raise ValueError(f"{name} should be a valid json")
    return value


def check_file_exists(file_path: str) -> bool:
    try:
        with open(file_path) as f:
            return True
    except FileNotFoundError:
        return False
