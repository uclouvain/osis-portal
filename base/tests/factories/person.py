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
import operator
import random

import factory
import factory.fuzzy
from django.conf import settings
from unidecode import unidecode

from base import models as mdl
from base.tests.factories.user import UserFactory


def generate_person_email(person, domain=None):
    if domain is None:
        domain = factory.Faker('domain_name').generate({})
    return '{0}.{1}@{2}'.format(unidecode(person.first_name), person.last_name.replace(' ', ''), domain).lower()


def generate_global_id() -> str:
    first_digit = str(random.randint(1, 9))
    other_digits = [str(random.randint(0, 9)) for _ in range(8)]
    return "".join([first_digit] + other_digits)


class PersonFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'base.Person'

    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    email = factory.LazyAttribute(generate_person_email)
    phone = factory.Faker('phone_number')
    language = settings.LANGUAGE_CODE
    gender = factory.Iterator(mdl.person.Person.GENDER_CHOICES, getter=operator.itemgetter(0))
    user = factory.SubFactory(UserFactory)
    global_id = factory.LazyFunction(generate_global_id)
