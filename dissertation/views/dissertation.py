##############################################################################
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
##############################################################################

from admission.models import academic_year, offer_year
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from base import models as mdl
from base.views import layout
from dissertation.models import dissertation, dissertation_role, dissertation_update, proposition_dissertation,\
    proposition_role
from dissertation.forms import DissertationForm, DissertationUpdateForm


@login_required
def dissertations(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    memories = dissertation.search_by_user(student)
    return layout.render(request, 'dissertations_list.html',
                         {'dissertations': memories,
                          'student': student})


@login_required
def dissertation_delete(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    memory.deactivate()
    dissertation_update.add(request, memory, memory.status, justification="manager_set_active_false ")
    return redirect('dissertations')


@login_required
def dissertation_detail(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    count = dissertation.count_submit_by_user(student)
    if memory.author != student:
        return redirect('dissertations')
    else:
        count_dissertation_role = dissertation_role.count_by_dissertation(memory)
        count_proposition_role = proposition_role.count_by_dissertation(memory)
        proposition_roles = proposition_role.search_by_dissertation(memory)
        if count_proposition_role == 0:
            if count_dissertation_role == 0:
                dissertation_role.add('PROMOTEUR', memory.proposition_dissertation.author, memory)
        else:
            if count_dissertation_role == 0:
                for role in proposition_roles:
                    dissertation_role.add(role.status, role.adviser, memory)
        dissertation_roles = dissertation_role.search_by_dissertation(memory)
        return layout.render(request, 'dissertation_detail.html',
                             {'count': count,
                              'count_dissertation_role': count_dissertation_role,
                              'dissertation': memory,
                              'dissertation_roles': dissertation_roles,
                              'student': student})


@login_required
def dissertation_history(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    dissertation_updates = dissertation_update.search_by_dissertation(memory)
    return layout.render(request, 'dissertation_history.html',
                         {'dissertation': memory,
                          'dissertation_updates': dissertation_updates})


@login_required
def dissertation_new(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    offers = mdl.offer.find_by_student(student)
    if request.method == "POST":
        form = DissertationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dissertations')
        else:
            form.fields["defend_year"].queryset = academic_year.find_last_academic_years()
            form.fields["offer_year_start"].queryset = offer_year.find_by_offer(offers)
            form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offers)
    else:
        form = DissertationForm(initial={'active': True, 'author': student})
        form.fields["defend_year"].queryset = academic_year.find_last_academic_years()
        form.fields["offer_year_start"].queryset = offer_year.find_by_offer(offers)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offer(offers)
    return layout.render(request, 'dissertation_new.html',
                         {'form': form,
                          'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES})


@login_required
def dissertations_search(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    memories = dissertation.search(terms=request.GET['search'], author=student)
    return layout.render(request, "dissertations_list.html",
                         {'student': student,
                          'dissertations': memories})


@login_required
def dissertation_to_dir_submit(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    old_status = memory.status
    new_status = dissertation.get_next_status(memory, "go_forward")
    if request.method == "POST":
        form = DissertationUpdateForm(request.POST)
        if form.is_valid():
            memory.go_forward()
            data = form.cleaned_data
            justification = data['justification']
            dissertation_update.add(request, memory, old_status, justification=justification)
            return redirect('dissertation_detail', pk=pk)
    else:
        form = DissertationUpdateForm()
    return layout.render(request, 'dissertation_add_justification.html',
                         {'form': form, 'dissertation': memory, "old_status": old_status, "new_status": new_status})
