# Research -> Exp Dev companion handoff — SWR-cascade design for multi-timescale replay

**From**: Research (2x adjacency-cascade drill — biology side)
**To**: Exp Dev (next cycle that picks up multi-timescale replay design)
**Source analysis**: [research_swr_cascade_drill_2026-05-24.md](research_swr_cascade_drill_2026-05-24.md)
**Companion prior**: [research_pt_cascade_drill_2026-05-24.md](research_pt_cascade_drill_2026-05-24.md) (physics side; found CONTINUOUS sqrt(N) scaling — no discrete optimum)
**Pause state**: respect `data/orchestrator_paused.flag` per [[feedback-obey-user-pause-explicitly]]
**Role contract compliance**: per [[feedback-no-experiment-design-in-prompts]] this handoff specifies TASK + WHY + FALSIFIER STRUCTURE + SCRIPT-BASE POINTERS only; exp_dev owns anchor names, sweep grids, threshold numerics in substrate units, queue choice, ETA, and pre-committed cap_map decisions.

---

## Why this hand-off exists

The PT-cascade drill found that ~40 years of physics literature gives a CONTINUOUS sqrt(N) replica-count scaling rule with no discrete optimum. The SWR-cascade drill examined whether neuroscience corroborates or refutes the basin-discrete framing implicit in our substrate's multi-timescale replay design.

**Net answer**: biology DOES corroborate discreteness (Latchoumane 2017 optogenetic causality, Helfrich 2025 epilepsy cascade-failure), but DOES NOT independently establish that depth=3 is OPTIMAL — only that the depth that exists in biology is causally engaged.

This handoff translates the SWR-cascade drill's five falsifiable predictions into substrate-design starting points. Exp_dev decides parameters and ships per role contract.

---

## Priority order (Research's leverage ranking; exp_dev may revise)

| # | Direction | Priority | Type | Default queue (exp_dev may revise) |
|---|---|---|---|---|
| 1 | **Pred-1 — Cascade-depth sweep N ∈ {1..6} (basin-discrete answer)** | TOP | Empirical: depth sweep on continual-learning benchmark | overnight_queue (depth sweep is compute-heavy) |
| 2 | **Pred-3 — Phase-locked vs phase-random replay (Latchoumane analog)** | HIGH | Empirical: timing-structure ablation at fixed depth | overnight_queue |
| 3 | **Pred-5 — Hard-gated (encoding/replay exclusive) vs mixed mode** | HIGH | Empirical: gating ablation | overnight_queue or remote_cpu_queue if mechanism is cheap |
| 4 | **Pred-2 — Frequency-ratio sweep at fixed N=3** | MEDIUM | Empirical: ratio sweep | overnight_queue |
| 5 | **Pred-4 — Inter-replay refractory interval sweep** | MEDIUM | Empirical: refractory sweep | remote_cpu_queue if cheap; overnight_queue if expensive |

---

## Pred-1 — Cascade-depth sweep (HIGHEST LEVERAGE)

**Scope**: Compare substrate continual-learning performance with replay cascades of depth N ∈ {1, 2, 3, 4, 5, 6} (single-timescale → six nested timescales). Measure forgetting / retention / interference on the existing Bet B benchmark family (or substrate-appropriate equivalent).

**Why this matters**: this is the single experiment that distinguishes PT-physics (smooth sqrt(N) scaling) from biology (discrete knee at N=3) AT THE SUBSTRATE LEVEL. The result tells us which world our substrate lives in.

**Falsifier statements (exp_dev pre-registers numerical bounds per [[feedback-envelope-expansion-fail-bands]])**:
- HARD-PASS: Performance curve has a KNEE at N=3 (N=3 within X% of N=6 while N=2 is >Y% behind N=3). Confirms biology-style discrete-depth advantage.
- HARD-FAIL HF1: N=3 within X% of N=2 (no benefit going from 2 to 3 levels). Cascade depth not special.
- HARD-FAIL HF2: Performance scales smoothly as sqrt(N) with no knee. Substrate follows PT-physics, not biology.
- HARD-FAIL HF3: Performance keeps improving linearly past N=3. Optimum is at higher depth than biology uses.
- MIDDLE BAND: N=3 beats N=2 by X-Y% and N=6 beats N=3 by similar — partial discreteness, no sharp knee.

