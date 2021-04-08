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
import uuid

import mock
from django.contrib.auth.models import Permission
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.student import StudentFactory
from base.tests.factories.user import UserFactory
from internship.models import internship_choice as mdl_internship_choice
from internship.models.enums.user_account_status import UserAccountStatus
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.models import test_internship_offer, test_organization, test_internship_speciality, \
    test_internship_choice, test_internship_student_information


class TestMain(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.user = cls.student.person.user
        cls.cohort = CohortFactory()
        cls.internship = InternshipFactory(cohort=cls.cohort)
        cls.student_information = test_internship_student_information.create_student_information(cls.user,
                                                                                                 cls.cohort,
                                                                                                 cls.student.person)
        add_permission(cls.user, "can_access_internship")

    def test_can_access_internship_student_home(self):
        home_url = reverse("internship_student_home", kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(home_url)
        self.assertEqual(response.status_code, 200)

    def test_can_access_internship_selection(self):
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(selection_url)
        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)
        response = self.client.get(selection_url)
        self.assertEqual(response.status_code, 200)

    @mock.patch('internship.services.internship.InternshipAPIService.get_master_by_email')
    @mock.patch('internship.services.internship.InternshipAPIService.activate_master_account')
    def test_first_master_access_activate_user_account(self, mock_activate, mock_get_master_email):
        mock_get_master_email.return_value = {'uuid': uuid.uuid4(), 'user_account_status': UserAccountStatus.INACTIVE}
        url = reverse("internship")
        self.client.force_login(self.user)
        self.client.get(url)
        self.assertTrue(mock_activate.called)


class TestSelectInternship(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.student = StudentFactory()
        cls.user = cls.student.person.user
        add_permission(cls.user, "can_access_internship")

        cls.cohort = CohortFactory()
        cls.student_information = test_internship_student_information.create_student_information(cls.user, cls.cohort,
                                                                                                 cls.student.person)

        cls.speciality_1 = test_internship_speciality.create_speciality(name="urgence", cohort=cls.cohort)
        cls.speciality_2 = test_internship_speciality.create_speciality(name="chirurgie", cohort=cls.cohort)
        cls.internship_1 = InternshipFactory(name=cls.speciality_1.name, cohort=cls.cohort,
                                             speciality=cls.speciality_1)
        cls.internship_2 = InternshipFactory(name=cls.speciality_2.name, cohort=cls.cohort,
                                             speciality=cls.speciality_2)

        cls.organization_1 = test_organization.create_organization(reference="01", cohort=cls.cohort)
        cls.organization_2 = test_organization.create_organization(reference="02", cohort=cls.cohort)
        cls.organization_3 = test_organization.create_organization(reference="03", cohort=cls.cohort)
        cls.organization_4 = test_organization.create_organization(reference="04", cohort=cls.cohort)
        cls.organization_5 = test_organization.create_organization(reference="05", cohort=cls.cohort)

        cls.offer_1 = test_internship_offer.create_specific_internship_offer(cls.organization_1, cls.speciality_1,
                                                                             cohort=cls.cohort)
        cls.offer_2 = test_internship_offer.create_specific_internship_offer(cls.organization_2, cls.speciality_1,
                                                                             cohort=cls.cohort)
        cls.offer_3 = test_internship_offer.create_specific_internship_offer(cls.organization_3, cls.speciality_1,
                                                                             cohort=cls.cohort)
        cls.offer_4 = test_internship_offer.create_specific_internship_offer(cls.organization_4, cls.speciality_1,
                                                                             cohort=cls.cohort)

        cls.offer_5 = test_internship_offer.create_specific_internship_offer(cls.organization_1, cls.speciality_2,
                                                                             cohort=cls.cohort)
        cls.offer_6 = test_internship_offer.create_specific_internship_offer(cls.organization_5, cls.speciality_2,
                                                                             cohort=cls.cohort)

    def setUp(self):
        self.client.force_login(self.user)

    def test_with_zero_choices(self):
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        response = self.client.post(selection_url, data={})
        self.assertEqual(response.status_code, 200)

    def test_with_one_choice(self):
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        response = self.client.post(selection_url, data={
            '{}-TOTAL_FORMS'.format(self.speciality_2.name): '2',
            '{}-INITIAL_FORMS'.format(self.speciality_2.name): '0',
            '{}-MIN_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-MAX_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-0-offer'.format(self.speciality_2.name): str(self.offer_5.id),
            '{}-0-preference'.format(self.speciality_2.name): '1',
            '{}-1-offer'.format(self.speciality_2.name): str(self.offer_6.id),
            '{}-1-preference'.format(self.speciality_2.name): '0',
            'current_internship'.format(self.speciality_2.name): self.internship_2.id,
        })
        choices = list(mdl_internship_choice.search(student=self.student))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(choices), 1)
        self.assertEqual(choices[0].organization, self.organization_1)
        self.assertEqual(choices[0].speciality, self.speciality_2)
        self.assertEqual(choices[0].internship_id, self.internship_2.id)
        self.assertEqual(choices[0].choice, 1)

    def test_with_multiple_internships_choices(self):
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        response = self.client.post(selection_url, data={
            '{}-TOTAL_FORMS'.format(self.speciality_1.name): '4',
            '{}-INITIAL_FORMS'.format(self.speciality_1.name): '0',
            '{}-MIN_NUM_FORMS'.format(self.speciality_1.name): '4',
            '{}-MAX_NUM_FORMS'.format(self.speciality_1.name): '4',
            '{}-0-offer'.format(self.speciality_1.name): str(self.offer_1.id),
            '{}-0-preference'.format(self.speciality_1.name): '1',
            '{}-1-offer'.format(self.speciality_1.name): str(self.offer_2.id),
            '{}-1-preference'.format(self.speciality_1.name): '2',
            '{}-2-offer'.format(self.speciality_1.name): str(self.offer_3.id),
            '{}-2-preference'.format(self.speciality_1.name): '3',
            '{}-3-offer'.format(self.speciality_1.name): str(self.offer_4.id),
            '{}-3-preference'.format(self.speciality_1.name): '4',
            '{}-TOTAL_FORMS'.format(self.speciality_2.name): '2',
            '{}-INITIAL_FORMS'.format(self.speciality_2.name): '0',
            '{}-MIN_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-MAX_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-0-offer'.format(self.speciality_2.name): str(self.offer_5.id),
            '{}-0-preference'.format(self.speciality_2.name): '1',
            '{}-1-offer'.format(self.speciality_2.name): str(self.offer_6.id),
            '{}-1-preference'.format(self.speciality_2.name): '2',
            'current_internship'.format(self.speciality_2.name): self.internship_2.id,
        })
        choices = list(mdl_internship_choice.search(student=self.student))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(choices), 6)

    def test_with_incorrect_speciality(self):
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        self.client.post(selection_url, data={
            '{}-TOTAL_FORMS'.format(self.speciality_1.name): '4',
            '{}-INITIAL_FORMS'.format(self.speciality_1.name): '0',
            '{}-MIN_NUM_FORMS'.format(self.speciality_1.name): '4',
            '{}-MAX_NUM_FORMS'.format(self.speciality_1.name): '4',
            '{}-0-offer'.format(self.speciality_1.name): str(self.offer_1.id),
            '{}-0-preference'.format(self.speciality_1.name): '1',
            '{}-1-offer'.format(self.speciality_1.name): str(self.offer_5.id),
            '{}-1-preference'.format(self.speciality_1.name): '2',
            '{}-2-offer'.format(self.speciality_1.name): str(self.offer_3.id),
            '{}-2-preference'.format(self.speciality_1.name): '0',
            '{}-3-offer'.format(self.speciality_1.name): str(self.offer_4.id),
            '{}-3-preference'.format(self.speciality_1.name): '0',
            'current_internship'.format(self.speciality_1.name): self.internship_1.id,
        })
        choices = list(mdl_internship_choice.search(student=self.student))
        self.assertEqual(len(choices), 1)

    def test_replace_previous_choices(self):
        previous_choice = test_internship_choice.create_internship_choice(
            test_organization.create_organization(),
            self.student, self.speciality_2, self.internship_1
        )
        choices = list(mdl_internship_choice.search(student=self.student, speciality=self.speciality_2))
        self.assertEqual(len(choices), 1)
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        self.client.post(selection_url, data={
            '{}-TOTAL_FORMS'.format(self.speciality_2.name): '2',
            '{}-INITIAL_FORMS'.format(self.speciality_2.name): '0',
            '{}-MIN_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-MAX_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-0-offer'.format(self.speciality_2.name): str(self.offer_5.id),
            '{}-0-preference'.format(self.speciality_2.name): '1',
            '{}-1-offer'.format(self.speciality_2.name): str(self.offer_6.id),
            '{}-1-preference'.format(self.speciality_2.name): '0',
            'current_internship'.format(self.speciality_2.name): self.internship_2.id,
        })
        choices = list(mdl_internship_choice.search(student=self.student, speciality=self.speciality_2))
        self.assertEqual(len(choices), 1)
        self.assertNotEqual(previous_choice, choices[0])

    def test_two_personal_internships_at_most(self):
        organization = test_organization.create_organization(name="Stage personnel")
        speciality = test_internship_speciality.create_speciality(name="Stage personnel",
                                                                  acronym="SP")
        offer = test_internship_offer.create_specific_internship_offer(organization, speciality,
                                                                       title="Stage personnel")
        choice_1 = test_internship_choice.create_internship_choice(
            organization, self.student, speciality, self.internship_1
        )
        choice_2 = test_internship_choice.create_internship_choice(
            organization, self.student, speciality, self.internship_2
        )
        selection_url = reverse("select_internship", kwargs={'cohort_id': self.cohort.id})
        self.client.post(selection_url, data={
            '{}-TOTAL_FORMS'.format(self.speciality_2.name): '2',
            '{}-INITIAL_FORMS'.format(self.speciality_2.name): '0',
            '{}-MIN_NUM_FORMS'.format(self.speciality_2.name): '2',
            '{}-MAX_NUM_FORMS'.format(self.speciality_2.name): '2',
            'form-0-offer': str(offer.id),
            'form-0-preference': '1',
            'current_internship'.format(self.speciality_2.name): self.internship_2.id,
        })
        choices = list(mdl_internship_choice.search(student=self.student))
        self.assertEqual(len(choices), 2)
        self.assertIn(choice_1, choices)
        self.assertIn(choice_2, choices)


def add_permission(user, codename):
    perm = Permission.objects.get(codename=codename)
    user.user_permissions.add(perm)


class TestAjaxSelectiveInternship(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.student = StudentFactory(person__user=cls.user)
        add_permission(cls.student.person.user, "can_access_internship")
        cls.cohort = CohortFactory()
        cls.student_information = test_internship_student_information.create_student_information(
            cls.user,
            cls.cohort,
            cls.student.person
        )
        cls.selective_internship = InternshipFactory(
            name='Selective internship',
            cohort=cls.cohort,
            speciality=None
        )
        cls.specialty = test_internship_speciality.create_speciality(name="specialty", cohort=cls.cohort)

    def setUp(self):
        self.client.force_login(self.user)

    def test_get_specialty_preferences(self):
        selection_url = reverse("selective_internship_preferences", kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(selection_url, data={
            'student': self.student.pk,
            'internship': self.selective_internship.pk,
            'specialty': self.specialty.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fragment/internship_preferences.html')
