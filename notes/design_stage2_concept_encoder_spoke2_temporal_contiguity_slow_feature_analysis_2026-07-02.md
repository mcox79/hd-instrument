# Stage 2 Spoke 2 — Temporal contiguity trainer (SFA analog) design

**Filed:** 2026-07-02 evening (post-brain-best-in-class strategic pivot)
**Anchor:** `substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1`
**USER anchor 2026-07-02:** brain function is best-in-class reference standard
**Composes with:** Stage 2 Spoke 1 v3-D — competitive-Hebbian sparse coding ONLY (see [design v3-D](design_stage2_concept_encoder_spoke1_v3_WTA_base_PC_multiplicative_top_down_gain_2026-07-02.md) + [reference 5x drill convergence](../../../.claude/projects/d--AI/memory/reference_5x_drill_convergence_PC_redundant_with_WTA_for_concept_encoding_Spoke1_2026-07-02.md)).

## 🔬 AMENDMENT 2026-07-02 late evening — Spoke 2 is now the primary home for PC in Stage 2

Original Spoke 2 design (below) assumed Spoke 1 was PC + competitive allocation composed. 5x drill (6 of 6 convergent) + empirical drill (a51e4c) DECISIVELY FALSIFIED PC in Spoke 1 flat-composition. **Spoke 1 v3-D dropped PC entirely.** Consequences for Spoke 2:

1. **Spoke 2 becomes the load-bearing home for PC in the Stage 2 concept encoder.** Temporal contiguity is where 6 of 6 domain drills agree PC clearly wins its complexity:
   - Neuroscience: PC drives top-down invariance signals (DiCarlo IT, Friston active inference)
   - Math + info theory: PC earns complexity conditional on temporal input structure (Nessler 2013 conditional P_deflated=0.40 vs 0.22 generic)
   - ML/AI lit: I-JEPA-style latent predictive is one of two recommended v3 patterns (competitive base + temporal predictive)

2. **Foldiak trace rule design (below) STILL VALID as the primary Spoke 2 mechanism.** Foldiak IS a PC-like temporal predictive mechanism (post-synaptic factor = temporal trace = "predicted" future activity from current + past). It's the correct home for PC-style predictive dynamics.

3. **Optional stretch arm to add:** ARM_TRACE_PC_HIERARCHICAL — hierarchical PC modification of Foldiak trace, per Salvatori 2021 hierarchical PC. This would be the honest test of PC-in-correct-role: does hierarchical predictive stacking on top of competitive-Hebbian sparse base earn measurable complexity gain? P_CG conservative ≈ 0.30 (up from Spoke 2 baseline P_CG=0.35 due to composition risk with Spoke 1 v3-D bareness).

4. **Spoke 2 timeline expands slightly** to accommodate:
   - Base Foldiak trace on Spoke 1 v3-D (competitive-Hebbian) — 3-5 days (unchanged)
   - Optional hierarchical PC stretch arm — +2-3 days
   - Total: 5-8 days (up from 3-5)

**No content below is invalidated.** The Foldiak trace mechanism is exactly right for Spoke 2 regardless of Spoke 1 being PC + WTA or WTA alone — the trace operates on Spoke 1's post-synaptic activity, which is competitive-Hebbian winner activation in v3-D.

---

**Motivation:** Spoke 1 makes concepts EMERGE from co-occurrence but concepts do NOT yet know about INVARIANCE — a cat sentence and a paraphrased cat sentence get similar-but-different HDs. Spoke 2 adds temporal contiguity as a free-supervisor: adjacent-in-stream inputs get pulled together in HD space, non-adjacent stay apart. Brain analog: complex-cell learning in V1 (Foldiak 1991), invariant IT face-selective cell learning (DiCarlo & Cox 2007), Slow Feature Analysis (Wiskott & Sejnowski 2002).

## Substrate-KB concept-query result (mandatory pre-design)

Ran per USER-locked concept-query mandate.

