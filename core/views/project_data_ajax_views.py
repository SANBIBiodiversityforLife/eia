# Core & settings
from core import forms

# JSON & serialization
from django.http import JsonResponse

def flag_for_removal(request, pk, metadata_pk):
    """
    Acessible only via ajax, allows users to flag datasets for removal
    """
    # Flag a dataset for removal
    # If the form has been submitted and is valid
    if request.method == 'POST':
        # Create a form instance and populate it with the post data
        form = forms.RemovalFlagCreateForm(request.POST)

        # Security check
        if form.is_valid():
            flag = form.save(commit=False)
            flag.requested_by = request.user
            flag.metadata_id = metadata_pk
            flag.save()
            return JsonResponse({})
        else:
            return JsonResponse(form.errors, status=400)


def add_document(request, pk, metadata_pk=None):
    """
    Accessible only via ajax, this allows users to upload documents associated with particular metadata
    """
    # Add a metadata document
    if request.method == 'POST':
        # Create a form instance and populate it with the post data and the uploaded file
        form = forms.DocumentCreateForm(request.POST, request.FILES)

        # Security check
        if form.is_valid():
            document = form.save(commit=False)
            document.uploader = request.user
            document.project_id = pk
            if metadata_pk:
                document.metadata_id = metadata_pk
            document.save()
            return JsonResponse({'document': document.get_table_display()})
        else:
            return JsonResponse(form.errors, status=400)
