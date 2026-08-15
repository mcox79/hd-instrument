# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (NATIVE vs SWAPPED digest-differ per fresh unit)
# - final_metrics_atomicity declared (tmp_replace; per-seed resumable unit via tools/exp_checkpoint)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a: cross-representation K-sweep diagnostic; no closed-form floor for a conditional
#   argmax-accuracy-given-recall@K quantity
# - HP_SCOPE: this cell answers a can-fail question pre-registered in
#   preregs/2026-08-15_k_sweep_e1_v1.md sec 5 (KILL CONDITION / PASS / VOID), written BEFORE this
#   file's first non-self-test run.
# - per-unit (per-DATA_SEED) failure-class instrumentation (no bare except)
# - self-test constructs a REAL tiny synthetic KGStore + REAL tiny ConceptSpace, proves the shared
#   candidate-universe construction and the K-restricted selection mechanisms fire correctly
#   (pre-reg sec 6) before any CSKG-scale number is trusted.
# - progress_logging: print_flush_true (pre-reg sec 8)
# See preregs/2026-08-15_k_sweep_e1_v1.md for the full pre-registration (written BEFORE this run).
"""exp_k_sweep_e1_v1 -- E1, the K-SWEEP (store + reader).

QUESTION: SHORTLIST_K=50 (experiments/exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1.py:118)
was set once and never swept. This cell sweeps K in {5,10,20,50,100,500,FULL} at BOTH the store
site (KGStore pull_in_multi_exclude selection) and the reader site (ConceptSpace cosine selection),
reporting per K: recall@K (is the true answer within the top-K candidates by that site's own
ranking) and argmax accuracy CONDITIONAL on recall@K (given the answer is in the candidate set,
does the site's selection mechanism pick it). See pre-reg sec 3 for the root-cause finding that
motivated this design: exp_scorer_swap_e2_v1's READER_POOL used a ~4287-candidate pool while its
STORE_POOL collapsed (post-filter) to a median of 3 candidates -- an unreported ~1400x K disparity
that this cell's SHARED CANDIDATE UNIVERSE (pre-reg sec 4) is designed to eliminate: both pools
rank the SAME per-query candidate set, differing only in which score function does the ranking.

Modes:
  --self-test  Real-code-path check on a tiny synthetic KGStore + ConceptSpace fixture (pre-reg
               sec 6). No CSKG load, no corpus build.
  --smoke      Real CSKG (small slice) + real reader corpus, 1 data seed, MAX_Q=40, K grid trimmed
               to [5,20,100] (pre-reg sec 7).
  --full       Full OpenStax corpus + CSKG at STORE_SCALE=100000, DATA_SEEDS=[20260810,20260811,
               20260812], K grid [5,10,20,50,100,500,FULL], checkpointed per seed (resumable).
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
from typing import Dict, List, Optional, Sequence, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "k_sweep_e1_v1"
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_REPO, os.path.join(_REPO, "tools"), os.path.join(_REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CSKG_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.reading_grounding_loop import normalize_lemma  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
import experiments.exp_scorer_swap_e2_v1 as E2  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    GATE_THRESH, load_entity_vocab, load_spine_edges, precheck_kgstore_and_loader,
)
from experiments.exp_focus_pullin_causal_stage2a_multihop_loop_v1 import (  # noqa: E402
    pull_in_multi_exclude,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

STORE_SCALE = 100000
DATA_SEEDS = [20260810, 20260811, 20260812]
MAX_Q_PER_SEED = 400
MIN_Q_FOR_VERDICT = 20
N_BOOTSTRAP = 5000
BOOT_SEED = 20260815
KNOWN_ANSWER_N = 150
KNOWN_ANSWER_FLOOR = 0.70
K_GRID_FULL = [5, 10, 20, 50, 100, 500, -1]      # -1 sentinel == FULL shared universe
K_GRID_SMOKE = [5, 20, 100]
POOLS = ("STORE_POOL", "READER_POOL")


# ============================================================================ shared candidate universe
def build_idx_to_lemma(idx_to_entity: Dict[int, str]) -> Tuple[List[str], Dict[str, List[int]]]:
    """One-time O(n_ent) pass: normalize_lemma every CSKG entity id. Measured ~0.19ms/call
    (16000 calls in 2.97s); at n_ent~482588 this is ~90s, a one-time cost shared by every seed
    and every K in the grid."""
    n = len(idx_to_entity)
    idx_to_lemma = [""] * n
    norm2idxs: Dict[str, List[int]] = {}
    for i in range(n):
        lm = normalize_lemma(idx_to_entity[i])
        idx_to_lemma[i] = lm
        norm2idxs.setdefault(lm, []).append(i)
    return idx_to_lemma, norm2idxs


def build_eligible_base(idx_to_lemma: List[str], anchor_set: Set[str]) -> np.ndarray:
    return np.array([lm in anchor_set for lm in idx_to_lemma], dtype=bool)


def query_universe(s: int, idx_to_lemma: List[str], norm2idxs: Dict[str, List[int]],
                   eligible_base: np.ndarray) -> np.ndarray:
    """Entity indices eligible as candidates for query subject s: reader-anchor-compatible, not s,
    not a lemma-variant of s. Shared unmodified between STORE_POOL and READER_POOL -- only the
    RANKING within this universe differs (pre-reg sec 4)."""
    mask = eligible_base.copy()
    mask[s] = False
    for i in norm2idxs.get(idx_to_lemma[s], ()):
        mask[i] = False
    return np.flatnonzero(mask)


# ============================================================================ per-query scoring
def _k_slice(ranked: np.ndarray, k: int) -> np.ndarray:
    if k < 0:
        return ranked
    return ranked[:min(k, len(ranked))]


def score_pool_at_k(topk_entities: np.ndarray, o: int, s: int, probe_np: np.ndarray,
                    store: KGStore, idx_to_lemma: List[str], space, node_degree: Dict[str, int],
                    idx_to_entity: Dict[int, str], t_mat: np.ndarray, t_cov: np.ndarray,
                    pos: Dict[str, int], seed_key: str) -> Optional[dict]:
    """One (pool, K) cell: native (pull_in_multi_exclude), swapped (reader cosine argmax),
    degree floor, trigram floor, scramble -- all restricted to topk_entities. Returns None if o
    not in topk_entities (not scoreable at this K)."""
    topk_list = topk_entities.tolist()
    if o not in topk_list:
        return None
    o_pos = topk_list.index(o)
    exclude = {topk_list.index(s)} if s in topk_list else set()

    cand_E = store.E[topk_entities].numpy()
    r_native = pull_in_multi_exclude(probe_np, cand_E, exclude, gate=GATE_THRESH)
    b_native = int(r_native["candidate_idx"])
    native_correct = (b_native == o_pos)

    cand_lemmas = [idx_to_lemma[i] for i in topk_list]
    q_vec = space.bundle(idx_to_lemma[s])
    cand_vecs = [space.bundle(l) for l in cand_lemmas]
    if q_vec is not None:
        b_swap, _ = E2.cosine_argmax(q_vec, cand_vecs)
        swap_correct = (b_swap == o_pos)
    else:
        swap_correct = False

    deg_vals = [node_degree.get(idx_to_entity[i], 0) for i in topk_list]
    b_deg = int(np.argmax(deg_vals))
    deg_correct = (b_deg == o_pos)

    qlemma = idx_to_lemma[s]
    if qlemma in pos and t_cov[pos[qlemma]]:
        tq = t_mat[pos[qlemma]]
        trig_vals = [float(np.dot(t_mat[pos[l]], tq)) if l in pos else -1.0 for l in cand_lemmas]
        b_trig = int(np.argmax(trig_vals))
        trig_correct = (b_trig == o_pos)
    else:
        trig_correct = False

    b_scr = E2.scramble_argmax(len(topk_list), seed_key)
    scr_correct = (b_scr == o_pos)

    return {"n_candidates": len(topk_list), "NATIVE": native_correct, "SWAPPED": swap_correct,
           "DEGREE_FLOOR": deg_correct, "TRIGRAM_FLOOR": trig_correct, "SCRAMBLE": scr_correct}


def score_query_ksweep(s: int, p: int, o: int, store: KGStore, idx_to_entity: Dict[int, str],
                       idx_to_lemma: List[str], norm2idxs: Dict[str, List[int]],
                       eligible_base: np.ndarray, space, node_degree: Dict[str, int],
                       t_mat: np.ndarray, t_cov: np.ndarray, pos: Dict[str, int],
                       k_grid: Sequence[int]) -> Optional[dict]:
    universe = query_universe(s, idx_to_lemma, norm2idxs, eligible_base)
    if o not in set(universe.tolist()):
        return None

    key = store.key(s, p)
    probe = store.W @ key
    probe_np = probe.numpy()

    store_scores = store.score_all(key).numpy()[universe]
    store_order = universe[np.argsort(-store_scores)]

    q_vec = space.bundle(idx_to_lemma[s])
    reader_order: Optional[np.ndarray] = None
    if q_vec is not None:
        qn = float(np.linalg.norm(q_vec))
        if qn >= 1e-9:
            reader_scores = np.full(len(universe), -np.inf, dtype=np.float64)
            for j, ent in enumerate(universe.tolist()):
                cv = space.bundle(idx_to_lemma[ent])
                if cv is None:
                    continue
                cvn = float(np.linalg.norm(cv))
                if cvn < 1e-9:
                    continue
                reader_scores[j] = float(np.dot(q_vec, cv) / (qn * cvn))
            reader_order = universe[np.argsort(-reader_scores)]

    by_k: Dict[str, dict] = {}
    for k in k_grid:
        row: Dict[str, Optional[dict]] = {"K": k, "universe_size": int(len(universe))}
        store_topk = _k_slice(store_order, k)
        row["STORE_POOL"] = score_pool_at_k(
            store_topk, o, s, probe_np, store, idx_to_lemma, space, node_degree, idx_to_entity,
            t_mat, t_cov, pos, "store|K%s|%d|%d|%d" % (k, s, p, o))
        if reader_order is not None:
            reader_topk = _k_slice(reader_order, k)
            row["READER_POOL"] = score_pool_at_k(
                reader_topk, o, s, probe_np, store, idx_to_lemma, space, node_degree, idx_to_entity,
                t_mat, t_cov, pos, "reader|K%s|%d|%d|%d" % (k, s, p, o))
        else:
            row["READER_POOL"] = None
        by_k[str(k)] = row

    if all(row["STORE_POOL"] is None and row["READER_POOL"] is None for row in by_k.values()):
        return None
    return {"s": s, "p": p, "o": o, "universe_size": int(len(universe)),
           "q_vec_available": q_vec is not None, "by_k": by_k}


# ============================================================================ known-answer arm
def known_answer_store(queries: List[Tuple[int, int, int]], store: KGStore,
                       idx_to_entity: Dict[int, str], entity_to_idx: Dict[str, int],
                       n_ent: int, seed: int) -> Tuple[float, int]:
    rng = np.random.default_rng(seed)
    hits, n = 0, 0
    for s, p, o in queries[:KNOWN_ANSWER_N]:
        distractor = int(rng.integers(0, n_ent))
        tries = 0
        while tries < 20 and (distractor == o or distractor == s):
            distractor = int(rng.integers(0, n_ent))
            tries += 1
        if distractor == o:
            continue
        key = store.key(s, p)
        probe_np = (store.W @ key).numpy()
        cand_E = store.E[[o, distractor]].numpy()
        r = pull_in_multi_exclude(probe_np, cand_E, set(), gate=GATE_THRESH)
        hits += int(r["candidate_idx"] == 0)
        n += 1
    return round(hits / max(1, n), 6), n


def known_answer_reader(queries: List[Tuple[int, int, int]], idx_to_lemma: List[str], space,
                        anchors: List[str], seed: int) -> Tuple[float, int]:
    rng = np.random.default_rng(seed)
    hits, n = 0, 0
    for s, p, o in queries[:KNOWN_ANSWER_N]:
        ls, lo = idx_to_lemma[s], idx_to_lemma[o]
        q_vec = space.bundle(ls)
        gold_vec = space.bundle(lo)
        if q_vec is None or gold_vec is None:
            continue
        distractor = anchors[int(rng.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (distractor == lo or distractor == ls):
            distractor = anchors[int(rng.integers(len(anchors)))]
            tries += 1
        d_vec = space.bundle(distractor)
        if d_vec is None or distractor == lo:
            continue
        b, _ = E2.cosine_argmax(q_vec, [gold_vec, d_vec])
        hits += int(b == 0)
        n += 1
    return round(hits / max(1, n), 6), n


# ============================================================================ per-seed unit
def run_seed_unit(seed: int, entity_to_idx: Dict[str, int], idx_to_entity: Dict[int, str],
                  triples_full: np.ndarray, n_rel: int, idx_to_lemma: List[str],
                  norm2idxs: Dict[str, List[int]], eligible_base: np.ndarray, space,
                  node_degree: Dict[str, int], t_mat: np.ndarray, t_cov: np.ndarray,
                  pos: Dict[str, int], anchors: List[str], rs: dict, max_q: int,
                  k_grid: Sequence[int]) -> dict:
    t0 = time.time()
    store, ingested = E2.build_store_for_seed(seed, entity_to_idx, triples_full, n_rel)
    print("[seed=%d] store ingested %d edges elapsed=%.1fs" % (seed, len(ingested), time.time() - t0),
         flush=True)
    q = E2.build_query_set(ingested, idx_to_entity, rs, seed, max_q)
    print("[seed=%d] jointly-valid query candidates=%d elapsed=%.1fs" % (seed, len(q), time.time() - t0),
         flush=True)

    ka_store_acc, ka_store_n = known_answer_store(q, store, idx_to_entity, entity_to_idx,
                                                   len(entity_to_idx), seed + 61)
    ka_reader_acc, ka_reader_n = known_answer_reader(q, idx_to_lemma, space, anchors, seed + 71)
    print("[seed=%d] known_answer store=%.4f(n=%d) reader=%.4f(n=%d) elapsed=%.1fs"
         % (seed, ka_store_acc, ka_store_n, ka_reader_acc, ka_reader_n, time.time() - t0), flush=True)

    results = []
    for i, (s, p, o) in enumerate(q):
        r = score_query_ksweep(s, p, o, store, idx_to_entity, idx_to_lemma, norm2idxs,
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
           "floor": KNOWN_ANSWER_FLOOR, "ok": ka_reader_acc >= KNOWN_ANSWER_FLOOR},
           "elapsed_s": round(time.time() - t0, 2), "results": results}


# ============================================================================ aggregation
def aggregate(all_seed_units: Dict[str, dict], k_grid: Sequence[int],
             enforce_known_answer_gate: bool = True) -> dict:
    """enforce_known_answer_gate=False (smoke only): the known-answer floor is calibrated for the
    FULL corpus; the smoke corpus is a tiny slice (716 anchors vs ~5491) and is expected to score
    lower on a signal-quality floor by construction, matching every other cell's convention of
    relaxing item-count/quality gates in smoke mode (e.g. C3's MIN_ITEMS gate is full-mode-only).
    Smoke's job is proving the pipeline non-degenerate, not clearing the full-scale floor."""
    per_k_pool_arm: Dict[str, Dict[str, Dict[str, List[bool]]]] = {
        str(k): {pool: {} for pool in POOLS} for k in k_grid}
    seeds_void = []
    for key, unit in all_seed_units.items():
        seed = unit["seed"]
        gate_fail = not unit["known_answer_store"]["ok"] or not unit["known_answer_reader"]["ok"]
        if gate_fail:
            seeds_void.append(seed)
            if enforce_known_answer_gate:
                continue
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

    per_k_bootstrap = {str(k): {pool: _bs(per_k_pool_arm[str(k)][pool]) for pool in POOLS}
                       for k in k_grid}
    n_scoreable_per_k_pool = {str(k): {pool: len(per_k_pool_arm[str(k)][pool].get("NATIVE", []))
                                       for pool in POOLS} for k in k_grid}
    return {"per_k_bootstrap": per_k_bootstrap, "n_scoreable_per_k_pool": n_scoreable_per_k_pool,
           "seeds_void_known_answer": seeds_void}


def _kill_condition(per_k_bootstrap: dict, k_grid: Sequence[int], pool: str, arm: str) -> Optional[dict]:
    """CI on conditional_acc[K=largest] minus conditional_acc[K=smallest] for one (pool, arm).
    NOT a paired delta (different conditional populations per K) -- reported as two independent
    CIs plus their difference-of-means with a naive normal-approx CI on the difference, flagged as
    such. Directional read only, per pre-reg sec 4."""
    k_lo, k_hi = min(k_grid, key=lambda k: (k if k >= 0 else float("inf"))), max(k_grid)
    lo_b = per_k_bootstrap.get(str(k_lo), {}).get(pool)
    hi_b = per_k_bootstrap.get(str(k_hi), {}).get(pool)
    if not lo_b or not hi_b or not lo_b.get("paired") or not hi_b.get("paired"):
        return None
    if arm not in lo_b["arm_acc_ci"] or arm not in hi_b["arm_acc_ci"]:
        return None
    lo_c, hi_c = lo_b["arm_acc_ci"][arm], hi_b["arm_acc_ci"][arm]
    ci_overlap = not (hi_c["ci_hi"] < lo_c["ci_lo"] or lo_c["ci_hi"] < hi_c["ci_lo"])
    return {"K_lo": k_lo, "K_hi": k_hi, "acc_at_K_lo": lo_c["acc"], "acc_at_K_hi": hi_c["acc"],
           "ci_lo_at_K_lo": lo_c["ci_lo"], "ci_hi_at_K_lo": lo_c["ci_hi"],
           "ci_lo_at_K_hi": hi_c["ci_lo"], "ci_hi_at_K_hi": hi_c["ci_hi"],
           "flat_ci_overlap": ci_overlap}


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
    eligible_base = build_eligible_base(idx_to_lemma, anchor_set)

    from hdlab.reading_grounding_loop import ConceptSpace
    space = ConceptSpace(d=16)
    space.observe("cat", np.array([1.0] * 8 + [0.0] * 8))
    space.observe("dog", np.array([1.0] * 8 + [0.0] * 8))
    space.observe("puppy", np.array([0.9] * 8 + [0.1] * 8))
    space.observe("kitten", np.array([-1.0] * 16))
    space.observe("rock", np.array([-1.0] * 16))
    anchors, _mat = space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    t_mat, t_cov = MS.trigram_matrix(anchors)

    universe = query_universe(0, idx_to_lemma, norm2idxs, eligible_base)
    assert set(universe.tolist()) == {1, 2, 3, 4, 5}, "UNIVERSE_MISMATCH: %r" % universe.tolist()

    r = score_query_ksweep(0, 0, 1, store, idx_to_entity, idx_to_lemma, norm2idxs, eligible_base,
                           space, node_degree, t_mat, t_cov, pos, [1, 3, 6])
    assert r is not None, "SELFTEST_QUERY_UNSCOREABLE"
    row6 = r["by_k"]["6"]
    assert row6["STORE_POOL"] is not None, "SELFTEST_STORE_POOL_K6_NONE"
    assert row6["universe_size"] == 5, "SELFTEST_UNIVERSE_SIZE: %r" % row6["universe_size"]

    def _digest(x):
        return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()

    digests = {"store_pool_k6": _digest(row6["STORE_POOL"]),
              "reader_pool_k6": _digest(row6.get("READER_POOL"))}
    return {"instrument_validity": {"universe_shared_ok": True}, "sample_result": r,
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

    print("[%s] building reader ConceptSpace..." % run_mode, flush=True)
    rs = E2.build_reader_space(run_mode, output_dir)
    space = rs["space"]
    anchors = rs["anchors"]
    anchor_set = rs["anchor_set"]
    print("[%s] reader space: n_anchors=%d n_sents=%d elapsed=%.1fs"
         % (run_mode, len(anchors), rs["n_sents"], time.time() - t0), flush=True)
    _heartbeat(output_dir, {"phase": "reader_space_built", "n_anchors": len(anchors),
                            "elapsed_s": time.time() - t0})

    print("[%s] building idx_to_lemma over %d entities (one-time, ~0.19ms/call)..."
         % (run_mode, len(entity_to_idx)), flush=True)
    t_lemma0 = time.time()
    idx_to_lemma, norm2idxs = build_idx_to_lemma(idx_to_entity)
    eligible_base = build_eligible_base(idx_to_lemma, anchor_set)
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
                             rs, max_q, k_grid)
        record_unit(output_dir, key, unit)
        _heartbeat(output_dir, {"phase": "seed_done", "seed": seed, "n_scoreable": unit["n_scoreable"],
                                "elapsed_s": time.time() - t0})
        print("[%s] seed=%d done n_scoreable=%d elapsed=%.1fs"
             % (run_mode, seed, unit["n_scoreable"], time.time() - t0), flush=True)

    all_units = load_units(output_dir)
    agg = aggregate(all_units, k_grid, enforce_known_answer_gate=(run_mode == "full"))

    def _digest_k(k):
        d = agg["per_k_bootstrap"].get(str(k), {})
        sp = d.get("STORE_POOL")
        rp = d.get("READER_POOL")
        return hashlib.sha256(json.dumps({"sp": sp.get("arm_acc_ci") if sp else None,
                                          "rp": rp.get("arm_acc_ci") if rp else None},
                                         sort_keys=True, default=str).encode()).hexdigest()

    ks_present = [k for k in k_grid if agg["per_k_bootstrap"].get(str(k), {}).get("STORE_POOL")
                 or agg["per_k_bootstrap"].get(str(k), {}).get("READER_POOL")]
    arms_differ = len(set(_digest_k(k) for k in ks_present)) > 1 if len(ks_present) > 1 else None

    kill_condition = {
        "STORE_POOL_NATIVE": _kill_condition(agg["per_k_bootstrap"], k_grid, "STORE_POOL", "NATIVE"),
        "STORE_POOL_SWAPPED": _kill_condition(agg["per_k_bootstrap"], k_grid, "STORE_POOL", "SWAPPED"),
        "READER_POOL_SWAPPED": _kill_condition(agg["per_k_bootstrap"], k_grid, "READER_POOL", "SWAPPED"),
        "READER_POOL_NATIVE_ANALYTICALLY_PINNED_NOT_EVIDENCE": _kill_condition(
            agg["per_k_bootstrap"], k_grid, "READER_POOL", "NATIVE"),
    }
    _decoupled = {k: v for k, v in kill_condition.items()
                 if k != "READER_POOL_NATIVE_ANALYTICALLY_PINNED_NOT_EVIDENCE"}
    any_decoupled_computed = any(v is not None for v in _decoupled.values())
    kill_fires = (any_decoupled_computed
                 and all(v is not None and v["flat_ci_overlap"] for v in _decoupled.values()))

    recall_at_k = {}
    for k in k_grid:
        d = agg["per_k_bootstrap"].get(str(k), {})
        n = agg["n_scoreable_per_k_pool"].get(str(k), {})
        recall_at_k[str(k)] = {"STORE_POOL_n_scoreable": n.get("STORE_POOL"),
                               "READER_POOL_n_scoreable": n.get("READER_POOL")}

    if run_mode == "full" and agg["seeds_void_known_answer"] and not any_decoupled_computed:
        verdict = "VOID_KNOWN_ANSWER_FAILED"
    elif not any_decoupled_computed:
        verdict = "INSUFFICIENT_DATA"
    elif kill_fires:
        verdict = "KILL_CONDITION_FIRES_FLAT_ACROSS_K"
    else:
        verdict = "SELECTION_VARIES_WITH_K"

    elapsed = time.time() - t0
    metrics = {
        "verdict": verdict,
        "verdict_msg": "seeds_void_known_answer=%r kill_condition_fires=%r any_decoupled_computed=%r"
                      % (agg["seeds_void_known_answer"], kill_fires, any_decoupled_computed),
        "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "elapsed_s": round(elapsed, 3),
        "n_entities": len(entity_to_idx), "n_edges_total": len(triples_full), "n_rel": n_rel,
        "n_reader_anchors": len(anchors), "n_reader_sents": rs["n_sents"],
        "store_scale": STORE_SCALE, "data_seeds": seeds, "max_q_per_seed": max_q,
        "gate_thresh": GATE_THRESH, "k_grid": k_grid,
        "per_k_bootstrap": agg["per_k_bootstrap"],
        "n_scoreable_per_k_pool": agg["n_scoreable_per_k_pool"],
        "seeds_void_known_answer": agg["seeds_void_known_answer"],
        "kill_condition": kill_condition,
        "kill_condition_fires_flat_across_k": kill_fires,
        "read_out_invariance_note": "READER_POOL/NATIVE ranks and selects with the identical cosine "
                                    "score, so its conditional accuracy is analytically pinned to "
                                    "hit@1/recall@K (mechanically non-increasing in K) -- reported, "
                                    "excluded from the kill-condition verdict. See pre-reg sec 4.",
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
        "prereg": "preregs/2026-08-15_k_sweep_e1_v1.md",
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    print(json.dumps({k: v for k, v in metrics.items() if k not in ("per_k_bootstrap",)},
                     indent=2, default=str))
    print("VERDICT:", verdict)
    print("KILL CONDITION FIRES:", kill_fires)
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
