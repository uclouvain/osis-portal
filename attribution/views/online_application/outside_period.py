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
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView

from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar
from base.templatetags.academic_year_display import display_as_academic_year

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class OutsidePeriod(LoginRequiredMixin, TemplateView):
    template_name = "attribution_access_denied.html"

    @cached_property
    def calendar(self):
        return ApplicationCoursesRemoteCalendar(self.request.user.person)

    def dispatch(self, request, *args, **kwargs):
        if self.calendar.get_opened_academic_events():
            return HttpResponseRedirect(reverse('applications_overview'))
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        self._manage_previous_academic_event()
        self._manage_next_academic_event()
        return super().get_context_data(**kwargs)

    def _manage_next_academic_event(self):
        next_academic_event = self.calendar.get_next_academic_event()
        if next_academic_event:
            messages.add_message(
                self.request,
                messages.WARNING,
                _('The period of online application for courses %(year)s will open '
                  'on %(start_date)s until %(end_date)s') % {
                    'year': display_as_academic_year(next_academic_event.authorized_target_year),
                    'start_date': next_academic_event.start_date.strftime('%d/%m/%Y'),
                    'end_date': next_academic_event.end_date.strftime(
                        '%d/%m/%Y') if next_academic_event.end_date else ''
                }
            )

    def _manage_previous_academic_event(self):
        previous_academic_event = self.calendar.get_previous_academic_event()
        if previous_academic_event:
            messages.add_message(
                self.request,
                messages.WARNING,
                _('The period of online application for courses %(year)s was opened '
                  'from %(start_date)s to %(end_date)s') % {
                    'year': display_as_academic_year(previous_academic_event.authorized_target_year),
                    'start_date': previous_academic_event.start_date.strftime('%d/%m/%Y'),
                    'end_date': previous_academic_event.end_date.strftime('%d/%m/%Y')
                    if previous_academic_event.end_date else ''
                }
            )
