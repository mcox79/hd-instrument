"""concept_featural_enrichment_v2 -- FAIR, DECONFOUNDED re-test of concept content-enrichment.

v1 (CONTENT_ENRICHMENT_HARD_FAIL, B=0.1168 ~= RANDOM=0.1066) was VET-adjudicated CONFOUNDED: the head-
word concept->property assignment was CLEAN, but the AGGREGATION layer keyed the WHOLE arg1 CLAUSE as a
"filler" under the relation GROUP, attached it to EVERY content word of arg0, and SUMMED per-word bundles
over ALL content words of a fact. Generic hub words (something/water/object/energy/usually) dominated;
41.3% of fillers were df=1 whole-clauses so global distinctiveness degenerated to alphabetical tiebreak;
prop_overlap saturated at 1.6473 and the LURE outscored the gold; enr_cos went NEGATIVE everywhere
because property mass drowned the thin on-topic cosine. B ~= RANDOM = clean content was never presented
in isolation. v2 fixes the 4 confound sources, holding selection-logic + pool + combiner + learner +
split UNCHANGED (ONE variable stays = thin vs CLEAN-content-enriched meaning):

  FIX 1 (enrich only concept-carrying words): a subject word gets a property bundle ONLY if it is NOT a
         near-stopword hub (ENRICH_EXTRA_STOP) AND its store document-frequency is at/below the
         ENRICH_DF_PCTL percentile. Generic hubs (something/usually/object/energy/water-as-subject) drop.
  FIX 2 (atomic property fillers): each arg1 clause is decomposed into ATOMIC content tokens
         (arc._content_words); a filler is a feature ("renewable","water","fission"), not a sentence-
         clause. filler_df is now computed over atomic tokens (meaningful), not one-off clauses.
  FIX 3 (concept-relative distinctiveness): the distinctiveness feature (acr_distinct) weights a shared
         (group,filler) key by 1/(# answer-choices whose concept-keyset contains it) -- ANSWER-CHOICE-
         RELATIVE, not corpus-global df. A property present in ONLY the on-topic choice scores 1.0; a
         property shared across all choices scores 1/C. This is the crux: "water" globally is a moderate-
         df hub, but among {hydro,nuclear,coal} it is DISTINCTIVE of hydro.
  FIX 4 (normalization so head content is not drowned): the per-FACT property bundle is capped to
         K_FACT_PROPS distinctive-first atomic pairs AND unit-normalized before the gamma-additive mix
         L2(unit(thin) + GAMMA*unit(prop)), so property mass is bounded to GAMMA relative to head content.

FIX-TOOK FIRST GATE (reported BEFORE the verdict): enr_cos_gold_mean must go POSITIVE for on-topic gold
(v1 was negative everywhere) and clean-enriched must differ from RANDOM at the feature level. If enr_cos
stays negative / B still ~= RANDOM, the fix did NOT take -- report that honestly, do not over-claim.

--- v1 header (retained; scheme this cell deconfounds) ---
concept_featural_enrichment -- CONTENT-enriched concept meaning vs content-thin, for selection.

THE WALL (29544 fixed-signals / 29545 linear-learned / 29546 typed-relation-STRUCTURE): retrieval
REACHES the facts (wide RR pool), the combiner USES them (oracle gold->combiner Challenge ~0.71), but
SELECTION cannot ISOLATE the fine-content gold from fine-content lures. 29546 wired typed role-bind
(relation TYPE + argument ORDER) into selection and HARD_FAILED (B in-sample precision 0.0809 vs A
0.1865), with its OWN sub-diagnosis: "role-binding IS asymmetry-faithful (swap fires) but relation-
type/direction does NOT separate THESE gold-vs-lure pairs; redirect = ... content (lures differ by
fine content, not relation direction)". That is the CONFIRMED lever this cell opens.

THE DIAGNOSIS (drill notes/research_content_thin_concept_meaning_featural_enrichment_2026-07-25.md):
for a hydroelectric-dam question, selection picks nuclear/coal/gas power-plant facts (structurally
IDENTICAL: all "X PRODUCES electricity") and misses the hydro gold, because GloVe/WordNet put
hydro~nuclear~coal all close ("power/energy") and CANNOT represent their SPECIFIC content. Relation-
STRUCTURE (29546) is provably powerless here -- there IS no structural difference, only a CONTENT
difference in what fills the plant-type slot. The fix is DIFFERENT: bind each concept's OWN
DISTINGUISHING PROPERTIES -- already present, unused, in WorldTree's property tables (SOURCEOF/REQUIRES/
MADEOF/USEDFOR/PARTOF/CAUSE/KINDOF/PROP-*-RENEWABLE: hydro->renewable/water/dam, nuclear->fission/waste,
coal->nonrenewable/combustion) -- INTO the concept's meaning representation, so fine-content-similar
concepts become DISTINGUISHABLE. Rogers-McClelland PDP: fine differentiation is trained on explicit
property TRIPLES, not co-occurrence; Hoffman/Lambon-Ralph ATL hub: fine distinctions require BINDING
MULTIPLE typed features. This is CONCEPT-content enrichment (the concept rep itself becomes feature-rich),
distinct from 29546's fact-role STRUCTURE (which failed).

ONE variable = the concept MEANING representation (content-thin vs property-content-enriched). The
UNCHANGED WIDE RR pool (mr.reformulate_seeds/_rownorm_scores IMPORTED) and the UNCHANGED bind+bundle
combiner (agg.aggregate 'bundle' IMPORTED) are held FIXED. Arm A reuses 29545's EXACT flat feature
assembly + glass-box learner (imported) -> regression-anchor to the ~0.186 in-sample ceiling.

ENRICHMENT (reuses hd_fact_store's bind/bundle primitive, applied one level UP -- at the CONCEPT level):
for each content-word concept, look it up (as subject) across WorldTree's property tables, take up to K
DISTINCTIVE (rare-filler-first, Cree/McRae) properties, and bind each property's filler under its
relation-GROUP role key (the SAME bipolar role binding EventBundleCodec/hd_fact_store use). The concept's
property bundle is ADDED (gamma-weighted) to its EXISTING thin vector -- gamma=0 recovers thin EXACTLY.
  concept_bundle(c) = sum_i  group_key(rel_i) (*) enc(filler_i)          [(*) = elementwise bind]
  enriched_fact     = L2( thin_fact_hd + GAMMA * sum_{c in fact}  concept_bundle(c) )
  enriched_q_choice = L2( thin_(stem+choice)_hd + GAMMA * sum_{c in stem+choice} concept_bundle(c) )
Content-enriched selection features (per pool fact vs the question's choices):
  1 enr_cos_max   = max_c cos(enriched_fact, enriched_q_c)
  2 enr_cos_mean  = mean_c relu(cos(enriched_fact, enriched_q_c))
  3 prop_overlap  = max_c | {(group,filler)} of fact-concepts  INTERSECT  of (stem+choice_c)-concepts |
  4 distinct_match= max_c sum_{shared (g,filler)} 1/df(filler)          (distinctiveness-weighted)
  5 has_property  = 1.0 if the fact has >=1 concept with >=1 property row (coverage indicator)

Arms (concept MEANING content is the ONLY variable; pool + combiner UNCHANGED):
  A_thin      -- 29545 flat thin features -> glass-box learner    [BASELINE replicate ~0.186 in-sample]
  B_enriched  -- property-content features -> SAME learner         [MECHANISM: content enrichment]
  C_combined  -- thin + content features   -> SAME learner         [complementarity]
  B_single    -- content features w/ ONLY the single highest-coverage group [hub multi-feature ablation]
  RANDOM      -- content features w/ property assignment PERMUTED across concepts [MUST-FAIL: proves it
                 is the RIGHT properties, not mere added dimensionality/noise]
  ORACLE      -- gold central facts -> combiner                    [CEILING ~0.71]

FIRST GATE (coverage, reported FIRST): fraction of question content-word concepts (and pool facts) with
>=1 usable WorldTree property row. If thin (< COVERAGE_MIN) a positive on the covered subset is real but
NARROW -> honest COVERAGE_BOUND (report straight; the lever needs broader property data).

PLANTED MECHANISM (dam / hydroelectric-nuclear-coal, self_test): concept vectors whose THIN base is
near-identical (all "power plant") but whose bound property content differs (hydro renewable/water/dam
vs nuclear fission/waste vs coal fossil/combustion); a query matching hydro's properties must rank the
hydro fact top under ENRICHED with margin >= PLANT_MECH_HP where the THIN margin ~ 0 (base near-equal).
This is the CASE where relation-structure (29546) provably cannot help and only concept-content can.

PRIMARY = in-sample TRAIN sel_gold_precision (sharp; 29545 ceiling ~0.186) + end-to-end ARC Challenge
answer (toward oracle ~0.71). SECONDARY = TEST sel_gold_precision + coverage-filtered-subset precision.
MECHANISM = planted dam margin. HARD_PASS = enriched materially raises in-sample precision above the
thin ceiling AND lifts the answer significantly AND RANDOM does NOT AND the dam mechanism separates.
HARD_FAIL = enriched ~= thin (properties do not distinguish, or coverage too thin) -> redirect to
deeper perceptual grounding / richer property source (report STRAIGHT + sub-diagnosis). NO tuning to
force a win.

Contract: INLINE-LOCAL foreground-to-completion (GloVe + WorldTree git-ignored/large -> NOT remote-
portable, inherits 29544/29545/29546 contract); NO push/remote-persist; ASCII-only; deterministic
(fixed seeds, numpy default_rng, sorted iteration, zero-init GD, no hash()); repo .venv; VET-PENDING.

CELL-TEMPLATE MANDATORY:
# - except SystemExit: raise BEFORE except Exception (no BaseException; no bare except)
# - final_metrics_atomicity = tmp_replace ; start-marker ; crash-diagnostic ; heartbeat
# - real_code_path: self_test builds REAL SemanticHDEncoder + REAL group role keys + REAL typed
#   tablestore parse (rel.parse_tablestore_typed) + REAL property index + REAL concept-bundle enrichment
#   + REAL RR wide pool + imported 29545 learner + UNCHANGED combiner; PLANTED dam case asserts enriched
#   separates gold from lures where thin cannot (mechanism fires); arms-differ; no-leak (train/test disjoint)
# - deterministic_seeding: fixed int seeds + numpy default_rng + sorted iteration + zero-init GD; no hash()
# - baseline_in_band + AG-guard on A_thin TEST challenge (headroom to the ~0.71 ceiling)
# - storage = SHARDED (each fact = own embedding + own property bundle + own graph node)
# - GLASS-BOX INVARIANT: linear weights over NAMED content features (logged) + per-fact property content
#   (which WorldTree rows/relations enriched each concept, cap K) logged + the dam separation inspectable
# - all reported numbers MEASURED@ this cell's metrics.json
"""
from __future__ import annotations

