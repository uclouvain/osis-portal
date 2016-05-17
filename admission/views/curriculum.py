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

    message_success = None
    if save_step or next_step:
        is_valid, validation_messages, curricula = validate_fields_form(request)
        if is_valid:
            message_success = _('msg_info_saved')
            for curriculum in curricula:
                curriculum.save()


    #Get the data in bd for dropdown list
    local_universities_french = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'FRENCH', False)

    local_universities_dutch = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'DUTCH', False)

    return render(request, "curriculum.html", {"curricula":                 curricula,
                                               "local_universities_french": local_universities_french,
                                               "local_universities_dutch":  local_universities_dutch,
                                               "domains":                   mdl.domain.find_all(),
                                               "grade_types":               mdl.grade_type.find_all(),
                                               "validation_messages":       validation_messages,
                                               "message_success":           message_success})


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
        .find_by_institution_type_national_community('UNIVERSITY', 'FRENCH', False)

    local_universities_dutch = mdl_reference.education_institution\
        .find_by_institution_type_national_community('UNIVERSITY', 'DUTCH', False)
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
    sorted(names, key=cmp_to_key(locale.strcoll))
    for curriculum_form in names:
        print('curricululm',curriculum_form)
        curriculum_year = curriculum_form.replace('curriculum_year_', '')
        academic_year = mdl.academic_year.find_by_year(curriculum_year)
        curriculum = mdl.curriculum.find_by_person_year(a_person, int(curriculum_year))

        if curriculum is None:
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = a_person
            curriculum.academic_year = academic_year
        #default
        curriculum.path_type = None
        curriculum.national_education = None
        curriculum.language = None
        curriculum.national_institution = None
        curriculum.domain = None
        curriculum.grade_type = None
        curriculum.result = None
        curriculum.credits_enrolled = None
        curriculum.credits_obtained = None
        curriculum.diploma = False
        curriculum.diploma_title = None
        curriculum.activity_type = None
        curriculum.activity = None
        curriculum.activity_place = None
        #
        if request.POST.get('path_type_%s' % curriculum_year) is None:
            validation_messages['path_type_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.path_type = request.POST.get('path_type_%s' % curriculum_year)
            if curriculum.path_type == 'LOCAL_UNIVERSITY' or curriculum.path_type == 'LOCAL_HIGH_EDUCATION':
                is_valid, validation_messages, curriculum = validate_belgian_fields_form(request,
                                                                                         curriculum,
                                                                                         curriculum_year,
                                                                                         validation_messages,
                                                                                         is_valid)

        curricula.append(curriculum)

    return is_valid, validation_messages, curricula


def is_admission(a_person, secondary_education):
    if a_person.nationality.european_union:
        if secondary_education.national is True:
            return False
    return True


def validate_belgian_fields_form(request, curriculum, curriculum_year, validation_messages, is_valid):
    if request.POST.get('national_education_%s' % curriculum_year) is None:
        validation_messages['national_education_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        curriculum.national_education = request.POST.get('national_education_%s' % curriculum_year)
        if curriculum.national_education == 'FRENCH':
            curriculum.language = mdl_reference.language.find_by_code('fr')
            if request.POST.get('national_institution_french_%s' % curriculum_year) is None \
                    or request.POST.get('national_institution_french_%s' % curriculum_year) == '-':
                validation_messages['national_institution_french_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                national_institution = mdl_reference.education_institution\
                    .find_by_id(int(request.POST.get('national_institution_french_%s' % curriculum_year)))
                curriculum.national_institution = national_institution
        else:
            if curriculum.national_education == 'DUTCH':
                curriculum.language = mdl_reference.language.find_by_code('nl')
                if request.POST.get('national_institution_dutch_%s' % curriculum_year) is None \
                        or request.POST.get('national_institution_dutch_%s' % curriculum_year) == '-':
                    validation_messages['national_institution_dutch_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    national_institution = mdl_reference.education_institution\
                        .find_by_id(int(request.POST.get('national_institution_dutch_%s' % curriculum_year)))
                    curriculum.national_institution = national_institution

    if request.POST.get('domain_%s' % curriculum_year) is None \
            or request.POST.get('domain_%s' % curriculum_year) == '-':
        validation_messages['domain_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        domain = mdl.domain.find_by_id(int(request.POST.get('domain_%s' % curriculum_year)))
        curriculum.domain = domain

    if request.POST.get('grade_type_%s' % curriculum_year) is None \
            or request.POST.get('grade_type_%s' % curriculum_year) == '-':
        validation_messages['grade_type_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        grade_type = mdl.grade_type.find_by_id(int(request.POST.get('grade_type_%s' % curriculum_year)))
        curriculum.grade_type = grade_type

    if request.POST.get('diploma_%s' % curriculum_year) is None:
        validation_messages['diploma_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        if request.POST.get('diploma_%s' % curriculum_year) == "true":
            curriculum.diploma = True

    if request.POST.get('result_%s' % curriculum_year) is None \
            and ((curriculum.academic_year.year < 2014) or (curriculum.academic_year.year >= 2014 and curriculum.diploma)):
        validation_messages['result_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        curriculum.result = request.POST.get('result_%s' % curriculum_year)

    if curriculum.academic_year.year >= 2014:
        print('ici',request.POST.get('credits_enrolled_%s' % curriculum_year))
        if request.POST.get('credits_enrolled_%s' % curriculum_year) is None \
                or len(request.POST.get('credits_enrolled_%s' % curriculum_year)) == 0:
            validation_messages['credits_enrolled_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
    if request.POST.get('credits_enrolled_%s' % curriculum_year) \
            and len(request.POST.get('credits_enrolled_%s' % curriculum_year)) > 0:
            try:
                credits = float(request.POST.get('credits_enrolled_%s' % curriculum_year)\
                            .strip().replace(',', '.'))
                curriculum.credits_enrolled = credits
                if credits > 75:
                    validation_messages['credits_enrolled_%s' % curriculum_year] = _('credits_too_high')
                    is_valid = False
                else:
                    if credits < 0:
                        validation_messages['credits_enrolled_%s' % curriculum_year] = _('credits_negative')
                        is_valid = False
            except ValueError:
                validation_messages['credits_enrolled_%s' % curriculum_year] = _('numeric_field')
                is_valid = False

    if curriculum.academic_year.year >= 2014:
        if request.POST.get('credits_obtained_%s' % curriculum_year) is None \
                or len(request.POST.get('credits_obtained_%s' % curriculum_year)) == 0:
            validation_messages['credits_obtained_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
    if request.POST.get('credits_obtained_%s' % curriculum_year) \
            and len(request.POST.get('credits_obtained_%s' % curriculum_year)) > 0:
            try:
                credits = float(request.POST.get('credits_obtained_%s' % curriculum_year)
                            .strip().replace(',', '.'))

                curriculum.credits_obtained = credits
                if credits > 75:
                    validation_messages['credits_obtained_%s' % curriculum_year] = _('credits_too_high')
                    is_valid = False
                else:
                    if credits < 0:
                        validation_messages['credits_obtained_%s' % curriculum_year] = _('credits_negative')
                        is_valid = False
            except ValueError:
                validation_messages['credits_obtained_%s' % curriculum_year] = _('numeric_field')
                is_valid = False

    return is_valid, validation_messages, curriculum
