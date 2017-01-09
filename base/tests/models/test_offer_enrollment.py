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

from base import models as mdl_base


def create_offer_enrollment(student, offer_year):
    offer_enrollment = mdl_base.offer_enrollment.OfferEnrollment(student=student, offer_year=offer_year,
                                                                 date_enrollment=datetime.date.today())
    offer_enrollment.save()
    return offer_enrollment


def create_offer_enrollment_with_academic_year(an_offer_year, a_student, an_academic_year):
    an_offer_enrollment = mdl_base.offer_enrollment.OfferEnrollment()
    an_offer_enrollment.student = a_student
    an_offer_enrollment.offer_year = an_offer_year
    an_offer_enrollment.academic_year = an_academic_year
    an_offer_enrollment.date_enrollment = datetime.datetime.now()
    an_offer_enrollment.save()

    return an_offer_enrollment