"""Pre-dispatch VALIDITY PREFLIGHT: mechanize the fairness/validity disciplines.

Goal (USER 2026-07-11): "avoid bad tests, not catch them." Convert
remember-to-do fairness disciplines that today are only caught reactively in
landed-VET into cannot-skip gates that fire at SELF-TEST scale, BEFORE a run is
dispatched and wastes GPU/CPU time.

This module ADDS layers on top of the existing discriminator-fires gate
(experiments/_seed_checkpoint.assert_discriminator_fires + VacuousSmokeError).
It does NOT replace or weaken it. A cell's self_test() calls these asserts the
same way it already calls assert_discriminator_fires:

    from _validity_preflight import (
        assert_positive_control_passes,
        assert_metric_moves,
        assert_full_gates_exercised_at_selftest,
        assert_negative_control_fails_with_margin,
        assert_signature_compatible,
        assert_real_code_path_exercised,
        assert_guard_baseline_valid,
        run_validity_preflight,
    )

    ok &= assert_positive_control_passes(oracle_arm_cleared_bar, ...)
    ok &= assert_metric_moves(before=readout_null, after=readout_known_good, ...)
    ok &= assert_full_gates_exercised_at_selftest(FULL_GATES, exercised_here, ...)
    ok &= assert_negative_control_fails_with_margin(ctrl_scores, thresh, ...)

or, declaratively, one call the queue_add self-test path exercises through the
cell:

    ok &= run_validity_preflight([
        {"kind": "positive_control", "passed": oracle_cleared_bar, ...},
        {"kind": "metric_moves", "before": r0, "after": r1, ...},
        {"kind": "full_gates_exercised", "full_gates": [...], "exercised": {...}},
        {"kind": "negative_control_margin", "scores": [...], "threshold": t, ...},
    ], run_mode="selftest")

The 4 failure classes gated (each burned a real run in VET before this module):

  1. HARD-PASS BAR NOT PROVEN ACHIEVABLE. A must-fail scramble control was
     unwinnable by construction (degree-preserving scramble shortens paths, so
     "real beats scramble on median-hop" could never pass). GATE: a declared
     POSITIVE control (oracle/synthetic arm that SHOULD clear the HARD-PASS bar)
     must actually clear it at self-test scale; if it cannot, the bar is
     unwinnable or mis-directed -> flag.

  2. METRIC STRUCTURALLY FROZEN. FPE readout was EXACTLY 0.0 at 4/6 rungs while
     the direct readout climbed -- a broken readout masquerading as a negative.
     GATE: a reported metric must MOVE under a positive (known-good) input; an
     exact-frozen / exact-0.0 value that ignores input -> flag as possibly
     broken, not merely negative. Extends the telemetry-sensitivity discipline.

  3. FULL-MODE FAIL-CLOSED GATE NOT EXERCISED AT SELF-TEST. A split-identity
     assertion armed only at run_mode=full (self-test used assert_identity=false)
     -> fail-closed only after the expensive FULL. GATE: every fail-closed
     assertion the FULL arms must be exercised at self-test scale (tiny inputs).

  4. MUST-FAIL CONTROL NOT ROBUSTLY FAILING. A vacuous-smoke gate passed/failed
     nondeterministically (untrained control got lucky hits at small N). GATE:
     the must-fail control must fail DETERMINISTICALLY over repeats/seeds WITH
     MARGIN, not "failed once." Hardens assert_discriminator_fires from a single
     bool into a multi-repeat + margin check.

THREE MORE classes gated (2026-07-13, each burned a real REMOTE-gate/landed run):

  5. SELF-TEST EXERCISED A SYNTHETIC-ONLY PATH, NOT THE REAL SUBSTRATE API. A
     cell self-tested a toy branch and NEVER constructed the objects it uses at
     FULL (KGStore / the store-build helper / a fit module), so a signature/API
     bug slipped through the 0.2s local self-test and GATE_FAILed at the remote
     with `KGStore.__init__() got an unexpected keyword argument 'init_entities'`.
     GATE: the cell DECLARES the real substrate entrypoints its FULL run calls,
     plus the subset actually EXERCISED (constructed/called) during this self-
     test; any declared-but-not-exercised entrypoint -> flag (self-test is toy-
     only; the API-drift class of bug can only fail at the remote). Mirrors
     class 3's exercised-at-self-test shape, but for real code paths not gates.

  6. API/SIGNATURE DRIFT UNCHECKED. Cells invent kwargs/methods the live
     substrate does not have and never check the call against the actual current
     signature before ship. GATE: assert_signature_compatible binds each declared
     (callable, kwargs) against inspect.signature(callable) at self-test scale --
     an unexpected kwarg or a missing required arg fails LOCALLY in microseconds
     (no object constructed). Also advises when a kwarg maps to an OPTIONAL param
     (has a default): such version-specific kwargs may be absent on an out-of-sync
     remote (the local repo drifts thousands of commits ahead) -- prefer the
     portable/base call or verify remote parity.

  7. GUARD MIS-CALIBRATED AGAINST AN ARENA'S STRUCTURAL BASELINE. A
     control-beats-baseline break-guard (BROKEN_TEST_CONTROL_BEATS_POP) compared
     a control to POP, but POP is STRUCTURALLY ~0 on held-out-entity arenas
     (held-out tails have train-freq 0), so ANY live control clears it and the
     guard false-broke a real run. GATE: assert_guard_baseline_valid verifies the
     baseline a control-comparison guard fires against is NOT itself within eps of
     the arena floor (RANDOM / 1-over-N). A structurally-at-floor baseline means
     the guard mis-fires on this arena -> flag: compare the control to RANDOM /
     arm-floor, not to a structurally-zero incumbent.

ROLLOUT (warn-first). Read env VALIDITY_PREFLIGHT_MODE:
  - "warn" (DEFAULT): a DECLARED-and-failing check LOGS loudly to stderr with a
    [validity-preflight] WARN: prefix and the assert returns False (never
    raises) -- the self-test still exits 0 and the ship proceeds. This is the
    bake period. Collect warns; do not block good cells.
  - "enforce": a DECLARED-and-failing check RAISES ValidityPreflightError (an
    AssertionError subclass, mirroring VacuousSmokeError). That propagates out
    of the cell's --self-test -> non-zero exit -> queue_add.py step 3 fails the
    ship (existing exit-5 path). Flip to enforce only after a bake period and
    director sign-off.

  VALIDITY_PREFLIGHT_WARN=1 forces warn mode regardless (explicit override).

MISSING vs FAILING (backward-compat / migration):
  - A MISSING declaration (cell passed None / did not declare a positive control)
    always WARNs and returns True, even under enforce. Existing cells that have
    not opted in are never hard-blocked. Migration = declare the checks.
  - A DECLARED-and-failing check honors the mode (warn -> False+log; enforce ->
    raise).

No-op for FULL runs: like assert_discriminator_fires, every assert is a pass-
through when run_mode is not smoke/self_test. The FULL is the science, not a
gate self-check.

ASCII-only per feedback_ascii_only_in_scripts. No em-dashes in output.
"""
from __future__ import annotations

