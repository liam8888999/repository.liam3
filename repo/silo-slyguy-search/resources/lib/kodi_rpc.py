# -*- coding: utf-8 -*-
"""Small Kodi JSON-RPC helpers used by the search bridge."""

import json

import xbmc


def call(method, params=None):
    request = {"jsonrpc": "2.0", "id": "silo-slyguy-search", "method": method}
    if params is not None:
        request["params"] = params
    try:
        raw = xbmc.executeJSONRPC(json.dumps(request))
        response = json.loads(raw or "{}")
    except (TypeError, ValueError) as exc:
        xbmc.log("[script.silo.slyguy.search] JSON-RPC decode error: %s" % exc, xbmc.LOGWARNING)
        return None
    if response.get("error"):
        xbmc.log("[script.silo.slyguy.search] JSON-RPC %s failed: %s" % (method, response["error"]), xbmc.LOGWARNING)
        return None
    return response.get("result")


def get_installed_slyguy_video_addons():
    result = call("Addons.GetAddons", {
        "type": "xbmc.python.pluginsource",
        "content": "video",
        "enabled": True,
        "installed": True,
        "properties": ["name", "version", "thumbnail", "dependencies"],
    }) or {}

    addons = []
    for addon in result.get("addons", []):
        addon_id = str(addon.get("addonid") or "").strip()
        if not addon_id:
            continue

        dependencies = addon.get("dependencies") or []
        dependency_ids = {
            str(dep.get("addonid") or "").strip()
            for dep in dependencies
            if isinstance(dep, dict)
        }

        # SlyGuy video add-ons depend on the shared SlyGuy module. Their own
        # addon ids are normally plugin.video.* rather than slyguy.*.
        if "script.module.slyguy" not in dependency_ids:
            continue

        addons.append(addon)

    return sorted(
        addons,
        key=lambda item: str(
            item.get("name") or item.get("addonid") or ""
        ).lower(),
    )


def get_plugin_directory(url):
    result = call("Files.GetDirectory", {
        "directory": url,
        "media": "files",
        "properties": [
            "title",
            "thumbnail",
            "fanart",
            "plot",
            "year",
            "genre",
            "studio",
            "rating",
            "runtime",
            "season",
            "episode",
            "showtitle",
            "playcount",
            "resume",
            "file",
        ],
    }) or {}
    return result.get("files") or []
