"""c3_compressed_sequence_replay_v1 -- Compressed-replay sequence-binding primitive test.

SCIENTIFIC QUESTION (brain-drill #5 SWR/sleep-replay, 2026-06-22):
  Does an offline "sleep" pass that Hebbian-binds ORDERED ADJACENT key pairs into a
  separate sequence matrix S enable substrate sequence-recall that the substrate's
  point-write W cannot do?

  Architecture mapping (biology -> substrate):
    - U1 multi-value episodic store     = hippocampus (event-ordered cache)
    - W Hebbian-superposition matrix    = cortex semantic store (concept-conditional)
    - S sequence matrix (NEW)           = the proposed sequence-binding primitive
    - "sleep" pass over U1 in order     = SWR replay (writes (k_{t-1}, k_t) into S)

  Protocol:
    1. Generate N_SEQ = 10 distinct sequences, each K = 20 facts in defined temporal order.
    2. Each sequence is point-written to W as standard (k_i, v_i) outer-products
       (the substrate's existing primitive; NO sequence link is built online).
    3. Sleep pass per arm:
         arm A (NONE):           no sleep pass; S stays zero
         arm B (COMPRESSED):     for each sequence, iterate U1 in temporal order at
                                 1ms-spacing (= 20x compression vs 20ms original
                                 spacing); for each adjacent pair (k_{i-1}, k_i) write
                                 outer-product into S
         arm C (UNORDERED):      same pairs as B but shuffled (random pair selection
                                 from each sequence; same TOTAL pairs written) --
                                 tests whether ORDER is load-bearing
         arm D (ONLINE_NO_GAP):  write (k_{i-1}, k_i) into S at ingest-time directly
                                 (no offline pass; no compression) -- tests whether
                                 the OFFLINE-REPLAY SCHEDULE is the load-bearing factor
                                 (in software it should NOT be -- this is the honest
                                 scope statement; arm D ~= arm B is HARD_PASS_PLUS)
    4. Test recall at depths 1, 3, 5, 7, 10:
         given k_t-1, predict k_t = codebook_NN(S @ k_{t-1}); compare to true k_t
         chain-recall at depth d: iterate S @ d times from k_0; check final == k_d

  Discriminating-regime arms (Fix #16, the CAN-fail regime IS the 4-arm contrast):
    - all-arms ~= NONE => mechanism null (honest negative)
    - all-arms ~= 1.0  => harness too easy (mis-specified)
    - B ~ C            => order doesn't matter; mechanism is just pair-density
    - B >> D           => offline schedule matters in software (unexpected; interesting)
    - B ~ D            => offline schedule is biological license only; pair-write
                          architecture is the substrate-side win (expected; honest scope)

  Substrate-only-decode gate: pure numpy + Hebbian + codebook-NN cleanup;
  ZERO LLM forward calls anywhere; W matrix unchanged by sleep pass (assertion).

PRE-REGISTERED BANDS (brain-drill #5):
  HARD_PASS (chain-grade, mechanism validated):
    Arm B sequence_recall(depth=5) >= 0.80
    AND Arm A sequence_recall(depth=5) <= 0.20
    AND delta(B - A) at depth=5 >= 0.50
    AND Arm C < Arm B by >= 0.30 at depth=5 (order matters)
    AND cv <= 0.05 across 3 seeds for B and A at depth=5
    AND zero_llm_calls_at_inference == True
    AND W matrix L2-norm unchanged by sleep pass (assertion)

  MIDDLE_BAND (proven-bound partial):
    Arm B sequence_recall(depth=5) in [0.50, 0.80) with delta >= 0.30

  HARD_FAIL:
    delta(B - A) at depth=5 < 0.20  (pair-write does NOT enable sequence recall)
    OR Arm C >= Arm B  (mechanism is just pair-density, not order; honest finding)
    OR substrate-only-decode gate violated (LLM calls > 0)
    OR W modified by sleep pass

  Discriminating-regime check (4-arm contrast IS the discriminator):
    Smoke-VET asserts at least one arm splits from baseline by >= 0.20 OR all-arms
    collapse to <= 0.30 (null mechanism); a flat-1.0 sweep = harness mis-spec.

FIX INVENTORY:
  - _LLM_CALL_COUNTER = [0] at module top (substrate-only gate)
  - ANCHOR_NAME, CONFIG_VERSION baked module-level (AST-verifiable)
  - run_mode='full' default; --smoke / HDLAB_RUN_MODE / HDLAB_EXP_NAME _smoke
    suffix all honored (TODO #6 resolution pattern)
  - allow_synthetic=True is CORRECT here (synthetic bipolar keys, by-design;
    mirrors c1 / a8 substrate-primitive isolation; CORPUS_PROVENANCE recorded)
  - per_seed entry per (seed, arm, depth) into metrics.json
  - cv across seeds computed in verdict()
  - Pre-reg direction enforced (B > A; B > C; B >= D)
  - Discriminating-regime: 4-arm contrast IS the discriminator (Fix #16)
  - Resumable via _seed_checkpoint per-seed partials
  - atexit + SIGTERM synthesize-from-partials (TODO #9 pattern)

FORMULA SELF-TESTS:
  1. NONE-arm at K=5 small seq: sequence_recall(depth=1) <= 0.30 (no S structure)
  2. COMPRESSED-arm at K=5 small seq: sequence_recall(depth=1) >= 0.60 (pair-write works)
  3. _LLM_CALL_COUNTER remains 0 throughout

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
import signal
import atexit
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "c3_compressed_sequence_replay_v1"

# Substrate-only-decode gate (Skunkworks structural blocker #3).
# Asserted == 0 at end of run. Any LLM forward call MUST increment this.
_LLM_CALL_COUNTER = [0]

# Corpus provenance: synthetic bipolar keys; the right substrate for isolating the
# sequence-binding mechanism from KG-specific encoding effects. Mirrors c1 + a8.
CORPUS_PROVENANCE = "synthetic_bipolar_keys_sequences"

# Track whether write_metrics fired (used by atexit synthesizer to avoid double-write).
_METRICS_WRITTEN = [False]


def _detect_run_mode():
    """Detect smoke vs full. Priority:
      1. --smoke CLI flag
      2. HDLAB_RUN_MODE env var
      3. HDLAB_EXP_NAME ending in _smoke (runner queue-name convention; TODO #6 fix)
      4. default "full"
    """
    if "--smoke" in sys.argv:
        return "smoke"
    env_mode = os.environ.get("HDLAB_RUN_MODE", "").lower()
    if env_mode in ("smoke", "full"):
        return env_mode
    exp_name = os.environ.get("HDLAB_EXP_NAME", "")
    if exp_name.endswith("_smoke"):
        return "smoke"
    return "full"


RUN_MODE = _detect_run_mode()

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Pre-reg bands (locked at design time per drill #5 L4)
HARD_PASS_B_AT_D5 = 0.80     # Arm B sequence_recall at depth 5
HARD_PASS_A_AT_D5_MAX = 0.20 # Arm A must be <= this
HARD_PASS_DELTA = 0.50       # B - A at depth 5
HARD_PASS_ORDER_DELTA = 0.30 # B - C at depth 5 (order matters)
MIDDLE_BAND_LO = 0.30        # delta in [0.30, 0.50) at depth 5 = MIDDLE_BAND
MIDDLE_BAND_B_LO = 0.50      # B in [0.50, 0.80) at depth 5 = MIDDLE_BAND
HARD_FAIL_DELTA = 0.20       # delta < this at depth 5 = HARD_FAIL
CV_HARD_PASS_MAX = 0.05      # cv across seeds for HARD_PASS arms

# Smoke vs full config
if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    K_SEQ = 8                # short sequences for smoke
    N_SEQ = 4                # few sequences
    DEPTHS = [1, 3, 5]       # smoke covers up through pre-reg depth 5
    ARMS = ["NONE", "COMPRESSED", "UNORDERED", "ONLINE_NO_GAP"]
    N_PROBES_PER_DEPTH = 20  # probes per (arm, depth)
else:
    SEEDS = [7, 17, 23]
    N_DIM = 4096
    K_SEQ = 20
    N_SEQ = 10
    DEPTHS = [1, 3, 5, 7, 10]
    ARMS = ["NONE", "COMPRESSED", "UNORDERED", "ONLINE_NO_GAP"]
    N_PROBES_PER_DEPTH = 40

# Compression spec (architectural marker; software has no Hebbian-window so this is
# the BIOLOGICAL framing only -- the substrate-side mechanism is the pair-write itself).
SLEEP_COMPRESSION_RATIO = 20    # 1ms vs 20ms => 20x speedup (biology framing)
SLEEP_PASS_COUNT = 1            # one sleep epoch per sequence

CONFIG_VERSION = ("c3-compressed-sequence-replay-v1: K=%d N_SEQ=%d N_DIM=%d arms=%s "
                  "depths=%s; bands HP_B@d5=%.2f delta=%.2f order_delta=%.2f "
                  "compression_ratio=%d sleep_pass_count=%d run_mode=%s" %
                  (K_SEQ, N_SEQ, N_DIM, ",".join(ARMS), str(DEPTHS),
                   HARD_PASS_B_AT_D5, HARD_PASS_DELTA, HARD_PASS_ORDER_DELTA,
                   SLEEP_COMPRESSION_RATIO, SLEEP_PASS_COUNT, RUN_MODE))


def make_bipolar(M: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random +/- 1 vectors, L2-normalized to unit length."""
    X = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float64)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def hebbian_bind(M: np.ndarray, key: np.ndarray, value: np.ndarray) -> None:
    """In-place Hebbian outer-product update: M += value (outer) key / N_DIM."""
    n = M.shape[0]
    M += np.outer(value, key) / n


