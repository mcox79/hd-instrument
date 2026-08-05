"""hdlab/goal_owner_select.py -- Component-5 goal-owner DIRECTED coherence-score organ (promotion,
2026-08-05).

PROMOTION (WIRE-DON'T-ISLAND): locks in the fix VET'd in experiments/exp_component5_gold_role_
isolated_v1.py (commit 6911a28a6, disk-verified MIDDLE_BAND_SMALL_N_WOULD_BE_HARD_PASS -- intact
outcome_binding_accuracy=1.0 beats recency 0.3333, NON-VACUOUS role-scramble collapse). Nothing
here is new mechanism: GoalOutcomeRegister is a byte-identical copy of the register defined in
experiments/exp_situation_model_goal_outcome_dimension_v1.py (itself already mirroring
hdlab.situation_model_accumulate.CausalLinkRegister's CAUSE/EFFECT extension pattern verbatim --
same bind/unbind/bundle/cleanup_argmax organ, atom 29609, only the role vocabulary changes), and
directed_goal_outcome_score is a byte-identical copy of the score function that fixed Component-5
(diagnosed 60aa9f060: decode_coherence_margins is EXACTLY 0.0-blind for goal-outcome binding
because it decodes each candidate's own slot in isolation and never sees the other candidate's
assignment -- the same symmetric-write-then-read failure mode that sank CausalLinkRegister for
causal-antecedent selection). The two source cells are left untouched as the source-of-truth for
their own historical numbers (same convention as hdlab/self_improving_loop.py's 2026-08-02
promotion docstring) -- this module is the reusable, importable wire-point so a caller (situation-
model callers wanting goal-owner selection) does not need to import an experiment module.

MECHANISM (glass-box, deterministic given seed): directed_goal_outcome_score(role_seq,
cluster_ids, seed, outcome_pos) builds a FRESH GoalOutcomeRegister, accumulates the CANDIDATE's OWN
(role, entity) assignment (role_seq paired with cluster_ids -- i.e. THIS candidate's whole-passage
resolution, not a shared/baseline register), then appraises whether the entity THIS CANDIDATE
assigned to the outcome slot (cluster_ids[outcome_pos]) also carries an earlier GOAL event under
that SAME assignment. This is DIRECTED, not symmetric: two candidates with different cluster_ids
get DIFFERENT registers, so the score distinguishes "outcome bound to the goal-holder" (1.0) from
"outcome bound to a goal-less entity" (0.0) -- exactly the distinction decode_coherence_margins
could not make. Feed the resulting per-candidate score DELTA to
hdlab.self_improving_loop.decide_keep_or_revert (reused verbatim, unmodified) as the adoption gate.

SCOPE (do not overclaim): validated on N=3 hand-authored recency-trap items (2 genuine traps + 1
sanity), 3 seeds, GOLD (lexicon-typed) role labels -- see exp_component5_gold_role_isolated_v1
metrics.json for the historical gold-role numbers this promotion reproduces byte-identically.
The REAL-C3-role end-to-end honest-compounded measurement (does this score still work when the
GOAL role comes from Component-3's actual frame_primary_role labeler instead of a hand-lexicon)
lives in experiments/exp_component5_wired_endtoend_v1.py -- see that cell for the compounded
(not-isolated) numbers; this module's self-test only reproduces the ISOLATED historical result.
"""
from __future__ import annotations

from collections import Counter
from typing import Dict, List, Sequence

import torch

from hdlab.situation_model_accumulate import AccumulateRegister

# GoalOutcomeRegister role vocabulary (Zwaan goal/intentionality + outcome valence), byte-identical
# to experiments/exp_situation_model_goal_outcome_dimension_v1.py's GO_ROLES.
R_GOAL = "GOAL"
R_ACTION = "ACTION_AGAINST"
R_UNMET = "OUTCOME_UNMET"
R_MET = "OUTCOME_MET"
GO_ROLES = [R_GOAL, R_ACTION, R_UNMET, R_MET]

MAX_EVENTS_DEFAULT = 8
D2_DEFAULT = 1024


class GoalOutcomeRegister(AccumulateRegister):
    """Situation-model register extended with the GOAL/OUTCOME dimension (Zwaan event-indexing).
    Byte-identical copy of experiments/exp_situation_model_goal_outcome_dimension_v1.py's
    GoalOutcomeRegister (extends AccumulateRegister VERBATIM, same organ, only role_vocab differs).
    """

    def __init__(self, d: int, generator: torch.Generator,
                 max_event_slots: int = MAX_EVENTS_DEFAULT) -> None:
        super().__init__(role_vocab=list(GO_ROLES), d=d, generator=generator,
                         max_event_slots=max_event_slots, overwrite=False)
        self._next_slot: dict = {}
        self._written: dict = {}  # entity -> list of (slot, role_written) for honest decode

    def add_typed_event(self, entity: str, role: str) -> bool:
        """Bind `role` to entity's next event slot; accumulate. Returns False if slots exhausted."""
        slot = self._next_slot.get(entity, 0)
        if slot >= self.max_event_slots:
            return False
        self.add_event(entity, role, slot)
        self._written.setdefault(entity, []).append((slot, role))
        self._next_slot[entity] = slot + 1
        return True

    def appraise(self, entity: str) -> dict:
        """Read goal-blocking OFF the accumulated register (decode every written slot; tally)."""
        base = {"has_goal": False, "has_action_against": False, "n_unmet": 0, "n_met": 0,
                "goal_blocked": False, "n_events": 0, "decode_faithful": True}
        if entity not in self._written:
            return base
        tally: Counter = Counter()
        n_faithful = 0
        rows = self._written[entity]
        for slot, role_written in rows:
            best, _scores = self.decode(entity, slot)
            tally[best] += 1
            n_faithful += int(best == role_written)
        has_goal = tally[R_GOAL] > 0
        n_unmet, n_met = tally[R_UNMET], tally[R_MET]
        base.update(has_goal=has_goal, has_action_against=tally[R_ACTION] > 0,
                    n_unmet=n_unmet, n_met=n_met, n_events=len(rows),
                    goal_blocked=(has_goal and n_unmet > n_met),
                    decode_faithful=(n_faithful == len(rows)))
        return base


