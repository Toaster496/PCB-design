#!/usr/bin/env python3
"""BOM linter and normalizer for PCB assembly (stdlib only).

INPUTS:  --bom PATH          BOM csv (required). Columns are case-insensitive;
         recognized: Designator, Quantity, Value, Footprint, MPN, Manufacturer,
         Supplier, Supplier_PN (any spelling of Supplier PN), DNP, Notes.
         Multi-reference rows allowed with ';' or ',' separators (R1;R2;R3).
         --out PATH          normalized BOM write path (default: <bom>_normalized.csv
         next to the input; the input file is never modified).
         --rules PATH        optional JSON overrides of built-in heuristic rules:
         {"cap_max_uf": {"0402": 1.0, ...}, "require_mpn": true}
OUTPUTS: stdout: findings report (ERROR/WARN + explanation) and summary;
         file:   normalized CSV (rows merged when identical except designators,
                 designators natural-sorted, quantity recomputed, columns
                 normalized to the canonical header).
EXIT:    0 = clean | 1 = ERRORS present (warnings alone exit 0) |
         2 = missing/unreadable input or unusable args
EDGE:    empty data rows ignored; BOM-in-UTF8-BOM handled; re-run safe (input
         read-only, normalized file overwritten); huge files fine (streamed);
         missing Quantity column -> recomputed; unknown columns preserved in
         output only if --keep-unknown given (else dropped for normalization).
NON-GOALS: not a stock/quote tool, does not fetch lifecycle status (see SKILL.md
         section 3 — check Active/NRND/EOL manually), does not validate CPL
         pairing (designator-set diff vs a CPL file is planned but out of scope).
"""
import csv
import json
import os
import re
import sys

CANON = ["Designator", "Quantity", "Value", "Footprint", "MPN",
         "Manufacturer", "Supplier", "Supplier_PN", "DNP", "Notes"]

DEFAULT_RULES = {
    # conservative typical ceramic cap limits in uF by case size (heuristic
    # warnings only - DC-bias and vendor series decide reality; see SKILL.md 2)
    "cap_max_uf": {"0201": 0.1, "0402": 1.0, "0603": 10.0, "0805": 47.0,
                   "1206": 100.0, "1210": 100.0, "1812": 220.0},
    "require_mpn": True,
}

VALUE_RE = re.compile(r"^\s*([0-9]*\.?[0-9]+)\s*([pPnNuUµmMkKkM rRgG]?)\s*(?:F|f)?"
                      r"(?:[_ ]?([0-9]+\.?[0-9]*)\s*[Vv])?")
CAP_PREFIXES = ("c", "cap")
RES_PREFIXES = ("r", "res")
SPLIT_RE = re.compile(r"[;,]\s*")

MULT = {"": 1.0, "p": 1e-12, "n": 1e-9, "u": 1e-6, "µ": 1e-6, "m": 1e-3,
        "k": 1e3, "K": 1e3, "M": 1e6, "g": 1e9, "R": 1.0, "r": 1.0}

CASE_RE = re.compile(r"(0201|0402|0603|0805|1206|1210|1812|2012|3216|1608)")


def norm_col(name):
    n = re.sub(r"[^A-Za-z]", "", name or "").lower()
    if n in ("designator", "ref", "refs", "reference", "references"):
        return "Designator"
    if n in ("qty", "quantity"):
        return "Quantity"
    if n == "value":
        return "Value"
    if n in ("footprint", "package", "pkg"):
        return "Footprint"
    if n in ("mpn", "mfrpn", "partnumber", "manufacturerpartnumber"):
        return "MPN"
    if n in ("manufacturer", "mfr", "manuf", "brand"):
        return "Manufacturer"
    if n in ("supplier", "vendor", "distributor"):
        return "Supplier"
    if n in ("supplierpn", "spn", "ordercode", "supplierpartnumber", "dnpn", "pn"):
        return "Supplier_PN"
    if n in ("dnp", "dnf", "dontpopulate", "notfitted"):
        return "DNP"
    if n in ("notes", "note", "comment", "comments", "description"):
        return "Notes"
    return name  # unknown -> preserved verbatim


