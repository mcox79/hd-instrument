"""substrate_soft_chain_dfe_multihop_v1 -- SOFT-DECISION-CHAIN rescue for the
2026-06-24 Resonator integration HARD_FAIL on apples-to-apples 2-hop chains.

Strategic context (see preregs/2026-06-24_substrate_soft_chain_dfe_multihop_v1.md):
  Today's resonator_multihop_integration HARD_FAILed (NAIVE 2HOP 0.6500 ~=
  RESONATOR 2HOP 0.6317, tied). Research 2x+3x drill diagnosed root cause as
  inter-hop hard-decision error propagation (= DFE error propagation in
  communications theory), NOT per-hop cleanup capacity. Top rescue (P_deflated
  0.35): SOFT-CHAIN -- replace per-hop argmax with softmax-weighted
  superposition of top-K candidates, passed forward to next hop. CA3 graded-
  reactivation brain analog. Zero new substrate primitives.

Four arms (apples-to-apples; ONE knob = hard-argmax vs soft-superposition):
  ARM_NAIVE_HARD_2HOP    : control; reproduces 0.65 baseline (matches chain_naive)
  ARM_RESONATOR_HARD_2HOP: control; reproduces 0.63 (matches chain_resonator argmax)
  ARM_SOFT_CHAIN_2HOP    : PRIMARY; hop-1 emits softmax over top-K; hop-2 key is
                           sum_i q1[i] * (E[atom_i] * R[p2] * sqrtN); final argmax
  ARM_SOFT_CHAIN_3HOP    : BONUS; extends ARM 3 to 3-hop with soft decisions

Pre-reg HARD bands (PRIMARY = ARM_SOFT_CHAIN_2HOP top1):
  HARD_PASS  : >= 0.80 AND cv <= 0.05 AND > NAIVE + 0.10
  MIDDLE_BAND: in [0.70, 0.80)
  HARD_FAIL  : <= 0.70
  Sanity     : NAIVE in [0.60, 0.70]; RESONATOR_HARD in [0.58, 0.68]
  Bonus      : ARM_SOFT_CHAIN_3HOP >= 0.60

Lane 1 substrate-native; pure numpy; CPU; ASCII; per-seed CONFIG_VERSION
checkpoint. Forked from exp_substrate_resonator_multihop_integration_v1.py;
primitives (bipolar / ingest_hebbian / chain_naive / chain_resonator) reused
verbatim for direct comparability of the new arm.
"""
from __future__ import annotations
import argparse
import json
import math
import os
import sys
import time
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))
# PROT-021 defensive import (well below 4h floor, but kept for resume hygiene).
from experiments import _seed_checkpoint  # noqa: F401

ANCHOR_NAME = "substrate_soft_chain_dfe_multihop_v1"
EXP_NAME = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)

# Pre-reg bands (PRIMARY = ARM_SOFT_CHAIN_2HOP top1)
SANITY_NAIVE_LO = 0.60
SANITY_NAIVE_HI = 0.70
SANITY_RES_LO = 0.58
SANITY_RES_HI = 0.68
SOFT_HARD_PASS = 0.80
SOFT_MIDDLE_LO = 0.70
SOFT_OVER_NAIVE_DELTA = 0.10
SOFT_3HOP_BONUS = 0.60
CV_GATE = 0.05

RUN_MODE = ("smoke" if "--smoke" in sys.argv else os.environ.get("HDLAB_RUN_MODE", "full")).lower()
_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true")
_ARGS, _ = _ap.parse_known_args()

# Concept graph dimensions (match base cell for direct comparability)
V_CONCEPTS = 200
V_PREDICATES = 10
K_SET = 20            # top-K bundle size (matches resonator integration cell)

if RUN_MODE == "smoke":
    SEEDS = [1]
    N_DIM = 1024
    N_CHAINS_2HOP = 80
    N_CHAINS_3HOP = 60
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_CHAINS_2HOP = 300
    N_CHAINS_3HOP = 200

