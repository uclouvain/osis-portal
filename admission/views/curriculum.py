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
import locale
from functools import cmp_to_key

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from admission import models as mdl
from base import models as mdl_base
from admission.views import common
from reference import models as mdl_reference
from admission.views import demande_validation
from reference.enums import education_institution_type, education_institution_national_comunity as national_cmunity_type

CURRICULUM_YEARS_REQUIRED = 5
MAX_CREDITS = 75


def save(request):
    save_step = False
    duplicate = False
    duplicate_year_origin = None
    validation_messages = {}

    key = 'bt_duplicate_'
    for k, v in request.POST.items():
        if k.startswith(key):
            duplicate = True
            duplicate_year_origin = int(k.replace(key, ''))
            break
    if duplicate:
        pass
    else:
        save_step = True

    message_success = None
    # Get the data in bd for dropdown list
    local_universities_french = mdl_reference.education_institution \
        .find_by_institution_type_national_community(education_institution_type.UNIVERSITY,
                                                     national_cmunity_type.FRENCH,
                                                     False)

    local_universities_dutch = mdl_reference.education_institution \
        .find_by_institution_type_national_community(education_institution_type.UNIVERSITY,
                                                     national_cmunity_type.DUTCH,
                                                     False)
    universities_cities = []
    universities = []

    if save_step or duplicate:
        is_valid, validation_messages, curricula, universities_cities, universities, duplication_possible \
            = validate_fields_form(request, duplicate_year_origin)
        is_valid = True  # a modifier avec issue 180
        if is_valid:
            message_success = _('msg_info_saved')
            for curriculum in curricula:
                curriculum.save()
        else:
            return render(request, "admission_home.html",
                          {"curricula": curricula,
                           "local_universities_french": local_universities_french,
                           "local_universities_dutch": local_universities_dutch,
                           "domains": mdl_reference.domain.find_current_domains(),
                           "subdomains": mdl_reference.domain.find_all_subdomains(),
                           "grade_types": mdl_reference.grade_type.find_all(),
                           "validation_messages": validation_messages,
                           "message_success": message_success,
                           "universities_cities": universities_cities,
                           "universities": universities,
                           "languages": mdl_reference.language.find_languages(),
                           "current_academic_year": mdl_base.academic_year.current_academic_year(),
                           "tab_active": 3})

    # Get the data in bd
    applicant = mdl.applicant.find_by_user(request.user)
    first_academic_year_for_cv = None
    curricula = []
    # find existing cv
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    if secondary_education:
        if secondary_education.academic_year:
            first_academic_year_for_cv = secondary_education.academic_year + 1

    current_academic_year = mdl_base.academic_year.current_academic_year().year

    year = first_academic_year_for_cv
    if year:
        while year < current_academic_year:
            curriculum = mdl.curriculum.find_by_person_year(applicant, year)
            if curriculum is None:
                # add cv empty cv's for the year if it's needed
                curriculum = mdl.curriculum.Curriculum()
                curriculum.person = applicant
                curriculum.academic_year = year
            curricula.append(curriculum)
            year += 1

    return render(request, "admission_home.html",
                  {"curricula": curricula,
                   "local_universities_french": local_universities_french,
                   "local_universities_dutch": local_universities_dutch,
                   "domains": mdl_reference.domain.find_current_domains(),
                   "subdomains": mdl_reference.domain.find_all_subdomains(),
                   "grade_types": mdl_reference.grade_type.find_all(),
                   "universities_countries": mdl_reference.education_institution.find_countries(),
                   "validation_messages": validation_messages,
                   "message_success": message_success,
                   "universities_cities": universities_cities,
                   "universities": universities,
                   "languages": mdl_reference.language.find_languages(),
                   "current_academic_year": mdl_base.academic_year.current_academic_year(),
                   "tab_active": 3})


