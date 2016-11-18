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
from datetime import datetime

from django.shortcuts import render
from django.utils.translation import ugettext_lazy as _

from admission import models as mdl
from base import models as mdl_base
from admission.views import common, navigation
from reference import models as mdl_reference
from admission.views import demande_validation
from admission.models.enums import document_type
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

FOREIGN_NATIONAL_DIPLOMA_TYPE = mdl.secondary_education.NATIONAL

ALERT_MANDATORY_FILE_RECTO_VERSO = _('mandatory_file_recto_verso')
ALERT_MANDATORY_FIELD = _('mandatory_field')
PROFESSIONAL_TYPE = 'PROFESSIONAL'
ADMISSION_EXAM_TYPE = 'ADMISSION'
LANGUAGE_EXAM_TYPE = 'LANGUAGE'
NB_YEARS_AVAILABLE_FOR_DIPLOMA_ACQUISITION = 50
FIELD_ON_STATUS = "on"
FIELD_TRUE_STATUS = 'true'
FIELD_FALSE_STATUS = 'false'
DATE_FORMAT = '%d/%m/%Y'


def get_secondary_education_exams(secondary_education):
    if secondary_education:
        admission_exam = mdl.secondary_education_exam.find_by_type(secondary_education_id=secondary_education.id,
                                                                   type='ADMISSION')
        professional_exam = mdl.secondary_education_exam.find_by_type(secondary_education_id=secondary_education.id,
                                                                      type=PROFESSIONAL_TYPE)
        local_language_exam = mdl.secondary_education_exam.find_by_type(secondary_education_id=secondary_education.id,
                                                                        type=LANGUAGE_EXAM_TYPE)
        return {"admission_exam": admission_exam,
                "professional_exam": professional_exam,
                "local_language_exam": local_language_exam}
    else:
        return {}


def diploma_save(request):
    next_step = False
    previous_step = False
    save_step = True

    if request.POST:
        if 'bt_next_step_up' in request.POST or 'bt_next_step_down' in request.POST:
            next_step = True
        else:
            if 'bt_previous_step_up' in request.POST or 'bt_previous_step_down' in request.POST:
                previous_step = True
        if 'submit_diploma' in request.POST:
            save_step = True

    application = mdl.application.find_first_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    secondary_education = mdl.secondary_education.find_by_person(applicant)

    if secondary_education is None:
        secondary_education = mdl.secondary_education.SecondaryEducation()
        secondary_education.academic_year = mdl_base.academic_year.current_academic_year()
        secondary_education.person = applicant

    if next_step or previous_step or save_step:
        secondary_education = populate_secondary_education(request, secondary_education)
        secondary_education.save()
        professional_exam = get_professional_exam(request, secondary_education)
        secondary_education_exam_update(secondary_education, PROFESSIONAL_TYPE, professional_exam)
        admission_exam = get_admission_exam(request, secondary_education)
        secondary_education_exam_update(secondary_education, ADMISSION_EXAM_TYPE, admission_exam)
        local_language_exam = get_local_language_exam(request, secondary_education)
        secondary_education_exam_update(secondary_education, LANGUAGE_EXAM_TYPE, local_language_exam)

        message_success = _('msg_info_saved')
        # Check if documents need to be deleted
        documents_update(request, secondary_education, application, professional_exam, admission_exam)

        if next_step:
            return render(request, "curriculum.html", {"application": application, "message_success": message_success})
        else:
            if previous_step:
                return HttpResponseRedirect(reverse('home'))
    app_id = None
    if application:
        app_id = application.id
    following_tab = navigation.get_following_tab(request, 'diploma', application)
    if following_tab:
        return following_tab

    data = get_prerequis_data(request, 1, app_id)
    data.update({"secondary_education": secondary_education})
    validation_messages = demande_validation.validate_diploma(application, secondary_education)

    if len(validation_messages) > 0:
        data.update({"validation_messages": validation_messages})
        data.update({"validated_diploma": False})
    else:
        data.update({"validation_messages": None})
        data.update({"validated_diploma": True})

    return render(request, "admission_home.html", data)


def diploma_update(request, application_id=None, saved=None):
    """
    Called when prerequis and diplomas are displayed
    :param request:
    :param application_id:
    :param saved:
    :return:
    """
    data = get_prerequis_data(request, saved, application_id)
    return render(request, "admission_home.html", data)


