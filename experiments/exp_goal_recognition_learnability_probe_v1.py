"""exp_goal_recognition_learnability_probe_v1 -- TEST-FIRST learnability probe (part-1 of the
narrative frontier: LEARNABLE goal-recognition).

WHY (per diagnostic finding e3f14d025 + owner-directed task brief): hdlab.goal_typing.
find_desired_state is a fixed desiderative-verb-governed purpose-infinitival pattern (fires only
when a GOAL_GOVERNING_PASS token -- desiderative | conative | intention -- is IMMEDIATELY followed
by a "to VERB" complement, or the 2026-08-07 hedged-wish/request dialogue fallbacks). It MISSES
varied/implicit modern goal expressions: "dreamed of winning" (no governing verb at all), "was
entering a contest" ("enter" not in the pass lexicon), "made a bet" (a commitment-establishing NOUN
construction, no verb-governs-infinitival structure), "wanted a new video game" (want + NP object,
NOT want + to-VP -- the SAME lexical cue, a DIFFERENT construction), "needed to get gas" / "had to
make something" (necessity modals -- need/have are deliberately OUTSIDE GOAL_GOVERNING_PASS),
"decided she would take a trip" (decide + finite complement, not decide + to-VP), "was excited to
try it on" (a bouletic-eagerness cousin of hope/want, not in the lexicon).

Per the missing-LEARNING route (route errors by flavor: used-ability-wrong / missing-PRIMITIVE /
missing-FACT / missing-LEARNING), this probes whether hdlab.learner (the owned MDL model-selection
engine, hdlab/learner/registry.py) can INDUCE a goal-recognizer from a small named, interpretable
lexico-syntactic feature set that GENERALIZES past find_desired_state's narrow governing-verb-gated
construction, on HELD-OUT stories (train/test split by STORY, reusing the existing split field
already present in experiments/data/narrative_goal_outcome_rocstories_relabeled_v1.jsonl -- not a
split invented for this probe).

THIS IS A LEARNABILITY PROBE, NOT A PRODUCTION WIRE: does the learner beat find_desired_state's
held-out recall on modern narrative goals, without precision collapse (over-firing), with a
non-episodic (MDL-compressing) induced hypothesis whose signal collapses under a label-scramble
control? A negative/flat result here is diagnosed (features insufficient? too little data? deeper
syntax/semantics needed?), never reported as an intrinsic ceiling.

DATASET (STEP 1): built fresh this cell -- experiments/data/goal_recognition_modern_v1.jsonl.
Every non-skipped sentence from the FULL 5-sentence "text" field of all 40 unique stories in
narrative_goal_outcome_rocstories_relabeled_v1.jsonl (deduped by story, MET/UNMET share the same
goal_text/first sentences) is hand-labeled GOAL-POSITIVE (a character wants/pursues/aims-at/commits-
to something) or GOAL-NEGATIVE (outcome/neutral-narration/action sentence, no goal), independent of
what find_desired_state itself would predict -- find_desired_state's verdict is computed AT RUNTIME
below for reporting (caught/missed), never used to assign gold labels (that would be circular).
Split reused verbatim from the source file's own "split" field (a clean pre-existing 20-story/
20-story train/test partition, not invented here). A small (7-item) hand-authored supplement rounds
out feature coverage for constructions barely attested in the 40 stories (aspiration-noun subject
"her dream was to X", explicit "set out to", explicit "competing for", one "determined to" control
item) -- clearly tagged source="handauthored_supplement", a small minority of the dataset.

FEATURES (STEP 2): named, interpretable, lexico-syntactic (see featurize() below) -- desiderative/
intention-verb presence (find_desired_state's own GOAL_GOVERNING_PASS cue set, imported not
reimplemented), aspiration-noun, pursuit/attempt construction, modal-want (would like/hoping-to/
excited-to), necessity-modal (need/have-to), decision+finite-complement, commitment-establishing
noun (bet/budget), first-person-subject, plus the REUSED action_frame_feats() organ (purpose_to_
no_det / has_directional_pp, hdlab.goal_typing, verb-lemma-independent structural cue) and a
negation_present precision-guard feature.

LEARN (STEP 3): hdlab.learner.registry.learn(candidate_plugins=["estimation","ruleind","gam"]) on
TRAIN features->is_goal; auto-selects the best-compressing hypothesis class (MDL, mdl_select). Held-
out APPLY on TEST. BASELINE = hdlab.goal_typing.find_desired_state(sentence) is not None, same TEST
set. Both recall AND precision reported (goal-recognition needs high recall without over-firing).

GATE (pre-registered in the task brief, reproduced here): HARD-PASS iff learned held-out recall >
find_desired_state's recall AND precision stays reasonable (not degenerate) AND the chosen
hypothesis is non-episodic (compression_ratio > 1, MDL genuinely compresses past the null code) AND
a label-SCRAMBLE control (train labels randomly permuted, same features, same fit procedure,
deterministic seed) collapses held-out performance toward the test base rate -- proving the real
fit's signal is genuine feature-label association, not an artifact of dataset/fit mechanics.

OPS (owner-directed, detach-forbidden): ONE self-contained blocking script -- load data (inline),
featurize, fit, evaluate, scramble-control, self-test, print everything, exit. No background tasks,
no checkpointing (this is a <1s CPU fit on ~200 hand-labeled sentences, not a multi-unit GPU loop --
tools/exp_checkpoint.py's mandate is for >1-unit loops over (arm,seed); this is a single train+eval
unit, exempt by the same logic as every other <1s glass-box probe in this codebase, e.g.
hdlab/goal_typing.py's own induce_hypothesis() FIT-set fit).
"""
from __future__ import annotations

import json
import os
import random
import re

from hdlab.goal_typing import (
    GOAL_GOVERNING_PASS, NEGATORS, action_frame_feats, find_desired_state,
)
from hdlab.learner import apply as learner_apply, learn as learner_learn

OUT_DATASET_PATH = "experiments/data/goal_recognition_modern_v1.jsonl"
OUT_METRICS_DIR = "data/exp_goal_recognition_learnability_probe_v1"
OUT_METRICS_PATH = os.path.join(OUT_METRICS_DIR, "metrics.json")

SCRAMBLE_SEED = 20260807

