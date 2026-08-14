#!/usr/bin/env python
# ------------------------------------------------------------------------------
# 13-08-2026
# RalfPeter <ralfpeter.bergheim@gmail.com>
# https://github.com/RalfPeter/
#
# Released under GNU GENERAL PUBLIC LICENSE v3. (Use at your own risk)
# ------------------------------------------------------------------------------
#  Programm           : gpx_utils.py
#  Version            : 2.0
#  Beschreibung       : Keine Beschreibung verfügbar.
#  Zeilen             : 180
#  Abhängigkeiten     : math
# ------------------------------------------------------------------------------

from math import radians, sin, cos, sqrt, atan, atan2, tan

# ===========================================================================================
# Konstante für den mittleren Erdradius in Metern (WGS-84-Mittelwert)
# ===========================================================================================
EARTH_RADIUS_METERS: float = 6371000.0
# ===========================================================================================
# WGS-84 ELLIPSOID KONSTANTEN
# ===========================================================================================
WGS84_A = 6378137.0  # Äquatorradius (große Halbachse) in Metern
WGS84_B = 6356752.314245  # Polradius (kleine Halbachse) in Metern
WGS84_F = 1 / 298.257223563  # Abplattung
MAX_ITERATIONS = 200
CONVERGENCE_THRESHOLD = 1e-12


