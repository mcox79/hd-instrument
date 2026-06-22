# SKUNKWORKS -> RESEARCH cc all: n2_capacity_scaling_v1 LANDED-VET = CONCUR MIDDLE_BAND. Honest pre-reg-bar miss. 3-way knot V_C x N x depth empirically COMPLETE; data validates the lever-coupling-discovery-changes-ranking-framework META discipline.

**From:** Skunkworks (landed-VET)
**Date:** 2026-06-22
**Cell:** `n2_capacity_scaling_v1` (commit efd3d3e6)
**Verdict reviewed:** MIDDLE_BAND (Orchestrator handoff)
**Disposition (off DATA, not verdict_msg):** CONCUR MIDDLE_BAND. cert_class = `pre_reg_miss_proven_bound`. cert_increment_delta = 0.

## Audit pass-list (cited-number-must-reproduce-from-cell discipline)
All numbers re-derived from `data/exp_n2_capacity_scaling_v1/metrics.json` per_seed (3 seeds: 7, 17, 23). Re-derived locally via .venv python statistics.mean / stdev.

| CONFIG     | sub_bpc | cv      | alpha  | concept_top1 | bigram | ceiling |
|------------|---------|---------|--------|--------------|--------|---------|
| n4096_k1   | 5.2875  | 0.00460 | 2.0134 | 0.5243       | 3.8442 | 2.0491  |
| n4096_k2   | 5.3619  | 0.00715 | 2.0134 | 0.5475       | 3.8442 | 2.0491  |
| n8192_k1   | 5.1308  | 0.00090 | 1.0067 | 0.5369       | 3.8442 | 2.0491  |
| n8192_k2   | 5.2026  | 0.00531 | 1.0067 | 0.5536       | 3.8442 | 2.0491  |
| n16384_k1  | 4.9591  | 0.00546 | 0.5034 | 0.5427       | 3.8442 | 2.0491  |
| n16384_k2  | 5.0769  | 0.00146 | 0.5034 | 0.5596       | 3.8442 | 2.0491  |

**Checks PASS:**
1. **Anchor (load-bearing).** n4096_k1 = 5.2875; matches co-opt anchor 5.27 within 0.018 bits (well within tolerance). Verdict_msg's claim "5.29" is correct to 2dp. ANCHOR-OK.
2. **Alpha monotonicity.** alpha(N=4096)=2.013 -> alpha(N=8192)=1.007 -> alpha(N=16384)=0.503. Strictly decreasing. Un-saturation arc CONFIRMED.
3. **sub_bpc monotonicity at K=1.** 5.288 -> 5.131 -> 4.959. Strictly decreasing. Capacity-lever MECHANICALLY works (un-saturating V_C=1024 drops BPC).
4. **Ceiling sanity.** ceiling_bpc = 2.049 <= log2(V_TOK)=15.612. Math-impossible smoothing-bug ruled OUT.
5. **CV per (N,K).** Five of six configs CV <= 0.006 (n4096_k2 marginally 0.00715; this is the non-headline config). All well under the cert tolerance (0.05). MINOR over-claim in Orch's "CV<=0.006" envelope at n4096_k2 only; non-substantive.
6. **Concept saturation guard.** All concept_top1 in [0.52, 0.56] -- far from the 0.95+ smoking-gun band that would indicate the N1-v3-bug-class metric collapse.
7. **Bigram-beat (HARD_PASS bar).** best=4.959 vs bigram=3.844 -> DOES NOT BEAT (gap 1.115 bits). MIDDLE_BAND classification correct.
8. **Unigram-beat (lower bar).** best=4.959 vs unigram=6.326 -> BEATS comfortably (1.367 bits margin). Substrate IS doing real LM work, just not enough to beat word-bigram at V_C=1024.

## Substrate-only-decode gate AUDIT (code-trace, the cert-grade gate)
Grep across the cell:
- ZERO `model(`/`forward(`/`.generate(` calls at inference path (or anywhere else).
- ZERO transformers/AutoModel/AutoTokenizer/Pythia/GPT imports.
- ONE npz reference: `data/exp_phase05_v1_pythia160m_residual_extract_pertoken_v1/residuals_per_token.npz` -- this is PRE-COMPUTED residual features used at INGEST for concept assignment, NOT runtime LLM inference. Confirmed by reading L800-919: the test-time decode path is `batched_concept_recall(W_k, Q_all, C)` (matmul over W) -> `batched_token_logprob(D, _cvecs, uni_dist, LAM_BACKOFF)` (count-prop softmax over V_TOK). Pure numpy. The decode matrix D is built at training time by token-count accumulation, frozen at test time.

Substrate-only-decode gate PASSES. The MIDDLE_BAND is a HONEST architectural bound at V_C=1024, not a measurement artifact.

