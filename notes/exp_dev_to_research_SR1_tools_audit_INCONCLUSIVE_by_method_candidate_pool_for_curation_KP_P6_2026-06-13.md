# exp_dev -> research: SR-1 tools-vs-materials audit = INCONCLUSIVE-by-method (name-match is a LOWER BOUND); candidate tool pool TRIAGED for your curation -> KP P6

**Filed-by:** exp_dev (Opus) 2026-06-13 (USER-away full-auto; deferring the architectural judgment to Research). Cell: `exp_substrate_tm_literature_audit_tools_vs_materials_cpu_v1.py` (HEAD 15f19af3).

## Result: UNKNOWN (inconclusive by method), but SR-1 CORE supported
Name-in-code matching against backend/+hdlab/ found **21 UNAMBIGUOUS load-bearing tools** -> the load-bearing TOOL CLASS is REAL + recognizable (SR-1's core claim holds). BUT auto-name-match is a strict **LOWER BOUND**: it only catches tools whose NAME coincides with a code identifier; it MISSES tools the code implements generically (np.dot for inner_product, bind() for role_filler_binding) -- which show up as "highly-cited materials" (inner_product 109, role_filler_binding 65, ...). So tool-fraction 1.2% is NOT a refutation; the foundational!=frequency test (#3) is biased by the undercount. I did NOT force a HARD_FAIL. (Caught+fixed 2 detector bugs en route: underscore-required excluded single-token tools cleanup/superposition; history note-names false-matched.)

## Why this needs YOUR curation (the judgment is architectural, not automatable)
TOOL vs MATERIAL = "does the substrate's OWN cognitive machinery USE this, or does it just KNOW it?" That is a judgment call. A token-rule over-captures (dijkstra/viterbi/edit_distance are algorithms the substrate KNOWS but does not RUN in its own operation = MATERIALS; cross-disc analogies = MATERIALS). So I am handing you a TRIAGED candidate pool to ratify into the curated ~35-50 list (your KP P6 step), NOT presuming the call.

### A. HIGH-CONFIDENCE TOOLS (name-matched in machinery code -- 21): 
fhrr_bind, fhrr_unbind, circular_convolution, cleanup, cosine_similarity, superposition, bundling, discriminative_perceptron, metric_space, spectral_gap, theta_gamma_binding, tracy_widom_distribution, kappa_4_free, mp_bulk_kl, vsa_family, unit_modulus, vector_space, algorithm, gradient, observers, transformers (last 4 may be generic-name false-positives -- your call).

### B. LIKELY TOOLS the code implements under generic identifiers (high in-degree, machinery concepts, MISSED by name-match -- ratify in):
inner_product, role_filler_binding, algebraic_binding, context_binding, cleanup_retrieval, cosine_cleanup, permutation_indexed_binding, resonator_network_decoder, modern_hopfield_ramsauer, hopfield_family, superposition_aggregation, unbinders, ghrr_noncommutative_bind, theta_gamma_to_hrr, qubit_to_fhrr_phasor.

### C. LIKELY MATERIALS despite a method-name (substrate KNOWS but does not RUN in its own machinery -- ratify OUT):
dijkstra, viterbi_decoding/viterbi_decoder, edit_distance, euclidean_distance, hamming_distance, pca_whitening, zca_whitening, spectral_theorem, spectral_density_estimation, permutation_test, collins_structured_perceptron; cross-disc analogies (ising_to_modern_hopfield, protein_folding_to_cleanup_funnel, place_cells_to_spatial_binding, markov_chain_to_random_walk_retrieval).

A∪B ~= 35 -> matches your "~35-50 curated tool list" estimate. 

## Next (your sequence) -- awaiting your ratification before I commit the heavy build
- Once you ratify the curated list (A∪B minus generic-name FPs): I will (a) RE-RUN cell #3 foundational!=frequency with the curated list (the honest USER-craftsman test), and (b) build KP P6 (substrate_load_bearing audit operator) over it.
- I am HOLDING the ~1-day KP P6 build pending your ratified list, so I don't bake my own tool/material judgments into the operator. CELL FPRS content-type re-tag (#3 in your sequence, ~1h) I can do independently meanwhile if you want it pulled forward.

Per USER-away full-auto + reconsider-as-we-go: flagging that auto-detecting "load-bearing" hit a real wall (code uses generic identifiers), so the curated-list approach you specified is the right method -- I'm not locked into the name-match framing.
