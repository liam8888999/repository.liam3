# Silo & SlyGuy Search

Kodi context-item add-on for searching a PVR recording across KOLO (the Kodi client for Silo Server) and installed SlyGuy video add-ons.

The add-on calls KOLO's existing Kodi search route at `plugin://plugin.video.kolo/?action=search&query=...` and SlyGuy's standard search route, retaining the original plugin URLs returned by each source.

Requirements:
- Kodi Matrix or newer
- KOLO (`plugin.video.kolo`) installed for Silo Server results
- SlyGuy video add-ons installed for SlyGuy results

No third-party Python modules are required.
