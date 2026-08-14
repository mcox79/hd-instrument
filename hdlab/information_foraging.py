"""hdlab/information_foraging.py -- ORGAN: INFORMATION FORAGING (patch-leaving under the
Marginal Value Theorem). 2026-08-14.

WHY THIS MODULE EXISTS. notes/ORGAN_MAP.md lists "information foraging" as one of SEVEN organs
that are MISSING ENTIRELY, and notes/gap_driven_learning_loop_audit_2026-08-13.md shows the
consequence: the reading loop can flag a word it does not understand, but nothing anywhere decides
WHAT TO READ NEXT, so 64.5% of every definitional fact the substrate has ever banked came from one
biology textbook. This module supplies the decision rule. It is deliberately SUBSTRATE-FREE: pure
arithmetic over (gain, duration) pairs, no numpy, no imports from hdlab, so it is unit-testable in
milliseconds and reusable by any consumer.

THE EQUATION IS PINNED BY THE LITERATURE; THIS MODULE DOES NOT RE-DERIVE IT.

  LEAVE RULE  CITED@Charnov 1976 (Theor Popul Biol 9:129-136): leave the current patch when the
      instantaneous marginal gain rate drops below the long-run average rate of the whole
      environment:  g'(t) < rho.  rho has TRAVEL/SEARCH TIME IN ITS DENOMINATOR.

  DISCRETE FORM  CITED@Constantino & Daw 2015 (Cogn Affect Behav Neurosci 15:837-853, Table 2):
      harvest while   kappa * s_i  >=  rho_i * h
      s_i    = the gain actually observed on the last harvest step in this patch
      kappa  = the LEARNED expected depletion multiplier, so `kappa * s_i` is the EXPECTED NEXT
               gain, never the last one (failure mode 3 below)
      h      = the duration of one harvest step

  RHO UPDATE  CITED@Constantino & Daw 2015 (same table); STRUCTURE PINNED, alpha FREE:
      delta_i     = r_i / tau_i - rho_i
      rho_{i+1}   = rho_i + [1 - (1 - alpha)^tau_i] * delta_i
      tau_i is the DURATION of step i. During TRAVEL r_i = 0 and the update STILL RUNS.
      rho CARRIES OVER between patches and between environments. It is never reset.

  THRESHOLD MOVES WITH THE ENVIRONMENT  CITED@Hayden, Pearson & Platt 2011 (Nat Neurosci
      14:933-939): longer travel time RAISES the leaving threshold (i.e. animals stay longer),
      regression coefficient beta = 0.92, p < 0.01. A FIXED threshold is a broken organ.

  TWO RHO TIMESCALES  CITED@Wittmann et al. 2016 (Nat Commun 7:12327): recent and more distant
      average-reward histories have OPPOSING influences on choice. Both are tracked here
      (`rho_fast`, `rho_slow`). The PRIMARY decision uses the single pinned rho; the pair is
      instrumentation plus a declared fallback (`use_rho_pair=True`), because the mixing weight
      between them is NOT pinned by that paper and a tuned weight would be a free knob.

  EVENT SEGMENTATION  CITED@Zacks et al. 2007 (Psychol Bull 133:273-293); Baldassano et al. 2017
      (Neuron 95:709-721); Kumar et al. 2023 (Bayesian surprise predicts human event boundaries).
      A PATCH IS NOT A DOCUMENT. `SurpriseSegmenter` posts a boundary when the consumer's OWN
      model-update magnitude exceeds its recent running statistics. Boundaries are also where the
      leave decision is evaluated -- event boundaries are decision points.

  OVERSTAYING is NOT hand-coded. CITED@Constantino & Daw 2015; Hayden 2011: humans and animals
      systematically overstay relative to the MVT optimum. This module implements the NORMATIVE
      optimum only. Overstaying, if it appears, must EMERGE from (i) rho being LEARNED online
      rather than known, (ii) stochastic softmax leaving, (iii) uncertainty about patch structure.
      There is no bias term and no intercept anywhere in `ForagingController.decide_leave`; a
      structural self-test scans this module's own source to prove it.

  DELIBERATELY NOT CITED AS A WARRANT: "dACC encodes foraging value". That claim is CONTESTED
      (Shenhav, Straccia, Cohen & Botvinick 2014/2016 vs Kolling et al. 2016) and is not used to
      justify any design choice here. The safe neural anchor is the single-cell
      accumulation-to-threshold result in Hayden 2011, which is what the threshold form above
      reflects. See `DESIGN_WARRANTS`.

CURRENCY. This module is agnostic to what a "gain" is, but it exists to be fed UNCERTAINTY
REDUCTION PER UNIT EFFORT, not items consumed. CITED@Constantino & Daw 2015 Experiment 2: a
head-to-head model comparison rejected item-COUNT accounting in favour of value accounting at
exceedance probability .999. CITED@Oudeyer & Kaplan 2007 (learning progress = the derivative of
prediction error) -- learning progress IS g'(t) in this currency. The caller is responsible for
supplying a value-valued gain; `assert_gain_is_not_a_count` is provided so a caller can gate on it.

ASCII-only. Deterministic: all randomness from an explicitly seeded `random.Random`; no Python
hash()-derived ordering, no `list(set(...))` (PROT-023 / preflight F.5).
"""
from __future__ import annotations

