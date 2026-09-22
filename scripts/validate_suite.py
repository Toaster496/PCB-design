#!/usr/bin/env python3
"""Mechanical acceptance check for the whole pcb-skills suite.

INPUTS:  argv[1] = suite root (default: this script's parent dir). Optional
         --quiet to suppress per-file OK lines.
OUTPUTS: stdout: per-check findings (PASS/FAIL/WARN + file:line where possible),
         summary, final status line. Read-only; writes nothing.
EXIT:    0 = suite passes all mechanical checks | 1 = one or more FAILs |
         2 = usage error (suite root not found)
EDGE:    empty skill dirs flagged; missing evals flagged; >300-line references
         without TOC flagged; non-utf8 files reported (not crashed); re-run safe;
         suites of any size (os.walk streamed).
NON-GOALS: not a style judge: phrasing/pushiness heuristics are WARNs, not
         FAILs; does not run the skills' evals; does not verify numbers'
         physical truth (provenance labels only, string-level).
"""
import ast
import io
import json
import os
import re
import sys

STDLIB_FALLBACK = {
    "argparse", "ast", "base64", "csv", "hashlib", "importlib", "io", "json",
    "os", "re", "secrets", "shutil", "subprocess", "sys", "time", "math",
    "collections", "contextlib", "pathlib", "tempfile", "unittest", "textwrap",
    "types", "typing", "urllib", "uuid", "functools", "itertools", "stat",
    "posixpath", "ntpath", "genericpath", "string", "struct", "warnings",
}
ALLOWED_LAZY = {"cryptography"}  # backup.py's guarded in-function fallback

FRONT_DELIM = re.compile(r"^---\s*$")
NAME_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")
LINK_RE = re.compile(r"\]\(([^)\s]+)\)")
TOC_RE = re.compile(r"^.*(TOC|Table of [Cc]ontents)\s*[:\(]", re.MULTILINE)
CONTRACT_KEYS = ("INPUTS:", "OUTPUTS:", "EXIT:", "EDGE:", "NON-GOALS:")


def parse_frontmatter(path):
    """Return (name, description_str, error) from a SKILL.md."""
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except (OSError, UnicodeDecodeError) as exc:
        return None, None, "unreadable: %s" % exc
    if not lines or not FRONT_DELIM.match(lines[0]):
        return None, None, "missing frontmatter start '---'"
    end = None
    for i, line in enumerate(lines[1:], start=1):
        if FRONT_DELIM.match(line):
            end = i
            break
    if end is None:
        return None, None, "unterminated frontmatter"
    name, desc, desc_buf, in_desc = None, None, [], False
    for line in lines[1:end]:
        if re.match(r"^name:\s*\S", line):
            name = line.split(":", 1)[1].strip()
            in_desc = False
            continue
        if re.match(r"^description:\s*>?-?", line):
            in_desc = True
            rest = line.split(">", 1)[1].lstrip("-").strip() if ">" in line else ""
            if rest:
                desc_buf.append(rest)
            continue
        if in_desc and (line.startswith("  ") or line.startswith("\t")):
            desc_buf.append(line.strip())
            continue
        in_desc = False
    if desc_buf:
        desc = " ".join(desc_buf)
    return name, desc, None


def check_links(path, root):
    """Return list of broken relative-link errors for a markdown file."""
    errors = []
    try:
        text = open(path, encoding="utf-8").read()
    except (OSError, UnicodeDecodeError) as exc:
        return ["unreadable: %s" % exc]
    for m in LINK_RE.finditer(text):
        target = m.group(1)
        if target.startswith(("http://", "https://", "mailto:", "#")):
            continue
        target = target.split("#")[0]
        if not target:
            continue
        resolved = os.path.normpath(os.path.join(os.path.dirname(path), target))
        if not os.path.exists(resolved):
            errors.append("broken link '%s' (resolved %s)" % (target, resolved))
    return errors


