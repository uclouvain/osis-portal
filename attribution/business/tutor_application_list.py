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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from base import models as mdl_base
from attribution import models as mdl_attribution


def get_application_list(global_id, academic_year=None):
    if not academic_year:
        academic_year = get_application_year()

    attrib = mdl_attribution.attribution_new.find_by_global_id(global_id)
    if attrib:
        return _filter_by_years(attrib.applications, academic_year.year)
    return None


def get_application_year():
    # Application year is always for next year
    return mdl_base.academic_year.find_next_academic_year()


def _filter_by_years(attribution_list, year):
    return [attribution for attribution in attribution_list if attribution.get('year') == year]