#!/usr/bin/env python3
"""Validate a PCB net-class rules matrix (CSV) for internal consistency.

INPUTS:  argv[1] = path to CSV with header:
         net_class,clearance_mm,min_width_mm,default_width_mm,max_width_mm,
         via_drill_mm,via_pad_mm,max_current_A,notes
         optional flag --fab-min "trace,space,drill" (mm) defaults "0.15,0.15,0.3"
         (budget quick-turn tier safe values; see SKILL.md section 7)
OUTPUTS: stdout report: one line per finding (WARN/ERROR + explanation), summary
         line, exit code. No files written (pure read-only validation).
         Example: python check_rules.py assets/rules_template.csv
EXIT:    0 = matrix valid | 1 = CSV/schema/consistency ERROR present |
         2 = missing/bad input file or unusable args
EDGE:    empty CSV (header only) => valid trivially with 0 classes checked;
         extra columns ignored; missing max_current_A allowed (blank);
         re-run safe (idempotent read-only); huge files fine (streamed lines).
NON-GOALS: does not compute IPC widths (use SKILL.md tables), does not read EDA
         rule files, does not modify the CSV. It checks internal sanity only.
"""
import csv
import sys

# Conservative sanity band derived from SKILL.md sections 1-4 (IPC-2152-consistent
# rounded 1 oz external defaults). Values outside are WARNed, not failed.
CURRENT_TO_WIDTH_MIN = [
    (0.5, 0.2), (1.0, 0.4), (2.0, 0.8), (3.0, 1.3), (5.0, 2.5), (10.0, 6.0),
]

def width_for_current(amps):
    """Conservative external 1oz width floor for a current (mm)."""
    best = 0.2
    for cur, w in CURRENT_TO_WIDTH_MIN:
        if amps >= cur:
            best = w
    return best

def parse_args(argv):
    if len(argv) < 2 or argv[1] in ("-h", "--help"):
        print(__doc__)
        return None
    path = argv[1]
    fab_min = (0.15, 0.15, 0.3)
    if "--fab-min" in argv:
        i = argv.index("--fab-min")
        try:
            parts = [float(x) for x in argv[i + 1].split(",")]
            if len(parts) != 3:
                raise ValueError
            fab_min = tuple(parts)
        except (ValueError, IndexError):
            print("ERROR: --fab-min expects 'trace,space,drill' in mm, 3 numbers")
            return None
    return path, fab_min

def fnum(row, key):
    val = row.get(key, "").strip()
    if val == "":
        return None
    try:
        return float(val)
    except ValueError:
        raise ValueError("non-numeric value %r in column %s" % (val, key))

def main(argv):
    parsed = parse_args(argv)
    if parsed is None:
        return 2
    path, (fab_trace, fab_space, fab_drill) = parsed
    errors, warnings = [], []
    try:
        fh = open(path, newline="", encoding="utf-8-sig")
    except OSError as exc:
        print("ERROR: cannot read %s (%s)" % (path, exc))
        return 2
    with fh:
        reader = csv.DictReader(fh)
        required = ["net_class", "clearance_mm", "min_width_mm",
                    "default_width_mm", "max_width_mm", "via_drill_mm", "via_pad_mm"]
        missing_cols = [c for c in required if c not in (reader.fieldnames or [])]
        if missing_cols:
            print("ERROR: CSV missing required columns: %s" % ", ".join(missing_cols))
            return 1
        classes = {}
        for lineno, row in enumerate(reader, start=2):
            name = (row.get("net_class") or "").strip()
            if not name:
                continue  # blank line
            if name in classes:
                errors.append("line %d: duplicate net_class '%s'" % (lineno, name))
            classes[name] = (lineno, row)
        if not classes:
            print("WARN: no net classes found (header-only CSV); nothing to check")
            return 0
        for name, (lineno, row) in classes.items():
            label = "'%s' (line %d)" % (name, lineno)
            try:
                clear = fnum(row, "clearance_mm")
                wmin = fnum(row, "min_width_mm")
                wdef = fnum(row, "default_width_mm")
                wmax = fnum(row, "max_width_mm")
                drill = fnum(row, "via_drill_mm")
                pad = fnum(row, "via_pad_mm")
                amps = fnum(row, "max_current_A")
            except ValueError as exc:
                errors.append("%s: %s" % (label, exc))
                continue
            vals = [v for v in (clear, wmin, wdef, wmax, drill, pad) if v is not None]
            if any(v <= 0 for v in vals):
                errors.append("%s: non-positive numeric value present" % label)
            if None in (clear, wmin, wdef, wmax, drill, pad):
                errors.append("%s: missing required numeric field" % label)
                continue
            # width ordering
            if not (wmin <= wdef <= wmax):
                errors.append("%s: width ordering violated (min %.3f <= default %.3f <= max %.3f)"
                              % (label, wmin, wdef, wmax))
            # fab minimums
            if wmin < fab_trace:
                errors.append("%s: min width %.3f below fab minimum %.3f" % (label, wmin, fab_trace))
            if clear < fab_space:
                errors.append("%s: clearance %.3f below fab minimum %.3f" % (label, clear, fab_space))
            if drill < fab_drill:
                errors.append("%s: via drill %.3f below fab minimum %.3f" % (label, drill, fab_drill))
            # annular ring
            ring = (pad - drill) / 2.0
            if ring < 0.125:
                warnings.append("%s: annular ring %.3f mm < 0.125 safe quick-turn default"
                                % (label, ring))
            # current sanity (informational unless flagrantly wrong)
            if amps is not None:
                need = width_for_current(amps)
                if wdef < need:
                    warnings.append("%s: default width %.3f mm thin for %s A "
                                    "(conservative external table suggests >= %.3f mm; verify IPC-2152)"
                                    % (label, wdef, amps, need))
    for msg in warnings:
        print("WARN: " + msg)
    for msg in errors:
        print("ERROR: " + msg)
    status = "VALID" if not errors else "INVALID"
    print("check_rules: %s (%d classes, %d errors, %d warnings)"
          % (status, len(classes), len(errors), len(warnings)))
    return 0 if not errors else 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))
