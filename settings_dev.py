"""
    Author: tianwei
    Email: liutianweidlut@gmail.com
    Description: Django setting for daily development
    Created: 2013-4-12
"""
from settings import *

print 'xxxxxxx'

DEBUG = True
TEMPLATE_DEBUG = DEBUG

# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
#         'NAME': 'sc',             # Or path to database file if using sqlite3.
#         'USER': 'root',                       # Not used with sqlite3.
#         'PASSWORD': 'root',                   # Not used with sqlite3.
#         'HOST': '192.168.3.118',                           # Set to empty string for localhost. Not used with sqlite3.
#         'PORT': '3306',                            # Set to empty string for default. Not used with sqlite3.
#     }
# }

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'ScientificResearch',             # Or path to database file if using sqlite3.
        'USER': 'root',                       # Not used with sqlite3.
        'PASSWORD': 'root',                   # Not used with sqlite3.
        'HOST': 'localhost',                           # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '3306',                           # Set to empty string for default. Not used with sqlite3.
    }
}


# Website settings
WEB_TITLE = "Province Management Dev"
