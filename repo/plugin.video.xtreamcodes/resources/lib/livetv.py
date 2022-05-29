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
from datetime import datetime

def verifySubscription():
    resp = urlquick.get(PLAYER_API, params=PARAMS, max_age=-1).text
    try:
        expire_date = json.loads(resp)['user_info']['exp_date']
    except:
        xbmcgui.Dialog().notification(ADDON_NAME, LANGUAGE(30101), ICON, 4000)
        return False
    if not expire_date:
        expire_date = "Never"
    elif expire_date:
        expire_date = int(expire_date)
        expire_date = datetime.fromtimestamp(expire_date)
        if expire_date < datetime.now():
            xbmcgui.Dialog().notification(ADDON_NAME, LANGUAGE(30100), ICON, 4000)
            return False

    xbmcgui.Dialog().notification(ADDON_NAME, LANGUAGE(30102) % expire_date, ICON, 4000)
    return True

def getLiveC(url):
    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
    CAT_PARAMS = {
                    'username': '**********',
                    'password': '**********',
                    'action': 'get_live_categories'
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
        addDir(title, catid, 6, infoLabels, infoArt, len(items))


def getLives(catid):
    xbmcplugin.setContent(int(sys.argv[1]), 'videos')
    log('browseLives')
    LIVE_PARAMS = {
                    'username': '**********',
                    'password': '**********', 
                    'action': 'get_live_streams',
                    'category_id': catid
                }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % LIVE_PARAMS)
    LIVE_PARAMS.update(PARAMS)
    items = json.loads(urlquick.get(PLAYER_API, params=LIVE_PARAMS).text)
    for item in items:
        cattttg = item['name']
        vidType = 'ts'
        title = formatTitles(item['name'])
        chid = item['stream_id']
        iconc = item['stream_icon']
        url = LIVE_URL % (USER, PASSWORD, chid, vidType)
        infoLabels = {"mediatype":"video", "title":title}
        infoArt = {
                    "thumb": iconc,
                    "poster": iconc,
                    "fanart": iconc,
                    "icon": iconc,
                    "logo": iconc
                }
        addLink(title, url, 9, infoLabels, infoArt, len(items))
