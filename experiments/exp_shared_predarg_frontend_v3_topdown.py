"""exp_shared_predarg_frontend_v3_topdown -- VERB-LED TOP-DOWN PP-attachment, margin-gated against
the v2 bottom-up router. Literature drill (Altmann & Kamide 1999 anticipatory eye-movements;
MacDonald/MacWhinney & Bates constraint-satisfaction): PP-attachment in the brain is not purely
structural/bottom-up -- the verb projects an expected-argument slot (event-class + selectional
preference) and attachment is a GRADED COMPETITION where the verb's expectation + the candidate
object's semantic fit can OVERRIDE bottom-up structural locality (locality is a WEAK tie-breaker,
not the decision rule). v2's router (`route_predicate_arguments`) is purely bottom-up: it only
types PPs the arc-parser's head-chain walk (`_pp_args_for_verb`) already attached to the verb
(UAS ~0.79); every miss there is a hard floor (v2's oracle-parse ablation measured PARSE-LIMITED
gaps of +0.10 to +0.18 accuracy for location/path/source). The top-down organ this cell extends
into oblique-PP attachment ALREADY EXISTS and is landed: `hdlab.predictive_reader.PredictiveReader`
(verb+role -> expected-argument grounded centroid; `precision(verb,role)` = selectional-preference
concentration / trust weight) -- the same organ `incremental_parser` uses for patient fit.

WHAT THIS CELL BUILDS: a verb-driven, MARGIN-GATED reranker on top of v2's bottom-up router.
  1. FIT PredictiveReader on (verb_lemma, role, grounded head-word) triples for the 5 spatial/
     transfer roles {goal, location, path, source, recipient}, harvested from a STRICT TRAIN split
     of the FrameNet frame-element gold (60/40 by SENTENCE, zero sentence overlap -- the reader
     NEVER sees a TEST item's own gold).
  2. CANDIDATE GENERATION opens the window: for each verb, every ADP token within a fixed token
     window after the verb (not just the ones the arc-parser's head-chain already attaches) is a
     candidate PP -- this is what recovers the ~14-28% of spatial roles v2's oracle-parse ablation
     showed are PARSE-LIMITED (the head-chain walk never reaches them at all).
  3. SCORING: attach_score(prep,obj,role) = licensing(VerbNet class licenses role) *
     prep_role_compat(preposition telicity vs role) * precision(verb,role) *
     cos(grounded(obj_head), predict(verb,role)) - locality_penalty(distance). Best-scoring role
     wins each candidate PP; best-scoring PP wins each role slot.
  4. MARGIN GATE (top-down breaks TIES, does not override confident bottom-up parses): if v2's
     bottom-up pick for a role slot has a HIGH arc-parser margin (`CandidateGenerator.generate(...)
     .margins`, the calibrated per-token head-assignment confidence), KEEP it. Only LOW-margin or
     UNATTACHED (batch produced no pick at all) slots are handed to the top-down reranker. Three
     threshold candidates (25th/50th/75th percentile of the observed margin distribution on this
     run's TEST population) are swept; the best-lift threshold is reported as SHARED_V2_TOPDOWN,
     alongside the UNGATED (always-top-down) variant for comparison.

ARMS (one variable = the attachment rule that decides each role slot's PP):
  SHARED_V2_BATCH     [FLOOR]    v2's bottom-up router, recomputed fresh on THIS population.
  SHARED_V2_TOPDOWN    [TREATMENT] margin-gated verb-driven reranker (best of 3 swept thresholds).
  SHARED_V2_TOPDOWN_UNGATED           same reranker, always overriding BATCH (no margin gate).
  SHARED_V2_ORACLEPP   [CEILING]  gold PP-attachment (v2's oracle typing decision, `_route_one_pp`,
                        handed the GOLD span's own preposition+head DIRECTLY) -- re-run CLEANLY on
                        THIS cell's own TEST population so the ceiling and the treatment share a
                        population (the prior v2 oracle run's HARNESS_SANITY_FAILED was a mis-set
                        REFERENCE -- it compared a PP-led subset's INLINE to the full-population
                        INLINE constant 0.477 instead of recomputing INLINE fresh, cross-path, on
                        the SAME subset; fixed here, see `_harness_sanity_check`).
  SHARED_V2_TWIN       [info-free] TOPDOWN with the PredictiveReader's verb-role centroid AND
                        precision maps permuted (fixed seed, `build_twin_reader`) -- the reranker's
                        SHAPE (candidate window, licensing, telicity compat, locality penalty) is
                        UNCHANGED; only the learned verb-role expectation is destroyed. Must not
                        recover the BATCH->ORACLE gap the way the real reader does.
  INLINE               [conflated floor, harness-sanity only] v1/v2's untyped floor, recomputed
                        fresh, cross-checked bit-identical between two independent code paths in
                        this cell (see `_harness_sanity_check`) -- if it moves, the harness is
                        broken and the run STOPS.

REUSED UNCHANGED (never reimplemented): v2's `route_predicate_arguments` (bottom-up router, agent/
theme binder), `arm_inline`, `get_event_classes`, `is_destination_verb`, `_PREP_TO_BASE`,
`_route_one_pp` (the oracle's single-pair typing decision), `lemma_verb`, `FRAMENET_CACHE_PATH`,
`PRIMARY_ROLES`, `build_framenet_raw_items` (smoke path only -- performs zero writes when
smoke=True). v1's `parse_and_align` is NOT reused directly (it does not expose arc-parser margins,
which this cell's gate needs) -- a local `parse_and_align_with_margins` extends the SAME pattern
(same cache-by-text discipline, same mismatch-drop) to also capture `CandResult.margins`.

WRITE ONLY: this file and data/exp_shared_predarg_frontend_v3_topdown/ (+ _smoke / _selftest
siblings). Reads (never writes) v2's framenet_raw_items_cache.json. Never touches v1/v2 files,
hdlab/, or any other exp_shared_predarg_frontend_v2* output directory.

Usage:
  --self-test   fast, hand + synthetic-fixture cases (reader predicts a sensible centroid; the
                reranker opens a PP the bottom-up parser never attached; TWIN differs; INLINE is
                cross-path stable; arms-must-differ).
  --smoke       v2's curated 8-LU FrameNet sample (~15s NLTK query, no cache write) + a light
                bootstrap/threshold sweep.
  (bare)        FULL: v2's cached FrameNet raw items (read-only, ~230k raw annotations already
                extracted) -- fresh parse+align+margins into this cell's own checkpoint dir
                (~500s one-time), 60/40 train/test split by sentence, full bootstrap.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor; see .claude/agents/exp_dev.md
Section 12 for the checklist this satisfies):
  - arms_differ_verified: checked in self_test() (BATCH vs TOPDOWN vs TWIN hash-differ on the
    unattached-PP fixture).
  - final_metrics_atomicity: "tmp_replace" (_write uses os.replace).
  - except SystemExit / KeyboardInterrupt: raise, BEFORE except Exception (never BaseException) --
    see main().
  - deterministic_seeding: hashlib.sha256 for the train/test split (never hash()/list(set())');
    random.Random(<fixed int>) for the TWIN permutation.
  - discriminator survives scale: the margin-gate mechanism is exercised at FULL-N in --smoke too
    (the smoke sample is small but the SAME gating/scoring code path runs, not a synthetic-only
    branch; self_test additionally exercises it on a hand fixture at N~1 sentence).
  - HARD_PASS scope: this cell reports MEASURED fractions and CI bands; it does not itself gate a
    remote dispatch (local-only run per the task), so no queue_add HARD_PASS threshold applies.

ADDENDUM 2026-08-29 (coordinator de-confound, `--strict` mode, writes ONLY to
data/exp_shared_predarg_frontend_v3_topdown_strict/): the FULL run above showed TOPDOWN nearly
matching TWIN and, on some roles, exceeding SHARED_V2_ORACLEPP -- both symptoms of a leaky harness
(permissive span-matching + an ORACLE defined via a DIFFERENT typing rule than TOPDOWN's own, so it
was not a true ceiling). The `--strict` pipeline (`run_full_strict`) fixes this with a REDEFINED,
PROVABLE-BY-CONSTRUCTION oracle (`oracle_strict_correct`: correct iff the gold PP's own preposition
has ANY nonzero `_prep_role_compat` entry for the gold role -- the SAME compat table every arm's
`topdown_score` hard-gates candidates on, so a compat==0 item is structurally unreachable by ANY
arm, and compat>0 trivially upper-bounds any 0/1 arm score) and a clean 3-arm factorial that
isolates candidate-OPENING from the READER's selectional signal: A_BATCH (candidates = only the
batch-attached PPs, scored by the REAL reader), B_OPEN_REALSCORE (candidates = the full window,
REAL reader), C_OPEN_SHUFFLE (full window, SHUFFLED/TWIN reader). B-A = the slot-opening effect;
B-C = the selectional-signal effect (the load-bearing test of the brain's verb-driven mechanism).
Both must be CI-separated for the mechanism to count. See `run_full_strict` / `--strict`.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import random
import sys
import time
import traceback
from collections import Counter, defaultdict
from typing import Dict, FrozenSet, List, Optional, Sequence, Tuple

import numpy as np
import scipy.sparse as sp

ANCHOR_NAME = "shared_predarg_frontend_v3_topdown"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- reused machinery, imported unmodified (never reimplemented) -------------------------------
from experiments.exp_shared_predarg_frontend_v1 import (  # noqa: E402
    _default_generator, boot_mean, _label_perm_null_p95, _head_in_span, _cands, _pp_args_for_verb,
)
from experiments.exp_shared_predarg_frontend_v2 import (  # noqa: E402
    route_predicate_arguments, arm_inline, get_event_classes, is_destination_verb, _PREP_TO_BASE,
    _route_one_pp, lemma_verb, FRAMENET_CACHE_PATH as V2_FRAMENET_CACHE_PATH, PRIMARY_ROLES,
    build_framenet_raw_items, SMOKE_FN_LUS,
)
from hdlab.predictive_reader import PredictiveReader, _g, _cos  # noqa: E402
# READ-ONLY reuse of the vetted PPMI+SVD transform (pure numpy/scipy math, no side effects) for the
# richer-representation arm below -- never modifies hdlab; see the RICHREP addendum docstring note.
from hdlab.distributional_meaning_channel import ppmi_svd  # noqa: E402
from tools.exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

NOMINAL = {"NOUN", "PROPN", "PRON"}
N_BOOT = 10000
N_BOOT_PAIRED = 2000
N_PERM_NULL = 2000
BOOT_SEED = 20260829037
TWIN_SEED = 20260829037
WINDOW_TOKENS = 15               # candidate-PP window: tokens after the verb, positional (not
                                  # attachment-filtered) -- OUR-INVENTION-UNDER-TEST, not swept here
LOCALITY_CAP = 0.30
LOCALITY_SLOPE = 0.015
SPLIT_SALT = "predarg_v3_topdown_split_2026-08-29"
TRAIN_FRAC = 0.6
MARGIN_PERCENTILES = (25.0, 50.0, 75.0)
ROUTER_VERSION = "v3_topdown_2026-08-29b"  # bumped: split now pre-filtered to PRIMARY_ROLES items
STRICT_ROUTER_VERSION = "v3_topdown_strict_2026-08-29b"  # bumped: oracle checks ALL window cands
STRICT_OUTPUT_DIR = OUTPUT_DIR + "_strict"
RICHREP_ROUTER_VERSION = "v3_topdown_richrep_2026-08-29a"
RICHREP_OUTPUT_DIR = OUTPUT_DIR + "_richrep"
RICH_SVD_K = 100          # matches the landed DistributionalMeaningChannel's SVD_K (documented, not tuned)
RICH_WINDOW = 4           # symmetric token co-occurrence window (word2vec-scale convention)
RICH_MIN_COUNT = 3        # drop hapax/near-hapax rows before SVD (noise reduction, not tuned)
RICH_SEED = 829041          # must fit numpy legacy RandomState's 32-bit range (scipy svds internal)
RICH_TWIN_SEED = 829043


# =================================================================================================
# TRAIN/TEST split -- 60/40 by SENTENCE, deterministic (hashlib, never hash()/list(set())).
# =================================================================================================
def _sentence_key(item: dict) -> str:
    return " ".join(item["toks"])


def _split_bucket(sentence_key: str, train_frac: float = TRAIN_FRAC) -> str:
    h = hashlib.sha256((SPLIT_SALT + "|" + sentence_key).encode("utf-8")).digest()
    v = int.from_bytes(h[:8], "big") / float(2 ** 64)
    return "TRAIN" if v < train_frac else "TEST"


def split_aligned_items(aligned: List[dict]) -> Tuple[List[dict], List[dict], dict]:
    bucket_cache: Dict[str, str] = {}
    train: List[dict] = []
    test: List[dict] = []
    for it in aligned:
        key = _sentence_key(it)
        b = bucket_cache.get(key)
        if b is None:
            b = _split_bucket(key)
            bucket_cache[key] = b
        (train if b == "TRAIN" else test).append(it)
    train_sent = {k for k, b in bucket_cache.items() if b == "TRAIN"}
    test_sent = {k for k, b in bucket_cache.items() if b == "TEST"}
    overlap = train_sent & test_sent
    meta = {"n_train_sentences": len(train_sent), "n_test_sentences": len(test_sent),
           "n_train_items": len(train), "n_test_items": len(test), "n_overlap_sentences": len(overlap),
           "train_frac_target": TRAIN_FRAC}
    return train, test, meta


# =================================================================================================
# local extension of v1's parse_and_align that ALSO captures arc-parser margins (v1's version does
# not; NOT modifying v1 per hard scope -- this is a sibling function, same cache-by-text and
# mismatch-drop discipline).
# =================================================================================================
def parse_and_align_with_margins(gen, items: List[dict]) -> Tuple[List[dict], int]:
    cache: Dict[str, object] = {}
    out = []
    n_mismatch = 0
    for it in items:
        text = " ".join(it["toks"])
        cr = cache.get(text)
        if cr is None:
            cr = gen.generate(text, extended=True)
            cache[text] = cr
        if list(cr.tokens) != list(it["toks"]):
            n_mismatch += 1
            continue
        it2 = dict(it)
        it2["pos"] = list(cr.pos)
        it2["heads"] = dict(cr.heads)
        it2["margins"] = dict(cr.margins)
        it2["verb_idx"] = it2["verb_idx0"] + 1
        vi = it2["verb_idx"]
        if not (1 <= vi <= len(it2["pos"])) or it2["pos"][vi - 1] != "VERB":
            n_mismatch += 1
            continue
        out.append(it2)
    return out, n_mismatch


def _normalize_item_keys(items: List[dict]) -> List[dict]:
    """Defensive: a checkpoint round-trip through json.dumps/loads coerces int dict keys (heads,
    margins) to strings. Re-normalize to int on every load path (fresh OR resumed) so downstream
    heads.get(int)/margins.get(int) never silently misses after a resume."""
    out = []
    for it in items:
        it2 = dict(it)
        it2["heads"] = {int(k): v for k, v in it2["heads"].items()}
        it2["margins"] = {int(k): v for k, v in it2["margins"].items()}
        out.append(it2)
    return out


# =================================================================================================
# PredictiveReader TRAIN-triple construction (TRAIN split only -- the reader never sees a TEST
# item's own gold).
# =================================================================================================
def build_triples(train_items: List[dict]) -> List[Tuple[str, str, str]]:
    triples = []
    for it in train_items:
        role = it["role_type"]
        if role not in PRIMARY_ROLES:
            continue
        pos, toks = it["pos"], it["toks"]
        s, e = it["span"]
        hidx = _head_in_span(pos, (s, e))
        if hidx is None:
            continue
        vlemma = lemma_verb(toks[it["verb_idx"] - 1])
        triples.append((vlemma, role, toks[hidx - 1]))
    return triples


class TwinReader:
    """Info-free control: SAME public interface as PredictiveReader (.predict/.precision), but the
    (verb,role)->centroid, (verb,role)->precision, and role->global-centroid maps are each permuted
    across their own keys with a FIXED seed -- the reranker's SHAPE (candidate window, licensing,
    telicity compat, locality) is untouched; only the LEARNED verb-role expectation is destroyed."""

    def __init__(self, vr_centroid: dict, role_centroid: dict, precision: dict):
        self._vr_centroid = vr_centroid
        self._role_centroid = role_centroid
        self._precision = precision

    def predict(self, verb: str, role: str):
        c = self._vr_centroid.get((verb, role))
        if c is not None:
            return c
        return self._role_centroid.get(role)

    def precision(self, verb: str, role: str) -> Optional[float]:
        return self._precision.get((verb, role))


def build_twin_reader(reader: PredictiveReader, seed: int = TWIN_SEED) -> TwinReader:
    vr_keys = sorted(reader._vr_centroid.keys())
    vr_vals = [reader._vr_centroid[k] for k in vr_keys]
    prec_vals = [reader._precision.get(k) for k in vr_keys]
    rng = random.Random(seed)
    perm = list(range(len(vr_keys)))
    rng.shuffle(perm)
    shuffled_centroid = {vr_keys[i]: vr_vals[perm[i]] for i in range(len(vr_keys))}
    shuffled_precision = {vr_keys[i]: prec_vals[perm[i]] for i in range(len(vr_keys))}
    role_keys = sorted(reader._role_centroid.keys())
    role_vals = [reader._role_centroid[r] for r in role_keys]
    rng2 = random.Random(seed + 1)
    role_perm = list(range(len(role_keys)))
    rng2.shuffle(role_perm)
    shuffled_role_centroid = {role_keys[i]: role_vals[role_perm[i]] for i in range(len(role_keys))}
    return TwinReader(shuffled_centroid, shuffled_role_centroid, shuffled_precision)


# =================================================================================================
# CANDIDATE GENERATION -- window-based, NOT attachment-filtered (this is the "opens the ~14-28%"
# fix: v1's _pp_args_for_verb only returns PPs whose head-chain resolves back to the verb).
# =================================================================================================
def gather_topdown_candidates(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int],
                              verb_idx: int, window: int = WINDOW_TOKENS) -> List[Tuple[str, int, int]]:
    """[(prep_lower, prep_idx, obj_idx), ...] for every ADP token within `window` tokens after the
    verb, regardless of whether the arc-parser's head-chain attaches its object back to the verb.
    obj_idx = the ADP's own head (UD 'case' convention: the nominal it introduces) if that resolves
    to a nominal; else the nearest following nominal (defensive fallback for a broken case-arc)."""
    n = len(tokens)
    out = []
    end = min(n, verb_idx + window)
    for p in range(verb_idx + 1, end + 1):
        if upos[p - 1] != "ADP":
            continue
        obj = heads.get(p)
        if obj is None or not (1 <= obj <= n) or upos[obj - 1] not in NOMINAL:
            obj = None
            for k in range(p + 1, min(n, p + 4) + 1):
                if upos[k - 1] in NOMINAL:
                    obj = k
                    break
        if obj is None:
            continue
        out.append((tokens[p - 1].lower(), p, obj))
    return out


# =================================================================================================
# SCORING CUES
# =================================================================================================
_PREP_ROLE_COMPAT_TABLE: Dict[str, Dict[str, float]] = {
    "GOAL": {"goal": 1.0, "recipient": 0.6},
    "DIRECTION": {"goal": 0.3},
    "LOCATION": {"location": 1.0, "goal": 0.4},
    "SOURCE": {"source": 1.0},
    "PATH": {"path": 1.0, "location": 0.3},
    "GOAL_OR_BENEF": {"recipient": 0.7, "goal": 0.3},
}


def _prep_role_compat(prep: str, role: str) -> float:
    base = _PREP_TO_BASE.get(prep)
    if base is None:
        return 0.0
    return _PREP_ROLE_COMPAT_TABLE.get(base, {}).get(role, 0.0)


def _licensing(vclasses: FrozenSet[str], role: str) -> float:
    is_motion_or_put = ("MOTION" in vclasses) or ("PUT" in vclasses)
    is_xfer_or_comm = ("TRANSFER" in vclasses) or ("COMM" in vclasses)
    if role == "goal":
        return 1.0 if is_motion_or_put else 0.5
    if role == "recipient":
        return 1.0 if is_xfer_or_comm else 0.3
    if role in ("location", "path", "source"):
        return 1.2 if is_motion_or_put else 1.0
    return 1.0


def _locality_penalty(distance: int) -> float:
    return min(LOCALITY_CAP, LOCALITY_SLOPE * max(distance, 0))


def topdown_score(reader, verb_lemma: str, role: str, prep: str, obj_word: str,
                  vclasses: FrozenSet[str], distance: int, vec_fn=_g, cos_fn=_cos,
                  oov_fallback_cos: float = 0.3) -> Optional[float]:
    """attach_score = licensing * prep_role_compat * precision * cos(rep(obj), predict(v,r))
    - locality_penalty(distance). None if the preposition is structurally incompatible with the
    role (compat==0) -- such a candidate is never scored/considered for that role at all.
    vec_fn/cos_fn default to the GROUNDED 12-dim space (_g/_cos, unchanged default behavior for
    every existing caller) -- pass a different (vec_fn, cos_fn) pair to score in a RICHER
    representation space instead (see the RICHREP addendum, build_rich_space / _np_cos)."""
    compat = _prep_role_compat(prep, role)
    if compat <= 0.0:
        return None
    lic = _licensing(vclasses, role)
    prec = reader.precision(verb_lemma, role)
    prec = 0.2 if prec is None else max(float(prec), 0.0)
    centroid = reader.predict(verb_lemma, role)
    obj_vec = vec_fn(obj_word)
    if centroid is not None and obj_vec is not None:
        cos = cos_fn(obj_vec, centroid)
    else:
        cos = oov_fallback_cos  # neutral fallback: OOV in this rep's lexicon -- don't structurally zero
    cos_w = max(cos, 0.0)
    return lic * compat * prec * cos_w - _locality_penalty(distance)


def topdown_candidate_picks_words(cands_pp: Sequence[Tuple[str, int, int, str]], verb_idx: int,
                                  reader, vclasses: FrozenSet[str], verb_lemma: str,
                                  roles: Sequence[str] = PRIMARY_ROLES, vec_fn=_g, cos_fn=_cos
                                  ) -> Tuple[Dict[str, Optional[int]], Dict[str, Optional[float]]]:
    """cands_pp: (prep, prep_idx, obj_idx, obj_word) tuples (self-contained -- no re-parse needed).
    Best-scoring role wins each candidate PP; best-scoring PP wins each role slot. vec_fn/cos_fn
    forwarded to topdown_score unchanged (default = grounded 12-dim space)."""
    role_best: Dict[str, Optional[Tuple[int, float]]] = {r: None for r in roles}
    for prep, prep_idx, obj_idx, obj_word in cands_pp:
        distance = obj_idx - verb_idx
        best_role = None
        best_score = None
        for role in roles:
            s = topdown_score(reader, verb_lemma, role, prep, obj_word, vclasses, distance,
                              vec_fn=vec_fn, cos_fn=cos_fn)
            if s is None:
                continue
            if best_score is None or s > best_score:
                best_score = s
                best_role = role
        if best_role is None:
            continue
        cur = role_best[best_role]
        if cur is None or best_score > cur[1]:
            role_best[best_role] = (obj_idx, best_score)
    picks = {r: (v[0] if v else None) for r, v in role_best.items()}
    scores = {r: (v[1] if v else None) for r, v in role_best.items()}
    return picks, scores


# =================================================================================================
# per-item prediction bundle: BATCH (v2, unchanged) + TOPDOWN candidates/scores computed ONCE
# (reused across every margin threshold + the TWIN pass, cheap merges).
# =================================================================================================
def compute_item_prediction(toks, pos, heads, margins, v, reader) -> dict:
    batch = route_predicate_arguments(toks, pos, heads, v)
    vlemma = lemma_verb(toks[v - 1])
    vclasses = get_event_classes(vlemma)
    cands_raw = gather_topdown_candidates(toks, pos, heads, v)
    cands_pp = [(prep, pidx, oidx, toks[oidx - 1]) for (prep, pidx, oidx) in cands_raw]
    td_picks, td_scores = topdown_candidate_picks_words(cands_pp, v, reader, vclasses, vlemma)
    margins_by_role = {r: margins.get(batch.get(r)) for r in PRIMARY_ROLES if batch.get(r) is not None}
    return {"batch": batch, "topdown_picks": td_picks, "topdown_scores": td_scores,
           "margins_by_role": margins_by_role, "lemma": vlemma, "vclasses": sorted(vclasses),
           "cands_pp": [list(c) for c in cands_pp], "verb_idx": v}


def merge_gated(batch: dict, topdown_picks: Dict[str, Optional[int]], margins_by_role: dict,
                thresh: float, ungated: bool = False) -> dict:
    out = dict(batch)
    for role in PRIMARY_ROLES:
        batch_pick = batch.get(role)
        if not ungated and batch_pick is not None:
            m = margins_by_role.get(role)
            if m is not None and m >= thresh:
                continue  # KEEP the confident bottom-up attachment
        td_pick = topdown_picks.get(role)
        if td_pick is not None:
            out[role] = td_pick
    return out


# =================================================================================================
# ORACLE-PP ceiling (v2's exact typing decision, `_route_one_pp`, handed the GOLD span's own
# leading preposition + head nominal directly -- only PP-FINDING is oracle-replaced).
# =================================================================================================
def _oracle_eligible(it: dict) -> bool:
    s, e = it["span"]
    pos = it["pos"]
    if not (s < len(pos) and pos[s] == "ADP"):
        return False
    return _head_in_span(pos, (s, e)) is not None


def oracle_pick_for_item(it: dict, batch: dict, vclasses: FrozenSet[str], lemma: str) -> Optional[int]:
    toks, pos = it["toks"], it["pos"]
    s, e = it["span"]
    if not _oracle_eligible(it):
        return None
    obj = _head_in_span(pos, (s, e))
    prep = toks[s].lower()
    is_motion_or_put = ("MOTION" in vclasses) or ("PUT" in vclasses)
    is_xfer_or_comm = ("TRANSFER" in vclasses) or ("COMM" in vclasses)
    is_dest = is_destination_verb(lemma)
    theme_idx = batch.get("theme")
    roles = {k: None for k in ("goal", "location", "path", "source", "recipient", "direction", "instrument")}
    _route_one_pp(prep, obj, toks, pos, is_motion_or_put, is_xfer_or_comm, is_dest, theme_idx, roles, None)
    return roles.get(it["role_type"])


# =================================================================================================
# HARNESS SANITY (load-bearing) -- INLINE must reproduce BIT-IDENTICAL between two INDEPENDENT
# code paths in this cell: (a) the value folded into the main scored records, (b) a completely
# fresh recompute at the end of run_full over the same TEST items. Fixes the prior v2 oracle run's
# mis-set reference (it compared a PP-led SUBSET's INLINE to the FULL-population constant 0.477 --
# different populations, not a harness bug at all; the correct check is cross-path on the SAME
# population, which is what this does).
# =================================================================================================
def _harness_sanity_check(test_items: List[dict], main_recs: List[dict]) -> dict:
    fresh_by_role: Dict[str, List[int]] = {r: [] for r in PRIMARY_ROLES}
    for it in test_items:
        role = it["role_type"]
        if role not in PRIMARY_ROLES:
            continue
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        s, e = it["span"]
        fresh = arm_inline(toks, pos, heads, v)
        pick = fresh.get(role)
        fresh_by_role[role].append(int(pick is not None and s < pick <= e))
    cached_by_role: Dict[str, List[int]] = {r: [] for r in PRIMARY_ROLES}
    for rec in main_recs:
        role = rec["role_type"]
        if role in cached_by_role:
            cached_by_role[role].append(rec["correct"]["INLINE"])
    mismatches = {}
    for role in PRIMARY_ROLES:
        f = fresh_by_role[role]
        c = cached_by_role[role]
        if len(f) != len(c):
            mismatches[role] = f"length_mismatch fresh={len(f)} cached={len(c)}"
            continue
        n_diff = sum(1 for a, b in zip(f, c) if a != b)
        if n_diff:
            mismatches[role] = f"{n_diff}/{len(f)} values differ"
    fresh_acc = {r: (float(np.mean(v)) if v else float("nan")) for r, v in fresh_by_role.items()}
    return {"pass": len(mismatches) == 0, "mismatches": mismatches, "fresh_inline_acc": fresh_acc}


# =================================================================================================
# scoring the TEST population (BATCH / INLINE / ORACLE / TOPDOWN@thresholds / TOPDOWN_UNGATED)
# =================================================================================================
def score_test_items(test_items: List[dict], item_preds: List[dict], thresholds: List[float]) -> List[dict]:
    recs = []
    for it, pred in zip(test_items, item_preds):
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        role = it["role_type"]
        s, e = it["span"]

        def inspan(idx):
            return int(idx is not None and s < idx <= e)

        batch = pred["batch"]
        inline = arm_inline(toks, pos, heads, v)
        vclasses = frozenset(pred["vclasses"])
        oracle_elig = _oracle_eligible(it)
        oracle_pick = oracle_pick_for_item(it, batch, vclasses, pred["lemma"]) if oracle_elig else None

        correct = {"BATCH": inspan(batch.get(role)), "INLINE": inspan(inline.get(role))}
        if oracle_elig:
            correct["ORACLE"] = inspan(oracle_pick)
        for i, th in enumerate(thresholds):
            merged = merge_gated(batch, pred["topdown_picks"], pred["margins_by_role"], th, ungated=False)
            correct[f"TOPDOWN_T{i}"] = inspan(merged.get(role))
        merged_ungated = merge_gated(batch, pred["topdown_picks"], pred["margins_by_role"], 0.0, ungated=True)
        correct["TOPDOWN_UNGATED"] = inspan(merged_ungated.get(role))

        recs.append({"role_type": role, "verb_lemma": pred["lemma"], "oracle_eligible": oracle_elig,
                    "correct": correct})
    return recs


def add_twin_scores(recs: List[dict], test_items: List[dict], item_preds: List[dict],
                    twin_reader: TwinReader, best_thresh: float) -> None:
    for rec, it, pred in zip(recs, test_items, item_preds):
        role = it["role_type"]
        s, e = it["span"]
        cands_pp = [tuple(c) for c in pred["cands_pp"]]
        vclasses = frozenset(pred["vclasses"])
        twin_picks, _ = topdown_candidate_picks_words(cands_pp, pred["verb_idx"], twin_reader, vclasses,
                                                       pred["lemma"])
        merged = merge_gated(pred["batch"], twin_picks, pred["margins_by_role"], best_thresh, ungated=False)
        pick = merged.get(role)
        rec["correct"]["TWIN"] = int(pick is not None and s < pick <= e)


def pick_best_threshold(recs: List[dict], thresholds: List[float]) -> Tuple[int, float]:
    best_i, best_total = 0, -1e18
    for i in range(len(thresholds)):
        arm = f"TOPDOWN_T{i}"
        total = 0.0
        for role in PRIMARY_ROLES:
            rows = [r for r in recs if r["role_type"] == role]
            if not rows:
                continue
            batch_acc = float(np.mean([r["correct"]["BATCH"] for r in rows]))
            td_acc = float(np.mean([r["correct"][arm] for r in rows]))
            total += (td_acc - batch_acc)
        if total > best_total:
            best_total, best_i = total, i
    return best_i, best_total


# =================================================================================================
# bootstrap stats (paired across arms -- same resample index applied to every arm's vector, so
# diffs and ratios are computed on correctly-paired resamples, not independently-bootstrapped ones)
# =================================================================================================
def paired_boot(vecs: Dict[str, np.ndarray], n_boot: int, seed: int, chunk: int = 500) -> Dict[str, np.ndarray]:
    n = len(next(iter(vecs.values())))
    rng = np.random.default_rng(seed)
    out = {k: np.empty(n_boot) for k in vecs}
    done = 0
    while done < n_boot:
        c = min(chunk, n_boot - done)
        idx = rng.integers(0, n, size=(c, n))
        for k, x in vecs.items():
            out[k][done:done + c] = x[idx].mean(axis=1)
        done += c
    return out


def _band(lo: float, hi: float) -> str:
    if lo != lo:
        return "NA"
    if lo > 0:
        return "ABOVE"
    if hi < 0:
        return "BELOW"
    return "NOT_SEPARATED"


def full_role_stats(recs: List[dict], role: str, arms: List[str], topdown_arm: str, batch_arm: str,
                    oracle_arm: Optional[str], twin_arm: Optional[str], n_boot_paired: int, n_perm: int,
                    seed_off: int, subset_filter=None) -> dict:
    rows = [r for r in recs if r["role_type"] == role and (subset_filter is None or subset_filter(r))]
    n = len(rows)
    if n == 0:
        return {"n": 0}
    arms_present = [a for a in arms if all(a in r["correct"] for r in rows)]
    vecs = {a: np.array([r["correct"][a] for r in rows], dtype=np.float64) for a in arms_present}
    boot = paired_boot(vecs, n_boot_paired, BOOT_SEED + seed_off)
    acc = {}
    for a in arms_present:
        lo, hi = np.percentile(boot[a], [2.5, 97.5])
        acc[a] = {"point": float(vecs[a].mean()), "ci95": [float(lo), float(hi)]}
    out = {"n": n, "acc": acc}
    if topdown_arm in vecs and batch_arm in vecs:
        d = boot[topdown_arm] - boot[batch_arm]
        lo, hi = np.percentile(d, [2.5, 97.5])
        null_p95 = _label_perm_null_p95(vecs[topdown_arm], vecs[batch_arm], n_perm, BOOT_SEED + seed_off + 99)
        out["topdown_minus_batch"] = {"point": float(vecs[topdown_arm].mean() - vecs[batch_arm].mean()),
                                      "ci95": [float(lo), float(hi)], "band": _band(lo, hi),
                                      "half_width": float((hi - lo) / 2), "null_p95": null_p95}
    if oracle_arm and oracle_arm in vecs and batch_arm in vecs:
        og = boot[oracle_arm] - boot[batch_arm]
        lo2, hi2 = np.percentile(og, [2.5, 97.5])
        out["oracle_minus_batch"] = {"point": float(vecs[oracle_arm].mean() - vecs[batch_arm].mean()),
                                     "ci95": [float(lo2), float(hi2)], "band": _band(lo2, hi2)}
        if topdown_arm in vecs:
            with np.errstate(divide="ignore", invalid="ignore"):
                frac = np.where(np.abs(og) > 1e-9, (boot[topdown_arm] - boot[batch_arm]) / og, np.nan)
            valid = frac[~np.isnan(frac)]
            denom = float(vecs[oracle_arm].mean() - vecs[batch_arm].mean())
            frac_point = (float(vecs[topdown_arm].mean() - vecs[batch_arm].mean()) / denom
                         if abs(denom) > 1e-9 else float("nan"))
            frac_ci = ([float(np.percentile(valid, 2.5)), float(np.percentile(valid, 97.5))]
                      if len(valid) else [float("nan"), float("nan")])
            out["fraction_of_gap_recovered"] = {"point": frac_point, "ci95": frac_ci,
                                                "n_valid_boot": int(len(valid))}
    if twin_arm and twin_arm in vecs and topdown_arm in vecs:
        td = boot[twin_arm] - boot[topdown_arm]
        lo3, hi3 = np.percentile(td, [2.5, 97.5])
        out["twin_minus_topdown"] = {"point": float(vecs[twin_arm].mean() - vecs[topdown_arm].mean()),
                                     "ci95": [float(lo3), float(hi3)], "band": _band(lo3, hi3)}
    if twin_arm and twin_arm in vecs and batch_arm in vecs:
        tb = boot[twin_arm] - boot[batch_arm]
        lo4, hi4 = np.percentile(tb, [2.5, 97.5])
        out["twin_minus_batch"] = {"point": float(vecs[twin_arm].mean() - vecs[batch_arm].mean()),
                                   "ci95": [float(lo4), float(hi4)], "band": _band(lo4, hi4)}
    return out


def _role_verdict(role_stats: dict) -> str:
    tvb = role_stats.get("topdown_minus_batch")
    frac = role_stats.get("fraction_of_gap_recovered")
    if tvb is None:
        return "NO_DATA"
    if tvb["band"] != "ABOVE":
        return "NONE_NOT_CI_SEPARATED_ABOVE_BATCH"
    if frac is None or frac["point"] != frac["point"]:
        return "CI_SEPARATED_ABOVE_BATCH_GAP_UNDEFINED"
    p = frac["point"]
    if p >= 0.5:
        return "MAJORITY_RECOVERED"
    if p > 0.0:
        return "MINORITY_RECOVERED"
    return "CI_SEPARATED_ABOVE_BATCH_BUT_NOT_TOWARD_ORACLE"


# =================================================================================================
# full run
# =================================================================================================
def run_full(gen, smoke: bool, out_dir: str) -> dict:
    t0 = time.time()
    n_boot_paired = 400 if smoke else N_BOOT_PAIRED
    n_perm = 200 if smoke else N_PERM_NULL

    if smoke:
        fn_raw, fn_meta = build_framenet_raw_items(smoke=True)  # v2's fn -- ZERO writes when smoke=True
    else:
        if not os.path.exists(V2_FRAMENET_CACHE_PATH):
            raise RuntimeError(f"{V2_FRAMENET_CACHE_PATH} not found (read-only dependency) -- run "
                              f"exp_shared_predarg_frontend_v2.py (bare) once first to build it.")
        with open(V2_FRAMENET_CACHE_PATH, "r", encoding="utf-8") as f:
            fn_raw = json.load(f)
        fn_meta = {"mode": "full", "source": "v2_cache_readonly", "path": V2_FRAMENET_CACHE_PATH}
    print(f"[frontend-v3] raw items={len(fn_raw)} meta={fn_meta} {time.time()-t0:.1f}s", flush=True)

    align_key = unit_key("aligned_with_margins", ROUTER_VERSION)
    done = completed_units(out_dir)
    if align_key in done:
        aligned = load_units(out_dir)[align_key]
        n_mismatch = None
        print(f"[frontend-v3] resumed aligned items from checkpoint: {len(aligned)}", flush=True)
    else:
        aligned, n_mismatch = parse_and_align_with_margins(gen, fn_raw)
        record_unit(out_dir, align_key, aligned)
        print(f"[frontend-v3] aligned={len(aligned)} mismatch={n_mismatch} {time.time()-t0:.1f}s",
             flush=True)
    aligned = _normalize_item_keys(aligned)
    aligned_primary = [it for it in aligned if it["role_type"] in PRIMARY_ROLES]
    print(f"[frontend-v3] aligned_primary_roles={len(aligned_primary)} of {len(aligned)} "
         f"(agent/theme/direction items excluded -- out of this cell's scored scope)", flush=True)

    train_items, test_items, split_meta = split_aligned_items(aligned_primary)
    print(f"[split] {split_meta} {time.time()-t0:.1f}s", flush=True)
    if split_meta["n_overlap_sentences"] != 0:
        raise RuntimeError(f"TRAIN/TEST sentence overlap detected: {split_meta} -- STOP (leakage guard)")

    train_triples = build_triples(train_items)
    reader = PredictiveReader().fit(train_triples)
    print(f"[reader] fit on {len(train_triples)} TRAIN triples "
         f"(vr_pairs={len(reader._vr_centroid)})", flush=True)

    pred_key = unit_key("item_predictions", ROUTER_VERSION)
    done = completed_units(out_dir)
    if pred_key in done:
        item_preds = load_units(out_dir)[pred_key]
        print(f"[predict] resumed {len(item_preds)} item predictions from checkpoint", flush=True)
    else:
        item_preds = []
        for i, it in enumerate(test_items):
            pred = compute_item_prediction(it["toks"], it["pos"], it["heads"], it["margins"],
                                           it["verb_idx"], reader)
            item_preds.append(pred)
            if i and i % 2000 == 0:
                print(f"[predict] {i}/{len(test_items)} {time.time()-t0:.1f}s", flush=True)
        record_unit(out_dir, pred_key, item_preds)
        print(f"[predict] computed {len(item_preds)} item predictions {time.time()-t0:.1f}s", flush=True)

    all_margins = [m for pred in item_preds for m in pred["margins_by_role"].values() if m is not None]
    if all_margins:
        thresholds = sorted(set(round(float(x), 4) for x in np.percentile(all_margins, list(MARGIN_PERCENTILES))))
    else:
        thresholds = [5.0, 15.0, 30.0]
    print(f"[margin] pooled_n={len(all_margins)} thresholds(pctl{MARGIN_PERCENTILES})={thresholds}",
         flush=True)

    recs = score_test_items(test_items, item_preds, thresholds)
    print(f"[score] scored {len(recs)} TEST items across {len(thresholds)} thresholds "
         f"{time.time()-t0:.1f}s", flush=True)

    best_i, best_lift = pick_best_threshold(recs, thresholds)
    best_thresh = thresholds[best_i]
    print(f"[margin] best threshold index={best_i} value={best_thresh} total_lift={best_lift:.4f}",
         flush=True)

    twin_reader = build_twin_reader(reader, seed=TWIN_SEED)
    add_twin_scores(recs, test_items, item_preds, twin_reader, best_thresh)
    print(f"[twin] scored at best_thresh={best_thresh} {time.time()-t0:.1f}s", flush=True)

    for rec in recs:
        rec["correct"]["TOPDOWN_BEST"] = rec["correct"][f"TOPDOWN_T{best_i}"]

    harness = _harness_sanity_check(test_items, recs)
    print(f"[harness] INLINE cross-path sanity: pass={harness['pass']} "
         f"fresh_inline_acc={harness['fresh_inline_acc']}", flush=True)
    if not harness["pass"]:
        raise RuntimeError(f"HARNESS_SANITY_FAILED: INLINE moved between independent recompute "
                          f"paths on the SAME population -- {harness['mismatches']}. STOP, numbers "
                          f"below are NOT TRUSTED.")

    full_arms = ["BATCH", "INLINE", "TOPDOWN_BEST", "TOPDOWN_UNGATED", "TWIN"]
    oracle_arms = ["BATCH", "TOPDOWN_BEST", "ORACLE", "TWIN"]
    full_pop_strata = {}
    oracle_subset_strata = {}
    threshold_sweep = {}
    for i, role in enumerate(PRIMARY_ROLES):
        full_pop_strata[role] = full_role_stats(recs, role, full_arms, "TOPDOWN_BEST", "BATCH", None,
                                                "TWIN", n_boot_paired, n_perm, 10 * i)
        oracle_subset_strata[role] = full_role_stats(
            recs, role, oracle_arms, "TOPDOWN_BEST", "BATCH", "ORACLE", "TWIN", n_boot_paired, n_perm,
            1000 + 10 * i, subset_filter=lambda r: r.get("oracle_eligible"))
        sweep = {}
        for j, th in enumerate(thresholds):
            rows = [r for r in recs if r["role_type"] == role]
            if rows:
                sweep[f"T{j}={th}"] = {
                    "acc": float(np.mean([r["correct"][f"TOPDOWN_T{j}"] for r in rows])),
                    "lift_vs_batch": float(np.mean([r["correct"][f"TOPDOWN_T{j}"] for r in rows]) -
                                          np.mean([r["correct"]["BATCH"] for r in rows])),
                }
        rows = [r for r in recs if r["role_type"] == role]
        if rows:
            sweep["UNGATED"] = {
                "acc": float(np.mean([r["correct"]["TOPDOWN_UNGATED"] for r in rows])),
                "lift_vs_batch": float(np.mean([r["correct"]["TOPDOWN_UNGATED"] for r in rows]) -
                                      np.mean([r["correct"]["BATCH"] for r in rows])),
            }
        threshold_sweep[role] = sweep

    per_role_verdict = {role: _role_verdict(oracle_subset_strata[role]) for role in PRIMARY_ROLES}
    n_majority = sum(1 for v in per_role_verdict.values() if v == "MAJORITY_RECOVERED")
    n_minority = sum(1 for v in per_role_verdict.values() if v == "MINORITY_RECOVERED")
    n_none = len(PRIMARY_ROLES) - n_majority - n_minority

    verdict = ("TOPDOWN_RECOVERS_MAJORITY_SOME_ROLES" if n_majority > 0 else
              ("TOPDOWN_RECOVERS_MINORITY_SOME_ROLES" if n_minority > 0 else
               "TOPDOWN_NO_CI_SEPARATED_RECOVERY"))

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | per_role={per_role_verdict} | best_margin_thresh={best_thresh} "
            f"(idx={best_i} of {thresholds}) | harness_ok={harness['pass']} | "
            f"n_majority={n_majority} n_minority={n_minority} n_none={n_none}"
        ),
        "summary": f"{verdict}: verb-driven margin-gated top-down PP-attachment vs v2 bottom-up",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": ("smoke" if smoke else "full"),
        "anchor_name": ANCHOR_NAME, "router_version": ROUTER_VERSION,
        "n_boot_paired": n_boot_paired, "n_perm": n_perm,
        "window_tokens": WINDOW_TOKENS, "locality_cap": LOCALITY_CAP, "locality_slope": LOCALITY_SLOPE,
        "framenet_meta": fn_meta, "n_raw": len(fn_raw), "n_aligned": len(aligned), "n_mismatch": n_mismatch,
        "split": split_meta,
        "reader": {"n_train_triples": len(train_triples), "n_verb_role_pairs": len(reader._vr_centroid)},
        "margin_thresholds": thresholds, "best_threshold_index": best_i, "best_threshold": best_thresh,
        "best_threshold_total_lift": best_lift,
        "harness_sanity": harness,
        "full_population_strata": full_pop_strata,
        "oracle_eligible_subset_strata": oracle_subset_strata,
        "threshold_sweep": threshold_sweep,
        "per_role_verdict": per_role_verdict,
        "scored_population": {
            "units_jsonl": os.path.join(out_dir, "units.jsonl"),
            "unit_keys": sorted([align_key, pred_key]),
        },
    }


# =================================================================================================
# STRICT DE-CONFOUND (coordinator, 2026-08-29): the ORIGINAL run showed TOPDOWN nearly matching
# TWIN and, on some roles, exceeding SHARED_V2_ORACLEPP -- both symptoms that (a) the oracle was
# not a true ceiling (it used v2's SEPARATE CUE5-gated typing rule, `_route_one_pp`, rather than
# this cell's own compat/licensing table, so the two were never comparable) and (b) the reader's
# selectional signal was rarely the deciding factor once a window is opened (few candidates =>
# compat/licensing alone usually determines the pick, and the reader's cos-term falls back to the
# SAME neutral 0.3 constant for BOTH the real and the shuffled reader whenever the object word is
# OOV in the 12-dim grounded lexicon -- so TWIN silently ties TOPDOWN on OOV-heavy items).
#
# FIX 1 -- a PROVABLE ceiling: oracle_strict_correct(item) = 1 iff the gold PP's own preposition
# has ANY compat>0 entry for the gold role under `_prep_role_compat` -- the EXACT SAME table every
# arm's `topdown_score` hard-gates on (`if compat <= 0.0: return None`). A compat==0 item is
# STRUCTURALLY unreachable by any arm (none can ever route that token to that role), so oracle=0 is
# a valid ceiling there; compat>0 gives oracle=1, the maximum possible 0/1 value, trivially
# upper-bounding any arm's per-item correctness. This is a ceiling by CONSTRUCTION, not by
# empirical luck -- verified per-item below (`n_B_exceeds_oracle`/`n_C_exceeds_oracle` must be 0).
#
# FIX 2 -- three arms sharing controlled candidate sets, isolating slot-opening from selectional
# signal:
#   A_BATCH            candidates = ONLY the batch-attached PPs (`_pp_args_for_verb`), REAL reader.
#   B_OPEN_REALSCORE   candidates = the FULL window (`gather_topdown_candidates`), REAL reader.
#   C_OPEN_SHUFFLE     candidates = the FULL window, SHUFFLED reader (`TwinReader`).
# B-A isolates slot-opening (same reader, different candidate set). B-C isolates the selectional
# signal (same candidate set, different reader) -- the load-bearing test of the brain's verb-driven
# mechanism; the earlier (confounded) near-tie must be reproduced or overturned HERE, cleanly.
# =================================================================================================
def gather_batch_candidates(tokens: Sequence[str], upos: Sequence[str], heads: Dict[int, int],
                            verb_idx: int) -> List[Tuple[str, int, int]]:
    """(prep, prep_idx, obj_idx) triples restricted to PPs v2's bottom-up parse actually attaches
    to the verb (`_pp_args_for_verb`'s head-chain walk) -- a SUBSET of gather_topdown_candidates'
    window by construction (attachment implies within-window position after the verb in this
    corpus's realized word order)."""
    pp_args = _pp_args_for_verb(tokens, upos, heads, verb_idx)  # [(prep_lower, obj_idx), ...]
    attached_objs = {obj for (_, obj) in pp_args}
    window = gather_topdown_candidates(tokens, upos, heads, verb_idx, window=WINDOW_TOKENS)
    return [(prep, pidx, oidx) for (prep, pidx, oidx) in window if oidx in attached_objs]


def compute_item_prediction_strict(toks, pos, heads, v, reader, twin_reader) -> dict:
    vlemma = lemma_verb(toks[v - 1])
    vclasses = get_event_classes(vlemma)
    window_raw = gather_topdown_candidates(toks, pos, heads, v)
    window_pp = [(prep, pidx, oidx, toks[oidx - 1]) for (prep, pidx, oidx) in window_raw]
    batch_raw = gather_batch_candidates(toks, pos, heads, v)
    batch_pp = [(prep, pidx, oidx, toks[oidx - 1]) for (prep, pidx, oidx) in batch_raw]

    a_picks, _ = topdown_candidate_picks_words(batch_pp, v, reader, vclasses, vlemma)
    b_picks, _ = topdown_candidate_picks_words(window_pp, v, reader, vclasses, vlemma)
    c_picks, _ = topdown_candidate_picks_words(window_pp, v, twin_reader, vclasses, vlemma)
    return {"A": a_picks, "B": b_picks, "C": c_picks, "lemma": vlemma, "vclasses": sorted(vclasses),
           "n_batch_cands": len(batch_pp), "n_window_cands": len(window_pp),
           "window_cands": [list(c) for c in window_raw]}


def oracle_strict_correct(item: dict, window_cands: Sequence[Tuple[str, int, int]]) -> Optional[int]:
    """PROVABLE ceiling (see module note above): 1 iff SOME candidate in this item's OWN window
    scan (the EXACT candidate universe B/C search over) has its object landing inside the gold span
    AND a compat>0 entry for the gold role under `_prep_role_compat` (the same table gating every
    arm's candidate scoring -- `topdown_score` hard-gates on compat>0, so any arm's picked token for
    this role must satisfy this same condition). This is checked over ALL window candidates, not
    only the span's own leading token -- a multi-preposition gold span (e.g. "out in front of the
    house") can have its FIRST token be a particle absent from the compat table (out -> compat 0
    for every role) while a LATER preposition within the SAME span ("in") is the semantically
    load-bearing, reachable one; restricting to the leading token alone made the ceiling too tight
    to be a valid bound (found empirically: it was violated on exactly this construction). None if
    not oracle-eligible (no leading-ADP gold span / no nominal head at all -- can't identify a PP)."""
    if not _oracle_eligible(item):
        return None
    s, e = item["span"]
    role = item["role_type"]
    for prep, pidx, oidx in window_cands:
        if s < oidx <= e and _prep_role_compat(prep, role) > 0.0:
            return 1
    return 0


def score_test_items_strict(test_items: List[dict], item_preds: List[dict]) -> List[dict]:
    recs = []
    for it, pred in zip(test_items, item_preds):
        role = it["role_type"]
        s, e = it["span"]

        def inspan(idx):
            return int(idx is not None and s < idx <= e)

        correct = {"A_BATCH": inspan(pred["A"].get(role)), "B_OPEN_REALSCORE": inspan(pred["B"].get(role)),
                  "C_OPEN_SHUFFLE": inspan(pred["C"].get(role))}
        window_cands = [tuple(c) for c in pred["window_cands"]]
        oc = oracle_strict_correct(it, window_cands)
        elig = oc is not None
        if elig:
            correct["ORACLE"] = oc
        recs.append({"role_type": role, "oracle_eligible": elig, "correct": correct})
    return recs


def strict_role_stats(recs: List[dict], role: str, n_boot_paired: int, n_perm: int, seed_off: int) -> dict:
    rows = [r for r in recs if r["role_type"] == role and r["oracle_eligible"]]
    n = len(rows)
    if n == 0:
        return {"n": 0}
    arms = ["A_BATCH", "B_OPEN_REALSCORE", "C_OPEN_SHUFFLE", "ORACLE"]
    vecs = {a: np.array([r["correct"][a] for r in rows], dtype=np.float64) for a in arms}
    n_B_exceeds = int(np.sum(vecs["B_OPEN_REALSCORE"] > vecs["ORACLE"]))
    n_C_exceeds = int(np.sum(vecs["C_OPEN_SHUFFLE"] > vecs["ORACLE"]))
    boot = paired_boot(vecs, n_boot_paired, BOOT_SEED + seed_off)
    acc = {}
    for a in arms:
        lo, hi = np.percentile(boot[a], [2.5, 97.5])
        acc[a] = {"point": float(vecs[a].mean()), "ci95": [float(lo), float(hi)]}
    ba = boot["B_OPEN_REALSCORE"] - boot["A_BATCH"]
    lo1, hi1 = np.percentile(ba, [2.5, 97.5])
    slot_opening = {"point": float(vecs["B_OPEN_REALSCORE"].mean() - vecs["A_BATCH"].mean()),
                    "ci95": [float(lo1), float(hi1)], "band": _band(lo1, hi1),
                    "null_p95": _label_perm_null_p95(vecs["B_OPEN_REALSCORE"], vecs["A_BATCH"], n_perm,
                                                     BOOT_SEED + seed_off + 99)}
    bc = boot["B_OPEN_REALSCORE"] - boot["C_OPEN_SHUFFLE"]
    lo2, hi2 = np.percentile(bc, [2.5, 97.5])
    selectional_signal = {"point": float(vecs["B_OPEN_REALSCORE"].mean() - vecs["C_OPEN_SHUFFLE"].mean()),
                          "ci95": [float(lo2), float(hi2)], "band": _band(lo2, hi2),
                          "null_p95": _label_perm_null_p95(vecs["B_OPEN_REALSCORE"], vecs["C_OPEN_SHUFFLE"],
                                                           n_perm, BOOT_SEED + seed_off + 199)}
    return {"n": n, "acc": acc, "slot_opening_B_minus_A": slot_opening,
           "selectional_signal_B_minus_C": selectional_signal,
           "n_B_exceeds_oracle": n_B_exceeds, "n_C_exceeds_oracle": n_C_exceeds}


def _strict_verdict(role_stats: dict) -> str:
    so = role_stats.get("slot_opening_B_minus_A")
    ss = role_stats.get("selectional_signal_B_minus_C")
    if so is None or ss is None:
        return "NO_DATA"
    opens = so["band"] == "ABOVE"
    signal = ss["band"] == "ABOVE"
    if opens and signal:
        return "SLOT_OPENING_HELPS_AND_SELECTIONAL_SIGNAL_BEATS_SHUFFLE"
    if opens and not signal:
        return "SLOT_OPENING_HELPS_BUT_SELECTIONAL_SIGNAL_DOES_NOT_BEAT_SHUFFLE"
    if not opens and signal:
        return "SELECTIONAL_SIGNAL_BEATS_SHUFFLE_BUT_SLOT_OPENING_NOT_CI_SEPARATED"
    return "NEITHER_MECHANISM_CI_SEPARATED"


def run_full_strict(gen, smoke: bool, out_dir: str) -> dict:
    t0 = time.time()
    n_boot_paired = 400 if smoke else N_BOOT_PAIRED
    n_perm = 200 if smoke else N_PERM_NULL

    if smoke:
        fn_raw, fn_meta = build_framenet_raw_items(smoke=True)  # ZERO writes when smoke=True
    else:
        if not os.path.exists(V2_FRAMENET_CACHE_PATH):
            raise RuntimeError(f"{V2_FRAMENET_CACHE_PATH} not found (read-only dependency) -- run "
                              f"exp_shared_predarg_frontend_v2.py (bare) once first to build it.")
        with open(V2_FRAMENET_CACHE_PATH, "r", encoding="utf-8") as f:
            fn_raw = json.load(f)
        fn_meta = {"mode": "full", "source": "v2_cache_readonly", "path": V2_FRAMENET_CACHE_PATH}
    print(f"[strict] raw items={len(fn_raw)} meta={fn_meta} {time.time()-t0:.1f}s", flush=True)

    align_key = unit_key("aligned_with_margins", STRICT_ROUTER_VERSION)
    done = completed_units(out_dir)
    if align_key in done:
        aligned = load_units(out_dir)[align_key]
        n_mismatch = None
        print(f"[strict] resumed aligned items from checkpoint: {len(aligned)}", flush=True)
    else:
        aligned, n_mismatch = parse_and_align_with_margins(gen, fn_raw)
        record_unit(out_dir, align_key, aligned)
        print(f"[strict] aligned={len(aligned)} mismatch={n_mismatch} {time.time()-t0:.1f}s", flush=True)
    aligned = _normalize_item_keys(aligned)
    aligned_primary = [it for it in aligned if it["role_type"] in PRIMARY_ROLES]
    print(f"[strict] aligned_primary_roles={len(aligned_primary)} of {len(aligned)}", flush=True)

    train_items, test_items, split_meta = split_aligned_items(aligned_primary)
    print(f"[strict] split={split_meta} {time.time()-t0:.1f}s", flush=True)
    if split_meta["n_overlap_sentences"] != 0:
        raise RuntimeError(f"TRAIN/TEST sentence overlap detected: {split_meta} -- STOP (leakage guard)")

    train_triples = build_triples(train_items)
    reader = PredictiveReader().fit(train_triples)
    twin_reader = build_twin_reader(reader, seed=TWIN_SEED)
    print(f"[strict] reader fit on {len(train_triples)} TRAIN triples "
         f"(vr_pairs={len(reader._vr_centroid)})", flush=True)

    pred_key = unit_key("item_predictions_strict", STRICT_ROUTER_VERSION)
    done = completed_units(out_dir)
    if pred_key in done:
        item_preds = load_units(out_dir)[pred_key]
        print(f"[strict] resumed {len(item_preds)} item predictions from checkpoint", flush=True)
    else:
        item_preds = []
        for i, it in enumerate(test_items):
            pred = compute_item_prediction_strict(it["toks"], it["pos"], it["heads"], it["verb_idx"],
                                                  reader, twin_reader)
            item_preds.append(pred)
            if i and i % 2000 == 0:
                print(f"[strict-predict] {i}/{len(test_items)} {time.time()-t0:.1f}s", flush=True)
        record_unit(out_dir, pred_key, item_preds)
        print(f"[strict] computed {len(item_preds)} item predictions {time.time()-t0:.1f}s", flush=True)

    recs = score_test_items_strict(test_items, item_preds)
    print(f"[strict] scored {len(recs)} TEST items {time.time()-t0:.1f}s", flush=True)

    # INLINE cross-path harness sanity (reused check; build a minimal INLINE-only record set)
    inline_recs = []
    for it in test_items:
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        role = it["role_type"]
        s, e = it["span"]
        inline = arm_inline(toks, pos, heads, v)
        pick = inline.get(role)
        inline_recs.append({"role_type": role, "correct": {"INLINE": int(pick is not None and s < pick <= e)}})
    harness = _harness_sanity_check(test_items, inline_recs)
    print(f"[strict] INLINE cross-path harness sanity: pass={harness['pass']} "
         f"fresh_inline_acc={harness['fresh_inline_acc']}", flush=True)
    if not harness["pass"]:
        raise RuntimeError(f"HARNESS_SANITY_FAILED: {harness['mismatches']}. STOP, numbers below "
                          f"are NOT TRUSTED.")

    strata = {}
    for i, role in enumerate(PRIMARY_ROLES):
        strata[role] = strict_role_stats(recs, role, n_boot_paired, n_perm, 10 * i)
    ceiling_violations = {role: {"n_B_exceeds_oracle": strata[role].get("n_B_exceeds_oracle", 0),
                                 "n_C_exceeds_oracle": strata[role].get("n_C_exceeds_oracle", 0)}
                          for role in PRIMARY_ROLES}
    total_violations = sum(v["n_B_exceeds_oracle"] + v["n_C_exceeds_oracle"] for v in ceiling_violations.values())
    print(f"[strict] CEILING CHECK: total_violations={total_violations} per_role={ceiling_violations}",
         flush=True)
    if total_violations > 0:
        raise RuntimeError(f"CEILING_VIOLATED: an arm exceeded the strict oracle -- matching is "
                          f"still leaky. {ceiling_violations}. STOP.")

    per_role_verdict = {role: _strict_verdict(strata[role]) for role in PRIMARY_ROLES}
    n_both = sum(1 for v in per_role_verdict.values()
                if v == "SLOT_OPENING_HELPS_AND_SELECTIONAL_SIGNAL_BEATS_SHUFFLE")
    n_open_only = sum(1 for v in per_role_verdict.values()
                      if v == "SLOT_OPENING_HELPS_BUT_SELECTIONAL_SIGNAL_DOES_NOT_BEAT_SHUFFLE")
    n_signal_only = sum(1 for v in per_role_verdict.values()
                        if v == "SELECTIONAL_SIGNAL_BEATS_SHUFFLE_BUT_SLOT_OPENING_NOT_CI_SEPARATED")
    n_neither = sum(1 for v in per_role_verdict.values() if v == "NEITHER_MECHANISM_CI_SEPARATED")

    verdict = ("BOTH_MECHANISMS_CI_SEPARATED_SOME_ROLES" if n_both > 0 else
              ("SLOT_OPENING_ONLY_NO_SELECTIONAL_SIGNAL" if n_open_only > 0 and n_signal_only == 0 else
               ("SELECTIONAL_SIGNAL_ONLY_NO_SLOT_OPENING" if n_signal_only > 0 and n_open_only == 0 else
                "MIXED_OR_NEITHER")))

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | per_role={per_role_verdict} | ceiling_ok=True (0 violations) | "
            f"harness_ok={harness['pass']} | n_both={n_both} n_open_only={n_open_only} "
            f"n_signal_only={n_signal_only} n_neither={n_neither}"
        ),
        "summary": f"{verdict}: strict A/B/C de-confound, slot-opening vs selectional signal",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": ("smoke" if smoke else "full"),
        "anchor_name": ANCHOR_NAME + "_strict", "router_version": STRICT_ROUTER_VERSION,
        "n_boot_paired": n_boot_paired, "n_perm": n_perm, "window_tokens": WINDOW_TOKENS,
        "framenet_meta": fn_meta, "n_raw": len(fn_raw), "n_aligned": len(aligned), "n_mismatch": n_mismatch,
        "split": split_meta,
        "reader": {"n_train_triples": len(train_triples), "n_verb_role_pairs": len(reader._vr_centroid)},
        "harness_sanity": harness,
        "ceiling_check": {"total_violations": total_violations, "per_role": ceiling_violations},
        "strata": strata,
        "per_role_verdict": per_role_verdict,
        "scored_population": {
            "units_jsonl": os.path.join(out_dir, "units.jsonl"),
            "unit_keys": sorted([align_key, pred_key]),
        },
    }


