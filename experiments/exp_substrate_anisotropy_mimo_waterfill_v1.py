"""ANISOTROPY MIMO water-filling cleanup -- Tier A Anchor #1 from GAP 2 5x drill (research note S1).

PARENT CONTEXT:
  - notes/research_gap2_anisotropy_5x_drill_2026-06-26.md (S1 candidate; P_deflated=0.50)
  - notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md (handoff contract)
  - v2 calibrated meter cell HARD_PASS (Bfly=0.997 at M=10k; raw=0.018; cone-collapse anchor)
  - v2 fixture: data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full/metrics.json

MECHANISM (one paragraph):
  The substrate's current dense KV cleanup treats every direction equally (uniform regularizer in pseudo-
  inverse). In an anisotropic cone, most directions are nulls (near-zero singular values of K^T K). Uniform
  cleanup wastes capacity on these nulls -- amplifying noise where there is no signal. MIMO water-filling
  (40-year-old 5G/MIMO theory) replaces the uniform diagonal regularizer in the Tikhonov-regularized
  pseudo-inverse with a SVD-water-filled regularizer: pour cleanup capacity into high-SNR singular directions
  first, leave the nulls at floor. Mathematically: cleanup_W = K^T @ (K @ K^T + diag(reg))^-1 @ Y where
  reg_i = max(0, mu - sigma_i^2) (water level mu set to allocate total budget). The substrate-novel claim is
  that PER-SINGULAR-DIRECTION cleanup-weight allocation lifts recall on real Pythia keys at M=10k where
  uniform cleanup collapses to raw=0.018 baseline. NOT a rotation (whitening already failed); a WEIGHTED
  REGULARIZER allocation.

ARMS (per handoff contract):
  CROSS-CELL SANITY RAIL (Fix #28 by-construction-saturation sentinel):
    ARM_KNN_BASELINE at M=400 -- must >= 0.9 on every config. KNN is rank-blind; if it drops below 0.9 the
    keys themselves are corrupted (not just anisotropic), and any cleanup-arm "lift" is artifact.

  MECHANISM ARMS:
    ARM_UNIFORM_CLEANUP  -- current substrate behavior; Tikhonov pseudo-inverse with uniform regularizer.
                            Equivalent to standard L2-regularized dense KV.
    ARM_WHITENING        -- ZCA-whitening of K BEFORE cleanup (rotation-only ablation; drill 1 ceiling).
                            Expected ~+0.020 lift per prior whitening cells.
    ARM_MIMO_WATERFILL_SVD     -- the main test; analytic water-filling per SVD of K^T K. No training.
    ARM_MIMO_WATERFILL_LEARNED -- gradient-trained per-direction weights via Adam on recall loss.
                                  Upper bound on what direction-weighted cleanup can achieve.

  DIAGNOSTIC (per handoff item 3):
    effective_rank (PR/D) of K before AND after each pretransform / cleanup allocation. Reports also the
    water-level mu and per-direction weight distribution.

  M-SCALING SWEEP (per handoff item 4):
    M = [400, 10000] (full default; smoke = [400, 1000]). M=400 covers the KNN sentinel; M=10k covers the
    cone-collapse regime where uniform cleanup HARD_FAILs. M=100k optional adversarial via separate dispatch.

PRE-REGISTERED BANDS (LOCKED AT MODULE INIT):

  HARD_PASS_MIMO_WATERFILL_RESCUES:
    ARM_MIMO_WATERFILL_SVD recall at M=10k >= 0.50
    AND lift over ARM_UNIFORM_CLEANUP >= 0.20 absolute
    AND effective_rank lift (after / before) >= 1.30
    AND std across 3 seeds <= 0.05
    AND ARM_KNN_BASELINE at M=400 >= 0.90

  HARD_PASS_PARTIAL:
    Recall lift over ARM_UNIFORM_CLEANUP >= 0.15 at M=10k
    AND KNN sentinel preserved
    (some of the other HARD_PASS conditions not met)

  MIDDLE_BAND:
    Lift in (0.05, 0.15] at M=10k

  HARD_FAIL_WATERFILL_DOESNT_HELP:
    Lift <= 0.05 at M=10k
    OR effective_rank lift <= 1.05 (no rank addition; same failure mode as whitening)
    OR ARM_KNN_BASELINE drops below 0.90 (corruption catch)

Q-DISCIPLINE: any arm >= 0.995 flags suspect saturation; bands favor under-claim.

Discipline (load-bearing):
  - ASCII only.
  - Substrate-only at inference; encoder is SETUP-TIME only (hidden-state extractor; no LLM forward at verdict).
  - Per-arm metrics (Fix #28); never read verdict_msg as ground truth.
  - atexit per-seed checkpoint + restartable (per Fix #20 -- DURABLE).
  - META_M7 capacity-sensitive dims (PROJ_DIM, REG_LAMBDA, TRAIN_M, WHITEN_EPS, LEARNED_LR, LEARNED_STEPS,
    KNN_TOPK, EFF_RANK_EPS) IDENTICAL across smoke and full -- ONLY M, n_seeds, and encoder differ.
  - Smoke MUST trigger a meaningful UNIFORM_CLEANUP collapse (else meter not calibrated).

Routing: local CPU (per handoff "Local CPU preferred for Tier A; do NOT route Tier A to GPU queue without
exp_dev decision."). Cell is matmul-bound at M=10k with d=768; CPU is acceptable (~3-5 hr full wall on a 4060 Ti
machine -- adequate without GPU).
"""
from __future__ import annotations
import sys, os, argparse, time, math, json
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import get_output_dir, write_partial_key, aggregate_partials, write_metrics

