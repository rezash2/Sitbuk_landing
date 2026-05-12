from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.getenv('DJANGO_SECRET_KEY', 'sitbuk-landing-demo-secret-key')
DEBUG = os.getenv('DJANGO_DEBUG', '1') == '1'
ALLOWED_HOSTS = [host.strip() for host in os.getenv('DJANGO_ALLOWED_HOSTS', '*').split(',') if host.strip()]
CSRF_TRUSTED_ORIGINS = [origin.strip() for origin in os.getenv('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if origin.strip()]

SITE_URL = os.getenv('DJANGO_SITE_URL', 'http://127.0.0.1:8000').rstrip('/')
SITE_DEFAULT_IMAGE = os.getenv('DJANGO_SITE_DEFAULT_IMAGE', '/static/landing/images/sitbuk_logo.png')

# Stage 32.5 - demo systems integration placeholders
# Configure these URLs after deploying the separated demo copies of Behnico and Sitbuk.
BEHNICO_DEMO_BASE_URL = os.getenv('BEHNICO_DEMO_BASE_URL', 'https://behnico-demo.sitbuk.com').rstrip('/')
SITBUK_DEMO_BASE_URL = os.getenv('SITBUK_DEMO_BASE_URL', 'https://erp-demo.sitbuk.com').rstrip('/')
DEMO_ACCESS_TOKEN_HOURS = int(os.getenv('DEMO_ACCESS_TOKEN_HOURS', '72'))

# Stage 32.7 - Bale bot integration placeholders
BALE_BOT_TOKEN = os.getenv('BALE_BOT_TOKEN', '')
BALE_BOT_USERNAME = os.getenv('BALE_BOT_USERNAME', '')
BALE_WEBHOOK_SECRET = os.getenv('BALE_WEBHOOK_SECRET', '')
BALE_BOT_API_BASE = os.getenv('BALE_BOT_API_BASE', 'https://tapi.bale.ai').rstrip('/')


INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'landing',
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
]

ROOT_URLCONF = 'config.urls'

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
                'landing.context_processors.site_shell',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'
ASGI_APPLICATION = 'config.asgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = 'fa-ir'
TIME_ZONE = 'Asia/Tehran'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

SERVE_STATIC_FILES = DEBUG or os.getenv('DJANGO_SERVE_STATIC', '1') == '1'
SERVE_MEDIA_FILES = DEBUG or os.getenv('DJANGO_SERVE_MEDIA', '1') == '1'

USE_X_FORWARDED_HOST = os.getenv('DJANGO_USE_X_FORWARDED_HOST', '1') == '1'
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_SSL_REDIRECT = os.getenv('DJANGO_SECURE_SSL_REDIRECT', '0') == '1'
SESSION_COOKIE_SECURE = os.getenv('DJANGO_SESSION_COOKIE_SECURE', '0') == '1'
CSRF_COOKIE_SECURE = os.getenv('DJANGO_CSRF_COOKIE_SECURE', '0') == '1'
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'SAMEORIGIN'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
