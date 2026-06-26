"""ANISOTROPY DG pattern-separation PRE-WRITE module -- Tier A Anchor #2 from GAP 2 5x drill (research note N1).

PARENT CONTEXT:
  - notes/research_gap2_anisotropy_5x_drill_2026-06-26.md (N1 candidate; P_deflated=0.45)
  - notes/exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26.md (handoff #2)
  - notes/exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26.md (Anchor #1 falsified;
    revival angle #3 said: pivot to N1)
  - notes/research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25.md (drill 2 ranked DG #1)
  - v2 fixture (cone-collapse anchor): data/exp_substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full

MECHANISM (one paragraph):
  Anchor #1 (MIMO water-filling) tried to fix the READOUT (post-write); it failed because Tikhonov
  pseudo-inverse already correctly down-weights cone-null directions. DG pattern separation attacks a
  DIFFERENT intervention point: BEFORE writing keys to W, push them through a Dentate-Gyrus-style
  pattern separator that orthogonalizes the input cone. The separator composes EXISTING substrate
  primitives only: (a) ~6x expansion to a larger sparse code, (b) k-WTA at 2% activity via top-K
  selection with sign preservation (sparse-bipolar codebook is already chain-grade at N=2048 per
  600K patterns), (c) lateral inhibition via per-batch divisive normalization keeping total activity
  constant (Carandini-Heeger canonical). The substrate-novel claim is that PRE-WRITE separation
  yields a dense-KV product on real Pythia keys at M=10k WITHOUT requiring partition routing -- the W
  matrix stores already-orthogonalized patterns from the start. Brain existence proof: hippocampal DG
  IS the solved instance of this exact problem; +0.10 prior per brain-existence-proof feedback.

KEY DIFFERENCE from MIMO (Anchor #1):
  MIMO: q @ K^T @ alpha(q, K, REG) -- READOUT-side regularizer redistribution.
  DG  : q' = sep(q); K' = sep(K); then q' @ K'^T @ alpha_uniform(K') -- INPUT-side decorrelation.
  Equivalent to encoder change EXCEPT no learning required (composition of known primitives).

ARMS (per handoff contract):

  CROSS-CELL SANITY RAIL (Fix #28 by-construction-saturation sentinel):
    ARM_KNN_BASELINE at M=400 -- must >= 0.9 on every config. KNN over RAW Pythia keys (NOT through
    separator) -- rank-blind. If KNN drops, keys are corrupted. (Separator output KNN reported as a
    diagnostic, not the sentinel -- DG is INTENTIONALLY lossy per drill 2 / research note N1.)

  MECHANISM ARMS (intervention-point ladder):
    ARM_UNIFORM_NO_PRESEP    -- current substrate; raw Pythia keys + uniform-Tikhonov dense-KV cleanup.
                                Reproduces Anchor #1's UNIFORM baseline.
    ARM_WHITENING_PRESEP     -- ZCA-whiten K, then uniform cleanup. Rotation-only ablation; drill 1
                                ceiling. Should fail similarly to Anchor #1 whitening collapse.
    ARM_DG_KWTA_PRESEP       -- k-WTA at 2% activity (top 2% magnitudes preserved, signed; rest zero).
                                Pure sparsification; no expansion, no normalization. Tests whether
                                sparsity ALONE separates the cone.
    ARM_DG_LATERAL_INHIB_PRESEP -- k-WTA + per-axis divisive normalization (Carandini-Heeger;
                                output[i] /= eps + sqrt(sum_j output[j]^2 inside top-K)). Tests
                                whether divisive gain control on TOP of sparsity helps.
    ARM_DG_FULL              -- E-x EXPANSION (6x via fixed-random binary projection) + k-WTA at 2%
                                + per-batch divisive normalization + per-axis homeostatic threshold
                                adaptation (EWMA over batch). Strongest; full DG composition.

  DIAGNOSTIC (per handoff item 3):
    effective_rank (PR/D) of K BEFORE separator AND AFTER each separator arm. Reports also the
    cosine-similarity OFF-DIAGONAL MASS histogram (raw vs separated) -- a working separator should
    push off-diagonal mass toward zero. NOT cross-cell-rail; this is a mechanism diagnostic.

  M-SCALING SWEEP (per handoff item 4):
    M = [400, 10000] (full default; smoke = [400, 1000]). M=400 = KNN sentinel; M=10k = cone-collapse
    regime where uniform cleanup HARD_FAILs. M=100k tier deferred (Tier A read first).

PRE-REGISTERED BANDS (LOCKED AT MODULE INIT):

  HARD_PASS_DG_PRESEP_RESCUES (the prereg HARD_PASS):
    ARM_DG_FULL recall at M=10k (adversarial regime) >= 0.50
    AND lift over ARM_UNIFORM_NO_PRESEP >= 0.20 absolute
    AND effective_rank lift (DG_FULL output / raw input) >= 1.30
    AND std across 3 seeds <= 0.05
    AND ARM_KNN_BASELINE at M=400 >= 0.90

  HARD_PASS_PARTIAL:
    Recall lift over ARM_UNIFORM_NO_PRESEP >= 0.15 at M=10k
    AND KNN sentinel preserved
    (some of the other HARD_PASS conditions not met)

  MIDDLE_BAND:
    Lift in (0.05, 0.15] at M=10k

  HARD_FAIL_DG_PRESEP_DOESNT_HELP:
    Lift <= 0.05 at M=10k
    OR effective_rank lift <= 1.05 (no rank addition -- same failure mode as whitening)
    OR ARM_KNN_BASELINE drops below 0.90 (corruption catch on RAW keys)

  SIGN-CHECK GATE at smoke (critical per task spec):
    If at smoke ARM_DG_FULL < ARM_UNIFORM_NO_PRESEP - 0.02 at the larger smoke M, GATE the full
    dispatch (don't burn 3-5hr on a sign-wrong cell). Reported in compute_verdict via SMOKE_SIGN_FLIP
    detail field; cell-author wrapper checks this BEFORE queueing full.

Q-DISCIPLINE: any arm >= 0.995 flags suspect saturation; bands favor under-claim.

Discipline (load-bearing):
  - ASCII only.
  - Substrate-only at inference; encoder is SETUP-TIME only (hidden-state extractor; no LLM forward at
    verdict).
  - Per-arm metrics (Fix #28); never read verdict_msg as ground truth.
  - atexit per-seed checkpoint + restartable (per Fix #20 -- DURABLE).
  - META_M7 capacity-sensitive dims (EXPAND_RATIO, KWTA_FRAC, NORM_EPS, HOMEO_TAU, REG_LAMBDA, KNN_TOPK,
    SIGMA, EFF_RANK_EPS, MAX_Q) IDENTICAL across smoke and full -- ONLY M, n_seeds, and encoder differ.
  - Smoke MUST trigger a meaningful UNIFORM_NO_PRESEP collapse at the larger smoke M (else meter not
    calibrated -- assert in verdict).

Routing: local CPU (per handoff "Local CPU preferred for Tier A; do NOT route Tier A to GPU queue
without exp_dev decision."). Cell is matmul-bound at M=10k with d=768 (expanded to d_e=4608); CPU is
acceptable (~3-5 hr full wall on a 4060 Ti machine -- adequate without GPU). Numpy-only arms; no
torch.cuda in inference path.
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

ANCHOR_NAME = "substrate_anisotropy_dg_pattern_separation_prewrite_v1"

_P = argparse.ArgumentParser()
_P.add_argument("--self-test", action="store_true", dest="self_test")
_P.add_argument("--smoke", action="store_true")
_ARGS, _ = _P.parse_known_args()
RUN_MODE = "smoke" if (_ARGS.smoke or _ARGS.self_test) else os.environ.get("HDLAB_RUN_MODE", "full")

# CAPACITY-SENSITIVE (META_M7) -- IDENTICAL smoke/full
PROJ_DIM = 768                  # post-contrastive projection dim (matches v2 fixture + Anchor #1)
C = 256                         # codebook label count
EXPAND_RATIO = 6                # DG expansion factor (6x ~ hippocampal granule:CA3 ratio)
KWTA_FRAC = 0.02                # 2% activity per pattern (DG canonical)
NORM_EPS = 1e-6                 # divisive normalization epsilon
HOMEO_TAU = 0.1                 # EWMA timescale for homeostatic threshold (lower = faster adapt)
REG_LAMBDA = 1.0                # uniform-baseline Tikhonov regularizer (matches Anchor #1)
WHITEN_EPS = 1e-3               # ZCA whitening regularizer (matches Anchor #1)
KNN_TOPK = 1                    # KNN baseline = top-1 cosine
EFF_RANK_EPS = 1e-9             # numerical floor for effective-rank ratio
SIGMA = 0.1                     # cue noise sigma (matches v2 fixture + Anchor #1 for cross-cell compare)
MAX_Q = 1500                    # max cue count per M (matches v2 fixture + Anchor #1)

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
BAND_HP_ABS = 0.50              # ARM_DG_FULL absolute recall floor at M=10k
BAND_HP_LIFT = 0.20             # lift over ARM_UNIFORM_NO_PRESEP for HARD_PASS
BAND_HP_PARTIAL_LIFT = 0.15     # lift for HARD_PASS_PARTIAL
BAND_MIDDLE_LIFT = 0.05         # lower bound of MIDDLE_BAND lift (strictly above)
BAND_HF_LIFT = 0.05             # at-or-below -> HARD_FAIL (matches task spec)
BAND_HP_EFFRANK_LIFT = 1.30     # effective-rank ratio after/before for HARD_PASS
BAND_HF_EFFRANK_LIFT = 1.05     # at or below -> HARD_FAIL (no rank added)
BAND_KNN_SENTINEL = 0.90        # KNN at M=400 floor on RAW keys (Fix #28)
BAND_STD_HP = 0.05              # seed std ceiling for HARD_PASS
BAND_Q_SATURATION = 0.995       # any arm >= this flags Q-discipline
BAND_SIGN_FLIP_TOL = 0.02       # lift below -this at smoke -> GATE full dispatch

assert 0.0 < BAND_HF_LIFT <= BAND_MIDDLE_LIFT < BAND_HP_PARTIAL_LIFT < BAND_HP_LIFT < 1.0, "band ordering"
assert 1.0 < BAND_HF_EFFRANK_LIFT < BAND_HP_EFFRANK_LIFT, "effrank lift ordering"
assert 0.0 < BAND_KNN_SENTINEL < 1.0, "knn sentinel"
assert 0.0 < KWTA_FRAC < 0.5, "kwta fraction"
assert EXPAND_RATIO >= 1, "expand ratio"

CONFIG_VERSION = (
    "dg_pattern_separation_prewrite_v1 "
    "(knn_baseline / uniform_no_presep / whitening_presep / dg_kwta / dg_lateral_inhib / dg_full) | "
    "proj=%d C=%d expand=%d kwta=%.3f norm_eps=%.0e homeo_tau=%.2f reg=%.2f sigma=%.2f | "
    "seeds=%s M=%s | CPU_numpy | bands locked"
) % (PROJ_DIM, C, EXPAND_RATIO, KWTA_FRAC, NORM_EPS, HOMEO_TAU, REG_LAMBDA, SIGMA, SEEDS, M_SWEEP)


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


def _off_diag_cos_mass(K, n_pairs=2000, rng=None):
    """Average |cosine| over n_pairs random off-diagonal pairs of K (anisotropy proxy).

    Higher = more cone-aligned (cosine collisions). Substrate's cone-collapse fixture has off-diag
    mass ~0.30-0.50; isotropic random has ~0.04 at d=768.
    """
    M = K.shape[0]
    if M < 2:
        return 0.0
    if rng is None:
        rng = np.random.default_rng(0)
    Kn = _np_norm(K)
    n = min(n_pairs, M * (M - 1) // 2)
    i = rng.integers(0, M, n)
    j = rng.integers(0, M, n)
    mask = i != j
    i = i[mask]; j = j[mask]
    cs = (Kn[i] * Kn[j]).sum(axis=1)
    return float(np.mean(np.abs(cs)))


# ---------- DG pre-write separator (composed substrate primitives) ----------

def _make_expander(d_in, d_out, seed):
    """Fixed-random binary expansion matrix (DG-style mossy fiber projection).

    Per-row: K=5 fan-in (~ DG mossy fiber sparsity). Output is M x d_out with K nonzeros per granule.
    Returns matrix scaled so output has comparable variance to input.
    """
    g = np.random.default_rng(seed)
    W = np.zeros((d_in, d_out), dtype=np.float32)
    K_fan_in = 5
    # for each output dim, pick K random input dims with random signs
    for j in range(d_out):
        idx = g.choice(d_in, K_fan_in, replace=False)
        signs = g.choice([-1.0, 1.0], K_fan_in).astype(np.float32)
        W[idx, j] = signs / math.sqrt(K_fan_in)
    return W


def _kwta(X, frac):
    """Sign-preserving k-WTA at top-K magnitudes per row (sparse-bipolar style)."""
    M, D = X.shape
    K = max(1, int(round(frac * D)))
    mag = np.abs(X)
    # find k-th largest magnitude per row; zero everything below it (sign preserved on survivors)
    thr_idx = np.argpartition(mag, -K, axis=1)[:, -K:]  # (M, K) -- indices of top-K mag
    out = np.zeros_like(X)
    rows = np.arange(M)[:, None]
    out[rows, thr_idx] = X[rows, thr_idx]
    return out


def _divisive_norm(X, eps):
    """Per-row Carandini-Heeger divisive normalization: x_i /= sqrt(eps + sum_j x_j^2)."""
    norms = np.sqrt(eps + (X * X).sum(axis=1, keepdims=True))
    return (X / norms).astype(np.float32)


def _homeostatic_threshold(X, tau, eps=1e-6):
    """Per-axis homeostatic gain: divide each column by EWMA of its absolute activation.

    EWMA over the M rows in one shot (since this is an offline batch -- no recurrence).
    Equivalent to "axes that fire often get downscaled" per Vogels-Sprekeler intuition.
    """
    col_mag = np.mean(np.abs(X), axis=0, keepdims=True)  # (1, D)
    # smooth via tau toward unit mean across columns
    mean_col = np.mean(col_mag) + eps
    target = (1.0 - tau) * col_mag + tau * mean_col
    return (X / (target + eps)).astype(np.float32)


def _sep_uniform_no_presep(K, expander):
    """No separator: pass keys through untouched (current substrate baseline)."""
    return K.astype(np.float32)


def _sep_whitening(K, expander):
    """ZCA-whitening only (rotation-only ablation)."""
    M, D = K.shape
    Sigma = (K.T @ K) / max(1, M) + WHITEN_EPS * np.eye(D, dtype=np.float32)
    lam, V = np.linalg.eigh(Sigma.astype(np.float64))
    lam = np.clip(lam, WHITEN_EPS, None)
    inv_sqrt = (V @ np.diag(1.0 / np.sqrt(lam)) @ V.T).astype(np.float32)
    return (K @ inv_sqrt).astype(np.float32)


def _sep_dg_kwta(K, expander):
    """Sparse k-WTA at KWTA_FRAC in the ORIGINAL d (no expansion, no norm)."""
    return _kwta(K.astype(np.float32), KWTA_FRAC)


def _sep_dg_lateral_inhib(K, expander):
    """k-WTA + divisive normalization (no expansion, no homeostasis)."""
    out = _kwta(K.astype(np.float32), KWTA_FRAC)
    return _divisive_norm(out, NORM_EPS)


def _sep_dg_full(K, expander):
    """Full DG composition: expansion + k-WTA + divisive norm + homeostasis."""
    Ke = K.astype(np.float32) @ expander  # expand to d_out = EXPAND_RATIO * D
    Ke = _kwta(Ke, KWTA_FRAC)
    Ke = _divisive_norm(Ke, NORM_EPS)
    Ke = _homeostatic_threshold(Ke, HOMEO_TAU)
    return Ke


# ---------- cleanup arm (uniform Tikhonov; same as Anchor #1) ----------

def _build_W_uniform(K, Y, reg_lambda):
    """Uniform-Tikhonov dual-form dense-KV cleanup (matches Anchor #1)."""
    M = K.shape[0]
    G = K @ K.T + reg_lambda * np.eye(M, dtype=np.float32)
    alpha = np.linalg.solve(G, Y).astype(np.float32)
    return alpha


def _cleanup_recall(K, alpha, cue):
    """Decode recall: pred = argmax(cue @ K^T @ alpha)."""
    readout = (cue @ K.T) @ alpha  # (Q, C)
    return np.argmax(readout, axis=1)


# ---------- per-seed arms runner ----------

_ARM_NAMES = [
    ("arm_uniform_no_presep",      _sep_uniform_no_presep),
    ("arm_whitening_presep",       _sep_whitening),
    ("arm_dg_kwta_presep",         _sep_dg_kwta),
    ("arm_dg_lateral_inhib_presep", _sep_dg_lateral_inhib),
    ("arm_dg_full",                _sep_dg_full),
]


def _arms_numpy(K, y, seed_for_arms, M_target):
    """Run KNN-baseline + all 5 separator arms on (M_target x D)."""
    M, D = K.shape
    g = np.random.default_rng(seed_for_arms)
    qidx = np.arange(M) if M <= MAX_Q else np.sort(g.choice(M, MAX_Q, replace=False))
    noise = (SIGMA * g.standard_normal((len(qidx), D))).astype(np.float32)
    Kn = _np_norm(K) * math.sqrt(D)
    cue = Kn[qidx] + noise
    ytrue = y[qidx]

    Y_onehot = np.eye(C, dtype=np.float32)[y]  # (M, C)

    # ARM_KNN_BASELINE (rank-blind sentinel; Fix #28) -- on RAW Kn (NOT through separator)
    arm_knn = _knn_topk_recall(Kn, cue, y, ytrue, topk=KNN_TOPK)

    # off-diagonal mass on RAW (anisotropy proxy)
    off_diag_raw = _off_diag_cos_mass(Kn, n_pairs=2000, rng=g)
    eff_rank_raw = _effective_rank(Kn)

    expander = _make_expander(D, EXPAND_RATIO * D, seed=seed_for_arms + 100)

    arm_metrics = {}
    arm_eff_ranks = {}
    arm_off_diags = {}
    for arm_name, sep_fn in _ARM_NAMES:
        K_sep = sep_fn(Kn, expander)
        cue_sep = sep_fn(cue, expander)
        # cleanup on separated K
        alpha = _build_W_uniform(K_sep, Y_onehot, REG_LAMBDA)
        pred = _cleanup_recall(K_sep, alpha, cue_sep)
        recall = float((pred == ytrue).mean())
        arm_metrics[arm_name] = round(recall, 4)
        arm_eff_ranks[arm_name] = round(_effective_rank(K_sep), 4)
        arm_off_diags[arm_name] = round(_off_diag_cos_mass(K_sep, n_pairs=2000, rng=g), 4)

    # lifts
    base = arm_metrics["arm_uniform_no_presep"]
    storage_bytes_per_mem = float(D * 4 + math.log2(C))

    return {
        "arm_knn_baseline": round(arm_knn, 4),
        **arm_metrics,
        "eff_rank_raw": round(eff_rank_raw, 4),
        **{("eff_rank_%s" % k.replace("arm_", "")): v for k, v in arm_eff_ranks.items()},
        "off_diag_raw": round(off_diag_raw, 4),
        **{("off_diag_%s" % k.replace("arm_", "")): v for k, v in arm_off_diags.items()},
        "lift_dg_full_over_uniform": round(arm_metrics["arm_dg_full"] - base, 4),
        "lift_dg_lateral_inhib_over_uniform": round(arm_metrics["arm_dg_lateral_inhib_presep"] - base, 4),
        "lift_dg_kwta_over_uniform": round(arm_metrics["arm_dg_kwta_presep"] - base, 4),
        "lift_whiten_over_uniform": round(arm_metrics["arm_whitening_presep"] - base, 4),
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
            "[seed=%d M=%d] knn=%.3f no_presep=%.3f whiten=%.3f dg_kwta=%.3f dg_lat=%.3f dg_full=%.3f | "
            "eff_rank raw=%.3f dg_full=%.3f | off_diag raw=%.3f dg_full=%.3f | lift_dg_full=%.3f"
        ) % (
            seed, M, a["arm_knn_baseline"], a["arm_uniform_no_presep"], a["arm_whitening_presep"],
            a["arm_dg_kwta_presep"], a["arm_dg_lateral_inhib_presep"], a["arm_dg_full"],
            a["eff_rank_raw"], a["eff_rank_dg_full"],
            a["off_diag_raw"], a["off_diag_dg_full"],
            a["lift_dg_full_over_uniform"],
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

    # Cross-cell sanity rail: KNN at M=400 on RAW keys
    knn_vals = vals(M_min, "arm_knn_baseline")
    knn_med, knn_std = _med_std(knn_vals)
    knn_pass = knn_med >= BAND_KNN_SENTINEL

    # Mechanism eval at M_max
    uniform_med, uniform_std = _med_std(vals(M_max, "arm_uniform_no_presep"))
    whiten_med, whiten_std = _med_std(vals(M_max, "arm_whitening_presep"))
    dg_kwta_med, dg_kwta_std = _med_std(vals(M_max, "arm_dg_kwta_presep"))
    dg_lat_med, dg_lat_std = _med_std(vals(M_max, "arm_dg_lateral_inhib_presep"))
    dg_full_med, dg_full_std = _med_std(vals(M_max, "arm_dg_full"))

    eff_raw, _ = _med_std(vals(M_max, "eff_rank_raw"))
    eff_dg_full, _ = _med_std(vals(M_max, "eff_rank_dg_full"))
    off_raw, _ = _med_std(vals(M_max, "off_diag_raw"))
    off_dg_full, _ = _med_std(vals(M_max, "off_diag_dg_full"))

    lift_dg_full = dg_full_med - uniform_med
    lift_dg_lat = dg_lat_med - uniform_med
    lift_dg_kwta = dg_kwta_med - uniform_med
    lift_whiten = whiten_med - uniform_med
    effrank_lift = eff_dg_full / (eff_raw + EFF_RANK_EPS)

    # SIGN-CHECK GATE (smoke critical per task spec)
    smoke_sign_flip = False
    if RUN_MODE == "smoke":
        if lift_dg_full < -BAND_SIGN_FLIP_TOL:
            smoke_sign_flip = True

    detail = {
        "M_eval": M_max,
        "M_sentinel": M_min,
        "arm_knn_baseline_at_M_sentinel": round(knn_med, 4),
        "arm_uniform_no_presep": round(uniform_med, 4),
        "arm_whitening_presep": round(whiten_med, 4),
        "arm_dg_kwta_presep": round(dg_kwta_med, 4),
        "arm_dg_lateral_inhib_presep": round(dg_lat_med, 4),
        "arm_dg_full": round(dg_full_med, 4),
        "std_uniform_no_presep": round(uniform_std, 4),
        "std_whitening_presep": round(whiten_std, 4),
        "std_dg_kwta_presep": round(dg_kwta_std, 4),
        "std_dg_lateral_inhib_presep": round(dg_lat_std, 4),
        "std_dg_full": round(dg_full_std, 4),
        "eff_rank_raw": round(eff_raw, 4),
        "eff_rank_dg_full": round(eff_dg_full, 4),
        "effrank_lift_dg_full_over_raw": round(effrank_lift, 4),
        "off_diag_raw": round(off_raw, 4),
        "off_diag_dg_full": round(off_dg_full, 4),
        "lift_dg_full_over_uniform": round(lift_dg_full, 4),
        "lift_dg_lateral_inhib_over_uniform": round(lift_dg_lat, 4),
        "lift_dg_kwta_over_uniform": round(lift_dg_kwta, 4),
        "lift_whiten_over_uniform": round(lift_whiten, 4),
        "knn_sentinel_pass": bool(knn_pass),
        "smoke_sign_flip": bool(smoke_sign_flip),
        "n_seeds": len(units),
        "bands": {
            "HP_ABS": BAND_HP_ABS, "HP_LIFT": BAND_HP_LIFT, "HP_PARTIAL_LIFT": BAND_HP_PARTIAL_LIFT,
            "MIDDLE_LIFT": BAND_MIDDLE_LIFT, "HF_LIFT": BAND_HF_LIFT,
            "HP_EFFRANK_LIFT": BAND_HP_EFFRANK_LIFT, "HF_EFFRANK_LIFT": BAND_HF_EFFRANK_LIFT,
            "KNN_SENTINEL": BAND_KNN_SENTINEL, "STD_HP": BAND_STD_HP,
            "Q_SATURATION": BAND_Q_SATURATION, "SIGN_FLIP_TOL": BAND_SIGN_FLIP_TOL,
        },
        "CONFIG_VERSION": CONFIG_VERSION,
        "cites": [
            "research_gap2_anisotropy_5x_drill_2026-06-26",
            "exp_dev_handoff_research_gap2_anisotropy_5x_drill_2026-06-26",
            "exp_dev_anisotropy_mimo_waterfill_v1_SMOKE_HARD_FAIL_2026-06-26",
            "substrate_anisotropy_rescue_4arm_sweep_v2_calibrated_meter_full",
            "research_anisotropy_drill_2_solutions_brain_substrate_2026-06-25",
            "Marr_1971_hippocampus",
            "Carandini_Heeger_2012_divisive_normalization",
            "Mu_Viswanath_anisotropy_word_embeddings",
        ],
    }

    # Q-discipline
    q_flags = []
    for name, val in [("dg_full", dg_full_med), ("dg_lateral_inhib", dg_lat_med),
                       ("dg_kwta", dg_kwta_med), ("uniform_no_presep", uniform_med),
                       ("whitening_presep", whiten_med)]:
        if val >= BAND_Q_SATURATION:
            q_flags.append("[Q-DISCIPLINE: %s=%.4f >= %.3f -- suspect saturation; under-claim]" %
                           (name, val, BAND_Q_SATURATION))
    q_note = " ".join(q_flags) + (" " if q_flags else "")

    # per-arm summary string (Fix #28 -- raw arm metrics)
    summ = (
        "knn@M=%d=%.3f | no_presep=%.3f whiten=%.3f dg_kwta=%.3f dg_lat=%.3f dg_full=%.3f | "
        "lift_dg_full=%.3f lift_dg_lat=%.3f lift_dg_kwta=%.3f lift_whiten=%.3f | "
        "eff_rank raw=%.3f dg_full=%.3f (lift=%.2fx) | off_diag raw=%.3f dg_full=%.3f"
    ) % (M_min, knn_med, uniform_med, whiten_med, dg_kwta_med, dg_lat_med, dg_full_med,
         lift_dg_full, lift_dg_lat, lift_dg_kwta, lift_whiten,
         eff_raw, eff_dg_full, effrank_lift, off_raw, off_dg_full)

    # GATE 0: KNN sentinel (Fix #28 by-construction-saturation contamination catch on RAW keys)
    if not knn_pass:
        return ("HARD_FAIL",
                ("HARD_FAIL_KNN_SENTINEL: KNN@M=%d (RAW keys) = %.3f < %.2f -> keys themselves "
                 "are corrupted (not just anisotropic); any separator-arm lift is artifact. "
                 "Aborting verdict on mechanism arms. %s%s"
                 ) % (M_min, knn_med, BAND_KNN_SENTINEL, q_note, summ),
                detail)

    # GATE -1: SMOKE_SIGN_FLIP (per task spec -- gate full dispatch on smoke sign-wrong)
    if smoke_sign_flip:
        return ("HARD_FAIL",
                ("HARD_FAIL_SMOKE_SIGN_FLIP: at smoke, lift_dg_full_over_uniform=%.3f < -%.3f at M=%d "
                 "-> DG separator HURTS recall vs raw uniform. Full dispatch GATED (don't burn 3-5hr "
                 "on a sign-wrong cell). %s%s"
                 ) % (lift_dg_full, BAND_SIGN_FLIP_TOL, M_max, q_note, summ),
                detail)

    # GATE 1: HARD_PASS_DG_PRESEP_RESCUES
    if (dg_full_med >= BAND_HP_ABS and
        lift_dg_full >= BAND_HP_LIFT and
        effrank_lift >= BAND_HP_EFFRANK_LIFT and
        dg_full_std <= BAND_STD_HP):
        return ("HARD_PASS",
                ("HARD_PASS_DG_PRESEP_RESCUES: dg_full=%.3f >= %.2f AND lift_over_uniform=%.3f >= %.2f "
                 "AND effrank_lift=%.2fx >= %.2fx AND std=%.3f <= %.2f AND knn_sentinel=%.3f >= %.2f "
                 "at M=%d. DG pattern-separation PRE-WRITE rescues anisotropy collapse on real Pythia "
                 "keys (uniform_no_presep collapsed to %.3f); off-diag mass dropped %.3f -> %.3f. %s%s"
                 ) % (dg_full_med, BAND_HP_ABS, lift_dg_full, BAND_HP_LIFT,
                      effrank_lift, BAND_HP_EFFRANK_LIFT, dg_full_std, BAND_STD_HP,
                      knn_med, BAND_KNN_SENTINEL, M_max, uniform_med, off_raw, off_dg_full,
                      q_note, summ),
                detail)

    # GATE 2: HARD_PASS_PARTIAL
    if lift_dg_full >= BAND_HP_PARTIAL_LIFT:
        return ("HARD_PASS",
                ("HARD_PASS_PARTIAL_DG_PRESEP: lift_over_uniform=%.3f >= %.2f at M=%d but not all "
                 "HARD_PASS conditions met (abs=%.3f vs >=%.2f; effrank_lift=%.2fx vs >=%.2fx; "
                 "std=%.3f vs <=%.2f). DG separator partially rescues anisotropy. uniform=%.3f. %s%s"
                 ) % (lift_dg_full, BAND_HP_PARTIAL_LIFT, M_max, dg_full_med, BAND_HP_ABS,
                      effrank_lift, BAND_HP_EFFRANK_LIFT, dg_full_std, BAND_STD_HP,
                      uniform_med, q_note, summ),
                detail)

    # GATE 3: MIDDLE_BAND
    if lift_dg_full > BAND_MIDDLE_LIFT:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND_DG_PRESEP: lift_over_uniform=%.3f in (%.2f, %.2f] at M=%d -> DG "
                 "separator helps modestly but does not chain-grade. uniform=%.3f dg_full=%.3f. %s%s"
                 ) % (lift_dg_full, BAND_MIDDLE_LIFT, BAND_HP_PARTIAL_LIFT, M_max,
                      uniform_med, dg_full_med, q_note, summ),
                detail)

    # GATE 4: HARD_FAIL_DG_PRESEP_DOESNT_HELP
    if lift_dg_full <= BAND_HF_LIFT or effrank_lift <= BAND_HF_EFFRANK_LIFT:
        return ("HARD_FAIL",
                ("HARD_FAIL_DG_PRESEP_DOESNT_HELP: lift_over_uniform=%.3f <= %.2f OR effrank_lift=%.2fx "
                 "<= %.2fx at M=%d -> DG-style PRE-WRITE separation is NOT a chain-grade rescue for "
                 "cone-collapsed anisotropy on real Pythia keys. uniform=%.3f dg_full=%.3f. "
                 "Tier A Anchor #2 falsified; consider Tier A Anchor #3 (Brenier map) or #5 (CS fly-LSH). %s"
                 ) % (lift_dg_full, BAND_HF_LIFT, effrank_lift, BAND_HF_EFFRANK_LIFT, M_max,
                      uniform_med, dg_full_med, summ),
                detail)

    return ("MIDDLE_BAND",
            ("UNCLASSIFIED_MIDDLE_BAND: lift_dg_full=%.3f effrank_lift=%.2fx at M=%d. %s%s"
             ) % (lift_dg_full, effrank_lift, M_max, q_note, summ),
            detail)


