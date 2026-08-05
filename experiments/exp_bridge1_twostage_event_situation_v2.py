# CELL-TEMPLATE MANDATORY (META_RULE_AC/AF/AG/AH + scope/scale/floor):
# - arms_differ_verified: hash digests of GOVERNOR_ONLY vs TWO_STAGE_PORT vs BOW vs
#   SCRAMBLED_EVENT vs SCRAMBLED_DISCOURSE prediction-sequences on subsets B+C (must not be
#   all-identical; TWO_STAGE vs GOVERNOR_ONLY must literally differ on subset B and C by
#   construction of the mechanism -- that IS the discriminator).
# - final_metrics_atomicity: tmp_replace
# - except SystemExit: raise BEFORE except Exception (no BaseException)
# - crlb_n/a: no swept capacity dimension; sign-accuracy discriminator only
# - baseline_in_band: n/a (differential/discourse grounding accuracy cell, not a cleanup sweep;
#   majority baseline for every subset is 0.500 by construction, matching the confirmation test)
# - discriminator survives scale: full-N == smoke-N item sets; only theta-training steps differ
#   (matches bridge1/confirmation precedent: SMOKE_N_TRAIN_THETA=4000, FULL=8000)
# - cardinality_ok: EXPECTED_N_SEEDS=5; HARD_FAIL_CARDINALITY_BREACH_META_RULE_H if fewer land
# - per-unit failure-class instrumentation (no bare except; per-seed crash recorded)
# - calibration_check: default_ok_for_this_regime (bands are the pre-registered HARD_PASS/
#   PARTIAL/HARD_FAIL thresholds from the deep-drill SYNTHESIS contract, set BEFORE running)
# - deterministic_seeding: torch.Generator + random.Random per seed; hashlib not builtin hash()
# - cell_chunked: true (per-seed unit via tools/exp_checkpoint.py)
# - all reported numbers MEASURED@ tagged in the completion report, not this file
"""BRIDGE-1/C-AB v2 = TWO-STAGE, EVENT + SITUATION-conditioned grounding. Corrects the governor-
only reader (experiments/exp_bridge1_governor_grounding_v1.py, commit 96e8e8404) that the
confirmation test (data/exp_bridge1_confirmation_test_v1/metrics.json, commit 761211bf6) MEASURED
insufficient: RULING_CONFIRMED, governor-only scores acc_A=0.962 (local-governor subset, KEEP) but
acc_B=0.500 and acc_C=0.500 (chance) on the event-differing and discourse-decisive subsets.

Per notes/deepdrill_SYNTHESIS_bridge1_certainty.md corrected build order:

STAGE 1 (KEPT, UNMODIFIED): the governor/adjmod-conditioned perceptron from BRIDGE-1 v1
(imported from experiments.exp_bridge1_governor_grounding_v1, never edited) -- this is the
DOMINANCE-DEFAULT sense-selection stage (drill 1: sense-selection via governing predicate is
real, early, local; correct as a first stage but must be OVERRIDABLE by higher cues).

STAGE 2a EVENT ASSEMBLY (Component-3 reuse: hdlab.thematic_role_labeler.frame_slot_role/
lemma_verb, already used unchanged inside bridge1's own governor-feature extraction; PLUS a
supplied OBJECT-IDENTITY lexicon standing in for full Component-3 argument-role+goal-relation
typing, since integrating the full frame_induction/situation_reader pipeline is out of scope for
this measurement cell -- flagged honestly below). A DIRECT-OBJECT is only trusted when the
governor->target path crosses no ADP token (a genitive/possessive PRON, as in "her arm", or a
DET, as in "the game", is fine; a preposition, as in "near the cross" or "with a favor", means the
target is inside/after a PP and is NOT the verb's direct object -- abstain). When a valid direct
object's identity is a GOAL_OBJECT (game/record/problem/film + generalization: deadline/task/exam/
puzzle/quiz/match/goal/target/assignment -- concrete achievement/task nominals a harm-governor
cannot act ON in the harm sense) the event type is forced to NEUTRAL regardless of governor class
("beat the game" != harm). When the object is ADVERSARIAL (enemy/intruder + generalization: rival/
thief/trespasser/foe) the event type is forced to BLOCK_HIGH regardless of governor class (aiding/
comforting an adversary is goal-INCONGRUENT even though the governor's own class is HELP). When the
object is an ANIMATE_HARMABLE body-part/companion (arm/hand/leg/face/head/neck/back/shoulder/wrist
+ dog) AND the verb is independently known force-capable (FORCE_CLASS_HARM: break/shoot +
generalization: crush/smash/choke/stomp/slam) while bridge1's OWN narrow governor dict has never
seen that verb (UNK), the event type is forced to BLOCK_HIGH (this is where event-assembly adds
NEW knowledge the governor-only reader structurally lacks: "broke her arm" vs "broke the record").
Anywhere none of these three closed conditions fire, event-assembly ABSTAINS (returns None) and
the dominance-default (governor TYPE) is used unmodified -- this is why subset A (bridge1's own
collision+unseen items, none of whose target nouns are goal-objects/adversarial/body-parts in this
lexicon) is predicted to be UNCHANGED by this stage.

STAGE 2b SITUATION-BIAS PORT (Component-5 spirit: AccumulateRegister/GoalOutcomeRegister-style
top-down bias input; implemented here as a coarse coref-adjacent lexical reader over the PRIOR
sentence -- "it" in the target clause corefers to the entity the prior sentence introduces, so the
port reads that sentence's descriptive words for a THREAT/BENIGN valence cue, per drill 3's
peanut-in-love mechanism). THREAT_WORDS/BENIGN_WORDS are closed lexicons (hungry/wolves/prowling/
escaped/python/slithering/masked/intruder/creeping/menacing/lurking/shark/venomous/snake vs
gentle/playful/puppy/friendly/loyal/curious/elderly/affection/tender/loved/stray/begging/dolphin).
If the prior sentence contains a THREAT word, situation-bias = BLOCK_HIGH; a BENIGN word ->
NEUTRAL; neither -> abstain (None). Items with no `prior` field (subsets A and B) never invoke
this stage.

COMBINE = BIASED COMPETITION, not hard serial gating: situation-bias (if it fires) wins over
event-assembly (if it fires) wins over the governor dominance-default (always available, never
erased) -- per drill 3's "discourse is co-equal and often dominant" finding. Every item's
GOV_TYPE / EVENT_TYPE / SITUATION_TYPE / FINAL_TYPE / winning-cue are logged per-item (glass-box).

HONEST SCOPE CAVEAT (drill-mandated, not hidden): the event/situation "Component-3/5" stand-ins
here are supplied closed lexicons + a structural (ADP-crossing) direct-object gate, NOT the full
hdlab.frame_induction / hdlab.situation_reader._assign_frame_primary_roles / hdlab.
coreference_resolver / hdlab.situation_model_accumulate pipelines named in the build brief. Deep-
wiring those organs is deferred; this cell measures whether the CORRECTED TWO-STAGE+PORT SHAPE
(the thing the deep-drill certified) recovers subset B/C, using the minimum lexical knowledge that
shape requires. frame_slot_role/lemma_verb ARE reused unchanged (inherited via bridge1's own
governor-feature path); hdlab.animacy_lexicon.lookup_animacy was evaluated for the ANIMATE_HARMABLE
gate but empirically returns "inanimate" for body-part nouns (arm/hand: WordNet's first noun sense
routes through body-part hypernyms, not person/animal) so a small supplementary body-part list
was added rather than silently mis-gating (see self_test check `_bodypart_wordnet_gap_documented`).

Judged on the SAME items as the confirmation test (imported unmodified from
experiments.exp_bridge1_confirmation_test_v1, commit 761211bf6) for direct comparability, PLUS new
disjoint-vocabulary generalization pairs for event-assembly (subset B_GEN) and the situation port
(subset C_GEN) to guard against the closed-lexicon override being circular-only-on-the-6-pairs.
See preregs/2026-08-05_bridge1_twostage_event_situation_v2.md and notes/deepdrill_SYNTHESIS_
bridge1_certainty.md.
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

ANCHOR_NAME = "bridge1_twostage_event_situation_v2"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402
from hdlab.thematic_role_labeler import train_perceptron  # noqa: E402
from hdlab.animacy_lexicon import lookup_animacy  # noqa: E402 (sanity cross-check only, see self_test)
import experiments.exp_grounded_appraisal_sim_earned_v1 as sim  # noqa: E402 (REUSE: frozen sim)
import experiments.exp_bridge1_governor_grounding_v1 as bridge1  # noqa: E402 (STAGE-1, unmodified)
import experiments.exp_bridge1_confirmation_test_v1 as conf  # noqa: E402 (REUSE: subsets A/B/C, gold_sign)

SEEDS = [0, 1, 2, 3, 4]
EXPECTED_N_SEEDS = len(SEEDS)
FULL_N_TRAIN_THETA = 8000
SMOKE_N_TRAIN_THETA = 4000

# ------------------------------------------------------------------------- STAGE 2a: event lexicon
GOAL_OBJECT_WHITELIST = {
    "game", "record", "problem", "film",                       # subset-B vocabulary
    "deadline", "task", "exam", "puzzle", "quiz", "match", "goal", "target", "assignment",  # gen
}
ADVERSARIAL_WHITELIST = {
    "enemy", "intruder",                                        # subset-B vocabulary
    "rival", "thief", "trespasser", "foe",                      # generalization
}
ANIMATE_HARMABLE_WHITELIST = {
    "dog", "arm",                                                # subset-B vocabulary
    "hand", "leg", "face", "head", "neck", "back", "shoulder", "wrist",  # generalization
}
OBJECT_EVENT_CLASS = {}
for _w in GOAL_OBJECT_WHITELIST:
    OBJECT_EVENT_CLASS[_w] = "GOAL_OBJECT"
for _w in ADVERSARIAL_WHITELIST:
    OBJECT_EVENT_CLASS[_w] = "ADVERSARIAL"
for _w in ANIMATE_HARMABLE_WHITELIST:
    OBJECT_EVENT_CLASS[_w] = "ANIMATE_HARMABLE"

FORCE_CLASS_HARM = {
    "break", "shoot",                                            # subset-B vocabulary (lemma)
    "crush", "smash", "choke", "stomp", "slam",                  # generalization
}

# ------------------------------------------------------------------------- STAGE 2b: situation lexicon
THREAT_WORDS = {"hungry", "wolves", "wolf", "prowling", "escaped", "python", "slithering", "masked",
                 "intruder", "creeping", "menacing", "lurking", "shark", "venomous", "snake",
                 "coyote", "circling"}
BENIGN_WORDS = {"gentle", "playful", "puppy", "friendly", "loyal", "curious", "elderly", "affection",
                 "tender", "loved", "stray", "begging", "dolphin", "cat"}


def _scrambled_class_dict(d: dict, seed: int) -> dict:
    """META_RULE-style scramble control (reused verbatim from bridge1's own helper of the same
    name; re-declared here to keep this module import-self-contained)."""
    keys_sorted = sorted(d.keys())
    vals_sorted = [d[k] for k in keys_sorted]
    rng = random.Random(seed)
    permuted = vals_sorted[:]
    rng.shuffle(permuted)
    return dict(zip(keys_sorted, permuted))


def valid_direct_object(pos, gi: int, target_idx: int) -> bool:
    """True iff a governing verb exists (gi>=0) and no ADP token sits between it and the target --
    i.e. the target is the verb's direct object, not inside/after a PP ("near the cross", "with a
    favor" -> False; "the game", "her arm" -> True, DET/PRON in between are fine)."""
    if gi < 0 or target_idx <= gi:
        return False
    for i in range(gi + 1, target_idx):
        if i < len(pos) and pos[i] == "ADP":
            return False
    return True


