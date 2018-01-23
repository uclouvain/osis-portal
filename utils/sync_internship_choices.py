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
import csv
from django.db import connection


class InternshipChoiceSynchronizer:
    def __init__(self, choices_file=None):
        self.choices_file = choices_file

    def sync(self):
        with open(self.choices_file, 'rt') as csvfile:
            rows = csv.reader(csvfile)
            next(rows, None)
            uuids = list(map(lambda x: x[-1], rows))
            self.sync_choices_by_uuids(uuids)

    def clean(self):
        self.remove_duplicates()

    def sync_choices_by_uuids(self, uuids):
        print("%s choices to sync..." % len(uuids))
        cursor = connection.cursor()
        cursor.execute("SELECT id FROM internship_internshipchoice where uuid NOT IN %s" % str(tuple(uuids)))
        choices_to_destroy = cursor.fetchall()
        self.__destroy_prompt(choices_to_destroy)

    def remove_duplicates(self):
        print("Looking for duplicates.")
        cursor = connection.cursor()
        cursor.execute("\
            SELECT id\
                FROM internship_internshipchoice\
                WHERE\
                id NOT IN (\
                    SELECT MAX(id)\
                        FROM internship_internshipchoice\
                        GROUP BY student_id, internship_id, choice\
                );")
        ids_to_destroy = cursor.fetchall()
        self.__destroy_prompt(ids_to_destroy)

    def __destroy_prompt(self, choices_to_destroy):
        print("About to delete %s choices. This cannot be reversed. Are you sure?" % len(list(choices_to_destroy)))
        if len(choices_to_destroy) > 0:
            while True:
                confirm = input('[c]continue or [x]exit: ')
                if confirm == 'c':
                    print("Deleting %s out-of-sync choices..." % len(list(choices_to_destroy)))
                    self.__destroy_ids(choices_to_destroy)
                    print("Done")
                    return confirm
                elif confirm == 'x':
                    print("Got it! Come back when your mind is made up.")
                    break
                else:
                    print("Invalid Option. Please Enter a Valid Option.")
        else:
            print("Nothing to do here... Moving on.")

    def __destroy_ids(self, ids_to_destroy):
        cursor = connection.cursor()
        format_strings = ','.join(['%s'] * len(ids_to_destroy))
        cursor.execute("\
            DELETE\
                FROM internship_internshipchoice\
                WHERE id IN (%s)" % format_strings, tuple(ids_to_destroy))
