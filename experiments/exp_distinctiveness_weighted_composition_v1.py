"""exp_distinctiveness_weighted_composition_v1 -- does weighting features by DISTINCTIVENESS
before bundling separate near-neighbours the way the brain does?

PRE-REG: preregs/2026-08-13_distinctiveness_weighted_composition.md (commit ac87fc807, filed
BEFORE any arm ran). Brain drill: notes/brain_drill_encoder_lexical_semantics_2026-08-13.md
(commit 471798502), element E1.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified at smoke gate (META_RULE_AF; ARMS-MUST-DIFFER hash-test)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH); SMOKE writes a SEPARATE output dir
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a declared + SE(rho) feasibility declared (pre-reg sec 9)
# - discriminator survives scale: SCRAMBLE_ASSIGN must FAIL the headline gate at smoke scale
# - HARD_PASS strictly above floor + 5% band-width (META_RULE_L)
# - cardinality_ok: EXPECTED_N_UNITS = 18 (3 supplies x 6 arms), gated in the verdict
# - per-unit failure-class instrumentation (META_RULE_J; no bare except, no BaseException)
# - deterministic seeding: fixed ints + hashlib only; no builtin hash(), no list(set())
# - all numbers in comments tagged MEASURED@ / HYPOTHESIZED@ / THEORETICAL@ / CITED@

THE ONE VARIABLE: weight each feature vector by its distinctiveness before bundle().
NO FILE UNDER hdlab/ IS MODIFIED. The weighting lives here; hdlab.bundling.bundle,
hdlab.situation_model_accumulate.unit_phase_vec, hdlab.lexical_similarity._cos_complex,
hdlab.grounded_similarity and hdlab.low_information_filter are all imported and called unmodified.

DISTINCTIVENESS = REUSE of hdlab/low_information_filter.py's existing PMI measure, per the
standing rule that a mechanism sharing an already-built process reuses that organ. With one
document per concept (doc = [concept] + its features), the organ's own pmi() reduces exactly to
log2(n_concepts / df_feature) -- the Tyler & Moss distinctiveness quantity. That reduction is
ASSERTED at runtime (_assert_pmi_reduction), and the streamed profile construction used for the
large CSKG population is ASSERTED bit-identical to the organ's own build_profile() on a
subsample (_assert_streamed_profile_matches_build_profile). No parallel measure is introduced.

ASCII-only.
"""
from __future__ import annotations

# THREAD PINS -- must precede numpy/torch import (they size their pools at import time).
import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import argparse
import csv
import gzip
import hashlib
import json
import math
import pickle
import platform
import re
import time
import traceback
from datetime import datetime, timezone
from typing import Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

import numpy as np
import torch
from scipy.stats import spearmanr

_THIS = os.path.abspath(__file__)
REPO_ROOT = os.path.dirname(os.path.dirname(_THIS))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import modulators                                    # noqa: E402
from hdlab.bundling import bundle                               # noqa: E402
from hdlab.grounded_similarity import (                         # noqa: E402
    GROUNDED_CAP, _raw_cos as grounded_raw_cos, grounded_similarity,
    grounded_vector, in_grounded_lexicon,
)
from hdlab.lexical_similarity import (                          # noqa: E402
    CONCEPT_FEATURES, _cos_complex, _feature_vectors,
)
from hdlab.low_information_filter import InformationProfile, build_profile   # noqa: E402
from hdlab.situation_model_accumulate import unit_phase_vec     # noqa: E402
from experiments._validity_preflight import run_validity_preflight          # noqa: E402
from tools.exp_checkpoint import completed_units, load_units, record_unit, unit_key  # noqa: E402

# ---------------------------------------------------------------------------------------------
# CONFIG (all pre-registered; nothing below is adjusted after seeing results)
# ---------------------------------------------------------------------------------------------
ANCHOR_NAME = "exp_distinctiveness_weighted_composition_v1"
PREREG_PATH = "preregs/2026-08-13_distinctiveness_weighted_composition.md"

OUT_FULL = os.path.join(REPO_ROOT, "data", ANCHOR_NAME)
OUT_SMOKE = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SMOKE")   # SEPARATE dir (mandatory)
OUT_SELFTEST = os.path.join(REPO_ROOT, "data", ANCHOR_NAME + "_SELFTEST")
CACHE_PATH = os.path.join(REPO_ROOT, "data", "_cache_cskg_simlex_canonical_v1.pkl")

SIMLEX_PATH = os.path.join(REPO_ROOT, "data", "encoder_eval_benchmarks", "simlex999.txt")
CSKG_PATH = os.path.join(REPO_ROOT, "data", "grounding_testbed", "cskg.tsv.gz")

# N_DIM: supply A matches hdlab.lexical_similarity exactly (8192 / seed 7) so its geometry
# reproduces the live module. Supply B/C use the repo-default 1024 (79,815 feature vectors at
# 8192 complex64 would be ~5.2GB). Pre-reg sec 10.
N_DIM_A, FEATURE_SEED_A = 8192, 7
N_DIM_BC, FEATURE_SEED_BC = 1024, 7
SCRAMBLE_SEED = 999          # matches hdlab.lexical_similarity.self_test step 5 convention
PHASE_CHUNK = 4096           # fixed -> phase generation order is deterministic

SUPPLIES = ("A_CONCEPT_FEATURES", "B_CSKG", "C_CSKG_NOLEXREL")
ARMS = ("WEIGHTED", "UNIFORM", "GROUNDED_RAW", "GROUNDED_CAPPED",
        "SCRAMBLE_ASSIGN", "SCRAMBLE_WEIGHTS")
EXPECTED_N_UNITS = len(SUPPLIES) * len(ARMS)          # 18; cardinality gate (META_RULE_H)

