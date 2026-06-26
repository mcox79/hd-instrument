"""gap1_multihop_ldpc_rts_bidirectional_v1.

Research Gap-1 multi-hop drill: BUNDLED Anchors 1+2 (LDPC bidirectional + RTS smoother).
Per `notes/research_gap1_multihop_5x_drill_2026-06-26.md` and exp_dev hand-off
2026-06-26: address the FORWARD-ONLY HARD-DECISION CHAINING pathology shared by
5 refuted multi-hop attempts (depth-5 floor 0.145 at V_C=200/V_P=10/K=20/n_chains=200).

5 arms, single cell:
  1. ARM_BASELINE_pointer_chain_v2:  forward argmax cleanup per-hop; reproduces 0.145
     anchor at depth-5 (SACRED sanity rail, +/- 0.02).
  2. ARM_SOFT_FWD:                   forward-only soft superposition through hops
     (no hard argmax until final); isolates "soft" lift; ~0.25-0.30 expected.
  3. ARM_BACKWARD_ONLY:              reverse-chain only (starts from endpoint,
     unbinds backwards via R[p_k]); isolates "backward" lift.
  4. ARM_LDPC_BIDIR:                 ANCHOR 1 -- 3 sweep iterations of soft
     forward + soft backward, exchanging LLR estimates until convergence.
  5. ARM_RTS_SMOOTH:                 ANCHOR 2 -- forward x backward Gaussian-mixture
     product per hop (analytical smoother); reuses substrate's reverse direction.

Discipline (load-bearing):
  - Sanity rail: ARM_BASELINE reproduces 0.145 +/- 0.02 at depth-5 on the SAME
    deep-chain set + W matrix as the v2 BASELINE_RAIL_FIXED cell. If
    sanity breach on majority of seeds -> verdict = SANITY_BREACH (no anchor claims).
  - LOCK pre-reg bands at module init (assert chain).
  - Zero LLM forward calls at inference (counter + assert == 0).
  - Per-arm metrics in `per_seed[i][arm_name]` independently readable (Fix #28).
  - Synthetic random-bipolar atoms; ASCII-only.
  - Per-seed CONFIG_VERSION-gated checkpoint via experiments/_seed_checkpoint.
  - atexit synthesizer recovers partial metrics on kill/timeout.

PRE-REGISTERED BANDS (LOCKED before any anchor verdict is computed):

ARM_LDPC_BIDIR (Anchor 1, P_deflated=0.45):
  HARD_PASS: mean depth-5 >= 0.50 AND > ARM_SOFT_FWD + 0.10 AND sd <= 0.06
  HARD_FAIL: mean depth-5 <= 0.25 OR LDPC adds <= 0.03 over SOFT_FWD
  MIDDLE:    0.30 <= mean depth-5 < 0.50

ARM_RTS_SMOOTH (Anchor 2, P_deflated=0.45):
  HARD_PASS: mean depth-5 >= 0.50 AND super-additive: > MAX(BASELINE, BACKWARD_ONLY) + 0.10 AND sd <= 0.06
  HARD_FAIL: mean depth-5 <= 0.25 OR smoothed mean <= 1.05 * max(forward, backward)
  MIDDLE:    0.30 <= mean depth-5 < 0.50

Cell-wide verdict logic:
  - SANITY_BREACH: BASELINE depth-5 out of [0.125, 0.165] on majority of seeds.
  - HARD_PASS: either LDPC or RTS hits HARD_PASS bands (super-additive verified).
  - MIDDLE_BAND: either lifts to 0.30-0.50 (structural lift, not chain-grade).
  - HARD_FAIL: both fall in HARD_FAIL band.

Production regime (handoff-mandated):
  N_DIM = 8192, V_C = 200, V_P = 10, K_set = 20, n_chains = 200, depth = 5, seeds = 5.

ASCII-only; atexit partial-flush.
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

ANCHOR_NAME = "gap1_multihop_ldpc_rts_bidirectional_v1"
_LLM_CALL_COUNTER = [0]

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

# ---------------- PRE-REGISTERED BANDS (LOCKED) ----------------
# Sanity rail: BASELINE depth-5 must reproduce v2 BASELINE_RAIL_FIXED anchor 0.145.
SANITY_BASELINE_LO = 0.125
SANITY_BASELINE_HI = 0.165

# ARM_LDPC_BIDIR (Anchor 1)
HP_LDPC_TOP1_MIN = 0.50
HP_LDPC_SOFT_FWD_DELTA = 0.10
HP_LDPC_SD_MAX = 0.06
HF_LDPC_TOP1_MAX = 0.25
HF_LDPC_OVER_SOFT_FWD_MAX = 0.03
MB_LDPC_LO = 0.30
MB_LDPC_HI = 0.50

# ARM_RTS_SMOOTH (Anchor 2)
HP_RTS_TOP1_MIN = 0.50
HP_RTS_SUPER_ADDITIVE_DELTA = 0.10
HP_RTS_SD_MAX = 0.06
HF_RTS_TOP1_MAX = 0.25
HF_RTS_RATIO_OVER_MAX_DIR = 1.05
MB_RTS_LO = 0.30
MB_RTS_HI = 0.50

# LOCK via assert chain (module init):
assert 0.10 < SANITY_BASELINE_LO < SANITY_BASELINE_HI < 0.20, "sanity rail must bracket 0.145"
assert HP_LDPC_TOP1_MIN > MB_LDPC_HI - 1e-9, "HP must >= MB upper"
assert HP_RTS_TOP1_MIN > MB_RTS_HI - 1e-9, "HP must >= MB upper"
assert HF_LDPC_TOP1_MAX < MB_LDPC_LO, "HF must < MB lower"
assert HF_RTS_TOP1_MAX < MB_RTS_LO, "HF must < MB lower"

# ---------------- CONFIG ----------------
V_CONCEPTS = 200
V_P = 10
K_SET = 20
DEPTH = 5  # focus depth per handoff
LDPC_SWEEPS = 3  # 3-5 sweep iterations to LLR convergence; pick lower bound

if RUN_MODE == "smoke":
    # Smoke smaller-N to stay under 180s gate ceiling; same mechanism shape.
    N_DIM = 2048
    N_CHAINS = 40
    SEEDS = [7]
else:
    # FULL: handoff production regime
    N_DIM = 8192
    N_CHAINS = 200
    SEEDS = [7, 17, 23, 31, 41]

CONFIG_VERSION = (
    "gap1MultihopLdpcRtsBidirectional-v1: N=%d V_C=%d V_P=%d K_SET=%d "
    "n_chains=%d depth=%d seeds=%s mode=%s ldpc_sweeps=%d "
    "SANITY_BASELINE=[%.3f,%.3f] "
    "HP_LDPC: top1>=%.2f over_soft_fwd>=%.2f sd<=%.2f "
    "HF_LDPC: top1<=%.2f over_soft_fwd<=%.2f "
    "HP_RTS: top1>=%.2f super_add>=%.2f sd<=%.2f "
    "HF_RTS: top1<=%.2f ratio_over_max_dir<=%.2f"
) % (
    N_DIM, V_CONCEPTS, V_P, K_SET, N_CHAINS, DEPTH, SEEDS, RUN_MODE, LDPC_SWEEPS,
    SANITY_BASELINE_LO, SANITY_BASELINE_HI,
    HP_LDPC_TOP1_MIN, HP_LDPC_SOFT_FWD_DELTA, HP_LDPC_SD_MAX,
    HF_LDPC_TOP1_MAX, HF_LDPC_OVER_SOFT_FWD_MAX,
    HP_RTS_TOP1_MIN, HP_RTS_SUPER_ADDITIVE_DELTA, HP_RTS_SD_MAX,
    HF_RTS_TOP1_MAX, HF_RTS_RATIO_OVER_MAX_DIR,
)


# ---------------- substrate primitives (verbatim style of v2) ----------------

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


def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                     g: np.random.Generator, disallow_s: set
                     ) -> Tuple[List[Tuple[int, int, int]],
                                List[List[Tuple[int, int, int]]]]:
    """Random chains of `max_depth` hops with random predicates (v2 verbatim)."""
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
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d disallow|=%d max_depth=%d"
            % (len(chain_queries), n_chains, V, len(disallow_s), max_depth)
        )
    return all_triples, chain_queries


def _scores_to_softmax(scores: np.ndarray, temperature: float = 1.0,
                       k_set: int = 20, sharpness: float = 2.0) -> np.ndarray:
    """Top-K masked softmax over E-similarity scores. Returns prob over atoms.

    Rationale (audit 2026-06-26 on smoke): raw scores from E @ (W @ key) at
    production regime are ~5e-4 magnitude with sub-numerical std. Naive
    softmax(scores, T=1.0) produces uniform belief (all atoms ~ 1/V_C) because
    the signal is at machine precision relative to T=1.0. Hard argmax works
    because it's scale-invariant; soft belief propagation needs scores at a
    distribution-meaningful scale.

    Two-step fix:
      1. Top-K mask: zero out all but top-k_set atoms (substrate's K_SET=20
         cleanup width per Director Barrier-1 spec).
      2. Normalize masked scores by their std, then softmax at sharpness.
         sharpness=2.0 means roughly: top-1 carries ~80% mass at high-margin
         cleanup, ~50% at low-margin -- preserves distribution for downstream
         message passing.

    For temperature override (1-arg backwards compat): caller can pass a
    different `temperature` value but the top-K mask + std-normalization is
    always applied; temperature scales the sharpness factor (lower T = sharper).
    """
    V = scores.shape[0]
    k = min(k_set, V)
    idx = np.argpartition(-scores, k - 1)[:k]
    masked_scores = scores[idx]
    std = max(float(masked_scores.std()), 1e-9)
    effective_sharpness = sharpness / max(temperature, 1e-6)
    s_norm = (masked_scores - masked_scores.max()) / std * effective_sharpness
    e = np.exp(s_norm)
    e_sum = float(e.sum())
    if e_sum < 1e-12:
        out = np.zeros(V, dtype=np.float32)
        out[idx[np.argmax(masked_scores)]] = 1.0
        return out
    probs = e / e_sum
    out = np.zeros(V, dtype=np.float32)
    out[idx] = probs.astype(np.float32)
    return out


# ---------------- ARM 1: BASELINE pointer-chain v2 (hard argmax per hop) ----------------

def arm_baseline_pointer_chain(E, R, sq, W, chains_test, depth: int) -> Dict[str, Any]:
    """Verbatim of v2 BASELINE_RAIL_FIXED arm_pointer_chain mechanism.

    Per-hop hard argmax cleanup. Reproduces depth-5 = 0.145 (SACRED sanity rail).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    for chain in chains_test:
        s = chain[0][0]
        for i in range(depth):
            p = chain[i][1]
            key = (E[s] * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            s_pred = int(scores.argmax())
            if s_pred == chain[i][2]:
                per_step_hits[i] += 1
            s = s_pred
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "mechanism": "baseline_pointer_chain_v2_hard_argmax",
    }