def top_level_imports(path):
    """Return (bad_imports, lazy_uncovered) for a python file."""
    try:
        src = open(path, encoding="utf-8").read()
        tree = ast.parse(src)
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return None, "parse failed: %s" % exc
    stdlib = getattr(sys, "stdlib_module_names", None) or STDLIB_FALLBACK
    bad = []
    uncovered = []

    class Visitor(ast.NodeVisitor):
        def __init__(self):
            self.parents = []

        def _check(self, node, mod):
            top = len(self.parents) == 0
            guarded = any(isinstance(p, ast.Try) for p in self.parents)
            if top and mod.split(".")[0] not in stdlib and mod not in ALLOWED_LAZY:
                bad.append("top-level non-stdlib import: %s (line %d)"
                           % (mod, getattr(node, "lineno", 0)))
            if (not top) and guarded and mod.split(".")[0] not in stdlib \
                    and mod not in ALLOWED_LAZY:
                uncovered.append("unguarded-by-allowlist lazy import: %s" % mod)

        def visit_Import(self, node):
            for alias in node.names:
                self._check(node, alias.name)
            self.generic_visit(node)

        def visit_ImportFrom(self, node):
            if node.module:
                self._check(node, node.module)
            self.generic_visit(node)

        def generic_visit(self, node):  # track ancestry
            self.parents.append(node)
            super().generic_visit(node)
            self.parents.pop()

    # ast.NodeVisitor.generic_visit handles children; wrap to track parents
    class ParentVisitor(Visitor):
        def __init__(self):
            super().__init__()
            self.stack = []

        def visit(self, node):
            self.stack.append(node)
            super().visit(node)
            self.stack.pop()

        def _check(self, node, mod):
            top = len(self.stack) <= 1
            guarded = any(isinstance(p, ast.Try) for p in self.stack[:-1])
            if top and mod.split(".")[0] not in stdlib and mod not in ALLOWED_LAZY:
                bad.append("top-level non-stdlib import: %s (line %d)"
                           % (mod, getattr(node, "lineno", 0)))
            if (not top) and not guarded and mod.split(".")[0] not in stdlib:
                uncovered.append("unguarded non-stdlib import in function: %s"
                                 % mod)

    ParentVisitor().visit(tree)
    return bad + uncovered, None


def check_contract_docstring(path):
    src = open(path, encoding="utf-8").read()
    missing = [k for k in CONTRACT_KEYS if k not in src[:4000]]
    if not src.lstrip().startswith(("#!", "'''", '"""')):
        return ["docstring/contract not at top of file"]
    return ["missing contract key %s" % k for k in missing]


def syntax_ok(path):
    """Syntax-check without writing bytecode (py_compile + /dev/null fails on
    some Python builds)."""
    try:
        src = open(path, encoding="utf-8").read()
        compile(src, path, "exec")
        return None
    except (OSError, SyntaxError, UnicodeDecodeError) as exc:
        return str(exc)