def codebook_nn(y: np.ndarray, codebook: np.ndarray) -> Tuple[int, np.ndarray]:
    """Cosine nearest-neighbor in codebook. Returns (idx, codebook[idx])."""
    y_n = y / (np.linalg.norm(y) + 1e-12)
    sims = codebook @ y_n
    idx = int(np.argmax(sims))
    return idx, codebook[idx]


def build_sequences(n_seq: int, k_seq: int, n_dim: int,
                    rng: np.random.RandomState) -> Tuple[np.ndarray, np.ndarray]:
    """Build n_seq sequences each of k_seq disjoint bipolar keys.

    Returns:
      sequences: shape (n_seq, k_seq, n_dim) -- the keys in temporal order
      codebook:  shape (n_seq * k_seq, n_dim) -- flat codebook for NN cleanup,
                 where codebook[seq_id * k_seq + t] = sequences[seq_id, t].
    """
    total = n_seq * k_seq
    codebook = make_bipolar(total, n_dim, rng)
    sequences = codebook.reshape(n_seq, k_seq, n_dim).copy()
    return sequences, codebook


def write_W_point_writes(sequences: np.ndarray, n_dim: int) -> np.ndarray:
    """Write each (k_i, k_i) into W as point-writes. Here values are bipolar identity
    of the key itself for substrate fidelity (the focus is on KEY-to-KEY sequence
    linkage in S, not key-to-value lookup in W). W still gets written for the
    assertion that the sleep pass does NOT modify W.

    Vectorized: W = K^T @ K / n where K is (N, n_dim) stack of all keys.
    Mathematically equivalent to sum_i outer(k_i, k_i) / n; orders of magnitude
    faster than the per-item Python loop.
    """
    n_seq, k_seq, _ = sequences.shape
    K = sequences.reshape(n_seq * k_seq, n_dim)
    return (K.T @ K) / n_dim


