# BIC WRG 134BP-HK product sheet (06/2006)

File: [bic-wrg-134-bp-hk-produktblatt-2006-06.pdf](bic-wrg-134-bp-hk-produktblatt-2006-06.pdf)

| | |
|---|---|
| Title | "Man nehme eine frische Brise: Das Lüftergerät mit Doppeleffekt" (BIC_WRG134HK_092006) |
| Publisher | Bau Info Center Lüftungstechnik, Hohenstein (part of Schwörer Haus KG) |
| Date | "Stand 06/2006"; PDF created 08.11.2006 |
| Models | WRG 134BP-HK (Art.-Nr. 52261), WRG 134BP-HKv (Art.-Nr. 52562) |
| Pages | 2 |
| Source | <https://www.schwoererhaus.de/wp-content/uploads/BIC_WRG134BPHK.pdf> (server date 25.06.2024) |
| Retrieved | 2026-11-01 |
| SHA-256 | `b9a4af034910e7c5bfb1d9b4d68db9305565588f1cf089dd88f95bb12e3ae627` |

## Summary

A marketing sheet for the heating and cooling variant. It is older than the
other references and some figures differ from the
[device description](schwoerer-wrg-134-bp-hk-geraetebeschreibung.md), so use
it for the overview and the drawing, not for exact values.

- **Concept:** ventilation unit with a counterflow heat exchanger and an
  integrated, reversible heat pump. Heating output about 2 kW in winter,
  cooling output up to 750 W in summer.
- **Drawing (page 2):** side and top view with numbered parts, the same
  numbering as the device description: 1 Zuluft, 2 Außenluft, 3 Abluft,
  4 Fortluft, 9 heat exchanger, 10 evaporator, 11 condenser, 12 compressor,
  19 bypass damper with actuator, 20 bypass filter, 21 not named in the legend.
- **Controller:** remote control panel, time programs, control of an additional
  heater or an external after-heater, air reduction on cold days, automatic
  summer bypass, external dampers, ground heat exchanger with booster fan,
  RS-232 connector. Modbus TCP is not mentioned; see the
  [parameter list](schwoerer-modbus-tcp-parameterliste-2020-03.md).
- **Technical data:**
  - Up to 250 m³/h, 330 m³/h with the stronger fans, at 100 Pa.
  - EC fans, about 12 W each at 111 m³/h and 49 W at 168 m³/h.
  - Heat exchanger heat recovery about 80 %.
  - Heat pump about 450 W input, R134a, reciprocating compressor.
  - About 99 kg, DN 140 connections.
- **Defrosting:** controlled by temperatures, with an electric pre-heater in
  the incoming air and an internal defrost of the heat pump by reversing the
  circuit.

The sheet does not describe the bypass as `außentemperaturgesteuert`, although
[registers.md](../registers.md) cites it for that word.
