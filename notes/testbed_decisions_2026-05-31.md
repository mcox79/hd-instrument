# Testbed decisions 2026-05-31

Session-end handoff so the next testbed session resumes cleanly.

## Headline state

- **Tier 1a (dashboard expansion)**: COMPLETE — 7/7 sub-items, 4 commits
- **Tier 1b (Lambda cloud infrastructure)**: COMPLETE — V1 reproducer canary
  PIPELINE_HARD_PASS at $0.14, 39/39 cells, cert_all_valid=True. Cloud
  pipeline validated end-to-end.
- **Tier 2a (Pattern B capability validation)**: COMPLETE — 5/5 capability
  tests pass on substrate-backed service.
- **Tier 2b prep (LLM comparison harness)**: COMPLETE — 5/5 mock LLM
  wiring tests pass. Awaiting Anthropic API key (user confirmed available;
  surface when V1 gate cleared — which it now has).
- **Cumulative Lambda session spend**: ~$0.69-2.00 (latest experiment in
  flight at time of writing; check
  `data/lambda_exp_*_report_*.json` for actuals after completion).
- **Account state**: $0/hr active between runs; verified after every
  experiment with manual cleanup checks.

## Active work AT SESSION END (UPDATED 2026-05-31 post-compaction)

### Lambda batch 1/3 RESULT: blocked at import (not a substrate failure)

- Background task `b1pb01eap` (anchor `path_d_24n_32n_envelope_v1_n4096`)
  completed with launch_experiment exit 0 but the experiment never ran.
  Import-time `FileNotFoundError: experiments/exp_t1_beta_sweep_v1_n4096.py`
  from `_metric_battery._instrumentation_selftest()`. File exists in local
  tree but is UNTRACKED in git so it never made it onto the cloud clone.
- Wall 5.1 min, cost $0.11 (boot + bootstrap; experiment never ran).
- Cleanup verified: 0 active instances, no leak flags.
- Lambda batch 2/3 (`modern_hopfield_cpu_extended_v9_n16384`) and 3/3
  (`adversarial_codebook_collision_defense_probe_v1_n4096`) NOT launched
  — same `_metric_battery` import path, same bug expected.
- Routing filed for orchestrator:
  `notes/strategy_request_to_strategy_metric_battery_selftest_blocks_cloud_dispatch_2026-05-31.md`
  Fix options: (1) commit the missing file, or (2) make selftest
  skip-gracefully. Re-launch batch 1/3 after orchestrator merges fix.

### Substrate-LLM Week 0 Missing 7 #1 (substrate_latency) — CPU only

- `testbed/llm_integration/substrate_latency.py` shipped + ran on local CPU.
- Results (`data/testbed_missing7/substrate_latency_cpu.json`):
  - `store @ N=4096`: mean 28ms / p99 32ms
  - `store @ N=8192`: errored (Kerdock codebook requires even log2(N);
    log2(8192)=13 odd). Easy fix: pass a different codebook for N=8192
    or skip N=8192 store measurement on CPU.
  - `path_d depth=1 @ N=4096 K=500`: mean 99.5ms / p99 131ms
  - `path_d depth=5 @ N=4096 K=500`: mean 431ms / p99 794ms
  - Substrate-only verdict on CPU: **FAIL** vs 150ms budget (5x over).
- **GPU run still required** for the real Missing 7 #1 deliverable. The
  updated handoff stipulates GPU=marsh@home with NO cloud spend
  authorized. GPU access path not yet confirmed this session — surface
  to user before any cloud-runner activation.

### Substrate-LLM Week 0 Missing 7 #2 (bridge_mlp_scaffold) — CPU only

- `testbed/llm_integration/bridge_mlp_scaffold.py` shipped + ran on local CPU.
- Architecture per handoff sec WEEK 0 MISSING 7 measurement (2):
  ForwardBridge R^4096 -> Linear(2048) -> GELU -> Linear(3072);
  ReverseBridge R^3072 -> Linear(2048) -> GELU -> Linear(4096).
  Bidirectional total 29.37M params (handoff target ~27M).
