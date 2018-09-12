##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2018 Université catholique de Louvain (http://www.uclouvain.be)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest import skip

from django.contrib.auth.models import Permission
from django.core.urlresolvers import reverse
from django.test import TestCase, Client

from assessments.tests.factories.score_encoding import ScoreEncodingFactory
from assessments.views import score_encoding
from base.tests.models import test_tutor
from django.contrib.auth.models import User


class DownloadPaperSheetTest(TestCase):
    def setUp(self):
        self.score_encoding = ScoreEncodingFactory()
        self.global_id = self.score_encoding.global_id
        self.tutor = test_tutor.create_tutor()
        self.tutor.person.user = User.objects.create_user('testo', password='testopw')
        self.tutor.person.save()
        perm = Permission.objects.get(codename="is_tutor")
        self.tutor.person.user.user_permissions.add(perm)

    @skip
    def test_when_score_sheet(self):
        self.tutor.person.global_id = self.global_id
        self.tutor.person.save()
        c = Client()
        c.force_login(self.tutor.person.user)
        url = reverse('scores_download', args=[self.global_id])
        response = c.get(url)
        self.assertEquals(response.content, score_encoding.print_scores(self.global_id))

    def test_when_no_score_sheet(self):
        self.tutor.person.global_id = "0124"
        self.tutor.person.save()
        c = Client()
        c.force_login(self.tutor.person.user)
        url = reverse('scores_download', args=["0124"])
        response = c.get(url)
        self.assertEqual(response.context['scores_sheets_unavailable'], True)
