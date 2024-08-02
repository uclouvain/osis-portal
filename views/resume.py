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
from types import SimpleNamespace

from django.contrib.auth.decorators import login_required, permission_required
from django.utils.datetime_safe import date
from django.utils.translation import gettext as _

import base.models as mdl_base
from base.views import layout
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.decorators.global_view_decorators import redirect_if_multiple_registrations
from internship.models.enums.civility import Civility
from internship.models.score_encoding_utils import APDS
from internship.services.internship import InternshipAPIService
from internship.templatetags.period import str_to_iso_date


@login_required
@permission_required('base.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
def view_student_resume(request, cohort_id):
    cohort = InternshipAPIService.get_cohort_detail(cohort_name=cohort_id, person=request.user.person)
    internships = InternshipAPIService.get_internships_by_cohort(cohort_name=cohort_id, person=request.user.person)

    student_information = InternshipAPIService.get_internship_student_information_list_by_person(
        person=request.user.person
    )
    periods = InternshipAPIService.get_periods(person=request.user.person, cohort_name=cohort_id)

    student_affectations = InternshipAPIService.get_person_affectations(person=request.user.person, cohort=cohort)
    student_affectations = [aff for aff in student_affectations if aff.period.name in [p.name for p in periods]]

    student_choices = InternshipAPIService.get_student_choices(
        person=request.user.person, cohort_name=cohort_id
    ).results

    student_choices = sorted(student_choices, key=lambda choice: choice.choice)

    publication_allowed = str_to_iso_date(cohort.publication_start_date) <= date.today()

    student = mdl_base.student.find_by_user(request.user)

    offers = {}

    # transform to SimpleNamespace to have free-form internship objects
    student_affectations = [SimpleNamespace(**affectation._data_store) for affectation in student_affectations]

    for affectation in student_affectations:
        score = InternshipAPIService.get_affectation(
            person=request.user.person,
            affectation_uuid=str(affectation.uuid)
        ).score
        if score and score.validated:
            score.comments = _replace_comments_keys_with_translations(score.comments)
            setattr(affectation, 'score', score)
        internship_offers = InternshipAPIService.get_internship_offers(
            person=request.user.person,
            cohort_name=cohort_id,
            specialty=affectation.speciality,
            organization=affectation.organization,
        ).results
        offer = next((offer for offer in internship_offers), None)
        if offer:
            offer.master = _get_internship_masters_repr(request.user.person, affectation)
        try:
            offers[affectation.organization.reference].update({affectation.speciality.name: offer})
        except KeyError:
            offers.update({affectation.organization.reference: {affectation.speciality.name: offer}})
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


def _replace_comments_keys_with_translations(comments):
    comments_keys_mapping = {
        'impr_areas': _('Improvement areas'),
        'suggestions': _('Suggested learning methods'),
        'good_perf_ex': _('Good performance examples'),
        'intermediary_evaluation': _('Intermediary evaluation')
    }
    return {comments_keys_mapping[k]: v for k, v in comments.items()}
