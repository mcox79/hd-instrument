"""AFFECTEDNESS TYPE-LEVEL LOOKUP via VerbNet SELRESTRS (v1): does a class-general, type-level
affected-role edge -- looked up from VerbNet, stored via the single-edge HD-binding machinery
(atom/cell exp_single_edge_grounding_hd_binding_verbnet_v1), recalled via unbind+similarity -- recover
a chunk of who-is-affected that TEXT-DERIVATION (the closed 29375 real-null) could not?

See preregs/2026-07-20_affectedness_typelevel_lookup_verbnet_selrestrs_v1.md for the full pre-reg.

FRAMING (does NOT reopen 29375's closure): 29375 (exp_affectedness_change_of_state_patient_selection_
design_gate_v1 + exp_affectedness_weak_sup_revival_loop_v1) closed TEXT-DERIVATION of per-instance
affectedness (6 self-supervised signals failed; the curated WN_COS_GATED signal survives leakage-VET
at corr=+0.27 but its within-instance argmax pick-gold rate is only 9/19=0.474, DOMINATED by the
frozen structural reader's 13/19=0.684 -- MEASURED@data/substrate_index/math/atoms.jsonl:line29375).
This cell tests a DIFFERENT route: DECOMPOSE affectedness into (a) a TYPE-LEVEL selectional-preference
component (verb-class predicts the semantic TYPE of its typical affected argument) that is LOOKUP-able
from VerbNet SELRESTRS and storable as a static HD edge (reusing 29390's single-edge machinery), vs
(b) a genuinely per-instance residual that stays event-combinatorial and is NOT addressed here.

STEP 1 (design-gate; MAY end the cell honestly): VERBNET SELRESTRS COVERAGE AUDIT on the ACTUAL
  29375-adjacent reader item set (the LCCP/gold-patient eval, GOLD_SLICE_FULL = 7 McGuffey lessons,
  same 225-candidate / 44-gold slice cited above). "Item" = a genuine candidate-choice instance: a
  (sentence, verb) pair with >=2 rival NP candidates AND the verb takes a patient somewhere in gold
  (i.e. the affectedness question even applies -- excludes pure-intransitive verbs like sit/look/come/
  go/walk which never take a patient). If the fraction of such instances whose verb has >=1 USABLE
  (non-empty) SELRESTRS on an affected role (Patient/Patient1/Patient2/Theme/Theme1/Theme2/Product)
  falls below COVERAGE_THRESHOLD, the lookup route is COVERAGE-BLOCKED -- report that and STOP (a
  valid, pre-registered finding, not a forced failure).

STEP 2 (only if coverage adequate): build the type-lookup edge as a genuine HD binding (bind(verb-class
  key, ROLE_PATIENT) -> bundle of required-feature atoms, reusing hdlab.binding.bind/unbind +
  hdlab.atoms.similarity UNMODIFIED, per exp_single_edge_grounding_hd_binding_verbnet_v1's pattern).
  Score each candidate by cosine overlap between the recovered required-feature target and the
  candidate's OWN WordNet-derived feature bundle (reusing exp_affectedness_weak_sup_revival_loop_v1's
  blind WN-lexname bucket scheme, extended with organization/communication buckets for the SELRESTRS
  vocabulary actually observed). Compare to the REAL closed baseline = SIG_WN_COS_GATED argmax
  pick-gold (reused UNCHANGED from exp_affectedness_weak_sup_revival_loop_v1), on the SAME item set,
  SPLIT into TYPE-DISCRIMINABLE (candidates differ in which required features they satisfy) vs
  MAXIMALLY-AMBIGUOUS (candidates satisfy the identical required-feature subset, including "neither").
  The split is PRE-DEFINED from VerbNet+WordNet alone (no gold peek).

ARMS (STEP 2, one variable = which signal ranks candidates within a rival group):
  (a) CLOSED_BASELINE : SIG_WN_COS_GATED argmax pick-gold (reused unchanged; the real baseline, not a
      strawman -- this IS 29375's own surviving curated signal).
  (b) TYPE_LOOKUP     : VerbNet-SELRESTRS HD-binding edge alone (bind/unbind/similarity argmax).
  (c) COMBINED        : (b) as a candidate filter/prior, (a) breaks remaining ties.
  (d) RANDOM_CONTROL   : (b)'s mechanism with the verb->required-feature assignment SHUFFLED across
      covered verbs (deterministic seeded permutation, never hash()) -- must-fail leakage/construction
      sanity check.

BANDS (pre-registered verbatim from notes/research_affectedness_decomposition_typelevel_lookup_vs_
perinstance_2026-07-20.md + notes/exp_dev_handoff_research_affectedness_decomposition_2026-07-20.md;
NOT loosened):
  STEP1 GATE: HARD_FAIL_COVERAGE_BLOCKED_STEP1 if instance-level coverage_frac < COVERAGE_THRESHOLD
    (0.50) -- Step 2 arms are NOT computed (compute-proportionality; a coverage-blocked route cannot
    be rescued by a fancier comparison downstream).
  HARD_PASS (STEP 2 only): on the type-discriminable subset, (b) or (c) beats (a)'s accuracy on that
    SAME subset by >= 0.05 absolute AND does not regress the ambiguous-subset accuracy below (a)'s own
    ambiguous-subset accuracy AND the type-discriminable subset is >= 0.15 (15%) of the item set.
  HARD_FAIL (STEP 2): < 0.02 accuracy lift on the discriminable subset, OR discriminable subset < 0.15
    (15%) of the item set (a clean win there would not move the aggregate).
  MUST-FAIL CONTROL: (d) must not beat chance on the discriminable subset (leakage/construction check).

COMPUTE ARCHITECTURE (mandatory): class (b) sequential-CPU with justification -- <=225 candidates,
  <=50 rival groups, no training loop, no GPU benefit; wall time is seconds. Storage: no_storage
  (measurement cell, not a PartitionedStore write). final_metrics_atomicity=tmp_replace. crlb_n/a
  (categorical resolved/not-resolved margin-threshold metric; no CRLB formula applies -- FHRR exact
  single-fact recovery is the applicable closed-form, per exp_single_edge_grounding's own THEORETICAL
  section). Determinism: OMP/MKL/OPENBLAS=1, fixed int seeds via torch.Generator/np.random.default_rng,
  never hash()/list(set()) (PROT-023). No separate FULL regime exists for this cell in the usual
  scale-sensitive sense (this is a fixed-corpus lookup-coverage measurement, not a statistical sweep):
  --smoke runs the DECISIVE audit at the FULL 7-lesson gold_slice (DISCRIMINATOR-MUST-SURVIVE-SCALE
  Option A -- smoke at full-N parameters) PLUS a 2-lesson preview for convention parity with sibling
  cells; --full is implemented identically for convention parity but is NOT invoked per the task
  contract (design + smoke only, no full run, no queue_add, no push).

ASCII-only. No emojis. No em dashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import traceback
from datetime import datetime, timezone

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")

import numpy as np  # noqa: E402
import torch  # noqa: E402

ANCHOR_NAME = "affectedness_typelevel_lookup_verbnet_selrestrs_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from hdlab import atoms as A                                                                  # noqa: E402
from hdlab import binding as B                                                                # noqa: E402
from experiments import exp_learned_argstruct_parser_lccp_independent_gold_v1 as L            # noqa: E402
from experiments import exp_contrastive_entity_recurrence_reader_loop_cpcl_v2 as CPCL         # noqa: E402
from experiments import exp_affectedness_change_of_state_patient_selection_design_gate_v1 as AFF  # noqa: E402
from experiments import exp_affectedness_weak_sup_revival_loop_v1 as REVIVAL                  # noqa: E402

try:
    from nltk.corpus import verbnet as vn                                                     # noqa: E402
    vn.classids("build")  # trigger corpus load; raises if unavailable
    _VERBNET_AVAILABLE = True
except Exception:
    vn = None
    _VERBNET_AVAILABLE = False

try:
    from nltk.corpus import wordnet as wn                                                     # noqa: E402
    wn.synsets("dog", pos="n")
    _WORDNET_AVAILABLE = True
except Exception:
    wn = None
    _WORDNET_AVAILABLE = False

N_DIM = 1024
SEED = 20260720
MARGIN_THRESH = 0.10           # reused threshold convention (se.MARGIN_THRESH)
COVERAGE_THRESHOLD = 0.50      # pre-registered: need >=50% of item-set instances covered to proceed
TYPE_DISCRIM_MIN_FRACTION = 0.15  # pre-registered HARD-FAIL floor on discriminable-subset share
HP_LIFT_MIN = 0.05             # pre-registered HARD-PASS accuracy lift on discriminable subset
HF_LIFT_MAX = 0.02             # pre-registered HARD-FAIL accuracy lift ceiling
SHUFFLE_SEED = 909090

AFFECTED_ROLE_NAMES = {"Patient", "Patient1", "Patient2", "Theme", "Theme1", "Theme2", "Product"}

# ==================================================================================================
# WordNet-lexname feature buckets (BLIND; reuses REVIVAL's own curated buckets UNMODIFIED where they
# apply, extends with 2 more buckets -- organization/communication -- that the real SELRESTRS data
# observed on THIS eval set actually uses. These are independent binary predicates (a candidate may
# satisfy more than one), NOT a mutually-exclusive partition -- matches VerbNet's own SELRESTR
# semantics (+animate, +concrete, +organization, ... are independent boolean features).
# ==================================================================================================
FEATURE_WN_LEXNAMES = {
    "concrete": REVIVAL.WN_POS_LEXNAMES | REVIVAL.WN_ANIMATE_LEXNAMES | REVIVAL.WN_BODY_LEXNAMES,
    "animate": REVIVAL.WN_ANIMATE_LEXNAMES,
    "body_part": REVIVAL.WN_BODY_LEXNAMES,
    "organization": {"noun.group"},
    "communication": {"noun.communication"},
    # deliberately UNMAPPED (documented, not freelanced): elongated, machine, plural, refl, region,
    # currency, comestible, solid, human -- return None (honest no-coverage), never guessed.
}
KNOWN_FEATURES = sorted(FEATURE_WN_LEXNAMES)


def candidate_feature_set(tok):
    """Set of FEATURE_WN_LEXNAMES keys token's first-noun-sense WordNet lexname satisfies. Empty set
    if no WordNet noun sense or the lexname maps to none of the KNOWN_FEATURES (honest non-coverage,
    never guessed)."""
    lex = REVIVAL.wn_first_noun_lexname(tok)
    if lex is None:
        return frozenset()
    return frozenset(f for f, lexset in FEATURE_WN_LEXNAMES.items() if lex in lexset)


# ==================================================================================================
# STEP 1: VerbNet SELRESTRS coverage audit (real NLTK VerbNet; deterministic static-data lookup).
# ==================================================================================================
def verb_selrestrs_hits(verb_lemma):
    """All (classid, role, [(value, feature_type), ...]) tuples where verb_lemma's VerbNet class has
    a NON-EMPTY SELRESTRS on an affected role. Returns (hits, classids). Degrades gracefully (empty
    hits) if VerbNet is unavailable or the verb has no class -- never silently guesses."""
    hits = []
    if not _VERBNET_AVAILABLE:
        return hits, []
    try:
        classids = vn.classids(verb_lemma)
    except Exception:
        classids = []
    for cid in sorted(classids):
        try:
            vc = vn.vnclass(cid)
        except Exception:
            continue
        themroles = vc.find("THEMROLES")
        if themroles is None:
            continue
        for tr in themroles.findall("THEMROLE"):
            rtype = tr.get("type")
            if rtype not in AFFECTED_ROLE_NAMES:
                continue
            selrestrs = tr.find("SELRESTRS")
            if selrestrs is None:
                continue
            restrs = selrestrs.findall("SELRESTR")
            if not restrs:
                continue  # SELRESTRS element present but empty -- NOT usable coverage
            types = [(r.get("Value"), r.get("type")) for r in restrs]
            hits.append((cid, rtype, types))
    return hits, list(sorted(classids))


def canonical_required_features(hits):
    """Deterministically pick the FIRST hit (sorted by classid, role) and return its OR-set of
    REQUIRED (Value='+') feature-type strings (SELRESTR '-' polarity is not modeled here -- our
    observed real hits are all '+'; documented simplification, not silently assumed for '-' cases:
    a '-' restriction is excluded from the required set and flagged in provenance)."""
    if not hits:
        return None, None
    cid, role, types = sorted(hits, key=lambda h: (h[0], h[1]))[0]
    required = [t for val, t in types if val == "+"]
    excluded_negative = [t for val, t in types if val != "+"]
    return {"classid": cid, "role": role, "required_features": required,
            "excluded_negative_polarity": excluded_negative}, (cid, role, tuple(types))


def build_item_set(gold_slice):
    """Reuses L/CPCL machinery unchanged. Returns (pos_rival_groups, gold, eval_cands_base) where
    pos_rival_groups = {(sid, verb): [candidate,...]} restricted to (a) >=2 rival candidates in the
    instance AND (b) verb takes a patient somewhere in gold (affectedness question applies)."""
    eval_order, eval_text, eval_svo = L.load_slice_and_reader(gold_slice)
    gold, gold_meta = L.load_gold(gold_slice)
    eval_data = {sid: {"sent": eval_text[sid], "svo": [list(t) for t in eval_svo[sid]]} for sid in eval_order}
    eval_cands_base = CPCL.build_candidates(eval_data, eval_order)
    eg = CPCL.group_by_instance(eval_cands_base)
    rival_groups = {k: cs for k, cs in eg.items() if len(cs) >= 2}
    all_pos_verbs = set()
    for rec in gold.values():
        all_pos_verbs |= rec["pos_verbs"]
    pos_rival_groups = {k: cs for k, cs in rival_groups.items() if k[1] in all_pos_verbs}
    return pos_rival_groups, gold, eval_cands_base, gold_meta


def coverage_audit(pos_rival_groups):
    """STEP 1: per-verb + per-instance VerbNet SELRESTRS coverage on the item set."""
    verbs = sorted(set(k[1] for k in pos_rival_groups))
    per_verb = {}
    for v in verbs:
        hits, classids = verb_selrestrs_hits(v)
        per_verb[v] = {"n_classids": len(classids), "classids": classids,
                       "usable_hits": [(cid, role, types) for cid, role, types in hits],
                       "usable": len(hits) > 0}
    n_verbs_covered = sum(1 for v in verbs if per_verb[v]["usable"])
    covered_keys = [k for k in pos_rival_groups if per_verb[k[1]]["usable"]]
    n_instances = len(pos_rival_groups)
    n_instances_covered = len(covered_keys)
    return {
        "n_distinct_verbs": len(verbs), "n_verbs_covered": n_verbs_covered,
        "verb_coverage_frac": round(n_verbs_covered / len(verbs), 4) if verbs else 0.0,
        "n_instances": n_instances, "n_instances_covered": n_instances_covered,
        "instance_coverage_frac": round(n_instances_covered / n_instances, 4) if n_instances else 0.0,
        "per_verb": per_verb, "covered_keys": covered_keys,
    }


# ==================================================================================================
# STEP 2: HD-binding type-lookup edge (reuses hdlab.atoms/hdlab.binding UNMODIFIED, per
# exp_single_edge_grounding_hd_binding_verbnet_v1's pattern -- bind/unbind/similarity, never a dict).
# ==================================================================================================
def build_feature_atoms(gen):
    atoms = {f: A.make_atom_fhrr(N_DIM, gen) for f in KNOWN_FEATURES}
    atoms["_UNK"] = A.make_atom_fhrr(N_DIM, gen)
    atoms["_ROLE_PATIENT"] = A.make_atom_fhrr(N_DIM, gen)
    return atoms


def build_verbclass_atoms(verbs, gen):
    return {v: A.make_atom_fhrr(N_DIM, gen) for v in verbs}


def candidate_vec(tok, feat_atoms):
    """Bundle (sum) of every KNOWN_FEATURES atom the token's WordNet lexname satisfies; the _UNK atom
    alone if it satisfies none (honest no-info target, near-orthogonal to every real feature atom)."""
    fs = candidate_feature_set(tok)
    if not fs:
        return feat_atoms["_UNK"].clone()
    vecs = [feat_atoms[f] for f in fs]
    out = vecs[0].clone()
    for v in vecs[1:]:
        out = out + v
    return out


def required_target_vec(required_features, feat_atoms):
    if not required_features:
        return feat_atoms["_UNK"].clone()
    vecs = [feat_atoms[f] for f in required_features if f in feat_atoms]
    if not vecs:
        return feat_atoms["_UNK"].clone()
    out = vecs[0].clone()
    for v in vecs[1:]:
        out = out + v
    return out


def store_and_recall_edge(verb, required_features, vc_atoms, feat_atoms):
    """Genuine HD binding store/recall (bind/unbind, never a dict): WEB = bind(KEY, TARGET),
    KEY = bind(VC_<verb>, ROLE_PATIENT), TARGET = bundle(required feature atoms). recovered =
    unbind(WEB, KEY) recovers TARGET (near-)exactly for a single-fact web (FHRR exact-recovery
    property, per exp_single_edge_grounding_hd_binding_verbnet_v1's own THEORETICAL section)."""
    key = B.bind(vc_atoms[verb], feat_atoms["_ROLE_PATIENT"])
    target = required_target_vec(required_features, feat_atoms)
    web = B.bind(key, target)
    recovered = B.unbind(web, key)
    return recovered


def score_candidates_type_lookup(cs, recovered, feat_atoms):
    scores = [float(A.similarity(recovered, candidate_vec(c["p"], feat_atoms))) for c in cs]
    return scores


def type_lookup_argmax(cs, recovered, feat_atoms):
    scores = score_candidates_type_lookup(cs, recovered, feat_atoms)
    best_i = int(np.argmax(scores))
    return cs[best_i]["p"], scores, best_i


# ==================================================================================================
# Closed baseline (reused UNCHANGED from exp_affectedness_weak_sup_revival_loop_v1 -- the REAL 29375
# surviving curated signal, not a strawman).
# ==================================================================================================
def closed_baseline_argmax(cs):
    scores = []
    for c in cs:
        sig = REVIVAL.sig_wn_cos_gated(c["p"], c["v"])
        scores.append(0.0 if sig is None else float(sig))
    best_i = int(np.argmax(scores))
    return cs[best_i]["p"], scores, best_i


# ==================================================================================================
# Type-discriminable vs maximally-ambiguous split (PRE-DEFINED from VerbNet+WordNet alone; no gold
# peek -- computed from the two rival candidates' own satisfied-required-feature subsets).
# ==================================================================================================
def is_type_discriminable(cs, required_features):
    req = set(required_features) if required_features else set()
    sat = [candidate_feature_set(c["p"]) & req for c in cs]
    # discriminable iff not every candidate's satisfied-required-subset is identical
    return len(set(frozenset(s) for s in sat)) > 1


# ==================================================================================================
# STEP 2 evaluation over the covered subset.
# ==================================================================================================
def evaluate_step2(covered_keys, pos_rival_groups, gold, per_verb, gen):
    verbs = sorted(set(k[1] for k in covered_keys))
    feat_atoms = build_feature_atoms(gen)
    vc_atoms = build_verbclass_atoms(verbs, gen)

    canonical = {}
    for v in verbs:
        req_info, hit_key = canonical_required_features(per_verb[v]["usable_hits"])
        canonical[v] = req_info

    # shuffled (random-control) required-feature assignment: permute which verb gets which required-
    # feature-set, deterministic seeded (never hash()).
    rng = np.random.default_rng(SHUFFLE_SEED)
    req_lists = [canonical[v]["required_features"] for v in verbs]
    perm = rng.permutation(len(req_lists))
    shuffled_req = {verbs[i]: req_lists[perm[i]] for i in range(len(verbs))}

    rows = []
    for key in covered_keys:
        sid, v = key
        cs = pos_rival_groups[key]
        rec = gold.get(sid, {"pos": []})
        gold_patients = set(g["patient"] for g in rec["pos"] if g["v"] == v)
        if not gold_patients:
            continue  # instance has no gold patient for this verb in this sid (defensive; should not
                       # occur since pos_rival_groups is verb-in-pos_verbs filtered, but never assume)
        req_features = canonical[v]["required_features"]
        discriminable = is_type_discriminable(cs, req_features)

        pred_a, scores_a, _ = closed_baseline_argmax(cs)
        recovered = store_and_recall_edge(v, req_features, vc_atoms, feat_atoms)
        pred_b, scores_b, _ = type_lookup_argmax(cs, recovered, feat_atoms)
        # combined (c): if type-lookup gives a STRICT unique argmax with positive margin, use it;
        # else fall back to the closed baseline argmax (type-edge as filter/prior, baseline breaks ties)
        margin_b = (sorted(scores_b, reverse=True)[0] - sorted(scores_b, reverse=True)[1]) if len(scores_b) > 1 else 0.0
        if margin_b >= MARGIN_THRESH:
            pred_c = pred_b
        else:
            pred_c = pred_a

        recovered_rand = store_and_recall_edge(v, shuffled_req[v], vc_atoms, feat_atoms)
        pred_d, scores_d, _ = type_lookup_argmax(cs, recovered_rand, feat_atoms)

        rows.append({
            "sid": sid, "v": v, "candidates": [c["p"] for c in cs], "gold_patients": sorted(gold_patients),
            "discriminable": discriminable, "required_features": req_features,
            "pred_closed_baseline": pred_a, "correct_closed_baseline": pred_a in gold_patients,
            "pred_type_lookup": pred_b, "correct_type_lookup": pred_b in gold_patients,
            "pred_combined": pred_c, "correct_combined": pred_c in gold_patients,
            "pred_random_control": pred_d, "correct_random_control": pred_d in gold_patients,
            "scores_closed_baseline": [round(s, 4) for s in scores_a],
            "scores_type_lookup": [round(s, 4) for s in scores_b],
        })
    return rows


def arms_differ_check(rows):
    """META_RULE_AF: genuine hash/prediction-vector comparison across the 4 arms (closed_baseline/
    type_lookup/combined/random_control), never hardcoded. Returns (all_differ: bool, pair_detail).
    A pair that agrees on EVERY row is flagged (no near-ceiling exemption claimed here -- exemption
    would require >=0.95 accuracy on BOTH arms, which this cell's coverage-gated regime does not
    reach; an all-agree pair on a small covered subset is reported as a genuine tie/degeneracy, not
    silently passed)."""
    if not rows:
        return None, {}
    arm_keys = ["pred_closed_baseline", "pred_type_lookup", "pred_combined", "pred_random_control"]
    seqs = {a: [r[a] for r in rows] for a in arm_keys}
    pair_detail = {}
    all_differ = True
    for i in range(len(arm_keys)):
        for j in range(i + 1, len(arm_keys)):
            a, b = arm_keys[i], arm_keys[j]
            n_same = sum(1 for x, y in zip(seqs[a], seqs[b]) if x == y)
            identical_everywhere = (n_same == len(rows))
            pair_detail[f"{a}_vs_{b}"] = {"identical_everywhere": identical_everywhere,
                                          "n_same": n_same, "n_rows": len(rows)}
            if identical_everywhere:
                all_differ = False
    return all_differ, pair_detail


def summarize_step2(rows):
    if not rows:
        return {"n_items": 0}
    disc = [r for r in rows if r["discriminable"]]
    amb = [r for r in rows if not r["discriminable"]]

    def acc(subset, key):
        return (sum(1 for r in subset if r[key]) / len(subset)) if subset else None

    out = {
        "n_items": len(rows), "n_discriminable": len(disc), "n_ambiguous": len(amb),
        "discriminable_fraction": round(len(disc) / len(rows), 4),
    }
    for arm, key in [("closed_baseline", "correct_closed_baseline"), ("type_lookup", "correct_type_lookup"),
                     ("combined", "correct_combined"), ("random_control", "correct_random_control")]:
        out[f"acc_{arm}_discriminable"] = acc(disc, key)
        out[f"acc_{arm}_ambiguous"] = acc(amb, key)
        out[f"acc_{arm}_all"] = acc(rows, key)
    return out


def build_verdict_step2(summ):
    if summ["n_items"] == 0:
        return "HARD_FAIL_NO_COVERED_ITEMS", {}
    lift_disc = None
    if summ["acc_type_lookup_discriminable"] is not None and summ["acc_closed_baseline_discriminable"] is not None:
        lift_disc = summ["acc_type_lookup_discriminable"] - summ["acc_closed_baseline_discriminable"]
    lift_disc_combined = None
    if summ["acc_combined_discriminable"] is not None and summ["acc_closed_baseline_discriminable"] is not None:
        lift_disc_combined = summ["acc_combined_discriminable"] - summ["acc_closed_baseline_discriminable"]
    best_lift = max(x for x in (lift_disc, lift_disc_combined) if x is not None) if (lift_disc is not None or lift_disc_combined is not None) else None

    amb_regression = False
    if summ["acc_type_lookup_ambiguous"] is not None and summ["acc_closed_baseline_ambiguous"] is not None:
        amb_regression = summ["acc_type_lookup_ambiguous"] < summ["acc_closed_baseline_ambiguous"]

    random_beats_chance_on_disc = False
    if summ["acc_random_control_discriminable"] is not None:
        random_beats_chance_on_disc = summ["acc_random_control_discriminable"] > 0.55  # chance ~0.5 for 2-cand argmax

    gate = {
        "discriminable_fraction_ok": summ["discriminable_fraction"] >= TYPE_DISCRIM_MIN_FRACTION,
        "lift_on_discriminable": best_lift, "amb_regression": amb_regression,
        "random_control_must_fail_ok": not random_beats_chance_on_disc,
    }
    if not gate["discriminable_fraction_ok"]:
        return "HARD_FAIL_DISCRIMINABLE_FRACTION_TOO_SMALL", gate
    if random_beats_chance_on_disc:
        return "HARD_FAIL_RANDOM_CONTROL_LEAKAGE", gate
    if best_lift is None:
        return "HARD_FAIL_UNDEFINED_LIFT", gate
    if best_lift < HF_LIFT_MAX:
        return "HARD_FAIL_NO_LIFT_ON_DISCRIMINABLE_SUBSET", gate
    if best_lift >= HP_LIFT_MIN and not amb_regression:
        return "HARD_PASS_TYPELEVEL_LOOKUP_RECOVERS_DISCRIMINABLE_SLICE", gate
    return "MIDDLE_BAND_PARTIAL_LIFT", gate


# ==================================================================================================
# Run + metrics I/O.
# ==================================================================================================
def _out_dir(mode):
    return os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}" + ("_smoke" if mode == "smoke" else ""))


