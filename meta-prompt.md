# META-PROMPT — Build a Portable "PCB Design Skills" Suite

> **How to use this file:** Paste everything below the line into any capable
> coding agent (Claude Code, Cursor, Windsurf, Codex CLI, Copilot, Gemini CLI,
> Aider, or a plain chat model with file access). It is fully self-contained —
> the executing AI does **not** need internet access, because the skill format
> specification is embedded here. It is written for an agent that **may** have
> just completed a successful PCB design in its workspace: if one exists, the
> prompt has it mine that real experience into generalized skills — and
> explicitly forbids inventing a project if none exists. The resulting suite
> teaches future agents to keep real projects backed up off-box (encrypted)
> with a living journal.

---

## YOUR MISSION

You are an expert PCB design engineer (15+ years: consumer, industrial, power,
RF, high-speed digital) **and** an expert author of AI "skills" (structured
markdown instruction packs). Your job is to create a complete, production-grade
**suite of PCB design skills** as plain markdown files, following the
**Anthropic Agent Skills format** (the same format used by the `skill-creator`
skill in the `anthropics/skills` GitHub repository, specified in full below).

The suite must teach an AI agent everything needed to take a PCB project from
requirements to fabrication-ready output:

1. **Board format & layout planning** — form factor, outline, stackup, mechanicals, component placement
2. **BOM creation & parts management** — sourcing, normalization, lifecycle, assembly-house formats
3. **PCB design rules** — clearances, trace/via sizing, current handling, DFM constraints
4. **Routing methods** — strategies for power, ground, signal, differential pairs, high-speed, RF
5. **Pitfalls to avoid** — the catalog of classic mistakes, per phase, with review checklists
6. **A meta-skill** — a `pcb-skill-creator` that lets the suite grow (new niche skills created *by* the suite, in the same format)
7. **Project continuity & disaster recovery** — a living project journal plus regular, verified, **encrypted** archive uploads to file hosts capable of >200 MB, with keys stored separately and resumable state, so a lost sandbox/VM/session never loses the project — and a leaked link never exposes it

**Context you may be running in:** a completed, high-quality PCB design may
exist in your current workspace/conversation. **If it does**, it is your
primary source material (Part 0): mine it read-only for battle-tested lessons,
but harvest **generalized engineering, not board trivia** — the suite must
serve any future PCB, not a rerun of one board. **If it does not**, build from
first principles + standards and never fabricate a project, its lessons, or
"field-tested" provenance (Part 0.3).

**Authoring, not performing:** this session produces instruction files. You
are NOT designing a PCB here, not running project management, and not
executing the workflows you document — those get performed later, by agents
using the skills on real projects (possibly you in a fresh session). When in
doubt, ask of every instruction you write: "does this teach a future agent, or
perform work now?" It should teach.

**Hard requirement — portability:** the skills must work in **any coding harness
and with any model**. Pure markdown + YAML frontmatter, relative links only,
Python-3-stdlib-only scripts, zero harness-specific syntax, graceful
degradation when EDA tools are absent.

---

## PART 0 — SOURCE MATERIAL: A COMPLETED PCB PROJECT (IF ONE EXISTS)

**Verify first — do not assume.** Check the workspace/conversation for real
project artifacts (schematic, PCB file, BOM, gerbers, fab correspondence,
design history). Two branches, no third option:

- **A real project exists:** it is source material to be **mined, not
  managed**. Treat it read-only this session — your deliverable is the skills
  suite. The journal/backup/resume behaviors of §2.9 are instructions you
  author for *future agents on their projects*, not something you perform here
  (except the optional 0.1 safeguard).
- **No project exists:** say so plainly in the final report and build from
  first principles + standards (0.3). **Never hallucinate a project:**
  inventing fake board details, fake lessons, or fake "field-tested"
  provenance tags would poison the suite with confident fiction — that is the
  single worst failure mode of this prompt. An honest standards-based skill
  beats a fabricated war story every time.

### 0.1 Inventory the project (read-only — only if it exists)

Survey the design and its history: files, artifacts, phases completed,
decisions made, problems that bit you and how they were fixed. This feeds the
harvest map (0.2).

*Optional courtesy safeguard:* if the completed project exists **only** in
this ephemeral sandbox, has no backup elsewhere, and the user has asked for
protection (or confirms when you offer), take a one-time archive upload using
§2.9's recipes — **encrypted, never plaintext** — before proceeding. Offer it,
do it only on confirmation, and report the URL. Never treat this as the
deliverable; if no host is reachable, print the manual commands a human can
run and move on to authoring.

### 0.2 Harvest lessons — the anti-overfitting discipline

Build a working file `HARVEST_MAP.md` (alongside, NOT shipped inside, the
suite): every notable lesson from the completed project → generalized form →
target skill/reference. Run each lesson through the **generalization ladder**:

| Rung | Lesson type | Treatment in the suite |
|---|---|---|
| 1 | Physics/process-based (return current, loop inductance, etch tolerance) | Universal rule, explained by mechanism |
| 2 | Conditional ("for >3 A rails…", "with 0.5 mm-pitch BGAs…") | Scoped rule with its trigger condition stated |
| 3 | A judgment call/preference that worked on this build | "Field-tested pattern" note, labeled with context |
| 4 | Project-specific fact (that MPN, that outline, that fab's quirk, net names) | ONLY as a labeled worked example — never a rule |

Apply the **different-board test** to every rung-1/2 candidate: "Would this
still hold on a completely different board class (battery BLE sensor vs 24 V
motor driver vs RF front-end)?" If not → scope it explicitly or demote it.

Hard prohibitions:

- Never turn this project's exact values (dimensions, MPNs, stackup, one fab's
  limits) into universal defaults. Defaults come from standards and
  fab-independent reasoning; project values appear only as labeled examples.
