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
import datetime
from django.test import TestCase
from django.contrib.auth.models import Group

from base.models import offer as mdl_offer
from base.tests.factories.offer import OfferFactory
from base.tests.factories.student import StudentFactory
from base.tests.factories.offer_year import OfferYearFactory
from base.tests.factories.offer_enrollment import OfferEnrollmentFactory


now = datetime.datetime.now()


class TestOffer(TestCase):
    def setUp(self):
        self.offer = OfferFactory()
        self.title = self.offer.title

    def test_str(self):
        self.assertEqual(str(self.offer), "{}".format(self.title))

    def test_find_by_id(self):
        self.assertEqual(mdl_offer.find_by_id(self.offer.id),
                         self.offer)

    def test_find_by_student(self):
        Group.objects.create(name='students')
        a_student = StudentFactory()
        an_offer_year = OfferYearFactory(offer=self.offer)
        OfferEnrollmentFactory(offer_year=an_offer_year, student=a_student,date_enrollment=datetime.datetime(an_offer_year.academic_year.year+1, 2,1))

        self.assertListEqual(list(mdl_offer.find_by_student(a_student)),
                             [self.offer])


