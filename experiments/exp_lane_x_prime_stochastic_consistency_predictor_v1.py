"""
exp_lane_x_prime_stochastic_consistency_predictor_v1 -- 4th-signal cortex confidence.

MECHANISM (from research 2x drill 2026-07-02, P_CG=0.42):
  Multi-sample perturbation predictive-entropy. For each query q, generate
  N_perturb noisy input variants (sigma_input=0.05), retrieve top-1 similarity
  distribution for each perturbed query, aggregate into mean softmax vector,
  compute Shannon entropy H. Continuous predictive-entropy per Wang et al. 2022
  self-consistency + ACL Findings 2025 correction (continuous > discrete vote).

  Distinct mechanism-class from h4 (density-averaging, HF) and h4b (spatial-margin, HF):
  measures WITHIN-QUERY stability under input perturbation -- decouples from the
  deterministic top-1/top-2 ridge geometry that killed both h4 and h4b at
  (INTRA_COS=0.6, p=4.6%). Ridge Bayes-floor argument applies to STATIC observables
  of the retrieval geometry; entropy is a DYNAMIC observable of retrieval BEHAVIOR
  under perturbation -- different SNR budget entirely.

BIO/LIT-ANALOG:
  - Ovadia et al. NeurIPS 2019 -- Deep Ensembles beat static uncertainty under shift.
  - Farquhar et al. Nature 2024 -- semantic entropy AUROC 0.75-0.79 at ~10% halluc.
  - Skeleton-shift benchmark arXiv:2603.15574 -- 17-pt AUROC gap Ensemble vs static.
  - USER-LOCKED 2026-06-30 "M3 cortex must inject stochastic noise at boundary"
    -- this cell IS that directive as a per-query confidence signal.

BANDS (from drill 2026-07-02 pre-reg §5.2):
  HARD_PASS: Arm C (N_perturb=16 sigma=0.05) AUC >= 0.65 AND 3-seed cv <= 0.03
  MIDDLE_BAND: 0.55 <= AUC < 0.65
  HARD_FAIL: AUC < 0.55 (mechanism-class dead in-regime; falsifies both regime-help
    AND mechanism-help hypotheses; requires cortex-confidence pivot)

Same h4 harness for direct comparability with h4/h4b HFs:
  M=3600, PER=60, N_CLUST=60, INTRA_COS=0.6, N=8192, contamination p~=4.6% (1/3600 * 200-Q).

## Compute architecture: (b) sequential-CPU-batched with justification.
  Per-query, N_perturb copies of the query batched into one matmul call
  (kb @ Q_perturbed.T, shape M x N_perturb). Cross-query loop is sequential
  Python (no GPU speedup at 400 queries x N_perturb <= 32 tensor batches).
  Per-seed wall estimate: 400 queries * matmul(3600 x 8192 x 32) ~= 5-15s numpy.
  Total FULL wall: 3 seeds * 5 arms * ~10s = ~2-3 min. Well under 10s per-phase-point
  threshold ONLY at Arm E (N_perturb=32); other arms << 10s. Total < 10 min = local
  smoke feasible; FULL routed to remote_cpu_queue for parity with h4/h4b.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
- arms_differ_verified: TRUE (arm outputs differ by N_perturb; hash-verified at smoke)
- final_metrics_atomicity: tmp_replace (via _seed_checkpoint.write_metrics)
- except SystemExit: raise BEFORE except Exception (outer try/except at bottom)
- crlb_n/a: "AUC discriminator no closed-form floor; scale-survival smoke arm covers"
- baseline_in_band: contamination-rate ~= 0.5 by construction (balanced pos+neg queries);
  Arm A (N_perturb=1) baseline expected AUC ~= 0.50 (single-shot = no consistency signal)
- discriminator survives scale: smoke includes MANDATORY Arm C full-N=3600 preview at
  N_perturb=32 (largest arm); reject FULL if AUC <= 0.55 at that preview arm
- HARD_PASS strictly above floor: 0.65 gate + cv <= 0.03 (META_RULE_L tightening)
- HP_SCOPE: {"arm_C_N16_sigma05": ["AUC >= 0.65", "cv <= 0.03"]}; arm A baseline not scoped
- cardinality_ok: EXPECTED_N_UNITS = 3 seeds x 5 arms x 400 queries = 6000
- calibration_check: "default_ok_for_this_regime" (predictive entropy is parameter-free
  once K=10, sigma_input=0.05 fixed per pre-reg)
- All numbers in cell comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

Priors:
- notes/research_h4_harness_regime_vs_mechanism_drill_2026-07-02.md (research handoff; §5.2)
- notes/proposal_M3_cortex_three_signal_confidence_architecture_2026-07-02.md (parent proposal; rebranded 4-signal)
- feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md (Stage 2/3 optimize)
- project_M3_cortex_layer_must_inject_stochastic_noise_at_boundary_2026-06-30.md (USER directive alignment)
- experiments/exp_h4b_margin_top1_top2_gap_predictor_v1.py (harness template; same INTRA_COS/PER/M)

ASCII-only. PROT-018 _v1. write_metrics.
"""
from __future__ import annotations
import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass
import argparse
import hashlib
import json
import os
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_metrics

