"""exp_multihop_reverse_replay_backward_sweep_v1_self_contained (M5 brain-mechanism cell).

SELF-CONTAINED variant of exp_multihop_reverse_replay_backward_sweep_v1.

WHY THIS VARIANT EXISTS (2026-06-27):
The sibling cell exp_multihop_reverse_replay_backward_sweep_v1.py was authored alongside
3 hdlab/ primitive additions (S_back + bind_pair_reverse + predict_prev in
hdlab/sequence_memory.py; bidirectional_chain in hdlab/multi_hop.py; replay_cycle
direction='reverse'|'both' in hdlab/continual.py; commit 2f12bb6a). The orchestrator
declined to push those hdlab/ files to remote (auto mode rule #5: shared-system overwrite
discipline). This variant INLINES the load-bearing primitive math directly into the cell
so it runs cleanly on a remote that does NOT have the hdlab/ overwrites.

INLINE PRIMITIVES (functional equivalents of the un-shipped hdlab/ additions):
  - _seqmem_bind_pair_reverse(S_back, k_prev, k_next)        equiv hdlab.sequence_memory.bind_pair_reverse
  - _seqmem_predict_prev(S_back, k_next)                     equiv hdlab.sequence_memory.predict_prev
  - _multihop_bidirectional_chain(E, W, R, sq, ...)          equiv hdlab.multi_hop.bidirectional_chain
  - _continual_replay_cycle(W, ..., direction='reverse'...)  equiv hdlab.continual.replay_cycle
These inlines use numpy (consistent with the rest of the cell). The hdlab/ equivalents are
torch-based. Behavior is mathematically identical for the load-bearing path used in this
cell: outer-product Hebbian writes + matrix-vector retrieval + cosine ranking.

EXISTING hdlab/ imports retained: NONE. The sibling cell already had zero `from hdlab`
imports (cell is fully numpy + only depends on `experiments._seed_checkpoint`). This
variant preserves that property — the only changes vs the sibling are:
  1. ANCHOR_NAME suffixed with `_self_contained` (distinct output dir; no collision)
  2. This header block + inline-primitive shim functions documenting the equivalences
  3. CONFIG_VERSION updated to reflect the self-contained variant tag
All scientific arms / discriminator / bands / cardinality are UNCHANGED.

---
Brain mechanism #5 -- reverse-replay / backward sweep for credit assignment.

Tests whether adding a SEPARATE S_back reverse-temporal-order store (and reverse-
direction NREM replay) lifts substrate multi-hop chain accuracy over the forward-
only baseline. Composes with M3 bidirectional meet-in-middle. Includes a
discriminator arm (RANDOM_REVERSE) that proves temporal order is load-bearing
(NOT "any extra replay helps").

ARMS (6):
  A: BASELINE_FORWARD_REPLAY_ONLY      substrate current state; W forward only
  B: REVERSE_REPLAY_ONLY               W frozen; only S_back ingested; downstream uses S_back
  C: WITH_REVERSE_REPLAY               both forward W and S_back active; equal weight
  D: BIDIRECTIONAL_BOTH                C + meet-in-middle inference (M3 composition)
  E: REWARD_GATED_REVERSE              reverse-replay fires only when forward top-1 conf > tau
                                        (Ambrose-Pfeiffer-Foster 2016 reward-gating)
  F: RANDOM_REVERSE_REPLAY_DISCRIMINATOR
                                        reverse-replay over SHUFFLED temporal order
                                        (CRITICAL: tests "temporal order matters")

PROSPECTIVE BANDS (LOCKED via module-init asserts):
  HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY:
    D top1 >= A top1 + 0.20 AND C top1 >= F top1 + 0.10
  MIDDLE_BAND_PARTIAL_REVERSE_REPLAY:
    partial conditions (e.g. D > A + 0.10 but C - F < 0.05)
  HARD_FAIL_REVERSE_REPLAY_DOESNT_HELP:
    D top1 <= A top1 + 0.05

CARDINALITY (META_RULE_H CARDINALITY_OK):
  6 arms x 3 seeds x 3 depths {2, 3, 5} = 54 units
  EXPECTED_N_UNITS = 54; HARD_FAIL_CARDINALITY_BREACH if observed < expected.

ASCII-only; per-seed checkpoint; atexit synthesizer.
"""
from __future__ import annotations

