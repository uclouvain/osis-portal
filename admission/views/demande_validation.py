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

from admission.views import assimilation_criteria as assimilation_criteria_view
from django.utils.translation import ugettext_lazy as _
from admission.models.enums import document_type
from admission.models.enums import application_type


ALERT_MANDATORY_FIELD = _('mandatory_field')
ALERT_MANDATORY_FILE = _('mandatory_file')
ALERT_MANDATORY_FILE_RECTO_VERSO = _('mandatory_file_recto_verso')
PROFESSIONAL_TYPE = 'PROFESSIONAL'
ADMISSION_EXAM_TYPE = 'ADMISSION'
LANGUAGE_EXAM_TYPE = 'LANGUAGE'


def validate_profil(applicant):
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
    if applicant_legal_adress is None \
            or (applicant_legal_adress.street is None \
                or applicant_legal_adress.number is None \
                or applicant_legal_adress.postal_code is None \
                or applicant_legal_adress.city is None \
                or applicant_legal_adress.country is None):
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
                        docs = mdl.applicant_document_file.\
                            find_document_by_applicant_and_description(applicant, document_typ)
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
        docs_needed = assimilation_criteria_view.get_list_documents_descriptions(assimilation_criteria.criteria.id)
        for doc_needed in docs_needed:
            doc = mdl.applicant_document_file. \
                find_document_by_applicant_and_description(applicant, doc_needed)
            if not doc.exists():
                return False
    return True


def validate_diploma(application, secondary_education):
    validation_messages = {}

    if secondary_education:
        validate_prerequisites_data(application, secondary_education, validation_messages)

    return validation_messages


def validate_prerequisites_data(application, secondary_education, validation_messages):
    admission_exam = mdl.secondary_education_exam.find_by_type(secondary_education_id=secondary_education.id,
                                                               type='ADMISSION')
    professional_exam = mdl.secondary_education_exam.find_by_type(secondary_education_id=secondary_education.id,
                                                                  type='PROFESSIONAL')
    local_language_exam = mdl.secondary_education_exam.find_by_type(secondary_education_id=secondary_education.id,
                                                                    type='LANGUAGE')
    if secondary_education.diploma is not True \
            and admission_exam is None \
            and professional_exam is None \
            and local_language_exam is None:
        validation_messages['diploma'] = _('msg_one_prerequisite')
    else:
        if secondary_education.diploma is True and secondary_education.national is True:
            if secondary_education.academic_year is None:
                validation_messages['academic_year'] = ALERT_MANDATORY_FIELD
            if secondary_education.national_community is None:
                validation_messages['local_community'] = ALERT_MANDATORY_FIELD
            else:
                if secondary_education.national_community == 'FRENCH' \
                        and secondary_education.academic_year < 1994 \
                        and secondary_education.dipl_acc_high_educ is None:
                    validation_messages['dipl_acc_high_educ'] = ALERT_MANDATORY_FIELD

                if secondary_education.national_community == 'DUTCH' \
                        and secondary_education.academic_year < 1992 \
                        and secondary_education.dipl_acc_high_educ is None:
                    validation_messages['dipl_acc_high_educ'] = ALERT_MANDATORY_FIELD

            if secondary_education.national_institution is None:
                validation_messages['school'] = _('msg_school_name')
            else:
                if secondary_education.national_institution.national_community == 'FRENCH' \
                        and secondary_education.education_type is None:
                    validation_messages['pnl_teaching_type'] = _('msg_error_education_type')

            if secondary_education.path_repetition is None:
                validation_messages['path_repetition'] = ALERT_MANDATORY_FIELD
            if secondary_education.path_reorientation is None:
                validation_messages['path_reorientation'] = ALERT_MANDATORY_FIELD
            if secondary_education.result is None:
                validation_messages['result'] = ALERT_MANDATORY_FIELD
            # Validation of the needed documents
            validation_messages.update(validate_needed_docs(application))

        validation_messages.update(validate_professional_exam(professional_exam, application))
        validation_messages.update(validate_admission_exam(admission_exam, application))
        validation_messages.update(validate_local_language_exam(local_language_exam))


def _validate_application():
    return False


def _validate_curriculum():
    return False


def _validate_accounting():
    return False


