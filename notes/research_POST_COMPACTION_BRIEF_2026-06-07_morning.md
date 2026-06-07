# Research Post-Compaction Brief -- 2026-06-07 morning

Read this first on context recovery.

## North star (locked yesterday evening)

The project goal is a functional system that empirically beats LLMs of comparable size on
chosen benchmarks. Privacy, audit, multi-hop reasoning, continual learning, and adversarial
robustness are the planned advantages. Storage efficiency is one of the planned strengths
but reality is 286 KB per fact today; engineering paths exist to reach 200-800 bytes per
fact in v3 (structured KBs) or 1-3 KB (mixed KBs). 5-7 weeks to v1 demo per the timeline.

## In-flight drills (dispatched, not yet returned)

Two drills running in background:

1. Privacy failure mechanism 3x drill. Asks why SRHT and DP noise both failed on production
   Llama encoder. Considers 8 alternative mechanisms (privacy-tuned whitening, rank
   randomization, cone-aware retrieval, DP at write time instead of read, encoder fine-tuning
   for privacy, negative-class injection, two-stage filter, homomorphic). Will return three
   cheap test paths if any look promising plus an honest assessment of whether the floor is
   fundamental on causal-LM encoders. North-star-critical. Agent dispatched roughly 10
   minutes before this brief was written.

2. Synthetic-vs-real prediction gap 2x drill. Research methodology. Asks why three drills
   in a row (sparse-KEY, SRHT, MiniLM-as-proxy) had predictions that real-data tests
   disproved. Wants warning signs we should check before authorizing engineering. Will
   return updated drill output template requiring theoretical-P x empirical-P split. Agent
   dispatched at same time as the privacy drill.

When these land, synthesize each in plain prose 10-15 lines (per the new feedback memory),
file any routing implications to Exp-Dev/Orchestrator.

## Exp-Dev empirical cells in flight or queued

Storage program: seven cells from this morning plus three Tier-A supplement cells. All apply
multi-dimensional acceptance criteria from my supplement note (audit + ZKL + K-hop +
adversarial + perf, not just retrieval). Each cell reports a safe operating regime, not
just pass/fail.

The seven original cells: sparse-W validation at production N=65536 (gates everything; 30
min GPU), 4-bit W quantization, lower-N substrate test, source vector PCA compression,
content-addressable keys, hybrid sparse-key dense-value, forgetting/pruning policy. The
three supplement cells: predicate/fact ratio audit on real KB sample (30 min CPU), retrieval
F1 vs N sweep at {4096,8192,16384,32768,65536}, exponential-energy capacity at N=4096.

Exp-Dev has been building cells in real time from the routing notes. Visible work: 4-bit
quantization cell, soft-Krum Byzantine cell (passed earlier as part of v1 distributed
reasoning), corroboration gossip damp cell, SRHT cells now cancelled, DP noise cells now
failed. Multiple SkyPilot safety scripts also in the tree.

Privacy probes queued by Exp-Dev: Llama eigenspectrum diagnostic (gives mechanism for why
SRHT/anisotropy behaves as it does on Llama).

When these cells return, synthesize each per the standing duties.

## Testbed CELL-3 and CELL-4

Testbed authorized to dispatch CELL-3 (Wikipedia distillation, 22M student feature-mimic on
left-padded cache) and CELL-4 (HP-12 V2 at 100K facts, production recipe). CELL-4 launch
gated on confirming multi-head H=2 setup before launch. Pre-compaction brief from Testbed
landed showing dispatch preparation. Watch for verdicts.

## Cycle progression today

Cycle 151 found the SRHT real-key gap (later determined to be attack-methodology mismatch),
K-hop noise opposite trends, sparse-KEY low-B only.

Cycle 152 composition wins (subscribe + as_of + GDPR + bitemporal all compose), K-hop K_max
= 54 at 32K classes, GDPR concurrent safety 0 leaks per 5000 trials.

