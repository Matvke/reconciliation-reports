import os
from pathlib import Path
from tempfile import gettempdir

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure")

ALLOWED_HOSTS = []
env_allowed_hosts = os.getenv("ALLOWED_HOSTS")
if env_allowed_hosts:
    hosts = [host.strip() for host in env_allowed_hosts.split(",") if host.strip()]
    ALLOWED_HOSTS.extend(hosts)

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "acts.apps.ActsConfig",
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

ROOT_URLCONF = "reconciliation.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "reconciliation.wsgi.application"

if DEBUG:
    DATA_DIR = BASE_DIR
else:
    def _pick_data_dir() -> Path:
        candidates = []
        env_data_dir = os.getenv("DATA_DIR")
        if env_data_dir:
            candidates.append(Path(env_data_dir))
        candidates.extend(
            [
                Path("/app/data"),
                BASE_DIR / "data",
                Path(gettempdir()) / "reconciliation-data",
            ]
        )

        for path in candidates:
            try:
                path.mkdir(parents=True, exist_ok=True)
                probe = path / ".write_test"
                probe.write_text("ok", encoding="utf-8")
                probe.unlink(missing_ok=True)
                return path
            except OSError:
                continue

        raise RuntimeError("No writable DATA_DIR candidate found")

    DATA_DIR = _pick_data_dir()

STATIC_ROOT = BASE_DIR / "static"
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
        "CONN_MAX_AGE": int(os.getenv("DB_CONN_MAX_AGE", "60")),
        "OPTIONS": {
            "timeout": int(os.getenv("SQLITE_TIMEOUT", "20")),
        },
    }
}

CSRF_TRUSTED_ORIGINS = []
env_csrf_origins = os.getenv("CSRF_TRUSTED_ORIGINS")
if env_csrf_origins:
    origins = [
        origin.strip() for origin in env_csrf_origins.split(",") if origin.strip()
    ]
    CSRF_TRUSTED_ORIGINS.extend(origins)

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

LANGUAGE_CODE = "ru-RU"

TIME_ZONE = "Europe/Samara"

USE_I18N = True

USE_TZ = True

LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