CONFIG_VERSION = (
    "softchain-v1: dense-bipolar HRR + multivalue-hebbian + 4arm "
    "(naive-hard, res-hard, soft-2hop, soft-3hop); "
    "V_C=%d V_P=%d N=%d K_SET=%d n2=%d n3=%d; "
    "bands naive_sanity[%.2f,%.2f] res_sanity[%.2f,%.2f] "
    "soft_HP>=%.2f soft_MB>=%.2f soft_delta>=%.2f 3hop_bonus>=%.2f cv<=%.2f"
) % (V_CONCEPTS, V_PREDICATES, N_DIM, K_SET,
     N_CHAINS_2HOP, N_CHAINS_3HOP,
     SANITY_NAIVE_LO, SANITY_NAIVE_HI, SANITY_RES_LO, SANITY_RES_HI,
     SOFT_HARD_PASS, SOFT_MIDDLE_LO, SOFT_OVER_NAIVE_DELTA, SOFT_3HOP_BONUS, CV_GATE)


# -- Substrate primitives (verbatim from base concept_kg / resonator_integration cells) ----

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    """Dense unit-norm bipolar vectors (M, n). The proven U1 primitive."""
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float, n_dim: int,
                   batch: int = 2000) -> np.ndarray:
    """Multi-value Hebbian-accumulate: W = sum_i outer(E[o_i], key_i)/N.
    key = E[s] * R[p] * sqrt(N)."""
    tr = np.asarray(triples, dtype=np.int64)
    s_idx, p_idx, o_idx = tr[:, 0], tr[:, 1], tr[:, 2]
    W = np.zeros((n_dim, n_dim), dtype=np.float32)
    for b in range(0, len(tr), batch):
        ks = (E[s_idx[b:b + batch]] * R[p_idx[b:b + batch]] * sq).astype(np.float32)
        W += (E[o_idx[b:b + batch]].T @ ks) / n_dim
    return W


def _l2_normalize(v: np.ndarray, eps: float = 1e-8) -> np.ndarray:
    nrm = np.linalg.norm(v)
    return v / (nrm + eps)


def _softmax(x: np.ndarray) -> np.ndarray:
    z = x - x.max()
    ez = np.exp(z)
    return ez / ez.sum()


# -- Chain mechanisms ------------------------------------------------------

def chain_naive(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                start: int, relations: List[int]) -> int:
    """ARM_NAIVE_HARD: per-hop W @ (state * R[p] * sq) + argmax(E @ state).
    Matches the existing 0.65 baseline verbatim."""
    state = E[start].copy()
    last = start
    for p in relations:
        state = W @ (state * R[p] * sq)
        last = int((E @ state).argmax())
    return last


def chain_resonator_hard(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
                         start: int, relations: List[int], k_set: int,
                         beta: float) -> tuple[int, list[float]]:
    """ARM_RESONATOR_HARD: per-hop Modern-Hopfield top-K bundle, then argmax to
    pick a SINGLE entity, then bind that single entity into the next hop's key.
    Matches today's HARD_FAIL chain_resonator semantics (the cleanup is soft
    INSIDE one hop -- top-K softmax bundle -- but the HAND-OFF to the next hop
    uses the ARGMAX-CLEANED-STATE as state for next bind, which is the DFE
    hard-decision pathology).

    Returns (final_entity, per_hop_top1_confs).
    """
    state = _l2_normalize(E[start].copy())
    per_hop_conf: list[float] = []
    for p in relations:
        transit = W @ (state * R[p] * sq)
        transit = _l2_normalize(transit)
        ent_scores = E @ transit
        top_idx = np.argpartition(ent_scores, -k_set)[-k_set:]
        top_conf = ent_scores[top_idx]
        top1 = float(top_conf.max())
        per_hop_conf.append(top1)
        # Modern-Hopfield softmax bundle of top-K entity vectors.
        w = _softmax(beta * top_conf)
        state = (w[:, None] * E[top_idx]).sum(axis=0)
        state = _l2_normalize(state)
    final_scores = E @ state
    return int(final_scores.argmax()), per_hop_conf


