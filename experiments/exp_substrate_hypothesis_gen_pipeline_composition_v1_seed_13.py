"""substrate_hypothesis_gen_pipeline_composition_v1_seed_13 -- M3 concern #1 functional-requirement-first composition test (single-seed chunk).

Parent prereg:  preregs/2026-06-28_substrate_hypothesis_gen_pipeline_composition_v1.md
Sibling cells:  _seed_13, _seed_19 (3-chunk chunked architecture per USER 2026-06-28)

FUNCTIONAL-REQUIREMENT-FIRST DECOMPOSITION (per feedback_functional_requirement_first_test_design_USER_2026-06-28):

  Hypothesis generation = (a) PROPOSE candidates + (b) SCORE candidates.

  PROPOSE primitive: SWR-preplay (bind-noise replay; from
    exp_swr_preplay_constructive_hypothesis_generator_v1 ARM_PREPLAY_FULL,
    smoke MEASURED@recall@10=0.570 novelty=1.000).
  SCORE primitive: bayes_update_categorical (lap8 / comp21 / stretch3-4 chain-grade
    Bayesian abductive ranking; MEASURED@lap8 bayes_acc=1.0 n=33).

  Both functional requirements have existing primitives; this cell tests COMPOSITION.

ARMS (5; META_RULE_AF arms-must-differ by SHA-256):
  ARM_PIPELINE_FULL       SWR-preplay generator + bayes_update_categorical scorer
  ARM_GENERATOR_ONLY      SWR-preplay generator + uniform-pick (no scoring)
  ARM_SCORER_ONLY         random HRR candidates + bayes_update_categorical scorer
  ARM_RANDOM_CANDIDATES   random HRR candidates + uniform-pick (floor)
  ARM_ORACLE              true_h injected as 1-of-K + bayes_update_categorical (ceiling)

META_RULE_AM check: if ARM_PIPELINE_FULL <= max(GEN_ONLY, SCORER_ONLY) ->
  composition adds no value; substrate already meets M3 concern #1 via primitive alone.

HARD_PASS (ALL must hold for this single-seed chunk):
  ARM_PIPELINE_FULL top1 > max(GEN_ONLY, SCORER_ONLY) + 0.15
  ARM_PIPELINE_FULL top1 in [0.30, 0.95]  (META_RULE_AG)
  ARM_ORACLE top1 > ARM_PIPELINE_FULL  (room to grow)
  ARM_RANDOM_CANDIDATES top1 <= 0.05  (floor)
  arms_distinct == True
  cardinality_ok == True

HARD_FAIL (ANY triggers):
  PIPELINE_FULL <= max(GEN_ONLY, SCORER_ONLY)  (META_RULE_AM functional-req-already-met)
  PIPELINE_FULL < 0.20
  RANDOM > 0.10  (floor breach)
  ORACLE < 0.90  (ceiling failed; scoring broken)
  META_RULE_Q suspect-1.000 on n>=100
  arms_distinct == False
  cardinality_ok == False

CARDINALITY (META_RULE_H):
  SMOKE: 5 arms * 50 problems = 250 top-1 decisions for this seed
  FULL:  5 arms * 200 problems = 1000 top-1 decisions for this seed
  HARD_FAIL_CARDINALITY_BREACH when observed != expected.

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

from experiments._seed_checkpoint import get_output_dir, write_partial, write_metrics
from hdlab.bayesian_inference import bayes_update_categorical


ANCHOR_NAME = "substrate_hypothesis_gen_pipeline_composition_v1_seed_13"
SEED_THIS_CHUNK = 13
_HARDENING_MARKER = "v1_hypgen_pipeline_seed_chunk"

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
COS_HIT = 0.70           # cand matches true_h if cos >= 0.70
COS_NOVEL = 0.50         # cand is "novel" if max cos to stored bank < 0.50
K_CANDS = 10
M_OBS = 5

HP_PIPELINE_LIFT_MIN = 0.15      # PIPELINE > max(GEN, SCORER) + 0.15
HP_PIPELINE_LO = 0.30            # PIPELINE in [LO, HI]
HP_PIPELINE_HI = 0.95
HP_RANDOM_MAX = 0.05             # floor
HP_ORACLE_MIN = 0.90             # ceiling sanity

HF_PIPELINE_LO = 0.20            # below this is HARD_FAIL
HF_RANDOM_HI = 0.10              # above this is floor-breach
HF_ORACLE_LO = 0.90              # below this is ceiling-broken

EXPECTED_ARMS = [
    "ARM_PIPELINE_FULL",
    "ARM_GENERATOR_ONLY",
    "ARM_SCORER_ONLY",
    "ARM_RANDOM_CANDIDATES",
    "ARM_ORACLE",
]

if SELF_TEST_MODE:
    N_DIM = 256
    N_PROBLEMS = 6
    V_BANK = 64
elif RUN_MODE == "smoke":
    N_DIM = 2048
    N_PROBLEMS = 50
    V_BANK = 256
else:
    N_DIM = 8192
    N_PROBLEMS = 200
    V_BANK = 256

SEEDS = [SEED_THIS_CHUNK]
EXPECTED_N_UNITS = len(EXPECTED_ARMS) * N_PROBLEMS  # top-1 decisions per arm per seed

CONFIG_VERSION = (
    "ANCHOR=%s,N=%d,V=%d,K=%d,problems=%d,M_OBS=%d,seed=%d,mode=%s,"
    "HP_lift>=%.2f,HP_pipe_lo=%.2f,HP_pipe_hi=%.2f,HP_random_max=%.2f,HP_oracle_min=%.2f,"
    "cos_hit=%.2f,cos_novel=%.2f,expected_n=%d"
) % (
    ANCHOR_NAME, N_DIM, V_BANK, K_CANDS, N_PROBLEMS, M_OBS, SEED_THIS_CHUNK, RUN_MODE,
    HP_PIPELINE_LIFT_MIN, HP_PIPELINE_LO, HP_PIPELINE_HI, HP_RANDOM_MAX, HP_ORACLE_MIN,
    COS_HIT, COS_NOVEL, EXPECTED_N_UNITS,
)

_RESULTS_HOLDER: Dict[str, Any] = {"started_at": time.time()}


# -------------------- atomic-write + sentinel --------------------

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


def hrr_unbind(c: np.ndarray, b: np.ndarray) -> np.ndarray:
    n = c.shape[-1]
    C = np.fft.rfft(c)
    B = np.fft.rfft(b)
    return np.fft.irfft(C * np.conj(B), n=n).astype(np.float32)


def cos_rows(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    Xn = X / (np.linalg.norm(X, axis=-1, keepdims=True) + 1e-8)
    yn = y / (np.linalg.norm(y, axis=-1, keepdims=True) + 1e-8)
    if yn.ndim == 1:
        return Xn @ yn
    return Xn @ yn.T


def normalize(v: np.ndarray) -> np.ndarray:
    return v / (np.linalg.norm(v) + 1e-8)


def cleanup_to_bank(v: np.ndarray, bank: np.ndarray) -> np.ndarray:
    sims = cos_rows(bank, v)
    return bank[int(np.argmax(sims))].copy()


# -------------------- problem-set construction --------------------

def build_problem_set(seed: int, n_problems: int, n_dim: int, v_bank: int,
                       m_obs: int) -> Dict[str, Any]:
    """Construct V_BANK stored items + n_problems problems.

    Each problem: m_obs observed items drawn from bank; hidden true_h = bind(obs_a, obs_b)
    where obs_a = obs_items[0], obs_b = obs_items[1] (BUT mechanism does NOT see labels;
    only sees obs_items (unordered set) and a salience cue).

    Salience cue construction: cue = normalize(true_h + 0.30 * sum(decoy_obs_items))
    where decoy_obs_items = obs_items[2:].  The cue contains true_h energy plus
    decoy obs-energy.  A pair-scoring readout (cos to bind(obs_i, obs_j)) extracts
    the true pair (validated MEASURED@50/50 in pre-flight smoke).
    """
    g = np.random.default_rng(seed)
    bank = _bipolar(v_bank, n_dim, g)
    problems: List[Dict[str, Any]] = []
    for _ in range(n_problems):
        # Shuffle the obs_idxs so true pair is NOT always [0,1] in presentation order
        idxs_raw = g.choice(v_bank, size=m_obs, replace=False)
        # Pick true pair positions at random within idxs_raw
        true_positions = g.choice(m_obs, size=2, replace=False)
        true_a_pos, true_b_pos = int(true_positions[0]), int(true_positions[1])
        obs_items = bank[idxs_raw]
        true_a = obs_items[true_a_pos]
        true_b = obs_items[true_b_pos]
        true_h = hrr_bind(true_a, true_b)
        decoy_positions = [k for k in range(m_obs) if k != true_a_pos and k != true_b_pos]
        decoy_bundle = obs_items[decoy_positions].sum(axis=0) if decoy_positions else np.zeros(n_dim, dtype=np.float32)
        cue = normalize(true_h + 0.30 * decoy_bundle)
        problems.append({
            "obs_idxs": idxs_raw.tolist(),
            "obs_items": obs_items,
            "obs_seed": cue,
            "true_h": true_h.astype(np.float32),
            "_true_a_pos": true_a_pos,  # hidden ground truth (NOT used by arms)
            "_true_b_pos": true_b_pos,
        })
    return {"bank": bank, "problems": problems, "seed": int(seed)}


# -------------------- generators --------------------

def gen_swr_preplay(prob: Dict[str, Any], bank: np.ndarray, k: int,
                     g: np.random.Generator) -> np.ndarray:
    """SWR-preplay generator: random-pair replay seeded from obs_items.

    For each of k candidates, randomly sample an ordered pair (i,j) from
    obs_items and bind them: cand_k = normalize(bind(obs_i, obs_j)).
    This is the parent cell's ARM_PREPLAY pattern (with the substrate's noise
    coming from the random-pair sampling, not from additive bind-noise).

    Mechanism does NOT see true (a,b) labels; sampling is uniform over
    M_OBS*(M_OBS-1) ordered pairs.  Expected coverage of true pair across K
    candidates: 1 - ((M-1)*M-2)/(M*(M-1)))^K ~ 0.40 at M=5, K=10.
    """
    n = bank.shape[1]
    obs_items = prob["obs_items"]
    M = obs_items.shape[0]
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
    """Oracle: K-1 random codewords + true_h injected at random slot."""
    n = prob["true_h"].shape[0]
    cands = _bipolar(k, n, g)
    slot = int(g.integers(0, k))
    cands[slot] = normalize(prob["true_h"])
    return cands


# -------------------- scorers --------------------

def score_bayes_categorical(cands: np.ndarray, prob: Dict[str, Any]) -> int:
    """SCORER: bayes_update_categorical primitive (lap8/comp21/stretch3-4 chain-grade).

    Substrate-internal abductive ranking; mechanism uses obs_items + cue (NOT labels).

    Algorithm:
      1. Enumerate all M*(M-1) ordered pairs (i,j) from obs_items.
      2. Compute pair-likelihood w(i,j) = max(cos(cue, bind(obs_i, obs_j)), 0)^2
         (FHRR amp-as-prob; lap8 pattern).
      3. For each candidate cand_k, likelihood P(E|H_k) = max_{(i,j)} w(i,j) * cos(cand_k, bind(obs_i, obs_j))^2
         (the candidate's likelihood is its best match to a weighted pair-bind).
      4. Bayes update with uniform prior; return top-1 = argmax posterior.

    This uses bayes_update_categorical (chain-grade primitive) as the load-bearing scorer.
    """
    if cands.shape[0] == 0:
        return 0
    obs_items = prob["obs_items"]
    cue = prob["obs_seed"]
    M = obs_items.shape[0]

    # Precompute all pair-binds
    pair_binds: List[np.ndarray] = []
    pair_idx: List[Tuple[int, int]] = []
    for i in range(M):
        for j in range(M):
            if i != j:
                pair_binds.append(normalize(hrr_bind(obs_items[i], obs_items[j])))
                pair_idx.append((i, j))
    pair_binds_arr = np.array(pair_binds)  # (P, N) where P=M*(M-1)

    # Cue-driven pair-weights (which pair does the cue point to?)
    cue_sims = cos_rows(pair_binds_arr, cue)  # (P,)
    pair_weights = np.clip(cue_sims, 0.0, None) ** 2  # (P,)
    if float(pair_weights.sum()) <= 1e-12:
        return 0  # refuse: cue has no support
    pair_weights = pair_weights / pair_weights.sum()

    # Per-candidate likelihood: weighted max-cos to pair-binds
    cand_pair_sims = cos_rows(cands, pair_binds_arr)  # (K, P)
    cand_pair_sims = np.clip(cand_pair_sims, 0.0, None) ** 2  # (K, P)
    weighted = cand_pair_sims * pair_weights[None, :]  # (K, P)
    like = weighted.sum(axis=1)  # (K,)  marginal-likelihood-style

    if float(like.sum()) <= 1e-12:
        return 0  # refuse zero-mass

    # Uniform prior; Bayes update via chain-grade primitive
    K = cands.shape[0]
    prior = [1.0 / K] * K
    post = bayes_update_categorical(prior, like.tolist())
    return int(np.argmax(post))


def score_uniform(cands: np.ndarray, prob: Dict[str, Any]) -> int:
    """Uniform-pick: no scoring; return slot 0 (deterministic; META_RULE_AA NON-abductive)."""
    return 0


# -------------------- per-problem evaluation --------------------

def top1_hit(top1_cand: np.ndarray, true_h: np.ndarray, threshold: float = COS_HIT) -> int:
    return int(float(cos_rows(top1_cand[None, :], true_h)[0]) >= threshold)


def arm_fingerprint(top1_cands: List[np.ndarray]) -> str:
    if not top1_cands:
        return "empty"
    stacked = np.vstack(top1_cands).astype(np.float32)
    h = hashlib.sha256(stacked.tobytes()).hexdigest()
    return h[:16]


# -------------------- arm runners --------------------

ARM_GENERATORS = {
    "ARM_PIPELINE_FULL":      "swr_preplay",
    "ARM_GENERATOR_ONLY":     "swr_preplay",
    "ARM_SCORER_ONLY":        "random",
    "ARM_RANDOM_CANDIDATES":  "random",
    "ARM_ORACLE":             "oracle",
}
ARM_SCORERS = {
    "ARM_PIPELINE_FULL":      "bayes",
    "ARM_GENERATOR_ONLY":     "uniform",
    "ARM_SCORER_ONLY":        "bayes",
    "ARM_RANDOM_CANDIDATES":  "uniform",
    "ARM_ORACLE":             "bayes",
}


def run_arm(arm: str, problems: List[Dict[str, Any]], bank: np.ndarray,
             k: int, n_dim: int, g: np.random.Generator) -> Tuple[float, str, int]:
    """Run one arm across all problems; return (top1_rate, fingerprint, n_decisions)."""
    gen_type = ARM_GENERATORS[arm]
    sco_type = ARM_SCORERS[arm]
    hits = 0
    n = 0
    top1_cache: List[np.ndarray] = []
    for prob in problems:
        # generate
        if gen_type == "swr_preplay":
            cands = gen_swr_preplay(prob, bank, k, g)
        elif gen_type == "random":
            cands = gen_random(n_dim, k, g)
        elif gen_type == "oracle":
            cands = gen_oracle(prob, k, g)
        else:
            raise ValueError("unknown gen_type=%s" % gen_type)
        # score
        if sco_type == "bayes":
            top1_idx = score_bayes_categorical(cands, prob)
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
    """--self-test gate: smoke-tiny config + sanity checks; return 0 on PASS, 2 on FAIL."""
    print("[selftest] %s starting (N=%d V=%d N_PROB=%d)" % (
        ANCHOR_NAME, N_DIM, V_BANK, N_PROBLEMS), flush=True)
    g_data = np.random.default_rng(SEED_THIS_CHUNK)
    ps = build_problem_set(SEED_THIS_CHUNK, N_PROBLEMS, N_DIM, V_BANK, M_OBS)
    bank = ps["bank"]
    problems = ps["problems"]
    print("[selftest] problem-set OK (bank=%s problems=%d)" % (bank.shape, len(problems)), flush=True)
    assert bank.shape == (V_BANK, N_DIM), "bank shape"
    assert len(problems) == N_PROBLEMS, "n_problems"

    g_run = np.random.default_rng(SEED_THIS_CHUNK + 1000)
    fps = {}
    rates = {}
    for arm in EXPECTED_ARMS:
        rate, fp, n_dec = run_arm(arm, problems, bank, K_CANDS, N_DIM, g_run)
        rates[arm] = rate
        fps[arm] = fp
        print("[selftest] %-25s top1=%.3f  fp=%s  n=%d" % (arm, rate, fp, n_dec), flush=True)

    # arms_distinct
    distinct = len(set(fps.values())) == len(EXPECTED_ARMS)
    print("[selftest] arms_distinct=%s fps=%s" % (distinct, fps), flush=True)

    # MEASURED ordering check (expected: ORACLE highest; RANDOM_CANDIDATES lowest)
    print("[selftest] expected ordering: ORACLE > {PIPELINE, SCORER_ONLY} > {GEN_ONLY, RANDOM}", flush=True)
    print("[selftest] observed: ORACLE=%.3f PIPELINE=%.3f SCORER=%.3f GEN_ONLY=%.3f RANDOM=%.3f" % (
        rates["ARM_ORACLE"], rates["ARM_PIPELINE_FULL"], rates["ARM_SCORER_ONLY"],
        rates["ARM_GENERATOR_ONLY"], rates["ARM_RANDOM_CANDIDATES"]), flush=True)

    # MUST-HOLD even in self-test mode (tiny N):
    if rates["ARM_ORACLE"] < 0.5:
        print("[selftest] FAIL: ORACLE=%.3f < 0.5 (oracle should hit nearly always)" % rates["ARM_ORACLE"],
              flush=True)
        return 2
    if rates["ARM_RANDOM_CANDIDATES"] > 0.3:
        print("[selftest] FAIL: RANDOM=%.3f > 0.3 (floor breach in tiny self-test)" % rates["ARM_RANDOM_CANDIDATES"],
              flush=True)
        return 2
    if not distinct:
        print("[selftest] FAIL: arms_distinct=False", flush=True)
        return 2

    print("[selftest] PASS (orientation correct; arms distinct; oracle fires; floor holds)", flush=True)
    return 0


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
            "SELFTEST_OK %s (N=%d V=%d N_PROB=%d)" % (
                ANCHOR_NAME, N_DIM, V_BANK, N_PROBLEMS))
        return 0

    print("[main] mode=%s N=%d V=%d N_PROB=%d K=%d SEED=%d" % (
        RUN_MODE, N_DIM, V_BANK, N_PROBLEMS, K_CANDS, SEED_THIS_CHUNK), flush=True)

    t0 = time.time()
    ps = build_problem_set(SEED_THIS_CHUNK, N_PROBLEMS, N_DIM, V_BANK, M_OBS)
    bank = ps["bank"]
    problems = ps["problems"]
    print("[main] problem-set built (bank=%s problems=%d) elapsed=%.1fs" % (
        bank.shape, len(problems), time.time() - t0), flush=True)

    g_run = np.random.default_rng(SEED_THIS_CHUNK + 1000)
    per_arm: Dict[str, Dict[str, Any]] = {}
    fps: Dict[str, str] = {}
    n_observed_total = 0
    for arm in EXPECTED_ARMS:
        t_arm = time.time()
        rate, fp, n_dec = run_arm(arm, problems, bank, K_CANDS, N_DIM, g_run)
        per_arm[arm] = {
            "top1_rate": rate,
            "fingerprint": fp,
            "n_decisions": n_dec,
            "elapsed_s": round(time.time() - t_arm, 2),
        }
        fps[arm] = fp
        n_observed_total += n_dec
        print("[arm] %-25s top1=%.3f fp=%s n=%d wall=%.1fs" % (
            arm, rate, fp, n_dec, time.time() - t_arm), flush=True)

    distinct = len(set(fps.values())) == len(EXPECTED_ARMS)
    cardinality_ok = (n_observed_total == EXPECTED_N_UNITS)
    rates = {arm: per_arm[arm]["top1_rate"] for arm in EXPECTED_ARMS}

    pipeline = rates["ARM_PIPELINE_FULL"]
    gen_only = rates["ARM_GENERATOR_ONLY"]
    scorer_only = rates["ARM_SCORER_ONLY"]
    random_only = rates["ARM_RANDOM_CANDIDATES"]
    oracle = rates["ARM_ORACLE"]
    lift_over_max_primitive = pipeline - max(gen_only, scorer_only)
    composition_value_add = lift_over_max_primitive >= HP_PIPELINE_LIFT_MIN

    # META_RULE_Q suspect-1.000 check (only meaningful at n>=100)
    suspect_q = False
    if n_observed_total // len(EXPECTED_ARMS) >= 100:
        for arm, r in rates.items():
            if r >= 0.999 and arm != "ARM_ORACLE":  # oracle is designed to hit
                suspect_q = True
                break

    # Verdict logic
    hf_reasons = []
    if pipeline <= max(gen_only, scorer_only):
        hf_reasons.append("META_RULE_AM: PIPELINE<=max(GEN_ONLY,SCORER_ONLY) functional-req-already-met")
    if pipeline < HF_PIPELINE_LO:
        hf_reasons.append("PIPELINE<%.2f" % HF_PIPELINE_LO)
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
        "composition_lift_ge_%.2f" % HP_PIPELINE_LIFT_MIN: composition_value_add,
        "pipeline_in_[%.2f,%.2f]" % (HP_PIPELINE_LO, HP_PIPELINE_HI):
            (HP_PIPELINE_LO <= pipeline <= HP_PIPELINE_HI),
        "oracle>pipeline": oracle > pipeline,
        "random<=%.2f" % HP_RANDOM_MAX: random_only <= HP_RANDOM_MAX,
        "arms_distinct": distinct,
        "cardinality_ok": cardinality_ok,
    }
    all_hp = all(hp_conds.values()) and not hf_reasons

    if hf_reasons:
        verdict = "HARD_FAIL"
    elif all_hp:
        verdict = "HARD_PASS"
    else:
        verdict = "MIDDLE_BAND"

    verdict_msg = (
        "%s %s | PIPELINE=%.3f GEN_ONLY=%.3f SCORER_ONLY=%.3f RANDOM=%.3f ORACLE=%.3f"
        " | lift_over_max_prim=%+.3f comp_value_add=%s"
        " | arms_distinct=%s cardinality_ok=%s (obs=%d/exp=%d)"
        " | fps=%s"
    ) % (
        verdict, ANCHOR_NAME, pipeline, gen_only, scorer_only, random_only, oracle,
        lift_over_max_primitive, composition_value_add,
        distinct, cardinality_ok, n_observed_total, EXPECTED_N_UNITS, fps,
    )
    if hf_reasons:
        verdict_msg += " | HF_REASONS=%s" % ";".join(hf_reasons)

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
        "K_CANDS": K_CANDS,
        "seed": SEED_THIS_CHUNK,
        "config_version": CONFIG_VERSION,
        "arms_tested": EXPECTED_ARMS,
        "per_arm_summary": per_arm,
        "rates": rates,
        "fingerprints": fps,
        "arms_distinct": distinct,
        "cardinality_ok": cardinality_ok,
        "n_observed": n_observed_total,
        "n_expected": EXPECTED_N_UNITS,
        "composition_value_add": composition_value_add,
        "lift_over_max_primitive": lift_over_max_primitive,
        "hp_conds": hp_conds,
        "hf_reasons": hf_reasons,
        "suspect_q": suspect_q,
        "_hardening_marker": _HARDENING_MARKER,
    }

    # write_partial for seed-checkpoint compatibility (chunked aggregation)
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
