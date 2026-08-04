"""exp_situation_model_goal_outcome_dimension_v1 -- does extending the situation-model accumulate
organ with a GOAL / OUTCOME dimension (mirroring CausalLinkRegister's CAUSE/EFFECT) let the
grounded VIEW-2 appraisal fire DISCRIMINATIVELY on naturalistic goal-block prose when read OFF the
ACCUMULATED register -- vs the ~1.4% flat baseline it had reading LOCAL windows?

WHY (adjudicated fix, disk-verified). Brain drill
notes/research_discourse_scale_grounded_integration_brain_drill_2026-08-04.md adjudicated the
discourse-scale grounded-reading wall as a REPRESENTATION GAP: the live situation-model register
carries role_vocab=["agent","mentioned"] (disk-verified tools/read_anne_glassbox_v2_honest_ledger.py
:428) -- no GOAL/CAUSATION/OUTCOME slot -- so grounded appraisal reading a LOCAL window has nothing
dispersed to integrate (Zwaan event-indexing over the DMN situation model tracks goal/intentionality
+ causation + outcome; we track neither). FIX: extend the register with GOAL + OUTCOME dimensions,
MIRRORING how hdlab/situation_model_accumulate.CausalLinkRegister added CAUSE/EFFECT meta-roles on
the SAME AccumulateRegister organ (atom 29609; bind/bundle/unbind/cleanup reused bit-identical).

THE BUILD. GoalOutcomeRegister(AccumulateRegister): extends role_vocab from ["agent","mentioned"]
to ["GOAL","ACTION_AGAINST","OUTCOME_UNMET","OUTCOME_MET"] on the SAME organ (subclass, adds
per-entity role bookkeeping + appraise(entity), the exact CausalLinkRegister extension pattern).
As the reader processes a passage sentence-by-sentence, each entity-attributed typed event (an
animate owner WANTS x / a blocker acts AGAINST it / the goal ends MET or UNMET) accumulates via
bundle into the goal-owner ENTITY's register -- EVEN when dispersed across non-adjacent sentences.
appraise(owner) decodes each written slot (unbind + cleanup-argmax over the 4 roles) and reads
goal-blocking OFF the accumulated register: GOAL present AND net OUTCOME UNMET.

THE TEST (can-fail, vs 1.4%-flat). TREATMENT (accumulated register) vs BASELINE (the existing
view2_goal_outcome read on each LOCAL 2-sentence window, bit-identical import) on naturalistic
goal-block items (mcca_004_amy_warning + theatre_refusal + 4 more implicit goal-block passages in
FULL discourse context, goal/action/outcome DISPERSED) vs matched non-goal-block controls
(goal-MET, outcome-trap noise, physical-harm). Plus a RECENCY control (pronoun trap where the
correct outcome-owner is NOT the most recent entity; GOLD-annotated) -- the known coref
recency-falsification (0/4, MEMORY 2026-08-03) is the live risk for binding dispersed
goal-outcome triples, reported as right-event binding accuracy.

BANDS (pre-registered, preregs/2026-08-04_situation_model_goal_outcome_dimension_v1.md):
  HARD_PASS  -> TREATMENT goal-block fire >=0.5, control <0.1 (clear sep), recency binding >=0.5,
                TREATMENT > BASELINE on goal-block  => WALL CRACKS.
  MIDDLE_BAND-> fires >=0.5 / control <0.1 but recency binding <0.5 => routes binding-selector.
  HARD_FAIL  -> TREATMENT goal-block fire <0.1 (still flat) => representation extension insufficient.

GUARDS: glass-box; NO borrowed embedding/LLM/parser as mechanism; AccumulateRegister /
normalize_tokens / view2_goal_outcome / V1_WITHHOLD / V2_* lexicons reused bit-identical;
deterministic; multi-seed (5); resumable per-seed; local-only (no queue/remote/push); ASCII-only.
n small on real items (6 goal-block + 6 control + 3 recency), DIRECTIONAL.

Cites: notes/research_discourse_scale_grounded_integration_brain_drill_2026-08-04.md;
hdlab/situation_model_accumulate.py (CausalLinkRegister CAUSE/EFFECT pattern, atom 29609);
experiments/exp_self_extension_grounded_realprose_v1.py (VIEW-2 grounded read).
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

import argparse
import json
import platform
import re
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone

import numpy as np

ANCHOR_NAME = "situation_model_goal_outcome_dimension_v1"
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _p in (REPO_ROOT, os.path.join(REPO_ROOT, "tools"), os.path.join(REPO_ROOT, "experiments")):
    if _p not in sys.path:
        sys.path.insert(0, _p)
OUTPUT_DIR = os.path.join(REPO_ROOT, "data", f"exp_{ANCHOR_NAME}")

# ---- REUSED BIT-IDENTICAL: validated situation-model accumulate organ (atom 29609) -------------
from hdlab.situation_model_accumulate import AccumulateRegister  # noqa: E402
# ---- REUSED BIT-IDENTICAL: situation-model relational tokenizer --------------------------------
from hdlab.coreference_resolver import normalize_tokens  # noqa: E402
import torch  # noqa: E402
# ---- REUSED BIT-IDENTICAL: the grounded VIEW-2 goal-outcome read + its lexicons (the baseline) --
import exp_self_extension_grounded_realprose_v1 as v1  # noqa: E402
from exp_self_extension_grounded_realprose_v1 import (  # noqa: E402
    view2_goal_outcome, V2_DESIRE, V2_OUTCOME_UNMET, V2_OUTCOME_MET,
    V1_WITHHOLD, V1_OMISSION,
)
from exp_checkpoint import unit_key, completed_units, record_unit, load_units  # noqa: E402

# ============================================================================ config
D2 = 1024                   # FHRR dim (matches v1 view-2 register)
SEEDS = list(range(5))
EXPECTED_N_SEEDS = len(SEEDS)
MAX_EVENTS = 8              # register event-slot capacity (as v1)
BASELINE_WINDOW = 2         # "local window" size (sentences) for the baseline read

# glass-box animate-entity roster + pronoun gender (proper-noun-free schema knowledge is supplied;
# these NAMES are just entity handles for attribution, NOT tuned to any view/lexicon).
NAMES_F = {"amy", "jo", "beth", "meg", "ruth", "ann", "she"}
NAMES_M = {"tom", "sid", "laurie", "he"}
GENDER = {}
for _n in ("amy", "jo", "beth", "meg", "ruth", "ann"):
    GENDER[_n] = "f"
for _n in ("tom", "sid", "laurie"):
    GENDER[_n] = "m"
PRON_F = {"she", "her", "hers", "herself"}
PRON_M = {"he", "him", "his", "himself"}
ANIMATE_NAMES = set(GENDER.keys())

# GoalOutcomeRegister roles (the extended dimension -- Zwaan goal/intentionality + outcome valence)
R_GOAL = "GOAL"
R_ACTION = "ACTION_AGAINST"
R_UNMET = "OUTCOME_UNMET"
R_MET = "OUTCOME_MET"
GO_ROLES = [R_GOAL, R_ACTION, R_UNMET, R_MET]


# ============================================================================ THE EXTENDED ORGAN
class GoalOutcomeRegister(AccumulateRegister):
    """Situation-model register EXTENDED with the GOAL / OUTCOME dimension (Zwaan event-indexing),
    mirroring hdlab.situation_model_accumulate.CausalLinkRegister's CAUSE/EFFECT extension.

    IDENTICAL to CausalLinkRegister's pattern: extends AccumulateRegister VERBATIM (same
    bind/unbind/bundle/cleanup_argmax chain, same ACCUMULATE-via-bundle organ, atom 29609) with a
    fixed meta-role vocabulary and per-entity role bookkeeping (an entity can carry GOAL with no
    OUTCOME, so decode must not guess an unbound role). The ONLY change vs the live reader's
    register is role_vocab: ["agent","mentioned"] -> ["GOAL","ACTION_AGAINST","OUTCOME_UNMET",
    "OUTCOME_MET"] -- no new binding/cleanup mechanism.

    add_typed_event(entity, role): binds role_vec to the next per-entity event slot and accumulates.
    appraise(entity): decodes every written slot (unbind + cleanup-argmax over the 4 roles) and
    reads goal-blocking OFF the accumulated register -- GOAL present AND net OUTCOME UNMET.
    """

    def __init__(self, d: int, generator: torch.Generator, max_event_slots: int = MAX_EVENTS) -> None:
        super().__init__(role_vocab=list(GO_ROLES), d=d, generator=generator,
                         max_event_slots=max_event_slots, overwrite=False)
        self._next_slot: dict = {}
        self._written: dict = {}  # entity -> list of (slot, role_written) for honest decode

    def add_typed_event(self, entity: str, role: str) -> bool:
        """Bind `role` to entity's next event slot; accumulate. Returns False if slots exhausted."""
        slot = self._next_slot.get(entity, 0)
        if slot >= self.max_event_slots:
            return False
        self.add_event(entity, role, slot)          # base organ: bind(role_vec, idx_vec[slot]) + bundle
        self._written.setdefault(entity, []).append((slot, role))
        self._next_slot[entity] = slot + 1
        return True

    def appraise(self, entity: str) -> dict:
        """Read goal-blocking OFF the accumulated register (NOT a local window). Decode each written
        slot through the accumulate organ (unbind + cleanup) and tally the recovered roles."""
        base = {"has_goal": False, "has_action_against": False, "n_unmet": 0, "n_met": 0,
                "goal_blocked": False, "n_events": 0, "decode_faithful": True}
        if entity not in self._written:
            return base
        tally = Counter()
        n_faithful = 0
        rows = self._written[entity]
        for slot, role_written in rows:
            best, _scores = self.decode(entity, slot)   # unbind by idx, cleanup-argmax over 4 roles
            tally[best] += 1
            n_faithful += int(best == role_written)
        has_goal = tally[R_GOAL] > 0
        n_unmet, n_met = tally[R_UNMET], tally[R_MET]
        base.update(has_goal=has_goal, has_action_against=tally[R_ACTION] > 0,
                    n_unmet=n_unmet, n_met=n_met, n_events=len(rows),
                    goal_blocked=(has_goal and n_unmet > n_met),
                    decode_faithful=(n_faithful == len(rows)))
        return base


