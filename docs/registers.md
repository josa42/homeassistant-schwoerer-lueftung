# Official Modbus Register Documentation

**Source:** Schwörer Haus KG Official Modbus TCP Documentation  
**Document Date:** 31.03.2020  
**Firmware Versions:**  
- Leistungsteil (Power Unit): V02.25  
- Bedienteil (Control Unit): V01.10

**Minimum Required Versions:**
- Leistungsteil: V02.11
- Bedienteil: V01.05

---

## Connection Information

- **Protocol:** Modbus TCP
- **Port:** 502
- **Data Type:** Word (16-bit signed)
- **Read Function:** Function Code 03 (Read Holding Registers)
- **Write Function:** Function Code 16 (Write Multiple Registers)
- **Activation:** Must be enabled via: Settings → Basic Settings → Network → Modbus TCP

---

## Register Map

### Operation Mode & Fan Control (100-145)

| Register | Read | Write | Function | Values | Notes |
|----------|------|-------|----------|--------|-------|
| 100 | ✅ | ✅ | Betriebsart (Operation Mode) | 0=Aus (Off)<br>1=Handbetrieb (Manual)<br>2=Winterbetrieb (Winter)<br>3=Sommerbetrieb (Summer)<br>4=Sommer Abluft (Summer Exhaust) | |
| 101 | ✅ | ✅ | Manuelle Luftstufe (Manual Fan Level) | 0=Aus (Off)<br>1=Stufe 1 (Level 1)<br>2=Stufe 2 (Level 2)<br>3=Stufe 3 (Level 3)<br>4=Stufe 4 (Level 4)<br>5=Automatik (Auto) *<br>6=Linearbetrieb (Linear) | *Optional |
| 102 | ✅ | ❌ | Aktuelle Luftstufe (Current Fan Level) | 0=Aus<br>1=Stufe 1<br>2=Stufe 2<br>3=Stufe 3<br>4=Stufe 4 | Read-only |
| 103 | ✅ | ✅ | Manuelle Lineare Luftleistung (Manual Linear Air Performance) | 30-100% | |
| 104 | ✅ | ❌ | Luftstufen Überschreibung (Fan Level Override) | 0=Inaktiv (Inactive)<br>1=Aktiv (Active) | Read-only |
| 110 | ✅ | ❌ | Zeitprogramm Basis Luftstufe (Time Program Base Level) | 0=Aus<br>1-4=Stufe 1-4 | Read-only |
| 111 | ✅ | ✅ | Stoßlüftung (Shock Ventilation) | 0=Inaktiv<br>1=Aktiv | |
| 112 | ✅ | ❌ | Restlaufzeit Stoßlüftung (Remaining Time Shock Vent) | 0-60 minutes | Read-only |
| 114 | ✅ | ❌ | Status Wärmepumpe (Heat Pump Status) | 0=Aus (Off)<br>5=WP Heizen (Heating)<br>49=WP Kühlen (Cooling) | Read-only |
| 116 | ✅ | ❌ | NHR Zustand (After-Heater State) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 117 | ✅ | ❌ | Status Gebläse Zuluft (Supply Fan Status) | 0=Deaktiviert (Disabled)<br>1=Anlaufphase (Startup)<br>2=Aktiv (Active)<br>5=Standby<br>6=Fehler (Error) | Read-only |
| 118 | ✅ | ❌ | Status Gebläse Abluft (Exhaust Fan Status) | 0=Deaktiviert<br>1=Anlaufphase<br>2=Aktiv<br>5=Standby<br>6=Fehler | Read-only |
| 121 | ✅ | ❌ | EWT Zustand (Ground Heat Exchanger State) | 0=EWT aus/geschlossen (Off/Closed)<br>1=EWT Heizbetrieb (Heating)<br>2=EWT Kühlbetrieb (Cooling) | Read-only |
| 123 | ✅ | ❌ | Bypass Zustand (Bypass State) | 0=Bypass geschlossen (Closed)<br>1=Bypass offen Kühlen (Open Cooling)<br>2=Bypass offen Heizen (Open Heating) | Read-only |
| 131 | ✅ | ❌ | Aussenklappe Zustand (Outdoor Damper State) | 0=geschlossen (Closed)<br>1=offen (Open) | Read-only |
| 133 | ✅ | ❌ | Vorheizregister Zustand (Pre-Heater State) | 0=Aus (Off)<br>1=VHR 1 aktiv<br>2=VHR 2 aktiv<br>3=VHR 1 & 2 aktiv | Read-only |
| 140 | ✅ | ❌ | Luftstufe Zeitprogramm (Fan Level Time Program) | 0=Aus<br>1-4=Stufe 1-4 | Read-only |
| 141 | ✅ | ❌ | Luftstufe Sensoren (Fan Level Sensors) | 0=Aus<br>1-4=Stufe 1-4 | Read-only, Optional |
| 142 | ✅ | ❌ | Luftleistung aktuell Zuluft (Current Supply Air Performance) | 0-100% | Read-only |
| 143 | ✅ | ❌ | Luftleistung aktuell Abluft (Current Exhaust Air Performance) | 0-100% | Read-only |
| 144 | ✅ | ❌ | Aktuelle Drehzahl Zuluft (Current Supply Fan RPM) | 0-10000 rpm | Read-only |
| 145 | ✅ | ❌ | Aktuelle Drehzahl Abluft (Current Exhaust Fan RPM) | 0-10000 rpm | Read-only |

