##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.test import TestCase

from base.models.person import Person
from base.models.utils.utils import get_object_or_none
from base.tests.factories.person import PersonFactory


class UtilsTest(TestCase):

    def test_get_object_or_none_exists(self):
        person = PersonFactory()
        object = get_object_or_none(Person, pk=person.pk)
        self.assertEqual(object, person)

    def test_get_object_or_none_does_not_exist(self):
        object = get_object_or_none(Person, pk=None)
        self.assertIsNone(object)

    def test_get_object_or_none_error(self):
        with self.assertRaises(ValueError):
            get_object_or_none(None)