# ============================================================================ glass-box attribution
def _ordered_tokens(sentence: str):
    """Order-preserving lowercase content tokens (attribution needs ORDER; normalize_tokens returns
    a set and is reused only for the bit-identical lexicon membership tests below)."""
    return [t for t in re.findall(r"[a-z']+", sentence.lower()) if t]


def _sentences(text: str):
    return [s.strip() for s in re.split(r"[.!?]", text) if s.strip()]


class RecencyEntityResolver:
    """Deterministic recency-shaped pronoun resolver (the KNOWN coref failure mode, MEMORY
    2026-08-03: coref backward-search IS recency, 0/4 on the recency-trap). Names resolve to
    themselves; a bare pronoun resolves to the MOST RECENT gender-compatible animate entity.
    NAMED explicitly so the recency control genuinely probes this mechanism -- brain: hippocampal
    antecedent retrieval, here in its recency-privileging (falsified) form."""

    def __init__(self):
        self._recent = []  # entity names in order of mention (most recent last)

    def subject_entity(self, sentence: str):
        toks = _ordered_tokens(sentence)
        for t in toks:                                   # first explicit animate NAME = subject
            if t in ANIMATE_NAMES:
                self._note(t)
                return t
        for t in toks:                                   # else first pronoun -> recency-resolved
            if t in PRON_F or t in PRON_M:
                want = "f" if t in PRON_F else "m"
                for e in reversed(self._recent):         # BACKWARD search == recency
                    if GENDER.get(e) == want:
                        return e
                return None
        return None

    def _note(self, entity: str):
        self._recent.append(entity)


