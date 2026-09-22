---
name: pcb-flow
description: >-
  End-to-end orchestrator for printed circuit board design: phase-by-phase workflow from
  requirements to fabrication-ready outputs, with review gates and continuity checkpoints.
  Use this whenever the user is starting, planning, reviewing, or resuming ANY hardware or
  PCB work — "I'm designing a PCB", "help me with my board", "new hardware project",
  "layout review", "ready to order boards", "what order do I do things in", "schematic vs
  layout vs gerbers", even if they never say the word "PCB" (e.g. "custom board for my
  robot"). It routes to the right specialist skill (pcb-board-format, pcb-layout,
  pcb-design-rules, pcb-routing, pcb-bom, pcb-pitfalls, pcb-project-continuity) at each
  phase. Also use it to decide which phase an in-flight project is currently in.
---

# pcb-flow — the design-flow orchestrator

You are guiding a PCB from idea to fabrication-ready package. Your job at any moment:
figure out the current phase, answer that phase's questions, satisfy its exit criteria,
then advance. Load specialist skills only when their phase arrives — that keeps context
small and instructions relevant.

If the project already exists mid-stream, jump to "Diagnosing an in-flight project"
below. If it is new, start at Phase 0.

## Phase map

| # | Phase | Questions to answer | Exit criteria (all must hold) | Load next | Artifacts produced |
|---|---|---|---|---|---|
| 0 | Requirements | What does it do? Size/power/environment/cost/volume? Which fab/assembly? Which EDA tool? | Written requirements block; net estimate of voltage rails & current per rail; enclosure/mechanical constraints captured; fab + assembly house chosen (tentatively) | `pcb-board-format` | `requirements.md` (project journal section is fine) |
| 1 | Architecture | Block diagram? How many sub-circuits (MCU, power, interfaces, sensing, actuation)? Rail tree? Make/buy partition? | Block diagram every sub-circuit named; rail tree with source→rail→load currents; interface list (pin count per connector) | `pcb-design-rules` (early constraint set) + `pcb-bom` (part selection begins) | block diagram, rail tree, preliminary MPN list |
| 2 | Schematic capture | Every block drawn, every net named, every part real? | ERC clean or every residual warning explained; power flags set; net names reviewable; symmetric channels audited for symmetry | `pcb-pitfalls` (schematic-review section) | schematic file, netlist |
| 3 | Schematic review | Would this board power up and work? | Independent review pass vs `pcb-pitfalls` checklist; ALL review notes resolved or consciously waived; BOM sanity (no NPN-as-PNP-class errors) | `pcb-bom` | review notes, updated schematic |
| 4 | BOM freeze | Can every line actually be bought and assembled? | Every line has MPN + supplier PN + status=Active; alternates noted for single-source parts; DNP lines flagged; `bom_lint.py` clean | `pcb-board-format` | frozen BOM + CPL pairing |
| 5 | Board setup | Outline, stackup, and rules right for the fab? | Outline drawn with connectors + mounting located in-canvas; stackup chosen with rationale; design rules entered (net classes + clearance/width/via); fab capability confirmed within limits | `pcb-layout` | board file with outline + rules |
| 6 | Placement | Are parts in the right neighborhoods? | Zones drawn; placement order honored; decoupling placed; thermal + EMC placement rules pass; ratsnest crossings reduced to trivial | `pcb-routing` | placed board |
| 7 | Routing | Are all nets connected the way physics wants? | 100% connectivity (0 unconnected, zone islands refilled & explained); DRC 0 errors; warnings triaged; return paths, hot loops, diff pairs checked | `pcb-pitfalls` (post-route checklist) | routed board |
| 8 | DRC/DFM cleanup | Will the fab actually build this? | DRC clean; silkscreen readable; no DFM violations per fab tier; gerber spot-check | `pcb-pitfalls` (`gerber_audit.py`) | DRC-clean board |
| 9 | Fab package | Can a stranger order my board from these files? | Gerbers + drill + outline; pos.csv + BOM for assembly; fab notes; `gerber_audit.py` clean; visual review incl. 3D pass | `pcb-project-continuity` (final checkpoint) | fab zip |
| 10 | Bring-up | Does the physical board work? | Bring-up notes written (test points, expected voltages, flash procedure); revision list started | — (loop back to Phase 1/2 for rev B) | bring-up doc |

