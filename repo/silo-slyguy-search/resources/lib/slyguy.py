# -*- coding: utf-8 -*-
"""SlyGuy search bridge."""

import json
import queue
import threading
import time
from urllib.parse import quote_plus, unquote_plus

import xbmc

from . import kodi_rpc

SEARCH_TIMEOUT_SECONDS = 6.0
MAX_PARALLEL_SEARCHES = 4


def _is_error_item(item):
    path = str(item.get("file") or "").strip()
    if not path:
        return False
    try:
        decoded = unquote_plus(path)
        payload = json.loads(decoded)
        return isinstance(payload, dict) and bool(payload.get("error"))
    except (TypeError, ValueError):
        return False


def _search_one(addon, query, output):
    addon_id = str(addon.get("addonid") or "").strip()
    addon_name = str(addon.get("name") or addon_id).strip()
    if not addon_id:
        output.put((addon_id, addon_name, None, "missing addon id"))
        return

    url = "plugin://%s/?_=search&query=%s&_run_plugin=1" % (
        addon_id, quote_plus(query)
    )

    try:
        files = kodi_rpc.get_plugin_directory(url)
        output.put((addon_id, addon_name, files, None))
    except Exception as exc:
        output.put((addon_id, addon_name, None, str(exc)))


def _search_addons_with_timeouts(addons, query):
    output = queue.Queue()
    pending = list(addons)
    active = []
    finished = []

    while pending or active:
        while pending and len(active) < MAX_PARALLEL_SEARCHES:
            addon = pending.pop(0)
            started = time.monotonic()
            thread = threading.Thread(
                target=_search_one,
                args=(addon, query, output),
                name="SlyGuySearch",
                daemon=True,
            )
            active.append((thread, addon, started))
            thread.start()

        for entry in list(active):
            thread, addon, started = entry
            if not thread.is_alive():
                active.remove(entry)

        while True:
            try:
                finished.append(output.get_nowait())
            except queue.Empty:
                break

        now = time.monotonic()
        for entry in list(active):
            thread, addon, started = entry
            if now - started >= SEARCH_TIMEOUT_SECONDS:
                active.remove(entry)
                addon_id = str(addon.get("addonid") or "").strip()
                addon_name = str(addon.get("name") or addon_id).strip()
                xbmc.log(
                    "[script.silo.slyguy.search] %s timed out after %.1fs; continuing with other providers"
                    % (addon_id or addon_name, SEARCH_TIMEOUT_SECONDS),
                    xbmc.LOGWARNING,
                )
                finished.append((addon_id, addon_name, None, "timeout"))

        if active:
            xbmc.sleep(50)

    by_addon = {}
    for addon_id, addon_name, files, error in finished:
        if addon_id and addon_id not in by_addon:
            by_addon[addon_id] = (addon_name, files, error)

    return by_addon


def search(query):
    query = str(query or "").strip()
    if not query:
        return []

    results = []
    addons = kodi_rpc.get_installed_slyguy_video_addons()
    xbmc.log(
        "[script.silo.slyguy.search] Searching %d SlyGuy video add-on(s) for %r"
        % (len(addons), query),
        xbmc.LOGINFO,
    )

    provider_results = _search_addons_with_timeouts(addons, query)

    for addon in addons:
        addon_id = str(addon.get("addonid") or "").strip()
        addon_name = str(addon.get("name") or addon_id).strip()
        if not addon_id:
            continue

        provider = provider_results.get(addon_id)
        if provider is None:
            continue

        stored_name, files, error = provider
        addon_name = stored_name or addon_name
        if error:
            xbmc.log(
                "[script.silo.slyguy.search] %s search skipped: %s"
                % (addon_id, error),
                xbmc.LOGWARNING,
            )
            continue

        count = 0
        for item in files or []:
            if _is_error_item(item):
                xbmc.log(
                    "[script.silo.slyguy.search] %s returned an error item; ignoring it"
                    % addon_id,
                    xbmc.LOGWARNING,
                )
                continue

            path = str(item.get("file") or "").strip()
            label = str(item.get("label") or item.get("title") or "").strip()
            if not path or not label:
                continue

            result = dict(item)
            result.update(
                source="SlyGuy",
                source_addon_id=addon_id,
                source_name=addon_name,
                path=path,
            )
            results.append(result)
            count += 1

        xbmc.log(
            "[script.silo.slyguy.search] %s returned %d result(s)"
            % (addon_id, count),
            xbmc.LOGINFO,
        )

    return results