Exp_dev sets X, Y in substrate units; biology's effect sizes are not directly translatable.

**Script-base reuse**: continual-learning benchmarks already in `experiments/exp_wave14_betB_*` family; cascade-depth is a wrapper over existing replay machinery. Exp_dev selects base script.

**Discipline citations**:
- Per [[feedback-no-smoke]]: pre-reg both HARD-PASS and HARD-FAIL numerical bounds before run.
- Per [[feedback-strategy-spec-formula-selftests]]: if depth-sweep uses closed-form scaling formula, include (input → expected output) selftest cells.
- Per [[feedback-rehabilitation-after-rejection]]: if HARD-FAIL HF2 (smooth scaling), file 3-5 rescue sketches before closing the basin-discrete hypothesis.

---

## Pred-3 — Phase-locked vs phase-random replay (Latchoumane analog)

**Scope**: At fixed N=3 cascade, compare PHASE-LOCKED replay (level-3 events triggered only during level-2 active phase; level-2 only during level-1 up-phase) vs PHASE-RANDOM replay (same event rates, random relative phase). Same total compute budget for both conditions.

**Why this matters**: Latchoumane 2017 (Neuron) is the gold-standard biology causality result — in-phase thalamic spindle stimulation improves consolidation while out-of-phase does NOT, despite identical event counts. If substrate replicates this, the DISCRETE TIMING STRUCTURE matters, not just event rate. If substrate doesn't replicate, our replay is content-driven, not timing-driven.

**Falsifier statements**:
- HARD-PASS: Phase-locked beats random by X% on consolidation metric, replicates across 3 seeds.
- HARD-FAIL HF1: Phase-locked indistinguishable from random. Latchoumane optogenetic effect does NOT transfer.
- HARD-FAIL HF2: Random outperforms locked. Substrate has different optimal structure than biology.
- MIDDLE: Phase-locked wins on some seeds, loses on others — high variance, no clear effect.

**Script-base reuse**: extends Pred-1 cascade-depth machinery with phase-control parameter.

---

## Pred-5 — Hard-gated vs mixed-mode replay (SWR-theta exclusion analog)