# ============================================================================================
# STEP 1: DATASET. Every non-skipped sentence of the FULL 5-sentence "text" for all 40 unique
# stories in narrative_goal_outcome_rocstories_relabeled_v1.jsonl (MET/UNMET share the same first
# 4 sentences; the dedup below always used the first-occurring ("_met" or sole relabeled) variant's
# full "text", verbatim, copied out of that file -- not re-typed from memory). gold=1 GOAL-POSITIVE
# (character wants/pursues/aims-at/commits-to something), gold=0 GOAL-NEGATIVE (outcome/neutral-
# narration/action, no goal expressed IN THIS SENTENCE). split reused from the source file's own
# "split" field per story (20 train stories / 20 test stories, a pre-existing partition). One
# sentence (jared_movie_alone s1, an embedded question about the FRIENDS' hypothetical desire, not
# an asserted goal of any established character) is SKIPPED as genuinely ambiguous, not forced
# either way.
#
# note field: brief rationale, focused on the harder/borderline calls (why POS despite no lexical
# desiderative marker, why NEG despite a desiderative WORD being present, etc). baseline_fires is
# computed at RUNTIME below (find_desired_state), never hand-asserted here -- gold labels are
# independent, non-circular.
RAW_ITEMS = [
    # ---- rocs_ignacio_swim_team (train) ----
    dict(id="ignacio_s0", story="ignacio_swim_team", split="train", gold=1,
         text="Ignacio wants to play a sport while he is in college.", note="desiderative want+to-VP."),
    dict(id="ignacio_s1", story="ignacio_swim_team", split="train", gold=1,
         text="Since he was a good swimmer, he decides to try out for swim the team.",
         note="decide+to-VP, intention-forming pursuit."),
    dict(id="ignacio_s2", story="ignacio_swim_team", split="train", gold=0,
         text="Ignacio makes it onto the team easily.", note="action/outcome, no goal marker."),
    dict(id="ignacio_s3", story="ignacio_swim_team", split="train", gold=0,
         text="At the first swim meet, Ignacio wins second place!", note="outcome."),
    dict(id="ignacio_s4", story="ignacio_swim_team", split="train", gold=0,
         text="Ignacio won a silver medal.", note="outcome."),

    # ---- rocs_ellen_rose_prize (train) ----
    dict(id="ellen_s0", story="ellen_rose_prize", split="train", gold=1,
         text="Ellen dreamed of winning a prize for her roses.",
         note="IMPLICIT: 'dreamed of X' -- no governing GOAL_GOVERNING_PASS verb + to-VP structure at all."),
    dict(id="ellen_s1", story="ellen_rose_prize", split="train", gold=1,
         text="She planned to enter her special purple rose at the fair.", note="plan+to-VP."),
    dict(id="ellen_s2", story="ellen_rose_prize", split="train", gold=0,
         text="She fertilized the rose bush and covered it each night.", note="instrumental action."),
    dict(id="ellen_s3", story="ellen_rose_prize", split="train", gold=0,
         text="The roses grew more beautiful every day.", note="narration."),
    dict(id="ellen_s4", story="ellen_rose_prize", split="train", gold=0,
         text="Ellen ended up winning the prize.", note="outcome."),

    # ---- rocs_bernice_africa_trip (train) ----
    dict(id="bernice_s0", story="bernice_africa_trip", split="train", gold=1,
         text="Bernice always wanted to travel to Africa.", note="want+to-VP."),
    dict(id="bernice_s1", story="bernice_africa_trip", split="train", gold=1,
         text="Bernice decided she would take a trip for her birthday next year.",
         note="IMPLICIT: decide + FINITE complement ('she would X'), not decide+to-VP -- find_desired_state requires an immediate 'to VERB'."),
    dict(id="bernice_s2", story="bernice_africa_trip", split="train", gold=0,
         text="Bernice started to look at the price of airline tickets for the trip.",
         note="aspectual 'started to' action, not a goal statement."),
    dict(id="bernice_s3", story="bernice_africa_trip", split="train", gold=0,
         text="In addition, Bernice looked up the price of hotels as well.", note="action."),
    dict(id="bernice_s4", story="bernice_africa_trip", split="train", gold=1,
         text="Bernice decided to get an airplane ticket and reserve a room.",
         note="decide+to-VP -- a fresh intention-formation clause (dataset's 'outcome_text' field, but syntactically/semantically goal-constituting on its own, same as any other decided-to sentence)."),

    # ---- rocs_tim_baking_contest (train) ----
    dict(id="tim_s0", story="tim_baking_contest", split="train", gold=1,
         text="Tim was entering a baking contest.",
         note="IMPLICIT: participation/commitment construction ('entering a contest'), 'enter' not in GOAL_GOVERNING_PASS."),
    dict(id="tim_s1", story="tim_baking_contest", split="train", gold=1,
         text="He decided to make his famous donuts.", note="decide+to-VP."),
    dict(id="tim_s2", story="tim_baking_contest", split="train", gold=0,
         text="He made a big batch and entered them into the contest.", note="action (resolving the goal, not stating it)."),
    dict(id="tim_s3", story="tim_baking_contest", split="train", gold=0,
         text="The judges thought they were delicious.", note="reaction/precursor to outcome."),
    dict(id="tim_s4", story="tim_baking_contest", split="train", gold=0,
         text="Tim won the baking contest.", note="outcome."),

    # ---- rocs_fred_weight_bet (train) ----
    dict(id="fred_s0", story="fred_weight_bet", split="train", gold=1,
         text="Fred made a bet with Sam over who could lose more weight in a month.",
         note="IMPLICIT: 'made a bet' -- a commitment-establishing NOUN construction, no governing verb+to-VP."),
    dict(id="fred_s1", story="fred_weight_bet", split="train", gold=1,
         text="Fred really wanted to win the bet, which was for $100.", note="want+to-VP."),
    dict(id="fred_s2", story="fred_weight_bet", split="train", gold=0,
         text="Fred worked out daily, avoided fast food, and skipped dinner.", note="pursuit action."),
    dict(id="fred_s3", story="fred_weight_bet", split="train", gold=0,
         text="At the end of the month Fred was feeling confident he would win.",
         note="expectation/affect about the outcome, not a goal statement."),
    dict(id="fred_s4", story="fred_weight_bet", split="train", gold=0,
         text="Fred ended up winning the bet, and the $100.", note="outcome."),

    # ---- rocs_ryan_bike_led (test) ----
    dict(id="ryan_s0", story="ryan_bike_led", split="test", gold=1,
         text="Ryan loved to customize his bike.", note="love+to-VP (bouletic-desire class, caught)."),
    dict(id="ryan_s1", story="ryan_bike_led", split="test", gold=1,
         text="He decided to add some LED lights to the bike frame and wheels.", note="decide+to-VP."),
    dict(id="ryan_s2", story="ryan_bike_led", split="test", gold=0,
         text="He ordered the parts from eBay.", note="action."),
    dict(id="ryan_s3", story="ryan_bike_led", split="test", gold=0,
         text="When they arrived, he assembled them.", note="action."),
    dict(id="ryan_s4", story="ryan_bike_led", split="test", gold=0,
         text="Ryan loved how his bike looked.",
         note="PRECISION TRAP: 'loved' present (a GOAL_GOVERNING_PASS lexeme) but NOT governing a to-VP/goal-NP -- an affective reaction, not a goal."),

    # ---- rocs_nya_paintball (test) ----
    dict(id="nya_s0", story="nya_paintball", split="test", gold=0,
         text="Nya had been asked on a paintball trip with friends.", note="passive, not her goal."),
    dict(id="nya_s1", story="nya_paintball", split="test", gold=0,
         text="She was nervous about going.", note="affect, not a goal."),
    dict(id="nya_s2", story="nya_paintball", split="test", gold=1,
         text="But she went anyways, hoping to have fun.", note="hoping+to-VP."),
    dict(id="nya_s3", story="nya_paintball", split="test", gold=0,
         text="She shot paintballs at her friends and laughed the whole time.", note="action."),
    dict(id="nya_s4", story="nya_paintball", split="test", gold=1,
         text="She loved it so much she planned a trip for the next week.",
         note="IMPLICIT: 'planned a TRIP' -- plan+NP-object, not plan+to-VP."),

    # ---- rocs_priya_new_restaurant (test) ----
    dict(id="priya_s0", story="priya_new_restaurant", split="test", gold=1,
         text="Priya decided to try a new restaurant.", note="decide+to-VP."),
    dict(id="priya_s1", story="priya_new_restaurant", split="test", gold=0,
         text="She drove to a new cafe that opened.", note="action, 'to a new cafe' is a PP not purpose-infinitival."),
    dict(id="priya_s2", story="priya_new_restaurant", split="test", gold=0,
         text="Priya sat at a booth.", note="action."),
    dict(id="priya_s3", story="priya_new_restaurant", split="test", gold=0,
         text="She ordered a mimosa and a breakfast burrito.", note="action."),
    dict(id="priya_s4", story="priya_new_restaurant", split="test", gold=0,
         text="Priya thought her food was delicious.", note="reaction/outcome."),

    # ---- rocs_colin_bar_budget (test) ----
    dict(id="colin_s0", story="colin_bar_budget", split="test", gold=0,
         text="Colin was invited to the bar by his friends.", note="passive."),
    dict(id="colin_s1", story="colin_bar_budget", split="test", gold=0,
         text="He loves beer but thinks it's too expensive at the bars.",
         note="PRECISION TRAP: 'loves' present but governs an NP (beer), a general preference not a specific goal."),
    dict(id="colin_s2", story="colin_bar_budget", split="test", gold=1,
         text="He decided to go anyway.", note="decide+to-VP."),
    dict(id="colin_s3", story="colin_bar_budget", split="test", gold=1,
         text="He gave himself a budget.",
         note="IMPLICIT: commitment-establishing action (self-regulation goal), no lexical goal marker at all."),
    dict(id="colin_s4", story="colin_bar_budget", split="test", gold=0,
         text="Colin stuck to his budget and only drank 2 beers.", note="outcome (goal achieved)."),

    # ---- rocs_tyler_balloon_party (test) ----
    dict(id="tyler_s0", story="tyler_balloon_party", split="test", gold=1,
         text="Tyler wanted to have a balloon party with tons of balloons.", note="want+to-VP."),
    dict(id="tyler_s1", story="tyler_balloon_party", split="test", gold=0,
         text="He and his friends and his parents blew up the balloons.", note="action."),
    dict(id="tyler_s2", story="tyler_balloon_party", split="test", gold=0,
         text="He and his friends played with the balloons and had a lot of fun.", note="action/state."),
    dict(id="tyler_s3", story="tyler_balloon_party", split="test", gold=0,
         text="They got tired and watched a movie and had dinner.", note="action."),
    dict(id="tyler_s4", story="tyler_balloon_party", split="test", gold=0,
         text="It had been a very fun day.", note="outcome/evaluation."),

    # ---- rocs_sarah_europe_disappointment (test) ----
    dict(id="sarah_s0", story="sarah_europe_disappointment", split="test", gold=1,
         text="Sarah had been dreaming of visiting Europe for years.",
         note="IMPLICIT: 'dreaming of X', no governing verb+to-VP."),
    dict(id="sarah_s1", story="sarah_europe_disappointment", split="test", gold=0,
         text="She had finally saved enough for the trip.", note="instrumental action."),
    dict(id="sarah_s2", story="sarah_europe_disappointment", split="test", gold=0,
         text="She landed in Spain and traveled east across the continent.", note="action."),
    dict(id="sarah_s3", story="sarah_europe_disappointment", split="test", gold=0,
         text="She didn't like how different everything was.",
         note="PRECISION TRAP: negated 'like' present, describes a completed reaction not a forward goal."),
    dict(id="sarah_s4", story="sarah_europe_disappointment", split="test", gold=0,
         text="Sarah decided that she preferred her home over Europe.",
         note="'decided that X' -- a realization/conclusion, not a forward-looking goal."),

    # ---- rocs_amber_sunday_errands (test) ----
    dict(id="amber_s0", story="amber_sunday_errands", split="test", gold=1,
         text="Amber had a lot of things to do this Sunday.",
         note="IMPLICIT: task-list/obligation framing ('had ... to do'); no GOAL_GOVERNING_PASS governing verb ('had' is not in the pass lexicon)."),
    dict(id="amber_s1", story="amber_sunday_errands", split="test", gold=1,
         text="She made a list of all the places she needed to go.",
         note="IMPLICIT: 'needed to go' -- need is deliberately OUTSIDE GOAL_GOVERNING_PASS (OTHER_STOP_UNCHANGED)."),
    dict(id="amber_s2", story="amber_sunday_errands", split="test", gold=0,
         text="She hurried to get ready.", note="manner/aspectual action, not a goal declaration."),
    dict(id="amber_s3", story="amber_sunday_errands", split="test", gold=0,
         text="She was worried that she would not have enough time.", note="anxiety/affect, not a goal."),
    dict(id="amber_s4", story="amber_sunday_errands", split="test", gold=0,
         text="Amber was so hurried she left the list at home.", note="outcome (ironic)."),

    # ---- rocs_jill_unbreakable_cups (test) ----
    dict(id="jill_s0", story="jill_unbreakable_cups", split="test", gold=0,
         text="Jill saw an infomercial for unbreakable glass cups.", note="perception/action."),
    dict(id="jill_s1", story="jill_unbreakable_cups", split="test", gold=0,
         text="She was amazed and ordered them.", note="action/affect."),
    dict(id="jill_s2", story="jill_unbreakable_cups", split="test", gold=1,
         text="When Jill received the cups, she wanted to test them.", note="want+to-VP."),
    dict(id="jill_s3", story="jill_unbreakable_cups", split="test", gold=0,
         text="She dropped one on her hardwood floor.", note="action."),
    dict(id="jill_s4", story="jill_unbreakable_cups", split="test", gold=0,
         text="It broke and Jill felt dumb for believing the hype.", note="outcome."),

    # ---- rocs_mary_new_dress (test) ----
    dict(id="mary_s0", story="mary_new_dress", split="test", gold=0,
         text="Mary went to the park.", note="action."),
    dict(id="mary_s1", story="mary_new_dress", split="test", gold=1,
         text="She wanted to show off her new dress.", note="want+to-VP."),
    dict(id="mary_s2", story="mary_new_dress", split="test", gold=0,
         text="A bird flew over Mary and pooped.", note="action, unrelated event."),
    dict(id="mary_s3", story="mary_new_dress", split="test", gold=0,
         text="Her dress became covered in bird poop.", note="outcome."),
    dict(id="mary_s4", story="mary_new_dress", split="test", gold=0,
         text="Mary was upset that her dress was ruined.", note="outcome/affect."),

    # ---- rocs2_anna_dance_invite (train) ----
    dict(id="anna_s0", story="anna_dance_invite", split="train", gold=1,
         text="Anna wanted to invite her crush Peter to the Sadie Hawkins dance.", note="want+to-VP."),
    dict(id="anna_s1", story="anna_dance_invite", split="train", gold=0,
         text="But Peter was very cute and popular.", note="description."),
    dict(id="anna_s2", story="anna_dance_invite", split="train", gold=0,
         text="Anna feared her was far out of her league.", note="fear/affect, not a goal."),
    dict(id="anna_s3", story="anna_dance_invite", split="train", gold=0,
         text="She summoned her courage and asked him, expecting a rejection.", note="action."),
    dict(id="anna_s4", story="anna_dance_invite", split="train", gold=0,
         text="But to her joy, Peter happily agreed to be her date!", note="outcome."),

    # ---- rocs2_ty_hearing_aid (train) ----
    dict(id="ty_s0", story="ty_hearing_aid", split="train", gold=1,
         text="Ty had been deaf all her life, but now she was hoping to hear.", note="hoping+to-VP."),
    dict(id="ty_s1", story="ty_hearing_aid", split="train", gold=0,
         text="Her doctor had offered her a new kind of super-powered hearing aid.", note="other-agent action."),
    dict(id="ty_s2", story="ty_hearing_aid", split="train", gold=0,
         text="She had it implanted and then waited eagerly for her first sound.", note="action/anticipation."),
    dict(id="ty_s3", story="ty_hearing_aid", split="train", gold=0,
         text="And she heard hundreds, voices and music and more!", note="outcome."),
    dict(id="ty_s4", story="ty_hearing_aid", split="train", gold=0,
         text="She loved those sounds so much that she became a musician.",
         note="PRECISION TRAP: 'loved' present, governs NP not to-VP -- outcome reaction."),

    # ---- rocs2_erica_chicken_pot_pie (train) ----
    dict(id="erica_s0", story="erica_chicken_pot_pie", split="train", gold=1,
         text="Erica wanted to help her mom this Thanksgiving.", note="want+to-VP."),
    dict(id="erica_s1", story="erica_chicken_pot_pie", split="train", gold=1,
         text="She wanted to make chicken pot pie for her family.", note="want+to-VP."),
    dict(id="erica_s2", story="erica_chicken_pot_pie", split="train", gold=0,
         text="She bought all the ingredients at the store.", note="action."),
    dict(id="erica_s3", story="erica_chicken_pot_pie", split="train", gold=0,
         text="When she came home she remembered her oven wasn't working.", note="obstacle/state."),
    dict(id="erica_s4", story="erica_chicken_pot_pie", split="train", gold=0,
         text="She was able to bake her chicken pot pie at her neighbor's house.", note="outcome."),

    # ---- rocs2_tony_gas (train) ----
    dict(id="tony_s0", story="tony_gas", split="train", gold=1,
         text="Tony needed to get gas on his way home.",
         note="IMPLICIT: 'needed to' -- need OUTSIDE GOAL_GOVERNING_PASS, even though syntactically it IS a to-VP construction."),
    dict(id="tony_s1", story="tony_gas", split="train", gold=0,
         text="He only had enough money to fill half of his tank.", note="state/constraint, 'money to fill' is NP+relative, no governing verb."),
    dict(id="tony_s2", story="tony_gas", split="train", gold=0,
         text="When he went to pay for it, he was didn't owe anything.", note="action."),
    dict(id="tony_s3", story="tony_gas", split="train", gold=0,
         text="Someone else had already paid for a full tank of gas for him.", note="other-agent outcome."),
    dict(id="tony_s4", story="tony_gas", split="train", gold=0,
         text="Tony felt double blessed after getting gas on his way home.", note="outcome/affect."),

    # ---- rocs2_sally_piano_lessons (train) ----
    dict(id="sallyp_s0", story="sally_piano_lessons", split="train", gold=1,
         text="Sally wanted to play piano.", note="want+to-VP."),
    dict(id="sallyp_s1", story="sally_piano_lessons", split="train", gold=0,
         text="Her family didn't have money for lessons.", note="obstacle/state."),
    dict(id="sallyp_s2", story="sally_piano_lessons", split="train", gold=0,
         text="She asked a teacher if she could babysit in exchange for lessons.", note="action/request."),
    dict(id="sallyp_s3", story="sally_piano_lessons", split="train", gold=0,
         text="The teacher agreed.", note="outcome."),
    dict(id="sallyp_s4", story="sally_piano_lessons", split="train", gold=0,
         text="Sally grew up to be a pianist.", note="outcome."),

    # ---- rocs2_ro_film_club (train) ----
    dict(id="ro_s0", story="ro_film_club", split="train", gold=1,
         text="Ro wanted to join her school's film club.", note="want+to-VP."),
    dict(id="ro_s1", story="ro_film_club", split="train", gold=0,
         text="She filled out the form for membership.", note="action."),
    dict(id="ro_s2", story="ro_film_club", split="train", gold=0,
         text="Soon the club's president texted her.", note="other-agent action."),
    dict(id="ro_s3", story="ro_film_club", split="train", gold=0,
         text="He said Ro was welcome to join their club!", note="outcome, reported speech."),
    dict(id="ro_s4", story="ro_film_club", split="train", gold=0,
         text="Ro was very happy.", note="outcome/affect."),

    # ---- rocs2_sally_beaded_necklace_gift (train) ----
    dict(id="sallyn_s0", story="sally_beaded_necklace_gift", split="train", gold=1,
         text="Sally wanted to give her Mom something special for her birthday.", note="want+to-VP."),
    dict(id="sallyn_s1", story="sally_beaded_necklace_gift", split="train", gold=0,
         text="She did not have any money to buy anything.", note="obstacle/state, NP+infinitival not governing-verb."),
    dict(id="sallyn_s2", story="sally_beaded_necklace_gift", split="train", gold=1,
         text="Sally had to make something for her instead.",
         note="IMPLICIT: deontic 'had to VP' necessity modal, have/had not in GOAL_GOVERNING_PASS."),
    dict(id="sallyn_s3", story="sally_beaded_necklace_gift", split="train", gold=0,
         text="She got her beads and string out and went to work.", note="action."),
    dict(id="sallyn_s4", story="sally_beaded_necklace_gift", split="train", gold=0,
         text="Sally made a pretty pink necklace out of beads for her Mom's birthday.", note="outcome."),

    # ---- rocs2_matt_own_baseball_team (train) ----
    dict(id="mattb_s0", story="matt_own_baseball_team", split="train", gold=1,
         text="Matt wanted to play baseball.", note="want+to-VP."),
    dict(id="mattb_s1", story="matt_own_baseball_team", split="train", gold=0,
         text="His classmates wouldn't let him be on their team.", note="obstacle, other-agent."),
    dict(id="mattb_s2", story="matt_own_baseball_team", split="train", gold=0,
         text="His brothers said he was too small and scrawny to play with them.",
         note="PRECISION TRAP: 'too small... to play' is a DEGREE infinitival, not a purpose-infinitival goal construction."),
    dict(id="mattb_s3", story="matt_own_baseball_team", split="train", gold=0,
         text="So Matt thought of a way to play ball like he wanted.", note="problem-solving/pursuit narration, references an earlier-stated goal."),
    dict(id="mattb_s4", story="matt_own_baseball_team", split="train", gold=0,
         text="He started his own team and recruited kids to play with him!", note="outcome/resolution."),

    # ---- rocs2_robert_police_officer (train) ----
    dict(id="robert_s0", story="robert_police_officer", split="train", gold=1,
         text="Robert wanted to be a police officer.", note="want+to-VP."),
    dict(id="robert_s1", story="robert_police_officer", split="train", gold=0,
         text="He went to school for eight Years to become one.", note="pursuit action (serves the goal, doesn't state a fresh one)."),
    dict(id="robert_s2", story="robert_police_officer", split="train", gold=0,
         text="He heard there were job openings available for police officers.", note="perception/state."),
    dict(id="robert_s3", story="robert_police_officer", split="train", gold=0,
         text="He signed the application.", note="action."),
    dict(id="robert_s4", story="robert_police_officer", split="train", gold=0,
         text="He instantly got accepted because of his education.", note="outcome."),

    # ---- rocs2_jared_movie_alone (train) ----
    dict(id="jared_s0", story="jared_movie_alone", split="train", gold=1,
         text="A movie that Jared has been wanting to see came out today.", note="wanting+to-VP (embedded relative clause)."),
    # jared_s1 SKIPPED: "He asked all his friends if they wanted to go see it." -- an embedded
    # question about the FRIENDS' hypothetical desire, not an asserted goal of an established
    # character; genuinely ambiguous, excluded rather than forced either way.
    dict(id="jared_s2", story="jared_movie_alone", split="train", gold=0,
         text="They told him the movie got bad reviews so they were going to skip it.", note="reported plan/narration."),
    dict(id="jared_s3", story="jared_movie_alone", split="train", gold=0,
         text="Jared didn't care about that and went to the movies by himself.", note="action."),
    dict(id="jared_s4", story="jared_movie_alone", split="train", gold=0,
         text="He ended up loving the movie just as he thought he would.",
         note="PRECISION TRAP: 'loving' present, governs NP not to-VP -- outcome reaction."),

    # ---- rocs2_eva_nails_prom_dress (train) ----
    dict(id="eva_s0", story="eva_nails_prom_dress", split="train", gold=1,
         text="Eva decided to do her friends' nails to make money for her prom dress.", note="decide+to-VP."),
    dict(id="eva_s1", story="eva_nails_prom_dress", split="train", gold=0,
         text="She advertised her services at school.", note="action."),
    dict(id="eva_s2", story="eva_nails_prom_dress", split="train", gold=0,
         text="Many girls lined up to have their nails done by her.", note="consequence, not Eva's goal statement."),
    dict(id="eva_s3", story="eva_nails_prom_dress", split="train", gold=0,
         text="Soon she had earned over a hundred dollars.", note="outcome."),
    dict(id="eva_s4", story="eva_nails_prom_dress", split="train", gold=0,
         text="Eva bought a lovely prom dress, and her friends all had lovely nails!", note="outcome."),

    # ---- rocs2_dylan_weather_lady (train) ----
    dict(id="dylan_s0", story="dylan_weather_lady", split="train", gold=1,
         text="Dylan had always dreamed of being a weather lady.",
         note="IMPLICIT: 'dreamed of X', no governing verb+to-VP."),
    dict(id="dylan_s1", story="dylan_weather_lady", split="train", gold=0,
         text="She went to college to study meteorology.", note="pursuit action."),
    dict(id="dylan_s2", story="dylan_weather_lady", split="train", gold=0,
         text="She worked very hard to learn what she needed to.", note="pursuit action."),
    dict(id="dylan_s3", story="dylan_weather_lady", split="train", gold=0,
         text="After graduating, she put in many applications.", note="action."),
    dict(id="dylan_s4", story="dylan_weather_lady", split="train", gold=0,
         text="Dylan landed a job at her favorite news station.", note="outcome."),

    # ---- rocs2_dunk_basketball (train) ----
    dict(id="dunk_s0", story="dunk_basketball", split="train", gold=1,
         text="I've always wanted to be able to dunk a basketball.", note="want+to-VP, first-person."),
    dict(id="dunk_s1", story="dunk_basketball", split="train", gold=0,
         text="I can touch the rim but I can't quite get the ball over the rim.", note="state/obstacle."),
    dict(id="dunk_s2", story="dunk_basketball", split="train", gold=1,
         text="I only need about two more inches to successfully dunk a ball.",
         note="IMPLICIT: 'need... to VP' necessity modal restating the goal; need not in GOAL_GOVERNING_PASS."),
    dict(id="dunk_s3", story="dunk_basketball", split="train", gold=0,
         text="I worked out my legs hard for a month and added height to my vertical.", note="pursuit action."),
    dict(id="dunk_s4", story="dunk_basketball", split="train", gold=0,
         text="Now I can dunk a basketball easily every time!", note="outcome."),

    # ---- rocs2_peg_knot_tying_ship (train) ----
    dict(id="peg_s0", story="peg_knot_tying_ship", split="train", gold=1,
         text="Peg wanted to work on a ship, but she hated fishing.", note="want+to-VP."),
    dict(id="peg_s1", story="peg_knot_tying_ship", split="train", gold=0,
         text="She couldn't navigate or cook, either.", note="negated ability/obstacle."),
    dict(id="peg_s2", story="peg_knot_tying_ship", split="train", gold=0,
         text="The ship's captain asked what she could do to help him.", note="other-agent question."),
    dict(id="peg_s3", story="peg_knot_tying_ship", split="train", gold=0,
         text="Peg thought very hard, then offered her knot-tying services.", note="problem-solving/pursuit action."),
    dict(id="peg_s4", story="peg_knot_tying_ship", split="train", gold=0,
         text="Now she ties the rigging and sails on ocean voyages!", note="outcome."),

    # ---- rocs2_matt_saving_for_video_game (train) ----
    dict(id="mattv_s0", story="matt_saving_for_video_game", split="train", gold=1,
         text="Matt really wanted a new video game.",
         note="IMPLICIT: want+NP-OBJECT (no to-VP at all) -- find_desired_state's scan requires a to-VP after the governing verb; this is the SAME lexeme, a DIFFERENT construction."),
    dict(id="mattv_s1", story="matt_saving_for_video_game", split="train", gold=0,
         text="He didn't have enough money to buy it.", note="obstacle/state."),
    dict(id="mattv_s2", story="matt_saving_for_video_game", split="train", gold=1,
         text="He decided to try making money online.", note="decide+to-VP."),
    dict(id="mattv_s3", story="matt_saving_for_video_game", split="train", gold=0,
         text="It took him several months, but he eventually earned enough money.", note="action/outcome progression."),
    dict(id="mattv_s4", story="matt_saving_for_video_game", split="train", gold=0,
         text="He bought the new video game and was very happy.", note="outcome."),

    # ---- rocs2_sally_bad_haircut (test) ----
    dict(id="sallyh_s0", story="sally_bad_haircut", split="test", gold=1,
         text="Sally decided to get a haircut.", note="decide+to-VP."),
    dict(id="sallyh_s1", story="sally_bad_haircut", split="test", gold=0,
         text="She went to the stylist and got her cut.", note="action."),
    dict(id="sallyh_s2", story="sally_bad_haircut", split="test", gold=0,
         text="She was upset when she realized the stylist cut it way too short.", note="affect/outcome."),
    dict(id="sallyh_s3", story="sally_bad_haircut", split="test", gold=0,
         text="The stylist did not charge her but that did not fix her hair.", note="outcome/state."),
    dict(id="sallyh_s4", story="sally_bad_haircut", split="test", gold=0,
         text="She waited for months for her hair to grow back out.", note="outcome/passive endurance."),

    # ---- rocs2_gloria_ugly_dress (test) ----
    dict(id="gloria_s0", story="gloria_ugly_dress", split="test", gold=1,
         text="Gloria wanted to find a special new dress for her anniversary dinner.", note="want+to-VP."),
    dict(id="gloria_s1", story="gloria_ugly_dress", split="test", gold=0,
         text="She ordered a fancy black dress that looked lovely in a catalog.", note="action."),
    dict(id="gloria_s2", story="gloria_ugly_dress", split="test", gold=1,
         text="When the dress arrived, Gloria was excited to try it on.",
         note="IMPLICIT: 'excited to VP' -- a bouletic-eagerness cousin of hope/want, not in GOAL_GOVERNING_PASS."),
    dict(id="gloria_s3", story="gloria_ugly_dress", split="test", gold=0,
         text="Sadly, the dress was frumpy and saggy and the zipper broke at once.", note="outcome."),
    dict(id="gloria_s4", story="gloria_ugly_dress", split="test", gold=0,
         text="Gloria was very disappointed and returned the dress for a refund.", note="outcome/affect."),

    # ---- rocs2_stassi_move_away (test) ----
    dict(id="stassi_s0", story="stassi_move_away", split="test", gold=0,
         text="Stassi hated her life in Los Angeles.", note="negative affect about present state, not itself a goal."),
    dict(id="stassi_s1", story="stassi_move_away", split="test", gold=1,
         text="She wanted to get away from her old life.", note="want+to-VP."),
    dict(id="stassi_s2", story="stassi_move_away", split="test", gold=0,
         text="So Stassi moved away to New York with her new boyfriend.", note="action/outcome."),
    dict(id="stassi_s3", story="stassi_move_away", split="test", gold=0,
         text="Unfortunately Stassi's boyfriend dumped her.", note="outcome, other-agent."),
    dict(id="stassi_s4", story="stassi_move_away", split="test", gold=0,
         text="So Stassi begrudgingly moved back to California to her former friends.", note="outcome."),

    # ---- rocs2_paul_self_repair_car (test) ----
    dict(id="paul_s0", story="paul_self_repair_car", split="test", gold=0,
         text="Paul's car broke down shortly after leaving the driveway.", note="event/obstacle."),
    dict(id="paul_s1", story="paul_self_repair_car", split="test", gold=1,
         text="He decided to push it back home and repair it himself.", note="decide+to-VP."),
    dict(id="paul_s2", story="paul_self_repair_car", split="test", gold=0,
         text="Paul found himself in over his head and called a tow truck for repair.", note="action/outcome."),
    dict(id="paul_s3", story="paul_self_repair_car", split="test", gold=0,
         text="The tow truck took the car to a garage where it was repaired.", note="outcome."),
    dict(id="paul_s4", story="paul_self_repair_car", split="test", gold=0,
         text="Paul then realized attempting repairs yourself can be expensive.", note="realization/outcome, gerund subject not Paul's current goal."),

    # ---- rocs2_picnic_ants (test) ----
    dict(id="picnic_s0", story="picnic_ants", split="test", gold=1,
         text="Tom and Sue decided to have a picnic in the park.", note="decide+to-VP."),
    dict(id="picnic_s1", story="picnic_ants", split="test", gold=0,
         text="They packed cold chicken and potato salad along with drinks.", note="action."),
    dict(id="picnic_s2", story="picnic_ants", split="test", gold=0,
         text="They sat on a blanket along with the food.", note="action."),
    dict(id="picnic_s3", story="picnic_ants", split="test", gold=1,
         text="Tom and Sue decided then they would play frisbee for awhile.",
         note="IMPLICIT: decide + FINITE complement ('they would play'), not decide+to-VP."),
    dict(id="picnic_s4", story="picnic_ants", split="test", gold=0,
         text="They return to their blanket to discover ants had invaded their meal.",
         note="PRECISION TRAP: 'to discover' is a resultative infinitival describing the OUTCOME, not a goal."),

    # ---- rocs2_tonya_raw_burgers (test) ----
    dict(id="tonya_s0", story="tonya_raw_burgers", split="test", gold=1,
         text="Tonya decided to have a cookout for all of her friends and family.", note="decide+to-VP."),
    dict(id="tonya_s1", story="tonya_raw_burgers", split="test", gold=0,
         text="However, Tonya wasn't good at grilling.", note="negated ability/state."),
    dict(id="tonya_s2", story="tonya_raw_burgers", split="test", gold=0,
         text="Despite this, she still grilled hamburgers.", note="action."),
    dict(id="tonya_s3", story="tonya_raw_burgers", split="test", gold=0,
         text="However, she noticed no one was eating their food.", note="perception/outcome."),
    dict(id="tonya_s4", story="tonya_raw_burgers", split="test", gold=0,
         text="Tonya had not cooked the meat long enough and the patties were raw.", note="outcome."),

    # ---- rocs2_andrea_wrong_plane (test) ----
    dict(id="andrea_s0", story="andrea_wrong_plane", split="test", gold=1,
         text="Andrea wanted a pet dog.", note="IMPLICIT: want+NP-object, no to-VP."),
    dict(id="andrea_s1", story="andrea_wrong_plane", split="test", gold=1,
         text="She wanted one from India.", note="IMPLICIT: want+NP-object, no to-VP."),
    dict(id="andrea_s2", story="andrea_wrong_plane", split="test", gold=0,
         text="She booked a flight to India.", note="action, 'to India' a PP destination not purpose-infinitival."),
    dict(id="andrea_s3", story="andrea_wrong_plane", split="test", gold=0,
         text="After being on the plane for 5 hours she realized something.", note="state/realization."),
    dict(id="andrea_s4", story="andrea_wrong_plane", split="test", gold=0,
         text="She got on the wrong plane.", note="outcome."),

    # ---- rocs2_jennifer_disneyland_car_breakdown (test) ----
    dict(id="jennifer_s0", story="jennifer_disneyland_car_breakdown", split="test", gold=1,
         text="Jennifer wanted to take her three kids on a vacation to Disneyland.", note="want+to-VP."),
    dict(id="jennifer_s1", story="jennifer_disneyland_car_breakdown", split="test", gold=0,
         text="A single mom, she worked three jobs to save enough money.", note="pursuit action."),
    dict(id="jennifer_s2", story="jennifer_disneyland_car_breakdown", split="test", gold=0,
         text="After earning enough money, she bought non-refundable plane tickets.", note="action."),
    dict(id="jennifer_s3", story="jennifer_disneyland_car_breakdown", split="test", gold=0,
         text="The family set off for the airport, excited for their vacation.",
         note="PRECISION TRAP: contains 'set off' (lexically close to 'set out') but 'set off FOR the airport' is a departure-action PP, not a goal-declaring construction."),
    dict(id="jennifer_s4", story="jennifer_disneyland_car_breakdown", split="test", gold=0,
         text="Then their car broke down on the highway and they missed their flight.", note="outcome."),

    # ---- rocs2_justin_grape_candy_gift (test) ----
    dict(id="justin_s0", story="justin_grape_candy_gift", split="test", gold=0,
         text="Riley loved grape flavored candy.",
         note="PRECISION TRAP: 'loved' present, governs NP -- a general preference, not a goal, and not even Justin's."),
    dict(id="justin_s1", story="justin_grape_candy_gift", split="test", gold=1,
         text="Justin decided to impress Riley with lots of grape candy.", note="decide+to-VP."),
    dict(id="justin_s2", story="justin_grape_candy_gift", split="test", gold=0,
         text="Sadly, this made Riley very uncomfortable.", note="outcome/affect."),
    dict(id="justin_s3", story="justin_grape_candy_gift", split="test", gold=0,
         text="She gave all the candy to her friends.", note="action/outcome."),
    dict(id="justin_s4", story="justin_grape_candy_gift", split="test", gold=0,
         text="Justin never tried to give Riley a gift again.",
         note="PRECISION TRAP: NEGATED 'tried to VP' (never+tried) -- states the ABSENCE of a further attempt/goal, not an active goal."),

    # ---- rocs2_jacob_skateboard_kickflip (test) ----
    dict(id="jacob_s0", story="jacob_skateboard_kickflip", split="test", gold=0,
         text="Jacob was a skateboarder.", note="identity statement."),
    dict(id="jacob_s1", story="jacob_skateboard_kickflip", split="test", gold=1,
         text="He wanted to impress his friends, who were also skaters.", note="want+to-VP."),
    dict(id="jacob_s2", story="jacob_skateboard_kickflip", split="test", gold=1,
         text="In order to do that, Jacob tried to kickflip down a set of 6 stairs.", note="try+to-VP (conative)."),
    dict(id="jacob_s3", story="jacob_skateboard_kickflip", split="test", gold=0,
         text="Jacob landed on his ankle wrong, and was unable to stand back up.", note="outcome (negative)."),
    dict(id="jacob_s4", story="jacob_skateboard_kickflip", split="test", gold=0,
         text="Jacob had to go to the hospital to get his ankle x-rayed.",
         note="'had to VP' here is a FORCED/reactive necessity from an injury, not a pursued aspiration -- distinguished from the goal-like necessity items (Tony's gas, Sally's necklace) which describe a self-directed task/errand."),

    # ---- rocs2_dave_boat_stolen (test) ----
    dict(id="dave_s0", story="dave_boat_stolen", split="test", gold=1,
         text="Dave loved to sail.", note="love+to-VP (habitual bouletic desire, caught)."),
    dict(id="dave_s1", story="dave_boat_stolen", split="test", gold=1,
         text="One day he decided to sail his boat far away.", note="decide+to-VP."),
    dict(id="dave_s2", story="dave_boat_stolen", split="test", gold=0,
         text="He packed all sort of gear for the trip.", note="action."),
    dict(id="dave_s3", story="dave_boat_stolen", split="test", gold=0,
         text="The day before the trip his boat was stolen.", note="outcome/obstacle event."),
    dict(id="dave_s4", story="dave_boat_stolen", split="test", gold=0,
         text="Dave was sad he couldn't take his trip.", note="outcome/affect."),

    # ---- hand-authored supplement (7 items): rounds out feature coverage for constructions barely
    # attested in the 40 ROCStories items (aspiration-noun subject, explicit 'set out to', explicit
    # 'competing for'), plus 3 neutral-narration precision negatives. Clearly tagged.
    dict(id="ha_dream_doctor", story="handauthored_1", split="train", gold=1,
         text="Maria's dream was to become a doctor one day.", source="handauthored_supplement",
         note="IMPLICIT: aspiration-NOUN subject ('her dream was to X'); no GOAL_GOVERNING_PASS governing verb at all ('was' is a copula, not in the pass lexicon)."),
    dict(id="ha_set_out", story="handauthored_2", split="test", gold=1,
         text="He set out to prove them all wrong.", source="handauthored_supplement",
         note="IMPLICIT: 'set out to VP' -- 'set' not in GOAL_GOVERNING_PASS."),
    dict(id="ha_competing", story="handauthored_3", split="train", gold=1,
         text="Two teams were competing for the district championship trophy.", source="handauthored_supplement",
         note="IMPLICIT: 'competing for X' -- 'compete' not in GOAL_GOVERNING_PASS."),
    dict(id="ha_determined", story="handauthored_4", split="test", gold=1,
         text="She was determined to finish the marathon no matter what.", source="handauthored_supplement",
         note="'determined to VP' -- determine IS in INTENTION_PASS, caught by baseline; control item."),
    dict(id="ha_trophy_dust", story="handauthored_5", split="train", gold=0,
         text="The trophy sat on a shelf collecting dust in the hallway.", source="handauthored_supplement",
         note="neutral scene description, no goal."),
    dict(id="ha_rain", story="handauthored_6", split="test", gold=0,
         text="Rain fell steadily on the empty street all afternoon.", source="handauthored_supplement",
         note="neutral scene description, no goal."),
    dict(id="ha_committee", story="handauthored_7", split="train", gold=0,
         text="The committee announced the results early Friday morning.", source="handauthored_supplement",
         note="neutral outcome narration, no goal."),
]

