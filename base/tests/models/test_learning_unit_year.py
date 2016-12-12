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
from base import models as mdl_base


def create_learning_unit_year(data):
    learning_unit_year = mdl_base.learning_unit_year.LearningUnitYear()
    if 'acronym' in data:
        learning_unit_year.acronym = data['acronym']
    if 'title' in data:
        learning_unit_year.title = data['title']
    if 'academic_year' in data:
        learning_unit_year.academic_year = data['academic_year']
    if 'weight' in data:
        learning_unit_year.weight = data['weight']
    if 'learning_unit' in data:
        learning_unit_year.learning_unit = data['learning_unit']
    learning_unit_year.save()
    return learning_unit_year
