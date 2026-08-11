#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 10-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm          : gpx_io.py
#  Version           : 2.0
#  Beschreibung      : Keine Beschreibung verfügbar.
#  Zeilen            : 229
#  Abhängigkeiten    : datetime, functools, io, lxml, pathlib, typing
#  Klassen           : GPXDataLoader
# ------------------------------------------------------------------------------
#  Public Methoden:
#    GPXDataLoader                                        → Hochperformanter, speicherschonender GPX-Parser auf Basis von lxml.etree.iterparse.
#      get_tracks()                                       → Gibt alle geladenen Tracks der Datei zurück.
#      get_routes()                                       → Gibt alle geladenen Routen der Datei zurück.
#      get_all()                                          → Gibt Tracks und Routen kombiniert zurück.
# ------------------------------------------------------------------------------
#  Copyright (C) 2026 <ralfpeter.bergheim@gmail.com>
# ------------------------------------------------------------------------------

from __future__ import annotations
import io
from functools import cache
from datetime import datetime
from pathlib import Path
from typing import Final
from lxml import etree

from rpg_gpx.gpx_const import TAG_TRK, TAG_RTE, TAG_TRKPT, TAG_RTEPT, TAG_RPT, XPATH_GARMIN_RPT
from rpg_gpx.gpx_schema import GeoPointTime, GPXTrackInfo, DEFAULT_DATETIME_TZ


# --------------------------------------------------------------------------------
# Caching für Tag-Namen
# --------------------------------------------------------------------------------
@cache
def _get_local_name(tag: str) -> str:
    """Entfernt den Namespace aus einem XML-Tag und cached das Ergebnis.

    :param tag: (str) Das Tag mit Namespace ({URI}local_name).
    :return: (str) Bereinigter Tag-Name.
    """
    return tag.rpartition("}")[2]


