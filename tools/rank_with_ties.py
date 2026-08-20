"""A rank helper that CANNOT hand you a number without telling you about the ties behind it.

WHY THIS EXISTS -- THREE FALSE RESULTS IN ONE DAY, ALL FROM ONE LINE OF ARITHMETIC (2026-08-20):

  1. **DG pattern separation at 1% sparsity** read median rank 18.0 against a co-occurrence floor of
     17.0 -- apparent parity with word-counting for the first time in the project, reproduced on two
     seeds. Random 10-sparse NOISE scored **14.0**. 89.4% of its similarities were exactly 0.0.
  2. **"We never pick an available correct synonym, 775 of 775."** A random picker also scores zero:
     expected 0.44 and 0.16 hits, P(zero | random) 0.64 and 0.85.
  3. **First-order co-occurrence** read 21.0 optimistic and **100.0 pessimistic** -- 92.2% of items
     had ties, 79.2% of every score column was exactly 0.0.

Every one is `1 + sum(scores > scores[target])` -- a STRICT inequality -- meeting a score
distribution with mass piled on one value. **Ties count as BEATEN, so the LESS a representation
knows, the better it scores.** Three in a day is a tooling problem, not three coincidences, and a
rule written in a document did not prevent the second and third: the rule was added to CLAUDE.md
that same morning and then not applied to the next two scripts.

**SO THE GUARD LIVES IN THE FUNCTION, NOT IN A HABIT.** `rank_with_ties` returns a RankResult, and
the tie count is a field on it -- there is no call signature that yields a bare rank.

    from tools.rank_with_ties import rank_with_ties, format_arms

    r = rank_with_ties(scores, target_idx, exclude=self_idx)
    r.optimistic   # ties counted as BEATEN     -- what the broken runs used
    r.pessimistic  # ties counted as BEATING
    r.midpoint     # the honest single number when ties are real
    r.n_tied       # how many competitors tie with the target
    r.suspicious   # True when ties are dense enough to make `optimistic` meaningless

HOW TO READ IT: if `optimistic` and `pessimistic` disagree materially, THE OPTIMISTIC NUMBER IS NOT
A RESULT. Report the midpoint, or fix the representation so the ties go away.
"""
from dataclasses import dataclass
from typing import Optional, Sequence

import numpy as np

SUSPICIOUS_TIE_FRACTION = 0.05      # >5% of the field tied with the target is enough to distort


@dataclass(frozen=True)
class RankResult:
    optimistic: int
    pessimistic: int
    midpoint: float
    n_tied: int
    n_candidates: int
    zero_fraction: float

    @property
    def suspicious(self) -> bool:
        """True when ties are dense enough that `optimistic` cannot be trusted on its own."""
        if self.n_candidates <= 0:
            return True
        return (self.n_tied / self.n_candidates) > SUSPICIOUS_TIE_FRACTION

    def __str__(self) -> str:
        s = "rank %d..%d (mid %.1f)" % (self.optimistic, self.pessimistic, self.midpoint)
        if self.suspicious:
            s += "  [TIES: %d of %d tie with the target -- the optimistic number is NOT a result]" \
                 % (self.n_tied, self.n_candidates)
        return s


def rank_with_ties(scores: Sequence[float], target: int,
                   exclude: Optional[int] = None) -> RankResult:
    """Rank of `target` among `scores`, under BOTH tie conventions, with the tie count.

    `exclude` drops one index from the comparison (usually the item's own row).
    """
    s = np.asarray(scores, dtype=np.float64).copy()
    if exclude is not None and 0 <= exclude < s.size and exclude != target:
        s[exclude] = -np.inf
    v = s[target]
    greater = int(np.sum(s > v))
    equal = int(np.sum(s == v)) - 1                  # exclude the target itself
    n = int(np.sum(np.isfinite(s)))
    return RankResult(optimistic=greater + 1,
                      pessimistic=greater + equal + 1,
                      midpoint=greater + 1 + equal / 2.0,
                      n_tied=max(0, equal),
                      n_candidates=max(1, n),
                      zero_fraction=float(np.mean(s == 0.0)))


def format_arms(results_by_arm: dict) -> str:
    """One table per arm, with the tie columns that make an optimistic number readable.

    `results_by_arm`: {arm_name: [RankResult, ...]}
    """
    lines = ["%-14s %9s %9s %9s | %9s %9s" %
             ("arm", "OPTIMIS", "MIDPOINT", "PESSIM", "med ties", "%items"),
             "-" * 68]
    for arm, rs in results_by_arm.items():
        if not rs:
            continue
        o = np.median([r.optimistic for r in rs])
        m = np.median([r.midpoint for r in rs])
        p = np.median([r.pessimistic for r in rs])
        t = np.median([r.n_tied for r in rs])
        frac = 100.0 * float(np.mean([r.suspicious for r in rs]))
        flag = "   <- OPTIMISTIC IS NOT A RESULT" if frac > 25.0 else ""
        lines.append("%-14s %9.1f %9.1f %9.1f | %9.1f %8.1f%%%s" % (arm, o, m, p, t, frac, flag))
    return "\n".join(lines)


def _self_test() -> int:
    """POSITIVE CONTROLS ON THE THREE REAL FAILURES, not on invented cases."""
    # 1. no ties -- both conventions must agree
    r = rank_with_ties([0.9, 0.5, 0.3], 0)
    assert (r.optimistic, r.pessimistic, r.n_tied) == (1, 1, 0), r
    assert not r.suspicious

    # 2. THE DG CASE: a sparse code where almost everything ties at 0 with the target.
    #    Optimistic says "rank 1", pessimistic says "last". This is the shape that produced a
    #    twenty-fold fake win.
    scores = [0.0] * 100 + [0.4]
    r = rank_with_ties(scores, 0)
    assert r.optimistic == 2, r
    assert r.pessimistic == 101, r
    assert r.suspicious, "dense ties must be flagged -- this is the DG failure"

    # 3. THE COOC1 CASE: most of the field is zero, the target is zero too.
    scores = np.zeros(200)
    scores[:10] = np.linspace(1, 2, 10)
    r = rank_with_ties(scores, 50)
    assert r.optimistic == 11 and r.pessimistic == 200, r
    assert r.suspicious

    # 4. a CLEAN sparse case must NOT be flagged, or the guard cries wolf and gets ignored
    r = rank_with_ties(list(np.linspace(0, 1, 300)), 100)
    assert not r.suspicious, "a tie-free field must not be flagged"

    # 5. exclude must not corrupt the target's own rank
    r = rank_with_ties([0.9, 0.8, 0.7], 1, exclude=0)
    assert r.optimistic == 1, r

    print("self-test: clean case agrees under both conventions")
    print("self-test: the DG shape (100 tied at 0) -> optimistic 2, pessimistic 101, FLAGGED")
    print("self-test: the COOC1 shape (190 of 200 zero) -> optimistic 11, pessimistic 200, FLAGGED")
    print("self-test: a tie-free field is NOT flagged (the guard does not cry wolf)")
    print("SELF-TEST PASS")
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(_self_test())
