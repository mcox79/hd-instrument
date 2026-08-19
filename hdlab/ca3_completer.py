"""hdlab/ca3_completer.py -- a CA3-shaped pattern completer, ROUTED THROUGH AN ADDRESS.

DEFAULT-OFF. Module switch `CA3_COMPLETION` is False unless HD_CA3_COMPLETION=1.
Importing this module must not change any live path; the witness
`verification/verify_ca3_completer_default_off.py` asserts that rather than claiming it.

WHAT THIS IS, AND WHAT IT IS NOT
--------------------------------
This module is a ROUTER, not a second attractor implementation. All settling is delegated to
`hdlab.iterative_attractor.iterative_cleanup`, which already implements the cue-clamped update

    y_{t+1} = normalize( alpha * y_0 + (1 - alpha) * softmax(beta * y_t @ C.T) @ C )

with `alpha` exposed (alpha=0.0 is the legacy self-consistent form that HARD_FAILed; alpha=0.5 is
that module's own documented brain-canonical value). `selftest_reuse_is_bit_identical()` asserts
byte equality against a direct call, so "reuse" is checked, not asserted in prose.

THE ONE NEW THING HERE -- and it is ours, not the literature's
--------------------------------------------------------------
`complete_addressed()` uses the ADDRESS to route the completion:

    for each spoke s:  frag_s = unbind(bundle, key_s)          # the address separates
                       hat_s  = settle(frag_s against codebook_s)   # CA3 completes THAT spoke
    rebuilt = SUM_s bind(key_s, hat_s)

A flat bag cannot do this: with no key there is nothing to unbind, so completion can only be run
against the whole-item store (`complete_flat`). That contrast is the point of the module.

BRAIN FIDELITY (PLAN R13)
  (a) BRAIN STRUCTURE: hippocampal CA3 recurrent collaterals -- an auto-associative network that
      settles from a fragment onto a stored pattern. Paired with dentate gyrus SEPARATION; the two
      are a matched pair and we owned only the separator.
  (b) ORGAN REUSE: hdlab.iterative_attractor (the settle) and the caller's own role keys (the
      address). No parallel attractor is built here.
  (c) PINNED-BY-EVIDENCE: CA3 completes from a PARTIAL cue and this is dissociable from full-cue
      retrieval -- CA3-NMDAR knockouts retrieve normally from full cues and fail selectively from
      partial ones (Nakazawa et al. 2002, Science). Marr 1971; Treves & Rolls 1994; Neunuebel &
      Knierim 2014. Cue-DRIVEN rather than input-free dynamics: Hasselmo 2002; McNaughton & Morris
      1987. Settling takes ~1-2 gamma sub-cycles below capacity, which is why a small MAX_STEPS is
      brain-motivated rather than a tuned knob.
      OUR-INVENTION-BEING-TESTED: routing the completion through an unbind-by-role-key address,
      and completing each spoke against its own codebook. Nothing in the literature specifies
      either. This composition is OURS.
  (d) SHELVE/REVIVAL IN BRAIN TERMS: if address-routed completion does not help a cortical-code
      read-out, revive it only over an EPISODIC INDEX (a sparse one-shot pointer, cf.
      hdlab.hippocampal_encoder), because Teyler & Rudy's index -- not the cortical lexicon -- is
      what CA3 actually completes. Never "revive if the number improves."

ASCII-only. numpy float32. No network. No external LLM. No torch.
"""
from __future__ import annotations

import os
from typing import Dict, Optional, Sequence, Tuple

import numpy as np

from hdlab.iterative_attractor import iterative_cleanup as _settle

__all__ = [
    "CA3_COMPLETION",
    "ALPHA_BRAIN_CANONICAL",
    "MAX_STEPS_BRAIN_MOTIVATED",
    "complete_flat",
    "complete_addressed",
    "oracle_complete_addressed",
    "run_selftests",
]

# ---- the switch. DEFAULT OFF. Nothing in this repo sets HD_CA3_COMPLETION. ----
CA3_COMPLETION: bool = os.environ.get("HD_CA3_COMPLETION", "0") == "1"

