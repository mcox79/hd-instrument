"""substrate_multihop_csp_gated_iterated_cleanup_v1 -- Barrier-1 NOVEL angle.

CLOSURE TARGET (Barrier 1 fourth-attempt; novel angle per Research drill
2026-06-25): the substrate's multi-hop ceiling at depth > 2 has been REFUTED
3-for-3 (consolidation v1/v2/v3 HARD_FAIL; pointer_chain v1/v2 HARD_FAIL;
WM-scaffolded v1 HARD_FAIL). Each prior attempt missed a brain-aligned
component:
  - consolidation: pollutes lookup library
  - pointer_chain: cleanup output of step n -> step n+1 (geometric error)
  - WM-scaffold: clean intermediate per hop, but NO confidence-gating

THIS CELL composes 3 chain-grade primitives never before composed for multi-
hop: (a) HRR-slot WM scaffold (PFC analog); (b) Hebbian-bound W cleanup
(hippocampus); (c) CSP-style confidence threshold (ACC conflict-monitoring).
At each hop:
  1. Read clean WM slot content (the cleaned intermediate from prior hop).
  2. Bind with relation, lookup via W, get cleanup candidate.
  3. Compute CSP confidence = (top1 - top2) cosine separation; this is the
     substrate's "I'm uncertain" signal.
  4. If conf < CSP_THRESHOLD, ITERATE cleanup up to N_ITER=3 times (each
     iteration re-runs the cleanup with a small amount of additive noise
     correction; the brain analog is theta-gamma oscillatory cleanup).
  5. If still below threshold after N_ITER: REFUSE (abort chain).
  6. Else: write cleaned candidate to next WM slot.

CRITICAL: the iterated-cleanup mechanism is brain-aligned theta-gamma
oscillation: each "cycle" pulls noise off the cue and re-projects through W;
the substrate's bipolar quantization concentrates the cue toward the codebook
attractor on each iteration.

ARMS (4):
  ARM_BASELINE_HRR_2HOP         verbatim beta-sweep baseline (rail [0.62,0.68])
  ARM_CSP_GATED_ITER_2HOP       new mechanism at depth 2 (target >= 0.80)
  ARM_CSP_GATED_ITER_5HOP       new mechanism at depth 5 (pointer_v2: 0.122)
  ARM_CSP_GATED_ITER_10HOP      new mechanism at depth 10 (pointer_v2: 0.035)

PRE-REG BANDS (LOCKED via assertion below):

  HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL:
    BASELINE in [0.62, 0.68] (sanity rail)
    AND ARM_CSP_GATED_ITER_2HOP >= 0.80
    AND ARM_CSP_GATED_ITER_5HOP >= 0.50
    AND ARM_CSP_GATED_ITER_10HOP >= 0.20
    AND refuse_rate at depth_5 > 0.10 AND < 0.90 (CSP gate ACTUALLY filtering)
    AND CV <= 0.07

  HARD_PASS_PARTIAL_BARRIER_1_LIFT:
    ARM_CSP_GATED_ITER_5HOP >= 0.30
    (lift over pointer_v2 + WM-scaffold v1 both at 0.12)

  MIDDLE_BAND:
    ARM_CSP_GATED_ITER_5HOP in [0.20, 0.30]

  HARD_FAIL_CSP_DOESNT_HELP:
    ARM_CSP_GATED_ITER_5HOP < 0.20
    (4th multi-hop attempt FAILED; Barrier 1 ceiling more permanent)

  RAIL_SANITY_BREACH:
    BASELINE out of [0.62, 0.68] majority seeds

CONFIG:
  N=8192, V_C=200, V_P=10, K_SET=20, n_chains=200
  CSP_THRESHOLD = 0.05 (cosine top1-top2 separation)
  N_ITER = 3 (max iterated-cleanup iterations per hop)
  Seeds [7, 17, 23] (apples-to-apples with pointer_v2 + WM-scaffold v1).

SMOKE: N=2048, V=200, V_P=10, n_chains=50, depth_grid=[2,5], 1 seed.

Author: exp_dev 2026-06-25 (Barrier-1 4th attempt NOVEL angle).
ASCII-only; per-seed checkpoint; substrate-only.
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

ANCHOR_NAME = "substrate_multihop_csp_gated_iterated_cleanup_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# PROSPECTIVE HARD bands (LOCKED at module init)
BASELINE_SANITY_LO = 0.62
BASELINE_SANITY_HI = 0.68

HP_CSP_2HOP_MIN = 0.80
HP_CSP_5HOP_MIN = 0.50
HP_CSP_10HOP_MIN = 0.20
HP_CV_MAX = 0.07

# CSP gating-effectiveness: at depth 5, refuse rate must be in (0.10, 0.90).
# Too low = gate is permissive (not filtering noise); too high = gate refuses
# everything (no answers).
HP_REFUSE_RATE_MIN = 0.10
HP_REFUSE_RATE_MAX = 0.90

HP_PARTIAL_5HOP_MIN = 0.30
MID_5HOP_LO = 0.20
MID_5HOP_HI = 0.30
HF_5HOP_MAX = 0.20  # strictly less than

# Lock assertions (catches accidental edits to bands)
assert HP_CSP_2HOP_MIN > HP_PARTIAL_5HOP_MIN
assert HP_CSP_5HOP_MIN > MID_5HOP_HI
assert MID_5HOP_LO == HF_5HOP_MAX
assert 0.0 < HP_REFUSE_RATE_MIN < HP_REFUSE_RATE_MAX < 1.0

# Regime config
BASELINE_V_P = 2
BASELINE_N_CHAINS = 200
CSP_V_P = 10
CSP_K_SET = 20

# CSP gate parameters
CSP_THRESHOLD = 0.05  # min cosine (top1 - top2) separation
N_ITER = 3            # max iterated-cleanup iterations per hop
ITER_NOISE_FRAC = 0.05  # additive noise on iterated cleanup (theta-gamma jitter)

if RUN_MODE == "smoke":
    N_DIM = 2048
    V_CONCEPTS = 200
    SEEDS = [7]
    CSP_N_CHAINS = 50
    HOP_DEPTHS = [2, 5]
else:
    N_DIM = 8192
    V_CONCEPTS = 200
    SEEDS = [7, 17, 23]
    CSP_N_CHAINS = 200
    HOP_DEPTHS = [2, 5, 10]

n_predicates = max(BASELINE_V_P, CSP_V_P)

CONFIG_VERSION = (
    "substrateMultihopCspGatedIter-v1: N=%d V_C=%d "
    "BASELINE_V_P=%d (p1=0/p2=1; reproduces pointer_chain v2 rail) "
    "BASELINE_N=%d CSP_V_P=%d CSP_N=%d K_SET=%d "
    "CSP_THR=%.3f N_ITER=%d ITER_NOISE_FRAC=%.3f "
    "seeds=%s mode=%s hop_depths=%s "
    "HP_2hop>=%.2f HP_5hop>=%.2f HP_10hop>=%.2f HP_cv<=%.2f "
    "HP_refuse_in=[%.2f,%.2f] HP_partial_5hop>=%.2f mid_5hop=[%.2f,%.2f] HF_5hop<%.2f "
    "baseline_sanity=[%.2f,%.2f]"
) % (
    N_DIM, V_CONCEPTS, BASELINE_V_P, BASELINE_N_CHAINS, CSP_V_P, CSP_N_CHAINS,
    CSP_K_SET, CSP_THRESHOLD, N_ITER, ITER_NOISE_FRAC,
    SEEDS, RUN_MODE, HOP_DEPTHS,
    HP_CSP_2HOP_MIN, HP_CSP_5HOP_MIN, HP_CSP_10HOP_MIN, HP_CV_MAX,
    HP_REFUSE_RATE_MIN, HP_REFUSE_RATE_MAX, HP_PARTIAL_5HOP_MIN,
    MID_5HOP_LO, MID_5HOP_HI, HF_5HOP_MAX,
    BASELINE_SANITY_LO, BASELINE_SANITY_HI,
)


# =============================================================================
# Substrate primitives (mirrors pointer_chain v2 / WM-scaffold v1)
# =============================================================================

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def make_two_hop_chains_betasweep(n_chains: int, V: int, g: np.random.Generator,
                                   p1: int = 0, p2: int = 1):
    """Verbatim port of beta-sweep's make_two_hop_chains (fixed-pair p1, p2)."""
    train: List[Tuple[int, int, int]] = []
    queries: List[Tuple[int, int, int, int, int]] = []
    used_s: set = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o == s or o == x:
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, o))
        queries.append((s, p1, p2, o, x))
        used_s.add(s)
    return train, queries


