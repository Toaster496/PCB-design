# PROJECT_JOURNAL.md — <project name>

> The living journal. Updated at EVERY checkpoint: journal first, then archive,
> upload, verify, index. A capable agent with ZERO prior context must be able to
> resume from this file alone — write accordingly.

## Snapshot

- Date: <YYYY-MM-DD HH:MM TZ>
- Phase: <e.g. M2 routing — see pcb-flow phase map>
- Latest backup: <URL> (<date>, sha256 <first 12 hex>)
- Key location: <URL2 / human-held>
- Canonical project path: </absolute/path>

## Done so far

- <milestone> — artifacts: <paths>
- <milestone> — artifacts: <paths>

## In progress

- <the 1-2 live threads, each with next concrete action>

## Todo list

- [ ] <item> — acceptance: <measurable criterion>
- [ ] <item> — acceptance: <measurable criterion>

## Decision log

| Decision | Why | Alternatives rejected | Revisit when |
|---|---|---|---|
| <e.g. 2-layer, bottom GND pour> | <speed class + cost> | 4-layer (+cost, unneeded) | <if USB-HS added> |

## Project-specific pitfalls & things to avoid

> This list only ever GROWS.

- <mistake made or nearly made — with the mechanism and the guard now in place>

## Open questions & risks

- <question/who answers>

## Resume playbook

> What a fresh agent must do, in order:

1. Read this Snapshot + the Backup manifest in `BACKUPS.md`.
2. Open <specific files> and verify <specific checks>.
3. The current sub-task is <X>; the next concrete action is <Y>.
4. Before any destructive step (list current candidates): checkpoint first
   (pcb-project-continuity §2).
5. Phase gate exit criteria live in: ../pcb-flow/SKILL.md phase map.

## Backup manifest

See `BACKUPS.md` (same directory). Index columns: date | phase | host | URL |
size | sha256 | cipher+method | key location/policy | expiry note.