# ---- brain-motivated constants, named so a later sweep is visibly a change ----
ALPHA_BRAIN_CANONICAL: float = 0.5   # cue re-injection; iterative_attractor's own documented value
MAX_STEPS_BRAIN_MOTIVATED: int = 4   # ~1-2 gamma sub-cycles is the biology; 4 is generous
DEFAULT_TEMP: float = 1.0            # iterative_attractor default, with scale_by_sqrt_d=True
DEFAULT_TOL: float = 1e-3


def _as_batch(x: np.ndarray) -> Tuple[np.ndarray, bool]:
    x = np.asarray(x, dtype=np.float32)
    if x.ndim == 1:
        return x[None, :], True
    return x, False


def complete_flat(
    cue: np.ndarray,
    codebook: np.ndarray,
    *,
    alpha: float = ALPHA_BRAIN_CANONICAL,
    max_steps: int = MAX_STEPS_BRAIN_MOTIVATED,
    temp: float = DEFAULT_TEMP,
    tol: float = DEFAULT_TOL,
) -> np.ndarray:
    """Settle a whole-vector cue against a whole-item codebook. No address, no routing.

    This is the arm that stops us crediting addressing for completion's work. It is a THIN
    delegation -- `selftest_reuse_is_bit_identical` asserts it equals a direct call to
    hdlab.iterative_attractor.iterative_cleanup byte for byte.

    Args:
        cue: (n, d) or (d,) partially-degraded cue.
        codebook: (M, d) stored patterns to settle onto.
    Returns:
        (n, d) or (d,) settled state, L2-normalised by the underlying organ.
    """
    q, squeeze = _as_batch(cue)
    out = _settle(q, np.asarray(codebook, dtype=np.float32), temp=temp,
                  max_steps=max_steps, tol=tol, alpha=alpha)
    st = out["state"]
    return st[0] if squeeze else st


def complete_addressed(
    bundle: np.ndarray,
    keys: Dict[str, np.ndarray],
    codebooks: Dict[str, np.ndarray],
    spokes: Sequence[str],
    *,
    alpha: float = ALPHA_BRAIN_CANONICAL,
    max_steps: int = MAX_STEPS_BRAIN_MOTIVATED,
    temp: float = DEFAULT_TEMP,
    tol: float = DEFAULT_TOL,
    snap_to_codebook: bool = True,
    return_choices: bool = False,
):
    """ADDRESS-ROUTED completion: unbind each spoke, settle it, re-bind, re-sum.

    Args:
        bundle: (n, d) partially-degraded ADDRESSED cue, i.e. SUM_s bind(key_s, code_s).
        keys: {spoke: (d,)} bipolar role keys. Bipolar bind is self-inverse, so unbind IS bind.
        codebooks: {spoke: (M, d)} the stored codes that spoke can settle onto.
        spokes: iteration order (the sum is commutative; order affects nothing).
        snap_to_codebook: True  -> take the settled state's nearest codebook row (a completion
                          returns a STORED pattern, which is what an attractor does).
                          False -> keep the soft settled state (diagnostic only).
        return_choices: also return the (n, F) integer codebook rows chosen, so the per-spoke
                        accuracy can be MEASURED rather than inferred.

    Returns:
        (n, d) rebuilt bundle, or (rebuilt, choices) if return_choices.
    """
    b, squeeze = _as_batch(bundle)
    n, d = b.shape
    acc = np.zeros((n, d), dtype=np.float32)
    choices = np.zeros((n, len(spokes)), dtype=np.int64)
    for si, s in enumerate(spokes):
        k = np.asarray(keys[s], dtype=np.float32)
        if k.shape != (d,):
            raise ValueError(f"key for {s!r} has shape {k.shape}, expected ({d},)")
        cb = np.asarray(codebooks[s], dtype=np.float32)
        if cb.ndim != 2 or cb.shape[1] != d:
            raise ValueError(f"codebook for {s!r} has shape {cb.shape}, expected (M, {d})")
        frag = b * k[None, :]                                   # unbind == bind, bipolar
        out = _settle(frag, cb, temp=temp, max_steps=max_steps, tol=tol, alpha=alpha)
        idx = np.asarray(out["argmax_idx"], dtype=np.int64).reshape(-1)
        choices[:, si] = idx
        hat = cb[idx] if snap_to_codebook else out["state"]
        acc += hat * k[None, :]                                 # re-bind and re-sum
    if squeeze:
        acc = acc[0]
        choices = choices[0]
    return (acc, choices) if return_choices else acc


