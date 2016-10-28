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
from base import models as mdl_base
from admission.forms import AccountingForm
from admission.views import demande_validation, navigation


def accounting(request, application_id=None):
    print('accoutning')
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    academic_yr = mdl_base.academic_year.current_academic_year()
    previous_academic_year = mdl_base.academic_year.find_by_year(academic_yr.year - 1)
    sport_affiliation_amount = 0
    culture_affiliation_amount = 0
    solidary_affiliation_amount = 0
    applicant = mdl.applicant.find_by_user(request.user)

    data = {
        "academic_year": academic_yr,
        "previous_academic_year": previous_academic_year,
        "sport_affiliation_amount": sport_affiliation_amount,
        "culture_affiliation_amount": culture_affiliation_amount,
        "solidary_affiliation_amount": solidary_affiliation_amount,
        "application": application,
        "debts_check": debts_check(application),
        "reduction_possible": reduction_possible(application),
        "third_cycle": third_cycle(application),
        "tab_active": navigation.ACCOUNTING_TAB,
        "applications": mdl.application.find_by_user(request.user),
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def accounting_update(request, application_id=None):
    next_tab = navigation.ACCOUNTING_TAB
    academic_yr = mdl_base.academic_year.current_academic_year()
    previous_academic_year = mdl_base.academic_year.find_by_year(academic_yr.year - 1)
    sport_affiliation_amount = 0
    culture_affiliation_amount = 0
    solidary_affiliation_amount = 0
    accounting_form = None
    if request.method == 'POST':
        accounting_form = AccountingForm(data=request.POST)

    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)

    try:
        if application.offer_year and application.applicant:
            application.save()
    except:
        pass
    following_tab = navigation.get_following_tab(request, 'accounting', application)
    if following_tab:
        return following_tab
    data = {
        "academic_year": academic_yr,
        "previous_academic_year": previous_academic_year,
        "sport_affiliation_amount": sport_affiliation_amount,
        "culture_affiliation_amount": culture_affiliation_amount,
        "solidary_affiliation_amount": solidary_affiliation_amount,
        "application": application,
        "form": accounting_form,
        "debts_check": debts_check(application),
        "reduction_possible": reduction_possible(application),
        "third_cycle": third_cycle(application),
        "tab_active": next_tab,
        "applications": mdl.application.find_by_user(request.user),
    }
    applicant = mdl.applicant.find_by_user(request.user)
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def populate_application(request, application):
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
    if request.POST.get('study_grant') == "true":
        application.study_grant = True
        if request.POST.get('study_grant_number'):
            application.study_grant_number = request.POST.get('study_grant_number')
    else:
        if request.POST.get('deduction_children') == "true":
            application.deduction_children = True
    if request.POST.get('scholarship') == "true":
        application.scholarship = True
        if request.POST.get('scholarship_organization'):
            application.scholarship_organization = request.POST.get('scholarship_organization')
    if request.POST.get('sport_membership') == "true":
        application.sport_membership = True
    if request.POST.get('culture_membership') == "true":
        application.culture_membership = True
    if request.POST.get('solidarity_membership') == "true":
        application.solidarity_membership = True
    if request.POST.get('bank_account_iban'):
        application.bank_account_iban = request.POST.get('bank_account_iban')
    if request.POST.get('bank_account_bic'):
        application.bank_account_bic = request.POST.get('bank_account_bic')
    if request.POST.get('bank_account_name'):
        application.bank_account_name = request.POST.get('bank_account_name')
    return application


def debts_check(application):
    if application:
        academic_yr = mdl_base.academic_year.current_academic_year()
        previous_academic_year = academic_yr.year - 1
        secondary_curriculum = mdl.curriculum.find_local_french(application.applicant, previous_academic_year)
        if secondary_curriculum:
            return True

    return False


def reduction_possible(application):
    try:
        if application.offer_year.acronym.endswith("1BA") or \
                application.offer_year.acronym.endswith("2M1") or \
                application.offer_year.acronym.endswith("2MD") or \
                application.offer_year.acronym.endswith("2MA") or \
                application.offer_year.acronym.endswith("2MC") or \
                application.offer_year.acronym.endswith("3D") or \
                application.offer_year.acronym.find("2MS/") != -1:
            return True
    except:  # RelatedObjectDoesNotExist
        return False
    return False


def third_cycle(application):
    try:
        if application.offer_year.acronym.endswith("2MC") or application.offer_year.acronym.endswith("3D"):
            return True
    except:  # RelatedObjectDoesNotExist
        return False
    return False