def event_type_for_item(it, object_event_class: dict, force_class: set, gov_class_dict: dict):
    """Returns (event_type_or_None, object_class_or_None, gov_word_or_None)."""
    gi = bridge1.nearest_verb_idx(it["tokens"], it["pos"], it["target_idx"])
    if not valid_direct_object(it["pos"], gi, it["target_idx"]):
        return None, None, None
    gov_word = bridge1.lemma_verb(it["tokens"][gi])
    obj_word = it["target_word"].lower()
    obj_class = object_event_class.get(obj_word)
    if obj_class == "GOAL_OBJECT":
        return "NEUTRAL", obj_class, gov_word
    if obj_class == "ADVERSARIAL":
        return "BLOCK_HIGH", obj_class, gov_word
    if obj_class == "ANIMATE_HARMABLE":
        gclass_narrow = gov_class_dict.get(gov_word, "UNK")
        if gov_word in force_class and gclass_narrow == "UNK":
            return "BLOCK_HIGH", obj_class, gov_word
        return None, obj_class, gov_word
    return None, None, gov_word


def situation_type_for_prior(prior_text, threat_words: set, benign_words: set):
    if prior_text is None:
        return None
    toks = set(t.strip(".,\"'();:").lower() for t in prior_text.split())
    if toks & threat_words:
        return "BLOCK_HIGH"
    if toks & benign_words:
        return "NEUTRAL"
    return None


