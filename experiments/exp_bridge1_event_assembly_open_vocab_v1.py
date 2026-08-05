# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: hash digests of GOVERNOR_ONLY vs TWO_STAGE_REAL vs TWO_STAGE_CLOSED vs BOW
#   vs SCRAMBLED_EVENT_REAL prediction-sequences on subset Bopen (must not be all-identical;
#   TWO_STAGE_REAL vs GOVERNOR_ONLY must literally differ by construction -- that IS the discriminator).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity dimension; sign-accuracy discriminator only
# - baseline_in_band: n/a; governor-only baseline on Bopen/Bgap is 0.500 by construction (governor
#   sees the same UNK class for both members of every pair -- matches original v2's confirmed pattern)
# - discriminator survives scale: full-N == smoke-N item sets; only theta-training steps differ
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands pre-registered below, set BEFORE running)
# - deterministic_seeding: torch.Generator + random.Random per seed; hashlib not builtin hash()
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py)
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""BRIDGE-1 event-assembly REAL-ORGAN / OPEN-VOCABULARY test.

v2 (experiments/exp_bridge1_twostage_event_situation_v2.py, commit b226cfad6) proved the TWO-STAGE
SHAPE recovers subset B (governor-matched, event-differing pairs) using a CLOSED hand-authored
object->event-class whitelist (GOAL_OBJECT_WHITELIST / ADVERSARIAL_WHITELIST /
ANIMATE_HARMABLE_WHITELIST, v2 L131-149) standing in for the real Component-3 patient-extraction +
animacy-classification organs. That is a construction-bounded shape proof, not yet a measured
capability: does the REAL organ recover B on OPEN vocabulary the whitelist never saw?

THIS CELL replaces the object-identity axis of v2's Stage-2a with the real organs:
  - patient/object EXTRACTION: v2's own structural gate, reused unmodified (bridge1.nearest_verb_idx
    + v2.valid_direct_object -- a governing verb must exist and no ADP token may sit between it and
    the target, i.e. the target is the verb's direct object, not inside/after a PP). This IS
    Component-3's minimal argument-identification step for a simple transitive clause; no change
    needed here, it was already real (never part of the closed lexicon).
  - patient CATEGORY: hdlab.animacy_lexicon.lookup_animacy (WordNet first-noun-sense hypernym-
    closure lookup, glass-box symbolic dictionary, not a hand-authored per-item category map) drives
    the event-class decision. Object identity is no longer read off a bespoke whitelist; it is
    CLASSIFIED by a general-purpose lexicon that has never seen these specific words.

