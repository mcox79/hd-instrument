"""ROLE-ELIGIBILITY CASCADE (REC): does a glass-box STRUCTURAL argument/adjunct classifier SUPPRESS the
bare-NP-adjunct-as-PATIENT residual (came HOME) that LCCP arm-C still licenses, WITHOUT hurting true
transitive-argument recall, vs INDEPENDENT gold -- the exact trade-off the semantic/coherence gate failed?

QUESTION (the VET-localized break-0.50 residual, per the arg/adjunct brain-drill
notes/research_argument_adjunct_distinction_brain_drill_2026-07-19.md + VET atom a5c9d930):
  LCCP arm-C (precision 0.50 vs independent gold) still mis-licenses BARE locative/temporal-form fillers as
  the PATIENT ("came HOME"). These are ADJUNCTS (Needham&Toivonen: 'home' is a GRADIENT derived-argument),
  never a direct object. The confirmed diagnosis (VET a5c9d930): selectional-coherence is ORTHOGONAL to
  arg/adjunct ("came home" is perfectly coherent) -> a semantic gate CANNOT catch this; the fix must be
  STRUCTURAL. LCCP's f_prep/f_func/f_clause weights already handle MARKED non-objects; the residual is the
  UNMARKED bare-NP adjunct (no prep, no function-word marker). Does a 2-signal Role-Eligibility Cascade
  (categorial prior + learned verb-diversity entropy) suppress these WITHOUT hurting true arguments?

THE 3-SIGNAL CASCADE (glass-box, CPU, NO treebank, NO external LLM; built on LCCP arm-C output):
  ARM A  = LCCP arm-C kept set as-is (the 0.50 baseline; still licenses came/home as patient).
  ARM B1 = A + CATEGORIAL PRIOR (Signal 0): suppress a kept PATIENT filler iff it is (a) a BARE adverbial
    FORM (immediate pre-token in the raw sentence is NOT a determiner/possessive/preposition -> no NP shell)
    AND (b) grounded place/time/manner TYPE (WordNet first-noun-sense lexname in {noun.location, noun.time}
    OR a dominant locative/temporal ADVERB sense). This is a category RULE (form-class + grounded-type),
    NOT a hand-list of adjunct words. The BARE-FORM guard is the precision protector: true place/time
    PATIENTS ("left the room", "spend his time", "choose their places") are DETERMINER-marked NP shells ->
    NOT bare -> KEPT. (isolates the cheap structural prior; ONE variable A->B1.)
  ARM B2 = B1 + VERB-DIVERSITY ENTROPY (Signal 1, LEARNED): for every remaining bare-NP post-verbal filler,
    compute cross-verb co-occurrence breadth (# distinct verbs the filler appears with across the corpus,
    PropBank AM-vs-ARG design logic: wide = adjunct, narrow = argument); suppress a kept patient iff its
    verb-diversity >= div_thr. (isolates the learned generalizing lever; ONE variable B1->B2; CORPUS-SPARSE
    on 163 sents -> pre-registered can-FAIL via recall cost, drill Prediction-4.)
  DERIVED-ARGUMENT / DEFERRED middle state (Signal 2, Needham&Toivonen): a suppressed categorial filler on a
    directed-MOTION verb (WordNet verb.motion) is TAGGED DERIVED_ARG_GOAL (never PATIENT, but a real GOAL
    role) rather than hard-discarded -- recorded per-instance for VET (n is tiny; spot-check, not a metric).

MEASURED (decisive, per arm, vs INDEPENDENT gold data/gold_mcguffey_lccp_argstruct_v1.json):
  overall precision/recall/F1 + the FP class split (subcat/within/spurious, reused from LCCP scorer);
  the CATEGORIAL-TARGET RESIDUAL (arm-A FPs that ARE bare-form grounded place/time/manner) and the fraction
  B1/B2 suppress; the TRANSITIVE-ARGUMENT RECALL RETENTION (gold-pos patients each arm keeps -- the exact
  trade-off the semantic gate failed); per-SIGNAL attribution (B1 alone vs B1->B2 delta); the verb-diversity
  DISTRIBUTION SEPARATION (place/time vs other fillers -- Prediction-4 corpus-sufficiency check); per-
  instance suppression + derived-arg dump for VET re-annotation.

DESIGN-GATE (pre-registered; verified at smoke BEFORE full):
  (G1) REAL baseline = LIVE LCCP arm-C recompute vs INDEPENDENT gold (precision ~0.50, reproduced not cited).
  (G2) baseline_in_band: 0.05 < arm-A precision < 0.95 (real, un-saturated wall).
  (G3) CAN-FAIL-BOTH-WAYS: HARD_PASS (B1 suppresses >=50% of the categorial-target residual AND transitive-
       recall cost <=0.05 AND precision non-decreasing = a real STRUCTURAL break-0.50 step succeeding where
       the semantic gate failed) OR HARD_FAIL (categorial recall cost >0.10 = the trade-off BITES, semantic-
       gate failure reproduced; OR <15% of the target residual suppressed) OR PARTIAL/LOW_CEILING (the
       addressable residual is a small fraction of the 0.50 wall -> corpus-sparsity caps absolute magnitude).
  (G4) discriminator fires: B1 suppresses >0 arm-A patients AND kept sets differ across A/B1/B2.
  (G5) ONE VARIABLE per signal: A->B1 = categorial prior; B1->B2 = verb-diversity entropy (both structural/
       distributional; the LCCP cue-weights held IDENTICAL -- arm A is LCCP arm-C output, untouched).

VERDICT BANDS (pre-registered):
  categorial_reduction_frac = |B1 suppressed among categorial-target residual| / |categorial-target residual|
  transitive_recall_cost_B1 = recall_A - recall_B1  (patient-level, gold-pos)
  residual_share = |categorial-target residual| / total_FP_A  (how much of the 0.50 wall is arg/adjunct)
  HARD_PASS_STRUCTURAL_NO_RECALL_COST: categorial_reduction_frac >= 0.50 AND transitive_recall_cost_B1 <= 0.05
    AND precision_B1 >= precision_A. (categorial signal cleanly separates arg/adjunct where semantics could not.)
  HARD_FAIL_TRADEOFF_BITES: transitive_recall_cost_B1 > 0.10 (categorial hurts TRUE patients -- the semantic-
    gate failure mode) OR categorial_reduction_frac < 0.15 (residual NOT structurally separable).
  MIDDLE_BAND_PARTIAL: in between.
  SCOPE TAG (independent, honest magnitude): LOW_CEILING_CORPUS_SPARSE if residual_share < 0.15 (the arg/
    adjunct-attributable residual is a SMALL fraction of the 0.50 wall; most FPs are orthogonal modes --
    quotative speaker attribution / prep-slip / locative-inversion / wrong-constituent -- the coref + head-
    finder levers' job, NOT this cell). B2 tag: VERB_DIVERSITY_CORPUS_SPARSE if (mean_nverbs_place_time -
    mean_nverbs_other) < 0.5 OR B2 recall cost >= its extra FP-suppression (signal too sparse / inverted).

BRAIN-CHECK (pre-registered; outcome NOT pre-assumed): categorial/form + grounded-type + verb-diversity
  (PropBank ARG/AM) is brain-faithful (children license verb frames from distribution; Friederici&Frisch
  frame-TYPE gate distinct from count). The bare-form categorial prior is exhaustive/global where the brain's
  online parser must approximate. REAL bound the brain SHARES: the arg/adjunct boundary is a documented
  GRADIENT (Przepiorkowski, Toivonen) with a genuine derived-argument middle for exactly "came home"
  (Needham&Toivonen) -- clean binary separation is NOT achievable even by expert linguistic theory, hence the
  DERIVED_ARG_GOAL deferred tag not a forced binary. Corpus-sparsity risk (Prediction-4): verb-diversity
  entropy on 163 sents may not separate arg/adjunct -> same-limit accept, Signal-0 categorial does the work.

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- one live LCCP arm-C recompute
  (~30-60s) + a glass-box pre-token form check + WordNet lexname query + a distinct-verb count over ~114
  sentences; wall < ~90s. Foreground local-to-completion (NO queue; NO push; NO remote-persist). Storage:
  no_storage (extraction-precision measurement). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds (LCCP's),
  deterministic hashlib + deterministic WordNet synset order; no salted builtin hash / list(set).

CELL-TEMPLATE MANDATORY (LOCAL foreground measurement; NOT queue-dispatched):
- arms_differ_verified at smoke (A vs B1 vs B2 kept-set hashes differ)
- final_metrics_atomicity: tmp_replace (os.replace)
- except SystemExit: raise BEFORE except Exception (no BaseException)
- baseline_in_band at smoke (0.05 < arm-A precision < 0.95)
- discriminator fires at smoke (B1 suppresses >0; kept sets differ)
- scaffold-free witness: a REAL came/home the classifier suppresses that LCCP-alone licenses; a true place/
  time patient (left/room, spend/time, choose/places) it KEEPS (form-guard); a derived-arg GOAL tag on come/home
- deterministic seeding; numbers tagged MEASURED@ (printed at run) / CITED@ (0.50 LCCP arm-C atom 29338)
"""
from __future__ import annotations

