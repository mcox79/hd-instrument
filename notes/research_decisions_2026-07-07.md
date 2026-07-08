
- 2026-07-07T17:28:27Z research: 2x negative-revival on resonator self-margin HARD-FAIL -> notes/research_resonator_basin_proliferation_self_predictability_2026-07-07.md. Mechanism CONFIRMED (convergence-basin/spurious-joint-fixed-point proliferation, cross-validated 3 independent lit-scans + substrate's own 2026-05-19 history, same Frady-Sommer/Karunaratne-Langenegger paper family). Self-predictability: NO ready closed form this cycle (P_deflated=0.65 negative finding), but this is an effort/scoping boundary not a fundamental one (unlike row 8b) -- own z_init=16.8 derivation verified to <1%, combinatorial-count check honestly HARD-FAILs by ~10x (informative, localizes the real derivation gap). No 4th CG_META family minted. Concrete near-term actionable: apply substrate's own validated ACF rescue (cap_map row 51, codebook-size axis) to the untested factor-count axis (this cell) -- template experiments/exp_wave14b_acf_resonator.py.

- 2026-07-07 (brain-component-driven-development, next-arc audit): re-ranked all 5 missing/weak brain-component
  candidates (thalamus, cerebellum x2 targets, basal-ganglia, neuromodulation, CLS-consolidation, cortical
  microcircuit) for a PROVEN CONSUMER post-thalamic-router-shelving. 4/6 confirmed still consumer-less
  (thalamus pre-shelved; CLS tied to deferred general-knowledge ingest; neuromodulation-as-encoder-gain-knob
  is my own unevidenced hypothesis; cortical-microcircuit 2x narrow HARD_FAIL banked) -- unchanged from the
  07-06 backup's own conclusion, no new evidence today. 1 cerebellum target (autonomous-decomposition waypoint
  chain) is NOW CLOSED (`exp_pfc_gate_waypoint_rescue_coarse2fine_verify_v1` FULL HARD_FAIL, DELTA=0.004).
  TOP PICK: cerebellum-class SR-rollout anticipatory-bias mechanism for the OTHER target -- the already-BUILT,
  already-HARD_PASS-at-d4 PFC-BG gate's (`exp_pfc_gate_cfrpe_trained_v2`) own measured depth-degradation
  (gonogo_lift 0.653->0.075, d4->d6). Prior lever (multi-gamma/branching, smoke-only) found NOT the driver;
  2 fresh external lit-scans independently confirm gamma-only is an established-insufficient fix class in the
  literature, and find the specific anticipatory-forward-model-for-gating-horizon combination has NO direct
  precedent (novel synthesis, P capped). Full cell spec (3-arm smoke, CPU, reuses on-disk SR machinery) in
  notes/research_brain_component_consumer_ranking_cerebellum_control_depth_2026-07-07.md.

- 2026-07-07 (2x drill, converging negative -- noise-compounding bound across 3 cells): resonator K-way
  basin proliferation, autonomous waypoint HARD_FAIL_COMPOUNDING_ERROR_BOUND_REAL, cerebellar SR-rollout
  (recovered_frac=-1.40) all show recurrent/multi-step decode underperforming single-step. VERDICT: CONTRABLE,
  not fundamental -- TWO distinct sub-mechanisms, neither shared by reasoning-depth's survival. Class A (no
  external reset mid-iteration, resonator): fully deterministic zero-T coupled search, no randomization axis
  exists in the code today (confirmed by source re-read). Class B (self-referential correction, waypoint +
  cerebellar rollout): fresh on-disk re-read finds `retry_rate_combo=0.0`/`fallback_rate_combo=0.0` at the
  deepest FULL-tested waypoint regime -- the verify-gate NEVER triggered, proving it checked the pick against
  the SAME noisy R matrix that produced it (decision-feedback-equalizer-style correlated error, not
  regenerative-repeater-style independent reset) -- explains why a well-precedented rescue still landed
  DELTA=0.004. Reasoning-depth survives because each hop is a hard argmax decode against a FIXED EXTERNAL
  codebook (regenerative-digital-repeater property, zero residual noise on success, i.i.d per-hop failure,
  composes as p^D). TOP candidate: finite-temperature Glauber relaxation + redundant-restart plurality vote on
  the resonator K4 case -- converges independently with field advisor's own #2-ranked D1 candidate. Full note:
  notes/research_noise_compounding_bound_deep_mechanism_2026-07-07.md. P_deflated=0.50 (mechanism diagnosis,
  capped) / 0.28 (rescue clears MIDDLE) / 0.20 (rescue clears HARD-PASS).

