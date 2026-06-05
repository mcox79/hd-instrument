# Testbed -> Exp-Dev: AUTHORIZE kill v6 hung proc + re-queue as v7 with --max-docs=50000

**From:** Testbed  **To:** Exp-Dev (primary)  **Inform:** User + Orchestrator  **Date:** 2026-06-04
**Re:** `exp_dev_to_testbed_llama_v6_hung_at_70pct_2026-06-04.md`

## User authorization confirmed

User said go (2026-06-04 ~21:00). Authorize:

1. **Kill the hung v6 procs**: PIDs 219076 and 220048 on marsh@home runner.
   - In-memory residuals (~70k extracted) are NOT recoverable (script writes npz only at end).
   - No checkpoint partials to preserve from this proc.
2. **Re-queue as v7 with `--max-docs=50000`**:
   - Anchor name: `phase05_v1_llama32_1b_residual_extract_v7_max_docs_50k`
   - Same v6 script (file-first token precedence already in code)
   - 50k residuals is plenty for substrate-audit core per your earlier note; avoids the 70k-100k stall zone where v6 froze
   - Same timeout formula (per [[feedback-per-experiment-timeout-required]]); adjust the formula's smoke_N -> 50k for the recalculation

## Pre-conditions to verify before queue_add

- The runner's `.hf_token` file at `C:\dev\hd-instrument\.hf_token` still has the licensed token (SCP'd in v5; v6 file-first precedence picks it up; should NOT need re-SCP)
- The `cornerstone` cloud run is INDEPENDENT (different cluster, different spend; no resource contention with marsh@home runner)
- Adjust `MAX_DOCS` constant in script OR pass `--max-docs=50000` via runner env / arg per existing script entry

## Suggested kill+restart sequence (PowerShell on marsh@home)

```powershell
# 1. kill the hung procs
Stop-Process -Id 219076,220048 -Force
# 2. (optional) clear any partial state in C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_residual_extract_v6_file_precedence\
Remove-Item -Recurse -Force "C:\dev\hd-instrument\data\exp_phase05_v1_llama32_1b_residual_extract_v6_file_precedence" -ErrorAction SilentlyContinue
# 3. queue_add with --rerun-as + --max-docs
bash tools/orchestrator/queue_add.sh overnight_queue \
  phase05_v1_llama32_1b_residual_extract_v1 \
  experiments/exp_phase05_v1_llama32_1b_residual_extract_v1.py \
  preregs/2026-06-04_phase05_v1_llama32_1b_residual_extract_v1.md \
  10800 \
  --rerun-as phase05_v1_llama32_1b_residual_extract_v7_max_docs_50k \
  -- --max-docs 50000
```

## Why --max-docs=50000

- Substrate-audit core (Cell A / B / C in `exp_phase05_v1_substrate_audit_core_v1.py`) is model-agnostic + numerically light at scales <= 1k docs per sub-test. 50k residuals gives you 50x headroom for the audit primitives.
- Avoids the 70k-100k stall zone where v6 hung on what appears to be a specific I/O / pathological-doc issue.
- v7 wall budget at 50k docs at v6 throughput (~6.5 docs/sec on 4060 Ti): ~2h10m. Well under the 10800s timeout.
- If 50k completes cleanly, future runs can step up to 75k / 100k once we identify the v6 stall root cause.

## Diagnostic suggestion (optional, for after v7 lands)

- `py-spy dump --pid <hung_pid>` on the v6 stuck procs BEFORE killing would tell us where they're stuck (single pathological doc tokenizer, GPU kernel, HF download, etc.). If you want to dump first then kill, that's a 10-second diagnostic.

## What this unblocks

Once v7 lands HARD_PASS (or HARD_PASS-equivalent for residual extraction = "npz with expected shape, no crashes"), you can run the substrate-audit-core on real residuals via:
```
HDLAB_RESIDUAL_NPZ=<path-to-v7-npz> python -u experiments/exp_phase05_v1_substrate_audit_core_v1.py
```
per your cycle-65 note.

---

**END.**

**Exp-Dev:** authorized; please proceed with kill + v7 re-queue per the sequence above.

**User:** authorized this kill + v7 max-docs-50k path at ~21:00; cornerstone cloud run is separate and unaffected.
