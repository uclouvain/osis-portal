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
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import ugettext_lazy as _
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView, FormView

from attribution.calendar.application_courses_calendar import ApplicationCoursesRemoteCalendar
from attribution.forms.application import ApplicationForm, VacantAttributionFilterForm
from attribution.services.application import ApplicationService, ApplicationBusinessException
from attribution.utils import permission
from base.forms.base_forms import GlobalIdForm
from base.models.tutor import Tutor
from base.templatetags.academic_year_display import display_as_academic_year
from base.views import layout
from frontoffice.settings.osis_sdk.utils import MultipleApiBusinessException

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.can_access_attribution_application', raise_exception=True)
def outside_period(request):
    calendar = ApplicationCoursesRemoteCalendar()
    if calendar.get_opened_academic_events():
        return HttpResponseRedirect(reverse('applications_overview'))

    previous_academic_event = calendar.get_previous_academic_event()
    if previous_academic_event:
        messages.add_message(
            request,
            messages.WARNING,
            _('The period of online application for courses %(year)s opened on %(start_date)s to %(end_date)s') % {
                'year': display_as_academic_year(previous_academic_event.authorized_target_year),
                'start_date': previous_academic_event.start_date.strftime('%d/%m/%Y'),
                'end_date': previous_academic_event.end_date.strftime('%d/%m/%Y')
                if previous_academic_event.end_date else ''
            }
        )

    next_academic_event = calendar.get_next_academic_event()
    if next_academic_event:
        messages.add_message(
            request,
            messages.WARNING,
            _('The period of online application for courses %(year)s will open on %(start_date)s to %(end_date)s') % {
                'year': display_as_academic_year(next_academic_event.authorized_target_year),
                'start_date': next_academic_event.start_date.strftime('%d/%m/%Y'),
                'end_date': next_academic_event.end_date.strftime('%d/%m/%Y') if next_academic_event.end_date else ''
            }
        )
    return layout.render(request, "attribution_access_denied.html", {})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
@require_http_methods(["GET", "POST"])
def administration_applications(request):
    if request.method == "POST":
        form = GlobalIdForm(request.POST)
        if form.is_valid():
            global_id = form.cleaned_data['global_id']
            return redirect('visualize_tutor_applications', global_id=global_id)
    else:
        form = GlobalIdForm()
    return layout.render(request, "admin/applications_administration.html", {"form": form})


class ApplicationOverviewView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    # TemplateView
    template_name = "attribution_overview.html"

    def get(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")
        return super().get(request, *args, **kwargs)

    @cached_property
    def tutor(self):
        return self.request.user.person.tutor

    @cached_property
    def application_course_calendar(self):
        calendars = ApplicationCoursesRemoteCalendar().get_opened_academic_events()
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
            [
                float(attribution.lecturing_volume) if attribution.lecturing_volume else 0
                for attribution in self.charge_summary
            ]
        )

    def get_total_practical_charge(self):
        return sum(
            [
                float(attribution.practical_volume) if attribution.practical_volume else 0
                for attribution in self.charge_summary
            ]
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(),
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
        return Tutor.objects.filter(person__global_id=self.kwargs['global_id'])


class SearchVacantCoursesView(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    # TemplateView
    template_name = "attribution_vacant_list.html"

    @cached_property
    def tutor(self):
        return self.request.user.person.tutor

    def get(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")

        form = VacantAttributionFilterForm(data=request.GET)
        if request.GET and form.is_valid():
            kwargs['vacant_courses'] = ApplicationService.search_vacant_courses(
                code=form.cleaned_data['learning_container_acronym'],
                allocation_faculty=getattr(form.cleaned_data['faculty'], 'acronym', ''),
                person=self.tutor.person
            )
        kwargs['form'] = form
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'a_tutor': self.tutor,
            'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
        }


class CreateApplicationView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
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
    def vacant_course(self):
        return ApplicationService.get_vacant_course(code=self.kwargs['vacant_course_code'], person=self.tutor.person)

    def get(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")
        return super().get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")
        return super().post(request, *args, **kwargs)

    def get_form_kwargs(self):
        return {
            **super().get_form_kwargs(),
            'vacant_course': self.vacant_course
        }

    def form_valid(self, form):
        try:
            ApplicationService.create_application(
                vacant_course_code=self.kwargs['vacant_course_code'],
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

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'save_url': reverse('create_application', kwargs={'vacant_course_code': self.kwargs['vacant_course_code']}),
            'cancel_url': reverse('applications_overview'),
            'a_tutor': self.tutor,
            'help_button_url': settings.ATTRIBUTION_CONFIG.get('HELP_BUTTON_URL'),
        }

    def get_success_url(self):
        return reverse('applications_overview')


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


class RenewMultipleAttributionsAboutToExpireView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")

        post_data = dict(request.POST.lists())
        vacant_course_codes = [
            param.split("_")[-1] for param, value in post_data.items() if "vacant_course_" in param
        ]

        if vacant_course_codes:
            ApplicationService.renew_attributions_about_to_expire(vacant_course_codes, self.request.user.person)
        else:
            messages.add_message(request, messages.ERROR, _('No attribution renewed'))
        return redirect('applications_overview')


class DeleteApplicationView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")

        ApplicationService.delete_application(self.kwargs['application_uuid'], self.request.user.person)
        messages.add_message(request, messages.SUCCESS, _('Application successfully deleted'))
        return redirect('applications_overview')


class SendApplicationsSummaryView(LoginRequiredMixin, PermissionRequiredMixin, View):
    # PermissionRequiredMixin
    permission_required = "base.can_access_attribution_application"
    raise_exception = True

    def post(self, request, *args, **kwargs):
        if not permission.is_online_application_opened(self.request.user):
            return redirect("outside_applications_period")

        ApplicationService.send_applications_summary(self.request.user.person)
        messages.add_message(request, messages.INFO, _('An email with your applications have been sent'))
        return redirect('applications_overview')
