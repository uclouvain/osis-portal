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
import json

from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _
from django.test import TestCase

from base.forms.base_forms import RegistrationIdForm
import base.tests.models.test_offer_year
import base.tests.models.test_student
from base.tests.factories.student import StudentFactory
from base.tests.factories.person import PersonFactory
from performance.models.enums import offer_registration_state
from performance.tests.factories.student_performance import StudentPerformanceFactory
import performance.tests.models.test_student_performance
from performance.views import main

OK = 200
ACCESS_DENIED = 401


class TestMain(TestCase):
    def setUp(self):
        self.student_performance = performance.tests.models.test_student_performance.create_student_performance()
        self.offer_year = base.tests.models.test_offer_year.create_offer_year()
        self.json_points = performance.tests.models.test_student_performance.load_json_file("performance/tests/ressources/points2.json")
        self.json_points_2 = performance.tests.models.test_student_performance.load_json_file("performance/tests/ressources/points3.json")

    def test_convert_student_performance_to_dic(self):
        student_performance_dic = main.convert_student_performance_to_dic(self.student_performance)
        expected = {"academic_year": '2016 - 2017',
                    "acronym": "SINF2MS/G",
                    "title": " Master [120] en sciences informatiques, à finalité spécialisée ",
                    "pk": self.student_performance.pk,
                    "offer_registration_state": offer_registration_state.REGISTERED}
        self.assertDictEqual(student_performance_dic, expected)

    def test_convert_student_performance_misformated_to_dict(self):
        student_perf = performance.tests.models.test_student_performance.create_student_performance(acronym="SINF1BA")
        with open("performance/tests/ressources/points_missformated.json") as f:
            student_perf.data = json.load(f)
        self.assertIsNone(main.convert_student_performance_to_dic(student_perf))

    def test_check_right_access(self):
        student = base.tests.models.test_student.create_student(self.student_performance.registration_id)
        has_access = main.check_right_access(self.student_performance, student)
        self.assertTrue(has_access)

        student = base.tests.models.test_student.create_student(registration_id="879466")
        has_access = main.check_right_access(self.student_performance, student)
        self.assertFalse(has_access)


class ViewPerformanceHomeTest(TestCase):
    def setUp(self):
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)

        self.student = StudentFactory()

        self.url = reverse('performance_home')
        self.client.force_login(self.student.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_not_a_student(self):
        a_person = PersonFactory()
        self.client.logout()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_multiple_students_objects_for_one_user(self):
        StudentFactory(person=self.student.person)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'dashboard.html')

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('error_multiple_registration_id'))

    def test_with_empty_programs_list(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'performance_home_student.html')
        self.assertEqual(response.status_code, OK)

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['programs'], [])
        self.assertEqual(response.context['registration_states_to_show'],
                         offer_registration_state.STATES_TO_SHOW_ON_PAGE)

    def test_with_program_list(self):
        a_student_performance = StudentPerformanceFactory(registration_id=self.student.registration_id,
                                                          academic_year=2017)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'performance_home_student.html')
        self.assertEqual(response.status_code, OK)

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['programs'],
                         [{'academic_year': '2017 - 2018',
                           'acronym': a_student_performance.acronym,
                           'offer_registration_state': 'CESSATION',
                           'pk': a_student_performance.pk,
                           'title': ' Master [120] en sciences informatiques, à finalité spécialisée '}]
                         )
        self.assertEqual(response.context['registration_states_to_show'],
                         offer_registration_state.STATES_TO_SHOW_ON_PAGE)


