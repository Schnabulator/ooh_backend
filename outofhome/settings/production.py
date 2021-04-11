from .base import *


ALLOWED_HOSTS = ["ooh.amatt.de", "localhost"]
DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'outofhome',
        'USER': 'ooh',
        'PASSWORD': 'IPCU2zLehKXCmhwl9ewY',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}