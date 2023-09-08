#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import List

from osis_reference_sdk.model.academic_calendar import AcademicCalendar

from base.models.person import Person
from reference.services.academic_calendar import AcademicCalendarService

REFERENCE_INSCRIPTION_AUX_COURS = 'COURSE_ENROLLMENT_SWITCHING_CALENDAR'


class PeriodeInscriptionAuxCoursService:
    @classmethod
    def get_annee(cls, person: 'Person') -> int:
        calendriers = AcademicCalendarService.get_academic_calendar_list(
            person,
            reference=REFERENCE_INSCRIPTION_AUX_COURS
        )['results']  # type: List[AcademicCalendar]
        today = datetime.date.today()
        return next(
            calendrier for calendrier in calendriers
            if calendrier.start_date <= today <= calendrier.end_date
        ).data_year
