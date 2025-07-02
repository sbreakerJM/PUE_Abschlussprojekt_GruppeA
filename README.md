
# EKG-Analyse-App

Diese Anwendung ermöglicht es, EKG-Daten hochzuladen, zu visualisieren und Herzfrequenz-Analysen durchzuführen. Sie bietet außerdem Benutzerverwaltung mit Login, Profilbearbeitung und Anomalieerkennung.

---

## Voraussetzungen

Installiere zuerst die benötigten Pakete:

```bash
pip install streamlit pandas numpy plotly scipy
```

---

## Starten der App

Im Projektordner:

```bash
bash: python -m streamlit run main.py
```

---
# Nutzerinformationen für Huber, Heyer und Schmirander:

Julian Huber: Benutzername: huber; Passwort: test123

Yannic Heyer: Benutzername: heyer; Passwort: test123

Yunus Schmirander: Benutzername: schmirander; Passwort: test123

## Funktionen

### Benutzerverwaltung
- Registrierung & Login
- Profil anzeigen und bearbeiten
- Profilbild (optional) hochladen
- Änderungen speichern

### EKG-Upload
- Hochladen von `.txt`-Dateien
- Automatische Speicherung mit Datumsangabe
- Unterstützung mehrerer EKG-Tests pro Benutzer

### Analysefunktionen
- Visualisierung des EKG-Signals
- Interaktive Zeitbereichsauswahl (Slider)
- Erkennung von Herzschlägen (Peaks)
- Berechnung der Herzfrequenz
- Gleitender Durchschnitt zur Glättung

### Anomalieerkennung
- Benutzerdefinierbare Grenzwerte:
  - Tachykardie-Schwelle (z. B. > 100 bpm)
  - Bradykardie-Schwelle (z. B. < 60 bpm)
- Anzeige auffälliger Herzfrequenzwerte

### Weitere Features
- Plotly-Visualisierung für interaktive Diagramme
- Darstellung der berechneten Herzfrequenz als Tabelle
- Fortschrittlicher Filter für sichtbare EKG-Intervalle

---

## Projektstruktur (wichtigste Ordner)

```
PUE_Abschlussprojekt_GruppeA/
├── main.py
├── data/
│   ├── ekg_data/         # Hochgeladene EKG-Dateien (.txt)
│   ├── pictures/         # Profilbilder
│   └── users.json        # Benutzer-DB (TinyDB)
├── Src/
│   ├── ekg_data.py       # EKG-Datenklasse
│   ├── find_peaks.py     # Peak-Erkennung
│   ├── analyze_hr_data.py
│   ├── user_db.py
│   └── ...
```

---

## Beispiel-Benutzer

**Benutzername:** `testuser`  
**Passwort:** `1234` *(wenn definiert)*