class DisplayResultForSpecificStudentPerformanceTest(TestCase):
    def setUp(self):
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)

        self.student = StudentFactory()
        self.student_performance = StudentPerformanceFactory(registration_id=self.student.registration_id)

        self.url = reverse('performance_student_result', args=[self.student_performance.pk])
        self.client.force_login(self.student.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_not_a_student(self):
        a_person = PersonFactory()
        self.client.logout()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_multiple_students_objects_for_one_user(self):
        StudentFactory(person=self.student.person)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'dashboard.html')

        messages = list(response.context['messages'])

        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('error_multiple_registration_id'))

    def test_when_none_student_performance(self):
        self.student_performance.delete()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'access_denied.html')
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_when_trying_to_access_other_student_performance(self):
        an_other_student = StudentFactory()
        self.client.force_login(an_other_student.person.user)

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'access_denied.html')
        self.assertEqual(response.status_code, ACCESS_DENIED)

    def test_with_performance_present(self):
        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'performance_result_student.html')
        self.assertEqual(response.status_code, OK)

        self.assertJSONEqual(response.context['results'], json.dumps(self.student_performance.data))
        self.assertEqual(response.context['creation_date'], self.student_performance.creation_date)
        self.assertEqual(response.context['update_date'], self.student_performance.update_date)
        self.assertEqual(response.context['fetch_timed_out'], False)
        self.assertEqual(response.context['not_authorized_message'], None)

    def test_with_not_authorized_message(self):
        self.student_performance.authorized = False
        self.student_performance.save()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'performance_result_student.html')
        self.assertEqual(response.status_code, OK)

        self.assertJSONEqual(response.context['results'], json.dumps(self.student_performance.data))
        self.assertEqual(response.context['creation_date'], self.student_performance.creation_date)
        self.assertEqual(response.context['update_date'], self.student_performance.update_date)
        self.assertEqual(response.context['fetch_timed_out'], False)
        self.assertEqual(response.context['not_authorized_message'],
                         _('performance_result_note_not_autorized').format(_(self.student_performance.session_locked)))


