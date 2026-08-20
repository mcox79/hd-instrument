"""A single-seed result cannot return a PASS from this module. There is no call signature for it.

WHY THIS EXISTS, AND IT IS THE SAME REASON `tools/rank_with_ties.py` EXISTS.
On 2026-08-20 I withdrew FOUR of my own claims in one session. Every one had the identical shape:

    one seed produced a clean-looking number, and I led with it.

The rule that names this -- *a single-seed win is a HYPOTHESIS* -- is in MEMORY.md, in CLAUDE.md,
and was sitting in my own limits section of the note whose headline I then had to retract. **A rule
in a document is a habit; a habit is not a guard.** The project already learned this once: the tie
rule was written down on the morning of 2026-08-20 and violated twice the same day, so it was moved
into a function. This is that move, for replication.

WHAT IT REFUSES TO DO:
  * return `REPLICATED` from fewer than `min_seeds` (default 2) seeds -- returns
    `SINGLE_SEED_HYPOTHESIS` instead, whatever the effect size;
  * ignore an INFORMATION-FREE CONTROL. If you pass control effects it checks whether the control
    reproduced HALF the treatment's effect on any seed, and calls `ARTIFACT_CONTROL_MATCHES` when it
    did on a third of them or more. **This is the check that caught the real one**: a random vector
    beat the right definition on seed 101, and the wrong definition tied it on seed 13;
  * paper over a SIGN FLIP across seeds;
  * paper over a magnitude that swings by more than `unstable_ratio` (default 5x) across seeds --
    the real case ran -16.0 / -1.0 / -5.0, a 16x spread that averaged to something publishable.

WHAT IT DOES NOT DO: decide whether the effect matters. It has no access to your floors, your CIs or
your task. **It answers "did this reproduce and is it distinguishable from nothing", never "is this
good".** Clearing this gate is necessary and nowhere near sufficient -- the measurement bar
(CI-separated margin over the strongest RUN floor) still applies on top.

CONVENTION: effects are `treatment - baseline` in the metric's own units, and `lower_is_better`
says which sign is an improvement. Control effects are in the SAME units, one list per control arm.

    from replication_gate import replication_verdict
    v = replication_verdict([-16.0, -1.0, -5.0],
                            controls={"NOISE": [23.5, -8.0, 5.0], "SHUFFLE": [3.5, 9.0, -4.0]},
                            lower_is_better=True)
    print(v.verdict, "|", v.why)     # ARTIFACT_CONTROL_MATCHES | ...

Run `python tools/replication_gate.py --self-test` -- it is checked against the real 2026-08-20
failure AND against a genuine effect, because a guard that flags everything gets ignored.
"""
from __future__ import annotations

import statistics
import sys
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence

SINGLE_SEED = "SINGLE_SEED_HYPOTHESIS"
ARTIFACT = "ARTIFACT_CONTROL_MATCHES"
SIGN_FLIP = "INCONSISTENT_SIGN"
UNSTABLE = "UNSTABLE_MAGNITUDE"
REPLICATED = "REPLICATED"


@dataclass
class ReplicationVerdict:
    verdict: str
    why: str
    n_seeds: int
    per_seed: List[float]
    median_effect: float
    sign_agreement: float
    magnitude_ratio: float
    control_matched_seeds: Dict[str, List[int]] = field(default_factory=dict)

    @property
    def is_pass(self) -> bool:
        """The ONLY property that reads as success. Deliberately not a bare bool return."""
        return self.verdict == REPLICATED

    def __str__(self) -> str:
        lines = ["%s -- %s" % (self.verdict, self.why),
                 "  seeds=%d  per-seed effects=%s" % (self.n_seeds,
                                                      ", ".join("%+.2f" % e for e in self.per_seed)),
                 "  median=%+.2f  sign agreement=%.0f%%  magnitude spread=%.1fx"
                 % (self.median_effect, 100 * self.sign_agreement, self.magnitude_ratio)]
        for name, seeds in self.control_matched_seeds.items():
            if seeds:
                lines.append("  !! control %r reproduced >=half the effect on seed index %s"
                             % (name, seeds))
        return "\n".join(lines)


