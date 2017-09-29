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
import factory
import factory.fuzzy
import string
import json
import datetime


def load_score_encoding_sample():
    sample = "assessments/tests/resources/score_encoding_sample.json"
    with open(sample) as file_sample:
        # Reassign publication date as today to pass method assessments.views.score_encoding.is_outdated
        json_obj = json.load(file_sample)
        json_obj['publication_date'] = _get_today_date()
        return json.dumps(json_obj)


def _get_today_date():
    now = datetime.datetime.now()
    return '%s/%s/%s' % (now.day, now.month, now.year)


class ScoreEncodingFactory(factory.DjangoModelFactory):
    class Meta:
        model = 'assessments.ScoreEncoding'

    global_id = factory.fuzzy.FuzzyText(length=10, chars=string.digits)
    document = load_score_encoding_sample()
