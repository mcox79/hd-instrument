"""WITNESS: `hdlab.learner` must not drag experiment cells (or global state changes) into an import.

WHAT THIS PROTECTS. Before 2026-08-22, `hdlab/learner/registry.py` eagerly imported four plugins to
build `PLUGINS = {plugin.NAME: plugin}`. Two of those plugins import EXPERIMENT CELLS, and a cell
legitimately configures itself as a script at module level:

    os.environ.setdefault("OMP_NUM_THREADS", "1")
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

So `import hdlab.reading_grounding_loop` pulled 8 cells into `sys.modules` and SILENTLY rewrote
`sys.stdout`'s encoding (cp1252 -> utf-8) and pinned OMP_NUM_THREADS=1 for the whole process. That
crashed a real audit that ran under `redirect_stdout(StringIO)`, because StringIO has no
`.reconfigure`.

Measured: `hdlab.learner` alone pulled all 8; `reading_grounding_loop` added none beyond it. This
file is the sole gateway, so the registry's lazy plugin map is the whole fix.

THE DUPLICATION THIS GUARDS. Making the map lazy required declaring the plugin NAMES statically
(you cannot read `plugin.NAME` without importing the plugin). That duplicates a fact that lives in
the plugin modules, so `test_declared_names_match_the_modules` asserts the two still agree -- the
duplication cannot rot silently.
"""
from __future__ import annotations

import os
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, REPO)


def _probe(code: str) -> str:
    """Run `code` in a FRESH interpreter. Required: import side effects are global and one-shot,
    so they cannot be observed in a process that has already imported the module."""
    exe = os.path.join(REPO, ".venv", "Scripts", "python.exe")
    if not os.path.exists(exe):
        exe = sys.executable
    out = subprocess.run([exe, "-c", code], cwd=REPO, capture_output=True, text=True, timeout=300)
    assert out.returncode == 0, f"probe failed: {out.stderr[-600:]}"
    return out.stdout.strip()


def test_importing_the_live_module_pulls_no_experiment_cells():
    got = _probe(
        "import sys; sys.path.insert(0,'.');"
        "import hdlab.reading_grounding_loop;"
        "print(len([m for m in sys.modules if m.startswith('experiments.')]))")
    assert got == "0", f"importing the live module pulled {got} experiment cells (must be 0)"


def test_importing_the_live_module_does_not_mutate_global_state():
    got = _probe(
        "import sys, os; sys.path.insert(0,'.');"
        "b=(sys.stdout.encoding, sys.stdout.errors, os.environ.get('OMP_NUM_THREADS'));"
        "import hdlab.reading_grounding_loop;"
        "a=(sys.stdout.encoding, sys.stdout.errors, os.environ.get('OMP_NUM_THREADS'));"
        "print('SAME' if a==b else f'MUTATED {b} -> {a}')")
    assert got == "SAME", got


def test_declared_names_match_the_modules():
    """The lazy map declares names statically; the modules own the truth. They must agree."""
    from hdlab.learner import PLUGINS
    for name in PLUGINS:
        assert PLUGINS[name].NAME == name, (
            f"registry declares {name!r} but the module says {PLUGINS[name].NAME!r}")


def test_candidate_order_is_preserved():
    """`list(PLUGINS.keys())` is learn()'s default candidate list, so its ORDER is behaviour."""
    from hdlab.learner import PLUGINS
    assert list(PLUGINS.keys()) == ["estimation", "ruleind", "gam", "proginduction"], \
        f"candidate order changed: {list(PLUGINS.keys())}"


def test_plugins_still_load_and_expose_the_interface():
    """Laziness is worthless if the plugin never loads. POSITIVE CONTROL that it does."""
    from hdlab.learner import PLUGINS
    for name in PLUGINS:
        mod = PLUGINS[name]
        assert hasattr(mod, "learn") and hasattr(mod, "apply"), f"{name} lost its interface"


def _run() -> int:
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    failed = 0
    for t in tests:
        try:
            t()
            print(f"  PASS  {t.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"  FAIL  {t.__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(_run())