def main(argv):
    quiet = "--quiet" in argv
    args = [a for a in argv[1:] if not a.startswith("--")]
    root = os.path.abspath(args[0] if args else
                           os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    if not os.path.isdir(root):
        print("ERROR: suite root not found: %s" % root)
        return 2
    fails, warns, counts = [], [], {"skills": 0, "refs": 0, "scripts": 0,
                                    "evals": 0, "assets": 0}
    # discover skill dirs (contain SKILL.md)
    skill_dirs = sorted(
        d for d in (os.path.join(root, n) for n in os.listdir(root))
        if os.path.isdir(d) and os.path.isfile(os.path.join(d, "SKILL.md")))
    counts["skills"] = len(skill_dirs)
    if len(skill_dirs) < 9:
        warns.append("only %d skills found (suite defines 9)" % len(skill_dirs))

    for d in skill_dirs:
        sk = os.path.join(d, "SKILL.md")
        name, desc, err = parse_frontmatter(sk)
        dname = os.path.basename(d)
        if err:
            fails.append("%s/SKILL.md: %s" % (dname, err))
            continue
        if not NAME_RE.match(name or ""):
            fails.append("%s: name %r invalid (lowercase-hyphen <=64)" % (dname, name))
        if name != dname:
            fails.append("%s: frontmatter name %r != directory %r" % (dname, name, dname))
        if not desc:
            fails.append("%s: description missing" % dname)
        else:
            if len(desc) > 1024:
                fails.append("%s: description %d chars > 1024" % (dname, len(desc)))
            if len(desc) < 150:
                warns.append("%s: description short (%d chars) - pushy trigger "
                             "list recommended" % (dname, len(desc)))
        body_lines = open(sk, encoding="utf-8").read().count("\n") + 1
        if body_lines > 500:
            fails.append("%s/SKILL.md: %d lines > 500" % (dname, body_lines))
        for e in check_links(sk, root):
            fails.append("%s/SKILL.md: %s" % (dname, e))
        if not quiet:
            print("OK  %-24s name=%s desc=%d lines=%d"
                  % (dname, name, len(desc or ""), body_lines))
        # references
        refs = os.path.join(d, "references")
        if os.path.isdir(refs):
            for f in sorted(os.listdir(refs)):
                fp = os.path.join(refs, f)
                counts["refs"] += 1
                text = open(fp, encoding="utf-8").read()
                nlines = text.count("\n") + 1
                if nlines > 300 and not TOC_RE.search("\n".join(
                        text.splitlines()[:40])):
                    fails.append("%s/references/%s: %d lines, no TOC in head"
                                 % (dname, f, nlines))
                for e in check_links(fp, root):
                    fails.append("%s/references/%s: %s" % (dname, f, e))
        # scripts
        scr = os.path.join(d, "scripts")
        if os.path.isdir(scr):
            for f in sorted(os.listdir(scr)):
                if not f.endswith(".py"):
                    continue
                fp = os.path.join(scr, f)
                counts["scripts"] += 1
                perr = syntax_ok(fp)
                if perr:
                    fails.append("%s/scripts/%s: syntax %s" % (dname, f, perr))
                    continue
                bad, perr = top_level_imports(fp)
                if perr:
                    fails.append("%s/scripts/%s: %s" % (dname, f, perr))
                for b in (bad or []):
                    fails.append("%s/scripts/%s: %s" % (dname, f, b))
                for c in check_contract_docstring(fp):
                    fails.append("%s/scripts/%s: %s" % (dname, f, c))
                if "--help" not in open(fp, encoding="utf-8").read():
                    warns.append("%s/scripts/%s: no --help handling seen" % (dname, f))
        # assets
        ass = os.path.join(d, "assets")
        if os.path.isdir(ass):
            counts["assets"] += len(os.listdir(ass))
        # evals
        ev = os.path.join(d, "evals", "evals.json")
        counts["evals"] += 1
        if not os.path.isfile(ev):
            fails.append("%s/evals/evals.json: missing" % dname)
        else:
            try:
                data = json.load(open(ev, encoding="utf-8"))
                skill = data.get("skill_name")
                if skill != dname:
                    fails.append("%s/evals: skill_name %r != dir" % (dname, skill))
                evals = data.get("evals", [])
                if len(evals) < 3:
                    fails.append("%s/evals: only %d evals (<3)" % (dname, len(evals)))
                nearmiss = 0
                for item in evals:
                    for k in ("prompt", "expected_output", "assertions"):
                        if k not in item or not item[k]:
                            fails.append("%s/evals: eval %s missing %s"
                                         % (dname, item.get("id"), k))
                    blob = json.dumps(item).lower()
                    if any(s in blob for s in ("not trigger", "does not trigger",
                                               "no pcb", "does not apply",
                                               "not apply")):
                        nearmiss += 1
                if nearmiss == 0:
                    fails.append("%s/evals: no near-miss should-NOT-trigger eval"
                                 % dname)
            except (ValueError, OSError) as exc:
                fails.append("%s/evals: invalid JSON (%s)" % (dname, exc))
    # suite-level scripts
    sscr = os.path.join(root, "scripts")
    if os.path.isdir(sscr):
        for f in sorted(os.listdir(sscr)):
            if f.endswith(".py"):
                counts["scripts"] += 1
                perr = syntax_ok(os.path.join(sscr, f))
                if perr:
                    fails.append("scripts/%s: syntax %s" % (f, perr))
    for w in warns:
        print("WARN: " + w)
    for f in fails:
        print("FAIL: " + f)
    print("validate_suite: %s (%d skills, %d references, %d scripts, %d eval "
          "files; %d FAIL, %d WARN)"
          % ("PASS" if not fails else "FAIL", counts["skills"], counts["refs"],
             counts["scripts"], counts["evals"], len(fails), len(warns)))
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
