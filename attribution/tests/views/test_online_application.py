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
import datetime

from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from attribution.models.enums import function
from attribution.tests.factories.attribution import AttributionNewFactory
from attribution.utils import tutor_application_epc
from base.models.enums import academic_calendar_type
from base.models.enums import learning_component_year_type
from base.models.enums import vacant_declaration_type
from base.tests.factories.academic_calendar import AcademicCalendarFactory
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.learning_unit_component import LearningUnitComponentFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory
from base.tests.factories.user import UserFactory
from base.models.enums import component_type, learning_unit_year_subtypes
from base.tests.factories.entity import EntityFactory
from base.tests.factories.entity_version import EntityVersionFactory
from base.tests.factories.entity_container_year import EntityContainerYearFactory
from base.models.enums import entity_container_year_link_type as entity_types


class TestOnlineApplication(TestCase):
    def setUp(self):
        # Create Group tutor
        Group.objects.create(name="tutors")

        # Create user
        user = UserFactory(username="tutor_application")
        person = PersonFactory(global_id="578945612", user=user)
        self.tutor = TutorFactory(person=person)

        # Add permission and log into app
        add_permission(user, "can_access_attribution_application")
        self.client.force_login(user)

        # Create current academic year
        today = datetime.datetime.today()
        self.current_academic_year = create_current_academic_year()

        # Create application year
        # Application is always next year
        self.application_academic_year = AcademicYearFactory(year=self.current_academic_year.year + 1)

        # Create Event to allow teacher to register
        start_date = datetime.datetime.today() - datetime.timedelta(days=10)
        end_date = datetime.datetime.today() + datetime.timedelta(days=15)
        self.academic_calendar = AcademicCalendarFactory(
            academic_year=self.current_academic_year,
            reference=academic_calendar_type.TEACHING_CHARGE_APPLICATION,
            start_date=start_date,
            end_date=end_date
        )
        self.agro_entity = EntityFactory()
        self.agro_entity_version = EntityVersionFactory(entity=self.agro_entity, acronym="AGRO",
                                                        entity_type='FACULTY',
                                                        start_date=self.academic_calendar.start_date,
                                                        end_date=self.academic_calendar.end_date)

        self.drt_entity = EntityFactory()
        self.drt_entity_version = EntityVersionFactory(entity=self.drt_entity, acronym="DRT",
                                                       entity_type='FACULTY',
                                                       start_date=self.academic_calendar.start_date,
                                                       end_date=self.academic_calendar.end_date)

        # Creation context with multiple learning container year
        self._create_multiple_learning_container_year()
        self.attribution = AttributionNewFactory(
            global_id=person.global_id,
            applications=self._get_default_application_list(),
            attributions=self._get_default_attribution_list()
        )


    def test_redirection_to_outside_encoding_period(self):
        # Remove teaching charge application event
        self.academic_calendar.delete()
        url = reverse('applications_overview')
        url_outside = reverse('outside_applications_period')
        response = self.client.get(url)
        self.assertRedirects(response, "%s?next=%s" % (url_outside, url))  # Redirection

    def test_message_outside_encoding_period(self):
        # Remove teaching charge application event
        self.academic_calendar.delete()
        url = reverse('outside_applications_period')
        response = self.client.get(url)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'warning')
        self.assertEqual(messages[0].message, _('The period of online application is closed'))

    def test_applictions_overview(self):
        url = reverse('applications_overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['a_tutor'], self.tutor)
        self.assertEqual(context['current_academic_year'], self.current_academic_year)
        self.assertEqual(context['application_year'], self.application_academic_year)
        self.assertEqual(len(context['attributions']), 1)
        self.assertEqual(context['attributions'][0]['acronym'], self.lagro2500_next.acronym)
        self.assertEqual(len(context['applications']), 1)
        self.assertEqual(context['applications'][0]['acronym'], self.lagro1600_next.acronym)
        self.assertEqual(len(context['attributions_about_to_expire']), 1)
        self.assertEqual(context['attributions_about_to_expire'][0]['acronym'], self.lbir1300_current.acronym)

    def test_applications_overview_post_method_not_allowed(self):
        url = reverse('applications_overview')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_search_vacant_attribution_initial(self):
        url = reverse('vacant_attributions_search')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context[0]
        self.assertEqual(context['a_tutor'], self.tutor)
        self.assertTrue(context['search_form'])
        self.assertFalse(context['attributions_vacant'])

    def test_search_vacant_attribution_post_not_allowed(self):
        url = reverse('vacant_attributions_search')
        response = self.client.post(url)
        self.assertEqual(response.status_code, 405)

    def test_search_vacant_attribution_search_list(self):
        url = reverse('vacant_attributions_search')
        response = self.client.get(url, data={'learning_container_acronym': 'LAGRO'})
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(context['a_tutor'], self.tutor)
        self.assertTrue(context['search_form'])
        self.assertEqual(len(context['attributions_vacant']), 2)
        # Check if LAGRO1600 have the boolean already applied
        self.assertTrue((next(attrib for attrib in context['attributions_vacant']
                              if attrib.get('acronym') == self.lagro1600_next.acronym and
                              attrib.get('already_applied')), False))

    def test_search_vacant_attribution_search_list_by_faculty(self):
        url = reverse('vacant_attributions_search')
        response = self.client.get(
            url, data={
                'learning_container_acronym': 'LAGRO',
                'faculty': self.agro_entity_version.id
            }
        )
        self.assertEqual(response.status_code, 200)
        context = response.context[-1]
        self.assertEqual(len(context['attributions_vacant']), 2)


    def test_search_vacant_attribution_with_delcaration_vac_not_allowed(self):
        # Create container with type_declaration_vacant not in [RESEVED_FOR_INTERNS, OPEN_FOR_EXTERNS]
        self.lagro1234_current = _create_learning_container_with_components("LAGRO1234", self.current_academic_year)
        # Creation learning container for next academic year [==> application academic year]
        self.lagro1234_next = _create_learning_container_with_components\
            ("LAGRO1234", self.application_academic_year, 70, 70,
             type_declaration_vacant=vacant_declaration_type.DO_NOT_ASSIGN)
        url = reverse('vacant_attributions_search')
        response = self.client.get(url, data={'learning_container_acronym': 'LAGRO1234'})
        self.assertEqual(response.status_code, 200)
        context = response.context[0]
        self.assertEqual(context['a_tutor'], self.tutor)
        self.assertTrue(context['search_form'])
        self.assertFalse(context['attributions_vacant'])

    def test_renew_applications(self):
        url = reverse('renew_applications')
        post_data = {'learning_container_year_' + self.lbir1300_next.acronym: 'on'}
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)  # redirection
        self.attribution.refresh_from_db()
        self.assertEqual(len(self.attribution.applications), 2)  # Now we have two applications

    def test_renew_applications_with_bad_learning_container(self):
        url = reverse('renew_applications')
        post_data = {'learning_container_year_' + self.lagro2500_next.acronym: 'on'}
        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        messages = list(response.context['messages'])
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0].tags, 'error')
        self.assertEqual(messages[0].message, _('No attribution renewed'))

    def test_renew_applications_method_not_allowed(self):
        url = reverse('renew_applications')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_delete_application(self):
        url = reverse('delete_tutor_application', kwargs={'learning_container_year_id': self.lagro1600_next.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 302)  # redirection
        self.attribution.refresh_from_db()
        # pending flag must be set to 'deleted'
        self.assertTrue((next(attrib for attrib in self.attribution.applications
                              if attrib.get('acronym') == self.lagro1600_next.acronym and
                              attrib.get('pending') == tutor_application_epc.DELETE_OPERATION), False))

    def test_delete_application_with_wrong_container(self):
        url = reverse('delete_tutor_application', kwargs={'learning_container_year_id': self.lbir1300_next.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 404)  # Not found

    def test_delete_application_method_not_allowed(self):
        url = reverse('delete_tutor_application', kwargs={'learning_container_year_id': self.lagro1600_next.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 405)

    def test_get_edit_application_form(self):
        url = reverse('create_or_update_tutor_application',
                      kwargs={'learning_container_year_id': self.lagro1600_next.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context[0]
        self.assertEqual(context['a_tutor'], self.tutor)
        self.assertEqual(context['learning_container_year'], self.lagro1600_next)
        self.assertTrue(context['form'])

    def test_post_edit_application_form(self):
        url = reverse('create_or_update_tutor_application',
                      kwargs={'learning_container_year_id': self.lagro1600_next.id})
        post_data = _get_application_example(self.lagro1600_next, '54', '7')
        response = self.client.post(url, data=post_data, follow=True)
        self.assertEqual(response.status_code, 200)
        self.attribution.refresh_from_db()
        self.assertEqual(len(self.attribution.applications), 1)
        self.assertEqual(self.attribution.applications[0]['charge_lecturing_asked'], '54.0')
        self.assertEqual(self.attribution.applications[0]['charge_practical_asked'], '7.0')
        self.assertEqual(self.attribution.applications[0]['pending'], tutor_application_epc.UPDATE_OPERATION)

    def test_post_edit_application_form_with_empty_value(self):
        url = reverse('create_or_update_tutor_application',
                      kwargs={'learning_container_year_id': self.lagro1600_next.id})
        post_data = _get_application_example(self.lagro1600_next, None, None)
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        context = response.context[0]
        self.assertTrue(context.get('form'))
        form = context['form']
        self.assertTrue(form.errors)  # Not valid because not number entered

    def test_post_edit_application_form_with_empty_lecturing_value(self):
        url = reverse('create_or_update_tutor_application',
                      kwargs={'learning_container_year_id': self.lagro1600_next.id})
        post_data = _get_application_example(self.lagro1600_next, "15", "")
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 302)
        self.attribution.refresh_from_db()
        self.assertEqual(len(self.attribution.applications), 1)
        self.assertEqual(self.attribution.applications[0]['charge_lecturing_asked'], '15.0')
        self.assertEqual(self.attribution.applications[0]['charge_practical_asked'], '0.0')
        self.assertEqual(self.attribution.applications[0]['pending'], tutor_application_epc.UPDATE_OPERATION)

    def test_post_edit_application_form_with_value_under_zero(self):
        url = reverse('create_or_update_tutor_application',
                      kwargs={'learning_container_year_id': self.lagro1600_next.id})
        post_data = _get_application_example(self.lagro1600_next, '-1', '5')
        response = self.client.post(url, data=post_data)
        self.assertEqual(response.status_code, 200)
        context = response.context[0]
        self.assertTrue(context.get('form'))
        form = context['form']
        self.assertTrue(form.errors)  # Not valid because -1 entered

    def test_post_overview_with_lecturing_and_practical_component_partim(self):
        lbira2101a_next = _create_learning_container_with_components("LBIRA2101A", self.application_academic_year,
                                                                     volume_lecturing=20, volume_practical_exercices=20,
                                                                         subtype=learning_unit_year_subtypes.PARTIM)
        lbira2101a_current = _create_learning_container_with_components(
            "LBIRA2101A", self.current_academic_year,
            volume_lecturing=20, volume_practical_exercices=20,
            subtype=learning_unit_year_subtypes.PARTIM)
        _link_components_and_learning_unit_year_to_container(lbira2101a_current, "LBIRA2101",
                                                             subtype=learning_unit_year_subtypes.FULL)
        _link_components_and_learning_unit_year_to_container(lbira2101a_next, "LBIRA2101",
                                                             subtype=learning_unit_year_subtypes.FULL)
        self.attribution.delete()
        self.attribution = AttributionNewFactory(
            global_id=self.tutor.person.global_id,
            applications=[_get_application_example(lbira2101a_next, "10", "10")]
        )

        url = reverse('applications_overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        context = response.context[0]
        self.assertEqual(len(context['applications']), 1)
        self.assertEqual(context['applications'][0]['acronym'], lbira2101a_next.acronym)
        with self.assertRaises(KeyError):
            context['applications'][0]['PRACTICAL_EXERCISES']
        with self.assertRaises(KeyError):
            context['applications'][0]['LECTURING']

    def _create_multiple_learning_container_year(self):
        # ici
        # Creation learning container for current academic year
        self.lbir1200_current = _create_learning_container_with_components("LBIR1200", self.current_academic_year)
        self.lbir1300_current = _create_learning_container_with_components("LBIR1300", self.current_academic_year)
        self.ldroi1500_current = _create_learning_container_with_components("LDROI1500", self.current_academic_year)

        # Creation learning container for next academic year [==> application academic year]
        self.lbir1200_next = _create_learning_container_with_components("LBIR1200", self.application_academic_year,
                                                                        70, 70)
        self.lbir1300_next = _create_learning_container_with_components("LBIR1300", self.application_academic_year,
                                                                        60, 60)
        self.lagro1600_next = _create_learning_container_with_components("LAGRO1600", self.application_academic_year,
                                                                         54, 7)
        self.lagro2500_next = _create_learning_container_with_components("LAGRO2500", self.application_academic_year,
                                                                         0, 70)
        self._create_entity_container_yrs()


    def _get_default_application_list(self):
        return [
            _get_application_example(self.lagro1600_next, '15', '0')
        ]

    def _get_default_attribution_list(self):
        return [
            # Attribution in current year
            _get_attribution_example(self.lbir1200_current, '20.0', '31.5', 2015, 2019),
            _get_attribution_example(self.lbir1300_current, '21.5', '40', 2015, self.current_academic_year.year),
            # Attribution in next year
            _get_attribution_example(self.lagro2500_next, '29', '10', 2015, 2020)
        ]

    def _create_entity_container_yrs(self):
        EntityContainerYearFactory(learning_container_year=self.lbir1200_current,
                                   entity=self.agro_entity,
                                   type=entity_types.ALLOCATION_ENTITY)
        EntityContainerYearFactory(learning_container_year=self.lbir1300_current,
                                   entity=self.agro_entity,
                                   type=entity_types.ALLOCATION_ENTITY)
        EntityContainerYearFactory(learning_container_year=self.lbir1200_next,
                                   entity=self.agro_entity,
                                   type=entity_types.ALLOCATION_ENTITY)
        EntityContainerYearFactory(learning_container_year=self.lbir1300_next,
                                   entity=self.agro_entity,
                                   type=entity_types.ALLOCATION_ENTITY)
        EntityContainerYearFactory(learning_container_year=self.lagro1600_next,
                                   entity=self.agro_entity,
                                   type=entity_types.ALLOCATION_ENTITY)
        EntityContainerYearFactory(learning_container_year=self.lagro2500_next,
                                   entity=self.agro_entity,
                                   type=entity_types.ALLOCATION_ENTITY)
        EntityContainerYearFactory(learning_container_year=self.ldroi1500_current,
                                   entity=self.drt_entity)


def _create_learning_container_with_components(acronym, academic_year, volume_lecturing=None,
                                               volume_practical_exercices=None,
                                               subtype=learning_unit_year_subtypes.FULL,
                                               type_declaration_vacant=vacant_declaration_type.RESEVED_FOR_INTERNS):
    l_container = LearningContainerYearFactory(acronym=acronym, academic_year=academic_year,
                                               type_declaration_vacant=type_declaration_vacant)
    return _link_components_and_learning_unit_year_to_container(l_container, l_container.acronym,
                                                                volume_lecturing, volume_practical_exercices, subtype)


def _link_components_and_learning_unit_year_to_container(l_container, acronym,
                                                         volume_lecturing=None,
                                                         volume_practical_exercices=None,
                                                         subtype=learning_unit_year_subtypes.FULL):
    a_learning_unit_year = LearningUnitYearFactory(acronym=acronym, academic_year=l_container.academic_year,
                                                   specific_title=l_container.common_title, subtype=subtype,
                                                   learning_container_year=l_container)
    if volume_lecturing:
        a_component = LearningComponentYearFactory(
            learning_container_year=l_container,
            type=learning_component_year_type.LECTURING,
            volume_declared_vacant=volume_lecturing
        )
        LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year, learning_component_year=a_component,
                                     type=component_type.LECTURING)
    if volume_practical_exercices:
        a_component = LearningComponentYearFactory(
            learning_container_year=l_container,
            type=learning_component_year_type.PRACTICAL_EXERCISES,
            volume_declared_vacant=volume_practical_exercices
        )
        LearningUnitComponentFactory(learning_unit_year=a_learning_unit_year, learning_component_year=a_component,
                                     type=component_type.PRACTICAL_EXERCISES)
    return l_container


def _get_application_example(learning_container_year, volume_lecturing, volume_practical_exercice, flag=None):
    return {
        'remark': 'This is the remarks',
        'course_summary': 'This is the course summary',
        'charge_lecturing_asked': volume_lecturing,
        'charge_practical_asked': volume_practical_exercice,
        'acronym': learning_container_year.acronym,
        'year': learning_container_year.academic_year.year,
        'pending': flag
    }


def _get_attribution_example(learning_container_year, volume_lecturing, volume_practical_exercice,
                             start_year, end_year):
    return {
        'acronym': learning_container_year.acronym,
        'title': learning_container_year.common_title,
        'year': learning_container_year.academic_year.year,
        learning_component_year_type.LECTURING: volume_lecturing,
        learning_component_year_type.PRACTICAL_EXERCISES: volume_practical_exercice,
        'start_year': start_year,
        'end_year': end_year,
        'function': function.HOLDER,
        'is_substitute': False
    }


def get_permission(codename):
    return Permission.objects.filter(codename=codename).first()


def add_permission(user, codename):
    perm = get_permission(codename)
    user.user_permissions.add(perm)
