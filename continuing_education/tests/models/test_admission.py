##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from continuing_education.models import admission
from continuing_education.tests.factories.admission import AdmissionFactory

class TestAdmission(TestCase):
    def setUp(self):
        self.admission = AdmissionFactory()

    def test_find_by_id(self):
        an_admission = self.admission
        persisted_admission = admission.find_by_id(an_admission.id)
        self.assertEqual(an_admission.id, persisted_admission.id)

        nonexistent_admission = admission.find_by_id(0)
        self.assertIsNone(nonexistent_admission)

    # to be changed with student id
    def test_find_by_student(self):
        an_admission = self.admission
        persisted_admission = admission.find_by_student(an_admission.first_name, an_admission.last_name)
        self.assertTrue(persisted_admission.exists())

        nonexistent_admission = admission.find_by_student("first_name", "last_name")
        self.assertFalse(nonexistent_admission.exists())