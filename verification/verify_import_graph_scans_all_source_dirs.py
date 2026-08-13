"""Witness: the capability-registry import graph must not be BLIND to whole directories.

WHY THIS EXISTS (2026-08-13, defect D4, found while landing D1/D2/D3 --
notes/registry_tighten_audit_2026-08-13.md). After the D1/D2/D3 fixes tightened the WIRED
verdict, three rows flipped WIRED -> ISLAND. Two of those flips were FALSE ALARMS, and a
false ISLAND is the more dangerous error direction: it makes us "wire" what is already
wired, or shelve a live capability.

Root cause: `integration_health.compute_import_graph()` read exactly two directories,
NON-recursively -- `experiments/` and `hdlab/` (`_pyfiles` = `os.listdir`). Nothing else in
the repo could ever be seen as an IMPORTER:

  * `tools/` -> `tools/` edges did not exist. `tools/inflight_monitor.py` is imported at
    `tools/dash_gui.py:54` and still read as a zero-consumer ISLAND.
  * `verification/` was never scanned -- a module whose only importer is a certification
    witness read as an ISLAND (`hdlab/parse_goal_extraction.py` <-
    `verification/test_parse_goal_extraction.py:37`).
  * `backend/` and `scripts/` likewise.
  * hdlab SUBPACKAGES (`hdlab/dashboard/`, `hdlab/learner/`, `hdlab/learner/plugins/`) were
    never scanned, so intra-subpackage relative imports and `__init__.py` re-exports were
    invisible.
  * `importlib`/`__import__` edges were neither followed nor recorded.

FAILING-BEFORE: run with `HDI_WITNESS_TOOLS_DIR=<dir holding the PRE-D4 tools/>` and the
D4 tests fail (the pre-fix `compute_import_graph` has no `root=` parameter, returns a bare
6-tuple with no `.path_consumers`, and reports the real repo's tools/->tools/ edge as
absent). Run with the default (repo `tools/`) and all pass.

No scaffolding in the product path: fixtures are throwaway temp directories, the real-repo
assertions read real files, and the functions under test are the ones the audit calls.
"""
from __future__ import annotations

import inspect
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

_ORIG = {k: getattr(cra, k) for k in
         ("ROOT", "COMPOSED_ENTRY_PATHS_REL", "DOC_MENTION_PATHS_REL") if hasattr(cra, k)}

_REAL_GRAPH = None


def _restore() -> None:
    for k, v in _ORIG.items():
        setattr(cra, k, v)


def _require_wide_scan() -> None:
    """Precondition shared by every D4 test: the graph must be pointable at a root and
    must expose path-keyed edges. On the pre-fix module both are absent."""
    assert "root" in inspect.signature(ih.compute_import_graph).parameters, (
        "compute_import_graph() has no `root` parameter: the graph can only ever scan "
        "experiments/ + hdlab/, so tools/, verification/, backend/, scripts/ and hdlab "
        "subpackages are invisible as importers (D4)")


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _fixture_repo(tmp: str) -> Path:
    """A miniature repo exercising every previously-blind edge class."""
    root = Path(tmp) / "repo"
    # (1) tools/ -> tools/ sibling bare import (the tools/dash_gui.py:54 shape)
    _write(root / "tools" / "target_tool.py", "def build_state():\n    return 1\n")
    _write(root / "tools" / "consumer_tool.py",
           "import os, sys\n"
           "sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))\n"
           "from target_tool import build_state  # noqa: E402\n")
    # (2) verification/ -> hdlab/ package import
    _write(root / "hdlab" / "organ.py", "def f():\n    return 2\n")
    _write(root / "verification" / "test_organ.py", "from hdlab.organ import f\n")
    # (3) backend/ -> hdlab/ package import
    _write(root / "hdlab" / "labeler.py", "def g():\n    return 3\n")
    _write(root / "backend" / "substrate_index" / "sequence_labeler.py",
           "from hdlab.labeler import g\n")
    # (4) hdlab subpackage: __init__ re-export + intra-subpackage relative import
    _write(root / "hdlab" / "learner" / "__init__.py", "from .plugins import ALPHA\n")
    _write(root / "hdlab" / "learner" / "plugins" / "__init__.py", "from .alpha import ALPHA\n")
    _write(root / "hdlab" / "learner" / "plugins" / "alpha.py", "ALPHA = 4\n")
    # (5) negative control: imported by nobody, anywhere
    _write(root / "hdlab" / "orphan.py", "ORPHAN = 5\n")
    # (6) dynamic imports: one string literal (resolvable), one variable (NOT)
    _write(root / "tools" / "dyn_consumer.py",
           "import importlib\n"
           "MOD = importlib.import_module('hdlab.organ')\n"
           "def load(name):\n"
           "    return importlib.import_module(name)\n")
    # (7) prose-only mention must STILL not create an edge (D2/D3 must survive D4)
    _write(root / "tools" / "prose_only.py",
           '"""Mentions hdlab.orphan and target_tool in a docstring only."""\n'
           "# see hdlab.orphan for details\n"
           "ROWS = [('hdlab.orphan', 'Orphan')]\n")
    return root


