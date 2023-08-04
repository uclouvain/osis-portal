# ############################################################################
#  OSIS stands for Open Student Information System. It's an application
#  designed to manage the core business of higher education institutions,
#  such as universities, faculties, institutes and professional schools.
#  The core business involves the administration of students, teachers,
#  courses, programs and so on.
#
#  Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  A copy of this license - GNU General Public License - is available
#  at the root of the source code of this program.  If not,
#  see http://www.gnu.org/licenses/.
# ############################################################################
import subprocess

from django.conf import settings
from django.core.management import BaseCommand

from base.management.commands.check_all_app_messages import check_messages_for_app, has_locale_directory

SUCCESS_RETURN_CODE = 0


class Command(BaseCommand):
    def handle(self, *args, **options):
        apps = settings.INSTALLED_APPS
        apps_with_locale_directory = {app for app in apps if has_locale_directory(app)}

        changed_files = subprocess.check_output(["git", "diff", "--name-only"], text=True).split('\n')
        changed_apps = {file.split('/')[0] for file in changed_files if file != ''}

        errors = []
        for app in changed_apps.intersection(apps_with_locale_directory):
            output_message, return_code = check_messages_for_app(app)
            if return_code != SUCCESS_RETURN_CODE:
                error_message = f"{app}\n{output_message}"
                errors.append(error_message)

        if errors:
            self.stderr.write("\n".join(errors))
            raise SystemExit(1)
        else:
            self.stdout.write("All good")
