#!/usr/bin/env python3
##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2016 Université catholique de Louvain (http://www.uclouvain.be)
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
import sys
import dotenv

if __name__ == "__main__":
    dotenv.read_dotenv()

    SETTINGS_FILE = os.environ.get('DJANGO_SETTINGS_MODULE', 'frontoffice.settings.local')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", SETTINGS_FILE)

    from django.core.management import execute_from_command_line

    try:
        execute_from_command_line(sys.argv)
    except KeyError as ke:
        print("Error loading application.")
        print("The following environment var is not defined : {}".format(str(ke)))
        print("Check the following possible causes :")
        print(" - You don't have a .env file. You can copy .env.example to .env to use default")
        print(" - Mandatory variables are not defined in your .env file.")
        sys.exit("SettingsKeyError")
    except ImportError as ie:
        print("Error loading application : {}".format(str(ie)))
        print("Check the following possible causes :")
        print(" - The DJANGO_SETTINGS_MODULE defined in your .env doesn't exist")
        print(" - No DJANGO_SETTINGS_MODULE is defined and the default 'frontoffice.settings.local' doesn't exist ")
        sys.exit("DjangoSettingsError")

