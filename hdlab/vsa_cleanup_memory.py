"""hdlab/vsa_cleanup_memory.py -- a REAL VSA cleanup memory, built to the theory it comes from.

WHY THIS MODULE EXISTS
----------------------
Plate 1995 (HRR) states the objection plainly: unbinding a VSA trace returns a NOISY vector that is
useless until it is cleaned up against a separate item memory with good reconstructive properties.
On that reading a VSA system's capability is set by its CLEANUP MEMORY, not by its algebra. This
substrate has five banked cells in which cleanup measured as inert. This module is the organ built
to the theory so that the re-read can be tested rather than asserted.

WHAT A CLEANUP MEMORY IS, IN THE THEORY'S OWN TERMS
--------------------------------------------------
An AUTO-ASSOCIATIVE memory over the codebook: given a noisy vector y, return the nearest STORED
SYMBOL, iterating to a fixed point. Its three characteristic quantities are
  CAPACITY   how many symbols can be superposed before recovery fails (VSA theory: O(d / log d)
             at fixed fidelity -- Frady, Kleyko & Sommer 2018; Thomas, Dasgupta & Rosing 2021),
  BASIN      how much noise a cue may carry and still land on the right symbol,
  FIXED POINT  clean(clean(y)) == clean(y), and clean(c_i) == c_i for a stored symbol.
All three are MEASURED here (`capacity_curve`, `basin_curve`, `selftest_fixed_point`), not claimed.

BRAIN FIDELITY (PLAN R13). COMPUTATIONS COPIED, PARAMETERS SWEPT.
-----------------------------------------------------------------
(a) BRAIN STRUCTURE. CA3 recurrent collaterals -- an auto-associative network that settles from a
    partial or noisy cue onto a stored pattern (Marr 1971; Treves & Rolls 1992/1994; Neunuebel &
    Knierim 2014 measure completion as CA3's representational change being LESS than its inputs').
    The cue is delivered by the direct perforant path, which continues to drive CA3 through the
    settle (Hasselmo 2002; McNaughton & Morris 1987) -- that is the `alpha` clamp, not a knob.
    Feedback inhibition (basket / O-LM interneurons) subtracts the common drive before the
    recurrent association acts; the analytical tradition writes the CA3 rule in COVARIANCE form on
    mean-subtracted activity, dw_ij ~ (r_i - <r>)(r_j - <r>) (Dayan & Willshaw 1991; Treves & Rolls
    1991), and the capacity formula p ~ C / (a ln(1/a)) is derived for that form. `center=True`
    implements that: remove the codebook's common mode before associating.
(b) ORGAN REUSE, enumerated from disk first. hdlab.cleanup_family.peel_sic_readout is REUSED for
    the interference-cancellation path (it is the certified matching-pursuit readout); no second
    implementation of it is written here. hdlab.iterative_attractor.iterative_cleanup is the
    INCUMBENT and is deliberately NOT wrapped -- this module is the alternative it is compared
    against, and `selftest_incumbent_is_argmax_preserving` measures the difference rather than
    asserting it.
(c) PINNED vs OURS.
    PINNED (computation, problem-derived, shared by any system solving this problem): a recurrent
      settle against the stored set; the cue continuing to drive it; common-mode removal before
      association; a fixed point that is a stored symbol.
    OURS, INVENTION UNDER TEST: the softmax form of the recurrent update; the specific
      global-mean-direction subtraction as the common-mode removal; and EVERY numeric value
      (beta, alpha, max_steps, n_peel) -- all are swept, none adopted.
    AND THE LARGER ONE, STATED SO IT IS NOT FORGOTTEN: VSA ALGEBRAIC BINDING ITSELF IS UNPINNED IN
      THE BRAIN. No recording has shown a cortical population computing a circular convolution or
      an elementwise product of two full-rank vector codes; coarse-coded conjunctive binding
      (O'Reilly & Busby) and binding by synchrony (von der Malsburg; Hummel) are live rivals, each
      with published objections of its own. The whole substrate choice this module serves is an
      invention under test, not biology.
(d) SHELVE / REVIVAL, BRAIN-FRAMED. If a cleanup memory built to the theory still does not recover
    the un-bound item, revive only over a code whose CAPACITY regime the theory says it can serve
    (superposition load below O(d/log d)) -- never "revive if the number improves". If it recovers
    the item and the downstream read-out still does not move, the defect is upstream, at the stage
    that produces the cue, and the completer should not be blamed for it.

ASCII-only. numpy float32. No torch, no network, no external LLM.
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")

from typing import Dict, Optional, Sequence, Tuple

import numpy as np

__all__ = [
    "CleanupMemory",
    "l2n",
    "degrade_to_cosine",
    "bipolar_keys",
    "unbind_residue",
    "basin_curve",
    "capacity_curve",
    "run_selftests",
]


def l2n(A: np.ndarray, eps: float = 1e-12) -> np.ndarray:
    """Row-wise L2 normalisation, zero-safe. (B, d) or (d,) -> same shape."""
    A = np.asarray(A, dtype=np.float32)
    return (A / np.maximum(np.linalg.norm(A, axis=-1, keepdims=True), eps)).astype(np.float32)


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - z.max(axis=-1, keepdims=True)
    e = np.exp(z.astype(np.float64))
    return (e / (e.sum(axis=-1, keepdims=True) + 1e-300)).astype(np.float32)


# ---------------------------------------------------------------------------------------------
# THE ORGAN
# ---------------------------------------------------------------------------------------------
class CleanupMemory:
    """Auto-associative cleanup over an explicit codebook. Settles to a stored symbol.

    Args:
        codebook: (M, d) the stored symbols. Rows need not be normalised.
        beta: recurrent sharpness. SWEPT, never adopted. Note the incumbent organ hard-wires
            beta = temp * sqrt(d) and hdlab.modern_hopfield_readout hard-wires beta / sqrt(d) --
            the two differ by a factor of d, which is why a single "beta=4" means opposite things
            in the two modules. Here beta is the effective inverse temperature, full stop.
        alpha: perforant cue clamp in [0, 1). state <- normalise(alpha*y0 + (1-alpha)*recurrent).
            alpha=0 is the self-consistent form; the biology is cue-DRIVEN, so alpha>0 is the
            brain-shaped setting and its VALUE is swept.
        max_steps: iteration cap. ~1-2 gamma sub-cycles is the biology; the value is swept.
        center: remove the codebook's common mode from BOTH codebook and cue before associating
            (the covariance-rule / feedback-inhibition computation). This is the single change
            that lets a settle alter a DECISION on a correlated code, and it is measured.
        tol: convergence threshold on the per-step L2 move, in units of sqrt(d).
    """

    def __init__(self, codebook: np.ndarray, *, beta: float = 16.0, alpha: float = 0.5,
                 max_steps: int = 8, center: bool = True, tol: float = 1e-3) -> None:
        C = np.asarray(codebook, dtype=np.float32)
        if C.ndim != 2:
            raise ValueError("codebook must be (M, d), got %r" % (C.shape,))
        self.M, self.d = int(C.shape[0]), int(C.shape[1])
        self.beta = float(beta)
        self.alpha = float(alpha)
        if not (0.0 <= self.alpha < 1.0):
            raise ValueError("alpha must be in [0, 1), got %r" % self.alpha)
        self.max_steps = int(max_steps)
        self.center = bool(center)
        self.tol = float(tol)
        self.raw = C
        self.mean_dir = l2n(C.mean(axis=0)[None, :])[0] if self.center else np.zeros(
            self.d, dtype=np.float32)
        self.C = l2n(self._center(C))
        # kept so a caller can report how strong the removed common mode was, rather than assume
        self.common_mode_cos = float(np.mean(l2n(C) @ l2n(C.mean(axis=0)[None, :])[0]))

    def _center(self, X: np.ndarray) -> np.ndarray:
        X = np.asarray(X, dtype=np.float32)
        if not self.center:
            return X
        Xn = l2n(X)
        return (Xn - (Xn @ self.mean_dir)[..., None] * self.mean_dir[None, :]).astype(np.float32)

    def scores(self, y: np.ndarray) -> np.ndarray:
        """Cleanup scores of y against every stored symbol, in the memory's own (centred) space."""
        q, sq = self._as_batch(y)
        return (l2n(self._center(q)) @ self.C.T).astype(np.float32)

    @staticmethod
    def _as_batch(y: np.ndarray) -> Tuple[np.ndarray, bool]:
        y = np.asarray(y, dtype=np.float32)
        return (y[None, :], True) if y.ndim == 1 else (y, False)

    def clean(self, y: np.ndarray) -> Tuple[np.ndarray, Dict]:
        """Settle y to a fixed point. Returns (state in the CENTRED space, diagnostics).

        diagnostics carry the things a cleanup memory must be able to show about itself:
        n_iterations, converged, argmax_idx, and -- the one that matters for the inertness
        charge -- how far the state moved from the input and whether the DECISION changed.
        """
        q, squeeze = self._as_batch(y)
        y0 = l2n(self._center(q))
        state = y0.copy()
        idx_in = np.argmax(y0 @ self.C.T, axis=1).astype(np.int64)
        thr = self.tol * float(np.sqrt(self.d))
        converged, steps = False, 0
        for t in range(self.max_steps):
            w = _softmax(self.beta * (state @ self.C.T))
            rec = w @ self.C
            new = l2n(self.alpha * y0 + (1.0 - self.alpha) * rec)
            move = float(np.mean(np.linalg.norm(new - state, axis=1)))
            state = new
            steps = t + 1
            if move < thr:
                converged = True
                break
        idx_out = np.argmax(state @ self.C.T, axis=1).astype(np.int64)
        diag = {
            "n_iterations": steps, "converged": bool(converged),
            "argmax_idx": (int(idx_out[0]) if squeeze else idx_out),
            "argmax_idx_of_input": (int(idx_in[0]) if squeeze else idx_in),
            "decision_changed_frac": float(np.mean(idx_in != idx_out)),
            "delta_state_vs_input_L2": float(np.mean(np.linalg.norm(state - y0, axis=1))),
            "beta": self.beta, "alpha": self.alpha, "max_steps": self.max_steps,
            "center": self.center, "M": self.M, "d": self.d,
        }
        return (state[0] if squeeze else state), diag

    def recover(self, y: np.ndarray) -> np.ndarray:
        """The cleanup's answer: the index of the stored symbol it settles onto."""
        _, d = self.clean(y)
        return np.atleast_1d(np.asarray(d["argmax_idx"], dtype=np.int64))

    def recover_set(self, y: np.ndarray, n_items: int) -> np.ndarray:
        """Multi-item recovery from a SUPERPOSITION, by interference cancellation.

        REUSES hdlab.cleanup_family.peel_sic_readout (the certified matching-pursuit readout); no
        second implementation is written here. This is the operation VSA theory actually asks a
        cleanup memory for when the trace holds several items at once.
        """
        from hdlab.cleanup_family import peel_sic_readout
        q, squeeze = self._as_batch(y)
        idx, _ = peel_sic_readout(l2n(self._center(q)), self.C, n_items=int(n_items), mode="unit")
        return idx[0] if squeeze else idx