- `bash tools/substrate_query.sh "slow feature analysis temporal contiguity invariance concept training"` (chunk_KB stale 126h; still ran):
  - Rank 1: v1 wordnet entity "invariance" cos=0.297 — generic dictionary hit, NO substantive prior work
  - Rank 2/3: `notes/research_to_testbed_..._TIME-BASED_ruleset...2026-06-13.md::chunk009` cos=0.273 — philosophy-of-time atoms (A-series/B-series/LTL), UNRELATED to SFA
  - Rank 4: `k_signal invariance` cos=0.272 from lock-in-amp cell — signal-processing invariance, DIFFERENT domain
- Prior arc work on SFA / temporal contiguity / Foldiak trace / slow-feature invariance: **NONE**

Safe to proceed with novel design. Chunk KB is 5.3d stale so I'm accepting mild uncertainty on the absence-claim, but the SFA / Foldiak / temporal-trace vocabulary is distinctive enough that a chunk-index hit would show up in the top-5 if it existed.

## Brain mechanism review (plain-English)

The brain learns concept invariance from **temporal contiguity** — the assumption that things you see close together in time are usually the same thing. When a cat walks in front of you, you see it from many angles in a few seconds. The visual system uses this: neurons whose activity is temporally slow-varying end up firing for "the same cat" across all those views, forming an invariant representation.

- **Foldiak trace rule (1991):** local Hebbian rule where post-synaptic activity is replaced by a running exponential trace of recent activity. Hebb learning on the trace makes representations that are temporally stable persist; transient patterns get suppressed. Proven to produce complex-cell-like invariance in V1 models.
- **Wiskott & Sejnowski SFA (2002):** formalized objective — find output functions y(x) that minimize <(dy/dt)²> subject to <y>=0, <y²>=1, and decorrelation across outputs. Provably extracts driving invariants of the input stream. In hierarchical form, reproduces complex cells, place cells, head-direction cells, view-invariant object cells.
- **Ventral stream (DiCarlo & Cox 2007; Li & DiCarlo 2008):** IT face-selective cells develop position/scale invariance from experience with temporally-continuous natural viewing. Experimental swap-manipulation (present two objects at same location within saccade window → IT neuron confuses them) directly demonstrated the mechanism.
- **Rao-Ballard predictive coding + temporal prior (Friston):** predictive-coding hierarchies with slow priors on higher layers formally implement SFA at the top layers.

**Load-bearing intuition:** Spoke 1 gives concepts a co-occurrence structure ("cat" and "kitten" cluster because their context-words overlap). Spoke 2 gives concepts INVARIANCE ("cat-front" and "cat-side" cluster because they appear in temporally-adjacent contexts, e.g. adjacent sentences of a paragraph about a cat).

## Substrate-native mechanism review

Existing hdlab primitives that could compose:

- `hdlab/sequence_memory.py::SequenceMatrix.bind_pair(k_prev, k_next)` — outer-product Hebbian into S such that S @ k_prev ≈ k_next. **NOT directly invariance** — this is transition PREDICTION, not similarity. Could be repurposed for Option C (see below) but the semantics are load-bearing-different.
- `hdlab/continual.py::replay_cycle` — periodic re-Hebbian of stored (k, v) pairs into W. Designed for consolidation against continual-write drift, NOT for temporal-contiguity training. Not directly usable.
- `hdlab/predictive_coding.py` (Spoke 1) — Rao-Ballard predict + Hebbian update. Provides the base weights Spoke 2 modifies.
- `hdlab/excitability.py` (Spoke 1) — Tonegawa excitability trace. **The trace mechanism is architecturally identical** to what Foldiak needs. Spoke 2 can extend excitability.py's trace or add a parallel "temporal-averaging trace" module.

Conclusion: no existing primitive IS the temporal-contiguity trainer, but `excitability.py`'s trace architecture is a compositional starting point.

## Candidate mechanisms (4 options)

### Option A — Foldiak trace rule (RECOMMENDED)

**Mechanism:** maintain a running exponential trace `t = alpha * h + (1-alpha) * t_prev` of each dimension's activation. Replace the Hebbian post-synaptic term with the trace: `dW ~ t · x^T` instead of `h · x^T`. Learning pulls representations toward what was recently active, so temporally-close inputs converge.

