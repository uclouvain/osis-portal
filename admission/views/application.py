##############################################################################
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
from django.shortcuts import render, get_object_or_404
from reference import models as mdl_reference

from datetime import datetime
from admission.views.common import home, get_picture_id, get_id_document
from functools import cmp_to_key
import locale
from django.utils.translation import ugettext_lazy as _
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from admission.views.common import extra_information
from admission.views import demande_validation
from admission.views import tabs
from admission.views import tabs


def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                  {"offers": None,
                   "offer": application.offer_year,
                   "application": application})


def profile_confirmed(request):
    return render(request, "profile_confirmed.html")


def save_application_offer(request):
    next_tab = None
    application = None

    if request.method == 'POST':
        new_application = False
        next_tab = request.POST.get('next_tab')

        offer_year = None
        offer_year_id = request.POST.get('offer_year_id')

        application_id = request.POST.get('application_id')

        if application_id == 'None':
            application_id = None
        if application_id:
            application = get_object_or_404(mdl.application.Application, pk=application_id)
            secondary_education = mdl.secondary_education.find_by_person(application.applicant)
        else:
            application = mdl.application.init_application(request.user)
            new_application = True
            person_application = mdl.applicant.find_by_user(request.user)
            application.applicant = person_application
            secondary_education = mdl.secondary_education.SecondaryEducation()
            secondary_education.applicant = application.applicant

        if secondary_education and secondary_education.academic_year is None:
            secondary_education.academic_year = mdl.academic_year.current_academic_year()

        if offer_year_id:
            offer_year = mdl.offer_year.find_by_id(offer_year_id)

        application.offer_year = offer_year

        if request.POST.get('rdb_offer_belgiandegree'):
            if request.POST.get('rdb_offer_belgiandegree') == "true":
                application.national_degree = True
            else:
                application.national_degree = False
        if request.POST.get('rdb_offer_vae'):
            if request.POST.get('rdb_offer_vae') == "true":
                application.valuation_possible = True
            else:
                application.valuation_possible = False
        if request.POST.get('rdb_offer_samestudies'):
            if request.POST.get('rdb_offer_samestudies') == "true":
                application.started_similar_studies = True
            else:
                application.started_similar_studies = False
        if request.POST.get('rdb_offer_valuecredits'):
            if request.POST.get('rdb_offer_valuecredits') == "true":
                application.credits_to_value = True
            else:
                application.credits_to_value = False
        if request.POST.get('rdb_offer_sameprogram'):
            if request.POST.get('rdb_offer_sameprogram') == "true":
                application.applied_to_sameprogram = True
            else:
                application.resident = False
        if request.POST.get('rdb_offer_resident'):
            if request.POST.get('rdb_offer_resident') == "true":
                application.resident = True
            else:
                application.resident = False
        if request.POST.get('txt_offer_lottery'):
            application.raffle_number = request.POST.get('txt_offer_lottery')

        application.save()

        if new_application is False:
            # delete all existing application_assimilation_criteria
            for a in mdl.application_assimilation_criteria.find_by_application(application):
                a.delete()

        # If application assimilation criteria exists copy them to application assimilation criteria

        applicant_assimilation_criteria_list = mdl.applicant_assimilation_criteria.\
            find_by_applicant(application.applicant)
        for applicant_assimilation_criteria in applicant_assimilation_criteria_list:
            # Copy the applicant_assimilation_criteria
            mdl.application_assimilation_criteria.\
                copy_from_applicant_assimilation_criteria(applicant_assimilation_criteria, application)
        # answer_question_
        for key, value in request.POST.items():
            if "txt_answer_question_" in key:
                answer = mdl.answer.Answer()
                answer.application = application
                answer.value = value
                # as it's txt_answer we know that it's there is only one option available,
                # (SHORT_INPUT_TEXT, LONG_INPUT_TEXT)
                option_id = key.replace("txt_answer_question_", "")
                answer.option = mdl.option.find_by_id(int(option_id))
                answer.save()
            else:
                if "txt_answer_radio_chck_optid_" in key:

                    # RADIO_BUTTON
                    if "on" == value:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option_id = key.replace("txt_answer_radio_chck_optid_", "")
                        option = mdl.option.find_by_id(int(option_id))
                        answer.option = option
                        answer.value = option.value
                        answer.save()
                else:
                    if "slt_question_" in key:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option = mdl.option.find_by_id(value)
                        answer.option = option
                        answer.value = option.value
                        answer.save()
    applicant = mdl.applicant.find_by_user(request.user)

    if next_tab == "0":
        return HttpResponseRedirect(reverse('profile', args=(application.id,)))

    if next_tab == "1":
        return HttpResponseRedirect(reverse('applications', args=(application.id,)))

    if next_tab == "2":
        return HttpResponseRedirect(reverse('diploma_update', args=(application.id,)))

    if next_tab == "3":
        return HttpResponseRedirect(reverse('curriculum_update', args=(application.id,)))

    if next_tab == "4":
        return HttpResponseRedirect(reverse('accounting_update', args=(application.id,)))

    if next_tab == "5":
        return HttpResponseRedirect(reverse('sociological_survey', args=(application.id,)))

    if next_tab == "6":
        return HttpResponseRedirect(reverse('attachments', args=(application.id,)))

    if next_tab == "7":
        return HttpResponseRedirect(reverse('submission', args=(application.id,)))
    data = {
        'tab_active': next_tab,
        'application': application,
        'picture': get_picture_id(request.user),
        'id_document': get_id_document(request.user),
        'applicant': applicant
    }
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return render(request, "admission_home.html", data)


