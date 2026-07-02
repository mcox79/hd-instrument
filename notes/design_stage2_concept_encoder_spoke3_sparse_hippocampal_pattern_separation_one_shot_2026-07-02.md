# Stage 2 Spoke 3 — Sparse hippocampal-analog pattern-separation index for one-shot new-concept binding + slow consolidation

**Filed:** 2026-07-02 evening (post-brain-best-in-class strategic pivot)
**Anchor:** `substrate_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_v1`
**USER anchor 2026-07-02:** brain function is best-in-class reference standard
**Composes with:** Stage 2 Spoke 1 (predictive coding + competitive allocation + char+positional) — `notes/design_stage2_concept_encoder_spoke1_predictive_coding_competitive_allocation_2026-07-02.md`; and Stage 2 Spoke 2 (Foldiak temporal-contiguity trace) — `notes/design_stage2_concept_encoder_spoke2_temporal_contiguity_slow_feature_analysis_2026-07-02.md`.
**Motivation:** Spokes 1+2 give the substrate concept HDs that (i) emerge from co-occurrence and (ii) are paraphrase-invariant. Both mechanisms are slow — many exposures of a concept are required before the gradient-descent-like Hebbian rule locks it in. The brain does not work this way. When you meet a new person, their name binds after one exposure and is usable in the next conversation. Spoke 3 gives the substrate that same fast one-shot binding without disturbing Spokes 1+2's slow, stable cortical concepts, via a hippocampal-analog sparse index + slow replay-based consolidation.

## Substrate-KB concept-query result (mandatory pre-design)

Ran per USER-locked concept-query mandate (2026-07-01):

### Q1: hippocampal sparse pattern separation dentate gyrus CA3
Top hits (v1 KB, cos filtered):
- Rank 1: `Parahippocampal gyrus` cos=0.372 (neurolex anatomy)
- Rank 4: `Dentate gyrus` cos=0.327 (neurolex; PART_OF HIPPOCAMPUS; PROJECTS_TO HIPPOCAMPUS_CA3)
- Rank 5: `DENTATE_GYRUS` cos=0.327 (curated fallback; PART_OF HIPPOCAMPUS; PROJECTS_TO HIPPOCAMPUS_CA3)

Interpretation: neuroanatomy is in the substrate; NO prior substrate-arc cell has attempted DG/CA3-analog sparse pattern separation as a mechanism.

### Q2: complementary learning systems episodic memory consolidation
Top hits:
- Rank 1: `Complementary Learning Systems family` cos=0.467 (school atom)
- Rank 2: `Complementary Learning Systems (CLS)` cos=0.467 (math atom, TIER=T2 primitive)
- Rank 4: `Memory consolidation` cos=0.422 (science atom)
- Rank 5: `SCHOOL/complementary_learning_systems_family` cos=0.411

Interpretation: CLS THEORY is already a T2 primitive in the substrate. CLS is atomized as a school/family and as a primitive but NO cell has built the CLS composition (fast hippocampus + slow cortex + replay-consolidation) in code.

### Q3: one shot binding fast index sparse coding substrate
Top hits:
- Rank 1: `binding` cos=0.354 (generic)
- Rank 2: `substrate_encoding_shotgun_native_v1` cos=0.337 (**HARD_FAIL**, VERDICT_OF metric edge)
- Rank 3: `SPARSE_CODING_HARD_FAIL` cos=0.331 (`exp_wave14_sparse_coding_ppmi_v1` — HARD_FAIL)
- Rank 5: `exp_substrate_sequence_binding_v1` cos=0.323 (prereg only, exists in several cross-modal binding preregs)

Interpretation: TWO prior sparse-coding attempts hit HF (wave14 PPMI-sparse + shotgun-native). Both are earlier-Stage sparse-coding attempts at the encoder level; both known-negative.

### Prior-arc explicit reference (2026-06-23 sparse_engram_allocation)