---

### Temperature Sensors (200-209)

| Register | Read | Write | Function | Range | Notes |
|----------|------|-------|----------|-------|-------|
| 200 | ✅ | ❌ | T1 nach EWT (After Ground Heat Exchanger) | -50 to +100°C / 10 | Read-only |
| 201 | ✅ | ❌ | T2 nach VHR (After Pre-Heater) | -50 to +100°C / 10 | Read-only |
| 202 | ✅ | ❌ | T3 vor NE (Before After-Heater) | -50 to +100°C / 10 | Read-only |
| 203 | ✅ | ❌ | T4 nach NE (After After-Heater) | -50 to +100°C / 10 | Read-only |
| 204 | ✅ | ❌ | T5 Abluft (Exhaust Air) | -50 to +100°C / 10 | Read-only |
| 205 | ✅ | ❌ | T6 im WT (In Heat Exchanger) | -50 to +100°C / 10 | Read-only |
| 206 | ✅ | ❌ | T7 Verdampfer (Evaporator) | -50 to +100°C / 10 | Read-only |
| 207 | ✅ | ❌ | T8 Kondensator (Condenser) | -50 to +100°C / 10 | Read-only |
| 209 | ✅ | ❌ | T10 Aussen (Outdoor) | -50 to +100°C / 10 | Read-only |

**Note:** Temperature values are in Celsius × 10 (e.g., 201 = 20.1°C)

---

### Heating/Cooling Control (230-234)

| Register | Read | Write | Function | Values | Notes |
|----------|------|-------|----------|--------|-------|
| 230 | ✅ | ✅ | Heiz-Kühlfunktion (Heat/Cool Function) | 0=Aus (Off)<br>1=Heizen (Heating)<br>2=Kühlen (Cooling)<br>3=Auto T-Aussen (Auto Outdoor Temp)<br>4=Auto Digitaler Eingang (Auto Digital Input) | |
| 231 | ✅ | ✅ | Wärmepumpe Heizen (Heat Pump Heating) | 0=Heizen Aus (Off)<br>1=Heizen frei (Enabled) | |
| 232 | ✅ | ✅ | Wärmepumpe Kühlen (Heat Pump Cooling) | 0=Kühlen Aus (Off)<br>1=Kühlen frei (Enabled) | |
| 234 | ✅ | ✅ | Zusatzheizung Haus (Auxiliary House Heating) | 0=Aus (Off)<br>1=ZH Haus frei (Enabled) | |

---

