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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################

from django.test import SimpleTestCase

from base.templatetags.api_template_tags import compute_visible_indices, DEFAULT_CONDENSED_PAGINATION_DELTA


class ApiTemplateTagsTestCase(SimpleTestCase):

    def test_should_compute_visible_indices_in_pagination(self):
        pages_count = 20
        pages = [{'number': page+1} for page in range(0, pages_count)]

        visible_indices = compute_visible_indices(pages, int(pages_count/2), DEFAULT_CONDENSED_PAGINATION_DELTA)
        expected_pagination_indices = [1, 8, 9, 10, 11, 12, 20]

        self.assertEqual(visible_indices, expected_pagination_indices)