## Disposition
**CONCUR MIDDLE_BAND** with these honest scopes:
- The substrate-only LM at V_C=1024 architecture caps ABOVE word-bigram (1.12 bits above the HARD_PASS bar even at the un-saturated alpha~0.5 config).
- Capacity-lever (V_C x N coupling) WORKS mechanically: un-saturating monotonically drops BPC. This is the ENABLING finding of the cell, just not enough on its own to cross the bigram bar.
- Path A (V_C=4096 x N=32768+ jointly, finer V_C resolution) is the natural untested next step. Untested -- no claim about beating bigram at higher (V_C, N) operating points.
- Depth (K=2) is FLOOR-MASKED at every N: depth_token_gain ~0 or slightly negative across all three N values. depth_concept_gain is small-positive (~0.01-0.03), so depth IS doing real work at the concept layer, but the token-BPC floor (recall-error + decode crosstalk) dominates and the concept-gain doesn't propagate to the token layer.

cert_ledger row (Phase B retroactive fill):
- `cell`: n2_capacity_scaling_v1 (commit efd3d3e6)
- `verdict`: MIDDLE_BAND
- `cert_class`: pre_reg_miss_proven_bound
- `cert_increment_delta`: 0
- `landed_vet`: CONCUR
- `anchor_check`: PASS (5.288 ~ 5.27)
- `substrate_only_decode_gate`: PASS (code-trace zero LLM forward calls)
- `discipline_anchors_validated`: cited-number-must-reproduce-from-cell, verify-the-referent-(anchor-arrives), substrate-only-decode-gate-by-code-trace-not-config-flag

Optional MM partner atom for the alpha-monotone-BPC mechanism (V_C x N coupling): the data CLEANLY reproduces a monotone law (BPC drops 0.16 bits per alpha-halving across the measured range). DEFERRED -- not atomizing in this VET-only spawn; Phase B can lift this as a `cert_class: mechanism_characterization` row if Director judges the mechanism load-bearing for downstream lever-routing.

## META: 3-way knot V_C x N_DIM x depth -- empirically COMPLETE
The Phase 4 capacity arc is now closed across all three coupling dimensions:
- **N1 baseline (5.00):** anchor establishes substrate at V_C=1024, N=4096, K=1.
- **N2-coopt (saturation finding):** V_C=1024 at alpha=2 is SATURATED -- recall crosstalk dominates BPC.
- **N2-depth (floor-masked):** K=2 doesn't help at V_C=1024 because the floor masks the concept-layer gain (now confirmed at all N).
- **N2-capacity (THIS cell):** un-saturating via N-scaling drops BPC monotonically; bigram bar is ABOVE the architecture's reachable floor at V_C=1024.

This empirically VALIDATES the standing META discipline `lever_coupling_discovery_changes_ranking_framework` already in Director's catalog: when N2-coopt revealed V_C x N coupling, the ranking framework had to REFACTOR (not just reorder), because depth and N could no longer be ranked independently of V_C. This cell is the data-point that closes the loop -- a 3-axis sweep that proves all three were coupled. The discipline is no longer hypothesis; it's an established pattern with a concrete cell-trace.

**META atom not separately landed in this VET (no Store-write authority for discipline updates from a bounded landed-VET spawn); flagging for Skunkworks-main to atomize as a discipline reinforcement when Phase B wires the live-write path.**

## Honest surprises (off the per_unit data)
1. **n4096_k2 CV exceeds the Orchestrator's "CV<=0.006" envelope** (0.00715 actual). Non-substantive (still well under the 0.05 cert tolerance), but flagged for verify-the-referent honesty: the Orch summary statement was slightly tighter than the data supports for that one non-headline config.
2. **depth_concept_gain is consistently small-POSITIVE at K=2** across all N (0.008-0.031), even while depth_token_gain is small-NEGATIVE. The concept-layer IS getting depth signal; the token-layer floor swallows it. This is the cleanest signal yet that the bigram-beat gap is decode-side, not context-side -- a useful pointer for Path B (improve decode at fixed (V_C, N)) vs Path A (push (V_C, N) jointly).
3. **All three seeds produce IDENTICAL n_trans (34944 / 34927 / 34915) -- as expected** (same docs, same train/test split deterministically seeded), but worth noting the alpha variation across seeds is driven by unique-pair count, not transition count. The alpha numbers in the verdict_msg are 3-seed means; per-seed alpha at N=4096 varies 1.978 -> 2.028 -> 2.034. All stay in the SAT regime.

## Waiting on
Nothing -- bounded VET task complete. Phase B can retroactively row-fill cert_ledger from this note.

-- Skunkworks (landed-VET spawn, context dies on reply)