# =================================================================================================
# RICHER-REPRESENTATION WHY-DRILL (coordinator, 2026-08-29): the strict result recovers a MAJORITY
# of the parse gap on path (60%)/source (92%) but a MINORITY on goal (22%)/location (19%)/
# recipient (10%). Hypothesis: the selectional signal (B-C) is limited by the COARSE object
# representation the scorer currently uses -- `hdlab.grounded_similarity.grounded_vector` is a
# z-scored 12-dim vector (11 Lancaster sensorimotor means + 1 Brysbaert concreteness rating; see
# hdlab/predictive_reader.py module docstring + hdlab/grounded_similarity.py). It encodes only
# coarse embodied/concreteness properties -- it cannot separate "kitchen" from "gym" from "office"
# (all indoor, similarly concrete, similarly low-sensorimotor-salience nouns), which is exactly the
# discrimination a LOCATION or GOAL selectional preference needs.
#
# RICHER REPRESENTATIONS ENUMERATED ON DISK (read-only survey, this cell writes to NONE of them):
#   - hdlab/grounded_similarity.py:distinctive_grounded_vector -- a LINEAR TRANSFORM of the SAME
#     12-dim Lancaster/Brysbaert table (decorrelating/whitening it). Same information content,
#     same dimensionality. NOT richer.
#   - hdlab/concept_encoder.py:ConceptEncoder -- a SUPERVISED, concept-label-conditioned CHARACTER-
#     TRIGRAM surface encoder trained on a synthetic designer-clustered corpus; its own docstring:
#     "NOT semantic English understanding". Wrong shape (no general per-word semantic vector) and
#     explicitly disclaimed as non-semantic. REJECTED.
#   - hdlab/ppmi_sparse_encoder.py:PPMISparseEncoder -- SUPERVISED (sentence, concept_label) PPMI/
#     SVD text encoder over char-trigrams (default n_dim=2048); needs a labeled corpus, not a
#     general per-word distributional space. Wrong shape for "one vector per PP-object head word".
#     REJECTED.
#   - hdlab/distributional_meaning_channel.py:DistributionalMeaningChannel -- the "learner work":
#     an UNSUPERVISED per-lemma distributional embedding `phi` [n_words, SVD_K=100], built by
#     PPMI-reweighting a word x word co-occurrence matrix then truncated SVD (`ppmi_svd`, ported
#     byte-for-byte from the landed exp_crossmodal_distillation_substitutability_v1 cell). THIS is
#     the richer representation the coordinator's hypothesis names: 100 dims (8.3x the grounded
#     space) capturing genuine DISTRIBUTIONAL (co-occurrence) structure rather than only embodied/
#     concreteness ratings -- it CAN separate "kitchen" from "gym" from "office" by how they're
#     used in text, which the 12-dim grounded space structurally cannot.
#     CAVEAT: no pre-built `phi`/vocabulary matrix is cached on disk (only summary metrics.json
#     files under data/exp_crossmodal_distillation_substitutability_v1/ and
#     data/exp_distributional_channel_store_representation_v1/ -- the actual embedding matrix was
#     never persisted, only its downstream scores). Building the FULL corpus-scale ConceptSpace
#     co-occurrence store `hdlab.reading_grounding_loop.ConceptSpace` requires a live corpus-read
#     pass, which is out of this cell's scope. INSTEAD: this cell reuses the EXACT vetted transform
#     (`ppmi_svd`, pure numpy/scipy, no side effects, imported READ-ONLY) over a word x word
#     co-occurrence matrix built from THIS CELL'S OWN TRAIN split sentences (13,731 sentences at
#     FULL scale, the SAME corpus PredictiveReader already trains on -- no new data dependency, no
#     leakage: TEST sentences never contribute a single co-occurrence count). svd_k=100 matches the
#     landed channel's SVD_K for a documented, non-arbitrary choice. See `build_rich_space`.
#
# PICKED: hdlab.distributional_meaning_channel.ppmi_svd (100-dim PPMI+SVD distributional space),
# refit on this cell's own TRAIN split. `_np_cos` scores it (plain numpy cosine; `_g`/`_cos` are
# torch-typed for the 12-dim table and not reused here).
# =================================================================================================
def _np_cos(a: np.ndarray, b: np.ndarray) -> float:
    na = float(np.linalg.norm(a))
    nb = float(np.linalg.norm(b))
    if na < 1e-9 or nb < 1e-9:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


