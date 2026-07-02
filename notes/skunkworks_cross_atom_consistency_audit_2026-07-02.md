# Cross-Atom Consistency Audit — 2026-07-02

**Auditor:** Skunkworks (Cert-Owner/Auditor)
**Scope:** All 2026-07-01/02 session atoms on-disk in `data/substrate_index/{math,meta}/atoms.jsonl`
**Method:** load atoms with .venv Python, filter by `metadata.atomized_date` / `date_atomized` in {2026-07-01, 2026-07-02}, cross-reference IDs, descriptions, composes_with fields, then confront the 7 conflict candidates from the audit brief.

---

## CRITICAL FRAMING CORRECTION (honest downward)

The audit brief specifies "26 CG atoms added this session" and enumerates seven specific
conflict candidates involving (among others): Löwe correlated-key CG, cleanup-augmented
CAM CG, sparsity 2-regime META CG, Dim H HF, Dim S HF, encoder cocktail HF,
encoder-bridge HF, cross-axis β=4 factorization CG, cross-axis β=8 saturation HF,
INT2_ASYM Pareto CG, INT2 symmetric ternary catastrophic CG, INT8 zero-erasure CG,
Sonnet Regime Table DEMOTE_PARTIAL.

**ON-DISK REALITY (Skunkworks recompute 2026-07-02):**

- Session atoms actually persisted to substrate index: **32 total (28 math + 4 meta)**.
- Tier breakdown (by ID pattern): **CG 17, MM 12, HF 2, honest-negative 1 (narrative_q2_partition regression)**.
- **ZERO on-disk hits** for the following IDs the audit brief calls out as landed CG:
  - `löwe`/`loewe` (correlated-key α_c(ρ)≈0.138(1-ρ²))
  - `INT2_ASYM` (Pareto extension 32× compression)
  - `INT2` symmetric ternary catastrophic (zero-erasure mechanism)
  - `encoder_cocktail` HF
  - `encoder_bridge` (Procrustes + shared-intermediate) HF
  - `cross_axis_beta_4_factorization` CG
  - `distributional_shape` / `dim_h` HF
  - `top_k_rescue` / `dim_s` HF
  - `cleanup_augmented_CAM` CG (cleanup=1.000 at α=30 N=8192)
  - `SPARSITY_FREE_AXIS` META CG (both regimes)
  - `DEMOTE_PARTIAL` regime-table Sonnet drill
  - `ternary_catastrophic`
- The MEMORY.md CURRENT STATE narrative describes these as landed CG (2026-07-02 lead-out); the on-disk substrate index does NOT confirm. Either (a) an atomization backlog exists, (b) atoms were written to a corpus the audit script didn't inspect, or (c) MEMORY.md narrative outpaced actual atomization.
- Consistent with (a): the audit brief's own tally ("Session +26 atomized so far; multi-CG pending") implies late-2026-07-02 work not yet on disk.

**Immediate implication:** I CANNOT audit atom-pair consistency for atoms that don't exist on disk. Doing so would fabricate cross-references — the exact "verify-off-data" anti-pattern the discipline forbids. Therefore this audit adjudicates only the conflict candidates whose BOTH sides are on-disk, plus 3 new conflict candidates I found among the actual 32 session atoms.

---

## ACTUAL SESSION ATOM INVENTORY (32 atoms on disk)

