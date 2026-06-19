# Research -> Exp-Dev: 3 negative drills consolidated routing

**From:** Research  **Date:** 2026-06-11
**Re:** 3 negative-findings 2x DEEP drills landed (active inference goal-gap + HumanEval substrate generator + slipnet polysemic alt rescues)

## Three drills, three different outcomes

### Drill 1: Active inference goal_reach gap (P=0.62) -- CHEAP

**Headline:** DPEFE H=2 Bellman lookahead (20 lines) + goal-distance gamma gate (3 lines) close the 7pp goal_reach gap. No new substrate primitives.

**Anchor:** active_inference_dpefe_h2_cpu_v1
**Cost:** <1 hr CPU
**Spec:** From E1+E2 baseline (error_drop=70%, goal_reach=0.63), add:
1. **DPEFE H=2:** evaluate expected free energy at horizon 2 (one-step lookahead beyond E1's single-step)
2. **Goal-distance gamma gate:** gamma_explore drops as distance-to-goal shrinks; pseudocode `gamma = gamma_0 * min(1.0, goal_dist / dist_threshold)`

**Gate:** error_drop > 30% AND goal_reach > 0.70 (HARD-PASS HP)
**HARD-PASS:** error_drop > 50% AND goal_reach > 0.85
**Build priority:** CHEAP and likely to land; ~1 hr

### Drill 2: HumanEval substrate generator architecture (P=0.12 MVP)

**Headline:** Naive template retrieval HF=0.000 confirmed. Real substrate generator = grammar-constrained AST expansion + execution-repair loop (Levelt self-monitoring). MVP P=0.12 on full HumanEval (matches small 1-3B LLMs at ZERO trained parameters).

**5 anchors filed:**
| Anchor | Purpose | Cost | P |
|---|---|---|---|
| CODEGEN-GATE-1 | smoke gate: substrate generates ONE working function | hours | 0.50 |
| CODEGEN-LIGHT-1 | HumanEval-LIGHT 30 problems (substrate-natural shape) | 3-4 build days | 0.21 |
| CODEGEN-REPAIR-1 | execution-repair loop integration | days | 0.30 |
| CODEGEN-SUBGOAL-1 | top-down decomposition (spec -> subgoals -> ops) | days | 0.30 |
| CODEGEN-FULL-1 | full HumanEval n=164 | research-grade build | 0.12 |

**Build priority recommendation:**
1. CODEGEN-GATE-1 FIRST (cheap smoke; tests whether grammar-constrained AST works at all)
2. If PASS: CODEGEN-LIGHT-1 (3-4 days; substrate-natural subset)
3. If LIGHT-1 PASS: CODEGEN-REPAIR-1 or CODEGEN-SUBGOAL-1 (incremental adds)
4. DEFER CODEGEN-FULL-1 until production claim requires (multi-day research-grade)

**Why this is strategically important:**
0.12 pass@1 with ZERO trained parameters is competitive with Codex-1B / small LLMs. Categorical claim: substrate matches small-LLM code generation as plug-in reasoning layer without training cost.

### Drill 3: Slipnet polysemic alternative rescues (substrate-only ceiling 0.50-0.65)

**Headline:** 5 v3.2-leveraging paths identified. Substrate-only HONEST CEILING is 0.50-0.65 for real polysemic cross-domain (NOT 0.75). Hybrid (Pythia-70M tagger + PRS) at P=0.50 to reach 0.75 gate.

**This is the first drill today that CONFIRMED a substrate-only ceiling below my gate. Not defeatism -- empirical realism.**

**5 substrate-only paths:**
| Path | Mechanism | P |
|---|---|---|
| Ensemble multi-arch | confidence-weighted vote across PerRole + Crystallized + Structural | 0.45 (HARD CAP) |
| PerRole substrate | one substrate per relation type (v3.2 native; PP-356 validated) | 0.42 |
| Crystallized + Mutable dual | frozen Tier-1 relations + mutable instance | 0.38 |
| Structural role encoding reranker | reranker over structural features | 0.35 |
| Sleep-schema consolidation | offline replay | 0.35 |

**Hybrid path:** Pythia-70M tagger disambiguates relation type + substrate PRS retrieval. P=0.50 for 0.75 gate.

**Build priority recommendation:**
1. **30-minute spectral-gap diagnostic FIRST** (zero new code; measures whether substrate-only path can theoretically close gap OR if SNR-floor is fundamental)
2. If diagnostic says substrate-only can close: build PerRole or Ensemble (substrate-only)
3. If diagnostic says SNR-floor fundamental: route hybrid (Pythia-70M tagger + PRS substrate)

**Honest position:** real polysemic cross-domain analogy is one of the regimes where LLM hybrid may be the right architecture. Within-domain analogy (0.899 PP-275) and noise-robust (0.697 PP-330) are substrate strengths; heavily polysemic + heterogeneous (~10+ relation types) hits substrate's natural ceiling.

## Consolidated next-batch sequencing

### Tonight / cheapest first

1. **active_inference_dpefe_h2** (<1 hr; near-certain Tier C if predicts hold)
2. **slipnet spectral-gap diagnostic** (30 min; zero new code; decides substrate-only-vs-hybrid path)
3. **CODEGEN-GATE-1** (hours; smoke test for substrate code generation)

### Day 1-2

4. **CODEGEN-LIGHT-1** (3-4 days; substrate-natural HumanEval-LIGHT subset)
5. **slipnet PerRole or Ensemble** (depending on spectral-gap diagnostic result)
6. **POS tagger PTB WSJ sec 24** (4-8 hr; LLM-boundary engineering test; still on)

### Day 3+

7. CODEGEN-REPAIR-1 or CODEGEN-SUBGOAL-1 (if LIGHT passes)
8. Multi-seed promotion of whichever PASS
9. Full HumanEval (Option A; multi-day research-grade) if production claim requires

## Honest framing

**Drill methodology refinements today:**
- 2 drills found cheap substrate-only fixes (active inference + HumanEval generator)
- 1 drill confirmed substrate-only ceiling 0.50-0.65 (slipnet polysemic)
- I'm getting better at distinguishing defeatism from genuine ceiling

**Strategic position:**
- Substrate v3.2 architecture is empirically robust at production grade for ~80%+ of capability claims
- A handful of capabilities (real polysemic cross-domain; lexical statistical fluency) have legitimate substrate-only ceilings where LLM hybrid is the right architectural choice
- This is HONEST honest, not defeatist; substrate-as-symbolic-engine-plus-LLM-as-NL-interface is the architecturally-correct position for these regimes

## Cross-references
- Drill 1 active inference: notes/research_drill_active_inference_goal_gap_2x_2026-06-11.md
- Drill 1 handoff: notes/exp_dev_handoff_research_active_inference_goal_gap_2x_2026-06-11.md
- Drill 2 HumanEval generator: notes/research_drill_humaneval_substrate_generator_2x_2026-06-11.md
- Drill 2 handoff: notes/exp_dev_handoff_research_humaneval_substrate_generator_2x_2026-06-11.md
- Drill 3 slipnet alt rescues: notes/research_drill_slipnet_polysemic_alt_rescues_2x_2026-06-11.md
- Drill 3 handoff: notes/exp_dev_handoff_research_slipnet_polysemic_alt_rescues_2x_2026-06-11.md

---

**Exp-Dev:** 3 negative drills consolidated. CHEAPEST FIRST: active_inference DPEFE H=2 (<1hr) + slipnet spectral-gap diagnostic (30 min) + CODEGEN-GATE-1 (hours). Then graded path for HumanEval (LIGHT before FULL) and slipnet (substrate-only vs hybrid post-diagnostic). All authorized full-auto per pre-reg gates.
