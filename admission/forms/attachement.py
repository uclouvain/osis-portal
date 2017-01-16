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
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from osis_common.models.document_file import DocumentFile


class RemoveAttachmentForm(forms.Form):
    attachment_id = forms.IntegerField(min_value=0)

    def clean(self):
        cleaned_data = super(RemoveAttachmentForm, self).clean()
        attachment_id = cleaned_data.get('attachment_id')
        if attachment_id:
            try:
                DocumentFile.objects.get(pk=attachment_id)
            except ObjectDoesNotExist:
                self.add_error('attachment_id', _('attachment_does_not_exist'))