import inspect
import math
import os
import sys
from typing import Any, Callable, Iterable, Mapping, Optional, Sequence


# --------------------------------------------------------------------------- #
# Mode + error type                                                           #
# --------------------------------------------------------------------------- #

class ValidityPreflightError(AssertionError):
    """A DECLARED validity-preflight check failed under enforce mode.

    Subclass of AssertionError (mirrors VacuousSmokeError) so it propagates out
    of a cell's --self-test as a non-zero exit and fails the ship at
    queue_add.py step 3, exactly like the existing discriminator-fires gate.
    """


WARN_PREFIX = "[validity-preflight] WARN:"
BLOCK_PREFIX = "[validity-preflight] BLOCK:"


def _resolve_mode(mode: Optional[str]) -> str:
    """Return 'warn' or 'enforce'. Explicit arg > env > default 'warn'."""
    if mode is not None:
        m = str(mode).strip().lower()
        return "enforce" if m == "enforce" else "warn"
    # Explicit warn override wins over MODE for safety during bake.
    if str(os.environ.get("VALIDITY_PREFLIGHT_WARN", "")).strip().lower() in (
            "1", "true", "yes", "on"):
        return "warn"
    env_mode = str(os.environ.get("VALIDITY_PREFLIGHT_MODE", "")).strip().lower()
    return "enforce" if env_mode == "enforce" else "warn"


