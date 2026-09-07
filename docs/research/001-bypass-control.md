# Bypass control

Can the heat exchanger bypass be commanded over Modbus, and does running the
unit in Handbetrieb prevent it from opening?

No and probably not. There is no write register for the bypass on any known
firmware, and the damper is driven by the controller alone. What can be reached
over Modbus are the two conditions the controller evaluates, so the bypass can
be steered indirectly. The belief that Handbetrieb blocks it rests on an
observation that has a simpler explanation.

Investigated 2026-09-07 against a WGT, no ground heat exchanger, 6 rooms.

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
function would need. The firmware opens the damper when outside air is warmer
than the exhaust air and heat is wanted, so the logic is not gated on
Sommerbetrieb in the way the summer marketing suggests.

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
Handbetrieb, is equally well explained by the weather, and no test that
separates the two has been run yet.

## What would settle it

Set 100 to Sommerbetrieb on an evening when 209 is below 204, hold a room
setpoint under its current temperature, and watch 123. That is one register
write and it distinguishes the two explanations. Repeating it with 100 left at
Handbetrieb answers whether the Betriebsart matters at all.

Finding a command register, if one exists, needs a differential capture:
the full 0–1023 map with the bypass shut and again with it open, then a diff.
Registers 122 and 132 are the closest neighbours of the two damper states and
both read 1 while their documented partners read 0, which makes them the first
things to look at. A writability probe that reads a register and writes the
same value back would map the writable surface without changing any setting,
though a register whose read and write meanings differ would not be safe under
it.

## Not established

Other manufacturers gate the bypass with a lower limit on the outdoor
temperature, so that it will not pull in cold night air. Whether the WGT has
such a limit, and whether it is reachable over Modbus, is unknown. The figures
that turn up in web searches for this belong to Helios units and do not apply
here.

[wgt]: https://github.com/fgoettel/wgt/blob/main/wgt/lueftungsanlage.py
[gist]: https://gist.github.com/JavanXD/a3e8911e69f3a27a81eeeb80414bb6ab
[iobroker]: https://forum.iobroker.net/topic/36535/neuer-adapter-schwoerer-ventcube
[knx]: https://knx-user-forum.de/forum/öffentlicher-bereich/knx-eib-forum/diy-do-it-yourself/1822296-modbus-schwörer-heizung
[openhab]: https://openhabforum.de/viewtopic.php?t=8701
[brochure]: https://www.schwoererhaus.de/wp-content/uploads/BIC_WRG134BPHK.pdf
