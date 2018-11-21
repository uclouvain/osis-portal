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

from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import redirect
from django.utils.translation import ugettext_lazy as _

import base.models as mdl_base
import internship.models as mdl_internship
from base.views import layout
from dashboard.views import main as dash_main_view
from internship.decorators.cohort_view_decorators import redirect_if_not_in_cohort
from internship.decorators.global_view_decorators import redirect_if_multiple_registrations


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
def view_internship_home(request, cohort_id):
    cohort = mdl_internship.cohort.Cohort.objects.get(pk=cohort_id)
    today = datetime.date.today()
    subscription_allowed = cohort.subscription_start_date <= today <= cohort.subscription_end_date
    return layout.render(request, "internship_home.html", locals())


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
def view_cohort_selection(request):
    student = mdl_base.student.find_by_user(request.user)
    if student:
        cohort_subscriptions = mdl_internship.internship_student_information.find_by_person(student.person)
        if cohort_subscriptions:
            cohorts = [subscription.cohort for subscription in cohort_subscriptions]
            return layout.render(request, "cohort_selection.html", {'cohorts': cohorts})
        else:
            messages.add_message(
                request,
                messages.ERROR,
                _('It seems you are not subscribed to internships, you may want to check with your administration.')
            )
            return redirect(dash_main_view.home)
    else:
        messages.add_message(
            request,
            messages.ERROR,
            _('It seems you are not subscribed to internships, you may want to check with your administration.')
        )
        return redirect(dash_main_view.home)


@login_required
@permission_required('internship.can_access_internship', raise_exception=True)
@redirect_if_multiple_registrations
@redirect_if_not_in_cohort
def view_internship_home(request, cohort_id):
    cohort = mdl_internship.cohort.Cohort.objects.get(pk=cohort_id)
    today = datetime.date.today()
    subscription_allowed = cohort.subscription_start_date <= today <= cohort.subscription_end_date
    return layout.render(request, "internship_home.html", locals())
