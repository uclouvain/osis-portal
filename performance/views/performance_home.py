from types import SimpleNamespace
from typing import List

from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.core.exceptions import MultipleObjectsReturned, PermissionDenied
from django.utils.functional import cached_property
from django.views.generic import TemplateView
from osis_offer_enrollment_sdk.model.enrollment import Enrollment

from base.business import student as student_business
from base.models.student import Student
from dashboard.views import main as dash_main_view
from performance.models.enums import offer_registration_state
from performance.models.student_performance import StudentPerformance
from performance.services.offer_enrollment import OfferEnrollmentService
from performance.views import main as performance_main_view


class PerformanceHome(LoginRequiredMixin, PermissionRequiredMixin, TemplateView):
    permission_required = "base.is_student"
    template_name = "performance_home_student.html"
    raise_exception = True

    def get_context_data(self, **kwargs):
        print(self.student.registration_id)
        return {
            **super().get_context_data(**kwargs),
            "student": self.student,
            "programs": self.offer_enrollments_list,
            "registration_states_to_show": offer_registration_state.STATES_TO_SHOW_ON_PAGE
        }

    @cached_property
    def offer_enrollments_list(self):
        offer_enrollments = OfferEnrollmentService.get_my_enrollments_list(self.student.person).results
        allowed_registration_states = [value for key, value in offer_registration_state.OFFER_REGISTRAION_STATES]
        offer_enrollments_to_display = []
        for offer_enrollment in offer_enrollments:
            student_performance = self._get_correspondant_student_performance(offer_enrollment)
            registration_state = student_performance and student_performance.offer_registration_state
            if registration_state in allowed_registration_states:
                offer_enrollments_to_display.append(
                    SimpleNamespace(
                        **offer_enrollment.to_dict(),
                        offer_registration_state=registration_state,
                        pk=student_performance.pk
                    )
                )
                print(offer_enrollment)
        return offer_enrollments_to_display

    def _get_correspondant_student_performance(self, offer_enrollment: Enrollment) -> StudentPerformance:
        return next(
            (student_performance
             for student_performance in self.student_performances
             if student_performance.acronym == offer_enrollment.acronym
             and student_performance.academic_year == offer_enrollment.year),
            None
        )

    @cached_property
    def student(self) -> Student:
        try:
            return student_business.find_by_user_and_discriminate(self.request.user)
        except MultipleObjectsReturned:
            return dash_main_view.show_multiple_registration_id_error(self.request)

    @cached_property
    def student_performances(self) -> List[StudentPerformance]:
        if self.student:
            return StudentPerformance.objects.filter(
                registration_id=self.student.registration_id
            ).only('academic_year', "acronym", "offer_registration_state", "pk")
        return []


class PerformanceHomeAdmin(PerformanceHome):
    template_name = "performance_home_admin.html"
    raise_exception = False

    def _check_permissions(self):
        if not performance_main_view.__can_access_performance_administration(self.request):
            raise PermissionDenied
        if self.student and \
                not performance_main_view.__can_visualize_student_programs(self.request, self.student.registration_id):
            raise PermissionDenied

    def get_context_data(self, **kwargs):
        self._check_permissions()
        return super().get_context_data(**kwargs)
