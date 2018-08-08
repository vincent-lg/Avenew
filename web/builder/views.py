# -*- coding: utf-8 -*-

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
            # Try to find the first builder in this account, which will be the author
            author = None
            if request.user.db._playable_characters:
                for character in request.user.db._playable_characters:
                    if character.check_permstring("builder"):
                        author = character
                        break

            # If no author, don't execute the batch YML
            if author is None:
                content["messages"] = [(3, 0, "The logged-in account doesn't have a character who is a builder.")]
            else:
                batch = request.FILES['file']
                messages = batch_YAML(batch, author)
                messages.sort(key=lambda m: m[1])
                documents = len([m for m in messages if m[0] == 1])
                warnings = len([m for m in messages if m[0] == 2])
                errors = len([m for m in messages if m[0] == 3])
                message = "{} document{s} appliqué{s}, {} warning{}, {} erreur{}.".format(
                        documents,
                        warnings, "s" if warnings > 1 else "",
                        errors, "s" if errors > 1 else "",
                        s="s" if documents > 1 else "")
                messages.insert(0, (0, 0, message))
                content["messages"] = messages
    else:
        form = UploadFileForm()

    content["form"] = form
    return render(request, 'builder/batch.html', content)
