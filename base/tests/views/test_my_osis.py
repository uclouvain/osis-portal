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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from base.tests.factories.person import PersonFactory

FRENCH_LANGUAGE = settings.LANGUAGE_CODE
ENGLISH_LANGUAGE = 'en'


class ProfileLangTest(TestCase):
    def setUp(self):
        self.person = PersonFactory()
        self.person.language = FRENCH_LANGUAGE
        self.person.save()

        self.url = reverse('profile_lang', args=[ENGLISH_LANGUAGE])
        self.client.force_login(self.person.user)

    def test_user_not_logged(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertRedirects(response, '/login/?next={}'.format(self.url))

    def test_language_not_known(self):
        url = reverse('profile_lang', args=["unk"])
        response = self.client.get(url, HTTP_REFERER='/')
        self.person.refresh_from_db()

        self.assertRedirects(response, '/')
        self.assertEqual(self.person.language, FRENCH_LANGUAGE)

    def test_change_language(self):
        response = self.client.get(self.url, HTTP_REFERER='/')
        self.person.refresh_from_db()

        self.assertRedirects(response, '/')
        self.assertEqual(self.person.language, ENGLISH_LANGUAGE)



