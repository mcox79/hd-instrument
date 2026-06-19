# exp_dev hand-off: R-PRIME-3 task-pair geometry sweep

**Filed:** 2026-05-24 by orchestrator (v192 paired commit, Ship 1).
**Status:** READY for exp_dev pickup. Pre-reg + script + queue entry owned by exp_dev.

---

## WHAT

Sweep Bet B retention across deliberately-spaced task-pair representational distances. Probe whether **task-pair geometry** (measured as mean cosine between task-A and task-B representations) is the dominant axis for Bet B retention variation.

## WHY

The existing-data analysis filed at `notes/research_existing_data_analyses_2026-05-24.md` (v192 V4) surfaced a **35% retA drop** between same-corpus (retA=0.954 base Kovacs v9) and diff-corpus (retA=0.600 multitask_diff_corpus) Bet B variants. This is the **largest effect across all Bet B variants tested** — larger than any structural ablation (Ablation A=0.821, Ablation B replay-only=0.846, EWC=0.736 across lambda sweep).

R-PRIME-3 in `notes/research_R_PRIME_directions_2026-05-24.md` predicts retention depends on task-pair representational distance. With existing data anchoring two endpoints (same-corpus 0.954, diff-corpus 0.600), 4 intermediate points would directly test whether retention is monotone in cosine distance with the predicted slope.

## CONTEXT POINTERS

- `notes/research_R_PRIME_directions_2026-05-24.md` — full R-PRIME-3 spec
- `notes/research_3_capability_deep_agenda_2026-05-24.md` — Capability 2 (multi-task retention) priorities
- `notes/research_existing_data_analyses_2026-05-24.md` — 35% retA drop motivating this ship; cluster-structure finding
- `notes/substrate_capability_map.md` v192 block — Bet B retention 🟡 PARTIAL with 8 rehab axes
- `exp_wave14_betB_multitask_diff_corpus_v1.py` — existing diff-corpus implementation (likely starting point)
- `exp_wave14_betB_4stage_continual_v1.py` — existing 4-stage continual (alt starting point)
- Cap_map v190 Bet B variants table (lines varies; grep "retA=" notes/substrate_capability_map.md v190)

## CONTRACT (deliverable shape)

- exp_dev decides: corpus pairs, M, K, N, seed count, queue choice, ETA.
- exp_dev decides: cosine measurement method (mean over context vectors, mean over codebook, joint-binding measure — pick one and document).
- exp_dev decides: HARD-PASS / HARD-FAIL / MIDDLE thresholds for the SLOPE of retA vs cosine (not just retA itself; the slope IS the mechanism signal).
- Pre-reg file in `notes/preregs/` ahead of FULL run.
- Smoke first, FULL on smoke clearance.
- 5-seed FULL minimum.

## AUTONOMY DECLARATION

You decide all design parameters: task-pair set, cosine measurement, threshold bounds for slope, queue placement, seed count, ETA. Do NOT ship parameter grids designed in this hand-off — design them yourself.

## DISCIPLINE CITATIONS

- per [[feedback-no-experiment-design-in-prompts]] — this hand-off names task SHAPE, not parameters
- per [[feedback-pipeline-pacing]] — fill CPU/GPU queue depth >= 1 at all times
- per [[feedback-verify-implementations]] — match cosine measurement to literature anchor cited in pre-reg
- per [[feedback-no-smoke]] — honest reread of label=msg=data after FULL; pre-reg the slope-threshold bands explicitly

---
BULK-ARCHIVED 2026-06-01: orchestrator-filed handoff to exp_dev; acted on (cap_map v312+ reflects evidence of completed work); bulk-archived per dashboard inbox-clearance Path A pattern.
