---
name: pcb-layout
description: >-
  Component placement and board zoning for PCBs: functional-zone partitioning,
  flow-based placement, dirty/clean separation, placement order workflow (mechanicals →
  anchors → decoupling → test points), decoupling capacitor loop-area physics, thermal
  and EMC-aware placement, wireless-module antenna keepouts, and assembly/rework
  access. Use whenever the user is placing parts, "starting layout", asking where
  components should go, complaining the ratsnest is a mess, asking about decoupling cap
  or crystal placement, antenna keepouts, hot components, test points, or silkscreen
  readability — even casually like "where do i put the buck converter".
---

# pcb-layout — zoning & placement

Placement is where the board's EMC, thermal, routing, and serviceability budgets are
mostly spent. A good placement makes ordinary routing rules produce an extraordinary
board; a bad placement cannot be rescued by routing heroics. Work placement
deliberately, in passes, with the ratsnest as your score.

## 1. Zoning methodology

Partition the board into functional zones BEFORE any part is placed:

```
 [connectors / entry edge]
 [protection & filtering at the boundary]
 [power conversion]   [digital / MCU]   [analog / sensing]
 [RF]  [actuators / high-current outputs]
```

**Rules of zoning:**

1. **Flow follows signal direction.** Signal enters (connector edge) → gets protected
   (TVS/filters AT the boundary) → processed (MCU/analog) → exits (outputs, second
   connector). Placing zones in flow order minimizes net crossings — visible directly
   as a calmer ratsnest.
2. **Dirty and clean zones never share real estate.** Switching converters, motor
   drivers, and fast digital edges are "dirty" (high dV/dt, dI/dt); sense amplifiers,
   ADC front-ends, precision references, crystals, RF receivers are "clean". Separate
   them with distance (a few mm of nothing beats any filter you forgot to add) and
   preferably a ground moat/pour boundary. The separation discipline is what makes
   2-layer mixed-signal boards work.
3. **Connectors live at zone boundaries** — that is where protection parts go, and it
   keeps cable dressing outside the sensitive interior.
4. **Zone map onto the physical constraints first**: the enclosure fixes connector
   positions, mounting, and the antenna region; everything else negotiates around them.

Draw the zone rectangles (on a mechanical/keepout layer or in a comment) so later
placement decisions have something to violate visibly.

## 2. Placement order (the workflow)

| Pass | Place | Why this order |
|---|---|---|
| 1 | **Mechanicals & position-fixed parts** (mounting holes, connectors, switches, LEDs, the wireless module) | They are non-negotiable; everything else fits around them |
| 2 | **Anchors** — big ICs, magnetics (inductors/transformers), the crystal, the main regulator, modules | They define zone centers and the biggest ratsnest bundles |
| 3 | **Decoupling & local passives** around their anchors | Placed relative to anchor pins; delay past pass 2 and via/pad access is gone |
| 4 | **Test points & debug instrumentation** | Before routing claims the space; after routing there is no space |
| 5 | **Cosmetics** — labels, polarity marks, fiducials, silk | Last, but do them — pass/fail at bring-up often depends on them |

**Iterate with the ratsnest as the objective function.** After each pass, look at the
ratsnest: bundles crossing each other at an angle = placement smell. Move parts (cheap
now), don't plan to route around (expensive forever). Two or three placement
iterations cost minutes; they save routing hours.

## 3. Decoupling capacitors — the loop-area physics

Why placement dominates: a decoupling cap's job is to be a LOW-IMPEDANCE local
current reservoir above ~10 MHz. Its impedance is dominated not by the capacitor but
by the loop inductance of [IC pin → trace → cap → via → plane]. Rule-of-thumb physics:
~1 nH per mm of loop perimeter. A 5 mm detour plus vias behaves like a series
inductor that makes the cap useless exactly where you need it.

Placement method per power pin:

1. Cap within ~1–2 mm of the IC power pin (closer beats bigger; a small cap at 1 mm
   outperforms a large one at 10 mm — at high frequency, inductance caps the benefit).
2. Via from the cap's ground pad straight DOWN to the plane, immediately beside the
   pad, not shared with three other nets' vias.
3. If the IC has an opposite-side layer available, cap under the IC pins is often the
   shortest loop of all (check assembly/rework tradeoff).
4. Bulk caps (10–47 µF class) per IC cluster or rail entry — those care about the
   milliamps-times-milliseconds domain, placement is lenient (near the rail's entry
   or the IC cluster, within cm).
5. Local hierarchy: smallest cap closest to the pin; the cap sizes form a
   decade-spaced ladder (e.g. 100 nF + 10 µF) — the ladder only works if the small one
   actually sees the pin.

Anti-patterns: cap tucked neatly between two other parts 8 mm away "because it looked
tidy"; one cap shared between two ICs (each IC needs its own local loop); via-in-pad
without plugging when BGA pitch demands it (see `../../pcb-design-rules/SKILL.md`).

## 4. Thermal placement

- **Hot parts spread, don't cluster**: regulators, MOSFETs, motor drivers, LED strings,
  RF PAs each need surrounding copper area to spread heat into; two hot parts adjacent
  stack their heat-affected zones.