def create_admission_exam_type(admission_exam_type_name):
    new_admission_exam_type = mdl.admission_exam_type.AdmissionExamType()
    new_admission_exam_type.adhoc = True
    new_admission_exam_type.name = admission_exam_type_name
    new_admission_exam_type.save()
    return new_admission_exam_type


def populate_secondary_education(request, secondary_education):
    secondary_education = initialization_secondary_education(secondary_education)

    if request.POST.get('diploma'):
        if request.POST.get('diploma') == FIELD_TRUE_STATUS:
            populate_diploma_data(request, secondary_education)
        else:
            secondary_education.diploma = False

    # international_diploma
    if secondary_education.diploma is True and secondary_education.national is False:
        populate_international_diploma(request, secondary_education)
    # common
    if secondary_education.diploma is True \
            and (secondary_education.national is True or secondary_education.international_diploma is True):
        academic_year = None
        if request.POST.get('academic_year'):
            academic_year = int(request.POST.get('academic_year'))
        secondary_education.academic_year = academic_year

    return secondary_education


def populate_international_diploma(request, secondary_education):
    secondary_education.international_diploma = request.POST.get('international_diploma')

    if request.POST.get('international_diploma_country') \
            and request.POST.get('international_diploma_country') != "-":
        secondary_education.international_diploma_country = \
            get_country(request.POST.get('international_diploma_country'))
    if request.POST.get('international_diploma_language') \
            and request.POST.get('international_diploma_language') != "-":
        language_int = request.POST.get('international_diploma_language')
        if language_int == 'None':
            language_int = None
        if language_int:
            secondary_education.international_diploma_language = mdl_reference.language \
                .find_by_id(int(language_int))
    if secondary_education.international_diploma == FOREIGN_NATIONAL_DIPLOMA_TYPE:
        secondary_education.international_equivalence = request.POST.get('international_equivalence')
    secondary_education.result = request.POST.get('foreign_result')


def populate_diploma_data(request, secondary_education):
    secondary_education.diploma = True
    if request.POST.get('academic_year') and request.POST.get('academic_year').isnumeric():
        secondary_education.academic_year = int(request.POST.get('academic_year'))
    if request.POST.get('rdb_local_foreign'):
        if request.POST.get('rdb_local_foreign') == FIELD_TRUE_STATUS:
            secondary_education.national = True
            secondary_education.result = request.POST.get('result')
            if request.POST.get('local_community'):
                secondary_education.national_community = request.POST.get('local_community')
        else:
            secondary_education.national = False
            secondary_education.result = request.POST.get('foreign_result')
            secondary_education.national = False
    if request.POST.get('other_school') == FIELD_ON_STATUS:
        secondary_education.national_institution = get_other_education_institution(request)
    else:
        if request.POST.get('school') and request.POST.get('school').isnumeric():
            national_institution = mdl_reference.education_institution \
                .find_by_id(int(request.POST.get('school')))
            secondary_education.national_institution = national_institution
    if request.POST.get('other_education') == 'on':
        existing_education_type = mdl_reference.education_type \
            .find_by_name(request.POST.get('other_education_type'))
        if existing_education_type:
            secondary_education.education_type = existing_education_type
        else:
            secondary_education.education_type = create_new_education_type(request)
    else:
        if request.POST.get('rdb_education_transition_type'):
            secondary_education.education_type = mdl_reference.education_type \
                .find_by_id(int(request.POST.get('rdb_education_transition_type')))
        if request.POST.get('rdb_education_technic_type'):
            secondary_education.education_type = mdl_reference.education_type \
                .find_by_id(int(request.POST.get('rdb_education_technic_type')))

    secondary_education.dipl_acc_high_educ = get_boolean_value(request.POST.get('dipl_acc_high_educ'))
    secondary_education.path_repetition = get_boolean_value(request.POST.get('path_repetition'))
    secondary_education.path_reorientation = get_boolean_value(request.POST.get('path_reorientation'))


def get_other_education_institution(request):
    existing_institution = mdl_reference.education_institution \
        .find_by_name_city_postal_code(request.POST.get('CESS_other_school_name'),
                                       request.POST.get('CESS_other_school_city'),
                                       request.POST.get('CESS_other_school_postal_code'),
                                       request.POST.get('school_local_community'))

    if existing_institution:
        return existing_institution
    else:
        if request.POST.get('CESS_other_school_name') or \
                request.POST.get('CESS_other_school_city') or \
                request.POST.get('CESS_other_school_postal_code'):
            return create_new_education_instit(request)
        else:
            return None


