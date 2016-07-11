from django.shortcuts import render
from admission.models.file import File
from admission.forms import NewFileForm


def new_file(request):
    if request.method == "POST":
        form = NewFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = File()
            file.name = form.cleaned_data["name"]
            file.file = form.cleaned_data["file"]
            file.save()
    else:
        form = NewFileForm()
    return render(request, 'new_file.html', {'form': form})