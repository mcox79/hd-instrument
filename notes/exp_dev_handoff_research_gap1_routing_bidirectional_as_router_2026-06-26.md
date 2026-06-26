# exp_dev hand-off -- research: gap1 routing bidirectional-as-router (cross-domain drill)

**Filed by:** research (opus-4.7-1m)
**Date:** 2026-06-26
**Trigger:** research_gap1_routing_bidirectional_as_router_2026-06-26.md (this drill)
**Pause state:** check `data/orchestrator_paused.flag` at dispatch time.

Per [[feedback-no-experiment-design-in-prompts]]: this hand-off lists anchor candidates as pointers; cell-design + pre-reg is exp_dev's own substantive work.

---

## Anchor candidates (rank-ordered for exp_dev pickup)

### #1 (HIGHEST priority -- USER's steelman): `substrate_partition_routing_bidirectional_collide_v1_META_M7`

**Substrate-product reading:** Tests if forward-walked state + backward-walked-per-candidate states can ROUTE to correct partition WITHOUT oracle. USER intuition direct test. Replaces Cell B v2's `target_part = target_o // part_sz` with `argmax_p sum_{Z in part_p} state_fwd . state_bwd(Z)`.

**Tier hint:** TIER A (chain-grade-eligible if HP_PASS; removes BIAS-P from Cell B v2 0.955 result).

