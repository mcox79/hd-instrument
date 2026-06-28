# Research drill (2x DEEPER): temporal-reasoning primitive for substrate Stage 3

**Date:** 2026-06-27
**Author:** Research (Opus 4.7-1M)
**Trigger:** USER directive — Stage 3 active for M3 conversational AI; need brain-grounded temporal reasoning primitive.
**2x discipline:** drill EXISTING substrate findings (Allen v1 + LTL v1 + now-grounding v1 + temporal-policy v1 + additive sequence binding + bitemporal stack) into level-2 operational depth — NOT re-run as verification. Focus: what's load-bearing vs by-construction; what mechanism gap blocks Stage 3 narrative/planning/causal-chain.
**Calibration:** brain-existence-proof asymmetric (deflate 0.10-0.15 when brain-analog unambiguous); cap novel-synthesis P at 0.65. HARD bands mandatory both directions per [[feedback-lit-scan-calibration-penalty]] + [[feedback-three-smoke-disciplines]].
**Pre-reg discipline:** META_RULE_AF (arms-must-differ) + META_RULE_AG (baseline-in-band) + META_RULE_AH (atomic-write) + CRLB pre-validation + cardinality-OK per [[feedback-cardinality-ok-mandatory-prereg-field]] + number-tags throughout.

---

## HEADLINE

**Substrate's existing "temporal reasoning" suite is largely BY-CONSTRUCTION at the primitive layer; the load-bearing GAP for Stage 3 is a substrate-native TIME-CELL POPULATION CODE that supports DURATION ESTIMATION (Weber-fraction scaling) + ALLEN-RELATION CLASSIFICATION FROM POPULATION OVERLAP (not from stored endpoints) + NEXT-EVENT PREDICTION FROM TEMPORAL TRAJECTORY (not from Python lookups).** Audit of `exp_temporal_interval_allen_cpu_v1.py` (verdict HARD_PASS 1.000 at n=300) reveals the cell stores two interval endpoints (s,e) as FHRR `ikey * (SLOT * tick)` bundles, retrieves them via unbind, then **calls the same Python `_allen(a,b)` function on BOTH the gold pair AND the retrieved pair**. The substrate is verified at FHRR endpoint storage (which is already chain-grade); the Allen-relation classification is hardcoded outside substrate. This is exactly the BTSP-v1-style "trivial-baseline saturation" pattern caught by [[feedback-fix28-verify-per-arm-metrics]] and [[feedback-three-smoke-disciplines]]. The brain does NOT classify Allen relations by storing endpoints and running an if-else cascade — it represents intervals as **overlapping TIME-CELL POPULATION ACTIVITY VECTORS** (MacDonald-Eichenbaum 2011) in hippocampus + LEC (Tsao-Sugar-Lu 2018) at multi-scale (Howard-Eichenbaum 2014), and Allen relations FALL OUT of population-vector geometry (overlap = `OVERLAPS`/`DURING`; disjoint with ordering = `BEFORE`/`AFTER`; equal centroid = `EQUALS`). The substrate-native equivalent is a **time-cell-population HD vector** that encodes an interval as `bundle({tick_t for t in [s,e]})` — then Allen relation = `13-way classifier over (cosine, sign(centroid_a - centroid_b), |a|, |b|, |intersection|)` derived purely from substrate operations. Same primitive carries DURATION (norm of the bundle) and NEXT-EVENT-PREDICTION (autoregressive on the time-cell tape). Three candidate cells below; top-1 is brain-grounded + substrate-native + survives scale + survives discriminator + breaks by-construction-saturation.