def _tokset(text: str):
    return normalize_tokens(text)                        # bit-identical to v1._tokens


def type_sentence_events(sentence: str, subject):
    """Emit the typed goal/action/outcome events a sentence contributes, attributed to `subject`.
    Lexicon membership reuses V2_DESIRE / V2_OUTCOME_* / V1_WITHHOLD|OMISSION bit-identical."""
    t = _tokset(sentence)
    events = []
    has_desire = bool(t & V2_DESIRE)
    has_unmet = bool(t & V2_OUTCOME_UNMET)
    has_met = bool(t & V2_OUTCOME_MET)
    has_block = bool(t & (V1_WITHHOLD | V1_OMISSION))
    if has_desire and subject is not None:
        events.append((subject, R_GOAL))
    if has_unmet and subject is not None:
        events.append((subject, R_UNMET))
    if has_met and subject is not None:
        events.append((subject, R_MET))
    return events, dict(has_desire=has_desire, has_unmet=has_unmet, has_met=has_met,
                        has_block=has_block, subject=subject)


def attribute_discourse(text: str, goal_owner: str):
    """Sentence-by-sentence attribution of typed events across the FULL discourse. ACTION_AGAINST
    (a withhold/omission by anyone) is bound to the goal_owner (owner-centric appraisal); GOAL /
    OUTCOME are bound to the sentence's resolved subject entity."""
    resolver = RecencyEntityResolver()
    per_sentence = []
    all_events = []
    for si, sent in enumerate(_sentences(text)):
        subj = resolver.subject_entity(sent)
        ev, info = type_sentence_events(sent, subj)
        if info["has_block"]:
            ev = ev + [(goal_owner, R_ACTION)]           # block is AGAINST the owner's goal
        info["sentence_idx"] = si
        info["events"] = ev
        per_sentence.append(info)
        all_events.extend(ev)
    return all_events, per_sentence