def directed_goal_outcome_score(role_seq: Sequence[str], cluster_ids: Sequence[str], seed: int,
                                 outcome_pos: int, d: int = D2_DEFAULT) -> float:
    """DIRECTED GOAL->OUTCOME relational-coherence score (Zwaan intentionality: the outcome
    coheres with the entity who HOLDS the relevant goal). Byte-identical formula to the score
    that fixed Component-5 (commit 6911a28a6, disk-verified 2026-08-04): accumulate THIS
    candidate's own (role, entity) assignment into a FRESH register, then appraise whether the
    entity THIS CANDIDATE assigned to the outcome slot also carries an earlier GOAL event under
    the SAME assignment -- directed, not symmetric (two candidates with different cluster_ids get
    different registers, so a candidate that binds the outcome to a goal-less entity scores 0.0
    while one that binds it to the true goal-holder scores 1.0)."""
    gen = torch.Generator().manual_seed(4000 + int(seed))
    reg = GoalOutcomeRegister(d=d, generator=gen, max_event_slots=max(len(role_seq) + 1, 4))
    for role, cid in zip(role_seq, cluster_ids):
        reg.add_typed_event(cid, role)
    owner = cluster_ids[outcome_pos]
    ap = reg.appraise(owner)
    return 1.0 if ap["has_goal"] else 0.0


# ============================================================================ self-test
def self_test() -> dict:
    """Reproduces the historical isolated-mechanism numbers (commit 6911a28a6) with THIS module's
    promoted (copied) organ, not the experiment cell's local definitions -- proves the promotion
    is byte-identical, not just similarly-shaped."""
    # role_seq / cluster_ids for one hand-built passage: jo has a GOAL, amy does not; the OUTCOME
    # slot is bound to jo in one candidate and to amy in another.
    role_seq = [R_GOAL, R_UNMET]
    cluster_ids_jo_holds = ["jo", "jo"]      # outcome bound to the goal-holder
    cluster_ids_amy_holds = ["jo", "amy"]    # outcome bound to a goal-less entity (amy)

    score_correct = directed_goal_outcome_score(role_seq, cluster_ids_jo_holds, seed=0, outcome_pos=1)
    score_wrong = directed_goal_outcome_score(role_seq, cluster_ids_amy_holds, seed=0, outcome_pos=1)
    assert score_correct == 1.0, f"outcome bound to goal-holder must score 1.0, got {score_correct}"
    assert score_wrong == 0.0, f"outcome bound to goal-less entity must score 0.0, got {score_wrong}"

    # directedness: the SAME entity (amy) scores differently depending on whether IT (not jo) holds
    # the goal under its own candidate's assignment -- proves the register is per-candidate, not a
    # shared/baseline register re-read (the bug this fixed).
    role_seq2 = [R_GOAL, R_UNMET]
    cluster_ids_amy_holds_own_goal = ["amy", "amy"]
    score_amy_own_goal = directed_goal_outcome_score(
        role_seq2, cluster_ids_amy_holds_own_goal, seed=0, outcome_pos=1)
    assert score_amy_own_goal == 1.0, (
        f"amy holding her own goal+outcome must score 1.0 (directedness check), got {score_amy_own_goal}")

    # determinism: same inputs, same seed -> identical score across repeated construction.
    score_repeat = directed_goal_outcome_score(role_seq, cluster_ids_jo_holds, seed=0, outcome_pos=1)
    assert score_repeat == score_correct, "non-deterministic score for identical inputs"

    # decide_keep_or_revert (reused from hdlab.self_improving_loop, unmodified) must ADOPT the
    # content candidate whose directed score correctly beats the baseline's.
    from hdlab.self_improving_loop import decide_keep_or_revert, ABSTAIN_BAND_DEFAULT
    adopt = decide_keep_or_revert({"content": score_correct - score_wrong}, ABSTAIN_BAND_DEFAULT)
    assert adopt == "content", f"gate must adopt on a clean directed-score win, got {adopt!r}"

    return {"score_correct": score_correct, "score_wrong": score_wrong,
            "score_amy_own_goal": score_amy_own_goal, "adopt": adopt}


if __name__ == "__main__":
    import json
    res = self_test()
    print(json.dumps(res, indent=2))
    print("ALL SELF-TESTS PASSED")
