# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.xtreamcodes

from __future__ import unicode_literals


import json
import urlquick
from .vars import *
from .create_item import *
from .tools import log
from .country_codes import CC

def getMovieC(url):
    log('getMovieC')
    CAT_PARAMS = {
                    'username': '**********',
                    'password': '**********',
                    'action': 'get_vod_categories'
                }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % CAT_PARAMS)
    CAT_PARAMS.update(PARAMS)
    items = json.loads(urlquick.get(PLAYER_API, params=CAT_PARAMS).text)
    for item in items:
        title = formatTitles(item['category_name'])
        catid = item['category_id']
        infoLabels = {
                        "mediatype": "video",
                        "label": title,
                        "title": title
                    }
        infoArt = {
                    "thumb": ICON,
                    "poster": ICON,
                    "fanart": FANART,
                    "icon": ICON,
                    "logo": ICON
                }
        addDir(title, catid, 8, infoLabels, infoArt, len(items))


def getMovies(catid):
    CONTENT_TYPE  = 'movies'
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    log('browseMovies')
    MOVIES_PARAMS = {
                        'username': '**********',
                        'password': '**********',
                        'action': 'get_vod_streams',
                        'category_id': catid
                    }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % MOVIES_PARAMS)
    MOVIES_PARAMS.update(PARAMS)
    items = json.loads(urlquick.get(PLAYER_API, params=MOVIES_PARAMS).text)
    for item in items:
        title = formatTitles(item['name'])
        mid = item['stream_id']
        vidType = item['container_extension']
        url = MOVIE_URL % (USER, PASSWORD, mid, vidType)
        thumb = item['stream_icon']
        infoLabels = {"mediatype":"movies", "title":title}
        infoArt = {
                    "thumb": thumb,
                    "poster": thumb,
                    "fanart": thumb,
                    "icon": ICON,
                    "logo": ICON
                }
        addLink(title, url, 9, infoLabels, infoArt, len(items))