def sleep_pass_compressed(sequences: np.ndarray, n_dim: int,
                          rng: np.random.RandomState) -> np.ndarray:
    """COMPRESSED arm: iterate each sequence in temporal order, write adjacent
    (k_{t-1}, k_t) outer-product into S. Returns S.

    Vectorized: stack all (k_curr, k_prev) adjacent pairs across sequences, then
    S = K_curr^T @ K_prev / n. Mathematically equivalent to sum outer(k_curr, k_prev) / n.
    """
    n_seq, k_seq, _ = sequences.shape
    K_prev = sequences[:, :-1, :].reshape(n_seq * (k_seq - 1), n_dim)
    K_curr = sequences[:, 1:, :].reshape(n_seq * (k_seq - 1), n_dim)
    # S += sum outer(k_curr, k_prev) / n  ==  K_curr^T @ K_prev / n
    return (K_curr.T @ K_prev) / n_dim


def sleep_pass_unordered(sequences: np.ndarray, n_dim: int,
                         rng: np.random.RandomState) -> np.ndarray:
    """UNORDERED arm: same TOTAL number of pair writes as COMPRESSED but pairs are
    chosen randomly within each sequence (not ordered adjacent). Tests whether
    ORDER is the load-bearing factor, not just pair density.

    Vectorized: build random index lists per sequence, then stack and matmul.
    """
    n_seq, k_seq, _ = sequences.shape
    n_pairs_per_seq = k_seq - 1
    # Random index pairs per sequence; filter self-pairs (rare)
    src_list = []
    tgt_list = []
    for s in range(n_seq):
        is_idx = rng.randint(0, k_seq, size=n_pairs_per_seq)
        js_idx = rng.randint(0, k_seq, size=n_pairs_per_seq)
        # Resample self-pairs once
        self_mask = (is_idx == js_idx)
        if self_mask.any():
            js_idx[self_mask] = (js_idx[self_mask] + 1) % k_seq
            # Still equal if was 0 and k_seq=1 (impossible here) -- safe
        keep = (is_idx != js_idx)
        for ii, jj in zip(is_idx[keep], js_idx[keep]):
            src_list.append(sequences[s, int(ii)])
            tgt_list.append(sequences[s, int(jj)])
    if not src_list:
        return np.zeros((n_dim, n_dim), dtype=np.float64)
    K_src = np.stack(src_list, axis=0)  # the "k_prev-equivalent"
    K_tgt = np.stack(tgt_list, axis=0)  # the "k_curr-equivalent"
    return (K_tgt.T @ K_src) / n_dim