# ============================================================================ TREATMENT / BASELINE
def treatment_fires(text: str, goal_owner: str, seed: int):
    """TREATMENT: accumulate all dispersed typed events into GoalOutcomeRegister; appraise(owner)
    reads goal-blocking OFF the accumulated register."""
    gen = torch.Generator().manual_seed(2000 + int(seed))
    reg = GoalOutcomeRegister(d=D2, generator=gen, max_event_slots=MAX_EVENTS)
    events, per_sentence = attribute_discourse(text, goal_owner)
    for (entity, role) in events:
        reg.add_typed_event(entity, role)
    ap = reg.appraise(goal_owner)
    return ap["goal_blocked"], ap, per_sentence


def baseline_fires(text: str, seed: int):
    """BASELINE: the EXISTING view2_goal_outcome (bit-identical) read on each LOCAL 2-sentence
    window; fire = ANY window fires. Reproduces 'reading local windows' (entity-blind, local)."""
    sents = _sentences(text)
    for i in range(max(1, len(sents) - BASELINE_WINDOW + 1)):
        window = ". ".join(sents[i:i + BASELINE_WINDOW]) + " ."
        fires, _ = view2_goal_outcome(window, seed)
        if fires:
            return True
    # single-window fallback for very short passages
    if len(sents) < BASELINE_WINDOW:
        return view2_goal_outcome(text, seed)[0]
    return False


# ============================================================================ eval corpus
# Naturalistic goal-block items -- goal / action / outcome DISPERSED across non-adjacent sentences,
# in FULL discourse context. mcca_004 + theatre_refusal are the gold-ruler items (verbatim spans
# woven into full discourse); 4 more implicit goal-block passages. goal_owner is a glass-box
# annotation (NOT tuned to the views). class labels are NEVER read by attribution/appraisal.
GOAL_BLOCK = [
    dict(id="mcca_004_amy_warning", owner="amy", cls="goal_block", subtype="withholding",
         text="Amy wanted to be warned in time about the unsafe ice. "
              "Jo heard the little cry behind her but kept still. "
              "No matter whether she heard or not, let her mind herself. "
              "Amy threw up her hands and went down, and was lost under the ice."),
    dict(id="theatre_refusal", owner="amy", cls="goal_block", subtype="withholding",
         text="Amy was dying for some fun and longed to go to the play. "
              "Jo refused to take her along that night. "
              "You shan't stir a step, said Jo, and would not hear a word. "
              "Amy was left behind, wailing and sorry by the fire."),
    dict(id="beth_fair", owner="beth", cls="goal_block", subtype="withholding",
         text="Beth hoped to win a place at the summer fair. "
              "The others neglected her and kept the news to themselves. "
              "Beth waited a long while by the gate. "
              "In the end she missed her chance and was left sorry."),
    dict(id="tom_shore", owner="tom", cls="goal_block", subtype="withholding",
         text="Tom longed to reach the far shore before dark. "
              "Sid refused to lend him the boat and ignored his pleading. "
              "Tom stepped onto the thin ice alone. "
              "He fell through and sank, lost in the cold water."),
    dict(id="book_burning_spite", owner="jo", cls="goal_block", subtype="spite_destruction",
         text="Jo meant to finish her little book before Father came home. "
              "Amy was angry and full of spite that day. "
              "I burned it up, said Amy at last. "
              "Jo could never write it again, and it was a dreadful calamity."),
    dict(id="mcca_003_forger", owner="meg", cls="goal_block", subtype="borderline",
         text="Meg wanted to know who forged the mock love-letter. "
              "Laurie had confessed and asked pardon for the trick. "
              "He has been punished quite enough, they said. "
              "They would tell no more, and the matter was left unsolved and sorry."),
]

