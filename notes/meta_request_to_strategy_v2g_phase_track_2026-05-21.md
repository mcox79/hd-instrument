# META -> Strategy: V2.G multi-regime substrate track + triple-point characterization + capability-inventory phase-transformation reframe

**Sender**: META session (session 6)
**Recipient**: Strategy session (session 1)
**Date**: 2026-05-21 ~22:00 EDT (cycle 25 followup)
**User-directed**: Yes. User asked META cycle 25 about V2 substrates enabling holy-grail capabilities, phase-transformation applicability, and reversible-transformation possibilities; META cycle 26 surfaced triple-point hypothesis; user directed META: "file a request for what you've identified - triple point and v2.g as a track + framing the capability-test inventory through the phase-transformation lens."

## What this document is

A single integrated proposal containing three coordinated items:

1. **R-question Rxx (critical-point / triple-point characterization)** — cheap (1-cycle) empirical test of whether substrate is operating near a phase-diagram critical point. Determines architectural cost of V2.G.
2. **V2.G multi-regime substrate track** — new V2 candidate parallel to V2.D (Bet Y) and V2.B. Implements STACK = P.5 sleep/wake + P.2 metaplasticity + P.6 asymmetric β + active eviction. Per Research phase-transformations note (P=0.75 substrate-novel combination).
3. **Capability-test inventory reframe** — Bet S/T/U/V/W from META cycle 20 inventory reinterpreted as substrate operating-mode tests rather than separate mechanisms. Several capability tests collapse into "different configurations of the same substrate" if V2.G lands.

