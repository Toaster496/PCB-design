# The skill-format contract (embedded, self-contained)

Condensed, normative copy of the Anthropic Agent Skills format this suite follows.
A new skill authored per this file works in any harness that loads skills by
directory (Claude Code / Claude.ai, and paste-export elsewhere).

TOC: §1 Anatomy · §2 Frontmatter · §3 Progressive disclosure · §4 Writing
standards · §5 Script contract · §6 Portability · §7 Evals · §8 Acceptance
checklist

## §1 Anatomy

```
skill-name/
├── SKILL.md              (required: YAML frontmatter + markdown body, <500 lines ideal)
├── references/*.md       (optional: docs loaded into context as needed)
├── scripts/*.py          (optional: executable helpers, deterministic tasks)
├── assets/*              (optional: templates used in OUTPUT files)
└── evals/evals.json      (3+ realistic test prompts)
```

## §2 Frontmatter

```yaml
---
name: skill-name          # == directory name; [a-z0-9-]; <=64 chars
description: >-           # <=1024 chars; third person; WHAT it does + WHEN to
  ...                     # trigger. ALL trigger info lives HERE, never the body.
---
```

- Descriptions are **pushy**: models under-trigger skills; enumerate the
  situations, phrasings, synonyms ("use this whenever the user is doing X, Y, Z
  even without the word 'PCB'").
- Optional extra keys (license, version) allowed; harnesses ignore unknown keys;
  never harness-specific keys in required skills.

## §3 Progressive disclosure (three loading levels)

1. Metadata (name+description) always in context (~100 words) — keep dense.
2. SKILL.md body loaded when triggered — keep <500 lines; hot path: workflow,
   decision tables, most-used rules; push deep detail to references/ with clear
   pointers ("for voltage-based clearance tables read references/clearance.md").
3. Bundled resources read/executed on demand, unlimited size — scripts run
   WITHOUT being loaded into context; say when to run and what they output.

Domain organization: one reference file per variant (per-EDA-tool, per-fab) with
a selection table in SKILL.md so only the relevant file gets read.

## §4 Writing standards

- Imperative form ("Route the pair…", not "The pair should be routed…").
- Explain WHY (physics/fab-process/assembly mechanism) — models generalize from
  reasons, not from MUSTs. All-caps ALWAYS/NEVER is a yellow flag; reframe with
  reasoning. True hard constraints (safety, DRC minimums) are the exception.
- Tables over prose for numbers.
- Good/bad example pairs, labeled as examples (never rules).
- Provenance for every number: standard (IPC-2221/2152/7351, IEC 62368-1),
  named fab/host, or "conservative generic default — verify". Zero invented
  precise numbers.
- Self-contained: each skill brief-repeats anything essential instead of only
  cross-linking (a harness may load one skill without its siblings).
- Every internal link RELATIVE and resolving from the skill directory.

## §5 Script contract

Python ≥3.8; **stdlib imports only** (external TOOLS via detect-and-shell-out:
kicad-cli, openssl, age, gpg, curl, split); every script starts:

```python
"""<one-line purpose>

INPUTS:  args / env vars / files consumed (with formats)
OUTPUTS: files written, stdout shape, side effects (network: yes/no)
EXIT:    0 ok | 1 bad input | 2 missing tool/env | 3+ documented domain codes
EDGE:    empty/huge inputs, offline, missing optional tool, corrupt file,
         re-run behavior (idempotent? overwrite? append?)
NON-GOALS: what this deliberately does NOT attempt
"""
```

Deterministic; `--help`; documented exit codes; NO network calls (sole
sanctioned exception: the continuity skill's backup.py, which must degrade
gracefully and print manual commands when offline/blocked). Lazy third-party
module use is permitted ONLY as a last-resort guarded fallback inside
try/except in a function (the single existing precedent: backup.py's optional
cryptography path) — top-level imports must remain stdlib.

## §6 Portability rules

- Plain UTF-8 markdown; no HTML, no vendor markup.
- Relative links only, resolvable from the skill directory.
- EDA tools referenced as variants; core instructions must work with NONE
  installed (agent may only be advising a human / editing text files).
- Flatten test: a SKILL.md body pasted into any system prompt still gives
  complete usable guidance.
- No malicious/surprising content (principle of lack of surprise); skills advise
  hardware design only.

## §7 Evals format

`evals/evals.json`:

```json
{
  "skill_name": "pcb-<domain>",
  "evals": [
    {
      "id": 1,
      "prompt": "realistic user phrasing with specifics and typos",
      "expected_output": "what a good skill-using response looks like",
      "files": [],
      "assertions": ["objectively checkable statement", "..."]
    }
  ]
}
```

3+ per skill; MUST mix should-trigger and near-miss should-NOT-trigger prompts
(near-misses are the quality signal: "route my Express server" must not trigger
pcb-routing).

## §8 Acceptance checklist (before declaring a new skill done)

- [ ] name == directory; frontmatter valid; description ≤1024 chars, third
      person, pushy with triggers
- [ ] SKILL.md body <500 lines; references >300 lines have TOC
- [ ] all links relative and resolve; sibling cross-links both directions
- [ ] scripts: stdlib top-level imports, --help, py_compile clean, contract
      docstring present, no network (except backup.py precedent)
- [ ] evals: 3+ incl. near-miss negatives, realistic phrasing
- [ ] no fabricated numbers; provenance on every value; HV/safety → human review
- [ ] flatten test passes; suite `validate_suite.py` exits 0
- [ ] README/flow routing updated; suite journal checkpointed
