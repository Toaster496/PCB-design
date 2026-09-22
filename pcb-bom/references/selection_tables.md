# Component selection starter tables

Conservative starting points — every part decision still gets its own datasheet check
(lifecycle, ratings, availability per SKILL.md §3). Provenance: these are
category-level guidance from distributor-standard families, not endorsements of
specific MPNs; where an MPN family is named it is as a recognizable example, verify
current status before design-in.

## §1 Passives starter kits (the ~10 values that cover 90% of designs)

**Resistors (1%, 0603 class unless noted):**
1.0, 4.7, 10, 22, 33, 47, 100, 1k, 4.7k, 10k, 22k, 47k, 100k, 1M — the E12-ish
core. Add exact divider values per circuit (0.1% only where a measurement rides on
it — voltage references, shunt amps).
- LED limiters: 330R–2k2 (aim ~5–10 mA modern LEDs)
- I2C pullups: 4.7k–10k (bus speed dependent: 2.2k–4.7k at 400 kHz class)
- Straps: 10k default (weak enough for boot changes, strong against noise)
- Gate pull-downs on half-bridges: 10k–100k ALWAYS (never let a gate float at
  power-up — both FETs half-on is a smoke condition)
- Current shunts: milliohm-class 1%/25 ppm parts (1206/2010 for power dissipation)

**Capacitors (X7R/NP0 mix, 0603/0805/1206):**
- Decoupling: 100n (every IC pin) + 10u/16V–25V (per cluster/rail)
- Bulk: 10u–100u electrolytic/polymer at rail entries; ≥2× rail voltage rating
- Crystal loads: NP0/C0G at the exact crystal-specified value (12–22p typical,
  C0G dielectric — stability matters here)
- Buck input/output: per datasheet's recommended values FIRST (converter caps are
  part of the control loop, not generic decoupling)
- RF/matching: NP0 at exact value with tight tolerance (5% class or better)

## §2 Regulators & LDO categories

| Need | Category | Selection logic |
|---|---|---|
| 3V3 logic rail, ≤500 mA, quiet | LDO (SOT-23-5/DFN class, fixed) | PSRR + dropout; e.g. any modern 300 mA-class LDO with enable |
| Rail from 24 V industrial input | LDO rated ≥30 V input or pre-buck | headroom = dissipation = (Vin-Vout)·I on the package |
| Efficient step-down ≥1 A | sync buck (integrated FETs) | datasheet hot-loop figure drives layout (`../../pcb-routing/SKILL.md`) |
| Motor/actuator rails | buck with external FETs or controller | current class + gate-drive voltage availability |
| USB VBUS to 3V3 | 500 mA-class LDO + input ferrite | + CC/pd contract check per `../../pcb-layout` |
| Battery systems | BMS + charger IC + fuel gauge | dedicated skill territory (see `../../pcb-skill-creator/SKILL.md` to author one) |

Rule: 2–5 V dropout headroom for LDOs (thermal check: P=(Vin−Vout)·I on the package's
θja); bucks: follow the datasheet's inductor/Cout values and re-derive when repurposing
(feedback divider recompute, compensation check).

## §3 ESD/TVS selection by interface

| Interface | Protection family | Key parameters |
|---|---|---|
| USB2 data | low-cap ESD array (~1 pF-class) | keep D+/D- cap symmetric; 5 V-class stand-off |
| USB VBUS | TVS diode 5 V-class standoff | surge rating per environment |
| Ethernet | Ethernet transformer WITH Bob-Smith termination | caps 1kV-rated 2kV class for unused pairs |
| RS-485/CAN | automotive-rated TVS array | stand-off ≥ line common-mode |
| 24 V industrial in | SMA/SMB TVS 33–36 V standoff | reverse diode + fuse upstream |
| Contacts/buttons | ESD array at connector | chassis/ground return path per layout skill §5 |

Placement: at the connector, before anything else (see `../../pcb-layout/SKILL.md`).

## §4 Crystals & resonators

- MCU HSE: 8–40 MHz AT-cut crystal + 2× C0G load caps; load cap value =
  (CL_spec − pin/stray capacitance) per MCU datasheet; place within mm of pins.
- 32 kHz RTC: tuning-fork crystal — drive level matters (series resistor if
  datasheet says so); watch crystal footprint mechanicals.
- Modules with internal clocks (ESP-class, many BLE SOCs): NO external crystal —
  read the module datasheet, don't add parts the design doesn't have.
- Ceramic resonators with built-in caps: acceptable for tolerant timing; wider
  tolerance than crystals (±0.5% class vs ±20 ppm) — never for USB/precision.

## §5 Connector quick-guidance

| Signal | Connector family notes |
|---|---|
| MCU debug | 1×6/2×3 pin header, 2.54 mm, keyed by pin-1 marking (SWD/UART conventions) |
| Motor outputs | screw terminal (5.08 mm) or XT/JST by current; lock-clip for vibration |
| USB-C | 16-pin receptacle + shell pads grounded + CC Rd 5.1k×2 |
| Board-to-board | match BOTH footprints + mating stack before layout |
| Programming ISP | tag-connect footprint option: no connector cost on production |

Every connector: check the CABLE exists as a catalog item (SKILL.md §5 risk note).
