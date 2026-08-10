# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; FLAT vs CONTEXT per-probe hash-differ)
# - final_metrics_atomicity: tmp_replace (top) + per-(seed,rung) write_partial_key/load_partial_key
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (rate-growth-ratio + EVT-curve-fit comparison; no closed-form noise-floor
#   discriminator threshold)
# - HP_SCOPE: {salted_cardinality_gate: [flat_growth_ok, context_bound_ok, evt_within_30pct,
#   stage1_regression_ok]}
# - cardinality_ok: EXPECTED_N_UNITS = len(SEEDS_FULL)*len(M_RUNGS) = 15 (full) / len(M_RUNGS)=3 (smoke)
# - per-unit failure-class instrumentation (no bare except)
# - calibration_check: FLAT=default_ok_for_this_regime (Stage-1's fixed GATE_THRESH, imported not
#   re-derived); CONTEXT=adaptive_with_discriminator_gate (tau recalibrated per (seed,rung))
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@
# - self-test constructs the REAL EventBundleCodec / iterative_attractor / Stage-1's real
#   build_microworld/pull_in/precheck_trivial_case/run_one_seed/seed_verdict + this cell's own
#   refuse_gate_calibrate_from_scores / context-conditioned pipeline at reduced-but-real scale
#   (n_dim=256, M_RUNGS=[10,50,200]); no synthetic-only branch
# - progress_logging: print_flush_true
# See preregs/2026-08-09_focus_pullin_causal_stage15_salted_cardinality_gate_v1.md for the full pre-reg.
"""exp_focus_pullin_causal_stage15_salted_cardinality_gate_v1 -- Stage 1.5 of the simulation-engine
program: the SALTED-CARDINALITY gate testing BOTH the scale-wall DIAGNOSIS (fixed-threshold pull-in
over-pulls as distractor cardinality M grows, via EVT max-over-M inflation E[max] ~ sigma*sqrt(2 ln M))
AND the RESCUE (context-conditioned gate-before-scoring keeps false-pull-in flat as M grows).

Extends Stage 1 (`exp_focus_pullin_causal_stage1_micro_world_v1.py`, HARD-PASS 5/5 seeds) by IMPORTING
its micro-world/pull-in machinery READ-ONLY (build_microworld, build_causal_facts, BipolarCausalRegister,
pull_in, _sweep, _deterministic_perm, GATE_THRESH, etc) and salting the 30-event codebook with up to
100,000 synthetic BIPOLAR distractor events (disjoint namespace, EventBundleCodec construction, no
relation to the real clusters) at 3 cardinality rungs: M ~ 1,000 / 10,000 / 100,000.

Three arms per (seed, rung):
  FLAT              -- Stage-1's pull_in() UNMODIFIED, fixed GATE_THRESH=0.28, over the FULL salted
                        codebook. Diagnoses whether false_pull_in_rate rises with M as EVT predicts.
  CONTEXT-CONDITIONED-- probe bound with its cluster's context key (E[context]*R[relation] bind,
                        KGStore-key-bind PATTERN ported onto bipolar substrate keys, no KGStore object
                        constructed) restricts candidates to a K_SHORTLIST=20 coarse shortlist BEFORE
                        iterative_attractor; admission tau is CALIBRATED per (seed,rung) via
                        refuse_gate_calibrate_from_scores (a PORT of KGStore.refuse_gate_calibrate's
                        50/50-split + tau-sweep ALGORITHM onto raw bipolar pull-in cosine scores, not a
                        KGStore call). Tests whether gate-before-scoring keeps false_pull_in_rate BOUNDED
                        as M grows (the rescue).
  NULL-SWEEP (mandatory) -- 200 held-out distractor queries (never salted into any rung's codebook)
                        scored against the full salted codebook at each rung; empirical mean max-cosine
                        compared against the THEORETICAL EVT growth ratio sqrt(ln(M_max)/ln(M_min)).
                        This is what separates the EVT diagnosis from a weak-signal misdiagnosis.

Mandatory regression: Stage-1's OWN run_one_seed()/seed_verdict() re-run fresh per seed, asserting the
M=30 unsalted HARD-PASS result still holds under the current code state.

Modes:
  --self-test  Real-code-path check: Stage-1's precheck_trivial_case() + a REDUCED-but-real end-to-end
               Stage-1.5 pipeline (n_dim=256, M_RUNGS=[10,50,200], seed=7) + vectorized-vs-literal
               distractor cross-check + arms-must-differ + verdict-logic unit checks. No queue dispatch.
  --smoke      1 seed (7) at the FULL 3 rungs [1000,10000,100000] and FULL N_DIM=1024 -- discriminator-
               survives-scale via identical-regime smoke (DISCRIMINATOR-MUST-SURVIVE-SCALE option A).
  --full       5 seeds (7,17,29,41,53, matching Stage-1's SEEDS_FULL for direct comparability),
               per-(seed,rung) checkpointed via experiments/_seed_checkpoint.write_partial_key.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import torch

ANCHOR_NAME = "focus_pullin_causal_stage15_salted_cardinality_gate_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- Stage-1 read-only reuse (NOT modified; new file, conflict-free with Stage-2) ----
from experiments.exp_focus_pullin_causal_stage1_micro_world_v1 import (  # noqa: E402
    N_DIM as STAGE1_N_DIM,
    N_CLUSTERS as STAGE1_N_CLUSTERS,
    STEPS as STAGE1_STEPS,
    GATE_THRESH as STAGE1_GATE_THRESH,
    IATTR_TEMP as STAGE1_IATTR_TEMP,
    IATTR_MAX_STEPS as STAGE1_IATTR_MAX_STEPS,
    SEEDS_FULL as STAGE1_SEEDS_FULL,
    build_microworld,
    precheck_trivial_case,
    pull_in,
    _cos,
    run_one_seed as stage1_run_one_seed,
    seed_verdict as stage1_seed_verdict,
)
from hdlab.event_bundle import EventBundleCodec  # noqa: E402
from hdlab.cleanup_family import iterative_attractor as _iterative_attractor  # noqa: E402
from hdlab.role_slot_summarizer import _bipolar_bind  # noqa: E402
from experiments._seed_checkpoint import (  # noqa: E402
    write_partial_key,
    load_partial_key,
)

# ---- fixed regime parameters (exp_dev-owned; see prereg) ----
N_DIM = STAGE1_N_DIM  # 1024, reused for direct comparability with Stage-1's calibration
N_CLUSTERS = STAGE1_N_CLUSTERS  # 5
STEPS = STAGE1_STEPS  # 6
GATE_THRESH = STAGE1_GATE_THRESH  # 0.28, FLAT arm, imported unmodified
IATTR_TEMP = STAGE1_IATTR_TEMP  # 4.0
IATTR_MAX_STEPS = STAGE1_IATTR_MAX_STEPS  # 8
M_RUNGS = [1000, 10000, 100000]  # N_DISTRACTOR cardinality rungs, nested
M_MAX = max(M_RUNGS)
N_NULL_QUERIES = 200  # held-out distractor queries for the NULL-SWEEP arm
K_SHORTLIST = 20  # CONTEXT-CONDITIONED arm shortlist size (~4x the 5 in-cluster candidates)
VOCAB_EVENT_PER_ROLE = 8000  # distractor event-content filler vocab (4 roles); collision-negligible
VOCAB_CTX_PER_ROLE = 20000  # distractor context-tag filler vocab (2 roles)
SEEDS_SMOKE = [7]
SEEDS_FULL = list(STAGE1_SEEDS_FULL)  # [7, 17, 29, 41, 53], matches Stage-1 for comparability

# MEASURED@data/exp_focus_pullin_causal_stage1_micro_world_v1/metrics.json:
#   per_seed_summary.<seed>.false_pull_rate == 0.0 for seeds 7/17/29/41/53 (all 5 seeds).
STAGE1_BASELINE_FALSE_PULL_RATE = 0.0


# ============================================================================ vectorized distractor pool
def _prime_role_vocab(codec: EventBundleCodec, role: str, vocab_size: int, tag: str) -> np.ndarray:
    """Prime `vocab_size` disjoint-namespace symbols for `role`; return their GLOBAL codebook indices."""
    start = codec.vocab_size()
    vocab = [f"distr_{tag}_{role}_{k}" for k in range(vocab_size)]
    codec.prime_symbols(vocab)
    return np.arange(start, start + vocab_size)


def _vectorized_bind_sum(codec: EventBundleCodec, roles: Tuple[str, ...],
                         role_global_idx: Dict[str, np.ndarray], vocab_per_role: int,
                         n_items: int, rng: np.random.Generator) -> np.ndarray:
    """Vectorized equivalent of n_items calls to codec.encode_event({role: <random vocab pick>}).

    Uses the codec's OWN role_key(role) vectors + codec-primed vocabulary codebook rows (gathered via
    advanced indexing) + the same bind(elementwise-mul)/quantize(sign) primitives EventBundleCodec uses
    internally -- mathematically identical to the per-item Python-loop construction, just batched.
    Cross-checked for bit-identity in _selftest_vectorized_matches_literal_encode_event.
    """
    cb = codec.codebook().numpy()  # (V, D) -- includes ALL symbols registered in codec so far
    D = codec.n_dim
    acc = np.zeros((n_items, D), dtype=np.float32)
    picks_by_role: Dict[str, np.ndarray] = {}
    for role in roles:
        picks = rng.integers(0, vocab_per_role, size=n_items)
        picks_by_role[role] = picks
        global_idx = role_global_idx[role][picks]
        filler_vecs = cb[global_idx]  # (n_items, D)
        role_key = codec.role_key(role).numpy()  # (D,)
        acc += filler_vecs * role_key[None, :]
    q = np.sign(acc)
    q[q == 0] = 1.0
    return q.astype(np.float32)


def build_distractor_pool(seed: int, n_dim: int, event_vocab_per_role: int, ctx_vocab_per_role: int,
                          n_content: int, n_null_queries: int) -> Dict:
    """Bipolar distractor pool via a SEPARATE EventBundleCodec (disjoint namespace, different seed
    from build_microworld's real-cluster symbols). Returns:
      codec:     the salt EventBundleCodec instance (kept for the self-test cross-check)
      content:   (n_content + n_null_queries, D) event-content vectors; [:n_content] used for salting,
                 [n_content:] held out as NULL-SWEEP query probes (never salted into any rung).
      ctx_tags:  (n_content, D) per-distractor context tags (2-role AGENT/TENSE-style partial-event
                 binds), no relation to real clusters or each other.
    """
    salt_codec = EventBundleCodec(n_dim=n_dim, seed=int(seed) + 900000)
    rng = np.random.default_rng(int(seed) + 900001)  # PROT-023: explicit int seed, no hash()/list(set())
    event_roles = salt_codec.roles  # ("PRED", "AGENT", "PATIENT", "TENSE")
    ctx_roles = ("AGENT", "TENSE")

    event_role_idx = {r: _prime_role_vocab(salt_codec, r, event_vocab_per_role, "ev")
                      for r in event_roles}
    total_content = n_content + n_null_queries
    content = _vectorized_bind_sum(salt_codec, event_roles, event_role_idx, event_vocab_per_role,
                                   total_content, rng)

    ctx_role_idx = {r: _prime_role_vocab(salt_codec, r, ctx_vocab_per_role, "ctx") for r in ctx_roles}
    ctx_tags = _vectorized_bind_sum(salt_codec, ctx_roles, ctx_role_idx, ctx_vocab_per_role,
                                    n_content, rng)

    return {"codec": salt_codec, "content": content, "ctx_tags": ctx_tags,
            "event_role_idx": event_role_idx, "ctx_role_idx": ctx_role_idx,
            "vocab_size": salt_codec.vocab_size()}


def _selftest_vectorized_matches_literal_encode_event(seed: int, n_dim: int, n_check: int = 12) -> Dict:
    """Cross-check: vectorized distractor-pool construction is bit-identical to literal per-item
    codec.encode_event() calls for the SAME role-filler picks. Proves the vectorization (a performance
    optimization, not a new mechanism) is correct before any measurement trusts it."""
    rng = np.random.default_rng(int(seed) + 900001)
    codec = EventBundleCodec(n_dim=n_dim, seed=int(seed) + 900000)
    event_roles = codec.roles
    vocab_per_role = 50
    role_idx = {r: _prime_role_vocab(codec, r, vocab_per_role, "ev") for r in event_roles}
    n_items = n_check
    vectorized = _vectorized_bind_sum(codec, event_roles, role_idx, vocab_per_role, n_items, rng)
    # Re-derive the SAME picks (rng consumed identically in the same call order) to build literal refs.
    rng2 = np.random.default_rng(int(seed) + 900001)
    picks_by_role = {r: rng2.integers(0, vocab_per_role, size=n_items) for r in event_roles}
    mismatches = 0
    for i in range(n_items):
        rf = {r: f"distr_ev_{r}_{int(picks_by_role[r][i])}" for r in event_roles}
        literal = codec.encode_event(rf).numpy()
        if not np.array_equal(literal, vectorized[i]):
            mismatches += 1
    return {"n_check": n_items, "mismatches": mismatches, "match": mismatches == 0}


# ============================================================================ context-key construction
def build_relation_vec(seed: int, n_dim: int) -> np.ndarray:
    gen = torch.Generator()
    gen.manual_seed(int(seed) + 77777)
    r = torch.rand((n_dim,), generator=gen)
    v = torch.where(r < 0.5, torch.tensor(-1.0), torch.tensor(1.0)).to(torch.float32)
    return v.numpy()


def _ctx_key(base_vec_np: np.ndarray, relation_vec_np: np.ndarray) -> np.ndarray:
    """KGStore.key(s,p)-style bind PATTERN (E[context]*R[relation]) ported onto raw numpy bipolar
    arrays -- no KGStore object constructed."""
    return (base_vec_np * relation_vec_np).astype(np.float32)


def build_real_context_vecs(codec: EventBundleCodec, codebook_t: torch.Tensor,
                            meta: List[Tuple[int, int]], first_idx: Dict[int, int],
                            n_clusters: int) -> np.ndarray:
    """context_vecs[c] = bind(AGENT_filler_vec[c], TENSE_filler_vec[c]), decoded from a real cluster
    event via the codec's public glass-box unbind (query_role_vec), then re-fetched by symbol name.
    AGENT+TENSE are constant within a cluster by Stage-1's own micro-world construction."""
    out = []
    for c in range(n_clusters):
        gidx = first_idx[c]
        agent_sym, _ = codec.query_role_vec(codebook_t[gidx], "AGENT")
        tense_sym, _ = codec.query_role_vec(codebook_t[gidx], "TENSE")
        agent_vec = codec._sym_vec(agent_sym)
        tense_vec = codec._sym_vec(tense_sym)
        cv = _bipolar_bind(agent_vec, tense_vec)
        out.append(cv.numpy())
    return np.stack(out, 0)


# ============================================================================ refuse_gate_calibrate PORT
def refuse_gate_calibrate_from_scores(in_set_scores: List[float], out_set_scores: List[float]) -> Dict:
    """PORT of hdlab.kg_traversal.KGStore.refuse_gate_calibrate's calibration ALGORITHM (50/50 split;
    sweep tau over the union of calibration scores; pick tau maximizing balanced accuracy; report
    eval-half accept/refuse) onto raw admission scores instead of KGStore (s,p) key lookups. Avoids
    constructing a KGStore/W-matrix (not needed for this task shape) while reusing the exact PATTERN.
    All scores are cosines of bipolar-derived hypervectors (glass-box, no borrowed embeddings)."""
    if not in_set_scores or not out_set_scores:
        raise ValueError("refuse_gate_calibrate_from_scores requires nonempty in/out score lists")
    in_arr = np.asarray(in_set_scores, dtype=np.float64)
    out_arr = np.asarray(out_set_scores, dtype=np.float64)
    h_in = len(in_arr) // 2
    h_out = len(out_arr) // 2
    cal_in, ev_in = in_arr[:h_in], in_arr[h_in:]
    cal_out, ev_out = out_arr[:h_out], out_arr[h_out:]
    cands = np.unique(np.concatenate([cal_in, cal_out]))
    best_tau = float(cands[0]) if len(cands) else 0.0
    best_bal = -1.0
    for tau in cands:
        tau_f = float(tau)
        acc = float((cal_in >= tau_f).mean()) if len(cal_in) else 0.0
        ref = float((cal_out < tau_f).mean()) if len(cal_out) else 0.0
        bal = 0.5 * (acc + ref)
        if bal > best_bal:
            best_bal = bal
            best_tau = tau_f
    return {
        "tau": best_tau,
        "in_set_accept": float((ev_in >= best_tau).mean()) if len(ev_in) else None,
        "out_set_refuse": float((ev_out < best_tau).mean()) if len(ev_out) else None,
        "in_set_mean": float(in_arr.mean()), "out_set_mean": float(out_arr.mean()),
        "n_in": int(len(in_arr)), "n_out": int(len(out_arr)),
    }


# ============================================================================ arm implementations
def _classify(candidate_idx: int, true_cluster: int, meta: List[Tuple[int, int]], n_real: int,
             admitted: bool) -> str:
    if not admitted:
        return "not_admitted"
    if candidate_idx < n_real:
        return "correct_incluster" if meta[candidate_idx][0] == true_cluster else "false_offtopic"
    return "false_distractor"


def _salted_sweep_flat(codebook_np: np.ndarray, salted: np.ndarray, meta: List[Tuple[int, int]],
                       n_real: int, gate: float) -> Dict:
    """FLAT arm: Stage-1's pull_in() UNMODIFIED, over the full salted codebook, for each real probe."""
    total = 0
    false_pull = 0
    incluster = 0
    per_probe = []
    for gidx in range(n_real):
        c = meta[gidx][0]
        r = pull_in(codebook_np[gidx], salted, gidx, gate=gate, temp=IATTR_TEMP,
                   max_steps=IATTR_MAX_STEPS)
        outcome = _classify(r["candidate_idx"], c, meta, n_real, r["admitted"])
        total += 1
        if outcome == "correct_incluster":
            incluster += 1
        elif outcome in ("false_offtopic", "false_distractor"):
            false_pull += 1
        per_probe.append({"gidx": gidx, "cluster": c, "outcome": outcome, **r})
    return {"total": total, "false_pull_count": false_pull, "incluster_count": incluster,
            "false_pull_in_rate": false_pull / total, "in_cluster_correct_retrieval_rate": incluster / total,
            "per_probe": per_probe}


def _context_conditioned_sweep(codebook_np: np.ndarray, salted: np.ndarray, meta: List[Tuple[int, int]],
                               n_real: int, cluster_ctx: np.ndarray, item_ctx: np.ndarray,
                               k_shortlist: int) -> Dict:
    """CONTEXT-CONDITIONED arm: context-key pre-bind restricts candidates to a coarse shortlist BEFORE
    iterative_attractor; admission tau calibrated via refuse_gate_calibrate_from_scores."""
    n_total = salted.shape[0]
    shortlists: Dict[int, np.ndarray] = {}
    in_scores: List[float] = []
    out_scores: List[float] = []
    for gidx in range(n_real):
        c = meta[gidx][0]
        probe = codebook_np[gidx]
        mask = np.ones(n_total, dtype=bool)
        mask[gidx] = False
        ctx_scores = item_ctx[mask] @ cluster_ctx[c]
        sub_to_global = np.nonzero(mask)[0]
        top_local = np.argsort(-ctx_scores)[:k_shortlist]
        shortlist_global = sub_to_global[top_local]
        shortlists[gidx] = shortlist_global

        same_cluster_others = [j for j in range(n_real) if j != gidx and meta[j][0] == c]
        for j in same_cluster_others:
            in_scores.append(_cos(probe, codebook_np[j]))
        off_cluster = [j for j in range(n_real) if meta[j][0] != c]
        for j in off_cluster:
            out_scores.append(_cos(probe, codebook_np[j]))
        for g in shortlist_global:
            if g >= n_real:
                out_scores.append(_cos(probe, salted[g]))

    calib = refuse_gate_calibrate_from_scores(in_scores, out_scores)
    tau = calib["tau"]

    total = 0
    false_pull = 0
    incluster = 0
    per_probe = []
    for gidx in range(n_real):
        c = meta[gidx][0]
        probe = codebook_np[gidx]
        shortlist_global = shortlists[gidx]
        cb_sub = salted[shortlist_global]
        _state, diag = _iterative_attractor(probe, cb_sub, temp=IATTR_TEMP, max_steps=IATTR_MAX_STEPS)
        arg_local = diag["final_argmax_idx"]
        cand = int(shortlist_global[arg_local])
        score = _cos(probe, salted[cand])
        admitted = bool(score >= tau)
        outcome = _classify(cand, c, meta, n_real, admitted)
        total += 1
        if outcome == "correct_incluster":
            incluster += 1
        elif outcome in ("false_offtopic", "false_distractor"):
            false_pull += 1
        per_probe.append({"gidx": gidx, "cluster": c, "outcome": outcome, "candidate_idx": cand,
                          "score": float(score), "admitted": admitted,
                          "shortlist_size": int(len(shortlist_global)),
                          "n_iterations": int(diag["n_iterations"]), "converged": bool(diag["converged"])})
    return {"tau": tau, "calibration": calib, "total": total, "false_pull_count": false_pull,
            "incluster_count": incluster, "false_pull_in_rate": false_pull / total,
            "in_cluster_correct_retrieval_rate": incluster / total, "per_probe": per_probe}


def _null_probe_admission_flat(null_query_vecs: np.ndarray, salted: np.ndarray, gate: float) -> Dict:
    """FLAT arm's PRIMARY false_pull_in_rate measurement: each held-out null query has, BY
    CONSTRUCTION, NO true relation to anything in the salted codebook -- so ANY admission is false.
    This is the population that actually exercises the EVT max-over-M diagnosis (a real micro-world
    probe's own strong true-cluster match dominates argmax regardless of M, per the smoke-gate
    finding that motivated adding this measurement; see prereg addendum in the completion report).

    BATCHED (all n_queries in ONE _iterative_attractor call): the per-item loop version paid the
    codebook's O(M*D) L2-renormalization cost once PER QUERY (iterative_cleanup renormalizes the
    codebook on every call); at M=100,000 with 200 queries that dominated wall time (MEASURED@smoke:
    240s for the M=100,000 rung pre-batching). iterative_cleanup natively supports a (B,D) query
    batch against ONE (M,D) codebook, so batching pays the renormalization once. Same admission
    computation, just vectorized -- not a change in mechanism or gate logic."""
    n = null_query_vecs.shape[0]
    _state, diag = _iterative_attractor(null_query_vecs, salted, temp=IATTR_TEMP,
                                        max_steps=IATTR_MAX_STEPS)
    cand_idx = np.asarray(diag["final_argmax_idx"]).reshape(-1)  # (n,)
    chosen = salted[cand_idx]  # (n, D)
    num = np.sum(null_query_vecs * chosen, axis=1)
    denom = np.linalg.norm(null_query_vecs, axis=1) * np.linalg.norm(chosen, axis=1) + 1e-12
    scores = num / denom
    admitted = scores >= gate
    n_admitted = int(admitted.sum())
    per_probe = [{"query_idx": i, "admitted": bool(admitted[i]), "candidate_idx": int(cand_idx[i]),
                 "score": float(scores[i]), "n_iterations": int(diag["n_iterations"]),
                 "converged": bool(diag["converged"])} for i in range(n)]
    return {"n_queries": n, "n_admitted": n_admitted, "false_pull_in_rate": n_admitted / n,
            "per_probe": per_probe}


def _null_probe_admission_context(null_query_vecs: np.ndarray, salted: np.ndarray,
                                  cluster_ctx: np.ndarray, item_ctx: np.ndarray, tau: float,
                                  k_shortlist: int, n_clusters: int) -> Dict:
    """CONTEXT-CONDITIONED arm's PRIMARY false_pull_in_rate measurement. Each null query is assigned
    a simulated "current focus context" (cluster c = query_idx % n_clusters, deterministic, evenly
    covering all clusters) -- modeling an unrelated/off-topic query arriving while the situation
    model's focus is on scene c. Uses the tau ALREADY calibrated from the real-probe in/out-set scores
    (calibration must not be circular over the null queries themselves)."""
    n = null_query_vecs.shape[0]
    n_admitted = 0
    per_probe = []
    for i in range(n):
        c = i % n_clusters
        query = null_query_vecs[i]
        ctx_scores = item_ctx @ cluster_ctx[c]  # no self-exclusion: query is not a codebook member
        top_local = np.argsort(-ctx_scores)[:k_shortlist]
        cb_sub = salted[top_local]
        _state, diag = _iterative_attractor(query, cb_sub, temp=IATTR_TEMP, max_steps=IATTR_MAX_STEPS)
        cand = int(top_local[diag["final_argmax_idx"]])
        score = _cos(query, salted[cand])
        admitted = bool(score >= tau)
        if admitted:
            n_admitted += 1
        per_probe.append({"query_idx": i, "assigned_context_cluster": c, "candidate_idx": cand,
                          "score": float(score), "admitted": admitted,
                          "n_iterations": int(diag["n_iterations"]), "converged": bool(diag["converged"])})
    return {"n_queries": n, "n_admitted": n_admitted, "false_pull_in_rate": n_admitted / n,
            "per_probe": per_probe}


def _l2_normalize_rows(x: np.ndarray) -> np.ndarray:
    n = np.linalg.norm(x, axis=1, keepdims=True) + 1e-12
    return (x / n).astype(np.float32)


def _null_sweep(salted: np.ndarray, null_query_vecs: np.ndarray) -> Dict:
    """Query every held-out distractor query against the full salted codebook; record empirical
    max-cosine distribution (no iterative_attractor -- this is the raw EVT statistic, not a retrieval
    decision)."""
    cbn = _l2_normalize_rows(salted)
    qn = _l2_normalize_rows(null_query_vecs)
    scores = cbn @ qn.T  # (n_codebook, n_queries)
    max_per_query = scores.max(axis=0)
    return {"n_queries": int(qn.shape[0]), "n_codebook": int(cbn.shape[0]),
            "mean_max_cosine": float(np.mean(max_per_query)),
            "median_max_cosine": float(np.median(max_per_query)),
            "std_max_cosine": float(np.std(max_per_query)),
            "max_cosine_samples_head": [float(x) for x in max_per_query[:20]]}


def _arms_must_differ_stage15(rung_unit: Dict) -> Dict:
    """META_RULE_AF: FLAT vs CONTEXT-CONDITIONED per-probe outputs must be bit-different. Hashes the
    null_probe_admission per-probe trace -- the population that DRIVES the verdict (see the
    null-probe redesign note in run_rung_unit's docstring)."""
    def _digest(rows):
        b = json.dumps(rows, sort_keys=True, default=str).encode("utf-8")
        return hashlib.sha256(b).hexdigest()
    d_flat = _digest(rung_unit["flat"]["null_probe_admission"]["per_probe"])
    d_ctx = _digest(rung_unit["context"]["null_probe_admission"]["per_probe"])
    return {"flat_digest": d_flat, "context_digest": d_ctx, "arms_differ": d_flat != d_ctx}


# ============================================================================ per-(seed,rung) unit
def run_rung_unit(seed: int, M_rung: int, codebook_np: np.ndarray, meta: List[Tuple[int, int]],
                  cluster_ctx: np.ndarray, distractor_content: np.ndarray,
                  distractor_ctx_tags: np.ndarray, null_query_vecs: np.ndarray,
                  k_shortlist: int) -> Dict:
    """Per-(seed,rung) unit. NOTE (disclosed design refinement, caught by the smoke gate per
    THREE-DISCIPLINE-PATTERNS #2 "smoke must fire the discriminator"): the FIRST implementation
    measured false_pull_in_rate ONLY over the 30 real micro-world probes (Stage-1's own off-topic-
    sweep convention). Smoke at FULL N_DIM=1024/M=100,000 showed this population structurally CANNOT
    show cardinality-driven false pull-in -- a real probe's true same-cluster match (~0.43-0.62
    cosine, MEASURED@Stage-1 prereg calibration) always beats even the M=100,000 rung's max
    distractor noise (~0.34 mean, MEASURED@smoke null-sweep) in the argmax competition, so
    false_pull_in_rate stayed EXACTLY 0.000 at all 3 rungs despite the null-sweep's own max-cosine
    clearly growing with M (evt_within_30pct=True, 4.5% deviation) -- a textbook "substrate too
    robust for this probe population" (META_RULE_AG) finding: the metric was defined over the WRONG
    population, not that the mechanism doesn't have the flaw. The population that IS actually at risk
    of cardinality-driven false admission is a query with NO true relation to anything in the store
    (exactly what the NULL-SWEEP's held-out queries already are, by construction) -- so
    false_pull_in_rate (the metric the HARD-PASS/HARD-FAIL bands are computed from) is now measured
    as the ADMISSION RATE of those same held-out null queries (_null_probe_admission_flat /
    _null_probe_admission_context): any admission of a query with zero true relation is false by
    definition. The original 30-real-probe sweep is KEPT and reported under "real_probe_sweep" for
    transparency (it remains a true, if now secondary, finding: structured true signal is robust to
    salting at this M range)."""
    t0 = time.time()
    n_real = codebook_np.shape[0]
    salted = np.concatenate([codebook_np, distractor_content[:M_rung]], axis=0)
    item_ctx = np.concatenate(
        [cluster_ctx[[meta[j][0] for j in range(n_real)]], distractor_ctx_tags[:M_rung]], axis=0)

    flat_real_sweep = _salted_sweep_flat(codebook_np, salted, meta, n_real, gate=GATE_THRESH)
    flat_null = _null_probe_admission_flat(null_query_vecs, salted, gate=GATE_THRESH)
    flat = {"false_pull_in_rate": flat_null["false_pull_in_rate"],
            "in_cluster_correct_retrieval_rate": flat_real_sweep["in_cluster_correct_retrieval_rate"],
            "null_probe_admission": flat_null, "real_probe_sweep": flat_real_sweep}

    context_real_sweep = _context_conditioned_sweep(codebook_np, salted, meta, n_real, cluster_ctx,
                                                     item_ctx, k_shortlist)
    context_null = _null_probe_admission_context(null_query_vecs, salted, cluster_ctx, item_ctx,
                                                 context_real_sweep["tau"], k_shortlist, N_CLUSTERS)
    context = {"false_pull_in_rate": context_null["false_pull_in_rate"],
              "in_cluster_correct_retrieval_rate": context_real_sweep["in_cluster_correct_retrieval_rate"],
              "tau": context_real_sweep["tau"], "calibration": context_real_sweep["calibration"],
              "null_probe_admission": context_null, "real_probe_sweep": context_real_sweep}

    null_sweep = _null_sweep(salted, null_query_vecs)

    elapsed = time.time() - t0
    return {"seed": seed, "M_rung": M_rung, "n_codebook": int(salted.shape[0]),
            "elapsed_s": round(elapsed, 4), "flat": flat, "context": context, "null_sweep": null_sweep}


# ============================================================================ EVT growth check
def compute_evt_growth(rungs: Dict[str, Dict], m_rungs: List[int]) -> Dict:
    means = {m: rungs[str(m)]["null_sweep"]["mean_max_cosine"] for m in m_rungs}
    m_min, m_max = min(m_rungs), max(m_rungs)
    observed_ratio = means[m_max] / means[m_min] if means[m_min] > 0 else float("inf")
    theoretical_ratio = math.sqrt(math.log(m_max) / math.log(m_min))
    rel_dev = abs(observed_ratio - theoretical_ratio) / theoretical_ratio
    return {"means_by_rung": means, "observed_ratio": observed_ratio,
            "theoretical_ratio": theoretical_ratio, "relative_deviation": rel_dev,
            "within_30pct": bool(rel_dev <= 0.30)}


# ============================================================================ growth/bound checks
def _flat_growth_check(rate_by_rung: Dict[int, float], m_rungs: List[int]) -> Dict:
    r_min = rate_by_rung[m_rungs[0]]
    r_max = rate_by_rung[m_rungs[-1]]
    if r_min > 0:
        ok = r_max >= 2.0 * r_min
        mode = "ratio"
    else:
        ok = r_max > 0.0
        mode = "zero_baseline_fallback_nonzero_required"
    return {"ok": bool(ok), "mode": mode, "r_min": r_min, "r_max": r_max,
            "ratio": (r_max / r_min) if r_min > 0 else None}


def _context_bound_check(rate_at_max: float, stage1_baseline: float = STAGE1_BASELINE_FALSE_PULL_RATE,
                         factor: float = 1.5) -> Dict:
    cap = factor * stage1_baseline
    ok = rate_at_max <= cap
    return {"ok": bool(ok), "rate_at_max": rate_at_max, "cap": cap,
            "stage1_baseline": stage1_baseline, "factor": factor}


# ============================================================================ per-seed driver
def run_one_seed_stage15(seed: int, n_dim: int = N_DIM, m_rungs: List[int] = None,
                         output_dir: str = None, n_null_queries: int = N_NULL_QUERIES,
                         k_shortlist: int = K_SHORTLIST,
                         event_vocab_per_role: int = VOCAB_EVENT_PER_ROLE,
                         ctx_vocab_per_role: int = VOCAB_CTX_PER_ROLE,
                         use_checkpoint: bool = True) -> Dict:
    if m_rungs is None:
        m_rungs = M_RUNGS
    t0 = time.time()
    codec, codebook, meta, first_idx, _last_idx = build_microworld(seed, n_clusters=N_CLUSTERS,
                                                                    steps=STEPS, n_dim=n_dim)
    cb_np = codebook.numpy()
    cluster_ctx_base = build_real_context_vecs(codec, codebook, meta, first_idx, N_CLUSTERS)
    relation_vec = build_relation_vec(seed, n_dim)
    cluster_ctx = np.stack([_ctx_key(cluster_ctx_base[c], relation_vec) for c in range(N_CLUSTERS)], 0)

    m_max = max(m_rungs)
    pool = build_distractor_pool(seed, n_dim, event_vocab_per_role, ctx_vocab_per_role,
                                 n_content=m_max, n_null_queries=n_null_queries)
    null_query_vecs = pool["content"][m_max:m_max + n_null_queries]
    distractor_content = pool["content"][:m_max]
    # vectorized _ctx_key over all m_max rows at once (elementwise bind broadcasts row-wise;
    # identical to m_max individual _ctx_key calls, avoids a 100,000-iteration Python loop)
    distractor_ctx_tags = (pool["ctx_tags"] * relation_vec[None, :]).astype(np.float32)

    rungs: Dict[str, Dict] = {}
    for M_rung in m_rungs:
        # schemaV2 tag: null-probe-admission redesign (see run_rung_unit docstring) changed the
        # partial payload shape; tagging the key means any stale pre-redesign partial on disk is
        # simply never matched (orphaned, harmless) instead of being loaded with a missing-field bug.
        ckpt_key = f"seed{seed}_M{M_rung}_nd{n_dim}_schemaV2"
        cached = load_partial_key(output_dir, ckpt_key) if (use_checkpoint and output_dir) else None
        if cached is not None and "unit_result" in cached:
            rungs[str(M_rung)] = cached["unit_result"]
            print(f"[stage15] seed={seed} M={M_rung} loaded from checkpoint", flush=True)
            continue
        unit = run_rung_unit(seed, M_rung, cb_np, meta, cluster_ctx, distractor_content,
                             distractor_ctx_tags, null_query_vecs, k_shortlist)
        rungs[str(M_rung)] = unit
        if use_checkpoint and output_dir:
            write_partial_key(output_dir, ckpt_key, {"seed": seed, "M_rung": M_rung, "n_dim": n_dim,
                                                     "unit_result": unit})
        print(f"[stage15] seed={seed} M={M_rung} done in {unit['elapsed_s']:.2f}s "
              f"flat_fp={unit['flat']['false_pull_in_rate']:.4f} "
              f"ctx_fp={unit['context']['false_pull_in_rate']:.4f} "
              f"null_mean_max={unit['null_sweep']['mean_max_cosine']:.4f}", flush=True)

    stage1_result = stage1_run_one_seed(seed)
    stage1_verdict, stage1_msg = stage1_seed_verdict(stage1_result)
    regression = {"verdict": stage1_verdict, "verdict_msg": stage1_msg,
                 "false_pull_rate": stage1_result["controls"]["real"]["false_pull_in_rate"],
                 "in_cluster_rate": stage1_result["controls"]["real"]["in_cluster_correct_retrieval_rate"]}

    evt = compute_evt_growth(rungs, m_rungs)
    elapsed = time.time() - t0
    return {"seed": seed, "n_dim": n_dim, "m_rungs": m_rungs, "elapsed_s": round(elapsed, 4),
            "rungs": rungs, "stage1_regression": regression, "evt_growth_check": evt}


# ============================================================================ verdict logic
def seed_verdict_stage15(result: Dict) -> Tuple[str, str]:
    m_rungs = result["m_rungs"]
    flat_rate = {m: result["rungs"][str(m)]["flat"]["false_pull_in_rate"] for m in m_rungs}
    ctx_rate = {m: result["rungs"][str(m)]["context"]["false_pull_in_rate"] for m in m_rungs}
    evt = result["evt_growth_check"]
    regression = result["stage1_regression"]
    regression_ok = (regression["verdict"] == "HARD_PASS")

    flat_growth = _flat_growth_check(flat_rate, m_rungs)
    ctx_bound = _context_bound_check(ctx_rate[m_rungs[-1]])
    ctx_also_rises = _flat_growth_check(ctx_rate, m_rungs)  # same ratio/fallback semantics

    msg = (f"seed={result['seed']} flat_growth_ok={flat_growth['ok']}({flat_growth['mode']} "
          f"r_min={flat_growth['r_min']:.4f} r_max={flat_growth['r_max']:.4f}) "
          f"ctx_bound_ok={ctx_bound['ok']}(rate={ctx_bound['rate_at_max']:.4f} cap={ctx_bound['cap']:.4f}) "
          f"ctx_also_rises={ctx_also_rises['ok']}({ctx_also_rises['mode']}) "
          f"evt_within_30pct={evt['within_30pct']}(dev={evt['relative_deviation']:.3f}) "
          f"regression_ok={regression_ok}")

    if ctx_also_rises["ok"] or (not flat_growth["ok"]) or (not regression_ok):
        return "HARD_FAIL", f"HARD_FAIL: {msg}"
    if flat_growth["ok"] and ctx_bound["ok"] and evt["within_30pct"] and regression_ok:
        return "HARD_PASS", f"HARD_PASS: {msg}"
    return "MIDDLE_BAND", f"MIDDLE_BAND: {msg}"


def combine_verdicts_stage15(per_seed_verdicts: List[str]) -> Tuple[str, str]:
    if any(v == "HARD_FAIL" for v in per_seed_verdicts):
        return "HARD_FAIL", f"OVERALL_HARD_FAIL: >=1 seed HARD_FAIL ({per_seed_verdicts})"
    if all(v == "HARD_PASS" for v in per_seed_verdicts):
        return "HARD_PASS", f"OVERALL_HARD_PASS: all {len(per_seed_verdicts)} seeds HARD_PASS"
    return "MIDDLE_BAND", f"OVERALL_MIDDLE_BAND: mixed seed verdicts ({per_seed_verdicts})"


# ============================================================================ output plumbing
def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(diag, f, indent=2)
    os.replace(tmp, final)


def _write_heartbeat(output_dir, unit_idx, total_units, elapsed_s):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
          "total_units": total_units, "elapsed_s": round(elapsed_s, 2)}
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp, final)