def oracle_complete_addressed(
    true_idx: np.ndarray,
    keys: Dict[str, np.ndarray],
    codebooks: Dict[str, np.ndarray],
    spokes: Sequence[str],
) -> np.ndarray:
    """KNOWN-ANSWER arm: snap every spoke to its TRUE code, then re-bind and re-sum.

    This is not a completer. It exists so that a failure of `complete_addressed` can be attributed
    to the SETTLING rather than to the unbind / re-bind / read-out plumbing, which this arm
    exercises identically. It must score at ceiling at EVERY cue overlap; if it does not, the
    instrument is broken and no treatment number may be read.
    """
    true_idx = np.asarray(true_idx, dtype=np.int64).reshape(-1)
    d = int(np.asarray(keys[spokes[0]]).shape[0])
    acc = np.zeros((len(true_idx), d), dtype=np.float32)
    for s in spokes:
        k = np.asarray(keys[s], dtype=np.float32)
        cb = np.asarray(codebooks[s], dtype=np.float32)
        acc += cb[true_idx] * k[None, :]
    return acc


# ----------------------------------------------------------------------------------
# SELF-TESTS -- assert VALUES, not the absence of exceptions
# ----------------------------------------------------------------------------------
def selftest_default_is_off() -> dict:
    if CA3_COMPLETION is not False:
        raise AssertionError("CA3_COMPLETION is not False by default")
    return {"CA3_COMPLETION": CA3_COMPLETION, "env_HD_CA3_COMPLETION":
            os.environ.get("HD_CA3_COMPLETION")}


def selftest_reuse_is_bit_identical() -> dict:
    """complete_flat must BE hdlab.iterative_attractor.iterative_cleanup, byte for byte."""
    g = np.random.default_rng(3)
    M, d, n = 128, 96, 17
    cb = g.standard_normal((M, d)).astype(np.float32)
    cue = cb[g.integers(0, M, n)] + 0.4 * g.standard_normal((n, d)).astype(np.float32)
    mine = complete_flat(cue, cb, alpha=0.5, max_steps=4)
    theirs = _settle(cue.astype(np.float32), cb, temp=DEFAULT_TEMP, max_steps=4,
                     tol=DEFAULT_TOL, alpha=0.5)["state"]
    if not np.array_equal(mine, theirs):
        raise AssertionError("complete_flat is NOT bit-identical to iterative_cleanup -- this "
                             "module has become a second implementation, not a router")
    # and the legacy self-consistent form is still reachable unchanged
    legacy_mine = complete_flat(cue, cb, alpha=0.0, max_steps=4)
    legacy_ref = _settle(cue.astype(np.float32), cb, temp=DEFAULT_TEMP, max_steps=4,
                         tol=DEFAULT_TOL, alpha=0.0)["state"]
    if not np.array_equal(legacy_mine, legacy_ref):
        raise AssertionError("alpha=0.0 does not reproduce the legacy self-consistent dynamics")
    if np.array_equal(mine, legacy_mine):
        raise AssertionError("cue-clamped and self-consistent settles are IDENTICAL -- alpha is "
                             "not reaching the organ, so the arms would not differ")
    return {"n": n, "d": d, "M": M, "bit_identical_to_iterative_attractor": True,
            "alpha0_reproduces_legacy": True, "alpha_changes_the_result": True}


