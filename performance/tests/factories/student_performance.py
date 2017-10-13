##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import factory
import factory.fuzzy
import string
import operator
import json
import datetime
import pytz

from performance.models.enums import offer_registration_state as registration_state, session_month


def load_sample_student_performance():
    sample_path = "performance/tests/ressources/points.json"
    with open(sample_path) as file_sample:
        return json.load(file_sample)


class StudentPerformanceFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'performance.StudentPerformance'

    registration_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    academic_year = datetime.datetime.today().year
    acronym = factory.fuzzy.FuzzyText(length=15, chars=string.ascii_letters)
    data = load_sample_student_performance()
    update_date = datetime.datetime.now(tz=pytz.utc) + datetime.timedelta(days=1)
    creation_date = datetime.datetime.now(tz=pytz.utc)
    authorized = True
    offer_registration_state = registration_state.CESSATION
    session_locked = factory.Iterator(session_month.SESSION_MONTHS, getter=operator.itemgetter(0))
