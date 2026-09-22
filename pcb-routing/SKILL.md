---
name: pcb-routing
description: >-
  PCB routing strategy and technique: routing order of operations (fanout, critical
  signals, power, fill), ground-plane strategy and return-current physics, PDN and
  converter hot-loop routing, trace geometry, crosstalk, differential pairs, length
  matching, high-speed and RF addenda, and post-route DRC cleanup. Use whenever the
  user is routing or asking how to route — "traces", "planes", "ground pour",
  "stitching vias", "differential pair", "length matching", "USB routing", "how do i
  route the buck converter", "return path", "crosstalk", DRC error fixing, or when
  an autorouter or headless/scripted routing approach is being discussed.
---

# pcb-routing — routing strategy & techniques

Routing is applied electromagnetics: every trace is a transmission line, every
return current knows exactly where it wants to flow, and every mistake is an antenna.
The strategy here is about ORDER (what gets routed first and why) and PHYSICS (ground
above all). Tool button locations live in the variant references; read only your tool's
file when you need mechanics.

## 1. Order of operations

| Order | Route | Why this order |
|---|---|---|
| 1 | **Fanout/escape** — one via per escaped pad, short escape stubs | unlocks inner layers; defines channels; per-pitch strategy below |
| 2 | **Critical signals** — clocks, diff pairs, RF, analog sense | they get FIRST pick of the quiet real estate; everything else routes around them |
| 3 | **Power** — rails as pours/wide runs, converter hot loops | power geometry is performance geometry (loop area = spikes) |
| 4 | **General signal** | by zone, ratsnest-densest first |
| 5 | **Ground fill + stitching** | last, but PLANNED since placement |

**Never blind autoroute.** Interactive routing with the ratsnest as a plan beats any
autorouter pass because the router doesn't know which loop is hot, which pair is
timing-critical, or which plane break is fatal. Acceptable autorouter use: after
critical/power routing is locked, on the boring residue, with a via-count budget and
a full DRC+review pass after (many tools let you lock the good nets first).

**BGA escape by pitch** (0.8 mm+): straight channel escape; (0.5–0.65 mm): dogbone
(via offset diagonal from pad, channel between pads); (≤0.4 mm): via-in-pad (plugged
— `../../pcb-design-rules/references/vias.md`) or buy more layers.

## 2. Ground strategy — read this before routing anything

**The single most important fact in this skill:** return current flows under the
signal trace, in whatever adjacent plane exists, concentrated in a band ~1–2× trace
height wide, following the path of LEAST IMPEDANCE — at any frequency above ~kHz that
means least INDUCTANCE, which means directly under the trace, not the shortest DC
path through a via somewhere.

Everything else follows:

1. **Solid ground planes, unbroken under signals.** A slot or split under a trace
   forces the return to detour — the detour area IS a loop antenna; it radiates and
   picks up. If a split is unavoidable (rare, usually legacy 20th-century thinking),
   never cross it with a fast signal; if a signal must cross, bridge the split with
   a stitching capacitor where the signal crosses (return path continues through it).
2. **Plane splits are usually wrong.** The "split AGND/DGND" doctrine predates
   understanding of return paths: a single solid plane with disciplined routing (fast
   digital on its side, quiet analog on its side) beats split planes with signals
   crossing them. Split ONLY when the datasheet of a specific part demands it
   (rare, e.g. some AGC/RF parts), and then nothing crosses the split.
3. **Stitching vias** along every plane-adjacency change: signal layer transitions
   need a return via NEXT TO the signal via (within ~1–3 mm — the return's detour
   through the via pair is the loop). Edges, connector entries, and pour boundaries:
   stitch every 5–15 mm. Floating copper (islands) is bad: a GND island tied weakly
   resonates — tie islands with vias or delete them (DRC's zone-island warnings
   exist for this reason).
