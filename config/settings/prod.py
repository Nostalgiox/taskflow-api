import os

from .base import *  # noqa: F403

DEBUG = False

ALLOWED_HOSTS = ["*"]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Railway automatycznie ustawia RAILWAY_PUBLIC_DOMAIN
_railway_domain = os.environ.get("RAILWAY_PUBLIC_DOMAIN", "")
if _railway_domain:
    CSRF_TRUSTED_ORIGINS = [f"https://{_railway_domain}"]