def _is_selftest_mode(run_mode: str) -> bool:
    return str(run_mode).lower().replace("-", "_") in (
        "smoke", "self_test", "selftest")


def _emit(msg: str, *, mode: str) -> bool:
    """Handle a DECLARED failure per mode. Returns False (check failed).

    warn    -> print WARN line to stderr, return False.
    enforce -> raise ValidityPreflightError.
    """
    if mode == "enforce":
        raise ValidityPreflightError(f"{BLOCK_PREFIX} {msg}")
    print(f"{WARN_PREFIX} {msg}", file=sys.stderr, flush=True)
    return False


def _emit_missing(msg: str) -> bool:
    """A MISSING declaration: always warn (even under enforce), return True."""
    print(f"{WARN_PREFIX} (missing-declaration) {msg}", file=sys.stderr,
          flush=True)
    return True


# --------------------------------------------------------------------------- #
# Class 1: positive control must clear the HARD-PASS bar                       #
# --------------------------------------------------------------------------- #

def assert_positive_control_passes(
        positive_control_passed_headline_gate: Optional[bool],
        *,
        control_name: str = "positive_control",
        headline_name: str = "headline",
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        remedy: str = ("the HARD-PASS bar is unwinnable or mis-directed at this "
                       "scale -- re-derive the bar against the test's info-"
                       "ceiling, or fix the oracle arm, before dispatch"),
        extra: str = "") -> bool:
    """A declared POSITIVE control (oracle arm) must CLEAR the HARD-PASS bar.

    positive_control_passed_headline_gate:
      True  -> the oracle/synthetic arm that SHOULD pass did clear the bar. OK.
      False -> it did NOT clear the bar at self-test scale. The bar is
               unwinnable / mis-directed by construction -> flag.
      None  -> cell did not declare a positive control. MISSING -> warn always,
               return True (migration path).

    Mechanizes the "compute the test info-ceiling / is-the-bar-achievable"
    discipline as a pre-dispatch gate.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)
    if positive_control_passed_headline_gate is None:
        return _emit_missing(
            f"no POSITIVE control declared for {control_name!r} vs "
            f"{headline_name!r}. Cannot prove the HARD-PASS bar is achievable. "
            f"Declare an oracle/synthetic arm that SHOULD clear the bar so an "
            f"unwinnable/mis-directed bar is caught pre-dispatch.")
    if not positive_control_passed_headline_gate:
        return _emit(
            f"POSITIVE control {control_name!r} did NOT clear the "
            f"{headline_name!r} HARD-PASS bar at run_mode={run_mode}. If the arm "
            f"that SHOULD pass cannot, the bar is unwinnable or mis-directed and "
            f"no substrate truth could ever pass it. Remedy: {remedy}."
            + (f" {extra}" if extra else ""),
            mode=resolved)
    return True


# --------------------------------------------------------------------------- #
# Class 2: metric must move under a positive perturbation                      #
# --------------------------------------------------------------------------- #

def assert_metric_moves(
        *,
        metric_name: str,
        before: Optional[float] = None,
        after: Optional[float] = None,
        values: Optional[Sequence[float]] = None,
        min_delta: float = 1e-9,
        flag_exact_zero: bool = True,
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        extra: str = "") -> bool:
    """A reported metric must MOVE under a known-good (positive) perturbation.

    Two declaration forms (provide exactly one):

      before/after: `before` is the readout on a null/negative input, `after` is
        the readout on a KNOWN-GOOD input that SHOULD drive the metric. Flag if
        abs(after - before) < min_delta (did not move), or (flag_exact_zero and
        both are exactly 0.0) -- a readout stuck at exactly 0.0 on a known-good
        input is likely broken, not a genuine negative.

      values: a sequence of readouts across known-good conditions (e.g. ladder
        rungs). Flag if all values are exactly equal (frozen), or
        (flag_exact_zero and all values are exactly 0.0).

    Declaring NEITHER form (all None) is MISSING -> warn always, return True.

    Extends the telemetry-sensitivity discipline: a metric that ignores input
    auto-passes / fakes robustness. Root failure it closes: FPE readout EXACTLY
    0.0 at 4/6 rungs while the direct readout climbed.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)

    have_pair = before is not None and after is not None
    have_values = values is not None

    if not have_pair and not have_values:
        return _emit_missing(
            f"no move-check declared for metric {metric_name!r}. Provide "
            f"before/after (null vs known-good input) or a values series so a "
            f"structurally frozen / exact-0.0 readout is caught pre-dispatch.")

    if have_pair:
        b = float(before)
        a = float(after)
        if not (math.isfinite(a) and math.isfinite(b)):
            return _emit(
                f"metric {metric_name!r} is non-finite (before={b}, after={a}); "
                f"cannot prove it moves.", mode=resolved)
        if flag_exact_zero and a == 0.0 and b == 0.0:
            return _emit(
                f"metric {metric_name!r} is EXACTLY 0.0 on both the null and the "
                f"known-good input at run_mode={run_mode}. A readout stuck at "
                f"0.0 under a known-good input is likely BROKEN, not a genuine "
                f"negative. Verify the readout wiring before dispatch."
                + (f" {extra}" if extra else ""), mode=resolved)
        if abs(a - b) < min_delta:
            return _emit(
                f"metric {metric_name!r} did NOT move under a known-good "
                f"perturbation (before={b}, after={a}, |delta|={abs(a - b):.3g} "
                f"< min_delta={min_delta:g}) at run_mode={run_mode}. A metric "
                f"that ignores input auto-passes and fakes robustness; it may be "
                f"structurally frozen / broken." + (f" {extra}" if extra else ""),
                mode=resolved)
        return True

    # values form
    vals = [float(v) for v in values]  # type: ignore[arg-type]
    if len(vals) == 0:
        return _emit_missing(
            f"empty values series for metric {metric_name!r}; nothing to check.")
    if any(not math.isfinite(v) for v in vals):
        return _emit(
            f"metric {metric_name!r} values contain a non-finite entry: {vals}.",
            mode=resolved)
    if flag_exact_zero and all(v == 0.0 for v in vals):
        return _emit(
            f"metric {metric_name!r} is EXACTLY 0.0 at EVERY known-good "
            f"condition ({len(vals)} entries) at run_mode={run_mode}. A readout "
            f"stuck at 0.0 across all inputs is likely BROKEN, not a genuine "
            f"negative." + (f" {extra}" if extra else ""), mode=resolved)
    vmin, vmax = min(vals), max(vals)
    if (vmax - vmin) < min_delta:
        return _emit(
            f"metric {metric_name!r} is FROZEN across all {len(vals)} known-good "
            f"conditions (range={vmax - vmin:.3g} < min_delta={min_delta:g}, "
            f"constant={vals[0]}) at run_mode={run_mode}. It does not respond to "
            f"input; likely structurally frozen / broken."
            + (f" {extra}" if extra else ""), mode=resolved)
    return True


