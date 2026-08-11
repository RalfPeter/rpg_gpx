# rpg_gpx

Eine leistungsfähige, modulare Python-Framework-Suite zur Extraktion und Verarbeitung von **GoPro-Telemetriedaten (GPMF)**, Erzeugung von **GPX-Tracks**, **Geokodierung**, **Karten-Rendering**, **Video-Overlays** sowie wiederverwendbaren **PySide6-UI-Utilities**.

---

## 🏗️ Architektur & Modul-Übersicht

Das Framework **rpg-tools** stellt die zentrale Bibliothek dar, auf der Anwendungs-Suites wie **[gopro-tools](https://github.com/RalfPeter/gopro-tools)** (GUIs und CLI-Skripte) aufbauen:

  ┌───────────────────────────────────────────────────────────────────────────────────┐
  │                                    gopro-tools                                    │
  │        (Anwendungen: gui_gopro2file, gui_gopro2overlay, CLI Pipelines)            │
  └─────────────────────────────────────────┬─────────────────────────────────────────┘
                                            │  nutzt als Bibliothek
                                            ▼
  ┌─────────────────────────────────────────────────────────────────────────────────────┐
  │                                     rpg-tools                                       │
  │                              (Core Framework Suite)                                 │
  ├───────────┬───────────┬───────────┬────────────────┬───────────────────┬────────────┤
  │ rpg_gpmf  │  rpg_geo  │  rpg_gpx  │    rpg_gui     │     rpg_utils     │rpg_overlay │
  │Telemetrie │Geocoding  │GPX Tracks │ PySide6 Base   │ Shared Utilities  │ Video      │
  │GPMF KLV   │GeoNames   │Schema / IO│ Templates/Utils│ Logger/Config/Math│ Overlays   │
  └───────────┴───────────┴───────────┴────────────────┴───────────────────┴────────────┘

---

---

Typensichere Datenstrukturen (`GeoPointTime`), Schema-Validierung, I/O-Operationen und Hilfsfunktionen für GPX-Dateien.

### Enthaltene Komponenten
* **GPX I/O:** Lesen, Parsen und Schreiben von GPX-Dateien.
* **Transformatoren:** Konvertierung von Koordinaten, Höhenprofilen und Zeitstempeln.
* **Validierung:** Prüfung von Track-Integrität, zeitlichen Lücken und Plausibilität.

### Installation

pip install git+[https://github.com/RalfPeter/rpg_gpx.git](https://github.com/RalfPeter/rpg_gpx.git)

### Verwendung

from rpg_gpx import parse_gpx_file

track_points = parse_gpx_file("route.gpx")
