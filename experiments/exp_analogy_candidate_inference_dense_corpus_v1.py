"""exp_analogy_candidate_inference_dense_corpus_v1

DECISIVE mechanism-vs-data test. v2 (commit 5b2ff9f2e, HARD_FAIL) ruled out our alignment MECHANISM
(2x2 ablation: capacity + structured-SME alignment both neutral/negative) and isolated the wall to
CORPUS RELATION-SPARSITY: WorldTree gives each concept a median 1-2 relations (17% ZERO structure),
but structure-mapping analogy needs concepts embedded in RICH multi-relation webs. This cell swaps the
sparse WorldTree corpus for a DENSE + CLEAN relational corpus and asks: does the SAME v2 mechanism beat
the FREQUENCY_PRIOR when concepts have brain-realistic relational density?

THE ONE CHANGE = the CORPUS (and the density-based held-out-head selection it enables). Everything else
-- the v2 mechanism (capacity-limited + SME structural alignment), the leak-proof exclusion-from-ALL-
storage, the STORE_RECALL_FLOOR arm, the FLAT-MLP baseline, the FREQUENCY_PRIOR arm (the bar), the 3
must-fail controls (SCRAMBLED / SHUFFLED / RANDOM_ALIGNMENT), random-ID content (NO borrowed embedding),
and the entire verdict logic -- is REUSED VERBATIM from v2 via importlib exec + monkeypatch of the two
corpus entry points (load loader + split). Zero copy of the mechanism or verdict code.

CORPUS = WordNet (nltk, on disk). Typed synset/lemma relations, ONE canonical direction per inverse
pair so leak-proofing stays the single f[0]==R test (do NOT include hyponym alongside hypernym: the
inverse edge would leak the held-out answer). Relations extracted:
  antisym (one direction): HYPERNYM, PART_MERONYM, MEMBER_MERONYM, SUBSTANCE_MERONYM, ENTAILMENT, CAUSE
  symmetric (self-inverse): SIMILAR_TO, ALSO_SEE, VERB_GROUP, ATTRIBUTE
  lemma-level (self-inverse): DERIV (derivationally-related-forms), ANTONYM
Concept id = synset.name() (e.g. "dog.n.01"; unique). Content is random-ID (zero pretrained semantics).

DENSITY FILTER (the lever, coordinator fair-test refinement 29581): raw edges-per-concept is NOT the
bottleneck -- SHARED-EXACT-PARTNER (twin) correspondence is what SME one-to-one alignment consumes. So
(a) the PRIMARY held-out relation is HYPERNYM: LOW-FANOUT (median 1.0 hypernym/head => unambiguous tail
projection) and co-hyponyms are twin candidates -- high-fanout relations (many valid tails) fail for a
SEPARATE tail-ambiguity reason density cannot fix and are avoided as the decisive bar; (b) held-out
heads are selected GOLD-INDEPENDENTLY by non-R partner degree >= min_nonr_deg (brain-realistic density),
NOT by twin availability (that would leak the answer); (c) the cell REPORTS the twin diagnostic -- the
fraction of selected dense heads that have a twin sharing >=2 exact non-R partners, and the fraction
with a USABLE co-hyponym twin (a twin that also shares the gold hypernym, so its projection is correct)
-- this USABLE-twin fraction is the mechanism's realistic top-1 ceiling and is the REAL density metric.

DECISIVE READ (unchanged bands from v2 verdict logic):
  - ANALOGY_v2 beats FREQUENCY_PRIOR by >=0.15 (and FLAT, clears floor) + positive outdeg corr
    => HARD_PASS: mechanism IS sound; WorldTree failure was DATA (alignable-twin) sparsity. The brain-
       true fix is to BUILD relational density; the mechanism then works.
  - ANALOGY_v2 ties/loses FREQUENCY_PRIOR even with provable twins available
    => mechanism itself is insufficient (not just data); iterate mechanism or reconsider.
  - MIDDLE_BAND (beats freq by 0.05-0.15): density helps but is capped by realized twin availability.

Design-of-record: coordinator message 29581 (dense-corpus fair-test refinement) + v2 VET.
Base cell forked: experiments/exp_analogy_candidate_inference_heldout_edge_v2.py (commit 5b2ff9f2e).

MEASURED (pre-flight probes, this session; see completion report):
  - WordNet HYPERNYM dense pool at non-R deg>=8: 867 heads; USABLE co-hyponym twin rate 0.218
    (within twin-centered induced corpus n_dict~14694 n_triples~28874).  MEASURED@pre-flight-probe
  - FREQUENCY_PRIOR top-10 gold coverage of dense heads: 0.078 (the bar).      MEASURED@pre-flight-probe
  - HYPERNYM tail fanout: median 1.0 mean 1.02 (low-fanout, unambiguous).      MEASURED@pre-flight-probe
  - WorldTree per-concept relation median: 1-2 (the sparsity v2 hit).          CITED@v2 verdict 5b2ff9f2e

CELL-TEMPLATE MANDATORY (inherited verbatim from v2 run_experiment/verdict + this cell's loader):
# - arms_differ_verified at smoke gate (META_RULE_AF; ANALOGY_v2-involving collision gates)
# - final_metrics_atomicity = tmp_replace (META_RULE_AH)
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: prediction-accuracy discriminator; base_rate=1/n_dict + FREQUENCY_PRIOR reported as floors
# - baseline_in_band: EXEMPT (STORE_RECALL_FLOOR/FLAT/FREQUENCY_PRIOR are intended-floor baselines)
# - discriminator survives scale: smoke at full-N (N=1024) on HYPERNYM; planted self-test fires
# - HARD_PASS strictly above floor + margin (beats FREQ_PRIOR by >=0.15 AND FLAT by clear margin)
# - HP_SCOPE per-arm declaration (ANALOGY_v2 only)
# - cardinality_ok: EXPECTED_N_UNITS gate (inherited)
# - per-unit failure-class instrumentation (no bare except; inherited)
# - all numbers tagged MEASURED@/CITED@/THEORETICAL@ (above)
# - deterministic seeding (fixed ints, np.random.RandomState; sorted(set()); NO hash())
# - leak-proof: ONE direction per inverse relation pair (no hyponym alongside hypernym)

ASCII-only. No emojis. No em dashes in output.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import platform
import sys
import time
import traceback
from collections import defaultdict, Counter
from datetime import datetime, timezone

import numpy as np
import torch

try:
    sys.stdout.reconfigure(line_buffering=True)
except Exception:
    pass

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ANCHOR_NAME = "exp_analogy_candidate_inference_dense_corpus_v1"

# ---------------------------------------------------------------------------
# Verbatim reuse: exec the v2 module (which itself execs the TEM ref + v1). We pull the mechanism,
# the analogy-family evaluator, run_experiment (verdict logic), the infra + the split we will restore
# for the planted self-test. THE ONE CHANGE is a monkeypatch of two corpus entry points below.
# ---------------------------------------------------------------------------
_V2_PATH = os.path.join(REPO, "experiments", "exp_analogy_candidate_inference_heldout_edge_v2.py")
_v2spec = importlib.util.spec_from_file_location("_analogy_v2", _V2_PATH)
_v2 = importlib.util.module_from_spec(_v2spec)
_v2spec.loader.exec_module(_v2)  # top-level only defines functions; main is __main__-guarded

# original (WorldTree) entry points -- kept so the planted self-test uses the ORIGINAL split.
_ORIG_LOAD = _v2.load_worldtree_triples
_ORIG_SPLIT = _v2.build_analogy_split
run_experiment = _v2.run_experiment
eval_analogy_family = _v2.eval_analogy_family
eval_store_recall_floor = _v2.eval_store_recall_floor
build_analogy_split_v1 = _v2.build_analogy_split  # v1 logic (verbatim) used by planted test

# module-level config the monkeypatched loader/split read (set in main before run_experiment).
_CFG = {}


def _progress(msg):
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)


# ===========================================================================
# THE ONE CHANGE (1/2): WordNet dense-corpus loader.
# Returns (triples, rel_names) in the EXACT (rel_name, head, tail) string format the whole downstream
# pipeline (build_analogy_split -> build_profiles -> scorer -> floor/flat/freq) already consumes.
# ===========================================================================

# ONE canonical direction per inverse pair (leak-proof). Symmetric + lemma relations are self-inverse.
def _wordnet_raw_triples():
    from nltk.corpus import wordnet as wn
    syn_antisym = {
        "HYPERNYM": lambda s: s.hypernyms() + s.instance_hypernyms(),
        "PART_MERONYM": lambda s: s.part_meronyms(),
        "MEMBER_MERONYM": lambda s: s.member_meronyms(),
        "SUBSTANCE_MERONYM": lambda s: s.substance_meronyms(),
        "ENTAILMENT": lambda s: s.entailments(),
        "CAUSE": lambda s: s.causes(),
    }
    syn_sym = {
        "SIMILAR_TO": lambda s: s.similar_tos(),
        "ALSO_SEE": lambda s: s.also_sees(),
        "VERB_GROUP": lambda s: s.verb_groups(),
        "ATTRIBUTE": lambda s: s.attributes(),
    }
    triples = []
    seen = set()
    for s in wn.all_synsets():
        h = s.name()
        for rel, fn in syn_antisym.items():
            for t in fn(s):
                tn = t.name()
                if tn != h:
                    triples.append((rel, h, tn))
        for rel, fn in syn_sym.items():
            for t in fn(s):
                tn = t.name()
                if tn == h:
                    continue
                key = (rel,) + tuple(sorted((h, tn)))
                if key not in seen:
                    seen.add(key)
                    triples.append((rel, h, tn))
        for lem in s.lemmas():
            for d in lem.derivationally_related_forms():
                tn = d.synset().name()
                if tn != h:
                    key = ("DERIV",) + tuple(sorted((h, tn)))
                    if key not in seen:
                        seen.add(key)
                        triples.append(("DERIV", h, tn))
            for an in lem.antonyms():
                tn = an.synset().name()
                if tn != h:
                    key = ("ANTONYM",) + tuple(sorted((h, tn)))
                    if key not in seen:
                        seen.add(key)
                        triples.append(("ANTONYM", h, tn))
    return triples


def _nonr_partners(triples, R):
    """concept -> set of exact NON-R (rel, slot, partner) features (matches build_profiles keying)."""
    nonr = defaultdict(set)
    for (rel, a, b) in triples:
        if rel == R:
            continue
        nonr[a].add((rel, 0, b))
        nonr[b].add((rel, 1, a))
    return nonr


def build_wordnet_dense_corpus(heldout_rels, min_nonr_deg, max_dense_heads, seed,
                               max_concepts=2500, per_feat_cap=20):
    """Twin-centered dense corpus around density-selected held-out heads, BOUNDED for tractability.

    Returns (triples, rel_names, dense_heads_by_rel, density_report). Deterministic given args.
    The v2 analogy alignment is O(heads x sum_f |inv[f]|); an unbounded WordNet dictionary (~18k
    concepts, dense role-signature inverted lists) makes it intractable (killed at 42min). This bounds
    the corpus to <= max_concepts concepts -- an HONEST answer pool with real distractors (base_rate =
    1/n_dict reported) -- which bounds BOTH retrieval and alignment. Bounding the pool/search can only
    HURT analogy (fewer bases to align to), so the test stays FAIR/conservative. Leak-proofing (one
    direction per inverse pair) and the exclusion split are unchanged.

    Priority-kept concepts (so bounding does not delete the answer or the alignable structure):
      (1) all density-selected dense heads (candidates); (2) their exact non-R partners (alignment
      structure); (3) up to per_feat_cap co-owners per non-R feature (twins/bases -- capping only
      removes potential bases => conservative); (4) held-out-relation tails of all kept concepts (so
      bases can project the gold). Remaining budget to max_concepts is filled with RANDOM distractor
      concepts (seeded) from the full graph so the retrieval pool has genuine distractors.
    """
    raw = _wordnet_raw_triples()
    all_part = defaultdict(set)        # concept -> set((rel, partner))
    directed_heads = defaultdict(set)  # rel -> set(head)
    for (rel, a, b) in raw:
        all_part[a].add((rel, b))
        all_part[b].add((rel, a))
        directed_heads[rel].add(a)

    universe = set()
    dense_heads_by_rel = {}
    for R in heldout_rels:
        nonr = _nonr_partners(raw, R)
        inv = defaultdict(list)
        for c in sorted(nonr):                 # deterministic co-owner order
            for f in nonr[c]:
                inv[f].append(c)
        # gold-independent density selection: R-heads with >= min_nonr_deg exact non-R partners.
        cand = [a for a in directed_heads[R] if len(nonr.get(a, ())) >= min_nonr_deg]
        cand = sorted(cand, key=lambda a: (-len(nonr[a]), a))  # deterministic, densest first
        if max_dense_heads is not None:
            cand = cand[:max_dense_heads]
        dense_heads_by_rel[R] = list(cand)
        for a in cand:
            universe.add(a)
            for f in nonr[a]:
                universe.add(f[2])              # exact non-R partner (alignment structure)
                for co in inv[f][:per_feat_cap]:  # CAPPED co-owners (twins/bases; capping is conservative)
                    universe.add(co)
    # ensure held-out-relation tails of kept concepts are present so bases can project the gold.
    for a in list(universe):
        for R in heldout_rels:
            for (rel, b) in all_part[a]:
                if rel == R:
                    universe.add(b)
    # HARD CAP: bound to max_concepts. Keep all dense heads + a seeded fill (real distractors).
    must_keep = set()
    for R in heldout_rels:
        must_keep |= set(dense_heads_by_rel[R])
        for a in dense_heads_by_rel[R]:
            for (rel, b) in all_part[a]:
                if rel == R:
                    must_keep.add(b)            # gold tails / projection targets
    if len(universe) > max_concepts:
        rng = np.random.RandomState(seed)
        fill_pool = sorted(universe - must_keep)
        rng.shuffle(fill_pool)
        budget = max(0, max_concepts - len(must_keep))
        universe = must_keep | set(fill_pool[:budget])
    # induced subgraph on the universe (all relations retained -> non-R structure fully present).
    triples = [(rel, a, b) for (rel, a, b) in raw if a in universe and b in universe]
    rel_names = sorted(set(r for (r, _, _) in triples))
    # dense-heads-by-rel restricted to those still present as directed heads with in-corpus non-R deg.
    kept_heads = {}
    for R in heldout_rels:
        nonr_c = _nonr_partners(triples, R)
        present_heads = set(a for (rel, a, b) in triples if rel == R)
        kh = [a for a in dense_heads_by_rel[R]
              if a in present_heads and len(nonr_c.get(a, ())) >= min_nonr_deg]
        kept_heads[R] = kh
    density_report = _density_and_twin_report(triples, heldout_rels, min_nonr_deg, kept_heads)
    return triples, rel_names, kept_heads, density_report


def _density_and_twin_report(triples, heldout_rels, min_nonr_deg, dense_heads_by_rel):
    """Coordinator-requested REAL density metric: per-concept relation-count distribution AND
    shared-exact-partner (twin) density, per held-out relation. Twin = another concept sharing >=2
    exact non-R partners; USABLE twin = a twin that also shares the gold held-out tail (its projection
    is correct). USABLE-twin fraction is the mechanism's realistic top-1 ceiling."""
    report = {"n_triples": len(triples), "n_concepts": len(set([a for (_, a, _) in triples] +
                                                               [b for (_, _, b) in triples]))}
    per_rel = {}
    for R in heldout_rels:
        nonr = _nonr_partners(triples, R)
        tail_of = defaultdict(set)
        for (rel, a, b) in triples:
            if rel == R:
                tail_of[a].add(b)
        heads = list(dense_heads_by_rel.get(R, []))
        inv = defaultdict(set)
        for a in heads:
            for f in nonr.get(a, ()):
                inv[f].add(a)
        # measure over ALL heads (small enough); NON-R degree distribution (the WorldTree-1-2 lever).
        degs = np.array([len(nonr.get(a, ())) for a in heads], dtype=np.float64) if heads else np.array([0.0])
        has_twin = usable = 0
        for a in heads:
            cand = set()
            for f in nonr.get(a, ()):
                cand |= inv[f]
            cand.discard(a)
            twins = [b for b in cand if len(nonr[a] & nonr.get(b, set())) >= 2]
            if twins:
                has_twin += 1
                if any(tail_of.get(b, set()) & tail_of.get(a, set()) for b in twins):
                    usable += 1
        n = max(len(heads), 1)
        fan = np.array([len(v) for v in tail_of.values()], dtype=np.float64) if tail_of else np.array([0.0])
        per_rel[R] = {
            "n_dense_heads": len(heads),
            "min_nonr_deg": min_nonr_deg,
            "nonr_deg_median": float(np.median(degs)),
            "nonr_deg_mean": float(degs.mean()),
            "nonr_deg_p90": float(np.percentile(degs, 90)),
            "has_twin_frac": has_twin / n,
            "usable_cohypo_twin_frac": usable / n,   # realistic mechanism top-1 ceiling
            "tail_fanout_median": float(np.median(fan)),
            "tail_fanout_mean": float(fan.mean()),
        }
    report["per_heldout_relation"] = per_rel
    return report