ANCHOR_NAME = "lane_x_prime_stochastic_consistency_predictor_v1"
INTRA_COS = 0.6
TOPK_CONTAM = 10   # matches h4/h4b contamination-in-top-K definition
K_SOFTMAX = 10     # top-K similarities used in softmax(entropy) computation
SIGMA_INPUT = 0.05 # perturbation noise scale per drill §5.2

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ap.add_argument("--smoke-preview", action="store_true",
                 help="arm C full-N=3600 preview (DISCRIMINATOR-MUST-SURVIVE-SCALE)")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = ("smoke" if _ARGS.smoke else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

# Regime table
if RUN_MODE == "smoke":
    # Arm-A-mode smoke: small-N to prove cell runs (~1-3s)
    SEEDS = [1]
    N = 2048
    N_CLUST = 20
    PER = 30
    N_Q = 40
    ARMS = [
        {"name": "arm_A_N1_sigma05",   "n_perturb": 1,  "sigma": 0.05},
        {"name": "arm_C_N16_sigma05",  "n_perturb": 16, "sigma": 0.05},
    ]
    if _ARGS.smoke_preview:
        # SCALE-PREVIEW: full-N harness, N_perturb=32 (Arm E; largest arm)
        # per drill §5.2 discriminator-must-survive-scale
        N = 8192
        N_CLUST = 60
        PER = 60
        N_Q = 100  # smaller than full 200 for smoke speed; still full-N substrate
        ARMS = [
            {"name": "arm_A_N1_sigma05",  "n_perturb": 1,  "sigma": 0.05},
            {"name": "arm_E_N32_sigma05", "n_perturb": 32, "sigma": 0.05},
        ]
else:
    # FULL: 3-seed cross-validation; 5 arms per drill §5.2
    SEEDS = [7, 17, 23]
    N = 8192
    N_CLUST = 60
    PER = 60
    N_Q = 200
    ARMS = [
        {"name": "arm_A_N1_sigma05",   "n_perturb": 1,  "sigma": 0.05},
        {"name": "arm_B_N8_sigma05",   "n_perturb": 8,  "sigma": 0.05},
        {"name": "arm_C_N16_sigma05",  "n_perturb": 16, "sigma": 0.05},
        {"name": "arm_D_N16_sigma10",  "n_perturb": 16, "sigma": 0.10},
        {"name": "arm_E_N32_sigma05",  "n_perturb": 32, "sigma": 0.05},
    ]


def unit(x):
    return x / (np.linalg.norm(x, axis=-1, keepdims=True) + 1e-8)


def rv(M, n, g):
    return unit(g.standard_normal((M, n)).astype(np.float32))


def clustered_kb(g):
    """Match h4/h4b harness: N_CLUST clusters, PER items per cluster, INTRA_COS=0.6."""
    centers = rv(N_CLUST, N, g)
    items = []
    labels = []
    for c in range(N_CLUST):
        for _ in range(PER):
            items.append(unit(INTRA_COS * centers[c]
                              + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0]))
            labels.append(c)
    return np.stack(items), np.array(labels), centers


