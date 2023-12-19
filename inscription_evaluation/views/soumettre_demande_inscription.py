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
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_GET
from django.views.generic import View
from django.utils.translation import gettext_lazy as _

from continuing_education.views.common import display_error_messages, display_success_messages
from inscription_evaluation.services.recapitulatif import RecapitulatifService
from inscription_evaluation.views.common import InscriptionEvaluationViewMixin
from base.services.utils import ServiceException


@method_decorator(require_GET, name='dispatch')
class SoumettreDemandeInscriptionView(LoginRequiredMixin, InscriptionEvaluationViewMixin, View):
    name = 'soumettre-demande-inscription'

    # TemplateView
    template_name = "inscription_evaluation/blocks/soumettre_demande_inscription.html"

    def get(self, request, *args, **kwargs):
        try:
            # self.soumettre_demande()
            display_success_messages(
                request,
                self.get_success_message(),
            )
        except ServiceException as e:
            display_error_messages(request, e.messages)
        return redirect('inscription-evaluation:recapitulatif', code_programme=self.code_programme)

    def get_success_message(self):
        return _(
            "Evaluation registration form has been successfully submitted. "
            "A confirmation email will be sent to %(email)s."
        ) % {'email': self.request.user.person.email}

    def soumettre_demande(self):
        RecapitulatifService().soumettre(
            self.person,
            code_programme=self.code_programme,
        )
