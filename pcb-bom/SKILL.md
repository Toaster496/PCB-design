---
name: pcb-bom
description: >-
  BOM (bill of materials) creation and component selection for PCBs: required BOM
  columns and why, parts-selection philosophy (derating, package consolidation,
  lifecycle status, second sources), assembly-house BOM/CPL formats (JLCPCB PCBA /
  generic), and the bom_lint.py validation script. Use whenever the user is building
  or reviewing a parts list, "freezing the BOM", asking which parts to choose,
  checking NRND/EOL/lifecycle, alternates/second sources, reel/quantity math,
  DNP handling, LCSC part numbers, or preparing files for a PCBA order — even
  casually like "heres my parts list, is it ok to order".
---

# pcb-bom — BOM creation & parts management

The BOM is the contract between design and reality: an assembly line will build
EXACTLY what the BOM says, not what you meant. Two artifacts matter: the BOM itself
(parts list with full identifiers) and the CPL (centroid/pick-and-place file pairing
footprint-to-position so the machine knows WHERE each part goes).

**The default EDA export is not a BOM.** A typical schematic BOM export (Reference,
Value, Package) omits manufacturer part numbers, supplier ordering codes, lifecycle
status, and DNP flags — none of which a contract assembler will guess correctly.
Normalize into the template below, then lint it.

## 1. Required BOM columns (and why each exists)

| Column | Why |
|---|---|
| Reference | U1, R5, C19… designators; the assembler's placement key + your debug key |
| Qty | per-reference count (1 row may carry many refs) |
| Value | 10k, 100n, 1u_16V — the human-checkable truth; carry voltage/rating suffixes here when the MPN alone doesn't say |
| Footprint | must MATCH the board file's footprint names — mismatch = pick-and-place chaos |
| MPN | manufacturer part number — the unique physical part; absent MPN = the assembler substitutes something |
| Manufacturer | for MPN disambiguation + lifecycle lookups |
| Supplier / Supplier PN | Digi-Key/Mouser/LCSC ordering code (ordering copy-paste, no translation errors) |
| DNP | Do-Not-Populate flag — populated-by-default assumptions cause real smoke |
| Notes | "install exactly one of R16/R17", orientation, alternates, reel size |

Templates: `assets/bom_template.csv`, `assets/cpl_template.csv`, filled example
`assets/bom_example.csv`. One row may carry many references (R5, R6, R7) IF
everything else is identical.

**CPL (centroid) pairing**: the CPL file's footprint/designator set must equal the
BOM's populated set. Mismatched designators between BOM/CPL/board is the #1 PCBA
order rejection cause. Generate CPL from the BOARD (positions live there), BOM from
the SCHEMATIC (values live there), then reconcile by designator.

## 2. Parts-selection philosophy

