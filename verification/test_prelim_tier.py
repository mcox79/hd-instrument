"""Scaffold-free witness for hdlab.prelim_tier (the promoted middle-tier "prelim" module,
2026-08-11 WIRE-don't-island promotion of TierState/update_prelim_and_generalize out of
experiments/exp_crutch_fade_social_iqa_v1.py -- see hdlab/prelim_tier.py module docstring).

Three load-bearing properties this witness asserts directly (per the promotion's own
behavior-preservation contract), using REAL hdlab.grounding_acquisition_loop.Library /
hdlab.hd_fact_store.HDFactStore / hdlab.script_grain_acquisition_loop.ScriptLibrary objects at
tiny scale (no mocks, no synthetic-only branch):

  (a) retain-forever: an item registered in TierState.prelim_lib NEVER leaves PENDING status,
      across any number of update_prelim_and_generalize passes (Library.flag()'s "reject once
      terminal" guard must never fire against it).
  (b) re-encounter PULL precedes raw-source fallback: a sub-threshold fact stored on
      encounter-1 (via update_prelim_and_generalize) is answerable from the PRELIM tier on
      encounter-2 -- proven here by a tiny priority-order resolver (mirrors the source cell's
      own native -> prelim -> raw-crutch routing) whose raw-source arm is a sentinel that FAILS
      the test if it is ever reached.
  (c) caller-supplied functions are load-bearing, not decorative: swapping cluster_key_fn for a
      trivial constant-key function measurably changes clustering (unrelated items merge into
      one cluster), proving the module actually calls through to the caller's function rather
      than falling back to a hardcoded default.

Also re-runs hdlab.prelim_tier.self_test() (the module's own real-code-path self-test, mirroring
the source cell's self_test() sections 8-12) as an independent pass/fail signal.

Passes with tracing=False (no trace bus configured anywhere in this file; hdlab.tracing.emit is
a no-op by default -- nothing here opts in).
"""
from __future__ import annotations

import os
import sys

_REPO = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

import hdlab.prelim_tier as prelim_tier  # noqa: E402
from hdlab.grounding_acquisition_loop import context_vector  # noqa: E402
from hdlab.script_grain_acquisition_loop import build_instance_register, calibrate_novelty_threshold  # noqa: E402


def _retain_item(state: prelim_tier.TierState, pk: str, n_traces: int, text_prefix: str) -> None:
    for i in range(n_traces):
        cvec = context_vector(f"{text_prefix} repeated event occurrence, day {i}, calm weather.")
        state.prelim_lib.flag(pk, f"{pk}_{i}", "POS", cvec, 0)


def test_module_self_test_passes() -> None:
    """The module's own self-test (real Library/HDFactStore/ScriptLibrary objects, mirrors the
    source cell's self_test() sections 8-12) must pass and report every check True."""
    result = prelim_tier.self_test()
    assert all(result.values()), f"prelim_tier.self_test() reported a failing check: {result}"


def test_retain_forever_never_leaves_pending() -> None:
    """(a) An item in TierState.prelim_lib must NEVER leave PENDING status, across repeated
    update_prelim_and_generalize passes, including after it becomes eligible for (and receives)
    combined-evidence promotion into native_store_gen. This is the "retain forever, never
    discard" property the middle tier needs -- distinct from the BASE Library (used for the
    strict foundation gate elsewhere via consolidation_pass), which DOES terminalize."""
    state = prelim_tier.TierState(seed_base=10)
    pk = prelim_tier.default_pair_key("kettle", "boil")
    cluster_key_fn = lambda pk_: "same_family"  # noqa: E731

    _retain_item(state, pk, n_traces=12, text_prefix="kettle boiling")
    assert state.prelim_lib.items[pk].status == "PENDING"

    for pass_idx in range(5):
        diag = prelim_tier.update_prelim_and_generalize(state, cluster_key_fn, novelty_thresh=0.15)
        assert state.prelim_lib.items[pk].status == "PENDING", (
            f"retain-forever violated on pass {pass_idx}: status="
            f"{state.prelim_lib.items[pk].status}, diag={diag}")


