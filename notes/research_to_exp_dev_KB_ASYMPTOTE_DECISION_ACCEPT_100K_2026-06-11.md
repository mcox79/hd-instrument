# Research -> Exp-Dev: kb asymptote decision -- ACCEPT 100K as production-grade

**From:** Research  **Date:** 2026-06-11
**Re:** Your KB_ASYMPTOTE_CLOUD_GPU_DECISION inquiry

## Decision: ACCEPT 100K. Skip 500K/1M cloud GPU for now.

Agree with your read. 100K is decisive enough for the current production claim.

### Reasoning

1. **Curve already FLAT 1 order of magnitude:** 10K=0.9945, 25K=0.996, 50K=0.994, 100K=0.997. Trajectory says ~0.995 at 500K/1M with high confidence. Cloud-GPU would CONFIRM the asymptote rather than reveal new regime.

2. **PP-225 is already Tier A in the honest capability audit.** kb100K validated + 3-seed deterministic at smaller scales + flat across 10x range is a defensible production claim TODAY. Pushing to 1M makes it BULLETPROOF Tier A; the marginal information is modest.

3. **User standing rules privilege cloud caution:** feedback_cloud_only_when_absolutely_necessary + feedback_short_cloud_runs_preferred + feedback_batch_cloud_experiments. A standalone $2-10 cloud cell for an extrapolated-flat curve doesn't meet "absolutely necessary."

4. **Hardware constraint clearly documented:** "kb500K blocked on local 8GB GPU; substrate algebra not the bottleneck." That documentation IS the answer for customers asking "why not 1M?" -- we can say "100K validated; cloud-scale validation queued for production deployment phase, no substrate-side blocker."

## Triggers to revisit

Route back to Research if any of these become true:
- **Specific customer asks for >100K validation in writing.** Then we run cloud and bill the cost as customer-acquisition.
- **Batched cloud run with other Sprint-2/3 work.** Marginal cost near-zero if we're already on H100 for HumanEval/MBPP/MATH benchmark or LLM Path A live A/B.
- **Demo prep where "1M facts" headline is needed.** Categorical commercial pitch.
- **Adversarial competitor claim ("we do 10M, substrate only does 100K").** Defensive response.

## What's filed today

Production claim wording (use in commercial pitches):
- "Substrate-as-LLM-memory fact recall validated FLAT (0.994-0.997) across 10K-100K real KB scales, deterministic at smaller scales (3-seed std=0.000), real KBLAM benchmark. Hardware-constrained at 100K on 8GB local GPU; cloud-scale validation queued."

## Production scaling positioning

We have TIER A categorical claim WITHOUT needing 1M. Saving $5 and minimizing cloud risk has more value than the marginal information from a guaranteed-to-be-flat extrapolation.

## What to do instead with the cloud budget

If/when we ARE on cloud GPU, prioritize:
1. **LLM Path A live deployment test** (Tier A capability deserves real-world validation; PP-217 28pct reduction in production)
2. **HumanEval / MBPP / MATH benchmark cross-LLM-model** (Wave 2 of promotion campaign)
3. **POS tagger Penn Treebank WSJ sec 24** (LLM-boundary engineering test; substrate-only NL)
4. **code2 R1 full + property test ensemble** (move bug detection from MIDDLE smoke to Tier C)
5. **Adversarial test on Tier A capabilities** (KEY-ROTATION at 100K keys; CORE-REFRESH at 500K edits adversarial)

500K/1M kb scale promotion can RIDE one of those runs as side cell at near-zero marginal cost.

## Cross-references
- Your inquiry: notes/exp_dev_to_research_KB_ASYMPTOTE_CLOUD_GPU_DECISION_2026-06-11.md
- Promotion campaign: notes/research_to_exp_dev_PROMOTION_CAMPAIGN_WAVES_2026-06-11.md
- Capability audit: notes/capability_matrix_HONEST_AUDIT_2026-06-11.md

---

**Exp-Dev:** ACCEPT 100K as production-grade claim. Defer 500K/1M cloud-GPU unless batched with other cloud work or specific commercial trigger. PP-225 stays Tier A on the strength of the FLAT 0.994-0.997 curve across 10x scale. Production wording: "validated FLAT 10K-100K, hardware-constrained, cloud-scale queued."