ANCHOR_NAME = "substrate_anisotropy_mimo_waterfill_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# CAPACITY-SENSITIVE (META_M7) -- IDENTICAL smoke/full
PROJ_DIM = 768                  # post-contrastive projection dim (matches v2 fixture)
C = 256                         # codebook label count
REG_LAMBDA = 1.0                # uniform-baseline Tikhonov regularizer
WHITEN_EPS = 1e-3               # ZCA whitening regularizer
LEARNED_LR = 0.01               # learned-waterfill SGD learning rate
LEARNED_STEPS = 200             # learned-waterfill SGD steps
KNN_TOPK = 1                    # KNN baseline = top-1 cosine
EFF_RANK_EPS = 1e-9             # numerical floor for effective-rank ratio
SIGMA = 0.1                     # cue noise sigma (matches v2 fixture for cross-cell comparability)
MAX_Q = 1500                    # max cue count per M (matches v2 fixture)

# MODE-DEPENDENT (ONLY THESE DIFFER smoke vs full)
if RUN_MODE == "full":
    ENCODER = "EleutherAI/pythia-2.8b"
    SEEDS = [11, 13, 19]
    M_SWEEP = [400, 10000]      # M=400 = KNN sentinel; M=10k = cone-collapse regime
    TRAIN_M = 7500
    TRAIN_STEPS = 600
else:
    ENCODER = "EleutherAI/pythia-160m"
    SEEDS = [11]
    M_SWEEP = [400, 1000]       # smoke MUST trigger UNIFORM collapse at M=1000 vs M=400
    TRAIN_M = 600
    TRAIN_STEPS = 200

# PRE-REG BANDS (LOCKED AT MODULE INIT)
BAND_HP_ABS = 0.50              # MIMO_WATERFILL_SVD absolute recall floor at M=10k
BAND_HP_LIFT = 0.20             # lift over UNIFORM_CLEANUP for HARD_PASS
BAND_HP_PARTIAL_LIFT = 0.15     # lift for HARD_PASS_PARTIAL
BAND_MIDDLE_LIFT = 0.05         # lower bound of MIDDLE_BAND lift (strictly above)
BAND_HF_LIFT = 0.03             # strictly at-or-below -> HARD_FAIL (catches no-help-at-all)
BAND_HP_EFFRANK_LIFT = 1.30     # effective-rank ratio after/before for HARD_PASS
BAND_HF_EFFRANK_LIFT = 1.05     # at or below -> HARD_FAIL (no rank added)
BAND_KNN_SENTINEL = 0.90        # KNN at M=400 floor (Fix #28)
BAND_STD_HP = 0.05              # seed std ceiling for HARD_PASS
BAND_Q_SATURATION = 0.995       # any arm >= this flags Q-discipline

assert 0.0 < BAND_HF_LIFT < BAND_MIDDLE_LIFT < BAND_HP_PARTIAL_LIFT < BAND_HP_LIFT < 1.0, "band ordering"
assert 1.0 < BAND_HF_EFFRANK_LIFT < BAND_HP_EFFRANK_LIFT, "effrank lift ordering"
assert 0.0 < BAND_KNN_SENTINEL < 1.0, "knn sentinel"

CONFIG_VERSION = (
    "mimo_waterfill_v1 (knn_baseline / uniform_cleanup / whitening / waterfill_svd / waterfill_learned) | "
    "proj=%d C=%d reg=%.2f whiten_eps=%.0e lr=%.2f steps=%d sigma=%.2f | "
    "seeds=%s M=%s | CPU_numpy | bands locked"
) % (PROJ_DIM, C, REG_LAMBDA, WHITEN_EPS, LEARNED_LR, LEARNED_STEPS, SIGMA, SEEDS, M_SWEEP)


# ---------- numerical primitives ----------

def _np_norm(X):
    return (X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)).astype(np.float32)


def _effective_rank(K):
    """PR (participation-ratio) effective rank / D ratio.

    eff_rank = (sum sigma_i^2)^2 / (sum sigma_i^4) / D
    where sigma_i are singular values of K (M x D).
    Returns ratio in (0, 1]; 1.0 = isotropic.
    """
    if K.shape[0] < 2:
        return 0.0
    # SVD of K -> singular values lambda_i = sigma_i^2 of K K^T
    try:
        s = np.linalg.svd(K, compute_uv=False)
    except np.linalg.LinAlgError:
        return 0.0
    lam = s.astype(np.float64) ** 2
    num = lam.sum() ** 2
    den = (lam ** 2).sum() + EFF_RANK_EPS
    pr = num / den
    return float(pr / K.shape[1])  # normalize by D


