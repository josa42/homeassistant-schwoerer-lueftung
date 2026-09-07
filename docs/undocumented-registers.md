# Undocumented registers

The vendor datasheet (`registers.md`) documents 162 holding registers. A real
WGT implements **518**. This records what a probe of 0–1023 found, so the
findings are not lost and can be checked against another unit.

## Method

Single-register FC03 reads, one address at a time, 0–1023. Read-only: no write
of any kind was issued. Single reads rather than blocks because a failed *block*
read is ambiguous — it could span a gap or exceed a count limit — while a failed
single read is not: the address is not implemented.

The device answers **exception code 2 (Illegal Data Address)** for anything it
does not implement, which makes the probe unambiguous. That same strictness is
why the integration reads only contiguous runs of declared fields; see
[ADR 0002](adr/0002-contiguous-only-register-blocks.md).

Probed unit: WGT, no ground heat exchanger, 6 rooms, 2026-09-07.

## Confirmed

### 620–625 — real-time clock

Year, month, day, hour, minute, second. Read three times, three seconds apart,
tracking the wall clock:

```
device 2026-09-07 12:23:09   host 2026-09-07 12:23:11
device 2026-09-07 12:23:12   host 2026-09-07 12:23:14
device 2026-09-07 12:23:15   host 2026-09-07 12:23:17
```

Exposed as the `device_clock` diagnostic sensor, off by default.

### 208 — the missing T9

The datasheet numbers its sensors T1–T8 and T10, skipping 208. It is
implemented and reads a temperature sitting among its neighbours:

| Register | Value | Sensor |
| --- | --- | --- |
| 206 | 26.8 °C | T7 Verdampfer |
| 207 | 27.1 °C | T8 Kondensator |
| **208** | **25.9 °C** | **undocumented — almost certainly T9** |
| 209 | 29.8 °C | T10 Aussen |

Exposed as `temperature_t9`, off by default. What it measures is unknown.

## Strong candidate, unconfirmed

**Register 300 = 6**, on a unit with exactly 6 rooms configured. If that holds
across installations the config flow could detect the room count instead of
asking for it. Register 301 = 1. Needs a second unit with a different room
count before anything relies on it.

## Room-indexed blocks

Eight further 17-wide blocks share the shape of the known room registers — six
populated slots on a six-room unit, eleven zeros:

| Block | Rooms 1–6 | Known |
| --- | --- | --- |
| 320–336 | `9, 14, 7, 1, 5, 4` | no |
| 340–356 | `0, 0, 0, 1, 1, 1` | no |
| 360–376 | current temperature | **yes** |
| 380–396 | all zero | no |
| 400–416 | target temperature | **yes** |
| 420–436 | base temperature | **yes** |
| 440–456 | auxiliary heating enabled | **yes** |
| 460–476 | auxiliary heating active | **yes** |
| 480–496 | `8, 8, 8, 8, 8, 8` | no |
| 500–516 | scheduled heating enabled | **yes** |
| 520–536 | `8, 0, 0, 0, 0, 0` | no |
| 540–556, 560–576, 580–596 | all zero | no |

Identifying these means changing a setting on the unit and watching which
register moves. That is a write, so it was not attempted.

## Registers exist even without the hardware

The probed unit has **no ground heat exchanger**, yet all three of its registers
are implemented and read 0:

| Register | Meaning | Value |
| --- | --- | --- |
| 121 | EWT state | 0 |
| 200 | T1 after EWT | 0 |
| 813 | EWT operating hours | 0 |

This is the first evidence on a question the integration could not otherwise
answer: it suggests the firmware implements registers regardless of installed
hardware and returns 0, so a WRT would likely serve the heating registers too.

It is one unit, so the per-subsystem component split stays — but it is now an
informed hedge rather than a blind one.

## The gap that matters

Only **105–109** is missing from the 100–118 region; 113 and 115 are
implemented. That single hole is what made a block read of 100–112 fail.

## Every implemented run, 0–1023

| Range | Count | Documented | Undocumented | Values |
| --- | --- | --- | --- | --- |
| 100–104 | 5 | 5 | 0 | `[1, 2, 2, 50, 0]` |
| 110–118 | 9 | 7 | 2 | `[3, 0, 0, 3, 0, 0, 0, 2, 2]` |
| 120–135 | 16 | 4 | 12 | `[0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 138–147 | 10 | 6 | 4 | `[0, 2, 0, 2, 35, 35, 1095, 1095, 0, 0]` |
| 200–220 | 21 | 9 | 12 | `[0, 267, 268, 267, 264, 266, 267, 271, 259, 296, 0, 0, …]` |
| 228–232 | 5 | 3 | 2 | `[240, 1, 2, 0, 0]` |
| 234–238 | 5 | 1 | 4 | `[0, 0, 1, 0, 0]` |
| 240–255 | 16 | 13 | 3 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 260–266 | 7 | 2 | 5 | `[16, 0, 0, 26, 0, 40, 0]` |
| 270–280 | 11 | 0 | 11 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| 300–301 | 2 | 0 | 2 | `[6, 1]` |
| 320–336 | 17 | 0 | 17 | `[9, 14, 7, 1, 5, 4, 0, 0, 0, 0, 0, 0, …]` |
| 340–356 | 17 | 0 | 17 | `[0, 0, 0, 1, 1, 1, 0, 0, 0, 0, 0, 0, …]` |
| 360–376 | 17 | 17 | 0 | `[259, 255, 257, 243, 237, 228, 200, 200, 200, 200, 200, 200, …]` |
| 380–396 | 17 | 0 | 17 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 400–416 | 17 | 17 | 0 | `[200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, 200, …]` |
| 420–436 | 17 | 17 | 0 | `[200, 200, 200, 200, 200, 200, 210, 210, 210, 210, 210, 210, …]` |
| 440–456 | 17 | 17 | 0 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 460–476 | 17 | 17 | 0 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 480–496 | 17 | 0 | 17 | `[8, 8, 8, 8, 8, 8, 0, 0, 0, 0, 0, 0, …]` |
| 500–516 | 17 | 17 | 0 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 520–536 | 17 | 0 | 17 | `[8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 540–556 | 17 | 0 | 17 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 560–576 | 17 | 0 | 17 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 580–596 | 17 | 0 | 17 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 600–614 | 15 | 0 | 15 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 620–625 | 6 | 0 | 6 | `[2026, 9, 7, 12, 21, 32]` |
| 700–701 | 2 | 0 | 2 | `[0, 1]` |
| 720–729 | 10 | 0 | 10 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| 740–749 | 10 | 0 | 10 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| 760–769 | 10 | 0 | 10 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| 780–789 | 10 | 0 | 10 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| 800–815 | 16 | 10 | 6 | `[7950, 2397, 3388, 1918, 236, 1652, 24, 30, 0, 0, 890, 0, …]` |
| 880–889 | 10 | 0 | 10 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0]` |
| 900–979 | 80 | 0 | 80 | `[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, …]` |
| 1000–1003 | 4 | 0 | 4 | `[0, 0, 0, 0]` |
Nothing above 1003 was probed; the scan stopped at 1023.

Every register the integration declares was confirmed implemented — there are
no declared-but-missing addresses.
