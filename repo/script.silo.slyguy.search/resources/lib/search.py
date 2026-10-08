# -*- coding: utf-8 -*-
"""UI and search orchestration for the bridge add-on."""

import difflib
import re
import sys
import time
from collections import OrderedDict
from functools import lru_cache
from urllib.parse import parse_qsl, urlparse

import xbmc
import xbmcgui
import xbmcplugin

from . import kodi_rpc, silo, slyguy

ADDON_ID = "script.silo.slyguy.search"

SEARCH_CACHE_TTL_SECONDS = 45.0
SEARCH_CACHE_MAX_ENTRIES = 8
MAX_DISPLAY_RESULTS = 25

_SEARCH_CACHE = OrderedDict()


def _cache_key(query):
    return " ".join(str(query or "").strip().casefold().split())


def _get_cached_results(key):
    entry = _SEARCH_CACHE.get(key)
    if entry is None:
        return None

    cached_at, results = entry
    if time.monotonic() - cached_at >= SEARCH_CACHE_TTL_SECONDS:
        _SEARCH_CACHE.pop(key, None)
        return None

    _SEARCH_CACHE.move_to_end(key)
    return list(results)


def _store_cached_results(key, results):
    _SEARCH_CACHE[key] = (time.monotonic(), list(results))
    _SEARCH_CACHE.move_to_end(key)

    while len(_SEARCH_CACHE) > SEARCH_CACHE_MAX_ENTRIES:
        _SEARCH_CACHE.popitem(last=False)


def _handle_from_argv(argv=None):
    argv = argv if argv is not None else sys.argv
    try:
        return int(argv[1])
    except (IndexError, TypeError, ValueError):
        return -1


def _get_video_tag_value(tag, names):
    for name in names:
        getter = getattr(tag, name, None)
        if getter is None:
            continue
        try:
            value = getter()
        except Exception:
            continue
        if value not in (None, "", 0):
            return value
    return ""


def _info_label(name):
    try:
        return str(xbmc.getInfoLabel(name) or "").strip()
    except Exception:
        return ""


def query_from_listitem(list_item):
    if list_item is None:
        return ""

    # PVR recordings can expose the programme/EPG title separately from the
    # episode name. Prefer the explicit PVR fields before video-library fields.
    # EpgEventTitle is the programme title; EpisodeName is the episode subtitle.
    candidates = [
        _info_label("ListItem.TVShowTitle"),
        _info_label("ListItem.EpgEventTitle"),
    ]

    episode_name = _info_label("ListItem.EpisodeName")

    try:
        tag = list_item.getVideoInfoTag()
    except Exception:
        tag = None

    tag_show = ""
    tag_title = ""
    if tag is not None:
        tag_show = str(
            _get_video_tag_value(tag, ("getTVShowTitle", "getTvShowTitle"))
            or ""
        ).strip()
        tag_title = str(
            _get_video_tag_value(tag, ("getTitle", "getOriginalTitle"))
            or ""
        ).strip()

    # Do not accidentally use an episode title as the show title when Kodi has
    # only populated the generic title fields on a PVR recording.
    for value in candidates:
        if value and value.lower() != episode_name.lower():
            xbmc.log(
                "[script.silo.slyguy.search] Selected PVR programme/show title: %r"
                % value,
                xbmc.LOGINFO,
            )
            return value

    if tag_show and tag_show.lower() != episode_name.lower():
        xbmc.log(
            "[script.silo.slyguy.search] Selected VideoInfoTag TV show title: %r"
            % tag_show,
            xbmc.LOGINFO,
        )
        return tag_show

    # As a final PVR-specific fallback, the recording label/title is normally
    # the programme title. Only use the tag title when it is not the episode
    # subtitle.
    for getter_name in ("getLabel", "getLabel2"):
        try:
            value = str(getattr(list_item, getter_name)() or "").strip()
        except Exception:
            value = ""
        if value and value.lower() != episode_name.lower():
            xbmc.log(
                "[script.silo.slyguy.search] Using PVR recording label: %r"
                % value,
                xbmc.LOGINFO,
            )
            return value

    if tag_title:
        return tag_title

    return episode_name or ""


@lru_cache(maxsize=4096)
def _match_text(value):
    value = str(value or "").lower().strip()
    value = re.sub(r"[^a-z0-9]+", " ", value)
    return " ".join(value.split())


def _match_score(q, q_tokens, item):
    """Return a relevance score for a provider result."""
    if not q:
        return 0.0

    candidates = (
        ("title", item.get("title"), 1.00),
        ("originaltitle", item.get("originaltitle"), 0.98),
        ("tvshowtitle", item.get("tvshowtitle"), 0.96),
        ("showtitle", item.get("showtitle"), 0.96),
        ("label", item.get("label"), 0.94),
    )

    best = 0.0

    for field, value, weight in candidates:
        text = _match_text(value)
        if not text:
            continue

        score = 0.0
        if text == q:
            score = 1000.0
        elif text.startswith(q + " "):
            score = 900.0
        elif q in text:
            score = 800.0
        else:
            tokens = set(text.split())
            if q_tokens and q_tokens.issubset(tokens):
                score = 740.0

            ratio = difflib.SequenceMatcher(None, q, text).ratio()
            score = max(score, ratio * 650.0)

        if field in ("tvshowtitle", "showtitle"):
            score *= 0.96

        score -= max(0, len(text) - len(q)) * 0.25
        best = max(best, score * weight)

    return best