# --------------------------------------------------------------------------- #
# Class 3: FULL fail-closed gates must be exercised at self-test scale         #
# --------------------------------------------------------------------------- #

def assert_full_gates_exercised_at_selftest(
        full_fail_closed_gates: Optional[Iterable[str]],
        exercised_gates: Optional[Iterable[str]],
        *,
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        extra: str = "") -> bool:
    """Every fail-closed assertion the FULL arms must fire at self-test scale.

    full_fail_closed_gates: names of the fail-closed assertions the FULL run
      arms (e.g. "split_identity", "cardinality", "arms_differ"). Declaring None
      is MISSING -> warn always, return True.

    exercised_gates: names actually evaluated during THIS self-test (tiny
      inputs). Any FULL gate not in this set was armed only at run_mode=full and
      would fail-closed only after the expensive FULL -> flag.

    Root failure it closes: a GNN comparator's split-identity assertion armed
    only at run_mode=full (self-test used assert_identity=false), so a structural
    mismatch was caught only after the FULL.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)
    if full_fail_closed_gates is None:
        return _emit_missing(
            "no FULL fail-closed gate set declared. List the assertions the "
            "FULL arms (split_identity/cardinality/arms_differ/...) and the "
            "subset exercised at self-test so full-only gates are caught pre-"
            "dispatch.")
    declared = [str(g) for g in full_fail_closed_gates]
    exercised = set(str(g) for g in (exercised_gates or []))
    missing = [g for g in declared if g not in exercised]
    if missing:
        return _emit(
            f"FULL fail-closed gate(s) {missing} are NOT exercised at "
            f"run_mode={run_mode} (exercised={sorted(exercised)}). These arm "
            f"only at run_mode=full, so a structural mismatch (split-identity / "
            f"cardinality / arms-differ) would fail-closed only AFTER the "
            f"expensive FULL. Exercise them on tiny inputs at self-test."
            + (f" {extra}" if extra else ""), mode=resolved)
    return True


# --------------------------------------------------------------------------- #
# Class 4: must-fail control fails deterministically with margin               #
# --------------------------------------------------------------------------- #

def assert_negative_control_fails_with_margin(
        control_scores: Optional[Sequence[float]],
        headline_threshold: float,
        *,
        higher_is_pass: bool = True,
        margin: float = 0.0,
        n_repeats_min: int = 3,
        control_name: str = "negative_control",
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        extra: str = "") -> bool:
    """The must-fail control must fail DETERMINISTICALLY over repeats WITH MARGIN.

    control_scores: the negative/must-fail control's headline score on each
      repeat/seed. Declaring None is MISSING -> warn always, return True.

    headline_threshold + higher_is_pass define the PASS region:
      higher_is_pass=True  -> pass means score >= threshold; a robust FAIL needs
                              score <= threshold - margin on EVERY repeat.
      higher_is_pass=False -> pass means score <= threshold; a robust FAIL needs
                              score >= threshold + margin on EVERY repeat.

    Flag if fewer than n_repeats_min repeats (cannot prove determinism), or if
    ANY repeat lands in the PASS region or within `margin` of it (a lucky hit /
    no-margin fail).

    Hardens assert_discriminator_fires (a single bool) into a multi-repeat +
    margin check. Root failure it closes: a vacuous-smoke gate that passed/failed
    nondeterministically because an untrained control got lucky hits at small N.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)
    if control_scores is None:
        return _emit_missing(
            f"no repeated must-fail control scores declared for {control_name!r}."
            f" Provide >= {n_repeats_min} repeat/seed scores so nondeterministic "
            f"'failed once' controls are caught pre-dispatch.")
    scores = [float(s) for s in control_scores]
    if any(not math.isfinite(s) for s in scores):
        return _emit(
            f"must-fail control {control_name!r} has a non-finite score: "
            f"{scores}.", mode=resolved)
    if len(scores) < n_repeats_min:
        return _emit(
            f"must-fail control {control_name!r} has only {len(scores)} "
            f"repeat(s) (< n_repeats_min={n_repeats_min}) at run_mode={run_mode}."
            f" Cannot prove it fails DETERMINISTICALLY. A control that 'failed "
            f"once' can pass on the next seed (lucky hits at small N). Run more "
            f"repeats/seeds." + (f" {extra}" if extra else ""), mode=resolved)
    if margin < 0.0:
        return _emit(
            f"margin={margin} is negative for {control_name!r}; margin must be "
            f">= 0.", mode=resolved)

    # A repeat "robustly fails" iff it is strictly on the fail side by >= margin.
    def robustly_fails(s: float) -> bool:
        if higher_is_pass:
            return s <= headline_threshold - margin
        return s >= headline_threshold + margin

    offenders = [s for s in scores if not robustly_fails(s)]
    if offenders:
        worst = (max(offenders) if higher_is_pass else min(offenders))
        return _emit(
            f"must-fail control {control_name!r} does NOT fail robustly at "
            f"run_mode={run_mode}: {len(offenders)}/{len(scores)} repeat(s) "
            f"passed the headline or landed within margin={margin:g} of "
            f"threshold={headline_threshold:g} "
            f"(higher_is_pass={higher_is_pass}, worst offender={worst:g}, "
            f"all={scores}). The discriminator is nondeterministic; a green "
            f"verdict can be a lucky hit. Raise V/N or margin until the control "
            f"fails every repeat with margin." + (f" {extra}" if extra else ""),
            mode=resolved)
    return True