import os
import sys
import json
import time
import hashlib
import argparse
import platform
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

os.environ.setdefault("GENSIM_DATA_DIR", os.path.join(_REPO, "data", "gensim_cache"))

# reuse (UNCHANGED): the 29545 baseline features + glass-box learner + split; the WIDE RR pool; the
# bind+settle combiner; PPR graph; the typed tablestore parse (from 29546); arc + encoder helpers.
from experiments import exp_arc_selection_learned_relevance_glassbox_v1 as learned  # noqa: E402
from experiments import exp_arc_selection_relational_meaning_v1 as rel              # noqa: E402
from experiments import exp_arc_retrieval_multicue_ppr_discriminative_v1 as ppr     # noqa: E402
from experiments import exp_arc_retrieval_max_recall_ksweep_reretrieval_v1 as mr    # noqa: E402
from experiments import exp_arc_retrieval_selection_gate_suppression_v1 as gate     # noqa: E402
from experiments import exp_arc_aggregation_retriever_bindsettle_v1 as agg          # noqa: E402
from experiments import exp_arc_knowledge_scale_ingest_climb_v1 as arc              # noqa: E402
from experiments import exp_arc_selection_precision_coherence_subset_v1 as fixedsel  # noqa: E402
from experiments.exp_semantic_hd_encoder_meaning_match_v1 import (                  # noqa: E402
    SemanticHDEncoder, _load_glove, _load_wordnet)
from hdlab.event_bundle import EventBundleCodec                                     # noqa: E402

ANCHOR_NAME = "concept_featural_enrichment_v2"
SEED = 20260725

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

# reuse the 29545 learner + baseline features EXACTLY (regression-anchors Arm A to the ~0.186 ceiling)
FLAT_FEATURE_NAMES = learned.FEATURE_NAMES
train_glassbox_relevance = learned.train_glassbox_relevance
learned_score = learned.learned_score
_minmax_cols = learned._minmax_cols
_neg_count = learned._neg_count
question_features_flat = learned.question_features
_topk_idx = learned._topk_idx

# ---- content-enrichment config (author-set a priori; NOT tuned to force a win) ----
GAMMA = 0.5          # property-bundle weight added to the thin concept vector (gamma=0 => thin exactly)
K_PROPS = 6          # cap ATOMIC properties per concept (distinctive-first; Cree/McRae)
K_FACT_PROPS = 10    # FIX 4a: cap TOTAL atomic (group,filler) pairs per FACT (distinctive-first)
CONTENT_MIN_LEN = 4  # concept content-word min length (matches arc._content_words default)
ENRICH_DF_PCTL = 90.0  # FIX 1: a subject word is enrichable only if store-df <= this percentile (drop hubs)
FIX_TOOK_EPS = 0.01    # fix-took: clean-enriched gold acr_distinct must exceed RANDOM gold by this margin

# FIX 1: near-stopword content hubs that carry no distinctive concept content (a priori; not tuned).
# (df-percentile gate handles the rest; e.g. water/energy as SUBJECTS are high-df and drop, but they
#  survive as distinctive FILLERS where answer-choice-relative distinctiveness rewards them.)
ENRICH_EXTRA_STOP = frozenset("""
something someone somebody anything everything nothing thing things object objects stuff
usually sometimes always often normally generally typically mostly commonly
increase increases increasing increased decrease decreases decreasing decreased
amount amounts number numbers kind kinds type types example examples sort sorts
using used uses make makes made cause causes caused become becomes came come comes
different similar same various certain particular given called known
""".split())

# ---- content feature set (property-content; the ONE new meaning representation) ----
# acr_distinct = ANSWER-CHOICE-RELATIVE distinctiveness (FIX 3); replaces v1 global 1/df distinct_match.
ENR_FEATURE_NAMES = ("enr_cos_max", "enr_cos_mean", "prop_overlap", "acr_distinct", "has_property")

# ---- relation -> GROUP role (small stable set; each table binds its filler under its group key) ----
RELATION_GROUP = {
    "SOURCEOF": "SOURCE", "TRANSFER": "SOURCE", "CONVERSIONS": "SOURCE",
    "REQUIRES": "REQUIRES",
    "MADEOF": "COMPOSITION", "FORMEDBY": "COMPOSITION", "PARTOF": "COMPOSITION",
    "CONTAINS": "COMPOSITION",
    "USEDFOR": "USE", "AFFORDANCES": "USE", "VEHICLE": "USE",
    "CAUSE": "CAUSE", "IFTHEN": "CAUSE", "AFFECT": "CAUSE", "CHANGE": "CAUSE",
    "CHANGE-VEC": "CAUSE", "COUPLEDRELATIONSHIP": "CAUSE",
    "KINDOF": "KIND", "INSTANCES": "KIND", "EXAMPLES": "KIND", "SYNONYMY": "KIND",
    "LOCATIONS": "LOCATION", "HABITAT": "LOCATION",
    "PREDATOR-PREY": "ECOLOGY", "CONSUMERS-EATING": "ECOLOGY",
}
DEFAULT_GROUP = "PROP"  # PROP-* tables + ATTRIBUTE/MEASUREMENT/anything unmapped
GROUPS = ("SOURCE", "REQUIRES", "COMPOSITION", "USE", "CAUSE", "KIND", "LOCATION", "ECOLOGY", "PROP")


def _group_of(relation):
    return RELATION_GROUP.get(relation, DEFAULT_GROUP)


# ---- bands (author-designed a priori; from the drill's pre-registered predictions) ----
ENR_LIFT_HP = 0.05        # Pred1 HARD-PASS: B in-sample precision - A >= this (materially over ~0.186)
ENR_LIFT_HF = 0.02        # Pred1 HARD-FAIL: B in-sample precision - A <= this (no material content signal)
ENR_SUBSET_HP = 0.40      # Pred1 subset: B in-sample precision on coverage-filtered subset >= this
RANDOM_COLLAPSE_EPS = 0.02  # RANDOM in-sample precision must be within this OF (or below) baseline
PLANT_MECH_HP = 0.05      # Pred2 mechanism (planted dam): enriched gold-margin - thin gold-margin >= this
CHAL_LIFT_HP = 0.05       # Pred4 end-to-end: best(B,C) - A on TEST Challenge AND McNemar-significant
MB_CHAL_LIFT = 0.02       # positive-but-sub-HP band floor
RANDPOOL_MAX = 0.02       # (unused control tolerance placeholder; kept for band completeness)
COVERAGE_MIN = 0.30       # FIRST GATE: question-concept property coverage below this -> COVERAGE_BOUND
MCNEMAR_ALPHA = 0.05
AG_BASELINE_SAT = 0.95    # A_thin challenge >= this -> vacuous (no headroom)
BASELINE_PREC_LO = 0.10   # A_thin in-sample precision regression band (29545 ~0.186); WARN if outside
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
# vector helpers
# ---------------------------------------------------------------------------
def _l2_rows(mat):
    m = np.asarray(mat, dtype=np.float32)
    n = np.linalg.norm(m, axis=1, keepdims=True)
    n[n == 0] = 1.0
    return m / n


def group_keys_np(codec):
    """Return {group: bipolar +/-1 numpy key} from the EventBundleCodec (same binding hd_fact_store uses)."""
    return {g: codec.role_key(g).numpy().astype(np.float32) for g in GROUPS}


# ---------------------------------------------------------------------------
# property index from the TYPED tablestore parse (reuses 29546's parser)
# ---------------------------------------------------------------------------
def build_document_frequency(sents):
    """content-word -> # store facts containing it (document frequency, for FIX-1 subject hub gating)."""
    df = defaultdict(int)
    for s in sents:
        for w in set(arc._content_words(s, CONTENT_MIN_LEN)):
            df[w] += 1
    return dict(df)