# Matched non-goal-block controls (must stay LOW): goal-MET, outcome-trap noise, physical-harm.
CONTROLS = [
    dict(id="amy_met", owner="amy", cls="control_goal_met", subtype="met",
         text="Amy wanted to reach the far shore. "
              "She skated hard and steady across the ice. "
              "In good time she reached the bank. "
              "She was safe and warm, glad to have won across."),
    dict(id="beth_met", owner="beth", cls="control_goal_met", subtype="met",
         text="Beth hoped to finish her song for the concert. "
              "She practised all the long evening. "
              "At last she reached the final line. "
              "She won the little prize and enjoyed the day."),
    dict(id="noise_frost", owner=None, cls="control_noise", subtype="outcome_trap",
         text="The warm spell had passed and a frost lay along the shore. "
              "The ice sank and the drift fell. "
              "The light was lost over the field. "
              "The grey sun went down behind the hill."),
    dict(id="noise_mist", owner=None, cls="control_noise", subtype="outcome_trap",
         text="A chill mist floated past the meadow. "
              "The frost fell along the bank and the ice sank. "
              "The wind was lost over the hill. "
              "The grey sky went down at last."),
    dict(id="harm_knife", owner=None, cls="control_harm", subtype="physical",
         text="The half-breed saw his chance in the dark. "
              "He drove the knife to the hilt in the young man's breast. "
              "The man fell hard against the wall. "
              "He was killed there and lay still."),
    dict(id="harm_poker", owner=None, cls="control_harm", subtype="physical",
         text="Sid took up the heavy poker by the fire. "
              "He beat the boy over the head twice. "
              "The child dropped to the floor. "
              "He was left wounded and badly hurt."),
]

# RECENCY control (right-event vs most-recent) -- GENUINE pronoun traps. GOLD = the correct
# goal_blocked verdict under CORRECT (antecedent-faithful) binding. The owner's OWN outcome is
# stated with a PRONOUN whose true antecedent is the DISTANT owner, while a FOIL entity is
# introduced more recently -- so the naive recency-shaped resolver grabs the foil and mis-binds
# the outcome. This is the known coref failure mode (recency-trap 0/4, MEMORY 2026-08-03) exercised
# one level up on dispersed goal-outcome binding.
RECENCY = [
    # TRAP: owner Amy is blocked; her OWN unmet outcome ('she went down') is via a pronoun whose
    # gold antecedent is Amy, but foil Jo is more recent -> recency mis-binds to Jo -> MISS.
    dict(id="recency_amy_blocked_pronoun_foil_jo", owner="amy", gold_goal_blocked=True,
         gold_outcome_owner="amy", trap="pronoun_distant_antecedent",
         text="Amy longed to be warned in time about the ice. "
              "Jo raced on far ahead of her. "
              "Left unwarned, she went down and was lost."),
    # TRAP: owner Tom blocked; own unmet outcome via pronoun 'he', gold antecedent Tom, foil Sid
    # more recent -> recency grabs Sid -> MISS.
    dict(id="recency_tom_blocked_pronoun_foil_sid", owner="tom", gold_goal_blocked=True,
         gold_outcome_owner="tom", trap="pronoun_distant_antecedent",
         text="Tom wished to reach the mill first. "
              "Sid strode on quickly ahead. "
              "Far behind, he missed the way and sank, lost in the dark."),
    # NON-TRAP: owner Beth blocked; the pronoun antecedent IS the most recent (Beth is the only
    # entity) -> recency happens to be correct -> MATCH. Shows the metric is not trivially 0.
    dict(id="recency_beth_blocked_antecedent_is_recent", owner="beth", gold_goal_blocked=True,
         gold_outcome_owner="beth", trap="antecedent_is_recent",
         text="Beth wanted to win the prize at the fair. "
              "She waited a long while by the gate. "
              "In the end she missed her chance and was lost and sorry."),
]


# ============================================================================ per-seed unit
def run_seed(seed):
    rows = []
    for it in GOAL_BLOCK + CONTROLS:
        owner = it["owner"] if it["owner"] is not None else "__none__"
        t_fire, ap, per_sent = treatment_fires(it["text"], owner, seed)
        b_fire = baseline_fires(it["text"], seed)
        rows.append(dict(id=it["id"], cls=it["cls"], subtype=it["subtype"], owner=it["owner"],
                         treatment_fires=bool(t_fire), baseline_fires=bool(b_fire),
                         appraise=ap,
                         n_owner_events=ap["n_events"], decode_faithful=ap["decode_faithful"]))

    # recency probe: does the appraisal for the owner match the GOLD (correct, non-recency) verdict?
    rec_rows = []
    for it in RECENCY:
        t_fire, ap, per_sent = treatment_fires(it["text"], it["owner"], seed)
        # what entity did the recency resolver attribute the OUTCOME sentences to?
        outcome_subjects = [ps["subject"] for ps in per_sent if ps["has_unmet"] or ps["has_met"]]
        matches_gold = (bool(t_fire) == bool(it["gold_goal_blocked"]))
        rec_rows.append(dict(id=it["id"], owner=it["owner"], trap=it["trap"],
                             gold_goal_blocked=bool(it["gold_goal_blocked"]),
                             treatment_goal_blocked=bool(t_fire),
                             matches_gold=matches_gold,
                             gold_outcome_owner=it["gold_outcome_owner"],
                             resolver_outcome_subjects=outcome_subjects,
                             appraise=ap))

    def rate(cls_list, key):
        sub = [r for r in rows if r["cls"] in cls_list]
        return round(sum(r[key] for r in sub) / len(sub), 4) if sub else None

    gb = ["goal_block"]
    ctrl = ["control_goal_met", "control_noise", "control_harm"]
    return dict(
        seed=seed,
        treatment_goal_block_fire=rate(gb, "treatment_fires"),
        treatment_control_fire=rate(ctrl, "treatment_fires"),
        baseline_goal_block_fire=rate(gb, "baseline_fires"),
        baseline_control_fire=rate(ctrl, "baseline_fires"),
        treatment_control_met_fire=rate(["control_goal_met"], "treatment_fires"),
        treatment_control_noise_fire=rate(["control_noise"], "treatment_fires"),
        treatment_control_harm_fire=rate(["control_harm"], "treatment_fires"),
        recency_binding_accuracy=round(sum(r["matches_gold"] for r in rec_rows) / len(rec_rows), 4),
        all_decode_faithful=all(r["decode_faithful"] for r in rows),
        rows=rows, recency_rows=rec_rows,
    )