def update(request, application_id=None):
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    curricula = []
    message = None
    applicant = mdl.applicant.find_by_user(request.user)
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    current_academic_year = None
    if mdl_base.academic_year.current_academic_year():
        current_academic_year = mdl_base.academic_year.current_academic_year().year
    admission = is_admission(applicant, secondary_education)
    year_secondary = None
    year = None
    if current_academic_year:
        year = current_academic_year - CURRICULUM_YEARS_REQUIRED
    if secondary_education is None:
        pass
    else:
        if secondary_education and secondary_education.diploma is True and secondary_education.academic_year:
            year_secondary = secondary_education.academic_year

    if admission:
        if secondary_education and secondary_education.diploma is True and secondary_education.academic_year:
            year = secondary_education.academic_year + 1

    if year_secondary and year and year < year_secondary:
        year = year_secondary + 1
    if year and current_academic_year:
        while year < current_academic_year:
            # find existing cv
            curriculum = mdl.curriculum.find_by_person_year(applicant, year)
            if curriculum is None:
                # add cv empty cv's for the year if it's needed
                curriculum = mdl.curriculum.Curriculum()
                curriculum.person = applicant
                curriculum.academic_year = year
            curricula.append(curriculum)
            year = year + 1
    local_universities_french = mdl_reference.education_institution \
        .find_by_institution_type_national_community(education_institution_type.UNIVERSITY,
                                                     national_cmunity_type.FRENCH,
                                                     False)

    local_universities_dutch = mdl_reference.education_institution \
        .find_by_institution_type_national_community(education_institution_type.UNIVERSITY,
                                                     national_cmunity_type.DUTCH,
                                                     False)
    if message:
        return common.home(request)
    else:
        universities_cities, universities = populate_dropdown_list(curricula)

        data = {
            "curricula": curricula,
            "local_universities_french": local_universities_french,
            "local_universities_dutch": local_universities_dutch,
            "domains": mdl_reference.domain.find_current_domains(),
            "subdomains": mdl_reference.domain.find_all_subdomains(),
            "grade_types": mdl_reference.grade_type.find_all(),
            "universities_countries": mdl_reference.education_institution.find_countries(),
            "universities_cities": universities_cities,
            "universities": universities,
            "languages": mdl_reference.language.find_languages(),
            "current_academic_year": mdl_base.academic_year.current_academic_year(),
            "tab_active": 3,
            "application": application,
            'applications': mdl.application.find_by_user(request.user)
        }
        data.update(demande_validation.get_validation_status(application, applicant, request.user))
        return render(request, "admission_home.html", data)