Cycle 153 founded the causal reasoning cluster (PP-81 causal disambiguation precision
1.000 recall 0.973; PP-81a zero-crosstalk do() degradation 0.000; PP-82 counterfactual
replay 100% accuracy at 3.876 ms; rank-1 downdate confirmed algebraically equivalent to
Pearl's do() operator). Portfolio 32+80 -> 32+82.

Cycle 154 locked GDPR at EDPB Position 3 (HMAC keystore closes hash-relinkage gap), Chain
3 cross-shard K-hop confirmed at K=12 with 98.7% recovery, 50-line confidence filter works
at c_d=0.48 with T=0.5 (corrects earlier Cell A reading that filter was insufficient),
substrate answers SQL COUNT natively at 0.9% relative error, online concept extension lifts
jargon retrieval 0% to 100% via sparse-KEY vocab injection without encoder fine-tuning.
SRHT cancellation confirmed across 2 independent runs.

cap_map v475, HONEST count 1129, LVH 254, Portfolio 32+82.

## v1 plan (locked decisions)

Distributed reasoning ships with soft-Krum confidence-weighted bundling. The cheap
50-line filter at T=0.5 also works (cycle 154 confirmed) so we have two valid v1 paths;
soft-Krum is the planned implementation.

Privacy ships with qualified claim only: about 2x relative improvement over comparable RAG,
rate-limit at k<=5, full cryptographic audit trail. Absolute HIPAA-grade NOT defensible.
SRHT engineering (Authorization 3) cancelled. The 23x relative claim still needs an
explicit RAG arm to verify.

Sparse-KEY production usage: at B=1 single-shard storage only; not at intermediate hops
(LVH #248 Option B confirmed empirically by cycle 154's khop_sparse_bsweep test).

Storage stack: sparse-W validation at production N gates everything; 4-bit quant + lower-N
+ modern Hopfield n-sweep all running in parallel. Multi-dimensional acceptance criteria
apply. Realistic v1 landing: ~5 KB per fact (95% reduction from 286 KB current). v2 with
delta compression and N reduction: ~500 bytes - 1 KB per fact.

Bitemporal storage: 9-component build per Chain 2 Drill 5 FINAL spec (~3,800 lines, 6-7
weeks). HMAC keystore (cycle 154) plus erasure record append plus concurrency safety all
validated. Ready to start engineering when v1 distributed reasoning lands.

CELL-3 + CELL-4 Wikipedia and 100K-fact validation in flight at Testbed.

## Customer-facing claim posture

GDPR right-to-erasure: STRONG at EDPB Position 3 (strictest applicable standard).
Regulated-market deployment unlocked.

Bitemporal + as-of queries: STRONG (composition validated).

Reactive subscribe with cryptographic delivery: STRONG (cycle 150 + 152 production-ready).

Causal/counterfactual reasoning with real-time replay: STRONG (cycle 153 portfolio rows).

Multi-step verifiable reasoning K=12+: STRONG single-shard at K=20; cross-shard validated
at K=12 with 98.7%.

SQL aggregation: substrate answers COUNT natively at <1% error.

Privacy: QUALIFIED. About 2x relative vs RAG, rate-limit posture, full audit. Not HIPAA-
grade absolute.

Storage efficiency: NOT a current pitch. 286 KB per fact today vs LLM 4-40 bytes. After
v2 engineering, projection drops to 1-3 KB (mixed KBs) or 200-800 bytes (structured KBs)
which is in the user's accepted 10-100x band.

## Pending decisions for the user

None blocking right now. The Llama eigenspectrum diagnostic and DP-mechanism alternatives
are getting empirically tested via the cells already in flight. The RAG arm verification
for the 23x relative claim hasn't been run yet but isn't blocking v1.

## Active feedback rules

Plain language no hype: no emoji as emphasis, no superlatives, real-world consequences
first.

Concise cycle summaries: 10-15 lines prose, no tables/emoji headers, long-form goes in
research notes not chat replies.

North-star alignment: every drill and decision should advance the LLM-comparison demo
target. Substrate-internal exploration without integration context is drift.

Capability tracking SSOT: history.md tail + strategy_decisions tail + capability_scorecard.
Stale: substrate_capability_map.md (legacy). Do not create parallel inventories.

K-hop regimes are fragmented: do not conflate K=20 single-shard substrate reasoning with
K=12 cross-shard chain or K=10000+ chain_smoother readout. Each has its own validation.

Counterfactual is already enabled (rank-1 downdate as do() operator); not a gap.

## Cron and overnight loop

Cron d7ea1b05 runs every 15 minutes. Session-only, dies when VS Code closes. Standing
duties + safety constraints in overnight_loop_research_session.md memory entry.

## Memory entries (load on resume)

Top entries to read:
- north_star_functional_system_beats_LLMs.md
- overnight_loop_research_session.md
- capabilities_inventory_tracking.md (capability SSOT structure)
- feedback_plain_language_no_hype.md
- feedback_cycle_summaries_concise.md
- production_architecture_locked_2026-06-07.md
- phase2_5x_chains_gold_findings_2026-06-07.md

## What I am working on next when drills land

The privacy 3x and methodology 2x will land in 15-20 minutes from when this brief was
written. Synthesize each in plain prose 10-15 lines. Route any implications to Exp-Dev.

After those, start the benchmark suite definition work (Authorization 7 from the morning
list). Deliverable: concrete list of head-to-head benchmarks vs 1B LLM, why each plays to
substrate strengths, what scores would constitute a demonstrable win. Plain-language
document; not a marketing pitch.

Estimated 1-2 weeks for the benchmark suite work to complete. After that, integrated
pipeline build (substrate + Llama-1B for generation) is the week-3 engineering item.

## Heartbeat

data/heartbeat_research.json updated each cycle; data/cloud_paused_overnight.flag was the
overnight pause and may still be set; check and remove if morning operations should not
have it.

---

End of brief.