- Results (`data/testbed_missing7/bridge_mlp_latency_cpu.json`):
  - `forward_R4096_to_R3072 B=1`: mean 5.5ms / p99 7.5ms
  - `forward_R4096_to_R3072 B=8`: mean 6.8ms / p99 8.3ms
  - `reverse_R3072_to_R4096 B=1`: mean 5.4ms / p99 7.7ms
  - `reverse_R3072_to_R4096 B=8`: mean 6.8ms / p99 9.6ms
  - **Round-trip p99 (B=1): 15.2ms**
  - Bridge-only verdict on CPU: MIDDLE (fits but cuts substrate budget).
- GPU expected to be substantially faster for these dense matmuls.

### Combined CPU verdict (Missing 7 #1 + #2)

- Substrate Path D depth=5 p99 (431ms mean / 794ms p99) + bridge round-trip
  p99 (15.2ms) = ~810ms p99 on CPU.
- vs 150ms FAIL threshold: **FAIL on CPU by ~5x**.
- Substrate is the dominant cost (>98%); bridge cost is negligible.
- This is consistent with the handoff prediction that GPU is mandatory.

### GPU runs landed (RTX 4060 Ti 8GB on marsh@home; 2026-05-31T14:15 ET)

GPU access granted by orchestrator
(`notes/testbed_handoff_gpu_access_granted_2026-05-31.md`); SSH + concurrency
protocol followed; V2 24h sustained_workload ran concurrently with no
disruption (5637 MiB free / util 1% pre-and-post each run).

Substrate latency on CUDA (`data/testbed_missing7/substrate_latency_cuda.json`):
- `store @ N=4096`: mean 1.691ms / p99 1.888ms (~16x faster than CPU)
- `store @ N=8192`: errored (Kerdock log2 bug, unchanged)
- `path_d depth=1 @ N=4096 K=500`: mean 6.08ms / p99 7.84ms (~16x)
- `path_d depth=5 @ N=4096 K=500`: mean 12.50ms / **p99 19.78ms** (~40x)
- Substrate-only verdict on CUDA: **PASS** with 30.2ms headroom for bridge

Bridge MLP latency on CUDA (`data/testbed_missing7/bridge_mlp_latency_cuda.json`):
- `forward R^4096 -> R^3072 B=1`: mean 0.20ms / p99 0.27ms (~25x)
- `forward B=8`: mean 0.30ms / p99 0.38ms
- `reverse R^3072 -> R^4096 B=1`: mean 0.18ms / p99 0.32ms (~25x)
- `reverse B=8`: mean 0.29ms / p99 0.36ms
- **Round-trip p99 (B=1): 0.59ms** (~25x)
- Bridge-only verdict on CUDA: **PASS** (negligible vs budget)

### Combined GPU verdict (Missing 7 #1 + #2 partial)

- Substrate Path D depth=5 p99 (19.78ms) + bridge round-trip p99 (0.59ms)
  = **20.37ms p99 on GPU**
- vs 50ms PASS threshold: **PASS by 29.6ms** (well inside budget)
- Phi-3-mini-4bit per-token forward must fit in <29.6ms p99 to keep
  Missing 7 #4 verdict at PASS. Published Phi-3-mini-4bit on 4060-class
  GPUs is ~15-40ms/token at seq_len=512; likely PASS but Missing 7 #3
  measurement is decisive.
- Substrate-side latency budget question is RESOLVED. Architecture viable.

### Missing 7 #3 + #4 scripts authored and on remote

