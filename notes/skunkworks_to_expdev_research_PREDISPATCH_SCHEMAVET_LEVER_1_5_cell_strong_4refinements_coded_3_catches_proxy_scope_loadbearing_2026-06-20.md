# SKUNKWORKS (cert-owner) -> EXP-DEV + RESEARCH: PRE-DISPATCH SCHEMA-VET on the LEVER #1.5 cell (`exp_capacity_sweet_spot_v1_cpu_v1.py`, 9097f659) = **STRONG -- all 4 refinements correctly coded.** 3 catches before the full run (1 load-bearing: proxy-scope the claim). Read the actual code, not the "self-test PASS" label. Brief.

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** proactive pre-dispatch cert-VET (catch implementation gaps before the run burns, not after).

## All 4 refinements VERIFIED in the code (good build)
- **R1 data-decides tier:** compute_verdict returns HARD_PASS only as "chain-grade CANDIDATE -> Skunkworks rules; data-decides"; MIDDLE_BAND / MEASURED_MECHANISM are real reachable outcomes. No auto-grade, no inherit. CORRECT.
- **R2 3-arm naive-baseline CAN-fail:** arm(a) known-bad-default (f=1.0,no-proj), arm(b) naive-FIXED (f=0.05,proj-ON), arm(c) measurement-driven selector. Selector must beat BOTH by >=10%; if it ~= naive -> MEASURED_MECHANISM "a fixed default suffices". The genuine earns-its-keep test is THERE. CORRECT.
- **R3 fallback demonstrated:** TASK `out_of_envelope_FALLBACK` (target_alpha=12 > envelope 6) -> INSUFFICIENT_INPUT -> recall==default asserted; verdict HARD_FAILs if not demonstrated. Demonstrated-not-asserted. CORRECT. (Bonus: no-degrade uses a NON-INFERIORITY margin epsilon=0.02 -- satisfies my R3 "widen-or-margin" the margin way.)
- **R4 v1 scope=(f,projection) only:** select_config returns only {f, projection}; tau/encoder untouched. CORRECT.

## 3 CATCHES before the FULL run

**CATCH 1 (LOAD-BEARING -- proxy-scope the claim):** the validation `kv_recall` is a PROXY. Crowding = adding a shared component (line 78); projection = mean-centering (line 80, explicitly "the #7 learned proj is the production version"). So the cell validates the selector's CHOICE against a synthetic auto-assoc proxy, NOT the real Pythia-KV + #7 learned-projection production path. Two consequences for the honest_claim (currently silent on this):
- The **f-selection** IS verify-the-referent-aligned (it validates against the SAME auto-assoc capability the cited alpha_c(f) curve characterizes -- good, the cell notes this).
- The **projection-routing** benefit is validated on a MEAN-CENTER PROXY, NOT #7. So a HARD_PASS means "the selector's measurement-driven config-choice earns its keep on the cited auto-assoc capability (f) + a projection PROXY" -- it does NOT validate the #7 production projection. **REQUIRED:** the honest_claim + the atom must SCOPE this: "validated on the auto-assoc proxy regression-set (mean-center projection proxy, synthetic crowding); the #7 learned-projection production path is UNTESTED by this cell." Without that scope the cert reads as production-validated (overclaim) -- same scope-guard discipline as sparse onset-not-located / measured-bounds-are-config-contingent.

**CATCH 2 (hygiene -- hardcoded cited curve):** `ALPHA_C_BY_F` (line 40) is HARDCODED in the cell, not read from the sparse atom a3f473dd. The capped points (f0.01/f0.005 -> 6.0) are used in the 2x-margin check as if exact; that's CONSERVATIVE-safe (real alpha_c >= 6.0, so meeting margin at 6.0 guarantees it at the true value -> no correctness bug). BUT verify-the-referent: ideally LOAD the curve from the atom's `key_metrics.alpha_c_by_f` (+ honor `alpha_c_capped_by_f`), or at minimum ASSERT the hardcoded values match the atom -- so a future curve refinement can't silently desync the selector. Flag, not a blocker.

**CATCH 3 (hygiene -- seed stability):** 3 seeds, per-task means, but NO seed-CV gate on the HARD_PASS (unlike continual-writes region_std). Add a seed-CV / cross-seed-agreement note to the verdict so a HARD_PASS isn't riding seed-noise. Minor (3 seeds + non-inferiority margin make it defensible), but a clean add.

**Minor:** 5 tasks (4 discriminating + 1 fallback) is lighter than my suggested 7-9; the epsilon=0.02 non-inferiority margin makes it defensible -- optionally add 2 more discriminating tasks (e.g. very-low-load-high-c, high-load-mid-c) for power. Not required.

## Disposition: DISPATCH-READY on absorbing CATCH 1 (claim-scope)
- The selector LOGIC is well-built + the CAN-fail is genuine. CATCH 1 (proxy-scope the claim) is the one that keeps the eventual cert honest -- bake the proxy-scope into the honest_claim + (on land) the atom. CATCH 2/3 are hygiene (do if cheap). Then smoke (N=1024) -> full (N=4096). I landed-VET on the result with the proxy-scope locked.
- On the result tier: HARD_PASS here = "selector earns its keep on the proxy regression-set (chain-grade candidate)"; I'll rule the final grade off the data + the proxy-scope (data-decides). A genuine proxy-validated HARD_PASS is likely MEASURED_MECHANISM-to-chain-grade-candidate depending on whether the production #7 path is later validated -- we'll see what the data says.

## Standing
- **Exp-Dev:** absorb CATCH 1 (proxy-scope the honest_claim -- load-bearing) + ideally CATCH 2/3; then dispatch smoke->full. The build is otherwise strong -- the 4 refinements are correctly coded.
- **Research:** FYI the proxy-scope means the v1 lever's eventual claim is "selector earns keep on the cited auto-assoc capability + projection proxy" -- the #7 production-path validation is a v2/follow-up (don't let the map over-read it as production-validated).
- **Me:** pre-dispatch VET done. Reactive on the LEVER #1.5 result (landed-VET with proxy-scope) + pythia-KV cell + phase4b pre-reg. **Waiting on:** LEVER #1.5 + pythia cells landing. **USER-pending:** dashboard build (Testbed); Phase-3 cost brief.

-- Skunkworks (cert-owner)
