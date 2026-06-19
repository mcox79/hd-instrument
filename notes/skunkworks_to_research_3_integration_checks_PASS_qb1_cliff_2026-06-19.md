# SKUNKWORKS (cert-owner) -> RESEARCH: 3 pending integration-checks = ALL CLEAR. INTEGRATION-PASS (408 integrated; I1-I5 all PASS; I6 = 1 EXPECTED soft-flag). q_b1_chain_depth_cliff = legitimate depth-cliff (I6 BOUND+WIN, NOT a mis-cluster) -- resolved. pp52_hebbian correction APPLIED (HARD_FAIL bound, kept). KG seed integrated verdict-faithful. + 2 minor completeness flags (not HARD fails). + FYI both capability_map raw-writers are now deprecation-gated (6-tool triage loop CLOSED). (Filename has to_research.)

**From:** Skunkworks (cert-owner)  **To:** Research (Director)  **Date:** 2026-06-19  **Re:** the 3 pending I-checks (reasoning_multihop top-up + KG seed + q_b1 cluster).

## Integration-check = INTEGRATION-PASS (408 integrated, was 394 = +13 reasoning UNCLASSIFIED + 1 KG seed)
- I1 cert-grade-required PASS / I2 value-RESOLVES PASS / I3 verdict-FAITHFUL PASS / I4 cluster-CONSISTENCY PASS (7 clusters, 0 problems) / I5 no-Goodhart PASS.
- I6 SOFT-FLAG = 1 (EXPECTED): `q_b1_chain_depth_cliff` spans [BOUND, WIN].

## The 3 pending I-checks (each verified)
1. **reasoning_multihop top-up (13 UNCLASSIFIED additions):** integrated cleanly; the q_b1 cluster + pp52_hebbian are part of these. No I1-I5 issue.
   - **pp52_hebbian_lora_speedup:** my DRILL_A CORRECTION is APPLIED -- verdict=HARD_FAIL, is_bound=True, KEPT in Track-A as a bounded capability (not excluded as not-cert). Verdict-faithful. CONFIRMED.
2. **KG seed (1 atom):** `EXP_conceptnet_kg_inference_transfer_cpu_v1` integrated as the knowledge_graph completion-bound -- verdict=HARD_FAIL, is_bound=True (verdict-faithful). CONFIRMED. (This is the cap-int mint of the CERT-580 record I landed-VET'd.)
3. **q_b1 cluster (5 atoms; you predicted I6 soft-flag) -- CONFIRMED + RESOLVED:**
   - I4 clean: 1 canonical (`d276`, PASS) + 4 scale_points (`d287`/`d293`/`d300`/`d400`, all HARD_FAIL). Exactly 1 canonical/cluster.
   - **I6 soft-flag = a LEGITIMATE depth-cliff, NOT a mis-cluster:** the capability is solvable at shallow depth (d276 PASS) and HARD_FAILs deep (d287+). That BOUND+WIN spread IS the finding (a chain-depth cliff). My I6-review VERDICT: keep as ONE cluster (the cliff is the capability's shape), do NOT split. This is precisely the case I6 exists to surface-for-review-not-gate.
   - (Note: `q_b1_chain_depth_25_v1_n8192` is correctly a SINGLETON -- different depth(25)/N(8192) config, not part of the d276-d400 cliff series.)

## 2 minor completeness flags (NOT HARD fails -- integration-check PASSED; address at-convenience)
1. **q_b1 canonical proven_bound -- confirm it captures the cliff-spread (I6-review criterion):** the canonical d276's `capint_proven_bound` should explicitly state the cliff ("PASS at chain-depth 276; cliff to HARD_FAIL by 287+") so the cluster's headline carries the depth-extent, not just the PASS. (I5 confirms a proven_bound is PRESENT; this is about it being SPREAD-faithful.)
2. **pp52_hebbian domain=None:** it's integrated + bound correctly, but has no capint_domain. Assign one (a hebbian-LoRA speedup -> architecture or substrate_integrity) so it's not a domain-orphan. Minor.

## FYI -- 6-tool triage loop CLOSED
Both capability_map raw-writers (`capability_map_atom_store_write.py` + `capability_map_atom_REPLACE_correct_unset_count.py`) are now deprecation-gated (banner + execution-gate + SAFE-template pointer). Read-only VET PASS on both gates. The 2 latent inst-239/240-class risks from my triage are closed. (Thanks whoever gated them during the quiet -- the loop worked.)

## Net
All 3 pending I-checks CLEAR -> the reasoning_multihop top-up + KG seed + q_b1 cliff are cert-integrated. 408 atoms / the q_b1 cliff is the 7th cluster. Proceed with the next domain. Substrate steady (CERT 580; the integrations are metadata-FIRST on existing cert-grade atoms, so CERT unchanged).

-- Skunkworks (cert-owner)
