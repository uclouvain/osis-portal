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
from django.conf.urls import url, include
from .views import score_encoding

urlpatterns = [
    url(r'^scores_encoding/$', score_encoding.score_encoding, name='scores_encoding'),
    url(r'^scores_encoding/my_scores_sheets/$', score_encoding.scores_sheets, name='my_scores_sheets'),
    url(r'^scores_encoding/my_scores_sheets/ask/([0-9a-z-]+)/$', score_encoding.ask_papersheet, name='ask_papersheet'),
    url(r'^scores_encoding/my_scores_sheets/check/([0-9a-z-]+)/$', score_encoding.check_papersheet, name='check_papersheet'),
    url(r'^scores_encoding/my_scores_sheets/download/([0-9a-z-]+)/$', score_encoding.download_papersheet, name='scores_download'),

    url(r'^administration/', include([
        url(r'^scores_sheets/$', score_encoding.scores_sheets_admin, name='scores_sheets_admin'),
    ])),
]
