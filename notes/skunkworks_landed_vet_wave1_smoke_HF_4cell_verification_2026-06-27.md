# Skunkworks LANDED-VET: Wave 1 SMOKE_HARD_FAIL 4-cell verify-off-data audit

**Date:** 2026-06-27 evening
**Trigger:** USER directive 2026-06-27 ~15:00 PDT - skunktest every negative for verification, 2x verified negatives
**Method:** Per Fix #28 / META_RULE_T - read raw per-arm metrics.json; verify cited numbers reproduce; cross-check source code where framing claims a specific structural cause
**Atomization commit:** `ff601896`
**Store state pre-audit:** 177449 atoms (corrupted - see Store-repair section)
**Store state post-audit:** 177454 atoms (+5 atoms, instance 244-248)

## One-line verdicts

| Cell | Verdict | 2x-drill? | Atom |
|---|---|---|---|
| `exp_pfc_controller_per_step_operator_select_v1_smoke` | TEST_DESIGN_CONFIRMED | NO (pfc_softmax_v2 already HARD_PASS) | inst 244 |
| `exp_multi_readout_fisher_importance_v1_smoke` | TEST_DESIGN_CONFIRMED (UNDERSAMPLED_SMOKE) | NO (lock_in_amp_pca_readout_fisher_v1 in flight) | inst 245 |
| `exp_btsp_binary_synapse_one_shot_v1_smoke` | FIX_28_HALLUCINATED_HEADLINE (cert-owner OVERRIDE) | NO (v2_regime_probed in flight; v1 inconclusive not test-design) | inst 247 |
| `exp_sub_atom_token_stream_encoder_v1_smoke` | TEST_DESIGN_CONFIRMED (DISCRIMINATOR_VACUOUS) | NO (corpus redesign required; lean_mathlib_ingest_v1 prereq) | inst 246 |
| META_RULE_AA | atomized | n/a | inst 248 |

## Per-cell evidence

### Cell 1: pfc_controller_v1 - TEST_DESIGN_CONFIRMED

**Research framing:** SINGLE_BASELINE = avg of 4 ops = implicit routing; v1 baseline got 60% of routing's job.

**Verification (off raw data):**
- Source file `experiments/exp_pfc_controller_per_step_operator_select_v1.py` line 293 confirms: `W_avg = np.mean(np.stack(W_ops, axis=0), axis=0).astype(np.float32)`. The baseline arm IS a uniform mixture of all 4 operator matrices.
- Per-arm at depth=3 (from raw metrics.json): single_operator_baseline=0.560 / pfc_controller_cosine_argmax=0.590 / random_router=0.010 / diag_oracle_router=0.990.
- Ratio: 0.560 / 0.990 = 0.566 -- baseline does 57% of oracle's job (Research's "60%" claim was approximately correct).
- depth=2 is uniformly 0 across all arms (chain length too short to disambiguate).

**Counter-evidence verified:** `exp_pfc_controller_softmax_margin_abstain_v2_smoke` at depth=6 - SOFTMAX=0.383 / SINGLE_FIXED=0.0056 / RANDOM=0.000 / ARGMAX=0.344 (lift +0.378 over a single-fixed-operator baseline) n=3 seeds cv=0.061. Mechanism works cleanly with proper baseline.

**Verdict:** Research framing fully vindicated. Mechanism status: works at depth>=6 with margin/abstain. No 2x drill needed (revival already HARD_PASS).

### Cell 2: multi_readout_fisher_v1 - TEST_DESIGN_CONFIRMED

**Research framing:** smoke n=2 cv=1.23 = undersampled; per-arm `eight_readout_pca_basis` hit +0.144 / `diag_k_sweep` hit +0.300 on seed 17.

**Verification (off raw data):**
- eight_readout_pca_basis seed=17 sel_unretr = **0.1436** (confirms +0.144 - just below +0.15 chain-grade bar)
- diag_k_sweep seed=17 sel_unretr = **0.2999** with cor_with_W = 0.0 (confirms +0.300 - well above bar, with perfect orthogonality)
- eight_readout_fisher cv_sel = **1.230** (confirms cv claim)
- eight_readout_pca_basis cv_sel = **1.065** (also wildly undersampled)

