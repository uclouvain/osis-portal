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
from django.shortcuts import render, redirect
from admission import models as mdl
from admission.models.enums import document_type
from admission.views import demande_validation, navigation
from admission.forms.attachement import RemoveAttachmentForm
from osis_common.forms import UploadDocumentFileForm
from osis_common.models.document_file import DocumentFile


def update(request, application_id=None):
    application = mdl.application.find_by_id(application_id)
    curriculum_doc_present, letter_motivation_doc_present, past_attachments = check_document_type(application)
    applicant = mdl.applicant.find_by_user(request.user)
    form = UploadDocumentFileForm(initial={'storage_duration': 0, 'update_by': applicant})
    list_choices = document_type.FILE_TYPE_CHOICES
    data = {
        "form": form,
        "tab_active": navigation.ATTACHMENTS_TAB,
        "application": application,
        "applications": mdl.application.find_by_user(request.user),
        "attachments": past_attachments,
        'document_type_choices': list_choices,
        "letter_motivation_doc_present": letter_motivation_doc_present,
        "curriculum_doc_present": curriculum_doc_present,
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    return render(request, "admission_home.html", data)


def check_document_type(application):
    past_attachments = list_attachments(application)
    letter_motivation_doc_present = None
    curriculum_doc_present = None
    for attachment in past_attachments:
        if attachment.description == "letter_motivation":
            letter_motivation_doc_present = True
        if attachment.description == "curriculum":
            curriculum_doc_present = True
    return curriculum_doc_present, letter_motivation_doc_present, past_attachments


def remove_attachment(request, application_id=None):
    if request.method == "POST":
        form = RemoveAttachmentForm(request.POST)
        if form.is_valid():
            attachment_pk = form.cleaned_data['attachment_id']
            attachment_to_remove = DocumentFile.objects.get(pk=attachment_pk)
            safe_document_removal("admission_attachments", attachment_to_remove)
    return redirect('attachments', application_id)


def safe_document_removal(application_name, document):
    if document.application_name == application_name:
        document.delete()


def save_attachments(request, application_id):
    application = mdl.application.find_by_id(application_id)
    data = request.POST
    if request.method == "POST":
        document_form = UploadDocumentFileForm(request.POST, request.FILES)
        if document_form.is_valid():
            file = request.FILES['file']
            file_name = file.name
            if data['input_description']:
                description = data['input_description']
            else:
                description = data['description']
            storage_duration = 720
            application_name = "admission_attachments"
            content_type = file.content_type
            size = file.size
            doc_file = create_document_file(application_name, content_type, description, file, file_name, request, size,
                                            storage_duration)
            create_application_file(application, doc_file)
    return redirect("attachments", application_id)


def create_document_file(application_name, content_type, description, file, file_name, request, size, storage_duration):
    doc_file = DocumentFile(file_name=file_name, file=file,
                            description=description, storage_duration=storage_duration,
                            application_name=application_name, content_type=content_type,
                            size=size, update_by=request.user.username)
    doc_file.save()
    return doc_file


def create_application_file(application, doc_file):
    application_file = mdl.application_document_file.ApplicationDocumentFile()
    application_file.application = application
    application_file.document_file = doc_file
    application_file.save()


def list_attachments(application):
    application_document_files = mdl.application_document_file.find_document_by_application(application)
    document_files = [application_document_file.document_file for application_document_file
                      in application_document_files]
    return document_files
