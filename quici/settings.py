import os
from pathlib import Path
from datetime import timedelta
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-7zhugr7hk7f%#o8@wf)*yb9$i$y*1z@cw%qxy9d!)$0%qs#8ap')
DEBUG = True

ALLOWED_HOSTS = [".elasticbeanstalk.com","*",'quici-backend-1.onrender.com']


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
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ Added in correct order
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


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
            # "hosts": ["rediss://default:AV0vAAIncDJmZjk0Yjc0ZWI1Yzg0MWVlYjg4ODI3MjA1ZjUxZDkxNnAyMjM4NTU@warm-lacewing-23855.upstash.io:6379"],
           "hosts": ["rediss://default:ASiWAAIncDJjMTk5ZDhlM2UzYjQ0Yzk4OGMyYmU2ZTQ5YTQ1NzhkMXAyMTAzOTA@honest-jackal-10390.upstash.io:6379"]
        },
    },
}

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.sqlite3',
#         'NAME': BASE_DIR / 'db.sqlite3',
#     }
# }

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.postgresql',
#         'NAME': 'quici_db',
#         'USER': 'quici_db_user',
#         'PASSWORD': 'JSKhQgPBROBSiWu329fM0GtnbGtpIJKH',
#         'HOST': 'dpg-d3mki73uibrs738v8v9g-a.oregon-postgres.render.com',
#         'PORT': '5432',
#     }
# }

DB_HOST = os.environ.get('DB_HOST') or 'quicki-db.cfkoyeseecec.ap-south-1.rds.amazonaws.com'
DB_NAME = os.environ.get('DB_NAME') or 'quickidb'
DB_USER = os.environ.get('DB_USER') or 'ankit'
DB_PASSWORD = os.environ.get('DB_PASSWORD') or 'Ankit_Quicki'
DB_PORT = os.environ.get('DB_PORT') or '5432'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': DB_NAME,
        'USER': DB_USER,
        'PASSWORD': DB_PASSWORD,
        'HOST': DB_HOST,
        'PORT': DB_PORT,
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

# SIMPLE_JWT = {
#     'ACCESS_TOKEN_LIFETIME': timedelta(days=30),
#     'REFRESH_TOKEN_LIFETIME': timedelta(days=60),
#     'AUTH_HEADER_TYPES': ('Bearer',),
#     'SIGNING_KEY': os.environ.get('SECRET_KEY', 'django-insecure-7zhugr7hk7f%#o8@wf)*yb9$i$y*1z@cw%qxy9d!)$0%qs#8ap'),
# }

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=30),  # 1 month
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
    'SIGNING_KEY': os.environ.get('SECRET_KEY', 'django-insecure-7zhugr7hk7f%#o8@wf)*yb9$i$y*1z@cw%qxy9d!)$0%qs#8ap'),
    'ALGORITHM': 'HS256',
    'AUTH_TOKEN_CLASSES': ('rest_framework_simplejwt.tokens.AccessToken',),
}

# STATIC_URL = '/static/'
# MEDIA_URL = '/media/'
# MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# STATIC_ROOT = os.path.join(BASE_DIR, 'static')
# STATIC_URL = '/static/'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
AUTH_USER_MODEL = 'users.CustomUser'

AWS_S3_VERIFY = True

CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOW_CREDENTIALS = True

CORS_ALLOWED_ORIGINS = [
    'http://localhost:3000',
    'http://localhost:5173',
    'https://quici-restaurant.netlify.app',
    'https://quici-restaurant.pages.dev',
    'https://quicki-c6g.pages.dev',
    'https://quicki.net',
    'https://www.quicki.net',
    'www.quicki.net'
]

CSRF_TRUSTED_ORIGINS = [
    "https://quici-backend-1.onrender.com",
    "http://quici-backend-1.onrender.com",
    "https://quici-restaurant.pages.dev",
    'https://quicki-c6g.pages.dev',
    'https://api.quicki.net',
    'http://api.quicki.net',
    'https://quicki.net',
    'https://www.quicki.net'
]



EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True') == 'True'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER','rkinstitute85@gmail.com')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD','hchdlojdrkwtacnx')
DEFAULT_FROM_EMAIL = EMAIL_HOST_USER

RAZORPAY_KEY_ID = os.environ.get('RAZORPAY_KEY_ID','rzp_test_gp96uKYK1wp4hS')
RAZORPAY_KEY_SECRET = os.environ.get('RAZORPAY_KEY_SECRET','CrTK2UUkDVulKrpVUjSvzSC6')

# VAPID
VAPID_PUBLIC_KEY = 'BGInHhvVw4w2-wMWDJltZ4nGjVM4JODRLBRVK_BCIAzjMhTRhMJqAD-UJwRrbCira6zUr_cJ8Q1eLzicNWqAyeA'
VAPID_PRIVATE_KEY = 'GWyqKCJ08o4m2dUHghm0QbKh8yp5Rep4fxu6FZ47dgM'
VAPID_ADMIN_EMAIL = 'fakeclub256@gmail.com'


# settings.py

AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID','AKIAZ4SZDVVD2NGQ4OXZ')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY','g/SIqeh/gaYgrEjjXDj4d6pwn24xIyMsboIJ/v/9')
AWS_STORAGE_BUCKET_NAME = 'quicki-media'
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_REGION_NAME = 'ap-south-1'
AWS_S3_FILE_OVERWRITE = False
AWS_DEFAULT_ACL =  None
AWS_S3_VERITY = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'