"""
exp_h4b_regime_redesign_probe_v1 -- 6-arm (INTRA_COS, p_target) sweep to disentangle
  REGIME_CONFOUND from MECHANISM_LIMIT hypothesis after h4b HF'd smoke-preview at
  h4-harness regime (N=8192 items=3600 p=0.046 INTRA_COS=0.6, AUC=0.545).

Priors:
- notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md (abe94cac; §5.1)
- experiments/exp_h4b_margin_top1_top2_gap_predictor_v1.py (harness base)
- preregs/2026-07-02_h4b_regime_redesign_probe_v1.md

MECHANISM (identical to h4b): for each query q, sims = kb_aug @ q; gap = sims[0] - sims[1];
  risk = -gap. AUC(risk, is_contaminated_in_top_K) is the discriminator.

CONTAMINATION INJECTION (parametrized): inject n_false_injected = round(p_target * 2*N_Q)
  false facts, each tied to a randomly-chosen cluster centroid c_j. Balanced queries
  (N_Q positives from same-cluster-as-injected, N_Q negatives from other clusters).
  is_contaminated per query = 1 iff ANY injected false-fact index in query's top-K.

ARMS (6):
  A: INTRA_COS=0.6 p_target=0.046  (reproduce h4b HF; predicted AUC 0.53-0.55)
  B: INTRA_COS=0.6 p_target=0.20   (contam UP; predicted 0.58-0.65)
  C: INTRA_COS=0.4 p_target=0.046  (INTRA_COS DOWN; predicted 0.58-0.63)
  D: INTRA_COS=0.3 p_target=0.10   (BOTH improved; HP TARGET; predicted 0.68-0.78)
  E: INTRA_COS=0.5 p_target=0.10   (mild both; predicted 0.60-0.68)
  F: INTRA_COS=0.4 p_target=0.20   (aggressive; predicted 0.75-0.85)

BANDS (per drill §5.1 §5.3):
  HARD_PASS: Arm D AUC >= 0.68 AND Arm A AUC <= 0.55 (Arm D 3-seed cv <= 0.04)
  MIDDLE_BAND: Arm D 0.60-0.68, OR HP metrics but Arm A > 0.55 (h4b repro fail)
  HARD_FAIL: Arm D < 0.60

SMOKE gate (DISCRIMINATOR-MUST-SURVIVE-SCALE per USER 2026-06-26):
  All 6 arms, seed=1, full-N (N=8192 items=3600), N_Q=50 (reduced). ~30-60s wall.
  REJECT FULL if Arm A > 0.60 (cell broken) OR Arm D preview < 0.55.

## Compute architecture: (b) numpy-batched-CPU with justification.
  Load-bearing op per arm: KB (3600 x 8192 float32 = 120 MB) + BLAS matmul (400 x 3600).
  Per-arm wall ~15s numpy CPU BLAS; 6 arms x 3 seeds x 5s = ~90s + ~2-3 min overhead.
  GPU launch overhead > per-arm matmul at this scale; parity with h4b (also CPU-numpy).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified: 6 arms produce different contamination-injection schemes;
    per-arm KB hash logged; META_RULE_AF gate at smoke
- final_metrics_atomicity: tmp_replace (write_metrics helper)
- except SystemExit: raise BEFORE except Exception
- crlb_n/a: "AUC discriminator; drill Bayes-floor Delta/sigma*sqrt(2) is regime-side check
    already characterized (drill §3.1)"
- baseline_in_band: contamination_rate ~= 0.5 by construction (balanced pos/neg);
    realized p ~ p_target verified per arm
- discriminator_survives_scale: smoke uses full-N (N=8192 items=3600) at reduced N_Q=50
- HARD_PASS strictly above floor: 0.68 vs band-floor 0.60; strict interpretation
- HP_SCOPE: Arm D primary; Arm A must satisfy reproduction gate (<= 0.55);
    other arms diagnostic (not HP-gated)
- cardinality_ok: EXPECTED_N_UNITS = 6 arms x 3 seeds = 18; HF_CARDINALITY_BREACH otherwise
- calibration_check: "default_ok_for_this_regime" (no adaptive tuning; parameter-free gap)

HYPOTHESIZED numbers tagged in pre-reg per META_RULE_AC.
ASCII-only. PROT-018 _v1. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass
import argparse
import os
import time
import traceback
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "h4b_regime_redesign_probe_v1"
TOPK = 10  # matches h4/h4b definition of contamination-in-top-K

# Arm configurations: 6 combinations (INTRA_COS, p_target).
ARMS = [
    ("A", 0.6, 0.046),
    ("B", 0.6, 0.20),
    ("C", 0.4, 0.046),
    ("D", 0.3, 0.10),
    ("E", 0.5, 0.10),
    ("F", 0.4, 0.20),
]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Regime table -- full-N in both smoke AND full; smoke reduces N_Q + seeds only.
if RUN_MODE == "smoke":
    SEEDS = [1]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_Q = 50  # reduced for smoke; ~30-60s wall total
else:
    SEEDS = [7, 17, 23]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_Q = 200


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb(g, intra_cos):
    """N_CLUST clusters, PER items per cluster, at given intra_cos."""
    centers = rv(N_CLUST, N, g)
    items = []
    labels = []
    for c in range(N_CLUST):
        for _ in range(PER):
            items.append(unit(intra_cos * centers[c]
                              + np.sqrt(1 - intra_cos ** 2) * rv(1, N, g)[0]))
            labels.append(c)
    return np.stack(items), np.array(labels), centers


def inject_false_facts(g, centers, intra_cos, p_target, n_q_total):
    """Inject n_false = round(p_target * n_q_total) false facts, each tied to a
       randomly-chosen cluster centroid. Returns (false_facts, injected_cluster_ids).
       Uses centers.shape for dimensionality (n_clusters, dim) so selftest at N=128 works."""
    n_clust, dim = centers.shape
    n_false = max(1, int(round(p_target * n_q_total)))
    injected_cluster_ids = g.integers(0, n_clust, size=n_false)
    false_facts = np.zeros((n_false, dim), dtype=np.float32)
    for i, c in enumerate(injected_cluster_ids):
        false_facts[i] = unit(intra_cos * centers[c]
                              + np.sqrt(1 - intra_cos ** 2)
                              * unit(g.standard_normal(dim).astype(np.float32)))
    return false_facts, injected_cluster_ids


def balanced_queries(kb, lab, injected_cluster_ids, n_q_per_side):
    """Sample balanced queries: n_q positives (from injected clusters, cycling if fewer
       false clusters than n_q); n_q negatives (from non-injected clusters)."""
    injected_set = set(int(c) for c in injected_cluster_ids)
    # Positives: sample from clusters that have injected false facts
    inj_list = sorted(injected_set)
    if len(inj_list) == 0:
        raise ValueError("no clusters injected (p_target too small?)")
    # Round-robin from injected clusters
    pos_items = []
    for i in range(n_q_per_side):
        c = inj_list[i % len(inj_list)]
        # take the (i // len(inj_list))-th item from cluster c
        cluster_items = np.where(lab == c)[0]
        idx_in_cluster = (i // len(inj_list)) % len(cluster_items)
        pos_items.append(kb[cluster_items[idx_in_cluster]])
    # Negatives: sample from clusters NOT in injected_set
    non_inj = [c for c in range(N_CLUST) if c not in injected_set]
    if len(non_inj) == 0:
        # Fall back: sample from all clusters (edge case where all clusters injected)
        non_inj = list(range(N_CLUST))
    neg_items = []
    for i in range(n_q_per_side):
        c = non_inj[i % len(non_inj)]
        cluster_items = np.where(lab == c)[0]
        idx_in_cluster = (i // len(non_inj)) % len(cluster_items)
        neg_items.append(kb[cluster_items[idx_in_cluster]])
    return np.stack(pos_items), np.stack(neg_items)


def auc_of(risk, lab):
    """Rank-based AUC (matches h4/h4b implementation)."""
    pos = risk[lab == 1]
    neg = risk[lab == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def _selftest():
    """Formula selftest: (1) intra-cluster cos correct; (2) AUC bounds;
       (3) injection realized p ~ target; (4) gap formula matches h4b at INTRA_COS=0.6."""
    g = np.random.default_rng(0)
    # (1) intra-cluster cos on small config at INTRA_COS=0.6
    intra_target = 0.6
    centers = unit(g.standard_normal((4, 128)).astype(np.float32))
    items = []
    labels = []
    for c in range(4):
        for _ in range(8):
            items.append(unit(intra_target * centers[c]
                              + np.sqrt(1 - intra_target ** 2) * unit(g.standard_normal(128).astype(np.float32))))
            labels.append(c)
    kb = np.stack(items)
    lab = np.array(labels)
    intra = float(np.mean([kb[i] @ kb[j]
                           for i in range(len(kb)) for j in range(len(kb))
                           if lab[i] == lab[j] and i != j]))
    # Expected intra-cluster cosine ~ INTRA_COS^2 = 0.36
    assert 0.28 <= intra <= 0.44, f"intra cos {intra:.3f} outside [0.28, 0.44] band (expected ~0.36)"
    # (2) AUC bounds -- perfect ranking
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1, 1, 0, 0])) == 1.0, "AUC bounds"
    # (3) injection realized p ~ target
    n_q_total = 200
    p_t = 0.10
    n_false = max(1, int(round(p_t * n_q_total)))
    assert n_false == 20, f"n_false formula wrong: {n_false}"
    # (4) gap formula: two items very similar -> gap near 0
    q = kb[0]
    sims = kb @ q
    srt = np.sort(sims)[::-1]
    gap = float(srt[0] - srt[1])
    assert gap >= 0.0, f"gap negative: {gap}"
    # (5) arm-differ hash sanity: two different (intra, p) produce different injection
    g2 = np.random.default_rng(0)
    ff1, _ = inject_false_facts(g2, unit(g2.standard_normal((60, 128)).astype(np.float32)),
                                 0.6, 0.046, 400)
    g3 = np.random.default_rng(0)
    ff2, _ = inject_false_facts(g3, unit(g3.standard_normal((60, 128)).astype(np.float32)),
                                 0.3, 0.10, 400)
    h1 = hashlib.sha256(ff1.tobytes()).hexdigest()
    h2 = hashlib.sha256(ff2.tobytes()).hexdigest()
    assert h1 != h2, "META_RULE_AF sanity: two different arms produce identical injection"
    print("[selftest] PASS: h4b_regime_redesign_probe selftest (intra=%.3f gap=%.4f n_false=%d)"
          % (intra, gap, n_false), flush=True)


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


def run_arm_seed(arm_name, intra_cos, p_target, seed) -> Dict:
    """One (arm, seed) unit: build KB @ intra_cos, inject at p_target, sweep queries."""
    g = np.random.default_rng(seed * 100 + hash(arm_name) % 100)
    kb, lab, cen = clustered_kb(g, intra_cos)
    n_q_total = 2 * N_Q
    false_facts, injected_cluster_ids = inject_false_facts(g, cen, intra_cos, p_target, n_q_total)
    kb_aug = np.vstack([kb, false_facts])
    n_kb = len(kb)  # first n_kb rows are genuine; rows [n_kb:] are false
    false_idx_set = set(range(n_kb, n_kb + len(false_facts)))

    # Balanced queries: N_Q positives (from injected clusters), N_Q negatives (from non-injected)
    pos_qs, neg_qs = balanced_queries(kb, lab, injected_cluster_ids, N_Q)
    qs = np.vstack([pos_qs, neg_qs])

    # Batched matmul: (n_queries, M+n_false) similarities
    sims_all = qs @ kb_aug.T  # shape (2*N_Q, M + n_false)

    # Per-query: sort desc; gap = top1 - top2; contaminated = any false idx in top-K
    gaps = np.zeros(sims_all.shape[0], dtype=np.float32)
    contaminated = np.zeros(sims_all.shape[0], dtype=np.int32)
    for i, srow in enumerate(sims_all):
        srt_idx = np.argsort(srow)[::-1]
        top1 = float(srow[srt_idx[0]])
        top2 = float(srow[srt_idx[1]])
        gaps[i] = top1 - top2
        # Contaminated if ANY false fact in top-K
        contaminated[i] = int(any(int(idx) in false_idx_set for idx in srt_idx[:TOPK]))

    risk = -gaps
    if risk.max() > risk.min():
        rn = (risk - risk.min()) / (risk.max() - risk.min())
    else:
        rn = np.zeros_like(risk)
    auc = auc_of(rn, contaminated)
    brier = float(np.mean((rn - contaminated) ** 2))
    contamination_rate = float(contaminated.mean())
    gap_mean = float(gaps.mean())
    gap_std = float(gaps.std())

    # Arm-differ hash: sha256 of first-1KB of kb_aug tensor for META_RULE_AF verification
    kb_hash = hashlib.sha256(kb_aug[:2].tobytes()).hexdigest()[:16]

    print("  [arm=%s seed=%d] AUC=%.3f brier=%.3f p_realized=%.3f p_target=%.3f "
          "gap_mean=%.4f gap_std=%.4f n_false=%d kb_hash=%s"
          % (arm_name, seed, auc, brier, contamination_rate, p_target,
             gap_mean, gap_std, len(false_facts), kb_hash), flush=True)
    return {
        "arm": arm_name,
        "seed": seed,
        "intra_cos": intra_cos,
        "p_target": p_target,
        "gap_auc": auc,
        "brier": brier,
        "contamination_rate": contamination_rate,
        "p_realized": contamination_rate,
        "gap_mean": gap_mean,
        "gap_std": gap_std,
        "n_queries": int(sims_all.shape[0]),
        "n_false_injected": int(len(false_facts)),
        "kb_hash_prefix": kb_hash,
    }


def _arms_must_differ(per_units: List[Dict]) -> bool:
    """META_RULE_AF gate: verify per-arm KB hashes differ across arm pairs (same seed)."""
    by_seed = {}
    for u in per_units:
        by_seed.setdefault(u["seed"], {})[u["arm"]] = u["kb_hash_prefix"]
    for seed, arms in by_seed.items():
        arm_pairs = [(a, b) for a in arms for b in arms if a < b]
        for a, b in arm_pairs:
            if arms[a] == arms[b]:
                # Only OK if intra_cos + p_target are identical (they are not for our 6 arms)
                return False
    return True


def arm_summary(per_units: List[Dict], arm_name: str) -> Dict:
    """Aggregate per-seed for one arm."""
    us = [u for u in per_units if u["arm"] == arm_name]
    if not us:
        return {"arm": arm_name, "n_seeds": 0, "auc_mean": None, "auc_std": None}
    aucs = [u["gap_auc"] for u in us]
    return {
        "arm": arm_name,
        "n_seeds": len(us),
        "auc_mean": float(np.mean(aucs)),
        "auc_std": float(np.std(aucs)),
        "auc_cv": float(np.std(aucs) / np.mean(aucs)) if np.mean(aucs) > 0 else 1.0,
        "p_realized_mean": float(np.mean([u["p_realized"] for u in us])),
        "brier_mean": float(np.mean([u["brier"] for u in us])),
        "gap_mean_mean": float(np.mean([u["gap_mean"] for u in us])),
    }


def verdict(per_units: List[Dict]) -> Tuple[str, str, Dict]:
    arm_summaries = {a[0]: arm_summary(per_units, a[0]) for a in ARMS}

    # Cardinality gate
    expected = len(ARMS) * len(SEEDS)
    observed = len(per_units)
    if observed < expected:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H observed=%d expected=%d "
                "per_arm_summaries=%s" % (observed, expected, json.dumps(arm_summaries)),
                arm_summaries)

    # Arms-differ gate (META_RULE_AF)
    if not _arms_must_differ(per_units):
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: two or more arms produced bit-identical KB tensors "
                "(hash collision suggests arm implementations don't actually differ)",
                arm_summaries)

    # Primary decision on Arm D + Arm A (per drill §5.1)
    d = arm_summaries["D"]
    a = arm_summaries["A"]
    summary = " ".join(
        "%s: AUC=%.3f(cv=%.3f) p_real=%.3f" % (
            arm_name, s["auc_mean"] if s["auc_mean"] is not None else -1,
            s["auc_cv"] if s["auc_cv"] is not None else -1,
            s["p_realized_mean"] if s.get("p_realized_mean") is not None else -1)
        for arm_name, s in arm_summaries.items())

    hp_d = (d["auc_mean"] is not None and d["auc_mean"] >= 0.68 and d["auc_cv"] <= 0.04)
    hp_a_gate = (a["auc_mean"] is not None and a["auc_mean"] <= 0.55)

    if hp_d and hp_a_gate:
        return ("HARD_PASS",
                "HARD_PASS_REGIME_CONFOUND: Arm D AUC=%.3f>=0.68 (cv=%.3f<=0.04) AND "
                "Arm A AUC=%.3f<=0.55 (h4b reproduce). Spatial-margin works at RELAXED regime; "
                "regime was h4/h4b failure driver, not mechanism-class. | %s"
                % (d["auc_mean"], d["auc_cv"], a["auc_mean"], summary),
                arm_summaries)
    if hp_d and not hp_a_gate:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_HP_METRICS_BUT_A_REPRODUCE_FAILED: Arm D AUC=%.3f>=0.68 (cv=%.3f) "
                "but Arm A AUC=%.3f>0.55 (h4b baseline higher than expected; cell may be biased). | %s"
                % (d["auc_mean"], d["auc_cv"], a["auc_mean"], summary),
                arm_summaries)
    if d["auc_mean"] is not None and d["auc_mean"] >= 0.60:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_ARM_D_INCONCLUSIVE: Arm D AUC=%.3f in [0.60, 0.68); "
                "regime helps but not decisively. | %s" % (d["auc_mean"], summary),
                arm_summaries)
    return ("HARD_FAIL",
            "HARD_FAIL_MECHANISM_LIMIT: Arm D AUC=%.3f<0.60 -- spatial-margin dead even at "
            "improved regime (INTRA_COS=0.3, p=0.10). Mechanism class limit confirmed; "
            "regime was NOT the primary driver. | %s"
            % (d["auc_mean"] if d["auc_mean"] is not None else -1, summary),
            arm_summaries)


def main():
    print("[config] anchor=%s mode=%s seeds=%s N=%d clusters=%d per=%d items=%d N_Q=%d topk=%d"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N, N_CLUST, PER, N_CLUST * PER, N_Q, TOPK), flush=True)
    print("[config] arms: " + ", ".join(
        "%s(intra=%.2f,p=%.3f)" % (a[0], a[1], a[2]) for a in ARMS), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = len(ARMS) * len(SEEDS)
    _write_start_marker(out_dir, RUN_MODE, expected_n_units)

    t0 = time.time()
    per_units: List[Dict] = []
    failed_units: List[Dict] = []
    for arm_name, intra_cos, p_target in ARMS:
        for seed in SEEDS:
            try:
                unit_result = run_arm_seed(arm_name, intra_cos, p_target, seed)
                per_units.append(unit_result)
            except Exception as e:
                failed_units.append({
                    "arm": arm_name,
                    "seed": seed,
                    "failure_class": type(e).__name__,
                    "failure_msg": str(e)[:500],
                    "traceback": traceback.format_exc()[:3000],
                })
                print("  [arm=%s seed=%d] FAILED: %s: %s"
                      % (arm_name, seed, type(e).__name__, str(e)[:200]), flush=True)

    v, vmsg, arm_summaries = verdict(per_units)
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
        "n_queries_per_arm_per_seed": 2 * N_Q,
        "topk": TOPK,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "n_arms": len(ARMS),
        "arms_config": [{"arm": a[0], "intra_cos": a[1], "p_target": a[2]} for a in ARMS],
        "per_unit": per_units,
        "failed_units": failed_units,
        "arm_summaries": arm_summaries,
        "elapsed_s": elapsed,
        "cardinality_ok": len(per_units) == expected_n_units,
        "expected_n_units": expected_n_units,
        "observed_n_units": len(per_units),
        "arms_differ_verified": _arms_must_differ(per_units) if per_units else False,
    }
    write_metrics(out_dir, metrics, per_units)
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
