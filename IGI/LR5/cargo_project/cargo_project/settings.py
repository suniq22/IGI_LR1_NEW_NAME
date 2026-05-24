"""Django settings for cargo_project."""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-^h&l4l!4n_5p3yz!4-=7=5+m1q$g25g0=^!o2c!8=fz9z3vku5'
)

DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '*').split(',')

# Railway provides RAILWAY_PUBLIC_DOMAIN; auto-add it to ALLOWED_HOSTS
_railway_host = os.environ.get('RAILWAY_PUBLIC_DOMAIN')
if _railway_host and _railway_host not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(_railway_host)

CSRF_TRUSTED_ORIGINS = []
if _railway_host:
    CSRF_TRUSTED_ORIGINS.append(f'https://{_railway_host}')
# Extra trusted origins (comma-separated) from env
_extra_origins = os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '')
if _extra_origins:
    CSRF_TRUSTED_ORIGINS.extend(o.strip() for o in _extra_origins.split(',') if o.strip())

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'users.apps.UsersConfig',
    'main.apps.MainConfig',
    'cargo.apps.CargoConfig',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'users.middleware.TimezoneMiddleware',
]

ROOT_URLCONF = 'cargo_project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'main.context_processors.site_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'cargo_project.wsgi.application'

# Database
# 1. If DATABASE_URL is set (Railway / Render / Heroku) — use it.
# 2. Else if USE_POSTGRES=True — assemble from POSTGRES_* env vars (docker-compose).
# 3. Else — local SQLite.
if os.environ.get('DATABASE_URL'):
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(
            os.environ['DATABASE_URL'],
            conn_max_age=600,
            ssl_require=os.environ.get('DB_SSL_REQUIRE', 'False') == 'True',
        )
    }
elif os.environ.get('USE_POSTGRES', 'False') == 'True':
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('POSTGRES_DB', 'cargo_db'),
            'USER': os.environ.get('POSTGRES_USER', 'cargo_user'),
            'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'cargo_pass'),
            'HOST': os.environ.get('POSTGRES_HOST', 'db'),
            'PORT': os.environ.get('POSTGRES_PORT', '5432'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# Behind Railway/Heroku/Render TLS proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/users/login/'
LOGIN_REDIRECT_URL = '/users/profile/'
LOGOUT_REDIRECT_URL = '/'

# Logging
LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '[{asctime}] [{levelname}] [{name}] {message}',
            'style': '{',
        },
        'simple': {
            'format': '[{levelname}] {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': LOG_LEVEL,
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
        'file': {
            'level': LOG_LEVEL,
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': BASE_DIR / 'logs' / 'cargo.log',
            'maxBytes': 1024 * 1024 * 5,
            'backupCount': 3,
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'cargo': {'handlers': ['console', 'file'], 'level': LOG_LEVEL, 'propagate': False},
        'main': {'handlers': ['console', 'file'], 'level': LOG_LEVEL, 'propagate': False},
        'users': {'handlers': ['console', 'file'], 'level': LOG_LEVEL, 'propagate': False},
        'django': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
    },
}

# External APIs
QUOTABLE_API = 'https://api.quotable.io/random'
EXCHANGE_API = 'https://open.er-api.com/v6/latest/USD'

# Site
COMPANY_NAME = 'CargoGo'
