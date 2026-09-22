#!/usr/bin/env python3
"""Pre-release smoke-test audit of a PCB fab (gerber) package directory.

INPUTS:  argv[1] = package directory containing gerbers (and ideally drill +
         .gbrjob). Optional: --stackup-claim N (expected copper layer count,
         default: infer from files); --skip-paste (single-sided assembly boards
         where paste layers are intentionally absent).
OUTPUTS: stdout report: required-file presence (copper/mask/silk/paste/outline/
         drill), Excellon drill format/units sniff, copper layer count vs claim,
         empty/extra user-layer gerbers (KiCad's default job exports every layer),
         and a printable pre-release checklist tail. Read-only: writes nothing.
EXIT:    0 = package passes smoke test | 1 = ERRORS present (missing required
         file class, layer-count mismatch) | 2 = bad input (dir missing/args)
EDGE:    gerbers with CRLF/BOM tolerated (parsed as text, errors ignored);
         non-gerber files in dir ignored; re-run safe (read-only); large
         packages fine (streamed line scan); missing .gbrjob falls back to
         filename heuristics; embedded-header Excellon detected and downgraded
         to warning.
NON-GOALS: NOT a full CAM verifier: no aperture/geometry interpretation, no
         DRC, no netlist compare. The fab's own analyzer remains the second
         opinion. This is the cheap smoke test you run before every upload.
"""
import json
import os
import re
import sys

COPPER_HINTS = ("F_Cu", "B_Cu", "Inner", "In1_Cu", "In2_Cu", "In3_Cu", "In4_Cu",
                ".gtl", ".gbl", ".g2", ".g3", ".g4", ".g5", ".g6")
COPPER_RE = re.compile(r"(?:^|[-_.])(?:(F|B)_Cu|(?:Inner(\d+)|In(\d+))_Cu\.)"
                       r"|\.g(tl|bl|[2-9])$", re.IGNORECASE)
MASK_HINTS = ("F_Mask", "B_Mask", ".gts", ".gbs")
SILK_HINTS = ("F_Silkscreen", "B_Silkscreen", "F_Silk", "B_Silk", ".gto", ".gbo")
PASTE_HINTS = ("F_Paste", "B_Paste", ".gtp", ".gbp")
OUTLINE_HINTS = ("Edge_Cuts", ".gm1", "outline", "boardoutline", "profile")
DRILL_HINTS = (".drl", ".txt", "drill", "nc")
EXTRA_HINTS = ("User", "Eco", "Comments", "Drawings", "Margin", "Adhesive",
               "Courtyard", "Fab", ".gbrjob", ".gko", ".gpi")
DRAW_RE = re.compile(r"D0[123]\b", re.IGNORECASE)


def classify(fname):
    low = fname.lower()
    base = os.path.basename(low)
    if base.endswith(".gbrjob") or base.endswith(".json"):
        return "job", None
    if base.endswith(".drl") or "drill" in base or base.endswith(".nc"):
        return "drill", None
    for hint, cat in ((OUTLINE_HINTS, "outline"), (PASTE_HINTS, "paste"),
                      (MASK_HINTS, "mask"), (SILK_HINTS, "silk")):
        if any(h.lower() in low for h in hint):
            return cat, None
    if COPPER_RE.search(low):
        m = COPPER_RE.search(low)
        layer = None
        token = "".join(g for g in m.groups() if g) if m else ""
        if token.lower() in ("tl", "f_cu", "f"):
            layer = 1
        elif token.lower() in ("bl", "b_cu", "b"):
            layer = 99
        else:
            digits = re.findall(r"\d+", token)
            layer = int(digits[0]) + 1 if digits else None
        return "copper", layer
    if base.endswith((".gbr", ".gbrd", ".ger", ".art", ".pho")) or any(
            h.lower() in low for h in EXTRA_HINTS):
        return "other", None
    return None, None


def sniff_excellon(path):
    """Return (units, format_str, notes) heuristically from the drill head."""
    units, fmt, notes = None, None, []
    try:
        with open(path, "r", errors="replace") as fh:
            for _ in range(80):
                line = fh.readline()
                if not line:
                    break
                t = line.strip()
                if t.upper().startswith("M48"):
                    notes.append("M48 header present")
                if "METRIC" in t.upper():
                    units = "mm"
                elif "INCH" in t.upper() or 'IMPERIAL' in t.upper():
                    units = "inch"
                if t.startswith("FORMAT") or "FORMAT" in t.upper():
                    fmt = t
                if t.upper().startswith("G90"):
                    notes.append("absolute coords (G90)")
        if not any("M48" in n for n in notes):
            notes.append("NO M48 header - embedded/implicit format: verify with fab")
    except OSError as exc:
        notes.append("unreadable: %s" % exc)
    return units, fmt, notes


