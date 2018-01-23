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
import unicodecsv
import datetime
from django.http import HttpResponse


def export_as_csv_action(description="Export objects as CSV", fields=None, exclude=None, header=True):

    def export_as_csv(adminmodel, request, queryset):
        opts = adminmodel.model._meta

        if fields:
            field_names = fields
        else:
            field_names = [field.name for field in opts.fields]

        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=%s-%s.csv' % (str(opts).replace('.', '_'), str(datetime.datetime.now()))
        writer = unicodecsv.writer(response, encoding='utf-8')

        if header:
            writer.writerow(field_names)
        for record in queryset:
            get_attribute = lambda record, field: getattr(record, field)() if callable(getattr(record, field)) else getattr(record, field)
            row = [get_attribute(record, field) for field in field_names]
            writer.writerow(row)
        return response

    export_as_csv.short_description = description

    return export_as_csv
