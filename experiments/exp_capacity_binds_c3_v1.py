"""exp_capacity_binds_c3_v1 -- IS CAPACITY (VECTOR DIMENSIONALITY d) THE BINDING CONSTRAINT ON THE
C3 OPEN-VOCABULARY FINAL PICK?

PRE-REG: preregs/2026-08-15_capacity_binds_c3_v1.md, committed BEFORE this script ran.

WHY THIS CELL EXISTS. Three independent floored negatives tonight all named the same suspect from
different directions: coherence reranking is null because top-50 candidates share a coarse feature
bucket (exp_coherence_final_pick_transfer_v1); per-dimension gain is VISIBLE to the read-out but
null, attributed to too few observations per concept at d=256 (exp_per_row_gain_c3_vet_v1); the
superposition-regime audit names B4 (representation format/capacity) the largest measured lever the
program owns and the pinned unblocker for C3 (.claude/scan-out/superposition-regime-audit.json). B4's
existing evidence (exp_capacity_ceiling_near_far_v1, +0.0843 at 16x d) is on a DIFFERENT, easier
2-candidate near/far task, not the real 50-way open-vocabulary argmax C3 runs. This cell asks the
question on the REAL C3 harness for the first time.

MEASURES ONLY. No hdlab/ file is modified. No data/foundation/ or other persisted store is touched --
every anchor field is built FRESH IN MEMORY per (d, draw) via ConceptSpace(d=d) and
context_vector_masked(..., d=d), both already-parameterized hdlab primitives, and written only to
this cell's own throwaway data/ directory.

Reuses build_corpus / build_buckets / build_items / gold_meaning_set / MASTER_SEED / MAX_ITEMS /
_derangement / _is_variant from exp_grounding_readout_known_answer_v1 (never reimplemented) -- the
same construction exp_orthographic_floor_vet_v1 and exp_per_row_gain_c3_vet_v1 used to reproduce the
C3 headline bit-for-bit. Reuses salted_context_vector_masked and trigram_matrix from
exp_meaning_supply_separation_v1 (never reimplemented) for the second-draw spread control and the
orthographic floor arm.

CELL-TEMPLATE MANDATORY:
# - final_metrics_atomicity = tmp_replace; SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception; no bare except, no BaseException
# - per-unit checkpoint via tools/exp_checkpoint (unit = one (d, draw) pair), resume-safe
# - items/buckets/gold/pool are built ONCE and are d-independent by construction (verified, not
#   assumed): build_buckets/build_items never touch a vector.
ASCII-only.

Run:  .venv/Scripts/python.exe experiments/exp_capacity_binds_c3_v1.py [--smoke]
Output: data/exp_capacity_binds_c3_v1[_smoke]/metrics.json (atomic os.replace, ts_iso stamped).
Expected FULL runtime: several hours (4 d values x 2 draws, each a full-corpus ConceptSpace build
comparable to the ~543s exp_orthographic_floor_vet_v1 single build) -- run detached.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import numpy as np  # noqa: E402

from hdlab.reading_grounding_loop import (  # noqa: E402
    ConceptSpace, GRADED_COMPARATOR, context_vector_masked, normalize_lemma,
)
import experiments.exp_grounding_readout_known_answer_v1 as C3  # noqa: E402
import experiments.exp_meaning_supply_separation_v1 as MS  # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

SMOKE = "--smoke" in sys.argv
ANCHOR_NAME = "exp_capacity_binds_c3_v1" + ("_smoke" if SMOKE else "")
OUT = os.path.join(_REPO, "data", ANCHOR_NAME)
os.makedirs(OUT, exist_ok=True)

D_GRID = [64, 128] if SMOKE else [256, 512, 1024, 2048]
DRAWS = ("PRIMARY", "DRAW2")
SELF_RETRIEVAL_FLOOR = 0.70
N_BOOTSTRAP = 5000
KNOWN_ANSWER_SEED_OFFSET = 61
BOOTSTRAP_SEED_OFFSET = 71
DERANGEMENT_SEED_OFFSET = 31


def build_space_at_d(sents: List[str], buckets: Dict[str, List[int]], d: int, draw: str,
                     salt_cache: Dict[str, np.ndarray]) -> ConceptSpace:
    """Same accumulation loop as exp_grounding_readout_known_answer_v1.build_space, parameterized
    on d and on which independent projection draw to use. draw=='PRIMARY' calls the LIVE
    context_vector_masked (byte-identical to the unmodified path); draw=='DRAW2' calls
    salted_context_vector_masked with an independent hash salt (exp_meaning_supply_separation_v1's
    own reusable spread-control primitive, self_test-asserted to reproduce the live function
    byte-for-byte at salt='')."""
    sp = ConceptSpace(d=d)
    lemmas = sorted(buckets)
    t0 = time.time()
    for k, w in enumerate(lemmas):
        for i in buckets[w][:C3._n_profile(len(buckets[w]))]:
            if draw == "PRIMARY":
                v = context_vector_masked(sents[i], w, d=d)
            else:
                v = MS.salted_context_vector_masked(sents[i], w, d, draw, salt_cache, GRADED_COMPARATOR)
            sp.observe(w, v)
        if k % 1000 == 0 or k == len(lemmas) - 1:
            print("[space d=%d draw=%s] %d/%d elapsed=%.1fs" % (d, draw, k + 1, len(lemmas),
                                                                 time.time() - t0), flush=True)
    return sp


def score_unit(space: ConceptSpace, anchors: List[str], pos: Dict[str, int], n_anchors: int,
              items: List[dict], donors: List[int], norm2idx: Dict[str, List[int]],
              counts, t_mat: np.ndarray, t_cov: np.ndarray, compute_floors: bool,
              label: str, t0: float) -> dict:
    _, mat = space.anchor_matrix()
    mat_nrm = np.linalg.norm(mat, axis=1)
    mat_ok = mat_nrm >= 1e-9
    n = len(items)
    hits_base = np.zeros(n, dtype=bool)
    ranks_base = np.zeros(n, dtype=np.int64)
    top50_base = np.zeros(n, dtype=bool)
    picks_base: List[str] = []
    hits_scram = np.zeros(n, dtype=bool) if compute_floors else None
    hits_freq = np.zeros(n, dtype=bool) if compute_floors else None
    hits_trig = np.zeros(n, dtype=bool) if compute_floors else None
    anchor_arr = np.array(anchors)
    n_scored = 0

    for i, it in enumerate(items):
        L = it["L"]
        elig = np.ones(n_anchors, dtype=bool)
        for k in sorted(set(norm2idx[normalize_lemma(L)] + [pos[L]])):
            elig[k] = False
        elig &= mat_ok
        sel = np.flatnonzero(elig)
        if sel.size == 0:
            continue
        gold = C3.gold_meaning_set(L)
        gsel = np.array([j for j, a in enumerate(sel) if anchors[a] in gold], dtype=np.int64)

        q = space.bundle(L)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        sc = (mat[sel] @ q) / (mat_nrm[sel] * qn)
        b = int(np.argmax(sc))
        p = anchor_arr[sel[b]]
        picks_base.append(str(p))
        hits_base[i] = str(p) in gold
        if gsel.size:
            ranks_base[i] = int(np.sum(sc > float(np.max(sc[gsel])))) + 1
            top50_base[i] = bool(ranks_base[i] <= 50)
        else:
            ranks_base[i] = sel.size
            top50_base[i] = False
        n_scored += 1

        if compute_floors:
            qd = space.bundle(items[donors[i]]["L"])
            qdn = float(np.linalg.norm(qd))
            if qdn >= 1e-9:
                scs = (mat[sel] @ qd) / (mat_nrm[sel] * qdn)
                hits_scram[i] = str(anchor_arr[sel[int(np.argmax(scs))]]) in gold
            cnts = np.array([counts[anchors[a]] for a in sel], dtype=np.float64)
            hits_freq[i] = str(anchor_arr[sel[int(np.argmax(cnts))]]) in gold
            tq = t_mat[pos[L]] if t_cov[pos[L]] else None
            trig = (t_mat[sel] @ tq) if tq is not None else np.zeros(sel.size)
            hits_trig[i] = str(anchor_arr[sel[int(np.argmax(trig))]]) in gold

        if (i + 1) % 1000 == 0:
            print("[score %s] %d/%d elapsed=%.1fs" % (label, i + 1, n, time.time() - t0), flush=True)

    out = {
        "n_scored": n_scored,
        "n_mat_ok": int(mat_ok.sum()), "n_anchors": n_anchors,
        "hits_base": hits_base.astype(int).tolist(),
        "ranks_base": ranks_base.tolist(),
        "top50_base": top50_base.astype(int).tolist(),
        "example_picks_base": picks_base[:10],
    }
    if compute_floors:
        out["hits_scram"] = hits_scram.astype(int).tolist()
        out["hits_freq"] = hits_freq.astype(int).tolist()
        out["hits_trig"] = hits_trig.astype(int).tolist()
    return out


def known_answer(space: ConceptSpace, anchors: List[str], pos: Dict[str, int], sents: List[str],
                 items: List[dict], seed: int) -> Tuple[float, int]:
    """2-candidate self-retrieval positive control, own held-out sentence vs one random foreign
    anchor, reused construction from exp_per_row_gain_c3_vet_v1 / exp_grounding_readout_known_answer_v1,
    parameterized on d via space.d."""
    _, mat = space.anchor_matrix()
    mat_nrm = np.linalg.norm(mat, axis=1)
    rng_sr = np.random.default_rng(seed)
    hits, ntot = 0, 0
    for it in items[:min(300, len(items))]:
        L = it["L"]
        if it["sent_idx"] is None:
            continue
        other = anchors[int(rng_sr.integers(len(anchors)))]
        tries = 0
        while tries < 20 and (other == L or C3._is_variant(other, L)):
            other = anchors[int(rng_sr.integers(len(anchors)))]
            tries += 1
        if other == L:
            continue
        q = context_vector_masked(sents[it["sent_idx"]], L, d=space.d)
        qn = float(np.linalg.norm(q))
        if qn < 1e-9:
            continue
        cand = [pos[L], pos[other]]
        sc = (mat[cand] @ q) / (mat_nrm[cand] * qn)
        hits += int(sc[0] >= sc[1])
        ntot += 1
    return round(hits / max(1, ntot), 6), ntot


def main() -> int:
    t0 = time.time()
    sents = C3.build_corpus("smoke" if SMOKE else "full")
    buckets, counts = C3.build_buckets(sents)
    max_items = 200 if SMOKE else C3.MAX_ITEMS
    print("[corpus] n_sentences=%d n_candidate_lemmas=%d elapsed=%.1fs"
          % (len(sents), len(buckets), time.time() - t0), flush=True)

    # ---- items/pool/gold: built ONCE off the smallest-d PRIMARY space, then reused unmodified at
    # every d. build_items only checks `space.bundle(X) is None`, which never depends on d in
    # practice (every lemma in buckets gets >=1 profile sentence observed by construction), so this
    # is not a d-dependent choice -- it is the one build we need anyway (D_GRID[0], PRIMARY, is a
    # real unit in the sweep).
    seed_key = unit_key("d%d" % D_GRID[0], "PRIMARY")
    seed_space = build_space_at_d(sents, buckets, D_GRID[0], "PRIMARY", {})
    anchors, _seed_mat = seed_space.anchor_matrix()
    pos = {a: i for i, a in enumerate(anchors)}
    n_anchors = len(anchors)
    items, item_diag = C3.build_items(seed_space, buckets, counts, max_items)
    n = len(items)
    print("[items] n=%d n_anchors=%d elapsed=%.1fs" % (n, n_anchors, time.time() - t0), flush=True)

    norm2idx: Dict[str, List[int]] = defaultdict(list)
    for a in anchors:
        norm2idx[normalize_lemma(a)].append(pos[a])
    donors = C3._derangement(n, lambda i, j: len({items[j]["L"], items[j]["G"], items[j]["F"]}
                                                  & {items[i]["L"], items[i]["G"], items[i]["F"]}) > 0)
    t_mat, t_cov = MS.trigram_matrix(anchors)  # anchor-string-only, provably d-independent

    # ---- per-(d, draw) checkpointed units. seed_space's own scoring is recorded as the D_GRID[0]
    # PRIMARY unit so the expensive build above is not repeated.
    done = completed_units(OUT)
    known_answers: Dict[int, Tuple[float, int]] = {}

    for d in D_GRID:
        for draw in DRAWS:
            key = unit_key("d%d" % d, draw)
            if key in done:
                print("[resume] skip %s (already recorded)" % key, flush=True)
                continue
            if d == D_GRID[0] and draw == "PRIMARY":
                space = seed_space
            else:
                # a FRESH cache per (d, draw) build -- MS._salted_word_vec's cache is keyed by word
                # only (not (word, d)), so reusing a cache dict across different d values returns a
                # wrong-shaped vector (caught in smoke: ValueError broadcasting (128,) vs (64,)).
                space = build_space_at_d(sents, buckets, d, draw, {})
            compute_floors = (draw == "PRIMARY")
            res = score_unit(space, anchors, pos, n_anchors, items, donors, norm2idx, counts,
                             t_mat, t_cov, compute_floors, key, t0)
            if draw == "PRIMARY":
                ka_acc, ka_n = known_answer(space, anchors, pos, sents, items,
                                            C3.MASTER_SEED + KNOWN_ANSWER_SEED_OFFSET + d)
                res["known_answer_acc"] = ka_acc
                res["known_answer_n"] = ka_n
            record_unit(OUT, key, res)
            done.add(key)
            print("[unit done] %s hits_base_mean=%.4f elapsed=%.1fs"
                  % (key, float(np.mean(res["hits_base"])), time.time() - t0), flush=True)
            del space

    units = load_units(OUT)

    # ---- assemble arms for a single joint paired bootstrap over ALL (d, draw, arm) combinations
    arms: Dict[str, np.ndarray] = {}
    per_d: Dict[int, dict] = {}
    for d in D_GRID:
        pkey = unit_key("d%d" % d, "PRIMARY")
        dkey = unit_key("d%d" % d, "DRAW2")
        pu = units.get(pkey)
        du = units.get(dkey)
        if pu is None or du is None:
            per_d[d] = {"INCOMPLETE": True, "have_primary": pu is not None, "have_draw2": du is not None}
            continue
        arms["D%d_BASE" % d] = np.array(pu["hits_base"], dtype=float)
        arms["D%d_DRAW2" % d] = np.array(du["hits_base"], dtype=float)
        arms["D%d_SCRAM" % d] = np.array(pu["hits_scram"], dtype=float)
        arms["D%d_FREQ" % d] = np.array(pu["hits_freq"], dtype=float)
        arms["D%d_TRIG" % d] = np.array(pu["hits_trig"], dtype=float)
        arms["D%d_TOP50" % d] = np.array(pu["top50_base"], dtype=float)
        per_d[d] = {
            "n_mat_ok_primary": pu["n_mat_ok"], "n_mat_ok_draw2": du["n_mat_ok"], "n_anchors": n_anchors,
            "median_rank_primary": float(np.median(pu["ranks_base"])),
            "known_answer": {"acc": pu.get("known_answer_acc"), "n": pu.get("known_answer_n"),
                             "floor": SELF_RETRIEVAL_FLOOR,
                             "ok": bool((pu.get("known_answer_acc") or 0) >= SELF_RETRIEVAL_FLOOR)},
            "example_picks_primary": pu["example_picks_base"],
        }

    d0 = D_GRID[0]
    dN = D_GRID[-1]
    deltas = []
    for d in D_GRID:
        if "D%d_BASE" % d not in arms:
            continue
        deltas.append(("d_D%d_BASE_minus_TRIG" % d, "D%d_BASE" % d, "D%d_TRIG" % d))
        deltas.append(("d_D%d_BASE_minus_DRAW2" % d, "D%d_BASE" % d, "D%d_DRAW2" % d))
        deltas.append(("d_D%d_BASE_minus_SCRAM" % d, "D%d_BASE" % d, "D%d_SCRAM" % d))
        if d != d0 and ("D%d_BASE" % d0) in arms:
            deltas.append(("d_D%d_BASE_minus_D%d_BASE" % (d, d0), "D%d_BASE" % d, "D%d_BASE" % d0))
            deltas.append(("d_D%d_TOP50_minus_D%d_TOP50" % (d, d0), "D%d_TOP50" % d, "D%d_TOP50" % d0))
    for a, b in zip(D_GRID, D_GRID[1:]):
        if ("D%d_BASE" % a) in arms and ("D%d_BASE" % b) in arms:
            deltas.append(("d_D%d_BASE_minus_D%d_BASE" % (b, a), "D%d_BASE" % b, "D%d_BASE" % a))

    bs = MS.paired_bootstrap(arms, deltas, N_BOOTSTRAP, C3.MASTER_SEED + BOOTSTRAP_SEED_OFFSET) if arms else None

    a1_base_reproduces_headline = None
    if not SMOKE and ("D%d_BASE" % d0) in arms and d0 == 256:
        a1_base_reproduces_headline = abs(float(arms["D%d_BASE" % d0].mean()) - 0.048) < 1e-9

    monotonic_nondecreasing = None
    hit_seq = [float(arms["D%d_BASE" % d].mean()) for d in D_GRID if ("D%d_BASE" % d) in arms]
    if len(hit_seq) == len(D_GRID):
        monotonic_nondecreasing = all(hit_seq[i + 1] >= hit_seq[i] - 1e-9 for i in range(len(hit_seq) - 1))

    clears_bar_ci_separated = {}
    void_plumbing = {}
    for d in D_GRID:
        dl = "d_D%d_BASE_minus_TRIG" % d
        if bs and dl in bs["deltas"]:
            clears_bar_ci_separated[str(d)] = bool(bs["deltas"][dl]["ci_lo"] > 0)
        pdd = per_d.get(d, {})
        void_plumbing[str(d)] = bool(not pdd.get("known_answer", {}).get("ok", False)) if "known_answer" in pdd else True

    kill_condition_fires = None
    if len(D_GRID) >= 2 and ("D%d_BASE" % dN) in arms and ("D%d_BASE" % d0) in arms and bs:
        top_delta_key = "d_D%d_BASE_minus_D%d_BASE" % (dN, d0)
        if top_delta_key in bs["deltas"]:
            kill_condition_fires = bool(not bs["deltas"][top_delta_key]["ci_excludes_zero"])

    containment_moves = {}
    for d in D_GRID:
        if d == d0:
            continue
        dl = "d_D%d_TOP50_minus_D%d_TOP50" % (d, d0)
        if bs and dl in bs["deltas"]:
            containment_moves[str(d)] = {
                "delta_vs_d%d" % d0: bs["deltas"][dl]["delta"],
                "ci_excludes_zero": bs["deltas"][dl]["ci_excludes_zero"],
            }

    rep = {
        "anchor_name": ANCHOR_NAME,
        "what": "PRE-REGISTERED VET: does capacity (vector dimensionality d) bind the C3 "
                "open-vocabulary final pick? Identical items/pool/gold/scorer as "
                "exp_grounding_readout_known_answer_v1 across a d sweep; only the anchor field and "
                "queries are rebuilt per d.",
        "prereg": "preregs/2026-08-15_capacity_binds_c3_v1.md",
        "prior_work_check": "bash tools/substrate_query.sh top cosine 0.3047 "
                            "('Anchor 2 -- capacity retention under normalization (VALIDATION)', "
                            "notes/exp_dev_handoff_research_pattern_b_payload_control_2026-06-07.md) "
                            "-- read in full, an unrelated 2026-06-07 bundle-capacity-under-"
                            "normalization test, different mechanism and different question. NO prior "
                            "arc cell decomposes the C3 open-vocabulary final pick by dimensionality. "
                            "Confirms the independent check already in "
                            ".claude/scan-out/superposition-regime-audit.json (top non-self cosine "
                            "0.3311, a different adjacent question). NOVEL, not a rediscovery.",
        "read_out_invariance_check": "Transform under test is a full re-draw of every anchor row's "
                                     "DIRECTION at a different dimensionality (ConceptSpace(d=d) + "
                                     "context_vector_masked(..., d=d)), not a post-hoc scalar rescale "
                                     "of a fixed-direction row. It is OUTSIDE the invariance group the "
                                     "per-row-gain / global-scalar theorem covers (that theorem is "
                                     "about a POSITIVE SCALAR on an existing row, which cancels between "
                                     "the cosine numerator and its self-derived norm; changing d changes "
                                     "the number of coordinates and the joint distribution of pairwise "
                                     "cosines -- concentration of measure, already measured in the B4 "
                                     "cell as crosstalk falling 1/sqrt(d)). This transform IS visible to "
                                     "canonicalize_fast's cosine argmax; whether it helps on THIS task "
                                     "is what this cell measures rather than assumes.",
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "smoke": SMOKE,
        "d_grid": D_GRID, "draws": list(DRAWS),
        "n_items": n, "n_anchors": n_anchors, "item_construction": item_diag,
        "items_pool_gold_are_d_independent_by_construction": True,
        "a1_base_reproduces_c3_headline_0.0480_to_1e-9": a1_base_reproduces_headline,
        "per_d": {str(d): per_d.get(d) for d in D_GRID},
        "bootstrap": bs,
        "hit_at_1_sequence_by_d": dict(zip([str(d) for d in D_GRID], hit_seq)) if hit_seq else None,
        "monotonic_nondecreasing_across_d_grid": monotonic_nondecreasing,
        "clears_bar_CI_separated_per_d": clears_bar_ci_separated,
        "void_plumbing_per_d": void_plumbing,
        "kill_condition_flat_across_full_d_range_ci_includes_zero": kill_condition_fires,
        "containment_moves_with_d": containment_moves,
        "elapsed_s": round(time.time() - t0, 2),
    }
    p = os.path.join(OUT, "metrics.json")
    with open(p + ".tmp", "wb") as fh:
        fh.write(json.dumps(rep, indent=1).encode("utf-8"))
    os.replace(p + ".tmp", p)
    print("hit@1 by d:", rep["hit_at_1_sequence_by_d"])
    print("A1_BASE reproduces C3 headline 0.0480 exactly:", a1_base_reproduces_headline)
    print("monotonic non-decreasing across d grid:", monotonic_nondecreasing)
    print("clears bar CI-separated per d:", clears_bar_ci_separated)
    print("kill condition (flat across full range) fires:", kill_condition_fires)
    print("containment moves with d:", containment_moves)
    print("WROTE", p)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception as exc:
        _crash = os.path.join(OUT, "_crash_diagnostic.json")
        with open(_crash + ".tmp", "w", encoding="utf-8") as fh:
            json.dump({"anchor_name": ANCHOR_NAME,
                       "error": "%s: %s" % (type(exc).__name__, exc),
                       "traceback": traceback.format_exc(),
                       "ts_iso": datetime.now(timezone.utc).isoformat()}, fh, indent=2)
        os.replace(_crash + ".tmp", _crash)
        raise
