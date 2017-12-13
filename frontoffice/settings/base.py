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
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


# SECURITY Settings
# Those settings are mandatory and have to be defined in your .env file
SECRET_KEY = os.environ['SECRET_KEY']
DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
ALLOWED_HOSTS = os.environ['ALLOWED_HOSTS'].split()
ADMIN_URL = os.environ['ADMIN_URL']
ENVIRONMENT = os.environ['ENVIRONMENT']
CSRF_COOKIE_SECURE = os.environ.get('CSRF_COOKIE_SECURE', 'False').lower() == 'true'


# Base configuration
ROOT_URLCONF = os.environ.get('ROOT_URLCONF', 'frontoffice.urls')
WSGI_APPLICATION = os.environ.get('WSGI_APPLICATION', 'frontoffice.wsgi.application')
MESSAGE_STORAGE = os.environ.get('MESSAGE_STORAGE', 'django.contrib.messages.storage.cookie.CookieStorage')

# Application definition
# Common apps for all environments
# Specific apps (all osis-portal modules except base and reference + env specific apps like sentry)
# have to be defined in environment settings (ex: dev.py)
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
)

# Tests settings
TESTING = os.environ.get('TESTING', 'False').lower() == 'true'
if TESTING:
    # add test packages that have specific models for tests
    INSTALLED_APPS += ('osis_common.tests', )
APPS_TO_TEST = (
    'osis_common',
    'reference',
    'base',
)
TEST_RUNNER = os.environ.get('TEST_RUNNER', 'osis_common.tests.runner.InstalledAppsTestRunner')
SKIP_QUEUES_TESTS = os.environ.get('SKIP_QUEUES_TESTS', 'False').lower() == 'true'
QUEUES_TESTING_TIMEOUT = float(os.environ.get('QUEUES_TESTING_TIMEOUT', 0.1))

# Middleware config
# Override this tuple in yous environment config (ex dev.py) if you want specific midddleware in specific order
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

# Logging config
# This is a dev config, all the errors are redirect to console output
# Override this settings in your environment settings (ex dev.py) if you want to use different loggers
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
        'send_mail': {
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


DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ.get("DATABASE_NAME", 'osis_portal_local'),
        'USER': os.environ.get("POSTGRES_USER", 'osis_portal'),
        'PASSWORD': os.environ.get("POSTGRES_PASSWORD", 'osis'),
        'HOST': os.environ.get("POSTGRES_HOST", '127.0.0.1'),
        'PORT': os.environ.get("POSTGRES_PORT", '5432'),
        'ATOMIC_REQUEST':  os.environ.get('DATABASE_ATOMIC_REQUEST', 'False').lower() == 'true'
    },
}


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
# If you want to change the default settings,
# you have to redefine the LANGUAGE_CODE and LANGUAGES vars in environment settings (ex: dev.py)
LANGUAGE_CODE = 'fr-be'
LANGUAGES = [
    ('fr-be', _('French')),
    ('en', _('English')),
]
# You can change default values for internalizations settings in your .env file
TIME_ZONE = os.environ.get('TIME_ZONE', 'Europe/Brussels')
USE_I18N = os.environ.get('USE_I18N', 'True').lower() == 'true'
USE_L10N = os.environ.get('USE_L10N', 'True').lower() == 'true'
USE_TZ = os.environ.get('USE_TZ', 'True').lower() == 'true'


# Static files (CSS, JavaScript, Images) and Media
# https://docs.djangoproject.com/en/1.9/howto/static-files/
STATIC_URL = os.environ.get('STATIC_URL', '/static/')
MEDIA_ROOT = os.environ.get('MEDIA_ROOT', os.path.join(BASE_DIR, "uploads"))
MEDIA_URL = os.environ.get('MEDIA_URL',  '/media/')
CONTENT_TYPES = ['application/csv', 'application/doc', 'application/pdf', 'application/xls', 'application/xml',
                 'application/zip', 'image/jpeg', 'image/gif', 'image/png', 'text/html', 'text/plain']
MAX_UPLOAD_SIZE = int(os.environ.get('MAX_UPLOAD_SIZE', 5242880))


# Logging settings
# Logging framework is defined in env settings (ex: dev.py)
DEFAULT_LOGGER = os.environ.get('DEFAULT_LOGGER', 'default')
SEND_MAIL_LOGGER = os.environ.get('SEND_MAIL_LOGGER', 'send_mail')
QUEUE_EXCEPTION_LOGGER = os.environ.get('QUEUE_EXCEPTION_LOGGER', 'queue_exception')