def make_enrichable(word_df, pctl=ENRICH_DF_PCTL):
    """FIX 1: subject word is enrichable iff NOT a near-stopword hub AND store-df <= pctl percentile.

    Returns (enrichable_fn, df_threshold). Words unseen in the store (df=0) are enrichable (rare)."""
    vals = sorted(word_df.values())
    thr = float(np.percentile(np.asarray(vals, dtype=np.float64), pctl)) if vals else 0.0

    def enrichable(w):
        if w in ENRICH_EXTRA_STOP:
            return False
        return float(word_df.get(w, 0)) <= thr

    return enrichable, thr


def _atomic_fillers(a1):
    """FIX 2: decompose an arg1 object CLAUSE into ATOMIC content tokens (feature fillers)."""
    return sorted({f for f in arc._content_words(a1, CONTENT_MIN_LEN) if f not in ENRICH_EXTRA_STOP})


def build_property_index(uid2typed, enrichable):
    """concept subject-word -> list of (group, ATOMIC filler_token); plus filler_df (over atomic tokens).

    A property row is (arg0=subject, relation, arg1=object). FIX 1: only ENRICHABLE (non-hub, low-df)
    subject words get properties. FIX 2: the object clause is decomposed into atomic content tokens, so a
    filler is a reusable feature (not a one-off sentence clause). df(filler) = # distinct concepts with it."""
    props = defaultdict(list)
    seen_pair = defaultdict(set)                 # concept -> set of (group,filler) already added (dedupe)
    filler_concepts = defaultdict(set)           # filler_token -> set of concept words (for df)
    for uid in sorted(uid2typed.keys()):
        t = uid2typed[uid]
        a0, a1 = t.get("arg0", ""), t.get("arg1", "")
        if not a0 or not a1:
            continue
        group = _group_of(t.get("relation", ""))
        atoms = _atomic_fillers(a1)
        if not atoms:
            continue
        for w in arc._content_words(a0, CONTENT_MIN_LEN):
            if not enrichable(w):
                continue
            for filler in atoms:
                if filler == w:
                    continue                     # self-filler carries no distinguishing content
                key = (group, filler)
                if key in seen_pair[w]:
                    continue
                seen_pair[w].add(key)
                props[w].append((group, filler))
                filler_concepts[filler].add(w)
    filler_df = {f: len(cs) for f, cs in filler_concepts.items()}
    return dict(props), filler_df


def _select_props(plist, filler_df, k, only_group=None):
    """Pick up to k atomic properties for a concept, DISTINCTIVE (rare-filler) first (Cree/McRae)."""
    cand = [(g, f) for (g, f) in plist if (only_group is None or g == only_group)]
    cand = sorted(cand, key=lambda gf: (filler_df.get(gf[1], 1), gf[0], gf[1]))  # low df first; stable
    return cand[:k]


def build_concept_keys(props, filler_df, k, only_group=None):
    """concept word -> frozenset of selected (group, atomic-filler) pairs (distinctive-first, cap k)."""
    ck = {}
    for w in sorted(props.keys()):
        sel = _select_props(props[w], filler_df, k, only_group)
        if sel:
            ck[w] = frozenset(sel)
    return ck


def build_pair_vectors(concept_keys_maps, enc, gkeys):
    """{(group,filler): gkeys[group] (*) enc(filler)} over every pair referenced by the concept-key maps.

    Each filler is a SINGLE atomic token -> clean GloVe encoding. Bound once, reused at fact/choice level."""
    pairs = set()
    for ck in concept_keys_maps:
        for ks in ck.values():
            pairs |= ks
    fillers = sorted({f for (_g, f) in pairs})
    if fillers:
        FV = arc._encode_store(enc, fillers)          # [nF, nd] unit rows
    else:
        FV = np.zeros((0, enc.n_dim), dtype=np.float32)
    f2row = {f: i for i, f in enumerate(fillers)}
    pv = {}
    for (g, f) in sorted(pairs):
        pv[(g, f)] = (gkeys[g] * FV[f2row[f]]).astype(np.float32)
    return pv, len(fillers)


def aggregate_props(words, concept_keys, pair_vec, filler_df, nd, k_fact):
    """FIX 4: union selected pairs over ENRICHABLE words of an item, CAP to k_fact distinctive-first,
    sum the bound vectors, and UNIT-NORMALIZE (so property mass is bounded before the gamma mix).

    Returns (unit_property_bundle [nd], keyset frozenset of the capped (group,filler) pairs)."""
    pairs = set()
    for w in words:
        ks = concept_keys.get(w)
        if ks:
            pairs |= ks
    if not pairs:
        return np.zeros(nd, dtype=np.float32), frozenset()
    capped = sorted(pairs, key=lambda gf: (filler_df.get(gf[1], 1), gf[0], gf[1]))[:k_fact]
    acc = np.zeros(nd, dtype=np.float32)
    for gf in capped:
        v = pair_vec.get(gf)
        if v is not None:
            acc += v
    n = float(np.linalg.norm(acc))
    if n > 0.0:
        acc = acc / n
    return acc.astype(np.float32), frozenset(capped)


# ---------------------------------------------------------------------------
# content-enrichment selection features
# ---------------------------------------------------------------------------
def enriched_features(pool_idx, enr_fact, fact_keyset, filler_df, enr_q_choices, qc_keysets):
    """[P, 5] RAW content feature matrix for one question's pool. Answer-agnostic (all choices used)."""
    P = pool_idx.shape[0]
    C = enr_q_choices.shape[0]
    if P == 0:
        return np.zeros((0, len(ENR_FEATURE_NAMES)), dtype=np.float64)
    ef = enr_fact[pool_idx]                          # [P, nd]
    cbc = (ef @ enr_q_choices.T).astype(np.float64) if C else np.zeros((P, 0))  # [P, C]
    enr_cos_max = cbc.max(axis=1) if C else np.zeros(P)
    enr_cos_mean = np.maximum(cbc, 0.0).mean(axis=1) if C else np.zeros(P)
    # FIX 3: ANSWER-CHOICE-RELATIVE distinctiveness. A (group,filler) key present in only ONE choice's
    # concept-keyset is maximally distinctive for that choice (weight 1); shared across n choices -> 1/n.
    key_nchoice = defaultdict(int)
    for ks in qc_keysets:
        for k in ks:
            key_nchoice[k] += 1
    overlap = np.zeros(P, dtype=np.float64)
    acr = np.zeros(P, dtype=np.float64)
    has_prop = np.zeros(P, dtype=np.float64)
    for p, fi in enumerate(pool_idx.tolist()):
        fks = fact_keyset[fi]
        if fks:
            has_prop[p] = 1.0
        best_o = 0.0
        best_d = 0.0
        for c in range(C):
            inter = fks & qc_keysets[c]
            if inter:
                o = float(len(inter))
                d = 0.0
                for k in inter:
                    nc = key_nchoice.get(k, 1)
                    d += 1.0 / float(nc if nc > 0 else 1)   # answer-choice-relative, not corpus-global df
                if o > best_o:
                    best_o = o
                if d > best_d:
                    best_d = d
        overlap[p] = best_o
        acr[p] = best_d
    X = np.stack([enr_cos_max, enr_cos_mean, overlap, acr, has_prop], axis=1)
    assert X.shape == (P, len(ENR_FEATURE_NAMES)), "content feature matrix shape mismatch"
    return X.astype(np.float64)


# ---------------------------------------------------------------------------
# PLANTED dam mechanism (self-test): enriched separates gold from lures where thin cannot
# ---------------------------------------------------------------------------
def _planted_dam_discriminator(nd=512):
    """Three concepts (hydro/nuclear/coal) whose THIN base is near-identical (all 'power plant') but
    whose bound PROPERTY content differs. A query matching hydro's properties must rank the hydro fact
    top under ENRICHED with margin >= PLANT_MECH_HP, where the THIN margin ~ 0 (base near-equal).
    Uses random unit base + random unit filler vectors (like 29546's planted control) so the test is
    deterministic and isolates the binding mechanism from GloVe's incidental base differences."""
    rng = np.random.default_rng(731)
    codec = EventBundleCodec(n_dim=nd, roles=GROUPS, seed=SEED)
    gkeys = group_keys_np(codec)

    def unit(x):
        return (x / (np.linalg.norm(x) + 1e-12)).astype(np.float32)

    shared = unit(rng.standard_normal(nd))                       # the "power plant / produces electricity" base
    eps = 0.05
    base = {name: unit(shared + eps * unit(rng.standard_normal(nd)))
            for name in ("hydro", "nuclear", "coal")}            # near-identical thin bases

    # distinguishing property fillers (as unit vectors); groups match RELATION_GROUP
    renewable, water, dam = (unit(rng.standard_normal(nd)) for _ in range(3))
    fission, waste = (unit(rng.standard_normal(nd)) for _ in range(2))
    fossil, combustion = (unit(rng.standard_normal(nd)) for _ in range(2))
    props = {
        "hydro": [("SOURCE", renewable), ("REQUIRES", water), ("COMPOSITION", dam)],
        "nuclear": [("SOURCE", fission), ("CAUSE", waste)],
        "coal": [("KIND", fossil), ("CAUSE", combustion)],
    }

    def bundle(name):
        acc = np.zeros(nd, dtype=np.float32)
        for (g, fv) in props[name]:
            acc += gkeys[g] * fv
        return acc

    enr = {name: unit(base[name] + GAMMA * bundle(name)) for name in base}

    # query: matches hydro's property content (renewable+water+dam), same shared base
    q_prop = gkeys["SOURCE"] * renewable + gkeys["REQUIRES"] * water + gkeys["COMPOSITION"] * dam
    q_thin = unit(shared)
    q_enr = unit(shared + GAMMA * q_prop)

    thin_sims = {n: float(unit(base[n]) @ q_thin) for n in base}
    enr_sims = {n: float(enr[n] @ q_enr) for n in base}
    thin_margin = thin_sims["hydro"] - max(thin_sims["nuclear"], thin_sims["coal"])
    enr_margin = enr_sims["hydro"] - max(enr_sims["nuclear"], enr_sims["coal"])
    enr_ranks_gold_top = (enr_sims["hydro"] > enr_sims["nuclear"]) and (enr_sims["hydro"] > enr_sims["coal"])

    assert enr_ranks_gold_top, f"planted dam: enriched did not rank hydro gold top ({enr_sims})"
    assert enr_margin - thin_margin >= PLANT_MECH_HP, \
        f"planted dam mechanism did not fire (enr_margin={enr_margin:.3f} thin_margin={thin_margin:.3f})"
    assert thin_margin < enr_margin, "planted dam: thin margin not below enriched margin"
    return {"thin_sims": {k: round(v, 4) for k, v in thin_sims.items()},
            "enr_sims": {k: round(v, 4) for k, v in enr_sims.items()},
            "thin_margin": round(thin_margin, 4), "enr_margin": round(enr_margin, 4),
            "margin_lift": round(enr_margin - thin_margin, 4)}


