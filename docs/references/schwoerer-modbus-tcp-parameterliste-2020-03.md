# SchwörerHaus Modbus TCP parameter list (03/2020)

File: [schwoerer-modbus-tcp-parameterliste-2020-03.pdf](schwoerer-modbus-tcp-parameterliste-2020-03.pdf)

| | |
|---|---|
| Title | Modbus TCP Schnittstelle (Parameterliste_Modbus_TCP_03.2020) |
| Publisher | SchwörerHaus KG, Hans-Schwörer-Straße 8, 72531 Hohenstein-Oberstetten |
| Date | 31.03.2020 |
| Firmware covered | Leistungsteil V02.25, Bedienteil V01.10 |
| Minimum firmware | Leistungsteil V02.11, Bedienteil V01.05 |
| Pages | 9 |
| Source | Copy from the owner's house documents. It is not published online; how it was obtained is not recorded. |
| SHA-256 | `96acce071b042f0b59df219fdc315b4cd601d9f407bd5ab551c3570b7ed5a522` |

## Summary

The register map this integration is built on.
[registers.md](../registers.md) is a transcription of it, with notes from
probing the device added.

- **Disclaimer:** the interface (connector X29 on the main board) is not
  officially released by the manufacturer. SchwörerHaus and BIC give no warranty
  and no support for it, and changes from firmware updates are not covered.
  Not every listed parameter may be implemented yet.
- **Activation:** on the control panel under Einstellungen → Grundeinstellungen
  → Netzwerk → Modbus TCP. Port 502.
- **Data type:** 16-bit signed word. Read with function 03 (Read Holding
  Registers), write with function 16 (Write Multiple Registers).
- **Contents (registers 100 to 813):** operating mode, air levels, boost
  ventilation, states of heat pump, after-heater (NHR), fans, ground heat
  exchanger, bypass, outdoor damper and pre-heater; air flow and fan speed;
  heating and cooling function; temperatures T1 to T10 (200 to 209, T9 not
  listed); room temperatures, setpoints and base temperatures; additional
  heating per room; filter run times; error and status messages, including a
  sensor error per temperature sensor (770 to 779).
- **Sensor names:** T1 nach EWT, T2 nach VHR, T3 vor NE, T4 nach NE, T5 Abluft,
  T6 im WT, T7 Verdampfer, T8 Kondensator, T10 Außen. The names say where each
  sensor sits but not in which order the components follow each other; for
  that see the [DIBt approval](dibt-z-51.4-390-2023.md).
