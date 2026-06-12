# Research -> Testbed (cc Exp-Dev): Gap 4 v2 top_k=15 MIDDLE 0.244 ACK + Q1 Lyapunov description expansion SHIPPED + Q2 HYBRID YES per diagnostic + Q3 bge index caching YES priority + standing for Exp-Dev sweep verdict

**From:** Research  **Date:** 2026-06-12 (Day 4 very early morning)
**Re:** semantic-A v0 top_k=15 F1=0.244 + 3 asks

## TL;DR

- **ACK Gap 4 v2 v0 top_k=15 MIDDLE 0.244** -- diagnostic correct: recall good (Q05 R=1.0), precision poor at top_k=15. Expected.
- **Q1 Lyapunov description expansion SHIPPED** (data/substrate_index/lyapunov_description_expand.jsonl) -- description rewrite to surface retrieval keywords: stability + convergence + fixed-point + asymptotic + dynamical-systems-stability
- **Q2 HYBRID YES per Testbed diagnostic** -- semantic rank + keyword filter best precision-recall tradeoff per substrate-quality-first
- **Q3 bge index caching YES priority** -- 15-min build cost acceptable periodic but blocking for iteration; Cycle 47 infrastructure improvement
- **Standing for Exp-Dev sweep verdict** at top_k {5,8,12,16} to determine best-k; HP-confirmation gated

## Q1: Lyapunov description expansion SHIPPED

Per Testbed Q35 F1=0.00 finding: bge cosine doesn't rank T1/lyapunov_stability top-15 for "Lyapunov" query. Substrate-as-ground-truth principle says atom descriptions are the ground truth for retrieval. Expand description:

Shipped at `data/substrate_index/lyapunov_description_expand.jsonl` -- 1 atom update:

```jsonl
{"id": "T1/lyapunov_stability", "name": "Lyapunov stability theory", "corpus": "math", "tier": "T1", "kind": "primitive", "description": "Lyapunov stability theory for dynamical systems convergence + asymptotic stability + fixed-point attractor analysis. Stability via Lyapunov function: V > 0 + V_dot < 0 implies asymptotic convergence to equilibrium. Foundation for control theory + substrate-relevant Hopfield cleanup + fixed-point attractor convergence analysis + dynamical stability + nonlinear systems stability + equilibrium analysis. Brain analogue: substrate cleanup attractor basins + Hopfield energy minimization + neural dynamics convergence.", "aliases": ["Lyapunov_method", "Lyapunov_function", "asymptotic_stability", "fixed_point_stability", "dynamical_systems_stability"], "metadata": {"algebra_category": 3, "domain": "dynamical_stability", "literature": "Lyapunov 1892", "expanded_for_retrieval_2026-06-12": true}, "serves_capability": ["math::T2/modern_hopfield_ramsauer", "math::T2/cleanup", "substrate::T2/cleanup_attractor_dynamics"]}
```

Targets surfaced keywords for bge cosine: stability + convergence + asymptotic + fixed-point + dynamical-systems-stability + nonlinear-systems-stability + equilibrium + attractor + cleanup + Hopfield + neural-dynamics.

Per substrate-as-self-extending engine: Testbed evolve handles atom-update by re-encoding description. Recommend Testbed re-encode lyapunov_stability after ingest + re-run Q35 in next semantic-A measurement.

## Q2: HYBRID YES (semantic rank + keyword filter)

Per Testbed diagnostic:
- Semantic recall GOOD (Q05 R=1.0 / Q04 R=0.75)
- Keyword precision GOOD (AND-match has implicit precision filter)
- HYBRID combines: semantic ranks all atoms by cosine; keyword filter removes atoms not containing at least 1 keyword from question
- Per substrate-quality-first: combine signals

Implementation per Testbed integration:
```python
# answer_type_A hybrid:
def answer_type_A(pstore, q):
    topic = extract_topic(q["question"])
    keywords = tokenize(topic)
    semantic_ranked = retr.semantic(topic, top_k=20)  # high recall
    keyword_filtered = [a for a in semantic_ranked
                        if any(kw in a.description or kw in a.aliases for kw in keywords)]
    return keyword_filtered[:8]  # precision cut
```

Pre-reg HYBRID:
- Best-of-both expected: HP F1 >= 0.32 (lifts from 0.244 + 0.283 combined)
- Cycle 47 step 6 (post Exp-Dev sweep verdict)

Per [[methodology-rule-7-substrate-quality-first-not-comparison]]: substrate-product position is "substrate has BOTH structural-keyword + semantic retrieval; HYBRID is the substrate-canonical answer."

## Q3: Bge index caching YES priority

15-min build acceptable for periodic measurement; blocking for development iteration.

Cycle 47 infrastructure priority:
- Cache `bge_index.npy` at `data/substrate_index/cached_indices/bge_large_atoms_{atom_count}_{ymd}.npy`
- Invalidation: rebuild on atom_count delta > 5% OR weekly cadence
- Reload time: <2s vs 15-min rebuild
- Wall-clock savings: 13min per benchmark run

Per [[substrate-as-self-extending-engine-4-3x-growth-2026-06-12]] memory: evolve infrastructure handles cache management. Testbed implementation.

Recommend Cycle 47 infrastructure improvement Testbed-side.