def gerber_has_draws(path):
    """True if the gerber contains actual exposure commands (not just comments)."""
    try:
        with open(path, "r", errors="replace") as fh:
            for line in fh:
                if DRAW_RE.search(line):
                    return True
    except OSError:
        return True  # unreadable -> assume populated, don't false-positive
    return False


def main(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help") or not os.path.isdir(argv[1]):
        if argv[1:2] and argv[1] in ("-h", "--help"):
            print(__doc__)
            return 0
        print(__doc__)
        return 2
    target = argv[1]
    claim = None
    skip_paste = "--skip-paste" in argv
    if "--stackup-claim" in argv:
        i = argv.index("--stackup-claim")
        try:
            claim = int(argv[i + 1])
        except (ValueError, IndexError):
            print("ERROR: --stackup-claim needs an integer")
            return 2

    files = sorted(os.listdir(target))
    coppers, by_class, empty, drill_files, jobs = {}, {}, [], [], []
    for fname in files:
        cat, layer = classify(fname)
        if cat is None:
            continue
        path = os.path.join(target, fname)
        if cat == "job":
            jobs.append(fname)
            continue
        if cat == "drill":
            drill_files.append(fname)
            continue
        if cat == "copper":
            coppers[layer if layer else fname] = fname
        if cat != "copper":
            by_class.setdefault(cat, []).append(fname)
        if cat == "other" and not gerber_has_draws(path):
            empty.append(fname)

    # gbrjob cross-check (authoritative if present)
    if jobs:
        try:
            with open(os.path.join(target, jobs[0]), encoding="utf-8") as fh:
                job = json.load(fh)
            layers = [f.get("FileFunction", "") for f in job.get("Files", [])]
            job_copper = [l for l in layers if "Copper," in l]
            job_outline = [l for l in layers if "Profile" in l]
            job_drill = [l for l in layers if "Drill" in l or "Plated" in l]
            by_class.setdefault("job-outline", [])
            if job_outline:
                by_class["outline"] = by_class.get("outline", []) or ["(from gbrjob)"]
            if job_drill and not drill_files:
                drill_files.append("(gbrjob declares drill)")
            if job_copper:
                coppers = {i + 1: "(gbrjob L%d)" % (i + 1)
                           for i in range(len(job_copper))}
        except (OSError, ValueError):
            print("WARN: .gbrjob present but unparsable - using filename heuristics")

    errors, warnings = [], []

    def need(class_, label, count=1, optional=False):
        have = by_class.get(class_, [])
        if len(have) < count:
            msg = "missing %s file(s) (found %d of %d)" % (label, len(have), count)
            (warnings if optional else errors).append(msg)

    need("mask", "soldermask", 2)
    need("silk", "silkscreen", 1)
    need("outline", "board outline")
    if not drill_files:
        errors.append("missing drill file (.drl)")
    if not skip_paste:
        need("paste", "paste (or pass --skip-paste)", 2, optional=True)
    copper_count = len([k for k in coppers if k is not None])
    if not copper_count:
        errors.append("no copper layers recognized")
    if claim is not None and copper_count and copper_count != claim:
        errors.append("copper layer count %d != stackup claim %d"
                      % (copper_count, claim))
    if copper_count == 1:
        warnings.append("single copper layer recognized - verify (2-layer min typical)")

    for fname in drill_files:
        if fname.startswith("(gbrjob"):
            continue
        units, fmt, notes = sniff_excellon(os.path.join(target, fname))
        print("drill %s: units=%s %s notes: %s"
              % (fname, units or "UNKNOWN", fmt or "", "; ".join(notes)))
        if units is None:
            warnings.append("drill %s: units not detected (check header)" % fname)

    if empty:
        warnings.append("empty (no draws) non-production layers present: %s "
                        "- harmless but noisy; KiCad default job exports ALL "
                        "layers - consider limiting the gerber job" % ", ".join(empty))

    for w in warnings:
        print("WARN: " + w)
    for e in errors:
        print("ERROR: " + e)
    print("\n--- pre-release checklist (manual) ---")
    print("[ ] copper layers: %d %s" % (copper_count, sorted(
        str(k) for k in coppers)))
    print("[ ] mask: %s | silk: %s | paste: %s | outline: %s | drill: %s"
          % (by_class.get("mask", []), by_class.get("silk", []),
             by_class.get("paste", []) or ("skipped" if skip_paste else []),
             by_class.get("outline", []), drill_files))
    print("[ ] pos.csv + BOM exported from FINAL board; designators reconcile")
    print("[ ] fab notes filled (stackup/finish/copper/qty/impedance)")
    print("[ ] bring-up notes written BEFORE ordering")
    print("[ ] human review where mandated (HV/mains/safety/battery)")
    print("[ ] final backup uploaded + verified (download-back check)")
    status = "PASS" if not errors else "FAIL"
    print("gerber_audit: %s (%d files, %d copper, %d errors, %d warnings)"
          % (status, len(files), copper_count, len(errors), len(warnings)))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
