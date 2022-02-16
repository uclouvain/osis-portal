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
from django.conf.urls import url
from django.urls import path, include

from .views import score_encoding
from .views.attendance_marks.offers import SelectOffer
from .views.attendance_marks.outside_period import OutsidePeriod

app_name = "assessments"
urlpatterns = [
    url(r'^scores_encoding/$', score_encoding.score_encoding, name='scores_encoding'),
    url(r'^scores_encoding/xls/(?P<learning_unit_code>[0-9A-Za-z_-]+)/',
        score_encoding.score_sheet_xls,
        name='scores_sheet_xls',
        ),
    url(r'^scores_encoding/pdf/(?P<learning_unit_code>[0-9A-Za-z-_]+)/$',
        score_encoding.score_sheet_pdf,
        name='scores_sheet_pdf',
        ),
    path('attendance_marks/', include([
        path('select_offer/', SelectOffer.as_view(), name=SelectOffer.name),
        path('outside_period/', OutsidePeriod.as_view(), name=OutsidePeriod.name),
    ]))
]