def _load_wordnet_shim(rel_types, max_rows_per_rel):
    """Monkeypatch target for _v2.load_worldtree_triples. Signature-compatible (2 positional args).
    Builds the dense corpus from _CFG and stashes the density report + eligible dense heads for the
    split + metrics merge. Returns (triples, rel_names)."""
    heldout = _CFG["heldout_rels"]
    triples, rel_names, dense_heads, report = build_wordnet_dense_corpus(
        heldout, _CFG["min_nonr_deg"], _CFG.get("max_dense_heads"), _CFG.get("seed_for_corpus", 0),
        max_concepts=_CFG.get("max_concepts", 2500), per_feat_cap=_CFG.get("per_feat_cap", 20))
    _CFG["_dense_heads_by_rel"] = {R: set(dense_heads[R]) for R in dense_heads}
    _CFG["_density_report"] = report
    if len(triples) < 20:
        raise ValueError("INSUFFICIENT_DATA: WordNet corpus produced only %d triples" % len(triples))
    _progress("WordNet dense corpus: n_triples=%d n_rel=%d %s"
              % (len(triples), len(rel_names),
                 " ".join("%s[dense_heads=%d usable_twin=%.3f nonR_med=%.1f]"
                          % (R, report["per_heldout_relation"][R]["n_dense_heads"],
                             report["per_heldout_relation"][R]["usable_cohypo_twin_frac"],
                             report["per_heldout_relation"][R]["nonr_deg_median"])
                          for R in heldout)))
    return triples, rel_names