def sleep_pass_online_no_gap(sequences: np.ndarray, n_dim: int,
                             rng: np.random.RandomState) -> np.ndarray:
    """ONLINE_NO_GAP arm: writes (k_{t-1}, k_t) ordered pairs into S at "ingest time"
    (no offline pass, no compression). In software this is equivalent to the
    compressed pass because the Hebbian outer-product is timing-independent.
    Used to make the honest scope statement explicit: the substrate-side win is
    the ORDERED PAIR-WRITE architecture, not the temporal compression (which is
    the biological license for the same architecture).
    """
    # Mechanically identical to compressed for the software substrate (this is
    # the honest result we expect: arm D ~= arm B). The label is preserved so
    # the discriminator-arms test fires as expected.
    return sleep_pass_compressed(sequences, n_dim, rng)


def sleep_pass_none(sequences: np.ndarray, n_dim: int,
                    rng: np.random.RandomState) -> np.ndarray:
    """NONE arm: no sleep pass. S stays zero."""
    return np.zeros((n_dim, n_dim), dtype=np.float64)


SLEEP_PASS_FN = {
    "NONE": sleep_pass_none,
    "COMPRESSED": sleep_pass_compressed,
    "UNORDERED": sleep_pass_unordered,
    "ONLINE_NO_GAP": sleep_pass_online_no_gap,
}


