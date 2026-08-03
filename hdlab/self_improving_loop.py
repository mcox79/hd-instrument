"""Coherence-gated autonomous keep/revert controller (2026-08-02 promotion).

PROMOTION: locks in the self-improving loop's decision mechanism found + VET'd in
experiments/exp_coref_autonomous_fix_router_v1.py (commit 3d25cb038), per the USER "lock every
session gain into the durable substrate, not leave it archived in experiment cells" directive
(2026-08-02). Nothing here is new work: the two functions below are a faithful, byte-identical-
formula extraction of that cell's decode_margins_for_arm / _decide_autonomous, factored out so a
caller does not need to import an experiment module to reuse the controller. The cell itself is
left untouched (source of truth for the validated numbers).

SCOPE -- READ BEFORE USE (do not overclaim general autonomy):
  - Validated on DENSE content only: McGuffey g5g6 dense-pronoun-verbatim eval, where the
    autonomous (gold-free) router recovered ~67% of the oracle (gold-gated) router's achievable
    net gain over baseline, and correctly rejected 100% of a confirmed-negative "decay-window"
    trap lever using only its own coherence-margin signal (no label anywhere told it the trap
    lever was bad). See data/exp_coref_autonomous_fix_router_v1/metrics.json, eval_blocks.
    g5g6_reviewed for the exact numbers behind this claim.
  - CONTENT-DENSITY-GATED, not general-purpose: on the sparser combined_powered eval (mixed
    passage density) the same controller only TIES always-apply-all and shows FALSE_KEEP
    over-adoption -- it adopts on zero-gain coherence-margin spikes when there is not enough
    accumulated per-entity event structure to make the FHRR margin signal reliable. Do not
    deploy this controller on low-density / few-events-per-entity content without re-validating.
  - ADOPTION GRANULARITY = per (passage, candidate mechanism), not per individual decision.
    hdlab.coreference_resolver's resolvers each produce a cluster-id namespace scoped to their
    OWN full-passage resolution (entity "2" under resolver A and entity "2" under resolver B are
    different objects); stitching per-position picks from different resolutions into one array
    would silently corrupt whatever downstream (e.g. B3, situation-model query) scoring depends
    on that namespace. route_passage() below adopts a candidate's WHOLE resolution or none.

MECHANISM (glass-box; WIRE-DON'T-ISLAND -- reuses hdlab.situation_model_accumulate.
AccumulateRegister verbatim; does not reimplement coreference or the FHRR accumulate organ; does
not compute candidate resolutions itself -- callers supply them, typically from
hdlab.coreference_resolver): given a baseline whole-passage resolution and a library of candidate
whole-passage alternate resolutions of the SAME mention stream, decode_coherence_margins computes
the AccumulateRegister role-decode top1-vs-runner-up margin at every mention's own event slot
under a given cluster assignment (gold-free: no gold label is read anywhere in this module).
route_passage aggregates (mean) the per-candidate coherence-margin DELTA (candidate margin minus
baseline margin) over that candidate's changed-and-flagged positions and adopts whichever
candidate clears decide_keep_or_revert's abstain band above 0 (best candidate; ties / no evidence
-> keep baseline). Flagging (which positions are "worth routing") is the caller's responsibility
(the validated cell flags a pronoun decision iff hdlab.coreference_resolver.
run_strict_cb_instrumented reports n_compatible >= 2, i.e. real candidate competition) -- this
module does not embed a flagging policy.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Sequence

import torch

from hdlab.situation_model_accumulate import AccumulateRegister

ABSTAIN_BAND_DEFAULT = 0.02


def decode_coherence_margins(
    role_seq: Sequence[str],
    event_slots: Sequence[int],
    cluster_ids: Sequence[str],
    role_vocab: List[str],
    d: int,
    generator: torch.Generator,
    max_event_slots: int,
) -> List[float]:
    """Gold-free per-position coherence-margin signal: build a fresh AccumulateRegister from
    (role, event_slot) bound into whatever entity cluster_ids assigns each position to, then for
    every position decode that position's own (cluster, event_slot) and return the top1-vs-
    runner-up role-score margin. No gold label is read. Byte-identical construction to the
    validated exp_coref_autonomous_fix_router_v1.decode_margins_for_arm and
    probe_loop_autonomy_self_signal_v1.decode_margins_for_arm."""
    reg = AccumulateRegister(role_vocab, d, generator, max_event_slots=max_event_slots)
    for role, cid, slot in zip(role_seq, cluster_ids, event_slots):
        reg.add_event(cid, role, slot)
    margins: List[float] = []
    for cid, slot in zip(cluster_ids, event_slots):
        _pred, scores = reg.decode(cid, slot)
        vals = sorted(scores.values(), reverse=True)
        margins.append(vals[0] - vals[1] if len(vals) > 1 else vals[0])
    return margins


def decide_keep_or_revert(
    agg_deltas: Dict[str, float], abstain_band: float = ABSTAIN_BAND_DEFAULT
) -> Optional[str]:
    """Pure adoption rule (no data dependency): adopt the candidate with the highest aggregate
    coherence-margin delta iff it STRICTLY clears abstain_band above 0; else None (keep
    baseline). Empty input, all-negative input, and an exactly-at-band value all return None.
    Byte-identical to the validated cell's _decide_autonomous."""
    if not agg_deltas:
        return None
    best = max(agg_deltas, key=lambda name: agg_deltas[name])
    return best if agg_deltas[best] > abstain_band else None