import os
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import argparse
import hashlib
import json
import sys
import time
import traceback
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

import experiments.exp_learned_argstruct_parser_lccp_independent_gold_v1 as LCCP  # noqa: E402

ANCHOR_NAME = "arg_adjunct_role_eligibility_categorial_break050_v1"
CITED_LCCP_ARMC_PRECISION = 0.50  # CITED@ atom 29338 / LCCP arm-C independent-gold precision
ARMS = ["A_lccp_armC", "B1_categorial", "B2_verbdiversity"]

# ---- WordNet grounded typing (Signal-0 place/time/manner; Signal-2 verb.motion). Deterministic order.
_WN = None
_WN_OK = False
_WN_ERR = None
try:
    from nltk.corpus import wordnet as _wnmod
    _ = _wnmod.synsets("table")  # force-load; raises if corpus absent
    _WN = _wnmod
    _WN_OK = True
except Exception as _e:  # NOT BaseException; explicit, non-silent (flagged in metrics)
    _WN_ERR = f"{type(_e).__name__}: {str(_e)[:200]}"

# Determiner / possessive surface forms that mark an NP shell (NOT a bare adverbial). Principled closed
# class of English determiners+possessives+quantifier-determiners -- a grammatical category, not a
# corpus-tuned blocklist of adjunct words.
DETERMINERS = {"the", "a", "an", "this", "that", "these", "those", "his", "her", "its", "their", "my",
               "your", "our", "one", "some", "any", "no", "each", "every", "another", "all", "both",
               "many", "few", "much", "several", "such", "which", "what", "whose"}