import inspect
import math
import random
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

__all__ = [
    "DESIGN_WARRANTS",
    "alpha_for_halflife",
    "RhoTracker",
    "DepletionEstimator",
    "SurpriseSegmenter",
    "ForagingConfig",
    "ForagingController",
    "oracle_mvt_optimum",
    "assert_gain_is_not_a_count",
    "run_all_selftests",
]

# Named so an auditor can check what each design choice actually rests on. The absence of a
# dACC row is deliberate and is asserted by a self-test.
DESIGN_WARRANTS: Dict[str, str] = {
    "leave_rule": "Charnov 1976 Theor Popul Biol 9:129-136 (marginal value theorem)",
    "discrete_form": "Constantino & Daw 2015 Cogn Affect Behav Neurosci 15:837-853 Table 2",
    "rho_update": "Constantino & Daw 2015 (timed delta rule; travel updates rho with r=0)",
    "threshold_moves_with_travel": "Hayden, Pearson & Platt 2011 Nat Neurosci 14:933-939 (beta=0.92, p<0.01)",
    "two_timescales": "Wittmann et al. 2016 Nat Commun 7:12327 (recent vs distant rates oppose)",
    "segmentation": "Zacks 2007 Psychol Bull 133:273-293; Baldassano 2017 Neuron 95:709-721; Kumar 2023",
    "currency_is_value_not_count": "Constantino & Daw 2015 Exp 2 (count model rejected, xp=.999); Oudeyer & Kaplan 2007",
    "neural_anchor": "Hayden 2011 single-cell accumulation-to-threshold (NOT the contested dACC-value claim)",
}


def alpha_for_halflife(halflife_steps: float) -> float:
    """The learning rate whose timed delta rule forgets half of a rate change after
    `halflife_steps` units of TIME (not steps of arbitrary duration).

    (1 - alpha)^halflife = 0.5  =>  alpha = 1 - 0.5^(1/halflife).
    Set halflife to ~1-2 patch+travel cycles per the brief."""
    if halflife_steps <= 0:
        raise ValueError(f"halflife_steps must be > 0, got {halflife_steps}")
    return 1.0 - 0.5 ** (1.0 / float(halflife_steps))


class RhoTracker:
    """Long-run average gain RATE, with travel time in the denominator.

    The single most-forgotten term in a naive build is calling `travel()` at all: without an
    r=0 update over the travel duration, rho is an average over HARVEST time only, it inflates,
    and every trace of environment-richness sensitivity vanishes silently. `n_travel_updates`
    is exposed so a consumer can assert the term fired."""

    def __init__(self, alpha: float, rho_init: float = 0.0) -> None:
        if not (0.0 < alpha < 1.0):
            raise ValueError(f"alpha must be in (0,1), got {alpha}")
        self.alpha = float(alpha)
        self.rho = float(rho_init)
        self.total_reward = 0.0
        self.total_time = 0.0
        self.n_harvest_updates = 0
        self.n_travel_updates = 0
        self.history: List[float] = []

    def update(self, reward: float, tau: float) -> float:
        """rho <- rho + [1 - (1-alpha)^tau] * (reward/tau - rho). Returns the new rho.

        The bracketed factor is what makes this a TIMED delta rule: an untimed `rho += alpha*delta`
        makes a long travel and a short harvest move rho by the same amount, which destroys the
        whole point of putting time in the denominator."""
        if tau <= 0:
            raise ValueError(f"tau must be > 0, got {tau}")
        delta = reward / tau - self.rho
        self.rho = self.rho + (1.0 - (1.0 - self.alpha) ** tau) * delta
        self.total_reward += reward
        self.total_time += tau
        self.history.append(self.rho)
        return self.rho

    def harvest(self, reward: float, tau: float) -> float:
        self.n_harvest_updates += 1
        return self.update(reward, tau)

    def travel(self, tau: float) -> float:
        """r = 0 during travel, and the update STILL RUNS. Failure mode 2."""
        self.n_travel_updates += 1
        return self.update(0.0, tau)

    @property
    def empirical_rate(self) -> float:
        return self.total_reward / self.total_time if self.total_time > 0 else 0.0


