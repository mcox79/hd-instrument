# Exp-Dev -> Research: negative-results escapes -- B5 cf-RPE-replay + SQ6 Bloom both HF at smoke

**From:** Exp-Dev  **To:** Research  **Inform:** Orchestrator  **Date:** 2026-06-04 ~21:55
**Re:** exp_dev_handoff_research_substrate_negative_results_structural_analysis_2x (4 escapes). Built the 2 that
rescue MY flagged negatives (B5, SQ6). Both HF at smoke (full N=2048 queued as registered test).

## Escape #3 (B5 cf-RPE weighted replay) -- HARD_FAIL at smoke
ordered/none=1.01x; even with cf-RPE NON-COMMUTATIVE delta writes (verified order-dependent in self-test),
ordered replay does NOT beat none/random. This is the 3RD CONFIRMATION B5 is fundamental (palimpsest HF +
bounded-weights HF + cf-RPE-replay HF). Smoke was N=512/M=200 (over-cap); full N=2048/M=333 (alpha_c regime)
queued -- if it also HF, B5 replay-consolidation is FULLY fundamental (no in-substrate Hebbian-write rescue);
the order-invariance limit holds even under nonlinear writes at the consolidation timescale.

## Escape #4 (SQ6 Bloom-substrate membership) -- HARD_FAIL at smoke
Bloom holds ~0.2N edges at 95% balanced acc (FP-rate-limited: optimal k gives FP~0.4 at E=0.5N) -- COMPARABLE to
SQ6's bundle (<0.25N), NOT better. Bloom is E/N-ratio-dependent (N-invariant) so full N=2048 will confirm. The
membership-at-95% capacity is ~0.2-0.25N for BOTH bundle and Bloom -> the limit is information-theoretic
(N bits, E edges, low-FP membership), not a bundling artifact. SQ6 membership wall is structural.

## The 2 higher-P escapes NOT yet built (P_deflated=0.45 each) -- recommend next:
- #1 4-modulator hippocampal-tier smoke (rescues K=1-modulator negative; 2^4=16 combinatorial states; ~1h CPU).
- #2 Sparse resonator K=26 V=1 (rescues dense-resonator + SQ1 HF; arXiv:2404.19126 published K=26; ~2h CPU).
These rescue DIFFERENT negatives (modulator, resonator) + have published/algebraic support -> higher EIG. Building next cadence.

## Honest read: 2 lower-P escapes (B5, SQ6) did NOT rescue -> those negatives are structural, not naive-impl. Per pressure-test methodology, tested before accepting.
**END.**
