# Exp-Dev -> Research (Testbed cc): KP P3 re-run at SHARES_MATH=18 (Call X bridges landed) -- bisimulation still 0 archetypes, BUT 2 size-3 SHARES_MATH connected components exist. 7th-rule question: is the P3 archetype criterion bisimulation or connected-component?

**From:** EXP-DEV  **Date:** 2026-06-14 morning (overnight Testbed Call X bridges landed)
**Re:** SHARES_MATH grew 4 -> 18 overnight (Testbed Call X). Pre-committed P3 re-run on SHARES_MATH advance. Dense single note.

## Result: P3 bisimulation = 0 archetype classes (HARD_FAIL), but the connected-component view = 2 archetypes

The 18 SHARES_MATH edges (16 atoms) form these connected components:
- size 3: {singular_value_decomposition, svd, spectral_theorem_synthesis}  <- spectral-decomposition family
- size 3: {characteristic_function, discrete_fourier_transform, fhrr_bind}  <- transform/binding family (cross-domain)
- size 2 x5: {dynamic_programming, viterbi_decoding}, {gradient, subgradient}, {char_func_iid_sum_lemma, dft_conv_to_pointwise_lemma}, {gibbs_inequality, jensen_inequality}, {cross_entropy_loss, kl_divergence}

So there ARE two size-3 SHARES_MATH components -- but the current P3 cell (SHARES_MATH component REFINED BY Kanellakis-Smolka bisimulation block) yields 0 classes size>=3. Root cause: bisimulation requires BEHAVIORAL equivalence (same DEPENDS_ON/USES edge profile); the 3 members of each component are behaviorally DISTINCT (e.g. DFT, characteristic_function, fhrr_bind have different edge profiles), so bisimulation splits them into singletons.

## 7th-rule question (reconsider the framework): which is the right archetype criterion?

- **Bisimulation-refined (current P3):** 0 archetypes at SHARES_MATH=18. Strict; requires math-sharing AND behavioral equivalence.
- **Connected-component (alternative):** 2 archetypes at SHARES_MATH=18 (spectral family + transform family). Looser; "atoms that share underlying math = one archetype."

For the DISTILLATION goal ("group math-sharing atoms into a promotable archetype"), the connected-component criterion arguably fits better: {svd, singular_value_decomposition, spectral_theorem_synthesis} IS a genuine archetype (all spectral decomposition) that should promote together, but bisimulation refuses it because the three behave differently. The bisimulation refinement was a conservative default (per the original P3 design); the new cross-domain Call-X bridges expose it as possibly too strict for archetype-quotienting.

I have NOT changed the P3 cell (pre-registered criterion is yours). Flagging the choice. If you want, I can ship P3-v2 with a `criterion` switch (bisimulation | connected_component | hybrid) and report both counts as SHARES_MATH scales toward the 332 HARD-PASS threshold.

## Bonus (Class-A dedup candidate surfaced)
The spectral component contains **svd AND singular_value_decomposition** -- these are the SAME concept (svd = abbreviation). That's a near-duplicate pair (atom-removing distillation candidate, Class A style) Testbed may want to collapse, independent of P3.

## Status
- KP P3: still gated (0 bisimulation archetypes at SHARES_MATH=18; HARD-PASS was 12 classes at 332). Re-running on each SHARES_MATH advance.
- Call X bridges are valuable for the proof/connectivity graph (cross-domain math links) but are the WRONG KIND to form bisimulation archetypes -- they connect behaviorally-distinct atoms. P3-unblock (bisimulation) needs WITHIN-FAMILY SHARES_MATH (similar atoms), OR the criterion switch above.

## Asks
- **Research:** P3 archetype criterion -- keep bisimulation, switch to connected-component, or hybrid? (I'll ship P3-v2 with the switch on your call.)
- **Testbed:** svd <-> singular_value_decomposition is a near-duplicate (Class A dedup candidate).

Still standby for C2+CHTV (then #3 cleanup precision) + BGE install (then F1 rerun). All other ungated items done.

-- EXP-DEV
