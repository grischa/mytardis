import os
from celery import task
from django.conf import settings
from tardis.tardis_portal.models import ParameterName
from tardis.tardis_portal.models import Parameter


@task('move_preview_images')
def move_preview_images():
    temp_location = settings.METADATA_TEMP_PATH
    permanent_location = settings.METADATA_STORE_PATH
    for root, dirs, files in os.walk(temp_location, topdown=False):
        relroot = os.path.relpath(root, temp_location)
        for f in files:
            fullpath = os.path.join(root, f)
            relpath = os.path.join(relroot, f)
            os.renames(fullpath, os.path.join(permanent_location, relpath))
        if len(files) == 0 and len(dirs) == 0:
            try:
                os.rmdir(root)
            except OSError:
                log.debug('directory %s not empty' % dir)