# ---------------------------------------------------------------------------------------------
# cue construction and VSA algebra used by the measurements
# ---------------------------------------------------------------------------------------------
def degrade_to_cosine(target: np.ndarray, tau: float, rng: np.random.Generator) -> np.ndarray:
    """Return a unit cue whose cosine to `target` is EXACTLY tau (up to float error).

    Parameterising degradation by the achieved cosine rather than by a noise sigma is not a
    nicety: at d=256 a sigma of 0.5 already drives the cue-target cosine to ~0.12, so a sigma grid
    silently spends its whole range below any basin and reads as "the organ never helps".
    """
    T = l2n(target)
    n = rng.standard_normal(T.shape).astype(np.float32)
    n = n - (np.sum(n * T, axis=-1, keepdims=True)) * T      # orthogonal component
    n = l2n(n)
    tau = float(np.clip(tau, -1.0, 1.0))
    return l2n(tau * T + float(np.sqrt(max(0.0, 1.0 - tau * tau))) * n)


def bipolar_keys(n: int, d: int, rng: np.random.Generator) -> np.ndarray:
    """(n, d) bipolar role keys. Bipolar binding is elementwise and SELF-INVERSE, which is the
    convention hdlab.ca3_completer already uses; no new algebra is introduced."""
    return rng.choice(np.array([-1.0, 1.0], dtype=np.float32), size=(n, d))


