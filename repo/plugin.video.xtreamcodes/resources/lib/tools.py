# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.xtreamcodes

from __future__ import unicode_literals

import sys
import traceback
import re
import xbmc

from .country_codes import CC
from .vars import *

try:
    from urllib.parse import quote_plus
    from urllib.parse import unquote_plus
    from html.parser import HTMLParser
    import urllib.parse as urlparse
except ImportError:
    from urllib import quote_plus
    from urllib import unquote_plus
    import HTMLParser
    import urlparse



def log(msg, level=xbmc.LOGDEBUG):
    if DEBUG == False and level != xbmc.LOGERROR: return
    if level == xbmc.LOGERROR: msg += ' ,' + traceback.format_exc()
    xbmc.log(ADDON_ID + '-' + ADDON_VERSION + '-' + msg, level)


def getParams():
    return dict(urlparse.parse_qsl(sys.argv[2][1:]))

def formatTitles(title):
    unwantedchars = '-_:|.'
    for c in unwantedchars:
        # remove language and country prefix
        if title.split(c)[0] in CC and len(title.split(c)) > 1:
            title = title.split(c, 1)[1]
    for c in unwantedchars:
        # remove unwanted chars
        title = title.replace(c, ' ')
    title = title.title()
    # capitalise generic suffixs
    genericstrings = 'HD SD FHD H265 TV'

    for w in title.split(' '):
        # assumes string with less than 3 character is an abbreviation
        if len(''.join([i for i in w if not i.isdigit()])) < 4:
            title = title.replace(w, w.upper())
        if w.upper() in genericstrings.split(' '):
            title = title.replace(w, w.upper())
        p = ''
        for c in w:
            if c.isdigit() and len(w) > 4:
                title = title.replace(c, ' %s'%c)
                if p.isdigit():
                    title = title.replace('%s '%p, p)
            if c == '+':
                title = title.replace(c, '%s '%c)
            p = c
    # remove multispaces
    title = ' '.join(title.split())
    title = title.encode('utf-8').strip()
    return title.decode('utf-8')