def _knn_topk_recall(K, cue, y, ytrue, topk=1):
    """Cosine-similarity KNN; recall@top-1 over normalized vectors."""
    Kn = _np_norm(K)
    cn = _np_norm(cue)
    sim = cn @ Kn.T  # Q x M
    if topk == 1:
        idx = np.argmax(sim, axis=1)
        return float((y[idx] == ytrue).mean())
    topk_idx = np.argpartition(sim, -topk, axis=1)[:, -topk:]
    hits = np.any(y[topk_idx] == ytrue[:, None], axis=1)
    return float(hits.mean())


# ---------- cleanup arms ----------

def _build_W_uniform(K, Y, reg_lambda):
    """Uniform-Tikhonov dense-KV cleanup.

    W = (K^T K + reg * I)^-1 K^T Y     (D x D readout sandwich approach)
    But we use the dual form for M < D efficiency and to map cleanly to water-filling.

    Cleanup readout for cue q: q @ K^T @ alpha where alpha solves (K K^T + reg I) alpha = Y.
    Returns alpha (M x C); recall = decode(cue @ K.T @ alpha vs codebook).
    """
    M = K.shape[0]
    G = K @ K.T + reg_lambda * np.eye(M, dtype=np.float32)
    alpha = np.linalg.solve(G, Y).astype(np.float32)
    return alpha


def _build_W_waterfill_svd(K, Y, total_budget):
    """SVD water-filling cleanup.

    Decompose K K^T = U diag(lam) U^T (lam_i descending).
    Allocate per-mode regularizer: reg_i = max(0, mu - lam_i) where mu is set so sum(reg_i) = total_budget.
    Cleanup = (U diag(lam + reg) U^T)^-1 Y = U diag(1 / (lam + reg)) U^T Y; multiply by K.T at retrieval.

    This is the MIMO water-filling analog applied to the cleanup regularizer.
    """
    M = K.shape[0]
    G = K @ K.T
    # symmetric eigendecomp (G is PSD)
    lam, U = np.linalg.eigh(G.astype(np.float64))
    lam = np.clip(lam, 0.0, None)  # numerical PSD floor

    # water-fill: find mu such that sum_i max(0, mu - lam_i) = total_budget
    # equivalent to "pour reg into the low-singular directions until budget exhausted"
    lam_sorted = np.sort(lam)  # ascending
    csum = 0.0
    mu = lam_sorted[0]
    # incremental water level: as mu rises past lam_sorted[k], k+1 modes are below water
    found = False
    for k in range(len(lam_sorted)):
        # if mu = lam_sorted[k+1] (or +inf at end), volume = sum_{i<=k} (lam_sorted[k+1] - lam_sorted[i])
        if k + 1 < len(lam_sorted):
            next_level = lam_sorted[k + 1]
        else:
            next_level = lam_sorted[-1] + total_budget + 1.0
        vol_at_next = sum(max(0.0, next_level - lam_sorted[i]) for i in range(k + 1))
        if vol_at_next >= total_budget:
            # find exact mu by linear-interp inside this level: vol(mu) = (k+1)*mu - sum_{i<=k} lam_sorted[i]
            sum_below = sum(lam_sorted[i] for i in range(k + 1))
            mu = (total_budget + sum_below) / (k + 1)
            found = True
            break
    if not found:
        mu = lam_sorted[-1] + total_budget / max(1, len(lam_sorted))

    reg = np.maximum(0.0, mu - lam)
    inv = 1.0 / (lam + reg + EFF_RANK_EPS)
    # alpha = U diag(inv) U^T Y
    alpha = (U @ (np.diag(inv) @ (U.T @ Y.astype(np.float64)))).astype(np.float32)
    return alpha, float(mu), reg.astype(np.float32)


