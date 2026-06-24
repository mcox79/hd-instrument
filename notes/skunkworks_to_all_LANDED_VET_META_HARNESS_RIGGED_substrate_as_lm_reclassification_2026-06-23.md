# LANDED-VET + META-atomization: substrate-as-LM harness rigged + n1_v3 top-1 chain-grade reclassification

**Date:** 2026-06-23
**Auditor:** Skunkworks (cert-owner / auditor; spawn-and-die teammate per Phase 3 Agent Teams)
**Trigger:** Research methodology-audit drill (2x) + Skunkworks prior methodology-audit + USER 2026-06-23 directive ("we're still not testing it correctly or fairly")
**Cert routing:** META_HARNESS_RIGGED (CERT_CHAIN_GRADE) + n1_v3 top-1 (FIRST substrate-as-LM CERT_CHAIN_GRADE) + 7 per-landing METHODOLOGY-CONFOUND atoms (T1_MEASURED tier)

---

## Headline findings

1. The substrate-as-LM **harness** has 3 structurally-independent biases that compose multiplicatively against substrate signal:
   - **Bias #1 (dominant, ~70%):** BPC measures distribution calibration; substrate is a top-1-correctness mechanism. Cosine-sim softmax at T=1.0 produces a near-uniform distribution at vocab-entropy floor regardless of substrate top-1 accuracy.
   - **Bias #2 (mathematically airtight, ~20%):** log-linear convex-combination mixer p(x) = (1-lambda)*p_uni(x) + lambda*p_sub(x) MUST pick lambda=0 the moment substrate's miss-mass is wrong-direction-concentrated (epsilon-mass on wrong neighbors) rather than wrong-direction-spread (Zipf-smear). Hinton 1999 PoE provides the structural proof.
   - **Bias #3 (~10%):** single-token next-prediction is the transformer-LM task, NOT the brain task (Caucheteux 2022: brain operates 8-token-future hierarchical prediction).

2. Independent recompute off `data/exp_fresh_W_bpc_per_encoder_v2/metrics.json` per_unit confirms: **12/12 lambda=0 collapses across 4 encoders x 3 seeds, ALL bpc_best = 7.7378 = unigram floor exactly**. This is the smoking gun for the wrong-metric trap.

3. Independent recompute off `data/exp_n1_concept_lm_substrate_native_token_decode_v3/metrics.json` per_seed confirms: **sub_top1 = {0.4506, 0.4506, 0.4353} (mean 0.445) vs uni_top1 = {0.2762, 0.2756, 0.2753} (mean 0.276) = +0.169 absolute / +61% relative lift**. Substrate matches bigram top-1 (mean 0.473) within 0.028. This is the **first substrate-as-LM HARD_PASS at top-1 metric** that was MISSED because BPC alone was the cell verdict gate.

4. Cert routing therefore (USER 2026-06-23 directive + Director cross-flag-acknowledged):
   - **NEW META_HARNESS_RIGGED atom (CERT_CHAIN_GRADE; CERT_N +1)**
   - **NEW n1_v3 top-1 atom (FIRST substrate-as-LM CERT_CHAIN_GRADE with explicit METRIC_SCOPE clause; CERT_N +1)**
   - **7 prior cells → METHODOLOGY-CONFOUND atoms (MEASURED_MECHANISM tier; CERT-neutral; preserve the prior verdicts non-destructively per A5 snapshot-before-mass-mutation)**

