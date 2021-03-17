import os
from os.path import basename, dirname, join
import sys

FUNC = basename(dirname(__file__))
BASE = dirname(dirname(dirname(__file__)))
sys.path.insert(0, join(BASE, '.aws-sam', 'build', FUNC))

os.environ['TZ'] = 'America/Chicago'
