"""Scaffold-free witness for hdlab.self_improving_loop (coherence-gated autonomous keep/revert
controller, promotion of experiments/exp_coref_autonomous_fix_router_v1.py, commit 3d25cb038).

Builds a dense-like synthetic passage directly at the (role, event_slot, cluster_id) level (no
gold label is ever read by route_passage -- this fixture demonstrates the mechanism, it does not
supply an oracle). Background structure gives 3 entities (E1/E2/E3) 2-3 events each -- the
"dense" per-entity accumulated structure the promotion's SCOPE note requires (see module
docstring; the mechanism is noise-dominated at near-zero per-entity structure, which is exactly
why the same controller only ties on the sparser combined_powered McGuffey eval).

Two focus mentions isolate the mechanism cleanly:
  - GOOD FIX (fixture A): baseline mis-clusters mention M into an entity (E2) whose register
    ALREADY has an event bound at M's same event_slot (a collision -- crosstalk lowers the
    decode margin at that slot for both bound events). The good candidate re-clusters M into its
    correct entity (E1), which has NO existing event at that slot (collision-free) -- coherence
    margin rises. The controller must ADOPT this fix using only the gold-free delta.
  - BAD / TRAP FIX (fixture B): baseline correctly places M into its own entity (E1) at a slot
    with no existing collision. The trap candidate moves M into a DIFFERENT entity (E2) that
    ALREADY has an event at that same slot -- introducing a fresh collision, lowering the
    coherence margin. The controller must REJECT (revert to baseline) using only the gold-free
    delta -- exactly the shape of the real router rejecting the confirmed-negative decay-window
    lever with no label telling it the lever was bad.

Passes with tracing=False (no trace bus configured; hdlab.tracing.emit is a no-op).
"""
from __future__ import annotations

import os
import sys

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.self_improving_loop import decide_keep_or_revert, route_passage

ROLE_VOCAB = ["agent", "patient", "theme", "recipient"]
D = 512
MAX_EVENT_SLOTS = 4
ABSTAIN_BAND = 0.02

# Shared dense-like background (positions 0-7, identical across baseline and every candidate in
# both fixtures): E1 agent@0, agent@2; E2 patient@0, patient@1, theme@2; E3 theme@0, patient@1,
# recipient@3 -- each entity carries multiple events, matching real McGuffey's accumulated
# per-entity structure (not a 1-event toy).
_BG_ROLES = ["agent", "patient", "patient", "theme", "patient", "agent", "theme", "recipient"]
_BG_SLOTS = [0, 0, 1, 0, 1, 2, 2, 3]
_BG_CIDS = ["E1", "E2", "E2", "E3", "E3", "E1", "E2", "E3"]

# Focus mention M: role=agent, event_slot=1. E1 has NO event at slot 1 (collision-free target);
# E2 already has an event at slot 1 (patient, position 2) -- the collision target.
_M_ROLE = "agent"
_M_SLOT = 1
FOCUS_POS = 8  # index of M once appended to the background


def _stream(m_role=_M_ROLE, m_slot=_M_SLOT):
    return list(_BG_ROLES) + [m_role], list(_BG_SLOTS) + [m_slot]


def _seeded(seed: int):
    return lambda: torch.Generator().manual_seed(seed)


def test_pure_decision_rule() -> None:
    """decide_keep_or_revert: no-data-dependency unit tests (byte-identical rule to the
    validated router cell's _decide_autonomous)."""
    assert decide_keep_or_revert({"a": 0.1, "b": -0.05}) == "a"
    assert decide_keep_or_revert({"a": ABSTAIN_BAND}) is None, "exactly-at-band must NOT adopt"
    assert decide_keep_or_revert({"a": ABSTAIN_BAND + 1e-6}) == "a"
    assert decide_keep_or_revert({"a": -0.2}) is None
    assert decide_keep_or_revert({}) is None


