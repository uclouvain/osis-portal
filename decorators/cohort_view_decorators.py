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
from functools import wraps

from django.core.exceptions import MultipleObjectsReturned
from django.shortcuts import redirect
from django.urls import reverse

import base.models as mdl_base
from dashboard.views import main as dash_main_view
from internship.models import internship_student_information
from internship.models.cohort import Cohort


def redirect_if_not_in_cohort(function):
    @wraps(function)
    def wrapper(request, cohort_id, *args, **kwargs):
        try:
            student = mdl_base.student.find_by_user(request.user)
        except MultipleObjectsReturned:
            return dash_main_view.show_multiple_registration_id_error(request)

        if student and internship_student_information.find_by_person_in_cohort(cohort_id,
                                                                               student.person_id).count() > 0:
            return function(request, cohort_id, *args, **kwargs)
        else:
            return redirect(reverse("internship"))

    return wrapper


def redirect_if_subscription_not_allowed(function):
    @wraps(function)
    def wrapper(request, cohort_id, *args, **kwargs):
        try:
            mdl_base.student.find_by_user(request.user)
        except MultipleObjectsReturned:
            return dash_main_view.show_multiple_registration_id_error(request)

        cohort = Cohort.objects.get(pk=cohort_id)

        if cohort.subscription_start_date <= datetime.date.today() <= cohort.subscription_end_date:
            response = function(request, cohort_id, *args, **kwargs)
            return response
        else:
            return redirect(reverse("internship_student_home", kwargs={'cohort_id': cohort.id}))

    return wrapper
