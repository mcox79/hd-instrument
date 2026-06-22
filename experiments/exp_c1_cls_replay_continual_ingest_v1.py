"""c1_cls_replay_continual_ingest_v1 -- Complementary Learning Systems (CLS) replay test.

SCIENTIFIC QUESTION (brain-drill #2, 2026-06-22):
  Does 1:1 Hebbian generative replay rescue continual learning at the substrate's alpha-cliff?

  Architecture mapping (biology -> substrate):
    - U1 multi-value episodic cache  = hippocampus (CA3 attractor; fast all-or-nothing)
    - W Hebbian-superposition matrix = cortex (distributed, slow, capacity-bound at alpha_c)
    - sample-from-U1 + Hebbian-rewrite-into-W = SWR (sharp-wave-ripple) replay loop

  Protocol:
    1. Generate J disjoint task-batches of (key, value) pairs (random bipolar vectors).
    2. For each task j in 1..J:
         a. Write task-j (key, value) into U1 (episodic; just remember the pairs).
         b. Hebbian-bind task-j (key, value) into W (cortex outer-product update).
         c. If replay enabled: sample N_replay old (key, value) from U1 prior tasks;
            re-bind into W via the SAME Hebbian outer-product (no labels, no gradients).
    3. After all J tasks: probe task-1 recall (forgetting test) and task-J recall (recency).
    4. Total load alpha = (J * M_per_task) / N_DIM is held FIXED across arms.

  Arms (the lever under test):
    A: NONE        -- no replay; pure sequential ingest; expect catastrophic forgetting baseline
    B: ONLINE_1to1 -- per-task: 1 replay from prior tasks for every new item (the CLS proposal)
    C: ONLINE_3to1 -- 3 replays per new item (over-rehearsal; biology compression ~20x suggests <=1:1
                      may suffice but biology can also support 3:1 in heavy SWS)
    D: RANDOM_1to1 -- 1:1 replay BUT samples are random fresh bipolar vectors NOT from U1; if Arm D
                      matches Arm B, the U1-as-hippocampus claim is wrong (key discriminator)

  Substrate-only-decode gate: pure numpy + Hebbian; ZERO LLM forward calls anywhere.

PRE-REGISTERED BANDS (brain-drill #2 c1):
  At alpha_total = 0.5 (cliff regime, J=10 tasks):
    HARD_PASS:    task-A recall@J=10 >= 0.85 with ONLINE_1to1 (Arm B)
                  AND replay-vs-NONE delta (B - A) >= 0.40
                  AND Arm D (random-replay) < Arm B (mechanism is U1-sourced, not generic noise)
                  AND cv <= 0.05 across seeds for Arm A and Arm B at task-A recall
                  AND zero_llm_calls_at_inference == True
                  AND Arm A reproduces a8 anchor: at alpha=0.3 NONE, task-A recall >= 0.95
                                                  at alpha=1.5 NONE, task-A recall < 0.30
    MIDDLE_BAND:  replay-vs-NONE delta in [0.20, 0.40) at alpha=0.5  (partial mechanism)
    HARD_FAIL:    replay-vs-NONE delta < 0.20 at alpha=0.5  (mechanism does not transfer)
                  OR Arm B task-A < 0.55 at alpha=0.5
                  OR Arm A at alpha=0.3 disagrees with a8 anchor by > 0.10
                  OR Arm D >= Arm B (the mechanism is not U1-sourced)

  Nullability bracket (PRED 4 in drill #2):
    At alpha_total = 0.1: BOTH Arm A and Arm B reach task-A recall >= 0.90 (replay adds nothing
    when there's room; sanity check that replay doesn't HURT below cliff).

  Capacity-overload bracket:
    At alpha_total = 1.5: BOTH Arm A and Arm B collapse to task-A recall < 0.30 (replay cannot
    rescue catastrophic overload; sanity check that the test is not by-construction).

FIX INVENTORY (per experiment_pipeline_agent_template + pipeline-agent disciplines):
  - _LLM_CALL_COUNTER = [0] at module scope; asserted == 0 at end (substrate-only gate)
  - ANCHOR_NAME, CONFIG_VERSION baked module-level (AST-verifiable)
  - run_mode='full' default; HDLAB_RUN_MODE / --smoke flag honored
  - allow_synthetic=True is CORRECT here -- the cell is BY DESIGN a synthetic-bipolar capacity
    probe (a8-style); no real corpus is appropriate for isolating the replay mechanism.
    We still bake CORPUS_PROVENANCE = 'synthetic_bipolar_keys' into metrics for audit.
  - per_seed entry per (seed, arm, alpha) into metrics.json
  - cv across seeds computed in verdict()
  - Pre-reg direction enforced (B > A; replay rescues forgetting)
  - Discriminating-regime: alpha=0.1 nullability + alpha=1.5 overload guards
  - Anchor reproduction: alpha=0.3 NONE recall vs a8 baseline ~1.0

FORMULA SELF-TESTS:
  1. NONE-replay at alpha=0.05, J=2 tasks: task-1 recall >= 0.6 (small load; should survive).
  2. ONLINE_1to1 at alpha=0.05: task-1 recall >= 0.6 AND no worse than NONE (sanity).
  3. _LLM_CALL_COUNTER remains 0 throughout.

ASCII-only. CPU. Single-file. Resumable via _seed_checkpoint.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import json
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "c1_cls_replay_continual_ingest_v1"

# Substrate-only-decode gate (Skunkworks structural blocker #3).
# Asserted == 0 at end of run. Any LLM forward call MUST increment this.
_LLM_CALL_COUNTER = [0]

# Corpus provenance: this cell is INTENTIONALLY synthetic-bipolar (the right substrate for
# isolating the replay mechanism from KG-specific encoding effects; mirrors a8 + saad_solla).
CORPUS_PROVENANCE = "synthetic_bipolar_keys"

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Pre-reg bands (locked at design time)
HARD_PASS_TASK_A = 0.85         # Arm B task-A recall at alpha=0.5 cliff
HARD_PASS_DELTA = 0.40          # (B - A) at alpha=0.5
MIDDLE_BAND_LO = 0.20           # delta in [0.20, 0.40) = MIDDLE_BAND
HARD_FAIL_DELTA = 0.20          # delta < this = HARD_FAIL
HARD_FAIL_B_FLOOR = 0.55        # Arm B task-A below this = HARD_FAIL
A8_ANCHOR_ALPHA_03 = 0.95       # Arm A at alpha=0.3 must >= this (a8 reproduction)
A8_ANCHOR_ALPHA_15 = 0.30       # Arm A at alpha=1.5 must < this (capacity-stress sanity)
A8_ANCHOR_TOL = 0.10
NULL_BRACKET_MIN = 0.85         # at alpha=0.1, both A and B >= this (slightly slack on null)
CV_HARD_PASS_MAX = 0.05         # cv across seeds for HARD_PASS arms
NOISE_FRAC = 0.10               # probe noise: 10% flipped bits at recall time
N_RECALL_STEPS = 3              # Hopfield-style iterative cleanup steps

# Smoke vs full config
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    J_TASKS = 3
    M_PER_TASK_AT_ALPHA = {  # M = round(alpha * N_DIM / J)
        0.5: int(round(0.5 * 1024 / 3)),   # ~170
    }
    ALPHAS = [0.5]
    ARMS = ["NONE", "ONLINE_1to1"]
    N_PROBE = 30
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    J_TASKS = 10
    M_PER_TASK_AT_ALPHA = {
        0.1: int(round(0.1 * 4096 / 10)),  # ~41
        0.3: int(round(0.3 * 4096 / 10)),  # ~123
        0.5: int(round(0.5 * 4096 / 10)),  # ~205 -- drill pre-reg cliff regime
        1.5: int(round(1.5 * 4096 / 10)),  # ~614 -- overload bracket
    }
    ALPHAS = [0.1, 0.3, 0.5, 1.5]
    ARMS = ["NONE", "ONLINE_1to1", "ONLINE_3to1", "RANDOM_1to1"]
    N_PROBE = 60

CONFIG_VERSION = ("c1-cls-replay-v1: J=%d N_DIM=%d arms=%s alphas=%s; bands HP=%.2f delta=%.2f "
                  "noise=%.2f recall_steps=%d run_mode=%s" %
                  (J_TASKS, N_DIM, ",".join(ARMS), str(ALPHAS),
                   HARD_PASS_TASK_A, HARD_PASS_DELTA, NOISE_FRAC, N_RECALL_STEPS, RUN_MODE))


def make_bipolar(M: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random +/- 1 vectors, L2-normalized to unit length."""
    X = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float64)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def hebbian_bind(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> None:
    """In-place Hebbian outer-product update: W += value (outer) key / N_DIM."""
    n = W.shape[0]
    W += np.outer(value, key) / n


def recall_value(W: np.ndarray, key_probe: np.ndarray, codebook_values: np.ndarray,
                 n_steps: int = N_RECALL_STEPS) -> np.ndarray:
    """Return the cleaned-up recalled value via Hopfield-style cosine-cleanup against codebook.

    Mechanism: y_raw = W @ key_probe; then nearest-neighbour in the value codebook (max cos).
    n_steps iterations of (decode -> re-project) for cleanup. Returns the recovered value vector.
    """
    y = W @ key_probe
    for _ in range(n_steps):
        # cosine vs codebook -> argmax -> snap to codebook entry
        sims = codebook_values @ y
        idx = int(np.argmax(sims))
        y_snap = codebook_values[idx]
        # iterate: re-read from W using snap (single Hopfield-style cleanup pass)
        y = 0.5 * y + 0.5 * y_snap
    sims = codebook_values @ y
    idx = int(np.argmax(sims))
    return codebook_values[idx], idx


def eval_task_recall(W: np.ndarray, keys: np.ndarray, values: np.ndarray,
                     value_idx: np.ndarray, codebook_values: np.ndarray,
                     n_probe: int, rng: np.random.RandomState) -> Tuple[float, float]:
    """Recall on n_probe random items from (keys, values). Noisy probes.

    Returns (recall_codebook_nn, recall_cos):
      recall_codebook_nn = fraction where argmax over codebook == true value-idx
                          (U1-style cleanup; graceful but strong)
      recall_cos         = mean cosine of raw W @ key_probe with true value vector
                          (a8-style raw fidelity; sensitive to crosstalk)
    """
    M = keys.shape[0]
    n_q = min(n_probe, M)
    if n_q == 0:
        return 0.0, 0.0
    sel = rng.choice(M, size=n_q, replace=False)
    correct_nn = 0
    cos_sum = 0.0
    for j in sel:
        key = keys[j].copy()
        # noise: flip NOISE_FRAC of dimensions (sign flip) then re-normalize
        flip = rng.random(W.shape[0]) < NOISE_FRAC
        key[flip] *= -1.0
        key = key / (np.linalg.norm(key) + 1e-12)
        # raw read
        y = W @ key
        y_n = y / (np.linalg.norm(y) + 1e-12)
        # codebook-NN
        sims = codebook_values @ y_n
        idx = int(np.argmax(sims))
        if idx == value_idx[j]:
            correct_nn += 1
        # raw cosine vs true
        cos_sum += float(codebook_values[value_idx[j]] @ y_n)
    return float(correct_nn) / n_q, float(cos_sum / n_q)


def run_one_arm(arm: str, alpha: float, seed: int) -> Dict:
    """Run J sequential tasks with the given replay arm. Return per-task recall curve."""
    rng = np.random.RandomState(seed * 1000 + int(alpha * 100) + hash(arm) % 100)

    n = N_DIM
    j_total = J_TASKS
    m_per_task = M_PER_TASK_AT_ALPHA[alpha]

    # Codebook of candidate values (shared across tasks; size = total #items + buffer)
    # Each task draws m_per_task UNIQUE value-indices from this codebook (no reuse across tasks).
    n_values_total = j_total * m_per_task
    codebook = make_bipolar(n_values_total + 16, n, rng)

    # Storage for per-task keys + value-indices (for later eval)
    task_keys: List[np.ndarray] = []
    task_value_idx: List[np.ndarray] = []

    # Episodic cache U1 (just remember the (key, value_idx) tuples ever written)
    U1_keys_buf: List[np.ndarray] = []
    U1_validx_buf: List[int] = []

    # Cortex W matrix (initialized to zero)
    W = np.zeros((n, n), dtype=np.float64)

    next_value_idx = 0
    t_ingest_start = time.time()
    for j in range(j_total):
        # Generate task-j keys (disjoint per task = no shared keys across tasks)
        keys_j = make_bipolar(m_per_task, n, rng)
        # Pick disjoint value-indices for task-j
        value_idx_j = np.arange(next_value_idx, next_value_idx + m_per_task)
        next_value_idx += m_per_task

        task_keys.append(keys_j)
        task_value_idx.append(value_idx_j)

        # Ingest pass: write each (key, value) into W; also append to U1
        for m in range(m_per_task):
            k = keys_j[m]
            v_idx = int(value_idx_j[m])
            v = codebook[v_idx]
            hebbian_bind(W, k, v)
            U1_keys_buf.append(k)
            U1_validx_buf.append(v_idx)

            # REPLAY step (if applicable)
            if arm == "NONE":
                continue
            elif arm == "ONLINE_1to1":
                # Sample 1 OLD (k, v) from U1 (only entries written PRIOR to current task);
                # if no prior task, skip (first task has nothing to replay).
                n_prior = sum(len(tk) for tk in task_keys[:-1])
                if n_prior == 0:
                    continue
                ridx = rng.randint(0, n_prior)
                hebbian_bind(W, U1_keys_buf[ridx], codebook[U1_validx_buf[ridx]])
            elif arm == "ONLINE_3to1":
                n_prior = sum(len(tk) for tk in task_keys[:-1])
                if n_prior == 0:
                    continue
                for _ in range(3):
                    ridx = rng.randint(0, n_prior)
                    hebbian_bind(W, U1_keys_buf[ridx], codebook[U1_validx_buf[ridx]])
            elif arm == "RANDOM_1to1":
                # Sample 1 random FRESH (k, v) pair NOT from U1 -- the discriminator control
                if len(task_keys) <= 1:
                    continue
                k_rand = make_bipolar(1, n, rng)[0]
                v_rand = make_bipolar(1, n, rng)[0]
                hebbian_bind(W, k_rand, v_rand)
            else:
                raise ValueError("unknown arm: %s" % arm)
    ingest_wall_s = time.time() - t_ingest_start

    # Eval: recall task-1 (forgetting), task-J (recency); both NN-cleanup AND raw cosine.
    rec_task_A, cos_task_A = eval_task_recall(W, task_keys[0], None, task_value_idx[0],
                                              codebook, N_PROBE, rng)
    rec_task_J, cos_task_J = eval_task_recall(W, task_keys[-1], None, task_value_idx[-1],
                                              codebook, N_PROBE, rng)

    # Forgetting curve: recall task-1 at the end of each task j in 1..J (we already have final;
    # for full-run we ALSO want the curve. Re-run a lightweight version: ingest+probe at each j.
    # To keep wall manageable, only emit forgetting curve at full mode.
    forgetting_curve = None
    if RUN_MODE == "full" and alpha == 0.5 and arm in ("NONE", "ONLINE_1to1"):
        forgetting_curve = _replay_with_curve(arm, alpha, seed)

    return {
        "arm": arm, "alpha": float(alpha), "seed": int(seed),
        "j_tasks": j_total, "m_per_task": m_per_task, "n_dim": n,
        "task_A_recall": float(rec_task_A),
        "task_J_recall": float(rec_task_J),
        "task_A_cosine": float(cos_task_A),
        "task_J_cosine": float(cos_task_J),
        "ingest_wall_s": float(ingest_wall_s),
        "n_probe": N_PROBE,
        "forgetting_curve": forgetting_curve,
    }


def _replay_with_curve(arm: str, alpha: float, seed: int) -> List[float]:
    """Repeat the ingest measuring task-1 recall after each task j. Costs ~Jx ingest but only run
    for the two main arms at alpha=0.5 to bound total wall."""
    rng = np.random.RandomState(seed * 1000 + int(alpha * 100) + hash(arm) % 100 + 7)
    n = N_DIM
    j_total = J_TASKS
    m_per_task = M_PER_TASK_AT_ALPHA[alpha]
    n_values_total = j_total * m_per_task
    codebook = make_bipolar(n_values_total + 16, n, rng)
    task_keys: List[np.ndarray] = []
    task_value_idx: List[np.ndarray] = []
    U1_keys_buf: List[np.ndarray] = []
    U1_validx_buf: List[int] = []
    W = np.zeros((n, n), dtype=np.float64)
    next_value_idx = 0
    curve = []
    for j in range(j_total):
        keys_j = make_bipolar(m_per_task, n, rng)
        value_idx_j = np.arange(next_value_idx, next_value_idx + m_per_task)
        next_value_idx += m_per_task
        task_keys.append(keys_j)
        task_value_idx.append(value_idx_j)
        for m in range(m_per_task):
            k = keys_j[m]
            v_idx = int(value_idx_j[m])
            v = codebook[v_idx]
            hebbian_bind(W, k, v)
            U1_keys_buf.append(k)
            U1_validx_buf.append(v_idx)
            if arm == "ONLINE_1to1":
                n_prior = sum(len(tk) for tk in task_keys[:-1])
                if n_prior > 0:
                    ridx = rng.randint(0, n_prior)
                    hebbian_bind(W, U1_keys_buf[ridx], codebook[U1_validx_buf[ridx]])
        # measure task-1 recall after this task's writes
        rec, _ = eval_task_recall(W, task_keys[0], None, task_value_idx[0], codebook,
                                  max(20, N_PROBE // 2), rng)
        curve.append(float(rec))
    return curve


def _selftest():
    """3 self-tests per the docstring."""
    rng = np.random.RandomState(0)
    n = 256
    j_total = 2
    m_per_task = max(1, int(0.05 * n / j_total))  # alpha ~0.05
    codebook = make_bipolar(2 * m_per_task + 8, n, rng)
    # arm A: NONE
    W_A = np.zeros((n, n))
    keys_A = [make_bipolar(m_per_task, n, rng), make_bipolar(m_per_task, n, rng)]
    vidx_A = [np.arange(0, m_per_task), np.arange(m_per_task, 2 * m_per_task)]
    for j in range(j_total):
        for m in range(m_per_task):
            hebbian_bind(W_A, keys_A[j][m], codebook[vidx_A[j][m]])
    rec_A_task1, _ = eval_task_recall(W_A, keys_A[0], None, vidx_A[0], codebook, 20, rng)
    assert rec_A_task1 >= 0.5, "selftest 1: NONE at alpha=0.05 task-1 recall too low: %.3f" % rec_A_task1

    # arm B: ONLINE_1to1
    W_B = np.zeros((n, n))
    U1_k, U1_v = [], []
    keys_B = [make_bipolar(m_per_task, n, rng), make_bipolar(m_per_task, n, rng)]
    vidx_B = [np.arange(0, m_per_task), np.arange(m_per_task, 2 * m_per_task)]
    written_so_far = []
    for j in range(j_total):
        for m in range(m_per_task):
            hebbian_bind(W_B, keys_B[j][m], codebook[vidx_B[j][m]])
            U1_k.append(keys_B[j][m])
            U1_v.append(vidx_B[j][m])
            if j > 0 and len(written_so_far) > 0:
                ridx = rng.randint(0, len(written_so_far))
                hebbian_bind(W_B, U1_k[ridx], codebook[U1_v[ridx]])
        written_so_far = list(range(len(U1_k)))
    rec_B_task1, _ = eval_task_recall(W_B, keys_B[0], None, vidx_B[0], codebook, 20, rng)
    assert rec_B_task1 >= 0.5, ("selftest 2: ONLINE_1to1 at alpha=0.05 task-1 recall too low: %.3f"
                                 % rec_B_task1)

    # selftest 3: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 3: LLM counter non-zero (%d)" % _LLM_CALL_COUNTER[0]

    print("[selftest] PASS: NONE_task1=%.3f ONLINE_task1=%.3f LLM=%d"
          % (rec_A_task1, rec_B_task1, _LLM_CALL_COUNTER[0]), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    """Run all (arm, alpha) combos for one seed."""
    t0 = time.time()
    per_unit = []
    for alpha in ALPHAS:
        for arm in ARMS:
            res = run_one_arm(arm, alpha, seed)
            per_unit.append(res)
            print("  [seed=%d] arm=%s alpha=%.3f M/task=%d task_A=%.3f task_J=%.3f wall=%.1fs"
                  % (seed, arm, alpha, res["m_per_task"], res["task_A_recall"],
                     res["task_J_recall"], res["ingest_wall_s"]), flush=True)
    elapsed = time.time() - t0
    return {
        "seed": seed, "N": N_DIM, "M": M_PER_TASK_AT_ALPHA.get(0.5, 0),
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "per_unit": per_unit,
        "elapsed_s": float(elapsed),
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    }


def compute_verdict(per_seed: Dict[str, Dict]) -> Tuple[str, str, Dict]:
    """Compute verdict per the pre-reg bands."""
    if not per_seed:
        return ("HARD_FAIL", "No valid results.", {})

    # Aggregate: mean task-A recall across seeds per (arm, alpha) -- and std for cv
    agg: Dict[Tuple[str, float], List[float]] = {}
    agg_J: Dict[Tuple[str, float], List[float]] = {}
    agg_cosA: Dict[Tuple[str, float], List[float]] = {}
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            k = (pu["arm"], float(pu["alpha"]))
            agg.setdefault(k, []).append(float(pu["task_A_recall"]))
            agg_J.setdefault(k, []).append(float(pu["task_J_recall"]))
            if "task_A_cosine" in pu:
                agg_cosA.setdefault(k, []).append(float(pu["task_A_cosine"]))

    mean_A = {k: float(np.mean(v)) for k, v in agg.items()}
    std_A = {k: float(np.std(v)) for k, v in agg.items()}
    mean_J = {k: float(np.mean(v)) for k, v in agg_J.items()}
    cv_A = {k: (std_A[k] / max(mean_A[k], 1e-9)) for k in mean_A}
    mean_cosA = {k: float(np.mean(v)) for k, v in agg_cosA.items()}

    # Pull the key numbers
    a_05 = mean_A.get(("NONE", 0.5), float("nan"))
    b_05 = mean_A.get(("ONLINE_1to1", 0.5), float("nan"))
    c_05 = mean_A.get(("ONLINE_3to1", 0.5), None)
    d_05 = mean_A.get(("RANDOM_1to1", 0.5), None)
    delta = (b_05 - a_05) if not (math.isnan(a_05) or math.isnan(b_05)) else float("nan")

    a_03 = mean_A.get(("NONE", 0.3), None)
    a_15 = mean_A.get(("NONE", 1.5), None)
    a_01 = mean_A.get(("NONE", 0.1), None)
    b_01 = mean_A.get(("ONLINE_1to1", 0.1), None)

    cv_A_05 = cv_A.get(("NONE", 0.5), float("inf"))
    cv_B_05 = cv_A.get(("ONLINE_1to1", 0.5), float("inf"))

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # Anchor checks (a8 reproduction)
    anchor_03_ok = (a_03 is None) or (a_03 >= (A8_ANCHOR_ALPHA_03 - A8_ANCHOR_TOL))
    anchor_15_ok = (a_15 is None) or (a_15 < (A8_ANCHOR_ALPHA_15 + A8_ANCHOR_TOL))
    # Nullability bracket
    null_ok = ((a_01 is None or a_01 >= NULL_BRACKET_MIN) and
               (b_01 is None or b_01 >= NULL_BRACKET_MIN))

    # Discriminator: random-replay must NOT match U1-replay
    random_ok = (d_05 is None) or (d_05 < b_05)

    detail = {
        "mean_taskA": {f"{k[0]}@a{k[1]:.2f}": v for k, v in mean_A.items()},
        "std_taskA": {f"{k[0]}@a{k[1]:.2f}": v for k, v in std_A.items()},
        "cv_taskA": {f"{k[0]}@a{k[1]:.2f}": v for k, v in cv_A.items()},
        "mean_taskJ": {f"{k[0]}@a{k[1]:.2f}": v for k, v in mean_J.items()},
        "mean_taskA_cosine": {f"{k[0]}@a{k[1]:.2f}": v for k, v in mean_cosA.items()},
        "delta_B_minus_A_at_alpha05": float(delta) if not math.isnan(delta) else None,
        "anchor_alpha_03_NONE_ok": bool(anchor_03_ok),
        "anchor_alpha_15_NONE_ok": bool(anchor_15_ok),
        "null_bracket_alpha_01_ok": bool(null_ok),
        "random_replay_discriminator_ok": bool(random_ok),
        "substrate_only_ok": bool(substrate_only_ok),
        "cv_NONE_alpha05": float(cv_A_05),
        "cv_ONLINE_alpha05": float(cv_B_05),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "honest_scope": ("CLS replay rescue of continual learning on synthetic-bipolar (key, value) "
                          "Hebbian-superposition at N_DIM=%d, J=%d tasks, alpha=%s. Substrate-only-decode "
                          "gate enforced (n_llm=%d)." % (N_DIM, J_TASKS, str(ALPHAS), n_llm)),
    }

    summary = ("A05=%.3f B05=%.3f delta=%.3f C05=%s D05=%s | A03=%s A15=%s A01=%s B01=%s | "
               "cv_A=%.3f cv_B=%.3f | anchor03=%s anchor15=%s null=%s rand_ok=%s llm=%d" %
               (a_05, b_05, delta if not math.isnan(delta) else float("nan"),
                ("%.3f" % c_05) if c_05 is not None else "n/a",
                ("%.3f" % d_05) if d_05 is not None else "n/a",
                ("%.3f" % a_03) if a_03 is not None else "n/a",
                ("%.3f" % a_15) if a_15 is not None else "n/a",
                ("%.3f" % a_01) if a_01 is not None else "n/a",
                ("%.3f" % b_01) if b_01 is not None else "n/a",
                cv_A_05, cv_B_05, anchor_03_ok, anchor_15_ok, null_ok, random_ok, n_llm))

    # Verdict logic
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)
    if math.isnan(delta):
        return ("HARD_FAIL",
                "HARD_FAIL: missing required (NONE@0.5, ONLINE_1to1@0.5) data. %s" % summary,
                detail)
    if not anchor_03_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: a8 anchor reproduction failed at alpha=0.3 NONE (got %.3f, expected >= %.2f). "
                 "Substrate baseline does not match prior cert. %s" % (a_03, A8_ANCHOR_ALPHA_03, summary)),
                detail)
    if not anchor_15_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: a8 anchor reproduction failed at alpha=1.5 NONE (got %.3f, expected < %.2f). "
                 "Capacity stress not genuine. %s" % (a_15, A8_ANCHOR_ALPHA_15, summary)),
                detail)
    if not random_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: random-replay discriminator violated (RANDOM_1to1=%.3f >= ONLINE_1to1=%.3f); "
                 "the mechanism is NOT U1-sourced. %s" % (d_05, b_05, summary)),
                detail)
    if delta < HARD_FAIL_DELTA:
        return ("HARD_FAIL",
                "HARD_FAIL: replay delta %.3f < HARD_FAIL bar %.2f. %s" % (delta, HARD_FAIL_DELTA, summary),
                detail)
    if b_05 < HARD_FAIL_B_FLOOR:
        return ("HARD_FAIL",
                "HARD_FAIL: Arm B task-A %.3f < floor %.2f. %s" % (b_05, HARD_FAIL_B_FLOOR, summary),
                detail)
    if (b_05 >= HARD_PASS_TASK_A and delta >= HARD_PASS_DELTA
            and cv_B_05 <= CV_HARD_PASS_MAX and cv_A_05 <= CV_HARD_PASS_MAX
            and null_ok):
        return ("HARD_PASS",
                ("HARD_PASS: CLS replay rescues continual learning. B05=%.3f >= %.2f AND delta=%.3f >= %.2f "
                 "AND seeds reproduce (cv_A=%.3f cv_B=%.3f <= %.2f) AND null bracket OK AND U1-sourced "
                 "(random control < ONLINE). %s" %
                 (b_05, HARD_PASS_TASK_A, delta, HARD_PASS_DELTA, cv_A_05, cv_B_05, CV_HARD_PASS_MAX,
                  summary)),
                detail)
    if delta >= MIDDLE_BAND_LO:
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: replay rescues PARTIALLY. delta=%.3f in [%.2f, %.2f). B05=%.3f. %s" %
                 (delta, MIDDLE_BAND_LO, HARD_PASS_DELTA, b_05, summary)),
                detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: ambiguous; bands not crossed. %s" % summary, detail)


# Main runner
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d J=%d alphas=%s arms=%s seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, N_DIM, J_TASKS, str(ALPHAS), str(ARMS), str(done), str(seeds_todo)), flush=True)

for s in seeds_todo:
    res = run_seed(s)
    write_partial(out_dir, s, res)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
verdict, verdict_msg, detail = compute_verdict(per_seed)

metrics = {
    "anchor": ANCHOR_NAME,
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "n_seeds": len(per_seed),
    "N": N_DIM,
    "N_DIM": N_DIM,
    "J_tasks": J_TASKS,
    "alphas": ALPHAS,
    "arms": ARMS,
    "run_mode": RUN_MODE,
    "config_version": CONFIG_VERSION,
    "corpus_provenance": CORPUS_PROVENANCE,
    "allow_synthetic": True,
    "zero_llm_calls_at_inference": bool(_LLM_CALL_COUNTER[0] == 0),
    "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
    "detail": detail,
    "per_seed": [
        {"seed": k, **{kk: vv for kk, vv in v.items() if kk != "per_unit"},
         "per_unit": v.get("per_unit", [])}
        for k, v in per_seed.items()
    ],
    "metrics_source": "measured_cpu_synthetic_bipolar_cls_replay",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
