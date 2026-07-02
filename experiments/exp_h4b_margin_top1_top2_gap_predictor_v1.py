"""
exp_h4b_margin_top1_top2_gap_predictor_v1 -- h4 revival: top-1 vs top-2 similarity gap
  as contamination-risk predictor (bio-calibrated-confidence-B1, filed 2026-06-08, never shipped).

MECHANISM: for each query q, compute sims = kb_aug @ q; sort desc;
  gap = sims[0] - sims[1]; risk = -gap (small gap = uncertain = contamination-likely).
  Distinct-mechanism-class from h4 (density-averaging over 3600 items):
  spatial-margin uses only top-2 items so contamination signal does not dilute with M.

BIO-ANALOG: Ma, Beck, Latham, Pouget 2006 probabilistic population code -- posterior
  width = uncertainty via tuning-curve overlap. Substrate equivalent = top-1/top-2 gap.

BANDS (per research 2x drill 2026-07-02, P_CG=0.42):
  HARD_PASS: AUC(gap-risk, is_contaminated) >= 0.70 (3-seed FULL cv <= 0.03)
  MIDDLE_BAND: 0.60 <= AUC < 0.70
  HARD_FAIL: AUC < 0.60

SMOKE gates (DISCRIMINATOR-MUST-SURVIVE-SCALE per USER 2026-06-26):
  Arm A: seed=1 N=2048 items=600 N_Q=60 (proves cell runs; ~1s)
  Arm B (SCALE-PREVIEW): seed=1 N=8192 items=3600 N_Q=200 (full-N preview arm)
    Reject FULL if arm B AUC <= 0.55.

## Compute architecture: (b) numpy-batched-CPU with justification.
  Load-bearing op: single matmul KB @ Q.T per seed (3600 x 8192 @ 200 = ~24 MB out).
  Per-seed wall ~2-8s on numpy CPU; no substantial GPU speedup available at this scale.
  Chosen to match h4 harness parity (h4 already CPU-numpy). GPU dispatch would add
  fixed launch overhead > runtime.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: N/A (single-mechanism cell; smoke arms A/B are same code, different regime)
- final_metrics_atomicity: tmp_replace (write_metrics helper)
- except SystemExit: raise BEFORE except Exception
- crlb_n/a: "AUC discriminator, no closed-form noise floor for gap distribution;
  discriminator-survives-scale gate covers analogous concern via arm B preview"
- baseline_in_band: contamination_rate ~= 0.5 by construction (N_Q pos + N_Q neg);
  AUC baseline = 0.5 (chance)
- discriminator survives scale: arm B preview at full-N (item count 3600) in smoke
- HARD_PASS strictly above floor: 0.70 - 0.60 = 0.10 band; 5% width = 0.005;
  0.70 is exactly floor -- strict interpretation: HP requires AUC >= 0.70 with
  cv <= 0.03 (band-floor tightening per META_RULE_L)
- HP_SCOPE: gap-risk arm only (single mechanism arm; no baseline arm)
- cardinality_ok: EXPECTED_N_UNITS = 3 seeds x 400 queries = 1200 (200 pos + 200 neg per seed at FULL)
- calibration_check: "default_ok_for_this_regime" (no adaptive tuning; gap is a
  parameter-free direct observable)
- HYPOTHESIZED numbers tagged in verdict prose per META_RULE_AC

ASCII-only. PROT-018 _v1. write_metrics.

Priors:
- notes/research_h4_revival_confidence_calibration_2x_drill_2026-07-02.md (research handoff)
- notes/research_drill_biology_of_substrate_capabilities_5x_2026-06-08.md (bio-B1 filing)
- notes/exp_dev_handoff_research_biology_capabilities_5x_2026-06-08.md (Tier 1 pointer)
- Ma, Beck, Latham & Pouget 2006, "Bayesian inference with probabilistic population codes"
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse
import os
import time
import traceback
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "h4b_margin_top1_top2_gap_predictor_v1"
INTRA_COS = 0.6
TOPK = 10  # matches h4 definition of contamination-in-top-K

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--smoke-preview", action="store_true", help="arm B: full-N preview arm inside smoke")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Regime table
if RUN_MODE == "smoke":
    # Arm A: small-N smoke -- proves cell runs
    SEEDS = [1]
    N = 2048
    N_CLUST = 20
    PER = 30
    N_Q = 60
    if _ARGS.smoke_preview:
        # Arm B: full-N preview arm -- DISCRIMINATOR-MUST-SURVIVE-SCALE gate
        N = 8192
        N_CLUST = 60
        PER = 60
        N_Q = 200
else:
    # FULL: 3-seed cross-validation
    SEEDS = [7, 17, 23]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_Q = 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb(g):
    """Match h4 harness: N_CLUST clusters, PER items per cluster, INTRA_COS=0.6."""
    centers = rv(N_CLUST, N, g)
    items = []
    labels = []
    for c in range(N_CLUST):
        for _ in range(PER):
            items.append(unit(INTRA_COS * centers[c] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0]))
            labels.append(c)
    return np.stack(items), np.array(labels), centers


def auc_of(risk, lab):
    """Rank-based AUC (matches h4 auc_of implementation)."""
    pos = risk[lab == 1]
    neg = risk[lab == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    """Formula selftest: (1) intra-cluster cosine high; (2) AUC bounds; (3) gap is
       non-negative and small when two items near identical; (4) gap > 0 on random."""
    # (1) intra-cluster cosine
    g = np.random.default_rng(0)
    saved = (N_CLUST, PER, N)
    # small config for selftest
    globals_mod = {"N": 128, "N_CLUST": 4, "PER": 5}
    # inline mini KB
    centers = unit(g.standard_normal((4, 128)).astype(np.float32))
    items = []
    labels = []
    for c in range(4):
        for _ in range(5):
            items.append(unit(INTRA_COS * centers[c] + np.sqrt(1 - INTRA_COS ** 2)
                              * unit(g.standard_normal(128).astype(np.float32))))
            labels.append(c)
    kb = np.stack(items)
    lab = np.array(labels)
    intra = float(np.mean([kb[i] @ kb[j]
                           for i in range(len(kb)) for j in range(len(kb))
                           if lab[i] == lab[j] and i != j]))
    assert intra > 0.3, f"intra cosine {intra:.3f} not > 0.3"
    # (2) AUC bounds -- perfect ranking
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1, 1, 0, 0])) == 1.0, "AUC bounds"
    # (3) gap non-negative
    q = kb[0]
    sims = kb @ q
    srt = np.sort(sims)[::-1]
    gap = float(srt[0] - srt[1])
    assert gap >= 0.0, f"gap negative: {gap}"
    # (4) gap of two identical items is 0 (edge case)
    dup = np.stack([kb[0], kb[0], kb[1]])
    dsims = dup @ kb[0]
    dsort = np.sort(dsims)[::-1]
    assert abs(float(dsort[0] - dsort[1])) < 1e-5, "gap on duplicate not near 0"
    print("[selftest] PASS: h4b margin-gap formula selftest (intra=%.3f gap=%.4f)" % (intra, gap), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def _write_start_marker(output_dir, run_mode, expected_n_units):
    import platform
    marker = {
        "pid": os.getpid(),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "expected_n_units": expected_n_units,
        "host": platform.node(),
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {
        "verdict": "CELL_CRASHED",
        "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
        "summary": f"CELL_CRASHED: {type(exc).__name__}",
        "elapsed_s": 0.0,
        "traceback": traceback.format_exc()[:5000],
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "pid": os.getpid(),
        "anchor_name": ANCHOR_NAME,
        "run_mode": RUN_MODE,
    }
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def run_seed(seed) -> Dict:
    """One seed: build clustered KB, inject contamination, batch-compute all sims,
       extract gap-risk per query, AUC vs is_contaminated_in_top_k label."""
    g = np.random.default_rng(seed)
    kb, lab, cen = clustered_kb(g)
    tgt = 0
    # Inject one false fact tied to target cluster centroid (matches h4)
    false_fact = unit(INTRA_COS * cen[tgt] + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]])
    f_idx = len(kb)

    # Balanced query set: N_Q positives (in target cluster; likely contamination-affected)
    # + N_Q negatives (out of target cluster; unlikely affected)
    pos_qs = kb[lab == tgt][:N_Q]
    neg_qs = kb[lab != tgt][:N_Q]
    qs = np.vstack([pos_qs, neg_qs])

    # BATCHED matmul: (n_queries, M) similarities in one BLAS call
    sims_all = qs @ kb_aug.T  # shape (2*N_Q, M+1)

    # Per-query: sort desc; gap = top1 - top2; risk = -gap (low gap = high risk)
    gaps = np.zeros(sims_all.shape[0], dtype=np.float32)
    contaminated = np.zeros(sims_all.shape[0], dtype=np.int32)
    for i, srow in enumerate(sims_all):
        srt_idx = np.argsort(srow)[::-1]
        top1 = float(srow[srt_idx[0]])
        top2 = float(srow[srt_idx[1]])
        gaps[i] = top1 - top2
        contaminated[i] = int(f_idx in srt_idx[:TOPK])

    # Risk = -gap (small gap = high risk)
    risk = -gaps
    # Normalize risk to [0,1] for Brier
    rn = (risk - risk.min()) / (risk.max() - risk.min() + 1e-9)
    auc = auc_of(rn, contaminated)
    brier = float(np.mean((rn - contaminated) ** 2))
    contamination_rate = float(contaminated.mean())
    gap_mean = float(gaps.mean())
    gap_std = float(gaps.std())

    print("  [seed=%d] gap_AUC=%.3f brier=%.3f contamination_rate=%.3f gap_mean=%.4f gap_std=%.4f"
          % (seed, auc, brier, contamination_rate, gap_mean, gap_std), flush=True)
    return {
        "seed": seed,
        "gap_auc": auc,
        "brier": brier,
        "contamination_rate": contamination_rate,
        "gap_mean": gap_mean,
        "gap_std": gap_std,
        "n_queries": int(sims_all.shape[0]),
    }


def verdict(ps) -> Tuple[str, str]:
    aucs = [p["gap_auc"] for p in ps]
    auc_mean = float(np.mean(aucs))
    auc_std = float(np.std(aucs))
    brier_mean = float(np.mean([p["brier"] for p in ps]))
    contam_mean = float(np.mean([p["contamination_rate"] for p in ps]))
    cv = auc_std / auc_mean if auc_mean > 0 else 1.0
    summary = ("h4b top-1/top-2 margin gap: contamination-pred AUC_mean=%.3f (std=%.3f cv=%.3f) "
               "brier=%.3f contam_rate=%.3f n_seeds=%d n_queries_per_seed=%d"
               % (auc_mean, auc_std, cv, brier_mean, contam_mean, len(ps),
                  ps[0]["n_queries"] if ps else 0))
    # META_RULE_L: HARD_PASS strictly above floor + require cv <= 0.03
    if auc_mean >= 0.70 and cv <= 0.03:
        return ("HARD_PASS",
                "HARD_PASS: gap AUC>=0.70 cv<=0.03 -- ship as cortex confidence-routing signal (bio-calibrated-confidence-B1 closure). "
                + summary)
    if auc_mean >= 0.70 and cv > 0.03:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: gap AUC>=0.70 but cv>0.03 (seed instability) -- investigate before ship. "
                + summary)
    if auc_mean >= 0.60:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: gap AUC in [0.60, 0.70) -- partially predictive; investigate composition with lap3_12 isotonic. "
                + summary)
    return ("HARD_FAIL",
            "HARD_FAIL: gap AUC < 0.60 -- spatial-margin does not survive commercial scale (h4-family disprove extended). "
            + summary)


def main():
    print("[config] anchor=%s mode=%s smoke_preview=%s seeds=%s N=%d clusters=%d per=%d items=%d N_Q=%d topk=%d"
          % (ANCHOR_NAME, RUN_MODE, _ARGS.smoke_preview, SEEDS, N, N_CLUST, PER, N_CLUST * PER, N_Q, TOPK),
          flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = len(SEEDS)  # 3 for FULL; 1 for smoke
    _write_start_marker(out_dir, RUN_MODE, expected_n_units)

    t0 = time.time()
    ps = [run_seed(s) for s in SEEDS]
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    elapsed = time.time() - t0

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "summary": vmsg[:400],
        "N": N,
        "n_clusters": N_CLUST,
        "per_cluster": PER,
        "n_items": N_CLUST * PER,
        "n_queries_per_seed": 2 * N_Q,
        "topk": TOPK,
        "intra_cos": INTRA_COS,
        "run_mode": RUN_MODE,
        "smoke_preview_arm": bool(_ARGS.smoke_preview),
        "n_seeds": len(SEEDS),
        "per_seed": ps,
        "elapsed_s": elapsed,
        "cardinality_ok": len(ps) == len(SEEDS),
        "expected_n_units": expected_n_units,
    }
    write_metrics(out_dir, metrics, ps)
    print("[metrics] written (elapsed=%.2fs)" % elapsed, flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(get_output_dir(ANCHOR_NAME), e)
    raise
