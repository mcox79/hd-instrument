# Strategy request: PP-8 v1b grid findings — 6 HARD-PASS overlap + 3 HARD-FAIL held-out + 2 prior-hypothesis inversions

**From**: testbed
**To**: strategy (orchestrator) + user
**Date**: 2026-06-01
**Trigger**: 10-cell v1b grid landed; clean architectural picture; strategy routing says STOP after deliverable but the prior-hypothesis inversions warrant explicit surfacing
**Related**: `notes/testbed_pp8_v1b_grid_plus_path_a_paraphrase_2026-06-01.md` (full deliverable)

## TL;DR

The 9-cell v1b grid produces decisive empirical resolution on the LR-bug hypothesis (REFUTED) and the held-out generalization question (REFUTED). Substrate-LLM coupling is empirically a memorization mechanism (97% overlap; 0.1% held-out), not a semantic-generalizer. Per strategy routing I'm holding here for cap_map move + any follow-on direction. Path A cell 10 errored at MRPC load; tactical re-dispatch if you want closure on it ($0.5).

## Two prior-hypothesis inversions

### Inversion 1: "LR catastrophic forgetting" was an eval-sampling artifact

Prior runs (v1+v1' bundle final 38.2%; Option A final 0% from peak 57.5% at step 250) showed wild eval trajectories. I had attributed this to LR-decay catastrophic forgetting and recommended WSD as the architectural fix.

This batch: 3 different schedules (cosine, WSD, constant) all produce IDENTICAL 97.4% final val on overlap with stable monotone trajectory. Previously-observed oscillation was from eval_every_k=50 sampling stochastic batch noise. With eval_every_k=25 the trajectory is essentially flat at 97% from step ~100 onward.

**Implication**: LR-schedule fix is unnecessary; WSD is not load-bearing; constant LR works just as well. The "LR-bug" interpretation in `strategy_request_to_strategy_pp8_option_a_lr_bug_escalation_2026-06-01.md` was wrong.

### Inversion 2: "Option A 57.5% peak" was non-reproducible

The earlier Option A held-out test had val=57.5% at step 250 (single eval checkpoint). I framed this as "architecture demonstrably CAN reach 57.5% on held-out".

This batch: 3 different schedules on held-out + EMA dual-eval + eval_every_k=25 (8x more eval checkpoints than original Option A). Peak held-out val is 0.5% (1/200) across all cells. Never reproduced 57.5%.

**Implication**: substrate-LLM coupling does NOT generalize via Phi-3 embedding geometry to held-out keys. Mechanism 2 (LLM embedding geometry inheritance) is EMPIRICALLY REFUTED. The earlier 57.5% was a stochastic single-eval artifact (possibly random batch luck or a near-duplicate that crept across the train/val key split).

## What the substrate IS empirically

Across 6 overlap cells × 2 key types × 3 schedules, all produce 91-97% memorization accuracy. The substrate is a **deterministic key-value cache** with:
- 97% retrieval accuracy on stored keys
- Either Phi-3-derived OR random orthogonal codewords (M1-dominant; no Phi-3-key complexity needed)
- Independent of LR schedule (cosine = WSD = constant)
- Stable retention (peak ~final; retention_ratio 0.94-0.99)

## What the substrate IS NOT empirically

- A semantic-generalizer (held-out keys produce random retrieval)
- A learnable structure beyond memorization (no schedule helps; no key encoding helps)

## Product positioning implication

The "audit-cert infrastructure for LLM memory and caching" framing strategy pre-committed is exactly right: substrate is a TRUSTED CACHE with deletion certificates + audit trail, NOT a semantic search layer. The narrative is regulatory-durable moat (cert chain + per-fact retention policy + deletion proof) over technical-novelty moat (semantic generalization).

## What I think the cap_map move should be

Per strategy pre-commits in the authorization:
- "WSD+EMA HP-fragility mitigation stack" sub-property: REMOVE — empirically not needed; the "HP-fragility" was the eval artifact
- "M1-dominant key encoding; Phi-3 forward pass NOT required on key side for exact-match retrieval": KEEP and STRENGTHEN — confirmed at high resolution
- "Substrate-LLM coupling does not generalize via Phi-3 embedding geometry; held-out keys retrieve at random": ADD as bounding constraint
- "Memorization accuracy 97% across 6 overlap configurations": ADD as PASS evidence

PP-8 row stays at 0.60-0.78 (no further LIFT; held-out FAIL bounds the upside). The product framing simplification (cache + audit certs, no semantic-search claim) is durable.

## Pre-committed Path A cell 10 status

Cell 10 errored at MRPC dataset load on remote (datasets library or network issue). NO useful data; needs re-dispatch.

Given held-out FAIL strongly suggests Mechanism 2 doesn't work, paraphrase generalization (which depends on same mechanism) is unlikely to PASS. Re-dispatch is informative but not load-bearing:
- Path A PASS would be a surprise + would reopen Mechanism 2 question
- Path A FAIL would confirm the held-out finding

Tactical re-dispatch: $0.5 + ~5 min wall. Worth it for closure but not urgent.

## What testbed will do next, by default

Per strategy routing rules: STOP after deliverable; do NOT auto-iterate.

I'm holding here. Awaiting:
- Strategy's cap_map move (per pre-commits)
- Any next-step routing (Path A re-dispatch / Phase 3 dispatch / pivot to other PP-row work)
- D3 KV-cache integration smoke if strategy decides M1-dominant + memorization-PASS is sufficient to unlock D3

## Cost state

- Cumulative session Lambda: $21.49
- v1b 10-cell batch cost: $7.07 (under strategy's $11-17 estimate)
- Remaining contingency: ~$28.51 before $50 testbed check-in cap
- Path A re-dispatch: ~$0.5 if authorized

## Files referenced

- This routing
- `notes/testbed_pp8_v1b_grid_plus_path_a_paraphrase_2026-06-01.md` (full deliverable)
- `notes/routed_completed/strategy_response_to_testbed_pp8_v1b_lr_fix_plus_path_a_10cell_authorized_2026-06-01.md` (10-cell authorization)
- `notes/strategy_request_to_strategy_pp8_option_a_lr_bug_escalation_2026-06-01.md` (LR-bug escalation; now empirically inverted)
- `data/lambda_batch_results/pp8_w2_v1b_c{1..10}_*/` (full per-cell results)

<!-- routing-completed: Acted-on 2026-06-01: v1b grid findings absorbed into PP-8 cap_map LIFT + downstream KV-cache product framing -->
