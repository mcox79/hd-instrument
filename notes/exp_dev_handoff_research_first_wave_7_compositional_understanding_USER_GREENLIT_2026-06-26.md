# exp_dev hand-off — research: FIRST-WAVE 7 EXPERIMENTS, USER green-lit (compositional understanding track)

**Filed-by:** Research (Opus 4.7 1M)
**Date:** 2026-06-26
**Trigger:** USER 2026-06-26 green-light on synthesis-of-3-drills with revisions per user audit. This handoff consolidates the FIRST-WAVE anchors from 3 prior handoffs (cortex 4x / multi-hop relational 2x / WM probabilistic-decode 2x) PLUS 2 user-suggested additions (top-K composition refuse-gate; emergent slot discovery).

## Pause state

Check `data/orchestrator_paused.flag` before dispatching. If paused, file this hand-off; do NOT dispatch.

Per [[feedback-no-experiment-design-in-prompts]]: anchors below are POINTERS, not full cell specs. exp_dev authors cells. Pre-reg bands LOAD-BEARING — bake into prereg verbatim.

## Pivot frame (mandatory; see USER lock memory)

USER 2026-06-26 standing rule (`memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`): substrate has NO language understanding; we are NOT testing language prediction; we ARE building compositional understanding. text8 / BPC / bigram-gap are NOT relevant evals for ANY anchor below.

## Audit revisions from USER 2026-06-26 (mandatory context)

USER caught 3 overlooked chain-grade landings that supersede/modify prior anchors:

1. **CHAIN_GRADE multi-bank K=4096** (`exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1`) IS multiple separate W matrices per bank — provably orthogonal by construction. **Walsh-Hadamard CDMA anchor KILLED** (was reinventing already-chain-grade work).
2. **CHAIN_GRADE_DEPTH_EXTENDS at depth-15** (`exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1`: depth-5=0.965, depth-10=0.857, depth-15=0.808, cv≤0.024 today). Partition-oracle routing handles depth-15 at chain-grade. Holographic chunk-pack KEPT (USER directive — different mechanism class: training-time precomputation vs query-time routing; could compose with partition-oracle).
3. **PC primitive exists** (`hdlab/predictive_coding.py` Rao-Ballard 1999; `exp_pc1_predictive_coding_residual_gate_v1` MIDDLE_BAND). **Annealed Langevin diffusion KILLED** — replaced by wiring existing PC primitive into cleanup path.
4. **CHAIN_GRADE intent classifier at n=100** (`exp_substrate_intent_classifier_v2_production_scale_100plus_intents_smoke` SUB=1.000 cv=0.000). Typed multi-bank scope corrected from K=8 → K=64-128 to match this scale.
5. **CHAIN_GRADE SEMANTIC concept learner** (`exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1` 5/6 arms PASS) — load-bearing for emergent slot discovery (NEW anchor 5).

---

## First-wave anchors (7 experiments, USER green-lit)

### ANCHOR 1: cortex_E_tensor_separate_importance_v1

