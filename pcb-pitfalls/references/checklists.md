# Gate checklists — per phase

Every line: pass / fail / N-A. No unmarked lines. Run these at each phase gate of
`../../pcb-flow/SKILL.md`.

TOC: §1 Post-stackup · §2 Post-placement · §3 Post-route · §4 Pre-fab-release ·
§5 Schematic-review gate

## §1 Post-stackup (board setup complete)

- [ ] Outline single closed shape on outline layer; dims match enclosure; units mm.
- [ ] Mounting holes sized (screw table) + keepout rings; enclosure screws fit.
- [ ] Position-fixed connectors at TRUE locations (re-check vs mechanical drawing).
- [ ] Layer count justified by decision tree; stackup documented in journal.
- [ ] Impedance nets enumerated; fab worksheet requested (or N-A honestly marked).
- [ ] Net classes created; widths/clearances/vias per class; fab minimums ≥20% margin.
- [ ] Thickness fits every connector's mating spec.
- [ ] Panelization decision recorded; assembler spec fetched if panelizing.
- [ ] Fab notes template filled (no TBD).
- [ ] Zone/keepout rules for antenna, HV creepage, mechanical exclusions drawn.
- [ ] Journal + backup checkpoint DONE.

## §2 Post-placement

- [ ] Zones drawn & honored; flow direction consistent; no zigzag bundles.
- [ ] Placement order followed (mechanicals → anchors → decaps → TPs → silk).
- [ ] Every IC: decap ≤2 mm from power pins with own via; bulk per cluster.
- [ ] Crystal cluster ≤5 mm, guarded, no copper beneath on adjacent layers.
- [ ] Dirty/clean separation real (measure the mm): converter/MCU away from analog.
- [ ] Buck hot-loop parts adjacent (input cap + switches + diode cluster).
- [ ] Thermal: hot parts spread; electrolytics/crystals/sensors clear; EP via arrays
      reserved.
- [ ] Antenna keepout on ALL copper layers, extends past antenna; EMPTY.
- [ ] ESD/filters at connector entry, not at ICs.
- [ ] Test points: rails, resets, boot straps, buses, per-channel signals; labeled.
- [ ] Ratsnest: only neighbor connections remain; no long diagonal bundles.
- [ ] Courtyard overlaps zero (or documented assembly-safe).
- [ ] Journal + backup checkpoint DONE.

## §3 Post-route

- [ ] DRC: 0 errors; every remaining warning classified (inherited/cosmetic/accepted).
- [ ] Unconnected: 0 real gaps; zone artifacts refilled & explained.
- [ ] Hot loops visually small (buck input/output); SW node copper contained.
- [ ] No signal crosses plane splits (render planes alone and LOOK).
- [ ] Return vias accompany layer transitions on buses/critical nets.
- [ ] Diff pairs: geometry constant, no gaps crossed, matching at source end.
- [ ] Length-matching tolerance derived from budget (not folklore) and met.
- [ ] Power necks calculated, pours where current demands, via arrays on transitions.
- [ ] Sense/FB traces routed away from SW node, shielded, Kelvin at the point.
- [ ] No dead copper islands; stitching vias along edges/connector entries.
- [ ] Silkscreen: refdes all present, off pads, one reading orientation, polarity
      marks visible post-assembly.
- [ ] 3D pass done (collisions, heights, connector clash, antenna region clear).
- [ ] Journal + backup checkpoint DONE.

## §4 Pre-fab-release

- [ ] `gerber_audit.py` exit 0 on the package directory.
- [ ] Copper/mask/silk/paste/outline/drill files present; drill format & units snifffed
      correct; layer count matches stackup claim.
- [ ] Extra empty user-layer gerbers noted (harmless but flag in fab notes or drop).
- [ ] pos.csv + BOM exported from the FINAL board; designator sets reconciled;
      `bom_lint.py` exit 0.
- [ ] Fab notes complete: stackup/finish/copper/qty/impedance/special flags.
- [ ] Netlist→board diff clean (board connectivity == schematic connectivity).
- [ ] Fab capability re-verified against tightest features (date recorded).
- [ ] Human review done where mandated (HV/mains/safety/battery).
- [ ] Bring-up notes written BEFORE ordering (expected voltages per TP, bring-up
      order, flash procedure, failure decision tree).
- [ ] Journal updated; final archive uploaded + VERIFIED (download-back check).
- [ ] Critical release: ≥2 hosts hold the archive (`../../pcb-project-continuity`).

## §5 Schematic-review gate (Phase 3 of pcb-flow)

- [ ] ERC clean or every warning explained in journal.
- [ ] Net names reviewable (functional names, not N0032).
- [ ] Symmetry audit on repeated channels: scripted netlist comparison; all
      asymmetries intended & noted. [ft]
- [ ] Every input has a defined power-up state (pullups/pulldowns; gates
      especially — both-FET-on is smoke).
- [ ] Reset/EN RC ≥ slowest rail ramp incl. soft-start (compute the product).
- [ ] Power-tree check: every load's rail exists; every converter budgeted ≥20%.
- [ ] Every connector pin assigned; no floating connector pins on live nets.
- [ ] USB-C CC terminations present for UFP designs.
- [ ] ICs: decap on every power pin; bulk per rail/cluster.
- [ ] Buck feedback divider math verified (Vref math, not trust).
- [ ] Part symbols pin-verified against datasheet for anything borrowed/variant. [ft]
- [ ] Test strategy exists (what you'll measure at bring-up is decided HERE).
- [ ] Journal + backup checkpoint DONE.
