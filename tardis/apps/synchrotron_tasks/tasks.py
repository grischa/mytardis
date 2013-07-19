import subprocess
from celery import task
from django.conf import settings

import logging
log = logging.getLogger(__name__)


@task('move_preview_images')
def move_preview_images():
    temp_location = settings.METADATA_TEMP_PATH
    permanent_location = settings.METADATA_STORE_PATH

    subprocess.call(['rsync', '-av',
                     temp_location + '/', permanent_location])
    # to move files, could have used this... rsync is easier
    # for root, dirs, files in os.walk(temp_location, topdown=False):
    #     relroot = os.path.relpath(root, temp_location)
    #     for f in files:
    #         fullpath = os.path.join(root, f)
    #         relpath = os.path.join(relroot, f)
    #         os.renames(fullpath, os.path.join(permanent_location, relpath))
    #     if len(files) == 0 and len(dirs) == 0:
    #         try:
    #             os.rmdir(root)
    #         except OSError:
    #             log.debug('directory %s not empty' % root)
