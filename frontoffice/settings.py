##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import os
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'n#v8g9=3b&8xc9csdq88q3oegwfg-ny%)n9)c$nxr^$+h(0hmc'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


ADMIN_URL = 'admin/'

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'analytical',
    'osis_common',
    'rest_framework',
    'localflavor',
    'statici18n',
    'ckeditor',
    'reference',
    'base',
    'dashboard',
    'performance',
    'attribution',
    'dissertation',
    'internship',
    'exam_enrollment',
    'attestation'
)

# check if we are testing right now
TESTING = 'test' in sys.argv

if TESTING:
    # add test packages that have specific models for tests
    INSTALLED_APPS = INSTALLED_APPS + (
        'osis_common.tests',
    )

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)


REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ROOT_URLCONF = 'frontoffice.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'base.views.common.common_context_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'frontoffice.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("DATABASE_NAME", 'osis_front_dev'),
        'USER': os.environ.get("POSTGRES_USER", 'osis_usr'),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD", 'osis'),
        'HOST': os.environ.get("POSTGRES_HOST", '127.0.0.1'),
        'PORT': os.environ.get("POSTGRES_PORT", '5432'),
    },
}

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '%(asctime)s %(levelname)s %(module)s %(process)d %(thread)d %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
        'simple': {
            'format': '%(asctime)s %(levelname)s %(message)s',
            'datefmt': '%d-%m-%Y %H:%M:%S'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
            'level': 'DEBUG',
        },
    },
    'loggers': {
        'default': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'queue_exception': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        }
    },
}

DEFAULT_LOGGER = 'default'
QUEUE_EXCEPTION_LOGGER = 'queue_exception'

# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.9/topics/i18n/
LANGUAGE_CODE = 'fr-be'

LANGUAGES = [
    ('fr-be', _('French')),
    ('en', _('English')),
]

TIME_ZONE = 'Europe/Brussels'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
MEDIA_ROOT = os.path.join(BASE_DIR, "uploads")
MEDIA_URL = '/media/'

CONTENT_TYPES = ['application/csv', 'application/doc', 'application/pdf', 'application/xls', 'application/xml',
                 'application/zip', 'image/jpeg', 'image/gif', 'image/png', 'text/html', 'text/plain']
MAX_UPLOAD_SIZE = 5242880

MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = os.path.join(BASE_DIR, "base/tests/sent_mails")

DEFAULT_FROM_EMAIL = 'osis@localhost.be'
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Queues Definition
# Uncomment the configuration if you want to use the queue system
# The queue system uses RabbitMq queues to communicate with other application (ex : osis)
QUEUES = {
    'QUEUE_URL': os.environ.get("RABBITMQ_HOST") or 'localhost',
    'QUEUE_USER': os.environ.get("RABBITMQ_USER") or 'guest',
    'QUEUE_PASSWORD': os.environ.get("RABBITMQ_PASSWORD") or 'guest',
    'QUEUE_PORT': 5672,
    'QUEUE_CONTEXT_ROOT': '/',
    'QUEUES_NAME': {
        'MIGRATIONS_TO_PRODUCE': 'osis',
        'MIGRATIONS_TO_CONSUME': 'osis_portal',
        'PAPER_SHEET': 'paper_sheet',
        'PERFORMANCE': 'performance_to_client',
        'STUDENT_PERFORMANCE': 'rpc_performance_from_client',
        'STUDENT_POINTS': 'rpc_performance_to_client',
        'PERFORMANCE_UPDATE_EXP_DATE': 'performance_exp_date',
        'ATTRIBUTION': 'attribution',
        'ATTESTATION': 'rpc_attestation',
        'ATTESTATION_STATUS': 'rpc_attestation_status',
        'EXAM_ENROLLMENT_FORM': 'rpc_exam_enrollment_form',
        'EXAM_ENROLLMENT_FORM_SUBMISSION': 'exam_enrollment_form_submission',
    },
    'RPC_QUEUES_TIMEOUT': {
        'PAPER_SHEET': 60,
        'STUDENT_PERFORMANCE': 15,
        'ATTESTATION_STATUS': 10,
        'ATTESTATION': 60,
        'EXAM_ENROLLMENT_FORM': 15
    }
}

LOGIN_URL=reverse_lazy('login')
OVERRIDED_LOGOUT_URL = ''
OVERRIDED_LOGIN_URL = ''
LOGOUT_BUTTON = True

# This has to be replaced by the actual url where you institution logo can be found.
# Ex : LOGO_INSTITUTION_URL = 'https://www.google.be/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
# A relative URL will work on local , but not out of the box on the servers.
LOGO_INSTITUTION_URL = os.path.join(BASE_DIR, "base/static/img/logo_institution.jpg")

LOGO_EMAIL_SIGNATURE_URL = ''
LOGO_OSIS_URL = ''

EMAIL_PRODUCTION_SENDING = False
COMMON_EMAIL_RECEIVER = 'osis@localhost.org'

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            {'name': 'basicstyles', 'items': ['Bold', 'Italic', 'Underline', 'Strike', '-', 'RemoveFormat']},
            {'name': 'links', 'items': ['Link']},
            {'name': 'styles', 'items': ['Styles', 'Format', 'Font', 'FontSize', 'Source']},
            {'name': 'colors', 'items': ['TextColor', 'BGColor']},
            '/',
            {'name': 'insert', 'items': ['Table']},
            {'name': 'paragraph',
             'items': ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'Blockquote', 'CreateDiv', '-',
                       'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock']},
            {'name': 'forms',
             'items': ['Form', 'Checkbox', 'Radio', 'TextField', 'Textarea', 'Select', 'Button', 'ImageButton',
                       'HiddenField']},
            {'name': 'about', 'items': ['About']},
        ],
    },
}


TIME_TABLE_URL = ""
TIME_TABLE_NUMBER = ""
CATALOG_URL = ""

PERFORMANCE_CONFIG = {
    'UPDATE_DELTA_HOURS_CURRENT_ACADEMIC_YEAR': 12,
    'UPDATE_DELTA_HOURS_NON_CURRENT_ACADEMIC_YEAR': 720,
    'UPDATE_DELTA_HOURS_AFTER_CONSUMPTION': 24,
}

ATTESTATION_CONFIG = {
    'UPDATE_DELTA_HOURS_DEFAULT': os.environ.get("ATTESTATION_UPDATE_DELTA_HOURS", 72),
    'SERVER_TO_FETCH_URL': os.environ.get("ATTESTATION_API_URL", ''),
    'ATTESTATION_PATH': os.environ.get("ATTESTATION_API_PATH", ''),
    'SERVER_TO_FETCH_USER': os.environ.get("ATTESTATION_API_USER", ''),
    'SERVER_TO_FETCH_PASSWORD': os.environ.get("ATTESTATION_API_PASSWORD", ''),
}

try:
    from frontoffice.server_settings import *
    try:
        LOCALE_PATHS = SERVER_LOCALE_PATHS
    except NameError:
        pass
except ImportError:
    pass

LIST_CONFIG = {
    'UPDATE_DELTA_HOURS_DEFAULT': 72,
    'SERVER_TO_FETCH_URL': 'https://verpoorten.epc.uclouvain.be:8181/WebApi/',
    'LIST_PATH': 'resources/Liste/inscExam/{anac}/{codes}',
    'SERVER_TO_FETCH_USER': 'portail',
    'SERVER_TO_FETCH_PASSWORD': '&F1nZerb',
}
