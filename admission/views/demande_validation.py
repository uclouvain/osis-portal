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
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.models import User
from admission import models as mdl
from osis_common import models as mdl_common

from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from admission.views import assimilation_criteria as assimilation_criteria_view
from django.utils.translation import ugettext_lazy as _
from admission.models.enums import document_type


ALERT_MANDATORY_FIELD = _('mandatory_field')
ALERT_MANDATORY_FILE = _('mandatory_file')
PROFESSIONAL_TYPE = 'PROFESSIONAL'
ADMISSION_EXAM_TYPE = 'ADMISSION'
LANGUAGE_EXAM_TYPE = 'LANGUAGE'


def validate_profil(applicant, user):
    if applicant.user.last_name is None \
        or applicant.user.first_name is None \
        or applicant.birth_date is None\
        or applicant.birth_place is None\
        or applicant.birth_country is None\
        or applicant.gender is None\
        or applicant.civil_status is None\
        or applicant.nationality is None \
        or applicant.additional_email is None \
            or applicant.additional_email.strip() == '':
        return False
    if (applicant.registration_id and applicant.last_academic_year is None) \
            or (applicant.registration_id is None and applicant.last_academic_year):
        return False

    applicant_legal_adress = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
    if applicant_legal_adress is None:
        return False
    else:
        if applicant_legal_adress.street is None \
                or applicant_legal_adress.number is None \
                or applicant_legal_adress.postal_code is None \
                or applicant_legal_adress.city is None \
                or applicant_legal_adress.country is None:
            return False
    if applicant.nationality and not applicant.nationality.european_union:
        applicant_assimilation_criterias = mdl.applicant_assimilation_criteria.find_by_applicant(applicant)
        if not applicant_assimilation_criterias:
            return False
        else:
            criteria_doc_ok = False
            for applicant_assimilation_criteria in applicant_assimilation_criterias:
                list_document_type = assimilation_criteria_view.\
                    find_list_document_type_by_criteria(applicant_assimilation_criteria.criteria.id)
                for l in list_document_type:
                    nb_necessary_doc = len(list_document_type)
                    nb_doc = 0
                    for document_typ in l.descriptions:
                        docs = mdl_common.document_file.search(user, document_typ)
                        if docs:
                            nb_doc = nb_doc+1
                    if nb_necessary_doc == nb_doc:
                        criteria_doc_ok = True
                        break
                if criteria_doc_ok:
                    break
            if not criteria_doc_ok:
                return False
    assimilation_criteria_list = mdl.applicant_assimilation_criteria.find_by_applicant(applicant)
    for assimilation_criteria in assimilation_criteria_list:
        docs_needed = assimilation_criteria_view.get_list_docs(assimilation_criteria.criteria.id)
        for doc_needed in docs_needed:
            doc = mdl_common.document_file.search(user, doc_needed)
            if not doc.exists():
                return False
    return True


def validate_application(application):
    return False


