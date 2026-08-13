"""exp_anchor_pool_expansion_v1 -- matched ablation, ONE variable: THE ANCHOR POOL SIZE.

PRE-REG: preregs/2026-08-13_anchor_pool_expansion.md (filed BEFORE any arm ran).

THE FINDING UNDER TEST (notes/downstream_bottleneck_trace_2026-08-13.md +
notes/minimum_grounded_basis_derivation_and_refutation_2026-08-13.md): canonicalize_fast argmaxes
over ConceptSpace anchors only; anchors enter at exactly two sites (seed vocabulary at
reading_grounding_loop.py:1039-1044, already-grounded lemmas at :1279). Anchor universe = 887 seed
+ 374 grounded = 1261 vs ~16812 corpus content lemmas -- a 6% naming ceiling. `fruit` and `zone`
were never candidates. The ordered base vocabulary on disk holds 74287 rows; the loop loads 1000.

ARMS -- everything identical except which lemmas have an anchor profile in ConceptSpace:
  SMALL  anchor_pool=None                        -- the shipped default (887 seed lemmas)
  LARGE  anchor_pool=all 74287 base-vocab lemmas -- 50461 distinct, 12691 occur in the corpus

known_seed stays the shipped 887-lemma set in BOTH arms, so the target set, the gap gate, the
reading order, the admission policy and the comparator are untouched. F1/F3 OFF in both arms.

PRIMARY DISCRIMINATOR: KNOWN-ANSWER RECALL against two hand-scored fact sets (no hand-scoring,
not floor-limited). AVAILABILITY / RECALL@1 / RECALL@5 / AVAILABILITY-CONDITIONED RECALL.
The blind 100-row hand-score sample is SECONDARY and carries NO quality claim from this cell.

GROWTH IS PAUSED: everything is written under data/exp_anchor_pool_expansion_v1/ only.
ASCII-only. Deterministic: sorted(set(...)), hashlib-seeded vectors, fixed integer seeds.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import math
import platform
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab.closed_class_lexicon import is_closed_class, is_eligible_meaning
from hdlab.grounding_acquisition_loop import content_words
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    PBV_COMMIT_STRENGTH,
    ConceptSpace,
    ReadingLoopState,
    checkpoint,
    make_pbv_fns,
    normalize_lemma,
    pbv_trajectory_stats,
    process_sentence,
    seed_known_words,
)
from tools import exp_checkpoint

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import (
    CHUNK_SIZE, grounded_lemmas_in_store,
)
from experiments.exp_definitional_grounding_v5 import load_corpus_v5

ANCHOR_NAME = "anchor_pool_expansion_v1"
PREREG = "preregs/2026-08-13_anchor_pool_expansion.md"

ARMS = ["SMALL", "LARGE"]
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]
EXPECTED_N_UNITS = len(ARMS) * len(SEGMENTS)

# ONE VARIABLE: both arms get the IDENTICAL store seed and the IDENTICAL known_seed.
ARM_SEED = 4201
SEED_KNOWN_TOP_N = 1000              # shipped: top-1000 ROWS -> 887 distinct lemmas. BOTH arms.
LARGE_POOL_DEPTH = 74287             # chosen by measured coverage; see prereg sec 2.1
SMALL_POOL_DEPTH = None              # shipped default: no extra pool at all

SAMPLE_SEED = 42
SAMPLE_N = 50
BLIND_SHUFFLE_SEED = 42
TOP_K = 5

SMOKE_LIMIT_PER_SEGMENT = 400

# ---- SMALL regression reference (prereg sec 6, S4) ---------------------------------------------
REF_RUN = "data/exp_grounding_quality_readout_v1/metrics.json"
REF_N_FACTS = 384
REF_DIGEST16 = "836571fa99d5765d"

COVERAGE_PROBE = "data/exp_anchor_pool_expansion_v1/_probe_coverage.json"

BANDS = {
    "discriminator": "recall@1(LARGE) - recall@1(SMALL) on the v5 RELATION-MATCHED known-answer "
                     "key (GROUNDED_MEANING). v62 is relation-MISMATCHED and cannot carry the "
                     "verdict.",
    "POOL_WAS_BINDING": "availability delta >= +0.30 AND recall@1 delta >= +0.10",
    "PARTIAL": "recall@1 delta in [+0.03, +0.10)",
    "COMPARATOR_IS_BINDING": "availability delta >= +0.30 AND recall@1 delta < +0.03 -- the "
                             "answer is on the menu and still is not chosen. PRE-DECLARED FULLY "
                             "EXPECTED AND ACCEPTABLE.",
    "HURTS": "recall@1 delta <= -0.03 -- more candidates means more distractors. A live "
             "possibility, not a formality.",
    "BROKEN": "availability does not rise -- the manipulation failed; nothing else is interpreted.",
    "power": "n=1353 v5 probe subjects: SE(proportion near 0.05) = 0.006, SE(delta) <= 0.019, so "
             "+0.03 is resolvable at >1.5 SE and +0.10 at >5 SE.",
    "secondary_mechanistic": "per-arm agreement with a plain sentence-level co-occurrence "
                             "baseline (cooc_agreement_top1 / top5), hand-score independent.",
}


# =========================================================================== io helpers
def _output_dir(run_mode: str) -> str:
    return repo_path(f"data/exp_{ANCHOR_NAME}" + ("_smoke" if run_mode == "smoke" else ""))


def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _write_start_marker(output_dir: str, run_mode: str, arm: Optional[str]) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "arm": arm,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node(),
              "prereg": PREREG}
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"), marker)


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())) + "\n")


def _digest_pairs(pairs) -> str:
    h = hashlib.sha256()
    for s, o in sorted(set(pairs)):
        h.update(("%s\x1f%s\x1e" % (s, o)).encode("utf-8"))
    return h.hexdigest()


def _peak_rss_bytes() -> Optional[int]:
    """Peak working set of THIS process. psutil if present, else the Win32 PSAPI struct."""
    try:
        import psutil                                    # type: ignore
        return int(psutil.Process(os.getpid()).memory_info().peak_wset)
    except Exception:
        pass
    try:
        import ctypes
        from ctypes import wintypes

        class _PMC(ctypes.Structure):
            _fields_ = [("cb", wintypes.DWORD), ("PageFaultCount", wintypes.DWORD),
                        ("PeakWorkingSetSize", ctypes.c_size_t),
                        ("WorkingSetSize", ctypes.c_size_t),
                        ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                        ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                        ("PagefileUsage", ctypes.c_size_t),
                        ("PeakPagefileUsage", ctypes.c_size_t)]

        c = _PMC()
        c.cb = ctypes.sizeof(_PMC)
        if ctypes.windll.psapi.GetProcessMemoryInfo(
                ctypes.windll.kernel32.GetCurrentProcess(), ctypes.byref(c), c.cb):
            return int(c.PeakWorkingSetSize)
    except Exception:
        pass
    return None


# ============================================== ConceptSpace with an INCREMENTAL anchor matrix
class IncrementalConceptSpace(ConceptSpace):
    """BYTE-IDENTICAL drop-in for ConceptSpace, differing ONLY in how anchor_matrix() is computed.

    WHY IT EXISTS: stock anchor_matrix() rebuilds `np.sign(np.stack([...]))` whenever _version
    changed, and _version bumps on EVERY observe -- i.e. essentially once per encounter. At the
    shipped 1261 anchors x 2048 that is ~20 MB rebuilt ~84000 times; at this cell's 12691 anchors
    it is ~208 MB rebuilt ~84000 times, which is the difference between a 15-minute arm and an
    unusable one. Here rows are updated IN PLACE for touched lemmas and the matrix is rebuilt only
    when the anchor SET changes (bounded by the number of distinct anchors, not by encounters).

    It is a SPEED change and nothing else: `_selftest_incremental_space_matches_stock` asserts the
    returned (anchors, matrix) are equal element-for-element to the stock class's over a randomized
    observe / seed_from_bundle sequence, including anchor ORDER (which is what fixes
    canonicalize_fast's tie-break)."""

    def __init__(self, d: int = 2048) -> None:
        super().__init__(d)
        self._names: List[str] = []
        self._pos: Dict[str, int] = {}
        self._m: np.ndarray = np.zeros((0, d), dtype=np.float64)
        self._dirty: set = set()
        self.n_full_rebuilds = 0

    def observe(self, lemma: str, ctx_vec: np.ndarray) -> None:
        if lemma not in self._sums:
            self._sums[lemma] = np.zeros(self.d, dtype=np.float64)
        self._sums[lemma] += ctx_vec
        self._version += 1
        self._dirty.add(lemma)

    def seed_from_bundle(self, lemma: str, raw_sum: np.ndarray) -> None:
        self._sums[lemma] = np.array(raw_sum, dtype=np.float64, copy=True)
        self._version += 1
        self._dirty.add(lemma)

    def anchor_matrix(self) -> Tuple[List[str], np.ndarray]:
        if not self._dirty:
            return self._names, self._m
        if any(n not in self._pos for n in self._dirty):
            names = sorted(self._sums)
            self._m = (np.sign(np.stack([self._sums[a] for a in names], axis=0)) if names
                       else np.zeros((0, self.d), dtype=np.float64))
            self._names = names
            self._pos = {a: i for i, a in enumerate(names)}
            self.n_full_rebuilds += 1
        else:
            for n in sorted(self._dirty):
                np.sign(self._sums[n], out=self._m[self._pos[n]])
        self._dirty.clear()
        return self._names, self._m


def _selftest_incremental_space_matches_stock() -> None:
    """Randomized observe / seed_from_bundle sequence: the incremental space must return the
    SAME anchor order and an element-for-element identical matrix at every step."""
    rng = np.random.default_rng(7)
    d = 32
    a, b = ConceptSpace(d), IncrementalConceptSpace(d)
    vocab = ["zeta", "alpha", "mid", "beta", "omega", "kappa", "aa", "zz"]
    for step in range(400):
        w = vocab[int(rng.integers(0, len(vocab)))]
        v = rng.choice([-1.0, 0.0, 1.0], size=d)
        if int(rng.integers(0, 8)) == 0:
            a.seed_from_bundle(w, v)
            b.seed_from_bundle(w, v)
        else:
            a.observe(w, v)
            b.observe(w, v)
        if int(rng.integers(0, 3)) == 0 or step == 399:
            na, ma = a.anchor_matrix()
            nb, mb = b.anchor_matrix()
            assert na == nb, "anchor ORDER diverged at step %d: %r vs %r" % (step, na, nb)
            assert np.array_equal(ma, mb), "anchor MATRIX diverged at step %d" % step
            for n in na:
                assert np.array_equal(a.bundle(n), b.bundle(n))
                assert (n in a) == (n in b)
            assert a.anchors() == b.anchors()


# =========================================================================== corpus + pool
def build_stream(run_mode: str) -> List[Tuple[str, str]]:
    """IDENTICAL corpus + order to the reference run: load_corpus_v5(None, lineaware=True),
    34169 sentences. Holding it fixed is what makes SMALL reproducible against 384 /
    836571fa99d5765d."""
    limit = SMOKE_LIMIT_PER_SEGMENT if run_mode == "smoke" else None
    return load_corpus_v5(limit, lineaware=True)


def build_anchor_pool(depth: Optional[int]) -> Optional[frozenset]:
    if depth is None:
        return None
    return frozenset(normalize_lemma(w) for w in load_base_vocab_seed(depth))


def load_probe_sets() -> dict:
    with open(repo_path(COVERAGE_PROBE), encoding="utf-8") as f:
        return json.load(f)


# =========================================================================== post-hoc read-out
def probe_readout(state: ReadingLoopState, subjects: Sequence[str], k: int = TOP_K) -> dict:
    """POST-HOC read-out: for each probe subject the arm actually flagged, score sign(sum of its
    own trace context vectors) against THIS ARM's final anchor field with canonicalize_fast's own
    math (eligible anchors only, self excluded, zero-norm anchors scored 0.0, first-max-in-sorted-
    order tie-break) and return the top-k anchor names.

    Same procedure in both arms over the same subject list. It is NOT the live decision (which
    banks only ~380 of ~16000 targets, far too few to intersect a probe set) and is labelled as
    such in the metrics."""
    anchors, mat = state.space.anchor_matrix()
    elig = np.array([is_eligible_meaning(a) for a in anchors], dtype=bool)
    norms = np.linalg.norm(mat, axis=1)
    nonzero = norms >= 1e-9
    safe = np.where(nonzero, norms, 1.0)
    out: Dict[str, dict] = {}
    for s in sorted(set(subjects)):
        it = state.library.items.get(s)
        if it is None or not it.traces:
            out[s] = {"status": "NOT_FLAGGED", "top": [], "n_traces": 0}
            continue
        raw = np.sum([t.context_vec for t in it.traces], axis=0)
        nb = np.sign(raw)
        nn = float(np.linalg.norm(nb))
        if nn < 1e-9:
            out[s] = {"status": "EMPTY_PROFILE", "top": [], "n_traces": len(it.traces)}
            continue
        keep = elig.copy()
        i = int(np.searchsorted(anchors, s))
        if i < len(anchors) and anchors[i] == s:
            keep[i] = False
        sims = (mat @ nb) / (safe * nn)
        sims[~nonzero] = 0.0
        sims[~keep] = -np.inf
        order = np.argsort(-sims, kind="stable")[:k]
        out[s] = {"status": "OK", "n_traces": len(it.traces),
                  "top": [anchors[int(j)] for j in order if np.isfinite(sims[int(j)])],
                  "top1_cos": round(float(sims[int(order[0])]), 6) if order.size else None}
    return out


def score_probe(probe: Dict[str, List[str]], readout: dict, anchor_set: set,
                banked: Dict[str, str]) -> dict:
    """AVAILABILITY / RECALL@1 / RECALL@5 / AVAILABILITY-CONDITIONED RECALL, plus live banked
    recall. `probe` maps subject -> sorted list of KNOWN correct objects."""
    n = n_avail = n_r1 = n_r5 = n_cond = n_cond_hit = 0
    n_readable = n_banked = n_banked_hit = 0
    rows = []
    for s in sorted(probe):
        objs = probe[s]
        n += 1
        avail_objs = [o for o in objs if o in anchor_set]
        avail = bool(avail_objs)
        n_avail += int(avail)
        r = readout.get(s) or {"status": "NOT_FLAGGED", "top": []}
        top = r.get("top") or []
        readable = r.get("status") == "OK"
        n_readable += int(readable)
        hit1 = bool(top) and top[0] in objs
        hit5 = any(t in objs for t in top)
        n_r1 += int(hit1)
        n_r5 += int(hit5)
        if avail:
            n_cond += 1
            n_cond_hit += int(hit1)
        b = banked.get(s)
        if b is not None:
            n_banked += 1
            n_banked_hit += int(b in objs)
        rows.append({"subject": s, "known_objects": objs, "available": avail,
                     "readout_status": r.get("status"), "top": top,
                     "hit1": hit1, "hit5": hit5, "banked_object": b})
    def _r(a, b_):
        return round(a / b_, 6) if b_ else None
    return {
        "n_probe_subjects": n,
        "n_readable": n_readable,
        "availability": _r(n_avail, n), "n_available": n_avail,
        "recall_at_1": _r(n_r1, n), "n_recall_at_1": n_r1,
        "recall_at_5": _r(n_r5, n), "n_recall_at_5": n_r5,
        "availability_conditioned_recall_at_1": _r(n_cond_hit, n_cond),
        "n_availability_conditioned": n_cond, "n_availability_conditioned_hit": n_cond_hit,
        "live_banked": {"n_probe_subjects_banked": n_banked,
                        "n_banked_correct": n_banked_hit,
                        "live_banked_recall": _r(n_banked_hit, n_banked)},
        "rows": rows,
    }


# =========================================================================== one arm
def run_arm(arm: str, run_mode: str, output_dir: str) -> dict:
    already = exp_checkpoint.completed_units(output_dir)
    done_key = exp_checkpoint.unit_key("arm_done", arm)
    if done_key in already:
        return dict(exp_checkpoint.load_units(output_dir)[done_key], skipped=True)

    stream = build_stream(run_mode)
    store = HDFactStore(n_dim=N_DIM, seed=ARM_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    state.space = IncrementalConceptSpace(state.space.d)     # speed-only, self-tested identical
    seed_known_words(state, load_base_vocab_seed(SEED_KNOWN_TOP_N), source="seed_base_vocabulary")
    known_seed_snapshot = set(state.known_seed)

    # ---------------- THE ONE VARIABLE ----------------
    depth = LARGE_POOL_DEPTH if arm == "LARGE" else SMALL_POOL_DEPTH
    anchor_pool = build_anchor_pool(depth)
    # F1/F3 OFF in BOTH arms: readout=None, freeze_episode=False.
    propose_fn, verify_fn = make_pbv_fns(state)
    pbv_fns = (propose_fn, verify_fn)

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    seg_seen: Dict[str, int] = {}
    seg_units_written: Dict[str, bool] = {}
    t0 = time.time()
    last_hb = t0

    for chunk_idx in range(n_chunks):
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        for i, (seg, sent) in enumerate(chunk):
            seg_seen[seg] = seg_seen.get(seg, 0) + 1
            process_sentence(state, sent, f"{arm}_{chunk_idx}_{i}", pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=True, anchor_pool=anchor_pool)
        seg_tag = chunk[-1][0] if chunk else "unknown"
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=seg_tag,
                         schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
                         commit_strength=PBV_COMMIT_STRENGTH)

        if seg_tag in SEGMENTS and not seg_units_written.get(seg_tag):
            seg_units_written[seg_tag] = True
            key = exp_checkpoint.unit_key(arm, seg_tag)
            if key not in already:
                exp_checkpoint.record_unit(output_dir, key, {
                    "arm": arm, "segment": seg_tag, "first_chunk_idx": chunk_idx,
                    "n_anchors_at_segment_open": len(state.space.anchors()),
                    "n_grounded_at_segment_open": len(grounded_lemmas_in_store(state.store))})
        if chunk_idx % 10 == 0 or chunk_idx == n_chunks - 1:
            print(f"[progress] {arm} chunk={chunk_idx + 1}/{n_chunks} seg={seg_tag} "
                  f"anchors={len(state.space.anchors())} "
                  f"grounded={len(grounded_lemmas_in_store(state.store))} "
                  f"refused={row['n_refused_cumulative']} "
                  f"elapsed={time.time() - t0:.1f}s", flush=True)
        if time.time() - last_hb >= 60.0:
            last_hb = time.time()
            _heartbeat(output_dir, {"arm": arm, "chunk": chunk_idx, "n_chunks": n_chunks,
                                    "n_anchors": len(state.space.anchors()),
                                    "elapsed_s": round(time.time() - t0, 1)})

    traj = pbv_trajectory_stats(state.library)
    gm = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    grounded = grounded_lemmas_in_store(state.store)
    n_conf, n_disc = int(traj["n_confirm"]), int(traj["n_disconfirm"])
    verdict_bearing = n_conf + n_disc
    banked = {f.subject: f.obj for f in gm}

    anchors, mat = state.space.anchor_matrix()
    anchor_set = set(a for a in anchors if is_eligible_meaning(a))

    # ---- PRIMARY: known-answer recall, both keys
    probes = load_probe_sets()["probe_sets"]
    all_subj = sorted(set(list(probes["v62_predicate"]["subjects"])
                          + list(probes["v5_definitional"]["subjects"])))
    t_ro = time.time()
    readout = probe_readout(state, all_subj)
    known_answer = {}
    for key_name in ("v62_predicate", "v5_definitional"):
        known_answer[key_name] = score_probe(probes[key_name]["subjects"], readout,
                                             anchor_set, banked)
    print(f"[probe] {arm} readout over {len(all_subj)} subjects in {time.time() - t_ro:.1f}s",
          flush=True)

    summary = {
        "arm": arm,
        "anchor_pool_depth_rows": depth,
        "anchor_pool_n_lemmas": (len(anchor_pool) if anchor_pool is not None else 0),
        "known_seed_top_n_rows": SEED_KNOWN_TOP_N,
        "n_known_seed_lemmas": len(known_seed_snapshot),
        "encoder": "context_vector_masked", "readout": None, "freeze_episode": False,
        "n_sentences": len(stream), "n_chunks": n_chunks,
        "segments_seen": {s: seg_seen.get(s, 0) for s in SEGMENTS},
        "anchor_matrix_shape": [int(mat.shape[0]), int(mat.shape[1])],
        "anchor_matrix_bytes": int(mat.nbytes),
        "n_anchors": len(anchors),
        "n_eligible_anchors": len(anchor_set),
        "n_full_matrix_rebuilds": getattr(state.space, "n_full_rebuilds", None),
        "n_grounded": len(grounded),
        "n_meaning_facts": len(gm),
        "n_tautology_facts": sum(1 for f in gm if f.subject == f.obj),
        "n_closed_class_object_facts": sum(1 for f in gm if is_closed_class(f.obj)),
        "no_leak_violations": sorted(set(l for l in grounded if l in known_seed_snapshot)),
        "n_refusals": len(state.refusals),
        "refusal_reasons": _count_reasons(state.refusals),
        "trajectory": {k: v for k, v in traj.items() if k != "revisions"},
        "confirm_rate": round(n_conf / verdict_bearing, 6) if verdict_bearing else None,
        "n_verdict_bearing": verdict_bearing,
        "admission_rate": traj.get("informative_encounter_rate"),
        "pairs_digest": _digest_pairs((f.subject, f.obj) for f in gm),
        "grounded_objects": banked,
        "known_answer_recall": known_answer,
        "peak_rss_bytes": _peak_rss_bytes(),
        "elapsed_s": round(time.time() - t0, 2),
    }
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_provenance.json"),
                 [_prov_row(p) for p in state.provenance if p["relation"] == MEANING_RELATION])
    _atomic_json(os.path.join(output_dir, f"arm_{arm}_probe_readout.json"),
                 {"arm": arm, "n_subjects": len(all_subj), "readout": readout})
    exp_checkpoint.record_unit(output_dir, done_key, summary)
    return summary


