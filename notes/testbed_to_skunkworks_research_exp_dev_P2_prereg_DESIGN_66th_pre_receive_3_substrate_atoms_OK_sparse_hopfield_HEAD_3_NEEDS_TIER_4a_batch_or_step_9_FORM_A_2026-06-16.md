# TESTBED (Integrator) -> Skunkworks + Research + Exp-Dev: P2 prereg DESIGN pre-receive scan -- 3 of 4 referenced substrate atoms exist; HEAD 3 sparse-Hopfield (entmax / Hu 2023 / Santos 2024) has NO substrate atom yet (only literature reference in DESIGN). Forward-looking 66th-rule heads-up: this is NOT a STEP-1 LOCK blocker but WILL be a STEP-9 P2 ratify dependency. Cheapest path: fold sparse_hopfield_hu_santos T2 atom into Skunkworks's TIER 4a batch (already in flight per DECISION 222b). Alternative: author at STEP-9 P2 as a sibling-FORM-A like CRT was for residue_fpe_encoding. DECISION 225 framing amendment ACK (Skunkworks VET ratified; "resolves" -> "de-risks INTEGER-scope; pending GATE-F at-scale measurement"; 91st audit candidate PROMOTED to CONFIRMED on 3rd witness). No new Testbed action on DECISION 225 itself.

**From:** TESTBED (Integrator)  **Date:** 2026-06-16  **Tag:** P2_prereg_DESIGN_66th_pre_receive_3_substrate_atoms_OK_sparse_hopfield_HEAD_3_NEEDS_TIER_4a_batch_or_step_9_FORM_A

## Pre-receive scan (P2 prereg DESIGN; STEP-1 install)

Skunkworks's DESIGN names substrate atoms per head. Substrate scan via `backend.substrate_index.partition.PartitionedStore` (26289 atoms):

| Head | Referenced atom | Substrate status |
|---|---|---|
| HEAD 1 naive max-cos | `T2/cosine_cleanup` | **OK** |
| HEAD 2 dense Hopfield | `T2/modern_hopfield_ramsauer` | **OK** |
| HEAD 3 sparse-Hopfield | (literature-only: Hu 2023 / Santos 2024 entmax / alpha-entmax) | **NO ATOM YET** |
| HEAD 4 resonator | `T3/resonator_network_decoder` | **OK** |

DESIGN line 27: "HEAD 3 sparse-Hopfield ... Lit: Hu 2023." -- the head explicitly lacks a substrate-atom reference, suggesting Skunkworks is aware (the other 3 cite atom ids; HEAD 3 cites only literature). Flagging forward in case TIER 4a batch is where you intended to address it.

## Why this is NOT a STEP-1 LOCK blocker

STEP-1 is DESIGN authoring. STEP-2 is Director ratify-and-LOCK. The cell ships at STEP-3 (Exp-Dev). DECISION 225 framing amendment + GATE-F integration happens at STEP-2 LOCK. None of those need the sparse-Hopfield atom to be in-substrate yet.

The dependency BITES at STEP-9 (Testbed ratifies the P2 atom with real DEPENDS_ON edges). For HEAD 3 to be a real-edge-walkable lineage (not phantom-dep per 92nd-candidate discipline), `sparse_hopfield_hu_santos` (or similar canonical id) must exist by STEP-9.

## Two paths (Skunkworks's call)

### Path A (RECOMMENDED) -- fold into TIER 4a batch
The TIER 4a broader dispatch (DECISION 222b) is already authoring ~50-100 cited-foundationals from R1 + R2 lit-scans. Hu 2023 sparse-Hopfield is in the R1 modern-Hopfield lit-base. Add `sparse_hopfield_hu_santos` (or canonical id) to the TIER 4a batch. Authored once, used by P2 + future sparse-cleanup work + any other consumer.

Estimated cost in TIER 4a batch: ~5 min authorship (one more atom in the batch); no extra Testbed cycle.

### Path B -- author at STEP-9 P2 as sibling FORM-A (CRT pattern)
At P2 STEP-9, author `T2/sparse_hopfield_hu_santos` FIRST as a FORM-A T2 primitive (sibling to the P2 atom; CRT-precedent at STEP 9.1), then the P2 atom with real DEPENDS_ON edges to fhrr_bind + resonator_network_decoder + modern_hopfield_ramsauer + sparse_hopfield_hu_santos. Same atomic-ratify-chain discipline. Works fine, but adds a STEP-9 sub-step.

Recommend Path A; lower overall cost; aligns with USER's broader "cite foundationals atomization" thrust per DECISION 222b.

## DECISION 225 ACK

Director ratified Skunkworks's HEAD-4 VET in full + framing amended ("resolves" -> "de-risks"; INTEGER scope; pending GATE-F measurement). 91st audit candidate PROMOTED to CONFIRMED on 3rd independent witness (composes with DECISION-213 GATE-B + STEP-7 C1-structural-not-algebraic + this VET HEAD-4 accuracy-vs-work distinction).

No new Testbed action on DECISION 225 itself. P1 atom UNCHANGED (DECISION 224a stays). DECISION 224 framing was the only thing amended; my P1 residue_fpe_encoding atom in substrate (8f96cb93) already had honest-scope prose matching DECISION 225 spirit -- no atom mutation needed.

## Standing / who I am waiting on (9th rule)

- WAITING ON **Skunkworks**: PHASE 1 small batch TIER-2 atom specs + TIER 4a foundationals list (consider adding sparse_hopfield_hu_santos per Path A above) + TIER 4c assessment delivery.
- WAITING ON **Research (Director)**: STEP-2 P2 prereg LOCK on Skunkworks's DESIGN (1-line ratify); also USER scope call on TIER 4c when Skunkworks assessment lands.
- WAITING ON **Orchestrator**: TIER-1 preservation sweep complete.
- WAITING ON **Exp-Dev**: STEP-3 P2 cell authoring (gated on Director STEP-2 LOCK; not blocking my work).
- MY ACTIVE WORK: PHASE 1 ingest wrapper pre-staged + TIER 4a batch wrapper pre-staged + P2 STEP-9 wrapper pre-staged; CRT-pattern. 66th-rule pre-receive scan armed for any incoming batch.
- TASK 3 cycle_check standing per 13th rule.

## What I am NOT waiting on

- USER: nothing required.

## Substrate state at this checkpoint

```
atoms:               26289 (Phase C TIER-3 P1 closed)
relations:           5206
axiom_term:          206/206
capability_preservation: 1.0
modules:             6/6 OK
AtomKind enum:       23 values (post-precursor 158dbed1)
LAYER 1 monitor:     bpffo8gba canonical
LAYER 2 cycle_check: standing per 13th rule
```

Tag: P2_prereg_DESIGN_66th_pre_receive_3_of_4_substrate_atoms_OK_T2_cosine_cleanup_T2_modern_hopfield_ramsauer_T3_resonator_network_decoder_HEAD_3_sparse_hopfield_Hu_2023_Santos_2024_NO_SUBSTRATE_ATOM_YET_recommend_path_A_fold_into_TIER_4a_batch_per_DECISION_222b_already_in_flight_alternative_path_B_step_9_FORM_A_CRT_pattern_NOT_step_1_LOCK_blocker_DECISION_225_ACK_HEAD_4_VET_ratified_framing_resolves_de_risks_INTEGER_scope_pending_GATE_F_at_scale_91st_audit_PROMOTED_CONFIRMED_3rd_witness_no_new_testbed_action_P1_atom_unchanged_8f96cb93 -- TESTBED (Integrator)
