import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-7zhugr7hk7f%#o8@wf)*yb9$i$y*1z@cw%qxy9d!)$0%qs#8ap')
DEBUG = True

ALLOWED_HOSTS = ["*",'quici-backend-1.onrender.com']


INSTALLED_APPS = [
    'daphne',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'users',
    'menu',
    'orders',
    'payments',
    'offers',
    'reviews',
    'cart',
    'notifications',
    'reports',
    'wishlist',
    'channels'
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
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
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

ROOT_URLCONF = 'quici.urls'
ASGI_APPLICATION = 'quici.asgi.application'

# CHANNEL_LAYERS = {
#     'default': {
#         'BACKEND': 'channels_redis.core.RedisChannelLayer',
#         'CONFIG': {
#             'hosts': [('127.0.0.1', 6379)],
#         },
#     },
# }
# redis-cli --tls -u redis://default:AV0vAAIncDJmZjk0Yjc0ZWI1Yzg0MWVlYjg4ODI3MjA1ZjUxZDkxNnAyMjM4NTU@warm-lacewing-23855.upstash.io:6379

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": ["rediss://default:AV0vAAIncDJmZjk0Yjc0ZWI1Yzg0MWVlYjg4ODI3MjA1ZjUxZDkxNnAyMjM4NTU@warm-lacewing-23855.upstash.io:6379"],
        },
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'quici_db',
        'USER': 'quici_db_user',
        'PASSWORD': 'JSKhQgPBROBSiWu329fM0GtnbGtpIJKH',
        'HOST': 'dpg-d3mki73uibrs738v8v9g-a.oregon-postgres.render.com',
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': os.environ.get('SECRET_KEY', 'django-insecure-7zhugr7hk7f%#o8@wf)*yb9$i$y*1z@cw%qxy9d!)$0%qs#8ap'),
}

STATIC_URL = '/static/'
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'

# APPEND_SLASH = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://quici-restaurant.netlify.app',
    'https://quici-restaurant.page.dev'
]

CSRF_TRUSTED_ORIGINS = [
    "https://quici-backend-1.onrender.com", 
    "http://quici-backend-1.onrender.com"
]



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_PASS')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID', 'rzp_test_gp96uKYK1wp4hS')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET', 'CrTK2UUkDVulKrpVUjSvzSC6')

VAPID_PUBLIC_KEY = 'BGInHhvVw4w2-wMWDJltZ4nGjVM4JODRLBRVK_BCIAzjMhTRhMJqAD-UJwRrbCira6zUr_cJ8Q1eLzicNWqAyeA'
VAPID_PRIVATE_KEY = 'GWyqKCJ08o4m2dUHghm0QbKh8yp5Rep4fxu6FZ47dgM'
VAPID_ADMIN_EMAIL = 'fakeclub256@gmail.com'

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': BASE_DIR / 'logs' / 'django.log',
#         },
#     },
#     'loggers': {
#         '': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }