"""Django settings for nginx-log-processor."""

from pathlib import Path

from dotenv import load_dotenv

from .utils import get_env

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

SECRET_KEY = get_env(
    "SECRET_KEY",
    "django-insecure-development-only-key-change-me",
)
DEBUG = get_env("DEBUG", default=False, return_type=bool)
ALLOWED_HOSTS = [
    host.strip()
    for host in get_env("ALLOWED_HOSTS", "localhost,127.0.0.1").split(",")
    if host.strip()
]
CSRF_TRUSTED_ORIGINS = [
    origin.strip() for origin in get_env("CSRF_TRUSTED_ORIGINS", "").split(",") if origin.strip()
]

INSTALLED_APPS = [
    "unfold",
    "unfold.contrib.filters",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "django_filters",
    "drf_spectacular",
    "logs",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]
WSGI_APPLICATION = "config.wsgi.application"

DB_ENGINE = get_env("DB_ENGINE", "django.db.backends.sqlite3")
DATABASES = {
    "default": {
        "ENGINE": DB_ENGINE,
        "NAME": get_env("DB_NAME", str(BASE_DIR / "db.sqlite3")),
        "USER": get_env("DB_USER", ""),
        "PASSWORD": get_env("DB_PASSWORD", ""),
        "HOST": get_env("DB_HOST", ""),
        "PORT": get_env("DB_PORT", "5432"),
        "CONN_MAX_AGE": get_env("DB_CONN_MAX_AGE", default=60, return_type=int),
        "CONN_HEALTH_CHECKS": True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "ru"
TIME_ZONE = "Europe/Minsk"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.BasicAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 50,
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

SPECTACULAR_SETTINGS = {
    "TITLE": "Nginx Log Processor API",
    "DESCRIPTION": "Import structured Nginx logs and query them through a read-only API.",
    "VERSION": "1.0.0",
}
ENABLE_API_DOCS = get_env("ENABLE_API_DOCS", default=DEBUG, return_type=bool)

UNFOLD = {
    "SITE_TITLE": "Nginx Log Processor",
    "SITE_HEADER": "Nginx Log Processor",
    "SITE_SUBHEADER": "Access log administration",
    "SITE_SYMBOL": "monitoring",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": False,
}

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = get_env("SECURE_SSL_REDIRECT", default=False, return_type=bool)
SESSION_COOKIE_SECURE = get_env("SESSION_COOKIE_SECURE", default=False, return_type=bool)
CSRF_COOKIE_SECURE = get_env("CSRF_COOKIE_SECURE", default=False, return_type=bool)
SECURE_HSTS_SECONDS = get_env("SECURE_HSTS_SECONDS", default=0, return_type=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = get_env(
    "SECURE_HSTS_INCLUDE_SUBDOMAINS", default=False, return_type=bool
)
SECURE_HSTS_PRELOAD = get_env("SECURE_HSTS_PRELOAD", default=False, return_type=bool)
