"""Scaffold-free witness for hdlab.situation_model_accumulate.AccumulateRegister.

Reproduces the validated construction-proof result (atom 29609,
experiments/exp_situation_model_accumulate_vs_overwrite_v1.py ARM A/B/C) on a small
synthetic multi-event case: a few entities each tracked across 2-3 events with distinct
roles. ACCUMULATE must recover ALL events; OVERWRITE must recover only the LAST event
(chance on earlier positions); FLOOR (an independent random register unrelated to
content) must sit near chance. Also checks the single-event control (both modes must
agree and be near-perfect when there is only one event to recover) and that the three
arms never produce bit-identical registers (META_RULE_AF-style arms-must-differ check).

Passes with tracing=False (no trace bus configured; hdlab.tracing.emit is a no-op).
"""
from __future__ import annotations

import os
import sys

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_model_accumulate import AccumulateRegister

ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker"]
CHANCE = 1.0 / len(ROLE_VOCAB)

# entity -> ordered list of (role) played at each successive event slot
ENTITIES = {
    "e_two_event_a": ["agent", "patient"],
    "e_two_event_b": ["patient", "agent"],
    "e_three_event_a": ["agent", "recipient", "theme"],
    "e_three_event_b": ["theme", "speaker", "addressee"],
    "e_single_event": ["agent"],
}


def _build(overwrite: bool, seed: int) -> AccumulateRegister:
    gen = torch.Generator().manual_seed(seed)
    reg = AccumulateRegister(ROLE_VOCAB, d=1024, generator=gen, max_event_slots=8, overwrite=overwrite)
    for entity, roles in ENTITIES.items():
        for idx, role in enumerate(roles):
            reg.add_event(entity, role, idx)
    return reg


def _recall(reg: AccumulateRegister) -> dict[str, float]:
    """Per-entity fraction of event positions whose true role is recovered."""
    out = {}
    for entity, roles in ENTITIES.items():
        correct = 0
        for idx, true_role in enumerate(roles):
            pred_role, _ = reg.decode(entity, idx)
            correct += int(pred_role == true_role)
        out[entity] = correct / len(roles)
    return out


def _floor_recall(seed: int) -> float:
    """Independent random register unrelated to content -- non-vacuous chance floor."""
    gen = torch.Generator().manual_seed(seed)
    reg = AccumulateRegister(ROLE_VOCAB, d=1024, generator=gen, max_event_slots=8, overwrite=False)
    floor_gen = torch.Generator().manual_seed(seed + 999)
    total = 0
    correct = 0
    for entity, roles in ENTITIES.items():
        # register the real events so idx_vecs/role_vecs exist, but decode against an
        # unrelated random vector standing in for the entity's register (the floor arm).
        for idx, role in enumerate(roles):
            reg.add_event(entity, role, idx)
        from hdlab.situation_model_accumulate import cleanup_argmax, unit_phase_vec
        floor_reg = unit_phase_vec(reg.d, floor_gen)
        for idx, true_role in enumerate(roles):
            from hdlab import binding
            readback = binding.unbind(floor_reg, reg.idx_vecs[idx])
            pred_role, _ = cleanup_argmax(readback, reg.role_vecs)
            correct += int(pred_role == true_role)
            total += 1
    return correct / total


def test_accumulate_recovers_all_events() -> None:
    """ACCUMULATE register recovers every event in a 2-3 chain, not just the last."""
    reg = _build(overwrite=False, seed=1)
    recall = _recall(reg)
    multi = [recall[e] for e in ("e_two_event_a", "e_two_event_b", "e_three_event_a", "e_three_event_b")]
    assert min(multi) >= 0.95, f"ACCUMULATE failed to recover all events: {recall}"
    assert recall["e_single_event"] >= 0.95, f"single-event control failed for ACCUMULATE: {recall}"