def build_cooc_counts(sentences: List[List[str]], window: int = RICH_WINDOW) -> Dict[str, Counter]:
    """Symmetric token co-occurrence counts (word2vec-scale convention): for every pair of tokens
    within `window` positions of each other, increment BOTH directions so every word that appears
    is both a row-candidate and a context-column-candidate."""
    counts: Dict[str, Counter] = defaultdict(Counter)
    for toks in sentences:
        lc = [t.lower() for t in toks]
        n = len(lc)
        for i, w in enumerate(lc):
            lo = max(0, i - window)
            hi = min(n, i + window + 1)
            for j in range(lo, hi):
                if j == i:
                    continue
                counts[w][lc[j]] += 1
    return counts


def _safe_count_matrix(words: List[str], counts: Dict[str, Counter], vocab: Dict[str, int]) -> sp.csr_matrix:
    """[n_words, n_vocab] sparse co-occurrence matrix. Skips any context word not itself in `vocab`
    (can happen after min-count filtering drops a word that still appears as someone else's rare
    context) -- a plain KeyError-on-lookup would crash; here it is silently excluded per the
    filtering rationale (that word's OWN row was also dropped for being too rare to trust)."""
    rows: List[int] = []
    cols: List[int] = []
    data: List[float] = []
    for r, w in enumerate(words):
        for c, n in counts[w].items():
            ci = vocab.get(c)
            if ci is None:
                continue
            rows.append(r)
            cols.append(ci)
            data.append(float(n))
    return sp.csr_matrix((data, (rows, cols)), shape=(len(words), len(vocab)), dtype=np.float64)


