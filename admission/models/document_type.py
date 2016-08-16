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
#

DOCUMENT_TYPE_CHOICES = ((
                             'ID_CARD', 'identity_card', '', ''),
                            ('LETTER_MOTIVATION', 'letter_motivation', '', ''),
                            ('ID_PICTURE', 'id_picture', '', ''),
                            ('NATIONAL_DIPLOMA_VERSO', 'national_diploma_verso', '', ''),
                            ('NATIONAL_DIPLOMA_RECTO', 'national_diploma_recto', '', ''),
                            ('INTERNATIONAL_DIPLOMA_VERSO', 'international_diploma_verso', '', ''),
                            ('INTERNATIONAL_DIPLOMA_RECTO', 'international_diploma_recto', '', ''),
                            ('TRANSLATED_INTERNATIONAL_DIPLOMA_VERSO', 'translated_international_diploma_verso', '', ''),
                            ('TRANSLATED_INTERNATIONAL_DIPLOMA_RECTO', 'translated_international_diploma_recto', '', ''),
                            ('HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO', 'high_school_scores_transcript_recto', '', ''),
                            ('HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO', 'high_school_scores_transcript_verso', '', ''),
                            ('TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_RECTO',
                            'translated_high_school_scores_transcript_recto', '', ''),
                            ('TRANSLATED_HIGH_SCHOOL_SCORES_TRANSCRIPT_VERSO',
                            'translated_high_school_scores_transcript_verso', '', ''),
                            ('EQUIVALENCE', 'equivalence', '', ''),
                            ('ADMISSION_EXAM_CERTIFICATE', 'admission_exam_certificate', '', ''),
                            ('PROFESSIONAL_EXAM_CERTIFICATE', 'professional_exam_certificate', '', ''),
                            ('RESIDENT_LONG_DURATION', '', '', ''),
                            ('ID_FOREIGN_UNLIMITED', '', '', ''),
                            ('ATTACHMENT_26', '', '', ''),
                            ('REFUGEE_CARD', '', '', ''),
                            ('FAMILY_COMPOSITION', '', '', ''),
                            ('BIRTH_CERTIFICATE', '', '', ''),
                            ('RESIDENT_CERTIFICATE', '', '', ''),
                            ('STATELESS_CERTIFICATE', '', '', ''),
                            ('FOREIGN_INSCRIPTION_CERTIFICATE', '', '', ''),
                            ('SUBSIDIARY_PROTECTION_DECISION', '', '', ''),
                            ('RESIDENCE_PERMIT', '', '', ''),
                            ('PAYCHECK', '', '', ''),
                            ('CPAS', '', '', ''),
                            ('TUTORSHIP_CERTIFICATE', '', '', ''),
                            ('OTHER', '', '', ''),  # Hang va vérifier la signification de "les documents demandés pour l’étudiant à adapter pour la personne concernée. "
                            ('SCHOLARSHIP_CFWB', '', '', ''),
                            ('SCHOLARSHIP_DEVELOPMENT_COOPERATION', '', '', ''))


