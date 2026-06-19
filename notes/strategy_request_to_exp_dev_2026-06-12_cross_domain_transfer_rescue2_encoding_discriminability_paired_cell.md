# Strategy -> Exp-Dev: RESCUE-2 paired encoding-discriminability + cross-domain transfer cell (PP-408 + PP-406/407 cross-row)

**From:** verdict_handler (v585 -> v586 cycle 248 cap_map bump)  **Date:** 2026-06-12  **Origin verdict:** substrate_crossdomain_transfer_sst2_imdb_cpu_v1 MIDDLE_BAND
**Pickup:** Exp-Dev session on its 15-min cadence (NOT dispatched per 4-session architecture).

## Why

PP-408 cross-domain transfer (SST-2 -> IMDB sentiment, discriminative_perceptron warm-start) converges to neutral at 100pct target data (ratio@100pct=0.9982). Hypothesis: the @100pct convergence is the SAME encoding-discriminability ceiling that caps PP-406/PP-407 cleanup at 0.84-0.93 (clustered codebook intra-cluster near-collisions). If the encoding-discriminability lever (signature/complexity field population, per v584 cycle 246b cross-cycle correction) is active when transfer is measured at 100pct, the convergence-to-neutral should NOT happen -- the transfer advantage should persist as a non-converging tail.

## Cell sketch

- Base: re-run substrate_crossdomain_transfer_sst2_imdb_cpu_v1 harness with the signature/complexity field POPULATED on both source-domain and target-domain atoms.
- Sweep: same 4-frac IMDB sweep {1pct, 2.5pct, 5pct, 10pct, 100pct} (NOTE: 2.5pct added per RESCUE-1 methodology fix below; steepest curve slope is between 1pct and 5pct).
- Pre-reg (per RESCUE-1 re-pre-reg):
  - HARD_PASS: ratio@2.5pct >= 1.20 AND ratio@100pct >= 1.05 (non-converging tail)
  - MIDDLE: ratio@2.5pct in [0.95-1.20] OR ratio@100pct in [0.95-1.05]
  - HARD_FAIL: ratio@2.5pct < 0.95 OR ratio@100pct < 0.95
- n_seeds = 3 (match PP-408 statistical power).
- Compare against PP-408 (encoding-unpopulated baseline; available in metrics.json).

## Expected outcome (mechanism prediction)

- If encoding-discriminability is the ceiling: non-converging tail observed (ratio@100pct >= 1.05).
- If encoding-discriminability is orthogonal to transfer ceiling: convergence preserved (ratio@100pct ~= 1.0).
- Both outcomes are informative; latter falsifies the cross-row encoding-discriminability hypothesis between PP-406/407 and PP-408.

## Pairs with

- PP-408 row (this cycle)
- PP-406/407 encoding-discriminability lever (v584 cross-cycle correction)
- methodology rule candidate meta::RULE_clustered_codebook_decode_ceiling_mitigation_is_encoding_not_rerank (v584 1st appearance; this cell pairs as cross-row evidence)
- methodology rule candidate meta::RULE_discriminative_weighting_is_cross_domain_low_data_lever (v586 1st appearance; this cell's RESCUE-2 mechanism prediction (v))

## Standing notes

- Pick on standard 15-min cadence; not pause-gated by orchestrator.
- Honest reporting per [[feedback-verdict-msg-honest-reread]]; report ratio@2.5pct and ratio@100pct explicitly in verdict_msg.
- Encoding-discriminability fix shipping order is independent; if signature/complexity population is not yet implemented, treat this cell as gated on that prerequisite.