# --------------------------------------------------------------------------- #
# Class 5: self-test must EXERCISE the real substrate code path, not a toy one  #
# --------------------------------------------------------------------------- #

def assert_real_code_path_exercised(
        full_substrate_entrypoints: Optional[Iterable[str]],
        exercised_entrypoints: Optional[Iterable[str]],
        *,
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        extra: str = "") -> bool:
    """Every REAL substrate entrypoint the FULL uses must be exercised at self-test.

    full_substrate_entrypoints: names of the live-substrate objects/functions the
      FULL run constructs or calls (e.g. "KGStore", "build_store_with_codes",
      "ingest_triples", "fit_kge_anchor1"). Declaring None is MISSING -> warn
      always, return True (migration path).

    exercised_entrypoints: names actually constructed/called during THIS self-test
      (tiny inputs). Any FULL entrypoint NOT in this set means the self-test took a
      synthetic-only branch and never touched that real object -> a signature/API
      bug in it can only fail at the remote gate -> flag.

    Root failure it closes: exp_native_code_family_sweep_cskg_v1 passed a 0.2s
    self-test on a synthetic branch that never ran build_store_with_codes against
    the real KGStore, so `KGStore.__init__() got an unexpected keyword argument
    'init_entities'` GATE_FAILed only at the remote. Mirror of class 3, but for
    real code paths instead of fail-closed gates.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)
    if full_substrate_entrypoints is None:
        return _emit_missing(
            "no real-substrate-entrypoint set declared. List the live objects/"
            "functions the FULL constructs or calls (KGStore / store-build helper "
            "/ fit module) and the subset the self-test actually exercises, so a "
            "synthetic-only self-test that hides a signature/API bug is caught "
            "pre-dispatch.")
    declared = [str(g) for g in full_substrate_entrypoints]
    exercised = set(str(g) for g in (exercised_entrypoints or []))
    missing = [g for g in declared if g not in exercised]
    if missing:
        return _emit(
            f"real substrate entrypoint(s) {missing} are NOT exercised at "
            f"run_mode={run_mode} (exercised={sorted(exercised)}). The self-test "
            f"took a synthetic-only path and never constructed/called the REAL "
            f"object(s), so a signature/API drift in them (an unexpected kwarg, a "
            f"renamed method) can only fail at the remote gate. Construct/call the "
            f"REAL object(s) at tiny scale inside the self-test."
            + (f" {extra}" if extra else ""), mode=resolved)
    return True


# --------------------------------------------------------------------------- #
# Class 6: each substrate call must match the live signature (API-drift catch)  #
# --------------------------------------------------------------------------- #

def assert_signature_compatible(
        callable_obj: Optional[Callable[..., Any]],
        kwargs: Optional[Mapping[str, Any]] = None,
        *,
        args_count: int = 0,
        callable_name: Optional[str] = None,
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        warn_optional_kwargs: bool = True,
        extra: str = "") -> bool:
    """A substrate call's kwargs must bind against the live inspect.signature.

    callable_obj: the ACTUAL live callable the cell invokes (the imported KGStore
      class, the store-build helper, a fit function). Passing None is MISSING ->
      warn always, return True.
    kwargs: the keyword arguments the cell passes to it (values are ignored; only
      the KEYS are checked). args_count: number of POSITIONAL args the cell passes
      (so required-positional coverage is validated too).

    Uses inspect.signature(callable_obj).bind_partial(*placeholders, **kwargs):
      - an UNEXPECTED kwarg or a MISSING required parameter raises TypeError ->
        the call is INCOMPATIBLE with the live signature -> flag (fails LOCALLY in
        microseconds; no object is constructed).
      - if a passed kwarg maps to an OPTIONAL parameter (one with a default), emit
        an advisory: version-specific kwargs may be absent on an out-of-sync remote
        (the repo drifts thousands of commits ahead of the runner) -> prefer the
        portable/base call or verify remote parity. Advisory-only; does not fail.

    Root failure it closes: cells invent kwargs the live substrate lacks
    (`init_entities`) and never check the call against the real signature.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)
    if callable_obj is None:
        return _emit_missing(
            "no callable declared for a substrate-signature check. Pass the live "
            "callable (KGStore / store-build helper / fit fn) + the kwargs the "
            "cell uses so an invented/renamed kwarg is caught pre-dispatch.")
    name = callable_name or getattr(callable_obj, "__name__", repr(callable_obj))
    kw = dict(kwargs or {})
    try:
        sig = inspect.signature(callable_obj)
    except (ValueError, TypeError):
        # Builtins / C-extensions can be un-introspectable; treat as MISSING.
        return _emit_missing(
            f"could not introspect signature of {name!r} (un-introspectable "
            f"callable); skipping the signature check for it.")
    placeholders = [None] * int(max(0, args_count))
    try:
        sig.bind_partial(*placeholders, **kw)
    except TypeError as exc:
        return _emit(
            f"call to {name!r} is INCOMPATIBLE with its live signature "
            f"{str(sig)}: {exc}. The cell passes args={args_count} kwargs="
            f"{sorted(kw)} that do not bind. This is an API/signature drift (an "
            f"invented/renamed/removed kwarg or a missing required arg); it would "
            f"GATE_FAIL at the remote. Fix the call to match the live signature."
            + (f" {extra}" if extra else ""), mode=resolved)
    # Advisory: flag kwargs that hit OPTIONAL params (portability across drift).
    if warn_optional_kwargs and kw:
        params = sig.parameters
        optional_hits = [
            k for k in kw
            if k in params and params[k].default is not inspect.Parameter.empty]
        if optional_hits:
            print(f"{WARN_PREFIX} (advisory) call to {name!r} passes "
                  f"version-specific OPTIONAL kwarg(s) {sorted(optional_hits)} "
                  f"(they have defaults in the live signature). These may be "
                  f"ABSENT on an out-of-sync remote runner (the repo drifts ahead "
                  f"of the runner); prefer the portable/base call or verify remote "
                  f"parity before relying on them.", file=sys.stderr, flush=True)
    return True