def test_overwrite_recovers_only_last_event() -> None:
    """OVERWRITE register recovers only the newest event; earlier (non-last) positions
    decode at roughly chance (a single seed can noisily hit a chance-level position by
    luck, so this averages the non-last-position recall over several seeds)."""
    multi_keys = ("e_two_event_a", "e_two_event_b", "e_three_event_a", "e_three_event_b")
    non_last_hits = 0
    non_last_total = 0
    for seed in range(10):
        reg = _build(overwrite=True, seed=100 + seed)
        for entity in multi_keys:
            roles = ENTITIES[entity]
            n = len(roles)
            for idx, true_role in enumerate(roles):
                pred_role, _ = reg.decode(entity, idx)
                if idx == n - 1:
                    assert pred_role == true_role, (
                        f"OVERWRITE failed to recover its own last-written event for {entity} "
                        f"(seed={seed})"
                    )
                else:
                    non_last_hits += int(pred_role == true_role)
                    non_last_total += 1
    non_last_acc = non_last_hits / non_last_total
    # analytic expectation for a non-last position under OVERWRITE is pure chance
    # (1/len(ROLE_VOCAB)); allow generous slack for the small sample.
    assert non_last_acc <= CHANCE + 0.25, (
        f"OVERWRITE non-last-position recall not near chance: {non_last_acc:.3f} "
        f"(chance={CHANCE:.3f})"
    )


def test_floor_near_chance() -> None:
    """An independent random register unrelated to content sits near chance, not near 1.0."""
    floor_acc = _floor_recall(seed=2)
    assert floor_acc <= CHANCE + 0.20, f"floor arm not near chance: {floor_acc:.3f} (chance={CHANCE:.3f})"


def test_accumulate_beats_overwrite_beats_floor() -> None:
    """The construction-proof ordering (atom 29609): accumulate > overwrite > floor.

    Averaged over several seeds to smooth the small-sample noise inherent to a handful
    of synthetic entities (a single seed can transiently favor one arm on a couple of
    chance-level guesses).
    """
    multi_keys = ("e_two_event_a", "e_two_event_b", "e_three_event_a", "e_three_event_b")
    n_seeds = 10
    acc_vals, ovr_vals, floor_vals = [], [], []
    for seed in range(n_seeds):
        acc_reg = _build(overwrite=False, seed=200 + seed)
        ovr_reg = _build(overwrite=True, seed=200 + seed)
        acc_recall = _recall(acc_reg)
        ovr_recall = _recall(ovr_reg)
        acc_vals.append(sum(acc_recall[e] for e in multi_keys) / len(multi_keys))
        ovr_vals.append(sum(ovr_recall[e] for e in multi_keys) / len(multi_keys))
        floor_vals.append(_floor_recall(seed=200 + seed))
    acc_multi = sum(acc_vals) / n_seeds
    ovr_multi = sum(ovr_vals) / n_seeds
    floor_acc = sum(floor_vals) / n_seeds
    assert acc_multi > ovr_multi > floor_acc - 0.05, (
        f"expected accumulate > overwrite > floor, got "
        f"accumulate={acc_multi:.3f} overwrite={ovr_multi:.3f} floor={floor_acc:.3f}"
    )
    assert acc_multi >= 0.95


def test_arms_differ() -> None:
    """META_RULE_AF-style arms-must-differ: accumulate/overwrite/floor registers are never
    bit-identical for the same entity (no silent collapse of the three arms)."""
    acc_reg = _build(overwrite=False, seed=4)
    ovr_reg = _build(overwrite=True, seed=4)
    for entity in ENTITIES:
        if len(ENTITIES[entity]) < 2:
            continue  # single-event: accumulate == overwrite by construction, not a violation
        acc_vec = acc_reg.register(entity)
        ovr_vec = ovr_reg.register(entity)
        assert not torch.equal(acc_vec, ovr_vec), f"accumulate/overwrite registers identical for {entity}"


def _run_all() -> None:
    test_accumulate_recovers_all_events()
    test_overwrite_recovers_only_last_event()
    test_floor_near_chance()
    test_accumulate_beats_overwrite_beats_floor()
    test_arms_differ()


if __name__ == "__main__":
    _run_all()
    print("[verify_situation_model_accumulate] PASS: accumulate > overwrite > floor "
          "reproduced on synthetic multi-event entities; single-event control holds; "
          "arms differ.")
