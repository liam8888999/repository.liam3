# -*- coding: utf-8 -*-
"""Entry point for Silo & SlyGuy Search."""

import sys

from resources.lib import search


if __name__ == "__main__":
    search.handle_plugin(sys.argv)