# Email Settings
# By default Email are saved in the folder defined by EMAIL_FILE_PATH
# If you want ti use the smtp backend,
# you have to define EMAIL_BACKEND, EMAIL_HOST and EMAIL_PORT in your .env if the default values doesn't match.
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'osis@localhost.be')
SERVER_EMAIL = os.environ.get('SERVER_EMAIL', DEFAULT_FROM_EMAIL)
LOGO_EMAIL_SIGNATURE_URL = os.environ.get('LOGO_EMAIL_SIGNATURE_URL', '')
EMAIL_PRODUCTION_SENDING = os.environ.get('EMAIL_PRODUCTION_SENDING', 'False').lower() == 'true'
COMMON_EMAIL_RECEIVER = os.environ.get('COMMON_EMAIL_RECEIVER', 'osis@localhost.org')
EMAIL_BACKEND = os.environ.get('EMAIL_BACKEND', 'django.core.mail.backends.filebased.EmailBackend')
EMAIL_FILE_PATH = os.environ.get('EMAIL_FILE_PATH', os.path.join(BASE_DIR, "base/tests/sent_mails"))
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 25))
SEND_BROKEN_LINK_EMAILS = os.environ.get('SEND_BROKEN_LINK_EMAILS', 'True').lower() == 'true'


# Authentication settings
LOGIN_URL = os.environ.get('LOGIN_URL', reverse_lazy('login'))
LOGIN_REDIRECT_URL = os.environ.get('LOGIN_REDIRECT_URL', reverse_lazy('dashboard_home'))
LOGOUT_URL = os.environ.get('LOGOUT_URL', reverse_lazy('logout'))
OVERRIDED_LOGIN_URL = os.environ.get('OVERRIDED_LOGIN_URL', None)
OVERRIDED_LOGOUT_URL = os.environ.get('OVERRIDED_LOGOUT_URL', None)
LOGOUT_BUTTON = os.environ.get('LOGOUT_BUTTON', 'True').lower() == 'true'
PERSON_EXTERNAL_ID_PATTERN = os.environ.get('PERSON_EXTERNAL_ID_PATTERN', 'osis.person_{global_id}')


# This has to be set in your .env with the actual url where you institution logo can be found.
# Ex : LOGO_INSTITUTION_URL = 'https://www.google.be/images/branding/googlelogo/1x/googlelogo_color_272x92dp.png'
# A relative URL will work on local , but not out of the box on the servers.
LOGO_INSTITUTION_URL = os.environ.get('LOGO_INSTITUTION_URL',
                                      os.path.join(BASE_DIR, "base/static/img/logo_institution.jpg"))
LOGO_OSIS_URL = os.environ.get('LOGO_OSIS_URL', '')
OSIS_SCORE_ENCODING_URL = os.environ.get('OSIS_SCORE_ENCODING_URL', None)
OSIS_SCORE_ENCODING_VPN_HELP_URL = os.environ.get('OSIS_SCORE_ENCODING_VPN_HELP_URL', None)

# Queues Definition
# The queue system uses RabbitMq queues to communicate with other application (ex : osis)
def get_queue_timeout(timeout_name, default_timeout):
    return float(os.environ.get(timeout_name, QUEUES_TESTING_TIMEOUT if TESTING else default_timeout))