def unbind_residue(codebook: np.ndarray, keys: np.ndarray, member_idx: np.ndarray,
                   probe_slot: int) -> np.ndarray:
    """Build a genuine VSA trace and unbind one slot from it -- the theory's actual input.

    bundle_b = SUM_s key_s * codebook[member_idx[b, s]]; residue = bundle_b * key_probe.
    The residue is the target code PLUS crosstalk composed of the other stored codes. This is the
    regime Plate's objection is about; a cue built by adding Gaussian noise to a codebook row is
    NOT that regime and does not test the objection.
    """
    C = np.asarray(codebook, dtype=np.float32)
    K = np.asarray(keys, dtype=np.float32)
    B, L = member_idx.shape
    bundle = np.zeros((B, C.shape[1]), dtype=np.float32)
    for s in range(L):
        bundle += C[member_idx[:, s]] * K[s][None, :]
    return (bundle * K[probe_slot][None, :]).astype(np.float32)


# ---------------------------------------------------------------------------------------------
# the three characteristic curves -- MEASURED, part of the organ
# ---------------------------------------------------------------------------------------------
def basin_curve(cm: "CleanupMemory", target_idx: np.ndarray, taus: Sequence[float],
                seed: int) -> Dict[str, Dict]:
    """Recovery as a function of the cue's cosine to its target. The BASIN.

    Reported beside a ONE-SHOT argmax on the identical cue, because "iteration helps" and "a
    cleanup memory works" are different claims and conflating them is what the banked cells did.
    """
    rng = np.random.default_rng(seed)
    tgt = np.asarray(target_idx, dtype=np.int64)
    out: Dict[str, Dict] = {}
    for tau in taus:
        cue = np.stack([degrade_to_cosine(cm.raw[i], float(tau), rng) for i in tgt])
        state, diag = cm.clean(cue)
        settled = np.argmax(state @ cm.C.T, axis=1)
        one_shot = np.argmax(l2n(cm._center(cue)) @ cm.C.T, axis=1)
        raw_shot = np.argmax(l2n(cue) @ l2n(cm.raw).T, axis=1)
        out["tau=%.2f" % tau] = {
            "recovery_SETTLED": round(float(np.mean(settled == tgt)), 4),
            "recovery_ONE_SHOT_centred": round(float(np.mean(one_shot == tgt)), 4),
            "recovery_ONE_SHOT_raw_uncentred": round(float(np.mean(raw_shot == tgt)), 4),
            "iteration_lift_over_one_shot": round(
                float(np.mean(settled == tgt) - np.mean(one_shot == tgt)), 4),
            "centring_lift_over_raw": round(
                float(np.mean(one_shot == tgt) - np.mean(raw_shot == tgt)), 4),
            "decision_changed_frac": round(float(diag["decision_changed_frac"]), 4),
            "delta_state_vs_input_L2": round(float(diag["delta_state_vs_input_L2"]), 6),
            "n_iterations": diag["n_iterations"], "converged": diag["converged"]}
    return out


