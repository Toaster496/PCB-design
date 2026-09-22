---
name: pcb-skill-creator
description: >-
  Meta-skill for creating NEW pcb-* skills (pcb-flex-rigid, pcb-motor-drives,
  pcb-battery-management, pcb-audio, ...) so the suite grows without re-deriving
  conventions. Embeds the full skill-format contract in references/skill-format.md
  so it works standalone. Use when the user says "make a new pcb skill", "extend
  the pcb suite", "turn this PCB workflow/lesson into a skill", "add a niche board
  type to the skills", or when a gap in the existing skills has been identified
  that deserves a dedicated skill rather than a reference edit.
---

# pcb-skill-creator — extending the suite

The suite teaches boards generally; a niche skill teaches a domain deeply (flex,
motor drives, battery management, RF front-ends, audio, HDI, metal-core...). This
skill creates those without re-deriving the format conventions: the format
contract lives embedded in `references/skill-format.md` (self-contained — read it
before authoring; it is the authority for structure/frontmatter/scripts/evals).

## When to create a skill vs edit an existing one

| Situation | Action |
|---|---|
| A rule/pattern generalizes across boards | Edit the existing skill's SKILL.md or references/ |
| A whole DOMAIN has its own physics/process/workflow (flex stackups, BMS safety chains) | New skill |
| A per-EDA-tool variant of existing content | Add a reference file + selection row in the existing skill |
| A one-board-specific lesson | It goes in the PROJECT JOURNAL's pitfalls list — never a skill |

Different-domain test: would the content still be right on a completely different
board class? Skills teach CLASSES of boards; journals record THIS board.

## Workflow

1. **Capture intent** — write down before anything:
   - Task: what should the skill DO (imperative, concrete)?
   - Trigger: what user phrases/situations should activate it? (pushy list —
     models under-trigger)
   - Expected outputs: artifacts, decisions, formats?
   - Non-goals: what must it NOT do (boundaries vs siblings)?
2. **Interview edge cases** (with the user when interactive): the two hardest
   real cases, the near-miss that should NOT trigger, what a hobbyist vs a pro
   needs from it. If non-interactive, derive three edge cases yourself and write
   them into evals.
3. **Scope boundaries vs siblings**: list overlap with each existing skill
   (`../pcb-flow`, `../pcb-board-format`, ...). Rule: ONE skill owns a topic;
   others cross-link. If two skills would both teach X, one delegates. Add
   cross-links BOTH directions (new skill's SKILL.md ↔ sibling's SKILL.md) and
   a routing row in `../pcb-flow/SKILL.md`'s phase table or quick-routes.
4. **Draft SKILL.md** — frontmatter (name = directory, lowercase-hyphen ≤64;
   description third-person ≤1024 chars, WHAT + WHEN, trigger phrases) + body
   <500 lines: workflow, decision tables, the hottest 20% of the domain rules,
   pointers to references/ for the deep 80%. Imperative form; explain WHY
   (physics/process reasons) over rigid MUSTs; tables for numbers; provenance
   for every number (standard / named source / "conservative default — verify").
5. **Add resources** as needed: references/ (deep docs; >300 lines needs a TOC),
   scripts/ (Python ≥3.8, STDLIB-ONLY imports, `--help`, exit-code contract
   docstring per skill-format.md §scripts, deterministic, no network),
   assets/ (templates used in outputs).
6. **Write evals** — evals/evals.json, 3+ realistic prompts: at least one
     should-trigger, at least one near-miss should-NOT-trigger ("route my
     express server" must never fire pcb-routing). Realistic phrasing with
     typos/casual speech; assertions objectively checkable.
7. **Self-review against the acceptance checklist** (skill-format.md §checklist):
   run `../scripts/validate_suite.py` on the whole suite; fix everything; then
   flatten-test the SKILL.md (paste body into a bare prompt — still usable?).
8. **Iterate with feedback** — generalize from every test failure: fix the ROOT
   CAUSE and explain the why, don't overfit to the failing case or pile on new
   MUSTs. One targeted fix beats three blanket rules.
9. **Update the suite index**: README.md skill table + this suite's
   BUILD_STATE/journal records; announce in the final report.

## Naming and placement conventions

- Directory/name: `pcb-<domain>` (e.g. `pcb-flex-rigid`); the name MUST equal the
  directory; lowercase letters/digits/hyphens only.
- Suite root sits alongside the other skills; relative links only
  (`../pcb-flow/SKILL.md`).
- Version key in frontmatter optional (`version: 1`); harnesses ignore unknown keys.

## Domain-research checklist (before authoring the body)

For the target domain, gather: the 2–3 governing standards (IPC/IEC/USB-IF/etc.),
the canonical appnotes of its dominant parts (fab/vendor), the classic failure
modes (from teardowns, errata, community canon), and the decision tables the
domain actually uses (stackup choice, safety chain, impedance, derating). Cite
standards; label fab-dependent values; never invent precise numbers.

## The generalize-from-feedback principle (the core of iteration)

When an eval or a user review fails:

1. Find the MECHANISM the skill's instruction missed (physics, process, or
   workflow) — not the surface symptom.
2. Add the smallest instruction that teaches the mechanism, with its WHY.
3. Check it against the different-board test (Part 0 discipline —
   `/home/z/my-project/HARVEST_MAP.md` in the build environment records this
   suite's own harvest discipline; new authors maintain their own).
4. Re-run evals; expect the fix to generalize beyond the failing case.

What NOT to do: add a special-case rule per failure (rule pileup), tighten
constraints until trivial prompts pass (overfit), or respond to ambiguity with
MORE process (ambiguity needs a decision table, not bureaucracy).

## Deliverable shape (per new skill)

```
pcb-<domain>/
├── SKILL.md              (required: frontmatter + body <500 lines)
├── references/*.md       (deep docs, TOC if >300 lines)
├── scripts/*.py          (stdlib-only, contract docstring, --help, exit codes)
├── assets/*              (templates the outputs use)
└── evals/evals.json      (3+ prompts incl. near-miss negatives)
```

Then: validate (`../scripts/validate_suite.py`), smoke-export
(`../scripts/export_for_harness.py pcb-<domain>`), update suite README + flow
routing, checkpoint per `../pcb-project-continuity/SKILL.md`.