def validate_diploma(applicant, user):
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    validation_messages = {}
    is_valid = True
    if secondary_education:
        if secondary_education.diploma is True:
            if secondary_education.academic_year is None:
                validation_messages['academic_year'] = ALERT_MANDATORY_FIELD
                is_valid = False
            if secondary_education.result is None:
                validation_messages['result'] = ALERT_MANDATORY_FIELD
                is_valid = False
            if secondary_education.national is None:
                validation_messages['rdb_belgian_foreign'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                if secondary_education.national is True:
                    if secondary_education.national_community is None:
                        validation_messages['belgian_community'] = ALERT_MANDATORY_FIELD
                        is_valid = False
                    else:
                        if secondary_education.national_community == 'FRENCH':
                            # diploma of the French community
                            if secondary_education.academic_year.year < 1994:
                                if secondary_education.dipl_acc_high_educ is None:
                                    validation_messages['dipl_acc_high_educ'] = ALERT_MANDATORY_FIELD
                                    is_valid = False
                            if secondary_education.education_type is None:
                                    validation_messages['pnl_teaching_type'] = _('msg_error_other_education_type')
                                    is_valid = False
                        else:
                            if secondary_education.national_community == 'DUTCH':
                                # diploma of the Dutch community
                                if secondary_education.academic_year.year < 1992:
                                    if secondary_education.dipl_acc_high_educ is None:
                                        validation_messages['dipl_acc_high_educ'] = ALERT_MANDATORY_FIELD
                                        is_valid = False
                    if secondary_education.education_type == "FRENCH":
                        if secondary_education.education_type is None:
                            validation_messages['pnl_teaching_type'] = _('msg_error_education_type')
                            is_valid = False

                    if secondary_education.academic_year.year < 1994:
                        if secondary_education.path_repetition is None:
                            validation_messages['path_repetition'] = ALERT_MANDATORY_FIELD
                            is_valid = False
                        if secondary_education.path_orientation is None:
                            validation_messages['path_reorientation'] = ALERT_MANDATORY_FIELD
                            is_valid = False
                    if secondary_education.national_institution is None:
                        validation_messages['school'] = _('msg_school_name')
                        is_valid = False
                    doc = mdl_common.document_file.search(user, document_type.NATIONAL_DIPLOMA_RECTO)
                    if not doc.exists():
                        validation_messages['NATIONAL_DIPLOMA_RECTO'] = ALERT_MANDATORY_FILE
                        is_valid = False
                    doc = mdl_common.document_file.search(user, document_type.NATIONAL_DIPLOMA_VERSO)
                    if not doc.exists():
                        validation_messages['NATIONAL_DIPLOMA_VERSO'] = ALERT_MANDATORY_FILE
                        is_valid = False

                else:
                    if secondary_education.national is False:
                        if secondary_education.international_diploma is None:
                            validation_messages['international_diploma'] = _('msg_error_international_diploma')
                            is_valid = False
                        else:
                            if secondary_education.international_diploma == 'INTERNATIONAL':
                                if secondary_education.international_equivalence is None:
                                    validation_messages['international_equivalence'] = ALERT_MANDATORY_FIELD
                                    is_valid = False
                                else:
                                    if secondary_education.international_equivalence == 'YES':
                                        doc = mdl_common.document_file.search(user, document_type.EQUIVALENCE)
                                        if not doc.exists():
                                            validation_messages['EQUIVALENCE_FILE'] = ALERT_MANDATORY_FILE
                                            is_valid = False

                        if secondary_education.international_diploma_language is None:
                            validation_messages['language_regime'] = _('msg_language_diploma')
                            is_valid = False
                        else:
                            doc = mdl_common.document_file.search(user, document_type.INTERNATIONAL_DIPLOMA_RECTO)
                            if not doc.exists():
                                validation_messages['INTERNATIONAL_DIPLOMA_RECTO'] = ALERT_MANDATORY_FILE
                                is_valid = False
                            doc = mdl_common.document_file.search(user, document_type.INTERNATIONAL_DIPLOMA_VERSO)
                            if not doc.exists():
                                validation_messages['INTERNATIONAL_DIPLOMA_VERSO'] = ALERT_MANDATORY_FILE
                                is_valid = False
                            doc = mdl_common.document_file.search(user,
                                                                  document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO)
                            if not doc.exists():
                                validation_messages['HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO'] = ALERT_MANDATORY_FILE
                                is_valid = False
                            doc = mdl_common.document_file.search(user,
                                                                  document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO)
                            if not doc.exists():
                                validation_messages['HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO'] = ALERT_MANDATORY_FILE
                                is_valid = False
    # admission exam validation
    admission_exam = mdl.secondary_education_exam.find_by_type(secondary_education, ADMISSION_EXAM_TYPE)
    if admission_exam:
        if admission_exam.exam_date is None:
            validation_messages['admission_exam_date'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if admission_exam.institution is None:
            validation_messages['admission_exam_institution'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if admission_exam.admission_exam_type is None:
            validation_messages['admission_exam_type'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if admission_exam.result is None:
            validation_messages['admission_exam_result'] = ALERT_MANDATORY_FIELD
            is_valid = False

        doc = mdl_common.document_file.search(user, document_type.ADMISSION_EXAM_CERTIFICATE)
        if not doc.exists():
            validation_messages['ADMISSION_EXAM_CERTIFICATE'] = ALERT_MANDATORY_FILE
            is_valid = False
    # professional exam
    professional_exam = mdl.secondary_education_exam.find_by_type(secondary_education, PROFESSIONAL_TYPE)
    if professional_exam:
        if professional_exam.exam_date is None:
            validation_messages['professional_exam_date'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if professional_exam.institution is None:
            validation_messages['professional_exam_institution'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if professional_exam.result is None:
            validation_messages['professional_exam_result'] = ALERT_MANDATORY_FIELD
            is_valid = False

        doc = mdl_common.document_file.search(user, document_type.PROFESSIONAL_EXAM_CERTIFICATE)
        if not doc.exists():
            validation_messages['PROFESSIONAL_EXAM_CERTIFICATE'] = ALERT_MANDATORY_FILE
            is_valid = False
    # language exam
    language_exam = mdl.secondary_education_exam.find_by_type(secondary_education, LANGUAGE_EXAM_TYPE)
    if language_exam:
        if language_exam.exam_date is None:
            validation_messages['language_exam_date'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if language_exam.institution is None:
            validation_messages['language_exam_institution'] = ALERT_MANDATORY_FIELD
            is_valid = False
        if language_exam.result is None:
            validation_messages['language_exam_result'] = ALERT_MANDATORY_FIELD
            is_valid = False

        doc = mdl_common.document_file.search(user, document_type.LANGUAGE_EXAM_CERTIFICATE)
        if not doc.exists():
            validation_messages['LANGUAGE_EXAM_CERTIFICATE'] = ALERT_MANDATORY_FILE
            is_valid = False
    #
    if secondary_education.diploma is not True \
            and admission_exam is None \
            and professional_exam is None \
            and language_exam is None:
            validation_messages['prerequisites'] = _('prerequisites_min_data')
            is_valid = False
    # for key, value in validation_messages.items():
    #     print("{} : {}.".format(key, value))
    return is_valid


def validate_curriculum(application):
    return False


def validate_accounting():
    return False


def validate_sociological():
    return False


def validate_attachments():
    return False


def validate_submission():
    return False


def get_validation_status(application, applicant, user):
    return {
        "validated_profil":             validate_profil(applicant, user),
        "validated_diploma":            validate_diploma(applicant, user),
        "validated_curriculum":         validate_curriculum(application),
        "validated_application":        validate_application(application),
        "validated_accounting":         validate_accounting(),
        "validated_sociological":       validate_sociological(),
        "validated_attachments":        validate_attachments(),
        "validated_submission":         validate_submission()}
