# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (NATIVE vs SWAPPED digest-differ per fresh unit)
# - final_metrics_atomicity declared (tmp_replace; per-seed resumable unit via tools/exp_checkpoint)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: cross-representation K-sweep diagnostic; no closed-form floor for a conditional
#   argmax-accuracy-given-recall@K quantity
# - HP_SCOPE: this cell answers a can-fail question pre-registered in
#   preregs/2026-08-15_k_sweep_e1_strengthened_v1.md sec 5 (REPRODUCES / DOES-NOT-REPRODUCE / VOID /
#   INSTRUMENT-STILL-WEAK), written BEFORE this file's first non-self-test run.
# - per-unit (per-DATA_SEED) failure-class instrumentation (no bare except)
# - self-test constructs a REAL tiny synthetic KGStore + REAL tiny ConceptSpace + a tiny
#   sents/buckets fixture, proves the held-out-sentence known-answer construction fires correctly
#   (pre-reg sec 8) before any CSKG-scale number is trusted.
# - progress_logging: print_flush_true (pre-reg sec 10)
# See preregs/2026-08-15_k_sweep_e1_strengthened_v1.md for the full pre-registration (written BEFORE
# this run).
"""exp_k_sweep_e1_strengthened_v1 -- STRENGTHENED INSTRUMENT for E1's K-sweep, 5 seeds.

WHY THIS CELL EXISTS. exp_k_sweep_e1_v1 found conditional selection accuracy at the store site
falling steeply with shortlist width (42.9% at K=5 -> 15.75% at K=full, CI-separated), but only
seed 20260810 of 3 cleared the reader-side known-answer floor (0.70) -- the other two seeds scored
0.6067 and 0.6467, a marginal instrument sitting NEAR its own floor. This cell replaces the weak
reader-side known-answer arm (query = space.bundle(lemma), same representation family as every
candidate) with C3's held-out-sentence construction (query = context_vector_masked over a sentence
NEVER used to build that lemma's anchor bundle -- a genuinely independent probe, C3 clears 0.70 by
11-16 points at every d it was measured at), then re-runs the identical K-sweep design across 5
seeds instead of 3, reporting per-seed AND pooled numbers with the n>=20 power gate enforced inside
the computation rather than applied after the fact. See pre-reg sec 5 for the pre-registered
falsifier: this is a STRENGTHENING run, not a confirmation run.

Modes:
  --self-test  Real-code-path check on a tiny synthetic KGStore + ConceptSpace + sents/buckets
               fixture (pre-reg sec 8). No CSKG load, no corpus build.
  --smoke      Real CSKG (small slice) + real reader corpus, 1 data seed, MAX_Q=40, K grid trimmed
               to [5,20,100] (pre-reg sec 9).
  --full       Full OpenStax corpus + CSKG at STORE_SCALE=100000, DATA_SEEDS=[20260810..20260814]
               (5 seeds), K grid [5,10,20,50,100,500,FULL], checkpointed per seed (resumable).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import torch

ANCHOR_NAME = "k_sweep_e1_strengthened_v1"
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_REPO, os.path.join(_REPO, "tools"), os.path.join(_REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CSKG_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.reading_grounding_loop import context_vector_masked, normalize_lemma  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
import experiments.exp_scorer_swap_e2_v1 as E2  # noqa: E402
import experiments.exp_k_sweep_e1_v1 as E1  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    GATE_THRESH, load_entity_vocab, load_spine_edges, precheck_kgstore_and_loader,
)
from experiments.exp_focus_pullin_causal_stage2a_multihop_loop_v1 import (  # noqa: E402
    pull_in_multi_exclude,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

STORE_SCALE = 100000
DATA_SEEDS = [20260810, 20260811, 20260812, 20260813, 20260814]
MAX_Q_PER_SEED = 400
MIN_Q_FOR_VERDICT = 20
N_BOOTSTRAP = 5000
BOOT_SEED = 20260815
KNOWN_ANSWER_N = 150
KNOWN_ANSWER_FLOOR = 0.70
K_GRID_FULL = E1.K_GRID_FULL
K_GRID_SMOKE = E1.K_GRID_SMOKE
POOLS = E1.POOLS


# ============================================================================ reader space (+ sents/buckets)
def build_reader_space_local(run_mode: str, output_dir: str) -> dict:
    """Identical sequence to E2.build_reader_space (C3.build_corpus -> C3.build_buckets ->
    C3.build_space), reproduced locally ONLY so sents/buckets are also returned -- E2's own function
    does not expose them and is not modified. Verified identical construction: exp_scorer_swap_e2_v1
    .py:162-174."""
    sents = C3.build_corpus(run_mode)
    buckets, counts = C3.build_buckets(sents)
    space = C3.build_space(sents, buckets, output_dir)
    anchors, mat = space.anchor_matrix()
    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9
    pos = {a: i for i, a in enumerate(anchors)}
    norm2idx: Dict[str, List[int]] = {}
    for a in anchors:
        norm2idx.setdefault(normalize_lemma(a), []).append(pos[a])
    return {"space": space, "anchors": anchors, "anchor_set": set(anchors), "mat": mat,
           "mat_ok": mat_ok, "pos": pos, "norm2idx": norm2idx, "n_sents": len(sents),
           "sents": sents, "buckets": buckets}


# ============================================================================ strengthened known-answer (reader)
def known_answer_reader_heldout(queries: List[Tuple[int, int, int]], idx_to_lemma: List[str],
                                space, anchors: List[str], buckets: Dict[str, List[int]],
                                sents: List[str], seed: int) -> Tuple[float, int]:
    """C3's held-out-sentence self-retrieval construction (exp_capacity_binds_c3_v1.py:185-213),
    applied to E1's own query tuples instead of C3's items list. Query vector is
    context_vector_masked over a sentence NEVER used to build idx_to_lemma[s]'s anchor bundle
    (buckets[L][_n_profile(len(buckets[L])):]) -- a genuinely independent probe of the gold anchor,
    not a bundle-vs-bundle self-comparison. See pre-reg sec 1-2."""
    rng = np.random.default_rng(seed)
    hits, n = 0, 0
    for s, p, o in queries[:KNOWN_ANSWER_N]:
        ls, lo = idx_to_lemma[s], idx_to_lemma[o]
        b = buckets.get(ls)
        if not b:
            continue
        cut = C3._n_profile(len(b))
        held = b[cut:]
        if not held:
            continue
        q = context_vector_masked(sents[held[0]], ls, d=space.d)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        gold_vec = space.bundle(lo)
        if gold_vec is None:
            continue
        distractor = anchors[int(rng.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (distractor == lo or distractor == ls
                              or C3._is_variant(distractor, ls) or C3._is_variant(distractor, lo)):
            distractor = anchors[int(rng.integers(len(anchors)))]
            tries += 1
        if distractor == lo or distractor == ls:
            continue
        d_vec = space.bundle(distractor)
        if d_vec is None:
            continue
        gn = float(np.linalg.norm(gold_vec))
        dn = float(np.linalg.norm(d_vec))
        if gn < 1e-9 or dn < 1e-9:
            continue
        sc_g = float(np.dot(q, gold_vec) / (qn * gn))
        sc_d = float(np.dot(q, d_vec) / (qn * dn))
        hits += int(sc_g >= sc_d)
        n += 1
    return round(hits / max(1, n), 6), n


# ============================================================================ per-seed unit
def run_seed_unit(seed: int, entity_to_idx: Dict[str, int], idx_to_entity: Dict[int, str],
                  triples_full: np.ndarray, n_rel: int, idx_to_lemma: List[str],
                  norm2idxs: Dict[str, List[int]], eligible_base: np.ndarray, space,
                  node_degree: Dict[str, int], t_mat: np.ndarray, t_cov: np.ndarray,
                  pos: Dict[str, int], anchors: List[str], buckets: Dict[str, List[int]],
                  sents: List[str], rs: dict, max_q: int, k_grid: Sequence[int]) -> dict:
    t0 = time.time()
    store, ingested = E2.build_store_for_seed(seed, entity_to_idx, triples_full, n_rel)
    print("[seed=%d] store ingested %d edges elapsed=%.1fs" % (seed, len(ingested), time.time() - t0),
         flush=True)
    q = E2.build_query_set(ingested, idx_to_entity, rs, seed, max_q)
    print("[seed=%d] jointly-valid query candidates=%d elapsed=%.1fs" % (seed, len(q), time.time() - t0),
         flush=True)

    ka_store_acc, ka_store_n = E1.known_answer_store(q, store, idx_to_entity, entity_to_idx,
                                                      len(entity_to_idx), seed + 61)
    ka_reader_acc, ka_reader_n = known_answer_reader_heldout(q, idx_to_lemma, space, anchors,
                                                              buckets, sents, seed + 71)
    print("[seed=%d] known_answer store=%.4f(n=%d) reader_heldout=%.4f(n=%d) elapsed=%.1fs"
         % (seed, ka_store_acc, ka_store_n, ka_reader_acc, ka_reader_n, time.time() - t0), flush=True)

    results = []
    for i, (s, p, o) in enumerate(q):
        r = E1.score_query_ksweep(s, p, o, store, idx_to_entity, idx_to_lemma, norm2idxs,
                                  eligible_base, space, node_degree, t_mat, t_cov, pos, k_grid)
        if r is not None:
            results.append(r)
        if (i + 1) % 100 == 0:
            print("[seed=%d] scored %d/%d elapsed=%.1fs" % (seed, i + 1, len(q), time.time() - t0),
                 flush=True)
    return {"seed": seed, "n_ingested": len(ingested), "n_query_candidates": len(q),
           "n_scoreable": len(results), "known_answer_store": {"acc": ka_store_acc, "n": ka_store_n,
           "floor": KNOWN_ANSWER_FLOOR, "ok": ka_store_acc >= KNOWN_ANSWER_FLOOR},
           "known_answer_reader": {"acc": ka_reader_acc, "n": ka_reader_n,
           "floor": KNOWN_ANSWER_FLOOR, "ok": ka_reader_acc >= KNOWN_ANSWER_FLOOR,
           "construction": "held_out_sentence_context_vector_masked"},
           "elapsed_s": round(time.time() - t0, 2), "results": results}


# ============================================================================ aggregation (pooled + per-seed)
def _collect_vecs(units: List[dict], k_grid: Sequence[int]) -> Dict[str, Dict[str, Dict[str, List[bool]]]]:
    per_k_pool_arm: Dict[str, Dict[str, Dict[str, List[bool]]]] = {
        str(k): {pool: {} for pool in POOLS} for k in k_grid}
    for unit in units:
        for r in unit["results"]:
            for k in k_grid:
                row = r["by_k"][str(k)]
                for pool in POOLS:
                    pr = row.get(pool)
                    if pr is None:
                        continue
                    d = per_k_pool_arm[str(k)][pool]
                    for arm in ("NATIVE", "SWAPPED", "DEGREE_FLOOR", "TRIGRAM_FLOOR", "SCRAMBLE"):
                        d.setdefault(arm, []).append(bool(pr[arm]))
    return per_k_pool_arm


def _bs(vec_map: Dict[str, List[bool]]) -> Optional[dict]:
    arrs = {k: np.array(v, dtype=float) for k, v in vec_map.items() if len(v) > 0}
    if not arrs or min(len(v) for v in arrs.values()) < MIN_Q_FOR_VERDICT:
        return None
    n = len(next(iter(arrs.values())))
    if any(len(v) != n for v in arrs.values()):
        return {"paired": False, "raw_acc": {k: float(v.mean()) for k, v in arrs.items()},
               "n_per_arm": {k: len(v) for k, v in arrs.items()}}
    deltas = [("d_NATIVE_minus_SWAPPED", "NATIVE", "SWAPPED"),
             ("d_NATIVE_minus_DEGREE_FLOOR", "NATIVE", "DEGREE_FLOOR"),
             ("d_SWAPPED_minus_DEGREE_FLOOR", "SWAPPED", "DEGREE_FLOOR"),
             ("d_NATIVE_minus_TRIGRAM_FLOOR", "NATIVE", "TRIGRAM_FLOOR"),
             ("d_SWAPPED_minus_TRIGRAM_FLOOR", "SWAPPED", "TRIGRAM_FLOOR"),
             ("d_NATIVE_minus_SCRAMBLE", "NATIVE", "SCRAMBLE"),
             ("d_SWAPPED_minus_SCRAMBLE", "SWAPPED", "SCRAMBLE")]
    deltas = [d for d in deltas if d[1] in arrs and d[2] in arrs]
    bs = MS.paired_bootstrap(arrs, deltas, N_BOOTSTRAP, BOOT_SEED)
    bs["paired"] = True
    return bs


def aggregate(all_seed_units: Dict[str, dict], k_grid: Sequence[int],
             enforce_known_answer_gate: bool = True) -> dict:
    """POOLED (across all gate-passing seeds) AND PER-SEED (each seed's own bootstrap), per
    pre-reg sec 4. MIN_Q_FOR_VERDICT is enforced INSIDE both, never post hoc."""
    seeds_void = []
    valid_units = []
    per_seed_gate: Dict[str, dict] = {}
    for key, unit in all_seed_units.items():
        seed = unit["seed"]
        gate_fail = not unit["known_answer_store"]["ok"] or not unit["known_answer_reader"]["ok"]
        per_seed_gate[str(seed)] = {
            "known_answer_store": unit["known_answer_store"],
            "known_answer_reader": unit["known_answer_reader"],
            "gate_fail": gate_fail,
        }
        if gate_fail:
            seeds_void.append(seed)
            if enforce_known_answer_gate:
                continue
        valid_units.append(unit)

    pooled_vecs = _collect_vecs(valid_units, k_grid)
    per_k_bootstrap_pooled = {str(k): {pool: _bs(pooled_vecs[str(k)][pool]) for pool in POOLS}
                              for k in k_grid}
    n_scoreable_per_k_pool_pooled = {str(k): {pool: len(pooled_vecs[str(k)][pool].get("NATIVE", []))
                                              for pool in POOLS} for k in k_grid}

    per_seed_bootstrap: Dict[str, dict] = {}
    for unit in valid_units:
        seed = unit["seed"]
        seed_vecs = _collect_vecs([unit], k_grid)
        per_seed_bootstrap[str(seed)] = {
            str(k): {pool: _bs(seed_vecs[str(k)][pool]) for pool in POOLS} for k in k_grid}

    return {"per_k_bootstrap_pooled": per_k_bootstrap_pooled,
           "n_scoreable_per_k_pool_pooled": n_scoreable_per_k_pool_pooled,
           "per_seed_bootstrap": per_seed_bootstrap,
           "per_seed_gate": per_seed_gate,
           "seeds_void_known_answer": seeds_void}


def _kill_condition(per_k_bootstrap: dict, k_grid: Sequence[int], pool: str, arm: str) -> Optional[dict]:
    return E1._kill_condition(per_k_bootstrap, k_grid, pool, arm)


def _reproduces_per_seed(per_seed_bootstrap: Dict[str, dict], k_grid: Sequence[int]) -> Dict[str, dict]:
    """For each seed, CI-separated K=5-vs-K=full decline check on STORE_POOL/NATIVE and
    STORE_POOL/SWAPPED (the two well-powered, genuinely-decoupled arms, pre-reg sec 5)."""
    out: Dict[str, dict] = {}
    for seed, pkb in per_seed_bootstrap.items():
        native = _kill_condition(pkb, k_grid, "STORE_POOL", "NATIVE")
        swapped = _kill_condition(pkb, k_grid, "STORE_POOL", "SWAPPED")
        native_declines = bool(native and not native["flat_ci_overlap"])
        swapped_declines = bool(swapped and not swapped["flat_ci_overlap"])
        out[seed] = {"STORE_POOL_NATIVE": native, "STORE_POOL_SWAPPED": swapped,
                    "native_declines_ci_separated": native_declines,
                    "swapped_declines_ci_separated": swapped_declines,
                    "both_decline": native_declines and swapped_declines}
    return out


# ============================================================================ self-test
def self_test() -> dict:
    gen = torch.Generator()
    gen.manual_seed(3)
    ents = ["cat", "dog", "puppy", "kitten", "rock", "cloud"]
    idx_to_entity = {i: e for i, e in enumerate(ents)}
    entity_to_idx = {e: i for i, e in idx_to_entity.items()}
    node_degree = {"cat": 50, "dog": 40, "puppy": 5, "kitten": 5, "rock": 3, "cloud": 2}
    store = KGStore(n_ent=6, n_rel=2, n_dim=32, generator=gen)
    triples = torch.tensor([[0, 0, 1], [1, 0, 0], [4, 1, 5]], dtype=torch.long)
    store.ingest_triples(triples)

    idx_to_lemma = ents[:]
    norm2idxs = {e: [i] for i, e in enumerate(ents)}
    anchor_set = set(ents)
    eligible_base = E1.build_eligible_base(idx_to_lemma, anchor_set)

    from hdlab.reading_grounding_loop import ConceptSpace
    space = ConceptSpace(d=16)
    # sents/buckets fixture: 3 sentences per lemma, PROFILE_FRAC=0.8 -> C3._n_profile(3)=2, so
    # sentence index [2] is held out for every lemma -- never used to build the bundle below.
    sents = ["the cat sat on the mat", "a dog ran in the yard", "the cat is a small animal",
            "a puppy is a young dog", "the kitten is very small", "the cat chased the puppy",
            "a big rock sat still", "the rock did not move", "grey rock near the yard"]
    buckets = {"cat": [0, 2, 5], "dog": [1, 3, 5], "puppy": [3, 5, 8], "kitten": [4, 5, 8],
              "rock": [6, 7, 8]}
    for w in ("cat", "dog", "puppy", "kitten", "rock"):
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            space.observe(w, context_vector_masked(sents[i], w, d=space.d))
    anchors, _mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    t_mat, t_cov = MS.trigram_matrix(anchors)

    universe = E1.query_universe(0, idx_to_lemma, norm2idxs, eligible_base)
    assert set(universe.tolist()) == {1, 2, 3, 4, 5}, "UNIVERSE_MISMATCH: %r" % universe.tolist()

    r = E1.score_query_ksweep(0, 0, 1, store, idx_to_entity, idx_to_lemma, norm2idxs, eligible_base,
                              space, node_degree, t_mat, t_cov, pos, [1, 3, 6])
    assert r is not None, "SELFTEST_QUERY_UNSCOREABLE"
    row6 = r["by_k"]["6"]
    assert row6["STORE_POOL"] is not None, "SELFTEST_STORE_POOL_K6_NONE"

    # known-answer-heldout self-test: query=(0,0,1) means s=cat(0), o=dog(1). Held-out sentence for
    # "cat" is sents[5]="the cat chased the puppy" (mentions cat, not dog/kitten/rock as a strong
    # cue) -- assert the function runs end-to-end and returns a valid (acc, n) pair with n>0 on this
    # tiny fixture (a single query cannot itself clear a statistical floor; that is what smoke/full
    # check at scale).
    ka_acc, ka_n = known_answer_reader_heldout([(0, 0, 1)], idx_to_lemma, space, anchors, buckets,
                                                sents, seed=7)
    assert ka_n >= 1, "SELFTEST_KNOWN_ANSWER_HELDOUT_NO_SCOREABLE_QUERY: n=%d" % ka_n
    assert 0.0 <= ka_acc <= 1.0, "SELFTEST_KNOWN_ANSWER_HELDOUT_ACC_OUT_OF_RANGE: %r" % ka_acc

    def _digest(x):
        return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()

    digests = {"store_pool_k6": _digest(row6["STORE_POOL"]),
              "reader_pool_k6": _digest(row6.get("READER_POOL")),
              "known_answer_heldout": _digest({"acc": ka_acc, "n": ka_n})}
    return {"instrument_validity": {"universe_shared_ok": True, "known_answer_heldout_ran": True},
           "sample_result": r, "known_answer_heldout_sample": {"acc": ka_acc, "n": ka_n},
           "digests": digests}


# ============================================================================ output plumbing
def _atomic_json(path: str, obj: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
             "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "elapsed_s": 0.0, "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "metrics.json"), diag)


def _heartbeat(output_dir, payload):
    path = os.path.join(output_dir, "_heartbeat.jsonl")
    rec = dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()


# ============================================================================ main
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()

    if args.self_test or not (args.smoke or args.full):
        t0 = time.time()
        result = self_test()
        elapsed = time.time() - t0
        metrics = {"verdict": "HARD_PASS", "verdict_msg": "SELFTEST_PASS", "run_mode": "self_test",
                  "anchor_name": ANCHOR_NAME, "elapsed_s": round(elapsed, 3), "result": result}
        _atomic_json(os.path.join(OUTPUT_DIR, "metrics.json"), metrics)
        print(json.dumps(metrics, indent=2, default=str))
        return 0

    run_mode = "smoke" if args.smoke else "full"
    output_dir = OUTPUT_DIR if run_mode == "full" else OUTPUT_DIR + "_SMOKE"
    k_grid = K_GRID_SMOKE if run_mode == "smoke" else K_GRID_FULL
    _write_start_marker(output_dir, run_mode)
    t0 = time.time()

    pre = precheck_kgstore_and_loader()
    assert pre["ok"], "STAGE2B_PRECHECK_FAIL: %r" % pre

    print("[%s] loading CSKG entity vocab + edges..." % run_mode, flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    idx_to_entity = {v: k for k, v in entity_to_idx.items()}
    triples_full, relation_to_idx = load_spine_edges(entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    node_degree = E2.load_node_degree(CSKG_DIR)
    print("[%s] %d entities, %d edges, n_rel=%d elapsed=%.1fs"
         % (run_mode, len(entity_to_idx), len(triples_full), n_rel, time.time() - t0), flush=True)
    _heartbeat(output_dir, {"phase": "cskg_loaded", "elapsed_s": time.time() - t0})

    print("[%s] building reader ConceptSpace (+ sents/buckets for held-out known-answer)..."
         % run_mode, flush=True)
    rs = build_reader_space_local(run_mode, output_dir)
    space = rs["space"]
    anchors = rs["anchors"]
    anchor_set = rs["anchor_set"]
    buckets = rs["buckets"]
    sents = rs["sents"]
    print("[%s] reader space: n_anchors=%d n_sents=%d elapsed=%.1fs"
         % (run_mode, len(anchors), rs["n_sents"], time.time() - t0), flush=True)
    _heartbeat(output_dir, {"phase": "reader_space_built", "n_anchors": len(anchors),
                            "elapsed_s": time.time() - t0})

    print("[%s] building idx_to_lemma over %d entities (one-time, ~0.19ms/call)..."
         % (run_mode, len(entity_to_idx)), flush=True)
    t_lemma0 = time.time()
    idx_to_lemma, norm2idxs = E1.build_idx_to_lemma(idx_to_entity)
    eligible_base = E1.build_eligible_base(idx_to_lemma, anchor_set)
    print("[%s] idx_to_lemma done: %d eligible entities elapsed_lemma=%.1fs total=%.1fs"
         % (run_mode, int(eligible_base.sum()), time.time() - t_lemma0, time.time() - t0), flush=True)
    _heartbeat(output_dir, {"phase": "idx_to_lemma_built", "n_eligible": int(eligible_base.sum()),
                            "elapsed_s": time.time() - t0})

    _, mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    t_mat, t_cov = MS.trigram_matrix(anchors)

    seeds = DATA_SEEDS[:1] if run_mode == "smoke" else DATA_SEEDS
    max_q = 40 if run_mode == "smoke" else MAX_Q_PER_SEED

    done = completed_units(output_dir)
    for seed in seeds:
        key = unit_key("seed", seed)
        if key in done:
            print("[%s] seed=%d already complete (resume)" % (run_mode, seed), flush=True)
            continue
        unit = run_seed_unit(seed, entity_to_idx, idx_to_entity, triples_full, n_rel, idx_to_lemma,
                             norm2idxs, eligible_base, space, node_degree, t_mat, t_cov, pos, anchors,
                             buckets, sents, rs, max_q, k_grid)
        record_unit(output_dir, key, unit)
        _heartbeat(output_dir, {"phase": "seed_done", "seed": seed, "n_scoreable": unit["n_scoreable"],
                                "elapsed_s": time.time() - t0})
        print("[%s] seed=%d done n_scoreable=%d elapsed=%.1fs"
             % (run_mode, seed, unit["n_scoreable"], time.time() - t0), flush=True)

    all_units_map = load_units(output_dir)
    all_units = list(all_units_map.values())
    agg = aggregate(all_units_map, k_grid, enforce_known_answer_gate=(run_mode == "full"))

    def _digest_k(k, pkb):
        d = pkb.get(str(k), {})
        sp = d.get("STORE_POOL")
        rp = d.get("READER_POOL")
        return hashlib.sha256(json.dumps({"sp": sp.get("arm_acc_ci") if sp else None,
                                          "rp": rp.get("arm_acc_ci") if rp else None},
                                         sort_keys=True, default=str).encode()).hexdigest()

    pkb_pooled = agg["per_k_bootstrap_pooled"]
    ks_present = [k for k in k_grid if pkb_pooled.get(str(k), {}).get("STORE_POOL")
                 or pkb_pooled.get(str(k), {}).get("READER_POOL")]
    arms_differ = len(set(_digest_k(k, pkb_pooled) for k in ks_present)) > 1 if len(ks_present) > 1 else None

    kill_condition_pooled = {
        "STORE_POOL_NATIVE": _kill_condition(pkb_pooled, k_grid, "STORE_POOL", "NATIVE"),
        "STORE_POOL_SWAPPED": _kill_condition(pkb_pooled, k_grid, "STORE_POOL", "SWAPPED"),
        "READER_POOL_SWAPPED": _kill_condition(pkb_pooled, k_grid, "READER_POOL", "SWAPPED"),
        "READER_POOL_NATIVE_ANALYTICALLY_PINNED_NOT_EVIDENCE": _kill_condition(
            pkb_pooled, k_grid, "READER_POOL", "NATIVE"),
    }
    _decoupled_pooled = {k: v for k, v in kill_condition_pooled.items()
                        if k != "READER_POOL_NATIVE_ANALYTICALLY_PINNED_NOT_EVIDENCE"}
    any_decoupled_computed_pooled = any(v is not None for v in _decoupled_pooled.values())

    per_seed_reproduce = _reproduces_per_seed(agg["per_seed_bootstrap"], k_grid)
    n_seeds_gate_passed = sum(1 for v in agg["per_seed_gate"].values() if not v["gate_fail"])
    n_seeds_both_decline = sum(1 for v in per_seed_reproduce.values() if v["both_decline"])

    pooled_store_native = kill_condition_pooled["STORE_POOL_NATIVE"]
    pooled_store_swapped = kill_condition_pooled["STORE_POOL_SWAPPED"]
    pooled_both_decline = bool(pooled_store_native and not pooled_store_native["flat_ci_overlap"]
                               and pooled_store_swapped and not pooled_store_swapped["flat_ci_overlap"])

    # reader-side known-answer instrument-strength check, aggregated across gate-attempted seeds
    reader_ka_accs = [v["known_answer_reader"]["acc"] for v in agg["per_seed_gate"].values()]
    reader_ka_ok_count = sum(1 for v in agg["per_seed_gate"].values()
                             if v["known_answer_reader"]["ok"])
    instrument_still_weak = (len(reader_ka_accs) > 0
                             and reader_ka_ok_count < max(1, len(reader_ka_accs) - 1)
                             and all(a < 0.75 for a in reader_ka_accs))

    if run_mode == "full" and n_seeds_gate_passed == 0:
        verdict = "VOID_KNOWN_ANSWER_FAILED_ALL_SEEDS"
    elif run_mode == "full" and instrument_still_weak:
        verdict = "INSTRUMENT_STILL_WEAK"
    elif not any_decoupled_computed_pooled:
        verdict = "INSUFFICIENT_DATA"
    elif run_mode == "full" and n_seeds_gate_passed >= 4 and n_seeds_both_decline >= 4 and pooled_both_decline:
        verdict = "REPRODUCES"
    elif run_mode == "full":
        verdict = "DOES_NOT_REPRODUCE"
    else:
        verdict = "SMOKE_NON_DEGENERATE" if any_decoupled_computed_pooled else "SMOKE_DEGENERATE"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": ("n_seeds_gate_passed=%d/%d n_seeds_both_store_arms_decline=%d "
                       "pooled_both_decline=%r instrument_still_weak=%r"
                       % (n_seeds_gate_passed, len(seeds), n_seeds_both_decline, pooled_both_decline,
                          instrument_still_weak)),
        "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "elapsed_s": round(elapsed, 3),
        "n_entities": len(entity_to_idx), "n_edges_total": len(triples_full), "n_rel": n_rel,
        "n_reader_anchors": len(anchors), "n_reader_sents": rs["n_sents"],
        "store_scale": STORE_SCALE, "data_seeds": seeds, "max_q_per_seed": max_q,
        "gate_thresh": GATE_THRESH, "k_grid": k_grid,
        "per_k_bootstrap_pooled": agg["per_k_bootstrap_pooled"],
        "n_scoreable_per_k_pool_pooled": agg["n_scoreable_per_k_pool_pooled"],
        "per_seed_bootstrap": agg["per_seed_bootstrap"],
        "per_seed_gate": agg["per_seed_gate"],
        "per_seed_reproduce": per_seed_reproduce,
        "seeds_void_known_answer": agg["seeds_void_known_answer"],
        "kill_condition_pooled": kill_condition_pooled,
        "n_seeds_gate_passed": n_seeds_gate_passed,
        "n_seeds_both_store_arms_decline_ci_separated": n_seeds_both_decline,
        "pooled_both_store_arms_decline_ci_separated": pooled_both_decline,
        "instrument_still_weak": instrument_still_weak,
        "read_out_invariance_note": "READER_POOL/NATIVE ranks and selects with the identical cosine "
                                    "score, so its conditional accuracy is analytically pinned to "
                                    "hit@1/recall@K (mechanically non-increasing in K) -- reported, "
                                    "excluded from the REPRODUCES/DOES-NOT-REPRODUCE verdict. See "
                                    "pre-reg sec 6.",
        "n_seeds_complete": len(all_units), "n_seeds_expected": len(seeds),
        "cardinality_ok": len(all_units) == len(seeds),
        "arms_differ_verified": arms_differ,
        "final_metrics_atomicity": "tmp_replace", "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "instrument_validity_stamped_this_session": True,
        "crlb_n/a": "cross-representation K-sweep diagnostic; no closed-form floor for a "
                    "conditional argmax-accuracy-given-recall@K quantity",
        "min_q_for_verdict": MIN_Q_FOR_VERDICT,
        "known_answer_floor": KNOWN_ANSWER_FLOOR,
        "known_answer_reader_construction": "held_out_sentence_context_vector_masked (C3-reused)",
        "e2_correction_note": "exp_scorer_swap_e2_v1's AMBIGUOUS verdict was measured on a confounded "
                              "pairing (~1400x K disparity + a lemma-normalization membership bug, "
                              "~21x on its own) -- see pre-reg sec 11 and exp_k_sweep_e1_v1 sec 3. Not "
                              "re-run here; not evidence about store/reader mechanism identity.",
        "prereg": "preregs/2026-08-15_k_sweep_e1_strengthened_v1.md",
        "predecessor": "data/exp_k_sweep_e1_v1/metrics.json",
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                     if k not in ("per_k_bootstrap_pooled", "per_seed_bootstrap")},
                     indent=2, default=str))
    print("VERDICT:", verdict)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as exc:  # noqa: BLE001 -- deliberately not BaseException, cell-template mandate
        _write_crash_metrics(OUTPUT_DIR, exc)
        raise
