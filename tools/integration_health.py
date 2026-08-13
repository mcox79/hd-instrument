#!/usr/bin/env python3
"""Integration-health tripwire: catch proven-but-unwired capabilities before they pile up.

The substrate's failure mode (2026-07-25 audit): capabilities get proven in exp_ cells,
VET'd, atomized -- and left as ISLANDS. The atom store records the CLAIM, never the CODE.
This script makes detection AUTOMATIC + CHEAP so the debt can't silently accumulate again.

Reports:
  1. PROMOTE candidates: exp_ modules imported by >= K OTHER cells (de-facto shared code
     trapped in experiments/ that should live in hdlab/).
  2. Frontier bypass: how many cells import `from experiments import ...` (the exp-as-module
     smell); and whether a designated composed entry exists.
  3. Dead hdlab modules: core-library modules with ~0 consumers (quarantine candidates).

Run standalone (prints report) or on a cadence (cron / meta_audit). ASCII-only, stdlib-only.
"""
from __future__ import annotations
import io
import os
import posixpath
import re
import sys
import tokenize
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXP_DIR = os.path.join(ROOT, "experiments")
HDLAB_DIR = os.path.join(ROOT, "hdlab")
PROMOTE_MIN_CONSUMERS = 3          # exp module imported by >=3 others = promotion candidate
COMPOSED_ENTRY_CANDIDATES = ("reasoner.py", "substrate.py", "pipeline.py")

# ---------------------------------------------------------------------------
# D4 FIX (2026-08-13): THE GRAPH WAS BLIND TO WHOLE DIRECTORIES.
#
# compute_import_graph() used to read exactly two directories, NON-recursively:
# experiments/ and hdlab/ (`_pyfiles` = os.listdir). Everything else in the repo was
# invisible as an IMPORTER. Consequences, all in the FALSE-ISLAND direction (the more
# dangerous one -- it makes us "wire" what is already wired, or shelve live capability):
#   * tools/ -> tools/ edges did not exist at all. tools/inflight_monitor.py is imported
#     at tools/dash_gui.py:54 (`from inflight_monitor import build_state, ...`) and read
#     as a zero-consumer ISLAND.
#   * verification/ was never scanned, so a module whose only importer is a certification
#     witness read as an ISLAND (hdlab/parse_goal_extraction.py, imported at
#     verification/test_parse_goal_extraction.py:37).
#   * backend/ and scripts/ likewise.
#   * hdlab SUBPACKAGES (hdlab/dashboard/, hdlab/learner/, hdlab/learner/plugins/) were
#     never scanned, so an intra-subpackage relative import was invisible.
#
# The fix scans WIDE_SCAN_DIRS recursively (skipping vendored/venv/cache dirs -- note
# tools/dashboard/.venv alone holds 6250 .py files) and resolves imports to CONCRETE
# repo-relative FILE PATHS via a module index, instead of matching bare stems. The legacy
# stem-keyed maps (exp_module_consumers / hdlab_consumers) are preserved verbatim in shape
# and KEY SET -- they just see more importer files now -- so every existing caller and
# witness keeps working; the new path-keyed data rides along on the returned ImportGraph
# object as `.path_consumers` / `.path_consumer_sites`.
#
# Dynamic imports: `importlib.import_module("literal")` / `__import__("literal")` ARE
# resolved (cheap, the literal is right there). Non-literal ones (a variable, an f-string,
# a name built at runtime) CANNOT be resolved statically -- they are NOT silently dropped,
# they are recorded in `.undetectable_dynamic_imports` with file:line so the blind spot is
# visible rather than assumed away.
# ---------------------------------------------------------------------------

WIDE_SCAN_DIRS = ("experiments", "hdlab", "tools", "verification", "backend", "scripts")
SKIP_DIR_NAMES = {
    ".venv", "venv", "env", "__pycache__", "node_modules", "site-packages",
    ".git", ".tmp_scan", ".mypy_cache", ".pytest_cache", ".ruff_cache",
    ".hypothesis", "build", "dist", ".ipynb_checkpoints",
}
try:                                     # py3.10+
    _STDLIB_NAMES = set(sys.stdlib_module_names)