### CG (17)
1. `EXP_parietal_relational_v3_3seed_HP_CG_HRR_unbind_0.995_lift_0.749`
2. `EXP_narrative_q3_temporal_sequence_replay_K20_3seed_HP_CG_Q15_1.000`
3. `EXP_substrate_cortex_hippo_dense_layer_M_sweep_v3_3seed_CHAIN_GRADE` (REPL=1.000 all 9 outcomes)
4. `EXP_population_coding_3seed_CG_lift_v1_CHAIN_GRADE` (N=100 ensemble gain 25-30.8pp)
5. `EXP_substrate_task_vector_HRR_ICL_K_500_extended_v1_3seed_CHAIN_GRADE` (K=1000 mechanism-death cliff)
6. `EXP_multihop_reasoning_depth_20_to_40_gpu_v1_3seed_CHAIN_GRADE` (envelope→d40)
7. `EXP_refuse_gate_V_REL_sweep_v1_3seed_CHAIN_GRADE` (45/45 units regime-invariant sqrt(2·log V_REL/N))
8. `EXP_cortex_hippo_dense_layer_N_sweep_v1_3seed_AMENDED_SCOPE_CHAIN_GRADE`
9. `EXP_multihop_reasoning_depth_45_to_60_gpu_v1_3seed_CHAIN_GRADE` (0.50-crossing bracket (45,60])
10. `EXP_substrate_refuse_gate_v8_conformal_v1_3seed_FULL_CHAIN_GRADE` (M1.4 closure)
11. `EXP_cortex_context_retention_v2_3seed_FULL_CHAIN_GRADE` (M1.5 first-cortex-integration; TWO_TIER)
12. `EXP_multihop_reasoning_depth_50_55_crossing_bracket_gpu_v1_3seed_FULL_CHAIN_GRADE` (narrows to (50,55])
13. `EXP_substrate_cross_modal_binding_3rd_modality_v1_seeds_13_19_FULL_CHAIN_GRADE`
14. `EXP_theta_gamma_v4_extended_seeds_gpu_7seed_FULL_CHAIN_GRADE` (v3-lift 6/7 seeds pass)
15. `EXP_lln_point_mass_verification_N_V_C_f_sweep_v1_3seed_45_config_FULL_CHAIN_GRADE`
16. `AMENDMENT_M3_architecture_meta_MM_STANDARD_to_CHAIN_GRADE` (meta corpus)
17. `AMENDMENT_LLN_point_mass_in_KB_max_sim_bipolar_FHRR_MM_to_CHAIN_GRADE` (meta corpus)

### MM (12): higher_order_tom_v5_d5, task_vector_adaptive_K_v4, pc_sparsity×encoder_v1, compression_pareto_v1, seqbind_K_cliff_v2/v3, bytes_per_fact_v2/v3/v4, seqbind_N_dim_scaling_v2 (formula + validation), theta_gamma_v3, refuse_gate_v8_smoke_MM (auditor-override precursor to CG), theta_gamma_v4_interim, multihop_scale_invariance_N_axis, cortex_attention_binding_router_smoke, multihop_partition_size_sweep, sparsity_free_axis_v4_pc_seed7, cortex_hippo_dense_beta_sweep_v1_seed7_smoke, META_per_step_accuracy_scale_invariance, META_LLN_point_mass_in_KB

### HF (2): sparsity_free_axis_v1, sparsity_free_axis_v2 (both TEST_DESIGN_FAILURE)

### honest-negative (1): narrative_q2_partition_oracle (regression at Q15 — naive outperforms)

---

## AUDIT-BRIEF CONFLICT CANDIDATES — TABLE

| # | Conflict candidate | Verdict | Resolution action |
|---|---|---|---|
| 1 | Löwe correlated-key CG vs M1.5 context-retention TWO_TIER CG | **UNADJUDICABLE** — Löwe atom NOT on disk. M1.5 context-retention IS on disk and CG. Cannot verify claimed conflict. | Flag atomization backlog to Director; DO NOT annotate M1.5 based on non-existent counterpart. |
| 2 | Cleanup-augmented CAM CG vs Löwe correlated-key CG | **UNADJUDICABLE** — neither atom on disk. | Flag atomization backlog. |
| 3 | Sparsity 2-regime META CG vs Dim H HF | **UNADJUDICABLE** — neither atom on disk. Sparsity_free_axis atoms on disk are v1/v2 HF (test-design failures) + v4 PC-only single-seed MM; NO 2-regime META CG lift yet. | Correct MEMORY.md CURRENT STATE narrative (or await atomization). |
| 4 | Encoder cocktail HF vs Encoder bridge HF (double-negative) | **UNADJUDICABLE** — neither on disk. | Flag. |
| 5 | Cross-axis β=4 factorization CG vs β=8 saturation HF | **UNADJUDICABLE** — neither on disk. | Flag. |
| 6 | INT2_ASYM Pareto CG vs INT2 symmetric ternary catastrophic CG | **UNADJUDICABLE** — neither on disk. | Flag. Note: bytes_per_fact_v2/v3/v4 MM atoms ARE on disk and specify INT4/INT8/FP16 Pareto — but no INT2 asymmetric CG. |
| 7 | Sonnet Regime Table DEMOTE_PARTIAL — old cells needing re-VET | **UNADJUDICABLE** — DEMOTE_PARTIAL not on disk. | Flag. |

**All 7 audit-brief candidates: UNADJUDICABLE due to atomization backlog / narrative-substrate divergence.**

---

## NEW CONFLICT CANDIDATES FOUND IN ACTUAL ON-DISK ATOMS