# ---------------------------------------------------------------------------------------
def haversine(lat1: float | None = None, lon1: float | None = None, lat2: float | None = None, lon2: float | None = None) -> float:
    """Berechnet die Großkreisentfernung (Luftlinie) zwischen zwei Geopunkten.
    
    :param lat1: (float | None) Breitengrad des ersten Punkts in Dezimalgrad.
    :param lon1: (float | None) Längengrad des ersten Punkts in Dezimalgrad.
    :param lat2: (float | None) Breitengrad des zweiten Punkts in Dezimalgrad.
    :param lon2: (float | None) Längengrad des zweiten Punkts in Dezimalgrad.
    :return: (float) Beschreibung
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0

    # Wenn die Punkte identisch sind, ist die Distanz 0
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    # Statische Code-Analyse beruhigen
    assert lat1 is not None and lat2 is not None
    phi1: float = radians(lat1)
    phi2: float = radians(lat2)
    dphi: float = phi2 - phi1
    dlambda: float = radians(lon2 - lon1)
    # Haversine-Formel zur Berechnung des Zentralwinkels (a = sin²(Δφ/2) + cos(φ1) * cos(φ2) * sin²(Δλ/2))
    a: float = sin(dphi / 2.0) ** 2 + cos(phi1) * cos(phi2) * sin(dlambda / 2.0) ** 2

    # Großkreisentfernung = R * c, wobei c = 2 * atan2(sqrt(a), sqrt(1-a)) ist
    # atan2 ist numerisch stabiler als arcsin, besonders bei kleinen a (kurze Distanzen)
    return round(EARTH_RADIUS_METERS * (2.0 * atan2(sqrt(a), sqrt(1.0 - a))), 4)


# ---------------------------------------------------------------------------------------
def haversine_geo(lat1: float | None, lon1: float | None, lat2: float | None, lon2: float | None,) -> float:
    """Berechnet die präzise geodätische Distanz zwischen zwei Punkten auf dem WGS-84 Ellipsoid.
    
    :param lat1: (float | None) Breitengrad des ersten Punkts in Dezimalgrad.
    :param lon1: (float | None) Längengrad des ersten Punkts in Dezimalgrad.
    :param lat2: (float | None) Breitengrad des zweiten Punkts in Dezimalgrad.
    :param lon2: (float | None) Längengrad des zweiten Punkts in Dezimalgrad.
    :return: (float) Beschreibung
    """
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0

    # Wenn die Punkte identisch sind, ist die Distanz 0
    if lat1 == lat2 and lon1 == lon2:
        return 0.0

    # Konvertierung in Bogenmaß
    # Statische Code-Analyse beruhigen
    assert lat1 is not None and lat2 is not None
    u1 = atan((1 - WGS84_F) * tan(radians(lat1)))
    u2 = atan((1 - WGS84_F) * tan(radians(lat2)))
    lon_diff = radians(lon2 - lon1)

    sin_u1, cos_u1 = sin(u1), cos(u1)
    sin_u2, cos_u2 = sin(u2), cos(u2)

    lambda_lon = lon_diff

    # Iterative Berechnung des Zentralwinkels
    for _ in range(MAX_ITERATIONS):
        sin_lambda = sin(lambda_lon)
        cos_lambda = cos(lambda_lon)

        sin_sigma = sqrt(
            (cos_u2 * sin_lambda) ** 2
            + (cos_u1 * sin_u2 - sin_u1 * cos_u2 * cos_lambda) ** 2
        )

        # Antipodische Punkte abfangen (Punkte, die sich genau gegenüberliegen)
        if sin_sigma == 0:
            return 0.0

        cos_sigma = sin_u1 * sin_u2 + cos_u1 * cos_u2 * cos_lambda
        sigma = atan2(sin_sigma, cos_sigma)

        sin_alpha = cos_u1 * cos_u2 * sin_lambda / sin_sigma
        cos_sq_alpha = 1 - sin_alpha**2

        # Spezialfall: Großkreis verläuft über die Pole
        if cos_sq_alpha == 0:
            cos2_sigma_m = 0.0
        else:
            cos2_sigma_m = cos_sigma - 2 * sin_u1 * sin_u2 / cos_sq_alpha

        lambda_prev = lambda_lon
        c = (
            WGS84_F
            / 16
            * cos_sq_alpha
            * (4 + WGS84_F * (4 - 3 * cos_sq_alpha))
        )
        lambda_lon = lon_diff + (1 - c) * WGS84_F * sin_alpha * (
            sigma
            + c
            * sin_sigma
            * (
                cos2_sigma_m
                + c * cos_sigma * (-1 + 2 * cos2_sigma_m * cos2_sigma_m)
            )
        )

        # Prüfung auf Konvergenz
        if abs(lambda_lon - lambda_prev) < CONVERGENCE_THRESHOLD:
            break
    else:
        # Falls die Formel nicht konvergiert (z.B. bei fast antipodischen Punkten),
        # fallen wir als extrem robusten Fallback auf eine sphärische Näherung zurück.
        # log_msg = "Vincenty konvergiert nicht. Nutze sphärischen Fallback."
        # Hier optional loggen: log("haversine_geo", log_msg)
        return _spherical_fallback(lat1, lon1, lat2, lon2)

    # Auswertung der Distanz auf dem Ellipsoid
    u_sq = cos_sq_alpha * (WGS84_A**2 - WGS84_B**2) / (WGS84_B**2)
    a = 1 + u_sq / 16384 * (4096 + u_sq * (-768 + u_sq * (320 - 175 * u_sq)))
    b = u_sq / 1024 * (256 + u_sq * (-128 + u_sq * (74 - 47 * u_sq)))

    delta_sigma = (
        b
        * sin_sigma
        * (
            cos2_sigma_m
            + b
            / 4
            * (
                cos_sigma * (-1 + 2 * cos2_sigma_m**2)
                - b
                / 6
                * cos2_sigma_m
                * (-3 + 4 * sin_sigma**2)
                * (-3 + 4 * cos2_sigma_m**2)
            )
        )
    )

    distance_meters = WGS84_B * a * (sigma - delta_sigma)
    return round(distance_meters, 4)


# ---------------------------------------------------------------------------------------
def _spherical_fallback(lat1: float | None, lon1: float | None, lat2: float | None, lon2: float | None) -> float:
    """Einfacher numerischer Fallback basierend auf der Haversine-Formel.
    
    :param lat1: (float | None) Beschreibung
    :param lon1: (float | None) Beschreibung
    :param lat2: (float | None) Beschreibung
    :param lon2: (float | None) Beschreibung
    :return: (float) Beschreibung
    """
    # Sicherheitsnetz, falls die Funktion mal isoliert aufgerufen wird
    if lat1 is None or lon1 is None or lat2 is None or lon2 is None:
        return 0.0

    phi1 = radians(lat1)
    phi2 = radians(lat2)
    dphi = phi2 - phi1
    dlambda = radians(lon2 - lon1)
    a = (
        sin(dphi / 2.0) ** 2
        + cos(phi1) * cos(phi2) * sin(dlambda / 2.0) ** 2
    )
    # Mittlerer Erdradius nach WGS-84 (ca. 6371000.8 m)
    return round(6371000.8 * (2.0 * atan2(sqrt(a), sqrt(1.0 - a))), 4)