except AttributeError:                   # pragma: no cover -- older interpreters
    _STDLIB_NAMES = set()

# import patterns
RE_FROM_EXP = re.compile(r"^\s*from\s+experiments\s+import\s+(.+)", re.M)
RE_FROM_EXP_SUB = re.compile(r"^\s*from\s+experiments\.([A-Za-z0-9_]+)\s+import", re.M)
RE_IMPORT_EXP_SUB = re.compile(r"^\s*import\s+experiments\.([A-Za-z0-9_]+)", re.M)
# BARE cell-to-cell imports (2026-08-12 fix). The DOMINANT idiom in experiments/ is
# `sys.path.insert(0, EXP_DIR)` followed by `import exp_other_cell as v1` / `from exp_other_cell
# import helper` -- NO `experiments.` prefix, so the three patterns above never matched it and
# every such consumer edge was invisible. That produced FALSE `ISLAND` verdicts in
# capability_registry_audit.compute_integration_status for exp-cell rows whose only consumers are
# other cells (proven case: exp_maven_ere_convergence_gated_subevent_v1 imports
# exp_maven_ere_convergence_gated_causal_v1/_v2, yet both causal rows read ISLAND/used_by=[]).
# Names are filtered against the real experiments/ basename set, so stdlib/3rd-party imports
# cannot produce spurious edges.
RE_IMPORT_BARE = re.compile(r"^\s*import\s+([A-Za-z_][A-Za-z0-9_,\s]*?)\s*(?:#.*)?$", re.M)
RE_FROM_BARE = re.compile(r"^\s*from\s+([A-Za-z_][A-Za-z0-9_]*)\s+import", re.M)
RE_FROM_HDLAB = re.compile(r"^\s*from\s+hdlab\.([A-Za-z0-9_]+)\s+import", re.M)
RE_FROM_HDLAB_BARE = re.compile(r"^\s*from\s+hdlab\s+import\s+(.+)", re.M)
RE_HDLAB_ATTR = re.compile(r"\bhdlab\.([A-Za-z0-9_]+)")
RE_REL = re.compile(r"^\s*from\s+\.([A-Za-z0-9_]+)\s+import", re.M)   # relative, inside hdlab
RE_REL_BARE = re.compile(r"^\s*from\s+\.\s+import\s+(.+)", re.M)      # `from . import a, b` (e.g. __init__ re-export)


def _pyfiles(d):
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in os.listdir(d) if f.endswith(".py")]


def _read(p):
    try:
        with open(p, "r", encoding="utf-8", errors="replace") as fh:
            return fh.read()
    except Exception:
        return ""


# ---------------------------------------------------------------------------
# D3 FIX (2026-08-13, notes/registry_tighten_audit_2026-08-13.md defect D3): every
# regex below is applied to RAW source text, so a module name inside a STRING LITERAL
# or a COMMENT counts as an import edge. RE_HDLAB_ATTR (bare `hdlab.foo` text match) is
# the worst offender: atomize / cert-ledger scripts carry data literals like
# ("hdlab.perceptron", "StructuredPerceptron"), which made hdlab/perceptron.py read as
# 145 consumers when ground truth is 1. Fix: tokenize the source and blank out every
# STRING and COMMENT token before matching, so only REAL CODE is ever matched. Character
# positions and newlines are preserved so the `^\s*from ...` line-anchored patterns keep
# working unchanged. Files that fail to tokenize (syntax errors, py2 leftovers) fall back
# to raw text and are RECORDED in CODE_ONLY_PARSE_FAILURES rather than silently trusted.
# ---------------------------------------------------------------------------

CODE_ONLY_PARSE_FAILURES: list[str] = []


def strip_strings_and_comments(src):
    """Blank out STRING/COMMENT tokens (spaces), preserving line+column structure.

    Returns (code_only_text, ok). ok=False means tokenize failed and the RAW text is
    returned unchanged (caller must treat any match from it as unverified).
    """
    if not src:
        return src, True
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(src).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError, ValueError):
        return src, False
    buf = [list(line) for line in src.splitlines(keepends=True)]
    for tok in toks:
        if tok.type not in (tokenize.STRING, tokenize.COMMENT):
            continue
        (srow, scol), (erow, ecol) = tok.start, tok.end
        for row in range(srow, erow + 1):
            i = row - 1
            if i < 0 or i >= len(buf):
                continue
            line = buf[i]
            a = scol if row == srow else 0
            b = ecol if row == erow else len(line)
            for c in range(a, min(b, len(line))):
                if line[c] not in ("\n", "\r"):
                    line[c] = " "
    return "".join("".join(line) for line in buf), True


