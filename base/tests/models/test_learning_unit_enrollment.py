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


def create_learning_unit_enrollment(an_offer_enrollment, a_learning_unit_year):
    learning_unit_enrollment = mdl_base.learning_unit_enrollment.LearningUnitEnrollment()
    learning_unit_enrollment.offer_enrollment = an_offer_enrollment
    learning_unit_enrollment.learning_unit_year = a_learning_unit_year
    learning_unit_enrollment.date_enrollment = datetime.datetime.now()
    learning_unit_enrollment.save()
    return learning_unit_enrollment