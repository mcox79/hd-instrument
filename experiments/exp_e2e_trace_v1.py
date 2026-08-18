"""exp_e2e_trace_v1 -- STAGE-BY-STAGE ATTRITION CENSUS of the live reading-grounding path.

WHAT THIS IS: a census, not an evaluation. It runs the SHIPPED live path
(hdlab.reading_grounding_loop.process_sentence + checkpoint, PBV on, readout OFF, freeze OFF,
encoder OFF, anchor_pool OFF, definition_map OFF) over the full v5 line-aware corpus and counts,
at every stage, HOW MANY ITEMS ENTER, HOW MANY LEAVE, AND WHY THE REST ARE LOST.

NO QUALITY CLAIM IS MADE ANYWHERE IN THIS CELL. Nothing is hand-scored. The one place a
"correct answer" appears is the known-answer key read off
data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl, which is itself
only ~64% correct (notes/director_handscore_b3_v5_termboundary_2026-08-12.md); it is used ONLY to
split "the answer was ABSENT from the candidate set" from "the answer was PRESENT and not
selected", which is a structural question about the pipeline, not a correctness claim about the
substrate.

INSTRUMENTATION MUST NOT CHANGE BEHAVIOUR. Nothing in hdlab/ is modified. Every counter is a PURE
WRAPPER installed by monkeypatch on the module attribute the live code resolves at call time:

    hdlab.reading_grounding_loop.content_lemmas          (stage 1: input)
    hdlab.reading_grounding_loop.is_gap                  (stage 2: gap gate)
    hdlab.reading_grounding_loop.context_vector_masked   (stage 2b: encoding)
    hdlab.reading_grounding_loop.canonicalize_fast       (stages 3+4: candidates + selection)
    hdlab.grounding_acquisition_loop.schema_consistency_split_half   (stage 5: coherence gate)
    the ReadingLoopState's own Library.flag and HDFactStore.store bound methods (stages 2c + 7)

Each wrapper calls the original FIRST and returns its exact return value; none mutates any
argument, consumes any RNG, or touches any global the live path reads.

TWO WITNESSES that the instrumentation is inert:
  W1 `--mode self-test`: the SAME short slice is run twice, tracer ON and tracer OFF, and the
     banked (subject, object) pairs digest, fact count, refusal-reason counts, growth curve and
     full PBV trajectory must be IDENTICAL. (This is the analogue of
     hdlab.reading_grounding_loop._selftest_anchor_pool_is_off_by_default.)
  W2 the FULL run is configured identically to the landed reference arm
     data/exp_grounding_quality_readout_v1/metrics.json:objective_metrics.PBV_BASE and must
     reproduce its 384 facts / pairs_digest 836571fa99d5765d... / 24949 refusals / trajectory.
     A mismatch is reported LOUDLY in metrics.json and voids the census.

ASCII-only. Deterministic: fixed integer seeds, sorted(set(...)) iteration, hashlib-seeded
vectors, single-threaded BLAS.
"""
from __future__ import annotations

import os

# MUST precede numpy import (BLAS thread nondeterminism; CLAUDE.md "Thread-count env vars").
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
from collections import Counter, defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import hdlab.grounding_acquisition_loop as GAL
import hdlab.reading_grounding_loop as RGL

from hdlab.closed_class_lexicon import is_closed_class, is_eligible_meaning
from hdlab.grounding_acquisition_loop import MIN_CONFIRM, PATIENCE_MAX, content_words
from hdlab.hd_fact_store import HDFactStore
from hdlab.reading_grounding_loop import (
    KNOWN_RELATION,
    MEANING_RELATION,
    PBV_COMMIT_STRENGTH,
    PBV_INFORMATIVE_MIN,
    ReadingLoopState,
    checkpoint,
    make_pbv_fns,
    normalize_lemma,
    pbv_trajectory_stats,
    process_sentence,
    seed_known_words,
)

from experiments.exp_reading_grounding_loop_cycle1_v1 import (
    N_DIM, SCHEMA_THRESH_FULL, load_base_vocab_seed, repo_path,
)
from experiments.exp_reading_grounding_loop_cycle2_v1 import CHUNK_SIZE, grounded_lemmas_in_store
from experiments.exp_definitional_grounding_v5 import load_corpus_v5

ANCHOR_NAME = "e2e_trace_v1"
NOTE = "notes/e2e_substrate_trace_2026-08-13.md"

# ---- LIVE CONFIG: identical to data/exp_grounding_quality_readout_v1 arm PBV_BASE -------------
ARM_SEED = 4201
SEGMENTS = ["bootstrap", "ele_cont", "int_cont", "adv_new", "bio_new"]

# ---- W2 reference (MEASURED@data/exp_grounding_quality_readout_v1/metrics.json:
#      objective_metrics.PBV_BASE) --------------------------------------------------------------
REF = {
    "n_sentences": 34169, "n_chunks": 228, "n_grounded": 384, "n_meaning_facts": 384,
    "n_refusals": 24949,
    "refusal_reasons": {"CLOSED_CLASS_SUBJECT": 247, "HYPOTHESIS_BELOW_COMMIT_STRENGTH": 21240,
                        "NO_STANDING_HYPOTHESIS": 3462},
    "pairs_digest16": "836571fa99d5765d",
    "trajectory": {"n_items": 15990, "n_items_with_hypothesis": 10450, "n_items_revised": 3358,
                   "n_encounters": 83723, "n_informative_encounters": 26586,
                   "n_confirm": 1112, "n_disconfirm": 15540, "n_abandon": 5972,
                   "n_repropose": 5972, "n_revive": 10122},
}

V5_KEY = "data/foundation/reading_grounding_v5_termboundary/definitional_facts_v5.jsonl"

COS_BINS = [-1.01, -0.10, 0.00, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45,
            0.50, 0.60, 0.70, 0.85, 1.01]


# ============================================================================== io helpers
def _atomic_json(path: str, obj: object) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2)
    os.replace(tmp, path)


def _output_dir(run_mode: str) -> str:
    return repo_path("data/exp_" + ANCHOR_NAME + ("_selftest" if run_mode == "self-test" else ""))


def _write_start_marker(output_dir: str, run_mode: str) -> None:
    os.makedirs(output_dir, exist_ok=True)
    _atomic_json(os.path.join(output_dir, "_start_marker.json"),
                 {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                  "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node(),
                  "note": NOTE})


def _heartbeat(output_dir: str, payload: dict) -> None:
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(dict(payload, ts_iso=datetime.now(timezone.utc).isoformat())) + "\n")


def _digest_pairs(pairs) -> str:
    h = hashlib.sha256()
    for s, o in sorted(set(pairs)):
        h.update(("%s\x1f%s\x1e" % (s, o)).encode("utf-8"))
    return h.hexdigest()


def _quantiles(xs: List[float]) -> Optional[dict]:
    if not xs:
        return None
    a = np.sort(np.asarray(xs, dtype=np.float64))
    q = {("p%02d" % p): round(float(np.percentile(a, p)), 6)
         for p in (1, 5, 10, 25, 50, 75, 90, 95, 99)}
    q.update({"n": int(a.size), "min": round(float(a[0]), 6), "max": round(float(a[-1]), 6),
              "mean": round(float(a.mean()), 6)})
    return q


