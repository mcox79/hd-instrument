# exp_dev hand-off — research: CORTEX 4x cross-discipline selective-abstraction drill

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** 4x cross-disciplinary REVIVAL drill on FIVE failed CORTEX content-extraction cells; parent note `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md`. Unifying diagnosis: substrate lacks a per-atom IMPORTANCE signal independent of weight magnitude; 4 disciplines converge on the same answer (importance must be a SEPARATE TENSOR, not read off W).
**Supersedes within-scope:** Section 5 of `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` (M5 STC was refuted by `exp_gap4_stc_capture_selective_downscale_v1` HARD_FAIL).

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off and DO NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS not full cell specs. exp_dev authors cells per substrate-physics. Pre-reg bands LOAD-BEARING — bake into prereg verbatim.

## Pivot frame (mandatory context — USER 2026-06-26)

Substrate has NO understanding of language. We are NOT testing language prediction. We ARE testing whether substrate can build COMPOSITIONAL UNDERSTANDING via:
- bounded continual ingest (preserves old atoms while accepting new ones)
- selective abstraction (extracts compositional structure from co-occurrence)
- type-aware composition (refuses incompatible compositions rather than confabulating)

text8 / BPC / bigram-gap are NOT relevant evals. The eval for THESE anchors is RECALL on old atoms + EFFECTIVE CAPACITY + (for Anchor 2) CLUSTER-REPRESENTATIVE FIDELITY.

## Anchor candidates (rank-ordered)

### ANCHOR 1 (TOP PRIORITY): excitability_allocation_separate_tensor_v1

