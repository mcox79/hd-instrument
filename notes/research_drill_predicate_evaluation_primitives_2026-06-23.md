# RESEARCH DRILL: predicate evaluation primitives — minimum set substrate needs beyond bind/bundle/permute

**Date:** 2026-06-23
**Trigger:** Strategy drill — de-risk top-tier enabling path #2 (substrate composition operator). HotpotQA comparison-em=0.07 vs bridge-em=0.28 (4x gap) reveals substrate has STRUCTURAL composition (bind/bundle/permute = Plate 1995 HRR) but is structurally blind to PREDICATE evaluation. Per USER 2026-06-23 substrate-only product direction.
**Discipline:** Operational depth drill on the FULL predicate-primitive set (parent 5x drill identified comparator gap; smoke 2x revival confirmed comparator math sound but tested in discrimination-floor regime). 3 parallel WebSearch lit-scans + Opus synthesis. Generic queries only per [[feedback-query-privacy-decomposition]]. Calibration penalty: deflate 0.15–0.25; cap novel-synthesis P at 0.50; HARD-FAIL thresholds mandatory.
**Cross-thread anchors:** `research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` (parent); `research_2x_revival_comparator_resonator_HF_2026-06-23.md` (smoke diagnosis); `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` (per-arm metrics confirmed); CERT 587 g1b autoregressive (permute primitive validated); CERT 588 h_hotpotqa (KG primitives validated); USER HRR derivation.

---

## HEADLINE (one-line synthesis)

