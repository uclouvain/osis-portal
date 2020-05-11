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
import logging

from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import MultipleObjectsReturned

from base.views import layout
from dashboard.business import id_data as id_data_bus
from dashboard.views import main as dash_main_view

logger = logging.getLogger(settings.DEFAULT_LOGGER)


@login_required
@permission_required('base.is_student', raise_exception=True)
def home(request):
    try:
        data = id_data_bus.get_student_id_data(request.user)
    except MultipleObjectsReturned:
        logger.exception('User {} returned multiple students.'.format(request.user.username))
        return dash_main_view.show_multiple_registration_id_error(request)
    return layout.render(request, "student/personal_data.html", data)

