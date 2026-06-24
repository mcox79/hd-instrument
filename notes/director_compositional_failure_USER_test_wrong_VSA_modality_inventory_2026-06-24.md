# director_to_research_compositional_failure_test_wrong_VSA_modality_inventory_2026-06-24

## USER input (course correction to drill a443dee696efbc82d)

USER 2026-06-24: "the test must not be correct on the compositional generalization. Also remember - we tried a lot of different modalities in experiments - fhrr for example etc."

Two assertions:
1. The ARM 2 test design is broken (HRR IS compositional; test must be mismeasuring)
2. Existing VSA-modality data (FHRR, GHRR, MAP, VTB, sparse-bipolar) must be mined before any new comparison cell

## Confirmation of E1: ARM 2 test IS broken

Drill output file not yet on disk (`notes/research_compositional_generalization_critical_failure_2x_drill_2026-06-24.md` absent at check-time). Read the source directly.

**Cell:** `experiments/exp_substrate_brain_aligned_aliveness_shotgun_v1.py` lines 185-230.

**Verdict on ARM 2 design (E1 confirmed PARTIALLY — different root cause than `pair_storage`):**

The code IS role-binding-shaped:
```python
bank += _bind(subj[i], obj[j])      # line 199; bind = circ-conv via FFT
rec = _unbind(bank, subj[i])        # line 205; unbind on heldout subj
pred = argmax cosine(rec, obj_codebook)
```
So it's NOT trivial pair-storage. BUT the test is still broken for a DIFFERENT reason:

**Root cause:** HRR circular-convolution (lines 104-113) assumes DENSE random unit-norm vectors (Plate 1995). The cell feeds it **sparse-bipolar at f=0.05** (line 188-189). Sparse-bipolar FFT spectra concentrate in few bins -> bind product not in HRR's well-conditioned regime. Stacked harm: NO per-bind normalization (line 199 raw sum); bank L2 grows as sqrt(M) while obj codebook stays sparse -> unbind result lives off the codebook manifold.

**Evidence from per-seed partial:** `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/partial_metrics_s7.json`:
- `in_distribution_top1: 0.10` (TRAIN-pair recall barely above chance 0.05)
- `holdout_top1: 0.0`
- `mean_cosine_correct_holdout: -0.0008` (statistically zero)

If TRAIN-pair recall is at chance, the mechanism is broken on the recall basis — not on generalization. The cell's own self-test (line 516-519) uses dim=4096 + n_subj=n_obj=4 (M=8 train pairs) — orders of magnitude lighter crosstalk — and gates on in_dist_top1 > 0.50, which is permissive. Full run at M=200 superposition with sparse-bipolar primitives crosses an interference threshold the smoke never touched.

**Counter-evidence that HRR CAN do compositional generalization on this substrate** when designed correctly: `data/exp_contextual_encoding_hrr_PRODUCTION_held_out_v1/metrics.json` — MIDDLE_BAND with `ARM_BIND_RECENT_5: acc=0.412 lift=+0.212` over static word2vec baseline on heldout contexts. HRR bind/unbind generalizes; this cell's combination of primitives + load doesn't.

## VSA-modality inventory (Store-mine before any new comparison cell)

All paths under `d:/AI/hd-instrument/`.

### Cells/data with verdicts

| Cell | Modality | Verdict | Key metric |
|------|----------|---------|------------|
| `data/exp_ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1/` | FHRR vs GHRR | MIDDLE_BAND | GHRR dir_cos=0.057 (non-commutative WIN); FHRR=1.0 (commutative FAIL); recall@200 essentially tied 0.795 vs 0.810 |
| `data/exp_fhrr_rs_parity_cpu_v1/` | FHRR | HARD_PASS | Reed-Solomon erasure on FHRR phase-domain; recovered-recall=1.0 (K=6 R=2) |
| `data/exp_multihop_fhrr_binding_cpu_v1/` | FHRR | HARD_FAIL | ASDiv-1op=0.183 vs target 0.45; binding does NOT beat role-labels for math-word QA |
| `data/exp_hrr_depth_budget_sparse_bipolar_v2/` | sparse-bipolar HRR | HARD_PASS | f=0.02 vs dense lift=53.4x at N=4096 (Willshaw super-capacity confirmed) |
| `data/exp_pp55_vsa_binding_n65536_v5_n65536/` | VSA dense | MIDDLE_BAND | mean_cos=0.99990 (within band but seeds_hp=2/5) |
| `data/exp_substrate_sc_vsa_scaling_probe_partition_routing_10M_gpu_v1/` | VSA+L1 partition | HARD_PASS | routed_recall@10=0.933 @10M; substrate scales |
| `data/exp_contextual_encoding_hrr_PRODUCTION_held_out_v1/` | HRR (dense+context) | MIDDLE_BAND | ARM_BIND_RECENT_5 acc=0.412 lift=+0.212 on HELDOUT contexts -- HRR DOES generalize when designed right |

