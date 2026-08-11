"""Paket-Fassade fuer rpg_gpx."""

from .gpx_const import GPX_NAMESPACE, GPX_NAMESPACE_GARMIN, GPX_NAMESPACES, XPATH_GARMIN_RPT, TAG_TRK, TAG_RTE, TAG_TRKPT, TAG_RTEPT, TAG_RPT, TAG_ELE, TAG_TIME
from .gpx_io import GPXDataLoader
from .gpx_schema import DEFAULT_DATETIME_TZ, ZERO_TIMEDELTA, MAX_LAT, MIN_LAT, MAX_LON, MIN_LON, is_valid_float, safe_float, GeoPoint, GeoPointTime, GeoPointRef, GPXTrackInfo
from .gpx_utils import EARTH_RADIUS_METERS, WGS84_A, WGS84_B, WGS84_F, MAX_ITERATIONS, CONVERGENCE_THRESHOLD, haversine, haversine_geo

__all__ = [
    "GPX_NAMESPACE",
    "GPX_NAMESPACE_GARMIN",
    "GPX_NAMESPACES",
    "XPATH_GARMIN_RPT",
    "TAG_TRK",
    "TAG_RTE",
    "TAG_TRKPT",
    "TAG_RTEPT",
    "TAG_RPT",
    "TAG_ELE",
    "TAG_TIME",
    "GPXDataLoader",
    "DEFAULT_DATETIME_TZ",
    "ZERO_TIMEDELTA",
    "MAX_LAT",
    "MIN_LAT",
    "MAX_LON",
    "MIN_LON",
    "is_valid_float",
    "safe_float",
    "GeoPoint",
    "GeoPointTime",
    "GeoPointRef",
    "GPXTrackInfo",
    "EARTH_RADIUS_METERS",
    "WGS84_A",
    "WGS84_B",
    "WGS84_F",
    "MAX_ITERATIONS",
    "CONVERGENCE_THRESHOLD",
    "haversine",
    "haversine_geo"
]
