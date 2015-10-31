from django.shortcuts import render

def courses(request):
    return render(request, "courses.html", {})


def exams(request):
    return render(request, "exams.html", {})


def studies(request):
    return render(request, "index.html", {})
