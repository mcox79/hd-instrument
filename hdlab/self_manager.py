"""Self-manager: bank of content-free scalar meta-controllers over an already-working core.

This is the operational home for the substrate self-manager -- a small set of independent
SCALAR-in/SCALAR-out feedback loops that sit ABOVE the certified value-gate + attention-gate,
tuning their GAIN / THRESHOLD / HORIZON knobs rather than replacing any mechanism. Brain frame:
6 separable neuromodulatory channels (NE gain, ACh encode/retrieve, 5HT horizon, tonic-DA vigor,
ACC/EVC halting, homeostasis+sleep); see notes/research_neuromodulatory_self_manager_controller_2026-07-08.md.

DIAL #1 (the only dial promoted here): ACC/EVC ADAPTIVE HALTING -- "know when to stop / how much
compute to spend." A fixed hop/retry budget over-computes easy items (drifting PAST an already-reached
goal, since the actor has no STAY action) and under-computes hard items, under an UNKNOWN per-instance
difficulty distribution. The dial is a per-item LOCAL reflex (halt once an arrival/progress confidence
scalar crosses a threshold theta) whose single aggregate knob theta is tuned ONCE on a calibration set
by argmax accuracy-per-compute (the EVC value-per-effort objective), then FROZEN. No stored per-item map
(not brain-like), no new learned weights: content-free scalar in, halt decision out.

Provenance (FULL-proven, promoted exp-only -> operational):
  cell   experiments/exp_substrate_acc_evc_adaptive_halting_v1.py
  prereg preregs/2026-07-08_substrate_acc_evc_adaptive_halting_v1.md
  FULL   data/exp_substrate_acc_evc_adaptive_halting_v1/metrics.json -> HARD_PASS (5 seeds, run_mode=full)
         accpc[FIXED=0.0446 ADAPT=0.1878] adapt_vs_fixed=+3.21 adapt_vs_random=+3.87 scramble_gap=0.812
         acc[FIXED=0.178 ADAPT=0.769] hops[FIXED=4.00 ADAPT=4.10] corr[A=1.000 S=-0.026] closure=1.000
         MEASURED@data/exp_substrate_acc_evc_adaptive_halting_v1/metrics.json
  tier   MEASURED_MECHANISM expected for a first de-risked dial (prereg honesty flag); Skunkworks owns
         landed-VET / cert-atom filing. The load-bearing claim: the FROZEN depth knob DISCARDS an
         available arrival signal (over/under-running); making it adaptive RECOVERS it. RANDOM_DEPTH +
         SCRAMBLED_HALT controls prove the gain is signal-driven, not depth-variance or a pinned metric.

Envelope / honest scope:
  Certified on CLEAN codebook states, where arrival confidence cos(state,goal) is near-perfectly
  detectable so the adaptive detector approaches the ground-truth arrival oracle (closure=1.0). The
  harder regime -- imperfect cleanup / graded (noisy) arrival confidence where the detector is
  non-trivial -- is the natural follow-up and is NOT covered by this promotion. Callers on noisy /
  low-SNR arrival telemetry should re-validate before relying on the matched-compute gain.

PUBLIC API (content-free; caller supplies whatever per-step confidence its own process emits):
  accuracy_per_compute(correct, hops)            -> float  (EVC value-per-effort statistic == accpc)
  tune_halt_threshold(theta_grid, evaluate)      -> dict   (theta_star = argmax accpc on a calib set)
  run_halting(confidence_traj, theta, ...)       -> hops_used  (first-crossing local reflex, batched)
  AdaptiveHaltController(theta)                    (frozen scalar; .should_halt(...) / .run(...))
    AdaptiveHaltController.tuned(theta_grid, evaluate)  (tune + freeze in one call)
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Sequence, Tuple

import numpy as np


def accuracy_per_compute(correct: Any, hops: Any) -> float:
    """EVC value-per-effort: mean(correct) / mean(hops_used). 0.0 if no compute was spent."""
    c = np.asarray(correct, dtype=np.float64)
    h = np.asarray(hops, dtype=np.float64)
    if c.size == 0 or h.size == 0:
        raise ValueError("accuracy_per_compute requires non-empty correct/hops arrays")
    mh = float(np.mean(h))
    return float(np.mean(c)) / mh if mh > 1e-9 else 0.0


def tune_halt_threshold(
    theta_grid: Sequence[float],
    evaluate: Callable[[float], Tuple[Any, Any]],
) -> Dict[str, Any]:
    """Pick theta* = argmax accuracy-per-compute over theta_grid on a calibration set, then FREEZE.

    Args:
        theta_grid: candidate acceptance thresholds (scan in caller's preferred order).
        evaluate: evaluate(theta) -> (correct_array, hops_array) on the CALIBRATION split -- the
            per-item outcome and compute spent when halting at that theta. Content-free: the caller
            owns how confidence is produced and how correctness is judged.

    Returns:
        dict: {theta_star, accpc_star, curve:[{theta, acc, mean_hops, accpc}, ...]}.
        Strict argmax (first maximizer wins on ties), matching the certified cell's tuner.
    """
    grid = list(theta_grid)
    if not grid:
        raise ValueError("theta_grid must be non-empty")
    curve: List[Dict[str, float]] = []
    best_theta, best_accpc = float(grid[0]), -1.0
    for th in grid:
        correct, hops = evaluate(th)
        c = np.asarray(correct, dtype=np.float64)
        h = np.asarray(hops, dtype=np.float64)
        apc = accuracy_per_compute(c, h)
        curve.append({"theta": float(th), "acc": float(np.mean(c)),
                      "mean_hops": float(np.mean(h)), "accpc": float(apc)})
        if apc > best_accpc:
            best_accpc, best_theta = apc, float(th)
    return {"theta_star": float(best_theta), "accpc_star": float(best_accpc), "curve": curve}


def run_halting(
    confidence_traj: np.ndarray,
    theta: float,
    *,
    min_hops: int = 1,
) -> np.ndarray:
    """Batched first-crossing halt reflex: hops_used = first hop >= min_hops where confidence >= theta.

    Args:
        confidence_traj: (n_items, T) arrival/progress confidence, column h = confidence after h hops
            (h=0 == start). Caller supplies whatever scalar its process emits per step.
        theta: frozen acceptance threshold.
        min_hops: forced minimum hops before any early halt (>= 0).

    Returns:
        hops_used: (n_items,) int -- the halt hop-count; items that never cross run to the ceiling T-1.
    """
    conf = np.asarray(confidence_traj, dtype=np.float64)
    if conf.ndim != 2:
        raise ValueError("confidence_traj must be 2-D (n_items, T); got shape %s" % (conf.shape,))
    n, T = conf.shape
    if T < 1:
        raise ValueError("confidence_traj must have at least one column")
    mh = max(0, int(min_hops))
    hop_idx = np.arange(T)[None, :]
    crossed = (conf >= float(theta)) & (hop_idx >= mh)          # (n, T)
    any_crossed = crossed.any(axis=1)
    first_idx = crossed.argmax(axis=1)                          # argmax -> first True; 0 if none
    hops_used = np.where(any_crossed, first_idx, T - 1).astype(np.int64)
    return hops_used


class AdaptiveHaltController:
    """Frozen scalar ACC/EVC halting dial. Tune theta ONCE on a calib set, then apply as a local reflex."""

    def __init__(self, theta: float) -> None:
        self.theta = float(theta)

    @classmethod
    def tuned(cls, theta_grid: Sequence[float],
              evaluate: Callable[[float], Tuple[Any, Any]]) -> "AdaptiveHaltController":
        """Tune theta* = argmax accuracy-per-compute on the calib set, freeze, and return the controller."""
        res = tune_halt_threshold(theta_grid, evaluate)
        ctrl = cls(res["theta_star"])
        ctrl.tuning = res  # keep the curve/accpc_star for inspection
        return ctrl

    def should_halt(self, confidence: Any, hops_used: Any = None, min_hops: int = 1) -> Any:
        """Local reflex: halt (accept current node, take no further hop) once confidence >= theta.

        Works elementwise on a python float, a numpy array, or a torch tensor (uses only >= and &).
        If hops_used is given, halting is gated by hops_used >= min_hops (force min_hops moves first).
        """
        arrived = confidence >= self.theta
        if hops_used is None:
            return arrived
        eligible = hops_used >= min_hops
        return arrived & eligible

    def run(self, confidence_traj: np.ndarray, min_hops: int = 1) -> np.ndarray:
        """Apply the frozen threshold over a (n_items, T) confidence trajectory -> hops_used."""
        return run_halting(confidence_traj, self.theta, min_hops=min_hops)


# --- module provenance constants (for callers that want to assert what they are relying on) ---
CERTIFIED_CELL = "exp_substrate_acc_evc_adaptive_halting_v1"
CERTIFIED_VERDICT = "HARD_PASS"                 # FULL, 5 seeds; MEASURED@data/<cell>/metrics.json
CERTIFIED_REGIME = {"N": 8192, "V": 1200, "frozen_dd": 4, "L_support": [2, 3, 4, 5, 6], "seeds": 5}
CERTIFIED_CONFIDENCE = "clean_arrival_cos_state_goal"   # noisy/graded arrival NOT covered; re-validate


def _selftest() -> None:
    """Scaffold-free mechanism selftest on a synthetic heterogeneous-length halting problem.

    Reproduces the certified physics WITHOUT the substrate: a fixed depth over/under-runs a
    heterogeneous corpus; adaptive halting on a clean arrival signal matches-or-beats accuracy at
    EQUAL average compute; a fixed-threshold control underperforms at matched budget; scrambling the
    signal collapses the gain toward depth-variance.
    """
    rng = np.random.default_rng(0)
    n = 4000
    L_support = np.array([2, 3, 4, 5, 6])           # mean 4 == FROZEN_DD (strongest fixed baseline)
    FROZEN_DD = 4
    T = int(L_support.max()) + 1                     # hop columns 0..6
    true_L = rng.choice(L_support, size=n)

    # clean arrival confidence: peaks (~1) exactly at the true arrival hop, low elsewhere; drift past
    # the goal drops it back down (reached-then-drifted physics). Small noise on both bands.
    conf = 0.05 * rng.standard_normal((n, T))
    conf[np.arange(n), true_L] += 1.0
    conf = np.clip(conf, -0.3, 1.3)

    # correctness model: an item is correct iff you STOP exactly at its true arrival hop (accept the
    # true target). Stop early -> not arrived; stop late -> drifted past. Matches the actor's no-STAY drift.
    # calibration split (first half) tunes theta; eval split (second half) reports (held-out).
    cal = np.arange(n // 2)
    ev = np.arange(n // 2, n)
    L_cal, L_ev = true_L[cal], true_L[ev]
    conf_cal = conf[cal]

    def evaluate(theta):
        hops = run_halting(conf_cal, theta, min_hops=1)
        correct = (hops == L_cal).astype(np.int8)
        return correct, hops

    ctrl = AdaptiveHaltController.tuned([0.15, 0.25, 0.35, 0.45, 0.55], evaluate)
    theta_star = ctrl.theta

    # --- eval arms (matched held-out corpus, differ ONLY by halt policy) ---
    def corr_ev(hops):
        return (np.asarray(hops) == L_ev).astype(np.int8)

    hops_fixed = np.full(ev.size, FROZEN_DD, dtype=np.int64)
    hops_adapt = ctrl.run(conf[ev], min_hops=1)
    rand_depth = rng.choice(L_support, size=ev.size)
    # scrambled: permute the eval confidence rows so arrival-hop correspondence is destroyed (matched scale)
    hops_scr = run_halting(conf[ev][rng.permutation(ev.size)], theta_star, min_hops=1)

    c_fixed = corr_ev(hops_fixed)
    c_adapt = corr_ev(hops_adapt)
    c_rand = corr_ev(rand_depth)
    c_scr = corr_ev(hops_scr)

    apc_fixed = accuracy_per_compute(c_fixed, hops_fixed)
    apc_adapt = accuracy_per_compute(c_adapt, hops_adapt)
    apc_rand = accuracy_per_compute(c_rand, rand_depth)
    apc_scr = accuracy_per_compute(c_scr, hops_scr)

    acc_fixed, acc_adapt = float(np.mean(c_fixed)), float(np.mean(c_adapt))
    mh_fixed, mh_adapt = float(np.mean(hops_fixed)), float(np.mean(hops_adapt))

    # 1. certified gain: adaptive beats fixed on accuracy, at EQUAL-or-lower average compute.
    assert acc_adapt > acc_fixed + 0.20, "adaptive did not beat fixed accuracy (A=%.3f F=%.3f)" % (acc_adapt, acc_fixed)
    assert mh_adapt <= mh_fixed * 1.10, "adaptive spent MORE compute than fixed (A=%.2f F=%.2f)" % (mh_adapt, mh_fixed)
    # 2. accuracy-per-compute win >= 15% relative (the certified HARD_PASS gate; here far above).
    assert apc_adapt > apc_fixed * 1.15, "accpc win below 15%% (A=%.4f F=%.4f)" % (apc_adapt, apc_fixed)
    # 3. discriminator fires: a fixed-threshold control at the SAME budget as adaptive still underperforms.
    matched_depth = int(round(mh_adapt))
    c_matched = corr_ev(np.full(ev.size, matched_depth))
    assert acc_adapt > float(np.mean(c_matched)) + 0.20, \
        "fixed-at-matched-budget was NOT beaten (A=%.3f fixed@%d=%.3f)" % (acc_adapt, matched_depth, float(np.mean(c_matched)))
    # 4. signal load-bearing, not depth variance: adaptive beats random-depth on accpc.
    assert apc_adapt > apc_rand, "adaptive did not beat random-depth (A=%.4f R=%.4f)" % (apc_adapt, apc_rand)
    # 5. telemetry-sensitivity: scrambling the arrival signal collapses the gain.
    assert apc_scr < apc_adapt * 0.75, "scramble did not collapse (S=%.4f A=%.4f)" % (apc_scr, apc_adapt)
    # 6. genuine reallocation, not collapse-to-fixed: adaptive varies its depth.
    assert float(np.std(hops_adapt)) >= 0.5, "hop spread too small (collapsed to fixed): %.2f" % float(np.std(hops_adapt))
    # 7. tuner returned a usable curve.
    assert 0.0 <= theta_star <= 1.0 and len(ctrl.tuning["curve"]) == 5, "tuner curve malformed"

    print("[hdlab.self_manager selftest] PASS: adaptive halting reproduces certified matched-compute gain "
          "acc[F=%.3f A=%.3f] hops[F=%.2f A=%.2f] accpc[F=%.4f A=%.4f R=%.4f S=%.4f] theta*=%.2f "
          "spread=%.2f (fixed-at-matched-budget beaten, scramble collapses, signal load-bearing)"
          % (acc_fixed, acc_adapt, mh_fixed, mh_adapt, apc_fixed, apc_adapt, apc_rand, apc_scr,
             theta_star, float(np.std(hops_adapt))), flush=True)


if __name__ == "__main__":
    _selftest()
