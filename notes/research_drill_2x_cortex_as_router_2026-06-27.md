# RESEARCH (Director): 2x DRILL — cortex-as-router (operators LIVE in cortex schemas)

**Date:** 2026-06-27
**Filed-by:** research (Opus 4.7 1M)
**Trigger:** USER deep drill. Cortex-closure agent authoring `cortex_as_router_v1`. My job: pressure-test design + propose alternatives + lock fairness discipline.
**Calibration:** lit-scan deflation -0.15 to -0.25; novel-synthesis cap 0.50; brain-existence-proof bump +0.10 where earned.
**Builds-on:** `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` (separate-pathway depth drill, prior); `notes/research_drill_brain_multihop_M1_schema_chunking_cortex_3x_2026-06-27.md` (schema-chunking, complementary).

---

## HEADLINE

When PFC routes operators, the brain does NOT pick from a separate operator bank — it picks from the SAME cortex schemas that store content. Mathematically this is **mixture-of-experts with shared representation space** (Switch Transformer / GShard) or a **DNC-style read/write head over shared memory** (Graves 2016). Biologically this is the **Miller-Cohen 2001 PFC theory** (PFC encodes task-rules-as-context that BIAS cortex via biased competition) combined with **Mante-Sussillo 2013 PFC-driven contextual gating** (same cortex neurons compute different functions depending on PFC context vector — landmark empirical evidence). Two concrete substrate architectures emerge: TOP-1 **PFC-context-vector multiplicative gating of cortex (Mante-2013 substrate analog)** — `c_h` element-wise modulates cortex bank; cleanup proceeds on modulated bank; continuous, no hard argmax. TOP-2 **biased-competition argmax (Miller-Cohen substrate analog)** — `sim_i = (state · cortex_i) · sigmoid(c_h · cortex_i)`; hard argmax over TOP-K=4 cortex schemas matched to baseline operator count. Both arms must beat separate-operator-bank baseline by ≥ 0.10 at EQUAL operator-count to be chain-grade-eligible. **P_deflated TOP-1 = 0.45; TOP-2 = 0.35.** TOP-1 ranks higher because both angles independently nominate Mante-2013 (math + brain convergence) and Mante-2013 is direct empirical evidence (not just theory).

---

## ANGLE A — PURE MATH + COMPUTATION

**3 mechanism proposals:**

| # | Mechanism | One-line |
|---|---|---|
| A-Prop-1 | PFC context-key cosine-argmax over cortex | At hop h, PFC emits `c_h`; pick `s* = argmax_i(c_h · cortex_keys_i)` from TOP-K; apply `state_h+1 = bind(state_h, s*)` |
| A-Prop-2 | **PFC context-vector multiplicative modulation** | `cortex_active = cortex_bank ⊙ c_h`; cleanup picks among modulated schemas — soft, continuous, no argmax (MoE-shared-expert / Mante-2013 brain analog) |
| A-Prop-3 | CPS tag-projection within bundled state | `state_h = data_h + tag_h`; unbind tag, project onto cortex-bank to pick operator |

**Mathematical difference vs "operators in separate bank":** (a) CAPACITY — substrate cortex bank has 5-200x more atoms than a 4-operator bank; (b) COGNITIVE LOAD — no separate parameter set to maintain; (c) COMPOSITIONALITY — operators can be combined via bundling cortex schemas (`op_combined = schema_A + schema_B` — impossible with discrete bank); (d) COMPUTATIONAL CLASS — moves from "4-state finite automaton" to "vector-addressed Turing-like machine" with capacity bounded by cortex-bank size. The lit anchors: Switch Transformer (Fedus 2021), GShard shared-routing (Lepikhin 2020), DNC (Graves 2016), Penrose tensor networks / MERA shared-tensor.

**A-angle fairness considerations per proposal:** (1) shared-W constraint (cortex bank N-dim = operator bank N-dim, complex64 dtype); (2) equal operator count K=4 baseline-matched; (3) `c_h` parameter budget matched via low-rank projection.

