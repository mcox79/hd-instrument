"""Scaffold-free witness for slug context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark.

HEADLINE (recomputed here first-hand on SemCor -- no cached metrics):
  CONTEXT overrides the frequency habit and recovers a word's RARER, context-appropriate
  meaning on modern, multiply-attested data. On SUBORDINATE-congruent SemCor items (gold
  sense STRICTLY less frequent than the top sense -> the frequency floor MFS = 0 by
  construction), held-out per instance, floors recomputed on that population:
    (1) THE BAR: the context-likelihood read (reordered access, held-out SemCor prototypes)
        beats MFS CI-separated, and also beats UNIFORM chance CI-separated.
    (2) THE INFO-FREE TWIN LOSES CI-separated: a SHUFFLED-context twin (context from a
        different item) tracks the floors far below the real context read.
    (3) SETTLING does NOT earn its keep on selection accuracy: multi-step attractor
        settling CI-TIES or LOSES to the single feed-forward read (the research-predicted,
        honest negative; the relatedness signature -- not accuracy -- is settling's
        fingerprint, and it is absent in the sparse space whose relatedness axis is ~0).

Run: .venv/Scripts/python.exe verification/test_context_override_frequency.py
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

from experiments.exp_context_override_frequency_wsd_v1 import (
    extract_semcor, build_vocab, build_inventory, evaluate, arm_correct,
    uniform_correct, cluster_bootstrap_delta, cosine_gap, semantic_control_experiment,
)


def main() -> None:
    # independent recompute on a SemCor subset (fast, cache-backed)
    cache = os.path.join(REPO, "data", "exp_context_override_frequency_wsd_v1", "semcor_cache_witness.pkl")
    items = extract_semcor(max_files=40, cache_path=cache)
    vocab, idf = build_vocab(items)
    by = build_inventory(items, vocab, idf)
    wup_cache = {}
    res = evaluate(items, vocab, idf, by, lam=1.0, beta=8.0, rng_seed=20260826,
                   do_settle=True, wup_cache=wup_cache, n_null=6)
    lid = res["LEMMA"]; n = res["n"]
    assert n > 1000, f"expected a well-powered subordinate population, got n={n}"

    c_mfs = arm_correct(res, "COS", lam=1.0, beta=0.0)
    c_ctx = arm_correct(res, "COS", lam=0.0, beta=1.0)
    c_reord = arm_correct(res, "COS", lam=1.0, beta=8.0)
    c_unif = uniform_correct(res, 20260826)
    c_shuf = res["NULL_CTX"][:, 0]
    c_setlat = res["SET_LAT"]; c_sethop = res["SET_HOP"]

    # ---- [0] MFS == 0 on subordinate items by construction --------------------------------------
    assert c_mfs.mean() == 0.0, f"[0] MFS must be 0 on subordinate items, got {c_mfs.mean():.4f}"
    print(f"[0] subordinate n={n}: MFS (frequency floor) = {c_mfs.mean():.4f} (== 0 by construction)")

    # ---- [1] THE BAR: context beats MFS CI-separated, and beats UNIFORM ------------------------
    d_mfs = cluster_bootstrap_delta(c_mfs, c_ctx, lid, 1500, 1)
    d_unif = cluster_bootstrap_delta(c_unif, c_ctx, lid, 1500, 2)
    print(f"[1] CONTEXT_ONLY={c_ctx.mean():.4f} vs MFS d={d_mfs['delta_mean']:+.4f} "
          f"CI[{d_mfs['ci_lo']:+.4f},{d_mfs['ci_hi']:+.4f}] hw={d_mfs['ci_halfwidth']:.4f}; "
          f"vs UNIFORM({c_unif.mean():.4f}) d={d_unif['delta_mean']:+.4f} sep={d_unif['sep_above_0']}")
    assert d_mfs["sep_above_0"], f"[1] context must beat MFS CI-separated: {d_mfs}"
    assert d_unif["sep_above_0"], f"[1] context must beat uniform chance CI-separated: {d_unif}"

    # ---- [2] info-free SHUFFLE twin LOSES CI-separated ------------------------------------------
    d_shuf = cluster_bootstrap_delta(c_shuf, c_ctx, lid, 1500, 3)
    null_p95 = float(np.percentile(res["NULL_CTX"].mean(axis=0), 95))
    print(f"[2] SHUFFLE twin={c_shuf.mean():.4f} (null_p95={null_p95:.4f}); "
          f"CONTEXT-SHUFFLE d={d_shuf['delta_mean']:+.4f} sep={d_shuf['sep_above_0']}")
    assert d_shuf["sep_above_0"], f"[2] info-free shuffle twin must LOSE CI-separated: {d_shuf}"
    assert c_ctx.mean() > null_p95, f"[2] context must exceed the null p95 ceiling: {c_ctx.mean()} vs {null_p95}"

    # ---- [3] SETTLING does not beat the feed-forward read (CI-tie or loss) ----------------------
    d_settle = cluster_bootstrap_delta(c_reord, c_setlat, lid, 1500, 4)
    settle_beats = d_settle["sep_above_0"]
    print(f"[3] SETTLE_lateral={c_setlat.mean():.4f} vs feed-forward REORDERED={c_reord.mean():.4f}: "
          f"d={d_settle['delta_mean']:+.4f} CI[{d_settle['ci_lo']:+.4f},{d_settle['ci_hi']:+.4f}] "
          f"beats={settle_beats}")
    assert not settle_beats, (
        f"[3] settling must NOT CI-beat the feed-forward read (honest negative expected); got {d_settle}")

    # ---- [4] the sparse representation carries ~no relatedness axis (gate context for [3]) -------
    cg = cosine_gap(by, wup_cache)
    print(f"[4] representation gate: related-pair cos={cg['related_pair_cos_median']} "
          f"unrelated-pair cos={cg['unrelated_pair_cos_median']} "
          f"(dense PPMI+SVD opens the gap ~0.31 vs 0.28 yet settling still hurts -> fair negative)")

    # ---- [5] SEMANTIC CONTROL: gold-blind conflict trigger works + suppression lifts the override
    sc = semantic_control_experiment(by, vocab, idf, lam=1.0, beta=8.0, n_boot=800, seed=20260826, smoke=True)
    print(f"[5] semantic control: trigger AUC={sc['trigger_auc']:.4f} (shuffled twin {sc['trigger_twin_auc']:.4f}); "
          f"SUPPRESS subordinate {sc['reordered_subordinate_acc']:.4f}->{sc['suppression_subordinate_acc']:.4f} "
          f"(dSUB={sc['d_subordinate_OVERRIDE']['delta_mean']:+.4f} sep={sc['d_subordinate_OVERRIDE']['sep_above_0']}); "
          f"info-free shuffled-trigger twin loses(sub)={sc['info_free_twin_shuffled_trigger_subordinate']['REAL_vs_TWIN']['sep_above_0']}")
    assert sc["trigger_auc"] > sc["trigger_twin_auc"] + 0.10, (
        f"[5] the gold-blind conflict trigger must beat its shuffled-context twin: "
        f"{sc['trigger_auc']} vs {sc['trigger_twin_auc']}")
    assert sc["d_subordinate_OVERRIDE"]["sep_above_0"], (
        f"[5] gated suppression must lift the frequency-override cases CI-separated: {sc['d_subordinate_OVERRIDE']}")
    assert sc["info_free_twin_shuffled_trigger_subordinate"]["REAL_vs_TWIN"]["sep_above_0"], (
        "[5] the override gain must come from the REAL conflict trigger (shuffled-trigger twin must lose)")

    print("\nALL WITNESS ASSERTIONS PASSED")
    print("  CONTEXT overrides the frequency prior and recovers the RARER sense on modern SemCor data")
    print("  CI-separated over MFS(=0) and uniform chance; the info-free twin loses. And the missing")
    print("  organ -- SEMANTIC CONTROL (gold-blind conflict trigger AUC>>twin -> suppression of the")
    print("  dominant sense) -- lifts the frequency-override cases CI-separated, gain from the real trigger.")


if __name__ == "__main__":
    main()


# --- pytest-collectable wrapper (pri 128, mechanical; see notes/problems/447_witness_files_define_no_test_function_so_the_certification_gate_runs_nothing_from_them_give_every_witness_a_collectable_wrapper_with_a_cost_marker_and_an_execution_manifest/PROBLEM.md) ---
import pytest as _pri128_pytest
from verification._witness_wrap import _run_main_as_test as _pri128_run


@_pri128_pytest.mark.fast
def test_witness():
    _code, _out = _pri128_run(main)
    assert _code == 0, "witness exited %r:\n%s" % (_code, _out[-4000:])
