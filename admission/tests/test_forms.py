#############################################################################
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

from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from admission.models import applicant
from admission.views import sociological
from django.utils.encoding import force_text
import json
from admission import models as mdl
from django.contrib.auth.models import User
import admission.tests.data_for_tests as data_model
from django.test import Client
from admission.forms import SociologicalSurveyForm
from admission.models.enums import education, professional_activity


PROFESSION_EMPLOYEE = 'Employee'


class SociologicalSurveyFormTest(TestCase):

    def setUp(self):
        self.applicant = data_model.create_applicant()

    def test_valid_form(self):
        data = self.init_data()
        form = SociologicalSurveyForm(data)
        self.assertTrue(form.is_valid())
        data.update({'student_professional_activity': professional_activity.NO_PROFESSION})
        form = SociologicalSurveyForm(data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        data = self.init_data()
        data.update({'student_profession': None})
        form = SociologicalSurveyForm(data)
        self.assertFalse(form.is_valid())
        data.update({'student_professional_activity': professional_activity.NO_PROFESSION})
        self.assertFalse(form.is_valid())

    @staticmethod
    def init_data():
        profession_choice = mdl.profession.Profession.objects.create(name=PROFESSION_EMPLOYEE, adhoc=False)

        data = {'number_brothers_sisters': 2,
                'father_is_deceased': False,
                'father_education': education.PRIMARY,
                'father_profession': profession_choice.id,
                'mother_is_deceased': False,
                'mother_education': education.PRIMARY,
                'mother_profession': profession_choice.id,
                'student_professional_activity': professional_activity.PART_TIME,
                'student_profession': profession_choice.id,
                'conjoint_professional_activity': professional_activity.PART_TIME,
                'conjoint_profession': profession_choice.id,
                'paternal_grandfather_profession': profession_choice.id,
                'maternal_grandfather_profession': profession_choice.id
                }
        return data