def replication_verdict(effects: Sequence[float],
                        *,
                        controls: Optional[Dict[str, Sequence[float]]] = None,
                        lower_is_better: bool = True,
                        min_seeds: int = 2,
                        unstable_ratio: float = 5.0,
                        control_fraction: float = 1 / 3) -> ReplicationVerdict:
    """Did this reproduce, and is it distinguishable from an information-free control?"""
    eff = [float(e) for e in effects]
    if not eff:
        raise ValueError("no effects given -- a verdict on zero seeds is not a verdict")
    n = len(eff)
    # An IMPROVEMENT is negative when lower_is_better; normalise so positive == improvement.
    norm = [(-e if lower_is_better else e) for e in eff]
    med = statistics.median(eff)
    n_pos = sum(1 for x in norm if x > 0)
    agreement = max(n_pos, n - n_pos) / n
    mags = [abs(x) for x in norm]
    lo = min(m for m in mags) if mags else 0.0
    ratio = (max(mags) / lo) if lo > 1e-12 else float("inf")

    matched: Dict[str, List[int]] = {}
    if controls:
        for name, cvals in controls.items():
            cv = [float(c) for c in cvals]
            if len(cv) != n:
                raise ValueError("control %r has %d seeds, effects have %d -- they must be paired"
                                 % (name, len(cv), n))
            cnorm = [(-c if lower_is_better else c) for c in cv]
            # The control "matches" when it reproduces at least HALF the treatment's improvement.
            matched[name] = [i for i in range(n) if cnorm[i] >= 0.5 * norm[i] and norm[i] > 0]

    if n < min_seeds:
        return ReplicationVerdict(
            SINGLE_SEED, "only %d seed(s); %d required. A single-seed win is a HYPOTHESIS -- this "
                         "module will not call it anything else, at any effect size."
            % (n, min_seeds), n, eff, med, agreement, ratio, matched)

    worst = max((len(v) for v in matched.values()), default=0)
    if worst and worst >= max(1, int(round(control_fraction * n))):
        bad = {k: v for k, v in matched.items() if v}
        return ReplicationVerdict(
            ARTIFACT, "an INFORMATION-FREE control reproduced >=half the effect on %d of %d seeds "
                      "(%s). The effect is not distinguishable from the control, so it is not the "
                      "treatment's." % (worst, n, bad), n, eff, med, agreement, ratio, matched)

    if agreement < 1.0:
        return ReplicationVerdict(
            SIGN_FLIP, "the effect changes SIGN across seeds (%s). A median over a sign flip is not "
                       "an effect." % ", ".join("%+.2f" % e for e in eff),
            n, eff, med, agreement, ratio, matched)

    if ratio > unstable_ratio:
        return ReplicationVerdict(
            UNSTABLE, "magnitude swings %.1fx across seeds (%s), over the %.1fx limit. Report the "
                      "SMALLEST seed, not the median." % (ratio, ", ".join("%+.2f" % e for e in eff),
                                                          unstable_ratio),
            n, eff, med, agreement, ratio, matched)

    return ReplicationVerdict(
        REPLICATED, "same sign on %d/%d seeds, magnitude stable within %.1fx, and no control "
                    "reproduced half the effect. NOTE: this says REPRODUCIBLE, not GOOD -- the "
                    "floor/CI bar still applies." % (n, n, ratio),
        n, eff, med, agreement, ratio, matched)


def _self_test() -> int:
    fails = []

    # 1. THE REAL 2026-08-20 FAILURE. BOTH - PROFILE across seeds 7/101/13, with the two
    #    information-free blends actually run. MUST come back ARTIFACT.
    v = replication_verdict([-16.0, -1.0, -5.0],
                            controls={"NOISE": [23.5, -8.0, 5.0], "SHUFFLE": [3.5, 9.0, -4.0]},
                            lower_is_better=True)
    print("1. real failure (BOTH vs PROFILE, 3 seeds):", v.verdict)
    if v.verdict != ARTIFACT:
        fails.append("the real 2026-08-20 artifact was not caught: got %s" % v.verdict)
    if v.is_pass:
        fails.append("is_pass True on the known artifact")

    # 2. THE SAME RESULT AT THE MOMENT I PUBLISHED IT -- one seed. MUST NOT be REPLICATED.
    v1 = replication_verdict([-16.0], controls={"NOISE": [23.5]}, lower_is_better=True)
    print("2. one seed, big clean effect:          ", v1.verdict)
    if v1.verdict != SINGLE_SEED:
        fails.append("single seed did not return SINGLE_SEED_HYPOTHESIS: %s" % v1.verdict)

    # 3. NO CRY WOLF. A genuine, stable, control-clearing effect MUST pass, or the guard gets
    #    ignored -- the same reason rank_with_ties has a tie-free negative control.
    v2 = replication_verdict([-16.0, -15.0, -17.5],
                             controls={"NOISE": [2.0, -1.0, 0.5]}, lower_is_better=True)
    print("3. genuine stable effect (must PASS):   ", v2.verdict)
    if v2.verdict != REPLICATED or not v2.is_pass:
        fails.append("a genuine effect was flagged (%s) -- a guard that flags everything is "
                     "ignored" % v2.verdict)

    # 4. SIGN FLIP hidden by a median.
    v3 = replication_verdict([-16.0, +9.0, -4.0], lower_is_better=True)
    print("4. sign flip across seeds:              ", v3.verdict)
    if v3.verdict != SIGN_FLIP:
        fails.append("sign flip not caught: %s" % v3.verdict)

    # 5. UNSTABLE magnitude, all same sign -- the -16/-1 spread with the controls removed.
    v4 = replication_verdict([-16.0, -1.0, -5.0], lower_is_better=True)
    print("5. same sign, 16x magnitude spread:     ", v4.verdict)
    if v4.verdict != UNSTABLE:
        fails.append("unstable magnitude not caught: %s" % v4.verdict)

    # 6. higher-is-better metrics must work too (hit rates, not ranks).
    v5 = replication_verdict([0.12, 0.11, 0.13], controls={"SHUF": [0.001, 0.0, 0.002]},
                             lower_is_better=False)
    print("6. higher-is-better, genuine:           ", v5.verdict)
    if v5.verdict != REPLICATED:
        fails.append("higher_is_better genuine effect failed: %s" % v5.verdict)

    # 7. a paired-length mistake must RAISE, not silently mis-score.
    try:
        replication_verdict([-1.0, -2.0], controls={"X": [0.0]})
        fails.append("mismatched control length did not raise")
    except ValueError:
        print("7. mismatched control length raises:     OK")

    print()
    if fails:
        print("SELF-TEST FAIL:")
        for f in fails:
            print("  -", f)
        return 1
    print("SELF-TEST PASS -- caught the real artifact, refused the single seed, and did NOT "
          "flag a genuine effect.")
    return 0


if __name__ == "__main__":
    if "--self-test" in sys.argv:
        raise SystemExit(_self_test())
    print(__doc__)
    raise SystemExit(_self_test())
