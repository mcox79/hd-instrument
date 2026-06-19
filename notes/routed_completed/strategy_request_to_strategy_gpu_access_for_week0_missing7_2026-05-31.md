# Routing: orchestrator — GPU access (or remote dispatch) for Week 0 Missing 7

**From**: testbed session
**To**: orchestrator (strategy)
**Date**: 2026-05-31
**Type**: resource-access + experiment-dispatch request
**Severity**: blocks Week 0 Missing 7 #1 + #2 + #3 + #4 (i.e., all 4 measurements)

## Why orchestrator (not testbed) is being asked

Per `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
sec DECISIONS RESOLVED (a): "GPU = LOCAL REMOTE DESKTOP (marsh@home or
equivalent) ... NO cloud spend authorized; if a hardware blocker
requires cloud, escalate to orchestrator + user before any cloud-runner
activation."

Testbed has finished what it can do on local CPU. To deliver the Week 0
Missing 7 PASS/MIDDLE/FAIL verdict, testbed needs either:

- **(Option A) SSH/credential access to marsh@home** so testbed runs the
  scripts itself (preferred — fewer round-trips), OR
- **(Option B) Orchestrator dispatches the runs on marsh@home** and
  returns the JSON outputs to testbed for verdict assembly, OR
- **(Option C) User dispatches them manually** and pastes results.

Testbed has no preference among A/B/C; whichever has lowest user friction.

## CPU baselines testbed already shipped (current turn)

- `testbed/llm_integration/substrate_latency.py`
  - CPU result: Path D depth=5 N=4096 K=500 = 431ms mean / **794ms p99**
  - FAIL on CPU by 5x against 150ms budget; expected — substrate
    matmul-heavy ops benefit hugely from GPU
- `testbed/llm_integration/bridge_mlp_scaffold.py`
  - CPU result: round-trip p99 at B=1 = **15.2ms** (29.37M params total)
  - MIDDLE on CPU; expected sub-ms on GPU

Combined CPU verdict: ~810ms p99 = FAIL by 5x. Confirms handoff prediction
that GPU is mandatory.

## What testbed needs run on the GPU

### Run #1 — substrate_latency.py on GPU (Missing 7 #1)

```bash
cd hd-instrument
python -m testbed.llm_integration.substrate_latency --device cuda
```

Writes `data/testbed_missing7/substrate_latency_cuda.json` with
store/path_d_depth1/path_d_depth5 latencies at 5 seeds. Wall: ~2-3 min.
Dependencies: hd-instrument repo + torch + the standard substrate
`experiments._multi_hop_mechanisms.build_shared` + `path_d_run`.

**Known limitation**: N=8192 store measurement errors (Kerdock codebook
requires even log2(N); log2(8192)=13 odd). Easy fix testbed can ship
later; not blocking.

### Run #2 — bridge_mlp_scaffold.py on GPU (Missing 7 #2)

```bash
cd hd-instrument
python -m testbed.llm_integration.bridge_mlp_scaffold --device cuda
```

Writes `data/testbed_missing7/bridge_mlp_latency_cuda.json` with
forward/reverse latencies at B=1 and B=8, 5 seeds. Wall: ~30 sec.
Dependencies: hd-instrument repo + torch.

### Run #3 — Phi-3-mini-4bit token-gen latency (Missing 7 #3) — script NOT YET WRITTEN

Testbed will ship `testbed/llm_integration/phi3_token_latency.py` next
turn (or after orchestrator confirms the GPU has Phi-3-mini available).
The script will measure per-token generation latency at seq_len in
{128, 512, 2048} over 100 generations, mean + p99.

**Hardware requirements**:
- CUDA GPU with >=4GB VRAM for Phi-3-mini-3.8B 4-bit, OR >=8GB VRAM for
  fp16 (handoff dec (a) says if >8GB use fp16; if 8GB use 4bit)
- `transformers >= 4.40` + `bitsandbytes >= 0.43` + `accelerate >= 0.30`
- HuggingFace download access (Phi-3-mini-3.8B is MIT-licensed,
  publicly available, no gating)
- ~7.5GB disk for the model weights

**Testbed needs from orchestrator before writing this script**: confirmation
that Phi-3-mini is already on the GPU box OR confirmation that the GPU
box has internet to download it on first run.

### Run #4 — end-to-end integrated forward-pass (Missing 7 #4) — script NOT YET WRITTEN

Composes #1 + #2 + #3: Phi-3 emits query head -> ReverseBridge ->
substrate Path D depth=5 -> ForwardBridge -> Phi-3 prefix token.
Measures total wall per integrated query. Wall: ~1 min after #3 lands.

## Specifically requesting from orchestrator

1. **Hardware confirmation**: is marsh@home actually online and reachable
   right now? (per testbed handoff and `project_anthropic_api_key_available`
   memory note, the GPU is the intended path but availability not
   verified this session)
2. **Access path**: SSH + repo-clone instructions, OR a dispatch
   mechanism orchestrator owns (e.g., similar to Lambda's
   launch_experiment.py but pointed at home GPU), OR confirm user will
   dispatch manually.
3. **GPU specs**: `nvidia-smi` output once accessible so testbed knows
   whether Phi-3-mini-4bit (8GB) or Phi-3-mini-fp16 (24GB) is the
   correct configuration. Affects #3 + #4 script defaults.
4. **HF model availability**: is Phi-3-mini already downloaded on the GPU
   box, or does first-run need internet + ~7.5GB pull?

## What testbed will do once unblocked

Per handoff sec WEEK 0 MISSING 7 deliverable:

```
notes/testbed_missing7_llm_integration_latency_v1_2026-05-31.md
```

with the 4 measurements (#1 + #2 + #3 + #4), each at mean + p99 across
5 seeds, plus PASS/MIDDLE/FAIL classification:
- PASS: substrate Path D depth=5 + bridge round-trip p99 < 50ms
- MIDDLE: in [50ms, 150ms]
- FAIL: > 150ms p99 (escalate to research before Week 1)

Plus status_log entry importance=HIGH with the verdict.

## Files this routing references

- `notes/testbed_handoff_substrate_llm_deep_integration_2026-05-31.md`
  (the LLM integration handoff sec DECISIONS RESOLVED (a))
- `testbed/llm_integration/substrate_latency.py`
  (Missing 7 #1 script, CPU-tested)
- `testbed/llm_integration/bridge_mlp_scaffold.py`
  (Missing 7 #2 script, CPU-tested)
- `data/testbed_missing7/substrate_latency_cpu.json`
  (CPU baseline result, file present)
- `data/testbed_missing7/bridge_mlp_latency_cpu.json`
  (CPU baseline result, file present)
- `notes/testbed_decisions_2026-05-31.md`
  (full session state including this routing pointer)

## No urgency tag

This is gating but not time-critical. Week 0 budget is ~1 week wall.
Testbed has CPU baselines in hand; can wait for orchestrator + user to
align on the GPU access path.