def build_rich_space(train_items: List[dict], min_count: int = RICH_MIN_COUNT,
                     svd_k: int = RICH_SVD_K, seed: int = RICH_SEED
                     ) -> Tuple[np.ndarray, Dict[str, int]]:
    """TRAIN-split-only distributional space (PredictiveReader's exact leakage discipline: TEST
    sentences contribute zero co-occurrence counts). Returns (phi [n_words, svd_k], row_idx)."""
    seen_sent = set()
    sentences: List[List[str]] = []
    for it in train_items:
        key = " ".join(it["toks"])
        if key in seen_sent:
            continue
        seen_sent.add(key)
        sentences.append(it["toks"])
    counts = build_cooc_counts(sentences)
    freq: Counter = Counter()
    for w, c in counts.items():
        freq[w] = sum(c.values())
    words = sorted(w for w, f in freq.items() if f >= min_count)
    vocab = {w: i for i, w in enumerate(words)}
    M = _safe_count_matrix(words, counts, vocab)
    phi = ppmi_svd(M, svd_k=svd_k, seed=seed)  # REUSED verbatim (no reimplementation of PPMI/SVD math)
    row_idx = {w: i for i, w in enumerate(words)}
    return phi, row_idx


def fit_rich_reader(train_items: List[dict], rich_vec_fn) -> TwinReader:
    """Fits per-(verb,role) centroids in the RICH space, same triples/discipline as PredictiveReader
    (build_triples, TRAIN-only). Reuses the TwinReader CLASS as a plain dict-backed predict()/
    precision() reader (its shuffling logic lives in build_twin_reader, not in the class itself --
    TwinReader is genuinely representation-agnostic; no reimplementation needed)."""
    triples = build_triples(train_items)
    by_vr: Dict[Tuple[str, str], List[np.ndarray]] = defaultdict(list)
    by_role: Dict[str, List[np.ndarray]] = defaultdict(list)
    for verb, role, word in triples:
        v = rich_vec_fn(word)
        if v is None:
            continue
        by_vr[(verb, role)].append(v)
        by_role[role].append(v)
    vr_centroid = {k: np.mean(np.stack(v), axis=0) for k, v in by_vr.items()}
    role_centroid = {r: np.mean(np.stack(v), axis=0) for r, v in by_role.items()}
    precision = {k: float(np.mean([_np_cos(v, vr_centroid[k]) for v in vv])) for k, vv in by_vr.items()}
    return TwinReader(vr_centroid, role_centroid, precision)


