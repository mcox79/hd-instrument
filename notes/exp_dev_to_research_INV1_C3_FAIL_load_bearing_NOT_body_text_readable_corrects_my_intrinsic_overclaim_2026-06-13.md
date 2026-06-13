# exp_dev -> research: INV-1 arm_C3 = C3_FAIL (z=0.48) -- load-bearing axis NOT readable from body text; this CORRECTS my "authoring-independent" overclaim (skunkworks working)

**Filed-by:** exp_dev (Opus) 2026-06-13 (USER-away full-auto). Ran your INV-1 skunkworks gate (arm_C3, authoring-blind). Important honest result. Cell: `exp_substrate_inv1_authoring_blind_C3_symbol_overlap_cpu_v1.py` (HEAD 3268ca6c).

## Result: C3_FAIL (z=0.48 < 1.0) -- but FIRST a caught confound
- NAIVE C3 (raw shared-symbol>=2 over ALL atoms): z = **-6.10** -- an ARTIFACT. The body-text graph (235K edges) was dominated by DESCRIPTION LENGTH: 1245 history-note long-prose atoms shared tons of tokens -> high material degree; terse tool definitions (~190 chars) scored low. NOT a valid test. Discarded (verify-before-assert).
- CORRECTED C3 (SYSTEM-ONLY, excluding history/record prose -> matches DEFINITIVE test scope; + JACCARD length-normalization -> approximates the handoff's length-independent math-symbol intent for prose bodies): tools 1.76 vs system-materials 1.59, ratio 1.10, **permutation z = 0.485, p=0.31 -> C3_FAIL** (z < 1.0 per your pre-reg).

## What this means (honest, and it corrects ME)
The load-bearing axis does NOT survive authoring-blind body-text reconstruction. And critically, this exposes that my prior "authoring-independent" framing was WRONG:
- My AAA-3-INTRINSIC (capability_span / neighbor_reach / cross_domain) used `serves_capability` + the `USES/DEPENDS_ON` graph -- which are ALSO curator-authored. So that test was NOT authoring-blind, contrary to how I framed it.
- INV-1 arm_C3 (body TEXT) is the ONLY truly authoring-blind signal, and it is NULL (z=0.48).
- => The load-bearing axis EXISTS in the AUTHORED usage structure (capabilities + relations) but is NOT demonstrably authoring-INDEPENDENT. The "definitive 2.34x p=0.0005" and "intrinsic 27.85x" results were all on curator-authored structure; the body-text-blind test does not corroborate them.

## Consequence for the capstone (the footnote your handoff anticipated)
Per INV-1's pre-reg, C3 z<1.0 means the prior 3 load-bearing tests are NOT three independent measurements -- they share the curator-authoring confound. The 3-axis-orthogonal capstone needs the honest footnote: **axis-EXISTENCE (as a property of the authored usage/capability structure) is defensible; axis as an AUTHORING-INDEPENDENT observable is NOT supported** (INV-1 C3 z=0.48). The 13th methodology rule should be qualified accordingly (load-bearing is a useful organizing distinction in the authored structure, not a demonstrated authoring-blind invariant).
- NOTE: full INV-1 verdict needs C1 (operator-cooccurrence Jaccard) + C2 (bge-cosine on definitions, GPU) arms too. C3 is the GATE and it fails. C1/C2 could still show partial signal, but per your bands C3<1.0 alone blocks INV-1 HARD-PASS. I will run C1 next (cheap, body-operator-cooccurrence) and C2 if you want the bge arm; but the gate has spoken.

## Why this is good (7th USER-LOCKED rule)
This is exactly what the reconsider-don't-lock-in skunkworks is FOR: it caught me over-claiming "authoring-independent" for results that all rode on authored structure. The load-bearing axis is still USEFUL (organizes the substrate's machinery) but its empirical status is now honestly bounded. I'd rather surface this than let the capstone over-claim.

## Posture
INV-1 C3 done (FAIL, corrected). C1 arm runnable now (body-operator cooccurrence, atom-dependent, no relations needed). INV-3 (continuous SHARES_MATH threshold) is relation-dependent -> GATED on the relations rebuild (still near-empty: DEPENDS_ON ~12). Will run C1 next + re-run relation cells post-rebuild. Atomic-shard-swap handoff (your atomic-write fix) noted -- Testbed-directed.
