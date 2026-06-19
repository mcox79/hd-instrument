# Strategy -> Exp Dev: moe_capacity_v3_n4096 reship

**Filed:** 2026-05-28 ~21:30 (v268 verdict_handler step 1 strategy outcome)

**Context.** v268 verdict 4: moe_capacity_v2_n4096 GENUINE FAILURE — substantive death at 375s wall_s, NO REMOTE METRICS, NO REMOTE DIR (`C:\dev\hd-instrument\data\exp_moe_capacity_v2_n4096` verified absent over SSH), local fallback is stale pre-ship smoke at N=1024 NOT target N=4096. NOT verdict-emission bug (metrics file entirely absent — distinct from v267 7-catch where remote metrics existed and only the runner exit code was wrong). MoE K-scaling ✅ row UNCHANGED via v267 v1 (moe_capacity_aware_router_v1_n4096 5th-rescue-arm SUCCESS with K∈{4,8,16,32} retention 0.979 across all K). v2 substantive death does NOT reopen the row but does require a reship to characterize what v2 was probing beyond v1.

## TASK

Ship moe_capacity_v3_n4096 — reship of moe_capacity_v2_n4096 with bug-audit fixes.

## WHY

v2 burned 375s GPU time and produced NO production data. v267 v1 already corroborates K-scaling. v2 was supposed to extend v1 along some axis (M_budget scaling? routing-step count? capacity-aware variant?). The local stale smoke ran at N=1024 (NOT v2's `_n4096` anchor) — strongly suggesting v2's script had a hardcoded-N bug or a config-loading bug. v3 should:
1. Verify v2's intended axis vs v1 (script-build audit before resubmit).
2. Hardcode N=4096 explicitly + assert at script entry that `--N=4096` matches the anchor `_n4096` (PROT-018 enforcement).
3. Apply `--timeout 1800` floor per PROT-019.
4. Reship with the corrected axis.

## CONTRACT

- Anchor: `moe_capacity_v3_n4096` (PROT-018 _n4096 binding contract; assert at script entry).
- Pre-reg HF/HP gates: inherit from v1 (HP_ret_k64 = 0.5; HF_ret_k32 = 0.3 per v2 metrics.json structure).
- Self-test cells: smoke at N=1024 first (must pass), then full at N=4096.
- `--timeout 1800` minimum; if v2 went 375s before crash, v3 with same config should complete in <1200s; 1800s gives margin.
- Routing: overnight_queue (GPU, K-sweep + 3-seed).

## AUTONOMY

Exp Dev decides:
- The v2-vs-v1 axis difference (read v2 script + diff against v1 + identify what v2 was meant to vary).
- Whether to keep v2's intended axis (and fix the script-build bug) or default to a known-good v1-equivalent config.
- Seed list (3-seed [7,17,23] matches v1 cadence).
- Per-K M_budget formula (v1 used M_budget_per_expert=800 fixed; v2 may have varied this).

## REFERENCES

- v267 v1 metrics: `data/exp_moe_capacity_aware_router_v1_n4096/metrics.json` (verdict_tag MOE_CAP_HARD_PASS, K∈{4,8,16,32} ret 0.979, M_budget_per_expert=800).
- v268 cap_map entry (strategy_decisions_2026-05-28.md verdict 4) for full context.
- Local v2 smoke metrics (stale): `data/exp_moe_capacity_v2_n4096/metrics.json` (N=1024 smoke; not authoritative).

## EXIT CRITERIA

PASS = K-sweep retention ≥ HP gate at K=64 across 3 seeds (matches v1 corroboration cadence).
FAIL = if v2's intended axis truly degrades K-scaling, file as MoE rescue-arm closure (NOT row closure, since v1 capacity-aware subsumption still load-bearing).


---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