def _hist(counter: Counter) -> Dict[str, int]:
    out = {}
    for i in range(len(COS_BINS) - 1):
        out["[%.2f,%.2f)" % (COS_BINS[i], COS_BINS[i + 1])] = int(counter.get(i, 0))
    return out


def _bin_of(x: float) -> int:
    i = int(np.searchsorted(COS_BINS, x, side="right")) - 1
    return max(0, min(len(COS_BINS) - 2, i))


# ============================================================================== the tracer
class Tracer:
    """Pure counting wrappers over the live path. install() monkeypatches module attributes the
    live code resolves at CALL time; uninstall() restores them. No wrapper mutates an argument or
    changes a return value."""

    def __init__(self) -> None:
        self.state: Optional[ReadingLoopState] = None
        self.key: Dict[str, set] = {}
        self.installed = False
        self.stage = "none"                 # "propose" | "verify" | "gate" | "none"

        # ---- stage 1: input
        self.n_sentences = 0
        self.n_raw_ws_tokens = 0
        self.n_content_word_tokens = 0        # tokens surviving content_words()
        self.n_lemma_occurrences = 0          # distinct content LEMMAS per sentence, summed
        self.n_sentences_zero_content = 0
        self.lemma_freq: Counter = Counter()

        # ---- stage 2: gap gate / target selection
        self.n_seed_occurrences = 0           # anchor-accumulation only, never a target
        self.n_nonseed_occurrences = 0
        self.n_isgap_calls = 0
        self.n_gap_true = 0
        self.n_gap_false = 0                  # detector says the foundation knows it
        self.gap_true_lemmas: set = set()
        self.gap_false_lemmas: set = set()
        self.seed_lemmas_seen: set = set()

        # ---- stage 2b: encoding
        self.n_encode_calls = 0
        self.n_encode_zero = 0                # all-stopword / no-content window -> all-zero vector

        # ---- stage 2c: flag
        self.n_flag_calls = 0
        self.n_flag_true = 0
        self.n_flag_false = 0                 # terminal item, trace refused

        # ---- stages 3+4: candidates + selection
        self.n_canon_calls = 0
        self.n_canon_by_stage: Counter = Counter()
        self.n_pool_empty = 0                 # zero anchors at all
        self.n_pool_no_scannable = 0          # anchors exist, none eligible/scannable
        self.n_query_zero_norm = 0            # target profile is a zero vector
        self.pool_sizes: List[int] = []       # scannable candidates offered, sampled
        self.pool_size_sum = 0
        self.pool_size_min = None
        self.pool_size_max = 0
        self.cos_hist: Counter = Counter()
        self.cos_sample: List[float] = []
        self.n_cleared = 0                    # argmax cleared informative_min -> a candidate
        self.n_not_cleared = 0                # self-return: uninformative encounter
        self.cleared_by_stage: Counter = Counter()
        self.winner_freq: Counter = Counter()

        # ---- stage 5: consolidation / admission
        self.n_schema_calls = 0
        self.n_schema_none = 0
        self.n_schema_below = 0
        self.n_schema_ok = 0
        self.schema_sample: List[float] = []
        self.pass_rows: List[dict] = []

        # ---- stage 6: PBV
        self.n_propose_calls = 0
        self.n_propose_none = 0               # SILENT: no hypothesis, nothing logged anywhere
        self.n_propose_some = 0
        self.n_verify_calls = 0
        self.n_verify_none = 0
        self.n_verify_true = 0
        self.n_verify_false = 0

        # ---- stage 7: store
        self.store_resolutions: Counter = Counter()
        self.store_writes_by_relation: Counter = Counter()
        self.sr_objects: Dict[Tuple[str, str], List[str]] = defaultdict(list)

        # ---- known-answer key tracking, LIVE (at the decision, not post-hoc)
        self.key_calls: Counter = Counter()
        self.key_avail_calls: Counter = Counter()
        self.key_argmax_hit: Counter = Counter()
        self.key_best_rank: Dict[str, int] = {}
        self.key_answer_cos: Dict[str, float] = {}
        self.key_winner_cos: Dict[str, float] = {}

        # ---- timing (inclusive; canonicalize/encode time is nested inside flag time)
        self.t: Counter = Counter()

        self._orig: Dict[str, object] = {}

    # ---------------------------------------------------------------- install / uninstall
    def install(self, state: ReadingLoopState, key: Dict[str, set]) -> None:
        assert not self.installed, "tracer already installed"
        self.state = state
        self.key = key
        self._orig = {
            "content_lemmas": RGL.content_lemmas,
            "is_gap": RGL.is_gap,
            "context_vector_masked": RGL.context_vector_masked,
            "canonicalize_fast": RGL.canonicalize_fast,
            "schema": GAL.schema_consistency_split_half,
            "flag": state.library.flag,
            "store": state.store.store,
        }
        RGL.content_lemmas = self._w_content_lemmas
        RGL.is_gap = self._w_is_gap
        RGL.context_vector_masked = self._w_encode
        RGL.canonicalize_fast = self._w_canonicalize_fast
        GAL.schema_consistency_split_half = self._w_schema
        state.library.flag = self._w_flag                     # instance attr shadows the method
        state.store.store = self._w_store
        self.installed = True

    def uninstall(self) -> None:
        if not self.installed:
            return
        RGL.content_lemmas = self._orig["content_lemmas"]
        RGL.is_gap = self._orig["is_gap"]
        RGL.context_vector_masked = self._orig["context_vector_masked"]
        RGL.canonicalize_fast = self._orig["canonicalize_fast"]
        GAL.schema_consistency_split_half = self._orig["schema"]
        try:
            del self.state.library.flag                      # type: ignore[union-attr]
        except AttributeError:
            pass
        try:
            del self.state.store.store                       # type: ignore[union-attr]
        except AttributeError:
            pass
        self.installed = False

    # ---------------------------------------------------------------- stage 1
    def _w_content_lemmas(self, sentence: str) -> List[str]:
        t0 = time.perf_counter()
        out = self._orig["content_lemmas"](sentence)          # type: ignore[operator]
        self.t["stage1_input"] += time.perf_counter() - t0
        self.n_sentences += 1
        self.n_raw_ws_tokens += len(sentence.split())
        self.n_content_word_tokens += len(content_words(sentence))
        self.n_lemma_occurrences += len(out)
        if not out:
            self.n_sentences_zero_content += 1
        seed = self.state.known_seed                          # type: ignore[union-attr]
        for lm in out:
            self.lemma_freq[lm] += 1
            if lm in seed:
                self.n_seed_occurrences += 1
                self.seed_lemmas_seen.add(lm)
            else:
                self.n_nonseed_occurrences += 1
        return out

    # ---------------------------------------------------------------- stage 2
    def _w_is_gap(self, state, lemma: str) -> bool:
        t0 = time.perf_counter()
        r = self._orig["is_gap"](state, lemma)                # type: ignore[operator]
        self.t["stage2_gap"] += time.perf_counter() - t0
        self.n_isgap_calls += 1
        if r:
            self.n_gap_true += 1
            self.gap_true_lemmas.add(lemma)
        else:
            self.n_gap_false += 1
            self.gap_false_lemmas.add(lemma)
        return r

    def _w_encode(self, sentence: str, target_lemma: str, d: int = GAL.D) -> np.ndarray:
        t0 = time.perf_counter()
        v = self._orig["context_vector_masked"](sentence, target_lemma, d)   # type: ignore[operator]
        self.t["stage2b_encode"] += time.perf_counter() - t0
        self.n_encode_calls += 1
        if not np.any(v != 0.0):
            self.n_encode_zero += 1
        return v

    def _w_flag(self, *args, **kwargs) -> bool:
        t0 = time.perf_counter()
        r = self._orig["flag"](*args, **kwargs)               # type: ignore[operator]
        self.t["stage2c_flag_incl"] += time.perf_counter() - t0
        self.n_flag_calls += 1
        if r:
            self.n_flag_true += 1
        else:
            self.n_flag_false += 1
        return r

    # ---------------------------------------------------------------- stages 3 + 4
    def _w_canonicalize_fast(self, new_lemma, new_raw_sum, space, thresh=RGL.SENSE_MATCH_THRESH,
                             eligible_mask=None, *, readout=None):
        t0 = time.perf_counter()
        out = self._orig["canonicalize_fast"](                # type: ignore[operator]
            new_lemma, new_raw_sum, space, thresh=thresh, eligible_mask=eligible_mask,
            readout=readout)
        self.t["stage34_select"] += time.perf_counter() - t0
        obj, cos = out
        self.n_canon_calls += 1
        self.n_canon_by_stage[self.stage] += 1

        anchors, mat = space.anchor_matrix()
        n_anchors = len(anchors)
        if n_anchors == 0:
            self.n_pool_empty += 1
            n_scan = 0
            keep = None
        else:
            keep = np.ones(n_anchors, dtype=bool) if eligible_mask is None else eligible_mask.copy()
            i = int(np.searchsorted(anchors, new_lemma))
            if i < n_anchors and anchors[i] == new_lemma:
                keep[i] = False
            n_scan = int(keep.sum())
            if n_scan == 0:
                self.n_pool_no_scannable += 1
        nb = np.sign(new_raw_sum)
        if float(np.linalg.norm(nb)) < 1e-9:
            self.n_query_zero_norm += 1
        self.pool_size_sum += n_scan
        self.pool_size_max = max(self.pool_size_max, n_scan)
        self.pool_size_min = n_scan if self.pool_size_min is None else min(self.pool_size_min, n_scan)
        if self.n_canon_calls % 97 == 0:
            self.pool_sizes.append(n_scan)
            self.cos_sample.append(float(cos))
        self.cos_hist[_bin_of(float(cos))] += 1
        if obj == new_lemma:
            self.n_not_cleared += 1
        else:
            self.n_cleared += 1
            self.cleared_by_stage[self.stage] += 1
            self.winner_freq[obj] += 1

        answers = self.key.get(new_lemma)
        if answers and keep is not None and n_scan:
            self._key_probe(new_lemma, answers, anchors, mat, keep, nb, obj, float(cos))
        return out

    def _key_probe(self, lemma, answers, anchors, mat, keep, nb, winner, winner_cos) -> None:
        """LIVE absent-vs-not-selected probe for a known-answer subject: is a correct object a
        scannable anchor at THIS decision, and if so what rank does it get. Read-only."""
        t0 = time.perf_counter()
        self.key_calls[lemma] += 1
        idxs = []
        for a in sorted(answers):
            j = int(np.searchsorted(anchors, a))
            if j < len(anchors) and anchors[j] == a and keep[j]:
                idxs.append(j)
        if not idxs:
            self.t["key_probe"] += time.perf_counter() - t0
            return
        self.key_avail_calls[lemma] += 1
        if winner in answers:
            self.key_argmax_hit[lemma] += 1
        nn = float(np.linalg.norm(nb))
        if nn < 1e-9:
            self.t["key_probe"] += time.perf_counter() - t0
            return
        norms = np.linalg.norm(mat, axis=1)
        ok = keep & (norms >= 1e-9)
        sims = np.full(len(anchors), -np.inf)
        if ok.any():
            sims[ok] = (mat[ok] @ nb) / (norms[ok] * nn)
        sims[keep & ~ok] = 0.0
        best_j = max(idxs, key=lambda j: sims[j])
        ans_cos = float(sims[best_j])
        rank = int(1 + np.sum(sims[keep] > ans_cos))
        prev = self.key_best_rank.get(lemma)
        if prev is None or rank < prev:
            self.key_best_rank[lemma] = rank
            self.key_answer_cos[lemma] = round(ans_cos, 6)
            self.key_winner_cos[lemma] = round(winner_cos, 6)
        self.t["key_probe"] += time.perf_counter() - t0

    # ---------------------------------------------------------------- stage 5
    def _w_schema(self, traces, min_half_size=2, coherence_fn=None):
        t0 = time.perf_counter()
        s = self._orig["schema"](traces, min_half_size=min_half_size,   # type: ignore[operator]
                                 coherence_fn=coherence_fn)
        self.t["stage5_schema"] += time.perf_counter() - t0
        self.n_schema_calls += 1
        if s is None:
            self.n_schema_none += 1
        else:
            if len(self.schema_sample) < 200000:
                self.schema_sample.append(float(s))
            if s >= SCHEMA_THRESH_FULL:
                self.n_schema_ok += 1
            else:
                self.n_schema_below += 1
        return s

    # ---------------------------------------------------------------- stage 7
    def _w_store(self, *args, **kwargs):
        t0 = time.perf_counter()
        res = self._orig["store"](*args, **kwargs)            # type: ignore[operator]
        self.t["stage7_store"] += time.perf_counter() - t0
        subject, relation, obj = args[0], args[1], args[2]
        self.store_resolutions[res.resolution] += 1
        self.store_writes_by_relation[relation] += 1
        self.sr_objects[(subject, relation)].append(obj)
        return res

    # ---------------------------------------------------------------- PBV fn wrappers
    def wrap_pbv(self, propose_fn, verify_fn):
        def propose(item, tr):
            self.stage = "propose"
            t0 = time.perf_counter()
            try:
                r = propose_fn(item, tr)
            finally:
                self.stage = "none"
            self.t["stage6_propose_incl"] += time.perf_counter() - t0
            self.n_propose_calls += 1
            if r is None:
                self.n_propose_none += 1
            else:
                self.n_propose_some += 1
            return r

        def verify(item, tr):
            self.stage = "verify"
            t0 = time.perf_counter()
            try:
                r = verify_fn(item, tr)
            finally:
                self.stage = "none"
            self.t["stage6_verify_incl"] += time.perf_counter() - t0
            self.n_verify_calls += 1
            if r is None:
                self.n_verify_none += 1
            elif r:
                self.n_verify_true += 1
            else:
                self.n_verify_false += 1
            return r

        for attr in ("freeze_stats", "release_episodes"):
            if hasattr(propose_fn, attr):
                setattr(propose, attr, getattr(propose_fn, attr))
            if hasattr(verify_fn, attr):
                setattr(verify, attr, getattr(verify_fn, attr))
        return propose, verify

    # ---------------------------------------------------------------- pre-consolidation census
    def observe_pre_consolidation(self, state: ReadingLoopState, pass_idx: int) -> dict:
        """READ-ONLY replication of consolidation_pass's OWN eligibility arithmetic, evaluated on
        the library exactly as it stands before the pass. Touches only cheap scalar fields
        (status / len(traces) / first_min_confirm_pass); never computes a vector, never mutates."""
        t0 = time.perf_counter()
        n_items = n_pending = n_under = n_wait = n_eligible = 0
        for lemma in state.library.items:
            it = state.library.items[lemma]
            n_items += 1
            if it.status != "PENDING":
                continue
            n_pending += 1
            if len(it.traces) < MIN_CONFIRM:
                n_under += 1
                continue
            first = it.first_min_confirm_pass
            if first is None or pass_idx <= first:
                n_wait += 1                 # intervening-pass rule (no patience cost)
                continue
            n_eligible += 1
        row = {"pass_idx": pass_idx, "n_library_items": n_items, "n_pending": n_pending,
               "n_under_min_confirm": n_under, "n_intervening_wait": n_wait,
               "n_reaching_schema_gate": n_eligible}
        self.t["stage5_census"] += time.perf_counter() - t0
        return row