def test_router_keeps_coherence_raising_good_fix() -> None:
    """Fixture A: baseline collides M into E2 (which already occupies slot 1); the 'good'
    candidate re-clusters M into its own collision-free entity E1. The controller must ADOPT
    'good' using only the gold-free coherence-margin delta, reliably across seeds (no cherry-
    picked single seed -- this fixture's effect size is large: collision -> collision-free)."""
    roles, slots = _stream()
    baseline = _BG_CIDS + ["E2"]  # M mis-clustered into E2: collides with position 2 (E2@slot1)
    good = _BG_CIDS + ["E1"]      # M correctly clustered into E1: no existing event at slot 1
    n_adopted = 0
    for seed in range(20):
        res = route_passage(roles, slots, baseline, {"good": good}, [FOCUS_POS], ROLE_VOCAB, D,
                            _seeded(seed), MAX_EVENT_SLOTS)
        pc = res["per_candidate"]["good"]
        assert pc["applicable"] and pc["n_changed_flagged"] == 1, pc
        if res["adopt"] == "good":
            n_adopted += 1
    assert n_adopted == 20, f"good fix should be adopted on every seed (collision->clean is a " \
        f"large, reliable effect), got {n_adopted}/20"


def test_router_rejects_coherence_lowering_trap_fix() -> None:
    """Fixture B: baseline correctly (collision-free) clusters M into E1. The 'trap' candidate
    moves M into E2, which ALREADY has an event at slot 1 -- introducing a fresh collision. The
    controller must REJECT (revert to baseline) using only the gold-free coherence-margin delta,
    reliably across seeds -- mirroring the real router's rejection of the confirmed-negative
    decay-window lever with no label anywhere telling it the lever was bad."""
    roles, slots = _stream()
    baseline = _BG_CIDS + ["E1"]  # M correctly clustered into E1: no collision
    trap = _BG_CIDS + ["E2"]      # M moved into E2: collides with position 2 (E2@slot1)
    n_rejected = 0
    for seed in range(20):
        res = route_passage(roles, slots, baseline, {"trap": trap}, [FOCUS_POS], ROLE_VOCAB, D,
                            _seeded(seed), MAX_EVENT_SLOTS)
        pc = res["per_candidate"]["trap"]
        assert pc["applicable"] and pc["n_changed_flagged"] == 1, pc
        if res["adopt"] is None:
            n_rejected += 1
    assert n_rejected == 20, f"trap fix should be rejected on every seed (clean->collision is a " \
        f"large, reliable effect), got {n_rejected}/20"


def test_router_prefers_good_over_trap_when_both_offered() -> None:
    """Both candidates offered at once against the SAME (colliding) baseline: 'good' resolves
    the collision, 'trap' merely relocates it elsewhere. The controller must adopt 'good', never
    'trap', reliably across seeds -- the competitive framing the real router runs (two
    independently-computed candidate mechanisms per passage)."""
    roles, slots = _stream()
    baseline = _BG_CIDS + ["E2"]  # colliding, same as fixture A
    good = _BG_CIDS + ["E1"]
    trap = _BG_CIDS + ["E3"]      # E3 also already occupies slot 1 (position 4): still colliding
    for seed in range(10):
        res = route_passage(roles, slots, baseline, {"good": good, "trap": trap}, [FOCUS_POS],
                            ROLE_VOCAB, D, _seeded(seed), MAX_EVENT_SLOTS)
        assert res["adopt"] == "good", f"seed={seed}: expected 'good', got {res['adopt']} " \
            f"per_candidate={res['per_candidate']}"


def test_no_data_no_flagged_positions_keeps_baseline() -> None:
    """No flagged positions -> no candidate is ever 'applicable' -> controller keeps baseline
    (adopt=None), never fabricates evidence."""
    roles, slots = _stream()
    baseline = _BG_CIDS + ["E2"]
    good = _BG_CIDS + ["E1"]
    res = route_passage(roles, slots, baseline, {"good": good}, [], ROLE_VOCAB, D, _seeded(0),
                        MAX_EVENT_SLOTS)
    assert res["adopt"] is None
    assert res["per_candidate"]["good"]["applicable"] is False
    assert res["adopted_cluster_ids"] == baseline


def _run_all() -> None:
    test_pure_decision_rule()
    test_router_keeps_coherence_raising_good_fix()
    test_router_rejects_coherence_lowering_trap_fix()
    test_router_prefers_good_over_trap_when_both_offered()
    test_no_data_no_flagged_positions_keeps_baseline()


if __name__ == "__main__":
    _run_all()
    print("[verify_self_improving_loop] PASS: pure adoption-rule logic unit-tested; the "
          "controller ADOPTS a coherence-raising good fix and REJECTS a coherence-lowering trap "
          "fix on a dense-like synthetic passage using ONLY the gold-free coherence-margin-delta "
          "signal, reliably across seeds; prefers good over trap when both are offered; keeps "
          "baseline when nothing is flagged.")