# ============================================================================ aggregate + verdict
def aggregate(per_seed):
    seeds = sorted(per_seed.keys())
    n = len(seeds)

    def mean(key):
        vals = [per_seed[s][key] for s in seeds if per_seed[s][key] is not None]
        return round(float(np.mean(vals)), 4) if vals else None

    tgb = mean("treatment_goal_block_fire")
    tc = mean("treatment_control_fire")
    bgb = mean("baseline_goal_block_fire")
    bc = mean("baseline_control_fire")
    rec = mean("recency_binding_accuracy")
    decode_ok = all(per_seed[s]["all_decode_faithful"] for s in seeds)

    fires_discriminative = (tgb is not None and tc is not None and tgb >= 0.5 and tc < 0.1)
    beats_baseline = (tgb is not None and bgb is not None and tgb > bgb)

    if n < EXPECTED_N_SEEDS:
        verdict = "HARD_FAIL_CARDINALITY_BREACH"
    elif tgb is not None and tgb < 0.1:
        verdict = "HARD_FAIL_STILL_FLAT_REPRESENTATION_INSUFFICIENT"
    elif fires_discriminative and beats_baseline and rec is not None and rec >= 0.5:
        verdict = "WALL_CRACKS_DISCOURSE_GROUNDED_READ_WORKS"
    elif fires_discriminative and (rec is None or rec < 0.5):
        verdict = "MIDDLE_BAND_FIRES_BUT_RECENCY_CONFOUND_ROUTES_BINDING_SELECTOR"
    elif fires_discriminative and not beats_baseline:
        verdict = "FIRES_BUT_NO_LIFT_OVER_LOCAL_BASELINE"
    else:
        verdict = "PARTIAL_OR_INSUFFICIENT"

    summary = (f"TREATMENT goal_block={tgb} control={tc} (met={mean('treatment_control_met_fire')} "
               f"noise={mean('treatment_control_noise_fire')} harm={mean('treatment_control_harm_fire')}) "
               f"| BASELINE goal_block={bgb} control={bc} | recency_binding_acc={rec} "
               f"| decode_faithful={decode_ok} | vs ~1.4% flat naturalistic baseline")

    return dict(
        verdict=verdict, verdict_msg=f"{verdict}: {summary}", summary=summary, n_seeds=n,
        means=dict(
            treatment_goal_block_fire=tgb, treatment_control_fire=tc,
            treatment_control_met_fire=mean("treatment_control_met_fire"),
            treatment_control_noise_fire=mean("treatment_control_noise_fire"),
            treatment_control_harm_fire=mean("treatment_control_harm_fire"),
            baseline_goal_block_fire=bgb, baseline_control_fire=bc,
            recency_binding_accuracy=rec,
        ),
        bands=dict(fires_discriminative=fires_discriminative, beats_baseline=beats_baseline,
                   recency_binds_right_event=(rec is not None and rec >= 0.5),
                   all_decode_faithful=decode_ok),
        naturalistic_flat_baseline_ref=0.014,
        per_seed_rows_seed0=per_seed[seeds[0]]["rows"],
        recency_rows_seed0=per_seed[seeds[0]]["recency_rows"],
        register_extension=dict(
            organ="hdlab.situation_model_accumulate.AccumulateRegister (atom 29609), reused bit-identical",
            pattern="GoalOutcomeRegister(AccumulateRegister) mirrors CausalLinkRegister: extends "
                    "role_vocab ['agent','mentioned'] -> ['GOAL','ACTION_AGAINST','OUTCOME_UNMET',"
                    "'OUTCOME_MET'] + per-entity role bookkeeping + appraise(); same "
                    "bind/bundle/unbind/cleanup_argmax chain, no new binding/cleanup mechanism",
            read="appraise(owner) decodes each accumulated slot OFF the register (not a local window)",
        ),
        brain_structures=dict(
            goal_outcome_dimension="Zwaan event-indexing (intentionality/causation/outcome) over the "
                                   "DMN situation model (Zwaan & Radvansky 1998; Lerner 2011 DMN "
                                   "paragraph-scale integration)",
            binding="hippocampal relational binding (Ranganath & Ritchey 2012 PMAT) reused as one "
                    "substrate across dimension types -- mirrors CausalLinkRegister CAUSE/EFFECT reuse",
            appraisal="OFC/vmPFC outcome-value appraisal over the represented situation "
                      "(Moors/Scherer/Frijda 2013; Kintsch C-I)",
            entity_attribution="coreference / hippocampal antecedent retrieval; the recency-shaped "
                               "resolver is the KNOWN FALSIFIED failure mode (coref recency-trap 0/4, "
                               "MEMORY 2026-08-03), probed by the recency control",
        ),
        caveats=[
            "n small + DIRECTIONAL: 6 goal-block (incl mcca_004 + theatre_refusal gold rulers woven "
            "into full discourse, 1 spite-destruction boundary, 1 borderline) + 6 controls "
            "(2 goal-met, 2 outcome-trap noise, 2 physical-harm) + 3 recency-trap probes.",
            "The ~1.4% flat naturalistic baseline is the reported reference figure (0.014) for the "
            "local-window read; this cell's BASELINE arm reproduces the local-window read on THESE "
            "items (small n) as the matched on-item comparator -- not a re-measurement of the 1.4%.",
            "Supplied goal-schema KNOWLEDGE (V2_DESIRE / V2_OUTCOME_* / V1_WITHHOLD lexicons, "
            "proper-noun-free, reused bit-identical from the grounded VIEW-2) is ALLOWED (supply "
            "knowledge, not the reading mechanism); attribution + appraisal never read the class label.",
            "Entity attribution uses a deterministic RECENCY-shaped pronoun resolver -- named as the "
            "known-falsified coref failure mode; the goal-block items mostly use explicit names so "
            "the DISCRIMINATION test isolates dispersal/accumulation, while the recency probe isolates "
            "right-event-vs-most-recent binding.",
            "AccumulateRegister / normalize_tokens / view2_goal_outcome / V1/V2 lexicons reused "
            "bit-identical; no borrowed embedding/LLM/parser as mechanism; deterministic; multi-seed.",
        ],
    )


