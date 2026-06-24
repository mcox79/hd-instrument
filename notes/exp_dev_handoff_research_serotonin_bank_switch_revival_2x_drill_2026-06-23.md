# exp_dev hand-off — research: serotonin bank-switch HARD_FAIL revival (2x drill)

**Filed:** 2026-06-23 by research sub-agent (after 2x revival drill on Skunkworks batch VET TARGET 2).

**Trigger:** `notes/research_serotonin_bank_switch_revival_2x_drill_2026-06-23.md` HEADLINE recommends K=2 production-N rescue cell as highest-yield discriminator (P_deflated=0.55 HARD_PASS) against the `substrate_serotonin_mode_switch_bank_select_LM_v1` HARD_FAIL.

**Pause state:** check `data/orchestrator_paused.flag` before dispatch.

**Per [[feedback-no-experiment-design-in-prompts]]:** this hand-off names ANCHORS + POINTERS + PRE-REG BANDS only. exp_dev designs ALL of: N_TRAIN, V, seed count details, lambda-grid exact values, encoder seed strategy, smoke profile, FULL profile parameters, queue choice. Research provides the FAILURE-MODE analysis, the CANDIDATE RANK ORDER, and the PRE-REG BANDS (not the numerical implementation parameters).

---

## Anchor candidates (rank-ordered)

### Rank 1 (HIGHEST yield, dispatch FIRST)

**Anchor:** `substrate_k2_bank_param_matched_LM_v1`