if not TESTING or not SKIP_QUEUES_TESTS:
    QUEUES = {
        'QUEUE_URL': os.environ.get('RABBITMQ_HOST', 'localhost'),
        'QUEUE_USER': os.environ.get('RABBITMQ_USER', 'guest'),
        'QUEUE_PASSWORD': os.environ.get('RABBITMQ_PASSWORD', 'guest'),
        'QUEUE_PORT': int(os.environ.get('RABBITMQ_PORT', 5672)),
        'QUEUE_CONTEXT_ROOT': os.environ.get('RABBITMQ_CONTEXT_ROOT', '/'),
        'QUEUES_NAME': {
            'MIGRATIONS_TO_PRODUCE': 'osis',
            'MIGRATIONS_TO_CONSUME': 'osis_portal',
            'PERFORMANCE': 'performance_to_client',
            'STUDENT_PERFORMANCE': 'rpc_performance_from_client',
            'PERFORMANCE_UPDATE_EXP_DATE': 'performance_exp_date',
            'ATTRIBUTION': 'attribution',
            'ATTESTATION': 'rpc_attestation',
            'ATTESTATION_STATUS': 'rpc_attestation_status',
            'EXAM_ENROLLMENT_FORM': 'rpc_exam_enrollment_form',
            'EXAM_ENROLLMENT_FORM_REQUEST': 'exam_enrollment_form_request',
            'EXAM_ENROLLMENT_FORM_RESPONSE': 'exam_enrollment_form_response',
            'EXAM_ENROLLMENT_FORM_SUBMISSION': 'exam_enrollment_form_submission',
            'SCORE_ENCODING_PDF_REQUEST': 'score_encoding_pdf_request',
            'SCORE_ENCODING_PDF_RESPONSE': 'score_encoding_pdf_response',
            'ATTRIBUTION_RESPONSE': 'attribution_response',
            'APPLICATION_REQUEST': 'application_request',
            'APPLICATION_RESPONSE': 'application_response',
            'APPLICATION_OSIS_PORTAL': 'application_osis_portal',
        },
        'QUEUES_TIMEOUT': {
            'EXAM_ENROLLMENT_FORM_RESPONSE': get_queue_timeout('EXAM_ENROLLMENT_FORM_RESPONSE_TIMEOUT', 15),
            'PAPER_SHEET_TIMEOUT': get_queue_timeout('PAPER_SHEET_TIMEOUT', 60),
        },
        'RPC_QUEUES_TIMEOUT': {
            'STUDENT_PERFORMANCE': get_queue_timeout('STUDENT_PERFORMANCE_TIMEOUT', 15),
            'ATTESTATION_STATUS': get_queue_timeout('ATTESTATION_STATUS_TIMEOUT', 10),
            'ATTESTATION': get_queue_timeout('ATTESTATION_TIMEOUT', 60),
            'EXAM_ENROLLMENT_FORM': get_queue_timeout('EXAM_ENROLLMENT_FORM_TIMEOUT', 15)
        }
    }

# Additionnal Locale Path
# Add local path in your environment settings (ex: dev.py)
LOCALE_PATHS = ()


# Apps Settings

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

REST_FRAMEWORK = {
    # Use Django's standard `django.contrib.auth` permissions,
    # or allow read-only access for unauthenticated users.
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly'
    ]
}

ATTRIBUTION_CONFIG = {
    'TIME_TABLE_URL': os.environ.get('ATTRIBUTION_TIME_TABLE_URL', ''),
    'TIME_TABLE_NUMBER': os.environ.get('ATTRIBUTION_TIME_TABLE_NUMBER', ''),
    'CATALOG_URL': os.environ.get('ATTRIBUTION_CATALOG_URL', ''),
    'SERVER_TO_FETCH_URL': os.environ.get("ATTRIBUTION_API_URL", ''),
    'ATTRIBUTION_PATH': os.environ.get("ATTRIBUTION_API_PATH", ''),
    'SERVER_TO_FETCH_USER': os.environ.get("ATTRIBUTION_API_USER", ''),
    'SERVER_TO_FETCH_PASSWORD': os.environ.get("ATTRIBUTION_API_PASSWORD", ''),
}

PERFORMANCE_CONFIG = {
    'UPDATE_DELTA_HOURS_CURRENT_ACADEMIC_YEAR': int(os.environ.get('PERFORMANCE_UPDT_DELTA_CURRENT_ACAD_YR', 12)),
    'UPDATE_DELTA_HOURS_NON_CURRENT_ACADEMIC_YEAR': int(os.environ.get('PERFORMANCE_UPDT_DELTA_NON_CURRENT_ACAD_YR', 720)),
    'UPDATE_DELTA_HOURS_AFTER_CONSUMPTION': int(os.environ.get('PERFORMANCE_UPDT_DELTA_AFTER_CONS', 24)),
}

ATTESTATION_CONFIG = {
    'UPDATE_DELTA_HOURS_DEFAULT': int(os.environ.get("ATTESTATION_UPDATE_DELTA_HOURS", 72)),
    'SERVER_TO_FETCH_URL': os.environ.get("ATTESTATION_API_URL", ''),
    'ATTESTATION_PATH': os.environ.get("ATTESTATION_API_PATH", ''),
    'SERVER_TO_FETCH_USER': os.environ.get("ATTESTATION_API_USER", ''),
    'SERVER_TO_FETCH_PASSWORD': os.environ.get("ATTESTATION_API_PASSWORD", ''),
}
