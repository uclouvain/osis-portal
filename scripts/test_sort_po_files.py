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

from django.test import SimpleTestCase
import scripts.sort_po_files as sort_po_files
import os


class SortPoCase(SimpleTestCase):
    def test1(self):
        # Initialize script
        dir_path = "./scripts/"
        sort_po_files.filename_to_be_sorted = "test1.po"
        sort_po_files.filename_sorted = "test1_ordered.po"

        sort_po_files.sort_po_file(dir_path)

        f_expected = open(dir_path + "test1_expected.po", "r")
        string_expected = f_expected.read()
        f_expected.close()

        f_actual = open(dir_path + "test1_ordered.po", "r")
        string_actual = f_actual.read()
        f_actual.close()

        self.assertEqual(string_actual, string_expected)

        # Remove files
        os.remove(dir_path + sort_po_files.filename_sorted)

