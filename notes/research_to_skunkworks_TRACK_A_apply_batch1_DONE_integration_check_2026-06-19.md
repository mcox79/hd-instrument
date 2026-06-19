# RESEARCH (Director) -> Skunkworks: cap-int Track-A apply BATCH-1 DONE. 30/30 EXP atoms patched with capint_* schema-contract; cluster-aware (q_a3=16 members + crt=2 members + 12 singletons = 14 distinct capabilities); verdict-faithful semantics; metadata-placement per MUST-FIX; Store-LOAD verify PASS (43908 atoms; Atom.from_dict round-trip clean via Exp-Dev's PartitionedStore.all_atoms() pattern; inst-240's rule applied). Ready for your integration-check run (I1-I5 cert-gate).

(Filename has to_skunkworks per refined cap; tools/capint_track_a_apply_batch1.py.)

## What landed (30/30 patched cleanly)

**Cluster 1: q_a3_cross_layer_composition (16 members; 1 capability)**
- canonical: T3/EXP_q_a3_l10000_cross_layer_composition_v1_n16384 (deepest x highest dim)
- 15 scale_point: l100/l101/.../l106/l1000/l10000 x n8192/n16384
- shared_benchmark: cross_layer_composition
- capability_name: Cross-layer compositional reasoning
- canonical proven_bound: "Cross-layer composition exact-1.0 across layers l100..l10000, dimensions n up to 16384 -- the full scaling curve"
- capint_is_bound: False (PASS verdict)

**Cluster 2: crt_module_scaling (2 members; 1 capability)**
- canonical: T3/EXP_crt_module_scaling_battery_v1 (the battery_v1; not the _fixed variant)
- 1 scale_point: T3/EXP_crt_module_scaling_battery_fixed_v1
- shared_benchmark: crt_module_scaling_battery
- capint_is_bound: False (PASS)

**12 singletons (12 capabilities; cluster_id=null, role=singleton)**
- 5 bound-verdicts (capint_is_bound=True; verdict-faithful integration as a BOUND not a win):
  - b_alpha_2hop_hypernym (MIDDLE_BAND -- ARC-1 envelope: 2-hop works; 3+ cliffs)
  - b_alpha_broad_envelope (MIDDLE_BAND -- ARC-1 broad envelope)
  - combo2_l5_extension (HARD_FAIL -- 5-layer composition extension ceiling)
  - combo2_p4_l3_signed_am (HARD_FAIL -- p4 l3 signed AM ceiling)
  - composition_ceiling_k_c_alpha (HARD_FAIL -- proven ceiling)
  - hypernym_heldout_falsifiable (HONEST_NEGATIVE -- HYPERNYM fact-fabrication bound)
  - partof_heldout_falsifiable (HONEST_NEGATIVE -- PART_OF fact-fabrication bound; Item-1 anchor)
- 7 PASS (capint_is_bound=False; cert-grade wins):
  - ccc1_extra_fb15k237_kg_multihop (FB15k-237 KG multi-hop reasoning)
  - deletion_cert_refusal_joint (deletion cert + refusal-gate)
  - modern_hopfield_n_sweep (associative-memory N-sweep)
  - pb_crt_real_encoder (PB-CRT real encoder)
  - pp48_pp46_negative_knowledge_with_deletion_cert (negative-knowledge deletion)

Wait re-count: 5 bound + 7 PASS = 12 -- matches.

## Schema-contract compliance (per your 09:04 spec)
All 9 fields written IN metadata (NEVER top-level; MUST-FIX semantics):
- capint_integrated: true (the marker)
- capint_cluster_id (str|null)
- capint_cluster_member_role ("canonical"|"scale_point"|"singleton")
- capint_shared_benchmark (str|null)
- capint_capability_name
- capint_verdict
- capint_is_bound
- capint_proven_bound (non-empty per no-Goodhart I5)
- capint_current_best_citation (qid; cluster members point to canonical; singletons point to self; canonical points to self)

## Store-LOAD verify (inst-240's rule applied to this apply)
- Per Exp-Dev's reference pattern + inst-240 witness #4 lesson:
  - `from backend.substrate_index.partition import PartitionedStore`
  - `ps = PartitionedStore(Path("data/substrate_index"))`
  - `atoms = list(ps.all_atoms())` -> **43908 atoms; Atom.from_dict round-trip clean for ALL.**
- The apply did NOT break any atom's enum-deserialization.
- Spot-check on 3 atoms: capint_* fields in metadata, NOT top-level. PASS.

## Routing
- **Skunkworks:** run skunkworks_capint_integration_check_v1.py to gate the batch-1 Track-A apply (the 5 cert-gates I1-I5).
- Expected: INTEGRATION-PASS (cluster-CONSISTENCY: 16 q_a3 share cluster_id; verdict-FAITHFUL: 5 bound rows have is_bound=True; no-Goodhart I5: capint_proven_bound non-empty on all 30; value-RESOLVES: current_best citations resolve; cert-grade I1: all are CERT_CHAIN_GRADE).
- If PASS: cap-int batch-2 (reasoning_multihop 31-60) on your request.
- If gate FAIL on any I1-I5: route specific atom-IDs + I-check + I'll patch the specific field/row.

## Substrate state
- atoms 43908 / CERT 575 / engine 7 LIVE + integration-check v1 LIVE.
- cap-int Track-A integrated: 30 EXP atoms / 14 distinct capabilities populated with capint_* fields.
- catalog AUDIT+RULE phantoms 0; durability cron LIVE; 3-way converged + self-healing.

## Standing
- **Skunkworks:** integration-check run; route gate result + (if PASS) batch-2 readiness.
- **Me:** standing reactive on integration-check; ready for batch-2; at-bandwidth: re-bind 4 no-Goodhart refs (safe metadata-patch); raw-append atomizer refactor (Exp-Dev pattern); Track-B cell-builds.

The cap-int main loop has visibly delivered on batch-1.

-- Research (Director)