Phase 10 loops: every bring-up finding feeds `pcb-pitfalls` (project-specific list in the
journal) and the next revision starts at Phase 1 with the lessons attached.

**Continuity is an exit criterion, not a phase.** At EVERY gate: update the project
journal FIRST, then archive + upload + verify (procedure and scripts in
`../pcb-project-continuity/SKILL.md`). A phase is not "done" until its state survives the
death of the current session. This is cheap and it is the single habit that most
reliably rescues long hardware projects — sandboxes, VMs, and chat contexts all die on
their own schedule; hardware lives for weeks.

## Phase guidance in brief

### Phase 0 — requirements interview

Run the interview script in `references/interview.md` (10–15 minutes of questions; full
script there). The short version — capture, in writing:

1. **Function**: what does the board do? What talks to what?
2. **Power**: input source(s) and voltage(s); current per rail; battery or mains?
3. **Size & mechanics**: enclosure? mounting? connectors fixed in position? max height?
4. **Environment**: temperature, vibration, moisture, ESD exposure, EMC approvals needed?
5. **Cost & volume**: 1 prototype or 10k units? Assembly in-house or contracted?
6. **Fab & assembly house**: this sets your physical limits (see `../pcb-board-format/references/fab-capabilities.md`).
7. **EDA tool**: KiCad / Altium / EasyEDA / other — affects variant instructions only, never the physics.
8. **Standards to meet**: safety (IEC 62368-1), automotive, medical, IPC class 2 vs 3?

Write the answers down BEFORE drawing anything. Requirement changes after routing cost
10–100× what they cost now. If the user cannot answer a question, record the assumption
you are making and mark it revisit-later.

### Phase 1 — architecture

Draw the block diagram (ASCII is fine — boxes and arrows, one box per sub-circuit, label
every arrow with signal AND rail). Then the rail tree: every power source → every
converter → every rail → every load with its current. Check: every load's rail exists;
every converter's budget covers its loads with ≥20% margin; every input has protection
(reverse polarity, TVS, fuse) appropriate to the environment.

### Phase 2–3 — schematic and its review

Capture rules that prevent whole classes of bugs:

- **Name nets like they will be read**: `MOTOR1_IN1`, not `N0032`. Net names are your
  first schematic review tool.
- **Power flags / no-connect** explicitly — silent ERC suppression hides real errors.
- **Symmetry audit for repeated channels**: if the design has N copies of a channel
  (motor drivers, LED strings, sensor front-ends), script a netlist-level comparison of
  the copies — component values, pullups/pulldowns, decoupling — and reconcile every
  asymmetry as intended or fix it. Eyes gloss over the 6th copy of the same sub-circuit;
  scripted audits don't. (Field-tested: a missing input pulldown on one of six identical
  driver channels escaped visual review and was caught by exactly this audit.)
- **Pull-up/pull-down completeness**: every input that floats at power-up or reset gets
  a defined state. Every enable line, every boot-strapping pin, every unused-but-live
  input.
- **Reset & boot timing**: any EN/RESET RC delay must dominate the slowest power rail's
  ramp (including the LDO/buck soft-start). When repurposing a converter for a different
  output voltage, recompute everything tied to that voltage: feedback divider,
  compensation, output caps, inductor ripple current.

