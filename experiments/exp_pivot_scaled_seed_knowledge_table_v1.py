"""SCALED FOUNDATION TEST ("the choose leg"): does a PROPERLY-SCALED LLM-built + KB-VETTED selectional
table -- covering the reader's WHOLE working vocabulary, not the ~120-pair probe-scoped tiny table -- move
the selectional 2AFC reading decision at COVERAGE, beyond both the thin corpus-frequency mechanism AND the
prior tiny pivot table? And does a mechanical VerbNet+WordNet AUDITOR over the LLM-authored table catch
INJECTED contradiction-errors (the honesty mechanism for dense knowledge the ontology alone cannot supply)?

BACKGROUND (the two prior pivot cells this scales up from):
  29471 exp_pivot_selectional_knowledge_richness_2afc_v1 (MEASURED@data/exp_pivot_selectional_knowledge_
    richness_2afc_v1/metrics.json): a TINY, probe-scoped LLM-built table (117 pairs, hand-built ONLY for a
    59-item 2AFC probe) landed HARD_PASS_KNOWLEDGE_POVERTY_WAS_THE_WALL: acc_thin=0.475 -> acc_rich=0.814
    (+0.339), scramble collapses to 0.466 (chance), monotone coverage climb. But the table's SCOPE was never
    tested: does covering the reader's actual WORKING VOCABULARY (not a curated 59-item probe) sustain that
    lift, or was the tiny table's win an artifact of being hand-scoped exactly to its own eval set (rich_
    cov_on_items was 1.000 BY CONSTRUCTION)?
  29475 exp_pivot_selectional_independent_kb_2afc_v1 (MEASURED@data/exp_pivot_selectional_independent_kb_
    2afc_v1/metrics.json): a pure VerbNet+WordNet ontology (ZERO LLM, ZERO corpus attestation) recovers only
    acc_indep_kb=0.568 (gap=+0.093 vs thin, MIDDLE_BAND, frac_of_llm_lift_recovered=0.275 -- ~27%). Ontology
    alone is too sparse (selrestrs empty for most verbs); the LLM must supply DENSITY. But density-at-SCALE
    was never built or tested -- this cell builds it.

THIS CELL builds a NEW, SCALED table (LLM-authored at build time = this agent's own general-knowledge
  ratings, same discipline as 29471) covering the reader's actual working vocabulary: the (verb_lemma, noun)
  pairs structurally mined from the reader corpus (SCV.MINING_FILES_FULL = primer/first/second/fourth-reader
  -- the SAME corpus the THIN gfit mechanism is fit on, and structurally DISJOINT from the Third-Reader gold
  the 59-item probe/independent-gold test lives in). Frequency-selected: top TOP_K_VERBS verb lemmas (by
  real-corpus instance count) x up to MAX_NOUNS_PER_VERB most-frequent attested content-noun patients each,
  UNION the 29471 tiny table's own 117 pairs (so SCALED is a strict vocabulary SUPERSET of TINY, never a
  regression). KB-VETTED: every SCALED entry is checked against an AUDITOR built from VerbNet selectional
  restrictions + WordNet fine-sense similarity (reusing 29475's score_indep_kb_components VERBATIM) --
  entries where the LLM rating strongly CONTRADICTS the ontology's own checkable signal are FLAGGED (not
  deleted; per the task's explicit honesty-mechanism design, absence of ontology signal is NOT grounds to
  flag -- the ontology is known-sparse per 29475, so only CONTRADICTION when a checkable signal exists).

CONCEPT-ID KEYED SCHEMA (vision-ready, locked per task spec): every table entry carries BOTH the lemma-pair
  string key (verb_lemma|noun_lemma, for O(1) runtime dict lookup) AND a stable verb_concept_id / noun_
  concept_id (primary WordNet synset name, or "verbnet:<classid>" fallback for OOV-WordNet verbs) -- a
  future perceptual front-end binds features onto the concept_id, not the raw string.

TWO TEST SLICES (one variable = the knowledge table; task/scorer/mechanism IDENTICAL across arms, reusing
  29471's _2afc scorer VERBATIM):
  (1) ORIGINAL_ITEMS (continuity/sanity, n=59, IMPORTED from 29471 byte-for-byte): the same independent-gold
      Third-Reader 2AFC probe 29471/29475 used. SCALED is a superset of TINY's vocabulary so this slice is
      NOT the primary discriminator (SCALED should reproduce ~= TINY here by construction) -- reported for
      continuity + as a regression check (SCALED must not be WORSE than TINY on pairs TINY already covers).
  (2) COVERAGE_SLICE (the PRIMARY discriminator, n~=N_COVSLICE_TARGET, NEW, built in this cell): items whose
      (verb, gold_patient) pair is drawn from real ATTESTED co-occurrence in the mining corpus (structural
      pseudo-gold: "this verb+noun pair really occurred together in real reader text" -- NOT independently
      human-annotated argument structure like the Third-Reader gold; explicitly a weaker, HONEST substitute
      whose limitation is stated, not hidden) with a same-class-preferred distractor negative (same
      methodology as 29471's sample_negatives). This slice is STRUCTURALLY disjoint in SOURCE TEXT from the
      Third-Reader probe (mining files explicitly EXCLUDE mcguffey_third_reader.clean.txt -- see SCV module
      docstring EXCLUDED_FROM_MINING) -- the held-out-slice guardrail is satisfied by corpus-disjointness,
      NOT by withholding vocabulary from the table (withholding vocabulary would make TINY's structural
      coverage gap untestable -- the whole point is that TINY was scoped to a DIFFERENT, narrower probe and
      SCALED was scoped to the CORPUS; both facts are stated openly, not obscured). The leakage guard that
      DOES apply: every table entry was rated from a blind list of (verb,noun) pairs with NO visibility into
      which pair would end up "gold-attested" vs "sampled-negative" in ANY item (ratings assigned BEFORE
      item construction, exactly 29471's discipline) -- so the accuracy lift is not tunable-by-construction
      even though the vocabulary IS scoped to this corpus.

ARMS (both slices): ARM_THIN (P.build_thin_gfit, reused verbatim -- reproduces the reader's real thin
  mechanism); ARM_TINY (29471's rich_selectional_table.json, loaded read-only, OOV->0.5); ARM_SCALED (this
  cell's new scaled_seed_table_v1.json, OOV->0.5); ARM_RANDOM (P.make_random_score, reused -- can-fail
  control); ARM_SCALED_SCRAMBLED (SCALED values permuted across its own keys -- must-fail anti-cheat).

KB-VET AUDITOR + INJECTED-ERROR TEST (the honesty mechanism for LLM-supplied density the ontology alone
  cannot verify): for every SCALED entry where 29475's score_indep_kb_components(v,n) returns a CHECKABLE
  ontology signal (example_score from VerbNet-exemplar WordNet-similarity, or selrestr_score from VerbNet
  typed restrictions -- NOT the 0.5 OOV backoff, which means "ontology has nothing to say", NOT a
  contradiction), flag CONTRADICTION iff |llm_rating - ontology_signal| >= CONTRA_THRESH. This is flag-on-
  disagreement, never delete-on-absence (ontology is known-sparse per 29475; most verbs have NO selrestr).
  INJECTED-ERROR CAN-FAIL TEST: sample N_INJECT currently-non-flagged checkable entries (fixed seed),
  corrupt each to a value that CONTRADICTS its own ontology signal (a synthetic "wrong LLM entry"), rerun
  the auditor, and measure catch_rate (fraction of injected corruptions flagged) against false_flag_rate
  (flag rate on the UNMODIFIED checkable entries -- the auditor's own baseline noise level). A vacuous
  auditor (catch_rate ~= false_flag_rate) must HARD_FAIL per the task's own spec.

PRE-REGISTERED VERDICT BANDS (set BEFORE running the FULL; do NOT redefine mid-run; COVERAGE_SLICE is the
  primary discriminator, ORIGINAL_ITEMS is continuity-only):
  HARD_PASS_SCALED_KNOWLEDGE_HELPS_AT_COVERAGE: ALL of --
    coverage_scaled_cov >= 0.55  AND  coverage_tiny_cov <= 0.15  AND
    (acc_scaled_cov - acc_thin_cov) >= 0.12  AND  (acc_scaled_cov - acc_tiny_cov) >= 0.12  AND
    acc_scaled_cov >= 0.65  AND  0.40 <= acc_random_cov <= 0.60  AND
    (acc_scaled_cov - acc_scaled_cov_scrambled) >= 0.10  AND
    auditor_catch_rate_injected >= 0.75  AND  auditor_false_flag_rate_clean <= 0.25
    -> covering the reader's whole working vocabulary (not just a curated probe) DOES move the reading
       decision; coverage was a real limit and LLM+KB-vetted scaling is the lever; the auditor is a live
       honesty mechanism.
  HARD_FAIL_SCALING_DIDNT_HELP_OR_AUDITOR_VACUOUS: ANY of --
    (acc_scaled_cov - acc_tiny_cov) <= 0.05  (scaled does not clearly beat the tiny table at broader
       coverage -- coverage was NOT the limit; granularity/mechanism is, exactly as 29475 hinted) OR
    (acc_scaled_cov - acc_thin_cov) <= 0.03  (scaled does not even beat the thin corpus-frequency mechanism
       at the vocabulary it was built for -- the authored content itself is not helping) OR
    auditor_catch_rate_injected < 0.34  (auditor is vacuous; catches less than a third of injected wrong
       entries -- the honesty mechanism does not work) OR
    (acc_scaled_cov - acc_scaled_cov_scrambled) <= 0.03  (anti-cheat: scrambling does not collapse the lift
       -- an artifact of the value SET, not the assignment) OR
    NOT (0.40 <= acc_random_cov <= 0.60)  OR  coverage_tiny_cov > 0.20  (harness not sane: either the task is
       not can-fail, or TINY already covers this "broader" slice adequately -- the coverage-gap premise
       itself is false).
  MIDDLE_BAND: otherwise.

FAIRNESS / NO ANSWER-LEAKAGE: ratings for ALL SCALED table pairs are authored from a shuffled, UNLABELED
  (verb,noun) pair list (dump via --dump-scope), BEFORE either item set (ORIGINAL_ITEMS or COVERAGE_SLICE)
  assigns any pair a gold/distractor role -- this agent never sees which noun is "the attested/gold" vs "the
  sampled negative" for any pair while rating. SAME 2AFC mechanism/scorer (P._2afc, imported not
  reimplemented) across ALL arms and BOTH slices. ONLY the score table differs per arm.

COMPUTE ARCHITECTURE: class (b) sequential-CPU with justification -- corpus mining reuses SCV's cached
  reader pass (~5-6min once, cached thereafter) + pure dict lookups + O(items) 2AFC comparisons + nltk
  VerbNet/WordNet calls at build time for the auditor; NO matmul, NO GPU-batchable primitive. Storage:
  no_storage (JSON table artifacts only). Runtime invariant: glass-box dict lookup ONLY at scoring time; NO
  LLM/network/autograd at inference (build-time LLM authoring only, exactly 29471's invariant).
  progress_logging: print_flush. Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds, numpy default_rng,
  sorted(set); NO hash()-seeded RNG. LOCAL-ONLY, foreground-to-completion; NO queue, NO push, NO
  remote-persist, NO git add -A.

CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
  - arms_differ_verified at smoke gate (hash test over 5 per-item score vectors x 2 item sets)
  - final_metrics_atomicity: tmp_replace
  - except SystemExit: raise BEFORE except Exception (no BaseException)
  - crlb_n/a: 2AFC discrimination-accuracy measurement; no quantitative noise floor for the discriminator
  - baseline_in_band at smoke (ARM_THIN in (0.05,0.95) on both slices; ARM_RANDOM ~0.5 = can-fail)
  - discriminator survives scale: COVERAGE_SLICE at full corpus IS the scale; smoke uses smaller mining
    files (SCV.MINING_FILES_SMOKE) + smaller TOP_K_VERBS, same mechanism/algorithm
  - HARD_PASS strictly above floor (gap>=0.12 well above +0.05 FAIL edge; scramble margin>=0.10;
    auditor catch>=0.75 well above the <0.34 FAIL edge)
  - all numbers in comments tagged MEASURED@/HYPOTHESIZED@/THEORETICAL@/CITED@
  - deterministic_seeding: fixed int seeds + numpy default_rng + sorted(set); no hash()/list(set())
  - cardinality_ok: coverage curve (backoff-to-thin) has EXPECTED_COV_POINTS=5, on both slices
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import sys
import time
import traceback
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "pivot_scaled_seed_knowledge_table_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

# Reuse 29471 (item construction, thin gfit, 2AFC scorer, random/scramble generators, tiny table loader)
# and 29475 (VerbNet+WordNet ontology scorer, the auditor's core signal) VERBATIM -- one-variable discipline.
from experiments import exp_pivot_selectional_knowledge_richness_2afc_v1 as P  # noqa: E402
from experiments import exp_pivot_selectional_independent_kb_2afc_v1 as K  # noqa: E402
from experiments import exp_scene_coherence_verifier_contrastive_scv_v1 as SCV  # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L  # noqa: E402

from experiments._validity_preflight import run_validity_preflight  # noqa: E402

from nltk.corpus import wordnet as wn  # noqa: E402

NEG_SEED = P.NEG_SEED  # 20260723 -- shared fixed base seed, no hash()-derived anything
COV_POINTS = P.COV_POINTS
EXPECTED_COV_POINTS = P.EXPECTED_COV_POINTS

# ---- Vocabulary-mining corpus (NOTE: narrower than P.build_thin_gfit's SCV.MINING_FILES_FULL). The
# primer + first_reader files open with LETTER/WORD-DRILL content ("dog the ran" / "a o n d g r th" --
# phonics primers, not narrative prose), which corrupts SVO extraction with nonsense pairs (verified by
# inspection: 'err|azure', 'catch|catch', 'know|know' -- self-referential/garbage mis-parses). ARM_THIN
# (P.build_thin_gfit) is REUSED VERBATIM and keeps its own established SCV.MINING_FILES_FULL scope
# (that mechanism's accuracy is already measured/accepted from 29471/29475) -- ONLY this cell's OWN
# scope-selection + coverage-slice construction restricts to the two CLEAN narrative-prose files, for
# authoring-quality reasons (rating garbage pairs "accurately low" wastes authoring effort and produces a
# meaningless coverage-slice pseudo-gold; see 'become|breadth', 'call|danco|fred' etc. in the excluded
# files' output during design).
VOCAB_MINING_FILES_FULL = [
    "data/corpora/graded_readers_graded/cleaned/mcguffey_second_reader.clean.txt",
    "data/corpora/graded_readers_graded/cleaned/mcguffey_fourth_reader.clean.txt",
]
VOCAB_MINING_FILES_SMOKE = [
    "data/corpora/graded_readers_graded/cleaned/mcguffey_second_reader.clean.txt",
]

# ---- Scope-selection algorithm parameters (deterministic; pre-registered) --------------------------
TOP_K_VERBS_FULL = 110
TOP_K_VERBS_SMOKE = 24
MAX_NOUNS_PER_VERB_FULL = 3
MAX_NOUNS_PER_VERB_SMOKE = 3
MIN_PAIR_FREQ = 1

# ---- Coverage-slice construction parameters --------------------------------------------------------
N_COVSLICE_VERBS_FULL = 110
N_COVSLICE_VERBS_SMOKE = 16
# Verbs whose gold-schema role is NOT a direct-object patient (per gold_mcguffey_lccp_argstruct_v1's own
# "nopat" definition: intransitive-motion / cognition-clausal / oblique-perception / report / aspectual /
# copular) -- EXCLUDED only from being the POSITIVE-attestation verb in the coverage-slice pseudo-gold
# (their surface SVO extraction is often a clausal-complement mis-parse, not a true patient). They are NOT
# excluded from the SCALED table's own vocabulary scope (the table is corpus-general, not gold-schema-gated).
EXCLUDE_NOPAT_VERBS_FOR_COVSLICE_GOLD = {
    "say", "said", "cry", "ask", "answer", "retort", "tell", "call", "exclaim", "speak",
    "think", "know", "wonder", "mean", "wish", "hope", "believe", "suppose", "prefer", "intend", "learn",
    "come", "go", "sit", "stand", "fall", "run", "walk", "spring", "leap", "creep", "swim",
    "begin", "commence", "try", "continue", "seem", "look", "want",
}

# ---- Auditor parameters (pre-registered) -----------------------------------------------------------
CONTRA_THRESH = 0.45          # |llm_rating - ontology_signal| >= this => flag as CONTRADICTION
N_INJECT = 24                 # size of the injected-error can-fail battery
INJECT_SEED = NEG_SEED + 101  # fixed, distinct from all other seeds in this arc

SCALED_TABLE_PATH = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}", "scaled_seed_table_v1.json")


# ======================================================================================================
# 1. Corpus mining + frequency-based scope selection (deterministic; the "reader's working vocabulary").
# ======================================================================================================
def _is_real_verb(lemma):
    """Filters OCR-noise tokens from the structural miner (e.g. 'err') -- must be a real WordNet verb."""
    if not lemma.isalpha() or len(lemma) < 2:
        return False
    try:
        return bool(wn.synsets(lemma, pos="v"))
    except Exception:
        return False


def mine_pairs(mode, out_dir):
    """Mine (verb_lemma, content_noun_patient) frequency from the reader corpus (SAME corpus + cache
    convention as P.build_thin_gfit -- SCV.MINING_FILES_FULL/SMOKE, structurally EXCLUDES the Third-Reader
    gold source per SCV.EXCLUDED_FROM_MINING). Returns (pair_freq: Counter[(v,n)], verb_freq: Counter[v],
    per_verb_noun_freq: dict[v -> Counter[n]], n_mine: int)."""
    files = VOCAB_MINING_FILES_SMOKE if mode == "smoke" else VOCAB_MINING_FILES_FULL
    cache = os.path.join(out_dir, "_mining_cache.json")
    mine_data = SCV.run_reader_on_files(files, cache, max_sents=(500 if mode == "smoke" else None))
    pair_freq = Counter()
    verb_freq = Counter()
    per_verb_noun_freq = defaultdict(Counter)
    for sid, rec in mine_data.items():
        for tup in rec.get("svo", []):
            v_surf, _a, p = tup
            vl = L.lemma_verb(v_surf).lower()
            pl = p.lower()
            if not _is_real_verb(vl):
                continue
            if not P._is_content_noun(pl):
                continue
            pair_freq[(vl, pl)] += 1
            verb_freq[vl] += 1
            per_verb_noun_freq[vl][pl] += 1
    return pair_freq, verb_freq, per_verb_noun_freq, len(mine_data)


def select_scope_pairs(verb_freq, per_verb_noun_freq, top_k_verbs, max_nouns_per_verb, min_pair_freq):
    """Deterministic frequency-selected vocabulary scope: top verb lemmas x top attested nouns each.
    UNION with the 29471 tiny table's own pairs (SCALED is a strict vocabulary superset of TINY)."""
    top_verbs = sorted(verb_freq.keys(), key=lambda v: (-verb_freq[v], v))[:top_k_verbs]
    scope = set()
    for v in top_verbs:
        nouns = [n for n, c in per_verb_noun_freq[v].items() if c >= min_pair_freq]
        nouns = sorted(nouns, key=lambda n: (-per_verb_noun_freq[v][n], n))[:max_nouns_per_verb]
        for n in nouns:
            scope.add((v, n))
    tiny_tab = P.load_rich_table()
    if tiny_tab:
        scope |= set(tiny_tab.keys())
    return sorted(scope), sorted(top_verbs)


