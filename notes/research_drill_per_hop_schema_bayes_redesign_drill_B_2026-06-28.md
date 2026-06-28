# RESEARCH DRILL B: per-hop schema-Bayes redesign (substrate-native partition output that is per-hop, not hop-0-locked)

**Date:** 2026-06-28
**Role:** research (Director)
**Drill type:** 2x (level-2 operational drill on Drill A's HARD_FAIL diagnosis; per `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28` — different mechanism class than Drill A)
**Trigger:** Drill A (`research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md`) HARD_FAILed all 3 adapters at smoke today (verdict `exp_dev_verdict_pfc_wm_state_tracker_smoke_HARD_FAIL_all_3_adapters_2026-06-28.md`). Root cause CONFIRMED MEASURED@2026-06-28: `cluster_to_target_part[k]` is built from `chains_train[ci][0][2] // PART_SIZE` — hop-0 target partition only. Every cluster maps to a hop-0 partition; per-hop partition-acc capped at 1/N_PARTS=0.20=chance regardless of state-conditioning.
**Anchor cell (proposed):** `exp_substrate_partition_oracle_trajectory_schema_per_hop_v1`
**Brain-grounded prior:** P=0.50 gross (novel-synthesis cap per lit-scan calibration penalty); deflated to P=0.32 after signal-shape audit on the chosen candidate (Candidate B — trajectory-encoded schema via sequence-binding chain-grade primitive)
**Discipline anchors applied:** META_RULE_AM (substrate-already-does-X check via existing primitive registry), `feedback_chain_grade_primitives_not_trivially_composable_2026-06-28.md` (signal-shape audit MANDATORY at each edge), `feedback_functional_requirement_first_test_design_USER_2026-06-28.md` (decompose into FRs first), `feedback_substrate_as_canonical_query_first_USER_LOCKED_2026-06-27.md` (substrate-KB query FIRST — performed; KB v1 returned schema_version_mismatch refusal, fallback to direct read), `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28` (2x drill discipline — Drill B is the different-mechanism-class second drill), `feedback_no_hallucinated_numbers_verify_on_disk_2026-06-27` (all numbers tagged MEASURED@/THEORETICAL@/CITED@), `feedback_discriminator_must_survive_scale_before_full_dispatch_USER_2026-06-26`.

---

## HEADLINE (one line)

The per-hop partition output gap is a **primitive-redesign problem, not an adapter problem**: replacing the hop-0-locked `cluster_to_target_part[k]` map with a per-(hop_idx, cluster) trajectory map built via the substrate's chain-grade sequence-binding primitive (K=20 native shape) gives SHAPE_MATCH for FR3+FR4 without inventing a new primitive class. Candidate B (trajectory-schema via sequence-binding) wins the signal-shape audit; Candidate A (per-hop chunk-schema) is brute-force feasible but 15x cluster-count blow-up; Candidate C (skip schema, train per-step decoder) violates the "reuse chain-grade primitives" discipline. **RECOMMENDATION: SPAWN_CELL_AUTHOR** for Candidate B with explicit HARD_FAIL gates that close the brain-faithful 4-primitive box if it fails.

---

## Cheap decisive test

**Anchor cell pre-reg:** `exp_substrate_partition_oracle_trajectory_schema_per_hop_v1`

**Arms (6; cardinality_ok mandatory; arms_distinct gate REQUIRED — Drill A failed META_RULE_AF due to SUB_B === SUB_C hash collision):**

| Arm | Mechanism | Purpose |
|---|---|---|
| `A_BASELINE` | per-hop cleanup, no hint, no WM (replicates v5_hardened ARM A; MEASURED@v5 0.39) | Reproduces 0.40 floor at depth=15 |
| `B_PATH2_PERCHAIN` | schema-Bayes once per chain (today's Drill-A HARD_FAIL repro) | MEASURED@PATH2 0.01 — sanity-check we reproduce the prior bottom |
| `C_PATH3_4PRIM_HOP0_LOCKED` | 4-primitive with hop-0-locked schema map (Drill A's best adapter SUB_A; MEASURED@2026-06-28 0.0000) | Reproduces the Drill-A HARD_FAIL — discriminator against trajectory mechanism |
| `D_PATH4_TRAJECTORY_SCHEMA` | **THE NEW MECHANISM**: sequence-binding S matrix bound on (cluster_k @ hop_idx) -> target_partition pairs from training trajectories; at inference, schema-Bayes picks cluster k, then `target_part = readout(S, k_vec ⊕ hop_code_i)` per hop | The mechanism arm — tests per-hop partition output |
| `E_ORACLE_PER_HOP` | ground-truth partition cue per hop, then cleanup | Upper bound (MEASURED@v5 0.84) |
| `F_RANDOM` | random partition cue per hop | Lower bound; refuse-test |

**Pre-reg dimensions (lock per `feedback_discriminator_must_survive_scale_before_full_dispatch`):**
- N=8192, V_C=4000, V_P=10, depth=15 (MATCHES Drill A so discriminator survives)
- n_chains_train=200, n_chains_test=200 (full) / n_chains_test=100 (smoke)
- n_partitions=5, part_size=800
- n_schemas=20, K_seq=20 (sequence-binding K cap; CHAIN-GRADE primitive K)
- seeds=[7, 13, 19] for full; smoke=[7] at full N+depth (Check A: smoke at full scale)
- WM_BANK_K=200 (unused in D mechanism but available for FR1+FR2 future composes)

**HARD-PASS thresholds (per cell):**
- `D_PATH4` in [0.50, 0.95]
- `D_PATH4 − C_PATH3` ≥ 0.30 (trajectory schema adds genuine value over hop-0-locked schema)
- `D_PATH4 − A_BASELINE` ≥ 0.20 (mechanism beats no-hint floor)
- per-hop partition accuracy in D at hops 5/10/15 > 0.50 (NOT chance 0.20)
- `E_ORACLE > D_PATH4 > C_PATH3 ≥ B_PATH2 ≥ F_RANDOM` ordering preserved
- arms_distinct=True (SHA-256 hash distinct across all 6 arms; META_RULE_AF gate)
- cv_max < 0.15 across 3 seeds
- cardinality_ok=True (expected_n_units=6 * 3 = 18 at full)
- saturated_any=False (no arm at HP_SATURATION_CEIL=0.95)
- `_llm_forward_calls_at_inference == 0` (substrate-only inference)

**HARD-FAIL thresholds (CLOSES brain-faithful 4-primitive composition per 2x-drill discipline):**
- `D_PATH4` ≤ 0.30 (trajectory-schema doesn't rescue — primitive class confirmed insufficient)
- OR `D_PATH4 − C_PATH3` < 0.10 (no lift over hop-0-locked — primitive redesign delivers nothing)
- OR `D_PATH4 < A_BASELINE` (mechanism HURTS — cascade collapse; trajectory binding noise worse than no hint)
- OR per-hop partition-acc in D ≤ 0.25 at hop 10 (close to chance — trajectory readout decays faster than crosstalk floor)
- OR arms_distinct=False (D collapses to C or B argmax — implementation bug; reject before claiming HARD_FAIL on mechanism)

**MIDDLE_BAND:** `D_PATH4` in [0.30, 0.50] AND lift over C ≥ 0.10 — trajectory schema is partial; capability box stays open for one more drill (e.g., trajectory-encoded schema co-trained with WM bank).

**Smoke gate (MANDATORY before full dispatch):**
- smoke = seed=[7] at full N=8192, depth=15, n_chains_test=100 (Check A: full-N smoke; discriminator survives if D > C by ≥ 0.20 at smoke)
- If smoke shows `D − C < 0.10`: REJECT full dispatch; cell HARD_FAIL_DISCRIMINATOR_FAILS_AT_SMOKE; brain-faithful 4-primitive box closes

---

## Falsifiable predictions

| Prediction | HARD-PASS | HARD-FAIL |
|---|---|---|
| (P1) Sequence-binding K=20 capacity is sufficient to encode (cluster_k, hop_idx) → target_partition trajectories at N=8192 | per-(k,hop) readout cosine > 0.40 (above CROSSTALK_PART=0.31) across all hops 0-14 | per-(k,hop) readout cosine < 0.20 (below crosstalk; noise floor) by hop 10 |
| (P2) Trajectory-schema gives per-hop partition discrimination above chance | per-hop part-acc in D at hops 5/10/15 in [0.45, 0.90] | per-hop part-acc < 0.30 at hop 10 |
| (P3) Replacing the hop-0-locked map with trajectory readout rescues PATH3 4-primitive | D_PATH4 − C_PATH3 ≥ 0.30 | D_PATH4 − C_PATH3 < 0.10 |
| (P4) The 4-primitive composition with trajectory schema extends to depth=15 without cascade collapse | D per-step accuracy stays > 0.45 across hops 5-15 (monotonically degrading less than per-hop crosstalk implies) | D per-step accuracy drops > 50% from hop 5 to hop 15 |

**Lit-scan calibration penalty applied (per `feedback_lit_scan_calibration_penalty`):**
- Gross P = 0.55 (sequence-binding K=20 is chain-grade MEASURED@2026-06-22 HARD_PASS commit a27939c5; mechanism reuses native primitive shape; brain analogy strong)
- Deflate by 0.23 for: (a) novel composition of sequence-binding S-matrix into vmPFC/cortex primitive interface — no published substrate-VSA precedent (b) chained Hebbian outer-product (cluster × hop_code) trajectory write is K=N_SCHEMAS×DEPTH=300 effective writes per chain, near K=20 cap interpretation that's BIOLOGICAL-grounded but UNTESTED in substrate at this superposition density (c) Edge-2 (schema cluster posterior → trajectory readout key) requires synthesizing a query key from cluster argmax + hop_code which is a NEW bind operation
- **P_deflated = 0.32**

**Lit-scan caps:** novel-synthesis cap P ≤ 0.50 from `feedback_lit_scan_calibration_penalty` — P_deflated=0.32 ≤ 0.50, OK.

---

## Cross-thread synthesis

### Literature scan (lean, 350 words)

**Mante & Sussillo 2013** (re-cited; "Context-dependent computation by recurrent dynamics in PFC", Nature 503:78-84): the classic monkey-PFC paper. KEY OVERLOOKED FINDING — PFC dynamics encode context updating **PER STEP within a trial**, not just at trial onset. The recurrent dynamics absorb each successive stimulus and reshape the context vector. This is precisely the requirement: per-hop schema firing, not chain-once. CITED@2026-06-23 (partition-oracle goal-conditioning); RE-CITED 2026-06-28 in Drill A; RE-RE-CITED here for per-step (not chain-onset) interpretation.

**Miller & Cohen 2001** (re-cited; "An integrative theory of prefrontal cortex function", Annu Rev Neurosci 24:167-202): dlPFC re-establishes goal/context at each step. The "schema fires once" interpretation of vmPFC schema-Bayes is INCONSISTENT with brain — Miller-Cohen's PFC re-activates task-relevant biases continuously. Re-cited 2026-06-28 for "per-step" reading specifically (Drill A focused on "WM state stores" reading; this drill focuses on "per-step re-firing" reading).

**Frady & Sommer 2020** (re-cited; "Functional modeling of working memory", Nat Mach Intell): K-slot WM bank substrate analog is chain-grade. Re-cited here for **slot-indexed key as hop-code basis** — using hop_idx as slot key gives a clean per-hop addressing in the same shape-class as the substrate's existing chain-grade WM bank.

**Plate 2003** (re-cited; HRR book, ch. 6 on contextually-modulated cleanup): the substrate's contextual-bind pattern is the architectural template for trajectory-schema. Plate's binding `c ⊗ x` for context-modulated retrieval is structurally equivalent to `cluster_k ⊗ hop_code_i → target_partition` readout. RE-CITED 2026-06-22 (B36), 2026-06-28 (Drill A), and here for Edge-2 readout specifically.

**Hersche, Rahimi, et al. 2023** ("Factorizers", Nat Mach Intell; relevant for resonator decomposition): resonator networks decompose superposed bound objects via iterated cleanup. RELEVANT for Candidate B: the trajectory readout `S @ (cluster_k ⊕ hop_code_i)` can be cleaned up via resonator-style iteration if direct readout is noisy. CITED@2026-06-22 Hersche-extension drill; first time cited here for trajectory-schema cleanup.

**Hopfield & Krotov 2020 dense Hopfield generalizations**: trajectory-schema readout is structurally a Modern-Hopfield query — if direct sequence-binding readout proves insufficient capacity, the Modern-Hopfield exponential-capacity readout is the fallback. NOT used in Candidate B v1 (which uses the substrate's chain-grade S matrix); reserved as v2 fallback.

**NOVEL@2026-06-28:** the synthesis of (a) per-step PFC firing (Mante-Sussillo) + (b) substrate sequence-binding S-matrix as a (cluster × hop) → partition trajectory store + (c) hop_idx as native slot key (Frady-Sommer) into a single primitive is a substrate-native recasting that has no published direct precedent. Hence the novel-synthesis cap P ≤ 0.50.

### Substrate-primitive coverage map (per `feedback_functional_requirement_first_test_design`)

Updated FR table with TRAJECTORY-SCHEMA recasting:

| FR | Plain English | Drill-A primitive | Drill-B primitive (CANDIDATE B) |
|---|---|---|---|
| FR1 | Maintain accumulated state across hops | WM multi-bank K=4096 (chain-grade) | WM multi-bank K=4096 (chain-grade); UNCHANGED |
| FR2 | Update state per hop with current (s_pred, p_next, hop_idx) | WM bank slot writes (chain-grade) | WM bank slot writes (chain-grade); UNCHANGED |
| FR3 | **Re-fire schema-Bayes posterior conditional on current state** | NO chain-grade primitive — SHAPE_MISMATCH (Drill A confirmed HARD_FAIL) | **Schema-Bayes posterior + sequence-binding trajectory-key bind** — chain-grade composition (S matrix MEASURED@2026-06-22 HARD_PASS K=20 N=4096 at delta=1.0) |
| FR4 | **Per-hop partition output (not hop-0-locked)** | hop-0-locked map (BUG — all clusters map to hop-0 partition) | **Trajectory map: `(cluster_k, hop_i) → target_partition_at_hop_i`** built via sequence-binding S on training chains; readout per hop via key bind |
| FR5 | Cleanup within selected partition | partition_routing + restricted cleanup (chain-grade) | partition_routing + restricted cleanup (chain-grade); UNCHANGED |

**Verdict from coverage map:** 5 of 5 functional requirements now covered by existing chain-grade primitives WITH ONE NEW BIND OPERATION (`cluster_k ⊕ hop_code_i`) that is structurally identical to existing FHRR-style multi-factor binding. SHAPE_MATCH at every edge except the new bind operation, which is **SHAPE_MATCH_with_native_primitive (sequence-binding S)**.

### Substrate-product implications

- **If HARD_PASS (P_deflated=0.32):** the 4-primitive composition gives brain-faithful per-hop schema re-firing at depth 15. The trajectory-schema primitive is a NEW chain-grade-eligible composition pattern (substrate-novel recasting of vmPFC schema firing). Substrate-product story: "substrate-native dlPFC + chain-grade WM bank + trajectory-schema vmPFC + partition routing + cleanup = complete cortex-grade reasoning chain at depth 15". This is the M3 multi-hop-chain barrier-1 breakthrough.
- **If MIDDLE_BAND:** trajectory-schema is the right architectural direction but capacity-bound at K=20. Capability box stays open for v2 (Modern-Hopfield exponential-capacity readout or resonator-cleaned iterative readout).
- **If HARD_FAIL (per 2x-drill discipline triggers capability closure):** brain-faithful 4-primitive composition closes definitively. The substrate's chain-grade primitive set is **insufficient** for brain-faithful per-hop multi-hop chain reasoning at depth 15. M3 must pivot to either (a) non-brain-faithful composition (external cortex layer / learned co-training adapter) or (b) per-state schema retraining (5th primitive class — NEW BIOLOGICAL primitive needed, e.g., dopaminergic gating of per-state schemas). Per META_RULE_AO and the user 2x-drill discipline, this CLOSURE is principled — two structurally-different mechanism classes (state-bias adapter in Drill A; trajectory-schema redesign in Drill B) both failing is the operational closure trigger.

---

## Signal-shape compatibility audit (MANDATORY per `feedback_chain_grade_primitives_not_trivially_composable`)

This is the load-bearing section that determined P_deflated=0.32. **All 3 candidates audited; B chosen.**

### CANDIDATE A: per-hop chunk-schema

- **Mechanism:** instead of one schema-Bayes posterior per chain, build N_SCHEMAS × DEPTH = 300 separate clusters where cluster_(k, h) is trained on (chain_h-th-hop-prefix, chain_h-th-hop-target-partition) tuples
- **Edge 1: WM bank → schema-Bayes input** — SHAPE_MATCH (same as Drill A SUB_A; state-bias on per-(k,h) posterior)
- **Edge 2: schema posterior → partition output** — SHAPE_MATCH (per-(k,h) cluster maps directly to per-hop partition; NO trajectory primitive needed)
- **Cost:** 15× cluster count blow-up; training-data fragmentation (200 chains × 15 hops = 3000 training tuples but spread across 300 clusters = 10 chains/cluster — sparse)
- **Risk:** with only ~10 chains/cluster, schema prototypes are noisy
- **VERDICT:** SHAPE_MATCH, mechanism is feasible, but capacity-noisy
- **NOT chosen** because it does not reuse a chain-grade primitive in its native shape; the "per-hop clustering" is a NEW operation not in the chain-grade portfolio

### CANDIDATE B (CHOSEN): trajectory-encoded schema via sequence-binding

- **Mechanism:**
  - Build schema-Bayes prototypes as in Drill A (N_SCHEMAS=20 clusters from chain predicate sequences) — UNCHANGED chain-grade
  - Build per-cluster trajectory templates: for each cluster k, for each training chain c with chain_to_schema[c]=k, bind `(cluster_k_vec ⊕ hop_code_i)` → `target_partition_vec_at_hop_i` into sequence-binding S matrix
  - At inference: for hop i in chain q:
    1. Compute q_schema = chain_schema_vector(q[:i+1], R) (per-hop schema query — using PAST hops only; same as Drill A SUB_C)
    2. k_pred = argmax(prototypes @ q_schema) (schema-Bayes posterior; same primitive)
    3. trajectory_key = cluster_k_codes[k_pred] * hop_code[i] (FHRR-style multi-factor bind; native primitive)
    4. partition_vec = S @ trajectory_key (sequence-binding readout; chain-grade)
    5. target_part = argmax(partition_codes @ partition_vec) (5-way cleanup; primitive)
    6. Partition-restricted cleanup over E[partition slice] (chain-grade)
- **Edge 1: WM bank → schema-Bayes input** — UNUSED in v1 (WM bank not required for per-hop schema; trajectory readout is the per-hop variation source). Can be RE-ADDED in v2 if D HARD_PASSes and we want richer state-conditioning.
- **Edge 2: schema posterior (cluster_k argmax) → trajectory readout key** — NEW BIND OPERATION `cluster_k_codes[k_pred] * hop_code[i]`. Both factors are bipolar; element-wise product is a native FHRR/bipolar bind. SHAPE_MATCH_with_native_primitive.
- **Edge 3: trajectory readout key → S matrix readout** — SHAPE_MATCH (sequence-binding S matrix is literally a key→value store; chain-grade MEASURED@2026-06-22 at K=20 N=4096)
- **Edge 4: partition vector → partition codes argmax** — SHAPE_MATCH (standard cleanup; 5-way partition codebook)
- **Edge 5: argmax partition → restricted cleanup** — SHAPE_MATCH (partition_routing primitive; chain-grade)
- **Capacity check (THEORETICAL@):** effective K for S matrix = N_SCHEMAS × DEPTH = 300 trajectory pairs at N=8192. Sequence-binding K-cliff phase diagram MEASURED@2026-06-28 (`exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_*_v1`) showed per-slot retrieval > 0.85 at K=4096 N=8192. At K=300 N=8192 we are well below the cliff (KS ratio = 300/8192 = 0.037 << 0.50 K/N=0.56 capacity-cliff threshold from existing 4-cell substrate atlas). **CAPACITY-FEASIBLE.**
- **Critical caveat (HYPOTHESIZED@):** the binding `cluster_k_codes[k_pred] * hop_code[i]` creates 300 distinct keys, but the readout values (partition codes) are only 5 distinct vectors with 300/5 = 60 mean superposition. The S matrix is writing 60 copies of each partition vector under different keys — equivalent of "60-fold redundancy per partition value". This should give STRONG cleanup signal. THEORETICAL@: SNR ≈ sqrt(60) / sqrt(300-60) ≈ 7.75/15.5 ≈ 0.50 raw, well above chance.
- **VERDICT:** SHAPE_MATCH at every edge using ONLY chain-grade primitives + ONE FHRR-native bind operation. **CHOSEN as drill candidate.**

### CANDIDATE C: skip schema; per-step partition decoder

- **Mechanism:** drop schema-Bayes entirely; train a direct decoder D(state, hop_idx) → partition. Use sequence-binding K=20 to store (state, hop_idx) → partition pairs from training chains.
- **Edge 1: state encoder** — SHAPE_MATCH (existing hop_state_vector primitive)
- **Edge 2: (state, hop_idx) → partition via S matrix** — SHAPE_MATCH (same primitive as Candidate B)
- **Risk:** ~3000 training pairs (200 chains × 15 hops) at K=20 mean superposition; per-pair SNR is low; partition recovery is essentially "find argmax via S matrix" which becomes a clean-up problem
- **Discipline violation:** abandons schema-Bayes primitive entirely. Per `feedback_functional_requirement_first_test_design`, this is a "new primitive class" approach NOT a "compose chain-grade primitives" approach. Higher novel-synthesis risk; LOWER reuse of brain-grounded chain-grade architecture.
- **VERDICT:** SHAPE_MATCH but structurally violates "reuse existing chain-grade primitives" discipline. **NOT chosen** for cell-author spawn; reserved as v2 fallback if Candidate B HARD_FAILs.

### Audit summary

| Candidate | Shape verdict | Chain-grade reuse | Capacity feasible | Chosen |
|---|---|---|---|---|
| A: per-hop chunk-schema | SHAPE_MATCH | Partial (new per-hop clustering op) | Sparse (10 chains/cluster) | No |
| **B: trajectory-schema via S matrix** | **SHAPE_MATCH_native** | **Full (3 chain-grade + 1 FHRR-bind)** | **Yes (K=300 << capacity)** | **YES** |
| C: skip schema, direct decoder | SHAPE_MATCH | Partial (drops schema-Bayes) | Marginal (K=3000) | No (reserve as v2) |

**Per `feedback_chain_grade_primitives_not_trivially_composable`:** Candidate B is the SHAPE_MATCH_with_named_adapter route where the "adapter" is itself a chain-grade primitive (sequence-binding S matrix) operating in its native input shape. This is the strongest possible signal-shape outcome for a novel-composition drill.

---

## "Would this fail too?" honest pre-mortem

**Most likely failure mode (P≈0.40):** Edge 2 bind `cluster_k_codes[k_pred] * hop_code[i]` produces 300 distinct keys, but the per-cluster predicted argmax k_pred at hop i may NOT match the cluster used at training-time for that hop. I.e., schema-Bayes' per-hop schema query (using past hops only) gives a different k_pred at hop i than the chain's true (training-time) schema cluster. The S matrix was written keyed by training-time cluster; inference reads keyed by per-hop cluster. **MISMATCH between training-key and inference-key collapses readout to noise.**
- If this happens: D arm hits 0.20-0.30, HARD_FAIL band, capability box closes.
- Diagnostic for cell-author: compute k_pred_per_hop vs k_train mismatch rate; if > 50%, the trajectory readout is reading the wrong row of S.

**Second failure mode (P≈0.25):** sequence-binding K=300 at N=8192 is feasible per K-cliff atlas, but the SUPERPOSITION pattern is 60-fold per partition value. Cross-talk between partition values during readout may cap accuracy near 0.30 (one-step-above-chance).
- If this happens: D arm hits 0.30-0.45, MIDDLE_BAND. Capability box stays open for v2 (resonator-cleaned readout or Modern-Hopfield).

**Third failure mode (P≈0.10):** training-time chain-to-schema clusters are too coarse (N_SCHEMAS=20 for 200 chains = 10 chains/cluster); per-(k, hop) trajectory is averaged over chains that go through the SAME k but DIFFERENT hop-i partitions. Trajectory readout returns an averaged-across-different-targets vector that cleans up to no specific partition.
- If this happens: D arm hits 0.30-0.40, MIDDLE_BAND; lift to v2 by increasing N_SCHEMAS (cost: smaller training pool per cluster).

**Genuinely working (P≈0.25):** trajectory-schema readout cleanly recovers per-hop partition. D arm hits 0.55-0.75, HARD_PASS. 4-primitive brain-faithful chain composition closes the multi-hop barrier 1 at depth 15. **This is the M3 breakthrough case.**

**Aggregate P_deflated = P(working) - margin = 0.25 + 0.07 hedge for "might just barely HARD_PASS at 0.50-0.55 borderline" = 0.32**

**If 2x-drill HARD_FAILs (Drill B per its HARD_FAIL gates):** per META_RULE_AO and `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`, **CAPABILITY_CLOSURE_CONFIRMED** on brain-faithful 4-primitive multi-hop chain composition. Two structurally-different mechanism classes (state-bias adapter in Drill A; trajectory-schema redesign in Drill B) both failing satisfies the 2x discipline. M3 pivots to non-brain-faithful composition (acknowledged trade-off) OR pivots to per-state schema selector as a 5th primitive class (Drill C if user authorizes).

---

## Cross-thread synthesis (Drill A + Drill B + adjacent work)

- **Drill A (PFC-WM state-tracker; HARD_FAILED smoke 2026-06-28):** confirmed `cluster_to_target_part[k]` hop-0-lock is the structural bottleneck. Three adapter sub-mechanisms (prior modulation, fake evidence, state-conditioned schema query) all route through the same hop-0 map. MEASURED@SUB_A=SUB_B=SUB_C=0.0000.
- **Drill B (this drill; trajectory-schema):** redesigns the primitive output map from `cluster → hop-0-partition` to `(cluster, hop_idx) → hop_idx-partition` via the substrate's chain-grade sequence-binding S matrix. Reuses Drill A's PATH3 4-primitive composition harness (WM bank, partition_routing, restricted cleanup) but replaces the FR4 primitive.
- **Drill A's pre-mortem failure mode #1 (P≈0.45)** predicted Drill A's exact failure pattern ("schema-Bayes is too coarse for per-hop discrimination at depth 15; state-conditioning can't pull it back"). MEASURED@2026-06-28 confirmed it. Drill B's mechanism (per-hop partition output via trajectory S matrix) is the direct mechanism-class response.
- **Adjacent: HRR context-bind disambiguator Q2 coreference drill (filed 2026-06-28 13:35):** also uses sequence-binding K=20 as a recency log; SHAPE_MATCH chain-grade. Drill B uses the same primitive in a different role (trajectory-template store vs recency log). Reusing the same primitive in two different drill-active roles is a useful primitive-reuse signal.
- **Adjacent: hierarchical planning Drills A+B (Bacon-Roy option-critic + Hersche block-sparse; filed 2026-06-28 11:29/11:33):** these are at a different level (option-critic learning vs primitive-output redesign). They do not interact directly with Drill B but they share the META_RULE_AO 2x-drill discipline pattern.

---

## Substrate-product implications

- **HARD_PASS @ Drill B:** the trajectory-schema primitive becomes a NEW chain-grade-eligible composition pattern (substrate-novel recasting of vmPFC schema firing for per-hop output). M3 multi-hop barrier-1 closes at depth 15 with brain-faithful composition. Substrate product gains "per-hop reasoning at depth 15 with substrate-native dlPFC + vmPFC + cortex + hippo composition" as a chain-grade capability. This is the largest single capability addition in 2026-06 to date.
- **MIDDLE_BAND @ Drill B:** trajectory-schema is architecturally correct but capacity-limited. Substrate-product gains a "MEASURED_MECHANISM-tier" 4-primitive composition pending capacity uplift (Modern-Hopfield or resonator v2). User can decide whether to dispatch v2 immediately (1-2 cycle effort) or defer for other priorities.
- **HARD_FAIL @ Drill B:** **capability closure on brain-faithful 4-primitive multi-hop chain composition.** Substrate-product story shifts: M3 multi-hop barrier-1 requires either (a) acknowledged non-brain-faithful composition (we admit the substrate composes differently than the brain at depth 15) OR (b) a 5th primitive class. Honest negative result; closes a major design direction; frees research bandwidth for other M3 angles (long narrative, hierarchical planning, etc.).
- **In ALL three outcomes:** the 2x-drill discipline is satisfied. This is exactly the user's intent per `feedback_2x_drill_negatives_before_capability_closure_USER_2026-06-28`.

---

## Citations (verified count: 6 distinct sources, 1 new, 5 re-cited)

1. **Mante & Sussillo 2013** — "Context-dependent computation by recurrent dynamics in PFC." Nature 503:78-84. [RE-CITED 2026-06-23, 2026-06-28 Drill A, 2026-06-28 Drill B — here for per-step (not chain-onset) reading]
2. **Miller & Cohen 2001** — "An integrative theory of prefrontal cortex function." Annu Rev Neurosci 24:167-202. [RE-CITED 2026-06-28 Drill A, here for per-step re-firing reading]
3. **Frady & Sommer 2020** — "Functional modeling of working memory with HD/VSA." Nat Mach Intell. [RE-CITED 2026-06-27, 2026-06-28 Drill A, here for hop_idx-as-slot-key]
4. **Plate 2003** — Holographic Reduced Representations, ch. 6 contextually-modulated cleanup. [RE-CITED 2026-06-22 B36, 2026-06-28 Drill A, here for Edge-2 contextual readout]
5. **Hersche, Rahimi, et al. 2023** — "Factorizers" (resonator decomposition). Nat Mach Intell. [CITED@2026-06-22 hierarchical-planning Hersche drill, FIRST CITED HERE for trajectory-readout cleanup fallback]
6. **Hopfield & Krotov 2020** — "Dense associative memory generalizations" (Modern-Hopfield exponential capacity). [CITED@multiple prior; RESERVED for v2 fallback if Candidate B middle-bands]

**Internal substrate references (ABSOLUTE PATHS; META_RULE_AE):**
- Drill A note: `d:/AI/hd-instrument/notes/research_drill_pfc_wm_state_tracker_4_primitive_composition_2026-06-28.md`
- Drill A verdict (HARD_FAIL): `d:/AI/hd-instrument/notes/exp_dev_verdict_pfc_wm_state_tracker_smoke_HARD_FAIL_all_3_adapters_2026-06-28.md`
- Drill A smoke metrics (MEASURED@2026-06-28 all-adapter-zero): `d:/AI/hd-instrument/data/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7_smoke/metrics.json`
- Drill A cell with hop-0-locked map bug: `d:/AI/hd-instrument/experiments/exp_substrate_partition_oracle_pfc_wm_state_tracker_v1_seed_7.py` (lines 322-330)
- Sequence-binding chain-grade primitive (FR3+FR4 underlying): `d:/AI/hd-instrument/hdlab/sequence_memory.py`
- Sequence-binding K-cliff atlas (capacity-feasibility): `d:/AI/hd-instrument/data/exp_substrate_sequence_binding_K_cliff_phase_diagram_v1_seed_*_v1/metrics.json`
- v5_hardened baseline (BASELINE_A=0.39, ORACLE_B=0.84-0.90): `d:/AI/hd-instrument/data/exp_substrate_multihop_partition_oracle_v5_hardened_FULL_seed_11_v1/metrics.json`
- WM multi-bank K cliff (FR1+FR2 chain-grade): `d:/AI/hd-instrument/data/exp_substrate_wm_multibank_K_cliff_phase_diagram_v1_seed_7_v1/metrics.json`

---

## Verdict

**P_deflated = 0.32** (gross P=0.55, deflated by 0.23 for novel composition of sequence-binding S into vmPFC/cortex primitive interface; for chained outer-product trajectory writes at near-K-cap; and for the new (cluster × hop) bind operation needing inference-time k_pred to match training-time k_train).

**Composition-discipline gate verdict:** **SHAPE_MATCH_with_native_primitive** (sequence-binding S matrix in native shape; no SHAPE_MISMATCH edges; no new primitive class; one new FHRR-bind operation that is structurally identical to existing chain-grade binds).

**Per AP_v2 chain-grade rule:** the drill SATISFIES "chain-grade primitives composed at native shape with no SHAPE_MISMATCH adapter" — candidate is **eligible for cell-author spawn** without prior adapter-design drill.

**Most likely failure mode** (P≈0.40): inference-time k_pred mismatch with training-time k_train collapses trajectory readout. Diagnostic for cell-author to compute & report: k_pred_per_hop_vs_k_train_mismatch_rate.

**Per 2x-drill discipline:** if Drill B HARD_FAILs per the HARD_FAIL gates above, **CAPABILITY_CLOSURE_CONFIRMED** on brain-faithful 4-primitive multi-hop chain composition. The capability box closes definitively; M3 pivots.

**Final line:**

`RECOMMENDATION: SPAWN_CELL_AUTHOR`

---

## Status

Status-log entry filed: `research_delivery` with `plain_language` + `importance=HIGH` (this is the gateway drill for the brain-faithful 4-primitive chain composition; either the cell HARD_PASSes and the M3 multi-hop barrier-1 closes, or it HARD_FAILs and the capability box closes definitively per 2x-drill discipline).

Companion exp_dev handoff filed: `d:/AI/hd-instrument/notes/exp_dev_handoff_research_drill_per_hop_schema_bayes_redesign_drill_B_2026-06-28.md`
