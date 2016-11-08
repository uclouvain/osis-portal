##############################################################################
#
# OSIS stands for Open Student Information System. It's an application
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
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU General Public License for more details.
#
#    A copy of this license - GNU General Public License - is available
#    at the root of the source code of this program.  If not,
#    see http://www.gnu.org/licenses/.
#
##############################################################################
from unittest import TestCase
from admission.forms.sociological_survey import SociologicalSurveyForm
from admission.models.sociological_survey import SociologicalSurvey
from admission.tests import data_for_tests as data_model
from admission.models.enums import professional_activity as professional_activity_enum
from admission.models import sociological_survey as mdl_sociological_survey

PROFESSION_EMPLOYEE = 'Employee'


def init_form(data=None):
    return SociologicalSurveyForm(data=data)


class NumberBrotherSistersValidation(TestCase):

    @classmethod
    def setUpClass(cls):
        super(NumberBrotherSistersValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()

    def init_form(self, num_brothers_sisters=None):
        return init_form(data={
            'applicant': self.applicant.id,
            'number_brothers_sisters': num_brothers_sisters
        })

    def test_num_brothers_sisters_none(self):
        form = self.init_form()
        form.is_valid()
        self.assertEqual(form.cleaned_data.get('number_brothers_sisters'), 0)

    def test_num_brothers_sisters_zero(self):
        form = self.init_form(num_brothers_sisters=0)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data.get('number_brothers_sisters'), 0)

    def test_num_brothers_sisters_non_zero(self):
        form = self.init_form(num_brothers_sisters=3)
        form.is_valid()
        self.assertEqual(form.cleaned_data.get('number_brothers_sisters'), 3)


