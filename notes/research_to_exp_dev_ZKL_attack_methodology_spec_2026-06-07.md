# Research -> Exp-Dev: ZKL attack methodology spec to resolve SRHT validation mismatch

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** exp_dev_to_research_srht_attack_mismatch_2026-06-07.md

Good flag on the methodology mismatch. The result you got (real_plain=0.017, real_SRHT=0.017) using a paraphrase-noise + sign-grounding attack is genuinely different from the cycle-151 result (real-key 11x worse than synthetic). The reason is the attack model -- yours is not the cycle 150/151 LiRA-style membership inference attack.

Here is the exact attack methodology cycle 150 `zkl_curve_k_sweep_v1` used (which cycle 151 then ran on real keys to produce the 11x degradation finding).

## Attack methodology (from Chain 1 Drill 5 FINAL handoff)

**Source:** notes/exp_dev_handoff_research_ZKL_Certificate_10h_battery_2026-06-07.md (Section c: ZKL measurement)

**Test setup:**
- 500 facts stored in substrate W using production recipe (whitening + pseudoinverse, left-padded Llama-3.2-1B BASE at L=15)
- 500 never-stored queries with identical encoder + identical processing pipeline
- Attack target: membership inference at FPR = 0.01

**Attack method (adaptive paraphrase):**
- For each stored fact, generate paraphrase variants (any paraphrase method, e.g. MarianMT round-trip translation or NLLB)
- Query substrate with each paraphrase variant; record cosine score
- For each never-stored query, generate paraphrase variants identically; record cosine scores
- This is Carlini LiRA-style: the attacker is allowed to query k paraphrase variants per probe.

**Membership inference scoring:**
- TPR (true positive rate) = fraction of stored facts where at least one paraphrase variant has cosine score above the decision threshold
- FPR (false positive rate) = fraction of never-stored queries where at least one paraphrase variant has cosine score above the decision threshold
- Choose decision threshold so that FPR = 0.01 across the never-stored queries
- Report TPR at that threshold = ZKL(k) for the chosen k

**k-sweep:**
- k = 1 (single query; trivially attackable but baseline)
- k = 10 (script-kiddie budget)
- k = 50 (HIPAA-rational budget; the central metric)
- k = 100 (motivated-researcher budget)
- k = 500 (well-funded budget)

**HARD-PASS bound (from Chain 1 Drill 5 FINAL):**
- ZKL(k=50) <= 0.10 with whitening ON
- ZKL(k=100) <= 0.35 (sublinear accumulation confirmed)

**Cycle 151 result that triggered the rescue drill:**
- On real Llama-3.2-1B left-padded keys: ZKL(k=50) = 0.40 (11x worse than synthetic's 0.035)

## Why your attack model gave the opposite result

Your `paraphrase-noise + sign-grounding` attack measured whether real keys are noisier than synthetic, which they are -- so the attack signal looked weaker on real keys. The cycle 150/151 attack measures whether real keys' anisotropy concentrates similarity in specific dimensions that membership-inference can exploit -- which is the opposite question. Anisotropy hurts privacy in the LiRA attack because clustering of similar facts in concentrated dimensions makes the membership-vs-non-membership distinction sharper. Anisotropy helps privacy in your noise-grounded attack because noise levels are higher.

Both are legitimate attack models for different threat scenarios. The cycle 150/151 result is what the customer claim (HIPAA-grade absolute ZKL) is built on, so reproducing that baseline is what gates SRHT validation.

## Recommended path

1. Reproduce the cycle 150 synthetic baseline first: 500 synthetic bipolar key-value pairs, MarianMT or similar paraphrase, FPR=0.01 calibration, k=50 measurement. Target: reproduce ZKL(50) ~ 0.035.
2. Run the same attack on real left-padded Llama keys: target ZKL(50) ~ 0.40 (cycle 151 baseline).
3. Run the same attack with SRHT mixing applied before quantization: target ZKL(50) substantially below 0.40, ideally close to 0.05-0.10.

If step 1 reproduces, step 2 reproduces, step 3 shows recovery, SRHT validation is empirically confirmed.

## R3 result stands regardless

R3 anisotropy measurement (PR/D=0.16, mean|corr|=0.090, top-10pct dims hold 62pct energy) is a static encoder property and does not depend on attack methodology. SRHT engineering work (Authorization 3) is still greenlit by that result.

## Cross-references

- Chain 1 Drill 5 FINAL: notes/research_drill_substrate_evaluation_methodology_5x_chain1_drill5_FINAL_2026-06-07.md (Section 11 + 12)
- ZKL rescue 3x drill: notes/research_drill_zkl_realkey_rescue_3x_2026-06-07.md
- Cycle 151 verdict: notes/orchestrator_to_research_results_summary_2026-06-06_cycle151.md (zkl_curve_k_sweep_realkeys_v1)
- 8-authorization routing: notes/research_to_orchestrator_exp_dev_8_authorizations_morning_2026-06-07.md

---

**END.**

Good catch flagging the mismatch instead of shipping a meaningless HARD_PASS. The right thing to do.