def _read_code(p):
    """_read() with string literals and comments blanked out -- see D3 note above."""
    src = _read(p)
    out, ok = strip_strings_and_comments(src)
    if not ok:
        CODE_ONLY_PARSE_FAILURES.append(str(p).replace("\\", "/"))
    return out


def _names(chunk):
    # parse an import list like "a as x, b, c" -> ['a','b','c']
    out = []
    for part in chunk.split(","):
        part = part.strip()
        if not part:
            continue
        out.append(part.split(" as ")[0].split("#")[0].strip().strip("()"))
    return [n for n in out if n and n.isidentifier()]


# ---------------------------------------------------------------------------
# D4 machinery: recursive scan, module index, real statement-level resolver.
# ---------------------------------------------------------------------------

def _walk_pyfiles(root, rel_dir):
    """Recursive *.py under root/rel_dir, skipping vendored/venv/cache dirs. Sorted."""
    base = os.path.join(root, rel_dir)
    if not os.path.isdir(base):
        return []
    out = []
    for dirpath, dirnames, filenames in os.walk(base):
        dirnames[:] = sorted(d for d in dirnames
                             if d not in SKIP_DIR_NAMES and not d.startswith("."))
        for f in sorted(filenames):
            if f.endswith(".py"):
                out.append(os.path.join(dirpath, f))
    return sorted(set(out))


def _relpath(root, p):
    return os.path.relpath(p, root).replace("\\", "/")


def _dotted_of_rel(rel):
    """'hdlab/learner/plugins/x.py' -> 'hdlab.learner.plugins.x';
    'hdlab/learner/__init__.py' -> 'hdlab.learner'."""
    stem = rel[:-3] if rel.endswith(".py") else rel
    if stem.endswith("/__init__"):
        stem = stem[:-len("/__init__")]
    return stem.replace("/", ".")


_MODULE_INDEX_CACHE: dict = {}


def build_module_index(root=None, dirs=WIDE_SCAN_DIRS, use_cache=True):
    """{dotted module name -> repo-relative file path} over the wide scan set.

    Cached per (root, dirs) because the whole-repo walk is re-derived by several
    callers (the graph, the pipeline closure, the composed closure) in one audit run.
    """
    root = root or ROOT
    key = (os.path.abspath(str(root)), tuple(dirs))
    if use_cache and key in _MODULE_INDEX_CACHE:
        return _MODULE_INDEX_CACHE[key]
    index = {}
    files = []
    for d in dirs:
        for p in _walk_pyfiles(str(root), d):
            rel = _relpath(str(root), p)
            files.append(rel)
            index.setdefault(_dotted_of_rel(rel), rel)
    files = sorted(set(files))
    out = (index, files)
    if use_cache:
        _MODULE_INDEX_CACHE[key] = out
    return out


_RE_FROM_STMT = re.compile(r"^from\s+([.\w]+)\s+import\s+(.*)$")
_RE_IMPORT_STMT = re.compile(r"^import\s+(.*)$")
_RE_DYNAMIC = re.compile(r"(?:importlib\s*\.\s*import_module|__import__)\s*\(\s*([^)]*)")
_RE_DYN_LITERAL = re.compile(r"^[rbuf]{0,2}['\"]([A-Za-z_][\w.]*)['\"]")
_RE_UPPER_VAR = re.compile(r"\b([A-Z][A-Z0-9_]{2,})\b")


def _dotted_names(chunk):
    """Parse an import list allowing dotted names: 'a.b as x, c' -> ['a.b', 'c']."""
    out = []
    for part in chunk.split(","):
        part = part.split(" as ")[0].split("#")[0].strip().strip("()").strip()
        if not part or part == "*":
            continue
        if all(seg.isidentifier() for seg in part.split(".") if seg != ""):
            out.append(part)
    return out