def test_pull_precedes_raw_source_fallback_on_reencounter() -> None:
    """(b) A sub-threshold fact stored on encounter-1 must be answerable from the PRELIM tier
    on encounter-2, and a caller's own priority-order routing (native -> prelim -> raw source,
    mirroring the source cell's resolve_item) must never reach the raw-source arm once PRELIM
    has the answer. The raw-source arm below is a sentinel that raises if invoked -- if the
    routing logic incorrectly skipped past a live PRELIM hit, this test would fail loudly
    rather than silently passing on the wrong tier."""
    state = prelim_tier.TierState(seed_base=20)
    pk = prelim_tier.default_pair_key("engine", "stall")
    cluster_key_fn = lambda pk_: "mechanical"  # noqa: E731

    # encounter-1: sub-threshold exposure (n=5 < promote_min_exposure=8) -- must RETAIN, not
    # promote (cluster size 1 < CLUSTER_MIN_MEMBERS=3).
    _retain_item(state, pk, n_traces=5, text_prefix="engine stalled again")
    diag = prelim_tier.update_prelim_and_generalize(state, cluster_key_fn, novelty_thresh=0.15)
    assert diag["newly_retained"] == 1, diag
    assert state.native_store_gen.query(pk, "OUTCOME_POLARITY") == [], (
        "a lone sub-threshold item must not already be native-promoted (test setup invariant)")

    def _raw_source_sentinel(_pk: str) -> str:
        raise AssertionError(
            "raw-source fallback reached despite a live PRELIM hit -- PULL-before-fallback "
            "priority order violated")

    def answer_item(query_pk: str) -> str:
        """Mirrors the source cell's native -> prelim -> raw-crutch priority order (the ONLY
        real precedent on disk for how a caller uses this tier; see design audit
        notes/director_three_tier_knowledge_architecture_design_audit_2026-08-11.md "FUSE" note
        -- strict priority order, not score fusion)."""
        native_hit = state.native_store_gen.query(query_pk, "OUTCOME_POLARITY")
        if native_hit and native_hit[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"):
            return "NATIVE_RESOLVED"
        prelim_hit = state.prelim_store.query(query_pk, "OUTCOME_POLARITY")
        if prelim_hit and prelim_hit[0]["status"] in ("ACTIVE", "COMBINED", "FLAGGED"):
            return "PRELIM_RESOLVED"
        return _raw_source_sentinel(query_pk)

    # encounter-2 (re-encounter): must resolve via PRELIM, never reaching the raw-source arm.
    tag = answer_item(pk)
    assert tag == "PRELIM_RESOLVED", f"expected PRELIM_RESOLVED at re-encounter, got {tag}"


def test_caller_supplied_cluster_key_fn_is_load_bearing() -> None:
    """(c) cluster_key_fn is actually consulted, not silently ignored: two items that get
    DIFFERENT cluster keys must land in DIFFERENT clusters; the SAME two items under a trivial
    constant-key function must collapse into ONE cluster. Uses two independent TierState
    instances (not two passes over the same state) so pk_cluster's sticky-membership guard
    cannot itself explain the difference.

    novelty_thresh is CALIBRATED (via script_grain_acquisition_loop.calibrate_novelty_threshold,
    exactly mirroring the source cell's own self_test "DG over-merge tripwire" -- see
    exp_crutch_fade_social_iqa_v1.py self_test() section (11)), not a hand-picked magic number:
    both retained items vote POS here, so their CA3/DG registers share the CONSEQUENT role term
    regardless of cluster key (MEASURED: two same-consequent, different-trigger registers score
    cosine~0.25; two same-consequent, same-trigger registers score cosine~0.46) -- a fixed
    threshold picked without calibration (e.g. the module's own NOVELTY_THRESH fallback-only
    constant) can sit on the wrong side of that gap by accident, exactly the failure mode
    calibration exists to avoid."""
    pk_a = prelim_tier.default_pair_key("rain", "wet")
    pk_b = prelim_tier.default_pair_key("boat", "fix")

    calib = calibrate_novelty_threshold(
        matched_pairs=[(build_instance_register("a", "b", "causes", "OUTCOME_POS"),
                       build_instance_register("c", "d", "causes", "OUTCOME_POS"))],
        wrong_pairs=[(build_instance_register("a", "b", "causes", "OUTCOME_POS"),
                     build_instance_register("c", "d", "xintent", "OUTCOME_POS"))])
    assert calib["discriminates"], f"calibration setup must discriminate: {calib}"
    novelty_thresh = calib["novelty_thresh"]

    def _build(cluster_key_fn):
        state = prelim_tier.TierState(seed_base=30)
        _retain_item(state, pk_a, n_traces=5, text_prefix="rain event")
        _retain_item(state, pk_b, n_traces=5, text_prefix="boat repair event")
        prelim_tier.update_prelim_and_generalize(state, cluster_key_fn, novelty_thresh=novelty_thresh)
        return state

    distinguishing_key_fn = lambda pk: {pk_a: "causes", pk_b: "xintent"}[pk]  # noqa: E731
    trivial_key_fn = lambda pk: "SAME_FOR_EVERYTHING"  # noqa: E731

    state_distinct = _build(distinguishing_key_fn)
    state_merged = _build(trivial_key_fn)

    assert state_distinct.pk_cluster[pk_a] != state_distinct.pk_cluster[pk_b], (
        "distinguishing cluster_key_fn must keep unrelated items in separate clusters")
    assert state_merged.pk_cluster[pk_a] == state_merged.pk_cluster[pk_b], (
        "a constant cluster_key_fn must merge the same two items into ONE cluster -- if this "
        "fails, cluster_key_fn is not actually driving clustering (a hardcoded default would "
        "produce the SAME result regardless of what the caller passes in)")


def _run_all() -> None:
    test_module_self_test_passes()
    test_retain_forever_never_leaves_pending()
    test_pull_precedes_raw_source_fallback_on_reencounter()
    test_caller_supplied_cluster_key_fn_is_load_bearing()


if __name__ == "__main__":
    _run_all()
    print("[test_prelim_tier] PASS: retain-forever + pull-before-raw-fallback + "
          "caller-supplied-cluster_key_fn-is-load-bearing + module self_test all reproduced "
          "(tracing=False).")
