from __future__ import absolute_import, unicode_literals

import os
import sys

import dotenv

# So that we can launch test via jetbrains IDE

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if 'test' in sys.argv:
    os.environ.setdefault('TESTING', 'True')
dotenv.read_dotenv(os.path.join(BASE_DIR, '.env'))
sys.path.extend(os.environ.get('EXTRA_SYS_PATHS').split()) if os.environ.get('EXTRA_SYS_PATHS') else None

SETTINGS_FILE = os.environ.get('DJANGO_SETTINGS_MODULE', 'backoffice.settings.local')
os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)

