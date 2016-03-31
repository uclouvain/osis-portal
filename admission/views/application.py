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


def application_update(request, application_id):
    application = mdl.application.find_by_id(application_id)
    return render(request, "offer_selection.html",
                           {"offers":      None,
                            "offer":       application.offer_year,
                            "application": application})


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
        #answer_question_
        for key, value in request.POST.items():
            if "txt_answer_question_" in key:
                answer = mdl.answer.Answer()
                answer.application = application
                answer.value = value
                # as it's txt_answer we know that it's there is only one option available, (SHORT_INPUT_TEXT, LONG_INPUT_TEXT)
                option_id = key.replace("txt_answer_question_", "")
                answer.option = mdl.option.find_by_id(int(option_id))
                answer.save()
            else:
                if "txt_answer_radio_optid_" in key:
                    #RADIO_BUTTON
                    if "on" == value:
                        answer = mdl.answer.Answer()
                        answer.application = application
                        option_id = key.replace("txt_answer_radio_optid_", "")
                        option =  mdl.option.find_by_id(int(option_id))
                        answer.option = option
                        answer.value = option.value
                        answer.save()

        return render(request, "diploma.html", {"application": application})