def secondary_education_exam_update(secondary_education, secondary_education_exam_type, secondary_education_exam):
    if secondary_education_exam:
        secondary_education_exam.save()
    else:
        # Delete if it exists
        if secondary_education:
            secondary_education_exam = mdl.secondary_education_exam.find_by_type(secondary_education,
                                                                                 secondary_education_exam_type)
            if secondary_education_exam:
                secondary_education_exam.delete()


def documents_update(request, secondary_education, application, professional_exam, admission_exam):
    list_unwanted_files = []

    if not secondary_education.diploma:
        list_unwanted_files.append(document_type.NATIONAL_DIPLOMA_RECTO)
        list_unwanted_files.append(document_type.NATIONAL_DIPLOMA_VERSO)
        list_unwanted_files.append(document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO)
        list_unwanted_files.append(document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO)
    if secondary_education.diploma and secondary_education.national:
        list_unwanted_files.append(document_type.INTERNATIONAL_DIPLOMA_RECTO)
        list_unwanted_files.append(document_type.INTERNATIONAL_DIPLOMA_VERSO)
    if secondary_education.international_diploma is None \
            or secondary_education.international_diploma != FOREIGN_NATIONAL_DIPLOMA_TYPE:
        list_unwanted_files.append(document_type.EQUIVALENCE)
    if secondary_education.international_diploma_language is None \
            or secondary_education.international_diploma_language.recognized:
        list_unwanted_files.append(document_type.TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO)
        list_unwanted_files.append(document_type.TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO)
        list_unwanted_files.append(document_type.TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO)
        list_unwanted_files.append(document_type.TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO)
    if professional_exam is None:
        list_unwanted_files.append(document_type.PROFESSIONAL_EXAM_CERTIFICATE)
    if admission_exam is None:
        list_unwanted_files.append(document_type.ADMISSION_EXAM_CERTIFICATE)
    delete_documents(request, application, list_unwanted_files)


def delete_documents(request, application, list_unwanted_files):
    applicant = mdl.applicant.find_by_user(request.user)
    for file_description in list_unwanted_files:
        documents = mdl.applicant_document_file.find_document_by_applicant_and_description(applicant, file_description)
        for document in documents:
            documents_application = mdl.application_document_file.search(application, file_description)
            for doc_application in documents_application:
                doc_application.delete()
            document.document_file.delete()


def get_secondary_education_files(application):
    return{'national_diploma_verso': mdl.application_document_file.find_first(application,
                                                                              document_type.NATIONAL_DIPLOMA_VERSO),
           'national_diploma_recto': mdl.application_document_file.find_first(application,
                                                                              document_type.NATIONAL_DIPLOMA_RECTO),
           'international_diploma_verso':
               mdl.application_document_file.search(application, document_type.INTERNATIONAL_DIPLOMA_VERSO),
           'international_diploma_recto':
               mdl.application_document_file.search(application, document_type.INTERNATIONAL_DIPLOMA_RECTO),
           'translated_international_diploma_verso':
               mdl.application_document_file.search(application, document_type.TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO),
           'translated_international_diploma_recto':
               mdl.application_document_file.search(application, document_type.TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO),
           'high_school_scores_transcript_recto':
               mdl.application_document_file.search(application, document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO),
           'high_school_scores_transcript_verso':
               mdl.application_document_file.search(application, document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO),
           'translated_high_school_scores_transcript_recto':
               mdl.application_document_file.search(application,
                                                    document_type.TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO),
           'translated_high_school_scores_transcript_verso':
               mdl.application_document_file.search(application,
                                                    document_type.TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO),
           'equivalence_file':
               mdl.application_document_file.find_first(application, document_type.EQUIVALENCE),
           'admission_exam_file':
               mdl.application_document_file.find_first(application, document_type.ADMISSION_EXAM_CERTIFICATE),
           'professional_exam_file':
               mdl.application_document_file.find_first(application, document_type.PROFESSIONAL_EXAM_CERTIFICATE),
           'language_exam_file':
               mdl.application_document_file.find_first(application, document_type.LANGUAGE_EXAM_CERTIFICATE)}