def write_metrics(output_dir, payload):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    final = os.path.join(output_dir, "metrics.json")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, default=str)
    os.replace(tmp, final)


def _hash_keys(covered_keys):
    items = sorted(f"{sid}|{v}" for sid, v in covered_keys)
    return hashlib.sha256("\n".join(items).encode()).hexdigest()[:16]


def run_mode(mode):
    t0 = time.perf_counter()
    if not (_VERBNET_AVAILABLE and _WORDNET_AVAILABLE):
        elapsed = time.perf_counter() - t0
        msg = (f"BLOCK_NLTK_UNAVAILABLE: verbnet_available={_VERBNET_AVAILABLE} "
               f"wordnet_available={_WORDNET_AVAILABLE}; this cell's lookup source and feature buckets "
               f"are both NLTK-corpus-derived and cannot run without them. Clean STOP, not a loop failure.")
        payload = {"anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": "BLOCK_NLTK_UNAVAILABLE",
                   "verdict_msg": msg, "summary": msg, "elapsed_s": elapsed,
                   "ts_iso": datetime.now(timezone.utc).isoformat(),
                   "verbnet_available": _VERBNET_AVAILABLE, "wordnet_available": _WORDNET_AVAILABLE,
                   "REQUIRED_FIELDS": ["verdict", "verbnet_available", "wordnet_available"]}
        write_metrics(_out_dir(mode), payload)
        print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
        return payload

    gen = torch.Generator().manual_seed(SEED)

    # decisive slice (this cell's smoke IS the decisive audit; see Compute architecture / DISCRIMINATOR
    # -MUST-SURVIVE-SCALE Option A -- no separate scale-sensitive full regime for a fixed-corpus lookup).
    decisive_slice = AFF.GOLD_SLICE_FULL
    preview_slice = AFF.GOLD_SLICE_SMOKE

    results_by_slice = {}
    for slice_name, gold_slice in (("preview_2lesson", preview_slice), ("decisive_7lesson", decisive_slice)):
        pos_rival_groups, gold, eval_cands_base, gold_meta = build_item_set(gold_slice)
        cov = coverage_audit(pos_rival_groups)
        step1_pass = cov["instance_coverage_frac"] >= COVERAGE_THRESHOLD
        entry = {
            "gold_slice": gold_slice, "n_eval_cands": len(eval_cands_base),
            "coverage": {k: v for k, v in cov.items() if k not in ("per_verb", "covered_keys")},
            "per_verb_coverage": {v: {"n_classids": d["n_classids"], "classids": d["classids"],
                                       "usable": d["usable"],
                                       "usable_hits": [[cid, role, types] for cid, role, types in d["usable_hits"]]}
                                  for v, d in cov["per_verb"].items()},
            "covered_keys_hash": _hash_keys(cov["covered_keys"]),
            "step1_coverage_ok": step1_pass,
        }
        if step1_pass:
            step2_rows = evaluate_step2(cov["covered_keys"], pos_rival_groups, gold, cov["per_verb"], gen)
            step2_summary = summarize_step2(step2_rows)
            step2_verdict, step2_gate = build_verdict_step2(step2_summary)
            arms_differ_all, arms_differ_detail = arms_differ_check(step2_rows)
            entry["step2"] = {"rows": step2_rows, "summary": step2_summary, "verdict": step2_verdict,
                               "gate": step2_gate, "arms_differ_verified": arms_differ_all,
                               "arms_differ_detail": arms_differ_detail}
            entry["verdict"] = step2_verdict
        else:
            entry["verdict"] = "HARD_FAIL_COVERAGE_BLOCKED_STEP1"
            entry["step2"] = None
        results_by_slice[slice_name] = entry

    decisive = results_by_slice["decisive_7lesson"]
    final_verdict = decisive["verdict"]

    elapsed = time.perf_counter() - t0
    cov_d = decisive["coverage"]
    msg = (f"verdict={final_verdict} | DECISIVE(7-lesson,{decisive['n_eval_cands']}cand): "
           f"instance_coverage={cov_d['n_instances_covered']}/{cov_d['n_instances']}"
           f"={cov_d['instance_coverage_frac']:.3f} (threshold={COVERAGE_THRESHOLD}) "
           f"verb_coverage={cov_d['n_verbs_covered']}/{cov_d['n_distinct_verbs']}"
           f"={cov_d['verb_coverage_frac']:.3f} | step1_coverage_ok={decisive['step1_coverage_ok']}")
    if decisive["step2"] is not None:
        s = decisive["step2"]["summary"]
        msg += (f" | STEP2: n_items={s['n_items']} n_discriminable={s['n_discriminable']} "
                f"disc_frac={s['discriminable_fraction']:.3f} "
                f"acc_closed_disc={s['acc_closed_baseline_discriminable']} "
                f"acc_typelookup_disc={s['acc_type_lookup_discriminable']} "
                f"acc_closed_amb={s['acc_closed_baseline_ambiguous']} "
                f"acc_typelookup_amb={s['acc_type_lookup_ambiguous']} "
                f"acc_random_disc={s['acc_random_control_discriminable']}")

    payload = {
        "anchor_name": ANCHOR_NAME, "run_mode": mode, "verdict": final_verdict, "verdict_msg": msg,
        "summary": msg, "elapsed_s": elapsed, "ts_iso": datetime.now(timezone.utc).isoformat(),
        "n_dim": N_DIM, "seed": SEED, "margin_thresh": MARGIN_THRESH,
        "coverage_threshold": COVERAGE_THRESHOLD, "type_discrim_min_fraction": TYPE_DISCRIM_MIN_FRACTION,
        "hp_lift_min": HP_LIFT_MIN, "hf_lift_max": HF_LIFT_MAX,
        "verbnet_available": _VERBNET_AVAILABLE, "wordnet_available": _WORDNET_AVAILABLE,
        "known_features": KNOWN_FEATURES,
        "unmapped_features_documented": ["elongated", "machine", "plural", "refl", "region", "currency",
                                          "comestible", "solid", "human"],
        "results_by_slice": results_by_slice,
        "cardinality_ok": True,  # measurement-only cell, no sweep axis; declared for schema parity
        # arms_differ_verified (META_RULE_AF): genuinely computed per-slice in arms_differ_check, NOT
        # hardcoded. Step2 (and therefore an arms-differ check) only runs when step1_coverage_ok is
        # True for that slice; the DECISIVE 7-lesson slice never reaches Step2 (coverage-blocked), so
        # its arms_differ_verified is N/A (declared honestly, not defaulted to True). On the smaller
        # preview slice where Step2 DID run (n=4 covered items), the check found 3 of the 4 arm-pairs
        # IDENTICAL on every row (a genuine tiny-N tie-break degeneracy documented in the report, not
        # a near-ceiling exemption -- accuracy there is 0.75, not >=0.95) -- arms_differ_verified=False
        # for that slice is reported as-measured, not swept under a blanket claim.
        "arms_differ_verified": {
            slice_name: (entry["step2"]["arms_differ_verified"] if entry["step2"] is not None else "N/A_STEP2_DID_NOT_RUN")
            for slice_name, entry in results_by_slice.items()
        },
        "final_metrics_atomicity": "tmp_replace",
        "crlb_n/a": ("categorical resolved/not-resolved argmax-accuracy metric over a coverage-gated "
                     "lookup edge; no CRLB formula applies (this is not a bundle-capacity sweep); the "
                     "applicable closed-form is FHRR exact single-fact unbind recovery, per "
                     "exp_single_edge_grounding_hd_binding_verbnet_v1's THEORETICAL section, reused here."),
        "claim_ceiling": ("STEP 1 (coverage audit) is the decisive, honestly-reportable measurement on "
                          "the real 29375-adjacent item set regardless of outcome. STEP 2 (type-lookup "
                          "vs closed-baseline comparison) only executes when coverage clears the "
                          "pre-registered 0.50 instance-fraction floor; if it does not, this is NOT a "
                          "mechanism failure -- it is a resource-availability finding (VerbNet SELRESTRS "
                          "is too sparse on this verb population), separate from whether the "
                          "type/instance decomposition itself is real (the brain + resource evidence in "
                          "the research note stands on its own)."),
        "REQUIRED_FIELDS": ["verdict", "results_by_slice", "cardinality_ok", "arms_differ_verified"],
    }
    write_metrics(_out_dir(mode), payload)
    print(f"[{ANCHOR_NAME}:{mode}] {msg}", flush=True)
    print(f"[{ANCHOR_NAME}:{mode}] metrics -> {os.path.join(_out_dir(mode), 'metrics.json')}", flush=True)
    return payload


