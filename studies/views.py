from django.shortcuts import render
from django.utils import timezone
from .models import AcademicYear, Exam, ExamEnrollment, OfferEnrollment, LearningUnitEnrollment

def certifications(request):
    return render(request, "certifications.html", {})

def courses(request, year = 0):
    if year == 0:
        academic_year = AcademicYear.objects.filter(start_date__lte=timezone.now()).filter(end_date__gte=timezone.now()).first()
    else:
        academic_year = AcademicYear.objects.get(year=year)

    if academic_year is not None:
        learning_unit_enrollments = LearningUnitEnrollment.objects.filter(learning_unit_year__academic_year__pk=academic_year.id)

    return render(request, "courses.html", {'enrollments': learning_unit_enrollments,
                                            'academic_year': academic_year})

def course(request, year = 0, id = 0):
    academic_year = None
    if year == 0:
        academic_year = AcademicYear.objects.filter(start_date__lte=timezone.now()).filter(end_date__gte=timezone.now()).first()
    else:
        academic_year = AcademicYear.objects.get(year=year)

    learning_unit_enrollment = LearningUnitEnrollment.objects.get(id=id)

    exams = Exam.objects.filter(learning_unit_year=learning_unit_enrollment.learning_unit_year)
    exams_with_scores = []
    for exam in exams :
        exam_enrollment = ExamEnrollment.objects.filter(exam=exam)
        for exam_enrol in exam_enrollment :
            dic = {'exam' : exam, 'score' : exam_enrol.score}
            exams_with_scores.append(dic)

    return render(request, "course.html", {'enrollment': learning_unit_enrollment,
                                           'academic_year': academic_year,
                                           'exams_with_scores': exams_with_scores})

def exams(request):
    return render(request, "exams.html", {})

def requests(request):
    return render(request, "requests.html", {})

def studies(request):
    enrollments = OfferEnrollment.objects.all()
    return render(request, "studies.html", {'enrollments': enrollments})