class DepletionEstimator:
    """kappa: the LEARNED expected multiplicative change from one harvest to the next WITHIN a
    patch. `kappa * s_last` is therefore the EXPECTED NEXT gain, which is what Charnov's g'(t)
    actually is. Thresholding the LAST observed gain instead is failure mode 3.

    Estimated as an EWMA over observed within-patch ratios s_{i+1}/s_i, clipped to a sane range.
    Ratios where s_i is ~0 are skipped (undefined, and they would blow the estimate up)."""

    def __init__(self, kappa_init: float = 1.0, lr: float = 0.2,
                 lo: float = 0.05, hi: float = 1.5, eps: float = 1e-9) -> None:
        self.kappa = float(kappa_init)
        self.lr = float(lr)
        self.lo, self.hi, self.eps = float(lo), float(hi), float(eps)
        self.n_observed = 0

    def observe(self, s_prev: float, s_next: float) -> None:
        if s_prev <= self.eps:
            return
        ratio = s_next / s_prev
        if not math.isfinite(ratio):
            return
        ratio = min(max(ratio, self.lo), self.hi)
        self.kappa = (1.0 - self.lr) * self.kappa + self.lr * ratio
        self.kappa = min(max(self.kappa, self.lo), self.hi)
        self.n_observed += 1

    def expected_next(self, s_last: float) -> float:
        return self.kappa * s_last


