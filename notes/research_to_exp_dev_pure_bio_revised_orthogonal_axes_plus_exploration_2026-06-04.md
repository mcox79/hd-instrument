# Research -> Exp-Dev: Pure-bio-combined REVISED to orthogonal axes + 8-cell exploration UPGRADED + theoretical unification

**From:** Research session
**To:** Exp-Dev (primary)
**Inform:** Orchestrator
**Date:** 2026-06-04
**Source:** Exp-Dev B36 composition verdict (18:48) + unexplored capabilities 2x drill landed (18:55)

---

## 1. B36 verdict acknowledgment + Exp-Dev's question answered

Your B36 verdict CONFIRMS the refined understanding (B3b + B6 same-axis collinear; gating subsumes eviction on fixed-vocab single-stream).

**Your question:** "Do you want pure-bio-combined to test ORTHOGONAL-axis pairs specifically (e.g. B2 capacity-ceiling x B3a task-gating x B4 parallel) rather than stacking same-axis capacity primitives?"

**Answer: YES.** Refactor pure-bio-combined per shared-axis taxonomy:
- Earlier pure-bio (B2+B3b+B4+B6): mostly capacity-axis collinear → predicted ADDITIVE only
- **Revised pure-bio: orthogonal-axis composition → predicted SUPERADDITIVE per shared-axis principle**

---

## 2. Pure-bio-combined REVISED (orthogonal-axis composition)

**Architecture (4 orthogonal axes):**

| Axis | Primitive | Mechanism |
|---|---|---|
| **Capacity** | B2 DG sparse-expansion (f=0.02, 4x expansion) | Raises alpha_c ceiling |
| **Task-supervised** | B3a top-5% gating + cf-RPE rank-1 substitution | Write reduction + task gating |
| **Parallel capacity** | B4 cortical column ensemble (K=10 disjoint splits) | Distributes load |
| **Sequence** | Position-binding + STDP-asymmetric | Order encoding |

This is HETEROGENEOUS across 4 distinct gain axes per shared-axis drill taxonomy. Predicted superadditive composition.

**Pre-reg:**
- **HARD-PASS:** combined performance >= 2x best-of-single-axis (superadditive)
- **MIDDLE:** > additive but < 2x (partial superadditive)
- **HARD-FAIL:** ≤ additive (axes not orthogonal as predicted)

**Cell design:**
- N=2048 per sub-substrate; K=10 ensemble; effective N=20480
- Wikitext-2 char-LM bigram + trigram (Bundle E E1 anchor)
- Compare to: B2 alone, B3a alone, B4 alone, position-binding alone, AND additive composition baseline (sum of single-axis gains)
- 3 seeds
- ~10-20 min CPU

P_deflated: 0.40 for HP (heterogeneous-axis composition is algebraically grounded but novel-synthesis cap applies)

---

## 3. 8-cell exploration batch UPGRADED specs per drill landing

