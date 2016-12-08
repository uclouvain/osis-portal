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
from django.forms import formset_factory
from admission.models.enums import application_type
from django.utils.translation import ugettext_lazy as _


def update(request, application_id=None):
    application = mdl.application.find_by_id(application_id)
    past_attachments = list_attachments(application)
    UploadDocumentFileFormSet = formset_factory(UploadDocumentFileForm, extra=0)
    document_formset = UploadDocumentFileFormSet()
    applicant = mdl.applicant.find_by_user(request.user)
    remove_attachment_form = RemoveAttachmentForm()
    list_choices = [x[1] for x in document_type.DOCUMENT_TYPE_CHOICES]
    data = {
        "tab_active": navigation.ATTACHMENTS_TAB,
        "application": application,
        "applications": mdl.application.find_by_user(request.user),
        "document_formset": document_formset,
        "attachments": past_attachments,
        "removeAttachmentForm": remove_attachment_form,
        "list_choices": list_choices
    }
    data.update(demande_validation.get_validation_status(application, applicant))
    letter_motivation_doc_present = False
    curriculum_doc_present = False

    if application.application_type ==  application_type.ADMISSION:
        for p in past_attachments:
            if p.description == 'letter_motivation':
                letter_motivation_doc_present=True
            if p.description == 'curriculum':
                curriculum_doc_present=True
    data.update({'letter_motivation_doc_present': letter_motivation_doc_present,
                 'curriculum_doc_present': curriculum_doc_present})
    return render(request, "admission_home.html", data)


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


def list_attachments(application):
    application_document_files = mdl.application_document_file.find_document_by_application(application)
    document_files =[application_document_file.document_file for application_document_file
            in application_document_files]

    for doc in document_files:
        doc.description = _(doc.description)

    return document_files


def save_attachments(request, application_id):
    application = mdl.application.find_by_id(application_id)
    UploadDocumentFileFormSet = formset_factory(UploadDocumentFileForm, extra=0)
    if request.method == "POST":
        document_formset = UploadDocumentFileFormSet(request.POST, request.FILES)
        if document_formset.is_valid():
            for document in document_formset:
                file_name = document.cleaned_data['file_name']
                file = document.cleaned_data['file']
                description = document.cleaned_data['description']
                storage_duration = 720
                application_name = "admission_attachments"
                content_type = file.content_type
                size = file.size
                doc_file = DocumentFile(file_name=file_name, file=file,
                                        description=description, storage_duration=storage_duration,
                                        application_name=application_name, content_type=content_type,
                                        size=size, update_by=request.user.username)
                doc_file.save()
                application_file = mdl.application_document_file.ApplicationDocumentFile()
                application_file.application = application
                application_file.document_file = doc_file
                application_file.save()
    return redirect("attachments", application_id)