- **Prefer your approved list first**: parts you (or the suite's users) have used
  and that libraries already model — symbol/footprint errors are costlier than
  part-cost deltas.
- **Consolidate passives**: minimize DISTINCT values and package sizes. E24 series
  for resistors (E96 only where precision demands — each E96 value is another line
  to source/stock); one package size per class (0402 default for machine assembly,
  0603 for any hand rework, 0805/1206 where power/voltage demand). A BOM with 3
  values of 10k in 2 packages is three inventory mistakes deep.
- **Voltage derating**: ≥2× headroom rule of thumb for ceramics on rails (16 V part
  on a 12 V rail is the floor, not the target); electrolytics derate for lifetime
  (voltage + ripple current + temperature). Capacitor DC-BIAS: a "10 µF" 0402 X5R
  at 12 V can present ~3 µF effective — the class-2 ceramics' permittivity falls
  with field; size by the vendor's DC-bias curve, not the case-size headline.
- **Temperature class**: X7R/NP0 for anything timing/precision-adjacent; X5R
  tolerated for bulk decoupling away from heat. Resistor TCR matters in dividers
  that set voltages you measure (100 ppm/°C class vs 25 ppm).
- **Package availability**: avoid exotic footprints with one global source
  (0201, odd metric sizes, custom shields) unless the part demands it.

## 3. Lifecycle & sourcing

- Check status at selection: **Active / NRND (not recommended for new designs) /
  EOL (end of life)** — NRND in a new design = scheduled redesign. Note the date
  checked in the BOM notes; statuses change.
- **Second sources & alternates**: a valid alternate = same footprint (drop-in),
  equal-or-better electricals, same-or-better temp/lifecycle. Record alternates in
  Notes; for every single-source part, name the risk in the journal.
- Supplier PNs for the houses you'll actually use: Digi-Key/Mouser (west), LCSC
  (JLC-adjacent, cheapest for proto PCBA), authorized-distributor rule: gray-market
  brokers are the counterfeit vector — don't route production parts through them.
- Long-lead awareness: magnetics, connectors, and any part with 8-week+ quoted
  lead times get flagged BEFORE BOM freeze (Phase 4 of `../../pcb-flow/SKILL.md`).
- Quantity vs reel math: supplier reel sizes (e.g. 4k/10k for 0402 tapes) vs your
  build quantity — a 250-qty build ordering cut-tape pays per-part premium; note
  the packaging choice in Supplier PN/Notes (Digi-Key: DKT vs DKR suffixes, etc.).

## 4. Assembly-house formats

**JLCPCB PCBA workflow** (typical — verify current program details, they change):
- BOM + CPL uploaded per their template; parts sourced from LCSC (their catalog:
  "Basic" parts = stocked/cheap, "Extended" = surcharge/longer lead; prefer Basic
  where the design allows).
- Their system validates designator/footprint matching; every mismatch = an email
  exchange + days.
- One-sided assembly preferred (each extra side = setup fee); DNP rows are honored
  if flagged.
- Consigned parts: their process has a paperwork + incoming-inspection flow; plan
  the timeline.

**Generic CPL/BOM pairing** (any contract assembler): BOM row set = CPL designator
set = board file's footprints; the CPL carries designator, footprint, mid-X/mid-Y
in mm (ask the assembler's axis/orientation convention — origin top-left vs
center, rotation direction — and match their template).

**DNP handling**: mark DNP in its own column (not by deleting the row — deleted
rows make the designator sets mismatch); the assembler skips them; bring-up
configurations (source-select 0R links: "populate exactly one") live in Notes.

## 5. Cost & risk

- Price breaks (1/10/100/1000) are real: at 100+ boards, passives' per-part price
  halves matter more than the MCU choice sometimes.
- Single-source = schedule risk; connector families = mechanical risk (mating
  cycles, cable-assembly availability — check that the CABLE for your connector is
  also a catalog item, not a custom unicorn).
- Passives-count reduction (merge values) is the cheapest BOM line-item cost
  cutter: fewer reels loaded = cheaper setup at any assembler.

## 6. `scripts/bom_lint.py` — the flagship linter

Stdlib-only CSV tool. Checks: duplicate designators, missing
MPN/Manufacturer/Supplier fields, value-vs-footprint sanity (e.g. a 10uF on an
0402 footprint warns: DC-bias reality check), DNP consistency, distinct-value /
distinct-package consolidation report, empty required columns. Outputs a finding
report + a normalized CSV (sorted, merged reference rows). Contract docstring in
the script; usage:

```
python scripts/bom_lint.py --bom my_bom.csv [--out normalized.csv] [--rules assets/bom_rules.json]
```

Fix every ERROR; review every WARN; THEN call the BOM frozen.

## 7. Selection starter tables

Common passives starter kits (the ~10 values that cover 90% of designs),
regulator/LDO category map, ESD/TVS selection by interface, crystal/resonator
selection notes: `references/selection_tables.md`.

## 8. BOM freeze exit checklist

- [ ] Every row: MPN + Manufacturer + Supplier + Supplier PN present (or DNP).
- [ ] Lifecycle status checked for every ACTIVE-critical part; date recorded.
- [ ] Footprint column matches the board file names EXACTLY.
- [ ] Designator sets match between BOM, CPL, and board.
- [ ] DNP rows flagged with the bring-up plan (what populates instead).
- [ ] Alternates recorded for single-source parts; risk flagged in journal.
- [ ] `bom_lint.py` exit 0.
- [ ] Journal + backup checkpoint (`../../pcb-project-continuity/SKILL.md`).