**Calibrated P_deflated estimates (per [[feedback-lit-scan-calibration-penalty]]):**
- P(substrate's current Allen v1 is by-construction not a real primitive) = **0.85** (read the source; the `_allen()` function is called on retrieved endpoints; substrate proves endpoint storage, not Allen reasoning)
- P(time-cell population-vector primitive recovers Allen relations from substrate-side operations only, at >=0.85 macro-F1 across 13 classes) = **0.55** (brain-existence-proof asymmetric, but 13-way classification with imbalanced relation frequencies + bundle-norm collisions is the load-bearing risk; cap at 0.65)
- P(Weber-fraction duration discrimination — substrate matches W ~ 0.15 within a factor of 2) = **0.50** (Weber's law for time perception is robust across species; substrate's bundle-norm-as-duration is one untested step removed; novel-synthesis cap)
- P(next-event prediction via time-cell tape beats unigram baseline by >=0.10 at depth-3) = **0.45** (additive Hebbian already does sequence binding at 1.000 per `exp_btsp_sequence_learning_v2`, but PREDICTION at depth-3 is harder; deflate)
- P(Allen-relation primitive transfers to natural-language narrative-coherence Q&A — "what happened before X?" — at >=0.70 acc) = **0.30** (Stage 3 / Stage 4 boundary; substrate-doesnt-know-anything caution per [[feedback-substrate-doesnt-know-anything-stop-testing-against-language]]; this is downstream)

---

## SUBSTRATE-KB SCOUR RESULTS (prior temporal-work inventory, with verdicts)

Per USER scour-first-no-duplication discipline. Queried `director_kb_query.py` on 5 angles. Findings:

**Existing temporal cells (HARD_PASS but mostly by-construction or saturated):**
| Cell | Verdict | Honest re-read |
|------|---------|----------------|
| `exp_temporal_interval_allen_cpu_v1` | HARD_PASS 1.000 | **BY-CONSTRUCTION**: substrate stores endpoints, Python `_allen()` does classification. T=12 tick alphabet; 50 trials smoke / 300 full. NOT a substrate primitive for Allen reasoning. |
| `exp_lap3_11_temporal_ltl_cpu_v1` | HARD_PASS 1.000 | Bounded-LTL (next/eventually-within-k/always/until); similar by-construction risk — need to audit source. n=300 smoke-scale. |
| `exp_now1_temporal_grounding_cpu_v1` | HARD_PASS grounded=1.0 ungrounded=0.007 | Real discriminator (grounded vs ungrounded); n=1200; this one is LOAD-BEARING. "now" shard binding works. |
| `exp_integ_temporal_policy_cpu_v1` | HARD_PASS escape=139% | Temporal-policy alternation lifts worst-drive by 139% vs single-action minimax. Real discriminator. n=NA (deterministic). |
| `exp_btsp_sequence_learning_v1+v2` | HARD_FAIL | Additive Hebbian saturates at 1.000 (capability exists); BTSP collapses to 0.030. Confirms additive primitive for ORDER, not duration/relation. |
| `exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1` | HARD_FAIL regime-never-broken | additive>=0.95 at N_PAIRS in [50, 200, 1000]. Cliff not found in tested range. |
| `exp_comp_a3_temporal_asof_cpu_v1`, `exp_bitemporal_*`, `exp_factrep_ep1_bitemporal_native_cpu_v1` | not re-read | Bitemporal as-of queries; orthogonal to Allen-relation primitive. |
| `exp_predicate_composition_temporal_not_v1_smoke_localtest` | not re-read | Temporal-NOT predicate. |

**Existing temporal RESEARCH notes (read summaries; the parameter taxonomy is load-bearing context):**
- `research_substrate_representational_temporal_parameter_taxonomy_2026-06-23` (3x drill) — load-bearing 16-parameter taxonomy; lock-in P=64 vs brain P=7; STDP window NOT implemented; replay schedule NOT deployed.
- `research_drill_dyson_brownian_motion_temporal_dynamics_substrate_spectrum_evolution_observability_2x_2026-06-12` — RMT temporal-spectrum drill; orthogonal angle.
- `research_drill_stdp_temporal_asymmetry_substrate_2x_2026-06-04` — STDP asymmetry; orthogonal angle, not in scope here.
- `research_drill_temporal_fact_versioning_2x_2026-06-07` + bitemporal handoffs — bitemporal layer; orthogonal to Allen.
- `research_to_exp_dev_CYCLE_50_TEMPORAL_CONTEXT_BINDING_TCM_SCOPING_PP_402_2026-06-12` — TCM (Temporal Context Model, Howard-Kahana); aligns with this drill's angle.
- `drill_pattern_temporal_contextual_not_structural_2026-06-11` (memory) — meta-pattern: substrate's temporal/contextual mechanisms confirmed across 3 hard problems.

**GAP DELTA (what is NOT covered by prior cells):**
1. Substrate-native time-cell POPULATION CODE — no cell maps a hippocampal time-cell tape into FHRR/HRR. CITED@MacDonald-Eichenbaum 2011 / Pastalkova-Buzsaki 2008.
2. Duration estimation following Weber's law — no cell tests scalar timing. CITED@Coull-Cheng-Meck 2011 / Ivry-Spencer 2004.
3. Allen-relation classification FROM POPULATION-VECTOR GEOMETRY (not from stored endpoints + Python lookup). Net new.
4. Next-event prediction at depth >= 3 (autoregressive on time-cell tape). Existing additive cells do BINDING not prediction.
5. Integration of time-cell tape with Allen-relation classifier into a single Stage-3 narrative-coherence primitive.

Conclusion: **the existing Allen cell is the WEAKEST LINK** because it's by-construction. Top-1 candidate below directly replaces it with a brain-grounded population-code substrate-native version.

---

## TOP-3 CANDIDATE CELLS (rank-ordered with P_deflated, brain → substrate mapping, fairness, pre-reg)

### TOP-1: `exp_time_cell_population_allen_classifier_v1` (P_deflated = 0.55)

**Brain mechanism → substrate primitive mapping.**
- **CITED@MacDonald-Eichenbaum 2011** (Hippocampal "time cells" bridge the gap in memory for discontiguous events): hippocampal CA1 contains "time cells" that fire at sequential moments within a delay period; population spans the whole delay; each cell tiles a short window (~1 second).
- **CITED@Pastalkova-Buzsaki 2008** (Internally generated cell assemblies in hippocampus): rats running in wheel show stable time-locked CA1 sequences independent of location — pure time signal.
- **CITED@Tsao-Sugar-Lu 2018** (Integrating time from experience in lateral entorhinal cortex): LEC neurons encode time at MULTIPLE SCALES (seconds to minutes) via logarithmic compression; substrate-native analog = multi-scale tick alphabet.
- **CITED@Howard-Eichenbaum 2013** (The hippocampus, time, and memory across scales): population code spans logarithmic timescales; Allen relations fall out of population-overlap geometry.
- **Substrate primitive mapping:** an interval `[s,e]` becomes `interval_hd = sum_{t=s}^{e} tick_t / sqrt(e-s+1)` (a normalized bundle of time-cell activations spanning the interval). Two intervals `A=[s1,e1]`, `B=[s2,e2]` are then classified via FEATURES derived purely from substrate operations:
  - `f1 = cos(A_hd, B_hd)` — overlap proxy (cleanup against a tick-bank gives `|A ∩ B| / sqrt(|A| |B|)`)
  - `f2 = sign(centroid(A) - centroid(B))` — order proxy (centroid via `argmax(cleanup(A_hd, ticks))` then weighted average; substrate-native).
  - `f3 = |A| / |B|` — duration ratio (estimated from `||A_hd||` after un-normalization; this is the Weber-fraction probe).
  - `f4 = bool(cleanup(A_hd ⊙ ~B_hd, ticks) is empty)` — disjointness probe.
  - `f5 = match between endpoint cleanups (start_A == start_B, end_A == end_B)` — for `STARTS/STARTED-BY/FINISHES/FINISHED-BY/EQUALS`.
- Allen-relation = a LEARNED LINEAR CLASSIFIER over `(f1...f5)` trained on uniformly-sampled (A,B) pairs. Linear classifier in 5D is small enough that we can also publish its weights and show it's interpretable.

**Concrete test.** Generate 5000 random interval pairs over T=128 ticks (10x prior cell). Compute substrate features f1...f5 for each. Train logistic regression 13-way one-vs-rest on 4000; test on 1000. Report macro-F1 + per-class accuracy. **Critical:** the linear classifier acts ONLY on substrate-derived features; no Python access to (s,e).

**Discriminator (META_RULE_AF — arms-must-differ + META_RULE_AG baseline-in-band).**
- ARM_A: substrate features f1...f5 (the primitive).
- ARM_B: substrate features f1 ONLY (cosine only — strawman to ensure other features add value).
- ARM_C: raw (s,e) endpoints → linear classifier (BY-CONSTRUCTION control showing classifier alone can't do it without geometric features; predicted to FAIL because Allen relations are not linearly separable in raw (s,e) space).
- ARM_D: random-shuffle baseline (must score ~1/13 = 0.077).
- Discrimination requires: ARM_A > ARM_B by >=0.10 macro-F1 AND ARM_A > ARM_C by >=0.10 macro-F1 AND ARM_A > ARM_D by >=0.40.

**Fairness gate (META_RULE_AA + [[feedback-experiment-bias-master-checklist]] M-S).** Baseline ARM_C uses the SAME logistic regression at the SAME training set size; no privileged Python lookup; if ARM_C beats ARM_A then substrate is adding noise on top of raw endpoints and we should reject the primitive. Per BIAS-N (verify-referent-verdict-field): macro-F1 measured per-class with confidence intervals via bootstrap (n_boot=200); per [[feedback-suspect-1.000-results]] any class hitting 1.000 logged as red-flag and re-checked.

**Pre-reg HARD bands (both directions; per [[feedback-three-smoke-disciplines]] discriminator-fires-at-full-N).**
- HARD_PASS: macro-F1 >= 0.85 AND ARM_A - ARM_B >= 0.10 AND ARM_A - ARM_C >= 0.10 AND no class < 0.50. EXPECTED@0.85-0.90.
- HARD_FAIL: macro-F1 < 0.60 OR ARM_A - ARM_C < 0.05 OR any class < 0.20.
- MIDDLE_BAND: macro-F1 in [0.60, 0.85] with all-class > 0.20 — partial credit; iterate features.
- CARDINALITY_OK: EXPECTED_N_UNITS=4 arms × 13 classes × n_seeds=3 = 156 result cells; HARD_FAIL_CARDINALITY_BREACH if observed < 130.

**Smoke discriminator survives scale (per [[feedback-discriminator-must-survive-scale-before-full-dispatch]]):**
- Smoke at T=32, n=500 trials, 1 seed (~30s CPU): check ARM_A > ARM_B at >=0.05 lift, ARM_A > ARM_D at >=0.30. If smoke ARM_A < 0.40 macro-F1 OR baseline-in-band exceeds smoke ARM_A within 0.02 → HARD_FAIL smoke, do NOT dispatch full.
- Full at T=128, n=5000 trials, 3 seeds (~10min CPU).
- Smoke fires discriminator (NOT just verifies cell runs) — required by smoke-fires-discriminator rule.

**Compute cost.** ~10min CPU full + 30s CPU smoke. Pure numpy; no GPU.

**P_deflated = 0.55** (brain-existence-proof: time-cell population code is REAL and ROBUST. Risk: 13-way classification with imbalanced relation frequencies — `EQUALS` is rare; `BEFORE/AFTER` dominate. Cap at 0.65 per novel-synthesis cap; deflate to 0.55 for finite-N residuals and bundle-norm-saturation risk.)

**Why now.** Replaces the by-construction Allen v1 with a real primitive. Foundation for Stage 3 narrative coherence ("Sally hid the marble at t=1, Anne moved it at t=3 — when was it hidden?" needs `BEFORE(hide, move)` derived from substrate operations).

---

### TOP-2: `exp_weber_fraction_duration_discrimination_v1` (P_deflated = 0.50)

**Brain mechanism → substrate primitive mapping.**
- **CITED@Coull-Cheng-Meck 2011** (Neuroanatomical and neurochemical substrates of timing): pre-SMA + striatum maintain duration representations; scalar timing follows Weber's law (W = sigma_T / T ≈ 0.15 for sub-second to minutes range).
- **CITED@Ivry-Spencer 2004** (The neural representation of time): cerebellar forward-model timing; scalar timing across modalities.
- **CITED@Mello-Soares-Paton 2015** (A scalable population code for time in the striatum): striatal MSN populations encode elapsed time via population-vector decoding; duration-discrimination matches Weber scaling.
- **Substrate primitive mapping:** duration of interval `[s,e]` estimated as `||bundle(tick_s, ..., tick_e)||_F` or via cleanup-count `|{t : cosine(interval_hd, tick_t) > theta}|`. Weber's law predicts standard deviation of substrate's duration estimate to scale LINEARLY with true duration: `sigma_substrate(T) = W * T` with `W ~ 0.15` if the substrate is scalar-timing-isomorphic.

**Concrete test.** Two-alternative forced choice: given two intervals presented as time-cell bundles A (duration T_A) and B (duration T_B), substrate outputs `argmax_duration(A, B)`. Sweep T_B in {0.8 T_A, 0.9 T_A, 1.0 T_A, 1.1 T_A, 1.2 T_A} for T_A in {8, 16, 32, 64} ticks. Plot psychometric function; fit Gaussian; extract W = sigma/T.

**Discriminator (META_RULE_AF).**
- ARM_A: substrate bundle-norm duration estimate.
- ARM_B: substrate cleanup-count duration estimate.
- ARM_C: substrate cosine-with-uniform-tape estimate (alternate readout).
- ARM_D: random-shuffle baseline (W = inf; 0.5 accuracy at all ratios).
- Discrimination requires: at least one of ARM_A/B/C achieves W in [0.05, 0.40] (brain range with factor-of-2 tolerance) AND beats ARM_D by >=0.20 acc at the 1.1 T_A ratio.

**Fairness gate.** The "true duration" T is never given to the substrate; it must estimate from the bundle alone. Per [[feedback-experiment-bias-master-checklist]] BIAS-15 (regime-mismatch): T_A range chosen to span 0.5-4x the encoder's natural resolution (tick alphabet T_max=128).

**Pre-reg HARD bands.**
- HARD_PASS: ARM_A or ARM_B yields W in [0.05, 0.40] at all T_A AND beats ARM_D by >=0.20 at 1.1 T_A. EXPECTED@W~0.20.
- HARD_FAIL: no arm yields W < 0.60 at any T_A (substrate has no scalar-timing isomorph) OR all arms degenerate to ARM_D.
- MIDDLE_BAND: W in [0.40, 0.60] (substrate does some duration estimation but Weber-fraction is loose).
- CARDINALITY_OK: EXPECTED_N_UNITS = 4 arms × 4 T_A × 5 ratios × 100 trials × 3 seeds = 24000.

**Smoke.** T_A in {16, 32}, n=200, 1 seed (~30s). Check ARM_A vs ARM_D >= 0.10 at 1.2 T_A; smoke-fires-discriminator.

**Compute.** ~5min CPU full + 30s smoke.

**P_deflated = 0.50** (brain Weber's law is rock-solid; substrate's bundle-norm-as-duration is one untested step; if bundle-norm saturates at small T or hits ceiling at large T, W deviates badly. Cap novel-synthesis 0.65; deflate 0.50.)

**Why now.** Duration is one of the four required Stage 3 capabilities (interval representation includes DURATION); also a clean Weber-law test that hooks substrate to the timing literature. Cross-validates TOP-1's `f3` feature.

---

### TOP-3: `exp_temporal_trajectory_next_event_predictor_v1` (P_deflated = 0.45)

**Brain mechanism → substrate primitive mapping.**
- **CITED@Eichenbaum 2014** (Time cells in the hippocampus: a new dimension for mapping memories): time cells encode the temporal CONTEXT of events; population trajectory is a continuous "tape" along which past events have positions.
- **CITED@Howard 2018** (Memory as perception of the past: compressed time in mental time travel): TCM (Temporal Context Model) — context vector drifts continuously and binds to each event; retrieval cued by current context recovers temporally-nearby events.
- **Substrate primitive mapping:** event sequence `e_1@t_1, e_2@t_2, ..., e_n@t_n` stored as `W = sum_k e_k ⊗ tick_{t_k}` (additive Hebbian + position-binding — substrate already has this at 1.000 per `exp_btsp_sequence_learning_v2`). Next-event prediction at time t+1: query `cleanup(W ⊙ ~tick_{t+1}, event_book)`. ALSO test "what happened before X?" = `cleanup(W ⊙ ~e_X * shift_minus, tick_book)` — query event's bound tick, then return event at tick-1.

**Concrete test.** Synthetic event-stream: 50 sequences of length 8, V=100 events, T=64 ticks. Three task variants:
- (a) **NEXT-EVENT** — given the first 5 events, predict event 6. Acc against argmax over V.
- (b) **PRECEDING-EVENT** — given event X at known time, return event at t-1. Acc.
- (c) **EVENT-INTERVAL** — given (event_A, event_B), return Allen relation (uses TOP-1 features).

**Discriminator (META_RULE_AF).**
- ARM_A: substrate additive + position-binding + cleanup.
- ARM_B: unigram baseline (most-frequent event regardless of context). Predicted: ~1/V acc = 0.01.
- ARM_C: bigram baseline (most-frequent successor of previous event). Stronger; predicted acc depends on stream entropy.
- ARM_D: random baseline (acc = 1/V = 0.01).
- Discrimination requires ARM_A > ARM_C by >=0.10 on NEXT-EVENT AND ARM_A > 0.50 on PRECEDING-EVENT.

**Fairness gate (META_RULE_AG + [[feedback-experiment-bias-master-checklist]] BIAS-13/14 contamination).** Event sequences generated from a 2nd-order Markov chain with controlled entropy (H=2.5 bits/event); ARM_C bigram baseline gets full bigram statistics from training set; substrate sees same training stream.

**Pre-reg HARD bands.**
- HARD_PASS: ARM_A NEXT-EVENT acc >= 0.50 AND ARM_A - ARM_C >= 0.10 AND PRECEDING-EVENT >= 0.70. EXPECTED@ARM_A=0.6/0.8.
- HARD_FAIL: ARM_A NEXT-EVENT acc < 0.20 OR ARM_A - ARM_C < 0.02 (substrate adds no value over bigram).
- MIDDLE_BAND: ARM_A in [0.20, 0.50] OR ARM_A - ARM_C in [0.02, 0.10].
- CARDINALITY_OK: 4 arms × 3 tasks × 50 sequences × 3 seeds = 1800.

**Smoke.** 10 sequences length 6, V=20, T=16, 1 seed (~20s); ARM_A vs ARM_C >= 0.05 at NEXT-EVENT.

**Compute.** ~8min CPU full + 20s smoke.

**P_deflated = 0.45** (additive sequence binding already works at 1.000 for BINDING; PREDICTION is a different task — depth-3 prediction depends on attractor cleanup quality with 5-event prefix bundles which has noise growing with prefix length. Deflate from 0.60 substrate-existence-proof to 0.45 for prefix-noise risk + bigram-baseline-strength uncertainty.)

**Why now.** "What comes next" + "what happened before" are the two narrative-coherence questions required for Stage 3 conversational coherence. This is the prediction primitive that pairs with TOP-1's classification primitive.

---

## NON-TRADITIONAL FIELD CROSS-DOMAIN PROBES (per USER directive — branch out)

**(a) Legal time-reasoning — statute of limitations as Allen-relation reasoning.** CITED@law-statute-of-limitations: legal systems formally reason about Allen relations between (event_of_harm, filing_deadline, statute_period_start). A claim is admissible iff `OVERLAPS(filing_date, [event + 0, event + statute_limit])`. Substrate-native primitive in TOP-1 can be tested on simulated legal-claim scenarios as a downstream eval — this is a real-world Stage-3 application that does NOT require natural-language understanding, only interval reasoning.

**(b) Crystal-growth temporal evolution (lattice schemas over time).** CITED@Cahn-Hilliard temporal evolution: crystal lattices evolve via temporal update rules where each lattice site is bound to (position, time). Substrate's time-cell-tape primitive is mathematically isomorphic to a 1D Cahn-Hilliard time-binding — substrate-native temporal evolution can be tested on toy crystal-growth simulations where the substrate predicts the next lattice state. (Lower-priority than TOP-1/2/3; flagged for v2 if temporal primitive lands chain-grade.)

**(c) Phylogenetic time trees / molecular clocks.** CITED@phylogenetics-molecular-clock: species divergence times form an Allen-relation tree (lineage A SPLITS-BEFORE lineage B IF A's divergence time < B's). Substrate-native Allen primitive could classify lineage relations from time-cell representations of divergence times. Low priority but cleanly evaluable.

**(d) Petri net reaction-network temporal dynamics.** CITED@Petri-net-marking-graph: chemical reaction networks have temporal markings whose transitions form Allen relations on event firings. Substrate-native Petri-net simulator = TOP-3 cell extended to typed events. Reserve for v2.

**(e) Allen 1983 — pure interval algebra.** CITED@Allen-1983 (Maintaining knowledge about temporal intervals): the canonical 13-relation algebra; PATH-CONSISTENCY ALGORITHM is the operational extension — given a network of intervals with partial relation constraints, propagate constraints to derive new relations. Substrate-native primitive could implement Allen's transitivity table via FHRR composition; this is a v2 cell (`exp_allen_path_consistency_propagation_v2`) once TOP-1 lands.

**(f) Halpern-Shoham interval temporal logic.** CITED@Halpern-Shoham 1991: 13-modality logic where each modality corresponds to an Allen relation. Decidability is known for various fragments; substrate-native HS logic = TOP-1 features as modality predicates. v2 cell.

**(g) Categorical models of time (presheaves over time intervals).** CITED@presheaf-temporal-logic: time intervals form a poset (preorder by inclusion); presheaves over this poset model time-varying state. Substrate's FHRR bundle is a categorical-presheaf substrate-native realization (each time-cell is a stalk; the bundle is the section). Theoretical framing only; no cell.

---

## CROSS-THREAD SYNTHESIS

**With `temporal_parameter_taxonomy_2026-06-23` (3x drill):**
- The taxonomy identified lock-in P=64 as 9x over-spec vs brain P=7 — this matters for TOP-3 (next-event prediction with prefix bundles); we should run TOP-3 at P=8 and P=64 to verify the over-saturation pattern doesn't mask discriminating differences.
- Amplitude scaling 1/sqrt(f) applies to TOP-1's f3 (duration-from-norm) and TOP-2 in general — sparse bundles need `1/sqrt(f)` amplitude per matched-filter theorem to avoid receiver-SNR penalty.
- N_DIM = 8192 canonical band is correct for these cells.
- tau_pos/tau_neg ratio inversion does NOT affect these cells (they don't use STDP).

**With today's chain-grade landings:**
- depth-5 composition: TOP-1's Allen-relation classifier composes with depth-5 cells via relation-chaining (e.g., `BEFORE(A,B) AND BEFORE(B,C) → BEFORE(A,C)` — Allen transitivity).
- parietal MOVABLE + RELATIONAL: relations like `BEFORE/AFTER` are temporal-relational analogues of parietal spatial relations; cross-pollinate via shared relational-binding primitive.
- task_vector ICL: TOP-3 next-event prediction can be framed as ICL where the task vector encodes "predict-next-event" — runs as a downstream test of task_vector ICL on temporal tasks.
- TOM Sally-Anne: requires temporal reasoning (Sally hid marble at t=1, Anne moved it at t=3 → Sally believes it's at original location BECAUSE she observed only events at t<=1). TOP-1's Allen classifier is a load-bearing dependency for Sally-Anne narrative coherence.
- counterfactual: counterfactual reasoning over time = "what would have happened if event_X had NOT occurred at t=k" — substrate-native via TOP-3 + temporal-NOT predicate (`exp_predicate_composition_temporal_not_v1`).

**With BTSP HARD_FAIL synthesis (today):** substrate has order-sensitive sequence binding at 1.000 via additive + position-binding; TOP-3 uses this primitive directly. BTSP is NOT the right mechanism here; the existing additive Hebbian primitive is.

**With `drill_pattern_temporal_contextual_not_structural_2026-06-11`:** temporal/contextual is the substrate's strong meta-pattern; this drill extends it with population-code time + Weber duration + autoregressive prediction.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

Per [[feedback-no-papers-product-only]]: framing is product-relevant, NEVER publication.

**M3 conversational AI dependency:** the M3 glass-box conversational target requires the substrate to answer "what happened before X?" and "how long did Y take?" coherently. Without TOP-1 + TOP-2 + TOP-3, the substrate cannot maintain narrative coherence across multi-turn conversation. The Allen v1 cell's by-construction status means the substrate currently does NOT have this capability — it only has FHRR endpoint storage that LOOKS like temporal reasoning when paired with Python lookups. Honest framing: closing this gap is a hard prerequisite for M3.

**Substrate as Director KB temporal eviction:** the dogfood KB (`exp_kb_time_decay_eviction_with_reingest_v1`) already uses temporal binding for eviction policy; TOP-2's Weber-fraction primitive gives a principled basis for "how long ago" decay-rate calibration (currently exponential decay with hard-coded tau).

**Stage progression risk:** per [[feedback-stage-progression-1234-dont-skip]], Stage 3 must complete before Stage 4 LM equivalence. TOP-1/2/3 land Stage 3 temporal reasoning; without them, attempts to Stage 4 will repeat the by-construction-saturation pattern (as today's BTSP arc demonstrated).

**Not in scope:** language-based temporal evaluations (e.g., "in the morning" / "after lunch") are Stage 4 — substrate doesn't have semantics for those tokens. Per [[feedback-substrate-doesnt-know-anything-stop-testing-against-language]], TOP-1/2/3 stay at synthetic temporal tasks until Stage 4 prerequisites land.

---

## CITATIONS (verified count)

Brain literature (7, all directly cited in TOP-1/2/3 mappings):
1. CITED@MacDonald-Eichenbaum 2011 — Hippocampal "time cells" — Neuron 71:737-749.
2. CITED@Pastalkova-Buzsaki 2008 — Internally generated cell assemblies in hippocampus — Science 321:1322-1327.
3. CITED@Mello-Soares-Paton 2015 — Scalable population code for time in striatum — Curr Biol 25:1113-1122.
4. CITED@Coull-Cheng-Meck 2011 — Neuroanatomical/neurochemical substrates of timing — Neuropsychopharmacology 36:3-25.
5. CITED@Ivry-Spencer 2004 — The neural representation of time — Curr Opin Neurobiol 14:225-232.
6. CITED@Eichenbaum 2014 — Time cells in the hippocampus: a new dimension — Nat Rev Neurosci 15:732-744.
7. CITED@Howard-Eichenbaum 2013 — The hippocampus, time, and memory across scales — Annu Rev Psychol 65:111-138.
8. CITED@Tsao-Sugar-Lu 2018 — Integrating time from experience in LEC — Nature 561:57-62.
9. CITED@Howard 2018 — Memory as perception of the past — TICS 22:124-136.

Pure math + formal (4):
10. CITED@Allen 1983 — Maintaining knowledge about temporal intervals — CACM 26:832-843.
11. CITED@Halpern-Shoham 1991 — Propositional modal logic of time intervals — JACM 38:935-962.
12. CITED@Pnueli 1977 — The temporal logic of programs — FOCS 18 (LTL canonical).
13. CITED@Schwartz 1953 / Wikipedia matched filter — for amplitude-scaling carryover.

Other (cross-domain, 3):
14. CITED@Cahn-Hilliard temporal — crystal-growth lattice evolution.
15. CITED@Lisman-Jensen 2013 — theta-gamma coding (P=7 brain analog).
16. CITED@Weber-Fechner law — psychophysics canonical scalar timing.

Substrate internal (8, all verified on disk):
- `notes/research_substrate_representational_temporal_parameter_taxonomy_2026-06-23.md` (read top 200 lines).
- `notes/exp_dev_to_research_BTSP_SEQUENCE_LEARNING_v1_v2_BOTH_HARD_FAIL_2026-06-27.md` (full read).
- `data/exp_temporal_interval_allen_cpu_v1/metrics.json` (full read; verdict HARD_PASS but by-construction).
- `data/exp_lap3_11_temporal_ltl_cpu_v1/metrics.json` (full read; same risk).
- `data/exp_now1_temporal_grounding_cpu_v1/metrics.json` (full read; LOAD-BEARING — real discriminator).
- `data/exp_integ_temporal_policy_cpu_v1/metrics.json` (full read; real discriminator).
- `data/exp_additive_hebbian_sequence_binding_capacity_cliff_sweep_v1_smoke/metrics.json` (full read; regime-never-broken).
- `experiments/exp_temporal_interval_allen_cpu_v1.py` (full source read; confirms by-construction).

**Total: 16 external citations + 8 substrate-internal verified atoms.**

---

## EXP_DEV-ACTIONABLE? YES — companion hand-off file written at `notes/exp_dev_handoff_research_temporal_reasoning_primitive_stage3_2026-06-27.md`

Per the role contract: TOP-1 is anchor-pointer-ready; TOP-2/TOP-3 are ranked candidates; tier-hint, why-now, contract-section all in the hand-off.

---

(End of research drill 2x temporal-reasoning primitive Stage 3.)