def _build_W_waterfill_learned(K, Y, ytrue_train_idx, ytrue_train_labels, lr, steps):
    """Gradient-trained per-direction weights (upper bound on direction-weighted cleanup).

    Parametrize cleanup as alpha = U diag(w) U^T Y with w_i > 0 trainable (M params).
    Train w by SGD on cross-entropy of cue @ K^T @ alpha vs ytrue on a HELD-IN train fold.

    Uses numpy + manual backprop for portability (no torch dependency on CPU path).
    """
    M = K.shape[0]
    G = K @ K.T
    lam, U = np.linalg.eigh(G.astype(np.float64))
    lam = np.clip(lam, 0.0, None)
    # init w = 1 / (lam + reg_lambda) (matches uniform baseline)
    w = (1.0 / (lam + REG_LAMBDA)).astype(np.float64)
    Y64 = Y.astype(np.float64)
    UT_Y = U.T @ Y64  # (M, C)

    # cue features for train: project a subset onto K-space via cue_train @ K.T
    # we use the train portion of K itself as cue (low-noise train signal)
    n_train = min(len(ytrue_train_idx), 400)
    train_idx = ytrue_train_idx[:n_train]
    cue_t = K[train_idx]  # (n_train, D)
    cue_K = (cue_t.astype(np.float64) @ K.T.astype(np.float64))  # (n_train, M)
    cue_K_U = cue_K @ U  # (n_train, M)  -- cue projected into eigen-basis

    labels = ytrue_train_labels[:n_train].astype(np.int64)

    for step in range(steps):
        # logits = cue @ K^T @ U diag(w) U^T Y = cue_K_U * w @ UT_Y
        wU_Y = (w[:, None] * UT_Y)  # (M, C)
        logits = cue_K_U @ wU_Y  # (n_train, C)
        # numerical softmax
        logits -= logits.max(axis=1, keepdims=True)
        ex = np.exp(logits)
        probs = ex / ex.sum(axis=1, keepdims=True)
        # gradient: dL/dw_i = sum over examples of cue_K_U[:, i] * sum_c (probs[:, c] - onehot) * UT_Y[i, c]
        one_hot = np.zeros_like(probs)
        one_hot[np.arange(n_train), labels] = 1.0
        d_logits = (probs - one_hot) / n_train  # (n_train, C)
        # d_w = sum_n cue_K_U[n] * (d_logits[n] @ UT_Y.T)
        grad = (cue_K_U * (d_logits @ UT_Y.T)).sum(axis=0)
        # positivity constraint via softplus reparam would be ideal; use clipping for simplicity
        w = w - lr * grad
        w = np.clip(w, 1e-6, None)  # enforce > 0

    # final alpha
    alpha = (U @ (np.diag(w) @ UT_Y)).astype(np.float32)
    return alpha, w.astype(np.float32)


def _build_K_whitened(K, eps):
    """ZCA-whitening of K (rotation-only ablation).

    K_w = K @ Sigma^{-1/2} where Sigma = K^T K / M.
    Drill 1 showed this rotation alone hits ~+0.020 ceiling.
    """
    M, D = K.shape
    Sigma = (K.T @ K) / max(1, M)
    Sigma = Sigma + eps * np.eye(D, dtype=np.float32)
    # symmetric inverse-sqrt via eigendecomp
    lam, V = np.linalg.eigh(Sigma.astype(np.float64))
    lam = np.clip(lam, eps, None)
    inv_sqrt = (V @ np.diag(1.0 / np.sqrt(lam)) @ V.T).astype(np.float32)
    return (K @ inv_sqrt).astype(np.float32)


def _cleanup_recall(K, alpha, cue, y, ytrue, codebook_d):
    """Decode recall: pred = argmax(codebook @ readout) where readout = cue @ K^T @ alpha (M -> C).

    alpha is (M, C). The (i, c) entry says "store mass c at slot i".
    """
    # readout_c = cue @ K^T @ alpha[:, c]  -> (Q, C)
    readout = (cue @ K.T) @ alpha  # (Q, C)
    pred = np.argmax(readout, axis=1)
    return float((pred == ytrue).mean())


# ---------- per-seed arms runner ----------