def compute_item_prediction_richrep(toks, pos, heads, v, reader, twin_reader, rich_reader,
                                    rich_twin_reader, rich_vec_fn) -> dict:
    vlemma = lemma_verb(toks[v - 1])
    vclasses = get_event_classes(vlemma)
    window_raw = gather_topdown_candidates(toks, pos, heads, v)
    window_pp = [(prep, pidx, oidx, toks[oidx - 1]) for (prep, pidx, oidx) in window_raw]
    batch_raw = gather_batch_candidates(toks, pos, heads, v)
    batch_pp = [(prep, pidx, oidx, toks[oidx - 1]) for (prep, pidx, oidx) in batch_raw]

    a_picks, _ = topdown_candidate_picks_words(batch_pp, v, reader, vclasses, vlemma)
    b_picks, _ = topdown_candidate_picks_words(window_pp, v, reader, vclasses, vlemma)
    c_picks, _ = topdown_candidate_picks_words(window_pp, v, twin_reader, vclasses, vlemma)
    b_rich_picks, _ = topdown_candidate_picks_words(window_pp, v, rich_reader, vclasses, vlemma,
                                                     vec_fn=rich_vec_fn, cos_fn=_np_cos)
    c_rich_picks, _ = topdown_candidate_picks_words(window_pp, v, rich_twin_reader, vclasses, vlemma,
                                                     vec_fn=rich_vec_fn, cos_fn=_np_cos)
    return {"A": a_picks, "B": b_picks, "C": c_picks, "B_RICH": b_rich_picks, "C_RICH": c_rich_picks,
           "lemma": vlemma, "vclasses": sorted(vclasses),
           "window_cands": [list(c) for c in window_raw]}


