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
from django.core.exceptions import MultipleObjectsReturned
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

import dashboard.views.home
from attestation.queues import student_attestation
from base.business import student as student_bsn
from base.models import student as student_mdl, person as person_mdl

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.is_student', raise_exception=True)
def download_attestation(request, academic_year, attestation_type):
    try:
        student = student_bsn.find_by_user_and_discriminate(request.user)
    except MultipleObjectsReturned:
        logger.exception('User {} returned multiple students.'.format(request.user.username))
        return dashboard.views.home.show_multiple_registration_id_error(request)

    attestation_pdf = student_attestation.fetch_student_attestation(student.person.global_id,
                                                                    academic_year,
                                                                    attestation_type,
                                                                    request.user)

    if attestation_pdf:
        return _make_pdf_attestation(attestation_pdf, attestation_type)
    else:
        messages.add_message(request, messages.ERROR, _('Student attestations'))
        return redirect(reverse('attestation_home'))


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def download_student_attestation(request, global_id, academic_year, attestation_type):
    attestation_pdf = student_attestation.fetch_student_attestation(global_id,
                                                                    academic_year,
                                                                    attestation_type,
                                                                    request.user)
    if attestation_pdf:
        return _make_pdf_attestation(attestation_pdf, attestation_type)
    else:
        person = person_mdl.find_by_global_id(global_id)
        student = student_mdl.find_by_person(person)
        messages.add_message(request, messages.ERROR, _('Student attestations'))
        return redirect(reverse('attestation_admin_view', args=[student.registration_id]))


def _make_pdf_attestation(attestation_pdf, attestation_type):
    filename = "%s.pdf" % _(attestation_type)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="%s"' % filename
    response.write(attestation_pdf)
    return response
