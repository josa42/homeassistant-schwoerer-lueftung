# Bypass control

Can the heat exchanger bypass be commanded over Modbus, and does running the
unit in Handbetrieb prevent it from opening?

No, and Handbetrieb does not block it. There is no write register for the bypass
on any known firmware, and the damper is driven by the controller alone. What can
be reached over Modbus are the conditions the controller evaluates, so the bypass
can be steered indirectly. A week of recorder history, taken entirely in
Handbetrieb, has the damper opening and closing over a hundred times.

Investigated 2026-09-07 against a WGT, no ground heat exchanger, 6 rooms. The
measurements in `A week of the unit's own history` cover 2026-09-07 to
2026-09-14 on the same unit, all of it on the cooling side. The heating side of
the bypass is untouched by this document.

## The register is read-only, on paper and in practice

Register 123 carries a bypass state and nothing else. The 03/2020 parameter
list gives it no write address, and the three states it reports (`0` closed,
`1` open for cooling, `2` open for heating) are outputs, not commands.

No published project writes it. [fgoettel/wgt][wgt] declares `bypass` as a
property with a getter and no setter, while `betriebsart` and `heizen_kuehlen`
next to it have both. The [VentCube Home Assistant gist][gist] models it as a
sensor. The [ioBroker Ventcube adapter][iobroker] and the [KNX][knx] and
[openHAB][openhab] threads read it and never write it.

The 0–1023 probe in `undocumented-registers.md` found twelve undocumented
registers in 120–135, so an undocumented write path is not ruled out. Nothing
in that block is identified yet, and identifying one takes writes that were not
attempted.

## The damper is the controller's, by design

The BIC datasheet for the WRG 134 BP HK lists the bypass as
`Bypass-Klappe: außentemperaturgesteuert, im Gerät integriert`, with item 18 of
the exploded view being the `Bypass-Klappe mit Stellmotor`. The [product
brochure][brochure] describes the regulation as offering a `Sommerbypass als
integrierter, automatischer Bypass`.

So the damper has a servo the controller owns, and the product was never sold
with a manual override. That is consistent with the parameter list, and it is
the reason to expect a hunt for a hidden write register to come up empty.

## What actually opens it

SchwörerHaus states the condition directly:

> Die automatische Bypassfunktion schaltet sich ein, wenn die Außentemperatur
> geringer als die Raumisttemperatur und die Raumsolltemperatur niedriger
> eingestellt ist als die Isttemperatur.

Two conditions, both of which must hold:

| Condition | Registers |
| --- | --- |
| outdoor colder than the room | 209 < 360+n |
| room setpoint below the room temperature | 400+n < 360+n |

The second one is writable. The integration already exposes it as the climate
entity's target temperature. Dropping a room's setpoint below its current
temperature creates the cooling demand the controller is looking for, and while
it is cooler outside than inside, that is what opens the bypass. Raising the
setpoint closes it.

This is not bypass control. It is control of the input the bypass decision is
made from, which is as close as this interface gets.

## A week of the unit's own history

The Home Assistant recorder held 2026-09-07 to 2026-09-14 for this unit, which
covers over 100 damper transitions. `Heiz-Kühlfunktion` was Kühlen throughout,
the heat pump never ran, the fan sat on stage 2 apart from a few hours on 09-09,
and every room setpoint was 20 °C while the rooms ranged from 14.8 to 29.6 °C.

Betriebsart was Handbetrieb for the whole week and the damper was open for about
four fifths of it. That settles the question this document opened with: Handbetrieb
does not prevent the bypass from opening.

Everything below is the cooling side only. Register 230 sat on Kühlen throughout,
register 123 reported nothing but `0` closed and `1` open for cooling, and
`2` open for heating never appeared once. None of the thresholds measured here
say anything about what the damper does when the unit is asked to heat.