def get_prerequis_data(request, saved, application_id):
    message_info = ""
    if saved:
        message_info = _('msg_info_saved')

    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.find_first_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    other_language_regime = mdl_reference.language.find_unrecognized_languages()
    recognized_languages = mdl_reference.language.find_recognized_languages()
    exam_types = mdl.admission_exam_type.find_all_by_adhoc(False)
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    education_type_transition = mdl_reference.education_type.find_education_type_by_adhoc('TRANSITION', False)
    education_type_qualification = mdl_reference.education_type.find_education_type_by_adhoc('QUALIFICATION', False)
    local_language_exam_link = mdl.properties.find_by_key('PROFESSIONAL_EXAM_LINK')
    professional_exam_link = mdl.properties.find_by_key('LOCAL_LANGUAGE_EXAM_LINK')
    countries = mdl_reference.country.find_excluding("BE")
    current_academic_year = mdl_base.academic_year.current_academic_year()
    academic_years = []
    if current_academic_year:
        upper_bound = current_academic_year.year
        low_bound = upper_bound - NB_YEARS_AVAILABLE_FOR_DIPLOMA_ACQUISITION
        year_cpt = low_bound
        while year_cpt <= upper_bound:
            academic_years.append(year_cpt)
            year_cpt = year_cpt + 1
    current_year = None
    if current_academic_year:
        current_year = current_academic_year.year
    data = {"application":                  application,
            "academic_years":               academic_years,
            "secondary_education":          secondary_education,
            "countries":                    countries,
            "recognized_languages":         recognized_languages,
            "languages":                    other_language_regime,
            "exam_types":                   exam_types,
            'local_language_exam_link':     local_language_exam_link,
            "professional_exam_link":       professional_exam_link,
            "education_type_transition":    education_type_transition,
            "education_type_qualification": education_type_qualification,
            "current_academic_year":        current_year,
            "local_language_exam_needed":   common.is_local_language_exam_needed(request.user),
            'tab_active':                   navigation.PREREQUISITES_TAB,
            'applications':                 mdl.application.find_by_user(request.user),
            'message_info':                 message_info}
    # merge dictionaries
    data.update(get_secondary_education_exams(secondary_education))
    data.update(get_secondary_education_files(application))
    data.update(demande_validation.get_validation_status(application, applicant))
    return data


def initialization_secondary_education(secondary_education):
    secondary_education.diploma = None
    secondary_education.academic_year = None
    secondary_education.national = None
    secondary_education.national_community = None
    secondary_education.national_institution = None
    secondary_education.education_type = None
    secondary_education.dipl_acc_high_educ = None
    secondary_education.path_repetition = None
    secondary_education.path_reorientation = None
    secondary_education.result = None
    secondary_education.international_diploma = None
    secondary_education.international_diploma_country = None
    secondary_education.international_diploma_language = None
    secondary_education.international_equivalence = None
    return secondary_education


def create_new_education_type(request):
    new_education_type = mdl_reference.education_type.EducationType()
    new_education_type.adhoc = True
    new_education_type.name = request.POST.get('other_education_type')
    new_education_type.type = 'ANOTHER'
    new_education_type.save()
    return new_education_type


def create_new_education_instit(request):
    new_education_institution = mdl_reference.education_institution.EducationInstitution()
    new_education_institution.name = request.POST.get('CESS_other_school_name')
    new_education_institution.city = request.POST.get('CESS_other_school_city')
    new_education_institution.postal_code = request.POST.get('CESS_other_school_postal_code')
    new_education_institution.institution_type = "SECONDARY"
    new_education_institution.national_community = request.POST.get('school_local_community')
    new_education_institution.adhoc = True
    new_education_institution.country = mdl_reference.country.find_by_iso_code('BE')
    new_education_institution.save()
    return new_education_institution


def set_national_institution(name, city, postal_code, adhoc):
    national_institution = mdl_reference.education_institution.EducationInstitution()
    national_institution.name = name
    national_institution.city = city
    national_institution.postal_code = postal_code
    national_institution.adhoc = adhoc
    return national_institution


def get_country(country_id):
    if country_id == "-1":
        country_id = None
    country = None
    if country_id and int(country_id) >= 0:
        country = mdl_reference.country.find_by_id(int(country_id))
    return country


