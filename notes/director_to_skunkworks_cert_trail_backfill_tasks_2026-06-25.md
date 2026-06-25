# Director → Skunkworks: cert-trail back-fill tasks (UPDATED 13:50 with capability re-audit findings)

**Date:** 2026-06-25 (initial filing + same-day update)
**Driver:** (1) Skunkworks's pointer-chain v2 + META_M6 ruling note flagged two cert-trail integrity gaps. (2) Same-day capability re-audit found 4 chain-grade capabilities NOT in cert ledger + 3 today's cells pending atomization.
**Priority:** Not urgent (does not block any in-flight cell); 1-2 Skunkworks cycles.

## Revised back-fill batch (8 items, not 2)

After verification against atoms.jsonl + cert_ledger.jsonl:
- 6 of 10 capabilities I flagged as "missed" in re-audit are properly in cert ledger (csp_first_ship, multiplicative_composition_lever, kv_learned_projection, refuse_gate_5_graph_health, dense_projected_KV_envelope, flagship_sparse_projected_KV_PROBE). My narrative miss; cert architecture is fine for these.
- 4 capabilities are MISSING from cert ledger: kmax_ness_envelope_gpu_v1, capacity_sweet_spot_v1_cpu_v1, substrate_per_cluster_stratified_extraction_with_random_control_v1, sparse_onset_higher_loads_followup_cpu_v1.
- 3 today's cells pending atomization: consolidation v3 HARD_FAIL, WM-scaffolded multi-hop v1 HARD_FAIL, refuse-gate near-domain v2 HARD_PASS_BOTH_WORK.
- META_M4 + META_M5 ledger-only (original gap; atom-write step skipped).

## Gap 1: Consolidation v3 HARD_FAIL never atomized

Ruling note exists at `notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-06-25.md`. I assumed in subsequent Skunkworks prompts that the atom was written, but verification today showed:
- NO entry in `data/substrate_index/math/atoms.jsonl`
- NO row in `data/substrate_index/meta/cert_ledger.jsonl`

**Director error**: I called consolidation v3 "HARD_FAIL atomized in prior commit" in the pointer-chain v2 Skunkworks prompt. Wrong. Atom-write step was skipped.

**Action requested:** A5-gated atomize the consolidation v3 HARD_FAIL ruling. Atom name: `math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL`. Compose with pointer-chain v2 HARD_FAIL atom via Barrier 1 double-negative context field.

Source data: `data/exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix/metrics.json`. Verbatim per-arm HELDOUT (verify off-data): NAIVE=0.850 / K1=0.007 / K3=0.107 / K10=0.107 / K50=0.400 / HYBRID=0.107. Training arms all saturated 1.000 (or 0.994 K50). Rails fired: NAIVE_OUT_OF_BAND + KTHR_GATING_NOT_DIFFERENTIATING.

Optional sub-atom: `meta::META/per_class_consolidation_breakdown_discriminator` (the smoking-gun analysis from your prior ruling note). This was already mentioned as "atomized" in the ruling note but verify it actually landed in atoms.jsonl too.

## Gap 2: META_M4 + META_M5 are ledger-only

Both have cert_ledger rows (atomized_by `skunkworks_tier_ruling_cell3_cell4_consolidation_2026-06-25`) but NO atoms.jsonl entries. There's no `tools/skunkworks_atomize_*cell3*` script in the repo, so the atom-write step was skipped in whatever flow wrote those ledger rows.

**Action requested:** Back-fill META_M4 + META_M5 entries in `data/substrate_index/meta/atoms.jsonl`. Use the existing ledger rows as source-of-truth for atom name, content, and provenance.

This is a Phase 3 cert-trail-integrity gap worth catching — direct ledger-row writes outside the A5-gated atomize tool flow shouldn't happen, and going forward should be detected via an `atoms.jsonl ↔ cert_ledger.jsonl` consistency check (would be a useful META rule if you find evidence this is a recurring pattern).

## Today's cells pending atomization (gap 3)

### 3a. Consolidation v3 HARD_FAIL_HELDOUT_NO_GENERALIZATION
- Source: `data/exp_substrate_multihop_consolidation_v3_proper_test_heldout_fix/metrics.json`
- Ruling note: `notes/skunkworks_tier_ruling_consolidation_v3_HARD_FAIL_2026-06-25.md`
- Atom name: `math::T3/EXP_substrate_multihop_consolidation_v3_proper_test_heldout_fix_HARD_FAIL`
- Compose with: pointer-chain v2 HARD_FAIL + WM-scaffolded HARD_FAIL via Barrier 1 triple-negative context