# ============================================================================== known-answer key
def load_key(corpus_lemmas: set, known_seed: set) -> Dict[str, set]:
    """subject -> set of KNOWN objects, from the v5 definitional facts. Same restriction rules as
    data/exp_anchor_pool_expansion_v1/_probe_coverage.py (single-token subject and object, subject
    not already seed-known, subject occurs in the corpus, object eligible), rebuilt here so this
    cell does not depend on another cell's output directory."""
    by_subj: Dict[str, set] = {}
    n_rows = 0
    with open(repo_path(V5_KEY), encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            n_rows += 1
            s_raw = r.get("subject_head_lemma") or r.get("subject") or ""
            parts = str(s_raw).split()
            if len(parts) != 1:
                continue
            o_parts = str(r.get("object") or "").split()
            if len(o_parts) != 1:
                continue
            s, o = normalize_lemma(parts[0]), normalize_lemma(o_parts[0])
            if not s or not o or s == o or s in known_seed or s not in corpus_lemmas:
                continue
            if not is_eligible_meaning(o):
                continue
            by_subj.setdefault(s, set()).add(o)
    return by_subj


# ============================================================================== the run
def build_stream(run_mode: str) -> List[Tuple[str, str]]:
    limit = 60 if run_mode == "self-test" else None
    return load_corpus_v5(limit, lineaware=True)


def new_state() -> ReadingLoopState:
    store = HDFactStore(n_dim=N_DIM, seed=ARM_SEED,
                        relation_cardinality={KNOWN_RELATION: "FUNCTIONAL",
                                              MEANING_RELATION: "FUNCTIONAL"},
                        use_index=True)
    state = ReadingLoopState(store=store)
    seed_known_words(state, load_base_vocab_seed(), source="seed_base_vocabulary")
    return state


def run_pass(stream, output_dir: str, tracer: Optional[Tracer], key: Optional[Dict[str, set]],
             progress: bool = True) -> dict:
    """One full live reading pass. tracer=None is the UNINSTRUMENTED control path."""
    state = new_state()
    if tracer is not None:
        tracer.install(state, key or {})
    propose_fn, verify_fn = make_pbv_fns(state)                # readout OFF, freeze OFF (shipped)
    if tracer is not None:
        propose_fn, verify_fn = tracer.wrap_pbv(propose_fn, verify_fn)
    pbv_fns = (propose_fn, verify_fn)

    n_chunks = math.ceil(len(stream) / CHUNK_SIZE) if stream else 0
    t0 = time.time()
    last_hb = t0
    curve: List[dict] = []
    for chunk_idx in range(n_chunks):
        chunk = stream[chunk_idx * CHUNK_SIZE:(chunk_idx + 1) * CHUNK_SIZE]
        t_read = time.time()
        for i, (seg, sent) in enumerate(chunk):
            process_sentence(state, sent, "E2E_%d_%d" % (chunk_idx, i), pass_idx=chunk_idx,
                             pbv_fns=pbv_fns, revive_terminal=True)
        t_read = time.time() - t_read
        pre = tracer.observe_pre_consolidation(state, chunk_idx) if tracer is not None else {}
        t_cons = time.time()
        seg_tag = chunk[-1][0] if chunk else "unknown"
        row = checkpoint(state, pass_idx=chunk_idx, source_tag=seg_tag,
                         schema_thresh=SCHEMA_THRESH_FULL, pbv=True,
                         commit_strength=PBV_COMMIT_STRENGTH)
        t_cons = time.time() - t_cons
        if tracer is not None:
            tracer.t["read_phase"] += t_read
            tracer.t["consolidation_phase"] += t_cons
            reasons = Counter(r["reason"] for r in state.refusals if r["pass_idx"] == chunk_idx)
            pre.update({"segment": seg_tag, "n_anchors": len(state.space.anchors()),
                        "newly_grounded": row["newly_grounded"],
                        "newly_escalated": row["newly_escalated"],
                        "n_refused_this_pass": row["n_refused_this_pass"],
                        "refusal_reasons_this_pass": dict(sorted(reasons.items())),
                        "cumulative_grounded": row["cumulative_grounded"],
                        "read_s": round(t_read, 3), "consolidation_s": round(t_cons, 3)})
            tracer.pass_rows.append(pre)
            curve.append(pre)
            with open(os.path.join(output_dir, "pass_curve.jsonl"), "a", encoding="utf-8") as f:
                f.write(json.dumps(pre) + "\n")
        if progress and (chunk_idx % 10 == 0 or chunk_idx == n_chunks - 1):
            print("[progress] chunk=%d/%d seg=%s anchors=%d grounded=%d refused=%d elapsed=%.1fs"
                  % (chunk_idx + 1, n_chunks, seg_tag, len(state.space.anchors()),
                     row["cumulative_grounded"], row["n_refused_cumulative"], time.time() - t0),
                  flush=True)
        if progress and time.time() - last_hb >= 60.0:
            last_hb = time.time()
            _heartbeat(output_dir, {"chunk": chunk_idx, "n_chunks": n_chunks,
                                    "elapsed_s": round(time.time() - t0, 1)})
    traj = pbv_trajectory_stats(state.library)
    gm = [f for f in state.store.live_facts() if f.relation == MEANING_RELATION]
    out = {
        "state": state,
        "elapsed_s": round(time.time() - t0, 2),
        "n_chunks": n_chunks,
        "n_meaning_facts": len(gm),
        "n_grounded": len(grounded_lemmas_in_store(state.store)),
        "n_refusals": len(state.refusals),
        "refusal_reasons": dict(sorted(Counter(r["reason"] for r in state.refusals).items())),
        "pairs_digest": _digest_pairs((f.subject, f.obj) for f in gm),
        "trajectory": {k: v for k, v in traj.items() if k != "revisions"},
        "growth_curve": state.growth_curve,
        "banked": {f.subject: f.obj for f in gm},
        "curve": curve,
    }
    if tracer is not None:
        tracer.uninstall()
    return out


# ============================================================================== W1 self-test
def selftest(output_dir: str) -> dict:
    """W1: tracer ON vs tracer OFF on the SAME slice must be identical in every observable."""
    stream = build_stream("self-test")
    tr = Tracer()
    on = run_pass(stream, output_dir, tr, {}, progress=False)
    off = run_pass(stream, output_dir, None, None, progress=False)
    checks = {
        "n_meaning_facts": (on["n_meaning_facts"], off["n_meaning_facts"]),
        "n_grounded": (on["n_grounded"], off["n_grounded"]),
        "n_refusals": (on["n_refusals"], off["n_refusals"]),
        "refusal_reasons": (on["refusal_reasons"], off["refusal_reasons"]),
        "pairs_digest": (on["pairs_digest"], off["pairs_digest"]),
        "trajectory": (on["trajectory"], off["trajectory"]),
        "growth_curve": (json.dumps(on["growth_curve"], default=str),
                         json.dumps(off["growth_curve"], default=str)),
        "banked": (on["banked"], off["banked"]),
    }
    bad = {k: v for k, v in checks.items() if v[0] != v[1]}
    assert not bad, "INSTRUMENTATION CHANGED BEHAVIOUR: %r" % (sorted(bad),)
    # the tracer must also have RESTORED every patched attribute
    assert RGL.content_lemmas.__name__ == "content_lemmas", "content_lemmas not restored"
    assert RGL.canonicalize_fast.__name__ == "canonicalize_fast", "canonicalize_fast not restored"
    assert GAL.schema_consistency_split_half.__name__ == "schema_consistency_split_half"
    assert not hasattr(on["state"].library, "__dict__") or "flag" not in vars(on["state"].library)
    # and it must actually have COUNTED something (a no-op tracer would pass vacuously)
    assert tr.n_sentences == len(stream) and tr.n_canon_calls > 0 and tr.n_schema_calls > 0, (
        "tracer collected nothing: %d sentences, %d canon calls, %d schema calls"
        % (tr.n_sentences, tr.n_canon_calls, tr.n_schema_calls))
    return {"ok": True, "n_sentences": len(stream), "n_facts": on["n_meaning_facts"],
            "pairs_digest16": on["pairs_digest"][:16], "n_canon_calls": tr.n_canon_calls,
            "n_schema_calls": tr.n_schema_calls, "n_refusals": on["n_refusals"],
            "counted_lemma_occurrences": tr.n_lemma_occurrences}


# ============================================================================== metrics assembly
def key_outcome(tracer: Tracer, res: dict, key: Dict[str, set]) -> dict:
    """Where the correct answer is lost, for the known-answer subjects the run actually met.

    Buckets are DISJOINT and ordered by how far the answer got:
      NEVER_ENCOUNTERED   the subject never reached a read-out call at all
      ABSENT              reached the read-out, and no correct object was EVER a scannable anchor
      PRESENT_NOT_ARGMAX  a correct object was available, never won the argmax
      ARGMAX_NOT_BANKED   won the argmax at least once, no fact banked
      BANKED_CORRECT / BANKED_OTHER
    """
    state: ReadingLoopState = res["state"]
    banked = res["banked"]
    buckets: Counter = Counter()
    rows = []
    for s in sorted(key):
        answers = key[s]
        calls = tracer.key_calls.get(s, 0)
        avail = tracer.key_avail_calls.get(s, 0)
        hits = tracer.key_argmax_hit.get(s, 0)
        b = banked.get(s)
        it = state.library.items.get(s)
        proposed = []
        if it is not None:
            proposed = [e.get("obj") for e in it.hypothesis_log
                        if e.get("event") in ("PROPOSE", "REPROPOSE")]
        ever_proposed_correct = any(o in answers for o in proposed)
        if b is not None:
            bucket = "BANKED_CORRECT" if b in answers else "BANKED_OTHER"
        elif calls == 0:
            bucket = "NEVER_ENCOUNTERED"
        elif avail == 0:
            bucket = "ABSENT"
        elif hits == 0:
            bucket = "PRESENT_NOT_ARGMAX"
        else:
            bucket = "ARGMAX_NOT_BANKED"
        buckets[bucket] += 1
        rows.append({"subject": s, "answers": sorted(answers), "n_readout_calls": calls,
                     "n_calls_answer_available": avail, "n_calls_answer_argmax": hits,
                     "best_rank": tracer.key_best_rank.get(s),
                     "answer_cos_at_best_rank": tracer.key_answer_cos.get(s),
                     "winner_cos_at_best_rank": tracer.key_winner_cos.get(s),
                     "ever_proposed_correct": ever_proposed_correct,
                     "n_traces": len(it.traces) if it is not None else 0,
                     "item_status": it.status if it is not None else None,
                     "banked_object": b, "bucket": bucket})
    ranks = [r["best_rank"] for r in rows if r["best_rank"] is not None]
    n_prop_correct = sum(1 for r in rows if r["ever_proposed_correct"])
    return {
        "n_key_subjects": len(key),
        "buckets": dict(sorted(buckets.items())),
        "best_rank_of_correct_answer_when_available": _quantiles([float(x) for x in ranks]),
        "n_subjects_with_answer_available_at_least_once": len(ranks),
        "n_subjects_correct_answer_ever_proposed_as_hypothesis": n_prop_correct,
        "rows_file": "key_subject_rows.json",
        "rows": rows,
    }


def assemble(tracer: Tracer, res: dict, key: Dict[str, set], run_mode: str,
             output_dir: str) -> dict:
    state: ReadingLoopState = res["state"]
    banked = res["banked"]
    gm_subjects = sorted(banked)

    # ---- W2 reference reproduction
    w2 = {
        "reference": "data/exp_grounding_quality_readout_v1/metrics.json:objective_metrics."
                     "PBV_BASE",
        "expected": REF,
        "observed": {"n_sentences": tracer.n_sentences, "n_chunks": res["n_chunks"],
                     "n_grounded": res["n_grounded"],
                     "n_meaning_facts": res["n_meaning_facts"],
                     "n_refusals": res["n_refusals"],
                     "refusal_reasons": res["refusal_reasons"],
                     "pairs_digest16": res["pairs_digest"][:16],
                     "trajectory": {k: res["trajectory"].get(k) for k in REF["trajectory"]}},
    }
    w2["matches"] = (run_mode == "full"
                     and w2["observed"]["pairs_digest16"] == REF["pairs_digest16"]
                     and w2["observed"]["n_meaning_facts"] == REF["n_meaning_facts"]
                     and w2["observed"]["n_refusals"] == REF["n_refusals"]
                     and w2["observed"]["refusal_reasons"] == REF["refusal_reasons"]
                     and w2["observed"]["trajectory"] == REF["trajectory"])

    # ---- displacement
    multi = {("%s|%s" % k): v for k, v in sorted(tracer.sr_objects.items())
             if len(sorted(set(v))) > 1}
    repeat_writes = {("%s|%s" % k): len(v) for k, v in sorted(tracer.sr_objects.items())
                     if len(v) > 1}
    superseded = sum(1 for f in state.store._facts
                     if f.relation == MEANING_RELATION and f.status == "SUPERSEDED")
    dropped = sum(1 for f in state.store._facts
                  if f.relation == MEANING_RELATION and f.status == "DROPPED")

    # ---- terminal fate of every library item
    fate = Counter(it.status for it in state.library.items.values())
    exposures = [len(it.traces) for it in state.library.items.values()]
    hyp_strength = [it.hypothesis.strength for it in state.library.items.values()
                    if it.hypothesis is not None]

    n_lemma_occ = tracer.n_lemma_occurrences
    n_terminal_skip = tracer.n_nonseed_occurrences - tracer.n_isgap_calls
    n_zero_ctx_skip = tracer.n_gap_true - tracer.n_flag_calls

    stages = [
        {"stage": "1_input_sentences", "enter": tracer.n_sentences,
         "leave": tracer.n_sentences - tracer.n_sentences_zero_content,
         "lost": tracer.n_sentences_zero_content,
         "why_lost": {"sentence_had_no_content_lemma": tracer.n_sentences_zero_content}},
        {"stage": "1b_tokens_to_content_lemmas", "enter": tracer.n_raw_ws_tokens,
         "leave": n_lemma_occ,
         "lost": tracer.n_raw_ws_tokens - n_lemma_occ,
         "why_lost": {"stopword_or_len<=2_or_nonalpha (content_words regex + stoplist)":
                      tracer.n_raw_ws_tokens - tracer.n_content_word_tokens,
                      "duplicate_lemma_within_the_same_sentence (content_lemmas is a set)":
                      tracer.n_content_word_tokens - n_lemma_occ}},
        {"stage": "2_gap_gate", "enter": n_lemma_occ, "leave": tracer.n_gap_true,
         "lost": n_lemma_occ - tracer.n_gap_true,
         "why_lost": {"seed_known_word (anchor accumulation only, never a target)":
                      tracer.n_seed_occurrences,
                      "already_terminal_library_item (GROUNDED, or ESCALATED past revivals)":
                      n_terminal_skip,
                      "gap_detector_says_known": tracer.n_gap_false}},
        {"stage": "2b_encoding", "enter": tracer.n_gap_true, "leave": tracer.n_flag_calls,
         "lost": n_zero_ctx_skip,
         "why_lost": {"all_zero_context_vector (SILENT continue, rgl:1076)": n_zero_ctx_skip}},
        {"stage": "2c_trace_appended", "enter": tracer.n_flag_calls, "leave": tracer.n_flag_true,
         "lost": tracer.n_flag_false,
         "why_lost": {"Library.flag refused (terminal, revivals exhausted)": tracer.n_flag_false}},
        {"stage": "3_candidate_pool", "enter": tracer.n_canon_calls,
         "leave": tracer.n_canon_calls - tracer.n_pool_empty - tracer.n_pool_no_scannable
                  - tracer.n_query_zero_norm,
         "lost": tracer.n_pool_empty + tracer.n_pool_no_scannable + tracer.n_query_zero_norm,
         "why_lost": {"anchor_field_empty (SILENT self-return)": tracer.n_pool_empty,
                      "no_scannable_anchor (SILENT self-return)": tracer.n_pool_no_scannable,
                      "query_profile_zero_norm (SILENT self-return)": tracer.n_query_zero_norm}},
        {"stage": "4_selection_threshold", "enter": tracer.n_canon_calls,
         "leave": tracer.n_cleared, "lost": tracer.n_not_cleared,
         "why_lost": {"argmax_cosine_below_PBV_INFORMATIVE_MIN=%.2f (uninformative encounter)"
                      % PBV_INFORMATIVE_MIN: tracer.n_not_cleared}},
        {"stage": "5_consolidation_eligibility",
         "enter": sum(r["n_pending"] for r in tracer.pass_rows),
         "leave": sum(r["n_reaching_schema_gate"] for r in tracer.pass_rows),
         "lost": sum(r["n_under_min_confirm"] + r["n_intervening_wait"] for r in tracer.pass_rows),
         "why_lost": {"under_MIN_CONFIRM=%d exposures" % MIN_CONFIRM:
                      sum(r["n_under_min_confirm"] for r in tracer.pass_rows),
                      "intervening_pass_wait (no patience cost)":
                      sum(r["n_intervening_wait"] for r in tracer.pass_rows)},
         "unit": "ITEM-PASSES (one library item counted once per consolidation pass)"},
        {"stage": "5b_schema_coherence_gate", "enter": tracer.n_schema_calls,
         "leave": tracer.n_schema_ok,
         "lost": tracer.n_schema_none + tracer.n_schema_below,
         "why_lost": {"schema_score_None (too few traces to split; SILENT continue, no patience)":
                      tracer.n_schema_none,
                      "schema_score_below_%.2f" % SCHEMA_THRESH_FULL: tracer.n_schema_below},
         "unit": "ITEM-PASSES"},
        {"stage": "6_admission_gate_PBV", "enter": tracer.n_schema_ok,
         "leave": res["n_meaning_facts"],
         "lost": res["n_refusals"], "why_lost": res["refusal_reasons"],
         "unit": "ITEM-PASSES in, FACTS out"},
        {"stage": "7_store_write", "enter": res["n_meaning_facts"],
         "leave": len(gm_subjects), "lost": res["n_meaning_facts"] - len(gm_subjects),
         "why_lost": {"same-subject displacement (FUNCTIONAL supersede)": superseded,
                      "lower-trust write dropped": dropped}},
    ]

    silent = [
        {"site": "hdlab/reading_grounding_loop.py:1076 process_sentence",
         "behaviour": "all-zero context vector -> `continue`; the occurrence is dropped with no "
                      "counter, no log line and no refusal row",
         "count": n_zero_ctx_skip},
        {"site": "hdlab/reading_grounding_loop.py:657 canonicalize_fast",
         "behaviour": "empty anchor field -> returns (target, 0.0), which the caller reads as "
                      "'uninformative encounter'; an EMPTY POOL and a BELOW-THRESHOLD ARGMAX are "
                      "the same return value",
         "count": tracer.n_pool_empty},
        {"site": "hdlab/reading_grounding_loop.py:663 canonicalize_fast",
         "behaviour": "no scannable anchor (mask all False) -> same indistinguishable self-return",
         "count": tracer.n_pool_no_scannable},
        {"site": "hdlab/reading_grounding_loop.py:668 canonicalize_fast",
         "behaviour": "zero-norm query profile -> same indistinguishable self-return",
         "count": tracer.n_query_zero_norm},
        {"site": "hdlab/grounding_acquisition_loop.py:331 Library._propose",
         "behaviour": "propose_fn returned None -> `return` with NO hypothesis_log entry, so an "
                      "encounter that failed to propose leaves no trace in the audit trail "
                      "(only failed VERIFY is counted, as Hypothesis.n_uninformative)",
         "count": tracer.n_propose_none},
        {"site": "hdlab/grounding_acquisition_loop.py:524 consolidation_pass",
         "behaviour": "schema_score is None -> `continue`, no patience cost, nothing recorded",
         "count": tracer.n_schema_none},
        {"site": "hdlab/grounding_acquisition_loop.py:126 context_vector",
         "behaviour": "window with no content word -> all-zero vector returned as if it were a "
                      "representation (the caller's `np.any` guard is the only thing that "
                      "notices)",
         "count": tracer.n_encode_zero},
        {"site": "hdlab/reading_grounding_loop.py ReadingLoopState.refusals",
         "behaviour": "the refusal ledger is never written to disk by the loop itself; only a "
                      "calling cell that chooses to persist it keeps the per-lemma reasons",
         "count": len(state.refusals)},
    ]

    t = dict(tracer.t)
    total_stage_time = res["elapsed_s"]
    timing = {
        "wall_clock_s": total_stage_time,
        "read_phase_s": round(t.get("read_phase", 0.0), 2),
        "consolidation_phase_s": round(t.get("consolidation_phase", 0.0), 2),
        "inclusive_by_stage_s": {k: round(v, 2) for k, v in sorted(t.items())},
        "note": "INCLUSIVE and NESTED: stage34_select is inside stage6_propose/verify, which is "
                "inside stage2c_flag_incl, which is inside read_phase. key_probe and the "
                "stage-1/2 counters are INSTRUMENTATION OVERHEAD, not live-path cost.",
        "instrumentation_overhead_s": round(t.get("key_probe", 0.0) + t.get("stage5_census", 0.0), 2),
    }

    metrics = {
        "anchor_name": ANCHOR_NAME,
        "run_mode": run_mode,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "note": NOTE,
        "QUALITY_CLAIM": "NONE. This cell counts attrition; it scores nothing.",
        "wire_status": "NOTHING WIRED. hdlab/ is unmodified; all counters are external wrappers.",
        "config": {
            "corpus": "experiments.exp_definitional_grounding_v5.load_corpus_v5(None, "
                      "lineaware=True)",
            "n_sentences": tracer.n_sentences, "n_chunks": res["n_chunks"],
            "CHUNK_SIZE": CHUNK_SIZE, "N_DIM": N_DIM, "ARM_SEED": ARM_SEED,
            "seed_vocabulary_rows": 1000,
            "n_known_seed_lemmas": len(state.known_seed),
            "SCHEMA_THRESH": SCHEMA_THRESH_FULL, "MIN_CONFIRM": MIN_CONFIRM,
            "PATIENCE_MAX": PATIENCE_MAX,
            "PBV_INFORMATIVE_MIN": PBV_INFORMATIVE_MIN,
            "PBV_COMMIT_STRENGTH": PBV_COMMIT_STRENGTH,
            "readout": None, "freeze_episode": False, "encoder": "context_vector_masked (bag)",
            "anchor_pool": None, "definition_map": None, "revive_terminal": True,
        },
        "W1_instrumentation_inert_selftest": "run --mode self-test (asserts tracer ON == tracer "
                                             "OFF on the same slice)",
        "W2_reference_reproduction": w2,
        "ATTRITION_TABLE": stages,
        "stage_detail": {
            "1_input": {
                "n_sentences": tracer.n_sentences,
                "n_sentences_with_zero_content_lemmas": tracer.n_sentences_zero_content,
                "n_whitespace_tokens": tracer.n_raw_ws_tokens,
                "n_content_word_tokens": tracer.n_content_word_tokens,
                "n_content_lemma_occurrences": n_lemma_occ,
                "n_distinct_content_lemmas": len(tracer.lemma_freq),
                "n_distinct_eligible_content_lemmas":
                    sum(1 for l in tracer.lemma_freq if is_eligible_meaning(l)),
            },
            "2_gap": {
                "n_seed_occurrences": tracer.n_seed_occurrences,
                "n_nonseed_occurrences": tracer.n_nonseed_occurrences,
                "n_terminal_skips": n_terminal_skip,
                "n_is_gap_calls": tracer.n_isgap_calls,
                "n_gap_true": tracer.n_gap_true, "n_gap_false": tracer.n_gap_false,
                "n_distinct_seed_lemmas_seen": len(tracer.seed_lemmas_seen),
                "n_distinct_lemmas_called_gap": len(tracer.gap_true_lemmas),
                "n_distinct_lemmas_called_known": len(tracer.gap_false_lemmas),
                "n_encode_calls": tracer.n_encode_calls,
                "n_encode_zero_vectors": tracer.n_encode_zero,
                "n_flag_calls": tracer.n_flag_calls, "n_flag_true": tracer.n_flag_true,
                "n_flag_false": tracer.n_flag_false,
            },
            "3_candidates": {
                "n_readout_calls": tracer.n_canon_calls,
                "calls_by_context": dict(sorted(tracer.n_canon_by_stage.items())),
                "mean_scannable_candidates_per_call":
                    round(tracer.pool_size_sum / tracer.n_canon_calls, 3) if tracer.n_canon_calls else None,
                "min_scannable": tracer.pool_size_min, "max_scannable": tracer.pool_size_max,
                "pool_size_quantiles_sampled_every_97th_call":
                    _quantiles([float(x) for x in tracer.pool_sizes]),
                "n_calls_pool_empty": tracer.n_pool_empty,
                "n_calls_no_scannable_anchor": tracer.n_pool_no_scannable,
                "n_calls_query_zero_norm": tracer.n_query_zero_norm,
                "final_n_anchors": len(state.space.anchors()),
                "final_n_eligible_anchors":
                    sum(1 for a in state.space.anchors() if is_eligible_meaning(a)),
            },
            "4_selection": {
                "n_cleared_threshold": tracer.n_cleared,
                "n_below_threshold_self_return": tracer.n_not_cleared,
                "clear_rate": round(tracer.n_cleared / tracer.n_canon_calls, 6)
                              if tracer.n_canon_calls else None,
                "cleared_by_context": dict(sorted(tracer.cleared_by_stage.items())),
                "argmax_cosine_histogram_all_calls": _hist(tracer.cos_hist),
                "argmax_cosine_quantiles_sampled_every_97th_call": _quantiles(tracer.cos_sample),
                "top_20_winning_anchors": [{"anchor": a, "n_wins": n} for a, n
                                           in tracer.winner_freq.most_common(20)],
                "n_distinct_winning_anchors": len(tracer.winner_freq),
            },
            "5_consolidation": {
                "n_item_passes_pending": sum(r["n_pending"] for r in tracer.pass_rows),
                "n_item_passes_under_min_confirm":
                    sum(r["n_under_min_confirm"] for r in tracer.pass_rows),
                "n_item_passes_intervening_wait":
                    sum(r["n_intervening_wait"] for r in tracer.pass_rows),
                "n_item_passes_reaching_schema_gate":
                    sum(r["n_reaching_schema_gate"] for r in tracer.pass_rows),
                "n_schema_calls": tracer.n_schema_calls,
                "n_schema_none": tracer.n_schema_none,
                "n_schema_below_thresh": tracer.n_schema_below,
                "n_schema_ok": tracer.n_schema_ok,
                "schema_score_quantiles": _quantiles(tracer.schema_sample),
                "consistency_check_schema_calls_equal_eligible_item_passes":
                    tracer.n_schema_calls == sum(r["n_reaching_schema_gate"]
                                                 for r in tracer.pass_rows),
                "consistency_check_schema_ok_equals_refusals_plus_facts":
                    tracer.n_schema_ok == res["n_refusals"] + res["n_meaning_facts"],
                "refusal_reasons": res["refusal_reasons"],
                "item_terminal_fate": dict(sorted(fate.items())),
                "exposures_per_item": _quantiles([float(x) for x in exposures]),
            },
            "6_pbv": {
                "n_propose_calls": tracer.n_propose_calls,
                "n_propose_returned_none_SILENT": tracer.n_propose_none,
                "n_propose_returned_candidate": tracer.n_propose_some,
                "n_verify_calls": tracer.n_verify_calls,
                "n_verify_uninformative": tracer.n_verify_none,
                "n_verify_confirm": tracer.n_verify_true,
                "n_verify_disconfirm": tracer.n_verify_false,
                "trajectory": res["trajectory"],
                "final_hypothesis_strength_quantiles": _quantiles(hyp_strength),
                "n_items_holding_a_final_hypothesis": len(hyp_strength),
                "n_items_final_hypothesis_at_or_above_commit":
                    sum(1 for s in hyp_strength if s >= PBV_COMMIT_STRENGTH),
            },
            "7_store": {
                "n_meaning_facts": res["n_meaning_facts"],
                "n_distinct_subjects": len(gm_subjects),
                "n_tautologies": sum(1 for s, o in banked.items() if s == o),
                "n_closed_class_objects": sum(1 for o in banked.values() if is_closed_class(o)),
                "store_resolutions": dict(sorted(tracer.store_resolutions.items())),
                "writes_by_relation": dict(sorted(tracer.store_writes_by_relation.items())),
                "n_subject_relation_pairs_written_more_than_once": len(repeat_writes),
                "n_subject_relation_pairs_with_CONFLICTING_objects": len(multi),
                "conflicting_examples": dict(list(multi.items())[:20]),
                "n_meaning_facts_superseded": superseded,
                "n_meaning_facts_dropped": dropped,
                "displacement_verdict":
                    "NO DISPLACEMENT: every GROUNDED_MEANING subject was written exactly once"
                    if not multi and superseded == 0 else
                    "DISPLACEMENT OBSERVED -- see conflicting_examples",
                "object_concentration_top10":
                    [{"object": o, "n": n} for o, n in Counter(banked.values()).most_common(10)],
            },
        },
        "WHERE_THE_CORRECT_ANSWER_IS_LOST": key_outcome(tracer, res, key),
        "SILENT_EMPTY_RETURNS": silent,
        "TIMING": timing,
        "LIMITATIONS": [
            "This is a CENSUS. No fact is scored for correctness anywhere in this cell.",
            "The known-answer key is the v5 definitional extraction, itself ~64% correct, so the "
            "ABSENT / PRESENT_NOT_ARGMAX split is structural: 'the key's object was not on the "
            "menu' does not mean 'no correct answer was on the menu'.",
            "Stage-5 counts are ITEM-PASSES, not distinct items: one library item is counted once "
            "per consolidation pass it is pending for, which is how consolidation_pass itself "
            "works. Distinct-item outcomes are in stage_detail.5_consolidation.item_terminal_fate.",
            "Timing is INCLUSIVE and nested; the per-stage seconds do not sum to wall clock.",
            "The stage-2 split between 'terminal skip' and 'gap-detector says known' is derived "
            "arithmetically (non-seed occurrences minus is_gap calls); it is exact given that "
            "process_sentence's only other exit before is_gap is the terminal-status check.",
            "One configuration only: the shipped default. F1/F3, the structural encoder, the "
            "anchor pool and the definitional wire are all OFF, as they are in production.",
        ],
    }
    _atomic_json(os.path.join(output_dir, "key_subject_rows.json"),
                 metrics["WHERE_THE_CORRECT_ANSWER_IS_LOST"].pop("rows"))
    _atomic_json(os.path.join(output_dir, "pass_rows.json"), tracer.pass_rows)
    _atomic_json(os.path.join(output_dir, "banked_facts.json"), banked)
    return metrics


# ============================================================================== main
def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=("full", "smoke", "self-test"), default="full")
    args = ap.parse_args()

    output_dir = _output_dir(args.mode)
    os.makedirs(output_dir, exist_ok=True)
    _write_start_marker(output_dir, args.mode)
    with open(os.path.join(output_dir, "_run_pid.txt"), "w", encoding="utf-8") as f:
        f.write(str(os.getpid()))

    if args.mode == "self-test":
        r = selftest(output_dir)
        _atomic_json(os.path.join(output_dir, "selftest.json"), r)
        print(json.dumps(r, indent=2), flush=True)
        return

    try:
        t_all = time.time()
        stream = build_stream(args.mode)
        print("[setup] corpus sentences=%d" % len(stream), flush=True)

        # the key needs the corpus lemma inventory and the seed set, both cheap to precompute
        probe_state = new_state()
        known_seed = set(probe_state.known_seed)
        corpus_lemmas = set()
        for _seg, sent in stream:
            corpus_lemmas.update(RGL.content_lemmas(sent))
        key = load_key(corpus_lemmas, known_seed)
        print("[setup] known-answer key subjects=%d  corpus lemmas=%d"
              % (len(key), len(corpus_lemmas)), flush=True)
        del probe_state

        tracer = Tracer()
        res = run_pass(stream, output_dir, tracer, key, progress=True)
        metrics = assemble(tracer, res, key, args.mode, output_dir)
        metrics["TIMING"]["total_including_setup_s"] = round(time.time() - t_all, 2)
        _atomic_json(os.path.join(output_dir, "metrics.json"), metrics)
        print(json.dumps({"W2_matches_reference": metrics["W2_reference_reproduction"]["matches"],
                          "n_facts": res["n_meaning_facts"],
                          "digest16": res["pairs_digest"][:16],
                          "elapsed_s": res["elapsed_s"],
                          "buckets": metrics["WHERE_THE_CORRECT_ANSWER_IS_LOST"]["buckets"]},
                         indent=2), flush=True)
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        with open(os.path.join(output_dir, "_crash.txt"), "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise


if __name__ == "__main__":
    main()