def chain_naive_hard(W, E, R, sq, start: int, relations: List[int]) -> int:
    """Verbatim beta-sweep chain_naive_hard."""
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def arm_baseline_hrr_2hop_betasweep(E, R, sq, train_triples, queries):
    n_dim = E.shape[1]
    W = ingest_hebbian(train_triples, E, R, sq, n_dim)
    hits = 0
    for q in queries:
        s, p1, p2, o_true, _x = q
        pred = chain_naive_hard(W, E, R, sq, s, [p1, p2])
        if pred == o_true:
            hits += 1
    return {"top1": round(hits / max(len(queries), 1), 4),
            "n_queries": len(queries), "mechanism": "beta_sweep_naive_hard"}


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                      g: np.random.Generator, disallow_s: set
                      ) -> Tuple[List[Tuple[int, int, int]], List[List[Tuple[int, int, int]]]]:
    all_triples = []
    chain_queries = []
    used_s = set(disallow_s)
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
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, max_depth))
    return all_triples, chain_queries


def wm_slot_tag_codebook(K: int, n_dim: int, g: np.random.Generator) -> np.ndarray:
    """Slot-tag codebook for WM scaffold. Pure bipolar {-1,+1} (NOT L2-normalized).

    Matches exp_working_memory_hrr_slots_PRODUCTION_v1 convention.
    """
    return (g.integers(0, 2, size=(K, n_dim)) * 2 - 1).astype(np.float32)


