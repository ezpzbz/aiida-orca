"""Check that version numbers match.

Check version number in setup.json and aiida_zeopp/__init__.py and make sure
they match.
"""
import os
import json
import sys

THIS_PATH = os.path.split(os.path.realpath(__file__))[0]

# Get content of setup.json
SETUP_FNAME = 'setup.json'
SETUP_PATH = os.path.join(THIS_PATH, os.pardir, SETUP_FNAME)
with open(SETUP_PATH) as f:
    SETUP_CONTENT = json.load(f)

# Get version from python package
sys.path.insert(0, os.path.join(THIS_PATH, os.pardir))
import aiida_orca  # pylint: disable=wrong-import-position
VERSION = aiida_orca.__version__

if VERSION != SETUP_CONTENT['version']:
    print('version number mismatch detected:')
    print("version number in '{}': {}".format(SETUP_FNAME, SETUP_CONTENT['version']))
    print("version number in '{}/__init__.py': {}".format('aiida_orca', VERSION))
    sys.exit(1)
