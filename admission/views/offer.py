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
from rest_framework import serializers
from admission import models as mdl
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from rest_framework.renderers import JSONRenderer


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class OfferSerializer(serializers.ModelSerializer):
    class Meta:
        model = mdl.offer_year.OfferYear
        fields = ('id', 'acronym','title', 'title_international')


def search(request):
    level = request.GET['level']
    domain = request.GET['domain']
    offers = mdl.offer_year.search(level, domain)
    serializer = OfferSerializer(offers, many=True)
    return JSONResponse(serializer.data)


def offer_selection(request):
    offers = None
    application = mdl.application.find_by_user(request.user)
    grade_choices = mdl.grade_type.GRADE_CHOICES
    return render(request, "offer_selection.html",
                          {"gradetypes":  mdl.grade_type.find_all(),
                           "domains":     mdl.domain.find_all(),
                           "offers":      offers,
                           "offer":       None,
                           "application": application,
                           "grade_choices": grade_choices})


def _get_offer_type(request):
    offer_type=None

    if request.POST.get('bachelor_type'):
        offer_type = request.POST['bachelor_type']
    if request.POST.get('master_type'):
        offer_type = request.POST['master_type']
    if request.POST.get('doctorate_type'):
        offer_type = request.POST['doctorate_type']
    if offer_type:
        return get_object_or_404(mdl.grade_type.GradeType, pk=offer_type)
    return None


def _get_domain(request):
    domain_id = request.POST.get('domain')
    domain = None
    if domain_id:
        domain = get_object_or_404(mdl.domain.Domain, pk=domain_id)
    return domain


def save_offer_selection(request):
    if request.method =='POST' and 'save' in request.POST:
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
                print(value)
                #answer to save
                # answer = mdl.answer.Answer()
                # answer.application = application
                # answer.value = value
                # answer.option #pas trop sûre pour l'option
                # answer.save()

        return render(request, "diploma.html", {"application": application})


def selection_offer(request, offer_id):
    offer_year = get_object_or_404(mdl.offer_year.OfferYear, pk=offer_id)
    grade = _get_offer_type(request)
    domain = _get_domain(request)

    return render(request, "offer_selection.html",
                           {"gradetypes":  mdl.grade_type.find_all(),
                            "domains":     mdl.domain.find_all(),
                            "offers":      None,
                            "offer":       offer_year,
                            "offer_type":  grade,
                            "domain":      domain})
