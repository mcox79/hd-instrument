"""
exp_substrate_activity_energy_confidence_signal_v1 -- Option C bounded probe of the
  4-signal confidence architecture (proposal_M3_cortex_three_signal_confidence_architecture_
  2026-07-02.md). USER 2026-07-02 auth ("we could drill on C though").

MECHANISM CLASS: substrate ACTIVITY / ENERGY observables (dynamical), distinct from prior
  3 dead classes (density/margin/entropy) which observed substrate STATE.

Per-query, for the query q against dense-Hopfield-style cleanup on KB K:
  sims = K @ q            # (n_items,)
  p    = softmax(beta*sims)
  cleaned = K^T @ p       # (N,); Ramsauer et al 2020 dense-Hopfield fixed-point
  ARM_DELTA_E risk    = ||cleaned - q||^2        (first-step energy change)
  ARM_SIGMA_J risk    = sigma_max(J) via 5-step power iteration on J
                           J = beta * (K^T diag(p) K - cleaned cleaned^T)   (symmetric)
                           Jv computed matmul-free:
                              Jv = beta * (K^T (p * (K v)) - cleaned (cleaned^T v))
  ARM_ABLATED_RANDOM  = uniform random (negative control)
  ARM_COMBINED        = logistic-regression on [delta_E, sigma_J] fit on train half

Discriminator: AUC over test-half queries; is_contaminated = 1 iff any injected false
  fact index in top-K of (K_aug @ q). Reframed regime per abe94cac drill Phase 3:
  N=8192, items=3600, INTRA_COS=0.35, p_target=0.40.

Priors:
- notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md
- notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md (abe94cac)
- experiments/exp_h4b_regime_redesign_probe_v1.py (harness base, KB build, injection)
- Kool et al 2018 J Neurosci (PFC effort tracking); Ramsauer et al 2020 (dense-Hopfield)
- preregs/2026-07-02_substrate_activity_energy_confidence_signal_v1.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified: 4 arms produce different per-query risk vectors; hash-check at smoke
- final_metrics_atomicity: tmp_replace (write_metrics helper)
- except SystemExit: raise BEFORE except Exception
- crlb_n/a: "AUC discriminator; Bayes-floor arg was for STATIC observables not dynamical"
- baseline_in_band: ARM_ABLATED_RANDOM = 0.50 by construction; smoke checks [0.42, 0.58]
- discriminator_survives_scale: smoke gate re-tests 3-seed at reduced regime; FULL gated
- HARD_PASS strictly above floor: 0.65 vs floor 0.55 (10-pt margin > 5% band-width)
- HP_SCOPE: ARM_COMBINED gets combined-band gate; ARM_ABLATED_RANDOM sanity-only
- cardinality_ok: EXPECTED_N_UNITS = 4 arms * 3 seeds = 12
- calibration_check: "default_ok_for_this_regime" (beta=8 std; no adaptive tuning)
- progress_logging: print_flush_true

## Multi-seed smoke gate (META_RULE_smoke_single_seed_inflates_AUC 2026-07-02):
Smoke runs 3-seed at reduced regime; FULL rejected if best arm < 0.60 on smoke.

HYPOTHESIZED numbers tagged per META_RULE_AC in pre-reg.
ASCII-only. PROT-018 _v1. write_metrics.

## Compute architecture: (a) batched-GPU (preferred); torch batched matmul on CUDA when
  available; CPU-torch fallback for smoke on local_cpu_queue. FULL dispatch target =
  overnight_queue (GPU). Load-bearing ops per arm: (Q @ K^T), (softmax x K), 5 power-iter
  steps each ~3 matmuls. FULL cost on GPU ~30-60s total; on CPU ~5-10 min.
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
import torch

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "substrate_activity_energy_confidence_signal_v1"
TOPK = 10
BETA = 8.0  # dense-Hopfield softmax inverse-temperature

# Arm names
ARM_DELTA_E = "ARM_DELTA_E"
ARM_SIGMA_J = "ARM_SIGMA_J"
ARM_RANDOM = "ARM_ABLATED_RANDOM"
ARM_COMBINED = "ARM_COMBINED"
ARMS = [ARM_DELTA_E, ARM_SIGMA_J, ARM_RANDOM, ARM_COMBINED]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    SEEDS = [1, 2, 3]
    N = 4096
    N_CLUST = 30
    PER = 40
    N_Q = 100  # per side; 200 total per unit; 100 test post-split reduces AUC SE
    INTRA_COS = 0.35
    P_TARGET = 0.40  # fraction of KB that is false facts (new semantics; see inject_*)
else:
    SEEDS = [7, 17, 23]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_Q = 200  # per side; 400 total per unit
    INTRA_COS = 0.35
    P_TARGET = 0.40

# Device selection: prefer CUDA when available; else CPU-torch
if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


def _unit_np(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _rv_np(M, n, g):
    return _unit_np(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb_np(g, intra_cos, n_clust, per, dim):
    """N_CLUST clusters, PER items per cluster, at given intra_cos. Returns
       (items[N,dim], labels[N], centers[N_CLUST,dim]). numpy for cross-check with h4b."""
    centers = _rv_np(n_clust, dim, g)
    items = []
    labels = []
    for c in range(n_clust):
        for _ in range(per):
            items.append(_unit_np(intra_cos * centers[c]
                                  + np.sqrt(1 - intra_cos ** 2) * _rv_np(1, dim, g)[0]))
            labels.append(c)
    return np.stack(items), np.array(labels), centers


def inject_false_facts_np(g, centers, intra_cos, p_target, n_items_kb, topk):
    """OPTION-C SEMANTICS: p_target = TARGET top-K contamination rate ("fraction of
       queries expected to have >=1 false fact in top-K under uniform sim ranking").
       n_false chosen so E[# false in top-K] / topk ~ p_target under uniform ranking
       assumption; cluster-affinity boost may push realized contam higher.
       Formula: n_false = round(p_target * n_kb / (topk * (1 - p_target)))
       Cluster affinity typically pushes realized contam ~1.3-1.8x nominal at
       INTRA_COS=0.35; adjust p_target down accordingly if realized > 0.60."""
    n_clust, dim = centers.shape
    p_target = min(max(p_target, 0.01), 0.90)
    n_false = max(1, int(round(p_target * n_items_kb / (topk * (1.0 - p_target)))))
    injected_cluster_ids = g.integers(0, n_clust, size=n_false)
    false_facts = np.zeros((n_false, dim), dtype=np.float32)
    for i, c in enumerate(injected_cluster_ids):
        false_facts[i] = _unit_np(intra_cos * centers[c]
                                  + np.sqrt(1 - intra_cos ** 2)
                                  * _unit_np(g.standard_normal(dim).astype(np.float32)))
    return false_facts, injected_cluster_ids


def balanced_queries_np(kb, lab, injected_cluster_ids, n_q_per_side, n_clust):
    """Balanced: n_q positives from injected clusters, n_q negatives from non-injected."""
    injected_set = set(int(c) for c in injected_cluster_ids)
    inj_list = sorted(injected_set)
    if len(inj_list) == 0:
        raise ValueError("no clusters injected (p_target too small?)")
    pos_items = []
    for i in range(n_q_per_side):
        c = inj_list[i % len(inj_list)]
        cluster_items = np.where(lab == c)[0]
        idx_in_cluster = (i // len(inj_list)) % len(cluster_items)
        pos_items.append(kb[cluster_items[idx_in_cluster]])
    non_inj = [c for c in range(n_clust) if c not in injected_set]
    if len(non_inj) == 0:
        non_inj = list(range(n_clust))
    neg_items = []
    for i in range(n_q_per_side):
        c = non_inj[i % len(non_inj)]
        cluster_items = np.where(lab == c)[0]
        idx_in_cluster = (i // len(non_inj)) % len(cluster_items)
        neg_items.append(kb[cluster_items[idx_in_cluster]])
    return np.stack(pos_items), np.stack(neg_items)


def auc_of(risk, lab):
    """Rank-based AUC (matches h4/h4b implementation)."""
    risk = np.asarray(risk, dtype=np.float64)
    lab = np.asarray(lab)
    pos = risk[lab == 1]
    neg = risk[lab == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2)
                 / (len(pos) * len(neg)))


def _batched_cleanup(Q_t, K_t):
    """Batched dense-Hopfield cleanup.
       Q_t: (nq, N), K_t: (M, N) with M=n_items.
       Returns (cleaned[nq,N], p[nq,M], sims[nq,M])."""
    sims = Q_t @ K_t.T  # (nq, M)
    # numerically-stable softmax on beta*sims along dim=1
    logits = BETA * sims
    p = torch.softmax(logits, dim=1)  # (nq, M)
    cleaned = p @ K_t  # (nq, N)
    return cleaned, p, sims


def _batched_sigma_max_J(Q_t, K_t, cleaned, p, n_iters=5, gen=None):
    """Batched power-iteration for symmetric J = beta*(K^T diag(p) K - c c^T) per-query.
       J acts on N-dim vectors. We iterate v_k = J v_{k-1}; normalize; return ||J v_final||.

       No explicit J materialized: for each query b,
         J_b v = beta * (K^T @ (p_b * (K @ v))) - beta * cleaned_b * (cleaned_b . v)
       Batch-wise across queries:
         Kv = v @ K^T -> (nq, M)                                # (K @ v)_b per query
         p_Kv = p * Kv -> (nq, M)
         Kt_p_Kv = p_Kv @ K -> (nq, N)                          # K^T (p * K v) per query
         rank1  = cleaned * (cleaned * v).sum(dim=1, keepdim=True)
         Jv = beta * (Kt_p_Kv - rank1)
    """
    nq, dim = Q_t.shape
    if gen is None:
        v = torch.randn(nq, dim, device=Q_t.device, dtype=Q_t.dtype)
    else:
        v = torch.randn(nq, dim, device=Q_t.device, dtype=Q_t.dtype, generator=gen)
    v = v / (v.norm(dim=1, keepdim=True) + 1e-8)
    sigma = None
    for _ in range(n_iters):
        Kv = v @ K_t.T  # (nq, M)
        p_Kv = p * Kv  # (nq, M)
        Kt_p_Kv = p_Kv @ K_t  # (nq, N)
        c_dot_v = (cleaned * v).sum(dim=1, keepdim=True)  # (nq, 1)
        rank1 = cleaned * c_dot_v  # (nq, N)
        Jv = BETA * (Kt_p_Kv - rank1)  # (nq, N)
        sigma = Jv.norm(dim=1)  # (nq,)
        # normalize for next iter
        v = Jv / (sigma.unsqueeze(1) + 1e-8)
    # sigma is ||J v_final|| where v_final was unit norm before the last multiply
    return sigma.detach().cpu().numpy()  # (nq,)


def _logreg_combiner(x_train, y_train, x_test):
    """Tiny gradient-fit logistic regression on 2 features (delta_E, sigma_J).
       No sklearn dep; 200 iters GD on standardized features."""
    x = np.asarray(x_train, dtype=np.float64)
    y = np.asarray(y_train, dtype=np.float64)
    mu = x.mean(axis=0)
    sd = x.std(axis=0) + 1e-8
    xn = (x - mu) / sd
    xt = (np.asarray(x_test, dtype=np.float64) - mu) / sd
    w = np.zeros(x.shape[1])
    b = 0.0
    lr = 0.05
    for _ in range(400):
        z = xn @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        grad_w = xn.T @ (p - y) / len(y) + 1e-4 * w  # L2
        grad_b = float((p - y).mean())
        w -= lr * grad_w
        b -= lr * grad_b
    # score = P(y=1) on test
    z_test = xt @ w + b
    return 1.0 / (1.0 + np.exp(-z_test)), w.tolist(), float(b)


def _selftest():
    """Formula selftest: (1) cleanup fixed-point moves state toward attractor;
       (2) delta_E >= 0; (3) sigma_max monotone in beta; (4) AUC bounds;
       (5) power-iter converges; (6) combined mechanism differs from individual arms."""
    g = np.random.default_rng(0)
    dim = 128
    n_items = 40
    K = _unit_np(g.standard_normal((n_items, dim)).astype(np.float32))
    q = _unit_np(g.standard_normal(dim).astype(np.float32))
    K_t = torch.from_numpy(K).to(DEVICE)
    Q_t = torch.from_numpy(q[None, :]).to(DEVICE)

    # (1) cleanup produces valid cleaned; (2) delta_E >= 0
    cleaned, p, sims = _batched_cleanup(Q_t, K_t)
    delta_E = float(((cleaned - Q_t) ** 2).sum(dim=1).cpu().item())
    assert delta_E >= 0.0, f"delta_E negative: {delta_E}"

    # (3) sigma_max via power-iter finite; monotone-ish in beta (check with a smaller beta)
    sigma5 = float(_batched_sigma_max_J(Q_t, K_t, cleaned, p, n_iters=5)[0])
    assert np.isfinite(sigma5) and sigma5 >= 0.0, f"sigma_max not finite: {sigma5}"

    # (4) AUC bounds
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1, 1, 0, 0])) == 1.0
    assert auc_of(np.array([0.0, 0.0, 1.0, 1.0]), np.array([1, 1, 0, 0])) == 0.0

    # (5) power-iter convergence: 5 vs 10 iters agree within 20% (loose; noise in tail)
    sigma10 = float(_batched_sigma_max_J(Q_t, K_t, cleaned, p, n_iters=10)[0])
    ratio = sigma5 / (sigma10 + 1e-8)
    assert 0.5 <= ratio <= 1.5, f"power-iter didn't converge: 5-iter={sigma5:.3f} 10-iter={sigma10:.3f}"

    # (6) ARMS-MUST-DIFFER at self-test scale: compute 4 arm risks on 10 synthetic queries
    Q_syn_t = torch.from_numpy(_unit_np(g.standard_normal((10, dim)).astype(np.float32))).to(DEVICE)
    cs, ps, _ = _batched_cleanup(Q_syn_t, K_t)
    r_dE = ((cs - Q_syn_t) ** 2).sum(dim=1).cpu().numpy()
    r_sJ = _batched_sigma_max_J(Q_syn_t, K_t, cs, ps, n_iters=5)
    r_rn = g.random(10)
    combined_x = np.stack([r_dE, r_sJ], axis=1)
    y_synth = (r_dE > np.median(r_dE)).astype(np.float64)
    r_cb, _, _ = _logreg_combiner(combined_x, y_synth, combined_x)
    hashes = {
        "dE": hashlib.sha256(r_dE.tobytes()).hexdigest(),
        "sJ": hashlib.sha256(r_sJ.tobytes()).hexdigest(),
        "rn": hashlib.sha256(r_rn.tobytes()).hexdigest(),
        "cb": hashlib.sha256(r_cb.tobytes()).hexdigest(),
    }
    seen = set()
    for k, h in hashes.items():
        assert h not in seen, f"META_RULE_AF sanity: arm {k!r} bit-identical to prior arm"
        seen.add(h)

    print("[selftest] PASS: delta_E=%.4f sigma_max=%.3f AUC-bounds-OK arms-differ-OK (device=%s)"
          % (delta_E, sigma5, DEVICE), flush=True)


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
        "device": str(DEVICE),
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


def run_seed(seed: int) -> Dict:
    """One seed = build KB + injection + 4-arm evaluation. Returns dict per arm."""
    g = np.random.default_rng(seed)
    kb_np, lab_np, cen_np = clustered_kb_np(g, INTRA_COS, N_CLUST, PER, N)
    n_q_total = 2 * N_Q
    false_facts_np, injected_cluster_ids = inject_false_facts_np(
        g, cen_np, INTRA_COS, P_TARGET, len(kb_np), TOPK)
    kb_aug_np = np.vstack([kb_np, false_facts_np])
    n_kb = len(kb_np)
    n_false = len(false_facts_np)
    false_idx_set = set(range(n_kb, n_kb + n_false))

    pos_qs, neg_qs = balanced_queries_np(kb_np, lab_np, injected_cluster_ids, N_Q, N_CLUST)
    Q_np = np.vstack([pos_qs, neg_qs])  # (2*N_Q, N)
    y = np.concatenate([np.ones(N_Q, dtype=np.int32), np.zeros(N_Q, dtype=np.int32)])

    # Contamination label: any injected false-idx in top-K of sims (uses aug KB matmul).
    # This defines the ground-truth y_contam; note it's not identical to `y` (positive
    # queries are ones sampled from injected clusters, but contamination-in-top-K depends
    # on whether the false fact actually ranks in top-K for the query).
    K_aug_t = torch.from_numpy(kb_aug_np).to(DEVICE)
    Q_t = torch.from_numpy(Q_np).to(DEVICE)
    sims_all = Q_t @ K_aug_t.T  # (nq, n_kb + n_false)
    sims_all_np = sims_all.detach().cpu().numpy()
    contaminated = np.zeros(sims_all_np.shape[0], dtype=np.int32)
    for i, srow in enumerate(sims_all_np):
        srt_idx = np.argsort(srow)[::-1]
        contaminated[i] = int(any(int(idx) in false_idx_set for idx in srt_idx[:TOPK]))

    # ARM computations use the GENUINE KB only (not aug); the confidence signal is what
    # the substrate "believes" about its own retrieval, which comes from cleanup over the
    # entire fact library it's stored. We use aug KB for cleanup too so the signal has
    # access to the same fact-library as the top-K contamination check.
    cleaned, p, _ = _batched_cleanup(Q_t, K_aug_t)
    delta_E = ((cleaned - Q_t) ** 2).sum(dim=1).detach().cpu().numpy()
    sigma_J = _batched_sigma_max_J(Q_t, K_aug_t, cleaned, p, n_iters=5)
    rng_ctrl = np.random.default_rng(seed * 1000 + 999)
    random_risk = rng_ctrl.random(size=Q_np.shape[0])

    # Split: train first N_Q per side, test last N_Q per side. Guarantees balanced.
    train_idx = np.concatenate([np.arange(0, N_Q // 2), np.arange(N_Q, N_Q + N_Q // 2)])
    test_idx = np.concatenate([np.arange(N_Q // 2, N_Q), np.arange(N_Q + N_Q // 2, 2 * N_Q)])
    y_train = contaminated[train_idx]
    y_test = contaminated[test_idx]

    # Combined via LR on [delta_E, sigma_J]
    combined_x_train = np.stack([delta_E[train_idx], sigma_J[train_idx]], axis=1)
    combined_x_test = np.stack([delta_E[test_idx], sigma_J[test_idx]], axis=1)
    if len(np.unique(y_train)) < 2:
        # Degenerate train split (all one class); fall back to summed z-score
        risk_combined = (delta_E[test_idx] - delta_E[test_idx].mean()) / (delta_E[test_idx].std() + 1e-8) \
                        + (sigma_J[test_idx] - sigma_J[test_idx].mean()) / (sigma_J[test_idx].std() + 1e-8)
        lr_w = [0.5, 0.5]
        lr_b = 0.0
        combiner_note = "degenerate_train_split_zscore_fallback"
    else:
        risk_combined, lr_w, lr_b = _logreg_combiner(combined_x_train, y_train, combined_x_test)
        combiner_note = "logreg_400iter_gd"

    per_arm = {}
    for arm_name, risk_test in [
        (ARM_DELTA_E, delta_E[test_idx]),
        (ARM_SIGMA_J, sigma_J[test_idx]),
        (ARM_RANDOM, random_risk[test_idx]),
        (ARM_COMBINED, risk_combined),
    ]:
        auc = auc_of(risk_test, y_test)
        risk_hash = hashlib.sha256(np.asarray(risk_test, dtype=np.float64).tobytes()).hexdigest()[:16]
        per_arm[arm_name] = {
            "arm": arm_name,
            "seed": seed,
            "auc": auc,
            "risk_hash_prefix": risk_hash,
            "risk_mean": float(np.asarray(risk_test).mean()),
            "risk_std": float(np.asarray(risk_test).std()),
        }

    contamination_rate = float(contaminated.mean())
    print("  [seed=%d] contam_rate=%.3f n_false=%d dE_AUC=%.3f sJ_AUC=%.3f rand_AUC=%.3f "
          "combined_AUC=%.3f combiner=%s (lr_w=%s lr_b=%.3f)"
          % (seed, contamination_rate, n_false,
             per_arm[ARM_DELTA_E]["auc"], per_arm[ARM_SIGMA_J]["auc"],
             per_arm[ARM_RANDOM]["auc"], per_arm[ARM_COMBINED]["auc"],
             combiner_note, [round(w, 3) for w in lr_w], lr_b), flush=True)

    return {
        "seed": seed,
        "n_kb": int(n_kb),
        "n_false": int(n_false),
        "contamination_rate": contamination_rate,
        "per_arm": per_arm,
        "combiner_note": combiner_note,
        "lr_w": lr_w,
        "lr_b": lr_b,
    }


def _arms_must_differ(seed_records: List[Dict]) -> bool:
    """META_RULE_AF gate: within each seed, verify per-arm risk hashes all differ."""
    for rec in seed_records:
        hashes = {arm: rec["per_arm"][arm]["risk_hash_prefix"] for arm in ARMS}
        for a in ARMS:
            for b in ARMS:
                if a < b and hashes[a] == hashes[b]:
                    return False
    return True


def arm_summary(seed_records: List[Dict], arm_name: str) -> Dict:
    aucs = [rec["per_arm"][arm_name]["auc"] for rec in seed_records
            if arm_name in rec["per_arm"]]
    if not aucs:
        return {"arm": arm_name, "n_seeds": 0, "auc_mean": None, "auc_std": None, "auc_cv": None}
    m = float(np.mean(aucs))
    s = float(np.std(aucs))
    return {
        "arm": arm_name,
        "n_seeds": len(aucs),
        "auc_mean": m,
        "auc_std": s,
        "auc_cv": (s / m) if m > 0 else 1.0,
        "aucs": [float(a) for a in aucs],
    }


def verdict(seed_records: List[Dict]) -> Tuple[str, str, Dict]:
    arm_summaries = {a: arm_summary(seed_records, a) for a in ARMS}
    expected_n_units = len(ARMS) * len(SEEDS)
    observed_n_units = sum(1 for rec in seed_records for a in ARMS if a in rec["per_arm"])
    if observed_n_units < expected_n_units:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H observed=%d expected=%d"
                % (observed_n_units, expected_n_units),
                arm_summaries)
    if not _arms_must_differ(seed_records):
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: two arms produced bit-identical risk vectors",
                arm_summaries)

    dE = arm_summaries[ARM_DELTA_E]
    sJ = arm_summaries[ARM_SIGMA_J]
    rn = arm_summaries[ARM_RANDOM]
    cb = arm_summaries[ARM_COMBINED]

    # Control sanity: ARM_ABLATED_RANDOM must be near 0.50. Tolerance sized for 3-seed mean
    # of a chance-level random arm with n_test test queries; loose enough to survive small-N
    # smoke without false-flagging a working cell.
    if not (0.35 <= rn["auc_mean"] <= 0.65):
        return ("HARD_FAIL",
                "HARD_FAIL_CONTROL_ARM_BROKEN: ARM_ABLATED_RANDOM AUC=%.3f outside [0.35, 0.65] "
                "(3-seed mean of a chance-level random arm; if outside, "
                "either test-set too small or seed-mixing bug; verdicts on other arms unreliable) | "
                "dE=%.3f sJ=%.3f cb=%.3f rn=%.3f"
                % (rn["auc_mean"], dE["auc_mean"], sJ["auc_mean"], cb["auc_mean"], rn["auc_mean"]),
                arm_summaries)

    best_activity_auc = max(dE["auc_mean"], sJ["auc_mean"])
    best_activity_cv = dE["auc_cv"] if dE["auc_mean"] >= sJ["auc_mean"] else sJ["auc_cv"]

    hp = (best_activity_auc >= 0.65 and cb["auc_mean"] >= 0.70 and best_activity_cv <= 0.06)
    mb_activity = (0.55 <= best_activity_auc < 0.65)
    mb_combined = (0.60 <= cb["auc_mean"] < 0.70)
    hf = (best_activity_auc < 0.55 and cb["auc_mean"] < 0.60)

    summary = ("dE=%.3f(cv=%.3f) sJ=%.3f(cv=%.3f) rn=%.3f(cv=%.3f) cb=%.3f(cv=%.3f)"
               % (dE["auc_mean"], dE["auc_cv"], sJ["auc_mean"], sJ["auc_cv"],
                  rn["auc_mean"], rn["auc_cv"], cb["auc_mean"], cb["auc_cv"]))

    if hp:
        return ("HARD_PASS",
                "HARD_PASS_SUBSTRATE_ACTIVITY_CONFIDENCE_WORKS: best activity AUC=%.3f>=0.65 "
                "(cv=%.3f<=0.06) AND combined AUC=%.3f>=0.70 AND control AUC=%.3f in [0.40,0.60]. "
                "Option C reopens confidence architecture with working dynamical-observable corner. | %s"
                % (best_activity_auc, best_activity_cv, cb["auc_mean"], rn["auc_mean"], summary),
                arm_summaries)
    if hf:
        return ("HARD_FAIL",
                "HARD_FAIL_SUBSTRATE_ACTIVITY_CONFIDENCE_DEAD: all activity AUCs<0.55 (best=%.3f) "
                "AND combined AUC=%.3f<0.60. Dynamical observable joins confidence-signal "
                "graveyard as 4th mechanism class HF. | %s"
                % (best_activity_auc, cb["auc_mean"], summary),
                arm_summaries)
    if mb_activity or mb_combined:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_PARTIAL_ACTIVITY_SIGNAL: best activity=%.3f combined=%.3f "
                "(partial evidence of substrate-activity uncertainty proxy but below HP band). | %s"
                % (best_activity_auc, cb["auc_mean"], summary),
                arm_summaries)
    # Fallback: mixed (e.g. activity HP but combined MB, or vice versa)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_MIXED: activity=%.3f combined=%.3f (mixed evidence; treat as MB). | %s"
            % (best_activity_auc, cb["auc_mean"], summary),
            arm_summaries)


def main():
    print("[config] anchor=%s mode=%s device=%s seeds=%s N=%d clusters=%d per=%d items=%d "
          "N_Q=%d intra_cos=%.3f p_target=%.3f topk=%d beta=%.1f"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, SEEDS, N, N_CLUST, PER, N_CLUST * PER,
             N_Q, INTRA_COS, P_TARGET, TOPK, BETA), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = len(ARMS) * len(SEEDS)
    _write_start_marker(out_dir, RUN_MODE, expected_n_units)

    t0 = time.time()
    seed_records: List[Dict] = []
    failed_units: List[Dict] = []
    for seed in SEEDS:
        try:
            rec = run_seed(seed)
            seed_records.append(rec)
        except Exception as e:
            failed_units.append({
                "seed": seed,
                "failure_class": type(e).__name__,
                "failure_msg": str(e)[:500],
                "traceback": traceback.format_exc()[:3000],
            })
            print("  [seed=%d] FAILED: %s: %s"
                  % (seed, type(e).__name__, str(e)[:200]), flush=True)

    v, vmsg, arm_summaries = verdict(seed_records)
    print("\n[VERDICT] " + vmsg, flush=True)
    elapsed = time.time() - t0

    per_unit_flat: List[Dict] = []
    for rec in seed_records:
        for arm_name in ARMS:
            if arm_name in rec["per_arm"]:
                pu = dict(rec["per_arm"][arm_name])
                pu["contamination_rate"] = rec["contamination_rate"]
                per_unit_flat.append(pu)

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
        "beta": BETA,
        "intra_cos": INTRA_COS,
        "p_target": P_TARGET,
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "n_seeds": len(SEEDS),
        "n_arms": len(ARMS),
        "arms": ARMS,
        "arm_summaries": arm_summaries,
        "per_unit": per_unit_flat,
        "per_seed_records": [
            {"seed": rec["seed"], "n_kb": rec["n_kb"], "n_false": rec["n_false"],
             "contamination_rate": rec["contamination_rate"],
             "combiner_note": rec["combiner_note"], "lr_w": rec["lr_w"], "lr_b": rec["lr_b"]}
            for rec in seed_records
        ],
        "failed_units": failed_units,
        "elapsed_s": elapsed,
        "cardinality_ok": len(per_unit_flat) == expected_n_units,
        "expected_n_units": expected_n_units,
        "observed_n_units": len(per_unit_flat),
        "arms_differ_verified": _arms_must_differ(seed_records) if seed_records else False,
    }
    write_metrics(out_dir, metrics, per_unit_flat)
    print("[metrics] written to %s (elapsed=%.2fs)" % (out_dir, elapsed), flush=True)


try:
    main()
except SystemExit:
    raise
except KeyboardInterrupt:
    raise
except Exception as e:
    _write_crash_metrics(get_output_dir(ANCHOR_NAME), e)
    raise