Reading this back needs one trick. A climate entity's state stays `fan_only`
forever, so `last_changed` is constant across its whole history and the room
temperature in `current_temperature` has to be keyed on `last_updated` instead.

### It switches on the difference, not on a fixed temperature

Three consecutive days closed as the outdoor temperature caught up with the
extract air, and reopened once it was about 2 K below again:

| | T10 outdoor | T5 extract | T5 - T10 |
| --- | --- | --- | --- |
| 09-12 13:14 closed | 24.1 | 24.2 | +0.1 K |
| 09-12 19:55 opened | 20.2 | 24.8 | +4.6 K |
| 09-13 17:17 closed | 23.4 | 24.0 | +0.6 K |
| 09-13 18:13 opened | 22.3 | 23.9 | +1.6 K |
| 09-14 14:57 closed | 25.6 | 25.3 | -0.3 K |
| 09-14 18:18 opened | 24.0 | 26.2 | +2.2 K |

So the closing edge sits where outdoor reaches indoor, the opening edge about
2 K below it, and the hysteresis between them is 1.5 to 2 K. Neither edge is
anywhere near a fixed absolute temperature: the same damper closed at 23.4 °C
outdoor on one day and stayed open at 24.0 °C on the next, because the indoor
temperature had moved with it.

### The 10 °C lower limit is real

Restricting the week to five-minute windows where the extract air was at least
3 K warmer than outdoor, so that the cooling condition was clearly satisfied,
leaves the outdoor temperature as the only thing that can explain the damper:

| T10 outdoor | Share of time open |
| --- | --- |
| 8 to 9 °C | 0 % |
| 9 to 10 °C | 17 % |
| 10 to 11 °C | 86 % |
| above 11 °C | 97 to 100 % |

The cut is sharp enough to see without a model. At the threshold the damper does
not settle, it pulses: 43 transitions in 98 minutes on 09-10 and 37 in 64
minutes on 09-11, all of them between 9.7 and 10.2 °C outdoor while the extract
air was at 24 °C.

10 °C is the factory default for the WRG-Temperatur lower limit in this family,
and the measurement lands on it. No register for that parameter is identified,
so whether it can be read or changed over Modbus is still open.

The obvious alternative, a minimum supply temperature rather than a minimum
outdoor temperature, does not hold up. T2 reads 4 K above T10 whether the damper
is open or shut, so it sits ahead of the exchanger and is not a controlled
variable.

### The room setpoint condition, seen once

On 09-10 the damper was open with 13 °C outdoor against 23.9 °C extract, a 7 K
cooling potential, and it closed at 08:56 anyway. What changed is that room 1
had been dropping under the cold supply air and crossed its own setpoint:

| Time | T10 outdoor | Room 1 | Setpoint | Bypass |
| --- | --- | --- | --- | --- |
| 08:45 | 13.1 | 22.6 | 20.0 | open |
| 09:00 | 13.3 | 18.7 | 20.0 | closed |
| 09:30 | 15.6 | 20.4 | 20.0 | closed |
| 09:40 | 16.5 | 21.1 | 20.0 | open |

That is the second of SchwörerHaus's two conditions doing exactly what it says,
and it is the one that is writable.

The condition is room 1's alone. Taking every five-minute window where the
outdoor side was clearly in favour of opening, meaning the extract air at least
3 K warmer than outdoor and outdoor above 11 °C, the damper was open 95 % of the
time. Splitting those windows by which room was under its setpoint separates room
1 from the rest:

| Under its setpoint | Windows | Bypass open |
| --- | --- | --- |
| Room 1, Wohnzimmer | 10 | 20 % |
| Kinderzimmer 1 | 267 | 97 % |
| Kinderzimmer 2 | 157 | 100 % |
| Schlafzimmer | 70 | 89 % |
| average of all six rooms | 31 | 94 % |

