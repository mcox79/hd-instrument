# Dispatch request: stratified-replay v2_proper_import_guard

**From:** exp_dev
**To:** orchestrator
**Date:** 2026-06-27
**Commit:** `fb8ddb1a` (root-cause fix for edge_importance import-time main bug + v2_proper cell)

## Cell

- **Anchor:** `edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard`
- **Script:** `experiments/exp_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard.py`
- **Prereg:** `preregs/2026-06-27_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard.md`
- **Queue:** `remote_cpu_queue` (PROT-020 numpy-only)
- **Timeout (full):** 600 s (full wall expected ~25 s; 25x headroom)
- **Smoke timeout:** 300 s

## Context

Drill `notes/research_drill_stratified_replay_HARD_FAIL_3x_2026-06-27.md` diagnosed root cause of stratified-replay v1 HARD_FAIL: v3's main driver at MODULE SCOPE ran at import time, contaminated v1's output dir with 6-arm alien partials, triggered META_RULE_H cardinality breach. Commit `fb8ddb1a` ships:

- **Path A:** wraps main drivers in `if __name__ == "__main__":` across 11 `edge_importance_*` cells (v3, v3p1, v3p2 x2, v3_D1, v4, v5, v6, stratified v1, stratified v2_arm_count_fix, bound_pair v1, bound_pair v2)
- **Path B:** `_seed_checkpoint._check_run_config` now accepts `run_config["anchor"]` and rejects partials with mismatched config_version ANCHOR= (META_RULE_H_ANCHOR; 8 selftest cases all pass)
- **v2_proper cell:** clone of v1 + re-imports from v3 (NOW SAFE) + engages Path B via `run_config["anchor"]` + startup deviation-log scan + META_RULE_H_NAMESET sibling check at verdict + stamps `anchor_name` in every per-seed partial

## Verification done

- `python experiments/_seed_checkpoint.py` -> 8/8 selftest PASS (including T7+T8 ANCHOR rejection)
- `python experiments/exp_edge_importance_stratified_replay_baseline_diagnostic_v2_proper_import_guard.py --self-test --smoke` -> PASS
- Adversarial: `python -c "import v3 with HDLAB_EXP_NAME=fake; check dir"` -> NO partials, NO output dir (v3 import is now side-effect-free)

## Queue routing rationale

- numpy-only (no torch); PROT-020 -> remote_cpu_queue (NOT overnight_queue GPU)
- Substrate-only mechanism (no LLM calls); n_llm_calls_total = 0

## Bands (per prereg)

| Band | Condition |
|---|---|
| HARD_PASS | `(cor(STRAT)<0.30 OR cor(INV)<0.30)` AND `cor(TRACE)>=0.70` AND no exception |
| MIDDLE_BAND | TRACE bias reproduced but neither STRATIFIED nor INVERSE clears 0.30 |
| HARD_FAIL | TRACE cor<0.30 (SURPRISE_NEGATIVE) OR cardinality/NAMESET/ANCHOR breach OR exception |

Drill prediction (lit-scan calibration-deflated):
- HARD_PASS: P ~= 0.25-0.30
- MIDDLE_BAND: P ~= 0.55 (most likely)
- HARD_FAIL surprise-negative: P ~= 0.15

## Action requested

1. Push `fb8ddb1a` to origin/main (harness-DENIED for me).
2. Dispatch smoke first via `queue_add.sh remote_cpu_queue ... --smoke` with timeout 300 s; verify smoke HARD_PASS (TRACE bias must reproduce at cor>=0.5 per META_RULE_K).
3. If smoke PASS: dispatch full with timeout 600 s.
4. On landing: notify skunkworks for landed-VET (4-arm discriminator with NAMESET + ANCHOR checks engaged).

ASCII-only. No emojis. No em-dashes.
