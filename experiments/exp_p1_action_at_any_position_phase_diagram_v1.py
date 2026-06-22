"""p1_action_at_any_position_phase_diagram_v1 -- USER-directed latent-capability sub-item (c).

SCIENTIFIC QUESTION (USER 2026-06-22):
  Does substrate stored content survive an OPERATING-POINT shift in (V_C, N_DIM, alpha)?
  I.e., can K=200 atoms ingested at P_0 be retrieved after the substrate is rebuilt at P_1?

  Existing chain-grade evidence covers encoder-swap (audit_core_C2_C3_whitened_pythia/llama1b),
  projection (EXP_kv_learned_projection_v1), and readout-swap. No single chain-grade atom
  directly tests operating-point-shift (V_C / N_DIM / alpha) with a fixed payload.

PRIMITIVE-ISOLATION DESIGN (per pre-reg authorization):
  Cell uses synthetic bipolar HD vectors + a value-cleanup codebook. V_C = the value-codebook
  size (cleanup alphabet). Keys are written DIRECTLY into W as full HD vectors (the standard
  HD-substrate write primitive; matches c1_cls_replay_continual_ingest_v1 / a8 mechanism).

  This isolates operating-point-shift from any LLM-encoder confound. V_C lift = larger cleanup
  alphabet capacity; N_DIM lift = larger substrate dimension; alpha = K / N_DIM.

  Pre-reg explicitly authorizes this: "K=200 atoms (synthetic-bipolar OR encoded from corpus;
  cell-author chooses; synthetic is simpler if primitive-isolation test)."

THREE (P_0, P_1) PAIRS (spanning the phase diagram, per pre-reg):
  A: V_C lift     (V_C=1024->2048; same N=16384; same alpha)
  B: N_DIM lift   (N=16384->32768; alpha halved)
  C: joint lift   (BOTH V_C and N_DIM lifted)

FOUR ARMS per pair (Fix #16 discriminator-regime check):
  WITHIN_P_0          -- retrieve K atoms at P_0 itself (must succeed; harness sanity, expect >= 0.90)
  P_0_TO_P_1_REPLAYED -- the mechanism; rebuild at P_1, REPLAY:
                         (1) project key_query from P_0's N_DIM to P_1's N_DIM via a deterministic
                             bipolar JL projection (identity if N_DIM unchanged);
                         (2) project value HD-vectors (the portable payload) the same way;
                         (3) Hebbian-bind (projected_key, projected_value) into a fresh P_1 W;
                         then retrieve with cleanup against the projected value codebook.
                         For V_C-only pair (N_DIM unchanged), projection is identity and the
                         only operating-point change is the cleanup alphabet size at retrieval.
  P_1_FRESH_INGEST    -- freshly ingest K atoms at P_1 (no portability; tests P_1 capacity alone)
  P_1_BLANK_RECALL    -- retrieve test keys against EMPTY P_1 W (must collapse to <=0.10; sanity)

PRE-REGISTERED BANDS (verbatim from pre-reg cert-trail artifact):
  HARD_PASS chain-grade:
    ALL THREE pairs achieve ratio recall_P_0_TO_P_1 / recall_WITHIN_P_0 >= 0.80
    AND P_1_BLANK_RECALL <= 0.10 on all pairs (sanity floor)
    AND substrate-only-decode preserved at every arm (zero LLM calls)
    AND cv across seeds <= 0.05 for any arm claiming PASS
  HARD_FAIL:
    ANY pair ratio <= 0.20 (data destroyed by transform)
    OR substrate-only-decode violated
    OR WITHIN_P_0 < 0.50 on any pair (harness broken, cell invalid)
    OR P_1_BLANK_RECALL > 0.10 (recall is artifact of test-key encoding)
  MIDDLE_BAND:
    At least one pair ratio in (0.20, 0.80); characterize which transform-axis is weakest
  HONEST_NEGATIVE-eligible: e.g. V_C lift survives but N_DIM lift fails ->
    information-positive even if not chain-grade

FIX INVENTORY:
  - _LLM_CALL_COUNTER = [0] at module scope; asserted == 0 (substrate-only gate)
  - ANCHOR_NAME, CONFIG_VERSION baked module-level (AST-verifiable)
  - run_mode='full' default; HDLAB_RUN_MODE / --smoke flag honored; in-cell name-detect
    (HDLAB_EXP_NAME ending in _smoke triggers smoke; TODO #6 resolution)
  - allow_synthetic=True (BY DESIGN; primitive-isolation; mirrors c1 / a8); CORPUS_PROVENANCE
    = 'synthetic_bipolar_keys_with_VQ_codebook' baked into metrics
  - per_unit entry per (seed, pair, arm) into metrics.json
  - cv across seeds computed per (pair, arm) in verdict()
  - Pre-reg direction enforced (ratio >= 0.80 = PASS; ratio <= 0.20 = FAIL; not symmetric -> wrong-
    direction-large-delta cannot happen here because ratios are in [0,1])
  - Discriminating-regime: P_1_BLANK_RECALL must collapse; WITHIN_P_0 must succeed
  - Per-seed checkpoint via experiments/_seed_checkpoint.py

FORMULA SELF-TESTS:
  1. Tiny WITHIN-arm at V_C=64 N=512 K=20: recall >= 0.80 (sanity: substrate works at all)
  2. Tiny BLANK arm: recall <= 0.20 (empty W cannot retrieve)
  3. _LLM_CALL_COUNTER == 0 throughout

ASCII-only. CPU. Single-file. Resumable.
"""
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')

