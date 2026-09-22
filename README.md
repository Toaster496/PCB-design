# pcb-skills — a portable PCB design skills suite

A suite of 9 agent skills that take a PCB project from requirements to
fabrication-ready output — written for any capable coding agent or chat model with
file access, in plain markdown (Anthropic Agent Skills format). Physics-first:
every rule carries its mechanism, every number its provenance.

Built in part from lessons harvested from a real, completed board build (2-layer,
ESP32-C3-module + 3× motor drivers, budget quick-turn fab) — generalized,
anonymized, and standards-checked. Every "field-tested" tag in the suite traces to
a genuinely harvested lesson.

## Skill index

| Skill | Purpose (one line) | Triggers when |
|---|---|---|
| `pcb-flow` | End-to-end orchestrator: phase map, gates, routing to siblings | any PCB start / review / resume / "where am I" |
| `pcb-board-format` | Outline, stackup, materials, mechanicals, panelization | layer count, thickness, mounting, cutouts, panel, fab limits |
| `pcb-layout` | Zoning, placement order, decoupling, thermal/EMC placement | placing parts, ratsnest trouble, cap/crystal/antenna placement |
| `pcb-design-rules` | Net classes, creepage/clearance, width/current, vias | "is this wide/ far enough", rules setup, DRC constraints |
| `pcb-routing` | Routing strategy, ground physics, PDN, diff pairs, post-route | routing anything, planes/pours, matching, DRC cleanup |
| `pcb-bom` | BOM/CPL formats, part selection, lifecycle, PCBA workflows | parts lists, freezing BOM, sourcing, assembly order files |
| `pcb-pitfalls` | Mistakes catalog, gate checklists, gerber audit | pre-order review, bug symptom hunt, "what am I missing" |
| `pcb-project-continuity` | Journal, encrypted off-box backups, resume playbook | checkpoint/backup/resume/lost-session, status questions |
| `pcb-skill-creator` | Meta-skill: author new pcb-* skills in-format | "make a new skill", "extend the suite", gap identified |

Entry point for a new project: `pcb-flow`. Deep question mid-project: the matching
specialist skill above.

## Dependencies

- Python ≥ 3.8, standard library only, for the bundled scripts
  (`bom_lint.py`, `check_rules.py`, `gerber_audit.py`, `backup.py`,
  `validate_suite.py`, `export_for_harness.py`). Optional external TOOLS the
  scripts detect and shell out to when present: `curl`, `tar`, `sha256sum`,
  `openssl`/`age`/`gpg` (backup encryption), `kicad-cli` (headless DRC/exports).
- No mandatory EDA tool: every skill works with none installed (advising a human
  / editing text files); KiCad / Altium / EasyEDA variants are reference files.
- One deliberate exception to "no network": `pcb-project-continuity/scripts/
  backup.py` (fail-closed, manual-recipe fallback; see its docstring).

## Installation

See `INSTALL.md` for per-harness instructions (Claude Code / Claude.ai, Cursor,
Windsurf, Codex CLI/AGENTS.md, Copilot, or plain paste via the flattened export).

## Scripts

| Script | Runs | Does |
|---|---|---|
| `pcb-design-rules/scripts/check_rules.py` | offline | validates the net-class rules CSV before EDA entry |
| `pcb-bom/scripts/bom_lint.py` | offline | BOM lint + normalize (dups, MPN, value/footprint sanity, consolidation) |
| `pcb-pitfalls/scripts/gerber_audit.py` | offline | fab-package smoke test (file classes, drill sniff, layer count) |
| `pcb-project-continuity/scripts/backup.py` | network | encrypt (fail closed) + upload + verify + index a project checkpoint |
| `scripts/validate_suite.py` | offline | mechanical acceptance check of the whole suite |
| `scripts/export_for_harness.py` | offline | flatten a skill for system-prompt/rules/AGENTS.md pasting |

## Suite conventions

- Relative links only (`../pcb-routing/SKILL.md`), resolvable from each skill
  directory.
- Frontmatter uses only portable keys (name, description, license, version);
  unknown keys are ignored by harnesses; no harness-specific keys are required.
- The optional lazy third-party import inside
  `pcb-project-continuity/scripts/backup.py` (the `cryptography` last-resort
  fallback, guarded in-function per the skill-format contract) is the single
  sanctioned deviation from pure-stdlib top-level imports.
- Provenance classes used throughout: IPC/IEC standard · named fab/host ·
  "conservative generic default — verify".

## License

MIT (each skill's frontmatter may carry `license: MIT`; harnesses ignore it).

## Extending

New niche domain (flex, BMS, audio, HDI…)? Author it with
`pcb-skill-creator/SKILL.md` — the format contract is embedded at
`pcb-skill-creator/references/skill-format.md`, and `scripts/validate_suite.py`
enforces it mechanically.
