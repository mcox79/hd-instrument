# strategy_request_to_exp_dev_v304_v7_continuous_embedding_infra_diagnostic_2026-06-01

**Source.** verdict_handler v304 batched-9 wave, V7 `continuous_embedding_storage_substrate_v1_n16384` TRUE INFRA_FAILURE.

**Symptom.**
- `verdict=failed wall_s=12` from bridge `verdict_landed`
- `get_metrics(...)` returned `None` for BOTH remote and local
- Remote directory `C:/dev/hd-instrument/data/exp_continuous_embedding_storage_substrate_v1_n16384` DOES NOT EXIST (Get-ChildItem returned PathNotFound)
- 12-second wall = script crashed at startup before creating output directory

**Intended capability.** SimHash projection + moat-survival measurement at N=16384 for the continuous_embedding_storage substrate. Capability REMAINS UNTESTED at FULL.

**TASK (for exp_dev, when un-paused).**
1. **DIAG** — Investigate via remote runner log + venv-shim launcher log; find the crash point (ImportError? Pre-reg validator rejection? OOM at large-N matrix construction? Missing dependency?). Likely candidates:
   - SimHash projection helper missing or mis-imported
   - Pre-reg fail-band validator rejected at startup with non-zero exit before any partial_metrics file write
   - OOM at the N=16384 substrate construction step (12 seconds is too short for a clean OOM crash, more likely an import or pre-reg gate)
2. **RE-DESIGN** — Once root cause identified, re-design with:
   - Import-chain coverage in smoke (per PROT brief Section 3k)
   - Smaller N smoke run to validate the import chain BEFORE FULL ship
   - Output-directory write at the very top of the script (so even an early crash leaves a `crash.log` you can SCP back)
3. **RE-SHIP** — At N=16384 same FULL parameters, after smoke passes the import chain.

**AUTONOMY.** You decide the diagnostic ordering, the smoke design, the re-ship N (could be N=4096 or N=8192 first if N=16384 OOMs at construction), the anchor name (must satisfy PROT-018; if you re-ship at N=8192 use `_v2_n8192` not the original `_v1_n16384`).

**PAUSE GATE.** This routing file is filed but NOT auto-dispatched. exp_dev refuses while `data/orchestrator_paused.flag` exists. The orchestrator decides when to invoke.

**RESCUE SET.** PROT-004/006 cheapest-first:
- R1 (CHEAPEST, 0-compute, APPLIED inline above) — Diagnose script-log + import-chain; capability untested.
- R2 (CHEAP, ~10min DIAG + ~30min re-ship CPU OR ~10min Lambda) — Smoke at smaller N validates import chain; re-ship at FULL.
- R3 (MEDIUM, ~1h CPU) — If OOM at N=16384, re-ship at N=8192 or N=4096 with anchor-name corrected.
- R4 (MEDIUM, ~1-2h CPU) — Cross-N replication once V7 re-ships clean.
- R5 (HIGH-COST, deferred) — Full moat-survival x SimHash-rank x cross-N grid.

**STRATEGIC CONTEXT.** SimHash + moat-survival is a substrate-product-killer-feature candidate (live-drift-detection class). Capability EVAL is open. Re-shipping this anchor is HIGH PRIORITY in the next un-paused exp_dev cycle.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
