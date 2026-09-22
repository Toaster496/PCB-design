# BUILD_STATE.md — resumable build state for the pcb-skills suite

A fresh session: read this file, then `/home/z/my-project/HARVEST_MAP.md`, then continue
from "Next". Keep this file current at every skill boundary.

## Status: COMPLETE (v1) — validated, packaged, uploaded

| Skill | State | Files done |
|---|---|---|
| pcb-flow | DONE | SKILL.md, references/interview.md, evals/evals.json |
| pcb-board-format | DONE | SKILL.md, references/{stackups,fab-capabilities,panelization}.md, assets/fab_notes_template.md, evals |
| pcb-layout | DONE | SKILL.md, references/{checklists-archetypes,gallery}.md, evals |
| pcb-design-rules | DONE | SKILL.md, references/{clearance,current-capacity,vias,high-voltage,eda-rule-files}.md, scripts/check_rules.py (tested, exit 0), assets/rules_template.csv, evals |
| pcb-routing | DONE | SKILL.md, references/{kicad,altium,generic,high-speed,rf}.md, evals |
| pcb-bom | DONE | SKILL.md, references/selection_tables.md, scripts/bom_lint.py (tested: clean+error paths), assets/{bom_template,bom_example,cpl_template}.csv, evals |
| pcb-pitfalls | DONE | SKILL.md, references/{pitfalls,checklists}.md, scripts/gerber_audit.py (tested on real fab pkg: PASS), evals |
| pcb-project-continuity | DONE | SKILL.md, references/hosts.md, scripts/backup.py (tested: compile/help/dry-run/fail-closed), assets/journal_template.md, evals |
| pcb-skill-creator | DONE | SKILL.md, references/skill-format.md, evals |
| suite-level (README/INSTALL/validate/export) | DONE | README.md, INSTALL.md, scripts/{validate_suite,export_for_harness}.py |

## Conventions locked for this build

- Format: Anthropic Agent Skills (YAML frontmatter name+description, SKILL.md <500 lines,
  references/ >300 lines need TOC, scripts stdlib-only w/ contract docstring, evals 3+).
- Defaults (headless run): KiCad-first variants + generic fallback; all board classes;
  budget quick-turn fab assumptions; all harnesses; host chain gofile → filebin → catbox
  with mandatory encryption + split key policy for project archives; full anonymization.
- Source project exists and is mined read-only (see HARVEST_MAP.md, 23 lessons H1–H23).
- Suite root: /home/z/my-project/pcb-skills/ ; suite zip delivered via filebin (user request).
- Cross-link policy: siblings referenced as `../<skill>/SKILL.md` relative links.
- Every numeric value carries provenance: standard (IPC-2221/2152/7351, IEC 62368-1),
  named fab tier, or "conservative generic default — verify against your fab".

## Validation record

- validate_suite.py: PASS (9 skills, 21 references, 6 scripts, 9 eval files, 0 FAIL, 0 WARN)
- export_for_harness.py: flat/rules/agents smoke tests OK (flat self-contained, 5 refs inlined)
- check_rules.py on template: exit 0; bom_lint.py: clean + error paths tested; gerber_audit.py:
  PASS on a real 30-file fab package; backup.py: compile/help/dry-run/fail-closed tested
- Self-review: no identifying details, no harness-specific syntax, all field-tested tags
  traced to HARVEST_MAP rows

## Next

Suite v1 complete. Possible follow-ups for a future session:
- live re-verification of hosts.md limits/retention from an environment with web access
- live fab capability refresh (JLCPCB/PCBWay pages) into fab-capabilities.md
- author first niche domain skill (pcb-flex-rigid / pcb-battery-management) per
  pcb-skill-creator to validate the meta-skill end-to-end

## Open issues

- None blocking. Host matrix + fab capability tables are seeded field data marked
  unverified — probe before production reliance (by design).