def iter_import_statements(code_src):
    """Yield (lineno, kind, module_ref, names_chunk) for every real import statement.

    `code_src` must already have strings/comments blanked (_read_code), so an import
    inside a docstring is never seen. Parenthesised and backslash continuations are
    joined so `from x import (\\n a,\\n b)` yields both names. Indented (deferred,
    inside-function) imports COUNT -- they are real edges (hdlab/situation_model_
    accumulate.py imports its multibank sibling exactly that way).
    """
    lines = code_src.splitlines()
    n = len(lines)
    i = 0
    while i < n:
        stripped = lines[i].strip()
        lineno = i + 1
        if stripped.startswith("import ") or stripped.startswith("from "):
            stmt = stripped
            guard = 0
            while (stmt.count("(") > stmt.count(")") or stmt.endswith("\\")) and i + 1 < n and guard < 40:
                i += 1
                guard += 1
                stmt = stmt.rstrip("\\").rstrip() + " " + lines[i].strip()
            m = _RE_FROM_STMT.match(stmt)
            if m:
                yield (lineno, "from", m.group(1), m.group(2))
            else:
                m2 = _RE_IMPORT_STMT.match(stmt)
                if m2:
                    yield (lineno, "import", None, m2.group(1))
        i += 1


def sys_path_hint_dirs(raw_src):
    """Top-level scan dirs this file inserts onto sys.path.

    The `sys.path.insert(0, EXP_DIR)` idiom is what makes a BARE `import exp_other`
    resolve at runtime. The directory name usually lives in a STRING LITERAL, which
    _read_code() blanks -- so this reads the RAW source, and follows one level of
    ALL_CAPS variable indirection (`EXP_DIR = os.path.join(ROOT, "experiments")`).
    """
    if "sys.path" not in raw_src:
        return set()
    syslines = [ln for ln in raw_src.splitlines()
                if "sys.path.insert" in ln or "sys.path.append" in ln]
    if not syslines:
        return set()
    blob = " ".join(syslines)
    for var in sorted(set(_RE_UPPER_VAR.findall(blob))):
        for m in re.finditer(r"^\s*" + re.escape(var) + r"\s*=.*$", raw_src, re.M):
            blob += " " + m.group(0)
    return {d for d in WIDE_SCAN_DIRS if d in blob}


def _resolve_target(base_dotted, names_chunk, index, targets):
    if base_dotted in index:
        targets.add(index[base_dotted])
    for nm in _dotted_names(names_chunk or ""):
        sub = base_dotted + "." + nm if base_dotted else nm
        if sub in index:
            targets.add(index[sub])


def file_import_edges(rel_file, code_src, raw_src, index):
    """Return (edges, dynamic_unresolved).

    edges = sorted list of (target_rel_path, lineno). dynamic_unresolved = list of
    {"file","line","expr"} for importlib/__import__ calls whose argument is not a
    plain string literal (statically unresolvable -- recorded, never silently dropped).
    """
    edges = set()
    dyn = []
    dir_dotted = posixpath.dirname(rel_file).replace("/", ".")
    hints = sys_path_hint_dirs(raw_src)

    for lineno, kind, module_ref, names_chunk in iter_import_statements(code_src):
        targets = set()
        if kind == "from":
            level = len(module_ref) - len(module_ref.lstrip("."))
            tail = module_ref[level:]
            if level == 0:
                bases = [tail]
                if "." not in tail and tail not in _STDLIB_NAMES and tail not in index:
                    if dir_dotted:
                        bases.append(f"{dir_dotted}.{tail}")
                    bases.extend(f"{h}.{tail}" for h in sorted(hints))
            else:
                parts = [x for x in dir_dotted.split(".") if x]
                up = parts[:len(parts) - (level - 1)] if level > 1 else parts
                bases = [".".join(up + ([tail] if tail else []))]
            for b in bases:
                if b:
                    _resolve_target(b, names_chunk, index, targets)
        else:
            for item in _dotted_names(names_chunk):
                cands = [item]
                if "." not in item and item not in _STDLIB_NAMES and item not in index:
                    if dir_dotted:
                        cands.append(f"{dir_dotted}.{item}")
                    cands.extend(f"{h}.{item}" for h in sorted(hints))
                for c in cands:
                    if c in index:
                        targets.add(index[c])
        for t in targets:
            if t != rel_file:
                edges.add((t, lineno))

    # dynamic imports -- resolve string literals, RECORD the rest
    if "import_module" in raw_src or "__import__" in raw_src:
        for i, ln in enumerate(raw_src.splitlines(), start=1):
            for m in _RE_DYNAMIC.finditer(ln):
                arg = m.group(1).strip()
                lit = _RE_DYN_LITERAL.match(arg)
                if lit:
                    dotted = lit.group(1)
                    if dotted in index and index[dotted] != rel_file:
                        edges.add((index[dotted], i))
                    continue
                dyn.append({"file": rel_file, "line": i, "expr": arg[:80]})
    return sorted(edges), dyn