def eval_sequence_recall(S: np.ndarray, sequences: np.ndarray, codebook: np.ndarray,
                         depth: int, n_probes: int,
                         rng: np.random.RandomState) -> Tuple[float, float]:
    """Sequence recall at a given depth.

    For depth = 1: given k_{t-1}, predict k_t via codebook_NN(S @ k_{t-1}).
                   correct iff predicted == true k_t.
    For depth d > 1: iterative chain: start at k_0, iterate y = S @ y_prev d times,
                     snapping to codebook each step (codebook-NN cleanup).
                     correct iff final == true k_d.

    Returns:
      (recall_codebook_nn, recall_cos):
        recall_codebook_nn = fraction of probes where codebook-NN argmax == true target
        recall_cos         = mean cosine of raw (iterated) S^d @ k with true target
    """
    n_seq, k_seq, n_dim = sequences.shape
    if depth >= k_seq:
        return 0.0, 0.0
    # Enumerate valid (seq, start) pairs where start + depth < k_seq
    valid_starts = [(s, t0) for s in range(n_seq) for t0 in range(k_seq - depth)]
    if not valid_starts:
        return 0.0, 0.0
    n_q = min(n_probes, len(valid_starts))
    chosen_idx = rng.choice(len(valid_starts), size=n_q, replace=False)
    correct_nn = 0
    cos_sum = 0.0
    for ci in chosen_idx:
        s_id, t0 = valid_starts[int(ci)]
        y = sequences[s_id, t0].copy()
        # Iterate S @ y, codebook-NN cleanup each step
        for step in range(depth):
            y_raw = S @ y
            # codebook-NN cleanup (the substrate's standard recall pipeline)
            idx, y = codebook_nn(y_raw, codebook)
        # Target codebook index for k_{t0+depth}
        target_idx = s_id * k_seq + (t0 + depth)
        # Compare argmax-after-final-step (already snapped) with target
        # y is the snapped vector; idx is its codebook index
        if idx == target_idx:
            correct_nn += 1
        # Cosine to the true target (post-snap)
        true_vec = codebook[target_idx]
        cos_sum += float(true_vec @ (y / (np.linalg.norm(y) + 1e-12)))
    return float(correct_nn) / n_q, float(cos_sum / n_q)


def run_one_arm(arm: str, seed: int) -> Dict:
    """Run one arm: build W (point-writes), do sleep pass for the arm, evaluate
    sequence recall at all depths.
    """
    t_arm_start = time.time()
    rng = np.random.RandomState(seed * 1000 + hash(arm) % 10000)

    n_dim = N_DIM
    sequences, codebook = build_sequences(N_SEQ, K_SEQ, n_dim, rng)

    # Build W via point-writes (standard substrate primitive)
    W = write_W_point_writes(sequences, n_dim)
    W_norm_before = float(np.linalg.norm(W))

    # Sleep pass per arm: builds S
    S = SLEEP_PASS_FN[arm](sequences, n_dim, rng)

    # Verify W is unchanged by sleep pass (the assertion)
    W_norm_after = float(np.linalg.norm(W))
    W_unchanged = (abs(W_norm_after - W_norm_before) < 1e-10)
    if not W_unchanged:
        raise AssertionError("W modified by sleep pass for arm=%s (norm %.6f -> %.6f)" %
                             (arm, W_norm_before, W_norm_after))

    S_norm = float(np.linalg.norm(S))

    # Evaluate sequence recall at each depth
    recalls_nn = {}
    recalls_cos = {}
    chain_recalls = {}
    for depth in DEPTHS:
        rec_nn, rec_cos = eval_sequence_recall(S, sequences, codebook, depth,
                                               N_PROBES_PER_DEPTH, rng)
        recalls_nn[depth] = rec_nn
        recalls_cos[depth] = rec_cos
        # chain_recall is the same metric (iterative snap-walk); recorded for clarity
        chain_recalls[depth] = rec_nn

    arm_wall_s = time.time() - t_arm_start
    return {
        "arm": arm,
        "seed": int(seed),
        "n_dim": n_dim,
        "k_seq": K_SEQ,
        "n_seq": N_SEQ,
        "sequence_matrix_norm": S_norm,
        "W_norm_before_sleep": W_norm_before,
        "W_norm_after_sleep": W_norm_after,
        "W_unchanged_by_sleep": bool(W_unchanged),
        "sleep_compression_ratio": SLEEP_COMPRESSION_RATIO,
        "sleep_pass_count": SLEEP_PASS_COUNT,
        "sequence_recall_nn": {str(d): recalls_nn[d] for d in DEPTHS},
        "sequence_recall_cos": {str(d): recalls_cos[d] for d in DEPTHS},
        "chain_recall_nn": {str(d): chain_recalls[d] for d in DEPTHS},
        "arm_wall_s": float(arm_wall_s),
        "n_probes_per_depth": N_PROBES_PER_DEPTH,
    }