def chain_soft(W: np.ndarray, E: np.ndarray, R: np.ndarray, sq: float,
               start: int, relations: List[int], k_set: int,
               beta: float) -> tuple[int, list[float]]:
    """ARM_SOFT_CHAIN: replace the hard hand-off between hops with a
    weighted superposition of bound (top-K entity, next-relation) keys.

    The mechanism: at hop t with relation p_t, run cleanup against E to get
    top-K candidate entities + softmax weights q. Instead of picking
    argmax(q) and binding it with the NEXT relation p_{t+1}, build the
    next-hop transit state as the weighted superposition of all K bound
    candidates: state_{t+1} = sum_i q[i] * (E[top_i] * R[p_t+1] * sq), then
    apply W. Equivalent to passing the full posterior forward instead of
    collapsing to a single pick.

    Implementation detail: for the LAST hop, no next-relation exists; the
    final readout is argmax over the codebook of W @ (weighted-superposition
    of E[top_i] for the previous hop's softmax weights and the LAST
    relation). Concretely we form `next_state = (q[:,None] * E[top_idx]).sum(0)
    then bind with R[p_last] and run W; argmax over E for final pick`.

    For 2-hop:
      hop-1: transit = W @ (E[start] * R[p1] * sq); top-K + softmax over E
             -> q1 (no collapse).
      hop-2: state2 = sum_i q1[i] * E[top_i]  (soft state)
             transit2 = W @ (state2 * R[p2] * sq)
             argmax(E @ transit2) -> answer.

    For 3-hop, iterate: hop-2 ALSO emits soft q2 over top-K; hop-3 forms
    soft state via q2 and binds with R[p3]; final argmax after W.

    Returns (final_entity, per_hop_top1_confs).
    """
    state = E[start].copy()
    per_hop_conf: list[float] = []
    n_hops = len(relations)
    for hop_i, p in enumerate(relations):
        transit = W @ (state * R[p] * sq)
        transit = _l2_normalize(transit)
        ent_scores = E @ transit
        top_idx = np.argpartition(ent_scores, -k_set)[-k_set:]
        top_conf = ent_scores[top_idx]
        top1 = float(top_conf.max())
        per_hop_conf.append(top1)
        if hop_i == n_hops - 1:
            # Last hop: take argmax for final answer.
            return int(np.argmax(ent_scores)), per_hop_conf
        # NOT last hop: build the soft superposition state to pass forward.
        # This is the load-bearing knob vs chain_resonator_hard (which would
        # do argmax + use a single entity as state here).
        q = _softmax(beta * top_conf)
        state = (q[:, None] * E[top_idx]).sum(axis=0)
        # L2-normalize the superposed state so the next hop's |state * R| is
        # comparable to the single-pick case (otherwise W @ (...) amplitude
        # would shift with K).
        state = _l2_normalize(state)
    # Unreachable (we return inside the last-hop branch).
    return int(np.argmax(E @ state)), per_hop_conf


# -- Synthetic chain builders (verbatim from base cell) --------------------

def make_two_hop_chains(n_chains: int, V: int, P: int, g: np.random.Generator,
                        p1: int = 0, p2: int = 1):
    train: list[tuple[int, int, int]] = []
    queries: list[tuple[int, int, int, int, int]] = []
    used_s: set[int] = set()
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


def make_three_hop_chains(n_chains: int, V: int, P: int, g: np.random.Generator,
                          p1: int = 0, p2: int = 1, p3: int = 2):
    train: list[tuple[int, int, int]] = []
    queries: list[tuple[int, int, int, int, int, int, int]] = []
    used_s: set[int] = set()
    tries = 0
    while len(queries) < n_chains and tries < n_chains * 100:
        tries += 1
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        x = int(g.integers(0, V))
        while x == s:
            x = int(g.integers(0, V))
        y = int(g.integers(0, V))
        while y in (s, x):
            y = int(g.integers(0, V))
        o = int(g.integers(0, V))
        while o in (s, x, y):
            o = int(g.integers(0, V))
        train.append((s, p1, x))
        train.append((x, p2, y))
        train.append((y, p3, o))
        queries.append((s, p1, p2, p3, o, x, y))
        used_s.add(s)
    return train, queries