### Error & Status Messages (240-254)

| Register | Read | Write | Function | Values | Notes |
|----------|------|-------|----------|--------|-------|
| 240 | ✅ | ❌ | Fehlermeldung (Error Message) | See Error Codes below | Read-only |
| 242 | ✅ | ❌ | Meldung Druckwächter Aktiv (Pressure Switch Active) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 243 | ✅ | ❌ | EVU Sperre Aktiv (Utility Company Lock Active) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 244 | ✅ | ❌ | Tür offen (Door Open) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 245 | ✅ | ❌ | Gerätefilter verschmutzt (Device Filter Dirty) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 246 | ✅ | ❌ | Vorgelagerter Filter verschmutzt (Pre-Filter Dirty) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 247 | ✅ | ❌ | Niedertarif abgeschaltet (Low Tariff Disabled) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 248 | ✅ | ❌ | Versorgungsspannung abgeschaltet (Supply Voltage Off) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 250 | ✅ | ❌ | Pressostat ausgelöst (Pressure Switch Triggered) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 251 | ✅ | ❌ | EVU Sperre extern Aktiv (External Utility Lock) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 252 | ✅ | ❌ | Heizmodul Testbetrieb aktiv (Heating Module Test Active) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 253 | ✅ | ❌ | Notbetrieb aktiv (Emergency Mode Active) | 0=inaktiv<br>1=Meldung steht an | Read-only |
| 254 | ✅ | ❌ | Zuluft zu kalt (Supply Air Too Cold) | 0=inaktiv<br>1=Meldung steht an | Read-only |

---

### Filter Maintenance (263-265)

| Register | Read | Write | Function | Range | Notes |
|----------|------|-------|----------|-------|-------|
| 263 | ✅ | ❌ | Restlaufzeit Vorgelagerter Filter (Pre-Filter Remaining Days) | 0-255 days | Read-only |
| 265 | ✅ | ❌ | Restlaufzeit Gerätefilter (Device Filter Remaining Days) | 0-255 days | Read-only |

---

### Room Temperature Actual Values (360-376)

