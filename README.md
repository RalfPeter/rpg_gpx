# RPG Tools Framework Suite

Eine leistungsfähige, modulare Python-Framework-Suite zur Extraktion und Verarbeitung von **GoPro-Telemetriedaten (GPMF)**, Erzeugung von **GPX-Tracks**, **Geokodierung**, **Karten-Rendering**, **Video-Overlays** sowie wiederverwendbaren **PySide6-UI-Utilities**.

---

## 🏗️ Architektur & Modul-Übersicht

Das Framework **rpg-tools** stellt die zentrale Bibliothek dar, auf der Anwendungs-Suites wie **[gopro-tools](https://github.com/RalfPeter/gopro-tools)** (GUIs und CLI-Skripte) aufbauen:

```mermaid
flowchart TD
    GOPRO["<b>gopro-tools</b><br/>(Anwendungen: gui_gopro2file, gui_gopro2overlay, CLI Pipelines)"]

    GOPRO -->|nutzt als Bibliothek| RPG["<b>rpg-tools</b><br/>(Core Framework Suite)"]

    subgraph Modules [" "]
        direction LR
        M1["<b>rpg_gpmf</b><br/>Telemetrie<br/>GPMF KLV"]
        M2["<b>rpg_geo</b><br/>Geocoding<br/>GeoNames"]
        M3["<b>rpg_gpx</b><br/>GPX Tracks<br/>Schema / IO"]
        M4["<b>rpg_gui</b><br/>PySide6 Base<br/>Templates/Utils"]
        M5["<b>rpg_utils</b><br/>Shared Utilities<br/>Logger/Config/Math"]
        M6["<b>rpg_overlay</b><br/>Video<br/>Overlays"]
    end

```

---

---

## rpg_gpx
