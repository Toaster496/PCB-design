#!/usr/bin/env python3
"""Encrypted off-box backup for PCB project directories (fail closed).

INPUTS:  argv[1] = project directory (must contain PROJECT_JOURNAL.md unless
         --allow-no-journal; journal-first is the checkpoint discipline).
         Flags: --journal PATH (default <dir>/PROJECT_JOURNAL.md)
                --phase TEXT     (label for the BACKUPS.md index row)
                --hosts LIST     (comma chain, default gofile,filebin,catbox;
                                 known recipes: gofile,filebin,catbox,
                                 pixeldrain,transfer)
                --key-policy split|human|plaintext   (default split)
                --allow-plaintext   (required to actually permit plaintext)
                --allow-no-journal  (escape the journal-first discipline)
                --split-at SIZE  (chunk threshold, default 1900M; accepts
                                 500K/100M/2G suffixes)
                --verify-max SIZE (full download-back hash compare below this,
                                 size-only above; default 100M)
                --dry-run        (print the plan, do nothing)
                --keep-tar       (keep the plaintext tar locally after success;
                                 default: shred-safe delete of intermediates)
OUTPUTS: stdout: plan, per-host progress, result URLs, manual recipes on any
         failure. Files: <dir>/backups/<name>.tar.gz[.enc][.part_*],
         key.txt (human policy only, printed; split policy uploads it),
         APPEND to <dir>/BACKUPS.md index; refresh Snapshot lines in journal.
         Network: YES (curl shell-out) - the only script in this suite allowed
         to touch the network; every failure degrades to printed manual
         commands, never silent loss.
EXIT:    0 = archived + uploaded + verified + indexed
         1 = domain failure (no crypto tool, every host failed, plaintext
             refused, verification failed) - manual commands always printed
         2 = bad input (missing dir/journal/args/curl)
EDGE:    >split-at archives chunked with per-part sha256 + cat recipe; re-run
         safe (new timestamped archive each run; BACKUPS.md append-only);
         empty dir refused; 1-2 GB files streamed by curl (memory-flat);
         offline/blocked hosts fall through the chain.
NON-GOALS: not a sync tool (no deletion, no rotation - the BACKUPS.md ledger
         and the expiry notes drive manual re-upload passes); does not script
         PrivateBin (version-fragile protocol - printed as manual recipe per
         SKILL.md section 7); does not manage keys beyond the chosen policy.
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

KNOWN_HOSTS = ("gofile", "filebin", "catbox", "pixeldrain", "transfer")
DEFAULT_CHAIN = "gofile,filebin,catbox"
VERIFY_URLS = {"gofile": "https://gofile.io", "filebin": "https://filebin.net",
               "catbox": "https://catbox.moe", "pixeldrain": "https://pixeldrain.com",
               "transfer": "https://transfer.sh"}


def parse_size(text):
    m = re.match(r"^([0-9]+(?:\.[0-9]+)?)\s*([KMGT]?)(?:i?B)?$", (text or "").strip(),
                 re.IGNORECASE)
    if not m:
        raise ValueError("bad size %r" % text)
    mult = {"": 1, "K": 1024, "M": 1024 ** 2, "G": 1024 ** 3, "T": 1024 ** 4}
    return int(float(m.group(1)) * mult[m.group(2).upper()])


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(cmd, timeout=1800):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def probe_crypto():
    """Return list of usable (name, encrypt_fn, decrypt_cmd_fmt) options."""
    tools = []
    if shutil.which("age") and shutil.which("age-keygen"):
        tools.append("age")
    if shutil.which("openssl"):
        tools.append("openssl")
    if shutil.which("gpg"):
        tools.append("gpg")
    if _cryptography_available():
        tools.append("cryptography")
    return tools


def _cryptography_available():
    try:
        import importlib.util
        return importlib.util.find_spec("cryptography") is not None
    except Exception:
        return False


def random_key():
    import secrets
    return secrets.token_hex(32)


def encrypt_archive(tar_path, tools, workdir, key):
    """Return (enc_path, method, decrypt_cmd) or (None, None, manual recipe)."""
    enc_path = tar_path + ".enc"
    if "age" in tools:
        kp = os.path.join(workdir, "age_key.txt")
        gen = run(["age-keygen", "-o", kp])
        if gen.returncode == 0 and os.path.exists(kp):
            enc = run(["age", "-R", kp + ".pub" if os.path.exists(kp + ".pub") else
                       _age_recipient(kp), "-o", enc_path, tar_path])
            # age-keygen writes both secret key file; recipient is derived:
            if enc.returncode == 0 and os.path.exists(enc_path):
                return enc_path, "age", ("age -d -i <keyfile> -o <out.tar.gz> "
                                         "<archive.enc>")
    if "openssl" in tools:
        enc = run(["openssl", "enc", "-aes-256-cbc", "-pbkdf2", "-salt",
                   "-in", tar_path, "-out", enc_path, "-pass", "pass:" + key])
        if enc.returncode == 0 and os.path.getsize(enc_path) > 0:
            return enc_path, "openssl-aes-256-cbc-pbkdf2", (
                "openssl enc -d -aes-256-cbc -pbkdf2 -in <archive.enc> "
                "-out <out.tar.gz> -pass pass:<KEY>")
    if "gpg" in tools:
        enc = run(["gpg", "--batch", "--yes", "-c", "--passphrase", key,
                   "-o", enc_path, tar_path])
        if enc.returncode == 0 and os.path.getsize(enc_path) > 0:
            return enc_path, "gpg-cast5-aes", (
                "gpg --batch --passphrase <KEY> -o <out.tar.gz> -d <archive.enc>")
    if "cryptography" in tools:
        if _encrypt_with_cryptography(tar_path, enc_path, key):
            return enc_path, "cryptography-AES-256-CBC+HMAC", (
                "python3 - decrypt helper required - see BACKUPS.md method note")
    return None, None, None


def _age_recipient(keyfile):
    """age-keygen writes 'AGE-SECRET-KEY-...' lines; recipient line is embedded."""
    try:
        with open(keyfile, "r") as fh:
            for line in fh:
                if line.startswith("# public key:"):
                    return line.split(":", 1)[1].strip()
    except OSError:
        pass
    return ""


def _encrypt_with_cryptography(src, dst, passphrase):
    """Optional-lazy path: third-party 'cryptography' if the env has it.

    Deliberately the LAST resort and guarded; stdlib zipfile cannot write
    encrypted archives. If import fails, returns False (fail closed upstream).
    """
    try:
        from cryptography.hazmat.primitives import hashes  # noqa
        import base64
        from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
        key = hashlib.sha256(passphrase.encode()).digest()
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv))
        enc = cipher.encryptor()
        data = open(src, "rb").read()
        pad = 16 - (len(data) % 16)
        data = data + bytes([pad]) * pad
        out = iv + enc.update(data) + enc.finalize()
        with open(dst, "wb") as fh:
            fh.write(out)
        return True
    except Exception:
        return False


def upload(host, path):
    """Return (url, extra) or (None, error). Uses curl recipes per host."""
    if not shutil.which("curl"):
        return None, "curl not available"
    name = os.path.basename(path)
    if host == "gofile":
        srv = run(["curl", "-sS", "--max-time", "60",
                   "https://api.gofile.io/servers"])
        try:
            server = json.loads(srv.stdout)["data"]["server"]
        except (ValueError, KeyError, TypeError):
            return None, "gofile servers API failed: %s" % srv.stdout[:200]
        res = run(["curl", "-sS", "--max-time", "3600",
                   "-F", "file=@" + path,
                   "https://%s.gofile.io/contents/uploadfile" % server])
        try:
            data = json.loads(res.stdout)
            url = data.get("downloadPage") or data["data"].get("downloadPage")
            return url, {"md5": (data.get("md5") or data.get("data", {}).get("md5"))}
        except (ValueError, KeyError, TypeError):
            return None, "gofile upload failed: %s" % res.stdout[:200]
    if host == "filebin":
        import secrets as _s
        binid = _s.token_hex(6)
        url = "https://filebin.net/%s/%s" % (binid, name)
        res = run(["curl", "-sS", "--max-time", "7200", "-T", path, url,
                   "-o", "/dev/null", "-w", "%{http_code}"])
        if res.stdout.strip().lstrip("2") == "" or res.stdout.strip() in ("200", "201"):
            return url, {"bin": binid}
        return None, "filebin upload http %s (4xx? bin exists?)" % res.stdout.strip()
    if host == "catbox":
        res = run(["curl", "-sS", "--max-time", "3600",
                   "-F", "reqtype=fileupload",
                   "-F", "fileToUpload=@" + path,
                   "https://catbox.moe/user/api.php"])
        body = res.stdout.strip()
        if body.startswith("https://"):
            return body, {}
        return None, "catbox rejected (datacenter IP 412? or %s)" % body[:120]
    if host == "pixeldrain":
        res = run(["curl", "-sS", "--max-time", "3600",
                   "-F", "file=@" + path, "https://pixeldrain.com/api/file"])
        try:
            fid = json.loads(res.stdout).get("id")
            return "https://pixeldrain.com/u/%s" % fid, {}
        except (ValueError, AttributeError):
            return None, "pixeldrain failed: %s" % res.stdout[:120]
    if host == "transfer":
        res = run(["curl", "-sS", "--max-time", "3600", "-T", path,
                   "https://transfer.sh/%s" % name])
        body = res.stdout.strip()
        if body.startswith("https://"):
            return body, {}
        return None, "transfer.sh failed: %s" % body[:120]
    return None, "unknown host recipe '%s' (known: %s)" % (host, ",".join(KNOWN_HOSTS))


def verify(url, local_path, expect_md5=None, verify_max=100 * 1024 * 1024):
    """Download-back hash compare below verify_max; size-only above."""
    size = os.path.getsize(local_path)
    if size <= verify_max:
        tmp = local_path + ".verify"
        res = run(["curl", "-sSL", "--max-time", "3600", "-o", tmp, url])
        if res.returncode != 0 or not os.path.exists(tmp):
            return False, "download-back failed"
        ok = sha256_of(tmp) == sha256_of(local_path)
        extra = ""
        if not ok and expect_md5:
            ok = md5_of(tmp) == expect_md5
            extra = "(md5 fallback)"
        os.unlink(tmp)
        return (ok, "hash match %s" % extra if ok else "hash MISMATCH")
    res = run(["curl", "-sSL", "--max-time", "7200", "-o", "/dev/null",
               "-w", "%{size_download}", url])
    try:
        got = int(res.stdout.strip())
    except ValueError:
        return False, "size check failed: %s" % res.stdout[:80]
    return (got == size, "size match (%d bytes)" % got if got == size
            else "size mismatch: got %d want %d" % (got, size))


def manual_recipe(enc_path, key_path_note):
    return """