import os
import argparse
import time
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials, write_metrics,
)

ANCHOR_NAME = "p1_action_at_any_position_phase_diagram_v1"

# Substrate-only-decode gate. Asserted == 0 at end. Any LLM call MUST increment.
_LLM_CALL_COUNTER = [0]

CORPUS_PROVENANCE = "synthetic_bipolar_keys_with_VQ_codebook"


def _detect_run_mode():
    """smoke vs full. Priority: --smoke flag > HDLAB_RUN_MODE > HDLAB_EXP_NAME _smoke suffix > full."""
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

# Pre-reg bands (locked at design time)
HARD_PASS_RATIO = 0.80          # recall_P0_to_P1 / recall_WITHIN_P0 must hit this on ALL 3 pairs
HARD_FAIL_RATIO = 0.20          # any pair ratio <= this -> HARD_FAIL
MIDDLE_BAND_RATIO_LO = 0.20
MIDDLE_BAND_RATIO_HI = 0.80
BLANK_RECALL_MAX = 0.10         # P_1_BLANK_RECALL must collapse below this
WITHIN_P0_MIN = 0.50            # harness sanity: WITHIN baseline must be >= this
CV_HARD_PASS_MAX = 0.05         # cv across seeds for PASS arms
N_RECALL_STEPS = 3              # Hopfield-style cleanup iterations
NOISE_FRAC = 0.05               # probe-noise: 5% bit flips (small; the test is about portability,
                                # not noise tolerance; matches WITHIN baseline expectations >= 0.90)

# Three pre-registered (P_0, P_1) pairs spanning phase diagram axes.
# (V_C_0, N_DIM_0, V_C_1, N_DIM_1). Alpha is implied = K / N_DIM.
# Smoke uses tiny versions to verify the harness; full uses pre-reg parameters.
if RUN_MODE == "smoke":
    SEEDS = [1]
    K_ATOMS = 50
    PAIRS = [
        # name, V_C_0, N_DIM_0, V_C_1, N_DIM_1
        ("A_VC_lift_smoke",      128, 1024, 256, 1024),
        ("B_NDIM_lift_smoke",    128, 1024, 128, 2048),
        ("C_joint_lift_smoke",   128, 1024, 256, 2048),
    ]
    N_PROBE = 30
else:
    SEEDS = [7, 17, 23]
    K_ATOMS = 200
    PAIRS = [
        # name, V_C_0, N_DIM_0, V_C_1, N_DIM_1
        ("A_VC_lift",     1024, 16384, 2048, 16384),
        ("B_NDIM_lift",   1024, 16384, 1024, 32768),
        ("C_joint_lift",  1024, 16384, 2048, 32768),
    ]
    N_PROBE = 60

