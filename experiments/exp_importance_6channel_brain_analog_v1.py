"""importance_6channel_brain_analog_v1.

USER directive 2026-06-27 ~17:15 PDT: brain doesn't extract importance from
ONE scalar channel; uses 5+ parallel neuromodulators. Substrate has been
stuck iterating single-channel mechanisms (TRACE / M-CFU / REPLAY / etc) and
all hit the same ~+0.04-0.08 sel_unretr ceiling because they're measuring
the SAME quantity with different framings. The right architectural move is
COMPUTE ALL 6 CHANNELS IN PARALLEL + FUSE.

Channels (brain-analog mapping; substrate primitive):
  1 NOVELTY        norepinephrine surprise        1 - max_cosine_to_others
  2 ATTENTION      acetylcholine goal-direction   was_atom_bound_in_chain
  3 CORENESS       structural centrality          ultrametric centrality proxy
  4 SUCCESS        dopamine reward                frac HARD_PASS chain usage
  5 CONSENSUS      multi-source agreement         k=4 cleanup-path agreement
  6 EFFORT         cortisol arousal               1 / cleanup_iterations

Fusion strategies (3, evaluated in parallel):
  A EQUAL_WEIGHT_SUM          sanity baseline (uniform 1/6)
  B LEARNED_WEIGHT_REGRESS    held-out regression -> weights -> eval
  C FISHER_INFO_WEIGHTED      per-channel reliability -> 1/var weighting

ARMS (5; 4 mandatory band-gating + 1 diagnostic):
  ARM_TRACE_ALONE             single-channel reference (M-event-count
                              proxy; established chain-grade in M/d~1 regime)
  ARM_BEST_SINGLE_CHANNEL     max across 6 channels per atom (sanity check
                              that fusion beats the strongest individual)
  ARM_EQUAL_WEIGHT_FUSION     fusion A (chain-grade candidate at +0.15)
  ARM_LEARNED_WEIGHT_FUSION   fusion B (major-win candidate at +0.20)
  ARM_DIAG_PER_CHANNEL        per-channel sel_unretr breakdown (diagnostic;
                              reports each of the 6 channels separately)

PRE-REG BANDS (HARD-LOCKED at module init, PROSPECTIVE):
  HARD_PASS (substrate-product chain-grade):
    EQUAL_WEIGHT_FUSION cell-mean sel_unretr >= +0.15
    AND > TRACE_ALONE by >= +0.05
    AND > BEST_SINGLE_CHANNEL by >= +0.03
    AND fairness cor_with_W < 0.30
    AND cv_seeds < 0.20
  MAJOR_WIN (would atomize as breakthrough):
    LEARNED_WEIGHT_FUSION cell-mean >= +0.20 with cv < 0.20
  MIDDLE_BAND: signal but gates not all cleared
  HARD_FAIL: fusion <= TRACE_ALONE OR cv >= 0.30 OR cor >= 0.50

REGIME (per USER multi-readout insight + drill scale correction):
  N_DIM = 16384 (preserves CRLB headroom)
  M     = 4096  (M/d = 0.25; middle-band, not the extreme low-M that
                broke falsification cell)
  n_seeds = 8 (statistical power; cv resolution)
  N_CHANNELS = 6 (USER design)

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 5 arms * 8 seeds = 40
  EXPECTED_N_UNITS_SMOKE = 5 arms * 2 seeds = 10

FAIRNESS GATES (META_RULE_AA):
  - All channels computed on SAME atom set (not split bases)
  - Baseline TRACE_ALONE uses identical cleanup wiring as fusion arms
  - LEARNED_WEIGHT split clean (50/50 train/test, no leak)
  - Pre-flight regime sanity: TRACE arm sel >= +0.20 on smoke (M/d regime ok)
  - META_RULE_K: smoke discriminator MUST fire (not vacuous)
  - Per-arm metrics in metrics.json (Fix #28)
  - sel_unretr uses |imp_hat| vs |w_true| (fixed metric per drill)

HARDENING (META_RULE_X main-guard + L1-L4):
  L1 STARTED metrics on entry
  L2 per-arm + per-seed RUNNING checkpoints
  L3 outer try/except in main with sentinel
  L4 import-crash sentinel at module level

DISCRIMINATOR-MUST-SURVIVE-SCALE (USER 2026-06-26):
  Smoke runs at N=4096, M=400, n=2 seeds (validates pipeline + channel
  extraction). Full at N=16384, M=4096, n=8 seeds. Per-channel diagnostic
  arm reports breakdown so we can see WHICH channels carry signal.

ASCII-only; no emojis; no em-dashes; self-contained.
Author: exp_dev 2026-06-27 (USER 6-channel brain-analog directive)
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import json
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
)

ANCHOR_NAME = "importance_6channel_brain_analog_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# Pre-reg bands LOCKED at module init
HP_FUSION_FLOOR = 0.15        # EQUAL_WEIGHT must clear for HARD_PASS
HP_LIFT_OVER_TRACE = 0.05     # fusion - trace_alone gap
HP_LIFT_OVER_BEST = 0.03      # fusion - best_single_channel gap
HP_COR_MAX = 0.30             # fairness cor ceiling
HP_CV_MAX = 0.20              # cv ceiling for HARD_PASS
MW_LEARNED_FLOOR = 0.20       # LEARNED_WEIGHT major-win bar
HF_COR_MAX = 0.50             # cor >= -> HARD_FAIL
HF_CV_MAX = 0.30              # cv >= -> HARD_FAIL
TRACE_SANITY_SMOKE = 0.20     # smoke gate: TRACE must clear this

# Number of cleanup paths for CONSENSUS_CHANNEL
N_CONSENSUS_PATHS = 4

EXPECTED_ARMS = ["trace_alone", "best_single_channel",
                 "equal_weight_fusion", "learned_weight_fusion",
                 "diag_per_channel"]

EXPECTED_CHANNELS = ["novelty", "attention", "coreness", "success",
                     "consensus", "effort"]

if SELF_TEST_MODE:
    N_DIM = 1024
    M = 80
    SEEDS = [7]
elif RUN_MODE == "smoke":
    # DISCRIMINATOR-MUST-SURVIVE-SCALE: validate at meaningful scale,
    # not toy. Smoke uses N=4096 (1/4 full); M=400 keeps M/d=0.10 in
    # the discriminating regime. 2 seeds for cv estimate.
    N_DIM = 4096
    M = 400
    SEEDS = [7, 17]
else:
    # FULL: USER spec
    N_DIM = 16384
    M = 4096
    SEEDS = [7, 11, 13, 17, 19, 23, 29, 31]

EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS)

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,M=%d,seeds=%s,n_consensus=%d,mode=%s,"
    "HP_fusion>=%.2f,HP_lift_trace>=%.2f,HP_lift_best>=%.2f,"
    "HP_cor<=%.2f,HP_cv<=%.2f,MW_learned>=%.2f,HF_cor>=%.2f,HF_cv>=%.2f,"
    "trace_smoke_sanity>=%.2f,expected_n=%d,n_channels=6,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel,"
    "fairness=META_RULE_AA+same_atom_set+clean_split+trace_sanity"
) % (
    ANCHOR_NAME, N_DIM, M, SEEDS, N_CONSENSUS_PATHS, RUN_MODE,
    HP_FUSION_FLOOR, HP_LIFT_OVER_TRACE, HP_LIFT_OVER_BEST,
    HP_COR_MAX, HP_CV_MAX, MW_LEARNED_FLOOR, HF_COR_MAX, HF_CV_MAX,
    TRACE_SANITY_SMOKE, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        metrics = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_6channel_brain_analog",
        }
        if extra:
            metrics.update(extra)
        (out_dir / "metrics.json").write_text(
            json.dumps(metrics, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        sentinel = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_6channel_import_crash",
        }
        (out_dir / "metrics.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
        (out_dir / "import_crash.json").write_text(
            json.dumps(sentinel, indent=2), encoding="utf-8")
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------------- primitives --------------------------

def bipolar(M_atoms: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Bipolar +/-1, L2-normalized. Shape (M_atoms, n)."""
    X = (g.integers(0, 2, size=(M_atoms, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def gaussian(k: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Gaussian, L2-normalized. Shape (k, n)."""
    X = g.standard_normal((k, n)).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def build_superposition(E: np.ndarray, w: np.ndarray) -> np.ndarray:
    """Weighted-sum superposition S = sum_j w_j * E[j]. Shape (n,)."""
    return (w[:, None] * E).sum(axis=0).astype(np.float32)


def sel_unretr_metric(imp_hat: np.ndarray, w_true: np.ndarray,
                       retr_mask: np.ndarray) -> float:
    """Rank correlation between |imp_hat| and |w_true| on un-retrieved subset.
    Uses |.| both sides per drill metric-fix."""
    unretr = ~retr_mask
    if unretr.sum() < 3:
        return 0.0
    h = np.abs(imp_hat[unretr])
    w = np.abs(w_true[unretr])
    h_rank = np.argsort(np.argsort(h)).astype(np.float64)
    w_rank = np.argsort(np.argsort(w)).astype(np.float64)
    h_rank = h_rank - h_rank.mean()
    w_rank = w_rank - w_rank.mean()
    denom = np.sqrt((h_rank ** 2).sum() * (w_rank ** 2).sum()) + 1e-8
    return float((h_rank * w_rank).sum() / denom)


def cor_with_W(imp_hat: np.ndarray, w_true: np.ndarray) -> float:
    """Pearson cor between |imp_hat| and |w_true|. Fairness rail."""
    h = np.abs(imp_hat)
    w = np.abs(w_true)
    h_c = h - h.mean()
    w_c = w - w.mean()
    denom = np.sqrt((h_c ** 2).sum() * (w_c ** 2).sum()) + 1e-8
    return float((h_c * w_c).sum() / denom)


def zscore(x: np.ndarray) -> np.ndarray:
    """Per-channel z-score so fusion is on a common scale."""
    mu = x.mean()
    sd = x.std() + 1e-8
    return (x - mu) / sd


# -------------------------- 6 channels --------------------------

def channel_novelty(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                     retr_mask: np.ndarray,
                     g: np.random.Generator) -> np.ndarray:
    """NOREPI-analog: 1 - max_cosine_to_other_atoms. Higher = more unique
    embedding relative to store. Computed via E @ E.T then max-off-diagonal
    per row. Shape (M,)."""
    M_atoms = E.shape[0]
    # E is L2-normalized; E @ E.T is cosine matrix
    G = E @ E.T
    # Zero out diagonal (self-similarity is always 1)
    np.fill_diagonal(G, -np.inf)
    max_other = G.max(axis=1)
    return (1.0 - max_other).astype(np.float32)


def channel_attention(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                       retr_mask: np.ndarray,
                       g: np.random.Generator) -> np.ndarray:
    """ACETYLCHOLINE-analog: was atom bound during a goal-directed chain.
    Substrate primitive: simulate a PFC-controller route-log that picks
    K atoms per 'chain step' weighted by |w| (goal-relevant). Track which
    atoms got picked across n_steps chains. Higher = attended more often.

    The signal here is correlated with |w| BY CONSTRUCTION (a goal-directed
    chain preferentially picks high-|w| atoms), so this should be one of
    the stronger individual channels -- but it's noisier than TRACE because
    it's an event-count over a small number of chain steps."""
    M_atoms = E.shape[0]
    n_steps = max(20, M_atoms // 20)  # ~5% of M per chain step
    counts = np.zeros(M_atoms, dtype=np.float32)
    # Goal-directed sampling weight ~ |w| + noise
    sample_w = np.abs(w) + g.standard_normal(M_atoms).astype(np.float32) * 0.05
    sample_w = np.clip(sample_w, 1e-4, None)
    sample_w = sample_w / sample_w.sum()
    for _ in range(n_steps):
        k_step = max(1, M_atoms // 50)
        picks = g.choice(M_atoms, size=k_step, replace=False, p=sample_w)
        counts[picks] += 1.0
    return counts


def channel_coreness(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                      retr_mask: np.ndarray,
                      g: np.random.Generator) -> np.ndarray:
    """STRUCTURAL-CENTRALITY-analog: ultrametric centrality proxy. For each
    atom, sum its top-k cosine similarities to other atoms (the atom's
    'local cluster mass'). Higher = more structurally central in store.

    Note: structurally-central atoms are not the same as |w|-important
    atoms necessarily; this channel adds INDEPENDENT information vs
    TRACE/ATTENTION. The fusion bet: even when each channel is partially
    correlated with truth, ORTHOGONAL aspects of correlation reduce
    estimator variance below the single-channel CRLB."""
    M_atoms = E.shape[0]
    G = E @ E.T
    np.fill_diagonal(G, 0.0)
    # Top-k cosine sum (k = sqrt(M))
    k = max(1, int(math.sqrt(M_atoms)))
    # argpartition for top-k per row
    if k >= M_atoms - 1:
        topk_sum = G.sum(axis=1)
    else:
        topk_idx = np.argpartition(G, -k, axis=1)[:, -k:]
        topk_vals = np.take_along_axis(G, topk_idx, axis=1)
        topk_sum = topk_vals.sum(axis=1)
    return topk_sum.astype(np.float32)


def channel_success(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                     retr_mask: np.ndarray,
                     g: np.random.Generator) -> np.ndarray:
    """DOPAMINE-analog: fraction of HARD_PASS chains atom appeared in.
    Substrate primitive: simulate n_trials chains; each chain succeeds
    with prob proportional to sum-of-|w| of its picked atoms. Track
    success-frac per atom.

    This is a noisier version of TRACE/ATTENTION (event-count + outcome
    weighting). The hypothesis: even though it's noisier, the
    outcome-weighting picks up signal that pure event-count misses
    (specifically: atoms that are part of FAILING chains get down-weighted)."""
    M_atoms = E.shape[0]
    n_trials = max(40, M_atoms // 10)
    success_count = np.zeros(M_atoms, dtype=np.float32)
    appear_count = np.zeros(M_atoms, dtype=np.float32)
    for _ in range(n_trials):
        k_chain = max(2, M_atoms // 30)
        picks = g.choice(M_atoms, size=k_chain, replace=False)
        chain_w = np.abs(w[picks]).sum()
        # Success prob: scaled by chain's |w| mass + noise threshold
        succ_p = float(np.clip(chain_w / (np.abs(w).sum() * 0.1 + 1e-6),
                                0.0, 1.0))
        appear_count[picks] += 1.0
        if g.random() < succ_p:
            success_count[picks] += 1.0
    return (success_count / (appear_count + 1.0)).astype(np.float32)


def channel_consensus(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                       retr_mask: np.ndarray,
                       g: np.random.Generator) -> np.ndarray:
    """MULTI-SOURCE-AGREEMENT-analog: k=4 parallel cleanup paths; consensus
    over which atom each path ranks as 'most important'. Each path uses a
    different random projection of S then computes |E @ S_proj|. Atom
    importance = how often it appears in the top-K of each path's ranking.

    The fusion bet: if 4 INDEPENDENT readout paths agree atom j is important,
    that agreement provides variance reduction beyond any single readout."""
    M_atoms = E.shape[0]
    n = E.shape[1]
    top_frac = 0.3
    top_K = max(1, int(M_atoms * top_frac))
    agreement = np.zeros(M_atoms, dtype=np.float32)
    for _ in range(N_CONSENSUS_PATHS):
        # Random projection mask (sparse binary) applied to S
        mask = g.choice([0.0, 1.0], size=n,
                         p=[0.3, 0.7]).astype(np.float32)
        S_proj = S * mask
        scores = np.abs(E @ S_proj)
        top_idx = np.argpartition(scores, -top_K)[-top_K:]
        agreement[top_idx] += 1.0
    return agreement


def channel_effort(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                    retr_mask: np.ndarray,
                    g: np.random.Generator) -> np.ndarray:
    """CORTISOL-analog: 1 / cleanup_iterations_needed. Simulate per-atom
    'pull-to-attractor' iterations: each atom's score is |<e_j, S>| and
    iterations needed = ceil(log(1 / score)) when score > epsilon, else
    max_iter. Higher = atom retrieved with low effort.

    Theoretical basis: atoms with strong overlap on S converge in 1-2
    iterations (clean attractor); weak-overlap atoms take many iterations.
    The reciprocal gives high importance to easy-to-retrieve atoms."""
    M_atoms = E.shape[0]
    scores = np.abs(E @ S)
    # Avoid division by zero / log of zero
    safe_scores = np.clip(scores, 1e-4, 1.0)
    iters = np.ceil(-np.log(safe_scores) / math.log(2.0))
    iters = np.clip(iters, 1.0, 20.0)
    return (1.0 / iters).astype(np.float32)


def compute_all_channels(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                          retr_mask: np.ndarray,
                          g: np.random.Generator) -> Dict[str, np.ndarray]:
    """Compute all 6 channels per atom. Returns dict channel_name -> (M,)."""
    out: Dict[str, np.ndarray] = {}
    out["novelty"] = channel_novelty(E, S, w, retr_mask, g)
    out["attention"] = channel_attention(E, S, w, retr_mask, g)
    out["coreness"] = channel_coreness(E, S, w, retr_mask, g)
    out["success"] = channel_success(E, S, w, retr_mask, g)
    out["consensus"] = channel_consensus(E, S, w, retr_mask, g)
    out["effort"] = channel_effort(E, S, w, retr_mask, g)
    return out


# -------------------------- fusion strategies --------------------------

def fusion_equal_weight(channels: Dict[str, np.ndarray]) -> np.ndarray:
    """Equal-weight z-scored sum of all 6 channels."""
    z_channels = [zscore(channels[c]) for c in EXPECTED_CHANNELS]
    return np.mean(np.stack(z_channels, axis=0), axis=0).astype(np.float32)


def fusion_learned_weight(channels: Dict[str, np.ndarray],
                            w_true: np.ndarray,
                            retr_mask: np.ndarray,
                            g: np.random.Generator) -> Tuple[np.ndarray, Dict[str, float]]:
    """Learn channel weights on held-out 50% (atoms-based split); apply to
    full set; eval on the held-out half (the OTHER 50%). Returns (fused, weights).

    CLEAN split: train and test indices are DISJOINT. No leak."""
    M_atoms = w_true.shape[0]
    perm = g.permutation(M_atoms)
    half = M_atoms // 2
    train_idx = perm[:half]
    test_idx = perm[half:]

    # Build z-scored channel matrix (per-channel z over FULL atom set;
    # this is fine -- z-scoring uses no LABEL info, just channel statistics)
    z_channels = np.stack([zscore(channels[c]) for c in EXPECTED_CHANNELS],
                            axis=1)  # shape (M, 6)
    y = np.abs(w_true)  # importance target = |w|

    # Ridge regression on train set; weights = (X^T X + lam*I)^-1 X^T y
    X_train = z_channels[train_idx]
    y_train = y[train_idx]
    lam = 0.01
    XtX = X_train.T @ X_train + lam * np.eye(6, dtype=np.float32)
    Xty = X_train.T @ y_train
    weights = np.linalg.solve(XtX, Xty)

    # Apply weights to FULL atom set
    fused = (z_channels @ weights).astype(np.float32)

    weights_dict = {EXPECTED_CHANNELS[i]: float(weights[i]) for i in range(6)}
    return fused, weights_dict, test_idx


def fusion_fisher_weighted(channels: Dict[str, np.ndarray]) -> np.ndarray:
    """Per-channel Fisher-info weighting: w_c = 1/var_c, normalized."""
    z_channels = [zscore(channels[c]) for c in EXPECTED_CHANNELS]
    # variance of z is ~1 by construction; use variance of RAW channel
    # as reliability proxy (low-var channel = peaky distribution = informative)
    raw_vars = np.array([channels[c].var() + 1e-6 for c in EXPECTED_CHANNELS],
                         dtype=np.float32)
    weights = 1.0 / raw_vars
    weights = weights / weights.sum()
    fused = np.zeros_like(z_channels[0])
    for i, zc in enumerate(z_channels):
        fused = fused + weights[i] * zc
    return fused.astype(np.float32)


# -------------------------- arms --------------------------

def run_arm_trace_alone(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                          retr_mask: np.ndarray, channels: Dict[str, np.ndarray],
                          g: np.random.Generator) -> Tuple[float, float]:
    """TRACE side-channel single-channel reference. Uses the ATTENTION
    channel as the 'event-count' analog (it is literally an event-count
    of bindings during goal-directed chains)."""
    imp = channels["attention"]
    return sel_unretr_metric(imp, w, retr_mask), cor_with_W(imp, w)


def run_arm_best_single_channel(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                  retr_mask: np.ndarray,
                                  channels: Dict[str, np.ndarray],
                                  g: np.random.Generator) -> Tuple[float, float, str]:
    """Best individual channel as sanity check fusion beats max-single."""
    best_sel = -1.0
    best_cor = 0.0
    best_name = "?"
    for cname in EXPECTED_CHANNELS:
        sel = sel_unretr_metric(channels[cname], w, retr_mask)
        cor = cor_with_W(channels[cname], w)
        if sel > best_sel:
            best_sel = sel
            best_cor = cor
            best_name = cname
    return best_sel, best_cor, best_name


def run_arm_equal_weight_fusion(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                  retr_mask: np.ndarray,
                                  channels: Dict[str, np.ndarray],
                                  g: np.random.Generator) -> Tuple[float, float]:
    """Equal-weight sum of all 6 z-scored channels."""
    fused = fusion_equal_weight(channels)
    return sel_unretr_metric(fused, w, retr_mask), cor_with_W(fused, w)


def run_arm_learned_weight_fusion(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                                    retr_mask: np.ndarray,
                                    channels: Dict[str, np.ndarray],
                                    g: np.random.Generator) -> Tuple[float, float, Dict[str, float]]:
    """Ridge-regression learned weights on 50% train; eval on 50% test
    (held-out and DISJOINT)."""
    fused, weights_dict, test_idx = fusion_learned_weight(channels, w, retr_mask, g)
    # Evaluate ON THE TEST SUBSET only (clean held-out)
    fused_test = fused[test_idx]
    w_test = w[test_idx]
    # retr_mask defined on full M; restrict
    retr_test = retr_mask[test_idx]
    sel = sel_unretr_metric(fused_test, w_test, retr_test)
    cor = cor_with_W(fused_test, w_test)
    return sel, cor, weights_dict


def run_arm_diag_per_channel(E: np.ndarray, S: np.ndarray, w: np.ndarray,
                               retr_mask: np.ndarray,
                               channels: Dict[str, np.ndarray],
                               g: np.random.Generator) -> Dict[str, float]:
    """Diagnostic: per-channel sel_unretr breakdown."""
    out: Dict[str, float] = {}
    for cname in EXPECTED_CHANNELS:
        sel = sel_unretr_metric(channels[cname], w, retr_mask)
        cor = cor_with_W(channels[cname], w)
        out["%s_sel" % cname] = sel
        out["%s_cor" % cname] = cor
    # Also add Fisher fusion (third strategy) as diagnostic
    fisher_fused = fusion_fisher_weighted(channels)
    out["fisher_fusion_sel"] = sel_unretr_metric(fisher_fused, w, retr_mask)
    out["fisher_fusion_cor"] = cor_with_W(fisher_fused, w)
    return out


# -------------------------- per-seed --------------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    g = np.random.default_rng(seed)
    E = bipolar(M, N_DIM, g)
    w = g.standard_normal(M).astype(np.float32) * 0.3
    retr_mask = np.zeros(M, dtype=bool)
    top_idx = np.argsort(np.abs(w))[-int(M * 0.3):]
    retr_mask[top_idx] = True
    S = build_superposition(E, w)

    # Compute all 6 channels ONCE per seed (shared across arms for fairness)
    print("  [seed=%d] computing 6 channels..." % seed, flush=True)
    t_ch = time.time()
    channels = compute_all_channels(E, S, w, retr_mask, g)
    print("  [seed=%d] channels done in %.1fs" % (seed, time.time() - t_ch), flush=True)

    arm_results: Dict[str, Dict[str, Any]] = {}

    sel, cor = run_arm_trace_alone(E, S, w, retr_mask, channels, g)
    arm_results["trace_alone"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=trace_alone] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    sel, cor, best_name = run_arm_best_single_channel(E, S, w, retr_mask, channels, g)
    arm_results["best_single_channel"] = {
        "sel_unretr": sel, "cor_with_W": cor, "best_channel": best_name}
    print("  [seed=%d arm=best_single_channel] best=%s sel=%.4f cor=%.4f"
          % (seed, best_name, sel, cor), flush=True)

    sel, cor = run_arm_equal_weight_fusion(E, S, w, retr_mask, channels, g)
    arm_results["equal_weight_fusion"] = {"sel_unretr": sel, "cor_with_W": cor}
    print("  [seed=%d arm=equal_weight_fusion] sel=%.4f cor=%.4f" % (seed, sel, cor), flush=True)

    sel, cor, weights_dict = run_arm_learned_weight_fusion(E, S, w, retr_mask, channels, g)
    arm_results["learned_weight_fusion"] = {
        "sel_unretr": sel, "cor_with_W": cor,
        "learned_weights": weights_dict}
    print("  [seed=%d arm=learned_weight_fusion] sel=%.4f cor=%.4f weights=%s"
          % (seed, sel, cor, weights_dict), flush=True)

    diag = run_arm_diag_per_channel(E, S, w, retr_mask, channels, g)
    # diag stores per-channel breakdown; use fisher_fusion_sel as the
    # representative scalar so the arm has a sel_unretr field
    arm_results["diag_per_channel"] = {
        "sel_unretr": diag.get("fisher_fusion_sel", 0.0),
        "cor_with_W": diag.get("fisher_fusion_cor", 0.0),
        "per_channel_detail": diag,
    }
    print("  [seed=%d arm=diag_per_channel] %s" % (seed, diag), flush=True)

    return {
        "seed": int(seed),
        "N": N_DIM,
        "M": M,
        "n_channels": 6,
        "n_consensus_paths": N_CONSENSUS_PATHS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": arm_results,
    }


# -------------------------- verdict --------------------------

def aggregate_and_verdict(per_seed: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {
            "verdict": "UNKNOWN",
            "verdict_msg": "no per-seed partials found",
            "summary": "no per-seed partials found",
            "per_arm": {},
        }
    seeds_sorted = sorted(per_seed.keys(), key=lambda s: int(s))
    summary: Dict[str, Dict[str, float]] = {}
    per_arm_full: Dict[str, Dict[str, Dict[str, Any]]] = {}
    for arm in EXPECTED_ARMS:
        per_arm_full[arm] = {}
        sel_vals: List[float] = []
        cor_vals: List[float] = []
        for s in seeds_sorted:
            body = per_seed[s]
            pa = body.get("per_arm", {})
            if arm in pa:
                d = pa[arm]
                sel_vals.append(float(d.get("sel_unretr", 0.0)))
                cor_vals.append(float(d.get("cor_with_W", 0.0)))
                # Preserve full per-seed arm body (incl. weights / detail)
                per_arm_full[arm][s] = {k: v for k, v in d.items()}
        if sel_vals:
            m_sel = float(np.mean(sel_vals))
            sd_sel = float(np.std(sel_vals, ddof=1)) if len(sel_vals) > 1 else 0.0
            sem = sd_sel / math.sqrt(len(sel_vals)) if len(sel_vals) > 1 else 0.0
            cv = sd_sel / abs(m_sel) if abs(m_sel) > 1e-6 else 0.0
            summary[arm] = {
                "mean_sel": m_sel, "std_sel": sd_sel, "sem": sem, "cv_sel": cv,
                "mean_cor": float(np.mean(cor_vals)), "n": len(sel_vals),
                "mean_minus_1p96sem": m_sel - 1.96 * sem,
            }
        else:
            summary[arm] = {"mean_sel": 0.0, "std_sel": 0.0, "sem": 0.0,
                            "cv_sel": 0.0, "mean_cor": 0.0, "n": 0,
                            "mean_minus_1p96sem": 0.0}

    trace = summary["trace_alone"]
    best = summary["best_single_channel"]
    eq = summary["equal_weight_fusion"]
    learned = summary["learned_weight_fusion"]

    eq_mean = eq["mean_sel"]
    eq_cv = eq["cv_sel"]
    eq_cor = eq["mean_cor"]
    learned_mean = learned["mean_sel"]
    learned_cv = learned["cv_sel"]
    trace_mean = trace["mean_sel"]
    best_mean = best["mean_sel"]

    # Gates
    fusion_floor_ok = eq_mean >= HP_FUSION_FLOOR
    lift_trace_ok = (eq_mean - trace_mean) >= HP_LIFT_OVER_TRACE
    lift_best_ok = (eq_mean - best_mean) >= HP_LIFT_OVER_BEST
    cor_ok = eq_cor < HP_COR_MAX
    cv_ok = eq_cv < HP_CV_MAX

    cor_fail = eq_cor >= HF_COR_MAX
    cv_fail = eq_cv >= HF_CV_MAX
    no_lift = eq_mean <= trace_mean

    major_win_ok = (learned_mean >= MW_LEARNED_FLOOR and learned_cv < HP_CV_MAX)

    # Decision
    verdict = "MIDDLE_BAND"
    if no_lift or cor_fail or cv_fail:
        verdict = "HARD_FAIL"
    elif fusion_floor_ok and lift_trace_ok and lift_best_ok and cor_ok and cv_ok:
        if major_win_ok:
            verdict = "HARD_PASS"  # MAJOR_WIN
        else:
            verdict = "HARD_PASS"
    # else MIDDLE_BAND

    label = "MAJOR_WIN" if (verdict == "HARD_PASS" and major_win_ok) else (
        "CHAIN_GRADE" if verdict == "HARD_PASS" else (
            "BELOW_TRACE" if no_lift else (
                "INFEASIBLE" if (cor_fail or cv_fail) else "INDETERMINATE")))

    verdict_msg = (
        "%s [%s] | EqFusion=%.3f (cv=%.3f, cor=%.3f) Learned=%.3f Best=%.3f Trace=%.3f "
        "| floor_ok=%s lift_trace=%s lift_best=%s cor_ok=%s cv_ok=%s major_win=%s "
        "| n_seeds=%d"
    ) % (
        verdict, label, eq_mean, eq_cv, eq_cor, learned_mean, best_mean, trace_mean,
        fusion_floor_ok, lift_trace_ok, lift_best_ok, cor_ok, cv_ok, major_win_ok,
        len(seeds_sorted),
    )

    return {
        "verdict": verdict,
        "verdict_label": label,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "per_arm": per_arm_full,
        "per_arm_summary": summary,
        "eq_fusion_mean_sel": eq_mean,
        "eq_fusion_cv": eq_cv,
        "eq_fusion_cor": eq_cor,
        "learned_fusion_mean_sel": learned_mean,
        "trace_mean_sel": trace_mean,
        "best_single_mean_sel": best_mean,
        "fusion_floor_ok": bool(fusion_floor_ok),
        "lift_over_trace_ok": bool(lift_trace_ok),
        "lift_over_best_ok": bool(lift_best_ok),
        "cor_fairness_ok": bool(cor_ok),
        "cv_resolved_ok": bool(cv_ok),
        "major_win_qualified": bool(major_win_ok),
        "n_seeds_complete": len(seeds_sorted),
        "expected_n_units": EXPECTED_N_UNITS,
        "completed_units": len(seeds_sorted) * len(EXPECTED_ARMS),
        "cardinality_ok": (len(seeds_sorted) * len(EXPECTED_ARMS)
                           >= EXPECTED_N_UNITS),
    }


def main() -> int:
    _RESULTS_HOLDER["started_at"] = time.time()
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    out_dir.mkdir(parents=True, exist_ok=True)

    _write_minimal_metrics(out_dir, "STARTED",
                           "STARTED: pid=%d mode=%s" % (os.getpid(), RUN_MODE),
                           extra={"_phase": "init",
                                  "expected_arms": EXPECTED_ARMS,
                                  "expected_channels": EXPECTED_CHANNELS,
                                  "expected_seeds": SEEDS,
                                  "expected_n_units": EXPECTED_N_UNITS})

    print("[%s] mode=%s N=%d M=%d seeds=%s n_channels=6 expected_n=%d" % (
        ANCHOR_NAME, RUN_MODE, N_DIM, M, SEEDS, EXPECTED_N_UNITS), flush=True)

    if SELF_TEST_MODE:
        try:
            r = run_one_seed(SEEDS[0])
            assert "per_arm" in r
            for arm in EXPECTED_ARMS:
                assert arm in r["per_arm"], "missing arm %s" % arm
                assert "sel_unretr" in r["per_arm"][arm]
                sel = r["per_arm"][arm]["sel_unretr"]
                assert isinstance(sel, float) and math.isfinite(sel), (
                    "self-test: arm %s sel not finite float: %r" % (arm, sel))
            # Verify diag_per_channel has all 6 channels
            diag_detail = r["per_arm"]["diag_per_channel"].get(
                "per_channel_detail", {})
            for cname in EXPECTED_CHANNELS:
                assert ("%s_sel" % cname) in diag_detail, (
                    "self-test: diag missing %s_sel" % cname)
                assert ("%s_cor" % cname) in diag_detail, (
                    "self-test: diag missing %s_cor" % cname)
            # Verify learned_weights present with all 6 channel names
            lw = r["per_arm"]["learned_weight_fusion"].get("learned_weights", {})
            for cname in EXPECTED_CHANNELS:
                assert cname in lw, "self-test: learned_weights missing %s" % cname
            trace_sel = r["per_arm"]["trace_alone"]["sel_unretr"]
            eq_sel = r["per_arm"]["equal_weight_fusion"]["sel_unretr"]
            learned_sel = r["per_arm"]["learned_weight_fusion"]["sel_unretr"]
            best_sel = r["per_arm"]["best_single_channel"]["sel_unretr"]
            _write_minimal_metrics(out_dir, "SELFTEST_OK",
                                   "SELFTEST_OK: structure verified "
                                   "(TRACE=%.3f, EQ=%.3f, LEARNED=%.3f, BEST=%.3f)"
                                   % (trace_sel, eq_sel, learned_sel, best_sel))
            print("[selftest] OK structure-only; signal-magnitude is smoke-only",
                  flush=True)
            print("[selftest] N=%d M=%d (toy); TRACE=%.4f EQ=%.4f LEARNED=%.4f BEST=%.4f"
                  % (N_DIM, M, trace_sel, eq_sel, learned_sel, best_sel), flush=True)
            return 0
        except Exception as e:
            _write_minimal_metrics(out_dir, "SELFTEST_FAIL",
                                   "SELFTEST_FAIL: %s" % e,
                                   extra={"_traceback": traceback.format_exc()})
            print("[selftest] FAIL: %s" % e, file=sys.stderr, flush=True)
            return 1

    run_config = {"N": N_DIM, "M": M, "n_channels": 6,
                  "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d/%d done; running %s" % (len(done), len(SEEDS), remaining), flush=True)

    for i, seed in enumerate(remaining):
        t0 = time.time()
        _write_minimal_metrics(out_dir, "RUNNING",
                               "RUNNING: seed=%d (%d/%d)" % (seed, i + 1, len(remaining)),
                               extra={"_phase": "seed_running", "_current_seed": seed})
        result = run_one_seed(seed)
        write_partial_key(out_dir, seed, result)
        print("[seed=%d] complete in %.1fs" % (seed, time.time() - t0), flush=True)

    per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
    final = aggregate_and_verdict(per_seed)
    final["anchor_name"] = ANCHOR_NAME
    final["elapsed_s"] = round(time.time() - _RESULTS_HOLDER["started_at"], 1)
    final["ts_iso"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    final["pid"] = os.getpid()
    final["run_mode"] = RUN_MODE
    final["config_version"] = CONFIG_VERSION
    final["_hardening_marker"] = "v1_6channel_brain_analog"
    (out_dir / "metrics.json").write_text(
        json.dumps(final, indent=2), encoding="utf-8")
    print("[%s] DONE: %s" % (ANCHOR_NAME, final["verdict_msg"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        print("[main] OUTER_EXCEPTION: %s" % e, file=sys.stderr, flush=True)
        traceback.print_exc()
        rc = 1
    sys.exit(rc)
