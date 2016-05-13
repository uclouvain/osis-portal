##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
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
from admission import models as mdl
from django.shortcuts import render, get_object_or_404
from reference import models as mdl_reference

from datetime import datetime
from admission.views.common import home
from functools import cmp_to_key
import locale
from django.utils.translation import ugettext_lazy as _
import string


ALERT_MANDATORY_FIELD = _('champ_obligatoire')


def read(request):
    secondary_education = mdl.secondary_education.find_by_person(request.user)
    first_academic_year_for_cv = None
    curricula = None
    if secondary_education:
        first_academic_year_for_cv = secondary_education.academic_year
    # find existing cv
    # add cv empty cv's for the year if it's needed
    path_types = None
    education_types = None
    local_universities = None
    domains = mdl.domain.find_all()
    grade_types = mdl.grade_type.find_all()
    return render(request, "curriculum.html", {"application": application,
                                               "curricula": curricula,
                                               "path_types":  path_types,
                                               "education_types" : education_types,
                                               "local_universities": local_universities,
                                               "domains": domains,
                                               "grade_types": grade_types })


def save(request):
    next_step = False
    previous_step = False
    save_step = False
    validation_messages = {}
    if request.POST:
        if 'bt_next_step_up' in request.POST or 'bt_next_step_down' in request.POST:
            next_step = True
        else:
            if 'bt_previous_step_up' in request.POST or 'bt_previous_step_down' in request.POST:
                previous_step = True
            else:
                if 'bt_save_up' in request.POST or 'bt_save_down' in request.POST:
                    save_step = True

    if previous_step:
        return home(request)

    is_valid = True
    message_success = None
    if save_step or next_step:
        is_valid, validation_messages, curricula = validate_fields_form(request)
        if is_valid:
            message_success = _('msg_info_saved')
            for curriculum in curricula:
                curriculum.save()
    #Get the data in bd
    a_person = mdl.person.find_by_user(request.user)
    first_academic_year_for_cv = None
    curricula = []
    message = None
    # find existing cv
    secondary_education = mdl.secondary_education.find_by_person(a_person)
    if secondary_education:
        if secondary_education.academic_year is None:
            message ="Vous ne pouvez pas encoder d'études supérieures sans avoir réussit vos études secondaires"
        else:
            first_academic_year_for_cv = secondary_education.academic_year.year + 1
    current_academic_year = mdl.academic_year.current_academic_year().year
    year = first_academic_year_for_cv
    while year < current_academic_year:
        academic_year = mdl.academic_year.find_by_year(year)
        curriculum = mdl.curriculum.find_one_by_academic_year(academic_year)
        if curriculum is None:
            # add cv empty cv's for the year if it's needed
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = a_person
            curriculum.academic_year = academic_year
        curricula.append(curriculum)
        year = year + 1

    local_universities_french = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', False, 'FRENCH')
    local_universities_dutch = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', False, 'DUTCH')

    return render(request, "curriculum.html", {"curricula":                 curricula,
                                                       "local_universities_french": local_universities_french,
                                                       "local_universities_dutch":  local_universities_dutch,
                                                       "domains":                   mdl.domain.find_all(),
                                                       "grade_types":               mdl.grade_type.find_all(),
                                                       "validation_messages" :validation_messages,
                                                       "message_success": message_success})


def update(request):
    curricula = []
    message = None
    a_person = mdl.person.find_by_user(request.user)
    secondary_education = mdl.secondary_education.find_by_person(a_person)
    current_academic_year = mdl.academic_year.current_academic_year().year
    admission = is_admission(a_person, secondary_education)

    year = current_academic_year - 5
    if admission:
        if secondary_education.secondary_education_diploma is True:
            year = secondary_education.academic_year.year + 1

    while year < current_academic_year:
        academic_year = mdl.academic_year.find_by_year(year)
        # find existing cv
        curriculum = mdl.curriculum.find_one_by_academic_year(academic_year)
        if curriculum is None:
            # add cv empty cv's for the year if it's needed
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = a_person
            curriculum.academic_year = academic_year
        curricula.append(curriculum)
        year = year + 1

    local_universities_french = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', False, 'FRENCH')
    local_universities_dutch = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', False, 'DUTCH')
    if message:
        return home(request)
    else:
        return render(request, "curriculum.html", {"curricula":                 curricula,
                                                   "local_universities_french": local_universities_french,
                                                   "local_universities_dutch":  local_universities_dutch,
                                                   "domains":                   mdl.domain.find_all(),
                                                   "grade_types":               mdl.grade_type.find_all()})


def validate_fields_form(request):
    is_valid = True
    curricula = []
    validation_messages = {}
    a_person = mdl.person.find_by_user(request.user)
    names = [v for k, v in request.POST.items() if k.startswith('curriculum_year_')]

    for curriculum_form in names:
        curriculum_year = curriculum_form.replace('curriculum_year_', '')
        academic_year = mdl.academic_year.find_by_year(curriculum_year)
        curriculum = mdl.curriculum.find_by_person_year(a_person, int(curriculum_year))
        if curriculum is None:
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = a_person
            curriculum.academic_year = academic_year
        if request.POST.get('path_type_%s' % curriculum_year) is None:
            validation_messages['path_type_%s' % curriculum_year] = ALERT_MANDATORY_FIELD
            is_valid = False
        else:
            curriculum.path_type = request.POST.get('path_type_%s' % curriculum_year)

        curricula.append(curriculum)

    return is_valid, validation_messages, curricula


def is_admission(a_person, secondary_education):
    if a_person.nationality.european_union:
        if secondary_education.national is True:
            return False
    return True
