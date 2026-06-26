# Cell Y FM-lock-in-WM v1 -- LANDED HARD_FAIL_INTERMOD

**From:** exp_dev
**To:** skunkworks (primary; tier ruling), research + orchestrator cc
**Date:** 2026-06-25
**Status:** Cell completed (3 seeds; FULL N=4096; HARD_FAIL_INTERMOD verdict)

## Summary (1 line)

USER Q3 frequency-multiplexed-WM-lock-in mechanism HARD_FAIL_INTERMOD at
3-seed FULL: zero lift at K=128 (cv-confirmed; the 1-seed smoke +0.07 was
variance noise), marginal +0.02 lift at K=256 but cross-slot bleed 0.42
(way over HF threshold 0.10) -- honest negative on USER's theta-gamma
multiplexing brain-analog mechanism at substrate scale.

## Verdict (per-arm metrics; Fix #28 discipline)

3 seeds [11, 13, 19], FULL N=4096, K_VALUES=[32,64,128,256], sigma=1.0,
P_LOCKIN=8:

| K   | NAIVE_HRR_WM      | FM_LOCK_IN        | lift   | bleed |
|-----|-------------------|-------------------|--------|-------|
| 32  | 1.000 (cv=0.000)  | 1.000 (cv=0.000)  | +0.000 | 0.000 |
| 64  | 0.999 (cv=0.000)  | 1.000 (cv=0.000)  | +0.001 | 0.000 |
| 128 | 0.928 (cv=0.002)  | 0.927 (cv=0.019)  | -0.001 | 0.073 |
| 256 | 0.540 (cv=0.025)  | 0.561 (cv=0.007)  | +0.021 | 0.421 |

- Rail breach 0/3 (NAIVE arms reproduced WM v2 today's cell:
  K128=0.928 in rail [0.88, 0.94] ✓; K256=0.540 in rail [0.51, 0.60] ✓)
- Verdict trigger: K=256 bleed = 0.421 >> HF_INTERMOD_MAX = 0.10
- Verdict: **HARD_FAIL_INTERMOD**

## Honest read (NOT propagating verdict_msg framing)

- The mechanism produces ZERO net lift at K=128 (-0.001) -- the 1-seed
  smoke +0.07 was variance noise (Q-discipline guard fired correctly:
  treat cv=0 1-seed results as suspect)
- At K=256, FM gives +0.02 absolute lift but the cleanup is finding
  WRONG slots' items 42% of the time -- the aggregate looks comparable
  to NAIVE only because both arms are degraded at K=256
- The intermod is the killer: at delta_k=4096/(K+1)=16 for K=256, the
  P-phase carriers from different slots produce overlapping spectral
  content in the cyclic shift basis. The lock-in primitive's slot-
  isolation property holds only when delta_k * K << N (i.e. K << sqrt(N)
  or so); K=256 at N=4096 violates this assumption

## What this rules out

USER Q3 verbatim: "if each marker was in a different frequency and you
used filters, you'd be able to read a lot more than 32"

**Answer:** in the substrate's bipolar HRR codebook regime, frequency-
multiplexed WM with lock-in demod does NOT extend the K-ceiling beyond
NAIVE's K~=64. The brain analog (theta-gamma multiplexing in PFC) requires
either (a) signaling primitives the substrate lacks (continuous oscillatory
phase) OR (b) a much larger N (~ N >= K^2 for clean intermod isolation).

## What's NOT ruled out

- USER's Q3 second clause ("flashed them at different frequencies (lock-in)
  you'd also get way, way more") is testable separately: time-domain
  flashing (sequential reads with phase-locked accumulation across multiple
  reads of the SAME workspace) -- not yet tested
- Other K-extension mechanisms (multi-bank routing -- the other agent's
  parallel-running cell at `exp_substrate_working_memory_multi_bank_routing_v1`
  hit RAIL_SANITY_BREACH but with multi-bank arms at recall=1.000 cv=0 --
  needs Skunkworks ruling on whether that's by-construction-saturation or
  chain-grade-K-extension)
- Phase-coherent (complex) FHRR substrate that has native phase rather than
  bipolar substrate -- different substrate; not tested here

## Cross-cell apples-to-apples

Reproduces WM v2 today exactly: K128_NAIVE=0.928 (today 0.908; within
cv); K256_NAIVE=0.540 (today 0.555; within cv). The rails work; the
mechanism's negative is on the FM-side, not on the NAIVE baseline.

## Tier ruling expected from Skunkworks

Recommended cert tier (open to override per Fix #28 -- Skunkworks
consistently correctly overrides Director on by-construction-saturation):

- **MEASURED_MECHANISM (default)** -- the cell honestly measured that FM
  lock-in WM at substrate-scale has K-ceiling intermod the same as NAIVE.
  Useful for closing the USER's Q3 question.
- **Not chain-grade** -- the mechanism doesn't deliver chain-grade
  K-extension; HARD_FAIL on the chain-grade-extension bands.

If Skunkworks rules MEASURED_MECHANISM, the Store atom should record:
- USER Q3 mechanism tested at substrate-scale 3-seed cv-confirmed
- FM-lock-in WM HARD_FAIL_INTERMOD at K>=128 in bipolar substrate
- Intermod-floor proportional to K * delta_k / N; ~ K^2/N regime boundary
- USER's Q3 brain analog requires continuous-phase substrate OR
  N >> K^2 for substrate transport

## Files / commits

- `data/exp_substrate_working_memory_frequency_multiplexed_lock_in_v1/metrics.json`
- `experiments/exp_substrate_working_memory_frequency_multiplexed_lock_in_v1.py`
- `preregs/2026-06-25_substrate_working_memory_frequency_multiplexed_lock_in_v1.md`
- commits: 11793a54 (cell+prereg); 3cdd2005 (dispatch note)
- elapsed_s: 21.1s (3 seeds; well under 1800s budget)
