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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime

import factory.fuzzy
from factory.faker import faker

fake = faker.Faker()


class EnrollmentDictFactory(dict, factory.DictFactory):
    date_enrollment = datetime.date.today()
    enrollment_state = "ENROLLED"
    student_last_name = fake.last_name()
    student_first_name = fake.first_name()
    student_email = fake.email()
    student_registration_id = factory.fuzzy.FuzzyText(length=10)
    program = factory.fuzzy.FuzzyText(length=7)
    learning_unit_year = 2020
    learning_unit_acronym = f"{factory.fuzzy.FuzzyText(length=5)}{factory.fuzzy.FuzzyInteger(low=1000, high=2000)}"

    specific_profile = None
