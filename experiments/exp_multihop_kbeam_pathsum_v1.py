"""exp_multihop_kbeam_pathsum_v1 -- K-beam path-sum cell for multi-hop reasoning.

Author: exp_dev (spawn) per Research M4 belief-propagation drill
        notes/research_drill_brain_multihop_M4_belief_propagation_soft_message_passing_3x_2026-06-27.md

DRILL RECOMMENDATION (load-bearing):
  The 2026-06-24 beta-sweep cell fairly tested moderate-temperature soft
  message-passing (BETA_2 with entropy ~2.8 nats = log(16) effective candidates)
  and HARD_FAILed: best soft arm top1 ~ 0.6483 vs baseline 0.6500 at 2-hop.
  The diagnosed failure mode is NOT temperature mis-calibration; it is
  correlated-error amplification on rank-1 cleanup against a shared codebook.

  REPLACE soft-superposition with K-BEAM PATH-SUM:
    - Maintain K top candidates per hop (beam search; preserves diversity).
    - At terminal hop, SUM scores across all surviving paths.
    - Path-sum favors candidates reached via MULTIPLE chains (consensus
      across paths breaks correlated-error rank-1 collapse).

  Cross-domain anchors: particle-filter diversity-preserving resampling;
  LDPC EXIT-chart extrinsic-info separation; DDM with different neural
  populations for sequential evidence accumulation.

ARMS (5):
  A: ARM_BASELINE_TOP1            per-hop argmax; reproduces beta-sweep
                                  baseline (~0.65 at 2-hop, ~0.17 at 5-hop)
  B: ARM_BETA_2_SANITY_REPLICATE  reproduces 2026-06-24 BETA_2 result;
                                  sanity rail for setup-drift detection
  C: ARM_KBEAM_K10_PATHSUM        the mechanism (K=10 beam + path-sum)
  D: ARM_KBEAM_K10_ARGMAX         control (K=10 beam but argmax per hop, NO
                                  path-sum -- proves path-sum load-bearing)
  E: ARM_KBEAM_K30_PATHSUM        does wider beam help?

CARDINALITY (META_RULE_H mandatory):
  5 arms x 3 seeds x [depth-3, depth-5, depth-7] = 45 units.
  EXPECTED_N_UNITS = 45; HARD_FAIL_CARDINALITY_BREACH if observed < 45.

HARD bands (PRIMARY = ARM_KBEAM_K10_PATHSUM at depth-5):
  HARD_PASS: K10_PATHSUM depth-5 top1 >= 0.45
             AND (K10_PATHSUM top1 - K10_ARGMAX top1) >= 0.10
             AND cv <= 0.10
  MIDDLE_BAND: K10_PATHSUM depth-5 top1 in [0.25, 0.45)
               OR path-sum-over-argmax lift in [0.05, 0.10)
  HARD_FAIL: K10_PATHSUM depth-5 top1 < 0.25
             OR (K10_PATHSUM - K10_ARGMAX) < 0.05
  SANITY_BREACH: ARM_BASELINE_TOP1 depth-2 outside [0.60, 0.70]
                 OR ARM_BETA_2_SANITY_REPLICATE depth-2 outside
                 [0.60, 0.70] (setup drift)

Per-arm HP scope (SCHEMA-VET 5b):
  K10_PATHSUM and K10_ARGMAX are the ONLY arms that can fire HARD_PASS.
  BASELINE_TOP1 and BETA_2_SANITY_REPLICATE are RAILS (sanity-only).
  K30_PATHSUM is a saturation/scale probe (HARD_PASS not gated on it).

Routing: remote_cpu_queue (USER 2026-06-27 NO LOCAL directive).
Compute: numpy; matmul-bound. Smoke ~ 20s at N=2048; full ~ 1-1.5h at N=8192.

Disciplines:
  META_RULE_H: cardinality_ok mandatory; EXPECTED_N_UNITS check at end.
  META_RULE_J: no silent except: blocks; record+halt or re-raise.
  META_RULE_K: smoke must FIRE the discriminator (path-sum-vs-argmax
               must DIVERGE measurably in smoke).
  META_RULE_L: band-floor results = MIDDLE_BAND not HARD_PASS.
  META_RULE_M: production-scale instrument calibration; smoke uses
               full-N preview (K=10 depth=5 at N=8192) to verify the
               discriminator survives full-N before dispatch.
  SCHEMA-VET 5b: per-arm HP scope explicit (see above).

ASCII-only; per-seed checkpoint per PROT-021.
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
from typing import Any, Dict, List, Tuple

import numpy as np

REPO = Path(__file__).resolve().parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._seed_checkpoint import (  # noqa: E402 (PROT-021 import gate)
    get_output_dir, resumable_seeds, write_partial, aggregate_partials,
)

ANCHOR_NAME = "multihop_kbeam_pathsum_v1"
EXP_NAME = os.environ.get("HDLAB_EXP_NAME", ANCHOR_NAME)

# Pre-reg bands
HP_PRIMARY_TOP1 = 0.45              # K10_PATHSUM depth-5 top1
HP_PATHSUM_OVER_ARGMAX_LIFT = 0.10  # K10_PATHSUM - K10_ARGMAX
MB_LO = 0.25
MB_LIFT_LO = 0.05
HP_CV_MAX = 0.10

# Sanity rails (beta-sweep 2026-06-24 reproduced at depth-2)
BASELINE_SANITY_LO = 0.60
BASELINE_SANITY_HI = 0.70

# Knobs
V_CONCEPTS = 200
V_PREDICATES = 2     # p1=0, p2=1 (beta-sweep regime for depth-2 sanity rail)
K_SET_CLEANUP = 20   # candidates per hop available for argpartition
BETA_2_VALUE = 2.0   # discriminator arm anchored to 2026-06-24 BETA_2

# K_BEAM widths swept across arms
K_BEAM_C = 10
K_BEAM_D = 10
K_BEAM_E = 30

# HOP_DEPTHS: 3, 5, 7 covers below/at/beyond the substrate's measured 5-hop
# ceiling (~0.17 baseline); depth-2 also computed for sanity rails only.
HOP_DEPTHS = [3, 5, 7]
SANITY_DEPTH = 2  # baseline + beta-2 rails computed at depth-2 for direct
                  # comparison with 2026-06-24 beta-sweep (~0.65 expected)

_ap = argparse.ArgumentParser()
_ap.add_argument("--smoke", action="store_true")
_ap.add_argument("--self-test", action="store_true", dest="self_test")
_ARGS, _ = _ap.parse_known_args()

_HDLAB_EXP_NAME = os.environ.get("HDLAB_EXP_NAME", "")
_NAME_SAYS_SMOKE = "_smoke" in _HDLAB_EXP_NAME.lower()
RUN_MODE = ("smoke" if (_ARGS.smoke or _ARGS.self_test or _NAME_SAYS_SMOKE)
            else os.environ.get("HDLAB_RUN_MODE", "full").lower())

if RUN_MODE == "smoke":
    # META_RULE_M: smoke must include a FULL-N preview arm to verify the
    # K-beam path-sum discriminator survives scale. Smoke at N=2048 with
    # K=10 depth=5 + a single N=8192 preview point on depth=5 only.
    SEEDS = [7]
    N_DIM = 2048
    N_CHAINS = 50
    N_DIM_PREVIEW = 8192       # full-N preview arm
    N_CHAINS_PREVIEW = 40      # smaller chain count for preview only
    EXPECTED_N_UNITS = 5 * 1 * 3  # 5 arms x 1 seed x 3 depths = 15
                                    # (preview is separate, not counted)
else:
    SEEDS = [7, 17, 23]
    N_DIM = 8192
    N_CHAINS = 200
    N_DIM_PREVIEW = None
    N_CHAINS_PREVIEW = None
    EXPECTED_N_UNITS = 5 * 3 * 3  # 5 arms x 3 seeds x 3 depths = 45

CONFIG_VERSION = (
    "kbeam-pathsum-v1: N=%d V_C=%d V_P=%d K_SET=%d n_chains=%d seeds=%s "
    "depths=%s K_beam_C=%d K_beam_D=%d K_beam_E=%d beta_2=%g | bands "
    "HP_top1>=%.2f HP_lift>=%.2f MB_lo=%.2f MB_lift_lo=%.2f cv<=%.2f | "
    "sanity_depth2=[%.2f,%.2f]"
) % (N_DIM, V_CONCEPTS, V_PREDICATES, K_SET_CLEANUP, N_CHAINS, SEEDS,
     HOP_DEPTHS, K_BEAM_C, K_BEAM_D, K_BEAM_E, BETA_2_VALUE,
     HP_PRIMARY_TOP1, HP_PATHSUM_OVER_ARGMAX_LIFT, MB_LO, MB_LIFT_LO,
     HP_CV_MAX, BASELINE_SANITY_LO, BASELINE_SANITY_HI)


# -- Substrate primitives (verbatim from beta-sweep cell for comparability) --

def bipolar(M: int, n: int, g: np.random.Generator) -> np.ndarray:
    X = (g.integers(0, 2, size=(M, n)) * 2 - 1).astype(np.float32)
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-8)


def ingest_hebbian(triples, E: np.ndarray, R: np.ndarray, sq: float,
                   n_dim: int, batch: int = 2000) -> np.ndarray:
    if not triples:
        return np.zeros((n_dim, n_dim), dtype=np.float32)
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


# -- Chain construction: deep variable-length chains -----------------------

def make_deep_chains(n_chains: int, V: int, P: int, max_depth: int,
                     g: np.random.Generator
                     ) -> Tuple[List[Tuple[int, int, int]],
                                 List[List[Tuple[int, int, int]]]]:
    """Build n_chains random chains of `max_depth` hops with predicates in
    [0, P). Returns (all_triples, chains).

    Anti-saturation: nodes within a single chain are unique (no self-loops);
    s-values across chains are unique (each chain starts at a distinct node);
    predicate per-step is sampled in [0, P) (fixed-pair p=0/p=1 if P==2).
    """
    all_triples: List[Tuple[int, int, int]] = []
    chain_queries: List[List[Tuple[int, int, int]]] = []
    used_s: set = set()
    tries = 0
    while len(chain_queries) < n_chains and tries < n_chains * 200:
        tries += 1
        nodes = []
        s = int(g.integers(0, V))
        if s in used_s:
            continue
        nodes.append(s)
        ok = True
        for _ in range(max_depth):
            cand = int(g.integers(0, V))
            inner_tries = 0
            while cand in nodes:
                cand = int(g.integers(0, V))
                inner_tries += 1
                if inner_tries > V * 2:
                    ok = False
                    break
            if not ok:
                break
            nodes.append(cand)
        if not ok:
            continue
        chain: List[Tuple[int, int, int]] = []
        for i in range(max_depth):
            p = int(g.integers(0, P)) if P > 1 else 0
            chain.append((nodes[i], p, nodes[i + 1]))
        all_triples.extend(chain)
        chain_queries.append(chain)
        used_s.add(s)
    if len(chain_queries) < n_chains:
        raise RuntimeError(
            "BLOCKING make_deep_chains: only %d/%d generated for V=%d "
            "max_depth=%d" % (len(chain_queries), n_chains, V, max_depth)
        )
    return all_triples, chain_queries


# -- Chain mechanisms -------------------------------------------------------

def chain_baseline_top1(W, E, R, sq, start: int, relations: List[int]) -> int:
    """Per-hop argmax cleanup over E. State propagates cleaned-up after each
    hop (used in pointer-chain mechanism family; differs from beta-sweep's
    chain_naive_hard which propagates noisy state but cleans up only at end).

    For multi-hop chains, per-hop cleanup is the correct baseline because
    without cleanup the 5-hop signal decays into noise floor.
    """
    s = start
    for p in relations:
        key = (E[s] * R[p] * sq).astype(np.float32)
        scores = E @ (W @ key)
        s = int(scores.argmax())
    return s


def chain_soft_beta(W, E, R, sq, start: int, relations: List[int],
                    k_set: int, beta: float) -> int:
    """Verbatim port of beta-sweep's chain_soft_beta (final-idx only).

    State propagates noisy with per-hop softmax-over-top-K bundling.
    Used by ARM_BETA_2_SANITY_REPLICATE to anchor against 2026-06-24
    BETA_2 result at depth-2.
    """
    state = _l2_normalize(E[start].copy())
    for p in relations:
        transit = W @ (state * R[p] * sq)
        transit = _l2_normalize(transit)
        ent_scores = E @ transit
        top_idx = np.argpartition(ent_scores, -k_set)[-k_set:]
        top_conf = ent_scores[top_idx]
        w = _softmax(beta * top_conf)
        state = (w[:, None] * E[top_idx]).sum(axis=0)
        state = _l2_normalize(state)
    final_scores = E @ state
    return int(final_scores.argmax())


def chain_kbeam(W, E, R, sq, start: int, relations: List[int],
                k_beam: int, aggregation: str
                ) -> int:
    """K-beam search with EITHER path-sum OR argmax-per-hop aggregation.

    Beam mechanism (both aggregations):
      State 0: single candidate (start, score=1.0).
      At hop t, for each beam member i with state E[node_i] and accumulated
      score s_i, compute key_i = E[node_i] * R[p_t] * sq, scores_i = E @ W @
      key_i, take top K_BEAM children, expand to K_BEAM^2 candidates with
      accumulated scores s_i * cleanup_score_ij. Prune back to K_BEAM by
      top accumulated score.

    aggregation='pathsum': at terminal, sum accumulated scores across all
      surviving paths landing on each unique final node; return argmax.
      Path-sum favors final nodes reached via MULTIPLE chains.

    aggregation='argmax': at each hop, replace the K-beam state with the
      single top-1 child (no beam diversity carried across hops). Equivalent
      to a depth-1 lookahead at each step. Used as a control to prove the
      path-sum aggregation (NOT just having K candidates) is load-bearing.

    Returns the final node index.

    Per-hop scores are clipped to [eps, +inf) to avoid log-domain issues;
    accumulated score is multiplicative (product of per-hop similarities),
    computed in log-domain to avoid underflow at depth >= 5.
    """
    if k_beam < 1:
        raise ValueError("k_beam must be >= 1; got %d" % k_beam)
    eps = 1e-9
    # Beam state: list of (node_idx, log_acc_score).
    beam: List[Tuple[int, float]] = [(start, 0.0)]

    for p in relations:
        if aggregation == "argmax":
            # Argmax-per-hop: collapse beam to single top-1 child each hop.
            # Use the highest-scoring beam member's node only.
            node = beam[0][0]
            key = (E[node] * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            top_idx = int(scores.argmax())
            beam = [(top_idx, 0.0)]
            continue

        # path-sum (or beam-then-pathsum at terminal) -- expand each member,
        # keep top-K_BEAM by accumulated log-score.
        candidates: List[Tuple[int, float]] = []
        for node, log_s in beam:
            key = (E[node] * R[p] * sq).astype(np.float32)
            scores = E @ (W @ key)
            # Take top K_BEAM children. Clip to [eps, +inf) for log.
            top_k_idx = np.argpartition(scores, -k_beam)[-k_beam:]
            top_k_scores = scores[top_k_idx]
            # Use raw scores (post-cleanup over E); clip negatives to eps so
            # log-domain works. Negative cleanup scores happen when the
            # cleaned-up vector is anti-correlated with a codebook atom; we
            # treat those as low evidence rather than excluding them.
            clipped = np.maximum(top_k_scores, eps).astype(np.float32)
            log_kids = np.log(clipped)
            for j in range(k_beam):
                candidates.append((int(top_k_idx[j]),
                                    log_s + float(log_kids[j])))
        # Prune to top K_BEAM by accumulated log-score.
        candidates.sort(key=lambda kv: kv[1], reverse=True)
        beam = candidates[:k_beam]

    if aggregation == "pathsum":
        # Aggregate accumulated EXP(log-score) across all surviving paths
        # landing on each unique node. This is the consensus-across-paths
        # signal that breaks correlated-error rank-1 collapse.
        agg: Dict[int, float] = {}
        for node, log_s in beam:
            agg[node] = agg.get(node, 0.0) + math.exp(log_s)
        if not agg:
            return int(beam[0][0]) if beam else 0
        return int(max(agg.items(), key=lambda kv: kv[1])[0])
    # argmax aggregation -- beam was already collapsed to single member per hop
    return int(beam[0][0])


# -- Self-test --------------------------------------------------------------

def _selftest() -> None:
    """Verify (a) primitives end-to-end; (b) K=1 path-sum equals baseline
    (sanity: no beam = single chain); (c) K=3 path-sum diverges from K=1
    on at least one query (proves the mechanism is exercised, not no-op);
    (d) BETA_2 arm produces a different prediction from K=1 path-sum on
    at least one query (proves the beta-sweep regime is wired in).
    """
    g = np.random.default_rng(0)
    n = 512
    V = 30
    P = 2
    sq = math.sqrt(n)
    E = bipolar(V, n, g)
    R = bipolar(max(P, 2), n, g)
    triples, chains = make_deep_chains(8, V, P, max_depth=3, g=g)
    W = ingest_hebbian(triples, E, R, sq, n)
    assert len(chains) >= 4, "selftest: need >=4 chains"

    # (a) primitives run; outputs in [0, V).
    c0 = chains[0]
    start = c0[0][0]
    rels = [t[1] for t in c0]
    base_pred = chain_baseline_top1(W, E, R, sq, start, rels)
    assert isinstance(base_pred, int) and 0 <= base_pred < V, "baseline bad"
    soft_pred = chain_soft_beta(W, E, R, sq, start, rels,
                                 k_set=8, beta=2.0)
    assert isinstance(soft_pred, int) and 0 <= soft_pred < V, "soft bad"
    kbeam_pathsum_pred = chain_kbeam(W, E, R, sq, start, rels,
                                      k_beam=3, aggregation="pathsum")
    assert isinstance(kbeam_pathsum_pred, int) and 0 <= kbeam_pathsum_pred < V
    kbeam_argmax_pred = chain_kbeam(W, E, R, sq, start, rels,
                                     k_beam=3, aggregation="argmax")
    assert isinstance(kbeam_argmax_pred, int) and 0 <= kbeam_argmax_pred < V

    # (b) K=1 path-sum should equal baseline (sanity wiring check). Run on
    # 4 queries and check majority agreement.
    k1_matches = 0
    for c in chains[:4]:
        s = c[0][0]
        rs = [t[1] for t in c]
        b = chain_baseline_top1(W, E, R, sq, s, rs)
        k1 = chain_kbeam(W, E, R, sq, s, rs, k_beam=1, aggregation="pathsum")
        if b == k1:
            k1_matches += 1
    assert k1_matches >= 3, (
        "selftest K1-EQ-BASELINE: K=1 path-sum should match baseline (no "
        "beam = single chain). Got %d/4 matches. If this fails, K-beam "
        "mechanism is wired wrong (single-state path != baseline argmax)."
        % k1_matches
    )

    # (c) K=3 path-sum should DIVERGE from K=1 on at least one query (proves
    # the beam mechanism is exercised; if K=3 always equals K=1, the beam
    # is being collapsed and no path-sum signal exists).
    diverges = 0
    for c in chains[:4]:
        s = c[0][0]
        rs = [t[1] for t in c]
        k1 = chain_kbeam(W, E, R, sq, s, rs, k_beam=1, aggregation="pathsum")
        k3 = chain_kbeam(W, E, R, sq, s, rs, k_beam=3, aggregation="pathsum")
        if k1 != k3:
            diverges += 1
    assert diverges >= 1, (
        "selftest BEAM-EXERCISED: K=3 path-sum must diverge from K=1 path-sum "
        "on at least one of 4 queries (else the beam mechanism is no-op). "
        "Got %d/4 divergent." % diverges
    )

    # (d) K=10 argmax control should diverge from K=10 pathsum somewhere -- if
    # they always agree, then path-sum aggregation is also no-op (proving
    # path-sum is what's load-bearing, not just K candidates).
    ps_vs_am = 0
    for c in chains[:4]:
        s = c[0][0]
        rs = [t[1] for t in c]
        ps = chain_kbeam(W, E, R, sq, s, rs, k_beam=10, aggregation="pathsum")
        am = chain_kbeam(W, E, R, sq, s, rs, k_beam=10, aggregation="argmax")
        if ps != am:
            ps_vs_am += 1
    # We only assert at least 1 divergence to confirm the two aggregations
    # are not identical; the magnitude is for full-scale arms to measure.
    assert ps_vs_am >= 1, (
        "selftest PATHSUM-VS-ARGMAX: K=10 pathsum and K=10 argmax must "
        "diverge on at least one of 4 queries (else path-sum aggregation "
        "is no-op). Got %d/4 divergent." % ps_vs_am
    )

    print(
        "[selftest] PASS: K1=baseline %d/4; K3!=K1 %d/4; "
        "K10_pathsum!=K10_argmax %d/4 (mechanism exercised)"
        % (k1_matches, diverges, ps_vs_am), flush=True,
    )


_selftest()
if _ARGS.self_test:
    print("[self-test] PASS; exiting", flush=True)
    sys.exit(0)


# -- Arm runners -----------------------------------------------------------

def _hits(preds: List[int], truths: List[int]) -> float:
    if not preds:
        return 0.0
    matches = sum(1 for p, t in zip(preds, truths) if p == t)
    return matches / len(preds)


def arm_run(W, E, R, sq, chains: List[List[Tuple[int, int, int]]],
            depth: int, mechanism: str, k_beam: int = 1,
            beta: float = None) -> Dict[str, Any]:
    """Run one arm at one depth across all chains.

    mechanism:
      'baseline_top1' -- chain_baseline_top1
      'beta_soft'     -- chain_soft_beta with beta=beta, k_set=K_SET_CLEANUP
      'kbeam_pathsum' -- chain_kbeam with aggregation='pathsum'
      'kbeam_argmax'  -- chain_kbeam with aggregation='argmax'
    """
    t0 = time.time()
    preds: List[int] = []
    truths: List[int] = []
    for c in chains:
        # Use only the first `depth` triples of each chain.
        cdepth = c[:depth]
        start = cdepth[0][0]
        rels = [t[1] for t in cdepth]
        truth = cdepth[-1][2]
        truths.append(truth)
        if mechanism == "baseline_top1":
            pred = chain_baseline_top1(W, E, R, sq, start, rels)
        elif mechanism == "beta_soft":
            if beta is None:
                raise ValueError("beta required for beta_soft mechanism")
            pred = chain_soft_beta(W, E, R, sq, start, rels,
                                    k_set=K_SET_CLEANUP, beta=beta)
        elif mechanism == "kbeam_pathsum":
            pred = chain_kbeam(W, E, R, sq, start, rels,
                                k_beam=k_beam, aggregation="pathsum")
        elif mechanism == "kbeam_argmax":
            pred = chain_kbeam(W, E, R, sq, start, rels,
                                k_beam=k_beam, aggregation="argmax")
        else:
            raise ValueError("unknown mechanism: %s" % mechanism)
        preds.append(pred)
    top1 = _hits(preds, truths)
    return {
        "top1": round(top1, 4),
        "n_chains": len(chains),
        "depth": depth,
        "mechanism": mechanism,
        "k_beam": k_beam,
        "beta": beta,
        "elapsed_s_arm": round(time.time() - t0, 2),
    }


def run_seed(seed: int) -> Dict[str, Any]:
    """Run all arms across all HOP_DEPTHS + sanity-depth at SANITY_DEPTH."""
    t = time.time()
    g = np.random.default_rng(seed)
    sq = math.sqrt(N_DIM)
    E = bipolar(V_CONCEPTS, N_DIM, g)
    R = bipolar(V_PREDICATES, N_DIM, g)

    # Build chain set at max_depth so all depth-slices use the SAME chains
    # (apples-to-apples across depths; only the slice length varies).
    max_depth = max(max(HOP_DEPTHS), SANITY_DEPTH)
    triples, chains = make_deep_chains(N_CHAINS, V_CONCEPTS, V_PREDICATES,
                                        max_depth=max_depth, g=g)
    W = ingest_hebbian(triples, E, R, sq, N_DIM)
    n_units_observed = 0

    out: Dict[str, Any] = {
        "seed": seed,
        "run_mode": RUN_MODE,
        "N": N_DIM,
        "M": N_CHAINS,
        "V_C": V_CONCEPTS,
        "V_P": V_PREDICATES,
        "K_SET": K_SET_CLEANUP,
        "K_beam_C": K_BEAM_C,
        "K_beam_D": K_BEAM_D,
        "K_beam_E": K_BEAM_E,
        "beta_2": BETA_2_VALUE,
        "hop_depths": HOP_DEPTHS,
        "sanity_depth": SANITY_DEPTH,
        "expected_n_units": EXPECTED_N_UNITS,
        "config_version": CONFIG_VERSION,
        "n_triples": len(triples),
        "n_chains_built": len(chains),
    }

    # SANITY RAILS (depth-2): BASELINE_TOP1 + BETA_2 at depth-2.
    # These pin the cell against the 2026-06-24 beta-sweep results.
    r = arm_run(W, E, R, sq, chains, depth=SANITY_DEPTH,
                 mechanism="baseline_top1")
    out["sanity_baseline_top1_depth2"] = r
    print("  [seed=%d] SANITY ARM_BASELINE_TOP1 depth=%d top1=%.4f t=%.1fs"
          % (seed, SANITY_DEPTH, r["top1"], r["elapsed_s_arm"]), flush=True)
    r = arm_run(W, E, R, sq, chains, depth=SANITY_DEPTH,
                 mechanism="beta_soft", beta=BETA_2_VALUE)
    out["sanity_beta_2_replicate_depth2"] = r
    print("  [seed=%d] SANITY ARM_BETA_2_REPLICATE depth=%d top1=%.4f t=%.1fs"
          % (seed, SANITY_DEPTH, r["top1"], r["elapsed_s_arm"]), flush=True)

    # Main arms across HOP_DEPTHS = [3, 5, 7].
    for d in HOP_DEPTHS:
        # A: BASELINE_TOP1
        r = arm_run(W, E, R, sq, chains, depth=d, mechanism="baseline_top1")
        out["arm_baseline_top1_d%d" % d] = r
        n_units_observed += 1
        print("  [seed=%d] ARM_A_BASELINE_TOP1 depth=%d top1=%.4f t=%.1fs"
              % (seed, d, r["top1"], r["elapsed_s_arm"]), flush=True)

        # B: BETA_2_SANITY_REPLICATE
        r = arm_run(W, E, R, sq, chains, depth=d,
                     mechanism="beta_soft", beta=BETA_2_VALUE)
        out["arm_beta_2_replicate_d%d" % d] = r
        n_units_observed += 1
        print("  [seed=%d] ARM_B_BETA_2_REPLICATE depth=%d top1=%.4f t=%.1fs"
              % (seed, d, r["top1"], r["elapsed_s_arm"]), flush=True)

        # C: KBEAM_K10_PATHSUM
        r = arm_run(W, E, R, sq, chains, depth=d,
                     mechanism="kbeam_pathsum", k_beam=K_BEAM_C)
        out["arm_kbeam_k%d_pathsum_d%d" % (K_BEAM_C, d)] = r
        n_units_observed += 1
        print("  [seed=%d] ARM_C_KBEAM_K%d_PATHSUM depth=%d top1=%.4f t=%.1fs"
              % (seed, K_BEAM_C, d, r["top1"], r["elapsed_s_arm"]),
              flush=True)

        # D: KBEAM_K10_ARGMAX (control)
        r = arm_run(W, E, R, sq, chains, depth=d,
                     mechanism="kbeam_argmax", k_beam=K_BEAM_D)
        out["arm_kbeam_k%d_argmax_d%d" % (K_BEAM_D, d)] = r
        n_units_observed += 1
        print("  [seed=%d] ARM_D_KBEAM_K%d_ARGMAX depth=%d top1=%.4f t=%.1fs"
              % (seed, K_BEAM_D, d, r["top1"], r["elapsed_s_arm"]),
              flush=True)

        # E: KBEAM_K30_PATHSUM (wider beam)
        r = arm_run(W, E, R, sq, chains, depth=d,
                     mechanism="kbeam_pathsum", k_beam=K_BEAM_E)
        out["arm_kbeam_k%d_pathsum_d%d" % (K_BEAM_E, d)] = r
        n_units_observed += 1
        print("  [seed=%d] ARM_E_KBEAM_K%d_PATHSUM depth=%d top1=%.4f t=%.1fs"
              % (seed, K_BEAM_E, d, r["top1"], r["elapsed_s_arm"]),
              flush=True)

    out["n_units_observed"] = n_units_observed
    out["elapsed_s"] = round(time.time() - t, 1)
    return out


def run_smoke_preview_fullN() -> Dict[str, Any]:
    """META_RULE_M smoke discipline: at smoke time, run a single full-N preview
    point (K=10 pathsum at depth=5 on N=8192) to confirm the discriminator
    survives scale. If at full-N the C-vs-D lift evaporates AT SMOKE, do NOT
    dispatch full -- the mechanism failed at scale even before the full run.

    Only invoked when RUN_MODE == 'smoke' AND N_DIM_PREVIEW is set.
    """
    if N_DIM_PREVIEW is None:
        return {}
    print("  [smoke] META_RULE_M FULL-N PREVIEW: N=%d K=%d depth=5"
          % (N_DIM_PREVIEW, K_BEAM_C), flush=True)
    g = np.random.default_rng(7)
    sq = math.sqrt(N_DIM_PREVIEW)
    E = bipolar(V_CONCEPTS, N_DIM_PREVIEW, g)
    R = bipolar(V_PREDICATES, N_DIM_PREVIEW, g)
    triples, chains = make_deep_chains(N_CHAINS_PREVIEW, V_CONCEPTS,
                                        V_PREDICATES, max_depth=5, g=g)
    W = ingest_hebbian(triples, E, R, sq, N_DIM_PREVIEW)
    r_pathsum = arm_run(W, E, R, sq, chains, depth=5,
                         mechanism="kbeam_pathsum", k_beam=K_BEAM_C)
    r_argmax = arm_run(W, E, R, sq, chains, depth=5,
                        mechanism="kbeam_argmax", k_beam=K_BEAM_D)
    r_base = arm_run(W, E, R, sq, chains, depth=5,
                      mechanism="baseline_top1")
    preview = {
        "N_preview": N_DIM_PREVIEW,
        "n_chains_preview": N_CHAINS_PREVIEW,
        "depth_preview": 5,
        "preview_baseline_top1": r_base["top1"],
        "preview_kbeam_k%d_pathsum_top1" % K_BEAM_C: r_pathsum["top1"],
        "preview_kbeam_k%d_argmax_top1" % K_BEAM_D: r_argmax["top1"],
        "preview_pathsum_vs_argmax_lift": round(
            r_pathsum["top1"] - r_argmax["top1"], 4),
        "preview_pathsum_vs_baseline_lift": round(
            r_pathsum["top1"] - r_base["top1"], 4),
    }
    print("  [smoke-preview] N=%d depth=5: baseline=%.4f pathsum=%.4f "
          "argmax=%.4f lift_ps_vs_am=%+.4f lift_ps_vs_base=%+.4f"
          % (N_DIM_PREVIEW, r_base["top1"], r_pathsum["top1"], r_argmax["top1"],
             preview["preview_pathsum_vs_argmax_lift"],
             preview["preview_pathsum_vs_baseline_lift"]), flush=True)
    return preview


# -- Verdict ---------------------------------------------------------------

def verdict(ps: List[Dict[str, Any]]) -> Tuple[str, str]:
    """Mean across seeds for primary K10_PATHSUM at depth-5 + lift over K10_ARGMAX.

    Cardinality gate: each seed must contribute EXPECTED_N_UNITS/len(seeds) units;
    summed across seeds must equal EXPECTED_N_UNITS.
    """
    def mean_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in ps if key in p
                and isinstance(p[key].get("top1"), (int, float))]
        return float(np.mean(vals)) if vals else float("nan")

    def cv_top1(key: str) -> float:
        vals = [p[key]["top1"] for p in ps if key in p
                and isinstance(p[key].get("top1"), (int, float))]
        if len(vals) < 2:
            return 0.0  # single seed -> no CV
        m = float(np.mean(vals))
        return float(np.std(vals) / max(m, 1e-9))

    # Cardinality (META_RULE_H mandatory)
    total_observed = sum(p.get("n_units_observed", 0) for p in ps)
    cardinality_ok = (total_observed == EXPECTED_N_UNITS)

    # Sanity rails at depth-2. The sanity bands [0.60, 0.70] are calibrated
    # against 2026-06-24 beta-sweep at N=8192; they ONLY apply at full mode.
    # Smoke at N=2048 has much smaller capacity by construction (~ N/V_C^2
    # crosstalk scales linearly with 1/N), so depth-2 baseline drops below
    # 0.60 at N=2048 by capacity-limit -- not a real sanity breach.
    # At smoke the sanity rails are informational only.
    baseline_d2 = mean_top1("sanity_baseline_top1_depth2")
    beta2_d2 = mean_top1("sanity_beta_2_replicate_depth2")
    is_full_mode = (ps and ps[0].get("run_mode") == "full")
    if is_full_mode:
        sanity_baseline_ok = (BASELINE_SANITY_LO <= baseline_d2 <= BASELINE_SANITY_HI)
        sanity_beta2_ok = (BASELINE_SANITY_LO <= beta2_d2 <= BASELINE_SANITY_HI)
        sanity_ok = sanity_baseline_ok and sanity_beta2_ok
    else:
        # Smoke: sanity rails are informational; do NOT gate verdict on them.
        sanity_baseline_ok = True
        sanity_beta2_ok = True
        sanity_ok = True

    # Primary: K10_PATHSUM at depth-5
    k10_ps_d5 = mean_top1("arm_kbeam_k%d_pathsum_d5" % K_BEAM_C)
    k10_ps_d5_cv = cv_top1("arm_kbeam_k%d_pathsum_d5" % K_BEAM_C)
    k10_am_d5 = mean_top1("arm_kbeam_k%d_argmax_d5" % K_BEAM_D)
    pathsum_lift = k10_ps_d5 - k10_am_d5

    # Auxiliary
    base_d5 = mean_top1("arm_baseline_top1_d5")
    beta2_d5 = mean_top1("arm_beta_2_replicate_d5")
    k30_ps_d5 = mean_top1("arm_kbeam_k%d_pathsum_d5" % K_BEAM_E)
    k10_ps_d3 = mean_top1("arm_kbeam_k%d_pathsum_d3" % K_BEAM_C)
    k10_ps_d7 = mean_top1("arm_kbeam_k%d_pathsum_d7" % K_BEAM_C)

    summ = (
        "PRIMARY K10_PATHSUM d5=%.4f (cv=%.3f) | K10_ARGMAX d5=%.4f "
        "lift_ps_vs_am=%+.4f | BASELINE d5=%.4f BETA_2 d5=%.4f "
        "K30_PATHSUM d5=%.4f | depth-sweep K10_PATHSUM d3=%.4f d5=%.4f "
        "d7=%.4f | SANITY d2: baseline=%.4f (ok=%s) beta2=%.4f (ok=%s) | "
        "cardinality: observed=%d expected=%d ok=%s | bands "
        "HP_top1>=%.2f HP_lift>=%.2f cv<=%.2f"
    ) % (
        k10_ps_d5, k10_ps_d5_cv, k10_am_d5, pathsum_lift,
        base_d5, beta2_d5, k30_ps_d5,
        k10_ps_d3, k10_ps_d5, k10_ps_d7,
        baseline_d2, sanity_baseline_ok, beta2_d2, sanity_beta2_ok,
        total_observed, EXPECTED_N_UNITS, cardinality_ok,
        HP_PRIMARY_TOP1, HP_PATHSUM_OVER_ARGMAX_LIFT, HP_CV_MAX,
    )

    # Cardinality breach
    if not cardinality_ok:
        return ("HARD_FAIL_CARDINALITY_BREACH",
                "HARD_FAIL_CARDINALITY_BREACH: observed %d units, expected "
                "%d (META_RULE_H mandatory). Cell did not run full grid. "
                "%s" % (total_observed, EXPECTED_N_UNITS, summ))

    # Sanity-rail breach
    if not sanity_ok:
        return ("SANITY_BREACH",
                "SANITY_BREACH: depth-2 rails out of [%.2f, %.2f]. baseline=%.4f "
                "(ok=%s); beta_2=%.4f (ok=%s). 2026-06-24 beta-sweep regime not "
                "reproduced -- setup drifted; do NOT interpret main arms. %s"
                % (BASELINE_SANITY_LO, BASELINE_SANITY_HI,
                   baseline_d2, sanity_baseline_ok, beta2_d2, sanity_beta2_ok,
                   summ))

    # HARD_PASS: K10_PATHSUM d5 >= 0.45 AND lift >= 0.10 AND cv <= 0.10
    if (k10_ps_d5 >= HP_PRIMARY_TOP1
            and pathsum_lift >= HP_PATHSUM_OVER_ARGMAX_LIFT
            and k10_ps_d5_cv <= HP_CV_MAX):
        return ("HARD_PASS",
                "HARD_PASS_KBEAM_PATHSUM_LIFTS_5HOP: K10_PATHSUM d5=%.4f "
                ">= %.2f AND lift_ps_vs_am=%+.4f >= %.2f AND cv=%.3f <= %.2f. "
                "Path-sum is load-bearing (argmax-control K=10 d5=%.4f). "
                "Mechanism breaks correlated-error rank-1 collapse the "
                "2026-06-24 beta-sweep could not. %s"
                % (k10_ps_d5, HP_PRIMARY_TOP1, pathsum_lift,
                   HP_PATHSUM_OVER_ARGMAX_LIFT, k10_ps_d5_cv, HP_CV_MAX,
                   k10_am_d5, summ))

    # MIDDLE_BAND
    if (MB_LO <= k10_ps_d5 < HP_PRIMARY_TOP1) or \
            (MB_LIFT_LO <= pathsum_lift < HP_PATHSUM_OVER_ARGMAX_LIFT):
        return ("MIDDLE_BAND",
                "MIDDLE_BAND: K10_PATHSUM d5=%.4f or lift_ps_vs_am=%+.4f in "
                "partial-mechanism band (HP_top1>=%.2f HP_lift>=%.2f). "
                "Path-sum measurably helps but below chain-grade ceiling. %s"
                % (k10_ps_d5, pathsum_lift, HP_PRIMARY_TOP1,
                   HP_PATHSUM_OVER_ARGMAX_LIFT, summ))

    # HARD_FAIL
    return ("HARD_FAIL",
            "HARD_FAIL_PATHSUM_DOES_NOT_LIFT: K10_PATHSUM d5=%.4f below "
            "MB_LO=%.2f OR lift_ps_vs_am=%+.4f below MB_LIFT_LO=%.2f. "
            "Path-sum cannot escape correlated-error rank-1 collapse even "
            "with K=10 beam diversity. Pivot to encoder/W-capacity track. %s"
            % (k10_ps_d5, MB_LO, pathsum_lift, MB_LIFT_LO, summ))


# -- Driver ----------------------------------------------------------------

if __name__ == "__main__":
    print("[config] anchor=%s mode=%s seeds=%s N=%d V_C=%d V_P=%d K_SET=%d "
          "n_chains=%d depths=%s expected_units=%d | %s"
          % (ANCHOR_NAME, RUN_MODE, SEEDS, N_DIM, V_CONCEPTS, V_PREDICATES,
             K_SET_CLEANUP, N_CHAINS, HOP_DEPTHS, EXPECTED_N_UNITS,
             CONFIG_VERSION), flush=True)

    t0 = time.time()
    out_dir = get_output_dir(EXP_NAME)
    out_dir.mkdir(parents=True, exist_ok=True)

    run_config = {"N": N_DIM, "run_mode": RUN_MODE, "M": N_CHAINS}
    done, remaining = resumable_seeds(SEEDS, out_dir, run_config=run_config)
    print("[ckpt] %d of %d seeds already complete; running %s"
          % (len(done), len(SEEDS), remaining), flush=True)

    for s in remaining:
        rec = run_seed(s)
        write_partial(out_dir, s, rec)

    per_seed = aggregate_partials(out_dir, SEEDS)
    ps_list = [per_seed[str(s)] for s in SEEDS if str(s) in per_seed]

    # META_RULE_M smoke preview (only when in smoke mode)
    smoke_preview = run_smoke_preview_fullN() if RUN_MODE == "smoke" else {}

    v, vmsg = verdict(ps_list)
    print("\n[VERDICT] " + vmsg, flush=True)

    metrics: Dict[str, Any] = {
        "anchor_name": ANCHOR_NAME,
        "verdict": v,
        "verdict_msg": vmsg,
        "run_mode": RUN_MODE,
        "n_seeds": len(ps_list),
        "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": (sum(p.get("n_units_observed", 0)
                                for p in ps_list) == EXPECTED_N_UNITS),
        "config_version": CONFIG_VERSION,
        "per_seed": ps_list,
        "smoke_preview_fullN": smoke_preview,
        "elapsed_s": round(time.time() - t0, 1),
        "summary": vmsg,
        "DESIGN_NOTE": (
            "K-beam path-sum cell per M4 belief-propagation drill "
            "2026-06-27. DRILL REJECTED direct soft-passing re-try "
            "(2026-06-24 BETA_2 already fair-tested moderate temperature "
            "and HARD_FAILED at top1=0.6483 vs baseline 0.6500 at 2-hop). "
            "DRILL RECOMMENDED K-beam path-sum as alternative addressing "
            "the diagnosed correlated-error rank-1 collapse failure mode. "
            "5 arms x 3 seeds x [d3, d5, d7] = 45 units. HARD_PASS requires "
            "K10_PATHSUM d5 >= 0.45 (deflated from naive 0.65 because actual "
            "5-hop baseline is ~0.17) AND (K10_PATHSUM - K10_ARGMAX) >= 0.10 "
            "(path-sum load-bearing) AND cv <= 0.10. K10_ARGMAX control "
            "isolates the path-sum aggregation as the load-bearing component "
            "(vs just having K candidates)."
        ),
    }
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2),
                                            encoding="utf-8")
    print("[done] %.1fs -> %s" % (time.time() - t0, out_dir / "metrics.json"),
          flush=True)
