# Strategic Synthesis — 2026-05-18 GPU session

## Where we landed

**Best: 2.4963 bits/char** on the 38KB byte-level corpus. Gap to tiny-transformer
ceiling (2.39): **0.106 bits**. Down from 0.45 at session start.

74% of the original gap closed. The remaining ~10% is now believed to be a
structural property of the FHRR + random-IID + Hebbian-delta-rule basin at
this data scale.

## What worked, what didn't

**5 brain-inspired experiments tested:**

| Experiment | Hypothesis | Result | Verdict |
|---|---|---|---|
| BR1 dendritic NL (magnitude_relu) | nonlinear neuron readout | 2.4994 | win, −0.02 |
| BR5 grid-cell positions | structured positional code | 2.5094 | slight hurt |
| BR3 climbing-fiber error matrix | sparse supervised side-channel | 2.5008 | neutral |
| BR4 PFC attractor (persistent state) | working-memory analog | 2.7841 | hurts, −0.28 |
| BR2 DG sparse projector | pre-pool decorrelation | 2.945 | broken (normalization) |

Only one helped, and it was a single-line readout change, not a new module.

**MX10 parallel tempering K=8 + RSB diagnosis:**

PT done correctly (23% swap acceptance — Earl-Deem optimal). Best replica
2.4963, ensemble 2.6300, best-replica gain over single-config baseline =
0.003 bits (FP-noise level).

P(q) overlap analysis:
- Full off-diagonal: mean 0.715, std 0.254 (looked wide)
- **Cold replicas only (decay ≤ 3e-4): mean 0.9987, std 0.0009 — essentially identical**
- Hot replicas: noisy (haven't converged)

The four cold replicas converged to the same W matrix. **This is NOT FRSB
clustering — it's a single-basin landscape.** Different starting points and
different decay schedules all reach the same solution.

## The architectural conclusion

The 0.10-bit residual gap is NOT a sampling-dynamics problem (PT can't help,
no clusters to escape) and NOT a missing-module problem (federated additions
mostly failed). It is an architectural property of:

- Random IID FHRR atoms (capacity / SNR ceiling per Frady-Kleyko-Sommer)
- Hebbian delta-rule learning (basin geometry)
- Single-W readout (with magnitude_relu)
- 38KB corpus (data-determined landscape)

All paths through this configuration converge to the same W and the same
2.50 bpc floor.

## What experiments remain meaningful

Three honest strategic options for next session:

**Option A — Functional capability testing.** Stop chasing perplexity on
this one task. Test what our system can DO that transformers can't or do
differently:
- Continual learning: train A, then B, test A retention (Hebbian should win)
- Few-shot in-context learning: pool-based pattern completion at inference
- Sample efficiency: bits/char vs corpus size N at small N
- Compositional generalization: held-out byte-bigram combinations
- Catastrophic forgetting test: explicit measurement

Cost: each is a 1-3 hour experiment. Total: 1-2 days of GPU work.
Expected outcome: empirical claims about functional differentiation, not
perplexity wins.

**Option B — Scale & tune.** Close more of the gap on standard metric:
- 1-10 MB corpus (does the floor dissolve?)
- BSC substrate (different landscape geometry, also hardware-relevant)
- Multi-seed runs for variance on current best
- Population annealing if BSC also shows clustering

Cost: 1-2 days of GPU work. Expected outcome: another 0.05-0.10 bpc, or a
clear empirical scaling story (the 38KB ceiling holds at scale, or it doesn't).

**Option C — Continue federated brain exploration.** More untested bio-modules:
- BR6 sleep replay (offline pool replay)
- BR2 retry with fixed normalization
- BR13 sparse k-WTA atoms
- BR15 tuning-curve byte atoms

Cost: 1 day. Expected outcome: more null/marginal results given the basin
finding. Lowest expected payoff.

## Honest recommendation

Option A is the most informative use of further compute. The perplexity
gap on this task is small, the basin is unique, and incremental tuning
yields diminishing returns. The bigger open question is whether this
architecture has *qualitatively different capabilities* than transformers
on tasks neither perplexity nor the standard benchmark suite captures.

Option B is the safe scientific completion (writeup-ready empirical
scaling story).

Option C has the lowest expected payoff given what we've already learned.

## What we've learned this session (compressed)

- Multi-epoch + pool + decay compounds; +0.32 bpc improvement from base
- Single architectural addition (magnitude_relu); +0.02 bpc
- Federated bio-inspired modules: mostly null
- Parallel tempering: confirms single-basin landscape
- The 38KB / FHRR / N=4096 / random-IID / Hebbian-delta basin has a real
  floor at ~2.50 bpc, reachable from many starting points
- We don't yet know: does the floor scale (Option B)? does this matter for
  capability differentiation (Option A)?
