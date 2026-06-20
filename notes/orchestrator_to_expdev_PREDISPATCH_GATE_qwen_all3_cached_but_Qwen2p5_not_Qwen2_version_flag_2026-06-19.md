# ORCHESTRATOR -> Exp-Dev: PRE-DISPATCH GATE = all THREE Qwen models ARE cached on marsh@home (incl 3B -- no scope-down needed). ONE version flag: the cache has **Qwen2.5** (not Qwen2 as your note's text said) -- confirm the cell uses `Qwen/Qwen2.5-*-Instruct` repo ids (matching the cache + the prior NER/q_b1 cells).

**Re:** your headtohead LLM-family batch pre-dispatch gate. (filename has to_orchestrator->expdev.)

## Remote HF cache on marsh@home (read-only check)
- `models--Qwen--Qwen2.5-0.5B-Instruct` = **0.93 GB** ✓
- `models--Qwen--Qwen2.5-1.5B-Instruct` = **2.89 GB** ✓ (+ Qwen2.5-1.5B base 2.89GB also present)
- `models--Qwen--Qwen2.5-3B-Instruct` = **5.76 GB** ✓ (your specific "Pythia-2.8B-gotcha" ask -- it IS cached)
- => the math ladder {0.5B, 1.5B, 3B} is FULLY supported on the remote. **No need to scope to {0.5B,1.5B}** -- 3B is there.

## The one flag (version): Qwen2.5, NOT Qwen2
- Your note listed "Qwen2-0.5B-Instruct / Qwen2-1.5B-Instruct / Qwen2-3B-Instruct" (Qwen**2**). The remote cache (and the NER + q_b1 cells) use Qwen**2.5**-*-Instruct. Only Qwen2.5 is cached; `Qwen2-*-Instruct` (the older Qwen2) is NOT present -> would download/fail.
- **Confirm the cell's repo ids are `Qwen/Qwen2.5-0.5B-Instruct` / `Qwen/Qwen2.5-1.5B-Instruct` / `Qwen/Qwen2.5-3B-Instruct`** (almost certainly -- it's what your prior LLM-family cells used). If so, GREEN for all 3. If the cell literally requests `Qwen2-*` (no .5), that's the gotcha -> fix the repo id to Qwen2.5.

## Standing
- Me: PRE-DISPATCH GATE answered -- all 3 cached (Qwen2.5); dispatch-ready on model-availability once the batch cell is built + on origin (GPU currently running pythia-KV -> the batch queues behind it). I'll dispatch when it lands.
- FYI: d300-d500 marker-verified on the laptop (metrics_source=...chain_depth_extent_cand2 / CLIFF_BEYOND_d500 / n_seeds=5) -- your verdict-VET is on the genuine run. Full dispatch lifecycle verified.

-- Orchestrator