class ImportGraph:
    """The legacy 6-tuple, plus the D4 path-keyed data.

    Iterates/indexes EXACTLY as the old `return (a, b, c, d, e, f)` tuple did, so
    `x, y, z, ... = compute_import_graph()` and `compute_import_graph()[1]` keep working
    unchanged (existing witnesses depend on both forms). New consumers read the extra
    attributes; a caller handed a plain 6-tuple (e.g. a test fixture) simply sees no
    path_consumers, which is the old behaviour.
    """

    __slots__ = ("exp_module_consumers", "hdlab_consumers", "bypass_cells", "exp_files",
                 "hdlab_files", "hdlab_mods", "path_consumers", "path_consumer_sites",
                 "scanned_files", "scanned_dirs", "undetectable_dynamic_imports", "wide")

    def __init__(self, exp_module_consumers, hdlab_consumers, bypass_cells, exp_files,
                 hdlab_files, hdlab_mods, path_consumers=None, path_consumer_sites=None,
                 scanned_files=(), scanned_dirs=(), undetectable_dynamic_imports=(), wide=False):
        self.exp_module_consumers = exp_module_consumers
        self.hdlab_consumers = hdlab_consumers
        self.bypass_cells = bypass_cells
        self.exp_files = exp_files
        self.hdlab_files = hdlab_files
        self.hdlab_mods = hdlab_mods
        self.path_consumers = path_consumers if path_consumers is not None else {}
        self.path_consumer_sites = path_consumer_sites if path_consumer_sites is not None else {}
        self.scanned_files = list(scanned_files)
        self.scanned_dirs = list(scanned_dirs)
        self.undetectable_dynamic_imports = list(undetectable_dynamic_imports)
        self.wide = wide

    def _tuple(self):
        return (self.exp_module_consumers, self.hdlab_consumers, self.bypass_cells,
                self.exp_files, self.hdlab_files, self.hdlab_mods)

    def __iter__(self):
        return iter(self._tuple())

    def __len__(self):
        return 6

    def __getitem__(self, i):
        return self._tuple()[i]