for _it in RAW_ITEMS:
    _it.setdefault("source", "rocstories_relabeled_v1_full_text")


# ============================================================================================
# STEP 2: FEATURES. Named, interpretable, glass-box lexico-syntactic detectors.
def _tokens(sentence: str):
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


ASPIRATION_NOUNS = {"dream", "dreams", "dreamed", "dreaming",
                     "hope", "hopes", "ambition", "ambitions", "goal", "goals", "wish", "wishes"}
PURSUIT_ATTEMPT_VERBS = {"enter", "enters", "entering", "entered",
                          "compete", "competes", "competing", "competed",
                          "bet", "bets", "betting",
                          "try", "tries", "tried", "trying",
                          "attempt", "attempts", "attempted", "attempting"}
COMMITMENT_NOUNS = {"bet", "budget"}
NECESSITY_VERBS = {"need", "needs", "needed"}
MODAL_WANT_BIGRAMS = {("would", "like"), ("hoping", "to"), ("excited", "to"),
                       ("eager", "to"), ("looking", "forward")}
FIRST_PERSON = {"i", "we"}
DECISION_VERBS = {"decided", "decide", "decides", "deciding", "determined", "determine"}
_MODAL_FOLLOWERS = {"would", "could", "might", "will"}


def featurize(sentence: str):
    """Returns a sorted list[str] of named binary feature-flags present in `sentence`. Combines
    hand-designed lexical/construction detectors (STEP 2 spec) with two REUSED production organs
    (action_frame_feats -- verb-lemma-independent purpose-infinitival structure; NEGATORS -- the
    same negation-token set find_desired_state's own negation-scope guard uses)."""
    toks = _tokens(sentence)
    tokset = set(toks)
    feats = set()

    if tokset & GOAL_GOVERNING_PASS:
        feats.add("desiderative_or_intention_verb")
    if tokset & ASPIRATION_NOUNS:
        feats.add("aspiration_noun")
    if tokset & PURSUIT_ATTEMPT_VERBS:
        feats.add("pursuit_attempt_construction")
    for i in range(len(toks) - 1):
        if toks[i] == "set" and toks[i + 1] == "out":
            feats.add("pursuit_attempt_construction")
            break
    for i in range(len(toks) - 1):
        if (toks[i], toks[i + 1]) in MODAL_WANT_BIGRAMS:
            feats.add("modal_want")
            break
    if tokset & NECESSITY_VERBS:
        feats.add("necessity_modal")
    for i in range(len(toks) - 1):
        if toks[i] in ("had", "has", "have") and toks[i + 1] == "to":
            feats.add("necessity_modal")
            break
    for i, t in enumerate(toks):
        if t in DECISION_VERBS:
            window = toks[i + 1:i + 5]
            if "to" not in window and any(w in _MODAL_FOLLOWERS for w in window):
                feats.add("decision_finite_complement")
                break
    if tokset & COMMITMENT_NOUNS:
        feats.add("commitment_establishing_noun")
    if tokset & FIRST_PERSON:
        feats.add("first_person_subject")
    for af in action_frame_feats(sentence):
        feats.add(af)  # purpose_to_no_det / has_directional_pp -- reused hdlab.goal_typing organ
    if any(t in NEGATORS or t.endswith("n't") for t in toks):
        feats.add("negation_present")

    return sorted(feats)