def validate_fields_form(request, duplicate_year_origin):
    duplication_possible = True
    is_valid = True
    curricula = []
    universities_cities = []
    universities = []
    validation_messages = {}
    applicant = mdl.applicant.find_by_user(request.user)
    names = [v for k, v in request.POST.items() if k.startswith('curriculum_year_')]
    # to keep the order of the cv from the oldest to the more recent
    names = sorted(names, key=cmp_to_key(locale.strcoll))
    duplicate_year_destination = None
    if duplicate_year_origin:
        duplicate_year_destination = duplicate_year_origin + 1

    cpt = 0
    data_dict_to_duplicate = None
    for curriculum_form in names:
        curriculum_year = curriculum_form.replace('curriculum_year_', '')
        data_dict = data_dictionnary_building(request, curriculum_year)

        if duplicate_year_origin:
            # If duplication expected
            if int(curriculum_year) == duplicate_year_destination:
                data_dict = data_dict_to_duplicate.copy()
            if int(curriculum_year) == duplicate_year_origin:
                data_dict_to_duplicate = data_dict.copy()

        # No need to validate the curriculum of the year which is going to be duplicated
        curriculum = mdl.curriculum.find_by_person_year(applicant, int(curriculum_year))

        if not curriculum:
            curriculum = mdl.curriculum.Curriculum()
            curriculum.person = applicant
            curriculum.academic_year = curriculum_year
        # default
        curriculum.path_type = None
        curriculum.national_education = None
        curriculum.language = None
        curriculum.national_institution = None
        curriculum.domain = None
        curriculum.sub_domain = None
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
        if data_dict['path_type'] is None:
            validation_messages['path_type_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.path_type = data_dict['path_type']

            if curriculum.path_type == 'LOCAL_UNIVERSITY' or curriculum.path_type == 'LOCAL_HIGH_EDUCATION':
                is_valid, validation_messages, curriculum = validate_local_fields_form(curriculum,
                                                                                       curriculum_year,
                                                                                       validation_messages,
                                                                                       is_valid,
                                                                                       data_dict)
            else:
                if curriculum.path_type == 'FOREIGN_UNIVERSITY' or curriculum.path_type == 'FOREIGN_HIGH_EDUCATION':
                    is_valid, validation_messages, curriculum, universities_cities, universities, \
                        = validate_foreign_university_fields_form(curriculum,
                                                                  curriculum_year,
                                                                  validation_messages,
                                                                  is_valid,
                                                                  universities_cities,
                                                                  universities,
                                                                  data_dict)
                else:
                    if curriculum.path_type == 'ANOTHER_ACTIVITY':
                        is_valid, validation_messages, curriculum \
                            = validate_another_activity_fields_form(curriculum,
                                                                    curriculum_year,
                                                                    validation_messages,
                                                                    is_valid,
                                                                    data_dict)
            if duplicate_year_origin and int(curriculum_year) == duplicate_year_origin and not is_valid:
                duplication_possible = False
        curricula.append(curriculum)

        cpt = cpt + 1

    return is_valid, validation_messages, curricula, universities_cities, universities, duplication_possible


def is_admission(applicant, secondary_education):
    if applicant.nationality and applicant.nationality.european_union:
        if secondary_education and secondary_education.national is True:
            return False
    return True


def validate_local_fields_form(curriculum, curriculum_year, validation_messages, is_valid, data_dict):
    if curriculum.path_type == "LOCAL_UNIVERSITY":
        if data_dict['national_education'] is None:
            validation_messages['national_education_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.national_education = data_dict['national_education']
            if curriculum.national_education == 'FRENCH':
                curriculum.language = mdl_reference.language.find_by_code('fr')
                if data_dict['national_institution_french'] is None \
                        or data_dict['national_institution_french'] == '-':
                    validation_messages['national_institution_french_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    national_institution = mdl_reference.education_institution \
                        .find_by_id(int(data_dict['national_institution_french']))
                    curriculum.national_institution = national_institution
            else:
                if curriculum.national_education == 'DUTCH':
                    curriculum.language = mdl_reference.language.find_by_code('nl')
                    if data_dict['national_institution_dutch'] is None \
                            or data_dict['national_institution_dutch'] == '-':
                        validation_messages['national_institution_dutch_%s' % curriculum_year] = _('mandatory_field')
                        is_valid = False
                    else:
                        national_institution = mdl_reference.education_institution \
                            .find_by_id(int(data_dict['national_institution_dutch']))
                        curriculum.national_institution = national_institution
        if data_dict['domain'] is None \
                or data_dict['domain'] == '-':
            validation_messages['domain_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            domain = mdl_reference.domain.find_by_id(int(data_dict['domain']))
            curriculum.domain = domain
            if domain.sub_domains:
                if data_dict['subdomain'] is None \
                        or data_dict['subdomain'] == '-':
                    validation_messages['subdomain_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    sub_domain = mdl_reference.domain.find_by_id(int(data_dict['subdomain']))
                    curriculum.sub_domain = sub_domain

        if data_dict['corresponds_to_domain'] == "false":
            if data_dict['diploma_title'] is None \
                    or len(data_dict['diploma_title'].strip()) == 0:
                validation_messages['diploma_title_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
        if data_dict['grade_type'] is None \
                or data_dict['grade_type'] == '-':
            validation_messages['grade_type_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            grade_type = mdl_reference.grade_type.find_by_id(int(data_dict['grade_type']))
            curriculum.grade_type = grade_type
        if data_dict['result_national'] is None \
                and (curriculum.academic_year.year < 2014 or
                     (curriculum.academic_year.year >= 2014 and curriculum.diploma)):
            validation_messages['result_national_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.result = data_dict['result_national']

    if curriculum.path_type == "LOCAL_HIGH_EDUCATION":
        if data_dict['national_education']:
            curriculum.national_education = data_dict['national_education']

        if data_dict['other_school_high_non_university'] == "on":

            if data_dict['other_high_non_university_name'] is None \
                    or len(data_dict['other_high_non_university_name'].strip()) == 0:
                validation_messages['high_non_university_name_%s' % curriculum_year] = _('msg_school_name')
                is_valid = False
            else:
                national_institution = mdl_reference.education_institution.EducationInstitution()
                national_institution.adhoc = True
                national_institution.name = data_dict['other_high_non_university_name']
                national_institution.save()
                curriculum.national_institution = national_institution
        else:
            if data_dict['national_high_non_university_institution'] is None \
                    or data_dict['national_high_non_university_institution'] == "-":
                validation_messages['high_non_university_name_%s' % curriculum_year] = _('msg_school_name')
                is_valid = False
            else:
                national_institution = mdl_reference.education_institution \
                    .find_by_id(int(data_dict['national_high_non_university_institution']))
                curriculum.national_institution = national_institution
        if data_dict['domain_non_university'] is None \
                or data_dict['domain_non_university'] == '-':
            validation_messages['domain_non_university_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            domain = mdl_reference.domain.find_by_id(int(data_dict['domain_non_university']))
            curriculum.domain = domain
        if data_dict['grade_type_no_university'] is None \
                or data_dict['grade_type_no_university'] == '-':
            validation_messages['grade_type_no_university_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            curriculum.grade_type_no_university = data_dict['grade_type_no_university']

        if data_dict['study_systems'] and data_dict['study_systems'] != "-":
            curriculum.study_system = data_dict['study_systems']
        else:
            curriculum.study_system = None

        if data_dict['result_national'] \
                and data_dict['result_national'] != "-":
            curriculum.result = data_dict['result_national']
        else:
            curriculum.result = None
    # common fields for local university and no-university curriculum
    if data_dict['diploma_title'] and len(data_dict['diploma_title'].strip()) > 0:
        curriculum.diploma_title = data_dict['diploma_title']

    if data_dict['diploma'] is None:
        validation_messages['diploma_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        if data_dict['diploma'] == "true":
            curriculum.diploma = True

    if curriculum.academic_year.year >= 2014:
        if data_dict['credits_enrolled'] is None or len(data_dict['credits_enrolled']) == 0:
            validation_messages['credits_enrolled_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
            curriculum.credits_enrolled = None
    if data_dict['credits_enrolled'] and len(data_dict['credits_enrolled']) > 0:
        try:
            credits = float(data_dict['credits_enrolled'].strip().replace(',', '.'))
            curriculum.credits_enrolled = credits
            if credits > MAX_CREDITS:
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
        if data_dict['credits_obtained'] is None \
                or len(data_dict['credits_obtained']) == 0:
            validation_messages['credits_obtained_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
            curriculum.credits_obtained = None
    if data_dict['credits_obtained'] and len(data_dict['credits_obtained']) > 0:
        try:
            credits = float(data_dict['credits_obtained'].strip().replace(',', '.'))
            curriculum.credits_obtained = credits
            if credits > MAX_CREDITS:
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


def validate_foreign_university_fields_form(curriculum,
                                            curriculum_year,
                                            validation_messages,
                                            is_valid,
                                            universities_cities,
                                            universities,
                                            data_dict):
    cities_list = []
    universities_list = []
    national_institution = mdl_reference.education_institution.EducationInstitution()
    national_institution.adhoc = False

    if curriculum.path_type == 'FOREIGN_UNIVERSITY':
        if data_dict['foreign_institution_country'] is None \
                or data_dict['foreign_institution_country'] == "-":
            validation_messages['foreign_institution_country_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False
        else:
            country = mdl_reference.country.find_by_id(int(data_dict['foreign_institution_country']))
            universities_by_country = mdl_reference.education_institution.find_by_country(country)

            for university in universities_by_country:
                cities_list.append(university.city)

            national_institution.country = country
            if (data_dict['foreign_institution_city'] is None or data_dict['foreign_institution_city'] == "-") \
                    and data_dict['city_specify'] is None:
                validation_messages['foreign_institution_city_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                universities_by_city = mdl_reference.education_institution \
                    .find_by_city(data_dict['foreign_institution_city'])

                for university in universities_by_city:
                    universities_list.append(university)

                if data_dict['foreign_institution_city'] \
                        and data_dict['foreign_institution_city'] != "-":
                    national_institution.city = data_dict['foreign_institution_city']
                else:
                    national_institution.city = data_dict['city_specify']
                    national_institution.adhoc = True
                if (data_dict['foreign_institution_name'] is None or data_dict['foreign_institution_name'] == "-") \
                        and (data_dict['name_specify'] is None or len(data_dict['name_specify']) == 0):
                    validation_messages['foreign_institution_%s' % curriculum_year] = _('mandatory_university_name')
                    is_valid = False
                else:
                    if data_dict['foreign_institution_name'] and data_dict['foreign_institution_name'] != "-":
                        national_institution = mdl_reference.education_institution \
                            .find_by_id(int(data_dict['foreign_institution_name']))
                        national_institution = national_institution
                    else:
                        if data_dict['name_specify'] \
                                and len(data_dict['name_specify']) > 0:
                            national_institution.name = data_dict['name_specify']
                            national_institution.adhoc = True

        if national_institution.adhoc is True:
            national_institution.save()
        else:
            national_institution = mdl_reference.education_institution \
                .find_by_country_city_name(national_institution.country,
                                           national_institution.city,
                                           national_institution.name)

        curriculum.national_institution = national_institution

        universities_cities.append(cities_list)
        universities.append(universities_list)

    if curriculum.path_type == "FOREIGN_HIGH_EDUCATION":
        if data_dict['foreign_high_institution_name'] and data_dict['foreign_high_institution_name'] != "-":
            if (data_dict['national_institution_locality_adhoc'] is None or
                    data_dict['national_institution_locality_adhoc'] != "on") \
                        and (data_dict['national_institution_name_adhoc'] is None or
                             data_dict['national_institution_name_adhoc'] != "on"):

                n = mdl_reference.education_institution \
                    .find_by_id(int(data_dict['foreign_high_institution_name']))
                curriculum.national_institution = n
            else:
                national_institution = mdl_reference.education_institution.EducationInstitution()
                national_institution.adhoc = True
                if data_dict['national_institution_locality_adhoc'] == "on":
                    if data_dict['city_specify'] is None:
                        validation_messages['foreign_institution_city_%s' % curriculum_year] = _('mandatory_field')
                        is_valid = False
                    else:
                        national_institution.city = data_dict['city_specify']
                if data_dict['national_institution_name_adhoc'] == "on":
                    if data_dict['name_specify'] is None:
                        validation_messages['foreign_institution%s' % curriculum_year] = _('mandatory_field')
                        is_valid = False
                    else:
                        national_institution.name = data_dict['txt_name_specify']

                if data_dict['foreign_high_institution_country'] \
                        and data_dict['foreign_high_institution_country'] == "-":
                    validation_messages['foreign_institution_country_%s' % curriculum_year] = _('mandatory_field')
                    is_valid = False
                else:
                    national_institution.country = mdl_reference.country \
                        .find_by_id(int(data_dict['foreign_high_institution_country']))
                # to avoid duplication
                existing_national_institution = mdl_reference.education_institution \
                    .find_by_country_city_name(national_institution.country,
                                               national_institution.city,
                                               national_institution.name)
                if existing_national_institution:
                    curriculum.national_institution = existing_national_institution
                else:
                    curriculum.national_institution = national_institution
        else:
            validation_messages['foreign_institution_%s' % curriculum_year] = _('institution_mandatory')
            is_valid = False
        if curriculum.national_institution:
            if curriculum.national_institution.city:
                universities_by_city = mdl_reference.education_institution \
                    .find_by_city(curriculum.national_institution.city)
                for university in universities_by_city:
                    universities_list.append(university)

    if data_dict['domain_foreign'] is None \
            or data_dict['domain_foreign'] == '-':
        validation_messages['domain_foreign_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        domain = mdl_reference.domain.find_by_id(int(data_dict['domain_foreign']))
        curriculum.domain = domain
        if domain.sub_domains:
            if data_dict['subdomain_foreign'] is None \
                    or data_dict['subdomain_foreign'] == '-':
                validation_messages['subdomain_foreign_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                sub_domain = mdl_reference.domain.find_by_id(int(data_dict['subdomain_foreign']))
                curriculum.sub_domain = sub_domain

    if data_dict['grade_type_foreign'] is None \
            or data_dict['grade_type_foreign'] == '-':
        validation_messages['grade_type_foreign_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        grade_type = mdl_reference.grade_type.find_by_id(int(data_dict['grade_type_foreign']))
        curriculum.grade_type = grade_type

    if data_dict['diploma_title']:
        curriculum.diploma_title = data_dict['diploma_title']

    if data_dict['diploma_foreign'] is None:
        validation_messages['diploma_foreign_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        if data_dict['diploma_foreign'] == "true":
            curriculum.diploma = True

    if data_dict['result'] is None \
            and (curriculum.academic_year.year < 2014 or
                 (curriculum.academic_year.year >= 2014 and curriculum.diploma)):
        validation_messages['result_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        curriculum.result = data_dict['result']

    if data_dict['credits_enrolled_foreign'] and len(data_dict['credits_enrolled_foreign']) > 0:
        try:
            credits = float(data_dict['credits_enrolled_foreign'].strip().replace(',', '.'))
            curriculum.credits_enrolled = credits
            if credits > MAX_CREDITS:
                validation_messages['credits_enrolled_foreign_%s' % curriculum_year] = _('credits_too_high')
                is_valid = False
            else:
                if credits < 0:
                    validation_messages['credits_enrolled_foreign_%s' % curriculum_year] = _('credits_negative')
                    is_valid = False
        except ValueError:
            validation_messages['credits_enrolled_foreign_%s' % curriculum_year] = _('numeric_field')
            is_valid = False

    if data_dict['credits_obtained_foreign'] and len(data_dict['credits_obtained_foreign']) > 0:
        try:
            credits = float(data_dict['credits_obtained_foreign'].strip().replace(',', '.'))
            curriculum.credits_obtained = credits
            if credits > MAX_CREDITS:
                validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('credits_too_high')
                is_valid = False
            else:
                if credits < 0:
                    validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('credits_negative')
                    is_valid = False
        except ValueError:
            validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('numeric_field')
            is_valid = False
    if curriculum.path_type == "FOREIGN_HIGH_EDUCATION":
        if data_dict['linguistic_regime'] is None or data_dict['linguistic_regime'] == "-":
            validation_messages['credits_obtained_foreign_%s' % curriculum_year] = _('mandatory_field')
            is_valid = False

    if data_dict['linguistic_regime'] \
            and data_dict['linguistic_regime'] != "-":
        l = mdl_reference.language.find_by_id(int(data_dict['linguistic_regime']))
        curriculum.language = l

    return is_valid, validation_messages, curriculum, universities_cities, universities


def populate_dropdown_list(curricula):
    universities_cities = []
    universities = []
    for cv in curricula:
        cities_list = []
        universities_list = []
        if cv.national_institution:
            universities_by_city = mdl_reference.education_institution \
                .find_by_city_not_isocode(cv.national_institution.city, 'BE', 'UNIVERSITY')
            universities_by_country = mdl_reference.education_institution \
                .find_by_country(cv.national_institution.country)

            for university in universities_by_country:
                cities_list.append(university.city)

            universities_cities.append(cities_list)
            for university in universities_by_city:
                universities_list.append(university)
            universities.append(universities_list)
    return universities_cities, universities


def populate_dropdown_foreign_high_list(curricula):
    foreign_high_institution_countries = []
    foreign_high_institution_cities = []
    foreign_high_institutions = []
    for curriculum in curricula:
        cities_list = []
        institutions_list = []
        countries_list = []
        if curriculum.national_institution:
            institutions_by_city = mdl_reference.education_institution \
                .find_by_city_country(curriculum.national_institution.city, curriculum.national_institution.country)
            institution_by_country = mdl_reference.education_institution \
                .find_by_country(curriculum.national_institution.country)
            countries_list.append(curriculum.national_institution.country)
            foreign_high_institution_countries.append(countries_list)
            for institution in institution_by_country:
                cities_list.append(institution.city)

            foreign_high_institution_cities.append(cities_list)

            for institution in institutions_by_city:
                institutions_list.append(institution)
            foreign_high_institutions.append(institutions_list)

    return foreign_high_institution_countries, foreign_high_institution_cities, foreign_high_institutions


def validate_another_activity_fields_form(curriculum, curriculum_year, validation_messages, is_valid, data_dict):
    if data_dict['activity_type'] is None:
        validation_messages['activity_type_%s' % curriculum_year] = _('mandatory_field')
        is_valid = False
    else:
        curriculum.activity_type = data_dict['activity_type']
        if curriculum.activity_type == 'JOB' \
                or curriculum.activity_type == 'INTERNSHIP' \
                or curriculum.activity_type == 'VOLUNTEERING':

            if data_dict['activity'] is None \
                    or len(data_dict['activity']) == 0:
                validation_messages['activity_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                curriculum.activity = data_dict['activity']
            if data_dict['activity_place'] is None \
                    or len(data_dict['activity_place']) == 0:
                validation_messages['activity_place_%s' % curriculum_year] = _('mandatory_field')
                is_valid = False
            else:
                curriculum.activity_place = data_dict['activity_place']

    return is_valid, validation_messages, curriculum


def errors_update(request):
    return update(request)


def data_dictionnary_building(request, curriculum_year):
    data_dict = {'path_type': request.POST.get('path_type_%s' % curriculum_year),
                 'national_education': request.POST.get('national_education_%s' % curriculum_year),
                 'national_institution_french': request.POST.get('national_institution_french_%s' % curriculum_year),
                 'national_institution_dutch': request.POST.get('national_institution_dutch_%s' % curriculum_year),
                 'domain': request.POST.get('domain_%s' % curriculum_year),
                 'subdomain': request.POST.get('subdomain_%s' % curriculum_year),
                 'corresponds_to_domain': request.POST.get('corresponds_to_domain_%s' % curriculum_year),
                 'diploma_title': request.POST.get('diploma_title_%s' % curriculum_year),
                 'result_national': request.POST.get('result_national_%s' % curriculum_year),
                 'other_school_high_non_university':
                     request.POST.get('other_school_high_non_university_%s' % curriculum_year),
                 'other_high_non_university_name':
                     request.POST.get('other_high_non_university_name_%s' % curriculum_year),
                 'national_high_non_university_institution':
                     request.POST.get('national_high_non_university_institution_%s' % curriculum_year),
                 'domain_non_university': request.POST.get('domain_non_university_%s' % curriculum_year),
                 'grade_type_no_university': request.POST.get('grade_type_no_university_%s' % curriculum_year),
                 'study_systems': request.POST.get('study_systems_%s' % curriculum_year),
                 'grade_type': request.POST.get('grade_type_%s' % curriculum_year),
                 'diploma': request.POST.get('diploma_%s' % curriculum_year),
                 'credits_enrolled': request.POST.get('credits_enrolled_%s' % curriculum_year),
                 'credits_obtained': request.POST.get('credits_obtained_%s' % curriculum_year),
                 'foreign_institution_country': request.POST.get('foreign_institution_country_%s' % curriculum_year),
                 'foreign_institution_city': request.POST.get('foreign_institution_city_%s' % curriculum_year),
                 'city_specify': request.POST.get('city_specify_%s' % curriculum_year),
                 'txt_name_specify': request.POST.get('txt_name_specify_%s' % curriculum_year),
                 'foreign_institution_name': request.POST.get('foreign_institution_name_%s' % curriculum_year),
                 'name_specify': request.POST.get('name_specify_%s' % curriculum_year),
                 'foreign_institution': request.POST.get('foreign_institution_%s' % curriculum_year),
                 'foreign_high_institution_name':
                     request.POST.get('foreign_high_institution_name_%s' % curriculum_year),
                 'foreign_high_institution_country':
                     request.POST.get('foreign_high_institution_country_%s' % curriculum_year),
                 'national_institution_locality_adhoc':
                     request.POST.get('national_institution_locality_adhoc_%s' % curriculum_year),
                 'national_institution_name_adhoc':
                     request.POST.get('national_institution_name_adhoc_%s' % curriculum_year),
                 'domain_foreign': request.POST.get('domain_foreign_%s' % curriculum_year),
                 'grade_type_foreign': request.POST.get('grade_type_foreign_%s' % curriculum_year),
                 'subdomain_foreign': request.POST.get('subdomain_foreign_%s' % curriculum_year),
                 'diploma_foreign': request.POST.get('diploma_foreign_%s' % curriculum_year),
                 'result': request.POST.get('result_%s' % curriculum_year),
                 'credits_enrolled_foreign': request.POST.get('credits_enrolled_foreign_%s' % curriculum_year),
                 'credits_obtained_foreign': request.POST.get('credits_obtained_foreign_%s' % curriculum_year),
                 'linguistic_regime': request.POST.get('linguistic_regime_%s' % curriculum_year),
                 'activity': request.POST.get('activity_%s' % curriculum_year),
                 'activity_type': request.POST.get('activity_type_%s' % curriculum_year),
                 'activity_place': request.POST.get('activity_place_%s' % curriculum_year)}
    return data_dict