# Grounded place/time lexnames (Signal-0 category). Manner handled via adverb sense below.
PLACE_LEX = {"noun.location"}
TIME_LEX = {"noun.time"}


def grounded_adjunct_type(token):
    """Return 'PLACE' | 'TIME' | 'MANNER' | None for a filler token, via WordNet grounded typing.
    Deterministic. Place/time = dominant (first-2) noun-sense lexname noun.location/noun.time OR a dominant
    locative/temporal ADVERB sense. Grounded-type category rule -- NOT a hand-authored adjunct word list."""
    if not _WN_OK:
        return None
    t = (token or "").lower()
    if not t.isalpha() or len(t) < 3:
        return None
    # PRONOUNS are a nominal, PATIENT-eligible closed class -- never a bare locative/temporal adverbial form.
    # (Guards WordNet mis-typings like 'me' -> noun.location(Maine) from suppressing true pronoun patients.)
    if t in LCCP.PRONOUN:
        return None
    nsyns = _WN.synsets(t, pos="n")
    lex_n = [s.lexname() for s in nsyns[:2]]
    if lex_n:
        if lex_n[0] in PLACE_LEX or (len(lex_n) > 1 and lex_n[0] not in TIME_LEX and lex_n[1] in PLACE_LEX and lex_n[0] == "noun.location"):
            return "PLACE"
        if lex_n[0] in PLACE_LEX:
            return "PLACE"
        if lex_n[0] in TIME_LEX:
            return "TIME"
    # dominant adverb sense with locative/temporal gloss (home/there/here/away/abroad/indoors/hence...)
    advs = _WN.synsets(t, pos="r")
    if advs and not nsyns:
        # bare adverbial with no noun sense at all -> locative/temporal/manner adverb
        return "MANNER"
    return None


def is_motion_verb(v_lemma):
    """Directed-motion construction detector (Signal-2 derived-argument): WordNet verb.motion in first-3
    verb synsets. Glass-box, deterministic. Used ONLY to tag a suppressed goal-locative as DERIVED_ARG_GOAL."""
    if not _WN_OK:
        return False
    syns = _WN.synsets((v_lemma or "").lower(), pos="v")[:3]
    return any(s.lexname() == "verb.motion" for s in syns)