MECHANISM (mirrors v2's own event_type_for_item exactly, animacy substituted for the whitelist
lookup -- see event_type_for_item_real below):
  - patient animate (person/animal per WordNet) AND governing verb is UNK to bridge1's own narrow
    governor-class dict AND that verb is independently known force-capable (FORCE_CLASS_HARM_REAL,
    a VERB-side lexicon, unchanged axis, not what is under test here) -> BLOCK_HIGH. This is the
    "broke her arm" pattern: the governor stage has no opinion (UNK verb), patient affectedness
    (animate = can-be-harmed) supplies the missing signal.
  - patient inanimate/abstract (object/abstract per WordNet) -> NEUTRAL, UNCONDITIONALLY (matches
    v2's own GOAL_OBJECT semantics: "beat the game" is not harm regardless of the governor's own
    class, because the patient cannot BE harmed in the relevant sense).
  - anywhere neither condition fires (uncovered word, or animate patient with a governor-known
    verb where the governor's own class already applies) -> ABSTAIN (None), governor dominance-
    default is used unmodified, exactly like v2.

HONEST SCOPE NARROWING vs v2 (reported, not hidden): v2's whitelist ALSO had an ADVERSARIAL branch
(enemy/rival/thief -> BLOCK_HIGH regardless of governor class, overriding a HELP-class governor like
"aided"/"comforted"). That branch encodes SOCIAL-RELATIONAL valence (adversary vs sympathetic
person), not affectedness/animacy -- WordNet has no such axis (an enemy and a refugee are both
`person`, animate). The real-organ path here therefore does NOT replace ADVERSARIAL; those two of
v2's six original subset-B pairs (aided/comforted enemy-vs-refugee/widow) are structurally
un-recoverable by an animacy-only organ and are reported as a SEPARATE missing-component finding
(route: a relational-valence/social-appraisal lexicon, out of scope for this cell), not folded into
the open-vocab pass/fail gate below. The pre-registered discriminator (subset Bopen) is built to be
100% animacy-decidable by design (no adversarial-type pairs), consistent with the WHY pointer's own
framing of the event-class signal ("ANIMATE-HARMABLE patient vs INANIMATE/ABSTRACT-GOAL object ->
animacy + affectedness is the real signal").

SCOPE OF APPLICATION (glass-box, documented, mirrors v2's own scoping discipline): the real-organ
animacy classifier is invoked over the vocabulary of the pools actually under test here (B, Bgen,
Bopen, Bgap) -- built once into REAL_ANIMACY_MAP via build_real_animacy_map(). Subset A (bridge1's
own collision+unseen regression set) is asserted DISJOINT from this vocabulary (self_test check
`_subset_A_disjoint_from_real_animacy_vocab`), so subset A's own items are structurally unreachable
by this stage and its accuracy is UNCHANGED, exactly like v2's own OBJECT_EVENT_CLASS scoping
(v2 self_test's `risky_words.isdisjoint(...)` check, same discipline, real organ instead of a
per-word hand list). This is a scope-of-WHICH-ITEMS-get-evaluated decision, not a whitelist of
per-word categories -- the category itself (animate/inanimate) is a live WordNet lookup for
whatever word appears in-scope, not a hardcoded map. A universal apply-to-everything design was
tried and rejected during authoring: WordNet classifies abstract HARM nouns (insult/curse/threat/
penalty, already present in subset A) as `abstract` (inanimate) exactly like achievement nominals
(game/record/puzzle) -- animacy alone cannot tell "an abstract noun that already carries its own
harm valence" apart from "an abstract task-noun a harm-verb cannot literally act on"; applying the
inanimate->NEUTRAL override to subset A's vocabulary would have silently regressed it (insult would
flip from correctly-HARM to wrongly-NEUTRAL). Scoping to the tested pools avoids this without
hand-coding per-word categories within those pools.

KNOWN WORDNET GAP, quantified honestly (subset Bgap below): WordNet routes body-part nouns through
BODY-PART hypernyms, not person/animal senses, so `lookup_animacy("arm"/"ankle"/"elbow"/...)`
returns "inanimate"/"object" -- a documented false negative (see hdlab/animacy_lexicon.py module
docstring). v2 patched this for its OWN six body-part words (arm/hand/leg/face/head/neck/back/
shoulder/wrist) via BODY_PART_SUPPLEMENT (kept here, unchanged, small, documented). That supplement
is explicitly NOT extended to cover this cell's open-vocab gap-quantification words (ankle/elbow/
knee) -- covering the test items would defeat the point of measuring the gap. Bgap therefore
measures the RAW organ's miss rate on a genuinely uncovered body-part slice.

Pools A/B/Bgen reused unmodified from v2 (commit b226cfad6) for direct comparability; NEW pools
Bopen (primary discriminator, disjoint-vocabulary animate-vs-inanimate pairs, never seen by any
whitelist/supplement) and Bgap (body-part-gap quantification, disjoint from BODY_PART_SUPPLEMENT).
Subset C / the situation-bias port are OUT OF SCOPE for this cell (not touched, not re-evaluated).
"""

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import traceback
from datetime import datetime, timezone

import torch

ANCHOR_NAME = "bridge1_event_assembly_open_vocab_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab.thematic_role_labeler import train_perceptron  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402 (REAL ORGAN: patient category)
import experiments.exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402 (REUSE: frozen sim)
import experiments.exp_bridge1_governor_grounding_v1 as bridge1  # noqa: E402 (STAGE-1, unmodified)
import experiments.exp_bridge1_confirmation_test_v1 as conf  # noqa: E402 (REUSE: subsets A/B, gold_sign)
import experiments.exp_bridge1_twostage_event_situation_v2 as v2  # noqa: E402 (REUSE: harness, closed-lexicon reference arm)

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
FULL_N_TRAIN_THETA = 8000
SMOKE_N_TRAIN_THETA = 4000

# ------------------------------------------------------------------------- REAL ORGAN: patient category
# Documented supplement for the WordNet body-part gap (see module docstring). Same six-word
# generalization set v2 used (arm/hand were subset-B vocabulary; the rest are v2's own Bgen words).
# Deliberately NOT extended to this cell's Bgap words (ankle/elbow/knee) -- that would defeat Bgap.
BODY_PART_SUPPLEMENT = {
    w: {"animacy": "animate", "category": "body_part", "agent_capable": False}
    for w in ("arm", "hand", "leg", "face", "head", "neck", "back", "shoulder", "wrist")
}

# VERB-side force-capability lexicon (unchanged axis, NOT under test -- the axis under test is the
# object/patient-category assignment, now via lookup_animacy instead of a hand-authored map).
# Superset of v2's FORCE_CLASS_HARM plus new UNK-to-governor verbs used by Bopen/Bgap below.
FORCE_CLASS_HARM_REAL = set(v2.FORCE_CLASS_HARM) | {
    "batter", "clobber", "wallop", "pummel", "maul", "claw",     # Bopen verbs (lemma form)
    "crack", "wrench", "twist",                                   # Bgap verbs (lemma form)
}


def real_animacy_lookup(word: str, pos_tag=None):
    """word -> {"animacy","category","agent_capable"} | None. Supplement checked FIRST (documented
    WordNet body-part patch), else a live hdlab.animacy_lexicon.lookup_animacy call -- NOT a
    per-item hand-authored category map."""
    w = word.lower().strip(".,\"'();:")
    if w in BODY_PART_SUPPLEMENT:
        return BODY_PART_SUPPLEMENT[w]
    return lookup_animacy(word, pos_tag)


def build_real_animacy_map(items, lookup_fn=real_animacy_lookup) -> dict:
    """Builds word(lower) -> animacy-dict for the target-word vocabulary of `items` only (scope-of-
    application discipline, see module docstring) using the REAL organ, not a hand-picked map."""
    m = {}
    for it in items:
        w = it["target_word"].lower().strip(".,\"'();:")
        if w in m:
            continue
        pos_tag = it["pos"][it["target_idx"]] if it["target_idx"] < len(it["pos"]) else None
        r = lookup_fn(w, pos_tag)
        if r is not None:
            m[w] = r
    return m


def event_type_for_item_real(it, animacy_map: dict, force_class: set, gov_class_dict: dict):
    """Same control-flow as v2.event_type_for_item, animacy substituted for the whitelist lookup.
    Returns (event_type_or_None, category_or_None, gov_word_or_None)."""
    gi = bridge1.nearest_verb_idx(it["tokens"], it["pos"], it["target_idx"])
    if not v2.valid_direct_object(it["pos"], gi, it["target_idx"]):
        return None, None, None
    gov_word = bridge1.lemma_verb(it["tokens"][gi])
    obj_word = it["target_word"].lower()
    a = animacy_map.get(obj_word)
    if a is None:
        return None, None, gov_word
    if a["animacy"] == "inanimate":
        return "NEUTRAL", a["category"], gov_word
    gclass_narrow = gov_class_dict.get(gov_word, "UNK")
    if gov_word in force_class and gclass_narrow == "UNK":
        return "BLOCK_HIGH", a["category"], gov_word
    return None, a["category"], gov_word


# ------------------------------------------------------------------------- open-vocab items (NEW)
def build_subset_B_open():
    """6 NEW pairs (12 items). Verbs disjoint from bridge1.GOVERNOR_VERB_CLASS (genuinely UNK) and
    from v2's FORCE_CLASS_HARM. Objects disjoint from GOAL_OBJECT_WHITELIST / ADVERSARIAL_WHITELIST
    / ANIMATE_HARMABLE_WHITELIST / BODY_PART_SUPPLEMENT and from every item in v2/conf -- genuinely
    novel to any lexicon in this codebase. Every pair: one inanimate/abstract artifact patient (gold
    NEUTRAL), one animate person/animal patient (gold BLOCK_HIGH), governor held fixed within pair."""
    pairs = []
    pairs.append(("battered",
        conf.mk_gold_item(["she", "battered", "the", "fence"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "fence", "NEUTRAL", "Bopen_battered_nonharm"),
        conf.mk_gold_item(["she", "battered", "her", "nephew"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "nephew", "BLOCK_HIGH", "Bopen_battered_harm")))
    pairs.append(("clobbered",
        conf.mk_gold_item(["he", "clobbered", "the", "ledger"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "ledger", "NEUTRAL", "Bopen_clobbered_nonharm"),
        conf.mk_gold_item(["he", "clobbered", "the", "tenant"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "tenant", "BLOCK_HIGH", "Bopen_clobbered_harm")))
    pairs.append(("walloped",
        conf.mk_gold_item(["she", "walloped", "the", "canoe"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "canoe", "NEUTRAL", "Bopen_walloped_nonharm"),
        conf.mk_gold_item(["she", "walloped", "the", "drummer"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "drummer", "BLOCK_HIGH", "Bopen_walloped_harm")))
    pairs.append(("pummeled",
        conf.mk_gold_item(["he", "pummeled", "the", "statue"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "statue", "NEUTRAL", "Bopen_pummeled_nonharm"),
        conf.mk_gold_item(["he", "pummeled", "the", "sailor"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "sailor", "BLOCK_HIGH", "Bopen_pummeled_harm")))
    pairs.append(("mauled",
        conf.mk_gold_item(["she", "mauled", "the", "contract"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "contract", "NEUTRAL", "Bopen_mauled_nonharm"),
        conf.mk_gold_item(["she", "mauled", "the", "toddler"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "toddler", "BLOCK_HIGH", "Bopen_mauled_harm")))
    pairs.append(("clawed",
        conf.mk_gold_item(["he", "clawed", "the", "essay"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "essay", "NEUTRAL", "Bopen_clawed_nonharm"),
        conf.mk_gold_item(["he", "clawed", "the", "colt"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "colt", "BLOCK_HIGH", "Bopen_clawed_harm")))
    return pairs


def build_subset_B_gap():
    """3 NEW pairs (6 items). Same construction as Bopen but the animate member is a BODY-PART noun
    deliberately NOT in BODY_PART_SUPPLEMENT (ankle/elbow/knee, disjoint from v2's arm/hand/leg/
    face/head/neck/back/shoulder/wrist list) -- quantifies the raw WordNet body-part gap on open
    vocabulary. The inanimate member of each pair is a genuine artifact the real organ SHOULD get
    right (isolates the gap to the animate/body-part side, not a general organ failure)."""
    pairs = []
    pairs.append(("cracked",
        conf.mk_gold_item(["she", "cracked", "the", "vase"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "vase", "NEUTRAL", "Bgap_cracked_nonharm"),
        conf.mk_gold_item(["she", "cracked", "her", "ankle"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "ankle", "BLOCK_HIGH", "Bgap_cracked_harm")))
    pairs.append(("wrenched",
        conf.mk_gold_item(["he", "wrenched", "the", "lever"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "lever", "NEUTRAL", "Bgap_wrenched_nonharm"),
        conf.mk_gold_item(["he", "wrenched", "her", "elbow"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "elbow", "BLOCK_HIGH", "Bgap_wrenched_harm")))
    pairs.append(("twisted",
        conf.mk_gold_item(["she", "twisted", "the", "wire"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "wire", "NEUTRAL", "Bgap_twisted_nonharm"),
        conf.mk_gold_item(["she", "twisted", "her", "knee"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "knee", "BLOCK_HIGH", "Bgap_twisted_harm")))
    return pairs


SUBSET_B_OPEN_PAIRS = build_subset_B_open()
SUBSET_B_OPEN = [it for _f, a, b in SUBSET_B_OPEN_PAIRS for it in (a, b)]
SUBSET_B_GAP_PAIRS = build_subset_B_gap()
SUBSET_B_GAP = [it for _f, a, b in SUBSET_B_GAP_PAIRS for it in (a, b)]

# vocabulary the real-organ animacy map is built over (scope-of-application, see module docstring).
REAL_ORGAN_SCOPE_ITEMS = list(conf.SUBSET_B) + list(v2.SUBSET_B_GEN) + SUBSET_B_OPEN + SUBSET_B_GAP
REAL_ANIMACY_MAP = build_real_animacy_map(REAL_ORGAN_SCOPE_ITEMS)


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, n_train_theta: int) -> dict:
    try:
        gen = torch.Generator().manual_seed(seed)
        cb = sim.Codebook(gen)
        g_theta = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
        theta = sim.train_theta(cb, g_theta, "FULL", n_train_theta)

        # STAGE 1 (unmodified): governor perceptron, trained exactly as bridge1/confirmation/v2.
        train_ex = [(bridge1.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                                      bridge1.GOVERNOR_VERB_CLASS,
                                                      bridge1.ADJ_MODIFIER_CLASS)[0],
                     it["gold_type"]) for it in bridge1.TRAIN_ITEMS]
        pred_gov, w_gov, roles = train_perceptron(train_ex, seed=seed + 1000, epochs=20,
                                                    roles=sim.TYPES)
        train_bow = [(bridge1.bow_feats(it["tokens"], it["target_word"]), it["gold_type"])
                     for it in bridge1.TRAIN_ITEMS]
        pred_bow, w_bow, _ = train_perceptron(train_bow, seed=seed + 2000, epochs=20, roles=sim.TYPES)

        def gov_feats(it):
            return bridge1.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                                    bridge1.GOVERNOR_VERB_CLASS,
                                                    bridge1.ADJ_MODIFIER_CLASS)[0]

        def gov_type(it):
            return pred_gov(gov_feats(it))

        def bow_type(it):
            return pred_bow(bridge1.bow_feats(it["tokens"], it["target_word"]))

        # SCRAMBLED animacy map (can-fail control): permute the REAL map's values across its own
        # keys (same style as v2._scrambled_class_dict), seeded.
        scr_real_animacy_map = v2._scrambled_class_dict(REAL_ANIMACY_MAP, seed=seed + 6000)
        scr_closed_object_event_class = v2._scrambled_class_dict(v2.OBJECT_EVENT_CLASS, seed=seed + 4000)

        def two_stage_real_type(it):
            gt = gov_type(it)
            et, _cat, _gw = event_type_for_item_real(it, REAL_ANIMACY_MAP, FORCE_CLASS_HARM_REAL,
                                                       bridge1.GOVERNOR_VERB_CLASS)
            final_t, _winner = v2.combine_biased_competition(gt, et, None)
            return final_t

        def two_stage_real_witness(it):
            gt = gov_type(it)
            et, cat, gw = event_type_for_item_real(it, REAL_ANIMACY_MAP, FORCE_CLASS_HARM_REAL,
                                                     bridge1.GOVERNOR_VERB_CLASS)
            final_t, winner = v2.combine_biased_competition(gt, et, None)
            return {"note": it.get("note"), "gov_type": gt, "event_type": et,
                    "patient_category": cat, "gov_word": gw, "final_type": final_t,
                    "winner": winner}

        def scrambled_event_real_type(it):
            gt = gov_type(it)
            et, _cat, _gw = event_type_for_item_real(it, scr_real_animacy_map, FORCE_CLASS_HARM_REAL,
                                                       bridge1.GOVERNOR_VERB_CLASS)
            final_t, _winner = v2.combine_biased_competition(gt, et, None)
            return final_t

        def two_stage_closed_type(it):
            gt = gov_type(it)
            et, _oc, _gw = v2.event_type_for_item(it, v2.OBJECT_EVENT_CLASS, v2.FORCE_CLASS_HARM,
                                                    bridge1.GOVERNOR_VERB_CLASS)
            final_t, _winner = v2.combine_biased_competition(gt, et, None)
            return final_t

        def scrambled_event_closed_type(it):
            gt = gov_type(it)
            et, _oc, _gw = v2.event_type_for_item(it, scr_closed_object_event_class,
                                                    v2.FORCE_CLASS_HARM, bridge1.GOVERNOR_VERB_CLASS)
            final_t, _winner = v2.combine_biased_competition(gt, et, None)
            return final_t

        pools = {"A": conf.SUBSET_A, "B": conf.SUBSET_B, "Bgen": v2.SUBSET_B_GEN,
                  "Bopen": SUBSET_B_OPEN, "Bgap": SUBSET_B_GAP}
        arms = {"governor": gov_type, "bow": bow_type,
                "two_stage_real": two_stage_real_type,
                "scrambled_event_real": scrambled_event_real_type,
                "two_stage_closed": two_stage_closed_type,
                "scrambled_event_closed": scrambled_event_closed_type}

        acc = {}
        digs = {}
        for pool_name, items in pools.items():
            for arm_name, fn in arms.items():
                a, _details = v2.eval_items(items, fn, cb, theta)
                acc[f"acc_{pool_name}_{arm_name}"] = a
                d, _seq = v2.preds_digest(items, fn)
                digs[f"digest_{pool_name}_{arm_name}"] = d

        witness_Bopen = [two_stage_real_witness(it) for it in SUBSET_B_OPEN]
        witness_Bgap = [two_stage_real_witness(it) for it in SUBSET_B_GAP]

        v_bh = bridge1.valence_for_type(cb, theta, "BLOCK_HIGH")
        v_bl = bridge1.valence_for_type(cb, theta, "BLOCK_LOW")

        # arms-must-differ: TWO_STAGE_REAL must not be bit-identical to GOVERNOR on Bopen (that would
        # mean the real organ never overrode anything -- a wiring bug, not a result).
        real_eq_governor_Bopen = digs["digest_Bopen_two_stage_real"] == digs["digest_Bopen_governor"]

        return {
            "seed": seed,
            "acc": acc,
            "digests": digs,
            "real_eq_governor_Bopen": real_eq_governor_Bopen,
            "witness_Bopen": witness_Bopen,
            "witness_Bgap": witness_Bgap,
            "theta_witness": {"BLOCK_HIGH": v_bh, "BLOCK_LOW": v_bl, "coh_vs_cope_differ": v_bh != v_bl},
            "failure_class": None,
        }
    except Exception as e:
        return {"seed": seed, "failure_class": f"{type(e).__name__}: {str(e)[:300]}",
                "traceback": traceback.format_exc()[:3000]}


# ------------------------------------------------------------------------- verdict
def aggregate_and_verdict(per_seed: dict) -> dict:
    seeds = sorted(per_seed.keys())
    failed = [s for s in seeds if per_seed[s].get("failure_class")]
    ok_seeds = [s for s in seeds if not per_seed[s].get("failure_class")]

    def mean_acc(key):
        vals = [float(per_seed[s]["acc"][key]) for s in ok_seeds]
        return sum(vals) / max(1, len(vals))

    n = len(seeds)
    if n < EXPECTED_N_SEEDS or len(ok_seeds) < EXPECTED_N_SEEDS:
        return {
            "verdict": "HARD_FAIL_CARDINALITY_BREACH_META_RULE_H",
            "verdict_msg": f"landed {n} seeds ({len(ok_seeds)} ok, {len(failed)} failed), "
                           f"expected {EXPECTED_N_SEEDS}",
            "summary": "cardinality breach", "n_seeds": n, "n_ok": len(ok_seeds),
            "failed_seeds": failed,
        }

    m = {}
    for pool in ("A", "B", "Bgen", "Bopen", "Bgap"):
        for arm in ("governor", "bow", "two_stage_real", "scrambled_event_real",
                    "two_stage_closed", "scrambled_event_closed"):
            m[f"{pool}_{arm}"] = mean_acc(f"acc_{pool}_{arm}")

    any_eq_Bopen = any(per_seed[s]["real_eq_governor_Bopen"] for s in ok_seeds)
    coh_cope_differ_all = all(per_seed[s]["theta_witness"]["coh_vs_cope_differ"] for s in ok_seeds)

    lift_Bopen = m["Bopen_two_stage_real"] - m["Bopen_scrambled_event_real"]
    lift_Bgap = m["Bgap_two_stage_real"] - m["Bgap_scrambled_event_real"]

    regression_on_A = m["A_two_stage_real"] < 0.85
    bopen_pass = (m["Bopen_two_stage_real"] >= 0.75) and (lift_Bopen >= 0.15) and (m["Bopen_bow"] <= 0.60)
    bopen_governor_at_chance = 0.40 <= m["Bopen_governor"] <= 0.60
    bgap_recovers = m["Bgap_two_stage_real"] >= 0.75
    bgap_gap_present = m["Bgap_two_stage_real"] < m["Bopen_two_stage_real"] - 0.10
    hard_fail_bopen = m["Bopen_two_stage_real"] < 0.60

    if any_eq_Bopen:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif regression_on_A:
        verdict = "HARD_FAIL_REGRESSION_ON_A"
    elif bopen_pass and bgap_recovers:
        verdict = "HARD_PASS"
    elif bopen_pass and not bgap_recovers:
        verdict = "PARTIAL_WITH_BODYPART_GAP"
    elif hard_fail_bopen:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"A_two_stage_real={m['A_two_stage_real']:.3f} (A_governor={m['A_governor']:.3f}) "
               f"Bopen_two_stage_real={m['Bopen_two_stage_real']:.3f} "
               f"Bopen_governor={m['Bopen_governor']:.3f} "
               f"Bopen_scrambled_event_real={m['Bopen_scrambled_event_real']:.3f} "
               f"lift_Bopen={lift_Bopen:.3f} Bopen_bow={m['Bopen_bow']:.3f} "
               f"Bgap_two_stage_real={m['Bgap_two_stage_real']:.3f} "
               f"Bgap_governor={m['Bgap_governor']:.3f} lift_Bgap={lift_Bgap:.3f} "
               f"B_two_stage_real={m['B_two_stage_real']:.3f} (orig B closed-lexicon reference: "
               f"B_two_stage_closed={m['B_two_stage_closed']:.3f}) "
               f"Bgen_two_stage_real={m['Bgen_two_stage_real']:.3f} "
               f"(Bgen_two_stage_closed={m['Bgen_two_stage_closed']:.3f})")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": m,
        "bands": {"regression_on_A": regression_on_A, "bopen_pass": bopen_pass,
                  "bopen_governor_at_chance": bopen_governor_at_chance,
                  "bgap_recovers": bgap_recovers, "bgap_gap_present": bgap_gap_present,
                  "hard_fail_bopen": hard_fail_bopen, "lift_Bopen": lift_Bopen, "lift_Bgap": lift_Bgap,
                  "any_eq_Bopen": any_eq_Bopen, "coh_cope_differ_all_seeds": coh_cope_differ_all},
    }


# ------------------------------------------------------------------------- infra
def out_dir_for(run_mode: str) -> str:
    return OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"


def _write_start_marker(output_dir, run_mode, expected):
    marker = {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
              "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "expected_n_units": expected,
              "host": platform.node()}
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "_start_marker.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(marker, f)
    os.replace(tmp, os.path.join(output_dir, "_start_marker.json"))


def _write_metrics(output_dir, d):
    os.makedirs(output_dir, exist_ok=True)
    tmp = os.path.join(output_dir, "metrics.json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(d, f, indent=2, default=str)
    os.replace(tmp, os.path.join(output_dir, "metrics.json"))


def _write_crash(output_dir, exc):
    diag = {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(exc).__name__}: {str(exc)[:500]}",
            "summary": f"CELL_CRASHED: {type(exc).__name__}", "elapsed_s": 0.0,
            "traceback": traceback.format_exc()[:5000],
            "ts_iso": datetime.now(timezone.utc).isoformat(), "anchor_name": ANCHOR_NAME}
    _write_metrics(output_dir, diag)


def run(n_train_theta, run_mode):
    t0 = time.perf_counter()
    output_dir = out_dir_for(run_mode)
    _write_start_marker(output_dir, run_mode, EXPECTED_N_SEEDS)
    done = completed_units(output_dir)
    for seed in SEEDS:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} already done, skipping", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed, n_train_theta)
        record_unit(output_dir, k, res)
        if res.get("failure_class"):
            print(f"[FAIL] seed={seed} {res['failure_class']}", flush=True)
        else:
            a = res["acc"]
            print(f"[progress] seed={seed} done in {time.perf_counter()-ts:.1f}s "
                  f"A={a['acc_A_two_stage_real']:.3f} Bopen={a['acc_Bopen_two_stage_real']:.3f} "
                  f"Bopen_gov={a['acc_Bopen_governor']:.3f} "
                  f"Bopen_scr={a['acc_Bopen_scrambled_event_real']:.3f} "
                  f"Bgap={a['acc_Bgap_two_stage_real']:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta,
                     "n_subset_A": len(conf.SUBSET_A), "n_subset_B": len(conf.SUBSET_B),
                     "n_subset_Bgen": len(v2.SUBSET_B_GEN), "n_subset_Bopen": len(SUBSET_B_OPEN),
                     "n_subset_Bgap": len(SUBSET_B_GAP),
                     "real_animacy_map_coverage": len(REAL_ANIMACY_MAP),
                     "baseline_reference": "data/exp_bridge1_twostage_event_situation_v2/metrics.json "
                                           "closed-lexicon HARD_PASS, commit b226cfad6"}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) REAL_ANIMACY_MAP correctly classifies Bopen/Bgap vocabulary (spot-check a few);
    (2) subset-A target words are DISJOINT from REAL_ANIMACY_MAP (scope-of-application, no
    regression by construction); (3) documents the WordNet body-part gap on Bgap words specifically
    (ankle/elbow/knee return inanimate raw, NOT in BODY_PART_SUPPLEMENT); (4) Bopen/Bgap object
    vocabulary is disjoint from every whitelist/supplement in this file and in v2; (5) tiny
    end-to-end run: two_stage_real beats governor on Bopen, scrambled control collapses the lift,
    bow stays low, subset A not regressed, arms differ, Bgap shows the quantified gap."""
    # (1) spot-check real animacy classification
    assert REAL_ANIMACY_MAP["fence"]["animacy"] == "inanimate"
    assert REAL_ANIMACY_MAP["nephew"]["animacy"] == "animate"
    assert REAL_ANIMACY_MAP["colt"]["animacy"] == "animate"
    assert REAL_ANIMACY_MAP["statue"]["animacy"] == "inanimate"

    # (2) subset-A disjointness (scope-of-application, no regression by construction)
    subset_a_words = set(it["target_word"].lower() for it in conf.SUBSET_A)
    leaked = subset_a_words & set(REAL_ANIMACY_MAP.keys())
    assert not leaked, f"subset-A target word leaked into REAL_ANIMACY_MAP: {leaked}"

    # (3) documented WordNet body-part gap on Bgap-specific words (NOT in the supplement)
    for w in ("ankle", "elbow", "knee"):
        assert w not in BODY_PART_SUPPLEMENT, f"{w} must stay out of BODY_PART_SUPPLEMENT for Bgap to test the raw gap"
        raw = lookup_animacy(w, "NOUN")
        assert raw is not None and raw["animacy"] == "inanimate", (
            f"WordNet body-part gap assumption changed for {w} -- re-check Bgap design")

    # (4) open-vocab disjointness from every whitelist/supplement
    bopen_words = set(it["target_word"].lower() for it in SUBSET_B_OPEN)
    bgap_words = set(it["target_word"].lower() for it in SUBSET_B_GAP)
    closed_vocab = (set(v2.GOAL_OBJECT_WHITELIST) | set(v2.ADVERSARIAL_WHITELIST) |
                    set(v2.ANIMATE_HARMABLE_WHITELIST) | set(BODY_PART_SUPPLEMENT.keys()))
    assert bopen_words.isdisjoint(closed_vocab), f"Bopen leaked into a closed lexicon: {bopen_words & closed_vocab}"
    assert bgap_words.isdisjoint(closed_vocab), f"Bgap leaked into a closed lexicon: {bgap_words & closed_vocab}"
    v2_bgen_words = set(it["target_word"].lower() for it in v2.SUBSET_B_GEN)
    conf_b_words = set(it["target_word"].lower() for it in conf.SUBSET_B)
    assert bopen_words.isdisjoint(v2_bgen_words | conf_b_words), "Bopen reuses a v2/conf item word"

    # (5)+ tiny end-to-end run
    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    a = res["acc"]
    assert a["acc_Bopen_two_stage_real"] > a["acc_Bopen_governor"], (
        f"real-organ event-assembly did not fire on Bopen: "
        f"real={a['acc_Bopen_two_stage_real']:.3f} governor={a['acc_Bopen_governor']:.3f}")
    assert 0.40 <= a["acc_Bopen_governor"] <= 0.60, (
        f"governor-only baseline on Bopen should be ~0.500 by construction, got "
        f"{a['acc_Bopen_governor']:.3f}")
    assert a["acc_Bopen_two_stage_real"] - a["acc_Bopen_scrambled_event_real"] > 0.10, (
        f"scrambled-animacy control did not collapse the Bopen lift: "
        f"real={a['acc_Bopen_two_stage_real']:.3f} scrambled={a['acc_Bopen_scrambled_event_real']:.3f}")
    assert a["acc_A_two_stage_real"] >= 0.80, (
        f"subset A regressed: two_stage_real={a['acc_A_two_stage_real']:.3f} "
        f"(governor was {a['acc_A_governor']:.3f})")
    assert not res["real_eq_governor_Bopen"], (
        "META_RULE_AF: two_stage_real bit-identical to governor-only on Bopen -- real organ never "
        "overrode anything")
    assert res["theta_witness"]["coh_vs_cope_differ"], "theta witness: coping did not differentiate value"

    print(f"[SELFTEST PASS] A_real={a['acc_A_two_stage_real']:.3f} A_governor={a['acc_A_governor']:.3f} "
          f"Bopen_real={a['acc_Bopen_two_stage_real']:.3f} Bopen_governor={a['acc_Bopen_governor']:.3f} "
          f"Bopen_scrambled={a['acc_Bopen_scrambled_event_real']:.3f} Bopen_bow={a['acc_Bopen_bow']:.3f} "
          f"Bgap_real={a['acc_Bgap_two_stage_real']:.3f} Bgap_governor={a['acc_Bgap_governor']:.3f} "
          f"B_real={a['acc_B_two_stage_real']:.3f} B_closed_ref={a['acc_B_two_stage_closed']:.3f}",
          flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(line_buffering=True)
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        ok = self_test()
        raise SystemExit(0 if ok else 1)
    if args.smoke:
        run(SMOKE_N_TRAIN_THETA, "smoke")
        raise SystemExit(0)
    run(FULL_N_TRAIN_THETA, "full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:  # NOT BaseException
        _write_crash(OUTPUT_DIR, e)
        raise
