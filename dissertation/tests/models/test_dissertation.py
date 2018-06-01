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
from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.person import PersonFactory
from base.tests.factories.offer import OfferFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from dissertation.models import dissertation

class DissertationModelTestCase(TestCase):
    def setUp(self):
        self.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory.create(first_name='Pierre',
                                                last_name='Dupont',
                                                email='laurent.dermine@uclouvain.be')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_student1 = PersonFactory.create(last_name="Durant",
                                                user=None,
                                                email='laurent.dermine@uclouvain.be')
        self.student1 = StudentFactory.create(person=a_person_student1)
        a_person_student2 = PersonFactory.create(last_name="Robert",
                                                user=None,
                                                email='laurent.dermine@uclouvain.be')
        self.student2 = StudentFactory.create(person=a_person_student2)
        self.offer1 = OfferFactory(title="test_offer1")
        self.academic_year2017 = AcademicYearFactory(year=2017)
        self.offer_year_start2017 = OfferYearFactory(acronym="test_offer1", offer=self.offer1,
                                                  academic_year=self.academic_year2017)
        self.academic_year2015 = AcademicYearFactory(year=2015)
        self.offer_year_start2015 = OfferYearFactory(acronym="test_offer1", offer=self.offer1,
                                                  academic_year=self.academic_year2015)

        self.offer_enrollment2017 = OfferEnrollmentFactory(offer_year= self.offer_year_start2017,
                                                           student= self.student1)
        self.offer_enrollment2015 = OfferEnrollmentFactory(offer_year=self.offer_year_start2015,
                                                           student=self.student2)
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       creator=a_person_teacher,
                                                                       title='Proposition de memoire'
                                                                       )

    def test_count_dissertations(self):
        self.client.force_login(self.manager.person.user)
        self.dissertation_test_count2015 = DissertationFactory(author=self.student1,
                                                               offer_year_start=self.offer_year_start2015,
                                                               proposition_dissertation=self.proposition_dissertation,
                                                               status='COM_SUBMIT',
                                                               active=True,
                                                               dissertation_role__adviser=self.teacher,
                                                               dissertation_role__status='PROMOTEUR')

        self.dissertation_test_count2017 = DissertationFactory(author=self.student2,
                                                               offer_year_start=self.offer_year_start2017,
                                                               proposition_dissertation=self.proposition_dissertation,
                                                               status='COM_SUBMIT',
                                                               active=True,
                                                               dissertation_role__adviser=self.teacher,
                                                               dissertation_role__status='PROMOTEUR')

        self.assertEqual(dissertation.count_by_proposition(self.proposition_dissertation),1)