# ===========================================================================
# THE ONE CHANGE (2/2): density-gated held-out-head selection.
# v1's build_analogy_split logic VERBATIM + a single added gold-INDEPENDENT restriction: candidate
# held-out heads must be in the dense-eligible set (non-R partner degree >= min_nonr_deg). Leak-proof
# exclusion-from-ALL-storage (stored_fac never contains a held-out head's R-edge) is byte-identical.
# ===========================================================================

def _build_analogy_split_dense(triples, seed, heldout_rels, n_heldout_per_rel):
    rng = np.random.RandomState(seed)
    concepts = sorted(set([t[1] for t in triples] + [t[2] for t in triples]))
    cidx = {c: i for i, c in enumerate(concepts)}
    rel_names = sorted(set(t[0] for t in triples))
    ridx = {r: i for i, r in enumerate(rel_names)}
    fac = [(ridx[r], cidx[a], cidx[b]) for (r, a, b) in triples]

    rels_of_concept = defaultdict(set)
    for (r, a, b) in fac:
        rels_of_concept[a].add(r)
        rels_of_concept[b].add(r)

    heads_of_rel = defaultdict(lambda: defaultdict(set))
    for (r, a, b) in fac:
        heads_of_rel[r][a].add(b)

    dense_by_rel = _CFG.get("_dense_heads_by_rel", {})  # rel_name -> set(concept_name)

    heldout = {}
    heldout_pairs = set()
    for rname in heldout_rels:
        if rname not in ridx:
            continue
        R = ridx[rname]
        eligible = dense_by_rel.get(rname)  # gold-INDEPENDENT density gate (None => no gate)
        cand = [a for a in heads_of_rel[R]
                if len(rels_of_concept[a] - {R}) >= 1
                and (eligible is None or concepts[a] in eligible)]
        cand = sorted(cand)
        rng.shuffle(cand)
        pick = cand[:n_heldout_per_rel]
        heldout[R] = {a: set(heads_of_rel[R][a]) for a in pick}
        for a in pick:
            heldout_pairs.add((R, a))

    stored_fac = [f for f in fac if (f[0], f[1]) not in heldout_pairs]
    return {
        "concepts": concepts, "cidx": cidx, "rel_names": rel_names, "ridx": ridx,
        "fac": fac, "stored_fac": stored_fac,
        "heldout": heldout, "heldout_pairs": heldout_pairs,
        "n_dict": len(concepts),
    }


