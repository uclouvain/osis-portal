##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
import factory


class CountryFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'reference.Country'

    external_id = factory.Faker('text', max_nb_chars=100)
    iso_code = factory.Sequence(lambda n: str(n)[-2:])
    name = factory.Sequence(lambda n: 'Country - %d' % n)
    nationality = factory.Faker('text', max_nb_chars=80)
    european_union = factory.Faker('boolean', chance_of_getting_true=50)
    dialing_code = factory.Faker('random_element', elements=('+32', '+33', '+1'))
    cref_code = factory.Faker('random_element', elements=('ABC', 'D3F', 'K-M'))