def _rank_results(query, results):
    ranked = []
    for index, item in enumerate(results):
        source = str(item.get("source") or "").strip().lower()
        source_priority = 0 if source == "silo" else 1
        ranked.append(
            (
                _match_score(query, item),
                source_priority,
                index,
                item,
            )
        )

    # Relevance is primary. Silo wins ties between otherwise equally relevant
    # results, then the original provider order remains stable.
    ranked.sort(key=lambda row: (-row[0],def _rank_results(query, results):
    q = _match_text(query)
    q_tokens = set(q.split()) if q else set()

    ranked = []
    for index, item in enumerate(results):
        source = str(item.get("source") or "").strip().lower()
        source_priority = 0 if source == "silo" else 1
        ranked.append(
            (
                _match_score(q, q_tokens, item),
                source_priority,
                index,
                item,
            )
        )

    ranked.sort(key=lambda row: (-row[0], row[1], row[2]))

    xbmc.log(
        "[script.silo.slyguy.search] Ranked %d combined result(s) for %r"
        % (len(ranked), query),
        xbmc.LOGINFO,
    )
    for position, (score, _, _, item) in enumerate(ranked[:5], 1):
        label = item.get("label") or item.get("title") or ""
        xbmc.log(
            "[script.silo.slyguy.search] Rank %d score=%.1f label=%r source=%r"
            % (
                position,
                score,
                label,
                item.get("source_name") or item.get("source") or "",
            ),
            xbmc.LOGDEBUG,
        )

    return [item for _, _, _, item in ranked]


def _normalise_result(item):
    path = str(item.get("path") or item.get("file") or "").strip()
    label = str(item.get("label") or item.get("title") or "").strip()
    if not path or not label:
        return None

    source = str(item.get("source") or "").strip()
    addon_name = str(item.get("source_name") or source).strip()
    display_label = label
    if source == "SlyGuy" and addon_name:
        display_label = "[%s] %s" % (addon_name, label)
    elif source == "Silo":
        display_label = "[Silo] %s" % label

    li = xbmcgui.ListItem(label=display_label)
    for art_key, rpc_key in (("thumb", "thumbnail"), ("fanart", "fanart")):
        value = item.get(rpc_key)
        if value:
            li.setArt({art_key: value})

    video_tag = li.getVideoInfoTag()
    for setter, value in (
        ("setTitle", display_label),
        ("setPlot", item.get("plot")),
        ("setYear", item.get("year")),
        ("setRating", item.get("rating")),
        ("setDuration", item.get("runtime")),
        ("setSeason", item.get("season")),
        ("setEpisode", item.get("episode")),
    ):
        if value in (None, "", 0):
            continue
        method = getattr(video_tag, setter, None)
        if method is None:
            continue
        try:
            method(value)
        except (TypeError, ValueError):
            try:
                method(int(value))
            except Exception:
                pass

    is_folder = item.get("type") == "folder" or item.get("filetype") == "directory" or path.endswith("/")
    if not is_folder and str(item.get("type") or "").lower() in {"movie", "episode", "file"}:
        li.setProperty("IsPlayable", "true")
    return display_label, path, li, is_folder


def _dedupe(results):
    seen = set()
    output = []
    for item in results:
        key = (
            str(item.get("source_addon_id") or item.get("source") or "").strip(),
            str(item.get("path") or item.get("file") or "").strip(),
        )
        if key in seen:
            continue
        seen.add(key)
        output.append(item)
    return output


def run_search(query):
    query = str(query or "").strip()
    if not query:
        return []

    key = _cache_key(query)
    cached = _get_cached_results(key)
    if cached is not None:
        xbmc.log(
            "[script.silo.slyguy.search] Search cache hit for %r (%d result(s))"
            % (query, len(cached)),
            xbmc.LOGDEBUG,
        )
        return cached

    combined = _dedupe(silo.search(query) + slyguy.search(query))
    ranked = _rank_results(query, combined)

    # Rank everything first, then only build Kodi list items for the best
    # matches. This preserves relevance ordering without making Kodi render
    # potentially hundreds of provider results.
    ranked = ranked[:MAX_DISPLAY_RESULTS]
    _store_cached_results(key, ranked)
    return list(ranked)


def show_results(query, handle=None):
    # Keep provider aggregation silent. Individual add-ons may still emit their
    # own explicit dialogs, but this bridge does not display a search popup.
    results = run_search(query)

    handle = _handle_from_argv() if handle is None else handle
    xbmcplugin.setPluginCategory(handle, "Search: %s" % query)
    xbmcplugin.setContent(handle, "videos")

    # Relevance is calculated before items are added. Prevent Kodi/skin sorting
    # the list by the visible "[Addon Name] ..." label and destroying that order.
    xbmcplugin.addSortMethod(handle, xbmcplugin.SORT_METHOD_UNSORTED)

    added = 0
    for result in results:
        normalised = _normalise_result(result)
        if normalised is None:
            continue
        _, path, li, is_folder = normalised
        xbmcplugin.addDirectoryItem(handle, path, li, is_folder)
        added += 1

    if not added:
        xbmcgui.Dialog().notification("Search Streaming Services", "No results found for: %s" % query)
    xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=True)


def handle_plugin(argv):
    handle = _handle_from_argv(argv)
    query = ""
    route = ""

    if len(argv) > 2:
        parsed = urlparse(argv[2])
        params = dict(parse_qsl(parsed.query, keep_blank_values=True))
        route = params.get("_", "").strip()
        query = params.get("query", "").strip()

    if route == "search" and query:
        show_results(query, handle)
        return

    # No route means Kodi has navigated to the plugin root. This is the
    # transient window created by the PVR context action; close it so Back
    # returns to the recordings container rather than opening a new search.
    if not route:
        xbmc.executebuiltin("Action(Close)")
        xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=True)
        return

    xbmcplugin.endOfDirectory(handle, succeeded=True, cacheToDisc=True)