def pre_token_form(sid, sent_text, v_surf, p_surf):
    """Immediate pre-token of the filler in the raw sentence + its FORM class.
    Returns (prev_token, 'DET'|'PREP'|'BARE'|'NONE'). BARE = no determiner/possessive/preposition shell."""
    tk = LCCP.tokenize(sent_text[sid])
    iv, ip = LCCP.find_pair_positions(tk, v_surf, p_surf)
    if ip is None:
        return None, "NONE"
    prev = tk[ip - 1] if ip - 1 >= 0 else ""
    if prev in DETERMINERS:
        return prev, "DET"
    if prev in LCCP.PREPS:
        return prev, "PREP"
    return prev, "BARE"


def kept_hash(kept):
    items = sorted(f"{sid}|{'|'.join(t)}" for sid, t in kept)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


# ----------------------------------------------------------------------------------------------
# The Role-Eligibility Cascade over LCCP arm-C output.
# ----------------------------------------------------------------------------------------------
def build_cascade(order, sent_text, reader_svo, keptC, div_thr):
    """Return (kept_A, kept_B1, kept_B2, per_instance, verb_div, cat_target_meta).
    keptC = LCCP arm-C kept list of (sid, (v_surf,a,p)). Applies Signal-0 categorial then Signal-1 diversity."""
    # verb-diversity: distinct verbs each filler token co-occurs with, over ALL reader candidates
    filler_verbs = defaultdict(set)
    for sid in order:
        for (v, a, p) in reader_svo[sid]:
            filler_verbs[p].add(LCCP.lemma_verb(v))
    verb_div = {p: len(vs) for p, vs in filler_verbs.items()}

    kept_A = list(keptC)
    kept_B1, kept_B2 = [], []
    per_instance = []
    for sid, tup in keptC:
        v_surf, a, p = tup
        v_lemma = LCCP.lemma_verb(v_surf)
        prev, form = pre_token_form(sid, sent_text, v_surf, p)
        gtype = grounded_adjunct_type(p)
        # Signal-0 categorial: bare adverbial FORM + grounded place/time/manner TYPE -> adjunct, suppress
        cat_adjunct = bool(form == "BARE" and gtype in ("PLACE", "TIME", "MANNER"))
        b1_keep = not cat_adjunct
        # Signal-1 verb-diversity: over the bare-NP fillers B1 kept, high cross-verb breadth -> adjunct
        nverbs = verb_div.get(p, 0)
        div_adjunct = bool(b1_keep and form == "BARE" and nverbs >= div_thr)
        b2_keep = b1_keep and not div_adjunct
        # Signal-2 derived-argument tag (never patient; a real GOAL role) for motion-verb goal-locatives
        derived_tag = None
        if cat_adjunct and gtype == "PLACE" and is_motion_verb(v_lemma):
            derived_tag = "DERIVED_ARG_GOAL"
        elif cat_adjunct:
            derived_tag = "ADJUNCT_" + (gtype or "?")
        if b1_keep:
            kept_B1.append((sid, tup))
        if b2_keep:
            kept_B2.append((sid, tup))
        per_instance.append({
            "sid": sid, "v": v_lemma, "patient": p, "pre_token": prev, "form": form,
            "grounded_type": gtype, "verb_diversity": nverbs,
            "cat_adjunct_suppressed_B1": cat_adjunct, "div_adjunct_suppressed_B2": div_adjunct,
            "derived_arg_tag": derived_tag,
        })
    cat_target_meta = {"filler_verbs": {p: sorted(vs) for p, vs in filler_verbs.items()}}
    return kept_A, kept_B1, kept_B2, per_instance, verb_div, cat_target_meta


def categorial_target_residual(kept_A, gold, sent_text):
    """arm-A FALSE POSITIVES that ARE bare-form grounded place/time/manner (the addressable arg/adjunct class)."""
    target = []
    for sid, tup in kept_A:
        v = LCCP.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None:
            continue  # it's a TRUE patient, not a residual FP
        prev, form = pre_token_form(sid, sent_text, tup[0], p)
        gtype = grounded_adjunct_type(p)
        if form == "BARE" and gtype in ("PLACE", "TIME", "MANNER"):
            cls = "SUBCAT" if v in rec["nopat"] else ("WITHIN" if v in rec["pos_verbs"] else "SPURIOUS")
            target.append({"sid": sid, "v": v, "patient": p, "grounded_type": gtype, "fp_class": cls})
    return target


