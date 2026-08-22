class InvalidEnvVariable(Exception):
    """An environment variable has an invalid value."""


class MissingEnvVariable(Exception):
    """A required environment variable is missing."""