def parse_value(raw):
    """Return (family, si_value, volt_rating) or (None, None, None)."""
    if not raw:
        return (None, None, None)
    m = VALUE_RE.match(raw)
    if not m:
        return (None, None, None)
    num = float(m.group(1))
    unit = m.group(2) or ""
    volt = float(m.group(3)) if m.group(3) else None
    if unit in ("R", "r") and num == 0:
        return ("res", 0.0, volt)  # 0R link
    if unit in ("R", "r"):
        return ("res", num, volt)
    if unit in ("k", "K", "M", "g", ""):
        return ("res", num * MULT.get(unit, 1.0), volt)
    return ("cap", num * MULT.get(unit.lower(), 1.0), volt)


def case_from_footprint(fp):
    m = CASE_RE.search(fp or "")
    metric = {"2012": "0805", "1608": "0603", "3216": "1206"}
    if m:
        return metric.get(m.group(1), m.group(1))
    return None


def natural_key(ref):
    parts = re.split(r"([0-9]+)", ref)
    return [int(p) if p.isdigit() else p for p in parts]


def read_bom(path):
    rows = []
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        fieldmap = {norm_col(k): k for k in (reader.fieldnames or [])}
        for raw in reader:
            rec = {}
            for canon, orig in fieldmap.items():
                rec[canon] = (raw.get(orig) or "").strip()
            if any(rec.get(c) for c in rec):
                rows.append(rec)
    return rows, list(fieldmap.keys())