def suppressed_true_patients(kept_from, kept_to, gold):
    """gold-pos patients present in kept_from but removed in kept_to (the RECALL COST of the suppression)."""
    to_set = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in kept_to)
    lost = []
    for sid, tup in kept_from:
        v = LCCP.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None and (sid, v, p) not in to_set:
            lost.append({"sid": sid, "v": v, "patient": p})
    return lost


def verb_diversity_separation(order, reader_svo):
    """Prediction-4 corpus-sufficiency: verb-diversity of place/time-typed fillers vs other fillers."""
    filler_verbs = defaultdict(set)
    for sid in order:
        for (v, a, p) in reader_svo[sid]:
            filler_verbs[p].add(LCCP.lemma_verb(v))
    pt, other = [], []
    for p, vs in filler_verbs.items():
        n = len(vs)
        if grounded_adjunct_type(p) in ("PLACE", "TIME", "MANNER"):
            pt.append(n)
        else:
            other.append(n)
    return {"n_place_time_fillers": len(pt), "mean_nverbs_place_time": round(float(np.mean(pt)), 4) if pt else 0.0,
            "max_nverbs_place_time": int(max(pt)) if pt else 0,
            "n_other_fillers": len(other), "mean_nverbs_other": round(float(np.mean(other)), 4) if other else 0.0,
            "max_nverbs_other": int(max(other)) if other else 0,
            "separation_gap": round((float(np.mean(pt)) if pt else 0.0) - (float(np.mean(other)) if other else 0.0), 4)}


# ----------------------------------------------------------------------------------------------
# Config + run.
# ----------------------------------------------------------------------------------------------
def cfg_smoke():
    # smoke slice MUST contain the bare-NP-adjunct discriminator (came/home lives in L10) -- SMOKE-MUST-FIRE.
    return dict(slice_lessons=["L04", "L10"], div_thr=3, seed=7)


def cfg_full():
    return dict(slice_lessons=["L04", "L05", "L07", "L08", "L09", "L10", "L12"], div_thr=3, seed=7)


def run_lccp_armC(slice_lessons, seed):
    """Live LCCP arm-C recompute (G1 real baseline; reproduced not cited)."""
    lcfg = dict(slice_lessons=slice_lessons, sel_keep=0.28, sel_drop=0.10, lr=0.20, epochs=60,
                keep_thr=0.45, subcat_thr=0.42, heldout_frac=0.25, k_constructions=4, seed=seed)
    order, sent_text, reader_svo = LCCP.load_slice_and_reader(slice_lessons)
    gold, gold_meta = LCCP.load_gold(slice_lessons)
    toks = set()
    for sid in order:
        for v, a, p in reader_svo[sid]:
            toks.update([p, LCCP.lemma_verb(v)])
    for sid, rec in gold.items():
        for g in rec["pos"]:
            toks.update([g["patient"], g["v"]])
    glove = LCCP.load_glove_for(toks)
    decisions, artifacts, subcat_dec, ho, seen, inst_groups, w = LCCP.run_arms(
        order, reader_svo, sent_text, glove, lcfg, seed)
    return order, sent_text, reader_svo, gold, gold_meta, decisions["C_lccp"]


