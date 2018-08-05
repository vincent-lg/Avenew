from django.http import HttpResponseRedirect
from django.shortcuts import render

from web.decorators import ensure_perm
from world.batch_yml import batch_YAML
from .forms import UploadFileForm

@ensure_perm(permission="builder")
def index(request):
    return render(request, "builder/index.html")

@ensure_perm(permission="builder")
def batch(request):
    content = {}
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            batch = request.FILES['file']
            content.update({"messages": batch_YAML(batch, None)})
    else:
        form = UploadFileForm()

    content["form"] = form
    return render(request, 'builder/batch.html', content)