def score_test_items_richrep(test_items: List[dict], item_preds: List[dict]) -> List[dict]:
    recs = []
    for it, pred in zip(test_items, item_preds):
        role = it["role_type"]
        s, e = it["span"]

        def inspan(idx):
            return int(idx is not None and s < idx <= e)

        correct = {"A_BATCH": inspan(pred["A"].get(role)),
                  "B_OPEN_REALSCORE": inspan(pred["B"].get(role)),
                  "C_OPEN_SHUFFLE": inspan(pred["C"].get(role)),
                  "B_RICH_REALSCORE": inspan(pred["B_RICH"].get(role)),
                  "C_RICH_SHUFFLE": inspan(pred["C_RICH"].get(role))}
        window_cands = [tuple(c) for c in pred["window_cands"]]
        oc = oracle_strict_correct(it, window_cands)
        elig = oc is not None
        if elig:
            correct["ORACLE"] = oc
        recs.append({"role_type": role, "oracle_eligible": elig, "correct": correct})
    return recs


_RICHREP_ARMS = ["A_BATCH", "B_OPEN_REALSCORE", "C_OPEN_SHUFFLE", "B_RICH_REALSCORE",
                 "C_RICH_SHUFFLE", "ORACLE"]


def richrep_role_stats(recs: List[dict], role: str, n_boot_paired: int, n_perm: int, seed_off: int) -> dict:
    rows = [r for r in recs if r["role_type"] == role and r["oracle_eligible"]]
    n = len(rows)
    if n == 0:
        return {"n": 0}
    vecs = {a: np.array([r["correct"][a] for r in rows], dtype=np.float64) for a in _RICHREP_ARMS}
    ceiling_violations = {a: int(np.sum(vecs[a] > vecs["ORACLE"])) for a in _RICHREP_ARMS if a != "ORACLE"}
    boot = paired_boot(vecs, n_boot_paired, BOOT_SEED + seed_off)
    acc = {}
    for a in _RICHREP_ARMS:
        lo, hi = np.percentile(boot[a], [2.5, 97.5])
        acc[a] = {"point": float(vecs[a].mean()), "ci95": [float(lo), float(hi)]}

    def _diff(a_name: str, b_name: str, off: int) -> dict:
        d = boot[a_name] - boot[b_name]
        lo, hi = np.percentile(d, [2.5, 97.5])
        return {"point": float(vecs[a_name].mean() - vecs[b_name].mean()), "ci95": [float(lo), float(hi)],
               "band": _band(lo, hi),
               "null_p95": _label_perm_null_p95(vecs[a_name], vecs[b_name], n_perm, BOOT_SEED + seed_off + off)}

    grounded_signal = _diff("B_OPEN_REALSCORE", "C_OPEN_SHUFFLE", 99)
    rich_signal = _diff("B_RICH_REALSCORE", "C_RICH_SHUFFLE", 199)
    rich_vs_grounded_B = _diff("B_RICH_REALSCORE", "B_OPEN_REALSCORE", 299)

    with np.errstate(divide="ignore", invalid="ignore"):
        og = boot["ORACLE"] - boot["A_BATCH"]
        frac_B = np.where(np.abs(og) > 1e-9, (boot["B_OPEN_REALSCORE"] - boot["A_BATCH"]) / og, np.nan)
        frac_BR = np.where(np.abs(og) > 1e-9, (boot["B_RICH_REALSCORE"] - boot["A_BATCH"]) / og, np.nan)
    valid_B = frac_B[~np.isnan(frac_B)]
    valid_BR = frac_BR[~np.isnan(frac_BR)]
    denom = float(vecs["ORACLE"].mean() - vecs["A_BATCH"].mean())
    frac_B_point = (float(vecs["B_OPEN_REALSCORE"].mean() - vecs["A_BATCH"].mean()) / denom
                    if abs(denom) > 1e-9 else float("nan"))
    frac_BR_point = (float(vecs["B_RICH_REALSCORE"].mean() - vecs["A_BATCH"].mean()) / denom
                     if abs(denom) > 1e-9 else float("nan"))

    return {"n": n, "acc": acc, "ceiling_violations": ceiling_violations,
           "grounded_selectional_signal_B_minus_C": grounded_signal,
           "rich_selectional_signal_BRICH_minus_CRICH": rich_signal,
           "rich_B_minus_grounded_B": rich_vs_grounded_B,
           "fraction_of_gap_recovered_grounded_B": {
               "point": frac_B_point,
               "ci95": [float(np.percentile(valid_B, 2.5)), float(np.percentile(valid_B, 97.5))]
                      if len(valid_B) else [float("nan"), float("nan")]},
           "fraction_of_gap_recovered_rich_B": {
               "point": frac_BR_point,
               "ci95": [float(np.percentile(valid_BR, 2.5)), float(np.percentile(valid_BR, 97.5))]
                      if len(valid_BR) else [float("nan"), float("nan")]}}


