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

import json
from django.test import TestCase
from performance.models import student_performance


class CouchBasePerformanceTest(TestCase):

    def test_document_creation(self):
        document = {
            "registration_id": "64641200",
            "first_name": "Eddy",
            "last_name": "Ndizera",
            "academic_years": [
                {
                    "year": "2015 - 2016",
                    "anac": "2015",
                    "programs": [
                        {
                            "mention_explanation": "",
                            "acronym": "SINF2MS/G",
                            "program_id": "13128",
                            "title": "Master [120] en sciences informatiques, à finalité spécialisée",
                            "total_ECTS": "62.0",
                            "results": [
                                {
                                    "month": "janvier",
                                    "mean": "-",
                                    "mention": "-",
                                    "insc": "IS"
                                },
                                {
                                    "month": "juin",
                                    "mean": "13.85",
                                    "mention": "R",
                                    "insc": "EP"
                                },
                                {
                                    "month": "septembre",
                                    "mean": "-",
                                    "mention": "-",
                                    "insc": "-"
                                }
                            ],
                            "learning_units": [
                                {
                                    "acronym": "LINGI2132",
                                    "title": "Languages and translators",
                                    "insc": "I",
                                    "credit_report": "K",
                                    "credits": "6.0",
                                    "exams": [
                                        {
                                            "session": "janvier",
                                            "score": "-",
                                            "status_exam": "-"
                                        },
                                        {
                                            "session": "juin",
                                            "score": "15.0",
                                            "status_exam": "I"
                                        },
                                        {
                                            "session": "septembre",
                                            "score": "-",
                                            "status_exam": "-"
                                        }
                                    ]

                                }
                            ]
                        }
                    ]
                }
            ]
        }

        document_id = "64641200-2015-SINF2MSG"
        student_performance.save_document(document_id, document)

        persisted_document = student_performance.fetch_document(document_id)
        self.assertEqual(document, persisted_document.value, "The document is different from the persisted document.")