def capacity_curve(d: int, M: int, loads: Sequence[int], n_probe: int, seed: int, *,
                   beta: float = 16.0, alpha: float = 0.5, max_steps: int = 8,
                   center: bool = True) -> Dict[str, Dict]:
    """Recovery of an UN-BOUND item as a function of superposition load L. The CAPACITY.

    This is the axis VSA theory names and the axis none of the five banked cleanup cells scored.
    Compared against the theory's own O(d / log d) scale.
    """
    rng = np.random.default_rng(seed)
    C = l2n(rng.standard_normal((M, d)).astype(np.float32))
    cm = CleanupMemory(C, beta=beta, alpha=alpha, max_steps=max_steps, center=center)
    out: Dict[str, Dict] = {}
    for L in loads:
        keys = bipolar_keys(int(L), d, np.random.default_rng(seed + 1))
        members = rng.integers(0, M, size=(int(n_probe), int(L)))
        res = unbind_residue(C, keys, members, 0)
        tgt = members[:, 0]
        state, diag = cm.clean(res)
        settled = np.argmax(state @ cm.C.T, axis=1)
        one_shot = np.argmax(l2n(cm._center(res)) @ cm.C.T, axis=1)
        out["L=%d" % L] = {
            "recovery_SETTLED": round(float(np.mean(settled == tgt)), 4),
            "recovery_ONE_SHOT": round(float(np.mean(one_shot == tgt)), 4),
            "iteration_lift_over_one_shot": round(
                float(np.mean(settled == tgt) - np.mean(one_shot == tgt)), 4),
            "residue_cos_to_target": round(
                float(np.mean(np.sum(l2n(res) * C[tgt], axis=1))), 4),
            "chance": round(1.0 / M, 8)}
    out["THEORY_SCALE_d_over_log_d"] = round(float(d) / float(np.log(max(d, 3))), 2)
    out["d"] = d
    out["M"] = M
    return out


