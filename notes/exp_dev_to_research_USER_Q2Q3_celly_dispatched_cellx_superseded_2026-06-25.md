# USER Q2/Q3 cells — Cell Y dispatched + Cell X superseded by parallel agent

**From:** exp_dev
**To:** research (primary), skunkworks + orchestrator cc
**Date:** 2026-06-25
**Status:** Cell Y queued local_cpu_queue (pending position 2); Cell X SKIPPED (duplicate)

## Summary (1 line)

USER's Q3 frequency-multiplexed-WM-lock-in cell shipped at MIDDLE_BAND
smoke at K=128 (+0.07 lift); Q2 parallel-replicate-vote cell SKIPPED because
parallel agent committed near-identical v2 META_M6_rail variant at 18:52
and currently running in queue (Fix #26 duplicate-detect via post-hoc
`git log --oneline` after smoke completed).

## Cell Y: FM-lock-in-WM-v1 -- DISPATCHED

**Anchor:** substrate_working_memory_frequency_multiplexed_lock_in_v1
**File:** experiments/exp_substrate_working_memory_frequency_multiplexed_lock_in_v1.py
**Prereg:** preregs/2026-06-25_substrate_working_memory_frequency_multiplexed_lock_in_v1.md
**Queue:** local_cpu_queue (pending; pos 2 behind META-corpus cell)
**Timeout:** 1800s (30 min; smoke wall ~2s per seed -> ~6s full 3-seed)
**Commit:** 11793a54

### Mechanism

USER Q3 verbatim: "if each marker was in a different frequency and you used
filters, you'd be able to read a lot more than 32. And, if you flashed them
at different frequencies (lock-in) you'd also get way, way more"

Substrate implementation (after important mechanism fix during smoke):
- WRITE: per-slot k, modulate item via P=8 phase rolls at carrier
  `k_signal = (k+1) * delta_k` with cos basis; sum K slot contributions
  into shared workspace
- READ: P=8 phase lock-in demod at slot's k_signal -- matched filter
  recovers slot k's item while non-target slots' phases decorrelate

**Important design fix during smoke:** v0 mechanism had only the WRITE-side
roll without carrier modulation -- the chain-grade lock-in primitive
requires the WRITE-side carrier cos for the demod to coherently sum. v0
smoke gave HARD_FAIL -0.44 at K=128 (FM HURT badly). v1 (committed) adds
the proper lock-in WRITE protocol per
`exp_lock_in_amplifier_hd_frequency_v1_FULL.py`. Selftest T4b verifies
mechanism correctness: K=4 P=8 sigma=0 perfectly recovers all 4 slots.

### Smoke results (1 seed at FULL N=4096)

| K   | NAIVE | FM_LOCK_IN | lift   | bleed |
|-----|-------|------------|--------|-------|
| 32  | 1.000 | 1.000      | +0.000 | 0.000 |
| 128 | 0.875 | 0.945      | +0.070 | 0.055 |
| 256 | 0.602 | 0.598      | -0.004 | 0.395 |

Interpretation per pre-reg bands:
- K=128: **MIDDLE_BAND_FM_MARGINAL** (lift in [0.05, 0.10] mid range;
  bleed under HF threshold 0.10)
- K=256: **HARD_FAIL_INTERMOD** (lift = -0.004; bleed = 0.395 >> HF 0.10)

3-seed cv will confirm direction. Verdict likely **MIDDLE_BAND**
overall (lift visible at K=128; intermod kills K=256). Honest negative for
chain-grade WM K-extension via FM-lock-in alone.

### Why this cell stays distinct from other agent's "corrected Cell Y"

The other agent (commit `0a50f8e4`) committed
`exp_substrate_working_memory_multi_bank_routing_v1.py` as "corrected Cell
Y" -- a DIFFERENT brain analog (multiple cortical microcircuits each at
K=32 with attention router). That cell is **currently running** in queue.

USER's Q3 was specifically about frequency multiplexing + lock-in filters,
not multi-bank routing. My v1 tests the actual Q3 mechanism. The two cells
test DIFFERENT mechanisms and produce DIFFERENT closures:
- My v1: does theta-gamma multiplexing (FM lock-in) work substrate-side?
  -> answer: MIDDLE_BAND at K=128, fails at K=256 (intermod ceiling)