def _prov_row(p: dict) -> dict:
    return {k: p.get(k) for k in ("fid", "subject", "relation", "object", "segment", "pass_idx",
                                  "best_cos", "n_exposures", "schema_score", "evidence",
                                  "hypothesis")}


def _count_reasons(refusals: List[dict]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for r in refusals:
        out[r["reason"]] = out.get(r["reason"], 0) + 1
    return dict(sorted(out.items()))


# ================================================== SECONDARY: co-occurrence baseline
def cooccurrence_top(run_mode: str, k: int = 5) -> Dict[str, List[str]]:
    """PLAIN sentence-level co-occurrence over the FULL corpus: subject -> its k highest-count
    co-occurring content lemmas, restricted to is_eligible_meaning, ties broken by sorted lemma.
    Identical recipe to exp_structured_comparator_v1 so the two cells' numbers are comparable."""
    counts: Dict[str, Counter] = defaultdict(Counter)
    for _seg, sent in build_stream(run_mode):
        lem = sorted(set(normalize_lemma(w) for w in content_words(sent)))
        for a in lem:
            for b in lem:
                if a != b:
                    counts[a][b] += 1
    out: Dict[str, List[str]] = {}
    for a, c in counts.items():
        ranked = sorted(((-n, b) for b, n in c.items() if is_eligible_meaning(b)))
        out[a] = [b for _n, b in ranked[:k]]
    return out


def cooc_agreement(pairs: Dict[str, str], top: Dict[str, List[str]]) -> dict:
    n = t1 = t5 = miss = 0
    for s, o in sorted(pairs.items()):
        tops = top.get(s)
        if not tops:
            miss += 1
            continue
        n += 1
        t1 += int(o == tops[0])
        t5 += int(o in tops)
    return {"n_scored": n, "n_subject_absent_from_baseline": miss,
            "cooc_agreement_top1": round(t1 / n, 6) if n else None,
            "cooc_agreement_top5": round(t5 / n, 6) if n else None}


# =========================================================================== audit sample
def _sample_rows(prov: List[dict]) -> List[dict]:
    """50 rows, random.Random(42).sample over fid order -- the SAME sampling convention as
    data/exp_grounding_quality_readout_v1."""
    by_fid = sorted(prov, key=lambda r: (int(r["fid"]), str(r["subject"])))
    n = min(SAMPLE_N, len(by_fid))
    picked = random.Random(SAMPLE_SEED).sample(by_fid, n)
    rows = []
    for r in picked:
        sents = sorted(set(e.get("sentence") for e in (r.get("evidence") or [])
                           if e.get("sentence")))
        hyp = r.get("hypothesis") or {}
        rows.append({
            "subject": r["subject"], "object": r["object"],
            "subject_type": "COMMON", "subject_head_lemma": r["subject"],
            "segment": r.get("segment"), "pattern": None,
            "n_attestations": r.get("n_exposures"), "pmi": None, "patterns_seen": [],
            "source_sentences": sents[:5],
            "definiendum_surface": None, "definiens_surface": None,
            "fid": r["fid"], "relation": r["relation"],
            "best_cos": r.get("best_cos"), "schema_score": r.get("schema_score"),
            "n_confirm": hyp.get("n_confirm"), "n_disconfirm": hyp.get("n_disconfirm"),
            "n_abandoned": hyp.get("n_abandoned"),
        })
    return rows


_ASCII_FOLD = {0x2018: "'", 0x2019: "'", 0x201a: "'", 0x201b: "'", 0x201c: '"', 0x201d: '"',
               0x201e: '"', 0x2013: "-", 0x2014: "-", 0x2212: "-", 0x2026: "...", 0x00a0: " "}


def _ascii(s: str) -> str:
    return "".join(c if ord(c) < 128 else "?" for c in s.translate(_ASCII_FOLD))


def write_scoring_sheet(path: str, blind_rows: List[dict]) -> None:
    """EXACT format of data/exp_grounding_quality_readout_v1/SCORING_SHEET.txt (100-char rule,
    `[%03d] subj  ->  obj`, 6-space indent, sentence truncated to s[:157] + '...').

    NO-LEAK: best_cos, schema_score, every attestation counter, fid and segment are NOT printed,
    and EXACTLY ONE context sentence is printed per row so block shape carries no arm signal.
    arm_key.json is never read here."""
    lines = [
        "GROUNDED_MEANING BLIND SCORING SHEET  (exp_%s)" % ANCHOR_NAME,
        "%d rows, file order preserved. Rubric: MEANINGFUL / RELATED / NOISE." % len(blind_rows),
        "Line 1: [idx] subject -> assigned grounded meaning.  Line 2: one context sentence "
        "(<=160 chars).",
        "Write your verdict at the end of line 1 for each row.",
        "=" * 100,
        "",
    ]
    for i, r in enumerate(blind_rows, start=1):
        lines.append("[%03d] %s  ->  %s" % (i, _ascii(r["subject"]), _ascii(r["object"])))
        srcs = r.get("source_sentences") or [""]
        s = _ascii(srcs[0])
        if len(s) > 160:
            s = s[:157] + "..."
        lines.append('      "%s"' % s)
        lines.append("")
    with open(path + ".tmp", "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    os.replace(path + ".tmp", path)


def write_audit_samples(output_dir: str, arms: Dict[str, dict]) -> dict:
    combined = []
    out_paths = {}
    for arm in ARMS:
        with open(os.path.join(output_dir, f"arm_{arm}_provenance.json"), encoding="utf-8") as f:
            prov = json.load(f)
        rows = _sample_rows(prov)
        env = {
            "arm": arm, "n_facts_in_arm": arms[arm]["n_meaning_facts"],
            "sample_seed": SAMPLE_SEED,
            "sampling": "random.Random(42).sample over fid order",
            "rubric": "MEANINGFUL / RELATED / NOISE per "
                      "notes/foundation_grounding_sample_2026-08-12.md",
            "scored": False,
            "note": "UNSCORED. The cell assigns no buckets and claims no quality band. This "
                    "sample is SECONDARY; the primary discriminator is known-answer recall. "
                    "Bands: " + PREREG + " sec 4.",
            "rows": rows,
        }
        name = f"b3_audit_sample_{arm}.json"
        _atomic_json(os.path.join(output_dir, name), env)
        out_paths[arm] = name
        combined.extend((arm, r) for r in rows)

    rng = random.Random(BLIND_SHUFFLE_SEED)
    rng.shuffle(combined)
    blind_rows, key_rows = [], []
    for i, (arm, r) in enumerate(combined):
        blind_rows.append(dict(r, blind_id=i))
        key_rows.append({"blind_id": i, "arm": arm, "subject": r["subject"],
                         "object": r["object"], "fid": r["fid"]})
    _atomic_json(os.path.join(output_dir, "blind_sample.json"), {
        "n_rows": len(blind_rows), "shuffle_seed": BLIND_SHUFFLE_SEED,
        "sample_seed": SAMPLE_SEED,
        "arms_present": "TWO, LABELS STRIPPED -- the key is in arm_key.json, do not open it "
                        "until every row is scored",
        "rubric": "MEANINGFUL / RELATED / NOISE per "
                  "notes/foundation_grounding_sample_2026-08-12.md",
        "instruction": "Score each row's (subject -> object) read-out as MEANINGFUL / RELATED / "
                       "NOISE using source_sentences as context. Score all rows in ONE sitting.",
        "scored": False, "bands": BANDS, "rows": blind_rows,
    })
    _atomic_json(os.path.join(output_dir, "arm_key.json"), {
        "warning": "DO NOT OPEN UNTIL blind_sample.json IS FULLY SCORED",
        "shuffle_seed": BLIND_SHUFFLE_SEED, "rows": key_rows})
    write_scoring_sheet(os.path.join(output_dir, "SCORING_SHEET.txt"), blind_rows)
    return {"per_arm_files": out_paths, "blind_file": "blind_sample.json",
            "key_file": "arm_key.json", "sheet": "SCORING_SHEET.txt",
            "n_blind_rows": len(blind_rows)}


# =========================================================================== finalize
def _band(av_delta: Optional[float], r1_delta: Optional[float]) -> str:
    if av_delta is None or r1_delta is None:
        return "INCOMPLETE"
    if av_delta < 0.30:
        return "BROKEN_MANIPULATION_DID_NOT_MOVE"
    if r1_delta <= -0.03:
        return "HURTS"
    if r1_delta >= 0.10:
        return "POOL_WAS_BINDING"
    if r1_delta >= 0.03:
        return "PARTIAL"
    return "COMPARATOR_IS_BINDING"


def finalize(run_mode: str, output_dir: str) -> dict:
    units = exp_checkpoint.load_units(output_dir)
    arms = {a: units[exp_checkpoint.unit_key("arm_done", a)] for a in ARMS
            if exp_checkpoint.unit_key("arm_done", a) in units}
    missing_arms = [a for a in ARMS if a not in arms]

    present = sorted(set(units))
    expected = sorted(set(exp_checkpoint.unit_key(a, s) for a in ARMS for s in SEGMENTS))
    missing_units = [k for k in expected if k not in present]
    s1 = not missing_arms and not missing_units

    s2 = {a: {"n_tautology_facts": arms[a]["n_tautology_facts"],
              "n_closed_class_object_facts": arms[a]["n_closed_class_object_facts"],
              "no_leak_violations": arms[a]["no_leak_violations"]} for a in arms}
    s2_ok = all(v["n_tautology_facts"] == 0 and v["n_closed_class_object_facts"] == 0
                and not v["no_leak_violations"] for v in s2.values())

    digests = {a: arms[a]["pairs_digest"] for a in arms}
    s3 = len(arms) == len(ARMS) and len(sorted(set(digests.values()))) == len(ARMS)

    s4 = {"reference": REF_RUN, "expected_n_facts": REF_N_FACTS,
          "expected_digest16": REF_DIGEST16}
    if "SMALL" in arms:
        got_n = arms["SMALL"]["n_meaning_facts"]
        got_d = arms["SMALL"]["pairs_digest"][:16]
        s4.update({"observed_n_facts": got_n, "observed_digest16": got_d,
                   "small_reproduces_reference": bool(got_n == REF_N_FACTS
                                                      and got_d == REF_DIGEST16)})
    else:
        s4["small_reproduces_reference"] = None

    s5 = {a: {"n_meaning_facts": arms[a]["n_meaning_facts"],
              "meets_yield_floor_50": arms[a]["n_meaning_facts"] >= 50} for a in arms}

    # ---- PRIMARY: known-answer recall deltas
    def _slim(ka):
        return {k: v for k, v in ka.items() if k != "rows"}

    primary = {}
    for key_name in ("v5_definitional", "v62_predicate"):
        per_arm = {a: _slim(arms[a]["known_answer_recall"][key_name]) for a in arms}
        d = {}
        if len(per_arm) == 2:
            for m in ("availability", "recall_at_1", "recall_at_5",
                      "availability_conditioned_recall_at_1"):
                lo, hi = per_arm["SMALL"][m], per_arm["LARGE"][m]
                d[m + "_delta"] = (round(hi - lo, 6) if (lo is not None and hi is not None)
                                   else None)
        primary[key_name] = {"per_arm": per_arm, "deltas": d}

    v5d = primary["v5_definitional"]["deltas"]
    band = _band(v5d.get("availability_delta"), v5d.get("recall_at_1_delta"))

    # ---- SECONDARY: co-occurrence agreement, per arm
    top = cooccurrence_top(run_mode, k=5)
    cooc = {a: cooc_agreement(arms[a]["grounded_objects"], top) for a in arms}

    sample_info = {}
    if len(arms) == len(ARMS):
        sample_info = write_audit_samples(output_dir, arms)

    metrics = {
        "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(), "prereg": PREREG,
        "wire_status": "VET_PENDING -- anchor_pool is DEFAULT-OFF; nothing wired ON",
        "verdict": band if (s1 and s2_ok and s3) else "STRUCTURAL_INCOMPLETE",
        "verdict_msg": (
            "ONE VARIABLE = anchor pool size. Band is read off the v5 RELATION-MATCHED "
            "known-answer key. NO quality claim is made from the blind hand-score sample."),
        "QUALITY_CLAIM": "NONE from the hand-score sample -- the Director scores that blind. The "
                         "known-answer recall numbers are objective and hand-score independent.",
        "bands_preregistered": BANDS,
        "chosen_depth": {
            "seed_depth_rows": LARGE_POOL_DEPTH,
            "why": "shallowest depth reaching a great majority of corpus content lemmas "
                   "(0.7549 of types, 0.9477 of tokens); depth 20000 reaches only 0.5092 of "
                   "types. Marginal anchor cost is small (12691 vs 8561 occurring lemmas) "
                   "because the CORPUS vocabulary is the binding constraint.",
            "coverage_table": "data/exp_anchor_pool_expansion_v1/_probe_coverage.json",
        },
        "PRIMARY_known_answer_recall": primary,
        "structural_gates": {
            "S1_cardinality": {"ok": s1, "expected_n_units": EXPECTED_N_UNITS,
                               "n_present": len(present), "missing_units": missing_units,
                               "missing_arms": missing_arms},
            "S2_integrity": {"ok": s2_ok, "per_arm": s2},
            "S3_arms_differ": {"ok": s3, "digests": digests},
            "S4_small_regression": s4,
            "S5_yield_floor": s5,
            "S6_default_off_witness":
                "hdlab.reading_grounding_loop._selftest_anchor_pool_is_off_by_default",
        },
        "secondary_cooccurrence_agreement": {
            "what": "agreement between each arm's banked (subject -> object) facts and a PLAIN "
                    "sentence-level co-occurrence baseline over the same 34169-sentence corpus. "
                    "Hand-score independent. Same recipe as exp_structured_comparator_v1.",
            "per_arm": cooc,
        },
        "resources": {a: {"anchor_matrix_shape": arms[a]["anchor_matrix_shape"],
                          "anchor_matrix_bytes": arms[a]["anchor_matrix_bytes"],
                          "n_anchors": arms[a]["n_anchors"],
                          "n_eligible_anchors": arms[a]["n_eligible_anchors"],
                          "peak_rss_bytes": arms[a]["peak_rss_bytes"],
                          "elapsed_s": arms[a]["elapsed_s"]} for a in arms},
        "objective_metrics": {a: {k: v for k, v in arms[a].items()
                                  if k not in ("grounded_objects", "known_answer_recall")}
                              for a in arms},
        "deliverable": sample_info,
        "limitations": [
            "A pool lemma's anchor profile is a bag-of-co-occurrence sum exactly like a seed "
            "anchor's. This cell tests AVAILABILITY, not a better representation.",
            "24.5% of corpus content types are absent from the base vocabulary at ANY depth "
            "(proper nouns, technical biology terms); that sets LARGE's availability ceiling.",
            "The primary read-out is POST-HOC against each arm's FINAL anchor field, not the "
            "field as it stood at the live decision. Fair between arms (same procedure both "
            "sides); not the live decision.",
            "The v5 key is 64% correct, so recall against it is bounded near 0.64 and the DELTA, "
            "not the level, is interpretable. The v62 key is 94% correct but its relations are "
            "ENABLING_CONDITION / PROCESS_ACTION etc, NOT GROUNDED_MEANING -- relation-mismatched "
            "to the read-out, reported for completeness only.",
            "Expanding the pool also lets a target be named by a word the loop has not itself "
            "grounded; that is the intended manipulation, but it means LARGE's banked facts are "
            "not a subset-comparable population to SMALL's.",
        ],
    }
    _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
    return metrics


# =========================================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    ap.add_argument("--arm", choices=ARMS + ["finalize", "all"], default=None)
    args = ap.parse_args()

    if args.mode == "self-test":
        from hdlab.reading_grounding_loop import _run_all_selftests
        _selftest_incremental_space_matches_stock()
        r = _run_all_selftests()
        print(json.dumps({"selftests": len(r), "incremental_space_matches_stock": True,
                          "anchor_pool_off_by_default": r["anchor_pool_off_by_default_ok"],
                          "ok": True}, indent=2))
        return

    _selftest_incremental_space_matches_stock()          # gate: never run on an unproven space
    output_dir = _output_dir(args.mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, args.mode, args.arm)
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    todo = ARMS + ["finalize"] if args.arm in (None, "all") else [args.arm]
    for step in todo:
        try:
            if step == "finalize":
                m = finalize(args.mode, output_dir)
                print(json.dumps({"verdict": m["verdict"],
                                  "S4": m["structural_gates"]["S4_small_regression"],
                                  "v5": m["PRIMARY_known_answer_recall"]["v5_definitional"],
                                  "v62": m["PRIMARY_known_answer_recall"]["v62_predicate"],
                                  "cooc": m["secondary_cooccurrence_agreement"]["per_arm"],
                                  "resources": m["resources"]}, indent=2), flush=True)
            else:
                s = run_arm(step, args.mode, output_dir)
                print(json.dumps({k: s[k] for k in (
                    "arm", "anchor_pool_depth_rows", "n_anchors", "anchor_matrix_shape",
                    "n_meaning_facts", "n_grounded", "peak_rss_bytes", "elapsed_s")}, indent=2),
                    flush=True)
        except Exception:
            traceback.print_exc()
            raise


if __name__ == "__main__":
    main()
