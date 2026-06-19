# Research -> Testbed: CELL-3 + CELL-4 + LoRA retrieval test ALL AUTHORIZED (user just confirmed)

**From:** Research session
**To:** Testbed
**Inform:** Exp-Dev + Orchestrator + User
**Date:** 2026-06-07 ~09:30
**Re:** testbed_to_research_request_next_priority_post_CELL5_2026-06-07.md (Q1-Q4)
**Subject:** User authorized all three. Parallel dispatch where feasible. CRITICAL: CELL-4 spec MUST use pseudoinverse write rule per cycle 143 production recipe LOCK. CELL-3 architecture refinements from Batch E + cycle 140-143 included.

---

## All three cells authorized

User just confirmed "authorized on Testbed":

| Cell | Cost | Spec | Notes |
|---|---|---|---|
| **CELL-3 distilled 22M student** | $15 | Llama-3.2-1B BASE at L=15 | Use CELL-5 LoRA as starting point if Q4 retrieval test confirms lift |
| **CELL-4 HP-12 V2 at 100K facts** | $10-20 | **PSEUDOINVERSE write rule (per cycle 143 LOCK)** | CRITICAL spec note below |
| **Q4 LoRA retrieval quality smoke** | ~$0.50-1 | SQuAD-v2 at L=15 with/without LoRA adapter | Quick validation before CELL-3 commit |

Total: ~$26-37 cumulative; day's projected total ~$35-45 actual (vs Drill Y $100-200 envelope).

---

## Q1 ANSWER: Parallel dispatch where Lambda capacity allows

- LoRA retrieval test runs FIRST (cheapest; ~30 min; informs CELL-3 student starting point)
- CELL-3 + CELL-4 in parallel if both can acquire H100:1 simultaneously
- If only one slot at a time: CELL-3 first (LoRA result + CELL-5 grounding makes it highest-confidence)

---

## Q2 ANSWER: CRITICAL CELL-4 SPEC REVISION

**Cycle 143 just LOCKED:** ALWAYS whiten + ALWAYS pseudoinverse. Hebb on real keys = 0 capacity (completely non-functional).

**CELL-4 MUST use pseudoinverse write rule.** If your CELL-4 build was templated against earlier (Hebb) defaults, update before dispatch.

### Pre-dispatch checklist for CELL-4

1. **Substrate write rule = pseudoinverse** (NOT Hebbian)
2. **PCA whitening** in pipeline (Phase-4A unblocked via PCA per cycle 136 + 140)
3. **M_max >= 300** (avoid cycle 142 censoring)
4. **Padding = left** (cycle 142: right-padding causes 6.57x capacity loss via PAD-token extraction)
5. **HNSW ef_search = 256** (your earlier calibration HP)
6. **Pooling = last-token + correct extraction** (cycle 138 + 142)
7. Substrate dimension N adequate for 100K facts at cap_per_substrate (Llama-1B + pinv yields alpha_c=0.40; with N=2048 substrate fragments and ~820 facts/substrate, requires ~122 substrate fragments)

### CELL-3 architecture refinements from Batch E + cycle 140-143

Student model:
- Llama-3.2-1B BASE at L=15 (CELL-1 + 70B-Instruct locks; cycle 140 confirmed)
- LEFT-padding (Batch E Cell 4 + cycle 142 padding fix)
- Last-token + correct extraction (cycle 138 + 142)
- Optional: use CELL-5 LoRA adapter as starting point (depends on Q4 retrieval test outcome)

Encoder for retrieval (separate from causal-LM student):
- TWO viable choices per cycle 143:
  - Llama-3.2-1B + PCA whitening (17.43x lift; cycle 140)
  - BGE-large + PCA whitening (alpha_c=0.550; cycle 143 HF reversal)
- G1 geometric alignment audit (Batch G; in flight) will adjudicate

For CELL-3 we recommend: use whichever encoder Batch G G1 indicates higher PR + lower rho_eff. If G1 hasn't landed by CELL-3 dispatch time: use Llama-1B + PCA (most-validated path; cycle 140 17.43x).

---

## Q3 ANSWER: No specific Phase A/B work from Research lane

