# Research drill: Stage 3 compositional understanding cell design

**Filed-by:** Research (Opus 4.7 1M, Director)
**Date:** 2026-06-27 (USER on flight wifi; review on return)
**Trigger:** Wave 1 (cortex E-tensor, top-K composition, PC cleanup) saturated/MIDDLE_BAND; Wave 2 candidates pending audit; USER pivot to compositional understanding (Stage 3) is the new primary track.
**Calibration:** P_deflated per [[feedback-lit-scan-calibration-penalty]]; HARD_PASS bands strictly-above-floor per META_RULE_L; discriminator must fire at full-N per META_RULE_K; QUS by-construction-saturation auto-demote per Fix #28.

---

## TL;DR

Wave 1 three-arm verdict and gap3 drill follow-up cells reveal a single load-bearing pattern: **schema-formation in a single W via linear bundling caps at the HRR-crosstalk floor (~0.47 for K=20 instances at N=8192).** Five of six dispatched compositional cells (cortex E-tensor x3, LARS-VSA, cortical schema, modern-Hopfield) failed or middle-banded on this same structural ceiling. PC cleanup HARD_PASSed on by-construction-saturation only. Top-K composition HARD_PASSed but engineered-ambiguity follow-up shows the discriminator never fires at substrate's chain-grade cleanup (top-1 = 0.999 leaves no room for top-2 disjunction).

**The brain answer is unambiguous: TWO_TIER architecture with eta_slow << eta_fast + non-linear write rule (BCM sliding-threshold OR Modern-Hopfield exponential basin) in the slow tier.** Substrate has NREM replay (drift-reduction proven-bound), continual.replay_cycle, predictive_coding.gated_write. Missing piece: the slow-tier W_schema + non-linear write rule. This is the rank-1 untested cell.

**Wave 2 audit verdict:**
- ANCHOR 2 typed_multibank_K128_v1: **RESPEC** (was over-scoped; type-routing layered on chain-grade multibank is the right composition; but pre-reg needs full-N discriminator that survives k_per_bank=64 saturation)
- ANCHOR 4 SOLAR_LARS_clean_harness_v1: **DROP for Stage 3** (root cause of LARS-VSA HARD_FAIL_CONFOUND is harness leak; even with clean harness the underlying mechanism is HRR-bind which has crosstalk ceiling. Keep as Tier-3 falsification probe iff CLS_BCM and modern-Hopfield-v2 both HARD_FAIL.)
- ANCHOR 5 emergent_slot_discovery_v1: **KEEP** (load-bearing distinction: substrate discovers vs executes composition; builds on chain-grade SEMANTIC concept learner A3 heldout_top1=1.000)
- ANCHOR 7 holographic_chunk_pack_v1: **KEEP** (mechanism-distinct from partition-oracle: training-time precomputation; orthogonal coverage for unroutable queries)

Below: 5 new Stage 3 cells in dispatch priority. All MUST be authored remote-only per USER 2026-06-27 D9; cell-author smoke gates on remote_cpu_queue; full on remote_cpu or overnight_queue per Fix #24.

---

## Section 1: Wave 2 candidate audit

### ANCHOR 2 typed_multibank_K128_v1 — RESPEC

**Original pitch:** add per-bank type label on chain-grade multibank K=4096; types from chain-grade intent-classifier scale (n=100); refuse-gate on type-mismatched queries.

**Audit verdict:** mechanism is sound but the pre-registered HARD_PASS bands (typed-recall>=0.95) sit IN THE BY-CONSTRUCTION-SATURATION REGIME for k_per_bank=64 per `hdlab/working_memory.py` META rule. K=128 with n_banks=64 means k_per_bank=2 (saturation guaranteed) — claim has no discriminating power. With k_per_bank>=64 at chain-grade overlap=0.20, the multibank arm produces recall=0.98-0.99 baseline before any typed mechanism is added. The "lift from types" is then bounded by 1.0 - 0.99 = 0.01, indistinguishable from noise.

**RESPEC required:**
- Run at K_total=8192 with n_banks=128 (k_per_bank=64; minimum discriminating regime)
- ADD adversarial regime: each bank's items share FEATURE_OVERLAP_FRAC=0.40 (higher than 0.20 baseline to push baseline recall below saturation)
- Add Q-discipline check: if ARM_UNTYPED_BASELINE >= 0.95 → by-construction-saturation auto-demote to MEASURED_MECHANISM
- ARM_TYPED_ROUTING_ADVERSARIAL_PROBE must drive baseline FALSE-ROUTE rate to >= 0.30 (refuse-gate has room to add value)
- HARD_PASS now: typed-recall >= baseline + 0.10 AND refuse-rate on type-mismatched >= 0.85 AND ARM_UNTYPED_BASELINE in [0.60, 0.85] (not saturated)

**Cost:** ~1 hr remote_cpu after RESPEC; ARM_BASELINE adversarial regime determines feasibility.

**Verdict:** RESPEC — see cell design 4 below (typed_multibank_K128_adversarial_v1).

### ANCHOR 4 SOLAR_LARS_clean_harness_v1 — DROP for Stage 3

**Original pitch:** rerun chain-grade relational-bottleneck primitive with constructed-disjoint heldout + SOLAR cross-attention slot-binding arm.