- Never embed identifying details (client/company names, proprietary net names,
  unreleased product info) — anonymize worked examples.
- Where a harvested lesson contradicts a standard (IPC-2221/2152/7351), the
  standard wins unless you document it as a deliberate, scoped deviation —
  and then say exactly that.

Provenance is a feature: marking a rule "field-tested on a completed 4-layer
USB-C project" (no identifying detail) adds credibility — but such tags may
ONLY be used for lessons genuinely harvested from the real project (0.1), and
the marker must never narrow the rule's applicability.

### 0.3 If no completed project exists in context

State plainly in the final report: "no source project was present — suite
built from standards and first principles." Skip the harvest map and every
"field-tested" tag. Do not simulate, invent, or gesture at a project that
isn't there. Everything else in this prompt still applies — including
encoding the full continuity discipline into the suite (§2.9), since future
users will bring their own real projects to it.

---

## PART 1 — THE SKILL FORMAT CONTRACT (follow exactly)

This is the format specification, adapted from `anthropics/skills` →
`skills/skill-creator`. Do not fetch it; everything you need is here.

### 1.1 Anatomy of one skill

```
skill-name/
├── SKILL.md              (required)
│   ├── YAML frontmatter  (name, description required)
│   └── Markdown body     (instructions, <500 lines ideal)
├── references/           (optional — docs loaded into context as needed)
│   └── *.md              (each >300 lines MUST include a table of contents at top)
├── scripts/              (optional — executable helpers for deterministic tasks)
│   └── *.py              (Python 3, stdlib only, each with a usage docstring)
├── assets/               (optional — templates used in output: CSV/XLSX templates, layer-stack tables)
└── evals/
    └── evals.json        (3+ realistic test prompts per skill — see §4.3)
```

### 1.2 Frontmatter rules

```yaml
---
name: skill-name          # MUST equal directory name; lowercase letters, digits, hyphens; ≤64 chars
description: >-           # ≤1024 chars; third person; WHAT it does + WHEN to trigger.
  ...                     # Triggering info goes ONLY here, never in the body.
---
```