- 2026-07-07 (forward-derivation, 970K scale-test forecast): classified the encoder's two readouts
  by decode regime per the self-margin taxonomy -- discrete SBC block-argmax algebra (K=128 x L=32)
  = disjoint-block/collision-count (holds at 970K, combinatorial margin ~180 orders of magnitude,
  P_deflated~0.60-0.65 HARD-PASS); continuous dense retrieval (`ret_agree10`) = order-statistic/
  distance-concentration (ALREADY failing at 0.18-0.27 at 18% of scale, forecast to degrade further
  with NO cliff, P_deflated~0.05 HARD-PASS at 970K on plain SBC). GSBC graded-code lever already
  measures 1.5-3x better at the SAME 177,899 scale (0.31-0.68) but its own density-dial retune is
  unverified past ~160K and is the one place a genuine Donoho-Tanner-class sharp cliff is plausible
  (P_deflated~0.30-0.35, capped, HARD-PASS at 970K IF retuned). Cheapest next action: CPU-only
  near-duplicate density measurement in the real `entities.jsonl` (Test 0), before any GPU scale-test
  dispatch. Full note: notes/research_encoder_970k_marchenko_pastur_codebook_collision_forecast_2026-07-07.md.
  3 parallel Sonnet lit-scans, 33 verified external sources, zero substrate-novel terms sent externally.

- 2026-07-07 (Test 0 executed, CPU-only, no GPU, no dispatch): measured near-duplicate density
  directly in the real `data/substrate_director_kb_v1/entities.jsonl` (970,069 rows, confirmed on
  disk). Finding: exact-dup rate low (0.66%), but 15.86% of V (note/prereg document chunks) sit in
  near-identical clusters by construction (within-doc Jaccard 0.96-0.97) and WordNet polysemy
  collapses 121,274 rows to 89,395 distinct lemmas (39.6% share a lemma with >=1 other row).
  Effective-distinct/V drops from 0.9966 (naive exact-dup) to ~0.79-0.83. Re-derived birthday margin
  with the effective-distinct count: still ~180.5+ orders of magnitude vs raw V's 180.4 -- the
  discrete-algebra "combinatorial margin holds" conclusion is CONFIRMED robust to the measured
  structure (GREEN). Structured-collision risk is real but narrow: concentrated in 2 identified,
  cheaply-dedupable sources (chunking + WordNet polysemy), not diffuse across the corpus
  (YELLOW, not RED). Concrete recommendation: dedup near-identical sibling chunks before the 970K
  scale-test (shrinks V by up to ~14%, ~138K rows); retune GSBC density dial against effective
  V~800K-830K if deduped, or raw 970,069 as a safe fallback if not. Also discovered: the 970K KB is
  NOT ConceptNet-like as the prior forecast assumed -- it is a dogfood ingest mixing external KBs
  (WordNet/GO/KEGG/FrameNet/VerbNet/NeuroLex) with the project's own notes/preregs/memory/metrics,
  chunked. Full note: notes/research_970k_kb_near_duplicate_density_test0_2026-07-07.md.
  0 external citations this cycle (internal filesystem measurement, not a lit-scan).

- 2026-07-07 (bounded convergence drill, re-slice attempt): tried to re-slice EXISTING
  keyed@J5/shuffled_key per-item retrieval results by chunk-vs-non-chunk membership (Test 0's own
  named next step) to test whether the retrieval margin is CONCENTRATED in the near-dup pool or
  DIFFUSE. VERDICT: neither -- DATA-ABSENT. Checked all 14 full-scale metrics.json files in the
  encoder lineage plus every non-metrics.json artifact under data/exp_encoder_*/substrate_concept_
  encoder*: none contain per-item outcomes, only aggregate scalars. Confirmed structurally by
  reading the eval code itself (_keyed_unit/_semantic_unit in exp_encoder_migration_step1b_v3_
  ..._core.py): per-trial KB-row identity and per-row rank-agreement are computed transiently in
  memory and reduced to a scalar before return -- never serialized. MID_TRIALS=60 also means even a
  logging fix would face a thin per-run sample (~48 expected near-dup draws per unit). This closes
  the "re-slice" branch as a dead end (cheaply, no GPU/training) -- any future test of Test 0's
  structured-collision hypothesis needs new inference with logging added, not a re-slice. Test 0's
  P_deflated (0.35-0.45, capped 0.50) for the underlying hypothesis is UNCHANGED (no new evidence
  either way). Dedup of note/prereg chunk siblings remains reasonable on its own structural merits
  regardless. Full note: notes/research_970k_retrieval_margin_concentration_reslice_2026-07-07.md.
  0 external citations (internal code/filesystem audit).

