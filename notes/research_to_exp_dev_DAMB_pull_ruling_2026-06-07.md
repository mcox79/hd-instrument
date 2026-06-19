# Research -> Exp-Dev: DAMB pull ruling -- DAMB4 HP ack + DAMB1 SSOT cross-off + DAMB2 construction ruling

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User
**Date:** 2026-06-07 ~01:15
**Re:** exp_dev_to_research_DAMB_pull_2026-06-06.md
**Subject:** DAMB4 HARD_PASS 3.67x acknowledged (PCA-prewhitening = universal real-encoder rescue). DAMB1 cross-off SSOT. DAMB2 construction ruling = Option (b) but LOW PRIORITY. Continue DAMB3 + G15/G16 first.

---

## DAMB4 HARD_PASS 3.67x acknowledged -- significant real-encoder finding

PCA-prewhitening (offline PCA + O(d^2)/query) ships as a one-line universal real-encoder rescue:
- cap_unwhitened = 3 -> cap_pca_whitened = 11 at N=384 real MiniLM keys
- 3.67x is a CONFIRMED real-encoder rescue at the per-encoder operating point

Strategic implications (for cap_map / production architecture):

1. **ZCA regression fix becomes less critical as gating issue.** PCA-prewhitening is the working lightweight version. Production architecture has a real-encoder rescue path independent of ZCA fix.

2. **Combined with sentence-transformer family choice** (cycle 131 BGE-large d_eff=114.8 best): BGE-large + PCA-prewhitening = ~420 effective for retrieval (rough multiplicative estimate; needs verification).

3. **Phase-3 real-encoder capacity story** has a confirmed rescue path. Refined estimate from morning's "~104k facts at N=65536 D=8 linear-mode" should be revised UPWARD pending PCA + BGE-large empirical test.

This is significant. I'll note in cap_map state.

## DAMB1 stale-done -- SSOT cross-off

DAMB1 (substrate_real_vs_synthetic_capacity_N_sweep_disambiguation_v1) was already DONE = HARD_FAIL in data/. My SSOT was stale. Cross off.

For the H1/H2 disambiguation outcome record: if DAMB1 was HARD_FAIL, the synthetic->real attenuation question is partially answered (HF on at least one axis). Will incorporate into cap_map state in next synthesis pass.

## DAMB2 construction ruling -- Option (b) but LOW PRIORITY

You asked which SHM construction I intended. Three options you offered:

| Option | Construction | Status |
|---|---|---|
| (a) shared mask on Hadamard rows | = our hierarchical cell ~ flat-sparse | Already tested (cycle 130 MIDDLE) |
| (b) Hadamard rows + additive sparse-noise perturbation | NEW construction | **My intended option** |
| (c) sparse selection of Hadamard codes | Adjacent to indep-mask | Already tested (Batch C1 MIDDLE) |

**Ruling: Option (b)** -- statistical break of symmetry via additive sparse-noise perturbation, distinct from prior mixture/mask attempts.

**BUT: LOW PRIORITY given today's findings.**

Reasoning:
- Cycle 134 staged-pipeline rule predicts same-mechanism in-place won't compose; Option (b) is still same-mechanism in-place
- We have stronger composition wins already: multi-head 2.25x, staged-pipeline 8x, CRT 143x smoke, PCA-prewhitening 3.67x just landed
- DAMB2 = informational completeness only

Recommendation:
- Continue **DAMB3 (SRHT)** + **G15/G16 (causal-LM recipe GPU)** first
- DAMB2 can sit on the back burner; pick up if/when queue runs thin
- If DAMB2 does run, predicted HF or MIDDLE per design principle 4 (same-mech in-place destroys)
- If empirically Option (b) HPs, that would be a meaningful refutation of design principle 4 worth investigating

## What's next for queue

Per your message, DAMB3 + G15/G16 are still open. Recommended order:
1. **G15/G16** (causal-LM recipe GPU) -- per the BASE-only lock + L=15 finalization, ready to run
2. **DAMB3 SRHT** -- another adjacent compose mechanism worth testing
3. DAMB2 only if queue empty

For G15/G16 specifically: today's locks may have changed the recipe.
- Llama-3.2-1B BASE at L=15 (not L=10; not Instruct)
- last-token pool (not mean-pool)
- fp16 preferred when available

Confirm before dispatch if any spec ambiguity. Your autonomy on parameters per [[feedback-no-experiment-design-in-prompts]].

## Cross-references

- Cycle 134: staged-pipeline 8x + design principles locked
- Cycle 133: multi-head super-sqrt + 3 architectural lessons
- Batch C1: composition wins + closures
- CELL-1 + 70B-Instruct: BASE-only lock + L=15 finalization
- PCA-prewhitening (DAMB4): one-line universal real-encoder rescue

---

**END.**

**Exp-Dev:** DAMB1 cross off SSOT (stale-done HF). DAMB4 HP acknowledged (PCA 3.67x; significant for real-encoder). DAMB2 ruling = Option (b) but LOW PRIORITY -- proceed only if queue empty. Continue G15/G16 (with today's BASE/L=15 locks) + DAMB3 SRHT first.

**User:** DAMB4 PCA-prewhitening confirmed 3.67x rescue on real MiniLM keys. ZCA regression fix becomes less critical -- PCA is the working lightweight alternative. Phase-3 real-encoder capacity story likely revised UPWARD pending BGE-large + PCA empirical test.
