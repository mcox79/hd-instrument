# BACKUP corrections-pending — verified categorization 2026-06-28

**Status:** Awaiting USER call on whether to apply now, in-bundle after VETs, or hold.
**Context:** Comprehensive substrate-state audit (Skunkworks aba2c5) flagged ~14 BACKUP characteristics changes. Director did per-capability verification across cert_ledger.jsonl + atoms.jsonl + commits + notes. Audit was **wrong on several high-stakes items** — your caution was correct.

---

## CONFIRMED DEMOTE (3 entries; safe to apply)

These have only MM evidence across full broad-pattern ledger search. Audit was right.

| BACKUP row | Current | Verified | Recommended edit |
|---|---|---|---|
| TOM Sally-Anne 2nd-order (Stage 3) | CG ✓ PARTIAL | 1 MM smoke (theory_of_mind_sally_anne_nested_hrr_v1) | CG ✓ → MM PARTIAL |
| CF latency delta-stack (Cell 2) (Stage 3) | CG ✓ PARTIAL | 1 MM smoke; **Cell 1 vmPFC regret stays CG** (counterfactual_regret_comparison_vmpfc_v1 + 2 sibling CG) | CG ✓ → MM PARTIAL on Cell 2 only |
| Sequence binding for narrative Q3 (Stage 3) | CG ✓ PARTIAL | 1 MM single-seed (narrative_Q3_temporal_via_sequence_replay_K20_V_C_axis_invariance); **Stage 1 sequence binding K-cliff stays CG separately** | CG ✓ → MM PARTIAL on Stage 3 narrative-application only |

## CONFIRMED ADD (2 entries; safe to apply)

These have chain-grade ledger entries but no row in BACKUP characteristics table.

| Capability | Evidence | Where to add |
|---|---|---|
| compose_freq_routing_v5 DEFINITIVE | math::T3/EXP_substrate_compose_freq_routing_v5_DEFINITIVE (CG 2026-06-25 pre_reg_pass) | Stage 2 row: "compose_freq routing v5" CG ✓ MID |
| p1_v2_action_at_any_position | 2 CG entries (p1_action_at_any_position_phase_diagram_v1 + p1_v2_action_at_any_position_LLM_class_v1, 2026-06-22) | Stage 1 row: "Action-at-any-position lever" CG ✓ MID |

BIAS13 basis_layer_label_contamination_proof_v4 DEFINITIVE is already cited in BACKUP meta-rules; optional surface in characteristics table.

---

## KEEP CG ✓ — AUDIT WAS WRONG (4 entries; do not change)

Broader-pattern ledger search found chain-grade evidence the audit's narrow regex missed.

| BACKUP row | Audit recommendation | Verified evidence — KEEP |
|---|---|---|
| Cleanup attractor (Stage 1) | DEMOTE to MM/HN | 4 CG entries: modern_hopfield_n_sweep_v1, permutation_binding_multiocc_v2 (cleanup rescues FHRR), phase_diagram_multihop_depth_ceiling_30 (cleanup load-bearing), multihop_brain_pushback_v3 |
| Continual learning CRISPR (Stage 1) | DEMOTE | 1 CG: a8_continual_writes_no_catastrophic_forgetting_v1 |
| NREM replay (Stage 2) | DEMOTE | 1 CG (c3_compressed_sequence_replay_v1) + 1 PB (substrate_continual_NREM_replay_v1 proven_bound). **BACKUP's "at small-M; chain-grade-scale BLOCKED at M=8192" qualifier is exactly accurate.** Keep. |
| TWO_TIER generational W (Stage 2) | DEMOTE | 1 proven_bound (gap4_two_tier_generational_W_v1) — strong evidence; "CG ✓ HIGH" reasonable but framing could be "PROVEN_BOUND" if strict |

## HOLD — AUDIT ALSO WRONG (2 entries)

| Capability | Audit recommendation | Verified state — do not apply audit's suggestion |
|---|---|---|
| role_tagged_compositional | ADD as CG ✓ | Skunkworks 2026-06-25 already ruled MM (by-construction-saturation; encoder carries lift, NOT role-binding). See notes/skunkworks_tier_ruling_cell5_role_tagged_compgen_KG_2026-06-25.md. Do NOT add. |
| Higher_order_TOM_3rd CLOSED-neg | "0 atoms — DEMOTE/REVISE" | Closure evidence exists in commits + notes (c9484c52 TOM v2 reframed cell + 828749ba smoke HF FLAT_DEPTH note + 2026-06-28 exp_dev note). Substantively closed; needs atomization, not demotion. **Action: queue for Skunkworks atomization, keep BACKUP claim.** |

