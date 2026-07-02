"""
exp_substrate_activity_energy_confidence_signal_v2_extended -- 7-arm extension of v1
  (aa8030 landed MB 0.571 at 3-seed FULL). USER 2026-07-02 auth: "if the confidence
  signal landed MB, let's explore that more -- that is not a small deal".

EXTENSION HYPOTHESIS: 3 additional orthogonal activity observables should stack via
  logistic-regression combiner and lift combined AUC toward HP band (0.65).
  Brain analog: PFC integrates multi-signal uncertainty (Kool 2018; Shenhav 2013).

Arms (7):
  ARM_DELTA_E              (v1 retained) - ||cleaned - q||^2
  ARM_SIGMA_J              (v1 retained) - power-iteration sigma_max(J) at cleaned
  ARM_TEMP_ENTROPY         (NEW)         - Shannon entropy of softmax(beta*sims)
  ARM_MULTI_SAMPLE_VOTE    (NEW)         - top-1 disagreement over 5 perturbed queries
  ARM_RECONSTRUCTION_ERR   (NEW)         - ||cleanup(cleanup(q)) - cleanup(q)||^2
  ARM_ABLATED_RANDOM       (v1 retained) - uniform random negative control
  ARM_COMBINED_5           (LOAD-BEARING) - logistic-regression over 5 signals

Regime = v1 identical (N=8192, items=3600, INTRA_COS=0.35, p_target=0.40).
Discriminator: AUC over test half (200 test queries per seed).

Priors:
- experiments/exp_substrate_activity_energy_confidence_signal_v1.py (base + KB build)
- data/exp_substrate_activity_energy_confidence_signal_v1/metrics.json (MB baseline)
- preregs/2026-07-02_substrate_activity_energy_confidence_signal_v2_extended.md
- Kool et al 2018 J Neurosci (PFC metabolic-effort); Shenhav 2013 EVC theory

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified: 7 arms produce different per-query risk vectors; hash-check
- final_metrics_atomicity: tmp_replace (write_metrics helper)
- except SystemExit: raise BEFORE except Exception
- crlb_n/a: "AUC discriminator; dynamical-mixed class not yet closed-form"
- baseline_in_band: ARM_ABLATED_RANDOM = 0.50 by construction
- discriminator_survives_scale: multi-seed smoke gate at reduced regime
- HARD_PASS strictly above floor: COMBINED_5 0.65 vs floor 0.55
- HP_SCOPE: COMBINED_5 gets load-bearing gate; individuals report-only
- cardinality_ok: EXPECTED_N_UNITS = 7 arms * 3 seeds = 21
- calibration_check: default_ok (beta=8, sigma_pert=0.05)
- progress_logging: print_flush_true

## Compute architecture: (a) batched-GPU / batched-CPU-torch. Per-seed wall:
  ~5-10s GPU / 2-5min CPU-torch. FULL total: ~30s GPU / 10-15min CPU-torch.

ASCII-only. write_metrics. HYPOTHESIZED numbers tagged per META_RULE_AC in pre-reg.
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

ANCHOR_NAME = "substrate_activity_energy_confidence_signal_v2_extended"
TOPK = 10
BETA = 8.0
N_PERTURBATIONS = 5
SIGMA_PERT = 0.30  # perturbation of unit query vectors; at sigma=0.05 all 5 perturbed
                   #   queries collapse to same top-1 (VOTE degenerate); 0.30 tuned at
                   #   smoke to produce non-trivial disagreement while staying "near" q

# Arm names
ARM_DELTA_E = "ARM_DELTA_E"
ARM_SIGMA_J = "ARM_SIGMA_J"
ARM_TEMP_ENTROPY = "ARM_TEMP_ENTROPY"
ARM_MULTI_SAMPLE_VOTE = "ARM_MULTI_SAMPLE_VOTE"
ARM_RECONSTRUCTION_ERR = "ARM_RECONSTRUCTION_ERR"
ARM_RANDOM = "ARM_ABLATED_RANDOM"
ARM_COMBINED_5 = "ARM_COMBINED_5"
INDIVIDUAL_ACTIVITY_ARMS = [ARM_DELTA_E, ARM_SIGMA_J, ARM_TEMP_ENTROPY,
                            ARM_MULTI_SAMPLE_VOTE, ARM_RECONSTRUCTION_ERR]
ARMS = INDIVIDUAL_ACTIVITY_ARMS + [ARM_RANDOM, ARM_COMBINED_5]

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
    N_Q = 50   # per side; 100 total; 50 test post-split
    INTRA_COS = 0.35
    P_TARGET = 0.40
else:
    SEEDS = [7, 17, 23]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_Q = 200  # per side; 400 total; 200 test post-split (matches v1)
    INTRA_COS = 0.35
    P_TARGET = 0.40

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


def _unit_np(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def _rv_np(M, n, g):
    return _unit_np(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb_np(g, intra_cos, n_clust, per, dim):
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
    """OPTION-C SEMANTICS: p_target = target top-K contamination rate."""
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
    """Dense-Hopfield cleanup. Returns (cleaned[nq,N], p[nq,M], sims[nq,M])."""
    sims = Q_t @ K_t.T
    logits = BETA * sims
    p = torch.softmax(logits, dim=1)
    cleaned = p @ K_t
    return cleaned, p, sims


def _batched_sigma_max_J(Q_t, K_t, cleaned, p, n_iters=5, gen=None):
    nq, dim = Q_t.shape
    if gen is None:
        v = torch.randn(nq, dim, device=Q_t.device, dtype=Q_t.dtype)
    else:
        v = torch.randn(nq, dim, device=Q_t.device, dtype=Q_t.dtype, generator=gen)
    v = v / (v.norm(dim=1, keepdim=True) + 1e-8)
    sigma = None
    for _ in range(n_iters):
        Kv = v @ K_t.T
        p_Kv = p * Kv
        Kt_p_Kv = p_Kv @ K_t
        c_dot_v = (cleaned * v).sum(dim=1, keepdim=True)
        rank1 = cleaned * c_dot_v
        Jv = BETA * (Kt_p_Kv - rank1)
        sigma = Jv.norm(dim=1)
        v = Jv / (sigma.unsqueeze(1) + 1e-8)
    return sigma.detach().cpu().numpy()


def _batched_temp_entropy(p):
    """Shannon entropy of softmax distribution p over KB items, per query.
       Higher entropy = more spread (less confident retrieval). Returns numpy (nq,)."""
    # H = -sum_i p_i * log(p_i); clamp for log stability
    p_safe = torch.clamp(p, min=1e-12)
    entropy = -(p * torch.log(p_safe)).sum(dim=1)
    return entropy.detach().cpu().numpy()


def _batched_multi_sample_vote(Q_t, K_t, n_pert, sigma_pert, gen=None):
    """For each query, sample n_pert perturbations; get top-1 index of each; return
       disagreement fraction = 1 - (max_freq_top1 / n_pert). Higher = more inconsistent.

       Batching: Q_t is (nq, N). Perturbations stacked as (nq * n_pert, N); one big matmul."""
    nq, dim = Q_t.shape
    # Broadcast queries then add noise
    Q_expanded = Q_t.unsqueeze(1).expand(nq, n_pert, dim).contiguous().reshape(nq * n_pert, dim)
    if gen is None:
        noise = torch.randn(nq * n_pert, dim, device=Q_t.device, dtype=Q_t.dtype)
    else:
        noise = torch.randn(nq * n_pert, dim, device=Q_t.device, dtype=Q_t.dtype, generator=gen)
    Q_pert = Q_expanded + sigma_pert * noise
    # renormalize to unit sphere (matches encoder convention)
    Q_pert = Q_pert / (Q_pert.norm(dim=1, keepdim=True) + 1e-8)
    sims_pert = Q_pert @ K_t.T  # (nq*n_pert, M)
    top1 = sims_pert.argmax(dim=1).detach().cpu().numpy()  # (nq*n_pert,)
    top1 = top1.reshape(nq, n_pert)  # (nq, n_pert)
    # per-row: max frequency of any single index over the n_pert samples
    disagreement = np.zeros(nq, dtype=np.float64)
    for i in range(nq):
        row = top1[i]
        # count frequency of each value; take max
        _, counts = np.unique(row, return_counts=True)
        max_freq = counts.max()
        disagreement[i] = 1.0 - (max_freq / n_pert)
    return disagreement


def _batched_reconstruction_err(cleaned, K_t):
    """Second-order cleanup: apply cleanup to cleaned; measure delta.
       cleaned_next = K^T softmax(beta * K @ cleaned).
       Returns numpy (nq,) of ||cleaned_next - cleaned||^2."""
    # Normalize cleaned to unit sphere first (else beta * K @ cleaned scaling drifts)
    cleaned_norm = cleaned / (cleaned.norm(dim=1, keepdim=True) + 1e-8)
    sims2 = cleaned_norm @ K_t.T
    logits2 = BETA * sims2
    p2 = torch.softmax(logits2, dim=1)
    cleaned2 = p2 @ K_t
    delta = ((cleaned2 - cleaned) ** 2).sum(dim=1)
    return delta.detach().cpu().numpy()


def _logreg_combiner(x_train, y_train, x_test):
    """Logistic regression on n_features via gradient descent."""
    x = np.asarray(x_train, dtype=np.float64)
    y = np.asarray(y_train, dtype=np.float64)
    mu = x.mean(axis=0)
    sd = x.std(axis=0) + 1e-8
    xn = (x - mu) / sd
    xt = (np.asarray(x_test, dtype=np.float64) - mu) / sd
    w = np.zeros(x.shape[1])
    b = 0.0
    lr = 0.05
    for _ in range(600):  # extra iters for 5-feature convergence
        z = xn @ w + b
        p = 1.0 / (1.0 + np.exp(-z))
        grad_w = xn.T @ (p - y) / len(y) + 1e-4 * w
        grad_b = float((p - y).mean())
        w -= lr * grad_w
        b -= lr * grad_b
    z_test = xt @ w + b
    return 1.0 / (1.0 + np.exp(-z_test)), w.tolist(), float(b)


def _selftest():
    """Formula selftest: check all 7 arm computations produce valid outputs."""
    g = np.random.default_rng(0)
    dim = 128
    n_items = 40
    K = _unit_np(g.standard_normal((n_items, dim)).astype(np.float32))
    Q_syn = _unit_np(g.standard_normal((10, dim)).astype(np.float32))
    K_t = torch.from_numpy(K).to(DEVICE)
    Q_t = torch.from_numpy(Q_syn).to(DEVICE)

    # cleanup + delta_E
    cleaned, p, sims = _batched_cleanup(Q_t, K_t)
    r_dE = ((cleaned - Q_t) ** 2).sum(dim=1).detach().cpu().numpy()
    assert (r_dE >= 0).all(), "delta_E negative"

    # sigma_max
    r_sJ = _batched_sigma_max_J(Q_t, K_t, cleaned, p, n_iters=5)
    assert np.isfinite(r_sJ).all() and (r_sJ >= 0).all(), "sigma_max invalid"

    # temp_entropy
    r_TE = _batched_temp_entropy(p)
    assert np.isfinite(r_TE).all() and (r_TE >= 0).all(), "temp_entropy invalid"
    # max entropy for M=40 items is log(40) ~ 3.69
    assert (r_TE <= np.log(n_items) + 0.01).all(), "temp_entropy exceeds log(M)"

    # multi-sample vote
    r_VOTE = _batched_multi_sample_vote(Q_t, K_t, N_PERTURBATIONS, SIGMA_PERT)
    assert np.isfinite(r_VOTE).all() and (r_VOTE >= 0).all() and (r_VOTE <= 1).all(), "vote invalid"

    # reconstruction
    r_REC = _batched_reconstruction_err(cleaned, K_t)
    assert np.isfinite(r_REC).all() and (r_REC >= 0).all(), "reconstruction invalid"

    # random control
    r_rn = g.random(10)

    # combined
    combined_x = np.stack([r_dE, r_sJ, r_TE, r_VOTE, r_REC], axis=1)
    y_synth = (r_dE > np.median(r_dE)).astype(np.float64)
    r_cb, _, _ = _logreg_combiner(combined_x, y_synth, combined_x)
    assert np.isfinite(r_cb).all() and (r_cb >= 0).all() and (r_cb <= 1).all(), "combined invalid"

    # AUC bounds
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1, 1, 0, 0])) == 1.0
    assert auc_of(np.array([0.0, 0.0, 1.0, 1.0]), np.array([1, 1, 0, 0])) == 0.0

    # META_RULE_AF: all 7 arms produce different risk vectors
    all_risks = {
        "dE": r_dE, "sJ": r_sJ, "TE": r_TE, "VOTE": r_VOTE,
        "REC": r_REC, "rn": r_rn, "cb": r_cb,
    }
    hashes = {k: hashlib.sha256(np.asarray(v, dtype=np.float64).tobytes()).hexdigest()
              for k, v in all_risks.items()}
    seen = {}
    for k, h in hashes.items():
        assert h not in seen.values(), \
            "META_RULE_AF: arm %s bit-identical to %s" % (k, [kk for kk, vv in seen.items() if vv == h])
        seen[k] = h

    print("[selftest] PASS: dE=%.4f sJ=%.3f TE=%.3f VOTE=%.3f REC=%.4f "
          "arms-differ-OK AUC-bounds-OK (device=%s)"
          % (float(r_dE.mean()), float(r_sJ.mean()), float(r_TE.mean()),
             float(r_VOTE.mean()), float(r_REC.mean()), DEVICE), flush=True)


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
    """One seed = build KB + injection + 7-arm evaluation."""
    g = np.random.default_rng(seed)
    kb_np, lab_np, cen_np = clustered_kb_np(g, INTRA_COS, N_CLUST, PER, N)
    false_facts_np, injected_cluster_ids = inject_false_facts_np(
        g, cen_np, INTRA_COS, P_TARGET, len(kb_np), TOPK)
    kb_aug_np = np.vstack([kb_np, false_facts_np])
    n_kb = len(kb_np)
    n_false = len(false_facts_np)
    false_idx_set = set(range(n_kb, n_kb + n_false))

    pos_qs, neg_qs = balanced_queries_np(kb_np, lab_np, injected_cluster_ids, N_Q, N_CLUST)
    Q_np = np.vstack([pos_qs, neg_qs])

    K_aug_t = torch.from_numpy(kb_aug_np).to(DEVICE)
    Q_t = torch.from_numpy(Q_np).to(DEVICE)

    # Contamination ground-truth
    sims_all = Q_t @ K_aug_t.T
    sims_all_np = sims_all.detach().cpu().numpy()
    contaminated = np.zeros(sims_all_np.shape[0], dtype=np.int32)
    for i, srow in enumerate(sims_all_np):
        srt_idx = np.argsort(srow)[::-1]
        contaminated[i] = int(any(int(idx) in false_idx_set for idx in srt_idx[:TOPK]))

    # === Compute all 5 activity observables ===
    # Pass 1: primary cleanup (used by dE, sJ, TE, REC)
    cleaned, p, _ = _batched_cleanup(Q_t, K_aug_t)
    delta_E = ((cleaned - Q_t) ** 2).sum(dim=1).detach().cpu().numpy()
    sigma_J = _batched_sigma_max_J(Q_t, K_aug_t, cleaned, p, n_iters=5)
    temp_entropy = _batched_temp_entropy(p)
    reconstruction_err = _batched_reconstruction_err(cleaned, K_aug_t)

    # Multi-sample vote (independent perturbation pass)
    torch_gen = torch.Generator(device=Q_t.device).manual_seed(seed * 7919 + 13)
    multi_sample_vote = _batched_multi_sample_vote(
        Q_t, K_aug_t, N_PERTURBATIONS, SIGMA_PERT, gen=torch_gen)

    # Random control
    rng_ctrl = np.random.default_rng(seed * 1000 + 999)
    random_risk = rng_ctrl.random(size=Q_np.shape[0])

    # Train/test split
    train_idx = np.concatenate([np.arange(0, N_Q // 2), np.arange(N_Q, N_Q + N_Q // 2)])
    test_idx = np.concatenate([np.arange(N_Q // 2, N_Q), np.arange(N_Q + N_Q // 2, 2 * N_Q)])
    y_train = contaminated[train_idx]
    y_test = contaminated[test_idx]

    # Combined-5 via LR on all 5 individual signals
    features_train = np.stack([
        delta_E[train_idx], sigma_J[train_idx], temp_entropy[train_idx],
        multi_sample_vote[train_idx], reconstruction_err[train_idx],
    ], axis=1)
    features_test = np.stack([
        delta_E[test_idx], sigma_J[test_idx], temp_entropy[test_idx],
        multi_sample_vote[test_idx], reconstruction_err[test_idx],
    ], axis=1)

    if len(np.unique(y_train)) < 2:
        # Degenerate train split: fallback to summed z-scores over 5 features
        risk_combined = np.zeros(len(test_idx))
        for f_col in range(features_test.shape[1]):
            f = features_test[:, f_col]
            risk_combined = risk_combined + (f - f.mean()) / (f.std() + 1e-8)
        lr_w = [0.2] * 5
        lr_b = 0.0
        combiner_note = "degenerate_train_split_zscore_fallback"
    else:
        risk_combined, lr_w, lr_b = _logreg_combiner(features_train, y_train, features_test)
        combiner_note = "logreg_600iter_gd_5feat"

    per_arm = {}
    arm_risks = [
        (ARM_DELTA_E, delta_E[test_idx]),
        (ARM_SIGMA_J, sigma_J[test_idx]),
        (ARM_TEMP_ENTROPY, temp_entropy[test_idx]),
        (ARM_MULTI_SAMPLE_VOTE, multi_sample_vote[test_idx]),
        (ARM_RECONSTRUCTION_ERR, reconstruction_err[test_idx]),
        (ARM_RANDOM, random_risk[test_idx]),
        (ARM_COMBINED_5, risk_combined),
    ]
    for arm_name, risk_test in arm_risks:
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
    print("  [seed=%d] contam=%.3f n_false=%d | dE=%.3f sJ=%.3f TE=%.3f VOTE=%.3f "
          "REC=%.3f rn=%.3f cb5=%.3f | %s (lr_w=%s lr_b=%.2f)"
          % (seed, contamination_rate, n_false,
             per_arm[ARM_DELTA_E]["auc"], per_arm[ARM_SIGMA_J]["auc"],
             per_arm[ARM_TEMP_ENTROPY]["auc"], per_arm[ARM_MULTI_SAMPLE_VOTE]["auc"],
             per_arm[ARM_RECONSTRUCTION_ERR]["auc"], per_arm[ARM_RANDOM]["auc"],
             per_arm[ARM_COMBINED_5]["auc"], combiner_note,
             [round(w, 3) for w in lr_w], lr_b), flush=True)

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
    for rec in seed_records:
        hashes = {arm: rec["per_arm"][arm]["risk_hash_prefix"] for arm in ARMS
                  if arm in rec["per_arm"]}
        seen = {}
        for a, h in hashes.items():
            if h in seen.values():
                return False
            seen[a] = h
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
                % (observed_n_units, expected_n_units), arm_summaries)
    if not _arms_must_differ(seed_records):
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: two arms produced bit-identical risk vectors",
                arm_summaries)

    rn = arm_summaries[ARM_RANDOM]
    cb5 = arm_summaries[ARM_COMBINED_5]
    best_individual = max(arm_summaries[a]["auc_mean"] for a in INDIVIDUAL_ACTIVITY_ARMS)

    # Control sanity
    if not (0.35 <= rn["auc_mean"] <= 0.65):
        return ("HARD_FAIL",
                "HARD_FAIL_CONTROL_ARM_BROKEN: ARM_ABLATED_RANDOM AUC=%.3f outside [0.35, 0.65]"
                % rn["auc_mean"], arm_summaries)

    summary = " ".join([
        "%s=%.3f(cv=%.3f)" % (a.replace("ARM_", "").lower()[:6],
                              arm_summaries[a]["auc_mean"], arm_summaries[a]["auc_cv"])
        for a in ARMS
    ])

    # Bands: LOAD-BEARING metric = ARM_COMBINED_5 AUC
    hp = (cb5["auc_mean"] >= 0.65 and cb5["auc_cv"] <= 0.10
          and 0.42 <= rn["auc_mean"] <= 0.58)
    mb = (0.55 <= cb5["auc_mean"] < 0.65)
    hf = (cb5["auc_mean"] < 0.55)

    if hp:
        return ("HARD_PASS",
                "HARD_PASS_5SIG_ORTHOGONALITY_LIFT: COMBINED_5 AUC=%.3f>=0.65 (cv=%.3f<=0.10) "
                "vs best individual=%.3f. 5-signal orthogonality push clears HP band; "
                "Confidence Header primitive CG-eligible for M3 cortex. | %s"
                % (cb5["auc_mean"], cb5["auc_cv"], best_individual, summary), arm_summaries)
    if hf:
        return ("HARD_FAIL",
                "HARD_FAIL_ADDING_SIGNALS_DIDNT_HELP: COMBINED_5 AUC=%.3f<0.55 vs v1 combined-2=0.571. "
                "5 orthogonal activity observables collapse to chance; substrate-activity class has "
                "structural floor. | %s"
                % (cb5["auc_mean"], summary), arm_summaries)
    if mb:
        v1_baseline = 0.571
        delta_vs_v1 = cb5["auc_mean"] - v1_baseline
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_MARGINAL_5SIG_LIFT: COMBINED_5 AUC=%.3f in [0.55,0.65); delta vs v1 "
                "combined-2 (0.571) = %+.3f. Partial evidence 3 new signals add lift but not "
                "enough to clear HP. | %s"
                % (cb5["auc_mean"], delta_vs_v1, summary), arm_summaries)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_EDGE: COMBINED_5 AUC=%.3f. | %s" % (cb5["auc_mean"], summary),
            arm_summaries)


def main():
    print("[config] anchor=%s mode=%s device=%s seeds=%s N=%d clusters=%d per=%d items=%d "
          "N_Q=%d intra_cos=%.3f p_target=%.3f topk=%d beta=%.1f n_pert=%d sigma_pert=%.3f"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, SEEDS, N, N_CLUST, PER, N_CLUST * PER,
             N_Q, INTRA_COS, P_TARGET, TOPK, BETA, N_PERTURBATIONS, SIGMA_PERT), flush=True)
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
        "n_perturbations": N_PERTURBATIONS,
        "sigma_pert": SIGMA_PERT,
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
        "v1_baseline_combined_2_auc": 0.571,
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