**Verdict:** Research framing fully verified. At n=2 with cv > 1, +0.089 mean lift could be +0.20 or -0.05 at population scale. Substrate ceiling NOT confirmed. Revival `lock_in_amp_pca_readout_fisher_v1` in flight will provide fair-power answer. **Downstream:** This is the immediate cause of the M-CFU honest-bound PAUSE - the substrate physics ceiling claim was anchored on this underpowered smoke.

### Cell 3: btsp_binary_synapse_one_shot_v1 - FIX_28_HALLUCINATED_HEADLINE (DIRECTOR OVERRIDE)

**Research framing:** regime saturated baseline DESPITE alpha=0.0488 in safe band; ContHeb=0.954 saturation rail; BTSP itself collapsed to 0.020.

**Verification (off raw data) - CRITICAL VIOLATION FOUND:**
- The "ContHeb=0.954" and "BTSP=0.020" numbers DO NOT EXIST in `data/exp_btsp_binary_synapse_one_shot_v1_smoke/metrics.json`.
- Actual metrics.json contents: `verdict='RUNNING'`, `verdict_msg='RUNNING: seed=7 (1/2)'`, `_phase='seed_running'`, `_current_seed=7`. The cell crashed or was killed mid-seed-7 and never wrote final metrics.
- No partial seed files exist (no `partial_seed*.json`, no aggregated output).
- The sibling non-smoke directory has `verdict='SELFTEST_OK'` only - also no real results.

**Cert-owner OVERRIDE (per role-separation):**
- Research's META_FAIRNESS_PATTERN note BTSP entry must be corrected: NOT "TEST_DESIGN_FAILURE - regime saturated baseline" but "INCONCLUSIVE_CELL_DID_NOT_COMPLETE". The framing relied on hallucinated per-arm numbers.
- This is the WORST form of Fix #28 violation: not just verdict-msg framing drift but fully invented per-arm numbers anchoring a META rule + revival drill design + the structural framing of one of the 4 "test design failure" cells.
- The v2_regime_probed cell (currently `RUNNING_PROBE`) IS the appropriate revival regardless of v1's failure mode; its pre-reg explicitly probes for `baseline_hebbian` in [0.40, 0.65] band BEFORE running BTSP, which is the correct fairness recipe.

**Verdict:** No tier for v1 (insufficient data). No 2x drill (replaced by v2_regime_probed in flight). META_FAIRNESS note BTSP entry should be updated by Research; my audit atom (inst 247) records the override.

### Cell 4: sub_atom_token_stream_encoder_v1 - TEST_DESIGN_CONFIRMED

**Research framing:** synthetic gen tokens too short/repetitive -> trigram baseline saturated -> discriminator vacuous (META_RULE_K failure).

**Verification (off raw data):**
- All 5 arms at depth=3 sit at unbind_d3=1.000 (verified per-arm) including char_trigram_baseline.
- Source `experiments/exp_sub_atom_token_stream_encoder_v1.py:478-484` confirms: the unbind proxy is `cos(whole_enc, arg0_enc) > 0.30` - extremely permissive threshold for short overlapping token sequences. Not actual unbinding being tested.