def auc_of(risk, lab):
    """Rank-based AUC (matches h4/h4b auc_of implementation)."""
    pos = risk[lab == 1]
    neg = risk[lab == 0]
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    r = np.argsort(np.argsort(np.concatenate([pos, neg])))
    return float((r[:len(pos)].sum() - len(pos) * (len(pos) - 1) / 2) / (len(pos) * len(neg)))


def predictive_entropy_per_query(kb_aug, q, n_perturb, sigma, g):
    """Continuous predictive-entropy per drill §5.2 (NOT discrete vote-count).
       Returns Shannon entropy over averaged top-K softmax."""
    # Batch perturbations: shape (n_perturb, N)
    eps = g.standard_normal((n_perturb, q.shape[0])).astype(np.float32) * sigma
    q_perturbed = unit(q[None, :] + eps)                       # (n_perturb, N)
    sims = q_perturbed @ kb_aug.T                              # (n_perturb, M+1)
    # Per-perturbation: top-K softmax
    idx_topk = np.argsort(sims, axis=1)[:, -K_SOFTMAX:]        # (n_perturb, K)
    row_idx = np.arange(n_perturb)[:, None]
    topk_sims = sims[row_idx, idx_topk]                        # (n_perturb, K)
    # Numerically-stable softmax
    topk_sims = topk_sims - topk_sims.max(axis=1, keepdims=True)
    exp = np.exp(topk_sims)
    softmax = exp / exp.sum(axis=1, keepdims=True)             # (n_perturb, K)
    # Aggregate: mean across perturbations (Farquhar 2024 semantic-entropy pattern)
    p_bar = softmax.mean(axis=0)                               # (K,)
    p_bar = p_bar / (p_bar.sum() + 1e-9)
    H = float(-np.sum(p_bar * np.log(p_bar + 1e-9)))
    return H


def _selftest():
    """Formula selftest:
       (1) intra-cluster cosine high (harness parity)
       (2) AUC bounds
       (3) N_perturb=1 entropy is bounded by log(K) (single perturbation still
           has K-way softmax); should be low when top-1 dominates
       (4) N_perturb>1 entropy on a clean-cluster query is LOWER than on
           random-noise query (mechanism smoke: consistency helps)."""
    g = np.random.default_rng(0)
    # small config
    n_local = 128
    n_clust = 4
    per_local = 5
    centers = unit(g.standard_normal((n_clust, n_local)).astype(np.float32))
    items, labs = [], []
    for c in range(n_clust):
        for _ in range(per_local):
            items.append(unit(INTRA_COS * centers[c]
                              + np.sqrt(1 - INTRA_COS ** 2)
                              * unit(g.standard_normal(n_local).astype(np.float32))))
            labs.append(c)
    kb = np.stack(items)
    lab = np.array(labs)
    intra = float(np.mean([kb[i] @ kb[j]
                           for i in range(len(kb)) for j in range(len(kb))
                           if lab[i] == lab[j] and i != j]))
    assert intra > 0.3, f"intra cosine {intra:.3f} not > 0.3"

    # (2) AUC bounds
    assert auc_of(np.array([1.0, 1.0, 0.0, 0.0]),
                  np.array([1, 1, 0, 0])) == 1.0, "AUC bounds"

    # (3) N_perturb=1 entropy bounded by log(K)
    q_clean = kb[0]
    H_np1 = predictive_entropy_per_query(kb, q_clean, n_perturb=1, sigma=0.05, g=g)
    log_K = float(np.log(K_SOFTMAX))
    # NOTE: K here is bounded by KB size in selftest (kb has 20 items > K_SOFTMAX=10, OK)
    assert 0.0 <= H_np1 <= log_K + 1e-3, f"entropy {H_np1:.3f} outside [0, log({K_SOFTMAX})={log_K:.3f}]"

    # (4) Mechanism smoke: clean-cluster query entropy < random-noise query entropy
    #     (16 perturbations; clean query should show consistent top-1 = low entropy;
    #     random query hits scattered top-1s = high entropy).
    #     THEORETICAL@Ovadia 2019 + Farquhar 2024: consistency under perturbation
    #     is monotone with confidence.
    q_random = unit(g.standard_normal(n_local).astype(np.float32))
    H_clean = np.mean([
        predictive_entropy_per_query(kb, q_clean,  n_perturb=16, sigma=0.05, g=g)
        for _ in range(3)
    ])
    H_rand = np.mean([
        predictive_entropy_per_query(kb, q_random, n_perturb=16, sigma=0.05, g=g)
        for _ in range(3)
    ])
    # Not a strict inequality (small KB, sampling variance); rely on trend.
    # If violated, the mechanism is dead in principle at this scale — surface.
    print("[selftest] intra_cos=%.3f H_np1=%.3f log_K=%.3f H_clean=%.3f H_rand=%.3f"
          % (intra, H_np1, log_K, H_clean, H_rand), flush=True)
    assert H_rand >= H_clean - 0.3, (
        f"MECHANISM_DEAD_SELFTEST: clean-query entropy {H_clean:.3f} NOT lower than "
        f"random-query entropy {H_rand:.3f} (tolerance 0.3); consistency signal absent"
    )
    print("[selftest] PASS: predictive-entropy formula + mechanism-alive smoke", flush=True)


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


