# Prereg — wave14_realtime_inference_learning_v1_rerun

**Date**: 2026-05-24
**Author**: orchestrator exp_dev role (inline)
**Cap_map cell**: K5 Real-time learning during inference — KILLER Tier 2

## Trigger

v190 cap_map V10 LABEL-OVER-CLAIM detection: v1 FULL reported bpc_online=0.000 / bpc_frozen=0.000 / delta=0.000 — structurally implausible (smoke gave bpc_online=3.762 / bpc_frozen=3.834 in normal range). Root cause: corpus_a length 48512 bytes, pretrain_bytes=50000 + T_infer=4000 = 54000 needed -> infer_corpus is empty -> n_predictions=0 -> bpc = 0/max(0,1) = 0 across all seeds; metric collapse not a substrate-capability reading.

This rerun caps pretrain_bytes against the live corpus length and adds hard assertions so the instrumentation bug class fails LOUDLY (assertion) instead of silently (zero metric) if it recurs.

## Mechanism

Identical to v1: offline pre-train W on corpus_a slice; held-out slice runs through two W variants (frozen + online delta-rule update per batch); compare mean BPC. Bands identical to v1.

Only changes:
- pretrain_bytes capped at min(40000, corpus_len - T_infer - 200) — explicit anti-bug.
- Hard `assert` statements on infer_idx non-empty and bpc_frozen, bpc_online in (0, 9) range.
- Renamed config field `pretrain_bytes_requested` and `corpus_len` for audit.

## Falsifier statements (unchanged from v1)

| Band | Threshold | Interpretation |
|---|---|---|
| **HARD-PASS** | mean (bpc_online - bpc_frozen) <= -0.05 bits/char across 3 seeds | Online updates LIFT capability; K5 substrate-compatible; K5 ⚪ -> ✅ track |
| **HARD-FAIL** | mean (bpc_online - bpc_frozen) >= +0.05 bits/char | Online updates DEGRADE prediction; K5 incompatible |
| **MIDDLE** | intermediate | Pipeline viable but no capability uplift |

## Substrate-product reading

- HARD-PASS: substrate supports real-time learning during inference; portfolio gains new ✅ row in KILLER T2.
- HARD-FAIL: online updates hurt; K5 closed-FAIL.
- MIDDLE: pipeline runs but online updates have no measurable effect.

## Discipline citations

- per [[feedback-no-smoke]]: bands falsifiable BEFORE running.
- per [[feedback-verdict-msg-honest-reread]]: v190 V10 LABEL-OVER-CLAIM 3rd labeled-vs-honest entry this session resolved by this rerun.

## Smoke

PASSED (smoke at N=512: bpc_frozen=3.834 bpc_online=3.762 delta=-0.072 -> REALTIME_INFERENCE_HARD_PASS). Smoke now produces real values (matches old smoke; instrumentation bug was FULL-only); demonstrates the fix works at smoke scale.