class SelectStudentTest(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.user.user_permissions.add(Permission.objects.get(codename="is_faculty_administrator"))
        Group.objects.create(name="students")
        self.student = StudentFactory()
        self.student_performance = StudentPerformanceFactory(registration_id=self.student.registration_id)

        self.url = reverse('performance_administration')

        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url, follow=True)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_has_not_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url, follow=True)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_get_request(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_administration.html')

        self.assertIsInstance(response.context['form'], RegistrationIdForm)

    def test_invalid_registration_id_post_request(self):
        response = self.client.post(self.url, data={'registration_id': str(int(self.student.registration_id) - 1)})

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_administration.html')

        self.assertIsInstance(response.context['form'], RegistrationIdForm)

        self.assertFormError(response, 'form', 'registration_id', _('no_student_with_this_registration_id'))

    def test_valid_post_request(self):
        response = self.client.post(self.url, data={'registration_id': self.student.registration_id})

        expected_url = reverse('performance_student_programs_admin', args=[self.student.registration_id])
        self.assertRedirects(response, expected_url)


class VisualizeStudentPrograms(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.user.user_permissions.add(Permission.objects.get(codename="is_faculty_administrator"))
        Group.objects.create(name="students")
        self.student = StudentFactory()
        self.student_performance = StudentPerformanceFactory(registration_id=self.student.registration_id,
                                                             academic_year=2017)

        self.url = reverse('performance_student_programs_admin', args=[self.student.registration_id])

        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_has_not_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_with_no_corresponding_student(self):
        self.student.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

        self.assertEqual(response.context['student'], None)
        self.assertEqual(response.context['programs'], None)
        self.assertEqual(response.context['registration_states_to_show'],
                         offer_registration_state.STATES_TO_SHOW_ON_PAGE)

    def test_when_empty_programs_list(self):
        self.student_performance.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['programs'], [])
        self.assertEqual(response.context['registration_states_to_show'],
                         offer_registration_state.STATES_TO_SHOW_ON_PAGE)

    def test_when_program(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_home_admin.html')

        self.assertEqual(response.context['student'], self.student)
        self.assertEqual(response.context['programs'],
                         [{'academic_year': '2017 - 2018',
                           'acronym': self.student_performance.acronym,
                           'offer_registration_state': 'CESSATION',
                           'pk': self.student_performance.pk,
                           'title': ' Master [120] en sciences informatiques, à finalité spécialisée '}]
                         )
        self.assertEqual(response.context['registration_states_to_show'],
                         offer_registration_state.STATES_TO_SHOW_ON_PAGE)


class VisualizeStudentResult(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.user.user_permissions.add(Permission.objects.get(codename="is_faculty_administrator"))
        self.student_performance = StudentPerformanceFactory()

        self.url = reverse('performance_student_result_admin', args=[self.student_performance.pk])

        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, "/login/?next={}".format(self.url))

    def test_user_has_not_permission(self):
        a_person = PersonFactory()
        self.client.force_login(a_person.user)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def test_no_corresponding_student_performance(self):
        self.student_performance.delete()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_result_admin.html')

        self.assertEqual(response.context['results'], None)
        self.assertEqual(response.context['creation_date'], None)
        self.assertEqual(response.context['update_date'], None)
        self.assertEqual(response.context['fetch_timed_out'], None)
        self.assertEqual(response.context['not_authorized_message'], None)

    def test_when_found_student_performance(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'admin/performance_result_admin.html')

        self.assertJSONEqual(response.context['results'], json.dumps(self.student_performance.data))
        self.assertEqual(response.context['creation_date'], self.student_performance.creation_date)
        self.assertEqual(response.context['update_date'], self.student_performance.update_date)
        self.assertEqual(response.context['fetch_timed_out'], False)
        self.assertEqual(response.context['not_authorized_message'], None)

    def test_with_not_authorized_message(self):
        self.student_performance.authorized = False
        self.student_performance.save()

        response = self.client.get(self.url)

        self.assertTemplateUsed(response, 'admin/performance_result_admin.html')
        self.assertEqual(response.status_code, OK)

        self.assertJSONEqual(response.context['results'], json.dumps(self.student_performance.data))
        self.assertEqual(response.context['creation_date'], self.student_performance.creation_date)
        self.assertEqual(response.context['update_date'], self.student_performance.update_date)
        self.assertEqual(response.context['fetch_timed_out'], False)
        self.assertEqual(response.context['not_authorized_message'],
                         _('performance_result_note_not_autorized').format(_(self.student_performance.session_locked)))


class ViewPerformanceByAcronymAndYear(TestCase):

    def __test_access_denied(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, ACCESS_DENIED)
        self.assertTemplateUsed(response, 'access_denied.html')

    def __test_access_ok(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, OK)
        self.assertTemplateUsed(response, 'performance_result_student.html')

    def setUp(self):
        self.simple_acronym_input = 'DROI1BA'
        self.simple_acronym = "DROI1BA"
        self.complex_acronym_input = 'DROI2MS_G'
        self.complex_acronym = "DROI2MS/G"
        self.invalid_acronym_input = "BIR1BA"
        self.acronym_with_space_input = "IAG IS"
        self.acronym_with_space = "IAG IS"
        self.valid_year = 2017
        self.invalid_year = 2020
        self.person = PersonFactory()
        students_group = Group.objects.create(name="students")
        permission = Permission.objects.get(codename="is_student")
        students_group.permissions.add(permission)
        self.student = StudentFactory()
        self.student_performance = StudentPerformanceFactory(registration_id=self.student.registration_id,
                                                             academic_year=self.valid_year,
                                                             acronym=self.simple_acronym)
        self.student_performance_complex = StudentPerformanceFactory(registration_id=self.student.registration_id,
                                                                     academic_year=self.valid_year,
                                                                     acronym=self.complex_acronym)
        self.student_performance_with_space = StudentPerformanceFactory(registration_id=self.student.registration_id,
                                                                        academic_year=self.valid_year,
                                                                        acronym=self.acronym_with_space)

    def test_clean_acronym(self):
        self.assertEqual(self.simple_acronym, main._clean_acronym(self.simple_acronym_input))
        self.assertEqual(self.complex_acronym, main._clean_acronym(self.complex_acronym_input))
        self.assertEqual(self.complex_acronym, main._clean_acronym("droi2ms_g"))

    def test_anonymous(self):
        self.client.logout()
        url = reverse('performance_student_by_acronym_and_year', args=[self.simple_acronym_input, self.valid_year])
        response = self.client.get(url)
        self.assertRedirects(response, "/login/?next={}".format(url))

    def test_non_student(self):
        self.client.force_login(self.person.user)
        url = reverse('performance_student_by_acronym_and_year', args=[self.simple_acronym_input, self.valid_year])
        self.__test_access_denied(url)

    def test_valid_student(self):
        self.client.force_login(self.student.person.user)
        url = reverse('performance_student_by_acronym_and_year', args=[self.simple_acronym_input, self.valid_year])
        self.__test_access_ok(url)
        url = reverse('performance_student_by_acronym_and_year', args=[self.complex_acronym_input, self.valid_year])
        self.__test_access_ok(url)

    def test_invalid_student(self):
        self.client.force_login(self.student.person.user)
        url = reverse('performance_student_by_acronym_and_year', args=[self.simple_acronym_input, self.invalid_year])
        self.__test_access_denied(url)
        url = reverse('performance_student_by_acronym_and_year', args=[self.invalid_acronym_input, self.valid_year])
        self.__test_access_denied(url)

    def test_acronym_with_space(self):
        self.client.force_login(self.student.person.user)
        url = reverse('performance_student_by_acronym_and_year', args=[self.acronym_with_space_input, self.valid_year])
        self.__test_access_ok(url)
