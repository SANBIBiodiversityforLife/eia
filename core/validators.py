import os
import magic
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.core.exceptions import ValidationError


# One of the dependencies for this is python-magic in order to check out file types safely
# See http://blog.hayleyanderson.us/2015/07/18/validating-file-types-in-django/
def validate_spreadsheet(upload):
    pass
    # Make uploaded file accessible for analysis by saving in tmp
    tmp_path = 'tmp/%s' % upload.name[2:]
    default_storage.save(tmp_path, ContentFile(upload.file.read()))
    full_tmp_path = os.path.join(settings.MEDIA_ROOT, tmp_path)

    # Get MIME type of file using python-magic and then delete
    magic_object = magic.Magic(magic_file="C:\\magic\\magic", mime=True)
    file_type = magic_object.from_file(full_tmp_path)
    default_storage.delete(tmp_path)

    # Raise validation error if uploaded file is not an acceptable form of media
    if file_type not in [b'text/csv', b'application/csv', b'text/plain', b'application/zip']:
        raise ValidationError('File type not supported. Please upload a CSV or XLSX.')
    else:
        pass