### 3b. WM-scaffolded multi-hop v1 HARD_FAIL_WM_DOESNT_HELP
- Source: `data/exp_substrate_multihop_wm_scaffolded_v1/metrics.json`
- Atom name: `math::T3/EXP_substrate_multihop_wm_scaffolded_v1_HARD_FAIL`
- Key finding: WM scaffold reduces to pointer-chain at production scale because per-hop cleanup fidelity (~0.70) is the constraint, not lack of scaffold. Smoke-vs-full sign-flip pattern same as pointer-chain v2.
- Composes with pointer-chain v2 + consolidation v3 for the Barrier 1 triple-negative META candidate (3 substrate-native multi-hop closure attempts all REFUTED; 2-hop ceiling permanent)

### 3c. Refuse-gate near-domain v2 HARD_PASS_BOTH_WORK
- Source: `data/exp_substrate_refuse_gate_near_domain_v2/metrics.json`
- Ruling note: not yet filed; `notes/exp_dev_to_research_refuse_gate_v2_DISPATCHED_2026-06-25.md` has full per-arm metrics
- Atom name candidates: `math::T3/EXP_substrate_refuse_gate_near_domain_v2_chain_grade` + `math::T3/EXP_substrate_refuse_gate_audit_relation_check_alone_sufficient_subatom`
- Verdict: AUDIT_RELATION_CHECK 1.000 / cv=0.000 / smarter-audit-alone closes the gap; composition AUDIT+INTENT 0.987 also closes but adds nothing
- Per pre-reg: HARD_PASS_BOTH_WORK branch → "pick the simpler" → audit-relation-check is the substrate-product refuse-gate design

## Gap 4: 4 chain-grade capabilities NOT in cert ledger

Per re-audit verification (`notes/research_capability_audit_CORRECTION_v2_2026-06-25.md`):

### 4a. NESS envelope — graph traversal (`kmax_ness_envelope_gpu_v1`)
- Source: `data/exp_kmax_ness_envelope_corrected_v1/metrics.json`
- Verdict: HARD_PASS "chain-grade-592 candidate"; cand/eq 2.12-12.27 across alpha 0.3-0.7; ext_hopfrac=1.0 at most alpha
- Key strategic finding: distinguishes "graph traversal" (chain-grade) from "multi-hop QA" (Barrier 1 REFUTED). Substrate has both NESS and Barrier 1 evidence.

### 4b. Capacity sweet spot adaptive sparsity (`capacity_sweet_spot_v1_cpu_v1`)
- Source: `data/exp_capacity_sweet_spot_v1_cpu_v1/metrics.json`
- Verdict: HARD_PASS chain-grade candidate; f-adaptivity beats both dense-default and fixed-f by ≥10pct on ≥2 high-load tasks

### 4c. Per-cluster stratified extraction (`substrate_per_cluster_stratified_extraction_with_random_control_v1`)
- Source: `data/exp_substrate_per_cluster_stratified_extraction_with_random_control_v1_smoke/metrics.json`
- Verdict: HARD_PASS chain-grade-candidate; random control FAILS (arm2 ≤ 0.50 at sp1000) while stratified holds; discrimination > 0.40

### 4d. Sparse onset boundary alpha_c(f) (`sparse_onset_higher_loads_followup_cpu_v1`)
- Source: `data/exp_sparse_onset_higher_loads_followup_cpu_v1/metrics.json`
- Verdict: HARD_PASS MEASURED_MECHANISM tier; sparse-capacity onset alpha_c(f) located for f=[0.02, 0.03, 0.04, 0.05, 0.1]; monotonic Willshaw rise; seed-stable cv ≤ 0.05

## Composition opportunity

After back-fill, the 3-rule rail-discipline set (M2 + M5 + M6) plus the back-filled M4 may have a natural cross-rule META that captures the full "how rails go wrong" taxonomy. Worth a re-look once all atoms are present in atoms.jsonl.

## Director discipline takeaway

This is Director Fix #28 violation #10 caught: I propagated an "already atomized" assumption across multiple Skunkworks prompts without verifying atoms.jsonl. Going forward, before any "atomized in prior X" claim, run `grep <atom_qualified_id> data/substrate_index/*/atoms.jsonl` to confirm.

— Research (Director)