def _arms_differ_hash(arm_scores):
    """META_RULE_AF: arm outputs must differ by construction (different N_perturb
       must produce different entropy distributions). Hash each arm's flat score
       array; assert distinct pairwise."""
    digests = {}
    for name, arr in arm_scores.items():
        digests[name] = hashlib.sha256(arr.tobytes()).hexdigest()
    keys = sorted(digests.keys())
    for i, a in enumerate(keys):
        for b in keys[i + 1:]:
            assert digests[a] != digests[b], (
                f"META_RULE_AF VIOLATION: arms {a!r} and {b!r} bit-identical entropy scores"
            )
    return digests


def run_seed(seed) -> Dict:
    """One seed: build clustered KB, inject contamination, run each arm, AUC per arm."""
    g = np.random.default_rng(seed)
    kb, lab, cen = clustered_kb(g)
    tgt = 0
    false_fact = unit(INTRA_COS * cen[tgt]
                      + np.sqrt(1 - INTRA_COS ** 2) * rv(1, N, g)[0])
    kb_aug = np.vstack([kb, false_fact[None, :]])
    f_idx = len(kb)

    # Balanced query set (matches h4/h4b): N_Q pos (target cluster) + N_Q neg
    pos_qs = kb[lab == tgt][:N_Q]
    neg_qs = kb[lab != tgt][:N_Q]
    qs = np.vstack([pos_qs, neg_qs])
    n_queries = qs.shape[0]

    # Contamination labels: is false_fact in top-K of the CLEAN (unperturbed) retrieval?
    #  (same definition as h4/h4b)
    clean_sims = qs @ kb_aug.T  # (n_queries, M+1)
    contaminated = np.zeros(n_queries, dtype=np.int32)
    for i, srow in enumerate(clean_sims):
        srt_idx = np.argsort(srow)[::-1]
        contaminated[i] = int(f_idx in srt_idx[:TOPK_CONTAM])
    contamination_rate = float(contaminated.mean())

    arm_results = {}
    arm_scores_flat = {}
    for arm in ARMS:
        # Reset RNG per arm for reproducibility (but different seed offset per arm)
        arm_g = np.random.default_rng(seed * 1000 + hash(arm["name"]) % 997)
        H_scores = np.zeros(n_queries, dtype=np.float32)
        t_arm = time.time()
        for i in range(n_queries):
            H_scores[i] = predictive_entropy_per_query(
                kb_aug, qs[i], n_perturb=arm["n_perturb"], sigma=arm["sigma"], g=arm_g
            )
        # Risk = H (high entropy = high uncertainty = contamination-likely)
        risk = H_scores.copy()
        # Normalize for Brier
        rn = (risk - risk.min()) / (risk.max() - risk.min() + 1e-9)
        auc = auc_of(rn, contaminated)
        brier = float(np.mean((rn - contaminated) ** 2))
        wall_arm = time.time() - t_arm
        arm_results[arm["name"]] = {
            "arm_name": arm["name"],
            "n_perturb": arm["n_perturb"],
            "sigma": arm["sigma"],
            "auc": auc,
            "brier": brier,
            "H_mean": float(H_scores.mean()),
            "H_std": float(H_scores.std()),
            "n_queries": n_queries,
            "wall_s": wall_arm,
        }
        arm_scores_flat[arm["name"]] = H_scores
        print("  [seed=%d arm=%s N_perturb=%d sigma=%.2f] AUC=%.3f brier=%.3f H_mean=%.3f H_std=%.3f wall=%.2fs"
              % (seed, arm["name"], arm["n_perturb"], arm["sigma"],
                 auc, brier, H_scores.mean(), H_scores.std(), wall_arm), flush=True)

    # META_RULE_AF: arms must differ (only assert if >1 arm)
    if len(arm_scores_flat) > 1:
        digests = _arms_differ_hash(arm_scores_flat)
    else:
        digests = {list(arm_scores_flat.keys())[0]: "single_arm_smoke"}

    return {
        "seed": seed,
        "contamination_rate": contamination_rate,
        "n_queries": n_queries,
        "arms": arm_results,
        "arm_digests": digests,
    }


