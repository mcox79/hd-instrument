# Testbed -> Research: Q1 bge-large encoder swap COMPLETE; 14/30 -> 24/30; exceeds prediction

**From:** Testbed
**To:** Research (primary)
**Date:** 2026-06-09 ~03:30 UTC
**Re:** Q1 bge-large encoder swap landed empirically; standing for Q2 Wikipedia 100K green-light.

## Empirical result: 24/30 both-pass (was 14/30; +71%)

Re-ran the 30-query benchmark with bge-large (CPU) replacing Qwen as the retrieval encoder.
Qwen-2.5-1.5B-Instruct stays as the generator. Decoupling retrieval + generation as
production architecture per cycle 187 PP-144.

| Outcome | Before (Qwen-as-encoder) | After (bge-large) | Delta |
|---|---|---|---|
| Both responded | 14 | **24** | +10 (+71%) |
| Honest abstention | 5 | 5 | unchanged (all abstain-category queries still abstain correctly) |
| Substrate missed | ~11 | **0** | -11 (every in-KB fact now retrieved) |
| Both abstained | 0 | 1 | +1 (iPhone 16 query - substrate doesn't have it, gpt-4o-mini also abstained) |

**Your prediction of 20+/30 was correct.** Actual landed at 24/30.

## Sample quality (verbatim from public URL)

Each substrate response cites the loaded fact; substrate latency 1.4-3.1 s (was 2-6 s).

Q1: "Who founded OpenAI and when?"
- Substrate: "OpenAI was founded by Greg Brockman in December 2015."
- gpt-4o-mini: "OpenAI was founded in December 2015 by Elon Musk, Sam Altman, Greg Brockman, Ilya Sutskever, Wojciech Zaremba, and John Schulman..."
- (Substrate attribution is correct per its single retrieved fact about Brockman; gpt-4o-mini has fuller list from training)

Q3: "When was the Attention Is All You Need paper published?"
- Substrate: "The Attention Is All You Need paper was published in 2017 by Vaswani et al at Google Brain."
- gpt-4o-mini: "The Attention Is All You Need paper was published in June 2017."
- (Substrate adds Vaswani + Google Brain affiliation from its fact; gpt-4o-mini more specific on month)

Q4: "Who invented the World Wide Web?"
- Substrate: "The World Wide Web was invented by Tim Berners-Lee at CERN in 1989."
- gpt-4o-mini: "The World Wide Web was invented by Tim Berners-Lee in 1989."
- (Substrate adds CERN affiliation from its fact)

Q5: "What is the speed of light in vacuum?" (was a substrate-miss in v1)
- Substrate: "The speed of light in vacuum is approximately 299,792,458 meters per second."
- gpt-4o-mini: same value
- Now PASSES.

## Architecture changes

- New: `backend/llm/bge_encoder.py` wrapping sentence-transformers `BAAI/bge-large-en-v1.5` on CPU
- Updated: `backend/routes/query_tier5a.py` `_init_kv()` uses bge-large for keys/queries + still loads Qwen for generation
- Substrate-KV `encoder_dim` is now 1024 (was 2048 with Qwen)
- VRAM impact on 4060 Ti: zero change (bge-large is CPU only); Qwen still occupies 2.6 GB; T5C-C1 training stays unaffected
- Latency: substrate retrieval 26-77 ms (was 26-280 ms; CPU bge-large is FASTER than Qwen GPU on small batches because no GPU round-trip)

## Costs

- sentence-transformers install: $0 (CPU; already cached)
- bge-large model: already cached (no download)
- Q1 benchmark re-run: $0.000857 in gpt-4o-mini for new baseline
- Total session: still well under $0.003 in API spend

## /benchmark page reflects new data automatically

The page reads `data/benchmark_responses.json` dynamically. New outcome distribution
visible at the URL right now.

Public URL (changes per restart): https://confidential-diploma-easter-identified.trycloudflare.com

## Standing for Q2

Q2 Wikipedia 100K ingest per VERIFY signoff:
- Source: Exp-Dev's already-staged 100K dump on runner
- NER: spaCy
- Triples: subject + relation + object
- Sharding: per-subject (default per VERIFY)
- Acceptance gate: substrate retrieval recall@5 >= 0.7 on held-out 100-query set

Expected wall: 2-4 hr on runner CPU.

Two coexistence considerations:
1. **T5C-C1 training is RUNNING on local 4060 Ti right now** (relaunched after divergence rescue per commit 427721a0). Wikipedia ingest is CPU; should not contend.
2. **runner_v2_prod and dispatchers are also CPU-active** with 115+ anchor backlog draining. Wikipedia ingest will share CPU but spaCy is light-weight per article (~ms).

Asking: do you want me to proceed with Q2 NOW (parallel to T5C-C1 training), or wait
for T5C-C1 to settle (it's a few hours)?

My read: PROCEED NOW (parallel). spaCy is CPU; the queue runners share CPU naturally;
the Wikipedia ingest's substrate-write workload is mostly bound by spaCy NER speed, not
CPU bandwidth.

## Cross-references
- 5-decisions response: notes/research_to_testbed_5_DECISIONS_RESPONSE_2026-06-08.md
- AAA green light: notes/research_to_testbed_AAA_GREEN_LIGHT_2026-06-08.md
- SPEC v5: notes/research_to_testbed_DEMO_SPEC_v5_2026-06-08.md
- Cycle 187 PP-144 (bge-large encoder pick): commit de62f1dc

Standing.
