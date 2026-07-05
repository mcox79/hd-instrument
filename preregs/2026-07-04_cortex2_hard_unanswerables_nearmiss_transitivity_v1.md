# Pre-reg: cortex2_hard_unanswerables_nearmiss_transitivity_v1 (2026-07-04)

The HARD follow-up to cortex2_provenance_faithfulness_and_calibrated_refuse_v1. v1 got refuse/AUROC=1.0
but flagged it as by-construction-EASY (unanswerables had support FULLY ABSENT). This cell replaces
those with HARD unanswerables to decide: is the glass-box audit a GENUINE differentiator or an
easy-test artifact? CPU-local, NO re-encode, no substrate mutation. Sharded FHRR KG over FB15k-237.

## Two HARD classes
1. NEAR-MISS: valid hop1 to a REAL, often HIGH-DEGREE intermediate, but the FINAL edge is absent.
   Tests whether per-hop confidence still refuses when a busy intermediate raises the noise floor.
2. TRANSITIVITY-VIOLATION (ATTACK-7): BOTH edges present (mechanically composable) but the composition
   is arbitrary/non-materialized. Label (NON-CIRCULAR vs the confidence detector): VIOLATION iff no
   direct edge (s, any_r, tail) corroborates the composition. Detector under test = per-hop cleanup-
   cosine confidence (independent of that corroboration label). Same mid-distribution as answerable so
   composition-validity is isolated from difficulty.

## Discriminator (populated, robust)
AUROC separates answerable-correct confidence (should-answer) from each hard class's confidence
(should-refuse). ~0.5 => confidence CANNOT tell them apart. Both sets NQ each.

## Pre-registered bands
- GENUINE_DIFFERENTIATOR: faithfulness_answerable >= 0.70 AND near-miss AUROC > 0.65 with
  refuse-precision > black-box's 0.0 AND cortex beats black-box on transitivity via chain-completeness.
- EASY_TEST_ARTIFACT: near-miss AUROC < 0.60 (collapses to chance) => v1's 1.0 was an artifact.
- Transitivity finding reported regardless: AUROC ~0.5 => per-hop confidence does NOT catch transitivity
  (expected: it measures hop-support, not composition-validity); glass-box value there = auditability.

## RESULT (FULL, 3 seeds, VE=6014; MEASURED@data/exp_cortex2_hard_unanswerables_nearmiss_transitivity_v1/metrics.json)
- verdict: GENUINE_DIFFERENTIATOR.
- faithfulness_answerable = 0.842 (std 0.044) -- decisive metric HOLDS on the hard cell.
- NEAR-MISS: AUROC = 1.000 (std 0.000), refuse-precision = 1.000, confabulate-rate = 0.000. Confidence
  robustly catches missing-final-edge EVEN with busy intermediates -> NOT an artifact.
- TRANSITIVITY: AUROC = 0.529 (std 0.007) ~ chance, refuse-precision = 0.131 (~ base refuse rate).
  Confidence CANNOT catch transitivity violations (both hops supported). HONEST NEGATIVE.
  BUT faithfulness_transitivity = 0.814 (audit honest even for the fallacy) and chain-completeness
  cortex = 1.000 vs black-box = 0.500 -> the glass-box exposes the exact composition for external audit;
  the black-box's decorative citations cannot.
- easy-ref (v1 regime, on-cell): AUROC = 1.000 -> reproduces v1's easy result for contrast.

## Interpretation
Confidence works when a HOP lacks support (near-miss AUROC 1.0, easy 1.0); it FAILS when the composition
is invalid but hops are supported (transitivity AUROC 0.53). So the glass-box's AUTO-REFUSE is genuine
for support-absence but blind to composition-validity. The differentiator that survives the transitivity
class is FAITHFUL PROVENANCE / COMPLETENESS (auditability), not auto-refuse. Genuine, not artifact --
with a clearly-scoped limit (transitivity needs a corroboration/consistency check the faithful trace
ENABLES but this cell did not build; that is the honest next step, not a wall).

## SCHEMA-VET / discipline
cardinality_ok true (3 seeds); arms_differ_verified true; final_metrics_atomicity tmp_replace; crlb_n/a
(fractions over deterministic argmax re-runs); baseline = black-box completeness 0.5 < cortex 1.0
(in-band); discriminator_survives_scale (near-miss/transitivity AUROC identical smoke->full at 3x);
except SystemExit: raise before except Exception; start_marker + crash-diagnostic; progress_logging
line_buffered_stdout. Ran CPU-local foreground (119s, does not hog laptop).
