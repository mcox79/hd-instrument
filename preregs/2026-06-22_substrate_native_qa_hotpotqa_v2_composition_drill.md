# Pre-reg: substrate_native_qa_hotpotqa_v2_composition_drill

**Date (UTC):** 2026-06-22
**Author:** Exp-Dev (per Research 2x-revival drill `notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md`)
**Anchor:** `substrate_native_qa_hotpotqa_v2_composition_drill`
**Script:** `experiments/exp_substrate_native_qa_hotpotqa_v2_composition_drill.py`
**Routing:** `remote_cpu_queue` (post-processing layer on substrate signal collection; numpy-bound; ~2hr wall)
**Run config (FULL):** N_DIM=8192, N_Q=1000, GEN_DEPTH=4, TOP_K=5, SIGMA=0.10, SEEDS=[7,17,23]

---

## Rationale

v1 cell `substrate_native_qa_hotpotqa_v1` HARD_FAIL'd at composed_em=0.010 but the
GENERATION_ONLY arm achieved EM=0.122 (cv=0.004 across 3 seeds, n=1000) = a
substrate-as-LLM-substitute existence proof OBSCURED by mode-aggregation composition
sabotage. Per Research 2x-revival drill (2026-06-22), this v2 tests:

1. **B-axis SCORE FUSION** (alpha-sweep): replace mode aggregation with
   `posterior = alpha * norm(KG_score) + (1-alpha) * norm(gen_visit_count)`.
2. **C-axis CHARACTERIZATION**: 5 CAN-FAIL discriminators of whether the 12.2%
   GENERATION_ONLY signal is real substrate work vs trivial artifact.
3. **HARNESS ANCHOR**: re-run v1's GENERATION_ONLY logic exactly to confirm v1
   invariant before interpreting the new arms.

---

## Arms (11 + 1 harness)

### HARNESS_ANCHOR (CAN-FAIL discriminator -- MUST reproduce v1)

- `GENERATION_ONLY_REPRO` -- exact v1 spec (nearest-entity seed + mode of visited).
  Must reproduce v1 EM within `|delta| <= 0.005`. If broken, v2 verdict is
  UNINTERPRETABLE (HARD_FAIL).

### B SCORE-FUSION (6 alpha points)

- `COMPOSED_alpha_0.0` -- generation-only baseline
- `COMPOSED_alpha_0.2`
- `COMPOSED_alpha_0.4`
- `COMPOSED_alpha_0.6`
- `COMPOSED_alpha_0.8`
- `COMPOSED_alpha_1.0` -- retrieval-only baseline

Each computes `posterior = alpha * norm_per_row(KG_scores) + (1-alpha) * norm_per_row(gen_visit_counts)`
where `norm_per_row` is per-row min-max [0,1]. argmax over `posterior` = prediction.

### C CHARACTERIZATION (5 CAN-FAIL gates)

- `FREQ_BIAS`: restrict prediction to top-100 most-frequent gold-answer entities.
  If EM stays near 12%, generation rides answer-frequency bias.
- `SUBSTRING_OVERLAP`: count rate of `pred_string in question_string` + EM
  conditioned on each.
- `QUESTION_TYPE_SPLIT`: per-type EM (HotpotQA `bridge` vs `comparison`).
- `START_ENTITY_LEAK`: count rate(pred == nearest-entity-seed) +
  EM | start_entity in/not-in supporting_facts.
- `RANDOM_SEED_CONTROL`: same generation logic but RANDOM start entity. If EM
  stays ~12%, generation is uniform-prior emission not seed-conditioned.

---

## HARD bands

### HARD_PASS (composition fix CONFIRMED -- chain-grade-positive)

ALL of:
- `best_alpha_COMPOSED_em >= 0.20`
- `(best_alpha_COMPOSED_em - GENERATION_ONLY_REPRO_em) >= +0.05` (composition lift)
- `|GENERATION_ONLY_REPRO_em - 0.122| <= 0.005` (harness reproduces v1)
- `n_llm_calls == 0` (substrate-only-decode gate)
- `cv across 3 seeds for best-alpha COMPOSED <= 0.10`

### HARD_FAIL

ANY of:
- `best_alpha_COMPOSED_em <= GENERATION_ONLY_REPRO_em` (composition still no lift)
- `|GENERATION_ONLY_REPRO_em - 0.122| > 0.005` (harness REPRODUCTION violated --
  v1 invariant broken, drill verdict uninterpretable)
- `n_llm_calls > 0`

### MIDDLE_BAND

In between (e.g. composition lifts but `best_em < 0.20`, or cv > 0.10).

---

## Discriminator (Fix #16)

- **Mechanism-discriminating bands**: HARD_PASS requires BOTH score-fusion lift
  AND harness reproduction. A passing cell cannot be explained by the
  generation-only signal alone OR by a corrupted v1 invariant.
- **CAN-FAIL gates** (built into ARM SET):
  - `GENERATION_ONLY_REPRO` MUST reproduce v1 (harness invariant)
  - `RANDOM_SEED_CONTROL` MUST drop EM substantially (per drill prediction: 0%
    with random seed; observation > 5% would be middle-band)
  - `SUBSTRING_OVERLAP` MUST stay below 80% (else it's question-rebroadcast)
  - `FREQ_BIAS` MUST drop EM substantially from gen-only (else freq bias artifact)
  - `START_ENTITY_LEAK` separates seed-rebroadcast from genuine generation expansion

---

## Substrate-only-decode gate

- `n_llm_calls == 0` enforced via `_LLM_CALL_COUNTER` (asserted at exit).
- Encoder: char-trigram (no MiniLM); preserves v1's encoder regime so the
  harness reproduction is meaningful.

---

## Routing + wall budget

- **Queue:** `remote_cpu_queue` (matmul + per-question loops; numpy-bound; CPU is
  the right substrate for this; GPU not required).
- **Wall estimate:** 3 seeds * (1 harness pass ~ 200s + signal-collect ~ 400s
  for 2x rollouts + B/C arms ~ 0s post-processing) ~= 1800s/seed * 3 = ~90min,
  + 30min slack = ~2hr.
- **Timeout:** 10800s (3hr).
- **Smoke:** N_DIM=2048, N_Q=50, 1 seed (~30-60s wall expected). Smoke uses loose
  HARNESS_TOL=0.10 (sqrt(1/50)*0.122 ~ 0.05 inherent variance at N=50); FULL uses
  tight HARNESS_TOL=0.005 (matches v1 cv=0.004). Smoke is gate-only -- must run
  end-to-end + produce metrics + all arms emit -- not band-load-bearing.

---

## Pre-reg honesty (P_deflated)

Per Research drill: P(any axis lands chain-grade evidence) = 0.50 (deflated
0.15-0.25 from naive; capped at 0.50 per novel-synthesis discipline).

- Naive P(B PASS = score-fusion adds lift) ~ 0.45.
- Deflated P(B PASS) = 0.25-0.30 (retrieval baseline at 1.9% so low that score
  fusion may collapse to alpha~0 = gen-only).
- Naive P(C-positive consistent characterization) ~ 0.55.
- Deflated P(C-positive ALL three negatives) = 0.35-0.40.

---

## Output (one line for spawn contract)

`substrate_native_qa_hotpotqa_v2_composition_drill dispatched to remote_cpu: spawn=<id>, cell=<commit>, smoke=<verdict>, est_wall=<min>, best_alpha_smoke=<value>`