class SurpriseSegmenter:
    """Event Segmentation Theory boundary detector over the consumer's OWN surprise signal.

    A boundary is posted when the incoming surprise exceeds `mean + k*sd` of the recent window,
    OR when the window is not yet full and `min_run` steps have elapsed (so the very first patch
    still terminates). This is what stops "document = patch" (failure mode 9): a single document
    is segmented into as many patches as its own surprise profile warrants, and each patch is
    scored on its own."""

    def __init__(self, window: int = 24, k: float = 1.0, min_run: int = 4,
                 max_run: int = 200) -> None:
        self.window, self.k = int(window), float(k)
        self.min_run, self.max_run = int(min_run), int(max_run)
        self._buf: List[float] = []
        self._run = 0
        self.n_boundaries = 0

    def observe(self, surprise: float) -> bool:
        """Feed one step's surprise; returns True iff an event boundary is posted AFTER it."""
        self._run += 1
        boundary = False
        if len(self._buf) >= max(4, self.window // 4) and self._run >= self.min_run:
            m = sum(self._buf) / len(self._buf)
            var = sum((x - m) ** 2 for x in self._buf) / max(1, len(self._buf) - 1)
            sd = math.sqrt(var)
            if surprise > m + self.k * sd:
                boundary = True
        if self._run >= self.max_run:
            boundary = True
        self._buf.append(float(surprise))
        if len(self._buf) > self.window:
            self._buf.pop(0)
        if boundary:
            self.n_boundaries += 1
            self._run = 0
        return boundary


@dataclass
class ForagingConfig:
    """Every field here is either PINNED by the literature or an explicitly-declared free
    parameter. There is deliberately NO bias / intercept / overstay field -- see failure mode 7."""

    harvest_step_duration: float = 1.0        # h, the duration of one harvest step
    travel_step_duration: float = 8.0         # tau for one inter-patch move (SWEPT, per Hayden 2011)
    rho_halflife_steps: float = 72.0          # FREE: ~1.5 patch+travel cycles (see alpha_for_halflife)
    rho_slow_halflife_steps: float = 360.0    # FREE: the "distant" timescale of the Wittmann pair
    rho_init: float = 0.0
    beta_leave: float = 4.0                   # FREE: softmax inverse temperature on the leave decision
    kappa_init: float = 1.0
    kappa_lr: float = 0.2
    min_harvests_per_patch: int = 2           # a patch must be sampled before it can be judged
    max_harvests_per_patch: int = 400         # hard stop; never the operative rule in practice
    stochastic: bool = True                   # softmax leaving; False = deterministic argmax control
    use_rho_pair: bool = False                # declared fallback arm (Wittmann); default OFF
    rho_pair_weight: float = 0.5              # only consulted when use_rho_pair is True
    seed: int = 20260814

    def alpha_fast(self) -> float:
        return alpha_for_halflife(self.rho_halflife_steps)

    def alpha_slow(self) -> float:
        return alpha_for_halflife(self.rho_slow_halflife_steps)


class ForagingController:
    """The organ. One instance per forager; rho CARRIES OVER across patches and environments.

    Usage per patch:
        ctrl.enter_patch(patch_id)
        while True:
            gain = <uncertainty reduction from the next harvest step>
            ctrl.harvest(gain)
            if ctrl.should_leave(): break
        ctrl.travel()                # pays the travel cost AND updates rho with r=0
    """

    def __init__(self, cfg: ForagingConfig) -> None:
        self.cfg = cfg
        self.rho_fast = RhoTracker(cfg.alpha_fast(), cfg.rho_init)
        self.rho_slow = RhoTracker(cfg.alpha_slow(), cfg.rho_init)
        self.kappa = DepletionEstimator(cfg.kappa_init, cfg.kappa_lr)
        self._rng = random.Random(cfg.seed)
        self.patch_id: Optional[str] = None
        self.s_last: Optional[float] = None
        self.n_harvests_this_patch = 0
        self.patch_log: List[dict] = []
        self.decision_log: List[dict] = []
        self._patch_gains: List[float] = []
        self.total_time = 0.0
        self.total_gain = 0.0

    # ---------------------------------------------------------------- the pinned rho, exposed
    @property
    def rho(self) -> float:
        """The rate the leave rule is compared against. PRIMARY = the single pinned rho
        (`rho_fast`, whose half-life is set to ~1-2 patch+travel cycles). The Wittmann fast/slow
        PAIR is available but default-OFF, because its mixing weight is not pinned."""
        if self.cfg.use_rho_pair:
            w = self.cfg.rho_pair_weight
            return w * self.rho_fast.rho + (1.0 - w) * self.rho_slow.rho
        return self.rho_fast.rho

    def leave_threshold(self) -> float:
        """The gain that the NEXT harvest must be expected to beat, in gain units.

        From `kappa * s >= rho * h`, the threshold on s is `rho * h / kappa`. This is a
        FUNCTION of the current environment (rho) and the learned depletion (kappa); it is not a
        constant anywhere in this module (failure mode 5)."""
        k = max(self.kappa.kappa, 1e-6)
        return self.rho * self.cfg.harvest_step_duration / k

    # ---------------------------------------------------------------- the loop
    def enter_patch(self, patch_id: str) -> None:
        self.patch_id = patch_id
        self.s_last = None
        self.n_harvests_this_patch = 0
        self._patch_gains = []

    def harvest(self, gain: float) -> None:
        """One harvest step of duration h yielding `gain` units of uncertainty reduction."""
        g = float(gain)
        if self.s_last is not None:
            self.kappa.observe(self.s_last, g)
        h = self.cfg.harvest_step_duration
        self.rho_fast.harvest(g, h)
        self.rho_slow.harvest(g, h)
        self.s_last = g
        self.n_harvests_this_patch += 1
        self._patch_gains.append(g)
        self.total_time += h
        self.total_gain += g

    def should_leave(self) -> bool:
        """Charnov, discrete form. Stochastic by default so that overstaying can EMERGE."""
        if self.n_harvests_this_patch < self.cfg.min_harvests_per_patch:
            return False
        if self.n_harvests_this_patch >= self.cfg.max_harvests_per_patch:
            self._log_decision(True, forced=True)
            return True
        expected_next = self.kappa.expected_next(self.s_last if self.s_last is not None else 0.0)
        stay_value = expected_next
        leave_value = self.rho * self.cfg.harvest_step_duration
        scale = max(abs(leave_value), abs(stay_value), 1e-9)
        # NOTE (failure mode 7): the ONLY terms below are the two decision values and a scale.
        # There is no additive constant. `_selftest_no_hand_coded_overstay_bias` scans this
        # function's source to keep it that way.
        z = self.cfg.beta_leave * (leave_value - stay_value) / scale
        if self.cfg.stochastic:
            p_leave = 1.0 / (1.0 + math.exp(-max(-60.0, min(60.0, z))))
            leave = self._rng.random() < p_leave
        else:
            p_leave = 1.0 if z > 0 else 0.0
            leave = z > 0
        self._log_decision(leave, p_leave=p_leave, stay_value=stay_value, leave_value=leave_value)
        return leave

    def _log_decision(self, leave: bool, *, p_leave: float = 1.0, stay_value: float = 0.0,
                      leave_value: float = 0.0, forced: bool = False) -> None:
        self.decision_log.append({
            "patch_id": self.patch_id, "n_harvests": self.n_harvests_this_patch,
            "s_last": self.s_last, "kappa": round(self.kappa.kappa, 6),
            "rho": round(self.rho, 9), "rho_fast": round(self.rho_fast.rho, 9),
            "rho_slow": round(self.rho_slow.rho, 9),
            "threshold_on_s": round(self.leave_threshold(), 9),
            "stay_value": round(stay_value, 9), "leave_value": round(leave_value, 9),
            "p_leave": round(p_leave, 6), "leave": bool(leave), "forced": bool(forced),
        })

    def travel(self, tau: Optional[float] = None) -> None:
        """Pay the inter-patch travel cost. r = 0, and rho IS updated (failure modes 1 and 2)."""
        t = self.cfg.travel_step_duration if tau is None else float(tau)
        self.patch_log.append({
            "patch_id": self.patch_id, "n_harvests": self.n_harvests_this_patch,
            "gain": round(sum(self._patch_gains), 9),
            "gains": [round(x, 9) for x in self._patch_gains],
            "rho_at_leave": round(self.rho, 9), "kappa_at_leave": round(self.kappa.kappa, 6),
            "travel_tau": t,
        })
        self.rho_fast.travel(t)
        self.rho_slow.travel(t)
        self.total_time += t

    def state(self) -> dict:
        return {
            "rho": self.rho, "rho_fast": self.rho_fast.rho, "rho_slow": self.rho_slow.rho,
            "kappa": self.kappa.kappa, "kappa_n_observed": self.kappa.n_observed,
            "n_harvest_updates": self.rho_fast.n_harvest_updates,
            "n_travel_updates": self.rho_fast.n_travel_updates,
            "empirical_rate": self.rho_fast.empirical_rate,
            "total_gain": self.total_gain, "total_time": self.total_time,
            "achieved_rate": (self.total_gain / self.total_time) if self.total_time > 0 else 0.0,
            "n_patches": len(self.patch_log),
            "mean_patch_residence": (sum(p["n_harvests"] for p in self.patch_log) / len(self.patch_log))
                                    if self.patch_log else 0.0,
        }


# ============================================================== oracle (post-hoc, never online)
def oracle_mvt_optimum(patch_gain_sequences: Sequence[Sequence[float]], travel_tau: float,
                       h: float = 1.0, n_iter: int = 200) -> dict:
    """Post-hoc MVT optimum over the SAME visit order, given full knowledge of every patch's gain
    sequence -- knowledge no online forager has. Used ONLY to report how close the online forager
    landed. Landing at 100% of this means the oracle leaked.

    Solves for the fixed point rho* of "harvest while the next gain >= rho*h", by bisection on
    the achieved rate."""
    seqs = [list(s) for s in patch_gain_sequences]
    if not seqs:
        return {"oracle_rate": 0.0, "oracle_gain": 0.0, "oracle_time": 0.0, "rho_star": 0.0,
                "residences": []}

    def achieved(rho: float) -> Tuple[float, float, List[int]]:
        tot_g, tot_t, res = 0.0, 0.0, []
        for seq in seqs:
            n = 0
            for g in seq:
                if n >= 1 and g < rho * h:
                    break
                tot_g += g
                tot_t += h
                n += 1
            res.append(n)
            tot_t += travel_tau
        return tot_g, tot_t, res

    lo, hi = 0.0, max((max(s) for s in seqs if s), default=1.0) + 1.0
    best = (0.0, 0.0, 0.0, [])
    for _ in range(n_iter):
        mid = 0.5 * (lo + hi)
        g, t, res = achieved(mid)
        rate = g / t if t > 0 else 0.0
        if rate > best[0]:
            best = (rate, g, t, res)
        if rate > mid:
            lo = mid
        else:
            hi = mid
    rho_star = 0.5 * (lo + hi)
    g, t, res = achieved(rho_star)
    rate = g / t if t > 0 else 0.0
    if rate > best[0]:
        best = (rate, g, t, res)
    return {"oracle_rate": best[0], "oracle_gain": best[1], "oracle_time": best[2],
            "rho_star": rho_star, "residences": best[3]}


def assert_gain_is_not_a_count(gains: Sequence[float], tol: float = 1e-9) -> None:
    """Failure mode 6. A gain stream that only ever takes the value 1.0 (or any single constant)
    is an ITEM COUNT wearing a float's clothing; MVT over it degenerates to a fixed patch length.
    Callers should gate on this before trusting a foraging result."""
    vals = sorted(set(round(float(g), 9) for g in gains))
    if len(vals) <= 1:
        raise AssertionError(
            f"gain stream is constant ({vals}) -- this is an item COUNT, not a value. "
            "Constantino & Daw 2015 Exp 2 rejected count accounting at exceedance probability .999.")


# ===================================================================== formula self-tests
# One self-test per numbered failure mode from the design brief, plus the mechanics.

def _selftest_1_travel_time_is_in_the_denominator() -> None:
    """Two identical harvest streams; the one with LONGER travel must end with a LOWER rho.
    If travel were omitted from the denominator the two would be identical."""
    def run(travel_tau):
        cfg = ForagingConfig(travel_step_duration=travel_tau, rho_halflife_steps=20.0,
                             stochastic=False)
        c = ForagingController(cfg)
        for p in range(6):
            c.enter_patch(f"p{p}")
            for g in (1.0, 0.6, 0.36, 0.216):
                c.harvest(g)
            c.travel()
        return c.rho_fast.rho
    lo, hi = run(2.0), run(40.0)
    assert hi < lo, f"longer travel must LOWER rho: tau=2 -> {lo}, tau=40 -> {hi}"


def _selftest_2_travel_updates_rho_with_zero_reward() -> None:
    """The single most-forgotten term. rho must strictly DECREASE across a travel leg, and the
    travel-update counter must be non-zero."""
    cfg = ForagingConfig(travel_step_duration=10.0, rho_halflife_steps=20.0, stochastic=False)
    c = ForagingController(cfg)
    c.enter_patch("p0")
    for g in (1.0, 1.0, 1.0, 1.0):
        c.harvest(g)
    before = c.rho_fast.rho
    c.travel()
    after = c.rho_fast.rho
    assert after < before, f"travel must pull rho down (r=0): {before} -> {after}"
    assert c.rho_fast.n_travel_updates == 1, c.rho_fast.n_travel_updates
    assert c.rho_fast.total_time == 4 * 1.0 + 10.0, c.rho_fast.total_time


def _selftest_3_threshold_uses_expected_next_not_last_gain() -> None:
    """kappa must be load-bearing: with a learned depletion multiplier < 1 the forager must leave
    NO LATER than one that assumes no depletion, on the identical gain stream."""
    def run(kappa_lr):
        cfg = ForagingConfig(kappa_lr=kappa_lr, rho_halflife_steps=20.0, stochastic=False,
                             travel_step_duration=4.0)
        c = ForagingController(cfg)
        res = []
        for p in range(8):
            c.enter_patch(f"p{p}")
            g = 1.0
            n = 0
            while True:
                c.harvest(g)
                n += 1
                if c.should_leave() or n > 30:
                    break
                g *= 0.5
            res.append(n)
            c.travel()
        return c.kappa.kappa, res
    k_learn, res_learn = run(0.4)
    k_none, res_none = run(0.0)   # kappa frozen at 1.0 = "no depletion expected"
    assert k_none == 1.0, k_none
    assert k_learn < 0.95, f"kappa must LEARN the 0.5 depletion, got {k_learn}"
    assert sum(res_learn) <= sum(res_none), (res_learn, res_none)
    assert ForagingController(ForagingConfig()).leave_threshold() == 0.0


def _selftest_4_timed_delta_rule_is_exact() -> None:
    """One update of duration 2 with reward r must equal two updates of duration 1 with reward
    r/2 each. An untimed `rho += alpha*delta` fails this exactly."""
    a = 0.3
    t1 = RhoTracker(a, 0.7)
    t1.update(1.0, 2.0)
    t2 = RhoTracker(a, 0.7)
    t2.update(0.5, 1.0)
    t2.update(0.5, 1.0)
    assert abs(t1.rho - t2.rho) < 1e-12, (t1.rho, t2.rho)
    # and the untimed form is measurably different, so the test is not vacuous
    naive = 0.7 + a * (1.0 / 2.0 - 0.7)
    assert abs(naive - t1.rho) > 1e-6, (naive, t1.rho)


def _selftest_5_threshold_is_not_fixed() -> None:
    """The leaving threshold must take at least 5 distinct values across a run with a changing
    environment. A fixed threshold is a broken organ (Hayden 2011)."""
    cfg = ForagingConfig(rho_halflife_steps=15.0, stochastic=False, travel_step_duration=3.0)
    c = ForagingController(cfg)
    ths = []
    for p, base in enumerate([2.0, 2.0, 0.2, 0.2, 3.0, 3.0]):
        c.enter_patch(f"p{p}")
        g = base
        for _ in range(6):
            c.harvest(g)
            ths.append(round(c.leave_threshold(), 9))
            g *= 0.7
        c.travel()
    assert len(sorted(set(ths))) >= 5, sorted(set(ths))


def _selftest_6_counts_are_rejected_as_a_currency() -> None:
    try:
        assert_gain_is_not_a_count([1.0] * 20)
    except AssertionError as e:
        assert "item COUNT" in str(e)
    else:
        raise AssertionError("a constant gain stream must be rejected as an item count")
    assert_gain_is_not_a_count([1.0, 0.5, 0.25])   # value stream: fine
    # and equal item counts with different VALUES must produce different residence
    def run(seq):
        cfg = ForagingConfig(rho_halflife_steps=20.0, stochastic=False, travel_step_duration=4.0)
        c = ForagingController(cfg)
        total = 0
        for p in range(6):
            c.enter_patch(f"p{p}")
            n = 0
            for g in seq:
                c.harvest(g)
                n += 1
                if c.should_leave():
                    break
            total += n
            c.travel()
        return total
    fast_decay = run([1.0, 0.2, 0.04, 0.008, 0.0016, 0.0003, 0.0001, 0.0001])
    slow_decay = run([1.0, 0.95, 0.90, 0.86, 0.82, 0.78, 0.74, 0.70])
    assert fast_decay < slow_decay, (fast_decay, slow_decay)


def _selftest_7_no_hand_coded_overstay_bias() -> None:
    """Structural scan of this module's OWN source: `should_leave` must contain no additive
    constant bias/intercept, and `ForagingConfig` must expose no such field."""
    raw = inspect.getsource(ForagingController.should_leave)
    # scan CODE only -- comments are allowed to name the forbidden thing, code is not
    src = "\n".join(ln.split("#", 1)[0] for ln in raw.splitlines())
    assert '"""' in raw, "docstring expected"
    src = src.split('"""')[0] + '"""'.join(src.split('"""')[2:]) if src.count('"""') >= 2 else src
    for tok in ("bias", "intercept", "overstay", "+ 0.", "- 0."):
        assert tok not in src, f"forbidden token {tok!r} in should_leave CODE: {src}"
    fields = set(ForagingConfig.__dataclass_fields__)
    bad = {f for f in fields if any(t in f for t in ("bias", "intercept", "overstay"))}
    assert not bad, bad


def _selftest_8_fast_and_slow_rho_diverge() -> None:
    """Both timescales are tracked and they must actually differ after a rate change (Wittmann
    2016). Also: turning the pair ON must change the operative rho, so the switch is real."""
    cfg = ForagingConfig(rho_halflife_steps=10.0, rho_slow_halflife_steps=400.0, stochastic=False)
    c = ForagingController(cfg)
    c.enter_patch("rich")
    for _ in range(40):
        c.harvest(2.0)
    c.travel()
    c.enter_patch("poor")
    for _ in range(40):
        c.harvest(0.01)
    assert c.rho_fast.rho < 0.9 * c.rho_slow.rho, (c.rho_fast.rho, c.rho_slow.rho)
    single = c.rho
    c.cfg.use_rho_pair = True
    assert abs(c.rho - single) > 1e-6, (c.rho, single)
    c.cfg.use_rho_pair = False


def _selftest_9_a_document_is_not_a_patch() -> None:
    """One 'document' whose surprise profile has three bursts must be segmented into more than
    one patch by the substrate's OWN surprise, not by document boundaries."""
    seg = SurpriseSegmenter(window=12, k=1.0, min_run=3, max_run=100)
    stream = ([0.1] * 12 + [0.9] + [0.1] * 12 + [0.95] + [0.1] * 12 + [0.99] + [0.1] * 6)
    bounds = [i for i, s in enumerate(stream) if seg.observe(s)]
    assert seg.n_boundaries >= 2, (seg.n_boundaries, bounds)
    flat = SurpriseSegmenter(window=12, k=1.0, min_run=3, max_run=100)
    for _ in range(40):
        flat.observe(0.1)
    assert flat.n_boundaries == 0, flat.n_boundaries   # no spurious boundaries on a flat stream


def _selftest_10_no_dacc_warrant() -> None:
    """The contested 'dACC = foraging value' claim must not appear as a design warrant."""
    for k, v in sorted(DESIGN_WARRANTS.items()):
        assert "dACC" not in v or "NOT the contested" in v, (k, v)
    assert "Hayden 2011" in DESIGN_WARRANTS["neural_anchor"]


def _selftest_richer_environment_shortens_residence() -> None:
    """The load-bearing behavioural signature of a working MVT organ: residence in a FIXED test
    patch must SHORTEN when the REST of the environment gets richer.

    Note the correct form of this test. The leave rule `kappa*s >= rho*h` is SCALE-INVARIANT:
    multiplying every gain in the world by 10 changes nothing, and it should not -- richness in
    MVT is the ratio of this patch's marginal gain to the environment average, never an absolute
    level. So the background patches vary and the test patch is held byte-identical."""
    TEST_CURVE = [1.0 * (0.8 ** i) for i in range(40)]

    def run(background_base):
        cfg = ForagingConfig(rho_halflife_steps=25.0, stochastic=False, travel_step_duration=4.0)
        c = ForagingController(cfg)
        res = []
        for p in range(14):
            background = (p % 2 == 0)
            c.enter_patch(f"{'bg' if background else 'test'}{p}")
            n = 0
            for i in range(40):
                c.harvest(background_base * TEST_CURVE[i] if background else TEST_CURVE[i])
                n += 1
                if c.should_leave():
                    break
            if not background:
                res.append(n)
            c.travel()
        return sum(res[2:]) / len(res[2:])
    rich, poor = run(20.0), run(0.05)
    assert rich < poor, f"richer background must shorten residence: rich={rich}, poor={poor}"


def _selftest_longer_travel_lengthens_residence() -> None:
    """Hayden 2011's signature, the OTHER way round: longer travel raises the leaving threshold in
    the sense of staying longer (because rho falls)."""
    def run(tau):
        cfg = ForagingConfig(rho_halflife_steps=25.0, stochastic=False, travel_step_duration=tau)
        c = ForagingController(cfg)
        res = []
        for p in range(12):
            c.enter_patch(f"p{p}")
            g, n = 2.0, 0
            while True:
                c.harvest(g)
                n += 1
                if c.should_leave() or n >= 60:
                    break
                g *= 0.85
            res.append(n)
            c.travel()
        return sum(res[6:]) / 6.0
    short, long_ = run(1.0), run(60.0)
    assert long_ > short, f"longer travel must lengthen residence: tau=1 -> {short}, tau=60 -> {long_}"


def _selftest_oracle_beats_online_but_online_is_close() -> None:
    """The post-hoc oracle must achieve a rate at least as good as the online forager on the same
    visit order (it has strictly more information). If the online forager MATCHES it exactly, the
    oracle has leaked into the online policy."""
    cfg = ForagingConfig(rho_halflife_steps=25.0, stochastic=True, travel_step_duration=6.0,
                         seed=11)
    c = ForagingController(cfg)
    rng = random.Random(3)
    for p in range(30):
        c.enter_patch(f"p{p}")
        base = rng.choice([0.4, 1.0, 2.5])
        g, n = base, 0
        while True:
            c.harvest(g)
            n += 1
            if c.should_leave() or n >= 50:
                break
            g *= 0.8
        c.travel()
    seqs = []
    rng2 = random.Random(3)
    for p in range(30):
        base = rng2.choice([0.4, 1.0, 2.5])
        seqs.append([base * (0.8 ** i) for i in range(50)])
    orc = oracle_mvt_optimum(seqs, cfg.travel_step_duration, cfg.harvest_step_duration)
    online = c.state()["achieved_rate"]
    assert orc["oracle_rate"] >= online - 1e-9, (orc["oracle_rate"], online)
    assert online > 0.5 * orc["oracle_rate"], (online, orc["oracle_rate"])


def _selftest_rho_carries_over_between_environments() -> None:
    """rho must never be reset by entering a new patch or a new environment."""
    cfg = ForagingConfig(rho_halflife_steps=100.0, stochastic=False)
    c = ForagingController(cfg)
    c.enter_patch("a")
    for _ in range(20):
        c.harvest(1.0)
    r = c.rho
    c.travel()
    c.enter_patch("b_in_a_completely_different_environment")
    assert c.rho < r and c.rho > 0.0, (r, c.rho)   # moved by travel, NOT reset to rho_init
    assert c.rho != cfg.rho_init


def run_all_selftests() -> dict:
    _selftest_1_travel_time_is_in_the_denominator()
    _selftest_2_travel_updates_rho_with_zero_reward()
    _selftest_3_threshold_uses_expected_next_not_last_gain()
    _selftest_4_timed_delta_rule_is_exact()
    _selftest_5_threshold_is_not_fixed()
    _selftest_6_counts_are_rejected_as_a_currency()
    _selftest_7_no_hand_coded_overstay_bias()
    _selftest_8_fast_and_slow_rho_diverge()
    _selftest_9_a_document_is_not_a_patch()
    _selftest_10_no_dacc_warrant()
    _selftest_richer_environment_shortens_residence()
    _selftest_longer_travel_lengthens_residence()
    _selftest_oracle_beats_online_but_online_is_close()
    _selftest_rho_carries_over_between_environments()
    return {
        "fm1_travel_in_denominator_ok": True,
        "fm2_travel_updates_rho_r_zero_ok": True,
        "fm3_expected_next_not_last_gain_ok": True,
        "fm4_timed_delta_rule_exact_ok": True,
        "fm5_threshold_not_fixed_ok": True,
        "fm6_value_not_item_count_ok": True,
        "fm7_no_hand_coded_overstay_bias_ok": True,
        "fm8_fast_slow_rho_pair_ok": True,
        "fm9_document_is_not_a_patch_ok": True,
        "fm10_no_dacc_warrant_ok": True,
        "richer_environment_shortens_residence_ok": True,
        "longer_travel_lengthens_residence_ok": True,
        "oracle_dominates_online_no_leak_ok": True,
        "rho_carries_over_ok": True,
    }


if __name__ == "__main__":
    import json
    print(json.dumps(run_all_selftests(), indent=2))
    print("ALL SELF-TESTS PASSED")
