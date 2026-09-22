---
name: pcb-project-continuity
description: >-
  Project continuity and disaster recovery for hardware/PCB projects: a living
  project journal (PROJECT_JOURNAL.md), checkpoint policy at every phase gate,
  encrypted archive backups uploaded off-box to public file hosts with key
  separation, a BACKUPS.md index with expiry tracking, and a resume playbook for a
  fresh agent with zero context. Use whenever the user says "back up the project",
  "checkpoint", "save progress", "upload the project files", "I lost my sandbox /
  VM / session", "resume where we left off", "restore the project", "update the
  journal", "what's the project status / todo", or any long-running hardware
  project phase transition — continuity is part of every phase gate.
---

# pcb-project-continuity — journal, backups, disaster recovery

Sandboxes die. VMs get reclaimed. Chat contexts truncate. Hardware projects live
for weeks. This skill is the insurance policy: every phase-gate exit includes
"journal updated + verified backup uploaded" (`../../pcb-flow/SKILL.md`), and any
fresh session can resume from a cold start with zero prior context.

**Assume every upload host is public.** Possession of the URL IS access. PCB
projects are frequently proprietary or client IP — plaintext upload of a project
archive is a data breach. The default is encrypt-before-upload, fail closed; the
one exception is the `--allow-plaintext` escape hatch the USER must explicitly
pull after reading the warning.

## 1. The living journal — `PROJECT_JOURNAL.md`

At the project root, updated at EVERY checkpoint (not at the end). Template:
`assets/journal_template.md`. Sections:

1. **Snapshot** — date, current phase, latest backup URL + date. Written for a
   10-second orientation.
2. **Done so far** — with pointers to artifacts (files, not memories).
3. **In progress** — the one or two live threads.
4. **Todo list** — prioritized; EVERY item carries an acceptance criterion
   ("routing done" is not done; "DRC 0 errors + unconnected 0 real + journal
   updated" is).
5. **Decision log** — decision | why | alternatives rejected | when to revisit.
   This is what stops re-litigating solved questions in session N+7.
6. **Project-specific pitfalls & things to avoid** — the mistakes THIS board made
   or nearly made. This list only ever GROWS (an entry is removed only when the
   board it describes is dead).
7. **Open questions & risks**.
8. **Resume playbook** — exactly what a fresh agent must read/open/do next,
   stepwise, with paths. Written for zero context. THIS section is the whole point.
9. **Backup manifest** — pointer to `BACKUPS.md`.

The journal is written so that a capable model with zero prior context can resume
without asking questions. If a resume requires asking the user something, the
journal is deficient — fix the journal, not just the answer.

## 2. Checkpoint policy — when to back up

Checkpoint (journal update FIRST, then archive → upload → verify → index):

- At **every phase gate** of pcb-flow (requirements→…→fab package).
- **Before any risky bulk operation**: autorouter pass, global DRC/class change,
  big refactor, library migration, file-format conversion.
- Every **~1–2 h** of active work on long runs.
- **Immediately** whenever the journal's "next step" is destructive (deleting
  tracks, moving footprints, overwriting files).

Order matters: journal FIRST (it describes the state the archive captures — an
archive without its journal is a puzzle box), then archive, then upload, then
VERIFY (below), then index.

## 3. Archive discipline

**What goes in**: schematic, PCB, libraries, BOM/CPL, gerbers, journal,
`BACKUPS.md`, rules files, harness/project config, scripts specific to this
project. What stays out: caches, 3D model caches over ~100 MB (record their
re-download recipe in the journal instead), `.git/` internals (optional: include
a git bundle instead — smaller and re-cloneable).

**Packing**: `tar.gz`. Full projects commonly exceed **200 MB** — never assume
small; the host chain must cope.

**sha256 of every archive** — recorded in `BACKUPS.md` and verified after every
restore.

**Chunking when a host's limit is below archive size**:
```
split -b 1900M archive.tar.gz.enc archive.tar.gz.enc.part_
# manifest lists parts in order + per-part sha256 + restore recipe:
cat archive.tar.gz.enc.part_* > archive.tar.gz.enc   # glob sorts lexicographically
```

## 4. Encrypt BEFORE upload — mandatory default, fail closed

Every host is public and link-addressable. Rules:

1. **Encrypt every archive (AES-256-class)** using the first available tool,
   probed in order: `age` (keypair) → `openssl enc -aes-256-cbc -pbkdf2` →
   `gpg -c` → Python `cryptography` (if present in the environment; stdlib
   `zipfile` CANNOT write encrypted archives — don't try). Record the method in
   `BACKUPS.md`.
2. **Fresh random key per archive** — never reuse, never store the key in or
   beside the archive.
3. **Key-policy tiers** (`--key-policy`):
   - `split` (default): upload the key as a tiny separate file to a **DIFFERENT
     host** than the archive; record both URLs in `BACKUPS.md` — a future harness
     fetches both and decrypts without a human. URL-secrecy of archive + key on
     different hosts = attacker must compromise two independent links.
   - `human`: print the key ONCE for offline safekeeping, record only "human-held"
     in the index. Strongest. Required default when the journal flags client IP.
     Recovery impossible without the human — by design.
   - `plaintext`: REFUSED unless the user explicitly passed `--allow-plaintext`
     after the tool printed an IP-exposure warning.
4. **No crypto tool available → do not upload. Fail closed.** Print ready-to-run
   manual encrypt+upload commands instead (a human with a residential line can
   run them).
5. `BACKUPS.md` + journal hold the map (which archive where, key where, method,
   sha256) — they are project-internal; the dual-track paste (§7) carries them
   safely off-box.

## 5. Host matrix + upload recipes

Seeded with field-tested data; re-verify live (limits/retention change; rows
marked *unverified* need a probe — procedure below): `references/hosts.md`.

Rules encoded:

- **Verify every upload**: download back and sha256-compare (or the host's own
  checksum — gofile returns md5), or at minimum a size/HEAD check. An unverified
  backup is a hope, not a backup.
- **Never trust a single host**: critical releases get ≥2 copies on different
  hosts. (Single host for intermediate checkpoints is acceptable risk — the next
  checkpoint repairs it.)
- **Probe with a tiny test file** before relying on any host from a new
  environment; record probe result + date in the journal.
- **Log expiry semantics** in `BACKUPS.md` (gofile: ~10-day inactivity expiry →
  schedule re-uploads; filebin: short inactivity-based; catbox permanent but
  datacenter-IP-hostile) — a future session must know when a link dies.
- Cloudflare-challenged hosts: TLS-impersonating HTTP clients sometimes pass —
  an OPTIONAL MANUAL tactic for environments that already have one, never a
  script dependency.
- Environment bootstrap patterns (local-prefix toolchain installs, resumable
  downloads) for the resume case: `references/hosts.md` §resume-notes.

## 6. `scripts/backup.py` — the executor

The suite's only network-capable script (stdlib core; shells out to detected
tools: tar, sha256, split, age/openssl/gpg, curl). Behavior:

```
python scripts/backup.py <project_dir> [--journal PATH] [--hosts gofile,filebin,catbox]
                          [--key-policy split|human|plaintext] [--allow-plaintext]
                          [--split-at 1900M] [--dry-run] [--keep-tar]
```

Packs → hashes → **encrypts (fail closed)** → key policy (split uploads key to a
different host in the chain) → walks the host fallback chain → verifies each
upload → appends to `BACKUPS.md` (date | phase | host | URL | size | sha256 |
cipher+method | key location/policy | expiry note) → refreshes the journal
Snapshot → prints the dual-track manual recipe. On total failure: non-zero exit +
ready-to-run manual commands. Full contract in the script docstring; run
`--dry-run` first on any new environment.

## 7. Journal dual-track (survives link rot)

The journal (+ current `BACKUPS.md`) rides inside every big archive AND is
uploaded as a standalone copy after each phase gate to an end-to-end-encrypted
paste host — PrivateBin on a `never`-expire instance is the canonical choice
(key in the URL fragment; the server sees only ciphertext). Protocol differs
per PrivateBin version: inspect the instance's JS before scripting it — the
recipe is a documented manual step, not a script dependency. Purpose: the
recovery MAP survives even when every big-file link has rotted.

## 8. Resume playbook — cold start

A fresh agent with zero context recovers a project like this:

1. Find the newest `BACKUPS.md`/dual-track journal copy; read the Snapshot +
   Backup manifest (which archive, which host, which key host, which method).
2. Download archive and key file from their respective hosts.
3. Verify sha256 against the manifest.
4. Decrypt with the recorded method:
   `openssl enc -d -aes-256-cbc -pbkdf2 -pass file:key.txt -in a.tar.gz.enc -out a.tar.gz`
   (or `age -d -i key.txt`, or `gpg --batch --passphrase-file key.txt -d`).
5. Unpack; **read `PROJECT_JOURNAL.md` FIRST** — Snapshot, then Resume playbook,
   then Decision log, then Todo.
6. Follow the journal's Resume playbook; verify the current phase's exit criteria
   (`../../pcb-flow/SKILL.md`) before continuing; the first action after any
   destructive step is a new checkpoint.
7. No backup anywhere? Say so plainly; rebuild from the artifacts that DO exist,
   journal from scratch, and checkpoint immediately after reconstruction.

## 9. Provenance note

This skill's behaviors were validated the hard way on a real multi-session board
build: the project survived sandbox loss via exactly this pattern (milestone
checkpoints to off-box hosts, journal-first ordering, recovery from the newest
live bin after the older one expired). The failure that motivated the expiry
logging: the ORIGINAL host bin had silently expired — only the manifest made that
diagnosable in minutes. Field-tested, mechanism-generalized, board-anonymized.