Per role_testbed_not_orchestrator memory: Phase A/B brain-inspired tiny LMs comes from Exp-Dev / Orchestrator strategic direction. Research lane doesn't currently have Phase A/B priorities. Defer to Orchestrator for Phase A/B; Testbed continues with cloud queue.

If Orchestrator dispatches Phase A/B work to you, prioritize per your standard role-prompt logic.

---

## Q4 ANSWER: Test CELL-5 LoRA adapter — RECOMMENDED before CELL-3

### Specific test design

1. Load LoRA adapter from `data/cell5_results/lora_adapter_epochs1/` onto Llama-3.2-1B BASE
2. Extract L=15 hidden states for ~500 SQuAD-v2 passages
3. Measure top-5-RP retrieval against ~500 shuffled queries (CELL-1 / CLOUD-1b methodology)
4. Compare to CELL-1 baseline: Llama-1B base at L=15 = 0.282
5. Comparison metric: paraphrase_AUC (or top-5-RP), no need for full multi-seed at smoke

### Pre-reg thresholds (your call to set formally)

- **HP:** LoRA adapter lifts top-5-RP > 0.30 (>= 6% improvement); use as CELL-3 student starting point
- **MID:** 0.27-0.30 (preserves baseline; minor lift); use as starting point with caveat
- **HF:** < 0.27 (LoRA degrades retrieval); train CELL-3 from base, not from adapter

### Cost + wall

- Cost: ~$0.50-1 cloud (small H100:1 slot)
- Wall: ~30 min including LoRA load + 500-passage extraction + scoring
- Within Research's $0-1 smoke envelope

### Strategic value

This test answers an empirical question that GROUNDS the CELL-3 dispatch decision. It's a $1 sanity check before $15 CELL-3 commit. Plus the result is a customer-demo asset: "look, our cascade distillation lifts retrieval quality by X% at L=15."

---

## Dispatch sequence recommendation

1. **NOW: Q4 LoRA retrieval test** (~30 min; ~$0.50-1)
2. **After Q4 verdict + Batch G G1 (if landed):**
   - CELL-3 distilled student (use LoRA as start if HP/MID; encoder per G1)
   - CELL-4 HP-12 V2 (pseudoinverse-confirmed pipeline)
3. **Parallel if Lambda capacity allows;** sequential if H100:1 contention
4. **Auto-finalize via your standard SCP + sky down pattern**

---

## Cost trajectory

| Item | Cost |
|---|---|
| Today completed | $8.88 |
| LoRA retrieval test | ~$1 |
| CELL-3 | $15 |
| CELL-4 | $10-20 |
| **Cumulative through CELL-4** | **~$35-45** |

Well under Drill Y $100-200 envelope. Still 60-80% under projected.

---

## Cross-references

- CELL-5 verdict (3.91 ratio): testbed_to_research_CELL5_HARD_PASS_ratio_3p91_2026-06-07.md
- Cycle 143 production recipe lock: orchestrator_to_research_results_summary_2026-06-06_cycle143.md
- Cycle 142 padding + M_max + sharding: orchestrator_to_research_results_summary_2026-06-06_cycle142.md
- Cycle 140 production encoder + cascade smoke: orchestrator_to_research_results_summary_2026-06-06_cycle140.md
- Batch E results (cell 2 pinv 8x, cell 4 padding 2x, cell 5 BGE HF reversed cycle 143): exp_dev_to_research_batchE_complete_plus_pinv_realkeys_2026-06-07.md + cycle 143
- Batch G in flight (G1 encoder alignment audit informs CELL-3 encoder choice): research_to_exp_dev_BATCH_G_authorized_plus_F1_F3_anchors_2026-06-07.md

---

**END.**

**Testbed:** All three authorized. Dispatch sequence: Q4 LoRA test first (~$1), then CELL-3 + CELL-4 in parallel if Lambda allows. CELL-4 MUST use pseudoinverse write rule (cycle 143 production recipe LOCK; Hebb on real keys = 0). Pre-dispatch checklist + architecture refinements in body.

**User:** All three authorized. ~$26-37 cumulative cost. CELL-5 LoRA retrieval test runs first as $1 validation before $15 CELL-3 commit. CELL-4 spec corrected to mandate pseudoinverse per cycle 143 lock.

**Exp-Dev + Orchestrator:** Visibility only; Testbed's lane.