class StudentProfessionValidation(TestCase):

    @classmethod
    def setUpClass(cls):
        super(StudentProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def init_form(self, student_profession_id=None, other_profession=None, adhoc=False):
        return init_form(data={
            'applicant': self.applicant.id,
            'student_profession': student_profession_id,
            'student_profession_other_name': other_profession,
            'student_profession_not_found': adhoc
        })

    def test_profession_no_other_profession(self):
        form = self.init_form(student_profession_id=self.profession.id)
        form.is_valid()
        self.assertEqual(form._get_or_other_student_profession(), self.profession)

    def test_no_profession_no_other_profession(self):
        form = self.init_form()
        form.is_valid()
        self.assertIsNone(form._get_or_other_student_profession())

    def test_profession_and_other_profession(self):
        form = self.init_form(student_profession_id=self.profession.id,
                              other_profession='Triturateur')
        form.is_valid()
        self.assertEqual(form._get_or_other_student_profession(), self.profession)

    def test_no_profession_other_profession_and_adhoc(self):
        form = self.init_form(other_profession='Jongleur', adhoc=True)
        form.is_valid()
        self.assertEqual(form._get_or_other_student_profession().name, form.cleaned_data.get('student_profession_other_name'))
        self.assertTrue(form.cleaned_data.get('student_profession').adhoc)

    def test_no_profession_other_profession_no_adhoc(self):
        form = self.init_form(other_profession='Serveur')
        form.is_valid()
        self.assertIsNone(form._get_or_other_student_profession())


class FatherProfessionValidation(TestCase):
    @classmethod
    def setUpClass(cls):
        super(FatherProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def init_form(self, father_profession_id=None, other_profession=None, adhoc=False):
        return init_form(data={
            'applicant': self.applicant.id,
            'father_profession': father_profession_id,
            'father_profession_other_name': other_profession,
            'father_profession_not_found': adhoc
        })

    def test_profession_no_other_profession(self):
        form = self.init_form(father_profession_id=self.profession.id)
        form.is_valid()
        self.assertEqual(form._get_or_other_father_profession(), self.profession)

    def test_no_profession_no_other_profession(self):
        form = self.init_form()
        form.is_valid()
        self.assertIsNone(form._get_or_other_father_profession())

    def test_profession_and_other_profession(self):
        form = self.init_form(father_profession_id=self.profession.id,
                              other_profession='Triturateur')
        form.is_valid()
        self.assertEqual(form._get_or_other_father_profession(), self.profession)

    def test_no_profession_other_profession_and_adhoc(self):
        form = self.init_form(other_profession='Jongleur', adhoc=True)
        form.is_valid()
        self.assertEqual(form._get_or_other_father_profession().name, form.cleaned_data.get('father_profession_other_name'))
        self.assertTrue(form.cleaned_data.get('father_profession').adhoc)

    def test_no_profession_other_profession_no_adhoc(self):
        form = self.init_form(other_profession='Serveur')
        form.is_valid()
        self.assertIsNone(form._get_or_other_father_profession())


class MotherProfessionValidation(TestCase):
    @classmethod
    def setUpClass(cls):
        super(MotherProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def init_form(self, mother_profession_id=None, other_profession=None, adhoc=False):
        return init_form(data={
            'applicant': self.applicant.id,
            'mother_profession': mother_profession_id,
            'mother_profession_other_name': other_profession,
            'mother_profession_not_found': adhoc
        })

    def test_profession_no_other_profession(self):
        form = self.init_form(mother_profession_id=self.profession.id)
        form.is_valid()
        self.assertEqual(form._get_or_other_mother_profession(), self.profession)

    def test_no_profession_no_other_profession(self):
        form = self.init_form()
        form.is_valid()
        self.assertIsNone(form._get_or_other_mother_profession())

    def test_profession_and_other_profession(self):
        form = self.init_form(mother_profession_id=self.profession.id,
                              other_profession='Triturateur')
        form.is_valid()
        self.assertEqual(form._get_or_other_mother_profession(), self.profession)

    def test_no_profession_other_profession_and_adhoc(self):
        form = self.init_form(other_profession='Jongleur', adhoc=True)
        form.is_valid()
        self.assertEqual(form._get_or_other_mother_profession().name, form.cleaned_data.get('mother_profession_other_name'))
        self.assertTrue(form.cleaned_data.get('mother_profession').adhoc)

    def test_no_profession_other_profession_no_adhoc(self):
        form = self.init_form(other_profession='Serveur')
        form.is_valid()
        self.assertIsNone(form._get_or_other_mother_profession())


class ConjointProfessionValidation(TestCase):
    @classmethod
    def setUpClass(cls):
        super(ConjointProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def init_form(self, conjoint_profession_id=None, other_profession=None, adhoc=False):
        return init_form(data={
            'applicant': self.applicant.id,
            'conjoint_profession': conjoint_profession_id,
            'conjoint_profession_other_name': other_profession,
            'conjoint_profession_not_found': adhoc
        })

    def test_profession_no_other_profession(self):
        form = self.init_form(conjoint_profession_id=self.profession.id)
        form.is_valid()
        self.assertEqual(form._get_or_other_conjoint_profession(), self.profession)

    def test_no_profession_no_other_profession(self):
        form = self.init_form()
        form.is_valid()
        self.assertIsNone(form._get_or_other_conjoint_profession())

    def test_profession_and_other_profession(self):
        form = self.init_form(conjoint_profession_id=self.profession.id,
                              other_profession='Triturateur')
        form.is_valid()
        self.assertEqual(form._get_or_other_conjoint_profession(), self.profession)

    def test_no_profession_other_profession_and_adhoc(self):
        form = self.init_form(other_profession='Jongleur', adhoc=True)
        form.is_valid()
        self.assertEqual(form._get_or_other_conjoint_profession().name,
                         form.cleaned_data.get('conjoint_profession_other_name'))
        self.assertTrue(form.cleaned_data.get('conjoint_profession').adhoc)

    def test_no_profession_other_profession_no_adhoc(self):
        form = self.init_form(other_profession='Serveur')
        form.is_valid()
        self.assertIsNone(form._get_or_other_conjoint_profession())


class PaternalGrandfatherProfessionValidation(TestCase):
    @classmethod
    def setUpClass(cls):
        super(PaternalGrandfatherProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def init_form(self, paternal_grandfather_profession_id=None, other_profession=None, adhoc=False):
        return init_form(data={
            'applicant': self.applicant.id,
            'paternal_grandfather_profession': paternal_grandfather_profession_id,
            'paternal_grandfather_profession_other_name': other_profession,
            'paternal_grandfather_profession_not_found': adhoc
        })

    def test_profession_no_other_profession(self):
        form = self.init_form(paternal_grandfather_profession_id=self.profession.id)
        form.is_valid()
        self.assertEqual(form._get_or_other_paternal_grandfather_profession(), self.profession)

    def test_no_profession_no_other_profession(self):
        form = self.init_form()
        form.is_valid()
        self.assertIsNone(form._get_or_other_paternal_grandfather_profession())

    def test_profession_and_other_profession(self):
        form = self.init_form(paternal_grandfather_profession_id=self.profession.id,
                              other_profession='Triturateur')
        form.is_valid()
        self.assertEqual(form._get_or_other_paternal_grandfather_profession(), self.profession)

    def test_no_profession_other_profession_and_adhoc(self):
        form = self.init_form(other_profession='Jongleur', adhoc=True)
        form.is_valid()
        self.assertEqual(form._get_or_other_paternal_grandfather_profession().name,
                         form.cleaned_data.get('paternal_grandfather_profession_other_name'))
        self.assertTrue(form.cleaned_data.get('paternal_grandfather_profession').adhoc)

    def test_no_profession_other_profession_no_adhoc(self):
        form = self.init_form(other_profession='Serveur')
        form.is_valid()
        self.assertIsNone(form._get_or_other_paternal_grandfather_profession())


class MaternalGrandfatherProfessionValidation(TestCase):
    @classmethod
    def setUpClass(cls):
        super(MaternalGrandfatherProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def init_form(self, maternal_grandfather_profession_id=None, other_profession=None, adhoc=False):
        return init_form(data={
            'applicant': self.applicant.id,
            'maternal_grandfather_profession': maternal_grandfather_profession_id,
            'maternal_grandfather_profession_other_name': other_profession,
            'maternal_grandfather_profession_not_found': adhoc
        })

    def test_profession_no_other_profession(self):
        form = self.init_form(maternal_grandfather_profession_id=self.profession.id)
        form.is_valid()
        self.assertEqual(form._get_or_other_maternal_grandfather_profession(), self.profession)

    def test_no_profession_no_other_profession(self):
        form = self.init_form()
        form.is_valid()
        self.assertIsNone(form._get_or_other_maternal_grandfather_profession())

    def test_profession_and_other_profession(self):
        form = self.init_form(maternal_grandfather_profession_id=self.profession.id,
                              other_profession='Triturateur')
        form.is_valid()
        self.assertEqual(form._get_or_other_maternal_grandfather_profession(), self.profession)

    def test_no_profession_other_profession_and_adhoc(self):
        form = self.init_form(other_profession='Jongleur', adhoc=True)
        form.is_valid()
        self.assertEqual(form._get_or_other_maternal_grandfather_profession().name,
                         form.cleaned_data.get('maternal_grandfather_profession_other_name'))
        self.assertTrue(form.cleaned_data.get('maternal_grandfather_profession').adhoc)

    def test_no_profession_other_profession_no_adhoc(self):
        form = self.init_form(other_profession='Serveur')
        form.is_valid()
        self.assertIsNone(form._get_or_other_maternal_grandfather_profession())


class StudentProfesionnalActivityProfessionValidation(TestCase):

    def init_form_proff(self, professional_activity=None, profession=None):
        return init_form(data={
            'applicant': self.applicant.id,
            'student_professional_activity': professional_activity,
            'student_profession': profession
        })

    @classmethod
    def setUpClass(cls):
        super(StudentProfesionnalActivityProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def test_professional_activity_none_and_profession_none(self):
        form = self.init_form_proff()
        self.assertTrue(form.is_valid())

    def test_no_professional_activity_and_profession_none(self):
        form = self.init_form_proff(professional_activity=professional_activity_enum.NO_PROFESSION)
        self.assertTrue(form.is_valid())

    def test_no_prof_activity_with_profession(self):
        form = self.init_form_proff(professional_activity=professional_activity_enum.NO_PROFESSION,
                                    profession=self.profession.id)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get('student_professional_activity') is not None)

    def test_prof_activity_none_with_profession(self):
        form = self.init_form_proff(profession=self.profession.id)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get('student_professional_activity') is not None)

    def test_prof_activity_valid_and_profession_none(self):
        form = self.init_form_proff(professional_activity=professional_activity_enum.FULL_TIME)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get('student_profession') is not None)


class ConjointProfesionnalActivityProfessionValidation(TestCase):
    def init_form_proff(self, professional_activity=None, conjoint_profession_id=None):
        return init_form(data={
            'applicant': self.applicant.id,
            'conjoint_professional_activity': professional_activity,
            'conjoint_profession': conjoint_profession_id
        })

    @classmethod
    def setUpClass(cls):
        super(ConjointProfesionnalActivityProfessionValidation, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)

    def test_professional_activity_none_and_profession_none(self):
        form = self.init_form_proff()
        self.assertTrue(form.is_valid(), form.errors)

    def test_no_professional_activity_and_profession_none(self):
        form = self.init_form_proff(professional_activity=professional_activity_enum.NO_PROFESSION)
        form.is_valid()
        self.assertTrue(form.is_valid(), form.errors)

    def test_no_prof_activity_with_profession(self):
        form = self.init_form_proff(professional_activity=professional_activity_enum.NO_PROFESSION,
                                    conjoint_profession_id=self.profession.id)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get('conjoint_professional_activity') is not None)

    def test_prof_activity_none_with_profession(self):
        form = self.init_form_proff(conjoint_profession_id=self.profession.id)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get('conjoint_professional_activity') is not None)

    def test_prof_activity_valid_and_profession_none(self):
        form = self.init_form_proff(professional_activity=professional_activity_enum.FULL_TIME)
        self.assertFalse(form.is_valid())
        self.assertTrue(form.errors.get('conjoint_profession') is not None)


class InitNotFoundAndOther(TestCase):
    @classmethod
    def setUpClass(cls):
        super(InitNotFoundAndOther, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)
        cls.profession_adhoc = data_model.get_or_create_profession('Balayeur', True)

    def test_with_profession_not_adhoc(self):
        sociological_survey = SociologicalSurvey(
            applicant=self.applicant,
            student_profession=self.profession,
            father_profession=self.profession,
            mother_profession=self.profession,
            conjoint_profession=self.profession,
            paternal_grandfather_profession=self.profession,
            maternal_grandfather_profession=self.profession
        )
        form = SociologicalSurveyForm(instance=sociological_survey)
        self.assertFalse(form.initial.get('student_profession_not_found'))
        self.assertIsNone(form.initial.get('student_profession_other_name'))
        self.assertFalse(form.initial.get('father_profession_not_found'))
        self.assertIsNone(form.initial.get('father_profession_other_name'))
        self.assertFalse(form.initial.get('mother_profession_not_found'))
        self.assertIsNone(form.initial.get('mother_profession_other_name'))
        self.assertFalse(form.initial.get('conjoint_profession_not_found'))
        self.assertIsNone(form.initial.get('conjoint_profession_other_name'))
        self.assertFalse(form.initial.get('paternal_grandfather_profession_not_found'))
        self.assertIsNone(form.initial.get('paternal_grandfather_profession_other_name'))
        self.assertFalse(form.initial.get('maternal_grandfather_profession_not_found'))
        self.assertIsNone(form.initial.get('maternal_grandfather_profession_other_name'))

    def test_all_None(self):
        form = init_form()
        self.assertFalse(form.initial.get('student_profession_not_found'))
        self.assertIsNone(form.initial.get('student_profession_other_name'))
        self.assertFalse(form.initial.get('father_profession_not_found'))
        self.assertIsNone(form.initial.get('father_profession_other_name'))
        self.assertFalse(form.initial.get('mother_profession_not_found'))
        self.assertIsNone(form.initial.get('mother_profession_other_name'))
        self.assertFalse(form.initial.get('conjoint_profession_not_found'))
        self.assertIsNone(form.initial.get('conjoint_profession_other_name'))
        self.assertFalse(form.initial.get('paternal_grandfather_profession_not_found'))
        self.assertIsNone(form.initial.get('paternal_grandfather_profession_other_name'))
        self.assertFalse(form.initial.get('maternal_grandfather_profession_not_found'))
        self.assertIsNone(form.initial.get('maternal_grandfather_profession_other_name'))

    def test_with_profession_with_adhoc(self):
        sociological_survey = SociologicalSurvey(
            applicant=self.applicant,
            student_profession=self.profession_adhoc,
            father_profession=self.profession_adhoc,
            mother_profession=self.profession_adhoc,
            conjoint_profession=self.profession_adhoc,
            paternal_grandfather_profession=self.profession_adhoc,
            maternal_grandfather_profession=self.profession_adhoc
        )
        form = SociologicalSurveyForm(instance=sociological_survey)
        self.assertTrue(form.initial.get('student_profession_not_found'))
        self.assertEqual(form.initial.get('student_profession_other_name'), self.profession_adhoc.name)
        self.assertTrue(form.initial.get('father_profession_not_found'))
        self.assertEqual(form.initial.get('father_profession_other_name'), self.profession_adhoc.name)
        self.assertTrue(form.initial.get('mother_profession_not_found'))
        self.assertEqual(form.initial.get('mother_profession_other_name'), self.profession_adhoc.name)
        self.assertTrue(form.initial.get('conjoint_profession_not_found'))
        self.assertEqual(form.initial.get('conjoint_profession_other_name'), self.profession_adhoc.name)
        self.assertTrue(form.initial.get('paternal_grandfather_profession_not_found'))
        self.assertEqual(form.initial.get('paternal_grandfather_profession_other_name'), self.profession_adhoc.name)
        self.assertTrue(form.initial.get('maternal_grandfather_profession_not_found'))
        self.assertEqual(form.initial.get('maternal_grandfather_profession_other_name'), self.profession_adhoc.name)


class TestCleanProfessionBeforeSave(TestCase):
    @classmethod
    def setUpClass(cls):
        super(TestCleanProfessionBeforeSave, cls).setUpClass()
        cls.applicant = data_model.get_or_create_applicant()
        cls.profession = data_model.get_or_create_profession(PROFESSION_EMPLOYEE, False)
        cls.profession_adhoc = data_model.get_or_create_profession('Balayeur', True)

    def test_clean_form_from_view(self):
        given_conjoint_profession_name = "Nez"
        given_mother_profession_name = "Obstétricienne"
        given_father_profession_name = "Barman"
        given_student_profession_name = 'Pompier'
        given_maternal_grandfather_profession_name = 'Mineur'
        given_paternal_grandfather_profession_name = 'Cordonnier'
        form = init_form(data={
            'applicant': self.applicant.id,
            'number_brothers_sisters': 2,
            'student_profession_not_found': True,
            'student_profession_other_name': given_student_profession_name,
            'student_professional_activity': professional_activity_enum.FULL_TIME,
            'conjoint_profession_not_found': True,
            'conjoint_profession_other_name': given_conjoint_profession_name,
            'conjoint_professional_activity': professional_activity_enum.FULL_TIME,
            'father_profession_not_found': True,
            'father_profession_other_name': given_father_profession_name,
            'mother_profession_not_found': True,
            'mother_profession_other_name': given_mother_profession_name,
            'maternal_grandfather_profession_not_found': True,
            'maternal_grandfather_profession_other_name': given_maternal_grandfather_profession_name,
            'paternal_grandfather_profession_not_found': True,
            'paternal_grandfather_profession_other_name': given_paternal_grandfather_profession_name,
        })
        self.assertTrue(form.is_valid(), str(form.errors))
        form.save(applicant=self.applicant)
        sociological_survey = mdl_sociological_survey.find_by_applicant(applicant=self.applicant)
        self.assertTrue(sociological_survey.student_profession.adhoc)
        self.assertTrue(sociological_survey.student_profession.name == given_student_profession_name)
        self.assertTrue(sociological_survey.conjoint_profession.adhoc)
        self.assertTrue(sociological_survey.conjoint_profession.name == given_conjoint_profession_name)
        self.assertTrue(sociological_survey.mother_profession.adhoc)
        self.assertTrue(sociological_survey.mother_profession.name == given_mother_profession_name)
        self.assertTrue(sociological_survey.father_profession.adhoc)
        self.assertTrue(sociological_survey.father_profession.name == given_father_profession_name)
        self.assertTrue(sociological_survey.paternal_grandfather_profession.adhoc)
        self.assertTrue(sociological_survey.paternal_grandfather_profession.name == given_paternal_grandfather_profession_name)
        self.assertTrue(sociological_survey.maternal_grandfather_profession.adhoc)
        self.assertTrue(sociological_survey.maternal_grandfather_profession.name == given_maternal_grandfather_profession_name)