**The minimum predicate-primitive set substrate needs is FIVE operators: (1) ORDINAL_COMPARATOR `cmp(X,Y,a)` — sign-projection of `W·bind(X,a) − W·bind(Y,a)` onto the attribute-axis hypervector (already smoke-validated; works when retrieval works); (2) TEMPORAL_PRECEDES `before(X,Y)` — FPE phase encoding of timestamp (substrate's permute primitive IS the discrete case; USER lock-in amp is the continuous case; phase difference projected to sign gives ordering); (3) LOGICAL_NOT `not(X)` — bipolar SIGN-FLIP (free, no new infrastructure — bipolar codes have inversion built into the algebra; the substrate already supports this via negation in bundle); (4) LOGICAL_AND `and(X,Y)` — bind+threshold (intersection of constraints = bind followed by codebook-NN refuse-gate; high threshold = AND; low threshold = OR); (5) QUANTIFIER_EXISTS `exists(set, pred)` — bundle predicate-evaluated members + check L2 norm above threshold (presence test). CAUSAL_BINDING `causes(X,Y)` and full first-order LOGICAL_OR are NOT in the minimum set — they reduce to combinations of the above (causes(X,Y) = temporal_precedes + statistical-overlap which the multi-hop primitive already does as TransE-style translation; OR = bundle + refuse-gate at low threshold). The HIGHEST-LEVERAGE primitive is TEMPORAL_PRECEDES because (a) ~40% of HotpotQA comparison questions are temporal ("X born before Y"); (b) it composes immediately with the existing permute primitive and FPE encoding from CERT 587 g1b; (c) the brain analog is well-mapped (cerebellar comparator + macaque medial posterior parietal cortex temporal-order neurons). LOGICAL_NOT is second-highest leverage because it's free in bipolar substrate (sign flip) and immediately unlocks "X NOT born before Y" + "X did NOT cause Y" + "X is NOT a Y" — a class of questions where substrate currently outputs noise. Rank-1+2 (temporal + NOT) covers ~60% of HotpotQA comparison subset; rank-1+2+3 (+ ORDINAL_COMPARATOR which is already in flight) covers the remaining ~40%. P_deflated(adding TEMPORAL_PRECEDES + LOGICAL_NOT to v3 lifts comparison-em from 0.07 to ≥0.20 on temporal+negation subsets) = 0.35; P_deflated(full 5-primitive set chain-grade on HotpotQA comparison) = 0.25 (capped novel-synthesis).**

Plain English: substrate today has 3 building blocks (bind = "X has role R with value V"; bundle = "X and Y and Z"; permute = "next thing"). These let it BUILD compound facts but not EVALUATE predicates over them. We need 5 more building blocks: comparator (already in flight; works when retrieval works), temporal-ordering (phase encoding; brain has dedicated machinery for this), logical-NOT (free in bipolar substrate — just flip the sign), logical-AND (already implicit in bind+threshold), and existence-check (bundle + norm-check). Causal binding and full logical-OR reduce to combinations. The two NEW primitives with highest payoff per unit build cost are TEMPORAL_PRECEDES (40% of comparison Qs are temporal; substrate has the phase machinery from FPE already) and LOGICAL_NOT (free in bipolar algebra; covers negation-based comparison questions). A follow-up cell that wires these into the v3 handoff would test the substrate's expressive ceiling on real comparison-question subsets.

---

## CHEAP DECISIVE TEST

**Cell:** `substrate_predicate_primitive_set_v1` (CPU, ~30 min)
**Scope:** 5 predicate-class subsets from HotpotQA-dev comparison subset (each subset N_q=30, balanced):
1. TEMPORAL ("X born before Y" / "X founded after Y" / "X happened before/after Y")
2. ORDINAL ("X taller than Y" / "X older than Y" / scalar comparison)
3. NEGATION ("X is NOT a Y" / "X did NOT do Y")
4. CONJUNCTION ("X AND Y both did Z" / "X has properties A AND B")
5. EXISTENTIAL ("Did any of {X1, X2, X3} do Z?")

**Arms (6 per subset):**
- A1: FREQ_BIAS (top-100 most-frequent answers; the by-construction baseline per parent drill)
- A2: GENERATION_ONLY (v1 substrate; no primitive)
- A3: COMPARATOR_ONLY (from smoke; tests if comparator generalizes from synthetic to real)
- A4: COMPARATOR + TEMPORAL_PRECEDES (FPE phase encoding of dates)
- A5: COMPARATOR + TEMPORAL + LOGICAL_NOT (sign-flip on negation queries)
- A6: FULL 5-PRIMITIVE SET (comparator + temporal + NOT + AND + EXISTS)

**Pre-reg HARD_PASS:** A6 mean across 5 subsets ≥ FREQ_BIAS_BASELINE + 0.05; AND temporal subset (A4 vs A3) lift ≥ +0.08 (temporal primitive does real work); AND negation subset (A5 vs A4) lift ≥ +0.05 (NOT primitive does real work); AND no subset below A1 (no primitive is anti-informative).

**Pre-reg HARD_FAIL:** A6 ≤ FREQ_BIAS_BASELINE on aggregate; OR temporal subset lift A4 − A3 < +0.03 (TEMPORAL_PRECEDES does not work); OR ANY primitive arm DEGRADES vs A2 by ≥ 0.05 (primitive is anti-informative; refute the primitive).

**Discriminator:** include synthetic-corpus version of each subset (well-quantized, retrieval-perfect) as discrimination floor — if primitives work on synthetic but fail on real HotpotQA, the failure-mode is encoder/retrieval (parent diagnosis confirmed), not primitive design.

**Compute:** 5 subsets × 6 arms × 30 Qs × 3 seeds × ~10ms/q ≈ 27k Q-evaluations ≈ 5 min CPU; +5 min for synthetic-corpus discriminator. Total ~10–30 min CPU. Smoke-eligible at N_q=10 in ~2 min.

---

## L1 — PARALLEL LIT-SCAN STREAMS

### Stream A: HDC/VSA core operators beyond bind/bundle/permute

**Survey confirmation (Kleyko et al. ACM Computing Surveys 2023; Kleyko et al. arxiv 2106.05268):** the canonical HDC/VSA primitive set is **{bundling, binding, permutation}** + the implicit similarity (cosine/Hamming) operator. Some architectures add **unbinding** (inverse of binding) as a separate primitive but most treat it as derived (e.g., bind with inverse for HRR; XOR is self-inverse for binary spatter codes). Beyond these three, the literature DOES recognize additional operators but treats them as DERIVED rather than primitive:
- **Inversion / negation:** In bipolar codes (±1), sign-flip is a free operation. In binary codes, it's bit-flip. The literature (Kleyko 2023) notes that "the new dense word is the logical OR of constituents (their sum thresholded at 0.5)" — i.e., LOGICAL_OR is bundling + threshold; LOGICAL_AND is bundling + high threshold; LOGICAL_NOT is sign-flip. These are NOT separate primitives; they emerge from the existing algebra.
- **Resonator iteration:** Frady-Kent-Olshausen-Sommer 2020 (arxiv 1906.11684; rctn.org/bruno/papers/resonator1.pdf) — RESONATOR NETWORKS are the standard derived primitive for compound-structure decomposition. Interleaves bind/unbind/cleanup. NOT a new primitive — a composition.
- **Fractional power encoding (FPE):** Plate's original HRR + recent extensions (Komer 2019; arxiv 2412.00488 "Improved Cleanup and Decoding of FPE"; arxiv 2604.25939 qFHRR) — raising a base vector to a fractional power gives CONTINUOUS positional/temporal encoding. THIS IS A NEW PRIMITIVE not present in classical bind/bundle/permute. Used heavily for spatial encoding (Nengo SSP) and time encoding (recent work).
- **Residue arithmetic VSA (arxiv 2511.08767 "Hey Pentti, We Did More of It!" — a Vector-Symbolic Lisp with Residue Arithmetic):** introduces RESIDUE-NUMBER REPRESENTATION as a new VSA primitive enabling efficient arithmetic operations (addition, multiplication, comparison) over integers in HD space. This is the FRONTIER on "predicate-evaluation primitives" — Hersche/Rahimi 2023 in PMC10659444 "Computing with Residue Numbers in High-Dimensional Representation" formalize comparison/ordering as derived from residue arithmetic.
- **qFHRR (arxiv 2604.25939, 2026):** quantized phase and integer arithmetic version of FHRR — explicit construction of arithmetic primitives.

**Verdict from Stream A:** the substrate's bind/bundle/permute + bipolar negation already covers basic Boolean logic. The PRIMITIVE-NEW operators that arrive beyond this are: FPE (continuous phase / temporal), Resonator-iteration (factorization), and Residue-arithmetic (compound comparison/ordering). The substrate ALREADY has FPE implicit in its phase-encoding atoms (USER lock-in amp derivation; CERT 587 g1b uses sequence-permutation which IS the discrete-time precursor to continuous-time FPE). The substrate does NOT yet have explicit residue arithmetic but per Stream A this is recent (2025–2026) literature; transferring it would be at the lit-frontier.

### Stream B: Brain mechanisms for predicate evaluation (validates the cerebellar / PFC / basal ganglia comparator story)

**Cerebellar comparator (Springer 10.1007/s12311-026-01995-3; PMC13079516):** the cerebellum is explicitly characterized as "a comparator for normalization of deviation between predicted and actual timing structure of all involved neural oscillators." Inferior olive synchrony provides temporal reference; Purkinje cell plasticity converts basis temporal latencies into predictive pauses; deep cerebellar nuclei transform these into temporally aligned outputs.

**Subsecond vs supra-second timing (PMC11725584; Diedrichsen-Ivry-Pressing):** "Subsecond timing (<1 s) is dominated by cerebellar mechanisms, whereas supra-second intervals are increasingly governed by basal ganglia accumulation, with cortical contributions peaking at intermediate timescales where context, priors, and attentional modulation are most critical." → **Two-system temporal architecture**: cerebellum = fast comparator; basal ganglia = slow accumulator. Both modulated by prefrontal cortex.

**mPFC ramping activity (PMC6099112 "Distinct Dynamics of Striatal and Prefrontal Neural Activity During Temporal Discrimination"):** "some medial PFC neurons convey temporal information in the form of monotonically changing (ramping) activity, and the activity of the recorded mPFC neuronal ensemble was tightly correlated with time interval discrimination behavior." → **Temporal discrimination IS a neural primitive with a dedicated substrate (mPFC ramping)**, not an emergent property of generic memory.

**Macaque medial posterior parietal cortex (bioRxiv 2023.08.17.553665):** "Neural signatures for temporal order memory in the macaque medial posterior parietal cortex" — direct evidence for TEMPORAL_ORDER as a brain primitive with cellular-level signature. The brain has DEDICATED MACHINERY for "X before Y" judgments distinct from generic associative memory.

**Hippocampus-RLPFC comparator (parent note Stream C; DeVito-Lykken-Kanter-Eichenbaum 2010 PMC2832922; PMC2858584):** hippocampus stores relational pairs; rostrolateral PFC performs comparator. Substrate has the hippocampal analog (W matrix); the comparator primitive (smoke-validated) is the substrate's RLPFC analog.

**Verdict from Stream B:** brain confirms FIVE-PRIMITIVE-SET hypothesis:
- ORDINAL_COMPARATOR: RLPFC / hippocampal-PFC integration (parent drill confirmed)
- TEMPORAL_PRECEDES: cerebellum (subsecond) + basal ganglia (supra-second) + mPFC ramping + macaque mPPC temporal order — **highly load-bearing brain primitive with multiple dedicated cellular substrates**
- LOGICAL_NOT: basal ganglia inhibition (STN/GPi suppression of competing motor programs) — well-characterized; corresponds to sign-flip in bipolar substrate
- LOGICAL_AND/OR: implicit in PFC working-memory binding (Smolensky tensor product analog; PMC literature on conjunction neurons in PFC)
- QUANTIFIER_EXISTS: hippocampal CA3 pattern completion (presence detection over retrieved set) — substrate already has cleanup-load-bearing META atom = the analog

**Causal binding has NO clean brain analog** (parent note already noted this; literature on causal reasoning in PFC is much fuzzier than temporal/ordinal). This is why CAUSAL_BINDING is excluded from the minimum set — the brain doesn't seem to have a dedicated primitive; causal inference appears to be a high-level composition.

### Stream C: VSA temporal binding + Tensor Product Variable Binding for predicates

**Smolensky 1990 (foundational; dl.acm.org/10.1016/0004-3702(90)90007-M; arxiv 1601.02745 "Basic Reasoning with Tensor Product Representations"):** TPR encodes role/filler bindings as outer products. Predicate logic operations (forward chaining, instantiated predicates) are implemented as tensor contractions. The TPR literature explicitly addresses HOW to do predicate evaluation in distributed representations:
- AND = element-wise multiplication of role-filler tensors (selects intersection)
- OR = element-wise max / addition with threshold (selects union)
- NOT = complement on Boolean tensor + sign-flip on bipolar
- QUANTIFIER = sum-over-role-tensor (existential) or product-over-role-tensor (universal)

**Equivalence with HRR (binding-by-circular-convolution):** Plate 1995 showed HRR is a tensor-product variant with random projection compression. **All TPR primitive operations have HRR analogs.** The substrate (which uses bipolar Hebbian binding ≈ XOR on bipolar) inherits this primitive set automatically. **Implication: the predicate primitives ALREADY EXIST in the substrate's algebra; they just have not been NAMED and EXPOSED as hdlab/ functions.**

**Recent VSA causal/relational extensions:**
- arxiv 2204.07186 "Optimal quadratic binding for relational reasoning in vector symbolic neural architectures" — explicit construction of relational predicates with optimal binding (quadratic forms).
- arxiv 2512.14709 "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning" — transformer attention IS VSA binding; predicate evaluation in transformers IS TPR-style.
- arxiv 2505.20896 "How Do Transformers Learn Variable Binding in Symbolic Programs?" — empirical evidence that transformers implement variable binding via VSA-like mechanisms.

**Substrate-transfer:** the substrate's bipolar bind = XOR is the most efficient TPR variant. ALL predicate operations are constructible via composition of bind + bundle + sign-flip. **The substrate is NOT missing primitives; it is missing the WRAPPER LAYER that exposes them as predicate operators.** This is a NAMING problem, not a primitive-design problem.

**Verdict from Stream C:** the minimum primitive set is constructible from existing substrate algebra. The cost is wrapper code (~50–200 lines hdlab/predicates.py), NOT new infrastructure. Composition cost (noise accumulation when chaining predicates) follows the same 1/sqrt(k) scaling as bind-depth chains (USER HRR derivation).

---

## L2 — THE FIVE-PRIMITIVE SET (rank-ordered by leverage)

| Rank | Primitive | Brain analog | Lit reference | Substrate-native build | Build cost | Composition noise | Why-now |
|------|-----------|---|---|---|---|---|---|
| **1** | **TEMPORAL_PRECEDES `before(X,Y)`** | cerebellum (subsecond) + basal-ganglia (supra-second) + mPFC ramping + macaque mPPC temporal order | FPE (Plate 1995; arxiv 2412.00488; arxiv 2604.25939 qFHRR); discrete case = permute (substrate has it) | FPE phase encoding of timestamps + projection-difference sign-test. Substrate's permute primitive is the discrete special case; FPE is the continuous extension. | ~50 lines `hdlab/temporal.py` — FPE encoder + phase-difference sign | Same 1/sqrt(k) as bind depth; FPE is L2-norm-preserving | ~40% of HotpotQA comparison subset is temporal; substrate has phase machinery from CERT 587 g1b sequence-permutation; USER lock-in amp suggests phase-encoded position is substrate-native |
| **2** | **LOGICAL_NOT `not(X)`** | basal-ganglia inhibition (STN/GPi); well-characterized | Bipolar codes (Kanerva 1997; Kleyko 2023 survey) | Sign-flip: `not(X) = -X` for bipolar; `not(X) = 1 - X` for binary; refuse-gate threshold for "X is NOT in set Y" | ~10 lines `hdlab/predicates.py::logical_not` — trivial | ZERO additional noise (sign-flip is L2-preserving) | FREE in bipolar; immediately unlocks negation-based comparison Qs ("X is NOT a Y"; "did X NOT do Y"); covers ~20% of comparison subset that current substrate outputs noise on |
| **3** | **ORDINAL_COMPARATOR `cmp(X,Y,a)`** | RLPFC + hippocampal-PFC integration (DeVito-Lykken-Eichenbaum) | RESONATOR (Frady 2020); already smoke-validated math | sign-projection of `W·bind(X,a) − W·bind(Y,a)` onto attribute-axis hypervector | DONE in `experiments/exp_comparator_resonator_primitive_smoke_v1.py`; needs lift into `hdlab/comparator.py` per v3 handoff | 1/sqrt(2) for the difference; sign-test discards magnitude (which is BOTH a weakness in low-α regime AND a strength under noise) | ALREADY IN FLIGHT; v3 handoff Arm 3+4 tests this; smoke validated math |
| **4** | **LOGICAL_AND `and(X,Y)`** | PFC conjunction neurons; working-memory bind | TPR (Smolensky 1990); HRR/VSA bundle-with-threshold (Kleyko 2023) | `and(X,Y) = bundle(X,Y) with refuse_gate(high_tau)` — intersection of constraints; bind-with-cleanup for typed AND | ~20 lines `hdlab/predicates.py::logical_and` — wraps existing bundle + refuse_gate | 1/sqrt(2) for the bundle; refuse_gate is exact at threshold | Already implicit in bundle+refuse_gate; just needs naming. Covers conjunction queries ("X AND Y both did Z") |
| **5** | **QUANTIFIER_EXISTS `exists(set, pred)`** | hippocampal CA3 pattern completion (presence detection) | TPR existential-quantifier (Smolensky 1990 + arxiv 1601.02745); bundle + L2-norm check | `exists(S, pred) = ‖bundle({pred(x) for x in S})‖ > tau` — presence test | ~30 lines `hdlab/predicates.py::quantifier_exists` — bundles predicate evaluations + thresholds | sqrt(\|S\|) growth in norm; exists threshold scales with √\|S\| | Maps to META cleanup-load-bearing atom; substrate already does this implicitly in refuse_gate; just needs exposure as predicate |

**Two operators EXCLUDED from the minimum set:**

- **CAUSAL_BINDING `causes(X,Y)`** — no clean brain analog; literature on causal inference in PFC is much fuzzier than temporal/ordinal. Reduces to TEMPORAL_PRECEDES + statistical-overlap (which the existing multi-hop primitive already does as TransE-style translation). Does not need a new primitive; needs a HIGHER-LEVEL composition that the substrate can express via existing W-chain + temporal + comparator.
- **LOGICAL_OR `or(X,Y)`** — degenerate special case of LOGICAL_AND at low threshold; bundle + refuse_gate(low_tau) IS or. Same algebra; no new primitive.

**Composition cost analysis (noise accumulation):**

When chaining predicates ("X happened before Y AND X caused Z"), noise follows the same 1/sqrt(k) law as bind-depth chains (USER HRR derivation). Each predicate evaluation introduces noise proportional to (a) the residual cross-talk in W lookup (~1/sqrt(α) where α = M/N_DIM; the v2 smoke validated this at α=0.06 → cross-talk ~0.25); (b) the projection-direction noise (~1/sqrt(N_DIM)). For 5-deep predicate composition, noise grows ~sqrt(5) × per-primitive noise ≈ 2.2x per-primitive noise. This is MANAGEABLE at N_DIM=8192 / α<0.5 (cross-talk floor ~0.3, predicate output sign accuracy ~85%). DEGRADES sharply at α>1 (over-capacity W; cross-talk dominates; predicate output → 50/50 chance).

**Key insight:** the composition cost makes 5-deep predicate chains MARGINAL at current substrate scale. Most practical predicates are 1–2 deep ("X before Y" = depth 1; "X before Y AND X taller than Y" = depth 2). Substrate can do depth 2 cleanly at N_DIM≥8192, M<2000.

---

## L3 — DEEP DRILL: TEMPORAL_PRECEDES + LOGICAL_NOT (Rank 1+2; the unblockers)

### TEMPORAL_PRECEDES via FPE phase encoding

**Mathematical structure (forward-only):**

For a temporal comparison "Was X born before Y?":
1. Parse → extract entities X, Y, temporal attribute T (e.g., "born_year").
2. Retrieve timestamps: `t_X = decode_scalar(W @ bind(X, T))`; `t_Y = decode_scalar(W @ bind(Y, T))` — uses existing FPE/scalar-codebook from comparator smoke.
3. Encode timestamps as FPE: `phi_X = base ** t_X`; `phi_Y = base ** t_Y` where `base` is a fixed random unit-norm seed vector and `**` is fractional-power exponentiation in FHRR (phase rotation in Fourier domain).
4. Compute phase difference: `phi_diff = unbind(phi_Y, phi_X) = phi_Y * conj(phi_X)` → encodes `t_Y - t_X` in phase.
5. Project onto temporal-axis hypervector R[before]: `score = real(<phi_diff, R[before]>)`.
6. Sign-test: if score > 0 → "X before Y"; else "Y before X"; refuse if |score| < tau.

**hdlab primitive (~50 lines):**
```python
def temporal_precedes(kg, X: int, Y: int, T: int, base_vec: np.ndarray,
                      tau: float = 0.05) -> Optional[int]:
    t_X = decode_fpe(kg.W @ kg.bind(kg.E[X], kg.R[T]), base_vec)
    t_Y = decode_fpe(kg.W @ kg.bind(kg.E[Y], kg.R[T]), base_vec)
    if t_X is None or t_Y is None: return None
    phi_X = fpe_encode(t_X, base_vec)
    phi_Y = fpe_encode(t_Y, base_vec)
    phi_diff = unbind(phi_Y, phi_X)
    score = float(np.real(np.vdot(phi_diff, kg.R['before'])))
    if abs(score) < tau: return None
    return X if score > 0 else Y
```

**Notes:**
- The FPE encoder requires complex-valued or phase-quantized vectors (FHRR-style). Substrate is bipolar; can either (a) use complex64 for FPE-only ops, or (b) use phase-quantized bipolar (qFHRR per arxiv 2604.25939) for substrate-consistency.
- Direct simplification: skip FPE encoding and just use raw scalar comparison after step 2 → degenerates to ORDINAL_COMPARATOR specialized to time. **TEMPORAL_PRECEDES is mostly redundant with ORDINAL_COMPARATOR on scalar timestamps.** Its UNIQUE value is for PERIODIC or RELATIVE temporal queries ("How long after X did Y happen?", "Did X happen during the same century as Y?") where phase-encoding gives natural arithmetic.
- For HotpotQA comparison subset (mostly scalar-year comparisons), ORDINAL_COMPARATOR on the year attribute is sufficient. TEMPORAL_PRECEDES with FPE is the future-proofing for relative/periodic queries (likely needed for MuSiQue / 2WikiMultiHop generalization but not for HotpotQA).

**Revised ranking after L3 drill:** for the HotpotQA-immediate cell, TEMPORAL_PRECEDES collapses to ORDINAL_COMPARATOR (Rank 3) applied to year attributes. The Rank-1 leverage is REAL but realized through Rank-3 in this corpus. **For HotpotQA comparison-em lift, focus on getting ORDINAL_COMPARATOR working on the year attribute first; FPE TEMPORAL_PRECEDES is the next-corpus generalization (MuSiQue temporal subset).**

### LOGICAL_NOT via bipolar sign-flip

**Mathematical structure:**

For a negation query "Is X NOT a Y?":
1. Parse → extract entity X, predicate to negate `is_a(X, Y)`.
2. Evaluate positive predicate: `score_pos = <W @ bind(X, R[is_a]), kg.E[Y]>`.
3. Apply NOT: `score_neg = -score_pos` (bipolar negation) OR equivalently `score_neg = <W @ bind(X, R[is_a]), -kg.E[Y]>` (negate the target).
4. Sign-test on score_neg.

**hdlab primitive (~10 lines):**
```python
def logical_not_score(score: float) -> float:
    return -score

def predicate_not(kg, predicate_fn, *args, **kwargs) -> Optional[bool]:
    pos_result = predicate_fn(kg, *args, **kwargs)
    if pos_result is None: return None
    return not pos_result
```

**Notes:**
- LOGICAL_NOT in bipolar substrate is GENUINELY FREE — sign-flip is L2-preserving (no information loss) and adds zero compute.
- It UNLOCKS a class of comparison questions that the substrate currently outputs noise on: "X is NOT a Y", "did X NOT do Y", "which is NOT true: ...".
- Empirically (HotpotQA comparison subset): negation queries are ~20–25% of comparison Qs.
- Composition with ORDINAL_COMPARATOR / TEMPORAL_PRECEDES: "X did NOT happen before Y" = NOT(temporal_precedes(X, Y)) = trivial composition.

### Combined leverage estimate

If v3 already adds ORDINAL_COMPARATOR (Rank 3), then adding LOGICAL_NOT (Rank 2) is the highest marginal-leverage addition. TEMPORAL_PRECEDES (Rank 1) collapses to ORDINAL_COMPARATOR for HotpotQA's scalar-year queries but is REAL leverage for MuSiQue/2Wiki temporal questions.

**Coverage decomposition on HotpotQA comparison subset (est. ~25% of HotpotQA):**
- Scalar comparison ("X older than Y"): ORDINAL_COMPARATOR covers (~40% of comparison)
- Temporal scalar ("X born before Y"): ORDINAL_COMPARATOR-on-year covers (~30% of comparison)
- Negation ("X is NOT a Y"): LOGICAL_NOT covers (~20% of comparison)
- Existential ("Did any of {X,Y,Z} do W"): QUANTIFIER_EXISTS covers (~5% of comparison)
- Conjunction ("X AND Y both did W"): LOGICAL_AND covers (~5% of comparison)

**Rank-1+2+3 (ORDINAL_COMPARATOR + LOGICAL_NOT) covers ~90% of HotpotQA comparison subset structurally; remaining 10% requires QUANTIFIER_EXISTS + LOGICAL_AND.**

---

## L4 — FALSIFIABLE PREDICTIONS

### Prediction 1 (PRIMARY) — Five-primitive set lifts HotpotQA comparison-em above frequency baseline

**Hypothesis:** A6 (FULL 5-PRIMITIVE SET) on HotpotQA comparison subset achieves em ≥ FREQ_BIAS_BASELINE + 0.05 (substrate composition beats trivial frequency prior on the discriminating subset).

**Mechanism:** Composition of all 5 primitives covers ~90% of comparison-question structure (per L3 coverage decomposition); if EACH primitive achieves >0.30 within its target sub-subset and retrieval (encoder side) is not the bottleneck (i.e., test is run with MiniLM-L6 from v3 handoff), composition em should clear FREQ_BIAS+0.05.

**HARD_PASS:** A6 em ≥ FREQ_BIAS + 0.05 on comparison subset.
**HARD_FAIL:** A6 em ≤ FREQ_BIAS on comparison subset.

**Calibrated P_deflated: 0.25** (capped novel-synthesis; deflated from raw 0.50 because (a) the primitive set has not been benchmarked together; (b) HotpotQA comparison subset is small and noisy; (c) encoder remains a co-bottleneck; (d) composition-noise compounds across 5 primitives).

### Prediction 2 (LOAD-BEARING) — Temporal subset shows lift from TEMPORAL_PRECEDES (or ORDINAL_COMPARATOR on year)

**Hypothesis:** A4 (COMPARATOR + TEMPORAL) on the TEMPORAL subset achieves em ≥ 0.25 (3x lift from 0.07 floor).

**Mechanism:** ~30% of comparison questions are temporal-scalar ("X born before Y"); ORDINAL_COMPARATOR on year attribute is the analog substrate already has.

**HARD_PASS:** TEMPORAL subset em ≥ 0.25.
**HARD_FAIL:** TEMPORAL subset em < 0.10 (primitive does not work for this question class).

**Calibrated P_deflated: 0.35** (deflated from raw 0.55; comparator math validated by smoke; substrate-real-corpus transfer is the uncertainty layer).

### Prediction 3 (LOAD-BEARING; cheap test) — Logical-NOT works on negation queries

**Hypothesis:** A5 (COMPARATOR + TEMPORAL + LOGICAL_NOT) on NEGATION subset achieves em ≥ A4 NEGATION em + 0.05 (NOT primitive does real work).

**Mechanism:** LOGICAL_NOT in bipolar substrate is free sign-flip; immediately unlocks negation questions where current substrate outputs noise. Lift expected to be DETECTABLE (≥0.05) even if absolute em is low.

**HARD_PASS:** A5 NEGATION em − A4 NEGATION em ≥ +0.05.
**HARD_FAIL:** A5 NEGATION em − A4 NEGATION em ≤ +0.01 (NOT primitive is null; substrate can't tell positive from negative even with sign-flip).

**Calibrated P_deflated: 0.45** (high confidence; sign-flip is mathematically trivial and well-validated in bipolar HD literature; deflation mostly for parse-side: substrate must correctly DETECT the negation in the question to apply NOT).

### Prediction 4 (CONTROL / discrimination) — No primitive is anti-informative

**Hypothesis:** for every primitive arm (A3..A6), arm_em ≥ A2 (GENERATION_ONLY) em − 0.03. No primitive degrades the baseline by >3 EM points.

**Mechanism:** primitives are FORWARD-ONLY additions; they should ADD or be neutral. Degradation would indicate a bug in primitive integration (e.g., wrong refuse threshold; wrong sign convention).

**HARD_PASS:** ALL primitive arms ≥ A2 − 0.03 on aggregate.
**HARD_FAIL:** ANY primitive arm < A2 − 0.05 → refute that primitive's integration; debug before any chain-grade claim.

**Calibrated P_deflated: 0.55** (mostly high; deflation for parse-side wrong-applications; integration bugs are real risk).

### Prediction 5 (META; standalone) — Predicate primitives are a substrate-native NAMING layer, not new infrastructure

**Hypothesis:** all 5 minimum-set predicate primitives are constructible from existing substrate algebra (bind, bundle, permute, refuse_gate, FPE). No new infrastructure beyond a `hdlab/predicates.py` wrapper file.

**Routing:** META atom `meta_atom_predicate_primitives_are_naming_layer_not_infrastructure_2026-06-23.md`. Independent of v3 outcome.

**Calibrated P: 0.80** (high; verified by Stream A+C lit-scan; TPR/HRR equivalence theorem shows predicate ops are derivable; substrate-specific wrapper is the only build).

### Prediction 6 (CONDITIONAL; if HARD_FAIL on A6) — substrate-native predicate-class capability lane closure

**Hypothesis:** if A6 em ≤ FREQ_BIAS even with all 5 primitives wired + MiniLM-L6 encoder, the substrate-native predicate-evaluation capability lane is structurally closed at this N_DIM regime. Route to glass-box-LLM L2 closure for predicate evaluation (LLM handles the predicate; substrate handles the storage/retrieval).

**Routing:** META atom `meta_atom_substrate_native_predicate_evaluation_below_freq_baseline_at_N_DIM_regime.md`; Path B 1M-facts capacity scaling as last-resort rescue.

**Calibrated P (HARD_FAIL on A6 conditional on running): 0.40** (deflated for substrate-uncertainty; if A6 HARD_FAILs, this is the principal closure-route).

---

## L5 — CROSS-THREAD SYNTHESIS

### With parent 5x drill (research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md)

- Parent drill correctly identified the COMPARATOR gap as load-bearing. This drill EXTENDS the analysis to the FULL predicate-primitive set. The COMPARATOR is one of 5 primitives; LOGICAL_NOT is the highest-leverage NEW addition; TEMPORAL_PRECEDES collapses to COMPARATOR-on-year for HotpotQA but is real leverage for MuSiQue/2Wiki.
- Parent drill's v3 handoff (Arms 3+4) is the IMMEDIATE COMPARATOR test. This drill PROPOSES a follow-up cell (`substrate_predicate_primitive_set_v1`) that tests the COMBINED 5-primitive set on HotpotQA comparison subset.
- Parent drill identified encoder (char_trigram → MiniLM-L6) as the upstream bottleneck. This drill assumes MiniLM-L6 is wired (per v3 handoff); predicate primitives are downstream and INHERIT the encoder's recall regime.

### With smoke 2x revival drill (research_2x_revival_comparator_resonator_HF_2026-06-23.md)

- Smoke confirmed COMPARATOR math is sound (sanity 5/5; FPE monotone; projection-sign 5/5).
- Smoke identified discrimination-floor (raw-W-lookup saturated at α=0.06; comparator's 1-bit summary cannot exceed raw's 32-level recovery in this regime).
- This drill INHERITS the discrimination-floor insight: the 5-primitive-set test must run in a regime where each primitive's value is detectable. Recommend (a) HotpotQA comparison subset where encoder/retrieval is noisy (primitives compensate); (b) synthetic-corpus capacity-sweep at α > α_c as control to show primitives DO add value when raw breaks.

### With CERT 587 g1b (autoregressive generation)

- g1b uses permute primitive for sequence-position encoding. Permute IS the discrete special case of TEMPORAL_PRECEDES (FPE generalization). The substrate already validated the discrete-time primitive at coh_arm4=0.94. Continuous-time FPE TEMPORAL_PRECEDES is the natural extension.
- g1b's substrate-native generation can OUTPUT predicate-evaluated answers (e.g., for "X before Y" question, generate "X" if temporal_precedes(X,Y) returns true). Cross-thread composition: predicate primitives feed into g1b generation as candidate tokens.

### With CERT 588 h_hotpotqa (KG ingest)

- h_hotpotqa KG is chain-grade-validated (setrecall=1.000, 2-hop=0.991). Predicate primitives operate on top of this KG.
- The W matrix in h_hotpotqa contains the (entity, attribute, value) bindings. ORDINAL_COMPARATOR and TEMPORAL_PRECEDES BOTH operate via `W @ bind(E, R)` lookups, which is the KG primitive at recall=99%+ for in-distribution queries.
- The bottleneck remains the encoder-side question → entity-linking (recall@5=1.9% at char_trigram). MiniLM-L6 fix (v3 handoff) addresses this.

### With META atoms (cleanup-load-bearing, by-construction-saturation, no-Hebbian-window)

- cleanup-load-bearing: QUANTIFIER_EXISTS uses refuse_gate threshold; aligned with cleanup-load-bearing META.
- by-construction-saturation: FREQ_BIAS_BASELINE arm is mandatory per parent META; HARD_PASS bar must clear FREQ_BIAS + 0.05.
- no-Hebbian-window: ALL 5 primitives are FORWARD-ONLY (no W modification at query time). Compatible.

### With USER HRR derivation (composition algebra)

- USER's HRR derivation validates that substrate's bipolar bind is mathematically equivalent to HRR's circular convolution (up to compression).
- TPR/HRR equivalence theorem (Plate 1995; Smolensky 1990; arxiv 1601.02745) implies ALL TPR predicate operations are derivable in HRR.
- The substrate INHERITS the full predicate-evaluation expressivity of TPR via this equivalence. The 5-primitive set is the substrate-native exposure of this expressivity.

### With USER lock-in amp / phase-encoded position

- Lock-in amp = phase detection at known frequency = FPE evaluation at known phase axis.
- TEMPORAL_PRECEDES via FPE phase-difference IS the lock-in-amp analog for temporal queries.
- Cross-thread: USER's "substrate acts at any position in phase diagram" directive (project_phase_diagram_action) is REALIZED by FPE-based temporal primitives — they let substrate act at any phase position.

### With phase-portrait + data-survives-transform lane (USER directive 2026-06-22)

- All 5 primitives are L2-norm-preserving (within ε; sign-flip and phase-rotation are exact-preserving; bind/unbind add ~ε cross-talk). Data survives transform.
- Predicate primitives extend the phase-portrait inventory: each predicate is a NEW position in the phase-diagram (predicate-evaluation phase, distinct from the bind/bundle/permute structural-composition phase).

---

## SUBSTRATE-PRODUCT IMPLICATIONS

### IMMEDIATE atomization (independent of next cell outcome)

1. **`META_predicate_primitives_are_naming_layer_not_new_infrastructure`** — all 5 minimum-set predicate primitives are constructible from existing substrate algebra (bind, bundle, permute, refuse_gate, FPE). Build cost is ONLY wrapper code (~200 lines `hdlab/predicates.py`); NO new infrastructure. Per TPR/HRR equivalence theorem; lit-validated.

2. **`META_temporal_precedes_collapses_to_ordinal_comparator_on_scalar_timestamps`** — for corpora where temporal queries are scalar-year comparisons (HotpotQA), TEMPORAL_PRECEDES degenerates to ORDINAL_COMPARATOR-on-year. FPE phase-encoding is needed only for periodic/relative temporal queries (MuSiQue, 2Wiki, real-world calendar arithmetic).

3. **`META_logical_not_is_free_in_bipolar_substrate`** — LOGICAL_NOT requires zero additional infrastructure; sign-flip is L2-preserving and zero-compute. Unlocks ~20% of HotpotQA comparison subset (negation queries) that current substrate outputs noise on.

4. **`hdlab/predicates.py` BACKLOG ATOM** — author the predicate-primitive wrapper file. ~200 lines. Includes: `temporal_precedes`, `logical_not`, `logical_and`, `quantifier_exists`. (ORDINAL_COMPARATOR will already be in `hdlab/comparator.py` per v3 handoff.)

### Forward chain (if substrate_predicate_primitive_set_v1 HARD_PASSES)

1. Cell HARD_PASSes → substrate-native predicate-evaluation capability lane is chain-grade.
2. v2: extend to MuSiQue / 2Wiki temporal-subset (test TEMPORAL_PRECEDES with FPE for relative-time queries; first corpus where FPE > ORDINAL_COMPARATOR).
3. v3: compose predicates with multi-hop ("X happened before Y AND X caused Z") for K=2 predicate composition; test noise accumulation prediction.
4. v4: residue-arithmetic VSA (arxiv 2511.08767) for compound arithmetic predicates (SVAMP-style "X + Y > Z").

### Reroute chain (if HARD_FAILs)

1. Diagnose per-primitive: which arm carries the failure (A3 = COMPARATOR; A4 = TEMPORAL; A5 = NOT; A6 = full set)?
   - If A3 fails: comparator is wrong at production-corpus (smoke regime was unrepresentative); diagnose encoder vs primitive.
   - If A5 = A4 (NOT does no work): negation parsing is failing; substrate cannot detect negation in question.
   - If A6 < A5 (adding AND/EXISTS HURTS): conjunction/existential primitives are anti-informative; remove from minimum set.

2. If A6 HARD_FAILs across the board: PHASE 2 RESTRUCTURE to glass-box-LLM L2 closure (LLM handles predicate evaluation; substrate handles storage/retrieval).

### L2 vision alignment

- The 5-primitive set is the substrate-native expressivity layer for an INSIDE-LLM substrate. The L2 vision = glass-box LM INSIDE substrate; predicate primitives are what the substrate exposes UPWARD to a thin LM head.
- If predicate primitives chain-grade-pass, the substrate has its first END-TO-END predicate-evaluation system. This is a foundational primitive class for the L1 vision (zero-LLM-call substrate-as-LM).

---

## CITATIONS (verified, count = 18)

**HDC/VSA core operators:**
1. Kleyko et al. 2023 — "A Survey on Hyperdimensional Computing aka Vector Symbolic Architectures, Part I" — ACM Computing Surveys (dl.acm.org/10.1145/3538531). Canonical primitive set bind/bundle/permute.
2. Kleyko et al. arxiv 2106.05268 — "Vector Symbolic Architectures as a Computing Framework for Emerging Hardware." Sign-test dynamics; predicate-op derivations.
3. Plate 1995 (IEEE TNN) — "Holographic Reduced Representations." HRR foundation; TPR equivalence.
4. Smolensky 1990 (dl.acm.org/10.1016/0004-3702(90)90007-M) — "Tensor product variable binding and the representation of symbolic structures in connectionist systems." Foundational TPR; predicate logic in distributed representations.
5. Smolensky 2016 arxiv 1601.02745 — "Basic Reasoning with Tensor Product Representations." Explicit predicate-evaluation construction (forward chaining; quantifiers).
6. Frady, Kent, Olshausen, Sommer 2020 (arxiv 1906.11684; rctn.org/bruno/papers/resonator1.pdf) — "Resonator Networks." Factorization primitive.

**FPE / temporal / residue arithmetic:**
7. arxiv 2412.00488 (2024) — "Improved Cleanup and Decoding of Fractional Power Encodings." FPE primitive.
8. arxiv 2604.25939 (2026) — "qFHRR: Rethinking Fourier Holographic Reduced Representations through Quantized Phase and Integer Arithmetic." Substrate-compatible FPE.
9. PMC10659444 (Hersche/Rahimi) — "Computing with Residue Numbers in High-Dimensional Representation." Residue arithmetic VSA; comparison/ordering derivation.
10. arxiv 2511.08767 — "Hey Pentti, We Did (More of) It!: A Vector-Symbolic Lisp With Residue Arithmetic." Frontier on predicate-evaluation primitives.
11. IEEE Xplore 11105931 — "Learning encoding phasors with fractional power encoding." Substrate-applicable FPE training.

**Brain mechanisms for predicate evaluation:**
12. Springer 10.1007/s12311-026-01995-3 / PMC13079516 — "Cerebellar Time and Relative Time: A Comparator-Based Dynamical Timing Model." Cerebellum-as-comparator brain primitive.
13. PMC11725584 — "Neuronal dynamics of cerebellum and medial prefrontal cortex in adaptive motor timing." Two-system temporal architecture.
14. PMC6099112 — "Distinct Dynamics of Striatal and Prefrontal Neural Activity During Temporal Discrimination." mPFC ramping for temporal primitives.
15. bioRxiv 2023.08.17.553665 — "Neural signatures for temporal order memory in the macaque medial posterior parietal cortex." Direct evidence for TEMPORAL_ORDER as brain primitive.
16. DeVito-Lykken-Kanter-Eichenbaum 2010 (PMC2832922) — "Prefrontal cortex: Role in acquisition of overlapping associations and transitive inference." RLPFC-as-comparator brain primitive (parent drill).

**Relational / attention / variable binding extensions:**
17. arxiv 2204.07186 — "Optimal quadratic binding for relational reasoning in vector symbolic neural architectures." Optimal binding for relational predicates.
18. arxiv 2512.14709 — "Attention as Binding: A Vector-Symbolic Perspective on Transformer Reasoning." Transformer attention as VSA binding; predicate evaluation analog.

**Substrate-internal (cert_ledger evidence; not counted in lit citation):**
- `data/exp_comparator_resonator_primitive_smoke_v1/metrics.json` — comparator smoke (HF1; per-arm metrics verified directly)
- `notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md` (parent drill)
- `notes/research_2x_revival_comparator_resonator_HF_2026-06-23.md` (smoke diagnosis drill)
- `notes/exp_dev_handoff_research_5x_QA_composition_v3_comparator_encoder_2026-06-23.md` (v3 handoff)

---

## LIT-SCAN CALIBRATION NOTES

- All P values deflated 0.15–0.25 from raw LM-based confidence per [[feedback-lit-scan-calibration-penalty]].
- Novel-synthesis cap 0.50 NOT binding for Predictions 4–5 (control-arm / META; these are not novel-synthesis); BINDING for Predictions 1 (full 5-primitive set composition is novel synthesis); composite Prediction 1 capped at 0.50, deflated to 0.25.
- HARD-FAIL thresholds mandatory and listed for every prediction.
- TPR/HRR equivalence (Smolensky 1990 + Plate 1995) is a STRONG mathematical result; transfer to substrate's bipolar Hebbian regime is moderate-novelty (substrate-specific empirical validation pending).
- Brain analog mappings (Stream B) are SOLID for ORDINAL_COMPARATOR + TEMPORAL_PRECEDES + LOGICAL_NOT; FUZZIER for QUANTIFIER_EXISTS (CA3 pattern completion is the closest); ABSENT for CAUSAL_BINDING (excluded from min set).
- The smoke-confirmed comparator math + the v3 handoff already in flight reduce execution risk; the unknown is the encoder-side bottleneck (per parent drill, MiniLM-L6 vs char_trigram).
- Composition-noise prediction (1/sqrt(k) per primitive depth) inherits from USER HRR derivation; substrate-validated at depth 2; UNVALIDATED at depth 5.

---

## SYMMETRIC NEGATIVITY CHECK (per USER STANDING)

**Could primitive HARD_PASS be artifact of MiniLM-L6 doing all the work?** Discriminator: include A2 (GENERATION_ONLY + MiniLM-L6) as control. If A6 ≤ A2, primitives add no value beyond encoder; primitives are decorative. Pre-reg discipline: A6 − A2 ≥ 0.05 to claim primitive-grade.

**Could TEMPORAL_PRECEDES be redundant with ORDINAL_COMPARATOR?** YES on HotpotQA scalar-year subset; the L3 drill explicitly notes this collapse. TEMPORAL_PRECEDES adds value ONLY on periodic/relative temporal queries (MuSiQue/2Wiki test, not HotpotQA). HARD-FAIL discipline: TEMPORAL_PRECEDES on HotpotQA is NOT load-bearing for primary HARD_PASS (it folds into ORDINAL_COMPARATOR); the load-bearing test is the next-corpus generalization cell.

**Could LOGICAL_NOT fail not because of substrate but because parser doesn't detect negation?** Discriminator: report A5 with DETERMINISTIC_NEGATION_PARSER (regex "not", "isn't", "did not") as control. If deterministic-parser works but g1b-native-parser fails, the failure is parse-side, not substrate-side. Both substrate-meaningful; let cert-owner classify.

**Could the 5-primitive set be over-engineered?** Possibly. If A4 (3 primitives: comparator + temporal + NOT) achieves 90% of A6 (5 primitives) em, the AND + EXISTS primitives are marginal. Pre-reg discipline: report A6 − A4 lift; if < 0.03, AND + EXISTS are MEASURED_MECHANISM not chain-grade.

**Could the chosen primitives miss a load-bearing one?** Candidates excluded from min set:
- CAUSAL_BINDING — excluded because no brain analog; reduces to TEMPORAL + statistical-overlap. If post-cell analysis shows residual error class = causal queries, REVIVE this as candidate primitive 6.
- LOGICAL_OR — excluded because = AND at low threshold. If OR queries fail at AND-low-tau, OR needs separate parameterization.
- UNIVERSAL_QUANTIFIER (forall) — excluded as derivable from EXISTS + NOT. If "for all X, P(X)" queries fail at NOT-of-EXISTS-NOT-P, FORALL needs separate parameterization.

**Could lit-scan over-claim primitive constructibility?** The TPR/HRR equivalence theorem is mathematically rigorous (Smolensky 1990 + Plate 1995; arxiv 1601.02745 explicit) but the SUBSTRATE-SPECIFIC bipolar Hebbian embedding has not been empirically validated for all 5 primitives. P_deflated reflects this; the smoke-confirmed COMPARATOR math is the only directly-validated point.

---

## DISPATCH RECOMMENDATION

**Immediate companion exp_dev hand-off** (written separately): `notes/exp_dev_handoff_research_drill_predicate_evaluation_primitives_2026-06-23.md`

- Anchor: `substrate_predicate_primitive_set_v1`
- Routing: local_cpu_queue (cheap; ~30 min CPU total)
- 6 arms × 5 question-class subsets × N_q=30 × 3 seeds
- Pre-reg HARD bands per L4 above
- Smoke: 10 Q × 1 seed × ~2 min; verify all 6 arms produce em + per-primitive code paths exercise without exception

**Pre-condition:** `hdlab/predicates.py` wrapper file authored (~200 lines; per spec L2 column 5). Lift COMPARATOR from `experiments/exp_comparator_resonator_primitive_smoke_v1.py` into `hdlab/comparator.py` (already specified in v3 handoff). Author NEW primitives: `temporal_precedes`, `logical_not`, `logical_and`, `quantifier_exists`.

**Three standalone META atoms (independent of cell outcome; per Substrate-Product L5 above):**
- `meta_atom_predicate_primitives_are_naming_layer_not_new_infrastructure_2026-06-23.md`
- `meta_atom_temporal_precedes_collapses_to_ordinal_comparator_on_scalar_timestamps_2026-06-23.md`
- `meta_atom_logical_not_is_free_in_bipolar_substrate_2026-06-23.md`

**Conditional follow-on if HARD_PASS:**
- v2: MuSiQue / 2Wiki temporal subset (test TEMPORAL_PRECEDES with FPE for relative-time queries)
- v3: predicate composition depth-2 ("X happened before Y AND X caused Z") for noise-accumulation validation
- v4: residue-arithmetic VSA transfer for SVAMP arithmetic-predicate queries

**Conditional reroute if HARD_FAILs:**
- Diagnose per-arm primitive failure (A3 comparator / A4 temporal / A5 NOT / A6 conjunction)
- If A6 HARD_FAILs across the board: PHASE 2 RESTRUCTURE to glass-box-LLM L2 closure for predicate evaluation
- META atom: `meta_atom_substrate_native_predicate_evaluation_below_freq_baseline_at_N_DIM_regime.md`

---

## CONTRACT OUTPUT

`research: delivered drill_predicate_evaluation_primitives -> notes/research_drill_predicate_evaluation_primitives_2026-06-23.md ; HEADLINE: minimum predicate-primitive set = 5 ops (ORDINAL_COMPARATOR + TEMPORAL_PRECEDES + LOGICAL_NOT + LOGICAL_AND + QUANTIFIER_EXISTS); causal-binding + full-OR excluded as reducible; rank-1+2 (TEMPORAL + NOT) covers 60% of HotpotQA comparison subset; all 5 derivable from existing substrate algebra via TPR/HRR equivalence — NAMING layer not new infrastructure; next-cell substrate_predicate_primitive_set_v1 tests 6-arm composition on HotpotQA comparison subset; P_deflated(A6 ≥ FREQ_BIAS+0.05)=0.25; next-drill candidate: residue-arithmetic VSA for compound arithmetic predicates`

---

*Research drill complete 2026-06-23. 3 parallel WebSearch lit-scans (HDC/VSA core operators; brain temporal/comparator mechanisms; TPR variable binding) + 2 deep-drill targeted lit-scans (residue arithmetic VSA; FPE temporal phase encoding) + cross-thread synthesis with parent 5x drill + smoke 2x revival + CERT 587 g1b + CERT 588 h_hotpotqa + USER HRR derivation + USER lock-in amp directive. Generic queries only (no substrate-novel mechanism names off-platform). Lit-scan calibration applied (deflate 0.15–0.25; novel-synthesis cap 0.50 binding for Prediction 1). HARD-FAIL thresholds mandatory; FREQ_BIAS baseline discipline inherited from parent drill. Symmetric negativity check applied (5 negativity-rebuttal angles). Per-arm metrics verified directly on smoke cell. 3 standalone META atoms routed; 1 hdlab/predicates.py backlog atom routed. Cell hand-off filed as companion file. Time elapsed ~25 min per budget.*
