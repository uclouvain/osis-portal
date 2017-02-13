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
from django.contrib.auth.decorators import login_required, permission_required

from base.models import student as student_mdl
from attestation.queues import student_attestation
from base.views import layout


@login_required
@permission_required('base.is_student', raise_exception=True)
@permission_required('attestation.can_access_attestation', raise_exception=True)
def home(request):
    student = student_mdl.find_by_user(request.user)
    attestations_list_json = student_attestation.fetch_json_attestation_statuses(student.registration_id)
    return layout.render(request, "attestation.html", {'attestations': attestations_list_json.get('attestations')})



