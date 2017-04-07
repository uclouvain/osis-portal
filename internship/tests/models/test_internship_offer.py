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
from internship.models import internship_offer
from internship.tests.models import test_organization, test_internship_speciality
from internship.tests.factories.cohort import CohortFactory

def create_internship_offer(cohort=None):
    if cohort == None:
        cohort = CohortFactory()
    organization = test_organization.create_organization()
    speciality = test_internship_speciality.create_speciality()
    offer = internship_offer.InternshipOffer(speciality=speciality, organization=organization, title="offer_test", cohort=cohort,
                                             maximum_enrollments=20)
    offer.save()
    return offer


def create_specific_internship_offer(organization, speciality, title="offer_test", cohort=None):
    if cohort == None:
        cohort = CohortFactory()
    offer = internship_offer.InternshipOffer(speciality=speciality, organization=organization, title=title, cohort=cohort,
                                             maximum_enrollments=20)
    offer.save()
    return offer


class TestInternshipOffer(TestCase):
    def setUp(self):
        self.offer = create_internship_offer()

    def test_find_by_speciality(self):
        speciality = self.offer.speciality
        actual_offers = internship_offer.find_by_speciality(speciality)
        self.assertIn(self.offer, actual_offers)

        speciality = test_internship_speciality.create_speciality(name="radiologie")
        actual_offers = internship_offer.find_by_speciality(speciality)
        self.assertNotIn(self.offer, actual_offers)

    def test_get_py_pk(self):
        pk = self.offer.pk
        actual_offer = internship_offer.find_by_pk(pk)
        self.assertEquals(self.offer, actual_offer)

        pk = 45
        self.assertFalse(internship_offer.find_by_pk(pk))

    def test_get_number_selectable(self):
        expected = 1
        actual = internship_offer.get_number_selectable(self.offer.cohort)
        self.assertEqual(expected, actual)

        self.offer.selectable = False
        self.offer.save()
        expected = 0
        actual = internship_offer.get_number_selectable(self.offer.cohort)
        self.assertEqual(expected, actual)

    def test_find_selectable_by_speciality(self):
        speciality = test_internship_speciality.create_speciality("OTHER", "OTHER", cohort=self.offer.cohort)
        organization = test_organization.create_organization("ORG", "ORG", "02", cohort=self.offer.cohort)
        other_offer = create_specific_internship_offer(organization, speciality, "other_offer", cohort=self.offer.cohort)

        actual = list(internship_offer.find_selectable_by_speciality_and_cohort(self.offer.speciality, self.offer.cohort))
        self.assertEqual(len(actual), 1)
        self.assertIn(self.offer, actual)

        self.offer.selectable = False
        self.offer.save()
        actual = list(internship_offer.find_selectable_by_speciality_and_cohort(speciality=self.offer.speciality, cohort=self.offer.cohort))
        self.assertEqual(len(actual), 0)

        actual = list(internship_offer.find_selectable_by_speciality_and_cohort(speciality, self.offer.cohort))
        self.assertEqual(len(actual), 1)
        self.assertIn(other_offer, actual)
