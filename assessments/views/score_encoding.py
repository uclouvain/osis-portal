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
from django.contrib.auth.mixins import PermissionRequiredMixin, LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from django.views import View
from rest_framework import status

from assessments.services.assessments import AssessmentsService

logger = logging.getLogger(settings.DEFAULT_LOGGER)
queue_exception_logger = logging.getLogger(settings.QUEUE_EXCEPTION_LOGGER)


class ScoreSheetXls(LoginRequiredMixin, PermissionRequiredMixin, View):
    permission_required = 'base.is_tutor'
    raise_exception = True
    name = 'scores_sheet_xls'

    def get(self, request, *args, **kwargs):
        file = AssessmentsService.get_xls_score_sheet(self.kwargs['learning_unit_code'], request.user.person)
        if isinstance(file, BufferedReader):
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet; charset=binary'
            response = HttpResponse(file, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename={self.get_filename(file.name)}'

            return response
        elif isinstance(file, dict):
            error_status = file.get('error_status')
            message = _('Unexpected error')
            if error_status in [status.HTTP_400_BAD_REQUEST, status.HTTP_401_UNAUTHORIZED] and file.get('error_body'):
                message = ". ".join(json.loads(file.get('error_body')))
            messages.add_message(request, messages.INFO, message, "alert-info")
        return redirect(reverse('students_list'))

    @staticmethod
    def get_filename(temp_file_name: str) -> str:
        filename = temp_file_name
        pos = filename.rfind('/')
        return filename[pos + 1:]