# --------------------------------------------------------------------------- #
# Class 7: a control-comparison guard's baseline must not be at the arena floor #
# --------------------------------------------------------------------------- #

def assert_guard_baseline_valid(
        baseline_score: Optional[float],
        floor_score: Optional[float],
        *,
        guard_name: str = "control_beats_baseline_guard",
        baseline_name: str = "baseline",
        floor_name: str = "floor",
        eps: float = 0.02,
        run_mode: str = "selftest",
        mode: Optional[str] = None,
        extra: str = "") -> bool:
    """A control-beats-baseline break-guard must fire against a NON-floor baseline.

    baseline_score: the incumbent the guard compares controls against (e.g. POP
      MRR). Declaring None is MISSING -> warn always, return True.
    floor_score: the arena's structural floor (RANDOM MRR, or 1-over-N). eps: how
      close to the floor counts as "structurally at floor".

    If the baseline is itself within eps of the floor (baseline <= floor + eps),
    then a "control beats baseline -> BROKEN" guard mis-fires: any live control
    trivially clears a structurally-zero baseline, so the guard false-breaks a
    real run. Flag it: compare the control to RANDOM / arm-floor, not to a
    structurally-zero incumbent.

    Root failure it closes: exp_anchor_compose_magnitude_opt landed
    BROKEN_TEST_CONTROL_BEATS_POP on a held-out-entity arena where POP is
    structurally ~0 (held-out tails have train-freq 0), so RANDOM cleared POP by
    construction -> a FALSE break.
    """
    if not _is_selftest_mode(run_mode):
        return True
    resolved = _resolve_mode(mode)
    if baseline_score is None:
        return _emit_missing(
            f"no baseline score declared for guard {guard_name!r}. Pass the "
            f"baseline the guard compares controls against ({baseline_name}) plus "
            f"the arena floor ({floor_name}) so a guard that mis-fires on this "
            f"arena's structural zeros is caught pre-dispatch.")
    if floor_score is None:
        return _emit_missing(
            f"no floor score declared for guard {guard_name!r}. Pass the arena "
            f"floor (RANDOM / 1-over-N) so a structurally-at-floor baseline is "
            f"detectable.")
    b = float(baseline_score)
    f = float(floor_score)
    if not (math.isfinite(b) and math.isfinite(f)):
        return _emit(
            f"guard {guard_name!r} has a non-finite baseline/floor "
            f"({baseline_name}={b}, {floor_name}={f}); cannot prove the baseline "
            f"is above the floor. A guard that fires against a non-finite baseline "
            f"is unreliable.", mode=resolved)
    if b <= f + eps:
        return _emit(
            f"guard {guard_name!r} compares controls against {baseline_name} "
            f"(={b:.4g}) which is STRUCTURALLY AT the arena floor {floor_name} "
            f"(={f:.4g}, eps={eps:g}). On this arena any live control clears the "
            f"baseline by construction, so a 'control beats {baseline_name}' break "
            f"-guard MIS-FIRES and false-breaks a real run. Remedy: compare the "
            f"control to {floor_name} / arm-floor (or gate the guard on "
            f"{baseline_name} being above the floor first)."
            + (f" {extra}" if extra else ""), mode=resolved)
    return True