4. **Single-point vs multipoint grounding** decision: at board scale, MULTIPLE
   stitches (multipoint) — it's RF out there; single-point star ground is for
   audio-frequency instrument innards and battery SELV gadgets with one ground
   reference. Hybrid: star the sensitive analog cluster's RETURNS to one pour point,
   but keep the pour multipoint to the main plane.
5. **Two-layer boards**: top = signals + power pours, bottom = as-close-to-solid GND
   pour as the crossing signals allow; route bottom-layer signals predominantly on
   ONE axis; each top-layer GND region stitches to the bottom pour frequently.
   USB2-FS, CAN, I2C, UART boards live happily this way; the discipline is the cost.

## 3. Power distribution (PDN) & converter loops

- **Hot loops FIRST — name them out loud**: the buck input loop (input cap + high
  switch + low switch/diode + ground return) and the output loop (switch + inductor +
  output cap + return) carry the board's highest dI/dt. Minimize their AREA — place
  the parts for a minimal loop (`../../pcb-layout/SKILL.md` §5), then route the loop
  as a fat short path with solid return underneath. The SW node (the switching
  voltage) gets copper sized for thermal, but it is NOT poured wide across the board
  — SW node area = radiating patch antenna area.
- **Planes vs traces**: 3V3-class logic rails → pour/plane sharing with GND's
  capacitance; amps-class rails → pours with calculated necks; sense/fine-bias rails
  → routed clean. Don't plane a rail you need to isolate (analog AVDD often wants
  ferrite separation, not plane sharing).
- **Decoupling hierarchy**: bulk (rail entry, 10–100 µF) → mid (per cluster, µF-class)
  → local (per pin, 100 nF + 10 nF where fast). Placement physics:
  `../../pcb-layout/SKILL.md` §3. Target-impedance intuition: the plane pair + cap
  ladder is a parallel impedance network; each decade of cap covers its band only if
  its LOOP is short — a far cap is off the network at high frequency.
- **Kelvin sense lines**: sense (FB, shunt amp) routes as a routed PAIR out of the
  current path's junction points, kept out of the field of the hot loop (route them
  away, shielded by GND, never parallel to SW node).
- **Star vs daisy-chain vs plane for multiple loads**: star at the regulator for
  mixed quiet/loud loads (shared trace impedance couples the loads); daisy-chain
  only for same-type loads with a stiff local decap each; plane when the loads are
  many and logic-class. A 2-layer power board's compromise: a poured "ground spine"
  with loads' returns stitching to it at their own point.

## 4. Signal routing geometry

