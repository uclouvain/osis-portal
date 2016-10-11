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
from admission.views.common import home, documents_upload
from admission.views import common
from reference import models as mdl_reference
from admission.views import demande_validation
from admission.models.enums import document_type
from osis_common import models as mdl_osis_common
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from admission.models.enums import application_type


ALERT_MANDATORY_FILE_RECTO_VERSO = _('mandatory_file_recto_verso')
ALERT_MANDATORY_FIELD = _('mandatory_field')
PROFESSIONAL_TYPE = 'PROFESSIONAL'
ADMISSION_EXAM_TYPE = 'ADMISSION'
LANGUAGE_EXAM_TYPE = 'LANGUAGE'


def validate_fields_form(request, secondary_education, next_step, application):
    validation_messages = {}
    is_valid = True
    academic_year = None
    admission_exam = None

    if request.POST.get('diploma'):
        if request.POST.get('diploma') == 'true':
            # secondary education diploma
            secondary_education.diploma = True

            if request.POST.get('academic_year') is None:
                validation_messages['academic_year'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                academic_year = mdl_base.academic_year.find_by_id(int(request.POST.get('academic_year')))
                secondary_education.academic_year = academic_year
            if request.POST.get('rdb_local_foreign') is None:
                validation_messages['rdb_local_foreign'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                if request.POST.get('rdb_local_foreign') == 'true':
                    secondary_education.national = True
                    # Local diploma
                    if request.POST.get('result') is None:
                        validation_messages['result'] = ALERT_MANDATORY_FIELD
                        is_valid = False
                    else:
                        secondary_education.result = request.POST.get('result')
                    if request.POST.get('local_community') is None:
                        validation_messages['local_community'] = ALERT_MANDATORY_FIELD
                        is_valid = False
                    else:
                        secondary_education.national_community = request.POST.get('local_community')
                        if request.POST.get('local_community') == 'FRENCH':
                            # diploma of the French community
                            if academic_year.year < 1994:
                                if request.POST.get('dipl_acc_high_educ') is None:
                                    validation_messages['dipl_acc_high_educ'] = ALERT_MANDATORY_FIELD
                                    is_valid = False
                            if request.POST.get('other_education') == 'on':
                                if request.POST.get('other_education_type') is None:
                                    validation_messages['pnl_teaching_type'] = _('msg_error_other_education_type')
                                    is_valid = False
                                else:
                                    new_education_type = mdl_reference.education_type.EducationType()
                                    new_education_type.adhoc = True
                                    new_education_type.name = request.POST.get('other_education_type')
                                    new_education_type.type = 'ANOTHER'
                                    new_education_type.save()
                                    secondary_education.education_type = new_education_type

                        else:
                            if request.POST.get('local_community') == 'DUTCH':
                                # diploma of the Dutch community
                                if academic_year.year < 1992:
                                    if request.POST.get('dipl_acc_high_educ') is None:
                                        validation_messages['dipl_acc_high_educ'] = ALERT_MANDATORY_FIELD
                                        is_valid = False

                    if request.POST.get('school_local_community') == 'FRENCH':
                        # Local school
                        if request.POST.get('rdb_education_transition_type') is None \
                                and request.POST.get('rdb_education_technic_type') is None\
                                and request.POST.get('other_education') is None:
                            validation_messages['pnl_teaching_type'] = _('msg_error_education_type')
                            is_valid = False
                        else:
                            if request.POST.get('rdb_education_transition_type'):
                                secondary_education.education_type = mdl_reference.education_type\
                                    .find_by_id(int(request.POST.get('rdb_education_transition_type')))
                            if request.POST.get('rdb_education_technic_type'):
                                secondary_education.education_type = mdl_reference.education_type\
                                    .find_by_id(int(request.POST.get('rdb_education_technic_type')))

                    if academic_year.year < 1994:
                        if request.POST.get('path_repetition') is None:
                            validation_messages['path_repetition'] = ALERT_MANDATORY_FIELD
                            is_valid = False
                        if request.POST.get('path_reorientation') is None:
                            validation_messages['path_reorientation'] = ALERT_MANDATORY_FIELD
                            is_valid = False
                    if (request.POST.get('school') is None or request.POST.get('school') == "-" or
                            request.POST.get('school') == "")\
                        and ((request.POST.get('CESS_other_school_name') is None or
                              (len(request.POST.get('CESS_other_school_name')) == 0))
                             and (request.POST.get('CESS_other_school_city') is None or
                                  len(request.POST.get('CESS_other_school_city')) == 0)
                             and (request.POST.get('CESS_other_school_postal_code') is None or
                                  len(request.POST.get('CESS_other_school_postal_code')) == 0)):
                        validation_messages['school'] = _('msg_school_name')
                        is_valid = False
                        # reset institution fields
                        secondary_education.national_institution = mdl_reference\
                            .education_institution.EducationInstitution()
                        secondary_education.national_institution.name = ""
                        secondary_education.national_institution.city = ""
                        secondary_education.national_institution.postal_code = ""
                        secondary_education.national_institution.adhoc = False
                    else:
                        if request.POST.get('other_school') == "on":
                            if request.POST.get('school_local_community') is None:
                                validation_messages['school'] = _('msg_error_school_local_community')
                                is_valid = False

                            national_institution = mdl_reference.education_institution.EducationInstitution()
                            national_institution.adhoc = True
                            national_institution.name = request.POST.get('CESS_other_school_name')
                            national_institution.city = request.POST.get('CESS_other_school_city')
                            national_institution.postal_code = request.POST.get('CESS_other_school_postal_code')

                            if request.POST.get('school_local_community'):
                                national_institution.national_community = request.POST\
                                    .get('school_local_community')
                            secondary_education.national_institution = national_institution

                        else:
                            if request.POST.get('school') \
                                    and request.POST.get('school') != "-" \
                                    and request.POST.get('school').isnumeric():
                                national_institution = mdl_reference.education_institution\
                                    .find_by_id(int(request.POST.get('school')))
                                secondary_education.national_institution = national_institution
                    # Validation of the needed documents
                    doc_recto = mdl.application_document_file.search(application, document_type.NATIONAL_DIPLOMA_RECTO)
                    doc_verso = mdl.application_document_file.search(application, document_type.NATIONAL_DIPLOMA_VERSO)
                    if doc_recto.exists() is False or doc_verso.exists() is False:
                        validation_messages['national_diploma_doc'] = ALERT_MANDATORY_FILE_RECTO_VERSO
                    if application.application_type == application_type.ADMISSION:
                        doc_recto = mdl.application_document_file.search(application, document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO)
                        doc_verso = mdl.application_document_file.search(application, document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO)
                        if doc_recto.exists() is False or doc_verso.exists() is False:
                            validation_messages['high_school_diploma_doc'] = ALERT_MANDATORY_FILE_RECTO_VERSO
                else:
                    if request.POST.get('rdb_local_foreign') == 'false':
                        if request.POST.get('foreign_result') is None:
                            validation_messages['foreign_result'] = ALERT_MANDATORY_FIELD
                            is_valid = False
                        else:
                            secondary_education.result = request.POST.get('foreign_result')
                        secondary_education.national = False
                        # Foreign diploma
                        if request.POST.get('international_diploma') is None:
                            validation_messages['international_diploma'] = _('msg_error_international_diploma')
                            is_valid = False
                        else:
                            secondary_education.international_diploma = request.POST.get('international_diploma')
                            if secondary_education.international_diploma == 'INTERNATIONAL':
                                if request.POST.get('international_equivalence') is None:
                                    validation_messages['international_equivalence'] = ALERT_MANDATORY_FIELD
                                    is_valid = False
                                else:
                                    secondary_education.international_equivalence = request\
                                        .POST.get('international_equivalence')
                            else:
                                secondary_education.international_equivalence = None
                        if request.POST.get('other_language_regime') == 'on':
                            if request.POST.get('other_international_diploma_language') is None or \
                                    request.POST.get('other_international_diploma_language') == "-":
                                validation_messages['language_regime'] = _('msg_other_language_diploma')
                                is_valid = False
                        else:
                            if request.POST.get('international_diploma_language') == "-":
                                validation_messages['language_regime'] = _('msg_language_diploma')
                                is_valid = False

        else:
            if request.POST.get('diploma') == 'false':
                secondary_education.diploma = False

            is_valid, validation_messages, secondary_education, admission_exam = validate_admission_exam(
                request,
                is_valid,
                validation_messages,
                secondary_education)
    else:
        validation_messages['diploma'] = ALERT_MANDATORY_FIELD
        is_valid = False

    is_valid, validation_messages, secondary_education, professional_exam = validate_professional_exam(
        request,
        is_valid,
        validation_messages,
        secondary_education)
    is_valid, validation_messages, secondary_education, local_language_exam = validate_local_language_exam(
        request, is_valid, validation_messages, secondary_education)

    if request.POST.get('diploma') == 'false' \
            and request.POST.get('admission_exam') == 'false' \
            and request.POST.get('professional_exam') == 'false':
        if next_step is True:
            validation_messages['final'] = "%s" % _('msg_error_next_step_impossible')
            validation_messages['final3'] = "%s " % _('question_professional_experience')
            validation_messages['final2'] = "%s " % _('question_admission_exam')
            validation_messages['final1'] = "%s " % _('question_get_diploma')
        validation_messages['diploma'] = "%s " % _('msg_one_prerequisite')
        is_valid = False

    return is_valid, validation_messages, secondary_education, professional_exam, admission_exam, local_language_exam


def get_secondary_education_exams_data(secondary_education):
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
    validate_diploma = False
    if request.POST:
        if 'bt_next_step_up' in request.POST or 'bt_next_step_down' in request.POST:
            next_step = True
        else:
            if 'bt_previous_step_up' in request.POST or 'bt_previous_step_down' in request.POST:
                previous_step = True
        if 'submit_diploma' in request.POST:
            save_step = True
        if 'validate_diploma' in request.POST:
            validate_diploma = True

    application = mdl.application.find_first_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    if validate_diploma:
        if secondary_education is None:
            secondary_education = mdl.secondary_education.SecondaryEducation()
            secondary_education.academic_year = mdl_base.academic_year.current_academic_year()
            secondary_education.person = applicant
        return validate(request, application, secondary_education, next_step)

    if secondary_education is None:
        secondary_education = mdl.secondary_education.SecondaryEducation()
        secondary_education.academic_year = mdl_base.academic_year.current_academic_year()
        secondary_education.person = applicant

    if next_step or previous_step or save_step:
        # Check if all the necessary fields have been filled
        is_valid, validation_messages, secondary_education, professional_exam, admission_exam, local_language_exam = \
            validate_fields_form(request, secondary_education, next_step, application)
        secondary_education = populate_secondary_education(request, secondary_education)
        secondary_education.save()
        secondary_education_exam_update(secondary_education, PROFESSIONAL_TYPE, professional_exam)
        secondary_education_exam_update(secondary_education, ADMISSION_EXAM_TYPE, admission_exam)
        secondary_education_exam_update(secondary_education, LANGUAGE_EXAM_TYPE, local_language_exam)

        message_success = _('msg_info_saved')
        # Check if documents need to be deleted
        documents_update(request, secondary_education, application, professional_exam, admission_exam)
        #
        if next_step:
            return render(request, "curriculum.html", {"application": application, "message_success": message_success})
        else:
            if previous_step:
                return HttpResponseRedirect(reverse('home'))
    app_id = None
    if application:
        app_id = application.id

    return HttpResponseRedirect(reverse('diploma_update', kwargs={'application_id': app_id, 'saved': 1}))


def diploma_update(request, application_id=None, saved=None):
    """
    Called when prerequis and diplomas are displayed
    :param request:
    :param application_id:
    :param saved:
    :return:
    """
    if saved:
        message_info = _('msg_info_saved')
    else:
        message_info = ""
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.find_first_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    other_language_regime = mdl_reference.language.find_languages_by_recognized(False)
    recognized_languages = mdl_reference.language.find_languages_by_recognized(True)
    exam_types = mdl.admission_exam_type.find_all_by_adhoc(False)
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    education_type_transition = mdl_reference.education_type.find_education_type_by_adhoc('TRANSITION', False)
    education_type_qualification = mdl_reference.education_type.find_education_type_by_adhoc('QUALIFICATION', False)
    local_language_exam_link = mdl.properties.find_by_key('PROFESSIONAL_EXAM_LINK')
    professional_exam_link = mdl.properties.find_by_key('LOCAL_LANGUAGE_EXAM_LINK')
    countries = mdl_reference.country.find_excluding("BE")
    academic_years = mdl_base.academic_year.find_academic_years()

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
            "current_academic_year":        mdl_base.academic_year.current_academic_year(),
            "local_language_exam_needed":   common.is_local_language_exam_needed(request.user),
            'tab_active':                   2,
            'applications': mdl.application.find_by_user(request.user),
            'message_info': message_info}

    # merge dictionaries
    data.update(get_secondary_education_exams_data(secondary_education))
    data.update(get_secondary_education_files_data(application))
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return render(request, "admission_home.html", data)


def validate_professional_exam(request, is_valid, validation_messages, secondary_education):
    professional_exam = None
    if request.POST.get('professional_exam') is None:
        validation_messages['professional_exam'] = ALERT_MANDATORY_FIELD
        is_valid = False
    else:
        if request.POST.get('professional_exam') == 'true':
            professional_exam = mdl.secondary_education_exam.find_by_type(secondary_education, PROFESSIONAL_TYPE)
            if professional_exam is None:
                professional_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                professional_exam.secondary_education = secondary_education
            professional_exam.type = PROFESSIONAL_TYPE
            professional_exam.exam_date = None
            if request.POST.get('professional_exam_date') is None \
                    or len(request.POST.get('professional_exam_date').strip()) == 0:
                validation_messages['professional_exam_date'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                try:
                    professional_exam.exam_date = datetime\
                        .strptime(request.POST.get('professional_exam_date'), '%d/%m/%Y')
                except ValueError:
                    validation_messages['professional_exam_date'] = _('wrong_date')
                    is_valid = False
                    professional_exam.exam_date = None

            if request.POST.get('professional_exam_institution') is None \
                    or len(request.POST.get('professional_exam_institution').strip()) == 0:
                validation_messages['professional_exam_institution'] = ALERT_MANDATORY_FIELD
                is_valid = False
                professional_exam.institution = None
            else:
                professional_exam.institution = request.POST.get('professional_exam_institution')
            if request.POST.get('professional_exam_result') is None:
                validation_messages['professional_exam_result'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                professional_exam.result = request.POST.get('professional_exam_result')
    return is_valid, validation_messages, secondary_education, professional_exam


def validate_local_language_exam(request, is_valid, validation_messages, secondary_education):
    local_language_exam = None
    if common.is_local_language_exam_needed(request.user) and request.POST.get('local_language_exam') is None:
        validation_messages['local_language_exam'] = "Il faut répondre oui ou non"
        is_valid = False
    else:
        if request.POST.get('local_language_exam') == 'true':
            local_language_exam = mdl.secondary_education_exam.find_by_type(secondary_education, LANGUAGE_EXAM_TYPE)
            if local_language_exam is None:
                local_language_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                local_language_exam.type = 'LANGUAGE'
                local_language_exam.secondary_education = secondary_education
            local_language_exam.exam_date = None
            if request.POST.get('local_language_exam_date') is None \
                    or len(request.POST.get('local_language_exam_date').strip()) == 0:
                validation_messages['local_language_exam_date'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                try:
                    local_language_exam.exam_date = datetime\
                        .strptime(request.POST.get('local_language_exam_date'), '%d/%m/%Y')
                except ValueError:
                    validation_messages['local_language_exam_date'] = _('wrong_date')
                    is_valid = False
                    local_language_exam.exam_date = None
            local_language_exam.institution = None
            if request.POST.get('local_language_exam_institution') is None \
                    or len(request.POST.get('local_language_exam_institution').strip()) == 0:
                validation_messages['local_language_exam_institution'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                local_language_exam.institution = request\
                    .POST.get('local_language_exam_institution')
            if request.POST.get('local_language_exam_result') is None:
                validation_messages['local_language_exam_result'] = ALERT_MANDATORY_FIELD
                is_valid = False
                local_language_exam.result = None
            else:
                local_language_exam.result = request.POST.get('local_language_exam_result')
    return is_valid, validation_messages, secondary_education, local_language_exam


def validate_admission_exam(request, is_valid, validation_messages, secondary_education):
    admission_exam = None
    if request.POST.get('admission_exam') is None:
        validation_messages['admission_exam'] = ALERT_MANDATORY_FIELD
        is_valid = False
    else:
        if request.POST.get('admission_exam') == 'true':
            admission_exam = mdl.secondary_education_exam.find_by_type(secondary_education, ADMISSION_EXAM_TYPE)
            if admission_exam is None:
                admission_exam = mdl.secondary_education_exam.SecondaryEducationExam()
                admission_exam.type = ADMISSION_EXAM_TYPE
                admission_exam.secondary_education = secondary_education

            if request.POST.get('admission_exam_date') is None \
                    or len(request.POST.get('admission_exam_date').strip()) == 0:
                validation_messages['admission_exam_date'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                try:
                    admission_exam.exam_date = datetime\
                        .strptime(request.POST.get('admission_exam_date'), '%d/%m/%Y')
                except ValueError:
                    validation_messages['admission_exam_date'] = _('wrong_date')
                    is_valid = False
                    admission_exam.exam_date = None
            if request.POST.get('admission_exam_institution') is None \
                    or len(request.POST.get('admission_exam_institution').strip()) == 0:
                validation_messages['admission_exam_institution'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                admission_exam.institution = request.POST.get('admission_exam_institution')
            if request.POST.get('admission_exam_type') is None \
                    and (request.POST.get('admission_exam_type_other') is None or
                         len(request.POST.get('admission_exam_type_other').strip()) == 0):
                validation_messages['admission_exam_type'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                if request.POST.get('admission_exam_type') == 'OTHER_EXAM':
                    if request.POST.get('admission_exam_type_other') is None \
                            or len(request.POST.get('admission_exam_type_other').strip()) == 0:
                        validation_messages['admission_exam_type'] = "Pour autre examen il faut préciser"
                        is_valid = False
                    else:
                        new_admission_exam_type = mdl.admission_exam_type.AdmissionExamType()
                        new_admission_exam_type.adhoc = True
                        new_admission_exam_type.name = request.POST.get('admission_exam_type_other')
                        new_admission_exam_type.save()
                        admission_exam.admission_exam_type = new_admission_exam_type

                if request.POST.get('chb_admission_exam_type_other') == "on":
                    new_admission_exam_type = mdl.admission_exam_type.AdmissionExamType()
                    new_admission_exam_type.adhoc = True
                    new_admission_exam_type.name = request.POST.get('admission_exam_type_other')
                    new_admission_exam_type.save()
                    admission_exam.admission_exam_type = new_admission_exam_type
                else:
                    admission_exam_type_existing = mdl.admission_exam_type \
                        .find_by_id(int(request.POST.get('admission_exam_type')))
                    admission_exam.admission_exam_type = admission_exam_type_existing

            if request.POST.get('admission_exam_result') is None:
                validation_messages['admission_exam_result'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                admission_exam.result = request.POST.get('admission_exam_result')

    return is_valid, validation_messages, secondary_education, admission_exam


def populate_secondary_education(request, secondary_education):
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

    if request.POST.get('diploma'):
        if request.POST.get('diploma') == 'true':
            if request.POST.get('academic_year'):
                academic_year = mdl_base.academic_year.find_by_id(int(request.POST.get('academic_year')))
                secondary_education.academic_year = academic_year
            secondary_education.diploma = True
            if request.POST.get('rdb_local_foreign'):
                if request.POST.get('rdb_local_foreign') == 'true':
                    secondary_education.national = True
                    secondary_education.result = request.POST.get('result')
                    if request.POST.get('local_community'):
                        secondary_education.national_community = request.POST.get('local_community')
                else:
                    secondary_education.national = False
                    secondary_education.result = request.POST.get('foreign_result')
                    secondary_education.national = False
            if request.POST.get('other_school') == "on":
                existing_institution = mdl_reference.education_institution\
                    .find_by_name_city_postal_code(request.POST.get('CESS_other_school_name'),
                                                   request.POST.get('CESS_other_school_city'),
                                                   request.POST.get('CESS_other_school_postal_code'),
                                                   request.POST.get('school_local_community'))
                if existing_institution:
                    secondary_education.national_institution = existing_institution
                else:
                    new_education_institution = mdl_reference.education_institution.EducationInstitution()
                    new_education_institution.name = request.POST.get('CESS_other_school_name')
                    new_education_institution.city = request.POST.get('CESS_other_school_city')
                    new_education_institution.postal_code = request.POST.get('CESS_other_school_postal_code')
                    new_education_institution.institution_type = "SECONDARY"
                    new_education_institution.national_community = request.POST.get('school_local_community')
                    new_education_institution.adhoc = True
                    new_education_institution.country = mdl_reference.country.find_by_iso_code('BE')
                    new_education_institution.save()
                    secondary_education.national_institution = new_education_institution
            else:
                if request.POST.get('school'):
                    national_institution = mdl_reference.education_institution\
                        .find_by_id(int(request.POST.get('school')))
                    secondary_education.national_institution = national_institution

            if request.POST.get('other_education') == 'on':
                existing_education_type = mdl_reference.education_type\
                    .find_by_name(request.POST.get('other_education_type'))
                if existing_education_type:
                    secondary_education.education_type = existing_education_type
                else:
                    new_education_type = mdl_reference.education_type.EducationType()
                    new_education_type.adhoc = True
                    new_education_type.name = request.POST.get('other_education_type')
                    new_education_type.type = 'ANOTHER'
                    new_education_type.save()
                    secondary_education.education_type = new_education_type
            else:
                if request.POST.get('rdb_education_transition_type'):
                    secondary_education.education_type = mdl_reference.education_type\
                        .find_by_id(int(request.POST.get('rdb_education_transition_type')))
                if request.POST.get('rdb_education_technic_type'):
                    secondary_education.education_type = mdl_reference.education_type\
                        .find_by_id(int(request.POST.get('rdb_education_technic_type')))

            if request.POST.get('dipl_acc_high_educ'):
                if request.POST.get('dipl_acc_high_educ') == 'true':
                    secondary_education.dipl_acc_high_educ = True
                else:
                    if request.POST.get('dipl_acc_high_educ') == 'false':
                        secondary_education.dipl_acc_high_educ = False

            if request.POST.get('path_repetition'):
                if request.POST.get('path_repetition') == 'true':
                    secondary_education.path_repetition = True
                else:
                    if request.POST.get('path_repetition') == 'false':
                        secondary_education.path_repetition = False

            if request.POST.get('path_reorientation'):
                if request.POST.get('path_reorientation') == 'true':
                    secondary_education.path_reorientation = True
                else:
                    if request.POST.get('path_reorientation') == 'false':
                        secondary_education.path_reorientation = False

        else:
            secondary_education.diploma = False

    # international_diploma
    secondary_education.international_diploma = None
    secondary_education.international_diploma_country = None
    secondary_education.international_diploma_language = None
    secondary_education.international_equivalence = None
    if secondary_education.diploma is True and secondary_education.national is False:
        if request.POST.get('international_diploma') == "true":
            secondary_education.international_diploma = True
        else:
            if request.POST.get('international_diploma') == "false":
                secondary_education.international_diploma = False
        secondary_education.international_diploma = request.POST.get('international_diploma')
        if request.POST.get('international_diploma_country') \
                and request.POST.get('international_diploma_country') != "-":
            country_id = request.POST.get('international_diploma_country')
            if country_id == "-1":
                country_id = None
            international_diploma_country = None
            if country_id and int(country_id) >= 0:
                international_diploma_country = mdl_reference.country\
                    .find_by_id(int(country_id))
            secondary_education.international_diploma_country = international_diploma_country
        if request.POST.get('other_language_regime') \
            and request.POST.get('other_language_regime') == "on" \
                and request.POST.get('other_language_regime') != "-":
            secondary_education.international_diploma_language = mdl_reference.language\
                .find_by_id(int(request.POST.get('other_international_diploma_language')))
        else:
            if request.POST.get('international_diploma_language') \
                    and request.POST.get('international_diploma_language') != "-":
                language_int = request.POST.get('international_diploma_language')
                if language_int == 'None':
                    language_int = None
                if language_int:
                    secondary_education.international_diploma_language = mdl_reference.language\
                        .find_by_id(int(language_int))

        secondary_education.international_equivalence = request.POST.get('international_equivalence')

        secondary_education.result = request.POST.get('foreign_result')
    # common
    if secondary_education.diploma is True \
            and (secondary_education.national is True or secondary_education.international_diploma is True):
        academic_year = None
        if request.POST.get('academic_year'):
            academic_year = mdl_base.academic_year.find_by_id(int(request.POST.get('academic_year')))
        secondary_education.academic_year = academic_year

    return secondary_education


def secondary_education_exam_update(secondary_education, type, secondary_education_exam):
    if secondary_education_exam:
        secondary_education_exam.save()
    else:
        # Delete if it exists
        if secondary_education:
            secondary_education_exam = mdl.secondary_education_exam.find_by_type(secondary_education, type)
            if secondary_education_exam:
                secondary_education_exam.delete()


def documents_update(request, secondary_education, application, professional_exam, admission_exam):
    list_unwanted_files = []

    if not secondary_education.diploma:
        list_unwanted_files.append(document_type.NATIONAL_DIPLOMA_RECTO)
        list_unwanted_files.append(document_type.NATIONAL_DIPLOMA_VERSO)
        list_unwanted_files.append(document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO)
        list_unwanted_files.append(document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO)
    if not secondary_education.international_diploma:
        list_unwanted_files.append(document_type.INTERNATIONAL_DIPLOMA_RECTO)
        list_unwanted_files.append(document_type.INTERNATIONAL_DIPLOMA_VERSO)
    if secondary_education.international_diploma is None \
            or secondary_education.international_diploma != 'INTERNATIONAL':
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
    for file_description in list_unwanted_files:
        documents = mdl_osis_common.document_file.search(request.user, file_description)
        for document in documents:
            documents_application = mdl.application_document_file.search(application, file_description)
            for doc_application in documents_application:
                doc_application.delete()
            document.delete()


def get_secondary_education_files_data(application):
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
    if saved:
        message_info = _('msg_info_saved')
    else:
        message_info = ""

    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.find_first_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    other_language_regime = mdl_reference.language.find_languages_by_recognized(False)
    recognized_languages = mdl_reference.language.find_languages_by_recognized(True)
    exam_types = mdl.admission_exam_type.find_all_by_adhoc(False)
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    education_type_transition = mdl_reference.education_type.find_education_type_by_adhoc('TRANSITION', False)
    education_type_qualification = mdl_reference.education_type.find_education_type_by_adhoc('QUALIFICATION', False)
    local_language_exam_link = mdl.properties.find_by_key('PROFESSIONAL_EXAM_LINK')
    professional_exam_link = mdl.properties.find_by_key('LOCAL_LANGUAGE_EXAM_LINK')
    countries = mdl_reference.country.find_excluding("BE")
    academic_years = mdl_base.academic_year.find_academic_years()

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
            "current_academic_year":        mdl_base.academic_year.current_academic_year(),
            "local_language_exam_needed":   common.is_local_language_exam_needed(request.user),
            'tab_active':                   2,
            'applications':                 mdl.application.find_by_user(request.user),
            'message_info':                 message_info,
            'current_academic_year':        mdl_base.academic_year.current_academic_year(),
            'form': None}

    # merge dictionaries
    data.update(get_secondary_education_exams_data(secondary_education))
    data.update(get_secondary_education_files_data(application))
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return data


def validate(request, application, secondary_education, next_step):
    application_id = None
    if application:
        application_id = application.id

    is_valid, validation_messages, secondary_education, professional_exam, admission_exam, local_language_exam = \
        validate_fields_form(request, secondary_education, next_step, application)

    data = get_prerequis_data(request, None, application_id)
    data.update({"secondary_education": secondary_education})

    if len(validation_messages) > 0:
        data.update({'valid_data': False})
        data.update({"validation_messages": validation_messages})
    else:
        data.update({'valid_data': True})
        data.update({"validation_messages": None})

    return render(request, "admission_home.html", data)