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
from django.contrib.auth.models import User, Permission
from django.test import TestCase
from django.urls import reverse

import base.tests.models.test_student
from internship.models import internship_choice as mdl_internship_choice
from internship.tests.factories.cohort import CohortFactory
from internship.tests.factories.internship import InternshipFactory
from internship.tests.models import test_internship_offer, test_organization, test_internship_speciality, \
    test_internship_choice, test_internship_student_information


class TestMain(TestCase):
    def setUp(self):
        self.student = base.tests.models.test_student.create_student("45451298")
        self.user = User.objects.create_user('user', 'user@test.com', 'userpass')
        self.student.person.user = self.user
        self.student.person.save()
        self.cohort = CohortFactory()
        self.internship = InternshipFactory(cohort=self.cohort)
        self.student_information = test_internship_student_information.create_student_information(self.user,
                                                                                                  self.cohort,
                                                                                                  self.student.person)
        add_permission(self.student.person.user, "can_access_internship")

    def test_can_access_internship_home(self):
        home_url = reverse("internship_home", kwargs={'cohort_id': self.cohort.id})
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


class TestSelectInternship(TestCase):
    def setUp(self):
        self.student = base.tests.models.test_student.create_student("45451298")
        user = User.objects.create_user('user', 'user@test.com', 'userpass')
        self.student.person.user = user
        self.student.person.save()
        add_permission(self.student.person.user, "can_access_internship")

        self.client.force_login(user)

        self.cohort = CohortFactory()
        self.student_information = test_internship_student_information.create_student_information(user, self.cohort,
                                                                                                  self.student.person)

        self.speciality_1 = test_internship_speciality.create_speciality(name="urgence", cohort=self.cohort)
        self.speciality_2 = test_internship_speciality.create_speciality(name="chirurgie", cohort=self.cohort)
        self.internship_1 = InternshipFactory(name=self.speciality_1.name, cohort=self.cohort,
                                              speciality=self.speciality_1)
        self.internship_2 = InternshipFactory(name=self.speciality_2.name, cohort=self.cohort,
                                              speciality=self.speciality_2)

        self.organization_1 = test_organization.create_organization(reference="01", cohort=self.cohort)
        self.organization_2 = test_organization.create_organization(reference="02", cohort=self.cohort)
        self.organization_3 = test_organization.create_organization(reference="03", cohort=self.cohort)
        self.organization_4 = test_organization.create_organization(reference="04", cohort=self.cohort)
        self.organization_5 = test_organization.create_organization(reference="05", cohort=self.cohort)

        self.offer_1 = test_internship_offer.create_specific_internship_offer(self.organization_1, self.speciality_1,
                                                                              cohort=self.cohort)
        self.offer_2 = test_internship_offer.create_specific_internship_offer(self.organization_2, self.speciality_1,
                                                                              cohort=self.cohort)
        self.offer_3 = test_internship_offer.create_specific_internship_offer(self.organization_3, self.speciality_1,
                                                                              cohort=self.cohort)
        self.offer_4 = test_internship_offer.create_specific_internship_offer(self.organization_4, self.speciality_1,
                                                                              cohort=self.cohort)

        self.offer_5 = test_internship_offer.create_specific_internship_offer(self.organization_1, self.speciality_2,
                                                                              cohort=self.cohort)
        self.offer_6 = test_internship_offer.create_specific_internship_offer(self.organization_5, self.speciality_2,
                                                                              cohort=self.cohort)

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
    perm = get_permission(codename)
    user.user_permissions.add(perm)


def get_permission(codename):
    return Permission.objects.get(codename=codename)


class TestAjaxSelectiveInternship(TestCase):
    def setUp(self):
        self.student = base.tests.models.test_student.create_student("45451298")
        user = User.objects.create_user('user', 'user@test.com', 'userpass')
        self.student.person.user = user
        self.student.person.save()
        add_permission(self.student.person.user, "can_access_internship")
        self.client.force_login(user)
        self.cohort = CohortFactory()
        self.student_information = test_internship_student_information.create_student_information(
            user,
            self.cohort,
            self.student.person
        )
        self.selective_internship = InternshipFactory(
            name='Selective internship',
            cohort=self.cohort,
            speciality=None
        )
        self.specialty = test_internship_speciality.create_speciality(name="specialty", cohort=self.cohort)

    def test_get_specialty_preferences(self):
        selection_url = reverse("selective_internship_preferences", kwargs={'cohort_id': self.cohort.id})
        response = self.client.get(selection_url, data={
            'student': self.student.pk,
            'internship': self.selective_internship.pk,
            'specialty': self.specialty.pk
        })
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'fragment/internship_preferences.html')
