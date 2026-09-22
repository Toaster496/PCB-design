# INSTALL — harness installation matrix

Install path conventions change; each section notes the generic fallback and marks
version-specific specifics as "verify current convention" — check your harness's
current docs when in doubt. The universal fallback (last section) works everywhere.

## Claude Code / Claude.ai

**Personal (all projects):** copy each skill folder into `~/.claude/skills/`:
```bash
mkdir -p ~/.claude/skills
cp -r pcb-skills/pcb-* ~/.claude/skills/
```
**Project-scoped (recommended for a hardware repo):** `<project>/.claude/skills/`
```bash
cd /path/to/your/board-project
mkdir -p .claude/skills && cp -r /path/to/pcb-skills/pcb-* .claude/skills/
```
Claude Code discovers skills by scanning those directories (verify current
convention in the docs; `claude skill list`-style commands confirm loading).
**Claude.ai web:** Settings → Capabilities → Skills → upload the skill folder/zip
(one zip per skill, or the suite zipped and unpacked per-skill). Then reference
them naturally ("use the pcb-flow skill").

## Cursor

Skills aren't auto-loaded; use one of:
1. **Project rules (recommended):** flatten each needed skill into
   `.cursor/rules/` — generate the rules variant with the suite's exporter:
   ```bash
   python pcb-skills/scripts/export_for_harness.py pcb-skills/pcb-flow \
          --style rules --out .cursor/rules/pcb-flow.mdc
   ```
   (verify current `.mdc` frontmatter convention in Cursor's rules docs — the
   exporter emits a generic always-on rule header you may need to adjust).
2. **@-mention:** in chat, `@pcb-skills/pcb-routing/SKILL.md` pulls the file in.
3. **AGENTS.md-style:** add pointers (below) to `.cursor/rules` or repo root.

## Windsurf

`.windsurf/rules/` works like Cursor's rules dir (verify current convention):
```bash
python pcb-skills/scripts/export_for_harness.py pcb-skills/pcb-pitfalls \
       --style rules --out .windsurf/rules/pcb-pitfalls.mdc
```
or @-mention / open the SKILL.md directly in the workspace and ask the agent to
follow it.

## Codex CLI / AGENTS.md harnesses

Add pointers to `AGENTS.md` at repo root (generated fragment):
```bash
python pcb-skills/scripts/export_for_harness.py pcb-skills/pcb-flow \
       --style agents --out AGENTS.md.fragment
cat AGENTS.md.fragment >> AGENTS.md
```
The fragment tells the agent where each skill lives and when to read which file.

## GitHub Copilot

`.github/copilot-instructions.md` (verify current support for instructions files
in your environment) — same fragment approach:
```bash
python pcb-skills/scripts/export_for_harness.py pcb-skills/pcb-bom \
       --style agents --out .github/pcb-bom.instructions.md
```
or commit the whole suite in-repo and add one pointer line per skill to your
copilot instructions: "For BOM work, follow pcb-skills/pcb-bom/SKILL.md."

## Any other agent / plain chat model

**Universal fallback — flattened export:** pick the skill you need and paste:
```bash
python pcb-skills/scripts/export_for_harness.py pcb-skills/pcb-design-rules \
       --style flat --out pcb-design-rules.flat.md
```
Then paste the file's contents into the system prompt / first message. The
flatten test guarantees it still gives complete guidance standalone. For models
with file access, simply keep the suite in the workspace and point the agent at
`pcb-skills/pcb-flow/SKILL.md` as the entry point.

## Post-install verification

```bash
python pcb-skills/scripts/validate_suite.py pcb-skills/    # expect exit 0
```
Then in your harness, ask: "I'm starting a new PCB project" — pcb-flow should
trigger (its description is written to fire on such phrasings).