---

## DEFER — IN-FLIGHT VETS WILL RESOLVE (4 entries)

These rows have v2 revivals in flight or freshly-landed FULLs awaiting VET. Don't edit until VETs return.

| BACKUP row | Status | Pending |
|---|---|---|
| Lock_in_amp (Stage 2) | v1 atomized MM; v2 smoke PASS; FULL pending | a91161 hdi_exp_dev wrapping; Skunkworks VET next |
| ANCHOR 4 time-decay (Stage 2) | v1 smoke MM; today's FULL = 2/3 HP + 1 MB borderline | a5d374 Skunkworks covers (in audit follow-up batch) |
| TASK_VECTOR HRR ICL K-cliff (Stage 3) | v1 honest-downward to MM (metric artifact); v2 with monotonic-decay metric SMOKE + FULL smoke 3-seed HP | aa25e8 cell agent returned; FULL landings pending; Skunkworks VET next |
| Capacity multi-bank α-K (Stage 1) | v1 atomized MM; v2 SMOKE clean + full-N preview discriminator fires; 3 seeds on GPU | a1bfde returned; FULL landings ~10-15min/seed; Skunkworks VET next |

## CRITICAL — CLS HANDOFF POTENTIAL DISPROOF (in flight)

| BACKUP row | Status |
|---|---|
| CLS handoff at chain-grade M=8192 CLOSED-negative | Today's `exp_cortex_hippo_handoff_FULL_seed_23` HARD_PASS may DISPROVE this CLOSED-neg if at the same M=8192 regime. **Sub-audit in flight (a5d374 Skunkworks; explicit instruction to verify regime-match before any tier decision).** Possible outcomes: MAINTAIN / REOPEN / REVISE-to-regime-conditional. |

---

## CERT COUNT CORRECTION (safe to apply with bundle)

BACKUP line 35 says "492 chain-grade certifications" — actual is **494** (sum of cert_increment_delta>0 from cert_ledger.jsonl).
- Earlier Skunkworks reported cert_n=630 — that figure cannot be reconciled with the ledger (no field exists; audit confirmed authoritative count is 494)

---

## NEXT-WAVE SKUNKWORKS BATCHES (from audit; queue when a5d374 returns)

To avoid concurrent atom-writes, queue serially after a5d374 returns:

1. **MEDIUM-priority backlog** — Lock_in_amp v1 MM ledger entry, Capacity_multibank v1 MM ledger entry (these are already-atomized but worth verifying ledger), wm_multibank v3 HP ledger entry, multihop v4 HP ledger entry, partition_oracle hardened MBs
2. **BATCH 2026-06-27 HF cells** — ~10 atoms for swr_preplay, self_explanation, importance_ceiling, edge_importance v6, etc.
3. **BATCH 2026-06-25** — 128 cells; topic-batched atomization; includes substrate_basis_layer_label_contamination_proof_v3 / role_tagged_compositional (already ruled MM) / compose_freq_routing v4 → v5 chain / stage1_definitive_validation / stage1_SEMANTIC_concept_learner / stage3_integrated_audit_device
4. **LEGACY wave14 backfill (2026-05-24)** — 23 cells; check parent wave14 atom first
5. **Higher_order_TOM_3rd closure atomization** — atomize today's v2 reframed smoke HF + earlier flat-depth evidence as the closure-pair
6. **role_tagged_compositional ledger entry** — write the 2026-06-25 MM ruling to cert_ledger.jsonl from the existing note

---

## WHAT TO TELL USER

- **Audit was right on:** TOM Sally-Anne, CF latency Cell 2, Sequence binding narrative Q3 (3 demotes). Compose_freq_routing_v5 + p1_v2 missing (2 adds).
- **Audit was wrong on:** Cleanup_attractor, Continual_CRISPR, NREM, TWO_TIER (4 KEEPs); role_tagged ADD (it's MM); Higher_order_TOM_3rd DEMOTE (closure stands).
- **In flight:** 4 v2 revivals + Skunkworks high-priority VET; bundle edit best made after they return.
- **Cert count:** 492 → 494 (off by 2; the +2 from BACKUP-cited promotions did make it into ledger).