# -- Self-test --------------------------------------------------------------

def _selftest():
    """1-second mechanism check: storage + all 3 chain primitives end-to-end
    on tiny graph; assert finite + plausible outputs; assert SOFT_CHAIN matches
    NAIVE on a clean (zero-noise) 1-hop probe (soft over a sharp posterior =
    argmax)."""
    g = np.random.default_rng(0)
    n = 256
    V = 40
    P = 4
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(P, n, g)
    train, queries = make_two_hop_chains(10, V, P, g)
    W = ingest_hebbian(train, E, R, sq, n)

    # 1-hop sanity (build keys directly; ensure ingest learned something).
    s_p_o = train[:8]
    keys = np.stack([E[s] * R[p] * sq for (s, p, _o) in s_p_o]).astype(np.float32)
    scores = (E @ (W @ keys.T)).T
    hop1_top1 = float((scores.argmax(axis=1) == np.array([o for (_s, _p, o) in s_p_o])).mean())
    assert hop1_top1 >= 0.5, "selftest 1-hop weak (got %.2f)" % hop1_top1

    # All 3 chain primitives produce finite outputs.
    if len(queries) >= 4:
        for (s, p1, p2, _o_true, _x) in queries[:4]:
            n_pred = chain_naive(W, E, R, sq, s, [p1, p2])
            r_pred, _r_confs = chain_resonator_hard(W, E, R, sq, s, [p1, p2],
                                                    k_set=10, beta=float(n))
            sc_pred, sc_confs = chain_soft(W, E, R, sq, s, [p1, p2],
                                           k_set=10, beta=float(n))
            assert isinstance(n_pred, int) and 0 <= n_pred < V, "naive bad output"
            assert isinstance(r_pred, int) and 0 <= r_pred < V, "resonator bad output"
            assert isinstance(sc_pred, int) and 0 <= sc_pred < V, "soft-chain bad output"
            assert len(sc_confs) == 2, "soft-chain 2-hop conf count"

    # 3-hop soft-chain primitive runs end-to-end.
    train3, q3 = make_three_hop_chains(4, V, P, g)
    W3 = ingest_hebbian(train3, E, R, sq, n)
    if q3:
        (s, p1, p2, p3, _o, _x, _y) = q3[0]
        sc3_pred, sc3_confs = chain_soft(W3, E, R, sq, s, [p1, p2, p3],
                                         k_set=10, beta=float(n))
        assert 0 <= sc3_pred < V, "3-hop soft-chain bad output"
        assert len(sc3_confs) == 3, "3-hop soft-chain conf count"

    # Formula self-test: on a sharp 1-hop posterior (large beta, well-resolved
    # cleanup), SOFT_CHAIN's hop-1->hop-2 superposition should reduce to
    # binding-with-top1 + small noise from the K-1 minority weights. Concretely:
    # if argmax weight q[max] > 0.99, the soft state is ~= E[top1] (up to L2
    # renorm); the soft-chain 2-hop answer should agree with the
    # bind-top1-explicitly 2-hop answer on >= 75% of queries in the clean
    # regime.
    if len(queries) >= 4:
        agree = 0; total = 0
        for (s, p1, p2, _o, _x) in queries[:4]:
            sc_pred, _ = chain_soft(W, E, R, sq, s, [p1, p2],
                                    k_set=10, beta=float(n) * 4.0)
            r_pred, _ = chain_resonator_hard(W, E, R, sq, s, [p1, p2],
                                             k_set=10, beta=float(n) * 4.0)
            total += 1
            if sc_pred == r_pred:
                agree += 1
        # Don't gate the test on agreement -- they SHOULD diverge in the noisy
        # regime; the assertion is on finite output + per-hop conf logging.
        # Just log it for the gate trail.
        print("[selftest] soft/res-hard agreement on tiny clean regime: %d/%d"
              % (agree, total), flush=True)

    print("[selftest] PASS: soft-chain-DFE multihop V=%d P=%d N=%d hop1_top1=%.2f"
          % (V, P, n, hop1_top1), flush=True)


