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
from dissertation.tests.factories.adviser import AdviserManagerFactory, AdviserTeacherFactory
from dissertation.tests.factories.dissertation import DissertationFactory
from dissertation.tests.factories.offer_proposition import OfferPropositionFactory
from dissertation.tests.factories.proposition_dissertation import PropositionDissertationFactory
from osis_common.models import message_history
from osis_common.models import message_template

ERROR_405_BAD_REQUEST = 405
ERROR_404_PAGE_NO_FOUND = 404
HTTP_OK = 200
ERROR_403_NOT_AUTORIZED = 403
MAXIMUM_IN_REQUEST = 50


class DissertationViewTestCase(TestCase):
    fixtures = ['dissertation/fixtures/message_template.json', ]

    def setUp(self):
        self.maxDiff = None
        self.manager = AdviserManagerFactory()
        a_person_teacher = PersonFactory.create(first_name='Pierre',
                                                last_name='Dupont',
                                                email='laurent.dermine@uclouvain.be')
        self.teacher = AdviserTeacherFactory(person=a_person_teacher)
        a_person_teacher2 = PersonFactory.create(first_name='Marco',
                                                 last_name='Millet',
                                                 email='laurent.dermine@uclouvain.be')
        self.teacher2 = AdviserTeacherFactory(person=a_person_teacher2)
        a_person_student = PersonFactory.create(last_name="Durant",
                                                user=None,
                                                email='laurent.dermine@uclouvain.be')
        self.student = StudentFactory.create(person=a_person_student)
        self.offer1 = OfferFactory(title="test_offer1")
        self.offer2 = OfferFactory(title="test_offer2")
        self.academic_year1 = AcademicYearFactory()
        self.academic_year2 = AcademicYearFactory(year=self.academic_year1.year - 1)
        self.offer_year_start1 = OfferYearFactory(acronym="test_offer1", offer=self.offer1,
                                                  academic_year=self.academic_year1)
        self.offer_proposition1 = OfferPropositionFactory(offer=self.offer1, global_email_to_commission=True)
        self.offer_proposition2 = OfferPropositionFactory(offer=self.offer2, global_email_to_commission=False)
        self.proposition_dissertation = PropositionDissertationFactory(author=self.teacher,
                                                                       creator=a_person_teacher,
                                                                       title='Proposition 1212121'
                                                                       )



    def test_email_new_dissert(self):
        self.dissertation_test_email = DissertationFactory(author=self.student,
                                                           title='Dissertation_test_email',
                                                           offer_year_start=self.offer_year_start1,
                                                           proposition_dissertation=self.proposition_dissertation,
                                                           status='DRAFT',
                                                           active=True,
                                                           dissertation_role__adviser=self.teacher,
                                                           dissertation_role__status='PROMOTEUR'
                                                           )
        self.client.force_login(self.manager.person.user)
        count_messages_before_status_change = len(message_history.find_my_messages(self.teacher.person.id))
        self.dissertation_test_email.go_forward()
        message_history_result = message_history.find_my_messages(self.teacher.person.id)
        self.assertEqual(count_messages_before_status_change + 1, len(message_history_result))
        self.assertNotEqual(
            message_template.find_by_reference('dissertation_adviser_new_project_dissertation_txt'),
            None)
        self.assertNotEqual(
            message_template.find_by_reference('dissertation_adviser_new_project_dissertation_html'),
            None)
        assert 'Vous avez reçu une demande d\'encadrement de mémoire' in message_history_result.last().subject


