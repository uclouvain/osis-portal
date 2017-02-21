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
from attribution import models as mdl_attribution


def create_attribution(data):
    attribution = mdl_attribution.attribution.Attribution()
    start = None
    if 'start_year' in data:
        start = data['start_year']
    end = None
    if 'end_year' in data:
        end = data['end_year']
    if 'function' in data:
        attribution.function = data['function']
    if 'learning_unit_year' in data:
        attribution.learning_unit_year = data['learning_unit_year']
        year_yr = attribution.learning_unit_year.academic_year.year
        if start is None:
            attribution.start_year = year_yr
        if end is None:
            attribution.end_year = year_yr+1
    if start:
        attribution.start_year = start
    if end:
        attribution.end_year = end
    if 'tutor' in data:
        attribution.tutor = data['tutor']
    attribution.save()
    return attribution

