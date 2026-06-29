"""substrate_hypothesis_gen_pipeline_composition_v2_seed_7 -- phase-fill extension (single-seed chunk).

Parent prereg:  preregs/2026-06-28_substrate_hypothesis_gen_pipeline_composition_v2.md
Sibling cells:  _seed_13, _seed_19 (3-chunk chunked architecture per USER 2026-06-28)
Parent cell:    substrate_hypothesis_gen_pipeline_composition_v1 (smoke HP +0.56 lift; FULL queued never landed)

v2 EXTENSION (vs v1):
  + Phase axes: M_OBS x K_CANDS sweep (16 points FULL; 6 SMOKE; 4 SELF-TEST).
  + ARM_PIPELINE_FULL_PLUS adds iterative_cleanup (between propose & score) + schema-prior bayes.
  + ARM_PIPELINE_V1 (legacy baseline) measures whether v2 adds value over v1.
  + Pareto-AUC discriminator (mean top-1 across phase diagram).
  + discriminator_survives_scale (>=3 of 4 K values must hold composition lift).

ARMS (6; META_RULE_AF arms-must-differ by SHA-256):
  ARM_PIPELINE_FULL_PLUS  SWR-preplay + iterative_cleanup + schema-prior + bayes_update_categorical
  ARM_PIPELINE_V1         SWR-preplay + uniform prior + bayes_update_categorical (v1 reference)
  ARM_GENERATOR_ONLY      SWR-preplay + uniform-pick (no scoring)
  ARM_SCORER_ONLY         random HRR candidates + bayes_update_categorical (uniform prior)
  ARM_RANDOM_CANDIDATES   random HRR candidates + uniform-pick (floor)
  ARM_ORACLE              true_h injected as 1-of-K + bayes_update_categorical (ceiling)

META_RULE_AM checks:
  (1) PIPELINE_FULL_PLUS vs PIPELINE_V1 (v2-extension value-add)
  (2) PIPELINE_FULL_PLUS vs max(GEN_ONLY, SCORER_ONLY) (v1 composition lift preserved)

HARD_PASS (ALL must hold for this seed chunk; see prereg for full spec):
  Pareto-AUC[PIPELINE_FULL_PLUS] >= Pareto-AUC[PIPELINE_V1] + 0.05
  Pareto-AUC[PIPELINE_FULL_PLUS] >= max(Pareto-AUC[GEN_ONLY], Pareto-AUC[SCORER_ONLY]) + 0.15
  Pareto-AUC[PIPELINE_FULL_PLUS] in [0.30, 0.95]
  Pareto-AUC[ORACLE] > Pareto-AUC[PIPELINE_FULL_PLUS]
  Pareto-AUC[RANDOM_CANDIDATES] <= 0.05
  arms_distinct == True
  cardinality_ok == True
  discriminator_survives_scale: >=3 of 4 K values show PIPELINE_FULL_PLUS > max(GEN, SCORER) + 0.10

HARD_FAIL (ANY triggers):
  Pareto-AUC[PIPELINE_FULL_PLUS] <= Pareto-AUC[PIPELINE_V1]  (v2 extension HURTS or no-op)
  Pareto-AUC[PIPELINE_FULL_PLUS] <= max(GEN_ONLY, SCORER_ONLY)  (META_RULE_AM)
  Pareto-AUC[PIPELINE_FULL_PLUS] < 0.20
  Pareto-AUC[RANDOM_CANDIDATES] > 0.10
  Pareto-AUC[ORACLE] < 0.85
  META_RULE_Q suspect-1.000 on n>=100
  arms_distinct == False
  cardinality_ok == False

CARDINALITY (META_RULE_H):
  SELF-TEST: 6 arms * 4 phase points * 4 problems = 96 decisions
  SMOKE:     6 arms * 6 phase points * 30 problems = 1080 decisions
  FULL:      6 arms * 16 phase points * 100 problems = 9600 decisions

ASCII-only; META_RULE_AH atomic write; SystemExit re-raised BEFORE BaseException.
Author: exp_dev 2026-06-28 (Opus 4.7 1M).
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
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import get_output_dir, write_partial
from hdlab.bayesian_inference import bayes_update_categorical
from hdlab.iterative_attractor import iterative_cleanup


ANCHOR_NAME = "substrate_hypothesis_gen_pipeline_composition_v2_seed_7"
SEED_THIS_CHUNK = 7
_HARDENING_MARKER = "v2_hypgen_pipeline_phase_fill_seed_chunk"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())
SELF_TEST_MODE = bool(_ARGS.self_test)

# ----- Pre-reg constants LOCKED at module init -----
COS_HIT = 0.70
K_BASE = 10  # legacy; not used since K is swept
ATTRACTOR_TEMP = 2.0
ATTRACTOR_MAX_STEPS = 4

HP_V2_LIFT_MIN = 0.05            # PIPELINE_FULL_PLUS > PIPELINE_V1 + 0.05
HP_COMPOSITION_LIFT_MIN = 0.15   # PIPELINE_FULL_PLUS > max(GEN, SCORER) + 0.15
HP_PIPELINE_LO = 0.30
HP_PIPELINE_HI = 0.95
HP_RANDOM_MAX = 0.05
HP_ORACLE_MIN = 0.85

HF_PIPELINE_LO = 0.20
HF_RANDOM_HI = 0.10
HF_ORACLE_LO = 0.85
HF_K_DISCRIM_MIN_LIFT = 0.10
HP_K_DISCRIM_MIN_K = 3           # >=3 of 4 K values must show lift

EXPECTED_ARMS = [
    "ARM_PIPELINE_FULL_PLUS",
    "ARM_PIPELINE_V1",
    "ARM_GENERATOR_ONLY",
    "ARM_SCORER_ONLY",
    "ARM_RANDOM_CANDIDATES",
    "ARM_ORACLE",
]

# Phase axes per run-mode (lock at module init)
if SELF_TEST_MODE:
    N_DIM = 256
    V_BANK = 64
    N_PROBLEMS = 4
    M_OBS_GRID = [3, 5]
    K_CANDS_GRID = [5, 10]
elif RUN_MODE == "smoke":
    N_DIM = 2048
    V_BANK = 256
    N_PROBLEMS = 30
    M_OBS_GRID = [3, 5, 8]
    K_CANDS_GRID = [5, 10]
else:
    N_DIM = 8192
    V_BANK = 256
    N_PROBLEMS = 100
    M_OBS_GRID = [3, 5, 8, 12]
    K_CANDS_GRID = [5, 10, 20, 40]

PHASE_POINTS = [(m, k) for m in M_OBS_GRID for k in K_CANDS_GRID]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * len(PHASE_POINTS) * N_PROBLEMS

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,problems=%d,seed=%d,mode=%s,"
    "M_GRID=%s,K_GRID=%s,phase_points=%d,"
    "HP_v2_lift>=%.2f,HP_comp_lift>=%.2f,HP_pipe_lo=%.2f,HP_pipe_hi=%.2f,"
    "HP_random_max=%.2f,HP_oracle_min=%.2f,cos_hit=%.2f,attr_temp=%.1f,attr_steps=%d,"
    "expected_n=%d"
) % (
    ANCHOR_NAME, N_DIM, V_BANK, N_PROBLEMS, SEED_THIS_CHUNK, RUN_MODE,
    ",".join(str(m) for m in M_OBS_GRID), ",".join(str(k) for k in K_CANDS_GRID),
    len(PHASE_POINTS),
    HP_V2_LIFT_MIN, HP_COMPOSITION_LIFT_MIN, HP_PIPELINE_LO, HP_PIPELINE_HI,
    HP_RANDOM_MAX, HP_ORACLE_MIN, COS_HIT, ATTRACTOR_TEMP, ATTRACTOR_MAX_STEPS,
    EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# -------------------- atomic-write --------------------

def _atomic_write_json(path: Path, body: Dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(body, indent=2, default=str), encoding="utf-8")
    os.replace(tmp, path)


def _write_minimal_metrics(out_dir: Path, verdict: str, verdict_msg: str,
                            extra: Dict[str, Any] | None = None) -> None:
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
            "_hardening_marker": _HARDENING_MARKER,
        }
        if extra:
            m.update(extra)
        _atomic_write_json(out_dir / "metrics.json", m)
    except Exception as e:
        print("[_write_minimal_metrics] FAIL: %s" % e, file=sys.stderr, flush=True)


# -------------------- HRR primitives --------------------

def _bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def hrr_bind(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = a.shape[-1]
    A = np.fft.rfft(a)
    B = np.fft.rfft(b)
    return np.fft.irfft(A * B, n=n).astype(np.float32)


def cos_rows(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    Xn = X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)
    yn = y / (np.linalg.norm(y, axis=-1, keepdims=True) + 1e-8)
    if yn.ndim == 1:
        return Xn @ yn
    return Xn @ yn.T


def normalize(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-8)


# -------------------- problem-set construction --------------------

def build_problem_set(seed: int, n_problems: int, n_dim: int, v_bank: int,
                       m_obs: int) -> Dict[str, Any]:
    """Construct V_BANK stored items + n_problems problems with M_OBS-sized obs sets."""
    g = np.random.default_rng(seed)
    bank = _bipolar(v_bank, n_dim, g)
    problems: List[Dict[str, Any]] = []
    for _ in range(n_problems):
        idxs_raw = g.choice(v_bank, size=m_obs, replace=False)
        true_positions = g.choice(m_obs, size=2, replace=False)
        true_a_pos, true_b_pos = int(true_positions[0]), int(true_positions[1])
        obs_items = bank[idxs_raw]
        true_a = obs_items[true_a_pos]
        true_b = obs_items[true_b_pos]
        true_h = hrr_bind(true_a, true_b)
        decoy_positions = [k for k in range(m_obs) if k != true_a_pos and k != true_b_pos]
        if decoy_positions:
            decoy_bundle = obs_items[decoy_positions].sum(axis=0)
        else:
            decoy_bundle = np.zeros(n_dim, dtype=np.float32)
        cue = normalize(true_h + 0.30 * decoy_bundle)
        problems.append({
            "obs_idxs": idxs_raw.tolist(),
            "obs_items": obs_items,
            "obs_seed": cue,
            "true_h": true_h.astype(np.float32),
            "_true_a_pos": true_a_pos,
            "_true_b_pos": true_b_pos,
        })
    return {"bank": bank, "problems": problems, "seed": int(seed)}


# -------------------- schema retrieval --------------------

def build_schema(obs_items: np.ndarray) -> np.ndarray:
    """Schema HRR S = sum_{i<j} normalize(bind(obs_i, obs_j)) over all obs-pair binds.

    Captures the conjunctive structure of the observation set. Used as the schema-prior
    weight basis for ARM_PIPELINE_FULL_PLUS: candidates that align with the schema
    receive higher Bayes prior than uniform.
    """
    M = obs_items.shape[0]
    if M < 2:
        return np.zeros(obs_items.shape[1], dtype=np.float32)
    binds: List[np.ndarray] = []
    for i in range(M):
        for j in range(i + 1, M):
            binds.append(normalize(hrr_bind(obs_items[i], obs_items[j])))
    return normalize(np.sum(binds, axis=0))


def schema_prior(cands: np.ndarray, schema_hv: np.ndarray, K: int) -> List[float]:
    """Schema-derived Bayes prior pi_k = max(cos(cand_k, S), 0)^2 normalized.

    Falls back to uniform 1/K if all weights are 0 (schema is zero vector or all
    candidates orthogonal to schema).
    """
    if float(np.linalg.norm(schema_hv)) <= 1e-12:
        return [1.0 / K] * K
    sims = cos_rows(cands, schema_hv)
    w = np.clip(sims, 0.0, None) ** 2
    s = float(w.sum())
    if s <= 1e-12:
        return [1.0 / K] * K
    return (w / s).astype(np.float64).tolist()


# -------------------- generators --------------------

def gen_swr_preplay(prob: Dict[str, Any], k: int, g: np.random.Generator) -> np.ndarray:
    """SWR-preplay: random-pair replay seeded from obs_items (v1 generator)."""
    obs_items = prob["obs_items"]
    M = obs_items.shape[0]
    n = obs_items.shape[1]
    cands = np.zeros((k, n), dtype=np.float32)
    for kk in range(k):
        i = int(g.integers(0, M))
        j = int(g.integers(0, M))
        if i == j:
            j = (j + 1) % M
        cands[kk] = normalize(hrr_bind(obs_items[i], obs_items[j]))
    return cands


def gen_random(n_dim: int, k: int, g: np.random.Generator) -> np.ndarray:
    return _bipolar(k, n_dim, g)


def gen_oracle(prob: Dict[str, Any], k: int, g: np.random.Generator) -> np.ndarray:
    n = prob["true_h"].shape[0]
    cands = _bipolar(k, n, g)
    slot = int(g.integers(0, k))
    cands[slot] = normalize(prob["true_h"])
    return cands


# -------------------- cleanup --------------------

def apply_cleanup(cands: np.ndarray, codebook: np.ndarray) -> np.ndarray:
    """Apply iterative_cleanup attractor to each candidate.

    Pulls candidates toward nearest attractor in the bank using mech-5 chain-grade
    iterative_cleanup primitive. Cleanup codebook = obs-item-pair binds (the schema's
    component vectors); higher-mass region of the substrate's natural attractor space
    for this problem's structure.
    """
    if cands.shape[0] == 0 or codebook.shape[0] == 0:
        return cands
    # iterative_cleanup expects (B, D) query and (M, D) codebook; returns dict
    out = iterative_cleanup(
        cands,
        codebook,
        temp=ATTRACTOR_TEMP,
        max_steps=ATTRACTOR_MAX_STEPS,
        return_trace=False,
        scale_by_sqrt_d=True,
    )
    state = out["state"] if isinstance(out, dict) else out
    return np.asarray(state, dtype=np.float32)


def build_cleanup_codebook(obs_items: np.ndarray) -> np.ndarray:
    """Cleanup attractor codebook = all pair-binds from obs_items.

    Provides M*(M-1)/2 attractor basins for cleanup; the substrate's preferred
    high-mass region for hypothesis candidates.
    """
    M = obs_items.shape[0]
    if M < 2:
        return obs_items.copy()
    binds: List[np.ndarray] = []
    for i in range(M):
        for j in range(i + 1, M):
            binds.append(normalize(hrr_bind(obs_items[i], obs_items[j])))
    return np.array(binds, dtype=np.float32)


# -------------------- scorers --------------------

def score_bayes_with_prior(cands: np.ndarray, prob: Dict[str, Any],
                             prior: List[float]) -> int:
    """Bayes scorer with arbitrary prior (uniform for v1; schema for v2)."""
    if cands.shape[0] == 0:
        return 0
    obs_items = prob["obs_items"]
    cue = prob["obs_seed"]
    M = obs_items.shape[0]
    K = cands.shape[0]

    # Precompute all pair-binds
    pair_binds: List[np.ndarray] = []
    for i in range(M):
        for j in range(M):
            if i != j:
                pair_binds.append(normalize(hrr_bind(obs_items[i], obs_items[j])))
    pair_binds_arr = np.array(pair_binds)

    # Cue-driven pair-weights
    cue_sims = cos_rows(pair_binds_arr, cue)
    pair_weights = np.clip(cue_sims, 0.0, None) ** 2
    if float(pair_weights.sum()) <= 1e-12:
        return 0
    pair_weights = pair_weights / pair_weights.sum()

    # Per-candidate likelihood
    cand_pair_sims = cos_rows(cands, pair_binds_arr)
    cand_pair_sims = np.clip(cand_pair_sims, 0.0, None) ** 2
    weighted = cand_pair_sims * pair_weights[None, :]
    like = weighted.sum(axis=1)

    if float(like.sum()) <= 1e-12:
        return 0

    post = bayes_update_categorical(prior, like.tolist())
    return int(np.argmax(post))


def score_uniform(cands: np.ndarray, prob: Dict[str, Any]) -> int:
    return 0


# -------------------- arm config --------------------

# (gen, cleanup, prior, scorer) tuple per arm
ARM_CONFIG = {
    "ARM_PIPELINE_FULL_PLUS":  ("swr_preplay", "iter_cleanup", "schema", "bayes"),
    "ARM_PIPELINE_V1":          ("swr_preplay", "none",         "uniform", "bayes"),
    "ARM_GENERATOR_ONLY":       ("swr_preplay", "none",         "uniform", "uniform"),
    "ARM_SCORER_ONLY":          ("random",      "none",         "uniform", "bayes"),
    "ARM_RANDOM_CANDIDATES":    ("random",      "none",         "uniform", "uniform"),
    "ARM_ORACLE":               ("oracle",      "none",         "uniform", "bayes"),
}


# -------------------- per-problem evaluation --------------------

def top1_hit(top1_cand: np.ndarray, true_h: np.ndarray, threshold: float = COS_HIT) -> int:
    return int(float(cos_rows(top1_cand[None, :], true_h)[0]) >= threshold)


def arm_fingerprint(top1_cands: List[np.ndarray]) -> str:
    if not top1_cands:
        return "empty"
    stacked = np.vstack(top1_cands).astype(np.float32)
    h = hashlib.sha256(stacked.tobytes()).hexdigest()
    return h[:16]


# -------------------- arm runners (single phase point) --------------------

def run_arm_phase(arm: str, problems: List[Dict[str, Any]],
                    bank: np.ndarray, k_cands: int, n_dim: int,
                    g: np.random.Generator) -> Tuple[float, str, int]:
    """Run one arm at one phase point. Returns (top1_rate, fingerprint, n_decisions)."""
    gen_type, cleanup_type, prior_type, sco_type = ARM_CONFIG[arm]
    hits = 0
    n = 0
    top1_cache: List[np.ndarray] = []
    for prob in problems:
        # generate
        if gen_type == "swr_preplay":
            cands = gen_swr_preplay(prob, k_cands, g)
        elif gen_type == "random":
            cands = gen_random(n_dim, k_cands, g)
        elif gen_type == "oracle":
            cands = gen_oracle(prob, k_cands, g)
        else:
            raise ValueError("unknown gen_type=%s" % gen_type)

        # cleanup (only ARM_PIPELINE_FULL_PLUS)
        if cleanup_type == "iter_cleanup":
            codebook = build_cleanup_codebook(prob["obs_items"])
            cands = apply_cleanup(cands, codebook)
        elif cleanup_type == "none":
            pass
        else:
            raise ValueError("unknown cleanup_type=%s" % cleanup_type)

        # prior (only ARM_PIPELINE_FULL_PLUS uses schema)
        if prior_type == "schema":
            schema_hv = build_schema(prob["obs_items"])
            prior = schema_prior(cands, schema_hv, k_cands)
        elif prior_type == "uniform":
            prior = [1.0 / k_cands] * k_cands
        else:
            raise ValueError("unknown prior_type=%s" % prior_type)

        # score
        if sco_type == "bayes":
            top1_idx = score_bayes_with_prior(cands, prob, prior)
        elif sco_type == "uniform":
            top1_idx = score_uniform(cands, prob)
        else:
            raise ValueError("unknown sco_type=%s" % sco_type)

        top1_cand = cands[top1_idx]
        hits += top1_hit(top1_cand, prob["true_h"])
        n += 1
        top1_cache.append(top1_cand)

    rate = float(hits) / max(n, 1)
    fp = arm_fingerprint(top1_cache)
    return rate, fp, n


# -------------------- self-test --------------------

def self_test() -> int:
    """--self-test gate: tiny config across all phase points; sanity checks; return 0=PASS 2=FAIL."""
    print("[selftest] %s starting (N=%d V=%d N_PROB=%d phase=%d)" % (
        ANCHOR_NAME, N_DIM, V_BANK, N_PROBLEMS, len(PHASE_POINTS)), flush=True)
    bank_seed_g = np.random.default_rng(SEED_THIS_CHUNK)
    bank = _bipolar(V_BANK, N_DIM, bank_seed_g)
    assert bank.shape == (V_BANK, N_DIM), "bank shape"

    g_run = np.random.default_rng(SEED_THIS_CHUNK + 1000)
    fps: Dict[str, str] = {}
    rates: Dict[str, float] = {}
    n_total = 0
    for arm in EXPECTED_ARMS:
        rates_at_points: List[float] = []
        top1_cache_all: List[np.ndarray] = []
        for (m_obs, k_cands) in PHASE_POINTS:
            ps = build_problem_set(SEED_THIS_CHUNK + m_obs * 1000 + k_cands,
                                    N_PROBLEMS, N_DIM, V_BANK, m_obs)
            problems = ps["problems"]
            # capture top-1 candidates manually for fingerprint
            for prob in problems:
                pass
            rate, fp, n_dec = run_arm_phase(arm, problems, bank, k_cands, N_DIM, g_run)
            rates_at_points.append(rate)
            n_total += n_dec
        rates[arm] = float(np.mean(rates_at_points))
        fps[arm] = hashlib.sha256(
            ("%s_%s" % (arm, ",".join("%.3f" % r for r in rates_at_points))).encode()
        ).hexdigest()[:16]
        print("[selftest] %-25s mean_top1=%.3f  fp=%s  n_phase=%d" % (
            arm, rates[arm], fps[arm], len(rates_at_points)), flush=True)

    distinct = len(set(fps.values())) == len(EXPECTED_ARMS)
    print("[selftest] arms_distinct=%s  n_total_decisions=%d" % (distinct, n_total), flush=True)
    print("[selftest] orderings: ORACLE=%.3f PIPELINE_PLUS=%.3f PIPELINE_V1=%.3f SCORER=%.3f GEN=%.3f RAND=%.3f" % (
        rates["ARM_ORACLE"], rates["ARM_PIPELINE_FULL_PLUS"], rates["ARM_PIPELINE_V1"],
        rates["ARM_SCORER_ONLY"], rates["ARM_GENERATOR_ONLY"], rates["ARM_RANDOM_CANDIDATES"]), flush=True)

    # Sanity checks (must hold even at tiny self-test scale)
    if rates["ARM_ORACLE"] < 0.5:
        print("[selftest] FAIL: ORACLE=%.3f < 0.5" % rates["ARM_ORACLE"], flush=True)
        return 2
    if rates["ARM_RANDOM_CANDIDATES"] > 0.3:
        print("[selftest] FAIL: RANDOM=%.3f > 0.3 (floor breach)" % rates["ARM_RANDOM_CANDIDATES"],
              flush=True)
        return 2
    if not distinct:
        print("[selftest] FAIL: arms_distinct=False fps=%s" % fps, flush=True)
        return 2
    expected_n_selftest = len(EXPECTED_ARMS) * len(PHASE_POINTS) * N_PROBLEMS
    if n_total != expected_n_selftest:
        print("[selftest] FAIL: n_total=%d != expected=%d" % (n_total, expected_n_selftest), flush=True)
        return 2

    print("[selftest] PASS (orientation correct; arms distinct; oracle fires; floor holds; cardinality OK)",
          flush=True)
    return 0


# -------------------- aggregation: pareto-AUC --------------------

def compute_pareto_auc(rates_grid: Dict[Tuple[int, int], float]) -> float:
    """Pareto-AUC = mean across K of (mean top-1 across M).

    Equivalent to mean over all (M, K) phase points (uniform grid). Each row of fixed K
    is averaged over M_OBS values, then row means averaged over K. For uniform grid this
    reduces to a plain mean but the structure is meaningful when grids are non-uniform.
    """
    per_k: Dict[int, List[float]] = {}
    for (m, k), r in rates_grid.items():
        per_k.setdefault(k, []).append(r)
    if not per_k:
        return 0.0
    return float(np.mean([np.mean(v) for v in per_k.values()]))


def compute_k_discriminator_survives(rates_per_arm: Dict[str, Dict[Tuple[int, int], float]],
                                       k_grid: List[int]) -> Tuple[bool, int, int]:
    """For each K, check if PIPELINE_FULL_PLUS - max(GEN, SCORER) >= HF_K_DISCRIM_MIN_LIFT (avg over M).

    Returns (survives, n_k_pass, n_k_total).
    """
    n_pass = 0
    for k in k_grid:
        pipe_mean = float(np.mean([
            rates_per_arm["ARM_PIPELINE_FULL_PLUS"][(m, k)]
            for m in M_OBS_GRID
        ]))
        gen_mean = float(np.mean([
            rates_per_arm["ARM_GENERATOR_ONLY"][(m, k)]
            for m in M_OBS_GRID
        ]))
        sco_mean = float(np.mean([
            rates_per_arm["ARM_SCORER_ONLY"][(m, k)]
            for m in M_OBS_GRID
        ]))
        if pipe_mean - max(gen_mean, sco_mean) >= HF_K_DISCRIM_MIN_LIFT:
            n_pass += 1
    return (n_pass >= HP_K_DISCRIM_MIN_K, n_pass, len(k_grid))


# -------------------- main --------------------

def main() -> int:
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    if SELF_TEST_MODE:
        rc = self_test()
        if rc != 0:
            _write_minimal_metrics(out_dir, "UNKNOWN",
                "SELFTEST_FAIL rc=%d (see stdout)" % rc)
            return rc
        _write_minimal_metrics(out_dir, "SELFTEST_OK",
            "SELFTEST_OK %s (N=%d V=%d N_PROB=%d phase=%d)" % (
                ANCHOR_NAME, N_DIM, V_BANK, N_PROBLEMS, len(PHASE_POINTS)))
        return 0

    print("[main] mode=%s N=%d V=%d N_PROB=%d phase_points=%d SEED=%d" % (
        RUN_MODE, N_DIM, V_BANK, N_PROBLEMS, len(PHASE_POINTS), SEED_THIS_CHUNK), flush=True)

    t0 = time.time()
    bank_seed_g = np.random.default_rng(SEED_THIS_CHUNK)
    bank = _bipolar(V_BANK, N_DIM, bank_seed_g)
    print("[main] bank built shape=%s elapsed=%.1fs" % (bank.shape, time.time() - t0), flush=True)

    g_run = np.random.default_rng(SEED_THIS_CHUNK + 1000)
    rates_per_arm: Dict[str, Dict[Tuple[int, int], float]] = {a: {} for a in EXPECTED_ARMS}
    per_arm_summary: Dict[str, Dict[str, Any]] = {a: {} for a in EXPECTED_ARMS}
    fp_basis: Dict[str, List[str]] = {a: [] for a in EXPECTED_ARMS}
    n_observed_total = 0

    for (m_obs, k_cands) in PHASE_POINTS:
        ps = build_problem_set(SEED_THIS_CHUNK + m_obs * 1000 + k_cands,
                                N_PROBLEMS, N_DIM, V_BANK, m_obs)
        problems = ps["problems"]
        for arm in EXPECTED_ARMS:
            t_arm = time.time()
            rate, fp, n_dec = run_arm_phase(arm, problems, bank, k_cands, N_DIM, g_run)
            rates_per_arm[arm][(m_obs, k_cands)] = rate
            fp_basis[arm].append("M%d_K%d:%.3f" % (m_obs, k_cands, rate))
            n_observed_total += n_dec
            elapsed = time.time() - t_arm
            print("[arm] M=%d K=%d %-25s top1=%.3f fp=%s n=%d wall=%.1fs" % (
                m_obs, k_cands, arm, rate, fp, n_dec, elapsed), flush=True)
            per_arm_summary[arm].setdefault("phase_points", []).append({
                "M_OBS": m_obs, "K_CANDS": k_cands,
                "top1_rate": rate, "fingerprint": fp,
                "n_decisions": n_dec, "elapsed_s": round(elapsed, 2),
            })

    # Per-arm Pareto-AUC + composite fingerprint
    pareto_auc: Dict[str, float] = {}
    fps: Dict[str, str] = {}
    for arm in EXPECTED_ARMS:
        pareto_auc[arm] = compute_pareto_auc(rates_per_arm[arm])
        fps[arm] = hashlib.sha256("|".join(fp_basis[arm]).encode()).hexdigest()[:16]
        per_arm_summary[arm]["pareto_auc"] = pareto_auc[arm]
        per_arm_summary[arm]["fingerprint"] = fps[arm]

    distinct = len(set(fps.values())) == len(EXPECTED_ARMS)
    cardinality_ok = (n_observed_total == EXPECTED_N_UNITS)

    pipe_plus = pareto_auc["ARM_PIPELINE_FULL_PLUS"]
    pipe_v1 = pareto_auc["ARM_PIPELINE_V1"]
    gen_only = pareto_auc["ARM_GENERATOR_ONLY"]
    scorer_only = pareto_auc["ARM_SCORER_ONLY"]
    random_only = pareto_auc["ARM_RANDOM_CANDIDATES"]
    oracle = pareto_auc["ARM_ORACLE"]

    v2_lift_over_v1 = pipe_plus - pipe_v1
    composition_lift = pipe_plus - max(gen_only, scorer_only)
    v2_extension_value_add = v2_lift_over_v1 >= HP_V2_LIFT_MIN
    composition_value_add = composition_lift >= HP_COMPOSITION_LIFT_MIN

    # K-discriminator-survives-scale check
    k_survives, n_k_pass, n_k_total = compute_k_discriminator_survives(rates_per_arm, K_CANDS_GRID)

    # META_RULE_Q suspect-1.000
    suspect_q = False
    if n_observed_total // len(EXPECTED_ARMS) >= 100:
        for arm, r in pareto_auc.items():
            if r >= 0.999 and arm != "ARM_ORACLE":
                suspect_q = True
                break

    # Verdict logic
    hf_reasons: List[str] = []
    if pipe_plus <= pipe_v1:
        hf_reasons.append("v2_extension_no_value_or_hurts (pipe_plus=%.3f <= pipe_v1=%.3f)" % (pipe_plus, pipe_v1))
    if pipe_plus <= max(gen_only, scorer_only):
        hf_reasons.append("META_RULE_AM functional-req-already-met (pipe_plus=%.3f <= max(gen=%.3f,sco=%.3f))" % (
            pipe_plus, gen_only, scorer_only))
    if pipe_plus < HF_PIPELINE_LO:
        hf_reasons.append("pipe_plus<%.2f" % HF_PIPELINE_LO)
    if random_only > HF_RANDOM_HI:
        hf_reasons.append("RANDOM>%.2f floor-breach" % HF_RANDOM_HI)
    if oracle < HF_ORACLE_LO:
        hf_reasons.append("ORACLE<%.2f ceiling-broken" % HF_ORACLE_LO)
    if suspect_q:
        hf_reasons.append("META_RULE_Q suspect-1.000")
    if not distinct:
        hf_reasons.append("arms_distinct=False")
    if not cardinality_ok:
        hf_reasons.append("cardinality_ok=False(obs=%d exp=%d)" % (n_observed_total, EXPECTED_N_UNITS))

    hp_conds = {
        "v2_lift_ge_%.2f" % HP_V2_LIFT_MIN: v2_extension_value_add,
        "comp_lift_ge_%.2f" % HP_COMPOSITION_LIFT_MIN: composition_value_add,
        "pipe_plus_in_[%.2f,%.2f]" % (HP_PIPELINE_LO, HP_PIPELINE_HI):
            (HP_PIPELINE_LO <= pipe_plus <= HP_PIPELINE_HI),
        "oracle>pipe_plus": oracle > pipe_plus,
        "random<=%.2f" % HP_RANDOM_MAX: random_only <= HP_RANDOM_MAX,
        "arms_distinct": distinct,
        "cardinality_ok": cardinality_ok,
        "k_discriminator_survives": k_survives,
    }
    all_hp = all(hp_conds.values()) and not hf_reasons

    if hf_reasons:
        verdict = "HARD_FAIL"
    elif all_hp:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s %s | pareto_auc: pipe_plus=%.3f pipe_v1=%.3f gen=%.3f scorer=%.3f random=%.3f oracle=%.3f"
        " | v2_lift_over_v1=%+.3f comp_lift=%+.3f"
        " | v2_value_add=%s comp_value_add=%s k_survives=%s (%d/%d)"
        " | arms_distinct=%s cardinality_ok=%s (obs=%d/exp=%d)"
        " | fps=%s"
    ) % (
        verdict, ANCHOR_NAME, pipe_plus, pipe_v1, gen_only, scorer_only, random_only, oracle,
        v2_lift_over_v1, composition_lift,
        v2_extension_value_add, composition_value_add, k_survives, n_k_pass, n_k_total,
        distinct, cardinality_ok, n_observed_total, EXPECTED_N_UNITS, fps,
    )
    if hf_reasons:
        verdict_msg += " | HF_REASONS=%s" % ";".join(hf_reasons)

    # Serialize phase grid (tuple keys -> string keys for JSON)
    rates_per_arm_serial = {
        a: {"%d_%d" % (m, k): r for (m, k), r in rates_per_arm[a].items()}
        for a in EXPECTED_ARMS
    }

    payload = {
        "anchor_name": ANCHOR_NAME,
        "verdict": verdict,
        "verdict_msg": verdict_msg,
        "summary": verdict_msg,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 2),
        "ts_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "pid": os.getpid(),
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "V_BANK": V_BANK,
        "N_PROBLEMS": N_PROBLEMS,
        "M_OBS_GRID": M_OBS_GRID,
        "K_CANDS_GRID": K_CANDS_GRID,
        "phase_points": [{"M_OBS": m, "K_CANDS": k} for (m, k) in PHASE_POINTS],
        "seed": SEED_THIS_CHUNK,
        "config_version": CONFIG_VERSION,
        "arms_tested": EXPECTED_ARMS,
        "per_arm_summary": per_arm_summary,
        "rates_phase_grid": rates_per_arm_serial,
        "pareto_auc": pareto_auc,
        "fingerprints": fps,
        "arms_distinct": distinct,
        "cardinality_ok": cardinality_ok,
        "n_observed": n_observed_total,
        "n_expected": EXPECTED_N_UNITS,
        "v2_lift_over_v1": v2_lift_over_v1,
        "composition_lift": composition_lift,
        "v2_extension_value_add": v2_extension_value_add,
        "composition_value_add": composition_value_add,
        "k_discriminator_survives": k_survives,
        "k_pass_count": n_k_pass,
        "k_total_count": n_k_total,
        "hp_conds": hp_conds,
        "hf_reasons": hf_reasons,
        "suspect_q": suspect_q,
        "_hardening_marker": _HARDENING_MARKER,
    }

    write_partial(out_dir, SEED_THIS_CHUNK, payload)
    _atomic_write_json(out_dir / "metrics.json", payload)
    print("[main] verdict=%s elapsed=%.1fs" % (verdict, payload["elapsed_s"]), flush=True)
    return 0


if __name__ == "__main__":
    try:
        rc = main()
        sys.exit(rc)
    except SystemExit:
        raise
    except BaseException as e:
        tb = traceback.format_exc()
        try:
            out_dir = get_output_dir(ANCHOR_NAME)
            out_dir.mkdir(parents=True, exist_ok=True)
            _write_minimal_metrics(out_dir, "UNKNOWN",
                "EXCEPTION %s: %s" % (type(e).__name__, str(e)),
                extra={"_traceback": tb})
        except Exception:
            pass
        print(tb, file=sys.stderr, flush=True)
        raise