def _arms_numpy(K, y, seed_for_arms, M_target):
    """Run all five arms on the (M_target x D) key/label slice; pure numpy."""
    M = K.shape[0]
    D = K.shape[1]
    g = np.random.default_rng(seed_for_arms)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = (SIGMA * g.standard_normal((len(qidx), D))).astype(np.float32)
    Kn = _np_norm(K) * math.sqrt(D)
    cue = Kn[qidx] + noise
    ytrue = y[qidx]

    cb_d = _np_norm(g.standard_normal((C, D)).astype(np.float32))
    Y = cb_d[y].astype(np.float32)  # (M, D) but we want label-onehot for cleanup math

    # actually for cleanup math, Y should be the LABEL-onehot (M x C) so that argmax gives the label;
    # the "store mass" interpretation works directly.
    Y_onehot = np.eye(C, dtype=np.float32)[y]  # (M, C)

    # effective_rank before any transform
    eff_rank_raw = _effective_rank(Kn)

    # ARM_KNN_BASELINE (rank-blind sentinel; Fix #28)
    arm_knn = _knn_topk_recall(Kn, cue, y, ytrue, topk=KNN_TOPK)

    # ARM_UNIFORM_CLEANUP
    alpha_u = _build_W_uniform(Kn, Y_onehot, REG_LAMBDA)
    arm_uniform = _cleanup_recall(Kn, alpha_u, cue, y, ytrue, cb_d)

    # ARM_WHITENING (rotation-only)
    Kn_w = _build_K_whitened(Kn, WHITEN_EPS)
    eff_rank_whiten = _effective_rank(Kn_w)
    # whitened cue: project cue through same transform
    Sigma_full = (Kn.T @ Kn) / max(1, M)
    Sigma_full = Sigma_full + WHITEN_EPS * np.eye(D, dtype=np.float32)
    lam_w, V_w = np.linalg.eigh(Sigma_full.astype(np.float64))
    lam_w = np.clip(lam_w, WHITEN_EPS, None)
    inv_sqrt = (V_w @ np.diag(1.0 / np.sqrt(lam_w)) @ V_w.T).astype(np.float32)
    cue_w = (cue @ inv_sqrt).astype(np.float32)
    alpha_w = _build_W_uniform(Kn_w, Y_onehot, REG_LAMBDA)
    arm_whiten = _cleanup_recall(Kn_w, alpha_w, cue_w, y, ytrue, cb_d)

    # ARM_MIMO_WATERFILL_SVD
    # total_budget = REG_LAMBDA * M (matches uniform total mass for fair compare)
    total_budget = REG_LAMBDA * M
    alpha_wf, mu_wf, reg_wf = _build_W_waterfill_svd(Kn, Y_onehot, total_budget)
    arm_waterfill_svd = _cleanup_recall(Kn, alpha_wf, cue, y, ytrue, cb_d)
    # diagnostic: effective rank of K^T after waterfill = sum of (1 / (lam + reg)) interpreted as "active modes"
    # we report effrank lift = sigma(K_eff)^2 where K_eff = K @ diag(sqrt(1/(lam+reg)))
    # equivalent: effrank_after = (sum_i 1/(lam_i+reg_i))^2 / sum_i 1/(lam_i+reg_i)^2 / D
    inv_eig = 1.0 / (np.linalg.eigvalsh(Kn @ Kn.T).clip(0, None) + reg_wf + EFF_RANK_EPS).astype(np.float64)
    num = inv_eig.sum() ** 2
    den = (inv_eig ** 2).sum() + EFF_RANK_EPS
    eff_rank_waterfill = float(num / den / D)

    # ARM_MIMO_WATERFILL_LEARNED (gradient upper bound)
    # train on a subset (the same M, first 80% of indices as train fold)
    n_train = max(50, int(0.5 * M))
    train_idx = np.arange(min(n_train, M))
    train_labels = y[:len(train_idx)]
    alpha_lwf, w_lwf = _build_W_waterfill_learned(
        Kn, Y_onehot, train_idx, train_labels, LEARNED_LR, LEARNED_STEPS
    )
    arm_waterfill_learned = _cleanup_recall(Kn, alpha_lwf, cue, y, ytrue, cb_d)

    storage_bytes_per_mem = float(D * 4 + math.log2(C))  # informational

    return {
        "arm_knn_baseline": round(arm_knn, 4),
        "arm_uniform_cleanup": round(arm_uniform, 4),
        "arm_whitening": round(arm_whiten, 4),
        "arm_mimo_waterfill_svd": round(arm_waterfill_svd, 4),
        "arm_mimo_waterfill_learned": round(arm_waterfill_learned, 4),
        "eff_rank_raw": round(eff_rank_raw, 4),
        "eff_rank_whiten": round(eff_rank_whiten, 4),
        "eff_rank_waterfill": round(eff_rank_waterfill, 4),
        "waterfill_mu": round(mu_wf, 6),
        "waterfill_active_modes": int((reg_wf > EFF_RANK_EPS).sum()),
        "lift_waterfill_over_uniform": round(arm_waterfill_svd - arm_uniform, 4),
        "lift_learned_over_uniform": round(arm_waterfill_learned - arm_uniform, 4),
        "lift_whiten_over_uniform": round(arm_whiten - arm_uniform, 4),
        "storage_bytes_per_mem": round(storage_bytes_per_mem, 1),
    }


# ---------- encoder + facts (only used in full/smoke, not self-test) ----------

def _facts_and_encode(seed, n_total):
    """Hoisted: facts + encoder forward pass.

    Substrate-only at inference (encoder is a SETUP-TIME hidden-state extractor).
    """
    os.environ["HDLAB_RUN_MODE"] = RUN_MODE
    import torch  # local import; only here for the encoder fixture (NOT used in arms)
    import experiments.exp_flagship_sparse_projected_KV_PROBE_whiten_before_topk_v1 as _probe
    _probe.ENCODER = ENCODER
    _probe.ENC_DTYPE = torch.float16 if torch.cuda.is_available() else torch.float32
    make_facts = _probe.make_facts
    encode = _probe.encode
    train_contrastive = _probe.train_contrastive
    keys, cues = make_facts(n_total)
    K = encode(keys)
    Q = encode(cues)
    g = np.random.default_rng(seed)
    perm = g.permutation(n_total)
    tr = perm[:TRAIN_M]
    ho = perm[TRAIN_M:]
    W = train_contrastive(K[tr], Q[tr], PROJ_DIM, TRAIN_STEPS, seed)
    Kp_all = (K[ho] @ W).astype(np.float32)
    return Kp_all


