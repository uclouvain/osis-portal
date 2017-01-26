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
from admission.models.enums import document_type
from reference.enums import assimilation_criteria as assimilation_criteria_enum


def criteria1():
    list_document_type = []
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_1,
                        'descriptions': [document_type.RESIDENT_LONG_DURATION],
                        'first': True}
    list_document_type.append(assimilation_doc)
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_1,
                        'descriptions': [document_type.ID_FOREIGN_UNLIMITED],
                        'first': False}
    list_document_type.append(assimilation_doc)
    return list_document_type


def criteria2():
    list_document_type = []

    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_2,
                        'descriptions': [document_type.ATTACHMENT_26],
                        'first': True}
    list_document_type.append(assimilation_doc)

    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_2,
                        'descriptions': [document_type.REFUGEE_CARD,
                                         document_type.FAMILY_COMPOSITION,
                                         document_type.BIRTH_CERTIFICATE],
                        'first': False}

    list_document_type.append(assimilation_doc)
    #
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_2,
                        'descriptions': [document_type.REFUGEE_CARD,
                                         document_type.RESIDENT_CERTIFICATE,
                                         document_type.BIRTH_CERTIFICATE],
                        'first': False}
    list_document_type.append(assimilation_doc)
    #
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_2,
                        'descriptions': [document_type.FOREIGN_INSCRIPTION_CERTIFICATE,
                                         document_type.SUBSIDIARY_PROTECTION_DECISION,
                                         document_type.RESIDENCE_PERMIT],
                        'first': False}
    list_document_type.append(assimilation_doc)
    #
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_2,
                        'descriptions': [document_type.STATELESS_CERTIFICATE, ],
                        'first': False}
    list_document_type.append(assimilation_doc)
    return list_document_type


def find_assimilation_basic_documents():
    """
    Make a list of all the documents possible while encoding assimilation criteria
    List of object with
    :return:
    """
    list_document_type = []
    list_document_type.extend(criteria1())
    list_document_type.extend(criteria2())
    list_document_type.extend(criteria3())
    list_document_type.extend(criteria4())
    list_document_type.extend(criteria5())
    list_document_type.extend(criteria6())
    list_document_type.extend(criteria7())

    return list_document_type


def find_list_assimilation_basic_documents():
        assimilation_uploads = [
            document_type.ID_CARD,
            document_type.RESIDENT_LONG_DURATION,
            document_type.ID_FOREIGN_UNLIMITED,
            document_type.ATTACHMENT_26,
            document_type.REFUGEE_CARD,
            document_type.FAMILY_COMPOSITION,
            document_type.BIRTH_CERTIFICATE,
            document_type.RESIDENT_CERTIFICATE,
            document_type.STATELESS_CERTIFICATE,
            document_type.FOREIGN_INSCRIPTION_CERTIFICATE,
            document_type.SUBSIDIARY_PROTECTION_DECISION,
            document_type.RESIDENCE_PERMIT,
            document_type.PAYCHECK_1,
            document_type.PAYCHECK_2,
            document_type.PAYCHECK_3,
            document_type.PAYCHECK_4,
            document_type.PAYCHECK_5,
            document_type.PAYCHECK_6,
            document_type.CPAS,
            document_type.TUTORSHIP_CERTIFICATE,
            document_type.OTHER,
            document_type.SCHOLARSHIP_CFWB,
            document_type.SCHOLARSHIP_DEVELOPMENT_COOPERATION]
        return assimilation_uploads


def criteria3():
    list_document_type = []

    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_3,
                        'descriptions': [document_type.FAMILY_COMPOSITION,
                                         document_type.PAYCHECK_1, document_type.PAYCHECK_2,
                                         document_type.PAYCHECK_3, document_type.PAYCHECK_4,
                                         document_type.PAYCHECK_5, document_type.PAYCHECK_6, document_type.ID_CARD],
                        'first': True}
    list_document_type.append(assimilation_doc)
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_3,
                        'descriptions': [document_type.RESIDENT_CERTIFICATE,
                                         document_type.PAYCHECK_1, document_type.PAYCHECK_2,
                                         document_type.PAYCHECK_3, document_type.PAYCHECK_4,
                                         document_type.PAYCHECK_5, document_type.PAYCHECK_6, document_type.ID_CARD],
                        'first': False}
    list_document_type.append(assimilation_doc)
    return list_document_type


def criteria4():
    list_document_type = []

    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_4,
                        'descriptions': [document_type.CPAS],
                        'first': True}
    list_document_type.append(assimilation_doc)
    return list_document_type


def criteria5():
    list_document_type = []

    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_5,
                        'descriptions': [document_type.ID_CARD, document_type.TUTORSHIP_CERTIFICATE],
                        'first': True}
    list_document_type.append(assimilation_doc)
    return list_document_type


def criteria6():
    list_document_type = []
    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_6,
                        'descriptions': [document_type.SCHOLARSHIP_CFWB, document_type.TUTORSHIP_CERTIFICATE],
                        'first': True}
    list_document_type.append(assimilation_doc)
    return list_document_type


def criteria7():
    list_document_type = []

    assimilation_doc = {'criteria': assimilation_criteria_enum.CRITERIA_7,
                        'descriptions': [document_type.RESIDENT_LONG_DURATION],
                        'first': True}
    list_document_type.append(assimilation_doc)
    return list_document_type


def find_list_document_type_by_criteria(criteria):
    list_document_type = []
    if criteria == assimilation_criteria_enum.CRITERIA_1:
        list_document_type.extend(criteria1())
    if criteria == assimilation_criteria_enum.CRITERIA_2:
        list_document_type.extend(criteria2())
    if criteria == assimilation_criteria_enum.CRITERIA_3:
        list_document_type.extend(criteria3())
    if criteria == assimilation_criteria_enum.CRITERIA_4:
        list_document_type.extend(criteria4())
    if criteria == assimilation_criteria_enum.CRITERIA_5:
        list_document_type.extend(criteria5())
    if criteria == assimilation_criteria_enum.CRITERIA_6:
        list_document_type.extend(criteria6())
    if criteria == assimilation_criteria_enum.CRITERIA_7:
        list_document_type.extend(criteria7())
    return list_document_type


def get_list_documents_descriptions(criteria):
    list_document_type = []
    if criteria == assimilation_criteria_enum.CRITERIA_1:
        list_document_type.extend(criteria1())
    if criteria == assimilation_criteria_enum.CRITERIA_2:
        list_document_type.extend(criteria2())
    if criteria == assimilation_criteria_enum.CRITERIA_3:
        list_document_type.extend(criteria3())
    if criteria == assimilation_criteria_enum.CRITERIA_4:
        list_document_type.extend(criteria4())
    if criteria == assimilation_criteria_enum.CRITERIA_5:
        list_document_type.extend(criteria5())
    if criteria == assimilation_criteria_enum.CRITERIA_6:
        list_document_type.extend(criteria6())
    if criteria == assimilation_criteria_enum.CRITERIA_7:
        list_document_type.extend(criteria7())
    list_documents_description = []
    for l in list_document_type:
        for description in l['descriptions']:
            if description not in list_documents_description:
                list_documents_description.append(description)
    return list_documents_description


def find_list_only_assimilation_documents():
    list_documents = find_list_assimilation_basic_documents()
    list_documents.remove(document_type.ID_CARD)
    return list_documents