Kinderzimmer 1 spent a quarter of the week under its setpoint, down to 14.8 °C,
and the damper ignored it. Room 1 went under for 50 minutes and the damper
followed. Ten windows is a thin sample, but the contrast against rooms with
twenty times the data is not thin, and it rules out both the coldest room and the
average as the thing being compared.

### Heiz-Kühlfunktion gates it, the rest does not

Register 230 closes the damper the moment it leaves Kühlen. Switching it to
Heizen at 09-09 10:04 closed the bypass within seconds, and switching back 13
seconds later reopened it at 10:06, with the temperatures unchanged across both.

Betriebsart, the heat pump registers and the fan stage held still while the
damper switched over a hundred times, so none of them gate it.

### Where the rule and the damper disagree

Classifying every five-minute window of the week against the rule gives 77.3 %
agreement and 12.5 % disagreement, with 10.2 % inside the hysteresis band where
the rule deliberately predicts nothing. The disagreements are not spread evenly,
and most of them are not a defect in the rule.

Matching each of the 18 transitions to the nearest predicted one sorts them by
how fast the difference was crossing the threshold:

| Crossing | Transitions | Median timing error |
| --- | --- | --- |
| steep, 1 K/h or more | 11 | 14 min |
| flat, under 1 K/h | 7 | 160 min |

Where the difference moves through the threshold, the rule is right to within a
quarter hour. Where it crawls along the threshold for hours, the moment of
switching is not determined by any threshold rule at all: at 0.2 K/h, being
0.3 K off moves the switch by an hour and a half. 58 % of the disagreeing time
sits within 1 K of a threshold. All five transitions driven by the 10 °C limit
land within 22 minutes, so that limit is sharp and the difference condition is
the fuzzy one.

The remaining 8.7 hours sit clearly on the wrong side. An averaged outdoor
reading predicts their sign: while outdoor rises, an average trails below it and
holds the damper open too long; while outdoor falls, it holds it shut. Four of
the seven episodes longer than an hour carry that signature, including the two
largest, 09-08 morning at +2.1 K/h staying open 2.8 h too long and 09-12 evening
at -2.5 K/h staying shut 1.2 h. The other three have no outdoor trend to speak
of.

Smoothing T10 with a time constant of 90 to 120 minutes halves the disagreement,
12.5 % down to 6.1 %, and the optimum is real: longer constants get worse again.
But the same smoothing matches fewer transitions, 4 of 18 against 9 of 18 for
the raw reading. It mostly removes the model's own flip-flopping in flat
stretches instead of predicting the real moments. Averaging is supported, not
proven.

### The switching points, at full resolution

Read from raw recorder states rather than five-minute means, every value below
is at most 99 s old at the moment the damper moved:

| Time | | T10 | T5 | T5-T10 | Room 1 | What moved it |
| --- | --- | --- | --- | --- | --- | --- |
| 09-08 12:05 | shut | 30.7 | 26.9 | -3.80 | 26.0 | difference, 2.7 h late |
| 09-08 22:38 | open | 23.9 | 27.3 | +3.40 | 25.7 | difference, 2.6 h late |
| 09-09 10:04 | shut | 15.5 | 24.4 | +8.90 | 20.9 | register 230 set to Heizen |
| 09-10 01:08 | shut | 10.1 | 24.7 | +14.60 | 23.6 | 10 °C limit |
| 09-10 08:15 | open | 9.7 | 23.9 | +14.20 | 23.1 | 10 °C limit |
| 09-10 08:56 | shut | 13.0 | 24.0 | +11.00 | 18.6 | room 1 below its setpoint |
| 09-10 09:38 | open | 16.1 | 24.0 | +7.90 | 21.0 | room 1 back above it |
| 09-11 03:54 | shut | 10.2 | 24.0 | +13.80 | 23.2 | 10 °C limit |
| 09-11 07:22 | open | 9.6 | 23.3 | +13.70 | 22.5 | 10 °C limit |
| 09-11 16:14 | shut | 21.4 | 24.6 | **+3.20** | 22.9 | **unexplained** |
| 09-11 19:02 | open | 21.7 | 24.3 | +2.60 | 23.8 | difference |
| 09-11 20:10 | open | 17.5 | 23.7 | +6.20 | 21.0 | difference |
| 09-12 13:14 | shut | 24.1 | 24.2 | +0.10 | 23.2 | difference |
| 09-12 19:55 | open | 20.3 | 24.8 | +4.50 | 22.9 | difference, 1.2 h late |
| 09-13 17:17 | shut | 23.4 | 23.9 | +0.50 | 21.5 | difference |
| 09-13 18:13 | open | 22.2 | 23.9 | +1.70 | 22.8 | difference |
| 09-14 14:57 | shut | 25.5 | 25.3 | -0.20 | 24.8 | difference |
| 09-14 18:18 | open | 24.0 | 26.2 | +2.20 | 24.9 | difference |

