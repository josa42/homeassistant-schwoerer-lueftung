# WRG 134 BP HK: device description and technical data

File: [schwoerer-wrg-134-bp-hk-geraetebeschreibung.pdf](schwoerer-wrg-134-bp-hk-geraetebeschreibung.pdf)

| | |
|---|---|
| Title | Bedienungsanleitung für Lüftungsgeräte mit Wärmepumpe, pages 4 and 5 (sections 1 "Gerätebeschreibung" and 2 "Technische Daten") |
| Publisher | Schwörer Haus KG |
| Document | "Bedienung und Wartung WRG 134 BP HK, 134 BP SH", May 2016 (from the PDF metadata) |
| PDF created | 14.06.2017 |
| Pages | 2 (an extract of the manual) |
| Source | Copy from the owner's house documents. It is not published online; how it was obtained is not recorded. |
| SHA-256 | `06676056e9cc9b386e9bb09e5a832ae3daf6e99627fdc28f5a5dfeca400e6155` |

## Summary

The manufacturer's own description of how the unit works, and its technical
data.

- **Air path in heating mode:** exhaust and outdoor air pass each other in the
  counterflow heat exchanger. A small heat pump then heats the pre-warmed fresh
  air further: the evaporator takes heat from the exhaust air, and the condenser
  gives it to "die im Wärmetauscher (9) vorgewärmte Frischluft". This agrees
  with the [DIBt approval](dibt-z-51.4-390-2023.md).
- **Cooling mode (WRG 134 BP HK only):** the circuit is reversed. The coil in
  the supply air then works as evaporator and cools the supply air, and the coil
  in the exhaust air works as condenser and gives the heat to the outgoing air.
  The Modbus names T7 Verdampfer and T8 Kondensator therefore describe the
  heating mode.
- **Numbered parts (drawing):** 1 Zuluft, 2 Außenluft, 3 Abluft, 4 Fortluft,
  5 supply fan, 6 exhaust fan, 7 outdoor filter, 8 exhaust filter,
  9 counterflow heat exchanger, 10 evaporator, 11 condenser, 12 compressor,
  13 condensate drain, 14 control board, 18 bypass damper with actuator,
  19 bypass filter.
- **Technical data:**
  - Air flow 90 to 300 m³/h depending on version, 4 levels.
  - Heat exchanger efficiency above 80 %.
  - Compressor Danfoss SC 10, SC 15 or SC 18; refrigerant R134a.
  - Heating output up to 2.0, 2.5 or 2.8 kW including the heat exchanger.
  - Cooling output up to 620, 910 or 1080 W, measured at 0 °C evaporation
    temperature.
  - Defrosting starts at an evaporation temperature of -9 °C.
  - 230 V, at most 630 W, 37 dB(A) at 1 m, 105 kg.
  - Operating range -20 °C to +35 °C outdoor air.
- **Bypass:** a damper with an actuator. [registers.md](../registers.md)
  covers what this means for control over Modbus.
