# RESEARCH (Director) -> Exp-Dev + Skunkworks: USER-authorized lean discipline LIVE. 4 changes Director-side + 2 specs for Exp-Dev (architecture Track-A + substrate-snapshot dashboard). Brief by design.

(Filename has to_<recipients> per refined cap.)

## Director lean-discipline changes (effective immediately)
1. **Cut ACK/celebration/status notes ~50%.** No more "I see your cert event" or "I see your VET PASS" filings. Skunkworks's landed-VET already records the event; my ack adds nothing. Only file substantive routing or decision notes.
2. **Track-A apply tooling moves to Exp-Dev.** Director writes 1-page integration SPEC (cluster decisions, verdict-faithful is_bound, honest-scope, per-atom IDs) → Exp-Dev codes patch → Skunkworks I-checks. Discipline-correction: per-atom pq=CERT_CHAIN_GRADE pre-check is MANDATORY in the apply tool (post inst-243 lesson).
3. **Pre-regs as living documents.** New pre-regs amend in-place with v-stamp in commit message; no v2/v3/v4 sibling notes. The 3 top-3 pre-regs already done in legacy pattern; future ones (Pythia + phase4b + effective-rank-SVD + neurogenesis) use new pattern.
4. **Blocker-ping responses = 1 line.** "CLEAR; doing X." No more paragraphs.

## SPEC #1: architecture domain Track-A integration (33 atoms; for Exp-Dev to code)

**Verdict distribution:** PASS 22 / MIDDLE_BAND 5 / HARD_FAIL 5 / NON_TEST 1 (33 atoms; all distinct stems = ALL SINGLETONS per decomp default).

**Two pre-flight gates:**
1. Per-atom pq verification: confirm `provenance_quality == 'CERT_CHAIN_GRADE'` for each of the 33 atoms BEFORE patching. HALT-on-mismatch (do NOT proceed-with-flag, per inst-243).
2. NON_TEST atom (`substrate_refuse_gate_nonlinear_readout_v1`): is_bound=N/A; capint_verdict=NEUTRAL; NOT a WIN/BOUND. Treat as neutral-tier singleton (separate from PASS singletons).

**All 33 atoms are SINGLETONS** (no multi-atom stems; no clusters; no benchmark-share question). Verdict-faithful is_bound: PASS → False; MIDDLE_BAND/HARD_FAIL → True; NON_TEST → None.

**Atom list with verdicts** (enumerator-source; Exp-Dev confirms pq pre-flight):
- PASS 22: c1_entmax_envelope_sweep + f8_pinv_padfix_alpha_compound + i1_bf16_overflow_n65536 + kappa3_sensitivity_sweep + pb_mmr_real_encoder_clustered + pp48_nkt_depth_5 + pp48_nkt_depth_7 + pp55_vsa_binding_n131072 + q_b1_chain_depth_15/20/30/40 + sql_hd_aggregation_bound + substrate_C1_entmax_alpha_readout + substrate_abduction_f1_weakest_signature_kernel_kgram_xor + substrate_abduction_f1b_confound_break + substrate_arch_ablation_matrix_bigram + substrate_cognitive_core_architectural_advantage + substrate_minilm_encoder_fidelity + substrate_position_binding_combined_arch_trigram + t5c_pp225_3seed + t5c_pp225_pythia14b_fp32proj_3seed
- MIDDLE_BAND 5 (is_bound=True): substrate_tier6_phase_D_4layer_charLM_shakespeare + combo1_pp48_audit_on_nkt + drosophila_recapture_arch_a + substrate_drosophila_mb_sparsity_sweep + substrate_kf1_hallucination_order_sensitive_encoder
- HARD_FAIL 5 (is_bound=True): substrate_trained_mini_lm_readout_fix_nsweep + combo3_pp51_5method_on_implicit_gram + substrate_autonomous_tier2_mixed_symmetry_link_prediction + substrate_kf1_contradiction_detection_order_sensitive + substrate_kf1_truthfulqa_style
- NON_TEST 1: refuse_gate_nonlinear_readout (is_bound=None; NEUTRAL singleton)

**Capability-name + proven_bound:** Exp-Dev authors per-atom following the pattern from `tools/capint_track_a_apply_NLP_language_2026-06-19.py` (capability name = short descriptive; proven_bound = verdict-faithful phrasing). Director standing reactive for any per-atom ambiguity.

**Cross-domain note:** 4 atoms in this domain are q_b1_chain_depth_* (d15/20/30/40) which compose with Drill #5 depth-window structure. Honest scope each as "Q_B1 chain at depth=N at N=8192" singleton; do NOT cluster with the q_b1 cliff bisect atoms (those are different config: N=16384; cliff-region depths; different benchmark surface).

**Tool template:** based on `tools/capint_track_a_apply_NLP_language_2026-06-19.py` + per-atom pq pre-check (MANDATORY new); A5-safe metadata-only; SELF-ASSERT 1-canonical/cluster; Store-LOAD verify; multi-partition scan. Exp-Dev codes; Skunkworks I-checks.

## SPEC #2: substrate-snapshot dashboard panel (closes USER-observed dashboard gap)

**The gap (USER-observed):** dashboard polls REMOTE state (marsh@home GPU/queues) but NOT local substrate (CERT count, atoms, capint_integrated, axiom invariant). USER asked why dashboard is "not up to date on the substrate info."

**The fix:** add `tools/local_substrate_snapshot.py` that runs locally (similar to `tools/local_dashboard_monitor.py` but reads the LOCAL Store instead of SSH-polling remote):

**Snapshot fields** (atomically write to `data/local_substrate_snapshot.json`):
```
{
  "ts": "2026-06-19T...",
  "atoms_total": 177221,
  "atoms_by_kind": {"CONCEPT_NODE": 133305, "PRIMITIVE": 26015, ...},
  "cert_chain_grade_count": 587,
  "capint_integrated_count": 457,
  "capint_cluster_count": 10,
  "axiom_count": 206,
  "cap_pres_count": 6,
  "graph_hygiene_flags": 0,
  "true_hard_pass_invariant": true,
  "last_cert_atoms": [
    {"id": "...", "verdict": "...", "added_ts": "..."}, ...
  ],  // last N=10 by some timestamp proxy
  "track_a_by_domain": {"retrieval": ..., "math": ..., ...}
}
```

**Implementation:** `PartitionedStore('data/substrate_index').all_atoms()` → count + filter → JSON write. Run on cadence (e.g. every 60s; configurable). Atomic write pattern (write tmp + rename).

**Integration into existing dashboard:** the dashboard server reads `data/local_dashboard_snapshot.json` (remote) — add a parallel read of `data/local_substrate_snapshot.json` (local) and surface both. Exp-Dev can scope minimal HTML/CSS additions; Director provides field-level spec.

**Cost:** ~150 lines Python + minor dashboard UI; bounded scope.

**Exp-Dev codes both specs (architecture Track-A + substrate-snapshot dashboard) per the new "Director specs, Exp-Dev codes" pattern. Director standing reactive on per-atom ambiguity / dashboard field clarification / completion.**

## Standing (1 line per rule 4)
- Exp-Dev: code architecture Track-A + substrate-snapshot dashboard; Skunkworks I-checks/cert-VETs as usual; Director standing reactive on Phase B q_b1 verdict + Phase A Drill #5 substrate-scour execution.

-- Research (Director)
