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
from typing import Optional

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.views.generic import TemplateView

from base.services.utils import ServiceException
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin
from learning_unit.services.classe import ClasseService
from learning_unit.services.learning_unit import LearningUnitService


@method_decorator(require_POST, name='dispatch')
class DesinscrireAUnCoursHorsProgrammeView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, TemplateView):
    name = 'desinscrire-cours-hors-programme'

    # TemplateView
    template_name = "inscription_aux_cours/cours/desinscrire_hors_programme.html"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.erreurs = []

    @property
    def code_mini_formation(self) -> Optional[str]:
        return self.request.POST.get('code_mini_formation')

    @property
    def code_cours(self) -> str:
        return self.request.POST.get('code_cours')

    def post(self, request, *args, **kwargs):
        try:
            self.desinscrire_a_un_cours()
        except ServiceException as e:
            self.erreurs = e.messages

        return super().get(request, *args, **kwargs)

    def get_intitule_cours(self) -> str:
        result = LearningUnitService.search_learning_units(
            self.person,
            year=self.annee_academique,
            learning_unit_codes=[self.code_cours]
        )
        if result:
            return result[0]['title']


        result = ClasseService.rechercher_classes(
            self.person,
            annee=self.annee_academique,
            codes=self.codes_cours_du_programme_annuel
        )
        if result:
            return result[0]['intitule']
        return ""

    def desinscrire_a_un_cours(self):
        CoursService().desinscrire(
            self.person,
            code_programme=self.code_programme,
            code_cours=self.code_cours,
            code_mini_formation=self.code_mini_formation,
        )

    def get_credits_inscription_cours(self) -> Optional[float]:
        programme_annuel = CoursService().recuperer_programme_annuel(self.person, self.code_programme)
        inscriptions = programme_annuel.tronc_commun
        inscriptions += [
            inscription
            for insccriptions_a_une_mini_formation in programme_annuel['mini_formations']
            for inscription in insccriptions_a_une_mini_formation['cours']
        ]
        inscription = next(
            (inscription for inscription in inscriptions if inscription['code'] == self.code_cours),
            None
        )
        if inscription:
            return inscription.credits
        return None

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            "code_mini_formation": self.code_mini_formation,
            "code_cours": self.code_cours,
            "code_programme": self.code_programme,
            "erreurs": self.erreurs,
            "intitule_cours": self.get_intitule_cours(),
            "credits": self.get_credits_inscription_cours(),
        }