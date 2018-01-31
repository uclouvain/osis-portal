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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.forms import formset_factory
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _
from django.views.decorators.http import require_POST

import base.models as mdl
import internship.models as mdl_int
from base.views import layout
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.decorators.cohort_view_decorators import redirect_if_subscription_not_allowed
from internship.decorators.global_view_decorators import redirect_if_multiple_registrations
from internship.forms.form_offer_preference import OfferPreferenceFormSet, OfferPreferenceForm
from internship.forms.form_select_speciality import SpecialityForm


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
@redirect_if_subscription_not_allowed
def view_internship_selection(request, cohort_id, internship_id=-1, speciality_id=-1):
    cohort = mdl_int.cohort.Cohort.objects.get(pk=cohort_id)

    if not mdl_int.internship_offer.cohort_open_for_selection(cohort):
        return layout.render(request, "internship_selection_closed.html", {'cohort': cohort})

    if int(internship_id) < 1:
        current_internship = mdl_int.internship.find_by_cohort(cohort).first()
        return redirect(view_internship_selection, cohort_id=cohort_id, internship_id=current_internship.id)

    internships = mdl_int.internship.find_by_cohort(cohort).order_by("speciality__name", "name")

    specialities = mdl_int.internship_speciality.find_selectables(cohort).order_by("name")
    current_internship = internships.get(pk=internship_id)
    student = mdl.student.find_by_user(request.user)
    internship_choices = mdl_int.internship_choice.InternshipChoice.objects.filter(speciality_id__in=specialities,
                                                                                   internship=current_internship,
                                                                                   student=student)
    current_choice = internship_choices.filter(internship=current_internship).first()

    if current_choice is not None and int(speciality_id) < 0:
        speciality_id = current_choice.speciality_id

    if current_internship.speciality is not None:
        speciality = current_internship.speciality
    else:
        speciality = specialities.filter(pk=speciality_id).first()
        non_mandatory_offers = mdl_int.internship_offer.find_selectable_by_cohort(cohort=cohort)
        speciality_ids = non_mandatory_offers.values_list("speciality_id", flat=True)
        specialities = specialities.filter(id__in=speciality_ids).order_by("name")

    selectable_offers = mdl_int.internship_offer.find_selectable_by_speciality_and_cohort(speciality, cohort)

    formset = _handle_formset_to_save(request, selectable_offers, student, current_internship, speciality)

    first_choices_by_organization = get_first_choices_by_organization(speciality)
    offers_forms = zip_offers_formset_and_first_choices(formset, selectable_offers, first_choices_by_organization)

    return layout.render(request, "internship_selection.html",
                         {"internships": internships,
                          "current_internship": current_internship,
                          "speciality_form": SpecialityForm(),
                          "all_specialities": specialities,
                          "formset": formset,
                          "offers_forms": offers_forms,
                          "speciality_id": int(speciality_id),
                          "internship_choices": internship_choices,
                          "current_choice": current_choice,
                          "can_submit": len(selectable_offers) > 0,
                          "cohort": cohort})


@require_POST
@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
def assign_speciality_for_internship(request, cohort_id, internship_id):
    speciality_id = None
    if request.method == "POST":
        try:
            speciality_id = int(request.POST.get("speciality_id", 0))
        except ValueError:
            speciality_id = 0

    return redirect("select_internship_speciality", cohort_id=cohort_id, internship_id=internship_id,
                    speciality_id=speciality_id)


def get_first_choices_by_organization(speciality):
    list_number_choices = mdl_int.internship_choice.get_number_first_choice_by_organization(speciality)
    dict_number_choices_by_organization = dict()
    for number_first_choices in list_number_choices:
        dict_number_choices_by_organization[number_first_choices["organization"]] = \
            number_first_choices["organization__count"]
    return dict_number_choices_by_organization


def zip_offers_formset_and_first_choices(formset, internships_offers, number_choices_by_organization):
    zipped_data = None
    if internships_offers:
        zipped_data = []
        for offer, form in zip(internships_offers, formset):
            zipped_data.append((offer, form, number_choices_by_organization.get(offer.organization.id, 0)))
    return zipped_data


def _handle_formset_to_save(request, selectable_offers, student, current_internship, speciality):
    offer_preference_formset = formset_factory(OfferPreferenceForm, formset=OfferPreferenceFormSet,
                                               extra=len(selectable_offers), min_num=len(selectable_offers),
                                               max_num=len(selectable_offers), validate_min=True, validate_max=True)

    if request.method == 'POST':
        formset = offer_preference_formset(request.POST)
        if formset.is_valid() and do_not_exceed_maximum_personnal_internship(speciality, student):
            _remove_previous_choices(student, current_internship, speciality)
            save_student_choices(formset, student, current_internship, speciality)
            messages.add_message(request, messages.SUCCESS, _('internship_choice_successfully_saved'))
    else:
        formset = offer_preference_formset()

    return formset


def _remove_previous_choices(student, internship, speciality):
    if internship.speciality_id is not None:
        previous_choices = mdl_int.internship_choice.search(student=student, internship=internship,
                                                            speciality=speciality)
    else:
        previous_choices = mdl_int.internship_choice.search(student=student, internship=internship)
    if previous_choices:
        previous_choices.delete()


def save_student_choices(formset, student, internship, speciality):
    for form in formset:
        if form.cleaned_data:
            offer_pk = form.cleaned_data["offer"]
            preference_value = int(form.cleaned_data["preference"])
            offer = mdl_int.internship_offer.find_by_pk(offer_pk)
            if has_been_selected(preference_value) and is_correct_speciality(offer, speciality):
                internship_choice = mdl_int.internship_choice.InternshipChoice(student=student,
                                                                               organization=offer.organization,
                                                                               speciality=speciality,
                                                                               choice=preference_value,
                                                                               internship=internship,
                                                                               priority=False)
                internship_choice.save()


def has_been_selected(preference_value):
    return bool(preference_value)


def is_correct_speciality(offer, speciality):
    return offer.speciality == speciality


def do_not_exceed_maximum_personnal_internship(speciality, student):
    if speciality.acronym != "SP":
        return True
    number_choices_personal_internship = \
        mdl_int.internship_choice.search(student=student, speciality=speciality).count()
    return number_choices_personal_internship < 2
