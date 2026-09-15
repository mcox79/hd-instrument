"""Scaffold-free witness for slug resolve_retrieval_interference_among_similar_memories.

HEADLINE (recomputed here first-hand on the REAL hdlab additive retrieval organ -- no cached metrics):
  Adding the encoding CONTEXT to the additive Lewis-Vasishth activation RESOLVES retrieval interference
  among genuinely similar memories, while still EXHIBITING the residual fan effect. Specifically, on a
  same-content-cluster interference instrument with a TCM drifting context, in a LEAK-SAFE regime where
  neither content alone nor context alone resolves it (both far below the exact-context oracle):
    (1) THE BAR: context reinstatement (CTX_ADD = content + w_ctx*context) beats the CONTEXT-FREE additive
        baseline (== the landed AdditiveCueRetrieval rule) CI-separated, at every competitor count K.
    (2) THE INFO-FREE TWINS LOSE CI-separated: a SHUFFLED-context and a RANDOM-context twin both track the
        content-only baseline (the context signal is real, not a free extra channel).
    (3) LEAK GUARD: context-ALONE sits far below the exact-context oracle (context BIASES, does not
        identify) -- the win is genuine CUE COMBINATION.
    (4) RESIDUAL FAN EFFECT: recovery DEGRADES gracefully as competitor count rises (content-only steeply;
        context-aided gently) -- a faithful model exhibits it; a ZERO-fan model has leaked.
    (5) BOUNDARY (the bar's decisive negative branch): when competitors are encoded ADJACENT in time so
        their contexts are NON-separable, context reinstatement collapses toward content-only -- context
        resolves interference ONLY when the memories have separable context.

CONTENT_ONLY is asserted BIT-IDENTICAL to the live hdlab.content_addressable_retrieval.AdditiveCueRetrieval
argmax, so the baseline IS the live organ.

Run: .venv/Scripts/python.exe verification/test_context_interference_resolution.py
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys

import numpy as np

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO not in sys.path:
    sys.path.insert(0, REPO)

from hdlab.content_addressable_retrieval import AdditiveCueRetrieval
from experiments.exp_context_interference_resolution_v1 import (
    Store, full_experiment, run_cell, score_content_only, noisy_argmax, ARMS_MAIN,
)


def _acc(cell, arm):
    return cell["arms"][arm]["acc"]


def main() -> None:
    # ---- [0] CONTENT_ONLY IS the live organ (bit-identical argmax) --------------------------------
    import torch
    store = Store(128, 6, 6, content_sigma=0.6, ctx_rho=0.9, seed=5)
    g = torch.Generator().manual_seed(9)
    mismatches = 0
    for c in range(6):
        tr = store.make_trial(store.clusters[c][0], K=4, cue_sigma=0.6, eta=1.0, g=g)
        live = AdditiveCueRetrieval()
        for cid in tr.cluster_ids:
            live.add(cid, store.items[cid]["features"], payload=cid)
        live_pick = live.retrieve(tr.cue_content).item_id
        ours = noisy_argmax(score_content_only(store, tr), 0.0, np.random.default_rng(0))
        mismatches += int(live_pick != ours)
    assert mismatches == 0, f"CONTENT_ONLY must equal the live organ argmax: {mismatches} mismatches"
    print("[0] CONTENT_ONLY == live AdditiveCueRetrieval argmax (0 mismatches over 6 trials)")

    # ---- headline FULL run (leak-safe regime), independent recompute -----------------------------
    res = full_experiment(d=256, n_clusters=60, cluster_size=9, content_sigma=0.6, ctx_rho=0.9,
                          cue_sigma=0.6, eta=1.6, w_ctx=3.0, gate_temp=0.3, sep=0.5, act_noise_s=0.15,
                          K_values=[1, 2, 4, 8], test_seeds=[201, 202, 203], n_boot=4000)
    Ks = [1, 2, 4, 8]

    # ---- [1] the bar: CTX_ADD beats content-only CI-separated at EVERY K --------------------------
    for K in Ks:
        w = res["per_K"][K]["CTX_ADD_vs_CONTENT"]
        print(f"[1] K={K}: CTX_ADD-CONTENT = {w['delta']:+.4f} CI[{w['ci_lo']:+.4f},{w['ci_hi']:+.4f}] "
              f"(CTX_ADD={_acc(res['per_K'][K],'CTX_ADD'):.3f} vs CONTENT={_acc(res['per_K'][K],'CONTENT_ONLY'):.3f})")
        assert w["sep_above_0"], f"context must beat content-only CI-separated at K={K}: {w}"

    # ---- [2] info-free twins LOSE CI-separated at every K -----------------------------------------
    for K in Ks:
        ts = res["per_K"][K]["CTX_ADD_vs_SHUFFLE"]
        trd = res["per_K"][K]["CTX_ADD_vs_RANDOM"]
        assert ts["sep_above_0"], f"shuffled-context twin must LOSE at K={K}: {ts}"
        assert trd["sep_above_0"], f"random-context twin must LOSE at K={K}: {trd}"
    print("[2] info-free twins (SHUFFLE, RANDOM) LOSE CI-separated at every K "
          f"(K=8: -SHUFFLE {res['per_K'][8]['CTX_ADD_vs_SHUFFLE']['delta']:+.3f}, "
          f"-RANDOM {res['per_K'][8]['CTX_ADD_vs_RANDOM']['delta']:+.3f})")

    # ---- [3] LEAK GUARD: context-alone far below the exact-context oracle at every K ---------------
    for K in Ks:
        c = res["per_K"][K]
        alone = _acc(c, "CTX_ALONE")
        oracle = _acc(c, "CTX_ORACLE")
        assert alone < 0.9, f"context-alone must be sub-ceiling (biases, not identifies) at K={K}: {alone}"
        assert oracle - alone > 0.15, f"context-alone must be clearly below the oracle at K={K}: {alone} vs {oracle}"
    print("[3] leak guard: CTX_ALONE << oracle at every K "
          f"(K=8: alone {_acc(res['per_K'][8],'CTX_ALONE'):.3f} vs oracle {_acc(res['per_K'][8],'CTX_ORACLE'):.3f}); "
          "the win is CUE COMBINATION, not a leak")

    # ---- [4] residual fan effect: CTX_ADD degrades with competitor count --------------------------
    ctx_by_K = [_acc(res["per_K"][K], "CTX_ADD") for K in Ks]
    content_by_K = [_acc(res["per_K"][K], "CONTENT_ONLY") for K in Ks]
    assert ctx_by_K[-1] < ctx_by_K[0], f"context arm must still show a fan cost: {ctx_by_K}"
    assert content_by_K[-1] < content_by_K[0] - 0.15, f"content-only must show a steep fan cost: {content_by_K}"
    print(f"[4] residual fan effect present: CTX_ADD {ctx_by_K[0]:.3f}(K=1)->{ctx_by_K[-1]:.3f}(K=8), "
          f"CONTENT {content_by_K[0]:.3f}->{content_by_K[-1]:.3f} (steeper) -- resolution reduces but "
          "does NOT eliminate interference")

    # ---- [5] BOUNDARY: adjacent-in-time (non-separable context) collapses the win -----------------
    bnd = full_experiment(d=256, n_clusters=60, cluster_size=9, content_sigma=0.6, ctx_rho=0.9,
                          cue_sigma=0.6, eta=1.6, w_ctx=3.0, gate_temp=0.3, sep=0.5, act_noise_s=0.15,
                          K_values=[8], test_seeds=[201, 202, 203], n_boot=2000, member_layout="adjacent")
    bc = bnd["per_K"][8]
    sep_ctx_add = _acc(res["per_K"][8], "CTX_ADD")
    adj_ctx_add = _acc(bc, "CTX_ADD")
    assert adj_ctx_add < sep_ctx_add - 0.2, (
        f"with NON-separable (adjacent) context the win must collapse: separable {sep_ctx_add:.3f} vs "
        f"adjacent {adj_ctx_add:.3f}")
    print(f"[5] boundary: adjacent-in-time context collapses CTX_ADD {sep_ctx_add:.3f}->{adj_ctx_add:.3f} "
          "-- context resolves interference ONLY when it is separable (the bar's decisive negative branch)")

    print("\nALL WITNESS ASSERTIONS PASSED")
    print("  CONTEXT reinstatement (additive, Lewis-Vasishth/TCM) RESOLVES interference among similar")
    print("  memories CI-separated over the context-free baseline; twins lose; leak-safe cue combination;")
    print("  residual fan effect exhibited; and it collapses when context is non-separable (correctly).")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.corpus
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