- `testbed/llm_integration/phi3_token_latency.py` (Missing 7 #3)
  Loads `microsoft/Phi-3-mini-4k-instruct` at 4-bit NF4 double-quant +
  bf16 compute via BitsAndBytesConfig. Measures per-token decode wall
  at seq_len in {128, 512, 2048}; 100 generations per seq_len
  (5 seeds x 20 reps); reports mean + p99 plus prefill wall.
- `testbed/llm_integration/phi3_integrated_latency.py` (Missing 7 #4)
  Composes the full integrated pipeline:
  Phi-3 prefill -> last hidden state R^3072 -> ReverseBridge ->
  sign() bipolar -> Path D depth=5 K=500 N=4096 -> codeword R^4096 ->
  ForwardBridge -> prefix embed R^3072 -> Phi-3 decode 1 token with
  prefix injected via inputs_embeds + past_key_values. Measures total
  wall per integrated query with per-component breakdown
  (reverse_bridge / substrate_path_d / forward_bridge / phi3_decode_1tok).
  Bridges Xavier-init (untrained); substrate W populated; both seeded.
- Both scripts SCPd to marsh@home, AST-clean.
- Remote venv prereqs: installed transformers 5.9.0 + bitsandbytes 0.49.2
  + accelerate 1.13.0.

### Concurrency state — waiting for V2 drain

- V2 24h sustained_workload still on GPU until ~2026-05-31T21:11 ET.
  Phi-3-mini-4bit model load is ~3.8 GB; can't risk pushing V2 to OOM.
  Concurrency protocol mandates wait per
  `notes/testbed_handoff_gpu_access_granted_2026-05-31.md` sec
  "What requires waiting for V2 to finish".
- Both Phi-3 scripts will fire as soon as VRAM drains; first run also
  pulls Phi-3-mini from HuggingFace (~3.8 GB on first instantiation;
  ~5-10 min over typical home connection).

### Still pending for Week 0 (per updated handoff)

- Missing 7 #1 fix: N=8192 store measurement (Kerdock even-log2 constraint;
  cosmetic — not blocking the verdict given Missing 7 #1 PASS at N=4096)
- Missing 7 #3 + #4 GPU runs (waiting for V2 drain at ~21:11 ET)
- Deliverable: `notes/testbed_missing7_llm_integration_latency_v1_2026-05-31.md`
  with PASS/MIDDLE/FAIL verdict combining substrate + bridge + LLM + integrated
  (assembled after #3 + #4 land)

### Lambda batch ready to relaunch (awaiting user auth)

- Orchestrator commit 7959353 on origin/main fixes the metric_battery
  selftest dependency. `experiments/exp_t1_beta_sweep_v1_n4096.py` is
  now tracked in git; Lambda's bootstrap `git clone` will pull it.
- Same 3 anchors as before. Expected ~$1.45 total
  (path_d_24n_32n_envelope $0.65 + modern_hopfield_v9 $0.50 +
  adversarial_defense $0.30). Cumulative session spend would land ~$2.25.
- Awaiting explicit user authorization to relaunch.

## Cumulative Lambda session spend

~$0.80 ($0.69 canary chain + $0.11 batch 1/3 import-blocked). Within
budget; no leaks; no GPU spend.

## Three Lambda safety layers shipped this session

1. **Terminate retry-with-backoff + leak flag** (`tools/cloud/launch_v1_canary.py`,
   `tools/cloud/bootstrap_and_terminate.py`, `tools/cloud/launch_experiment.py`):
   6 attempts with exponential backoff, sticky flag file if all fail
2. **Always-verbose remote dispatch** (`feedback_always_verbose_remote_dispatch`
   memory): `set -ex` + `python -u` + `stdbuf -oL` + `tee` to remote log +
   SCP back regardless of exit code
3. **Pre-launch snapshot + 5xx retry + orphan reconcile**
   (`feedback_cloud_launch_snapshot_reconcile` memory): snapshot active
   instances pre-call, retry transient 5xx, reconcile post-call against
   the snapshot so silent orphans get terminated

## Open engineering item: generic progress wrapper

`launch_v1_canary.py` has live progress tracking (ProgressPoller thread +
`v1_progress_wrapper.py` cell-line parser). The generic
`launch_experiment.py` does NOT yet. For Path D 24N-32N + Modern Hopfield
v9 + adversarial defense probes, each prints per-cell completion lines in
similar shape. A generic wrapper would take ~30 min to write — pattern:

  - Accept a regex for cell completion + a total-cells count
  - Reuse `hdlab_service/progress_emitter.py` (already shipped, generic)
  - launch_experiment.py spawns the same ProgressPoller thread

Filing this as a deliberate gap. Ship next session once the user OKs.

## Cap_map state (read-only for testbed)

Last bumped by orchestrator at v290. Path D sub-row is at 0.85-0.95; the
in-flight experiment 1/3 may LIFT the upper bound on completion. Modern
Hopfield NEW row at 0.65-0.80 conservative; cross-codebook + M>N runs in
the 3-pack would inform LIFT. Adversarial defense probes inform two
deployment-blocker annotations.

## Filed memories this session

- `feedback_always_verbose_remote_dispatch` — every SSH-dispatched
  experiment MUST use set -ex + python -u + stdbuf -oL + tee + SCP-back
- `feedback_cloud_launch_snapshot_reconcile` — snapshot before
  state-changing cloud API calls; reconcile after; reply is hint not truth
- `project_anthropic_api_key_available` — user has Anthropic key ready
  for Tier 2b; surface when V1 gate clears (it now has)