**Why now:** Cell B v2 + Cell C v2 just landed CHAIN_GRADE (this morning's verdicts). PART_ORACLE 0.955 has BIAS-P (oracle routing flag). USER explicitly asked this question in-thread.

**Cell B v2 / Cell C v2 reuse:** SAME `_forward_state` + `_backward_state` from Cell C v2; SAME `arm_compose_partition` skeleton from Cell B v2 -- replace ONLY the `target_part` line with the bidir-collide routing.

**META_M7 rail mandatory:** ARM_REPRODUCE_POINTER_CHAIN_V2_5HOP at 2000 bindings, band [0.08, 0.25].

**Decision-grade outcomes (research-suggested; exp_dev pre-reg autonomous):**
- HARD_PASS: bidir-collide top1 >= 0.80 across 3 seeds AND META_M7 in band
- HARD_FAIL: bidir-collide top1 <= 0.50 across 3 seeds (routing not viable from bidirectional)
- MIDDLE_BAND: [0.50, 0.80) -- route a 2x drill for refinement variants (max-instead-of-sum; deeper-back-walks)

**Compute hint:** ~1200s per arm per 3 seeds; estimate ~5500s wall for full 6-arm cell on local_cpu.

---

### #2 (CHEAP DECISIVE): `substrate_partition_routing_fly_lsh_v1_META_M7`

**Substrate-product reading:** Tests if fly-LSH expansion of state_fwd projects onto partition-discriminable centroids. SECONDARY USER hypothesis (substrate-native LSH router).

**Tier hint:** TIER A.

**Why now:** Cheapest router (~30s per arm per seed); useful EVEN IF #1 HARD_FAIL (LSH may discriminate where bidir doesn't because LSH uses sparse random projection rather than cleanup-noise-laden cosine).

**Cell B v2 reuse:** `fly_lsh_expand` already implemented; just need to compute LSH'd partition centroids and route by cosine.

**Decision-grade outcomes:**
- HARD_PASS: fly-LSH-router top1 >= 0.80
- HARD_FAIL: <= 0.50
- COMPOSE variant: 2-stage LSH-then-bidir (#1 + #2 composition)

**Compute hint:** ~700s per seed for composed; sub-200s for bare LSH-router.

---

### #3 (COMPOSITION): `substrate_partition_routing_two_stage_bidir_lsh_v1`

**Substrate-product reading:** Hierarchical router; LSH narrows top-K parts coarsely, bidir-collide ranks fine. Only valuable if BOTH #1 and #2 land >= MIDDLE_BAND.

**Tier hint:** TIER A (composed mechanism).

**Why now:** Only dispatch AFTER #1 and #2 verdicts arrive; if both >= MIDDLE_BAND, dispatch as evidence of INDEPENDENT discriminators.

**Decision-grade outcomes:**
- HARD_PASS: top1 >= 0.90 AND independent_lift over either #1 or #2 alone >= 0.05
- Otherwise: factor design; one signal is dominant

---

### #4 (BRAIN-GROUNDED FALLBACK): `substrate_partition_routing_bg_gated_two_layer_v1`

**Substrate-product reading:** Confidence-gated cascade. If forward-pass margin > tau: accept. Else: route to bidir-collide for that hop. Substrate analog of BG-thalamic disinhibition.

**Tier hint:** TIER B (introduces a NEW substrate primitive: routing-confidence-gate).

**Why now:** Only dispatch if #1 lands MIDDLE_BAND (NOT HARD_PASS); BG-gating is a refinement variant, not a primary discriminator.

**Decision-grade outcomes:** depends on what fraction of queries fall back; need <50% fallback for cleanly "BG-grade" claim (else collapses to bidir).

---

### #5 (LEARNED CLOSED-FORM): `substrate_partition_routing_learned_pseudoinverse_v1`

**Substrate-product reading:** Train R_route in R^{N x N_PARTS} via closed-form least-squares on training chains; inference is matrix-vector product. NO BACKPROP. Substrate's learned-projection family (kv_learned chain-grade-passed).

**Tier hint:** TIER A.

**Why now:** Only dispatch if #1 + #2 + #3 ALL HARD_FAIL (routing is the structural bottleneck; need learned signal). Closed-form solve respects substrate's no-gradient discipline.

**Decision-grade outcomes:**
- HARD_PASS: top1 >= 0.80 on held-out 20% chains; train-test gap <= 0.10
- HARD_FAIL: overfit (gap > 0.10) OR underfit (held-out <= 0.50)

---

## Context pointers (file paths; no inline summaries)

- `notes/research_gap1_routing_bidirectional_as_router_2026-06-26.md` (this drill's full reasoning)
- `notes/exp_dev_to_research_Cell_B_C_v2_META_M7_redispatch_DISPATCHED_2026-06-25.md` (Cell B/C v2 dispatch)
- `data/exp_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail/metrics.json` (Cell B v2 verdict; PART_ORACLE=0.955)
- `data/exp_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail/metrics.json` (Cell C v2 verdict; BIDIR_MEET_MID=0.62, mean_midpoint_cosine=0.0000)
- `experiments/exp_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail.py` (partition + fly-LSH primitives to reuse)
- `experiments/exp_substrate_multihop_bidirectional_meet_middle_v2_META_M7_rail.py` (`_forward_state`, `_backward_state`, `arm_bidirectional_meet_middle_rank`)
- `preregs/2026-06-25_substrate_multihop_compose_fly_lsh_multibank_partition_v2_META_M7_rail.md` (envelope template for routing pre-reg)

---

## Contract section

1. exp_dev OWNS cell design + pre-reg + smoke. Research informs anchor selection; does NOT design arms.
2. META_M7 REPRODUCE_PV2 rail is mandatory in every dispatched cell per Cell B/C v2 discipline.
3. BIAS-P scope flag from Cell B v2 is the THING being tested -- verdict_msg must explicitly state which arm removes the flag (if any).
4. Compute budget guidance only; exp_dev determines smoke vs full split, seed list, etc.
5. Skunkworks landed-VET routing per chain-grade-eligibility (TIER A cells).
6. ASCII-only; substrate-only; substrate-native primitives only; new primitive ONLY for cand #4 (routing-confidence-gate) with justification.

---

## Autonomy declaration

This hand-off is INFORMATIVE not DIRECTIVE. exp_dev decides:
- Whether to bundle #1 + #2 (research recommends YES; they share fwd-state infrastructure)
- Whether #3, #4, #5 dispatch is conditioned on #1, #2 verdicts (research recommends YES)
- Cell pre-reg envelope-fail-bands, smoke gate, seed counts, V_C value, depth
- Whether to include the V_naive_centroid arm explicitly as a falsification anchor (research recommends YES; cheap and decisive against centroid-routing)

If pause flag is set: defer dispatch; queue as priority-1 routing handoff for first non-paused window.