# ---------------------------------------------------------------------------
# Config presets
# ---------------------------------------------------------------------------

def cfg_full():
    # PRIMARY decisive bar = HYPERNYM (low-fanout, twin-rich). Brain-realistic density: non-R deg>=8
    # (MEASURED usable-twin ceiling 0.218 over 867 heads). Full-N=1024, 3 seeds.
    return {"run_mode": "full", "N": 1024, "seeds": [7, 13, 19],
            "rel_types": ["WORDNET_ALL"], "max_rows_per_rel": 100000,
            "heldout_rels": ["HYPERNYM"], "n_heldout_per_rel": 120, "flat_steps": 500,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5,
            "cap_rels": 4, "struct_role_weight": 0.25, "gamma": 1.0,
            "min_nonr_deg": 8, "max_dense_heads": 900, "max_concepts": 2500, "per_feat_cap": 20}


def cfg_full_meronym():
    # LESS-TAUTOLOGICAL cross-check (coordinator concern 2): hold out PART_MERONYM instead of HYPERNYM.
    # Co-parts are NOT definitionally shared by co-hyponyms (unlike hypernyms), so a win here is genuine
    # relational inference, not taxonomic self-fulfillment. Alignment may use hypernymy structure (similar
    # things have similar parts = real Gentner analogy). Smaller dense pool -> min_nonr_deg=5.
    return {"run_mode": "full", "N": 1024, "seeds": [7, 13, 19],
            "rel_types": ["WORDNET_ALL"], "max_rows_per_rel": 100000,
            "heldout_rels": ["PART_MERONYM"], "n_heldout_per_rel": 100, "flat_steps": 500,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5,
            "cap_rels": 4, "struct_role_weight": 0.25, "gamma": 1.0,
            "min_nonr_deg": 5, "max_dense_heads": 700, "max_concepts": 2500, "per_feat_cap": 20}


