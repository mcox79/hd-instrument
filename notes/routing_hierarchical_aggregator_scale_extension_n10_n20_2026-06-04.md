# Routing -- Hierarchical aggregator scale extension at N=10 and N=20 corpora

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical scale-extension (2 cells extending 5-corpus aggregator HP)
**Source:** 5-corpus hierarchical meta-aggregator HARD_PASS at N=2048 (per exp_dev compaction brief 2026-06-04 PM; substrate aggregator BPC=2.598 vs specialist 2.561; deletion retention 1.002)

---

## Capability question

Does substrate hierarchical aggregator multiplicative capacity scaling (per cross-domain interference 2x drill: N_domains * alpha_c * N total patterns at orthogonal domain keys) hold at N_domains=10 and N_domains=20?

The 5-corpus HP at N_substrate=2048 used ~5 patterns per domain. Cross-domain interference drill predicted:
- N_domains=5, N=2048, alpha_c=0.138, ~5 patterns each: well below capacity (~28 patterns / 1413 ceiling)
- N_domains=10, N=2048, ~10 patterns each: well below capacity (~138 patterns / 2826 ceiling)
- N_domains=20, N=2048, ~20 patterns each: ~414 patterns / 5652 ceiling -- still below; predicted HP
- N_domains=50, N=2048, ~50 patterns each: ~2585 patterns / 14130 ceiling -- approaching capacity; predicted MIDDLE/HF
- N_domains=100, N=2048, ~100 patterns each: ~10341 patterns / 28260 ceiling -- catastrophic per AGS curve at 0.85 * alpha_c

