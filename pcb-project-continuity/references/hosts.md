# Host matrix — upload recipes, limits, gotchas

⚠️ Public file hosts change limits and behavior; treat this table as field-tested
seed data and re-verify with a probe upload (§probe) from each new environment.
Record probe results + dates in the project journal.

| Host | Upload recipe (essentials) | Max size | Retention | Gotchas (field-tested) |
|---|---|---|---|---|
| gofile.io | `GET https://api.gofile.io/servers` → multipart POST field `file` to `https://{server}.gofile.io/contents/uploadfile` | large files OK | deletes after ~10 days with no downloads | inactivity expiry — schedule re-uploads; response JSON includes `md5` — verify with it |
| filebin.net | `curl -T archive.tar.gz.enc https://filebin.net/{bin}/{name}` (client picks the bin id) | large OK | short, inactivity-based — verify | the bin id is the only secret; no auth needed |
| catbox.moe | form POST `reqtype=fileupload` + `fileToUpload=<file>` to `https://catbox.moe/user/api.php` | 500 MB | permanent | rejects datacenter/VPN IPs (`HTTP 412 "Invalid uploader"`) — works from residential lines only |
| pixeldrain | multipart POST field `file` to `https://pixeldrain.com/api/file` | ~10 GB | inactivity-based — verify | API may demand an (anonymous) token now — verify before relying |
| transfer.sh | `curl -T file https://transfer.sh/{name}` | verify (historically GBs) | verify | service has been flaky/for-sale; treat as last resort |
| litterbox.catbox.moe | like catbox + `time=72h` | 1 GB | 72 h | emergency hand-offs only — expires |
| PrivateBin (`never` instance) | JSON POST of AES-GCM-encrypted payload, key lives in the URL fragment; protocol differs per major version — inspect the instance's JS | small (text) | permanent on `never` instances | ideal for a journal-only copy alongside the big archive; server sees only ciphertext |

Default chain (configurable via `--hosts`): **gofile → filebin → catbox**. Rationale:
gofile tolerates size but expires (re-upload discipline needed); filebin is trivially
scriptable; catbox is permanent but datacenter-hostile — the chain covers three
independent failure modes. A `split` key upload skips the archive's host and lands
on the NEXT host in the chain.

## Manual recipes (printable, for humans / offline script use)

```bash
# filebin (bin id of random hex; record both URLs)
BIN=$(head -c6 /dev/urandom | xxd -p)
curl -T project.tar.gz.enc "https://filebin.net/${BIN}/project.tar.gz.enc"
curl -T key.txt          "https://filebin.net/${BIN2}/key.txt"   # DIFFERENT bin!

# gofile
SRV=$(curl -s https://api.gofile.io/servers | grep -o '"server":"[^"]*"' | head -1 | cut -d'"' -f4)
curl -F "file=@project.tar.gz.enc" "https://${SRV}.gofile.io/contents/uploadfile"

# catbox (residential IP)
curl -F "reqtype=fileupload" -F "fileToUpload=@project.tar.gz.enc" https://catbox.moe/user/api.php
```

Encrypt manually (probe order; record which):
```bash
openssl rand -hex 32 > key.txt
openssl enc -aes-256-cbc -pbkdf2 -salt -in project.tar.gz -out project.tar.gz.enc -pass file:key.txt
# decrypt: openssl enc -d -aes-256-cbc -pbkdf2 -in project.tar.gz.enc -out project.tar.gz -pass file:key.txt
```

## Probe procedure (before relying on any host)

1. `echo probe-$(date) > probe.txt` → upload via the host recipe.
2. Verify the download-back (or host checksum) matches.
3. Record in the journal: host, date, result, observed limits.
4. If a probe fails with an HTML challenge page (Cloudflare): the host is
   script-hostile from this environment — optional manual tactic: a
   TLS-impersonating HTTP client, IF the environment already has one, as a human
   decision — never a script dependency.

## Resume-notes: environment bootstrap patterns (field-tested)

- **Toolchain without sudo**: distro .deb packages can be unpacked into a local
  prefix (`$HOME/tool/root`) with env vars exported via a sourced script
  (KICAD_*_DIR-style paths, PYTHONPATH, LD_LIBRARY_PATH) — works for headless
  kicad-cli + python bindings; record the exact env script path in the journal.
- **Large asset downloads** (3D model packages, hundreds of MB): resumable
  `curl -C -` to a cache dir; never restart from zero; journal records the URL +
  expected size so any session can re-fetch.
- **Canonical path discipline**: constrained environments lose access to
  privileged paths (`/root/...`); keep ALL project state under a user-writable
  root and write that path into the journal Snapshot.

## Expiry ledger discipline

`BACKUPS.md` carries an "expiry note" column; fill it from this table plus probe
observations (gofile ~10 d idle, filebin short, litterbox 72 h hard, catbox none).
A re-upload pass is a 5-minute job WHEN the ledger says it's due — schedule it at
every phase gate review rather than hoping. A link that died silently is
indistinguishable from a link that never existed, except by the ledger.
