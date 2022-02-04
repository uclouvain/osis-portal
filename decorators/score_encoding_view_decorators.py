# -*- coding: utf-8 -*-
############################################################################
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
############################################################################
from functools import wraps

from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _

from internship.services.internship import InternshipAPIService


def _check_is_master(request):
    master = InternshipAPIService.get_master(person=request.user.person)
    if not master:
        messages.add_message(
            request, messages.ERROR, _("Score encoding is only accessible to internship's masters")
        )
        return redirect(reverse('home'))
    return master


def _check_match_allocations(request, master, specialty_uuid, organization_uuid):
    allocations = InternshipAPIService.get_master_allocations(person=request.user.person, master_uuid=master.uuid)
    allocations_details = [(allocation.specialty.uuid, allocation.organization.uuid) for allocation in allocations]

    # get parent allocation details if subspecialty
    allocations_details += [
        (allocation.specialty.parend.uuid, allocation.organization.uuid) for allocation in allocations
        if allocation.specialty.parent
    ]

    return (specialty_uuid, organization_uuid) in allocations_details


def redirect_if_not_master(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        _check_is_master(request)
        response = function(request, *args, **kwargs)
        return response
    return wrapper


def redirect_if_not_master_with_matching_allocation(function):
    @wraps(function)
    def wrapper(request, *args, **kwargs):
        master = _check_is_master(request)
        if _check_match_allocations(request, master, kwargs['specialty_uuid'], kwargs['organization_uuid']):
            response = function(request, *args, **kwargs)
            return response
        else:
            messages.add_message(
                request, messages.ERROR,
                _("The requested scores sheet does not match your internship's allocations")
            )
        return redirect(reverse('internship_score_encoding'))
    return wrapper