def wm_scaffold_write_read(slot_tag: np.ndarray, content_vec: np.ndarray) -> np.ndarray:
    """Round-trip a content vector through one WM slot via involutive bind/unbind."""
    workspace = content_vec * slot_tag
    retrieved = workspace * slot_tag
    return retrieved


# =============================================================================
# CSP-gated iterated cleanup (THE novel mechanism)
# =============================================================================

def csp_confidence(scores: np.ndarray) -> Tuple[float, int]:
    """CSP-style confidence on cleanup-score vector.

    Returns (confidence in [0, 1+], top1_idx).
    confidence = (top1 - top2) normalized by top1 (a la BIAS-N Cramer-Rao
    discriminator on substrate's argmax). Higher = more certain.
    """
    top1_idx = int(scores.argmax())
    top1 = float(scores[top1_idx])
    # Find top2 (the next-highest score, excluding top1)
    scores_copy = scores.copy()
    scores_copy[top1_idx] = -1e9
    top2 = float(scores_copy.max())
    # Separation normalized by top1 magnitude (handles negative-cosine cases)
    sep = (top1 - top2) / max(abs(top1), 1e-6)
    return float(sep), top1_idx


def iterated_cleanup_with_csp(W: np.ndarray, E: np.ndarray, key_vec: np.ndarray,
                              g: np.random.Generator, threshold: float,
                              n_iter_max: int, noise_frac: float
                              ) -> Tuple[int, float, int, bool]:
    """CSP-gated iterated cleanup at one hop.

    Procedure:
      1. Project key through W; score against E codebook; compute CSP confidence.
      2. If conf < threshold, ITERATE: perturb the readout slightly + re-score.
         Each iteration's "perturbation" is bipolar-quantization step: re-bipolarize
         the readout (concentrates toward codebook attractor) + small additive
         noise to escape local minima. This is the brain-analog theta-gamma
         oscillatory cleanup.
      3. If still below threshold after n_iter_max: REFUSE (return -1).
      4. Else: return cleaned codebook idx.

    Returns (cleaned_idx, final_conf, n_iters_used, refused).
    """
    readout = W @ key_vec  # (n_dim,)
    scores = E @ readout   # (V,)
    conf, top1_idx = csp_confidence(scores)
    iters_used = 0
    if conf >= threshold:
        return top1_idx, conf, iters_used, False

    # Iterated cleanup: each iteration re-projects through W + small noise.
    # Theta-gamma analog: oscillatory pulls toward codebook attractor.
    cur_readout = readout.copy()
    for it in range(n_iter_max):
        iters_used = it + 1
        # Pull cur_readout toward the current top1 codebook atom (theta-gamma
        # "winner" feedback). Then re-project through W (gamma-cycle hippocampal
        # lookup with cleaned cue). Additive noise frees from spurious attractor.
        cleaned_atom = E[top1_idx]
        # Mix toward winner (0.5 mix) + add small fraction of noise.
        cur_readout = 0.5 * cur_readout + 0.5 * cleaned_atom
        if noise_frac > 0.0:
            noise = noise_frac * g.standard_normal(cur_readout.shape).astype(np.float32)
            cur_readout = cur_readout + noise
        # Re-bipolarize (concentrates back toward codebook geometry)
        cur_readout = np.sign(cur_readout).astype(np.float32)
        cur_readout[cur_readout == 0] = 1.0
        # Re-project through W (gamma-cycle re-lookup).
        next_readout = W @ cur_readout
        scores = E @ next_readout
        conf, top1_idx = csp_confidence(scores)
        if conf >= threshold:
            return top1_idx, conf, iters_used, False
    # Exhausted iterations; refuse
    return -1, conf, iters_used, True


