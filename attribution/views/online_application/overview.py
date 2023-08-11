##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
import logging

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.utils.functional import cached_property
from django.views.generic import TemplateView

from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar
from attribution.services.application import ApplicationService
from attribution.utils import permission
from base.models.tutor import Tutor
from base.templatetags.academic_year_display import display_as_academic_year

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class ApplicationOverviewView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    # TemplateView
    template_name = "attribution_overview.html"

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        elif not permission.is_online_application_opened(request.user):
            return redirect("outside_applications_period")
        return super().dispatch(request, *args, **kwargs)

    @cached_property
    def tutor(self):
        return self.request.user.person.tutor

    @cached_property
    def application_course_calendar(self):
        calendars = ApplicationCoursesRemoteCalendar(self.tutor.person).get_opened_academic_events()
        if len(calendars) > 1:
            logger.warning("Multiple application courses calendars opened at same time")
        return calendars[0]

    @cached_property
    def applications(self):
        return ApplicationService.get_applications(self.tutor.person)

    @cached_property
    def attributions_about_to_expire(self):
        return ApplicationService.get_attribution_about_to_expires(self.tutor.person)

    @cached_property
    def charge_summary(self):
        return ApplicationService.get_my_charge_summary(self.tutor.person)

    def get_total_lecturing_charge(self):
        return sum(
            float(attribution.lecturing_volume) if attribution.lecturing_volume else 0
            for attribution in self.charge_summary
        )

    def get_total_practical_charge(self):
        return sum(
            float(attribution.practical_volume) if attribution.practical_volume else 0
            for attribution in self.charge_summary
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'application_course_calendar': self.application_course_calendar,
            'attributions_about_to_expire': self.attributions_about_to_expire,
            'attributions': self.charge_summary,
            'tot_lecturing': self.get_total_lecturing_charge(),
            'tot_practical': self.get_total_practical_charge(),
            'applications': self.applications,
            'application_academic_year': display_as_academic_year(
                self.application_course_calendar.authorized_target_year
            ),
            'previous_academic_year': display_as_academic_year(
                self.application_course_calendar.authorized_target_year - 1
            ),
            'a_tutor': self.tutor,
            'catalog_url': settings.ATTRIBUTION_CONFIG.get('CATALOG_URL'),
            'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
        }


class ApplicationOverviewAdminView(ApplicationOverviewView):
    permission_required = "base.is_faculty_administrator"

    @cached_property
    def tutor(self):
        return Tutor.objects.get(person__global_id=self.kwargs['global_id'])
