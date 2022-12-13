#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2022 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from base.services.utils import ServiceException
from continuing_education.views.common import display_error_messages, display_success_messages
from inscription_aux_cours.services.formulaire_inscription import FormulaireInscriptionService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


@method_decorator(require_POST, name='dispatch')
class SoumettrePropositionView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = 'soumettre-proposition'

    # TemplateView
    template_name = "inscription_aux_cours/cours/blocks/soumettre_proposition.html"

    def post(self, request, *args, **kwargs):
        try:
            pass
            #self.soumettre_proposition()
        except ServiceException as e:
            display_error_messages(request, e.messages)
        display_success_messages(request, _("Proposition of annual program successfully submitted"))
        return super().get(request, *args, **kwargs)

    def soumettre_proposition(self):
        FormulaireInscriptionService().soumettre_proposition(
            self.person,
            code_programme=self.code_programme,
        )

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'proposition_deja_soumise': True,
        }
