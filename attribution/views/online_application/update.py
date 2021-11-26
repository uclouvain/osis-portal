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
import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.views.generic import FormView

from attribution.forms.application import ApplicationForm
from attribution.services.application import ApplicationService, ApplicationBusinessException
from attribution.utils import permission
from frontoffice.settings.osis_sdk.utils import MultipleApiBusinessException

logger = logging.getLogger(settings.DEFAULT_LOGGER)


class UpdateApplicationView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    # FormView
    form_class = ApplicationForm
    template_name = "application_form.html"

    @cached_property
    def tutor(self):
        return self.request.user.person.tutor

    @cached_property
    def application(self):
        return ApplicationService.get_application(self.kwargs['application_uuid'], self.tutor.person)

    @cached_property
    def vacant_course(self):
        return ApplicationService.get_vacant_course(code=self.application.code, person=self.tutor.person)

    def get(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        try:
            ApplicationService.update_application(
                application_uuid=self.kwargs['application_uuid'],
                lecturing_volume=form.cleaned_data['charge_lecturing_asked'],
                practical_volume=form.cleaned_data['charge_practical_asked'],
                remark=form.cleaned_data['remark'],
                course_summary=form.cleaned_data['course_summary'],
                person=self.tutor.person
            )
        except MultipleApiBusinessException as multiple_business_api_exception:
            for exception in multiple_business_api_exception.exceptions:
                if exception.status_code == ApplicationBusinessException.LecturingAndPracticalChargeNotFilled.value:
                    form.add_error('charge_lecturing_asked', exception.detail)
                    form.add_error('charge_practical_asked', exception.detail)
                else:
                    messages.add_message(self.request, messages.ERROR, exception.detail)
            return self.render_to_response(self.get_context_data(form=form))
        return super().form_valid(form)

    def get_initial(self):
        return {
            'charge_lecturing_asked': self.application.lecturing_volume,
            'charge_practical_asked': self.application.practical_volume,
            'course_summary': self.application.course_summary,
            'remark': self.application.remark
        }

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            'vacant_course': self.vacant_course
        }

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'save_url': reverse('update_application', kwargs={'application_uuid': self.kwargs['application_uuid']}),
            'cancel_url': reverse('applications_overview'),
            'a_tutor': self.tutor,
            'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
        }

    def get_success_url(self):
        return reverse('applications_overview')