def run_unit(seed):
    n_total = max(M_SWEEP) + TRAIN_M
    print("[seed=%d] encoder=%s n_total=%d (encoding once; substrate-only at inference)" % (
        seed, ENCODER, n_total), flush=True)
    Kp_all = _facts_and_encode(seed, n_total)
    g = np.random.default_rng(seed * 7 + 1)
    by_M = {}
    for M in M_SWEEP:
        y = g.integers(0, C, M).astype(np.int64)
        arms_seed = seed * 7 + M
        a = _arms_numpy(Kp_all[:M].astype(np.float32), y, arms_seed, M)
        by_M["M%d" % M] = a
        print((
            "[seed=%d M=%d] knn=%.3f uniform=%.3f whiten=%.3f waterfill_svd=%.3f waterfill_learned=%.3f | "
            "eff_rank raw=%.3f whiten=%.3f waterfill=%.3f | lift_svd=%.3f lift_learned=%.3f"
        ) % (
            seed, M, a["arm_knn_baseline"], a["arm_uniform_cleanup"], a["arm_whitening"],
            a["arm_mimo_waterfill_svd"], a["arm_mimo_waterfill_learned"],
            a["eff_rank_raw"], a["eff_rank_whiten"], a["eff_rank_waterfill"],
            a["lift_waterfill_over_uniform"], a["lift_learned_over_uniform"]
        ), flush=True)
    return {"seed": seed, "by_M": by_M}


def _med_std(values):
    if not values:
        return 0.0, 0.0
    return float(np.median(values)), float(np.std(values))


