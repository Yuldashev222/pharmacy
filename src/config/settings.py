import os
from pathlib import Path
from datetime import timedelta

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
TIME_ZONE = 'Asia/Tashkent'
DEBUG = int(os.environ.get('DEBUG', 1))
WSGI_APPLICATION = 'config.wsgi.application'
MEDIA_ROOT = os.path.join(BASE_DIR.joinpath('media'))
STATIC_ROOT = os.path.join(BASE_DIR.joinpath('static'))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = os.environ.get('SECRET_KEY', 'asgdygHAGDHGSH435464655^%$^%^&$%')
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost zbesstudio.uz 127.0.0.1 [::1]').split(' ')
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_REDIRECT_URL = 'profile'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR.joinpath('templates')],
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

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 'django_celery_results'
    'rest_framework',
    'rest_framework_simplejwt.token_blacklist',
    'drf_yasg',
    'django_filters',
    'corsheaders',

    # apps
    'api.v1.apps.general.apps.GeneralConfig',
    'api.v1.apps.accounts.apps.AccountsConfig',
    'api.v1.apps.companies.apps.CompaniesConfig',
    'api.v1.apps.pharmacies.apps.PharmaciesConfig',
    'api.v1.apps.firms.apps.FirmsConfig',
    'api.v1.apps.debts.apps.DebtsConfig',
    'api.v1.apps.expenses.apps.ExpensesConfig',
    'api.v1.apps.incomes.apps.IncomesConfig',
    'api.v1.apps.wages.apps.WagesConfig',
    'api.v1.apps.reports.apps.ReportsConfig',
    'api.v1.apps.clients.apps.ClientsConfig',
]

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('POSTGRES_DB_ENGINE', 'django.db.backends.sqlite3'),
        'NAME': os.environ.get('POSTGRES_DB_NAME', BASE_DIR.joinpath('db.sqlite3')),
        'USER': os.environ.get('POSTGRES_DB_USER', 'user'),
        'PASSWORD': os.environ.get('POSTGRES_DB_PASSWORD', 'password'),
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
    'DEFAULT_FILTER_BACKENDS': [
        'django_filters.rest_framework.DjangoFilterBackend'
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.LimitOffsetPagination',
    'PAGE_SIZE': 10,

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

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SIMPLE JWT CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=10),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": False,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": "",
    "AUDIENCE": None,
    "ISSUER": None,
    "JSON_ENCODER": None,
    "JWK_URL": None,
    "LEEWAY": 0,

    "AUTH_HEADER_TYPES": ("Bearer",),
    "AUTH_HEADER_NAME": "HTTP_AUTHORIZATION",
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "USER_AUTHENTICATION_RULE": "rest_framework_simplejwt.authentication.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
    "TOKEN_VERIFY_SERIALIZER": "rest_framework_simplejwt.serializers.TokenVerifySerializer",
    "TOKEN_BLACKLIST_SERIALIZER": "rest_framework_simplejwt.serializers.TokenBlacklistSerializer",
    "SLIDING_TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainSlidingSerializer",
    "SLIDING_TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSlidingSerializer",
}
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
SIMPLE JWT CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

CORS_ORIGIN_ALLOW_ALL = True