# Routing -- Substrate hierarchical 5-corpus meta-training architecture empirical test

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Type:** Empirical test (5 sub-models + substrate aggregator; CPU)
**Source:** User question on "train 100 LLMs in parallel + train meta-LLM on those" 2026-06-04

---

## Capability question

Can substrate aggregate distilled outputs from N=5 specialized sub-LMs (each trained on a different domain corpus) such that the aggregated substrate state predicts next-token across ALL 5 domains better than any single sub-LM?

This is the smallest viable test of the hierarchical training architecture: parallel sub-models -> substrate aggregator -> optional meta-model.

If HP: substrate provides genuine hierarchical knowledge aggregation; opens flagship product direction (train many small models in parallel; aggregate via substrate; continual learning via single Hebbian writes).

---

## Pre-reg HP/MID/HF bands

**Anchor:** `substrate_hierarchical_5corpus_meta_v1_n4096`

**Setup:**
- 5 character-LMs each trained on different corpus subsets (e.g., Shakespeare; SciFi excerpts; News headlines; Technical documentation; Cooking recipes)
- Each sub-LM: ~10K params; N=512 substrate dimension; cf-RPE + Drosophila sparse architecture (today's Bundle A HP combo)
- Substrate aggregator: N=4096; bind(context_vec, domain_key) for each sub-LM output
- Test: held-out next-token prediction across ALL 5 domain test sets

**Cells:**
- Cell H1: each sub-LM individually evaluated on its OWN domain (baseline)
- Cell H2: each sub-LM evaluated on OTHER domains (cross-domain failure baseline)
- Cell H3: substrate aggregator evaluated on ALL domains (key test)
- Cell H4: substrate aggregator + per-domain deletion-cert test (audit primitive validation)

**HARD-PASS:**
- H3 substrate aggregator achieves BPC across all 5 domains better than:
  - Each sub-LM evaluated on OTHER domains (Cell H2 cross-domain baseline) AND
  - Substrate aggregator preserves 80%+ of each sub-LM's own-domain accuracy (vs Cell H1)
- AND H4 deletion-cert test: removing one domain's bindings preserves all other domains at >= 95% retention (algebraic guarantee per Ramsauer Theorem 1)
- AND 3/3 seeds converge

This validates: (a) substrate aggregates without information loss; (b) audit primitives preserved across aggregation.

**MIDDLE:** partial aggregation success (some domains preserved; others degraded); audit primitives partially preserved (deletion-cert >= 70% retention)

**HARD-FAIL:** substrate aggregator BPC > sub-LM cross-domain baseline (aggregation makes things worse, not better) OR deletion-cert < 50% retention (audit primitives broken)

## Resource

Local CPU. 5 small char-LMs + substrate Hebbian write is matmul-light.

## Cost ceiling

$0 CPU. Per-sub-LM training ~5-10 min. Substrate aggregation ~1-2 min. Total ~30-60 min wall for full pipeline.

## P_deflated (per today's methodology)

**P_algebraic = 0.55**: VSA binding + Hebbian aggregation is algebraically supported; HRR (Plate 1995) + ImageBind-class cross-modal binding precedent

**P_implementation:**
- P_convergence = 0.65: 5 small Hebbian writes + 1 substrate aggregation is straightforward
- P_budget = 0.50: substrate N=4096 vs 5 x sub-LM at N=512 is borderline capacity-fit
- P_no_subsumption = 0.85: W-modifying (Hebbian writes); not subject to NESS subsumption
- P_task_match = 0.55: bigram-class across 5 domains is at the K* ceiling
- Joint P_implementation ~ 0.16

**P_joint = 0.55 * 0.16 ~ 0.09 for clean HP**

Note: LOW joint P because budget + task-match are borderline at substrate-class scale. Even MIDDLE result is informative.

## Engineering scope

~6-10h:
- 5-corpus data collection + tokenization (~2h; can use HuggingFace datasets)
- 5 sub-LM training pipeline (~2h; reuses Bundle A cf-RPE + sparse scaffold)
- Substrate aggregator: bind(context, domain_key) + Hebbian write (~1-2h)
- Cross-domain evaluation harness (~1h)
- Audit primitive validation: deletion-cert test (~1h)

Total: ~6-10h engineering, ~30-60 min experiment wall.

## Strategic outcome

### If HP

- Substrate hierarchical aggregation EMPIRICALLY validated at smallest scale
- Opens flagship product direction: train 10-100 small models in parallel; aggregate via substrate
- Confirms substrate's audit primitives preserve across hierarchical composition
- Cap_map sub-property founding for "substrate as hierarchical meta-knowledge store"

### If MIDDLE

- Substrate aggregates partially; some domains preserved; identifies which domains compose well
- Inform scaling: increase N; adjust per-domain capacity allocation
- Audit primitives possibly broken at aggregation; characterize the failure mode

### If HF

- Substrate aggregation fundamentally broken at substrate-class scale
- Identifies the BARRIER (capacity? task complexity? domain conflict?)
- Doesn't kill the hierarchical idea but characterizes the empirical barrier
- Next-step: test with fewer domains (3 vs 5) or larger substrate (N=16384)

---

## What this is (plain language)

Train 5 small character-language-models, each on a different kind of text (Shakespeare, SciFi, News, Technical, Cooking). Each sub-LM learns to predict next character in its own corpus.

Then aggregate all 5 sub-LMs' learned knowledge into ONE substrate via Hebbian binding (each context bound to a domain key).

Test: can the aggregated substrate handle ALL 5 domains as well as the individual sub-LMs? Plus: can we DELETE one domain's contribution from the substrate without breaking the others (audit primitive)?

If yes: substrate is a genuine hierarchical aggregator. Opens path to "train 100 specialized models in parallel + aggregate via substrate" architecture.

If no: identifies the barrier (likely capacity at substrate-class scale).

---

## Strategic context

This connects to TWO research drills running in parallel:
1. Training-speed + hierarchical-architecture 2x drill (in flight; ~45 min)
2. Unified cross-modal substrate 2x drill (in flight; ~30 min)

Empirical result here anchors both drills' theoretical predictions.

If HP: substrate's product narrative expands to "hierarchical meta-training architecture for parallel-trained specialized models." This is potentially THE biggest product positioning we've identified.

If HF: confirms substrate-class scale is below the threshold for this architecture; need to test at larger scale OR identify the algebraic barrier.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: smallest viable test of hierarchical aggregation
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- Per [[feedback-small-scale-first-methodology]]: rung-1 5-corpus test before scaling
- Per [[feedback-verdicts-include-intuitive-explanation]]: plain language throughout
- ASCII-only

PROT-018: anchor uses `_n4096_v1` suffix
PROT-021: source=local CPU, run_mode=full, n_seeds=3

---

**END.**

**Exp-Dev:** ~6-10h engineering + ~30-60 min CPU wall. Reuses Bundle A scaffolds (cf-RPE + Drosophila sparse) + adds substrate aggregator + 5-corpus data + cross-domain eval. Verdict drives "substrate as hierarchical meta-training architecture" capability characterization.

**Orchestrator:** informed. Cap_map sub-property founding pending verdict.

**Research session:** holds for verdict; ships training-speed + hierarchical-architecture cap_map updates per drill + empirical synthesis.
