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

from internship.models import organization as mdl_organization
from django.test import TestCase
from internship.tests.factories.cohort import CohortFactory


def create_organization(name="OSIS", acronym="OSIS", reference="01", cohort=None):
    if cohort == None:
        cohort = CohortFactory()
    organization = mdl_organization.Organization(name=name, acronym=acronym, reference=reference, cohort=cohort)
    organization.save()
    return organization


class TestSearch(TestCase):
    def setUp(self):
        self.cohort = CohortFactory()
        self.organization = create_organization(cohort=self.cohort)
        self.organization2 = create_organization(name="OSAS", reference="02", cohort=self.cohort)

    def test_with_specific_name(self):
        organizations = list(mdl_organization.search("OSIS", self.cohort))
        self.assertListEqual(organizations, [self.organization])

    def test_with_no_match(self):
        organizations = list(mdl_organization.search("NO MATCH", self.cohort))
        self.assertFalse(organizations)

    def test_with_prefix(self):
        organizations = list(mdl_organization.search("OS", self.cohort))
        self.assertEqual(len(organizations), 2)
        self.assertIn(self.organization, organizations)
        self.assertIn(self.organization2, organizations)

