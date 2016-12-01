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
from django.contrib.auth.models import User
from django.test import TestCase, RequestFactory
import admission.tests.data_for_tests as data_model
from admission.views import application
from base import models as mdl_base
from base.models.enums import component_type
from attribution.models.enums import function


class TeachingLoadTest(TestCase):

    def setUp(self):
        self.a_user = User.objects.create_user(username='jacob', email='jacob@localhost', password='top_secret')
        a_person = data_model.create_person(self.a_user)
        # a_tutor = data_model.create_tutor(a_person)
        # a_learning_unit_year = data_model.create_learning_unit_year({})
        # an_academic_year = data_model.create_academic_year()
        # an_attribution = data_model.create_attribution({'function': function.CO_HOLDER,
        #                                                 'learning_unit_year': a_learning_unit_year,
        #                                                 'tutor': a_tutor})
        # a_learning_unit_component_lecture = data_model.create_learning_unit_component({
        #     'learning_unit_year': a_learning_unit_year,
        #     'type': component_type.LECTURING,
        #     'duration': 15})
        # a_learning_unit_component_practice = data_model.create_learning_unit_component({
        #     'learning_unit_year': a_learning_unit_year,
        #     'type': component_type.PRACTICAL_EXERCISES,
        #     'duration': 15})
        #
        # an_attribution_charge_lecture = data_model.create_attribution_charge(
        #     {'attribution': an_attribution,
        #      'learning_unit_component': a_learning_unit_component_lecture,
        #      'allocation_charge': 15})
        # an_attribution_charge_practice = data_model.create_attribution_charge(
        #     {'attribution': an_attribution,
        #      'learning_unit_component': a_learning_unit_component_practice,
        #      'allocation_charge': 15})

    def test_get_person_from_user(self):
        self.assertEqual(self.get_person(self.a_user), self.a_person)

    def get_person(self, a_user):
        return a_user





