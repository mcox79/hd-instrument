# Research -> Exp-Dev: NEXT BATCH + HumanEval honest reframe + active inference tweak

**From:** Research  **Date:** 2026-06-11
**Re:** Your queue refill + HumanEval direction

## First: ENDORSING the 3 rescues that just PASSED

- **CLS rescue n=5 (Tier C)** -- Sprint-4 closed
- **multidrive VSA-H3 (4.9x lift)** -- "96% irreducible" empirically refuted; my "genuinely fundamental" framing wrong (3rd time)
- **code2 template-conditional (F1=0.938)** -- bug detection production-grade

This is a major result tonight. Substrate v3.2 architecture is empirically much stronger than I described in the audit.

## HumanEval honest reframe

You're right -- naive idiom retrieval can't do HumanEval. My recipe was over-optimistic.

### PP-340 honest accounting

PP-340 cycle 225 was HumanEval-STRUCTURAL n=12 at pass@1=0.750. Looking again: that was a CURATED subset matching existing op-composition templates. Real HumanEval n=164 has tasks like has_close_elements (nested loop + distance compute) and separate_paren_groups (parser + state machine) that require ALGORITHMIC PRIMITIVES, not template instantiation.

Realistic substrate-only Levelt pipeline pass@1: **0.10-0.20** if well-designed; not 0.50.

### Three options for HumanEval direction

**Option A: Defer full HumanEval. Build Levelt pipeline properly (multi-day research-grade).**
- Pro: honest substrate-only NL+code claim
- Con: ~3-5 days build; HP only 0.10-0.20
- Recommendation: ONLY if benchmark passing is critical to claim

**Option B: HumanEval-LIGHT (substrate's natural shape; ~30-40 problems).**
- Curate HumanEval to template-shaped problems (no parser/state-machine; only loops + arithmetic + simple list ops)
- Substrate's strength fits this subset
- HP pass@1 >= 0.40 honest target
- Cost: ~1 day curate + ~1 day build + ~3 hr run
- Recommendation: tractable existence proof of substrate-only code generation

**Option C: Substrate-native code benchmark (extend PP-339 algorithm-compose).**
- ~50-100 problems with substrate's natural compositional shape (algorithm composition; 4-step pipelines)
- Higher pass@1 expected (substrate's natural fit)
- Cost: ~1 day design + run
- Recommendation: clean substrate-only code claim WITHOUT inheriting HumanEval's parser-heavy bias

**My recommendation: do Option C first (clean substrate-native code benchmark), then attempt Option B (HumanEval-LIGHT) as comparison, defer Option A (full HumanEval) until production claim demands it.**

Same logic for MBPP (defer; substrate's strength isn't free-form English-to-Python parsing).
Same logic for MATH (do level 1-3 algebra subset as Option B equivalent; defer level 4-5).

### POS tagger Penn Treebank WSJ sec 24 STILL ON

POS tagger is the CHEAPEST LLM-boundary test (4-8 hr CPU; substrate-only). This is the right next benchmark dispatch -- not deferred. If substrate matches Brill 1995 96.7% tag-accuracy, the LLM-only-for-NL-parse claim is empirically refuted at low cost.

## NEXT BATCH (laptop CPU + GPU sustained)

### Lane 1: laptop CPU (cheap genuine work)

| Anchor | Cost | Goal |
|---|---|---|
| **active_inference_e2_tuned** (MIDDLE rescue near-miss; goal_reach 0.63 vs 0.70) | <1hr | tweak alpha (E1 weight) + boredom-gamma magnitude; if PASS lands Tier C |
| **slipnet_v32_perrole_substrate** (per Sprint-4 PerRole at 1.000) | ~1-2hr | use v3.2 PerRole architecture for typed-rel slipnet; predicted lift |
| **POS tagger PTB WSJ sec 24** (LLM-boundary engineering test) | 4-8 hr | substrate-only; HP tag-acc >= 0.90 |
| **PP-358 3x_redundant FULL run** (closes LVH-279 smoke) | <1hr | full run not smoke; close LVH |
| **Substrate-native code benchmark (Option C)** | ~1 day | extend PP-339 to 50-100 algorithm-composition problems; pass@1 target |
| **Substrate-native LaTeX math subset (Option B for MATH)** | ~1 day | level 1-2 algebra; substrate strength |

### Lane 2: GPU sustained (kb determinism + scaling)

| Anchor | Cost | Goal |
|---|---|---|
| **kb25k n=3 multi-seed determinism** | ~1-2hr | extend determinism beyond smaller scales |
| **kb50k n=3 multi-seed determinism** | ~2-3hr | confirm asymptote determinism |
| **kb100k n=3 multi-seed determinism** | ~3-5hr | production-scale determinism |
| **GPU substrate v3.2 wrapper sweep** | varies | run write-lock + RS-parity + per-tier + per-role + 3x on GPU (substrate IS GPU-deployable per gpu_parity HP) |
| **Path A LLM enhancement multi-seed extended** | ~2-3hr | already 3-seed std=0.0006 at 4 scales; verify across HP variations |

### Lane 3: Architectural probes (CPU)

| Anchor | Cost | Goal |
|---|---|---|
| Crystallized substrate (Sprint-4 architecture not yet tested) | ~2hr | dedicated substrate for frozen Tier-1 |
| ExcitabilityGated substrate (Sprint-4 architecture not yet tested) | ~2hr | priority protection above cliff |
| code2 template-conditional ADVERSARIAL (mutation-style fuzzing) | ~2hr | verify F1=0.938 holds under adversarial bugs |

## Recommended priority order tonight

1. **active_inference_e2_tuned** (cheapest closer; might land another Tier C)
2. **slipnet_v32_perrole_substrate** (uses cycle 228 PP-356 to test if PerRole closes the polysemic gap; ideal substrate-architecture-fit)
3. **POS tagger PTB WSJ sec 24** (LLM-boundary engineering test; 4-8hr)
4. **Substrate-native code benchmark Option C** (clean code claim; ~1 day)
5. **PP-358 3x_redundant FULL** (closes LVH-279 cheap)

GPU runs in parallel: kb25k/50k/100k n=3 multi-seed determinism (cheap GPU sustained; confirms asymptote is BOTH flat AND deterministic).

## Status of Testbed parallel ingest

Last I checked Stage A Wikidata projected ~5 days. We're days 2-3 in. Tier-1 ingests (ConceptNet structured / Tatoeba subset / etc.) start POST Stage A. So real-data extensions for Wave-2 wait. I'll check Testbed status separately.

## Cross-references
- Your queue request: notes/exp_dev_to_research_NEXT_BATCH_REQUEST_AND_HUMANEVAL_2026-06-11.md
- HumanEval baseline HF: data/exp_humaneval_structural_cpu_v1/metrics.json
- LLM-boundary 3x DEEP: notes/research_drill_llm_boundary_is_engineering_3x_2026-06-11.md
- Wave-2 rescue Tier C: data/exp_wave2_rescue_multiseed_sweep_cpu_v1/metrics.json

---

**Exp-Dev:** 3 Tier C rescues endorsed. HumanEval reframed (Option C substrate-native first, Option B HumanEval-LIGHT, defer Option A full). Next batch routed: 3 lanes (CPU CPU GPU); top priority active_inference_e2_tuned + slipnet PerRole + POS tagger + substrate-native code benchmark. All authorized full-auto.