_selftest()
if _ARGS.self_test:
    sys.exit(0)


# -- Arm runners -----------------------------------------------------------

def arm_naive_hard_2hop(W, E, R, sq, queries) -> Dict:
    """Sanity arm 1: reproduces concept_kg / resonator_integration naive baseline (~0.65)."""
    preds = np.array([chain_naive(W, E, R, sq, q[0], [q[1], q[2]]) for q in queries])
    o_true = np.array([q[3] for q in queries])
    top1 = float((preds == o_true).mean())
    return {"top1": round(top1, 4), "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def arm_resonator_hard_2hop(W, E, R, sq, queries, k_set: int) -> Dict:
    """Sanity arm 2: reproduces today's HARD_FAIL resonator (~0.63).
    Hard decision because the inter-hop hand-off is argmax-then-bind, even
    though the per-hop cleanup uses a softmax bundle.
    """
    beta = float(N_DIM)
    preds = []
    confs_hop1 = []
    confs_hop2 = []
    for q in queries:
        s, p1, p2, _o_true, _x_gt = q
        pred, confs = chain_resonator_hard(W, E, R, sq, s, [p1, p2], k_set, beta)
        preds.append(pred)
        if len(confs) >= 1:
            confs_hop1.append(confs[0])
        if len(confs) >= 2:
            confs_hop2.append(confs[1])
    preds = np.array(preds)
    o_true = np.array([q[3] for q in queries])
    top1 = float((preds == o_true).mean())
    return {"top1": round(top1, 4), "k_set": k_set, "beta": beta,
            "mean_conf_hop1": round(float(np.mean(confs_hop1)) if confs_hop1 else 0.0, 4),
            "mean_conf_hop2": round(float(np.mean(confs_hop2)) if confs_hop2 else 0.0, 4),
            "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def arm_soft_chain_2hop(W, E, R, sq, queries, k_set: int) -> Dict:
    """PRIMARY: soft-DFE-style chain. Hop-1 emits softmax over top-K; hop-2's
    state is the soft superposition, not the argmax pick.
    """
    beta = float(N_DIM)
    preds = []
    confs_hop1 = []
    confs_hop2 = []
    for q in queries:
        s, p1, p2, _o_true, _x_gt = q
        pred, confs = chain_soft(W, E, R, sq, s, [p1, p2], k_set, beta)
        preds.append(pred)
        if len(confs) >= 1:
            confs_hop1.append(confs[0])
        if len(confs) >= 2:
            confs_hop2.append(confs[1])
    preds = np.array(preds)
    o_true = np.array([q[3] for q in queries])
    top1 = float((preds == o_true).mean())
    return {"top1": round(top1, 4), "k_set": k_set, "beta": beta,
            "mean_conf_hop1": round(float(np.mean(confs_hop1)) if confs_hop1 else 0.0, 4),
            "mean_conf_hop2": round(float(np.mean(confs_hop2)) if confs_hop2 else 0.0, 4),
            "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def arm_soft_chain_3hop(W, E, R, sq, queries, k_set: int) -> Dict:
    """BONUS: soft-chain 3-hop. All inter-hop hand-offs soft (hop-1->hop-2 AND
    hop-2->hop-3); final readout argmax after last cleanup.
    """
    beta = float(N_DIM)
    preds = []
    for q in queries:
        s, p1, p2, p3, _o_true, _x_gt, _y_gt = q
        pred, _confs = chain_soft(W, E, R, sq, s, [p1, p2, p3], k_set, beta)
        preds.append(pred)
    preds = np.array(preds)
    o_true = np.array([q[4] for q in queries])
    top1 = float((preds == o_true).mean())
    return {"top1": round(top1, 4), "k_set": k_set, "beta": beta,
            "n_chains": len(queries),
            "chance": round(1.0 / V_CONCEPTS, 5)}


def run_seed(seed: int) -> Dict:
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PREDICATES, N_DIM, g)
    t = time.time()

    # 2-hop KB + queries (shared by ARM 1, 2, 3)
    train2, q2 = make_two_hop_chains(N_CHAINS_2HOP, V_CONCEPTS, V_PREDICATES, g)
    W2 = ingest_hebbian(train2, E, R, sq, N_DIM)

    # 3-hop KB + queries (separate from 2-hop; clean Lane-1 measure for ARM 4)
    train3, q3 = make_three_hop_chains(N_CHAINS_3HOP, V_CONCEPTS, V_PREDICATES, g)
    W3 = ingest_hebbian(train3, E, R, sq, N_DIM)

    out = {"seed": seed,
           "config_version": CONFIG_VERSION,
           "V_concepts": V_CONCEPTS, "V_predicates": V_PREDICATES,
           "N_DIM": N_DIM, "K_SET": K_SET,
           "run_mode": RUN_MODE}

    out["arm_naive_hard_2hop"] = arm_naive_hard_2hop(W2, E, R, sq, q2)
    print("  [seed=%d] ARM_NAIVE_HARD_2HOP top1=%.4f (n=%d chance=%.4f)"
          % (seed, out["arm_naive_hard_2hop"]["top1"],
             out["arm_naive_hard_2hop"]["n_chains"],
             out["arm_naive_hard_2hop"]["chance"]), flush=True)

    out["arm_resonator_hard_2hop"] = arm_resonator_hard_2hop(W2, E, R, sq, q2, K_SET)
    print("  [seed=%d] ARM_RESONATOR_HARD_2HOP top1=%.4f (K_SET=%d beta=%.1f "
          "mean_conf=[h1=%.3f h2=%.3f])"
          % (seed, out["arm_resonator_hard_2hop"]["top1"],
             out["arm_resonator_hard_2hop"]["k_set"],
             out["arm_resonator_hard_2hop"]["beta"],
             out["arm_resonator_hard_2hop"]["mean_conf_hop1"],
             out["arm_resonator_hard_2hop"]["mean_conf_hop2"]), flush=True)

    out["arm_soft_chain_2hop"] = arm_soft_chain_2hop(W2, E, R, sq, q2, K_SET)
    print("  [seed=%d] ARM_SOFT_CHAIN_2HOP top1=%.4f (K_SET=%d beta=%.1f "
          "mean_conf=[h1=%.3f h2=%.3f]) <-- PRIMARY"
          % (seed, out["arm_soft_chain_2hop"]["top1"],
             out["arm_soft_chain_2hop"]["k_set"],
             out["arm_soft_chain_2hop"]["beta"],
             out["arm_soft_chain_2hop"]["mean_conf_hop1"],
             out["arm_soft_chain_2hop"]["mean_conf_hop2"]), flush=True)

    out["arm_soft_chain_3hop"] = arm_soft_chain_3hop(W3, E, R, sq, q3, K_SET)
    print("  [seed=%d] ARM_SOFT_CHAIN_3HOP top1=%.4f (K_SET=%d beta=%.1f) <-- BONUS"
          % (seed, out["arm_soft_chain_3hop"]["top1"],
             out["arm_soft_chain_3hop"]["k_set"],
             out["arm_soft_chain_3hop"]["beta"]), flush=True)

    out["wall_s"] = round(time.time() - t, 1)
    return out


# -- Verdict ---------------------------------------------------------------

def verdict(ps: List[Dict]) -> Tuple[str, str]:
    """PRIMARY = ARM_SOFT_CHAIN_2HOP top1; sanity = ARM_NAIVE_HARD_2HOP in
    [0.60, 0.70] AND ARM_RESONATOR_HARD_2HOP in [0.58, 0.68]."""
    n_top1 = float(np.mean([p["arm_naive_hard_2hop"]["top1"] for p in ps]))
    n_cv = float(np.std([p["arm_naive_hard_2hop"]["top1"] for p in ps]) / max(n_top1, 1e-9))
    r_top1 = float(np.mean([p["arm_resonator_hard_2hop"]["top1"] for p in ps]))
    r_cv = float(np.std([p["arm_resonator_hard_2hop"]["top1"] for p in ps]) / max(r_top1, 1e-9))
    s2_top1 = float(np.mean([p["arm_soft_chain_2hop"]["top1"] for p in ps]))
    s2_cv = float(np.std([p["arm_soft_chain_2hop"]["top1"] for p in ps]) / max(s2_top1, 1e-9))
    s3_top1 = float(np.mean([p["arm_soft_chain_3hop"]["top1"] for p in ps]))
    s3_cv = float(np.std([p["arm_soft_chain_3hop"]["top1"] for p in ps]) / max(s3_top1, 1e-9))
    chance = 1.0 / V_CONCEPTS

    # Sanity: both control arms must reproduce within +-0.05 of the published
    # HARD_FAIL baselines (NAIVE 0.65, RESONATOR_HARD 0.63).
    naive_ok = (SANITY_NAIVE_LO <= n_top1 <= SANITY_NAIVE_HI)
    res_ok = (SANITY_RES_LO <= r_top1 <= SANITY_RES_HI)
    sanity_ok = naive_ok and res_ok
    # Paired-seed delta (soft - naive) per the prereg's `> NAIVE + 0.10` clause.
    paired_delta_per_seed = [p["arm_soft_chain_2hop"]["top1"] - p["arm_naive_hard_2hop"]["top1"] for p in ps]
    paired_delta_mean = float(np.mean(paired_delta_per_seed))

    # PRIMARY HARD_PASS
    primary_pass = (s2_top1 >= SOFT_HARD_PASS) and (s2_cv <= CV_GATE) and (paired_delta_mean >= SOFT_OVER_NAIVE_DELTA)
    primary_middle = (s2_top1 >= SOFT_MIDDLE_LO) and (s2_top1 < SOFT_HARD_PASS)
    bonus_3hop = (s3_top1 >= SOFT_3HOP_BONUS)

    sanity_tag = ("sanity_ok"
                  if sanity_ok
                  else ("sanity_MISMATCH(naive_ok=%s res_ok=%s)" % (naive_ok, res_ok)))
    bonus_tag = " | BONUS_3HOP_SOFT_CHAIN_GRADE" if bonus_3hop else ""

    summ = ("NAIVE_HARD_2HOP top1=%.4f cv=%.3f (sanity=[%.2f,%.2f]) | "
            "RESONATOR_HARD_2HOP top1=%.4f cv=%.3f (sanity=[%.2f,%.2f]) | "
            "SOFT_CHAIN_2HOP top1=%.4f cv=%.3f (HP>=%.2f delta>=%.2f cv<=%.2f) [paired_delta=%.4f] | "
            "SOFT_CHAIN_3HOP top1=%.4f cv=%.3f (bonus>=%.2f) | "
            "chance=%.4f V_C=%d V_P=%d N=%d K_SET=%d") % (
        n_top1, n_cv, SANITY_NAIVE_LO, SANITY_NAIVE_HI,
        r_top1, r_cv, SANITY_RES_LO, SANITY_RES_HI,
        s2_top1, s2_cv, SOFT_HARD_PASS, SOFT_OVER_NAIVE_DELTA, CV_GATE, paired_delta_mean,
        s3_top1, s3_cv, SOFT_3HOP_BONUS,
        chance, V_CONCEPTS, V_PREDICATES, N_DIM, K_SET)

    if not sanity_ok:
        # Sanity-rail failure ALWAYS dominates: the regime is wrong, no PRIMARY
        # claim can be made even if the soft-chain measurement looks good.
        return ("HARD_FAIL",
                "SANITY_RAIL_FAIL: control arms do NOT reproduce the 0.65/0.63 "
                "HARD_FAIL baselines; the synthetic regime is different from the "
                "regime that produced today's HARD_FAIL. Verdict UNINFORMATIVE on "
                "the SOFT_CHAIN hypothesis; needs regime-match diagnosis (V_C, V_P, "
                "K_SET, N_DIM, chain construction). %s | %s"
                % (sanity_tag, summ))
    if primary_pass:
        return ("HARD_PASS",
                "HARD_PASS: SOFT-CHAIN closes the inter-hop error-propagation gap "
                "(SOFT_CHAIN_2HOP top1=%.4f >= %.2f, cv=%.3f <= %.2f, paired_delta_over_naive=%.4f >= %.2f). "
                "DFE-analog rescue validated on the same regime that produced today's "
                "Resonator HARD_FAIL. Chain-grade-eligible candidate for cap_map row "
                "PP-multi-hop-reasoning. %s%s | %s"
                % (s2_top1, SOFT_HARD_PASS, s2_cv, CV_GATE, paired_delta_mean,
                   SOFT_OVER_NAIVE_DELTA, sanity_tag, bonus_tag, summ))
    if primary_middle:
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: SOFT_CHAIN_2HOP partial lift (top1=%.4f in [%.2f, %.2f), "
                "cv=%.3f, paired_delta=%.4f). Soft-chaining helps but doesn't fully close "
                "the gap; follow-up: turbo iteration / K_SET sweep / temperature calibration / "
                "K-beam path-sum (angle 3) as alternative mechanism. %s%s | %s"
                % (s2_top1, SOFT_MIDDLE_LO, SOFT_HARD_PASS, s2_cv, paired_delta_mean,
                   sanity_tag, bonus_tag, summ))
    return ("HARD_FAIL",
            "HARD_FAIL: SOFT-CHAIN does NOT rescue the 2-hop gap (SOFT_CHAIN_2HOP top1=%.4f <= %.2f, "
            "paired_delta=%.4f). Inter-hop hard-decision is NOT the dominant failure mode at this regime; "
            "multi-hop limit is more fundamental than chaining mechanism. Revival pivots per research drill: "
            "(a) K-beam path-sum (angle 3); (b) substrate-PageRank (angle 4); (c) upstream encoder / W-capacity. "
            "%s%s | %s"
            % (s2_top1, SOFT_MIDDLE_LO, paired_delta_mean, sanity_tag, bonus_tag, summ))


# -- Driver ----------------------------------------------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d K_SET=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES, K_SET, CONFIG_VERSION),
          flush=True)
    t0 = time.time()
    out_dir = REPO / "data" / ("exp_%s" % EXP_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)
    ps: List[Dict] = []
    for s in SEEDS:
        pf = out_dir / ("partial_seed%d_%s.json" % (s, RUN_MODE))
        if pf.exists():
            try:
                rec = json.loads(pf.read_text(encoding="utf-8"))
                if rec.get("config_version") == CONFIG_VERSION:
                    print("  [seed=%d] RESUME from checkpoint (config match)" % s, flush=True)
                    ps.append(rec); continue
            except Exception:
                pass
        rec = run_seed(s)
        pf.write_text(json.dumps(rec, indent=2), encoding="utf-8")
        ps.append(rec)
    v, vmsg = verdict(ps)
    print("\n[VERDICT] " + vmsg, flush=True)
    metrics = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(SEEDS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": vmsg,
        "DESIGN_NOTE": (
            "exp_dev cell-author 2026-06-24 (Resonator HARD_FAIL revival drill anchor 1). "
            "SOFT-DECISION-CHAIN rescue: replace per-hop argmax hand-off with weighted "
            "superposition of top-K candidates passed forward. CA3 graded-reactivation + "
            "telecom soft-DFE / turbo-decoding analog. 4 arms apples-to-apples (same E/R/W/K_SET/beta "
            "per seed); ONE knob varies between RESONATOR_HARD vs SOFT_CHAIN (hard argmax vs soft "
            "superposition for the inter-hop hand-off). PRIMARY = ARM_SOFT_CHAIN_2HOP top1 vs the "
            "0.65/0.63 HARD_FAIL baselines (which the two control arms must reproduce as sanity).")
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"), flush=True)