def get_professional_exam(request, secondary_education):
    professional_exam = None
    if request.POST.get('professional_exam'):
        if request.POST.get('professional_exam') == FIELD_TRUE_STATUS:
            professional_exam = mdl.secondary_education_exam.find_by_type(secondary_education, PROFESSIONAL_TYPE)
            if professional_exam is None:
                professional_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                professional_exam.secondary_education = secondary_education
            professional_exam.type = PROFESSIONAL_TYPE
            professional_exam.exam_date = None
            if not(request.POST.get('professional_exam_date') is None or
                   len(request.POST.get('professional_exam_date').strip()) == 0):
                try:
                    professional_exam.exam_date = datetime\
                        .strptime(request.POST.get('professional_exam_date'), DATE_FORMAT)
                except ValueError:
                    professional_exam.exam_date = None

            if request.POST.get('professional_exam_institution') is None \
                    or len(request.POST.get('professional_exam_institution').strip()) == 0:
                professional_exam.institution = None
            else:
                professional_exam.institution = request.POST.get('professional_exam_institution')
            if request.POST.get('professional_exam_result') is None:
                professional_exam.result = None
            else:
                professional_exam.result = request.POST.get('professional_exam_result')
    return professional_exam


def get_admission_exam(request, secondary_education):
    admission_exam = None
    if request.POST.get('admission_exam'):
        if request.POST.get('admission_exam') == FIELD_TRUE_STATUS:
            admission_exam = mdl.secondary_education_exam.find_by_type(secondary_education, ADMISSION_EXAM_TYPE)
            if admission_exam is None:
                admission_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                admission_exam.type = ADMISSION_EXAM_TYPE
                admission_exam.secondary_education = secondary_education

            if request.POST.get('admission_exam_date') is None \
                    or len(request.POST.get('admission_exam_date').strip()) == 0:
                admission_exam.exam_date = None
            else:
                try:
                    admission_exam.exam_date = datetime\
                        .strptime(request.POST.get('admission_exam_date'), DATE_FORMAT)
                except ValueError:
                    admission_exam.exam_date = None
            if request.POST.get('admission_exam_institution') is None \
                    or len(request.POST.get('admission_exam_institution').strip()) == 0:
                admission_exam.institution = None
            else:
                admission_exam.institution = request.POST.get('admission_exam_institution')
            if request.POST.get('admission_exam_type') is None \
                    and (request.POST.get('admission_exam_type_other') is None or
                         len(request.POST.get('admission_exam_type_other').strip()) == 0):
                admission_exam.admission_exam_type = None
            else:
                if request.POST.get('admission_exam_type') == 'OTHER_EXAM':
                    if request.POST.get('admission_exam_type_other') is None \
                            or len(request.POST.get('admission_exam_type_other').strip()) == 0:
                        admission_exam.admission_exam_type = None
                    else:
                        admission_exam.admission_exam_type = \
                            create_admission_exam_type(request.POST.get('admission_exam_type_other'))

                if request.POST.get('chb_admission_exam_type_other') == "on":
                    admission_exam.admission_exam_type = \
                        create_admission_exam_type(request.POST.get('admission_exam_type_other'))
                else:
                    admission_exam.admission_exam_type = mdl.admission_exam_type\
                        .find_by_id(int(request.POST.get('admission_exam_type')))

            if request.POST.get('admission_exam_result') is None:
                admission_exam.result = None
            else:
                admission_exam.result = request.POST.get('admission_exam_result')

    return admission_exam


def get_local_language_exam(request, secondary_education):
    local_language_exam = None
    if not(common.is_local_language_exam_needed(request.user) and request.POST.get('local_language_exam') is None):
        if request.POST.get('local_language_exam') == FIELD_TRUE_STATUS:
            local_language_exam = mdl.secondary_education_exam.find_by_type(secondary_education, LANGUAGE_EXAM_TYPE)
            if local_language_exam is None:
                local_language_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                local_language_exam.type = 'LANGUAGE'
                local_language_exam.secondary_education = secondary_education
            local_language_exam.exam_date = None
            if not(request.POST.get('local_language_exam_date') is None or
                   len(request.POST.get('local_language_exam_date').strip()) == 0):
                try:
                    local_language_exam.exam_date = datetime\
                        .strptime(request.POST.get('local_language_exam_date'), '%d/%m/%Y')
                except ValueError:
                    local_language_exam.exam_date = None
            local_language_exam.institution = None
            if not(request.POST.get('local_language_exam_institution') is None or
                   len(request.POST.get('local_language_exam_institution').strip()) == 0):
                local_language_exam.institution = request\
                    .POST.get('local_language_exam_institution')
            if request.POST.get('local_language_exam_result') is None:
                local_language_exam.result = None
            else:
                local_language_exam.result = request.POST.get('local_language_exam_result')
    return local_language_exam


def get_boolean_value(field):
    if field:
        if field == FIELD_TRUE_STATUS:
            return True
        else:
            if field == FIELD_FALSE_STATUS:
                return False
    return None
