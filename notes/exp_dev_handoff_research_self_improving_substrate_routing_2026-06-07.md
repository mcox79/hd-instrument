# exp_dev hand-off -- research: self-improving substrate routing architecture

**Filed:** 2026-06-07 by research sub-agent (3x deep drill cycle).

**Trigger:** Research drill delivered architecture spec for self-improving routing composition (Pattern-B + continual learning + sleep defrag + adversarial detection + router + bridge cache + LLM fallback). Three cheap pre-tests identified; dispatching to exp_dev for anchor design and queue placement.

**Research note path:** d:/AI/hd-instrument/notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md

**Pause state:** Check data/orchestrator_paused.flag before dispatching. If paused, queue handoff for next active cycle.

**Per [[feedback-no-experiment-design-in-prompts]]:** This hand-off names ANCHORS + POINTERS only. exp_dev designs ALL of: N, M, K, seed count, threshold bands, query count, queue choice (Tier A/B/C), anchor name, ETA, smoke profile, FULL profile. Research does NOT specify numerical parameters.

---

## Anchor Candidates (rank-ordered)

### Anchor 1: Cold-Start Router Simulation (Zipfian accumulation curve)
**Anchor pointer:** Research note Section 10, Pre-Test 1 (Cheap, ~2 hours). Synthetic Zipfian query distribution over bridge entity vocabulary; measure fast-path fraction X(Q) and bridge coverage C(Q) at increasing query counts Q.
**Substrate-product reading:** Validates the bridge accumulation model before any integration work. If C(Q) and X(Q) grow as predicted by the power-law saturation model, the self-improving routing claim is structurally supported. If they do not grow, the architecture needs revision before engineering investment. This is the cheapest gate in the pipeline.
**Tier hint:** Local / CPU. No GPU needed. Pure Python simulation.
**Why now:** Must pass BEFORE Pre-Test 3 (production encoder run) per drill-pretest-required memory rule. Unblocks the medium and expensive pre-tests. Zero cloud cost.

### Anchor 2: Smoke Router on HotpotQA Subset (real query distribution)
**Anchor pointer:** Research note Section 10, Pre-Test 2 (Medium, ~1 week). Take cycle 167 sleep defrag stack + add bridge frequency counter + basic threshold router. Run against HotpotQA subset. Measure fast-path fraction growth over Q={50, 100, 200, 500} queries.
**Substrate-product reading:** Validates that the accumulation mechanism works on a real (non-synthetic) query distribution. HotpotQA bridge entity distribution is realistic for enterprise multi-hop use cases. If X grows from ~0.10 to ~0.25 over 500 queries, the warm-up curve is real. If X stays flat, the threshold calibration or the bridge detection logic needs debugging.
**Tier hint:** Remote CPU preferred (cycle 167 defrag stack runs on CPU). Possibly local GPU acceptable. HotpotQA subset (500 queries) is lightweight.
**Why now:** Can run in parallel with Anchor 1. Pre-Test 1 validates the model; Pre-Test 2 validates the implementation. Together they cover both the analytical and empirical gates.

### Anchor 3: Bridge Cache Growth on Production Encoder (small-scale equilibrium)
**Anchor pointer:** Research note Section 10, Pre-Test 3 (Small-Scale Equilibrium, ~2-3 weeks). Production Llama-1B BASE encoder (left-pad, PCA whitened). 5K queries from HotpotQA or TriviaQA. Measure C, X, effective latency at Q={500, 1K, 2K, 5K}. One sleep defrag pass every 500 queries.
**Substrate-product reading:** Validates the full integration at small scale. This is the Pythia sanity-check analogue (per feedback-pythia-sanity-check-before-cloud memory rule) before any large-scale cloud run. If bridge cache growth appears on the production encoder with real query vectors, the self-improving architecture is empirically validated at the mechanism level. If not, the encoder projection or the bridge frequency counter logic is broken.
**Tier hint:** Remote GPU (production encoder required for real query vectors). Budget 1 cloud run. MUST be gated on Anchor 1 PASS per drill-pretest-required memory rule.
**Why now:** Is the gate before any large-scale (Q=100K) self-improving deployment test. Do not run before Anchor 1 passes.

---

## Context Pointers

- Research note (full architecture spec, pre-test designs, risk analysis): d:/AI/hd-instrument/notes/research_drill_self_improving_substrate_routing_3x_2026-06-07.md
- Cycle 167 sleep defrag integration (Components C+D validated): check notes for cycle 167 verdict
- Cycle 165 cold-start bridge coverage baseline (~55-70%): check notes for cycle 165 verdict
- Cycle 158 Pattern-B unbind HP acc=1.0: check notes for cycle 158 verdict
- Cycle 154 continual learning HP: check notes for cycle 154 verdict
- Production architecture locked file: d:/AI/hd-instrument/memory/production_architecture_locked_2026-06-07.md
- Afternoon post-compaction brief (most recent state): d:/AI/hd-instrument/notes/research_POST_COMPACTION_BRIEF_2026-06-07_afternoon.md

---

## Contract

exp_dev is authorized to:
1. Design and queue Anchor 1 (cold-start simulation) immediately -- local/CPU, no cloud cost.
2. Design and queue Anchor 2 (HotpotQA smoke router) -- remote CPU, low cost.
3. Design and queue Anchor 3 (production encoder bridge cache) ONLY IF Anchor 1 has PASSED -- remote GPU, moderate cost.

exp_dev is NOT authorized to:
- Design large-scale (Q=100K+) deployment tests before Anchor 3 PASSES.
- Skip the Anchor 1 gate for Anchor 3.
- Combine all three into one run (they must be staged per the drill-pretest-required rule).

---

## Autonomy Declaration

exp_dev decides all of: N, M, K, query count Q, threshold values theta_fast and theta_slow, seed count, queue routing (Tier A/B/C), anchor names, smoke vs full profile, timing. The research note provides the PREDICTION STRUCTURE (pass/fail criteria); exp_dev translates those into concrete numerical experiment designs using the hd-instrument parameter conventions.