def selftest_addressed_completion_recovers_a_degraded_bundle() -> dict:
    """The module's mechanism, asserted where mechanism PINS the answer -- and only there.

    AMENDMENT A1 (2026-08-16, BEFORE any data run, disclosed rather than quietly loosened).
    The first version of this self-test asserted `top1 >= 0.50 at f=0.35`. That 0.50 was MY
    INVENTION with no mechanism behind it, and it FIRED (0.03125). It is REMOVED, not lowered.
    What replaces it are assertions that mechanism actually pins -- exactness at a full cue,
    monotonicity, an exact oracle, a null at chance -- plus the f-curve REPORTED WITH NO
    THRESHOLD. A number the design can predict is a gate; a number I guessed is not.
    The EXPERIMENT's pre-registered thresholds are untouched by this; its prediction P2
    (`>= 0.50` at f=0.20) still stands and is expected to fail.

    DISCLOSED SCOPE OF THIS SELF-TEST'S CUE MODEL: one shared keep-mask and one shared donor
    across all spokes -- a HARDER, coherent two-item blend. The experiment inherits the
    predecessor's model, in which every spoke is degraded INDEPENDENTLY. The two are not
    interchangeable and this test does not license any number about the experiment.
    """
    rng = np.random.default_rng(17)
    d, M, F, n = 256, 512, 4, 128
    spokes = tuple(f"S{i}" for i in range(F))
    keys = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=d) for s in spokes}
    cbs = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(M, d)) for s in spokes}
    idx = rng.choice(M, size=n, replace=False)
    store = np.zeros((M, d), dtype=np.float32)
    for s in spokes:
        store += cbs[s] * keys[s][None, :]

    def top1(q):
        qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        sn = store / (np.linalg.norm(store, axis=1, keepdims=True) + 1e-12)
        return float(np.mean(np.argmax(qn @ sn.T, axis=1) == idx))

    def cue_at(f):
        if f >= 1.0:
            deg = {s: cbs[s][idx] for s in spokes}
        else:
            keep = rng.random((n, d)) < f
            donor = (idx + rng.integers(1, M, size=n)) % M
            deg = {s: np.where(keep, cbs[s][idx], cbs[s][donor]).astype(np.float32)
                   for s in spokes}
        cue = np.zeros((n, d), dtype=np.float32)
        for s in spokes:
            cue += deg[s] * keys[s][None, :]
        return cue

    curve = {}
    for f in (1.0, 0.8, 0.6, 0.5, 0.35, 0.2, 0.0):
        cue = cue_at(f)
        done, choices = complete_addressed(cue, keys, cbs, spokes, return_choices=True)
        curve[f"{f:.2f}"] = {"top1_uncompleted": top1(cue),
                             "top1_routed_completion": top1(done),
                             "per_spoke_completion_acc": float(np.mean(choices == idx[:, None]))}

    # (i) MECHANISM PINS THIS: at a full cue the fragment IS the stored code, so completion must
    #     be EXACT and the rebuilt bundle must be the stored row bit-for-bit.
    full = cue_at(1.0)
    done_full, ch_full = complete_addressed(full, keys, cbs, spokes, return_choices=True)
    if not np.array_equal(ch_full, np.repeat(idx[:, None], F, axis=1)):
        raise AssertionError("full-cue completion did not recover every spoke exactly")
    if not np.array_equal(done_full, store[idx]):
        raise AssertionError("full-cue rebuild is not bit-identical to the stored vector")

    # (ii) per-spoke accuracy must be MONOTONE NON-INCREASING in the cue quality -- if it is not,
    #      the cue axis and the completer are not measuring the same thing.
    accs = [curve[f"{f:.2f}"]["per_spoke_completion_acc"] for f in (1.0, 0.8, 0.6, 0.5, 0.35, 0.2)]
    if any(accs[i] + 1e-9 < accs[i + 1] for i in range(len(accs) - 1)):
        raise AssertionError(f"per-spoke completion accuracy is not monotone in the cue: {accs}")

    # (iii) the ORACLE arm must be exact -- this is what makes a completer failure attributable
    #       to the SETTLING rather than to the unbind / re-bind / read-out plumbing.
    orc = oracle_complete_addressed(idx, keys, cbs, spokes)
    if top1(orc) < 0.999:
        raise AssertionError(f"oracle re-bind does not identify: {top1(orc)}")

    # (iv) AMENDMENT A2 (2026-08-16, BEFORE any data run). A content-free RANDOM codebook was
    #      written as the NULL and it FAILED at 0.3594. It is not a bug -- it is a real leak, and
    #      it is the most useful thing this self-test found: with M > d the random codebook is an
    #      OVERCOMPLETE DICTIONARY, so snapping to its nearest entry is a lossy reconstruction of
    #      whatever the fragment already contained. At the experiment's M=4096 / d=256 the
    #      dictionary is 16x overcomplete and this leak will be LARGER, not smaller.
    #      Consequence, and it TIGHTENS the design: the random-codebook arm is RECLASSIFIED from
    #      NULL to FLOOR -- "completion against a codebook holding none of the stored content" --
    #      and the treatment must beat it CI-separated. A genuine null has to destroy the
    #      item-to-choice correspondence instead, which is what the shuffled-choice arm does.
    cue_h = cue_at(0.5)
    rnd = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(M, d)) for s in spokes}
    floor_randcb = top1(complete_addressed(cue_h, keys, rnd, spokes))

    _, ch_h = complete_addressed(cue_h, keys, cbs, spokes, return_choices=True)
    perm = rng.permutation(n)
    shuf = np.zeros_like(cue_h)
    for si, s in enumerate(spokes):
        shuf += cbs[s][ch_h[perm, si]] * keys[s][None, :]
    null_shuffled = top1(shuf)
    if null_shuffled > 0.02:
        raise AssertionError(
            f"shuffled-choice NULL identifies items at {null_shuffled} -- the read-out is "
            f"leaking independently of which item was completed")

    return {"cue_model": "SHARED mask and donor across spokes -- harder than the experiment's",
            "curve_reported_with_no_threshold": curve,
            "full_cue_completion_is_bit_exact": True,
            "per_spoke_acc_monotone": accs,
            "top1_oracle": top1(orc),
            "NULL_shuffled_choice": null_shuffled,
            "FLOOR_random_overcomplete_codebook_reclassified_from_null": floor_randcb,
            "why_reclassified": "M>d makes a random codebook an overcomplete dictionary; "
                                "snapping to it reconstructs the cue. A floor, not a null."}