- Make descriptions **"pushy"**: models under-trigger skills, so enumerate the
  situations, phrasings, and synonyms that should activate it ("Use this
  whenever the user is doing X, Y, or Z, even if they don't say the word
  'PCB' explicitly").
- Optional extra keys (e.g. `license`, `version`) are allowed — harnesses
  ignore unknown keys. Do **not** use harness-specific keys
  (`allowed-tools`, etc.) in required skills; if you add them, note in the
  suite README that they're optional metadata.

### 1.3 Progressive disclosure (the three-level loading model)

1. **Metadata** (name + description) — always in context (~100 words). Keep it dense.
2. **SKILL.md body** — loaded when the skill triggers. Keep **under 500 lines**.
   Workflow, decision tables, the most-used rules. If you approach the limit,
   push detail into `references/` with clear pointers ("for voltage-based
   clearance tables, read `references/clearance.md`").
3. **Bundled resources** — read/executed as needed, unlimited size. Scripts can
   run **without** being loaded into context; say when to run them and what
   they output.

**Domain organization:** when a skill spans variants (e.g., per-EDA-tool or
per-fab instructions), use one reference file per variant and have SKILL.md
contain a selection table so the model reads only the relevant file:

```
pcb-design-rules/
├── SKILL.md              (workflow + which reference to read when)
└── references/
    ├── kicad.md
    ├── altium.md
    ├── easyeda.md
    └── generic.md
```

### 1.4 Writing standards

- **Imperative form** for instructions ("Route the differential pair…", not
  "The pair should be routed…").
- **Explain the *why*** — modern models generalize far better when they
  understand the reason (physics, fab process, assembly process) than when
  given rigid MUSTs. If you catch yourself writing ALL-CAPS ALWAYS/NEVER,
  reframe with reasoning. A few true hard constraints (safety, DRC minimums)
  are fine.
- **Tables over prose** for numbers (clearance matrices, trace-width/current,
  drill sizes, via aspect ratios).
- **Good/Bad example pairs** for layout and routing decisions, formatted as:

  ```markdown
  **Example 1:**
  Input: 4-layer board, STM32 + USB-C + buck regulator, 50×80 mm
  Output: [stackup table] [zone plan] [placement order] …
  ```

- **Provenance for every number.** Cite the standard (IPC-2221, IPC-2152,
  IPC-7351, IPC-A-610, J-STD-001) or the fab (JLCPCB, PCBWay, Eurocircuits,
  OSH Park) or label it "conservative generic default — verify against your
  fab's capability page." **Never invent precise-looking numbers without a
  source label.** Where values are fab- or voltage-dependent, give the method
  plus a safe starting range.
- **Self-contained skills.** A harness may load one skill without its
  siblings; repeat (briefly) anything essential rather than only cross-linking.
- **Script contracts.** Every bundled script begins with a docstring contract
  in exactly this shape — it exists so any agent can use, debug, or extend the
  script without reading its source, and so `validate_suite.py` can enforce it:

  ```python
  """<one-line purpose>

  INPUTS:  args / env vars / files consumed (with formats)
  OUTPUTS: files written, stdout shape, side effects (network: yes/no)
  EXIT:    0 ok | 1 bad input | 2 missing tool/env | 3+ documented domain codes
  EDGE:    empty/huge inputs, offline, missing optional tool, corrupt file,
           re-run behavior (idempotent? overwrite? append?)
  NON-GOALS: what this script deliberately does NOT attempt
  """
  ```

### 1.5 Harness-portability rules (non-negotiable)

- Plain UTF-8 markdown; no HTML, no vendor markup, no custom tags.
- All links **relative** (`references/x.md`), resolvable from the skill directory.
- Scripts: Python ≥3.8, **stdlib imports only** — a bundled script may never
  `import` a third-party package. Scripts MAY *detect and shell out to*
  optional external tools (`kicad-cli`, `openssl`, `age`, `gpg`, `curl`,
  `split`) and must degrade gracefully when they are absent. Reference docs
  may *mention* third-party clients (e.g., TLS-impersonating HTTP libraries
  for Cloudflare-blocked hosts) strictly as optional manual tactics for
  humans/environments that already have them — never as script dependencies.
  Scripts are deterministic, with `--help` support and documented exit codes.
  **No network calls** — with one carve-out: the optional backup script of
  `pcb-project-continuity` (§2.9) may use the network, but must degrade
  gracefully: host fallback chain, clear errors, and when offline/blocked it
  prints ready-to-run manual `curl` commands instead of failing silently.
- Reference EDA tools only as *variants* (KiCad / Altium / EasyEDA / generic);
  the core instruction must work with none of them installed (the agent may
  only be advising a human or editing netlists/text files).
- Each skill must also survive the "flatten test": if its SKILL.md body is
  pasted into any system prompt, it still gives complete, usable guidance.

### 1.6 Safety

No malicious content, no exploit code, nothing surprising (the "principle of
lack of surprise"). Skills advise on hardware design only.

---

## PART 2 — THE SUITE: SCOPE OF EACH SKILL

Create these **9 skills** under a top-level `pcb-skills/` directory. Each scope
below lists the topics that MUST be covered — distribute them between SKILL.md
(hot path) and `references/` (deep detail) per §1.3. Merge or split only with a
stated justification in your final report.

### 2.1 `pcb-flow` — orchestrator / entry point

The conductor skill. Covers the end-to-end design flow and routes the agent to
the right sibling skill at each phase:

- Phases: requirements → architecture/block diagram → schematic capture →
  schematic review → BOM freeze → board setup (outline/stackup/rules) →
  placement → routing → DRC/DFM/ERC cleanup → review → fab package
  (Gerbers/drill/pick-and-place/BOM) → assembly bring-up notes → revision loop.
- A phase table: phase | questions to answer | exit criteria | which skill to
  load next | typical artifacts produced.
- How to run a design review at each gate; what "done" means per phase.
- Continuity hooks: every phase gate's exit criteria include "journal updated +
  verified backup uploaded" (procedure in `pcb-project-continuity`).
- Requirement-gathering interview script for the agent (application, size,
  power, environment, cost target, volume, fab/assembly house, EDA tool,
  standards to meet).
- Description must trigger on generic phrases like "I'm designing a PCB",
  "help me with my board", "starting a new hardware project".

### 2.2 `pcb-board-format` — board format, outline, stackup, mechanicals

- Form factor & outline: enclosure-driven design, board-to-board connectors,
  standard sizes, irregular outlines, rounded corners (and why), cutouts/slots
  and their clearance rules.
- Mechanicals: mounting-hole sizes (M2/M2.5/M3), plated vs non-plated,
  keepout rings around holes, edge clearance for connectors and overhanging
  parts, board thickness vs connector fit, height restrictions/z-profiles.
- Stackup selection: 1/2/4/6/8-layer decision tree by complexity, signal
  speed, power density, cost; canonical 4-layer (SIG-GND-PWR-SIG) and 6-layer
  stackups with rationale; layer ordering rules; why signal layers need
  adjacent reference planes; controlled-impedance stackup planning and how to
  ask a fab for their impedance calculator results.
- Copper weights, dielectrics (FR-4, TG ratings), finishes (HASL/ENIG/OSP/
  immersion silver) — selection table with cost/reliability/solderability
  tradeoffs.
- Panelization: breakaway rails, V-score vs mouse-bites vs stamp holes,
  panel sizing for assembly, tooling holes, fiducials (global + local).
- Fab documentation layers: silkscreen conventions, board outline layer
  discipline, drill drawings, fab notes template (put a fillable template in
  `assets/`).
- Reference file: example fab capability tables (a budget quick-turn fab, a
  premium fab) with the caveat "verify current values on the fab's site".
- Standards to cite: IPC-2221 (generic design), IPC-6012 (qualification).

### 2.3 `pcb-layout` — component placement & board zoning

- Zoning methodology: partition the board into functional zones (input/
  connector edge, power conversion, digital/MCU, RF, analog, mechanical);
  flow-based placement (signal enters → processed → exits) to minimize
  crossings; dirty/clean separation (switching noise vs sensitive analog).
- Placement order workflow: mechanicals & connectors first → big/anchor parts
  (ICs, magnetics, crystals) → decoupling & passives around them → test points
  → cosmetics; iterate with the ratsnest as feedback.
- Decoupling capacitor placement: why via-to-plane distance and loop area
  dominate; local vs bulk; per-pin placement rules; capacitor orientation to
  shorten loop.
- Thermal placement: hot parts (regulators, MOSFETs, RF PAs) spread out, away
  from heat-sensitive parts (electrolytics, crystals, sensors); airflow
  direction awareness; copper pour as heatsink; keepout under antennas.
- EMC-driven placement: connectors at zone boundaries, filter components
  (ferrites, TVS, common-mode chokes) placed AT the boundary where the signal
  crosses, oscillator/crystal close to the IC with ground guard and no
  underlying pours on adjacent layers, sensitive traces away from board edges.
- Assembly & serviceability: hand-solder access, rework clearance, connector
  cable-bend radius, polarity/orientation consistency, fiducials, test points
  (minimum per net strategy), silkscreen readability and never-on-pad rules,
  courtyard/IPC-7351 spacing for manufacturability.
- Reference file: placement checklists per board archetype (MCU board, SMPS
  board, RF board, sensor front-end) + a `references/gallery.md` describing
  classic placement patterns in words/ASCII diagrams.

### 2.4 `pcb-design-rules` — design rules & constraints

- Net classes as the core organizing idea: power, signal, high-speed,
  differential, RF, high-voltage — with rule sets per class.
- Clearance: how to derive spacing from working voltage (creepage vs
  clearance, IPC-2221 Table 6.1 / IEC 62368-1 as the standards to cite),
  internal vs external layers, coated vs uncoated, altitude derating note;
  component-to-board and pad-to-pad clearances.
- Trace width: current vs temperature rise (IPC-2152 as the modern standard,
  IPC-2221 curves as legacy), external vs internal copper, starting widths
  for common currents; when to pour polygons instead.
- Vias: drill size vs annular ring (and why ring matters — drill registration
  tolerance), via current capacity rule of thumb vs a plated barrel, aspect
  ratio limits (≈10:1 typical, verify per fab), tenting, via-in-pad (and when
  it needs plugging/capping), thermal vias under exposed pads (array sizing
  guidance).
- Soldermask & silk rules: mask dam widths between pads, mask-to-copper
  clearance, silk-to-mask and silk-to-pad clearance, minimum silk line width.
- Thermal relief: spoke count/width defaults and when to use solid connections
  (high current) vs relieved (wave solder).
- DFM constraints by fab tier: minimum trace/space/drill/annular ring for
  budget quick-turn vs premium; "design to the cheapest fab you'd actually
  use" philosophy; castellated holes, edge connectors (gold fingers, beveling).
- Rule-file management: how to encode all this in each EDA tool (variant
  reference files), and a script `scripts/check_rules.py` that validates a
  generic CSV rules matrix (net class × parameter) for internal consistency
  (e.g., min width ≤ default ≤ max, clearance ≥ fab minimum).
- High-voltage addendum reference: reinforced insulation, slots, corona,
  potting, conformal coating, and the warning that HV design needs qualified
  human review.

### 2.5 `pcb-routing` — routing strategy & techniques

- Order of operations: fanout/escape first (BGA strategies by pitch: dogbone,
  via-in-pad, channel escape), critical signals (clocks, diff pairs, RF)
  next, then power, then general signal; never auto-route blind — explain why
  interactive routing with the ratsnest as a plan beats autorouting, and when
  an autorouter pass is acceptable.
- Ground strategy (the single most important section): solid ground planes,
  return current follows the path of least impedance directly under the
  signal (explain with physics), why plane splits under traces are usually
  wrong, stitching vias along return-path discontinuities and board edges,
  ground islands and why floating copper is bad, single-point vs multipoint
  grounding decision.
- Power distribution: planes vs wide traces vs polygon pours; PDN basics
  (target impedance intuition, decoupling hierarchy: bulk → mid → local);
  current loop area minimization for switching converters (hot loops first —
  name them: buck input loop, output loop, SW node); star routing vs daisy
  chain vs plane for different loads; Kelvin connections for sense lines.
- Signal routing geometry: 45° or curved corners and why (impedance
  continuity, acid traps in etching), trace width consistency for impedance,
  avoiding stubs (or T-taps only where harmless), crosstalk control (3W rule,
  spacing, reference-plane integrity), guard traces with stitched vias.
- Differential pairs: intra-pair spacing consistency, coupling, intra-pair
  length matching (skew budget reasoning), inter-pair separation, never
  splitting pairs across plane gaps, per-protocol targets (USB 90Ω, Ethernet
  100Ω, LVDS 100Ω — mark as "typical, check protocol/fab").
- Length matching & timing: which buses need it (DDR, parallel buses, some
  SerDes), matching groups/tolerance reasoning (why ±X mil exists — derive
  from timing budget, don't just parrot numbers), serpentine routing rules
  (amplitude ≥3× width to avoid coupling, prefer accordion on the source end).
- High-speed & RF addendum reference files: controlled impedance workflow
  (ask fab → constrain → verify), reference plane changes and via stitching,
  RF transmission line types (microstrip/CPW), RF routing do's (short,
  straight, grounded coplanar) and don'ts, antenna keepout and feedline rules.
- Post-route: DRC sweep strategy, fixing violations without creating new
  ones, removing dead copper, silkscreen cleanup, final visual review passes
  (top/bottom/each layer, 3D check for collisions).
- Variant reference files for tool mechanics: `references/kicad.md`
  (interactive router modes, push/shove, diff-pair tool, length tuning),
  `references/altium.md`, `references/generic.md`.

### 2.6 `pcb-bom` — BOM creation & component selection

- BOM from schematic: required columns (Reference, Qty, Value, Footprint,
  MPN, Manufacturer, Supplier, Supplier PN, DNP flag, Notes) and why each
  exists; reference designator grouping; assets/ contains
  `bom_template.csv` and `cpl_template.csv` (centroid/pick-and-place) plus a
  filled example row set.
- Parts selection philosophy: prefer parts already on your approved list;
  consolidate passives (minimize distinct values: E24/E96 discipline, one
  package size per class where possible — e.g. 0402 default, 0603 for
  hand-soldering), voltage derating (≥2× headroom rule of thumb, ceramic
  DC-bias derating — explain that 10µF 0402 X5R @ 12V may be 3µF effective),
  temperature class (X7R vs X5R, resistor TCR where it matters), package
  availability (avoid exotic footprints).
- Lifecycle & sourcing: check Active/NRND/EOL status, second sources and
  alternates (what makes a valid alternate: same footprint, equal-or-better
  electricals, same or better temp/lifecycle), supplier part numbers for
  Digi-Key/Mouser/LCSC, avoiding counterfeit-prone parts from gray market,
  long-lead-time awareness for magnetics/connectors.
- Assembly-house formats: JLCPCB PCBA workflow (LCSC part numbers, "basic
  vs extended" parts concept — mark as "verify current program details"),
  generic CPL/BOM pairing, one-sided assembly considerations, DNP handling.
- Cost & risk: price breaks vs volume, single-source risks, connector
  mechanicals (mating cycles, availability of cable assemblies), passives
  count reduction.
- Script: `scripts/bom_lint.py` — stdlib-only CSV tool that checks: duplicate
  reference designators, missing MPN/supplier fields, value/footprint
  mismatches against a rules table, distinct-value count report, DNP
  consistency, and outputs a corrected/normalized CSV. This is the flagship
  script of the suite; make it robust and well-tested.
- Reference: `references/selection_tables.md` — common passives starter kits
  (the 10 values that cover 90% of designs), common regulators/LDOs categories,
  ESD/TVS selection by interface, crystal/resonator selection notes.

### 2.7 `pcb-pitfalls` — mistakes catalog & review checklists

The hard-won-knowledge skill. Organized as: **phase → pitfall → symptom →
why it happens → fix/prevention**. Minimum coverage:

- *Board setup:* wrong layer count for the job; outline on wrong layer;
  slots without copper clearance; mounting hole keepout violated; fiducials
  missing/obstructed; panelization that assembly house can't handle.
- *Placement:* decoupling caps too far / wrong via pattern; crystal too far
  from MCU or with traces under it; connector orientation fighting the cable;
  hot parts clustered; test points forgotten until after routing; antenna
  keepout encroached by ground pour.
- *Routing:* 90° corners on RF/high-speed; return path crossing plane split;
  long stubs; diff pair split across layers without stitching; length matched
  by snaking right at the receiver (crosstalk); power routed as thin trace
  when current demands pour; switching loop area enormous; ground via
  count too low at plane transitions; acid traps / starved thermals (etch
  artifacts) left in.
- *Rules/DFM:* designing below fab minimums then paying the "capability
  surcharge"; annular ring too small (drill breakout); mask dams that can't
  be printed between fine-pitch pads; silkscreen over pads; un-tented vias in
  paste area causing solder wicking.
- *BOM/sourcing:* NRND parts designed in; single-source connector; wrong
  supplier PN (reel size vs qty); MPN missing so assembler guesses; polarized
  parts without orientation marks; mixing 0402 and 0201 needlessly (assembly
  cost).
- *Solder/assembly:* tombstone-prone two-pad passives without thermal
  balance; heavy parts with no mechanical anchor; BGA with via-in-pad
  un-plugged; no rework access under big shields.
- *EMC/ESD:* ESD protection placed after the sensitive IC instead of at the
  connector; filter ground return long and inductive; enclosure seam/gap
  resonances ignored; shield cans without grounding stitches.
- Deliverables inside the skill: `references/checklists.md` (per-phase gate
  checklists: post-stackup, post-placement, post-route, pre-fab-release),
  `references/pitfalls.md` (the full catalog with the 5-field structure),
  and a script `scripts/gerber_audit.py` (stdlib-only) that sanity-audits a
  released fab package: file presence (copper layers, mask, silk, paste,
  outline, drill), drill file format/units sniffing, layer count vs stackup
  claim, and a printable pre-release checklist. Keep it heuristic and clearly
  documented — it's a smoke test, not a full CAM verifier.
- The SKILL.md body: top-20 most expensive mistakes (ranked by blast radius)
  + how to run a structured self-review + when to demand a human review.

### 2.8 `pcb-skill-creator` — the meta-skill (suite extender)

A skill whose purpose is creating NEW pcb-* skills (e.g. `pcb-flex-rigid`,
`pcb-motor-drives`, `pcb-battery-management`, `pcb-audio`) so the suite can
grow without re-deriving conventions:

- Embeds a condensed copy of this format contract (§1) as
  `references/skill-format.md` so it works standalone.
- Workflow: capture intent (what task, when to trigger, expected outputs) →
  interview on edge cases → pick scope boundaries vs existing siblings
  (avoid overlap; add cross-links in `pcb-flow` and sibling descriptions) →
  draft SKILL.md → add references/scripts/assets → write evals → self-review
  against the acceptance checklist (§4) → iterate with user feedback.
- Includes the "generalize from feedback" principle: fix root causes and
  explain the *why*, don't overfit to test cases or pile on rigid MUSTs.
- Description triggers: "make a new pcb skill", "extend the pcb suite",
  "turn this PCB workflow into a skill".

### 2.9 `pcb-project-continuity` — journal, backups, disaster recovery

The suite's insurance policy: sandboxes/VMs die, sessions get truncated, and
hardware projects live for weeks. This skill keeps all project state durable
and resumable whenever an agent uses the suite on a real project — you are
authoring these behaviors as instructions, not performing them in this
session. It must cover:

- **The living journal** — `PROJECT_JOURNAL.md` at the project root, updated at
  every checkpoint (not at the end!). Template in `assets/journal_template.md`
  with these sections: Snapshot (date, phase, latest backup URL) · Done so far
  (with pointers to artifacts) · In progress · **Todo list** (prioritized, each
  with an acceptance criterion) · Decision log (decision | why | alternatives
  rejected | when to revisit) · **Project-specific pitfalls & things to avoid**
  (the mistakes THIS board actually made or nearly made — this list only ever
  grows) · Open questions & risks · **Resume playbook** (exactly what a fresh
  agent with zero context must read/open/do next) · Backup manifest.
- **Checkpoint policy — when to back up:** at every `pcb-flow` phase gate;
  before any risky bulk operation (autoroute pass, global DRC/class change,
  big refactor, library migration); every ~1–2 h of active work on long runs;
  and immediately whenever the journal's "next step" is destructive. Each
  checkpoint = journal update FIRST, then archive, then upload, then verify,
  then index.
- **Archive discipline:** what goes in (schematic, PCB, libraries, BOM/CPL,
  gerbers, journal, rules files, this project's harness exports); packing
  (`tar.gz`; full projects commonly exceed **200 MB** — the host chain must
  cope, never assume small); `sha256` of every archive; when a host's limit is
  below the archive size, chunk with `split -b 1900M` and list parts + order +
  per-part hashes in the manifest, with the `cat part_* > archive.tar.gz`
  restore recipe.
- **Encrypt BEFORE upload — mandatory default, fail closed.** Every host in
  the matrix is public and link-addressable: possession of the URL IS access.
  PCB projects are frequently proprietary or client IP, so the skill must
  treat plaintext upload as a data breach. Rules to encode:
  - Encrypt every archive (AES-256) using whichever tool is available, probed
    in order: `age` → `openssl enc -aes-256-cbc -pbkdf2` → `gpg -c` → Python
    `cryptography` (if importable in the environment; stdlib `zipfile` cannot
    WRITE encrypted archives — don't try). Record the method in `BACKUPS.md`.
  - **Key separation:** generate a fresh random key/passphrase per archive;
    never store it in or beside the archive. Key policy tiers (`--key-policy`):
    `split` (default) — upload the key as a tiny separate file to a *different*
    host than the archive, and record both URLs in `BACKUPS.md`, so a future
    harness can fetch both and decrypt without a human; `human` — print the
    key once for offline safekeeping (strongest; recovery impossible without
    the human — required default when the journal flags client IP);
    `plaintext` — refuse unless the user explicitly passes
    `--allow-plaintext` AFTER the tool prints an IP-exposure warning.
  - If **no** encryption tool is available: do not upload (fail closed) —
    print ready-to-run manual encrypt+upload commands instead.
  - `BACKUPS.md` + journal hold the map (which archive where, which key where,
    method, sha256) — they are project-internal and must never themselves be
    uploaded in plaintext; the dual-track paste below carries them safely.
- **Host matrix + upload recipes** — `references/hosts.md`. Seed it with this
  known-good field data (re-verify limits/retention live if you have web
  access; otherwise mark rows "unverified — test before relying"):

  | Host | Upload recipe (essentials) | Max size | Retention | Gotchas (field-tested) |
  |---|---|---|---|---|
  | gofile.io | `GET https://api.gofile.io/servers` → multipart POST field `file` to `https://{server}.gofile.io/contents/uploadfile` | large files OK | deletes after ~10 days with no downloads | inactivity expiry — schedule re-uploads; response JSON includes `md5` — verify with it |
  | catbox.moe | form POST `reqtype=fileupload` + `fileToUpload=<file>` to `https://catbox.moe/user/api.php` | 500 MB | permanent | rejects datacenter/VPN IPs (`HTTP 412 "Invalid uploader"`) — works from residential lines only |
  | filebin.net | `curl -T archive.tar.gz https://filebin.net/{bin}/{name}` (client picks the bin id) | large OK | short, inactivity-based — verify | the bin id is the only secret; no auth needed |
  | pixeldrain | multipart POST field `file` to `https://pixeldrain.com/api/file` | ~10 GB | inactivity-based — verify | API may demand an (anonymous) token now — verify before relying |
  | transfer.sh | `curl -T file https://transfer.sh/{name}` | verify (historically GBs) | verify | service has been flaky/for-sale; treat as last resort |
  | litterbox.catbox.moe | like catbox + `time=72h` | 1 GB | 72 h | emergency hand-offs only — expires |
  | PrivateBin (`never` instance) | JSON POST of AES-GCM-encrypted payload, key lives in the URL fragment; protocol differs per major version — inspect the instance's JS | small (text) | permanent on `never` instances | ideal for a journal-only copy alongside the big archive; server sees only ciphertext |

  Rules to encode in the skill: **verify every upload** (download back, or
  compare the host-provided checksum, or at minimum a `HEAD`/size check);
  **never trust a single host** — critical releases get ≥2 copies on different
  hosts; **assume every host is public** — obscurity of a URL is not access
  control, encryption is (see above); **probe with a tiny test file before
  relying on any host from a new environment**, and record the probe result +
  date in the journal; Cloudflare challenges can sometimes be passed with
  TLS-impersonating HTTP clients — document that as an optional *manual*
  tactic for environments that already have such a client, never as a script
  dependency (§1.5); **log expiry semantics in `BACKUPS.md`** so a future
  session knows when a link dies and must re-upload.
- **`scripts/backup.py`** (the §1.5 network carve-out; stdlib imports only,
  shells out to detected encryption/upload tools): packs → hashes →
  **encrypts (fail closed if no crypto tool)** → handles key policy
  (`split`/`human`/`plaintext`-with-warning) → walks the host fallback chain
  (archive and, for `split`, the key file to a *different* host) → verifies →
  appends to `BACKUPS.md` index (date | phase | host | URL | size | sha256 |
  cipher+method | key location/policy | expiry note) → refreshes the journal
  Snapshot section. Flags: `--dry-run`, `--hosts`, `--journal`, `--split-at`,
  `--key-policy`, `--allow-plaintext`. When every host fails: exit non-zero
  AND print ready-to-run manual commands for a human with a residential
  connection. Full contract docstring per §1.4.
- **Journal dual-track:** the journal (plus the current `BACKUPS.md` index) is
  inside every big archive AND gets uploaded as a standalone copy to a
  permanent paste host (PrivateBin `never` instance or equivalent — itself
  end-to-end encrypted, key in the URL fragment) after each phase gate — so
  the recovery map survives even when every big-file link has rotted.
- **Resume playbook** — how a fresh agent in a fresh VM recovers: get newest
  archive URL (+ key URL when policy is `split`) from `BACKUPS.md`/dual-track
  journal copy → download archive and key from their respective hosts →
  verify sha256 → decrypt (method recorded in the index) → unpack → **read
  `PROJECT_JOURNAL.md` first** → follow its Resume playbook section → continue
  work. The journal must be written so that a capable model with zero prior
  context can resume without asking questions.
- Description triggers: "back up the project", "checkpoint", "save progress",
  "upload the project files", "I lost the sandbox/VM", "resume where we left
  off", "restore the project", "update the journal", "what's the project
  status/todo".

---

## PART 3 — SUITE-LEVEL DELIVERABLES

At the top level of `pcb-skills/`:

1. **`README.md`** — what the suite is, skill index table (skill | one-line
   purpose | when it triggers), dependency notes (Python ≥3.8; optional:
   kicad-cli), license (MIT unless the user specifies otherwise).
2. **`INSTALL.md` — harness installation matrix.** Concrete instructions for
   each harness (verify against the harness's current docs if you have web
   access; otherwise include the generic fallback and label version-specific
   paths "verify current convention"):
   - **Claude Code / Claude.ai:** copy skill folders to `~/.claude/skills/`
     (personal) or `<project>/.claude/skills/` (project); on Claude.ai upload
     the skill folder/zip in Settings → Capabilities → Skills.
   - **Cursor:** reference skills as project rules (`.cursor/rules/*.mdc`)
     or @-mention the SKILL.md files; include a generated rules variant.
   - **Windsurf:** `.windsurf/rules/` equivalent.
   - **Codex CLI / AGENTS.md harnesses:** add pointers in `AGENTS.md`.
   - **GitHub Copilot:** `.github/copilot-instructions.md` pointer pattern.
   - **Any other agent / plain chat:** paste the flattened export (below).
3. **`scripts/export_for_harness.py`** (suite-level, stdlib-only) — flattens
   a chosen skill (SKILL.md + selected references inlined) into:
   (a) one self-contained markdown for system-prompt pasting,
   (b) a Cursor/Windsurf-style rules file, (c) an AGENTS.md fragment.
   Validates frontmatter and link integrity while it's at it.
4. **`scripts/validate_suite.py`** (suite-level, stdlib-only) — runs the whole
   acceptance checklist (§4.1/§4.2) mechanically: frontmatter presence and
   key constraints (name ≤64 chars matching dir, description ≤1024 chars),
   SKILL.md line counts, reference TOC requirement, relative-link resolution,
   script syntax check (`py_compile`), **script contract docstring presence
   (INPUTS/OUTPUTS/EXIT/EDGE/NON-GOALS per §1.4) and a scan for third-party
   imports**, evals.json schema. **Run it yourself and iterate until it passes
   clean.**

---

## PART 4 — PROCESS YOU MUST FOLLOW

### 4.1 Order of work

0. **Inventory & harvest (Part 0):** verify whether a completed project
   actually exists — never assume or invent one. If it does: survey it
   read-only and start `HARVEST_MAP.md` — each lesson → generalized form →
   target skill (Part 0.2); take the optional project safeguard only under
   0.1's conditions and with user confirmation. If it does not: note that and
   proceed per 0.3. Then move straight into authoring: you are building
   skills, not running a design or project-management session.
1. **Clarify (only if interactive):** ask the user, in ONE consolidated
   message, at most 5 questions: (a) primary EDA toolchain (KiCad / Altium /
   EasyEDA / mixed / none), (b) typical board classes (MCU+digital / power /
   RF / mixed), (c) typical fab & assembly house, (d) install targets
   (which harnesses), (e) continuity preferences: file hosts you trust / know
   are reachable from this environment, and any confidentiality limits on
   anonymized examples harvested from the completed project. If no answer is
   possible (headless run), proceed with defaults: KiCad-first variants +
   generic fallbacks, all board classes, budget quick-turn fab assumptions,
   all harnesses, host chain gofile → filebin → catbox with mandatory
   encryption and `split` key policy (journal dual-tracked to a PrivateBin
   `never` instance), full anonymization.
2. **Research (only if you have web access):** pull current capability tables
   from JLCPCB/PCBWay, current skill-format docs from
   `github.com/anthropics/skills`, and current size/retention limits for the
   §2.9 host matrix; correct the embedded specs if upstream changed, and note
   the divergence in your final report. Without web access, rely on §1 and
   §2.9 exactly, marking host rows "unverified — probe before relying".
3. **Build in this order** (each depends on the previous for cross-links):
   `pcb-flow` skeleton → content skills (2.2–2.7) → `pcb-project-continuity`
   → `pcb-skill-creator` → suite-level deliverables (Part 3) → fix all
   cross-links → run `validate_suite.py` → run `export_for_harness.py` smoke
   test. **Persist incrementally — this build is bigger than one guaranteed
   session:** write each skill's files to disk as soon as it is finished
   (never batch-write at the end). Maintain a small `BUILD_STATE.md` at the
   suite root (skills done | in progress | next | open issues) and update it
   at every skill boundary, so any fresh session — or the user on another
   machine — can resume exactly where you stopped. If the user requests a
   subset (e.g., "routing + BOM only"), deliver that subset at full quality
   and record the remainder as next steps in `BUILD_STATE.md` rather than
   diluting everything. If the environment is ephemeral and the run is long,
   an occasional lightweight snapshot of the growing tree is sensible build
   hygiene — keep it cheap and unobtrusive; it never displaces authoring.
4. **Self-review pass:** re-read every SKILL.md with fresh eyes against §4.2
   and the Part 0.2 anti-overfitting rules (generalization ladder,
   different-board test, anonymization). Tighten, cut what doesn't pull its
   weight, ensure every "why" is explained.
5. **Final report:** file tree, per-skill summary table (name | lines in
   SKILL.md | references | scripts | evals), validation output, harvest-map
   summary (how many lessons landed where, at which rung — or "no source
   project" statement), any assumptions you made, the `BUILD_STATE.md`
   pointer, and — if the optional safeguard or build snapshots were taken —
   those URLs with sha256 and expiry notes.

### 4.2 Acceptance checklist (must all pass before you declare done)

- [ ] Part 0 honored: project existence **verified, never assumed** — if one exists: inventoried read-only, `HARVEST_MAP.md` complete, "field-tested" tags used only for genuinely harvested lessons; if none: report says so and the suite contains zero fabricated project references; optional safeguard performed only under 0.1's conditions (and if so: encrypted, uploaded, verified, reported)
- [ ] Every harvested lesson passed the generalization ladder and the different-board test; no board-specific value presented as a universal rule; no identifying details anywhere in the suite
- [ ] Directory layout exactly per §1.1; every skill has valid frontmatter (§1.2)
- [ ] Every `description` is third-person, ≤1024 chars, pushy with explicit triggers
- [ ] Every SKILL.md body <500 lines; every reference >300 lines has a TOC
- [ ] All internal links relative and resolving; no broken sibling cross-links
- [ ] All scripts: Python 3, stdlib **imports** only (external tools via detect-and-shell-out), `--help`, `py_compile` clean, and each starts with the §1.4 contract docstring (INPUTS/OUTPUTS/EXIT/EDGE/NON-GOALS); no network except `pcb-project-continuity/scripts/backup.py`, which must fail gracefully and print manual fallback commands
- [ ] `pcb-project-continuity` complete: journal template (assets/), host matrix + upload recipes + probe/verify rules (references/hosts.md), **encrypt-before-upload mandated with fail-closed behavior, per-archive keys, `split`/`human`/`plaintext` key-policy tiers**, `backup.py` with fallback chain, chunking recipe for >200 MB archives, `BACKUPS.md` index format (incl. cipher + key location), resume playbook covering key retrieval + decryption — all as *instructions for future agents*, none of it performed on the user's project during authoring (except the optional 0.1 safeguard)
- [ ] `BUILD_STATE.md` exists at the suite root and is current (resumability: a fresh session can continue the build from it)
- [ ] No harness-specific syntax anywhere in skill content; flatten test (§1.5) passes for each SKILL.md
- [ ] Every numeric value has provenance (standard, named fab/host, or "conservative default — verify")
- [ ] Zero invented precise numbers presented as facts; HV/safety topics carry human-review warnings
- [ ] `validate_suite.py` exits 0 on the whole suite
- [ ] README.md + INSTALL.md complete per Part 3

### 4.3 Evals (per skill)

`evals/evals.json` in skill-creator format:

```json
{
  "skill_name": "pcb-routing",
  "evals": [
    {
      "id": 1,
      "prompt": "realistic user phrasing, with specifics and even typos — e.g. 'im laying out a 4 layer stm32 board with usb-c, the diff pair keeps throwing drc errors when i try to length match, what am i doing wrong'",
      "expected_output": "what a good agent response using this skill looks like",
      "files": [],
      "assertions": ["objectively checkable statements, e.g. 'response mentions intra-pair skew vs inter-pair length budget'", "'response warns against splitting pair across plane gap'"]
    }
  ]
}
```

3+ evals per skill, mixing should-trigger and near-miss should-NOT-trigger
prompts (near-misses matter: "route my Express server" must not trigger
`pcb-routing`).

---

## PART 5 — QUALITY BAR (how to think while writing)

- Write for **a smart model that has never fabbed a board**: every rule gets
  its physical or process reason. "Keep the decoupling loop short" is weak;
  "the inductance between cap and IC pin sets the frequency ceiling of the
  bypass — a 5 mm loop with vias behaves like a series inductor above ~10 MHz,
  so place the cap within ~1–2 mm with via straight to the plane" is strong.
- Prefer **decision tables and trees** over walls of text.
- Assume the user ranges from a hobbyist on their first KiCad board to a
  professional needing a review co-pilot: skills must scale — quick defaults
  up front, depth in references.
- Balance: don't bury every topic in caveats, but never state a
  fab-dependent value as universal law.
- Experience from your completed project is gold — but only in generalized
  form. Every rule you write must pass the different-board test (Part 0.2);
  specifics belong in labeled worked examples, never in rules.
- Length discipline: a bloated skill wastes context in EVERY invocation.
  If a section isn't pulling its weight, cut it or demote it to references/.

---

## PART 6 — START NOW

Remember what this session is: **authoring skills, not being one.** Start with
Part 0 — verify whether a completed project actually exists (never assume,
never fabricate). If one does: inventory it read-only and harvest its lessons
into `HARVEST_MAP.md` (offer the optional safeguard only under 0.1's
conditions). If none: proceed per 0.3, standards-first. Then §4.1 step 1
(clarifying questions or documented defaults), then build the entire suite in
the current working directory under `pcb-skills/`, writing every file to disk
as you go and keeping `BUILD_STATE.md` current. Do not stop after planning —
produce all files. When done, present the final report (§4.1 step 5)
including the `validate_suite.py` output, the harvest-map summary, the
`BUILD_STATE.md` pointer, and any optional safeguard/snapshot URLs.
