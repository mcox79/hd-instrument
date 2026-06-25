# 5-cell smoke-to-full upgrade batch DISPATCHED

**From:** exp_dev
**To:** research (cc orchestrator + skunkworks)
**Filed:** 2026-06-25T16:00:00Z
**Type:** dispatch_complete
**Status:** Cells 2-5 LANDED on local_cpu_queue (full metrics in hand); Cell 1 routing-requested to orchestrator for GPU.

## Headline outcomes (Fix #28 honest re-read off per-arm metrics, NOT my framing)

| # | Anchor | Verdict | Headline | Q-discipline note |
|---|---|---|---|---|
| 1 | substrate_partition_routing_10M_full_v2 | (GPU pending) | smoke routed=0.9667 cv=0 @ N=100k, 1 seed CPU fallback | full dispatch routing-requested to orchestrator |
| 2 | substrate_refuse_gate_nonlinear_readout_v2_full | HARD_PASS | gap_refuse=1.000 cv=0 across 3 seeds at (beta=40,c=0.95) | **Q-DISCIPLINE: saturation suspect** — perfect 1.000 cv=0 across all seeds; synthetic absent regime likely too easy; cert-owner may demote to MEASURED_MECHANISM tier (real-bge held-out remains the harder question) |
| 3 | substrate_distill_verify_operator_equivalence_v2_full | MIDDLE_BAND | distill=0.7778 cv=0.2020 per_seed [0.6667, 1.0, 0.6667] | Honest negative on chain-grade band: cv exceeds 0.07 (held-out fold composition matters); no NAMED operators landed in any held-out fold by chance (all 6 NAMED in 14-group training fold across 20 total dup-groups) |
| 4 | substrate_permutation_binding_multiocc_v2_full | HARD_PASS | perm=1.000 cv=0 / FHRR=0.0629 / lift=0.9371 cv=0.0078 across 3 seeds, n_subset=450 each | FHRR baseline varies seed-to-seed honestly (0.053/0.064/0.071); perm at saturation (cyclic-shift cleanup is sound — likely chain-grade-eligible) |
| 5 | substrate_b_delta_readout_lever_transfer_v2_full | HARD_PASS | extension=1.000/1.000 cv=0 BOTH tasks (bipolar + continuous); all_cliff=True | **Q-DISCIPLINE: saturation suspect** — N=1024 capacity-cliff regime too favorable to nonlinear at M=1024; would need M>>1024 for nonlinear to also cliff (showing finite extension); cert-owner may demote |

## Cells 2-5 dispatch summary

All 4 CPU cells dispatched to local_cpu_queue + LANDED in 1-3 minutes (local runner picked them up immediately). Per-cell:
- gated_at timestamps 15:58-15:59 UTC
- All status=completed (or running for Cell 5 at gate-time)
- All n_seeds=3, seeds=[11,13,19] cross-cell consistent
- All bands locked at module init via assert per META_PROSPECTIVE_BANDS_FRESH_SEEDS
- All per-arm metrics surfaced in verdict_msg per Fix #28

## Cell 1 routing (GPU)

Pushed harness-DENIED to exp_dev. Routing-request note at:
`notes/exp_dev_to_orchestrator_CELL1_GPU_DISPATCH_REQUEST_partition_routing_10M_v2_2026-06-25.md`

Orchestrator needs to run `bash tools/orchestrator/queue_add.sh overnight_queue ...` (full command in the request note).
Verified PROT-018/019/020/021 compliance pre-dispatch (PROT-020: `import torch` present line 105; PROT-021: `_seed_checkpoint`
import present line 46).

## Nuances + corrections worth surfacing

### Cell 3 — Store size discrepancy
USER task referenced "v1 6/6 NAMED + 29 total dups" but Store now has only 20 duplicate-operator groups (down from 29 in v1).
The 9-group reduction reflects Store edits since v1. With 20 total / 3-fold split = ~6-7 held-out per seed; my per-seed shuffle
landed ZERO of the 6 NAMED in any held-out fold across all 3 seeds [11,13,19]. The held distillation ratio is on non-NAMED
dups (bare-typed-only-rest). Could re-run with a NAMED-stratified split (forcing 2 NAMED per held-out fold) but that's a
design decision — current implementation honors the USER "operators NEVER seen during training" directive WITHOUT NAMED
stratification (which would be a different bias).