def run_config(cfg):
    order, sent_text, reader_svo, gold, gold_meta, keptC = run_lccp_armC(cfg["slice_lessons"], cfg["seed"])
    kept_A, kept_B1, kept_B2, per_instance, verb_div, cmeta = build_cascade(
        order, sent_text, reader_svo, keptC, cfg["div_thr"])
    decisions = {"A_lccp_armC": kept_A, "B1_categorial": kept_B1, "B2_verbdiversity": kept_B2}

    arm_metrics = {arm: LCCP.score_arm(decisions[arm], gold) for arm in ARMS}
    cat_target = categorial_target_residual(kept_A, gold, sent_text)
    # how many of the categorial-target residual does each arm suppress?
    def suppressed_targets(kept):
        keep_set = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in kept)
        return [t for t in cat_target if (t["sid"], t["v"], t["patient"]) not in keep_set]
    b1_supp_target = suppressed_targets(kept_B1)
    b2_supp_target = suppressed_targets(kept_B2)
    recall_cost_B1 = suppressed_true_patients(kept_A, kept_B1, gold)
    recall_cost_B2_over_B1 = suppressed_true_patients(kept_B1, kept_B2, gold)
    b2_extra_fp = [d for d in per_instance if d["div_adjunct_suppressed_B2"]]
    vdiv_sep = verb_diversity_separation(order, reader_svo)

    A = arm_metrics["A_lccp_armC"]; B1 = arm_metrics["B1_categorial"]; B2 = arm_metrics["B2_verbdiversity"]
    n_target = len(cat_target)
    cat_reduction_frac = (len(b1_supp_target) / n_target) if n_target else 0.0
    recall_cost_pts = round(A["recall"] - B1["recall"], 4)
    residual_share = round(n_target / A["total_fp"], 4) if A["total_fp"] else 0.0

    attribution = {
        "categorial_target_residual": cat_target, "n_categorial_target": n_target,
        "B1_suppressed_targets": b1_supp_target, "categorial_reduction_frac": round(cat_reduction_frac, 4),
        "B1_transitive_recall_cost_pts": recall_cost_pts, "B1_true_patients_lost": recall_cost_B1,
        "B2_extra_suppressed_targets_beyond_B1": [t for t in b2_supp_target if t not in b1_supp_target],
        "B2_bare_fillers_suppressed": [(d["sid"], d["v"], d["patient"], d["verb_diversity"]) for d in b2_extra_fp],
        "B2_true_patients_lost_over_B1": recall_cost_B2_over_B1,
        "residual_share_of_total_FP": residual_share,
        "verb_diversity_separation": vdiv_sep,
    }
    return arm_metrics, attribution, per_instance, decisions, gold, gold_meta, order


def build_verdict(arm_metrics, attribution):
    A = arm_metrics["A_lccp_armC"]; B1 = arm_metrics["B1_categorial"]
    frac = attribution["categorial_reduction_frac"]
    recall_cost = attribution["B1_transitive_recall_cost_pts"]
    prec_nondecr = B1["precision"] >= A["precision"]
    n_target = attribution["n_categorial_target"]
    if recall_cost > 0.10 or (n_target > 0 and frac < 0.15):
        verdict = "HARD_FAIL_TRADEOFF_BITES"
    elif n_target > 0 and frac >= 0.50 and recall_cost <= 0.05 and prec_nondecr:
        verdict = "HARD_PASS_STRUCTURAL_NO_RECALL_COST"
    else:
        verdict = "MIDDLE_BAND_PARTIAL"
    # independent scope tag (magnitude honesty)
    scope = "LOW_CEILING_CORPUS_SPARSE" if attribution["residual_share_of_total_FP"] < 0.15 else "MATERIAL_SHARE"
    sep = attribution["verb_diversity_separation"]
    b2_extra = len(attribution["B2_extra_suppressed_targets_beyond_B1"])
    b2_cost = len(attribution["B2_true_patients_lost_over_B1"])
    b2_tag = ("VERB_DIVERSITY_CORPUS_SPARSE"
              if (sep["separation_gap"] < 0.5 or b2_cost >= max(1, b2_extra)) else "VERB_DIVERSITY_ADDS")
    return {"verdict": verdict, "scope_tag": scope, "verb_diversity_tag": b2_tag,
            "categorial_reduction_frac": frac, "B1_transitive_recall_cost_pts": recall_cost,
            "precision_A": A["precision"], "precision_B1": B1["precision"],
            "precision_delta_B1_minus_A": round(B1["precision"] - A["precision"], 4),
            "residual_share_of_total_FP": attribution["residual_share_of_total_FP"],
            "b2_extra_fp_suppressed": b2_extra, "b2_true_patients_lost": b2_cost}


def scaffold_free_witness(per_instance, decisions, gold):
    """A REAL came/home suppressed by B1 (kept by A) + a true place/time patient KEPT by B1 (form-guard) +
    a derived-arg GOAL tag."""
    a_set = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in decisions["A_lccp_armC"])
    b1_set = set((sid, LCCP.lemma_verb(t[0]), t[2]) for sid, t in decisions["B1_categorial"])
    supp = None
    for d in per_instance:
        if d["cat_adjunct_suppressed_B1"]:
            supp = [d["sid"], d["v"], d["patient"], d["grounded_type"], d["derived_arg_tag"]]
            break
    # a true place/time patient B1 KEEPS (determiner-marked; the form-guard protects true args)
    keep_pt = None
    for sid, tup in decisions["B1_categorial"]:
        v = LCCP.lemma_verb(tup[0]); p = tup[2]
        rec = gold.get(sid, {"pos": [], "nopat": set(), "pos_verbs": set()})
        if LCCP.match_pos(v, p, rec["pos"]) is not None and grounded_adjunct_type(p) in ("PLACE", "TIME"):
            keep_pt = [sid, v, p, grounded_adjunct_type(p)]
            break
    derived = [d for d in per_instance if d["derived_arg_tag"] == "DERIVED_ARG_GOAL"]
    return {"came_home_class_suppressed_by_B1_kept_by_A": supp,
            "true_place_time_patient_kept_by_B1_form_guard": keep_pt,
            "derived_arg_goal_tags": [[d["sid"], d["v"], d["patient"]] for d in derived],
            "witness": "PASS" if (supp is not None) else "PARTIAL"}


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)
    os.replace(tmp, final)


