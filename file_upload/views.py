from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import UploadFileForm
from django.http import HttpResponse
from . import route
from collections import OrderedDict
import json

import sys

# ------------------------------------------------------------------
from .opencv import get_opencv
from .route import get_route

def opencv(request, status=None):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            sys.stderr.write("*** file_upload *** aaa ***\n")
            handle_uploaded_file(request.FILES['file'])
            file_obj = request.FILES['file']
            filename = 'media/documents/' + file_obj.name
            sys.stderr.write(file_obj.name + "\n")
            result = get_opencv(filename);
            return render(request, 'file_upload/res.html', result)
    else:
        form = UploadFileForm()
    return render(request, 'file_upload/upload.html', {'form': form})


def file_upload(request, status=None):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            sys.stderr.write("*** file_upload *** aaa ***\n")
            handle_uploaded_file(request.FILES['file'])
            file_obj = request.FILES['file']
            filename = 'media/documents/' + file_obj.name
            sys.stderr.write(file_obj.name + "\n")
            result = get_route(filename);
            json_str = json.dumps(result, ensure_ascii=False, indent=2)
            return HttpResponse(json_str, content_type='application/json; charset=UTF-8', status=status)
    else:
        form = UploadFileForm()
    return render(request, 'file_upload/upload.html', {'form': form})
#
#
# ------------------------------------------------------------------
def handle_uploaded_file(file_obj):
    sys.stderr.write("*** handle_uploaded_file *** aaa ***\n")
    sys.stderr.write(file_obj.name + "\n")
    file_path = 'media/documents/' + file_obj.name 
    sys.stderr.write(file_path + "\n")
    with open(file_path, 'wb+') as destination:
        for chunk in file_obj.chunks():
            sys.stderr.write("*** handle_uploaded_file *** ccc ***\n")
            destination.write(chunk)
            sys.stderr.write("*** handle_uploaded_file *** eee ***\n")
#
# ------------------------------------------------------------------
def success(request):
    str_out = "Success!<p />"
    str_out += "成功<p /><p>"
    return HttpResponse(str_out)
# ------------------------------------------------------------------
