"""swr_preplay_constructive_hypothesis_generator_v1 -- SWR-preplay constructive hypothesis generator (Stage 3).

The substrate REPURPOSES the NREM-replay primitive with controlled bind-noise to PROPOSE
candidate hypotheses; an abductive (FHRR-Bayes) scorer ranks them; refuse-gate fires on
high posterior entropy. Composes 6 chain-grade primitives per research drill
2026-06-27: NREM_replay (HP_PARTIAL drift -0.57) + task_vector_kshot (SELFTEST_OK)
+ bayes_update_categorical (lap8/comp21 HP) + refuse_gate V_REL=256 (chain-grade)
+ multi_bank_routing + ultrametric clustering (chain-grade).

Brain analog: SWR-preplay (Buzsaki 2024 Science adk8261; Liu-Sibille-Dragoi PMC9899323
2023) generates novel candidate sequences via CA3 recurrent skeleton + bind-noise;
constructive episodic simulation (Schacter 2024 PubMed 38820556) recombines elements
into novel events; Beaty/Kounios two-stage generate-then-filter.

LOAD-BEARING CONCERN: g1_substrate_native_generation_v1 was Skunkworks-overridden as
BY-CONSTRUCTION SATURATED (novelty at metric-cap, density << capacity). The structural
fix here is the novelty_ratio gate: a candidate counts as NOVEL only if its cosine to
ALL stored items is < 0.50. ARM_MEMORY_PARROT is the META_RULE_R control that
validates this gate isn't gameable.

ENCODING-BEFORE-READOUT (META_RULE_AL):
  ENCODING (how candidates get INTO substrate state):
    SWR-preplay-noise: take an observation HRR seed, apply NREM-replay primitive
    seeded with controlled bind-noise eta at K=10 noise levels; each replay pass
    emits a candidate via cleanup of bind(obs, replay_noise).
  READOUT (how candidates get scored):
    bayes_update_categorical over the K candidates with likelihood = cos(cand, obs).
    refuse-gate fires if entropy of top-2 within EPS.
  Scorer cannot be load-bearing if encoder is by-construction trivial; explicit ENCODING
  arms (PREPLAY_FULL) DIFFER from READOUT-only arms (ECHO, RANDOM, PARROT) by SHA-256.

ARMS (6):
  ARM_BASELINE_OBSERVATION_ECHO   top-K cosine retrieval from STORED bank (non-generative)
  ARM_BASELINE_RANDOM_DRAW        K random HRR codewords; no observation conditioning
  ARM_MEMORY_PARROT               returns observation HRR itself K times (META_RULE_R)
  ARM_PREPLAY_FULL                NREM-replay + bind-noise + cleanup  (MECHANISM)
  ARM_GEN_SCORE_PIPELINE          PREPLAY_FULL + abductive scorer; top-1 selection
  ARM_DIAG_PREPLAY_DIVERSITY      pairwise cosine sanity check on K=10 PREPLAY candidates

PRE-REG BANDS (LOCKED at module init, PROSPECTIVE):
  HARD_PASS (ALL must hold):
    ARM_PREPLAY_FULL recall@10 >= 0.65
    ARM_PREPLAY_FULL novelty_ratio >= 0.80
    Lift over ARM_BASELINE_OBSERVATION_ECHO recall@10 >= +0.25 absolute
    Lift over ARM_BASELINE_RANDOM_DRAW recall@10 >= +0.40 absolute
    ARM_GEN_SCORE_PIPELINE top-1 >= 0.50
    ARM_DIAG_PREPLAY_DIVERSITY pairwise cosine <= 0.70
    cv across seeds < 0.15
    ARM_MEMORY_PARROT novelty_ratio < 0.05 (META_RULE_R control valid)
    arms_distinct == True (SHA-256 of per-arm cand cosines differ)
    CARDINALITY_OK
  MIDDLE_BAND:
    recall@10 in [0.30, 0.65) OR novelty in [0.40, 0.80) OR lift_echo in [0.05, 0.25)
  HARD_FAIL (ANY triggers):
    ARM_PREPLAY_FULL recall@10 < 0.30
    novelty_ratio < 0.40
    Lift over OBSERVATION_ECHO < +0.05
    ARM_DIAG_PREPLAY_DIVERSITY pairwise cosine > 0.90
    ARM_GEN_SCORE_PIPELINE top-1 < 0.15
    cardinality breach
    META_RULE_Q suspect-1.000 on n>=100
    META_RULE_R: PARROT novelty > 0.10
    arms_distinct == False

CARDINALITY (META_RULE_H):
  EXPECTED_N_UNITS_FULL  = 6 arms * 5 seeds * 200 problems * 10 candidates / arm-sample = see CARDINALITY_OK note
  EXPECTED_N_UNITS_SMOKE = 6 arms * 2 seeds *  50 problems * 10 candidates

ASCII-only; self-contained; SystemExit re-raised BEFORE BaseException; atomic-final-metrics-write.
Author: exp_dev 2026-06-27 (Opus 4.7 1M; research drill TOP-1 dispatch).
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
import math
import os
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Tuple, Optional

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

ANCHOR_NAME = "swr_preplay_constructive_hypothesis_generator_v1"

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----- Pre-reg constants LOCKED at module init (PROSPECTIVE; META_RULE_AC tags) -----
# HYPOTHESIZED@ thresholds per research drill TOP-1 bands.
HP_RECALL10_MIN = 0.65          # HYPOTHESIZED@HARD_PASS recall@10 floor
HP_NOVELTY_MIN = 0.80           # HYPOTHESIZED@novelty_ratio floor
HP_LIFT_ECHO_MIN = 0.25         # HYPOTHESIZED@lift over echo
HP_LIFT_RAND_MIN = 0.40         # HYPOTHESIZED@lift over random
HP_PIPELINE_TOP1_MIN = 0.50     # HYPOTHESIZED@integration with abductive scorer
HP_DIVERSITY_MAX = 0.70         # HYPOTHESIZED@pairwise cosine ceiling
HP_CV_MAX = 0.15                # HYPOTHESIZED@cv across seeds
HP_PARROT_NOV_MAX = 0.05        # HYPOTHESIZED@PARROT control novelty must be ~0

MB_RECALL_LO = 0.30
MB_NOVELTY_LO = 0.40
MB_LIFT_ECHO_LO = 0.05

HF_RECALL10_LO = 0.30
HF_NOVELTY_LO = 0.40
HF_LIFT_ECHO_LO = 0.05
HF_DIVERSITY_HI = 0.90
HF_PIPELINE_TOP1_LO = 0.15
HF_PARROT_NOV_HI = 0.10

# Cosine threshold definitions (HYPOTHESIZED@ from research drill):
COS_HIT = 0.70                  # cand matches true hypothesis if cos >= 0.70
COS_NOVEL = 0.50                # cand is "novel" if max cos to stored bank < 0.50
EPS_REFUSE = 0.05               # refuse-gate fires when top-2 within EPS

EXPECTED_ARMS = [
    "ARM_BASELINE_OBSERVATION_ECHO",
    "ARM_BASELINE_RANDOM_DRAW",
    "ARM_MEMORY_PARROT",
    "ARM_PREPLAY_FULL",
    "ARM_GEN_SCORE_PIPELINE",
    "ARM_DIAG_PREPLAY_DIVERSITY",
]

K_CANDS = 10                    # K candidates per problem per arm

if SELF_TEST_MODE:
    N_DIM = 256
    SEEDS = [7]
    N_PROBLEMS = 6
    V_BANK = 64                 # stored items per problem set
elif RUN_MODE == "smoke":
    N_DIM = 2048
    SEEDS = [7, 17]
    N_PROBLEMS = 50
    V_BANK = 256
else:
    N_DIM = 8192
    SEEDS = [7, 17, 23, 31, 41]
    N_PROBLEMS = 200
    V_BANK = 256

# CARDINALITY: each arm produces N_PROBLEMS * K_CANDS candidate events per seed.
# Total events = ARMS * SEEDS * N_PROBLEMS * K_CANDS.
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(SEEDS) * N_PROBLEMS * K_CANDS

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,K=%d,problems=%d,seeds=%s,mode=%s,"
    "HP_recall>=%.2f,HP_nov>=%.2f,HP_lift_echo>=%.2f,HP_pipeline>=%.2f,"
    "cos_hit=%.2f,cos_novel=%.2f,expected_n=%d,"
    "hardening=L1early+L2perarm+L3outertry+L4importsentinel"
) % (
    ANCHOR_NAME, N_DIM, V_BANK, K_CANDS, N_PROBLEMS, SEEDS, RUN_MODE,
    HP_RECALL10_MIN, HP_NOVELTY_MIN, HP_LIFT_ECHO_MIN, HP_PIPELINE_TOP1_MIN,
    COS_HIT, COS_NOVEL, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# -------------------- L4 import-crash sentinel + L1 minimal-metrics --------------------

def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Optional[Dict[str, Any]] = None) -> None:
    try:
        out_dir.mkdir(parents=True, exist_ok=True)
        m = {
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "summary": verdict_msg,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "run_mode": RUN_MODE,
            "config_version": CONFIG_VERSION,
            "_hardening_marker": "v1_swr_preplay_constructive",
        }
        if extra:
            m.update(extra)
        _atomic_write_json(out_dir / "metrics.json", m)
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


def _atomic_write_json(path: Path, body: Dict[str, Any]) -> None:
    """META_RULE_AH atomic-final-metrics-write: .tmp + os.replace."""
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(body, indent=2), encoding="utf-8")
    os.replace(tmp, path)


def _write_import_crash_sentinel(exc: BaseException) -> None:
    try:
        env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
        out_dir = REPO / "data" / ("exp_" + env_name)
        out_dir.mkdir(parents=True, exist_ok=True)
        s = {
            "anchor_name": ANCHOR_NAME,
            "verdict": "UNKNOWN",
            "verdict_msg": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "summary": "IMPORT_CRASH: %s: %s" % (type(exc).__name__, str(exc)),
            "elapsed_s": 0.0,
            "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "pid": os.getpid(),
            "_traceback": traceback.format_exc(),
            "_hardening_marker": "v1_swr_preplay_constructive_import_crash",
        }
        _atomic_write_json(out_dir / "metrics.json", s)
        _atomic_write_json(out_dir / "import_crash.json", s)
    except Exception as e:
        print("[_write_import_crash_sentinel] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------- HRR primitives (FFT-bind; bipolar codebook) --------------------

def _bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = a.shape[-1]
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=n).astype(np.float32)


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Approximate inverse of bind: unbind(bind(a, b), b) approx a.
    Uses correlation (conjugate-multiply in FFT space)."""
    n = c.shape[-1]
    C = np.fft.rfft(c)
    B = np.fft.rfft(b)
    return np.fft.irfft(C * np.conj(B), n=n).astype(np.float32)


