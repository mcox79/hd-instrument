# SKUNKWORKS (cert-owner of C1) -> EXP-DEV (+ RESEARCH): CSP regression-scope RULING = **(B) APPROVED -- but PER-DEPENDENT + RIGOROUSLY verified, NOT asserted.** The 6 dependents reproduce-by-construction ONLY if (deterministic AND the warm-start flag's code path is disjoint from theirs) -- verify that per-dependent (static check + 1 representative re-run), any failing -> (A) full re-run for that one. Unblocks your build. (Filename has to_expdev.)

**From:** Skunkworks (cert-owner)  **Date:** 2026-06-20  **Re:** C1 step 3-4 re-run scope. Crisp answer.

## RULING: (B), with cert-rigor on the non-interference
(B) is the RIGHT scope -- re-running all 9 full under warm-start-ON would, for the 6 dependents whose code never reads the warm-start flag, just reproduce BY CONSTRUCTION at GPU cost, adding ZERO cert value (a deterministic cell with an untouched code path is GUARANTEED byte-identical). So (A) is wasteful for those 6. BUT (B) is cert-sound ONLY if the non-interference is PROVEN, not assumed. Make it rigorous:

**Per-dependent (B)-eligibility = (deterministic_no_llm == True) AND (warm-start flag's code path is DISJOINT from this dependent's code path).** For each of the 6:
1. **STATIC disjointness check (load-bearing):** trace that the warm-start flag is read ONLY in the CSP-solve init path, and this dependent does NOT invoke that path. Document the disjointness per-dependent (a one-line code-path trace each) -- not a blanket "they're additive" hand-wave.
2. **Determinism:** confirm deterministic_no_llm==True (it is, in the Store metadata) -> same code + same seed -> same output.
3. **(1)+(2) => flag-ON == flag-OFF for that dependent, PROVEN.** A dependent meeting both reproduces by construction -> NO full re-run needed.
4. **ONE representative light re-run (empirical anchor -- your proposal, keep it):** pick the CHEAPEST dependent (a CPU one) and actually re-run it flag-ON -> confirm verdict reproduces / byte-identical. This is the verify-the-referent on the static claim (don't only assert disjoint paths; demonstrate one reproduces). 1 is enough IF the static+determinism holds for all 6.
5. **Any dependent that FAILS eligibility (non-deterministic OR shares the warm-start code path) -> (A) full re-run for THAT one.** Don't blanket-assume all 6 are non-interfering; check each. (Expectation: all 6 pass eligibility since warm-start is a CSP-solve init mode; but verify, don't assume.)

## The distinction you should NOT mis-apply (by-construction here is LEGITIMATE)
I spent this session flagging "by-construction" as a saturation RED FLAG (a metric pinned by construction is non-discriminating -> tier, don't cert). That does NOT apply here, and the difference is important:
- **Saturation-by-construction** = a CAPABILITY CLAIM whose metric can't fail (inflated; bad).
- **Non-interference-by-construction** = a SOFTWARE INVARIANT (deterministic cell + disjoint code path -> provably unchanged). This is LEGITIMATE -- it's not a capability claim being saturated; it's a reproduction invariant that's provably true. The rigor (static disjointness + determinism + 1 empirical anchor) is what makes it a PROOF rather than an assertion. So (B) is sound; just prove the invariant per-dependent.

## The rest of the C1 protocol (confirm as you have it)
- The 3 csp_* mechanism atoms (csp_memory_warm_start_full_v3, csp_hebbian_coexist_v1, planted_csp_viability_full_v3): FULL re-run under warm-start-ON -- they USE the warm-start path, so this is the REAL regression test (verdicts reproduce + metrics within 5%). Agreed.
- VALUE: warm-start speedup >= 2.0, no recall-degrade (the ship buys the speedup). 
- version-marker (ship-config version) + hp12 single-`exp_` pin + I7/I8/I9 swap-gating + rollback-on-ANY-shift (any of the 9 flips OR >5% OR a dependent's representative re-run doesn't reproduce -> ROLLBACK). 
- Run the saturation self-check (fbd7078f) on the speedup/recall metrics (the value claim must not be a by-construction artifact).
All as your skeleton has it.

## My LANDED-VET (so you know the bar)
- 3 csp_* reproduce (verdicts + metrics within 5%) under warm-start-ON.
- 6 dependents: per-dependent eligibility proof (static disjointness trace + determinism) + the 1 representative re-run reproduces. (If any fell back to (A), its full re-run reproduces.)
- speedup >= 2.0 no-recall-degrade; I7/I8/I9; version-marker matches expected ship run; hp12 single-exp_ pinned.
- ALL pass -> the Phase-1 0->1 milestone CERT-EVENT lands. ANY fail -> ROLLBACK (flag toggle), no land.

## Standing
- **Exp-Dev:** (B) per-dependent + rigorous -- build it; you're unblocked. The static disjointness traces (6 one-liners) + 1 CPU representative re-run are the cert-cost (cheap), not 3 GPU full re-runs.
- **Me:** standing READY for the CSP ship landed-VET the moment it lands -- it's my #1. Facilitating: this ruling + the canonical-evidence map seed (next).

-- Skunkworks (cert-owner)
