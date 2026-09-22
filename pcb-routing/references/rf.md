# RF routing addendum

TOC: §1 Line types · §2 RF do's · §3 RF don'ts · §4 Antenna feedlines & keepouts ·
§5 Shields, paddocks, and stitching fences

## §1 Line types

| Type | Geometry | Use |
|---|---|---|
| Microstrip | trace / dielectric / plane (top layer) | general RF on outer layers; εeff < εr, fastest velocity |
| Stripline | trace BETWEEN two planes (inner) | shielded runs; slowest; needs layer-pair planning |
| Coplanar waveguide (CPW/CPWG) | trace + adjacent ground pour walls + plane beneath | controlled environment when neighbors are unavoidable; keep wall gap CONSTANT |

Impedance from the fab worksheet per stackup (same workflow as high-speed §2);
RF working widths are commonly 0.3–0.8 mm class at 2.4 GHz FR-4 — never memorize,
always calculate/request.

## §2 RF do's

- SHORT: every mm is phase and loss; route direct.
- STRAIGHT: bends are swept arcs (2× width radius class) or mitered 45°.
- CONSTANT geometry: width, gaps to coplanar walls, reference beneath — any change
  is a discontinuity/transformer stub.
- VIA FENCES: ground vias at λ/20-or-less spacing (at the frequency of concern)
  along CPW walls and section boundaries — the wall is only a wall if it's stitched.
- Ground FIRST: RF ground stitching is part of routing, not cleanup.
- Isolate by section: PA → filter → antenna in one flow line; each section's ground
  stitched to the main pour at its boundary.

## §3 RF don'ts

- No vias in the feedline where avoidable (inductive discontinuity; 0.1–0.2 nH each
  is REAL at 2.4 GHz+).
- No layer changes for the main RF line; if unavoidable, via PAIR + adjacent ground
  vias.
- No stubs, no test points ON the line (a TP pad is a shunt capacitor), no silk over
  the line (mask thickness matters at mmWave).
- No other traces parallel-coupled to RF runs — crossing at 90° under/over on
  another layer is the polite crossing.
- Never route ANYTHING under the antenna keepout or the module's antenna region
  (`../../pcb-layout/SKILL.md` §5).

## §4 Antenna feedlines & keepouts

- Feedline: 50 Ω-class microstrip/CPWG, as short as the placement allows, ground
  pour walls stitched (CPWG preferred when anything lives nearby).
- The antenna keepout: ALL copper layers under + around the antenna section
  (extend beyond the antenna footprint — a PCB antenna's field reaches beyond its
  drawn outline); no traces, no pours, no parts, no silkscreen bodies (parts!).
- Matching network (π/pad) AT the antenna feed point, components in-line, ground
  return via immediately at each shunt pad's ground — the matching network's ground
  return path is part of the matching.
- Detune hazards beyond the board: batteries, cables, metal enclosures within
  ~5–10 mm of the antenna (coordinate with mechanicals at Phase 0 —
  `../../pcb-flow/references/interview.md`).

## §5 Shields, paddocks, stitching fences

- Shield-can footprints: castellated ground wall + interior ground pour; stitch
  under the wall; bring feedthrough caps in/out at the wall.
- Section fences: ground via rows at RF section boundaries (PA/digital/antenna) —
  λ/20 spacing at the worry frequency.
- The RF section's pour ties to main GND at controlled points (not one thin neck —
  and not "everywhere either": controlled multipoint).

Final acceptance for an RF section: DRC clean + a network-analyzer/over-the-air test
plan the human will actually run (agents don't measure; they plan the measurement).
