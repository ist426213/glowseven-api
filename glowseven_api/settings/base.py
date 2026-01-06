from pathlib import Path
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# ------------------------------------------------------------------------------
# Environment configuration
# ------------------------------------------------------------------------------
env = environ.Env(
    DEBUG=(bool, False),
)

# Load .env IF IT EXISTS (Linux-safe, Docker-safe)
ENV_FILE = BASE_DIR / ".env"
if ENV_FILE.exists():
    environ.Env.read_env(ENV_FILE)

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
SECRET_KEY = env("DJANGO_SECRET_KEY")

DEBUG = env.bool("DEBUG", default=False)

# ------------------------------------------------------------------------------
# Applications
# ------------------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # Third-party
    "rest_framework",

    # Local apps
    "categories",
    "products",
    "catalog",
    "core",
]

# ------------------------------------------------------------------------------
# Middleware
# ------------------------------------------------------------------------------
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# ------------------------------------------------------------------------------
# URLs / WSGI
# ------------------------------------------------------------------------------
ROOT_URLCONF = "glowseven_api.urls"
WSGI_APPLICATION = "glowseven_api.wsgi.application"

# ------------------------------------------------------------------------------
# Templates
# ------------------------------------------------------------------------------
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
    }
]

# ------------------------------------------------------------------------------
# Internationalization
# ------------------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# ------------------------------------------------------------------------------
# Static / Media
# ------------------------------------------------------------------------------
STATIC_URL = "/static/"
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# ------------------------------------------------------------------------------
# Defaults
# ------------------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
APPEND_SLASH = False
