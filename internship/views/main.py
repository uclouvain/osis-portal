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
from django.shortcuts import redirect
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
def view_internship_selection(request, internship_id="1", speciality_id="-1"):
    NUMBER_NON_MANDATORY_INTERNSHIPS = 6
    student = mdl_base.student.find_by_user(request.user)

    speciality = mdl_internship.internship_speciality.find_by_id(speciality_id)
    internships_offers = mdl_internship.internship_offer.find_by_speciality(speciality)

    speciality_form = SpecialityForm()
    offer_preference_formset = formset_factory(OfferPreferenceForm, formset=OfferPreferenceFormSet,
                                               extra=internships_offers.count())
    formset = offer_preference_formset()

    if request.method == 'POST':
        formset = offer_preference_formset(request.POST)
        if formset.is_valid():
            remove_previous_choices(student, internship_id)
            save_student_choices(formset, student, int(internship_id), speciality)

    zipped_data = None
    if internships_offers:
        zipped_data = zip(internships_offers, formset)

    return layout.render(request, "internship_selection.html",
                         {"number_non_mandatory_internships": range(1, NUMBER_NON_MANDATORY_INTERNSHIPS + 1),
                          "speciality_form": speciality_form,
                          "formset": formset,
                          "offers_forms": zipped_data,
                          "intern_id": int(internship_id)})


@login_required
@permission_required('base.is_student', raise_exception=True)
def assign_speciality_for_internship(request, internship_id):
    speciality_id = None
    if request.method == "POST":
        speciality_form = SpecialityForm(request.POST)
        if speciality_form.is_valid():
            speciality_selected = speciality_form.cleaned_data["speciality"]
            speciality_id = speciality_selected.id
    return redirect("select_internship_speciality", internship_id=internship_id, speciality_id=speciality_id)


def remove_previous_choices(student, internship_id):
    previous_choices = mdl_internship.internship_choice.search(student, internship_id)
    if previous_choices:
        previous_choices.delete()


def save_student_choices(formset, student, internship_id, speciality):
    for form in formset:
        if form.cleaned_data:
            offer_pk = form.cleaned_data["offer"]
            preference_value = int(form.cleaned_data["preference"])
            if has_been_selected(preference_value):
                offer = mdl_internship.internship_offer.find_by_pk(offer_pk)
                internship_choice = mdl_internship.internship_choice.InternshipChoice(student=student,
                                                                                      organization=offer.organization,
                                                                                      speciality=speciality,
                                                                                      choice=preference_value,
                                                                                      internship_choice=internship_id,
                                                                                      priority=False)
                internship_choice.save()


def has_been_selected(preference_value):
    return bool(preference_value)