# PRE-REGISTERED BANDS -- pre-reg sec 8. DO NOT EDIT AFTER A RUN.
HP_RHO_MIN = 0.35
HP_DELTA_UNIFORM = 0.08
HP_DELTA_GROUNDED = 0.15
HP_SCRAMBLE_MAX = 0.05
HF_SHAPE_DELTA = 0.03
HF_SUPPLY_COVERAGE = 0.20
BAND_MARGIN_FRAC = 0.05      # META_RULE_L: clear by <5% of band width -> MIDDLE_BAND

# Public calibration points, quoted alongside, NOT arms.
# CITED@Mrksic et al. 2016 arXiv:1603.00892 Table 2 (via drill sec 1.5f)
CALIBRATION = {"glove": 0.41, "counter_fitting": 0.58, "human_iaa": 0.67}

# Supply C drops lexical-relation edges -- a synonym/similarity dictionary would otherwise supply
# the answer directly. Pre-reg sec 5.
LEXREL_DROP = frozenset({
    "/r/Synonym", "/r/Antonym", "/r/SimilarTo", "/r/RelatedTo", "/r/DistinctFrom",
    "/r/DerivedFrom", "/r/EtymologicallyRelatedTo", "/r/EtymologicallyDerivedFrom", "/r/FormOf",
})

# Canonical CSKG concept node: exactly /c/en/<lowercase-word>. This makes label <-> node 1:1, so
# "one document per concept" holds exactly and the organ's pmi reduction is exact.
# MEASURED@pre-flight probe 2026-08-13: 276,365 such nodes, 1,767,049 edges, 1028/1028 SimLex
# words covered, 79,815 distinct features over the SimLex vocabulary.
_CANON_NODE = re.compile(r"^/c/en/[a-z]+$")

SMOKE_PAIR_SCALES = (120, 480)      # multi-scale smoke (pair count is the statistic's load axis)


# ---------------------------------------------------------------------------------------------
# Durability plumbing (pre-reg sec 11)
# ---------------------------------------------------------------------------------------------
def _write_start_marker(output_dir: str, run_mode: str) -> None:
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": EXPECTED_N_UNITS, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _heartbeat(output_dir: str, unit_idx: int, total_units: int, elapsed_s: float,
               extra: Optional[dict] = None) -> None:
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "unit_idx": unit_idx,
           "total_units": total_units, "elapsed_s": round(elapsed_s, 3)}
    if extra:
        row["extra"] = extra
    os.makedirs(output_dir, exist_ok=True)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
        f.flush()
        os.fsync(f.fileno())


def _atomic_write_metrics(output_dir: str, metrics: dict) -> str:
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)          # META_RULE_AH
    return final


def _write_crash_metrics(output_dir: str, exc: Exception) -> None:
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__,
            "elapsed_s": 0.0, "run_mode": "crash",
            "failure_class": type(exc).__name__,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _atomic_write_metrics(output_dir, diag)


def _stable_seed(key: str) -> int:
    """Deterministic across processes (F.5: never builtin hash(), never list(set()))."""
    return int.from_bytes(hashlib.sha256(key.encode("utf-8")).digest()[:8], "big") % (2 ** 31)


# ---------------------------------------------------------------------------------------------
# Data
# ---------------------------------------------------------------------------------------------
def load_simlex(limit: Optional[int] = None) -> List[Tuple[str, str, float]]:
    out: List[Tuple[str, str, float]] = []
    with open(SIMLEX_PATH, encoding="utf-8") as f:
        for row in csv.DictReader(f, delimiter="\t"):
            out.append((row["word1"], row["word2"], float(row["SimLex999"])))
    if limit is not None:
        out = out[:limit]
    return out


def build_cskg_cache(vocab: Set[str]) -> dict:
    """Two streaming passes over CSKG restricted to canonical /c/en/<word> nodes.

    Pass 1 -- feature sets for the evaluated vocabulary + the needed-feature set.
    Pass 2 -- document frequency of each needed feature over the WHOLE canonical concept
              population (that is the population distinctiveness is measured against), plus a
              2,000-concept document sample used to prove the streamed profile construction is
              equivalent to the organ's own build_profile().
    Node1 is contiguous in the file (MEASURED@pre-flight probe: 0 contiguity violations over
    1,511,784 node1 groups), so per-concept dedupe is exact.
    """
    t0 = time.time()
    word_feats: Dict[str, Set[str]] = {}
    n_docs = 0
    print("[cskg] pass 1/2 (feature sets for evaluated vocabulary)", flush=True)
    with gzip.open(CSKG_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        last = None
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 6 or not _CANON_NODE.match(p[1]):
                continue
            if p[1] != last:
                last = p[1]
                n_docs += 1
            w = p[1][6:]
            if w in vocab:
                word_feats.setdefault(w, set()).add(p[2] + "|" + p[3])
    needed: Set[str] = set()
    for s in word_feats.values():
        needed |= s
    print("[cskg] pass 1 done: %d concepts in population, %d evaluated words, %d needed features "
          "(%.1fs)" % (n_docs, len(word_feats), len(needed), time.time() - t0), flush=True)

    print("[cskg] pass 2/2 (document frequency over the full concept population)", flush=True)
    df: Dict[str, int] = {}
    sample_docs: List[List[str]] = []
    cur_node: Optional[str] = None
    cur_feats: Set[str] = set()

    def _flush(node: Optional[str], feats: Set[str]) -> None:
        if node is None:
            return
        for ft in feats:
            df[ft] = df.get(ft, 0) + 1
        if len(sample_docs) < 2000 and feats:
            sample_docs.append([node[6:]] + sorted(feats))

    with gzip.open(CSKG_PATH, "rt", encoding="utf-8") as f:
        f.readline()
        for line in f:
            p = line.rstrip("\n").split("\t")
            if len(p) < 6 or not _CANON_NODE.match(p[1]):
                continue
            if p[1] != cur_node:
                _flush(cur_node, cur_feats)
                cur_node, cur_feats = p[1], set()
            ft = p[2] + "|" + p[3]
            if ft in needed or len(sample_docs) < 2000:
                cur_feats.add(ft)
    _flush(cur_node, cur_feats)
    cache = {"n_docs": n_docs,
             "word_feats": {w: sorted(s) for w, s in word_feats.items()},
             "df": {k: v for k, v in df.items() if k in needed},
             "sample_docs": sample_docs}
    print("[cskg] pass 2 done: df for %d features, %d sample docs (%.1fs total)"
          % (len(cache["df"]), len(sample_docs), time.time() - t0), flush=True)
    return cache


def get_cskg_cache(vocab: Set[str]) -> dict:
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "rb") as f:
            cache = pickle.load(f)
        if set(cache["word_feats"]) >= vocab:
            print("[cskg] using cache %s" % CACHE_PATH, flush=True)
            return cache
        print("[cskg] cache vocabulary insufficient; rebuilding", flush=True)
    cache = build_cskg_cache(vocab)
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    tmp = CACHE_PATH + ".tmp"
    with open(tmp, "wb") as f:
        pickle.dump(cache, f, protocol=4)
    os.replace(tmp, CACHE_PATH)
    return cache