# ============================================================================ infra
def _write_json(path, d):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as f:
        json.dump(d, f, indent=2)
    os.replace(tmp, path)


def run(run_mode):
    t0 = time.perf_counter()
    out_dir = OUTPUT_DIR if run_mode == "full" else f"{OUTPUT_DIR}_{run_mode}"
    os.makedirs(out_dir, exist_ok=True)
    _write_json(os.path.join(out_dir, "_start_marker.json"),
                {"pid": os.getpid(), "ts_iso": datetime.now(timezone.utc).isoformat(),
                 "anchor_name": ANCHOR_NAME, "run_mode": run_mode, "host": platform.node()})

    seeds = SEEDS if run_mode == "full" else SEEDS[:2]
    done = completed_units(out_dir)
    for seed in seeds:
        k = unit_key("seed", seed)
        if k in done:
            print(f"[resume] seed={seed} done, skip", flush=True)
            continue
        ts = time.perf_counter()
        res = run_seed(seed)
        record_unit(out_dir, k, res)
        print(f"[progress] seed={seed} {time.perf_counter()-ts:.2f}s "
              f"T_gb={res['treatment_goal_block_fire']} T_ctrl={res['treatment_control_fire']} "
              f"B_gb={res['baseline_goal_block_fire']} recency={res['recency_binding_accuracy']} "
              f"decode_ok={res['all_decode_faithful']}", flush=True)

    per_seed = {int(r["seed"]): r for r in load_units(out_dir).values()}
    agg = aggregate(per_seed)
    agg["run_mode"] = run_mode
    agg["elapsed_s"] = time.perf_counter() - t0
    agg["ts_iso"] = datetime.now(timezone.utc).isoformat()
    agg["anchor_name"] = ANCHOR_NAME
    agg["config"] = dict(D2=D2, seeds=seeds, max_events=MAX_EVENTS, baseline_window=BASELINE_WINDOW,
                         n_goal_block=len(GOAL_BLOCK), n_control=len(CONTROLS), n_recency=len(RECENCY))
    agg["prereg"] = "preregs/2026-08-04_situation_model_goal_outcome_dimension_v1.md"
    agg["cites"] = ["notes/research_discourse_scale_grounded_integration_brain_drill_2026-08-04.md",
                    "hdlab/situation_model_accumulate.py (CausalLinkRegister CAUSE/EFFECT, atom 29609)",
                    "experiments/exp_self_extension_grounded_realprose_v1.py (VIEW-2 grounded read)"]
    agg["per_seed"] = per_seed
    _write_json(os.path.join(out_dir, "metrics.json"), agg)
    print(f"[VERDICT] {agg['verdict_msg']}", flush=True)
    print(f"[elapsed] {agg['elapsed_s']:.2f}s", flush=True)
    return agg