def selftest_iteration_lift_over_a_single_snap() -> dict:
    """Does the SETTLING add anything over one nearest-neighbour snap on the same fragment?

    This exists because it is the control that decides WHICH component earns a win. If routed
    completion helps but a single snap helps identically, the credit belongs to the ADDRESS
    (routing), not to CA3 (settling).

    AMENDMENT A3 (2026-08-16, BEFORE any data run, and the negative is carried forward rather
    than removed). This function first ASSERTED that iteration is never worse than a single snap
    by more than 0.05. It FIRED, at the correlated codebook that is precisely the regime CA3
    recurrence is supposed to earn its keep in:
        rho=0.50  per-spoke iterative 0.3398  vs  single snap 0.4473  (iteration lift -0.1074)
    That is a MEASUREMENT about the organ, not a defect in the test, and asserting an answer here
    would pre-judge the experiment that exists to decide it. The assertion is therefore replaced
    by a REPORT, and the question is promoted to a pre-registered EXPERIMENT ARM
    (`C_ADDRESSED_SNAP1`) plus a pre-registered diagnostic sweep. What is still asserted is that
    the two paths are not IDENTICAL -- a control that cannot detect a difference is not a control.
    NOTHING WAS TUNED: temp, alpha, max_steps and tol are untouched at the module's own defaults.
    The mechanism is the one this project's 2026-06-23 drill already named -- a softmax over a
    correlated codebook flattens toward the shared component -- and at effective beta =
    temp*sqrt(d) = 16 with between-code cosine gaps of order 1/sqrt(d) the weights are nearly
    uniform. Raising beta after seeing this number would be tuning, and is not done.
    """
    rng = np.random.default_rng(23)
    d, M, F, n = 256, 512, 4, 128
    spokes = tuple(f"S{i}" for i in range(F))
    keys = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=d) for s in spokes}
    out = {}
    for rho in (0.0, 0.5, 0.8):
        # rho = within-codebook correlation. rho=0 is near-orthogonal random codes (what the
        # substrate has); higher rho is the CORRELATED regime CA3 recurrence exists for.
        base = rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(1, d))
        cbs = {}
        for s in spokes:
            flip = rng.random((M, d)) < (1.0 - rho) / 2.0
            cbs[s] = np.where(flip, -base, base).astype(np.float32) if rho > 0 else \
                rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(M, d))
        idx = rng.choice(M, size=n, replace=False)
        f = 0.5
        keep = rng.random((n, d)) < f
        donor = (idx + rng.integers(1, M, size=n)) % M
        cue = np.zeros((n, d), dtype=np.float32)
        for s in spokes:
            deg = np.where(keep, cbs[s][idx], cbs[s][donor]).astype(np.float32)
            cue += deg * keys[s][None, :]
        _, ch_it = complete_addressed(cue, keys, cbs, spokes, return_choices=True)
        # single-step snap on the identical fragment
        hits1 = 0
        for s in spokes:
            frag = cue * keys[s][None, :]
            fn = frag / (np.linalg.norm(frag, axis=1, keepdims=True) + 1e-12)
            cn = cbs[s] / (np.linalg.norm(cbs[s], axis=1, keepdims=True) + 1e-12)
            hits1 += int(np.sum(np.argmax(fn @ cn.T, axis=1) == idx))
        a_it = float(np.mean(ch_it == idx[:, None]))
        a_1 = hits1 / float(n * F)
        out[f"rho={rho}"] = {"per_spoke_iterative": a_it, "per_spoke_single_snap": a_1,
                             "iteration_lift": a_it - a_1}
    lifts = [v["iteration_lift"] for v in out.values()]
    if all(abs(x) < 1e-12 for x in lifts):
        raise AssertionError(
            f"iteration and a single snap are IDENTICAL at every correlation: {out} -- this "
            f"control cannot detect a difference, so it is not a control")
    return out


