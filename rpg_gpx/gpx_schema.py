#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 13-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm           : gpx_schema.py
#  Version            : 2.0
#  Beschreibung       : Keine Beschreibung verfügbar.
#  Zeilen             : 145
#  Abhängigkeiten     : dataclasses, datetime, typing
#  Klassen            : GPXTrackInfo, GeoPoint, GeoPointRef, GeoPointTime
# ------------------------------------------------------------------------------

from __future__ import annotations
from typing import Any, Final
from datetime import UTC, datetime, timedelta, tzinfo
from dataclasses import dataclass


# -------------------------------------------------------------------------------------------
# Extraktion von Literalen in Konstanten zur Maximierung der Wartbarkeit
# DEFAULT_PRECISION: Final[int] = 6
DEFAULT_DATETIME_TZ: Final[tzinfo] = UTC
ZERO_TIMEDELTA: timedelta = timedelta(0)
# Konstanten für Validierungsgrenzen
MAX_LAT: Final[float] = 90.0
MIN_LAT: Final[float] = -90.0
MAX_LON: Final[float] = 180.0
MIN_LON: Final[float] = -180.0


# -------------------------------------------------------------------------------------------
def is_valid_float(value: float | int | str | Any) -> bool:
    """Prüft, ob der Wert in ein gültiges Float umgewandelt werden kann.

    :param value: (any) Der zu prüfende Wert.
    """
    if isinstance(value, (float, int)):
        return True
    try:
        float(value)
        return True
    except (ValueError, TypeError):
        return False


# -------------------------------------------------------------------------------------------
def safe_float(value: float | int | str | Any) -> float:
    """Wandelt den Wert sicher in ein Float um.

    :param value: (any) Der umzuwandelnde Wert.
    """
    return float(value) if not isinstance(value, float) else value


# ================================================================================
# 1. Datencontainer (alle immutable und speichereffizient)
# 2. Klassen mit Spezial-Logik (DateTimeLocation)
# ================================================================================
@dataclass(slots=True)
class GeoPoint:
    """Basisklasse für Geokoordinaten (immutable, speichereffizient)."""

    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None

    # --------------------------------------------------------------------------------
    def __post_init__(self) -> None:
        """Laufzeit-optimierte Post-Init-Validierung ohne teure Try/Except-Orgien.
        
        :return: (None) Beschreibung des Rückgabewerts.
        """

        lat = self.latitude
        lon = self.longitude
        ele = self.elevation

        # Nur validieren/runden, wenn Werte vorhanden sind
        if lat is not None:
            if not (MIN_LAT <= lat <= MAX_LAT):
                raise ValueError(f"Latitude muss zwischen {MIN_LAT} und {MAX_LAT} liegen.")
            # lat = round(float(lat), DEFAULT_PRECISION)

        if lon is not None:
            if not (MIN_LON <= lon <= MAX_LON):
                raise ValueError(f"Longitude muss zwischen {MIN_LON} und {MAX_LON} liegen.")
            # lon = round(float(lon), DEFAULT_PRECISION)

        # if ele is not None:
        #     ele = round(float(ele), DEFAULT_PRECISION)

        # Zuweisung bei frozen=True nur ausführen, wenn sich durch Runden etwas verändert hat
        if lat != self.latitude:
            object.__setattr__(self, 'latitude', lat)
        if lon != self.longitude:
            object.__setattr__(self, 'longitude', lon)
        if ele != self.elevation:
            object.__setattr__(self, 'elevation', ele)


# ================================================================================
# ================================================================================
@dataclass(slots=True)
class GeoPointTime(GeoPoint):
    """Klasse für einen GPS-Punkt mit zugehörigem Zeitstempel und Höhe."""

    timestamp: datetime | None = None
    tz: tzinfo | None = None
    desc: str = ""

    # --------------------------------------------------------------------------------
    def __post_init__(self) -> None:
        """Stellt sicher, dass UTC-Zeitstempel die Standard-UTC-Instanz nutzen.
        
        :return: (None) Beschreibung des Rückgabewerts.
        """

        # Falls die Basisklasse GeoPoint zwingend ihr eigenes __post_init__ benötigt:
        GeoPoint.__post_init__(self)  # Schnellere Alternative zu super() ohne Import-Konflikte!

        ts = self.timestamp
        if ts is None:
            return

        # 1. Abbruch bei naiver Zeit oder wenn bereits die Ziel-Zeitzone gesetzt ist
        if ts.tzinfo is None or ts.tzinfo is DEFAULT_DATETIME_TZ:
            return

        # 2. utcoffset() direkt auf dem datetime-Objekt aufrufen
        # Gibt timedelta oder None zurück -> Vergleiche direkt mit ZERO_TIMEDELTA
        if ts.utcoffset() == ZERO_TIMEDELTA:
            self.timestamp = ts.replace(tzinfo=DEFAULT_DATETIME_TZ)


# ================================================================================
# ================================================================================
@dataclass
class GeoPointRef(GeoPointTime):
    """GPS-Punkt mit Dateiname und Abstandsdaten (immutable, speichereffizient)."""

    filename: str | None = None
    diff: float | None = None
    dist: float | None = None


# ===========================================================================================
# GpxTrackInfo
# ===========================================================================================
@dataclass
class GPXTrackInfo:
    """Container für die Daten eines einzelnen GPX-Tracks/Segments."""

    # Die Liste der Koordinaten
    points: list[GeoPointTime]
    # Ein einzelner Zeitstempel (z.B. Startzeit des Tracks)
    start_time: datetime | None = None
    end_time: datetime | None = None
