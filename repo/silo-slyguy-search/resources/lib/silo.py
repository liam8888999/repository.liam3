# -*- coding: utf-8 -*-
"""Silo search bridge."""

from urllib.parse import quote_plus

import xbmc

from . import kodi_rpc


def search(query):
    query = str(query or "").strip()
    if not query:
        return []

    url = "plugin://plugin.video.silo/?action=search&query=%s" % quote_plus(query)
    try:
        files = kodi_rpc.get_plugin_directory(url)
    except Exception as exc:
        xbmc.log("[script.silo.slyguy.search] Silo search failed: %s" % exc, xbmc.LOGWARNING)
        return []

    results = []
    filtered = 0

    for item in files:
        media_type = str(
            item.get("type")
            or item.get("media_type")
            or item.get("mediatype")
            or ""
        ).strip().lower()

        path = str(item.get("file") or "").strip()
        label = str(item.get("label") or item.get("title") or "").strip()

        # Silo's search route includes people and episodes. This bridge is
        # deliberately limited to movie and TV-show results.
        is_person = (
            media_type in ("person", "actor")
            or label.startswith("[Person]")
            or "action=person" in path.lower()
        )
        is_episode = (
            media_type == "episode"
            or label.startswith("[Episode]")
        )

        if is_person or is_episode:
            filtered += 1
            continue

        if path and label:
            result = dict(item)
            result.update(
                source="Silo",
                source_addon_id="plugin.video.silo",
                source_name="Silo",
                path=path,
            )
            results.append(result)

    xbmc.log(
        "[script.silo.slyguy.search] Filtered %d Silo people/episode result(s)"
        % filtered,
        xbmc.LOGINFO,
    )

    xbmc.log("[script.silo.slyguy.search] Silo returned %d result(s) for %r" % (len(results), query), xbmc.LOGINFO)
    return results
