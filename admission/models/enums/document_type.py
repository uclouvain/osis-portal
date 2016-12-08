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


ID_CARD = 'ID_CARD'
LETTER_MOTIVATION = 'LETTER_MOTIVATION'
ID_PICTURE = 'ID_PICTURE'
NATIONAL_DIPLOMA_VERSO = 'NATIONAL_DIPLOMA_VERSO'
NATIONAL_DIPLOMA_RECTO = 'NATIONAL_DIPLOMA_RECTO'
INTERNATIONAL_DIPLOMA_VERSO = 'INTERNATIONAL_DIPLOMA_VERSO'
INTERNATIONAL_DIPLOMA_RECTO = 'INTERNATIONAL_DIPLOMA_RECTO'
TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO = 'TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO'
TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO = 'TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO'
HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO = 'HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO'
HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO = 'HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO'
TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO = 'TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO'

TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO = 'TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO'
EQUIVALENCE = 'EQUIVALENCE'
ADMISSION_EXAM_CERTIFICATE = 'ADMISSION_EXAM_CERTIFICATE'
PROFESSIONAL_EXAM_CERTIFICATE = 'PROFESSIONAL_EXAM_CERTIFICATE'
LANGUAGE_EXAM_CERTIFICATE = 'LANGUAGE_EXAM_CERTIFICATE'
RESIDENT_LONG_DURATION = 'RESIDENT_LONG_DURATION'
ID_FOREIGN_UNLIMITED = 'ID_FOREIGN_UNLIMITED'
ATTACHMENT_26 = 'ATTACHMENT_26'
REFUGEE_CARD = 'REFUGEE_CARD'
FAMILY_COMPOSITION = 'FAMILY_COMPOSITION'
BIRTH_CERTIFICATE = 'BIRTH_CERTIFICATE'
RESIDENT_CERTIFICATE = 'RESIDENT_CERTIFICATE'
STATELESS_CERTIFICATE = 'STATELESS_CERTIFICATE'
FOREIGN_INSCRIPTION_CERTIFICATE = 'FOREIGN_INSCRIPTION_CERTIFICATE'
SUBSIDIARY_PROTECTION_DECISION = 'SUBSIDIARY_PROTECTION_DECISION'
RESIDENCE_PERMIT = 'RESIDENCE_PERMIT'
PAYCHECK_1 = 'PAYCHECK_1'
PAYCHECK_2 = 'PAYCHECK_2'
PAYCHECK_3 = 'PAYCHECK_3'
PAYCHECK_4 = 'PAYCHECK_4'
PAYCHECK_5 = 'PAYCHECK_5'
PAYCHECK_6 = 'PAYCHECK_6'
CPAS = 'CPAS'
TUTORSHIP_CERTIFICATE = 'TUTORSHIP_CERTIFICATE'
OTHER = 'OTHER'
SCHOLARSHIP_CFWB = 'SCHOLARSHIP_CFWB'
SCHOLARSHIP_DEVELOPMENT_COOPERATION = 'SCHOLARSHIP_DEVELOPMENT_COOPERATION'

CURRICULUM = 'CURRICULUM'

DOCUMENT_TYPE_CHOICES = ((ID_CARD, 'identity_card', '', ''),
                         (LETTER_MOTIVATION, 'letter_motivation', '', ''),
                         (ID_PICTURE, 'id_picture', '', ''),
                         (NATIONAL_DIPLOMA_VERSO, 'national_diploma_verso', '', ''),
                         (NATIONAL_DIPLOMA_RECTO, 'national_diploma_recto', '', ''),
                         (INTERNATIONAL_DIPLOMA_VERSO, 'international_diploma_verso', '', ''),
                         (INTERNATIONAL_DIPLOMA_RECTO, 'international_diploma_recto', '', ''),
                         (TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO, 'translated_international_diploma_verso', '', ''),
                         (TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO, 'translated_international_diploma_recto', '', ''),
                         (HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO, 'high_school_scores_transcript_recto', '', ''),
                         (HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO, 'high_school_scores_transcript_verso', '', ''),
                         (TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO,
                         'translated_high_school_scores_transcript_recto', '', ''),
                         (TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO,
                         'translated_high_school_scores_transcript_verso', '', ''),
                         (EQUIVALENCE, 'equivalence', '', ''),
                         (ADMISSION_EXAM_CERTIFICATE, 'admission_exam_certificate', '', ''),
                         (PROFESSIONAL_EXAM_CERTIFICATE, 'professional_exam_certificate', '', ''),
                         (LANGUAGE_EXAM_CERTIFICATE, 'language_exam_certificate', '', ''),
                         (RESIDENT_LONG_DURATION, 'resident_long_duration', '', ''),
                         (ID_FOREIGN_UNLIMITED, 'id_foreign_unlimited', '', ''),
                         (ATTACHMENT_26, 'attachment_26', '', ''),
                         (REFUGEE_CARD, 'refugee_card', '', ''),
                         (FAMILY_COMPOSITION, 'family_composition', '', ''),
                         (BIRTH_CERTIFICATE, 'birth_certificate', '', ''),
                         (RESIDENT_CERTIFICATE, 'resident_certificate', '', ''),
                         (STATELESS_CERTIFICATE, 'stateless_certificate', '', ''),
                         (FOREIGN_INSCRIPTION_CERTIFICATE, 'foreign_inscription_certificate', '', ''),
                         (SUBSIDIARY_PROTECTION_DECISION, 'subsidiary_protection_decision', '', ''),
                         (RESIDENCE_PERMIT, 'residence_permit', '', ''),
                         (PAYCHECK_1, 'paycheck_1', '', ''),
                         (PAYCHECK_2, 'paycheck_2', '', ''),
                         (PAYCHECK_3, 'paycheck_3', '', ''),
                         (PAYCHECK_4, 'paycheck_4', '', ''),
                         (PAYCHECK_5, 'paycheck_5', '', ''),
                         (PAYCHECK_6, 'paycheck_6', '', ''),
                         (CPAS, 'cpas', '', ''),
                         (TUTORSHIP_CERTIFICATE, 'tutorship_certificate', '', ''),
                         (OTHER, 'other', '', ''),
                         (SCHOLARSHIP_CFWB, 'scholarship_cfwb', '', ''),
                         (SCHOLARSHIP_DEVELOPMENT_COOPERATION, 'scholarship_development_cooperation', '', ''),
                         (CURRICULUM, 'curriculum', '', ''))


def find(document_type):
    for l in DOCUMENT_TYPE_CHOICES:
        if document_type in l:
            return l

