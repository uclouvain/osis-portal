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
import datetime

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.datetime_safe import date

from base.models import student as mdl_student
from base.views import layout
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.decorators.global_view_decorators import redirect_if_multiple_registrations
from internship.models import cohort as mdl_internship_cohort
from internship.models import internship as mdl_internship
from internship.models import internship_choice as mdl_internship_choice
from internship.models import internship_offer as mdl_internship_offer
from internship.models import internship_speciality as mdl_internship_speciality
from internship.models import internship_student_affectation_stat as mdl_student_affectation
from internship.models import internship_student_information as mdl_student_information
from internship.models import period as mdl_period
from internship.models.enums.civility import Civility
from internship.models.score_encoding_utils import APDS
from internship.services.internship import InternshipAPIService


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
def view_student_resume(request, cohort_id):
    cohort = mdl_internship_cohort.Cohort.objects.get(pk=cohort_id)
    student = mdl_student.find_by_user(request.user)
    internships = mdl_internship.Internship.objects.filter(cohort=cohort).order_by('speciality', 'name')

    student_information = mdl_student_information.find_by_user_in_cohort(request.user, cohort=cohort)
    periods = mdl_period.Period.objects.filter(cohort=cohort)
    period_ids = periods.values_list("pk", flat=True)
    student_affectations = mdl_student_affectation.InternshipStudentAffectationStat.objects.filter(
        student=student,
        period_id__in=period_ids
    ).order_by("period__name")
    specialities = mdl_internship_speciality.find_by_cohort(cohort)
    student_choices = mdl_internship_choice.search(student=student, specialities=specialities)
    cohort = mdl_internship_cohort.Cohort.objects.get(pk=cohort_id)
    publication_allowed = cohort.publication_start_date <= datetime.date.today()
    offers = {}
    for affectation in student_affectations:
        score = InternshipAPIService.get_affectation(
            person=request.user.person,
            affectation_uuid=str(affectation.uuid)
        ).score
        if score and score.validated:
            setattr(affectation, 'score', score)
        offer = mdl_internship_offer.find_offer(
            cohort=cohort,
            speciality=affectation.speciality,
            organization=affectation.organization
        ).first()
        offer.master = _get_internship_masters_repr(request.user.person, affectation)
        try:
            offers[affectation.organization].update({affectation.speciality: offer})
        except KeyError:
            offers.update({affectation.organization: {affectation.speciality: offer}})
    return layout.render(request, "student_resume.html", {
        "student": student,
        "student_information": student_information,
        "student_affectations": student_affectations,
        "student_choices": student_choices,
        "internships": internships,
        "publication_allowed": publication_allowed,
        "cohort": cohort,
        "offers": offers,
        "current_date": date.today(),
        "apds": APDS,
    })


def _get_internship_masters_repr(person, affectation):
    allocations = InternshipAPIService.get_mastered_allocations(
        person=person,
        specialty_uuid=str(affectation.speciality.uuid),
        organization_uuid=str(affectation.organization.uuid)
    )
    return " & ".join(
        ["{} {}".format(
            Civility.get_acronym(alloc.master.civility),
            alloc.master.person.last_name.upper()
        ) for alloc in allocations]
    )


def save_from_form(form, person, cohort):
    defaults = {
        "location": form.cleaned_data["location"],
        "postal_code": form.cleaned_data["postal_code"],
        "city": form.cleaned_data["city"],
        "country": form.cleaned_data["country"],
        "email": form.cleaned_data["email"],
        "phone_mobile": form.cleaned_data["phone_mobile"],
        "contest": form.cleaned_data["contest"],
    }

    mdl_student_information.InternshipStudentInformation.objects.update_or_create(person=person, cohort=cohort,
                                                                                  defaults=defaults)
