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
import copy
from typing import List, Dict

from django.http import Http404
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from osis_inscription_cours_sdk.model.autorise_inscrire_aux_cours import AutoriseInscrireAuxCours
from osis_inscription_cours_sdk.model.contact_faculte import ContactFaculte
from osis_offer_enrollment_sdk.model.inscription import Inscription
from osis_program_management_sdk.model.programme import Programme

from base.models.person import Person
from base.services.offer_enrollment import InscriptionFormationsService
from inscription_aux_cours.services.autorisation import AutorisationService
from inscription_aux_cours.services.contact import ContactService
from inscription_aux_cours.services.periode import PeriodeInscriptionAuxCoursService
from learning_unit.services.learning_unit import LearningUnitService
from program_management.services.programme import ProgrammeService


class CompositionPAEViewMixin:
    permission_required = "base.is_student"

    @cached_property
    def person(self) -> 'Person':
        return Person.objects.get(user=self.request.user)

    @property
    def code_programme(self) -> str:
        return self.kwargs['code_programme']

    @property
    def sigle_formation(self) -> str:
        return self.programme.sigle

    @cached_property
    def annee_academique(self) -> 'int':
        return PeriodeInscriptionAuxCoursService().get_annee(self.person)

    @cached_property
    def contact(self) -> 'ContactFaculte':
        try:
            return ContactService.get_contact_faculte(
                self.person,
                sigle_formation=self.sigle_formation.replace('11BA', '1BA'),
                annee=self.annee_academique,
                pour_premiere_annee="11BA" in self.sigle_formation,
            )
        except Http404:
            return None

    @cached_property
    def inscription(self) -> 'Inscription':
        inscriptions = InscriptionFormationsService.mes_inscriptions(self.person, annee=self.annee_academique)
        return next(inscription for inscription in inscriptions if inscription.code_programme == self.code_programme)

    @cached_property
    def programme(self) -> 'Programme':
        return recuperer_programmes(self.person, self.annee_academique, [self.inscription])[0]

    @cached_property
    def autorisation(self) -> 'AutoriseInscrireAuxCours':
        return AutorisationService().est_autorise(self.person, self.code_programme)

    def dispatch(self, request, *args, **kwargs):
        if not self.autorisation.autorise:
            return redirect(
                reverse('inscription-aux-cours:non-autorisee', kwargs={'code_programme': self.code_programme})
            )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        return {
            **super().get_context_data(**kwargs),
            'programme': self.programme,
            'person': self.person,
            'contact': self.contact,
        }

    def recuperer_intitules_unites_enseignement(self, codes: List[str]) -> Dict[str, str]:
        data = LearningUnitService.search_learning_unit_and_learning_class_titles(
            year=self.annee_academique, codes=codes, person=self.person
        )
        return {
            row['acronym']: row['title'] for row in data
        }


def recuperer_programmes(person: 'Person', annee: int, inscriptions: List['Inscription']) -> List['Programme']:
    codes = [inscription.code_programme for inscription in inscriptions]
    programmes = ProgrammeService.rechercher(person, annee=annee, codes=codes)

    # exclure doctorat et formation doctorale
    programmes = [
        p for p in programmes if not (ProgrammeService.est_doctorat(p) or ProgrammeService.est_formation_doctorale(p))
    ]

    codes_inscriptions_premiere_annee = [
        inscription.code_programme for inscription in inscriptions if inscription.est_en_premiere_annee
    ]
    return [
        adapter_programme_pour_premiere_annee_de_bachelier(programme)
        if programme.code in codes_inscriptions_premiere_annee
        else programme
        for programme in programmes
    ]


def adapter_programme_pour_premiere_annee_de_bachelier(programme: 'Programme') -> 'Programme':
    copy_programme = copy.copy(programme)
    copy_programme.sigle = generer_sigle_programme_pour_premiere_annee_de_bachelier(programme.sigle)
    copy_programme.intitule_formation = generer_intitule_formation_pour_premiere_annee_de_bachelier(
        programme.intitule_formation
    )
    return copy_programme


def generer_intitule_formation_pour_premiere_annee_de_bachelier(intitule: 'str') -> 'str':
    prefixe = _('First year of')
    return f"{prefixe} {intitule[0].lower()}{intitule[1:]}"


def generer_sigle_programme_pour_premiere_annee_de_bachelier(sigle: 'str') -> 'str':
    return sigle.replace("1BA", "11BA")