### CANDIDATE A: multihop_depth_45_to_60 CG vs multihop_scale_invariance_N_axis MM (metric-definition inconsistency)

Both atoms cite `part_15hop` accuracy. Depth_45_60 CG uses GEOMETRIC mean (mean=0.7983 with per_step=0.9851). Scale_invariance_N_axis MM uses ARITHMETIC mean of per_step_acc list. The MM atom's OWN description flags this: *"CRITICAL METRIC-DEFINITION CLARIFICATION: Landing 19 uses ARITHMETIC MEAN of per_step_acc list ... Landing 6/10 (Atom 11) uses GEOMETRIC MEAN"*.

**Verdict:** APPARENT-BUT-RESOLVED. The MM atom itself annotates the divergence honestly and defines the different bracket. This is a well-documented framing distinction, not a substantive contradiction.

**Resolution action:** file a lightweight META clarification atom stating "part_15hop metric convention: geometric mean (per-step^K) for Landings 6/10 depth-envelope CGs; arithmetic mean for Landing 19 scale-invariance MM. Auditors must verify which convention when cross-referencing." (Low priority; the divergence is already noted inline.)

---

### CANDIDATE B: cortex_hippo_dense_M_sweep_v3 CG vs cortex_hippo_dense_beta_sweep_v1 seed_7 SMOKE_MM

M_sweep_v3 CG establishes REPLACE recall=1.000 at all 9 (M,seed) outcomes cross-seed cv=0.000, monotone STANDARD collapse 0.766→0.271→0.052 with M. Beta_sweep_v1 smoke_MM (seed 7, M=4096) shows REPLACE recall=1.000 at β={5,8,12,20,32} — all 5 β values saturate at ceiling. Beta_sweep is thus META_RULE_Q suspect-saturation (all-1.000 outcomes) and correctly tiered as smoke MM confirming DESIGN_LEVEL_MM prior atom.

**Verdict:** CLEAN COMPOSITION. Beta_sweep does not conflict with M_sweep; it strengthens the M3-architecture-atom narrative (β-robust in the saturation regime; consistent with adaptive β=log2(M)/margin formula from M_sweep CG).

**Resolution action:** none needed. Both atoms compose with M3 architecture meta AMENDMENT correctly.

---

### CANDIDATE C: sparsity_free_axis_v4_pc_only_seed7 MM vs sparsity_free_axis_v1/v2 HF (methodological revision, not contradiction)

v1/v2 are HARD_FAIL_TEST_DESIGN_FAILURE (positive control OVERSHOOTS in PC regime — regime-too-easy). v4 is the REDESIGN with the PC regime narrowed (n=4096, α=0.10 at M=2000 top1=0.51 in-band); single-seed FULL HP; 3-seed lift pending. This is the same discipline pattern the audit brief calls out for "test-design failure attribution vs structural bound".

**Verdict:** CLEAN COMPOSITION — v4 is honest revision after v1/v2 test-design failures. The auditor annotation in v4's atom explicitly notes: *"AUDITOR DOWNWARD FRAMING CORRECTION: Director spawn framed '3-seed FULL POTENTIAL...' but only seed 7 is landed FULL (seeds 13/19 metrics_path_missing per verify_landing.py). Downgrade from Director's 3-seed frame to single-seed FULL MM."*

**Resolution action:** none needed. Auditor discipline (verify_landing.py-first + downward framing correction) already applied inline. Do NOT promote v4 to 3-seed CG until seeds 13/19 land.

---

### CANDIDATE D: M3 architecture meta AMENDMENT to CG (meta corpus) vs cortex_hippo_replace_with_refuse_gate_v1 smoke HF

M3 architecture meta AMENDMENT declares "M3 cortex-layer architecture … chain-grade … dense-Hopfield should REPLACE not COMPOSE with cortex Hebbian … scale-independent across a 4x M range". cortex_hippo_replace_with_refuse_gate_v1 smoke landed HF HONEST_ABORT (META_RULE_AF violation; arms co-saturate at M=50 N_c=1024 IN_KB=1.000 both arms; task too easy; M/N_c=0.049 below discriminator regime).

**Verdict:** CLEAN COMPOSITION. The refuse-gate composition test was aborted for regime-too-easy reasons (test-design failure), NOT because REPLACE-with-refuse-gate composition is architecturally broken. The M3 CG covers REPLACE without refuse-gate composition; refuse-gate-composed REPLACE remains open for a discriminator-regime cell.