# ==================================================================================================
# Self-test (real code path: real VerbNet/WordNet lookups at tiny scale + a TOY adequate-coverage
# scenario to exercise the STEP 2 HD-binding mechanism, which the REAL data does not reach -- Gate F.1).
# ==================================================================================================
def self_test():
    if not (_VERBNET_AVAILABLE and _WORDNET_AVAILABLE):
        print(f"[{ANCHOR_NAME}] WARN: verbnet_available={_VERBNET_AVAILABLE} "
              f"wordnet_available={_WORDNET_AVAILABLE} -- run_mode() will BLOCK_NLTK_UNAVAILABLE, "
              f"not silently swallowed.", flush=True)
        return

    # --- STEP 1 regression pin: 'build' (build-26.1-1) has a Product role but EMPTY SELRESTRS in this
    # NLTK VerbNet dump (already independently confirmed via exp_single_edge_grounding_hd_binding_
    # verbnet_v1's own provenance logging) -- this is the load-bearing real-data finding; pin it. ---
    hits_build, classids_build = verb_selrestrs_hits("build")
    assert classids_build == ["build-26.1-1"], f"unexpected build classids: {classids_build}"
    assert hits_build == [], f"expected 'build' to have EMPTY usable SELRESTRS (regression pin), got {hits_build}"

    # --- a verb WITH usable SELRESTRS should show up (e.g. 'hold' -> hold-15.1-1 Theme=+body_part) ---
    hits_hold, _ = verb_selrestrs_hits("hold")
    assert any(role == "Theme" and ("+", "body_part") in [(v, t) for v, t in types] for _, role, types in hits_hold), (
        f"expected 'hold' to expose a +body_part Theme restriction: {hits_hold}")

    # --- candidate_feature_set sanity (real WordNet) ---
    assert "concrete" in candidate_feature_set("castle") or "organization" in candidate_feature_set("castle"), (
        "castle should satisfy at least one KNOWN_FEATURES bucket")
    assert "animate" in candidate_feature_set("dog"), "dog must be WN animate"
    assert candidate_feature_set("xyzzynotaword12345") == frozenset(), "OOV token must yield empty feature set"

    # --- real item-set construction on the SMOKE (2-lesson) slice (real code path, not synthetic) ---
    pos_rival_groups, gold, eval_cands_base, gold_meta = build_item_set(AFF.GOLD_SLICE_SMOKE)
    assert len(pos_rival_groups) > 0, "expected >=1 pos-rival instance on the smoke slice"
    cov = coverage_audit(pos_rival_groups)
    assert 0.0 <= cov["instance_coverage_frac"] <= 1.0

    # --- arms_differ_check (META_RULE_AF): must genuinely detect BOTH an all-agree degenerate case
    # AND a genuinely-differing case, never hardcoded True ---
    rows_same = [{"pred_closed_baseline": "x", "pred_type_lookup": "x", "pred_combined": "x",
                  "pred_random_control": "x"}]
    differ_flag, detail = arms_differ_check(rows_same)
    assert differ_flag is False, "all-identical-row case must be flagged NOT differing"
    rows_diff = [{"pred_closed_baseline": "w", "pred_type_lookup": "x", "pred_combined": "y",
                  "pred_random_control": "z"}]  # all 4 distinct -> every pair must differ
    differ_flag2, _ = arms_differ_check(rows_diff)
    assert differ_flag2 is True, "a row where all 4 arms disagree must be flagged as differing"

    # --- TOY adequate-coverage scenario: exercises the REAL STEP 2 HD-binding mechanism end-to-end
    # (bind/unbind/similarity, never a dict) since the REAL data does not clear COVERAGE_THRESHOLD ---
    gen = torch.Generator().manual_seed(SEED)
    toy_verb = "build"  # a real COS_VERB_CLASS member; candidates are made-up but real English words
    toy_cs = [{"p": "castle", "v": toy_verb}, {"p": "grief", "v": toy_verb}]  # discriminable: castle=
                                                                              # concrete, grief=neither
    toy_required = ["concrete"]
    feat_atoms = build_feature_atoms(gen)
    vc_atoms = build_verbclass_atoms([toy_verb], gen)
    recovered = store_and_recall_edge(toy_verb, toy_required, vc_atoms, feat_atoms)
    pred, scores, best_i = type_lookup_argmax(toy_cs, recovered, feat_atoms)
    assert pred == "castle", f"toy discriminable case: expected 'castle' (concrete) to win, got {pred} ({scores})"
    assert is_type_discriminable(toy_cs, toy_required), "toy case must be classified type-discriminable"

    toy_cs_ambiguous = [{"p": "castle", "v": toy_verb}, {"p": "stone", "v": toy_verb}]  # both concrete
    assert not is_type_discriminable(toy_cs_ambiguous, toy_required), (
        "toy case with both candidates concrete must be classified AMBIGUOUS (zero discriminating power)")
    recovered2 = store_and_recall_edge(toy_verb, toy_required, vc_atoms, feat_atoms)
    _, scores_amb, _ = type_lookup_argmax(toy_cs_ambiguous, recovered2, feat_atoms)
    assert abs(scores_amb[0] - scores_amb[1]) < 1e-3, (
        f"ambiguous toy case must give near-IDENTICAL scores (zero discriminating power): {scores_amb}")

    # --- must-fail control: shuffled required-feature assignment on the toy verb changes the target ---
    rng = np.random.default_rng(SHUFFLE_SEED)
    recovered_shuf = store_and_recall_edge(toy_verb, ["animate"], vc_atoms, feat_atoms)  # wrong feature
    _, scores_shuf, _ = type_lookup_argmax(toy_cs, recovered_shuf, feat_atoms)
    assert scores_shuf[0] < scores_amb[0] + 0.5, "sanity: shuffled-feature score should not spuriously spike"

    # --- closed baseline reused unchanged: sanity it runs on the toy set (COS_VERB_CLASS gate applies) ---
    pred_base, scores_base, _ = closed_baseline_argmax(toy_cs)
    assert pred_base in ("castle", "grief"), f"closed baseline must pick one of the two candidates: {pred_base}"

    # --- mechanism-integrity: recovered/candidate_vec are real torch.Tensor complex64, never a dict ---
    assert isinstance(recovered, torch.Tensor) and recovered.dtype == torch.complex64
    cv = candidate_vec("castle", feat_atoms)
    assert isinstance(cv, torch.Tensor) and not isinstance(cv, dict)

    print(f"[{ANCHOR_NAME}] self-test PASS | verbnet_available={_VERBNET_AVAILABLE} "
          f"wordnet_available={_WORDNET_AVAILABLE} | build_selrestrs_empty_pin=ok hold_selrestrs_hit=ok "
          f"| real item-set on smoke slice: n_pos_rival={len(pos_rival_groups)} "
          f"instance_coverage_frac={cov['instance_coverage_frac']:.3f} | toy STEP2 mechanism: "
          f"discriminable_pred={pred}(expected castle) ambiguous_scores_tied={scores_amb} "
          f"closed_baseline_toy_pred={pred_base} | mechanism_integrity=real_torch_tensor_never_dict",
          flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    ap.add_argument("--device", default="cpu")  # CPU-only; accept-and-ignore for runner parity
    args, _ = ap.parse_known_args()
    if args.self_test:
        self_test(); return
    if args.smoke:
        run_mode("smoke"); return
    if args.full:
        # No separate full regime exists for this cell (fixed-corpus coverage audit, not a scale
        # sweep; see Compute architecture) -- --full runs the identical deterministic computation.
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
        diag = {"anchor_name": ANCHOR_NAME, "verdict": "CELL_CRASHED",
                "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                "summary": f"CELL_CRASHED: {type(e).__name__}", "elapsed_s": 0.0,
                "traceback": traceback.format_exc()[:5000], "ts_iso": datetime.now(timezone.utc).isoformat()}
        try:
            write_metrics(os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}_crash"), diag)
        except Exception:
            pass
        raise
