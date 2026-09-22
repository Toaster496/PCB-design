---
name: pcb-board-format
description: >-
  Board format, outline, stackup, and mechanical setup for PCBs: choosing layer count,
  board thickness, copper and dielectric materials, surface finish; drawing outlines
  with cutouts and slots; mounting holes and mechanical clearance; panelization for
  assembly; and fab note documentation. Use whenever the user discusses board size,
  "how many layers", layer stackup, 2 vs 4 layer boards, FR-4/Tg, ENIG vs HASL,
  board thickness, mounting holes (M2/M3), cutouts/slots, panelization, V-score,
  castellated boards, gold fingers, or is about to create the physical board file —
  even for questions like "my board needs to fit in this enclosure" or "is 1.6mm the
  right thickness".
---

# pcb-board-format — outline, stackup, mechanicals

Board setup decisions are made once and punished forever: the outline, stackup, and
materials determine what routing, impedance, thermal, and assembly can achieve. Make
them deliberately, at Phase 5, before placement.

## 1. Outline & form factor

**Start from the enclosure, not the copper.** The board's job is to fit its mechanical
world:

1. Draw the outline on the board's **Edge_Cuts / outline layer** — never on a copper,
   silkscreen, or mechanical-comment layer (a classic mistake: fab mills the wrong
   layer or ignores it entirely).
2. Place the position-fixed items FIRST, as real parts: connectors the enclosure
   dictates, mounting holes, LEDs/buttons visible through the case, antenna module
   position (usually an edge/corner).
3. Board-to-board connectors: align mated boards' outlines before either is placed —
   draw both outlines if needed.
4. Rectangular is cheap; every curve adds fab cost. Rounded corners are used when a
   board slides into rails/sleeves, or an enclosure corner demands it (typical radius
   1–3 mm — verify against fab's minimum router bit, commonly 1.0–2.0 mm; a generic
   conservative value is ≥1 mm).
5. Cutouts and interior slots: allowed, but each is routed (milled), which costs money
   and adds a tool-diameter constraint — interior corners can never be sharper than
   the router bit (generic conservative inner radius ≥1 mm; many quick-turn fabs run
   0.8–1.0 mm bits). Keep copper, pads, and components ≥0.5 mm (conservative generic
   default — verify per fab) away from any routed edge, more for mains-voltage
   creepage.

**Edge clearance for parts & copper:** components that survive the reflow oven still
get sheared in panel depaneling. Keep parts ≥0.5 mm from V-score lines and ≥2 mm from
mouse-bite/stamp-hole edges (conservative generic defaults; see
`references/panelization.md`). Copper-to-board-edge: ≥0.3 mm typical quick-turn
minimum; 0.5 mm is safer and costs nothing.

## 2. Stackup selection

Layer-count decision tree (full rationale and canonical stackups in
`references/stackups.md`):

| Situation | Layers | Why |
|---|---|---|
| Single rail, low speed (≤ a few MHz edges), hand-assembled, no FCC/CE | 1 | Cheapest; everything on one layer, jumpers allowed |
| MCU ≤ ~50 MHz edges, mixed-signal, want EMC margin | 2 | Bottom layer becomes near-solid ground pour; the workhorse of hobby/light-industrial boards |
| Fast edges (USB 2.0 HS, Ethernet, DDR, dense BGA), or FCC/CE emission margin needed | 4 | Full ground + power planes; every signal layer adjacent to a reference plane |
| Dense high-speed (multi-Gb SerDes, dense DDR), strong EMC requirements | 6+ | Extra plane pairs; impedance control throughout |

**Why signal layers want adjacent reference planes:** return current flows directly
under/below its trace (least impedance) — but only if an unbroken plane is adjacent. A
signal layer sandwiched between two planes gets a tight, well-defined return path and
controlled impedance; a signal layer facing another signal layer gets crosstalk and
radiation. This single fact drives every canonical stackup.

Canonical 4-layer: **SIG − GND − PWR − SIG** (outer signals, inner planes; power and
ground couple capacitively, each signal layer faces a plane). Alternatives and
6/8-layer options with tradeoffs: `references/stackups.md` §2.

**Controlled impedance:** decide which nets need it (USB 90 Ω diff, Ethernet 100 Ω
diff, single-ended RF 50 Ω — typical protocol values, verify against the protocol
spec). Do NOT hand-compute and hard-code widths: send the stackup to the fab and ask
for their impedance worksheet results (they etch to THEIR process). The workflow: pick
stackup → request fab's impedance values → enter returned widths/spacings as design
rules → route → confirm in fab's return email that the stackup is on their standard
list (non-standard prepreg = surcharge). Detailed workflow: `references/stackups.md` §4.

## 3. Materials & finishes

| Choice | Options | Selection logic |
|---|---|---|
| Base | FR-4 Tg130/Tg150+, high-Tg for thick/multilayer or thermal cycling | Tg150+ if the board runs hot (>~105 °C ambient or power-dense) or has ≥6 layers / thick copper — verify rating per vendor |
| Copper | 35 µm (1 oz) default; 70 µm (2 oz) for high-current/power | 2 oz relaxes etch precision (wider min trace/space), raises cost — use only when current demands (`../../pcb-design-rules` current tables) |
| Surface finish | HASL (cheap, uneven for fine pitch), ENIG (flat, gold, storability, cost), OSP (cheapest flat, short shelf life), immersion Ag (flat, tarnishes) | Fine-pitch/BGA/0402-and-below → flat finish (ENIG/OSP); prototypes from budget fabs → HASL is fine. Contact/edge connectors → ENIG gold |
| Solder mask | Green default; others often free now | Matte reduces glare under inspection lamps; white can raise temp slightly in sun-exposed outdoor use (marginal) |
| Thickness | 1.6 mm default | Set by connectors (USB-C/ PCIe edge / castellated module carrier) and stiffness needs; thin 0.8–1.0 mm flexes — avoid thin boards with heavy connectors at the edge |

