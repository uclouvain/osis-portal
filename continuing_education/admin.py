from django.contrib import admin
from continuing_education.models import admission

admin.site.register(admission.Admission, admission.AdmissionAdmin)
