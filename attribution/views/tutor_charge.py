##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
import contextlib
import logging
from types import SimpleNamespace
from typing import List

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.db.models import Case, When, BooleanField, Value, F, CharField
from django.db.models.functions import Concat
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic.base import TemplateView
from osis_attribution_sdk.models import Attribution

from attribution.services.attribution import AttributionService
from base.forms.base_forms import GlobalIdForm
from base.models.academic_year import AcademicYear, current_academic_year
from base.models.learning_unit_year import LearningUnitYear
from base.models.person import Person
from base.utils import string_utils
from base.views import layout

YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST = 2017
MAIL_TO = 'mailto:'
STUDENT_LIST_EMAIL_END = '@listes-student.uclouvain.be'
logger = logging.getLogger(settings.DEFAULT_LOGGER)


class TutorChargeView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.can_access_attribution"
    raise_exception = False

    template_name = "tutor_charge.html"

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'display_years_tab': self.get_display_years_tab(),
            'current_year_displayed': self.get_current_year_displayed(),
            'person': self.person,
            'attributions': self.attributions,
            'total_lecturing_charge': self.get_total_lecturing_charge(),
            'total_practical_charge': self.get_total_practical_charge()
        }

    def get_current_year_displayed(self) -> int:
        year = self.request.GET.get('displayYear') or current_academic_year().year
        return int(year)

    def get_display_years_tab(self) -> List:
        max_year_in_past_attribution = current_academic_year().year - 5
        max_year_in_future_attribution = current_academic_year().year + 4
        return AcademicYear.objects.filter(
            year__gte=max_year_in_past_attribution,
            year__lte=max_year_in_future_attribution
        ).annotate(
            is_active=Case(
                When(year=self.get_current_year_displayed(), then=True),
                default=False,
                output_field=BooleanField(),
            ),
            url=Concat(Value(self.get_tutor_charge_url()), F('year'), output_field=CharField())
        ).values('year', 'is_active', 'url').order_by('-year')

    @cached_property
    def person(self) -> Person:
        return self.request.user.person

    def get_tutor_charge_url(self) -> str:
        return reverse('tutor_charge') + "?displayYear="

    @cached_property
    def attributions(self):
        attributions = AttributionService.get_attributions_list(self.get_current_year_displayed(), self.person, True)
        return [self._format_attribution_row(attribution) for attribution in attributions]

    def get_total_lecturing_charge(self):
        return sum(
            [
                float(attribution.lecturing_charge) if attribution.lecturing_charge else 0
                for attribution in self.attributions if not attribution.is_partim
            ]
        )

    def get_total_practical_charge(self):
        return sum(
            [
                float(attribution.practical_charge) if attribution.practical_charge else 0
                for attribution in self.attributions if not attribution.is_partim
            ]
        )

    def _format_attribution_row(self, attribution: Attribution):
        # It's mandatory to convert ModelNormal (Come from OpenAPI Generator) to SimpleNamespace in order to
        # add computed property
        percentage_allocation_charge = compute_percentage_allocation_charge(
            float(attribution.lecturing_charge) if attribution.lecturing_charge else 0,
            float(attribution.practical_charge) if attribution.practical_charge else 0,
            float(attribution.total_learning_unit_charge) if attribution.total_learning_unit_charge else 0
        ) if attribution.lecturing_charge or attribution.practical_charge else None
        for class_repartition in attribution.effective_class_repartition:
            clean_code = class_repartition.code.replace('-', '').replace('_', '')
            class_repartition.students_list_email = get_email_students(clean_code, attribution.year)
            class_repartition.repartition_students_url = ''  # FIXME: Create Url + View and use here
        return SimpleNamespace(
            **{
                **attribution.to_dict(),
                'students_list_email': get_email_students(attribution.code, attribution.year),
                'percentage_allocation_charge': percentage_allocation_charge,
                'attribution_students_url': self.get_attribution_students_url(attribution.code, attribution.year),
            }
        )

    def get_attribution_students_url(self, code: str, year: int):
        with contextlib.suppress(LearningUnitYear.DoesNotExist):
            learning_unit_year_id = LearningUnitYear.objects.get(acronym=code, academic_year__year=year).pk
            return reverse('attribution_students', kwargs={
                'learning_unit_year_id': learning_unit_year_id,
                'a_tutor': self.person.tutor.pk
            })


class AdminTutorChargeView(TutorChargeView):
    permission_required = "base.is_faculty_administrator"

    template_name = "tutor_charge_admin.html"

    @cached_property
    def person(self) -> Person:
        return Person.objects.get(global_id=self.kwargs['global_id'])

    def get_tutor_charge_url(self) -> str:
        return reverse('tutor_charge_admin', kwargs={'global_id': self.person.global_id}) + "?displayYear="

    def get_attribution_students_url(self, code: str, year: int):
        with contextlib.suppress(LearningUnitYear.DoesNotExist):
            learning_unit_year_id = LearningUnitYear.objects.get(acronym=code, academic_year__year=year).pk
            return reverse('attribution_students_admin', kwargs={
                'learning_unit_year_id': learning_unit_year_id,
                'a_tutor': self.person.tutor.pk
            })


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def attribution_administration(request):
    return layout.render(request, 'admin/attribution_administration.html', {})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def select_tutor_attributions(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            return HttpResponseRedirect(
                reverse("tutor_charge_admin", kwargs={'global_id': global_id})
            )
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/attribution_administration.html", {"form": form})


def get_email_students(an_acronym, year):
    if string_utils.is_string_not_null_empty(an_acronym):
        if year >= YEAR_NEW_MANAGEMENT_OF_EMAIL_LIST:
            return "{0}{1}-{2}{3}".format(MAIL_TO, an_acronym.lower(), year, STUDENT_LIST_EMAIL_END)
        else:
            return "{0}{1}{2}".format(MAIL_TO, an_acronym.lower(), STUDENT_LIST_EMAIL_END)
    return None


def compute_percentage_allocation_charge(lecturing_charge, practical_charge, total_learning_unit_charge):
    if total_learning_unit_charge > 0:
        percentage = (lecturing_charge + practical_charge) * 100 / total_learning_unit_charge
        return "%0.1f" % (percentage,)
    return None
