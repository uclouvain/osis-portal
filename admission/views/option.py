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
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer
from admission import models as mdl
from admission.models.answer import find_by_option, find_by_user_and_option
from base import models as mdl_base


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


def find_by_offer(request):
    offer_yr_id = request.GET['offer']

    offer_yr = mdl_base.offer_year.find_by_id(offer_yr_id)
    questions = mdl.question.find_form_ordered_questions(offer_yr)
    options = []
    question_list = []
    if questions:
        for question in questions:
            options_by_question = mdl.option.find_options_by_question_id(question.id)
            for o in options_by_question:
                options.append(o)

        for option in options:
            options_max_number = 0
            if option.question.type == 'RADIO_BUTTON' or option.question.type == 'CHECKBOX' \
                    or option.question.type == 'DROPDOWN_LIST':
                options_max_number = mdl.option.find_number_options_by_question_id(option.question.id)
            answers = find_by_user_and_option(request.user, option.id)
            answer = ""
            if answers.exists():
                answer = answers[0].value
            question_list.append({'answer': answer,
                                  'option_id': option.id,
                                  'option_label': option.label,
                                  'option_description': option.description,
                                  'option_value': option.value,
                                  'option_order': option.order,
                                  'question_id': option.question.id,
                                  'question_label': option.question.label,
                                  'question_type': option.question.type,
                                  'question_required': option.question.required,
                                  'question_description': option.question.description,
                                  'options_max_number': options_max_number})
    return JSONResponse(question_list)