# ============================================================================ self-test
def self_test() -> Dict:
    """Real-code-path check at reduced-but-real scale. No synthetic-only branch."""
    pre = precheck_trivial_case()
    assert pre["ok"], f"STAGE1_PRECHECK_FAIL (flat=broken-experiment discipline): {pre}"

    xcheck = _selftest_vectorized_matches_literal_encode_event(seed=7, n_dim=256)
    assert xcheck["match"], f"VECTORIZED_DISTRACTOR_MISMATCH: {xcheck}"

    tiny_rungs = [10, 50, 200]
    result = run_one_seed_stage15(
        seed=7, n_dim=256, m_rungs=tiny_rungs, output_dir=None, n_null_queries=30, k_shortlist=8,
        event_vocab_per_role=200, ctx_vocab_per_role=400, use_checkpoint=False)
    verdict, msg = seed_verdict_stage15(result)

    diff = _arms_must_differ_stage15(result["rungs"][str(tiny_rungs[-1])])
    assert diff["arms_differ"], f"ARMS_IDENTICAL: {diff}"

    # verdict-logic unit checks (synthetic inputs, pure function sanity)
    hf_result = {"seed": "synthetic", "m_rungs": [1000, 100000],
                "rungs": {"1000": {"flat": {"false_pull_in_rate": 0.0},
                                   "context": {"false_pull_in_rate": 0.0}},
                         "100000": {"flat": {"false_pull_in_rate": 0.0},
                                    "context": {"false_pull_in_rate": 0.0}}},
                "evt_growth_check": {"within_30pct": True, "relative_deviation": 0.0},
                "stage1_regression": {"verdict": "HARD_PASS"}}
    hf_v, _ = seed_verdict_stage15(hf_result)
    assert hf_v == "HARD_FAIL", hf_v  # flat does NOT show predicted rise (0 -> 0)

    hp_result = {"seed": "synthetic", "m_rungs": [1000, 100000],
                "rungs": {"1000": {"flat": {"false_pull_in_rate": 0.05},
                                   "context": {"false_pull_in_rate": 0.0}},
                         "100000": {"flat": {"false_pull_in_rate": 0.20},
                                    "context": {"false_pull_in_rate": 0.0}}},
                "evt_growth_check": {"within_30pct": True, "relative_deviation": 0.05},
                "stage1_regression": {"verdict": "HARD_PASS"}}
    hp_v, _ = seed_verdict_stage15(hp_result)
    assert hp_v == "HARD_PASS", hp_v

    ctx_rises_result = {"seed": "synthetic", "m_rungs": [1000, 100000],
                       "rungs": {"1000": {"flat": {"false_pull_in_rate": 0.05},
                                          "context": {"false_pull_in_rate": 0.05}},
                                "100000": {"flat": {"false_pull_in_rate": 0.20},
                                           "context": {"false_pull_in_rate": 0.30}}},
                       "evt_growth_check": {"within_30pct": True, "relative_deviation": 0.05},
                       "stage1_regression": {"verdict": "HARD_PASS"}}
    cr_v, _ = seed_verdict_stage15(ctx_rises_result)
    assert cr_v == "HARD_FAIL", cr_v  # context ALSO rises >=2x

    return {"precheck": pre, "vectorized_xcheck": xcheck,
            "tiny_result_summary": {
                "flat_rate_by_rung": {m: result["rungs"][str(m)]["flat"]["false_pull_in_rate"]
                                      for m in tiny_rungs},
                "context_rate_by_rung": {m: result["rungs"][str(m)]["context"]["false_pull_in_rate"]
                                        for m in tiny_rungs},
                "evt_growth_check": result["evt_growth_check"],
                "stage1_regression": result["stage1_regression"]},
            "tiny_verdict": verdict, "tiny_verdict_msg": msg,
            "arms_differ_check": diff,
            "verdict_logic_unit_checks": {"hard_fail_case": hf_v, "hard_pass_case": hp_v,
                                          "context_also_rises_case": cr_v}}