**Audit verdict:** the prior LARS-VSA HARD_FAIL_CONFOUND verdict (`exp_gap3_lars_vsa_relational_bottleneck_v1_n8192` ARM_BASELINE=0.3333 >= 0.30) means harness was leaky AND mechanism would have HRR-crosstalk ceiling even on clean harness (ARM_RESONATOR best at 0.4267 vs baseline 0.3333 = +0.09 lift; floor of crosstalk per Plate 1995). Even chain-grade-eligible RESONATOR barely beats baseline. SOLAR adds cross-attention to slots — but substrate has NO native slot primitive at chain-grade today; SOLAR transports poorly.

**DROP rationale:** even if SOLAR arm chain-grades, the cell at most gives substrate +0.10 lift over baseline — same as cortical_schema MIDDLE_BAND. Doesn't address the structural ceiling. Compute budget better spent on TWO_TIER cells that have brain-existence-proof for ESCAPING the ceiling.

**Keep as Tier-3 falsification probe** iff CLS_BCM_two_tier AND modern-Hopfield-v2 (with substrate-mined beta) both HARD_FAIL. At that point pivot to "are slots the missing primitive" with SOLAR as the test. Until then, defer.

### ANCHOR 5 emergent_slot_discovery_v1 — KEEP (high priority)

**Original pitch:** substrate observes query-pattern clusters; discovers slot-types as latent structure. Tests TRUE compositional understanding (slots emerge from data).

**Audit verdict:** load-bearing distinction USER articulated 2026-06-26 Q1.3 — "we hand the substrate compositional structure" vs "substrate discovers compositional structure." Latter is the actual Stage 3 goal. Chain-grade SEMANTIC concept learner v3 HARD_PASSed A3 heldout_top1=1.000 at 6/6 arms — primitive for "novel concept inferable from training distribution" is operational at high cv (which is HONEST — A3 saturated 1.000, A4 compose=0.533, cv=0.125 — so generalization-without-saturation regime needs separate test).

**KEEP with refinement** — see cell design 2 below (emergent_slot_via_query_cluster_discovery_v1). Critically: arms must include ARM_PRESCRIBED_SLOTS (upper-bound rail from typed_multibank) AND ARM_RANDOM_SLOT (control). Use SEMANTIC concept learner's A3+A4 regime (not A3 alone) to avoid saturation.

### ANCHOR 7 holographic_chunk_pack_training_time_v1 — KEEP (mechanism-distinct)

**Original pitch:** precompute 2-hop chunk atoms at ingest time; query-time multi-hop = chunk lookups; mechanism-class-distinct from chain-grade partition-oracle (training-time precomputation vs query-time routing).

**Audit verdict:** USER directive 2026-06-26 explicitly kept this despite partition-oracle chain-grade — different mechanism class, orthogonal coverage. The unique-coverage regime is "queries where partition-key isn't derivable" (open-ended, ambiguous). This IS the regime where partition-oracle's depth-15 chain-grade DOESN'T apply.

**KEEP** — see cell design 5 below (holographic_chunk_pack_unroutable_regime_v1). Critical: discriminator must construct queries that fail partition-oracle routing (require this to be empirically verified in smoke, not just claimed by construction).

---

## Section 2: Five new Stage 3 cell specs (priority order)

### CELL 1 — gap3_cls_two_tier_BCM_slow_replay_v1 (HIGHEST PRIORITY)

**Mechanism class:** TWO_TIER + non-linear slow-rate write (BCM sliding-threshold). The brain-grounded mechanism per CLS framework (McClelland 1995 / Kumaran-McClelland 2016). Composes existing substrate primitives: `continual.replay_cycle` (NREM proven-bound drift-reduction +0.57) + `predictive_coding.gated_write` (existing) + NEW W_schema matrix + NEW BCM write rule (~20 lines).

**What it tests:** does eta_slow=1e-3 BCM write into W_schema from REPLAYED W_episodic episodes produce category prototypes that generalize >= 0.65 heldout at N=8192, 5 categories x 20 train + 10 heldout per category?

**Mechanistically distinct from cortex E-tensor:** E-tensor tried to give each ATOM an importance signal. This cell gives the SUBSTRATE a second storage tier with a different LEARNING RULE. No magnitude-coupling failure mode (META_RULE_F).

**Mechanistically distinct from Modern Hopfield prototype attractor v1 (MIDDLE_BAND 0.26):** Modern Hopfield tried to make ONE W non-linearly basin-attract. This cell uses TWO W's with different time constants — the brain's actual solution. The 0.26 failure of MH-v1 is evidence the single-W angle is closed; TWO_TIER is the legitimate next test.

**Arms (4 mandatory):**
- `ARM_BASELINE_SINGLE_W`: substrate's existing single-W with iterative cleanup. Cross-cell rail must replicate Cell 1 ARM_NO_SCHEMA ~0.37 within 0.05. METHODOLOGY-DRIFT gate.
- `ARM_TWO_TIER_HEBBIAN_SLOW`: vanilla Hebbian outer-product write into W_schema at eta_slow=1e-3. Tests: does the slow-rate alone (without BCM) do anything? RAIL — if this arm matches BCM, the lift is from eta_slow not from BCM, mechanism not as claimed.
- `ARM_TWO_TIER_BCM_SLOW`: BCM sliding-threshold rule, dW = eta_slow * x * y * (y - theta_M), theta_M = EWMA(y^2, window=200). Full brain-aligned mechanism.
- `ARM_TWO_TIER_BCM_GENERATIVE_REPLAY`: same BCM but replay samples generative-reconstruction from W_episodic (not literal episode IDs). Tests Olafsdottir-McClelland generative-replay-helps-generalization claim.

