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
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied

from base.views import layout
from osis_common.utils import native


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('base.is_administrator'), login_url='/403/', redirect_field_name=None)
def data(request):
    sql_data_management_enabled = _is_sql_data_management_enabled()
    return layout.render(request, 'admin/data.html', locals())


@login_required
@user_passes_test(lambda u: u.is_staff and u.has_perm('base.is_administrator'), login_url='/403/', redirect_field_name=None)
def data_maintenance(request):
    if not _is_sql_data_management_enabled():
        raise PermissionDenied("SQL data management is not enabled in this environment")

    sql_command = request.POST.get('sql_command')
    results = native.execute(sql_command)
    forbidden_sql_keywords = native.get_forbidden_sql_keywords()
    return layout.render(request, "admin/data_maintenance.html", {'section': 'data_maintenance',
                                                                  'sql_command': sql_command,
                                                                  'results': results,
                                                                  'forbidden_sql_keywords': forbidden_sql_keywords
                                                                  }
                         )


def _is_sql_data_management_enabled():
    if hasattr(settings, 'ENABLE_SQL_DATA_MANAGEMENT'):
        return settings.ENABLE_SQL_DATA_MANAGEMENT
    return False