def application_view(request, application_id):
    application = mdl.application.find_by_id(application_id)
    answers = mdl.answer.find_by_application(application_id)
    return render(request, "application.html",
                  {"application": application,
                   "answers": answers})


def applications(request, application_id=None):
    tab_status = tabs.init(request)
    application_list = mdl.application.find_by_user(request.user)
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    data = {
        'applications': application_list,
        'grade_choices': mdl_reference.grade_type.GRADE_CHOICES,
        'domains': mdl_reference.domain.find_all_domains(),
        'tab_active': 1,
        'application': application,
        'tab_profile': tab_status['tab_profile'],
        'tab_applications': tab_status['tab_applications'],
        'tab_diploma': tab_status['tab_diploma'],
        'tab_curriculum': tab_status['tab_curriculum'],
        'tab_accounting': tab_status['tab_accounting'],
        'tab_sociological': tab_status['tab_sociological'],
        'tab_attachments': tab_status['tab_attachments'],
        'tab_submission': tab_status['tab_submission'],
        "local_language_exam_needed": is_local_language_exam_needed(request.user)
    }
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return render(request, "admission_home.html", data)


def submission(request, application_id=None):
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    tab_status = tabs.init(request)
    data = {
        'application': application,
        'display_admission_exam': extra_information(request, application),
        'tab_active': 7,
        'tab_profile': tab_status['tab_profile'],
        'tab_applications': tab_status['tab_applications'],
        'tab_diploma': tab_status['tab_diploma'],
        'tab_curriculum': tab_status['tab_curriculum'],
        'tab_accounting': tab_status['tab_accounting'],
        'tab_sociological': tab_status['tab_sociological'],
        'tab_attachments': tab_status['tab_attachments'],
        'tab_submission': tab_status['tab_submission'],
        'applications': mdl.application.find_by_user(request.user)
    }
    applicant = mdl.applicant.find_by_user(request.user)
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return render(request, "admission_home.html", data)


def application_delete(request, application_id):
    application = mdl.application.find_by_id(application_id)
    application.delete()
    return HttpResponseRedirect(reverse('home'))


def change_application_offer(request, application_id=None):
    application = mdl.application.find_by_id(application_id)
    # application.offer_year = None  # Ici on ne peut pas mettre None
    application.save()
    application_list = mdl.application.find_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    data = {
        'applications': application_list,
        'grade_choices': mdl_reference.grade_type.GRADE_CHOICES,
        'domains': mdl_reference.domain.find_all_domains(),
        'tab_active': 1,
        'first': True,
        'application': application,
    }
    data.update(demande_validation.get_validation_status(application, applicant, request.user))
    return render(request, "admission_home.html", data)


def is_local_language_exam_needed(user):
    local_language_exam_needed = False
    applications_list = mdl.application.find_by_user(user)
    for application in applications_list:
        if application.offer_year.grade_type.grade == 'BACHELOR' or \
                        application.offer_year.grade_type.grade == 'MASTER' or \
                        application.offer_year.grade_type.grade == 'TRAINING_CERTIFICATE':
            local_language_exam_needed = True
            break
    return local_language_exam_needed
