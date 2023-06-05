import os
from pathlib import Path
from datetime import timedelta

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
DJANGO CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
USE_TZ = True
USE_I18N = True
MEDIA_URL = 'media/'
STATIC_URL = 'static/'
LANGUAGE_CODE = 'en-us'
ROOT_URLCONF = 'config.urls'
TIME_ZONE = 'Asia/Tashkent'
CELERY_TIMEZONE = 'Asia/Tashkent'
DEBUG = True
WSGI_APPLICATION = 'config.wsgi.application'
MEDIA_ROOT = os.path.join(BASE_DIR.joinpath('media'))
STATIC_ROOT = os.path.join(BASE_DIR.joinpath('static'))
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
SECRET_KEY = os.getenv('SECRET_KEY')
ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS').split(' ') + os.getenv('DOMAINS').split(' ')
AUTH_USER_MODEL = 'accounts.CustomUser'
LOGIN_REDIRECT_URL = 'profile'

ESKIZ_UZ_EMAIL = os.getenv('ESKIZ_UZ_EMAIL')
ESKIZ_UZ_PASSWORD = os.getenv('ESKIZ_UZ_PASSWORD')
ESKIZ_UZ_TOKEN_URL = os.getenv('ESKIZ_UZ_TOKEN_URL')
ESKIZ_UZ_SEND_SMS_URL = os.getenv('ESKIZ_UZ_SEND_SMS_URL')
ESKIZ_UZ_ALPHA_NICK = os.getenv('ESKIZ_UZ_ALPHA_NICK', '4546')
ESKIZ_UZ_CALLBACK_URL = os.getenv('ESKIZ_UZ_CALLBACK_URL', None)

MIDDLEWARE = [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
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
    'debug_toolbar',

    # apps
    'api.v1.apps.accounts.apps.AccountsConfig',
    'api.v1.apps.companies.apps.CompaniesConfig',
    'api.v1.apps.pharmacies.apps.PharmaciesConfig',
    'api.v1.apps.firms.apps.FirmsConfig',
    'api.v1.apps.debts.apps.DebtsConfig',
    'api.v1.apps.expenses.apps.ExpensesConfig',
    'api.v1.apps.incomes.apps.IncomesConfig',
    'api.v1.apps.clients.apps.ClientsConfig',
    'api.v1.apps.drugs.apps.DrugsConfig',
    'api.v1.apps.receipts.apps.ReceiptsConfig',
    'api.v1.apps.remainders.apps.RemaindersConfig',
    'api.v1.apps.offers.apps.OffersConfig',
]

DATABASES = {
    'default': {
        'ENGINE': os.getenv('POSTGRES_DB_ENGINE'),
        'NAME': os.getenv('POSTGRES_DB_NAME'),
        'USER': os.getenv('POSTGRES_DB_USER'),
        'PASSWORD': os.getenv('POSTGRES_DB_PASSWORD'),
        'HOST': os.getenv('POSTGRES_DB_HOST'),
        'PORT': os.getenv('POSTGRES_DB_PORT'),
    },
}
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.db.backends.sqlite3',
#        'NAME': BASE_DIR.joinpath('db.sqlite3'),
#    },
#}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://127.0.0.1:16379/1'
    }
}
print(os.getenv('POSTGRES_DB_ENGINE'))
INTERNAL_IPS = []
if DEBUG:
    INTERNAL_IPS = [
        "127.0.0.1",
        "localhost",
        "zbesstudio.uz",
        "89.223.127.4",
    ]
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
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,

    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
#        'rest_framework.authentication.SessionAuthentication',
#        'rest_framework.authentication.BasicAuthentication'
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
    "USER_AUTHENTICATION_RULE": "api.v1.apps.accounts.services.default_user_authentication_rule",

    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
    "TOKEN_USER_CLASS": "rest_framework_simplejwt.models.TokenUser",

    "JTI_CLAIM": "jti",

    "TOKEN_OBTAIN_SERIALIZER": "api.v1.apps.accounts.serializers.CustomTokenObtainPairSerializer",
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

""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CELERY CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_TIMEZONE = 'Asia/Tashkent'
CELERY_ENABLE_UTC = False
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
CELERY CONFIGURATIONS
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