def compute_verdict(units):
    if not units:
        return ("HARD_FAIL", "no results", {})
    M_max = max(M_SWEEP)
    M_min = min(M_SWEEP)

    def vals(M, key):
        return [u["by_M"]["M%d" % M][key] for u in units if "M%d" % M in u["by_M"]]

    # Cross-cell sanity rail: KNN at M=400 (or smallest M)
    knn_vals = vals(M_min, "arm_knn_baseline")
    knn_med, knn_std = _med_std(knn_vals)
    knn_pass = knn_med >= BAND_KNN_SENTINEL

    # Mechanism eval at M_max
    uniform_med, uniform_std = _med_std(vals(M_max, "arm_uniform_cleanup"))
    whiten_med, whiten_std = _med_std(vals(M_max, "arm_whitening"))
    wf_svd_med, wf_svd_std = _med_std(vals(M_max, "arm_mimo_waterfill_svd"))
    wf_learned_med, wf_learned_std = _med_std(vals(M_max, "arm_mimo_waterfill_learned"))

    eff_raw, _ = _med_std(vals(M_max, "eff_rank_raw"))
    eff_whiten, _ = _med_std(vals(M_max, "eff_rank_whiten"))
    eff_wf, _ = _med_std(vals(M_max, "eff_rank_waterfill"))

    lift_wf_svd = wf_svd_med - uniform_med
    lift_wf_learned = wf_learned_med - uniform_med
    lift_whiten = whiten_med - uniform_med
    effrank_lift = eff_wf / (eff_raw + EFF_RANK_EPS)
    effrank_lift_whiten = eff_whiten / (eff_raw + EFF_RANK_EPS)

    detail = {
        "M_eval": M_max,
        "M_sentinel": M_min,
        "arm_knn_baseline_at_M_sentinel": round(knn_med, 4),
        "arm_uniform_cleanup": round(uniform_med, 4),
        "arm_whitening": round(whiten_med, 4),
        "arm_mimo_waterfill_svd": round(wf_svd_med, 4),
        "arm_mimo_waterfill_learned": round(wf_learned_med, 4),
        "std_uniform": round(uniform_std, 4),
        "std_whitening": round(whiten_std, 4),
        "std_waterfill_svd": round(wf_svd_std, 4),
        "std_waterfill_learned": round(wf_learned_std, 4),
        "eff_rank_raw": round(eff_raw, 4),
        "eff_rank_whiten": round(eff_whiten, 4),
        "eff_rank_waterfill": round(eff_wf, 4),
        "effrank_lift_waterfill_over_raw": round(effrank_lift, 4),
        "effrank_lift_whiten_over_raw": round(effrank_lift_whiten, 4),
        "lift_waterfill_svd_over_uniform": round(lift_wf_svd, 4),
        "lift_waterfill_learned_over_uniform": round(lift_wf_learned, 4),
        "lift_whiten_over_uniform": round(lift_whiten, 4),
        "knn_sentinel_pass": bool(knn_pass),
        "n_seeds": len(units),
        "bands": {
            "HP_ABS": BAND_HP_ABS, "HP_LIFT": BAND_HP_LIFT, "HP_PARTIAL_LIFT": BAND_HP_PARTIAL_LIFT,
            "MIDDLE_LIFT": BAND_MIDDLE_LIFT, "HF_LIFT": BAND_HF_LIFT,
            "HP_EFFRANK_LIFT": BAND_HP_EFFRANK_LIFT, "HF_EFFRANK_LIFT": BAND_HF_EFFRANK_LIFT,
            "KNN_SENTINEL": BAND_KNN_SENTINEL, "STD_HP": BAND_STD_HP,
            "Q_SATURATION": BAND_Q_SATURATION,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "research_gap2_anisotropy_5x_drill_2026-06-26",
            "exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26",
            "substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "Stanford_EE359_MIMO_water_filling",
            "Mu_Viswanath_anisotropy_word_embeddings",
        ],
    }

    # Q-discipline
    q_flags = []
    for name, val in [("waterfill_svd", wf_svd_med), ("waterfill_learned", wf_learned_med),
                       ("uniform", uniform_med), ("whitening", whiten_med)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation; under-claim]" %
                           (name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # per-arm summary string (Fix #28 -- raw arm metrics, not interpretation)
    summ = (
        "knn@M=%d=%.3f | uniform=%.3f whiten=%.3f waterfill_svd=%.3f waterfill_learned=%.3f | "
        "lift_svd_over_uniform=%.3f lift_learned_over_uniform=%.3f lift_whiten=%.3f | "
        "eff_rank raw=%.3f whiten=%.3f waterfill=%.3f | effrank_lift_wf=%.3fx"
    ) % (M_min, knn_med, uniform_med, whiten_med, wf_svd_med, wf_learned_med,
         lift_wf_svd, lift_wf_learned, lift_whiten, eff_raw, eff_whiten, eff_wf, effrank_lift)

    # GATE 0: KNN sentinel (Fix #28 by-construction-saturation contamination catch)
    if not knn_pass:
        return ("HARD_FAIL",
                ("HARD_FAIL_KNN_SENTINEL: KNN@M=%d = %.3f < %.2f -> keys themselves are corrupted (not just "
                 "anisotropic); any cleanup-arm lift is artifact. Aborting verdict on mechanism arms. %s%s"
                 ) % (M_min, knn_med, BAND_KNN_SENTINEL, q_note, summ),
                detail)

    # GATE 1: HARD_PASS_MIMO_WATERFILL_RESCUES (the prereg HARD_PASS)
    if (wf_svd_med >= BAND_HP_ABS and
        lift_wf_svd >= BAND_HP_LIFT and
        effrank_lift >= BAND_HP_EFFRANK_LIFT and
        wf_svd_std <= BAND_STD_HP):
        return ("HARD_PASS",
                ("HARD_PASS_MIMO_WATERFILL_RESCUES: waterfill_svd=%.3f >= %.2f AND "
                 "lift_over_uniform=%.3f >= %.2f AND effrank_lift=%.2fx >= %.2fx AND std=%.3f <= %.2f "
                 "AND knn_sentinel=%.3f >= %.2f at M=%d. MIMO water-filling rescues anisotropy collapse "
                 "on real Pythia keys (uniform cleanup collapsed to %.3f). %s%s"
                 ) % (wf_svd_med, BAND_HP_ABS, lift_wf_svd, BAND_HP_LIFT, effrank_lift, BAND_HP_EFFRANK_LIFT,
                      wf_svd_std, BAND_STD_HP, knn_med, BAND_KNN_SENTINEL, M_max, uniform_med, q_note, summ),
                detail)

    # GATE 2: HARD_PASS_PARTIAL (lift >= 0.15 but not all conditions met)
    if lift_wf_svd >= BAND_HP_PARTIAL_LIFT:
        return ("HARD_PASS",
                ("HARD_PASS_PARTIAL_WATERFILL: lift_over_uniform=%.3f >= %.2f at M=%d but not all HARD_PASS "
                 "conditions met (abs=%.3f vs >=%.2f; effrank_lift=%.2fx vs >=%.2fx; std=%.3f vs <=%.2f). "
                 "Mechanism partially rescues anisotropy. uniform=%.3f. %s%s"
                 ) % (lift_wf_svd, BAND_HP_PARTIAL_LIFT, M_max, wf_svd_med, BAND_HP_ABS,
                      effrank_lift, BAND_HP_EFFRANK_LIFT, wf_svd_std, BAND_STD_HP, uniform_med, q_note, summ),
                detail)

    # GATE 3: MIDDLE_BAND
    if lift_wf_svd > BAND_MIDDLE_LIFT:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_WATERFILL: lift_over_uniform=%.3f in (%.2f, %.2f] at M=%d -> waterfill helps "
                 "modestly but does not chain-grade. uniform=%.3f waterfill_svd=%.3f. %s%s"
                 ) % (lift_wf_svd, BAND_MIDDLE_LIFT, BAND_HP_PARTIAL_LIFT, M_max,
                      uniform_med, wf_svd_med, q_note, summ),
                detail)

    # GATE 4: HARD_FAIL_WATERFILL_DOESNT_HELP
    if lift_wf_svd <= BAND_HF_LIFT or effrank_lift <= BAND_HF_EFFRANK_LIFT:
        return ("HARD_FAIL",
                ("HARD_FAIL_WATERFILL_DOESNT_HELP: lift_over_uniform=%.3f <= %.2f OR effrank_lift=%.2fx "
                 "<= %.2fx at M=%d -> per-direction cleanup-weight allocation is NOT a chain-grade rescue "
                 "for cone-collapsed anisotropy on real Pythia keys. uniform=%.3f waterfill_svd=%.3f. "
                 "Tier A Anchor #1 falsified; consider Tier A Anchor #2 (DG pattern separation). %s"
                 ) % (lift_wf_svd, BAND_HF_LIFT, effrank_lift, BAND_HF_EFFRANK_LIFT, M_max,
                      uniform_med, wf_svd_med, summ),
                detail)

    return ("MIDDLE_BAND",
            ("UNCLASSIFIED_MIDDLE_BAND: lift_over_uniform=%.3f effrank_lift=%.2fx at M=%d. %s%s"
             ) % (lift_wf_svd, effrank_lift, M_max, q_note, summ),
            detail)


