# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.xtreamcodes

from __future__ import unicode_literals
import xbmcaddon
from os import sep as osSeparator

ADDON_ID = 'plugin.video.xtreamcodes'
MEDIA_URL = xbmcaddon.Addon().getAddonInfo('path') + osSeparator  + 'resources' + osSeparator + 'images' + osSeparator
LIVETV = MEDIA_URL + 'livetv.png'
TVSHOWS = MEDIA_URL + 'tvshows.png'
MOVIES = MEDIA_URL + 'movies.png'
REAL_SETTINGS = xbmcaddon.Addon(id=ADDON_ID)
ADDON_NAME = REAL_SETTINGS.getAddonInfo('name')
SETTINGS_LOC = REAL_SETTINGS.getAddonInfo('profile')
ADDON_PATH = REAL_SETTINGS.getAddonInfo('path')
ADDON_VERSION = REAL_SETTINGS.getAddonInfo('version')
ICON = REAL_SETTINGS.getAddonInfo('icon')
FANART = REAL_SETTINGS.getAddonInfo('fanart')
LANGUAGE = REAL_SETTINGS.getLocalizedString
DEBUG = REAL_SETTINGS.getSetting('Enable_Debugging') == 'true'
HOST = REAL_SETTINGS.getSetting('Host')
PORT = REAL_SETTINGS.getSetting('Port')
USER = REAL_SETTINGS.getSetting('User')
PASSWORD = REAL_SETTINGS.getSetting('Password')
BASE_URL = 'http://%s:%s' % (HOST, PORT)
PLAYER_API = BASE_URL + '/player_api.php'
PARAMS = {
            'username': USER,
            'password': PASSWORD,
        }

MOVIE_URL = BASE_URL + '/movie/%s/%s/%s.%s'
VID_URL = BASE_URL + '/series/%s/%s/%s.%s'
LIVE_URL = BASE_URL + '/live/%s/%s/%s.%s'


MAIN_MENU = [
                {"name": "Live", "mode": "3", "thumb": LIVETV},
                {"name": "Movies", "mode": "7", "thumb": MOVIES},
                {"name": "TVSHOWS", "mode": "1", "thumb": TVSHOWS}
            ]