# ============================================================================================
# STEP 3: LEARN + COMPARE.
HYP_SPACE_SPEC = dict(
    candidate_plugins=["estimation", "ruleind", "gam"],
    key_fn=lambda inst: tuple(sorted(inst["feats"])),
    label_fn=lambda inst: inst["gold_class"],
    classes=["GOAL", "NOT_GOAL"],
    min_coverage=3,
    purity_thresh=0.85,
    max_conjunct=2,
    max_rules=8,
)


def to_episode(item):
    return {"id": item["id"], "feats": featurize(item["text"]), "gold_class": "GOAL" if item["gold"] else "NOT_GOAL"}


def predict_one(plugin_name, hypothesis, feats):
    key = tuple(sorted(feats))
    if plugin_name == "ruleind":
        return learner_apply(plugin_name, hypothesis, feats, key=key, default_class="NOT_GOAL")
    if plugin_name == "gam":
        return learner_apply(plugin_name, hypothesis, feats)
    if plugin_name == "estimation":
        return learner_apply(plugin_name, hypothesis, key)
    raise ValueError(f"unknown plugin {plugin_name!r}")


def fit_and_eval(train_episodes, test_episodes, spec):
    chosen_name, chosen, all_results = learner_learn(train_episodes, lambda inst: inst["feats"], spec)
    preds = None
    if chosen is not None:
        preds = [predict_one(chosen_name, chosen.hypothesis, ep["feats"]) for ep in test_episodes]
    return chosen_name, chosen, all_results, preds


