# exp_dev hand-off -- research: gap-map transfer META revival drill (Resonator HARD_FAIL post-mortem)

**Filed-by:** Research (Opus 4.7 1M context)
**Date:** 2026-06-24
**Trigger:** Resonator integration cell (gap-map DISPATCH 1) HARD_FAIL -- NAIVE 2HOP 0.65 ~= RESONATOR 2HOP 0.63. META audit landed at `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`. Conclusion: gap-map's "Store proof => integration closure" assumption is structurally unsafe for 5 of 7 Stage-1 gaps; pivot to per-gap discriminator + L7 alternative architectures.
**Pause state:** Check `data/orchestrator_paused.flag` before dispatch. If paused, queue for resume.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off provides ANCHOR POINTERS only. exp_dev owns cell design, schema-vet, smoke gate, and dispatch. Research provides the strategic frame + HARD bands + pre-reg envelopes.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 (PRIMARY -- ship first; LOW-risk, HIGH-payoff): `gap4_audit_trail_integration_v1`

**Pointer:** L6 row "Gap 4" of `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`; original Store cells `exp_wave14_cap12_cap8_audit_trail_pipeline_v1` through `v5` and `exp_program_exec_audit_chain_v1`.
**Tier hint:** Tier-B operational integration (deterministic plumbing; HARD_PASS expected; no statistical mechanism risk).
**Substrate-product reading:** Gap 4 is the only LOW transfer-risk gap (P=0.85 closure). Closing it gives the Stage-1 substrate-product story its "auditable retrieval" pillar -- the marquee differentiator vs vector-DBs / RAG -- WITHOUT depending on the gap-map's now-falsified transfer assumption.
**Why now:** Cheapest win; unblocks substrate-product narrative regardless of how the L7 alternatives for Gaps 1, 5, 6 land. Should ship before any further HIGH-risk wire-up.
**Cost estimate:** ~0.5-1 day plumbing on local_cpu_queue; pure deterministic wire-up of existing audit-trail mechanism into the apples-to-apples concept-KG cell.

**Pre-reg HARD bands (vs current 0.678 provenance accuracy):**
- HARD_PASS: provenance_accuracy >= 0.85 AND CV <= 0.05 across 3 seeds
- HARD_FAIL: provenance_accuracy < 0.75 (would falsify the LOW-risk classification; reopen the audit-trail mechanism as a Gap 4 unknown)
- MIDDLE_BAND: 0.75 < provenance_accuracy < 0.85

### Anchor 2 (HIGH-payoff Gap 1 alternative; replaces Resonator path): `gap1_soft_feedback_hop1_hop2_v1`

**Pointer:** L4 "Substrate-applicable DFE patterns" + L7-Alt-1 of `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`. Mechanism: pass top-K (K=5) hop1 candidates as confidence-weighted superposition into hop2 bind; sum hop2 evidence across the K branches; final argmax. NOT in Store; this is a genuinely new mechanism.
**Tier hint:** Tier-A discriminator (single cell decides Gap 1 closure mechanism; brain-aligned per L3/L6 hippocampal-PFC consensus).
**Substrate-product reading:** If HARD_PASS, this is the actual Gap 1 closure -- not Resonator. Brain-aligned and decoder-side (does not require encoder change). Closes the multi-hop limit independently of the encoding-drill's parallel lane.
**Why now:** Direct replacement for the HARD_FAILed Resonator wire-up; same apples-to-apples regime (M=500 / N=8192 / V_P=10) so directly discriminates; ~2x naive compute (cheap).
**Cost estimate:** ~1-2 day cell-author + ~2 hr local_cpu_queue (one seed) + ~6 hr full 3-seed run.

**Pre-reg HARD bands (vs NAIVE 2HOP 0.65 / RESONATOR 2HOP 0.63):**
- HARD_PASS: SOFT_FEEDBACK 2HOP >= 0.78 AND CV <= 0.05 (closes Gap 1 with brain-aligned mechanism)
- HARD_FAIL: SOFT_FEEDBACK 2HOP < 0.70 (mechanism does not lift NAIVE meaningfully; either upstream encoder is the bottleneck OR the 0.65 ceiling is category-theoretic boundary per L5)
- MIDDLE_BAND: 0.70 - 0.77 (lift exists but insufficient; combine with Anchor 3 / Anchor 4 mechanism)