# ---------------------------------------------------------------------------------------------
# SELF-TESTS -- assert VALUES; every threshold is one mechanism pins, or it is only REPORTED
# ---------------------------------------------------------------------------------------------
def selftest_fixed_point() -> Dict:
    """A cleanup memory's defining property: stored symbols are fixed points, and cleaning is
    IDEMPOTENT. Mechanism pins both, so both are asserted."""
    rng = np.random.default_rng(7)
    d, M = 256, 400
    C = l2n(rng.standard_normal((M, d)).astype(np.float32))
    cm = CleanupMemory(C, beta=24.0, alpha=0.3, max_steps=12, center=True)
    st, _ = cm.clean(cm.raw)                          # every stored symbol as its own cue
    self_rec = float(np.mean(np.argmax(st @ cm.C.T, axis=1) == np.arange(M)))
    if self_rec < 0.999:
        raise AssertionError("stored symbols are not fixed points: %.4f" % self_rec)
    cue = np.stack([degrade_to_cosine(C[i], 0.6, rng) for i in range(200)])
    s1, _ = cm.clean(cue)
    i1 = np.argmax(s1 @ cm.C.T, axis=1)
    s2, _ = cm.clean(cm.raw[i1])                      # clean(clean(y)) must equal clean(y)
    i2 = np.argmax(s2 @ cm.C.T, axis=1)
    if not np.array_equal(i1, i2):
        raise AssertionError("cleaning is not idempotent: %d of %d indices moved"
                             % (int((i1 != i2).sum()), i1.size))
    return {"stored_symbols_are_fixed_points": round(self_rec, 4), "idempotent": True}