Two things follow. The scatter is not a resolution artifact, because the raw
values scatter exactly as widely as the five-minute means did. And 09-11 16:14
breaks a pure hysteresis model: the damper shut at +3.2 K, above the +1.7 K and
+2.2 K at which it opened on other days. A damper that closes above its own
opening threshold is not answering to the difference alone.

Nothing else visible over Modbus moved at that moment. No mode or fan stage
change, the heat pump off, every room above its setpoint, and the only sensors
that moved were the ones the damper itself moves. Whatever closed it is either
not exposed on the bus or is not a temperature.

The four events near 10 °C are worth reading twice: it shut at 10.1 and 10.2 and
opened at 9.7 and 9.6. The release sits *below* the block, which no ordinary
hysteresis does. That is the pulsing, sampled at two arbitrary moments, and it
is why those four numbers bracket the limit rather than bounding it from one
side.

## Betriebsart is a season, not a fan mode

The premise that the bypass needs Sommerbetrieb, and that Sommerbetrieb costs
manual fan control, does not survive a look at the register map. Those are two
registers:

| Register | Meaning | Writable |
| --- | --- | --- |
| 100 | Betriebsart: off, Handbetrieb, Winter, Sommer, Sommer Abluft | yes |
| 101 | Manuelle Luftstufe: 0–4, 5 automatic, 6 linear | yes |

Setting 100 to Sommerbetrieb and 101 to a fixed stage asks for the summer
season logic and a fixed fan stage at the same time. Whether the unit honours
both is untested, but nothing in the parameter list couples them, and the
existence of a separate `Luftstufen Überschreibung` at 104 argues that the
effective stage is arbitrated between several sources rather than dictated by
the Betriebsart.

The bypass state also reports `2 = open (heating)`, which no summer-only
function would need. Presumably the firmware opens the damper when outside air is
warmer than the exhaust air and heat is wanted, which would mean the logic is not
gated on Sommerbetrieb in the way the summer marketing suggests. That reading
comes from the existence of the state and nothing else: the heating side has not
been observed.

## The unit at the time of investigation

Read-only single-register FC03 across 90–260, with the dev Home Assistant
stopped:

| Register | Value | Meaning |
| --- | --- | --- |
| 100 | 1 | Handbetrieb |
| 101 | 2 | manual stage 2 |
| 102 | 2 | current stage 2 |
| 123 | 0 | bypass closed |
| 204 | 26.7 °C | T5 exhaust |
| 209 | 30.7 °C | T10 outdoor |
| 230 | 2 | Heiz-Kühlfunktion: Kühlen |
| 231 | 0 | heat pump heating off |
| 232 | 0 | heat pump cooling off |

Outdoor was 4 K warmer than the exhaust air. The first of the two conditions
was false, so a correctly working bypass is closed here regardless of the
Betriebsart. The observation that started this, a bypass that stays shut in
Handbetrieb, was the weather: the week of history below has the same unit in the
same Betriebsart opening the damper as soon as it was cooler outside.

