"""Scaffold-free witness: hdlab.situation_model_multibank.MultiBankAccumulateRegister is a
correct drop-in for hdlab.situation_model_accumulate.AccumulateRegister via the
make_situation_register factory (2026-08-03 wire-point, closing the
WIRED_BUT_NOT_PIPELINE_REACHABLE gap named in tools/capability_registry_audit.py's
ACTIVE_PIPELINE_ENTRY_POINTS reachability check).

Two claims checked:

1. DROP-IN CORRECTNESS AT SMALL SCALE (the pilot regime the active reader actually runs at):
   given the SAME (role, event_idx) writes with SAME-SEEDED symbol tables, backend="multibank"
   and backend="flat" decode the SAME predicted role at every position and agree on
   .entities(). (Their top1-vs-runner-up MARGIN magnitudes are not required to match --
   multibank routes different event_idx values into different banks by
   stable_bank_id(event_idx, n_banks), so even at small scale it can bundle FEWER co-occurring
   events per bank than the flat register does, which changes the margin's magnitude without
   changing which role wins. The correctness bar for a drop-in memory backend is the decoded
   PREDICTION, i.e. what self_improving_loop.decide_keep_or_revert ultimately acts on, not
   incidental margin magnitude -- checked separately below.) This is the correctness bar for
   switching the default backend: no regression at the scale the pipeline runs at today.

2. HIGH-LOAD CAPACITY RETENTION (the reason multibank is wired at all): at max_event_slots
   large enough to stress the flat register's single-bundle cross-talk floor, multibank(n_banks=8)
   holds decode self-consistency far above the flat register, reproducing (at reduced scale
   for a fast witness) the capacity-headroom result MEASURED in
   data/exp_situation_model_multibank_capacity_v1/metrics.json (d=512, n_events=256, 5 seeds:
   flat=0.6547, multibank_8=0.9992 -- MEASURED@d:/AI/hd-instrument/data/
   exp_situation_model_multibank_capacity_v1/metrics.json:verdict_msg).

Passes with tracing=False (no trace bus configured; hdlab.tracing.emit is a no-op).
"""
from __future__ import annotations

import os
import sys

import torch

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from hdlab.situation_model_accumulate import AccumulateRegister, make_situation_register
from hdlab.situation_model_multibank import MultiBankAccumulateRegister

ROLE_VOCAB = ["agent", "patient", "theme", "recipient", "addressee", "speaker"]

# Small pilot-scale case, matching the shape of the Anne reader's consolidated-only
# situation model (a handful of entities, 2-4 events each, max_event_slots=8).
SMALL_ENTITIES = {
    "e_a": ["agent", "patient"],
    "e_b": ["patient", "agent", "theme"],
    "e_c": ["agent"],
    "e_d": ["theme", "speaker", "addressee", "agent"],
}


def test_factory_returns_declared_backend() -> None:
    """make_situation_register(backend=...) returns the exact class it declares, and rejects
    an unknown backend name loudly rather than silently falling back."""
    gen = torch.Generator().manual_seed(0)
    reg_mb = make_situation_register(ROLE_VOCAB, d=256, generator=gen, backend="multibank")
    assert isinstance(reg_mb, MultiBankAccumulateRegister)
    gen2 = torch.Generator().manual_seed(0)
    reg_flat = make_situation_register(ROLE_VOCAB, d=256, generator=gen2, backend="flat")
    assert isinstance(reg_flat, AccumulateRegister)
    assert not isinstance(reg_flat, MultiBankAccumulateRegister)
    try:
        make_situation_register(ROLE_VOCAB, d=256, generator=gen, backend="bogus")
        raise AssertionError("expected ValueError for unknown backend")
    except ValueError:
        pass