def cfg_smoke():
    # HYPERNYM held out, full-N (discriminator survives scale). Lower density gate (>=5) + capped heads
    # for speed; verify STORE_RECALL_FLOOR collapses, dense heads genuinely rich, twin diagnostic fires.
    return {"run_mode": "smoke", "N": 1024, "seeds": [7],
            "rel_types": ["WORDNET_ALL"], "max_rows_per_rel": 100000,
            "heldout_rels": ["HYPERNYM"], "n_heldout_per_rel": 50, "flat_steps": 150,
            "topk": 10, "topk_align": 50, "use_idf": True, "role_weight": 0.5,
            "cap_rels": 4, "struct_role_weight": 0.25, "gamma": 1.0,
            "min_nonr_deg": 5, "max_dense_heads": 350}


# ---------------------------------------------------------------------------
# Self-test: (1) planted twins via the v2 mechanism + ORIGINAL split (mechanism NOT broken);
#            (2) WordNet loader + dense split smoke: dense heads genuinely have >= min relations,
#                STORE_RECALL_FLOOR collapses on a real WordNet split, twin diagnostic computes.
# ---------------------------------------------------------------------------

def self_test():
    _progress("SELF-TEST start")
    # (1) planted-twins: reuse v2's own planted graph via the ORIGINAL (v1) split -> ANALOGY_v2 solves
    #     twins >> FREQUENCY_PRIOR/RANDOM; floor + shuffled collapse. Proves the mechanism fires.
    rng = np.random.RandomState(7)
    K, per_cluster, n_attr_rel = 8, 12, 4
    triples = []
    categories = ["CAT_%02d" % k for k in range(K)]
    attr_pool = ["attr_%02d_%02d" % (k, j) for k in range(K) for j in range(3)]
    for k in range(K):
        shared_attrs = ["attr_%02d_%02d" % (k, j) for j in range(3)]
        for c in range(per_cluster):
            h = "c_%02d_%02d" % (k, c)
            triples.append(("CATEGORY", h, categories[k]))
            for ai, at in enumerate(shared_attrs):
                triples.append(("ATTR_%d" % (ai % n_attr_rel), h, at))
            triples.append(("ATTR_%d" % (rng.randint(0, n_attr_rel)),
                            h, attr_pool[rng.randint(0, len(attr_pool))]))
    S = _ORIG_SPLIT(triples, 7, ["CATEGORY"], K * 4)
    Rc = S["ridx"]["CATEGORY"]
    for (r, a_, b_) in S["stored_fac"]:
        assert not (r == Rc and (Rc, a_) in S["heldout_pairs"]), "EXCLUSION LEAK in stored_fac"
    an_out, _, _, _, diag = eval_analogy_family(
        S, topk=10, topk_align=20, use_idf=True, seed=7, cap_rels=4, struct_role_weight=0.25,
        gamma=1.0, role_weight=0.5)
    gen = torch.Generator().manual_seed(7)
    floor, _ = eval_store_recall_floor(S, 128, gen, topk=10)
    an1 = an_out["ANALOGY_v2"]["top1"]
    fp1 = an_out["FREQUENCY_PRIOR"]["top1"]
    rd1 = an_out["RANDOM_ALIGNMENT"]["top1"]
    sh1 = an_out["SHUFFLED_PROFILE"]["top1"]
    base_rate = 1.0 / S["n_dict"]
    _progress("planted: ANALOGY_v2=%.3f FREQ=%.3f RANDOM=%.3f SHUFFLED=%.3f FLOOR=%.3f"
              % (an1, fp1, rd1, sh1, floor["top1"]))
    assert an1 >= 0.80, "INSTRUMENT VACUOUS: ANALOGY_v2 did not solve planted twins (%.3f)" % an1
    assert an1 > fp1 + 0.20, "ANALOGY_v2 did not beat FREQUENCY_PRIOR (%.3f vs %.3f)" % (an1, fp1)
    assert an1 > rd1 + 0.20, "ANALOGY_v2 did not beat RANDOM (%.3f vs %.3f)" % (an1, rd1)
    assert sh1 < an1 - 0.20, "SHUFFLED did not collapse (%.3f vs %.3f)" % (sh1, an1)
    assert floor["top1"] <= max(20.0 * base_rate, 0.02), (
        "STORE_RECALL_FLOOR did not collapse (%.3f) -> exclusion leak" % floor["top1"])
    _progress("(1) mechanism fires on planted twins + leak-proof floor collapses: PASS")

    # (2) WordNet loader + dense split: real-code-path exercise at tiny density gate.
    global _CFG
    _CFG = {"heldout_rels": ["HYPERNYM"], "min_nonr_deg": 6, "max_dense_heads": 60, "seed_for_corpus": 0}
    tri, rel_names = _load_wordnet_shim(["WORDNET_ALL"], 100000)
    assert len(tri) >= 100, "WordNet loader produced too few triples (%d)" % len(tri)
    assert "HYPERNYM" in rel_names, "HYPERNYM relation missing from WordNet corpus"
    rep = _CFG["_density_report"]["per_heldout_relation"]["HYPERNYM"]
    assert rep["n_dense_heads"] >= 10, "too few dense heads (%d)" % rep["n_dense_heads"]
    assert rep["nonr_deg_median"] >= 6.0 - 1e-9, (
        "density gate not honored: nonR_deg_median=%.2f < gate 6" % rep["nonr_deg_median"])
    # leak-proof check on the WordNet dense split: no inverse-relation duplicate (one direction only).
    assert "HYPONYM" not in rel_names and "PART_HOLONYM" not in rel_names, (
        "INVERSE RELATION PRESENT -> would leak held-out answer")
    Sw = _build_analogy_split_dense(tri, 7, ["HYPERNYM"], 30)
    Rh = Sw["ridx"]["HYPERNYM"]
    for (r, a_, b_) in Sw["stored_fac"]:
        assert not (r == Rh and (Rh, a_) in Sw["heldout_pairs"]), "EXCLUSION LEAK in WordNet stored_fac"
    # every selected head must be in the dense-eligible set (density gate honored by the split).
    dense_set = _CFG["_dense_heads_by_rel"]["HYPERNYM"]
    for (R, a_idx) in Sw["heldout_pairs"]:
        assert Sw["concepts"][a_idx] in dense_set, "split selected a NON-dense head -> gate not honored"
    # floor at production N=1024 (tiny-N crosstalk + hub-tail frequency recovery otherwise inflates
    # it). Collapse band here is a sanity gate distinguishing "near base-rate" from a working recall
    # mechanism (which would score >0.2); the STRICT gating floor runs inside run_experiment.
    genw = torch.Generator().manual_seed(7)
    floorw, _ = eval_store_recall_floor(Sw, 1024, genw, topk=10)
    assert floorw["top1"] <= 0.10, (
        "WordNet STORE_RECALL_FLOOR did not collapse (%.3f) -> exclusion leak" % floorw["top1"])
    _progress("(2) WordNet dense corpus real-code-path: n_dict=%d dense_heads=%d nonR_med=%.1f "
              "usable_twin=%.3f floor=%.4f collapse: PASS"
              % (Sw["n_dict"], rep["n_dense_heads"], rep["nonr_deg_median"],
                 rep["usable_cohypo_twin_frac"], floorw["top1"]))
    _CFG = {}
    _progress("SELF-TEST PASS")
    return {"verdict": "SELFTEST_PASS", "planted_analogy_v2": an1, "planted_freq_prior": fp1,
            "planted_floor": floor["top1"],
            "wordnet_n_dict": Sw["n_dict"], "wordnet_dense_heads": rep["n_dense_heads"],
            "wordnet_nonr_deg_median": rep["nonr_deg_median"],
            "wordnet_usable_twin_frac": rep["usable_cohypo_twin_frac"],
            "wordnet_floor_top1": floorw["top1"]}