# ============================================================================ self-test
def self_test():
    # (0) the register EXTENSION: role_vocab is the 4 goal/outcome dims, organ is AccumulateRegister
    gen = torch.Generator().manual_seed(0)
    reg = GoalOutcomeRegister(d=D2, generator=gen)
    assert isinstance(reg, AccumulateRegister), "GoalOutcomeRegister must extend the validated organ"
    assert reg.role_vocab == GO_ROLES, f"role_vocab not extended: {reg.role_vocab}"
    # write dispersed events for one owner and read them back OFF the register (decode faithful)
    for role in (R_GOAL, R_ACTION, R_UNMET, R_UNMET, R_MET):
        reg.add_typed_event("owner", role)
    ap = reg.appraise("owner")
    assert ap["decode_faithful"], f"accumulate organ decode not faithful: {ap}"
    assert ap["has_goal"] and ap["n_unmet"] == 2 and ap["n_met"] == 1 and ap["goal_blocked"], ap

    # (1) TREATMENT fires on a dispersed goal-block item; (2) BASELINE local-window does NOT
    gb = next(it for it in GOAL_BLOCK if it["id"] == "mcca_004_amy_warning")
    t_fire, ap, per_sent = treatment_fires(gb["text"], gb["owner"], 0)
    assert t_fire, f"TREATMENT missed dispersed goal-block: {ap}"
    # the goal and outcome are in NON-ADJACENT sentences -> the local 2-sentence read should miss
    assert not baseline_fires(gb["text"], 0), "BASELINE local window unexpectedly fired (not dispersed?)"

    # (3) controls stay silent under TREATMENT
    for cid in ("noise_frost", "harm_knife", "amy_met"):
        it = next(x for x in CONTROLS if x["id"] == cid)
        owner = it["owner"] if it["owner"] is not None else "__none__"
        cf, cap, _ = treatment_fires(it["text"], owner, 0)
        assert not cf, f"control {cid} FALSE-FIRED under TREATMENT: {cap}"

    # (4) lexicon reuse is bit-identical (guards against drift from the v1 grounded view)
    assert V2_DESIRE is v1.V2_DESIRE and V1_WITHHOLD is v1.V1_WITHHOLD, "lexicons not reused by-ref"

    # (5) one full seed sanity
    res = run_seed(0)
    assert res["treatment_goal_block_fire"] is not None and res["treatment_control_fire"] is not None
    print(f"[SELFTEST PASS] register extended (4 goal/outcome roles on AccumulateRegister); decode "
          f"faithful; TREATMENT fires on dispersed goal-block, BASELINE local window misses; controls "
          f"silent; seed0 T_gb={res['treatment_goal_block_fire']} T_ctrl={res['treatment_control_fire']} "
          f"B_gb={res['baseline_goal_block_fire']} recency={res['recency_binding_accuracy']}", flush=True)
    return True


def main():
    if sys.stdout is not None and hasattr(sys.stdout, "reconfigure"):
        try:
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except Exception:
            pass
    ap = argparse.ArgumentParser()
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--full", action="store_true")
    args = ap.parse_args()
    if args.self_test:
        raise SystemExit(0 if self_test() else 1)
    if args.smoke:
        run("smoke")
        raise SystemExit(0)
    run("full")
    raise SystemExit(0)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except KeyboardInterrupt:
        raise
    except Exception as e:
        _write_json(os.path.join(OUTPUT_DIR, "metrics.json"),
                    {"verdict": "CELL_CRASHED", "verdict_msg": f"{type(e).__name__}: {str(e)[:400]}",
                     "traceback": traceback.format_exc()[:5000],
                     "ts_iso": datetime.now(timezone.utc).isoformat()})
        raise
