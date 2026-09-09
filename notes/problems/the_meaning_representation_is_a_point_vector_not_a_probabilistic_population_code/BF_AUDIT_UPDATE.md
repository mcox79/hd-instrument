# AUDIT UPDATE -- probabilistic population-code meaning representation (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

Solver: the_meaning_representation_is_a_point_vector_not_a_probabilistic_population_code (2026-09-10).
This is the build of C7's path-to-fully-BF #5 / non-BF register row 10 (the deep architectural fix). Below are the
verdicts to fold into the living audit.

## 1. Row 2 (FUSION) BF-fix note -- REVISE
- OLD (from the C7 audit): "equal weights now; genuine precision needs a probabilistic population-code
  representation (deep fix)."
- MEASURED NOW: the population-code precision is the population GAIN = accumulated evidence (Ma/Beck/Latham/Pouget
  2006). It IS intrinsic and it DOES track correctness on the LEARNED channel -- per-item Spearman(gain, RR) = 0.221
  CI [0.114, 0.322], CI-separated ABOVE the point-vector peakedness baseline (-0.097; gain-minus-peak CI
  [0.141, 0.482]); binned Spearman 1.0. So the representation CAN carry precision (the deep fix's premise holds).
- BUT precision-weighted FUSION does NOT beat equal-weight Bayes (0.304 vs 0.324); a FITTED per-channel weight also
  fails (0.317 < 0.324). Equal-weight is at the per-query reweighting ceiling on this task.
- NEW fix note: "Population-code precision = gain confirmed (tracks correctness CI-sep, item 1). The lever is NOT
  fusion-reweighting (equal-weight is at ceiling; a fitted weight fails too) but (a) reliability-aware DEFERRAL and
  (b) growing the LEARNED channel to dominance -- its gain is the only earned precision (curated-channel gain
  anti-tracks)."

## 2. Non-BF register row 10 (point-vector meaning + cosine) -- STATUS CHANGE
- OLD: "IDENTIFIED as the deep architectural fix (population code -> intrinsic precision); proposed, not built."
- NEW: BUILT + MEASURED. Item 1 (precision tracks correctness) PASS; item 3 (recall byte-identical) PASS; item 2
  (fusion beats equal) LOCATED NEGATIVE with a number (reweighting ceiling; curated-channel dominance). Concrete
  hdlab proposal filed (carry per-concept gain; replace convergent_cue_reader.w with the intrinsic gain ratio).

## 3. NEW deviation found (add to the register)
- `convergent_cue_reader.DEFAULT_W = 12.0` -- a FITTED reliability weight, self-labelled OUR-INVENTION-UNDER-TEST
  ("our two cue codes are NOT one shared PPC population, so the automatic-gain story does not give the cross-cue
  ratio for free"). VERDICT: NOT_BF (fitted). BF FIX: the intrinsic per-query gain ratio g_sem/g_epi (matches the
  fitted weight with no fitting; parameter-free). This is the load-bearing landing for this problem.

## 4. Proposed `__bf_status__` deltas (Q111 -- strategy lands)
| organ | current | note |
|---|---|---|
| `convergent_cue_reader` | (propose) "BF_SPIRIT" | "convergent-cue Bayes combination is BF; the fitted reliability weight w is OUR-INVENTION -> replace with the intrinsic per-query gain ratio (this problem)" |
| `grounded_similarity` | "BF_SPIRIT" (unchanged) | ADD: "loads only the .mean columns; the per-word rater .SD (a behavioural reliability = population precision) is discarded at asset load -- carry it as the channel gain" |

## 5. The experience-quantity finding (durable, worth a line in the audit)
Population gain is a valid precision ONLY for LEARNED representations (accumulated synaptic evidence). MEASURED
contrast on the SimLex ranking: LEARNED dependency channel gain binned-Spearman +1.0 with correctness; CURATED
WordNet channel gain binned-Spearman -0.2 (anti-tracks -- more features = more polysemy); grounded rater-agreement
-0.4. A curated ontology has no earned gain, hence no intrinsic precision -- a general rule for judging which
channels can carry PPC precision.
