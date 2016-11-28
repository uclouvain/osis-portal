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
from django.db import models
from django.contrib import admin


class AnswerAdmin(admin.ModelAdmin):
    list_display = ['value']
    fieldsets = ((None, {'fields': ('value', 'option', 'application')}),)
    list_filter = ('application', 'option',)


class Answer(models.Model):
    value = models.TextField()
    option = models.ForeignKey('Option')
    application = models.ForeignKey('Application')

    def __str__(self):
        return u"%s" % self.value


def find_by_application(application):
    return Answer.objects.filter(application=application)


def find_by_option(option):
    return Answer.objects.filter(option=option)


def find_by_user_and_option(user, option):
    return Answer.objects.filter(application__applicant__user=user).filter(option=option)


def find_by_application_and_option(application, option):
    return Answer.objects.filter(application=application).filter(option=option)


def find_by_id(answer_id):
    return Answer.objects.get(id=answer_id)