# ---------------------------------------------------------------------------------------------
# Distinctiveness via hdlab.low_information_filter (REUSE -- no parallel measure)
# ---------------------------------------------------------------------------------------------
def _pair_key(a: str, b: str) -> Tuple[str, str]:
    return (a, b) if a <= b else (b, a)


def streamed_profile(n_docs: int, feat_df: Dict[str, int],
                     word_feats: Dict[str, Sequence[str]]) -> InformationProfile:
    """Construct the organ's own InformationProfile from a streamed df plus the EXACT sparse
    pair_df entries (each concept occupies exactly one document, so pair_df[(c,f)] == 1 and
    df[c] == 1 -- both exact, not approximations). prof.pmi() is then the organ's unmodified
    method. Equivalence to build_profile() is asserted in
    _assert_streamed_profile_matches_build_profile()."""
    df: Dict[str, int] = dict(feat_df)
    pair_df: Dict[Tuple[str, str], int] = {}
    for c, feats in word_feats.items():
        if c in df:
            raise ValueError("NAMESPACE COLLISION: concept %r is also a feature token" % c)
        df[c] = 1
        for ft in feats:
            pair_df[_pair_key(c, ft)] = 1
    return InformationProfile(
        n_docs=n_docs, df=df, pair_df=pair_df, df_threshold=1,
        calibration_lemma="<df is REPORTED ONLY, never gated>",
        excluded_open_class=[], pmi_floor=0.0,
        pmi_calibration={"status": "FLOOR_UNUSED_pmi_is_the_weight_not_a_gate"})


def _assert_streamed_profile_matches_build_profile(sample_docs: List[List[str]]) -> int:
    """PROOF that streamed_profile() is the organ's build_profile(), not a parallel measure."""
    docs = sample_docs[:400]
    ref = build_profile(docs, track_pairs=True)
    wf = {d[0]: d[1:] for d in docs}
    fdf: Dict[str, int] = {}
    for d in docs:
        for ft in d[1:]:
            fdf[ft] = fdf.get(ft, 0) + 1
    mine = streamed_profile(len(docs), fdf, wf)
    n = 0
    for c, feats in wf.items():
        for ft in feats:
            a, b = ref.pmi(c, ft), mine.pmi(c, ft)
            if not (abs(a - b) < 1e-12):
                raise AssertionError(
                    "STREAMED-PROFILE MISMATCH on (%r,%r): build_profile=%r streamed=%r"
                    % (c, ft, a, b))
            n += 1
    if n == 0:
        raise AssertionError("STREAMED-PROFILE CHECK VACUOUS: 0 (concept,feature) pairs compared")
    return n


def _assert_pmi_reduction(prof: InformationProfile, word_feats: Dict[str, Sequence[str]],
                          feat_df: Dict[str, int]) -> None:
    """Assert the organ's pmi() reduces to log2(n_docs/df_f) -- the pre-reg's analytic claim."""
    checked = 0
    for c, feats in word_feats.items():
        for ft in feats:
            expect = math.log(prof.n_docs / feat_df[ft], 2)
            got = prof.pmi(c, ft)
            if not (abs(expect - got) < 1e-9):
                raise AssertionError("PMI REDUCTION VIOLATED on (%r,%r): expected %r got %r"
                                     % (c, ft, expect, got))
            checked += 1
            if checked >= 5000:
                return
    if checked == 0:
        raise AssertionError("PMI REDUCTION CHECK VACUOUS: nothing compared")


# ---------------------------------------------------------------------------------------------
# Supplies
# ---------------------------------------------------------------------------------------------
class Supply:
    """One feature supply plus its distinctiveness weights and its FHRR feature geometry."""

    def __init__(self, name: str, word_feats: Dict[str, List[str]], weights: Dict[str, float],
                 n_dim: int, feature_seed: int, feature_vecs: Optional[Dict[str, torch.Tensor]],
                 phases: Optional[torch.Tensor], feat_index: Optional[Dict[str, int]]):
        self.name = name
        self.word_feats = word_feats
        self.weights = weights
        self.n_dim = n_dim
        self.feature_seed = feature_seed
        self.feature_vecs = feature_vecs      # supply A: the LIVE module's own vectors
        self.phases = phases                  # supply B/C: (n_feat, n_dim) float32
        self.feat_index = feat_index

    def stack(self, feats: Sequence[str]) -> torch.Tensor:
        if self.feature_vecs is not None:
            return torch.stack([self.feature_vecs[t] for t in feats])
        idx = torch.tensor([self.feat_index[t] for t in feats], dtype=torch.long)
        th = self.phases[idx]
        return torch.polar(torch.ones_like(th), th).to(torch.complex64)

    def concept_vector(self, feats: Sequence[str], w: Optional[Dict[str, float]]) -> torch.Tensor:
        """bundle() is called UNMODIFIED; the distinctiveness weighting is applied to the stacked
        feature vectors before the substrate op, which is the ONE variable of this cell."""
        feats = sorted(feats)                          # same order as _concept_vector_from
        stacked = self.stack(feats)
        if w is not None:
            wv = torch.tensor([w[t] for t in feats], dtype=torch.float32)
            stacked = stacked * torch.complex(wv, torch.zeros_like(wv)).unsqueeze(-1)
        return bundle(stacked)