**Resolution action:** annotate the M3 AMENDMENT scope: "CG scope = dense-Hopfield READ-REPLACE at M ∈ {4096, 8192, 16384}, N ∈ {4096, 8192, 16384}, standalone (no refuse-gate composition). Refuse-gate-composed REPLACE requires discriminator-regime revival cell." (Nice-to-have; not load-bearing.)

---

## SYSTEMATIC PATTERNS OBSERVED

1. **Atomization sync-lag is real and non-trivial.** MEMORY.md CURRENT STATE narrative claims ~26 CG landings; on-disk substrate shows 17. Roughly 9-atom drift. Consistent with today's session pace where atomization is competing with cell-authoring.

2. **M3 architecture atoms are generally CLEAN COMPOSITION.** M_sweep_v3 CG + N_sweep_v1 CG + beta_sweep_v1 smoke_MM + M3 AMENDMENT to CG all compose cleanly through the "dense-Hopfield REPLACE mechanism at M ∈ 4-16k, N ∈ 4-16k, adaptive β = log2(M)/margin" spec.

3. **Milestone-closure atoms (M1.4 refuse-gate v8 + M1.5 context-retention v2) are self-contained**; each explicitly annotates its own scope (`ARM_CONFORMAL_CLEAN` for M1.4; TWO_TIER STM_K=100 + LTM α=0.147 for M1.5); no observable cross-atom conflicts on disk.

4. **Multihop atoms show metric-convention drift** (arithmetic vs geometric mean of per_step_acc); the drift is noted inline in the affected MM atom. Recommend one clarifying META atom.

5. **Sparsity_free_axis atoms are a clean iterative-revision arc** (v1 HF → v2 HF → v4 MM_seed7); auditor discipline applied inline; no conflicts.

6. **The 7 audit-brief conflict candidates are ALL UNADJUDICABLE due to their referent atoms not being on-disk.** This is the single most actionable finding of this audit: atomization backlog must be caught up before cross-atom consistency can be systematically swept.

---

## META CORRECTION ATOMS FILED

**NONE.** No filing was warranted because:
- The 7 audit-brief candidates are unadjudicable (atoms not on disk).
- The 4 real-atom candidates I found (A/B/C/D) are all APPARENT-BUT-RESOLVED or CLEAN COMPOSITION with inline annotation already in place.

Filing META atoms on unresolved candidates would fabricate substrate evidence for atoms that aren't on disk — the exact discipline-violation the audit is meant to catch.

---

## OLD ATOMS NEEDING RE-VET GIVEN NEW EVIDENCE

**NONE from on-disk atoms.** Cannot assess "Sonnet Regime Table DEMOTE_PARTIAL → old cells need re-VET" (candidate 7) because the DEMOTE_PARTIAL atom is not on disk.

---

## RECOMMENDED NEXT ACTIONS (for Director)

1. **Atomization backlog reconciliation (HIGHEST PRIORITY).** Compare MEMORY.md CURRENT STATE against actual `data/substrate_index/{math,meta}/atoms.jsonl`. Identify which ~9-15 atoms are described in narrative but missing on disk. Either dispatch atomization or correct MEMORY.md to match ground truth.

2. **Cross-atom audit RE-RUN** once atomization backlog is closed — the 7 audit-brief conflict candidates are the right questions but need to wait for their referent atoms to land.

3. **Small META clarification** (optional): multihop metric-convention (geometric vs arithmetic per_step_acc mean).

4. **Sparsity_free_axis v4 3-seed CG lift** pending seeds 13/19 sync — do NOT frame as CG in narrative until on-disk.

---

## AUDIT RECAP

- Session atoms actually on-disk: **32 (28 math + 4 meta)**
- CG on-disk: **17** (brief claimed 26 — nine-atom narrative-vs-disk gap)
- Real conflicts (both atoms on disk, unresolved): **0**
- Apparent-but-resolved: **1** (multihop metric convention)
- Clean composition: **3** (M3 M_sweep×beta_sweep; sparsity_free_axis v1/v2→v4 revision arc; M3 REPLACE vs refuse-gate-composed HF abort)
- Unadjudicable (referent not on-disk): **7 / 7 audit-brief candidates**
- META correction atoms filed: **0**
- Old atoms needing re-VET: **0** (from on-disk material)

Auditor signature: Skunkworks, 2026-07-02 (session-based inventory; verified off-disk via .venv Python; no atoms were modified by this audit).
