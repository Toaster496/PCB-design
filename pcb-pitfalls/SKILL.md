---
name: pcb-pitfalls
description: >-
  The PCB mistakes catalog and review checklists: classic failure modes per design
  phase (board setup, placement, routing, rules/DFM, BOM/sourcing, assembly,
  EMC/ESD) with symptom, root cause, and prevention, plus per-phase gate checklists
  and the gerber_audit.py pre-release fab-package auditor. Use whenever the user is
  reviewing a design ("check my board before ordering"), hunting a bug with
  suspicious symptoms ("board resets when the motor spins"), preparing to release
  gerbers, asking "what goes wrong with X", or wants a design review — also for
  phrases like "is this a common mistake" or "what did i miss".
---

# pcb-pitfalls — mistakes catalog & review checklists

Every entry in this suite exists because some board failed somewhere. This skill is
the index of failure: the top-20 most expensive mistakes (ranked by blast radius),
how to run a structured self-review, when to escalate to a human, and the tools for
the pre-release gate.

Full catalog (5 fields per entry: phase → pitfall → symptom → why → fix/prevention):
`references/pitfalls.md`. Per-phase gate checklists:
`references/checklists.md`. Fab-package smoke test: `scripts/gerber_audit.py`.

## Top-20 most expensive mistakes (blast-radius ranked)

1. **Mains/HV clearance guessed** → product becomes an arc gap → fire/injury class.
   Never size from vibes; derive (design-rules §2) + human review. (`references/pitfalls.md` HV)
2. **ESD clamps at the IC instead of the connector** → every cable-borne surge
   couples through the interior first → dead port, dead MCU, in the field.
3. **Missing input pull-down/pull-up on gate-driver inputs** → floating gates at
   power-up → both bridge FETs partially on → smoke at first power-application.
   Every input gets a defined default state.
4. **Buck hot loop routed huge** → radiated/conducted spikes, failed EMC, mystery
   ADC noise, and dead fielded boards that "worked on the bench".
5. **Reset/EN RC faster than supply ramp** → MCU boots before its rail is stable →
   random boot failures, "bricked" units that aren't. (EN delay must dominate the
   slowest rail ramp, incl. soft-start.)
6. **Borrowed/variant footprint pinout unverified** → mechanical fit ≠ pin map:
   sibling-family modules share packages with different pin assignments → board
   powers a pin that isn't power. Verify pad-by-pad against the official datasheet.
7. **NRND/single-source part designed in** → the reorder 8 months later can't be
   built → forced redesign under time pressure.
8. **Missing USB-C CC pull-downs (Rd 5.1k)** → source supplies nothing (or
   defaults wrong) → "dead" board that's actually un-negotiated.
9. **Annular ring at the fab floor** → drill registration drift → intermittent
   opens on layer transitions → boards that work cold and fail warm.
10. **Decoupling caps far from pins** → cap loop inductance defeats them → RF-noon
    noise on "clean" rails, flaky MCU behavior. (1 nH/mm physics.)
11. **Antenna keepout violated by ground pour** → detuned radio → 5 m range instead
    of 50 m, "fixed" by firmware hacks forever.
12. **Plane split under a fast signal** → return path detour → EMC failure and
    crosstalk victim created where none existed.
13. **Serpentine length-matching at the receiver** (adjacent to victim nets) →
    the "fix" couples noise exactly where margins are spent.
14. **Tombstone-prone two-pad passives with unbalanced thermal ties** → one pad's
    pour connection solders late, part stands up → assembly yield loss.
15. **Via-in-pad unplugged on BGA** → paste wicks into the barrel → starved joints
    → BGA balls that pass test and fail in the field.
16. **Silkscreen on pads / refdes missing** → assembly errors + slow debug ("which
    of these 8 identical passives is R27?").
17. **Designing below fab minimums silently** → the order lands in the capability-
    surcharge queue (or gets fabbed wrong) → schedule slip + surprise cost.
18. **Orphaned tracks after part replacement** → connectivity lies: the netlist
    says connected, the board has an unterminated stub → works at DC, misbehaves
    with edges. Purge old-net tracks when replacing parts.
19. **No test points** → bring-up becomes circuit surgery; every debug session
    costs an hour of probing gymnastics.
20. **No verified off-box backup / journal at phase gates** → the sandbox dies and
    the project's real state dies with it (see `../pcb-project-continuity/SKILL.md`).
    The cheapest insurance on this list and the most frequently skipped.

## How to run a structured self-review

1. **Pick the gate checklist** for the phase (`references/checklists.md`:
   post-stackup, post-placement, post-route, pre-fab-release).
2. **Every line: pass / fail / N-A.** No skipping, no "probably fine" — an
   unmarked line is an unchecked line.
3. For every FAIL: fix now, or file in the journal's Todo with an acceptance
   criterion.
4. **Symptom-hunting mode** (debugging an existing board): open
   `references/pitfalls.md`, scan the *Symptom* column for the behavior, jump to
   the entry's fix. The catalog is organized phase → pitfall, but symptoms are the
   index a debugging session actually needs.
5. **Symmetry audit for repeated channels** (any N× repeated structure: script a
   netlist comparison across the copies — a missing pull resistor on one of six
   identical channels escapes eyeball review; this exact failure, caught by
   scripted audit, not by review, is a field-tested pattern).
6. Re-ERC / re-DRC after fixes. Fixing one thing breaks another often enough that
   the re-run IS the step, not the afterthought.

A review that finds nothing wrong usually hasn't looked hard enough — especially
schematic review and pre-fab. If your checklist run is all-pass in under five
minutes, you skimmed.

## When to demand a human review

The agent prepares; the human signs. Mandatory escalation:

- **Mains or HV anywhere on the board** (creepage/clearance sign-off).
- **Safety-standard compliance paths** (IEC 62368-1 class products, medical,
  automotive).
- **First article of a production run** (before the 10k reorder).
- **Lithium battery charging paths** (fire class failure).
- **Anything whose failure mode is fire, shock, or a recall rather than
  embarrassment.**

Recommended (not mandatory): every first board of a new design; every connector-
heavy board (mechanical interface to reality); every RF design beyond a canned
module (someone with a VNA should look at it).

## `scripts/gerber_audit.py` — pre-release smoke test

Audits a released fab package directory: file presence (copper layers, mask, silk,
paste, outline, drill), drill file format/units sniffing (Excellon headers), layer
count vs a claimed stackup (from the .gbrjob or --layers), empty/extra user-layer
gerbers (warns: KiCad's default job exports every layer — empty User/Eco layers are
noise, not errors), and prints a pre-release checklist. Heuristic smoke test, NOT a
full CAM verifier — the fab's own analyzer is the second opinion.

```
python scripts/gerber_audit.py /path/to/fab-dir [--layers 2] [--stackup-claim 4]
```

Exit codes and contract in the script docstring. Run it on the package BEFORE
ordering; run it on EVERY package (it's cheap and memory-free).

## Reading order for a rushed review

1. This SKILL.md top-20 list.
2. `references/checklists.md` — the gate for the current phase.
3. The full catalog `references/pitfalls.md` — read your phase's section; scan
   symptom column for anything already observed.
4. The sibling skills for depth on the failing topic.