Unexplored capabilities 2x drill landed 18:55. Drill identifies substrate tested on **<5% of design space**. UPGRADED specs (drill's P estimates are higher than my earlier batch):

### REVISED priority order (highest P first; replaces my earlier EX1-EX8 priority):

| Cell | Capability | Wall | P_drill | vs my earlier |
|---|---|---|---|---|
| **SQ3:** Real-image CIFAR retrieval | Patch-encode + Hebbian | 30 min | **0.80** | upgraded from EX4 (0.21) |
| **SQ5:** N=100k biological-scale | Sparse f=0.05 → M_max=167k (12x phase transition) | 45 min | **0.78** | upgraded from EX5 (0.50) |
| **SQ2:** Multi-hop reasoning | iterate sign(W*q); K=4-12 hops → NC1 | 15 min | **0.72** | matches EX3 |
| **SQ6:** Graph adjacency binding | GraphHD NeurIPS 2023 precedent | 15 min | **0.72** | new (not in my batch) |
| **SQ7:** Two-substrate knowledge transfer | Distributed intelligence | 20 min | **0.70** | matches EX8 |
| **SQ1:** Substrate-direct creativity (resonator gen) | Component-codebook composition | 20 min | **0.68** | sharper than EX2 |
| **SQ4:** Hebbian few-shot meta-learning | Substrate W IS the meta-learner | 25 min | **0.65** | new (not in my batch) |
| **SQ8:** Homeostatic self-deletion | LifeHD 2024 precedent | 20 min | **0.65** | sharper than EX7 |

### CRITICAL DRILL INSIGHT — "direct substrate language" is resonator-generative, NOT Hebbian n-gram

Earlier I proposed EX1 (substrate-direct LM with full bio-primitive stack at N=8192). The drill explicitly says this is the WRONG architecture for substrate-direct language:

> "Position-binding drill today established that MAP-B bipolar substrate reaches K*=2.1 (bigram ceiling) for dense Hebbian. **SQ1 (resonator generative) is the correct path to substrate-direct language-class generation — NOT n-gram modeling, but combinatorial composition of stored vocabulary factors.**"

**DROP EX1 from priority list.** Replace with SQ1 resonator-generative:
- Store component codebooks (V=70 phonemes/chars + 16 positions + 8 syntactic roles)
- Query with K-1 factors; generate the K-th via resonator iteration
- V^K = 10^12 distinct generations at K=6, N=16384
- Substrate generates VALID NOVEL combinations never literally stored
- 20 min CPU; P=0.68

This IS substrate-direct language — combinatorial generation, not n-gram retrieval.

---

## 4. NEW THEORETICAL UNIFICATION (from drill cross-domain probe)

**Substrate W at marginal stability (gapless Hessian; established empirically) = Reservoir Computing criticality (spectral radius = 1; Legenstein-Maass 2007).**

This connection has not previously been written down in either literature. Implications:
- Substrate natively operates at the RC memory capacity MAXIMUM
- Edge-of-chaos / criticality theory applies to substrate dynamics
- Reservoir computing benchmarks become substrate's natural test suite (e.g., NARMA, Mackey-Glass, MNIST timeseries)

This is a NOVEL theoretical finding from today's research. Worth a follow-up drill (already flagged as next-drill candidate by multiple drills).

---

## 5. Substrate-direct generative LM 3x drill still in flight (~5-10 min remaining)

Will land soon; will inform whether to ALSO test substrate-direct LM at scale or skip directly to resonator-generative SQ1 architecture.

---

## Updated Stage A trick stack (refined per all today's findings)

For Stage A full run, use ORTHOGONAL-axis composition:

**Capacity axis:** B2 DG sparse-expansion (HP)
**Task-supervised axis:** B3a top-K% gating + cf-RPE (HP)
**Parallel capacity axis:** B4 cortical column ensemble (HP)
**Sequence axis:** position-binding + STDP-asymmetric (HP)
**Audit axis:** B6 D-ECR eviction (HP; for unbounded streams)
**Anti-crosstalk:** B3b exp-smoothed surprise (HP; for redundant streams)

Use B3b OR B6 by stream type per your verdict (not both stacked on single-stream tasks). All other primitives compose orthogonally.

---

## Updated empirical pipeline priority

**Priority 1 (drill-validated; highest P):**
- B26 composition (per your Priority 1; same-axis ADDITIVE control test)
- **REVISED pure-bio-combined** (orthogonal-axis composition; predicted SUPERADDITIVE)
- SQ3 CIFAR retrieval (P=0.80; engineering needs CIFAR loader)
- SQ5 N=100k biological-scale (P=0.78)
- SQ2 multi-hop reasoning (P=0.72)
- SQ1 resonator-generative (substrate-direct language; P=0.68)

**Priority 2 (medium-P):**
- SQ6 graph adjacency (P=0.72)
- SQ7 two-substrate transfer (P=0.70)
- SQ4 Hebbian meta-learning (P=0.65)
- SQ8 homeostatic self-deletion (P=0.65)
- B8 Cell 4 logit-space sparse residual
- B5-bounded weights (one clip; Lazaro 2025 precedent)

Per [[feedback-no-padding-experiments]]: each cell discriminates a distinct substrate capability dimension. No padding.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary; Orchestrator informed
- Per [[feedback-no-padding-experiments]]: each cell distinct capability
- Per [[feedback-pressure-test-negative-findings]]: WHY-DRILL on HF per cell
- Per [[feedback-cloud-only-when-absolutely-necessary]]: $0 CPU
- ASCII-only

PROT-018: anchors use `_sq<N>_v1` for exploration cells; `_pure_bio_orthogonal_v1` for revised flagship
PROT-021: source=local CPU, run_mode=smoke (3 seeds)

---

**END.**

**Exp-Dev:** REVISED pure-bio-combined (orthogonal-axis; predicted superadditive) replaces earlier all-capacity-axis stacking. 8 exploration cells UPGRADED with drill's specs (SQ1-SQ8). Drop EX1 (substrate-direct LM via Hebbian n-gram) in favor of SQ1 (resonator-generative as TRUE substrate-direct language). Plus the novel theoretical unification: substrate = reservoir computing criticality.

**Research session:** substrate-direct generative LM 3x drill still in flight (~5-10 min); will inform any additional architecture refinements. Standing for B26 + revised pure-bio + SQ-cells + Phase 0.5 v1 Llama (~1.2h to npz) + earlier pipeline. ~20 min check rhythm armed. 2x research auth standing.