- **Anchor pointer:** new cell using new primitive `hdlab/excitability.py` (per-atom E tensor, EWMA-on-retrieval, slow decay)
- **Substrate-product reading:** per-atom E[i] tensor SEPARATE from W; downscale operations gate on E[i] (the "this matters" signal), not on |W[i]|. The missing CREB-analog primitive. Composes with TWO_TIER (E becomes promotion criterion) + NREM replay (E-weighted replay) + refuse-gate (novelty seeds initial E).
- **Why now:** addresses root cause of 3/5 cortex failures (Cell B / STC / cold-storage). All failed because substrate tried to read importance off |W| (the noisy thing); E is the orthogonal signal.
- **Arms (3 mandatory):** ARM_NO_E_BASELINE (reproduces Cell B failure; sanity rail); ARM_E_GATED_DOWNSCALE; ARM_RANDOM_GATED_DOWNSCALE (control — proves SELECTIVITY matters vs "any-fraction-downscale works")
- **Pre-reg bands:** HARD_PASS recall_old>=0.60 AND recall_recent>=0.85 AND ||W||_F bounded AND cv<=0.05 AND cor(E, |W|)<0.7 (E carries information |W| doesn't); MIDDLE recall_old in 0.30-0.60; HARD_FAIL recall_old<0.30 OR cor(E,|W|)>0.9 (E is just magnitude proxy) OR ARM_E indistinguishable from ARM_RANDOM
- **Cost:** ~3-5 hr local_cpu (3 seeds)
- **Queue:** local_cpu_queue
- **Source:** `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md` ANCHOR 1; P_deflated=0.45

### ANCHOR 2: typed_multibank_K128_v1

- **Anchor pointer:** new cell extending chain-grade `exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1` with per-bank type label
- **Substrate-product reading:** add per-slot type tag (K=64-128 types to match chain-grade intent-classifier scale); queries explicitly specify type; cross-type mismatched queries route through refuse-gate; built on chain-grade separate-substrates-per-bank multi-bank (USER's separation-by-construction insight, already proven)
- **Why now:** USER pivot LOAD-BEARING; foundational primitive for compositional understanding; builds on already-chain-grade infrastructure
- **Arms (3 mandatory):** ARM_UNTYPED_BASELINE (reproduces chain-grade multi-bank without types; sanity rail); ARM_TYPED_ROUTING (proposed); ARM_TYPED_ROUTING_ADVERSARIAL_PROBE (deliberately ill-typed queries; tests refuse-rate on type collisions)
- **Pre-reg bands:** HARD_PASS typed-recall>=0.95 at K=128 AND refuse-rate>=0.90 on type-mismatched AND cv<=0.05; MIDDLE typed-recall 0.85-0.95; HARD_FAIL typed-recall<0.80 OR refuse-rate<0.50 (type signal not actionable)
- **Cost:** ~30 min remote_cpu_queue (matmul-bound; route via orchestrator per Fix #24)
- **Queue:** remote_cpu_queue
- **Source:** `notes/research_wm_probabilistic_decode_2x_revival_drill_2026-06-26.md` ANCHOR 1 (modified per USER audit Q1.2 to K=64-128 scope); P_deflated=0.60

### ANCHOR 3: topk_composition_refuse_gate_v1 (USER NEW)

- **Anchor pointer:** new cell composing on chain-grade `hdlab/refuse_gate.py` + cleanup-energy gap
- **Substrate-product reading:** when top-1 and top-2 cleanup answers have small energy gap, substrate returns BOTH with disjunctive composition ("answer is in {X, Y}, here's why I can't disambiguate") rather than refusing. Compositional disjunction at the output. USER insight: don't waste the second-best signal; compose it.
- **Why now:** USER caught that binary refuse wastes information; substrate already has chain-grade refuse-gate (V_REL=256) + chain-grade cleanup; composing top-K with disjunctive output is cheaper than refuse + more useful for downstream composition
- **Arms (3 mandatory):** ARM_TOP1_COMMIT_BASELINE (current behavior; sanity rail); ARM_REFUSE_ON_SMALL_GAP (binary refuse); ARM_TOPK_DISJUNCTIVE (proposed — return top-K with confidence weights)
- **Pre-reg bands:** HARD_PASS disjunctive-output-correctness >= top1-commit-correctness AND ambiguous-case recall@K=2 >= 0.85 AND false-disjunction-rate <= 0.15 (don't return K=2 when top-1 is clearly best); MIDDLE disjunctive-correctness within 0.05 of top1; HARD_FAIL disjunctive-correctness < top1 (composition hurts) OR false-disjunction-rate > 0.40
- **Cost:** ~10 min smoke / ~1-2 hr full local_cpu_queue
- **Queue:** local_cpu_queue
- **Source:** USER Q3.1 follow-up 2026-06-26; composes on chain-grade primitives; estimated P_deflated=0.50

### ANCHOR 4: SOLAR_LARS_clean_harness_v1

- **Anchor pointer:** rerun chain-grade relational-bottleneck primitive with constructed-disjoint heldout + SOLAR-style cross-attention slot-binding arm
- **Substrate-product reading:** redo the LARS-VSA test under CLEAN harness (heldout (color, shape, position) tuples disjoint from train at feature level); add SOLAR arm (Webb-Russin-Cohen 2024 cross-attention slot-binding); decisive test of whether substrate can do TRUE compositional generalization
- **Why now:** prior LARS-VSA verdict was contaminated by harness leakage (heldout shared features with train); decisive rerun needed before any conclusion about relational-bottleneck composition
- **Arms (3 mandatory):** ARM_NO_COMPOSITION_BASELINE (chance + sanity rail; must be at 0.20 ± 0.05 on clean heldout); ARM_RELBOTTLENECK_CLEAN; ARM_SOLAR_SLOT
- **Pre-reg bands:** HARD_PASS RELBOTTLENECK_CLEAN >= 0.40 AND BASELINE <= 0.25 AND SOLAR > RELBOTTLENECK + 0.05 AND cv<=0.06; MIDDLE 0.25-0.40; HARD_FAIL RELBOTTLENECK_CLEAN <= 0.22 (no detectable lift over chance on clean harness — refutes relational composition at production scale) OR baseline > 0.25 (harness still leaks; REJECT cell)
- **Cost:** ~3-4 hr remote_cpu_queue (matmul-bound at N=8192)
- **Queue:** remote_cpu_queue
- **Source:** `notes/research_multihop_relational_2x_revival_drill_2026-06-26.md` ANCHOR 1; P_deflated=0.40

### ANCHOR 5: emergent_slot_discovery_v1 (USER NEW)

- **Anchor pointer:** new cell using chain-grade SEMANTIC concept learner primitive
- **Substrate-product reading:** substrate is given NO type labels; observes query-pattern clusters ("these atoms tend to answer queries of pattern X; those atoms answer pattern Y"); discovers slot-types as latent structure. Tests whether substrate can GENUINELY compose (slots emerge from data) vs EXECUTE compositions (slots prescribed by human)
- **Why now:** USER Q1.2/Q1.3 follow-up — load-bearing distinction between "we hand the substrate compositional structure" vs "substrate discovers compositional structure." The latter is the actual goal of the understanding pivot. Stage1 SEMANTIC concept learner just landed chain-grade with 5/6 arms PASS — the primitive exists.
- **Arms (3 mandatory):** ARM_PRESCRIBED_SLOTS_BASELINE (Anchor 2 typed-routing as upper-bound rail; sanity); ARM_EMERGENT_SLOTS_FROM_QUERY_CLUSTERS (proposed); ARM_RANDOM_SLOT_ASSIGNMENT (control — proves DISCOVERY matters vs "any slot structure helps")
- **Pre-reg bands:** HARD_PASS discovered-slot-recall within 0.10 of prescribed-slot-recall (discovery comparable to prescription) AND slot-purity >= 0.70 (discovered slots correspond to real semantic categories) AND cv<=0.05; MIDDLE within 0.20; HARD_FAIL discovered-slot-recall < prescribed by 0.30+ OR slot-purity < 0.40 (discovered "slots" are noise)
- **Cost:** ~4-6 hr local_cpu_queue (discovery iteration adds overhead)
- **Queue:** local_cpu_queue
- **Source:** USER Q1.3 follow-up; composes on chain-grade SEMANTIC concept learner; estimated P_deflated=0.40

### ANCHOR 6: pc_cleanup_attractor_v1 (replaces annealed Langevin)

- **Anchor pointer:** new cell wiring existing `hdlab/predictive_coding.py` primitive into multi-hop cleanup path
- **Substrate-product reading:** use PC's free-energy minimization (already validated; MIDDLE_BAND on residual-gate-v1) as the cleanup mechanism for multi-hop chains; tests whether monotone-descent denoising via PC eliminates the iterated-cleanup noise accumulation
- **Why now:** USER Q5.1 — PC primitive already exists in substrate; reusing it is cheaper than reinventing as annealed Langevin diffusion; less novel-synthesis risk; validates whether existing PC primitive composes with multi-hop chain query
- **Arms (3 mandatory):** ARM_VANILLA_CLEANUP_BASELINE (current behavior at depth-5; sanity rail); ARM_PC_CLEANUP_AT_EACH_HOP (proposed); ARM_PC_CLEANUP_FINAL_ONLY (control — tests whether per-hop matters vs final-state-only)
- **Pre-reg bands:** HARD_PASS depth-5 >= 0.65 (no degradation over baseline) AND depth-10 >= 0.50 AND free-energy monotonically decreases per hop (validates mechanism); MIDDLE depth-5 in 0.55-0.65; HARD_FAIL depth-5 <= 0.50 (PC hurts) OR free-energy non-monotonic (PC not converging)
- **Cost:** ~3-4 hr local_cpu_queue
- **Queue:** local_cpu_queue
- **Source:** USER Q5.1 follow-up; replaces annealed Langevin from `notes/research_multihop_relational_2x_revival_drill_2026-06-26.md` ANCHOR 3; estimated P_deflated=0.45

### ANCHOR 7: holographic_chunk_pack_training_time_v1 (USER KEPT despite partition-oracle chain-grade)

- **Anchor pointer:** new cell pre-computing 2-hop chunk atoms at INGEST time, addressable by chunk-id
- **Substrate-product reading:** during training, store 2-hop chunks `chunk_atom = bind(s, p1, intermediate, p2, o)` in W alongside single-hop triples; query-time multi-hop = chunk lookups (single-step accuracy per chunk). Different mechanism class from partition-oracle (training-time precomputation vs query-time routing); USER directive: if it's genuinely new and viable, try it regardless of partition-oracle chain-grade.
- **Why now:** USER Q4.2 — partition-oracle handles depth-15 at chain-grade but only when partition-key derivable from query. Holographic chunks address regimes where partition-key isn't derivable (open-ended queries, ambiguous routing). Could compose with partition-oracle for combined coverage.
- **Arms (4 mandatory):** ARM_PARTITION_ORACLE_BASELINE (chain-grade reference; sanity rail at depth-5/10/15); ARM_HOLOGRAPHIC_CHUNK_ONLY (proposed in isolation); ARM_PARTITION_PLUS_CHUNK_COMPOSED (tests composition with chain-grade primitive); ARM_HOLOGRAPHIC_CHUNK_ON_UNROUTABLE_QUERIES (tests the unique-coverage regime — queries where partition-oracle's key isn't derivable)
- **Pre-reg bands:** HARD_PASS HOLOGRAPHIC_CHUNK_ONLY >= 0.50 at depth-5 AND composed arm >= partition-oracle baseline AND unroutable-coverage > 0.40 (proves unique-coverage value); MIDDLE all arms within ±0.10 of partition-oracle (no unique value); HARD_FAIL HOLOGRAPHIC_CHUNK_ONLY <= 0.30 OR composed arm < partition-oracle (chunk-pack contaminates routing)
- **Cost:** ~4-5 hr local_cpu_queue (one-time chunk precomputation + query lookup)
- **Queue:** local_cpu_queue
- **Source:** `notes/research_multihop_relational_2x_revival_drill_2026-06-26.md` ANCHOR 2 (USER kept per Q4.2 — viable orthogonal mechanism class); P_deflated=0.40

---

## Dispatch ordering recommendation (exp_dev owns decision)

**Wave 1 (parallel, all cheap; ~10min-2hr each; local_cpu_queue):**
- ANCHOR 3 topk_composition_refuse_gate_v1 (~10 min smoke; cheapest)
- ANCHOR 6 pc_cleanup_attractor_v1 (~3-4 hr)
- ANCHOR 1 cortex_E_tensor (~3-5 hr)

**Wave 2 (parallel after Wave 1 verdicts inform; remote_cpu_queue):**
- ANCHOR 2 typed_multibank_K128_v1 (~30 min; matmul → remote)
- ANCHOR 4 SOLAR_LARS_clean_harness_v1 (~3-4 hr; matmul → remote)

**Wave 3 (parallel; local_cpu_queue):**
- ANCHOR 5 emergent_slot_discovery_v1 (after ANCHOR 2 verdict to use as rail; ~4-6 hr)
- ANCHOR 7 holographic_chunk_pack (~4-5 hr; independent of other anchors)

Per Fix #14: spawn budget ≤3 in-flight; serialize across waves.

---

## SUPERSEDED prior-handoff anchors (do NOT pick up these)

Within this first-wave, these prior-handoff anchors are SUPERSEDED:

- `exp_dev_handoff_research_wm_probabilistic_decode_2x_revival_2026-06-26.md` ANCHOR 2 walsh_hadamard_CDMA_wm_v1 → KILLED (multi-bank separate-substrates already chain-grade)
- `exp_dev_handoff_research_multihop_relational_2x_revival_2026-06-26.md` ANCHOR 3 annealed_langevin_diffusion_cleanup → REPLACED by ANCHOR 6 (PC primitive)

PRESERVED prior-handoff anchors (still valid as Tier-2/3 conditional):

- WM-revival ANCHOR 4 particle_filter_compositional (deferred on ANCHOR 2 typed_multibank verdict)
- Multi-hop ANCHORS 4-6 (TPR / PC hierarchical / HSR multi-scale) — conditional on first-wave outcomes
- Cortex ANCHORS 3-4 (SOC criticality / MDL turnover) — conditional on first-wave outcomes
- Compositional-understanding-drill-1 ANCHOR 2 predicate-argument (downgraded per USER — capability-composition hurts; defer until feature-based composition validated)

---

## Context pointers

- USER pivot: `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md`
- USER standing lock: `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- Source drill notes (read for math + mechanism diagnosis):
  - `notes/research_cortex_4x_cross_discipline_selective_abstraction_2026-06-26.md`
  - `notes/research_multihop_relational_2x_revival_drill_2026-06-26.md`
  - `notes/research_wm_probabilistic_decode_2x_revival_drill_2026-06-26.md`
- USER audit findings to honor:
  - chain-grade multi-bank: `data/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1/metrics.json`
  - chain-grade depth-15 multi-hop: `data/exp_phase_diagram_multihop_depth_extension_via_partition_oracle_v1/metrics.json`
  - chain-grade intent classifier n=100: `data/exp_substrate_intent_classifier_v2_production_scale_100plus_intents_smoke/metrics.json`
  - chain-grade SEMANTIC concept learner: `data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v1/metrics.json`
  - existing PC primitive: `hdlab/predictive_coding.py` + `data/exp_pc1_predictive_coding_residual_gate_v1/metrics.json`
- Bias master checklist: `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md`

## Contract

- All cells: META_M7 reproduce-once rail; substrate-only-decode gate (n_llm==0); per-seed runtime + cv<=0.05 required for chain-grade; ARM_BASELINE sanity rail mandatory; pre-flight Fix #26 verify-the-referent.
- text8 / BPC / bigram-gap NOT relevant evals for ANY anchor here. If exp_dev finds itself reaching for those metrics, STOP.
- Per Fix #28: default tier MIDDLE; let Skunkworks tier UP.
- Per [[feedback-use-peek-arm-metrics-before-framing]]: read metrics.json per-arm before any framing claim.
- USER Q1.3 insight is load-bearing: ANCHOR 5 (emergent slot discovery) is the decisive test for genuine compositional understanding vs prescribed-structure execution.

## Autonomy declaration

exp_dev owns: cell authoring within research-note guidance; smoke/full split; queue routing per Fix #24; reprioritization within wave; encoder + N_DIM + seed selection.

exp_dev does NOT own: re-defining HARD_PASS bands; substituting magnitude-based selectivity for ANCHOR 1 (defeats the point); skipping ARM_RANDOM control where specified (it's the discriminator); reaching for language-prediction evals; bumping to chain-grade pre-Skunkworks review.

USER explicitly green-lit all 7 first-wave anchors 2026-06-26 with Q-by-Q audit. No further research approval needed for Wave 1 dispatch.

---

-- Research (Opus 4.7-1M)
