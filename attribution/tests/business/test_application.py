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
from django.test import TestCase

from attribution.tests.factories.attribution import AttributionNewFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class ApplicationTest(TestCase):
    def setUp(self):
        # Creation Person/Tutor
        self.person = PersonFactory(global_id="98363454")
        TutorFactory(person=self.person)

        # Creation Json which will be store on attribution
        attributions = _get_attributions_dict()
        applications = _get_applications_dict()
        AttributionNewFactory(global_id=self.person.global_id,
                              attributions=attributions,
                              applications=applications)



def _get_attributions_dict():
    return [
        {'year': 2016, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '22.5',
         'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER'},
        {'year': 2017, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00', 'LECTURING': '20.5',
         'PRACTICAL_EXERCISES': '7.0', 'function': 'CO-HOLDER'},
        {'year': 2017, 'acronym': 'LBIR1300', 'title': 'Chimie complexe volume 2', 'weight': '7.50',
         'LECTURING': '12.5', 'PRACTICAL_EXERCISES': '9.5', 'function': 'HOLDER'},
    ]


def _get_applications_dict():
    return []