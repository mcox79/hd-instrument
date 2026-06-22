# n9 SMH Landed-VET (Skunkworks)

**Date:** 2026-06-22 UTC
**Cell:** exp_n9_smh_sparsemax_decode_v1 (commit 2f765150)
**Cert disposition:** HONEST_NEGATIVE (pre_reg_miss_proven_bound)
**Cert delta:** 0 (CERT 584 UNCHANGED)
**Cert ledger row hash:** `2caf2f8f6cf148ab`
**Atoms added:** 2 (cell record + META storage-chain item #3)

## Plain English

SMH (Sparse Modern Hopfield sparsemax-attractor decode) was the Path C ARM A 2x-revival
drill's #1 ranked rescue (composite P=0.234). The result is decisive HARD_FAIL: SMH
recall at M=10k sigma=0.1 = **0.0194**, far below the pre-reg HARD_FAIL bar of 0.35
(gap = 0.331). The key finding is not just the failure but the MECHANISM proof: SMH
and dense softmax Hopfield are identical to 4 decimals on every (M, sigma) cell -- the
decode form does not matter when the attention scores don't separate. Combined with the
projection value-cue recall@1 sanity = 0.010 chance at both seeds, the diagnosis is
unambiguous: the projection step is producing keys that are inseparable at the
substrate's effective dimensionality. The decode-algebra rescue family
(sparsemax-attractor / dense softmax Hopfield / argmax / tag-retrieval-class) is
EXHAUSTED for eff-rank-limited storage at high M. Next route is eff-rank-RAISING at
projection: whitening of the contrastive projection (cheap) and/or larger encoder
(pythia-160m -> 1B -> 2.8B; CERT 591 used 2.8B successfully).

## Verify-off-DATA reconciliation (all cited numbers reproduce within 0.0001)

| Metric | Claimed | Re-derived | Match |
|---|---|---|---|
| SMH @ M=10k sig=0.1 | 0.0194 | 0.0194 (mean of [0.0213, 0.0175]) | PASS |
| Dense softmax Hopfield @ M=10k sig=0.1 | 0.0194 | 0.0194 (mean of [0.0213, 0.0175]) | PASS |
| ARM A argmax @ M=10k sig=0.1 | 0.0081 | 0.0081 (mean of [0.0037, 0.0125]) | PASS |
| SMH shuffled CAN-FAIL ctrl @ M=10k sig=0.1 | 0.0050 | 0.0050 (mean of [0.0037, 0.0063]) | PASS |
| Anchor argmax @ M=1k sig=0.0 | 0.0337 | 0.0337 (mean of [0.0362, 0.0312]) | PASS |
| Projection value-cue recall@1 (s7, s17) | 0.010, 0.010 | 0.010, 0.010 | PASS |
| cv at discriminator | 0.098 | 0.0979 | PASS |
| SMH vs dense Hopfield delta per seed | 0.0 (claimed identical) | [0.0, 0.0] EXACTLY | PASS |

**Strongest evidence (load-bearing):** SMH and dense softmax Hopfield are identical to
4 decimals on EVERY (M, sigma) cell in the n9 sweep (9 cells x 2 seeds = 18 comparison
points; all delta = 0.0 EXACTLY). This is the strongest possible empirical proof that
decode form is not the bottleneck.

## Run-mode check (Fix #5)

- metrics.json top-level: `run_mode = "full"`
- per_seed[0].run_mode = "full"; per_seed[1].run_mode = "full"
- queue_entry_name = "n9_smh_sparsemax_decode_v1_smoke" (queue name carries `_smoke`
  suffix but the runner ignored it and ran full mode -- a known runner gap, now
  captured as Fix #11 template TODO #6 refinement)
- CONFIG_VERSION includes full-scale grid: M ∈ {1k, 5k, 10k}, sigma ∈ {0, 0.1, 0.3}

The cell honored full mode; the queue-entry-name `_smoke` suffix did NOT propagate.
This is a runner-gap, not a cell bug. The full-scale data is valid for cert ruling.

## Discriminating-regime sanity

cv across 2 completed seeds at the discriminator (M=10k, sigma=0.1) = 0.0979.
- Below the 0.10 noise-floor band: PASS
- The missing seed (s23) cannot move the verdict tier given the 17x gap from observed
  (0.0194) to HARD_FAIL bar (0.35)
- By-construction-saturation check PASSES: shuffled CAN-FAIL ctrl 0.0050 ~ chance after
  kWTA smoothing (theoretical 1/M = 0.0001; kWTA broadens to ~0.005); control valid
- substrate_only_decode_gate: N/A (KV-storage cell, not LM cell; per Path C revival
  framing); zero_llm_calls_at_inference = True (LLM only at encode)

## Cert disposition rationale

The cell-author labeled HARD_FAIL via the pre-reg HARD_FAIL bar (recall < 0.35 at
M=10k sig=0.1). Cert-owner RATIFIES the HARD_FAIL disposition off DATA + off pre-reg
INTENT (no overrule). The pre_reg_miss_proven_bound class is correct: the lever
(SMH sparsemax-attractor decode) is decisively bounded as a Path C rescue.

Direction-correct: HARD_FAIL bar was recall < 0.35; observed 0.0194 << 0.35 (no
wrong-direction inversion; no Skunkworks-style override needed).

## Atom landings (A5-gated PRE=POST=CERT 584; +2 atoms)

1. `math::T3/EXP_n9_smh_sparsemax_decode_v1` — EXPERIMENT_RECORD (HONEST_NEGATIVE,
   provenance_quality=HONEST_NEGATIVE, algebra=None, axiom_term unchanged)
2. `math::T3/META_storage_chain_item3_eff_rank_limited_at_projection_step_decode_algebra_rescue_family_exhausted_2026-06-22`
   — METHODOLOGY_RULE (DISCIPLINE_META; cert-neutral storage-chain diagnosis;
   composes with Path C ARM A HARD_FAIL row `f2a658ddda005c98`, Path D 4-arm storage-win
   MM row `de73c03c0510d4b2`, and n9 ledger row `2caf2f8f6cf148ab`)

## Composition map

The n9 HONEST_NEGATIVE + META storage-chain item #3 compose with:

- `T3/EXP_armA_projected_key_revival_v1` (Path C ARM A HARD_FAIL; ledger row
  `f2a658ddda005c98`) — n9 is the load-bearing eff-rank-limited proof on top of ARM A
- `T3/EXP_kv_learned_projection_v1` (CERT 591; the learned contrastive projection
  lineage) — the projection step n9 isolates as the failure site
- `T3/EXP_anisotropy_rescue_4arm_sweep_v1_gpu` (Path D 4-arm storage-win value-refined
  MM; ledger row `de73c03c0510d4b2`) — NOT invalidated by n9; uses a different storage
  mode; remains the currently-best demonstrable storage advantage
- 4-arm anisotropy MIDDLE_BAND smoke-tier (ledger row `1e1302ff6293598f` superseded by
  Path D) — superseded; n9 confirms the storage-chain diagnosis the supersession
  implied

## Cert ledger row payload (written in same A5 window)

```json
{
  "op": "cert_ruling",
  "atom_id": "math::T3/EXP_n9_smh_sparsemax_decode_v1",
  "cert_status": "honest_negative",
  "cert_class": "pre_reg_miss_proven_bound",
  "verified_off_data": true,
  "atomized_by": "skunkworks",
  "cell_commit": "2f765150",
  "verdict": "HARD_FAIL",
  "cert_increment_delta": 0,
  "cv": null,
  "referent_pointer": {
    "notes_path": "notes/n9_smh_sparsemax_decode_pipeline_complete_2026-06-22.md",
    "metrics_path": "data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json",
    "atom_qualified_id": "math::T3/EXP_n9_smh_sparsemax_decode_v1"
  },
  "supersedes": null,
  "note": "pipeline_agent_n9_smh_sparsemax_decode_v1_hard_fail_eff_rank_limited",
  "row_hash": "2caf2f8f6cf148ab"
}
```

## 2x -> 3x revival route (route-negatives-to-research)

**Routing ask to Research (per USER standing 2026-06-20 "route negatives for 2x/3x
revival drills"):** the decode-algebra rescue family is exhausted; the natural 3x
drill is at the **projection step** (eff-rank raising), not the decode step.

Priority-ranked revival angles (Research: please consider a 3x revival drill on these):

1. **Whitening of the contrastive projection** (CHEAPEST FIRST): remove the
   collapsed-direction artifact that drove proj_recall_sanity to chance. Single-cell
   decisive test; no encoder change; composable with everything downstream. Estimated
   composite P (calibrated against the n9 negative's MECHANISM diagnosis): 0.45-0.55
   (projection-step rescue is precedented by the CERT 591 lineage; whitening removes a
   known failure mode in learned-projection contrastive methods).

2. **Larger encoder upgrade (pythia-160m -> 1B):** CERT 591 used 2.8B successfully on
   held-out facts; the same encoder upgrade may revive sparse-superposition at high M
   by raising the effective rank of the value-cue space. Higher cost; pre-cell pre-reg
   needed.

3. **Combined whitening + larger encoder:** compose 1 + 2. Cheapest after each
   component is empirically validated.

4. **GATED -- DEFER: PKM (Product Key Memory; top-2 candidate from 2x drill).** PKM
   shares the key-factorization assumption that fails here. Should NOT be dispatched
   until eff-rank-raising is attempted -- otherwise PKM will fail by the same
   mechanism and waste a cycle.

## Fix #11 template refinements (5 TODOs updated)

See `tools/spawn_templates/experiment_pipeline_agent_template.md` for the patched
TODOs section. Five field-test findings landed:

1. TODO #6 + new bullet: queue_add.sh `--` env-after-separator pattern doesn't honor
   HDLAB_RUN_MODE=smoke; queue entry name `_smoke` suffix ignored by runner. Workaround
   = in-cell name detection.
2. TODO #7 + new bullet: drill per-seed estimate (5-15min) underestimated actual
   (~22min/seed). Cell-author MUST measure near-full-scale wall before drill-estimate
   becomes budget.
3. New TODO #8: conservative wall budget for encoding-dominant cells (2-3x the 3600s
   default; n_seeds * max(measured, 1500s) * 1.5 with 50% safety margin).
4. New TODO #9: atexit/SIGTERM synthesize-metrics-from-partials pattern (n9's
   write_metrics did not fire on SIGKILL timeout; partials saved but aggregate
   recovered externally).
5. New TODO #10: push-harness-DENIED handoff (CONFIRMATION; orchestrator route works
   as designed; no template patch needed).

Plus a POST-MORTEM section appended at template tail documenting first-use outcome.

## Asks

- **Research (Director):** please schedule the 3x revival drill on (a) whitening of
  the contrastive projection and (b) larger-encoder upgrade. PKM should be GATED
  behind eff-rank-raising.
- **Director:** please update `data/director_plan.json` to reflect:
  - Path C ARM A revival #1 (SMH sparsemax) = HONEST_NEGATIVE (proven bound; decode-
    algebra rescue family exhausted)
  - Next priority for Path C = eff-rank-raising at projection step (whitening first)
  - PKM = GATED / deferred behind eff-rank-raising
- **Exp-Dev (cell-author):** acknowledged the HARD_FAIL disposition ratification + the
  Fix #11 template refinements. The pipeline-template's first field test produced 5
  durable refinements; the template is correct in structure; the gaps are at the
  runner-passthrough + budget-floor + timeout-write layers (now patched).

## Artifacts

- Cell: `experiments/exp_n9_smh_sparsemax_decode_v1.py` (commit `2f765150`)
- Cell-author completion note: `notes/n9_smh_sparsemax_decode_pipeline_complete_2026-06-22.md`
- Metrics: `data/exp_n9_smh_sparsemax_decode_v1_smoke/metrics.json`
- Atomize tool: `tools/skunkworks_atomize_n9_smh_honest_negative_2026-06-22.py`
- Template (refined): `tools/spawn_templates/experiment_pipeline_agent_template.md`
- Pre-reg: `notes/research_path_c_armA_2x_revival_drill_2026-06-22.md`
- Composes-with: ledger rows `f2a658ddda005c98` (Path C ARM A), `de73c03c0510d4b2`
  (Path D 4-arm storage-win MM)
- New cert ledger row: `2caf2f8f6cf148ab` (n9 honest_negative; delta=0; CERT 584
  unchanged)
