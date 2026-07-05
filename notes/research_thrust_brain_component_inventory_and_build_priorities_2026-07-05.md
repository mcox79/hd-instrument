# Research thrust: brain-component inventory + build priorities

**Date:** 2026-07-05
**Type:** Strategic-thrust drill (USER-directed). Constructive build synthesis — brain-first, not vs-LLM.
**Scope:** Map substrate mechanisms <-> brain components with verified status/tier; test "brain mechanisms are load-bearing not decoration"; test "multiples/redundancy improve capability"; rank missing/weak components to build next.
**Discipline:** Lit-scan calibration penalty applied (P deflated 0.15-0.25; novel-synthesis P capped 0.50). Verified off-disk before propagating numbers (Fix #28) — one user-supplied figure could NOT be corroborated and is flagged, not silently accepted.
**Sub-agents:** 3 parallel Sonnet — (1) internal corpus scour for least-covered components, (2) external lit-scan on redundancy-generalizes-capability, (3) external lit-scan ranking 5 missing-component candidates.

---

## HEADLINE

**The substrate has 4 brain components working STRONGLY (hippocampal index-protection, CA3 regenerative cleanup, the content-only op-selection router, and the frame-slot language decoder) with genuine ablation-style evidence that each is load-bearing — function collapses toward zero without the specific mechanism and recovers substantially with it. "Multiples improve capability" is real but NOT a free lever: our own data (R banks of N == 1 bank of R*N, delta<0.004) already discovered the textbook caveat external lit confirms — redundancy only pays when it adds independent capacity, not when it re-partitions a fixed budget. The single highest-leverage next build is NOT a new component from scratch: it's training the two already-tested-but-weak basal-ganglia-flavored gates (PFC-BG goal-gate +0.05-0.06 lift, BG-analog conflict-operator +0.04 lift) with a reward-prediction-error signal the substrate already has (cfrpe) — composing two existing primitives, not inventing one.**

Plain-English: we're not missing brain parts wholesale — we're missing the TRAINING SIGNAL that makes the gating parts we already built actually work well. The brain's basal ganglia gate isn't a static rule; it's a rule trained by dopamine. Ours is still the static rule. Cerebellum and thalamic dynamic routing are genuinely absent, but there's nothing yet in the substrate for them to act on (no motor/sequential-action loop, no dynamic multi-subsystem traffic) — building those now would be building infrastructure with no load, so they're staged, not top-ranked.

---

## 1. INVENTORY (mechanism <-> brain component <-> verified status/tier)

| Brain component | Substrate mechanism | Status | Verified tier / metric | Source |
|---|---|---|---|---|
| Hippocampal index/DG-CA3 protection | Permutation/index-protected binding | **HAVE — strong** | MM_STANDARD: hub deg5+ recall **0.261→0.727** (+0.466), matches Clarkson-Ubaru-Yang O(K²) hub-punishment theory independently | `exp_deep_reasoning_hub_robustness_v1`; `research_5x_drill_memory_spec_and_brain_mechanism_2026-07-05.md` |
| CA3 attractor / regenerative cleanup | Digital-repeater cleanup vs analog-accumulate | **HAVE — strong** | MEASURED_MECHANISM: regen_d5 **~0.70 vs analog ~0.10** (collision-corrected), gap WIDENS with load, faith=1.0 | `research_5x_drill_reasoning_spec_and_brain_mechanism_2026-07-05.md` |
| Op-selection / content router | Nearest-class-HV router (4-class) | **HAVE — strong** | HARD_PASS cross-seed 3/3, confusion-matrix **1.000**, lift +0.75 vs no-router | `cortex_attention_binding_router_v2` (M1.6) |
| Language production (Levelt frame-slot) | Block-local resonator decoder | **HAVE — strong** | MM_STANDARD/CHAIN_GRADE: exact-ordered **1.000** on native GSBC fillers to D=26/V<=1024 | `exp_generation_decoder_gsbc_native_blocklocal_v1` |
| Entorhinal grid / modular code | CRT block-local modular composition | **HAVE — partial, unverified at scale** | HP-**SMOKE only**, n=1 seed (LVH #237); algebraically exact but PROT-021 multi-seed not met | `crt_multi_scale_grid_cell_composition_v1` |
| TEM (structural x content) | Content-conditioned relation transform | **HAVE — partial, frontier** | MIDDLE_BAND: genuine nonzero real-minus-shuf **0.05–0.13**, under-parameterized not walled | `exp_schema_relation_TEM_structural_content_binding_v1` |
| PFC-BG gating (PBWM) | Goal-conditioned additive-bias gate | **HAVE — weak** | MIDDLE_BAND: **+0.05–0.06** lift vs 66-point ORACLE headroom unclosed | `exp_pfc_goal_conditioned_gate_v1-v3` |
| BG-analog conflict resolution (non-PBWM) | Multiplicative/BG-analog integration op | **HAVE — weak** | MIDDLE_BAND: BG-analog=**0.040** best-of-3, 96% "irreducible" frustration; diagnostic COMPLETE | `frustration_bg_analog_cpu_v1`, `integ_softmax_t1_cpu_v1` |
| Population coding / redundancy | Erasure coding + multi-hub redundancy | **HAVE — real, standard law** | HARD_PASS erasure-coding recall=**1.000** (PP-354); multi-hub coverage 0.41→0.62 MIDDLE_BAND; but VET: equal-memory R-banks==1-bank, delta<0.004 (standard linear crosstalk, not a free multiplier) | PP-354; mycorrhizal multi-hub; memory VET 2026-07-05 |
| CLS (hippocampus-fast/cortex-slow) | Dual-W fast/slow store | **HAVE — weak/mixed** | 2x MIDDLE_BAND (+2–4pp lift, slow dominates) + 1x HARD_FAIL (`two_substrate_fastslow_cls`, recall 0.689/0.378 both below gate, seed-robust) | d2_1_dual_cls, cls1_dual_substrate_1k, two_substrate_fastslow_cls |
| Schema-formation / structural generalization | Subject-conditional relational mapping | **MISSING / open frontier** | SCOPED HARD_FAIL under 2 encodings, but comparison-axis control was VACUOUS (untested, not refuted) | `schema_ablation` FULL 12-arm, VET a0f6dae |
| Neuromodulation — dopamine RPE | cfrpe (counterfactual rank-1) | **HAVE — partial, mixed** | Large family: HARD_PASS in arch-ablation (+0.683 nats) / HARD_FAIL in weighted-replay — context-dependent | multiple cells across cycles |
| Neuromodulation — serotonin | Discrete bank-switch | **TRIED — wrong mechanism mapping** | HARD_FAIL, lift=-0.0022; brain lit says serotonin = diffuse multiplicative gain, cell tested discrete switching instead | `substrate_serotonin_mode_switch_bank_select_LM_v1` |
| Neuromodulation — acetylcholine | — | **MISSING** | zero hits | — |
| Basal ganglia proper (trained Go/NoGo + RPE) | — | **MISSING** | backlog placeholder only (BR9), never shipped as its own cell | `experiments_backlog.md` |
| Cortical microcircuit / predictive coding | Friston-FEP-inspired architecture | **TRIED — narrow HARD_FAIL x2** | HARD_FAIL bigram N=512 (-0.789 nats) and trigram N=4096 (-1.019 nats, 3/3 seeds); narrow task only | `substrate_arch_ablation_matrix_bigram_v1`, `substrate_friston_fep_trigram_cell_v1_n4096` |
| Thalamic dynamic routing hub | — | **MISSING** | backlog placeholder only (BR10); current inter-module "bridge" is static plumbing, not a brain-grounded dynamic gate | `experiments_backlog.md` |
| Cerebellar forward model | — | **MISSING** | backlog placeholders only (BR3, BR12), never shipped | `experiments_backlog.md` |

**Count:** 4 strong / 7 partial-weak-mixed / 2 tried-and-narrowly-failed / 4 genuinely missing, across 17 named components/sub-mechanisms.

**Flagged discrepancy (verify-off-disk):** the input framing's "deg8+ 0.40→0.99 via redundancy" could not be corroborated after a real search. The verified figure is the OPPOSITE direction of resolved: deg8+ still carries a **0.42–0.47 residual gap** ("inside headroom," i.e. buyable, not yet bought) per today's memory synthesis. The hub-rescue headline number (0.26→0.73) IS verified almost exactly (0.261→0.727). Do not propagate the 0.40→0.99 figure until a specific cell citing it is located.

---

## 2. REQUIRED FOR HIGHER FUNCTION — defensible, with real ablation-style evidence

Yes, this is defensible off our own data — four independent clean ablations, each showing **collapse without the mechanism, recovery with it**:

1. **Hippocampal index protection**: hub recall 0.21–0.261 (unprotected) → 0.727 (protected). Removing the index-protection is not a minor degradation, it's a structural failure mode (collision_frac 0.85 unprotected).
2. **CA3 regenerative cleanup**: analog-accumulate reasoning depth-5 ≈0.10 vs digital-repeater cleanup ≈0.70, and the gap **widens with load** — cleanup isn't a nice-to-have, it's what prevents noise compounding past the crosstalk threshold.
3. **Grid-modular/block-local structure**: dense bipolar-BSC generation on GSBC fillers = **0.000** (representation-mismatch); block-local/modular structure (entorhinal-grid-style) on the SAME task = exact-ordered **1.000**. Wrong structural class = total failure, not degradation.
4. **Language frame-slot decoding**: "blind factorization" reads as 0.000 without a known frame; frame-known decoding = 1.000. This reframed what looked like a generation wall as a comprehension problem — the frame-slot mechanism itself is necessary and load-bearing for the generation side.

Weaker/partial evidence in the same direction: TEM content-conditioning moves structural transfer from a flat 0.000 to a genuine but small 0.05-0.13 — necessary-looking but clearly not yet sufficient (frontier, not closed).

**P_deflated(claim: "brain's specific mechanisms are load-bearing, not decoration") = 0.65** (raw ~0.85 given four independent clean ablations; -0.20 lit-scan calibration for generalizing beyond these four specific cases).

---

## 3. MULTIPLES/REDUNDANCY IMPROVE CAPABILITY — real but conditional, not free

**Internal evidence:** erasure-coding redundancy is a genuine HARD_PASS (recall=1.000 recovering lost shards); multi-hub redundancy gives a real but partial MIDDLE_BAND win (coverage 0.41→0.62). But the decisive internal finding this session is a **caveat, not a confirmation**: equal-total-memory R redundant banks of size N perform IDENTICALLY to 1 bank of size R·N (delta<0.004) — this is the standard linear-crosstalk law, not a novel "redundancy lever." Multiples only help when they add **net new, independent** capacity — not when they re-partition a fixed budget.

**External lit-scan corroborates precisely this caveat** (independently, via generic-term search, no substrate specifics leaked): the ensemble/population-coding/N-version-programming/wisdom-of-crowds literature converges on **decorrelation among the redundant units being the necessary condition** — correlated failure / shared bottleneck is the dominant failure mode that voids the benefit (Krogh-Vedelsby ambiguity decomposition; Knight-Leveson correlated multi-version software failures; JMLR 2023 diversity theory). Our own R-banks-of-N finding IS this caveat, independently rediscovered.

**P_deflated(claim: "multiples/redundancy generically improve capability, with diminishing but positive returns, CONDITIONAL on decorrelation") = 0.45** (external raw 0.55, further -0.10 for compounding two independent calibration layers per contract discipline).

**Where else multiples would plausibly help (generalizing, ranked by how directly it fixes an already-measured weak point):**
1. Neuromodulation ensemble — cfrpe's context-dependent mixed results (HARD_PASS in some contexts, HARD_FAIL in others) may reflect a single noisy RPE estimator; an ensemble/averaged RPE signal is a natural next probe before concluding cfrpe is context-fragile.
2. BG-analog conflict resolution — currently ONE scalar operator (0.04 lift); the brain's striatal signal is population-coded, not scalar. A population-coded (not single-operator) BG-analog conflict signal is untested.
3. CLS timescales — currently exactly 2 tiers (fast/slow); the brain has more than 2 consolidation timescales. A 3-tier CLS has not been tried.

---

## 4. RANKED MISSING/WEAK COMPONENTS — build priority

Ranking = capability-gain × feasibility × brain-groundedness, combining internal evidence + external lit-scan (Agent C, 5 candidates independently ranked):

| Rank | Component | Capability gain | Feasibility | Evidence strength | Verdict |
|---|---|---|---|---|---|
| **1** | **Neuromodulation — trained dopamine-RPE signal + ACh-style uncertainty-gated learning rate** | HIGH | EASY (TD-error is a drop-in scalar; substrate already has cfrpe as a partial RPE-analog) | HIGH (Schultz 1997, decades-replicated) | **BUILD NEXT** |
| **2** | **Basal ganglia proper — TRAIN the existing weak gates with #1's signal** (replace static additive-bias / static BG-analog operator with RPE-trained Go/NoGo competition) | HIGH | MEDIUM (full published architecture exists — PBWM/Frank 2004/2006 — integration work, not new theory) | HIGH | **BUILD NEXT (paired with #1)** |
| 3 | Cerebellar forward model | MEDIUM | EASY-MEDIUM (supervised delta-rule is clean) | HIGH (Marr-Albus-Ito, 50+ yrs) | DEFER — no motor/sequential-action loop yet for it to act on; building it now is unloaded infrastructure |
| 4 | Thalamic dynamic routing hub | MEDIUM-HIGH | MEDIUM-HARD (no single canonical algorithm; usually soft-attention-as-gating) | MEDIUM (anatomy solid, computational routing role newer/contested) | DEFER — real gap (static bridge, not dynamic gate) but not yet load-bearing until a real multi-subsystem traffic problem exists |
| 5 | Cortical microcircuit / predictive coding | MEDIUM (uncertain) | MEDIUM (Rao-Ballard/Bastos formalism is clean, hierarchy hyperparameters are finicky) | MEDIUM | DEPRIORITIZE — already has 2 narrow in-house HARD_FAILs (bigram/trigram); not refuted broadly, but not the frontier priority now |

**Why #1+#2 jointly outrank everything else:** they are not new components, they are the missing HALF of two components we already built and already measured as weak. PBWM's own literature (Frank/O'Reilly) says Go/NoGo competition IS trained by dopaminergic reward-prediction-error — our PFC-BG gate and BG-analog operator have only ever been tested as STATIC rules (additive bias / fixed multiplicative operator). This is the cheapest possible high-leverage move: compose two already-working substrate-native primitives (cfrpe + the existing goal-gate harness with its measured 66-point oracle headroom) rather than build anything from scratch.

### Top pick's decisive first cell

**`exp_pfc_gate_cfrpe_trained_v1`** — reuse the existing `exp_pfc_goal_conditioned_gate` harness (already coded; ORACLE=1.000 ceiling and 66-point headroom already measured) and the existing `cfrpe` RPE-analog signal (already substrate-native, HARD_PASS in some contexts). Replace the additive-bias gate with a Go/NoGo competitive gate TRAINED by the cfrpe signal.

**Arms:** (1) `ADDITIVE_BASELINE` — reproduce existing mechanism, sanity rail ~+0.05-0.06 lift. (2) `CFRPE_TRAINED_GONOGO` — Go/NoGo competition trained on cfrpe reward-prediction-error. (3) `ORACLE` upper bound (=1.000, already measured).

**Capability this targets:** the two already-measured weak points at once — (a) goal-conditioned control / instruction-following (same content, different goal → different handling; 66-point oracle gap currently unclosed) and (b) conflict-resolution integration (currently only 4% operator-fixable).

**HARD-PASS:** `CFRPE_TRAINED_GONOGO` lift over `ADDITIVE_BASELINE` **>= 0.15** (closes >=25% of the 66-point oracle headroom), cross-seed cv<0.10.
**HARD-FAIL:** `CFRPE_TRAINED_GONOGO` <= `ADDITIVE_BASELINE` + 0.05 (RPE-training doesn't help; static additive bias was already near this architecture's ceiling).
**MIDDLE-BAND:** lift in 0.05-0.15 (real but incomplete, more headroom to close).

**Compute:** CPU, ~2-3 hr (reuses 2 existing harnesses; the "new" work is a training loop, not new representational machinery).

**P_deflated = 0.40** (raw ~0.60: reuses 2 proven substrate-native primitives, PBWM/Frank is decades-replicated; -0.20 novel-synthesis calibration for the specific composition never having been tried; capped consistent with novel-synthesis P<=0.50).

---

## Cheap decisive test (see Section 4 top-pick cell — this IS the cheap decisive test for the thrust)

Already spec'd above: `exp_pfc_gate_cfrpe_trained_v1`, 3 arms, CPU, ~2-3 hr, reuses 2 existing coded primitives (no new representational machinery, only a training loop composing them).

## Falsifiable predictions

**HARD-PASS** (thrust confirmed — the missing half of the gate really was the training signal): `CFRPE_TRAINED_GONOGO` lift over baseline >=0.15 cross-seed.
**HARD-FAIL** (thrust wrong — the gate's weakness is architectural, not a missing training signal): lift <=0.05.
**MIDDLE-BAND** (real but incomplete): lift 0.05-0.15.

## Cross-thread synthesis

Builds directly on today's `research_frontier_drill_control_instruction_following_pbwm_2026-07-05.md` (same PFC-BG gate family, same 66-point headroom, same PBWM/Miller-Cohen grounding) and `integrated_short_term_spec_sheet_5x_drills...2026-07-05.md` (hippocampal-index-as-master-key finding, memory VET's linear-crosstalk-law caveat on redundancy). Extends the neuromodulation thread (cfrpe family) by proposing to USE it as a training signal for control, not just as an architecture ingredient. Does not re-open cortical-predictive-coding (2x narrow HARD_FAIL already banked) or re-litigate CLS-dual-store (weak/mixed, 3 cells already run) without new leverage.

## Substrate-product implications

A trained (not static) basal-ganglia-style gate is the credibility-bearing feature for any "goal/instruction-conditioned control" product claim — right now that claim rests on a +0.05-0.06 lift, which is a weak substrate-product story. Closing even half the 66-point oracle gap materially strengthens the glass-box control narrative (inspectable Go/NoGo competition, not an opaque gating network) versus LLM agentic routing, which per prior lit-scan is usually unlogged/opaque.

## Citations (verified: 15, cross-checked by 2 independent Sonnet lit-scan sub-agents)

1. McClelland JL, McNaughton BL, O'Reilly RC (1995) Why there are complementary learning systems in the hippocampus and neocortex. *Psychol Rev* 102(3).
2. Clarkson E, Ubaru S, Yang J (2023) arXiv:2301.10352 — dimension-vs-hub-degree O(K²) scaling for VSA superposition.
3. Krogh A, Vedelsby J (1995) Neural network ensembles, cross validation, and active learning. NeurIPS.
4. Wood D et al (2023) A unified theory of diversity in ensemble learning. *JMLR* 24.
5. Knight JC, Leveson NG (1986) An experimental evaluation of the assumption of independence in multiversion programming. *IEEE Trans Softw Eng*.
6. Page SE — Diversity Prediction Theorem (*The Difference*, ~2007).
7. Schultz W, Dayan P, Montague PR (1997) A neural substrate of prediction and reward. *Science* 275.
8. Yu AJ, Dayan P (2005) Uncertainty, neuromodulation, and attention. *Neuron* 46.
9. O'Reilly RC, Frank MJ (2006) Making working memory work: a computational model of learning in the PFC and BG. *Neural Computation* 18(2).
10. Frank MJ, Seeberger LC, O'Reilly RC (2004) By carrot or by stick: cognitive reinforcement learning in Parkinsonism. *Science* 306.
11. Ito M / Marr D / Albus J — cerebellar learning theory synthesis, "50 Years Since the Marr, Ito, and Albus Models" (2020, *Neuroscience*).
12. Sherman SM, Guillery RW (2017) Functioning of circuits connecting thalamus and cortex. *Compr Physiol*.
13. Bastos AM et al (2012) Canonical microcircuits for predictive coding. *Neuron* 76.
14. Rao RP, Ballard DH (1999) Predictive coding in the visual cortex. *Nat Neurosci* 2.
15. Miller EK, Cohen JD (2001) An integrative theory of prefrontal cortex function. *Annu Rev Neurosci* 24.

Verified count: 15 (external citations cross-checked by 2 independent lit-scan sub-agents; internal figures verified via direct Grep/Read against `substrate_capability_map.md` and today's 5x-drill notes, not asserted from memory).