- **Anchor pointer:** `notes/research_serotonin_bank_switch_revival_2x_drill_2026-06-23.md` Rank-1 design section.
- **Substrate-product reading:** Direct K=2 reproduction of K-bank shotgun finding at production scale. If HARD_PASS, K=2 bank architecture becomes a NEW substrate-as-LM lift candidate (orthogonal to fair_harness lambda-mix, sparse-bipolar bundle, lock-in amp). Closes 10-20% of the 1.13-bit text8 bigram gap.
- **Tier hint:** Cheap — likely Remote CPU OR Local CPU. ~15-30 min wall at production N=8192 V=4000 N_TRAIN=100k with 3 seeds (matching serotonin cell's elapsed_s_seed).
- **Why now:** The cleanest single test of failure mode (A) [K=4 BEYOND optimum] + (C) [param-matched too-small per-bank]. Substrate has DIRECT measurement (K-bank shotgun K=2 +1.07 BPC peak); production-scale confirmation is the load-bearing missing piece.
- **Pre-reg bands (research-provided; exp_dev must include):**
  - HARD_PASS: feature-gated K=2 lift ≥ +0.10 BPC vs single-bank baseline; cv ≤ 0.05.
  - CHAIN_GRADE_BONUS: lift ≥ +0.20 AND beats K=2 random-routing by ≥ +0.05.
  - MIDDLE_BAND: lift ∈ [+0.03, +0.10].
  - HARD_FAIL: lift ≤ +0.03 (K-bank shotgun was a smoke artifact; bank class closes).
  - **C7 INSTR_SUSPECT guard:** if best_lambda=0.0 across all arms AND raw_bpc_at_T1_L1 close to vocab entropy (~11.97 bits at V=4000), tag INSTRUMENTATION_SUSPECT, NOT HARD_FAIL. Expand LAMBDA_GRID to include {0.02, 0.05, 0.07} per Skunkworks batch VET batch C7 finding.
  - **Fix #28 per-arm reporting mandatory:** raw_bpc_at_T1_L1, best_T, best_lambda, top1, mrr per arm.
- **4 arms required:** ARM_UNIGRAM, ARM_SINGLE_BANK (8192), ARM_K2_PARAM_MATCHED_RANDOM_SELECT (2×4096), ARM_K2_PARAM_MATCHED_FEATURE_GATED (2×4096 with Hebbian utility-gate, EXACTLY the serotonin cell's gate_W).

### Rank 2 (dispatch only IF Rank-1 HARD_PASSES)

**Anchor:** `substrate_k2_bank_additive_not_param_matched_LM_v1`

- **Anchor pointer:** `notes/research_serotonin_bank_switch_revival_2x_drill_2026-06-23.md` Rank-2 design section.
- **Substrate-product reading:** Test failure mode (C) directly. Brain doesn't param-match — adds banks rather than shrinking. K=2 at 8192 EACH (= 16384 total) tests whether the "lift" from K-bank architecture is real or just parameters.
- **Tier hint:** Likely Remote CPU OR GPU; ~30 min wall (2x memory/compute vs Rank-1).
- **Why now:** Discriminates "architecture lifts" from "extra parameters lift." Required arm: ARM_SINGLE_BANK_DOUBLE (N=16384 single, compute-matched control for ARM_K2_ADDITIVE).
- **Pre-reg bands (research-provided):**
  - HARD_PASS: K2-additive lift ≥ +0.15 BPC vs single-bank N=16384; cv ≤ 0.05.
  - CHAIN_GRADE_BONUS: lift ≥ +0.25 AND single-bank-double itself ≤ +0.05 lift over single-bank N=8192.
  - HARD_FAIL: K2-additive ≤ single-double + 0.03.

### Rank 3 (dispatch IF Rank-1 HARD_FAILS OR in parallel with Rank-2 if Rank-1 MIDDLE_BAND)

**Anchor:** `substrate_k2_bank_soft_mixture_LM_v1`

- **Anchor pointer:** `notes/research_serotonin_bank_switch_revival_2x_drill_2026-06-23.md` Rank-3 design section.
- **Substrate-product reading:** Test failure mode (B) directly. Replace hard argmax-routing with soft mixture-of-experts. Discriminates routing-failure from bank-count failure.
- **Tier hint:** Cheap; ~15 min CPU. Can co-ship with Rank-1 as an 8-arm bundle if exp_dev's cell-bundle design supports it.
- **Why now:** Brain prior (eLife 2020: 5-HT is multiplicative gain, NOT discrete selection) + mixture-of-experts literature (Shazeer 2017: soft top-k beats hard argmax) both favor soft-mixing. The 0.0135 lift over random in current cell IS evidence the gate carries some signal that hard-routing throws away.
- **4 arms:** ARM_UNIGRAM, ARM_SINGLE_BANK, ARM_K2_HARD_GATED (param-matched 2×4096, reproduces serotonin mechanism at K=2), ARM_K2_SOFT_GATED (param-matched 2×4096, SOFT mixture: `logits = sum_k softmax(gate)_k · (src @ W_k)`).
- **Pre-reg bands:**
  - HARD_PASS: soft-K2 lift ≥ +0.10 vs single-bank AND ≥ +0.05 vs hard-K2.
  - CHAIN_GRADE_BONUS: lift ≥ +0.20 AND ≥ +0.10 vs hard-K2 (soft-mixing is load-bearing).
  - HARD_FAIL: soft-K2 ≤ hard-K2 + 0.03.

---

## Context pointers (file paths, not summaries)

- `notes/research_serotonin_bank_switch_revival_2x_drill_2026-06-23.md` — THIS drill (full failure-mode analysis + 19 citations).
- `notes/skunkworks_to_all_BATCH_VET_4_recent_negatives_2026-06-23.md` TARGET 2 — Skunkworks GENUINE_FAILURE classification + C7 calibration-collapse pattern documented in TARGETS 3/4.
- `notes/shotgun_smoke_K_bank_count_sweep_2026-06-23.md` — K-bank shotgun K=2 +1.07 BPC peak measurement.
- `data/exp_substrate_serotonin_mode_switch_bank_select_LM_v1/metrics.json` — the HARD_FAIL itself; clean per-arm metrics (NOT calibration-collapsed).
- `experiments/exp_substrate_serotonin_mode_switch_bank_select_LM_v1.py` — gate_W Hebbian utility-trained, argmax-routing implementation to mirror in Rank-1.
- `data/exp_substrate_k_module_heterogeneous_compose_LM_v1/metrics.json` — C7 calibration-collapse cautionary tale (must guard against).
- `data/exp_fair_harness_substrate_as_lm_v1/metrics.json` — production single-bank baseline 7.3065 BPC.
- `notes/substrate_mine_modulator_gain_experiments_inventory_2026-06-23.md` — GAP #3 inventory entry.
- `data/text8_cache/text8.txt` — corpus (already in cell at line 87).

---

## Contract section

**Required-by-research (exp_dev MUST include):**
1. Pre-reg bands as specified above per rank.
2. C7 INSTR_SUSPECT guard (LAMBDA_GRID includes {0.02, 0.05, 0.07}; tag INSTRUMENTATION_SUSPECT if all arms collapse to best_lambda=0.0).
3. Fix #28 per-arm reporting (raw_bpc_at_T1_L1, best_T, best_lambda, top1, mrr).
4. 4-arm structure as specified per rank.
5. 3 seeds minimum (matches serotonin cell discipline).
6. Encoder: dense bipolar char-trigram (mirror serotonin cell line 201-211) to maintain A/B comparability — DO NOT switch encoder for Rank-1 (encoder change confounds the rescue test).
7. Mandatory instrumentation_selftest at module scope (mirror serotonin cell line 475-554).
8. Per-seed checkpoint via `experiments._seed_checkpoint` (mirror serotonin cell line 81-84).

**Free-for-exp_dev-to-design:**
- All non-pre-reg numerical parameters (exact LAMBDA_GRID values beyond required {0.02, 0.05, 0.07}; TEMP_GRID values; INGEST_CHUNK; RECALL_BATCH).
- Queue choice (Tier A/B/C per `agents/exp_dev.md` Section 0).
- Smoke profile (smoke parameters; the cell author writes the smoke test).
- ETA estimate.
- Cell-author smoke gate (REQUIRED per discipline; per-arm verify before FULL dispatch).
- Verdict synthesizer details.
- Whether Ranks 1+3 ship as 8-arm bundle or separate 4-arm cells (exp_dev's call; research recommends separate for cleaner per-cell pre-reg).

---

## Autonomy declaration

- Research has decided: failure-mode analysis, rank order, pre-reg bands.
- exp_dev decides: ALL implementation details, queue choice, smoke parameters, exact numerical thresholds beyond pre-reg, cell-author bundle structure, ETA.
- Orchestrator decides: dispatch order (Rank-1 first); whether to dispatch Ranks 2 + 3 sequentially or wait for Rank-1 verdict (research recommends WAIT — Rank-1 result determines which of Rank-2/Rank-3 is highest-yield next step).
- Skunkworks owns: post-landing VET (per A5 role separation); MEASURED_MECHANISM vs chain-grade tier-call.

**Estimated total cost (all 3 ranks):** ~1 hour wall on CPU sequential OR ~20 min on GPU parallel. Rank-1 alone is ~15-30 min CPU.

**Dispatch trigger:** Orchestrator pauses-flag clear AND queue has capacity. If paused, defer Rank-1 dispatch and atomize the research finding into Store; rescue cell remains queued in cap_map as the substrate-as-LM K-bank revival lever.
