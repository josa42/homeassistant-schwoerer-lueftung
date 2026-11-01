# DIBt Z-51.4-390: approval of the WRG 134 BP / BP-HK and WRG 334 / 334HK

File: [dibt-z-51.4-390-2023.pdf](dibt-z-51.4-390-2023.pdf)

| | |
|---|---|
| Title | Allgemeine bauaufsichtliche Zulassung / Allgemeine Bauartgenehmigung Nr. Z-51.4-390: Zentrale Lüftungsgeräte mit Wärmerückgewinnung und Luft/Luft-Wärmepumpe vom Typ "WRG 134 BP, WRG 134 BP-HK und WRG 334, WRG 334HK" |
| Issuer | Deutsches Institut für Bautechnik (DIBt), file number III 57-1.51.4-19/22 |
| Holder | Bau Info Center Lüftungstechnik, ein Unternehmensbereich der Schwörer Haus KG |
| Issued | 26.09.2023 |
| Valid until | 26.09.2028 |
| Pages | 20 (11 pages of text, 9 annexes) |
| Source | <https://www.dibt.de/pdf_storage/2023/Z-51.4-390(1.51.4-19!22).pdf> |
| Retrieved | 2026-10-31 |
| SHA-256 | `d9b5c4d8f524738910dc6e37e1d341c1073d0da86c68d5788d8648954dfe322f` |
| Predecessor | Z-51.4-390 of 31.07.2017, valid until 31.07.2022: <https://www.dibt.de/pdf_storage/2017/Z-51.4-390(1.51.4-45!11).pdf> |

The approval may only be reproduced in full (section I, item 5), which is why
the whole document is stored here.

## Summary

The official description of the unit's construction, written for the building
authorities. It is the only public, manufacturer-independent source found for
the order of the components in the air path.

- **Components (section 2.1):** supply and exhaust fan, a cross-counterflow
  plate heat exchanger of aluminium (500 x 325 x 275 mm, 76 channels per side),
  outdoor and exhaust filter, bypass, a heat pump placed after the heat
  exchanger, and the controller. Refrigerant R134a.
- **Air path:** "Durch die nachgeschaltete Wärmepumpe wird der den
  Wärmeübertrager verlassenden Abluft beim Durchströmen des Verdampfers nochmals
  Wärme entzogen und im Kondensator auf die im Wärmeübertrager bereits
  vorgewärmte Zuluft übertragen." The evaporator sits in the exhaust air after
  the heat exchanger, the condenser in the supply air after the heat exchanger.
- **HK variants:** the WRG 134 BP-HK and WRG 334HK can reverse the refrigerant
  circuit to cool in summer.
- **Pre-heater and frost protection:** the WRG 134 BP needs an electric
  pre-heater of 1500 W installed on site. The controller switches it "über einen
  im Ablufttrakt des Wärmeübertragers angeordneten Temperaturfühler", which
  measures the exhaust air temperature; at 0 °C the pre-heater switches on. The
  lowest outdoor temperature is -15 °C. This matches T6 "im WT" in the Modbus
  list ([parameter list](schwoerer-modbus-tcp-parameterliste-2020-03.md)).
- **Heat exchanger:** mean supply-side temperature ratio of 0.81 (annex 9).
- **Annex 5, "Schema - Luftführung":** drawing of the air path through the
  WRG 134 BP / BP-HK and the WRG 334 / 334HK. It shows the ducts, not the
  temperature sensors.
- **Annexes 6 to 9:** fan curves and the energy figures for the
  Gebäudeenergiegesetz (GEG), including COP and heating output of the heat pump
  with the heat exchanger upstream.

## Used for

- Order of heat exchanger, evaporator and condenser in the air path.
- Position of T6 on the exhaust side of the heat exchanger.
- Plausibility checks of the temperatures with the 0.81 temperature ratio.

The positions of T3 ("vor NE") and T4 ("nach NE") relative to the condenser
are not in this document. They follow from the device's own readings on
31.10.2026, with the after-heater off throughout
(`binary_sensor.technik_wgt_nhr_zustand`):

| | 10:43 (heat pump off) | 10:55 (heat pump on since 10:43:29) |
|---|---:|---:|
| T3 vor NE | 19.3 | 19.7 |
| T8 Kondensator | 18.4 | 46.0 |
| T4 nach NE | 18.0 | 44.1 |
| T6 im WT | 12.2 | 12.5 |
| T7 Verdampfer | 14.2 | -1.1 |

T3 and T6 do not react to the heat pump, while T4 follows the condenser and
T7 the evaporator. So T3 sits between the heat exchanger and the condenser,
T4 after the condenser and the after-heater, and T6 between the heat exchanger
and the evaporator. With the heat pump off (10:41, T2 10.0, T5 21.5), the 0.81
temperature ratio predicts 10.0 + 0.81 x 11.5 = 19.3 after the heat exchanger
on the supply side (T3 measured 19.3) and 21.5 - 0.81 x 11.5 = 12.2 on the
exhaust side (T6 measured 12.0 to 12.2).
