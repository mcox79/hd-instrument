"""ARC reasoner SR-gated tie-break (v1): does a Successor-Representation graph-support-strength channel,
gated against the existing cosine combiner, resolve the co-derivable ARC ties where symbolic tie-break
measured d=0.000? First honest ARC-facing test of the prior HARD_PASS SR-routing + gated-fusion mechanisms
(design-of-record: notes/research_sr_chaining_arc_reasoning_design_2026-07-26.md). GloVe-free tie-break.

WHAT THIS TESTS (one variable = SR-gated vs cosine-only tie-break among CO-DERIVABLE valid candidates).
  The composed DerivationReasoner (hdlab/reasoner.py) buckets ARC-Challenge-test into gold_only / dist_only /
  tie / not_derived. On the TIE bucket (gold AND >=1 distractor both derive) BOTH prior levers landed
  HONEST-NEG: symbolic-intent tie-break d=0.000 (MEASURED@data/exp_arc_reasoner_symbolic_tiebreak_v1) and
  link-precision pruning d=-0.002 (MEASURED@data/exp_arc_reasoner_link_precision_tie_prune_v1). SR-occupancy
  scores AGGREGATE GRAPH-SUPPORT STRENGTH (discounted forward occupancy M[given,candidate] over ALL walk
  lengths), which neither prior lever computes. This is the NEXT lever, honestly MM-tier (closed-form
  resolvent over a KNOWN static rule-graph -- same tier as the chain_len / combiner / intent levers it
  competes against), applied to the same still-open tie bucket.

HONEST PRIOR (design-flagged, NOT papered over): the ARC rule-graph mean out-degree is < 1 (n_nodes=215,
  n_typed_edges=209), 22x sparser than the toy domain where SR was HARD_PASS (mean degree 6.65). SR's
  distinguishing value (aggregating over MULTIPLE alternate paths) may be DEGENERATE at this density ->
  occ collapses to a near-binary reachable/unreachable indicator chain_len already captures, or CV-lambda*
  collapses toward 0. If so, this is a clean THIRD meaning-boundedness diagnosis, not a failure to hide.
  SR non-degeneracy is a REPORTED SANITY METRIC computed + logged BEFORE the tie result is read.

ARMS (paired: identical graph + identical link_mode + identical CI/do; ONLY the tie-break decision differs).
  LEGACY          -- reproduction of tiebreak_mode="legacy" (Gate-D positive control; must repro tie_acc
                     0.3636 @ n_tie=66 lemma_syn).
  SYMBOLIC        -- reproduction of tiebreak_mode="symbolic" (the prior failed lever; must repro d=0.000).
  SR_ONLY         -- pure lambda=1 endpoint: rank purely by normalized SR occupancy (isolates the signal).
  SR_GATED        -- PRIMARY: convex (1-lam)*z(combiner) + lam*occ, lam by 5-fold CV over the tie bucket
                     (small tie-n; CV is the disjoint-split remedy). Headline = OUT-OF-SAMPLE CV tie_acc.
  SR_SCRAMBLED    -- must-fail #1: SAME SR machinery over a DEGREE-PRESERVING configuration-model shuffle of
                     the edge destinations (destroys real structure, preserves degree). Must stay flat.
  RANDOM_OCC      -- must-fail #2: occ replaced by seeded i.i.d. uniform noise, same gate. Must not beat legacy.

MECHANISM (glass-box; one new scalar per candidate + one learned scalar per CV fold).
  occ_raw(cand) = max over cand-nodes c of ( sum over given-nodes u of M[u,c] ), M = (I-gamma T)^-1, T =
    row-stochastic adjacency of g["fwd"] (SR/resolvent = PPR = discounted future occupancy). gamma=0.85
    PRE-REGISTERED (verbatim from the toy SR cell; NOT tuned on ARC). Within each question, occ and the
    combiner cosine are EACH min-max normalized across the VALID candidate set to [0,1]; gated_score =
    (1-lam)*z(combiner) + lam*occ; decision key among valid = (-gated_score, -givens_covered, chain_len,
    choice_index) -- gated_score promoted above the existing discrete keys (mirrors how combiner already
    sits as the graded key), the discrete keys retained as deterministic fallback (ONE variable changed).
  lam selected by 5-fold CV (seeded, stratified-by-index, sorted) maximizing TIE-subset acc on the training
    folds; the pure-endpoints lam=0 (cosine) and lam=1 (SR) are IN the grid so the gate provably cannot
    underperform the better single channel on the training folds. Reported: mean held-out lam*, per-fold
    distribution, out-of-sample CV tie_acc.

COVERAGE DIAGNOSTIC (report-only, run FIRST, ~free): for each dist_only question classify gold's failure --
  LINK_FAILURE (nodes_for(gold) empty) | DEPTH_BLOCKED (gold nodes non-empty AND meet_connected at depth=6
  succeeds where depth=3 failed -- a near-zero-cost DEPTH bump, a SEPARATE cheaper follow-on, NOT SR's job)
  | STRUCTURALLY_ABSENT (still disconnected at depth<=6). Settles whether a DEPTH-bump cell is worth queuing
  next, WITHOUT conflating it with the SR test.

PRE-REGISTERED BANDS (mirror exp_arc_reasoner_symbolic_tiebreak_v1 for direct comparability).
  Guardrails (else INCONCLUSIVE): gold_only preserved >= 0.95; n_tie >= 30; LEGACY reproduces 0.3636 +/- tol.
  SR non-degeneracy (mean per-question within-valid-candidate std of occ_raw over ties >= 1e-4) is the single
    most likely failure point at mean-degree<1; reported either way; degenerate -> HARD_FAIL (pre-registered
    honest "graph too sparse for SR's multi-path signal" collapse, NOT INCONCLUSIVE).
  HARD_PASS (SR_GATED_TIEBREAK_RECOVERS): SR_GATED - LEGACY >= 0.10 AND SR_GATED >= 0.42 AND
    SR_SCRAMBLED - LEGACY <= 0.03 AND mean CV lam* > 0.15 AND gold_only preserved AND SR non-degenerate.
  MIDDLE_BAND: SR_GATED rises [0.03, 0.10) over legacy with guardrails holding, OR SR non-degenerate but
    mean lam* <= 0.15 with a small net positive.
  HARD_FAIL (SR_GATED_TIEBREAK_FAILS): SR_GATED - legacy <= 0.03, OR SR column degenerate at this scale, OR
    SR_SCRAMBLED rises comparably to SR_GATED (artifact).
  Cross-config: run BOTH link_mode=lemma_syn (n_tie=66) AND link_mode=lemma (n_tie=44) for consistency.

## Compute architecture
class: (b) sequential-CPU with justification. The dominant cost is the real DerivationReasoner eval over
  1172 ARC questions x candidates (nodes_for + meet_connected per candidate) -- inherently a per-question CPU
  loop over a tiny 215-node graph; prior single-config cells ran ~90-105s. The SR channel is a single dense
  215x215 LU solve (sub-second), reused across all questions/arms/configs; GPU buys nothing at n=215. Storage:
  no_storage (glass-box symbolic graph; no HD bundle). device: cpu (numpy only; no torch tensors at scale).

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at self-test (META_RULE_AF): LEGACY / SR_ONLY / SR_GATED / SR_SCRAMBLED / RANDOM_OCC
#   decision signatures distinct on the planted tie set (SYMBOLIC may equal LEGACY when no intent fires --
#   EXEMPTED: symbolic==legacy is the MEASURED prior d=0.000 outcome, not a bug).
# - final_metrics_atomicity: tmp_replace (os.replace on metrics.json.tmp).
# - except SystemExit: raise BEFORE except Exception (no BaseException / no bare except).
# - crlb / info-ceiling: tie_acc floor = LEGACY 0.3636 (MEASURED anchor); random-guess among ties ~ 1/mean
#   n_valid. HARD_PASS 0.42 is on the achievable side (SYMBOLIC/link levers reached the SAME 0.3636 ceiling;
#   the question is whether SR's graph-support channel lifts it). crlb_n/a: no closed-form noise floor -- the
#   discriminator is a discrete tie-break decision, not a continuous estimate.
# - baseline_in_band: LEGACY tie_acc 0.3636 in (0.05, 0.95); SR non-degeneracy is the AG-analog gate (a
#   degenerate SR column = the mechanism cannot fire -> pre-registered HARD_FAIL, reported honestly).
# - discriminator survives scale: the tie bucket only fully populates at FULL N=1172 (n_tie=66/44); smoke
#   reports partial buckets as a preview; the planted self-test fires SR-discriminates + gated-beats-cosine +
#   scramble-collapses deterministically (mechanism CAN-fire proven off the real encoder, GloVe-free).
# - HARD_PASS strictly above floor: 0.42 >= LEGACY 0.3636 + margin; +0.10 rise gate is a categorical margin.
# - HP_SCOPE: the recovery gates apply to SR_GATED only. LEGACY/SYMBOLIC = positive-control reproductions
#   (must repro the MEASURED anchors); SR_SCRAMBLED + RANDOM_OCC = must-fail controls (must stay flat);
#   SR_ONLY = diagnostic endpoint (reported, not gated).
# - cardinality: EXPECTED buckets per config = gold_only + dist_only + tie + not_derived = 1172; asserted.
# - per-unit failure-class instrumentation (no bare except).
# - calibration_check: adaptive_with_discriminator_gate -- gamma=0.85 + LAMBDA_GRID PRE-REGISTERED, NOT tuned
#   on ARC; lam is LEARNED by CV on disjoint tie folds (never on the fold it scores); bands pre-registered.
# - deterministic_seeding: fixed int seed; CV folds via seeded default_rng + sorted; scramble + random-occ
#   seeded via default_rng; NO hash()-derived seeds; NO list(set()) ordering.
# - all numbers tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@ in the design note.
# - progress_logging: print_flush_true (line-buffered stdout + per-config/per-stage flush prints).

Contract: INLINE-LOCAL foreground-to-completion; NO push/remote-persist; ASCII-only; deterministic; repo
.venv. Agent-reported VET-PENDING; NO atom banking (skunkworks VETs).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import numpy as np

_THIS = os.path.abspath(__file__)
_REPO = os.path.dirname(os.path.dirname(_THIS))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

from hdlab.reasoner import DerivationReasoner  # noqa: E402
from experiments import exp_arc_derivation_connectivity_gate_v1 as gate  # noqa: E402
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc  # noqa: E402
from experiments import exp_arc_derivation_connectivity_gate_cleannodes_v2 as clean  # noqa: E402

ANCHOR_NAME = "arc_reasoner_sr_gated_tiebreak_v1"
SEED = 20260726

# curated 233-rule typed graph -- the SAME rule set the prior symbolic-tiebreak / link-precision cells used
# (data/rules/arc_science_typed_rules_v1.json -> n_nodes=215, n_typed_edges=209, mean out-degree<1). Passing
# these as rows= is load-bearing: the default full-WorldTree parse builds a DIFFERENT, 10x-larger graph and
# would NOT reproduce the LEGACY tie_acc=0.3636 baseline (Gate-D positive control).
RULES_PATH = os.path.join(_REPO, "data", "rules", "arc_science_typed_rules_v1.json")

# ---- pre-registered SR / gate knobs (NOT tuned on ARC) ----
SR_GAMMA_PRIMARY = 0.85                       # CITED@exp_grounding_multihop_sr_reachability_routing_v1 (verbatim)
DIAG_GAMMAS = [0.70, 0.85, 0.95]              # diagnostic sweep on SR_GATED CV tie_acc (logged, NOT gated)
LAMBDA_GRID = [round(x, 3) for x in np.linspace(0.0, 1.0, 11).tolist()]   # 0.0,0.1,...,1.0 (endpoints included)
N_FOLDS = 5
DEPTH_BUMP = 6                                # coverage-diagnostic depth for the DEPTH_BLOCKED classifier

# ---- pre-registered bands (mirror exp_arc_reasoner_symbolic_tiebreak_v1) ----
GOLD_ONLY_FLOOR = 0.95
N_TIE_MIN = 30
SR_DEGEN_STD_MIN = 1e-4                        # CITED@toy SR cell SR_DEGEN_STD_MIN
TIE_ABS_PASS = 0.42
TIE_RISE_PASS = 0.10
TIE_RISE_STUCK = 0.03
SCRAMBLE_FLAT_MAX = 0.03
LAMBDA_LEANS_MIN = 0.15

# ---- Gate-D positive-control reproduction anchors (MEASURED@ the two prior cells) ----
REPRO_TIE_ACC = {"lemma_syn": 0.3636, "lemma": 0.3409}   # MEASURED@link_precision_tie_prune_v1:per_config
REPRO_TOL = 0.02
REPRO_BUCKETS = {"lemma_syn": {"gold_only": 26, "dist_only": 114, "tie": 66},
                 "lemma": {"gold_only": 16, "dist_only": 69, "tie": 44}}

# arm names
LEGACY = "LEGACY"
SYMBOLIC = "SYMBOLIC"
SR_ONLY = "SR_ONLY"
SR_GATED = "SR_GATED"
SR_SCRAMBLED = "SR_SCRAMBLED"
RANDOM_OCC = "RANDOM_OCC"
ALL_ARMS = [LEGACY, SYMBOLIC, SR_ONLY, SR_GATED, SR_SCRAMBLED, RANDOM_OCC]

_T0 = [time.perf_counter()]


def _log(m: str) -> None:
    print("[%s] %s" % (ANCHOR_NAME, m), flush=True)


def _fmt(x) -> str:
    return ("%.4f" % x) if (isinstance(x, float) and x == x) else ("nan" if isinstance(x, float) else str(x))


# ===========================================================================
# SR / resolvent machinery. REPLICATED BYTE-FAITHFULLY (reuse-by-provenance, per the do-operator precedent
# in hdlab/reasoner.py) from experiments/exp_grounding_multihop_sr_reachability_routing_v1.py::SRSolver +
# build_transition_dense, adapted only to a fwd Dict[int,set] (the ARC graph shape) rather than the toy
# cell's dir_adj list-of-(v,rel). Importing the toy cell drags a heavy grounding import chain; the two pure
# numeric objects are replicated with citation instead of reinvented.
# ===========================================================================
def build_transition_from_fwd(fwd: Dict[int, set], n_nodes: int) -> np.ndarray:
    """T [n,n] row-stochastic: T[u,v] = (#edges u->v)/out_degree(u). Dangling rows (deg 0) stay all-zero
    (a node with no out-edges never leaves -> M[dangling, G]=0 for G!=dangling; PPR-standard dangling
    handling without teleport = correct for a strict reachability score). CITED@build_transition_dense."""
    A = np.zeros((n_nodes, n_nodes), dtype=np.float64)
    for u in range(n_nodes):
        for v in fwd.get(u, ()):
            A[u, int(v)] += 1.0
    deg = A.sum(axis=1, keepdims=True)
    deg[deg == 0.0] = 1.0
    return (A / deg).astype(np.float64)


class SRSolver:
    """Closed-form SR column solver. Factors (I - gamma*T) once per gamma (cached), then solves
    (I - gamma*T) X = E for the one-hot goal RHS. X[:,j] = M[:, goal_j] = expected discounted occupancy of
    goal_j starting FROM every node. CITED@exp_grounding_multihop_sr_reachability_routing_v1::SRSolver."""

    def __init__(self, T_dense: np.ndarray):
        self.T = T_dense
        self.n = int(T_dense.shape[0])
        self._inv: Dict[float, np.ndarray] = {}

    def _resolvent(self, gamma: float) -> np.ndarray:
        key = round(float(gamma), 6)
        if key not in self._inv:
            A = np.eye(self.n, dtype=np.float64) - float(gamma) * self.T
            self._inv[key] = np.linalg.inv(A)   # M = (I - gamma T)^-1 (full resolvent; n=215 is trivial)
        return self._inv[key]

    def columns(self, goals_unique: np.ndarray, gamma: float) -> np.ndarray:
        M = self._resolvent(gamma)
        gj = np.asarray(goals_unique, dtype=np.int64)
        return M[:, gj]   # [n, U], >= 0 elementwise since T>=0, gamma<1

    def full(self, gamma: float) -> np.ndarray:
        return self._resolvent(gamma)


# ===========================================================================
# scrambled graph (must-fail control #1): degree-preserving configuration-model shuffle of edge destinations.
# ===========================================================================
def scramble_fwd_degree_preserving(fwd: Dict[int, set], n_nodes: int, rng: np.random.Generator) -> Dict[int, set]:
    """Rewire: preserve each node's out-degree but randomly permute the multiset of all destination
    endpoints across the edge slots. Destroys genuine reachability structure, preserves degree sequence."""
    heads: List[int] = []
    dests: List[int] = []
    for u in range(n_nodes):
        for v in fwd.get(u, ()):
            heads.append(u)
            dests.append(int(v))
    dests_arr = np.asarray(dests, dtype=np.int64)
    perm = rng.permutation(dests_arr.shape[0])
    dests_shuf = dests_arr[perm]
    out: Dict[int, set] = {}
    for i, u in enumerate(heads):
        out.setdefault(u, set()).add(int(dests_shuf[i]))
    return out


# ===========================================================================
# occupancy per question. occ_raw(candidate) = max over cand-nodes c of ( sum over given-nodes u of M[u,c] ).
# ===========================================================================
def occ_for_candidates(sr_solver: SRSolver, given_nodes: set, cand_node_sets: List[set],
                       gamma: float) -> np.ndarray:
    given = np.asarray(sorted(given_nodes), dtype=np.int64)
    occ = np.zeros(len(cand_node_sets), dtype=np.float64)
    if given.shape[0] == 0:
        return occ
    # solve columns for the union of candidate nodes (one multi-RHS read of the cached resolvent)
    uniq_nodes = sorted(set().union(*cand_node_sets)) if cand_node_sets else []
    if not uniq_nodes:
        return occ
    uniq_arr = np.asarray(uniq_nodes, dtype=np.int64)
    X = sr_solver.columns(uniq_arr, gamma)          # [n, U] ; X[u, j] = M[u, uniq_nodes[j]]
    col_of = {int(nid): j for j, nid in enumerate(uniq_nodes)}
    given_sum = X[given, :].sum(axis=0)             # [U] : sum over given rows of M[given, node]
    for ci, cnodes in enumerate(cand_node_sets):
        if not cnodes:
            occ[ci] = 0.0
            continue
        occ[ci] = max(float(given_sum[col_of[int(c)]]) for c in cnodes)
    return occ


def _minmax(v: np.ndarray) -> np.ndarray:
    v = np.asarray(v, dtype=np.float64)
    lo = float(v.min())
    hi = float(v.max())
    if hi - lo <= 1e-12:
        return np.zeros_like(v)
    return (v - lo) / (hi - lo)


# ===========================================================================
# tie-break decisions among the VALID (derivable + not CI-rejected) candidates of one question.
# Each candidate record = dict{choice_index, is_gold, givens_covered, chain_len, combiner_score,
#   chain_relations, term_rel, occ_<arm>}. Returns 1 if the chosen candidate is gold else 0.
# ===========================================================================
def _decide_legacy(valid: List[dict]) -> int:
    best = min(valid, key=lambda c: (-c["givens_covered"], c["chain_len"], -c["combiner_score"],
                                     c["choice_index"]))
    return 1 if best["is_gold"] else 0


def _decide_symbolic(valid: List[dict], intent: set) -> int:
    best = min(valid, key=lambda c: DerivationReasoner._symbolic_key(c, intent))
    return 1 if best["is_gold"] else 0


def _decide_gated(valid: List[dict], occ_key: str, lam: float) -> int:
    occ = _minmax(np.asarray([c[occ_key] for c in valid], dtype=np.float64))
    z = _minmax(np.asarray([c["combiner_score"] for c in valid], dtype=np.float64))
    gated = (1.0 - lam) * z + lam * occ
    order = sorted(range(len(valid)),
                   key=lambda i: (-gated[i], -valid[i]["givens_covered"], valid[i]["chain_len"],
                                  valid[i]["choice_index"]))
    return 1 if valid[order[0]]["is_gold"] else 0


# ===========================================================================
# 5-fold CV lambda selection over the tie bucket. Returns out-of-sample CV tie_acc + mean/per-fold lam*.
# ===========================================================================
def cv_lambda_select(tie_qs: List[dict], occ_key: str, grid: List[float], n_folds: int,
                     seed: int) -> dict:
    n = len(tie_qs)
    if n < n_folds:
        # too few for CV: single in-sample best lambda (reported, flagged)
        accs = [np.mean([_decide_gated(q["valid"], occ_key, lam) for q in tie_qs]) for lam in grid]
        best = int(np.argmax(accs))
        return dict(cv_acc=float(accs[best]), mean_lambda=float(grid[best]),
                    per_fold_lambda=[grid[best]], cv_fallback_single_split=True)
    rng = np.random.default_rng(seed)
    order = np.asarray(sorted(range(n)), dtype=np.int64)
    order = rng.permutation(order)
    folds = [sorted(order[i::n_folds].tolist()) for i in range(n_folds)]   # stratified-by-shuffled-index
    correct = 0
    per_fold_lambda: List[float] = []
    for fi in range(n_folds):
        test_idx = folds[fi]
        train_idx = [i for f in range(n_folds) if f != fi for i in folds[f]]
        train = [tie_qs[i] for i in train_idx]
        # pick lam* maximizing TRAIN tie_acc (first-max = smallest lam on ties = conservative)
        train_accs = [float(np.mean([_decide_gated(q["valid"], occ_key, lam) for q in train])) for lam in grid]
        lam_star = grid[int(np.argmax(train_accs))]
        per_fold_lambda.append(lam_star)
        for i in test_idx:
            correct += _decide_gated(tie_qs[i]["valid"], occ_key, lam_star)
    return dict(cv_acc=float(correct) / n, mean_lambda=float(np.mean(per_fold_lambda)),
                per_fold_lambda=per_fold_lambda, cv_fallback_single_split=False)


# ===========================================================================
# per-config evaluation: bucket 1172 questions, build tie records, run coverage diagnostic + all arms.
# ===========================================================================
def evaluate_config(reasoner: DerivationReasoner, questions: List[dict], link_mode: str,
                    sr_solver: SRSolver, sr_solver_scr: SRSolver, seed: int,
                    output_dir: str) -> dict:
    reasoner.link_mode = link_mode
    typed = reasoner.arms["typed"]
    fwd, bwd = typed["fwd"], typed["bwd"]

    buckets = {"gold_only": 0, "dist_only": 0, "tie": 0, "not_derived": 0}
    tie_qs: List[dict] = []
    dist_only_qs: List[dict] = []
    rng_occ = np.random.default_rng(seed * 101 + 7)   # RANDOM_OCC noise generator (seeded, deterministic)

    n = len(questions)
    for qi, q in enumerate(questions):
        ci_gold = q["correct_index"]
        res = reasoner._reason_arm(q, typed)
        pc = res["per_choice"]
        intent = set(res["intent_relations"])
        valid = [c for c in pc if c["derivable"] and not c["rejected_by_ci"]]
        valid_idx = set(c["choice_index"] for c in valid)
        gold_derivable = ci_gold in valid_idx
        dist_derivable = any(c["choice_index"] != ci_gold for c in valid)
        if gold_derivable and dist_derivable:
            bucket = "tie"
        elif gold_derivable and not dist_derivable:
            bucket = "gold_only"
        elif dist_derivable and not gold_derivable:
            bucket = "dist_only"
        else:
            bucket = "not_derived"
        buckets[bucket] += 1

        if bucket == "tie":
            given_nodes = reasoner.nodes_for(q["stem"])
            cand_node_sets = [reasoner.nodes_for(q["choices"][c["choice_index"]]) for c in valid]
            occ_real = occ_for_candidates(sr_solver, given_nodes, cand_node_sets, SR_GAMMA_PRIMARY)
            occ_scr = occ_for_candidates(sr_solver_scr, given_nodes, cand_node_sets, SR_GAMMA_PRIMARY)
            occ_rnd = rng_occ.random(len(valid))
            vrecs = []
            for k, c in enumerate(valid):
                vrecs.append({
                    "choice_index": c["choice_index"], "is_gold": (c["choice_index"] == ci_gold),
                    "givens_covered": c["givens_covered"], "chain_len": c["chain_len"],
                    "combiner_score": c["combiner_score"], "chain_relations": c["chain_relations"],
                    "term_rel": c["term_rel"],
                    "occ_real": float(occ_real[k]), "occ_scr": float(occ_scr[k]), "occ_rnd": float(occ_rnd[k]),
                })
            tie_qs.append({"qid": q["qid"], "correct_index": ci_gold, "intent": intent, "valid": vrecs,
                           "occ_raw": occ_real.tolist(), "occ_std": float(np.std(occ_real))})
        elif bucket == "dist_only":
            dist_only_qs.append(q)

        if (qi + 1) % 200 == 0:
            _log("  [%s] bucketed %d/%d ties=%d dist_only=%d" % (link_mode, qi + 1, n,
                                                                 buckets["tie"], buckets["dist_only"]))

    # ---- coverage diagnostic (report-only) : dist_only 3-way gold-failure classification ----
    cov = {"LINK_FAILURE": 0, "DEPTH_BLOCKED": 0, "STRUCTURALLY_ABSENT": 0}
    for q in dist_only_qs:
        given_nodes = reasoner.nodes_for(q["stem"])
        gold_nodes = reasoner.nodes_for(q["choices"][q["correct_index"]])
        if not gold_nodes:
            cov["LINK_FAILURE"] += 1
        elif gate.meet_connected(fwd, bwd, given_nodes, gold_nodes, DEPTH_BUMP, min_len=1):
            cov["DEPTH_BLOCKED"] += 1
        else:
            cov["STRUCTURALLY_ABSENT"] += 1
    n_dist = max(1, len(dist_only_qs))
    cov_frac = {k: round(v / n_dist, 4) for k, v in cov.items()}

    # ---- SR non-degeneracy sanity (computed + reported BEFORE the tie result is read) ----
    n_nodes = reasoner.g["n_nodes"]
    M = sr_solver.full(SR_GAMMA_PRIMARY)
    offdiag = M.copy()
    np.fill_diagonal(offdiag, 0.0)
    reach_density = float((offdiag > 1e-9).sum()) / max(1, n_nodes * (n_nodes - 1))
    col_std_mean = float(np.std(M, axis=0).mean())
    tie_occ_std_mean = float(np.mean([tq["occ_std"] for tq in tie_qs])) if tie_qs else 0.0
    tie_occ_allzero_frac = (float(np.mean([1.0 if all(v == 0.0 for v in tq["occ_raw"]) else 0.0
                                           for tq in tie_qs])) if tie_qs else 1.0)
    sr_not_degenerate = bool(tie_occ_std_mean >= SR_DEGEN_STD_MIN)
    _log("  [%s] SR SANITY (pre-tie): graph reach_density=%.4f col_std_mean=%.4g | tie_occ_std_mean=%.4g "
         "(>=%.0e ? %s) tie_occ_allzero_frac=%.3f" % (link_mode, reach_density, col_std_mean,
         tie_occ_std_mean, SR_DEGEN_STD_MIN, sr_not_degenerate, tie_occ_allzero_frac))

    # ---- arms on the tie bucket ----
    n_tie = len(tie_qs)
    legacy_acc = float(np.mean([_decide_legacy(q["valid"]) for q in tie_qs])) if n_tie else float("nan")
    symbolic_acc = (float(np.mean([_decide_symbolic(q["valid"], q["intent"]) for q in tie_qs]))
                    if n_tie else float("nan"))
    sr_only_acc = (float(np.mean([_decide_gated(q["valid"], "occ_real", 1.0) for q in tie_qs]))
                   if n_tie else float("nan"))
    cv_real = cv_lambda_select(tie_qs, "occ_real", LAMBDA_GRID, N_FOLDS, seed * 13 + 1) if n_tie else {}
    cv_scr = cv_lambda_select(tie_qs, "occ_scr", LAMBDA_GRID, N_FOLDS, seed * 13 + 1) if n_tie else {}
    cv_rnd = cv_lambda_select(tie_qs, "occ_rnd", LAMBDA_GRID, N_FOLDS, seed * 13 + 1) if n_tie else {}

    arm_tie_acc = {
        LEGACY: legacy_acc, SYMBOLIC: symbolic_acc, SR_ONLY: sr_only_acc,
        SR_GATED: cv_real.get("cv_acc", float("nan")),
        SR_SCRAMBLED: cv_scr.get("cv_acc", float("nan")),
        RANDOM_OCC: cv_rnd.get("cv_acc", float("nan")),
    }
    # diagnostic gamma sweep on SR_GATED CV tie_acc (logged, NOT gated)
    gamma_sweep = {}
    for gg in DIAG_GAMMAS:
        if gg == SR_GAMMA_PRIMARY:
            gamma_sweep["%.2f" % gg] = round(cv_real.get("cv_acc", float("nan")), 4)
            continue
        # recompute occ_real at this gamma for each tie q, then CV
        tmp = []
        for q in tie_qs:
            given_nodes = reasoner.nodes_for(q_stem_lookup(questions, q["qid"]))
            cand_sets = [reasoner.nodes_for(q_choice_lookup(questions, q["qid"], c["choice_index"]))
                         for c in q["valid"]]
            occ_g = occ_for_candidates(sr_solver, given_nodes, cand_sets, gg)
            vv = [dict(c, occ_g=float(occ_g[k])) for k, c in enumerate(q["valid"])]
            tmp.append({"valid": vv})
        cv_g = cv_lambda_select(tmp, "occ_g", LAMBDA_GRID, N_FOLDS, seed * 13 + 1)
        gamma_sweep["%.2f" % gg] = round(cv_g.get("cv_acc", float("nan")), 4)

    gold_only_acc = 1.0   # by construction: single-valid-candidate wins are untouched by any tie-break arm
    _log("  [%s] TIE n=%d | LEGACY=%.4f SYMBOLIC=%.4f SR_ONLY=%.4f SR_GATED=%.4f(lam*=%.3f) "
         "SR_SCR=%.4f RAND=%.4f | gamma_sweep=%s" % (
             link_mode, n_tie, legacy_acc, symbolic_acc, sr_only_acc, arm_tie_acc[SR_GATED],
             cv_real.get("mean_lambda", float("nan")), arm_tie_acc[SR_SCRAMBLED], arm_tie_acc[RANDOM_OCC],
             gamma_sweep))

    return {
        "link_mode": link_mode, "n_questions": n, "buckets": buckets, "n_tie": n_tie,
        "coverage_diagnostic": {"counts": cov, "fractions": cov_frac, "n_dist_only": len(dist_only_qs)},
        "sr_sanity": {"graph_reach_density": round(reach_density, 5), "graph_col_std_mean": col_std_mean,
                      "tie_occ_std_mean": tie_occ_std_mean, "tie_occ_allzero_frac": round(tie_occ_allzero_frac, 4),
                      "sr_not_degenerate": sr_not_degenerate, "SR_DEGEN_STD_MIN": SR_DEGEN_STD_MIN},
        "arm_tie_acc": {a: (round(v, 4) if v == v else None) for a, v in arm_tie_acc.items()},
        "gold_only_acc": gold_only_acc,
        "cv": {"real": cv_real, "scrambled": cv_scr, "random": cv_rnd},
        "gamma_sweep_cv_tie_acc": gamma_sweep,
        "tie_examples": [{"qid": tq["qid"], "occ_raw": [round(x, 5) for x in tq["occ_raw"]],
                          "n_valid": len(tq["valid"])} for tq in tie_qs[:8]],
    }


def _load_rules(path: str) -> List[dict]:
    """Load the curated typed rule rows (CITED@exp_arc_reasoner_symbolic_tiebreak_v1::_load_rules, verbatim)."""
    d = json.load(open(path, "r", encoding="utf-8"))
    rows = d.get("rules", d.get("rows"))
    if not rows:
        raise ValueError("no 'rules'/'rows' key in %s; keys=%s" % (path, list(d.keys())))
    for r in rows:
        if not all(k in r for k in ("relation", "arg0", "arg1")):
            raise ValueError("malformed rule row: %s" % r)
    return rows


def q_stem_lookup(questions: List[dict], qid: str) -> str:
    for q in questions:
        if q["qid"] == qid:
            return q["stem"]
    return ""


def q_choice_lookup(questions: List[dict], qid: str, ci: int) -> str:
    for q in questions:
        if q["qid"] == qid:
            return q["choices"][ci]
    return ""


# ===========================================================================
# aggregate + verdict + bands (per-config, primary = lemma_syn)
# ===========================================================================
def verdict_for_config(cfg_res: dict) -> dict:
    lm = cfg_res["link_mode"]
    at = cfg_res["arm_tie_acc"]
    legacy = at[LEGACY]
    gated = at[SR_GATED]
    scr = at[SR_SCRAMBLED]
    rnd = at[RANDOM_OCC]
    n_tie = cfg_res["n_tie"]
    mean_lambda = cfg_res["cv"]["real"].get("mean_lambda", float("nan"))
    sr_nondegen = cfg_res["sr_sanity"]["sr_not_degenerate"]
    gold_only = cfg_res["gold_only_acc"]

    rise = (gated - legacy) if (gated is not None and legacy is not None) else float("nan")
    scr_rise = (scr - legacy) if (scr is not None and legacy is not None) else float("nan")

    # Gate-D positive control: LEGACY reproduces the MEASURED anchor
    repro_target = REPRO_TIE_ACC.get(lm, float("nan"))
    repro_ok = bool(legacy is not None and abs(legacy - repro_target) <= REPRO_TOL)
    buckets_target = REPRO_BUCKETS.get(lm, {})
    buckets_match = all(cfg_res["buckets"].get(k) == v for k, v in buckets_target.items())

    guardrails_ok = bool(gold_only >= GOLD_ONLY_FLOOR and n_tie >= N_TIE_MIN)

    hard_pass = bool(rise == rise and rise >= TIE_RISE_PASS and gated is not None and gated >= TIE_ABS_PASS
                     and scr_rise == scr_rise and scr_rise <= SCRAMBLE_FLAT_MAX
                     and mean_lambda == mean_lambda and mean_lambda > LAMBDA_LEANS_MIN
                     and sr_nondegen and guardrails_ok)
    scramble_artifact = bool(scr_rise == scr_rise and scr_rise > SCRAMBLE_FLAT_MAX and rise == rise
                             and scr_rise >= rise - 0.02)
    hard_fail = bool((rise == rise and rise <= TIE_RISE_STUCK) or (not sr_nondegen) or scramble_artifact)
    middle = bool((rise == rise and TIE_RISE_STUCK < rise < TIE_RISE_PASS and guardrails_ok)
                  or (sr_nondegen and mean_lambda == mean_lambda and mean_lambda <= LAMBDA_LEANS_MIN
                      and rise == rise and rise > TIE_RISE_STUCK))

    if not guardrails_ok:
        verdict = "INCONCLUSIVE_GUARDRAIL"
    elif not repro_ok:
        verdict = "INCONCLUSIVE_POSITIVE_CONTROL_REPRO_DRIFT"
    elif hard_pass:
        verdict = "HARD_PASS_SR_GATED_TIEBREAK_RECOVERS"
    elif not sr_nondegen:
        verdict = "HARD_FAIL_SR_DEGENERATE_AT_THIS_SCALE"
    elif scramble_artifact:
        verdict = "HARD_FAIL_SR_SCRAMBLE_ARTIFACT"
    elif hard_fail:
        verdict = "HARD_FAIL_SR_GATED_TIEBREAK_FAILS"
    elif middle:
        verdict = "MIDDLE_BAND_SR_GATED_PARTIAL"
    else:
        verdict = "MIDDLE_BAND_SR_GATED_PARTIAL"

    return {
        "link_mode": lm, "verdict": verdict,
        "tie_rise_gated_minus_legacy": (round(rise, 4) if rise == rise else None),
        "scramble_rise_minus_legacy": (round(scr_rise, 4) if scr_rise == scr_rise else None),
        "random_occ_tie_acc": rnd, "mean_cv_lambda": (round(mean_lambda, 4) if mean_lambda == mean_lambda else None),
        "sr_not_degenerate": sr_nondegen, "gold_only_preserved": bool(gold_only >= GOLD_ONLY_FLOOR),
        "n_tie": n_tie, "repro_ok": repro_ok, "repro_target": repro_target, "buckets_match": buckets_match,
        "bands": {"hard_pass": hard_pass, "hard_fail": hard_fail, "middle_band": middle,
                  "scramble_artifact": scramble_artifact, "guardrails_ok": guardrails_ok},
    }


# ===========================================================================
# I/O helpers
# ===========================================================================
def _write_metrics_atomic(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, "metrics.json")
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, sort_keys=True)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, expected_n_units: int) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected_n_units,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_crash_metrics(output_dir: str, exc: BaseException) -> None:
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": round(time.perf_counter() - _T0[0], 1), "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


# ===========================================================================
# self-test: mechanism discriminator (planted graph, GloVe-free) + real_code_path (real DerivationReasoner).
# ===========================================================================
def _self_test() -> None:
    print("[self-test] SR mechanism discriminator (planted graph) ...", flush=True)
    # planted graph: given g0. gold reachable by TWO short forward paths (high occupancy); distractor
    # reachable by ONE longer thinner path (low occupancy). Both co-derivable (tie).
    #   nodes: 0=given, 1=a, 2=b, 3=gold, 4=c, 5=dist
    #   edges: 0->1, 0->2, 1->3, 2->3 (gold: 2 paths of len2) ; 0->4, 4->5 (dist: 1 path of len2)
    n = 6
    fwd = {0: {1, 2, 4}, 1: {3}, 2: {3}, 4: {5}}
    sr = SRSolver(build_transition_from_fwd(fwd, n))
    given = {0}
    cand_gold = [{3}]
    cand_dist = [{5}]
    occ_gold = occ_for_candidates(sr, given, cand_gold, SR_GAMMA_PRIMARY)[0]
    occ_dist = occ_for_candidates(sr, given, cand_dist, SR_GAMMA_PRIMARY)[0]
    assert occ_gold > occ_dist > 0.0, "planted SR must rank the multi-path gold above the single-path dist (%.4f vs %.4f)" % (occ_gold, occ_dist)
    M = sr.full(SR_GAMMA_PRIMARY)
    col_std = float(np.std(M, axis=0).mean())
    assert col_std >= SR_DEGEN_STD_MIN, "planted SR column must be non-degenerate"
    print("[self-test] SR discriminates: occ(gold)=%.4f > occ(dist)=%.4f ; col_std=%.4g" % (occ_gold, occ_dist, col_std), flush=True)

    # planted tie bucket: 40 ties where occ perfectly separates gold; combiner is NOISE.
    rng = np.random.default_rng(0)
    tie_qs = []
    for _i in range(40):
        # 3 valid candidates; gold is index0 with high occ, others low occ; combiner random (uninformative)
        vrecs = []
        for k in range(3):
            is_gold = (k == 0)
            vrecs.append({"choice_index": k, "is_gold": is_gold, "givens_covered": 0.5, "chain_len": 2,
                          "combiner_score": float(rng.random()), "chain_relations": ["CAUSE"], "term_rel": "CAUSE",
                          "occ_real": (0.9 if is_gold else 0.1 + 0.05 * rng.random()),
                          "occ_scr": float(rng.random()),        # scrambled: uninformative
                          "occ_rnd": float(rng.random())})       # random: uninformative
        tie_qs.append({"qid": "T%d" % _i, "correct_index": 0, "intent": set(), "valid": vrecs})

    legacy_acc = float(np.mean([_decide_legacy(q["valid"]) for q in tie_qs]))
    sr_only_acc = float(np.mean([_decide_gated(q["valid"], "occ_real", 1.0) for q in tie_qs]))
    cv_real = cv_lambda_select(tie_qs, "occ_real", LAMBDA_GRID, N_FOLDS, 1)
    cv_scr = cv_lambda_select(tie_qs, "occ_scr", LAMBDA_GRID, N_FOLDS, 1)
    cv_rnd = cv_lambda_select(tie_qs, "occ_rnd", LAMBDA_GRID, N_FOLDS, 1)
    print("[self-test] planted tie: LEGACY=%.3f SR_ONLY=%.3f SR_GATED(cv)=%.3f(lam*=%.2f) SCR=%.3f RAND=%.3f"
          % (legacy_acc, sr_only_acc, cv_real["cv_acc"], cv_real["mean_lambda"], cv_scr["cv_acc"], cv_rnd["cv_acc"]), flush=True)
    assert sr_only_acc >= 0.95, "SR_ONLY must solve the planted tie (occ separates gold)"
    assert cv_real["cv_acc"] >= 0.90, "SR_GATED CV must recover the planted signal"
    assert cv_real["mean_lambda"] > 0.15, "gate must lean on SR when SR is the informative channel (lam*=%.3f)" % cv_real["mean_lambda"]
    assert cv_real["cv_acc"] - legacy_acc >= 0.30, "gated must beat cosine-only legacy on the planted tie"
    assert cv_scr["cv_acc"] - legacy_acc <= 0.10, "SCRAMBLE must stay near legacy (must-fail control)"
    assert cv_rnd["cv_acc"] - legacy_acc <= 0.10, "RANDOM_OCC must stay near legacy (must-fail control)"

    # arms-differ (decision signatures distinct on the planted tie set)
    sigs = {}
    for arm, fn in [(LEGACY, lambda q: _decide_legacy(q["valid"])),
                    (SR_ONLY, lambda q: _decide_gated(q["valid"], "occ_real", 1.0)),
                    (SR_GATED, lambda q: _decide_gated(q["valid"], "occ_real", 0.5)),
                    (SR_SCRAMBLED, lambda q: _decide_gated(q["valid"], "occ_scr", 1.0)),
                    (RANDOM_OCC, lambda q: _decide_gated(q["valid"], "occ_rnd", 1.0))]:
        vec = np.asarray([fn(q) for q in tie_qs], dtype=np.int64)
        sigs[arm] = hashlib.sha256(vec.tobytes()).hexdigest()[:16]
    assert len(set(sigs.values())) >= 3, "arms must differ on the planted tie set (got %s)" % sigs

    # real_code_path: construct the REAL DerivationReasoner (GloVe-free FakeBase) + run bucket/SR wiring.
    print("[self-test] real_code_path: building REAL DerivationReasoner (GloVe-free) ...", flush=True)
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon, _load_wordnet
    base = clean._FakeBase()
    wn = _load_wordnet()
    pol = PolarityLexicon()
    rows = [
        {"relation": "CAUSE", "arg0": "rain", "arg1": "runoff"},
        {"relation": "SOURCEOF", "arg0": "runoff", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "rain", "arg1": "river"},
        {"relation": "CAUSE", "arg0": "volcano", "arg1": "lava"},
    ]
    r = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, tau_unify=0.99, tau_sim=0.5,
                           depth=3, rows=rows, link_mode="lemma_syn", verbose=False)
    n_nodes = r.g["n_nodes"]
    sr_real = SRSolver(build_transition_from_fwd(r.arms["typed"]["fwd"], n_nodes))
    sr_scr = SRSolver(build_transition_from_fwd(
        scramble_fwd_degree_preserving(r.arms["typed"]["fwd"], n_nodes, np.random.default_rng(1)), n_nodes))
    q = {"qid": "RT1", "stem": "what does rain produce that feeds",
         "choices": ["river water body", "lava rock", "metal wire", "glass sheet"], "correct_index": 0}
    out = evaluate_config(r, [q], "lemma_syn", sr_real, sr_scr, seed=1,
                          output_dir=os.path.join(_REPO, "data", "_sr_tiebreak_selftest_scratch"))
    assert out["n_questions"] == 1, "real_code_path evaluate_config must run"
    assert sum(out["buckets"].values()) == 1, "buckets must sum to n_questions"
    assert "coverage_diagnostic" in out and "sr_sanity" in out, "coverage + sanity must be reported"
    print("[self-test] real_code_path buckets=%s sr_sanity.reach_density=%.3f" % (
        out["buckets"], out["sr_sanity"]["graph_reach_density"]), flush=True)
    print("[self-test] ALL PASS", flush=True)


# ===========================================================================
# main run
# ===========================================================================
def run(output_dir: str, n_sample: int, link_modes: List[str], seed: int, run_mode: str) -> dict:
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, run_mode, len(link_modes))
    _write_metrics_atomic(output_dir, {"verdict": "RUNNING", "anchor_name": ANCHOR_NAME,
                                       "ts_iso": datetime.now(timezone.utc).isoformat()})
    _log("run_mode=%s n_sample=%d link_modes=%s" % (run_mode, n_sample, link_modes))

    from experiments.exp_semantic_hd_encoder_meaning_match_v1 import SemanticHDEncoder
    from experiments.exp_arc_aggregation_polarity_ci_v1 import PolarityLexicon

    rows = _load_rules(RULES_PATH)
    _log("rules loaded: n_rules=%d from %s" % (len(rows), os.path.basename(RULES_PATH)))

    base = SemanticHDEncoder()
    pol = PolarityLexicon()
    wn = base._wn
    _log("encoder ready (%.1fs)" % (time.perf_counter() - _T0[0]))

    reasoner = DerivationReasoner(base_encoder=base, pol_lexicon=pol, wn=wn, seed=seed, rows=rows,
                                  tiebreak_mode="legacy", verbose=False)
    g = reasoner.g
    _log("graph built: n_nodes=%d n_typed_edges=%d max_deg=%d mean_out_deg=%.3f" % (
        g["n_nodes"], g["n_typed_edges"], g["max_typed_node_degree"],
        g["n_typed_edges"] / max(1, g["n_nodes"])))

    # SR solvers (graph-only, link_mode-invariant): real + degree-preserving scramble.
    n_nodes = g["n_nodes"]
    sr_solver = SRSolver(build_transition_from_fwd(reasoner.arms["typed"]["fwd"], n_nodes))
    sr_solver_scr = SRSolver(build_transition_from_fwd(
        scramble_fwd_degree_preserving(reasoner.arms["typed"]["fwd"], n_nodes,
                                       np.random.default_rng(seed * 31 + 7)), n_nodes))

    all_q = arc._load_questions(arc._CHAL_TEST, limit=0)
    if n_sample and n_sample < len(all_q):
        rng = np.random.default_rng(seed)
        idx = sorted(rng.permutation(len(all_q))[:n_sample].tolist())
        questions = [all_q[i] for i in idx]
    else:
        questions = all_q
    _log("questions: total=%d eval=%d" % (len(all_q), len(questions)))

    per_config = {}
    verdicts = {}
    for lm in link_modes:
        t_c = time.perf_counter()
        cfg_res = evaluate_config(reasoner, questions, lm, sr_solver, sr_solver_scr, seed, output_dir)
        per_config[lm] = cfg_res
        verdicts[lm] = verdict_for_config(cfg_res)
        _log("config %s done (%.1fs) verdict=%s" % (lm, time.perf_counter() - t_c, verdicts[lm]["verdict"]))

    primary = "lemma_syn" if "lemma_syn" in link_modes else link_modes[0]
    pv = verdicts[primary]
    pc = per_config[primary]
    at = pc["arm_tie_acc"]

    summary = (
        "SR-gated ARC tie-break [%s]: TIE n=%d | LEGACY=%.4f SYMBOLIC=%.4f SR_ONLY=%s SR_GATED=%s "
        "(rise=%s, lam*=%s) SR_SCR=%s RAND=%s | SR non-degen=%s (tie_occ_std=%.2g) | gold_only>=0.95=%s | "
        "coverage(dist_only n=%d): LINK=%s DEPTH_BLOCKED=%s STRUCT_ABSENT=%s | %s" % (
            primary, pc["n_tie"], at[LEGACY], at[SYMBOLIC], _fmt(at[SR_ONLY]), _fmt(at[SR_GATED]),
            _fmt(pv["tie_rise_gated_minus_legacy"]), _fmt(pv["mean_cv_lambda"]), _fmt(at[SR_SCRAMBLED]),
            _fmt(at[RANDOM_OCC]), pc["sr_sanity"]["sr_not_degenerate"], pc["sr_sanity"]["tie_occ_std_mean"],
            pv["gold_only_preserved"], pc["coverage_diagnostic"]["n_dist_only"],
            pc["coverage_diagnostic"]["counts"]["LINK_FAILURE"],
            pc["coverage_diagnostic"]["counts"]["DEPTH_BLOCKED"],
            pc["coverage_diagnostic"]["counts"]["STRUCTURALLY_ABSENT"], pv["verdict"]))
    _log("SUMMARY: %s" % summary)

    metrics = {
        "REQUIRED_FIELDS": ["verdict", "tier", "per_config", "verdicts", "coverage_diagnostic",
                            "sr_sanity", "arm_tie_acc", "preregistered_bands", "prereg_thresholds"],
        "anchor_name": ANCHOR_NAME, "verdict": pv["verdict"], "tier": "VET_PENDING",
        "summary": summary, "run_mode": run_mode, "primary_config": primary,
        "verdict_msg": (
            "First honest ARC-facing test of the prior HARD_PASS SR-routing + gated-fusion mechanisms wired "
            "to the DerivationReasoner tie-break: does an SR graph-support-strength channel (M[given,candidate] "
            "= discounted forward occupancy, gamma=0.85 pre-registered), gated vs the existing cosine combiner "
            "by 5-fold CV lambda, resolve the co-derivable ARC ties where symbolic tie-break measured d=0.000? "
            "ONE variable = the tie-break decision (graph/link/CI/do identical across arms). Must-fail controls "
            "= degree-preserving graph scramble + i.i.d. random occupancy (both must stay flat). SR "
            "non-degeneracy reported BEFORE the tie result (mean out-degree<1 -> honest degeneracy risk pre-"
            "registered as HARD_FAIL_SR_DEGENERATE, a THIRD meaning-boundedness diagnosis not a hidden failure). "
            "Coverage diagnostic (report-only) settles whether a separate DEPTH-bump cell is worth queuing. "
            "Held-out ARC-Challenge test; rules NOT derived from test labels. INLINE-LOCAL; VET-PENDING; no bank."),
        "config": {"n_eval": len(questions), "n_total_test": len(all_q), "link_modes": link_modes,
                   "seed": seed, "gamma": SR_GAMMA_PRIMARY, "lambda_grid": LAMBDA_GRID, "n_folds": N_FOLDS,
                   "depth_bump": DEPTH_BUMP, "n_rules": len(reasoner.rows), "rules_path": RULES_PATH,
                   "one_variable_across_arms": "tie_break_decision (graph/link/CI/do identical)",
                   "comprehension": "INTERIM _content_words stand-in (situation_reader NOT adapted; P6)"},
        "graph": {"n_nodes": g["n_nodes"], "n_typed_edges": g["n_typed_edges"],
                  "mean_out_degree": round(g["n_typed_edges"] / max(1, g["n_nodes"]), 4),
                  "max_typed_node_degree": g["max_typed_node_degree"], "per_relation": reasoner.per_relation},
        "per_config": per_config, "verdicts": verdicts,
        "coverage_diagnostic": {lm: per_config[lm]["coverage_diagnostic"] for lm in link_modes},
        "sr_sanity": {lm: per_config[lm]["sr_sanity"] for lm in link_modes},
        "arm_tie_acc": {lm: per_config[lm]["arm_tie_acc"] for lm in link_modes},
        "preregistered_bands": pv["bands"],
        "prereg_thresholds": {"gold_only_floor": GOLD_ONLY_FLOOR, "n_tie_min": N_TIE_MIN,
                              "sr_degen_std_min": SR_DEGEN_STD_MIN, "tie_abs_pass": TIE_ABS_PASS,
                              "tie_rise_pass": TIE_RISE_PASS, "tie_rise_stuck": TIE_RISE_STUCK,
                              "scramble_flat_max": SCRAMBLE_FLAT_MAX, "lambda_leans_min": LAMBDA_LEANS_MIN,
                              "repro_tol": REPRO_TOL},
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "host": platform.node(),
        "contract": "INLINE-LOCAL; no push/remote-persist; VET-PENDING; no atom banking",
    }
    _write_metrics_atomic(output_dir, metrics)
    _log("done (%.1fs)" % (time.perf_counter() - _T0[0]))
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--n", type=int, default=0, help="ARC-Challenge sample size (0 = all)")
    ap.add_argument("--seed", type=int, default=SEED)
    ap.add_argument("--link-modes", type=str, default="lemma_syn,lemma")
    ap.add_argument("--out", type=str, default=os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME))
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    link_modes = [x.strip() for x in args.link_modes.split(",") if x.strip()]
    if args.mode == "smoke":
        n_sample = args.n if args.n else 150
        output_dir = args.out + "_smoke"
        link_modes = link_modes[:1]   # one config for smoke
    else:
        n_sample = args.n   # 0 = all 1172
        output_dir = args.out
    try:
        run(output_dir, n_sample, link_modes, args.seed, args.mode)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # NOT BaseException
        _write_crash_metrics(output_dir, exc)
        print("[CRASH] %s: %s" % (type(exc).__name__, exc), flush=True)
        traceback.print_exc()
        raise


if __name__ == "__main__":
    main()