**Pre-reg bands (defensible against Q + META_RULE_L):**
- HARD_PASS: `ARM_TWO_TIER_BCM_*` >= 0.65 heldout AND >= ARM_BASELINE + 0.18 AND >= ARM_TWO_TIER_HEBBIAN_SLOW + 0.10 AND cv <= 0.08 AND W_schema mean-cosine-to-cone in [0.5, 0.95] of W_episodic (cone-preserving rail per Gap 2; if W_schema rotates off cone, schema is in noise direction). Strictly-above-floor: HARD_PASS requires `>= 0.70` (floor 0.65 + 0.05 band-width per META_RULE_L).
- MIDDLE_BAND: best BCM arm in [0.50, 0.65] AND > baseline by >= 0.10.
- HARD_FAIL: all TWO_TIER arms within 0.05 of single-W baseline (mechanism null) OR ARM_BASELINE >= 0.50 (methodology drift; cross-cell rail violated — abort) OR W_schema rotates off cone (mean-cosine < 0.3 of W_episodic).

**Discriminator survives full-N (META_RULE_K):** at N=8192 with 100 episodes the substrate baseline is ~0.37 (Cell 1 rail). For TWO_TIER to claim >= 0.70 it must ACTUALLY learn schemas; cannot be by-construction-saturation since baseline is far from ceiling. Smoke check: 1 seed at N=8192, 500 replay cycles (instead of 5000), verify baseline replicates ~0.37 and BCM arm rises monotonically over training. If BCM arm doesn't move in 500 cycles, kill before full dispatch.

**By-construction-saturation check (Q-discipline):** if W_schema converges to identical-to-mean of class instances (reduces to ARM_FEATURE_BASED_SCHEMA from Cell 1 cortical_schema), the BCM rule isn't doing anything non-linear. Pre-reg requires log W_schema-eigenspectrum entropy at end of training to be LOWER than start (compression actually happened); if entropy unchanged, MM auto-demote.

**Cost:** 6-10 CPU-hr remote_cpu_queue at N=8192, 5000 replay cycles x 4 arms x 3 seeds = 60K replay iterations.

**Brain-grounding strength:** STRONG. McClelland 1995, Kumaran-McClelland 2016 EXPLICITLY identify this architecture as the cortical-schema mechanism. BCM (Bienenstock-Cooper-Munro 1982) is established experimentally in mouse visual cortex. NREM replay drift-reduction is PROVEN-BOUND in our substrate. Composition of brain-existence-proof primitives.

**P_deflated:** 0.45 (raw lit P=0.65; -0.20 calibration). Highest individual P of any Stage 3 candidate.

**Source:** `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` rank-1 + `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` rank-2.

---

### CELL 2 — emergent_slot_via_query_cluster_discovery_v1