def _build_phases(features: List[str], n_dim: int, seed: int) -> torch.Tensor:
    """Deterministic unit-phase geometry for a large feature vocabulary. Generated in fixed-size
    chunks in sorted-feature order from ONE seeded generator, so the result is reproducible."""
    gen = torch.Generator().manual_seed(seed)
    out = torch.empty((len(features), n_dim), dtype=torch.float32)
    for i in range(0, len(features), PHASE_CHUNK):
        j = min(i + PHASE_CHUNK, len(features))
        out[i:j] = torch.rand((j - i, n_dim), generator=gen) * (2.0 * math.pi)
    return out


def build_supply(name: str, eval_vocab: List[str], cskg_cache: Optional[dict]) -> Supply:
    if name == "A_CONCEPT_FEATURES":
        wf = {w: sorted(CONCEPT_FEATURES[w]) for w in eval_vocab if w in CONCEPT_FEATURES}
        docs = [[c] + sorted(CONCEPT_FEATURES[c]) for c in sorted(CONCEPT_FEATURES)]
        prof = build_profile(docs, track_pairs=True)     # FULL organ path
        feat_df = {}
        for d in docs:
            for ft in d[1:]:
                feat_df[ft] = feat_df.get(ft, 0) + 1
        _assert_pmi_reduction(prof, {d[0]: d[1:] for d in docs}, feat_df)
        weights = {}
        for c, feats in wf.items():
            for ft in feats:
                v = prof.pmi(c, ft)
                if ft in weights and abs(weights[ft] - v) > 1e-9:
                    raise AssertionError("weight not a pure function of the feature: %r" % ft)
                weights[ft] = v
        return Supply(name, wf, weights, N_DIM_A, FEATURE_SEED_A,
                      _feature_vectors(), None, None)

    if cskg_cache is None:
        raise ValueError("supply %r requires the CSKG cache" % name)
    drop_lexrel = (name == "C_CSKG_NOLEXREL")
    wf: Dict[str, List[str]] = {}
    for w in eval_vocab:
        feats = cskg_cache["word_feats"].get(w, [])
        if drop_lexrel:
            feats = [f for f in feats if f.split("|", 1)[0] not in LEXREL_DROP
                     and not f.startswith("/r/dbpedia/")]
        if feats:
            wf[w] = sorted(feats)
    feat_df = cskg_cache["df"]
    prof = streamed_profile(cskg_cache["n_docs"], feat_df, wf)
    _assert_pmi_reduction(prof, wf, feat_df)
    weights = {}
    for c, feats in wf.items():
        for ft in feats:
            weights[ft] = prof.pmi(c, ft)
    feats_sorted = sorted(weights)
    feat_index = {f: i for i, f in enumerate(feats_sorted)}
    phases = _build_phases(feats_sorted, N_DIM_BC, FEATURE_SEED_BC)
    return Supply(name, wf, weights, N_DIM_BC, FEATURE_SEED_BC, None, phases, feat_index)


# ---------------------------------------------------------------------------------------------
# Arms
# ---------------------------------------------------------------------------------------------
def _scrambled_assignment(sup: Supply) -> Dict[str, List[str]]:
    """Permute the word -> feature-set assignment (drill sec 3.3 control 3). Must collapse."""
    words = sorted(sup.word_feats)
    gen = torch.Generator().manual_seed(SCRAMBLE_SEED)
    perm = torch.randperm(len(words), generator=gen).tolist()
    return {words[i]: sup.word_feats[words[perm[i]]] for i in range(len(words))}


def _scrambled_weights(sup: Supply) -> Dict[str, float]:
    """Permute the distinctiveness VALUES across features (the dispatch brief's scramble).
    Feature sets stay intact, so this is expected to land near UNIFORM, NOT near zero -- see
    pre-reg sec 6 'DISCREPANCY BETWEEN THE BRIEF AND THE DRILL'."""
    feats = sorted(sup.weights)
    gen = torch.Generator().manual_seed(SCRAMBLE_SEED + 1)
    perm = torch.randperm(len(feats), generator=gen).tolist()
    return {feats[i]: sup.weights[feats[perm[i]]] for i in range(len(feats))}


def arm_scores(sup: Supply, arm: str,
               pairs: List[Tuple[str, str, float]]) -> Tuple[List[float], List[float]]:
    """Return (scores, golds) over the pairs, in order."""
    if arm == "GROUNDED_CAPPED":
        vals = [grounded_similarity(a, b) for a, b, _ in pairs]
    elif arm == "GROUNDED_RAW":
        vals = [grounded_raw_cos(grounded_vector(a), grounded_vector(b)) for a, b, _ in pairs]
    else:
        if arm == "WEIGHTED":
            wf, w = sup.word_feats, sup.weights
        elif arm == "UNIFORM":
            wf, w = sup.word_feats, None
        elif arm == "SCRAMBLE_ASSIGN":
            wf, w = _scrambled_assignment(sup), sup.weights
        elif arm == "SCRAMBLE_WEIGHTS":
            wf, w = sup.word_feats, _scrambled_weights(sup)
        else:
            raise ValueError("unknown arm %r" % arm)
        cache: Dict[str, torch.Tensor] = {}

        def cv(word: str) -> torch.Tensor:
            if word not in cache:
                cache[word] = sup.concept_vector(wf[word], w)
            return cache[word]

        vals = [_cos_complex(cv(a), cv(b)) for a, b, _ in pairs]
    if any(v is None for v in vals):
        raise AssertionError("arm %r produced a None score on the paired EVAL_SET" % arm)
    return [float(v) for v in vals], [g for _, _, g in pairs]