IPC references: IPC-2221 (generic design), IPC-6012 (board qualification/ performance
class). Values above are selection guidance, not fabrication limits.

## 4. Mechanicals

- **Mounting holes**: M2 = 2.2 mm dia, M2.5 = 2.7 mm, M3 = 3.2 mm (non-plated, common
  generic values; plated if the hole must ground to a standoff — then it's a pad with
  clearance). Keep copper and components a keepout ring around the hole: generous
  generic default = hole dia + 2–4 mm diameter total keepout (screw head + driver
  clearance); metal standoffs demand more edge copper clearance than plastic.
- **Plated vs non-plated mounting holes**: non-plated default (no accidental shorts,
  no plating cost); plated when you need screw-ground (EMC bonding) — then give it a
  proper annular ring and net it deliberately.
- **Height/z-profile**: build a mental (or drawn) side view per zone. Common
  violations: electrolytic under a shield can, shrouded connector colliding with
  enclosure rib, module antenna under a metal lid (fatal for RF).
- **Overhanging parts**: castellated/edge modules and right-angle connector bodies can
  legally overhang the board edge — verify nothing conductive below and the enclosure
  allows it. A module antenna overhanging the edge is often intentional (clearer RF);
  a USB connector overhanging is usually a placement bug.
- **Fiducials**: global (3, asymmetric triangle placement, ≥5 mm from edges/bad –
  verify per assembler) + local fiducials near fine-pitch clusters (0.4 mm pitch and
  below). Panel requirements: `references/panelization.md`.
- **Test/measurement access**: mechanicals phase is when you decide whether a
  connector, tag-point, or test point serves each external signal — not after routing.

## 5. Panelization (if the board is small or volume is real)

Breakaway methods (V-score vs mouse-bites vs stamp holes), rails/tooling holes,
panel sizing, and the economics — full detail in `references/panelization.md`.
One-line decision: single board with ≥~50 × 50 mm outline and hand/prototype assembly
→ don't panelize; small boards, machine assembly, or volume production → panelize
with V-score if the outline is rectangular, mouse-bites only where the outline is
irregular.

## 6. Fab documentation layers

- **Outline layer discipline**: exactly one authoritative board outline on
  Edge_Cuts/Board Outline. Duplicates (e.g. also on KeepOut or Mech1) create fab
  ambiguity — declare non-authoritative copies explicitly if a mechanical drawing
  layer must carry dimensions.
- **Silkscreen conventions**: reference designators readable from one primary
  orientation; polarity/rotation marks (pin-1 dot, diode cathode bar, electrolytic +
  stripe) visible AFTER assembly; never rely on silk under a part body. Minimum silk
  line width ~0.15 mm / 6 mil (quick-turn generic — verify; text height ≥1 mm).
- **Drill drawing**: optional at quick-turn fabs (they read the Excellon), mandatory
  for premium/mil-spec documentation packages — generate it, reviewers use it.
- **Fab notes**: fill `assets/fab_notes_template.md` per order — stackup + finish +
  copper weights + quantity + impedance notes + special process flags. The note block
  is what a human at the fab reads; ambiguous notes get free-run guesses.

## 7. Worked example (labeled, anonymized)

**Example 1 — 2-layer motor-driver board with MCU module:**
Input: 82 × 30 mm outline (enclosure rail constraint), 12 V input + on-board buck to
3V3, ESP32-C3-WROOM-class module with PCB antenna at the top edge, 3 × half-bridge
motor drivers at 1–2 A each, USB-C for programming, JLC-style quick-turn fab.
Output:
- 2-layer, 1.6 mm, 1 oz copper, HASL (0805-and-up passives, hand-reworkable).
- Stackup: SIG/BOT-GND-pour top? no — top = signals + power pour under drivers;
  bottom = near-solid GND pour with stitching vias (2-layer ground strategy per
  `../../pcb-routing/SKILL.md`).
- Mechanicals: 4 × M3 non-plated at corners (3.2 mm + keepout), USB-C on left edge
  (connector shell edge-flush), module antenna overhanging top edge with keepout rule
  area on both copper layers extending past the antenna region (see
  `../../pcb-layout/SKILL.md` wireless section).
- Finish: HASL acceptable (no fine pitch); ENIG chosen instead for the module pads'
  flatness and 6-month assembly delay.

*(This example is a labeled, anonymized worked case — the rules above do not derive
from it.)*

## 8. Verify-before-you-fab checklist

- [ ] Outline is a single closed shape on the outline layer; dimensions match the
      enclosure drawing; units confirmed (mm).
- [ ] Mounting holes present, sized, keepout rings drawn; enclosure screws fit.
- [ ] All position-fixed connectors placed at their true locations.
- [ ] Layer count & stackup chosen with the decision tree; impedance-critical nets
      identified; fab worksheet requested/returned.
- [ ] Thickness fits every connector's mating spec.
- [ ] Finish matches pitch + shelf-life + rework needs.
- [ ] Panelization decision made (and if panelized: rails, fiducials, breakaway
      clearance honored).
- [ ] Fab notes filled from the template; nothing marked "TBD".
- [ ] Journal + backup checkpoint at this gate (`../../pcb-project-continuity/SKILL.md`).
