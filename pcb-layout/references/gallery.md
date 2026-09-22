# Placement pattern gallery — classic arrangements in words and ASCII

TOC: §1 Buck converter cluster · §2 MCU decap ring · §3 USB-C entry · §4 Crystal
guard · §5 Motor driver channel · §6 Sensor bridge front-end · §7 Connector edge
protection

The point of this gallery: recognize the pattern, place parts to instantiate it, THEN
route. ASCII is schematic-of-placement, not to scale.

## §1 Buck converter cluster (hot-loop-first placement)

```
   VIN ──[fuse]──[input bulk cap C_IN]──┐
                                      │ ┌──────────┐
                              SW pin ─┼─┤  BUCK IC ├─
                    ┌───[HF cap]──────┘ │  L1 SW GND│
                    │                   └─┬────────┘
                 [diode or
                sync FET]              GND via ↓ plane
                    │
                 [L]──→ VOUT ──[C_OUT]──→ load
```
Placement action: C_IN HF cap, IC, diode, and (synchronous) low FET form a fist-sized
cluster — the loop C_IN→IC→diode→GND is THE hot loop (highest dI/dt in the board);
make its perimeter minimal with parts, not routing. Then L and C_OUT complete the
output loop. FB divider sits at the FB pin, far from SW node copper.

## §2 MCU decap ring

```
        ┌──C1──┐  ┌──C2──┐
        │      │  │      │        caps flanking each VDD pin,
      ┌─┴──────┴──┴──────┴─┐       each with its own via to GND
      │  MCU / SoC         │       immediately beside the pad
      │  pin1 ─ VDD ─ pin N│
      └─┬──────┬──┬──────┬─┘
        └──C3──┘  └──C4──┘
```
Placement action: caps in the pin-row gaps, vias down beside pads. Bulk (10 µF) once
per side, lenient position. If BGA: caps go on the opposite side DIRECTLY under the
power balls.

## §3 USB-C entry (2-layer MCU board)

```
  [shell] [VBUS] [CC1/CC2] [D+] [D-] [GND]     ← connector pads
     │      │       │       │     │     │
     ├── shell vias to GND pour (4+ stitched)
  [TVS array on all exposed signal pads, ≤2–3 mm inboard]
  [0.5–1 A polyfuse or ferrite on VBUS]
  [5.1k Rd pull-downs on CC1 AND CC2]
  [CM choke or series termination on D+/D- toward MCU]
```
Placement action: everything at the entry strip; the clamp sits BEFORE anything else
shares the net. Rd resistors close to the connector (they negotiate the contract —
if a port sees no Rd it supplies no VBUS default-current beyond 500 mA USB2 default;
cite USB Type-C Cable and Connector Spec for UFP Rd requirement).

## §4 Crystal guard

```
        GND guard (no pour beneath on next layer down)
       ┌────────────────────────┐
       │  XI ──[XTAL]── XO      │   load caps flank the xtal,
       │   └─[C1]  [C2]─┘      │    tie directly to the same
       └────────────────────────┘   local GND via, not a pour stroll
```
Placement action: XTAL + C1/C2 + single GND via inside a quiet region; guard ring
only if the MCU datasheet/appnote suggests it — never route other nets through the
region on ANY layer.

## §5 Motor-driver channel (repeated channel pattern)

```
   logic zone          per-channel power cluster
  ────────────── ┌────────────────────────────────┐
  PWM/EN →[R pu] │ [C_bulk]─┐   ┌─────────┐        │──→ motor OUT1
  (clean side)   │   ┌──────┴───┤ DRIVER  ├───────┤──→ motor OUT2
                 │  [CIN hf]────┤ GND pad │       │
                 │   [Rshunt]───┴─[via    └───────┘
                 │  sense]        array]      (pours + vias)
                 └────────────────────────────────┘
```
Placement action: identical mirror per channel; gate/FET loops inside the cluster;
shunt + Kelvin pads at the bottom; the cluster's GND pour ties to the plane by via
array. Logic pull resistors on the boundary so each input has a default state at
power-up.

## §6 Sensor bridge front-end

```
   [sense element / bridge]──(diff A, diff B)──[instrumentation amp
      at measurement point      symmetric traces   + gain network
                                                   + local reference]
                                      └── one guarded crossing → ADC
```
Placement action: amp at the bridge, NOT near the ADC; the two diff traces routed as
a symmetric pair through the moat crossing; gain network and its Kelvin reference
local to the amp.

## §7 Connector edge protection strip

```
 chassis/enclosure side
 ──────────────────────────
 [connector] [TVS][CM choke][series R/ferrite]   ← boundary strip
 ──────────────────────────
 interior / clean zones
```
Placement action: the strip belongs to EVERY external signal — power, comms, sensors.
Surge current's shortest path to ground must be at the connector (see EMC reasoning
in `../../SKILL.md` §5). Interior-side parts (MCU pins, sense inputs) come after the
strip, never before it.
