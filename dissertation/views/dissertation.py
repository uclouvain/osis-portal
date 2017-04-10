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

from base.models import offer_year
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect
from base import models as mdl
from base.views import layout
from dissertation.models import dissertation, dissertation_document_file,  dissertation_role, dissertation_update,\
    offer_proposition, proposition_dissertation, proposition_offer, proposition_role
from dissertation.forms import DissertationForm, DissertationEditForm, DissertationRoleForm,\
                                DissertationTitleForm, DissertationUpdateForm
from django.utils import timezone


@login_required
def dissertations(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    offers = mdl.offer.find_by_student(student)
    offer_propositions = offer_proposition.search_by_offers(offers)
    memories = dissertation.find_by_user(student)
    date_now = timezone.now().date()
    visibility = False
    for offer_pro in offer_propositions:
        if offer_pro.start_visibility_dissertation <= date_now <= offer_pro.end_visibility_dissertation:
            visibility = True
    return layout.render(request, 'dissertations_list.html',
                         {'date_now': date_now,
                          'dissertations': memories,
                          'student': student,
                          'visibility': visibility})


@login_required
def dissertation_delete(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    if memory.author_is_logged_student(request):
        memory.deactivate()
        dissertation_update.add(request, memory, memory.status, justification="student_set_active_false")
    return redirect('dissertations')


@login_required
def dissertation_detail(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)

    if memory.author_is_logged_student(request):
        off = memory.offer_year_start.offer
        offer_pro = offer_proposition.search_by_offer(off)
        offer_propositions = proposition_offer.search_by_proposition_dissertation(memory.proposition_dissertation)
        count = dissertation.count_submit_by_user(student, off)

        files = dissertation_document_file.find_by_dissertation(memory)
        filename = ""
        for file in files:
            filename = file.document_file.file_name

        count_dissertation_role = dissertation_role.count_by_dissertation(memory)
        count_reader = dissertation_role.count_reader_by_dissertation(memory)
        count_proposition_role = proposition_role.count_by_dissertation(memory)
        proposition_roles = proposition_role.search_by_dissertation(memory)
        jury_visibility = offer_pro.start_jury_visibility <= timezone.now().date() <= offer_pro.end_jury_visibility
        check_edit = offer_pro.start_edit_title <= timezone.now().date() <= offer_pro.end_edit_title

        if count_dissertation_role == 0:
            if count_proposition_role == 0:
                dissertation_role.add('PROMOTEUR', memory.proposition_dissertation.author, memory)
            else:
                for role in proposition_roles:
                    dissertation_role.add(role.status, role.adviser, memory)

        dissertation_roles = dissertation_role.search_by_dissertation(memory)
        return layout.render(request, 'dissertation_detail.html',
                             {'check_edit': check_edit,
                              'count': count,
                              'count_reader': count_reader,
                              'count_dissertation_role': count_dissertation_role,
                              'dissertation': memory,
                              'dissertation_roles': dissertation_roles,
                              'jury_visibility': jury_visibility,
                              'manage_readers': offer_pro.student_can_manage_readers,
                              'filename': filename,
                              'offer_propositions': offer_propositions})
    else:
        return redirect('dissertations')


@login_required
def dissertation_edit(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)

    if memory.author_is_logged_student(request):
        offers = mdl.offer.find_by_student(student)
        offer_pro = offer_proposition.search_by_offer(memory.offer_year_start.offer)

        if memory.status == 'DRAFT' or memory.status == 'DIR_KO':
            if request.method == "POST":
                form = DissertationEditForm(request.POST, instance=memory)
                if form.is_valid():
                    memory = form.save()
                    dissertation_update.add(request, memory, memory.status, justification="student_edit_dissertation")
                    return redirect('dissertation_detail', pk=memory.pk)
                else:
                    form.fields["offer_year_start"].queryset = offer_year.find_by_offer(offers)
                    form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
            else:
                form = DissertationEditForm(instance=memory)
                form.fields["offer_year_start"].queryset = offer_year.find_by_offer(offers)
                form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
            return layout.render(request, 'dissertation_edit_form.html',
                                 {'form': form,
                                  'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES})
        else:
            if offer_pro.start_edit_title <= timezone.now().date() <= offer_pro.end_edit_title:
                if request.method == "POST":
                    form = DissertationTitleForm(request.POST, instance=memory)
                    if form.is_valid():
                        memory = form.save()
                        dissertation_update.add(request, memory, memory.status, justification="student_edit_title")
                        return redirect('dissertation_detail', pk=memory.pk)
                else:
                    form = DissertationTitleForm(instance=memory)
                return layout.render(request, 'dissertation_title_form.html', {'form': form})
            else:
                return redirect('dissertation_detail', pk=memory.pk)
    else:
        return redirect('dissertations')


@login_required
def dissertation_history(request, pk):
    memory = get_object_or_404(dissertation.Dissertation, pk=pk)
    if memory.author_is_logged_student(request):
        dissertation_updates = dissertation_update.search_by_dissertation(memory)
        return layout.render(request, 'dissertation_history.html',
                             {'dissertation': memory,
                              'dissertation_updates': dissertation_updates})
    else:
        return redirect('dissertations')


@login_required
def dissertation_jury_new(request, pk):
    dissert = get_object_or_404(dissertation.Dissertation, pk=pk)
    if dissert.author_is_logged_student(request):
        count_dissertation_role = dissertation_role.count_by_dissertation(dissert)
        count_reader = dissertation_role.count_reader_by_dissertation(dissert)
        offer_pro = offer_proposition.search_by_offer(dissert.offer_year_start.offer)
        if offer_pro.student_can_manage_readers and count_dissertation_role < 5 and count_reader < 3:
            if request.method == "POST":
                form = DissertationRoleForm(request.POST)
                if form.is_valid():
                    data = form.cleaned_data
                    if not dissertation_role.count_by_status_student_dissertation(data['status'],
                                                                                  data['adviser'],
                                                                                  data['dissertation']):
                        form.save()
                        justification = "%s %s" % ("student_add_reader", data['adviser'])
                        dissertation_update.add(request, dissert, dissert.status, justification=justification)
                return redirect('dissertation_detail', pk=dissert.pk)
            else:
                form = DissertationRoleForm(initial={'status': "READER", 'dissertation': dissert})
                return layout.render(request, 'dissertation_reader_edit.html', {'form': form})
        else:
            return redirect('dissertation_detail', pk=dissert.pk)
    else:
        return redirect('dissertations')


@login_required
def dissertation_new(request):
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    offers = mdl.offer.find_by_student(student)
    offer_propositions = offer_proposition.search_by_offers(offers)
    date_now = timezone.now().date()

    if any(o.start_visibility_dissertation <= date_now <= o.end_visibility_dissertation for o in offer_propositions):
        if request.method == "POST":
            form = DissertationForm(request.POST)
            if form.is_valid():
                memory = form.save()
                dissertation_update.add(request, memory, memory.status, justification="student_creation_dissertation")
                return redirect('dissertation_detail', pk=memory.pk)
        else:
            form = DissertationForm(initial={'active': True, 'author': student})

        all_offer_propositions_offers = offer_proposition.get_all_offers()
        form.fields["offer_year_start"].queryset = \
            offer_year.find_by_student_enrollment_and_offers(student, all_offer_propositions_offers)
        form.fields["proposition_dissertation"].queryset = proposition_dissertation.search_by_offers(offers)
        return layout.render(request, 'dissertation_form.html',
                             {'form': form,
                              'defend_periode_choices': dissertation.DEFEND_PERIODE_CHOICES})
    else:
        return redirect('dissertations')


@login_required
def dissertation_reader_delete(request, pk):
    role = get_object_or_404(dissertation_role.DissertationRole, pk=pk)
    memory = role.dissertation
    if memory.author_is_logged_student(request):
        offer_pro = offer_proposition.search_by_offer(memory.offer_year_start.offer)
        if offer_pro.student_can_manage_readers and memory.status == 'DRAFT':
            justification = "%s %s" % ("student_delete_reader", str(role))
            dissertation_update.add(request, memory, memory.status, justification=justification)
            role.delete()
        return redirect('dissertation_detail', pk=memory.pk)
    else:
        return redirect('dissertations')


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
    person = mdl.person.find_by_user(request.user)
    student = mdl.student.find_by_person(person)
    submitted_memories_count = dissertation.count_submit_by_user(student, memory.offer_year_start.offer)

    if memory.author_is_logged_student(request) and submitted_memories_count == 0:
        old_status = memory.status
        new_status = dissertation.get_next_status(memory, "go_forward")
        status_dict = dict(dissertation.STATUS_CHOICES)
        new_status_display = status_dict[new_status]
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
                             {'form': form, 'dissertation': memory, "new_status_display": new_status_display})
    else:
        return redirect('dissertations')
