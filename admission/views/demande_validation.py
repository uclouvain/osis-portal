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


def validate_profil(applicant, user):
    if applicant.user.last_name is None \
        or applicant.user.first_name is None \
        or applicant.birth_date is None\
        or applicant.birth_place is None\
        or applicant.birth_country is None\
        or applicant.gender is None\
        or applicant.civil_status is None\
        or applicant.nationality is None \
            or applicant.additional_email is None:
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
    if applicant.nationality:
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


def validate_diploma(application):
    return False


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
