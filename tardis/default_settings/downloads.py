DOWNLOAD_PATH_MAPPERS = {
    'deep-storage': (
        'tardis.apps.deep_storage_download_mapper.mapper.deep_storage_mapper',
    ),
}

DEFAULT_PATH_MAPPER = 'deep-storage'
"""Site's default archive organization (i.e. path structure)
"""

SAFE_FILESYSTEM_CHARACTERS = ""
"""Don't percent-encode characters in the SAFE_FILESYSTEM_CHARACTERS
string when creating TARs and SFTP views.

There is a difference between filesystem-safe and shell-safe.
For example, in bash, we can create a file:

touch ' !#$&'\''()+;,:=@[]'

and then create a TAR containing that file:

tar cf test.tar ' !#$&'\''()+;,:=@[]'

and then remove the file and recreate it by extracting it from the TAR:

rm ' !#$&'\''()+;,:=@[]'
tar xvf test.tar

Extracting the file from the TAR archive alone is not dangerous, but the
filename could be considered dangerous for novice shell users or for
developers prone to introducing shell-injection vulnerabilities:
https://en.wikipedia.org/wiki/Code_injection#Shell_injection

SAFE_FILESYSTEM_CHARACTERS = " !#$&'()+,:;=@[]"
"""

SPACES_TO_UNDERSCORES = False
"""
Convert spaces to underscores in names for TARs and SFTP:
"""

DEFAULT_ARCHIVE_FORMATS = ['tar']
'''
Site's preferred archive types, with the most preferred first
other available option: 'tgz'. Add to list if desired
'''
