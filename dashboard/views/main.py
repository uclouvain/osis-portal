##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.utils.translation import ugettext_lazy as _

from base.views import layout
from attribution.utils import permission


@login_required
def home(request):
    # Adapt layout depending on the type of user (student, professor)
    return layout.render(request, "dashboard.html",
                         {'online_application_opened': permission.is_online_application_opened(request.user)})


@login_required
@permission_required('base.is_faculty_administrator', raise_exception=True)
def faculty_administration(request):
    return layout.render(request, "faculty_administrator_dashboard.html", {'online_application_opened': permission.is_online_application_opened(request.user)})


def show_multiple_registration_id_error(request):
    messages.add_message(request, messages.ERROR, _('error_multiple_registration_id'))
    return home(request)