def analytic_cosine(sup: Supply, weighted: bool,
                    pairs: List[Tuple[str, str, float]]) -> List[float]:
    """Exact weighted cosine over feature-incidence space -- the zero-noise limit of the FHRR
    bundle. Diagnostic only (pre-reg sec 6 item 6); bounds how much of a null result is
    embedding sampling noise rather than mechanism."""
    out = []
    for a, b, _ in pairs:
        fa, fb = set(sup.word_feats[a]), set(sup.word_feats[b])
        if weighted:
            num = sum(sup.weights[f] ** 2 for f in (fa & fb))
            na = math.sqrt(sum(sup.weights[f] ** 2 for f in fa))
            nb = math.sqrt(sum(sup.weights[f] ** 2 for f in fb))
        else:
            num = float(len(fa & fb))
            na, nb = math.sqrt(len(fa)), math.sqrt(len(fb))
        out.append(num / (na * nb) if na > 0 and nb > 0 else 0.0)
    return out


# ---------------------------------------------------------------------------------------------
# Verdict
# ---------------------------------------------------------------------------------------------
def classify_supply(name: str, cov_supply: float, rho: Dict[str, float],
                    n_eval: int) -> Tuple[str, List[str]]:
    """Pre-registered bands, evaluated in the pre-registered order. Pre-reg sec 8."""
    notes: List[str] = []
    if cov_supply < HF_SUPPLY_COVERAGE:
        return "HARD_FAIL_SUPPLY", [
            "cov_supply=%.4f < %.2f: the wall is feature SUPPLY (E2), not metric shape (E1); "
            "redirect to differentia harvesting via hdlab/definitional_extraction.py"
            % (cov_supply, HF_SUPPLY_COVERAGE)]
    d_uni = rho["WEIGHTED"] - rho["UNIFORM"]
    d_gnd = rho["WEIGHTED"] - rho["GROUNDED_RAW"]
    gates = {"rho>=0.35": (rho["WEIGHTED"], HP_RHO_MIN, True),
             "w-uniform>=+0.08": (d_uni, HP_DELTA_UNIFORM, True),
             "w-grounded>=+0.15": (d_gnd, HP_DELTA_GROUNDED, True),
             "scramble_assign<=0.05": (rho["SCRAMBLE_ASSIGN"], HP_SCRAMBLE_MAX, False)}
    all_pass = all((v >= t) if hi else (v <= t) for v, t, hi in gates.values())
    if all_pass:
        thin = [k for k, (v, t, hi) in gates.items()
                if abs(v - t) < BAND_MARGIN_FRAC * max(abs(t), 1e-9)]
        if thin:
            return "MIDDLE_BAND", ["META_RULE_L: cleared %s by <5%% of band width" % thin]
        return "HARD_PASS", notes
    if d_uni < HF_SHAPE_DELTA:
        return "HARD_FAIL_SHAPE", [
            "(WEIGHTED-UNIFORM)=%+.4f < +%.2f: the SHAPE hypothesis is REFUTED; next target is "
            "semantic-control gain (drill E4 -- concept_similarity has no context port)"
            % (d_uni, HF_SHAPE_DELTA)]
    failed = [k for k, (v, t, hi) in gates.items() if not ((v >= t) if hi else (v <= t))]
    return "MIDDLE_BAND", ["gates not met: %s" % failed]


