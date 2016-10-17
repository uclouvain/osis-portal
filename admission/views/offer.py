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
from django.shortcuts import render, get_object_or_404
from rest_framework import serializers
from rest_framework.renderers import JSONRenderer

from admission import models as mdl
from reference import models as mdl_reference
from admission.views.common import extra_information, validated_extra, get_picture_id
from base import models as mdl_base
from reference.enums import assimilation_criteria as assimilation_criteria_enum
from admission.views import assimilation_criteria as assimilation_criteria_view
from admission.views.common import  get_assimilation_documents_existing


class JSONResponse(HttpResponse):
    def __init__(self, data, **kwargs):
        content = JSONRenderer().render(data)
        kwargs['content_type'] = 'application/json'
        super(JSONResponse, self).__init__(content, **kwargs)


class OfferSerializer(serializers.ModelSerializer):
    institutional_grade_type = serializers.SerializerMethodField('get_grade_type')

    class Meta:
        model = mdl_base.offer_year.OfferYear
        fields = ('id', 'acronym', 'title', 'title_international', 'grade_type', 'subject_to_quota',
                  'institutional_grade_type')

    def get_grade_type(self, obj):
        return obj.grade_type.institutional_grade_type


def search(request):
    level = request.GET['level']
    domain = request.GET['domain']
    serializer = OfferSerializer([], many=True)
    if level != 'undefined' and domain != 'undefined':
        offer_year_domains = mdl_base.offer_year_domain.search(level, domain)
        list_offer_years = []
        for offer_year_domain in offer_year_domains:
            list_offer_years.append(offer_year_domain.offer_year)
        serializer = OfferSerializer(list_offer_years, many=True)
    return JSONResponse(serializer.data)


def find_by_id(request):
    offer_year_id = request.GET['offer']
    offer_year = mdl_base.offer_year.find_by_id(offer_year_id)
    serializer = OfferSerializer(offer_year)
    return JSONResponse(serializer.data)


def offer_selection(request):
    offers = None

    grade_choices = mdl_reference.grade_type.find_all()
    applicant = mdl.applicant.find_by_user(request.user)
    same_addresses = True
    person_contact_address = mdl.person_address.find_by_person_type(applicant, 'CONTACT')
    if person_contact_address:
        same_addresses = False
    application = mdl.application.init_application(request.user)
    applicant_assimilation_criteria = mdl.applicant_assimilation_criteria.find_by_applicant(applicant.id)
    return render(request, "admission_home.html",
                  {"gradetypes": mdl_reference.grade_type.find_all(),
                   "domains": mdl_reference.domain.find_current_domains(),
                   "offers": offers,
                   "offer": None,
                   "application": application,
                   "grade_choices": grade_choices,
                   'tab_active': 0,
                   'applicant': applicant,
                   'person_contact_address': person_contact_address,
                   'person_legal_address': mdl.person_address.find_by_person_type(applicant, 'LEGAL'),
                   'countries': mdl_reference.country.find_all(),
                   'assimilation_criteria': assimilation_criteria_enum.ASSIMILATION_CRITERIA_CHOICES,
                   'applicant_assimilation_criteria': applicant_assimilation_criteria,
                   'assimilation_basic_documents': assimilation_criteria_view.find_assimilation_basic_documents(),
                   'assimilation_documents_existing': get_assimilation_documents_existing(request.user),
                   'same_addresses': same_addresses,
                   'application': application})


def _get_offer_type(request):
    offer_type = None

    if request.POST.get('bachelor_type'):
        offer_type = request.POST['bachelor_type']
    if request.POST.get('master_type'):
        offer_type = request.POST['master_type']
    if request.POST.get('doctorate_type'):
        offer_type = request.POST['doctorate_type']
    if offer_type:
        return get_object_or_404(mdl_reference.grade_type.GradeType, pk=offer_type)
    return None


def _get_domain(request):
    domain_id = request.POST.get('domain')
    domain = None
    if domain_id:
        domain = get_object_or_404(mdl_reference.domain.Domain, pk=domain_id)
    return domain


def selection_offer(request, offer_id):
    offer_year = get_object_or_404(mdl_base.offer_year.OfferYear, pk=offer_id)
    grade = _get_offer_type(request)
    domain = _get_domain(request)

    return render(request, "offer_selection.html",
                           {"gradetypes":  mdl_reference.grade_type.find_all(),
                            "domains":     mdl_reference.domain.find_current_domains(),
                            "offers":      None,
                            "offer":       offer_year,
                            "offer_type":  grade,
                            "domain":      domain})


def demande_update(request, application_id=None):
    offers = None
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    grade_choices = mdl_reference.grade_type.find_all()
    an_applicant = mdl.applicant.find_by_user(request.user)
    secondary_education = mdl.secondary_education.find_by_person(an_applicant)
    person_legal_address = mdl.person_address.find_by_person_type(an_applicant, 'LEGAL')
    person_contact_address = mdl.person_address.find_by_person_type(an_applicant, 'CONTACT')
    return render(request, "admission_home.html",
                  {"gradetypes":             mdl_reference.grade_type.find_all(),
                   "domains":                mdl_reference.domain.find_current_domains(),
                   "offers":                 offers,
                   "offer":                  None,
                   "application":            application,
                   "grade_choices":          grade_choices,
                   'tab_active':             0,
                   "tab_demande_active":     0,
                   "display_admission_exam": extra_information(application),
                   "validated_extra":        validated_extra(secondary_education, application),
                   "picture": get_picture_id(request.user),
                   "id_document": get_id_document(request.user),
                   'person_legal_address': person_legal_address,
                   'person_contact_address': person_contact_address})




