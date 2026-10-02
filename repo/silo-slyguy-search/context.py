# -*- coding: utf-8 -*-
"""Kodi PVR-recording context-menu entry point."""

import sys
from urllib.parse import quote_plus

import xbmc
import xbmcgui

from resources.lib import search


def main():
    list_item = getattr(sys, "listitem", None)
    if list_item is None:
        xbmcgui.Dialog().notification("Search Streaming Services", "No recording was supplied to the context action")
        return

    query = search.query_from_listitem(list_item)
    if not query:
        xbmcgui.Dialog().notification("Search Streaming Services", "Could not determine the recording title")
        return

    xbmc.log("[script.silo.slyguy.search] Searching for PVR recording: %r" % query, xbmc.LOGINFO)
    url = "plugin://%s/?_=search&query=%s" % (search.ADDON_ID, quote_plus(query))
    xbmc.executebuiltin("ActivateWindow(Videos,%s,return)" % url)


if __name__ == "__main__":
    main()
