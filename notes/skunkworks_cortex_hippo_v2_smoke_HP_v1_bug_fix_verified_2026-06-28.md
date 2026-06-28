# Skunkworks landed-VET: cortex_hippo_handoff v2 replay-fixed seed_7 SMOKE HARD_PASS

**Date:** 2026-06-28
**Commit:** 831ca999 (atoms + tool); cell commit 522c38b8
**Anchor:** substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7
**Ruling:** SMOKE-VET HARD_PASS (CERT-neutral); v1 bug genuinely fixed (independent contrastive audit)
**CERT delta:** +0 (chain-grade increment deferred to 3-seed FULL landing)

## What actually landed (not what the spawn-prompt framed)

Director's spawn-prompt framed this as a chain-grade landed-VET; on-disk reality:
- ONE metrics.json present: `data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7/metrics.json`
- run_mode=**smoke** (NOT full)
- backend=**torch.cpu** (cuda_available=False; GPU not exercised)
- M=512, N_h=512, N_c=2048, N_replay=10 (NOT the chain-grade target M=8192, N_h=4096, N_c=8192, N_replay=50)
- alpha_simple=0.25 at smoke (chain-grade target alpha=1.0)
- 1 seed (not 3)
- seed_13 metrics.json: **NOT PRESENT** on disk
- seed_19 metrics.json: **NOT PRESENT** on disk

No queue entries / no dispatch evidence for seeds 13 or 19. The "(seed_13 + 19 in flight)" framing in the spawn-prompt was SPECULATIVE.

## Off-data recompute (verify-the-referent; Fix #28)

Skunkworks independent recompute (numpy RandomState replays):
- ARM_FULL_HANDOFF: 0.748047 (landed: 0.748047) MATCH
- ARM_NO_REPLAY: 0.001953 (landed: 0.001953) MATCH
- ARM_DIRECT_CORTEX: 1.000000 (landed: 1.000000) MATCH

Verdict gates (smoke-config, all 4 pass):
- full >= 0.50: True (0.748)
- gap_FULL_vs_NO >= 0.40: True (+0.746)
- arm_dist_FULL_vs_DIRECT > 0.05 (v2 NEW): True (0.252)
- alpha_simple >= 0.05: True (0.25 at smoke)
- bit-exact-collapse guard (arm_dist >= 1e-6): True
- NO_REPLAY fairness (<= 0.20): True (0.002)

## Source-code audit: is v1 bug genuinely fixed?

YES. Cell file lines 478-503 (ARM_FULL_HANDOFF torch path):

```
W_hippo.addmm_(vals_h.T, keys_h)
gen = torch.Generator(device=dev); gen.manual_seed(seed + 31)
for cycle in range(N_REPLAY_CYCLES):
    perm = torch.randperm(M_ITEMS, generator=gen, device=dev)
    cues_h = keys_h[perm]
    react_raw = cues_h @ W_hippo.T               # <-- READS W_hippo
    vals_react_h = torch.sign(react_raw)         # <-- DEPENDS on W_hippo
    vals_react_h = torch.where(vals_react_h == 0, torch.ones_like(vals_react_h), vals_react_h)
    cues_c = cues_h @ P_hc.T
    cues_c = cues_c / cues_c.norm(dim=1, keepdim=True).clamp_min(1e-12)
    vals_c_react = vals_react_h @ P_hc.T         # <-- carries W_hippo dependence
    vals_c_react = vals_c_react / vals_c_react.norm(dim=1, keepdim=True).clamp_min(1e-12)
    W_cortex.addmm_(vals_c_react.T, cues_c, alpha=ETA_CORTEX)   # <-- writes USING W_hippo readout
```

This is mathematically distinct from ARM_DIRECT_CORTEX (line 537):

```
W_cortex.addmm_(vals_c.T, keys_c, alpha=ETA_CORTEX)   # <-- writes STORED vals_c (bypasses W_hippo)
```

## Independent contrastive audit (separate from cell selftests; META rule first application)

Built in `tools/skunkworks_atomize_cortex_hippo_v2_smoke_HP_v1_bug_fix_verified_2026-06-28.py::run_independent_contrastive_audit`. Different RNG, smaller dims (M=256/Nh=256/Nc=512/n_replay=5):

| Comparison | diff_frob | Required | Result |
|---|---|---|---|
| (a) v2 FULL vs v2 DIRECT | 0.491 | > 0 | PASS (v2 genuinely distinct) |
| (b) v1-broken-reconstruction vs v2 DIRECT | 0.000 | ~0 (replicate v1 bug) | PASS (contrast valid) |
| (c) v2 FULL vs v2 FULL-with-W_hippo-zeroed-before-replay | 0.820 | > 0 | PASS (W_hippo load-bearing) |

The fact that (b) reproduces the v1 bug bit-exactly proves my contrastive setup correctly models the broken path. The fact that (a) and (c) both yield large diff_frob confirms (a) v2's FULL write expression IS different from DIRECT, and (c) W_hippo IS in the dataflow (not decorative).

## Cell selftests (necessary but not sufficient under META rule)

