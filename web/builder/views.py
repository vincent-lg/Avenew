import json
from pathlib import Path

from django.conf import settings
>>>>>>> master
from django.http import HttpResponseRedirect
from django.shortcuts import render
from yaml import safe_load_all

from web.decorators import ensure_perm
from world.batch_yml import batch_YAML
from .forms import UploadFileForm

@ensure_perm(permission="builder")
def index(request):
    return render(request, "builder/index.html")

@ensure_perm(permission="builder")
def batch_list(request):
    path = Path(settings.BATCH_DIR)
    if not path.exists():
        path.mkdir(parents=True)

    files = []
    for file in sorted(path.glob("*.yml")):
        files.append({
                'name': file.stem,
                'rel_path': file.relative_to(path),
                'size': file.stat().st_size,
        })

    return render(request, 'builder/batch/list.html', {'files': files})

@ensure_perm(permission="builder")
def batch_view(request, filename):
    dir_path = Path(settings.BATCH_DIR)
    batch = dir_path / filename
    if batch.exists:
        with batch.open('r', encoding="utf-8") as stream:
            documents = list(safe_load_all(stream))

        file = {
                'name': batch.stem,
                'rel_path': batch.relative_to(dir_path),
                'size': batch.stat().st_size,
                'documents': json.dumps(documents),
        }
    else:
        file = {
                'name': batch.stem,
                'rel_path': batch.relative_to(dir_path),
                'size': "unknown",
                'documents': [],
        }

    return render(request, 'builder/batch/view.html', {'file': file, 'lang': settings.LANGUAGE_CODE})

@ensure_perm(permission="builder")
def batch_apply(request):
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
    return render(request, 'builder/batch/apply.html', content)
