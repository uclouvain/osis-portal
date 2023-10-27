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
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from django.contrib.messages import SUCCESS, ERROR
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext as _
from osis_internship_sdk.models import MasterGet, Person, AllocationGet

from base.models.signals import GROUP_MASTERS_INTERNSHIP
from base.views import layout
from internship.decorators.score_encoding_view_decorators import redirect_if_not_master
from internship.models.enums.role_choice import ChoiceRole
from internship.services.internship import InternshipAPIService, InternshipServiceException


@login_required
@redirect_if_not_master
def manage_delegates(request):
    master = InternshipAPIService.get_master(person=request.user.person)
    allocations = InternshipAPIService.get_master_allocations(person=request.user.person, master_uuid=master['uuid'])

    master_allocations = [allocation for allocation in allocations if allocation['role'] == ChoiceRole.MASTER.name]
    if not master_allocations:
        return redirect(reverse('internship_master_home'))

    for allocation in master_allocations:
        allocation.__dict__['internship'] = _get_internship_reference(allocation)
        allocation.__dict__['delegated'] = InternshipAPIService.get_delegated_allocations(
            person=request.user.person,
            specialty_uuid=allocation['specialty']['uuid'],
            organization_uuid=allocation['organization']['uuid'],
        )
    return layout.render(request, "internship_manage_delegates.html", locals())


@login_required
@redirect_if_not_master
def new_delegate(request, specialty_uuid, organization_uuid):
    if request.POST:
        form = DelegateForm(request.POST)

        if form.is_valid():
            person = Person(
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                birth_date=str(form.cleaned_data['birth_date']),
                email=form.cleaned_data['email']
            )
            master = MasterGet(person=person, civility=form.cleaned_data['civility'])
            try:
                created_master = InternshipAPIService.post_master(request.user.person, master)
                if created_master:
                    organization = InternshipAPIService.get_organization(request.user.person, organization_uuid)
                    specialty = InternshipAPIService.get_specialty(request.user.person, specialty_uuid)
                    allocation = AllocationGet(
                        master=created_master,
                        organization=organization,
                        specialty=specialty,
                        role=ChoiceRole.DELEGATE.name
                    )
                    allocation = InternshipAPIService.post_master_allocation(request.user.person, allocation)
                    if allocation:
                        # TODO : remove when migrate to osis
                        _add_existing_user_to_internship_masters_group(person)
                        messages.add_message(
                            request, SUCCESS, _('Internship delegate {} created with success').format(
                                master.person.last_name
                            )
                        )
                    internship_ref = _get_internship_reference(allocation)
                    return redirect(reverse('internship_manage_delegates') + "?internship={}".format(internship_ref))
            except InternshipServiceException as e:
                messages.add_message(request, ERROR, _(
                    'An error occurred during delegate creation, '
                    'please contact internships administration (STAC) for further assistance.'
                ))
                if e.reason:
                    messages.add_message(request, ERROR, e.reason)
        else:
            for error in form.errors:
                messages.add_message(request, ERROR, error)
    return redirect(reverse('internship_manage_delegates'))


@login_required
@redirect_if_not_master
def delete_delegate(request, allocation_uuid):
    if InternshipAPIService.delete_master_allocation(request.user.person, allocation_uuid):
        messages.add_message(request, SUCCESS, _('Internship delegate deleted with success'))
    return redirect(reverse('internship_manage_delegates'))


def _get_internship_reference(allocation):
    return "{}{}".format(allocation['specialty']['acronym'], allocation['organization']['reference'])


def _add_existing_user_to_internship_masters_group(person):
    existing_user = _get_user_by_email(person.email)
    if existing_user and not existing_user.groups.filter(name=GROUP_MASTERS_INTERNSHIP).exists():
        group = Group.objects.get(name=GROUP_MASTERS_INTERNSHIP)
        existing_user.groups.add(group)


def _get_user_by_email(email):
    try:
        return User.objects.get(email=email)
    except User.DoesNotExist:
        return None


class DelegateForm(forms.Form):
    civility = forms.ChoiceField(choices=[('DOCTOR', 'DOCTOR'), ('PROFESSOR', 'PROFESSOR')])
    first_name = forms.CharField(max_length=50)
    last_name = forms.CharField(max_length=50)
    birth_date = forms.DateField()
    email = forms.EmailField(max_length=50)
