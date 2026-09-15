"""Scaffold-free witness for the_front_end_mishandles_non_canonical_argument_structure.

Independently recomputes the headline: the brain-faithful HYBRID graded cue-integration assigner beats the
current composed front-end (relcl_resolver.resolve_patient) on the role-balanced gold's PRE-VERBAL / non-
canonical slice, CI-separated (paired), with the info-free SHUFFLED-validity twin LOSING, while PRESERVING
canonical (post-verbal not CI-below) and net-positive OVERALL. Recomputes its own bootstrap -- does not trust
the experiment's verdict. Uses the cached aligned gold (built by exp_noncanonical_role_diagnostic_v1); rebuilds
it from the live front-end if absent (slow path).

Run: .venv/Scripts/python.exe verification/test_noncanonical_role_assigner.py
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

from hdlab.relcl_resolver import resolve_patient, precise_passive, _cands           # noqa: E402
from exp_competition_model_noncanonical_assigner_v2 import (                          # noqa: E402
    build_xy, fit_logistic, learned_weights_for_competition, competition_pick,
    hybrid_pick, robust_passive, CACHE)

SEED = 20260827
N_BOOT = 2000


def _span_set(g):
    return set(range(g[0], g[1])) if (len(g) == 2 and g[1] > g[0]) else set(g)


def _in(p, g):
    return p is not None and (p - 1) in _span_set(g)


def _paired_lo(a, b, seed=SEED):
    """Lower 2.5% of the paired bootstrap difference mean(a)-mean(b)."""
    a = np.asarray(a, float); b = np.asarray(b, float); r = np.random.default_rng(seed); n = len(a)
    d = np.array([(a[i].mean() - b[i].mean()) for i in (r.integers(0, n, n) for _ in range(N_BOOT))])
    return float(np.percentile(d, 2.5)), float(np.mean(a) - np.mean(b))


def _load_rows():
    if not os.path.exists(CACHE):
        print("[witness] cache absent -> rebuilding aligned gold from the live front-end (slow)...", flush=True)
        from exp_noncanonical_role_diagnostic_v1 import build_cache
        build_cache()
    return [json.loads(l) for l in open(CACHE, encoding="utf-8")]


def main():
    rows = _load_rows()
    sent_of = [" ".join(it["toks"]) for it in rows]
    uniq = sorted(set(sent_of))
    perm = np.random.default_rng(SEED).permutation(len(uniq))
    test_sents = set(uniq[i] for i in perm[: len(uniq) // 2])
    train = [it for it, s in zip(rows, sent_of) if s not in test_sents]
    test = [it for it, s in zip(rows, sent_of) if s in test_sents]

    X, y, _g = build_xy(train)
    W = learned_weights_for_competition(fit_logistic(X, y))
    wk = list(W); wv = [W[k] for k in wk]
    tw = np.random.default_rng(SEED + 99).permutation(len(wv))
    TWIN = {wk[i]: wv[tw[i]] for i in range(len(wk))}

    pre_floor, pre_hyb, pre_twin = [], [], []
    post_floor, post_hyb = [], []
    all_floor, all_hyb = [], []
    rec_precise, rec_robust = [], []
    for it in test:
        toks, pos, v, g = it["toks"], it["pos"], it["verb_idx"] + 1, it["patient"]
        cands = _cands(pos)
        if not cands:
            continue
        f = _in(resolve_patient(toks, pos, v, cands), g)
        h = _in(hybrid_pick(toks, pos, v, cands, W), g)
        all_floor.append(f); all_hyb.append(h)
        if it["patient_position"] == "pre":
            pre_floor.append(f); pre_hyb.append(h)
            pre_twin.append(_in(competition_pick(toks, pos, v, cands, TWIN), g))
            if it["category"] == "passive":
                rec_precise.append(precise_passive(toks, pos, v))
                rec_robust.append(robust_passive(toks, pos, v))
        else:
            post_floor.append(f); post_hyb.append(h)

    checks = []
    lo, d = _paired_lo(pre_hyb, pre_floor, SEED + 1)
    checks.append(("HYBRID beats front-end on pre-verbal slice CI-separated (paired lo>0)",
                   lo > 0, f"delta={d:.4f} paired_ci_lo={lo:.4f}"))
    lo2, d2 = _paired_lo(pre_hyb, pre_twin, SEED + 2)
    checks.append(("info-free shuffled-validity twin LOSES CI-separated",
                   lo2 > 0, f"delta={d2:.4f} paired_ci_lo={lo2:.4f}"))
    loP, dP = _paired_lo(post_hyb, post_floor, SEED + 3)
    checks.append(("canonical PRESERVED (post-verbal not CI-below floor: paired lo>=-0.01)",
                   loP >= -0.01, f"delta={dP:.4f} paired_ci_lo={loP:.4f}"))
    loA, dA = _paired_lo(all_hyb, all_floor, SEED + 4)
    checks.append(("net-POSITIVE overall CI-separated (paired lo>0)",
                   loA > 0, f"delta={dA:.4f} paired_ci_lo={loA:.4f}"))
    rp = np.mean(rec_precise); rr = np.mean(rec_robust)
    checks.append(("robust voice detector raises passive recall over precise_passive",
                   rr > rp, f"precise={rp:.4f} robust={rr:.4f}"))
    checks.append(("passive_weak validity learned NEGATIVE (the -ed ambiguity is distrusted)",
                   W["passive_weak"] < 0 < W["passive_strong"],
                   f"passive_weak={W['passive_weak']:.3f} passive_strong={W['passive_strong']:.3f}"))

    print(f"\n=== WITNESS: non-canonical role assigner (test n={len(all_floor)}) ===")
    print(f"  pre-verbal   FLOOR {np.mean(pre_floor):.4f} -> HYBRID {np.mean(pre_hyb):.4f}  (twin {np.mean(pre_twin):.4f})")
    print(f"  post-verbal  FLOOR {np.mean(post_floor):.4f} -> HYBRID {np.mean(post_hyb):.4f}")
    print(f"  overall      FLOOR {np.mean(all_floor):.4f} -> HYBRID {np.mean(all_hyb):.4f}")
    ok = True
    for name, passed, detail in checks:
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}\n         {detail}")
        ok = ok and passed
    print(f"\n{'ALL CHECKS PASS' if ok else 'WITNESS FAILED'}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
