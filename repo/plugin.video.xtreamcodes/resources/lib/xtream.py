# -*- coding: utf-8 -*-
# Copyright: (c) 2021, Chamchenko
# GNU General Public License v2.0+ (see LICENSE.txt or https://www.gnu.org/licenses/gpl-2.0.txt)
# This file is part of plugin.video.xtreamcodes

from __future__ import unicode_literals

import sys
import xbmc
import xbmcgui
import xbmcplugin
import xbmcaddon

from .tvshows import *
from .movies import *
from .livetv import *
from .vars import *
from .tools import *
from .create_item import *

if HOST == "" or PORT == "" or USER == "" or PASSWORD == "":
    xbmcaddon.Addon().openSettings()
    HOST = REAL_SETTINGS.getSetting('Host')
    PORT = REAL_SETTINGS.getSetting('Port')
    USER = REAL_SETTINGS.getSetting('User')
    PASSWORD = REAL_SETTINGS.getSetting('Password')


class XTREAM(object):
    def __init__(self):
        log('__init__')

    def buildMenu(self, url):
        if verifySubscription():
            for item in MAIN_MENU:
                title = item['name']
                thumb = item['thumb']
                mode = item['mode']
                infoLabels = {
                                "mediatype": "",
                                "label": name,
                                "title": title
                            }
                infoArt = {
                            "thumb": thumb,
                            "poster": thumb,
                            "fanart" :thumb,
                            "icon": thumb,
                            "logo": thumb
                        }
                addDir(title, '', mode, infoLabels, infoArt)
        else:
            return
    def browseLiveC(self, url):
        getLiveC(url)
    def browseLives(self, url):
        getLives(url)
    def browseMovieC(self, url):
        getMovieC(url)
    def browseMovies(self, url):
        getMovies(url)
    def browseShowsC(self, url):
        getShowsC(url)
    def browseShows(self, url):
        getShows(url)
    def browseSeasons(self, url):
        getSeasons(url)
    def browseEpisodes(self, url):
        getEpisodes(url)
    def playVideo(self, name, url, liz=None):
        log('playVideo')
        liz  = xbmcgui.ListItem(name, path=url)
        xbmcplugin.setResolvedUrl(int(sys.argv[1]), True, liz)


params=getParams()
try:
    url=unquote_plus(params["url"])
except:
    url=None
try:
    name=unquote_plus(params["name"])
except:
    name=None
try:
    mode=int(params["mode"])
except:
    mode=None
log("Mode: " + str(mode))
log("URL : " + str(url))
log("Name: " + str(name))

if mode==None:
    XTREAM().buildMenu(MAIN_MENU)
if mode == 1:
    XTREAM().browseShowsC(url)
elif mode == 2:
    XTREAM().browseShows(url)
elif mode == 3:
      XTREAM().browseLiveC(url)
elif mode == 4:
    XTREAM().browseSeasons(url)
elif mode == 5:
    XTREAM().browseEpisodes(url)
elif mode == 6:
      XTREAM().browseLives(url)
elif mode == 7:
      XTREAM().browseMovieC(url)
elif mode == 8:
      XTREAM().browseMovies(url)
elif mode == 9:
    XTREAM().playVideo(name, url)

xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_UNSORTED)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_NONE)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_LABEL)
xbmcplugin.addSortMethod(int(sys.argv[1]), xbmcplugin.SORT_METHOD_TITLE)
xbmcplugin.endOfDirectory(int(sys.argv[1]), cacheToDisc=True)
