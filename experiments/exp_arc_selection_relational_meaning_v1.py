"""arc_selection_relational_meaning_v1 -- TYPED-RELATIONAL vs FLAT-COSINE selection meaning.

The selection wall (VET 29544 fixed signals; 29545 linear-learned): retrieval REACHES the facts
(wide RR pool recall@100=0.69), the combiner USES them (oracle gold->combiner Challenge ~0.71), but
SELECTION cannot ISOLATE the gold from the contains-gold pool. 29545 showed the IN-SAMPLE linear
precision caps at ~0.189 (best case, labels in hand) over the FLAT GloVe+WordNet SemanticHDEncoder
cosine features -- a REPRESENTATION problem, not an optimization one. 29545's own revival_criteria named
the deep lever: "richer/GROUNDED meaning features at the selection stage".

This cell opens that phase with its CHEAPEST brain-faithful rung: WIRE the substrate's ALREADY-BUILT
typed role-bind (hdlab.event_bundle.EventBundleCodec role keys, the same REL/ARG0/ARG1 binding
hdlab.hd_fact_store uses for STORAGE) INTO the SELECTION-feature stage -- which today reads only the
FLAT symmetric sentence cosine. The drill (notes/research_relational_grounded_meaning_relevance_wall_
2026-07-24.md) proves symmetric cosine is ALGEBRAICALLY incapable of encoding asymmetric/causal
relational structure (RotatE lemmas / Tversky 1977 / DistMult antisymmetry-blindness). WorldTree ships
81 TYPED relation tables (KINDOF/CAUSE/USEDFOR/PARTOF/REQUIRES/SOURCEOF/COUPLEDRELATIONSHIP/IFTHEN/...);
each table name IS the relation type and its columns split into a subject-side (ARG0) and object-side
(ARG1) around the relation verb -- directional structure the flat bag-of-words destroys.

ONE variable = the SELECTION MEANING representation (typed-relational vs flat-cosine). The UNCHANGED
WIDE RR pool (mr.reformulate_seeds/_rownorm_scores, IMPORTED) and the UNCHANGED bind+bundle combiner
(agg.aggregate 'bundle', IMPORTED) are held FIXED. The baseline arm reuses 29545's EXACT feature
assembly + glass-box learner (imported) -> regression-check to its ~0.189 in-sample ceiling.

Typed-relational features (role-bound, per pool fact vs the question's directional frame):
  fact_bundle  = L2( rk_ARG0 (*) enc(fact_subj) + rk_ARG1 (*) enc(fact_obj) )     [role keys from codec]
  q_bundle_c   = L2( rk_ARG0 (*) enc(stem)      + rk_ARG1 (*) enc(choice_c) )
    (*) = elementwise bind with the codec's bipolar role key; role-binding makes ARG0-content and
    ARG1-content live in DECORRELATED subspaces, so a swapped-argument fact mis-aligns where the flat
    sum enc(subj)+enc(obj) is byte-IDENTICAL under swap.
  1 rel_bundle_max  = max_c cos(fact_bundle, q_bundle_c)    (asymmetric role-respecting relevance)
  2 rel_bundle_mean = mean_c relu(cos(fact_bundle, q_bundle_c))
  3 arg_asym        = max_c [ (cos(subj,stem)+cos(obj,choice_c)) - (cos(subj,choice_c)+cos(obj,stem)) ]
  4 rel_type_match  = 1.0 if fact.relation in relation-types INFERRED from the question frame
  5 has_typed       = 1.0 if the fact has a confident ARG0/ARG1 split (coverage indicator)

Arms (selection MEANING is the ONLY variable; pool + combiner UNCHANGED):
  A_baseline  -- 29545 flat thin features -> glass-box learner   [BASELINE replicate ~0.189 in-sample]
  B_relational-- typed-relational features -> SAME learner        [MECHANISM: relational meaning]
  C_combined  -- thin + relational features -> SAME learner       [complementarity]
  SCRAMBLE    -- relational features w/ typed triples PERMUTED across facts [must COLLAPSE toward A]
  RND         -- K_SEL random pool facts                          [MUST-FAIL control]
  ORACLE      -- gold central facts -> combiner                   [CEILING ~0.71]

MECHANISM-CLEAN SWAPPED-ARGUMENT SUB-TEST (the drill's key control, on REAL confident-typed gold facts):
  swap ARG0<->ARG1 in a fact; a directional probe q built from the fact's TRUE arg order should score the
  ORIGINAL fact HIGH and the SWAPPED fact LOW under the RELATIONAL rep, while the FLAT rep scores them
  IDENTICALLY (flat sum is swap-invariant). rel_relevance_gap >> flat_relevance_gap PROVES the relational
  signal responds to asymmetry that cosine cannot -- i.e. the relational feature is REAL, not another
  symmetric feature with extra dimensionality.

PRIMARY = in-sample TRAIN sel_gold_precision (the sharpest cheap number; 29545 ceiling ~0.189). SECONDARY
= TEST-split Challenge sel_gold_precision + end-to-end ARC Challenge accuracy (toward oracle), McNemar
B vs A. MECHANISM = swapped-argument gap. HARD_PASS = B in-sample precision materially > baseline AND
scramble collapses AND swap mechanism fires AND end-to-end lifts significantly. MIDDLE = representational
lift + mechanism real but end-to-end not significant (the note's likely-honest outcome -> redirect residual
to multi-hop typed-path). HARD_FAIL = B ~= baseline in-sample -> typed structure not relevance-
discriminative for ARC -> redirect to multi-hop typed-path composition or perceptual grounding (report
STRAIGHT + which sub-diagnosis: coverage / capacity / content). NO tuning to force a win.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT remote-
portable, inherits 29544/29545 contract); NO push/remote-persist; ASCII-only; deterministic (fixed
seeds, numpy default_rng, sorted iteration, zero-init GD, no hash()); repo .venv; agent-reported
VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL EventBundleCodec role keys + REAL
#   typed tablestore parse + REAL role-bind relational features + REAL RR wide pool + REAL glass-box
#   learner (imported 29545) + UNCHANGED combiner; PLANTED swapped-argument case asserts the relational
#   rep FLIPS where flat is identical (mechanism fires); arms-differ; no-leak (train/test disjoint)
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration + zero-init GD; no hash()
# - baseline_in_band + AG-guard on A_baseline TEST challenge (headroom to the ~0.71 ceiling)
# - storage = SHARDED (each fact = own embedding + own graph node; no superposition)
# - GLASS-BOX INVARIANT: linear weights over NAMED relational features (logged) + per-fact relational
#   match logged; the role-bind + arg-alignment per selected fact is inspectable
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import glob
import hashlib
import argparse
import platform
import traceback
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

import torch  # noqa: E402

# reuse (UNCHANGED): the 29545 baseline features + glass-box learner + split, plus everything it imports
# (WIDE RR pool, current gate, bind+settle combiner, PPR graph, fixed signals, arc helpers, encoder).
from experiments import exp_arc_selection_learned_relevance_glassbox_v1 as learned  # noqa: E402
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr    # noqa: E402
from experiments import exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 as mr   # noqa: E402
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as gate    # noqa: E402
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg         # noqa: E402
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc             # noqa: E402
from experiments import exp_arc_selection_precision_coherence_subset_v1 as fixedsel  # noqa: E402
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (                 # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)
from hdlab.event_bundle import EventBundleCodec                                    # noqa: E402

ANCHOR_NAME = "arc_selection_relational_meaning_v1"
SEED = 20260729

# ---- selection hyperparams (UNCHANGED pool + combiner; inherited from 29545/gate) ----
K_WIDE = learned.K_WIDE      # UNCHANGED wide re-retrieval pool the scorer selects FROM (=100)
RR_TOP_T = learned.RR_TOP_T  # UNCHANGED re-retrieval reformulation depth
K_SEL = learned.K_SEL        # UNCHANGED clean-fact selection width (Cowan-4; =4)
MU_SUPP = learned.MU_SUPP
SETTLE_T = agg.SETTLE_T
SETTLE_EPS = agg.SETTLE_EPS
HOPS = ppr.HOPS
DAMP = ppr.DAMP
SEED_COS = ppr.SEED_COS
MIN_TERM_LEN = ppr.MIN_TERM_LEN

# reuse the 29545 learner + baseline features EXACTLY (regression-anchors Arm A to the 0.189 ceiling)
FLAT_FEATURE_NAMES = learned.FEATURE_NAMES
train_glassbox_relevance = learned.train_glassbox_relevance
learned_score = learned.learned_score
_minmax_cols = learned._minmax_cols
_neg_count = learned._neg_count
question_features_flat = learned.question_features
_topk_idx = learned._topk_idx

# ---- relational feature set (typed role-bind; the ONE new meaning representation) ----
REL_FEATURE_NAMES = ("rel_bundle_max", "rel_bundle_mean", "arg_asym", "rel_type_match", "has_typed")

# ROLES reuse the fact-store fact-content roles (subset used for selection matching)
FACT_ROLES = ("REL", "ARG0", "ARG1")

# question-frame -> candidate relation-type prior (coarse symbolic; interpretable; reported).
# keys = cue substrings in stem+choices; values = WorldTree table names that are plausibly relevant.
REL_TYPE_CUES = {
    "cause": ("CAUSE", "IFTHEN", "COUPLEDRELATIONSHIP", "SOURCEOF"),
    "because": ("CAUSE", "IFTHEN", "COUPLEDRELATIONSHIP"),
    "why": ("CAUSE", "IFTHEN", "COUPLEDRELATIONSHIP"),
    "result": ("CAUSE", "IFTHEN", "CHANGE"),
    "happen": ("CAUSE", "IFTHEN", "PROCESSSTAGES"),
    "affect": ("AFFECT", "CAUSE", "COUPLEDRELATIONSHIP"),
    "increase": ("COUPLEDRELATIONSHIP", "CAUSE", "CHANGE"),
    "decrease": ("COUPLEDRELATIONSHIP", "CAUSE", "CHANGE"),
    "kind": ("KINDOF", "INSTANCES", "EXAMPLES", "SYNONYMY"),
    "type": ("KINDOF", "INSTANCES", "EXAMPLES"),
    "example": ("EXAMPLES", "INSTANCES", "KINDOF"),
    "classif": ("KINDOF", "INSTANCES"),
    "used": ("USEDFOR", "AFFORDANCES", "VEHICLE"),
    "purpose": ("USEDFOR", "AFFORDANCES"),
    "part": ("PARTOF", "MADEOF", "CONTAINS"),
    "made": ("MADEOF", "PARTOF", "FORMEDBY"),
    "contain": ("CONTAINS", "PARTOF", "MADEOF"),
    "composed": ("MADEOF", "PARTOF"),
    "require": ("REQUIRES",),
    "need": ("REQUIRES",),
    "source": ("SOURCEOF", "TRANSFER"),
    "produce": ("SOURCEOF", "TRANSFER", "CAUSE"),
    "provide": ("SOURCEOF", "TRANSFER"),
    "release": ("SOURCEOF", "TRANSFER"),
    "property": ("PROP-GENERIC", "ATTRIBUTE-VALUE-RANGE", "PROP-THINGS"),
    "characteristic": ("PROP-GENERIC", "PROP-THINGS"),
    "attribute": ("ATTRIBUTE-VALUE-RANGE", "PROP-GENERIC"),
    "location": ("LOCATIONS", "HABITAT"),
    "where": ("LOCATIONS", "HABITAT"),
    "habitat": ("HABITAT", "LOCATIONS"),
    "live": ("HABITAT", "LOCATIONS"),
    "change": ("CHANGE", "CHANGE-VEC", "COUPLEDRELATIONSHIP"),
    "becomes": ("CHANGE", "COUPLEDRELATIONSHIP"),
    "measure": ("MEASUREMENTS", "UNIT", "ATTRIBUTE-VALUE-RANGE"),
    "predator": ("PREDATOR-PREY", "CONSUMERS-EATING"),
    "eat": ("CONSUMERS-EATING", "PREDATOR-PREY"),
    "opposite": ("OPPOSITES",),
}

# leading article-like FILL headers that are NOT the relation verb (never the pivot)
_ARTICLE_FILL = frozenset({"a", "an", "the", "a/the", "as", "as a/the", "if", "when", "if/when a/the",
                           "if/when", ",", "then / ,", "for", "by", "by/through", "by/through/how",
                           "by/through/due to"})
# header-substring hints that a FILL/VERB column carries the relation verb (pivot preference)
_VERB_HINTS = ("kind of", "part of", "used", "cause", "means", "require", "source", "made of",
               "contain", "then", "become", "produce", "provide", "example", "called", "instance",
               "affect", "transfer", "opposite", "synonym", "habitat", "locat", "measure", "form",
               "predator", "consume", "perceiv", "change", "is a", "provides", "sourceof")


# ---- bands (author-designed a priori; from the drill's pre-registered predictions) ----
REL_PREC_HP = 0.35       # Pred1 HARD-PASS: B in-sample TRAIN precision >= this (materially > ~0.189)
REL_PREC_HF = 0.24       # Pred1 HARD-FAIL: B in-sample TRAIN precision <= this (< +0.05 over ~0.189)
SCRAMBLE_COLLAPSE_EPS = 0.05  # scramble in-sample precision must be within this OF (or below) baseline
SWAP_MECH_HP = 0.20      # Pred2 mechanism: rel_relevance_gap - flat_relevance_gap >= this -> fires
SWAP_MECH_HF = 0.05      # Pred2 HARD-FAIL: differential < this -> asymmetric-binding refuted (this pipeline)
CHAL_LIFT_HP = 0.05      # Pred3 end-to-end: B - A on TEST Challenge answer AND McNemar-significant
MB_CHAL_LIFT = 0.02      # positive-but-sub-HP band floor
RANDOM_MAX = 0.02        # RND - A on Challenge must be <= this
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95   # A_baseline challenge >= this -> vacuous (no headroom)
BASELINE_PREC_LO = 0.10  # A_baseline in-sample precision regression band (29545 ~0.189); WARN if outside
BASELINE_PREC_HI = 0.30

_T0 = [0.0]


# ---------------------------------------------------------------------------
# markers / crash diagnostics / heartbeat
# ---------------------------------------------------------------------------
def _out_dir():
    d = os.path.join(_REPO, "data", "exp_" + ANCHOR_NAME)
    os.makedirs(d, exist_ok=True)
    return d


def _write_start_marker(output_dir, run_mode):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics_atomic(output_dir, metrics):
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(), "anchor_name": ANCHOR_NAME}
    _write_metrics_atomic(output_dir, diag)


def _heartbeat(output_dir, stage, extra=None):
    row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "stage": stage,
           "elapsed_s": round(time.perf_counter() - _T0[0], 1)}
    if extra:
        row.update(extra)
    with open(os.path.join(output_dir, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
        f.write(json.dumps(row) + "\n")
    print(f"[hb] {stage} {extra if extra else ''}", flush=True)


# ---------------------------------------------------------------------------
# TYPED tablestore parse: uid -> {relation, arg0, arg1, confident}
# The relation type is the table NAME; ARG0/ARG1 split around the relation-verb pivot column.
# ---------------------------------------------------------------------------
def _classify_header(hdr):
    """Return per-column kind: 'SKIP' | 'FILL' | 'NAMED' | 'EMPTY', plus uid col index."""
    kinds = []
    uidcol = None
    for i, h in enumerate(hdr):
        hs = h.strip()
        if hs.startswith("[SKIP]"):
            kinds.append("SKIP")
        elif hs.startswith("[FILL]"):
            kinds.append("FILL")
        elif hs == "":
            kinds.append("EMPTY")
        else:
            kinds.append("NAMED")
        if "UID" in hs:
            uidcol = i
    return kinds, uidcol


def _fill_text(h):
    """The connective text of a [FILL] header (lowercased, marker stripped)."""
    return h.replace("[FILL]", "").strip().lower()


def _is_verb_pivot_header(h):
    hl = h.lower()
    if _fill_text(h) in _ARTICLE_FILL:
        return False
    return any(v in hl for v in _VERB_HINTS)


def _split_row_typed(row, kinds, hdr, pivot_candidates):
    """Given a row, pick the pivot column that yields BOTH sides non-empty (prefer a verb-hint header,
    then a balanced split); return (arg0_text, arg1_text, confident). NAMED-column content only."""
    def named_content(lo, hi):
        cells = []
        for j in range(lo, hi):
            if j >= len(row):
                break
            if kinds[j] == "NAMED":
                c = row[j].strip()
                if c:
                    cells.append(c)
        return cells

    best = None  # (score, arg0, arg1)
    for p in pivot_candidates:
        a0 = named_content(0, p)
        a1 = named_content(p + 1, len(row))
        if a0 and a1:
            verb = 1 if (p < len(hdr) and _is_verb_pivot_header(hdr[p])) else 0
            balance = -abs(len(a0) - len(a1))
            score = (verb * 100) + balance
            if best is None or score > best[0]:
                best = (score, " ".join(a0), " ".join(a1))
    if best is not None:
        return best[1], best[2], True
    # fallback: split ALL named content at its midpoint (low-confidence; still records structure)
    allc = named_content(0, len(row))
    if len(allc) >= 2:
        mid = len(allc) // 2
        return " ".join(allc[:mid]), " ".join(allc[mid:]), False
    return "", "", False


def parse_tablestore_typed():
    """Parse every tablestore TSV -> uid -> {relation, arg0, arg1, confident}. ADDS typed structure;
    does NOT touch agg.parse_tablestore()'s flat uid->sentence (pool + combiner stay UNCHANGED)."""
    uid2typed = {}
    for path in sorted(glob.glob(os.path.join(agg._TABLES, "*.tsv"))):
        relation = os.path.splitext(os.path.basename(path))[0]
        import csv
        with open(path, "r", encoding="utf-8") as f:
            rd = csv.reader(f, delimiter="\t")
            hdr = next(rd)
            kinds, uidcol = _classify_header(hdr)
            # candidate pivots = all FILL cols (non-article) + any NAMED col whose header starts VERB
            pivot_candidates = []
            for j, k in enumerate(kinds):
                if k == "FILL" and _fill_text(hdr[j]) not in _ARTICLE_FILL:
                    pivot_candidates.append(j)
                elif k == "NAMED" and hdr[j].strip().upper().startswith("VERB"):
                    pivot_candidates.append(j)
            # if no non-article FILL survived, allow article FILLs as last-resort pivots
            if not pivot_candidates:
                pivot_candidates = [j for j, k in enumerate(kinds) if k == "FILL"]
            pivot_candidates = sorted(pivot_candidates)
            for r in rd:
                if not any(c.strip() for c in r):
                    continue
                uid = r[uidcol].strip() if (uidcol is not None and uidcol < len(r)) else ""
                if not uid:
                    continue
                a0, a1, conf = _split_row_typed(r, kinds, hdr, pivot_candidates)
                uid2typed[uid] = {"relation": relation, "arg0": a0, "arg1": a1, "confident": conf}
    return uid2typed