# ---------------------------------------------------------------------------
# self-test
# ---------------------------------------------------------------------------
def self_test():
    print("[self-test] planted dam mechanism (enriched separates hydro gold from nuclear/coal lures "
          "where thin base is near-equal; margin lift >= PLANT_MECH_HP) ...", flush=True)
    planted = _planted_dam_discriminator()
    print(f"[self-test]   planted dam: {planted}", flush=True)

    print("[self-test] REAL flat store df -> FIX-1 hub gating + FIX-2 atomic typed parse + property "
          "index + REAL encoder + group role keys + pair vectors + FIX-4 capped/unit-norm aggregation + "
          "REAL RR pool path + imported 29545 learner + UNCHANGED combiner ...", flush=True)
    assert os.path.isdir(agg._TABLES), f"tablestore missing: {agg._TABLES}"
    uid2typed = rel.parse_tablestore_typed()
    assert len(uid2typed) > 100, f"typed parse too small ({len(uid2typed)})"
    # FIX 1: build store document-frequency and the hub-gating enrichable predicate from the REAL store
    flat_store = agg.parse_tablestore()
    word_df = build_document_frequency([flat_store[u] for u in sorted(flat_store.keys())])
    enrichable, df_thr = make_enrichable(word_df)
    assert df_thr > 0.0, f"df threshold degenerate ({df_thr})"
    # FIX-1 must gate the named hubs OUT of enrichment
    for hub in ("something", "usually", "energy"):
        assert not enrichable(hub), f"FIX-1 failed: hub {hub!r} still enrichable (df={word_df.get(hub)})"
    props, filler_df = build_property_index(uid2typed, enrichable)
    assert len(props) > 50, f"property index too small ({len(props)})"
    # FIX 2: fillers must be ATOMIC single tokens, not whole clauses
    for w, plist in list(props.items())[:200]:
        for (g, f) in plist:
            assert " " not in f, f"FIX-2 failed: non-atomic filler {f!r} for concept {w!r}"
    # energy-domain sanity: hydro/nuclear/coal concepts should have DISTINCT atomic property content
    for probe in ("hydroelectric", "nuclear", "coal"):
        if probe in props:
            print(f"[self-test]   props[{probe}]={_select_props(props[probe], filler_df, K_PROPS)[:6]}",
                  flush=True)

    kv = _load_glove()
    _load_wordnet()
    nd = 512
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)
    codec = EventBundleCodec(n_dim=nd, roles=GROUPS, seed=SEED)
    gkeys = group_keys_np(codec)
    concept_keys = build_concept_keys(props, filler_df, K_PROPS)
    assert len(concept_keys) > 20, f"concept keys degenerate ({len(concept_keys)})"
    pair_vec, nfill = build_pair_vectors([concept_keys], enc, gkeys)
    assert nfill > 0, f"pair vectors degenerate ({nfill})"

    # gamma=0 recovers thin EXACTLY (one-variable check)
    store_sents = ["a hydroelectric plant produces electricity",
                   "a nuclear plant produces electricity",
                   "coal is a kind of fossil fuel"]
    SV = arc._encode_store(enc, store_sents)
    fprop = np.zeros_like(SV)
    fkeys = []
    for i, s in enumerate(store_sents):
        acc, ks = aggregate_props(arc._content_words(s, CONTENT_MIN_LEN), concept_keys, pair_vec,
                                  filler_df, nd, K_FACT_PROPS)
        fprop[i] = acc
        fkeys.append(ks)
    enr_g0 = _l2_rows(SV + 0.0 * fprop)
    assert np.allclose(enr_g0, _l2_rows(SV)), "gamma=0 did not recover thin exactly"
    enr_fact = _l2_rows(SV + GAMMA * fprop)
    assert not np.allclose(enr_fact, _l2_rows(SV)), "enrichment did not change the representation"

    q = {"stem": "which power source is renewable", "choices": ["nuclear", "hydroelectric", "coal"]}
    choice_hd = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
    qc_keys = []
    enr_q = np.zeros_like(choice_hd)
    for c, ch in enumerate(q["choices"]):
        acc, ks = aggregate_props(arc._content_words(q["stem"] + " " + ch, CONTENT_MIN_LEN),
                                  concept_keys, pair_vec, filler_df, nd, K_FACT_PROPS)
        enr_q[c] = acc
        qc_keys.append(ks)
    enr_q = _l2_rows(choice_hd + GAMMA * enr_q)
    pool_idx = np.arange(len(store_sents), dtype=np.int64)
    X = enriched_features(pool_idx, enr_fact, fkeys, filler_df, enr_q, qc_keys)
    assert X.shape == (3, len(ENR_FEATURE_NAMES)), "real: content feature matrix shape"

    # imported 29545 learner trains on the REAL content features (tiny synthetic label)
    Xn = _minmax_cols(X)
    ylab = np.array([1.0, 0.0, 0.0], dtype=np.float64)
    w, b = train_glassbox_relevance(Xn, ylab)
    assert w.shape[0] == len(ENR_FEATURE_NAMES), "real: learned weight length"
    s = learned_score(Xn, w, b)
    assert s.shape[0] == 3, "real: score shape"

    # UNCHANGED combiner over a content-selected set
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"])])[0]
    choice_full = arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]])
    sel = pool_idx[_topk_idx(s, min(K_SEL, 3))]
    fh = SV[sel]
    q_rel = np.maximum(fh @ QQ, 0.0).astype(np.float32)
    sc, _ = agg.aggregate(fh, q_rel, choice_full, "bundle", rng=np.random.default_rng(0))
    assert sc.shape[0] == 3, "real: combiner reuse shape"

    # determinism
    w2, b2 = train_glassbox_relevance(Xn, ylab)
    assert np.allclose(w, w2) and abs(b - b2) < 1e-12, "real: training non-deterministic"

    # arms differ: thin base != enriched (content changes the representation)
    assert not np.allclose(enr_fact, _l2_rows(SV)), "real: enriched == thin"
    print("[self-test] PASS (planted dam mechanism fires; real property index + concept bundles + "
          "imported learner + UNCHANGED combiner; gamma=0 recovers thin; determinism)", flush=True)
    return True


# ---------------------------------------------------------------------------
# full/smoke run
# ---------------------------------------------------------------------------
def _config(mode):
    if mode == "smoke":
        return {"n_dim": 2048, "limit_easy": 120, "limit_chal": 120}
    return {"n_dim": 2048, "limit_easy": 500, "limit_chal": 600}


ARMS = ("A_thin", "B_enriched", "C_combined", "B_single", "RANDOM", "ORACLE")
FEATURE_ARMS = ("A_thin", "B_enriched", "C_combined", "B_single", "RANDOM")


def _highest_coverage_group(props, filler_df):
    """Group covering the most distinct concepts (for the B_single ablation)."""
    cov = defaultdict(set)
    for w in sorted(props.keys()):
        for (g, f) in _select_props(props[w], filler_df, K_PROPS):
            cov[g].add(w)
    best = None
    for g in GROUPS:
        n = len(cov.get(g, ()))
        if best is None or n > best[1]:
            best = (g, n)
    return best[0] if best else DEFAULT_GROUP