def dump_scope_pairs(mode):
    """Build the scope + write the SHUFFLED UNLABELED pair list for build-time rating (leakage guard:
    rated BEFORE any item/gold-vs-distractor role is assigned)."""
    out_dir = _out_dir(mode)
    os.makedirs(out_dir, exist_ok=True)
    pair_freq, verb_freq, per_verb_noun_freq, n_mine = mine_pairs(mode, out_dir)
    top_k = TOP_K_VERBS_SMOKE if mode == "smoke" else TOP_K_VERBS_FULL
    max_n = MAX_NOUNS_PER_VERB_SMOKE if mode == "smoke" else MAX_NOUNS_PER_VERB_FULL
    scope, top_verbs = select_scope_pairs(verb_freq, per_verb_noun_freq, top_k, max_n, MIN_PAIR_FREQ)
    rng = np.random.default_rng(NEG_SEED + 31)
    order = rng.permutation(len(scope)).tolist()
    shuffled = [{"verb": scope[i][0], "noun": scope[i][1]} for i in order]
    with open(os.path.join(out_dir, "_scope_pairs_to_rate.json"), "w", encoding="utf-8") as f:
        json.dump({"n_pairs": len(shuffled), "pairs": shuffled, "n_mine": n_mine,
                   "n_top_verbs": len(top_verbs),
                   "instructions": ("Rate each pair: how plausible is NOUN as the direct object of VERB, "
                                    "0.0=implausible/impossible ... 1.0=highly typical. GENERAL world "
                                    "knowledge only. Do NOT infer gold-vs-distractor role (none assigned "
                                    "yet).")}, f, indent=2)
    print(f"[{ANCHOR_NAME}:{mode}] scope={len(scope)} pairs over {len(top_verbs)} top verbs "
          f"(n_mine={n_mine}) -> _scope_pairs_to_rate.json", flush=True)
    return scope, top_verbs, pair_freq, verb_freq, per_verb_noun_freq, n_mine