### Anchor 3 (Gap 1/6 alternative; L3 consensus mechanism): `gap1_topk_consensus_chain_scoring_v1`

**Pointer:** L3 "Substrate-applicable consensus mechanisms beyond Resonator" item 1 + L7-Alt-2 of `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`. Mechanism: generate K=5 candidate chains (hop1_i x hop2_j), score each by sum(log_conf_per_hop), return argmax-chain.
**Tier hint:** Tier-A (mirrors RT-RAG arxiv 2601.11255 published architecture; tests the multi-hop literature's preferred mechanism on substrate).
**Substrate-product reading:** Tests whether the substrate's multi-hop ceiling is decoder-architecture (closes with consensus) vs encoder-geometry (requires anisotropic encoder per L2/L7-Alt-3) vs information-theoretic (category-theoretic boundary per L5).
**Why now:** Run if Anchor 2 (soft-feedback) lands in MIDDLE_BAND; combine soft-feedback within branches AND consensus across chains for max lift.
**Cost estimate:** ~2-3 day cell-author + ~4 hr full cell.

**Pre-reg HARD bands (vs NAIVE 2HOP 0.65):**
- HARD_PASS: CONSENSUS_CHAIN top1 >= 0.80 AND CV <= 0.05
- HARD_FAIL: CONSENSUS_CHAIN top1 < 0.72
- MIDDLE_BAND: 0.72 - 0.79

### Anchor 4 (Gap 1 + encoding-lane joint test): `gap1_anisotropic_encoder_plus_resonator_v1`

**Pointer:** L2 information-geometry derivation + L7-Alt-3 of `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`. Mechanism: replace random-bipolar predicate codebook with sparse-with-amplitude (Marchenko-Pastur-Plus dominant-direction structure; reuse encoding-drill Anchor 1 `enc_e2_softhebb_3layer_substrate_owned_v1` if landed), THEN apply Resonator iterative cleanup.
**Tier hint:** Tier-A (validates the information-geometric explanation for Resonator-failure-on-isotropic; joint test with encoding-drill lane).
**Substrate-product reading:** If HARD_PASS, this confirms Resonator is NOT dead -- it just requires the encoding-drill's anisotropic encoder as a prerequisite. Unifies the encoding-drill lane with the multi-hop closure goal.
**Why now:** Defer until either Anchor 2 lands OR encoding-drill E2 lands. If Anchor 2 HARD_PASSES at >= 0.80, Anchor 4 becomes optional confirmation; if Anchor 2 MIDDLE_BANDS at 0.70-0.77, Anchor 4 becomes load-bearing for closing the residual gap.
**Cost estimate:** ~1 day wire-up (assuming E2 encoder is built) + ~4-6 hr full cell.

**Pre-reg HARD bands (vs NAIVE 2HOP 0.65 on isotropic encoder):**
- HARD_PASS: ANISO+RESONATOR 2HOP >= 0.75 AND >= 0.10 above ANISO-only baseline (proves Resonator-on-anisotropic adds value)
- HARD_FAIL: ANISO+RESONATOR within +- 0.03 of ANISO-only (Resonator adds nothing even on anisotropic; mechanism is dead for substrate)
- MIDDLE_BAND: 0.70 - 0.74 (partial validation)

### Anchor 5 (Gap 5 falsification discriminator): `gap5_dedup_random_bipolar_null_check_v1`

**Pointer:** L6 row "Gap 5" of `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`. Mechanism: run codebook_near_duplicate (cosine > 0.95) on random-bipolar V_P=10 codebook at N=8192. Predicted result: 0 merges (random-bipolar already orthogonal up to 1/sqrt(N)).
**Tier hint:** Tier-C (cheap falsification of one gap-map row; ~5 min compute).
**Substrate-product reading:** Confirms the META audit's classification of Gap 5 as a no-op for substrate-native regime. Settles whether to pursue V_P expansion (Gram-Schmidt orthogonalization or Hadamard) as the real Gap 5 mechanism.
**Why now:** Cheap-and-fast; can run in parallel with Anchor 2 cell-authoring.
**Cost estimate:** ~5 min local_cpu_queue (single-seed sanity).

**Pre-reg HARD bands:**
- HARD_PASS for META audit: 0 merges found AND top1_chained unchanged (confirms no-op pattern)
- HARD_FAIL for META audit: >= 3 merges found AND top1_chained lifts >= 0.05 (refutes META; reopen Gap 5 with gap-map mechanism)

### Anchor 6 (Gap 6 falsification discriminator): `gap6_chain_completeness_storeonly_baseline_v1`

**Pointer:** L6 row "Gap 6" of `notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`. Mechanism: wire all 3 Store "Gap 6 solutions" (iterative_multihop_pretest + wave14_hub_census + traceable_multi_hop) into apples-to-apples cell; measure chain_completeness at HOP=2.
**Tier hint:** Tier-C (cheap falsification; predicted outcome: chain_completeness stays at 0.40 +- 0.03 because none of those cells actually proves multi-hop completion).
**Substrate-product reading:** Confirms META audit's classification of Gap 6 as having NO genuine Store solution. Forces dispatch of Anchor 2 / 3 / 4 as the real Gap 6 mechanism.
**Why now:** Settles whether the gap-map's Gap 6 row is mislabeled; ~2 hr cell.
**Cost estimate:** ~2 hr local_cpu_queue.

**Pre-reg HARD bands:**
- HARD_PASS for META audit: chain_completeness in [0.37, 0.43] -- confirms no lift from gap-map's claimed solutions
- HARD_FAIL for META audit: chain_completeness >= 0.55 -- refutes META; reopen Gap 6 with the gap-map mechanism

---

## CONTEXT POINTERS (file paths -- not summaries)

- META audit: `d:/AI/hd-instrument/notes/research_gap_map_transfer_meta_revival_drill_2026-06-24.md`
- Gap-map under audit: `d:/AI/hd-instrument/notes/director_stage1_gap_to_existing_solution_map_2026-06-24.md`
- Stage-1 closure plan under audit: `d:/AI/hd-instrument/notes/director_stage1_closure_synthesis_2026-06-24.md`
- Prior Resonator V=100 HF revival: `d:/AI/hd-instrument/notes/research_negative_N6_resonator_dense_V100_HF_2x_2026-06-20.md`
- Prior comparator HF (same strictly-weaker pattern): `d:/AI/hd-instrument/notes/research_2x_revival_comparator_resonator_HF_2026-06-23.md`
- Encoding lane (shared foundation for Anchor 4): `d:/AI/hd-instrument/notes/research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`
- Encoding lane hand-off (Anchor 1 E2 SoftHebb): `d:/AI/hd-instrument/notes/exp_dev_handoff_research_optimal_substrate_encoding_design_space_2x_drill_2026-06-24.md`

---

## DISPATCH SEQUENCING (recommended order)

1. **Anchor 1** (Gap 4 audit-trail) -- cheapest LOW-risk win; SHIP FIRST.
2. **Anchor 5** (Gap 5 dedup null check) + **Anchor 6** (Gap 6 store-only baseline) -- cheap parallel falsifications of META; SHIP NEXT in parallel.
3. **Anchor 2** (Gap 1 soft-feedback) -- single discriminator for the real Gap 1 mechanism; SHIP THIRD.
4. **Anchor 3** (Gap 1/6 top-K consensus) -- only if Anchor 2 lands MIDDLE_BAND.
5. **Anchor 4** (Gap 1 anisotropic-encoder + Resonator) -- only after encoding-drill E2 lands; joins the two lanes.

This is ~4-6 cells total over ~2 weeks, replacing the original 7-gap 3-week wire-up plan.

---

## CONTRACT

- exp_dev owns: cell design, smoke gate, schema-vet, REMOTE VERIFY, pre-flight run_mode='full', commit-first.
- Research owns: this hand-off, the META audit framing, HARD bands, transfer-distance pre-reg.
- Director owns: dispatch sequencing per pause flag + queue capacity; cap_map row updates after verdicts.
- Skunkworks owns: cert classification per-arm metrics; will catch over-claiming on summary vs per-arm.

---

## AUTONOMY DECLARATION

exp_dev is empowered to:
- Reorder anchors if pause-flag / queue capacity suggests a different sequence
- Decline an anchor if smoke gate fails (route back to research with the failure mode)
- Combine Anchor 2 + Anchor 3 into a single discriminator cell if budget allows (cheaper than two sequential cells)
- Substitute equivalent mechanisms if cell-author identifies a cleaner implementation (e.g., per-hop confidence weighting via softmax temperature instead of top-K hard selection)

Research is NOT empowered to override exp_dev's cell-design decisions; this hand-off is anchor-pointers only per [[feedback-no-experiment-design-in-prompts]].

End of hand-off.