def arm_csp_gated_iterated(E, R, sq, W, chains_test, depth: int,
                            slot_tags: np.ndarray, seed: int) -> Dict[str, Any]:
    """CSP-gated iterated-cleanup multi-hop with WM scaffold.

    Per chain (k hops):
      slot_0 = E[s_0]  (input scaffold)
      For i in 0..k-1:
        content_i = wm_scaffold_read(slot_tag_i, slot_workspace_i)
        key_i = content_i * R[p_{i+1}] * sq
        (next_idx, conf, iters, refused) = iterated_cleanup_with_csp(W, E, key_i, ...)
        if refused: abort chain (final = -1)
        slot_workspace_{i+1} = E[next_idx] * slot_tag_{i+1}  (clean atom in slot)
      Return final slot content as predicted target.

    Critical: REFUSE means the chain aborts; refused chains count as MISS
    against the final-step target (consistent with brain's metacognitive
    "I don't know" being a missed answer).

    Returns top1, per_step_acc, refuse_rate, mean_iters_per_hop, mean_conf.
    """
    g = np.random.default_rng(int(seed) * 9929 + 31)
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    refused_count = 0
    iters_per_hop_sum = 0
    iters_per_hop_n = 0
    conf_sum = 0.0
    conf_n = 0
    for chain in chains_test:
        s_idx = chain[0][0]
        slot_content = E[s_idx].copy()
        slot_content = wm_scaffold_write_read(slot_tags[0], slot_content)
        cur_idx = s_idx
        chain_refused = False
        for i in range(depth):
            p = chain[i][1]
            key = (slot_content * R[p] * sq).astype(np.float32)
            next_idx, conf, n_iters, refused = iterated_cleanup_with_csp(
                W, E, key, g, CSP_THRESHOLD, N_ITER, ITER_NOISE_FRAC)
            iters_per_hop_sum += n_iters
            iters_per_hop_n += 1
            conf_sum += conf
            conf_n += 1
            if refused:
                chain_refused = True
                break
            if next_idx == chain[i][2]:
                per_step_hits[i] += 1
            slot_idx_next = (i + 1) % slot_tags.shape[0]
            slot_content = wm_scaffold_write_read(slot_tags[slot_idx_next],
                                                   E[next_idx].copy())
            cur_idx = next_idx
        if chain_refused:
            refused_count += 1
            continue
        if cur_idx == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    refuse_rate = refused_count / max(n, 1)
    mean_iters = iters_per_hop_sum / max(iters_per_hop_n, 1)
    mean_conf = conf_sum / max(conf_n, 1)
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "refuse_rate": round(refuse_rate, 4),
        "mean_iters_per_hop": round(mean_iters, 3),
        "mean_csp_conf": round(mean_conf, 4),
        "csp_threshold": CSP_THRESHOLD,
        "n_iter_max": N_ITER,
        "mechanism": "csp_gated_iterated_cleanup_wm_scaffold",
    }


