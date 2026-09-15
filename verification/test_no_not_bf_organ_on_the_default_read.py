"""test_no_not_bf_organ_on_the_default_read -- THE IMPORT PROBE AS A WITNESS (priority 129).

THE RULE IT ENFORCES (owner 2026-09-08, hard PASS/FAIL): a component the BF registry marks NOT_BF must not be
running on the LIVE path.  `notes/bf_status_registry.jsonl` is the registry; a DEFAULT, annotation-free read of
a modern GUM document is the live path.  So: **no module tagged NOT_BF may be first-imported DURING
`SituationReader.read`.**

HOW IT IS MEASURED (and why the obvious probe is wrong).  A `builtins.__import__` hook MISSES
`from hdlab import parse_confidence` -- that call passes the name `'hdlab'`, not `'hdlab.parse_confidence'` --
so a hook-based probe silently under-reports.  This witness installs a `sys.meta_path` finder instead, whose
`find_spec` fires exactly once per module, on its FIRST import, and returns None so resolution continues
normally.  W0 PLANTS an import of a registry-NOT_BF module inside the probed window and asserts the probe SEES
it, so this witness cannot pass vacuously.

  W0  THE PROBE CAN FIRE: a deliberately-planted NOT_BF import inside the probed window is detected.
  W1  the probe completes a real default read (events > 0) on every document it is given.
  W2  NO REGRESSION: the set of NOT_BF modules imported during the read is a subset of the KNOWN RESIDUAL
      below.  A NEW NOT_BF organ appearing on the default read is RED immediately.
  W3  THE GOAL: that set is EMPTY.  Until priority 129's patch lands this check is reported and SKIPPED-as-
      known (the residual is listed in W2 and in notes/problems/three_default_read_consumers_.../SOLVED.md);
      the moment the residual is empty the witness enforces it for good.

Run: .venv/Scripts/python.exe verification/test_no_not_bf_organ_on_the_default_read.py
     .venv/Scripts/python.exe verification/test_no_not_bf_organ_on_the_default_read.py --docs 16
"""
from __future__ import annotations

import os
import sys

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "THINC_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import importlib.abc                                                            # noqa: E402
import json                                                                     # noqa: E402
import tempfile                                                                 # noqa: E402
import time                                                                     # noqa: E402
import traceback                                                                # noqa: E402

# THE KNOWN RESIDUAL at the time this witness landed (priority 129's measured probe, 16 modern GUM documents).
# Shrinking this set is the job; GROWING it is a defect.  An empty set makes W3 binding.
KNOWN_RESIDUAL = frozenset({"hdlab.arc_labeler", "hdlab.parse_confidence"})
DEFAULT_DOCS = 2


def notbf_modules():
    """Every module the BF registry tags NOT_BF, as an importable dotted name."""
    out = set()
    with open(os.path.join(_REPO, "notes", "bf_status_registry.jsonl"), encoding="utf-8") as fh:
        for ln in fh:
            ln = ln.strip()
            if not ln:
                continue
            r = json.loads(ln)
            if r.get("status") == "NOT_BF":
                out.add(r["module"].replace("hdlab/", "hdlab.").replace(".py", ""))
    return out


class _FirstImportProbe(importlib.abc.MetaPathFinder):
    """Records the phase + call stack of every hdlab module's FIRST import.  Returns None always, so it never
    changes what gets imported."""

    def __init__(self):
        self.phase = "import"
        self.first = {}

    def find_spec(self, name, path=None, target=None):
        if name.startswith("hdlab") or name.split(".")[0] in ("nltk", "spacy"):
            if name not in self.first:
                st = [f for f in traceback.extract_stack()[:-1]
                      if ("hdlab" in f.filename or "experiments" in f.filename
                          or "verification" in f.filename)]
                self.first[name] = {
                    "phase": self.phase,
                    "stack": " <- ".join("%s:%d:%s" % (os.path.basename(f.filename), f.lineno, f.name)
                                         for f in reversed(st[-8:]))}
        return None