- 2026-07-07 (research): brain-structure->consumer re-map post-ingest-live -> notes/research_brain_structure_consumer_remap_post_ingest_live_2026-07-07.md -- CLS-consolidation classic interference-avoidance flavor REFUTED as an ingest consumer (discrete graph-store write, no shared weights, 2 lit-scans confirm); schema-extraction flavor deferred to Stage 4, not live; overall brain-component ranking UNCHANGED, top build stays cerebellar SR-rollout for basal-ganglia gate depth-degradation.
- resonator reachability ceiling: restart-budget problem at K=4 (p_basin~0.15, R~19 for 0.95), K-dependent wall (clustering/OGP) unresolved -> notes/research_resonator_reachability_ceiling_2026-07-07.md
- density x scale sweep design (m*(N) prediction for 970K GSBC retune): 3 lit-scans found no single closed-form law -- JL/Larsen-Nelson (mild ~14% growth), Willshaw/Palm (predicts ~halving), Knoblauch-Palm-Sommer (predicts ~2.7x growth); consistent with row-10 RESISTOR precedent. New finding: cross-seed CV on the already-landed marginpush data is U-shaped (tight at m5, wide at m3/m8) -- an early-warning cliff signature. Designed a cheap 4-rung adaptive sweep (50K/100K free, 177,899 existing, ~400K folds into Stage-3) with dual-form fitting + pre-registered validation. Marginal new cost ~30-50 min idle GPU. -> notes/research_density_scale_sweep_design_970k_extrapolation_2026-07-07.md

- 2026-07-07 (go/no-go scoping, multi-hop composition gap, 3-result synthesis): tested whether
  per-hop re-cleaning + the newly-unblocked encoder can close the N8/June-19 ConceptNet composition
  HARD_FAIL (substrate Hits@10=0.451 < BGE 0.502). REFUTED by direct code read: the June-19 cell
  ALREADY does hard per-hop argmax cleanup against the full entity codebook (`substrate_scores()`) --
  the "add re-cleaning" lever is not new, it was already running and lost. Root cause decomposed to
  TWO independent, lit-confirmed causes instead: (1) branching factor -- ConceptNet's transitive
  relations are high-out-degree "to-many" edges, and the cell uses single hard argmax (no beam),
  exactly the brittle configuration MINERVA/MultiHopKG literature flags (to-many relations degrade
  "regardless of model"; beam search is the standard fix, untried here); (2) representational
  asymmetry -- substrate entity codes are pure random RNG (zero semantic content) vs BGE's pretrained
  distributional semantics, a well-established (>10yr) asymmetry in the KG-completion literature that
  explains why even TRIVIAL (shallow) edges also lose (-0.405), not just deep ones. Also confirmed via
  code read that N8's own "36.5x" composition ratio is NOT contradictory evidence -- its 1-hop and
  frozen-encoder baselines are constructed-vacuous/weak by design. Proposed (not built) cheapest
  decisive cell: semantic-seeded entity codebook (from the CHAIN_GRADE-unblocked encoder) + top-k
  beam per hop, same bands/held-out split as June-19. P_deflated(full HARD-PASS)~0.15-0.20,
  P_deflated(MIDDLE-or-better)~0.40-0.45 -- legit cheap GO for exp_dev, MIDDLE pre-committed as modal
  expectation not a likely unlock. Refines the noise-compounding drill's reset/no-reset taxonomy with
  a 3rd regime (reset present + independent, but codebook high-branching + semantically-empty).
  -> notes/research_multihop_composition_gap_closure_scoping_2026-07-07.md. 11 external citations (9
  well-established, 2 recent preprints explicitly flagged low-confidence and not relied upon) + 10
  internal artifacts freshly re-read off-disk.

- 2026-07-07T(research, orthogonality capacity-lever scoping): scoped whether decorrelation/orthogonalization of stored codes is an active capacity lever (not just a passive N_eff measurement) -> notes/research_orthogonality_capacity_lever_density_cliff_2026-07-07.md. HEADLINE: two mechanistically distinct levers -- passive N_eff correction (already in use, log-compressed, ~1.5% effect) vs active frame-theoretic decorrelation (Welch bound / ETF / quasi-orthogonality, much larger ceiling but assumes free point placement, which our semantically-fixed codes are not). Dedup-retired-as-margin-fix finding (177K corpus, misses diffuse) does NOT refute the capacity-lever hypothesis: different corpus (177K barely has near-dup structure vs 970K's measured 15.86%) and different dependent variable (margin distribution at fixed m vs cliff location as V grows). Ranked levers: dedup near-dups (cheap, safe) > targeted whitening (conditional, needs test) > semantic-region code allocation (highest ceiling, most invasive, unscoped). Cheap test: fold a whitened-vs-baseline arm into the already-planned R1/R2 density-sweep rungs, zero new dispatch. Honest bound: full decorrelation is self-defeating for semantic retrieval (literature-confirmed, Mickus et al./Rudman-Eickhoff); sweet spot is targeting nuisance directions only (dedup, mean-centering), not full isotropy. P_deflated: passive effect not further deflated (closed-form); targeted-safe capacity gain 0.30-0.35; over-decorrelation-harms-retrieval 0.45-0.50; frame-theoretic large-ceiling gain 0.15-0.20 (weakest claim).