**A-angle P_deflated = 0.40** (raw 0.55 − lit-scan-deflation 0.20 + novel-synthesis-cap binds at 0.50; further deflated for substrate-FHRR composition novelty).

---

## ANGLE B — BIOLOGY + BRAIN

**3 mechanism proposals:**

| # | Mechanism | Brain lit anchor |
|---|---|---|
| B-Prop-1 | **PFC-context multiplicative gating of cortex** | Mante-Sussillo 2013 Nature — landmark empirical demo: PFC context vector multiplicatively modulates SHARED sensory cortex; same units, different context → different computation. RNN modeling reproduces data. ~2000 citations; foundational empirical result. |
| B-Prop-2 | Biased-competition argmax over cortex | Miller-Cohen 2001 Annu Rev Neurosci (~24k citations) PFC theory: PFC neurons encode TASK RULES; output context biases posterior cortex via biased-competition (Desimone-Duncan 1995). Whichever cortex schema wins biased competition IS the operator. |
| B-Prop-3 | Two-stage WM-prime + attention-select | Working memory (Miller 1956 / Cowan 2010 ~4 items) PRIMES small candidate subset; attention picks within; brain doesn't search millions of schemas per step. Hierarchical efficiency. |

**Additional brain anchors load-bearing:** Wallis-Anderson-Miller 2001 (Nature) PFC neurons encode task-rule-dependent CATEGORY BOUNDARIES — same neuron, different rule → different category. Tonegawa engrams 2014-2020 — cortex schemas = engram-like sparse population codes; engrams are BOTH content (sensory features) AND function (connectivity profile determines what activates next) — this dual role IS the load-bearing insight: operators ARE engrams; engrams ARE both data and function-pointer. Glascher 2010 PFC vs basal ganglia — model-based PFC computation uses cortex-schemas as world-model elements.

**Key insight for substrate:** the brain's "operators" are NOT separate from cortex schemas. PFC emits CONTEXT; context biases cortex (via multiplication per Mante-2013 OR biased-competition per Miller-Cohen); whichever cortex schema fires under that bias IS the operator at this moment. Same cortex tissue implements different operators under different PFC contexts.