All three are mutually reinforcing. If item 1 confirms criticality, items 2 and 3 become substantially cheaper to execute. If item 1 disconfirms, item 2 still works but each STACK mode requires explicit engineering (per Research note's `P.5 + P.2 + eviction` decomposition).

---

## Item 1 -- R-question Rxx: Critical-point / triple-point characterization

### Substrate-level claim

The substrate may be empirically operating near a phase-diagram critical point or triple point in the (alpha, beta, n) phase space defined by Hopfield / spin-glass / modern-Hopfield frameworks. Direct experimental measurement of critical-point signatures would confirm or refute.

### Convergent empirical signals pointing at criticality

1. **Bet I (free probability) predicted sigma_c = exactly 16** via BBP threshold (Baik-Ben Arous-Peche). BBP IS a phase transition. Substrate operating at the BBP threshold means substrate is at the boundary between noise-dominated and signal-dominated regimes -- the literal definition of critical operation.

2. **alpha = 0.153, just above alpha_c = 0.138** (R29 ferromagnetism analysis). Substrate sits just inside the modern-Hopfield rescue regime, near the boundary with classical AGS spin-glass collapse.

3. **beta = 32 chosen empirically for Bet G calibration** corresponds exactly to where Bet I free-probability theory says BBP threshold lives. Two independent handles (empirical calibration + theoretical free-probability prediction) converging on the same value is consistent with critical-point operation.

4. **5-source RSB agreement** (R23 FRSB / R29 modern-Hopfield / R16 free probability / R18 RFOT / Bet E Parisi P(q)). Multiple phase-theoretic frameworks predicting the same regime is characteristic of *universality* -- the property that holds AT critical points.

5. **Bet B retention_A = 0.954 across three independent runs** (v7/v8/v9). Sharp attractor fixed points are critical-point signatures (universality forces independent runs to land at the same value).

6. **d=25 multi-hop cliff is the VSA-class info-theoretic bound** (Bet X cycle 64) -- same number arrived at via VSA noise math AND transformer CoT lower bounds (arXiv:2502.02393, arXiv:2505.23653). Universal scaling across different architectures is a critical-point signature.

### Honest probability estimates

- P(substrate is empirically near a triple point or critical point): **50-65%**
- P(the proposed measurement is informative either direction): **95%+**
- P(if confirmed, V2.G STACK requires significantly less engineering): **>80%**

### Proposed experiment

`wave14_critical_point_smoke_v1` -- 1 cycle Experiment Dev build + 1 cycle full run, ~1 GPU hour total.

**Three signatures to measure** (all on current substrate; no V2 required):

1. **Susceptibility chi(beta) sweep**: perturb cleanup temperature in a window around beta=32; measure output sensitivity (chi = d<output>/d<perturbation>). Critical-point signature: sharp peak at beta=32. Sub-critical signature: broad plateau.

2. **Event-statistics power spectrum**: log retrieval timings + outputs across N=10000 queries; FFT; look for 1/f^alpha scaling (self-organized criticality, Bak-Tang-Wiesenfeld 1987) vs exponential decay.

3. **Avalanche / error-cluster size distributions**: collect substrate's prediction errors and retrieval-collision events; histogram cluster sizes. Critical signature: power-law distribution. Sub-critical: exponential.

### Multi-probe success criteria

- 2 of 3 signatures show critical-point pattern -> substrate is empirically near criticality. Promote V2.G with reduced engineering estimate.
- 0 or 1 signature -> substrate is deep in one phase. V2.G STACK still viable but each mode requires explicit engineering per Research phase-transformations note.

### Materials analog (load-bearing per feedback_materials_science_probe)

Critical-point operation is the substrate equivalent of:
- Water at 0.01 C, 611 Pa (water/ice/vapor triple point) -- maximum sensitivity, all phases accessible
- Iron at Curie temperature -- ferromagnetic/paramagnetic transition with diverging susceptibility
- Spin glass at AT line -- replica-symmetric / replica-broken boundary
- Neuronal avalanches near criticality (Beggs-Plenz 2003 Science) -- biological brains operate near critical points

The hypothesis that substrate operates near criticality is the natural extension of the 5-source RSB identification; substrate's specific parameters (beta=32, alpha=0.153) align with the predicted critical-point location.

### Routing

- **Research**: lit-scan critical-point / SOC measurement literature; vet the 3 proposed signatures; specify measurement protocol. ~1 cycle.
- **Experiment Dev**: build `wave14_critical_point_smoke_v1` after Research delivers protocol. Cheap (1-cycle); no architectural change.
- **Strategy**: integrate result into cap_map; promote V2.G or downgrade depending on outcome.

---

## Item 2 -- V2.G multi-regime substrate track

### What V2.G is

A new V2 substrate track parallel to V2.D (Bet Y exponential-capacity dense AM) and V2.B (hybrid HRR+bipolar). Implements the Research phase-transformations STACK (top recommendation P=0.75 substrate-novel combination):

- **P.5 sleep/wake mode**: Fachechi 2019 dreaming-Hopfield unlearning (capacity climbs alpha_c -> ~1.0) + Tadros 2022 sleep-replay
- **P.2 metaplasticity / multi-timescale**: Benna-Fusi 2016 cascade variables (linear capacity in N vs sqrt(N) for binary)
- **P.6 asymmetric beta**: write-T != read-T (substrate-novel, no published precedent)
- **Active alpha-eviction**: load-modulated forgetting (couples to P.5)

### Why V2.G is distinct from V2.D and V2.B

| V2 candidate | What changes | Capability shape |
|---|---|---|
| V2.D (Bet Y) | Cleanup operator linear -> exponential | More capacity (5x), same capability class |
| V2.B (Bet X hybrid) | Add parallel HRR pool alongside BSC | Extends multi-hop past d=25 (target the VSA-class bound) |
| **V2.G (this)** | Per-query reversible mode switching with provenance | New capability class: multi-regime operation. LLMs structurally cannot do this. |

V2.D and V2.G are *complementary*: V2.D gives capacity; V2.G gives mode flexibility. Both can be co-developed.

### Substrate-level claim

A substrate with multiple operating regimes per-query selectable with full audit trail is a capability LLMs structurally do not have. Transformers have fixed weights at inference -- they cannot context-switch the *computation*, only the *attention pattern*. Substrate-with-modes would switch the underlying retrieval mechanism per query.

Concrete modes accessible via parameter knobs:
- **Cold retrieval mode** (high beta): sharp categorical recall; verification, exam-taking
- **Hot exploration mode** (low beta): smooth blended retrieval; ideation, novel combinations
- **Learning mode** (high plasticity, fast eta): rapid storage of new facts
- **Sleep / replay mode** (Fachechi dreaming + Tadros consolidation): offline restructuring
- **Forensics mode** (WHT decomposition): audit stored items
- **Multi-hypothesis mode** (multi-domain ferromagnetic analog): parallel basin access; this IS Bet T

Each mode reversibly accessible; same memory; different access regimes.

### Engineering cost estimate

- **Conditional on critical-point confirmed (Item 1 yields YES)**: 3-5 Experiment Dev cycles. Each mode is a parameter knob; substrate already at the critical point where modes are naturally accessible.
- **Conditional on critical-point NOT confirmed**: 5-10 cycles. Each mode requires explicit mechanism engineering (Fachechi dreaming-unlearning; Benna-Fusi cascade variables; asymmetric beta storage; eviction policy).

### Falsifiable predictions

If substrate IS near a critical point + V2.G built:
- Mode-switching latency under 100ms (parameter changes, not retraining)
- All current Bet primitives (A/B/C/G/I) work in each mode
- 5x capacity gain in V2.D mode preserved when V2.G is active
- Audit trace shows mode + parameters for each operation

If 0 of 4 predictions hold across 3 seeds at full scale, V2.G is closed as substrate-arch-incompatible. Otherwise integrate per partial-pass framing.

### Materials analog

A spin glass operating near a triple point IS a multi-regime substrate. Phase boundaries are reversibly crossable via small parameter changes. The substrate's 5-source RSB identification already places it in the materials class where this is natural.

---

## Item 3 -- Capability-test inventory phase-transformation reframe

### What this is

Reinterpretation of the META cycle 20 capability-test inventory (Bet S/T/U/V/W from candidates A/B/C/D/E) as different operating modes of the same substrate, rather than separate mechanism tests.

### Mapping

| META capability candidate | Existing Bet | Phase-transformation reframe |
|---|---|---|
| A Pattern completion | Bet S | Recall mode at recall-criticality (binding inversion exploitation; tunable beta) |
| B Hypothesis tracking with provenance | Bet T | Multi-domain mode (ferromagnetic-multi-domain analog per R29); parallel basin access |
| C Working memory with capacity / decay | Bet U | "Awake / learning" mode (high plasticity, sharp retrieval, bounded buffer) |
| D Self-reflective memory | Bet V | "Sleep / replay" mode storing prediction+outcome triples |
| E Counterfactual reasoning | Bet W | Conditional binding swap mode (what-if mode) |
| F Skill composition | Bet X (in flight) | Bound-sequence-as-callable; cross-mode if substrate supports |

### Strategic consequence if V2.G works

Capability tests S/T/U/V/W collapse from "five separate mechanism experiments" into "different parameter configurations of the same substrate." Each becomes a benchmark in a specific V2.G mode rather than a separate architecture.

Concretely: Bet T (hypothesis tracking) becomes "measure multi-basin retrieval in V2.G multi-domain mode" -- no new mechanism needed, just a benchmark task in the appropriate mode.

### Strategic consequence if V2.G does NOT work

Each capability test (S/T/U/V/W) remains a separate experiment per the original META cycle 20 inventory. No regression; the reframe is additive only.

### Reframed sequencing recommendation

If user / Strategy accept the reframe contingent on Item 1 outcome:

**Critical-point YES path**:
1. Phase 1: build V2.G core (3-5 cycles)
2. Phase 2: run Bet S/T/U/V/W as V2.G mode benchmarks (each ~1 cycle)
3. Phase 3: Lane D product validation on multi-mode V2.G substrate

**Critical-point NO path**: revert to META cycle 20 inventory ordering (Bet S first, etc.) and Research phase-transformations note STACK engineering plan.

---

## How the three items connect

```
Item 1 (cheap test)
   |
   v
   YES near criticality  ->  Item 2 (V2.G) is cheap to build
                          ->  Item 3 (capability reframe) makes sense
                          ->  Lane D product story has natural substrate

   NO not near criticality -> Item 2 (V2.G) still possible but
                              engineering-heavy per Research P.5 + P.2
                              decomposition (5-10 cycles)
                           -> Item 3 reframe still partially useful
                              but each capability needs explicit
                              mechanism
                           -> Capability tests from cycle 20 inventory
                              remain the right path
```

Item 1 is the gating test. Cheap, informative either direction.

---

## Recommended experimental plan addition

### Phase 1 immediate (next 2-3 Experiment Dev cycles)

- **R-question Rxx (critical-point characterization)**: route to Research for protocol design (~1 cycle). Research vets the 3 signatures (susceptibility, power spectrum, avalanche statistics) against critical-phenomena literature.
- **Bet Z (critical-point smoke)**: once Research delivers protocol, Experiment Dev builds `wave14_critical_point_smoke_v1` (~1 cycle). Run on current substrate; no V2 needed.
- **Wait for result**: 2-3 cycles total. Determines whether V2.G is cheap or expensive.

### Phase 2 conditional (after Phase 1 result)

If Phase 1 confirms criticality:
- **V2.G core build** (3-5 cycles): exposed mode-switching knobs on current substrate; parameter-controlled cold/hot/learning/sleep/forensics modes.
- **Bet S/T/U/V/W as V2.G benchmarks** (each 1 cycle): capability tests reframed as mode benchmarks.

If Phase 1 disconfirms criticality:
- Revert to original Bet S/T/U/V/W ordering per cycle 20 inventory.
- STACK is still useful but each mode requires explicit engineering.

### Phase 3 long horizon (after V2.G validation if it lands)

- Lane D product integration on V2.G multi-mode substrate.
- Bet Y (V2.D) capacity work continues in parallel.
- V2.B (hybrid HRR+bipolar for multi-hop past d=25) is the remaining V2 candidate; pursue based on capability ROI vs V2.D + V2.G.

---

## Honest caveats per feedback_no_smoke

- **Critical-point hypothesis is consistent with empirical signals but NOT directly measured yet**. The 6 convergent indicators (BBP exact, alpha just above critical, beta=32 = BBP, 5-source RSB, Bet B sharp attractor, d=25 universal bound) are necessary but not sufficient signatures. Direct measurement is required.

- **50-65% probability is META's honest estimate**, not a published frequency. Underlying observations are real; the inference to "near a triple point" is interpretive.

- **Substrate is finite-N (N=4096)**, so true asymptotic criticality is technically impossible. "Near critical" in the finite-N sense means specific universality-class behavior, not infinite susceptibility.

- **V2.G is conditional on Item 1**. If criticality disconfirmed, V2.G is more expensive than V2.D and probably not the next priority.

- **Capability reframe is additive only**. Doesn't replace existing META cycle 20 inventory ordering; just provides an alternative interpretation if V2.G lands.

- **No new commitments to product timeline**. V2.G is exploratory; Phase 1 outcome determines whether it gets serious resources.

- **Critical-point operation has real risks**: catastrophic transitions, hysteresis, heavy-tailed event distributions. These need empirical characterization before substrate ships at critical-point operating point.

---

## Per feedback_value_creation_not_competition

This proposal is grounded in materials physics + statistical mechanics. The substrate-novel value claims are:

1. **Multi-regime substrate with audit trail** is structurally something LLMs cannot match -- fixed-architecture transformers cannot switch operating mode per query
2. **Critical-point operation** is a quantifiable capability with rigorous condensed-matter physics behind it (Bak-Tang-Wiesenfeld SOC, Beggs-Plenz neuronal avalanches, Hopfield critical-point retrieval)
3. **The substrate's empirical position** (alpha=0.153, beta=32, 5-source RSB) is consistent with critical-point operation; measurement is needed to confirm

Framing is capability + math, not market positioning.

---

## What Strategy should do with this document

1. **Read once**; integrate into active_priorities + cap_map's strategic-framing section. This document anchors the V2.G + criticality framework.

2. **File Research request**: route Rxx (critical-point characterization) to Research with the 3 proposed signatures. Research vets against literature.

3. **File Experiment Dev request**: once Research delivers protocol, route Bet Z `wave14_critical_point_smoke_v1` to Experiment Dev. Cheap 1-cycle smoke.

4. **Update cap_map**: add V2.G as new track (parallel to V2.D, V2.B); add Bet Z and Rxx as new entries.

5. **Update active_priorities**: V2.G goes in V2 candidate inventory. Capability-reframe note added to Bet S/T/U/V/W rows (so future readers know the conditional pivot).

6. **Wait for Phase 1 result**: don't over-commit V2.G resources until criticality is empirically confirmed.

7. **Per PROT-009**: this commit must be paired with a strategy_decisions entry explaining the integration.

---

## Approval / authorization

- User has directed META cycle 26 conversation toward this synthesis
- User explicit prompt: "file a request for what you've identified - triple point and v2.g as a track + framing the capability-test inventory through the phase-transformation lens"
- META retains authority on the framing; Strategy decides actual prioritization and resource allocation
- User retains final say on whether to pursue V2.G if Item 1 confirms

---

## Cross-references

- `notes/research_phase_transformations_2026-05-21.md` (3 parallel agents, 50+ papers, P.5+P.2+P.6+eviction STACK at P=0.75)
- `notes/research_V2_substrate_evaluation_2026-05-21.md` (6 V2 candidates evaluated; V2.D winner)
- `notes/meta_request_to_strategy_capability_test_inventory_2026-05-21.md` (6 META candidates; Bet S/T/U/V/W/X promoted)
- `notes/meta_request_to_strategy_strategic_plan_2026-05-21.md` (canonical lane analysis)
- META cycle 25/26 user conversation on triple-point and reversible-transformation substrate
- Existing Bets: Bet I (free probability sigma_c=16), Bet G (TEMPSCALE beta=32), Bet B (retention_A=0.954 sharp attractor), Bet E (Parisi RSB), R23/R29/R16/R18/R22 (substrate-physics framework)
- Materials-physics literature: Bak-Tang-Wiesenfeld 1987 SOC; Beggs-Plenz 2003 neuronal avalanches; Fachechi 2019 dreaming-Hopfield; Tadros 2022 sleep-replay; Benna-Fusi 2016 metaplasticity; BBP transition

-- META session
