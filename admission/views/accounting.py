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
from django.shortcuts import render

from admission import models as mdl
from admission.forms.accounting import AccountingForm
from admission.views import demande_validation, navigation
from base import models as mdl_base


def accounting(request, application_id=None):
    application = get_application(application_id, request)
    return render(request, "admission_home.html", get_data(application, request))


def accounting_update(request, application_id=None):
    application = populate_save_application(request, application_id)

    following_tab = navigation.get_following_tab(request, 'accounting', application)
    if following_tab:
        return following_tab

    return render(request, "admission_home.html", get_data(application, request))


def populate_save_application(request, application_id):
    application = get_application(application_id, request)

    if application_has_offer_year(application) and application.applicant:
        application.study_grant = False
        application.study_grant_number = None
        application.deduction_children = False
        application.scholarship = False
        application.scholarship_organization = None
        application.sport_membership = False
        application.culture_membership = False
        application.solidarity_membership = False
        application.bank_account_iban = None
        application.bank_account_bic = None
        application.bank_account_name = None
        if radio_form_value_is_true(request.POST.get('study_grant')):
            application.study_grant = True
            if request.POST.get('study_grant_number'):
                application.study_grant_number = request.POST.get('study_grant_number')
        else:
            if radio_form_value_is_true(request.POST.get('deduction_children')):
                application.deduction_children = True
        if radio_form_value_is_true(request.POST.get('scholarship')):
            application.scholarship = True
            if request.POST.get('scholarship_organization'):
                application.scholarship_organization = request.POST.get('scholarship_organization')
        if radio_form_value_is_true(request.POST.get('sport_membership')):
            application.sport_membership = True
        if radio_form_value_is_true(request.POST.get('culture_membership')):
            application.culture_membership = True
        if radio_form_value_is_true(request.POST.get('solidarity_membership')):
            application.solidarity_membership = True
        if request.POST.get('bank_account_iban'):
            application.bank_account_iban = request.POST.get('bank_account_iban')
        if request.POST.get('bank_account_bic'):
            application.bank_account_bic = request.POST.get('bank_account_bic')
        if request.POST.get('bank_account_name'):
            application.bank_account_name = request.POST.get('bank_account_name')
        application.save()

    return application


def debts_check(application):
    if application:
        academic_yr = mdl_base.academic_year.current_academic_year()
        if academic_yr:
            previous_academic_year = academic_yr.year - 1
            secondary_curriculum = mdl.curriculum.find_local_french(application.applicant, previous_academic_year)
            if secondary_curriculum:
                return True
    return False


def reduction_possible(application):
    if application_has_offer_year(application) and offer_year_reduction_possible(application.offer_year.acronym):
            return True
    return False


def third_cycle(application):
    if application_has_offer_year(application) and application.offer_year.acronym.endswith("2MC") \
            or application.offer_year.acronym.endswith("3D"):
        return True

    return False


def offer_year_reduction_possible(acronym):
    if reduction_by_acronym_ending(acronym) or reduction_by_acronym_containing(acronym):
        return True
    return False


def reduction_by_acronym_ending(acronym):
    acronym_endings = {"1BA", "2M1", "2MD", "2MA", "2MC", "3D"}
    for ending in acronym_endings:
        if acronym.endswith(ending):
            return True
    return False


def reduction_by_acronym_containing(acronym):
    if acronym.find("2MS/") != -1:
        return True
    return False


def application_has_offer_year(application):
    if application and application.offer_year_id is not None:
        return True
    return False


def radio_form_value_is_true(form_value):
    if form_value == "true":
        return True
    return False


def get_data(application, request):
    applicant = mdl.applicant.find_by_user(request.user)
    academic_yr = mdl_base.academic_year.current_academic_year()
    previous_academic_year = None
    if academic_yr:
        previous_academic_year = mdl_base.academic_year.find_by_year(academic_yr.year - 1)
    accounting_form = None
    if request.method == 'POST':
        accounting_form = AccountingForm(data=request.POST)
    data = {
        "academic_year": academic_yr,
        "previous_academic_year": previous_academic_year,
        "sport_affiliation_amount": 0,
        "culture_affiliation_amount": 0,
        "solidary_affiliation_amount": 0,
        "application": application,
        "debts_check": debts_check(application),
        "reduction_possible": reduction_possible(application),
        "third_cycle": third_cycle(application),
        "tab_active": navigation.ACCOUNTING_TAB,
        "applications": mdl.application.find_by_user(request.user),
        "form": accounting_form,
    }

    data.update(demande_validation.get_validation_status(application, applicant))
    return data


def get_application(application_id, request):
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    return application
