# Research -> Exp-Dev: Batch F AUTHORIZED -- retroactive audit + composition tests (~9 cells; CPU; $0)

**From:** Research session
**To:** Exp-Dev
**Inform:** Orchestrator + User + Testbed
**Date:** 2026-06-07 ~08:30
**Re:** orchestrator cycle 142 (LVH #243 corrected; M_max=50 censoring discovery) + exp_dev_to_research_batchE_complete_plus_pinv_realkeys_2026-06-07.md (propose-back pseudoinverse on real keys)
**Subject:** User authorized Batch F. 6 retroactive HF audits at M_max>=300 + 2 composition tests + 1 engineering task. All CPU; $0; ~4-6h sequential. Pseudoinverse real-keys lever (8x rescue) adopted into SSOT.

---

## Why Batch F

Cycle 142 revealed three measurement systematic issues that may have BIASED today's HARD_FAIL verdicts:

1. **M_max=50 censoring** -- many prior HFs at M=50 may reflect measurement cap, not true substrate limit (true M_c=200; 4x censored)
2. **Pseudoinverse rescues real-encoder keys** (Exp-Dev's propose-back) -- Hebb alpha_c ~ 0 on real keys; pinv alpha_c=0.40. The HF verdicts that used Hebb on real-encoder substrate may revise UPWARD with pinv.
3. **alpha=0.005 sparse-coding default** -- prior alpha settings were sub-optimal (6x lift over alpha=0.05)

The combination of these three measurement biases means several of today's "settled" HARD_FAILs may need re-classification. Batch F runs the re-audit pass.

Plus 3 composition/engineering follow-ons.

---

## TIER 1 -- Retroactive HF re-audit (M_max>=300 + pinv where applicable)

### F1: norm-gate re-audit
- **Why:** original norm-gate HF (cycle ~118) used M_max=50; may have been measurement artifact
- **What to test:** repeat norm-gate experiment at M_max>=300; if HP at higher M_max, extraction-gate path reopens
- **Wall:** ~30 min CPU
- **Strategic value:** could rescue norm-gate as a viable extraction approach

### F2: kf1_contradiction re-audit
- **Why:** kf1 contradiction HF (cycle ~119) at M_max=50; negation gate may be open
- **What to test:** kf1_contradiction at M_max>=300 + pinv where applicable
- **Wall:** ~30 min CPU
- **Strategic value:** if HP, KF-1 contradiction detection succeeds without needing NEG1 DeBERTa drop-in

### F3: kf1_truthfulqa re-audit
- **Why:** TruthfulQA HF at M_max=50; same potential censoring issue
- **What to test:** at M_max>=300 + pinv where applicable
- **Wall:** ~30 min CPU
- **Strategic value:** TruthfulQA gate may be cleanly open

### F4: multi_head_x_corruption re-audit
- **Why:** corruption envelope <20% flip rate (cycle 137) may have been M_max-limited
- **What to test:** corruption sweep at M_max>=300
- **Wall:** ~30 min CPU
- **Strategic value:** if HP at >20% flip rate, multi-head viable in noisier production environments

### F5: codebook_collapse_recovery re-audit
- **Why:** recovery 69% (cycle 137) just below 70% threshold may be measurement artifact
- **What to test:** recovery sweep at M_max>=300 + pinv where applicable
- **Wall:** ~30 min CPU
- **Strategic value:** if HP, codebook recovery clears production threshold

### F6: BGE-large re-audit with M_max>=300 + pinv
- **Why:** BGE-large HF at 40 cap (cycle 141) may revise upward with proper M_max AND pinv (Hebb is broken on real keys per Exp-Dev's propose-back smoke)
- **What to test:** BGE-large capacity at M_max>=300 with pseudoinverse write rule
- **Wall:** ~30 min CPU
- **Strategic value:** if HP, BGE-large revives as encoder candidate alongside Llama-3.2-1B

---

## TIER 2 -- Composition tests (do the new levers stack?)

### F7: pinv x sparse x multi-head compound
- **Why:** pseudoinverse 11x + sparse 6x + multi-head 2.25x = ~150x synthetic theoretical IF they stack; need empirical confirmation
- **What to test:** ablation factorial across pinv vs Hebb, sparse alpha=0.005 vs 0.05, multi-head M=2 vs 1
- **Wall:** ~60 min CPU
- **Strategic value:** validates compound math; may reveal interaction effects

### F8: pinv x pad-fix x alpha=0.005 compound
- **Why:** today's 3 new defaults (pinv + correct padding + alpha=0.005) compound test
- **What to test:** baseline vs full-new-defaults ablation
- **Wall:** ~45 min CPU
- **Strategic value:** confirms new production recipe gives expected compound lift

---

## TIER 3 -- Engineering task (mechanical; can run during Tier 1-2)

### F9: PP-8 default swap alpha=0.005
- **Why:** orchestrator cycle 142 explicit recommendation
- **What to do:** update PP-8 sparse-coding default to alpha=0.005 in production code path
- **Wall:** ~15 min engineering
- **Strategic value:** locks in 6x lift across all PP-8-dependent cells going forward

---

## Total estimate

- Tier 1 (F1-F6 sequential): ~3 hours CPU
- Tier 2 (F7-F8 sequential): ~2 hours CPU
- Tier 3 (F9 engineering): ~15 min
- **Total: ~4-6h CPU sequential; ~2-3h with parallelism; $0**

---

## SSOT updates

**Adopt Exp-Dev's propose-back into SSOT:** pseudoinverse on real-encoder keys is now production-grade write-rule lever.

Per Exp-Dev's smoke: pinv alpha_c=0.40 on ZCA-whitened sign(MiniLM) keys vs Hebb alpha_c~0. "Pseudoinverse doesn't just beat Hebb on real keys -- it RESCUES capacity that Hebb can't reach at all."

This means:
- All real-encoder substrate cells should use pinv as default
- BGE-large + pinv full re-test is Batch F's F6 cell
- Llama-1B + pinv full re-test is a natural follow-up (if F6 HPs, dispatch as F10)

---

## Expected outcomes + production architecture revision

### If F1-F6 mostly HP (likely per cycle 142 framing)
- Multiple "closed" lines reopen
- Production architecture has more empirical paths
- Compound math validated upward
- KF-1 contradiction may not need NEG1 DeBERTa (F2)
- Multi-head corruption envelope expands (F4)
- Codebook recovery clears threshold (F5)
- BGE-large revives (F6)
- norm-gate extraction reopens (F1)

### If F7-F8 confirm stacking
- Production compound math validated
- Pipeline architecture becomes ship-ready

### If F1-F6 mostly HF at higher M_max (less likely but possible)
- Today's HF closures stand
- Provides cleaner empirical floors
- Either way: cleaner cap_map

---

## Cross-references

- Cycle 142 orchestrator note: orchestrator_to_research_results_summary_2026-06-06_cycle142.md
- Batch E complete + propose-back: exp_dev_to_research_batchE_complete_plus_pinv_realkeys_2026-06-07.md
- Cycle 141 pseudoinverse foundational: orchestrator_to_research_results_summary_2026-06-06_cycle141.md
- Drill 4 mean-pool tax (anchor for tax-finding pattern): research_drill_mean_pool_tax_investigation_2026-06-07.md

---

## Contract

You design anchor specifics, sweep grids, HP/MID/HF thresholds, queue assignments, timeout formulas. Pre-reg per envelope-fail-band protocol. write_metrics() required fields. ASCII-only. Apply [[feedback-no-experiment-design-in-prompts]] -- this handoff names anchors + WHY + tier only.

Per [[feedback-pressure-test-negative-findings]] discipline: cycle 142's M_max censoring revelation IS the negative-findings pressure-test; running these audits IS the protocol.

## Autonomy

You may:
- Reorder Tier 1 cells by queue state / runner availability
- Combine compatible cells into a single multi-arm test if more efficient
- Parallelize Tier 2 with Tier 1 if CPU/GPU lanes both available
- Add adjacent cells if a result opens follow-ups (e.g., F10 = Llama-1B + pinv re-test if F6 HPs)
- Skip F9 if engineering task conflicts with active experiments

---

**END.**

**Exp-Dev:** Batch F authorized (9 cells; ~2-3h parallel; $0). Tier 1 (F1-F6) is highest leverage (retroactive audit; reopens potentially closed lines). Tier 2 (F7-F8) tests composition. Tier 3 (F9) is engineering. Pseudoinverse on real-encoder keys adopted into SSOT per your propose-back smoke.

**User:** Batch F (9 cells) routed to Exp-Dev. Tests whether today's M_max=50 censoring affected prior HARD_FAIL verdicts. Could reopen norm-gate / KF-1 contradiction / TruthfulQA / multi-head corruption / codebook recovery / BGE-large encoder. Plus 2 composition tests (do pinv+sparse+multi-head stack? do new defaults compound?) + 1 engineering task (PP-8 default alpha=0.005). All CPU; $0.

**Orchestrator:** Visibility only.

**Testbed:** Visibility only; CELL-5 LoRA dispatch + Cell 10 HNSW WSL remain your standing items.
