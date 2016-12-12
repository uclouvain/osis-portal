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
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from admission import models as mdl
from admission.models.enums import coverage_access_degree as coverage_access_degree_choices
from admission.models.enums import question_type
from admission.views import common, demande_validation, navigation
from admission.views.common import extra_information
from admission.views.common import get_picture_id, get_id_document
from base import models as mdl_base
from osis_common import models as mdl_osis_common
from reference import models as mdl_reference
from reference.enums import institutional_grade_type as enum_institutional_grade_type


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
        next_tab = request.POST.get('next_tab')

        offer_year_id = request.POST.get('offer_year_id', None)
        application_id = request.POST.get('application_id', None)

        if application_id:
            application = get_object_or_404(mdl.application.Application, pk=application_id)
            secondary_education = mdl.secondary_education.find_by_person(application.applicant)
        else:
            application = mdl.application.init_application(request.user)
            applicant = mdl.applicant.find_by_user(request.user)
            application.applicant = applicant
            secondary_education = mdl.secondary_education.SecondaryEducation()
            secondary_education.applicant = application.applicant

        if secondary_education and secondary_education.academic_year is None:
            secondary_education.academic_year = mdl_base.academic_year.current_academic_year()

        if offer_year_id:
            offer_year = mdl_base.offer_year.find_by_id(offer_year_id)
            application.offer_year = offer_year

        if request.POST.get('national_coverage_degree'):
            if request.POST.get('national_coverage_degree') == "true":
                application.coverage_access_degree = coverage_access_degree_choices.NATIONAL
            else:
                application.coverage_access_degree = coverage_access_degree_choices.NON_NATIONAL

        if request.POST.get('valuation_possible'):
            if request.POST.get('valuation_possible') == "true":
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
        application.application_type = mdl.application.define_application_type(application.coverage_access_degree,
                                                                               request.user)
        if offer_year_id:
            application.save()
        delete_application_assimilation_criteria(application)

        if application.id:
            create_application_assimilation_criteria(application)
            delete_existing_answers(application)
            create_answers(application, request)
    applicant = mdl.applicant.find_by_user(request.user)

    if next_tab:
        return navigation.get_redirection(next_tab, application.id)

    data = {
        'tab_active': next_tab,
        'application': application,
        'picture': get_picture_id(request.user),
        'id_document': get_id_document(request.user),
        'applicant': applicant
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def application_view(request, application_id):
    application = mdl.application.find_by_id(application_id)
    answers = mdl.answer.find_by_application(application_id)
    return render(request, "application.html",
                  {"application": application,
                   "answers": answers})


def applications(request, application_id=None):
    application_list = mdl.application.find_by_user(request.user)
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        # application = mdl.application.init_application(request.user)
        application = None
    applicant = mdl.applicant.find_by_user(request.user)
    person_legal_address = mdl.person_address.find_by_person_type(applicant, 'LEGAL')
    countries = mdl_reference.country.find_all()
    a_domain = None
    a_parent_domain = None
    if application and application.offer_year:
        a_domain = mdl_base.offer_year_domain.find_by_offer_year(application.offer_year)
        a_parent_domain = a_domain.domain.parent
    data = {
        "applications": application_list,
        "grade_choices": enum_institutional_grade_type.INSTITUTIONAL_GRADE_CHOICES,
        "domains": mdl_reference.domain.find_current_domains(),
        'tab_active': navigation.DEMAND_TAB,
        "application": application,
        "local_language_exam_needed": common.is_local_language_exam_needed(request.user),
        "applicant": applicant,
        "person_legal_address": person_legal_address,
        "countries": countries,
        "domain": a_domain,
        "parent_domain": a_parent_domain
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def submission(request, application_id=None):
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    data = {
        'application': application,
        'display_admission_exam': extra_information(application),
        'tab_active': navigation.SUBMISSION_TAB,
        'applications': mdl.application.find_by_user(request.user)
    }
    applicant = mdl.applicant.find_by_user(request.user)
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def application_delete(request, application_id):
    application = mdl.application.find_by_id(application_id)
    application.delete()
    return HttpResponseRedirect(reverse('home'))


def change_application_offer(request, application_id=None):
    application = mdl.application.find_by_id(application_id)
    application.application_type = mdl.application.define_application_type(application.coverage_access_degree,
                                                                           request.user)
    application.save()
    application_list = mdl.application.find_by_user(request.user)
    applicant = mdl.applicant.find_by_user(request.user)
    data = {
        'applications': application_list,
        "grade_choices": enum_institutional_grade_type.INSTITUTIONAL_GRADE_CHOICES,
        "domains": mdl_reference.domain.find_current_domains(),
        'tab_active': navigation.DEMAND_TAB,
        "first": True,
        "application": application,
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def is_local_language_exam_needed(user):
    local_language_exam_needed = False
    applications_list = mdl.application.find_by_user(user)
    for application in applications_list:
        if application.offer_year.grade_type == 'BACHELOR' or \
                        application.offer_year.grade_type.startswith('MASTER') or \
                        application.offer_year.grade_type == 'TRAINING_CERTIFICATE':
            local_language_exam_needed = True
            break
    return local_language_exam_needed


def create_application_assimilation_criteria(application):
    # If application assimilation criteria exists copy them to application assimilation criteria
    applicant_assimilation_criteria_list = mdl.applicant_assimilation_criteria. \
        find_by_applicant(application.applicant)
    for applicant_assimilation_criteria in applicant_assimilation_criteria_list:
        # Copy the applicant_assimilation_criteria
        mdl.application_assimilation_criteria. \
            copy_from_applicant_assimilation_criteria(applicant_assimilation_criteria, application)


def delete_existing_answers(application):
    answers = mdl.answer.find_by_application(application)
    for answer in answers:
        if not answer.option.question.type == question_type.UPLOAD_BUTTON:
            answer.delete()


def create_answers(application, request):
    for key, value in request.FILES.items():
        if "txt_file_" in key:
            save_answer_from_upload(application, key, request)
    for key, value in request.POST.items():
        if "txt_answer_question_" in key:
            save_answer_from_input(application, key, value)
        if "txt_answer_radio_" in key:
            save_answer_from_radio(application, value)
        if "txt_answer_checkbox_" in key:
            save_answer_from_checkbox(application, key, value)
        if "slt_question_" in key:
            save_answer_from_dropdownlist(application, value)
        if "delete_document_file_" in key:
            option_id = key.replace("delete_document_file_", "")
            answer = mdl.answer.find_by_application_and_option(application.id, option_id)
            document_file = mdl_osis_common.document_file.DocumentFile.objects.filter(uuid=answer[0].value)
            answer.delete()
            document_file[0].delete()


def save_answer_from_upload(application, key, request):
    file_selected = request.FILES[key]
    new_document = create_new_document_file(file_selected.content_type,
                                            "offer_selection",
                                            file_selected,
                                            file_selected.name,
                                            request,
                                            file_selected.size)
    option_id = key.replace("txt_file_", "")
    answer = mdl.answer.find_by_application_and_option(application.id, option_id)
    if answer:
        answer = mdl.answer.find_by_id(answer)
        old_document_file = mdl_osis_common.document_file.DocumentFile.objects.filter(uuid=answer.value)
        old_document_file.delete()
        answer.value = new_document.uuid
    else:
        answer = mdl.answer.Answer()
        answer.application = application
        answer.option = mdl.option.find_by_id(int(option_id))
        answer.value = new_document.uuid
    answer.save()


def create_new_document_file(content_type, description, file, file_name, request, size):
    new_document = mdl_osis_common.document_file.DocumentFile(file_name=file_name,
                                                              file=file,
                                                              description=description,
                                                              storage_duration=720,
                                                              application_name='admission',
                                                              content_type=content_type,
                                                              size=size,
                                                              update_by=request.user)
    new_document.save()
    return new_document


def save_answer_from_input(application, key, value):
    option_id = key.replace("txt_answer_question_", "")
    answer = mdl.answer.Answer()
    answer.application = application
    answer.option = mdl.option.find_by_id(int(option_id))
    answer.value = value
    answer.save()


def save_answer_from_radio(application, value):
    option = mdl.option.find_by_id(value)
    create_new_answer(application, option)


def save_answer_from_checkbox(application, key, value):
    if "on" == value:
        option_id = key.replace("txt_answer_checkbox_", "")
        option = mdl.option.find_by_id(int(option_id))
        create_new_answer(application, option)


def save_answer_from_dropdownlist(application, value):
    if value != "0":
        option = mdl.option.find_by_id(value)
        create_new_answer(application, option)


def create_new_answer(application, option):
    answer = mdl.answer.Answer()
    answer.application = application
    answer.option = option
    answer.value = option.value
    answer.save()


def delete_application_assimilation_criteria(application):
    if application.id is None:
        # delete all existing application_assimilation_criteria
        for a in mdl.application_assimilation_criteria.find_by_application(application):
            a.delete()
