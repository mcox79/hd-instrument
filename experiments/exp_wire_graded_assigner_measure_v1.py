"""CONSOLIDATION composition-step measurement: WIRE the landed `hdlab.graded_role_assigner` into the composed
front-end and measure OFF-vs-ON on the ROLE-BALANCED gold's HELD-OUT test split.

This is the strategy-owned landing-verification for the p1 earned organ (STEP 16 landed it; STEP 15 integrated the
solver result). The solver's held-out result used W fit fresh in-test; THIS drives the LANDED organ's baked
`DEFAULT_VALIDITIES` (the static asset) so we confirm the wired organ reproduces the validated lift.

LEAK-FREE: the split is sentence-level, rng(20260827), first half = TEST. `DEFAULT_VALIDITIES` were fit on the
COMPLEMENT (train) -> measuring on TEST never touches the fitting data. IDENTICAL split to the organ's own witness.

ONE-VARIABLE OFF-vs-ON (the design gate), same candidate set (_cands, all nominals -- the STEP-9 winner):
  * FLOOR positional  : nearest POST-verbal nominal (no voice)                          -> naive floor.
  * OFF   resolve      : `relcl_resolver.resolve_patient` (voice + relcl, discrete)       -> the composed front-end.
  * ON    hybrid       : `graded_role_assigner.hybrid_role_patient` (LANDED, DEFAULT_VALIDITIES)  -> +graded route.
  * TWIN  shuffled     : hybrid with SHUFFLED validities -> info-free control, MUST lose.
The ONE variable OFF->ON is the graded Competition-Model route on the non-canonical fall-through. Reported split by
patient position (pre-verbal = the hard/reversible slice where STEP-10 localized the headroom; post-verbal = canonical).

Run:  .venv/Scripts/python.exe experiments/exp_wire_graded_assigner_measure_v1.py
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)
sys.path.insert(0, os.path.join(REPO, "experiments"))

from hdlab.relcl_resolver import resolve_patient, _cands                               # noqa: E402
from hdlab.graded_role_assigner import hybrid_role_patient, DEFAULT_VALIDITIES         # noqa: E402
from exp_competition_model_noncanonical_assigner_v2 import CACHE                        # noqa: E402

SEED = 20260827
N_BOOT = 2000


def _span_set(g):
    return set(range(g[0], g[1])) if (len(g) == 2 and g[1] > g[0]) else set(g)


def _in(p, g):
    return p is not None and (p - 1) in _span_set(g)


def _positional(pos, v, cands):
    after = [i for i in cands if i > v]
    return (after[0] if after else (cands[-1] if cands else None))


def _paired_lo(a, b, seed):
    """Lower 2.5% + mean of the paired bootstrap difference mean(a)-mean(b)."""
    a = np.asarray(a, float); b = np.asarray(b, float); r = np.random.default_rng(seed); n = len(a)
    d = np.array([(a[i].mean() - b[i].mean()) for i in (r.integers(0, n, n) for _ in range(N_BOOT))])
    lo, hi = float(np.percentile(d, 2.5)), float(np.percentile(d, 97.5))
    return lo, hi, float(np.mean(a) - np.mean(b))


def _band(lo, hi):
    return "ABOVE" if lo > 0 else ("BELOW" if hi < 0 else "NOT_SEP")


def main():
    rows = [json.loads(l) for l in open(CACHE, encoding="utf-8")]
    # EXACT held-out split (sentence-level, first half of the seed permutation = TEST -- the validities never saw it)
    sent_of = [" ".join(it["toks"]) for it in rows]
    uniq = sorted(set(sent_of))
    perm = np.random.default_rng(SEED).permutation(len(uniq))
    test_sents = set(uniq[i] for i in perm[: len(uniq) // 2])
    test = [it for it, s in zip(rows, sent_of) if s in test_sents]

    # info-free twin: shuffle the LANDED validities (seed matches the organ's own witness)
    keys = list(DEFAULT_VALIDITIES); vals = [DEFAULT_VALIDITIES[k] for k in keys]
    tperm = np.random.default_rng(SEED).permutation(len(vals))
    TWIN = {keys[i]: vals[tperm[i]] for i in range(len(keys))}

    A = {k: {"floor": [], "off": [], "on": [], "twin": []} for k in ("all", "pre", "post")}
    for it in test:
        toks, pos, v, g = it["toks"], it["pos"], it["verb_idx"] + 1, it["patient"]
        cands = _cands(pos)
        if not cands:
            continue
        fl = _in(_positional(pos, v, cands), g)
        of = _in(resolve_patient(toks, pos, v, cands), g)
        onv = _in(hybrid_role_patient(toks, pos, v, cands), g)
        tw = _in(hybrid_role_patient(toks, pos, v, cands, weights=TWIN), g)
        slot = "pre" if it.get("patient_position") == "pre" else "post"
        for key in ("all", slot):
            A[key]["floor"].append(fl); A[key]["off"].append(of); A[key]["on"].append(onv); A[key]["twin"].append(tw)

    n = len(A["all"]["off"])
    print(f"=== WIRE graded_role_assigner INTO the composed front-end (held-out TEST, n={n}) ===")
    print(f"    (LANDED organ DEFAULT_VALIDITIES; candidates = all nominals; leak-free test split)\n")
    for key in ("all", "pre", "post"):
        d = A[key]
        m = len(d["off"])
        print(f"  [{key.upper():4s} n={m}]  FLOOR {np.mean(d['floor']):.4f}   OFF/resolve {np.mean(d['off']):.4f}   "
              f"ON/hybrid {np.mean(d['on']):.4f}   TWIN {np.mean(d['twin']):.4f}")

    print("\n  --- ON vs OFF (the graded Competition-Model route; the ONE variable) ---")
    checks = []
    for key, need in (("pre", "lo>0"), ("all", "lo>0"), ("post", "lo>=-0.01")):
        lo, hi, dm = _paired_lo(A[key]["on"], A[key]["off"], SEED + 1 + hash(key) % 100)
        passed = (lo > 0) if need == "lo>0" else (lo >= -0.01)
        tag = "beats OFF CI-sep" if key != "post" else "canonical PRESERVED (not CI-below)"
        checks.append((f"{key.upper()} {tag}", passed, f"delta={dm:+.4f} paired_ci=[{lo:+.4f},{hi:+.4f}] band={_band(lo,hi)}"))
    # twin must lose on the pre slice (where the graded route actually fires)
    lo, hi, dm = _paired_lo(A["pre"]["on"], A["pre"]["twin"], SEED + 7)
    checks.append(("PRE info-free shuffled-validity twin LOSES CI-sep", lo > 0,
                   f"delta={dm:+.4f} paired_ci=[{lo:+.4f},{hi:+.4f}] band={_band(lo,hi)}"))

    ok = True
    for name, passed, detail in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {detail}")
        ok = ok and passed
    print(f"\n{'ALL CHECKS PASS -- the LANDED graded_role_assigner reproduces the held-out lift in-pipeline' if ok else 'MEASUREMENT FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
