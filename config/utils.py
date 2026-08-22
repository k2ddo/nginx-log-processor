import os
from typing import cast

from .exceptions import InvalidEnvVariable, MissingEnvVariable


def get_env[T: (str, int, float, bool)](
    key: str,
    default: T | None = None,
    return_type: type[T] = str,
) -> T:
    """Get and convert an environment variable to the requested type."""
    value = os.getenv(key)

    if value is None:
        if default is not None:
            return default
        raise MissingEnvVariable(f'Environment variable "{key}" is not set')

    if return_type is str:
        return cast("T", value)

    try:
        if return_type is bool:
            normalized_value = value.lower()
            if normalized_value in ("true", "1", "yes", "on"):
                return cast("T", True)
            if normalized_value in ("false", "0", "no", "off"):
                return cast("T", False)
            raise ValueError
        return return_type(value)
    except (TypeError, ValueError):
        raise InvalidEnvVariable(
            f'Environment variable "{key}" has an invalid value "{value}". '
            f"Expected {return_type.__name__}"
        ) from None