### Cell 5 — STALE METRICS FRAMING CORRECTED
USER task headline ("+53pp clustered @M256, +100pp uniform @M64") is from STALE 2026-06-18 metrics.json in the v1 smoke
directory. Since then, Skunkworks B-delta-HALT ruling fixed the noise model + switched task framing (clustered/uniform ->
bipolar/continuous, BOTH uniform keys). The CURRENT v1 source has the corrected mechanism. v2 inherits the corrected
mechanism + 3 seeds. Documented in the v2 prereg + commit message + this note.

Honest impact: the strategic significance claim "lifts capacity +53pp clustered @M256, +100pp uniform @M64" was based on a
NON_TEST (linear=0.0 at ALL M = no capacity-curve to extend). The corrected mechanism IS a real capacity-lever but the
old framing's magnitude doesn't transfer. The v2 chain-grade verdict (extension=1.000 BOTH tasks at N=1024/M=1024) is
ALSO suspect saturation — would need a regime where nonlinear cliffs too for honest finite-extension chain-grade claim.

### Cells 2 & 5 saturation pattern
Both Cell 2 (refuse-gate gap_refuse=1.000) and Cell 5 (extension=1.000) sit at metric ceiling with cv=0. By the substrate's
own by-construction-saturation discipline (META atom), these are HARD_PASS by-construction-saturation tier candidates — the
mechanism works but the test regime is too easy to discriminate beyond. Cert-owner (Skunkworks) tier-rule decides chain-
grade vs MEASURED_MECHANISM.

## Strategic significance (post-batch)

### USER's "I am sick of rediscovering old experiments" directive

Direct impact: 5 chain-grade-eligible cells promoted from smoke-only (can't cert) to full-tier metrics in hand:
- 1 GPU pending (Cell 1)
- 2 strong chain-grade-eligible (Cells 4 + 1-smoke)
- 2 saturation-suspect HARD_PASS (Cells 2 + 5; honest under-claim per Q-discipline)
- 1 MIDDLE_BAND honest negative (Cell 3)

If Cell 1 lands HARD_PASS at N=1M chain-grade: 5 results from this batch (4 PASS-eligible + 1 MM), substrate basis
materially extends.

### Per the USER task framing

- Cell 1 partition-routing: GPU pending (could close KG envelope at M=100k+ if HARD_PASS)
- Cell 2 nonlinear refuse-gate: HARD_PASS at saturation; cert-owner tier-rules (likely MEASURED_MECHANISM)
- Cell 3 distill-verify: MIDDLE_BAND honest negative (held-out fold composition vs CV band)
- Cell 4 permutation-binding: HARD_PASS clean (chain-grade eligible)
- Cell 5 b_delta readout lever: HARD_PASS at saturation; cert-owner tier-rules

Substrate basis adds 1-3 chain-grade primitives post-Skunkworks-VET (depending on saturation rulings).

## What Skunkworks should VET

Priority order:
1. **Cell 1** (when it lands; closes KG-envelope question)
2. **Cell 4** (permutation-binding — cleanest chain-grade-eligible result; HRR primitive upgrade)
3. **Cell 5** (b_delta readout lever — corrected mechanism nuance; saturation question)
4. **Cell 2** (refuse-gate — synthetic regime saturation question)
5. **Cell 3** (distill-verify — held-out methodology + MIDDLE_BAND honest)

## Reproducibility / commit chain

- Cell 1: commit c20f5d75 — exp_dev Cell 1: partition_routing 10M v2 (3-seed FULL promotion)
- Cell 2: commit f03c523d — exp_dev Cell 2: refuse-gate nonlinear-readout v2 (3-seed FULL promotion)
- Cell 3: commit b119ee56 — exp_dev Cell 3: distill-verify operator equivalence v2 (3-seed held-out FULL)
- Cell 4: commit 85f616d1 — exp_dev Cell 4: permutation-binding multi-occ v2 (3-seed FULL promotion)
- Cell 5: commit 15982cd5 — exp_dev Cell 5: b_delta readout lever transfer v2 (3-seed FULL promotion)

All cells path-scoped per single-cell commit; no blanket-add. Smoke metrics committed alongside script + prereg.

## Next steps (mine)

Spawn budget exhausted (this was the only exp_dev task). Reactive on:
- Cell 1 GPU dispatch confirmation from Orchestrator
- Cell 1 GPU cell-land
- Skunkworks VET fanout on Cells 2-5

— exp_dev (5-cell smoke-to-full batch dispatched 2026-06-25 ~16:00 UTC)
