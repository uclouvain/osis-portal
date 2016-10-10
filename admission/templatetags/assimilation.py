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
from django import template
from django.utils.translation import ugettext_lazy as _
from reference.enums import assimilation_criteria as assimilation_criteria_enum
register = template.Library()


@register.filter
def div_visibility(applicant_assimilation_criteria, criteria):
    for applicant_criteria_div in applicant_assimilation_criteria:
        if applicant_criteria_div.criteria == criteria[0] and applicant_criteria_div.selected:
            return True
    return False


@register.filter
def button_class(assimilation_documents_existing, document_description):
    for d in assimilation_documents_existing:
        if d.description == document_description:
            return "glyphicon glyphicon-ok-circle"
    return "glyphicon glyphicon-upload"


@register.filter
def button_title(assimilation_documents_existing, document_description):
    for d in assimilation_documents_existing:
        if d.description == document_description:
            return _('change_document')
    return _('add_document')


@register.filter
def table_display(assimilation_basic_documents, criteria):
    for doc in assimilation_basic_documents:
        if doc.criteria == criteria[0]:
            return True
    return False


@register.filter
def assimilation_criteria_radio(applicant_assimilation_criteria, criteria):
    if applicant_assimilation_criteria.exists():
        for applicant_criteria_div in applicant_assimilation_criteria:
            if applicant_criteria_div.criteria == criteria[0]:
                if not applicant_criteria_div.selected:
                    return "checked"
                else:
                    return ""
        return "checked"
    return ""


@register.filter
def button_class_color(assimilation_documents_existing, document_description):
    for d in assimilation_documents_existing:
        if d.description == document_description:
            return "btn btn-success class_upload_assimilation"
    return "btn btn-default class_upload_assimilation"


@register.filter
def assimilation_criteria_criteria5(applicant_assimilation_criteria, criteria):
    for applicant_criteria_div in applicant_assimilation_criteria:
        if applicant_criteria_div.criteria == assimilation_criteria_enum.CRITERIA_5:
            if applicant_criteria_div.additional_criteria:
                if applicant_criteria_div.additional_criteria == criteria:
                    return "selected"
    return ""