def run(mode, output_dir):
    cfg = _config(mode)
    nd = cfg["n_dim"]

    _heartbeat(output_dir, "load_glove")
    kv = _load_glove()
    _load_wordnet()
    enc = SemanticHDEncoder(n_dim=nd, seed=SEED, use_wordnet=True, kv=kv)
    codec = EventBundleCodec(n_dim=nd, roles=GROUPS, seed=SEED)
    gkeys = group_keys_np(codec)

    _heartbeat(output_dir, "load_questions")
    questions = agg.load_wt_questions(cfg["limit_easy"], cfg["limit_chal"])
    n_easy = sum(1 for q in questions if q["source"].startswith("ARC-Easy"))
    n_chal = len(questions) - n_easy
    chance = arc._chance_theoretical(questions)
    nQ = len(questions)
    train_mask, test_mask = learned._split_train_test(questions)
    print(f"[eval] {nQ} questions ({n_easy} Easy, {n_chal} Challenge) chance={chance:.3f} "
          f"train={int(train_mask.sum())} test={int(test_mask.sum())}", flush=True)

    # ---- store = FULL tablestore (flat sentences UNCHANGED) + TYPED parse -> property index ----
    _heartbeat(output_dir, "parse_tablestore")
    uid2sent = agg.parse_tablestore()
    uid2typed = rel.parse_tablestore_typed()
    uids = sorted(uid2sent.keys())
    sents = [uid2sent[u] for u in uids]
    uid2fi = {u: i for i, u in enumerate(uids)}
    nFacts = len(uids)
    # FIX 1: store document-frequency -> hub-gating enrichable predicate (built on the SAME flat store)
    word_df = build_document_frequency(sents)
    enrichable, df_thr = make_enrichable(word_df)
    n_hub_dropped = sum(1 for w in word_df if not enrichable(w))
    props, filler_df = build_property_index(uid2typed, enrichable)
    single_group = _highest_coverage_group(props, filler_df)
    print(f"[store] full tablestore = {nFacts} facts | property_concepts={len(props)} "
          f"atomic_fillers={len(filler_df)} single_group={single_group} df_thr={round(df_thr, 1)} "
          f"hub_words_dropped={n_hub_dropped}", flush=True)

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

    # ---- concept keys (the ONE new meaning representation) : full / single-group / random ----
    _heartbeat(output_dir, "concept_keys")
    concept_keys = build_concept_keys(props, filler_df, K_PROPS)
    concept_keys_s = build_concept_keys(props, filler_df, K_PROPS, only_group=single_group)
    # RANDOM property control: permute the concept->keyset assignment (destroys real content, keeps
    # dimensionality/noise). Deterministic permutation over property-carrying concepts (no hash()).
    pconcepts = sorted(concept_keys.keys())
    perm_rng = np.random.default_rng(SEED + 909)
    perm = perm_rng.permutation(len(pconcepts))
    concept_keys_r = {pconcepts[i]: concept_keys[pconcepts[perm[i]]] for i in range(len(pconcepts))}
    # bind every referenced (group,filler) atomic pair ONCE (reused at fact + choice level)
    pair_vec, nfill = build_pair_vectors([concept_keys, concept_keys_s], enc, gkeys)
    print(f"[content] concept keys built (full={len(concept_keys)} single={len(concept_keys_s)} "
          f"random-perm={len(concept_keys_r)}) atomic_fillers={nfill} df_thr={round(df_thr, 1)}", flush=True)

    # per-fact property aggregation (FIX 4: capped + unit-normalized prop vector + keyset) per variant
    def fact_props(ckmap):
        FP = np.zeros((nFacts, nd), dtype=np.float32)
        FK = [None] * nFacts
        for i in range(nFacts):
            acc, ks = aggregate_props(fact_terms[i], ckmap, pair_vec, filler_df, nd, K_FACT_PROPS)
            FP[i] = acc
            FK[i] = ks
        return FP, FK

    _heartbeat(output_dir, "fact_props")
    FP_full, FK_full = fact_props(concept_keys)
    FP_single, FK_single = fact_props(concept_keys_s)
    FP_rand, FK_rand = fact_props(concept_keys_r)

    enr_fact_full = _l2_rows(SV_store + GAMMA * FP_full)
    enr_fact_single = _l2_rows(SV_store + GAMMA * FP_single)
    enr_fact_rand = _l2_rows(SV_store + GAMMA * FP_rand)

    # coverage: fraction of facts with >=1 property key
    fact_cov = round(float(np.mean([1.0 if FK_full[i] else 0.0 for i in range(nFacts)])), 4)

    # ---- encode questions ONCE (UNCHANGED flat encodings) ----
    _heartbeat(output_dir, "encode_questions")
    QQ = arc._encode_store(enc, [q["stem"] + " " + " ".join(q["choices"]) for q in questions])
    STEM = arc._encode_store(enc, [q["stem"] for q in questions])
    choice_hd_map = [arc._encode_store(enc, [q["stem"] + " " + c for c in q["choices"]]) for q in questions]

    stem_words_per_q = [set(arc._content_words(q["stem"], MIN_TERM_LEN)) for q in questions]
    sc_words_per_q = [sorted(set(arc._content_words(q["stem"] + " " + " ".join(q["choices"]), MIN_TERM_LEN)))
                      for q in questions]
    uniq_words = sorted({w for ws in sc_words_per_q for w in ws})
    uw_vecs = arc._encode_store(enc, uniq_words)
    uw2row = {w: i for i, w in enumerate(uniq_words)}

    def wvecs(ws):
        return uw_vecs[[uw2row[w] for w in ws]] if ws else np.zeros((0, nd), np.float32)

    # question property coverage FIRST GATE (content-word concepts across all questions)
    q_concepts = sorted({w for ws in sc_words_per_q for w in ws})
    q_cov = round(float(np.mean([1.0 if w in concept_keys else 0.0 for w in q_concepts])), 4) if q_concepts else 0.0
    print(f"[coverage] question-concept property coverage={q_cov} (concepts={len(q_concepts)}); "
          f"fact coverage={fact_cov}", flush=True)

    # ---- WIDE RR pool (max-recall cell path, UNCHANGED; built on THIN term encodings) ----
    _heartbeat(output_dir, "ppr_wide_pool")
    seeds_sc = ppr.link_seeds(sc_words_per_q, vocab, t2i, term_vecs, [wvecs(ws) for ws in sc_words_per_q], SEED_COS)
    sm_sc = ppr.seeds_to_matrix(seeds_sc, nTerms)
    F_SC = ppr.fact_activation(ppr.ppr_batch(sm_sc, M, HOPS, DAMP), Sft)
    seeds2 = mr.reformulate_seeds(F_SC, seeds_sc, fact_terms, t2i, RR_TOP_T)
    F_P2 = ppr.fact_activation(ppr.ppr_batch(ppr.seeds_to_matrix(seeds2, nTerms), M, HOPS, DAMP), Sft)
    F_RR = mr._rownorm_scores(F_SC) + mr._rownorm_scores(F_P2)

    # ---- PASS A: per-question pool + flat features + content features (all variants) + gold ----
    _heartbeat(output_dir, "features")
    poolidx_list = [None] * nQ
    Xn_flat = [None] * nQ
    Xn_enr = [None] * nQ
    Xn_comb = [None] * nQ
    Xn_single = [None] * nQ
    Xn_rand = [None] * nQ
    gold_rows_list = [None] * nQ
    lure_flags = np.zeros(nQ, dtype=bool)
    covered_subset = np.zeros(nQ, dtype=bool)   # questions with >=2 distinguishing property keys among choices
    # FIX-TOOK accumulators (raw feature values on on-topic gold pool facts)
    enr_cos_gold_vals = []
    enr_cos_rand_gold_vals = []
    acr_gold_vals = []
    acr_rand_gold_vals = []

    def choice_enr(qi, ckmap):
        """[C, nd] enriched per-choice query + list of C keysets (content words of stem+choice)."""
        chd = choice_hd_map[qi]
        C = chd.shape[0]
        EQ = np.zeros((C, nd), dtype=np.float32)
        KS = []
        for c in range(C):
            words = arc._content_words(questions[qi]["stem"] + " " + questions[qi]["choices"][c],
                                       CONTENT_MIN_LEN)
            acc, ks = aggregate_props(words, ckmap, pair_vec, filler_df, nd, K_FACT_PROPS)
            EQ[c] = chd[c] + GAMMA * acc
            KS.append(ks)
        return _l2_rows(EQ), KS

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

        # CONTENT features (full / single-group / random-permuted)
        EQ_full, KS_full = choice_enr(qi, concept_keys)
        EQ_single, KS_single = choice_enr(qi, concept_keys_s)
        EQ_rand, KS_rand = choice_enr(qi, concept_keys_r)
        Xenr = enriched_features(pool_idx, enr_fact_full, FK_full, filler_df, EQ_full, KS_full)
        Xsingle = enriched_features(pool_idx, enr_fact_single, FK_single, filler_df, EQ_single, KS_single)
        Xrand = enriched_features(pool_idx, enr_fact_rand, FK_rand, filler_df, EQ_rand, KS_rand)

        # coverage-filtered subset: pool has facts sharing >=2 distinguishing property keys with a choice
        qks_union = set()
        for ks in KS_full:
            qks_union |= ks
        n_distinguishing = 0
        for i in pool_idx.tolist():
            if len(FK_full[i] & qks_union) >= 1:
                n_distinguishing += 1
        covered_subset[qi] = (len(qks_union) >= 2 and n_distinguishing >= 2)

        Xn_flat[qi] = _minmax_cols(Xflat)
        Xn_enr[qi] = _minmax_cols(Xenr)
        Xn_comb[qi] = _minmax_cols(np.concatenate([Xflat, Xenr], axis=1))
        Xn_single[qi] = _minmax_cols(Xsingle)
        Xn_rand[qi] = _minmax_cols(Xrand)
        gold_rows_list[qi] = np.array([uid2fi[u] for u in q["gold_central"] if u in uid2fi], dtype=np.int64)

        # FIX-TOOK diagnostic: RAW enr_cos_max (feat col 0) + acr_distinct (feat col 3) on ON-TOPIC GOLD
        # pool facts (v1 had enr_cos NEGATIVE everywhere; clean-enriched must go POSITIVE and differ from
        # RANDOM at the feature level). enr_cos_idx=0, acr_idx=3 in ENR_FEATURE_NAMES.
        gold_set_ft = set(int(g) for g in gold_rows_list[qi].tolist())
        gpos = [li for li, fi in enumerate(pool_idx.tolist()) if fi in gold_set_ft]
        if gpos:
            enr_cos_gold_vals.extend(Xenr[gpos, 0].tolist())
            enr_cos_rand_gold_vals.extend(Xrand[gpos, 0].tolist())
            acr_gold_vals.extend(Xenr[gpos, 3].tolist())
            acr_rand_gold_vals.extend(Xrand[gpos, 3].tolist())

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

    arm_feat = {"A_thin": Xn_flat, "B_enriched": Xn_enr, "C_combined": Xn_comb,
                "B_single": Xn_single, "RANDOM": Xn_rand}
    arm_names = {"A_thin": list(FLAT_FEATURE_NAMES), "B_enriched": list(ENR_FEATURE_NAMES),
                 "C_combined": list(FLAT_FEATURE_NAMES) + list(ENR_FEATURE_NAMES),
                 "B_single": list(ENR_FEATURE_NAMES), "RANDOM": list(ENR_FEATURE_NAMES)}
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

    # ---- FIX-TOOK FIRST GATE (reported BEFORE the verdict): did the deconfound take? ----
    # v1 pathology: enr_cos NEGATIVE for on-topic gold everywhere (property mass drowned thin cosine) AND
    # clean B ~= RANDOM at the feature level. v2 must reverse BOTH: enr_cos_gold_mean POSITIVE and clean
    # acr_distinct on gold materially above RANDOM.
    def _mean(v):
        return round(float(np.mean(v)), 4) if v else None

    enr_cos_gold_mean = _mean(enr_cos_gold_vals)
    enr_cos_rand_gold_mean = _mean(enr_cos_rand_gold_vals)
    acr_gold_mean = _mean(acr_gold_vals)
    acr_rand_gold_mean = _mean(acr_rand_gold_vals)
    enr_cos_gold_pos_frac = (round(float(np.mean(np.asarray(enr_cos_gold_vals) > 0.0)), 4)
                             if enr_cos_gold_vals else None)
    fix_enr_cos_positive = bool(enr_cos_gold_mean is not None and enr_cos_gold_mean > 0.0)
    fix_clean_neq_random = bool(acr_gold_mean is not None and acr_rand_gold_mean is not None
                                and acr_gold_mean > acr_rand_gold_mean + FIX_TOOK_EPS)
    fix_took = bool(fix_enr_cos_positive and fix_clean_neq_random)
    print(f"[FIX-TOOK] enr_cos_gold_mean={enr_cos_gold_mean} (v1 NEGATIVE) pos_frac={enr_cos_gold_pos_frac} "
          f"| acr_gold={acr_gold_mean} vs RANDOM_gold={acr_rand_gold_mean} "
          f"| enr_cos_positive={fix_enr_cos_positive} clean_neq_random={fix_clean_neq_random} "
          f"=> fix_took={fix_took}", flush=True)

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

        for name in FEATURE_ARMS:
            sel_glob = pool_idx[sel_local[name]]
            picks[name][qi] = combiner_pick(qi, sel_glob)
            denom = min(K_SEL, sel_glob.size) if sel_glob.size else 1
            sel_gold_hit[name][qi] = sum(1 for g in sel_glob.tolist() if g in gold_set) / denom
        picks["ORACLE"][qi] = combiner_pick(qi, gold_rows)
        sel_gold_hit["ORACLE"][qi] = 1.0 if gold_rows.size else 0.0

        if len(glass) < 14 and lure_flags[qi] and test_mask[qi]:
            b_local = sel_local["B_enriched"]
            Xr = Xn_enr[qi]
            contrib = {}
            for li in b_local.tolist():
                fi = int(pool_idx[li])
                contrib[str(fi)] = {
                    "sent": uid2sent.get(uids[fi], "")[:70],
                    "property_keys": sorted([f"{g}:{f}" for (g, f) in FK_full[fi]])[:6],
                    "feat": {ENR_FEATURE_NAMES[j]: round(float(Xr[li, j] * arm_w["B_enriched"][j]), 4)
                             for j in range(len(ENR_FEATURE_NAMES))},
                    "is_gold": int(fi in gold_set)}
            glass.append({
                "qid": q["qid"], "stem": q["stem"][:120], "choices": q["choices"],
                "correct_index": q["correct_index"], "split": "test",
                "covered_subset": bool(covered_subset[qi]),
                "gold_in_wide_pool": sum(1 for i in pool_idx.tolist() if i in gold_set),
                "picks": {name: int(picks[name][qi]) for name in ARMS},
                "B_enriched_selected": [uid2sent.get(uids[i], "")[:60]
                                        for i in pool_idx[b_local].tolist()],
                "A_thin_selected": [uid2sent.get(uids[i], "")[:60]
                                    for i in pool_idx[sel_local["A_thin"]].tolist()],
                "B_selected_gold": [int(i in gold_set) for i in pool_idx[b_local].tolist()],
                "A_selected_gold": [int(i in gold_set) for i in pool_idx[sel_local["A_thin"]].tolist()],
                "B_enriched_contributions": contrib,
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
    train_cov_sub = train_chal & covered_subset

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
            "insample_train_precision": selprec(train_chal, name),        # PRIMARY sharp number
            "insample_covered_subset_precision": selprec(train_cov_sub, name),
            "test_sel_gold_precision": selprec(test_chal, name),
        }
        print(f"[acc] {name}: insample_prec={accs[name]['insample_train_precision']} "
              f"subset_prec={accs[name]['insample_covered_subset_precision']} "
              f"test_prec={accs[name]['test_sel_gold_precision']} "
              f"test_chal={accs[name]['test_challenge']}", flush=True)

    # ---- PLANTED dam mechanism (measured here so the FULL metrics carry it, not just self-test) ----
    _heartbeat(output_dir, "dam_mechanism")
    planted = _planted_dam_discriminator(nd=nd)
    plant_margin_lift = planted["margin_lift"]
    plant_fires = bool(plant_margin_lift >= PLANT_MECH_HP)
    print(f"[dam] thin_margin={planted['thin_margin']} enr_margin={planted['enr_margin']} "
          f"lift={plant_margin_lift} fires={plant_fires}", flush=True)

    # ---- PRIMARY: in-sample precision A vs B; RANDOM collapse; end-to-end ----
    A_prec = accs["A_thin"]["insample_train_precision"] or 0.0
    B_prec = accs["B_enriched"]["insample_train_precision"] or 0.0
    C_prec = accs["C_combined"]["insample_train_precision"] or 0.0
    S_prec = accs["B_single"]["insample_train_precision"] or 0.0
    R_prec = accs["RANDOM"]["insample_train_precision"] or 0.0
    prec_lift = round(B_prec - A_prec, 4)
    random_collapses = bool(R_prec <= A_prec + RANDOM_COLLAPSE_EPS)
    baseline_regress_ok = BASELINE_PREC_LO <= A_prec <= BASELINE_PREC_HI

    A_sub = accs["A_thin"]["insample_covered_subset_precision"]
    B_sub = accs["B_enriched"]["insample_covered_subset_precision"]
    subset_hp = bool(B_sub is not None and B_sub >= ENR_SUBSET_HP)

    A_chal = accs["A_thin"]["test_challenge"] or 0.0
    B_chal = accs["B_enriched"]["test_challenge"] or 0.0
    C_chal = accs["C_combined"]["test_challenge"] or 0.0
    oracle_chal = accs["ORACLE"]["test_challenge"] or 0.0
    gap = round(oracle_chal - A_chal, 4)
    best_repr = "C_combined" if C_chal >= B_chal else "B_enriched"
    best_chal = max(B_chal, C_chal)
    best_lift = round(best_chal - A_chal, 4)
    gap_frac_closed = round(best_lift / gap, 4) if gap > 1e-9 else None

    B_test_prec = accs["B_enriched"]["test_sel_gold_precision"] or 0.0
    A_test_prec = accs["A_thin"]["test_sel_gold_precision"] or 0.0

    mc_b, mc_c, mc_stat, mc_p = gate.mcnemar(correct["A_thin"][test_chal],
                                             correct[best_repr][test_chal])
    sig = (mc_p is not None) and (mc_p < MCNEMAR_ALPHA)

    # ---- integrity gates ----
    ag_saturated = A_chal >= AG_BASELINE_SAT
    baseline_in_band = 0.05 < A_chal < 0.95
    digests = {name: hashlib.sha256(picks[name].tobytes()).hexdigest() for name in ARMS}
    n_distinct = len(set(digests[n] for n in FEATURE_ARMS))
    arms_differ = n_distinct >= 4
    enr_nontrivial = bool(np.any(np.abs(arm_w["B_enriched"]) > 1e-6))
    coverage_bound = bool(q_cov < COVERAGE_MIN)

    # predictions
    pred1_hp = bool(prec_lift >= ENR_LIFT_HP and random_collapses)
    pred1_hf = bool(prec_lift <= ENR_LIFT_HF)
    pred2_hp = plant_fires
    pred4_hp = bool(best_lift >= CHAL_LIFT_HP and sig)

    # ---- HARD-FAIL sub-diagnosis (only meaningful when Pred1 fails) ----
    sub_diag = None
    if pred1_hf:
        # which property table type dominates the covered concepts? (granularity check)
        gcov = defaultdict(int)
        for w in sorted(props.keys()):
            for (g, f) in _select_props(props[w], filler_df, K_PROPS):
                gcov[g] += 1
        dom_group = max(gcov.items(), key=lambda kv: kv[1])[0] if gcov else None
        if q_cov < COVERAGE_MIN:
            sub_diag = ("coverage: question-concept property coverage too thin "
                        f"(q_cov={q_cov} < {COVERAGE_MIN}); redirect = broader property source / curriculum breadth")
        elif dom_group in ("KIND", "PROP") and not plant_fires:
            sub_diag = ("granularity: covered concepts get mostly generic/shared property rows "
                        f"(dominant group={dom_group}); mechanism-specific SOURCE/CAUSE/REQUIRES rows sparse; "
                        "redirect = finer property source or perceptual grounding")
        elif plant_fires:
            sub_diag = ("scorer/content: the binding mechanism IS content-faithful (dam mechanism fires) but "
                        "the enriched content does NOT separate THESE real gold-vs-lure pairs linearly; redirect "
                        "= nonlinear learner on the richer features OR deeper perceptual grounding")
        else:
            sub_diag = ("capacity: property bundling + cosine readout does not carry the content at this "
                        "dim/noise (dam mechanism weak); redirect = capacity bounds check or grounding")

    # ---- verdict ----
    if ag_saturated:
        verdict = "CONTENT_ENRICHMENT_SATURATED"
        vmsg = f"baseline A_thin TEST Challenge {A_chal} >= {AG_BASELINE_SAT}: no headroom (report)."
    elif not arms_differ:
        verdict = "CONTENT_ENRICHMENT_ARMS_IDENTICAL_META_RULE_AF"
        vmsg = (f"feature arms produced < 4 distinct pick-vectors (n_distinct={n_distinct}); arm bug -- "
                f"do NOT trust the comparison.")
    elif not enr_nontrivial:
        verdict = "CONTENT_ENRICHMENT_DEGENERATE"
        vmsg = "enriched learner weights ~= 0 (no content feature separates gold on TRAIN); inspect."
    elif coverage_bound and pred1_hf:
        verdict = "CONTENT_ENRICHMENT_COVERAGE_BOUND"
        vmsg = (f"COVERAGE-BOUND (report STRAIGHT): question-concept property coverage {q_cov} < "
                f"{COVERAGE_MIN} AND enriched does not beat thin in-sample (B={B_prec} vs A={A_prec}, "
                f"lift {prec_lift:+.4f}). The lever needs BROADER property data. Covered-subset precision "
                f"B={B_sub} vs A={A_sub} (n where measurable). dam mechanism fires={plant_fires}.")
    elif pred1_hp and pred2_hp and pred4_hp:
        verdict = "CONTENT_ENRICHMENT_HARD_PASS"
        vmsg = (f"content-enriched MEANING beats content-thin ON ALL THREE: in-sample precision B={B_prec} "
                f"vs A={A_prec} (lift {prec_lift:+.4f} >= {ENR_LIFT_HP}); RANDOM-property collapses "
                f"(R={R_prec} <= A+{RANDOM_COLLAPSE_EPS}); dam mechanism separates hydro gold from lures "
                f"(margin lift {plant_margin_lift} >= {PLANT_MECH_HP}); end-to-end {best_repr} TEST Challenge "
                f"{best_chal} vs A {A_chal} (lift {best_lift:+.4f}, {gap_frac_closed} of the {gap} gap; "
                f"McNemar p={mc_p} < {MCNEMAR_ALPHA}). Binding concept properties closes real precision.")
    elif (pred1_hp or subset_hp or pred2_hp) and not pred1_hf:
        verdict = "CONTENT_ENRICHMENT_MIDDLE_BAND"
        vmsg = (f"MIDDLE (likely-honest outcome): representational lift and/or mechanism REAL but end-to-end "
                f"not decisive. in-sample precision B={B_prec} vs A={A_prec} (lift {prec_lift:+.4f}); "
                f"covered-subset B={B_sub} vs A={A_sub} (subset_hp={subset_hp}); RANDOM collapses="
                f"{random_collapses} (R={R_prec}); B_single={S_prec} (hub-binding: B>{S_prec}={bool(B_prec > S_prec)}); "
                f"dam mechanism fires={plant_fires} (lift={plant_margin_lift}); end-to-end {best_repr} "
                f"Challenge {best_chal} vs A {A_chal} (lift {best_lift:+.4f}, McNemar p={mc_p} sig={sig}). "
                f"Real but partial -> redirect residual to property-table breadth OR a nonlinear learner "
                f"on the richer content features.")
    else:
        verdict = "CONTENT_ENRICHMENT_HARD_FAIL"
        vmsg = (f"HONEST CEILING: content-enriched features do NOT beat content-thin in-sample "
                f"(B={B_prec} vs A={A_prec}, lift {prec_lift:+.4f} <= {ENR_LIFT_HF}). Bound property "
                f"content carries no material separable signal for ARC selection here. Sub-diagnosis: "
                f"{sub_diag}. dam mechanism fires={plant_fires} (lift={plant_margin_lift}); RANDOM "
                f"collapses={random_collapses}; end-to-end {best_repr} lift={best_lift:+.4f}. Redirect = "
                f"deeper perceptual grounding / richer property source (report STRAIGHT).")

    # FIX-TOOK FIRST GATE prefix (reported BEFORE the verdict claim, per task)
    vmsg = (f"[FIX-TOOK fix_took={fix_took}: enr_cos_gold_mean={enr_cos_gold_mean} (v1 NEGATIVE) "
            f"pos_frac={enr_cos_gold_pos_frac}; acr_gold={acr_gold_mean} vs RANDOM_gold={acr_rand_gold_mean}] "
            + vmsg)
    if not fix_took:
        vmsg = ("[FIX-DID-NOT-TAKE] deconfound did not reverse the v1 pathology (enr_cos still "
                "non-positive for gold OR clean ~= RANDOM at the feature level); the clean hypothesis is "
                "NOT cleanly presented in isolation -- treat the arm comparison below with caution. " + vmsg)

    grade = arc._grade_proxy(accs["B_enriched"]["test_easy"], accs["B_enriched"]["test_challenge"])

    metrics = {
        "verdict": verdict, "verdict_msg": vmsg,
        "summary": (f"{verdict}: [FIX-TOOK={fix_took} enr_cos_gold={enr_cos_gold_mean} acr_gold={acr_gold_mean} "
                    f"vs RAND {acr_rand_gold_mean}]; [in-sample prec] A={A_prec} B={B_prec} C={C_prec} "
                    f"B_single={S_prec} RANDOM={R_prec} (lift B-A={prec_lift:+.4f}); [subset] A={A_sub} B={B_sub}; "
                    f"[dam] margin_lift={plant_margin_lift} fires={plant_fires} (CONSTRUCTION-DETERMINED); "
                    f"[TEST Chal] A={A_chal} B={B_chal} C={C_chal} ORACLE={oracle_chal} "
                    f"best_lift={best_lift:+.4f} McNemar_p={mc_p}; q_cov={q_cov} fact_cov={fact_cov} "
                    f"| chance={round(chance,4)}"),
        "elapsed_s": round(time.perf_counter() - _T0[0], 1),
        "ts_iso": datetime.now(timezone.utc).isoformat(),
        "anchor_name": ANCHOR_NAME, "mode": mode, "run_mode": mode,
        "n_dim": nd, "seed": SEED,
        "gamma": GAMMA, "k_props": K_PROPS, "single_group": single_group,
        "n_questions": nQ, "n_easy": n_easy, "n_challenge": n_chal,
        "n_train": int(train_mask.sum()), "n_test": int(test_mask.sum()),
        "n_test_challenge": int(np.sum(test_chal)), "n_train_challenge": int(np.sum(train_chal)),
        "n_train_covered_subset": int(np.sum(train_cov_sub)),
        "n_covered_subset_total": int(np.sum(covered_subset)),
        "n_train_rows": n_train_rows, "n_train_gold_pos": n_train_pos,
        "chance_theoretical": round(chance, 4),
        "store_facts": nFacts, "graph_terms": nTerms,
        # FIRST GATE: coverage
        "question_concept_property_coverage": q_cov, "fact_property_coverage": fact_cov,
        "n_property_concepts": len(props), "n_unique_fillers": len(filler_df),
        "coverage_min": COVERAGE_MIN, "coverage_bound": coverage_bound,
        # FIX-TOOK FIRST GATE (deconfound diagnostics; reported BEFORE the verdict)
        "df_threshold": round(df_thr, 2), "n_hub_words_dropped": int(n_hub_dropped),
        "k_fact_props": K_FACT_PROPS, "enrich_df_pctl": ENRICH_DF_PCTL,
        "fix_took": {
            "enr_cos_gold_mean": enr_cos_gold_mean, "enr_cos_gold_positive_frac": enr_cos_gold_pos_frac,
            "enr_cos_random_gold_mean": enr_cos_rand_gold_mean,
            "acr_distinct_gold_mean": acr_gold_mean, "acr_distinct_random_gold_mean": acr_rand_gold_mean,
            "enr_cos_positive": fix_enr_cos_positive, "clean_neq_random_feature": fix_clean_neq_random,
            "fix_took": fix_took, "eps": FIX_TOOK_EPS,
            "note": ("v1 had enr_cos NEGATIVE for on-topic gold everywhere and B ~= RANDOM. fix_took=True "
                     "means the deconfound reversed both (enr_cos positive AND clean acr_distinct on gold "
                     "materially above RANDOM); the clean hypothesis is then genuinely presented in isolation.")},
        # selection + learner config
        "k_wide": K_WIDE, "k_sel": K_SEL, "rr_top_t": RR_TOP_T, "mu_supp": MU_SUPP,
        "l2_reg": learned.L2_REG, "gd_iters": learned.GD_ITERS, "gd_lr": learned.GD_LR,
        "split_frac_train": learned.SPLIT_FRAC_TRAIN,
        # GLASS-BOX: inspectable learned weights per arm + content feature names + groups
        "flat_feature_names": list(FLAT_FEATURE_NAMES),
        "enr_feature_names": list(ENR_FEATURE_NAMES),
        "relation_groups": list(GROUPS),
        "learned_weights_by_arm": arm_weights,
        "enr_learner_nontrivial": enr_nontrivial,
        # PRIMARY: in-sample TRAIN precision by arm (sharp; 29545 ceiling ~0.186)
        "insample_train_precision_by_arm": {n: accs[n]["insample_train_precision"] for n in ARMS},
        "A_insample_precision": A_prec, "B_insample_precision": B_prec,
        "C_insample_precision": C_prec, "B_single_insample_precision": S_prec,
        "RANDOM_insample_precision": R_prec,
        "insample_precision_lift_B_minus_A": prec_lift,
        "random_property_collapses": random_collapses, "random_collapse_eps": RANDOM_COLLAPSE_EPS,
        "baseline_precision_regression_ok": baseline_regress_ok,
        # coverage-filtered subset precision (the sharpest fair measurement)
        "insample_covered_subset_precision_by_arm": {
            n: accs[n]["insample_covered_subset_precision"] for n in ARMS},
        "A_covered_subset_precision": A_sub, "B_covered_subset_precision": B_sub,
        "subset_hard_pass": subset_hp,
        # hub multi-feature binding ablation (B vs B_single)
        "hub_binding": {"B_enriched_precision": B_prec, "B_single_precision": S_prec,
                        "multi_feature_beats_single": bool(B_prec > S_prec)},
        # MECHANISM: planted dam -- BIND/BUNDLE-MATH PROOF ONLY (CONSTRUCTION-DETERMINED; the shared
        # bound-property components align by construction). Does NOT license a content-faithfulness claim
        # on real data -- the real-data test is the fix-took gate + in-sample precision + end-to-end.
        "dam_mechanism": {"thin_margin": planted["thin_margin"], "enr_margin": planted["enr_margin"],
                          "margin_lift": plant_margin_lift, "fires": plant_fires,
                          "hp_threshold": PLANT_MECH_HP, "thin_sims": planted["thin_sims"],
                          "enr_sims": planted["enr_sims"],
                          "interpretation": "CONSTRUCTION-DETERMINED bind/bundle-math proof only; "
                                            "not evidence of content-faithfulness on real ARC data"},
        # SECONDARY: end-to-end accuracy by arm on TEST (judged on the ANSWER)
        "acc_by_arm": accs,
        "A_thin_test_challenge": A_chal, "B_enriched_test_challenge": B_chal,
        "C_combined_test_challenge": C_chal, "oracle_gold_test_challenge": oracle_chal,
        "selection_gap": gap,
        "best_repr_arm": best_repr, "best_repr_lift_challenge": best_lift,
        "gap_fraction_closed": gap_frac_closed,
        "test_sel_gold_precision_A": A_test_prec, "test_sel_gold_precision_B": B_test_prec,
        "mcnemar_challenge": {"arm": best_repr, "b_A_right_arm_wrong": mc_b,
                              "c_A_wrong_arm_right": mc_c,
                              "stat": None if mc_stat is None else round(mc_stat, 4),
                              "p_value": None if mc_p is None else round(mc_p, 5),
                              "significant": bool(sig)},
        "test_sel_gold_precision_by_arm": {n: accs[n]["test_sel_gold_precision"] for n in ARMS},
        # predictions (from the drill)
        "pred1_representational_hp": pred1_hp, "pred1_hard_fail": pred1_hf,
        "pred2_mechanism_hp": pred2_hp, "pred4_endtoend_hp": pred4_hp,
        "hard_fail_sub_diagnosis": sub_diag,
        # gates / integrity
        "baseline_in_band": bool(baseline_in_band), "ag_saturated": bool(ag_saturated),
        "arms_differ_verified": bool(arms_differ), "n_distinct_pick_vectors": int(n_distinct),
        "arm_pick_digests": digests,
        "bands": {"ENR_LIFT_HP": ENR_LIFT_HP, "ENR_LIFT_HF": ENR_LIFT_HF, "ENR_SUBSET_HP": ENR_SUBSET_HP,
                  "RANDOM_COLLAPSE_EPS": RANDOM_COLLAPSE_EPS, "PLANT_MECH_HP": PLANT_MECH_HP,
                  "CHAL_LIFT_HP": CHAL_LIFT_HP, "MB_CHAL_LIFT": MB_CHAL_LIFT, "COVERAGE_MIN": COVERAGE_MIN,
                  "mcnemar_alpha": MCNEMAR_ALPHA, "ag_baseline_sat": AG_BASELINE_SAT},
        "grade_proxy": grade,
        "wired_vs_stubbed": (
            "WIRED: the CONCEPT MEANING content is the ONLY variable. The WIDE re-retrieval pool (RR "
            "top-100, mr.reformulate_seeds/_rownorm_scores IMPORTED UNCHANGED, built on THIN term "
            "encodings) and the bind+bundle combiner (agg.aggregate 'bundle' IMPORTED UNCHANGED) are held "
            "fixed. Arm A_thin reuses 29545's EXACT flat feature assembly + glass-box learner (imported) -> "
            "regression-anchor to the ~0.186 in-sample ceiling. Arm B_enriched binds each concept's up-to-K "
            "DISTINCTIVE WorldTree property fillers under their relation-GROUP role key (the SAME bipolar "
            "binding EventBundleCodec/hd_fact_store use) and ADDS them (gamma-weighted; gamma=0 recovers thin "
            "EXACTLY) to the thin vector; features = enriched fact-vs-question cosine (max/mean) + symbolic "
            "shared-property overlap + distinctiveness-weighted match + coverage. C_combined = flat+content. "
            "B_single = content from the single highest-coverage group only (hub multi-feature ablation). "
            "RANDOM permutes the concept->property assignment (must collapse toward A). ORACLE = gold ceiling. "
            "PLANTED dam mechanism: enriched separates hydro gold from nuclear/coal lures where the thin base "
            "is near-equal (the case where relation-STRUCTURE (29546) provably cannot help). NO LEAK: "
            "TRAIN/TEST disjoint (learned._split_train_test); learner never sees TEST gold; gold used for "
            "TRAIN label + ORACLE + eval only. FIRST GATE = property coverage (reported). PRIMARY = in-sample "
            "TRAIN precision; SECONDARY = TEST sel_gold_precision + end-to-end Challenge + McNemar + covered-"
            "subset precision; MECHANISM = dam margin lift. STUBBED/NOTED-NOT-BUILT: perceptual grounding + "
            "nonlinear learner (the redirects if this HARD_FAILs)."),
        "contract": ("INLINE-LOCAL foreground-to-completion; no push/remote-persist; NOT remote-portable "
                     "(GloVe+WorldTree git-ignored/large; inherits 29544/29545/29546 contract); VET-PENDING; "
                     "FULL eval slice bounded (limit_easy=500 limit_chal=600, stratified) to fit one "
                     "foreground call"),
        "compute_architecture": ("mixed CPU: batched GloVe encode (store + unique property fillers + terms + "
                                 "questions) + scipy sparse batched PPR (2 passes, UNCHANGED) + numpy "
                                 "elementwise property bind + sum (cheap) + per-question feature assembly "
                                 "(continuous cosine + symbolic set-intersection overlap) + 5 glass-box "
                                 "full-batch logreg trains (deterministic zero-init GD) + UNCHANGED combiner; "
                                 "wall target < 10min. No GPU speedup needed (matmuls small)."),
        "storage_strategy": "sharded (each fact = own thin embedding + own property bundle + own graph node)",
        "progress_logging": "line_buffered_stdout",
        "calibration_check": ("default_ok_for_this_regime (learner hyperparams inherited from 29545 "
                              "L2/iters/lr author-set a priori; wide pool + combiner UNCHANGED; GAMMA=0.5, "
                              "K_PROPS=6, relation->group map author-set a priori NOT tuned to force a win; "
                              "RANDOM-property must-fail control present; the dam mechanism is analytic "
                              "(shared bound-property components align by construction) so the discriminator "
                              "survives scale)"),
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