**Scope**: Compare HARD-GATED replay (encoding-OFF during replay phase, replay-OFF during encoding phase — biology's SWR-theta state exclusion) vs MIXED replay (concurrent encoding + replay with proportionally reduced per-event rates).

**Why this matters**: Biology enforces a hard binary gate between encoding-mode (theta) and consolidation-mode (SWR). This prevents interference between new encoding and replay-driven consolidation. If substrate also benefits from hard gating, our continual-learning architecture should enforce mode-exclusivity, not interleave.

**Falsifier statements**:
- HARD-PASS: Hard-gated beats mixed by X% on continual-learning interference benchmark, stable advantage across 3 seeds.
- HARD-FAIL HF1: Mixed matches or beats hard-gated. Substrate doesn't suffer encoding-replay interference; biology's gating is overkill.
- HARD-FAIL HF2: Both fail differently (gated under-utilizes; mixed suffers interference) — partial-mix beats both extremes.

**Script-base reuse**: requires explicit encoding/replay scheduling; exp_dev selects base script.

---

## Pred-2 — Frequency-ratio sweep at fixed N=3

**Scope**: With N=3 cascade fixed, sweep adjacent-level timescale ratios r ∈ {2, 3, 5, 6, 10, 12, 20, 50}. Biology uses ratio ~6 (ripple/spindle in human) or ~12 (in rodent) between fastest two levels, and ~19 (spindle/SO) between slowest two. Test whether substrate has a similar sweet spot.

**Why this matters**: Biology's cascade is NOT uniform-geometric (r constant across levels). The substrate may also benefit from NON-UNIFORM ratios. If sweet spot exists at r in [5, 15], that corroborates biology's engineered-cascade hypothesis. If performance is monotone in r or insensitive, biology's ratio precision is epiphenomenal in substrate.

**Falsifier statements**:
- HARD-PASS: Best performance at r in [5, 15]; performance at r=2 and r=50 each >X% below.
- HARD-FAIL HF1: Performance monotonically increasing in r (no sweet spot — bigger is always better).
- HARD-FAIL HF2: Performance flat across r (no sensitivity at all).
- MIDDLE: Sweet spot exists but outside [5, 15] — e.g. at r=3 or r=25 — partial corroboration with different scaling.

**Script-base reuse**: same Pred-1 cascade machinery with ratio parameter.

---

## Pred-4 — Inter-replay refractory interval sweep

**Scope**: Sweep inter-replay-interval τ_ref ∈ {0.5x, 1x, 3x, 10x, 30x} the duration of a single replay event. Biology's spindle refractoriness is ~3–10x the spindle duration.

**Why this matters**: Biology's spaced-replay rhythm (3–4 s inter-spindle interval at ~0.2–0.3 Hz mesoscale) is hypothesized to prevent interference between successive memory reactivations. If substrate also benefits from spaced replay with τ_ref in [3x, 10x], that's a direct mapping.

**Falsifier statements**:
- HARD-PASS: Peak performance in τ_ref ∈ [3x, 10x] band, with >X% degradation at 0.5x and at 30x.
- HARD-FAIL HF1: Monotonic — shorter is always better (interference is not a real failure mode).
- HARD-FAIL HF2: Monotonic — longer is always better (no upper bound; spaced replay no benefit).

**Script-base reuse**: extends replay-scheduling machinery from Pred-1/Pred-3.

---

## Cross-cutting discipline notes

Per [[feedback-composition-classification]]: these five drills are INDEPENDENT (SCORE-level composition) — they can be run as separate sweeps without cross-coupling. Pred-1 should run FIRST to establish whether discrete-depth is real; if HARD-FAIL HF2 (continuous scaling), Preds 2-5 become much lower priority (the biology→substrate mapping is rejected at the foundational level).

Per [[feedback-ship-before-dependency-verified]]: verify substrate has the continual-learning benchmark infrastructure for Pred-1 BEFORE queueing the depth-sweep. If benchmark is itself shaky, ship a smoke run first.

Per [[feedback-pipeline-pacing]]: Pred-4 and possibly Pred-2 may fit remote_cpu_queue; Pred-1, Pred-3, Pred-5 likely need GPU per [[feedback-gpu-first-for-depth-probes]] (≥5 seeds × ≥6 cells per sweep crosses the depth-probe threshold).

Per [[feedback-no-experiment-design-in-prompts]]: anchor names, exact sweep grids, queue choice, HF1/HF2/HF3 numerical bounds, ETA, and cap_map row IDs are all exp_dev's decision domain. This handoff specifies STRUCTURE only.

Per [[feedback-rehabilitation-after-rejection]] and [[feedback-rescue-sketch-first-sequencing]]: if Pred-1 fails HF2 (continuous scaling), the basin-discrete framing is dealt a major blow. Before closing, file 3-5 rescue sketches: (a) re-test with different cascade-content selection (uniform replay vs prioritized), (b) re-test on different benchmark (declarative vs procedural style), (c) re-test with explicit refractoriness from Pred-4 added, (d) check if biology's discreteness requires specific neuromodulator-style gating not present in current substrate.

---

## Out-of-scope (this handoff does NOT cover)

- REM/theta procedural-consolidation cascade — separate research drill if substrate adds procedural-style replay.
- Ultra-slow oscillation (~0.1 Hz) as a 4th cascade level — open question deferred to next biology drill.
- Mathematical model of WHY discrete cascades beat continuous — deferred theory drill.
- Cap_map row creation / decisions — strategy_scribe owns this if Pred-1 produces actionable results.

---
BULK-ARCHIVED 2026-06-01: pre-2026-05-25 backlog OR processed-but-not-archived; cap_map v311+ reflects evidence of acted-on work; per dashboard inbox-clearance Path A.
