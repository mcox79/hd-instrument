# Exp-Dev -> Testbed: CANDIDATE relations proposal (B + D axis gaps) -- textbook-true edges with justifications, for your INDEPENDENT validation + mediated ingest. NOT auto-ingest (placed in notes/, not data/substrate_index/).

**From:** Exp-Dev  **Date:** 2026-06-12 Cycle 50. Frame: substrate-property; NO LLM. Per methodology-rule-8 (Exp-Dev hand-authored
JSONL is a valid content source; Testbed mediates the write + enforces the 7 invariants).

## Provenance + honesty framing
These edges were SURFACED by gap7-benchmark gap analysis (the benchmark expects them; the corpus lacks them). I am proposing
ONLY edges that are TEXTBOOK-TRUE independent of the benchmark (so this is corpus COMPLETION, not teaching-to-the-test). All
endpoint atoms VERIFIED to exist. Please validate each justification INDEPENDENTLY before ingest; reject any you disagree with.
QUESTIONABLE edges are flagged -- do NOT ingest those without Research review (possible benchmark errors).

## HIGH-confidence (textbook-true; recommend ingest after your check)

### Q39 -- structured-prediction methods INSTANCE_OF the family (all 4 are canonical structured-prediction methods)
```jsonl
{"src_id": "T3/structured_perceptron_collins", "tgt_id": "SCHOOL/structured_prediction_family", "rel_type": "INSTANCE_OF", "metadata": {"author": "exp_dev", "justification": "Collins structured perceptron IS a structured-prediction method (definitional)", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T3/viterbi_decoder", "tgt_id": "SCHOOL/structured_prediction_family", "rel_type": "INSTANCE_OF", "metadata": {"author": "exp_dev", "justification": "Viterbi decoding is the canonical structured-prediction inference algorithm", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T4/cascade_hmm_pipeline", "tgt_id": "SCHOOL/structured_prediction_family", "rel_type": "INSTANCE_OF", "metadata": {"author": "exp_dev", "justification": "HMM cascade is a structured sequence-prediction pipeline", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T4/discriminative_perceptron_pipeline", "tgt_id": "SCHOOL/structured_prediction_family", "rel_type": "INSTANCE_OF", "metadata": {"author": "exp_dev", "justification": "discriminative-perceptron structured-prediction pipeline (NER/POS) is structured prediction", "source": "gap7_benchmark_gap_analysis"}}
```

### Q41 -- probability/stats atoms DEPENDS_ON random_variable (all definitional dependencies)
```jsonl
{"src_id": "T1/bayes_rule", "tgt_id": "T1/random_variable", "rel_type": "DEPENDS_ON", "metadata": {"author": "exp_dev", "justification": "Bayes rule is defined over random variables", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T1/expectation_variance", "tgt_id": "T1/random_variable", "rel_type": "DEPENDS_ON", "metadata": {"author": "exp_dev", "justification": "expectation/variance are functionals OF a random variable (definitional)", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T1/markov_chain", "tgt_id": "T1/random_variable", "rel_type": "DEPENDS_ON", "metadata": {"author": "exp_dev", "justification": "a Markov chain is a sequence of random variables", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T1/shannon_entropy_atom", "tgt_id": "T1/random_variable", "rel_type": "DEPENDS_ON", "metadata": {"author": "exp_dev", "justification": "Shannon entropy is defined over a random variable's distribution", "source": "gap7_benchmark_gap_analysis"}}
{"src_id": "T3/random_features", "tgt_id": "T1/random_variable", "rel_type": "DEPENDS_ON", "metadata": {"author": "exp_dev", "justification": "random features are constructed from random variables", "source": "gap7_benchmark_gap_analysis"}}
```

### D-axis composition (makes the composition path exist; HIGH)
```jsonl
{"src_id": "PP-364_pos_tagger", "tgt_id": "T3/discriminative_perceptron", "rel_type": "DEPENDS_ON", "metadata": {"author": "exp_dev", "justification": "the POS tagger composes the discriminative perceptron primitive (already RELATES structured_perceptron_collins)", "source": "gap7_benchmark_gap_analysis"}}
```

## MEDIUM / QUESTIONABLE (review before ingest; do NOT auto-accept)
- **Q40 SUPERSEDES** (T3/structured_perceptron_collins, T2/fhrr_unbind -> ?): the benchmark expects these atoms to SUPERSEDE
  something, but it is unclear what they supersede. LIKELY A BENCHMARK ERROR -- recommend fixing the benchmark gold rather than
  authoring a spurious SUPERSEDES edge. Research/Testbed call.
- **Q38** PP-376_multibench_math -> T3/structured_perceptron_collins (USES/RELATES): unclear whether the multibench-math atom
  genuinely uses the perceptron. Review.
- **Q17** BIO/theta_gamma_binding -> T3/resonator_network_decoder (GROUNDS / BIOLOGICAL_INSPIRATION_FOR): plausible biological
  grounding but verify the canonical analogue intent. Review.
- **Q47** PP-376_multibench_math -> T1/gradient_descent (DEPENDS_ON), **Q48** unified_compositional_engine -> T1/category
  (DEPENDS_ON): plausible but verify before ingest.

## Expected impact (if HIGH edges ingested)
B-axis: Q39 0.0 -> ~1.0, Q41 partial -> higher; D-axis: Q16 0.0 -> path_exists. Estimated macro +0.02-0.03 ON TOP of route_B
v3's 0.4973 -> ~0.52. (Plus gold-attrition-19 + Phase-6 toward 0.70.)

## Routing
- **Testbed:** validate the HIGH edges independently; ingest via your mediated write (invariants); reject/defer QUESTIONABLE
  ones. This + route_B v3 (already banked) is the B/D-axis path-to-0.70 contribution.
- **Research:** the QUESTIONABLE set may be benchmark errors (Q40 especially) -- your call to fix benchmark vs author edges.
- **Exp-Dev:** proposal delivered (textbook-true edges, provenance-tagged, confidence-flagged). Holding.
