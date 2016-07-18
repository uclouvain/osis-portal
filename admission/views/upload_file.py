from django.shortcuts import render, redirect
from base.forms import UploadDocumentFileForm
from base.models.document_file import DocumentFile


def upload_file(request):
    if request.method == "POST":
        form = UploadDocumentFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.save()
            file.size = file.file.size
            file_type = form.cleaned_data["file"]
            content_type = file_type.content_type.split('/')[1]
            file.physical_extension = content_type
            file.save()
            return redirect('new_file')
        else:
            return render(request, 'new_file.html', {'form': form,
                                                     'content_type_choices': DocumentFile.CONTENT_TYPE_CHOICES,
                                                     'description_choices': DocumentFile.DESCRIPTION_CHOICES})
    else:
        form = UploadDocumentFileForm(initial={'storage_duration': 0,
                                               'physical_extension': "none",
                                               'document_type': "admission",
                                               'user': request.user})
        return render(request, 'new_file.html', {'form': form,
                                                 'content_type_choices': DocumentFile.CONTENT_TYPE_CHOICES,
                                                 'description_choices': DocumentFile.DESCRIPTION_CHOICES})
