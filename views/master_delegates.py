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
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.messages import SUCCESS
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from osis_internship_sdk.models import MasterGet, Person, AllocationGet

from base.views import layout
from internship.decorators.score_encoding_view_decorators import redirect_if_not_master
from internship.models.enums.role_choice import ChoiceRole
from internship.views.api_client import get_master_by_email, get_master_allocations, get_delegated_allocations, \
    post_master, get_organization, get_specialty, post_master_allocation, delete_master_allocation


@login_required
@redirect_if_not_master
def manage_delegates(request):
    master = get_master_by_email(request.user.email)
    allocations = get_master_allocations(master['uuid'])

    master_allocations = [allocation for allocation in allocations if allocation['role'] == ChoiceRole.MASTER.value]
    if not master_allocations:
        return redirect(reverse('internship_master_home'))

    for allocation in master_allocations:
        allocation.__dict__['internship'] = _get_internship_reference(allocation)
        allocation.__dict__['delegated'] = get_delegated_allocations(
            allocation['specialty']['uuid'], allocation['organization']['uuid']
        )
    return layout.render(request, "internship_manage_delegates.html", locals())


@login_required
@redirect_if_not_master
def new_delegate(request, specialty_uuid, organization_uuid):
    if request.POST:
        person = Person(
            first_name=request.POST.get('first_name'),
            last_name=request.POST.get('last_name'),
            birth_date=request.POST.get('birth_date'),
            email=request.POST.get('email')
        )
        master = MasterGet(person=person, civility=request.POST.get('civility'))
        created_master = post_master(master)
        if created_master:
            organization = get_organization(organization_uuid)
            specialty = get_specialty(specialty_uuid)
            allocation = AllocationGet(
                master=created_master,
                organization=organization,
                specialty=specialty,
                role=ChoiceRole.DELEGATE.value
            )
            allocation = post_master_allocation(allocation)
            if allocation:
                messages.add_message(
                    request, SUCCESS, _('Internship delegate {} created with success'.format(
                        master.person.last_name
                    ))
                )
    return redirect(reverse('internship_manage_delegates'))


@login_required
@redirect_if_not_master
def delete_delegate(request, allocation_uuid):
    if delete_master_allocation(allocation_uuid):
        messages.add_message(request, SUCCESS, _('Internship delegate deleted with success'))
    return redirect(reverse('internship_manage_delegates'))


def _get_internship_reference(allocation):
    return "{}{}".format(allocation['specialty']['acronym'], allocation['organization']['reference'])
