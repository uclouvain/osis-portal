##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import string

import factory.fuzzy

from base.tests.factories.student import StudentFactory
from base.models.enums import peps_type


class StudentSpecificProlileFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'base.StudentSpecificProfile'

    student = factory.SubFactory(StudentFactory)
    type = peps_type.PepsTypes.ARTIST
    subtype_disability = ''
    subtype_sport= ''
    guide = None
    arrangement_additional_time = False
    arrangement_appropriate_copy = False
    arrangement_other = False
    arrangement_specific_locale = False
    arrangement_comment = None