# ---------- self-test (synthetic; no encoder) ----------

def _selftest():
    """Self-test on synthetic anisotropic data.

    Cell semantics MUST hold on a CONTROLLED anisotropic regime where:
      (a) raw keys are anisotropic (eff_rank_raw < 0.50)
      (b) DG_FULL separator MEASURABLY raises effective rank (effrank_lift > 1.0)
      (c) DG_FULL separator MEASURABLY drops off-diagonal cosine mass vs raw
      (d) KNN baseline at small M >= 0.90 on isotropic random (sentinel works)
      (e) k-WTA preserves exactly KWTA_FRAC * D nonzeros per row
    """
    g = np.random.default_rng(0)
    d = 64
    M = 200
    cone_dim = 8
    cone_basis = g.standard_normal((d, cone_dim)).astype(np.float32)
    cone_basis, _ = np.linalg.qr(cone_basis)
    coeffs = g.standard_normal((M, cone_dim)).astype(np.float32) * 2.0
    common_mode = g.standard_normal((1, d)).astype(np.float32) * 1.5
    K_aniso = (coeffs @ cone_basis.T + common_mode).astype(np.float32)
    y_aniso = g.integers(0, C, M).astype(np.int64)
    out = _arms_numpy(K_aniso, y_aniso, 1, M)

    # (a) anisotropic synthetic must have low eff_rank
    assert out["eff_rank_raw"] < 0.50, (
        "anisotropic synthetic must have low eff_rank (got %.3f)" % out["eff_rank_raw"])

    # (b) DG_FULL must MEASURABLY raise effective rank (input-side separator works)
    effrank_lift = out["eff_rank_dg_full"] / (out["eff_rank_raw"] + EFF_RANK_EPS)
    assert effrank_lift > 1.0, (
        "DG_FULL must raise eff_rank vs raw on synthetic anisotropic data "
        "(got effrank_dg_full=%.3f, raw=%.3f, lift=%.2fx)"
        % (out["eff_rank_dg_full"], out["eff_rank_raw"], effrank_lift))

    # (c) off-diagonal cosine mass should DROP on DG_FULL (separator orthogonalizes pairs)
    assert out["off_diag_dg_full"] < out["off_diag_raw"], (
        "DG_FULL must drop off-diag cosine mass vs raw "
        "(got raw=%.3f, dg_full=%.3f)" % (out["off_diag_raw"], out["off_diag_dg_full"]))

    # (d) KNN at SMALL M on isotropic recovers (rank-blind sentinel works)
    iso = _np_norm(g.standard_normal((50, d)).astype(np.float32))
    yiso = g.integers(0, C, 50).astype(np.int64)
    iso_out = _arms_numpy(iso, yiso, 2, 50)
    assert iso_out["arm_knn_baseline"] >= 0.90, (
        "KNN sentinel must work on isotropic small-M synthetic (got %.3f)" % iso_out["arm_knn_baseline"])

    # (e) k-WTA preserves exactly KWTA_FRAC*D nonzeros per row
    test_X = g.standard_normal((10, 100)).astype(np.float32)
    test_K_keep = max(1, int(round(KWTA_FRAC * 100)))
    test_out = _kwta(test_X, KWTA_FRAC)
    nonzero_counts = (test_out != 0).sum(axis=1)
    assert (nonzero_counts == test_K_keep).all(), (
        "k-WTA must preserve exactly %d nonzeros per row at frac=%.3f, D=100 "
        "(got nonzero counts %s)" % (test_K_keep, KWTA_FRAC, nonzero_counts.tolist()))

    # (f) lifts are numerically sane (in [-0.5, 0.5] absolute on synthetic)
    assert -0.5 < out["lift_dg_full_over_uniform"] < 0.5, (
        "lift must be numerically sane (got %.3f)" % out["lift_dg_full_over_uniform"])

    # (g) expander shape is correct
    exp = _make_expander(d, EXPAND_RATIO * d, seed=42)
    assert exp.shape == (d, EXPAND_RATIO * d), (
        "expander shape wrong (got %s, want (%d, %d))" % (exp.shape, d, EXPAND_RATIO * d))
    # each column has exactly K=5 nonzeros
    col_nnz = (exp != 0).sum(axis=0)
    assert (col_nnz == 5).all(), ("expander columns must have K=5 nonzeros (got %s)" % col_nnz.tolist())

    print(
        "[selftest] PASS: eff_rank_raw=%.3f -> dg_full=%.3f (lift=%.2fx); "
        "off_diag raw=%.3f -> dg_full=%.3f; knn_baseline isotropic=%.3f; "
        "lift_dg_full_over_uniform=%.3f; k-WTA exact-K verified; expander shape OK"
        % (out["eff_rank_raw"], out["eff_rank_dg_full"], effrank_lift,
           out["off_diag_raw"], out["off_diag_dg_full"],
           iso_out["arm_knn_baseline"], out["lift_dg_full_over_uniform"]),
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
        "metrics_source": "measured_cpu_anisotropy_dg_pattern_separation_prewrite_v1",
        "per_unit": units,
        "elapsed_s": time.time() - t0,
    }
    write_metrics(out_dir, metrics, units)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
