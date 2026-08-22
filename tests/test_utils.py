import pytest

from config.exceptions import InvalidEnvVariable, MissingEnvVariable
from config.utils import get_env


def test_get_env_returns_and_converts_values(monkeypatch):
    monkeypatch.setenv("TEXT_VALUE", "configured")
    monkeypatch.setenv("INTEGER_VALUE", "42")
    monkeypatch.setenv("BOOLEAN_VALUE", "yes")

    assert get_env("TEXT_VALUE") == "configured"
    assert get_env("INTEGER_VALUE", return_type=int) == 42
    assert get_env("BOOLEAN_VALUE", return_type=bool) is True


def test_get_env_uses_default(monkeypatch):
    monkeypatch.delenv("MISSING_VALUE", raising=False)

    assert get_env("MISSING_VALUE", default="fallback") == "fallback"
    assert get_env("MISSING_VALUE", default=False, return_type=bool) is False


def test_get_env_requires_value_without_default(monkeypatch):
    monkeypatch.delenv("REQUIRED_VALUE", raising=False)

    with pytest.raises(MissingEnvVariable, match='"REQUIRED_VALUE" is not set'):
        get_env("REQUIRED_VALUE")


@pytest.mark.parametrize("value", ["false", "0", "no", "off"])
def test_get_env_recognizes_false_values(monkeypatch, value):
    monkeypatch.setenv("BOOLEAN_VALUE", value)

    assert get_env("BOOLEAN_VALUE", return_type=bool) is False


@pytest.mark.parametrize(
    ("value", "return_type"),
    [("sometimes", bool), ("not-an-integer", int)],
)
def test_get_env_rejects_invalid_values(monkeypatch, value, return_type):
    monkeypatch.setenv("INVALID_VALUE", value)

    with pytest.raises(InvalidEnvVariable, match="has an invalid value"):
        get_env("INVALID_VALUE", return_type=return_type)
