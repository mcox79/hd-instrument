"""Witness: a capability is WIRED only if REAL CODE actually imports it.

WHY THIS EXISTS (2026-08-13, notes/registry_tighten_audit_2026-08-13.md defects D1/D2/D3).
The wire-or-shelve gate is `data/capability_registry.jsonl`, and its WIRED verdict was
computed by `capability_registry_audit.compute_integration_status`. Three defects made that
verdict untrustworthy in the ONE direction that matters -- all three could only ever INFLATE
the WIRED count, i.e. the anti-islanding gate was reporting islands as wired:

  D2  the composed-entry check was `if base in src` -- a bare SUBSTRING match against the raw
      text of hdlab/reasoner.py, hdlab/cortex.py and CLAUDE.md, which SHORT-CIRCUITED to WIRED
      ahead of every other test. Any capability whose module stem was a short generic word
      (`store`, `memory`, `atoms`, `metrics`, `multi_hop`) matched prose, comments and unrelated
      identifiers with no import anywhere.
  D1  two of the five declared composed entry paths (hdlab/substrate.py, hdlab/pipeline.py) did
      not exist on disk and were skipped SILENTLY by `if p.exists()`.
  D3  `integration_health.RE_HDLAB_ATTR` text-matched `hdlab.X` inside STRING LITERALS, so a
      data literal like ("hdlab.perceptron", "StructuredPerceptron") in an atomize script
      counted as an import edge.

Each test below is a FAILING-BEFORE witness: run this file with
`HDI_WITNESS_TOOLS_DIR=<dir holding the PRE-FIX tools/>` and D2/D3 fail and D1 errors on the
missing `validate_entry_paths`; run it with the default (repo `tools/`) and all pass.

No scaffolding in the product path: the fixtures are throwaway temp directories, and the
functions under test are the real ones the audit calls.
"""
from __future__ import annotations

import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.environ.get("HDI_WITNESS_TOOLS_DIR") or os.path.join(ROOT, "tools")
sys.path.insert(0, TOOLS_DIR)

import capability_registry_audit as cra  # noqa: E402
import integration_health as ih  # noqa: E402

EMPTY_GRAPH = ({}, {}, set(), [], [], set())

# Snapshot the module globals the fixtures monkeypatch, so no test leaks into the next.
_ORIG = {k: getattr(cra, k) for k in
         ("ROOT", "COMPOSED_ENTRY_PATHS_REL", "DOC_MENTION_PATHS_REL",
          "COMPOSED_ENTRY_PATHS") if hasattr(cra, k)}


def _restore() -> None:
    for k, v in _ORIG.items():
        setattr(cra, k, v)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _make_fixture_root(tmp: str) -> Path:
    """A miniature repo: a composed entry that MENTIONS 'store' in prose but imports
    nothing, plus an unimported hdlab/store.py."""
    root = Path(tmp) / "repo"
    (root / "hdlab").mkdir(parents=True)
    (root / "hdlab" / "store.py").write_text(
        '"""Persistent trace storage."""\nVALUE = 1\n', encoding="utf-8")
    (root / "hdlab" / "really_imported.py").write_text("VALUE = 2\n", encoding="utf-8")
    # cortex.py: the exact shape of the D2 false positive -- the words 'store',
    # 'memory', 'atoms', 'metrics' appear in prose/identifiers, none is imported.
    (root / "hdlab" / "cortex.py").write_text(
        '"""Composed entry. Writes results to the store, keeps working memory\n'
        'of atoms, and emits metrics."""\n'
        "from .really_imported import VALUE  # the only REAL import\n"
        "def run():\n"
        "    memory_store_of_atoms_metrics = VALUE\n"
        "    return memory_store_of_atoms_metrics\n",
        encoding="utf-8")
    (root / "hdlab" / "reasoner.py").write_text(
        '"""Reasoner. Consults the store for multi_hop metrics."""\n', encoding="utf-8")
    return root


def _status(root: Path, rel_path: str) -> str:
    """Run compute_integration_status against the fixture, adapting to whichever
    version of the audit module is loaded (pre-fix takes a {path: source} dict,
    post-fix takes a reachability set)."""
    cra.ROOT = root
    row = {"id": "witness", "kind": "hdlab-module", "path": [rel_path],
           "gate_decision": "VET_PENDING"}
    if hasattr(cra, "COMPOSED_ENTRY_PATHS_REL"):          # post-fix
        cra.COMPOSED_ENTRY_PATHS_REL = ["hdlab/cortex.py", "hdlab/reasoner.py"]
        cra.DOC_MENTION_PATHS_REL = []
        composed = cra.compute_composed_reachable()
    else:                                                  # pre-fix
        cra.COMPOSED_ENTRY_PATHS = [root / "hdlab" / "cortex.py",
                                    root / "hdlab" / "reasoner.py"]
        composed = cra._composed_entry_sources()
    status, _used_by = cra.compute_integration_status(row, EMPTY_GRAPH, composed)
    return status


# ---------------------------------------------------------------------------
# D2 -- the critical one
# ---------------------------------------------------------------------------