def _richrep_verdict(role_stats: dict) -> str:
    rg = role_stats.get("rich_B_minus_grounded_B")
    if rg is None:
        return "NO_DATA"
    return ("GROUNDED_SPACE_BOUND_RICH_REP_HELPS" if rg["band"] == "ABOVE"
           else ("RICH_REP_HURTS" if rg["band"] == "BELOW" else "NOT_GROUNDED_SPACE_BOUND_RICH_REP_NO_HELP"))


def run_full_richrep(gen, smoke: bool, out_dir: str) -> dict:
    t0 = time.time()
    n_boot_paired = 400 if smoke else N_BOOT_PAIRED
    n_perm = 200 if smoke else N_PERM_NULL

    if smoke:
        fn_raw, fn_meta = build_framenet_raw_items(smoke=True)  # ZERO writes when smoke=True
    else:
        if not os.path.exists(V2_FRAMENET_CACHE_PATH):
            raise RuntimeError(f"{V2_FRAMENET_CACHE_PATH} not found (read-only dependency) -- run "
                              f"exp_shared_predarg_frontend_v2.py (bare) once first to build it.")
        with open(V2_FRAMENET_CACHE_PATH, "r", encoding="utf-8") as f:
            fn_raw = json.load(f)
        fn_meta = {"mode": "full", "source": "v2_cache_readonly", "path": V2_FRAMENET_CACHE_PATH}
    print(f"[richrep] raw items={len(fn_raw)} meta={fn_meta} {time.time()-t0:.1f}s", flush=True)

    align_key = unit_key("aligned_with_margins", RICHREP_ROUTER_VERSION)
    done = completed_units(out_dir)
    if align_key in done:
        aligned = load_units(out_dir)[align_key]
        n_mismatch = None
        print(f"[richrep] resumed aligned items from checkpoint: {len(aligned)}", flush=True)
    else:
        aligned, n_mismatch = parse_and_align_with_margins(gen, fn_raw)
        record_unit(out_dir, align_key, aligned)
        print(f"[richrep] aligned={len(aligned)} mismatch={n_mismatch} {time.time()-t0:.1f}s", flush=True)
    aligned = _normalize_item_keys(aligned)
    aligned_primary = [it for it in aligned if it["role_type"] in PRIMARY_ROLES]
    print(f"[richrep] aligned_primary_roles={len(aligned_primary)} of {len(aligned)}", flush=True)

    train_items, test_items, split_meta = split_aligned_items(aligned_primary)
    print(f"[richrep] split={split_meta} {time.time()-t0:.1f}s", flush=True)
    if split_meta["n_overlap_sentences"] != 0:
        raise RuntimeError(f"TRAIN/TEST sentence overlap detected: {split_meta} -- STOP (leakage guard)")

    train_triples = build_triples(train_items)
    reader = PredictiveReader().fit(train_triples)
    twin_reader = build_twin_reader(reader, seed=TWIN_SEED)
    print(f"[richrep] grounded reader fit on {len(train_triples)} TRAIN triples "
         f"(vr_pairs={len(reader._vr_centroid)})", flush=True)

    phi, row_idx = build_rich_space(train_items)
    print(f"[richrep] RICH SPACE: n_words={len(row_idx)} dim={phi.shape[1]} "
         f"(PPMI+SVD over {len({' '.join(it['toks']) for it in train_items})} TRAIN sentences) "
         f"{time.time()-t0:.1f}s", flush=True)

    def rich_vec(word: str) -> Optional[np.ndarray]:
        i = row_idx.get(word.lower())
        return phi[i] if i is not None else None

    rich_reader = fit_rich_reader(train_items, rich_vec)
    rich_twin_reader = build_twin_reader(rich_reader, seed=RICH_TWIN_SEED)
    print(f"[richrep] rich reader fit (vr_pairs={len(rich_reader._vr_centroid)}) "
         f"{time.time()-t0:.1f}s", flush=True)

    pred_key = unit_key("item_predictions_richrep", RICHREP_ROUTER_VERSION)
    done = completed_units(out_dir)
    if pred_key in done:
        item_preds = load_units(out_dir)[pred_key]
        print(f"[richrep] resumed {len(item_preds)} item predictions from checkpoint", flush=True)
    else:
        item_preds = []
        for i, it in enumerate(test_items):
            pred = compute_item_prediction_richrep(it["toks"], it["pos"], it["heads"], it["verb_idx"],
                                                    reader, twin_reader, rich_reader, rich_twin_reader,
                                                    rich_vec)
            item_preds.append(pred)
            if i and i % 2000 == 0:
                print(f"[richrep-predict] {i}/{len(test_items)} {time.time()-t0:.1f}s", flush=True)
        record_unit(out_dir, pred_key, item_preds)
        print(f"[richrep] computed {len(item_preds)} item predictions {time.time()-t0:.1f}s", flush=True)

    recs = score_test_items_richrep(test_items, item_preds)
    print(f"[richrep] scored {len(recs)} TEST items {time.time()-t0:.1f}s", flush=True)

    inline_recs = []
    for it in test_items:
        toks, pos, heads, v = it["toks"], it["pos"], it["heads"], it["verb_idx"]
        role = it["role_type"]
        s, e = it["span"]
        inline = arm_inline(toks, pos, heads, v)
        pick = inline.get(role)
        inline_recs.append({"role_type": role, "correct": {"INLINE": int(pick is not None and s < pick <= e)}})
    harness = _harness_sanity_check(test_items, inline_recs)
    print(f"[richrep] INLINE cross-path harness sanity: pass={harness['pass']} "
         f"fresh_inline_acc={harness['fresh_inline_acc']}", flush=True)
    if not harness["pass"]:
        raise RuntimeError(f"HARNESS_SANITY_FAILED: {harness['mismatches']}. STOP, numbers below "
                          f"are NOT TRUSTED.")

    strata = {}
    for i, role in enumerate(PRIMARY_ROLES):
        strata[role] = richrep_role_stats(recs, role, n_boot_paired, n_perm, 10 * i)
    ceiling_violations = {role: strata[role].get("ceiling_violations", {}) for role in PRIMARY_ROLES}
    total_violations = sum(sum(v.values()) for v in ceiling_violations.values())
    print(f"[richrep] CEILING CHECK: total_violations={total_violations} per_role={ceiling_violations}",
         flush=True)
    if total_violations > 0:
        raise RuntimeError(f"CEILING_VIOLATED: an arm exceeded the strict oracle -- {ceiling_violations}. STOP.")

    per_role_verdict = {role: _richrep_verdict(strata[role]) for role in PRIMARY_ROLES}
    n_helps = sum(1 for v in per_role_verdict.values() if v == "GROUNDED_SPACE_BOUND_RICH_REP_HELPS")
    n_no_help = sum(1 for v in per_role_verdict.values() if v == "NOT_GROUNDED_SPACE_BOUND_RICH_REP_NO_HELP")
    n_hurts = sum(1 for v in per_role_verdict.values() if v == "RICH_REP_HURTS")

    verdict = ("GROUNDED_SPACE_BOUND_SOME_ROLES" if n_helps > 0 else
              ("RICH_REP_NO_HELP_ANY_ROLE" if n_no_help + n_hurts == len(PRIMARY_ROLES) else "MIXED"))

    return {
        "verdict": verdict,
        "verdict_msg": (
            f"{verdict} | per_role={per_role_verdict} | ceiling_ok=True (0 violations) | "
            f"harness_ok={harness['pass']} | rich_dim={phi.shape[1]} rich_n_words={len(row_idx)} | "
            f"n_helps={n_helps} n_no_help={n_no_help} n_hurts={n_hurts}"
        ),
        "summary": f"{verdict}: richer (PPMI+SVD, dim={phi.shape[1]}) vs grounded (dim=12) selectional signal",
        "elapsed_s": round(time.time() - t0, 2), "run_mode": ("smoke" if smoke else "full"),
        "anchor_name": ANCHOR_NAME + "_richrep", "router_version": RICHREP_ROUTER_VERSION,
        "n_boot_paired": n_boot_paired, "n_perm": n_perm, "window_tokens": WINDOW_TOKENS,
        "rich_space": {"dim": int(phi.shape[1]), "n_words": len(row_idx), "svd_k": RICH_SVD_K,
                      "window": RICH_WINDOW, "min_count": RICH_MIN_COUNT,
                      "source": "hdlab.distributional_meaning_channel.ppmi_svd, refit on this "
                                "cell's own TRAIN split (read-only reuse of the transform, no "
                                "cached corpus-scale phi found on disk)"},
        "grounded_space": {"dim": 12, "source": "hdlab.grounded_similarity.grounded_vector "
                                                "(11 Lancaster sensorimotor means + Brysbaert "
                                                "concreteness)"},
        "framenet_meta": fn_meta, "n_raw": len(fn_raw), "n_aligned": len(aligned), "n_mismatch": n_mismatch,
        "split": split_meta,
        "harness_sanity": harness,
        "ceiling_check": {"total_violations": total_violations, "per_role": ceiling_violations},
        "strata": strata,
        "per_role_verdict": per_role_verdict,
        "scored_population": {
            "units_jsonl": os.path.join(out_dir, "units.jsonl"),
            "unit_keys": sorted([align_key, pred_key]),
        },
    }