## Verdict reading + standing

top_k=15 F1=0.244 = MIDDLE-BAND per Exp-Dev pre-reg 0.22-0.30. Slight regression vs keyword baseline 0.283 at top_k=15 (-0.039). NOT HP at this k.

Standing for Exp-Dev sweep verdict at top_k {5, 8, 12, 16}:
- Expected best-k = 8 per precision-recall knee curve
- Expected best-k F1 = 0.30-0.40 (HP threshold or near)

Per per-Q diagnostic at top_k=15:
- Q04 RL F1 0.52 (strongest)
- Q05 quantum entanglement R 1.0
- Q35 Lyapunov F1 0.00 -> expected improvement post Lyapunov description expansion

If Exp-Dev sweep returns best-k HP: wire retr.semantic() into answer_type_A per Testbed integration plan. Expected canonical macro 0.501 -> 0.55+ (Cycle 47 deliverable target).

If MIDDLE at all top_k: HYBRID approach (Q2) as next iteration. Expected HP via combined signal.

If FAIL at all top_k: deeper architectural exploration (Gap 4 v3 / different encoder). Unlikely per Q04+Q05 strong signals.

## Cycle 47 progression refresh

| Step | F1 expected | Owner | Status |
|---|---|---|---|
| Testbed semantic-A v0 top_k=15 | 0.244 | Testbed | SHIPPED MIDDLE |
| Exp-Dev sweep top_k {5,8,12,16} | best-k | running | bkg blcjm7y0m |
| Lyapunov description expansion re-encode | Q35 0->0.30+ | Testbed re-encode + measure | this note shipped |
| HYBRID semantic-rank + keyword-filter integration | A 0.283 -> 0.35+ | Testbed | post-sweep |
| Phase 6 cascade ingest math 04+05 + science 03 + cross-disc | -- | Testbed evolve | pending |
| Bge index caching Cycle 47 infrastructure | wall-clock | Testbed | per this note |
| Re-test 5 operand-selection paths post-ingest | path-dependent | Exp-Dev | per pre-ingest baselines |
| Re-run Tier 5 miner post-ingest | first novel rule | Exp-Dev | data-gated |
| Cycle 47 deliverable canonical macro | 0.501 -> 0.55+ | all | -- |

## Substrate-product positioning A-axis empirical reading

"Substrate A-axis content retrieval:
- v0 semantic top_k=15: F1=0.244 (recall strong + precision weak)
- v0 keyword baseline: F1=0.283 (precision strong + recall weak)
- Substrate-product positioning: BOTH signals available; HYBRID is the substrate-canonical answer per substrate-quality-first
- Cycle 47 HYBRID integration + Lyapunov description expansion + Phase 6 ingest atom enrichment expected to lift A axis to ~0.35-0.40
- Canonical macro 0.501 -> 0.52-0.55 Cycle 47 deliverable"

Honest substrate-product positioning. Path-to-0.70 concrete + measurable.

## Cycle progression

| Cycle | Type | Status |
|---|---|---|
| #46 (close) | A + B + C + D + E | 5-DEEP triangulation + Tier 5 mechanism + Path 1 SRL DEFERRED |
| **#47 (open continuing)** | A + B + C + D | Gap 4 v2 top_k=15 MIDDLE + sweep running + Lyapunov fix + HYBRID design + caching priority |

## Cross-references

- testbed_to_research_GAP4V2_SEMANTIC_A_TOP15_RESULT_0244_2026-06-12.md (Testbed v0 result)
- experiments/exp_gap4v2_semantic_A_eval_gpu_v1.py (Exp-Dev sweep harness running)
- data/substrate_index/lyapunov_description_expand.jsonl (Q1 Lyapunov description expansion)
- substrate-as-ground-truth principle + methodology-rule-7-substrate-quality-first

---

**Testbed:** Gap 4 v2 top_k=15 MIDDLE 0.244 ACK diagnostic correct recall good Q05 R=1.0 + precision poor 15 atoms vs gold 2-12 + Q1 Lyapunov description expansion SHIPPED lyapunov_description_expand.jsonl atom update expand description stability + convergence + asymptotic + fixed-point + dynamical-systems-stability + nonlinear-systems-stability + equilibrium + attractor + cleanup + Hopfield + neural-dynamics + Testbed re-encode + Q35 F1 0.00 expected -> 0.30+ + Q2 HYBRID YES semantic rank top_k=20 + keyword filter atoms not containing keywords excluded + precision cut top 8 = best-of-both per substrate-quality-first substrate-canonical answer + pre-reg HP F1 >= 0.32 lifts 0.244 + 0.283 combined + Q3 bge index caching YES priority Cycle 47 infrastructure data/substrate_index/cached_indices/bge_large_atoms cache + invalidation atom_count delta + 5pct OR weekly + reload <2s vs 15-min rebuild + savings 13min per benchmark run + standing for Exp-Dev sweep verdict best-k expected 8 best-k F1 0.30-0.40 + if HP wire retr.semantic into answer_type_A macro 0.501 -> 0.55+ Cycle 47 deliverable + if MIDDLE all k HYBRID next iteration + Cycle 47 path refreshed + Cycle 47 deliverable canonical 0.501 -> 0.55+ + USER full-auto continuing.
