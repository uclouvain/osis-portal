##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2017-2018 Université catholique de Louvain (http://www.uclouvain.be)
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

from reference.models import domain
from reference.tests.factories.domain import DomainFactory

class TestFindSubdomains(TestCase):
    def setUp(self):
        self.parent_domain = DomainFactory()

    def test_with_no_subdomdains(self):
        subdomains = list(domain.find_subdomains(self.parent_domain))
        self.assertEqual(subdomains, [])

    def test_with_subdomains(self):
        children_1 = DomainFactory(parent=self.parent_domain)
        children_2 = DomainFactory(parent=self.parent_domain)

        subdomains = list(domain.find_subdomains(self.parent_domain))
        self.assertEqual(len(subdomains), 2)
        self.assertIn(children_1, subdomains)
        self.assertIn(children_2, subdomains)