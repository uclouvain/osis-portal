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
from django.forms import formset_factory

from attribution.views import teaching_load
from base import models as mdl_base
from attribution.forms import AttributionForm


def home(request):
    a_person = mdl_base.person.find_by_global_id('1234567890')
    AttributionFormSet = formset_factory(AttributionForm, extra=0)
    attributions_representation = teaching_load.list_teaching_load_attribution_representation(a_person)
    initial_data = []
    year = None
    for attribution in attributions_representation:
        initial_data.append({'acronym': attribution.acronym,
                             'year':    attribution.year})
        year = attribution.year
    formset = AttributionFormSet(initial=initial_data)

    return render(request, "teaching_load.html", {
        'user': a_person.user,
        'attributions_representation': attributions_representation,
        'formset': formset,
        'year': year})
