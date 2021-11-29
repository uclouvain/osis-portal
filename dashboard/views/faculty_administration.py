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
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import TemplateView


class FacultyAdministration(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "faculty_administrator_dashboard.html"

    def test_func(self):
        return self._can_access_administration()

    def _can_access_administration(self):
        if self.request.user.has_perm('base.is_faculty_administrator'):
            return True
        can_access = False
        if 'performance' in settings.INSTALLED_APPS:
            from performance.views import main as perf_main_view
            can_access = perf_main_view._can_access_performance_administration(self.request)
        return can_access