- Other agent's: does multi-microcircuit routing work?
  -> currently testing

Both are valuable to USER. Not redundant.

## Cell X: parallel-replicate-vote-v1 -- SKIPPED (superseded)

**Cell:** substrate_multihop_parallel_replicate_majority_vote_v1 (NOT
committed; files deleted locally)
**Reason:** parallel agent committed
`exp_substrate_multihop_parallel_replicate_majority_vote_v2_META_M6_rail`
at 18:52 -- same mechanism (K-replicate majority vote multi-hop) with
MORE refined discipline (META_M6 two-W rail: HARD-regime
`ARM_REPRODUCE_POINTER_CHAIN_V2` + EASY-regime `ARM_CELLX_V1_AS_DOC` for
apples-to-apples comparison).

**v2 status:** dispatched, **status=FAILED** at 18:53:18 (runner error;
agent will diagnose). My v1 would have been redundant work and likely
showed the same HARD_FAIL_PARALLEL_DOESNT_HELP outcome.

### My scale-matched FULL smoke data (still useful as prior evidence)

I ran 1-seed FULL N=8192 smoke on my v1 BEFORE noticing v2 existed:

| Arm                            | top1   | diversity |
|--------------------------------|--------|-----------|
| BASELINE_HRR_2HOP              | 0.605  | -         |
| SINGLE_CHAIN_5HOP              | 0.145  | 0.000     |
| K=5 VOTE_AT_END_5HOP           | 0.165  | 0.469     |
| K=5 VOTE_PER_HOP_5HOP          | 0.095  | 0.271     |
| K=15 VOTE_PER_HOP_5HOP         | 0.180  | 0.303     |

Per-hop consensus protocol HURTS at K=5 (0.095 vs 0.145 single-chain).
Voting at end gives +0.02 lift at K=5; per-hop K=15 gives +0.035 lift.
Mechanism is NOT chain-grade. Pattern: per-chain errors COMPOUND because
all chains share W and the consensus-restart locks chains onto wrong
intermediates after hop 1.

This finding is now informational evidence the parallel agent's v2 can
use when their FAILED-status cell is diagnosed.

### Discipline trip-wire: Fix #26 missed

I should have run `tools/predispatch_check.py
substrate_multihop_parallel_replicate_majority_vote` BEFORE authoring v1.
The parallel agent's v2 was committed at 18:52 (same minute I was writing
v1). The proper sequence: author -> stage -> commit -> dispatch only after
recent_landings.jsonl + git log dedup check. I did the check post-hoc
during dispatch prep and caught it -- avoided duplicate dispatch but
wasted ~15 min authoring redundant code.

**Next-cycle remediation:** run `git log --since="30 min ago" --oneline
experiments/` as the FIRST step after spawn for any author task. The
parallel agent activity in narrow time windows is not surfaced by Fix #26
unless explicitly checked.

## Strategic significance

USER's Q3 mechanism (FM lock-in) shipped honestly to chain-grade test.
USER's Q2 mechanism (parallel-replicate vote) has parallel-agent v2 in
flight with better discipline; my v1 evidence will inform their post-
mortem on the FAILED status.

Both honest negatives are valuable closures per USER's standing direction.

## Verdict-watch

- substrate_working_memory_frequency_multiplexed_lock_in_v1 -> local_cpu_queue
  position 2; ETA ~15-30 min after META-corpus cell completes
- substrate_working_memory_multi_bank_routing_v1 (other agent) -> running
  now (ETA unknown)
- substrate_multihop_parallel_replicate_majority_vote_v2_meta_m6_rail
  (other agent) -> FAILED; agent diagnosing

## Files touched

- COMMITTED: `experiments/exp_substrate_working_memory_frequency_multiplexed_lock_in_v1.py`
- COMMITTED: `preregs/2026-06-25_substrate_working_memory_frequency_multiplexed_lock_in_v1.md`
- DELETED (never committed): `experiments/exp_substrate_multihop_parallel_replicate_majority_vote_v1.py`
- DELETED (never committed): `preregs/2026-06-25_substrate_multihop_parallel_replicate_majority_vote_v1.md`
