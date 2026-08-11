#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 10-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm          : gpx_const.py
#  Version           : 2.0
#  Beschreibung      : Keine Beschreibung verfügbar.
#  Zeilen            : 26
#  Abhängigkeiten    : typing
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter.bergheim@gmail.com>
# ------------------------------------------------------------------------------

from typing import Final


# --- GPX Namespace ---
GPX_NAMESPACE: Final[str] = "http://www.topografix.com/GPX/1/1"
GPX_NAMESPACE_GARMIN: Final[str] = "http://www.garmin.com/xmlschemas/GpxExtensions/v3"

GPX_NAMESPACES: Final[dict[str, str]] = {
    "gpxx": GPX_NAMESPACE_GARMIN,
    "trp": "http://www.garmin.com/xmlschemas/TripExtensions/v1",
    "gpx": "https://www.topografix.com/GPX/1/0",
}

XPATH_GARMIN_RPT: str = f".//{{{GPX_NAMESPACE_GARMIN}}}rpt"

# =======================================================================
# KONSTANTEN: HYBRID-STRATEGIE FÜR LXML
# =======================================================================
# Tag-Konstanten für den Direktvergleich im Hot-Path
TAG_TRK: Final[str] = "trk"
TAG_RTE: Final[str] = "rte"
TAG_TRKPT: Final[str] = "trkpt"
TAG_RTEPT: Final[str] = "rtept"
TAG_RPT: Final[str] = "rpt"
TAG_ELE: Final[str] = "ele"
TAG_TIME: Final[str] = "time"