### Other cells present (not yet peeked)

`exp_depth_pinned_fhrr_clipped`, `exp_depth_pinned_fhrr_fanout3`, `exp_depth_pinned_fhrr_l2bundle`, `exp_depth_vtb` (VTB modality), `exp_differentiable_vsa`, `exp_lap7_cont_truth_fhrr_cpu_v1`, `exp_lap8_bayesian_fhrr_cpu_v1`, `exp_multidrive_vsa_policy_h3_cpu_v1`, `exp_nl_vsa_oracle_parse_v1`, `exp_pp55_vsa_binding_n{16384,32768,131072}`, `exp_recurrent_vsa`, `exp_substrate_compositional_generalization_K10_to_K20_v1_n4096` (compositional-gen test on different K!), `exp_vsa_binding_n8192_v2`, `exp_vsa_binding_over_static_skahm_class_v1_n4096`, `exp_vsa_map_permute_sequences_v1`, `exp_vsa_permute_long_seq_gpu_v1`, `exp_wave14r_multihop_FHRR_*` (3 cells), `exp_wave14i_compositional_gen`, `exp_ghrr_charlm`.

### Notes/handoffs with substantive priors

- `notes/research_held_out_retrieval_generalization_VSA_2026-06-17.md` (direct topic match)
- `notes/exp_dev_to_research_testbed_STATUS_P3_built_queueready_GHRR_ruled_out_standing_on_Testbed_ingests_2026-06-13.md` (GHRR ruled out at one tier)
- `notes/exp_dev_to_skunkworks_research_NOVEL_ASSEMBLY_REJECT_ACCEPTED_ghrr_closes_compositional_rediscovery_not_invention_2026-06-15.md`
- `notes/research_synthesis_skunkworks_AUDITOR_GATE_PASS_triple_ratify_safe_42nd_honest_finding_fhrr_cycle_logged_for_hygiene_2026-06-15.md`
- `notes/research_drill_substrate_VSA_position_is_meaning_4x_2026-06-12.md`
- `notes/research_drill_vsa_composition_decomposition_benchmark_methodology_2x_2026-06-12.md`

## Recommendation: corrected compositional generalization cell

Do NOT re-run brain-aligned ARM 2 as-designed. Replace ARM 2 with a corrected cell that:

1. **Picks the modality from the inventory winners**:
   - **DENSE HRR with unit-norm vectors** (the design HRR was built for; not sparse-bipolar)
   - OR **FHRR** (phase-domain, well-conditioned for superposition at this M)
   - OR **GHRR** if directionality matters (non-commutative win documented)

2. **Per-bind normalization** + bank L2 normalization on each addition; matches the regime where `exp_contextual_encoding_hrr_PRODUCTION_held_out_v1` got lift=+0.212

3. **Verify-the-referent gate**: in_distribution_top1 MUST be >0.70 on TRAIN pairs at the chosen M before holdout result is even reported (sanity floor — last cell shipped holdout=0 with in_dist=0.10, clearly broken-mechanism not failed-capability)

4. **Held-out at same scale**: 20x20 with 50% coverage IF in-dist passes; if not, dial M down until in-dist crosses 0.70 then test heldout at that M

5. **Comparator arm**: same setup with sparse-bipolar+raw-circ-conv (the broken arm) so the methodology-confound is documented INSIDE the cell, not in a separate followup

6. **No new dispatch yet** — fact-finding only per Director instruction. Drill agent should ship corrected pre-reg; Skunkworks ratifies; THEN dispatch.

## Cite

- ARM 2 broken-mechanism evidence: `data/exp_substrate_brain_aligned_aliveness_shotgun_v1/partial_metrics_s7.json` `in_distribution_top1=0.10`
- HRR-CAN-generalize counter: `data/exp_contextual_encoding_hrr_PRODUCTION_held_out_v1/metrics.json` ARM_BIND_RECENT_5 lift=+0.212
- GHRR directionality structural win: `data/exp_ghrr_vs_fhrr_triple_encoder_capacity_directionality_cpu_v1/metrics.json` `ghrr_dir_cos=0.057` vs `fhrr_dir_cos=1.0`
- Sparse-bipolar IS valid in autoassociative regime: `data/exp_hrr_depth_budget_sparse_bipolar_v2/` (HARD_PASS, lift=53.4x) — but that cell does NOT use HRR-bind, it uses Hopfield-style cleanup; sparse-bipolar + circ-conv is the broken combo