- **Local:** yes — trace is per-neuron running average; Hebbian update is outer product of trace and input.
- **Composes with Spoke 1:** yes — Spoke 1's competitive-allocation output feeds the trace; Spoke 1's predictive-coding Hebbian rule uses the trace as its post-synaptic factor instead of the instantaneous winner-take-all output.
- **Modifies Spoke 1 weights:** yes but MINIMALLY — one line of Spoke 1's Hebbian rule is changed (`h → trace(h)`). No new layer.
- **Historical support:** Foldiak 1991 for V1 complex cells; used in many downstream invariance-learning models.

**Weakness:** trace-length hyperparameter (alpha) sensitive. Too fast → no invariance; too slow → different concepts merge.

### Option B — SFA proper (Wiskott projection)

**Mechanism:** learn a projection P such that P @ h has minimum squared temporal derivative subject to unit variance and decorrelation across output dimensions. Solved as generalized eigenvalue problem in linear case; iterative online form exists (Kompella et al. 2012 incremental SFA).

- **Local:** partially — online SFA (Kompella IncSFA) is local-per-neuron Hebbian/anti-Hebbian but requires whitening step that isn't strictly Hebbian.
- **Composes with Spoke 1:** as a POST-PROCESSING LAYER on top of Spoke 1 output. Does NOT modify Spoke 1 weights. Adds an N×N projection matrix.
- **Historical support:** strong theoretical guarantees, provably extracts driving invariants.

**Weakness:** more machinery than Foldiak; whitening step is a wart on the "purely local Hebbian" story; and layered on top rather than integrated means Spoke 1's competitive allocation is downstream-invisible unless we re-allocate after projection.

### Option C — Adjacent-pair Hebbian anti-Hebbian

**Mechanism:** for adjacent inputs (h_t, h_{t+1}) apply Hebbian `dW ~ h_t · h_{t+1}^T`; for non-adjacent (h_t, h_{t+k}, k >> 1) apply anti-Hebbian `dW ~ -h_t · h_{t+k}^T`. Representations that co-fire near-in-time strengthen mutual similarity via the W matrix; non-adjacent pairs get repelled. `SequenceMatrix.bind_pair` is the direct primitive.

- **Local:** yes — outer product on pair of activations.
- **Composes with Spoke 1:** as a PARALLEL RECURRENT LAYER — Spoke 1 output h feeds an associative W that pulls h_t toward W @ h_{t-1} via a settling step before readout. Modifies READOUT, not Spoke 1 weights.
- **Historical support:** classic Hebbian pair-similarity mechanism; SequenceMatrix already CG'd (exp_c3 HARD_PASS 2026-06-22). Anti-Hebbian negative sampling is a known trick from word2vec era.

**Weakness:** requires negative sampling (choosing non-adjacent pairs) which is a design knob and can be badly-behaved. Pair-Hebbian without anti-Hebb collapses to constant vector.

### Option D — Predictive-coding temporal-slow prior (novel synthesis)

**Mechanism:** modify Spoke 1's predictive-coding layer to predict h_{t+1} from h_t (temporal prediction) INSTEAD OF / IN ADDITION TO predicting current input from higher-level. Residual = h_{t+1} - predict(h_t); Hebbian on residual. Temporally-slow features get accurate temporal prediction with small residual; fast-changing features generate large residual and get suppressed. Effectively an autoregressive predictive-coding cell.

- **Local:** yes — same PC rule, different target.
- **Composes with Spoke 1:** replaces or supplements Spoke 1's PC target. Requires holding h_t in a short buffer.
- **Historical support:** predictive-coding-in-time is well-studied (Rao 1999 dynamic PC; Deep Predictive Coding networks). Substrate has no such variant yet.

**Weakness:** conflates temporal prediction with SFA; may end up learning a transition model instead of an invariance representation. High parameter interaction with Spoke 1's spatial PC.

### Recommendation: Option A primary, Option C secondary arm, Option B/D deferred