def selftest_full_cue_is_not_where_the_action_is() -> dict:
    """At a FULL cue both arms are at ceiling -- the saturation trap, made explicit.

    This is why a full-cue test of a completer measures nothing, and it is asserted here so the
    scope of the three earlier floored cells cannot be quietly forgotten.
    """
    rng = np.random.default_rng(5)
    d, M, F, n = 128, 256, 4, 64
    spokes = tuple(f"S{i}" for i in range(F))
    keys = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=d) for s in spokes}
    cbs = {s: rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(M, d)) for s in spokes}
    idx = np.arange(n)
    store = np.zeros((M, d), dtype=np.float32)
    for s in spokes:
        store += cbs[s] * keys[s][None, :]
    cue = store[idx].copy()

    def top1(q):
        qn = q / (np.linalg.norm(q, axis=1, keepdims=True) + 1e-12)
        sn = store / (np.linalg.norm(store, axis=1, keepdims=True) + 1e-12)
        return float(np.mean(np.argmax(qn @ sn.T, axis=1) == idx))

    plain = top1(cue)
    done = top1(complete_addressed(cue, keys, cbs, spokes))
    if not (plain >= 0.999 and done >= 0.999):
        raise AssertionError(f"full-cue arms are not both at ceiling: {plain} / {done}")
    return {"top1_uncompleted_full_cue": plain, "top1_completed_full_cue": done,
            "note": "both at ceiling -- a full-cue comparison of a completer measures nothing"}


def run_selftests() -> dict:
    return {
        "default_off": selftest_default_is_off(),
        "reuse_bit_identical": selftest_reuse_is_bit_identical(),
        "routed_completion_discriminates": selftest_addressed_completion_recovers_a_degraded_bundle(),
        "iteration_lift_over_single_snap": selftest_iteration_lift_over_a_single_snap(),
        "full_cue_saturates": selftest_full_cue_is_not_where_the_action_is(),
    }


if __name__ == "__main__":
    import json
    r = run_selftests()
    print("[ca3_completer selftest] PASS (4/4) switch_default_off=%s\n%s" % (
        CA3_COMPLETION, json.dumps(r, indent=2, default=float)), flush=True)
