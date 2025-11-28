"""
Production settings for deployment on Render
"""
from .settings import *
import os

# SECURITY SETTINGS
DEBUG = False
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-q$p7bwhr1&oiimk3@r59_5-nwsyqhqr*$wf+7pq=ko4+q(71m0')

# ALLOWED HOSTS
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    'hair-scalp-detector.onrender.com',  # Your actual Render domain
    '.onrender.com',  # All Render domains
    '.vercel.app',    # Your Vercel frontend domain (if needed)
]

# CORS SETTINGS for Vercel frontend
CORS_ALLOWED_ORIGINS = [
    "https://your-app.vercel.app",  # Replace with your actual Vercel domain
    "http://localhost:3000",
    "http://localhost:8000",
]

CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_HEADERS = [
    'accept',
    'accept-encoding',
    'authorization',
    'content-type',
    'dnt',
    'origin',
    'user-agent',
    'x-csrftoken',
    'x-requested-with',
]

# CSRF SETTINGS
CSRF_TRUSTED_ORIGINS = [
    'https://hair-scalp-detector.onrender.com',  # Your actual domain
    'https://*.onrender.com',
    'https://*.vercel.app',
]

# DATABASE
# Use SQLite for simplicity on free tier
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

# STATIC FILES
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Only include static dirs that exist
import os as _os
_static_dir = _os.path.join(BASE_DIR, 'myapp', 'static')
if _os.path.exists(_static_dir):
    STATICFILES_DIRS = [_static_dir]
else:
    STATICFILES_DIRS = []

# WhiteNoise for serving static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# MEDIA FILES
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# SECURITY
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# LOGGING
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