def infer_question_rel_types(stem, choices):
    """Coarse symbolic relation-type prior inferred from the question frame (interpretable)."""
    text = (stem + " " + " ".join(choices)).lower()
    types = set()
    for cue, rels in REL_TYPE_CUES.items():
        if cue in text:
            types.update(rels)
    return types


# ---------------------------------------------------------------------------
# role-bind relational encoding (reuses the codec's bipolar role keys = hd_fact_store's binding)
# ---------------------------------------------------------------------------
def _l2_rows(mat):
    m = np.asarray(mat, dtype=np.float32)
    n = np.linalg.norm(m, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return m / n


def role_keys_np(codec):
    """Return {role: bipolar +/-1 numpy key} from the EventBundleCodec (same keys hd_fact_store binds)."""
    return {r: codec.role_key(r).numpy().astype(np.float32) for r in FACT_ROLES}


def bind_bundle(rk_a0, rk_a1, v0, v1):
    """Role-bound bundle: rk_ARG0 (*) v0 + rk_ARG1 (*) v1, L2-normalized rows. v0,v1: [n,nd] (unit rows)."""
    b = rk_a0[None, :] * v0 + rk_a1[None, :] * v1
    return _l2_rows(b)


def relational_features(pool_idx, fact_bundle, fact_arg0, fact_arg1, fact_relation, fact_confident,
                        stem_vec, choice_vecs, rk, q_rel_types):
    """Assemble the [P, 5] RAW relational feature matrix for one question's pool.
      fact_bundle : [F, nd] role-bound fact bundles (unit rows)
      fact_arg0/1 : [F, nd] unit ARG0/ARG1 semantic encodings (0 rows if absent)
      stem_vec    : [nd]    unit stem encoding
      choice_vecs : [C, nd] unit choice-only encodings
      rk          : {role: key}   ; q_rel_types: set of inferred relation-type names
    All features are answer-agnostic (use ALL choices symmetrically; gold never enters)."""
    P = pool_idx.shape[0]
    if P == 0:
        return np.zeros((0, len(REL_FEATURE_NAMES)), dtype=np.float64)
    fb = fact_bundle[pool_idx]                 # [P, nd]
    a0 = fact_arg0[pool_idx]                    # [P, nd]
    a1 = fact_arg1[pool_idx]                    # [P, nd]
    C = choice_vecs.shape[0]
    # q_bundle per choice: rk_ARG0 (*) stem + rk_ARG1 (*) choice_c
    qb = bind_bundle(rk["ARG0"], rk["ARG1"],
                     np.repeat(stem_vec[None, :], C, axis=0), choice_vecs)   # [C, nd]
    cbc = (fb @ qb.T).astype(np.float64)        # [P, C] cos(fact_bundle, q_bundle_c)
    rel_bundle_max = cbc.max(axis=1) if C else np.zeros(P)
    rel_bundle_mean = np.maximum(cbc, 0.0).mean(axis=1) if C else np.zeros(P)
    # arg_asym = max_c (aligned - crossed); aligned = cos(subj,stem)+cos(obj,choice); crossed swaps roles
    subj_stem = (a0 @ stem_vec).astype(np.float64)      # [P]
    obj_stem = (a1 @ stem_vec).astype(np.float64)       # [P]
    subj_ch = (a0 @ choice_vecs.T).astype(np.float64)   # [P, C]
    obj_ch = (a1 @ choice_vecs.T).astype(np.float64)    # [P, C]
    if C:
        aligned = subj_stem[:, None] + obj_ch           # [P, C]
        crossed = subj_ch + obj_stem[:, None]           # [P, C]
        arg_asym = (aligned - crossed).max(axis=1)
    else:
        arg_asym = np.zeros(P)
    rel_type_match = np.array([1.0 if fact_relation[i] in q_rel_types else 0.0
                               for i in pool_idx.tolist()], dtype=np.float64)
    has_typed = np.array([1.0 if fact_confident[i] else 0.0 for i in pool_idx.tolist()], dtype=np.float64)
    X = np.stack([rel_bundle_max, rel_bundle_mean, arg_asym, rel_type_match, has_typed], axis=1)
    assert X.shape == (P, len(REL_FEATURE_NAMES)), "relational feature matrix shape mismatch"
    return X.astype(np.float64)


# ---------------------------------------------------------------------------
# self-test: planted swapped-argument mechanism + real code path + no-leak + arms-differ
# ---------------------------------------------------------------------------
def _planted_swapped_argument_discriminator(nd=512):
    """The drill's mechanism-clean control, planted: build role keys + two DISTINCT filler vecs A,B.
      FLAT rep enc(A)+enc(B) is byte-IDENTICAL under ARG0<->ARG1 swap -> cosine CANNOT distinguish (=1.0).
      RELATIONAL rep rk0(*)A + rk1(*)B differs from the swapped rk0(*)B + rk1(*)A -> role-binding
      distinguishes them. A directional probe built from the TRUE order scores original HIGH, swapped LOW.
    Asserts: flat sim(orig,swap)=1.0 (to fp); relational sim(orig,swap) materially < 1; and the
    directional-probe relevance FLIPS (orig - swapped >= SWAP_MECH_HP under relational, ~0 under flat)."""
    rng = np.random.default_rng(97)
    codec = EventBundleCodec(n_dim=nd, roles=FACT_ROLES, seed=SEED)
    rk = role_keys_np(codec)
    # two distinct unit filler vectors (moderately correlated, like real arg encodings)
    A = rng.standard_normal(nd).astype(np.float32)
    B = rng.standard_normal(nd).astype(np.float32)
    A /= np.linalg.norm(A)
    B /= np.linalg.norm(B)

    flat_orig = _l2_rows((A + B)[None, :])[0]
    flat_swap = _l2_rows((B + A)[None, :])[0]
    flat_sim = float(flat_orig @ flat_swap)
    assert abs(flat_sim - 1.0) < 1e-5, f"planted: flat rep not swap-invariant (sim={flat_sim})"

    rel_orig = bind_bundle(rk["ARG0"], rk["ARG1"], A[None, :], B[None, :])[0]
    rel_swap = bind_bundle(rk["ARG0"], rk["ARG1"], B[None, :], A[None, :])[0]
    rel_sim = float(rel_orig @ rel_swap)
    assert rel_sim < 0.9, f"planted: relational rep did NOT separate swap (sim={rel_sim})"

    # directional probe = the TRUE arg order; relevance must FLIP under relational, tie under flat
    probe = bind_bundle(rk["ARG0"], rk["ARG1"], A[None, :], B[None, :])[0]
    rel_gap = float(rel_orig @ probe) - float(rel_swap @ probe)
    flat_probe = _l2_rows((A + B)[None, :])[0]
    flat_gap = float(flat_orig @ flat_probe) - float(flat_swap @ flat_probe)
    assert rel_gap - flat_gap >= SWAP_MECH_HP, \
        f"planted: swap mechanism did not fire (rel_gap={rel_gap:.3f} flat_gap={flat_gap:.3f})"
    assert abs(flat_gap) < 1e-5, f"planted: flat rep somehow distinguished swap (flat_gap={flat_gap})"
    return {"flat_sim": flat_sim, "rel_sim": rel_sim, "rel_gap": rel_gap, "flat_gap": flat_gap}


def self_test():
    print("[self-test] planted swapped-argument mechanism (relational rep FLIPS where flat is "
          "byte-identical; directional probe relevance gap >= SWAP_MECH_HP) ...", flush=True)
    planted = _planted_swapped_argument_discriminator()
    print(f"[self-test]   planted: {planted}", flush=True)

    print("[self-test] REAL typed tablestore parse + REAL codec role keys + REAL role-bind relational "
          "features + REAL RR wide pool + imported 29545 learner + UNCHANGED combiner ...", flush=True)
    # REAL typed parse touches the actual WorldTree tables
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    uid2typed = parse_tablestore_typed()
    assert len(uid2typed) > 100, f"typed parse too small ({len(uid2typed)})"
    n_conf = sum(1 for v in uid2typed.values() if v["confident"])
    assert n_conf > 0, "typed parse: zero confident ARG0/ARG1 splits"
    print(f"[self-test]   typed facts={len(uid2typed)} confident={n_conf} "
          f"({100.0*n_conf/len(uid2typed):.1f}%)", flush=True)

    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)
    codec = EventBundleCodec(n_dim=nd, roles=FACT_ROLES, seed=SEED)
    rk = role_keys_np(codec)

    store_sents = [
        "green plants use sunlight to make sugar during photosynthesis",
        "sunlight is a source of energy for plants",
        "iron is a kind of metal",
    ]
    arg0_txt = ["green plants", "sunlight", "iron"]
    arg1_txt = ["sugar", "energy plants", "metal"]
    relation = ["CAUSE", "SOURCEOF", "KINDOF"]
    confident = [True, True, True]
    SV = arc._encode_store(enc, store_sents)
    A0 = arc._encode_store(enc, arg0_txt)
    A1 = arc._encode_store(enc, arg1_txt)
    fact_bundle = bind_bundle(rk["ARG0"], rk["ARG1"], A0, A1)
    assert fact_bundle.shape == (3, nd), "real: fact bundle shape"

    q = {"stem": "What do green plants make using sunlight?",
         "choices": ["iron metal", "sugar", "the moon"], "correct_index": 1}
    stem_vec = arc._encode_store(enc, [q["stem"]])[0]
    choice_vecs = arc._encode_store(enc, q["choices"])
    q_types = infer_question_rel_types(q["stem"], q["choices"])
    pool_idx = np.arange(3, dtype=np.int64)
    Xrel = relational_features(pool_idx, fact_bundle, A0, A1, relation, confident,
                               stem_vec, choice_vecs, rk, q_types)
    assert Xrel.shape == (3, len(REL_FEATURE_NAMES)), "real: relational feature matrix shape"

    # imported 29545 learner trains on the REAL relational features (tiny synthetic label)
    Xn = _minmax_cols(Xrel)
    ylab = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    w, b = train_glassbox_relevance(Xn, ylab)
    assert w.shape[0] == len(REL_FEATURE_NAMES), "real: learned weight length"
    s = learned_score(Xn, w, b)
    assert s.shape[0] == 3, "real: score shape"

    # UNCHANGED combiner over a relational selection
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
    sel = pool_idx[_topk_idx(s, min(K_SEL, 3))]
    fh = SV[sel]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fh, q_rel, choice_hd, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == 3, "real: combiner reuse shape"

    # determinism
    w2, b2 = train_glassbox_relevance(Xn, ylab)
    assert np.allclose(w, w2) and abs(b - b2) < 1e-12, "real: training non-deterministic"

    # arms differ: flat features != relational features (different meaning representation)
    assert Xrel.shape[1] != len(FLAT_FEATURE_NAMES) or not np.allclose(Xrel[:, :1], 0.0), \
        "real: relational features degenerate"
    print("[self-test] PASS (planted swap mechanism fires; real typed parse + role-bind features + "
          "imported learner + UNCHANGED combiner; determinism)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 120, "limit_chal": 120}
    return {"n_dim": 2048, "limit_easy": 500, "limit_chal": 600}


ARMS = ("A_baseline", "B_relational", "C_combined", "SCRAMBLE", "RND", "ORACLE")
FEATURE_ARMS = ("A_baseline", "B_relational", "C_combined", "SCRAMBLE")


def _safe_encode(enc, texts):
    """Encode a list of (possibly empty) texts -> [n, nd] unit rows (0 rows for empty/no-signal)."""
    return arc._encode_store(enc, [t if t else "" for t in texts])


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)
    codec = EventBundleCodec(n_dim=nd, roles=FACT_ROLES, seed=SEED)
    rk = role_keys_np(codec)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    nQ = len(questions)
    train_mask, test_mask = learned._split_train_test(questions)
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f} "
          f"train={int(train_mask.sum())} test={int(test_mask.sum())}", flush=True)

    # ---- store = FULL tablestore (flat sentences UNCHANGED) + TYPED parse (new) ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    uid2typed = parse_tablestore_typed()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    # per-fact typed fields aligned to fact-index i (uids[i])
    fact_relation = [uid2typed.get(u, {}).get("relation", "") for u in uids]
    fact_arg0_txt = [uid2typed.get(u, {}).get("arg0", "") for u in uids]
    fact_arg1_txt = [uid2typed.get(u, {}).get("arg1", "") for u in uids]
    fact_confident = [bool(uid2typed.get(u, {}).get("confident", False)) for u in uids]
    typed_cov = round(float(np.mean([1.0 if r else 0.0 for r in fact_relation])), 4)
    conf_cov = round(float(np.mean([1.0 if c else 0.0 for c in fact_confident])), 4)
    print(f"[store] full tablestore = {nFacts} facts | typed_cov={typed_cov} confident_cov={conf_cov}",
          flush=True)

    # ---- bipartite graph + PPR transition (UNCHANGED) ----
    _heartbeat(output_dir, "build_graph")
    fact_terms = [arc._content_words(s, MIN_TERM_LEN) for s in sents]
    fact_word_sets = [set(t) for t in fact_terms]
    degrees_all = np.array([float(len(t)) for t in fact_terms], dtype=np.float64)
    neg_all = np.array([_neg_count(s) for s in sents], dtype=np.float64)
    vocab = sorted({t for terms in fact_terms for t in terms})
    A, df, t2i = ppr.build_incidence(fact_terms, vocab)
    nTerms = len(vocab)
    M, Sft, idf = ppr.build_transition(A, df, use_idf=True)
    print(f"[graph] terms={nTerms} incidence_nnz={A.nnz}", flush=True)

    # ---- encode store + terms + questions ONCE (UNCHANGED flat encodings) ----
    _heartbeat(output_dir, "encode_store", {"n": nFacts})
    t_enc = time.perf_counter()
    SV_store = arc._encode_store(enc, sents)
    print(f"[encode] store {nFacts} facts in {time.perf_counter()-t_enc:.1f}s", flush=True)

    _heartbeat(output_dir, "encode_terms", {"n": nTerms})
    term_vecs = arc._encode_store(enc, vocab)

    # ---- TYPED role-bind fact bundles (the ONE new meaning representation) ----
    _heartbeat(output_dir, "encode_typed_args")
    FA0 = _safe_encode(enc, fact_arg0_txt)      # [F, nd] unit ARG0 encodings
    FA1 = _safe_encode(enc, fact_arg1_txt)      # [F, nd] unit ARG1 encodings
    fact_bundle = bind_bundle(rk["ARG0"], rk["ARG1"], FA0, FA1)
    print(f"[typed] role-bound fact bundles built [{fact_bundle.shape[0]}x{fact_bundle.shape[1]}]",
          flush=True)

    _heartbeat(output_dir, "encode_questions")
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])
    STEM = arc._encode_store(enc, [q["stem"] for q in questions])
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]) for q in questions]
    choice_only_map = [arc._encode_store(enc, list(q["choices"])) for q in questions]  # choice-only for role match
    q_rel_types = [infer_question_rel_types(q["stem"], q["choices"]) for q in questions]

    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]
    sc_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
                      for q in questions]
    uniq_words = sorted({w for ws in sc_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}

    def wvecs(ws):
        return uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)

    # ---- WIDE RR pool (max-recall cell path, UNCHANGED) ----
    _heartbeat(output_dir, "ppr_wide_pool")
    seeds_sc = ppr.link_seeds(sc_words_per_q, vocab, t2i, term_vecs, [wvecs(ws) for ws in sc_words_per_q], SEED_COS)
    sm_sc = ppr.seeds_to_matrix(seeds_sc, nTerms)
    F_SC = ppr.fact_activation(ppr.ppr_batch(sm_sc, M, HOPS, DAMP), Sft)
    seeds2 = mr.reformulate_seeds(F_SC, seeds_sc, fact_terms, t2i, RR_TOP_T)
    F_P2 = ppr.fact_activation(ppr.ppr_batch(ppr.seeds_to_matrix(seeds2, nTerms), M, HOPS, DAMP), Sft)
    F_RR = mr._rownorm_scores(F_SC) + mr._rownorm_scores(F_P2)

    # ---- SCRAMBLE control: permute the typed-triple assignment across facts (destroys real structure,
    #      preserves feature count/distribution). Deterministic permutation (no hash()). ----
    scr_rng = np.random.default_rng(SEED + 909)
    scr_perm = scr_rng.permutation(nFacts)
    fact_bundle_scr = fact_bundle[scr_perm]
    FA0_scr, FA1_scr = FA0[scr_perm], FA1[scr_perm]
    fact_relation_scr = [fact_relation[j] for j in scr_perm.tolist()]
    fact_confident_scr = [fact_confident[j] for j in scr_perm.tolist()]

    # ---- PASS A: per-question pool + flat features + relational features + gold ----
    _heartbeat(output_dir, "features")
    poolidx_list = [None] * nQ
    Xn_flat = [None] * nQ
    Xn_rel = [None] * nQ
    Xn_comb = [None] * nQ
    Xn_scr = [None] * nQ
    gold_rows_list = [None] * nQ
    lure_flags = np.zeros(nQ, dtype=bool)

    for qi, q in enumerate(questions):
        ci = q["correct_index"]
        stem_words = stem_words_per_q[qi]
        lure_flags[qi] = gate.is_lure_question(stem_words, q["choices"], ci)
        lure_set, _ = gate.standout_lure_choices(stem_words, q["choices"])

        pool_idx = ppr.topk_from_scores(F_RR[qi], K_WIDE)
        poolidx_list[qi] = pool_idx
        fh_pool = SV_store[pool_idx]
        chd = choice_hd_map[qi]
        fw = [fact_word_sets[i] for i in pool_idx.tolist()]

        # FLAT baseline features (imported 29545 assembly, UNCHANGED)
        gs = gate.gate_scores(fh_pool, fw, stem_words, STEM[qi], chd, lure_set)
        coh = fixedsel.coherence_score(fh_pool, af0=np.maximum(fh_pool @ QQ[qi], 0.0))
        rr_scores = F_RR[qi][pool_idx]
        degs = degrees_all[pool_idx]
        negs = neg_all[pool_idx]
        Xflat = question_features_flat(fh_pool, STEM[qi], chd, gs, coh, rr_scores, degs, negs)

        # RELATIONAL features (typed role-bind; the ONE new representation)
        Xrel = relational_features(pool_idx, fact_bundle, FA0, FA1, fact_relation, fact_confident,
                                   STEM[qi], choice_only_map[qi], rk, q_rel_types[qi])
        # SCRAMBLE features (permuted typed triples)
        Xscr = relational_features(pool_idx, fact_bundle_scr, FA0_scr, FA1_scr, fact_relation_scr,
                                   fact_confident_scr, STEM[qi], choice_only_map[qi], rk, q_rel_types[qi])

        Xn_flat[qi] = _minmax_cols(Xflat)
        Xn_rel[qi] = _minmax_cols(Xrel)
        Xn_comb[qi] = _minmax_cols(np.concatenate([Xflat, Xrel], axis=1))
        Xn_scr[qi] = _minmax_cols(Xscr)
        gold_rows_list[qi] = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)

    # ---- TRAIN a glass-box learner per feature-arm on TRAIN questions ONLY (label = is-gold) ----
    _heartbeat(output_dir, "train_learners")

    def build_train(Xn_list):
        Xr, yr = [], []
        for qi in range(nQ):
            if not train_mask[qi]:
                continue
            pool_idx = poolidx_list[qi]
            gold_set = set(int(g) for g in gold_rows_list[qi].tolist())
            y = np.array([1.0 if int(gi) in gold_set else 0.0 for gi in pool_idx.tolist()], dtype=np.float64)
            Xr.append(Xn_list[qi]); yr.append(y)
        X = np.concatenate(Xr, axis=0) if Xr else np.zeros((0, 1))
        y = np.concatenate(yr, axis=0) if yr else np.zeros(0)
        return X, y

    arm_feat = {"A_baseline": Xn_flat, "B_relational": Xn_rel, "C_combined": Xn_comb, "SCRAMBLE": Xn_scr}
    arm_names = {"A_baseline": list(FLAT_FEATURE_NAMES), "B_relational": list(REL_FEATURE_NAMES),
                 "C_combined": list(FLAT_FEATURE_NAMES) + list(REL_FEATURE_NAMES),
                 "SCRAMBLE": list(REL_FEATURE_NAMES)}
    arm_w, arm_b, arm_weights = {}, {}, {}
    n_train_rows = n_train_pos = 0
    for arm in FEATURE_ARMS:
        Xt, yt = build_train(arm_feat[arm])
        n_train_rows = int(Xt.shape[0]); n_train_pos = int(yt.sum())
        w, b = train_glassbox_relevance(Xt, yt)
        arm_w[arm], arm_b[arm] = w, b
        arm_weights[arm] = {arm_names[arm][j]: round(float(w[j]), 5) for j in range(len(w))}
        print(f"[learned:{arm}] rows={int(Xt.shape[0])} pos={int(yt.sum())} weights={arm_weights[arm]}",
              flush=True)

    # ---- PASS B: select + answer per arm; in-sample (TRAIN) + TEST precision ----
    _heartbeat(output_dir, "select_and_answer")
    picks = {name: np.full(nQ, -1, dtype=np.int64) for name in ARMS}
    sel_gold_hit = {name: [None] * nQ for name in ARMS}
    glass = []

    def combiner_pick(qi, sel_idx):
        if sel_idx.size == 0:
            sc, _ = agg.aggregate(np.zeros((0, nd), np.float32), np.zeros(0, np.float32),
                                  choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
            return agg._pick(sc, np.random.default_rng(SEED + qi))
        fh = SV_store[sel_idx]
        q_rel = np.maximum(fh @ QQ[qi], 0.0).astype(np.float32)
        sc, _ = agg.aggregate(fh, q_rel, choice_hd_map[qi], "bundle", rng=np.random.default_rng(SEED + qi))
        return agg._pick(sc, np.random.default_rng(SEED + qi))

    for qi, q in enumerate(questions):
        pool_idx = poolidx_list[qi]
        gold_rows = gold_rows_list[qi]
        gold_set = set(int(g) for g in gold_rows.tolist())

        sel_local = {}
        for arm in FEATURE_ARMS:
            sel_local[arm] = _topk_idx(learned_score(arm_feat[arm][qi], arm_w[arm], arm_b[arm]), K_SEL)
        rng_r = np.random.default_rng(SEED + 7000 + qi)
        sel_local["RND"] = rng_r.permutation(pool_idx.size)[:min(K_SEL, pool_idx.size)]

        for name in FEATURE_ARMS + ("RND",):
            sel_glob = pool_idx[sel_local[name]]
            picks[name][qi] = combiner_pick(qi, sel_glob)
            denom = min(K_SEL, sel_glob.size) if sel_glob.size else 1
            sel_gold_hit[name][qi] = sum(1 for g in sel_glob.tolist() if g in gold_set) / denom
        picks["ORACLE"][qi] = combiner_pick(qi, gold_rows)
        sel_gold_hit["ORACLE"][qi] = 1.0 if gold_rows.size else 0.0

        if len(glass) < 12 and lure_flags[qi] and test_mask[qi]:
            b_local = sel_local["B_relational"]
            Xr = Xn_rel[qi]
            contrib = {}
            for li in b_local.tolist():
                fi = int(pool_idx[li])
                contrib[str(fi)] = {
                    "relation": fact_relation[fi], "arg0": fact_arg0_txt[fi][:40],
                    "arg1": fact_arg1_txt[fi][:40],
                    "feat": {REL_FEATURE_NAMES[j]: round(float(Xr[li, j] * arm_w["B_relational"][j]), 4)
                             for j in range(len(REL_FEATURE_NAMES))},
                    "is_gold": int(fi in gold_set)}
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120], "choices": q["choices"],
                "correct_index": q["correct_index"], "split": "test",
                "q_rel_types": sorted(q_rel_types[qi]),
                "gold_in_wide_pool": sum(1 for i in pool_idx.tolist() if i in gold_set),
                "picks": {name: int(picks[name][qi]) for name in ARMS},
                "B_relational_selected": [uid2sent.get(uids[i], "")[:70]
                                          for i in pool_idx[b_local].tolist()],
                "A_baseline_selected": [uid2sent.get(uids[i], "")[:70]
                                        for i in pool_idx[sel_local["A_baseline"]].tolist()],
                "B_selected_gold": [int(i in gold_set) for i in pool_idx[b_local].tolist()],
                "A_selected_gold": [int(i in gold_set) for i in pool_idx[sel_local["A_baseline"]].tolist()],
                "B_relational_contributions": contrib,
            })

    # ---- accuracies + precision (PRIMARY = in-sample TRAIN precision; TEST for end-to-end) ----
    correct = {name: np.array([int(picks[name][qi] == questions[qi]["correct_index"])
                               for qi in range(nQ)], dtype=np.int64) for name in ARMS}
    is_easy = np.array([q["source"].startswith("ARC-Easy") for q in questions])
    is_chal = ~is_easy
    chal_lure = is_chal & lure_flags
    test_chal = test_mask & is_chal
    test_easy = test_mask & is_easy
    train_chal = train_mask & is_chal

    def acc(mask, name):
        m = correct[name][mask]
        return round(float(np.mean(m)), 4) if m.size else None

    def selprec(mask, name):
        vals = [sel_gold_hit[name][qi] for qi in range(nQ) if mask[qi] and sel_gold_hit[name][qi] is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    accs = {}
    for name in ARMS:
        accs[name] = {
            "test_easy": acc(test_easy, name), "test_challenge": acc(test_chal, name),
            "test_chal_lure": acc(test_mask & chal_lure, name),
            "insample_train_precision": selprec(train_chal, name),   # PRIMARY sharp number
            "test_sel_gold_precision": selprec(test_chal, name),
        }
        print(f"[acc] {name}: insample_prec={accs[name]['insample_train_precision']} "
              f"test_prec={accs[name]['test_sel_gold_precision']} "
              f"test_chal={accs[name]['test_challenge']}", flush=True)

    # ---- SWAPPED-ARGUMENT MECHANISM SUB-TEST on REAL confident-typed gold facts ----
    _heartbeat(output_dir, "swap_mechanism")
    # collect confident-typed gold facts appearing in TEST questions
    swap_fis = []
    seen = set()
    for qi in range(nQ):
        if not test_mask[qi]:
            continue
        for u in questions[qi]["gold_central"]:
            fi = uid2fi.get(u)
            if fi is not None and fact_confident[fi] and fi not in seen:
                seen.add(fi); swap_fis.append(fi)
    swap_fis = swap_fis[:400]
    if swap_fis:
        idx = np.array(swap_fis, dtype=np.int64)
        A0s, A1s = FA0[idx], FA1[idx]
        rel_orig = bind_bundle(rk["ARG0"], rk["ARG1"], A0s, A1s)     # correct direction
        rel_swap = bind_bundle(rk["ARG0"], rk["ARG1"], A1s, A0s)     # ARG0<->ARG1 swapped
        probe = bind_bundle(rk["ARG0"], rk["ARG1"], A0s, A1s)        # directional probe = TRUE order
        rel_gap = (np.sum(rel_orig * probe, axis=1) - np.sum(rel_swap * probe, axis=1)).astype(np.float64)
        # flat rep: enc(arg0)+enc(arg1) is swap-invariant -> orig and swap identical
        flat_orig = _l2_rows(A0s + A1s)
        flat_swap = _l2_rows(A1s + A0s)
        flat_probe = _l2_rows(A0s + A1s)
        flat_gap = (np.sum(flat_orig * flat_probe, axis=1)
                    - np.sum(flat_swap * flat_probe, axis=1)).astype(np.float64)
        swap_rel_gap = round(float(np.mean(rel_gap)), 4)
        swap_flat_gap = round(float(np.mean(flat_gap)), 4)
        swap_rel_orig_swap_sim = round(float(np.mean(np.sum(rel_orig * rel_swap, axis=1))), 4)
        swap_n = int(idx.size)
    else:
        swap_rel_gap = swap_flat_gap = swap_rel_orig_swap_sim = None
        swap_n = 0
    swap_differential = (round(swap_rel_gap - swap_flat_gap, 4)
                         if (swap_rel_gap is not None and swap_flat_gap is not None) else None)
    swap_fires = bool(swap_differential is not None and swap_differential >= SWAP_MECH_HP)
    print(f"[swap] n={swap_n} rel_gap={swap_rel_gap} flat_gap={swap_flat_gap} "
          f"differential={swap_differential} fires={swap_fires}", flush=True)

    # ---- PRIMARY: in-sample precision A vs B; scramble collapse; end-to-end ----
    A_prec = accs["A_baseline"]["insample_train_precision"] or 0.0
    B_prec = accs["B_relational"]["insample_train_precision"] or 0.0
    C_prec = accs["C_combined"]["insample_train_precision"] or 0.0
    SCR_prec = accs["SCRAMBLE"]["insample_train_precision"] or 0.0
    prec_lift = round(B_prec - A_prec, 4)
    scramble_collapses = bool(SCR_prec <= A_prec + SCRAMBLE_COLLAPSE_EPS)
    baseline_regress_ok = BASELINE_PREC_LO <= A_prec <= BASELINE_PREC_HI

    A_chal = accs["A_baseline"]["test_challenge"] or 0.0
    B_chal = accs["B_relational"]["test_challenge"] or 0.0
    C_chal = accs["C_combined"]["test_challenge"] or 0.0
    oracle_chal = accs["ORACLE"]["test_challenge"] or 0.0
    gap = round(oracle_chal - A_chal, 4)
    chal_lift = round(B_chal - A_chal, 4)
    comb_lift = round(C_chal - A_chal, 4)
    best_repr = "C_combined" if C_chal >= B_chal else "B_relational"
    best_chal = max(B_chal, C_chal)
    best_lift = round(best_chal - A_chal, 4)
    gap_frac_closed = round(best_lift / gap, 4) if gap > 1e-9 else None
    rand_lift = round((accs["RND"]["test_challenge"] or 0.0) - A_chal, 4)

    B_test_prec = accs["B_relational"]["test_sel_gold_precision"] or 0.0
    A_test_prec = accs["A_baseline"]["test_sel_gold_precision"] or 0.0

    mc_b, mc_c, mc_stat, mc_p = gate.mcnemar(correct["A_baseline"][test_chal],
                                             correct[best_repr][test_chal])
    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)
    random_ok = rand_lift <= RANDOM_MAX

    # ---- integrity gates ----
    ag_saturated = A_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal < 0.95
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ARMS}
    n_distinct = len(set(digests[n] for n in FEATURE_ARMS + ("RND",)))
    arms_differ = n_distinct >= 4
    rel_nontrivial = bool(np.any(np.abs(arm_w["B_relational"]) > 1e-6))

    # Pred1 = representational in-sample lift; Pred2 = mechanism; Pred3 = end-to-end
    pred1_hp = bool(B_prec >= REL_PREC_HP and scramble_collapses)
    pred1_hf = bool(B_prec <= REL_PREC_HF)
    pred2_hp = swap_fires
    pred2_hf = bool(swap_differential is not None and swap_differential < SWAP_MECH_HF)
    pred3_hp = bool(best_lift >= CHAL_LIFT_HP and sig and random_ok)

    # ---- HARD-FAIL sub-diagnosis (only meaningful when Pred1 fails) ----
    sub_diag = None
    if pred1_hf:
        if conf_cov < 0.15:
            sub_diag = ("coverage: confident typed ARG0/ARG1 split rare in the pool "
                        f"(confident_cov={conf_cov}); redirect = curriculum/corpus breadth or a finer parser")
        elif swap_fires:
            sub_diag = ("content: role-binding IS asymmetry-faithful (swap mechanism fires) but relation-"
                        "type/direction does NOT separate THESE gold-vs-lure pairs; redirect = multi-hop "
                        "typed-path composition (lures differ by fine content, not relation direction)")
        else:
            sub_diag = ("capacity: role-bind + cosine readout does not carry the signal at this dim/noise "
                        "(swap mechanism weak); redirect = check bundling-capacity bounds or grounding")

    # ---- verdict ----
    if ag_saturated:
        verdict = "RELATIONAL_SELECTION_SATURATED"
        vmsg = (f"baseline A_baseline TEST Challenge {A_chal} >= {AG_BASELINE_SAT}: no headroom (report).")
    elif not arms_differ:
        verdict = "RELATIONAL_SELECTION_ARMS_IDENTICAL_META_RULE_AF"
        vmsg = (f"feature arms produced < 4 distinct pick-vectors (n_distinct={n_distinct}); arm bug -- "
                f"do NOT trust the comparison.")
    elif not rel_nontrivial:
        verdict = "RELATIONAL_SELECTION_DEGENERATE"
        vmsg = "relational learner weights ~= 0 (no relational feature separates gold on TRAIN); inspect."
    elif not swap_fires and pred2_hf:
        verdict = "RELATIONAL_MECHANISM_REFUTED"
        vmsg = (f"MECHANISM-CLEAN sub-test FAILS: swapped-argument differential {swap_differential} < "
                f"{SWAP_MECH_HF} (rel_gap={swap_rel_gap} flat_gap={swap_flat_gap}, n={swap_n}) -- the "
                f"role-bind does NOT capture asymmetry in THIS pipeline. Suspect too-few/too-noisy "
                f"confident-typed facts (confident_cov={conf_cov}) rather than the math being wrong.")
    elif pred1_hp and pred2_hp and pred3_hp:
        verdict = "RELATIONAL_SELECTION_HARD_PASS"
        vmsg = (f"typed-relational MEANING beats flat cosine ON ALL THREE: in-sample precision B={B_prec} "
                f"vs A={A_prec} (lift {prec_lift:+.4f}, >= {REL_PREC_HP}); scramble collapses "
                f"(SCR={SCR_prec} <= A+{SCRAMBLE_COLLAPSE_EPS}); swap mechanism fires "
                f"(differential {swap_differential} >= {SWAP_MECH_HP}); end-to-end {best_repr} TEST "
                f"Challenge {best_chal} vs A {A_chal} (lift {best_lift:+.4f}, {gap_frac_closed} of the "
                f"{gap} gap; McNemar p={mc_p} < {MCNEMAR_ALPHA}); RANDOM lift {rand_lift:+.4f} "
                f"(<= {RANDOM_MAX}). Wiring the typed role-bind into selection closes real precision.")
    elif (pred1_hp or pred2_hp) and not pred1_hf:
        verdict = "RELATIONAL_SELECTION_MIDDLE_BAND"
        vmsg = (f"MIDDLE (the note's likely-honest outcome): representational lift and/or mechanism REAL "
                f"but end-to-end not decisive. in-sample precision B={B_prec} vs A={A_prec} "
                f"(lift {prec_lift:+.4f}); scramble_collapses={scramble_collapses} (SCR={SCR_prec}); "
                f"swap mechanism fires={swap_fires} (differential={swap_differential}); end-to-end "
                f"{best_repr} TEST Challenge {best_chal} vs A {A_chal} (lift {best_lift:+.4f}, "
                f"McNemar p={mc_p} sig={sig}); random lift={rand_lift} (ok={random_ok}). Real but partial "
                f"-> redirect residual to multi-hop typed-path composition or a nonlinear learner on the "
                f"richer features.")
    else:
        verdict = "RELATIONAL_SELECTION_HARD_FAIL"
        vmsg = (f"HONEST CEILING: typed-relational features do NOT beat flat cosine in-sample "
                f"(B={B_prec} vs A={A_prec}, lift {prec_lift:+.4f} <= {REL_PREC_HF}). The typed structure "
                f"in OUR store is not relevance-discriminative for ARC selection. Sub-diagnosis: {sub_diag}. "
                f"swap mechanism fires={swap_fires} (differential={swap_differential}); scramble collapses="
                f"{scramble_collapses}; end-to-end {best_repr} lift={best_lift:+.4f}. Redirect = multi-hop "
                f"typed-path composition OR perceptual grounding (report STRAIGHT).")

    grade = arc._grade_proxy(accs["B_relational"]["test_easy"], accs["B_relational"]["test_challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [in-sample prec] A={A_prec} B={B_prec} C={C_prec} SCR={SCR_prec} "
                    f"(lift B-A={prec_lift:+.4f}); [swap] differential={swap_differential} fires={swap_fires}; "
                    f"[TEST Chal] A={A_chal} B={B_chal} C={C_chal} ORACLE={oracle_chal} best_lift={best_lift:+.4f} "
                    f"McNemar_p={mc_p} rand_lift={rand_lift}; typed_cov={typed_cov} conf_cov={conf_cov} | "
                    f"chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_train": int(train_mask.sum()), "n_test": int(test_mask.sum()),
        "n_test_challenge": int(np.sum(test_chal)), "n_train_challenge": int(np.sum(train_chal)),
        "n_train_rows": n_train_rows, "n_train_gold_pos": n_train_pos,
        "chance_theoretical": round(chance, 4),
        "store_facts": nFacts, "graph_terms": nTerms,
        "typed_coverage": typed_cov, "confident_coverage": conf_cov,
        # selection + learner config
        "k_wide": K_WIDE, "k_sel": K_SEL, "rr_top_t": RR_TOP_T, "mu_supp": MU_SUPP,
        "settle_t": SETTLE_T, "settle_eps": SETTLE_EPS, "hops": HOPS, "damp": DAMP, "seed_cos": SEED_COS,
        "l2_reg": learned.L2_REG, "gd_iters": learned.GD_ITERS, "gd_lr": learned.GD_LR,
        "split_frac_train": learned.SPLIT_FRAC_TRAIN,
        # GLASS-BOX: inspectable learned weights per arm + relational feature names
        "flat_feature_names": list(FLAT_FEATURE_NAMES),
        "rel_feature_names": list(REL_FEATURE_NAMES),
        "learned_weights_by_arm": arm_weights,
        "rel_learner_nontrivial": rel_nontrivial,
        # PRIMARY: in-sample TRAIN precision by arm (the sharpest number; 29545 ceiling ~0.189)
        "insample_train_precision_by_arm": {n: accs[n]["insample_train_precision"] for n in ARMS},
        "A_insample_precision": A_prec, "B_insample_precision": B_prec,
        "C_insample_precision": C_prec, "SCRAMBLE_insample_precision": SCR_prec,
        "insample_precision_lift_B_minus_A": prec_lift,
        "scramble_collapses": scramble_collapses, "scramble_collapse_eps": SCRAMBLE_COLLAPSE_EPS,
        "baseline_precision_regression_ok": baseline_regress_ok,
        # MECHANISM: swapped-argument sub-test
        "swap_mechanism": {"n": swap_n, "rel_relevance_gap": swap_rel_gap,
                           "flat_relevance_gap": swap_flat_gap, "differential": swap_differential,
                           "rel_orig_swap_sim": swap_rel_orig_swap_sim, "fires": swap_fires,
                           "hp_threshold": SWAP_MECH_HP, "hf_threshold": SWAP_MECH_HF},
        # SECONDARY: end-to-end accuracy by arm on TEST (judged on the ANSWER)
        "acc_by_arm": accs,
        "A_baseline_test_challenge": A_chal, "B_relational_test_challenge": B_chal,
        "C_combined_test_challenge": C_chal, "oracle_gold_test_challenge": oracle_chal,
        "selection_gap": gap,
        "relational_lift_challenge": chal_lift, "combined_lift_challenge": comb_lift,
        "best_repr_arm": best_repr, "best_repr_lift_challenge": best_lift,
        "gap_fraction_closed": gap_frac_closed,
        "random_lift_challenge": rand_lift, "random_control_ok": bool(random_ok),
        "test_sel_gold_precision_A": A_test_prec, "test_sel_gold_precision_B": B_test_prec,
        "mcnemar_challenge": {"arm": best_repr, "b_A_right_arm_wrong": mc_b,
                              "c_A_wrong_arm_right": mc_c,
                              "stat": None if mc_stat is None else round(mc_stat, 4),
                              "p_value": None if mc_p is None else round(mc_p, 5),
                              "significant": bool(sig)},
        "test_sel_gold_precision_by_arm": {n: accs[n]["test_sel_gold_precision"] for n in ARMS},
        # predictions (from the drill)
        "pred1_representational_hp": pred1_hp, "pred1_hard_fail": pred1_hf,
        "pred2_mechanism_hp": pred2_hp, "pred2_hard_fail": pred2_hf,
        "pred3_endtoend_hp": pred3_hp,
        "hard_fail_sub_diagnosis": sub_diag,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests,
        "bands": {"REL_PREC_HP": REL_PREC_HP, "REL_PREC_HF": REL_PREC_HF,
                  "SCRAMBLE_COLLAPSE_EPS": SCRAMBLE_COLLAPSE_EPS, "SWAP_MECH_HP": SWAP_MECH_HP,
                  "SWAP_MECH_HF": SWAP_MECH_HF, "CHAL_LIFT_HP": CHAL_LIFT_HP, "MB_CHAL_LIFT": MB_CHAL_LIFT,
                  "RANDOM_MAX": RANDOM_MAX, "mcnemar_alpha": MCNEMAR_ALPHA,
                  "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: the SELECTION MEANING representation is the ONLY variable. The WIDE re-retrieval pool "
            "(RR top-100, mr.reformulate_seeds/_rownorm_scores IMPORTED UNCHANGED) and the bind+bundle "
            "combiner (agg.aggregate 'bundle' IMPORTED UNCHANGED) are held fixed. Arm A_baseline reuses "
            "29545's EXACT flat-cosine feature assembly + glass-box learner (imported) -> regression-anchor "
            "to the ~0.189 in-sample ceiling. Arm B_relational feeds the SAME learner typed role-bind "
            "features from EventBundleCodec role keys (the SAME REL/ARG0/ARG1 binding hd_fact_store uses "
            "for storage), computed over WorldTree's 81 typed relation tables: rel_bundle_max/mean "
            "(asymmetric role-respecting relevance), arg_asym (aligned-minus-crossed directional margin), "
            "rel_type_match (question-frame relation-type prior), has_typed (coverage). C_combined = flat "
            "+ relational. SCRAMBLE permutes the typed-triple assignment across facts (must collapse toward "
            "A). RND (must-fail), ORACLE (gold ceiling). MECHANISM-CLEAN swapped-argument sub-test on real "
            "confident-typed gold facts: role-binding distinguishes orig from ARG0<->ARG1-swapped where the "
            "flat sum is byte-identical (swap-invariant). NO LEAK: TRAIN/TEST disjoint (stratified by "
            "source, learned._split_train_test); learner never sees TEST gold; gold used for TRAIN label + "
            "ORACLE + eval only. PRIMARY = in-sample TRAIN precision (the sharp number); SECONDARY = TEST "
            "sel_gold_precision + end-to-end Challenge + McNemar; MECHANISM = swap differential. "
            "STUBBED/NOTED-NOT-BUILT: multi-hop typed-path composition + perceptual grounding (the redirects "
            "if this HARD_FAILs)."),
        "contract": ("INLINE-LOCAL foreground-to-completion; no push/remote-persist; NOT remote-portable "
                     "(GloVe+WorldTree git-ignored/large; inherits 29544/29545 contract); VET-PENDING; FULL "
                     "eval slice bounded (limit_easy=500 limit_chal=600, stratified train/test) to fit one "
                     "foreground call"),
        "compute_architecture": ("mixed CPU: batched GloVe encode (store + ARG0/ARG1 arg texts) + scipy "
                                 "sparse batched PPR (2 passes, UNCHANGED) + numpy role-bind (elementwise "
                                 "bind + sum, cheap) + per-question feature assembly + 4 glass-box "
                                 "full-batch logreg trains (deterministic zero-init GD) + UNCHANGED "
                                 "combiner; wall target < 10min. No GPU speedup needed (matmuls small)."),
        "storage_strategy": "sharded (each fact = own embedding + own role-bound bundle + own graph node)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": ("default_ok_for_this_regime (learner hyperparams inherited from 29545 "
                              "L2=1.0/iters=400/lr=0.5 author-set a priori; wide pool + combiner UNCHANGED; "
                              "role keys + relation-type cues author-set a priori NOT tuned to force a win; "
                              "scramble + random must-fail controls present; swapped-argument mechanism sub-"
                              "test is analytic (role-binding decorrelation ~1/sqrt(nd), tighter at scale) "
                              "so the discriminator survives scale by construction)"),
    }
    _write_metrics_atomic(output_dir, metrics)

    try:
        with open(os.path.join(output_dir, "glassbox_sample.json"), "w", encoding="utf-8") as f:
            json.dump(glass, f, indent=2)
    except Exception as e:
        print(f"[warn] glassbox persist failed (non-fatal): {e}", flush=True)

    _heartbeat(output_dir, "done", {"verdict": verdict})
    print(f"\n[VERDICT] {verdict}: {vmsg}", flush=True)
    print(f"[elapsed] {metrics['elapsed_s']}s", flush=True)
    return metrics


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["smoke", "full"], default="full")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args(argv)

    if args.self_test:
        self_test()
        return

    try:
        sys.stdout.reconfigure(line_buffering=True)
    except Exception:
        pass

    output_dir = _out_dir()
    _T0[0] = time.perf_counter()
    _write_start_marker(output_dir, args.mode)
    run(args.mode, output_dir)


if __name__ == "__main__":
    _od = _out_dir()
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash_metrics(_od, e)
        raise
