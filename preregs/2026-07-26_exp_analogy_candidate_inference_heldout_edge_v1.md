# Pre-reg: exp_analogy_candidate_inference_heldout_edge_v1

**Design-of-record:** notes/research_learned_inference_generalization_analogy_metalearning_2026-07-26.md
**Author:** hdi_exp_dev. **Date:** 2026-07-26. **Stage:** 3 (compositional understanding).
**Anchor:** exp_analogy_candidate_inference_heldout_edge_v1

## Question (directional / mechanism)
Can structure-mapping analogy (Gentner candidate-inference) predict a relational edge that was
NEVER stored in any form -- excluded from train_facts, from the associative memory M, and from every
bind/store call -- from a structurally-similar known base concept? This fixes the store-then-recall
confound in 29578/29579 (`exp_grounding_tem_factorized_heldout_concept_v1`), where the held-out fact
was still written into M at test time (code-confirmed lines 609-611), making "generalization" actually
lookup (RANDOM_G tied FACTORIZED_G, gap=0.0008).

## Compute architecture
- Class: (b) sequential-CPU with justification. Mechanism is sparse relational-profile cosine
  alignment (inverted-index accumulation over ~tens of features per query) + small FLAT MLP train +
  one bundled HRR memory build for the floor arm. No per-phase-point GPU batchable loop dominates;
  full wall < ~5 min. Storage strategy: **no_composition for analogy arm** (similarity+projection over
  profiles, no bind/unbind); **bundled** for the STORE_RECALL_FLOOR arm ONLY (exemption (b): the floor
  arm intentionally reproduces 29578/29579's bundled-memory pipeline on the exclusion-enforced split to
  show it collapses; the analogy arm does not store anything).
- Execution: LOCAL foreground-to-completion (remote/push NOT authorized by caller). smoke then full.

## Arms
1. STORE_RECALL_FLOOR -- bind/unbind/cleanup (reuse `build_memory`/`retrieve_tail_vec`/`cleanup`) on
   the exclusion-enforced split. **PREDICTED near base-rate floor (~1/n_dict ~ 0.0003), NOT 0.836.**
   THE GATE: elevated (near 0.8) => exclusion leaked => HARD_FAIL, respec entire cell.
2. FLAT-MLP -- `train_flat` reused verbatim on stored facts. PREDICTED ho_lift ~ 0 (per 29556).
3. ANALOGY (primary) -- relational-profile alignment (cosine over (rel,slot,neighbor) sparse features,
   IDF-weighted, random-ID content-agnostic) computed ONLY over relation-types OTHER than the predicted
   R; candidate inference = project the R-tail of the top-K structurally-aligned base concepts. Max-sim
   aggregation over the concept dictionary; top-1/top-10 reported.
4. FREQUENCY_PRIOR (honest confound baseline) -- predict the globally most-frequent R-tails. ANALOGY
   must beat this to show alignment quality (not relation-frequency skew) drives any lift.
5. Must-fail controls: SCRAMBLED_ANALOGY_SOURCE (permute E->D projection), SHUFFLED_PROFILE (permute
   which concept owns which profile), RANDOM_ALIGNMENT (random similarity score; necessity control that
   caught 29578/29579). ALL must collapse to within noise of FREQUENCY_PRIOR / base-rate.
6. Out-degree-vs-accuracy diagnostic (Gentner boundary condition): ANALOGY top-1 accuracy vs the
   queried head's non-R out-degree; positive relationship expected.

## Leak-proofing (load-bearing guards)
1. EXCLUSION FROM EVERY STORAGE STAGE: for each held-out head `a` under relation R, ALL (a,R,*) edges
   are removed from `stored_fac`; nothing about a's R-edge enters train_facts, M, FLAT training, or any
   profile. `a` retains its non-R edges (analogy needs alignable structure).
2. LEAK-PROOF ALIGNMENT: profiles used for alignment EXCLUDE the entire predicted relation-type R; the
   alignment score never sees an R-edge. Projection uses OTHER concepts' known R-edges only.
3. NO borrowed embedding: profiles are (rel,slot,neighbor) sparse features over random-ID concept
   indices; content vectors for floor/flat are random unitary carriers. No GloVe/BGE/distributional.

## Primary metric
Top-1 / top-10 accuracy predicting a held-out head's R-tail (gold = set of the head's true R-tails),
against the full concept dictionary (~3.4k) as candidate pool. Reported per arm + per heldout relation.

## Bands (per design-of-record)
- HARD-PASS: STORE_RECALL_FLOOR collapsed (no leak) AND all 3 must-fail controls collapse AND ANALOGY
  clears STORE_RECALL_FLOOR by >=10x base-rate or >=15pp AND clears FLAT by a comparable margin AND
  beats FREQUENCY_PRIOR AND positive out-degree-accuracy relationship.
- HARD-FAIL: ANALOGY ties floor/FLAT within ~5pp (analogy insufficient on this corpus) OR a control
  fails to collapse (bug -> respec) OR STORE_RECALL_FLOOR elevated (exclusion leaked -> respec cell).
- MIDDLE_BAND: ANALOGY clears floor+FLAT by 5-15pp with controls holding; or clears floor decisively
  but out-degree flat / does not beat FREQUENCY_PRIOR (relation-frequency-skew confound, reportable).

## SCHEMA-VET fields
- cardinality_ok: EXPECTED_N_UNITS = n_seeds * n_arms (7 scored arms); verdict counts and gates.
- crlb_n/a: "retrieval/prediction-accuracy discriminator; no Gaussian noise floor. base_rate=1/n_dict
  and FREQUENCY_PRIOR reported as the empirical floors; controls gated against them."
- discriminator_reachability: true (planted self-test proves ANALOGY >> FREQUENCY_PRIOR/RANDOM_ALIGNMENT
  when structural twins exist; instrument can fire).
- baseline_in_band: EXEMPT -- STORE_RECALL_FLOOR, FLAT, FREQUENCY_PRIOR are intended-floor baselines
  (known-floor exemption, same as reference cell). ANALOGY is the mechanism arm.
- arms_differ_verified: true (per-query top-1 prediction arrays hash-checked across mechanism/control arms).
- final_metrics_atomicity: tmp_replace.
- deterministic_seeding: true (fixed int seeds; np.random.RandomState(seed+offset); sorted(set());
  blake2b for any feature hashing; NO builtin hash()-seeded RNG, NO list(set()) ordering).
- start_marker_written / crash_diagnostic_present: true. cell_chunked: false (light multi-seed inline).
- progress_logging: line_buffered_stdout (cell < 15 min; flush on newline).
- real_code_path: verbatim reuse of reference cell's data-loader/binding/memory/flat via importlib exec
  of the exact source module; self-test asserts bind parity vs hdlab.binding.
- discriminating_fraction / effective_params: n/a (no parameter sweep axis; fixed regime).

## HP_SCOPE
{ANALOGY: [clears_floor_10x_or_15pp, clears_flat, beats_frequency_prior, positive_outdegree]}.
Baselines/controls inherit NO HARD_PASS gate; they are floor/collapse arms.