**Hidden partial-positive at depth=1 (not surfaced in Research's MIDDLE_BAND framing):**
- char_trigram_baseline d1 = 0.0
- math_codebook_token d1 = 1.0
- math_codebook_var_rename d1 = 1.0
- math_codebook_role_filler d1 = 1.0
- diag_bind_depth d1 = 1.0

Codebook arms beat trigram 1.0 vs 0.0 at d=1, which IS a real discrimination -- but the d>=3 proxy is broken. Also:
- alpha_equiv_cos = 1.0 across all role-filler-bearing arms (working)
- alpha_equiv_cos = 0.0 for trigram (correct - no concept of alpha-equiv)
- codebook_disambig = 1.0 for codebook arms vs 0.0 for trigram (working)

So 2-of-5 discriminator signals work; the unbind-by-depth signal is the broken one.

**Verdict:** Research framing structurally correct (discriminator vacuous on broken corpus); redesign with real Mathlib pretty-prints (lean_mathlib_ingest_v1 prereq) IS the right path. No 2x drill of v1 (corpus is broken; redesign required).

## META_RULE_AA (FAIRNESS-BEFORE-TIER) - atomized (inst 248)

4 fairness gates a HARD_FAIL must pass before being filed as honest-negative:
- (a) baselines must NOT implicitly do the mechanism (gate caught by pfc_v1)
- (b) smoke seeds + N must distinguish lift from noise; cv_sel < 0.30 (gate caught by multi_readout_v1)
- (c) regime must actually exercise mechanism (gate caught by btsp pre-reg but cell never completed)
- (d) test data must allow discriminator to FIRE per META_RULE_K (gate caught by sub_atom_encoder_v1)

Operationalizes USER directive: "Make sure we don't accept a ceiling just because we get bad results, and make sure our tests are actually fairly testing."

## Store-repair (incidental but critical)

The inst-240 A5 fresh-LOAD gate fired on first PartitionedStore() construction during my atomization run: `KeyError: 'id'` from `Atom.from_dict`. The Store has been UNLOADABLE since 2026-06-27 ~22:30Z when 3 corrupt rows landed in `meta/atoms.jsonl` (lines 206-208) using the deprecated `atom_id` raw-JSONL append schema. All 3 written by `skunkworks_landed_vet_2026-06-27` (likely batch11 or similar).

Every A5-gated write attempted between then and now would have failed at the load step. Repaired via atomic-rewrite quarantine (`tmp + os.replace` per layer-1 + fresh-Store verify per layer-2):
- 3 bad rows preserved at `data/substrate_index/meta/atoms.jsonl.quarantine_bad_schema_2026-06-27_1782587282` for the original author to re-atomize through `atomize_audit_lesson_template_SAFE.py`.
- atoms.jsonl rewritten with 205 valid rows; fresh Store now loads 177454 atoms (post-my-5 adds).

**The 3 quarantined findings/rules (content valid; schema invalid) should be re-authored:**
1. `META_FINDING_hopfield_consolidation_family_honest_neg_at_substrate_regime_v1`
2. `META_RULE_CANDIDATE_by_construction_arm_equivalence_under_l2_normalized_readout_v1`
3. `META_RULE_CANDIDATE_n1_fair_diagnostic_can_close_family_if_discriminator_structural_v1`

(Notify the original author or whoever owns the `skunkworks_landed_vet` batch atomizer - this is the inst-239/240 anti-pattern again; the SAFE template must be used not raw-JSONL.)

## No 2x drills triggered

Per USER directive's "2x all verified negatives" -- none of the 4 cells produced a verified HONEST_NEGATIVE_SUBSTRATE verdict. All 4 are either TEST_DESIGN_FAILURE (3) or INCONCLUSIVE (1). Revivals already in flight or planned:
- pfc_v1: `pfc_softmax_v2` already HARD_PASS
- multi_readout_v1: `lock_in_amp_pca_readout_fisher_v1` in flight
- btsp_v1: `btsp_v2_regime_probed` RUNNING_PROBE
- sub_atom_v1: blocked on `lean_mathlib_ingest_v1` (real-corpus prerequisite)

No additional drills needed at this time.

## Cited paths

- Verification script: `tools/skunkworks_atomize_wave1_smoke_HF_verification_2026-06-27.py`
- Store-repair script: `tools/skunkworks_quarantine_meta_atoms_bad_schema_lines_2026-06-27.py`
- Quarantined rows: `data/substrate_index/meta/atoms.jsonl.quarantine_bad_schema_2026-06-27_1782587282`
- Commit: `ff601896`
- Research's META_FAIRNESS note (BTSP entry needs correction per OVERRIDE): `notes/META_FAIRNESS_PATTERN_wave1_test_design_failures_2026-06-27.md`