def test_dropin_identical_decode_at_small_scale() -> None:
    """Same seed, same writes -> multibank and flat predict the SAME role at every position
    and agree on .entities() -- no decode-outcome regression at the scale the active pipeline
    runs at today. Also asserts both margins are non-trivial (>0), i.e. the coherence-margin
    signal self_improving_loop.decode_coherence_margins reads is meaningful under either
    backend, not that the two magnitudes coincide (see module docstring)."""
    d = 256
    max_slots = 8
    seed = 7
    gen_mb = torch.Generator().manual_seed(seed)
    reg_mb = make_situation_register(ROLE_VOCAB, d, gen_mb, max_event_slots=max_slots, backend="multibank")
    gen_flat = torch.Generator().manual_seed(seed)
    reg_flat = make_situation_register(ROLE_VOCAB, d, gen_flat, max_event_slots=max_slots, backend="flat")

    for entity, roles in SMALL_ENTITIES.items():
        for idx, role in enumerate(roles):
            reg_mb.add_event(entity, role, idx)
            reg_flat.add_event(entity, role, idx)

    assert set(reg_mb.entities()) == set(reg_flat.entities()) == set(SMALL_ENTITIES.keys())

    for entity, roles in SMALL_ENTITIES.items():
        for idx, true_role in enumerate(roles):
            pred_mb, scores_mb = reg_mb.decode(entity, idx)
            pred_flat, scores_flat = reg_flat.decode(entity, idx)
            assert pred_mb == pred_flat == true_role, (
                f"decode mismatch at small scale for {entity}@{idx}: "
                f"multibank={pred_mb} flat={pred_flat} true={true_role}"
            )
            margin_mb = sorted(scores_mb.values(), reverse=True)
            margin_flat = sorted(scores_flat.values(), reverse=True)
            m_mb = margin_mb[0] - margin_mb[1]
            m_flat = margin_flat[0] - margin_flat[1]
            assert m_mb > 0.0 and m_flat > 0.0, (
                f"non-trivial-margin check failed for {entity}@{idx}: "
                f"multibank_margin={m_mb:.6f} flat_margin={m_flat:.6f}"
            )


def test_single_event_entities_agree_across_backends() -> None:
    """The single-event control (both backends have only one bundle to route to) must be
    near-perfect under both backends, matching AccumulateRegister's own single-event control
    in verify_situation_model_accumulate.py."""
    d = 256
    gen_mb = torch.Generator().manual_seed(3)
    reg_mb = make_situation_register(ROLE_VOCAB, d, gen_mb, max_event_slots=8, backend="multibank")
    gen_flat = torch.Generator().manual_seed(3)
    reg_flat = make_situation_register(ROLE_VOCAB, d, gen_flat, max_event_slots=8, backend="flat")
    reg_mb.add_event("solo", "agent", 0)
    reg_flat.add_event("solo", "agent", 0)
    pred_mb, _ = reg_mb.decode("solo", 0)
    pred_flat, _ = reg_flat.decode("solo", 0)
    assert pred_mb == pred_flat == "agent"


def _decode_self_consistency(reg, entities_events: dict[str, list[int]], roles_written: dict[str, list[str]]) -> float:
    correct = 0
    total = 0
    for entity, slots in entities_events.items():
        for pos, slot in enumerate(slots):
            pred, _ = reg.decode(entity, slot)
            correct += int(pred == roles_written[entity][pos])
            total += 1
    return correct / total if total else 0.0