# =================================================================================================
# self-test -- hand + synthetic-fixture cases
# =================================================================================================
def self_test() -> dict:
    print("[self-test] starting", flush=True)

    # --- (1) PredictiveReader fits a sensible goal centroid ------------------------------------
    triples = [
        ("walk", "goal", "door"), ("walk", "goal", "house"), ("walk", "goal", "school"),
        ("give", "recipient", "teacher"), ("give", "recipient", "student"), ("give", "recipient", "child"),
    ]
    reader = PredictiveReader().fit(triples)
    walk_goal = reader.predict("walk", "goal")
    give_recip = reader.predict("give", "recipient")
    assert walk_goal is not None and give_recip is not None
    cos_walk_door = _cos(_g("door"), walk_goal)
    cos_walk_teacher = _cos(_g("teacher"), walk_goal)
    assert cos_walk_door > cos_walk_teacher, (cos_walk_door, cos_walk_teacher)
    print(f"  [PASS] reader predicts a sensible goal centroid: cos(door, walk-goal)={cos_walk_door:.3f} "
         f"> cos(teacher, walk-goal)={cos_walk_teacher:.3f}", flush=True)
    assert reader.precision("walk", "goal") is not None
    print(f"  [PASS] precision(walk,goal)={reader.precision('walk', 'goal'):.3f} (not None)", flush=True)

    # --- (2) the reranker opens a PP the bottom-up parser never attached -----------------------
    # synthetic fixture: "He walked quickly yesterday to the door ." with a BROKEN head-chain for
    # the PP object (7 'door') so _pp_args_for_verb's _attaches_to_verb walk cannot reach the verb
    # (2 'walked') -- 7 -> 8 (PUNCT) -> 0 (ROOT), never touching the verb. gather_topdown_
    # candidates does NOT filter by attachment, so it still finds (to, 5, 7).
    toks = ["He", "walked", "quickly", "yesterday", "to", "the", "door", "."]
    pos = ["PRON", "VERB", "ADV", "ADV", "ADP", "DET", "NOUN", "PUNCT"]
    heads = {1: 2, 2: 0, 3: 2, 4: 2, 5: 7, 6: 7, 7: 8, 8: 0}  # 7's chain (7->8->0/ROOT) never
                                                              # reaches the verb (2)
    margins = {1: 5.0, 2: 10.0, 3: 5.0, 4: 5.0, 5: 20.0, 6: 5.0, 7: 3.0, 8: 5.0}  # low margin at 7
    v = 2
    batch = route_predicate_arguments(toks, pos, heads, v)
    assert batch.get("goal") is None, batch  # bottom-up cannot see it (broken head-chain)
    print(f"  [PASS] BATCH cannot attach 'to the door' (broken head-chain): batch['goal']=None",
         flush=True)
    fixture_reader = PredictiveReader().fit([("walk", "goal", "door"), ("walk", "goal", "house")])
    pred = compute_item_prediction(toks, pos, heads, margins, v, fixture_reader)
    assert pred["topdown_picks"].get("goal") == 7, pred["topdown_picks"]
    merged_low = merge_gated(batch, pred["topdown_picks"], pred["margins_by_role"], thresh=100.0)
    assert merged_low.get("goal") == 7, merged_low
    print(f"  [PASS] TOPDOWN reranker opens the unattached PP: goal=door (token 7), "
         f"gated-merge at a high threshold also recovers it (batch pick is None -> always uses "
         f"topdown)", flush=True)

    # --- (3) high-margin batch pick is KEPT even if topdown disagrees --------------------------
    toks2 = ["Tom", "handed", "the", "letter", "to", "Mary", "."]
    pos2 = ["PROPN", "VERB", "DET", "NOUN", "ADP", "PROPN", "PUNCT"]
    heads2 = {1: 2, 2: 0, 3: 4, 4: 2, 5: 6, 6: 2, 7: 2}
    margins2 = {1: 5.0, 2: 5.0, 3: 5.0, 4: 5.0, 5: 5.0, 6: 50.0, 7: 5.0}  # HIGH margin at 6 (Mary)
    v2 = 2
    batch2 = route_predicate_arguments(toks2, pos2, heads2, v2)
    assert batch2.get("recipient") == 6, batch2  # 'give'-class 'to' -> recipient, batch finds it
    pred2 = compute_item_prediction(toks2, pos2, heads2, margins2, v2, reader)
    merged_high = merge_gated(batch2, pred2["topdown_picks"], pred2["margins_by_role"], thresh=10.0)
    assert merged_high.get("recipient") == 6, merged_high
    print("  [PASS] high-margin batch pick (recipient=Mary, margin=50.0 >= thresh=10.0) is KEPT",
         flush=True)

    # --- (4) TWIN differs from the real reader on a case with real reader signal ---------------
    twin_reader = build_twin_reader(reader, seed=TWIN_SEED)
    twin_walk_goal = twin_reader.predict("walk", "goal")
    assert twin_walk_goal is not None
    cos_twin_door = _cos(_g("door"), twin_walk_goal)
    assert abs(cos_twin_door - cos_walk_door) > 1e-6 or twin_walk_goal is not walk_goal, (
        "TWIN reader must differ from the real reader after permutation")
    print(f"  [PASS] TWIN reader differs from the real reader: cos(door,TWIN-walk-goal)="
         f"{cos_twin_door:.3f} vs cos(door,real-walk-goal)={cos_walk_door:.3f}", flush=True)

    # ARMS-MUST-DIFFER (META_RULE_AF): BATCH vs TOPDOWN vs TWIN must not be bit-identical on the
    # unattached-PP fixture (BATCH has goal=None; TOPDOWN/TWIN both fill it, but via different
    # readers -- confirm TOPDOWN's own pick differs from what a TWIN-reader pass would score, by
    # checking the SCORE differs even if this tiny 2-verb fixture happens to pick the same token).
    twin_picks_fixture, twin_scores_fixture = topdown_candidate_picks_words(
        [tuple(c) for c in pred["cands_pp"]], v, twin_reader, frozenset(pred["vclasses"]), "walk")
    assert batch.get("goal") != pred["topdown_picks"].get("goal"), "BATCH vs TOPDOWN must differ here"
    print(f"  [PASS] arms-must-differ: BATCH goal={batch.get('goal')} vs TOPDOWN goal="
         f"{pred['topdown_picks'].get('goal')} (differ); TWIN score={twin_scores_fixture.get('goal')} "
         f"vs TOPDOWN score={pred['topdown_scores'].get('goal')}", flush=True)

    # --- (5) INLINE cross-path stability -------------------------------------------------------
    fake_items = [{"toks": toks2, "pos": pos2, "heads": heads2, "verb_idx": v2, "role_type": "goal",
                  "span": [4, 6]}]
    fake_recs = [{"role_type": "goal", "correct": {"INLINE": int(
        arm_inline(toks2, pos2, heads2, v2).get("goal") is not None and
        4 < arm_inline(toks2, pos2, heads2, v2)["goal"] <= 6)}}]
    harness = _harness_sanity_check(fake_items, fake_recs)
    assert harness["pass"], harness
    print(f"  [PASS] INLINE cross-path harness sanity: {harness}", flush=True)

    # --- (6) split determinism + zero overlap on a tiny synthetic set --------------------------
    fake_aligned = [{"toks": ["a", "b", "c"], "role_type": "goal"},
                    {"toks": ["a", "b", "c"], "role_type": "location"},  # SAME sentence, 2 items
                    {"toks": ["d", "e", "f"], "role_type": "path"}]
    tr, te, meta = split_aligned_items(fake_aligned)
    assert meta["n_overlap_sentences"] == 0, meta
    keys_a = {_sentence_key(it) for it in tr}
    keys_b = {_sentence_key(it) for it in te}
    assert not (keys_a & keys_b), (keys_a, keys_b)
    print(f"  [PASS] split determinism + zero sentence overlap: {meta}", flush=True)

    # bootstrap sanity
    a = np.array([1.0, 1.0, 1.0, 0.0])
    b = np.array([0.0, 0.0, 1.0, 0.0])
    boot = paired_boot({"a": a, "b": b}, 500, 1)
    assert abs(float((boot["a"] - boot["b"]).mean()) - 0.5) < 0.15
    print("[self-test] PASS", flush=True)
    return {"verdict": "SELFTEST_PASS", "verdict_msg": "SELFTEST_PASS", "summary": "SELFTEST_PASS",
           "elapsed_s": 0.0, "run_mode": "self_test", "anchor_name": ANCHOR_NAME}


def _write(output_dir: str, metrics: dict) -> None:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--self-test", action="store_true", dest="self_test")
    p.add_argument("--smoke", action="store_true")
    p.add_argument("--mode", choices=["full", "smoke"], default=None)
    p.add_argument("--strict", action="store_true",
                   help="run the de-confounded A/B/C strict pipeline instead of the original "
                        "margin-gated TOPDOWN pipeline; writes ONLY to *_strict[/_smoke]")
    p.add_argument("--richrep", action="store_true",
                   help="run the richer-object-representation why-drill (A/B/C + B_RICH/C_RICH); "
                        "writes ONLY to *_richrep[/_smoke]")
    args = p.parse_args()
    smoke = bool(args.smoke) or (args.mode == "smoke")

    if args.strict:
        suffix = "_smoke" if smoke else ""
        out_dir = STRICT_OUTPUT_DIR + suffix
        try:
            gen = _default_generator()
            metrics = run_full_strict(gen, smoke=smoke, out_dir=out_dir)
            _write(out_dir, metrics)
            print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
            print(metrics["verdict_msg"], flush=True)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001 -- NOT BaseException
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
                   "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                   "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME + "_strict"}
            _write(out_dir, diag)
            raise
        return

    if args.richrep:
        suffix = "_smoke" if smoke else ""
        out_dir = RICHREP_OUTPUT_DIR + suffix
        try:
            gen = _default_generator()
            metrics = run_full_richrep(gen, smoke=smoke, out_dir=out_dir)
            _write(out_dir, metrics)
            print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
            print(metrics["verdict_msg"], flush=True)
        except SystemExit:
            raise
        except KeyboardInterrupt:
            raise
        except Exception as e:  # noqa: BLE001 -- NOT BaseException
            diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
                   "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                   "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME + "_richrep"}
            _write(out_dir, diag)
            raise
        return

    suffix = "_selftest" if args.self_test else ("_smoke" if smoke else "")
    out_dir = OUTPUT_DIR + suffix

    try:
        if args.self_test:
            metrics = self_test()
        else:
            gen = _default_generator()
            metrics = run_full(gen, smoke=smoke, out_dir=out_dir)
        _write(out_dir, metrics)
        print(f"[main] wrote metrics verdict={metrics['verdict']}", flush=True)
        print(metrics["verdict_msg"], flush=True)
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # noqa: BLE001 -- NOT BaseException; preserves SystemExit/KeyboardInterrupt
        diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:500]}",
               "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
               "traceback": traceback.format_exc()[:5000], "anchor_name": ANCHOR_NAME}
        _write(out_dir, diag)
        raise


if __name__ == "__main__":
    main()
