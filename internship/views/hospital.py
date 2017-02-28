# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from django.contrib.auth.decorators import login_required, permission_required
from base.views import layout
from internship.forms.form_search_hospital import SearchHospitalForm
from internship import models as mdl_internship


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_hospitals_list(request):
    cities = mdl_internship.organization_address.get_all_cities()
    hospitals = []

    if request.method == 'POST':
        form = SearchHospitalForm(cities, request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            city = form.cleaned_data['city']
            hospitals = get_hospitals(name=name, city=city)

    else:
        form = SearchHospitalForm(cities)

    return layout.render(request, "hospitals.html", {'search_form': form,
                                                     'hospitals': hospitals})


def get_hospitals(name="", city=""):
    if name:
        organizations = mdl_internship.organization.search(name)
    else:
        organizations = mdl_internship.organization.Organization.objects.all()
    hospitals = []
    for organization in organizations:
        organization_address = mdl_internship.organization_address.get_by_organization(organization)
        if not city or organization_address.city == city:
            hospitals.append((organization, organization_address))
    return hospitals