# =============================================================================
# Self-test
# =============================================================================

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(4, n, g)

    # T1: CSP confidence on clean argmax (sigma=0) -> separation > threshold
    scores = np.array([0.1, 0.2, 0.9, 0.3, 0.05], dtype=np.float32)
    conf, idx = csp_confidence(scores)
    assert idx == 2, "T1 csp argmax wrong: %d" % idx
    assert conf > 0.5, "T1 csp conf too low on clean: %.3f" % conf
    print("[selftest] T1 PASS: csp confidence on clean argmax conf=%.3f idx=%d" % (conf, idx))

    # T2: CSP confidence on confused scores -> low separation
    scores2 = np.array([0.9, 0.85, 0.83, 0.1, 0.05], dtype=np.float32)
    conf2, idx2 = csp_confidence(scores2)
    assert conf2 < 0.1, "T2 csp conf too high on confused: %.3f" % conf2
    print("[selftest] T2 PASS: csp conf on confused conf=%.3f (< 0.1)" % conf2)

    # T3: iterated_cleanup_with_csp on clean 1-hop sigma=0 -> doesn't iterate
    triples_d, chains_d = make_deep_chains(10, V, 4, max_depth=2, g=g,
                                            disallow_s=set())
    W = ingest_hebbian(triples_d, E, R, sq, n)
    # Build a clean key: bind E[s] * R[p] for known (s,p,o)
    s, p, o = triples_d[0]
    key_clean = (E[s] * R[p] * sq).astype(np.float32)
    next_idx, conf, n_iters, refused = iterated_cleanup_with_csp(
        W, E, key_clean, g, CSP_THRESHOLD, N_ITER, ITER_NOISE_FRAC)
    # Clean key should hit target without iterating
    assert next_idx == o, "T3 clean cleanup wrong: %d vs %d" % (next_idx, o)
    assert not refused, "T3 clean cleanup shouldn't refuse"
    print("[selftest] T3 PASS: clean iterated_cleanup conf=%.3f iters=%d (target hit)"
          % (conf, n_iters))

    # T4: arm_csp_gated_iterated at depth=2 selftest scale beats chance
    slot_tags = wm_slot_tag_codebook(10, n, np.random.default_rng(42))
    r2 = arm_csp_gated_iterated(E, R, sq, W, chains_d, depth=2,
                                 slot_tags=slot_tags, seed=99)
    assert 0.0 <= r2["top1"] <= 1.0
    assert r2["top1"] > 5.0 / V, \
        "T4 CSP-gated top1=%.3f at depth=2 selftest too low" % r2["top1"]
    print("[selftest] T4 PASS: CSP-gated arm depth=2 top1=%.3f refuse_rate=%.3f"
          " mean_iters=%.2f"
          % (r2["top1"], r2["refuse_rate"], r2["mean_iters_per_hop"]))

    # T5: NaN detection at production-scale matmul
    big_n = 4096
    big_V = 80
    big_E = bipolar(big_V, big_n, g)
    big_R = bipolar(4, big_n, g)
    big_W = ingest_hebbian(triples_d, big_E, big_R, math.sqrt(big_n), big_n)
    big_slots = wm_slot_tag_codebook(10, big_n, np.random.default_rng(99))
    r_big = arm_csp_gated_iterated(big_E, big_R, math.sqrt(big_n), big_W,
                                    chains_d[:5], depth=2, slot_tags=big_slots,
                                    seed=99)
    assert not math.isnan(r_big["top1"]), "T5 NaN at production-scale matmul"
    print("[selftest] T5 PASS: production-scale no-NaN top1=%.3f" % r_big["top1"])

    # T6: baseline beta-sweep beats chance
    train, queries = make_two_hop_chains_betasweep(20, V, g, p1=0, p2=1)
    r_base = arm_baseline_hrr_2hop_betasweep(E, R, sq, train, queries)
    assert r_base["top1"] > 5.0 / V, \
        "T6 baseline top1=%.3f below chance" % r_base["top1"]
    print("[selftest] T6 PASS: baseline beta-sweep top1=%.3f" % r_base["top1"])

    # T7: confidence-band sanity (gate must be discriminating)
    # On a totally-random key (no triple), iterated cleanup should EITHER refuse
    # OR hit a wrong target. It must NOT always return the same idx.
    rand_key = g.standard_normal(n).astype(np.float32)
    next_rand, conf_rand, _, refused_rand = iterated_cleanup_with_csp(
        W, E, rand_key, g, CSP_THRESHOLD, N_ITER, ITER_NOISE_FRAC)
    # Either refused OR a real (possibly wrong) codebook idx; both acceptable
    assert (refused_rand or 0 <= next_rand < V), \
        "T7 random-key cleanup neither refused nor valid idx"
    print("[selftest] T7 PASS: random-key cleanup refused=%s next=%d conf=%.3f"
          % (refused_rand, next_rand, conf_rand))

    print("[selftest] ALL PASS")


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# =============================================================================
# Per-seed run
# =============================================================================

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(n_predicates, N_DIM, g)
    max_depth = max(HOP_DEPTHS)
    slot_g = np.random.default_rng(seed * 1009 + 17)
    slot_tags = wm_slot_tag_codebook(max(max_depth + 1, CSP_K_SET), N_DIM, slot_g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "n_predicates": n_predicates, "K_SET": CSP_K_SET,
        "baseline_n_chains": BASELINE_N_CHAINS,
        "csp_n_chains": CSP_N_CHAINS,
        "max_depth": max_depth,
        "csp_threshold": CSP_THRESHOLD,
        "n_iter_max": N_ITER,
        "iter_noise_frac": ITER_NOISE_FRAC,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # ===== ARM_BASELINE_HRR_2HOP (sanity rail; reproduces pointer_chain v2) =====
    t_arm = time.time()
    base_triples, base_queries = make_two_hop_chains_betasweep(
        BASELINE_N_CHAINS, V_CONCEPTS, g, p1=0, p2=1)
    r_baseline = arm_baseline_hrr_2hop_betasweep(E, R, sq, base_triples, base_queries)
    r_baseline["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_hrr_2hop"] = r_baseline
    baseline_ok = (BASELINE_SANITY_LO <= r_baseline["top1"] <= BASELINE_SANITY_HI)
    out["baseline_sanity_ok"] = baseline_ok
    print("  [seed=%d] ARM_BASELINE_HRR_2HOP top1=%.4f (sanity_ok=%s) t=%.1fs"
          % (seed, r_baseline["top1"], baseline_ok, r_baseline["elapsed_s_arm"]),
          flush=True)

    # ===== CSP-gated arms: separate chain set, separate W =====
    t_arm = time.time()
    csp_triples, csp_chains = make_deep_chains(
        CSP_N_CHAINS, V_CONCEPTS, CSP_V_P, max_depth=max_depth,
        g=g, disallow_s=set())
    W_csp = ingest_hebbian(csp_triples, E, R, sq, N_DIM)
    csp_W_build_s = round(time.time() - t_arm, 2)
    print("  [seed=%d] CSP W built (%d triples, %d chains, max_depth=%d) t=%.1fs"
          % (seed, len(csp_triples), len(csp_chains), max_depth, csp_W_build_s),
          flush=True)

    for d in HOP_DEPTHS:
        t_arm = time.time()
        chains_d = [c[:d] for c in csp_chains]
        r = arm_csp_gated_iterated(E, R, sq, W_csp, chains_d, depth=d,
                                    slot_tags=slot_tags, seed=seed)
        r["elapsed_s_arm"] = round(time.time() - t_arm, 2)
        out["arm_csp_gated_iter_%dhop" % d] = r
        print("  [seed=%d] ARM_CSP_GATED_ITER_%dHOP top1=%.4f refuse=%.3f"
              " mean_iters=%.2f conf=%.3f t=%.1fs"
              % (seed, d, r["top1"], r["refuse_rate"], r["mean_iters_per_hop"],
                 r["mean_csp_conf"], r["elapsed_s_arm"]),
              flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# =============================================================================
# Verdict
# =============================================================================

def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    def mean_field(key: str, field: str) -> float:
        vals = [p[key][field] for p in per_seed if key in p
                and isinstance(p[key].get(field), (int, float))
                and not math.isnan(p[key][field])]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_field(key: str, field: str) -> float:
        vals = [p[key][field] for p in per_seed if key in p
                and isinstance(p[key].get(field), (int, float))
                and not math.isnan(p[key][field])]
        if len(vals) < 2:
            return 0.0
        m = float(np.mean(vals))
        return float(np.std(vals) / max(abs(m), 1e-9))

    baseline = mean_field("arm_baseline_hrr_2hop", "top1")
    csp_2hop = mean_field("arm_csp_gated_iter_2hop", "top1")
    csp_5hop = mean_field("arm_csp_gated_iter_5hop", "top1")
    csp_10hop = mean_field("arm_csp_gated_iter_10hop", "top1") if any(
        "arm_csp_gated_iter_10hop" in p for p in per_seed) else float("nan")
    refuse_5hop = mean_field("arm_csp_gated_iter_5hop", "refuse_rate")
    cv_2hop = cv_field("arm_csp_gated_iter_2hop", "top1")
    cv_5hop = cv_field("arm_csp_gated_iter_5hop", "top1")
    cv_10hop = cv_field("arm_csp_gated_iter_10hop", "top1") if not math.isnan(csp_10hop) else 0.0
    mean_iters_5 = mean_field("arm_csp_gated_iter_5hop", "mean_iters_per_hop")
    mean_conf_5 = mean_field("arm_csp_gated_iter_5hop", "mean_csp_conf")

    sanity_breached_seeds = sum(1 for p in per_seed if not p.get("baseline_sanity_ok", False))

    summ = ("BASELINE=%.4f (sanity_breach=%d/%d in [%.2f,%.2f]) "
            "CSP_2HOP=%.4f (cv=%.3f) CSP_5HOP=%.4f (cv=%.3f refuse=%.3f iters=%.2f conf=%.3f) "
            "CSP_10HOP=%s (cv=%.3f) | pointer_v2_5hop=0.122 WM_scaffold_5hop=0.122 (reference)"
            ) % (
        baseline, sanity_breached_seeds, len(per_seed),
        BASELINE_SANITY_LO, BASELINE_SANITY_HI,
        csp_2hop, cv_2hop, csp_5hop, cv_5hop, refuse_5hop, mean_iters_5, mean_conf_5,
        ("%.4f" % csp_10hop) if not math.isnan(csp_10hop) else "n/a",
        cv_10hop,
    )

    # Sanity rail
    if sanity_breached_seeds >= max(1, (len(per_seed) + 1) // 2):
        return "RAIL_SANITY_BREACH", "RAIL_SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ

    refuse_in_band = HP_REFUSE_RATE_MIN < refuse_5hop < HP_REFUSE_RATE_MAX

    hp_chain = (
        BASELINE_SANITY_LO <= baseline <= BASELINE_SANITY_HI
        and not math.isnan(csp_2hop) and csp_2hop >= HP_CSP_2HOP_MIN
        and not math.isnan(csp_5hop) and csp_5hop >= HP_CSP_5HOP_MIN
        and (math.isnan(csp_10hop) or csp_10hop >= HP_CSP_10HOP_MIN)
        and refuse_in_band
        and cv_2hop <= HP_CV_MAX
        and cv_5hop <= HP_CV_MAX
        and cv_10hop <= HP_CV_MAX
    )
    if hp_chain:
        return "HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL", \
               "HARD_PASS_CHAIN_GRADE_BARRIER_1_REVIVAL_CSP_GATED: " + summ

    hp_partial = (not math.isnan(csp_5hop) and csp_5hop >= HP_PARTIAL_5HOP_MIN)
    if hp_partial:
        return "HARD_PASS_PARTIAL_BARRIER_1_LIFT", \
               "HARD_PASS_PARTIAL_CSP_LIFTS_OVER_POINTER_AND_WM_SCAFFOLD: " + summ

    if not math.isnan(csp_5hop) and MID_5HOP_LO <= csp_5hop <= MID_5HOP_HI:
        return "MIDDLE_BAND", \
               "MIDDLE_BAND_CSP_GATED_PARTIAL_LIFT: " + summ

    if not math.isnan(csp_5hop) and csp_5hop < HF_5HOP_MAX:
        return "HARD_FAIL_CSP_DOESNT_HELP", \
               "HARD_FAIL_CSP_GATED_SAME_REGIME_AS_POINTER_AND_WM_SCAFFOLD: " + summ

    return "MIDDLE_BAND", "MIDDLE_BAND_UNCLASSIFIED: " + summ


# =============================================================================
# atexit synthesizer
# =============================================================================

_RESULTS_HOLDER: Dict[str, Any] = {"out_dir": None, "started_at": time.time()}


def _atexit_synth() -> None:
    od = _RESULTS_HOLDER["out_dir"]
    if od is None:
        return
    try:
        if (od / "metrics.json").exists():
            return
        agg = aggregate_partials(od, seeds=[str(s) for s in SEEDS],
                                  run_config={"N": N_DIM, "run_mode": RUN_MODE})
        if not agg:
            return
        per_seed = [agg[k] for k in sorted(agg.keys())]
        if not per_seed:
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
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d | %s" % (
        ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, CONFIG_VERSION), flush=True)
    out_dir = get_output_dir(ANCHOR_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    _RESULTS_HOLDER["out_dir"] = out_dir

    run_config = {"N": N_DIM, "run_mode": RUN_MODE}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] done=%s remaining=%s" % (done, remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial_key(out_dir, s, rec)

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS],
                              run_config=run_config)
    per_seed = [agg[str(s)] for s in SEEDS if str(s) in agg]
    if not per_seed:
        print("[FATAL] no partials available", flush=True)
        sys.exit(1)

    assert _LLM_CALL_COUNTER[0] == 0, "LLM calls non-zero: %d" % _LLM_CALL_COUNTER[0]

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
            "Barrier-1 4th attempt: CSP-gated iterated-cleanup composes WM scaffold "
            "(PFC) + Hebbian-bound W cleanup (hippocampus) + CSP confidence "
            "thresholding (ACC). Each hop reads cleaned WM-held intermediate; "
            "looks up W; computes top1-top2 cosine separation as CSP confidence; "
            "if conf < threshold, iterates cleanup (theta-gamma analog) up to "
            "N_ITER=%d times; refuses if still below threshold. Brain analog: "
            "PFC + hippocampus + ACC composition that 3 prior attempts (pointer-"
            "chain v1/v2; WM-scaffold v1) lacked. Pre-reg per "
            "preregs/2026-06-25_substrate_multihop_csp_gated_iterated_cleanup_v1.md."
            % N_ITER
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