def combine_biased_competition(gov_type: str, event_type, situation_type):
    """Situation-bias (if it fires) > event-assembly (if it fires) > governor dominance-default
    (always available, never erased -- logged as the suppressed-but-not-erased residual)."""
    if situation_type is not None:
        return situation_type, "situation"
    if event_type is not None:
        return event_type, "event"
    return gov_type, "governor"


# ------------------------------------------------------------------------- generalization items
def build_subset_B_gen():
    """4 NEW pairs (8 items). Fresh governor verbs / objects, disjoint from subset-B's own 6 pairs
    and from bridge1 TRAIN vocab, exercising the SAME three whitelist categories via NEW words."""
    pairs = []
    pairs.append(("crushed",
        conf.mk_gold_item(["he", "crushed", "the", "deadline"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "deadline", "NEUTRAL", "Bgen_crushed_nonharm"),
        conf.mk_gold_item(["he", "crushed", "her", "leg"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "leg", "BLOCK_HIGH", "Bgen_crushed_harm")))
    pairs.append(("helped",
        conf.mk_gold_item(["she", "helped", "the", "rival"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "rival", "BLOCK_HIGH", "Bgen_helped_harm"),
        conf.mk_gold_item(["she", "helped", "the", "neighbor"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "neighbor", "RECIPROCITY", "Bgen_helped_nonharm")))
    pairs.append(("smashed",
        conf.mk_gold_item(["he", "smashed", "the", "puzzle"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "puzzle", "NEUTRAL", "Bgen_smashed_nonharm"),
        conf.mk_gold_item(["he", "smashed", "her", "hand"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "hand", "BLOCK_HIGH", "Bgen_smashed_harm")))
    pairs.append(("comforted",
        conf.mk_gold_item(["she", "comforted", "the", "thief"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "thief", "BLOCK_HIGH", "Bgen_comforted_harm"),
        conf.mk_gold_item(["she", "comforted", "the", "neighbor"], ["PRON", "VERB", "DET", "NOUN"], 3,
                          "neighbor", "RECIPROCITY", "Bgen_comforted_nonharm")))
    return pairs


def build_subset_C_gen():
    """1 NEW pair (2 items). Fresh prior sentences / target clause, disjoint from subset-C's own 6
    pairs, exercising the SAME THREAT/BENIGN lexicon on NEW sentences."""
    pairs = []
    pairs.append(("touched2",
        conf.mk_gold_item(["it", "touched", "her", "cheek"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "cheek", "RECIPROCITY", "Cgen_touched_nonharm",
                          prior="A loyal old cat had curled up beside her every night."),
        conf.mk_gold_item(["it", "touched", "her", "cheek"], ["PRON", "VERB", "PRON", "NOUN"], 3,
                          "cheek", "BLOCK_HIGH", "Cgen_touched_harm",
                          prior="A hungry coyote had been circling the campsite for days.")))
    return pairs


SUBSET_B_GEN_PAIRS = build_subset_B_gen()
SUBSET_B_GEN = [it for _f, a, b in SUBSET_B_GEN_PAIRS for it in (a, b)]
SUBSET_C_GEN_PAIRS = build_subset_C_gen()
SUBSET_C_GEN = [it for _f, a, b in SUBSET_C_GEN_PAIRS for it in (a, b)]


# ------------------------------------------------------------------------- scoring
def eval_items(items, pred_type_fn, cb, theta):
    correct = 0
    per_item = []
    for it in items:
        t = pred_type_fn(it)
        v = bridge1.valence_for_type(cb, theta, t)
        s = 1 if v > 0 else -1
        g = conf.gold_sign(it["gold_type"])
        ok = (s == g)
        correct += int(ok)
        per_item.append({"note": it.get("note"), "pred_type": t, "correct": ok})
    return correct / max(1, len(items)), per_item


def preds_digest(items, pred_type_fn):
    seq = [pred_type_fn(it) for it in items]
    return hashlib.sha256(json.dumps(seq).encode()).hexdigest()[:16], seq


# ------------------------------------------------------------------------- per-seed unit
def run_seed(seed: int, n_train_theta: int) -> dict:
    try:
        gen = torch.Generator().manual_seed(seed)
        cb = sim.Codebook(gen)
        g_theta = torch.Generator().manual_seed(seed * 100 + sim.hash_variant("FULL"))
        theta = sim.train_theta(cb, g_theta, "FULL", n_train_theta)

        # STAGE 1 (unmodified): governor perceptron, trained exactly as bridge1/confirmation.
        train_ex = [(bridge1.extract_governor_feats(it["tokens"], it["pos"], it["target_idx"],
                                                      bridge1.GOVERNOR_VERB_CLASS,
                                                      bridge1.ADJ_MODIFIER_CLASS)[0],
                     it["gold_type"]) for it in bridge1.TRAIN_ITEMS]
        pred_gov, w_gov, roles = train_perceptron(train_ex, seed=seed + 1000, epochs=20,
                                                    roles=sim.TYPES)
        # BOW control (identical engine, raw-token feats, disjoint train/test vocab).
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

        # SCRAMBLED_EVENT lexicon (broken object->category assignment, seeded).
        scr_object_event_class = _scrambled_class_dict(OBJECT_EVENT_CLASS, seed=seed + 4000)

        def two_stage_type(it):
            gt = gov_type(it)
            et, _oc, _gw = event_type_for_item(it, OBJECT_EVENT_CLASS, FORCE_CLASS_HARM,
                                                bridge1.GOVERNOR_VERB_CLASS)
            st = situation_type_for_prior(it.get("prior"), THREAT_WORDS, BENIGN_WORDS)
            final_t, _winner = combine_biased_competition(gt, et, st)
            return final_t

        def two_stage_witness(it):
            gt = gov_type(it)
            et, oc, gw = event_type_for_item(it, OBJECT_EVENT_CLASS, FORCE_CLASS_HARM,
                                              bridge1.GOVERNOR_VERB_CLASS)
            st = situation_type_for_prior(it.get("prior"), THREAT_WORDS, BENIGN_WORDS)
            final_t, winner = combine_biased_competition(gt, et, st)
            return {"note": it.get("note"), "gov_type": gt, "event_type": et, "object_class": oc,
                    "gov_word": gw, "situation_type": st, "final_type": final_t, "winner": winner}

        def scrambled_event_type(it):
            gt = gov_type(it)
            et, _oc, _gw = event_type_for_item(it, scr_object_event_class, FORCE_CLASS_HARM,
                                                bridge1.GOVERNOR_VERB_CLASS)
            st = situation_type_for_prior(it.get("prior"), THREAT_WORDS, BENIGN_WORDS)
            final_t, _winner = combine_biased_competition(gt, et, st)
            return final_t

        # SCRAMBLED_DISCOURSE: mispair the `prior` field across all prior-bearing items (subset C
        # + C_GEN pooled), seeded shuffle -- event stage untouched.
        prior_bearing = conf.SUBSET_C + SUBSET_C_GEN
        priors_true = [it.get("prior") for it in prior_bearing]
        rng = random.Random(seed + 5000)
        priors_scrambled = priors_true[:]
        rng.shuffle(priors_scrambled)
        scrambled_prior_map = {id(it): p for it, p in zip(prior_bearing, priors_scrambled)}

        def scrambled_discourse_type(it):
            gt = gov_type(it)
            et, _oc, _gw = event_type_for_item(it, OBJECT_EVENT_CLASS, FORCE_CLASS_HARM,
                                                bridge1.GOVERNOR_VERB_CLASS)
            st = situation_type_for_prior(scrambled_prior_map.get(id(it)), THREAT_WORDS, BENIGN_WORDS)
            final_t, _winner = combine_biased_competition(gt, et, st)
            return final_t

        pools = {"A": conf.SUBSET_A, "B": conf.SUBSET_B, "C": conf.SUBSET_C,
                 "Bgen": SUBSET_B_GEN, "Cgen": SUBSET_C_GEN}
        arms = {"governor": gov_type, "two_stage": two_stage_type, "bow": bow_type,
                "scrambled_event": scrambled_event_type, "scrambled_discourse": scrambled_discourse_type}

        acc = {}
        digs = {}
        for pool_name, items in pools.items():
            for arm_name, fn in arms.items():
                a, _details = eval_items(items, fn, cb, theta)
                acc[f"acc_{pool_name}_{arm_name}"] = a
                d, _seq = preds_digest(items, fn)
                digs[f"digest_{pool_name}_{arm_name}"] = d

        witness_B = [two_stage_witness(it) for it in conf.SUBSET_B]
        witness_C = [two_stage_witness(it) for it in conf.SUBSET_C]

        v_bh = bridge1.valence_for_type(cb, theta, "BLOCK_HIGH")
        v_bl = bridge1.valence_for_type(cb, theta, "BLOCK_LOW")

        # arms-must-differ: TWO_STAGE must not be bit-identical to GOVERNOR on subset B or C
        # (that would mean the mechanism never overrides anything -- a wiring bug, not a result).
        two_stage_eq_governor_B = digs["digest_B_two_stage"] == digs["digest_B_governor"]
        two_stage_eq_governor_C = digs["digest_C_two_stage"] == digs["digest_C_governor"]

        return {
            "seed": seed,
            "acc": acc,
            "digests": digs,
            "two_stage_eq_governor_B": two_stage_eq_governor_B,
            "two_stage_eq_governor_C": two_stage_eq_governor_C,
            "witness_B": witness_B,
            "witness_C": witness_C,
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
    for pool in ("A", "B", "C", "Bgen", "Cgen"):
        for arm in ("governor", "two_stage", "bow", "scrambled_event", "scrambled_discourse"):
            m[f"{pool}_{arm}"] = mean_acc(f"acc_{pool}_{arm}")

    any_eq_B = any(per_seed[s]["two_stage_eq_governor_B"] for s in ok_seeds)
    any_eq_C = any(per_seed[s]["two_stage_eq_governor_C"] for s in ok_seeds)
    coh_cope_differ_all = all(per_seed[s]["theta_witness"]["coh_vs_cope_differ"] for s in ok_seeds)

    lift_B = m["B_two_stage"] - m["B_scrambled_event"]
    lift_C = m["C_two_stage"] - m["C_scrambled_discourse"]

    regression_on_A = m["A_two_stage"] < 0.85
    b_pass = (m["B_two_stage"] >= 0.75) and (lift_B >= 0.15) and (m["B_bow"] <= 0.60)
    c_pass = (m["C_two_stage"] >= 0.70) and (lift_C >= 0.15) and (m["C_bow"] <= 0.60)
    gen_pass = (m["Bgen_two_stage"] >= 0.70) and (m["Cgen_two_stage"] >= 0.60)
    hard_fail_B = m["B_two_stage"] < 0.60

    if any_eq_B and any_eq_C:
        verdict = "HARD_FAIL_ARMS_IDENTICAL_META_RULE_AF"
    elif regression_on_A:
        verdict = "HARD_FAIL_REGRESSION_ON_A"
    elif b_pass and c_pass and gen_pass:
        verdict = "HARD_PASS"
    elif b_pass and not c_pass:
        verdict = "PARTIAL_EVENT_FIXED_SITUATION_PENDING"
    elif hard_fail_B:
        verdict = "HARD_FAIL"
    else:
        verdict = "MIDDLE_BAND"

    summary = (f"A_two_stage={m['A_two_stage']:.3f} (baseline A_governor={m['A_governor']:.3f}) "
               f"B_two_stage={m['B_two_stage']:.3f} B_governor={m['B_governor']:.3f} "
               f"B_scrambled_event={m['B_scrambled_event']:.3f} lift_B={lift_B:.3f} "
               f"B_bow={m['B_bow']:.3f} "
               f"C_two_stage={m['C_two_stage']:.3f} C_governor={m['C_governor']:.3f} "
               f"C_scrambled_discourse={m['C_scrambled_discourse']:.3f} lift_C={lift_C:.3f} "
               f"C_bow={m['C_bow']:.3f} "
               f"Bgen_two_stage={m['Bgen_two_stage']:.3f} Cgen_two_stage={m['Cgen_two_stage']:.3f}")
    return {
        "verdict": verdict, "verdict_msg": f"{verdict}: {summary}", "summary": summary,
        "n_seeds": n, "n_ok": len(ok_seeds), "failed_seeds": failed,
        "means": m,
        "bands": {"regression_on_A": regression_on_A, "b_pass": b_pass, "c_pass": c_pass,
                  "gen_pass": gen_pass, "hard_fail_B": hard_fail_B, "lift_B": lift_B, "lift_C": lift_C,
                  "any_eq_B": any_eq_B, "any_eq_C": any_eq_C,
                  "coh_cope_differ_all_seeds": coh_cope_differ_all},
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
                  f"A={a['acc_A_two_stage']:.3f} B={a['acc_B_two_stage']:.3f} "
                  f"C={a['acc_C_two_stage']:.3f} B_scr={a['acc_B_scrambled_event']:.3f} "
                  f"C_scr={a['acc_C_scrambled_discourse']:.3f}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(output_dir).values()}
    agg = aggregate_and_verdict(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = {"seeds": SEEDS, "n_train_theta": n_train_theta,
                     "n_subset_A": len(conf.SUBSET_A), "n_subset_B": len(conf.SUBSET_B),
                     "n_subset_C": len(conf.SUBSET_C), "n_subset_B_gen": len(SUBSET_B_GEN),
                     "n_subset_C_gen": len(SUBSET_C_GEN),
                     "baseline_reference": "data/exp_bridge1_confirmation_test_v1/metrics.json "
                                           "(A=0.962, B=0.500, C=0.500, commit 761211bf6)"}
    agg["per_seed"] = per_seed
    _write_metrics(output_dir, agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.1f}s", flush=True)
    return agg


# ------------------------------------------------------------------------- self-test
def self_test():
    """(1) structural gate sanity (valid_direct_object true/false on hand-checked examples);
    (2) event/situation lexicons don't overlap bridge1 TRAIN governor vocab in a way that would
    make subset-A regress (spot-check the known-risky items: cross/sound/insult/warrior);
    (3) documents the WordNet body-part gap (arm/hand return inanimate; that's WHY the
    supplementary ANIMATE_HARMABLE list exists, not a silent bug); (4) tiny end-to-end run:
    two_stage beats governor on B and C, scrambled controls collapse the respective lift, bow
    stays low, subset A is not regressed, arms differ, theta witness fires."""
    # (1) structural gate
    toks = ["she", "beat", "the", "game"]
    pos = ["PRON", "VERB", "DET", "NOUN"]
    assert valid_direct_object(pos, 1, 3) is True
    toks2 = ["he", "attack", "her", "near", "the", "cross"]
    pos2 = ["PRON", "VERB", "PRON", "ADP", "DET", "NOUN"]
    assert valid_direct_object(pos2, 1, 5) is False, "ADP-crossing PP object must be rejected"
    toks3 = ["he", "broke", "her", "arm"]
    pos3 = ["PRON", "VERB", "PRON", "NOUN"]
    assert valid_direct_object(pos3, 1, 3) is True, "possessive PRON before object must be allowed"

    # (2) subset-A risk-item spot-check: event-assembly must ABSTAIN on these (object not in any
    # whitelist, or PP-crossing), preserving bridge1's own governor-only behavior on subset A.
    risky_words = {"cross", "sound", "insult", "warrior", "curse", "trick", "blow", "reward",
                   "penalty", "favor", "threat", "gift", "warning"}
    assert risky_words.isdisjoint(OBJECT_EVENT_CLASS.keys()), (
        f"a subset-A target word leaked into the event whitelist: "
        f"{risky_words & set(OBJECT_EVENT_CLASS.keys())}")

    # (3) documented WordNet body-part gap
    arm_lookup = lookup_animacy("arm")
    assert arm_lookup is not None and arm_lookup["animacy"] == "inanimate", (
        "WordNet body-part gap assumption changed -- re-check whether the supplementary "
        "ANIMATE_HARMABLE body-part list is still needed")

    # (4)+ tiny end-to-end run
    res = run_seed(0, n_train_theta=SMOKE_N_TRAIN_THETA)
    assert res["failure_class"] is None, f"run_seed crashed: {res.get('failure_class')}"
    a = res["acc"]
    assert a["acc_B_two_stage"] > a["acc_B_governor"], (
        f"event-assembly did not fire on B: two_stage={a['acc_B_two_stage']:.3f} "
        f"governor={a['acc_B_governor']:.3f}")
    assert a["acc_C_two_stage"] > a["acc_C_governor"], (
        f"situation-port did not fire on C: two_stage={a['acc_C_two_stage']:.3f} "
        f"governor={a['acc_C_governor']:.3f}")
    assert a["acc_B_two_stage"] - a["acc_B_scrambled_event"] > 0.10, (
        f"scrambled-event control did not collapse the B lift: two_stage={a['acc_B_two_stage']:.3f} "
        f"scrambled={a['acc_B_scrambled_event']:.3f}")
    assert a["acc_C_two_stage"] - a["acc_C_scrambled_discourse"] > 0.10, (
        f"scrambled-discourse control did not collapse the C lift: "
        f"two_stage={a['acc_C_two_stage']:.3f} scrambled={a['acc_C_scrambled_discourse']:.3f}")
    assert a["acc_A_two_stage"] >= 0.80, (
        f"subset A regressed: two_stage={a['acc_A_two_stage']:.3f} (governor was "
        f"{a['acc_A_governor']:.3f})")
    assert not res["two_stage_eq_governor_B"] or not res["two_stage_eq_governor_C"], (
        "META_RULE_AF: two_stage bit-identical to governor-only on BOTH B and C -- mechanism "
        "never overrode anything")
    assert res["theta_witness"]["coh_vs_cope_differ"], "theta witness: coping did not differentiate value"

    print(f"[SELFTEST PASS] A_two_stage={a['acc_A_two_stage']:.3f} A_governor={a['acc_A_governor']:.3f} "
          f"B_two_stage={a['acc_B_two_stage']:.3f} B_governor={a['acc_B_governor']:.3f} "
          f"B_scrambled_event={a['acc_B_scrambled_event']:.3f} B_bow={a['acc_B_bow']:.3f} "
          f"C_two_stage={a['acc_C_two_stage']:.3f} C_governor={a['acc_C_governor']:.3f} "
          f"C_scrambled_discourse={a['acc_C_scrambled_discourse']:.3f} C_bow={a['acc_C_bow']:.3f} "
          f"Bgen={a['acc_Bgen_two_stage']:.3f} Cgen={a['acc_Cgen_two_stage']:.3f}", flush=True)
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
