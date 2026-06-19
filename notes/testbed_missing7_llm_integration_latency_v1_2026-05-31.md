# Week 0 Missing 7 LLM-integration latency budget: v1 deliverable

**From**: testbed session
**Date**: 2026-05-31
**Closes**: `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
sec WEEK 0 MISSING 7 -- LLM INTEGRATION LATENCY BUDGET CHARACTERIZATION
**Hardware**: marsh@home RTX 4060 Ti 8GB (P_def 0.25-0.30 path per
DECISIONS RESOLVED (a))
**Source data**: `data/testbed_missing7/*.json` (4 JSON files)

## TL;DR

**Verdict: FAIL** (integrated query p99 = 218ms; > 150ms FAIL threshold).

**The bottleneck is Phi-3-mini-4bit decode, NOT substrate.** Substrate
Path D depth=5 and bridge MLP both PASS by wide margins on the 4060 Ti.
Phi-3-mini-4bit per-token decode at 4-bit NF4 + bf16 compute is 5x the
combined substrate+bridge cost.

Per handoff: FAIL "escalate to research before Week 1. Substrate-side
throughput is the bottleneck; needs research drill on async-batched or
precomputed-prefix variants BEFORE committing to Week 1 build."

**However**: substrate is NOT the bottleneck. The handoff's escalation
recipe assumes substrate-side rework. Actual findings flip the
recommendation: the substrate budget assumption was correct; LLM choice
is what fails. Discussion below distinguishes which architectural
options actually help and which would chase the wrong target.

## The 4 measurements

### Missing 7 #1 -- substrate baseline latency on CUDA

`testbed/llm_integration/substrate_latency.py` -> `data/testbed_missing7/substrate_latency_cuda.json`

| Measurement | mean (ms) | p99 (ms) | Verdict |
|---|---|---|---|
| store @ N=4096 | 1.69 | 1.89 | PASS |
| store @ N=8192 | errored | errored | (cosmetic; Kerdock log2 bug) |
| path_d depth=1, N=4096, K=500 | 6.08 | 7.84 | PASS |
| **path_d depth=5, N=4096, K=500** | **12.50** | **19.78** | **PASS** |

Substrate-only verdict per script: PASS with 30.2ms headroom under
50ms target (substrate alone). Production op (depth=5) safely below
budget; cells are matmul-dominant and uniform.

### Missing 7 #2 -- bridge MLP latency on CUDA

`testbed/llm_integration/bridge_mlp_scaffold.py` -> `data/testbed_missing7/bridge_mlp_latency_cuda.json`

29.37M-param bidirectional MLP (Forward R^4096 -> R^2048 -> R^3072;
Reverse R^3072 -> R^2048 -> R^4096; GELU; Xavier-init / untrained).

| Direction / batch | mean (ms) | p99 (ms) |
|---|---|---|
| forward B=1 | 0.20 | 0.27 |
| forward B=8 | 0.30 | 0.38 |
| reverse B=1 | 0.18 | 0.32 |
| reverse B=8 | 0.29 | 0.36 |
| **Round-trip B=1** | **0.38** | **0.59** | PASS |

Bridge-only verdict per script: PASS (negligible vs budget).

### Missing 7 #3 -- Phi-3-mini-4bit per-token decode latency

`testbed/llm_integration/phi3_token_latency.py` -> `data/testbed_missing7/phi3_token_latency_cuda.json`

Phi-3-mini-3.8B at NF4 4-bit + double-quant + bf16 compute, attention
implementation = "eager". Model loaded in 13.7s. seq_len rotated across
{128, 512, 2048} x 5 seeds x 20 reps per seed (100 generations per
seq_len). Prefill timed separately as a one-time-per-query cost (not
in per-token budget).

| seq_len | per-token mean (ms) | per-token p99 (ms) | prefill mean (ms) |
|---|---|---|---|
| 128 | 80.9 | 121.4 | 295.8 |
| **512** | **98.3** | **131.3** | **434.9** |
| 2048 | 156.3 | 183.8 | 4041.1 |

Per-token at production-reference seq_len=512 = 131ms p99. Phi-3-mini
alone occupies 4-5x the substrate's entire budget at seq_len=512.

Note: this script's printed "FAIL" verdict at the bottom of its run
output compared Phi-3 alone against substrate's 29ms remaining budget
(50 - 21). That comparison is conceptually wrong for the handoff PASS
criterion (which is on the integrated query, not per-component
balances). The actual decisive measurement is #4.

### Missing 7 #4 -- end-to-end integrated forward-pass

`testbed/llm_integration/phi3_integrated_latency.py` -> `data/testbed_missing7/phi3_integrated_latency_cuda.json`

Pipeline: Phi-3 prefill (timed separately, one-time per query) ->
extract hidden state at last position -> ReverseBridge R^3072 ->
R^4096 -> sign-binarize to bipolar -> Path D depth=5 retrieve at
N=4096 K_paths=500 -> ForwardBridge R^4096 -> R^3072 prefix embed ->
Phi-3 decode 1 token with prefix injected via inputs_embeds +
past_key_values.

5 seeds x 20 reps per seed x 2 seq_lens (128, 512). Bridges
random-init Xavier (untrained). Substrate W populated at M=4096.

**Total wall per integrated query:**

| seq_len | total mean (ms) | **total p99 (ms)** |
|---|---|---|
| 128 | 158.5 | 218.4 |
| **512** | **178.2** | **217.7** |

**Per-component breakdown at seq_len=512:**

| Component | mean (ms) | p99 (ms) | Share of total |
|---|---|---|---|
| reverse_bridge | 0.80 | 1.63 | 0.7% |
| substrate_path_d | 17.07 | 27.47 | 12.6% |
| forward_bridge | 0.65 | 1.05 | 0.5% |
| **phi3_decode_1tok** | **159.33** | **198.47** | **91.2%** |

(Note: per-cell-prefill is 435ms at seq_len=512; not in per-query
budget per handoff design -- prefill is amortized across many
integrated queries on the same conversation context.)

## Pre-registered band classification

Handoff sec WEEK 0 MISSING 7 decision criteria:
- PASS: total integrated p99 < 50ms (soft-prompt prefix-injection viable)
- MIDDLE: in [50, 150]ms (design works with deployment caveats)
- FAIL: > 150ms p99 (escalate to research before Week 1)

**Total p99 at seq_len=512 = 217.7ms**

**Result: FAIL** (217.7ms > 150ms threshold by 45%).

## Where the budget went

substrate + bridge = 30.2ms = 13.9% of total
phi3_decode = 198.5ms = 91.2% of total

The substrate component is well inside the per-query budget the
handoff anticipated. The substrate's contribution at production scale
is well-characterized: matmul-dominant, K_paths=500 indexable, no
sharp-cliff degradation across the cells tested.

Phi-3-mini-4bit on RTX 4060 Ti 8GB is the bottleneck. At 198ms p99 per
decode step, even a hypothetical substrate at 0ms cost would not bring
the integrated query below the 50ms PASS bar. The substrate budget the
handoff anticipated is correct in shape; the LLM-side budget
assumption (10-50ms per token on small LMs) was over-optimistic for
Phi-3-mini-4bit + 4060 Ti.

## Recommendation: escalation flavor matters

Handoff anticipates FAIL means "substrate-side throughput needs
async-batched or precomputed-prefix research drill before Week 1
build." Findings here REJECT that diagnosis. Substrate is fine.

**Actual options for closing the FAIL** (in approximate cost order):

1. **Larger / different GPU** (LLM-stage fix). Phi-3-mini-4bit on an
   RTX 3090 24GB (no 4-bit quantization overhead since model fits in
   fp16; 5-10x faster compute) or H100 (substantially faster) would
   bring per-token toward 20-50ms. Single-line config change; no
   architecture redesign. Cloud-spend gate (orchestrator + user).
2. **Different base LM** (LLM-stage fix). TinyLlama-1.1B or
   Phi-2-2.7B at fp16 on 8GB would land ~30-60ms per token. Lower
   absolute quality than Phi-3-mini; needs re-evaluation of the
   "1-3B is the right scale" research-side decision. Substrate-side
   design unchanged.
3. **Speculative decoding / quantization swap** (LLM-stage fix).
   Some 4-bit decoders run faster than others on consumer GPUs; the
   bnb NF4 + bf16 compute path may not be optimal for 4060 Ti. Could
   try Phi-3-mini-4k-instruct-bnb-4bit pre-quantized variant or AWQ
   instead of bnb. Single-config change; ~1-day exploration.
4. **Cloud LLM API for inference** (replace local LLM entirely).
   Anthropic Claude Haiku at production scale runs at 50-150ms p99
   per token with much higher absolute quality. Substrate-bridge
   integration would need an API-call boundary instead of in-process
   prefix-injection; new architecture but reuses the already-built
   Tier 2b Anthropic LLM client (Phase 1 PASS at 100pct exact-match
   today; cumulative session API spend $0.44).
5. **Async-batched substrate retrieval** (substrate-stage fix --
   the handoff's escalation recipe). Would help amortize substrate
   cost across multiple LLM queries but DOES NOT help the LLM-stage
   bottleneck per-query. Not the right fix for the failure mode
   observed here. Recommend NOT pursuing unless substrate
   instrumentation shows different bottleneck shape at a different
   workload.

## What testbed believes after Week 0

The substrate-LLM bridge architecture in the handoff is sound in shape.
Substrate Path D depth=5 + bridge round-trip on the 4060 Ti is 30ms
p99 -- well inside any reasonable integration budget. The
"substrate-LLM deep integration" Tier 1 killer-feature claim is
intact at the substrate-side level.

The 217ms integrated p99 is an LLM-choice + hardware constraint, not
an architecture problem. Options (1)-(4) above all close the gap;
each has a different cost / quality / engineering profile.

## Status_log implication

Filing HIGH importance: substrate-side Week 0 PASS confirmed; LLM-side
FAIL surfaced with explicit redirect of the escalation recommendation
(do not pursue substrate-side async-batched fix; pursue LLM-stage
options). Research's next drill should ingest this finding and
re-evaluate Week 1 GO/NO-GO with the per-component breakdown rather
than the integrated-total alone.

## Pending technical items (cosmetic; do not affect verdict)

- N=8192 store measurement errored (Kerdock codebook requires even
  log2(N); log2(8192)=13 odd). Cosmetic; substrate verdict not affected
  by missing this single cell. Easy fix: alternate codebook for N=8192
  store cell only.
- `phi3_token_latency.py` script's printed FAIL verdict at end of run
  used substrate-budget-remaining rather than total integrated budget.
  Misleading label; numbers are correct. Easy fix: align that script's
  verdict band to the integrated-query band like #4 does.

## Files of interest

- This deliverable note
- `data/testbed_missing7/substrate_latency_cuda.json` (#1)
- `data/testbed_missing7/bridge_mlp_latency_cuda.json` (#2)
- `data/testbed_missing7/phi3_token_latency_cuda.json` (#3)
- `data/testbed_missing7/phi3_integrated_latency_cuda.json` (#4)
- `testbed/llm_integration/substrate_latency.py`
- `testbed/llm_integration/bridge_mlp_scaffold.py`
- `testbed/llm_integration/phi3_token_latency.py`
- `testbed/llm_integration/phi3_integrated_latency.py`
- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
  (source handoff)
- `notes/testbed_handoff_gpu_access_granted_2026-05-31.md` (GPU
  concurrency protocol; V2 state cache was stale per `notes/testbed_decisions_2026-05-31.md`
  late-day update; Phi-3 ran with ~5.6 GB free VRAM)