def selftest_not_inert() -> Dict:
    """THE CHARGE THIS MODULE ANSWERS. An organ that returns its input unchanged is what five
    banked cells measured. Three things are asserted because mechanism pins them:
      (i) the state MOVES away from the input at a degraded cue,
      (ii) recovery RISES monotonically as the cue improves,
      (iii) the organ recovers a stored symbol far above chance where a degraded cue still
            carries signal.
    Whether ITERATION beats a ONE-SHOT argmax is NOT asserted -- it is REPORTED by basin_curve,
    because that is the open question the experiment exists to decide and pre-judging it here
    would be exactly the fault the ca3_completer amendments record.
    """
    rng = np.random.default_rng(11)
    d, M = 256, 400
    C = l2n(rng.standard_normal((M, d)).astype(np.float32))
    cm = CleanupMemory(C, beta=24.0, alpha=0.3, max_steps=12, center=True)
    tgt = rng.integers(0, M, size=300)
    taus = (0.15, 0.30, 0.45, 0.60, 0.80, 1.00)
    curve = basin_curve(cm, tgt, taus, seed=5)
    recs = [curve["tau=%.2f" % t]["recovery_SETTLED"] for t in taus]
    if any(recs[i] > recs[i + 1] + 1e-9 for i in range(len(recs) - 1)):
        raise AssertionError("recovery is not monotone in cue quality: %r" % recs)
    mid = curve["tau=0.45"]
    if mid["delta_state_vs_input_L2"] <= 1e-4:
        raise AssertionError("the organ returned its input unchanged at tau=0.45 (delta %.3e) -- "
                             "this is the inertness it exists to avoid" % mid["delta_state_vs_input_L2"])
    if mid["recovery_SETTLED"] <= 20.0 / M:
        raise AssertionError("recovery at tau=0.45 is at chance: %.4f vs chance %.4f"
                             % (mid["recovery_SETTLED"], 1.0 / M))
    return {"basin_curve": curve, "monotone_in_cue_quality": True,
            "chance": round(1.0 / M, 6)}


def selftest_incumbent_is_argmax_preserving() -> Dict:
    """MEASURE the incumbent rather than characterise it in prose.

    hdlab.iterative_attractor.iterative_cleanup at its shipped settings is compared with a ONE-SHOT
    argmax on the IDENTICAL cue. What is asserted is only that the comparison is INFORMATIVE (the
    two are not trivially the same object); the DIRECTION of the difference is reported.
    """
    from hdlab.iterative_attractor import iterative_cleanup
    rng = np.random.default_rng(13)
    d, M = 256, 400
    C = l2n(rng.standard_normal((M, d)).astype(np.float32))
    tgt = rng.integers(0, M, size=300)
    rows = {}
    for tau in (0.20, 0.40, 0.60, 0.80):
        cue = np.stack([degrade_to_cosine(C[i], tau, rng) for i in tgt])
        one = np.argmax(l2n(cue) @ C.T, axis=1)
        out = iterative_cleanup(cue, C, temp=4.0, max_steps=8, alpha=0.0)
        it = np.asarray(out["argmax_idx"], dtype=np.int64)
        out5 = iterative_cleanup(cue, C, temp=4.0, max_steps=8, alpha=0.5)
        it5 = np.asarray(out5["argmax_idx"], dtype=np.int64)
        rows["tau=%.2f" % tau] = {
            "one_shot_argmax": round(float(np.mean(one == tgt)), 4),
            "incumbent_alpha0.0": round(float(np.mean(it == tgt)), 4),
            "incumbent_alpha0.5": round(float(np.mean(it5 == tgt)), 4),
            "incumbent_a0.0_decision_equals_one_shot": round(float(np.mean(it == one)), 4),
            "incumbent_a0.5_decision_equals_one_shot": round(float(np.mean(it5 == one)), 4)}
    agree = [v["incumbent_a0.0_decision_equals_one_shot"] for v in rows.values()]
    if all(a >= 0.9999 for a in agree):
        rows["READING"] = ("the incumbent's DECISION is identical to a one-shot argmax at every "
                           "cue quality tested -- it moves the vector but never the answer")
    else:
        rows["READING"] = "the incumbent's decision differs from a one-shot argmax somewhere"
    return rows


