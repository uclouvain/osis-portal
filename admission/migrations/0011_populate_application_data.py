# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.exceptions import FieldDoesNotExist
from django.db import migrations

from admission.models.admission_exam_type import AdmissionExamType
from admission.models.answer import Answer
from admission.models.applicant import Applicant
from admission.models.applicant_document_file import ApplicantDocumentFile
from admission.models.application import Application
from admission.models.application_assimilation_criteria import ApplicationAssimilationCriteria
from admission.models.application_document_file import ApplicationDocumentFile
from admission.models.curriculum import Curriculum
from admission.models.person_address import PersonAddress
from admission.models.profession import Profession
from admission.models.secondary_education import SecondaryEducation
from admission.models.secondary_education_exam import SecondaryEducationExam
from admission.models.sociological_survey import SociologicalSurvey


def set_uuid_field(apps, schema_editor):
    """
    Set a random uuid value to all existing rows in all models containing an 'uuid' attribute in database.
    """
    model_classes = [AdmissionExamType, Answer, Applicant, ApplicantDocumentFile, Application,
                     ApplicationAssimilationCriteria, ApplicationDocumentFile, Curriculum, PersonAddress,
                     Profession, SecondaryEducation, SecondaryEducationExam, SociologicalSurvey]
    for model_class in model_classes:
        ids = model_class.objects.values_list('id', flat=True)
        if ids:
            for pk in ids:
                try:
                    model_class.objects.filter(pk=pk).update(uuid=uuid.uuid4())
                except FieldDoesNotExist:
                    break


class Migration(migrations.Migration):

    dependencies = [
        ('admission', '0010_create_sociological_survey'),
    ]

    operations = [
        migrations.RunPython(set_uuid_field),
    ]
