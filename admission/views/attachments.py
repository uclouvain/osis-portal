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


def update(request, application_id=None):
    if application_id:
        application = mdl.application.find_by_id(application_id)
    else:
        application = mdl.application.init_application(request.user)
    past_attachments = list_attachments(application)
    attachments_available = attachments_left_available(len(past_attachments))
    UploadDocumentFileFormSet = formset_factory(UploadDocumentFileForm, extra=0, max_num=attachments_available)
    if request.method == "POST":
        document_formset = UploadDocumentFileFormSet(request.POST, request.FILES)
        if document_formset.is_valid():
            for document in document_formset:
                save_document_from_form(document, request.user, application)
    elif request.method == "GET":
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
    return render(request, "admission_home.html", data)


def remove_attachment(request):
    """
    View used to remove previous attachments.
    :param request
    """
    if request.method == "POST":
        form = RemoveAttachmentForm(request.POST)
        if form.is_valid():
            attachment_pk = form.cleaned_data['attachment_id']
            # form is valid ensure that there is a document having that pk value
            attachment_to_remove = DocumentFile.objects.get(pk=attachment_pk)
            safe_document_removal("admission_attachments", attachment_to_remove)
    return redirect(update)


def safe_document_removal(application_name, document):
    """
    Safely remove a document by ensuring that the user is the one
    that owns the file and the application_name is the correct one.
    :param application_name: a string
    :param document
    :return:
    """
    if document.application_name == application_name:
        document.delete()


def list_attachments(application):
    """
    Returns the list of all the attachments uploaded by the user.
    :param application
    :return: an array of dictionnary
    """
    application_document_files = mdl.application_document_file.find_document_by_application(application)
    return [application_document_file.document_file for application_document_file
            in application_document_files]


def attachments_left_available(number_attachments_uploaded):
    """
    Compute the number of attachments left that the user can upload.
    :param number_attachments_uploaded: number of attachments already uploaded
    :return: slot available
    """
    max_num_attachments = 5
    num_attachments_uploaded = number_attachments_uploaded
    return max_num_attachments - num_attachments_uploaded


def save_document_from_form(document, user, application):
    """
    Save a document (attachment) from a form.
    :param document: an UploadDocumentForm received from a POST request.
    :param user: the current user
    :param application: the current application
    :return:
    """
    file_name = document.cleaned_data['file_name']
    file = document.cleaned_data['file']
    description = document.cleaned_data['description']
    # Never trust a user. They could change the hidden input values.
    # Ex: user, application_name, storage_duration, etc.
    storage_duration = 0
    application_name = "admission_attachments"
    content_type = file.content_type
    size = file.size

    doc_file = DocumentFile(file_name=file_name, file=file,
                            description=description, storage_duration=storage_duration,
                            application_name=application_name, content_type=content_type,
                            size=size, update_by=user.username)
    doc_file.save()
    application_file = mdl.application_document_file.ApplicationDocumentFile()
    application_file.application = application
    application_file.document_file = doc_file
    application_file.save()