# --------------------------------------------------------------------------- #
# Orchestration entrypoint                                                     #
# --------------------------------------------------------------------------- #

_KIND_DISPATCH = {
    "positive_control": "positive_control",
    "metric_moves": "metric_moves",
    "full_gates_exercised": "full_gates_exercised",
    "negative_control_margin": "negative_control_margin",
    "real_code_path": "real_code_path",
    "substrate_signature": "substrate_signature",
    "guard_baseline_valid": "guard_baseline_valid",
}


def run_validity_preflight(
        checks: Sequence[dict],
        *,
        run_mode: str = "selftest",
        mode: Optional[str] = None) -> bool:
    """Run whichever declared validity checks a cell provides. Returns overall ok.

    Each check is a dict with a "kind" plus that check's kwargs (minus run_mode/
    mode, which are threaded from here). Unknown kinds are a hard error (typo
    protection) regardless of warn/enforce -- a mistyped kind must never silently
    skip a gate.

        run_validity_preflight([
            {"kind": "positive_control", "positive_control_passed_headline_gate": ok1,
             "control_name": "oracle", "headline_name": "median_hop"},
            {"kind": "metric_moves", "metric_name": "fpe", "before": 0.0, "after": v},
            {"kind": "full_gates_exercised",
             "full_fail_closed_gates": ["split_identity"], "exercised_gates": {...}},
            {"kind": "negative_control_margin", "control_scores": [...],
             "headline_threshold": 0.5, "margin": 0.05},
        ], run_mode="selftest")

    Under warn mode the aggregate can be False (some check warned) while the
    self-test still exits 0. Under enforce mode the first declared-and-failing
    check raises ValidityPreflightError.
    """
    ok = True
    for i, check in enumerate(checks):
        if not isinstance(check, dict) or "kind" not in check:
            raise ValidityPreflightError(
                f"{BLOCK_PREFIX} check[{i}] is not a dict with a 'kind' key: "
                f"{check!r}")
        kind = str(check["kind"])
        args = {k: v for k, v in check.items() if k != "kind"}
        if kind == "positive_control":
            ok &= assert_positive_control_passes(
                args.pop("positive_control_passed_headline_gate", None),
                run_mode=run_mode, mode=mode, **args)
        elif kind == "metric_moves":
            ok &= assert_metric_moves(run_mode=run_mode, mode=mode, **args)
        elif kind == "full_gates_exercised":
            ok &= assert_full_gates_exercised_at_selftest(
                args.pop("full_fail_closed_gates", None),
                args.pop("exercised_gates", None),
                run_mode=run_mode, mode=mode, **args)
        elif kind == "negative_control_margin":
            ok &= assert_negative_control_fails_with_margin(
                args.pop("control_scores", None),
                args.pop("headline_threshold"),
                run_mode=run_mode, mode=mode, **args)
        elif kind == "real_code_path":
            ok &= assert_real_code_path_exercised(
                args.pop("full_substrate_entrypoints", None),
                args.pop("exercised_entrypoints", None),
                run_mode=run_mode, mode=mode, **args)
        elif kind == "substrate_signature":
            ok &= assert_signature_compatible(
                args.pop("callable_obj", None),
                args.pop("kwargs", None),
                run_mode=run_mode, mode=mode, **args)
        elif kind == "guard_baseline_valid":
            ok &= assert_guard_baseline_valid(
                args.pop("baseline_score", None),
                args.pop("floor_score", None),
                run_mode=run_mode, mode=mode, **args)
        else:
            raise ValidityPreflightError(
                f"{BLOCK_PREFIX} unknown validity-preflight check kind "
                f"{kind!r} at check[{i}]. Known kinds: "
                f"{sorted(_KIND_DISPATCH)}. A mistyped kind must not silently "
                f"skip a gate.")
    return bool(ok)


__all__ = [
    "ValidityPreflightError",
    "assert_positive_control_passes",
    "assert_metric_moves",
    "assert_full_gates_exercised_at_selftest",
    "assert_negative_control_fails_with_margin",
    "run_validity_preflight",
]
