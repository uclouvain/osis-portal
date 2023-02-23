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
from typing import Optional, List

from django.utils.translation import gettext_lazy as _
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST

from base.services.utils import ServiceException
from inscription_aux_cours.services.cours import CoursService
from inscription_aux_cours.views.common import InscriptionAuxCoursViewMixin


@method_decorator(require_POST, name='dispatch')
class InscrireAUnCoursHorsProgrammeView(LoginRequiredMixin, InscriptionAuxCoursViewMixin, View):
    name = 'inscrire-cours-hors-programme'

    @property
    def code_mini_formation(self) -> Optional[str]:
        return self.request.POST.get('code_mini_formation')

    @property
    def codes_cours(self) -> List[str]:
        return self.request.POST.getlist('cours', list())

    def post(self, request, *args, **kwargs):
        erreurs = []
        codes_cours_inscrits = []

        for code_cours in self.codes_cours:
            try:
                self.inscrire_a_un_cours(code_cours)
                codes_cours_inscrits.append(code_cours)
            except ServiceException as e:
                erreurs.extend(formatter_messages_d_erreurs(code_cours, e.messages))

        self.afficher_erreurs(erreurs)

        if codes_cours_inscrits:
            self.afficher_succes(codes_cours_inscrits)

        return redirect(
            reverse(
                "inscription-aux-cours:formulaire-inscription-cours",
                kwargs={"code_programme": self.code_programme}
            )
        )

    def inscrire_a_un_cours(self, code_cours: str) -> None:
        CoursService().inscrire(
            self.person,
            code_programme=self.code_programme,
            code_cours=code_cours,
            code_mini_formation=self.code_mini_formation,
            hors_formulaire=True
        )

    def afficher_erreurs(self, erreurs: List[str]) -> None:
        for erreur in erreurs:
            messages.add_message(self.request, messages.ERROR, erreur)

    def afficher_succes(self, codes_cours: List[str]):
        msg = _('You have been enrolled to {codes_cours}').format(
            codes_cours=", ".join(codes_cours)
        )
        messages.add_message(self.request, messages.SUCCESS, msg)


def formatter_messages_d_erreurs(code_cours: str, messages: List[str]) -> List[str]:
    return [f"{code_cours}: {message}" for message in messages]

