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

from base import models as mdl_base
from base.tests.factories.learning_unit import LearningUnitFactory


def create_learning_unit(data):
    learning_unit = mdl_base.learning_unit.LearningUnit()
    if 'acronym' in data:
        learning_unit.acronym = data['acronym']
    if 'title' in data:
        learning_unit.title = data['title']
    if 'description' in data:
        learning_unit.description = data['description']
    learning_unit.save()
    return learning_unit


class LearningUnitTest(TestCase):
    def setUp(self):
        self.title = "Title"
        self.acronym = "Acronym"
        self.learning_unit = LearningUnitFactory(title=self.title, acronym=self.acronym)

    def test_str(self):
        self.assertEqual(str(self.learning_unit), "{} - {}".format(self.acronym, self.title))

    def test_find_by_id(self):
        a_learning_unit = mdl_base.learning_unit.find_by_id(self.learning_unit.id)

        self.assertEqual(a_learning_unit, self.learning_unit)

    def test_search(self):
        self.assertListEqual(list(mdl_base.learning_unit.search(self.acronym)), [self.learning_unit])

        self.assertFalse(mdl_base.learning_unit.search("Other Acronym"))

