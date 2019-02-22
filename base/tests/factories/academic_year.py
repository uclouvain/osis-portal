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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import string

import factory.fuzzy
from django.utils import timezone


def get_current_year():
    now = datetime.datetime.now()
    ref_date = datetime.datetime(now.year, 9, 15)
    if now < ref_date:
        start_date = datetime.date(now.year - 1, 9, 15)
    else:
        start_date = datetime.date(now.year, 9, 15)
    return start_date.year


class AcademicYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.AcademicYear"

    external_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    year = factory.fuzzy.FuzzyInteger(2000, timezone.now().year)
    start_date = factory.LazyAttribute(lambda obj: datetime.date(obj.year, 9, 15))
    end_date = factory.LazyAttribute(lambda obj: datetime.date(obj.year+1, 9, 30))

    class Params:
        current = factory.Trait(
            year=get_current_year()
        )


def create_current_academic_year():
    now = datetime.datetime.now()
    ref_date = datetime.datetime(now.year, 9, 15)
    if now < ref_date:
        start_date = datetime.date(now.year - 1, 9, 15)
    else:
        start_date = datetime.date(now.year, 9, 15)

    return AcademicYearFactory(
        year=start_date.year,
        start_date=start_date,
        end_date=datetime.date(start_date.year + 1, start_date.month, 30)
    )

def get_current_year():
    now = datetime.datetime.now()
    ref_date = datetime.datetime(now.year, 9, 15)
    if now < ref_date:
        start_date = datetime.date(now.year - 1, 9, 15)
    else:
        start_date = datetime.date(now.year, 9, 15)
    return start_date.year