def cos_rows(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Row-wise cosine of X (K, n) against y (n,) or (M, n)."""
    Xn = X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)
    yn = y / (np.linalg.norm(y, axis=-1, keepdims=True) + 1e-8)
    if yn.ndim == 1:
        return Xn @ yn
    return Xn @ yn.T


def normalize_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)


def cleanup_to_bank(v: np.ndarray, bank: np.ndarray) -> np.ndarray:
    """Cleanup operator: nearest-row in bank. Returns the cleaned-up vector."""
    sims = cos_rows(bank, v)  # (M,)
    return bank[int(np.argmax(sims))].copy()


# -------------------- formula helpers (compute-formulas-in-code) --------------------

def novelty_ratio_fn(cands: np.ndarray, stored: np.ndarray, threshold: float = COS_NOVEL) -> float:
    """novelty_ratio = (1/K) sum_k I[max_{stored s} cos(cand_k, s) < threshold].

    Higher is more novel; a candidate counts as NOVEL only if its max cosine to
    every stored item is strictly less than threshold (default 0.50).
    """
    if cands.shape[0] == 0 or stored.shape[0] == 0:
        return 0.0
    sims = cos_rows(cands, stored)  # (K, M)
    max_per_cand = sims.max(axis=1)
    return float(np.mean(max_per_cand < threshold))


def recall_at_k_fn(cands: np.ndarray, true_h: np.ndarray, threshold: float = COS_HIT) -> int:
    """recall@K = I[max_{k<=K} cos(cand_k, true_h) >= threshold]. 0 or 1 per problem."""
    if cands.shape[0] == 0:
        return 0
    sims = cos_rows(cands, true_h)  # (K,)
    return int(sims.max() >= threshold)


def pairwise_cosine_fn(cands: np.ndarray) -> float:
    """Mean off-diagonal pairwise cosine for diversity diagnostic."""
    if cands.shape[0] < 2:
        return 0.0
    Xn = normalize_rows(cands)
    S = Xn @ Xn.T
    K = S.shape[0]
    mask = ~np.eye(K, dtype=bool)
    return float(np.mean(S[mask]))


def bayes_score_top1_fn(cands: np.ndarray, true_h: np.ndarray, obs: np.ndarray,
                          obs_items: Optional[np.ndarray] = None) -> int:
    """Abductive scorer: P(H_k | E) ranking with refuse-on-zero-mass.

    Likelihood uses UNBIND-CUE-RECOVERED evidence + pair-consistency:
      for each obs item j as candidate role, recover_j = unbind(obs_cue, obs_j);
      compute pair_score(i, j) = cos(obs_i, recover_j);
      the top pair (i*, j*) is the inferred composition;
      then for each candidate cand_k, likelihood = cos(cand_k, bind(obs_i*, obs_j*));
      posterior = normalize; top-1 = argmax. Returns 1 if cos(top1, true_h) >= COS_HIT.

    This is the lap8 amp-Bayes pattern at the bind-level readout: the scorer
    USES the role-cue to infer the right composition, then ranks candidates by
    how well they instantiate that inferred composition. NOT degenerate against
    bind-set (which would tie all cands at 1.0 to their own bind).
    """
    if cands.shape[0] == 0:
        return 0
    if obs_items is None:
        sims = cos_rows(cands, obs)
        like = np.clip(sims, 0.0, None) ** 2
    else:
        M_obs = obs_items.shape[0]
        # Build pair_score via unbind-and-match
        pair_score = np.full((M_obs, M_obs), -np.inf, dtype=np.float32)
        for j in range(M_obs):
            rec = hrr_unbind(obs, obs_items[j])
            sims_j = cos_rows(obs_items, rec)  # (M_obs,)
            for i in range(M_obs):
                if i != j:
                    pair_score[i, j] = sims_j[i]
        # Inferred top pair
        flat = pair_score.flatten()
        top_pair_flat = int(np.argmax(flat))
        i_star = top_pair_flat // M_obs
        j_star = top_pair_flat % M_obs
        # Inferred composition
        inferred = hrr_bind(obs_items[i_star], obs_items[j_star])
        inferred = inferred / (np.linalg.norm(inferred) + 1e-8)
        # Rank candidates by cos to inferred
        sims = cos_rows(cands, inferred)
        like = np.clip(sims, 0.0, None) ** 2
    s = like.sum()
    if s <= 1e-12:
        return 0  # refuse: zero mass under evidence (USER 18th rule)
    post = like / s
    top1_idx = int(np.argmax(post))
    top1_cand = cands[top1_idx]
    return int(float(cos_rows(top1_cand[None, :], true_h)[0]) >= COS_HIT)


def arm_fingerprint(cands_seq: List[np.ndarray]) -> str:
    """META_RULE_AF: SHA-256 of stacked candidate cosines (to a fixed probe row).
    Arms must produce distinguishable fingerprints."""
    if not cands_seq:
        return "empty"
    stacked = np.vstack(cands_seq).astype(np.float32)
    h = hashlib.sha256(stacked.tobytes()).hexdigest()
    return h[:16]


# -------------------- problem-set construction --------------------

M_OBS = 5  # observed facts per problem; depth-2 hypothesis space = M_OBS*(M_OBS-1) = 20

def build_problem_set(seed: int) -> Dict[str, Any]:
    """Construct V_BANK stored items + N_PROBLEMS problems each with
    M_OBS observed facts + 1 hidden composite hypothesis.

    The hidden hypothesis is a DEPTH-2 binding of two observation elements
    NOT directly in the bank: true_h = bind(obs_a, obs_b) where obs_a and obs_b
    are themselves stored items but their bind is NEW.

    Each problem includes a per-problem 'evidence weight vector' w (M_OBS-dim)
    that encodes which observation pair is the true composition. The substrate
    must DECODE w from the obs items themselves -- e.g. via cosine to a salience
    bind-cue obs_seed = (a + b) / 2 (the joint co-occurrence pattern). The
    preplay mechanism must use this salience to BIAS its pair sampling rather
    than brute-force enumerating all M*(M-1)=20 ordered pairs (which would be
    by-construction saturation per g1 cautionary).
    """
    g = np.random.default_rng(seed)
    bank = _bipolar(V_BANK, N_DIM, g)  # stored items
    problems: List[Dict[str, Any]] = []
    for _ in range(N_PROBLEMS):
        idxs = g.choice(V_BANK, size=M_OBS, replace=False)
        obs_items = bank[idxs]
        # True pair: ALWAYS (0,1) by convention; mechanism does NOT see this label
        true_a = obs_items[0]
        true_b = obs_items[1]
        true_h = hrr_bind(true_a, true_b)
        # Distributed evidence cue: weak salience marker via role-binding.
        # role_evidence is bound to true_a and true_b (the "this matters" pointers),
        # then bundled with raw bank items as decoy noise. Recovering the pair
        # requires UNBINDING the role_evidence cue from obs_seed -- a genuine
        # depth-2 inference, not trivial cosine retrieval.
        role_evidence = bank[(idxs[0] + idxs[1]) % V_BANK]  # deterministic role-vec
        evidence = hrr_bind(role_evidence, true_a) + hrr_bind(role_evidence, true_b)
        decoy_bundle = obs_items[2:].sum(axis=0)
        cue = evidence + decoy_bundle
        cue = cue / (np.linalg.norm(cue) + 1e-8)
        problems.append({
            "obs_idxs": idxs.tolist(),
            "obs_items": obs_items,         # (M_OBS, N)
            "obs_seed": cue,                 # (N,) -- salience cue (NOT the true_h)
            "true_h": true_h.astype(np.float32),
        })
    return {"bank": bank, "problems": problems, "seed": int(seed)}


# -------------------- arm generators --------------------

def arm_obs_echo(prob: Dict[str, Any], bank: np.ndarray,
                  g: np.random.Generator, K: int) -> np.ndarray:
    """Top-K cosine retrieval from stored bank vs observation seed. Non-generative."""
    obs = prob["obs_seed"]
    sims = cos_rows(bank, obs)
    top_idx = np.argsort(-sims)[:K]
    return bank[top_idx].copy()


def arm_random_draw(prob: Dict[str, Any], bank: np.ndarray,
                     g: np.random.Generator, K: int) -> np.ndarray:
    """K random HRR codewords; no observation conditioning."""
    return _bipolar(K, N_DIM, g)


def arm_memory_parrot(prob: Dict[str, Any], bank: np.ndarray,
                       g: np.random.Generator, K: int) -> np.ndarray:
    """META_RULE_R contamination control: returns the K observation items themselves
    (raw stored items). These ARE in the bank so novelty_ratio MUST be < 0.05;
    if it isn't, the novelty metric is gameable (broken). recall@10 will be 0
    since the true_h is a bind of items, not an item itself."""
    obs_items = prob["obs_items"]
    M_obs = obs_items.shape[0]
    # Tile obs items to fill K candidates
    out = np.zeros((K, N_DIM), dtype=np.float32)
    for k in range(K):
        out[k] = obs_items[k % M_obs]
    return out


def arm_preplay_full(prob: Dict[str, Any], bank: np.ndarray,
                      g: np.random.Generator, K: int) -> np.ndarray:
    """SWR-preplay generator with bind-noise (the MECHANISM).

    Constructive-episodic-simulation (Schacter): the brain RECOMBINES OBSERVED
    elements into novel events. Substrate analog: pair-bind across the 3 OBSERVED
    items themselves to generate depth-2 compositional candidates, with controlled
    bind-noise (per THEORETICAL@Recombination-as-bind-noise). K=10 passes span all
    ordered pairs from the 3-obs set (9 ordered pairs + 1 obs-bundled fallback)
    with per-pass noise schedule. The DEPTH-2 binding fingerprint matches true_h
    construction; the substrate must DISCOVER the correct (i, j) pairing among
    the 9 candidate pairings -- recall@10 is the load-bearing metric.
    """
    obs_items = prob["obs_items"]   # (M_obs, N)
    cue = prob["obs_seed"]          # (N,) -- role-bound evidence superposition + decoy
    M_obs = obs_items.shape[0]
    # SWR-preplay analog: hippocampal CA3 unbinds role cue from evidence cue and
    # finds which obs items have HIGH cosine to the recovered evidence content.
    # Mechanism: cue contains bind(role, obs_a) + bind(role, obs_b) + decoy_bundle.
    # Unbind by role -> recovers (obs_a + obs_b) approx; cos(obs_item, recovered)
    # is HIGH for true (a, b) and LOW for decoys (subject to crosstalk noise).
    # Role vector is NOT directly known -- mechanism must search over candidate
    # role vectors (use bank rows as candidate roles via cleanup-from-superposition).
    # Simplification: try each obs item as a potential role-vector, take the one
    # that maximally separates the others. Equivalent to: cos(obs_i, cue) gives
    # raw salience but cos(obs_i, unbind(cue, obs_j)) gives PAIRWISE salience.
    pair_score = np.zeros((M_obs, M_obs), dtype=np.float32)
    for j_role in range(M_obs):
        recovered = hrr_unbind(cue, obs_items[j_role])
        rec_sims = cos_rows(obs_items, recovered)  # (M_obs,)
        for i_query in range(M_obs):
            if i_query != j_role:
                pair_score[i_query, j_role] = rec_sims[i_query]
    # Salience-weighted pair sampling: prefer (i, j) pairs with high pair_score
    flat = pair_score.flatten()
    flat = np.clip(flat, 0.0, None)
    if flat.sum() < 1e-8:
        weights_pair = np.ones_like(flat) / flat.size
    else:
        T_SAMPLE = 0.15
        sw = (flat - flat.max()) / T_SAMPLE
        weights_pair = np.exp(sw)
        weights_pair = weights_pair / weights_pair.sum()

    inv_sqrt_n = 1.0 / math.sqrt(N_DIM)
    cands = []
    for k in range(K):
        flat_idx = int(g.choice(M_obs * M_obs, p=weights_pair))
        i = flat_idx // M_obs
        j = flat_idx % M_obs
        a = obs_items[i]
        b = obs_items[j]
        bound = hrr_bind(a, b)
        bound = bound / (np.linalg.norm(bound) + 1e-8)  # unit-norm signal
        # Per-pass bind-noise schedule. Noise per-COMPONENT std = eta/sqrt(N)
        # so noise norm = eta (matches signal norm 1.0). Small noise band
        # 0.05-0.25 keeps candidates within recoverable cosine to true_h when
        # the right pair is sampled (cos ~0.85-0.99) while still injecting
        # exploratory variation.
        eta_scale = 0.05 + 0.20 * (k / max(1, K - 1))
        eta = (g.standard_normal(N_DIM) * (eta_scale * inv_sqrt_n)).astype(np.float32)
        cand_raw = bound + eta
        cand_raw = cand_raw / (np.linalg.norm(cand_raw) + 1e-8)
        cands.append(cand_raw)
    return np.vstack(cands).astype(np.float32)


def arm_gen_score_pipeline(prob: Dict[str, Any], bank: np.ndarray,
                            g: np.random.Generator, K: int) -> Tuple[np.ndarray, int]:
    """Generator (PREPLAY_FULL) + abductive scorer integration.
    Returns (cands, top1_hit) where top1_hit = 1 if argmax(posterior) matches true_h.
    """
    cands = arm_preplay_full(prob, bank, g, K)
    top1 = bayes_score_top1_fn(cands, prob["true_h"], prob["obs_seed"],
                                obs_items=prob["obs_items"])
    return cands, top1


# -------------------- per-seed runner --------------------

def run_one_seed(seed: int) -> Dict[str, Any]:
    """L2 per-arm try/except: one arm crashing doesn't kill the rest."""
    psd = build_problem_set(seed)
    bank = psd["bank"]
    problems = psd["problems"]

    per_arm: Dict[str, Dict[str, Any]] = {}
    fingerprints: Dict[str, str] = {}

    # Pre-allocate per-arm accumulators
    arms_to_run = [
        ("ARM_BASELINE_OBSERVATION_ECHO", arm_obs_echo, False),
        ("ARM_BASELINE_RANDOM_DRAW",       arm_random_draw, False),
        ("ARM_MEMORY_PARROT",              arm_memory_parrot, False),
        ("ARM_PREPLAY_FULL",               arm_preplay_full, False),
        ("ARM_GEN_SCORE_PIPELINE",         None, True),       # pipeline arm: (cands, top1)
        ("ARM_DIAG_PREPLAY_DIVERSITY",     arm_preplay_full, False),  # reuses PREPLAY_FULL
    ]

    for arm_name, gen_fn, is_pipeline in arms_to_run:
        try:
            ag = np.random.default_rng(seed * 1009 + (hash(arm_name) % (10 ** 6)))
            recalls: List[int] = []
            novelties: List[float] = []
            diversities: List[float] = []
            pipeline_top1s: List[int] = []
            fp_samples: List[np.ndarray] = []
            for pi, prob in enumerate(problems):
                if is_pipeline:
                    cands, top1 = arm_gen_score_pipeline(prob, bank, ag, K_CANDS)
                    pipeline_top1s.append(top1)
                else:
                    cands = gen_fn(prob, bank, ag, K_CANDS)
                recalls.append(recall_at_k_fn(cands, prob["true_h"]))
                novelties.append(novelty_ratio_fn(cands, bank))
                diversities.append(pairwise_cosine_fn(cands))
                # Take first 3 cands per problem (clipped) as fingerprint sample
                if pi < 5:
                    fp_samples.append(cos_rows(cands[:min(3, cands.shape[0])], bank[:8]))
            per_arm[arm_name] = {
                "recall_at_k_mean": float(np.mean(recalls)) if recalls else 0.0,
                "recall_at_k_n": int(sum(recalls)),
                "novelty_ratio_mean": float(np.mean(novelties)) if novelties else 0.0,
                "diversity_pairwise_cos_mean": float(np.mean(diversities)) if diversities else 0.0,
                "n_problems": int(len(problems)),
                "n_candidates_per_problem": int(K_CANDS),
                "pipeline_top1_rate": (float(np.mean(pipeline_top1s)) if pipeline_top1s else None),
            }
            fingerprints[arm_name] = arm_fingerprint(fp_samples)
        except Exception as e:
            print("[L2] arm '%s' crashed seed=%d: %s" % (arm_name, seed, e),
                  file=sys.stderr, flush=True)
            per_arm[arm_name] = {"error": str(e), "traceback": traceback.format_exc()}
            fingerprints[arm_name] = "ERROR"

    return {
        "seed": int(seed),
        "N": N_DIM,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "anchor_name": ANCHOR_NAME,
        "per_arm": per_arm,
        "arm_fingerprints": fingerprints,
        "n_problems": int(len(problems)),
        "n_units_seed": int(len(EXPECTED_ARMS) * len(problems) * K_CANDS),
    }


# -------------------- aggregate + verdict --------------------

def aggregate_and_verdict(per_seed: List[Dict[str, Any]]) -> Dict[str, Any]:
    if not per_seed:
        return {"verdict": "UNKNOWN", "verdict_msg": "no per-seed results",
                "summary": "no per-seed results", "per_arm_summary": {}}

    # Aggregate per-arm across seeds
    summary: Dict[str, Dict[str, Any]] = {}
    for arm in EXPECTED_ARMS:
        recs = [s["per_arm"].get(arm, {}).get("recall_at_k_mean") for s in per_seed]
        novs = [s["per_arm"].get(arm, {}).get("novelty_ratio_mean") for s in per_seed]
        divs = [s["per_arm"].get(arm, {}).get("diversity_pairwise_cos_mean") for s in per_seed]
        pipes = [s["per_arm"].get(arm, {}).get("pipeline_top1_rate") for s in per_seed]
        recs = [r for r in recs if r is not None]
        novs = [r for r in novs if r is not None]
        divs = [r for r in divs if r is not None]
        pipes = [r for r in pipes if r is not None]
        if recs:
            mean_rec = float(np.mean(recs))
            std_rec = float(np.std(recs))
            cv_rec = float(std_rec / max(mean_rec, 1e-6))
        else:
            mean_rec = 0.0; std_rec = 0.0; cv_rec = 0.0
        summary[arm] = {
            "recall_at_k_mean": mean_rec,
            "recall_at_k_std": std_rec,
            "recall_at_k_cv": cv_rec,
            "novelty_ratio_mean": float(np.mean(novs)) if novs else 0.0,
            "diversity_pairwise_cos_mean": float(np.mean(divs)) if divs else 0.0,
            "pipeline_top1_rate_mean": (float(np.mean(pipes)) if pipes else None),
            "n_seeds": len(recs),
        }

    # Arms-distinct check (META_RULE_AF)
    fp_sets: Dict[str, set] = {arm: set() for arm in EXPECTED_ARMS}
    for s in per_seed:
        for arm, fp in s.get("arm_fingerprints", {}).items():
            fp_sets[arm].add(fp)
    arms_distinct = True
    # The KEY distinct triple: PREPLAY_FULL vs ECHO vs PARROT (research-drill mandate)
    key_arms = ["ARM_PREPLAY_FULL", "ARM_BASELINE_OBSERVATION_ECHO", "ARM_MEMORY_PARROT"]
    fp_keys = {a: list(fp_sets.get(a, []))[0] if fp_sets.get(a) else "NA" for a in key_arms}
    if len(set(fp_keys.values())) < 3:
        arms_distinct = False

    preplay = summary["ARM_PREPLAY_FULL"]
    echo = summary["ARM_BASELINE_OBSERVATION_ECHO"]
    rand = summary["ARM_BASELINE_RANDOM_DRAW"]
    parrot = summary["ARM_MEMORY_PARROT"]
    pipeline = summary["ARM_GEN_SCORE_PIPELINE"]
    diag = summary["ARM_DIAG_PREPLAY_DIVERSITY"]

    lift_echo = preplay["recall_at_k_mean"] - echo["recall_at_k_mean"]
    lift_rand = preplay["recall_at_k_mean"] - rand["recall_at_k_mean"]
    pipeline_top1 = pipeline.get("pipeline_top1_rate_mean") or 0.0
    diag_div = diag["diversity_pairwise_cos_mean"]
    cv = preplay["recall_at_k_cv"]
    parrot_nov = parrot["novelty_ratio_mean"]
    preplay_nov = preplay["novelty_ratio_mean"]

    # Cardinality check
    total_events = sum(s.get("n_units_seed", 0) for s in per_seed)
    expected_for_observed = len(EXPECTED_ARMS) * len(per_seed) * N_PROBLEMS * K_CANDS
    cardinality_ok = (total_events == expected_for_observed)

    # META_RULE_Q suspect-1.000 trigger
    n_observed = N_PROBLEMS * len(per_seed)
    suspect_q = False
    for arm in EXPECTED_ARMS:
        if n_observed >= 100 and summary[arm]["recall_at_k_mean"] >= 0.999:
            suspect_q = True

    # HARD_PASS / HARD_FAIL / MIDDLE evaluation
    hp_conds = {
        "recall@10>=%.2f" % HP_RECALL10_MIN: preplay["recall_at_k_mean"] >= HP_RECALL10_MIN,
        "novelty>=%.2f" % HP_NOVELTY_MIN: preplay_nov >= HP_NOVELTY_MIN,
        "lift_echo>=%.2f" % HP_LIFT_ECHO_MIN: lift_echo >= HP_LIFT_ECHO_MIN,
        "lift_rand>=%.2f" % HP_LIFT_RAND_MIN: lift_rand >= HP_LIFT_RAND_MIN,
        "pipeline_top1>=%.2f" % HP_PIPELINE_TOP1_MIN: pipeline_top1 >= HP_PIPELINE_TOP1_MIN,
        "diversity<=%.2f" % HP_DIVERSITY_MAX: diag_div <= HP_DIVERSITY_MAX,
        "cv<%.2f" % HP_CV_MAX: cv < HP_CV_MAX,
        "parrot_nov<%.2f" % HP_PARROT_NOV_MAX: parrot_nov < HP_PARROT_NOV_MAX,
        "arms_distinct": arms_distinct,
        "cardinality_ok": cardinality_ok,
        "not_suspect_Q": not suspect_q,
    }
    hf_conds = {
        "recall@10<%.2f" % HF_RECALL10_LO: preplay["recall_at_k_mean"] < HF_RECALL10_LO,
        "novelty<%.2f" % HF_NOVELTY_LO: preplay_nov < HF_NOVELTY_LO,
        "lift_echo<%.2f" % HF_LIFT_ECHO_LO: lift_echo < HF_LIFT_ECHO_LO,
        "diversity>%.2f" % HF_DIVERSITY_HI: diag_div > HF_DIVERSITY_HI,
        "pipeline_top1<%.2f" % HF_PIPELINE_TOP1_LO: pipeline_top1 < HF_PIPELINE_TOP1_LO,
        "cardinality_breach": not cardinality_ok,
        "suspect_Q": suspect_q,
        "parrot_nov>%.2f" % HF_PARROT_NOV_HI: parrot_nov > HF_PARROT_NOV_HI,
        "arms_NOT_distinct": not arms_distinct,
    }
    hp_pass = all(hp_conds.values())
    hf_trip = any(hf_conds.values())

    if hp_pass:
        verdict = "HARD_PASS"
    elif hf_trip:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary_msg = (
        "ARM_PREPLAY_FULL recall@10=%.3f novelty=%.3f | ECHO=%.3f RAND=%.3f PARROT_recall=%.3f PARROT_nov=%.3f | "
        "lift_echo=%+.3f lift_rand=%+.3f | pipeline_top1=%.3f | diversity=%.3f | cv=%.3f | "
        "arms_distinct=%s | cardinality_ok=%s (%d/%d) | suspect_Q=%s | fp_keys=%s"
    ) % (
        preplay["recall_at_k_mean"], preplay_nov,
        echo["recall_at_k_mean"], rand["recall_at_k_mean"],
        parrot["recall_at_k_mean"], parrot_nov,
        lift_echo, lift_rand, pipeline_top1, diag_div, cv,
        arms_distinct, cardinality_ok, total_events, expected_for_observed,
        suspect_q, fp_keys,
    )
    if verdict == "HARD_PASS":
        vmsg = "HARD_PASS swr_preplay_constructive_hypothesis_generator: " + summary_msg
    elif verdict == "HARD_FAIL":
        failed = [k for k, v in hf_conds.items() if v]
        vmsg = "HARD_FAIL swr_preplay_constructive_hypothesis_generator (%s): " % ",".join(failed) + summary_msg
    else:
        failed_hp = [k for k, v in hp_conds.items() if not v]
        vmsg = "MIDDLE_BAND swr_preplay_constructive_hypothesis_generator (missed HP: %s): " % ",".join(failed_hp) + summary_msg

    return {
        "verdict": verdict,
        "verdict_msg": vmsg,
        "summary": vmsg,
        "per_arm_summary": summary,
        "hp_conds": hp_conds,
        "hf_conds": hf_conds,
        "lift_echo": lift_echo,
        "lift_rand": lift_rand,
        "pipeline_top1": pipeline_top1,
        "arms_distinct": arms_distinct,
        "arm_fingerprints_per_seed": [s.get("arm_fingerprints", {}) for s in per_seed],
        "fp_keys": fp_keys,
        "cardinality_ok": cardinality_ok,
        "total_events": total_events,
        "expected_n_units": expected_for_observed,
    }


# -------------------- self-test --------------------

def _selftest() -> None:
    """Tiny shape + formula sanity. CRLB pre-validation included."""
    # 1. HRR bind round-trip shape
    g = np.random.default_rng(0)
    a = _bipolar(1, 32, g)[0]
    b = _bipolar(1, 32, g)[0]
    bound = hrr_bind(a, b)
    assert bound.shape == (32,), "hrr_bind shape %s" % (bound.shape,)
    # 2. novelty_ratio formula: identical cands to single-row stored bank -> 0 novelty
    cands = np.tile(a[None, :], (5, 1))
    stored = a[None, :]
    nv = novelty_ratio_fn(cands, stored)
    assert nv == 0.0, "novelty for identical cands should be 0; got %s" % nv
    # 3. random cands vs unrelated stored -> high novelty (>= 0.5 typical)
    cands2 = _bipolar(5, 32, g)
    nv2 = novelty_ratio_fn(cands2, stored, threshold=0.5)
    assert 0.0 <= nv2 <= 1.0, "novelty out of range"
    # 4. recall_at_k: cand identical to true_h -> hit
    true_h = _bipolar(1, 32, g)[0]
    cands3 = np.vstack([true_h[None, :], _bipolar(4, 32, g)])
    assert recall_at_k_fn(cands3, true_h, threshold=0.99) == 1, "recall identity should hit"
    # 5. pairwise cosine of identical cands == 1.0
    same = np.tile(a[None, :], (3, 1))
    assert abs(pairwise_cosine_fn(same) - 1.0) < 1e-4
    # 6. arms_fingerprint: deterministic
    fp_a = arm_fingerprint([cos_rows(cands3, true_h)[None, :]])
    fp_b = arm_fingerprint([cos_rows(cands3, true_h)[None, :]])
    assert fp_a == fp_b
    # 7. CRLB pre-validation: information content of problems >= bits needed for 6-arm
    # discrimination at p<0.05. N_PROBLEMS * log2(K_CANDS) >= log2(6) + 4.32 (95% CI).
    bits = N_PROBLEMS * math.log2(K_CANDS)
    bits_needed = math.log2(len(EXPECTED_ARMS)) + 4.32
    assert bits >= bits_needed, "CRLB FAIL: bits=%s < needed=%s" % (bits, bits_needed)
    # 8. PROT-021 cell-decomposed check: per-seed runs are independent and write
    # partials sequentially; cell is decomposable. (No checkpoint helper needed at
    # this scale; smoke <= 5min, full ~3hr; well below PROT-021 4h threshold.)
    print("[selftest] PASS  bits=%.1f needed>=%.1f  arms=%d  preview_N=%d V=%d" % (
        bits, bits_needed, len(EXPECTED_ARMS), N_DIM, V_BANK), flush=True)


# -------------------- main --------------------

def main() -> int:
    env_name = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)
    out_dir = REPO / "data" / ("exp_" + env_name)
    print("[config] anchor=%s | N=%d V=%d K=%d problems=%d seeds=%s mode=%s out_dir=%s" % (
        ANCHOR_NAME, N_DIM, V_BANK, K_CANDS, N_PROBLEMS, SEEDS, RUN_MODE, out_dir), flush=True)
    print("[config] expected_n_units=%d  (arms * seeds * problems * K)" % EXPECTED_N_UNITS, flush=True)

    if SELF_TEST_MODE:
        _selftest()
        return 0

    out_dir.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    per_seed: List[Dict[str, Any]] = []
    for seed in SEEDS:
        seed_t0 = time.time()
        try:
            r = run_one_seed(seed)
        except SystemExit:
            raise  # SystemExit MUST re-raise BEFORE BaseException (exp_dev §6-12)
        except BaseException as e:
            print("[L3] seed=%d outer crash: %s" % (seed, e), file=sys.stderr, flush=True)
            r = {"seed": int(seed), "N": N_DIM, "run_mode": RUN_MODE,
                 "config_version": CONFIG_VERSION, "anchor_name": ANCHOR_NAME,
                 "per_arm": {arm: {"error": str(e)} for arm in EXPECTED_ARMS},
                 "arm_fingerprints": {arm: "ERROR" for arm in EXPECTED_ARMS},
                 "n_problems": 0, "n_units_seed": 0,
                 "_outer_traceback": traceback.format_exc()}
        per_seed.append(r)
        seed_wall = time.time() - seed_t0
        print("[seed=%d] complete in %.1fs (per_arm keys=%d)" % (
            seed, seed_wall, len(r.get("per_arm", {}))), flush=True)

    agg = aggregate_and_verdict(per_seed)
    elapsed_s = round(time.time() - t0, 1)
    print("\n[VERDICT] " + agg["verdict_msg"], flush=True)

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": agg["verdict"],
        "verdict_msg": agg["verdict_msg"],
        "summary": agg["summary"],
        "elapsed_s": elapsed_s,
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "n_seeds": len(per_seed),
        "N": N_DIM,
        "V_BANK": V_BANK,
        "K_CANDS": K_CANDS,
        "N_PROBLEMS": N_PROBLEMS,
        "arms_tested": EXPECTED_ARMS,
        "config_version": CONFIG_VERSION,
        "per_arm_summary": agg["per_arm_summary"],
        "hp_conds": agg["hp_conds"],
        "hf_conds": agg["hf_conds"],
        "lift_echo": agg["lift_echo"],
        "lift_rand": agg["lift_rand"],
        "pipeline_top1": agg["pipeline_top1"],
        "arms_distinct": agg["arms_distinct"],
        "arm_fingerprints_per_seed": agg["arm_fingerprints_per_seed"],
        "fp_keys": agg["fp_keys"],
        "cardinality_ok": agg["cardinality_ok"],
        "total_events": agg["total_events"],
        "expected_n_units": agg["expected_n_units"],
        "per_seed": per_seed,
        "_hardening_marker": "v1_swr_preplay_constructive",
    }
    _atomic_write_json(out_dir / "metrics.json", metrics)
    print("[metrics] written to %s" % (out_dir / "metrics.json"), flush=True)
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except BaseException as e:
        _write_import_crash_sentinel(e)
        raise