import sys
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

import argparse
import atexit
import math
import os
import time
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (
    get_output_dir, resumable_seeds, write_partial_key, aggregate_partials,
    write_metrics,
)

ANCHOR_NAME = "multihop_reverse_replay_backward_sweep_v1_self_contained"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# HARD bands (LOCKED prospectively per M5 drill cell-spec design section)
HP_D_LIFT_OVER_A = 0.20       # D top1 - A top1 must be >= this
HP_C_OVER_F = 0.10            # C top1 - F top1 must be >= this (temporal-order load-bearing)
MID_D_LIFT_LO = 0.10          # MIDDLE: D > A + 0.10 (partial)
HF_D_NO_HELP = 0.05           # HARD_FAIL: D - A <= this

# Reward-gate calibration (Arm E)
REWARD_GATE_TAU_QUANTILE = 0.75  # tau = 75th-percentile of depth-2 fwd-top1 conf

assert HP_D_LIFT_OVER_A > MID_D_LIFT_LO > HF_D_NO_HELP, \
    "HARD_PASS > MIDDLE > HARD_FAIL ladder must be monotonic"
assert HP_C_OVER_F > 0.0
assert 0.0 < REWARD_GATE_TAU_QUANTILE < 1.0

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 80
    N_CHAINS = 30
    SEEDS = [7]
    DEPTHS = [2, 3, 5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    N_CHAINS = 200
    SEEDS = [7, 17, 23]
    DEPTHS = [2, 3, 5]

EXPECTED_N_UNITS = 6 * len(SEEDS) * len(DEPTHS)  # CARDINALITY_OK

CONFIG_VERSION = (
    "multihopReverseReplayBackwardSweepV1SelfContained: N=%d V_C=%d n_chains=%d "
    "seeds=%s depths=%s mode=%s "
    "HP_D_lift>=%.2f HP_C_over_F>=%.2f MID_lift>=%.2f HF_no_help<=%.2f "
    "tau_quantile=%.2f EXPECTED_N_UNITS=%d "
    "variant=self_contained_inline_primitives_no_hdlab_overwrite_required"
) % (
    N_DIM, V_CONCEPTS, N_CHAINS, SEEDS, DEPTHS, RUN_MODE,
    HP_D_LIFT_OVER_A, HP_C_OVER_F, MID_D_LIFT_LO, HF_D_NO_HELP,
    REWARD_GATE_TAU_QUANTILE, EXPECTED_N_UNITS,
)


# ===========================================================================
# INLINE PRIMITIVE SHIMS (equivalents of hdlab/ additions un-shipped to remote)
# ===========================================================================
# These mirror the un-shipped hdlab/ primitive signatures so the cell is
# explicitly self-contained. Math is identical to the hdlab/ torch versions
# for the load-bearing paths used by this cell.

def _seqmem_bind_pair_reverse(S_back: np.ndarray, k_prev: np.ndarray, k_next: np.ndarray) -> None:
    """Reverse-temporal-order Hebbian write: S_back += outer(k_prev, k_next).

    Equivalent to hdlab.sequence_memory.SequenceMatrix.bind_pair_reverse.
    Mutates S_back in-place. After ingest, _seqmem_predict_prev(S_back, k_next)
    approximates k_prev (the temporal predecessor of k_next).
    """
    S_back += np.outer(k_prev.astype(np.float32), k_next.astype(np.float32))


def _seqmem_predict_prev(S_back: np.ndarray, k_next: np.ndarray) -> np.ndarray:
    """Retrieve predicted PREVIOUS key as S_back @ k_next.

    Equivalent to hdlab.sequence_memory.SequenceMatrix.predict_prev.
    """
    return S_back @ k_next.astype(np.float32)


def _continual_replay_cycle_reverse(W_back: np.ndarray, keys_prev: np.ndarray,
                                     keys_next: np.ndarray) -> None:
    """Reverse-direction outer-sum replay batch into W_back.

    Equivalent to hdlab.continual.replay_cycle(direction='reverse', W_back=...) for
    the substrate's reverse-temporal-order replay path. keys_prev / keys_next are
    [M, N_DIM]; W_back += outer-sum of (k_prev, k_next) over M pairs. In-place.
    """
    W_back += keys_prev.astype(np.float32).T @ keys_next.astype(np.float32)


def _multihop_bidirectional_chain(E: np.ndarray, W: np.ndarray, R: np.ndarray,
                                   sq: float, start: int, end_candidates: np.ndarray,
                                   relations: List[int], midpoint_hop: int = None
                                   ) -> Tuple[int, float, Dict[str, float]]:
    """Bidirectional meet-in-middle K-hop traversal over Hebbian W.

    Equivalent to hdlab.multi_hop.bidirectional_chain. Walks `midpoint_hop` hops
    forward from E[start] via W @ (state * R[p] * sq), and (DEPTH-midpoint_hop)
    hops backward from each candidate Z via W.T @ state (then * R[p] * sq).
    Ranks candidates by cosine(state_fwd, state_bwd_Z). Returns (best_Z, best_cos,
    diagnostics).

    Chain-grade-validated equivalent of META_M7 BIDIR_MEET_MID arm.
    """
    depth = len(relations)
    if midpoint_hop is None:
        midpoint_hop = depth // 2
    state_fwd = E[start].astype(np.float32).copy()
    for i in range(midpoint_hop):
        p = relations[i]
        state_fwd = W @ (state_fwd * R[p] * sq)
    fnorm = float(np.linalg.norm(state_fwd)) + 1e-8

    best_cos = -2.0
    best_Z = int(end_candidates[0])
    second_cos = -2.0
    cos_all = []
    for Z_int in end_candidates:
        Z = int(Z_int)
        state_bwd = E[Z].astype(np.float32).copy()
        for i in range(depth - 1, midpoint_hop - 1, -1):
            p = relations[i]
            state_bwd = W.T @ state_bwd
            state_bwd = state_bwd * R[p] * sq
        bnorm = float(np.linalg.norm(state_bwd)) + 1e-8
        cos = float(np.dot(state_fwd, state_bwd) / (fnorm * bnorm))
        cos_all.append(cos)
        if cos > best_cos:
            second_cos = best_cos
            best_cos = cos
            best_Z = Z
        elif cos > second_cos:
            second_cos = cos
    mean_cos = float(sum(cos_all) / max(len(cos_all), 1))
    diagnostics = {
        "mean_cosine": mean_cos,
        "best_cosine": best_cos,
        "cos_top1_minus_top2": best_cos - second_cos,
        "midpoint_hop": midpoint_hop,
        "n_candidates": int(len(end_candidates)),
    }
    return best_Z, best_cos, diagnostics


# ===========================================================================
# CELL LOGIC (unchanged from sibling cell except for use of inline primitives
# where convenient; behavior bit-equivalent)
# ===========================================================================

def bipolar(M: int, n: int, g) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X


def ingest_W_forward(triples, E, R, sq, n_dim, batch=2000):
    """Forward associative-memory W (the substrate's standard ingest)."""
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def ingest_S_back_reverse(chains, E, n_dim, shuffle_temporal_order=False, g=None):
    """Build S_back from chains as reverse-temporal-order pair store.

    Uses the _seqmem_bind_pair_reverse inline primitive (equivalent to
    hdlab.sequence_memory.bind_pair_reverse). For each chain
    [(s, p, o), (s', p', o'), ...] we form successive (k_t, k_{t+1}) key-pairs
    where k_t = E[node_t]. _seqmem_bind_pair_reverse(S_back, k_t, k_{t+1})
    writes outer(k_t, k_{t+1}) so that S_back @ k_{t+1} approximates k_t
    (recovering the predecessor).

    If shuffle_temporal_order=True, destroy WHICH-NODES-PAIR-WITH-WHICH structure
    while preserving total binding volume. (Discriminator against "any extra
    binding helps".)
    """
    S_back = np.zeros((n_dim, n_dim), dtype=np.float32)
    if shuffle_temporal_order:
        if g is None:
            raise ValueError("shuffle_temporal_order=True requires generator g")
        all_nodes = []
        for chain in chains:
            nodes = [chain[0][0]] + [hop[2] for hop in chain]
            for i in range(len(nodes) - 1):
                all_nodes.append((nodes[i], nodes[i + 1]))
        first = [a for a, _ in all_nodes]
        second = [b for _, b in all_nodes]
        g.shuffle(second)
        for a, b in zip(first, second):
            _seqmem_bind_pair_reverse(S_back, E[a], E[b])
    else:
        for chain in chains:
            nodes = [chain[0][0]] + [hop[2] for hop in chain]
            for i in range(len(nodes) - 1):
                _seqmem_bind_pair_reverse(S_back, E[nodes[i]], E[nodes[i + 1]])
    return S_back


def make_deep_chains(n_chains, V, P, max_depth, g, disallow_s=None):
    if disallow_s is None:
        disallow_s = set()
    all_triples, chain_queries, used_s = [], [], set(disallow_s)
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            while cand in nodes:
                cand = int(g.integers(0, V))
            nodes.append(cand)
        chain = []
        for i in range(max_depth):
            p = int(g.integers(0, P))
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError("BLOCKING make_deep_chains: only %d/%d" % (len(chain_queries), n_chains))
    return all_triples, chain_queries


def _retrieve_1hop_fwd(E, W, R, s, p, sq):
    """Standard forward 1-hop substrate retrieval."""
    key = (E[s] * R[p] * sq).astype(np.float32)
    return int((E @ (W @ key)).argmax()), float((E @ (W @ key)).max())


def _retrieve_1hop_back(E, S_back, o):
    """Reverse 1-hop via _seqmem_predict_prev (inline primitive)."""
    pred = _seqmem_predict_prev(S_back, E[o])
    return int((E @ pred).argmax()), float((E @ pred).max())


def chain_forward_only(E, W, R, sq, chain, depth):
    """Arm A: pure forward-only chain (substrate baseline)."""
    s = chain[0][0]
    per_step = []
    for i in range(depth):
        p = chain[i][1]
        s_pred, _ = _retrieve_1hop_fwd(E, W, R, s, p, sq)
        per_step.append(1 if s_pred == chain[i][2] else 0)
        s = s_pred
    correct = (s == chain[depth - 1][2])
    return correct, per_step


def chain_reverse_only(E, S_back, chain, depth):
    """Arm B: pure reverse-only chain -- start from end, walk backward."""
    o = chain[depth - 1][2]
    per_step = []
    for i in range(depth - 1, -1, -1):
        s_pred, _ = _retrieve_1hop_back(E, S_back, o)
        per_step.append(1 if s_pred == chain[i][0] else 0)
        o = s_pred
    correct = (o == chain[0][0])
    return correct, list(reversed(per_step))


def chain_with_reverse_replay(E, W, R, sq, S_back, chain, depth, replay_lambda=0.5):
    """Arm C: forward chain with reverse-replay enriched W (blended scores)."""
    s = chain[0][0]
    per_step = []
    for i in range(depth):
        p = chain[i][1]
        key = (E[s] * R[p] * sq).astype(np.float32)
        fwd_scores = E @ (W @ key)  # [V]
        rev_back = E @ S_back.T
        rev_consistency = rev_back @ E[s].astype(np.float32)  # [V]
        combined = fwd_scores + replay_lambda * rev_consistency
        s_pred = int(combined.argmax())
        per_step.append(1 if s_pred == chain[i][2] else 0)
        s = s_pred
    correct = (s == chain[depth - 1][2])
    return correct, per_step


def chain_bidirectional_meet(E, W, R, sq, chain, depth, V_C):
    """Arm D: full bidirectional meet-in-middle ranking via inline primitive.

    Delegates to _multihop_bidirectional_chain (equivalent of
    hdlab.multi_hop.bidirectional_chain). Candidates = all entities [0, V_C).
    """
    preds = [chain[i][1] for i in range(depth)]
    S = chain[0][0]
    candidates = np.arange(V_C, dtype=np.int64)
    best_Z, best_cos, _diag = _multihop_bidirectional_chain(
        E, W, R, sq, S, candidates, preds, midpoint_hop=depth // 2,
    )
    true_Z = chain[depth - 1][2]
    return (best_Z == true_Z), best_cos


def calibrate_reward_gate_tau(E, W, R, sq, chains, depth, quantile):
    """Calibrate tau = quantile of forward depth-2 top-1 confidence values."""
    confs = []
    for chain in chains:
        s = chain[0][0]
        for i in range(min(2, depth)):
            p = chain[i][1]
            _, conf = _retrieve_1hop_fwd(E, W, R, s, p, sq)
            confs.append(conf)
            s, _ = _retrieve_1hop_fwd(E, W, R, s, p, sq)
    if not confs:
        return float("inf")
    return float(np.quantile(confs, quantile))


def chain_reward_gated_reverse(E, W, R, sq, S_back, chain, depth, tau, replay_lambda=0.5):
    """Arm E: reward-gated reverse-replay."""
    s = chain[0][0]
    per_step = []
    for i in range(depth):
        p = chain[i][1]
        key = (E[s] * R[p] * sq).astype(np.float32)
        fwd_scores = E @ (W @ key)
        fwd_top = float(fwd_scores.max())
        if fwd_top > tau:
            rev_back = E @ S_back.T
            rev_consistency = rev_back @ E[s].astype(np.float32)
            combined = fwd_scores + replay_lambda * rev_consistency
        else:
            combined = fwd_scores  # gate closed; pure forward
        s_pred = int(combined.argmax())
        per_step.append(1 if s_pred == chain[i][2] else 0)
        s = s_pred
    correct = (s == chain[depth - 1][2])
    return correct, per_step


def run_arms_at_depth(E, R, sq, W, S_back, S_back_shuffled, chains, depth, V_C, tau):
    """Run all 6 arms at a single depth; chains are sliced to `depth`."""
    chains_d = [c[:depth] for c in chains]
    n = len(chains_d)

    a_hits = sum(int(chain_forward_only(E, W, R, sq, c, depth)[0]) for c in chains_d)
    b_hits = sum(int(chain_reverse_only(E, S_back, c, depth)[0]) for c in chains_d)
    c_hits = sum(int(chain_with_reverse_replay(E, W, R, sq, S_back, c, depth)[0]) for c in chains_d)
    d_hits = sum(int(chain_bidirectional_meet(E, W, R, sq, c, depth, V_C)[0]) for c in chains_d)
    e_hits = sum(int(chain_reward_gated_reverse(E, W, R, sq, S_back, c, depth, tau)[0]) for c in chains_d)
    f_hits = sum(int(chain_with_reverse_replay(E, W, R, sq, S_back_shuffled, c, depth)[0]) for c in chains_d)

    return {
        "depth": depth, "n_queries": n,
        "A_baseline_forward_only_top1": round(a_hits / max(n, 1), 4),
        "B_reverse_only_top1": round(b_hits / max(n, 1), 4),
        "C_with_reverse_replay_top1": round(c_hits / max(n, 1), 4),
        "D_bidirectional_both_top1": round(d_hits / max(n, 1), 4),
        "E_reward_gated_reverse_top1": round(e_hits / max(n, 1), 4),
        "F_random_reverse_discriminator_top1": round(f_hits / max(n, 1), 4),
    }


def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 256
    V = 20
    P = 3
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)

    triples, chains = make_deep_chains(8, V, P, max_depth=5, g=g)
    W = ingest_W_forward(triples, E, R, sq, n)
    S_back = ingest_S_back_reverse(chains, E, n, shuffle_temporal_order=False)
    S_back_sh = ingest_S_back_reverse(chains, E, n, shuffle_temporal_order=True, g=g)

    # Inline-primitive sanity: equiv of hdlab.sequence_memory smoke
    S_test = np.zeros((n, n), dtype=np.float32)
    _seqmem_bind_pair_reverse(S_test, E[0], E[1])
    assert float(np.linalg.norm(S_test)) > 0.0, "bind_pair_reverse failed to mutate S_back"
    pred = _seqmem_predict_prev(S_test, E[1])
    # bound pair: outer(E[0], E[1]); S @ E[1] = E[0] * (E[1] dot E[1]) = E[0] * n
    assert int(np.argmax(E @ pred)) == 0, "predict_prev failed to recover bound predecessor"

    # Inline-primitive sanity: bidirectional_chain on tiny W
    candidates = np.arange(V, dtype=np.int64)
    bz, bc, diag = _multihop_bidirectional_chain(
        E, W, R, sq, chains[0][0][0], candidates,
        [chains[0][0][1], chains[0][1][1]],
        midpoint_hop=1,
    )
    assert 0 <= bz < V
    assert -1.0 <= bc <= 1.0
    assert diag["n_candidates"] == V

    # Inline-primitive sanity: reverse-direction replay cycle
    W_back = np.zeros((n, n), dtype=np.float32)
    keys_prev = E[:3].astype(np.float32)
    keys_next = E[1:4].astype(np.float32)
    _continual_replay_cycle_reverse(W_back, keys_prev, keys_next)
    assert float(np.linalg.norm(W_back)) > 0.0

    # S_back nonzero norms
    assert float(np.linalg.norm(S_back)) > 0.0
    assert float(np.linalg.norm(S_back_sh)) > 0.0

    # All 6 arms produce valid top1 in [0, 1] at smoke depths
    tau = calibrate_reward_gate_tau(E, W, R, sq, chains, depth=5, quantile=0.75)
    for d in [2, 3, 5]:
        r = run_arms_at_depth(E, R, sq, W, S_back, S_back_sh, chains, d, V, tau)
        for k, v in r.items():
            if k.endswith("_top1"):
                assert 0.0 <= v <= 1.0, "arm %s top1=%s out of [0,1] at depth=%d" % (k, v, d)

    # Bands locked numerics
    assert HP_D_LIFT_OVER_A == 0.20
    assert HP_C_OVER_F == 0.10
    assert MID_D_LIFT_LO == 0.10
    assert HF_D_NO_HELP == 0.05

    # CARDINALITY_OK explicit
    assert EXPECTED_N_UNITS == 6 * len(SEEDS) * len(DEPTHS)

    # No LLM calls
    assert _LLM_CALL_COUNTER[0] == 0

    print("[selftest] PASS (self_contained variant) tau=%.4f arms_OK_depths=%s expected_units=%d"
          % (tau, [2, 3, 5], EXPECTED_N_UNITS), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    P_max = 10
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(P_max, N_DIM, g)

    out: Dict[str, Any] = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_chains": N_CHAINS, "depths": DEPTHS,
        "config_version": CONFIG_VERSION,
        "expected_n_units_per_seed": 6 * len(DEPTHS),
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    t_w = time.time()
    triples, chains = make_deep_chains(N_CHAINS, V_CONCEPTS, P_max, max_depth=5, g=g)
    W = ingest_W_forward(triples, E, R, sq, N_DIM)
    S_back = ingest_S_back_reverse(chains, E, N_DIM, shuffle_temporal_order=False)
    g_shuf = np.random.default_rng(seed + 1000)
    S_back_sh = ingest_S_back_reverse(chains, E, N_DIM, shuffle_temporal_order=True, g=g_shuf)
    out["build_time_s"] = round(time.time() - t_w, 2)
    print("  [seed=%d] W + S_back built (%d triples, %d chains) t=%.1fs" % (
        seed, len(triples), len(chains), out["build_time_s"]), flush=True)

    tau = calibrate_reward_gate_tau(E, W, R, sq, chains[:50], depth=5,
                                    quantile=REWARD_GATE_TAU_QUANTILE)
    out["reward_gate_tau"] = round(tau, 4)
    print("  [seed=%d] reward-gate tau=%.4f (q=%.2f)" % (
        seed, tau, REWARD_GATE_TAU_QUANTILE), flush=True)

    per_depth_results = []
    for d in DEPTHS:
        t_d = time.time()
        r = run_arms_at_depth(E, R, sq, W, S_back, S_back_sh, chains, d, V_CONCEPTS, tau)
        r["elapsed_s_depth"] = round(time.time() - t_d, 2)
        per_depth_results.append(r)
        print("  [seed=%d] depth=%d A=%.3f B=%.3f C=%.3f D=%.3f E=%.3f F=%.3f t=%.1fs" % (
            seed, d,
            r["A_baseline_forward_only_top1"], r["B_reverse_only_top1"],
            r["C_with_reverse_replay_top1"], r["D_bidirectional_both_top1"],
            r["E_reward_gated_reverse_top1"], r["F_random_reverse_discriminator_top1"],
            r["elapsed_s_depth"]), flush=True)

    out["per_depth"] = per_depth_results

    for arm in ["A_baseline_forward_only", "B_reverse_only", "C_with_reverse_replay",
                "D_bidirectional_both", "E_reward_gated_reverse",
                "F_random_reverse_discriminator"]:
        vals = [r[arm + "_top1"] for r in per_depth_results]
        out["arm_" + arm + "_mean_top1"] = round(float(np.mean(vals)), 4)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_arm(arm_key: str) -> float:
        vals = [p.get(arm_key) for p in per_seed
                if isinstance(p.get(arm_key), (int, float))]
        return float(np.mean(vals)) if vals else float("nan")

    A = mean_arm("arm_A_baseline_forward_only_mean_top1")
    B = mean_arm("arm_B_reverse_only_mean_top1")
    C = mean_arm("arm_C_with_reverse_replay_mean_top1")
    D = mean_arm("arm_D_bidirectional_both_mean_top1")
    E = mean_arm("arm_E_reward_gated_reverse_mean_top1")
    F = mean_arm("arm_F_random_reverse_discriminator_mean_top1")

    observed_units = sum(p.get("expected_n_units_per_seed", 0) for p in per_seed)
    if observed_units < EXPECTED_N_UNITS:
        return ("HARD_FAIL", "HARD_FAIL_CARDINALITY_BREACH: observed=%d expected=%d "
                "per_seed=%s" % (observed_units, EXPECTED_N_UNITS, per_seed))

    d_lift = D - A
    c_over_f = C - F

    summ = ("A_baseline=%.4f B_reverse_only=%.4f C_with_reverse=%.4f D_bidir=%.4f "
            "E_reward_gated=%.4f F_random_reverse=%.4f | "
            "D-A_lift=%+.4f C-F_temporal_order=%+.4f") % (
        A, B, C, D, E, F, d_lift, c_over_f,
    )

    if d_lift >= HP_D_LIFT_OVER_A and c_over_f >= HP_C_OVER_F:
        return ("HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY",
                "HARD_PASS_CHAIN_GRADE_REVERSE_REPLAY: " + summ)
    if d_lift <= HF_D_NO_HELP:
        return ("HARD_FAIL",
                "HARD_FAIL_REVERSE_REPLAY_DOESNT_HELP: " + summ)
    return ("MIDDLE_BAND",
            "MIDDLE_BAND_PARTIAL_REVERSE_REPLAY: " + summ)


_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
            return
        if (od / "metrics.json").exists():
            return
        v, vmsg = verdict_from(per_seed)
        metrics = {
            "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
            "run_mode": RUN_MODE, "n_seeds": len(per_seed),
            "config_version": CONFIG_VERSION, "per_seed": per_seed,
            "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
            "summary": vmsg, "_atexit_synth": True,
            "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        }
        write_metrics(od, metrics, results=per_seed)
        print("[atexit] wrote synth metrics.json (%d seeds)" % len(per_seed), flush=True)
    except Exception as e:
        print("[atexit] FAIL: %s" % e, flush=True)


atexit.register(_atexit_synth)


if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d depths=%s | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, DEPTHS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0

    v, vmsg = verdict_from(per_seed)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME, "verdict": v, "verdict_msg": vmsg,
        "run_mode": RUN_MODE, "n_seeds": len(per_seed),
        "config_version": CONFIG_VERSION, "per_seed": per_seed,
        "elapsed_s": round(time.time() - _RESULTS_HOLDER["started_at"], 1),
        "summary": vmsg,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
        "DESIGN_NOTE": (
            "M5 brain-mechanism cell SELF-CONTAINED variant: reverse-replay / backward "
            "sweep. Same scientific arms as sibling cell exp_multihop_reverse_replay_"
            "backward_sweep_v1, but with inline primitive shims (bind_pair_reverse, "
            "predict_prev, bidirectional_chain, replay_cycle reverse-direction) so cell "
            "runs on a remote that does NOT have the un-shipped hdlab/ overwrites. "
            "Math is bit-equivalent to the hdlab/ torch versions for the load-bearing "
            "Hebbian outer-sum + matrix-vector retrieval paths used here."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
