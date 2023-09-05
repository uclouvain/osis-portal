import pathlib
import subprocess
from typing import List

from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        for lang_code in ['fr_BE', 'en']:
            self._check_duplicate_translation_key_without_same_translation_string(lang_code)

    def _check_duplicate_translation_key_without_same_translation_string(self, lang_code: str):
        self.stdout.write(f"Check duplicate translation key without same translation accros all apps in {lang_code}")

        default_po_file_location = f"locale/{lang_code}/LC_MESSAGES/django.po"
        po_files = [
            f"{app}/{default_po_file_location}" for app in settings.INSTALLED_APPS
            if pathlib.Path(f"{app}/{default_po_file_location}").is_file()
        ]
        result = self._concat_po_files_and_extract_fuzzy_translation(po_files)
        if result.strip() != "":
            self.stdout.write("**** Duplicate translation key without same translation found *****")
            self.stdout.write(result)
            self.stdout.write("*******************************************************************")
            raise SystemExit(1)
        self.stdout.write("OK")

    def _concat_po_files_and_extract_fuzzy_translation(self, po_files: List[str]):
        concat_process = subprocess.Popen(
            ["msgcat", "--more-than=1"] + po_files,
            stdout=subprocess.PIPE,
        )
        filter_fuzzy_process = subprocess.check_output(
            ["msgattrib", "--only-fuzzy"],
            stdin=concat_process.stdout,
            universal_newlines=True
        )
        concat_process.wait()
        return filter_fuzzy_process