# ===========================================================================================
# GPXDataLoader
# ===========================================================================================
# noinspection PyProtectedMember
class GPXDataLoader:
    """Hochperformanter, speicherschonender GPX-Parser auf Basis von lxml.etree.iterparse."""

    # --------------------------------------------------------------------------------
    def __init__(self, path: Path, verbose: bool = False) -> None:
        """Initialisiert den Loader und startet automatisch den Ladevorgang.
        
        :param path: (Path) Pfad zur GPX-Datei.
        :param verbose: (bool) Flag für detaillierte Log-Ausgaben.
        """
        self._path: Final[Path] = path
        self.verbose: Final[bool] = verbose
        self._tracks_list: list[GPXTrackInfo] = []
        self._routes_list: list[GPXTrackInfo] = []

        # Startet den Ladevorgang direkt bei Instanziierung
        self._load_gpx_data()

    # --------------------------------------------------------------------------------
    @staticmethod
    def _parse_point(elem: etree._Element) -> GeoPointTime | None:
        """Extrahiert GeoPointTime mit spekulativem Direktzugriff auf Kinder.

        :param elem: (etree._Element) Das Punkt-Element (<trkpt>, <rtept> oder <rpt>).
        :return: (GeoPointTime | None) Das erzeugte Punkte-Objekt oder None bei Fehler.
        """
        attrib = elem.attrib
        try:
            lat = float(attrib["lat"])
            lon = float(attrib["lon"])
        except (KeyError, ValueError):
            return None

        ele: float | None = None
        timestamp: datetime | None = None

        # Spekulativer Direktzugriff auf Kind 0 (<ele>) und Kind 1 (<time>)
        # Das deckt 99% aller GPX-Punkte ohne Tag-String-Erzeugung ab!
        num_children = len(elem)

        if num_children >= 1:
            child0 = elem[0]
            if "ele" in child0.tag and child0.text:
                try:
                    ele = float(child0.text)
                except ValueError:
                    pass

        if num_children >= 2:
            child1 = elem[1]
            if "time" in child1.tag and child1.text:
                text = child1.text
                try:
                    if text.endswith("Z"):
                        timestamp = datetime.fromisoformat(text[:-1]).replace(tzinfo=DEFAULT_DATETIME_TZ)
                    else:
                        timestamp = datetime.fromisoformat(text)
                except ValueError:
                    pass

        # Fallback für Punkte mit mehr Kindern, abweichender Reihenfolge oder Extensions
        if num_children > 2 or (ele is None and timestamp is None and num_children > 0):
            for child in elem:
                text = child.text
                if not text:
                    continue
                tag = child.tag
                if ele is None and "ele" in tag:
                    try:
                        ele = float(text)
                    except ValueError:
                        pass
                elif timestamp is None and "time" in tag:
                    try:
                        if text.endswith("Z"):
                            timestamp = datetime.fromisoformat(text[:-1]).replace(tzinfo=DEFAULT_DATETIME_TZ)
                        else:
                            timestamp = datetime.fromisoformat(text)
                    except ValueError:
                        pass

        return GeoPointTime(lat, lon, ele, timestamp, DEFAULT_DATETIME_TZ, "")

    # --------------------------------------------------------------------------------
    @staticmethod
    def _build_container_info(points: list[GeoPointTime]) -> GPXTrackInfo | None:
        """Validiert die gesammelten Punkte und erstellt das GPXTrackInfo-Objekt.

        :param points: (list[GeoPointTime]) Die bereits geparsten Punkte des Containers.
        :return: (GPXTrackInfo | None) Das strukturierte Track-Objekt oder None.
        """
        if not points:
            return None

        start_time = next((p.timestamp for p in points if p.timestamp), None)

        if start_time is None:
            return None

        return GPXTrackInfo(points=points, start_time=start_time)

    # -----------------------------------------------------------------------
    # STREAMING-IMPLEMENTATION
    # -----------------------------------------------------------------------
    def _load_gpx_data(self) -> None:
        """Parst die GPX-Datei hochperformant aus dem Arbeitsspeicher (Memory Stream).
        
        :return: (None) Beschreibung des Rückgabewerts.
        """

        with open(self._path, "rb") as f:
            xml_bytes = f.read()

        target_tags = (
            f"{{*}}{TAG_TRKPT}",
            f"{{*}}{TAG_RPT}",
            f"{{*}}{TAG_RTEPT}",
            f"{{*}}{TAG_TRK}",
            f"{{*}}{TAG_RTE}",
        )

        context = etree.iterparse(
            io.BytesIO(xml_bytes),
            events=("end",),
            tag=target_tags,
        )

        aktuelle_punkte: list[GeoPointTime] = []

        # Lokale Methoden-Referenzen für maximale Schleifengeschwindigkeit
        parse_point = self._parse_point
        append_punkt = aktuelle_punkte.append

        for _, element in context:
            tag: str = element.tag  # z. B. "{http://www.topografix.com/GPX/1/1}trkpt"

            # C-basierter Substring-Vergleich anstelle von _get_local_name
            if TAG_TRKPT in tag or TAG_RPT in tag:
                point = parse_point(element)
                if point is not None:
                    append_punkt(point)
                element.clear()

            elif TAG_RTEPT in tag:
                if element.find(XPATH_GARMIN_RPT) is None:
                    point = parse_point(element)
                    if point is not None:
                        append_punkt(point)
                element.clear()

            elif TAG_TRK in tag:
                if aktuelle_punkte:
                    track_info = self._build_container_info(aktuelle_punkte)
                    if track_info:
                        self._tracks_list.append(track_info)
                aktuelle_punkte = []
                append_punkt = aktuelle_punkte.append  # Referenz neu binden für die neue Liste
                element.clear()
                while element.getprevious() is not None:
                    del element.getparent()[0]

            elif TAG_RTE in tag:
                if aktuelle_punkte:
                    route_info = self._build_container_info(aktuelle_punkte)
                    if route_info:
                        self._routes_list.append(route_info)
                aktuelle_punkte = []
                append_punkt = aktuelle_punkte.append  # Referenz neu binden
                element.clear()
                while element.getprevious() is not None:
                    del element.getparent()[0]

    # -----------------------------------------------------------------------
    # ÖFFENTLICHE ZUGRIFFSMETHODEN
    # -----------------------------------------------------------------------
    def get_tracks(self) -> list[GPXTrackInfo]:
        """Gibt alle geladenen Tracks der Datei zurück.
        
        :return: (list[GPXTrackInfo]) Beschreibung des Rückgabewerts.
        """

        return self._tracks_list

    # --------------------------------------------------------------------------------
    def get_routes(self) -> list[GPXTrackInfo]:
        """Gibt alle geladenen Routen der Datei zurück.
        
        :return: (list[GPXTrackInfo]) Beschreibung des Rückgabewerts.
        """

        return self._routes_list

    # --------------------------------------------------------------------------------
    def get_all(self) -> list[GPXTrackInfo]:
        """Gibt Tracks und Routen kombiniert zurück.
        
        :return: (list[GPXTrackInfo]) Beschreibung des Rückgabewerts.
        """

        return self._tracks_list + self._routes_list
