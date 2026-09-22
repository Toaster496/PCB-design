# Stackups — layer counts, canonical arrangements, impedance

TOC: §1 Principles · §2 Canonical stackups · §3 Layer-pair decisions · §4 Controlled
impedance workflow · §5 Unusual stackups

## §1 Principles

1. **Return current wants the adjacent plane.** A trace's return current concentrates
   in whatever conductive surface is nearest, directly under the trace (path of least
   impedance — inductance-dominated above ~kHz). Every routing decision that breaks
   this (plane split under a trace, layer change without a stitching via) makes a
   loop antenna.
2. **Signal layers alternate with reference planes** whenever budget allows. Two
   signal layers facing each other = coupled crosstalk + undefined impedance.
3. **Power plane adjacent to ground plane** = interplane capacitance, the cheapest
   high-frequency decoupling there is (works into the hundreds of MHz).
4. **Outer layers are etched finer than inner** (surface copper), and are the only
   layers you can probe/rework — put the highest-density fanouts and test access
   there; put long quiet buses on inner shielded layers (4+ layer boards).
5. Symmetric copper (top/bottom balance) reduces warpage on thick boards — matters at
   ≥6 layers, 2 oz copper, or >2 mm thickness.

## §2 Canonical stackups

### 2-layer (the workhorse)
```
Top    : signals + power pour where needed
Bottom : ~solid GND pour (stitch vias to top GND islands)
```
- Bottom pour must stay unbroken under every signal that matters; crossing top-layer
  cuts with bottom signals is the classic 2-layer EMC mistake. Route bottom signals
  predominantly one axis (e.g. horizontal) so the pour is mostly intact.
- Works up to ~50 MHz edge rates with discipline; USB 2. full-speed, CAN, I2C, UART
  all fine. High-speed USB (480 Mbps) or Ethernet PHY MDI → prefer 4 layers.

### 4-layer (default for anything fast or regulated)
```
L1 Top    : signals + components
L2        : GND (solid)
L3        : PWR (or second GND if power is routed as pours)
L4 Bottom : signals
```
- Every signal on L1 references L2; every signal on L4 references L3. Keep L2
  UNBROKEN — route nothing on it if you can avoid it.
- Alternative `SIG-GND-GND-SIG` when power is poured on signal layers: better EMC,
  worse power distribution. Choose when rails are few and currents modest.
- Substituting a signal layer for the PWR plane (`SIG-GND-SIG-GND`) is also legit and
  gives two shielded signal layers — preferred for dense BGA fanout boards where power
  is one 3V3 rail poured locally.

### 6-layer (dense/high-speed)
```
L1 SIG / L2 GND / L3 SIG / L4 PWR / L5 GND / L6 SIG
```
- Two shielded signal layer pairs; power between planes. Common for Ethernet switches,
  fast SDRs, dense MCUs.
- Alternative with two inner signal layers (L3/L4) facing planes on both sides — for
  SerDes-heavy boards; slower buses go mid-stack, sensitive clocks go L1/L6? no —
  opposite: high-speed serial prefers inner shielded layers.

### 8-layer
Signal/plane alternation continues; typical driver is a third shielded pair for DDR
row/col buses or separations for RF. Beyond 8, you are in specialist territory —
engage the fab's stackup engineer.

## §3 Layer-pair decisions

| Need | Resolution |
|---|---|
| Controlled impedance on many nets | 4+ layers; every impedance layer adjacent to a plane |
| Big current (≥5 A rails) | Copper weight + pours/planes; consider 2 oz outer; dedicated PWR shape per `../../pcb-design-rules` current guidance |
| Thermal spreading | Internal GND plane as spreader; via arrays under thermal pads |
| Dense BGA escape | 6+ layers; assign one layer per BGA row-class (dogbone channels) |
| Cost floor | 2-layer; accept routing discipline burden |
| FCC/CE first-pass EMC | 4+ layers; solid adjacent references; stitched connectors |

## §4 Controlled-impedance workflow

1. **Enumerate impedance nets** from the protocol (USB2 90 Ω diff, LVDS 100 Ω diff,
   Ethernet 100 Ω diff, single-ended RF 50 Ω; PCIe 85 Ω diff — typical values; the
   PROTOCOL SPEC + fab's worksheet govern).
2. **Fix the stackup** (which layers the pairs route on, dielectric thicknesses).
3. **Send it to the fab** — "please confirm impedance control for this stackup and
   supply width/gap for 90 Ω diff on L1 and 100 Ω diff on L3". Fabs return values
   measured for THEIR etch process; homebrew calculators are approximations (etch
   trapezoid, prepreg squeeze, mask participation in microstrip models).
4. **Enter returned W/S as design rules** (net class constraints), route, and never
   eyeball-adjust them later.
5. **Confirm the stackup is on the fab's standard list.** Custom prepreg/cores = tooling
   surcharge + longer lead.
6. Document in fab notes: "impedance-controlled per fab worksheet dated <date>".

Coupons: fabs include impedance test coupons on the panel — ask for the report if the
design is production-bound.

## §5 Unusual stackups

- **Flex/rigid-flex**: separate discipline (copper adhesion, bend radius, stiffeners).
  If the design needs flex, author a dedicated skill via `../../pcb-skill-creator/SKILL.md`
  rather than improvising.
- **Metal-core (MCPCB)**: LED/high-power boards; one copper layer on an aluminum
  substrate; all routing rules change (no vias through the core, thermal vias are the
  whole point). Same advice: dedicated skill.
- **Hybrid**: heavy copper outer + signal inner — engages fab engineering directly.
