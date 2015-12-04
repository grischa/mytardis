#!/usr/bin/env python
import os
import sys
import subprocess

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tardis.test_settings")

    from django.core.management import execute_from_command_line
    if len(sys.argv) < 2:
        execute_from_command_line(['./test.py', 'test'])
    else:
        execute_from_command_line(sys.argv)
    pylint = subprocess.Popen(
        ['pylint', '--rcfile=.pylintrc', '-j', '2', 'tardis'],
        stdout=subprocess.PIPE)
    pylint_happy = True
    for output in pylint.stdout:
        if pylint_happy:
            print("pylint results")
            pylint_happy = False
        print output,
    if pylint_happy:
        print("pylint is happy")
    else:
        sys.exit(1)
