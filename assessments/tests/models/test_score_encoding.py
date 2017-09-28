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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
import datetime
import json

from django.test import TestCase

from assessments.models import score_encoding as mdl_score_encoding


class ScoreEncodingTest(TestCase):
    def setUp(self):
        self.score_encoding = create_score_encoding()
        self.global_id = self.score_encoding.global_id

    def test_find_by_global_id(self):
        score_encoding = mdl_score_encoding.find_by_global_id(global_id=self.global_id)
        self.assertEqual(score_encoding, self.score_encoding, "Wrong score encoding returned")

        score_encoding = mdl_score_encoding.find_by_global_id(global_id="101245")
        self.assertIsNone(score_encoding, "Should return no score encoding")

    def test_insert_or_update_document(self):
        new_document = get_sample()
        score_encoding = mdl_score_encoding.insert_or_update_document("1202151", new_document)
        self.assertJSONEqual(score_encoding.document, new_document, "Problem when inserting new document")

        mdl_score_encoding.insert_or_update_document(self.global_id, new_document)
        self.score_encoding.refresh_from_db()
        self.assertJSONEqual(self.score_encoding.document, new_document, "Problem when updating document")


sample_1 = "assessments/tests/resources/score_encoding_sample.json"
invalid_sample = "assessments/tests/resources/invalid_sample.json"
undated_sample = "assessments/tests/resources/undated_sample.json"


def create_score_encoding(global_id="001254"):
    document = get_sample()
    score_encoding = mdl_score_encoding.ScoreEncoding(global_id=global_id, document=document)
    score_encoding.save()
    return score_encoding


def create_invalid_score_encoding(global_id):
    invalid_document = get_invalid_sample()
    score_encoding = mdl_score_encoding.ScoreEncoding(global_id=global_id, document=invalid_document)
    score_encoding.save()
    return score_encoding


def load_sample(sample_path):
    with open(sample_path) as file_sample:
        return file_sample.read()


def get_sample():
    sample = get_old_sample()
    return update_publication_date(sample)


def get_old_sample():
    return load_sample(sample_1)


def get_invalid_sample():
    return load_sample(invalid_sample)


def get_undated_sample():
    return load_sample(undated_sample)


def update_publication_date(sample):
    json_sample = json.loads(sample)
    json_sample['publication_date'] = get_today_date()
    return json.dumps(json_sample)


def get_today_date():
    now = datetime.datetime.now()
    return '%s/%s/%s' % (now.day, now.month, now.year)




