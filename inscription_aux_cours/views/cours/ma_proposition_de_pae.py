##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2023 Université catholique de Louvain (http://www.uclouvain.be)
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
from typing import Optional

from django.http import HttpResponseForbidden
from django.utils.functional import cached_property

from django.views.generic import TemplateView
from django.urls import reverse

from base.views.common import access_denied
from continuing_education.views.common import display_error_messages
from base.services.utils import ServiceException
from django.shortcuts import redirect

from inscription_aux_cours.services.pdf_proposition_pae import PdfPropositionPaeService
from inscription_aux_cours.views.common import CompositionPAEViewMixin


class MaPropositionDePaeView(TemplateView, CompositionPAEViewMixin):
    name = "ma-proposition-de-pae"

    @property
    def uuid_fichier(self) -> Optional[str]:
        return self.kwargs.get('uuid')

    def get(self, request, *args, **kwargs):
        try:
            if self.ma_proposition_de_pae.get('links'):
                return redirect(self.ma_proposition_de_pae['links']['download'])
        except ServiceException as e:
            if e.status == HttpResponseForbidden.status_code:
                return access_denied(request=request, *args, **kwargs)
            display_error_messages(request, e.messages)
        display_error_messages(self.request, self.ma_proposition_de_pae['message'])
        return redirect(reverse("dashboard_home"))

    @cached_property
    def ma_proposition_de_pae(self):
        if self.uuid_fichier:
            return PdfPropositionPaeService().recuperer_par_uuid(self.person, uuid_fichier=self.uuid_fichier)
        return PdfPropositionPaeService().recuperer_par_code_programme(self.person, code_programme=self.code_programme)