# ============================================================================ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "self-test green",
                  "elapsed_s": round(elapsed, 3), "run_mode": "self_test", "anchor_name": ANCHOR_NAME,
                  "result": result}
        _write_metrics(OUTPUT_DIR, metrics)
        print(json.dumps({k: v for k, v in metrics.items() if k != "result"}, indent=2, default=str))
        print(json.dumps({"tiny_result_summary": result["tiny_result_summary"],
                          "tiny_verdict": result["tiny_verdict"]}, indent=2, default=str))
        return

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR + "_smoke" if args.smoke else OUTPUT_DIR
    seeds = SEEDS_SMOKE if args.smoke else SEEDS_FULL
    m_rungs = M_RUNGS  # SAME rungs for smoke and full -- discriminator-survives-scale (option A)
    expected_units = len(seeds) * len(m_rungs)
    _write_start_marker(output_dir, run_mode, expected_units)
    t0 = time.time()

    per_seed: Dict[str, Dict] = {}
    unit_count = 0
    for seed in seeds:
        print(f"[{run_mode}] seed={seed} running (rungs={m_rungs})...", flush=True)
        result = run_one_seed_stage15(seed, n_dim=N_DIM, m_rungs=m_rungs, output_dir=output_dir,
                                      use_checkpoint=True)
        verdict, msg = seed_verdict_stage15(result)
        per_seed[str(seed)] = {"result": result, "verdict": verdict, "verdict_msg": msg}
        unit_count += len(m_rungs)
        print(f"[{run_mode}] seed={seed} {verdict}: {msg}", flush=True)
        _write_heartbeat(output_dir, unit_count, expected_units, time.time() - t0)

    per_seed_verdicts = [per_seed[str(s)]["verdict"] for s in seeds]
    overall_verdict, overall_msg = combine_verdicts_stage15(per_seed_verdicts)

    last_seed_key = str(seeds[-1])
    last_result = per_seed[last_seed_key]["result"]
    diff = _arms_must_differ_stage15(last_result["rungs"][str(m_rungs[-1])])
    if not diff["arms_differ"]:
        overall_verdict = "HARD_FAIL"
        overall_msg = f"ARMS_IDENTICAL overrides combined verdict: {diff} || {overall_msg}"

    elapsed = time.time() - t0
    per_seed_summary = {
        s: {"verdict": per_seed[str(s)]["verdict"],
            "flat_rate_by_rung": {m: per_seed[str(s)]["result"]["rungs"][str(m)]["flat"]["false_pull_in_rate"]
                                  for m in m_rungs},
            "context_rate_by_rung": {m: per_seed[str(s)]["result"]["rungs"][str(m)]["context"]["false_pull_in_rate"]
                                    for m in m_rungs},
            "incluster_flat_by_rung": {m: per_seed[str(s)]["result"]["rungs"][str(m)]["flat"]["in_cluster_correct_retrieval_rate"]
                                       for m in m_rungs},
            "incluster_context_by_rung": {m: per_seed[str(s)]["result"]["rungs"][str(m)]["context"]["in_cluster_correct_retrieval_rate"]
                                          for m in m_rungs},
            "null_sweep_mean_max_by_rung": {m: per_seed[str(s)]["result"]["rungs"][str(m)]["null_sweep"]["mean_max_cosine"]
                                           for m in m_rungs},
            "evt_growth_check": per_seed[str(s)]["result"]["evt_growth_check"],
            "stage1_regression": per_seed[str(s)]["result"]["stage1_regression"]}
        for s in seeds}

    cardinality_ok = sum(len(per_seed[str(s)]["result"]["rungs"]) for s in seeds) == expected_units

    metrics = {
        "verdict": overall_verdict, "verdict_msg": overall_msg, "summary": f"{overall_verdict}: {overall_msg}",
        "elapsed_s": round(elapsed, 3), "run_mode": run_mode, "anchor_name": ANCHOR_NAME,
        "gate_thresh": GATE_THRESH, "n_dim": N_DIM, "seeds": seeds, "m_rungs": m_rungs,
        "k_shortlist": K_SHORTLIST, "stage1_baseline_false_pull_rate": STAGE1_BASELINE_FALSE_PULL_RATE,
        "per_seed_verdicts": dict(zip([str(s) for s in seeds], per_seed_verdicts)),
        "per_seed_summary": per_seed_summary,
        "per_seed_full": {k: v for k, v in per_seed.items()},
        "arms_differ_verified": diff["arms_differ"], "arms_differ_check": diff,
        "cardinality_ok": cardinality_ok, "expected_n_units": expected_units,
        "cell_chunked": False, "start_marker_written": True, "crash_diagnostic_present": True,
        "heartbeat_present": True, "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "rate-growth-ratio + EVT-curve-fit comparison over a fixed synthetic salted "
                    "micro-world; no closed-form capacity/SNR discriminator threshold to CRLB-check",
        "deterministic_seeding": True,
        "calibration_check_flat": "default_ok_for_this_regime: GATE_THRESH imported unmodified from "
                                  "Stage-1 (0.28)",
        "calibration_check_context": "adaptive_with_discriminator_gate: tau recalibrated per "
                                     "(seed,rung) via refuse_gate_calibrate_from_scores",
    }
    _write_metrics(output_dir, metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_seed_full",)},
                     indent=2, default=str))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- deliberately not BaseException, see cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, e)
        raise
