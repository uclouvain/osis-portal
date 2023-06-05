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

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from base.services.utils import ServiceException
from inscription_aux_cours.services.mini_formation import MiniFormationService
from inscription_aux_cours.views.common import CompositionPAEViewMixin


@method_decorator(require_POST, name='dispatch')
class InscrireAUneMiniFormationView(LoginRequiredMixin, CompositionPAEViewMixin, TemplateView):
    name = 'inscrire-mini-formation'

    # TemplateView
    template_name = "inscription_aux_cours/mini_formation/desinscrire.html"
    error_template_name = "inscription_aux_cours/mini_formation/inscrire.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.erreurs = []

    def get_template_names(self):
        if self.erreurs:
            return [self.error_template_name]
        return super().get_template_names()

    @property
    def code_mini_formation(self) -> str:
        return self.request.POST.get('code_mini_formation')

    def post(self, request, *args, **kwargs):
        code_mini_formation = self.code_mini_formation
        try:
            self.inscrire_a_une_mini_formation(code_mini_formation)
        except ServiceException as e:
            self.erreurs = e.messages
        return super().get(request, *args, **kwargs)

    def inscrire_a_une_mini_formation(self, code_mini_formation: str):
        MiniFormationService().inscrire(self.person, self.code_programme, code_mini_formation)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "code_mini_formation": self.code_mini_formation,
            "erreurs": self.erreurs
        }
