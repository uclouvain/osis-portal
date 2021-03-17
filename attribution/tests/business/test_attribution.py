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
from decimal import Decimal
from pprint import pprint

from django.contrib.auth.models import Group
from django.test import TestCase
from django.utils.translation import ugettext_lazy as _

from attribution.business import attribution
from attribution.tests.factories.attribution import AttributionNewFactory
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.enums import learning_component_year_type
from base.tests.factories.academic_year import AcademicYearFactory, create_current_academic_year
from base.tests.factories.learning_component_year import LearningComponentYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit_year import LearningUnitYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.tutor import TutorFactory


class AttributionTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Creation Person/Tutor
        Group.objects.create(name="tutors")
        cls.person = PersonFactory(global_id="98363454")
        TutorFactory(person=cls.person)

        _create_multiple_academic_year()
        cls.current_academic_year = current_academic_year()

        # Creation Json which will be store on attribution
        cls.attributions = _get_attributions_dict(cls.current_academic_year.year)

    def setUp(self):
        self.attrib = AttributionNewFactory(global_id=self.person.global_id,
                                            attributions=self.attributions)

    def test_get_attribution_list(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.current_academic_year)
        self.assertEqual(len(attribution_list), 3)

        previous_year = self.current_academic_year.year - 1
        academic_year_2016 = AcademicYear.objects.get(year=previous_year)
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            academic_year_2016)
        self.assertEqual(len(attribution_list), 1)

    def test_get_attribution_list_empty(self):
        academic_year = AcademicYearFactory(year=1990)
        attribution_list = attribution.get_attribution_list(self.person.global_id, academic_year)
        self.assertFalse(attribution_list)

    def test_get_attribution_order(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.current_academic_year)
        self.assertEqual(len(attribution_list), 3)
        self.assertEqual(attribution_list[0]['acronym'], "LAGRO1530")
        self.assertEqual(attribution_list[1]['acronym'], "LBIR1200")
        self.assertEqual(attribution_list[2]['acronym'], "LBIR1300")

    def test_computes_volumes_total(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.current_academic_year)
        volumes_total = attribution.get_volumes_total(attribution_list)
        self.assertTrue(volumes_total)
        self.assertEqual(volumes_total.get(learning_component_year_type.LECTURING), Decimal(53.5))
        self.assertEqual(volumes_total.get(learning_component_year_type.PRACTICAL_EXERCISES), Decimal(21.5))

    def test_append_team_and_volume_delcared_vacant(self):
        #  Create Container Year and component
        _create_learning_container_with_components(acronym="LBIR1300", academic_year=self.current_academic_year,
                                                   volume_lecturing=Decimal(15.5),
                                                   volume_practical_exercices=Decimal(5))
        _create_learning_container_with_components(acronym="LBIR1200", academic_year=self.current_academic_year,
                                                   volume_lecturing=Decimal(30),
                                                   volume_practical_exercices=Decimal(75))
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))

        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.current_academic_year)
        self.assertEqual(attribution_list[0]['acronym'], "LAGRO1530")
        self.assertEqual(attribution_list[0]['volume_lecturing_vacant'], Decimal(30))
        self.assertEqual(attribution_list[0]['volume_practical_exercices_vacant'], Decimal(30))
        self.assertEqual(attribution_list[0]['team'], False)
        self.assertEqual(attribution_list[1]['acronym'], "LBIR1200")
        self.assertEqual(attribution_list[1]['volume_lecturing_vacant'], Decimal(30))
        self.assertEqual(attribution_list[1]['volume_practical_exercices_vacant'], Decimal(75))
        self.assertEqual(attribution_list[1]['team'], False)
        self.assertEqual(attribution_list[2]['acronym'], "LBIR1300")
        self.assertEqual(attribution_list[2]['volume_lecturing_vacant'], Decimal(15.5))
        self.assertEqual(attribution_list[2]['volume_practical_exercices_vacant'], Decimal(5))
        self.assertEqual(attribution_list[2]['team'], False)

    def test_append_start_end_academic_year(self):
        attribution_list = attribution.get_attribution_list(self.person.global_id,
                                                            self.current_academic_year)

        self.assertEqual(attribution_list[0]['acronym'], "LAGRO1530")
        self.assertEqual(attribution_list[0]['start_academic_year'].year, self.current_academic_year.year-2)
        self.assertEqual(attribution_list[0]['end_academic_year'].year, self.current_academic_year.year)

        self.assertEqual(attribution_list[1]['acronym'], "LBIR1200")
        self.assertEqual(attribution_list[1]['start_academic_year'].year, self.current_academic_year.year-1)
        self.assertRaises(KeyError, lambda: attribution_list[1]['end_academic_year'])  # No end year

        self.assertEqual(attribution_list[2]['acronym'], "LBIR1300")
        self.assertEqual(attribution_list[2]['start_academic_year'].year, self.current_academic_year.year-2)
        self.assertEqual(attribution_list[2]['end_academic_year'].year, self.current_academic_year.year + 1)

    def test_get_attribution_list_about_to_expire(self):
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        _create_learning_container_with_components("LAGRO1530", next_academic_year, Decimal(30), Decimal(30))
        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(self.person.global_id,
                                                                                             self.current_academic_year)
        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertTrue(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertIsNone(attribution_list_about_to_expired[0]['not_renewable_reason'])

    def test_get_attribution_list_about_to_expire_volume_pratical_lower(self):
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        _create_learning_container_with_components("LAGRO1530", next_academic_year, Decimal(1), Decimal(30))
        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(self.person.global_id,
                                                                                             self.current_academic_year)
        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertFalse(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertEqual(attribution_list_about_to_expired[0]['not_renewable_reason'],
                         _("The vacant volume of the next academic year is lower than the current one"))

    def test_get_attribution_list_about_to_expire_volume_lecturing__lower(self):
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        _create_learning_container_with_components("LAGRO1530", next_academic_year, Decimal(30), Decimal(1))
        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(self.person.global_id,
                                                                                             self.current_academic_year)
        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertFalse(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertEqual(attribution_list_about_to_expired[0]['not_renewable_reason'],
                         _("The vacant volume of the next academic year is lower than the current one"))

    def test_get_attribution_list_about_to_expire_volume_zero_is_renewable(self):
        self.attrib.attributions = [
            {
                'year': self.current_academic_year.year, 'acronym': 'LAGRO1530', 'title': 'Agrochimie élémentaire',
                'weight': '5.00',
                'LECTURING': '0', 'PRACTICAL_EXERCISES': '0', 'function': 'HOLDER', 'start_year': 2015,
                'end_year': self.current_academic_year.year, 'is_substitute': False
            }
        ]
        self.attrib.save()
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        _create_learning_container_with_components("LAGRO1530", next_academic_year, Decimal(30), Decimal(30))
        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(self.person.global_id,
                                                                                             self.current_academic_year)
        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertTrue(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertEqual(attribution_list_about_to_expired[0]['not_renewable_reason'], None)

    def test_get_attribution_list_with_substitute_is_not_renewable(self):
        self.attrib.attributions = [
            {
                'year': self.current_academic_year.year, 'acronym': 'LAGRO1530', 'title': 'Agrochimie élémentaire',
                'weight': '5.00',
                'LECTURING': '0', 'PRACTICAL_EXERCISES': '0', 'function': 'HOLDER', 'start_year': 2015,
                'end_year': self.current_academic_year.year, 'is_substitute': True
            }
        ]
        self.attrib.save()
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        _create_learning_container_with_components("LAGRO1530", next_academic_year, Decimal(30), Decimal(30))
        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(self.person.global_id,
                                                                                             self.current_academic_year)
        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertFalse(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertEqual(attribution_list_about_to_expired[0]['not_renewable_reason'],
                         _('A substitute can not renew his function of substitute'))

    def test_get_attribution_list_when_attribute_not_renewable_because_team(self):
        self.attrib.attributions = [
            {
                'year': self.current_academic_year.year, 'acronym': 'LAGRO1530', 'title': 'Agrochimie élémentaire',
                'weight': '5.00',
                'LECTURING': '0', 'PRACTICAL_EXERCISES': '0', 'function': 'HOLDER', 'start_year': 2015,
                'end_year': self.current_academic_year.year, 'is_substitute': False
            }
        ]
        self.attrib.save()
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        container_year = _create_learning_container_with_components(
            "LAGRO1530",
            next_academic_year,
            Decimal(30),
            Decimal(30)
        )
        container_year.team = True
        container_year.save()

        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(self.person.global_id,
                                                                                             self.current_academic_year)
        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertFalse(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertEqual(
            attribution_list_about_to_expired[0]['not_renewable_reason'],
            _('This course is team-managed. The application to this activity is based on a paper transmission.')
        )

    def test_get_attribution_list_about_to_expire_already_applied(self):
        _create_learning_container_with_components("LAGRO1530", self.current_academic_year, Decimal(30), Decimal(30))
        next_academic_year = AcademicYear.objects.get(year=self.current_academic_year.year + 1)
        _create_learning_container_with_components("LAGRO1530", next_academic_year, Decimal(30), Decimal(30))
        application = [{
            'remark': 'This is the remarks',
            'course_summary': 'This is the course summary',
            'charge_lecturing_asked': 30,
            'charge_practical_asked': 30,
            'acronym': "LAGRO1530",
            'year': self.current_academic_year.year,
            'is_substitute': False
        }]
        self.attrib.applications = application
        self.attrib.save()

        attribution_list_about_to_expired = attribution.get_attribution_list_about_to_expire(
            self.person.global_id, self.current_academic_year
        )

        self.assertEqual(len(attribution_list_about_to_expired), 1)
        self.assertFalse(attribution_list_about_to_expired[0]['is_renewable'])
        self.assertEqual(attribution_list_about_to_expired[0]['not_renewable_reason'],
                         _('An application has already been submitted'))

    def test_calculate_effective_volume(self):
        vol_tot = 10.0
        planned_classes = 2
        data = {'PLANNED_CLASSES': planned_classes, 'VOLUME_TOTAL': vol_tot}
        self.assertEqual(attribution._calculate_effective_volume(data), vol_tot * planned_classes)

    def test_calculate_effective_volume_incorrect(self):
        vol_tot = 10.0
        planned_classes = -1
        data = {'PLANNED_CLASSES': planned_classes, 'VOLUME_TOTAL': vol_tot}
        self.assertEqual(attribution._calculate_effective_volume(data), attribution.NO_CHARGE)

    def test_calculate_effective_volume_no_volume_provided(self):
        self.assertEqual(attribution._calculate_effective_volume({'PLANNED_CLASSES': 1}), attribution.NO_CHARGE)

    def test_calculate_effective_volume_case_negative_volume(self):
        vol_tot = -10.0
        planned_classes = 1
        data = {'PLANNED_CLASSES': planned_classes, 'VOLUME_TOTAL': vol_tot}
        self.assertEqual(attribution._calculate_effective_volume(data), attribution.NO_CHARGE)

    def test_get_teachers_parameter_none(self):
        self.assertIsNone(attribution.get_teachers(None, None))
        self.assertIsNone(attribution.get_teachers('LCHM1111', None))
        academic_year = AcademicYearFactory()
        self.assertIsNone(attribution.get_teachers(None, academic_year))

    def test_get_teachers_no_teacher_found(self):
        self.assertIsNone(attribution.get_teachers('LCHM1111', 2017))

    def test_get_2_teachers_in_order(self):
        acronym_LCHM1111 = 'LCHM1111'
        acronym_LDVLP2627 = 'LDVLP2627'
        acronym_LDROI1110 = 'LDROI1110'

        # Create first teacher with one attribution on LCHM1111 and others
        person_first_alphabetical_order = PersonFactory(global_id='12345678', last_name='Antonelli')
        attribution_teacher_1_LCHM1111 = {'year': 2017, 'acronym': acronym_LCHM1111}
        attributions_teacher1 = [
            attribution_teacher_1_LCHM1111,
            {'year': 2016, 'acronym': acronym_LDVLP2627},
            {'year': 2017, 'acronym': acronym_LDVLP2627},
            {'year': 2017, 'acronym': acronym_LDROI1110}
        ]

        AttributionNewFactory(global_id=person_first_alphabetical_order.global_id,
                              attributions=attributions_teacher1)
        # Create second teacher with one attribution on LCHM1111
        person_second_alphabetical_order = PersonFactory(global_id='987654321', last_name='Barnet')
        attribution_teacher_2_LCHM1111 = {'year': 2017, 'acronym': acronym_LCHM1111}
        attributions_teacher2 = [attribution_teacher_2_LCHM1111]
        AttributionNewFactory(global_id=person_second_alphabetical_order.global_id,
                              attributions=attributions_teacher2)
        #
        attributions_result = attribution.get_teachers(acronym_LCHM1111, 2017)
        self.assertEqual(len(attributions_result), 2)
        self.assertEqual(attributions_result[0][attribution.PERSON_KEY],
                         person_first_alphabetical_order)

    def test_update_learning_unit_volume_no_components(self):
        """When no components found on database, the key 'lecturing_vol' / 'practical_exercises_vol' is set to 0.0"""
        l_container = LearningContainerYearFactory(acronym='LAGRO1530', academic_year=self.current_academic_year)
        LearningUnitYearFactory(acronym='LAGRO1530',
                                academic_year=self.current_academic_year,
                                learning_container_year=l_container)
        an_attribution = {
            'year': 2017, 'acronym': 'LAGRO1530', 'title': 'Chimie complexe', 'weight': '5.00',
            'LECTURING': '22.5', 'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER',
            'start_year': 2015, 'end_year': 2020
        }

        attribution.update_learning_unit_volume(an_attribution, self.current_academic_year)
        self.assertEqual(an_attribution['lecturing_vol'], Decimal(0.0))
        self.assertEqual(an_attribution['practical_exercises_vol'], Decimal(0.0))

    def test_calculate_component_volume(self):
        an_attribution = {
            'year': 2017, 'acronym': 'LAGRO1530', 'title': 'Chimie complexe', 'weight': '5.00',
            'LECTURING': '22.5', 'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER', 'start_year': 2015,
            'end_year': 2020
        }
        l_component_lecturing = LearningComponentYearFactory(type=learning_component_year_type.LECTURING)
        l_component_other = LearningComponentYearFactory(type=None)
        components_computed = {
            l_component_lecturing: {
                'VOLUME_TOTAL': Decimal(15),
                'PLANNED_CLASSES': 5
            },
            l_component_other: {
                'VOLUME_TOTAL': Decimal(1),
                'PLANNED_CLASSES': 1
            }
        }
        attribution._calculate_component_volume(an_attribution, components_computed)
        self.assertEqual(an_attribution['lecturing_vol'], Decimal(75))  # VOLUME_TOTAL * PLANNED_CLASSES
        self.assertRaises(KeyError, lambda: an_attribution['practical_exercises_vol'])

    def test_get_attribution_vacant_none(self):
        learning_container_yr = LearningContainerYearFactory()
        self.assertIsNone(attribution.get_attribution_vacant(learning_container_yr))

    def test_format_no_volume(self):
        attributions_without_volume = [
            {'year': 2018, 'acronym': 'LBIR1200'}]
        attributions_formalized = attribution._format_str_volume_to_decimal(attributions_without_volume)
        self.assertEqual(attributions_formalized[0]['LECTURING'], 0.0)
        self.assertEqual(attributions_formalized[0]['PRACTICAL_EXERCISES'], 0.0)


def _create_multiple_academic_year():
    current_year = datetime.date.today().year
    for year in range(current_year-3, current_year+2):
        AcademicYearFactory(year=year)


def _create_learning_container_with_components(acronym, academic_year, volume_lecturing=None,
                                               volume_practical_exercices=None):
    l_container = LearningContainerYearFactory(acronym=acronym, academic_year=academic_year)
    a_learning_unit_year = LearningUnitYearFactory(acronym=acronym, academic_year=academic_year,
                                                   specific_title=l_container.common_title,
                                                   learning_container_year=l_container)
    if volume_lecturing:
        LearningComponentYearFactory(
            learning_unit_year=a_learning_unit_year,
            type=learning_component_year_type.LECTURING,
            volume_declared_vacant=volume_lecturing
        )

    if volume_practical_exercices:
        LearningComponentYearFactory(
            learning_unit_year=a_learning_unit_year,
            type=learning_component_year_type.PRACTICAL_EXERCISES,
            volume_declared_vacant=volume_practical_exercices
        )

    return l_container


def _get_attributions_dict(current_year):
    previous_year = current_year - 1
    future_year = current_year + 1
    return [
        {
            'year': previous_year, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00',
            'LECTURING': '22.5',
            'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER', 'start_year': previous_year, 'end_year': previous_year,
            'is_substitute': False
        },
        {
            'year': current_year, 'acronym': 'LBIR1300', 'title': 'Chimie complexe volume 2', 'weight': '7.50',
            'LECTURING': '12.5', 'PRACTICAL_EXERCISES': '9.5', 'function': 'HOLDER', 'start_year': previous_year-1,
            'end_year': future_year, 'is_substitute': False
        },
        {
            'year': current_year, 'acronym': 'LBIR1200', 'title': 'Chimie complexe', 'weight': '5.00',
            'LECTURING': '20.5',
            'PRACTICAL_EXERCISES': '7.0', 'function': 'CO-HOLDER', 'start_year': previous_year, 'is_substitute': False
        },
        {
            'year': current_year, 'acronym': 'LAGRO1530', 'title': 'Agrochimie élémentaire', 'weight': '5.00',
            'LECTURING': '20.5',
            'PRACTICAL_EXERCISES': '5.0', 'function': 'HOLDER', 'start_year': previous_year-1,
            'end_year': current_year, 'is_substitute': False
        }
    ]
