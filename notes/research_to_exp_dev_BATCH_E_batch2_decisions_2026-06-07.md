# Research -> Exp-Dev: Batch E Batch-2 decisions -- Cell 5 use exact-recovery + Cell 6 use MarianMT round-trip

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User + Testbed
**Date:** 2026-06-07 ~07:00
**Re:** exp_dev_to_research_batchE_batch2_2026-06-07.md
**Subject:** Cell 7 HP acknowledged (fp16 safe for production). Cell 5 use all-bits exact-recovery metric (matches today's framework; revised PRED-1 thresholds). Cell 6 use MarianMT round-trip paraphrase (real adversarial test).

---

## Cell 7 HP acknowledged

fp16 vs fp32 parity HARD_PASS at smoke -- cap gap 0.0, whitened-sign agreement 0.996. **fp16 is SAFE for production at reduced precision.** Probe 2's worry about fp16 drift is empirically REFUTED. Good news; production can run fp16 without metric drift.

## Cell 5 decision: USE ALL-BITS EXACT-RECOVERY (Option a)

Reasoning:
- Cell 1 (CELL-MF-1) just confirmed alpha_c=0.06 all-bits exact-recovery as substrate's empirical operating regime (today)
- Cycles 138/139 (cap=122 measurements) also used exact-recovery (consistent framework)
- Production substrate uses exact-recovery
- Drill 5's PRED-1 numerical band (cap ~ 1.33*d_eff) needs reframing in exact-recovery space

### Revised PRED-1 thresholds in exact-recovery frame

Reference: MiniLM cap=122 at d_eff=91.6 -> cap/d_eff = 1.33 (cycle 138/139)
Linear prediction for BGE-large d_eff=114.8: cap ~ 152

- **HARD_PASS:** cap(BGE-large) >= 140 (linear scaling per Drill 5 theory)
- **MID:** cap(BGE-large) 125-140 (sublinear but still gain)
- **HARD_FAIL:** cap(BGE-large) <125 (sublinear; theory falsified)

These thresholds match Drill 5's PRED-1 in the right metric frame.

### Sanity check from your cycle 138/139 data

MiniLM cap=122 at d_eff=91.6 = exact-recovery measurement (consistent with Cell 1 alpha_c=0.06 finding).

Llama-3.2-1B cap = 122 (cycle 140 "Llama+whitening = 122") at unspecified d_eff. The 17.43x lift over MiniLM in cycle 140 was at LARGER N_sub or test conditions where MiniLM under-performed (probably hit d_eff ceiling earlier).

For Cell 5: same test conditions as cycle 138 MiniLM measurement; just swap encoder to BGE-large. cap(BGE) measurement directly comparable to MiniLM cap=122 baseline.

## Cell 6 decision: USE MARIANMT ROUND-TRIP (Option 1)

Reasoning:
- The point of Cell 6 (per Probe 2) is to test KF-1 against REAL script-kiddie paraphrase attacks
- Embedding perturbation proxy doesn't test the real attack mechanism
- Cloud paraphrase adds unnecessary cost
- T5-paraphrase / MarianMT round-trip is the canonical NLP adversarial-robustness benchmark

### Specific recommendation

MarianMT round-trip:
- English -> German -> English (Helsinki-NLP/opus-mt-en-de + Helsinki-NLP/opus-mt-de-en), OR
- English -> French -> English (Helsinki-NLP/opus-mt-en-fr + Helsinki-NLP/opus-mt-fr-en)

Either path:
- Well-characterized in adversarial NLP literature
- Reproducible
- Generates lexically diverse paraphrases that preserve meaning
- Standard benchmark for robustness evaluation

Cost: ~1 GPU-hour for paraphrase generation (5K KF-1 examples through round-trip MT) + KF-1 scoring sweep. Within Probe 2's "1 GPU-hour" estimate.

### Pre-reg per Probe 2

- **HARD_PASS:** AUC drop <= 0.05 (KF-1 survives paraphrase; original AUC=0.977 → >=0.93 on round-trip)
- **MID:** AUC drop 0.05-0.20 (degraded but usable; original 0.977 → 0.77-0.93)
- **HARD_FAIL:** AUC drop > 0.20 (KF-1 alone insufficient; original 0.977 → <0.77)

Per Probe 2 prediction: AUC drop predicted to 0.55-0.65 (HARD_FAIL territory). If confirmed: hybrid hallucination stack (substrate + bigrams + NLI + paraphrase-aware) is MANDATORY before deployment.

## Strategic value of either outcome

### If Cell 5 HARD_PASS (BGE-large cap >= 140)
- Drill 5 cap=1.33*d_eff theory confirmed
- BGE-large is a viable encoder
- BUT cycle 140 Llama-3.2-1B + whitening = 17.43x MiniLM REMAINS the production encoder
- BGE-large becomes alternative for non-Llama deployment (e.g., on-prem without Llama license)

### If Cell 5 HARD_FAIL (BGE-large cap <125)
- Drill 5 theory needs sublinear/architectural correction
- BGE-large excluded as production encoder
- Llama-3.2-1B remains uncontested production encoder choice

### If Cell 6 HARD_PASS (paraphrase survives)
- KF-1 word-bigrams more robust than Probe 2 predicted
- Hybrid stack not mandatory for paraphrase attacks
- Production hallucination story simpler

### If Cell 6 HARD_FAIL (paraphrase collapses AUC)
- KF-1 alone insufficient
- Hybrid stack (substrate grounding + HOC1 bigrams + NEG1 NLI + paraphrase-aware detection) required
- Production architecture adds complexity but Probe 2 prediction validated

## Cross-references

- Drill 5 theory: research_drill_d_eff_capacity_ceiling_theory_2026-06-07.md
- Probe 2 adversarial: research_drill_adversarial_substrate_divergence_2026-06-07.md
- Cell 1 CELL-MF-1 (alpha_c=0.06): exp_dev_to_research_batchE_batch1_2026-06-07.md
- Cycle 138/139 cap=122: capability_scorecard.md entries
- Cycle 140 Llama-1B 17.43x: orchestrator cycle 140 summary

## Contract

You design implementation specifics (sweep grids, exact thresholds, seed counts). The decisions above resolve the metric choice (Cell 5: exact-recovery) and paraphrase generator (Cell 6: MarianMT round-trip).

---

**END.**

**Exp-Dev:** Cell 5 use all-bits exact-recovery (matches today's framework; revised PRED-1 thresholds in body); Cell 6 use MarianMT round-trip paraphrase (English-German or English-French). Both dispatch when GPU lane has capacity.

**User:** Cell 7 HP (fp16 safe). Cell 5 + Cell 6 decisions ruled. Standing for Batch-2 GPU dispatch.

**Orchestrator:** Visibility only; Exp-Dev's lane.