The 2026-06-23 `sparse_engram_allocation_smoke_v1` HF (memoralized in `reference_sparse_engram_allocation_v1_FULL_HF_naive_WTA_falsified_2026-06-23.md`) is NOT surfacing on either of my specific queries above (chunk KB not covering the reference note, and the anchor doesn't share vocabulary with the queries). I know it exists from context/memory: it FALSIFIED naive WTA-collision-minimizing sampling at N=4096 3-seed FULL. Sparse-K10-competitive got noise=0.065, cap=10 (vs dense 1.0 / 10K). Load-bearing lesson: **sparse coding needs a LEARNING driver, not random-collision-minimization**.

Spoke 3 must AVOID the specific mechanism that HF'd:
- No pure WTA-collision-minimizing sampling
- No sample-N-candidate-position-sets-then-pick-lowest-collision
- No sparse code with NO learning driving which dimensions activate

## Brain mechanism review (plain-English, brain-best-in-class)

### Dentate gyrus (DG) — expansion + extreme sparsity + lateral inhibition

The DG receives input from entorhinal cortex (EC) layer II — roughly 40K EC neurons project to millions of DG granule cells (~10-100× expansion). Only ~1-3% of DG neurons are active at any moment. This extreme sparsity is enforced by:
- **Lateral inhibition** via basket cells (GABAergic; not random collision — active competition)
- **Sparse feedforward projection** from EC (each DG cell sees a different random subset of EC axons)
- **High threshold** on DG granule cell firing

The combination — expansion + lateral inhibition + high threshold — is called PATTERN SEPARATION: two similar EC inputs get mapped to very different DG codes. This lets the hippocampus store many episodes without interference.

### CA3 — recurrent auto-associator (Marr 1971)

CA3 receives sparse DG codes via mossy fibers (very strong, few-synapse "detonator" projections) and has extensive recurrent collaterals. CA3 acts as a Marr-1971 auto-associator: one-shot Hebbian binding on sparse DG code, then pattern completion at retrieval (partial cue → full pattern via recurrent dynamics).

### Consolidation — hippocampal replay drives cortical learning (Wilson-McNaughton 1994; McClelland-McNaughton-O'Reilly 1995)

During slow-wave sleep, hippocampal CA3 replays recent activity patterns at ~20× speed. This replay drives cortical (neocortex) Hebbian learning, transferring episodic memory from hippocampus to cortical semantic memory over hundreds of replay cycles. Complementary Learning Systems theory (McClelland/O'Reilly 1995): fast hippocampal binding + slow cortical consolidation, both are necessary; either alone breaks (fast-only → catastrophic interference; slow-only → no one-shot).

### Why the 2026-06-23 mechanism failed and DG/CA3-analog can succeed

The falsified mechanism was PURE ALLOCATION with no learning — it minimized collisions via sampling. The brain's DG does NOT sample-then-minimize; it computes DG activation as EXPANSION + THRESHOLD + INHIBITION on the input pattern. Two properties are load-bearing:

1. **Expansion first, then sparsify.** 2026-06-23 mechanism started sparse (10 non-zeros out of N=4096) — too sparse (0.25%) for information capacity. DG-analog target sparsity is ~1% (∼80 non-zeros at N=8192).
2. **Learning driver, not sampling.** DG activation is DRIVEN by input pattern via expansion projection; the sparsity comes from threshold, not from collision-sampling. CA3 THEN does Hebbian outer-product learning on the sparse DG code — the LEARNING happens in CA3, not in the DG-allocation step.

Spoke 3's DG-analog = expansion projection (random) + top-K threshold with k=1% + optional lateral-inhibition normalization. Its CA3-analog = Marr auto-associator via Hebbian outer product on the sparse code. Its consolidation = replay of stored CA3 patterns as inputs to Spokes 1+2 cortical encoder over many cycles.

## Substrate-native mechanism review

Existing hdlab primitives that compose for Spoke 3:

- `hdlab/learning.py::HebbianAssociations` — reward-modulated sparse-atom co-activation weights. Not directly Marr auto-associator (it's atom-pair weights, not dense outer-product on HD codes), but the update rule is Hebbian and the sparse-storage architecture is right. **Candidate for CA3-analog with modification** OR use HRR-outer-product directly on sparse DG codes.
- `hdlab/continual.py::replay_cycle` — periodic re-Hebbian of stored (k, v) pairs into W. This IS the consolidation mechanism, atomized as MEASURED_MECHANISM at +0.57 drift_reduction (NREM replay analog). **Directly usable for Spoke 3 consolidation loop.**
- `hdlab/memory.py::Codebook` — sparse index registry mapping names→vectors. **Directly usable as the CA3 pattern registry** (stores CA3 codes indexed by episode-id or concept-id).
- `hdlab/excitability.py::excitability_trace_allocation` — Tonegawa excitability trace winner-take-all (Spoke 1's WTA). **Composable as the DG-analog sparse-threshold step**, though Spoke 1 already uses it for its own WTA at higher sparsity; Spoke 3 needs a SEPARATE much-sparser variant.
- `hdlab/predictive_coding.py` (Spoke 1) — provides the "cortical" concept HDs that consolidation writes to.
- `hdlab/binding.py::hd_bind` — HRR bind, used for composing DG-code × CA3-code and for constructing the expansion projection.

Missing (new for Spoke 3):
- `hdlab/dg_expansion_projection.py` — random-projection expansion + top-K threshold + optional lateral-inhibition normalization; ~100-150 lines new.
- `hdlab/ca3_autoassociator.py` — Marr-style Hebbian outer-product on sparse DG codes; pattern-completion via one settling step; ~150-200 lines new.
- `hdlab/hippocampal_index.py` — orchestrator composing DG expansion → CA3 auto-associator → Codebook registry + replay-consolidation loop into Spokes 1+2; ~300-400 lines new.

## Candidate mechanisms (4 options)

### Option A — Marr-1971 CA3 auto-associator on random-projection DG code (RECOMMENDED)

**Mechanism:**
1. **DG-analog:** random-projection expansion `dg = P @ (Spoke1_output)` where `P` is a fixed random ~2× expansion projection (N → 2N). Apply top-K threshold with K=0.01·(2N) (target ~1% sparsity). Optional lateral-inhibition normalization (subtract mean of active dims). Output: sparse ternary `dg_code ∈ {-1, 0, +1}^{2N}`.
2. **CA3-analog:** for each new concept c, one-shot Hebbian outer-product write `W_ca3 += dg_code_c · dg_code_c^T`. Pattern completion via one settling step: `dg_completed = sign(W_ca3 @ dg_partial)`.
3. **Consolidation:** every M new concepts, replay stored CA3 codes as inputs to Spokes 1+2 encoder (using `continual.py::replay_cycle` architecture). Cortical concept HDs update via Spokes 1+2 slow Hebbian on the replayed patterns.
4. **Retrieval:** at query time, encode query via Spokes 1+2 (cortical) AND via DG+CA3 (hippocampal). Return top-K from BOTH pools, ranked by hippocampal similarity for recent concepts and cortical similarity for well-consolidated concepts.

- **Local:** yes — random projection is fixed; top-K is per-neuron threshold; Hebbian outer-product is local; replay is local per-pair.
- **Composes with Spokes 1+2:** as a PARALLEL FAST PATH from raw text → DG code → CA3 index. Cortical concept encoding (Spokes 1+2) unmodified. Consolidation reads FROM CA3 registry and writes INTO cortex via the existing Spokes 1+2 Hebbian rule.
- **Historical support:** Marr 1971 auto-associator theoretically proven for one-shot binding on sparse codes; McClelland/O'Reilly 1995 CLS-model computational evidence; contemporary neural HDR (Bricken et al. 2023 Anthropic superposition + sparse coding).

**Weakness:** the random-projection expansion doesn't itself LEARN — it's fixed. This is faithful to DG's mostly-fixed EC→DG projection but means DG's discriminative capacity is set at initialization. Mitigation: verify at N large enough that random-projection separation is provably good (Johnson-Lindenstrauss bound covers this for k=~1%).

### Option B — Expansion + Hebbian-adjusted projection (learning DG)

**Mechanism:** identical to Option A except the projection `P` is initialized random then adjusted by Hebbian rule on the DG output: `dP ~ dg_code · Spoke1_output^T`. Over time, the projection tunes to the input distribution.

- **Local:** yes.
- **Composes with Spokes 1+2:** same parallel path.
- **Historical support:** learned-sparse-coding literature (Olshausen-Field 1996 sparse coding V1). Not clearly DG-faithful — biological DG projection appears largely fixed after development.

**Weakness:** MORE MACHINERY and closer to Spoke 1's mechanism (Spoke 1 already learns via Hebbian). Doesn't add clear brain-analog value over Option A. Risk of learning-collision with Spoke 1's competitive-allocation update.

### Option C — Continuous-attractor hippocampal-cortical CLS with online replay

**Mechanism:** dense Hopfield-network CA3 + REM/NREM-differentiated replay (continual.py replay + companion synaptic-homeostasis global-downscale). Uses the full atomized CLS family primitives.

- **Local:** yes.
- **Composes with Spokes 1+2:** larger footprint; needs continual.py's replay engine wired to Spokes 1+2 Hebbian rule.
- **Historical support:** classical Hopfield + biologically-plausible CLS.

**Weakness:** DENSE CA3 codes have well-known capacity bound (~0.14N patterns before catastrophic interference). Sparse CA3 codes are ~10× higher capacity (Tsodyks-Feigel'man 1988). Option C loses that benefit.

### Option D — Learned expansion via predictive-coding on hippocampal readout

**Mechanism:** DG projection learned by minimizing prediction error of DG code reconstructing input. Novel synthesis — no direct brain grounding, extends Rao-Ballard PC into DG.

**Weakness:** high novelty. Novel-synthesis P_CG cap 0.50 from lit-scan calibration. Multiple hyperparameter interactions with Spoke 1's PC layer. Defer to Spoke 3 v2 if v1 negative.

### Recommendation: Option A primary, Option C secondary arm, Option B/D deferred

Option A is the minimal-mechanism Marr auto-associator on random-projection DG code — historically the winner of the sparse-hippocampal-index literature, adds three additive components (expansion projection + top-K + Hebbian outer-product) with clear brain grounding, and avoids the falsified 2026-06-23 mechanism explicitly (learning driver via Hebbian, expansion before sparsify, k=1% target). Option C provides the dense-Hopfield contrast arm to prove sparsity is doing work. Options B/D defer to Spoke 3 v2.

## Cell design

**Anchor:** `exp_substrate_concept_encoder_spoke3_sparse_hippocampal_pattern_separation_one_shot_v1`

**Prereq:** Spoke 1 CG (or MM); Spoke 2 CG (or MM). If either HF, Spoke 3 mechanism cannot be cleanly evaluated on top (falls back to random-codebook cortical HDs).

### Arms (6 arms × 3 seeds = 18 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_CORTEX_ONLY | Spokes 1+2 without any hippocampal path | Baseline — no fast binding, no one-shot |
| ARM_DG_CA3_MARR | DG expansion + top-K k=1% + Marr CA3 outer-product (Option A) | LOAD-BEARING (brain-analog CLS) |
| ARM_DG_ONLY_NO_CA3 | DG code stored raw; no CA3 auto-association; direct cosine retrieval | Ablation: proves CA3 auto-associator matters |
| ARM_CA3_DENSE_HOPFIELD | Dense Hopfield CA3 (no DG sparsification); Option C contrast | Ablation: proves sparsity matters |
| ARM_NO_CONSOLIDATION | Option A but NO replay-consolidation loop | Ablation: proves consolidation is load-bearing for retention |
| ARM_NAIVE_WTA_COLLISION_CONTROL | The 2026-06-23 falsified mechanism (WTA-collision-minimizing sampling) at k=1% | Sanity: reproduces prior HF; confirms Spoke 3 is doing something different |

### Corpus (episodic + concept-drift design)

**Smoke:** 200 concepts total. Structure per concept: 5 exposures over time (Spokes 1+2 slow-learning path benefits from repetition). Then INSERT 20 NEW-CONCEPT one-shot events at random points in the stream — each brand-new concept is introduced ONCE and immediately probed for retrieval (measures one-shot binding). Between one-shot events, the corpus continues showing the 200 base concepts. After all 20 one-shot events, run N replay-consolidation cycles, then re-probe the one-shot concepts for CONSOLIDATED cortical retrieval.

Corpus size: 5000 sentences over 200 base concepts + 20 one-shot events × 1 sentence each + probe queries per event.

Ground truth: concept-identity label per sentence; one-shot-event index and timestamp; probe target for each event (partial cue → full pattern completion target).

**FULL:** 10K base sentences over 500 concepts + 50 one-shot events with cued-retrieval + consolidation-retention probing at increasing delay intervals (Wickelgren-style forgetting curve measurement).

### Metrics per arm × seed

- `one_shot_top1_immediate`: for each one-shot event, top-1 retrieval accuracy on IMMEDIATE probe (target ≥ 0.7 for ARM_DG_CA3_MARR; ≈ 0 for ARM_CORTEX_ONLY since cortex hasn't seen the concept multiple times)
- `one_shot_top1_after_consolidation`: same but after N replay cycles; measures whether cortex learned from consolidation (target ≥ 0.5 for ARM_DG_CA3_MARR; ≤ 0.1 for ARM_NO_CONSOLIDATION)
- `pattern_completion_from_partial`: retrieve full pattern given 50%-masked cue; measures CA3 auto-associator (target ≥ 0.7 for ARM_DG_CA3_MARR; ≈ chance for ARM_DG_ONLY_NO_CA3)
- `cortex_interference`: on base 200 concepts, mean intra-concept cos before vs after 50 one-shot events (measures whether one-shot binding interferes with slow-learned cortical concepts; target: change ≤ 0.05 for ARM_DG_CA3_MARR; large drop for ARM_CA3_DENSE_HOPFIELD if it has capacity-collapse)
- `dg_sparse_rate`: mean fraction of DG dimensions active (target [0.008, 0.02] for ARM_DG_CA3_MARR; verify architecturally)
- `naive_wta_replicates_hf`: ARM_NAIVE_WTA_COLLISION_CONTROL one_shot_top1_immediate ≤ 0.15 (reproduces the 2026-06-23 HF)
- `arm_digest`: hash of concept-HD + CA3-code table per arm

### HP bands (HP_SCOPE: LOAD-BEARING on ARM_DG_CA3_MARR)

**HARD_PASS (target CG):**
- ARM_DG_CA3_MARR one_shot_top1_immediate ≥ 0.7 (one-shot binding works)
- ARM_DG_CA3_MARR one_shot_top1_after_consolidation ≥ 0.5 (consolidation transfers episodic → semantic)
- ARM_DG_CA3_MARR pattern_completion_from_partial ≥ 0.7 (CA3 auto-associator is functional)
- ARM_DG_CA3_MARR cortex_interference ≤ 0.05 (base cortical concepts protected)
- ARM_DG_CA3_MARR dg_sparse_rate ∈ [0.008, 0.02] (DG architecture invariant)
- ARM_DG_CA3_MARR one_shot_top1_immediate beats ARM_CORTEX_ONLY by ≥ +0.60 (hippocampal path indispensable for one-shot; cortex alone cannot do it)
- ARM_DG_CA3_MARR one_shot_top1_after_consolidation beats ARM_NO_CONSOLIDATION by ≥ +0.40 (consolidation is load-bearing)
- ARM_DG_CA3_MARR pattern_completion_from_partial beats ARM_DG_ONLY_NO_CA3 by ≥ +0.30 (CA3 outer-product is load-bearing)
- ARM_NAIVE_WTA_COLLISION_CONTROL one_shot_top1_immediate ≤ 0.15 (2026-06-23 HF reproduced — mechanism-difference is architectural)
- 3-seed HP; cv across seeds < 0.15

**HARD_FAIL:**
- ARM_DG_CA3_MARR one_shot_top1_immediate < 0.30 (one-shot binding not achieved)
- OR ARM_DG_CA3_MARR pattern_completion_from_partial < 0.35 (CA3 not doing pattern completion)
- OR ARM_DG_CA3_MARR cortex_interference > 0.20 (hippocampal writes destroy cortex — CLS decoupling broken)
- OR ARM_DG_CA3_MARR dg_sparse_rate outside [0.003, 0.05] (DG architecture broken)
- OR ARM_NAIVE_WTA_COLLISION_CONTROL one_shot_top1_immediate > 0.35 (control accidentally passes — cell arms aren't distinguishing)

**MIDDLE_BAND:**
- Any target intermediate → v2 with sparsity sweep, or Option B (Hebbian-adjusted projection), or replay-schedule tuning.

### Sanity + integration gates

- ARM_CORTEX_ONLY one_shot_top1_immediate ≈ chance (≤ 0.10) — proves cortex cannot do one-shot; validates the strategic motivation
- ARM_CORTEX_ONLY on the 200 base concepts matches Spoke 2's v1 numbers (regression sanity)
- ARM_NAIVE_WTA_COLLISION_CONTROL one_shot_top1_immediate matches 2026-06-23 sparse_K10_competitive noise=0.065 pattern (reproduces prior HF; validates the arm faithfully implements the falsified mechanism)
- ARM_DG_CA3_MARR dg_sparse_rate monotonic w.r.t. top-K threshold parameter (verify parameter is doing work)
- ARM_CA3_DENSE_HOPFIELD hits capacity collapse by concept 50-100 (Hopfield ~0.14N bound; validates capacity gap between dense/sparse)

### Substrate primitives called

- All Spoke 1 + Spoke 2 primitives (composed to build cortical encoding)
- Existing `hdlab/continual.py::replay_cycle` for consolidation loop (MEASURED_MECHANISM at +0.57 drift reduction — proven-bound composition point)
- Existing `hdlab/memory.py::Codebook` for CA3 index registry
- Existing `hdlab/excitability.py::excitability_trace_allocation` reused at k=1% for DG-analog top-K
- New: `hdlab/dg_expansion_projection.py` — random projection + top-K + optional lateral-inhibition normalization (~150 lines new)
- New: `hdlab/ca3_autoassociator.py` — Marr Hebbian outer-product + one-step settling (~200 lines new)
- New: `hdlab/hippocampal_index.py` — orchestrator (~350 lines new)
- No backprop, no gradient, no global error signal

### CELL-TEMPLATE MANDATORY compliance

Standard: arms_differ_verified (18 unique arm_digest), except SystemExit before except Exception, tmp_replace metrics, cardinality_ok, HP_SCOPE=LOAD_BEARING on ARM_DG_CA3_MARR, DG-sparse-rate architectural constraint verified, ARM_NAIVE_WTA_COLLISION_CONTROL reproduces 2026-06-23 falsified mechanism faithfully (this is verified by digest match on the sparse allocator's core loop), consolidation-cycle count HP-fixed and documented, replay-schedule fixed at continual.py default (every 100 events), ASCII-only.

### Compute architecture

- (a) batched-CPU-torch; corpus fits in memory
- DG expansion projection is O(N × 2N) matmul per input — the largest per-token op; consider caching batched
- CA3 outer-product write is O(k² · 2N) where k is #active dims ~ 80 — cheap per write
- Consolidation cycles are the heaviest cost — each cycle re-runs Spokes 1+2 slow-Hebbian on stored CA3 codes; count is HP-fixed
- Per-seed smoke wall estimate: ~5-10 min (5000 sentences + 20 one-shots + N replay cycles)
- FULL wall: ~30-60 min (10K + 50 one-shots + retention probing at delay intervals)
- Route: local_cpu smoke (USER SMOKE_ONLY_LOCAL); remote_cpu_queue for FULL

### Dispatch prereqs

1. Spoke 1 CG landed AND Spoke 2 CG landed (both extracted to hdlab; Spoke 3 imports them)
2. `dg_expansion_projection.py` + `ca3_autoassociator.py` + `hippocampal_index.py` authored + selftests passing
3. Cell file + prereg SCHEMA-VET (Skunkworks) with explicit citation of 2026-06-23 sparse_engram_allocation HF and mechanism-difference justification
4. Smoke gate on local_cpu — must show ARM_NAIVE_WTA_COLLISION_CONTROL reproduces prior HF signature (noise ≤ 0.10 at scale) before FULL dispatch

## Composability picture (Spokes 1+2+3 composed)

```
raw text ("Alice met Bob today")
    |
    v
[char + positional encoder]                    <-- Spoke 1
    |
    v
[predictive coding Hebbian with trace]         <-- Spoke 1 + Spoke 2 (temporal trace)
    |
    v
[competitive allocation WTA k=~2%]             <-- Spoke 1
    |
    | h_cortex (Spoke 1+2 cortical concept HD)
    |
    +--> [cortical readout / storage]          -- slow, semantic
    |
    v
[DG expansion projection P: N -> 2N]           <-- Spoke 3 NEW
    | random-fixed expansion
    v
[top-K threshold k=~1% + lateral inhibition]   <-- Spoke 3 NEW
    | dg_code (sparse, ternary)
    v
[CA3 Marr auto-associator, Hebbian outer]      <-- Spoke 3 NEW
    | W_ca3 += dg_code · dg_code^T (one-shot write)
    v
[Codebook stores CA3 pattern by episode-id]    <-- Spoke 3 registry
    |
    v
[Retrieval: partial cue -> DG expand -> CA3 settle -> completed pattern]
    |
    v
[Consolidation loop: every 100 events,
 replay CA3 patterns as inputs to Spoke 1+2 cortical Hebbian]  <-- Spoke 3 replay via continual.py
    |
    v
episodic HD becomes semantic-cortical HD over N replay cycles
```

**Architectural placement:** Spoke 3 is a **parallel path** from Spoke 1+2's h_cortex — one branch writes to slow cortex (unchanged), the other branch writes to fast hippocampal DG+CA3 index. Retrieval blends both, weighted by concept age / consolidation-progress. This preserves Spokes 1+2 as-is (no modification to their Hebbian rules) while adding the one-shot binding capability.

**Alternative placement (fallback):** if parallel-path Option A HF, v2 fallback = SEQUENTIAL — Spoke 3 becomes the first-stage encoder and Spokes 1+2 read from CA3 codes only. Loses the CLS decoupling (fast/slow) but is simpler. Preserved as v2 in HP band routing.

## P_CG estimate + calibration reasoning

**Pre-deflation P_CG:** ~0.50 based on lit support:
- Marr 1971 auto-associator + McClelland-O'Reilly 1995 CLS + Wilson-McNaughton 1994 replay is the strongest brain-mechanism theoretical foundation of any spoke (Nobel-adjacent lineage).
- Substrate has the supporting primitives (continual.py replay + Codebook + Hebbian) — three of the five components are already atomized.
- Composability with Spokes 1+2 is CLEAN as PARALLEL PATH (no modification to their weights).
- 2026-06-23 sparse_engram HF is EXPLICITLY diagnosed (naive WTA-collision-sampling vs learned Marr outer-product on expansion-projected code) and Spoke 3 mechanism differs in three orthogonal ways (expansion first, learning driver via Hebbian, k=1% not 0.25%).

**Deflations (lit-scan calibration penalty; USER-locked cap novel-synthesis at 0.50):**

- **-0.10** for novel-substrate-composition (DG-expansion + Marr-CA3 + CLS-consolidation composition hasn't been done in HD substrate literature specifically that I've located; hitting the 0.50 novel-synthesis cap)
- **-0.05** for the DG-expansion projection using a FIXED random projection (not learned) — the expansion projection choice is a mechanism-detail that a HF outcome could pin on this (Option B would be v2)
- **-0.10** for HIGHER PARAMETER COUNT than Spokes 1/2 (three additional components; sparsity target + replay cadence + expansion factor + top-K threshold all interact)
- **-0.10** for STRONG PREREQ DEPENDENCE — Spoke 3 conditional on both Spoke 1 CG AND Spoke 2 CG; either MM-only weakens the whole assembly and could produce MB even if Spoke 3's own mechanism is sound
- **-0.05** for the 2026-06-23 sparse-coding prior HF making Skunkworks reasonably more conservative on any sparse-mechanism cell (defensible prior)
- **-0.05** for the "one-shot binding" claim being high-bar — top-1 ≥ 0.7 on immediate retrieval is a strong claim; a MM at 0.4-0.6 range is plausible

**Post-deflation P_CG: ≈ 0.10 (conditional on Spoke 1 CG AND Spoke 2 CG both landing at CG)**

**Conditional table:**
| Spoke 1 verdict | Spoke 2 verdict | Spoke 3 P_CG |
|---|---|---|
| CG | CG | **0.10** (post-deflation) |
| CG | MM | 0.06 |
| MM | CG | 0.06 |
| MM | MM | 0.04 |
| Any HF | any | 0.02 (Spoke 3 mechanism cannot be evaluated on broken cortex) |

Note: P_CG is intentionally CONSERVATIVE — this is the highest-novelty spoke of the three (Spoke 1 uses well-established PC+WTA composition; Spoke 2 uses well-established Foldiak trace; Spoke 3 requires the substrate to succeed at CLS one-shot + consolidation which is closer to a research frontier). P_MM (measured-mechanism partial credit) is higher — estimated ~0.30 post-deflation conditional on Spoke 1 CG. Combined P(CG-or-MM) ≈ 0.40.

## Post-verdict routing

**HARD_PASS:** Spoke 3 CG. Extract `dg_expansion_projection.py` + `ca3_autoassociator.py` + `hippocampal_index.py` to hdlab (following M1.9 pattern). Fire Spoke 4 (grounding + sensorimotor) design work. Big deal: composed Spokes 1+2+3 covers 6/6 brain-property criteria as CG-tier substrate.

**HARD_FAIL:** file CG_HONEST_NEGATIVE closing DG-expansion + Marr-CA3 + CLS-consolidation composition. Options for v2:
- (i) Option B (Hebbian-adjusted DG projection)
- (ii) Sequential-placement fallback (Spoke 3 as first-stage encoder feeding Spokes 1+2 instead of parallel path)
- (iii) Route to research 2x-drill on why sparse hippocampal-analog + CLS pattern didn't compose in substrate (may indicate substrate-HD-space itself doesn't support the required capacity — deeper problem)

**MIDDLE_BAND:** file MM_TENTATIVE; v2 fills the highest-lift knob: (a) sparsity sweep at 0.5%, 1%, 2%, 3% to find the DG-analog sweet spot; (b) consolidation cadence sweep at 20, 100, 500 cycles/replay; (c) if pattern_completion PASSES but one_shot_top1_after_consolidation FAILS, the CA3 side is fine but consolidation isn't transferring — route to Spoke 3.5 = consolidation-mechanism-only cell.

## What CG at Spoke 3 unlocks

Substrate gains **one-shot new-concept binding** — introduce "the storage strategy Alice mentioned last night" ONCE and the substrate can retrieve it in the next query, even though cortex hasn't consolidated it yet. Over hours/days of use, that fast-hippocampal binding transfers to cortex, and the concept becomes semantic (available even after CA3 forgetting).

Combined Spoke 1 + Spoke 2 + Spoke 3 achieves the full brain-property criteria:
- (1) Emerged from data ✅ (Spoke 1)
- (2) Sparse-distributed ✅ (Spoke 1 + Spoke 3 sparse DG)
- (3) Predictive ✅ (Spoke 1)
- (4) Compositional ✅ (Spoke 1 HRR bind)
- (5) Grounded — partial ✅ via temporal-contiguity invariance (Spoke 2)
- (6) Continually updateable ✅ via CLS fast-hippocampus + slow-cortex + replay-consolidation (Spoke 3)

USER's dogfooded substrate-Director-KB gets to work like biological memory: a decision made in this session binds fast (Spoke 3 hippocampal), is retrievable immediately, and gradually consolidates into the cortical semantic store (Spokes 1+2) over subsequent sessions — no catastrophic forgetting, no giant one-shot exposure requirement, no borrowed embeddings.

## Reference: 2026-06-23 sparse_engram_allocation HF explicit mechanism-difference

| Property | 2026-06-23 (falsified) | Spoke 3 v1 (Option A) |
|---|---|---|
| Sparsity level | k=10 out of 4096 = 0.24% | k=~80 out of 16384 = 0.5% (DG-analog) |
| Sparsity mechanism | Sample-N-candidate-position-sets, pick lowest-collision | Expansion projection + top-K threshold |
| Learning | NONE (pure allocation) | Marr Hebbian outer-product on CA3 |
| Expansion before sparsify | NO | YES (N→2N random projection) |
| Consolidation | NONE | YES (replay-cycle to cortex every 100 events) |
| Underlying theory | Tonegawa CREB excitability | Marr 1971 auto-associator + CLS |
| N | 4096 | 8192 (with 2× expansion to 16384) |

Three orthogonal mechanism-differences. Cell explicitly includes ARM_NAIVE_WTA_COLLISION_CONTROL to reproduce the 2026-06-23 HF at Spoke 3's scale, proving the load-bearing distinction is architectural not scale-dependent.
