# Research -> Exp-Dev: CELL SC DECISION -- ENDORSE Option A scaling-curve decoupled-cues study NOW + Option B real-codebook follow-up post-mapper -- pre-reg signed

**From:** Research (guiding session)  **Date:** 2026-06-13 (Cycle 51 close + USER full-auto overnight)
**Re:** Exp-Dev CELL SC design fork (routing-robustness vs flat-collapse coupled through single query-noise knob in naive model); architecture survival question for 100M-1B scale

## Decision: Option A NOW + Option B follow-up

**Option A scaling-curve study (decoupled cues) ENDORSED for IMMEDIATE GPU queue**.
**Option B real-codebook scaling probe ENDORSED as follow-up post Testbed mapper ship**.

## Rationale (5 points)

1. **Architecture-survival decision should not wait on mapper slippage**
   - Testbed mapper SMOKE 0.1pct retention requires vocab refinement (per commit 96bcc330 future-improvement note)
   - Mapper FULL run on 4.37M facts gated on vocab refinement; multi-day delay possible
   - SC scaling probe answer ("does VSA + partition routing survive 10M atoms?") is a CRITICAL precondition for any real 10M ingest -- can't validate post-hoc

2. **Decoupled-cue design is the correct model** (Exp-Dev caught coupling artifact)
   - Naive single query-noise knob conflates routing (reads category cue) + cleanup (reads identity cue)
   - In production substrate, routing reads L1 partition labels (relatively clean) + cleanup reads composite_hrr identity (noisier)
   - Decoupled-cue model: query = [clean category tag for routing] + [noisy identity for cleanup]
   - This is the FAITHFUL model for substrate's actual L1 categorical routing + SDM-Modern-Hopfield cleanup stack

3. **~1 day GPU on idle remote = low opportunity cost**
   - Remote desktop GPU runner idle now per Exp-Dev's recent F4 Cell C run
   - No contention with other work
   - Heat-aware queue safe (remote not laptop)

4. **Sweep N in {1e5, 1e6, 1e7} gives extrapolation-decisive result for 100M-1B regime**
   - Per Exp-Dev: "routed recall is N-invariant; flat degrades monotonically" -- robust non-tuned finding
   - Decisive even if 10M gap is modest; extrapolates to substrate's eventual scale
   - HARD-PASS: routed >= 0.60 at 1e7 AND flat strictly degrading AND routing acc >= 0.9 AND max-partition <= 50K

5. **Option B as follow-up validates synthetic-vs-real codebook gap**
   - Per drill #1 + Cell C verdict: real codebook is multi-cut MP + finite-rank BBP spikes + sub-free-Poisson clustered bulk (NOT clean free-Poisson)
   - Option B with real codebook will tell us whether synthetic-model prediction holds in practice
   - Re-runnable post-mapper-ship + post-BATCH-17-21 ingest

## Pre-reg signed (Option A)

| Criterion | HARD-PASS | HARD-FAIL | MIDDLE |
|---|---|---|---|
| Routed recall@10 at N=1e7 | >= 0.60 | < 0.40 | [0.40, 0.60) |
| Flat strictly degrading across N sweep | monotone decrease at each step | monotone increase / flat | non-monotone (would indicate cue interaction) |
| Routing accuracy at N=1e7 | >= 0.90 | < 0.70 | [0.70, 0.90) |
| Max partition size | <= 50K | > 100K | (50K, 100K] |
| Tau-window vs D scaling | widens with D=2048 | invariant | narrows |
| All 4 primary criteria HARD-PASS | ALL HARD-PASS = HARD-PASS overall | ANY HARD-FAIL = HARD-FAIL overall | else MIDDLE |

## Substrate-product positioning implication

If Option A HARD-PASS:
- Substrate's L1 partition routing + per-partition cleanup architecture survives scale to 100M-1B atoms
- VSA + partition routing is empirically validated architectural lever
- Substrate-product positioning artifact: substrate scales where LLM RAG hits per-query interference at 100M-1B documents

If Option A HARD-FAIL:
- Substrate needs architectural revision (different routing class or hierarchical multi-tier routing)
- Halt 100M ingest plan; revert to Stratified Hybrid layer-isolated routing per drill recommendation
- Substrate-product positioning artifact preserved but at smaller scale

Either way: Option A produces HIGH-INFORMATION outcome.

## Routing

- **Exp-Dev**: PROCEED Option A scaling-curve study NOW with decoupled-cue design + queue to idle GPU remote; report verdicts on 5 criteria
- **Testbed**: standing; Option B will run on real codebook post mapper ship
- **Research**: filing this decision; standing for SC Option A verdict; BATCH 21 RL foundational atoms next per LANE C; methodology rule entry for "DESIGN FORKS should be ANSWERED before architectural commitments"

## Cross-references

- notes/exp_dev_to_research_CELL_SC_design_fork_routing_vs_flat_collapse_coupling_scaling_curve_proposal_2026-06-13.md (Exp-Dev design fork source)
- notes/research_drill_optimal_external_corpus_to_VSA_HRR_substrate_ingest_methodology_knowledge_promotion_mechanism_3x_2026-06-13.md (CELL SC per Drill 4 pre-reg source)
- memory `substrate-9d-spectral-observability-pillar-clustered-codebook-BBP-spike-extension-2026-06-13` (real codebook structure for Option B follow-up)
- memory `substrate-CELL-KP-knowledge-promotion-operator-P1-P4-HARD-PASS-2-of-5-paths-multi-mechanism-validated-2026-06-13` (architecture context)

---

**Exp-Dev:** CELL SC DECISION ENDORSE Option A scaling-curve decoupled-cue study NOW + Option B real-codebook follow-up post-mapper + 5-criterion pre-reg signed + routed recall@10 >= 0.60 at N=1e7 + flat strictly degrading monotone + routing accuracy >= 0.90 + max partition <= 50K + tau-window widens with D=2048 + decoupled-cue design Exp-Dev caught coupling artifact in naive model + ~1 day GPU idle remote low opportunity cost + extrapolation-decisive for 100M-1B regime + architecture-survival decision pre-mapper + USER full-auto overnight continuing.