def _validate_sociological():
    return False


def _validate_attachments():
    return False


def _validate_submission():
    return False


def get_validation_status(application, applicant):
    secondary_education = mdl.secondary_education.find_by_person(applicant)
    if secondary_education:
        validated_diploma = True
        if len(validate_diploma(application, secondary_education)) > 0:
            validated_diploma = False
    else:
        validated_diploma = False
    return {
        "validated_profil":             validate_profil(applicant),
        "validated_diploma":            validated_diploma,
        "validated_curriculum":         _validate_curriculum(),
        "validated_application":        _validate_application(),
        "validated_accounting":         _validate_accounting(),
        "validated_sociological":       _validate_sociological(),
        "validated_attachments":        _validate_attachments(),
        "validated_submission":         _validate_submission(),
        "validation_message":           None}


def validate_needed_docs(application):
    validation_messages = {}
    doc_recto = mdl.application_document_file.search(application, document_type.NATIONAL_DIPLOMA_RECTO)
    doc_verso = mdl.application_document_file.search(application, document_type.NATIONAL_DIPLOMA_VERSO)
    if doc_recto.exists() is False or doc_verso.exists() is False:
        validation_messages['national_diploma_doc'] = ALERT_MANDATORY_FILE_RECTO_VERSO
    if application and application.application_type == application_type.ADMISSION:
        doc_recto = mdl.application_document_file.search(application,
                                                         document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO)
        doc_verso = mdl.application_document_file.search(application,
                                                         document_type.HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO)
        if doc_recto.exists() is False or doc_verso.exists() is False:
            validation_messages['high_school_diploma_doc'] = ALERT_MANDATORY_FILE_RECTO_VERSO
    return validation_messages


def validate_professional_exam(professional_exam, application):
    validation_messages = {}
    if professional_exam:
        if professional_exam.exam_date is None:
            validation_messages['professional_exam_date'] = ALERT_MANDATORY_FIELD
        if professional_exam.institution is None:
            validation_messages['professional_exam_institution'] = ALERT_MANDATORY_FIELD
        if professional_exam.result is None:
            validation_messages['professional_exam_result'] = ALERT_MANDATORY_FIELD
        doc = mdl.application_document_file.search(application, document_type.PROFESSIONAL_EXAM_CERTIFICATE)
        if doc.exists() is False:
            validation_messages['professional_exam_doc'] = ALERT_MANDATORY_FIELD
    return validation_messages


def validate_admission_exam(admission_exam, application):
    validation_messages = {}
    if admission_exam:
        if admission_exam.exam_date is None:
            validation_messages['admission_exam_date'] = ALERT_MANDATORY_FIELD
        if admission_exam.institution is None:
            validation_messages['admission_exam_institution'] = ALERT_MANDATORY_FIELD
        if admission_exam.admission_exam_type is None:
            validation_messages['admission_exam_type'] = ALERT_MANDATORY_FIELD
        else:
            offer_year = get_application_offer_year(application)
            if offer_year:
                offer_admission_exam_type = mdl.offer_admission_exam_type.find_by_offer_year(offer_year)
                if offer_admission_exam_type and \
                        (offer_admission_exam_type.admission_exam_type != admission_exam.admission_exam_type):
                    validation_messages['admission_exam_type'] = "{0} '{1}' {2} {3}"\
                        .format(_('the_exam_type'),
                                offer_admission_exam_type.admission_exam_type.name,
                                _('is_required_for'),
                                application.offer_year.acronym)
        if admission_exam.result is None:
            validation_messages['admission_exam_result'] = ALERT_MANDATORY_FIELD

    return validation_messages


def validate_local_language_exam(local_language_exam):
    validation_messages = {}
    if local_language_exam:
        if local_language_exam.exam_date is None:
            validation_messages['local_language_exam_date'] = ALERT_MANDATORY_FIELD
        if local_language_exam.institution is None:
            validation_messages['local_language_exam_institution'] = ALERT_MANDATORY_FIELD
        if local_language_exam.result is None:
            validation_messages['local_language_exam_result'] = ALERT_MANDATORY_FIELD
    return validation_messages


def get_application_offer_year(application):
    if application:
        try:
            return application.offer_year
        except:
            return None
    return None