def _status(root: Path, rel_path: str, kind: str, graph) -> tuple[str, list]:
    cra.ROOT = root
    cra.COMPOSED_ENTRY_PATHS_REL = []
    cra.DOC_MENTION_PATHS_REL = []
    row = {"id": "witness", "kind": kind, "path": [rel_path], "gate_decision": "VET_PENDING"}
    return cra.compute_integration_status(row, graph, set())


# ---------------------------------------------------------------------------
# D4 -- the directory blindness
# ---------------------------------------------------------------------------

def test_tools_to_tools_edge_makes_a_row_wired():
    """THE headline case: tools/target_tool.py is imported ONLY by tools/consumer_tool.py.
    Pre-fix the graph never scanned tools/ as an importer, so this read ISLAND."""
    _require_wide_scan()
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        graph = ih.compute_import_graph(root=str(root))
        status, used_by = _status(root, "tools/target_tool.py", "tool", graph)
        assert status == "WIRED", (
            f"FALSE ISLAND: tools/target_tool.py is imported at tools/consumer_tool.py:3, "
            f"yet the audit reports {status!r} (used_by={used_by}) -- the import graph does "
            "not see tools/ -> tools/ edges")
        assert "tools/consumer_tool.py" in used_by, used_by
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_verification_only_importer_is_visible():
    _require_wide_scan()
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        graph = ih.compute_import_graph(root=str(root))
        status, used_by = _status(root, "hdlab/organ.py", "hdlab-module", graph)
        assert status == "WIRED", f"expected WIRED, got {status!r} (used_by={used_by})"
        assert "verification/test_organ.py" in used_by, used_by
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_backend_importer_is_visible():
    _require_wide_scan()
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        graph = ih.compute_import_graph(root=str(root))
        status, used_by = _status(root, "hdlab/labeler.py", "hdlab-module", graph)
        assert status == "WIRED", f"expected WIRED, got {status!r} (used_by={used_by})"
        assert "backend/substrate_index/sequence_labeler.py" in used_by, used_by
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_hdlab_subpackage_relative_and_init_reexport_edges():
    """`from .alpha import ALPHA` inside hdlab/learner/plugins/__init__.py, and the
    parent package's `from .plugins import ALPHA` re-export."""
    _require_wide_scan()
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        graph = ih.compute_import_graph(root=str(root))
        pc = graph.path_consumers
        assert "hdlab/learner/plugins/__init__.py" in pc.get("hdlab/learner/plugins/alpha.py", set()), (
            "intra-subpackage relative import invisible: "
            f"{sorted(pc.get('hdlab/learner/plugins/alpha.py', set()))}")
        assert "hdlab/learner/__init__.py" in pc.get("hdlab/learner/plugins/__init__.py", set()), (
            "__init__.py re-export edge invisible: "
            f"{sorted(pc.get('hdlab/learner/plugins/__init__.py', set()))}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_unimported_module_is_still_island():
    """Negative control: the widening must not blanket-promote. hdlab/orphan.py is named
    only in a docstring/comment/data-literal in tools/prose_only.py -- still ISLAND."""
    _require_wide_scan()
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        graph = ih.compute_import_graph(root=str(root))
        status, used_by = _status(root, "hdlab/orphan.py", "hdlab-module", graph)
        assert status == "ISLAND", (
            f"FALSE WIRED: hdlab/orphan.py has zero real importers, got {status!r} "
            f"(used_by={used_by}) -- a prose/data-literal mention is being counted as an edge")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


def test_dynamic_imports_resolved_or_recorded_never_silently_dropped():
    _require_wide_scan()
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        graph = ih.compute_import_graph(root=str(root))
        # literal form IS resolved
        assert "tools/dyn_consumer.py" in graph.path_consumers.get("hdlab/organ.py", set()), (
            "importlib.import_module('hdlab.organ') string-literal edge not resolved: "
            f"{sorted(graph.path_consumers.get('hdlab/organ.py', set()))}")
        # variable form CANNOT be resolved -- it must be RECORDED, not dropped
        recorded = [d for d in graph.undetectable_dynamic_imports
                    if d["file"] == "tools/dyn_consumer.py"]
        assert recorded, (
            "importlib.import_module(name) with a non-literal argument was silently "
            "dropped instead of being recorded in undetectable_dynamic_imports")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


# ---------------------------------------------------------------------------
# real-repo assertions (the two false alarms that motivated this fix)
# ---------------------------------------------------------------------------

def _real_graph():
    global _REAL_GRAPH
    if _REAL_GRAPH is None:
        _REAL_GRAPH = ih.compute_import_graph()
    return _REAL_GRAPH


def test_real_repo_inflight_monitor_has_its_tools_importer():
    _require_wide_scan()
    _restore()
    consumer = Path(ROOT) / "tools" / "dash_gui.py"
    assert consumer.exists(), consumer
    src = consumer.read_text(encoding="utf-8", errors="replace")
    assert "from inflight_monitor import" in src, "precondition gone: dash_gui no longer imports it"
    g = _real_graph()
    consumers = g.path_consumers.get("tools/inflight_monitor.py", set())
    assert "tools/dash_gui.py" in consumers, (
        f"tools/inflight_monitor.py consumers={sorted(consumers)} -- the real tools/->tools/ "
        "edge at tools/dash_gui.py:54 is invisible, so the row reads FALSE ISLAND")


def test_real_repo_parse_goal_extraction_has_its_verification_importer():
    _require_wide_scan()
    _restore()
    g = _real_graph()
    consumers = g.path_consumers.get("hdlab/parse_goal_extraction.py", set())
    assert "verification/test_parse_goal_extraction.py" in consumers, (
        f"hdlab/parse_goal_extraction.py consumers={sorted(consumers)} -- its certification "
        "witness importer is invisible, so the row reads FALSE ISLAND")


def test_real_repo_scan_covers_the_declared_dirs_and_skips_vendored_trees():
    _require_wide_scan()
    _restore()
    g = _real_graph()
    for d in ("experiments", "hdlab", "tools", "verification", "backend"):
        assert d in g.scanned_dirs, f"{d}/ not scanned: {g.scanned_dirs}"
    vendored = [f for f in g.scanned_files if "/.venv/" in f or "site-packages" in f
                or "__pycache__" in f]
    assert not vendored, f"vendored/venv trees pulled into the scan: {vendored[:5]}"


# ---------------------------------------------------------------------------
# backward compatibility -- the D1/D2/D3 witness and integration_health.main()
# both consume the historical 6-tuple shape
# ---------------------------------------------------------------------------

def test_legacy_tuple_shape_preserved():
    tmp = tempfile.mkdtemp()
    try:
        root = _fixture_repo(tmp)
        g = ih.compute_import_graph(exp_dir=str(root / "experiments"),
                                    hdlab_dir=str(root / "hdlab"))
        a, b, c, d, e, f = g            # 6-way unpack (capability_registry_audit does this)
        assert isinstance(g[1], dict)   # index access (the D3 witness does this)
        assert len(list(iter(g))) == 6
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
        _restore()


TESTS = [
    test_tools_to_tools_edge_makes_a_row_wired,
    test_verification_only_importer_is_visible,
    test_backend_importer_is_visible,
    test_hdlab_subpackage_relative_and_init_reexport_edges,
    test_unimported_module_is_still_island,
    test_dynamic_imports_resolved_or_recorded_never_silently_dropped,
    test_real_repo_inflight_monitor_has_its_tools_importer,
    test_real_repo_parse_goal_extraction_has_its_verification_importer,
    test_real_repo_scan_covers_the_declared_dirs_and_skips_vendored_trees,
    test_legacy_tuple_shape_preserved,
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