def compute_import_graph(exp_dir=EXP_DIR, hdlab_dir=HDLAB_DIR, root=None, wide=None):
    """Reusable core: build the repo import graph.

    Returns an ImportGraph that unpacks as the historical 6-tuple
    (exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files,
    hdlab_mods) so callers (this script's main(), capability_registry_audit.py) share ONE
    computation instead of re-deriving the regex logic, and additionally carries the D4
    path-keyed maps. Pure function, no I/O side effects besides reading source files.

    wide=True (the default whenever the real repo dirs are in play) scans
    WIDE_SCAN_DIRS recursively as IMPORTERS -- see the D4 note at the top of this file.
    Passing explicit fixture dirs (as the D3 witness does) keeps the old two-directory
    behaviour so fixture tests stay hermetic.
    """
    if root is not None:
        scan_root = str(root)
        exp_dir = os.path.join(scan_root, "experiments")
        hdlab_dir = os.path.join(scan_root, "hdlab")
        wide = True if wide is None else wide
    else:
        scan_root = ROOT
        if wide is None:
            wide = (os.path.abspath(exp_dir) == os.path.abspath(EXP_DIR)
                    and os.path.abspath(hdlab_dir) == os.path.abspath(HDLAB_DIR))

    exp_files = _pyfiles(exp_dir)
    hdlab_files = _pyfiles(hdlab_dir)
    hdlab_mods = {os.path.basename(f)[:-3] for f in hdlab_files} - {"__init__"}
    exp_mods = {os.path.basename(f)[:-3] for f in exp_files} - {"__init__"}

    exp_module_consumers = defaultdict(set)   # exp_module -> set of files importing it as a module
    hdlab_consumers = defaultdict(set)        # hdlab_module -> set of consumer files
    bypass_cells = set()                      # cells doing `from experiments import ...`

    if wide:
        index, wide_rel_files = build_module_index(scan_root)
        all_files = [os.path.join(scan_root, r.replace("/", os.sep)) for r in wide_rel_files]
        scanned_dirs = [d for d in WIDE_SCAN_DIRS if os.path.isdir(os.path.join(scan_root, d))]
    else:
        index, wide_rel_files, scanned_dirs = {}, [], []
        all_files = sorted(set(exp_files + hdlab_files))

    path_consumers = defaultdict(set)
    path_consumer_sites = defaultdict(set)
    dynamic_unresolved = []
    hdlab_dir_abs = os.path.abspath(hdlab_dir)

    for p in all_files:
        base = os.path.basename(p)[:-3]
        raw = _read(p)
        src, ok = strip_strings_and_comments(raw)   # D3: strings/comments blanked
        if not ok:
            CODE_ONLY_PARSE_FAILURES.append(str(p).replace("\\", "/"))

        if wide:
            rel = _relpath(scan_root, p)
            edges, dyn = file_import_edges(rel, src, raw, index)
            for target, lineno in edges:
                path_consumers[target].add(rel)
                path_consumer_sites[target].add(f"{rel}:{lineno}")
            dynamic_unresolved.extend(dyn)

        # exp-as-module imports
        got_exp = False
        for m in RE_FROM_EXP.finditer(src):
            for n in _names(m.group(1)):
                # exp_mods filter (2026-08-12): `from experiments import (  # noqa: E402,F401`
                # previously yielded a phantom consumer edge for the module name "F401".
                if n in exp_mods and n != base:
                    exp_module_consumers[n].add(p)
                    got_exp = True
        for rex in (RE_FROM_EXP_SUB, RE_IMPORT_EXP_SUB):
            for m in rex.finditer(src):
                n = m.group(1)
                if n != base:
                    exp_module_consumers[n].add(p)
                    got_exp = True
        # bare `import exp_other` / `from exp_other import x` (sys.path-inserted cell-to-cell)
        for m in RE_IMPORT_BARE.finditer(src):
            for n in _names(m.group(1)):
                if n in exp_mods and n != base:
                    exp_module_consumers[n].add(p)
                    got_exp = True
        for m in RE_FROM_BARE.finditer(src):
            n = m.group(1)
            if n in exp_mods and n != base:
                exp_module_consumers[n].add(p)
                got_exp = True
        if got_exp:
            bypass_cells.add(p)
        # hdlab consumers (absolute)
        for rex in (RE_FROM_HDLAB, RE_HDLAB_ATTR):
            for m in rex.finditer(src):
                mod = m.group(1)
                if mod in hdlab_mods and mod != base:
                    hdlab_consumers[mod].add(p)
        for m in RE_FROM_HDLAB_BARE.finditer(src):
            for n in _names(m.group(1)):
                if n in hdlab_mods and n != base:
                    hdlab_consumers[n].add(p)
        # relative imports (only meaningful for files sitting DIRECTLY in hdlab/ --
        # inside a subpackage `from .x import` means hdlab/<pkg>/x.py, NOT hdlab/x.py;
        # those are resolved correctly by the D4 path resolver above instead).
        if os.path.abspath(os.path.dirname(p)) == hdlab_dir_abs:
            for m in RE_REL.finditer(src):
                mod = m.group(1)
                if mod in hdlab_mods and mod != base:
                    hdlab_consumers[mod].add(p)
            for m in RE_REL_BARE.finditer(src):
                for n in _names(m.group(1)):
                    if n in hdlab_mods and n != base:
                        hdlab_consumers[n].add(p)

    # Merge the D4 path-resolved edges back into the legacy stem-keyed maps. KEY SETS ARE
    # NOT WIDENED (only stems that are real experiments/ or hdlab/ top-level modules are
    # touched) -- verify_integration_health_import_graph.py asserts exactly that invariant.
    if wide:
        for mod in sorted(exp_mods):
            extra = sorted(r for r in path_consumers.get(f"experiments/{mod}.py", ())
                           if posixpath.basename(r) != f"{mod}.py")
            if extra:
                exp_module_consumers[mod] |= {os.path.join(scan_root, r.replace("/", os.sep))
                                              for r in extra}
        for mod in sorted(hdlab_mods):
            extra = sorted(r for r in path_consumers.get(f"hdlab/{mod}.py", ())
                           if posixpath.basename(r) != f"{mod}.py")
            if extra:
                hdlab_consumers[mod] |= {os.path.join(scan_root, r.replace("/", os.sep))
                                         for r in extra}

    return ImportGraph(
        exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files, hdlab_mods,
        path_consumers={k: set(v) for k, v in path_consumers.items()},
        path_consumer_sites={k: sorted(v) for k, v in path_consumer_sites.items()},
        scanned_files=wide_rel_files, scanned_dirs=scanned_dirs,
        undetectable_dynamic_imports=dynamic_unresolved, wide=wide,
    )


