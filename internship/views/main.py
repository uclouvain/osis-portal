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
import base.models as mdl_base
import internship.models as mdl_internship
from internship.forms.form_select_speciality import SpecialityForm
from internship.forms.form_offer_preference import OfferPreferenceFormSet, OfferPreferenceForm
from django.forms import formset_factory


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_internship_home(request):

    return layout.render(request, "internship_home.html")


@login_required
@permission_required('base.is_student', raise_exception=True)
def view_internship_selection(request, internship_id="1"):
    NUMBER_NON_MANDATORY_INTERNSHIPS = 6

    internships_offers = None

    speciality_form = SpecialityForm()
    offer_preference_formset = formset_factory(OfferPreferenceForm, formset=OfferPreferenceFormSet, extra=2)
    formset = offer_preference_formset()

    if request.method == 'POST':
        if "select_speciality" in request.POST:
            speciality_form = SpecialityForm(request.POST)
            if speciality_form.is_valid():
                speciality_selected = speciality_form.cleaned_data["speciality"]
                internships_offers = mdl_internship.internship_offer.find_by_speciality(speciality_selected)
        elif "select_offers" in request.POST:
            formset = offer_preference_formset(request.POST)
            if formset.is_valid():
                student = mdl_base.student.find_by_user(request.user)
                save_student_choices(formset, student, int(internship_id))

    zipped_data = None
    if internships_offers:
        zipped_data = zip(internships_offers, formset)
    return layout.render(request, "internship_selection.html",
                         {"number_non_mandatory_internships": range(1, NUMBER_NON_MANDATORY_INTERNSHIPS + 1),
                          "speciality_form": speciality_form,
                          "formset": formset,
                          "offers_forms": zipped_data,
                          "internship_id": int(internship_id)})


def save_student_choices(formset, student, internship_id):
    for form in formset:
        if form.cleaned_data:
            offer_pk = form.cleaned_data["offer"]
            preference_value = form.cleaned_data["preference"]
            if has_been_selected(preference_value):
                offer = mdl_internship.internship_offer.find_by_pk(offer_pk)
                internship_choice = mdl_internship.internship_choice.InternshipChoice(student=student,
                                                                                      organization=offer.organization,
                                                                                      choice=preference_value,
                                                                                      internship_choice=internship_id,
                                                                                      priority=False)
                internship_choice.save()


def has_been_selected(preference_value):
    return preference_value != 0