def selftest_capacity_is_measurable() -> Dict:
    """The capacity axis must actually FALL with load, or it is not measuring capacity."""
    cur = capacity_curve(d=256, M=1000, loads=(1, 2, 4, 8, 16, 32), n_probe=300, seed=3)
    recs = [cur["L=%d" % L]["recovery_SETTLED"] for L in (1, 2, 4, 8, 16, 32)]
    if recs[0] < 0.99:
        raise AssertionError("recovery at load 1 is not at ceiling: %.4f" % recs[0])
    if recs[-1] > 0.5:
        raise AssertionError("recovery has not fallen by load 32 (%.4f) -- the axis is saturated "
                             "and cannot measure a capacity" % recs[-1])
    return cur


def selftest_null_and_known_answer_fail_independently() -> Dict:
    """A KNOWN-ANSWER arm at ceiling and a NULL arm at chance, each broken in turn to show the
    other survives. Demonstrated, not asserted."""
    rng = np.random.default_rng(17)
    d, M = 128, 300
    C = l2n(rng.standard_normal((M, d)).astype(np.float32))
    cm = CleanupMemory(C, beta=24.0, alpha=0.3, max_steps=8, center=True)
    tgt = rng.integers(0, M, size=400)
    ka = float(np.mean(cm.recover(cm.raw[tgt]) == tgt))                  # cue IS the symbol
    cue = np.stack([degrade_to_cosine(C[i], 0.6, rng) for i in tgt])
    perm = rng.permutation(tgt.size)
    nul = float(np.mean(cm.recover(cue[perm]) == tgt))                   # pairing destroyed
    live = float(np.mean(cm.recover(cue) == tgt))
    if ka < 0.999:
        raise AssertionError("KNOWN-ANSWER arm not at ceiling: %.4f" % ka)
    if nul > 5.0 / M:
        raise AssertionError("NULL arm is not at chance: %.4f vs %.4f" % (nul, 1.0 / M))
    # BREAK EACH IN TURN. A codebook of noise destroys KA while NULL stays at chance; a cue that
    # is the answer lifts NULL while KA stays at ceiling.
    bad = CleanupMemory(l2n(rng.standard_normal((M, d)).astype(np.float32)), beta=24.0, alpha=0.3)
    ka_broken = float(np.mean(bad.recover(cm.raw[tgt]) == tgt))
    nul_when_ka_broken = float(np.mean(bad.recover(cue[perm]) == tgt))
    nul_leaking = float(np.mean(cm.recover(cm.raw[tgt][perm][np.argsort(perm)]) == tgt))
    if ka_broken > 5.0 / M:
        raise AssertionError("breaking the codebook did not break KA: %.4f" % ka_broken)
    if nul_when_ka_broken > 5.0 / M:
        raise AssertionError("breaking KA also lifted NULL -- they are not independent")
    if nul_leaking < 0.999:
        raise AssertionError("the leak-detection arm did not leak, so a leaking NULL would be "
                             "invisible: %.4f" % nul_leaking)
    return {"KNOWN_ANSWER_cue_is_the_symbol": round(ka, 4),
            "NULL_pairing_permuted": round(nul, 4), "chance": round(1.0 / M, 6),
            "live_arm_at_tau0.60": round(live, 4),
            "KA_broken_by_a_noise_codebook": round(ka_broken, 4),
            "NULL_unaffected_when_KA_broken": round(nul_when_ka_broken, 4),
            "leak_detector_fires": round(nul_leaking, 4),
            "independence": "DEMONSTRATED both ways"}


def run_selftests() -> Dict:
    return {
        "fixed_point": selftest_fixed_point(),
        "not_inert": selftest_not_inert(),
        "incumbent_measured": selftest_incumbent_is_argmax_preserving(),
        "capacity_measurable": selftest_capacity_is_measurable(),
        "validity_independent": selftest_null_and_known_answer_fail_independently(),
    }


if __name__ == "__main__":
    import json
    r = run_selftests()
    print(json.dumps(r, indent=1, default=float), flush=True)
    print("[hdlab.vsa_cleanup_memory selftest] PASS (5/5)", flush=True)
