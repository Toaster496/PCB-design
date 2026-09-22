---
name: pcb-design-rules
description: >-
  PCB design rules and constraints: net-class organization, creepage and clearance
  derivation from working voltage, trace width vs current and temperature rise,
  via sizing/annular rings/aspect ratios, soldermask and silkscreen rules, thermal
  relief settings, and DFM-safe minimums by fab tier. Use whenever the user asks about
  trace width ("will 8 mil carry 2 amps?"), spacing/clearance for voltage ("how far
  apart for 230V?"), via sizes, annular rings, aspect ratio, net classes, DRC setup,
  constraint files, or is setting up design rules in KiCad/Altium/EasyEDA — also for
  "what should my clearance/width defaults be".
---

# pcb-design-rules — clearances, widths, vias, constraints

Design rules are the contract between your intent and the fab's process. Organize them
as **net classes** (not a single global minimum), so each class of net carries rules
matched to its physics: a 12 V signal and a 3 A motor output and a 90 Ω USB pair have
nothing in common and should never share constraints.

**Every number below carries provenance**: IPC-2221/IPC-2152 (the design standards),
IPC-7351 (land patterns), or "conservative generic default — verify against your fab's
capability page". Where a value is process- or fab-dependent, the METHOD is given so
you can derive or verify it. Never treat any single value as universal law.

## 1. Net classes — the organizing idea

| Net class | Typical clearance | Typical width | Vias | Notes |
|---|---|---|---|---|
| signal (default) | 0.2 mm | 0.2–0.25 mm | 0.3/0.6 | conservative quick-turn-safe defaults |
| power (≤1 A) | 0.2 mm | 0.3–0.5 mm | 0.3/0.6 | see §3 for per-current sizing |
| power (>1 A) | 0.2+ mm | per §3 table / pour | 0.4–0.5+ | pours beat traces at high current |
| high-speed diff | class + pair rules | per fab impedance sheet | 0.3, minimize | intra-pair geometry FIXED |
| RF | 2–3× width to neighbors | 50 Ω per calc | avoid in feedline | see `../../pcb-routing/SKILL.md` |
| high-voltage | per §2 derivation | per §3 | per §2 | creepage governs |

Method: create net classes in the EDA tool from this table, then adjust from the
schematic (assign by net name patterns, e.g. `12V*`, `MOTOR*`). Encode BEFORE placement
(`../../pcb-flow/SKILL.md` phase 5) — rules retrofit is how error storms start.

## 2. Clearance & creepage — derive from voltage

**Clearance** = shortest air distance; **creepage** = shortest distance along a
surface. Creepage ≥ clearance always (surface contamination makes the longer path
fail first). Working voltage > rated may still pass — but design to working voltage,
with transients considered.

Derivation method (cite IPC-2221 §6 Table 6-1 as the generic standard; IEC 62368-1 /
IPC-2221A external tables for product-safety classes):

| Working voltage (DC/peak) | Uncoated external, sea level (B1-type, IPC-2221 generic) | Internal layers / coated |
|---|---|---|
| 0–15 V | 0.05 mm min (use ≥0.2 mm anyway) | same |
| 16–30 V | 0.1 mm (use 0.2) | same |
| 31–50 V | 0.6 mm | 0.25 mm class |
| 51–100 V | 0.9–1.5 mm (conservative: 1.0) | 0.5 mm |
| 101–170 V | 2.0 mm conservative (IPC 6.4 per-row) | 1.0 mm |
| 171–250 V+ | 3.2 mm+ / use product-safety table | 1.5+ mm |

⚠️ These rows are IPC-2221 Table 6-1-style guidance rounded to conservative values —
for a real mains/safety design, read the actual standard rows (condition B1 vs A4 etc.
matter), apply altitude derating (above ~2 km, derate clearance ~per standard's factor),
pollution degree, and require a qualified human review (`references/high-voltage.md`).
Use ≥2× the tabulated minimum for prototype margin where space allows.

Pads-to-board-edge, pads-to-slots, and component-body clearances follow the same
derivation plus mechanical margin. Component-to-component: use courtyards (IPC-7351).

## 3. Trace width & current capacity

Modern standard: **IPC-2152** (the 2009 curve-based standard replacing IPC-2221's
chapter 6 charts). Method: width is set by (a) acceptable temperature rise ΔT, (b)
internal vs external layer (internal runs hotter — less heat-shedding), (c) copper
weight, (d) current. IPC-2221's old curves remain a usable conservative legacy.

Conservative quick-turn defaults (1 oz external copper, ΔT 10 °C, IPC-2152-consistent
rounded — verify with a calculator for your exact case):

| Current | External (1 oz) width | Internal (1 oz) width |
|---|---|---|
| 0.5 A | 0.2 mm | 0.4 mm |
| 1 A | 0.4 mm | 0.8 mm |
| 2 A | 0.8 mm | 1.6 mm |
| 3 A | 1.3 mm | 2.5 mm |
| 5 A | 2.5 mm | pour/planes |
| ≥5 A | pour/planes + stitch vias | pour |

Caveats that matter:
- These are steady-state, ΔT=10 °C, free convection. Enclosed/insulated boards: derate
  (use ΔT budget of your environment, or 5 °C for dense sealed products).
- A pour almost always beats a fat trace at ≥3–5 A: current spreads, heat spreads,
  inductance drops. Stitch multiple vias on transitions (each via has its own current
  rating, §4).
- 2 oz copper roughly halves the widths above (per IPC-2152 family curves — verify).

Full method, internal-layer derating, and pulse/transient handling:
`references/current-capacity.md`.

## 4. Vias

- **Annular ring** (pad radius minus hole radius): the drill registration tolerance
  eats ring on one side. Minimum by tier: budget quick-turn ~0.15 mm ring safe
  (0.1 mm advertised); IPC Class 3 wants ≥0.25 mm-class rings (verify class table).
  Small ring = drill breakout risk on layer transitions.
- **Aspect ratio** = board thickness / drill dia. ≈10:1 typical limit, 8:1 comfortably
  safe for quick-turn (1.6 mm board → 0.2 mm drill is the theoretical floor; 0.3 mm
  is the sane default).
- **Via current capacity** is NOT the trace-width table number: the plated barrel is
  the bottleneck. Rule of thumb (conservative, verify): a 0.3 mm drill / 25 µm
  barrel handles ~1 A at modest ΔT; use multiple vias in parallel for amps-class
  transitions (also lowers inductance). Detailed table: `references/vias.md`.
- **Tenting** (mask over via) — default ON for vias in paste/assembly regions: an
  open via next to a BGA pad wicks solder mid-reflow → starved joint. Tenting is
  free at most fabs.
- **Via-in-pad**: allowed (needed under 0.4–0.5 mm-pitch BGAs and QFN thermal pads),
  but the via must be PLUGGED (epoxy-filled + capped) or the paste steals.
  Budget-tier workaround: dogbone fanout instead (see `../../pcb-routing/SKILL.md`).
- **Thermal vias under exposed pads**: 3×3–5×5 array of 0.3 mm drills under a power
  pad, connecting to the opposite pour — the standard heat path. Solid connection
  (not thermal-relief) from pad to vias; see §6.
- **Stitching vias**: GND-to-GND every ~5–15 mm along plane transitions, board edges,
  and around connectors — cheap EMC insurance (`../../pcb-routing/SKILL.md` ground
  section).

## 5. Soldermask & silkscreen rules

| Rule | Conservative default (verify per fab) |
|---|---|
| Mask dam (web) between adjacent pads | 0.1 mm; below that, mask slivers lift — let mask open merge |
| Mask-to-copper clearance (expansion) | 0.05 mm typical, 0 with tight pitch |
| Silk-to-mask (clearance outside pads) | 0.15 mm so silk doesn't run onto pad openings |
| Silk over pads | NEVER — assembly paste/vision problem |
| Min silk line width | 0.15 mm; text ≥1.0 mm height, ≥0.15 stroke |
| Silk on vias (untented) | avoid — ink webs |

## 6. Thermal relief (zone/pour connection style)

A thermal-relief connection (spokes) exists so soldering iron heat doesn't drain into
the infinite pour and starve the joint — wave/hand-soldered THROUGH-HOLE pads want it.

| Pad type | Connection |
|---|---|
| Hand/wave-soldered TTH Pads | thermal relief: 2–4 spokes, spoke width ≥ 0.3 mm or 60% of pad width (sane defaults; balance: 4 spokes for power) |
| Power/EP pads (thermal path is the POINT) | SOLID connection — relief adds resistance/inductance to the path you designed |
| High-current SMT pads (≥3 A class) | solid, or direct pour entry |
| Shield/shell tabs to GND | solid + adjacent vias |
| Signal SMT pads in a pour | either works; relief eases rework, solid lowers inductance |

(A field-tested pattern from a completed 2-layer power board: forcing SOLID zone
connections on all driver/EP/shield GND pads while leaving hand-soldered connectors
relieved — the asymmetric policy is deliberate and worth encoding as your default.)

## 7. DFM constraints by fab tier

"Design to the cheapest fab you'd actually use": tier A (budget quick-turn) safe
normal = 0.15/0.15 mm trace/space, 0.3 mm drill, 0.15 mm annular ring, 8:1 aspect —
all features ≥20% inside the advertised limit. Tier table + verify procedure:
`../../pcb-board-format/references/fab-capabilities.md`. Castellations, gold fingers
(beveling), edge plating: only with a fab that lists them (and note them in fab
notes, `../../pcb-board-format/assets/fab_notes_template.md`).

## 8. Rule-file management per EDA tool

How to encode all of the above as actual constraints: KiCad net classes + custom
rules, Altium rules wizard/priorities, EasyEDA design-manager, generic (no tool) —
`references/eda-rule-files.md` (variant reference; read only your tool's section).

## 9. `scripts/check_rules.py` — CSV rules-matrix validator

Deterministic gate on your rules table before it enters the EDA tool. It reads the
CSV net-class matrix (`assets/rules_template.csv` format) and checks internal
consistency: min ≤ default ≤ max widths, clearance ≥ fab minimum, class names sane,
duplicate class detection, current-width sanity vs the §3 table, exit codes 0/1/2.
Usage:

```
python scripts/check_rules.py assets/rules_template.csv [--fab-min "0.15,0.15,0.3"]
```

Run it on your edited matrix; fix every finding; THEN enter the rules in the EDA tool.

## 10. High-voltage addendum

Reinforced insulation, slots, encapsulation/potting, corona: `references/high-voltage.md`.
⚠️ HV/mains designs need a qualified human review before fab — an agent can prepare,
never sign off.