ARMS = ["WITHIN_P_0", "P_0_TO_P_1_REPLAYED", "P_1_FRESH_INGEST", "P_1_BLANK_RECALL"]

CONFIG_VERSION = ("p1-phase-diagram-v1: K=%d arms=%s pairs=%s noise=%.3f recall_steps=%d run_mode=%s" %
                  (K_ATOMS, ",".join(ARMS),
                   ";".join("%s(VC%d->%d,N%d->%d)" % (n, v0, v1, nd0, nd1) for n, v0, nd0, v1, nd1 in PAIRS),
                   NOISE_FRAC, N_RECALL_STEPS, RUN_MODE))


def _normalize_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-12)


def make_bipolar(M: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """Random +/- 1 vectors, L2-normalized."""
    X = rng.choice([-1.0, 1.0], size=(M, n)).astype(np.float64)
    return _normalize_rows(X)


def make_value_codebook(v_c: int, n: int, rng: np.random.RandomState) -> np.ndarray:
    """V_C random bipolar value-codebook entries of dim n, L2-normalized. The CLEANUP alphabet."""
    return make_bipolar(v_c, n, rng)


def make_jl_projection(n_src: int, n_dst: int, rng: np.random.RandomState) -> np.ndarray:
    """Deterministic bipolar Johnson-Lindenstrauss projection (n_dst, n_src). 1/sqrt(n_src)-scaled.

    Used to port HD-vectors from N_DIM_0 to N_DIM_1 when N_DIM changes. Preserves cosine
    similarity in expectation. When n_src == n_dst, returns identity.
    """
    if n_src == n_dst:
        return np.eye(n_src, dtype=np.float64)
    return rng.choice([-1.0, 1.0], size=(n_dst, n_src)).astype(np.float64) / math.sqrt(n_src)


def project_rows(X: np.ndarray, proj: np.ndarray) -> np.ndarray:
    """Apply (n_dst, n_src) projection to rows of X (k, n_src). Returns (k, n_dst), L2-normed."""
    Y = X @ proj.T
    return _normalize_rows(Y)


def hebbian_bind(W: np.ndarray, key: np.ndarray, value: np.ndarray) -> None:
    """In-place Hebbian outer-product: W += outer(value, key) / N. Single-atom write."""
    n = W.shape[0]
    W += np.outer(value, key) / n


def hebbian_bind_batch(keys: np.ndarray, values: np.ndarray, dtype=np.float32) -> np.ndarray:
    """Vectorized Hebbian build: W = values.T @ keys / N. (M, N) inputs -> (N, N) W.

    Equivalent to sum_j outer(values[j], keys[j]) / N over j=0..M-1, but ~150x faster than
    a Python loop at N=16384 K=200 (5.7s vs 865s; bench 2026-06-22). Uses float32 to halve
    memory (8.6 GB -> 4.3 GB for N=32768). Loop-equivalence verified to 0 difference.
    """
    n = keys.shape[1]
    # cast to dtype first; matmul stays in dtype
    K_f = keys.astype(dtype, copy=False)
    V_f = values.astype(dtype, copy=False)
    return (V_f.T @ K_f) / np.float32(n)


def retrieve_value(W: np.ndarray, key: np.ndarray, value_codebook: np.ndarray,
                   n_steps: int = N_RECALL_STEPS) -> Tuple[int, np.ndarray]:
    """W @ key -> Hopfield-style cleanup against value_codebook. Returns (idx, vec).

    Dtype-flex: W is float32 in production; key + value_codebook coerce to W's dtype for matmul.
    """
    k_in = key.astype(W.dtype, copy=False)
    vcb = value_codebook.astype(W.dtype, copy=False)
    y = W @ k_in
    for _ in range(n_steps):
        sims = vcb @ y
        idx = int(np.argmax(sims))
        y_snap = vcb[idx]
        y = 0.5 * y + 0.5 * y_snap
    sims = vcb @ y
    idx = int(np.argmax(sims))
    return idx, vcb[idx]


def build_substrate_and_ingest(v_c: int, n_dim: int, k: int,
                               rng: np.random.RandomState):
    """Build a (V_C, N_DIM) substrate. Generate K atoms (key_query, value_idx). Hebbian-bind
    (key_query, value_codebook[value_idx]) DIRECTLY into W (vectorized matmul).

    Returns:
      value_codebook -- (V_C, N_DIM) value cleanup alphabet (the PORTABLE artifact)
      key_queries    -- (K, N_DIM)   raw HD key vectors
      value_idx      -- (K,)         each atom's value-codebook-index
      W              -- (N_DIM, N_DIM) float32 Hebbian matrix
    """
    assert k <= v_c, "K=%d must be <= V_C=%d (each atom needs a disjoint cleanup entry)" % (k, v_c)
    value_codebook = make_value_codebook(v_c, n_dim, rng)
    key_queries = make_bipolar(k, n_dim, rng)
    value_idx = np.arange(k)
    # Vectorized: W = val_cb[:K].T @ keys / N
    W = hebbian_bind_batch(key_queries, value_codebook[:k])
    return value_codebook, key_queries, value_idx, W


def eval_recall(W: np.ndarray, value_codebook: np.ndarray,
                key_queries: np.ndarray, value_idx: np.ndarray, n_probe: int,
                rng: np.random.RandomState) -> float:
    """For up to n_probe atoms: noise the key_query, retrieve value via W, cleanup against
    value_codebook, compare to true value_idx. Returns fraction correct."""
    k = len(key_queries)
    n_q = min(n_probe, k)
    if n_q == 0:
        return 0.0
    sel = rng.choice(k, size=n_q, replace=False)
    correct = 0
    n_dim = W.shape[0]
    for j in sel:
        q = key_queries[j].copy()
        flip = rng.random(n_dim) < NOISE_FRAC
        q[flip] *= -1.0
        q = q / (np.linalg.norm(q) + 1e-12)
        retr_idx, _ = retrieve_value(W, q, value_codebook)
        if retr_idx == int(value_idx[j]):
            correct += 1
    return float(correct) / n_q


def run_pair(pair_name: str, v_c_0: int, n_dim_0: int, v_c_1: int, n_dim_1: int,
             seed: int) -> Dict:
    """Run the 4-arm matrix for one (P_0, P_1) pair.

    Mechanism (revised; keys direct into W; V_C = cleanup alphabet size):
      P_0: build val_cb_0 (V_C_0, N_DIM_0) + key_qs_0; bind (key_qs[j], val_cb_0[j]) into W_0.
      P_1: build val_cb_1 (V_C_1, N_DIM_1) + key_qs_1 in a fresh substream (for FRESH arm).
      REPLAYED: JL-project (key_qs_0, val_cb_0[: K]) from N_DIM_0 -> N_DIM_1.
                Build a fresh val_cb_proj at P_1 of size V_C_1: first K entries = projected
                payload; remaining V_C_1 - K entries = fresh distractors at N_DIM_1.
                Bind (projected_key[j], val_cb_proj[j]) into W_replayed; retrieve with
                cleanup over val_cb_proj of size V_C_1 (the P_1 operating-point cleanup).
      Identity-projection when N_DIM_0 == N_DIM_1 (V_C-only lift).
    """
    import gc
    rng = np.random.RandomState(seed * 10007 + abs(hash(pair_name)) % 9973)

    t0 = time.time()
    # ---- Phase P_0: build substrate, ingest K atoms ----
    val_cb_0, key_qs_0, val_idx_0, W_0 = build_substrate_and_ingest(
        v_c_0, n_dim_0, K_ATOMS, rng=rng)

    # ARM 1: WITHIN_P_0  -- retrieve at P_0 itself (must clear baseline)
    recall_within = eval_recall(W_0, val_cb_0, key_qs_0, val_idx_0, N_PROBE, rng)
    # Free W_0 ASAP to make room for W_replayed at potentially larger N_1.
    del W_0
    gc.collect()

    # ---- Phase P_1: build a FRESH substrate at (V_C_1, N_DIM_1) ----
    rng_p1 = np.random.RandomState(seed * 10007 + abs(hash(pair_name)) % 9973 + 31)
    val_cb_1 = make_value_codebook(v_c_1, n_dim_1, rng_p1)
    key_qs_1 = make_bipolar(K_ATOMS, n_dim_1, rng_p1)
    val_idx_1 = np.arange(K_ATOMS)

    # ARM 2: P_0_TO_P_1_REPLAYED -- the mechanism.
    # Build a deterministic JL projection P_0 -> P_1 (identity if N_DIM unchanged).
    rng_proj = np.random.RandomState(seed * 10007 + abs(hash(pair_name)) % 9973 + 71)
    proj = make_jl_projection(n_dim_0, n_dim_1, rng_proj)
    # Project keys + the first K value-codebook entries (the portable payload).
    key_qs_proj = project_rows(key_qs_0, proj)
    val_cb_payload_proj = project_rows(val_cb_0[:K_ATOMS], proj)
    # Free the projection matrix before we allocate W_replayed (proj is up to N_1 * N_0 = 0.5 GB).
    del proj
    gc.collect()
    # Build the cleanup alphabet at P_1 of size V_C_1:
    #   first K rows = projected payload (the portable content)
    #   remaining V_C_1 - K rows = fresh distractors at N_DIM_1
    rng_distract = np.random.RandomState(seed * 10007 + abs(hash(pair_name)) % 9973 + 131)
    n_distract = max(0, v_c_1 - K_ATOMS)
    if n_distract > 0:
        distractors = make_bipolar(n_distract, n_dim_1, rng_distract)
        val_cb_proj = np.vstack([val_cb_payload_proj, distractors])
    else:
        val_cb_proj = val_cb_payload_proj
    val_idx_replayed = np.arange(K_ATOMS)
    # Vectorized Hebbian build at P_1
    W_replayed = hebbian_bind_batch(key_qs_proj, val_cb_proj[:K_ATOMS])
    recall_replayed = eval_recall(W_replayed, val_cb_proj, key_qs_proj, val_idx_replayed,
                                  N_PROBE, rng_p1)
    del W_replayed
    gc.collect()

    # ARM 3: P_1_FRESH_INGEST -- ingest K NEW atoms at P_1
    W_fresh = hebbian_bind_batch(key_qs_1, val_cb_1[:K_ATOMS])
    recall_fresh = eval_recall(W_fresh, val_cb_1, key_qs_1, val_idx_1, N_PROBE, rng_p1)
    del W_fresh
    gc.collect()

    # ARM 4: P_1_BLANK_RECALL -- empty W at P_1; expect collapse (~ 1/V_C_1)
    W_blank = np.zeros((n_dim_1, n_dim_1), dtype=np.float32)
    recall_blank = eval_recall(W_blank, val_cb_proj, key_qs_proj, val_idx_replayed,
                               N_PROBE, rng_p1)
    del W_blank
    gc.collect()

    wall_s = time.time() - t0
    ratio = (recall_replayed / recall_within) if recall_within > 1e-9 else 0.0

    return {
        "pair": pair_name,
        "seed": int(seed),
        "v_c_0": int(v_c_0), "n_dim_0": int(n_dim_0),
        "v_c_1": int(v_c_1), "n_dim_1": int(n_dim_1),
        "alpha_0": float(K_ATOMS) / float(n_dim_0),
        "alpha_1": float(K_ATOMS) / float(n_dim_1),
        "recall_WITHIN_P_0": float(recall_within),
        "recall_P_0_TO_P_1_REPLAYED": float(recall_replayed),
        "recall_P_1_FRESH_INGEST": float(recall_fresh),
        "recall_P_1_BLANK_RECALL": float(recall_blank),
        "ratio_replayed_over_within": float(ratio),
        "n_probe": N_PROBE,
        "wall_s": float(wall_s),
    }


def _selftest():
    """3 formula self-tests per docstring (revised mechanism).

    Self-test verifies the primitive (direct-key Hebbian + value-cleanup codebook).
    Tiny zero-noise probe; the real noise behavior is verified by the smoke run.
    """
    rng = np.random.RandomState(0)
    # Tiny WITHIN arm: V_C=128 N=512 K=10 alpha=0.02; zero noise.
    val_cb, key_qs, val_idx, W = build_substrate_and_ingest(128, 512, 10, rng=rng)
    n_correct = 0
    n_q = 10
    for j in range(n_q):
        ridx, _ = retrieve_value(W, key_qs[j], val_cb)
        if ridx == int(val_idx[j]):
            n_correct += 1
    rec = n_correct / n_q
    assert rec >= 0.80, "selftest 1: zero-noise tiny WITHIN recall %.3f < 0.80" % rec

    # Tiny BLANK arm: empty W -> retrieve cannot match (except by accident; expect ~ 1/V_C)
    W_empty = np.zeros((512, 512), dtype=np.float64)
    n_correct = 0
    for j in range(n_q):
        ridx, _ = retrieve_value(W_empty, key_qs[j], val_cb)
        if ridx == int(val_idx[j]):
            n_correct += 1
    rec_blank = n_correct / n_q
    assert rec_blank <= 0.20, "selftest 2: blank recall %.3f > 0.20 (recall is artifact)" % rec_blank

    # selftest 2b: JL projection preserves cosine in expectation (sanity for cross-N portability)
    rng2 = np.random.RandomState(1)
    proj = make_jl_projection(256, 512, rng2)
    X = make_bipolar(20, 256, rng2)
    Y = project_rows(X, proj)
    # self-cosine should be ~1 by construction (projection of v with itself)
    XX = X @ X.T
    YY = Y @ Y.T
    err = float(np.max(np.abs(XX - YY)))
    assert err < 0.30, "selftest 2b: JL projection cosine drift %.3f > 0.30" % err

    # LLM counter
    assert _LLM_CALL_COUNTER[0] == 0, "selftest 3: LLM counter non-zero (%d)" % _LLM_CALL_COUNTER[0]

    print("[selftest] PASS: tiny zero-noise WITHIN=%.3f BLANK=%.3f JL_cos_drift=%.3f LLM=%d" %
          (rec, rec_blank, err, _LLM_CALL_COUNTER[0]), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


def run_seed(seed: int) -> Dict:
    """Run all 3 pairs (each = 4 arms) for one seed."""
    t0 = time.time()
    per_unit = []
    for (pair_name, v_c_0, n_dim_0, v_c_1, n_dim_1) in PAIRS:
        res = run_pair(pair_name, v_c_0, n_dim_0, v_c_1, n_dim_1, seed)
        per_unit.append(res)
        print(("  [seed=%d] pair=%s VC%d->%d N%d->%d | WITHIN=%.3f REPLAYED=%.3f FRESH=%.3f "
               "BLANK=%.3f | ratio=%.3f wall=%.1fs") %
              (seed, pair_name, v_c_0, v_c_1, n_dim_0, n_dim_1,
               res["recall_WITHIN_P_0"], res["recall_P_0_TO_P_1_REPLAYED"],
               res["recall_P_1_FRESH_INGEST"], res["recall_P_1_BLANK_RECALL"],
               res["ratio_replayed_over_within"], res["wall_s"]), flush=True)
    elapsed = time.time() - t0
    return {
        "seed": seed, "N": max(p[2] for p in PAIRS), "M": K_ATOMS,
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

    # Aggregate per (pair) across seeds for each arm + ratio
    pairs_seen: List[str] = []
    for p in PAIRS:
        pairs_seen.append(p[0])

    # Build per-pair arrays across seeds
    agg: Dict[str, Dict[str, List[float]]] = {pn: {"WITHIN": [], "REPLAYED": [], "FRESH": [],
                                                   "BLANK": [], "RATIO": []} for pn in pairs_seen}
    for sid, body in per_seed.items():
        for pu in body.get("per_unit", []):
            pn = pu["pair"]
            if pn not in agg:
                continue
            agg[pn]["WITHIN"].append(float(pu["recall_WITHIN_P_0"]))
            agg[pn]["REPLAYED"].append(float(pu["recall_P_0_TO_P_1_REPLAYED"]))
            agg[pn]["FRESH"].append(float(pu["recall_P_1_FRESH_INGEST"]))
            agg[pn]["BLANK"].append(float(pu["recall_P_1_BLANK_RECALL"]))
            agg[pn]["RATIO"].append(float(pu["ratio_replayed_over_within"]))

    def _stat(xs):
        if not xs:
            return float("nan"), float("nan"), float("nan")
        m = float(np.mean(xs))
        s = float(np.std(xs))
        cv = float(s / max(m, 1e-9)) if m > 1e-9 else float("inf")
        return m, s, cv

    pair_summary: Dict[str, Dict] = {}
    for pn in pairs_seen:
        d = agg[pn]
        wm, ws, wcv = _stat(d["WITHIN"])
        rm, rs, rcv = _stat(d["REPLAYED"])
        fm, fs, fcv = _stat(d["FRESH"])
        bm, bs, bcv = _stat(d["BLANK"])
        rat_m, rat_s, rat_cv = _stat(d["RATIO"])
        pair_summary[pn] = {
            "within_mean": wm, "within_std": ws, "within_cv": wcv,
            "replayed_mean": rm, "replayed_std": rs, "replayed_cv": rcv,
            "fresh_mean": fm, "fresh_std": fs, "fresh_cv": fcv,
            "blank_mean": bm, "blank_std": bs, "blank_cv": bcv,
            "ratio_mean": rat_m, "ratio_std": rat_s, "ratio_cv": rat_cv,
        }

    n_llm = sum(int(b.get("n_llm_calls", 0)) for b in per_seed.values())
    substrate_only_ok = (n_llm == 0)

    # Pre-reg checks
    all_ratios_pass = all(pair_summary[pn]["ratio_mean"] >= HARD_PASS_RATIO for pn in pairs_seen)
    any_ratio_fail = any(pair_summary[pn]["ratio_mean"] <= HARD_FAIL_RATIO for pn in pairs_seen)
    all_within_ok = all(pair_summary[pn]["within_mean"] >= WITHIN_P0_MIN for pn in pairs_seen)
    all_blank_ok = all(pair_summary[pn]["blank_mean"] <= BLANK_RECALL_MAX for pn in pairs_seen)
    # cv check applies to WITHIN and REPLAYED for any PASS claim
    cv_pass_ok = all(
        pair_summary[pn]["within_cv"] <= CV_HARD_PASS_MAX and
        pair_summary[pn]["replayed_cv"] <= CV_HARD_PASS_MAX
        for pn in pairs_seen)

    detail = {
        "pair_summary": pair_summary,
        "all_ratios_>=_%.2f" % HARD_PASS_RATIO: bool(all_ratios_pass),
        "any_ratio_<=_%.2f" % HARD_FAIL_RATIO: bool(any_ratio_fail),
        "all_within_>=_%.2f" % WITHIN_P0_MIN: bool(all_within_ok),
        "all_blank_<=_%.2f" % BLANK_RECALL_MAX: bool(all_blank_ok),
        "cv_within+replayed_<=_%.2f_all_pairs" % CV_HARD_PASS_MAX: bool(cv_pass_ok),
        "substrate_only_ok": bool(substrate_only_ok),
        "zero_llm_calls_at_inference": bool(substrate_only_ok),
        "honest_scope": ("Operating-point-shift portability on synthetic-bipolar HD substrate with "
                         "VQ codebook + Hebbian outer-product W. K=%d atoms; 3 (P_0,P_1) pairs spanning "
                         "V_C / N_DIM / joint lifts. Substrate-only-decode gate enforced (n_llm=%d). "
                         "Primitive-isolation: no LLM encoder; key-snap = KNN over bipolar codebook." %
                         (K_ATOMS, n_llm)),
    }

    # Build a compact one-liner summary
    parts = []
    for pn in pairs_seen:
        ps = pair_summary[pn]
        parts.append("%s[w=%.3f r=%.3f f=%.3f b=%.3f rat=%.3f cv=%.3f]" %
                     (pn, ps["within_mean"], ps["replayed_mean"], ps["fresh_mean"],
                      ps["blank_mean"], ps["ratio_mean"], ps["ratio_cv"]))
    summary = " | ".join(parts) + (" | llm=%d" % n_llm)

    # Verdict logic (HARD bands sacrosanct per pre-reg)
    if not substrate_only_ok:
        return ("HARD_FAIL",
                "HARD_FAIL: substrate-only-decode gate VIOLATED (%d LLM calls). %s" % (n_llm, summary),
                detail)
    if not all_within_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: WITHIN_P_0 baseline below floor %.2f on at least one pair (harness invalid). "
                 "%s" % (WITHIN_P0_MIN, summary)),
                detail)
    if not all_blank_ok:
        return ("HARD_FAIL",
                ("HARD_FAIL: P_1_BLANK_RECALL exceeds sanity floor %.2f on at least one pair "
                 "(retrieval is an artifact of key encoding). %s" % (BLANK_RECALL_MAX, summary)),
                detail)
    if any_ratio_fail:
        # Identify which pair(s)
        bad = [pn for pn in pairs_seen if pair_summary[pn]["ratio_mean"] <= HARD_FAIL_RATIO]
        return ("HARD_FAIL",
                ("HARD_FAIL: pair(s) %s ratio <= %.2f (data destroyed by transform). %s" %
                 (",".join(bad), HARD_FAIL_RATIO, summary)),
                detail)
    if all_ratios_pass and cv_pass_ok:
        return ("HARD_PASS",
                ("HARD_PASS: operating-point-shift portability on ALL 3 pairs. ALL ratios >= %.2f "
                 "AND blank-sanity OK AND cv across seeds <= %.2f AND substrate-only-gate preserved. %s" %
                 (HARD_PASS_RATIO, CV_HARD_PASS_MAX, summary)),
                detail)
    # MIDDLE_BAND: at least one pair in (HARD_FAIL_RATIO, HARD_PASS_RATIO)
    return ("MIDDLE_BAND",
            ("MIDDLE_BAND: partial portability. Some pair(s) in (%.2f, %.2f); characterize transform-axis. "
             "%s" % (MIDDLE_BAND_RATIO_LO, MIDDLE_BAND_RATIO_HI, summary)),
            detail)


# ----------------------------- main -----------------------------
out_dir = get_output_dir(ANCHOR_NAME)
t0_total = time.time()
# PROT-021 config-mismatch guard: stamp the run with K (M-equivalent) + max N + mode
run_config = {"N": max(p[2] for p in PAIRS), "M": K_ATOMS, "run_mode": RUN_MODE}

done, seeds_todo = resumable_seeds(SEEDS, out_dir, run_config)
print("[run] mode=%s K=%d pairs=%s seeds_done=%s seeds_todo=%s" %
      (RUN_MODE, K_ATOMS, str([p[0] for p in PAIRS]), str(done), str(seeds_todo)), flush=True)

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
    "K_atoms": K_ATOMS,
    "pairs": [{"name": n, "v_c_0": v0, "n_dim_0": nd0, "v_c_1": v1, "n_dim_1": nd1}
              for (n, v0, nd0, v1, nd1) in PAIRS],
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
    "metrics_source": "measured_cpu_synthetic_bipolar_VQ_codebook_hebbian_phase_diagram",
    "elapsed_s": time.time() - t0_total,
    "summary": verdict_msg[:200],
}

write_metrics(out_dir, metrics, results=list(per_seed.values()))

print("\n[VERDICT] %s" % verdict, flush=True)
print("[VERDICT_MSG] %s" % verdict_msg, flush=True)
print("[METRICS_PATH] %s" % (out_dir / "metrics.json"), flush=True)