| Register | Read | Write | Function | Range | Notes |
|----------|------|-------|----------|-------|-------|
| 360 | ✅ | ❌ | Ist Temp Raum 1 (Room 1 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 361 | ✅ | ❌ | Ist Temp Raum 2 (Room 2 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 362 | ✅ | ❌ | Ist Temp Raum 3 (Room 3 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 363 | ✅ | ❌ | Ist Temp Raum 4 (Room 4 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 364 | ✅ | ❌ | Ist Temp Raum 5 (Room 5 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 365 | ✅ | ❌ | Ist Temp Raum 6 (Room 6 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 366 | ✅ | ❌ | Ist Temp Raum 7 (Room 7 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 367 | ✅ | ❌ | Ist Temp Raum 8 (Room 8 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 368 | ✅ | ❌ | Ist Temp Raum 9 (Room 9 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 369 | ✅ | ❌ | Ist Temp Raum 10 (Room 10 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 370 | ✅ | ❌ | Ist Temp Raum 11 (Room 11 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 371 | ✅ | ❌ | Ist Temp Raum 12 (Room 12 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 372 | ✅ | ❌ | Ist Temp Raum 13 (Room 13 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 373 | ✅ | ❌ | Ist Temp Raum 14 (Room 14 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 374 | ✅ | ❌ | Ist Temp Raum 15 (Room 15 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 375 | ✅ | ❌ | Ist Temp Raum 16 (Room 16 Actual Temp) | -50 to +100°C / 10 | Read-only |
| 376 | ✅ | ❌ | Ist Temp Raum 17 (Room 17 Actual Temp) | -50 to +100°C / 10 | Read-only |

---

### Room Temperature Setpoints (400-416)

| Register | Read | Write | Function | Range | Notes |
|----------|------|-------|----------|-------|-------|
| 400 | ✅ | ✅ | Soll Temp Raum 1 (Room 1 Target Temp) | 10-30°C / 10 | |
| 401 | ✅ | ✅ | Soll Temp Raum 2 (Room 2 Target Temp) | 10-30°C / 10 | |
| 402 | ✅ | ✅ | Soll Temp Raum 3 (Room 3 Target Temp) | 10-30°C / 10 | |
| 403 | ✅ | ✅ | Soll Temp Raum 4 (Room 4 Target Temp) | 10-30°C / 10 | |
| 404 | ✅ | ✅ | Soll Temp Raum 5 (Room 5 Target Temp) | 10-30°C / 10 | |
| 405 | ✅ | ✅ | Soll Temp Raum 6 (Room 6 Target Temp) | 10-30°C / 10 | |
| 406 | ✅ | ✅ | Soll Temp Raum 7 (Room 7 Target Temp) | 10-30°C / 10 | |
| 407 | ✅ | ✅ | Soll Temp Raum 8 (Room 8 Target Temp) | 10-30°C / 10 | |
| 408 | ✅ | ✅ | Soll Temp Raum 9 (Room 9 Target Temp) | 10-30°C / 10 | |
| 409 | ✅ | ✅ | Soll Temp Raum 10 (Room 10 Target Temp) | 10-30°C / 10 | |
| 410 | ✅ | ✅ | Soll Temp Raum 11 (Room 11 Target Temp) | 10-30°C / 10 | |
| 411 | ✅ | ✅ | Soll Temp Raum 12 (Room 12 Target Temp) | 10-30°C / 10 | |
| 412 | ✅ | ✅ | Soll Temp Raum 13 (Room 13 Target Temp) | 10-30°C / 10 | |
| 413 | ✅ | ✅ | Soll Temp Raum 14 (Room 14 Target Temp) | 10-30°C / 10 | |
| 414 | ✅ | ✅ | Soll Temp Raum 15 (Room 15 Target Temp) | 10-30°C / 10 | |
| 415 | ✅ | ✅ | Soll Temp Raum 16 (Room 16 Target Temp) | 10-30°C / 10 | |
| 416 | ✅ | ✅ | Soll Temp Raum 17 (Room 17 Target Temp) | 10-30°C / 10 | |

---

### Room Base Temperature (420-436)

| Register | Read | Write | Function | Range | Notes |
|----------|------|-------|----------|-------|-------|
| 420 | ✅ | ✅ | Grundtemperatur Raum 1 (Room 1 Base Temp) | 10-30°C / 10 | |
| 421 | ✅ | ✅ | Grundtemperatur Raum 2 (Room 2 Base Temp) | 10-30°C / 10 | |
| 422 | ✅ | ✅ | Grundtemperatur Raum 3 (Room 3 Base Temp) | 10-30°C / 10 | |
| 423 | ✅ | ✅ | Grundtemperatur Raum 4 (Room 4 Base Temp) | 10-30°C / 10 | |
| 424 | ✅ | ✅ | Grundtemperatur Raum 5 (Room 5 Base Temp) | 10-30°C / 10 | |
| 425 | ✅ | ✅ | Grundtemperatur Raum 6 (Room 6 Base Temp) | 10-30°C / 10 | |
| 426 | ✅ | ✅ | Grundtemperatur Raum 7 (Room 7 Base Temp) | 10-30°C / 10 | |
| 427 | ✅ | ✅ | Grundtemperatur Raum 8 (Room 8 Base Temp) | 10-30°C / 10 | |
| 428 | ✅ | ✅ | Grundtemperatur Raum 9 (Room 9 Base Temp) | 10-30°C / 10 | |
| 429 | ✅ | ✅ | Grundtemperatur Raum 10 (Room 10 Base Temp) | 10-30°C / 10 | |
| 430 | ✅ | ✅ | Grundtemperatur Raum 11 (Room 11 Base Temp) | 10-30°C / 10 | |
| 431 | ✅ | ✅ | Grundtemperatur Raum 12 (Room 12 Base Temp) | 10-30°C / 10 | |
| 432 | ✅ | ✅ | Grundtemperatur Raum 13 (Room 13 Base Temp) | 10-30°C / 10 | |
| 433 | ✅ | ✅ | Grundtemperatur Raum 14 (Room 14 Base Temp) | 10-30°C / 10 | |
| 434 | ✅ | ✅ | Grundtemperatur Raum 15 (Room 15 Base Temp) | 10-30°C / 10 | |
| 435 | ✅ | ✅ | Grundtemperatur Raum 16 (Room 16 Base Temp) | 10-30°C / 10 | |
| 436 | ✅ | ✅ | Grundtemperatur Raum 17 (Room 17 Base Temp) | 10-30°C / 10 | |

---

### Auxiliary Heating Enable (440-456)

| Register | Read | Write | Function | Values | Notes |
|----------|------|-------|----------|--------|-------|
| 440 | ✅ | ✅ | Zusatzheizung Freigabe Raum 1 (Room 1 Aux Heat Enable) | 0=Gesperrt (Blocked)<br>1=Heizen frei (Enabled) | |
| 441 | ✅ | ✅ | Zusatzheizung Freigabe Raum 2 (Room 2 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 442 | ✅ | ✅ | Zusatzheizung Freigabe Raum 3 (Room 3 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 443 | ✅ | ✅ | Zusatzheizung Freigabe Raum 4 (Room 4 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 444 | ✅ | ✅ | Zusatzheizung Freigabe Raum 5 (Room 5 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 445 | ✅ | ✅ | Zusatzheizung Freigabe Raum 6 (Room 6 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 446 | ✅ | ✅ | Zusatzheizung Freigabe Raum 7 (Room 7 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 447 | ✅ | ✅ | Zusatzheizung Freigabe Raum 8 (Room 8 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 448 | ✅ | ✅ | Zusatzheizung Freigabe Raum 9 (Room 9 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 449 | ✅ | ✅ | Zusatzheizung Freigabe Raum 10 (Room 10 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 450 | ✅ | ✅ | Zusatzheizung Freigabe Raum 11 (Room 11 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 451 | ✅ | ✅ | Zusatzheizung Freigabe Raum 12 (Room 12 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 452 | ✅ | ✅ | Zusatzheizung Freigabe Raum 13 (Room 13 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 453 | ✅ | ✅ | Zusatzheizung Freigabe Raum 14 (Room 14 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 454 | ✅ | ✅ | Zusatzheizung Freigabe Raum 15 (Room 15 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 455 | ✅ | ✅ | Zusatzheizung Freigabe Raum 16 (Room 16 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |
| 456 | ✅ | ✅ | Zusatzheizung Freigabe Raum 17 (Room 17 Aux Heat Enable) | 0=Gesperrt<br>1=Heizen frei | |

---

### Auxiliary Heating Active Status (460-476)

| Register | Read | Write | Function | Values | Notes |
|----------|------|-------|----------|--------|-------|
| 460 | ✅ | ❌ | Zusatzheizung aktiv Raum 1 (Room 1 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 461 | ✅ | ❌ | Zusatzheizung aktiv Raum 2 (Room 2 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 462 | ✅ | ❌ | Zusatzheizung aktiv Raum 3 (Room 3 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 463 | ✅ | ❌ | Zusatzheizung aktiv Raum 4 (Room 4 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 464 | ✅ | ❌ | Zusatzheizung aktiv Raum 5 (Room 5 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 465 | ✅ | ❌ | Zusatzheizung aktiv Raum 6 (Room 6 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 466 | ✅ | ❌ | Zusatzheizung aktiv Raum 7 (Room 7 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 467 | ✅ | ❌ | Zusatzheizung aktiv Raum 8 (Room 8 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 468 | ✅ | ❌ | Zusatzheizung aktiv Raum 9 (Room 9 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 469 | ✅ | ❌ | Zusatzheizung aktiv Raum 10 (Room 10 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 470 | ✅ | ❌ | Zusatzheizung aktiv Raum 11 (Room 11 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 471 | ✅ | ❌ | Zusatzheizung aktiv Raum 12 (Room 12 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 472 | ✅ | ❌ | Zusatzheizung aktiv Raum 13 (Room 13 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 473 | ✅ | ❌ | Zusatzheizung aktiv Raum 14 (Room 14 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 474 | ✅ | ❌ | Zusatzheizung aktiv Raum 15 (Room 15 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 475 | ✅ | ❌ | Zusatzheizung aktiv Raum 16 (Room 16 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |
| 476 | ✅ | ❌ | Zusatzheizung aktiv Raum 17 (Room 17 Aux Heat Active) | 0=Inaktiv<br>1=Aktiv | Read-only |

---

### Time Program Heating Enable (500-516)

| Register | Read | Write | Function | Values | Notes |
|----------|------|-------|----------|--------|-------|
| 500 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 1 (Room 1 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 501 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 2 (Room 2 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 502 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 3 (Room 3 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 503 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 4 (Room 4 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 504 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 5 (Room 5 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 505 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 6 (Room 6 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 506 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 7 (Room 7 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 507 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 8 (Room 8 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 508 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 9 (Room 9 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 509 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 10 (Room 10 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 510 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 11 (Room 11 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 511 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 12 (Room 12 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 512 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 13 (Room 13 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 513 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 14 (Room 14 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 514 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 15 (Room 15 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 515 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 16 (Room 16 Time Program) | 0=Inaktiv<br>1=Aktiv | |
| 516 | ✅ | ✅ | Freigabe Zeitprogramm Heizen Raum 17 (Room 17 Time Program) | 0=Inaktiv<br>1=Aktiv | |

---

### Operating Hours Counters (800-813)

| Register | Read | Write | Function | Unit | Notes |
|----------|------|-------|----------|------|-------|
| 800 | ✅ | ❌ | Betriebsstunden Lüfter (Fan Operating Hours) | Hours | Read-only |
| 801 | ✅ | ❌ | Betriebsstunden Lüfter Stufe 1 (Fan Level 1 Hours) | Hours | Read-only |
| 802 | ✅ | ❌ | Betriebsstunden Lüfter Stufe 2 (Fan Level 2 Hours) | Hours | Read-only |
| 803 | ✅ | ❌ | Betriebsstunden Lüfter Stufe 3 (Fan Level 3 Hours) | Hours | Read-only |
| 804 | ✅ | ❌ | Betriebsstunden Lüfter Stufe 4 (Fan Level 4 Hours) | Hours | Read-only |
| 805 | ✅ | ❌ | Betriebsstunden WP (Heat Pump Operating Hours) | Hours | Read-only |
| 806 | ✅ | ❌ | Betriebsstunden WP kühlen (Heat Pump Cooling Hours) | Hours | Read-only |
| 809 | ✅ | ❌ | Betriebsstunden VHR (Pre-Heater Operating Hours) | Hours | Read-only |
| 810 | ✅ | ❌ | Betriebsstunden ZH Raum (Room Aux Heating Hours) | Hours | Read-only |
| 813 | ✅ | ❌ | Betriebsstunden EWT (Ground Heat Exchanger Hours) | Hours | Read-only |

<br><br>

## Error Codes (Register 240)

| Code | Error Message |
|------|---------------|
| 0 | Kein Fehler (No Error) |
| 257 | Drehzahl Zuluft fehlt (Supply Fan RPM Missing) |
| 258 | Drehzahl Abluft fehlt (Exhaust Fan RPM Missing) |
| 259 | Ventilator Zuluft Mindestdrehzahl nicht erreicht (Supply Fan Min RPM Not Reached) |
| 260 | Ventilator Abluft Mindestdrehzahl nicht erreicht (Exhaust Fan Min RPM Not Reached) |
| 261 | Ventilator Zuluft max. Drehzahl überschritten (Supply Fan Max RPM Exceeded) |
| 262 | Ventilator Abluft max. Drehzahl überschritten (Exhaust Fan Max RPM Exceeded) |
| 513 | Kommunikationsfehler zur BDE (Communication Error to Control Panel) |
| 514 | Kommunikationsfehler Nebenbedieneinheit (Communication Error Secondary Control) |
| 515 | Kommunikationsfehler Heizmodul (Communication Error Heating Module) |
| 516 | Kommunikationsfehler Sensor (Communication Error Sensor) |
| 517 | Kommunikationsfehler Sensor-Adapter (Communication Error Sensor Adapter) |
| 518 | Kommunikation Empfänger (Communication Receiver) |
| 770 | Fehler Sensorelement T1-nach-EWT (Sensor Error T1 After GHE) |
| 771 | Fehler Sensorelement T2-nach Vhr (Sensor Error T2 After Pre-Heater) |
| 772 | Fehler Sensorelement T3-vorNhr (Sensor Error T3 Before After-Heater) |
| 773 | Fehler Sensorelement T4-nachNhr (Sensor Error T4 After After-Heater) |
| 774 | Fehler Sensorelement T5-Abluft (Sensor Error T5 Exhaust) |
| 775 | Fehler Sensorelement T6-imWT (Sensor Error T6 In Heat Exchanger) |
| 776 | Fehler Sensorelement T7-Verdampfer (Sensor Error T7 Evaporator) |
| 777 | Fehler Sensorelement T8-Kondensator (Sensor Error T8 Condenser) |
| 779 | Fehler Sensorelement T10-Außentemperatur (Sensor Error T10 Outdoor) |
| 1025 | Fehler Parameterspeicher (Parameter Memory Error) |
| 1026 | Fehler System-Bus (System Bus Error) |
| 1281 | Wärmepumpe Hochdruck (Heat Pump High Pressure) |
| 1282 | Wärmepumpe Niederdruck (Heat Pump Low Pressure) |
| 1283 | Maximale Abtauzeit überschritten (Max Defrost Time Exceeded) |
| 1284 | Wärmepumpe Niederdruck im Kühlbetrieb (Heat Pump Low Pressure in Cooling) |

<br><br>

## Important Notes

### Warranty Disclaimer

This interface (physical port X29 on the main board) is **NOT** an officially approved interface by the manufacturer.

- SchwörerHaus KG and BIC assume **NO warranty** for:
  - Changes caused by software updates
  - Changes caused by hardware modifications
  - Downstream systems or components
  
- **Operator is responsible** for:
  - Incorrect operation via this interface
  - Any damage or issues caused by using this interface

- **No support provided** by SchwörerHaus or BIC for this interface

- **Use at your own risk**

### Temperature Values

All temperature values are transmitted as **°C × 10**

Examples:
- Value 201 = 20.1°C
- Value -50 = -5.0°C
- Value 373 = 37.3°C

### Optional Features

Some registers are marked as "Optional" and may not be available on all devices or firmware versions. Check device capabilities before implementation.

<br><br>

## Undocumented Registers

| Register | Observed Value | Notes                               |
|---------:|---------------:|-------------------------------------|
|      208 |            198 | Could be T9 (19.8°C)                |
|      320 |              9 |                                     |
|      321 |             14 | Matches register 209 (outdoor temp) |
|      322 |              7 |                                     |
|      323 |              1 |                                     |
|      324 |              5 |                                     | 
|      325 |              4 |                                     | 
|      343 |              1 |                                     | 
|      344 |              1 |                                     | 
|      345 |              1 |                                     | 
|      480 |              7 |                                     | 
|      481 |              3 |                                     | 
|      482 |              8 |                                     | 
|      483 |              8 |                                     | 
|      484 |              3 |                                     | 
|      485 |             11 |                                     | 

---

**Document Version:** 31.03.2020  
**Source:** SchwörerHaus KG Official Documentation  
**Community Research Added:** 2026-01-21  
**Integration:** homeassistant-schwoerer-lueftung