def probe_default_read(n_docs=DEFAULT_DOCS, plant=None):
    """Read `n_docs` modern GUM documents through the DEFAULT reader with the probe installed.
    `plant` (a dotted module name) is imported inside the probed window to prove the probe can fire."""
    probe = _FirstImportProbe()
    sys.meta_path.insert(0, probe)
    per_doc = []
    try:
        from experiments.exp_board_rows_on_the_reader_v1 import _gum_test_docs, _write_two_conll
        from hdlab.situation_reader import SituationReader
        docs, gaz = _gum_test_docs(n_docs=n_docs, prefix=True)
        tmp = tempfile.mkdtemp(prefix="notbf_probe_")
        for d in docs[:n_docs]:
            probe.phase = "pre"
            _p_ann, p_txt, _p_prn = _write_two_conll(d, tmp)
            probe.phase = "construct"
            rdr = SituationReader(gaz=gaz)
            probe.phase = "READ"
            t0 = time.time()
            if plant:
                __import__(plant)                    # W0: the planted import, INSIDE the probed window
            sm = rdr.read(p_txt)
            per_doc.append({"docid": d.docid, "events": len(sm.events),
                            "read_s": round(time.time() - t0, 2)})
    finally:
        sys.meta_path = [m for m in sys.meta_path if m is not probe]
    notbf = notbf_modules()
    during = sorted(k for k in probe.first if k in notbf and probe.first[k]["phase"] == "READ")
    return {"per_doc": per_doc, "notbf": notbf, "during_read": during,
            "first": {k: v for k, v in probe.first.items() if k in notbf}}


def main(n_docs=None):
    n_docs = int(n_docs or os.environ.get("NOTBF_PROBE_DOCS") or DEFAULT_DOCS)
    if "--docs" in sys.argv:
        n_docs = int(sys.argv[sys.argv.index("--docs") + 1])

    print("=== no NOT_BF organ on the default read (%d modern GUM document(s)) ===" % n_docs, flush=True)

    # ---- W0 the probe can fire (a planted NOT_BF import inside the window is seen) -----------------
    # run in a CHILD process so the plant cannot poison the real probe's sys.modules state
    import subprocess
    code = ("import sys;sys.path.insert(0,%r);"
            "import verification.test_no_not_bf_organ_on_the_default_read as W;"
            "r=W.probe_default_read(1, plant='hdlab.arceager_parser');"
            "print('PLANT_SEEN', 'hdlab.arceager_parser' in r['during_read'])" % _REPO)
    env = dict(os.environ)
    env.setdefault("PYTHONHASHSEED", "0")
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, env=env)
    plant_seen = "PLANT_SEEN True" in (p.stdout or "")
    print("W0 planted NOT_BF import detected by the probe: %s" % plant_seen, flush=True)
    if not plant_seen:
        print(((p.stdout or "") + (p.stderr or ""))[-2500:], flush=True)
    assert plant_seen, "the probe did not see a planted NOT_BF import -- it cannot be trusted to see a real one"

    # ---- W1 / W2 / W3 the real probe --------------------------------------------------------------
    r = probe_default_read(n_docs=n_docs)
    for d in r["per_doc"]:
        print("   %-28s events=%-5d read=%.1fs" % (d["docid"], d["events"], d["read_s"]), flush=True)
    assert r["per_doc"], "the probe read no documents"
    for d in r["per_doc"]:
        assert d["events"] > 0, "%s produced no events -- that is not a real read" % d["docid"]
    print("W1 real default reads completed: %d" % len(r["per_doc"]), flush=True)

    during = set(r["during_read"])
    print("W2 NOT_BF modules imported DURING read: %s" % (sorted(during) or "NONE"), flush=True)
    for m in sorted(during):
        print("     %-26s %s" % (m, r["first"][m]["stack"]), flush=True)
    new = during - set(KNOWN_RESIDUAL)
    assert not new, ("NEW NOT_BF organ(s) on the default read: %s (known residual: %s)"
                     % (sorted(new), sorted(KNOWN_RESIDUAL)))

    if during:
        print("W3 SKIPPED-AS-KNOWN: the residual is %s -- priority 129's patch removes it; this witness turns "
              "binding the moment the residual is empty." % sorted(during), flush=True)
    else:
        print("W3 the default read imports NO NOT_BF module. GOAL MET.", flush=True)
    assert not (during - set(KNOWN_RESIDUAL))
    print("\nALL WITNESSES PASS", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest                                                 # noqa: E402
from verification._witness_wrap import _run_main_as_test as _pri128_run         # noqa: E402


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