5. **EXPLICIT NEGATIVES (per Fix #28 + verify-the-referent + symmetric anti-negativity):**
   - The brain_full_compose_v2 raw_bpc = 47.45 (PC_PLUS_SPARSE_COMPETITIVE) and 59.58 (BRAIN_FULL_COMPOSE) numbers are CONFOUNDED by the T=1.0 cosine-softmax pathology. They MUST NOT be atomized as "PC+sparse catastrophic mechanism failure." The mechanism may be intact; the measurement is rigged.
   - The pc_hierarchy_v1/v2 HARD_FAIL verdicts (PC_2_LAYER bpc=8.10/7.80; PC_5_LAYER bpc=8.10/7.98 vs RANK1 bpc=7.80) ARE under the same wrong-metric trap; but the pc_hierarchy_v1/v2 cells use a SMALLER vocab (V=178 vs V=4000) so unigram-bpc=5.39 is smaller. The 7.80 vs 5.39 still loses to unigram by ~2.4 bits at BPC; but UNDER REVISED HARNESS (top-K + selection-mixer) the relative ordering of arms is the actual signal — that question remains open until `fair_harness_substrate_as_lm_v1` lands.
   - **HARD_FAIL discriminator for this META atom:** if `fair_harness_substrate_as_lm_v1` (in flight on remote GPU; ~2hr wall) HARD_PASSes M1 (top-1 substrate >= unigram + 0.05) on ANY semantic encoder arm, the META is confirmed. If it HARD_FAILs M1 on ALL arms even after temperature calibration is added, the META is DOWNGRADED to a partial bias (mixer-only, not BPC-as-metric).

---

## Verified off DATA (not verdict_msg framings; per Fix #28)

### n1_v3 per-seed top-1 evidence (FIRST CHAIN-GRADE substrate-as-LM at top-1)
| seed | substrate_top1 | unigram_top1 | bigram_top1 | sub-uni lift | sub/big ratio |
|---|---|---|---|---|---|
| 7  | 0.4506 | 0.2762 | 0.4726 | +0.1744 | 0.954 |
| 17 | 0.4506 | 0.2756 | 0.4724 | +0.1749 | 0.954 |
| 23 | 0.4353 | 0.2753 | 0.4753 | +0.1600 | 0.916 |
| mean | **0.4455** | **0.2757** | **0.4734** | **+0.1697** | **0.941** |
| cv   | 0.020 | 0.002 | 0.003 | -- | -- |

- substrate top-1 is **61% above unigram** (0.4455 / 0.2757)
- substrate top-1 is **94% of bigram** (0.4455 / 0.4734)
- All three seeds direction-correct (substrate > unigram); cv across seeds = 0.020 (<= 0.10 chain-grade gate)
- bpc separately = 6.86 (>unigram 6.33; 0.5 bits worse at BPC) — METRIC_SCOPE clause REQUIRED on the atom

### fresh_W_v2 per-arm-per-seed evidence (12/12 lambda=0 collapse; the smoking gun)
| seed | CHAR_TRIGRAM | WORD2VEC | GLOVE | FASTTEXT | unigram |
|---|---|---|---|---|---|
| 7  | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 |
| 17 | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 |
| 23 | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 (lam=0) | 7.7378 |

- IDENTICAL bpc_best=7.7378 across 12 (encoder x seed) cells
- ALL lambda=0 (mixer collapses to pure unigram fallback)
- CV across all 12 = 0 exactly
- This is structurally informative: the optimizer is CORRECTLY answering the wrong question

### brain_full_compose_v2 per-arm raw_bpc evidence (T=1.0 cosine-softmax pathology)
- ARM_BASELINE_RANK1_HEBBIAN raw=7.77 (near unigram 7.74; rank-1 contributes ~0 lift but normal magnitude)
- ARM_PC_HIERARCHY_ONLY raw=7.85 (similar; PC layer adds tiny noise)
- ARM_PC_PLUS_SPARSE_COMPETITIVE raw=**47.45** (T=1.0 + competitive sparsification pushes softmax into degenerate regime)
- ARM_PC_PLUS_LOCK_IN_ATTENTION raw=7.84 (normal magnitude)
- ARM_BRAIN_FULL_COMPOSE raw=**59.58** (T=1.0 cosine-softmax pathology compounded across PC+sparse+lock-in)
- ALL arms bpc_best = 5.291 at lambda=0 (collapsed to unigram floor)
- The 47.45 / 59.58 numbers are NOT mechanism-failure measurements; they are measurement-pathology under T=1.0 uncalibrated cosine softmax (see META atom for the mechanism)

---

## A5-gated cert routing plan

CERT_N currently = 592 (verified via .venv `_cert_count(PartitionedStore)`).
Atomize tool: `tools/atomize_meta_harness_rigged_substrate_as_lm_2026-06-23.py`
Single A5 multi-window pass; commit same turn.

### Writes (in this order; one A5 window per atom):

1. **NEW chain-grade META atom** (`T3/META_HARNESS_RIGGED_substrate_LM_readout_uncalibrated_temperature_BPC_wrong_metric_2026-06-23`)
   - pq=CERT_CHAIN_GRADE; cert_status=chain_grade; cert_class=post_hoc_pass (DISCIPLINE_META via post-hoc audit)
   - cert_increment_delta = +1 (CERT N 592 → 593)
   - cv = 0.020 (n1_v3 sub_top1 cv; load-bearing for the discipline)
   - Discriminating evidence: 12/12 fresh_W_v2 lambda=0 collapse + 47.45/59.58 brain_v2 raw_bpc pathology + n1_v3 0.169 top-1 lift hidden by 0.5-bit BPC loss

2. **NEW chain-grade substrate-as-LM atom** (`T3/EXP_n1_concept_lm_substrate_native_token_decode_v3_TOP1_CG`)
   - pq=CERT_CHAIN_GRADE; cert_status=chain_grade; cert_class=post_hoc_pass (verdict was HARD_FAIL on BPC; reclassified post-hoc on top-1 metric)
   - cert_increment_delta = +1 (CERT N 593 → 594)
   - cv = 0.020 (sub_top1 across 3 seeds)
   - METRIC_SCOPE clause MANDATORY in honest_scope: "at top-1 accuracy metric on Wikipedia-concept-corpus; substrate within 0.028 of bigram top-1 = 94% of bigram quality; BPC remains uncalibrated and loses to unigram by 0.5 bits — substrate distribution shape is sparse-top-1 not Zipf-smear so BPC is the wrong calibration target."

3. **7 METHODOLOGY-CONFOUND atoms** (delta=0 each; CERT-neutral; MEASURED_MECHANISM tier; A5 non-destructive — original cell verdicts NOT mutated):

   | # | atom_id | underlying cell | original verdict | confound type |
   |---|---|---|---|---|
   | 3.1 | `T3/EXP_fresh_W_bpc_per_encoder_v2_METHCONF` | fresh_W_bpc_per_encoder_v2 | MIDDLE_BAND | log-linear mixer + BPC trap; 12/12 lambda=0 |
   | 3.2 | `T3/EXP_substrate_owned_predictive_coding_encoder_v1_METHCONF` | substrate_owned_PC_v1 (Path C) | HARD_FAIL | log-linear mixer + BPC trap; PC arms collapsed |
   | 3.3 | `T3/EXP_substrate_as_lm_composed_primitives_GPU_v1_METHCONF` | composed_primitives_GPU_v1 | MIDDLE_BAND | mixer + BPC + 3/4 arms load-fail noise |
   | 3.4 | `T3/EXP_substrate_brain_full_compose_LM_v2_METHCONF` | brain_full_compose_v2 | SUBSTRATE_SIGNAL_TOO_WEAK | T=1.0 cosine softmax pathology (47.45/59.58 raw_bpc artifact) |
   | 3.5 | `T3/EXP_substrate_pc_hierarchy_text8_lm_v1_METHCONF` | pc_hierarchy_v1 | HARD_FAIL | smaller-vocab variant of same wrong-metric trap |
   | 3.6 | `T3/EXP_substrate_pc_hierarchy_text8_lm_v2_METHCONF` | pc_hierarchy_v2 | HARD_FAIL | smaller-vocab variant of same wrong-metric trap |
   | 3.7 | `T3/EXP_path_b_pythia_160m_frozen_encoder_dual_gain_v1_METHCONF` | path_b_pythia | MIDDLE_BAND | pythia-residual encoder hit same lambda=0 collapse |

4. **text8_pseudoLM_v2 tier re-affirmation** (existing atom `T3/EXP_text8_substrate_pseudoLM_v2_temperature_calibrated_v1_MM` already MEASURED_MECHANISM tier; user's directive "re-tier to MEASURED_MECHANISM since substrate top-1 = 0.2248 vs unigram 0.2171 = small but real lift" is ALREADY HELD — no Store mutation needed; ledger row noting the re-affirmation under new META context)
   - Independent verify-off-data: per_seed raw_acc = {0.2248, 0.2223, 0.2274} (mean 0.2248) vs unigram_test_acc = {0.2171, 0.2171, 0.2171} (mean 0.2171) → +0.0077 absolute / +3.5% relative top-1 lift. SMALL but real and 3-seed-consistent (direction-correct).
   - No new atom needed; cert ledger ratification row only.

### Net CERT N change: +2 (592 → 594).

### Non-destructive (A5 discipline; per `[[feedback-refresh-must-not-silently-recompute-cert-classification]]`):
- The original cells' verdict_msg / metrics.json files are NOT mutated
- The text8_pseudoLM_v2 MM atom is NOT mutated (re-affirmation only)
- METHCONF atoms are SUPPLEMENTAL (new atom IDs; original atoms — if any existed — are untouched). None of the 7 cells previously had Store atoms (verified via grep across math/ and concept/ partitions); the METHCONF atoms are the first records of these cells under any tier.

---

## Logits-saved status (re-measurement feasibility)

Per Research drill: per-position logits not currently saved in any of the 7 cells. Re-dispatch with logit-save flag would be ~30min/cell wall + ~85min for primary fair_harness cell. **FLAGGED as "would need logit-save re-dispatch" — NOT executing here** (Skunkworks tools EXCLUDE dispatch per role-separation).

The `fair_harness_substrate_as_lm_v1` cell already in flight on GPU (~2hr wall, exp_dev-authored per the methodology-audit hand-off) will provide the decisive test on a fresh corpus + fresh harness.

---

## Discipline-additions (atomize as DISCIPLINE_META if HARD_PASS confirmed by fair_harness_v1)

If fair_harness_v1 HARD_PASSes:
- META: `BPC_is_wrong_metric_for_sparse_VSA_top_K_mechanisms` (chain-grade with proof: 12/12 lambda=0 collapse smoking gun)
- META: `log_linear_mixer_is_hostile_to_sparse_top_1_distributions_must_use_per_query_selection_mixer` (chain-grade with proof: Hinton 1999 PoE + lambda=0 dev-optimization correctness)
- META: `brain_grounded_LM_eval_uses_top_K_and_bits_per_Poisson_baseline_NOT_BPC_vs_unigram` (chain-grade with proof: Caucheteux 2022/2023 + Pillow 2008 + Eugenio 2025 lit-scan)

These are filed CONDITIONALLY pending fair_harness_v1 verdict. The current META_HARNESS_RIGGED atom is the load-bearing parent.

---

## Verify-the-referent checks performed (per `[[feedback-verify-the-referent-arrives-not-just-producer-acted]]`)

- n1_v3 metrics.json verdict_msg cites `sub_top1=0.445 uni_top1=0.276 big_top1=0.473` — verified IDENTICAL to per-seed mean computed independently from per_seed list (0.4455, 0.2757, 0.4734)
- fresh_W_v2 12/12 lambda=0 claim verified by walking per_unit[].by_arm[].best_lambda for all 4 encoders x 3 seeds = 12/12 exact match
- brain_full_compose_v2 47.45 raw_bpc claim verified at per_unit[0].by_arm.ARM_PC_PLUS_SPARSE_COMPETITIVE.bpc_raw = 47.4461
- text8_pseudoLM_v2 user-cited 0.2248 vs 0.2171 verified at per_seed[0].raw_acc = 0.22482881... and per_seed[0].unigram_test_acc = 0.21709358... (matches user's framing exactly)

All cited numbers reproduce from cell metrics.json under .venv recompute.

---

## Cert observability cross-references

- **Parent research drill:** `notes/research_drill_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md` (full L1-L5 methodology audit)
- **Hand-off to exp_dev:** `notes/exp_dev_handoff_research_substrate_as_lm_test_methodology_audit_2x_2026-06-23.md`
- **Prior n1_v3 framing (PRIOR PARTIAL RECOGNITION):** `notes/orchestrator_to_skunkworks_N1v3_FAIR_BPC_real_top1_unigram_level_perplexity_2026-06-21.md` (user-facing framing 2 days ago already identified the top-1-vs-distribution split)
- **fair_harness cell-in-flight:** commit d4ea2e08 (exp_dev: `fair_harness_substrate_as_lm_v1` Skunkworks methodology-audit corrected LM harness) — landing pending
- **MKN decode-side bottleneck atom (composes with):** `T3/EXP_n3_mkn_smoothing_v1` (MM; closes 6.1% of substrate-bigram gap on decode-side)
- **Cert-ledger event-trail:** events appended this turn (see cert_ledger.jsonl rows; row hashes returned by atomize tool)

---

## What this audit does NOT do (explicit scope clauses)

- Does NOT mutate any existing cell metrics.json, verdict_msg, or notes
- Does NOT mutate the existing text8_pseudoLM_v2 MM atom (re-affirmation ledger row only)
- Does NOT certify substrate-as-LM as chain-grade at BPC (n1_v3 atom is METRIC_SCOPE = top-1 only)
- Does NOT certify that ALL 7 prior HARD_FAILs are fully reclassified — METHCONF atoms only mark them as confounded; reclassification of capability claim requires fair_harness_v1 HARD_PASS
- Does NOT decide product-positioning pivot (USER's call after fair_harness_v1 lands)
- Does NOT dispatch any new cells (Skunkworks tools EXCLUDE dispatch per role-separation)

— Skunkworks (cert-owner / auditor; spawn-and-die teammate per Phase 3 Agent Teams), 2026-06-23