def run_mode(mode):
    t0 = time.perf_counter()
    cfg = cfg_smoke() if mode == "smoke" else cfg_full()
    output_dir = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))
    arm_metrics, attribution, per_instance, decisions, gold, gold_meta, order = run_config(cfg)
    vd = build_verdict(arm_metrics, attribution)

    hashes = {arm: kept_hash(decisions[arm]) for arm in ARMS}
    assert hashes["A_lccp_armC"] != hashes["B1_categorial"], "META_RULE_AF: A==B1 (categorial no-op)"
    # B1 vs B2 may legitimately be identical if verb-diversity suppresses nothing (corpus-sparse) -> exempt.
    b1b2_differ = hashes["B1_categorial"] != hashes["B2_verbdiversity"]

    A = arm_metrics["A_lccp_armC"]; B1 = arm_metrics["B1_categorial"]; B2 = arm_metrics["B2_verbdiversity"]
    baseline_in_band = bool(0.05 < A["precision"] < 0.95)
    n_b1_suppressed = len(decisions["A_lccp_armC"]) - len(decisions["B1_categorial"])
    discriminator_fires = bool(n_b1_suppressed > 0 and hashes["A_lccp_armC"] != hashes["B1_categorial"])
    witness = scaffold_free_witness(per_instance, decisions, gold)
    elapsed = time.perf_counter() - t0

    v = vd["verdict"]
    msg = (f"{v} [{vd['scope_tag']}] [{vd['verb_diversity_tag']}] | slice={'+'.join(cfg['slice_lessons'])} "
           f"| A P={A['precision']:.3f} R={A['recall']:.3f} FP={A['total_fp']}(sub={A['subcat_fp']},wf={A['within_frame_fp']},sp={A['spurious_verb_fp']}) "
           f"| B1 P={B1['precision']:.3f} R={B1['recall']:.3f} FP={B1['total_fp']} "
           f"| B2 P={B2['precision']:.3f} R={B2['recall']:.3f} FP={B2['total_fp']} "
           f"| cat_target_residual={attribution['n_categorial_target']} reduced_frac={vd['categorial_reduction_frac']:.3f} "
           f"| B1_recall_cost={vd['B1_transitive_recall_cost_pts']:+.3f} residual_share={vd['residual_share_of_total_FP']:.3f} "
           f"| Pdelta_B1={vd['precision_delta_B1_minus_A']:+.3f} "
           f"| vdiv gap={attribution['verb_diversity_separation']['separation_gap']:+.3f} "
           f"(PT={attribution['verb_diversity_separation']['mean_nverbs_place_time']:.2f}/other={attribution['verb_diversity_separation']['mean_nverbs_other']:.2f}) "
           f"B2extra={vd['b2_extra_fp_suppressed']} B2cost={vd['b2_true_patients_lost']} "
           f"| base_in_band={baseline_in_band} discrim={discriminator_fires} wn={_WN_OK}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": v, "verdict_msg": msg, "summary": msg,
        "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(), "config": cfg,
        "arm_metrics": arm_metrics, "verdict_detail": vd, "attribution": attribution,
        "per_instance": per_instance, "kept_hashes": hashes, "arms_differ_verified": True,
        "b1_b2_differ": b1b2_differ, "baseline_in_band": baseline_in_band,
        "discriminator_fires": discriminator_fires, "scaffold_free_witness": witness,
        "wordnet_available": _WN_OK, "wordnet_err": _WN_ERR, "final_metrics_atomicity": "tmp_replace",
        "cited_lccp_armC_precision": CITED_LCCP_ARMC_PRECISION,
        "independent_gold_source": "data/gold_mcguffey_lccp_argstruct_v1.json (single-annotator; pos + nopat verb-instances).",
        "gold_meta": gold_meta,
        "REQUIRED_FIELDS": ["verdict", "arm_metrics", "verdict_detail", "attribution", "per_instance",
                            "scaffold_free_witness"],
        "notes": ("REC arg/adjunct classifier over LCCP arm-C. A=LCCP arm-C, B1=+categorial prior (bare-form "
                  "+ grounded place/time/manner), B2=+verb-diversity entropy. HARD_PASS = B1 suppresses >=50% "
                  "of the bare-NP-adjunct target residual at recall-cost <=0.05 (structural signal succeeds "
                  "where semantic gate failed). HARD_FAIL = recall cost >0.10 (trade-off bites) OR <15% "
                  "reduced. Scope tag LOW_CEILING if the target residual is <15% of the 0.50 wall (corpus-"
                  "sparse; rest = orthogonal quotative/prep/inversion/wrong-constituent modes). CLAIM-VET-"
                  "pending; single-annotator gold (caveated); derived-arg GOAL tags spot-check-only."),
    }
    write_metrics(output_dir, payload)

    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(output_dir, 'metrics.json')}", flush=True)
    for arm in ARMS:
        m = arm_metrics[arm]
        print(f"  [{arm:>16}] P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} "
              f"n_pred={m['n_pred']} tp={m['tp']} FP(sub/wf/sp)={m['subcat_fp']}/{m['within_frame_fp']}/{m['spurious_verb_fp']}", flush=True)
    print(f"  [categorial target residual] n={attribution['n_categorial_target']} : "
          f"{[(t['sid'],t['v'],t['patient'],t['grounded_type']) for t in attribution['categorial_target_residual']]}", flush=True)
    print(f"  [B1 suppressed of target] {[(t['sid'],t['v'],t['patient']) for t in attribution['B1_suppressed_targets']]}", flush=True)
    print(f"  [B1 recall cost] true patients lost: {attribution['B1_true_patients_lost']}", flush=True)
    print(f"  [B2 verb-diversity] extra_fp={[b for b in attribution['B2_bare_fillers_suppressed']]} "
          f"true_patients_lost_over_B1={attribution['B2_true_patients_lost_over_B1']}", flush=True)
    print(f"  [verb-diversity separation] {attribution['verb_diversity_separation']}", flush=True)
    print(f"  [witness] {witness}", flush=True)
    return payload


