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
import datetime

from django.conf import settings
from django.forms import formset_factory
from django.shortcuts import render

from base import models as mdl_base
from attribution import models as mdl_attribution
from base.models.enums import component_type
from attribution.forms import AttributionForm
from django.contrib.auth.decorators import login_required


MAIL_TO = 'mailto:'
STUDENT_LIST_EMAIL_END = '@listes-student.uclouvain.be'


@login_required
def home(request):
    return by_year(request, datetime.datetime.now().year)


def get_person(a_user):
    return mdl_base.person.find_by_user(a_user)


def get_title_uppercase(learning_unit_year):
    if learning_unit_year and learning_unit_year.title:
        return learning_unit_year.title.upper()
    return ''


def get_attribution_allocation_charge(a_tutor, a_learning_unit_year, a_component_type):
    attribution_list = mdl_attribution.attribution.search(a_tutor, a_learning_unit_year)
    tot_allocation_charge = 0
    for an_attribution in attribution_list:
        a_learning_unit_components = mdl_base.learning_unit_component.search(a_learning_unit_year, a_component_type)
        for a_learning_unit_component in a_learning_unit_components:
            attribution_charges = mdl_attribution.attribution_charge.search(an_attribution, a_learning_unit_component)
            for attribution_charge in attribution_charges:
                tot_allocation_charge += attribution_charge.allocation_charge

    return tot_allocation_charge


def sum_learning_unit_year_duration(a_learning_unit_year):
    tot_duration = 0
    for learning_unit_component in mdl_base.learning_unit_component.search(a_learning_unit_year, None):
        if learning_unit_component.duration:
            tot_duration += learning_unit_component.duration
    return tot_duration


def sum_learning_unit_year_allocation_charge(a_tutor, a_learning_unit_year):
    return get_attribution_allocation_charge(a_tutor, a_learning_unit_year, None)


def calculate_format_percentage_allocation_charge(a_tutor, a_learning_unit_year):
    duration = sum_learning_unit_year_duration(a_learning_unit_year)
    if duration > 0:
        percentage = sum_learning_unit_year_allocation_charge(a_tutor, a_learning_unit_year) * 100 / duration
        return "%0.2f" % (percentage,)
    return None


def get_email_students(an_acronym):
    if an_acronym and len(an_acronym.strip()) > 0:
        return "{0}{1}{2}".format(MAIL_TO, an_acronym.lower(), STUDENT_LIST_EMAIL_END)
    return None


def get_schedule_url(an_acronym):
    if an_acronym and len(an_acronym.strip()) > 0:
        return settings.ADE_MAIN_URL.format(settings.ADE_PROJET_NUMBER, an_acronym.lower())
    return None


def list_attributions(a_person, an_academic_year):
    a_tutor = mdl_base.tutor.find_by_person(a_person)
    return mdl_attribution.attribution.find_by_tutor_year_order_by_acronym_fonction(a_tutor, an_academic_year)


def list_teaching_load_attribution_representation(a_person, an_academic_year):
    list = []
    a_tutor = mdl_base.tutor.find_by_person(a_person)
    for an_attribution in list_attributions(a_person, an_academic_year):
        a_learning_unit_year = an_attribution.learning_unit_year
        teaching_load_attribution_representation = {
            'acronym': a_learning_unit_year.acronym,
            'title': get_title_uppercase(a_learning_unit_year),
            'lecturing_allocation_charge': "%0.2f" % (get_attribution_allocation_charge(a_tutor,
                                                                                        a_learning_unit_year,
                                                                                        component_type.LECTURING),),
            'practice_allocation_charge': "%0.2f" % (get_attribution_allocation_charge(a_tutor,
                                                                                       a_learning_unit_year,
                                                                                       component_type.PRACTICAL_EXERCISES),),
            'percentage_allocation_charge': calculate_format_percentage_allocation_charge(a_tutor, a_learning_unit_year),
            'weight': a_learning_unit_year.weight,
            'url_schedule': get_schedule_url(a_learning_unit_year.acronym),
            'url_students_list_email': get_email_students(a_learning_unit_year.acronym),
            'function': an_attribution.function,
            'year': a_learning_unit_year.academic_year.year}
        list.append(teaching_load_attribution_representation)
    return list


def by_year(request, year):
    a_person = mdl_base.person.find_by_user(request.user)
    an_academic_year = None
    if year:
        an_academic_year = mdl_base.academic_year.find_by_year(year)
    attributions = list_teaching_load_attribution_representation(a_person, an_academic_year)

    return render(request, "teaching_load.html", {
        'user': a_person.user,
        'attributions': attributions,
        'formset': set_formset_years(a_person),
        'year': int(year)})


def get_attribution_years(a_person):
    a_tutor = mdl_base.tutor.find_by_person(a_person)
    return list(mdl_attribution.attribution.find_distinct_years(a_tutor))


def set_formset_years(a_person):
    AttributionFormSet = formset_factory(AttributionForm, extra=0)
    initial_data = []
    for yr in get_attribution_years(a_person):
        initial_data.append({'year': yr})

    return AttributionFormSet(initial=initial_data)




