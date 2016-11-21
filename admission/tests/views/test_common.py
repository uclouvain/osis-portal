##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase
from admission.views import common
from django.contrib.auth.models import User
import admission.tests.data_for_tests as data_model
from reference.enums import institutional_grade_type


class CommonTest(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@localhost', password='top_secret')
        self.applicant = data_model.create_applicant_by_user(self.user)

    def test_is_local_language_exam_needed_status(self):
        an_application = data_model.create_application(self.applicant)
        an_application.offer_year.grade_type = data_model.create_grade_type('BACHELOR', institutional_grade_type.BACHELOR, False)
        an_application.offer_year.save()
        self.assertFalse(common.is_local_language_exam_needed(an_application))

        an_application.offer_year.grade_type = data_model.create_grade_type('BACHELOR', institutional_grade_type.BACHELOR, True)
        an_application.offer_year.save()
        self.assertTrue(common.is_local_language_exam_needed(an_application))

        an_application.offer_year.grade_type = data_model.create_grade_type('BACHELORZ', None, False)
        an_application.offer_year.save()
        self.assertFalse(common.is_local_language_exam_needed(an_application))