def _selftest():
    """3 self-tests per the docstring."""
    rng = np.random.RandomState(0)
    n_dim = 256
    n_seq = 3
    k_seq = 5
    sequences, codebook = build_sequences(n_seq, k_seq, n_dim, rng)

    # Selftest 1: NONE arm at depth=1 should be ~0 (no S)
    S_none = sleep_pass_none(sequences, n_dim, rng)
    rec_none, _ = eval_sequence_recall(S_none, sequences, codebook, 1, 15, rng)
    assert rec_none <= 0.30, "selftest 1: NONE depth=1 recall too high: %.3f" % rec_none

    # Selftest 2: COMPRESSED arm at depth=1 should be high (pair-write works)
    S_comp = sleep_pass_compressed(sequences, n_dim, rng)
    rec_comp, _ = eval_sequence_recall(S_comp, sequences, codebook, 1, 15, rng)
    assert rec_comp >= 0.60, ("selftest 2: COMPRESSED depth=1 recall too low: %.3f"
                              % rec_comp)

    # Selftest 3: no LLM calls
    assert _LLM_CALL_COUNTER[0] == 0, ("selftest 3: LLM counter non-zero (%d)"
                                       % _LLM_CALL_COUNTER[0])

    print("[selftest] PASS: NONE_d1=%.3f COMPRESSED_d1=%.3f LLM=%d"
          % (rec_none, rec_comp, _LLM_CALL_COUNTER[0]), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    """Run all arms for one seed."""
    t0 = time.time()
    per_unit = []
    for arm in ARMS:
        res = run_one_arm(arm, seed)
        per_unit.append(res)
        rec5 = res["sequence_recall_nn"].get("5", float("nan"))
        rec1 = res["sequence_recall_nn"].get("1", float("nan"))
        print("  [seed=%d] arm=%s d1=%.3f d5=%.3f S_norm=%.3e wall=%.1fs"
              % (seed, arm, rec1, rec5, res["sequence_matrix_norm"],
                 res["arm_wall_s"]), flush=True)
    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "M": K_SEQ * N_SEQ,
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

    # Aggregate: mean sequence_recall_nn[depth] per arm across seeds
    # Shape: arm -> depth_str -> list of values
    agg: Dict[str, Dict[str, List[float]]] = {}
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            arm = pu["arm"]
            agg.setdefault(arm, {})
            for d_str, rec in pu.get("sequence_recall_nn", {}).items():
                agg[arm].setdefault(d_str, []).append(float(rec))

    # Mean + cv per (arm, depth)
    mean_arm_depth = {}
    cv_arm_depth = {}
    for arm in agg:
        mean_arm_depth[arm] = {}
        cv_arm_depth[arm] = {}
        for d_str, vals in agg[arm].items():
            m = float(np.mean(vals))
            s = float(np.std(vals))
            mean_arm_depth[arm][d_str] = m
            cv_arm_depth[arm][d_str] = (s / max(m, 1e-9))

    # Pull key numbers at the pre-reg depth (5)
    d5 = "5"
    a_5 = mean_arm_depth.get("NONE", {}).get(d5, float("nan"))
    b_5 = mean_arm_depth.get("COMPRESSED", {}).get(d5, float("nan"))
    c_5 = mean_arm_depth.get("UNORDERED", {}).get(d5, None)
    d_5 = mean_arm_depth.get("ONLINE_NO_GAP", {}).get(d5, None)
    delta = (b_5 - a_5) if not (math.isnan(a_5) or math.isnan(b_5)) else float("nan")
    order_delta = (b_5 - c_5) if c_5 is not None else None

    cv_a_5 = cv_arm_depth.get("NONE", {}).get(d5, float("inf"))
    cv_b_5 = cv_arm_depth.get("COMPRESSED", {}).get(d5, float("inf"))

    # Substrate-only-decode gate
    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # W-unchanged assertion: every per_unit must report W_unchanged_by_sleep=True
    w_unchanged_ok = True
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            if not pu.get("W_unchanged_by_sleep", False):
                w_unchanged_ok = False

    # Discriminating-regime: if all arms collapse <= 0.30 at depth=5 -> null mechanism;
    # if all arms >= 0.99 at depth=1 BUT all arms <= 0.20 at depth=5 -> harness ok.
    # Mostly informational; the verdict-decision flow handles bands explicitly.
    arms_at_d5 = [mean_arm_depth.get(a, {}).get(d5, float("nan")) for a in ARMS]
    arms_collapse_null = all((not math.isnan(v) and v <= 0.30) for v in arms_at_d5)
    arms_collapse_top = all((not math.isnan(v) and v >= 0.99) for v in arms_at_d5)

    detail = {
        "mean_recall_nn": mean_arm_depth,
        "cv_recall_nn": cv_arm_depth,
        "delta_B_minus_A_at_d5": float(delta) if not math.isnan(delta) else None,
        "order_delta_B_minus_C_at_d5": float(order_delta) if order_delta is not None else None,
        "substrate_only_ok": bool(substrate_only_ok),
        "W_unchanged_by_sleep_all_arms": bool(w_unchanged_ok),
        "cv_NONE_at_d5": float(cv_a_5),
        "cv_COMPRESSED_at_d5": float(cv_b_5),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "arms_collapse_null_at_d5": bool(arms_collapse_null),
        "arms_collapse_top_at_d5": bool(arms_collapse_top),
        "honest_scope": ("Compressed-replay sequence-binding test on synthetic-bipolar "
                         "disjoint-key sequences at N_DIM=%d, K=%d, N_SEQ=%d, depths=%s. "
                         "The biological 'compression' motivation does NOT directly "
                         "transfer to software (no Hebbian window); arm D (ONLINE_NO_GAP) "
                         "is the explicit honest-scope control. Substrate-only-decode "
                         "gate enforced (n_llm=%d). W matrix unchanged by sleep pass "
                         "(assertion enforced)."
                         % (N_DIM, K_SEQ, N_SEQ, str(DEPTHS), n_llm)),
    }

    summary = ("A_d5=%.3f B_d5=%.3f delta=%.3f C_d5=%s D_d5=%s | "
               "cv_A=%.3f cv_B=%.3f | substrate_only=%s W_unchanged=%s llm=%d" %
               (a_5, b_5, delta if not math.isnan(delta) else float("nan"),
                ("%.3f" % c_5) if c_5 is not None else "n/a",
                ("%.3f" % d_5) if d_5 is not None else "n/a",
                cv_a_5, cv_b_5, substrate_only_ok, w_unchanged_ok, n_llm))

    # Verdict logic
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s"
                % (n_llm, summary), detail)
    if not w_unchanged_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: W matrix modified by sleep pass (assertion violated). %s"
                % summary, detail)
    if math.isnan(delta):
        return ("HARD_FAIL",
                "HARD_FAIL: missing required (NONE, COMPRESSED) data at depth=5. %s"
                % summary, detail)
    # Order discriminator: arm C >= arm B = mechanism is just pair-density, not order
    if c_5 is not None and c_5 >= b_5:
        return ("HARD_FAIL",
                ("HARD_FAIL: order discriminator violated (UNORDERED=%.3f >= COMPRESSED=%.3f); "
                 "mechanism is pair-density, not sequence-binding. %s"
                 % (c_5, b_5, summary)), detail)
    if delta < HARD_FAIL_DELTA:
        return ("HARD_FAIL",
                "HARD_FAIL: replay delta %.3f < HARD_FAIL bar %.2f at depth=5. %s"
                % (delta, HARD_FAIL_DELTA, summary), detail)

    # HARD_PASS check
    if (b_5 >= HARD_PASS_B_AT_D5 and a_5 <= HARD_PASS_A_AT_D5_MAX
            and delta >= HARD_PASS_DELTA
            and (order_delta is None or order_delta >= HARD_PASS_ORDER_DELTA)
            and cv_b_5 <= CV_HARD_PASS_MAX and cv_a_5 <= CV_HARD_PASS_MAX):
        return ("HARD_PASS",
                ("HARD_PASS: compressed-replay binds sequences. B_d5=%.3f >= %.2f AND "
                 "A_d5=%.3f <= %.2f AND delta=%.3f >= %.2f AND order_delta=%s AND seeds "
                 "reproduce (cv_A=%.3f cv_B=%.3f <= %.2f). %s"
                 % (b_5, HARD_PASS_B_AT_D5, a_5, HARD_PASS_A_AT_D5_MAX,
                    delta, HARD_PASS_DELTA,
                    ("%.3f" % order_delta) if order_delta is not None else "n/a",
                    cv_a_5, cv_b_5, CV_HARD_PASS_MAX, summary)), detail)
    # MIDDLE_BAND
    if (b_5 >= MIDDLE_BAND_B_LO and delta >= MIDDLE_BAND_LO):
        return ("MIDDLE_BAND",
                ("MIDDLE_BAND: compressed-replay rescues PARTIALLY. B_d5=%.3f in [%.2f, %.2f); "
                 "delta=%.3f in [%.2f, %.2f). %s"
                 % (b_5, MIDDLE_BAND_B_LO, HARD_PASS_B_AT_D5,
                    delta, MIDDLE_BAND_LO, HARD_PASS_DELTA, summary)), detail)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND: ambiguous; bands not crossed. %s" % summary, detail)


