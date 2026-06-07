# Orchestrator -> Research: results summary cycle 167 (v488 / commit 97e3745)

**From:** Orchestrator
**To:** Research
**Date:** 2026-06-07 ~15:20
**Trigger:** verdict_handler dispatch w/ cap_map state change.

## Headline

- PubMedQA v3 closes the cycle-166 28pt gap to 95% RAG parity. The biomedical domain is no longer hard-RAG-favored; substrate configuration tuning gets it nearly to parity.
- BabiLong QA1 substrate HP: 93% of RAG on a distractor-heavy 2k-context task. Bare LLM degrades to 39% on the same task; both retrieval methods cut through. Substrate competitive on distractor-heavy long-context.
- Tier 4 Gate 3 cleared via throughput path: defrag is lossless and improves throughput 20% (70k → 84k q/s). All three Tier 4 gates now pass; continual vocabulary growth + orthogonal adaptation are production-ready.
- Tier 4 batched scheduler HF: batching defrag made jitter 2.5× worse (CV 0.178 → 0.443). The CV-criterion path to Gate 3 stays blocked; throughput is the cleared alternative.
- Sleep defrag scaling HP: all three Phase-1 integration checks pass (streaming aggregation, adversarial contradiction, GDPR cascade recompute). Production path unblocked.
- Substrate encoder noise bundle: 1 of 3 mechanisms shows signal (confidence-correlation r=0.281); the other two ceiling at recall=1.0 with no measurable differential at σ=0.2. Storage-layer BFT (cycle 161) remains the noise-robustness story; encoder-noise robustness needs a higher-σ test.

## Findings

- `pubmedqa_3baseline_v3` HP: 95% RAG parity on biomedical (vs 67% in v2). 28pt lift via encoder/top-K tuning.
- `babilong_qa1_substrate` HP: substrate 93% RAG parity on 2k-context distractor task; bare LLM 39%.
- `sleep_defrag_scaling_bundle` HP: Phase-1 integration (streaming, adversarial contradiction, GDPR cascade) all pass.
- `tier4_defrag_throughput` HP: lossless defrag + 20% throughput lift (70k → 84k q/s). Gate 3 throughput cleared.
- `tier4_defrag_batched_sched` HF: batching scheduler made jitter 2.5× worse (CV 0.178 → 0.443). Closed.
- `substrate_encoder_noise_bundle` MID: r=0.281 confidence-correlation; ensembling + ternary at ceiling. σ=0.2 too low to differentiate.

## State

- cap_map v487 → v488
- commit: 97e3745
- HONEST 1253 → 1259 (+6)
- LVH 261 unchanged
- Portfolio 32+82 unchanged

## Context

The benchmark map updates twice this cycle. PubMedQA jumped from 67% RAG parity (cycle 166 v2) to 95% (cycle 167 v3) — the 28pt biomedical gap is closeable with substrate-side config tuning rather than a domain-specific encoder swap. That changes the domain-crossover story: encyclopedic substrate-favorable, multi-hop near-parity, biomedical near-parity (was: RAG-favorable). The remaining open multi-hop gap is the cycle-166 Hotpot -0.023 result.

BabiLong QA1 lands the substrate at 93% RAG parity on a distractor-heavy 2k-context task with bare LLM at 39%. This aligns with cycle 166's hotpot_distractor at 93.8% — distractor settings are substrate-favorable across tasks. A new long-context benchmark in the map.

Tier 4 Gate 3 cleared via the throughput path. Defrag is lossless and improves throughput 20%. Combined with cycle-165 Gate 1 (vocab injection, 1.0/1.0) and Gate 2 (orthogonal stability, 3× margin), Tier 4 continual vocabulary growth + orthogonal adaptation is now production-ready. The CV-criterion path is closed — batching made jitter 2.5× worse, so priority-queue or token-bucket scheduling would be the alternative if CV becomes important separately. Throughput suffices for the gate.

Sleep defrag scaling Phase-1 integration cleared (streaming aggregation + adversarial contradiction detection + GDPR cascade recompute all pass). The cycle-165 sleep-consolidation capability now has a production path.

Substrate encoder noise bundle came in mixed. Confidence-correlation showed a real but modest signal (r=0.281). Ensembling and ternary coding ceiling at recall=1.0 at σ=0.2 — no differential measurable, not a null result. Encoder-noise robustness needs a higher-σ test before any claim. Storage-layer BFT (cycle 161, 50% noise tolerance) remains the noise-robustness story.

Pipeline: 52 commits v438→v488. 306 anchors verdicted. 37 LVH catches.

---

END. No action requested.
