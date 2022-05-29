import sys
from kodi_six import xbmc

from resources.lib.plugin import plugin

plugin.dispatch(sys.argv[2])