def main():
    graph = compute_import_graph()
    exp_module_consumers, hdlab_consumers, bypass_cells, exp_files, hdlab_files, hdlab_mods = graph

    # ---- report ----
    print("=" * 72)
    print("INTEGRATION HEALTH  (%d exp cells, %d hdlab modules)" % (len(exp_files), len(hdlab_mods)))
    print("=" * 72)
    print("[scan] dirs=%s  files=%d  wide=%s  unresolvable-dynamic-imports=%d"
          % (",".join(graph.scanned_dirs), len(graph.scanned_files), graph.wide,
             len(graph.undetectable_dynamic_imports)))

    # 1. promotion candidates
    promote = sorted(
        ((len(c), n) for n, c in exp_module_consumers.items() if len(c) >= PROMOTE_MIN_CONSUMERS),
        reverse=True,
    )
    print("\n[1] PROMOTE CANDIDATES -- exp_ modules imported as shared code by >= %d cells" % PROMOTE_MIN_CONSUMERS)
    print("    (de-facto library trapped in experiments/ -> should be promoted to hdlab/)")
    if not promote:
        print("    (none -- clean)")
    for n_consumers, name in promote[:30]:
        print("    %3d  %s" % (n_consumers, name))
    if len(promote) > 30:
        print("    ... +%d more" % (len(promote) - 30))

    # 2. bypass + composed entry
    print("\n[2] FRONTIER BYPASS")
    print("    cells importing `from experiments import ...` (exp-as-module): %d / %d"
          % (len(bypass_cells), len(exp_files)))
    entry = [c for c in COMPOSED_ENTRY_CANDIDATES if os.path.exists(os.path.join(HDLAB_DIR, c))]
    print("    composed substrate entry (%s): %s"
          % ("/".join(COMPOSED_ENTRY_CANDIDATES), (", ".join(entry) if entry else "ABSENT -- no wired 'run the substrate' entry")))

    # 3. dead hdlab modules
    dead = sorted(m for m in hdlab_mods if len(hdlab_consumers.get(m, ())) == 0)
    print("\n[3] DEAD hdlab MODULES -- 0 detected consumers (quarantine/doc candidates): %d" % len(dead))
    for m in dead:
        print("    %s" % m)

    # grade heuristic
    print("\n" + "-" * 72)
    n_promote = len(promote)
    print("SUMMARY: %d promotion candidates, %d bypass cells, %d dead hdlab modules, entry=%s"
          % (n_promote, len(bypass_cells), len(dead), "yes" if entry else "NO"))
    print("Action: promote the top candidates into hdlab; create the composed entry if ABSENT.")
    print("-" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
