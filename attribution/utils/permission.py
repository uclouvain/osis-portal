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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from base import models as mdl_base
from base.models.enums import academic_calendar_type
from attribution import models as mdl_attribution


def is_online_application_opened(user):
    return _is_academic_calendar_event_opened(academic_calendar_type.TEACHING_CHARGE_APPLICATION)


def _is_academic_calendar_event_opened(calendar_type):
    current_academic_year = mdl_base.academic_year.current_academic_year()
    if not current_academic_year:
        return False
    return mdl_base.academic_calendar.is_academic_calendar_opened(current_academic_year, calendar_type)


def is_summary_responsible(a_user):
    a_tutor = mdl_base.tutor.find_by_user(a_user)
    if a_tutor:
        return mdl_attribution.attribution.is_summary_responsible(a_tutor)
    return False