def test_generic_stem_named_in_prose_only_is_not_wired():
    """hdlab/store.py is imported by NOBODY. The word 'store' appears in the composed
    entries' prose. Pre-fix that substring short-circuited to WIRED."""
    tmp = tempfile.mkdtemp()
    try:
        root = _make_fixture_root(tmp)
        got = _status(root, "hdlab/store.py")
        assert got != "WIRED", (
            "FALSE WIRED: hdlab/store.py has zero importers anywhere, yet the audit called it "
            f"{got!r} -- the composed-entry check is matching the bare substring 'store' in "
            "prose instead of a real import statement")
        assert got == "ISLAND", f"expected ISLAND for a zero-consumer module, got {got!r}"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_genuinely_imported_module_is_still_wired():
    """Positive control: the fix must not simply demote everything. hdlab/
    really_imported.py IS imported by the composed entry and must stay WIRED."""
    tmp = tempfile.mkdtemp()
    try:
        root = _make_fixture_root(tmp)
        got = _status(root, "hdlab/really_imported.py")
        assert got == "WIRED", (
            f"expected WIRED for a module genuinely imported by a composed entry, got {got!r}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


# ---------------------------------------------------------------------------
# D1 -- a missing entry point must fail LOUD, never be skipped silently
# ---------------------------------------------------------------------------

def test_missing_entry_path_fails_loud():
    assert hasattr(cra, "validate_entry_paths"), (
        "no validate_entry_paths(): a declared-but-missing composed entry path is still being "
        "skipped silently by `if p.exists()`, so the import graph can be rooted at a file that "
        "does not exist and nothing says so (D1)")
    tmp = tempfile.mkdtemp()
    try:
        root = _make_fixture_root(tmp)
        cra.ROOT = root
        cra.COMPOSED_ENTRY_PATHS_REL = ["hdlab/cortex.py", "hdlab/does_not_exist.py"]
        cra.DOC_MENTION_PATHS_REL = []
        assert cra.validate_entry_paths() == ["hdlab/does_not_exist.py"]
        raised = False
        try:
            cra.compute_composed_reachable()
        except FileNotFoundError:
            raised = True
        assert raised, "a missing composed entry path did not raise -- still a silent skip"
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_declared_entry_points_all_exist_in_the_real_repo():
    """The live declaration must be true of disk RIGHT NOW (this is what caught D1)."""
    _restore()
    missing = [p for p in cra.COMPOSED_ENTRY_PATHS_REL if not (Path(ROOT) / p).exists()]
    assert not missing, f"declared composed entry path(s) missing on disk: {missing}"


# ---------------------------------------------------------------------------
# D3 -- `hdlab.X` inside a string literal or comment is not an import
# ---------------------------------------------------------------------------

def _d3_fixture(tmp: str):
    exp = Path(tmp) / "experiments"
    hdlab = Path(tmp) / "hdlab"
    exp.mkdir(parents=True)
    hdlab.mkdir(parents=True)
    (hdlab / "perceptron.py").write_text("VALUE = 1\n", encoding="utf-8")
    # data literal + comment + docstring only -- NO import of hdlab.perceptron
    (exp / "exp_witness_atomize_ledger.py").write_text(
        '"""Ledger. Records hdlab.perceptron as an atom claim."""\n'
        "ROWS = [\n"
        '    ("hdlab.perceptron", "StructuredPerceptron"),\n'
        "]\n"
        "# see hdlab.perceptron for the implementation\n"
        "MULTILINE = '''\nhdlab.perceptron\n'''\n",
        encoding="utf-8")
    (exp / "exp_witness_real_consumer.py").write_text(
        "from hdlab.perceptron import VALUE\n", encoding="utf-8")
    return str(exp), str(hdlab)


def test_hdlab_attr_inside_string_literal_is_not_a_consumer():
    tmp = tempfile.mkdtemp()
    try:
        exp, hdlab = _d3_fixture(tmp)
        hdlab_consumers = ih.compute_import_graph(exp_dir=exp, hdlab_dir=hdlab)[1]
        consumers = {os.path.basename(p) for p in hdlab_consumers.get("perceptron", set())}
        assert "exp_witness_atomize_ledger.py" not in consumers, (
            "FALSE CONSUMER: a file that only mentions 'hdlab.perceptron' inside a string "
            "literal / comment is counted as an importer -- RE_HDLAB_ATTR is matching text, "
            f"not code (D3). consumers={sorted(consumers)}")
        assert consumers == {"exp_witness_real_consumer.py"}, (
            f"expected exactly the one real importer, got {sorted(consumers)}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_string_stripping_preserves_line_structure():
    """The line-anchored `^\\s*from ...` patterns must keep working after stripping."""
    assert hasattr(ih, "strip_strings_and_comments"), "D3 fix absent"
    src = 'x = "aaa"  # note\nfrom hdlab.foo import bar\ny = """\nmulti\n"""\n'
    out, ok = ih.strip_strings_and_comments(src)
    assert ok
    assert len(out.splitlines()) == len(src.splitlines())
    assert "from hdlab.foo import bar" in out
    assert "aaa" not in out and "note" not in out and "multi" not in out


TESTS = [
    test_generic_stem_named_in_prose_only_is_not_wired,
    test_genuinely_imported_module_is_still_wired,
    test_missing_entry_path_fails_loud,
    test_declared_entry_points_all_exist_in_the_real_repo,
    test_hdlab_attr_inside_string_literal_is_not_a_consumer,
    test_string_stripping_preserves_line_structure,
]


if __name__ == "__main__":
    n_fail = 0
    for t in TESTS:
        try:
            t()
            print(f"[PASS] {t.__name__}")
        except Exception as e:                     # noqa: BLE001 -- witness reporter
            n_fail += 1
            print(f"[FAIL] {t.__name__}: {type(e).__name__}: {e}")
    print(f"[WITNESS] {len(TESTS) - n_fail}/{len(TESTS)} passed  (tools dir: {TOOLS_DIR})")
    sys.exit(1 if n_fail else 0)
