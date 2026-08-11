"""hdlab/prelim_tier.py -- middle tier ("prelim"): retain-forever + accumulate + CA3/DG-swept
combined-evidence generalization. Promoted 2026-08-11 out of a single experiment cell into a
reusable hdlab module (WIRE-don't-island; design audit
notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md, Gap G4 / "CONCRETE
BUILD SPEC" item [5] / "Minimal module inventory" item 3).

Source: `TierState` + `update_prelim_and_generalize`, extracted from
experiments/exp_crutch_fade_social_iqa_v1.py (class TierState ~L571, function
update_prelim_and_generalize ~L593-697, as of that cell's 2026-08-10 3-tier build). This is a
PROMOTION, not a redesign -- the gate math, control flow, and per-branch semantics are
byte-for-byte the same as the source; only the two Social-IQa/CSKG-specific dependencies are
now CALLER-SUPPLIED callables instead of hardcoded (see GENERALIZATION below). Behavior-
preservation is verified in verification/test_prelim_tier.py by reproducing the source cell's
own self-test fixtures (its self_test() sections 8-12) through this module with adapter
callables that replay the source's relation_family()/pk.split("::",1) logic exactly.

WHAT THIS IS (per the design audit's user's 5-step three-tier architecture, step 5): a MIDDLE
tier that is ALWAYS QUERIED FIRST (ahead of the raw external multi-source GATHER), ACCUMULATES
(retain-forever: items never leave PENDING, so Library.flag()'s "reject once terminal" guard
never fires against them), and is PERIODICALLY SWEPT for near-concept clusters (via the OWNED
CA3/DG attractor keying in hdlab.script_grain_acquisition_loop.ScriptLibrary.match_or_spawn) so
COMBINED evidence across related sub-threshold items can cross the same strict promotion gate a
single item alone cannot -- without the gate itself ever loosening (the cluster-grain gate is
STRICTLY stricter, never weaker, than the single-item gate: see CLUSTER_EXPOSURE_MULTIPLIER).

GENERALIZATION (2026-08-11, this promotion): the source cell's `relation_family(idx, pk)` (a
CSKG relation-type lookup keyed off a loaded CSKG edge index) and its implicit assumption that
every item key `pk` is an "a::b"-joined concept pair (used both for hub-degree exclusion and for
building the CA3/DG FHRR register via build_instance_register(a, b, ...)) are now CALLER-SUPPLIED
callables: `cluster_key_fn`, `register_fn`, `hub_score_fn`. This mirrors how hdlab.learner's
plugin registry (hdlab/learner/registry.py: learn()/apply() dispatch to a named hypothesis-space
plugin instead of a hardcoded estimator) generalized two prior one-off cells -- here the
generalization is direct callable injection (no registry needed; the caller has exactly one
clustering strategy per TierState instance). Nothing about item KEYS, clustering, or hub-
exclusion is CSKG- or Social-IQa-specific anymore: the module only assumes a `pk: str` opaque
item key (whatever string the caller used with Library.flag(pk, ...)). A caller whose keys ARE
"a::b" pairs (the source cell's own pair_key() shape) can use default_pair_key/default_register_fn
below unmodified; any other consumer (e.g. a future state-of-mind reasoning loop keying on
something other than concept pairs) supplies its own.

REUSE (wire-don't-island; every organ below is imported read-only, called verbatim, never
reimplemented):
  hdlab.grounding_acquisition_loop.Library / schema_consistency_split_half / _vote_margin / MIN_CONFIRM
  hdlab.hd_fact_store.HDFactStore
  hdlab.script_grain_acquisition_loop.ScriptLibrary / build_instance_register

ASCII-only. Deterministic throughout (no built-in hash(), sorted(set(...)) iteration order,
PROT-023/F.5 compliant -- inherited from the reused organs above; this module adds no new RNG use
of its own).
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Set

import numpy as np
import torch

from hdlab.grounding_acquisition_loop import (
    Library, MIN_CONFIRM, PROMOTE_MIN_EXPOSURE, PROMOTE_MIN_CONSISTENCY,
    schema_consistency_split_half, _vote_margin, Trace,
)
from hdlab.hd_fact_store import HDFactStore
from hdlab.script_grain_acquisition_loop import ScriptLibrary, build_instance_register

# ---- config (module defaults; every value below is a caller-overridable parameter, not a
# hardcoded constant baked into the gate logic -- these just preserve the source cell's own
# defaults so a straight port needs zero call-site changes beyond the two new required
# callables) ----
PRELIM_TRUST = "TRUST_LOW"                 # hd_fact_store TRUST_LEVEL ladder, reused unmodified
PRELIM_SCHEMA_THRESH = 0.10                # matches consolidation_pass's own default BANK gate
CLUSTER_MIN_MEMBERS = 3                    # min distinct items before a cluster's combined evidence
                                            # is even considered (avoids single-item "clusters")
CLUSTER_EXPOSURE_MULTIPLIER = 4            # coarser cluster-grain gate is STRICTER, never weaker,
                                            # than the single-item gate (source cell's disk-diagnosed
                                            # "never loosen the per-item gate" discipline)
DEFAULT_RELATION = "OUTCOME_POLARITY"      # hd_fact_store relation name for a retained/promoted item


def default_pair_key(a: str, b: str) -> str:
    """Symmetric 'a::b' pair-key builder -- the source cell's own pair_key(). NOT required by
    this module (any string scheme works as an item key); kept as a convenience for callers
    migrating concept-pair-shaped keys unmodified from exp_crutch_fade_social_iqa_v1.py."""
    lo, hi = (a, b) if a <= b else (b, a)
    return f"{lo}::{hi}"


def default_register_fn(pk: str, cluster_key: str, label: str) -> torch.Tensor:
    """Default CA3/DG FHRR register builder for '::'-joined pair keys (default_pair_key format;
    the source cell's ONLY register-building path). Splits pk into (agent, patient) on '::' and
    delegates to script_grain_acquisition_loop.build_instance_register(agent, patient,
    cluster_key, f"OUTCOME_{label}") -- byte-identical to the source cell's
    `a, b = pk.split("::", 1); build_instance_register(a, b, fam, f"OUTCOME_{label}")`. Callers
    whose item keys are NOT 'a::b' pairs must supply their own register_fn -- this default only
    makes sense for pair_key-shaped keys."""
    a, b = pk.split("::", 1)
    return build_instance_register(a, b, cluster_key, f"OUTCOME_{label}")


class TierState:
    """Bundles the middle-tier ('prelim') retain-forever store + CA3/DG generalization state for
    ONE logical side of a run (e.g. one arm, or 'real' vs a scramble control -- caller's choice;
    this module has no opinion on how many TierState instances a caller keeps alive at once).

    `prelim_lib` is a Library() instance that is NEVER passed through
    hdlab.grounding_acquisition_loop.consolidation_pass -- its items' .status is never mutated
    away from PENDING, so Library.flag()'s existing "reject once non-PENDING" guard never fires
    against it. This is exactly the "retain forever, never discard" property the middle tier
    needs: the BASE Library (used for the strict FOUNDATION gate elsewhere) terminalizes to
    GROUNDED/ESCALATED and then rejects new evidence -- correct for the strict gate, wrong for an
    always-accumulating middle tier, which is why a SEPARATE Library instance is used here rather
    than reusing the foundation one.

    `native_store_gen` is where BOTH single-item promotions (a caller typically mirrors its own
    consolidation_pass's promotion_log into this store -- see the source cell's
    `_mirror_single_promotions`, not reproduced here since it is a one-line caller-side loop, not
    part of the prelim-tier mechanism itself) AND this module's own combined-evidence cluster
    promotions land. A caller wanting to isolate combined-evidence-only promotions can instead
    read `promoted_cluster` (the set of item keys promoted via combined evidence specifically)."""

    def __init__(self, seed_base: int, n_dim: int = 2048, relation: str = DEFAULT_RELATION,
                 prelim_trust: str = PRELIM_TRUST) -> None:
        self.prelim_lib = Library()
        self.prelim_store = HDFactStore(n_dim=n_dim, seed=seed_base + 100, use_index=True)
        self.script_lib = ScriptLibrary()
        self.native_store_gen = HDFactStore(n_dim=n_dim, seed=seed_base + 200, use_index=True)
        self.pk_cluster: Dict[str, str] = {}            # item key -> ScriptLibraryItem.item_id (sticky)
        self.cluster_members: Dict[str, Set[str]] = {}  # item_id -> set(item key)
        self.promoted_single: Set[str] = set()           # item keys mirrored into native_store_gen
        self.promoted_cluster: Set[str] = set()          # item keys promoted via combined evidence
        self.relation = relation
        self.prelim_trust = prelim_trust


def update_prelim_and_generalize(state: TierState,
                                 cluster_key_fn: Callable[[str], str],
                                 novelty_thresh: float,
                                 *,
                                 register_fn: Callable[[str, str, str], torch.Tensor] = default_register_fn,
                                 min_confirm: int = MIN_CONFIRM,
                                 schema_thresh: float = PRELIM_SCHEMA_THRESH,
                                 promote_min_exposure: int = PROMOTE_MIN_EXPOSURE,
                                 promote_min_consistency: float = PROMOTE_MIN_CONSISTENCY,
                                 cluster_min_members: int = CLUSTER_MIN_MEMBERS,
                                 cluster_exposure_multiplier: int = CLUSTER_EXPOSURE_MULTIPLIER,
                                 hub_score_fn: Optional[Callable[[str], float]] = None,
                                 hub_score_thresh: float = float("inf"),
                                 trace_weight_fn: Optional[Callable[[List[Trace]], float]] = None,
                                 schema_min_half_size: int = 2,
                                 coherence_fn: Optional[Callable[[List[Trace], List[Trace]], float]] = None
                                 ) -> dict:
    """One checkpoint's PRELIM-retain + CA3/DG cluster-registration + combined-evidence-promotion
    pass. Reuses schema_consistency_split_half / _vote_margin (grounding_acquisition_loop, byte-
    identical to the single-item BANK gate) and ScriptLibrary.match_or_spawn / build_instance_
    register (script_grain_acquisition_loop, byte-identical to that module's own CA3/DG keying)
    -- no new gate math, only the wiring between owned organs plus caller-supplied
    generalization of the two Social-IQa/CSKG-specific pieces the source cell hardcoded.

    cluster_key_fn(pk) -> str: REQUIRED. Returns the clustering "family"/type label for item key
        pk (replaces the source cell's `relation_family(idx, pk)`, a CSKG relation-type lookup
        against a loaded edge index -- callers should supply whatever semantic-or-structural key
        groups "near concepts" for THEIR domain; the source cell's own follow-up experiment,
        exp_crutch_fade_social_iqa_v2_semantic_cluster_key.py, is a worked example of swapping
        this one function for a semantic-embedding key while holding everything else fixed).
    register_fn(pk, cluster_key, label) -> FHRR tensor: builds the CA3/DG register consumed by
        ScriptLibrary.match_or_spawn. Default (default_register_fn) assumes pk is an "a::b" pair
        key (default_pair_key format, the source cell's ONLY case); supply your own for any other
        key shape.
    hub_score_fn(pk) -> float, optional: if given, any item whose hub_score_fn(pk) exceeds
        hub_score_thresh is excluded from BOTH retain and cluster-registration (generalizes the
        source cell's HUB_DEGREE_THRESH hub-concept exclusion, which hardcoded a node_degree dict
        keyed by `pk.split("::", 1)` halves). Default None disables hub exclusion entirely
        (backward-compatible with callers that have no hub-degree concept).
    trace_weight_fn(traces) -> float, optional (2026-08-11, additive; default None preserves the
        exact prior raw-trace-count RETAIN gate byte-for-byte): used IN PLACE OF len(it.traces)
        for the min_confirm eligibility check below -- the THIS-IS-THE-GATE the independence-
        weighted-corroboration drill targets (see notes/2026-08-11 genuine-cross-source-
        corroboration drill; this is "before an item is even retained-into-middle/cluster-
        registered"). schema_min_half_size threads through to schema_consistency_split_half
        unchanged (default 2 preserves the prior n<4->None floor; a caller lowering min_confirm
        below 4 via trace_weight_fn should also consider lowering this, else the schema-coherence
        guard becomes the new binding floor -- see that function's own docstring).
    coherence_fn(half_a_traces, half_b_traces) -> float, optional (2026-08-11, additive; default
        None preserves the exact prior raw-context-vec-cosine RETAIN-gate schema check byte-for-
        byte): threads through UNCHANGED to schema_consistency_split_half's own coherence_fn
        parameter -- lets a caller replace the surface-word-overlap coherence check (the SAME
        second floor trace_weight_fn's own docstring above names) with a graded, meaning-based
        metric (e.g. concept_similarity-based cross-source paraphrase alignment) without this
        module knowing anything about words or concepts, same "organ stays generic" discipline as
        every other caller-supplied hook in this module.

    Returns a per-pass report dict; mutates `state` in place. Field names match the source cell's
    own tier_diag_log entries exactly (newly_retained, n_hub_excluded, n_prelim_pending_items,
    n_clusters, n_clusters_eligible_size, n_combined_promoted_total, n_combined_promoted_this_pass)
    so an existing caller's downstream reporting/metrics code needs no changes."""
    newly_retained = 0
    n_hub_excluded = 0
    for pk in sorted(state.prelim_lib.items):
        it = state.prelim_lib.items[pk]
        n = len(it.traces)
        confirm_score = float(n) if trace_weight_fn is None else float(trace_weight_fn(it.traces))
        if confirm_score < min_confirm:
            continue
        if hub_score_fn is not None and hub_score_fn(pk) > hub_score_thresh:
            n_hub_excluded += 1
            continue
        score = schema_consistency_split_half(it.traces, min_half_size=schema_min_half_size,
                                              coherence_fn=coherence_fn)
        if score is None or score < schema_thresh:
            continue
        margin, pos, neg = _vote_margin(it.traces)
        if margin == 0.0:
            continue
        label = "POS" if margin > 0 else "NEG"
        # RETAIN (idempotent -- CONSISTENT_DUP if already live with the same object)
        existing = state.prelim_store.query(pk, state.relation)
        if not existing:
            state.prelim_store.store(pk, state.relation, label, "prelim_retain", state.prelim_trust)
            newly_retained += 1
        # register into the CA3/DG cluster ONCE (sticky membership; avoid churn on re-evaluation)
        if pk not in state.pk_cluster:
            fam = cluster_key_fn(pk)
            reg = register_fn(pk, fam, label)
            item_id, spawned, m_score = state.script_lib.match_or_spawn(
                reg, pk, label, it.traces[0].context_vec, 0, true_type=fam,
                novelty_thresh=novelty_thresh)
            state.pk_cluster[pk] = item_id
            state.cluster_members.setdefault(item_id, set()).add(pk)

    # combined-evidence promotion: pull each member's OWN current traces fresh (no separate
    # bookkeeping to go stale) and evaluate the IDENTICAL single-item gate at cluster grain, over
    # the AGREEING subset of members only (fidelity guard) -- a member whose OWN vote opposes the
    # cluster's provisional majority is EXCLUDED from the evidence pool (so one dissenter cannot
    # block the whole cluster's genuinely-agreeing majority from promoting) AND never
    # force-promoted under the majority's label (bounded leakage, not just an aggregate dilution
    # that happens to fail the gate).
    n_combined_promoted_this_pass = 0
    for item_id, members in state.cluster_members.items():
        if len(members) < cluster_min_members:
            continue
        provisional_traces = []
        for pk in members:
            provisional_traces.extend(state.prelim_lib.items[pk].traces)
        if not provisional_traces:
            continue
        prov_margin, _, _ = _vote_margin(provisional_traces)
        if prov_margin == 0.0:
            continue
        majority_positive = prov_margin > 0
        agreeing_members, agreeing_traces = [], []
        for pk in members:
            own_margin, _, _ = _vote_margin(state.prelim_lib.items[pk].traces)
            if own_margin != 0.0 and (own_margin > 0) != majority_positive:
                continue  # dissenter: excluded from the evidence pool AND never promoted
            agreeing_members.append(pk)
            agreeing_traces.extend(state.prelim_lib.items[pk].traces)
        margin, pos, neg = _vote_margin(agreeing_traces)
        exposure = len(agreeing_traces)
        consistency = abs(margin)
        # cluster-grain gate is STRICTER than the single-item gate (never weaker) -- coarser
        # relation-family evidence needs a bigger, more convincing sample before its majority is
        # trustworthy.
        cluster_exposure_floor = promote_min_exposure * cluster_exposure_multiplier
        if exposure < cluster_exposure_floor or consistency < promote_min_consistency or margin == 0.0:
            continue
        cluster_label = "POS" if margin > 0 else "NEG"
        trust_sym = "TRUST_HIGH" if consistency >= 0.9 else "TRUST_MID"
        for pk in agreeing_members:
            if pk in state.promoted_cluster:
                continue
            state.native_store_gen.store(pk, state.relation, cluster_label,
                                         "combined_evidence_cluster", trust_sym)
            state.promoted_cluster.add(pk)
            n_combined_promoted_this_pass += 1
    return {
        "newly_retained": newly_retained,
        "n_hub_excluded": n_hub_excluded,
        "n_prelim_pending_items": len(state.prelim_lib.items),
        "n_clusters": len(state.cluster_members),
        "n_clusters_eligible_size": sum(1 for m in state.cluster_members.values()
                                        if len(m) >= cluster_min_members),
        "n_combined_promoted_total": len(state.promoted_cluster),
        "n_combined_promoted_this_pass": n_combined_promoted_this_pass,
    }


def self_test() -> dict:
    """Fast off-disk gate exercising the REAL code path (real Library / HDFactStore /
    ScriptLibrary / match_or_spawn objects, not a synthetic-only branch), per exp_dev SCHEMA-VET
    F.1. Mirrors sections 8-12 of experiments/exp_crutch_fade_social_iqa_v1.py's own self_test()
    (the source cell's own fixtures for this exact mechanism), using default_pair_key /
    default_register_fn as the caller-supplied adapters -- proving the generalized module
    reproduces the source cell's exact retain/pull/combined-evidence/fidelity-guard/hub-exclusion
    behavior. See verification/test_prelim_tier.py for the scaffold-free, tracing=False witness
    (this function is the shared exercised-code-path; the verification test additionally checks
    determinism and the "caller-supplied functions are actually used" swap-in-a-trivial-key
    requirement)."""
    from hdlab.grounding_acquisition_loop import context_vector

    def relation_family(pk: str, idx: Dict[str, str]) -> str:
        """Tiny synthetic stand-in for the source cell's CSKG-index-backed relation_family(idx,
        pk) -- looks up a pre-populated {pk: family} map instead of a real edge index. Adapter
        for THIS self-test only; a real caller supplies whatever it wants via cluster_key_fn."""
        return idx.get(pk, "UNKNOWN")

    fam_map = {
        default_pair_key("boat", "fix"): "xintent",
        default_pair_key("wagon", "fix"): "xintent",
        default_pair_key("gate", "fix"): "xintent",
        default_pair_key("rain", "wet"): "causes",
    }
    cluster_key_fn = lambda pk: relation_family(pk, fam_map)  # noqa: E731

    # (1) sub-threshold retain: n=5 traces (< promote_min_exposure=8) must RETAIN into
    # prelim_store but NOT promote to native (cluster size 1 < CLUSTER_MIN_MEMBERS).
    state = TierState(seed_base=500)
    pk_sub = default_pair_key("boat", "fix")
    for i in range(5):
        cvec = context_vector(f"Owen wanted to fix the boat before the trip departed, day {i}.")
        state.prelim_lib.flag(pk_sub, f"pr{i}", "POS", cvec, 0)
    diag1 = update_prelim_and_generalize(state, cluster_key_fn, novelty_thresh=0.15)
    assert diag1["newly_retained"] == 1, diag1
    prelim_hit = state.prelim_store.query(pk_sub, "OUTCOME_POLARITY")
    assert prelim_hit and prelim_hit[0]["object"] == "POS", (
        f"sub-threshold (n=5 < promote_min_exposure=8) item must RETAIN into prelim_store, got {prelim_hit}")
    assert state.native_store_gen.query(pk_sub, "OUTCOME_POLARITY") == [], (
        "a lone sub-threshold item (cluster size 1 < CLUSTER_MIN_MEMBERS) must NOT promote to native")

    # (1b) items NEVER leave PENDING (retain-forever): re-running the pass on the SAME state
    # (idempotent) must leave the item's Library status PENDING, never terminalized, and must not
    # re-count it as newly-retained a second time.
    assert state.prelim_lib.items[pk_sub].status == "PENDING", (
        f"prelim_lib items must never leave PENDING (retain-forever), got "
        f"{state.prelim_lib.items[pk_sub].status}")
    diag1b = update_prelim_and_generalize(state, cluster_key_fn, novelty_thresh=0.15)
    assert diag1b["newly_retained"] == 0, "idempotent re-run must not re-retain an already-live item"
    assert state.prelim_lib.items[pk_sub].status == "PENDING", "still PENDING after a second pass"

    # (2) re-encounter PULL: the retained item must be answerable from prelim_store at
    # re-encounter (the fade lever) -- queried directly here (a caller's own answer-time routing,
    # e.g. the source cell's resolve_item, is downstream of this module and not reproduced here).
    pull_hit = state.prelim_store.query(pk_sub, "OUTCOME_POLARITY")
    assert pull_hit and pull_hit[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"), (
        f"a retained item must be live-queryable (PULL) at re-encounter, got {pull_hit}")

    # (3) combined-evidence promotion: 3 DISTINCT pairs sharing the SAME cluster key. The CLUSTER
    # gate is 4x stricter than the single-item gate (cluster_exposure_floor = 8*4 = 32) -- 12
    # traces/pair alone would NOT cross 32, but COMBINED (12x3=36 >= 32, consistency=1.0 >= 0.75)
    # all 3 cross via the shared cluster-grain decision.
    state2 = TierState(seed_base=600)
    cluster_pairs = [default_pair_key("boat", "fix"), default_pair_key("wagon", "fix"),
                     default_pair_key("gate", "fix")]
    for pk_c in cluster_pairs:
        for i in range(12):
            cvec = context_vector(f"{pk_c} needed repair on trip day {i}, weather was fine today.")
            state2.prelim_lib.flag(pk_c, f"{pk_c}_{i}", "POS", cvec, 0)
    diag2 = update_prelim_and_generalize(state2, cluster_key_fn, novelty_thresh=0.15)
    assert diag2["n_clusters_eligible_size"] >= 1, diag2
    assert diag2["n_combined_promoted_total"] == 3, (
        f"3 sub-threshold same-cluster-key pairs whose COMBINED evidence clears the gate must all "
        f"promote, got {diag2}")
    for pk_c in cluster_pairs:
        hit = state2.native_store_gen.query(pk_c, "OUTCOME_POLARITY")
        assert hit and hit[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"), (
            f"{pk_c} must be live in native_store_gen after combined-evidence promotion, got {hit}")

    # (4) fidelity guard: a 4th cluster member whose OWN evidence DISAGREES with the cluster's
    # combined majority must NOT be force-promoted under the cluster's label, AND must not block
    # the 3 genuinely-agreeing members from promoting.
    state3 = TierState(seed_base=700)
    for pk_c in cluster_pairs:
        for i in range(12):
            cvec = context_vector(f"{pk_c} needed repair on trip day {i}, weather was fine today.")
            state3.prelim_lib.flag(pk_c, f"{pk_c}_{i}", "POS", cvec, 0)
    fam_map2 = dict(fam_map)
    pk_dissent = default_pair_key("gate", "lock")
    fam_map2[pk_dissent] = "xintent"
    cluster_key_fn2 = lambda pk: relation_family(pk, fam_map2)  # noqa: E731
    diag_reg = update_prelim_and_generalize(state3, cluster_key_fn2, novelty_thresh=0.15)
    assert all(pk_c in state3.promoted_cluster for pk_c in cluster_pairs), (
        f"the 3 clean members must promote on their own combined evidence first, got {diag_reg}")
    for i in range(6):
        cvec = context_vector(f"{pk_dissent} early day {i}.")
        state3.prelim_lib.flag(pk_dissent, f"d{i}", "POS", cvec, 0)
    for i in range(6, 16):
        cvec = context_vector(f"{pk_dissent} later day {i}.")
        state3.prelim_lib.flag(pk_dissent, f"d{i}", "NEG", cvec, 0)
    own_m, _, _ = _vote_margin(state3.prelim_lib.items[pk_dissent].traces)
    assert own_m < 0, f"test construction failed: pk_dissent's own margin must be negative, got {own_m}"
    shared_cluster_id = state3.pk_cluster[cluster_pairs[0]]
    state3.pk_cluster[pk_dissent] = shared_cluster_id
    state3.cluster_members[shared_cluster_id].add(pk_dissent)
    diag4 = update_prelim_and_generalize(state3, cluster_key_fn2, novelty_thresh=0.15)
    assert pk_dissent not in state3.promoted_cluster, (
        f"a member whose OWN evidence opposes the cluster majority must NOT be force-promoted "
        f"(guard failed): diag={diag4}")
    assert all(pk_c in state3.promoted_cluster for pk_c in cluster_pairs), (
        "the 3 AGREEING members must still be (remain) promoted despite the dissenting member")

    # (5) hub-degree exclusion (generalized): a caller-supplied hub_score_fn must exclude a
    # high-score item from BOTH retain and cluster registration, and must be a no-op when omitted
    # (backward-compatible default).
    state5 = TierState(seed_base=900)
    pk_hub = default_pair_key("happy", "party")
    for i in range(6):
        cvec = context_vector(f"happy party day {i}, everyone felt happy about it.")
        state5.prelim_lib.flag(pk_hub, f"h{i}", "POS", cvec, 0)
    hub_scores = {default_pair_key("happy", "party"): 8000.0}
    hub_fn = lambda pk: hub_scores.get(pk, 0.0)  # noqa: E731
    diag_nohub = update_prelim_and_generalize(state5, cluster_key_fn, novelty_thresh=0.15,
                                              hub_score_fn=hub_fn, hub_score_thresh=30.0)
    assert diag_nohub["n_hub_excluded"] == 1, diag_nohub
    assert state5.prelim_store.query(pk_hub, "OUTCOME_POLARITY") == [], (
        "a hub-flagged pair must NOT retain into prelim_store regardless of exposure")
    state6 = TierState(seed_base=901)
    for i in range(6):
        cvec = context_vector(f"happy party day {i}, everyone felt happy about it.")
        state6.prelim_lib.flag(pk_hub, f"h{i}", "POS", cvec, 0)
    diag_withhub = update_prelim_and_generalize(state6, cluster_key_fn, novelty_thresh=0.15)
    assert diag_withhub["n_hub_excluded"] == 0
    assert state6.prelim_store.query(pk_hub, "OUTCOME_POLARITY") != [], (
        "without hub_score_fn, retain behavior must be unchanged (backward-compatible default)")

    # (6) caller-supplied functions are ACTUALLY used: swap cluster_key_fn to a trivial
    # constant-key function and confirm clustering collapses to ONE cluster across families that
    # (1)/(3) kept separate (proves cluster_key_fn is load-bearing, not ignored).
    state7 = TierState(seed_base=1000)
    trivial_key_fn = lambda pk: "SAME_FOR_EVERYTHING"  # noqa: E731
    mixed_pairs = [default_pair_key("boat", "fix"), default_pair_key("rain", "wet")]
    for pk_m in mixed_pairs:
        for i in range(5):
            cvec = context_vector(f"{pk_m} event happened again, day {i}, ordinary circumstances.")
            state7.prelim_lib.flag(pk_m, f"t{i}", "POS", cvec, 0)
    update_prelim_and_generalize(state7, trivial_key_fn, novelty_thresh=0.15)
    cluster_ids = {state7.pk_cluster[pk_m] for pk_m in mixed_pairs}
    assert len(cluster_ids) == 1, (
        f"a constant cluster_key_fn must merge unrelated pairs into ONE cluster (proves the "
        f"caller-supplied function drives clustering), got {len(cluster_ids)} clusters: "
        f"{state7.pk_cluster}")

    # (7) coherence_fn (2026-08-11, additive): a caller-supplied coherence function must be
    # ACTUALLY consulted by the RETAIN gate (not silently ignored) -- a sentinel function that
    # always returns a score BELOW schema_thresh must block retain even though the default
    # (raw-cosine) metric on the SAME identical-context traces would retain; and a sentinel that
    # always returns a score ABOVE schema_thresh must retain even on genuinely-incoherent
    # (independent-random) context, proving the module no longer computes its own cosine at all
    # once coherence_fn is supplied (load-bearing, same convention as check (6) above).
    state8 = TierState(seed_base=1100)
    pk_coh = default_pair_key("boat", "fix")
    for i in range(5):
        cvec = context_vector(f"Owen wanted to fix the boat before the trip departed, day {i}.")
        state8.prelim_lib.flag(pk_coh, f"c{i}", "POS", cvec, 0)
    diag_blocked = update_prelim_and_generalize(state8, cluster_key_fn, novelty_thresh=0.15,
                                                coherence_fn=lambda a, b: 0.0)
    assert diag_blocked["newly_retained"] == 0, (
        f"coherence_fn returning a below-threshold score must block retain even on real coherent "
        f"context, got {diag_blocked}")
    assert state8.prelim_store.query(pk_coh, "OUTCOME_POLARITY") == [], (
        "coherence_fn=always-0.0 must prevent retain regardless of the default cosine metric")

    state9 = TierState(seed_base=1200)
    pk_incoh = default_pair_key("wagon", "fix")
    rng9 = np.random.default_rng(3)
    for i in range(5):
        cvec = rng9.choice([-1.0, 1.0], size=256)  # independent random noise -- genuinely incoherent
        state9.prelim_lib.flag(pk_incoh, f"n{i}", "POS", cvec, 0)
    diag_forced = update_prelim_and_generalize(state9, cluster_key_fn, novelty_thresh=0.15,
                                               coherence_fn=lambda a, b: 0.999)
    assert diag_forced["newly_retained"] == 1, (
        f"coherence_fn returning an above-threshold score must retain even on genuinely-incoherent "
        f"(independent-random) context -- proves the module computes NO cosine of its own once "
        f"coherence_fn is supplied, got {diag_forced}")
    assert state9.prelim_store.query(pk_incoh, "OUTCOME_POLARITY") != [], (
        "coherence_fn=always-0.999 must force retain on incoherent context (load-bearing proof)")

    print("[self-test] PASS: real Library/HDFactStore/ScriptLibrary objects exercised; "
          "retain-forever + re-encounter-pull + combined-evidence-promotion + fidelity-guard + "
          "generalized hub-exclusion + caller-supplied-cluster_key_fn-is-load-bearing + "
          "caller-supplied-coherence_fn-is-load-bearing all reproduced from "
          "experiments/exp_crutch_fade_social_iqa_v1.py's own fixtures", flush=True)
    return {
        "retain_ok": True,
        "retain_forever_pending_ok": True,
        "pull_ok": True,
        "combined_evidence_promotion_ok": True,
        "fidelity_guard_ok": True,
        "hub_exclusion_generalized_ok": True,
        "cluster_key_fn_load_bearing_ok": True,
        "coherence_fn_load_bearing_ok": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(self_test(), indent=2))
    print("ALL SELF-TESTS PASSED")