This test characterizes the empirical scaling at moderate N_domains before pushing to capacity limits (where D-ECR eviction + MCT early-warning would be tested separately by alpha-ramp/MCT experiment already running).

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_hierarchical_aggregator_scale_extension_n10_n20_v1_n2048`

**Cells:**
- Cell H1 (replicate baseline): N_domains=5, K_d=5 patterns/domain, N_substrate=2048 -- replicate 5-corpus HP (sanity check)
- Cell H2: N_domains=10, K_d=10 patterns/domain, N_substrate=2048 -- 2x scale
- Cell H3: N_domains=20, K_d=20 patterns/domain, N_substrate=2048 -- 4x scale

**Per-cell pre-reg:**

HARD-PASS:
- Substrate aggregator preserves >= 90% of specialist accuracy across ALL domains
- Cross-domain query baseline beats aggregator by >= 3x BPC (substrate is doing real aggregation)
- Deletion-cert retention >= 0.95 (audit primitive preserved at scale)
- 3/3 seeds converge

MIDDLE:
- Partial preservation: substrate aggregator 70-90% of specialist accuracy
- Deletion-cert retention 0.85-0.95

HARD-FAIL:
- Substrate aggregator < 70% of specialist OR deletion-cert retention < 0.85

**Aggregate verdict:**
- SCALES_CLEANLY: H1 + H2 + H3 all HP -> multiplicative capacity scaling confirmed
- SCALES_PARTIALLY: H1 + H2 HP; H3 MID/HF -> ceiling between N_domains=10 and 20 at K_d=20
- SCALES_BREAKS_EARLY: H2 MID/HF -> scaling ceiling lower than predicted

## Resource

Local CPU. Reuses 5-corpus aggregator scaffold (already validated 2026-06-04).

## Cost ceiling

$0 CPU. Per-seed wall: H1 ~5-10 min (replicate); H2 ~10-20 min (2x scale); H3 ~20-40 min (4x scale). Total ~2-3h CPU wall for 9 measurements (3 cells x 3 seeds).

## P_deflated (per today's methodology)

**P_algebraic = 0.70**: cross-domain interference drill predicts multiplicative capacity scaling at orthogonal keys; well-anchored algebraically. Today's 5-corpus HP empirically validates the principle at small N_domains.

**P_implementation:**
- P_convergence = 0.80 (5-corpus aggregator already HP; same scaffold)
- P_budget = 0.85 (N_substrate=2048 has comfortable headroom up to ~280 patterns; 20 domains x 20 patterns = 400 patterns approaches but doesn't exceed)
- P_no_subsumption = 0.95 (W-modifying Hebbian aggregation)
- P_task_match = 0.70 (scale-extension of empirically-validated 5-corpus task class)
- Joint P_implementation ~ 0.45

**P_joint (HP at H2 N=10) = 0.70 * 0.45 ~ 0.32**
**P_joint (HP at H3 N=20) = 0.55 * 0.45 ~ 0.25** (slightly lower; closer to capacity boundary)

## Engineering scope

~2-3h:
- Generate 10 + 20 domain corpora (extend existing 5-corpus generator; ~30 min)
- 10/20 sub-LM training pipeline (reuses 5-corpus scaffold; ~30-60 min)
- Substrate aggregator + cross-domain eval at 10/20 domains (~30-60 min)
- Per-cell deletion-cert validation (~30 min)

Reuses 5-corpus scaffold substantially.

## Strategic outcome

### If H1+H2+H3 all HP (multiplicative scaling holds at N=20)

- Substrate's hierarchical scaling EMPIRICALLY validated up to ~400 patterns total / 2826 ceiling
- Path opens for further scale extension (N_domains=50, 100 -- approaching capacity per cross-domain drill)
- D-ECR eviction empirical test becomes priority (substrate at capacity boundary)
- Product narrative: "substrate scales to 20+ specialized sub-models without capacity loss"

### If H2 HP, H3 MID/HF (scales to 10 cleanly, borderline at 20)

- Per-domain K_d=20 patterns may be the issue (not N_domains directly)
- Test with K_d held constant at 5 across N_domains=10, 20 to isolate

### If H2 MID/HF (scales break early at N=10)

- 5-corpus HP was edge case OR per-domain pattern count effect
- Cross-domain interference drill's multiplicative-capacity prediction needs refinement at scale

### Deletion-cert retention scaling

Each cell tests deletion-cert audit primitive at increasing scale. If retention degrades:
- HP retention >= 0.95: audit primitive preserved across hierarchical scale
- HF retention < 0.85: audit primitive degrades; orthogonality assumption breaks down

---

## What this is (plain language)

Today's 5-corpus aggregator test HARD_PASSED. Each of 5 sub-LMs is preserved by substrate aggregator with ~98.6% specialist accuracy AND deletion-cert audit works perfectly (retention 1.002).

Test: scale this to 10 corpora and 20 corpora. Does substrate aggregator STILL preserve specialist accuracy at higher N_domains? Does deletion-cert still work?

This tests whether substrate's hierarchical scaling is REAL at the predicted multiplicative capacity, or if it was a small-N edge case. Per cross-domain interference drill: should scale cleanly until N_domains * K_d approaches alpha_c * N_substrate (~283 patterns at N=2048).

If scales: substrate's product narrative extends to "20+ specialized sub-models with audit-preserved aggregation."

If breaks: characterizes where the empirical ceiling actually sits.

---

## Strategic context

Connects to:
1. 5-corpus aggregator HP (today's empirical anchor)
2. Cross-domain interference 2x drill (multiplicative capacity prediction)
3. Alpha-ramp/MCT smoke HP (capacity curve characterization)
4. Future Bundle (capacity-saturation eviction policies; could combine with this if scales break)

Bundle is PRE-CONDITION for any further substrate aggregator product positioning. If scales hold at N_domains=20: meta-LLM Level 3 architecture (separate drill in flight) becomes the next priority.

---

## What this is NOT

- NOT a meta-LLM test (that's separate; Level 3 architecture drill in flight)
- NOT a capacity-saturation test (that's alpha-ramp/MCT already running)
- NOT a cloud test ($0 CPU)
- NOT urgent dispatch (already-substantial Exp-Dev pipeline; can run in standby slot)

---

## Sequencing

This bundle is PRE-PLANNED for dispatch when Exp-Dev has CPU bandwidth (after current mini_lm v2 + alpha-ramp/MCT complete). Low priority vs Mode 4 resonator + Bundle G + Phase 0.5 v1 substrate-side core.

Engineering can start in parallel with other work; experiment dispatch when CPU runner free.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: 3 cells discriminate scaling at meaningful N_domains values
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-small-scale-first-methodology]]: empirically-validated 5-corpus -> 10/20 scale extension; not skipping rungs
- Per [[feedback-pressure-test-negative-findings]]: tests whether multiplicative scaling prediction (potentially-conservative claim) holds at larger scale
- ASCII-only

PROT-018: anchors use `_n2048_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** ~2-3h engineering + ~2-3h CPU wall total for 9 measurements (3 cells x 3 seeds). Verdict drives substrate hierarchical scaling empirical characterization beyond 5-corpus + informs Level 3 meta-LLM architecture priority.

**Research session:** holds for verdict + Level 3 meta-LLM drill landing; ships consolidated hierarchical scaling cap_map update post-empirical.
