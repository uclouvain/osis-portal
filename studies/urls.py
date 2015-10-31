from django.conf.urls import url
from django.conf.urls.i18n import i18n_patterns

from . import views

urlpatterns = [
    url(r'^$', views.studies, name='studies'),
    url(r'^courses/', views.courses, name='courses'),
    url(r'^exams/', views.exams, name='exams')]