# ---------------------------------------------------------------------------------------------
# Self-test (MANDATORY -- runs at module scope)
# ---------------------------------------------------------------------------------------------
def _instrumentation_selftest() -> dict:
    """Assert every claimed metric is non-null/non-sentinel, that the reused organ is genuinely
    the organ, and that no filter eliminates all items at tiny scale."""
    t0 = time.time()
    res: dict = {}

    # (0) bundle()'s modulator state must be uniform-sum, or feature ORDER would silently matter.
    st = modulators.current()
    assert st.recency == 0, "bundle() would apply recency decay (recency=%r); order would matter" % st.recency
    res["modulator_recency"] = st.recency

    # (1) the reused organ IS the organ: streamed construction == build_profile, on real docs.
    docs = [["dog", "R|animal", "R|pet"], ["cat", "R|animal", "R|pet"],
            ["rock", "R|mineral"], ["stone", "R|mineral"], ["moss", "R|plant"]]
    res["streamed_vs_build_profile_pairs_checked"] = _assert_streamed_profile_matches_build_profile(docs)
    assert res["streamed_vs_build_profile_pairs_checked"] > 0

    # (2) distinctiveness MOVES and is ordered the brain's way: a feature on FEW concepts must
    # outweigh a feature on MANY. This is the mechanism-fires assertion.
    wf = {d[0]: d[1:] for d in docs}
    fdf: Dict[str, int] = {}
    for d in docs:
        for ft in d[1:]:
            fdf[ft] = fdf.get(ft, 0) + 1
    prof = streamed_profile(len(docs), fdf, wf)
    w_shared = prof.pmi("dog", "R|animal")     # df=2
    w_distinct = prof.pmi("moss", "R|plant")   # df=1
    assert w_distinct > w_shared > 0, ("DISTINCTIVENESS NOT ORDERED: distinct=%r shared=%r"
                                       % (w_distinct, w_shared))
    res["w_distinctive"], res["w_shared"] = round(w_distinct, 6), round(w_shared, 6)

    # (3) the live substrate ops are callable and produce non-degenerate values at tiny scale.
    gen = torch.Generator().manual_seed(1)
    fv = {t: unit_phase_vec(64, gen) for t in ("R|animal", "R|pet", "R|mineral", "R|plant")}
    sup = Supply("selftest", wf, {ft: prof.pmi(k, ft) for k, fs in wf.items() for ft in fs},
                 64, 1, fv, None, None)
    v_w = sup.concept_vector(wf["dog"], sup.weights)
    v_u = sup.concept_vector(wf["dog"], None)
    assert v_w.shape == (64,) and v_u.shape == (64,)
    assert torch.isfinite(v_w.real).all() and torch.isfinite(v_w.imag).all(), "NaN/Inf in weighted bundle"
    c_self = _cos_complex(v_w, v_w)
    assert abs(c_self - 1.0) < 1e-4, "cosine of a vector with itself is %r, not 1" % c_self
    assert not torch.equal(v_w, v_u), (
        "META_RULE_AF: WEIGHTED and UNIFORM produced a bit-identical concept vector; the ONE "
        "variable is not actually varying")
    res["selftest_cos_self"] = round(c_self, 6)

    # (4) grounded control is live and non-sentinel.
    g = grounded_similarity("sofa", "couch")
    graw = grounded_raw_cos(grounded_vector("sofa"), grounded_vector("couch"))
    assert g is not None and 0.0 <= g <= GROUNDED_CAP, "grounded control returned %r" % g
    assert graw > g - 1e-9, "GROUNDED_RAW must be >= the capped form (it is the stronger control)"
    res["grounded_capped_sofa_couch"] = round(g, 4)
    res["grounded_raw_sofa_couch"] = round(graw, 4)

    # (5) the benchmark loads and its filters pass >= 1 item.
    pairs = load_simlex()
    assert len(pairs) == 999, "SimLex-999 loaded %d pairs" % len(pairs)
    vocab = sorted({w for p in pairs for w in p[:2]})
    n_cf = sum(1 for a, b, _ in pairs if a in CONCEPT_FEATURES and b in CONCEPT_FEATURES)
    assert n_cf >= 1, "CONCEPT_FEATURES filter eliminated ALL SimLex pairs (instrumentation bug)"
    n_gnd = sum(1 for a, b, _ in pairs if in_grounded_lexicon(a) and in_grounded_lexicon(b))
    assert n_gnd >= 1, "grounded-lexicon filter eliminated ALL SimLex pairs"
    res.update({"simlex_pairs": len(pairs), "simlex_vocab": len(vocab),
                "pairs_both_in_concept_features": n_cf, "pairs_both_in_grounded": n_gnd})

    # (6) spearman is wired and moves (a perfect and an anti-correlated series must differ).
    r_pos = float(spearmanr([1, 2, 3, 4, 5], [1, 2, 3, 4, 5]).statistic)
    r_neg = float(spearmanr([1, 2, 3, 4, 5], [5, 4, 3, 2, 1]).statistic)
    assert abs(r_pos - 1.0) < 1e-9 and abs(r_neg + 1.0) < 1e-9, (r_pos, r_neg)

    # (7) declared validity preflight (F.1/F.2 real-code-path + live-signature binding).
    exercised = {"build_profile", "InformationProfile", "bundle", "unit_phase_vec",
                 "_cos_complex", "grounded_similarity"}
    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["build_profile", "InformationProfile", "bundle",
                                        "unit_phase_vec", "_cos_complex", "grounded_similarity"],
         "exercised_entrypoints": exercised},
        {"kind": "substrate_signature", "callable_obj": build_profile,
         "callable_name": "build_profile", "kwargs": {"doc_lemmas": [], "track_pairs": True}},
        {"kind": "substrate_signature", "callable_obj": bundle, "callable_name": "bundle",
         "kwargs": {"vectors": None}},
        {"kind": "substrate_signature", "callable_obj": grounded_similarity,
         "callable_name": "grounded_similarity", "kwargs": {"word_a": "a", "word_b": "b"}},
        {"kind": "metric_moves", "metric_name": "distinctiveness_weight",
         "before": w_shared, "after": w_distinct},
    ], run_mode="selftest")
    res["validity_preflight_ok"] = bool(ok)
    res["selftest_elapsed_s"] = round(time.time() - t0, 3)
    print("[selftest] PASS %s" % json.dumps(res), flush=True)
    return res


