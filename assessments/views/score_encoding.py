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
import json
import logging
from io import BufferedReader

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _

from assessments.services.assessments import AssessmentsService
from base.views import layout

from rest_framework import status

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_encoding(request):
    score_encoding_url = settings.OSIS_SCORE_ENCODING_URL
    score_encoding_vpn_help_url = settings.OSIS_VPN_HELP_URL
    return layout.render(request, "score_encoding.html", locals())


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_sheet_xls(request, learning_unit_code: str):
    content_type = 'application/vnd.ms-excel'
    file = AssessmentsService.get_xls_score_sheet(learning_unit_code, request.user.person)
    return _build_response(content_type, file, request)


@login_required
@permission_required('base.is_tutor', raise_exception=True)
def score_sheet_pdf(request, learning_unit_code: str):
    file = AssessmentsService.get_score_sheet_pdf(learning_unit_code, request.user.person)
    content_type = 'application/pdf'
    return _build_response(content_type, file, request)


def get_filename(temp_file_name: str) -> str:
    filename = temp_file_name
    pos = filename.rfind('/')
    return filename[pos + 1:]


def _build_response(content_type, file, request):
    if isinstance(file, BufferedReader):
        response = HttpResponse(file, content_type=content_type)
        response['Content-Disposition'] = 'attachment; filename=%s' % get_filename(file.name)
        return response
    elif isinstance(file, dict):
        error_status = file.get('error_status')
        message = _('Unexpected error')
        if error_status == status.HTTP_400_BAD_REQUEST or error_status == status.HTTP_401_UNAUTHORIZED:
            if file.get('error_body'):
                message = ". ".join(message for message in json.loads(file.get('error_body')))
        messages.add_message(request, messages.INFO, message, "alert-info")
    return redirect(reverse('students_list'))
