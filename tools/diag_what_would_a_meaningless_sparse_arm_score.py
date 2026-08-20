"""THE DECISIVE REFUTATION, AND IT NEEDS NO CORPUS: what does a MEANINGLESS sparse code score?

CLAUDE.md carries the rule already: *"ASK WHAT SCORE A BROKEN ARM WOULD GET... before trusting a
winning arm, construct the EMPTY version of it and check that it LOSES."* This is that rule with the
sign flipped, because the suspect arm is not empty but SPARSE: **construct the MEANINGLESS version
and check whether it WINS.** If random noise at 1% sparsity reproduces the "win", the win is a
property of the METRIC at that sparsity and carries no information about pattern separation.

WHAT IS BEING REFUTED. `dg_separate(..., sparsity=0.01, expand_dim=1024)` scored median rank 18.0
(seed 7) and 15.0 (seed 101) where the shipped representation scores 52.5 and 35.5, against
co-occurrence floors of 17.0 and 11.0 -- i.e. it appeared to reach parity with word-counting for the
first time in the project.

THE ARITHMETIC THAT MAKES ME EXPECT AN ARTIFACT, STATED BEFORE THE RUN:
`k = round(0.01 * 1024) = 10` non-zero components. Two independent 10-subsets of 1024 slots are
DISJOINT with probability about `(1 - 10/1024)^10 ~= 0.906`. So roughly **90% of candidate/query
pairs have a dot product of EXACTLY 0.0**. The rank statistic is `1 + #{sims > sims[target]}` -- a
STRICT inequality -- so when the target also scores 0.0 (the common case), **every one of those ~90%
ties counts as BEATEN**, and the target's rank is set only by the ~10% that overlap at all.
With ~286 candidates that predicts a median rank in the tens **for a code containing no information
whatsoever**.

THREE ARMS, none of which knows anything about language:
  NOISE_SPARSE   every profile AND query an independent random 10-sparse unit vector
  NOISE_DENSE    the same, but dense -- the control that shows SPARSITY is the operative variable
  CONSTANT       every profile identical -> maximal ties, the degenerate extreme
The candidate count and probe count are matched to the real run so the numbers are comparable.

PRE-COMMITTED READINGS:
  NOISE_SPARSE lands in the same range as DG@0.01 (~15-20) -> **THE WIN IS AN ARTIFACT OF THE METRIC
      AT THAT SPARSITY AND MUST BE WITHDRAWN.** Nothing about pattern separation is demonstrated.
  NOISE_SPARSE stays near chance (~n/2 = ~143) -> the metric is sound at this sparsity and DG@0.01's
      result is REAL, which would make it the most important finding of the effort.
"""
import numpy as np

N_CAND, N_PROBE, EXPAND = 286, 300, 1024
SPARSITIES = (0.01, 0.02, 0.05, 0.10, 0.25)
rng = np.random.default_rng(20260820)


def sparse_unit(k):
    v = np.zeros(EXPAND)
    idx = rng.choice(EXPAND, size=k, replace=False)
    v[idx] = rng.normal(size=k)
    n = np.linalg.norm(v)
    return v / n if n > 0 else v


def rank_stats(U, Q, tgt):
    """Return (optimistic, pessimistic) median rank. Optimistic counts ties as BEATEN, which is
    exactly what the sweep used."""
    S = Q @ U.T
    opt, pes = [], []
    for i in range(len(Q)):
        row, t = S[i], S[i][tgt[i]]
        gt = int(np.sum(row > t))
        eq = int(np.sum(row == t)) - 1
        opt.append(gt + 1)
        pes.append(gt + eq + 1)
    return float(np.median(opt)), float(np.median(pes))


def _selftest_metric_detects_real_signal():
    """POSITIVE CONTROL on the harness itself: when the query IS the target's profile, rank must be
    1. Without this, 'noise scores well' could mean the harness is broken rather than the metric."""
    U = np.stack([sparse_unit(50) for _ in range(60)])
    tgt = list(range(60))
    o, p = rank_stats(U, U.copy(), tgt)
    assert o == 1.0 and p == 1.0, "harness cannot score a perfect match: opt=%s pes=%s" % (o, p)
    print("selftest harness: query==profile -> rank 1.0 both conventions OK", flush=True)


_selftest_metric_detects_real_signal()

print("\n%d candidates, %d probes, expand_dim %d" % (N_CAND, N_PROBE, EXPAND))
print("chance (no information, no ties) would be ~n/2 = %.1f\n" % (N_CAND / 2.0))
print("%-16s %6s | %10s %10s | %s" % ("arm", "k", "OPTIMIST", "PESSIM", "note"))
print("-" * 78)

for sp in SPARSITIES:
    k = max(1, round(sp * EXPAND))
    U = np.stack([sparse_unit(k) for _ in range(N_CAND)])
    tgt = list(rng.integers(0, N_CAND, size=N_PROBE))
    Q = np.stack([sparse_unit(k) for _ in range(N_PROBE)])   # queries UNRELATED to their targets
    o, p = rank_stats(U, Q, tgt)
    disjoint = (1 - k / EXPAND) ** k
    print("%-16s %6d | %10.1f %10.1f | ~%.0f%% of pairs share no support"
          % ("NOISE_SPARSE", k, o, p, 100 * disjoint))

Ud = rng.normal(size=(N_CAND, EXPAND))
Ud /= np.linalg.norm(Ud, axis=1, keepdims=True)
Qd = rng.normal(size=(N_PROBE, EXPAND))
Qd /= np.linalg.norm(Qd, axis=1, keepdims=True)
tgt = list(rng.integers(0, N_CAND, size=N_PROBE))
o, p = rank_stats(Ud, Qd, tgt)
print("%-16s %6d | %10.1f %10.1f | the control: dense noise, no ties" % ("NOISE_DENSE", EXPAND, o, p))

Uc = np.tile(sparse_unit(10), (N_CAND, 1))
o, p = rank_stats(Uc, Qd, tgt)
print("%-16s %6d | %10.1f %10.1f | degenerate extreme: every profile identical"
      % ("CONSTANT", 10, o, p))

print("\n" + "=" * 78)
print("OBSERVED IN THE REAL RUN:  DG@0.01 seed 7 = 18.0 (floor 17.0) | seed 101 = 15.0 (floor 11.0)")
print("                           RAW            = 52.5              |            = 35.5")
print("=" * 78)