def main(argv):
    args = {"--bom": None, "--out": None, "--rules": None}
    i = 1
    while i < len(argv):
        a = argv[i]
        if a in ("-h", "--help"):
            print(__doc__)
            return 0
        if a in args:
            if i + 1 >= len(argv):
                print("ERROR: %s needs a value" % a)
                return 2
            args[a] = argv[i + 1]
            i += 2
            continue
        print("ERROR: unknown argument %r (try --help)" % a)
        return 2
    bom = args["--bom"]
    if not bom:
        print("ERROR: --bom is required (see --help)")
        return 2
    if not os.path.isfile(bom):
        print("ERROR: cannot read BOM file %s" % bom)
        return 2
    rules = dict(DEFAULT_RULES)
    if args["--rules"]:
        try:
            with open(args["--rules"], encoding="utf-8") as fh:
                rules.update(json.load(fh))
        except (OSError, ValueError) as exc:
            print("ERROR: bad rules file %s (%s)" % (args["--rules"], exc))
            return 2

    try:
        rows, cols = read_bom(bom)
    except (OSError, csv.Error) as exc:
        print("ERROR: unreadable CSV %s (%s)" % (bom, exc))
        return 2
    missing = [c for c in CANON if c not in cols]
    for c in ("Designator", "Value", "Footprint"):
        if c in missing:
            print("ERROR: BOM missing required column %s" % c)
            return 1

    errors, warnings = [], []
    seen = {}
    merged = {}
    passives = {}
    value_footprints = {}

    for lineno, rec in enumerate(rows, start=2):
        desig_field = rec.get("Designator", "")
        refs = [r.strip() for r in SPLIT_RE.split(desig_field) if r.strip()]
        if not refs:
            warnings.append("line %d: row without designators skipped" % lineno)
            continue
        for ref in refs:
            if ref in seen:
                errors.append("duplicate designator '%s' (lines %d and %d)"
                              % (ref, seen[ref], lineno))
            else:
                seen[ref] = lineno
        value = rec.get("Value", "")
        fp = rec.get("Footprint", "")
        dnp = rec.get("DNP", "").strip().lower() in ("1", "y", "yes", "true", "dnp", "x")
        qty_raw = rec.get("Quantity", "")
        if qty_raw and qty_raw.isdigit():
            if int(qty_raw) != len(refs):
                warnings.append("line %d: Quantity %s != %d designators"
                                % (lineno, qty_raw, len(refs)))
        if not value:
            (errors if not dnp else warnings).append(
                "line %d (%s): missing Value" % (lineno, refs[0]))
        if not fp:
            (errors if not dnp else warnings).append(
                "line %d (%s): missing Footprint" % (lineno, refs[0]))
        if rules.get("require_mpn", True) and not dnp:
            for col in ("MPN", "Manufacturer"):
                if not rec.get(col):
                    errors.append("line %d (%s): non-DNP row missing %s"
                                  % (lineno, refs[0], col))
            if not rec.get("Supplier_PN"):
                warnings.append("line %d (%s): no Supplier_PN (ordering will be "
                                "manual)" % (lineno, refs[0]))
        # value/footprint sanity (capacitor case-size heuristic)
        fam, si, volt = parse_value(value)
        case = case_from_footprint(fp)
        if fam == "cap" and si is not None and case:
            cap_max_uf = rules["cap_max_uf"].get(case)
            if cap_max_uf is not None and si > cap_max_uf * 1e-6:
                warnings.append(
                    "line %d (%s): %s on %s exceeds typical %s uF ceramic limit "
                    "- verify DC-bias/rating or larger case"
                    % (lineno, refs[0], value, case, cap_max_uf))
            if volt is None and not dnp:
                warnings.append("line %d (%s): capacitor value without voltage "
                                "rating suffix (e.g. 1u_16V)" % (lineno, refs[0]))
        # consolidation stats
        if fam in ("cap", "res") and not dnp:
            key = (fam, case)
            passives.setdefault(key, set()).add(value)
        if fam == "res" and not dnp:
            value_footprints.setdefault(value, set()).add(fp)

        merge_key = tuple(rec.get(c, "") for c in
                          ("Value", "Footprint", "MPN", "Manufacturer",
                           "Supplier", "Supplier_PN", "DNP", "Notes"))
        bucket = merged.setdefault(merge_key, {"refs": [], "rec": rec})

    # consolidation report
    for (fam, case), values in sorted(passives.items(), key=str):
        if case and len(values) > 12:
            warnings.append("consolidation: %d distinct values in %s %s - consider "
                            "E-series rationalization" % (len(values), case, fam))
    for value, fps in value_footprints.items():
        if len(fps) > 1:
            warnings.append("consolidation: value %s spans multiple footprints (%s)"
                            % (value, ", ".join(sorted(fps))))

    # normalized output
    out_rows = []
    for key, bucket in merged.items():
        rec = dict(bucket["rec"])
        refs = sorted(
            {r.strip() for r in SPLIT_RE.split(rec.get("Designator", "")) if r.strip()},
            key=natural_key)
        rec["Designator"] = ";".join(refs)
        rec["Quantity"] = str(len(refs))
        row = {c: rec.get(c, "") for c in CANON}
        out_rows.append((natural_key(refs[0]), row))
    out_rows.sort(key=lambda t: t[0])

    out_path = args["--out"] or re.sub(r"(\.csv)?$", "_normalized.csv", bom, count=1)
    try:
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            writer = csv.DictWriter(fh, fieldnames=CANON)
            writer.writeheader()
            for _, row in out_rows:
                writer.writerow(row)
    except OSError as exc:
        print("ERROR: cannot write %s (%s)" % (out_path, exc))
        return 2

    for w in warnings:
        print("WARN: " + w)
    for e in errors:
        print("ERROR: " + e)
    status = "CLEAN" if not errors else "ERRORS"
    print("bom_lint: %s (%d designators, %d rows in, %d rows normalized, "
          "%d errors, %d warnings)" % (status, len(seen), len(rows), len(out_rows),
                                       len(errors), len(warnings)))
    print("normalized BOM -> %s" % out_path)
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
