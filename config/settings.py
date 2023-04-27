import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DJANGO CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
USE_TZ = True
USE_I18N = True
MEDIA_URL = 'media/'
STATIC_URL = 'static/'
LANGUAGE_CODE = 'en-us'
ROOT_URLCONF = 'config.urls'
TIME_ZONE = 'Europe/Stockholm'
DEBUG = int(os.environ.get('DEBUG', 1))
WSGI_APPLICATION = 'config.wsgi.application'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = os.environ.get('SECRET_KEY', 'asgdygHAGDHGSH435464655^%$^%^&$%')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost 127.0.0.1').split(' ')
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
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
            ],
        },
    },
]
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}
]
AUTH_USER_MODEL = 'accounts.CustomUser'

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'django_celery_results'
    'rest_framework',

    # apps
    'api.v1.apps.companies.apps.CompaniesConfig',
    'api.v1.apps.accounts.apps.AccountsConfig',
    'api.v1.apps.pharmacies.apps.PharmaciesConfig',
]

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('POSTGRES_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('POSTGRES_DB_NAME', BASE_DIR / 'db.sqlite3'),
        'USER': os.environ.get('POSTGRES_DB_USER'),
        'PASSWORD': os.environ.get('POSTGRES_DB_PASSWORD'),
        'HOST': os.environ.get('POSTGRES_DB_HOST', 'localhost'),
        'PORT': os.environ.get('POSTGRES_DB_PORT', '5432'),
    },
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:16379/1'
    }
}
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DJANGO CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CELERY CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_URL = 'redis://127.0.0.1:16379/0'
# CELERY_RESULT_BACKEND = 'django-db'
# CELERY_CACHE_BACKEND = 'default'
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CELERY CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DJANGO REST FRAMEWORK CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ],
    'DATETIME_FORMAT': '%Y-%m-%d %H:%M',
    'DATE_FORMAT': '%Y-%m-%d',
}
if DEBUG:
    REST_FRAMEWORK['DEFAULT_AUTHENTICATION_CLASSES'] += [
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication'
    ]
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DJANGO REST FRAMEWORK CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