# ======================================================================================================
# 2. Coverage-slice construction (structural pseudo-gold: real corpus attestation, NOT human-annotated).
# ======================================================================================================
def build_coverage_slice_items(verb_freq, per_verb_noun_freq, n_covslice_verbs):
    """Deterministic pseudo-gold 2AFC items from real corpus attestation. gold_patient = the verb's single
    MOST-FREQUENT attested content-noun patient (real co-occurrence = the pseudo-gold signal); neg_filler =
    a same-class-preferred distractor sampled (fixed RNG) from OTHER eligible verbs' attested patients.
    HONEST LIMITATION (stated, not hidden): this is STRUCTURAL attestation, not independent human argument-
    structure annotation like the Third-Reader gold -- eligible verbs exclude the gold schema's own nopat
    classes (report/cognition/motion/aspectual) to avoid mis-parsed clausal-complement "patients"."""
    eligible = [v for v in sorted(verb_freq.keys(), key=lambda v: (-verb_freq[v], v))
                if v not in EXCLUDE_NOPAT_VERBS_FOR_COVSLICE_GOLD][:n_covslice_verbs]
    items = []
    attested = {}
    pool_by_ss = defaultdict(set)
    all_pool = set()
    for v in eligible:
        nouns = sorted(per_verb_noun_freq[v].items(), key=lambda kv: (-kv[1], kv[0]))
        if not nouns:
            continue
        gp = nouns[0][0]
        ss = SCV.supersense(gp)
        if ss is None:
            continue
        attested[v] = set(per_verb_noun_freq[v].keys())
        pool_by_ss[ss].add(gp)
        all_pool.add(gp)
        items.append({"v": v, "gold_patient": gp, "gold_ss": ss})
    rng = np.random.default_rng(NEG_SEED + 41)
    for it in items:
        v, gp, ss = it["v"], it["gold_patient"], it["gold_ss"]
        excl = set(attested.get(v, set())) | {gp}
        same = sorted(pool_by_ss.get(ss, set()) - excl)
        cross = sorted(all_pool - excl - set(pool_by_ss.get(ss, set())))
        if same:
            neg = same[int(rng.integers(len(same)))]
            it["neg_stratum"] = "same_class"
        elif cross:
            neg = cross[int(rng.integers(len(cross)))]
            it["neg_stratum"] = "cross_class"
        else:
            pool = sorted(all_pool - {gp})
            neg = pool[int(rng.integers(max(1, len(pool))))] if pool else gp
            it["neg_stratum"] = "fallback"
        it["neg_filler"] = neg
        it["neg_ss"] = SCV.supersense(neg)
    items = [it for it in items if it["gold_patient"] != it["neg_filler"]]
    return sorted(items, key=lambda d: (d["v"], d["gold_patient"]))