- **Anchor pointer:** `experiments/exp_excitability_allocation_separate_tensor_v1.py` (new cell; substrate-native)
- **Substrate-product reading:** "Add a separate per-atom EXCITABILITY tensor E[i] updated ORTHOGONALLY from W; downscale / replace operations gated on E[i], NOT on |W[i]|. E updates on retrieval hits (EWMA boost) and decays slowly. This is the missing CREB-analog brain primitive — selectivity is upstream of plasticity. Discriminator: at J=2500 cycles continual ingest (matching Cell B / STC regime), recall_on_first_100_atoms >= 0.60 AND recall_on_recent >= 0.85 AND bounded ||W||_F"
- **Cross-discipline composition tags:** BIOLOGY (CREB excitability allocation; PKMzeta maintenance) + PURE MATH (information bottleneck side-information Y; K-SVD usage counter) + BRAIN (engram-allocation literature Josselyn-Frankland-Tonegawa)
- **Tier hint:** chain-grade-eligible IF recall_old>=0.60 AND recall_recent>=0.85 AND ||W||_F bounded AND cv<=0.05; MIDDLE_BAND if recall_old in 0.30-0.60 OR recall_recent in 0.60-0.85; HARD_FAIL if recall_old<0.30 (matches Cell B failure mode — E tensor didn't actually preserve right atoms) OR E[i] correlates too strongly (>0.9) with |W[i]| (E is just magnitude proxy, no new signal)
- **P_deflated:** **0.45** (deflated from 0.65 raw; brain-grounded mechanism most clearly missing; engram-allocation lit is robust; main risk is substrate retrieval-hit signal too weak)
- **Why now:** addresses SHARED ROOT CAUSE of 3/5 failed cells (STC tagging, Cell B global downscale, cold-storage migration) — all needed per-atom importance signal that doesn't exist in substrate today
- **Composition with existing chain-grade primitives:**
  - `hdlab/cleanup_memory.py` (hook retrieval log to drive E updates)
  - existing TWO_TIER architecture (`exp_gap4_two_tier_generational_W_v1` HARD_PASS) — E becomes the PROMOTION CRITERION (currently TWO_TIER uses recall-similarity; E gives bounded utility-based promotion)
  - existing NREM replay (`exp_substrate_continual_NREM_replay_v1` HARD_PASS) — replay strengthens high-E atoms preferentially
  - refuse-gate primitive — novelty signal feeds initial E for new atoms
- **NEW PRIMITIVE to author:** `hdlab/excitability.py` — per-atom E[i] tensor (float32, shape [num_atoms]); EWMA update on retrieval hits; decay rule; exposed to continual.py for E-gated downscale
- **Arms (3 mandatory minimum):**
  - ARM_BASELINE_NO_EXCITABILITY (reproduce Cell B failure baseline at matching regime; sanity rail)
  - ARM_E_GATED_DOWNSCALE (downscale only atoms with E[i] < e_thresh)
  - ARM_RANDOM_GATED_DOWNSCALE (downscale random subset of same size as E-gated; control for "selectivity matters" vs "magnitude-fraction matters")
- **Pre-reg bands (load-bearing; exp_dev refines specifics):**
  - HARD_PASS: recall_old>=0.60, recall_recent>=0.85, ||W||_F bounded by some explicit ceiling (exp_dev picks based on N), cv<=0.05 [P=0.30]
  - MIDDLE_BAND: recall_old 0.30-0.60 OR recall_recent 0.60-0.85 [P=0.45]
  - HARD_FAIL: recall_old<0.30 OR cor(E, |W|) > 0.9 OR ARM_E_GATED indistinguishable from ARM_RANDOM_GATED [P=0.25]
- **Smoke gate:** at J=500 cycles N=2048, E tensor updates correctly on synthetic retrieval log (round-trip test); E decays as expected; gating function flips atom inclusion based on E threshold; zero LLM calls AUDIT logged
- **Cost estimate:** ~3-5 CPU-hr local_cpu_queue (3 seeds; per-cycle overhead ~5-10% above no-E baseline)
- **Queue:** local_cpu_queue (CAN FIRE TODAY post-orchestrator routing)
- **What this teaches us:** if HARD_PASS, substrate has the missing CREB-analog primitive and 3/5 failed cells become re-runnable with new gating; if HARD_FAIL, selectivity-via-separate-tensor is also insufficient and substrate's continual-learning architecture needs deeper change

---

### ANCHOR 2: ultrametric_clustering_coarse_grain_atoms_v1

- **Anchor pointer:** `experiments/exp_ultrametric_clustering_coarse_grain_atoms_v1.py` (new cell)
- **Substrate-product reading:** "Detect atom clusters via ultrametric distance on W rows; collapse clusters with within-cluster cosine > 0.85 AND size>=5 to representative atom (cluster centroid) + residual codes. This is substrate-native RG coarse-graining = the missing COMPOSITIONAL-ABSTRACTION primitive. Discriminator: at J=5000 cycles, capacity_used drops by >=20% with recall_on_clustered_concepts >= 0.80 via cluster representative AND recall_on_unclustered >= 0.85"
- **Cross-discipline composition tags:** MATERIALS (spin glass ultrametric tree; metastable basin hierarchy) + PURE MATH (RG/Mehta-Schwab variational RG; persistent homology stability of clusters) + BRAIN (schema-fast-track; Tse-Morris consolidated clusters = schemas)
- **Tier hint:** chain-grade-eligible IF capacity_drop>=20% AND recall_clustered>=0.80 AND recall_unclustered>=0.85 AND cv<=0.05; MIDDLE_BAND if capacity_drop 5-20% with recall_clustered 0.50-0.80; HARD_FAIL if recall_clustered<0.50 (collapse destroyed information) OR no clusters detected (ultrametric structure absent)
- **P_deflated:** **0.40** (deflated from 0.55 raw; mathematically clean but cluster-representative-via-mean is approximation; HRR-bind composition might be wrong primitive for cluster representation)
- **Why now:** addresses compositional-extraction failure (`cortical_schema_extraction` Cell 1 MIDDLE_BAND — capability-based schema HURT performance because capability-relations weren't being properly composed). Ultrametric clustering FINDS latent compositional structure substrate already has but isn't extracting.
- **Composition with existing chain-grade primitives:**
  - `hdlab/cleanup_memory.py` (W matrix is the basin landscape input to ultrametric distance)
  - `hdlab/binding.py` (HRR composition for cluster representative experimentation)
  - existing FB15k-237 / ConceptNet KG ingest (cells should already have natural clusters by relation-type)
- **NEW PRIMITIVE to author:** `hdlab/ultrametric_clustering.py` — compute ultrametric distance matrix on W rows; agglomerative single-linkage cluster; collapse cluster to representative atom + 1-of-K code
- **Arms (3 mandatory minimum):**
  - ARM_NO_COLLAPSE (baseline — substrate runs without clustering; sanity rail)
  - ARM_ULTRAMETRIC_COLLAPSE (proposed mechanism)
  - ARM_RANDOM_CLUSTER_COLLAPSE (control — random equal-size clusters collapsed; tests whether STRUCTURE matters vs CAPACITY-REDUCTION matters)
- **Pre-reg bands:**
  - HARD_PASS: capacity_used drops >=20%, recall_clustered>=0.80 via centroid, recall_unclustered>=0.85, cv<=0.05 [P=0.25]
  - MIDDLE_BAND: capacity_drop 5-20%, recall_clustered 0.50-0.80 [P=0.40]
  - HARD_FAIL: recall_clustered<0.50 OR no clusters detected (substrate has no ultrametric structure to exploit) OR ARM_ULTRAMETRIC indistinguishable from ARM_RANDOM_CLUSTER [P=0.35]
- **Smoke gate:** at J=500 cycles N=2048, ultrametric distance matrix computes correctly on 200 atoms; single-linkage agglomerative produces sensible clusters on synthetic test where 50 atoms are explicitly 5 clusters of 10 with within-cluster cosine=0.9; collapse produces correct number of representatives; zero LLM AUDIT
- **Cost estimate:** ~4-6 CPU-hr local_cpu_queue (clustering O(N^2) on atom count; substrate-typical N_atoms ~1000-10000 is tolerable)
- **Queue:** local_cpu_queue (dispatch parallel with Anchor 1)
- **What this teaches us:** if HARD_PASS, substrate has the missing compositional-abstraction primitive AND ultrametric structure is present in W (validates spin-glass theoretical frame); if HARD_FAIL with no clusters, substrate W doesn't have the spin-glass basin structure assumed and theoretical frame is wrong; if HARD_FAIL with cluster_recall_destruction, cluster-representative-via-mean is wrong primitive

---

### ANCHOR 3: SOC_critical_write_rate_avalanche_v1

- **Anchor pointer:** `experiments/exp_SOC_critical_write_rate_avalanche_v1.py` (new cell)
- **Substrate-product reading:** "Self-organized criticality frame: each write triggers per-atom capacity check; over-saturated atoms AVALANCHE by redistributing excess to top-K nearest neighbors via heterosynaptic depression; tune write-rate to critical regime where avalanche-size distribution becomes scale-free (power-law slope ~-3/2 BTW universality). Discriminator: at J=5000 cycles, avalanche-size distribution KS-test against power-law p>0.05 AND recall_on_old>=0.50 AND ||W||_F bounded WITHOUT explicit downscale"
- **Cross-discipline composition tags:** MATERIALS (Bak-Tang-Wiesenfeld sandpile SOC + percolation phase transition) + BIOLOGY (heterosynaptic competition; STDP-BCM) + PURE MATH (RG framework for scale-free dynamics)
- **Tier hint:** chain-grade-eligible IF scale-free distribution KS p>0.05 AND recall_old>=0.50 AND ||W||_F bounded AND cv<=0.05; MIDDLE_BAND if heavy tail but not pure power-law, recall_old 0.30-0.50; HARD_FAIL if heterosynaptic depression destroys old atoms (recall_old<0.20) OR no avalanche dynamics emerge
- **P_deflated:** **0.30** (deflated from 0.45 raw; high implementation risk because substrate's continuous-valued W differs from BTW's integer-valued sandpile; novel-synthesis ceiling enforced)
- **Why now:** most theoretically elegant; tests UNIFIED frame (substrate IS a sandpile, just needs to find criticality). Worth running ALONGSIDE Anchor 1 to discriminate "explicit selectivity needed" vs "emergent criticality sufficient."
- **Composition with existing chain-grade primitives:**
  - `hdlab/cleanup_memory.py` (top-K nearest for redistribution)
  - `hdlab/continual.py` (write hook for avalanche check)
- **NEW PRIMITIVE to author:** `hdlab/avalanche_dynamics.py` — detect over-saturation (||W_i||>c*threshold); redistribute excess via heterosynaptic depression; track avalanche-size distribution + fit power-law slope
- **Arms (3 mandatory minimum):**
  - ARM_NO_AVALANCHE (baseline at multiple write-rates; sanity rail)
  - ARM_AVALANCHE_AT_CRITICAL_RATE (proposed mechanism at tuned write-rate)
  - ARM_AVALANCHE_AT_SUBCRITICAL_RATE (proposed mechanism at lower write-rate — should give exponential-not-power-law avalanche dist)
- **Pre-reg bands:**
  - HARD_PASS: power-law fit p>0.05, slope in [-1.7, -1.3], recall_old>=0.50, ||W||_F bounded, cv<=0.05 [P=0.20]
  - MIDDLE_BAND: heavy-tail but not power-law, recall_old 0.30-0.50 [P=0.35]
  - HARD_FAIL: recall_old<0.20 OR no avalanche events triggered (substrate too far below critical) [P=0.45]
- **Smoke gate:** at J=500 cycles N=2048, avalanche detection fires correctly on synthetic over-saturated atom; redistribution rule preserves total ||W||; cascade depth measurable; zero LLM AUDIT
- **Cost estimate:** ~4-6 CPU-hr local_cpu_queue
- **Queue:** local_cpu_queue (dispatch parallel with Anchor 1 if budget; otherwise after Anchor 1)
- **What this teaches us:** if HARD_PASS, substrate operates at criticality and homeostasis is EMERGENT not enforced (powerful substrate-product story); if HARD_FAIL, substrate's continuous-W is structurally different from sandpile and SOC frame doesn't translate

---

### ANCHOR 4: MDL_dictionary_turnover_atom_replacement_v1

- **Anchor pointer:** `experiments/exp_MDL_dictionary_turnover_atom_replacement_v1.py` (new cell)
- **Substrate-product reading:** "Per-atom MDL bits-saved metric (cleanup-hit log-likelihood approximation); every J_turnover cycles REPLACE bottom-5% atoms with either fresh random direction sampled near recent OOD inputs (50%) OR bound composition of top-2 most-frequently-co-retrieved atoms (50%). This converts unused atoms into novel-direction-probes or schema-anchors. Discriminator: at J=5000 cycles, effective_capacity (distinct retrievable concepts at fixed N) >= 1.5x baseline AND recall_top1 >= 0.85"
- **Cross-discipline composition tags:** PURE MATH (K-SVD dictionary learning + sparse-coding usage counter; MDL principle bits_saved vs bits_cost; persistent homology birth-death persistence) + BIOLOGY (glial pruning as long-timescale capacity reset)
- **Tier hint:** chain-grade-eligible IF effective_capacity >= 1.5x AND recall_top1 >= 0.85 AND cv<=0.05; MIDDLE_BAND if effective_capacity 1.1-1.5x; HARD_FAIL if turnover damages recall (recall_top1<0.50) OR no atoms qualify for turnover
- **P_deflated:** **0.40** (deflated from 0.55 raw; MDL approximation has theoretical risk in bits-saved estimator; bound-composition replacement is novel substrate operation)
- **Why now:** addresses "infinite W growth" differently from Anchor 1 — explicit replacement vs gated downscale. Complementary to Anchor 2 (Anchor 2 collapses clusters; Anchor 4 turns over individual atoms). Dispatch after Anchors 1+2 give signal on whether per-atom selectivity OR cluster-level coarse-graining is the right level.
- **Composition with existing chain-grade primitives:**
  - `hdlab/cleanup_memory.py` (hit log for usage counter)
  - `hdlab/atoms.py` (atom replacement / re-binding)
  - refuse-gate (OOD detection for novel-direction-probe seeding)
- **NEW PRIMITIVE to author:** `hdlab/mdl_turnover.py` — per-atom usage counter U[i] (EWMA); per-atom bits-saved estimator B[i] via cleanup-hit log-likelihood; atom replacement policy (random/bound-composition split)
- **Arms (3 mandatory minimum):**
  - ARM_NO_TURNOVER (baseline; sanity rail)
  - ARM_MDL_TURNOVER (proposed mechanism)
  - ARM_RANDOM_TURNOVER (control — same fraction of atoms replaced with fresh random; tests whether MDL CRITERION matters vs TURNOVER ITSELF helps)
- **Pre-reg bands:**
  - HARD_PASS: effective_capacity>=1.5x, recall_top1>=0.85, cv<=0.05 [P=0.25]
  - MIDDLE_BAND: effective_capacity 1.1-1.5x [P=0.45]
  - HARD_FAIL: recall_top1<0.50 OR B-U metrics too flat to discriminate atoms (no turnover candidates) [P=0.30]
- **Smoke gate:** at J=500 cycles N=2048, U/B per-atom metrics update correctly on synthetic retrieval log; replacement preserves dimension; bound-composition replacement produces correct linear combination; zero LLM AUDIT
- **Cost estimate:** ~4-6 CPU-hr local_cpu_queue
- **Queue:** local_cpu_queue (dispatch AFTER Anchors 1+2 verdict)
- **What this teaches us:** if HARD_PASS, substrate has explicit capacity-management primitive that uses information-theoretic criterion (substrate-product story: bounded W with optimal information density); if HARD_FAIL, MDL criterion doesn't translate to substrate's regime

---

## Context pointers (file paths, not summaries)

### Parent + supersession
- **Parent drill (this hand-off's source):** `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md`
- **Supersedes Section 5 of:** `notes/research_gap4_brain_selective_homeostasis_2026-06-26.md` (M5 STC was refuted)

### USER directives (mandatory context)
- **USER pivot 2026-06-26:** `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
- **USER standing memory:** `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- **No-experiment-design-in-prompts:** `memory/feedback_no_experiment_design_in_prompts.md` (or referenced via [[]] link in research.md)
- **Bias master checklist:** `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`
  - Principle Q (suspect 1.000) APPLIES: if Anchor 1's E correlates 1.000 with |W|, E is just magnitude-proxy; HARD_FAIL
  - Principle S (band-calibration regime checks): 3-arm minimum spelled out for each anchor
  - Principle R (BIAS-13/14/15 contamination/regime/mismatch): smoke gate uses synthetic data per [[feedback-smoke-clean-synthetic-data-not-substrate-state]]
  - Principle N (verify-referent + Cramer-Rao): each anchor's discriminator must distinguish between mechanism-class hypothesis and noise/random-control

### The 5 failed cells (read metrics.json before cell-authoring)
- `data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json` (MIDDLE_BAND; addresses Anchor 2)
- `data/exp_gap4_stc_capture_selective_downscale_v1/metrics.json` (HARD_FAIL — REFUTES prior M5 STC; addresses Anchor 1)
- `data/exp_substrate_synaptic_homeostasis_global_downscale_v1/metrics.json` (Cell B HARD_FAIL; addresses Anchor 1; baseline target)
- `data/exp_gap4_cold_storage_no_combine_v1_smoke/metrics.json` (HARD_FAIL; smoke regime issue; addresses Anchor 1)
- `data/exp_gap1_partition_routing_cortex_R_schema_closed_form_v1_META_M7/metrics.json` (HARD_FAIL; addresses Anchor 1 as routing signal)

### Existing chain-grade primitives (composition substrate)
- **TWO_TIER architecture:** `data/exp_gap4_two_tier_generational_W_v1/metrics.json` HARD_PASS — Anchor 1's E becomes the PROMOTION CRITERION
- **NREM replay:** `data/exp_substrate_continual_NREM_replay_v1/metrics.json` HARD_PASS — composes with Anchor 1 E-gated downscale
- **HRR binding:** `hdlab/binding.py` (chain-grade)
- **Cleanup memory:** `hdlab/cleanup_memory.py` (chain-grade; hook point for E/U/B/cluster computations)
- **Refuse-gate:** `hdlab/refuse_gate.py` (chain-grade; provides novelty signal for Anchors 1, 4)
- **TWO_TIER promotion:** existing continual.py — Anchor 1 modifies promotion criterion

### Fixes to honor (current discipline)
- Fix #26: pre-dispatch verify-the-referent via `tools/predispatch_check.py <anchor_name>`
- Fix #28: read metrics.json per-arm not verdict_msg (especially for the 5-cell analysis)
- Fix #24: if any anchor routes to GPU, must actually use GPU (these anchors target local_cpu_queue so N/A)
- Fix #21: poll filesystem for landings; use `tools/peek_arm_metrics.py` before any tier/framing claim

## Contract

- Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists ANCHORS and POINTERS only. exp_dev authors cells per substrate-physics. Pre-reg bands are load-bearing.
- All cells must include META_M7 reproduce-once rail.
- Substrate-only-decode gate preserved (n_llm == 0; AUDIT logged).
- Per-seed runtime + cv <= 0.05 required for chain-grade.
- ARM_BASELINE rail MANDATORY in every anchor (reproduces relevant prior failure mode for sanity).
- Smoke gate per anchor BEFORE full dispatch per [[feedback-smoke-clean-synthetic-data-not-substrate-state]].
- Pre-flight verify-the-referent gate per Fix #26.
- text8 / BPC / bigram-gap / next-token-prediction are NOT relevant evals here. If exp_dev finds itself reaching for those metrics, STOP and check with research.

## Autonomy declaration

exp_dev has full autonomy over:
- Cell authoring within research-note guidance (anchor + primitive + pre-reg bands)
- N_DIM, seed count, e_thresh / w_thresh / theta_tag / etc. specific numerical parameters within standard envelope
- Smoke profile / FULL profile split per queue-add gate
- Reprioritization between Anchors 1-4 within the rank-order (Anchor 1 should dispatch first; Anchors 2-3 may dispatch parallel; Anchor 4 after Anchors 1+2 verdict)
- Encoder choice (substrate-native default per [[feedback-clean-encoder-tests-no-contamination]])

exp_dev does NOT have autonomy over:
- Switching the anchor pointer (these 4 are the surface; cross-discipline analysis was deliberate)
- Substituting magnitude-based selectivity (e.g. |W| > thresh) for any anchor — that's the failed-cell class
- Adding LLM forward calls (substrate-only-decode gate)
- Re-introducing language-prediction evals (USER pivot is in force)
- Skipping the random-control arm (this is what distinguishes mechanism from "any-perturbation-helps")

## Filed by

Research (Opus 4.7 1M), 2026-06-26, parent note `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md`. Hand-off ready for `/exp_dev notes/exp_dev_handoff_research_cortex_4x_selective_abstraction_drill_2026-06-26.md` dispatch when orchestrator unpauses.