`python experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py --self-test`:
- `_selftest_anatomical_separation` PASS
- `_selftest_sparse_pattern_separator` PASS
- `_selftest_projection_dim_match` PASS
- `_selftest_chunk_seed_matches_anchor` PASS
- `_selftest_capacity_alpha` PASS (FULL config: alpha_simple=1.0)
- `_selftest_torch_batched_matches_numpy` PASS
- `_selftest_full_arm_uses_hippo_readout` (v2 NEW) PASS
- `_selftest_full_arm_differs_from_direct` (v2 NEW) PASS

Per the new META_RULE_INDEPENDENT_CONTRASTIVE_AUDIT (just atomized), cell selftests share author-bias with original bug; an independent audit by a separate role is required for bug-fix promotion. Both lines of evidence now converge.

## Expected-vs-observed mechanism shape

Director's spawn-prompt asked: is FULL=0.748 vs DIRECT=1.000 "OK because hippo introduces denoising overhead" or a different bug?

**Expected behavior, per pre-reg risk section:** DIRECT bypasses the lossy hippo channel and gets clean vals_c -> trivially saturates at M=512 << N_c=2048 capacity. FULL goes through interference-laden hippo readout `sign(W_h @ cue)` at alpha_hopfield=0.080 (lossy regime), so FULL recall lands below DIRECT by some nonzero margin. This is CLS-consistent (lossy consolidation channel; capacity-bounded readout fidelity). NOT a bug.

If FULL > DIRECT or FULL == DIRECT, THAT would be the bug. FULL < DIRECT with a substantial nonzero gap (0.252) is the expected v2 signature.

## CERT decision and tier

**Tier: SMOKE-VET HARD_PASS (CERT-neutral; smoke pass-through; cert_class=smoke_vet)**

Reasoning:
1. Chain-grade CERT increment requires FULL-config 3-seed cross-seed evidence.
2. Smoke run at M=512/N_c=2048 is the discriminator-survives-scale check; that's its purpose, not a chain-grade datum.
3. backend=torch.cpu means the GPU dispatch claim is UNVERIFIED at smoke (Fix #24).
4. Cell is cleared for FULL dispatch (all selftests PASS; smoke gates clear; v1 bug independently verified fixed).

A premature chain-grade tier ruling on smoke would be a Fix #28 violation (over-claiming from verdict_msg framings without per-arm at-scale evidence).

## Stage 2 NREM replay phase coverage update

Coverage delta: **NONE** at this audit. Stage 2 NREM replay coverage moves MID -> HIGH only on the 3-seed FULL HARD_PASS landing. Smoke clearance just keeps the door open.

## Composes with

- `T_methodology/META_RULE_AF_AMENDMENT_FULL_vs_DIRECT_bit_exact_equality_FATAL_for_handoff_cells` (the v1 audit amendment; just satisfied)
- `T3/EXP_cortex_hippo_handoff_FULL_seed_17_HARD_PASS_replay_consolidates_singlesee` (sibling cell at smaller dims; established the FULL path can work)
- `T3/EXP_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v1_seed_{7,13,19}_HARD_FAIL_*` (sibling v1 HF atoms preserved; chain trail intact)
- `T3/EXP_substrate_sequence_binding_K_cliff_phase_diagram_full_v2_CROSS_SEED_CHAIN_GRADE_*` (parallel Stage 2 chain-grade; just promoted today)

## Test-design red flags

Two new META atoms filed for the broader fleet:

1. **META_RULE_INDEPENDENT_CONTRASTIVE_AUDIT**: bug-fix promotion needs independent contrastive audit (cell selftests share author-bias).
2. **META_RULE_spawn_prompt_must_not_speculate_about_pending_landings**: Director spawn-prompts should not frame pending/in-flight seeds as if they exist; report on disk-present state only.

## Next actions for Director

1. Cell-author dispatches FULL 3-seed (M=8192, N_h=4096, N_c=8192, backend=torch.cuda) via `hdi_orchestrator` to remote_gpu_queue (per Fix #24 GPU routing rule; cell N_DIM>=8192 matmul-heavy).
2. Wait for 3 metrics.json on disk before re-spawning Skunkworks.
3. On 3-seed landing, re-spawn Skunkworks for chain-grade aggregation atom (potential CERT +1).
4. Substrate-KB query before next handoff cell-design per USER 2026-06-27 (canonical query-first).

## Files

- atomize tool: `d:/AI/hd-instrument/tools/skunkworks_atomize_cortex_hippo_v2_smoke_HP_v1_bug_fix_verified_2026-06-28.py`
- math atom: `d:/AI/hd-instrument/data/substrate_index/math/atoms.jsonl` (line 28708)
- meta atoms: `d:/AI/hd-instrument/data/substrate_index/meta/atoms.jsonl` (lines 252, 253)
- cert ledger: `d:/AI/hd-instrument/data/substrate_index/meta/cert_ledger.jsonl` (lines 947, 948, 949)
- cell: `d:/AI/hd-instrument/experiments/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7.py`
- pre-reg: `d:/AI/hd-instrument/preregs/2026-06-28_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed.md`
- landed metrics: `d:/AI/hd-instrument/data/exp_substrate_cortex_hippo_handoff_chain_grade_M_8192_GPU_v2_replay_fixed_seed_7/metrics.json`
- this commit: 831ca999