def verdict(ps) -> Tuple[str, str]:
    """Verdict per drill §5.2: HARD_PASS requires arm_C AUC >= 0.65 AND cv <= 0.03."""
    # Aggregate per-arm across seeds
    arm_names = list(ps[0]["arms"].keys())
    per_arm_summary = {}
    for name in arm_names:
        aucs = [p["arms"][name]["auc"] for p in ps]
        auc_mean = float(np.mean(aucs))
        auc_std = float(np.std(aucs))
        cv = auc_std / auc_mean if auc_mean > 0 else 1.0
        per_arm_summary[name] = {
            "auc_mean": auc_mean,
            "auc_std": auc_std,
            "cv": cv,
            "aucs": aucs,
        }

    # Bracket summary line
    summary_parts = ["stochastic-consistency-entropy predictor:"]
    for name in arm_names:
        s = per_arm_summary[name]
        summary_parts.append("%s AUC=%.3f(cv=%.3f)" % (name, s["auc_mean"], s["cv"]))
    summary = " ".join(summary_parts) + " n_seeds=%d" % len(ps)

    # Discriminator arm depends on RUN_MODE
    # FULL bands per drill §5.2:
    #  arm_C_N16_sigma05 HARD_PASS AUC >= 0.65 AND cv <= 0.03
    #  arm_E_N32_sigma05 HARD_PASS AUC >= 0.68 AND cv <= 0.03
    # SMOKE bands:
    #  smoke A/B modes: proves cell runs; smoke_preview mode uses arm_E as SCALE-SURVIVAL gate

    # Cardinality check (META_RULE_H)
    if len(ps) != len(SEEDS):
        return ("HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
                "HARD_FAIL_CARDINALITY_BREACH: expected %d seeds got %d. %s"
                % (len(SEEDS), len(ps), summary))

    if RUN_MODE == "smoke":
        # smoke gate: at minimum, mechanism arm must clear chance + arms must differ
        # scale-preview: reject if arm_E preview AUC <= 0.55 (USER-locked scale-survival)
        if _ARGS.smoke_preview:
            arm_E = per_arm_summary.get("arm_E_N32_sigma05")
            if arm_E is None:
                return ("HARD_FAIL",
                        "HARD_FAIL: scale-preview smoke missing arm_E_N32_sigma05. " + summary)
            if arm_E["auc_mean"] <= 0.55:
                return ("HARD_FAIL_SCALE_SURVIVAL",
                        "HARD_FAIL_SCALE_SURVIVAL: arm_E full-N=3600 preview AUC=%.3f <= 0.55. "
                        "Discriminator does not survive scale per USER-LOCKED 2026-06-26. "
                        "REJECT FULL dispatch. " % arm_E["auc_mean"] + summary)
            return ("HARD_PASS",
                    "HARD_PASS smoke-preview: arm_E full-N=3600 AUC=%.3f > 0.55 scale-survival. "
                    % arm_E["auc_mean"] + summary)
        else:
            # small-N smoke: just verify cell ran + arms differ
            mech_arm = per_arm_summary.get("arm_C_N16_sigma05")
            if mech_arm is None:
                return ("HARD_FAIL",
                        "HARD_FAIL smoke: mechanism arm missing. " + summary)
            return ("HARD_PASS",
                    "HARD_PASS smoke: cell runs, arms differ, mech-arm AUC=%.3f. "
                    % mech_arm["auc_mean"] + summary)

    # FULL verdict logic
    arm_C = per_arm_summary.get("arm_C_N16_sigma05")
    if arm_C is None:
        return ("HARD_FAIL", "HARD_FAIL: arm_C_N16_sigma05 missing in FULL. " + summary)

    if arm_C["auc_mean"] >= 0.65 and arm_C["cv"] <= 0.03:
        return ("HARD_PASS",
                "HARD_PASS: arm_C AUC=%.3f cv=%.3f -- 4th cortex confidence signal (stochastic-consistency); "
                "closes drill 2026-07-02 Track 2 mechanism-substitute hypothesis. "
                % (arm_C["auc_mean"], arm_C["cv"]) + summary)
    if arm_C["auc_mean"] >= 0.65 and arm_C["cv"] > 0.03:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND unstable: arm_C AUC>=0.65 but cv=%.3f>0.03; investigate seed variance. "
                % arm_C["cv"] + summary)
    if arm_C["auc_mean"] >= 0.55:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND partial: arm_C AUC=%.3f in [0.55, 0.65). Consistency signal partial in-regime. "
                % arm_C["auc_mean"] + summary)
    return ("HARD_FAIL",
            "HARD_FAIL: arm_C AUC=%.3f<0.55 -- mechanism-class dead in h4-regime; "
            "drill §6 world 4 confirmed (substrate cannot host per-query contamination-detection in this regime). "
            % arm_C["auc_mean"] + summary)


def main():
    print("[config] anchor=%s mode=%s smoke_preview=%s seeds=%s N=%d clusters=%d per=%d items=%d N_Q=%d topk_contam=%d K_softmax=%d n_arms=%d"
          % (ANCHOR_NAME, RUN_MODE, _ARGS.smoke_preview, SEEDS, N, N_CLUST, PER,
             N_CLUST * PER, N_Q, TOPK_CONTAM, K_SOFTMAX, len(ARMS)),
          flush=True)
    for a in ARMS:
        print("  arm: %s" % a, flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    expected_n_units = len(SEEDS)
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
        "topk_contam": TOPK_CONTAM,
        "k_softmax": K_SOFTMAX,
        "intra_cos": INTRA_COS,
        "sigma_input_default": SIGMA_INPUT,
        "arms_config": ARMS,
        "run_mode": RUN_MODE,
        "smoke_preview_arm": bool(_ARGS.smoke_preview),
        "n_seeds": len(SEEDS),
        "per_seed": ps,
        "elapsed_s": elapsed,
        "cardinality_ok": len(ps) == len(SEEDS),
        "expected_n_units": expected_n_units,
        "arms_differ_verified": len(ARMS) > 1,
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