def route_passage(
    role_seq: Sequence[str],
    event_slots: Sequence[int],
    baseline_cluster_ids: Sequence[str],
    candidate_cluster_ids: Dict[str, Sequence[str]],
    flagged_positions: Sequence[int],
    role_vocab: List[str],
    d: int,
    generator_factory: Callable[[], torch.Generator],
    max_event_slots: int,
    abstain_band: float = ABSTAIN_BAND_DEFAULT,
) -> dict:
    """The controller. Given one passage's mention stream already resolved by a baseline
    mechanism and by 1+ candidate mechanisms (each a same-length Sequence[str] of cluster ids --
    e.g. from hdlab.coreference_resolver.run_strict_cb vs run_principle_b_deixis), compute each
    candidate's gold-free coherence-margin delta over the positions where it BOTH changed the
    baseline's pick AND was flagged as worth routing, and adopt the best candidate's whole
    resolution if it clears abstain_band, else keep baseline (see module docstring, "ADOPTION
    GRANULARITY", for why this is per-candidate-whole-resolution, not per-decision).

    generator_factory must return a freshly-seeded torch.Generator (same seed every call) so the
    baseline decode and every candidate decode use an identical FHRR symbol table -- only the
    cluster assignment differs between calls. Typical caller: `lambda: torch.Generator().
    manual_seed(seed)`.

    Returns {"adopt": candidate_name_or_None, "adopted_cluster_ids": list[str],
    "per_candidate": {name: {"applicable": bool, "n_changed_flagged": int,
    "agg_coherence_delta": float|None}}}.
    """
    baseline_cluster_ids = list(baseline_cluster_ids)
    base_margins = decode_coherence_margins(
        role_seq, event_slots, baseline_cluster_ids, role_vocab, d, generator_factory(),
        max_event_slots,
    )

    per_candidate: Dict[str, dict] = {}
    agg_deltas: Dict[str, float] = {}
    for name, cand_ids in candidate_cluster_ids.items():
        cand_ids = list(cand_ids)
        assert len(cand_ids) == len(baseline_cluster_ids), (
            f"candidate {name!r} length {len(cand_ids)} != baseline length "
            f"{len(baseline_cluster_ids)}"
        )
        cand_margins = decode_coherence_margins(
            role_seq, event_slots, cand_ids, role_vocab, d, generator_factory(), max_event_slots,
        )
        changed_flagged = [p for p in flagged_positions if cand_ids[p] != baseline_cluster_ids[p]]
        deltas = [cand_margins[p] - base_margins[p] for p in changed_flagged]
        applicable = bool(changed_flagged)
        agg = (sum(deltas) / len(deltas)) if deltas else None
        per_candidate[name] = {
            "applicable": applicable,
            "n_changed_flagged": len(changed_flagged),
            "agg_coherence_delta": agg,
        }
        if applicable:
            agg_deltas[name] = agg

    adopt = decide_keep_or_revert(agg_deltas, abstain_band)
    adopted_cluster_ids = list(candidate_cluster_ids[adopt]) if adopt else baseline_cluster_ids
    return {
        "adopt": adopt,
        "adopted_cluster_ids": adopted_cluster_ids,
        "per_candidate": per_candidate,
    }
