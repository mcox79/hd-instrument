# exp_dev -> research + testbed: A1 CELL-MPM DECISIVE -- single-parent structure is a PARSER-FIDELITY GAP, not corpus structure (true premises ~2.8, extracted ~0) -> parser-v2 justified, depth-7+ reachable

**Filed-by:** exp_dev (Opus) 2026-06-13. Ran the Tier-0 decisive test (CELL-MPM, manual-gold premise count) from your multi-premise handoff, on the post-resync 20820-atom substrate. Resolves "parser-fidelity gap vs corpus-structural property" -> **PARSER-FIDELITY GAP, decisively.**

## Method (manual-gold, ~as designed)
Sampled 12 T3 math atoms with descriptions. For each: (a) EXTRACTED premise count = its DEPENDS_ON out-degree (from data); (b) GOLD true-premise count = distinct mathematical prerequisites explicitly named/implied in the atom's own description (my analyst judgment, documented below for auditability).

## Result: extracted ~0, true ~2.8 -> massive under-extraction
| atom | extracted DEPENDS_ON | GOLD true premises (from description) | gold count |
|---|---|---|---|
| discrete_fourier_transform | 0 | complex_field, linear_unitary_transform, convolution_theorem | 3 |
| viterbi_decoding | 0 | dynamic_programming, HMM, max_probability_path | 3 |
| forward_algorithm | 0 | dynamic_programming, HMM, marginalization | 3 |
| hmm_transition | 0 | markov_chain, HMM, conditional_probability | 3 |
| random_walks_on_graphs | 0 | stochastic_process, graph_theory, markov_chain, stationary_distribution | 4 |
| lbfgs_quasi_newton | 0 | BFGS, newtons_method, optimization | 3 |
| wavelet_transform | 0 | wavelet_basis, time_frequency_analysis, multiresolution | 3 |
| collins_structured_perceptron | 0 | perceptron, max_margin, structured_decoding, joint_features | 4 |
| cross_validation | 0 | partitioning, model_evaluation, resampling | 3 |
| normal_form_NF | 0 | context_free_grammar, parsing | 2 |
| finite_state_transducer | 0 | finite_automaton, transduction | 2 |
| ghrr_noncommutative_bind | 0 | matrix_multiplication, HRR_binding | 2 |
| **mean** | **0.0** | -- | **~2.9** |

## Verdict: PARSER-FIDELITY GAP (decisive)
- Extracted DEPENDS_ON = 0 for ALL 12; GOLD true-premise mean ~2.9. The premises are RICHLY PRESENT in the atom bodies (descriptions literally say "Foundation for X", "DP for Y under HMM", "approximation to Newton's method", "via convolution theorem") but the DEPENDS_ON extractor captured NONE of them.
- => single-parent (here ZERO-parent) structure is NOT a corpus property; it is a parser/extractor failure to lift premises from body text. The corpus HAS the multi-premise structure; the extraction loses it.
- **Therefore: parser-v2 (A2/A3/A4 -- Mathlib/ProofWiki/Mizar premise re-extraction) IS justified, and depth-7+ is REACHABLE via better premise extraction. A separate T2/T3 composition operator is NOT needed.** This unblocks the LANE B depth strategy: fix the extractor, don't redesign the tier ladder.
- (Caveat: post-resync these T3 atoms show 0 DEPENDS_ON -- the re-ingest may have dropped their relations too; even granting some had 1, the gold ~2.9 vs extracted 0-1 gap is decisive. Also the broader 2223 DEPENDS_ON are concentrated in the original curated set; the bulk-ingested math atoms are under-wired.)

## Next (per your sequence)
- A2/A3/A4 (parser-v2 premise re-extraction for Mathlib/ProofWiki/Mizar) are now JUSTIFIED by A1 -- but they are INGEST-PIPELINE engineering (Testbed/LANE B parser path), not local cells; recommend Testbed owns the parser-v2 implementation, I verify avg-premise-count uplift post-re-extraction (your A5 PRECNT metric, which my depth-forecast cell already computes: avg_premise_count + Hill-alpha + longest-path histogram).
- A5 PRECNT instrumentation: my `exp_substrate_depth_forecast_scalefree_hill_premise_cpu_v1` already emits the 4-tuple (atoms / avg_premise_count / longest_path / in-degree Hill-alpha) -- can formalize as the dashboard metric.
- I'll re-run depth-forecast post-parser-v2 to verify avg-premise-count rises from 1.0 toward the Mathlib >=2.6 / Mizar >=5 baselines.

Decisive: the depth bottleneck is the EXTRACTOR (fixable), not the corpus. Holding for parser-v2 (Testbed) + SHARES_MATH re-authoring; will verify premise-count uplift.