# ---------------------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------------------
def run(run_mode: str, output_dir: str, n_pairs: Optional[int]) -> dict:
    t0 = time.time()
    _write_start_marker(output_dir, run_mode)
    pairs_all = load_simlex(limit=n_pairs)
    vocab = sorted({w for p in pairs_all for w in p[:2]})
    # The CSKG cache is ALWAYS built over the FULL SimLex vocabulary, independent of --pairs, so
    # a smoke and the full run share one cache and exercise the identical data/import chain.
    cskg = get_cskg_cache({w for p in load_simlex() for w in p[:2]})
    _assert_streamed_profile_matches_build_profile(cskg["sample_docs"])

    done = completed_units(output_dir)
    per_supply: Dict[str, dict] = {}
    unit_idx = 0
    for sname in SUPPLIES:
        sup = build_supply(sname, vocab, None if sname == "A_CONCEPT_FEATURES" else cskg)
        cov_pairs = [p for p in pairs_all if p[0] in sup.word_feats and p[1] in sup.word_feats]
        cov_supply = len(cov_pairs) / len(pairs_all)
        eval_pairs = [p for p in cov_pairs
                      if in_grounded_lexicon(p[0]) and in_grounded_lexicon(p[1])]
        cov_eval = len(eval_pairs) / len(pairs_all)
        print("[%s] cov_supply=%.4f (%d/%d)  cov_eval=%.4f (%d)  n_features=%d"
              % (sname, cov_supply, len(cov_pairs), len(pairs_all), cov_eval, len(eval_pairs),
                 len(sup.weights)), flush=True)

        rho: Dict[str, float] = {}
        n_arm: Dict[str, int] = {}
        digests: Dict[str, str] = {}
        for arm in ARMS:
            key = unit_key(sname, arm)
            unit_idx += 1
            if key in done:
                r = load_units(output_dir)[key]
                rho[arm], n_arm[arm], digests[arm] = r["rho"], r["n"], r["digest"]
                print("[%s|%s] resumed rho=%.4f" % (sname, arm, r["rho"]), flush=True)
                continue
            if not eval_pairs:
                r = {"rho": float("nan"), "n": 0, "digest": "EMPTY_EVAL_SET",
                     "failure_class": "EMPTY_EVAL_SET"}
            else:
                scores, golds = arm_scores(sup, arm, eval_pairs)
                arr = np.asarray(scores, dtype=np.float64)
                sd = float(arr.std())
                rv = float(spearmanr(scores, golds).statistic) if sd > 0 else 0.0
                r = {"rho": rv, "n": len(eval_pairs),
                     "digest": hashlib.sha256(arr.tobytes()).hexdigest(),
                     "score_mean": float(arr.mean()), "score_std": sd,
                     "score_min": float(arr.min()), "score_max": float(arr.max()),
                     "failure_class": None}
                if sd == 0.0:
                    r["failure_class"] = "CONSTANT_SCORE_VECTOR"
            record_unit(output_dir, key, r)
            rho[arm], n_arm[arm], digests[arm] = r["rho"], r["n"], r["digest"]
            _heartbeat(output_dir, unit_idx, EXPECTED_N_UNITS, time.time() - t0,
                       {"supply": sname, "arm": arm, "rho": r["rho"]})
            print("[%s|%s] rho=%.4f n=%d" % (sname, arm, r["rho"], r["n"]), flush=True)

        # META_RULE_AF: no two arms may be bit-identical.
        # arms_differ_exempted: (GROUNDED_CAPPED, GROUNDED_RAW) -- one is a clip of the other by
        # construction, so identity between them means only that GROUNDED_CAP never binds on this
        # pair set. That is a reportable fact, not an arm-implementation bug.
        AF_EXEMPT = {("GROUNDED_CAPPED", "GROUNDED_RAW")}
        seen: Dict[str, str] = {}
        for arm, d in sorted(digests.items()):
            if d in seen and d != "EMPTY_EVAL_SET":
                pair = tuple(sorted((seen[d], arm)))
                if pair not in AF_EXEMPT:
                    raise AssertionError(
                        "META_RULE_AF VIOLATION: arms %r and %r bit-identical (%s)"
                        % (seen[d], arm, d))
            seen[d] = arm

        diag = {}
        if eval_pairs:
            golds = [g for _, _, g in eval_pairs]
            for tag, wgt in (("analytic_weighted", True), ("analytic_uniform", False)):
                v = analytic_cosine(sup, wgt, eval_pairs)
                diag[tag + "_rho"] = (float(spearmanr(v, golds).statistic)
                                      if float(np.std(v)) > 0 else 0.0)
            # Did the weighting have ROOM to act? Dynamic range of the distinctiveness weights
            # over the features that are actually SHARED between an evaluated pair (only shared
            # features enter the similarity numerator). A narrow range here means a null delta is
            # expected by construction and says nothing about the brain's mechanism.
            shared_w: List[float] = []
            for a, b, _ in eval_pairs:
                for f in (set(sup.word_feats[a]) & set(sup.word_feats[b])):
                    shared_w.append(sup.weights[f])
            allw = np.asarray(sorted(sup.weights.values()), dtype=np.float64)
            diag["weight_all_p05"] = float(np.percentile(allw, 5))
            diag["weight_all_p50"] = float(np.percentile(allw, 50))
            diag["weight_all_p95"] = float(np.percentile(allw, 95))
            if shared_w:
                sw = np.asarray(shared_w, dtype=np.float64)
                diag["weight_shared_p05"] = float(np.percentile(sw, 5))
                diag["weight_shared_p50"] = float(np.percentile(sw, 50))
                diag["weight_shared_p95"] = float(np.percentile(sw, 95))
                diag["weight_shared_ratio_p95_p05"] = float(
                    np.percentile(sw, 95) / max(np.percentile(sw, 5), 1e-9))
                diag["n_shared_feature_incidences"] = len(shared_w)
        verdict, notes = classify_supply(sname, cov_supply, rho, len(eval_pairs))
        if sname == "A_CONCEPT_FEATURES" and verdict == "HARD_PASS":
            verdict = "HARD_PASS_VOID_OWN_LEXICON"      # pre-reg sec 4, enforced in code
            notes.append("VOID: CONCEPT_FEATURES is constructed so synonyms share nearly all "
                         "tags; a HARD_PASS on our own lexicon carries no evidential weight.")
        per_supply[sname] = {
            "verdict": verdict, "notes": notes, "cov_supply": cov_supply, "cov_eval": cov_eval,
            "n_eval_pairs": len(eval_pairs), "n_covered_pairs": len(cov_pairs),
            "n_features": len(sup.weights), "n_words_with_features": len(sup.word_feats),
            "n_dim": sup.n_dim, "rho": {k: round(v, 4) for k, v in rho.items()},
            "delta_weighted_minus_uniform": round(rho["WEIGHTED"] - rho["UNIFORM"], 4),
            "delta_weighted_minus_grounded_raw": round(rho["WEIGHTED"] - rho["GROUNDED_RAW"], 4),
            "diagnostics": {k: round(v, 4) for k, v in diag.items()},
            "arm_digests": digests, "external_supply": sname != "A_CONCEPT_FEATURES",
            "se_rho_approx": round(1.0 / math.sqrt(max(len(eval_pairs) - 1, 1)), 4),
        }
        del sup

    units = load_units(output_dir)
    cardinality_ok = len(units) >= EXPECTED_N_UNITS
    headline = per_supply["C_CSKG_NOLEXREL"]["verdict"]
    if not cardinality_ok:
        headline = "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H"
    msg = ("A(own lexicon, VOID by construction)=%s cov=%.3f | B(CSKG)=%s cov=%.3f rho_w=%.3f "
           "d_uni=%+.3f | C(CSKG no-lexrel, STRICTEST)=%s cov=%.3f rho_w=%.3f d_uni=%+.3f"
           % (per_supply["A_CONCEPT_FEATURES"]["verdict"],
              per_supply["A_CONCEPT_FEATURES"]["cov_supply"],
              per_supply["B_CSKG"]["verdict"], per_supply["B_CSKG"]["cov_supply"],
              per_supply["B_CSKG"]["rho"]["WEIGHTED"],
              per_supply["B_CSKG"]["delta_weighted_minus_uniform"],
              per_supply["C_CSKG_NOLEXREL"]["verdict"],
              per_supply["C_CSKG_NOLEXREL"]["cov_supply"],
              per_supply["C_CSKG_NOLEXREL"]["rho"]["WEIGHTED"],
              per_supply["C_CSKG_NOLEXREL"]["delta_weighted_minus_uniform"]))
    metrics = {
        "verdict": headline, "verdict_msg": msg,
        "summary": "distinctiveness-weighted bundling vs uniform on held-out SimLex-999",
        "elapsed_s": round(time.time() - t0, 3), "run_mode": run_mode,
        "anchor_name": ANCHOR_NAME, "prereg": PREREG_PATH,
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_units": len(units), "expected_n_units": EXPECTED_N_UNITS,
        "cardinality_ok": cardinality_ok, "arms_differ_verified": True,
        "n_simlex_pairs_used": len(pairs_all),
        "bands": {"HP_RHO_MIN": HP_RHO_MIN, "HP_DELTA_UNIFORM": HP_DELTA_UNIFORM,
                  "HP_DELTA_GROUNDED": HP_DELTA_GROUNDED, "HP_SCRAMBLE_MAX": HP_SCRAMBLE_MAX,
                  "HF_SHAPE_DELTA": HF_SHAPE_DELTA, "HF_SUPPLY_COVERAGE": HF_SUPPLY_COVERAGE},
        "public_calibration_not_arms": CALIBRATION,
        "per_supply": per_supply, "units": units,
    }
    _atomic_write_metrics(output_dir, metrics)
    print("[verdict] %s -- %s" % (headline, msg), flush=True)
    return metrics


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-mode", default="full", choices=("full", "smoke", "self_test"))
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--pairs", type=int, default=None)
    args = ap.parse_args()
    mode = "self_test" if args.self_test else args.run_mode
    if mode == "self_test":
        os.makedirs(OUT_SELFTEST, exist_ok=True)
        _atomic_write_metrics(OUT_SELFTEST, {
            "verdict": "SELFTEST_PASS", "verdict_msg": "module-import self-test ran successfully",
            "summary": "self_test", "elapsed_s": 0.0, "run_mode": "self_test",
            "selftest": _SELFTEST_RESULT})
        return
    if mode == "smoke":
        for n in SMOKE_PAIR_SCALES:          # multi-scale smoke
            out = OUT_SMOKE + "_p%d" % n
            print("=== SMOKE at %d pairs -> %s ===" % (n, out), flush=True)
            m = run("smoke", out, n)
            # DISCRIMINATOR-FIRES. Scoped to the supplies where the TREATMENT actually carries
            # signal: a scramble control exists to prove an OBSERVED signal is earned, so where
            # the treatment is itself at the floor there is nothing for it to falsify and the
            # assertion would be mis-specified rather than informative. At least one supply MUST
            # carry signal, or the whole smoke is vacuous.
            # DISCLOSURE: the first smoke asserted this on C_CSKG_NOLEXREL specifically and it
            # raised, because C's own WEIGHTED rho sits at the scramble floor. Rescoping does NOT
            # touch any pre-registered band (pre-reg sec 8) and cannot turn a FAIL into a PASS --
            # the verdict was HARD_FAIL_SHAPE before and after.
            fired = []
            for sname, c in m["per_supply"].items():
                if c["n_eval_pairs"] == 0:
                    continue
                if c["rho"]["UNIFORM"] == c["rho"]["WEIGHTED"]:
                    raise AssertionError("VACUOUS SMOKE: %s WEIGHTED and UNIFORM rho identical"
                                         % sname)
                if c["rho"]["WEIGHTED"] < 0.20:
                    print("[smoke] %s: NO_SIGNAL_TO_FALSIFY (rho_WEIGHTED=%.4f at floor); "
                          "scramble assertion not applicable"
                          % (sname, c["rho"]["WEIGHTED"]), flush=True)
                    continue
                rho_scr = c["rho"]["SCRAMBLE_ASSIGN"]
                if not (rho_scr <= HP_SCRAMBLE_MAX or rho_scr < c["rho"]["WEIGHTED"] - 0.10):
                    raise AssertionError(
                        "VACUOUS SMOKE: %s SCRAMBLE_ASSIGN rho=%.4f did not collapse against "
                        "WEIGHTED rho=%.4f at %d pairs; the discriminator does not fire."
                        % (sname, rho_scr, c["rho"]["WEIGHTED"], n))
                fired.append(sname)
            if not fired:
                raise AssertionError(
                    "VACUOUS SMOKE at %d pairs: no supply carried signal above the floor, so the "
                    "scramble control was never exercised anywhere." % n)
            print("[smoke] discriminator fired on: %s" % fired, flush=True)
        print("SMOKE=PASS (all scales, discriminator fires)", flush=True)
        return
    run("full", OUT_FULL, args.pairs)


_SELFTEST_RESULT = _instrumentation_selftest()      # called at module scope, before any sweep

if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as _e:                          # NOT BaseException
        _out = OUT_SMOKE if "--run-mode" in sys.argv and "smoke" in sys.argv else OUT_FULL
        _write_crash_metrics(_out, _e)
        raise