# ---------------------------------------------------------------------------
# Infra
# ---------------------------------------------------------------------------

_HEARTBEAT_DIR = None


def _progress_hb(msg):
    """Monkeypatch target for _v2._progress: print + append a heartbeat line (monitorable). The v2
    seed/arm loop calls _progress at each seed, floor, flat, and analogy-family step, so this gives a
    per-chunk heartbeat without touching the verbatim run_experiment loop."""
    print("[%s] %s" % (ANCHOR_NAME, msg), flush=True)
    if _HEARTBEAT_DIR is None:
        return
    try:
        os.makedirs(_HEARTBEAT_DIR, exist_ok=True)
        row = {"ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(), "msg": msg}
        with open(os.path.join(_HEARTBEAT_DIR, "_heartbeat.jsonl"), "a", encoding="utf-8") as f:
            f.write(json.dumps(row) + "\n")
    except Exception:
        pass  # heartbeat is best-effort telemetry; never fail the run over it


def _write_start_marker(output_dir, run_mode, expected_n_units):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode,
              "expected_n_units": expected_n_units, "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    final = os.path.join(output_dir, "_start_marker.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, final)


def _write_metrics(output_dir, metrics):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=2)
    os.replace(tmp, final)  # atomic per META_RULE_AH


def _write_crash_metrics(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": "%s: %s" % (type(exc).__name__, str(exc)[:500]),
            "summary": "CELL_CRASHED: %s" % type(exc).__name__, "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "pid": os.getpid(),
            "anchor_name": ANCHOR_NAME, "failure_class": type(exc).__name__}
    _write_metrics(output_dir, diag)


