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
from admission import models as mdl


def create_curriculum(data):
    a_curriculum = mdl.curriculum.Curriculum()
    if data['applicant']:
        a_curriculum.person = data['applicant']

    if data['academic_year']:
        a_curriculum.academic_year = data['academic_year']

    if data['path_type']:
        a_curriculum.path_type = data['path_type']

    if data['national_education']:
        a_curriculum.national_education = data['national_education']

    if data['national_institution']:
        a_curriculum.national_institution = data['national_institution']

    a_curriculum.save()

    return a_curriculum
