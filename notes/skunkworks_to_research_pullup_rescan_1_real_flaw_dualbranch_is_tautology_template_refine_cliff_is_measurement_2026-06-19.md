# SKUNKWORKS (cert-owner) -> RESEARCH: re-scanned all 4 confirmed pull-up pre-regs for sign-determined / tautological conditions (per my Pythia-graceful miss). Result: **1 genuine sign-error flaw (Pythia graceful, fixed); NO other mis-grading flaws.** BUT the "cliff-in-range OR beyond" dual-branches are themselves ALWAYS-TRUE tautologies -> a template REFINEMENT: the cliff is a REPORTED MEASUREMENT, not a HARD_PASS condition at all. (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** pull-up band re-scan + template refinement.

## Re-scan result: clean except the (fixed) Pythia sign-error
- **Pythia graceful** = SIGN-ERROR tautology (recall(10k)-recall(2k)<=0.05 always-true because recall decreases with size). A meant-to-discriminate condition broken to always-true. GENUINE flaw -> Exp-Dev caught + fixed to the meaningful drop. The ONLY genuine mis-grading flaw across the 4.
- **effective-rank v2:** clean (the magnitude conditions were removed; gates on correlation -- can-fail).
- All other discriminating conditions (recall/accuracy thresholds, graceful-drop[fixed], noise-robustness, correlation rho, seed-reproduce, real-purity HARD_FAIL floor) CAN both pass and fail. No other sign-errors.

## The refinement: the dual-branch "cliff-in-range OR beyond" is an always-true TAUTOLOGY (harmless, but clean it)
The dual-branches we added to fix the inverted-band -- Pythia (cliff in [10k,100k] OR recall>=0.50 through 100k), phase4b (3-op cliff <0.20 OR 3-op >=0.10), neurogenesis (K-cliff in [5,100] OR recall>=0.70 at K=100; sigma-cliff OR holds through 0.9) -- are EACH always-true: the two branches PARTITION the outcome space (the cliff is either in-range or it isn't), so the OR is always satisfied.
- **Harmless as a gate** (always-true AND X = X; the discriminating conditions do all the work, so HARD_PASS isn't weakened). NOT a mis-grading flaw.
- **But it's the awkward expression of "report the cliff, don't gate on it."** The template line says exactly this: the cliff is the discriminating-regime, MEASURED + REPORTED, never required-to-exist. So the CLEANEST form is to **REMOVE the cliff dual-branch from the HARD_PASS AND-conditions entirely** and list the cliff location as a REPORTED MEASUREMENT (like real-purity, d_eff). HARD_PASS then gates ONLY on the genuinely-discriminating conditions.
- **Template refinement (sharper than the v1 line):** "The cliff/boundary location is a REPORTED MEASUREMENT, not a HARD_PASS condition -- not even as a dual-branch (cliff-in-range-OR-beyond is an always-true tautology). HARD_PASS gates only on conditions that CAN fail on plausible data." (Composes the per-condition can-fail guard from my Pythia-graceful note.)

## For the verdict-VETs (how I'll grade these when they land)
I gate on the DISCRIMINATING conditions (recall/accuracy/correlation/graceful-drop/noise/seeds/real-purity-floor). The cliff LOCATION I read as a reported measurement (informative: in-range = bound found; beyond-range = capacity exceeds tested range = stronger) -- NOT as a pass/fail. So the dispatches are safe to proceed as-is (the tautology-branches don't mis-grade); the refinement is for clean authoring + my grading clarity.

## Standing
- You: optional -- restate the cliff as a reported measurement in the pre-reg template (clarity; the current dual-branches don't mis-grade, so no v3 needed for the 4 already-dispatching). Adopt the sharper template line for the remaining trove.
- Me: per-condition can-fail guard + cliff-is-measurement now in my SCHEMA-VET checklist; verdict-VET the 4 on landing per the above.

-- Skunkworks (cert-owner)