def main():
    global _CFG
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--meronym-full", action="store_true")
    ap.add_argument("--output-dir", default=None)
    args = ap.parse_args()

    if args.self_test:
        out = self_test()
        print(json.dumps(out))
        return

    if args.meronym_full:
        cfg = cfg_full_meronym()
        suffix = "_meronym"
    elif args.smoke:
        cfg = cfg_smoke()
        suffix = "_smoke"
    else:
        cfg = cfg_full()
        suffix = ""
    output_dir = args.output_dir or os.path.join(REPO, "data", ANCHOR_NAME + suffix)

    # stash corpus config for the monkeypatched loader/split, then patch the two corpus entry points.
    _CFG = {"heldout_rels": cfg["heldout_rels"], "min_nonr_deg": cfg["min_nonr_deg"],
            "max_dense_heads": cfg.get("max_dense_heads"), "seed_for_corpus": cfg["seeds"][0],
            "max_concepts": cfg.get("max_concepts", 2500), "per_feat_cap": cfg.get("per_feat_cap", 20)}
    _v2.load_worldtree_triples = _load_wordnet_shim
    _v2.build_analogy_split = _build_analogy_split_dense
    global _HEARTBEAT_DIR
    _HEARTBEAT_DIR = output_dir
    _v2._progress = _progress_hb  # per-chunk heartbeat (monitorable) without touching run_experiment

    expected_units = len(cfg["seeds"]) * (2 + len(_v2.ANALOGY_ARMS))
    _write_start_marker(output_dir, cfg["run_mode"], expected_units)
    try:
        metrics = run_experiment(cfg, output_dir)
    finally:
        # restore (defensive; process is short-lived but keep module clean).
        _v2.load_worldtree_triples = _ORIG_LOAD
        _v2.build_analogy_split = _ORIG_SPLIT

    # merge the density + twin diagnostic (the REAL density metric) into metrics.
    metrics["corpus"] = "wordnet_dense_v1"
    metrics["density_report"] = _CFG.get("_density_report")
    metrics["min_nonr_deg"] = cfg["min_nonr_deg"]
    metrics["primary_heldout_relation"] = cfg["heldout_rels"]
    _write_metrics(output_dir, metrics)
    _progress("VERDICT %s | %s" % (metrics["verdict"], metrics["verdict_msg"]))
    dr = (metrics.get("density_report") or {}).get("per_heldout_relation", {})
    for R, d in dr.items():
        _progress("DENSITY[%s] dense_heads=%d nonR_deg(med=%.1f mean=%.1f) has_twin=%.3f "
                  "USABLE_twin=%.3f tail_fanout_med=%.1f"
                  % (R, d["n_dense_heads"], d["nonr_deg_median"], d["nonr_deg_mean"],
                     d["has_twin_frac"], d["usable_cohypo_twin_frac"], d["tail_fanout_median"]))


if __name__ == "__main__":
    _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME)
    try:
        if "--smoke" in sys.argv:
            _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME + "_smoke")
        elif "--meronym-full" in sys.argv:
            _out_dir_for_crash = os.path.join(REPO, "data", ANCHOR_NAME + "_meronym")
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        if "--self-test" not in sys.argv:
            _write_crash_metrics(_out_dir_for_crash, e)
        raise