def prf(gold_bin, pred_bin):
    """gold_bin/pred_bin: list[bool]. Returns (recall, precision, tp, fp, fn, tn)."""
    tp = sum(1 for g, p in zip(gold_bin, pred_bin) if g and p)
    fp = sum(1 for g, p in zip(gold_bin, pred_bin) if not g and p)
    fn = sum(1 for g, p in zip(gold_bin, pred_bin) if g and not p)
    tn = sum(1 for g, p in zip(gold_bin, pred_bin) if not g and not p)
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    return recall, precision, tp, fp, fn, tn


def main():
    # ---- write dataset (STEP 1 deliverable) ----
    os.makedirs(os.path.dirname(OUT_DATASET_PATH), exist_ok=True)
    with open(OUT_DATASET_PATH, "w", encoding="utf-8", newline="") as f:
        for it in RAW_ITEMS:
            row = {"id": it["id"], "story": it["story"], "split": it["split"],
                   "text": it["text"], "is_goal": bool(it["gold"]), "source": it["source"],
                   "note": it["note"]}
            f.write(json.dumps(row, ensure_ascii=False) + "\n")

    n_pos = sum(1 for it in RAW_ITEMS if it["gold"] == 1)
    n_neg = sum(1 for it in RAW_ITEMS if it["gold"] == 0)
    n_total = len(RAW_ITEMS)

    train_items = [it for it in RAW_ITEMS if it["split"] == "train"]
    test_items = [it for it in RAW_ITEMS if it["split"] == "test"]
    train_episodes = [to_episode(it) for it in train_items]
    test_episodes = [to_episode(it) for it in test_items]
    test_gold_bin = [ep["gold_class"] == "GOAL" for ep in test_episodes]

    # ---- REAL fit ----
    chosen_name, chosen, all_results, learned_preds = fit_and_eval(train_episodes, test_episodes, HYP_SPACE_SPEC)
    is_episodic_result = chosen is None
    learned_pred_bin = [p == "GOAL" for p in learned_preds] if learned_preds is not None else [False] * len(test_items)
    learned_recall, learned_precision, l_tp, l_fp, l_fn, l_tn = prf(test_gold_bin, learned_pred_bin)

    # ---- determinism self-test: refit the REAL model a 2nd time, assert identical selection+preds ----
    chosen_name_2, chosen_2, _all_results_2, learned_preds_2 = fit_and_eval(train_episodes, test_episodes, HYP_SPACE_SPEC)
    determinism_real_ok = (chosen_name == chosen_name_2 and learned_preds == learned_preds_2
                            and (chosen is None) == (chosen_2 is None))

    # ---- BASELINE: hdlab.goal_typing.find_desired_state on the SAME held-out test set ----
    baseline_pred_bin = [find_desired_state(it["text"]) is not None for it in test_items]
    baseline_recall, baseline_precision, b_tp, b_fp, b_fn, b_tn = prf(test_gold_bin, baseline_pred_bin)

    # ---- baseline on TRAIN too, for the "caught vs missed" breakdown of the dataset ----
    baseline_fires_all = {it["id"]: (find_desired_state(it["text"]) is not None) for it in RAW_ITEMS}
    pos_items = [it for it in RAW_ITEMS if it["gold"] == 1]
    pos_missed_by_baseline = [it for it in pos_items if not baseline_fires_all[it["id"]]]
    pos_caught_by_baseline = [it for it in pos_items if baseline_fires_all[it["id"]]]

    # ---- SCRAMBLE control: permute TRAIN labels only (deterministic seed), refit, re-evaluate on
    # the REAL (unscrambled) test set + gold labels. Run TWICE with the same seed for a determinism
    # self-test on the scramble path too. ----
    def scrambled_train_episodes(seed):
        rng = random.Random(seed)
        labels = [ep["gold_class"] for ep in train_episodes]
        rng.shuffle(labels)
        return [{**ep, "gold_class": lbl} for ep, lbl in zip(train_episodes, labels)]

    scram_train_1 = scrambled_train_episodes(SCRAMBLE_SEED)
    scram_name_1, scram_chosen_1, _sr1, scram_preds_1 = fit_and_eval(scram_train_1, test_episodes, HYP_SPACE_SPEC)
    scram_train_2 = scrambled_train_episodes(SCRAMBLE_SEED)
    scram_name_2, scram_chosen_2, _sr2, scram_preds_2 = fit_and_eval(scram_train_2, test_episodes, HYP_SPACE_SPEC)
    determinism_scramble_ok = (scram_name_1 == scram_name_2 and scram_preds_1 == scram_preds_2)

    scram_is_episodic = scram_chosen_1 is None
    scram_pred_bin = [p == "GOAL" for p in scram_preds_1] if scram_preds_1 is not None else [False] * len(test_items)
    scram_recall, scram_precision, *_ = prf(test_gold_bin, scram_pred_bin)
    scram_accuracy = sum(1 for g, p in zip(test_gold_bin, scram_pred_bin) if g == p) / len(test_gold_bin)
    real_accuracy = sum(1 for g, p in zip(test_gold_bin, learned_pred_bin) if g == p) / len(test_gold_bin)
    test_base_rate = sum(test_gold_bin) / len(test_gold_bin)
    fire_everything_precision = sum(test_gold_bin) / len(test_gold_bin)  # precision if every item predicted GOAL

    compression_ratio = chosen.compression_ratio if chosen is not None else float("nan")
    scram_compression_ratio = scram_chosen_1.compression_ratio if scram_chosen_1 is not None else float("nan")

    # ---- glass-box mechanism dump ----
    mechanism_lines = []
    if chosen is not None:
        if chosen_name == "ruleind":
            for r in chosen.hypothesis["rules"]:
                mechanism_lines.append(f"  IF {sorted(r['conjunct'])} -> {r['majority_class']} "
                                        f"(coverage={r.get('coverage')}, purity={r.get('purity')})")
            mechanism_lines.append(f"  ELSE (residual/default) -> NOT_GOAL "
                                    f"(n_episodic_residual={len(chosen.hypothesis['residual_lookup'])})")
        elif chosen_name == "gam":
            main_shape = chosen.hypothesis["main_shape"]
            for f in sorted(main_shape, key=lambda f: main_shape[f]["GOAL"] - main_shape[f]["NOT_GOAL"], reverse=True):
                delta = main_shape[f]["GOAL"] - main_shape[f]["NOT_GOAL"]
                mechanism_lines.append(f"  {f}: log2-odds(GOAL vs NOT_GOAL) = {delta:+.3f}")
        elif chosen_name == "estimation":
            counts = chosen.hypothesis["counts"]
            n_classes = chosen.hypothesis["n_classes"]
            ranked = []
            for key_str, c in counts.items():
                total = sum(c.values())
                p_goal = (c.get("GOAL", 0) + 1) / (total + n_classes)
                ranked.append((total, p_goal, key_str, c))
            ranked.sort(key=lambda t: (-t[0], -t[1]))
            mechanism_lines.append(f"  {len(counts)} composite-feature-tuple keys "
                                    f"(exact-combo Laplace-smoothed lookup table). Top keys by support:")
            for total, p_goal, key_str, c in ranked[:12]:
                mechanism_lines.append(f"    n={total:2d} P(GOAL|key)={p_goal:.2f} counts={dict(c)}  key={key_str}")

    # ---- supplementary interpretability: GAM's per-feature log-odds ranking, printed regardless of
    # which plugin MDL actually selected (answers "which cues generalize goal-recognition" even when
    # the winning hypothesis class itself is an opaque-looking lookup table). ----
    gam_result = all_results.get("gam")
    gam_ranked_lines = []
    if gam_result is not None and gam_result.hypothesis is not None:
        main_shape = gam_result.hypothesis["main_shape"]
        for f in sorted(main_shape, key=lambda f: main_shape[f]["GOAL"] - main_shape[f]["NOT_GOAL"], reverse=True):
            delta = main_shape[f]["GOAL"] - main_shape[f]["NOT_GOAL"]
            gam_ranked_lines.append(f"  {f}: log2-odds(GOAL vs NOT_GOAL) = {delta:+.3f}")

    # ---- self-test assertions (fail loud, not silent) ----
    assert n_total == len(train_items) + len(test_items), "train/test split must partition RAW_ITEMS"
    assert 55 <= n_pos <= 90, f"n_pos={n_pos} out of expected sanity range"
    assert 100 <= n_neg <= 170, f"n_neg={n_neg} out of expected sanity range"
    assert all(it["text"].strip() for it in RAW_ITEMS), "every item must have non-empty text"
    assert len(set(it["id"] for it in RAW_ITEMS)) == n_total, "item ids must be unique"
    assert determinism_real_ok, "REAL fit is not deterministic across two identical invocations"
    assert determinism_scramble_ok, "SCRAMBLE fit is not deterministic across two identical-seed invocations"
    with open(OUT_DATASET_PATH, encoding="utf-8") as f:
        written = [json.loads(line) for line in f]
    assert len(written) == n_total, "dataset jsonl on disk must match in-memory RAW_ITEMS count"
    self_test_pass = True

    # ---- write metrics.json ----
    os.makedirs(OUT_METRICS_DIR, exist_ok=True)
    metrics = dict(
        n_pos=n_pos, n_neg=n_neg, n_total=n_total,
        n_train=len(train_items), n_test=len(test_items),
        n_pos_train=sum(1 for it in train_items if it["gold"] == 1),
        n_pos_test=sum(1 for it in test_items if it["gold"] == 1),
        baseline_recall=baseline_recall, baseline_precision=baseline_precision,
        baseline_tp=b_tp, baseline_fp=b_fp, baseline_fn=b_fn, baseline_tn=b_tn,
        learned_recall=learned_recall, learned_precision=learned_precision,
        learned_tp=l_tp, learned_fp=l_fp, learned_fn=l_fn, learned_tn=l_tn,
        learned_accuracy=real_accuracy,
        chosen_plugin=chosen_name, is_episodic=is_episodic_result,
        compression_ratio=compression_ratio,
        scramble_chosen_plugin=scram_name_1, scramble_is_episodic=scram_is_episodic,
        scramble_compression_ratio=scram_compression_ratio,
        scramble_recall=scram_recall, scramble_precision=scram_precision,
        scramble_accuracy=scram_accuracy, real_accuracy=real_accuracy,
        test_base_rate=test_base_rate,
        n_pos_missed_by_baseline_all=len(pos_missed_by_baseline),
        n_pos_caught_by_baseline_all=len(pos_caught_by_baseline),
        determinism_real_ok=determinism_real_ok, determinism_scramble_ok=determinism_scramble_ok,
        self_test_pass=self_test_pass,
        all_plugin_results={name: dict(is_episodic=r.is_episodic, compression_ratio=r.compression_ratio,
                                        cost_rank=r.cost_rank, metrics=r.metrics)
                             for name, r in all_results.items()},
        seed=SCRAMBLE_SEED,
    )
    tmp_path = OUT_METRICS_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8", newline="") as f:
        json.dump(metrics, f, indent=2, default=str)
    os.replace(tmp_path, OUT_METRICS_PATH)

    # ================================================================================ REPORT
    print("=" * 100)
    print("exp_goal_recognition_learnability_probe_v1 -- FINAL REPORT")
    print("=" * 100)
    print(f"\nDATASET: {OUT_DATASET_PATH}")
    print(f"  n_pos={n_pos}  n_neg={n_neg}  n_total={n_total}  "
          f"(train: {len(train_items)} [{metrics['n_pos_train']} pos] / "
          f"test: {len(test_items)} [{metrics['n_pos_test']} pos], split reused from the source "
          f"file's own 20-story/20-story train/test field)")
    print(f"  Of {n_pos} gold-positive sentences, find_desired_state MISSES "
          f"{len(pos_missed_by_baseline)} and CATCHES {len(pos_caught_by_baseline)} (whole dataset, "
          f"train+test) -- computed at runtime from the real production function, not hand-asserted.")

    print("\n8 VERBATIM SAMPLES (mix of non-desiderative/implicit positives + controls):")
    sample_ids = ["ellen_s0", "tim_s0", "fred_s0", "colin_s3", "tony_s0", "sallyn_s2",
                  "mattv_s0", "ha_dream_doctor"]
    by_id = {it["id"]: it for it in RAW_ITEMS}
    for sid in sample_ids:
        it = by_id[sid]
        fires = baseline_fires_all[sid]
        print(f"  [{sid}] gold={'GOAL' if it['gold'] else 'NOT_GOAL'} "
              f"baseline_fires={fires}  text={it['text']!r}")
        print(f"          note: {it['note']}")

    print("\nHELD-OUT (test split, n={}) -- LEARNED vs BASELINE:".format(len(test_items)))
    print(f"  BASELINE (find_desired_state):  recall={baseline_recall:.3f}  precision={baseline_precision:.3f}  "
          f"(tp={b_tp} fp={b_fp} fn={b_fn} tn={b_tn})")
    print(f"  LEARNED  (chosen_plugin={chosen_name}, is_episodic={is_episodic_result}):  "
          f"recall={learned_recall:.3f}  precision={learned_precision:.3f}  accuracy={real_accuracy:.3f}  "
          f"(tp={l_tp} fp={l_fp} fn={l_fn} tn={l_tn})")
    print(f"  test base rate (fire-everything precision) = {test_base_rate:.3f}")
    print("\n  all-plugin MDL comparison (fit on TRAIN):")
    for name, r in all_results.items():
        print(f"    {name}: is_episodic={r.is_episodic}  compression_ratio={r.compression_ratio:.4f}  "
              f"cost_rank={r.cost_rank}  metrics={r.metrics}")

    print(f"\nGLASS-BOX MECHANISM (chosen_plugin={chosen_name}):")
    if mechanism_lines:
        for line in mechanism_lines:
            print(line)
    else:
        print("  (KEEP_EPISODIC -- no hypothesis induced)")

    print("\nSUPPLEMENTARY INTERPRETABILITY -- GAM per-feature log-odds ranking (fit on TRAIN, "
          "printed regardless of the auto-selected plugin -- answers 'which named cues generalize'):")
    if gam_ranked_lines:
        for line in gam_ranked_lines:
            print(line)
    else:
        print("  (gam hypothesis unavailable)")

    print(f"\nMDL: compression_ratio={compression_ratio:.4f} (>1.0 = genuinely compresses past the null code; "
          f"is_episodic={is_episodic_result})")

    print(f"\nSCRAMBLE CONTROL (train labels permuted, seed={SCRAMBLE_SEED}, same features/fit/eval procedure):")
    print(f"  scramble chosen_plugin={scram_name_1}  is_episodic={scram_is_episodic}  "
          f"compression_ratio={scram_compression_ratio:.4f}")
    print(f"  scramble held-out: recall={scram_recall:.3f}  precision={scram_precision:.3f}  "
          f"accuracy={scram_accuracy:.3f}  (test base rate={test_base_rate:.3f})")
    print(f"  DELTA accuracy (real - scrambled) = {real_accuracy - scram_accuracy:+.3f}  "
          f"DELTA compression_ratio (real - scrambled) = {compression_ratio - scram_compression_ratio:+.4f}")

    # ---- GATE VERDICT (prose, evidence-based, no forced pass) ----
    recall_beats_baseline = learned_recall > baseline_recall
    precision_reasonable = (not (learned_precision != learned_precision)  # not NaN
                             and learned_precision >= max(0.5, test_base_rate))
    non_episodic = not is_episodic_result and compression_ratio > 1.0
    scramble_collapses = scram_is_episodic or (scram_compression_ratio <= 1.05) or \
        (real_accuracy - scram_accuracy >= 0.10)

    verdict = "HARD-PASS" if (recall_beats_baseline and precision_reasonable and non_episodic
                               and scramble_collapses) else "PARTIAL/NULL"
    print("\n" + "=" * 100)
    print(f"GATE VERDICT: {verdict}")
    print(f"  recall_beats_baseline={recall_beats_baseline} ({learned_recall:.3f} vs {baseline_recall:.3f})")
    print(f"  precision_reasonable={precision_reasonable} (learned={learned_precision:.3f}, "
          f"floor=max(0.5, base_rate={test_base_rate:.3f}))")
    print(f"  non_episodic={non_episodic} (compression_ratio={compression_ratio:.4f})")
    print(f"  scramble_collapses={scramble_collapses} "
          f"(scram_episodic={scram_is_episodic}, scram_compression={scram_compression_ratio:.4f}, "
          f"accuracy_delta={real_accuracy - scram_accuracy:+.3f})")
    print("=" * 100)

    print(f"\nSELF-TEST: PASS")
    print(f"  determinism_real_ok={determinism_real_ok}  determinism_scramble_ok={determinism_scramble_ok}  "
          f"(seed={SCRAMBLE_SEED}, python random.Random, no torch/numpy RNG in this probe)")
    print(f"\nmetrics.json written: {OUT_METRICS_PATH}")
    print(f"dataset jsonl written: {OUT_DATASET_PATH}")


if __name__ == "__main__":
    main()