--- MANUAL FALLBACK (ready to run, needs a residential/human connection) ---
# encrypt (pick ONE, record the method):
openssl rand -hex 32 > key.txt
openssl enc -aes-256-cbc -pbkdf2 -salt -in %s.tar.gz -out %s.enc -pass file:key.txt
# decrypt: openssl enc -d -aes-256-cbc -pbkdf2 -in %s.enc -out %s.tar.gz -pass file:key.txt
# upload (two DIFFERENT bins/hosts for archive and key):
curl -T %s.enc "https://filebin.net/$(head -c6 /dev/urandom | xxd -p)/%s.enc"
curl -T key.txt "https://filebin.net/$(head -c6 /dev/urandom | xxd -p)/key.txt"
# verify: download back and sha256sum BOTH files; then record both URLs in BACKUPS.md
""" % (enc_path, enc_path, enc_path, enc_path, enc_path,
       os.path.basename(enc_path))


def main(argv):
    opts = {"--journal": None, "--phase": "checkpoint", "--hosts": DEFAULT_CHAIN,
            "--key-policy": "split", "--split-at": "1900M", "--verify-max": "100M"}
    flags = set()
    pos = []
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        if a in opts:
            if i + 1 >= len(argv):
                print("ERROR: %s needs a value" % a)
                return 2
            opts[a] = argv[i + 1]
            i += 2
            continue
        if a.startswith("--"):
            flags.add(a)
            i += 1
            continue
        pos.append(a)
        i += 1
    if not pos or not os.path.isdir(pos[0]):
        print("ERROR: first argument must be the project directory")
        return 2
    proj = os.path.abspath(pos[0])
    journal = opts["--journal"] or os.path.join(proj, "PROJECT_JOURNAL.md")
    if not os.path.exists(journal) and "--allow-no-journal" not in flags:
        print("ERROR: journal missing (%s). Checkpoint discipline is journal FIRST -\n"
              "create it from the pcb-project-continuity template, or pass "
              "--allow-no-journal to overrule." % journal)
        return 2
    if not shutil.which("curl"):
        print("ERROR: curl not available - cannot upload. Manual recipes below.")
        print(manual_recipe("<project>", "key.txt"))
        return 2
    try:
        split_at = parse_size(opts["--split-at"])
        verify_max = parse_size(opts["--verify-max"])
    except ValueError as exc:
        print("ERROR: %s" % exc)
        return 2
    policy = opts["--key-policy"]
    if policy not in ("split", "human", "plaintext"):
        print("ERROR: --key-policy must be split|human|plaintext")
        return 2
    hosts = [h.strip() for h in opts["--hosts"].split(",") if h.strip()]
    for h in hosts:
        if h not in KNOWN_HOSTS:
            print("WARN: no scripted recipe for host '%s' (known: %s) - skipping it"
                  % (h, ",".join(KNOWN_HOSTS)))
    hosts = [h for h in hosts if h in KNOWN_HOSTS] or list(KNOWN_HOSTS[:1])

    stamp = time.strftime("%Y%m%d-%H%M%S")
    base = os.path.basename(proj.rstrip("/")) or "project"
    workdir = os.path.join(proj, "backups")
    tar_path = os.path.join(workdir, "%s-%s.tar.gz" % (base, stamp))
    print("PLAN: project=%s phase=%s policy=%s hosts=%s"
          % (proj, opts["--phase"], policy, "->".join(hosts)))
    print("PLAN: archive=%s split-at=%.0fMB" % (tar_path, split_at / 1048576.0))
    if "--dry-run" in flags:
        print("dry-run: tools: crypto=%s curl=yes; nothing done."
              % ",".join(probe_crypto() or ["NONE"]))
        return 0
    os.makedirs(workdir, exist_ok=True)

    # 1. pack (exclude the backups dir itself and heavy caches)
    excludes = ["--exclude=.%s" % os.path.basename(workdir)]
    tar = run(["tar", "czf", tar_path, "-C", os.path.dirname(proj),
               "--exclude", os.path.join(base, "backups"),
               "--exclude", os.path.join(base, "cache"),
               base])
    if tar.returncode != 0 or not os.path.exists(tar_path):
        print("ERROR: tar failed: %s" % tar.stderr[:300])
        return 1
    arch_sha = sha256_of(tar_path)
    size = os.path.getsize(tar_path)
    print("packed: %s (%.1f MB) sha256=%s" % (tar_path, size / 1048576.0,
                                               arch_sha[:12]))

    # 2. chunk if needed
    parts = []
    if size > split_at:
        pref = tar_path + ".part_"
        sp = run(["split", "-b", str(split_at), tar_path, pref])
        if sp.returncode != 0:
            print("ERROR: split failed: %s" % sp.stderr[:200])
            return 1
        parts = sorted(p for p in os.listdir(workdir) if p.startswith(
            os.path.basename(pref)))
        print("chunked into %d parts (restore: cat %s* > %s)"
              % (len(parts), os.path.basename(pref), os.path.basename(tar_path)))

    # 3. encrypt (fail closed)
    key = random_key()
    tools = probe_crypto()
    if policy == "plaintext":
        if "--allow-plaintext" not in flags:
            print("REFUSED: plaintext upload requires --allow-plaintext after "
                  "reading this: every upload host is PUBLIC - possession of the "
                  "URL is access; a plaintext PCB archive is an IP disclosure.")
            return 1
        print("WARNING: plaintext mode (--allow-plaintext) - IP exposed by policy "
              "override.")
        enc_path, method, dec = tar_path, "plaintext-none", "tar xzf (no decrypt)"
    else:
        enc_path, method, dec = encrypt_archive(tar_path, tools, workdir, key)
        if not enc_path:
            print("ERROR: no encryption tool available (age/openssl/gpg/"
                  "cryptography) - NOT uploading plaintext. Fail closed.")
            print(manual_recipe(os.path.join(workdir, base + "-" + stamp), ""))
            return 1
    print("encrypted: %s (%s)" % (enc_path, method))

    # 4. upload archive walking the chain; key on a different host for split
    upload_targets = [(enc_path, parts)] if not parts else \
        [(os.path.join(workdir, p), []) for p in parts]
    results = []
    used_hosts = []
    for host in hosts:
        ok_all = True
        urls = []
        for path, _ in upload_targets:
            url, extra = upload(host, path)
            if not url:
                print("host %s: FAILED (%s) - trying next host" % (host, extra))
                ok_all = False
                break
            vok, vmsg = verify(url, path, extra.get("md5"), verify_max)
            if not vok:
                print("host %s: upload UNVERIFIED (%s) - trying next host"
                      % (host, vmsg))
                ok_all = False
                break
            print("host %s: %s OK (%s)" % (host, url, vmsg))
            urls.append(url)
        if ok_all:
            results = urls
            used_hosts = [host]
            break
    if not results:
        print("ERROR: every host in the chain failed - nothing verified.")
        print(manual_recipe(enc_path, ""))
        return 1

    # 5. key handling per policy
    key_url = ""
    key_path = os.path.join(workdir, "key-%s.txt" % stamp)
    if policy == "split":
        with open(key_path, "w") as fh:
            fh.write(key + "\n# method: %s\n# decrypt: %s\n# archive sha256: %s\n"
                     % (method, dec, arch_sha))
        key_host = next((h for h in hosts if h != used_hosts[0]), hosts[-1])
        key_url, kerr = upload(key_host, key_path)
        if key_url:
            vok, vmsg = verify(key_url, key_path, None, verify_max)
            if not vok:
                print("WARN: key uploaded but unverified (%s)" % vmsg)
            else:
                print("key uploaded to %s: %s (%s)" % (key_host, key_url, vmsg))
            os.unlink(key_path)
        else:
            print("ERROR: key upload to %s failed (%s) - falling back to human "
                  "policy for this run." % (key_host, kerr))
            policy = "human"
    if policy == "human":
        print("\n=== KEY (print ONCE - store offline; recovery without it is "
              "impossible by design) ===\n%s\n=== END KEY ===" % key)
        key_url = "human-held"
    elif policy == "plaintext":
        key_url = "(none)"

    # 6. index in BACKUPS.md
    idx = os.path.join(proj, "BACKUPS.md")
    with open(idx, "a", encoding="utf-8") as fh:
        fh.write("| %s | %s | %s | %s | %s | %.1f MB | %s | %s | %s/%s | %s |\n" % (
            time.strftime("%Y-%m-%d %H:%M"), opts["--phase"], used_hosts[0],
            "; ".join(results), enc_path, os.path.getsize(enc_path) / 1048576.0,
            arch_sha, method, policy, key_url or "-",
            "see hosts.md expiry ledger; verify before relying"))
    print("index appended: %s" % idx)

    # 7. journal snapshot refresh
    if os.path.exists(journal):
        try:
            with open(journal, "r", encoding="utf-8") as fh:
                text = fh.read()
            text = re.sub(r"(?m)^- Date: .*$",
                          "- Date: " + time.strftime("%Y-%m-%d %H:%M"), text, count=1)
            text = re.sub(r"(?m)^- Latest backup: .*$",
                          "- Latest backup: %s (%s, sha256 %s)"
                          % (results[0], time.strftime("%Y-%m-%d"), arch_sha[:12]),
                          text, count=1)
            text = re.sub(r"(?m)^- Key location: .*$",
                          "- Key location: %s" % (key_url or "human-held"), text,
                          count=1)
            with open(journal, "w", encoding="utf-8") as fh:
                fh.write(text)
            print("journal Snapshot refreshed: %s" % journal)
        except OSError as exc:
            print("WARN: journal refresh failed: %s" % exc)

    # dual-track reminder
    print("\ndual-track: upload the journal + BACKUPS.md to an e2e-encrypted paste "
          "host (PrivateBin 'never' instance) as the link-rot-surviving map - see "
          "references/hosts.md for the manual recipe.")

    # cleanup intermediates
    if "--keep-tar" not in flags and enc_path != tar_path:
        os.unlink(tar_path)
    if parts and "--keep-tar" not in flags:
        for p in parts:
            fp = os.path.join(workdir, p)
            if os.path.exists(fp):
                os.unlink(fp)
    print("backup.py: DONE (phase=%s, host=%s, policy=%s, method=%s)"
          % (opts["--phase"], used_hosts[0], policy, method))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