def test_high_load_multibank_holds_where_flat_degrades() -> None:
    """Capacity-retention claim, reduced scale for a fast witness (not a re-run of the full
    d=512/n_events=256/5-seed capacity cell -- that result is already MEASURED and cited in
    the module docstring; this only checks the SAME qualitative ordering holds so a future
    regression in either register's algebra is caught locally in seconds).

    At d=128 (deliberately small to force cross-talk cheaply) with 96 events packed onto ONE
    entity, the flat register's single bundle is overloaded and self-consistency drops well
    below 1.0, while multibank(n_banks=8) keeps per-bank load at ~12 events/bank and stays
    high. Uses ROLE_VOCAB (chance = 1/6 = 0.167) so a degraded flat register is visibly
    distinguishable from multibank, not just noisy."""
    d = 128
    n_events = 96
    n_banks = 8
    gen_mb = torch.Generator().manual_seed(11)
    reg_mb = make_situation_register(
        ROLE_VOCAB, d, gen_mb, max_event_slots=n_events, backend="multibank", n_banks=n_banks
    )
    gen_flat = torch.Generator().manual_seed(11)
    reg_flat = make_situation_register(ROLE_VOCAB, d, gen_flat, max_event_slots=n_events, backend="flat")

    roles_written = []
    for i in range(n_events):
        roles_written.append(ROLE_VOCAB[i % len(ROLE_VOCAB)])
        reg_mb.add_event("overloaded", roles_written[-1], i)
        reg_flat.add_event("overloaded", roles_written[-1], i)

    entities_events = {"overloaded": list(range(n_events))}
    roles_by_entity = {"overloaded": roles_written}

    acc_mb = _decode_self_consistency(reg_mb, entities_events, roles_by_entity)
    acc_flat = _decode_self_consistency(reg_flat, entities_events, roles_by_entity)

    # sha256-hash routing across n_banks is not perfectly uniform at this small n_events, so
    # allow generous slack around the average load (n_events/n_banks); the claim under test is
    # "meaningfully less than n_events" (i.e. routing happened), not exact balance.
    avg_load = n_events / n_banks
    assert reg_mb.max_bank_load("overloaded") <= avg_load * 2, (
        f"multibank per-bank load higher than expected: {reg_mb.max_bank_load('overloaded')} "
        f"(average={avg_load:.1f})"
    )
    assert acc_mb >= 0.95, f"multibank(n_banks={n_banks}) decode self-consistency degraded at high load: {acc_mb:.3f}"
    assert acc_flat <= 0.85, (
        f"flat register did not degrade as expected at n_events={n_events} (needed for a "
        f"meaningful comparison) -- got {acc_flat:.3f}; regime no longer discriminates"
    )
    assert acc_mb > acc_flat + 0.10, (
        f"multibank should clearly outperform flat at high per-entity event load: "
        f"multibank={acc_mb:.3f} flat={acc_flat:.3f}"
    )


def test_arms_differ_at_high_load() -> None:
    """META_RULE_AF-style arms-must-differ: multibank and flat registers are not
    bit-identical at high load (they route events differently by construction)."""
    d = 128
    n_events = 96
    gen_mb = torch.Generator().manual_seed(11)
    reg_mb = make_situation_register(ROLE_VOCAB, d, gen_mb, max_event_slots=n_events, backend="multibank", n_banks=8)
    gen_flat = torch.Generator().manual_seed(11)
    reg_flat = make_situation_register(ROLE_VOCAB, d, gen_flat, max_event_slots=n_events, backend="flat")
    for i in range(n_events):
        role = ROLE_VOCAB[i % len(ROLE_VOCAB)]
        reg_mb.add_event("overloaded", role, i)
        reg_flat.add_event("overloaded", role, i)
    vec_mb = reg_mb.register("overloaded")
    vec_flat = reg_flat.register("overloaded")
    assert not torch.equal(vec_mb, vec_flat), "multibank.register() bit-identical to flat.register() at high load"


def _run_all() -> None:
    test_factory_returns_declared_backend()
    test_dropin_identical_decode_at_small_scale()
    test_single_event_entities_agree_across_backends()
    test_high_load_multibank_holds_where_flat_degrades()
    test_arms_differ_at_high_load()


if __name__ == "__main__":
    _run_all()
    print("[verify_situation_model_multibank_dropin] PASS: multibank backend is drop-in "
          "identical to flat at small (pilot) scale, and retains decode self-consistency "
          "at high per-entity event load where flat degrades.")
