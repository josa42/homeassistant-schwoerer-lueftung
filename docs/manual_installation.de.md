# Manuelle Installation

[English](manual_installation.md) | **Deutsch**

Der [Button im README](../README.de.md#installation) erledigt all das mit einem
Klick. Diese Schritte sind für den Fall, dass der Button nicht funktioniert oder
du HACS gar nicht verwenden möchtest.

## Das Repository von Hand zu HACS hinzufügen

1. Stelle sicher, dass [HACS](https://hacs.xyz/) in deiner Home-Assistant-Instanz installiert ist
2. Öffne HACS → Integrationen
3. Klicke auf das Drei-Punkte-Menü (oben rechts) → Benutzerdefinierte Repositories
4. Repository-URL eintragen: `https://github.com/josa42/homeassistant-schwoerer-lueftung`
5. Kategorie: Integration
6. Klicke auf „Hinzufügen“
7. Klicke auf der Karte „Schwörer Lüftung“ auf „Herunterladen“
8. Starte Home Assistant neu

## Ohne HACS

1. Lade das neueste Release von den [GitHub-Releases](https://github.com/josa42/homeassistant-schwoerer-lueftung/releases) herunter
2. Entpacke den Ordner `custom_components/schwoerer_lueftung`
3. Kopiere ihn in das Verzeichnis `custom_components` deiner Home-Assistant-Installation:
   ```
   config/
   └── custom_components/
       └── schwoerer_lueftung/
   ```
4. Starte Home Assistant neu

Für ein Update wiederholst du das mit dem neuen Release und startest erneut neu.
HACS erledigt das mit einem Klick, deshalb ist es der empfohlene Weg.