## What would settle it

Whether the Betriebsart matters is answered: it does not. The open questions are
narrower now. Which indoor temperature the controller compares against needs a
day where the rooms disagree, for instance one room forced well away from the
others, because right now they all move together. The 10 °C limit needs a
parameter register before it can be read or moved.

Finding a command register, if one exists, needs a differential capture:
the full 0–1023 map with the bypass shut and again with it open, then a diff.
Registers 122 and 132 are the closest neighbours of the two damper states and
both read 1 while their documented partners read 0, which makes them the first
things to look at. A writability probe that reads a register and writes the
same value back would map the writable surface without changing any setting,
though a register whose read and write meanings differ would not be safe under
it.

## Not established

The WGT does gate the bypass with a lower limit on the outdoor temperature, and
it measures as 10 °C, but no register for that parameter is identified, so it
can be neither read nor changed over Modbus today. The figures that turn up in
web searches for this belong to Helios units and do not apply here.

At least one input is missing. The 09-11 16:14 closing at +3.2 K cannot be
reconciled with the openings at +1.7 K and +2.2 K under any single-threshold
model, with or without hysteresis, damping, or a dwell time, and nothing else on
the bus moved with it. Until that input is identified, the rule is a good
description of the damper's behaviour and not its logic.

Which indoor temperature the outdoor temperature is compared against is
undecided. T5 extract, the average of the six rooms and each individual room all
fit the week within three percentage points of each other, because they move
together. Room 1 is the natural candidate, since the setpoint condition turned out
to be room 1's, but that is an inference and not a measurement. Separating them
needs a room driven well away from the rest.

Three explanations were tested against the week and failed. A minimum dwell time
is contradicted by the 33-second pulsing at the 10 °C limit, and adding one to
the model matches no more transitions. Swapping the reference from T5 extract to
room 1 moves the disagreement from 12.5 % to 12.3 %. A wider hysteresis band gets
the disagreement down to 2.2 %, but only by predicting nothing across 31 % of the
week, and it contradicts the three closings observed at a difference near zero;
the threshold error each episode would need is anywhere from -2.8 to +6.9 K, so
it is not one constant offset either.

The room setpoint condition rests on 50 minutes of room 1 being under its
setpoint. What happened there is unambiguous and the other rooms rule out the
alternatives, but a second episode would be worth having.

Whether the damper modulates or is strictly two-state is unresolved. Register 123
reports three discrete states, and the pulsing at the 10 °C threshold is
consistent with a two-state damper being cycled.

The heating side is entirely uninvestigated. Every measurement here was taken
with register 230 on Kühlen, in September, and `2 = open (heating)` never showed
up in the recorder at all. What conditions open the damper for heating, whether
the 10 °C outdoor limit applies to them, whether the comparison inverts to
outdoor warmer than the room, and which way the hysteresis points are all
unknown. The two automatic modes of register 230, Auto T-Aussen and Auto
Digitaler Eingang, are equally untested; the week touched them for 13 seconds.

Settling it needs a heating season, or a day cold enough that setting 230 to
Heizen with room 1's setpoint above its current temperature is a realistic
demand. Watching 123 for state 2 under those conditions is the test.

[wgt]: https://github.com/fgoettel/wgt/blob/main/wgt/lueftungsanlage.py
[gist]: https://gist.github.com/JavanXD/a3e8911e69f3a27a81eeeb80414bb6ab
[iobroker]: https://forum.iobroker.net/topic/36535/neuer-adapter-schwoerer-ventcube
[knx]: https://knx-user-forum.de/forum/öffentlicher-bereich/knx-eib-forum/diy-do-it-yourself/1822296-modbus-schwörer-heizung
[openhab]: https://openhabforum.de/viewtopic.php?t=8701
[brochure]: https://www.schwoererhaus.de/wp-content/uploads/BIC_WRG134BPHK.pdf