**B-angle fairness considerations per proposal:** (1) parameter budget matched via low-rank `c_h = U @ rank_k_proj` with k=4; (2) verify gating actually varies per hop (silent gating ≡ no operator selection); (3) two-stage version requires SEPARATE projections at each stage (not one projection split — that's not two-stage).

**B-angle P_deflated = 0.50** (raw 0.65 − lit-deflation 0.15 + brain-bump 0.10 earned; novel-synthesis cap doesn't bind since Mante-2013 IS the mechanism, only substrate-port is novel).

---

## TOP-2 PICKS (P-ranked)

### TOP-1: PFC-context multiplicative gating (Mante-2013 substrate analog) — P_deflated = 0.45

Both angles independently nominate this. A-angle = MoE shared-expert via multiplicative gating (mathematically clean). B-angle = Mante-2013 direct empirical evidence.

**Falsifiable discriminator (pre-registered concrete numbers):**
- Baseline: `pfc_controller_per_step_operator_select_v1` separate-operator-bank arm at compositional-reasoning accuracy `acc_sep_bank` (Wave 1 measured; if not yet landed, use Wave 1 smoke estimate).
- Test arm: cortex-as-operator with multiplicative gating; PFC emits `c_h ∈ R^N`; cortex modulated = `cortex_bank ⊙ c_h`; cleanup within modulated bank; **operator count K=4 cortex schemas (closest to `c_h`)** to match baseline operator count.
- **HARD_PASS:** `acc_cortex_as_op` ≥ `acc_sep_bank` + 0.10 across 5 seeds (cv ≤ 0.08); AND per-hop gating-pattern entropy ≥ 1.5 bits (gating varies); AND cone-cosine of modulated to original cortex ≤ 0.95 (modulation non-trivial).
- **HARD_FAIL:** `acc_cortex_as_op` ≤ `acc_sep_bank` + 0.02 (no meaningful lift).
- **By-construction-saturation guard:** if `acc_cortex_as_op` ≥ 0.95 absolute, trigger Q-discipline — verify discriminator fired (per-hop operator choices DIFFER across hops); if single-operator-always, mechanism is by-construction.
- **Operator-count fairness sweep:** also K=4,8,16; chain-grade claim ONLY at K=4 (equal count) — isolates "operators-in-cortex" from "more operators help."

### TOP-2: Biased-competition argmax (Miller-Cohen substrate analog) — P_deflated = 0.35

Hard-argmax variant; testably distinct from TOP-1 (soft); foundational Miller-Cohen 2001 theory; substrate-feasible with existing primitives.

**Falsifiable discriminator (pre-registered concrete numbers):**
- Baseline: same `acc_sep_bank`.
- Test arm: per-hop `sim_i = (state_h · cortex_keys_i) · sigmoid(c_h · cortex_keys_i)`; `s* = argmax_i sim_i` from TOP-K=4 cortex schemas.
- **HARD_PASS:** `acc_cortex_argmax` ≥ `acc_sep_bank` + 0.10 across 5 seeds (cv ≤ 0.08); AND per-hop argmax covers ≥ 3 distinct schemas.
- **HARD_FAIL:** `acc_cortex_argmax` ≤ `acc_sep_bank` + 0.02; OR argmax collapses to 1 schema always.
- **Discrimination from TOP-1:** if both PASS and TOP-1 lift exceeds TOP-2 by ≥ 0.05, soft-gating wins (Mante-2013); if within 0.02, equivalent — pick by simplicity (TOP-2 has fewer continuous params).

---

## CRITICAL FAIRNESS DISCIPLINE (10-point — USER directive "very careful")

ALL must be in `cortex_as_router_v1` pre-reg. Each catches a specific by-construction-saturation I've personally violated:

1. **Renamed-atoms risk:** verify cortex schemas trace to CONTENT extraction in schema-integration's metrics (not seeded from operator templates). Provenance check pre-tier.
2. **Operator-count inflation:** chain-grade claim ONLY at K=4 (matched to baseline); sweep K=4,8,16 as separate arm to isolate "operators-in-cortex" from "more operators help."
3. **PFC parameter inflation:** match parameter count via low-rank `c_h = U @ z_h` with rank-k chosen so `params(c_h) ≈ params(baseline PFC controller)`.
4. **Shared-W:** cortex bank and operator bank MUST be same RANK, same DTYPE (complex64), same N_DIM. Only difference: shared vs separate.
5. **Verify-the-referent ROUTING (not STORAGE):** discriminator tests operators SELECTED PER HOP based on state. If per-hop selection is always same schema, test only measured storage. Pre-reg: per-hop operator-selection entropy ≥ 1.5 bits across test set.
6. **META_RULE_K (smoke FIRES discriminator):** smoke must show DIFFERENT schemas picked at different hops based on different states. If smoke shows always-same-schema, reject full dispatch.
7. **Discriminator-survives-scale:** smoke at N=1024 includes full-N=8192 preview arm showing baseline ≤ 0.50 of mechanism at full-N preview.
8. **Q-discipline (suspect 1.000):** any arm ≥ 0.95 absolute triggers by-construction investigation before HARD_PASS classification.
9. **CARDINALITY_OK:** pre-reg EXPECTED_N_UNITS = N_test_chains × N_hops; HARD_FAIL_CARDINALITY_BREACH if observed < 0.9× expected.
10. **BIAS-7 contamination:** test chains MUST NOT be the same chains used to extract cortex schemas — otherwise it's memorization, not compositional-reasoning. Pre-reg held-out set.

---

## RELATION TO CORTEX-CLOSURE AGENT'S IN-FLIGHT CELL

(a) **Independent verification:** both angles independently nominate Mante-2013 multiplicative gating; if their cell uses this, P_deflated = 0.45 is calibrated prior.
(b) **Alternative:** if their design is argmax-only, my TOP-2 (biased-competition with sigmoid bias) is the brain-aligned hard-argmax variant; queue as Wave 2 follow-up.
(c) **Fairness pressure-test:** 10 disciplines above are MUST-INCLUDE. Skunkworks should vet against these pre-tier. Missing any = by-construction-saturation risk per [[feedback-fix28-recurring]].
(d) **Upstream dependency:** Wave 1 PFC-controller must PASS for cortex-as-router to be meaningful. If Wave 1 MIDDLE_BAND or HARD_FAIL, defer this cell — don't dispatch into broken stack.

---

## RISKS + KILL-SWITCH

- **R1 mechanism degenerate:** `c_h` collapses to constant across hops → no compositional power. Falsifier: per-hop entropy of `c_h` ≥ 2.0 bits in smoke.
- **R2 cortex too narrow:** if schema-integration extracted ~3 schemas only, cortex bank too small to be meaningful operator vocabulary. Falsifier: cortex bank ≥ 20 schemas before shipping.
- **R3 noise floor:** at N=8192, modulating cortex by `c_h` might push schemas below cleanup floor. Falsifier: smoke clean-cortex top-1 ≥ 0.70; if not, raise to N=16384.
- **R4 upstream broken:** Wave 1 HARD_FAIL → this cell meaningless. Pre-condition: Wave 1 PASS.

**Kill-switch:** Wave 1 in MIDDLE_BAND/HARD_FAIL → defer.

---

## SOURCES

Sources:
- [An Integrative Theory of Prefrontal Cortex Function (Miller & Cohen 2001)](https://www.annualreviews.org/doi/10.1146/annurev.neuro.24.1.167)
- [Context-dependent computation by recurrent dynamics in PFC (Mante, Sussillo, Shenoy, Newsome 2013)](https://www.nature.com/articles/nature12742)
- [Single neurons in PFC encode abstract rules (Wallis, Anderson, Miller 2001)](https://www.nature.com/articles/35082081)
- [States vs Rewards dissociable neural prediction error signals (Glascher, Daw, Dayan, O'Doherty 2010)](https://www.cell.com/neuron/fulltext/S0896-6273(10)00287-1)
- [Optogenetic stimulation of hippocampal engram (Liu, Ramirez, Tonegawa 2012)](https://www.nature.com/articles/nature11028)
- [Memory engram cells have come of age (Tonegawa et al. 2015)](https://www.cell.com/neuron/fulltext/S0896-6273(15)00640-5)
- [Switch Transformers (Fedus, Zoph, Shazeer 2021, arxiv 2101.03961)](https://arxiv.org/abs/2101.03961)
- [GShard conditional computation (Lepikhin et al. 2020, arxiv 2006.16668)](https://arxiv.org/abs/2006.16668)
- [Differentiable Neural Computer (Graves et al. 2016)](https://www.nature.com/articles/nature20101)
- [Biased competition selective visual attention (Desimone & Duncan 1995)](https://www.annualreviews.org/doi/10.1146/annurev.ne.18.030195.001205)
- [Capacity Analysis of VSA (arxiv 2301.10352)](https://arxiv.org/abs/2301.10352)
- Internal: `notes/research_gap1_cortex_as_router_brain_mechanism_2026-06-26.md` (prior depth drill on separate-pathway routing)
- Internal: `notes/research_drill_brain_multihop_M1_schema_chunking_cortex_3x_2026-06-27.md` (complementary schema-chunking)

---

**End of drill.** TOP-1 P_deflated = 0.45 (Mante-2013 multiplicative gating — math+brain convergence); TOP-2 P_deflated = 0.35 (Miller-Cohen biased-competition). 10-point fairness discipline is MUST-INCLUDE pre-reg for any cell using cortex-as-operator framing.