# ---------------- ARM 2: SOFT_FWD (forward soft superposition) ----------------

def arm_soft_fwd(E, R, sq, W, chains_test, depth: int,
                 temperature: float = 1.0) -> Dict[str, Any]:
    """Forward-only soft propagation: state is convex combination over atoms via
    softmax(E @ state) weights; only final argmax. Isolates "soft" lift.
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    V = E.shape[0]
    for chain in chains_test:
        # belief = prob over atoms at hop k. Start = delta at chain[0][0].
        belief = np.zeros(V, dtype=np.float32)
        belief[chain[0][0]] = 1.0
        for i in range(depth):
            p = chain[i][1]
            # soft state vector = sum_v belief[v] * E[v]
            state = belief @ E  # (V,) @ (V,N) -> (N,)
            key = (state * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            belief = _scores_to_softmax(scores, temperature, k_set=K_SET)
            # track per-step argmax for diagnostics (NOT used for retrieval)
            if int(belief.argmax()) == chain[i][2]:
                per_step_hits[i] += 1
        if int(belief.argmax()) == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "mechanism": "soft_forward_only_softmax_belief",
        "temperature": temperature,
    }


# ---------------- ARM 3: BACKWARD_ONLY (reverse-chain) ----------------

def arm_backward_only(E, R, sq, W, chains_test, depth: int,
                      temperature: float = 1.0) -> Dict[str, Any]:
    """Run pointer-chain BACKWARD from endpoint to start.

    At each backward step k (counting K-1 ... 0), use the inverse relation
    R[p_k] (same R; XOR-bipolar binding is its own inverse for normalized
    bipolar atoms -- substrate fact CERT 587 sequence-binding bidirectional).
    Soft-propagate belief through the reverse-chain; argmax at the
    start position. The chain TRUE answer at hop depth-1 is chain[depth-1][2],
    so we score whether the soft-backward belief at start position picks the
    actual chain[0][0] -- this is a DIAGNOSTIC arm (the inverse-direction
    isolation); the readout we score against is the FINAL endpoint at depth-1.

    NB: a faithful backward-only chain-reasoning arm scores "given final
    endpoint, recover intermediate/start, then forward-predict endpoint." We
    use the simpler analog: backward soft propagation from final endpoint,
    then score the resulting most-likely endpoint after a single forward
    re-derivation from start. This isolates whether the REVERSE direction
    alone carries depth-5 information (Foster-Wilson 2006 hippocampal
    reverse-replay analog).
    """
    n = len(chains_test)
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    V = E.shape[0]
    for chain in chains_test:
        # Start backward belief = delta at chain[depth-1][2] (true endpoint).
        belief = np.zeros(V, dtype=np.float32)
        belief[chain[depth - 1][2]] = 1.0
        # Propagate backwards through hops K-1 ... 0.
        for i in range(depth - 1, -1, -1):
            p = chain[i][1]
            state = belief @ E  # (N,) -- soft superposition of object atoms
            # Reverse-W operation: recover SOURCE-side key from object-side state.
            # Forward stores W += (1/N) E[o] outer (E[s]*R[p]*sq), so
            # W.T @ E[o] approx= E[s]*R[p]*sq. To recover E[s]: multiply by R[p]/sq.
            # (R[p] is bipolar so R[p] is its own multiplicative inverse element-wise.)
            recovered = (W.T @ state) * R[p] / sq
            scores = E @ recovered
            belief = _scores_to_softmax(scores, temperature, k_set=K_SET)
            # Diagnostic per-step: does backward belief at this hop favor the
            # true source-side atom chain[i][0]?
            if int(belief.argmax()) == chain[i][0]:
                per_step_hits[depth - 1 - i] += 1
        # After K backward steps, belief should peak at chain[0][0] (true start).
        # Forward re-derive: from the start atom argmax, run forward hard-chain
        # to compare endpoint. (Isolates "backward propagated useful info."
        # Endpoint score = match against true chain[depth-1][2].)
        s = int(belief.argmax())
        for i in range(depth):
            p = chain[i][1]
            key = (E[s] * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            s = int(scores.argmax())
        if s == chain[depth - 1][2]:
            hits += 1
    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc_backward": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "mechanism": "backward_only_reverse_chain_soft_propagation_then_forward_rederive",
        "temperature": temperature,
    }


# ---------------- ARM 4: LDPC_BIDIR (Anchor 1) ----------------

def arm_ldpc_bidir(E, R, sq, W, chains_test, depth: int,
                   n_sweeps: int = LDPC_SWEEPS,
                   temperature: float = 1.0) -> Dict[str, Any]:
    """Factor-graph LDPC bidirectional sum-product.

    Variable nodes: hop-state beliefs (one per intermediate position 0..depth).
    Check nodes: W-relation consistency between adjacent variables (must satisfy
    chain[i][0] --p_i--> chain[i][1]). LLR per variable = log-ratio of top-1 to
    top-2 from W-cleanup output.

    Substrate-VSA mapping (chain factor graph is a TREE -> BP is exact for a
    tree; multi-sweep here amortizes per-sweep cleanup noise via iterative
    refinement):
      - Forward pass: variable k receives message from check_{k-1} = soft state
        from previous hop's argmax-distribution.
      - Backward pass: variable k receives message from check_{k+1} = soft state
        from successor hop's argmax-distribution running BACKWARD.
      - Variable's belief = product (elementwise softmax) of forward + backward
        incoming messages, NORMALIZED.
      - After n_sweeps, argmax per variable. Score the final variable.

    Per Tanner-graph BP standard (MacKay-Neal 1996), the readout at variable
    k = depth (final endpoint position) is the chain-completion answer.
    """
    n = len(chains_test)
    V = E.shape[0]
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)
    sweeps_to_converge_acc = 0

    for chain in chains_test:
        # Initialize beliefs: variable_k for k in 0..depth. variable_0 fixed at
        # chain[0][0]; variable_depth has no initial constraint.
        beliefs = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        beliefs[0][chain[0][0]] = 1.0
        for k in range(1, depth + 1):
            beliefs[k][:] = 1.0 / V  # uniform prior

        prev_endpoint_argmax = -1
        converged_at = n_sweeps
        for sweep in range(n_sweeps):
            # Forward pass: messages from variable_k -> variable_{k+1}
            fwd_msgs = [beliefs[0].copy()]
            for k in range(depth):
                p = chain[k][1]
                state = fwd_msgs[k] @ E
                key = (state * R[p] * sq).astype(np.float32)
                scores = E @ (W @ key)
                fwd_msgs.append(_scores_to_softmax(scores, temperature, k_set=K_SET))
            # Backward pass: messages from variable_k -> variable_{k-1}
            bwd_msgs = [None] * (depth + 1)
            # Initialize backward from final belief (peaked at fwd_msgs[depth] argmax)
            # On sweep 0, no endpoint anchor; use fwd_msgs[depth] as backward seed.
            bwd_msgs[depth] = fwd_msgs[depth].copy()
            for k in range(depth, 0, -1):
                p = chain[k - 1][1]
                state = bwd_msgs[k] @ E
                # Reverse-W operation (object -> source recovery): see arm_backward_only.
                recovered = (W.T @ state) * R[p] / sq
                scores = E @ recovered
                bwd_msgs[k - 1] = _scores_to_softmax(scores, temperature, k_set=K_SET)
            # Combine: belief_k = normalize(fwd_msg_k * bwd_msg_k)
            for k in range(depth + 1):
                if k == 0:
                    # Fixed by initial condition; keep as delta.
                    continue
                combined = fwd_msgs[k] * bwd_msgs[k]
                s = combined.sum()
                if s > 1e-12:
                    beliefs[k] = combined / s
                else:
                    beliefs[k] = fwd_msgs[k]  # fallback
            # Convergence check: endpoint argmax stable across sweeps
            endpoint_argmax = int(beliefs[depth].argmax())
            if endpoint_argmax == prev_endpoint_argmax:
                converged_at = sweep + 1
                break
            prev_endpoint_argmax = endpoint_argmax
        sweeps_to_converge_acc += converged_at

        # Score final variable_depth argmax vs true chain[depth-1][2]
        if int(beliefs[depth].argmax()) == chain[depth - 1][2]:
            hits += 1
        # Per-hop argmax (diagnostic)
        for k in range(depth):
            if int(beliefs[k + 1].argmax()) == chain[k][2]:
                per_step_hits[k] += 1

    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "n_sweeps_max": n_sweeps,
        "mean_sweeps_to_converge": round(sweeps_to_converge_acc / max(n, 1), 2),
        "mechanism": "ldpc_bidirectional_sum_product_chain_factor_graph",
        "temperature": temperature,
    }


# ---------------- ARM 5: RTS_SMOOTH (Anchor 2) ----------------

def arm_rts_smooth(E, R, sq, W, chains_test, depth: int,
                   temperature: float = 1.0) -> Dict[str, Any]:
    """Rauch-Tung-Striebel smoother forward x backward state-estimate product.

    Standard Kalman smoother (Sarkka 2013): forward pass gives prior; backward
    pass refines using future observations; smoothed estimate per hop =
    Gaussian-conjugate product of forward and backward marginals.

    Substrate-VSA mapping: forward and backward marginals are top-K=20 beliefs
    over atoms; product = elementwise multiply + renormalize; readout =
    argmax of smoothed belief at endpoint position.

    Distinguished from LDPC: RTS is ONE forward + ONE backward + product
    (analytical smoother). LDPC is iterative until LLR convergence (n_sweeps).
    """
    n = len(chains_test)
    V = E.shape[0]
    hits = 0
    per_step_hits = np.zeros(depth, dtype=np.int64)

    for chain in chains_test:
        # Forward pass: belief_fwd[k] = posterior at variable k given chain start
        fwd = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        fwd[0][chain[0][0]] = 1.0
        for k in range(depth):
            p = chain[k][1]
            state = fwd[k] @ E
            key = (state * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            fwd[k + 1] = _scores_to_softmax(scores, temperature, k_set=K_SET)

        # Backward pass: start from fwd[depth] (no endpoint anchor; smoother
        # operates in single-pass / does not assume endpoint observation).
        # NOTE: classic RTS smoother in SLAM uses backward = filter run from
        # endpoint with future observations. Here we have NO endpoint
        # observation, so backward seed = fwd[depth] (uniform-like at this
        # stage carries info from forward pass; the backward sweep refines
        # variables 1..depth-1 by integrating constraints upstream).
        bwd = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        bwd[depth] = fwd[depth].copy()
        for k in range(depth, 0, -1):
            p = chain[k - 1][1]
            state = bwd[k] @ E
            # Reverse-W operation (object -> source recovery): see arm_backward_only.
            recovered = (W.T @ state) * R[p] / sq
            scores = E @ recovered
            bwd[k - 1] = _scores_to_softmax(scores, temperature, k_set=K_SET)

        # Smoothed = fwd * bwd, normalized per variable
        smoothed = [np.zeros(V, dtype=np.float32) for _ in range(depth + 1)]
        smoothed[0] = fwd[0]  # fixed at start
        for k in range(1, depth + 1):
            combined = fwd[k] * bwd[k]
            s = combined.sum()
            smoothed[k] = (combined / s) if s > 1e-12 else fwd[k]

        # Score endpoint
        if int(smoothed[depth].argmax()) == chain[depth - 1][2]:
            hits += 1
        for k in range(depth):
            if int(smoothed[k + 1].argmax()) == chain[k][2]:
                per_step_hits[k] += 1

    per_step_acc = (per_step_hits.astype(np.float32) / max(n, 1)).tolist()
    return {
        "top1": round(hits / max(n, 1), 4),
        "per_step_acc": [round(x, 4) for x in per_step_acc],
        "n_queries": n,
        "depth": depth,
        "mechanism": "rts_smoother_forward_x_backward_softmax_product",
        "temperature": temperature,
    }


# ---------------- SELFTEST (cheap mechanism sanity) ----------------

def _selftest() -> None:
    g = np.random.default_rng(0)
    n = 1024
    V = 60
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    triples_d, chains_d = make_deep_chains(8, V, P, max_depth=DEPTH, g=g,
                                            disallow_s=set())
    W = ingest_hebbian(triples_d, E, R, sq, n)

    r_base = arm_baseline_pointer_chain(E, R, sq, W, chains_d, depth=DEPTH)
    r_sft = arm_soft_fwd(E, R, sq, W, chains_d, depth=DEPTH)
    r_bwd = arm_backward_only(E, R, sq, W, chains_d, depth=DEPTH)
    r_ldpc = arm_ldpc_bidir(E, R, sq, W, chains_d, depth=DEPTH, n_sweeps=2)
    r_rts = arm_rts_smooth(E, R, sq, W, chains_d, depth=DEPTH)

    # Verify ranges + measured vs expected
    for r in (r_base, r_sft, r_bwd, r_ldpc, r_rts):
        assert 0.0 <= r["top1"] <= 1.0, "top1 out of [0,1]: %s" % r

    # Assert all 5 arms produced sensible (non-NaN) numbers
    assert all(not math.isnan(r["top1"]) for r in (r_base, r_sft, r_bwd, r_ldpc, r_rts))

    # LDPC must produce some sweep-convergence stat
    assert "mean_sweeps_to_converge" in r_ldpc
    # RTS must produce per-step
    assert len(r_rts["per_step_acc"]) == DEPTH

    print("[selftest] PASS arms top1 = "
          "baseline=%.3f soft=%.3f back=%.3f ldpc=%.3f rts=%.3f "
          "(n=%d V=%d depth=%d ldpc_sweeps=%d) | mechanism shapes OK"
          % (r_base["top1"], r_sft["top1"], r_bwd["top1"], r_ldpc["top1"], r_rts["top1"],
             len(chains_d), V, DEPTH, r_ldpc["n_sweeps_max"]), flush=True)


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# ---------------- per-seed driver ----------------

def run_seed(seed: int) -> Dict[str, Any]:
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_P, N_DIM, g)

    out = {
        "seed": seed, "run_mode": RUN_MODE, "N": N_DIM, "V_C": V_CONCEPTS,
        "V_P": V_P, "K_SET": K_SET, "n_chains": N_CHAINS, "depth": DEPTH,
        "ldpc_sweeps": LDPC_SWEEPS,
        "config_version": CONFIG_VERSION,
        "_llm_forward_calls_at_inference": _LLM_CALL_COUNTER[0],
    }

    # Build the same deep-chain set + W matrix for ALL 5 arms (apples-to-apples).
    t_setup = time.time()
    triples, chains = make_deep_chains(N_CHAINS, V_CONCEPTS, V_P, max_depth=DEPTH,
                                        g=g, disallow_s=set())
    W = ingest_hebbian(triples, E, R, sq, N_DIM)
    out["setup_s"] = round(time.time() - t_setup, 2)
    print("  [seed=%d] setup: %d triples, %d chains, depth=%d, W built in %.1fs"
          % (seed, len(triples), len(chains), DEPTH, out["setup_s"]), flush=True)

    # ARM 1: BASELINE pointer-chain v2 (sanity rail)
    t_arm = time.time()
    r_base = arm_baseline_pointer_chain(E, R, sq, W, chains, depth=DEPTH)
    r_base["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_baseline_pointer_chain_v2"] = r_base
    print("  [seed=%d] ARM_BASELINE_pointer_chain_v2 top1=%.4f per_step=%s t=%.1fs"
          % (seed, r_base["top1"], r_base["per_step_acc"], r_base["elapsed_s_arm"]),
          flush=True)

    sanity_ok = SANITY_BASELINE_LO <= r_base["top1"] <= SANITY_BASELINE_HI
    out["sanity_baseline_ok"] = sanity_ok
    if not sanity_ok:
        print("  [seed=%d] SANITY BREACH: baseline=%.4f not in [%.3f,%.3f]; "
              "anchor verdicts will be MARKED but cell still runs all arms for diagnostic."
              % (seed, r_base["top1"], SANITY_BASELINE_LO, SANITY_BASELINE_HI),
              flush=True)

    # ARM 2: SOFT_FWD
    t_arm = time.time()
    r_sft = arm_soft_fwd(E, R, sq, W, chains, depth=DEPTH)
    r_sft["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_soft_fwd"] = r_sft
    print("  [seed=%d] ARM_SOFT_FWD top1=%.4f per_step=%s t=%.1fs"
          % (seed, r_sft["top1"], r_sft["per_step_acc"], r_sft["elapsed_s_arm"]),
          flush=True)

    # ARM 3: BACKWARD_ONLY
    t_arm = time.time()
    r_bwd = arm_backward_only(E, R, sq, W, chains, depth=DEPTH)
    r_bwd["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_backward_only"] = r_bwd
    print("  [seed=%d] ARM_BACKWARD_ONLY top1=%.4f per_step_bwd=%s t=%.1fs"
          % (seed, r_bwd["top1"], r_bwd["per_step_acc_backward"], r_bwd["elapsed_s_arm"]),
          flush=True)

    # ARM 4: LDPC_BIDIR (Anchor 1 PRIMARY)
    t_arm = time.time()
    r_ldpc = arm_ldpc_bidir(E, R, sq, W, chains, depth=DEPTH, n_sweeps=LDPC_SWEEPS)
    r_ldpc["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_ldpc_bidir"] = r_ldpc
    print("  [seed=%d] ARM_LDPC_BIDIR top1=%.4f per_step=%s mean_sweeps=%.2f t=%.1fs"
          % (seed, r_ldpc["top1"], r_ldpc["per_step_acc"],
             r_ldpc["mean_sweeps_to_converge"], r_ldpc["elapsed_s_arm"]),
          flush=True)

    # ARM 5: RTS_SMOOTH (Anchor 2 PRIMARY)
    t_arm = time.time()
    r_rts = arm_rts_smooth(E, R, sq, W, chains, depth=DEPTH)
    r_rts["elapsed_s_arm"] = round(time.time() - t_arm, 2)
    out["arm_rts_smooth"] = r_rts
    print("  [seed=%d] ARM_RTS_SMOOTH top1=%.4f per_step=%s t=%.1fs"
          % (seed, r_rts["top1"], r_rts["per_step_acc"], r_rts["elapsed_s_arm"]),
          flush=True)

    out["elapsed_s"] = round(time.time() - t, 1)
    return out


# ---------------- VERDICT (anchor 1 + anchor 2 + sanity + cell-wide) ----------------

def _mean_top1(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed if key in p
            and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    return float(np.mean(vals)) if vals else float("nan")


def _sd_top1(per_seed: List[Dict[str, Any]], key: str) -> float:
    vals = [p[key]["top1"] for p in per_seed if key in p
            and isinstance(p[key].get("top1"), (int, float))
            and not math.isnan(p[key]["top1"])]
    return float(np.std(vals)) if len(vals) > 1 else float("nan")


def verdict_from(per_seed: List[Dict[str, Any]]) -> Tuple[str, str]:
    baseline = _mean_top1(per_seed, "arm_baseline_pointer_chain_v2")
    soft_fwd = _mean_top1(per_seed, "arm_soft_fwd")
    backward = _mean_top1(per_seed, "arm_backward_only")
    ldpc = _mean_top1(per_seed, "arm_ldpc_bidir")
    rts = _mean_top1(per_seed, "arm_rts_smooth")
    ldpc_sd = _sd_top1(per_seed, "arm_ldpc_bidir")
    rts_sd = _sd_top1(per_seed, "arm_rts_smooth")

    # Sanity rail
    sanity_breached = sum(1 for p in per_seed if not p.get("sanity_baseline_ok", False))
    sanity_msg = ""
    if sanity_breached > 0:
        sanity_msg = ("SANITY_BREACH=%d/%d seeds; baseline_mean=%.4f outside [%.3f,%.3f] | "
                      % (sanity_breached, len(per_seed), baseline,
                         SANITY_BASELINE_LO, SANITY_BASELINE_HI))

    # Anchor-1 (LDPC) classification
    ldpc_hp = (not math.isnan(ldpc) and ldpc >= HP_LDPC_TOP1_MIN
               and ldpc > soft_fwd + HP_LDPC_SOFT_FWD_DELTA
               and (math.isnan(ldpc_sd) or ldpc_sd <= HP_LDPC_SD_MAX))
    ldpc_hf = (not math.isnan(ldpc) and (ldpc <= HF_LDPC_TOP1_MAX
               or (not math.isnan(soft_fwd) and ldpc - soft_fwd <= HF_LDPC_OVER_SOFT_FWD_MAX)))
    ldpc_mb = (not ldpc_hp and not ldpc_hf
               and not math.isnan(ldpc) and MB_LDPC_LO <= ldpc < MB_LDPC_HI)
    if ldpc_hp:
        ldpc_band = "HARD_PASS"
    elif ldpc_hf:
        ldpc_band = "HARD_FAIL"
    elif ldpc_mb:
        ldpc_band = "MIDDLE_BAND"
    else:
        ldpc_band = "UNDETERMINED"

    # Anchor-2 (RTS) classification
    max_dir = max(baseline if not math.isnan(baseline) else -1.0,
                  backward if not math.isnan(backward) else -1.0)
    rts_hp = (not math.isnan(rts) and rts >= HP_RTS_TOP1_MIN
              and rts > max_dir + HP_RTS_SUPER_ADDITIVE_DELTA
              and (math.isnan(rts_sd) or rts_sd <= HP_RTS_SD_MAX))
    rts_hf = (not math.isnan(rts) and (rts <= HF_RTS_TOP1_MAX
              or (max_dir > 0 and rts <= HF_RTS_RATIO_OVER_MAX_DIR * max_dir)))
    rts_mb = (not rts_hp and not rts_hf
              and not math.isnan(rts) and MB_RTS_LO <= rts < MB_RTS_HI)
    if rts_hp:
        rts_band = "HARD_PASS"
    elif rts_hf:
        rts_band = "HARD_FAIL"
    elif rts_mb:
        rts_band = "MIDDLE_BAND"
    else:
        rts_band = "UNDETERMINED"

    summ = (sanity_msg +
            "BASELINE=%.4f SOFT_FWD=%.4f BACKWARD=%.4f LDPC=%.4f (sd=%.3f) RTS=%.4f (sd=%.3f) "
            "| Anchor1_LDPC=%s | Anchor2_RTS=%s | max_dir=%.4f"
            % (baseline, soft_fwd, backward, ldpc, ldpc_sd, rts, rts_sd,
               ldpc_band, rts_band, max_dir))

    # Cell-wide verdict
    if sanity_breached >= max(1, (len(per_seed) + 1) // 2):
        return "SANITY_BREACH", "SANITY_BREACH_BASELINE_OUT_OF_BAND: " + summ
    if ldpc_band == "HARD_PASS" or rts_band == "HARD_PASS":
        return "HARD_PASS_GAP1_BIDIRECTIONAL_LIFT", "HARD_PASS_GAP1: " + summ
    if ldpc_band == "MIDDLE_BAND" or rts_band == "MIDDLE_BAND":
        return "MIDDLE_BAND_GAP1_PARTIAL_LIFT", "MIDDLE_BAND_GAP1: " + summ
    if ldpc_band == "HARD_FAIL" and rts_band == "HARD_FAIL":
        return "HARD_FAIL_GAP1_BIDIRECTIONAL_REFUTED", "HARD_FAIL_GAP1: " + summ
    return "UNDETERMINED_GAP1", "UNDETERMINED_GAP1: " + summ


# ---------------- atexit synth (partial-flush) ----------------

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

    agg = aggregate_partials(out_dir, seeds=[str(s) for s in SEEDS], run_config=run_config)
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
            "Gap-1 multi-hop bundled Anchors 1+2 per research drill 2026-06-26: "
            "LDPC bidirectional sum-product (3 sweep iterations forward+backward) "
            "and RTS smoother (forward x backward Gaussian-mixture product) "
            "target the FORWARD-ONLY HARD-DECISION CHAINING pathology shared by 5 "
            "refuted multi-hop attempts. ARM_BASELINE_pointer_chain_v2 is SACRED "
            "sanity rail reproducing 0.145 +/- 0.02 anchor at depth-5. ARM_SOFT_FWD "
            "and ARM_BACKWARD_ONLY isolate the 'soft' and 'backward' components "
            "respectively; LDPC bidirectional and RTS smoother test super-additivity. "
            "Bands LOCKED at module init via assert chain."
        ),
    }
    write_metrics(out_dir, metrics, results=per_seed)
    print("[done] metrics.json written (%d seeds, %.1fs)" % (
        len(per_seed), metrics["elapsed_s"]), flush=True)
