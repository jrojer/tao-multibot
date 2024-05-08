from typing import Any, Callable


def or_else(value: Any, default_f: Callable[[], Any]) -> Any:
    if value is None:
        return default_f()
    return value


def if_present_or_else(value: Any, f: Callable[[], Any], default_f: Callable[[], Any]) -> Any:
    if value is None:
        return default_f()
    return f(value) # type: ignore


def none_if_empty(value: Any) -> Any:
    if len(value) == 0:
        return None
    return value


def first_present(lambdas: list[Callable[[], Any]]) -> Any:
    for l in lambdas:
        result = l()
        if result is not None:
            return result
    return None