# ======================================================================================================
# 3. Table loading + generic scoring helpers.
# ======================================================================================================
def load_json_table(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8") as f:
        obj = json.load(f)
    tab = {}
    for k, val in obj.get("ratings", obj).items():
        if "|" in k:
            v, n = k.split("|", 1)
            tab[(v, n)] = float(val)
    return tab


def make_scrambled(table, seed):
    keys = sorted(table.keys())
    vals = [table[k] for k in keys]
    rng = np.random.default_rng(seed)
    perm = rng.permutation(len(vals)).tolist()
    scr = {keys[i]: vals[perm[i]] for i in range(len(keys))}

    def s(v, p):
        return scr.get((v, p), 0.5)
    return s


def table_coverage(items, table):
    need = set()
    for it in items:
        need.add((it["v"], it["gold_patient"]))
        need.add((it["v"], it["neg_filler"]))
    covered = sum(1 for k in need if k in table)
    return round(covered / max(1, len(need)), 4)


def thin_coverage_on_items(items, thin_score):
    n_oov = sum(1 for it in items
                if thin_score(it["v"], it["gold_patient"])[1] == "oov")
    return round(1.0 - n_oov / max(1, len(items)), 4)


# ======================================================================================================
# 4. KB-VET AUDITOR (reuses 29475's ontology scorer VERBATIM) + injected-error can-fail test.
# ======================================================================================================
def ontology_signal(v, n):
    """Reuses 29475's score_indep_kb_components VERBATIM. Returns (signal_or_None, kind)."""
    ex, sel, _noun_cid = K.score_indep_kb_components(v, n)
    if ex is not None:
        return ex, "example"
    if sel is not None:
        return sel, "selrestr"
    return None, "none"


def audit_table(table):
    """Per-entry ontology signal + contradiction flag. Returns (records list, flagged set of (v,n))."""
    records = []
    flagged = set()
    for (v, n), rating in sorted(table.items()):
        sig, kind = ontology_signal(v, n)
        is_contra = (sig is not None) and (abs(rating - sig) >= CONTRA_THRESH)
        if is_contra:
            flagged.add((v, n))
        records.append({"v": v, "n": n, "llm_rating": rating, "ontology_signal": sig,
                         "ontology_kind": kind, "flagged": is_contra})
    return records, flagged


def inject_errors(table, seed, n_inject):
    """Deterministically corrupt N_INJECT currently-benign checkable entries to CONTRADICT their own
    ontology signal (a synthetic 'wrong LLM entry'). Returns (injected_table, injected_keys set)."""
    records, flagged = audit_table(table)
    checkable_benign = [(r["v"], r["n"], r["ontology_signal"]) for r in records
                        if r["ontology_signal"] is not None and not r["flagged"]]
    checkable_benign = sorted(checkable_benign)
    rng = np.random.default_rng(seed)
    if not checkable_benign:
        return dict(table), set()
    idx = rng.permutation(len(checkable_benign))[:min(n_inject, len(checkable_benign))].tolist()
    injected_tab = dict(table)
    injected_keys = set()
    for i in idx:
        v, n, sig = checkable_benign[i]
        corrupted = 0.05 if sig >= 0.5 else 0.95
        injected_tab[(v, n)] = corrupted
        injected_keys.add((v, n))
    return injected_tab, injected_keys


def run_auditor_selftest(table, seed, n_inject):
    """Injected-error can-fail battery: catch_rate (flagged among injected) vs false_flag_rate (flagged
    among the REST of the checkable entries, unmodified -- the auditor's own baseline noise level)."""
    injected_tab, injected_keys = inject_errors(table, seed, n_inject)
    records, flagged = audit_table(injected_tab)
    n_injected = len(injected_keys)
    n_caught = sum(1 for k in injected_keys if k in flagged)
    catch_rate = round(n_caught / max(1, n_injected), 4)
    rest_checkable = [(r["v"], r["n"]) for r in records
                      if r["ontology_signal"] is not None and (r["v"], r["n"]) not in injected_keys]
    n_rest_flagged = sum(1 for k in rest_checkable if k in flagged)
    false_flag_rate = round(n_rest_flagged / max(1, len(rest_checkable)), 4)
    return {"n_injected": n_injected, "n_caught": n_caught, "catch_rate": catch_rate,
            "n_checkable_rest": len(rest_checkable), "n_rest_flagged": n_rest_flagged,
            "false_flag_rate": false_flag_rate, "injected_keys": sorted(injected_keys)}


# ======================================================================================================
# 5. IO helpers (atomic write per META_RULE_AH).
# ======================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def _write_start_marker(output_dir, mode):
    os.makedirs(output_dir, exist_ok=True)
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": mode, "host": platform.node()}
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


# ======================================================================================================
# 6. Main run.
# ======================================================================================================
def _score_slice(items, thin_score, tiny_tab, scaled_tab, rand_fn, scaled_scr_fn):
    acc_thin, pi_thin, strat_thin, strat_n = P._2afc(items, lambda v, p: thin_score(v, p)[0])
    acc_tiny, pi_tiny, strat_tiny, _ = P._2afc(items, lambda v, p: tiny_tab.get((v, p), 0.5))
    acc_scaled, pi_scaled, strat_scaled, _ = P._2afc(items, lambda v, p: scaled_tab.get((v, p), 0.5))
    acc_random, pi_rand, _, _ = P._2afc(items, rand_fn)
    acc_scr, pi_scr, _, _ = P._2afc(items, scaled_scr_fn)
    cov_curve = {}
    for f in COV_POINTS:
        sfn = P.make_rich_at_coverage(scaled_tab, thin_score, f)
        acc_f, _, _, _ = P._2afc(items, sfn)
        cov_curve[f"{f:.2f}"] = acc_f
    digests = {}
    for nm, pv in [("thin", pi_thin), ("tiny", pi_tiny), ("scaled", pi_scaled),
                   ("random", pi_rand), ("scaled_scrambled", pi_scr)]:
        digests[nm] = hashlib.sha256(np.asarray(pv, dtype=np.float64).tobytes()).hexdigest()[:16]
    return {
        "n_items": len(items),
        "acc_thin": acc_thin, "acc_tiny": acc_tiny, "acc_scaled": acc_scaled,
        "acc_random": acc_random, "acc_scaled_scrambled": acc_scr,
        "coverage_thin": thin_coverage_on_items(items, thin_score),
        "coverage_tiny": table_coverage(items, tiny_tab),
        "coverage_scaled": table_coverage(items, scaled_tab),
        "coverage_curve": cov_curve, "cardinality_ok": bool(len(cov_curve) == EXPECTED_COV_POINTS),
        "strat_acc_thin": strat_thin, "strat_acc_tiny": strat_tiny, "strat_acc_scaled": strat_scaled,
        "strat_n": strat_n,
        "digests": digests,
        "arms_differ_verified": len(set(digests.values())) == len(digests),
    }


def run_mode(mode):
    t0 = time.perf_counter()
    out_dir = _out_dir(mode)
    _write_start_marker(out_dir, mode)
    print(f"[{ANCHOR_NAME}:{mode}] START", flush=True)

    top_k = TOP_K_VERBS_SMOKE if mode == "smoke" else TOP_K_VERBS_FULL
    max_n = MAX_NOUNS_PER_VERB_SMOKE if mode == "smoke" else MAX_NOUNS_PER_VERB_FULL
    n_covslice_verbs = N_COVSLICE_VERBS_SMOKE if mode == "smoke" else N_COVSLICE_VERBS_FULL

    pair_freq, verb_freq, per_verb_noun_freq, n_mine = mine_pairs(mode, out_dir)
    scope, top_verbs = select_scope_pairs(verb_freq, per_verb_noun_freq, top_k, max_n, MIN_PAIR_FREQ)
    covslice_items = build_coverage_slice_items(verb_freq, per_verb_noun_freq, n_covslice_verbs)
    original_items = P.build_items()  # IDENTICAL to 29471/29475 (n=59, Third-Reader independent gold)

    thin_score, thin_stats, n_mine2 = P.build_thin_gfit(mode)
    tiny_tab = P.load_rich_table() or {}
    scaled_tab = load_json_table(SCALED_TABLE_PATH) or {}
    rand_fn = P.make_random_score()
    scaled_scr_fn = make_scrambled(scaled_tab, NEG_SEED + 51)

    scaled_present = len(scaled_tab) > 0

    res_orig = _score_slice(original_items, thin_score, tiny_tab, scaled_tab, rand_fn, scaled_scr_fn)
    res_cov = _score_slice(covslice_items, thin_score, tiny_tab, scaled_tab, rand_fn, scaled_scr_fn)

    audit_records, flagged = audit_table(scaled_tab) if scaled_present else ([], set())
    n_checkable = sum(1 for r in audit_records if r["ontology_signal"] is not None)
    n_flagged_clean = len(flagged)
    clean_flag_rate = round(n_flagged_clean / max(1, n_checkable), 4)
    auditor_battery = (run_auditor_selftest(scaled_tab, INJECT_SEED, N_INJECT) if scaled_present
                       else {"catch_rate": None, "false_flag_rate": None})

    baseline_in_band = bool(0.05 < res_cov["acc_thin"] < 0.95)
    random_is_chance = bool(0.40 <= res_cov["acc_random"] <= 0.60)
    discriminator_fires = bool(random_is_chance and baseline_in_band)

    verdict = "PENDING_SCALED_TABLE"
    band_reason = "scaled_seed_table_v1.json absent; run --dump-scope, author ratings, re-run"
    if scaled_present:
        gap_vs_thin_cov = round(res_cov["acc_scaled"] - res_cov["acc_thin"], 4)
        gap_vs_tiny_cov = round(res_cov["acc_scaled"] - res_cov["acc_tiny"], 4)
        scr_margin_cov = round(res_cov["acc_scaled"] - res_cov["acc_scaled_scrambled"], 4)
        catch = auditor_battery.get("catch_rate")
        ffr = auditor_battery.get("false_flag_rate")

        hard_fail = (
            gap_vs_tiny_cov <= 0.05
            or gap_vs_thin_cov <= 0.03
            or (catch is not None and catch < 0.34)
            or scr_margin_cov <= 0.03
            or not (random_is_chance and baseline_in_band)
            or res_cov["coverage_tiny"] > 0.20
        )
        hard_pass = (
            res_cov["coverage_scaled"] >= 0.55
            and res_cov["coverage_tiny"] <= 0.15
            and gap_vs_thin_cov >= 0.12
            and gap_vs_tiny_cov >= 0.12
            and res_cov["acc_scaled"] >= 0.65
            and random_is_chance
            and scr_margin_cov >= 0.10
            and (catch is not None and catch >= 0.75)
            and (ffr is not None and ffr <= 0.25)
        )
        if hard_fail:
            verdict = "HARD_FAIL_SCALING_DIDNT_HELP_OR_AUDITOR_VACUOUS"
            band_reason = (f"gap_vs_tiny_cov={gap_vs_tiny_cov:+.3f} gap_vs_thin_cov={gap_vs_thin_cov:+.3f} "
                           f"scr_margin_cov={scr_margin_cov:+.3f} catch_rate={catch} "
                           f"cov_tiny={res_cov['coverage_tiny']:.3f} "
                           f"random_ok={random_is_chance} base_in_band={baseline_in_band}")
        elif hard_pass:
            verdict = "HARD_PASS_SCALED_KNOWLEDGE_HELPS_AT_COVERAGE"
            band_reason = (f"cov_scaled={res_cov['coverage_scaled']:.3f} cov_tiny={res_cov['coverage_tiny']:.3f} "
                           f"gap_vs_thin_cov={gap_vs_thin_cov:+.3f} gap_vs_tiny_cov={gap_vs_tiny_cov:+.3f} "
                           f"scr_margin_cov={scr_margin_cov:+.3f} catch_rate={catch} false_flag_rate={ffr}")
        else:
            verdict = "MIDDLE_BAND"
            band_reason = (f"gap_vs_tiny_cov={gap_vs_tiny_cov:+.3f} gap_vs_thin_cov={gap_vs_thin_cov:+.3f} "
                           f"cov_scaled={res_cov['coverage_scaled']:.3f} catch_rate={catch}")

    elapsed = time.perf_counter() - t0
    msg = (f"VERDICT_core[COVSLICE n={res_cov['n_items']}] acc_scaled={res_cov['acc_scaled']} "
           f"acc_thin={res_cov['acc_thin']} acc_tiny={res_cov['acc_tiny']} "
           f"cov_scaled={res_cov['coverage_scaled']} cov_tiny={res_cov['coverage_tiny']} "
           f"cov_thin={res_cov['coverage_thin']} | auditor catch_rate={auditor_battery.get('catch_rate')} "
           f"false_flag_rate={auditor_battery.get('false_flag_rate')} n_checkable={n_checkable} "
           f"clean_flag_rate={clean_flag_rate} | ORIG[n={res_orig['n_items']}] "
           f"acc_scaled={res_orig['acc_scaled']} acc_tiny={res_orig['acc_tiny']} "
           f"acc_thin={res_orig['acc_thin']} | scope_pairs={len(scaled_tab)} top_verbs={len(top_verbs)} "
           f"n_mine={n_mine} | band_reason={band_reason}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_mining_sentences": n_mine, "n_scope_pairs": len(scaled_tab), "n_top_verbs": len(top_verbs),
        "n_covslice_items": len(covslice_items), "n_original_items": len(original_items),
        "coverage_slice": res_cov, "original_slice": res_orig,
        "auditor": {"n_checkable": n_checkable, "n_flagged_clean": n_flagged_clean,
                    "clean_flag_rate": clean_flag_rate, "injected_battery": auditor_battery,
                    "contra_thresh": CONTRA_THRESH, "n_inject": N_INJECT},
        "baseline_in_band": baseline_in_band, "random_is_chance": random_is_chance,
        "discriminator_fires": discriminator_fires,
        "band_reason": band_reason,
        "runtime_invariant": ("glass-box dict lookup ONLY at scoring time; NO LLM/network/autograd at "
                              "inference (build-time LLM authoring only, exactly 29471's invariant)"),
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": "2AFC discrimination-accuracy; no quantitative noise floor for the discriminator",
        "deterministic_seeding": "fixed int seeds + numpy default_rng + sorted(set); no hash()-seeded RNG",
        "one_variable_note": ("Identical 2AFC scorer (P._2afc, imported not reimplemented) and thin/tiny/"
                              "random mechanisms across both slices. ONLY the SCALED score table is new; "
                              "coverage-slice items are NEW (structural pseudo-gold from mining-corpus "
                              "attestation, disjoint SOURCE TEXT from the Third-Reader independent gold)."),
        "leakage_guard": ("SCALED table entries rated from a shuffled UNLABELED (verb,noun) pair list "
                          "(--dump-scope) BEFORE any item/gold-vs-distractor role was assigned to any pair "
                          "(29471's own discipline). Coverage-slice pseudo-gold = real corpus co-occurrence "
                          "(structural, not independently human-annotated) -- an HONEST, stated limitation, "
                          "not the same standard as the Third-Reader gold used for the continuity slice."),
        "coverage_slice_honest_limitation": ("gold_patient = the verb's most-frequent REAL attested content-"
                                             "noun patient in the mining corpus (structural pseudo-gold), NOT "
                                             "independent human argument-structure annotation. Verbs whose "
                                             "gold-schema role is nopat (report/cognition/motion/aspectual, "
                                             "per gold_mcguffey_lccp_argstruct_v1's own definition) are "
                                             "EXCLUDED from being the coverage-slice's positive-attestation "
                                             "verb to avoid clausal-complement mis-parses."),
        "mapped_ceiling_refs": (
            "29471 HARD_PASS_KNOWLEDGE_POVERTY_WAS_THE_WALL (tiny table): acc_thin=0.475->acc_rich=0.814 "
            "on a 59-item PROBE-SCOPED test (rich_cov_on_items=1.000 by construction). "
            "29475 MIDDLE_BAND_PARTIAL_GRANULARITY_RECOVERY (pure ontology): acc_indep_kb=0.568 "
            "(gap=+0.093 vs thin), frac_of_llm_lift_recovered=0.275 -- ontology alone recovers ~27%% of "
            "the LLM's lift; too sparse without LLM-supplied density."),
        "REQUIRED_FIELDS": ["verdict", "coverage_slice", "original_slice", "auditor",
                            "baseline_in_band", "random_is_chance", "runtime_invariant", "leakage_guard"],
    }
    write_metrics(out_dir, payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] verdict={verdict} -> {os.path.join(out_dir, 'metrics.json')}", flush=True)
    return payload


# ======================================================================================================
# 7. Self-test (constructs REAL objects at tiny scale; asserts arms + auditor + injected-error mechanics).
# ======================================================================================================
def self_test():
    exercised = set()

    # 1) REAL mining + scope-selection at SMOKE scale (real code path, not a synthetic-only branch).
    out_dir = _out_dir("smoke")
    pair_freq, verb_freq, per_verb_noun_freq, n_mine = mine_pairs("smoke", out_dir)
    exercised.add("SCV.run_reader_on_files")
    assert n_mine > 0 and len(verb_freq) > 0, "mining must produce real verb frequency at smoke scale"
    scope, top_verbs = select_scope_pairs(verb_freq, per_verb_noun_freq, TOP_K_VERBS_SMOKE,
                                          MAX_NOUNS_PER_VERB_SMOKE, MIN_PAIR_FREQ)
    scope2, top_verbs2 = select_scope_pairs(verb_freq, per_verb_noun_freq, TOP_K_VERBS_SMOKE,
                                            MAX_NOUNS_PER_VERB_SMOKE, MIN_PAIR_FREQ)
    assert scope == scope2 and top_verbs == top_verbs2, "scope selection must be deterministic"
    assert len(scope) > 0, "scope must be non-empty at smoke scale"
    exercised.add("select_scope_pairs")

    # 2) Coverage-slice construction: deterministic, well-formed, gold != neg.
    covslice = build_coverage_slice_items(verb_freq, per_verb_noun_freq, N_COVSLICE_VERBS_SMOKE)
    assert len(covslice) > 0, "coverage slice must be non-empty at smoke scale"
    for it in covslice:
        assert it["gold_patient"] != it["neg_filler"]
        assert it["neg_stratum"] in ("same_class", "cross_class", "fallback")
        assert it["v"] not in EXCLUDE_NOPAT_VERBS_FOR_COVSLICE_GOLD
    covslice2 = build_coverage_slice_items(verb_freq, per_verb_noun_freq, N_COVSLICE_VERBS_SMOKE)
    assert [(i["v"], i["gold_patient"], i["neg_filler"]) for i in covslice] == \
           [(i["v"], i["gold_patient"], i["neg_filler"]) for i in covslice2], "covslice must be deterministic"
    exercised.add("build_coverage_slice_items")

    # 3) REAL VerbNet/WordNet ontology signal (F.1: real_code_path) + auditor mechanics on a toy table.
    sig, kind = ontology_signal("give", "fruit")
    exercised.add("K.score_indep_kb_components")
    toy_table = {("give", "fruit"): 0.9, ("give", "day"): 0.1, ("eat", "apple"): 0.95, ("eat", "stone"): 0.05}
    records, flagged = audit_table(toy_table)
    assert isinstance(records, list) and len(records) == len(toy_table)
    exercised.add("audit_table")

    # 4) Injected-error can-fail battery on a toy table with KNOWN contradictions.
    #    Build a toy table where every entry has a checkable ontology signal, half already contradicting
    #    it (so injection has candidates to draw from that are currently benign) -- use "give"/"eat" family.
    toy_scaled = {}
    for v, n in [("give", "fruit"), ("give", "flowers"), ("give", "money"), ("eat", "apple"),
                 ("eat", "bread"), ("hold", "hands"), ("open", "door"), ("build", "houses")]:
        s, k = ontology_signal(v, n)
        toy_scaled[(v, n)] = (s if s is not None else 0.5)  # start BENIGN (rating == ontology signal)
    battery = run_auditor_selftest(toy_scaled, INJECT_SEED, n_inject=4)
    assert battery["n_injected"] >= 1, "toy injected-error battery must inject at least one entry"
    assert battery["catch_rate"] >= 0.5, (
        f"toy injected-error battery must catch most obviously-wrong entries; got {battery}")
    exercised.add("run_auditor_selftest")

    # 5) 2AFC + arms-differ mechanics reused from P (thin/tiny/scaled/random/scrambled all differ).
    #    Use DEDICATED toy items whose pairs are IN toy_scaled/tiny (real tiny table has "give"/"build"
    #    family entries) so TINY and SCALED do not both collapse to the same all-OOV 0.5 vector.
    thin_score, thin_stats, _ = P.build_thin_gfit("smoke")
    tiny_tab = P.load_rich_table() or {}
    rand_fn = P.make_random_score()
    scr_fn = make_scrambled(toy_scaled, NEG_SEED + 51)
    toy_arms_items = [
        {"v": "give", "gold_patient": "fruit", "neg_filler": "day", "neg_stratum": "cross_class"},
        {"v": "eat", "gold_patient": "apple", "neg_filler": "bread", "neg_stratum": "same_class"},
        {"v": "hold", "gold_patient": "hands", "neg_filler": "walk", "neg_stratum": "cross_class"},
        {"v": "build", "gold_patient": "houses", "neg_filler": "blockhouse", "neg_stratum": "same_class"},
    ]
    res = _score_slice(toy_arms_items, thin_score, tiny_tab, toy_scaled, rand_fn, scr_fn)
    assert res["arms_differ_verified"], "5 per-item score vectors must not be bit-identical (META_RULE_AF)"
    assert res["cardinality_ok"], "coverage curve must have EXPECTED_COV_POINTS entries"

    # 6) Determinism: table_coverage / thin_coverage_on_items are pure functions of inputs.
    c1 = table_coverage(covslice[:5], toy_scaled)
    c2 = table_coverage(covslice[:5], toy_scaled)
    assert c1 == c2

    ok = run_validity_preflight([
        {"kind": "real_code_path",
         "full_substrate_entrypoints": ["SCV.run_reader_on_files", "select_scope_pairs",
                                        "build_coverage_slice_items", "K.score_indep_kb_components",
                                        "audit_table", "run_auditor_selftest"],
         "exercised_entrypoints": exercised},
        {"kind": "metric_moves", "metric_name": "auditor_catch_rate",
         "before": 0.0, "after": battery["catch_rate"]},
        {"kind": "negative_control_margin", "control_scores": [battery["false_flag_rate"]] * 3,
         "headline_threshold": battery["catch_rate"], "higher_is_pass": True, "margin": 0.0,
         "control_name": "auditor_false_flag_rate_vs_catch_rate"},
    ], run_mode="self_test")
    assert ok, "validity preflight failed at self-test scale"

    print(f"[{ANCHOR_NAME}] self-test PASS | scope={len(scope)} covslice={len(covslice)} "
          f"toy_battery={battery} exercised={sorted(exercised)}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--dump-scope", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.dump_scope:
        dump_scope_pairs("full"); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --dump-scope | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
