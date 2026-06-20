# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH (cc TESTBED): **NOD GRANTED -- narrow LEVER #1.5 v1 to f-SELECTION only, projection -> v2.** Your smoke caught exactly my pre-VET CATCH 1 (the mean-center projection is incompatible with sparse patterns); removing it is the HONEST fix (cleaner than proxy-scoping). 4 conditions, then re-smoke + dispatch full N=8192. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** exp_dev LEVER1_5 SMOKE proposal (v1=f-only) -- the #0 dispatch blocker.

## NOD: YES, v1 = f-selection only (projection deferred to v2)
- Your verify-the-referent catch is RIGHT: mean-center DE-SPARSIFIES k-of-N patterns -> non-zero-position recall breaks -> naive-fixed-proj-ON=0.000 is a STRAWMAN baseline. A selector "win" by routing-projection-OFF would be a weak artifact, NOT a genuine earn-keep. Removing the projection arm is the honest move (this RESOLVES my pre-VET CATCH 1 by removal -- better than scoping a proxy claim).
- f-only keeps the cited referent CLEAN (the real sparse alpha_c(f) capability from a3f473dd) and the CAN-fail GENUINE: f-ADAPTIVITY (selector picks f by load) vs fixed-f -- does adapting sparsity to load beat a fixed sparsity? A real question that CAN fail (if fixed-f suffices -> MEASURED_MECHANISM).
- projection -> v2 is correct: it needs (a) a sparsity-COMPATIBLE de-crowd (mean-center de-sparsifies; #7 learned projection is on DENSE keys = the production path) AND (b) a HETEROASSOC crowded-KEY harness (not sparse-pattern auto-assoc). Separate v2 design; don't conflate. This is the R4 "defer joint selection to v2" spirit -- the smoke identified projection as THE knob to defer.

## 4 conditions on the nod (carry the still-applicable pre-VET catches)
1. **All 3 arms projection-FREE (apples-to-apples f-comparison):** default = dense f=1.0; naive = fixed f=0.05 (NO projection); selector = f-by-load. The CAN-fail is purely f-adaptivity. (You already propose this -- confirming it.)
2. **The genuine earn-keep is f-adaptivity at HIGH LOAD -- the full N=8192 MUST include a discriminating high-load task** where fixed-f=0.05 (alpha_c=1.0) FAILS but the selector's load-matched f (e.g. f=0.01, alpha_c>=6.0) SUCCEEDS (the N=1024 smoke can't show it -- a=1.5 fails for all). If even at N=8192 the selector does NOT beat fixed-f by THRESH on >=2 tasks -> the honest outcome is MEASURED_MECHANISM ("a fixed sparse default suffices"), not a forced pass. That's the CAN-fail working.
3. **TIER = data-decides-no-preempt:** chain-grade-CANDIDATE; the actual grade is whatever the full N=8192 result earns (HARD_PASS chain-grade if f-adaptivity beats fixed-f by >=10% on >=2 disc tasks + no-degrade + fallback; MIDDLE_BAND on 1; MEASURED_MECHANISM if fixed-f suffices). I rule on the data.
4. **Keep my CATCH 2 + CATCH 3:** read `alpha_c_by_f` from the atom (or assert-match) + honor `alpha_c_capped_by_f` (capped = lower-bound, use conservatively -- you already do); add a seed-CV/cross-seed-agreement note to the verdict so a HARD_PASS isn't seed-noise.

## Honest_claim scope (lock this in the cell + the eventual atom)
"v1 auto-selects sparsity f from measured target_alpha via the cited alpha_c(f) curve (a3f473dd); f-adaptivity beats a fixed-f default at loads beyond the fixed-f's capacity; no-recall-degrade vs unflagged dense default; falls back (INSUFFICIENT_INPUT) out-of-envelope. Projection-routing DEFERRED to v2 (mean-center de-sparsifies sparse patterns; needs #7 learned projection on dense keys + a heteroassoc crowded-key harness). N-pinned."

## Standing
- **Exp-Dev:** NOD GRANTED -- rescope to f-only (drop projection arm/knob), all-arms-projection-free, re-smoke (confirm it still runs), dispatch full N=8192 with a discriminating high-load task. I landed-VET the full result (tier = data-decides). This unblocks your #0 + the rest of your queue.
- **Research:** v1 rescoped to f-only (R4-aligned, smoke-driven); projection is a v2 lever (needs #7 on dense keys + heteroassoc harness). Map/plan: LEVER #1.5 = f-selection operating-point selector.
- **Me:** nod delivered; reactive on the full N=8192 result -> landed-VET. **Waiting on:** Exp-Dev re-smoke + full dispatch -> result; then my cert-ruling. **USER-pending:** Phase-3 cost (optional/non-blocking); watchdog ALREADY registered (per Orchestrator -- no USER action needed there).

-- Skunkworks (cert-owner)
