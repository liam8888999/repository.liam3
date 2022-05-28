# -*- coding: utf-8 -*-
"""Custon xbmcgui.DialogProgress."""

import sys

import xbmc
import xbmcgui

from resources import ADDON_NAME
from resources.lib.log import log_msg
from resources.lib.misc import notification


class ProgressBar(xbmcgui.DialogProgress):
    """Module to provide a Constom xbmcgui.DialogProgress."""

    def __init__(self):
        """ProgressBar __init__."""
        super(__class__, self).__init__()
        log_msg("""ProgressBar __init__.""")

    def create_progressdialog(self, head=ADDON_NAME, msg=''):
        """Method to create ProgressBar window"""
        self.create(head, msg)

    def update_progressdialog(self, perc, msg):
        """Method to update ProgressBar window."""
        if self.iscanceled():
            self._iscanceled_close()
        self.update(int(100 * perc), msg)
        xbmc.sleep(200)

    def _iscanceled_close(self):
        """Close method to close progress by cancel button."""
        self.close()
        notification('Desfazendo ultumas ações!', 3000)
        # Exec operations
        sys.exit()

    def close_progressdialog(self):
        """Close method to close progress by normal progress finish."""
        self.close()


class BGProgressBar(xbmcgui.DialogProgressBG):
    """Module to provide a Constom xbmcgui.DialogProgressBG."""

    def __init__(self):
        """BGProgressBar __init__."""
        super(__class__, self).__init__()
        log_msg("""BGProgressBar __init__.""")

    def _create(self, head=ADDON_NAME, msg=''):
        """Method to create BGProgressBar window"""
        self.create(head, msg)

    def _update(self, perc, msg):
        """Method to update BGProgressBar window."""
        if self.isFinished():
            xbmc.sleep(100)
            self._isFinished_close()
        self.update(int(perc), msg)

    def _isfinished_close(self):
        """Close method to close progress by cancel button."""
        self.close()
        notification('Background Desfazendo ultumas ações!', 3000)
        # Exec operations
        sys.exit()

    def _close(self):
        """Close method to close progress by normal progress finish."""
        self.close()