- **Corners: 45° or gentle curves, never sharp 90°** on anything fast — not because
  "the corner radiates" folk physics (it's a tiny effect at ordinary speeds), but
  because sharp inside corners create ACID TRAPS in etching (under-etched slivers)
  and impedance discontinuities accumulate. 45° costs nothing and is what the fab
  prefers; RF traces prefer swept arcs.
- **Width consistency for impedance**: a controlled-impedance net is only as good as
  its narrowest neck — enter widths as class constraints and don't eyeball-shrink
  to squeeze past a pad.
- **No stubs**: a stub is an unterminated quarter-wave-ish resonator and a
  reflection site. Route point-to-point; T-taps only for genuinely low-speed nets
  (I2C at classic rates tolerates them; USB never does).
- **Crosstalk control**: 3W rule (space ≥3× trace width center-to-center between
  aggressor/victim on adjacent parallel runs) as the workable heuristic; reference
  plane integrity matters more; guard traces (ground between two signals) only WITH
  stitching vias at both ends + periodic, else the guard becomes a radiator.
- **Layer assignments**: same-direction routing per layer (L1 horizontal, L4
  vertical...) reduces parallelism by construction; adjacent signal layers on 4+
  layer boards prefer perpendicular preferred-axes.

## 5. Differential pairs

- **Intra-pair geometry is CONSTANT**: width + gap locked along the whole run (that's
  the impedance); keep the pair coupled — don't spread the gap to squeeze past
  obstacles (spreading decouples and changes Z).
- **Intra-pair length matching (skew)**: budget comes from the RECEIVER's timing
  spec (e.g. USB2 wants pair skew ≪ bit-time fraction — a typical engineering target
  is <1–2 mm equivalent class; Ethernet pairs have their own per-spec budgets).
  Derive from the protocol, don't parrot folklore.
- **Inter-pair separation**: pairs spaced ≥3–5× intra-pair gap from other pairs; all
  diff pairs keep distance from fast single-ended nets.
- **NEVER split a pair across plane gaps or reference changes without treatment**:
  if a pair changes layers, change both members together with adjacent return vias.
- **Protocol targets (typical, verify per spec/fab sheet):** USB2 90 Ω, USB3
  85/90 Ω by spec version, Ethernet 100 Ω, LVDS 100 Ω, PCIe 85 Ω. Widths come from
  the FAB's impedance worksheet (`../../pcb-board-format/references/stackups.md` §4),
  never from memorized numbers.
- **Ground under diff pairs**: the pair references the plane; keep the plane solid
  and symmetric under both members.

## 6. Length matching & timing

- Which buses need it: DDR (byte-lanes + strobe, per-speed budgets), parallel buses
  with common setup windows, some SerDes with lane de-skew requirements. I2C/UART/
  SPI at ordinary rates do NOT need serpentine heroics.
- **Derive tolerance from the timing budget**: matching tolerance ≈ (setup/hold
  window fraction) × signal velocity. Rule-of-thumb sanity: 1 mm of FR-4 trace ≈
  ~6 ps one-way (verify: velocity ≈ c/√εeff, εeff ≈ 4 for microstrip internal-ish).
  Don't match to 0.1 mm when the budget allows 5 mm — that's context waste and
  serpentine crosstalk for nothing.
- **Serpentine rules**: amplitude ≥3× trace width (avoid self-coupling), uniform
  pitch, match at the SOURCE end if possible (accordion near the source), and keep
  serpentine sections out of parallel proximity with other long nets. A serpentine
  at the receiver end sits in the noisiest region and couples exactly where margins
  are spent — a classic mistake.

## 7. High-speed & RF addenda

Controlled-impedance workflow (fab worksheet → rules → route → verify), reference
plane changes, transmission line types (microstrip/CPW), RF do's/don'ts and antenna
feedline rules: `references/high-speed.md` and `references/rf.md`. Read them when
any net is faster than ~50 MHz edges or carries RF. RF rules in one line: SHORT,
STRAIGHT, 50 Ω-class, grounded-coplanar if company is unavoidable, and nothing near
the antenna but air.

## 8. Post-route cleanup

1. **DRC sweep strategy**: run full DRC; triage output — real errors (fix ALL),
   warnings (review: silkscreen-over-copper and courtyard overlaps are usually
   cosmetic; copper-clearance warnings never are), inherited (from the original
   design — document, don't chase). Fix in order: connectivity > clearance > silk.
2. **Fix without creating new ones**: fix one class at a time, re-run DRC after each
   class, never bulk-move tracks blind.
3. **Unconnected-list triage**: GND "unconnecteds" are usually zone-fill artifacts
   (refill zones, re-check; real islands = stitch or delete); signal unconnecteds
   are real gaps — gap-fill deliberately.
4. **Dead copper**: delete un-tied islands (DRC flags them); every island is a
   resonator waiting for a harmonic.
5. **Silkscreen cleanup**: refdes visible, off pads, consistent rotation; fix now —
   it's the last cheap moment.
6. **Visual review passes**: top copper, bottom, each pair, silkscreen alone, and a
   3D pass (`../../pcb-pitfalls/SKILL.md` pre-fab checklist). A 3D render catches
   height collisions 2D hides — worth the minutes.

## Tool mechanics (variant references)

- KiCad: interactive router modes (push/shove), diff-pair router, length-tuning
  tools — `references/kicad.md`
- Altium: — `references/altium.md`
- EasyEDA / generic / headless-scripted routing patterns — `references/generic.md`