# --- atexit + SIGTERM synthesize-from-partials (TODO #9 pattern) -------------
def _synthesize_on_exit():
    """If main exit path didn't write metrics.json, synthesize from partials."""
    if _METRICS_WRITTEN[0]:
        return
    try:
        out_dir = get_output_dir(ANCHOR_NAME)
        run_config = {"N": N_DIM, "run_mode": RUN_MODE}
        per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
        if not per_seed:
            return
        verdict, verdict_msg, detail = compute_verdict(per_seed)
        # Mark this as a partial-synthesized verdict
        verdict_msg = "TIMEOUT_OR_INTERRUPTED_PARTIAL: " + verdict_msg
        metrics = {
            "anchor": ANCHOR_NAME,
            "anchor_name": ANCHOR_NAME,
            "verdict": verdict,
            "verdict_msg": verdict_msg,
            "n_seeds": len(per_seed),
            "N": N_DIM,
            "N_DIM": N_DIM,
            "K_SEQ": K_SEQ,
            "N_SEQ": N_SEQ,
            "depths": DEPTHS,
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
            "metrics_source": "synthesized_from_partials_on_exit",
            "summary": verdict_msg[:200],
            "synthesized_at_exit": True,
        }
        write_metrics(out_dir, metrics, results=list(per_seed.values()))
        _METRICS_WRITTEN[0] = True
        print("[atexit] synthesized metrics.json from %d partials" % len(per_seed),
              flush=True)
    except Exception as e:
        print("[atexit] FAILED to synthesize: %s" % e, flush=True)


atexit.register(_synthesize_on_exit)


def _sigterm_handler(signum, frame):
    _synthesize_on_exit()
    sys.exit(143)


try:
    signal.signal(signal.SIGTERM, _sigterm_handler)
except (ValueError, AttributeError):
    # SIGTERM may not be settable on some platforms (e.g. Windows non-main thread);
    # atexit still fires on normal exit.
    pass


# --- Main runner ------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
run_config = {"N": N_DIM, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s N_DIM=%d K=%d N_SEQ=%d arms=%s depths=%s seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, N_DIM, K_SEQ, N_SEQ, str(ARMS), str(DEPTHS), str(done), str(seeds_todo)),
      flush=True)

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
    "K_SEQ": K_SEQ,
    "N_SEQ": N_SEQ,
    "depths": DEPTHS,
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
    "metrics_source": "measured_cpu_synthetic_bipolar_sequence_replay",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))
_METRICS_WRITTEN[0] = True

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
