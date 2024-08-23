from os import environ
from typing import Optional

from .exceptions import MissingEnvVariable


def get_env_var(
    variable_name: str,
    default: Optional[str] = None,
    raise_exception: bool = True
) -> Optional[str]:
    """Извлекает переменную из среды окружения"""
    if not (variable := environ.get(variable_name, default)):
        if raise_exception:
            raise MissingEnvVariable(f'{variable_name} is missing')
    
    return variable
