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
from admission.views.object_application import Object_application

ALERT_MANDATORY_FIELD = "Champ obligatoire"



def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                           {"offers":      None,
                            "offer":       application.offer_year,
                            "application": application})


def profile_confirmed(request):
    return render(request, "profile_confirmed.html")


def save_application_offer(request):
    if request.method == 'POST' and 'save' in request.POST:
        offer_year = None
        offer_year_id = request.POST.get('offer_year_id')

        application_id = request.POST.get('application_id')

        if application_id:
            application = get_object_or_404(mdl.application.Application, pk=application_id)
        else:
            application = mdl.application.Application()
            person_application = mdl.person.find_by_user(request.user)
            application.person = person_application

        if offer_year_id:
            offer_year = mdl.offer_year.find_by_id(offer_year_id)
            if offer_year.grade_type:
                if offer_year.grade_type.grade == 'DOCTORATE':
                    application.doctorate = True
                else:
                    application.doctorate = False

        application.offer_year = offer_year
        application.save()
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
        print('1')
        return render(request, "diploma.html", {"application": application,
                                                "academic_years": mdl.academic_year.find_academic_years(),
                                                "object_application": geto()})


def geto():
    print('geto')
    object_application=Object_application()
    object_application.rdb_diploma_sec = True
    object_application.academic_year = mdl.academic_year.find_by_id(3)
    object_application.rdb_belgian_foreign = True
    object_application.rdb_belgian_community = "FRENCH"
    print(object_application.rdb_diploma_sec)
    return object_application


def application_view(request, application_id):
    application = mdl.application.find_by_id(application_id)
    answers = mdl.answer.find_by_application(application_id)
    return render(request, "application.html",
                           {"application": application,
                            "answers": answers})


def diploma_save(request, application_id):
    print('diploma_save')
    next_step = False
    previous_step = False
    save_step = False
    validation_messages={}
    academic_years = mdl.academic_year.find_academic_years()
    if request.POST:
        if 'bt_next_step_up' in request.POST or 'bt_next_step_down' in request.POST:
             next_step = True
        else:
            if 'bt_previous_step_up' in request.POST or 'bt_previous_step_down' in request.POST:
                previous_step = True
            else:
                if 'bt_save_up' in request.POST or 'bt_save_down' in request.POST:
                    save_step = True



    application = get_object_or_404(mdl.application.Application, pk=application_id)
    if next_step:
        objet_application = Object_application()
        object_application =geto()
        #Check if all the necessary fields have been filled
        is_valid, validation_messages = validate_fields_form(request)
        if is_valid:
            return render(request, "curriculum.html", {"application": application,"object_application": geto()})
        else:
            return render(request, "diploma.html", {"application": application,
                                                    "validation_messages":validation_messages,
                                                    "academic_years": academic_years,
                                                    "object_application": geto()})
    else:
        return render(request, "diploma.html", {"application": application,
                                                "validation_messages":validation_messages,
                                                "academic_years": academic_years,
                                                "object_application": geto()})


def validate_fields_form(request):
    print('valide_fields_form')
    validation_messages = {}
    is_valid = True
    academic_year = None
    if request.POST.get('rdb_diploma_sec'):
        print(request.POST.get('rdb_diploma_sec'))
        if request.POST.get('rdb_diploma_sec') == 'true':
            #secondary education diploma
            if request.POST.get('academic_year') is None:
                validation_messages['academic_year'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                academic_year = mdl.academic_year.find_by_id(int(request.POST.get('academic_year')))
            if request.POST.get('rdb_belgian_foreign') is None:
                validation_messages['rdb_belgian_foreign'] = ALERT_MANDATORY_FIELD
                is_valid = False
            else:
                if request.POST.get('rdb_belgian_foreign') == 'true':
                    #Belgian diploma
                    if request.POST.get('rdb_belgian_community') is None:
                        validation_messages['academic_year'] = ALERT_MANDATORY_FIELD
                        is_valid = False
                    else:
                        if request.POST.get('rdb_belgian_community') == 'FRENCH':
                            #diploma of the French community
                            if academic_year.year < 1994:
                                if request.POST.get('rdb_daes') is None:
                                    validation_messages['rdb_daes'] = ALERT_MANDATORY_FIELD
                                    is_valid = False
                        else:
                            if request.POST.get('rdb_belgian_community') == 'DUTCH':
                                #diploma of the Dutch community
                                if academic_year.year < 1992:
                                    if request.POST.get('rdb_daes') is None:
                                        validation_messages['rdb_daes'] = ALERT_MANDATORY_FIELD
                                        is_valid = False

                    if request.POST.get('school') is None \
                        and ((request.POST.get('CESS_other_school_name') is None or len(request.POST.get('CESS_other_school_name'))==0)
                             and (request.POST.get('CESS_other_school_city') is None or len(request.POST.get('CESS_other_school_city'))==0)
                             and (request.POST.get('CESS_other_school_postal_code') is None or len(request.POST.get('CESS_other_school_postal_code'))==0)):
                        validation_messages['school'] = "Il faut préciser un établissement scolaire"
                        is_valid = False
                    if request.POST.get('rdb_school_belgian_community') == 'FRENCH':
                        #Belgian school
                        if request.POST.get('rdb_education_transition_type') is None and request.POST.get('rdb_education_technic_type') and request.POST.get('other_education'):
                            validation_messages['pnl_teaching_type'] = "Il faut préciser un type d'enseignement"
                            is_valid = False

                if academic_year.year < 1994:
                    if request.POST.get('repeated_grade') is None:
                        validation_messages['repeated_grade'] = ALERT_MANDATORY_FIELD
                        is_valid = False
                    if request.POST.get('re_orientation') is None:
                        validation_messages['re_orientation'] = ALERT_MANDATORY_FIELD
                        is_valid = False
                if request.POST.get('result') is None:
                    validation_messages['result'] = ALERT_MANDATORY_FIELD
                    is_valid = False
                #validation for the uploaded file

    else:
        validation_messages['rdb_diploma_sec'] = ALERT_MANDATORY_FIELD
        is_valid = False

    return is_valid, validation_messages


def curriculum_read(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "curriculum.html", {"application": application})


def curriculum_save(request, application_id):
    application = mdl.application.find_by_id(application_id)
    print('2')
    return render(request, "diploma.html", {"application": application,
                                            "academic_years": mdl.academic_year.find_academic_years(),
                                            "object_application" : geto()})

