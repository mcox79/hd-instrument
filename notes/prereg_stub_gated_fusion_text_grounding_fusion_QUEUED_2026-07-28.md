# PRE-REG STUB (QUEUED, not run) — apply hdlab/gated_fusion to text+grounding fusion

Status: **QUEUED-READY, NOT DISPATCHED.** Written by hdi_testbed 2026-07-28 as the
capability-gate's first real APPLICATION use of `hdlab/gated_fusion.py`. Do NOT run
this locally (no local GPU experiments per current directive) -- dispatch to the
remote GPU/CPU queue via `hdi_exp_dev` / `hdi_orchestrator` once the current
consolidation/grounding pipeline frees a slot.

## Why this exists
`gated_fusion` (`hdlab/gated_fusion.py`, promoted from
`experiments/exp_grounding_gated_fusion_relation_inference_mammal_v1.py`, HARD_PASS
+0.297 MRR, 8 seeds) proved the mechanism on RELATIONAL-vs-GROUNDED code fusion. The
encoder frontier has repeatedly circled a structurally identical problem it hasn't
applied the mechanism to: fusing the from-scratch TinyTransformer TEXT encoder
(`scale_win_tinytransformer_encoder`, tail 29591, registry-WIRE) with structured
GROUNDING estimates, without the naive equal-weight SUM diluting whichever arm is
weaker for a given entity/row (the exact failure mode `gated_fusion` was built to fix).

## Proposed cell (design-stage; author owns final pre-reg at dispatch time)
- **Anchor name:** `exp_gated_fusion_text_grounding_encoder_v1` (author may rename).
- **Arms:** TEXT_ONLY (scale_win_tinytransformer_encoder embedding), GROUNDED_ONLY
  (current best structured-grounding estimate for the same entities), GATED_FUSED
  (`hdlab.gated_fusion.gated_table` + `learn_lambda`, lambda fit on VAL), FUSED_EQUAL
  (naive SUM, the diluting baseline being replaced), SCRAMBLE_GATED (must-fail control:
  grounding attributes shuffled across entities, lambda re-learned), RANDOM (null),
  ORACLE (held-out folded in, arena-answerable ceiling).
- **Bands (mirror the source cell's pre-registered bands, recalibrate for the new
  arena's scale, do NOT reuse the mammal-KG numeric thresholds verbatim):**
  HARD_PASS = GATED_FUSED beats TEXT_ONLY by a real margin AND does not dilute below
  GROUNDED_ONLY AND beats SCRAMBLE_GATED by a real margin (same 3-condition shape as
  `HP_RECOVER_GAIN` / `DILUTION_TOL` / `SCR_ABS_MARGIN` in the source cell).
- **Scorer:** author supplies a `score_fn(fused_table) -> float` closure (filtered
  MRR or whatever the target task's real metric is) per `hdlab.gated_fusion.Scorer`
  -- this module has zero eval-pipeline dependency by design.
- **Import:** `from hdlab.gated_fusion import gated_table, equal_sum_table, learn_lambda`
  (NOT a copy-paste of the source cell's private `_gated_table` -- that's the whole
  point of promoting it).

## Gate this stub does NOT pre-decide
- Whether the text encoder and grounding estimate live in the same code space /
  dimensionality (may need a projection step before fusion is well-formed; author's
  job to check at design time, same preflight discipline as any other cell).
- Which grounding source is "current best" at dispatch time (WorldTree definitional
  grounding vs whatever supersedes Binder direct-supply by then) -- author picks the
  live grounding direction at dispatch, not this stub.

## Dispatch trigger
Consolidation/grounding pipeline frees a slot (per Director's active-program
sequencing) -- NOT before. This stub is the durability artifact so the idea survives
until then; it is intentionally NOT a queue_add.sh command (no cell exists yet to
dispatch).
