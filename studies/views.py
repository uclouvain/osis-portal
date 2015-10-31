from django.shortcuts import render

def studies(request):
    return render(request, "index.html", {})
