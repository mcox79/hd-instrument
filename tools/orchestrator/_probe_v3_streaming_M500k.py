"""One-off targeted probe: v3 streaming M=500k ARM_REPL only.

Purpose: verify GPU util scales when CPU-build is amortized over larger chunk-matmul
volume (M=100k smoke showed 14% peak util; expected to rise significantly at M=500k
because CPU-build is one-time-per-arm but chunk-matmul volume scales linearly with M).

Runs ONE ARM_REPL at M=500k N=8192 V=256 seed=7 with INT8 keys (matches full-run REPL config).
Emits streaming_peak_mb / gpu_mem_peak_mb / wall_s / recall_cosine_mean to stdout.
"""
from __future__ import annotations
import sys, time, json
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent.parent
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from experiments._substrate_cortex_hippo_dense_commercial_M_100k_1M_gpu_v3_chunked_upload_core import (
    N_CORTEX_FULL, V_DIM_FULL, N_QUERIES_SMOKE, ATTN_CHUNK_FULL, UPLOAD_BATCH_FULL,
    run_arm, run_one_M,
)

PROBE_M = 500_000
PROBE_SEED = 7
OUT_DIR = REPO / "data" / "_probe_v3_streaming_M500k"
OUT_DIR.mkdir(parents=True, exist_ok=True)

print(f"[probe] M={PROBE_M} N={N_CORTEX_FULL} V={V_DIM_FULL} chunk={ATTN_CHUNK_FULL} upload_batch={UPLOAD_BATCH_FULL} seed={PROBE_SEED} n_queries={N_QUERIES_SMOKE}", flush=True)
print(f"[probe] running ARM_REPL only (int8_keys=True, CPU-resident streamed)", flush=True)

t0 = time.time()
arms = run_one_M(
    seed=PROBE_SEED, M=PROBE_M, N=N_CORTEX_FULL, V=V_DIM_FULL,
    n_queries=N_QUERIES_SMOKE, chunk_size=ATTN_CHUNK_FULL,
    out_dir=OUT_DIR, use_torch=True, use_int8_keys=True,
    upload_batch=UPLOAD_BATCH_FULL,
)
elapsed = time.time() - t0

print(f"[probe] elapsed={elapsed:.2f}s n_arms={len(arms)}", flush=True)
# Find ARM_REPL row
repl_arms = [a for a in arms if a.get("arm_name") == "ARM_REPL"]
for a in repl_arms:
    print(f"[probe] ARM_REPL streaming_peak_mb={a.get('estimated_streaming_peak_mb'):.2f} gpu_mem_peak_mb={a.get('gpu_mem_peak_mb'):.2f} recall={a.get('recall_cosine_mean'):.4f} wall_s={a.get('wall_s'):.2f} strategy={a.get('upload_strategy')}", flush=True)

# Persist full result
(OUT_DIR / "probe_result.json").write_text(json.dumps({"M": PROBE_M, "seed": PROBE_SEED, "arms": arms, "elapsed_s": elapsed}, indent=2))
print(f"[probe] wrote {OUT_DIR / 'probe_result.json'}", flush=True)