Option A is the minimal-mechanism Foldiak trace — it is the historical winner for invariance from temporal contiguity, adds the fewest new components (one trace variable + one modified line in Spoke 1's Hebbian rule), and preserves the "purely local Hebbian" story. Option C tests the co-firing intuition and is CG'd as a primitive (SequenceMatrix); it's the natural composition-with-existing-substrate ablation. Option B is a stronger theoretical baseline but requires whitening (breaks Hebbian purity); defer to Spoke 2 v2 if v1 negative. Option D is a novel synthesis and holds too many degrees of freedom for a v1 discriminator.

## Cell design

**Anchor:** `exp_substrate_concept_encoder_spoke2_temporal_contiguity_foldiak_trace_v1`

**Prereq:** Spoke 1 CG (or MM). If Spoke 1 HARD_FAIL, Spoke 2 cell blocks until Spoke 1 rehab. Spoke 2 cell imports Spoke 1's `concept_encoder.py` and modifies its Hebbian post-synaptic factor.

### Arms (5 arms × 3 seeds = 15 units)

| Arm | Mechanism | Role |
|---|---|---|
| ARM_SPOKE1_ONLY | Spoke 1 without trace (baseline) | Control: no temporal contiguity |
| ARM_TRACE_FOLDIAK | Spoke 1 + Foldiak trace on Hebbian post-synaptic | LOAD-BEARING (Option A) |
| ARM_TRACE_ALPHA_FAST | Spoke 1 + trace with alpha=0.5 (nearly no smoothing) | Ablation: trace length matters |
| ARM_ADJACENT_PAIR_HEBB | Spoke 1 + Option C adjacent-pair Hebbian layer | Comparison mechanism |
| ARM_TRACE_SHUFFLE_CONTROL | Spoke 1 + Foldiak trace on TEMPORALLY-SHUFFLED stream | Sanity: proves temporal contiguity (not just trace filtering) is doing the work |

### Corpus (temporal-structure design)

**Smoke:** 50 concepts × 5 paraphrase variants each × 20 concept-repetitions per doc → 5000 sentences in a temporally-structured order where variants of the same concept appear in adjacent-sentence windows of size 3-5, then transition to next concept. Paraphrase variants for a concept synthesized by templated substitution (e.g. cat concept: "the cat sat on the mat" / "a feline rested on the rug" / "the kitty lay on the carpet" / ...). Ground truth: concept-identity label per sentence + temporal-window-index.

**FULL:** 10K sentences over 200 concepts with paraphrase-variant structure.

**Key discipline:** the SHUFFLE-CONTROL arm gets the SAME sentence set with random ordering. If it PASSES, the mechanism is doing bag-of-words filtering, NOT temporal-contiguity learning. If it FAILS while TRACE_FOLDIAK passes, temporal order is load-bearing.

### Metrics per arm × seed

- `sparse_rate`: Spoke 1 metric, must remain in [0.01, 0.03] band (invariant Spoke 2 does not destroy)
- `intra_concept_cos_across_variants`: mean cosine between HDs of variant-i and variant-j of the SAME concept (invariance measure; TARGET ≥ 0.6 for TRACE_FOLDIAK)
- `inter_concept_cos`: mean cosine between HDs of different concepts (separation; TARGET ≤ 0.1 for TRACE_FOLDIAK)
- `invariance_lift`: `intra_concept_cos_across_variants(TRACE_FOLDIAK) - intra_concept_cos_across_variants(SPOKE1_ONLY)` (headline number)
- `shuffle_gap`: `intra_concept_cos_across_variants(TRACE_FOLDIAK) - intra_concept_cos_across_variants(TRACE_SHUFFLE_CONTROL)` (proves temporal order is load-bearing)
- `arm_digest`: hash of concept-HD table

### HP bands (HP_SCOPE: LOAD-BEARING on ARM_TRACE_FOLDIAK)

**HARD_PASS (target CG):**
- ARM_TRACE_FOLDIAK intra_concept_cos_across_variants ≥ 0.6 (concept-variants become similar)
- ARM_TRACE_FOLDIAK inter_concept_cos ≤ 0.1 (still separates unrelated concepts)
- ARM_TRACE_FOLDIAK sparse_rate ∈ [0.01, 0.03] (Spoke 1 invariant preserved)
- ARM_TRACE_FOLDIAK invariance_lift ≥ +0.15 over ARM_SPOKE1_ONLY (Spoke 2 does real work)
- ARM_TRACE_FOLDIAK shuffle_gap ≥ +0.15 over ARM_TRACE_SHUFFLE_CONTROL (temporal order is load-bearing)
- ARM_TRACE_ALPHA_FAST intra_concept_cos_across_variants < ARM_TRACE_FOLDIAK - 0.10 (trace-length parameter is doing work)
- 3-seed HP; cv across seeds < 0.15

**HARD_FAIL:**
- ARM_TRACE_FOLDIAK intra_concept_cos_across_variants < 0.35 (invariance not achieved)
- OR ARM_TRACE_FOLDIAK inter_concept_cos > 0.30 (concept-separation destroyed — trace merged everything)
- OR ARM_TRACE_FOLDIAK sparse_rate outside [0.005, 0.10] (broke Spoke 1 architecture)
- OR shuffle_gap < +0.05 (mechanism is not using temporal contiguity — negative result on the whole thesis)

**MIDDLE_BAND:**
- Any target in intermediate range → v2 with alpha sweep, or Option B (SFA proper) as v2 mechanism, or Option C as v2 if trace approach fails.

### Sanity + integration gates

- ARM_SPOKE1_ONLY intra_concept_cos_across_variants approximately matches Spoke 1's v1 measurement on same corpus (regression sanity)
- ARM_TRACE_FOLDIAK inter_concept_cos NOT lower than ARM_SPOKE1_ONLY by more than 0.05 (separation preserved, not just intra-cluster inflation)
- Sparse rate constant across arms (or verify architecturally which arm is expected to shift and by how much)
- trace_alpha parameter monotonic — as alpha decreases (longer trace), intra_concept_cos_across_variants monotonically increases up to plateau

### Substrate primitives called

- All Spoke 1 primitives (hd_bind for char+position; predictive_coding; excitability trace for WTA)
- New: `hdlab/temporal_trace.py::TemporalTraceState` — running-average trace with configurable alpha; ~50 lines new
- Modified: Spoke 1's Hebbian post-synaptic factor accepts trace injection via injectable-callable (~20 lines Spoke 1 edit)
- ARM_ADJACENT_PAIR_HEBB uses existing `sequence_memory.py::SequenceMatrix.bind_pair` with settling-step readout
- No backprop, no gradient, no global error signal

### CELL-TEMPLATE MANDATORY compliance

Standard: arms_differ_verified (15 unique arm_digest), except SystemExit before except Exception, tmp_replace metrics, cardinality_ok, HP_SCOPE=LOAD_BEARING on TRACE_FOLDIAK, sparse-rate architectural constraint verified, shuffle-control gate explicit, ASCII-only.

### Compute architecture

- (a) batched-CPU-torch; corpus fits in memory; trace update is O(N) per sentence; Spoke 1 remains the bottleneck
- Per-seed smoke wall estimate: ~3-6 min (5000 sentences × Spoke 1 + trace)
- FULL wall: ~15-25 min (10K sentences × 200 concepts)
- Route: local_cpu smoke (USER SMOKE_ONLY_LOCAL); remote_cpu_queue for FULL

### Dispatch prereqs

1. Spoke 1 CG landed and extracted to hdlab (Spoke 2 imports from it)
2. `temporal_trace.py` authored + selftests passing
3. Cell file + prereg SCHEMA-VET (Skunkworks)
4. Smoke gate on local_cpu

## Composability picture (Spoke 1 + Spoke 2 composed)

```
raw text ("the cat sat on the mat")
    |
    v
[char + positional encoder]           <-- Spoke 1
    | word HDs bound with position
    v
[predictive coding Hebbian]           <-- Spoke 1
    | with post-synaptic factor now = trace(h) not h
    |     ^
    |     |
    |     [temporal trace running avg]  <-- Spoke 2 NEW (Option A)
    |     |
    v     |
[competitive allocation WTA]           <-- Spoke 1
    | sparse concept HD (bipolar)
    v
concept HD (temporally-invariant)
```

**Concrete change to Spoke 1:** the Hebbian update rule inside the PC block becomes `dW = eta * trace(post) @ pre^T` instead of `dW = eta * post @ pre^T`. Trace is a per-dim exponential moving average with alpha ~ 0.1 (i.e., ~10 sentences of memory). Trace state is per-input-stream — resets at document boundaries.

**Spoke 2 does modify Spoke 1 weights** (via the modified Hebbian rule) but does NOT add a second layer or output stage. This is the minimal-mechanism interpretation of Foldiak's original construction.

**Alternative interpretation (fallback if Option A negative):** Option C makes Spoke 2 a POST-PROCESSING layer — Spoke 1 output h is settled via `h_out = normalize(h + gamma * W_pair @ h_prev)` before readout. This is a two-layer story; keeps Spoke 1 pristine but at cost of more parameters.

## P_CG estimate + calibration reasoning

**Pre-deflation P_CG:** ~0.55 based on lit support:
- Foldiak trace rule + SFA are well-established mechanisms for temporal-contiguity invariance (V1, IT, place cells all have SFA-consistent representations).
- Substrate has all supporting primitives; only additive component (trace) is new.
- Composability with Spoke 1 is clean (one Hebbian line modified).

**Deflations (lit-scan calibration penalty, USER-locked cap novel-synthesis at 0.50):**
- **-0.10** for novel-synthesis (trace + WTA + PC composition not been done in HD substrate literature that I've located; hitting the 0.50 cap)
- **-0.05** for text-corpus SFA is weaker signal than vision-stream SFA (text sentence-adjacency has weaker temporal-contiguity signal than 30fps vision frames; a sentence and its paraphrase in a synthetic corpus is stronger, but real-world sentence adjacency may not be)
- **-0.05** for Spoke 2 depends on Spoke 1 CG (conditional P; if Spoke 1 MIDDLE_BAND or FAIL, Spoke 2 mechanism can't be cleanly evaluated on top)
- **-0.05** for hyperparameter sensitivity of trace alpha (Foldiak literature notes strong parameter sensitivity)

**Post-deflation P_CG: ≈ 0.35 (conditional on Spoke 1 CG or high-quality MM)**

If Spoke 1 HARD_FAIL, Spoke 2 P_CG drops to ~0.10 (mechanism can't be cleanly evaluated on random-codebook baseline).

## Post-verdict routing

**HARD_PASS:** Spoke 2 CG. Extract `temporal_trace.py` + modified concept_encoder to hdlab. Fire Spoke 3 (continual updateability + one-shot learning) and Spoke 4 (grounding) design work.

**HARD_FAIL:** file CG_HONEST_NEGATIVE closing Foldiak-trace-on-Spoke1 composition. Options for v2: (i) Option B (SFA proper with whitening), (ii) Option C (adjacent-pair Hebbian post-processing), (iii) Option D (temporal predictive coding). 2x-research drill on why text-adjacency signal was too weak.

**MIDDLE_BAND:** file MM_TENTATIVE; v2 = trace-alpha sweep + Option C parallel arm. Or v2 uses a stronger temporal-contiguity signal — same-doc paragraph pairs, or same-conversation utterance pairs, rather than adjacent-sentence in synthetic paraphrase corpus.

## What CG at Spoke 2 unlocks

Substrate concept HDs become **invariant** to paraphrase — "the cat sat on the mat" and "the kitty lay on the carpet" produce concept HDs with cosine ≥ 0.6 not because they share surface tokens (they don't) but because they were temporally adjacent in the training stream and the substrate learned "these are the same underlying concept". This closes Six-brain-property #5 partially (grounded-via-temporal-contiguity is a weaker form of grounding than sensorimotor, but it's the mechanism the ventral stream uses too).

Combined Spoke 1 + Spoke 2 covers 5 of 6 brain-property criteria:
- (1) Emerged from data ✅ (Spoke 1)
- (2) Sparse-distributed ✅ (Spoke 1)
- (3) Predictive ✅ (Spoke 1)
- (4) Compositional ✅ (Spoke 1 HRR bind)
- (5) Grounded — partial ✅ via temporal-contiguity invariance (Spoke 2)
- (6) Continually updateable — Spoke 3 target

USER's Stage 2 substrate-load ritual gets INVARIANCE — "storage strategy" query hits SHARDED atom regardless of which of 3 paraphrasings USER wrote it, because paraphrases produced similar concept HDs during ingest.
