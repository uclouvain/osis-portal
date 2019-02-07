##############################################################################
#
#    OSIS stands for Open Student Information System. It's an application
#    designed to manage the core business of higher education institutions,
#    such as universities, faculties, institutes and professional schools.
#    The core business involves the administration of students, teachers,
#    courses, programs and so on.
#
#    Copyright (C) 2015-2019 Université catholique de Louvain (http://www.uclouvain.be)
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
from django.http import JsonResponse


class AjaxTemplateMixin:
    """ Mixin for views:

    Adapt the requests of the view to be compatible with modal_form_submit.js
    """
    ajax_template_suffix = "_inner"

    def get_template_names(self):
        template_names = super().get_template_names()
        if self.request.is_ajax():
            template_names = [
                self._convert_template_name_to_ajax_template_name(template_name) for template_name in template_names
            ]
        return template_names

    @staticmethod
    def _convert_template_name_to_ajax_template_name(template_name):
        if "_inner.html" not in template_name:
            split = template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            return "".join(split)
        return template_name

    def form_valid(self, form):
        response = super().form_valid(form)
        return self._ajax_response() or response

    def forms_valid(self, forms):
        response = super().forms_valid(forms)
        return self._ajax_response() or response

    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        return self._ajax_response() or response

    def _ajax_response(self):
        # When the form is saved, we return only the url, not all the template
        if self.request.is_ajax():
            response = {"success": True}
            url = self.get_success_url()
            if url:
                response['success_url'] = url
            return JsonResponse(response)
