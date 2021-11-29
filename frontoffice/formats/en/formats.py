# ##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2021 Université catholique de Louvain (http://www.uclouvain.be)
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
# ##############################################################################
DATE_INPUT_FORMATS = [
    '%d/%m/%Y', '%d/%m/%y',             # '25/10/2006', '25/10/06'
    # '%b %d %Y', '%b %d, %Y',          # 'Oct 25 2006', 'Oct 25, 2006'
    # '%d %b %Y', '%d %b, %Y',          # '25 Oct 2006', '25 Oct, 2006'
    # '%B %d %Y', '%B %d, %Y',          # 'October 25 2006', 'October 25, 2006'
    # '%d %B %Y', '%d %B, %Y',          # '25 October 2006', '25 October, 2006'
]
DATETIME_INPUT_FORMATS = [
    '%Y-%m-%d %H:%M:%S',                # '2006-10-25 14:30:59'
    '%Y-%m-%d %H:%M:%S.%f',             # '2006-10-25 14:30:59.000200'
    '%Y-%m-%d %H:%M',                   # '2006-10-25 14:30'
    '%Y-%m-%d',                         # '2006-10-25'
    '%d/%m/%Y %H:%M:%S',                # '25/10/2006 14:30:59'
    '%d/%m/%Y %H:%M:%S.%f',             # '25/10/2006 14:30:59.000200'
    '%d/%m/%Y %H:%M',                   # '25/10/2006 14:30'
    '%d/%m/%Y',                         # '25/10/2006'
    '%d/%m/%y %H:%M:%S',                # '25/10/06 14:30:59'
    '%d/%m/%y %H:%M:%S.%f',             # '25/10/06 14:30:59.000200'
    '%d/%m/%y %H:%M',                   # '25/10/06 14:30'
    '%d/%m/%y',                         # '25/10/06'
]