def self_test():
    # form + grounded-type sanity on the canonical cases (MEASURED at run; asserts are structural invariants)
    assert LCCP.lemma_verb("came") == "come"
    assert grounded_adjunct_type("home") in ("PLACE", "MANNER"), grounded_adjunct_type("home")
    assert grounded_adjunct_type("castle") is None, grounded_adjunct_type("castle")
    assert grounded_adjunct_type("ball") is None
    # motion verb
    assert is_motion_verb("come") or is_motion_verb("go"), "come/go should be verb.motion"
    # end-to-end smoke
    cfg = cfg_smoke()
    arm_metrics, attribution, per_instance, decisions, gold, gold_meta, order = run_config(cfg)
    vd = build_verdict(arm_metrics, attribution)
    A = arm_metrics["A_lccp_armC"]; B1 = arm_metrics["B1_categorial"]
    # arms must differ (categorial fired) OR explicitly report no-fire
    ha = kept_hash(decisions["A_lccp_armC"]); hb = kept_hash(decisions["B1_categorial"])
    print(f"[{ANCHOR_NAME}] self-test: verdict={vd['verdict']} scope={vd['scope_tag']} "
          f"A_P={A['precision']:.3f} B1_P={B1['precision']:.3f} cat_target={attribution['n_categorial_target']} "
          f"reduced_frac={vd['categorial_reduction_frac']:.3f} recall_cost={vd['B1_transitive_recall_cost_pts']:+.3f} "
          f"A!=B1={ha != hb} wn_ok={_WN_OK}", flush=True)
    print(f"[{ANCHOR_NAME}] categorial target residual: "
          f"{[(t['sid'],t['v'],t['patient'],t['grounded_type']) for t in attribution['categorial_target_residual']]}", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        run_mode("full"); return
    ap.error("specify one of --self-test | --smoke | --full")


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        diag = {
            "anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
            "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
            "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat(),
        }
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
