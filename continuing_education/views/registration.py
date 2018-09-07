##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2017 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse

from continuing_education.forms.registration import RegistrationForm
from continuing_education.models.admission import Admission
from continuing_education.views.common import display_errors

@login_required
def registration_detail(request, admission_id):
    admission = get_object_or_404(Admission, pk=admission_id)
    return render(request, "registration_detail.html", locals())

@login_required
def registration_edit(request, admission_id):
    registration = get_object_or_404(Admission, pk=admission_id)

    form = RegistrationForm(request.POST or None, instance=registration)
    errors = []
    if form.is_valid():
        registration = form.save()
        return redirect(reverse('registration_detail', kwargs={'admission_id':admission_id}))
    else:
        errors.append(form.errors)
        display_errors(request, errors)

    return render(request, 'registration_form.html', locals())