Run ERC; explain every remaining warning in the journal ("benign: SBU pin-type mismatch
on USB-C", not just "ERC done").

### Phase 4 — BOM freeze

See `../pcb-bom/SKILL.md`. Gate = the BOM is purchasable as-written: MPNs, supplier PNs,
lifecycle status, DNP flags, alternates for single-source parts. Run
`../pcb-bom/scripts/bom_lint.py` and fix every finding.

### Phase 5 — board setup

See `../pcb-board-format/SKILL.md`. Lock the outline (with connectors and mounting holes
placed in real positions), pick the stackup by the decision tree, and enter the full
design-rule set (net classes, clearance, width, via) BEFORE placement — retrofitting
rules into a placed board is how DRC error storms are born.

### Phase 6 — placement

See `../pcb-layout/SKILL.md`. Placement order: mechanicals/connectors → anchors (ICs,
magnetics, crystals) → decoupling + local passives → test points → cosmetics. Placement
is 60% of routing quality: a placement whose ratsnest is a bird's-nest cannot be routed
well by any technique.

### Phase 7–8 — routing and cleanup

See `../pcb-routing/SKILL.md`. Route in priority order (fanout → critical → power →
fill). Ground strategy is the most consequential section in the whole suite — read it
before routing anything. Post-route: DRC to zero errors, triage warnings into
inherited/cosmetic vs real, then the visual review passes (per layer + 3D).

### Phase 9 — fab package

See `../pcb-pitfalls/SKILL.md` (release section + `gerber_audit.py`) and
`../pcb-board-format/assets/fab_notes_template.md`. The package must be complete enough
that a stranger could order your board: gerbers, drill, outline, pos+BOM for assembly,
fab notes. Re-verify the package contents against the audit script output.

### Phase 10 — bring-up notes

Write them BEFORE the boards arrive: expected voltage at each test point, bring-up order
(power rails first with no load, then programming, then per-channel function), flash
procedure, and the failure decision tree ("3V3 low → check source-select stuffing →
check LDO thermal"). Good bring-up notes are the cheapest debug instrument you own.

## Diagnosing an in-flight project

1. What files exist? (schematic only → you are at Phase 2–4; board file with outline →
   Phase 5; placed → 6; routed with DRC errors → 7–8; gerbers → 9.)
2. Is there a project journal? (`PROJECT_JOURNAL.md` at project root — see
   `../pcb-project-continuity/SKILL.md`.) If yes, read its Snapshot + Todo + Resume
   playbook FIRST — it exists precisely so you don't re-derive the plan. If no journal
   exists, create one from the template immediately and backfill from the files.
3. Does an off-box backup exist and is it verified fresh? If not, that is the first
   action, before any design work — you are one session crash away from losing the work
   you are about to review.
4. Then answer the current phase's exit criteria and continue.

## Running a design review at a gate

- Review against the phase's exit criteria as a checklist — every line: pass / fail / N-A.
- For every fail: fix now or file it in the journal's Todo with an acceptance criterion.
- A review that finds NOTHING wrong has usually not looked hard enough — especially at
  the schematic and pre-fab gates. Escalate to a human review (see
  `../pcb-pitfalls/SKILL.md` "when to demand a human review") for: mains/high-voltage
  exposure, safety-standard compliance paths, first articles of a production run, and
  any board whose failure mode is fire rather than embarrassment.

## What "done" means

The board is done when: (a) fab package passes audit, (b) bring-up notes exist, (c)
journal + backups current, (d) the user says stop. Not before. A board that is "done
except gerbers" is not done; a board that is ordered but whose journal is stale is one
sandbox crash away from being un-resumeable.

## Quick routes for common requests

- "Review my schematic/board" → Diagnose phase → run that phase's checklist from
  `../pcb-pitfalls/references/checklists.md`.
- "Which stackup?" → `../pcb-board-format/SKILL.md` decision tree.
- "Is this trace wide enough?" → `../pcb-design-rules/SKILL.md` current table.
- "How do I back this up / I lost my session" → `../pcb-project-continuity/SKILL.md`.
- "Make a new skill for X niche" → `../pcb-skill-creator/SKILL.md`.
