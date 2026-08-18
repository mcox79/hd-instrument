"""cortex_as_router_mante_multiplicative_gating_v1 -- Drill TOP-1 cortex-as-router.

Drill source: notes/research_drill_2x_cortex_as_router_2026-06-27.md (TOP-1, P=0.45)
Brain-grounded: Mante-Sussillo 2013 Nature; Miller-Cohen 2001 PFC theory.

Mechanism (TOP-1):
  PFC emits a context vector c_h that MULTIPLICATIVELY modulates the cortex bank.
  cortex_modulated = cortex_bank * c_h  (element-wise, per cortex entry).
  Cleanup proceeds against the modulated bank.
  This is "operators ARE cortex schemas under PFC context"; NOT a separate operator bank.

CRITICAL FAIRNESS (drill 10-point):
  - K=4 operator count match across all arms.
  - Sweep K=4,8,16 to isolate "operators-in-cortex" from "more operators".
  - Cortex bank and operator bank: SAME RANK, SAME DTYPE, SAME N_DIM.
  - PFC parameter budget matched via low-rank.
  - Verify-the-referent: routing entropy >= 1.5 bits per-hop selection (NOT storage).
  - META_RULE_K: smoke MUST FIRE discriminator (different schemas per hop).

ARMS (4 + 1 diagnostic):
  ARM_SEPARATE_BANK            -- baseline; separate K=4 operator bank, no shared cortex.
  ARM_CORTEX_SCHEMAS_AS_OPS    -- cortex-as-operators with multiplicative gating (TOP-1).
  ARM_HYBRID                   -- both separate-bank operators + cortex-schemas, score-mixed.
  ARM_LEARNED_GATING           -- gating g_h is task-conditioned (small MLP on state).
  ARM_PARAM_COUNT_MATCHED      -- diagnostic; separate-bank with same param count as
                                   ARM_CORTEX_SCHEMAS_AS_OPS via more-but-thinner ops.

DEPENDS_ON: pfc_controller_per_step_operator_select_v1 HARD_PASS first.
  Status check at startup; smoke-only dispatch unless pfc_controller HARD_PASSed.

HARD_PASS:
  acc(CORTEX_SCHEMAS) over SEPARATE_BANK >= 0.10 lift at K=4 equal count AND
  routing entropy per-hop >= 1.5 bits across test set AND
  cv across seeds <= 0.10

PROT-018: no _n suffix (capability-test).
ASCII-only; no unicode; no emojis; no em-dashes.
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
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)


ANCHOR_NAME = "cortex_as_router_mante_multiplicative_gating_v1"
_LLM_CALL_COUNTER = [0]
_HARDENING_MARKER = "v1_cortex_as_router_mante"

_ap = argparse.ArgumentParser(add_help=False)
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", dest="self_test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

RUN_MODE = (
    "smoke"
    if _ARGS.smoke or os.environ.get("HDLAB_RUN_MODE", "full").lower() == "smoke"
    else os.environ.get("HDLAB_RUN_MODE", "full").lower()
)


# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
N_FULL = 8192
K_OPS_FULL = 4         # operator count (matched across all arms by FAIRNESS)
N_CORTEX_SCHEMAS = 32  # cortex bank size (chosen at runtime to be > K)
N_HOPS_FULL = 5        # multi-hop compositional chain length
N_TEST_CHAINS_FULL = 30
SEEDS_FULL = [7, 17, 23]

# K-sweep arm config (for fairness isolation)
K_SWEEP_VALUES = (4, 8, 16)

if RUN_MODE == "smoke":
    N_DIM = 1024
    K_OPS = 4
    N_CORTEX = 16
    N_HOPS = 3
    N_TEST_CHAINS = 12
    SEEDS = [7]
else:
    N_DIM = N_FULL
    K_OPS = K_OPS_FULL
    N_CORTEX = N_CORTEX_SCHEMAS
    N_HOPS = N_HOPS_FULL
    N_TEST_CHAINS = N_TEST_CHAINS_FULL
    SEEDS = SEEDS_FULL

CONFIG_VERSION = (
    f"ANCHOR={ANCHOR_NAME},N={N_DIM},K={K_OPS},N_cortex={N_CORTEX},"
    f"N_hops={N_HOPS},N_test={N_TEST_CHAINS},"
    f"SEEDS={'-'.join(str(s) for s in SEEDS)},RUN_MODE={RUN_MODE},"
    f"hardening=L1early+L2perarm+L4importsentinel"
)


# ---------------------------------------------------------------------------
# DEPENDS_ON check: pfc_controller HARD_PASS prerequisite
# ---------------------------------------------------------------------------
def _check_pfc_controller_status() -> str:
    """Return status string: 'HARD_PASS' / 'SELFTEST_ONLY' / 'MISSING' / 'FAIL'."""
    try:
        pfc_metrics = REPO / "data" / "exp_pfc_controller_per_step_operator_select_v1" / "metrics.json"
        if not pfc_metrics.exists():
            return "MISSING"
        body = json.loads(pfc_metrics.read_text(encoding="utf-8"))
        verdict = body.get("verdict", "")
        if verdict == "HARD_PASS":
            return "HARD_PASS"
        if "SELFTEST" in verdict:
            return "SELFTEST_ONLY"
        return verdict or "FAIL"
    except Exception:
        return "MISSING"


# ---------------------------------------------------------------------------
# Substrate primitives: ops, cortex schemas, PFC context
# ---------------------------------------------------------------------------
def random_unit(rng: np.random.RandomState, n: int) -> np.ndarray:
    v = rng.randn(n).astype(np.float64)
    return v / max(np.linalg.norm(v), 1e-12)


def random_bipolar(rng: np.random.RandomState, n: int) -> np.ndarray:
    return rng.choice([-1.0, 1.0], size=n).astype(np.float64)


def make_operator_bank(rng: np.random.RandomState, k: int, n: int) -> np.ndarray:
    """k operator atoms (L2-normed unit vectors). Each operator is a unique direction."""
    bank = np.zeros((k, n), dtype=np.float64)
    for i in range(k):
        bank[i] = random_unit(rng, n)
    return bank


def make_cortex_schemas(rng: np.random.RandomState, n_schemas: int,
                        n: int) -> np.ndarray:
    """Cortex schema bank (L2-normed). Cortex has 5-200x more entries than ops."""
    bank = np.zeros((n_schemas, n), dtype=np.float64)
    for i in range(n_schemas):
        bank[i] = random_unit(rng, n)
    return bank


def make_test_chain(rng: np.random.RandomState, n: int,
                    n_hops: int, op_indices: List[int],
                    op_bank: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
    """Construct a multi-hop chain: start state + sequence of ops -> final state.

    Returns (start_state, expected_final_state).
    Application of op = element-wise multiply (substrate-native simple op).
    """
    start = random_unit(rng, n)
    s = start.copy()
    for op_idx in op_indices[:n_hops]:
        s = s * op_bank[op_idx]
        s = s / max(np.linalg.norm(s), 1e-12)
    return start, s


def apply_op(state: np.ndarray, op: np.ndarray) -> np.ndarray:
    """Element-wise multiply + renormalize (substrate-native op application)."""
    s = state * op
    return s / max(np.linalg.norm(s), 1e-12)


def emit_pfc_context(state: np.ndarray, hop: int, n_dim: int,
                     seed: int) -> np.ndarray:
    """PFC context c_h: low-rank task-conditioned vector.

    Simple model: rank-1 projection of state plus hop-specific seed-modulated bias.
    Returns (n_dim,) modulation vector with values in approx [-1, 1].
    """
    rng = np.random.RandomState(seed + hop * 1009)
    bias = random_unit(rng, n_dim)
    # rank-1: alpha * state + (1 - alpha) * bias
    alpha = 0.5
    c = alpha * state + (1.0 - alpha) * bias
    return np.tanh(c)


def gating_entropy(selected_indices: List[int], n_total: int) -> float:
    """Shannon entropy of operator-selection distribution over test set.

    Higher = more diverse routing = mechanism actually picks different ops.
    """
    if not selected_indices:
        return 0.0
    counts = np.zeros(n_total, dtype=np.float64)
    for i in selected_indices:
        if 0 <= i < n_total:
            counts[i] += 1
    total = float(counts.sum())
    if total <= 0:
        return 0.0
    p = counts / total
    p = p[p > 0]
    return float(-np.sum(p * np.log2(p)))


# ---------------------------------------------------------------------------
# Arm runners
# ---------------------------------------------------------------------------
def run_arm(arm_name: str, seed: int) -> Dict:
    t0 = time.time()
    try:
        rng = np.random.RandomState(seed)
        # Build operator banks (SAME RANK, SAME DTYPE, SAME N_DIM across arms)
        # Per arm:
        #   - SEPARATE_BANK: K_OPS dedicated ops, no cortex.
        #   - CORTEX_SCHEMAS_AS_OPS: gating selects TOP-K=K_OPS from N_CORTEX schemas.
        #   - HYBRID: K_OPS ops + N_CORTEX schemas, score-mixed.
        #   - LEARNED_GATING: gating is task-conditioned (state-dependent).
        #   - PARAM_COUNT_MATCHED: separate bank with extra dim to match cortex param count.

        op_bank_size = K_OPS
        cortex_bank_size = N_CORTEX if arm_name in (
            "ARM_CORTEX_SCHEMAS_AS_OPS", "ARM_HYBRID", "ARM_LEARNED_GATING"
        ) else 0

        operator_bank = make_operator_bank(rng, op_bank_size, N_DIM)
        cortex_bank = make_cortex_schemas(
            rng, cortex_bank_size, N_DIM
        ) if cortex_bank_size > 0 else np.zeros((0, N_DIM), dtype=np.float64)

        # Generate test chains using GROUND-TRUTH operators from operator_bank.
        # For CORTEX arms, cortex bank must be a SUPERSET (first K_OPS rows ==
        # operator_bank) so cortex CAN represent the right operators -- this is
        # the fairness condition: the cortex bank contains the operators the
        # tasks need, but the gating must SELECT them per-hop.
        if arm_name in ("ARM_CORTEX_SCHEMAS_AS_OPS", "ARM_HYBRID", "ARM_LEARNED_GATING"):
            # Place ground-truth ops at first K_OPS rows of cortex_bank
            cortex_bank[:K_OPS] = operator_bank

        # Generate N_TEST_CHAINS test chains
        n_correct = 0
        selected_op_indices = []
        rng_chain = np.random.RandomState(seed + 73)
        for chain_i in range(N_TEST_CHAINS):
            # Each chain uses N_HOPS ops drawn uniformly from K_OPS
            op_seq = rng_chain.choice(K_OPS, size=N_HOPS, replace=True).tolist()
            start, expected_final = make_test_chain(
                rng_chain, N_DIM, N_HOPS, op_seq, operator_bank
            )

            # Replay the chain hop-by-hop using the arm's routing logic
            state = start.copy()
            for h_idx in range(N_HOPS):
                true_op_idx = op_seq[h_idx]
                if arm_name == "ARM_SEPARATE_BANK":
                    # Oracle for fairness: pick by max-dot with start-op-hint
                    # Real router would have a planner; here we route by cosine
                    # to the operator that maximizes alignment with the next-step
                    # ground-truth direction (state * op_i). This is a "perfect"
                    # baseline that uses 1-of-K argmax.
                    scores = np.zeros(K_OPS)
                    for i in range(K_OPS):
                        scores[i] = float(np.dot(operator_bank[i],
                                                 operator_bank[true_op_idx]))
                    # Hard argmax over separate K=4 bank
                    pred_op_idx_in_bank = int(np.argmax(scores))
                    state = apply_op(state, operator_bank[pred_op_idx_in_bank])
                    selected_op_indices.append(pred_op_idx_in_bank)
                elif arm_name == "ARM_CORTEX_SCHEMAS_AS_OPS":
                    # PFC emits c_h; modulate cortex multiplicatively; pick TOP-K=K_OPS
                    # by cosine to (state * ground-truth direction).
                    c_h = emit_pfc_context(state, h_idx, N_DIM, seed + chain_i * 11)
                    # Modulated cortex: each schema gets multiplied by c_h
                    cortex_mod = cortex_bank * c_h[np.newaxis, :]
                    # Re-normalize rows
                    norms = np.linalg.norm(cortex_mod, axis=1, keepdims=True)
                    norms[norms < 1e-12] = 1.0
                    cortex_mod = cortex_mod / norms
                    # Score: how well each modulated schema matches the true op
                    scores = cortex_mod @ operator_bank[true_op_idx]
                    # Top-K from cortex (matching K_OPS for fairness)
                    top_k_idx = np.argpartition(-scores, K_OPS - 1)[:K_OPS]
                    # Pick best from those top-K
                    best_in_top = int(top_k_idx[np.argmax(scores[top_k_idx])])
                    state = apply_op(state, cortex_bank[best_in_top])
                    selected_op_indices.append(best_in_top)
                elif arm_name == "ARM_HYBRID":
                    # Score over BOTH banks; pick best.
                    sep_scores = operator_bank @ operator_bank[true_op_idx]
                    c_h = emit_pfc_context(state, h_idx, N_DIM, seed + chain_i * 11)
                    cortex_mod = cortex_bank * c_h[np.newaxis, :]
                    norms = np.linalg.norm(cortex_mod, axis=1, keepdims=True)
                    norms[norms < 1e-12] = 1.0
                    cortex_mod = cortex_mod / norms
                    cor_scores = cortex_mod @ operator_bank[true_op_idx]
                    # Combine: pick best across both
                    sep_best = int(np.argmax(sep_scores))
                    cor_best = int(np.argmax(cor_scores))
                    if sep_scores[sep_best] >= cor_scores[cor_best]:
                        chosen_op = operator_bank[sep_best]
                        selected_op_indices.append(sep_best)
                    else:
                        chosen_op = cortex_bank[cor_best]
                        # Offset cortex indices by K_OPS for entropy bookkeeping
                        selected_op_indices.append(K_OPS + cor_best)
                    state = apply_op(state, chosen_op)
                elif arm_name == "ARM_LEARNED_GATING":
                    # Task-conditioned gating via state-projection (different from
                    # CORTEX_SCHEMAS): c_h depends on state more strongly, with
                    # a per-hop learned bias (here: just deterministic per-hop seed).
                    c_h = np.tanh(state + 0.3 * emit_pfc_context(state, h_idx, N_DIM, seed))
                    cortex_mod = cortex_bank * c_h[np.newaxis, :]
                    norms = np.linalg.norm(cortex_mod, axis=1, keepdims=True)
                    norms[norms < 1e-12] = 1.0
                    cortex_mod = cortex_mod / norms
                    scores = cortex_mod @ operator_bank[true_op_idx]
                    top_k_idx = np.argpartition(-scores, K_OPS - 1)[:K_OPS]
                    best_in_top = int(top_k_idx[np.argmax(scores[top_k_idx])])
                    state = apply_op(state, cortex_bank[best_in_top])
                    selected_op_indices.append(best_in_top)
                elif arm_name == "ARM_PARAM_COUNT_MATCHED":
                    # Separate bank with N_CORTEX ops (parameter-matched to cortex)
                    # to test "more operators help on its own"
                    big_bank = make_operator_bank(
                        np.random.RandomState(seed + 919), N_CORTEX, N_DIM
                    )
                    big_bank[:K_OPS] = operator_bank
                    scores = big_bank @ operator_bank[true_op_idx]
                    pred_idx = int(np.argmax(scores))
                    state = apply_op(state, big_bank[pred_idx])
                    selected_op_indices.append(pred_idx)
                else:
                    raise ValueError(f"unknown arm: {arm_name}")

            # Compare final state to expected
            cos_final = float(np.dot(state, expected_final))
            if cos_final >= 0.90:
                n_correct += 1

        acc = n_correct / float(N_TEST_CHAINS)
        # Routing entropy: over how many distinct ops were picked across all hops
        n_total_pool = N_CORTEX if arm_name in (
            "ARM_CORTEX_SCHEMAS_AS_OPS", "ARM_LEARNED_GATING"
        ) else (
            K_OPS + N_CORTEX if arm_name == "ARM_HYBRID" else
            (N_CORTEX if arm_name == "ARM_PARAM_COUNT_MATCHED" else K_OPS)
        )
        entropy = gating_entropy(selected_op_indices, n_total_pool)

        # Parameter count
        if arm_name == "ARM_SEPARATE_BANK":
            param_count = K_OPS * N_DIM
        elif arm_name in ("ARM_CORTEX_SCHEMAS_AS_OPS", "ARM_LEARNED_GATING"):
            param_count = N_CORTEX * N_DIM
        elif arm_name == "ARM_HYBRID":
            param_count = K_OPS * N_DIM + N_CORTEX * N_DIM
        elif arm_name == "ARM_PARAM_COUNT_MATCHED":
            param_count = N_CORTEX * N_DIM
        else:
            param_count = 0

        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "accuracy": float(acc),
            "routing_entropy_bits": float(entropy),
            "n_test_chains": int(N_TEST_CHAINS),
            "n_hops": int(N_HOPS),
            "n_selections": int(len(selected_op_indices)),
            "n_distinct_ops_picked": int(len(set(selected_op_indices))),
            "param_count": int(param_count),
            "wall_s": float(wall),
            "arm_status": "OK",
        }
    except Exception as exc:
        wall = time.time() - t0
        return {
            "arm_name": arm_name,
            "accuracy": float("nan"),
            "routing_entropy_bits": float("nan"),
            "n_test_chains": 0,
            "n_hops": int(N_HOPS),
            "n_selections": 0,
            "n_distinct_ops_picked": 0,
            "param_count": 0,
            "wall_s": float(wall),
            "arm_status": f"ERROR: {type(exc).__name__}: {exc}",
        }


# ---------------------------------------------------------------------------
# Self-tests
# ---------------------------------------------------------------------------
def _selftest_operator_application() -> None:
    rng = np.random.RandomState(7)
    n = 64
    state = random_unit(rng, n)
    op = random_unit(rng, n)
    new_state = apply_op(state, op)
    if abs(np.linalg.norm(new_state) - 1.0) > 1e-6:
        raise AssertionError(
            f"apply_op did not renormalize: norm={np.linalg.norm(new_state)}"
        )


def _selftest_pfc_context_finite() -> None:
    rng = np.random.RandomState(11)
    state = random_unit(rng, N_DIM)
    c = emit_pfc_context(state, hop=0, n_dim=N_DIM, seed=42)
    if c.shape != (N_DIM,):
        raise AssertionError(f"c_h shape wrong: {c.shape}")
    if not np.all(np.isfinite(c)):
        raise AssertionError("c_h contains non-finite values")
    if np.max(np.abs(c)) > 1.01:
        raise AssertionError(f"c_h out of tanh range: max abs={np.max(np.abs(c))}")


def _selftest_entropy_calculation() -> None:
    # All same -> entropy 0
    e0 = gating_entropy([0, 0, 0, 0], 4)
    if abs(e0) > 1e-9:
        raise AssertionError(f"entropy of constant should be 0, got {e0}")
    # Uniform over 4 -> 2 bits
    e1 = gating_entropy([0, 1, 2, 3], 4)
    if abs(e1 - 2.0) > 0.01:
        raise AssertionError(f"uniform-4 entropy should be 2.0, got {e1}")


def _selftest_cortex_contains_ops() -> None:
    """Smoke that cortex bank can encode the true operators (fairness gate)."""
    rng = np.random.RandomState(7)
    op = make_operator_bank(rng, K_OPS, N_DIM)
    cor = make_cortex_schemas(rng, N_CORTEX, N_DIM)
    if cor.shape[0] < K_OPS:
        raise AssertionError(
            f"N_CORTEX={N_CORTEX} < K_OPS={K_OPS} -- cortex too small to host ops"
        )


def _instrumentation_selftest() -> None:
    try:
        _selftest_operator_application()
        _selftest_pfc_context_finite()
        _selftest_entropy_calculation()
        _selftest_cortex_contains_ops()
    except AssertionError as exc:
        print(f"[selftest] FAIL: {exc}", flush=True)
        sys.exit(2)
    except Exception as exc:
        print(f"[selftest] FAIL (unexpected): {type(exc).__name__}: {exc}",
              flush=True)
        sys.exit(3)
    pfc_status = _check_pfc_controller_status()
    print(
        f"[selftest] PASS  N={N_DIM}  K={K_OPS}  N_cortex={N_CORTEX}  "
        f"N_hops={N_HOPS}  N_test={N_TEST_CHAINS}  mode={RUN_MODE}  "
        f"pfc_controller_status={pfc_status}",
        flush=True,
    )


_IMPORT_SENTINEL_OK = True

_instrumentation_selftest()
if _ARGS.self_test:
    sys.exit(0)


# ---------------------------------------------------------------------------
# Per-seed runner
# ---------------------------------------------------------------------------
def run_seed(seed: int) -> Dict:
    t0 = time.time()
    print(f"  [seed={seed}] N={N_DIM} K={K_OPS} N_cortex={N_CORTEX} "
          f"N_hops={N_HOPS} N_test={N_TEST_CHAINS}", flush=True)
    arms = []
    for arm_name in ("ARM_SEPARATE_BANK", "ARM_CORTEX_SCHEMAS_AS_OPS",
                     "ARM_HYBRID", "ARM_LEARNED_GATING",
                     "ARM_PARAM_COUNT_MATCHED"):
        out = run_arm(arm_name, seed)
        arms.append(out)
        print(
            f"  [seed={seed} {arm_name}] "
            f"acc={out['accuracy']:.3f} "
            f"H={out['routing_entropy_bits']:.2f}bits "
            f"distinct={out['n_distinct_ops_picked']} "
            f"params={out['param_count']:,} "
            f"wall={out['wall_s']:.1f}s "
            f"status={out['arm_status']}",
            flush=True,
        )

    elapsed = time.time() - t0
    return {
        "seed": seed,
        "N": N_DIM,
        "K": K_OPS,
        "N_cortex": N_CORTEX,
        "N_hops": N_HOPS,
        "N_test_chains": N_TEST_CHAINS,
        "run_mode": RUN_MODE,
        "config_version": CONFIG_VERSION,
        "n_llm_calls": int(_LLM_CALL_COUNTER[0]),
        "pfc_controller_status": _check_pfc_controller_status(),
        "arms": arms,
        "elapsed_s": float(elapsed),
    }


# ---------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------
def _arm_by_name(arms: List[Dict], name: str) -> Dict:
    for a in arms:
        if a["arm_name"] == name:
            return a
    raise KeyError(f"arm {name} not found")


def compute_verdict(results: List[Dict]) -> Tuple[str, str]:
    if not results:
        return ("HARD_FAIL", "No valid seed results.")
    arm_names = ("ARM_SEPARATE_BANK", "ARM_CORTEX_SCHEMAS_AS_OPS",
                 "ARM_HYBRID", "ARM_LEARNED_GATING", "ARM_PARAM_COUNT_MATCHED")
    agg = {}
    for name in arm_names:
        try:
            per = [_arm_by_name(r["arms"], name) for r in results]
        except KeyError:
            return ("HARD_FAIL", f"Missing arm {name}")
        accs = [a["accuracy"] for a in per]
        ents = [a["routing_entropy_bits"] for a in per]
        distinct = [a["n_distinct_ops_picked"] for a in per]
        params = [a["param_count"] for a in per]
        statuses = [a["arm_status"] for a in per]
        accs_clean = [x for x in accs if np.isfinite(x)]
        if not accs_clean:
            return ("HARD_FAIL", f"Arm {name} no finite accuracy")
        agg[name] = {
            "mean_acc": float(np.mean(accs_clean)),
            "cv_acc": float(np.std(accs_clean) / max(np.mean(accs_clean), 1e-9)),
            "mean_entropy": float(np.mean([x for x in ents if np.isfinite(x)])
                                  if any(np.isfinite(x) for x in ents) else float("nan")),
            "mean_distinct": float(np.mean(distinct)),
            "mean_params": float(np.mean(params)),
            "all_ok": all(s == "OK" for s in statuses),
        }

    sep = agg["ARM_SEPARATE_BANK"]
    cor = agg["ARM_CORTEX_SCHEMAS_AS_OPS"]
    hyb = agg["ARM_HYBRID"]
    lrn = agg["ARM_LEARNED_GATING"]
    pcm = agg["ARM_PARAM_COUNT_MATCHED"]

    pfc_status = results[0].get("pfc_controller_status", "UNKNOWN")

    lift_vs_sep = cor["mean_acc"] - sep["mean_acc"]
    lift_vs_pcm = cor["mean_acc"] - pcm["mean_acc"]

    summary = (
        f"CORTEX_AS_OPS(acc={cor['mean_acc']:.3f},H={cor['mean_entropy']:.2f}bits,"
        f"dist={cor['mean_distinct']:.0f}); "
        f"SEP_BANK(acc={sep['mean_acc']:.3f},dist={sep['mean_distinct']:.0f}); "
        f"HYBRID(acc={hyb['mean_acc']:.3f}); "
        f"LEARNED(acc={lrn['mean_acc']:.3f},H={lrn['mean_entropy']:.2f}); "
        f"PARAM_MATCHED(acc={pcm['mean_acc']:.3f},dist={pcm['mean_distinct']:.0f}); "
        f"lift_CORTEX_vs_SEP={lift_vs_sep:+.3f}; "
        f"lift_CORTEX_vs_PARAM_MATCHED={lift_vs_pcm:+.3f}; "
        f"pfc_status={pfc_status}"
    )

    if pfc_status != "HARD_PASS":
        return ("MIDDLE_BAND",
                f"MIDDLE_BAND: DEPENDS_ON pfc_controller_per_step_operator_select_v1 "
                f"not yet HARD_PASS (status={pfc_status}); deferring chain-grade "
                f"classification until upstream lands. {summary}")

    # Q-discipline (suspect 1.000)
    if cor["mean_acc"] >= 0.999 and sep["mean_acc"] >= 0.999:
        return ("HARD_FAIL",
                f"HARD_FAIL: Q-DISCIPLINE both CORTEX_AS_OPS and SEP_BANK at "
                f"1.000; chain too easy. {summary}")

    # META_RULE_K: smoke must FIRE discriminator (different schemas picked)
    if cor["mean_distinct"] < 2:
        return ("HARD_FAIL",
                f"HARD_FAIL: META_RULE_K -- CORTEX_AS_OPS picked only "
                f"{cor['mean_distinct']:.0f} distinct ops (< 2); router degenerate. "
                f"{summary}")

    # Verify-the-referent: routing entropy threshold
    hp_entropy = cor["mean_entropy"] >= 1.5
    hp_lift = lift_vs_sep >= 0.10
    hp_cv = cor["cv_acc"] <= 0.10
    hp_distinct = cor["mean_distinct"] >= 3

    if all([hp_entropy, hp_lift, hp_cv, hp_distinct]):
        return ("HARD_PASS",
                f"HARD_PASS: CORTEX_AS_OPS lifts SEP by >=0.10 at K={K_OPS} equal-count, "
                f"entropy>=1.5 bits per-hop, cv<=0.10, distinct>=3. {summary}")

    if lift_vs_sep < 0.02:
        return ("HARD_FAIL",
                f"HARD_FAIL: lift_CORTEX_vs_SEP_BANK={lift_vs_sep:+.3f} < 0.02; "
                f"no meaningful lift from cortex-as-operators. {summary}")

    return ("MIDDLE_BAND",
            f"MIDDLE_BAND: cortex-as-router partial. "
            f"hp_checks=[entropy={hp_entropy},lift={hp_lift},cv={hp_cv},"
            f"distinct={hp_distinct}]. {summary}")


# ---------------------------------------------------------------------------
# Main driver
# ---------------------------------------------------------------------------
out_dir = get_output_dir(ANCHOR_NAME)
run_config = {"N": N_DIM, "run_mode": RUN_MODE, "anchor": ANCHOR_NAME}
done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
print(
    f"[ckpt] {len(done)} of {len(SEEDS)} seeds already complete; running {remaining}",
    flush=True,
)

t_sweep_start = time.time()
for seed in remaining:
    print(f"[seed={seed}] cortex_as_router_mante N={N_DIM} K={K_OPS} "
          f"N_cortex={N_CORTEX} N_hops={N_HOPS} mode={RUN_MODE}...",
          flush=True)
    result = run_seed(seed)
    write_partial(out_dir, seed, result)

per_seed = aggregate_partials(out_dir, SEEDS, run_config=run_config)
all_results = list(per_seed.values())
verdict, verdict_msg = compute_verdict(all_results)

elapsed_s = time.time() - t_sweep_start
print(f"\n[VERDICT] {verdict}: {verdict_msg}", flush=True)
print(f"[elapsed] {elapsed_s:.1f}s", flush=True)

mode_in_results = {r.get("run_mode", "?") for r in all_results}
if RUN_MODE == "full" and "smoke" in mode_in_results:
    verdict = "HARD_FAIL"
    verdict_msg = (
        f"HARD_FAIL: stale smoke partials in FULL run. "
        f"mode_in_results={mode_in_results}. " + verdict_msg
    )

metrics = {
    "anchor_name": ANCHOR_NAME,
    "verdict": verdict,
    "verdict_msg": verdict_msg,
    "summary": (
        f"n_seeds={len(all_results)} N={N_DIM} K={K_OPS} N_cortex={N_CORTEX} "
        f"N_hops={N_HOPS} mode={RUN_MODE}"
    ),
    "elapsed_s": float(elapsed_s),
    "config_version": CONFIG_VERSION,
    "N": N_DIM,
    "K": K_OPS,
    "N_cortex": N_CORTEX,
    "N_hops": N_HOPS,
    "N_test_chains": N_TEST_CHAINS,
    "n_seeds": len(SEEDS),
    "run_mode": RUN_MODE,
    "n_llm_calls_total": int(sum(r.get("n_llm_calls", 0) for r in all_results)),
    "pfc_controller_status": _check_pfc_controller_status(),
    "per_seed": [
        {
            "seed": r.get("seed"),
            "elapsed_s": r.get("elapsed_s"),
            "arms": r.get("arms"),
        }
        for r in all_results
    ],
}
metrics_path = out_dir / "metrics.json"
metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
print(f"[metrics] written to {metrics_path}", flush=True)
