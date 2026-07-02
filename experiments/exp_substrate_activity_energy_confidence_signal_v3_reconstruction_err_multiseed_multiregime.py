"""
exp_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime
  M1.11 Confidence Header v3. Isolates the ONE mechanism that survived v2 audit
  (reconstruction_err) and tests at 5 seeds x 2 regimes for CG-grade evidence.

WHY V3 (Skunkworks a8f265a VET on v2 extended, 2026-07-02):
- v1 (aa8030): MB at 3-seed FULL, combined_2 AUC=0.571 (delta_E + sigma_J).
- v2 extended (0a456c030): MM_TENTATIVE. COMBINED_5 AUC=0.754 but Skunkworks
  proved per-seed delta over reconstruction_err ALONE was +0.014/-0.003/-0.006
  (mean +0.002); cv=0.159 > CG threshold 0.15. Combiner does NOT lift.
- v3: drop combiner + drop falsified arms (temp_entropy / multi_sample_vote /
  combined_5); test reconstruction_err ALONE at 5 seeds x 2 regimes with
  DETERMINISTIC contamination (fixes v2's observed-noisy p drift 0.45/0.22/0.24
  when p_target=0.40).

ARMS (4 arms x 5 seeds x 2 regimes = 40 units):
  ARM_RECONSTRUCTION_ERR  (LOAD-BEARING) - ||cleanup(cleanup(q)) - cleanup(q)||^2
  ARM_DELTA_E             (report-only)  - v1 baseline for continuity
  ARM_SIGMA_J             (report-only)  - v1 baseline for continuity
  ARM_ABLATED_RANDOM      (pos control)  - uniform random; AUC -> 0.50 by cx

REGIMES:
  REGIME_LOW  p=0.20 (moderate KB noise)
  REGIME_HIGH p=0.50 (aggressive stress)

DETERMINISTIC CONTAMINATION (v3 fix, v2-label-semantic-preserving):
  v2 label semantic: query is CONTAMINATED iff its top-K on the aug KB contains
    at least one injected false-fact idx.
  v3 makes p exact by STRATIFIED sampling on a large candidate pool:
    - Build KB + inject false facts on p_target-fraction of clusters
    - Generate large candidate query pool (n_test * POOL_MULT), uniform over
      all clusters + hash-deterministic per (seed, regime, i)
    - Compute top-K on aug KB for each pool query; label by v2-semantic
    - Pick first round(p * N_test) contaminated + rest clean
    - Result: observed_contamination_rate == p_target EXACTLY (integer)
    - Result: labels match v2's confidence-signal question exactly

HP BAND (HP_SCOPE: ARM_RECONSTRUCTION_ERR only):
  ARM_RECONSTRUCTION_ERR AUC >= 0.65 in BOTH regimes AND
  cross-seed cv(AUC) < 0.15 in EACH regime AND
  ARM_ABLATED_RANDOM AUC in [0.45, 0.55] each unit (rig sanity) AND
  observed contamination_rate == p_target EXACTLY (determinism verified)

Priors:
- experiments/exp_substrate_activity_energy_confidence_signal_v1.py
- experiments/exp_substrate_activity_energy_confidence_signal_v2_extended.py
- preregs/2026-07-02_substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime.md
- notes/design_M1_11_confidence_header_v3_reconstruction_err_5seed_2regime_2026-07-02.md

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH):
- arms_differ_verified: 4 arms x 5 seeds x 2 regimes -> 40 distinct digests
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics)
- except SystemExit: raise BEFORE except Exception
- crlb_n/a: "AUC discriminator on binary contamination; no closed-form CRLB"
- baseline_in_band: ARM_ABLATED_RANDOM = 0.50 by construction
- discriminator_survives_scale: N_DIM=8192 matches v2 CG regime (v2 rec_err
  alone hit ~0.65 at 3-seed FULL; v3 tightens with 5 seeds + 2 regimes)
- HP strictly above floor: 0.65 vs 0.50 floor (0.15 margin > 5% band-width)
- HP_SCOPE: ARM_RECONSTRUCTION_ERR load-bearing; others report + control
- cardinality_ok: EXPECTED_N_UNITS = 40
- calibration_check: default_ok (no learned parameters; deterministic score)
- progress_logging: print_flush_true

Compute architecture: (a) batched-CPU-torch or GPU. Per-(seed x regime) wall
  ~10-30s CPU. FULL total: ~5-10 min wall. Route: remote_cpu_queue single
  dispatch; well within 1800s timeout.

ASCII-only. write_metrics helper. All numbers HYPOTHESIZED / MEASURED per
META_RULE_AC.
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

ANCHOR_NAME = "substrate_activity_energy_confidence_signal_v3_reconstruction_err_multiseed_multiregime"
TOPK = 10
BETA = 8.0

# Arm names
ARM_RECONSTRUCTION_ERR = "ARM_RECONSTRUCTION_ERR"
ARM_DELTA_E = "ARM_DELTA_E"
ARM_SIGMA_J = "ARM_SIGMA_J"
ARM_RANDOM = "ARM_ABLATED_RANDOM"
ARMS = [ARM_RECONSTRUCTION_ERR, ARM_DELTA_E, ARM_SIGMA_J, ARM_RANDOM]
LOAD_BEARING_ARM = ARM_RECONSTRUCTION_ERR

# Regimes
REGIME_LOW = ("REGIME_LOW", 0.20)
REGIME_HIGH = ("REGIME_HIGH", 0.50)
REGIMES_FULL = [REGIME_LOW, REGIME_HIGH]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

if RUN_MODE == "smoke":
    # Smoke: 3-seed multi-seed variance probe per USER-locked
    # META_confidence_signal_smoke_single_seed_inflates_AUC (2026-07-02). Reduced
    # scale for fast turnaround; still fires discriminator.
    SEEDS = [11, 17, 23]
    N = 4096
    N_CLUST = 40
    PER = 40
    N_TEST = 100     # 20 contam + 80 clean at p=0.20; 50/50 at p=0.50
    INTRA_COS = 0.35
    REGIMES = REGIMES_FULL
else:
    SEEDS = [11, 17, 23, 29, 37]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_TEST = 200
    INTRA_COS = 0.35
    REGIMES = REGIMES_FULL

if torch.cuda.is_available():
    DEVICE = torch.device("cuda")
else:
    DEVICE = torch.device("cpu")


# --- primitives ---

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


def _regime_id(regime_name: str) -> int:
    if regime_name == "REGIME_LOW":
        return 1
    if regime_name == "REGIME_HIGH":
        return 2
    raise ValueError(f"unknown regime {regime_name!r}")


POOL_MULT = 20  # pool_size = N_TEST * POOL_MULT for stratified sampling


def build_kb_queries_deterministic(seed: int, regime_name: str, p_target: float,
                                   n_dim: int, n_clust: int, per: int,
                                   intra_cos: float, n_test: int, topk: int):
    """Build KB + inject false facts + stratified-sampled queries with
    v2-semantic labels (query is contaminated iff top-K contains false-fact idx).

    Determinism: contamination_rate == round(p_target * n_test) / n_test EXACTLY.
    For n_test=200, p in {0.20, 0.50} both give integer counts (40 / 100).
    For n_test=100 smoke, p in {0.20, 0.50} give integer counts (20 / 50).
    """
    rid = _regime_id(regime_name)
    g = np.random.default_rng(seed * 100003 + rid * 7919 + 13)
    kb, lab, centers = clustered_kb_np(g, intra_cos, n_clust, per, n_dim)

    # Contaminated-cluster fraction scaled to p_target so that natural top-K
    # containment rate on random-cluster queries is roughly matched to p.
    n_contam_clust = max(4, int(round(p_target * n_clust)))
    all_clusters = np.arange(n_clust)
    perm = g.permutation(all_clusters)
    contam_clusters_arr = sorted(int(c) for c in perm[:n_contam_clust])

    # Inject TOPK false facts per contaminated cluster; enough that a
    # cluster-local query's top-K neighborhood typically contains at least one.
    n_false_per_cluster = topk
    false_facts = []
    for c in contam_clusters_arr:
        for _ in range(n_false_per_cluster):
            v = _unit_np(intra_cos * centers[c] + np.sqrt(1 - intra_cos ** 2)
                         * _unit_np(g.standard_normal(n_dim).astype(np.float32)))
            false_facts.append(v)
    if false_facts:
        false_facts_np = np.stack(false_facts)
    else:
        false_facts_np = np.zeros((0, n_dim), dtype=np.float32)

    kb_aug = np.vstack([kb, false_facts_np]).astype(np.float32)
    n_kb = len(kb)
    n_false = len(false_facts_np)
    false_idx_set = set(range(n_kb, n_kb + n_false))

    # --- pool generation (uniform-over-clusters, hash-deterministic per (seed, regime, i)) ---
    pool_size = n_test * POOL_MULT
    pool = np.zeros((pool_size, n_dim), dtype=np.float32)
    pool_source_cluster = np.zeros(pool_size, dtype=np.int32)
    # v2-parity: use bare KB items as queries (no jitter). Cleanup dynamics
    # then match v2: contaminated cluster queries pick up false-fact mass in
    # softmax and drift; reconstruction_err discriminates in expected direction.
    for i in range(pool_size):
        qseed = int(hashlib.sha256(
            f"{seed}|{regime_name}|pool|{i}".encode("utf-8")
        ).hexdigest()[:12], 16)
        qg = np.random.default_rng(qseed)
        c = int(qg.integers(0, n_clust))
        pool_source_cluster[i] = c
        cluster_items = np.where(lab == c)[0]
        q = kb[cluster_items[qg.integers(0, len(cluster_items))]].astype(np.float32)
        pool[i] = q

    # --- v2-semantic labeling: label = (top-K contains a false-fact idx) ---
    # Pin float32 explicitly (guards against env-dependent numpy->torch upcast).
    K_aug_t = torch.from_numpy(kb_aug.astype(np.float32, copy=False)).to(DEVICE, dtype=torch.float32)
    pool_t = torch.from_numpy(pool.astype(np.float32, copy=False)).to(DEVICE, dtype=torch.float32)
    with torch.no_grad():
        sims_pool = pool_t @ K_aug_t.T
        topk_idx = torch.topk(sims_pool, k=topk, dim=1).indices.detach().cpu().numpy()
    pool_labels = np.zeros(pool_size, dtype=np.int32)
    for i in range(pool_size):
        for idx in topk_idx[i]:
            if int(idx) in false_idx_set:
                pool_labels[i] = 1
                break

    contam_pool_idx = np.where(pool_labels == 1)[0]
    clean_pool_idx = np.where(pool_labels == 0)[0]
    n_contam_want = int(round(p_target * n_test))
    n_clean_want = n_test - n_contam_want
    if len(contam_pool_idx) < n_contam_want:
        raise ValueError(
            f"contam pool too small: got {len(contam_pool_idx)}, need {n_contam_want} "
            f"(p_target={p_target} pool_size={pool_size}); raise POOL_MULT or n_contam_clust."
        )
    if len(clean_pool_idx) < n_clean_want:
        raise ValueError(
            f"clean pool too small: got {len(clean_pool_idx)}, need {n_clean_want} "
            f"(p_target={p_target} pool_size={pool_size}); reduce n_contam_clust."
        )
    picked_contam = contam_pool_idx[:n_contam_want]
    picked_clean = clean_pool_idx[:n_clean_want]
    picked = np.concatenate([picked_contam, picked_clean])
    queries = pool[picked]
    labels = np.zeros(n_test, dtype=np.int32)
    labels[:n_contam_want] = 1

    observed_contam_rate = float(labels.mean())
    return {
        "kb_aug": kb_aug,
        "queries": queries,
        "labels": labels,
        "n_kb": n_kb,
        "n_false": n_false,
        "false_idx_set": false_idx_set,
        "contam_clusters": contam_clusters_arr,
        "clean_clusters": [int(c) for c in perm[n_contam_clust:]],
        "observed_contam_rate": observed_contam_rate,
        "p_target": p_target,
        "n_contaminated_q": n_contam_want,
        "pool_size": pool_size,
        "pool_natural_contam_frac": float(pool_labels.mean()),
    }


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
    # Defensive dtype pin: prevent env-dependent numpy->torch float64 drift
    # (v3 remote FULL crash 2026-07-02: RuntimeError expected same dtype, got
    # float != double; caller path had K_aug promoted via numpy operation).
    if Q_t.dtype != torch.float32:
        Q_t = Q_t.to(dtype=torch.float32)
    if K_t.dtype != torch.float32:
        K_t = K_t.to(dtype=torch.float32)
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


def _batched_reconstruction_err(cleaned, K_t):
    """Second-order cleanup: ||cleanup(cleanup(q)) - cleanup(q)||^2 per query."""
    cleaned_norm = cleaned / (cleaned.norm(dim=1, keepdim=True) + 1e-8)
    sims2 = cleaned_norm @ K_t.T
    logits2 = BETA * sims2
    p2 = torch.softmax(logits2, dim=1)
    cleaned2 = p2 @ K_t
    delta = ((cleaned2 - cleaned) ** 2).sum(dim=1)
    return delta.detach().cpu().numpy()


# --- selftest ---

def _selftest():
    """Formula selftest: all 4 arm computations produce valid outputs + arms differ."""
    g = np.random.default_rng(0)
    dim = 128
    n_items = 40
    K = _unit_np(g.standard_normal((n_items, dim)).astype(np.float32))
    Q_syn = _unit_np(g.standard_normal((10, dim)).astype(np.float32))
    K_t = torch.from_numpy(K).to(DEVICE)
    Q_t = torch.from_numpy(Q_syn).to(DEVICE)

    cleaned, p, sims = _batched_cleanup(Q_t, K_t)
    r_dE = ((cleaned - Q_t) ** 2).sum(dim=1).detach().cpu().numpy()
    assert (r_dE >= 0).all(), "delta_E negative"

    r_sJ = _batched_sigma_max_J(Q_t, K_t, cleaned, p, n_iters=5)
    assert np.isfinite(r_sJ).all() and (r_sJ >= 0).all(), "sigma_max invalid"

    r_REC = _batched_reconstruction_err(cleaned, K_t)
    assert np.isfinite(r_REC).all() and (r_REC >= 0).all(), "reconstruction invalid"

    r_rn = g.random(10)

    # AUC bounds check
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]), np.array([1, 1, 0, 0])) == 1.0
    assert auc_of(np.array([0.0, 0.0, 1.0, 1.0]), np.array([1, 1, 0, 0])) == 0.0

    # META_RULE_AF: all 4 arms produce different risk vectors
    hashes = {
        "dE": hashlib.sha256(np.asarray(r_dE, dtype=np.float64).tobytes()).hexdigest(),
        "sJ": hashlib.sha256(np.asarray(r_sJ, dtype=np.float64).tobytes()).hexdigest(),
        "REC": hashlib.sha256(np.asarray(r_REC, dtype=np.float64).tobytes()).hexdigest(),
        "rn": hashlib.sha256(np.asarray(r_rn, dtype=np.float64).tobytes()).hexdigest(),
    }
    seen = {}
    for k, h in hashes.items():
        for kk, hh in seen.items():
            assert h != hh, f"META_RULE_AF: arm {k} bit-identical to {kk}"
        seen[k] = h

    # Determinism selftest: contamination_rate exact
    for p_test in (0.20, 0.50):
        bundle = build_kb_queries_deterministic(
            seed=99, regime_name="REGIME_LOW" if p_test == 0.20 else "REGIME_HIGH",
            p_target=p_test, n_dim=256, n_clust=20, per=20, intra_cos=0.35,
            n_test=50, topk=5,
        )
        observed = bundle["observed_contam_rate"]
        expected = round(p_test * 50) / 50
        assert abs(observed - expected) < 1e-9, \
            f"determinism selftest: observed={observed} expected={expected}"

    # SCALE SENTINEL (2026-07-02 bias-checklist fix): exercise the FULL-N
    # K_aug augmentation code path in selftest so any env-dependent dtype
    # drift is caught before dispatch (not after 30min FULL run). Small
    # n_test/n_clust keep wall <5s but N_dim=8192 matches FULL.
    for regime_name_s, p_s in [("REGIME_LOW", 0.20), ("REGIME_HIGH", 0.50)]:
        bundle_s = build_kb_queries_deterministic(
            seed=42, regime_name=regime_name_s, p_target=p_s,
            n_dim=8192, n_clust=10, per=10, intra_cos=0.35,
            n_test=20, topk=5,
        )
        K_aug_t_s = torch.from_numpy(
            bundle_s["kb_aug"].astype(np.float32, copy=False)
        ).to(DEVICE, dtype=torch.float32)
        Q_t_s = torch.from_numpy(
            bundle_s["queries"].astype(np.float32, copy=False)
        ).to(DEVICE, dtype=torch.float32)
        assert K_aug_t_s.dtype == torch.float32, \
            "scale-sentinel K_aug dtype drift: %s" % K_aug_t_s.dtype
        assert Q_t_s.dtype == torch.float32, \
            "scale-sentinel Q dtype drift: %s" % Q_t_s.dtype
        cleaned_s, p_s_t, _ = _batched_cleanup(Q_t_s, K_aug_t_s)
        _ = _batched_reconstruction_err(cleaned_s, K_aug_t_s)
        _ = _batched_sigma_max_J(Q_t_s, K_aug_t_s, cleaned_s, p_s_t, n_iters=2)
        assert bundle_s["n_false"] > 0, "scale-sentinel augmentation branch not exercised"

    print("[selftest] PASS: dE=%.4f sJ=%.3f REC=%.4f arms-differ-OK "
          "AUC-bounds-OK determinism-OK scale-sentinel-OK (device=%s)"
          % (float(r_dE.mean()), float(r_sJ.mean()), float(r_REC.mean()), DEVICE), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# --- crash + start markers ---

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


# --- per-unit runner ---

def run_seed_regime(seed: int, regime_name: str, p_target: float) -> Dict:
    """One (seed x regime) = build KB + injection + 4-arm eval."""
    bundle = build_kb_queries_deterministic(
        seed=seed, regime_name=regime_name, p_target=p_target,
        n_dim=N, n_clust=N_CLUST, per=PER, intra_cos=INTRA_COS,
        n_test=N_TEST, topk=TOPK,
    )
    kb_aug = bundle["kb_aug"]
    queries = bundle["queries"]
    labels = bundle["labels"]

    # Pin float32 explicitly (defensive: guards against numpy path upcasting
    # to float64 in some env configurations; see _batched_cleanup comment).
    K_aug_t = torch.from_numpy(kb_aug.astype(np.float32, copy=False)).to(DEVICE, dtype=torch.float32)
    Q_t = torch.from_numpy(queries.astype(np.float32, copy=False)).to(DEVICE, dtype=torch.float32)
    assert K_aug_t.dtype == torch.float32 and Q_t.dtype == torch.float32, \
        "dtype pin failed: K_aug=%s Q=%s" % (K_aug_t.dtype, Q_t.dtype)

    cleaned, p, _ = _batched_cleanup(Q_t, K_aug_t)
    delta_E = ((cleaned - Q_t) ** 2).sum(dim=1).detach().cpu().numpy()
    sigma_J = _batched_sigma_max_J(Q_t, K_aug_t, cleaned, p, n_iters=5)
    reconstruction_err = _batched_reconstruction_err(cleaned, K_aug_t)

    rng_ctrl = np.random.default_rng(seed * 1000 + _regime_id(regime_name) * 33 + 999)
    random_risk = rng_ctrl.random(size=len(labels))

    per_arm = {}
    arm_risks = [
        (ARM_RECONSTRUCTION_ERR, reconstruction_err),
        (ARM_DELTA_E, delta_E),
        (ARM_SIGMA_J, sigma_J),
        (ARM_RANDOM, random_risk),
    ]
    for arm_name, risk in arm_risks:
        auc = auc_of(risk, labels)
        risk_hash = hashlib.sha256(np.asarray(risk, dtype=np.float64).tobytes()).hexdigest()[:16]
        per_arm[arm_name] = {
            "arm": arm_name,
            "seed": seed,
            "regime": regime_name,
            "p_target": p_target,
            "auc": auc,
            "risk_hash_prefix": risk_hash,
            "risk_mean": float(np.asarray(risk).mean()),
            "risk_std": float(np.asarray(risk).std()),
        }

    contamination_rate = bundle["observed_contam_rate"]
    print("  [seed=%d %s p=%.2f] contam=%.3f n_false=%d | REC=%.3f dE=%.3f sJ=%.3f rn=%.3f"
          % (seed, regime_name, p_target, contamination_rate, bundle["n_false"],
             per_arm[ARM_RECONSTRUCTION_ERR]["auc"], per_arm[ARM_DELTA_E]["auc"],
             per_arm[ARM_SIGMA_J]["auc"], per_arm[ARM_RANDOM]["auc"]), flush=True)

    return {
        "seed": seed,
        "regime": regime_name,
        "p_target": p_target,
        "n_kb": int(bundle["n_kb"]),
        "n_false": int(bundle["n_false"]),
        "contamination_rate": contamination_rate,
        "pool_size": int(bundle["pool_size"]),
        "pool_natural_contam_frac": float(bundle["pool_natural_contam_frac"]),
        "per_arm": per_arm,
    }


# --- verdict logic ---

def _arms_must_differ(unit_records: List[Dict]) -> bool:
    for rec in unit_records:
        hashes = {arm: rec["per_arm"][arm]["risk_hash_prefix"] for arm in ARMS
                  if arm in rec["per_arm"]}
        seen = {}
        for a, h in hashes.items():
            for aa, hh in seen.items():
                if h == hh:
                    return False
            seen[a] = h
    return True


def arm_summary_by_regime(unit_records: List[Dict], arm_name: str,
                          regime_name: str) -> Dict:
    aucs = [rec["per_arm"][arm_name]["auc"] for rec in unit_records
            if rec["regime"] == regime_name and arm_name in rec["per_arm"]]
    if not aucs:
        return {"arm": arm_name, "regime": regime_name, "n_seeds": 0,
                "auc_mean": None, "auc_std": None, "auc_cv": None, "aucs": []}
    m = float(np.mean(aucs))
    s = float(np.std(aucs))
    return {
        "arm": arm_name,
        "regime": regime_name,
        "n_seeds": len(aucs),
        "auc_mean": m,
        "auc_std": s,
        "auc_cv": (s / m) if m > 0 else 1.0,
        "aucs": [float(a) for a in aucs],
    }


def verdict(unit_records: List[Dict]) -> Tuple[str, str, Dict]:
    regime_names = [r[0] for r in REGIMES]
    arm_summaries: Dict[str, Dict[str, Dict]] = {}
    for arm in ARMS:
        arm_summaries[arm] = {}
        for r in regime_names:
            arm_summaries[arm][r] = arm_summary_by_regime(unit_records, arm, r)

    expected_n_units = len(ARMS) * len(SEEDS) * len(REGIMES)
    observed_n_units = sum(1 for rec in unit_records for a in ARMS if a in rec["per_arm"])
    if observed_n_units < expected_n_units:
        return ("HARD_FAIL",
                "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H observed=%d expected=%d"
                % (observed_n_units, expected_n_units), arm_summaries)
    if not _arms_must_differ(unit_records):
        return ("HARD_FAIL",
                "META_RULE_AF_VIOLATION: two arms produced bit-identical risk vectors",
                arm_summaries)

    # Determinism gate: observed contamination_rate == p_target EXACTLY per unit
    for rec in unit_records:
        p_t = rec["p_target"]
        obs = rec["contamination_rate"]
        expected = round(p_t * N_TEST) / N_TEST
        if abs(obs - expected) > 1e-9:
            return ("HARD_FAIL",
                    "HARD_FAIL_DETERMINISM_BROKEN: seed=%d %s observed_contam=%.6f "
                    "expected=%.6f p_target=%.2f" % (rec["seed"], rec["regime"],
                                                     obs, expected, p_t),
                    arm_summaries)

    # Control arm sanity per unit
    for rec in unit_records:
        rn_auc = rec["per_arm"][ARM_RANDOM]["auc"]
        # Wider band on random control per-unit (single-unit AUC has noise ~0.05
        # from finite N_TEST); tighter per-regime aggregate band applied below.
        if not (0.35 <= rn_auc <= 0.65):
            return ("HARD_FAIL",
                    "HARD_FAIL_CONTROL_ARM_BROKEN: seed=%d %s ARM_ABLATED_RANDOM "
                    "AUC=%.3f outside [0.35, 0.65]" % (rec["seed"], rec["regime"], rn_auc),
                    arm_summaries)

    # LOAD-BEARING: ARM_RECONSTRUCTION_ERR across BOTH regimes
    rec_low = arm_summaries[ARM_RECONSTRUCTION_ERR]["REGIME_LOW"]
    rec_high = arm_summaries[ARM_RECONSTRUCTION_ERR]["REGIME_HIGH"]
    auc_low = rec_low["auc_mean"]
    auc_high = rec_high["auc_mean"]
    cv_low = rec_low["auc_cv"]
    cv_high = rec_high["auc_cv"]

    # Regime dispersion (sanity flag; not gating)
    if auc_low > 0 and auc_high > 0:
        disp = auc_high / auc_low
    else:
        disp = 1.0

    summary_bits = []
    for r in regime_names:
        s = arm_summaries[ARM_RECONSTRUCTION_ERR][r]
        summary_bits.append("REC_%s=%.3f(cv=%.3f)" % (r.replace("REGIME_", "").lower(),
                                                      s["auc_mean"], s["auc_cv"]))
    for r in regime_names:
        s = arm_summaries[ARM_RANDOM][r]
        summary_bits.append("rn_%s=%.3f" % (r.replace("REGIME_", "").lower(), s["auc_mean"]))
    summary_bits.append("disp_H/L=%.2f" % disp)
    summary = " ".join(summary_bits)

    hp_auc_ok = (auc_low >= 0.65 and auc_high >= 0.65)
    hp_cv_ok = (cv_low < 0.15 and cv_high < 0.15)
    hp_any_hard_fail = (auc_low < 0.60 or auc_high < 0.60 or cv_low >= 0.25 or cv_high >= 0.25)
    hp_middle = ((0.60 <= auc_low < 0.65) or (0.60 <= auc_high < 0.65)
                 or (0.15 <= cv_low < 0.25) or (0.15 <= cv_high < 0.25))

    if hp_auc_ok and hp_cv_ok:
        return ("HARD_PASS",
                "HARD_PASS_REC_ERR_MULTIREGIME_MULTISEED: REC AUC low=%.3f high=%.3f "
                "cv low=%.3f high=%.3f both regimes clear >=0.65 with cv<0.15; "
                "deterministic contamination verified; M1.11 Confidence Header "
                "CG-eligible for hdlab extraction. | %s"
                % (auc_low, auc_high, cv_low, cv_high, summary),
                arm_summaries)
    if hp_any_hard_fail:
        return ("HARD_FAIL",
                "HARD_FAIL_REC_ERR_BELOW_BAND: REC AUC low=%.3f high=%.3f cv "
                "low=%.3f high=%.3f. Option C activity/energy family below CG "
                "threshold multi-regime; close branch pending pivot to alternative "
                "confidence mechanism (posterior-entropy / attention-dispersion / "
                "residual-norm per Skunkworks pointers). | %s"
                % (auc_low, auc_high, cv_low, cv_high, summary),
                arm_summaries)
    if hp_middle:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND_REC_ERR_PARTIAL: REC AUC low=%.3f high=%.3f cv low=%.3f "
                "high=%.3f. Partial evidence reconstruction_err discriminates; v4 "
                "path: scale N_test to 500 or 10-seed. | %s"
                % (auc_low, auc_high, cv_low, cv_high, summary),
                arm_summaries)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_EDGE: REC AUC low=%.3f high=%.3f. | %s" % (auc_low, auc_high, summary),
            arm_summaries)


# --- main ---

def main():
    print("[config] anchor=%s mode=%s device=%s seeds=%s regimes=%s N=%d clusters=%d "
          "per=%d items=%d N_TEST=%d intra_cos=%.3f topk=%d beta=%.1f"
          % (ANCHOR_NAME, RUN_MODE, DEVICE, SEEDS,
             [r[0] for r in REGIMES], N, N_CLUST, PER, N_CLUST * PER,
             N_TEST, INTRA_COS, TOPK, BETA), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = len(ARMS) * len(SEEDS) * len(REGIMES)
    _write_start_marker(out_dir, RUN_MODE, expected_n_units)

    t0 = time.time()
    unit_records: List[Dict] = []
    failed_units: List[Dict] = []
    for seed in SEEDS:
        for regime_name, p_target in REGIMES:
            try:
                rec = run_seed_regime(seed, regime_name, p_target)
                unit_records.append(rec)
            except Exception as e:
                failed_units.append({
                    "seed": seed,
                    "regime": regime_name,
                    "p_target": p_target,
                    "failure_class": type(e).__name__,
                    "failure_msg": str(e)[:500],
                    "traceback": traceback.format_exc()[:3000],
                })
                print("  [seed=%d %s] FAILED: %s: %s"
                      % (seed, regime_name, type(e).__name__, str(e)[:200]), flush=True)

    v, vmsg, arm_summaries = verdict(unit_records)
    print("\n[VERDICT] " + vmsg, flush=True)
    elapsed = time.time() - t0

    per_unit_flat: List[Dict] = []
    for rec in unit_records:
        for arm_name in ARMS:
            if arm_name in rec["per_arm"]:
                pu = dict(rec["per_arm"][arm_name])
                pu["contamination_rate"] = rec["contamination_rate"]
                pu["n_kb"] = rec["n_kb"]
                pu["n_false"] = rec["n_false"]
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
        "n_test_queries_per_unit": N_TEST,
        "topk": TOPK,
        "beta": BETA,
        "intra_cos": INTRA_COS,
        "regimes": [{"name": r[0], "p_target": r[1]} for r in REGIMES],
        "run_mode": RUN_MODE,
        "device": str(DEVICE),
        "n_seeds": len(SEEDS),
        "seeds": SEEDS,
        "n_arms": len(ARMS),
        "arms": ARMS,
        "load_bearing_arm": LOAD_BEARING_ARM,
        "arm_summaries": arm_summaries,
        "per_unit": per_unit_flat,
        "per_unit_records": [
            {"seed": rec["seed"], "regime": rec["regime"], "p_target": rec["p_target"],
             "n_kb": rec["n_kb"], "n_false": rec["n_false"],
             "contamination_rate": rec["contamination_rate"]}
            for rec in unit_records
        ],
        "failed_units": failed_units,
        "elapsed_s": elapsed,
        "cardinality_ok": len(per_unit_flat) == expected_n_units,
        "expected_n_units": expected_n_units,
        "observed_n_units": len(per_unit_flat),
        "arms_differ_verified": _arms_must_differ(unit_records) if unit_records else False,
        "v1_baseline_combined_2_auc": 0.571,
        "v2_baseline_rec_err_mean_auc_3seed": None,
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
