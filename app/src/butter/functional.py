def or_else(value, default_f):
    if value is None:
        return default_f()
    return value


def if_present_or_else(value, f, default_f):
    if value is None:
        return default_f()
    return f(value)


def none_if_empty(value):
    if len(value) == 0:
        return None
    return value


def first_present(lambdas):
    for l in lambdas:
        result = l()
        if result is not None:
            return result
    return None
