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
import factory
import factory.fuzzy
import string

from base.tests.factories.academic_year import AcademicYearFactory
from base.tests.factories.learning_container_year import LearningContainerYearFactory
from base.tests.factories.learning_unit import LearningUnitFactory
from base.models.enums import learning_unit_year_subtypes


class LearningUnitYearFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = "base.LearningUnitYear"
        django_get_or_create = ('acronym', 'academic_year')

    external_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    acronym = factory.Sequence(lambda n: 'LFAC%04d' % n)
    specific_title = factory.Sequence(lambda n: 'Learning unit year - %d' % n)
    credits = 5
    weight = 5
    academic_year = factory.SubFactory(AcademicYearFactory)
    learning_unit = factory.SubFactory(LearningUnitFactory)
    learning_container_year = factory.SubFactory(LearningContainerYearFactory)
    subtype = learning_unit_year_subtypes.FULL
