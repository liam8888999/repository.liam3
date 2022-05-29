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

def getShowsC(url):
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    log('getShowsC')
    CAT_PARAMS = {
                    'username': '**********',
                    'password': '**********',
                    'action': 'get_series_categories'
                }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % CAT_PARAMS)
    CAT_PARAMS.update(PARAMS)
    items = json.loads(urlquick.get(PLAYER_API, params=CAT_PARAMS).text)
    for item in items:
        title = formatTitles(item['category_name'])
        catid = item['category_id']
        infoLabels = {
                        "mediatype": "episode",
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
        addDir(title ,catid, 2, infoLabels, infoArt)



def getShows(catid):
    CONTENT_TYPE = 'tvshows'
    xbmcplugin.setContent(int(sys.argv[1]), 'tvshows')
    log('getShows')
    SHOWS_PARAMS = {
                    'username': '**********',
                    'password': '**********',
                    'action': 'get_series',
                    'category_id': catid
                }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % SHOWS_PARAMS)
    SHOWS_PARAMS.update(PARAMS)
    items = json.loads(urlquick.get(PLAYER_API, params=SHOWS_PARAMS).text)
    for item in items:
        title = formatTitles(item['name'])
        shid = item['series_id']
        try:
            plot  = item['plot']
        except:
            plot = 'Null'
        try:
            aired = item['releaseDate']
        except:
            aired = '1970-01-01'
        try:
            fanart = item['backdrop_path'][0]
        except:
            fanart = ICON
        thumb = item['cover']
        url   = json.dumps({
                            'fanart': fanart,
                            'shid': shid,
                            'thumb': thumb
                        })
        infoLabels = {
                        "mediatype": "tvshows",
                        "title": title,
                        "TVShowTitle": title,
                        "plot": plot
                    }
        infoArt = {
                    "thumb": thumb,
                    "poster": thumb,
                    "fanart": fanart,
                    "icon": ICON,
                    "logo": ICON
                }
        addDir(title, url, 4, infoLabels, infoArt)


def getSeasons(url):
    CONTENT_TYPE = 'tvshows'
    xbmcplugin.setContent(int(sys.argv[1]), 'seasons')
    log('getSeasons')
    items = json.loads(url)
    shid = items['shid']
    fanart = items['fanart']
    sthumb = items['thumb']
    shid = items['shid']
    SHOW_PARAMS = {
                    'username': '**********',
                    'password': '**********',
                    'action': 'get_series_info',
                    'series_id': shid
                }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % SHOW_PARAMS)
    SHOW_PARAMS.update(PARAMS)
    json_parser = json.loads(urlquick.get(PLAYER_API, params=SHOW_PARAMS).text)
    available = json_parser['episodes'].keys()
    items = json_parser
    if items['seasons'] != []:
        for item in items['seasons']:
            seasonnumber = item['season_number']
            if str(seasonnumber) not in available:
                continue
            title = 'Season %s' % seasonnumber
            try:
                aired = item['air_date']
            except:
                aired = '1970-01-01'
            thumb = item['cover']
            try:
                plot = item['overview']
            except:
                plot = 'Null'
            try:
                rating = item['rating']
            except:
                rating = 0
            url = json.dumps({
                                'shid': shid,
                                'seasonnumber': seasonnumber,
                                'sthumb': sthumb
                            })
            infoLabels = {
                            "mediatype": "tvshows",
                            "label": title,
                            "title": title,
                            "season": seasonnumber,
                            "aired": aired,
                            "plot": plot,
                            "TVShowTitle": title
                        }
            infoArt = {
                        "thumb": thumb,
                        "poster": thumb,
                        "fanart": fanart,
                        "icon": ICON,
                        "logo": ICON
                    }
            addDir(title, url, 5, infoLabels, infoArt)

    else:
        for item in available:
            title = 'Season %s' % str(item)
            seasonnumber = 1
            aired = '1970-01-01'
            thumb = sthumb
            plot = "Null"
            rating = 0
            url = json.dumps({
                                'shid': shid,
                                'seasonnumber': seasonnumber,
                                'sthumb': sthumb
                            })
            infoLabels = {
                            "mediatype": "tvshows",
                            "label": title,
                            "title": title,
                            "season": seasonnumber,
                            "aired": aired,
                            "plot": plot,
                            "TVShowTitle": title
                        }
            infoArt = {
                        "thumb": thumb,
                        "poster": thumb,
                        "fanart": fanart,
                        "icon": ICON,
                        "logo": ICON
                    }
            addDir(title, url, 5, infoLabels, infoArt)


def getEpisodes(url):
    log('getEpisodes')
    CONTENT_TYPE = 'episodes'
    xbmcplugin.setContent(int(sys.argv[1])    , 'episodes')
    items = json.loads(url)
    shid   = items['shid']
    sthumb   = items['sthumb']
    seasonnumber = str(items['seasonnumber'])
    EPISODE_PARAMS = {
                        'username': '**********',
                        'password': '**********',
                        'action': 'get_series_info',
                        'series_id': shid
                    }
    log('Fetching, url = %s' % PLAYER_API)
    log('Fetching, params = %s' % EPISODE_PARAMS)
    EPISODE_PARAMS.update(PARAMS)
    json_parser = json.loads(urlquick.get(PLAYER_API, params=EPISODE_PARAMS).text)
    showTitle = formatTitles(json_parser['info']['name'])
    items = json_parser['episodes']
    for item in items[seasonnumber]:
        title = formatTitles(item['title'])
        vidType = item['container_extension']
        try:
            thumb = item['info']['movie_image']
        except:
            thumb = sthumb
        try:
            aired = item['info']['releasedate']
        except:
            aired = '1970-01-01'
        seasonNumber = item['season']
        episodeNumber = item['episode_num']
        seinfo = ('S' + ('0' if seasonNumber < 10 else '') + str(seasonNumber) + 'E' + ('0' if episodeNumber < 10 else '') + str(episodeNumber))
        label  = '%s %s'%(showTitle, seinfo)
        try:
            duration = item['info']['duration_secs']
        except:
            duration = 0
        Vid = item['id']
        url = VID_URL % (USER, PASSWORD, Vid, vidType)
        try:
            plot   = item['info']['plot']
        except:
            plot = 'Null'
        infoLabels = {
                        "mediatype": "episode",
                        "label": label,
                        "title": label,
                        "TVShowTitle": showTitle,
                        "plot": plot,
                        "aired": aired,
                        "duration": duration,
                        "season": seasonNumber,
                        "episode": episodeNumber
                    }
        infoArt = {
                    "thumb": thumb,
                    "poster": thumb,
                    "fanart": FANART,
                    "icon": ICON,
                    "logo": ICON
                }
        addLink(title, url, 9, infoLabels, infoArt)