- **Keep heat-VICTIMS away from heat-SOURCES**: electrolytic caps (lifetime halves per
  ~10 °C), crystals (frequency drift), sensors (offset drift), battery holders.
- **Copper pour as heatsink**: a solid GND pour under/around a driver's thermal pad,
  stitched with a via array to the opposite plane, is the cheapest heatsink there is
  (via array sizing: `../../pcb-design-rules/SKILL.md` thermal-via guidance).
- **Airflow awareness**: if the product has a fan or convection path, align the
  hot-parts sequence with flow direction — upstream parts pre-heat downstream ones.
- **Antenna keepout is a thermal-adjacent fact**: any ground pour under a module
  antenna detunes it (see §5).

## 5. EMC-driven placement

- **Protection/filter parts go WHERE the signal crosses the boundary**, not near the
  sensitive IC: TVS diode, series ferrite/common-mode choke belong at the connector,
  within mm of the entry pad. ESD clamps placed after the filter or at the IC protect
  nothing — the induced surge has already coupled into interior nets.
  (The surge current needs the SHORTEST possible path from connector to chassis
  ground; every mm of trace between connector and clamp is an antenna radiating the
  ESD strike.)
- **Crystal/oscillator**: as close to the IC pins as the pin escape allows (≤3–5 mm
  typical target), guard ground around it, NO copper pours or routed signals on
  adjacent layers under the crystal region, load caps flanking the crystal with
  direct short traces to the IC's ground.
- **Sensitive traces stay off the board edge**: edge-parallel traces radiate (the
  edge is an unintentional antenna edge) and pick up ESD; route sensitive nets in the
  interior. Keep ~2–3× trace-width from edge minimum, more for anything analog.
- **Fast-switching loops get geometric attention NOW, not in routing**: place the
  buck converter's input cap, high-side switch, and diode (synchronous FET) so the
  hot loop is naturally small — placement decides loop area before routing draws a
  single trace (buck hot-loop: `../../pcb-routing/SKILL.md` §3).
- **Wireless modules**: antenna region must overhang or face empty space; keepout
  rule area on ALL copper layers under and around the antenna, extending beyond the
  module edge over the antenna section. No ground pour, no traces, no components —
  and remember batteries/cables/metal enclosures near the antenna detune it too
  (mechanical coordination, `../../pcb-board-format/SKILL.md`).

## 6. Assembly & serviceability

- **Hand-solder access** (if any rework is expected): 0603 minimum passives, rework
  gap around fine-pitch parts for an iron tip, no parts under shielding cans that
  cannot be removed.
- **Rework clearance**: one passive's width of space between tight SOIC rows where
  feasible; hot-air access to the big connectors.
- **Connector cable-bend radius**: right-angle connectors chosen so the cable exits
  without stressing adjacent parts; strain relief clips have footprints too.
- **Polarity/orientation consistency**: all diodes/electrolytics/ICs oriented the same
  way where possible — assembly error rates track visual inconsistency.
- **Test points**: one per NET you can't otherwise probe — every rail (voltage), every
  enable/communication bus node, every ground region. Distributed so a probe doesn't
  short two adjacent TP vias. Minimum per-net strategy: rails + resets + boot
  straps + each motor/gate channel + serial lines.
- **Silkscreen discipline**: refdes on EVERY part, readable from one dominant
  orientation; never ON pads (paste wicks, vision misreads); polarity marks visible
  after assembly; pin-1 marks on ICs + connectors.
- **Courtyard/IPC-7351 spacing**: keep courtyard-to-courtyard spacing so placement
  density doesn't sabotage assembly (IPC-7351 is the land-pattern/courtyard standard
  to cite; your library's footprints should already carry correct courtyards — when
  improvising one, courtyard = body + ~0.25 mm nominal, more for hand assembly).

## 7. Placement review checklist (exit gate)

- [ ] Zones drawn and honored; flow left-to-right (or chosen axis) with no
      back-and-forth bundles.
- [ ] All position-fixed parts at their true locations (check against the enclosure
      drawing ONE more time).
- [ ] Every IC: local decap ≤2 mm from its power pins, via straight down.
- [ ] Crystal/oscillator cluster tight and guarded; no pours beneath on adjacent
      layers.
- [ ] Dirty/clean separation: switching converter physically apart from analog
      front-ends; no clean nets threading the dirty zone.
- [ ] Buck/SMPS hot-loop parts adjacent by design.
- [ ] Thermal: hot parts spread; victims clear; pour vias planned.
- [ ] Antenna keepout on all copper layers, extending past the antenna; nothing in it.
- [ ] Test points present for the minimum-net set, probeable, labeled.
- [ ] Silkscreen: refdes everywhere, consistent orientation, nothing on pads.
- [ ] Ratsnest: no big multi-net crossings left; unconnected count is only
      neighbor-connections.
- [ ] Journal updated + backup checkpoint at this gate
      (`../../pcb-project-continuity/SKILL.md`).

Per-archetype checklists (MCU board / SMPS / RF / sensor front-end) and a gallery of
classic placement patterns: `references/checklists-archetypes.md` and
`references/gallery.md`.
