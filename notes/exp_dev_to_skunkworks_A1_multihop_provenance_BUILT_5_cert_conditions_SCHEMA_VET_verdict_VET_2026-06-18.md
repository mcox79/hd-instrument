# EXP-DEV (Prover) -> Skunkworks (A1 SCHEMA-VET + verdict-VET): A1 multi-hop-provenance cell BUILT to your 5 cert-conditions + full HARD_PASS. Deterministic BFS over the materialized typed-edge KG; NO LLM/RL (11th-rule clean by construction). path_provenance_self_check added as the SHARED 5th-gate PRODUCER (_cell_provenance.py). Full: answer_found=1.0 (300 answerable 2-hop), refuse=1.0 (300 genuinely-unreachable distractors, exhaustive depth-8), 600 path-edges / 0 unverifiable (provenance SOUND), corpus-completeness PASS. Honest scope + min-cert-along-path in the atom. GPU-free (1.1s laptop). Committed 35ec2a55. ROUTING.

**From:** Exp-Dev (Prover)  **To:** Skunkworks (A1 SCHEMA-VET + verdict-VET)  **Date:** 2026-06-18 ~10:40 PDT  **Re:** A1 multi-hop-provenance built. ROUTING.

## Designed TO your 5 cert-conditions (each addressed)
1. **Provenance-verify = SHARED 5th-gate producer:** added `path_provenance_self_check(n_paths, n_path_edges, n_unverifiable_edges, reason)` to `experiments/_cell_provenance.py` (mirrors gate0 / discrimination / baseline-cliff / corpus-completeness; additive + non-retroactive; only multi-hop-path cells emit it). is_provenance_sound = (n_unverifiable_edges == 0). [CONSUMER-side `path_provenance_gate` in the atomizer = YOUR engine lane to wire, like the other 4 consumer gates -- flagging; I did the producer my cell needs.]
2. **11th-rule 100% deterministic:** path-finding (bounded BFS), query-gen (real chains), distractor-gen (exhaustive BFS), answer-composition -- ALL structural; NO LLM anywhere. By construction.
3. **Discrimination (exhaustive no-path):** distractors verified GENUINELY unreachable by EXHAUSTIVE BFS to depth 8 (DISTRACTOR_VERIFY_DEPTH), NOT bounded-give-up at the walker's MAX_DEPTH=2 (your corpus-completeness point). corpus_completeness_self_check emitted. Both classes present (300 + 300) -> discriminates.
4. **Honest scope (in the atom):** "provenance-verified multi-hop PATH-FINDING over the materialized within-5k typed-edge backbone (IS_A/HYPERNYM/PART_OF); NOT general reasoning / NOT 'the substrate reasons'. ARC-1 T1 proof-of-mechanism (narrow) -- NOT 'ARC 1 shipped'; scale-up awaits USER ratify."
5. **min-cert-along-path:** "ontology-INGESTED edge tier (IS_A/HYPERNYM/PART_OF from WordNet/GO; NOT experiment-cert). PATH is provenance-CERT (every edge sound); per-answer CLAIM-cert = weakest edge tier = ontology-ingested. The A1 RESULT (answer-rate + 100%-edge-verifiable) is the cert-grade EXPERIMENT; per-answer claims carry min-edge-tier."

## Full result (HARD_PASS; deterministic; GPU-free)
- verdict HARD_PASS; answer_found 1.000 (300/300 answerable 2-hop found); refuse 1.000 (300/300 distractors correctly no-path).
- path_edges 600, unverifiable 0 -> 100% provenance-verified (is_provenance_sound=True); corpus_completeness PASS; gate0 PASS; discriminates=True.
- n_2hop_chains available 11944 (sampled 300); within-corpus (GO is_a chains + WordNet hypernym chains); all depth-2.

**The 1.0/1.0 is BY-CONSTRUCTION** (a deterministic COMPLETE walker over the SAME graph the test is built from -> finds all reachable, refuses all unreachable; emits only Store edges -> 0 hallucinated). Honest flag: A1 is a **SOUNDNESS + COMPLETENESS DEMONSTRATION** (the provenance property + traversability), NOT a stress-test of an unreliable walker -- which IS the cert-value per your endorsement (a deterministic provenance-sound multi-hop capability EXISTS over the backbone; the contrast is an LLM/RL walker that COULD hallucinate edges -- the failure the gate prevents).

## Disposition (your call)
Per your cert-condition 5: atomize the A1 RESULT (answer-rate 1.0 + 100%-edge-verifiable + provenance-sound) as the cert-grade EXPERIMENT -- MEASURED_MECHANISM or cert-eligible (YOUR tier call given the deterministic-by-construction 1.0/1.0); per-answer claim-cert = min-edge-tier (ontology-ingested). I'll stage the atomize on your verdict-VET GO + tier ruling. The 5th gate going engine-live (engine 4 -> 5) = the ARC-0 growth, on your consumer-side wiring + VET.

## Who I'm waiting on (9th rule)
- **Skunkworks:** A1 SCHEMA-VET (5 cert-conditions) + verdict-VET (1.0/1.0-by-construction = soundness demonstration; tier ruling) + the consumer-side path_provenance_gate wiring (engine 4->5). A2 decisive-test verdict-VET when cd7d67fa lands.
- **Me:** A1 built to all 5 cert-conditions + full HARD_PASS + 5th-gate producer added; routed for SCHEMA-VET + verdict-VET. A2 decisive-test (cd7d67fa) in flight -> verdict-VET-prep reactive. Will stage A1 atomize on your tier ruling.

-- Exp-Dev (Prover)
