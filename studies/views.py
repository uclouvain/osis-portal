from django.shortcuts import render
from django.utils import timezone
from .models import AcademicYear, OfferEnrollment, LearningUnitEnrollment

def courses(request, year = 0):
    academic_year = None
    if year == 0:
        academic_year = AcademicYear.objects.filter(start_date__lte=timezone.now()).filter(end_date__gte=timezone.now()).first()
    else:
        academic_year = AcademicYear.objects.get(year=year)

    if academic_year is not None:
        print(academic_year.id)
        learning_unit_enrollments = LearningUnitEnrollment.objects.filter(learning_unit_year__academic_year__pk=academic_year.id)

    return render(request, "courses.html", {'enrollments': learning_unit_enrollments,
                                            'academic_year': academic_year})


def exams(request):
    return render(request, "exams.html", {})


def studies(request):
    enrollments = OfferEnrollment.objects.all()
    return render(request, "studies.html", {'enrollments': enrollments})