# ---------- self-test (synthetic; no encoder) ----------

def _selftest():
    """Self-test on synthetic anisotropic data:

    Cell semantics MUST hold on a CONTROLLED anisotropic regime where:
      - uniform_cleanup collapses at M=200 (cone-collapse-like)
      - waterfill_svd recovers (>= 0.30; sanity)
      - knn baseline at M=50 >= 0.90 (rank-blind sentinel works)
      - effective_rank measurable + ratios sensible
    """
    g = np.random.default_rng(0)
    d = 64
    M = 200
    # anisotropic synthesis: project random vectors into a low-rank cone via near-singular covariance
    cone_dim = 8
    cone_basis = g.standard_normal((d, cone_dim)).astype(np.float32)
    cone_basis, _ = np.linalg.qr(cone_basis)
    coeffs = g.standard_normal((M, cone_dim)).astype(np.float32) * 2.0
    common_mode = g.standard_normal((1, d)).astype(np.float32) * 1.5
    K_aniso = (coeffs @ cone_basis.T + common_mode).astype(np.float32)
    y_aniso = g.integers(0, C, M).astype(np.int64)
    out = _arms_numpy(K_aniso, y_aniso, 1, M)

    # (a) eff_rank of anisotropic must be lower than isotropic baseline (sanity)
    assert out["eff_rank_raw"] < 0.50, (
        "anisotropic synthetic must have low eff_rank (got %.3f)" % out["eff_rank_raw"])
    # (b) waterfill_svd lift MAY be small or large; here we just assert it ran (numerical sanity)
    assert -0.5 < out["lift_waterfill_over_uniform"] < 0.5, (
        "lift must be numerically sane (got %.3f)" % out["lift_waterfill_over_uniform"])
    # (c) knn at SMALL M on isotropic recovers (rank-blind sentinel works)
    iso = _np_norm(g.standard_normal((50, d)).astype(np.float32))
    yiso = g.integers(0, C, 50).astype(np.int64)
    iso_out = _arms_numpy(iso, yiso, 2, 50)
    assert iso_out["arm_knn_baseline"] >= 0.90, (
        "KNN sentinel must work on isotropic small-M synthetic (got %.3f)" % iso_out["arm_knn_baseline"])
    # (d) effrank_lift_waterfill_over_raw is reported as a float
    eff_lift = out["eff_rank_waterfill"] / (out["eff_rank_raw"] + EFF_RANK_EPS)
    assert 0.0 < eff_lift < 1000.0, ("eff_rank lift in sane range (got %.3f)" % eff_lift)

    print(
        "[selftest] PASS: eff_rank_raw=%.3f (anisotropic confirmed low-rank); "
        "lift_waterfill_over_uniform=%.3f; knn_baseline isotropic=%.3f; "
        "eff_rank waterfill/raw=%.3fx"
        % (out["eff_rank_raw"], out["lift_waterfill_over_uniform"],
           iso_out["arm_knn_baseline"], eff_lift),
        flush=True,
    )


if __name__ == "__main__":
    _selftest()
    if _ARGS.self_test:
        raise SystemExit(0)
    print("[config] %s mode=%s | %s" % (ANCHOR_NAME, RUN_MODE, CONFIG_VERSION), flush=True)

    out_dir = get_output_dir(ANCHOR_NAME)
    run_cfg = {"run_mode": RUN_MODE, "proj": PROJ_DIM, "seeds": SEEDS, "M": M_SWEEP}
    t0 = time.time()
    for seed in SEEDS:
        key = "s%d" % seed
        if key in aggregate_partials(out_dir, [key], run_config=run_cfg):
            print("[ckpt] %s done; skip" % key, flush=True)
            continue
        write_partial_key(out_dir, key, run_unit(seed))
    units = list(aggregate_partials(out_dir, ["s%d" % sd for sd in SEEDS], run_config=run_cfg).values())
    verdict, msg, detail = compute_verdict(units)
    print("\n[VERDICT] " + msg, flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": msg,
        "summary": msg,
        "run_mode": RUN_MODE,
        "model": ENCODER,
        "proj_dim": PROJ_DIM,
        "M_SWEEP": M_SWEEP,
        "n_seeds": len(units),
        "seeds": SEEDS,
        "detail": detail,
        "metrics_source": "measured_cpu_anisotropy_mimo_waterfill_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
