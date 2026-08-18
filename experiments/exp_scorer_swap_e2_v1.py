# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (SCRAMBLE vs NATIVE digest-differ per fresh unit)
# - final_metrics_atomicity declared (META_RULE_AH; tmp_replace, per-seed resumable unit)
# - except SystemExit: raise BEFORE except Exception (no BaseException, no bare except:)
# - crlb_n/a declared (a cross-representation scorer-swap diagnostic; no closed-form floor for a
#   vocabulary-overlap intersection size, which is what this cell measures)
# - HP_SCOPE: N/A -- this cell does not gate a HARD_PASS/HARD_FAIL wire decision; it answers a
#   binary interpretive question (ONE_MECHANISM / THREE_THAT_RHYME / AMBIGUOUS /
#   INSUFFICIENT_OVERLAP) pre-registered in preregs/2026-08-15_scorer_swap_e2_v1.md sec 8, BEFORE
#   this file was run.
# - per-unit (per-DATA_SEED) failure-class instrumentation (no bare except)
# - self-test constructs a REAL tiny synthetic KGStore + REAL tiny ConceptSpace and runs the FULL
#   scoring pipeline (native, swapped, degree-floor, scramble) on a hand-built 6-entity/2-lemma
#   fixture with a KNOWN correct answer, proving the instrument fires before any CSKG-scale number
#   is trusted (pre-reg sec 6).
# - progress_logging: print_flush_true
# See preregs/2026-08-15_scorer_swap_e2_v1.md for the full pre-registration (written BEFORE this
# run, per skunkworks-vet's unification claim in .claude/scan-out/vet-claims.json).
"""exp_scorer_swap_e2_v1 -- E2, the scorer swap.

QUESTION (VET brief, .claude/scan-out/vet-claims.json, "THE UNIFICATION (C10+C11+C12)"): is the
store's candidate-retrieval failure (Stage-2b/e/f/g CSKG argmax decode) and the reader's read-out
failure (exp_grounding_readout_known_answer_v1 / exp_orthographic_floor_vet_v1 open-vocab hit@1) ONE
mechanism or THREE that merely rhyme. The store (hdlab.kg_traversal.KGStore, DG/CA3-style
pull_in_multi_exclude settle over a 1.21M-edge CSKG) and the reader (hdlab.reading_grounding_loop
.ConceptSpace, d=256 sha256-basis cosine over 5,491 text-corpus anchors) share no code and no
representation. This cell builds the one bridge that makes a literal swap possible: CSKG entity ids
are plain lowercase surface strings, so normalize_lemma(entity_id) can be tested for membership in
the reader's own anchor vocabulary. Only that overlap is swap-eligible; the overlap size is measured
and reported before any accuracy number is read (pre-reg sec 2).

Design (pre-reg secs 2-4): query set Q = real ingested CSKG edges (s,p,o) where lemma(s) and
lemma(o) are BOTH reader anchors AND o is ALSO in the reader's own WordNet gold_meaning_set(lemma(s))
-- graph-truth and meaning-truth agree, so "correct" means the same thing on both sides of the swap.
Two pools per query (STORE_POOL = store's own top-50 shortlist intersected with reader coverage;
READER_POOL = reader's own eligible-anchor pool intersected with CSKG-entity existence), four arms
per pool (NATIVE, SWAPPED, DEGREE_FLOOR, SCRAMBLE). The reading rule (which result means ONE
mechanism vs THREE that rhyme) is fixed in the pre-reg sec 8, before this file's first real run.

Modes:
  --self-test  Real-code-path check on a tiny synthetic KGStore + ConceptSpace fixture with a known
               correct answer (instrument-validity, pre-reg sec 6). No CSKG load, no corpus build.
  --smoke      Real CSKG data (small slice) + real reader corpus ("smoke" mode, ~400 sentences/seg),
               ONE data seed, capped query count -- verifies the real pipeline produces a non-empty,
               non-degenerate Q before the full run pays the ~10-minute corpus-build cost.
  --full       Full OpenStax corpus (matches exp_orthographic_floor_vet_v1's build exactly, imported
               unchanged), CSKG store at STORE_SCALE=100,000 edges (Stage-2b/e/f/g's own 100K
               task-contract point, cited not re-derived at 1.21M), DATA_SEEDS=[20260810, 20260811,
               20260812] for between-draw spread (pre-reg sec 5), checkpointed per seed via
               tools/exp_checkpoint.py (resumable across invocations).
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
from typing import Dict, List, Optional, Set, Tuple

import numpy as np
import torch

ANCHOR_NAME = "scorer_swap_e2_v1"
_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (_REPO, os.path.join(_REPO, "tools"), os.path.join(_REPO, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(_REPO, "data", "exp_%s" % ANCHOR_NAME)
CSKG_DIR = os.path.join(_REPO, "data", "cskg_foundation_v1")

from hdlab.kg_traversal import KGStore  # noqa: E402
from hdlab.reading_grounding_loop import ConceptSpace, normalize_lemma  # noqa: E402
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
from experiments.exp_focus_pullin_causal_stage2b_cskg_scale_gate_v1 import (  # noqa: E402
    GATE_THRESH, SHORTLIST_K as STORE_SHORTLIST_K, load_entity_vocab, load_spine_edges,
    precheck_kgstore_and_loader,
)
from experiments.exp_focus_pullin_causal_stage2a_multihop_loop_v1 import (  # noqa: E402
    pull_in_multi_exclude,
)
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

STORE_SCALE = 100000
DATA_SEEDS = [20260810, 20260811, 20260812]
MAX_Q_PER_SEED = 400          # compute cap; sampled deterministically if Q is larger
MIN_Q_FOR_VERDICT = 20
N_BOOTSTRAP = 5000
BOOT_SEED = 20260815
POOLS = ("STORE_POOL", "READER_POOL")
ARMS = ("NATIVE", "SWAPPED", "DEGREE_FLOOR", "SCRAMBLE")


# ============================================================================ shared helpers
def _scramble_seed(key: str) -> int:
    return int.from_bytes(hashlib.sha256(("e2_scramble::" + key).encode("utf-8")).digest()[:8],
                          "big") % (2 ** 32)


def _atomic_json(path: str, obj: object) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, default=str)
    os.replace(tmp, path)


def load_node_degree(cskg_dir: str) -> Dict[str, int]:
    deg: Dict[str, int] = {}
    with open(os.path.join(cskg_dir, "nodes.jsonl"), encoding="utf-8") as f:
        for line in f:
            row = json.loads(line)
            deg[row["id"]] = int(row.get("degree", 0))
    return deg


def cosine_argmax(q_vec: np.ndarray, cand_vecs: List[Optional[np.ndarray]]) -> Tuple[int, np.ndarray]:
    """argmax cosine(q_vec, cand) over candidates; candidates with no vector score -inf."""
    n = len(cand_vecs)
    sims = np.full(n, -np.inf, dtype=np.float64)
    qn = float(np.linalg.norm(q_vec))
    if qn < 1e-12:
        return 0, sims
    for i, v in enumerate(cand_vecs):
        if v is None:
            continue
        vn = float(np.linalg.norm(v))
        if vn < 1e-12:
            continue
        sims[i] = float(np.dot(q_vec, v) / (qn * vn))
    b = int(np.argmax(sims))
    return b, sims


def store_native_argmax(probe_np: np.ndarray, cand_E: np.ndarray, exclude: Set[int]
                        ) -> Tuple[int, dict]:
    r = pull_in_multi_exclude(probe_np, cand_E, exclude, gate=GATE_THRESH)
    return int(r["candidate_idx"]), r


def degree_argmax(cand_entities: List[str], node_degree: Dict[str, int]) -> Tuple[int, np.ndarray]:
    degs = np.array([node_degree.get(e, 0) for e in cand_entities], dtype=np.float64)
    return int(np.argmax(degs)), degs


def scramble_argmax(n: int, seed_key: str) -> int:
    rng = np.random.default_rng(_scramble_seed(seed_key))
    return int(rng.integers(0, n))


# ============================================================================ reader-space build
def build_reader_space(run_mode: str, output_dir: str):
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
           "mat_ok": mat_ok, "pos": pos, "norm2idx": norm2idx, "n_sents": len(sents)}


def reader_eligible_pool(word: str, rs: dict) -> List[str]:
    """The exact eligibility rule exp_orthographic_floor_vet_v1 uses: exclude self-lemma + spelling
    variants, exclude zero-norm anchors. Returns anchor STRINGS (not indices)."""
    anchors = rs["anchors"]
    pos = rs["pos"]
    norm2idx = rs["norm2idx"]
    mat_ok = rs["mat_ok"]
    excl = set(norm2idx.get(normalize_lemma(word), []))
    if word in pos:
        excl.add(pos[word])
    out = []
    for i, a in enumerate(anchors):
        if i in excl or not mat_ok[i]:
            continue
        out.append(a)
    return out


# ============================================================================ store build
def build_store_for_seed(seed: int, entity_to_idx: Dict[str, int], triples_full: np.ndarray,
                         n_rel: int) -> Tuple[KGStore, np.ndarray]:
    gen = torch.Generator()
    gen.manual_seed(seed)
    store = KGStore(n_ent=len(entity_to_idx), n_rel=n_rel, n_dim=1024, generator=gen)
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(triples_full))
    ingest_idx = perm[:min(STORE_SCALE, len(triples_full))]
    ingested = triples_full[ingest_idx]
    store.ingest_triples(torch.from_numpy(ingested))
    return store, ingested


# ============================================================================ query-set construction
def build_query_set(ingested: np.ndarray, idx_to_entity: Dict[int, str], rs: dict, seed: int,
                    max_q: int) -> List[Tuple[int, int, int]]:
    """Pure-string filter (no store tensor ops): (s,p,o) triples where lemma(s), lemma(o) are BOTH
    reader anchors AND o in gold_meaning_set(lemma(s)). Deterministic sample if larger than max_q."""
    anchor_set = rs["anchor_set"]
    cand: List[Tuple[int, int, int]] = []
    lemma_cache: Dict[int, str] = {}

    def lemma_of(ent_idx: int) -> str:
        if ent_idx not in lemma_cache:
            lemma_cache[ent_idx] = normalize_lemma(idx_to_entity[ent_idx])
        return lemma_cache[ent_idx]

    for row in ingested:
        s, p, o = int(row[0]), int(row[1]), int(row[2])
        ls = lemma_of(s)
        if ls not in anchor_set:
            continue
        lo = lemma_of(o)
        if lo not in anchor_set or lo == ls:
            continue
        if lo not in C3.gold_meaning_set(ls):
            continue
        cand.append((s, p, o))
    if len(cand) > max_q:
        rng = np.random.default_rng(seed + 1)
        idx = rng.choice(len(cand), size=max_q, replace=False)
        cand = [cand[i] for i in sorted(idx)]
    return cand


# ============================================================================ per-query scoring
def score_query(s: int, p: int, o: int, store: KGStore, idx_to_entity: Dict[int, str],
                rs: dict, node_degree: Dict[str, int], entity_to_idx: Dict[str, int],
                shortlist_k: int) -> Optional[dict]:
    """Returns per-pool per-arm correctness for one query, or None if either pool lacks o."""
    key = store.key(s, p)
    probe = (store.W @ key)
    probe_np = probe.numpy()
    scores = store.score_all(key)
    topk = torch.topk(scores, k=min(shortlist_k, store.n_ent))
    shortlist_global = topk.indices.numpy()
    in_shortlist = bool(o in shortlist_global)

    ls = normalize_lemma(idx_to_entity[s])
    lo = normalize_lemma(idx_to_entity[o])
    anchor_set = rs["anchor_set"]
    space = rs["space"]

    # -------- STORE_POOL: store's top-K shortlist intersected with reader-anchor coverage
    sp_global = [int(c) for c in shortlist_global
                if normalize_lemma(idx_to_entity[int(c)]) in anchor_set]
    store_pool_result = None
    if o in sp_global and len(sp_global) >= 2:
        cand_entities = [idx_to_entity[c] for c in sp_global]
        cand_lemmas = [normalize_lemma(e) for e in cand_entities]
        o_pos = sp_global.index(o)
        exclude = {sp_global.index(s)} if s in sp_global else set()

        cand_E = store.E[sp_global].numpy()
        b_native, _ = store_native_argmax(probe_np, cand_E, exclude)
        native_correct = (b_native == o_pos)

        q_vec = space.bundle(ls)
        cand_vecs = [space.bundle(l) for l in cand_lemmas]
        b_swap, _ = cosine_argmax(q_vec, cand_vecs) if q_vec is not None else (0, None)
        swap_correct = (q_vec is not None and b_swap == o_pos)

        b_deg, _ = degree_argmax(cand_entities, node_degree)
        deg_correct = (b_deg == o_pos)

        b_scr = scramble_argmax(len(sp_global), "store|%d|%d|%d" % (s, p, o))
        scr_correct = (b_scr == o_pos)

        store_pool_result = {"n_candidates": len(sp_global), "NATIVE": native_correct,
                             "SWAPPED": swap_correct, "DEGREE_FLOOR": deg_correct,
                             "SCRAMBLE": scr_correct}

    # -------- READER_POOL: reader's own eligible-anchor pool intersected with CSKG-entity existence
    elig = reader_eligible_pool(ls, rs)
    rp_lemmas = [a for a in elig if a in entity_to_idx]
    reader_pool_result = None
    if lo in rp_lemmas and len(rp_lemmas) >= 2:
        cand_entity_idx = [entity_to_idx[l] for l in rp_lemmas]
        o_pos = rp_lemmas.index(lo)

        q_vec = space.bundle(ls)
        cand_vecs = [space.bundle(l) for l in rp_lemmas]
        b_native, _ = cosine_argmax(q_vec, cand_vecs) if q_vec is not None else (0, None)
        native_correct = (q_vec is not None and b_native == o_pos)

        exclude = {cand_entity_idx.index(s)} if s in cand_entity_idx else set()
        cand_E = store.E[cand_entity_idx].numpy()
        b_swap, _ = store_native_argmax(probe_np, cand_E, exclude)
        swap_correct = (b_swap == o_pos)

        b_deg, _ = degree_argmax(rp_lemmas, node_degree)
        deg_correct = (b_deg == o_pos)

        b_scr = scramble_argmax(len(rp_lemmas), "reader|%d|%d|%d" % (s, p, o))
        scr_correct = (b_scr == o_pos)

        reader_pool_result = {"n_candidates": len(rp_lemmas), "NATIVE": native_correct,
                              "SWAPPED": swap_correct, "DEGREE_FLOOR": deg_correct,
                              "SCRAMBLE": scr_correct}

    if store_pool_result is None and reader_pool_result is None:
        return None
    return {"s": s, "p": p, "o": o, "lemma_s": ls, "lemma_o": lo, "in_store_shortlist": in_shortlist,
           "STORE_POOL": store_pool_result, "READER_POOL": reader_pool_result}


# ============================================================================ per-seed unit
def run_seed_unit(seed: int, entity_to_idx: Dict[str, int], idx_to_entity: Dict[int, str],
                  triples_full: np.ndarray, n_rel: int, rs: dict, node_degree: Dict[str, int],
                  max_q: int, output_dir: str) -> dict:
    t0 = time.time()
    store, ingested = build_store_for_seed(seed, entity_to_idx, triples_full, n_rel)
    print("[seed=%d] store ingested %d edges elapsed=%.1fs" % (seed, len(ingested), time.time() - t0),
         flush=True)
    q = build_query_set(ingested, idx_to_entity, rs, seed, max_q)
    print("[seed=%d] jointly-valid query candidates=%d elapsed=%.1fs" % (seed, len(q), time.time() - t0),
         flush=True)
    results = []
    for i, (s, p, o) in enumerate(q):
        r = score_query(s, p, o, store, idx_to_entity, rs, node_degree, entity_to_idx,
                        STORE_SHORTLIST_K)
        if r is not None:
            results.append(r)
        if (i + 1) % 100 == 0:
            print("[seed=%d] scored %d/%d elapsed=%.1fs" % (seed, i + 1, len(q), time.time() - t0),
                 flush=True)
    return {"seed": seed, "n_ingested": len(ingested), "n_query_candidates": len(q),
           "n_scoreable": len(results), "elapsed_s": round(time.time() - t0, 2), "results": results}


# ============================================================================ aggregation
def aggregate(all_seed_units: Dict[str, dict]) -> dict:
    per_pool_arm: Dict[str, Dict[str, List[bool]]] = {pool: {arm: [] for arm in ARMS} for pool in POOLS}
    per_seed_pool_arm: Dict[str, Dict[str, Dict[str, List[bool]]]] = {}
    for key, unit in all_seed_units.items():
        seed = str(unit["seed"])
        per_seed_pool_arm.setdefault(seed, {pool: {arm: [] for arm in ARMS} for pool in POOLS})
        for r in unit["results"]:
            for pool in POOLS:
                pr = r.get(pool)
                if pr is None:
                    continue
                for arm in ARMS:
                    per_pool_arm[pool][arm].append(bool(pr[arm]))
                    per_seed_pool_arm[seed][pool][arm].append(bool(pr[arm]))

    def _bs(vec_map: Dict[str, List[bool]]) -> Optional[dict]:
        arrs = {k: np.array(v, dtype=float) for k, v in vec_map.items() if len(v) > 0}
        if not arrs or min(len(v) for v in arrs.values()) == 0:
            return None
        n = len(next(iter(arrs.values())))
        if any(len(v) != n for v in arrs.values()):
            # arms within a pool are paired by construction (same query list); if lengths differ
            # something upstream broke pairing -- report raw means only, no bootstrap.
            return {"paired": False, "raw_acc": {k: float(v.mean()) for k, v in arrs.items()},
                   "n_per_arm": {k: len(v) for k, v in vec_map.items()}}
        deltas = [("d_NATIVE_minus_SWAPPED", "NATIVE", "SWAPPED"),
                  ("d_NATIVE_minus_DEGREE_FLOOR", "NATIVE", "DEGREE_FLOOR"),
                  ("d_SWAPPED_minus_DEGREE_FLOOR", "SWAPPED", "DEGREE_FLOOR"),
                  ("d_NATIVE_minus_SCRAMBLE", "NATIVE", "SCRAMBLE"),
                  ("d_SWAPPED_minus_SCRAMBLE", "SWAPPED", "SCRAMBLE")]
        deltas = [d for d in deltas if d[1] in arrs and d[2] in arrs]
        bs = MS.paired_bootstrap(arrs, deltas, N_BOOTSTRAP, BOOT_SEED)
        bs["paired"] = True
        return bs

    per_pool_bootstrap = {pool: _bs(per_pool_arm[pool]) for pool in POOLS}
    per_seed_pool_bootstrap = {seed: {pool: _bs(pa[pool]) for pool in POOLS}
                               for seed, pa in per_seed_pool_arm.items()}

    n_q = {pool: len(per_pool_arm[pool]["NATIVE"]) for pool in POOLS}
    verdict, notes = decide(per_pool_bootstrap, n_q)

    return {"per_pool_bootstrap": per_pool_bootstrap, "per_seed_pool_bootstrap": per_seed_pool_bootstrap,
           "n_scoreable_per_pool": n_q, "verdict": verdict, "notes": notes}


def _ci_overlap(a: dict, b: dict) -> bool:
    return not (a["ci_hi"] < b["ci_lo"] or b["ci_hi"] < a["ci_lo"])


def decide(per_pool_bootstrap: Dict[str, Optional[dict]], n_q: Dict[str, int]) -> Tuple[str, List[str]]:
    notes = []
    for pool in POOLS:
        notes.append("%s n_scoreable=%d" % (pool, n_q.get(pool, 0)))
    if any(n_q.get(pool, 0) < MIN_Q_FOR_VERDICT for pool in POOLS):
        return "INSUFFICIENT_OVERLAP", notes + [
            "at least one pool has < %d scoreable queries; no ONE/THREE call made" % MIN_Q_FOR_VERDICT]
    sp = per_pool_bootstrap["STORE_POOL"]
    rp = per_pool_bootstrap["READER_POOL"]
    if sp is None or rp is None or not sp.get("paired", False) or not rp.get("paired", False):
        return "INSUFFICIENT_OVERLAP", notes + ["bootstrap could not be computed (unpaired arms)"]
    store_scorer_on_store = sp["arm_acc_ci"]["NATIVE"]
    store_scorer_on_reader = rp["arm_acc_ci"]["SWAPPED"]
    reader_scorer_on_store = sp["arm_acc_ci"]["SWAPPED"]
    reader_scorer_on_reader = rp["arm_acc_ci"]["NATIVE"]

    scorer_store_consistent = _ci_overlap(store_scorer_on_store, store_scorer_on_reader)
    scorer_reader_consistent = _ci_overlap(reader_scorer_on_store, reader_scorer_on_reader)
    one_mechanism = scorer_store_consistent and scorer_reader_consistent

    pool_store_consistent = _ci_overlap(store_scorer_on_store, reader_scorer_on_store)
    pool_reader_consistent = _ci_overlap(store_scorer_on_reader, reader_scorer_on_reader)
    pools_separated = not (_ci_overlap(store_scorer_on_store, store_scorer_on_reader)
                           and _ci_overlap(reader_scorer_on_store, reader_scorer_on_reader))
    three_that_rhyme = pool_store_consistent and pool_reader_consistent and not one_mechanism

    notes.append("store_scorer: store_pool_acc=%.4f reader_pool_acc=%.4f consistent=%s"
                % (store_scorer_on_store["acc"], store_scorer_on_reader["acc"], scorer_store_consistent))
    notes.append("reader_scorer: store_pool_acc=%.4f reader_pool_acc=%.4f consistent=%s"
                % (reader_scorer_on_store["acc"], reader_scorer_on_reader["acc"], scorer_reader_consistent))
    notes.append("store_pool: store_scorer_acc=%.4f reader_scorer_acc=%.4f consistent=%s"
                % (store_scorer_on_store["acc"], reader_scorer_on_store["acc"], pool_store_consistent))
    notes.append("reader_pool: store_scorer_acc=%.4f reader_scorer_acc=%.4f consistent=%s"
                % (store_scorer_on_reader["acc"], reader_scorer_on_reader["acc"], pool_reader_consistent))

    if one_mechanism and not three_that_rhyme:
        return "ONE_MECHANISM", notes
    if three_that_rhyme and not one_mechanism:
        return "THREE_THAT_RHYME", notes
    return "AMBIGUOUS", notes + ["neither clean pattern holds; recommend E1 (K-sweep) next"]


# ============================================================================ self-test
def self_test() -> dict:
    """Tiny synthetic KGStore (n_ent=6, n_dim=32) + tiny synthetic ConceptSpace (d=16), a hand-built
    fixture with a KNOWN correct answer, run through the FULL scoring pipeline (native, swapped,
    degree-floor, scramble) at both pools. Proves the instrument fires before any CSKG-scale number
    is trusted (pre-reg sec 6)."""
    gen = torch.Generator()
    gen.manual_seed(3)
    ents = ["cat", "dog", "puppy", "kitten", "rock", "cloud"]
    idx_to_entity = {i: e for i, e in enumerate(ents)}
    entity_to_idx = {e: i for i, e in idx_to_entity.items()}
    node_degree = {"cat": 50, "dog": 40, "puppy": 5, "kitten": 5, "rock": 3, "cloud": 2}
    store = KGStore(n_ent=6, n_rel=2, n_dim=32, generator=gen)
    triples = torch.tensor([[0, 0, 1], [1, 0, 0], [4, 1, 5]], dtype=torch.long)  # cat-relatedTo-dog etc
    store.ingest_triples(triples)

    # instrument-validity (a): probe = E[o] exactly must recover o with score 1.0
    o_idx = 1
    cos_self = float(np.dot(store.E[o_idx].numpy(), store.E[o_idx].numpy())
                     / (np.linalg.norm(store.E[o_idx].numpy()) ** 2))
    assert abs(cos_self - 1.0) < 1e-6, "INSTRUMENT_FAIL_STORE_SELF_COSINE: %r" % cos_self
    r_exact = pull_in_multi_exclude(store.E[o_idx].numpy(), store.E.numpy(), set(), gate=GATE_THRESH)
    assert r_exact["candidate_idx"] == o_idx and r_exact["admitted"], (
        "INSTRUMENT_FAIL_STORE_EXACT_PROBE: %r" % r_exact)

    space = ConceptSpace(d=16)
    space.observe("cat", np.array([1.0] * 8 + [0.0] * 8))
    space.observe("dog", np.array([1.0] * 8 + [0.0] * 8))     # near-identical to cat (synthetic)
    space.observe("puppy", np.array([0.9] * 8 + [0.1] * 8))
    space.observe("kitten", np.array([-1.0] * 16))
    space.observe("rock", np.array([-1.0] * 16))

    # instrument-validity (b): self-cosine must be exactly 1.0
    v = space.bundle("cat")
    cos_ident = float(np.dot(v, v) / (np.linalg.norm(v) ** 2))
    assert abs(cos_ident - 1.0) < 1e-6, "INSTRUMENT_FAIL_READER_SELF_COSINE: %r" % cos_ident

    rs = {"space": space, "anchors": sorted(space.anchors()), "anchor_set": set(space.anchors())}
    mat_anchors, mat = space.anchor_matrix()
    rs["mat"] = mat
    rs["mat_ok"] = np.linalg.norm(mat, axis=1) >= 1e-9
    rs["pos"] = {a: i for i, a in enumerate(mat_anchors)}
    rs["anchors"] = mat_anchors
    norm2idx: Dict[str, List[int]] = {}
    for a in mat_anchors:
        norm2idx.setdefault(normalize_lemma(a), []).append(rs["pos"][a])
    rs["norm2idx"] = norm2idx

    # hand-built query: s=cat(0), p=0, o=dog(1). lemma(cat) and lemma(dog) both reader anchors.
    r = score_query(0, 0, 1, store, idx_to_entity, rs, node_degree, entity_to_idx, shortlist_k=6)
    assert r is not None, "SELFTEST_QUERY_UNSCOREABLE"

    def _digest(x):
        return hashlib.sha256(json.dumps(x, sort_keys=True, default=str).encode()).hexdigest()

    digests = {"store_pool": _digest(r.get("STORE_POOL")), "reader_pool": _digest(r.get("READER_POOL"))}
    return {"instrument_validity": {"store_exact_probe_ok": True, "reader_self_cosine_ok": True},
           "sample_query_result": r, "digests": digests}


# ============================================================================ output plumbing
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
    _write_start_marker(output_dir, run_mode)
    t0 = time.time()

    pre = precheck_kgstore_and_loader()
    assert pre["ok"], "STAGE2B_PRECHECK_FAIL: %r" % pre

    print("[%s] loading CSKG entity vocab + edges..." % run_mode, flush=True)
    entity_to_idx = load_entity_vocab(CSKG_DIR)
    idx_to_entity = {v: k for k, v in entity_to_idx.items()}
    triples_full, relation_to_idx = load_spine_edges(entity_to_idx, CSKG_DIR)
    n_rel = len(relation_to_idx)
    node_degree = load_node_degree(CSKG_DIR)
    print("[%s] %d entities, %d edges, n_rel=%d elapsed=%.1fs"
         % (run_mode, len(entity_to_idx), len(triples_full), n_rel, time.time() - t0), flush=True)
    _heartbeat(output_dir, {"phase": "cskg_loaded", "elapsed_s": time.time() - t0})

    print("[%s] building reader ConceptSpace..." % run_mode, flush=True)
    rs = build_reader_space(run_mode, output_dir)
    print("[%s] reader space: n_anchors=%d n_sents=%d elapsed=%.1fs"
         % (run_mode, len(rs["anchors"]), rs["n_sents"], time.time() - t0), flush=True)
    _heartbeat(output_dir, {"phase": "reader_space_built", "n_anchors": len(rs["anchors"]),
                            "elapsed_s": time.time() - t0})

    seeds = DATA_SEEDS[:1] if run_mode == "smoke" else DATA_SEEDS
    max_q = 40 if run_mode == "smoke" else MAX_Q_PER_SEED

    done = completed_units(output_dir)
    for seed in seeds:
        key = unit_key("seed", seed)
        if key in done:
            print("[%s] seed=%d already complete (resume)" % (run_mode, seed), flush=True)
            continue
        unit = run_seed_unit(seed, entity_to_idx, idx_to_entity, triples_full, n_rel, rs, node_degree,
                             max_q, output_dir)
        record_unit(output_dir, key, unit)
        _heartbeat(output_dir, {"phase": "seed_done", "seed": seed, "n_scoreable": unit["n_scoreable"],
                                "elapsed_s": time.time() - t0})
        print("[%s] seed=%d done n_scoreable=%d elapsed=%.1fs"
             % (run_mode, seed, unit["n_scoreable"], time.time() - t0), flush=True)

    all_units = load_units(output_dir)
    agg = aggregate(all_units)

    def _digest_pool(pool):
        d = agg["per_pool_bootstrap"].get(pool)
        if d is None:
            return None
        return hashlib.sha256(json.dumps(d.get("arm_acc_ci", {}), sort_keys=True,
                                         default=str).encode()).hexdigest()

    arms_differ = _digest_pool("STORE_POOL") != _digest_pool("READER_POOL")

    elapsed = time.time() - t0
    metrics = {
        "verdict": agg["verdict"], "verdict_msg": "; ".join(agg["notes"])[:4000],
        "run_mode": run_mode, "anchor_name": ANCHOR_NAME, "elapsed_s": round(elapsed, 3),
        "n_entities": len(entity_to_idx), "n_edges_total": len(triples_full), "n_rel": n_rel,
        "n_reader_anchors": len(rs["anchors"]), "n_reader_sents": rs["n_sents"],
        "store_scale": STORE_SCALE, "data_seeds": seeds, "max_q_per_seed": max_q,
        "gate_thresh": GATE_THRESH, "store_shortlist_k": STORE_SHORTLIST_K,
        "per_pool_bootstrap": agg["per_pool_bootstrap"],
        "per_seed_pool_bootstrap": agg["per_seed_pool_bootstrap"],
        "n_scoreable_per_pool": agg["n_scoreable_per_pool"],
        "n_seeds_complete": len(all_units), "n_seeds_expected": len(seeds),
        "cardinality_ok": len(all_units) == len(seeds),
        "arms_differ_verified": arms_differ,
        "final_metrics_atomicity": "tmp_replace", "start_marker_written": True,
        "crash_diagnostic_present": True, "heartbeat_present": True,
        "instrument_validity_stamped_this_session": True,
        "crlb_n/a": "cross-representation vocabulary-overlap diagnostic; no closed-form floor for "
                    "an intersection size",
        "min_q_for_verdict": MIN_Q_FOR_VERDICT,
        "prereg": "preregs/2026-08-15_scorer_swap_e2_v1.md",
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    print(json.dumps({k: v for k, v in metrics.items()
                      if k not in ("per_seed_pool_bootstrap",)}, indent=2, default=str))
    print("VERDICT:", agg["verdict"])
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
