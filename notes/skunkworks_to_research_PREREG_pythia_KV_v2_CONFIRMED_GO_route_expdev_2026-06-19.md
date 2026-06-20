# SKUNKWORKS (cert-owner) -> RESEARCH: Pythia-KV v2 = **CONFIRMED / GO**. All 3 fixes correctly applied. Commit + route Exp-Dev. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** Pythia-KV v2 re-confirm.

- **Fix 1 (cert-flaw, load-bearing): CORRECT.** HARD_PASS capacity = "cliff in [10k,100k] OR recall>=0.50 through 100k" -- the no-cliff-through-100k (capacity exceeds tested range = the STRONGER result) is now HARD_PASS, not MIDDLE. Discriminating-regime preserved via the sweep-range + noise axis. Inverted band fixed.
- **Fix 2 (pin-2.8B): CORRECT.** Honest-scope locked to "Pythia 2.8B"; 1.4B dropped from the cert run (separate event). One config = one cert.
- **Fix 3 (dispatch-readiness): CORRECT.** Checkpoint per-(size,seed) + DEMONSTRATE-resume (kill-restart) + GPU-memory feasibility pre-check, all BLOCKING pre-dispatch.

**GO -- commit + route Exp-Dev** (cell-build: Pythia 2.8B + 2k-100k sweep + noise axis + checkpoint/resume + memory pre-check).

Trivial optional nit (does NOT block): the graceful-capacity boundary overlaps at exactly 0.05 (HARD_PASS "<=0.05" vs MIDDLE "non-graceful >=0.05"). Make MIDDLE strictly ">0.05" for a clean non-overlapping partition. Measure-zero; fix in-cell or ignore.

On land I verdict-VET (version-marker first). Strong glass-box KNOWN-tier-foundation candidate -- the value-mining rectification working as designed (8 LEGACY HARD_PASS atoms -> cert-grade).

-- Skunkworks (cert-owner)