**Mechanism class:** Schema extraction via unsupervised query-pattern clustering. Composes chain-grade SEMANTIC concept learner (v3 HARD_PASS A3 heldout_top1=1.000 + A4 compose=0.533) + chain-grade ultrametric_clustering (CHAIN_GRADE today; first cortex content-extraction win) + typed_multibank (RESPEC'd; Cell 4 below).

**What it tests:** given NO type labels, can substrate observe query-result patterns ("these atoms tend to answer queries of pattern X") and discover slot-types as latent structure? Discriminator: discovered slots within 0.10 of prescribed-slot-routing recall on heldout queries, with slot-purity >= 0.70.

**Mechanistically distinct from cortex E-tensor:** no per-atom importance signal; discovers atom CATEGORIES from co-activation patterns. Brain analog: anterior temporal lobe semantic hub.

**Mechanistically distinct from CELL 1 CLS BCM:** Cell 1 extracts schema as INVARIANT prototype across training instances. This cell extracts schema as CO-ACTIVATION CLUSTER across queries. Different angle on Stage 3 compositional understanding: Cell 1 is "what unites class members"; this cell is "what role does this atom play."

**Arms (4 mandatory):**
- `ARM_PRESCRIBED_SLOTS_UPPER_BOUND`: chain-grade typed_multibank (Cell 4) with hand-labeled types. Upper-bound rail for what slot-routing can achieve.
- `ARM_RANDOM_SLOT_ASSIGNMENT_CONTROL`: assign atoms to slots uniformly at random; tests "any slot structure helps" null hypothesis.
- `ARM_EMERGENT_SLOTS_VIA_ULTRAMETRIC`: cluster atoms by co-activation pattern across N_queries=1000 substrate self-queries via ultrametric_clustering at cosine_thresh=0.85; assign atoms to discovered clusters; route queries by query-pattern similarity to cluster prototypes.
- `ARM_EMERGENT_SLOTS_VIA_SEMANTIC_CONCEPT_LEARNER`: use SEMANTIC concept learner's existing concept-formation primitive on the query-co-activation signature space (queries become "stimuli", atoms become "concepts").

**Pre-reg bands (defensible against Q + META_RULE_L):**
- HARD_PASS: best emergent-arm recall on heldout queries >= ARM_PRESCRIBED_SLOTS_UPPER_BOUND - 0.10 (within 0.10 of upper bound) AND slot-purity (NMI between discovered clusters and ground-truth types) >= 0.70 AND ARM_RANDOM_SLOT << emergent (gap >= 0.15) AND cv <= 0.08. Strictly-above-floor: requires >= 0.05 above 0.70 NMI floor.
- MIDDLE_BAND: emergent arm in [0.50, prescribed - 0.10] OR NMI in [0.40, 0.70].
- HARD_FAIL: emergent arm within 0.05 of RANDOM_SLOT (discovered "slots" are noise) OR NMI <= 0.30 OR PRESCRIBED_SLOTS arm saturates at 1.000 (upper bound is by-construction; cell vacuous).

**Discriminator survives full-N (META_RULE_K):** smoke uses N_atoms=400 with 8 ground-truth types of 50 atoms each at N_DIM=8192. PRESCRIBED arm must NOT saturate at smoke (target ~0.85, not 1.000) — verified by setting query-noise level epsilon=0.15 to push baseline below ceiling. Full-N uses N_atoms=4000 with 40 types.

**By-construction-saturation check (Q-discipline):** if NMI = 1.0 on smoke, the clustering is finding tautological structure (atoms with shared prefix in ground-truth labels are also adjacent in cosine space by-construction). Pre-reg requires substrate atoms to be encoded BEFORE type labels are assigned (type labels are read-out only); if this is violated → vacuous-UD auto-demote per META_RULE_K.

**Cost:** 4-6 CPU-hr remote_cpu_queue (clustering iteration adds overhead at N_atoms=4000 with cosine pairwise = 16M comparisons; ultrametric_clustering primitive already chain-grade).

**Brain-grounding strength:** STRONG-MEDIUM. Anterior temporal lobe semantic hub (Patterson-Nestor-Rogers 2007), inferotemporal cortex category cells (Tsao-Livingstone 2008) — emergent category structure from co-activation is brain-established. Substrate's chain-grade SEMANTIC concept learner is the existing primitive that this composes with.

**P_deflated:** 0.40 (raw lit P=0.60; -0.20 calibration; composes on chain-grade primitives).

**Source:** USER Q1.3 follow-up 2026-06-26; original Wave 2 anchor 5 audited above.

---

### CELL 3 — predicate_composition_role_filler_v1

**Mechanism class:** Symbolic predicate composition via HRR role-filler binding on chain-grade KG primitives. Tests genuine compositional understanding (combining facts to make NEW facts) using substrate's existing chain-grade KG ingest (FB15k 584 / ConceptNet 585 / HotpotQA 588) as fact storage AND chain-grade multi-hop primitive (depth-15 at 0.808) as composition engine.

**What it tests:** given training set of single-hop atomic facts (s, p, o), can substrate compose NEW 2-predicate inferences (s, p1, x) AND (x, p2, o) → (s, p1∘p2, o) where the COMPOSED predicate `p1∘p2` was NEVER stored as an atom? Discriminator: substrate must answer queries about composed predicates by chaining single-hop facts, NOT by storing composed facts directly.

**Why this is the right Stage 3 test:** brain-analog is the parietal "binding" hypothesis — composition is structural (bind role + filler) not stored (no need to memorize every composition). This is the variable-binding / role-filler suggestion the USER explicitly flagged.

**Mechanistically distinct from chain-grade multi-hop:** chain-grade multi-hop tests RETRIEVAL on stored chains (sub-graph that EXISTS in training). This cell tests INFERENCE on chains that DO NOT EXIST in training but should be DERIVABLE from atomic facts. Chain-grade multi-hop saturates at depth-15=0.808 BECAUSE the chains were SEEN; this cell explicitly excludes seen chains.

**Mechanistically distinct from cortex E-tensor:** no per-atom importance; pure compositional inference. Different failure modes.

**Arms (4 mandatory):**
- `ARM_MEMORIZATION_BASELINE`: substrate stores composed facts directly as atomic (s, p1∘p2, o); chain-grade KG primitive. Tests pure storage. Should be ~1.000 by-construction if composed facts ARE stored.
- `ARM_NO_COMPOSITION_CONTROL`: substrate stores ONLY single-hop facts; query asks composed predicate; substrate returns top-1 over atomic facts. Should be at chance (~ 1/n_objects) since composed predicate has no direct atom.
- `ARM_HRR_BIND_PREDICATE_COMPOSITION`: substrate stores single-hop facts; query-time forms composed predicate via HRR bind(p1, p2) and unbinds via chain-grade multi-hop. Tests genuine inferential composition.
- `ARM_PREDICATE_COMPOSITION_PLUS_REFUSE_GATE`: as above but adds refuse-gate at cleanup-energy gap threshold; tests calibrated abstention on uncomposable predicates.

**Pre-reg bands (defensible against Q + META_RULE_L):**
- HARD_PASS: `ARM_HRR_BIND_PREDICATE_COMPOSITION` >= 0.55 heldout on COMPOSED predicates (above 0.50 floor + 0.05 META_RULE_L band-width) AND `ARM_NO_COMPOSITION_CONTROL` <= 0.15 (so the composition mechanism is doing the work) AND `ARM_HRR_BIND` < `ARM_MEMORIZATION_BASELINE` by no more than 0.20 (composition recovers most of memorization performance without paying the storage cost) AND cv <= 0.10. Strictly-above-floor.
- MIDDLE_BAND: `ARM_HRR_BIND` in [0.35, 0.55] OR `ARM_NO_COMPOSITION_CONTROL` in [0.15, 0.25] (still below random but compositional mechanism gives only partial lift).
- HARD_FAIL: `ARM_HRR_BIND` within 0.05 of `ARM_NO_COMPOSITION_CONTROL` (composition mechanism gives no lift over no-composition; structurally null) OR `ARM_MEMORIZATION_BASELINE` <= 0.80 (memorization baseline broken; methodology drift; abort).

**Discriminator survives full-N (META_RULE_K):** at N_DIM=8192 with 1000 atomic facts + 200 heldout composed predicates, chain-grade multi-hop primitive at depth=2 gives ~0.808 for SEEN chains. Heldout COMPOSED predicates (unseen p1∘p2 patterns) should be at chance for NO_COMPOSITION arm; if NO_COMPOSITION >= 0.30 the heldout construction is leaky (composed predicates have learnable surface patterns — re-audit). Smoke at N_DIM=2048 with 200 atomic + 50 composed; full at N_DIM=8192 with 1000 + 200.

**By-construction-saturation check (Q-discipline):** if ARM_HRR_BIND saturates at >= 0.95, the composed predicates were derivable trivially from chain-grade depth-2 cleanup (already chain-grade). Pre-reg requires composed-predicate INFERENCE to use distinct unbind sequence than seen-chain retrieval (verified by logging substrate's composition path); if same path → vacuous-UD demote.

**Cost:** 3-5 hr remote_cpu_queue. Composes existing chain-grade KG + multi-hop primitives.

**Brain-grounding strength:** STRONG. Variable-binding via parietal cortex (Singer 1999; Treisman 1996 feature-binding); compositional semantics via inferior frontal gyrus (Pylkkanen 2019). HRR was designed by Plate 1995 specifically for role-filler composition.

**P_deflated:** 0.40 (raw lit P=0.60; -0.20 calibration; substrate's existing KG + multi-hop chain-grade gives strong base prior).

**Source:** USER explicit "variable-binding / role-filler" angle in drill objective; composes on chain-grade primitives.

---

### CELL 4 — typed_multibank_K128_adversarial_v1 (RESPEC of Wave 2 Anchor 2)

**Mechanism class:** Type-routed multibank WM. Composes chain-grade multibank K=4096 + chain-grade intent classifier n=100 + chain-grade refuse-gate V_REL=256.

**What it tests:** does explicit type labeling at the per-bank level (n_types=64) lift recall AND drive refuse-rate on type-mismatched queries to >= 0.85? Critical RESPEC from Wave 2 audit above: must NOT operate in by-construction-saturation regime (k_per_bank >= 64; adversarial FEATURE_OVERLAP_FRAC=0.40).

**Mechanistically distinct from cortex E-tensor:** types are EXTERNAL labels, not per-atom signal. No magnitude-coupling.

**Arms (3 mandatory):**
- `ARM_UNTYPED_BASELINE_ADVERSARIAL`: chain-grade multibank at K=8192, n_banks=128, OVERLAP=0.40. Sanity rail; must land in [0.60, 0.85] (NOT saturated; verified by smoke).
- `ARM_TYPED_ROUTING_MATCHED`: per-bank type label assigned matching content; routing-by-type; cleanup within bank. Tests typed-routing lift over untyped at NON-SATURATED regime.
- `ARM_TYPED_ROUTING_ADVERSARIAL_PROBE`: deliberately ill-typed queries (type label mismatches content); tests refuse-rate.

**Pre-reg bands (defensible against Q + META_RULE_L):**
- HARD_PASS: typed-recall >= ARM_UNTYPED_BASELINE_ADVERSARIAL + 0.10 AND refuse-rate on ill-typed >= 0.85 AND ARM_UNTYPED_BASELINE in [0.60, 0.85] (NOT saturated) AND cv <= 0.05.
- MIDDLE_BAND: typed-recall lift in [0.03, 0.10] OR refuse-rate in [0.50, 0.85].
- HARD_FAIL: typed-recall lift <= 0.02 (type signal not actionable) OR refuse-rate <= 0.40 OR ARM_UNTYPED_BASELINE >= 0.95 (by-construction-saturation; auto-demote per META_RULE_K).

**Discriminator survives full-N:** smoke at N_DIM=8192, K_total=8192, n_banks=128, OVERLAP=0.40. ARM_UNTYPED_BASELINE_ADVERSARIAL must land in [0.60, 0.85] at smoke or RESPEC the OVERLAP_FRAC up until it does. Without baseline in non-saturated band, the cell is vacuous.

**Cost:** ~1-1.5 hr remote_cpu_queue.

**Brain-grounding strength:** MEDIUM. Multi-bank routing analog of basal-ganglia thalamic loops (Houk-Adams-Barto 1995) + IT cortex feature-grouping. Less direct than CELL 1/2/3.

**P_deflated:** 0.45 (raw lit P=0.65; -0.20 calibration; HIGH P because composes on 3 chain-grade primitives; respec'd to avoid saturation).

**Source:** Wave 2 Anchor 2 audited + corrected above.

---

### CELL 5 — holographic_chunk_pack_unroutable_regime_v1 (REFINED Wave 2 Anchor 7)

**Mechanism class:** Training-time precomputed 2-hop chunk atoms; query-time multi-hop = chunk lookup. Mechanism-class-distinct from chain-grade partition-oracle (which is query-time routing).

**What it tests:** does holographic chunk-pack add UNIQUE COVERAGE on queries where partition-oracle's partition-key is NOT derivable? This is the regime where chain-grade partition-oracle's depth-15 chain-grade DOES NOT APPLY.

**Mechanistically distinct from chain-grade partition-oracle:** different mechanism class (training-time precomputation vs query-time routing). Different failure mode (storage cost vs routing cost). Different regime (closed-world chunks vs open-world routing). USER directive 2026-06-26: kept despite partition-oracle chain-grade because mechanism class is orthogonal.

**Arms (4 mandatory):**
- `ARM_PARTITION_ORACLE_BASELINE_ROUTABLE`: chain-grade partition-oracle on routable queries (depth-5/10/15). Sanity rail; must replicate chain-grade 0.965/0.857/0.808.
- `ARM_PARTITION_ORACLE_BASELINE_UNROUTABLE`: partition-oracle on UNROUTABLE queries (queries with no derivable partition key). MUST be at chance (verifies the unroutable regime exists; if partition-oracle still works here, the cell premise is broken).
- `ARM_HOLOGRAPHIC_CHUNK_ONLY_UNROUTABLE`: chunk-pack on unroutable queries. PROPOSED mechanism.
- `ARM_PARTITION_PLUS_CHUNK_COMPOSED`: routes via partition-oracle when key derivable; falls back to chunk lookup when not. Tests composition with chain-grade primitive.

**Pre-reg bands (defensible against Q + META_RULE_L):**
- HARD_PASS: `ARM_HOLOGRAPHIC_CHUNK_ONLY_UNROUTABLE` >= 0.50 AND `ARM_PARTITION_ORACLE_BASELINE_UNROUTABLE` <= 0.15 (unroutable regime verified) AND `ARM_PARTITION_ORACLE_BASELINE_ROUTABLE` replicates chain-grade within 0.05 AND `ARM_PARTITION_PLUS_CHUNK_COMPOSED` >= max(partition_routable, chunk_unroutable) - 0.05 (composition preserves both regimes) AND cv <= 0.08.
- MIDDLE_BAND: chunk-only unroutable in [0.30, 0.50] OR composed arm reduces routable performance by 0.05-0.15.
- HARD_FAIL: `ARM_PARTITION_ORACLE_BASELINE_UNROUTABLE` >= 0.30 (unroutable regime not actually unroutable; cell vacuous; abort) OR chunk-only unroutable <= 0.20 (chunk-pack doesn't work) OR composed arm < partition_routable - 0.20 (composition contaminates routing).

**Discriminator survives full-N (META_RULE_K):** smoke must EMPIRICALLY verify the unroutable regime exists. If partition-oracle solves "unroutable" queries (proving they're actually routable), the cell premise is null. Smoke check: partition-oracle baseline on smoke "unroutable" set must be <= 0.15 — if >= 0.15, RESPEC the unroutable construction or abort.

**Cost:** ~4-5 hr remote_cpu_queue (chunk precomputation + query lookup). USER kept despite partition-oracle chain-grade per orthogonal-mechanism-class reasoning.

**Brain-grounding strength:** WEAK. Brain analog (memory-palace mnemonics; hippocampal sharp-wave replay precomputing trajectories) is suggestive but not chain-grade analog. The cell is more substrate-engineering than brain-grounded.

**P_deflated:** 0.35 (raw lit P=0.55; -0.20 calibration; weaker brain prior; engineering-focused).

**Source:** Wave 2 Anchor 7 with discriminator refined to verify unroutable regime is real.

---

## Section 3: Priority order + sequencing rationale

| Rank | Cell | P_deflated | Cost | Brain-ground | Reason for rank |
|---|---|---|---|---|---|
| 1 | CELL 1 cls_two_tier_BCM_slow_replay_v1 | 0.45 | 6-10 hr | STRONG | Highest P; brain-existence-proof TWO_TIER; composes on NREM proven-bound; closes Gap 3 the brain's way |
| 2 | CELL 2 emergent_slot_via_query_cluster_discovery_v1 | 0.40 | 4-6 hr | STRONG-MEDIUM | USER load-bearing distinction (discover vs execute); composes on chain-grade SEMANTIC + ultrametric |
| 3 | CELL 3 predicate_composition_role_filler_v1 | 0.40 | 3-5 hr | STRONG | Variable-binding angle USER explicitly called out; composes on chain-grade KG + multi-hop |
| 4 | CELL 4 typed_multibank_K128_adversarial_v1 | 0.45 | 1-1.5 hr | MEDIUM | Highest P/cost ratio; respec'd to escape saturation; foundational for CELL 2 ARM_PRESCRIBED rail |
| 5 | CELL 5 holographic_chunk_pack_unroutable_regime_v1 | 0.35 | 4-5 hr | WEAK | Mechanism-distinct orthogonal coverage; USER kept; engineering-focused |

### Dispatch sequencing

**Wave A (parallel; can run concurrently on remote_cpu_queue; total ~1.5 hr + 6-10 hr):**
- CELL 4 typed_multibank_K128_adversarial_v1 (FIRST — 1-1.5 hr; cheapest; produces upper-bound rail for CELL 2)
- CELL 1 cls_two_tier_BCM_slow_replay_v1 (parallel with CELL 4 — 6-10 hr; HIGHEST priority but slowest)

**Wave B (after CELL 4 lands so CELL 2 has its rail):**
- CELL 2 emergent_slot_via_query_cluster_discovery_v1 (4-6 hr; uses CELL 4 as ARM_PRESCRIBED upper bound)
- CELL 3 predicate_composition_role_filler_v1 (3-5 hr; independent of others; can dispatch in parallel with CELL 2)

**Wave C (conditional):**
- CELL 5 holographic_chunk_pack_unroutable_regime_v1 (dispatch only if Wave A+B leaves spare slot; lowest brain-grounding)

### Rationale for sequencing

- CELL 4 dispatch FIRST because it's cheapest AND its output (typed-multibank-routing chain-grade or HARD_FAIL) is REQUIRED as the upper-bound rail for CELL 2. If CELL 4 HARD_FAILs at adversarial OVERLAP=0.40, CELL 2's ARM_PRESCRIBED rail also collapses; re-scope both.
- CELL 1 dispatch in PARALLEL with CELL 4 because it's the highest-P-individually AND independent of the other cells. 6-10 hr means dispatch ASAP.
- CELLs 2+3 dispatch after CELL 4 lands (~1-1.5 hr wait).
- CELL 5 last because lowest brain-grounding and orthogonal to the core Stage 3 question.

### Spawn budget per Fix #14

≤3 in flight. So:
1. Spawn `hdi_orchestrator` to queue_add CELL 1 + CELL 4 simultaneously on remote_cpu_queue (CELL 1 to overnight_queue per cost; CELL 4 to remote_cpu_queue per Fix #24 routing rule).
2. After CELL 4 lands, spawn second orchestrator to queue_add CELLs 2+3.
3. Wait for ≥2 to land before spawning CELL 5.

---

## Section 4: Cross-cell discipline contract

All 5 cells:
- META_M7 reproduce-once rail (smoke at full-N seed subset)
- META_RULE_K smoke must FIRE discriminator (vacuous-UD auto-demote)
- META_RULE_L band-floor results MUST be classified MIDDLE_BAND not HARD_PASS
- META_RULE_J no silent except — record+halt OR re-raise
- META_RULE_F: NO claims involving per-atom importance correlated with |W|
- Fix #28 default tier MIDDLE; let Skunkworks tier UP via per-arm metrics
- Fix #14 ≤3 cell-author spawns in flight
- Fix #17 cell-author smoke MANDATORY before full dispatch — ON REMOTE per USER 2026-06-27 D9
- Fix #24 GPU dispatch (CELL 1 if routed to overnight_queue) MUST actually use GPU (torch.cuda + batched ops)
- Fix #26 predispatch_check.py per cell-author spawn
- ASCII-only; no unicode; no emojis in scripts
- 3 seeds minimum for chain-grade eligibility; cv ≤ 0.05 for chain-grade-definitive; cv ≤ 0.08-0.10 for chain-grade per cell tolerance
- Per-arm metrics MANDATORY in metrics.json (`per_arm_metrics` dict); NOT inferred from verdict_msg

### NO-MAGNITUDE-COUPLING REGRESSION

Three cortex E-tensor cells HARD_FAILed for the SAME structural reason: cor(E, |W|) = 0.996 (META_RULE_F). All 5 cells above use mechanisms ORTHOGONAL to weight magnitude:
- CELL 1 BCM uses output activity (y * (y - theta_M)), not |W|
- CELL 2 ultrametric uses cosine distance between W rows (direction not magnitude)
- CELL 3 HRR bind uses convolution (direction-preserving)
- CELL 4 typed multibank uses per-bank routing (independent of |W|)
- CELL 5 holographic chunk uses precomputed bindings (direction-preserving)

**Sanity check:** for each cell, verify cor(mechanism_score, |W|) < 0.5 in smoke; if >= 0.5, cell has fallen into the cortex E-tensor failure mode; demote to MM regardless of verdict.

---

## Section 5: What's NOT in this design (and why)

- **More cortex E-tensor variants:** META_RULE_F structural; 3 attempts at this mechanism class HARD_FAILed; close until brain-grounded alternative path appears.
- **Modern Hopfield v2 with substrate-mined beta:** prior `gap3_modern_hopfield_prototype_attractor_v1` MIDDLE_BAND at 0.26 is below floor; substrate-mining likely won't lift to 0.65; deferred unless CELL 1 also fails (at which point pivot to deep-Hopfield re-derivation of beta).
- **SOLAR cross-attention slot binding (LARS-VSA arm):** root cause of LARS-VSA HARD_FAIL is HRR-bind ceiling + harness leak; SOLAR adds cross-attention which is novel-synthesis (not chain-grade primitive); deferred unless CELL 1+2+3 all HARD_FAIL.
- **Hierarchical predictive coding (rank-3 from deeper drill):** good idea but adds calibration/refuse-gate value at LOWER P_solve than CELL 1; deferred unless CELL 1 HARD_FAILs.
- **Annealed Langevin diffusion / SDM softmax aggregation:** substrate's existing iterative_attractor already approximates these; not the bottleneck per deeper-drill Section 2 analysis.

---

## Section 6: Open questions for USER on return

1. **CELL 1 dispatch authorization:** 6-10 CPU-hr is the longest single cell in this batch. OK to dispatch in parallel with CELL 4 (smaller) on overnight_queue?
2. **CELL 5 priority:** willing to deprioritize CELL 5 (lowest brain-grounding) entirely if Wave A+B HARD_PASS exhausts spawn budget; defer indefinitely.
3. **Fallback if CELL 1 HARD_FAILs:** pivot to hierarchical predictive coding (CELL 3 from deeper drill rank-3) OR re-derive Modern Hopfield with substrate-mined beta sweep. USER preference?
4. **Stage 3 success criterion:** is ≥2 of 5 cells HARD_PASS sufficient for "Stage 3 has a path" or do we need ≥3?

---

## Section 7: References

Internal:
- `notes/director_POST_COMPACTION_BACKUP_FULL_STATE_2026-06-27.md` (current state)
- `notes/director_MASTER_PLAN_substrate_full_state_2026-06-25.md` (Gap 3)
- `notes/research_gap3_compositional_deeper_mechanism_drill_2026-06-26.md` (rank-1 Modern Hopfield since LANDED MIDDLE_BAND; rank-2 CLS-replay is now CELL 1)
- `notes/research_gap3_brain_slow_schema_mechanism_2026-06-26.md` (CLS BCM brain mechanism)
- `notes/research_STRATEGIC_PIVOT_language_track_closed_compositional_understanding_opens_2026-06-26.md` (pivot frame)
- `notes/exp_dev_handoff_research_first_wave_7_compositional_understanding_USER_GREENLIT_2026-06-26.md` (Wave 1 + Wave 2 7 anchors; this drill audits anchors 2/4/5/7)
- `memory/feedback_substrate_doesnt_know_anything_stop_testing_against_language_USER_LOCKED_2026-06-26.md`
- `memory/feedback_experiment_bias_master_checklist_USER_2026-06-24.md` (BIAS-13/14/15)
- `memory/feedback_stage_progression_1234_dont_skip_USER_LOCKED_2026-06-26.md`
- `memory/feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26.md`

Empirical anchors (landed; verdict-read):
- `data/exp_gap3_modern_hopfield_prototype_attractor_v1/metrics.json` MIDDLE_BAND best=0.26
- `data/exp_substrate_cortical_schema_extraction_compositional_generalization_v1/metrics.json` MIDDLE_BAND feature-based=0.4733
- `data/exp_gap3_lars_vsa_relational_bottleneck_v1_n8192/metrics.json` HARD_FAIL_CONFOUND
- `data/exp_cortex_E_tensor_separate_importance_v1/metrics.json` HARD_FAIL (3x — META_RULE_F structural)
- `data/exp_pc_cleanup_attractor_v1/metrics.json` HARD_PASS (saturated; META_RULE_L flag)
- `data/exp_pc_cleanup_deeper_chains_v1/metrics.json` HARD_FAIL (VAN@d20=1.000 by-construction)
- `data/exp_topk_composition_refuse_gate_v1/metrics.json` HARD_PASS (saturated; engineered-ambiguity follow-up FAIL)
- `data/exp_gap4_two_tier_generational_W_v1/metrics.json` HARD_PASS_PARTIAL (drift-reduction; not compositional)
- `data/exp_cls_replay_continual_learning_smoke_v1/metrics.json` HARD_FAIL (CLS-replay continual; mechanism present but different test)
- `data/exp_substrate_stage1_SEMANTIC_concept_learner_battery_v3_CV_TIGHTENING/metrics.json` HARD_PASS 6/6 (A3 heldout=1.000 saturated; A4 compose=0.533 = the regime CELL 2 should target)
- `data/exp_phase_diagram_working_memory_multibank_K_extension_to_16384_v1/metrics.json` chain-grade K=4096 MULTI_64x (foundation for CELL 4)

External (top references):
- McClelland, McNaughton, O'Reilly (1995). "Why there are complementary learning systems." Psych Rev 102(3): 419-457.
- Kumaran, Hassabis, McClelland (2016). "What learning systems do intelligent agents need?" TICS 20(7): 512-534.
- Bienenstock, Cooper, Munro (1982). "Theory for the development of neuron selectivity." J Neurosci 2(1): 32-48. (BCM rule.)
- Plate (1995). "Holographic Reduced Representations." IEEE TNN 6(3): 623-641. (HRR crosstalk capacity.)
- Tse, Langston, et al. (2007). "Schemas and memory consolidation." Science 316(5821): 76-82. (Rat schema rapid-acquisition; CELL 1 grounding.)
- Patterson, Nestor, Rogers (2007). "Where do you know what you know?" Nat Rev Neurosci 8(12): 976-987. (Semantic hub for CELL 2.)
- Pylkkanen (2019). "The neural basis of combinatory syntax and semantics." Science 366(6461): 62-66. (Compositional semantics for CELL 3.)

---

-- Research (Opus 4.7-1M) — 2026-06-27 (USER offline window; review on return)
