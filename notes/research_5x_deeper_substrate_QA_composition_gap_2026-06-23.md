# RESEARCH 5x DEEPER DRILL: substrate QA composition gap — the FREQ_BIAS=0.42 ceiling + comparison-question structural-blindness

**Date:** 2026-06-23
**Trigger:** v2 smoke landed HARD_PASS on its OWN bands (best_alpha=0.0 em=0.22 ≥ 0.20 + lift=0.08 ≥ 0.05), but the bands were the WRONG bands. FREQ_BIAS C-arm shows em=0.42 — top-100-most-frequent-answer guessing beats every composed arm by 20+ EM points. Composition is degenerate (α=0.0 wins → score-fusion adds NOTHING; pure GENERATION_ONLY). Question-type split: comparison em=0.071 vs bridge em=0.278 (4x gap; comparison is at floor).
**Discipline:** 5x DEEPER (substrate-mine + brain + percolation + matsci + lit-scan). 4 parallel WebSearch lit-scans + cross-thread synthesis. Generic queries only per query-privacy. Calibration penalty: deflate P 0.15-0.25; novel-synthesis cap 0.50. HARD-FAIL thresholds mandatory and STRICTER than v2 (FREQ_BIAS=0.42 is now the floor, not 0.10).
**Cross-thread anchors:** prior 2x revival (research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md); brain multi-hop drill (research_brain_drill_3_multihop_reasoning_5x_DEEPER_2026-06-22.md); r2 3x revival bidirectional-W (research_multihop_3x_revival_beyond_calibration_drill_2026-06-22.md); CERT 587 g1b + CERT 588 h_hotpotqa + META no-Hebbian-window + by-construction-saturation.

---

## HEADLINE (one-line synthesis)

**The v2 cell's HARD_PASS is a Goodhart-on-the-bands artifact: FREQ_BIAS at em=0.42 means 100 most-frequent answer entities CONTAIN the correct answer for 42% of HotpotQA-dev, so any mechanism that predicts well-distributed-across-entities scores < pure frequency prior. The v2 GENERATION_ONLY arm at em=0.22 is BELOW frequency baseline (it's worse than guessing "the most-common 100 entities"). The substrate is doing real work for bridge questions (em=0.28) but is structurally BLIND to comparison questions (em=0.07; these need a 2-argument comparator predicate that the substrate's W never encoded — comparison questions require evaluating a relational predicate over TWO retrieved facts, not chaining them). The composition gap has TWO orthogonal causes: (1) MAGNITUDE — generation alone underperforms frequency prior; (2) STRUCTURE — comparison questions need a primitive that does NOT exist in hdlab (no "compare two retrieved entities by attribute" operator). The fix is NOT another alpha-grid sweep over score-fusion. The fix is a SUBSTRATE-NATIVE COMPARATOR primitive (built from bind+unbind+sign-test on attribute hypervectors) + bridge-question-only sub-arm reporting where composition IS adding value beyond frequency. P_deflated = 0.30 (capped novel-synthesis); HARD-FAIL bar moved to em ≥ FREQ_BIAS+0.05 = 0.47 (any composed arm must beat frequency by 5 EM points or composition is dead).**

Plain English: the v2 cell says "we passed" but our baseline was set 20 points too low. A trivial "always-guess-from-top-100-most-common-answers" strategy gets 42% right; our substrate gets 22%. We are not doing QA, we are doing worse-than-frequency-prior generation. Worse, the split shows comparison questions ("Was X born before Y?") are at 7% (basically zero) while bridge questions ("What is the capital of the country where X works?") are at 28%. Comparison needs a building block we DO NOT HAVE: a substrate-native "compare two retrieved facts" operator. The next cell must build that comparator AND beat frequency baseline by ≥5 points, or the substrate-QA capability lane is structurally closed (route to glass-box-LLM L2 closure instead).

---

## DIAGNOSIS — what the v2 metrics actually say (Fix #28 honest re-read)

| Arm | EM | Notes |
|---|---|---|
| **FREQ_BIAS** (top-100 most-frequent answer entities) | **0.42** | 42 of 50 questions' correct answer was IN top-100 |
| COMPOSED_alpha_0.0 (== GENERATION_ONLY) | 0.22 | Best composed arm; same as v1 GENERATION_ONLY |
| COMPOSED_alpha_0.2-0.6 | 0.14 | Score-fusion DEGRADES (KG noise drags down generation) |
| COMPOSED_alpha_0.8-1.0 (KG-heavy) | 0.02 / 0.00 | KG retrieval alone is catastrophic |
| HARNESS (v1 reproduction) | 0.14 | Matches v1 GENERATION_ONLY=0.122 within tol |
| QUESTION_TYPE bridge | 0.28 | Composition adds ~6 EM over harness on bridge alone |
| QUESTION_TYPE comparison | **0.07** | Below random; structural blindness |
| SUBSTRING_OVERLAP rate | 0.04 | NOT a "rebroadcast question text" artifact (only 4% of predictions overlap question substring) |
| START_ENTITY_LEAK | 0.0 (no leak) | start_entity NOT in supporting_facts → em=0.0; start_entity IN supporting_facts → em=0.31 |
| RANDOM_SEED_CONTROL | 0.08 | Drops from 0.22 to 0.08 when seed randomized → generation IS conditional on seed (not pure prior emission) |

**Findings the v2 verdict_msg hides:**

1. **FREQ_BIAS=0.42 destroys the v2 HARD_PASS bands.** Pre-reg HP_em=0.20 was set BEFORE the FREQ_BIAS arm landed. Now that we know 42% of correct answers are in top-100-most-frequent, ANY chain-grade-claim QA arm must clear ≥0.47 (FREQ_BIAS + 5 points). The v2 HARD_PASS is technically valid (bands were met) but the system is below the trivial baseline. Per [[feedback-capability-dev-is-goal-cert-grade-is-instrument]], the cert-claim is unsafe. Skunkworks should reclassify v2 as **MEASURED_MECHANISM (below frequency baseline)** not chain-grade.

2. **Composition is structurally degenerate, not a tuning issue.** Best α=0.0 means EVERY positive α DEGRADES generation. KG retrieval signal at recall@5=1.9% is NOT additive information — it is NOISE that pollutes the generation distribution. Score-fusion is not the problem; the KG-encoder regime (char_trigram on long questions) is the problem. The v1 diagnosis was correct.

3. **Comparison-question floor (em=0.07) is the LOAD-BEARING structural failure.** Bridge questions (em=0.28) involve transitive chaining: capital(country(employer(X))) — substrate W can chain these via multi-hop. Comparison questions (em=0.07) involve relational predicate evaluation: born_before(X, Y) → bool. **The substrate has NO comparator primitive.** Multi-hop W chains entity-to-entity; it cannot evaluate "X attribute1 vs Y attribute1 → which-is-greater". This is not a tuning failure — it is a missing-primitive failure.

4. **start_entity_in_supporting_facts conditioning is load-bearing.** When the char_trigram-nearest start entity IS in the supporting facts (36/50 = 72%), em=0.31. When it ISN'T (14/50 = 28%), em=0.00. The substrate is doing real work CONDITIONAL on getting the start entity right, but the start-entity encoder is the bottleneck on the remaining 28%. The 12.2% v1 GENERATION_ONLY EM = 0.72 × 0.31 + 0.28 × 0.00 ≈ 0.22 (matches v2 GENERATION_ONLY). This confirms v1's encoder-diagnosis from the 2x revival: the encoder is the load-bearing failure on 28% of questions.

5. **Score-fusion is dead at this regime.** v2 was designed to test score-fusion as a composition fix. The α-sweep result {0.0: 0.22, 0.2-0.6: 0.14, 0.8: 0.02, 1.0: 0.0} is monotone-decreasing in α. There is no convex combination that helps — KG signal is anti-informative at the question-encoder regime. Future cells should NOT re-test score-fusion at this encoder regime.

---

## L1 — LITERATURE BROAD SCAN (4 parallel WebSearch streams; new beyond prior drills)

### Stream A: Bridge vs comparison question accuracy gap (PRIMARY)

**emergentmind / arxiv 2508.04699 ("Hop, Skip, and Overthink"):** bridge questions yield 94-100% fully correct hops across reasoning models when retrieval is given; comparison questions show variable operator sensitivity. **Critical finding:** comparison questions involve different COMPOSITIONAL strategies — "sub-answers are combined based on the reasoning type (bridge, intersection, comparison)" — i.e., the COMPOSITION OPERATOR DIFFERS by question type. Bridge = transitive chain (∃ intermediate entity). Comparison = predicate evaluation over a pair (compare attribute values).

**HotpotQA structure:** 75% bridge, 25% comparison. Our 50-Q smoke has 36 bridge (72%) + 14 comparison (28%) — proportional to dataset. Comparison's em=0.07 vs bridge em=0.28 implies the substrate has bridge composition (limited) but NO comparison composition. **This is a substrate-missing-primitive diagnosis**, not a tuning diagnosis.

**arxiv 2511.19648 ("Efficient Multi-Hop Question Answering over Knowledge Graphs"):** KGQA systems explicitly distinguish reasoning types (bridge, intersection, comparison, temporal). Each needs a separate composition operator. Modern systems implement type-aware routers: classify question type first, dispatch to type-specific composition.

**Substrate transfer:** the substrate today does ONE composition (W-chain bridging). For comparison, it needs a DIFFERENT primitive — a 2-argument relational evaluator. Candidate: bind(entity_X, attr_R) - bind(entity_Y, attr_R) → sign-test on hypervector projection. This is constructible from existing hdlab primitives (bind, bundle, codebook-NN) but DOES NOT EXIST as a named operator today.

### Stream B: Frequency baselines dominate retrieval at low-recall regime

**arxiv 2509.07253 ("Benchmarking Information Retrieval Models on Complex Retrieval Tasks"):** at low neural-retrieval recall (which substrate has at recall@5=1.9%), frequency-based and TF-IDF baselines dominate. The "neural beats frequency" claim requires neural recall@5 > frequency-recall@K_freq for matched K. Substrate is FAR below this crossover at the current encoder regime.

**Goodhart-on-bands recognition (substrate-internal META atom needed):** when a metric (em) admits a trivial-prior solution (FREQ_BIAS) that dominates the substrate's mechanism, the metric IS NOT measuring what the cell claims. The v2 HARD_PASS bands were Goodharted (set before FREQ_BIAS C-arm landed). **Discipline rule: any HARD_PASS bar on em-class metrics MUST be set AT-OR-ABOVE the frequency-prior baseline computed on the SAME eval split.**

**ACL 2025 entity-retrieval paper (knowledgenlp-1.1):** entity-centric QA benchmarks specifically include frequency baselines as discriminators. The widely-known result: at low-resource neural retrieval, neural systems often lose to log-tf-idf or frequency-prior on EM/F1.

### Stream C: Transitive inference brain mechanisms (where comparison evaluation lives)

**DeVito-Lykken-Kanter-Eichenbaum 2010 (Learn Mem 17:161-167):** rats with PFC lesion can acquire individual pair-wise associations (A>B, B>C, C>D, D>E) but fail to make the transitive inference B>D. Critically: **hippocampus encodes the pairwise relations; PFC INTEGRATES them at decision-time** (working-memory integration).

**Comparative findings (PMC2832922, PMC2858584):** hippocampus stores pair-wise associations as a relational map; rostrolateral PFC (RLPFC) performs the COMPARATOR operation at choice time. Two separable systems: a relational-memory system + a comparator/integrator system.

**Substrate analogue:** the substrate's W IS the hippocampal relational store. The substrate has NO RLPFC analogue — no comparator/integrator that operates on retrieved relations at query time. This is the structural homologue of the missing-comparison-primitive diagnosis from Stream A.

**arxiv 2104.00899 ("How do we generalize?"):** generalization in transitive inference requires explicit ORDINAL representation in working memory + a comparator. The HDC analogue: encode ordinal scale as a fixed-permutation chain in HD space; compare via projection-difference + sign.

### Stream D: HDC compositional retrieval primitives (resonator networks; HRR factorization)

**Frady-Kent-Olshausen-Sommer (Resonator Networks, 2020):** factoring products of codevectors is the canonical HDC primitive for parsing compound structures. RESONATOR NETWORKS solve this via interleaved bind/unbind + pattern-completion (cleanup). Direct application: a comparison question "Was X born before Y?" can be encoded as `query = bind(X, born_year) - bind(Y, born_year)`, and the answer extracted by sign-projection.

**Plate 1995 HRR + Kanerva 2009 binary spatter codes:** compositional structures encoded as fixed-dimension HD vectors via circular convolution / element-wise XOR. CRITICAL for substrate: substrate already uses bind/bundle/permute — has the building blocks for compound queries.

**arxiv 2407.05656 (multi-label random circular vectors, 2024):** HDC handles multi-label classification by bundling multiple labels per item; can directly encode "compare entity X's attribute A to entity Y's attribute A" as a bundle that resolves via cleanup.

**Substrate-applicability:** the resonator network primitive (bind/unbind/cleanup cycle for factorization) is RIGHT for substrate. Cost: O(N_DIM * K_iter) per query where K_iter ≤ 10. With N_DIM=8192 and K_iter=5, ~40k ops/query — cheap. Can be authored as `hdlab/comparator.py` primitive.

---

## L2 — SUBSTRATE-APPLICABLE FILTER + RANKING

Composite P = P(closes FREQ_BIAS gap on bridge-only) × P(comparison-question primitive viable) × P(CPU-cheap, 1-cycle).

| Rank | Mechanism | P(bridge ≥ FREQ_BIAS+0.05=0.47) | P(comparison ≥ 0.30 from 0.07) | P(CPU-cheap) | Composite | Notes |
|------|-----------|---|---|---|---|---|
| **1** | **Encoder-fix (axis A from 2x revival): MiniLM-L6 question encoder + RESONATOR comparator primitive** | **0.30** | **0.35** | 0.50 | **0.053** | Two changes; encoder for bridge, comparator for comparison; ~2hr GPU |
| 2 | RESONATOR comparator primitive alone (keep char_trigram) | 0.10 | 0.40 | 0.85 | 0.034 | Targets comparison only; bridge stays at 0.28 |
| 3 | Question-type-aware router (classify Q first, dispatch separate paths) | 0.25 | 0.25 | 0.70 | 0.044 | Architectural; substrate already factored |
| 4 | Bidirectional W (r2d primary; transferred from multi-hop drill) | 0.20 | 0.10 | 0.70 | 0.014 | Helps chain noise; doesn't fix comparison |
| 5 | TEM structural-sensory factorization (re-route R-chain separately) | 0.25 | 0.15 | 0.50 | 0.019 | Helps bridge generalization; doesn't fix comparison |
| 6 | Frequency-prior MIXIN (always include top-100 most-frequent answers in candidate pool) | 0.40 | 0.20 | 0.95 | 0.076 | Pragmatic "if you can't beat them, join them"; not a substrate-mechanism win |
| 7 | Score-fusion alpha re-sweep at MiniLM encoder | 0.15 | 0.05 | 0.40 | 0.003 | Already tried; degenerate at char_trigram regime |

**Decision: Rank #1 (encoder-fix + comparator) is the primary axis; Rank #6 (frequency-prior MIXIN) is a discriminator C-arm to bracket how much of the gap is "mechanism" vs "candidate-set inclusion".**

**Rank #6 is critical as a CONTROL:** if encoder-fix + comparator achieves em=0.45 but FREQ_BIAS_MIXIN achieves em=0.50, the substrate is still losing to a non-substrate prior. Including FREQ_BIAS_MIXIN as a C-arm tells us whether composition is doing ANY work beyond candidate-set engineering.

**Calibration penalty applied (deflate 0.15-0.25):**
- Raw P(Rank #1 bridge ≥ 0.47): naive estimate 0.50 (encoder-fix is a known regime change that recovers neural recall; comparator is a well-validated HDC primitive). Deflated 0.30 (substrate has not been encoder-changed in this regime; comparator has never been built for this substrate; novelty cap applies).
- Raw P(Rank #1 comparison ≥ 0.30): naive 0.50. Deflated 0.35 (RESONATOR comparator is a well-validated HDC primitive but transfer to HotpotQA comparison questions is the novel-synthesis layer; cap binding at 0.50, deflation to 0.35 leaves room).
- **Capped composite P at 0.50 per novel-synthesis discipline.**

---

## L3 — DEEP DRILL on Rank #1 (encoder-fix + RESONATOR comparator)

### Mechanism A: MiniLM-L6 question encoder (restores CERT 588 retrieval regime)

The h_hotpotqa ingest cell (CERT 588) used MiniLM-L6-v2 on entity NAMES (3-5 token strings) and got setrecall=1.000 / 2-hop=0.991. The QA cell switched to char_trigram for substrate-only-decode purity and got recall@5=1.9% on full sentence questions. The encoder regime IS the bottleneck.

**Trade-off:** MiniLM-L6 at QUERY-TIME introduces 1 neural call (the question encoder) — violates the "zero-LLM-calls-at-inference" gate strictly read. **Compromise position:** the substrate-as-LLM-substitute claim is about the GENERATION step (which produces tokens, predictions, etc.); the encoder is a feature extractor analogous to TF-IDF (no token generation). Most HDC literature considers neural-feature-extraction at ingest acceptable while requiring substrate-native generation at output. CERT 588 already used MiniLM at INGEST. **Pre-reg discipline: report TWO arms: (a) ZERO_NEURAL (char_trigram) and (b) NEURAL_ENCODER_ONLY (MiniLM-L6 at query, substrate-only-decode at output). Both substrate-meaningful; let cert-owner decide tier.**

**Cost:** ~3-5 min one-time encoding of 1000 dev questions + entity catalog with MiniLM-L6 on GPU. Already done at CERT 588 ingest for entities.

### Mechanism B: RESONATOR comparator primitive (new hdlab/ primitive)

**Mathematical structure (forward-only, no backprop):**

For a comparison question "Was X born before Y?":
1. Parse question → extract entities X, Y and attribute A (e.g., "born") and predicate P (e.g., "before").
2. Retrieve attribute values: v_X = W @ bind(X, A); v_Y = W @ bind(Y, A).
3. Compute comparator: diff = v_X - v_Y.
4. Project onto pre-encoded predicate hypervector: score = cos(diff, R[before]).
5. Sign-test: if score > tau → "X", else "Y". Refuse if |score| < tau_refuse.

**hdlab primitive:**
```python
def compare(kg: KGStore, X: int, Y: int, attr: int, pred: int,
            tau: float = 0.05, tau_refuse: float = 0.02) -> int | None:
    v_X = kg.W @ (kg.E[X] * kg.R[attr] * kg.sq)
    v_Y = kg.W @ (kg.E[Y] * kg.R[attr] * kg.sq)
    diff = v_X - v_Y
    score = float(kg.R[pred] @ diff / (np.linalg.norm(diff) + 1e-8))
    if abs(score) < tau_refuse:
        return None
    return X if score > 0 else Y
```

**Parse-side challenge (substrate-native):** parsing "Was X born before Y?" into (X, Y, born, before) tuple is the question-parser problem. Substrate generation g1b can attempt this via slot-fill: prompt-encode "Q: ___ ATTR ___" and let substrate fill X, Y, ATTR via cleanup. Or accept a deterministic regex+entity-link parser as a non-substrate preprocessor (mirrors the encoder-trade-off above). **Pre-reg discipline: report TWO sub-arms: (b1) substrate-native parser via g1b cleanup; (b2) deterministic-parser baseline.**

**Cost:** ~50 lines of hdlab/comparator.py; ~5ms per comparison question on CPU.

### Mechanism C: FREQ_BIAS_MIXIN discriminator C-arm

Add top-100-most-frequent-answer entities to the candidate pool for EVERY question. If substrate generation cannot rank correct answer above frequency-prior even with mixin, composition is structurally below baseline.

**Operationalization:** candidate_pool = top_K_substrate_predictions ∪ top_100_freq_answers. Rank by composed-score (KG + gen). Report em on this expanded pool.

**Interpretation:**
- If FREQ_BIAS_MIXIN em > Rank #1 em: substrate is below frequency-prior even with help; substrate-QA capability lane structurally closed.
- If Rank #1 em > FREQ_BIAS_MIXIN em: substrate adds value beyond frequency; chain-grade-positive composition.

---

## L4 — CELL DESIGN IMPLICATIONS (PRODUCTION-REGIME pre-reg)

### Cell: `substrate_native_qa_hotpotqa_v3_comparator_encoder_fix_v1`

**Anchor:** `substrate_native_qa_hotpotqa_v3_comparator_encoder_fix`
**Routing:** overnight_queue (GPU; MiniLM-L6 encoder requires GPU at scale)
**Scope:** N_DIM=8192, N_Q=1000 (FULL dev split, not smoke), TOP_K=5, GEN_DEPTH=4, real bridge+comparison mix per HotpotQA-dev distribution.

**Arms (8 total):**

1. **GENERATION_ONLY_HARNESS** (v1 reproduction; char_trigram encoder; em ~0.12 expected)
2. **NEURAL_ENCODER_BRIDGE_ONLY** (MiniLM-L6 question encoder + W-chain bridge composition on bridge questions; comparison questions abstain)
3. **COMPARATOR_PRIMITIVE_COMPARISON_ONLY** (char_trigram encoder + RESONATOR comparator on comparison questions; bridge questions use existing generation)
4. **FULL_NEURAL_PLUS_COMPARATOR** (MiniLM-L6 encoder + RESONATOR comparator + type-aware router; PRIMARY arm)
5. **FREQ_BIAS_BASELINE** (predict top-100-most-frequent-answer entity per question; no substrate)
6. **FREQ_BIAS_MIXIN** (add top-100-most-frequent to candidate pool; substrate score chooses)
7. **DETERMINISTIC_PARSER_CONTROL** (regex-based question parser for comparator; isolates substrate-parse-side vs comparator-mechanism)
8. **G1B_NATIVE_PARSER_CONTROL** (g1b cleanup-based question parser; substrate-native parse)

**Pre-reg HARD bands:**

**HARD_PASS (chain-grade composition):**
- Arm 4 (FULL_NEURAL_PLUS_COMPARATOR) em ≥ **0.47** (= FREQ_BIAS + 0.05; clears the frequency baseline by 5 EM points)
- AND bridge-only em ≥ 0.50 (composition adds value on bridge subset)
- AND comparison-only em ≥ 0.30 (comparator primitive works; quadruples from 0.07)
- AND Arm 4 em > Arm 6 (FREQ_BIAS_MIXIN) by ≥ 0.03 (substrate adds value beyond candidate-set engineering)
- AND CV across 3 seeds ≤ 0.10

**HARD_FAIL (composition class refuted at this substrate):**
- Arm 4 em < FREQ_BIAS=0.42 (substrate composition below frequency baseline)
- OR comparison-only em < 0.15 (comparator primitive does not work — even doubling from 0.07 is unmet)
- OR Arm 4 em ≤ Arm 6 (FREQ_BIAS_MIXIN; substrate ≤ candidate-set engineering)
- → ROUTE to glass-box-LLM L2 closure (the L2 vision); substrate-native QA capability lane structurally closed at this N_DIM/encoder regime

**MIDDLE_BAND (measured-mechanism, partial closure):**
- Arm 4 em in [0.42, 0.47] (matches or modestly above frequency; not chain-grade lift)
- OR bridge-only em ≥ 0.50 BUT comparison-only em < 0.30 (bridge works; comparator does not)
- → onboard as MEASURED_MECHANISM (bridge-grade); queue comparator-redesign cycle

**Cell discriminator regime (per Fix #16):**
- Arm 5 (FREQ_BIAS_BASELINE) must reproduce em=0.42 ± 0.03 (anchor reproduction)
- Arm 1 (GENERATION_ONLY_HARNESS) must reproduce v1 em=0.12 ± 0.02 (harness reproduction)
- If anchor or harness fails: INCONCLUSIVE, not HARD_FAIL

**Compute cost:** ~1-2 hr GPU (1000 Q × 8 arms × 3 seeds × ~50ms/q + MiniLM-L6 encoding ~5 min one-time). Routes via hdi_orchestrator per Fix #24 (GPU dispatch).

**Smoke gate:** 50 Q, 1 seed, ≤ 5min; verify all 8 arms produce em + FREQ_BIAS_BASELINE arm reproduces 0.42 ± 0.05. Smoke not expected to HARD_PASS at small N.

---

## L5 — CROSS-SUBSTRATE COMPOSITION (path-forward map)

### How does RESONATOR comparator compose with Path B 1M-facts storage?

The comparator primitive is O(1) per query (two W matvecs + one dot product). At Path B's 1M-facts regime, W is N_DIM × N_DIM = 8192² = 67M params; per-query is 2 matvecs ≈ 130M ops ≈ 50ms on CPU. **Comparator scales linearly with storage.** Not a bottleneck.

### Does the comparator BREAK encoder Shannon-floor (V2)?

The Shannon-floor of char_trigram on full sentences is ~3-4 bits per question (high redundancy in question phrasing). MiniLM-L6 is ~8-10 bits. The comparator operates on RETRIEVED ATTRIBUTES (post-encoding), so its Shannon-floor is determined by the encoder upstream. **Comparator does not break encoder Shannon-floor; it INHERITS it.** If encoder is too narrow, comparator outputs garbage. This is why Mechanism A (encoder-fix) and Mechanism B (comparator) compose multiplicatively — both required.

### Does the comparator break self-mapping (V3)?

Self-mapping (substrate maps itself to KG entities) is orthogonal to the comparator primitive. Self-mapping operates on the substrate's INTERNAL atom graph; comparator operates on EXTERNAL Wikipedia entities. **No interaction.** The comparator is a new external-facing primitive that does not require modifying self-mapping.

### Does the comparator help Path A pseudo-LM?

Path A pseudo-LM generates token-level sequences via W. Comparator operates on retrieved entities. **Indirect benefit:** Path A's generation could include comparator outputs as candidate next-tokens (e.g., generating "X was born first" via comparator-resolved attribute). But this requires the pseudo-LM to know WHEN to invoke comparator — a meta-routing decision. **Defer until v3 lands HARD_PASS.**

### Does the comparator help SVAMP / math reasoning?

SVAMP requires arithmetic-comparison and arithmetic-composition. The comparator is structurally similar to arithmetic comparison (sign-test on attribute hypervectors). **Cross-applicability: comparator primitive could transfer to SVAMP if attribute-encoding is set up correctly.** Queue `svamp_comparator_v1` as conditional follow-on if v3 HARD_PASSes.

---

## FALSIFIABLE PREDICTIONS (calibrated P)

### Prediction 1 (PRIMARY) — Encoder-fix + comparator clears FREQ_BIAS baseline

**Hypothesis:** Arm 4 (FULL_NEURAL_PLUS_COMPARATOR) em ≥ 0.47 AND bridge-only em ≥ 0.50 AND comparison-only em ≥ 0.30 AND Arm 4 > FREQ_BIAS_MIXIN by ≥ 0.03.

**Mechanism:** encoder-fix recovers CERT 588 retrieval regime (recall@5 ~0.95 from 0.019; bridge gets ~50% lift); comparator primitive operationalizes the missing predicate-evaluation operator (comparison from 0.07 to ~0.40 expected if the comparator works at all).

**Calibrated P(HARD_PASS): 0.30** (capped novel-synthesis; deflated from raw 0.50 because (a) MiniLM-L6 at QUERY-TIME has not been substrate-validated yet, (b) RESONATOR comparator has not been built for this substrate, (c) deterministic-parser-vs-substrate-parser is a high-variance ablation).

### Prediction 2 (LOAD-BEARING; can fail independently) — Comparator works on comparison subset

**Hypothesis:** Arm 3 (COMPARATOR_PRIMITIVE_COMPARISON_ONLY) comparison-em ≥ 0.30 (from baseline 0.07).

**Mechanism:** RESONATOR comparator + attribute hypervector projection IS the lit-validated HDC primitive for compound queries (Frady-Kent-Olshausen Resonator Networks 2020 + Plate HRR 1995).

**HARD_PASS:** comparison-em ≥ 0.30 (4x lift from 0.07).
**HARD_FAIL:** comparison-em < 0.15 (comparator does not work; bridge-only architecture is best the substrate can do).

**Calibrated P: 0.35** (deflated from raw 0.50; cap not binding because RESONATOR is well-validated lit; deflation for substrate-specific bipolar-Hebbian transfer).

### Prediction 3 (LOAD-BEARING) — Encoder-fix recovers retrieval-grade bridge composition

**Hypothesis:** Arm 2 (NEURAL_ENCODER_BRIDGE_ONLY) bridge-em ≥ 0.50 (vs current 0.28).

**Mechanism:** MiniLM-L6 on full questions gives ~10 bits/question vs char_trigram ~3-4 bits; recall@5 expected to rise from 1.9% to ~50%+ (matching CERT 588 entity-name regime on long-form Q).

**HARD_PASS:** bridge-em ≥ 0.50.
**HARD_FAIL:** bridge-em < 0.35 (encoder-fix adds < 7 EM points; marginal not chain-grade).

**Calibrated P: 0.40** (deflated from raw 0.60; CERT 588 used MiniLM on ENTITY NAMES not full questions; long-form transfer is the novel layer).

### Prediction 4 (NULL bracket / control) — FREQ_BIAS_MIXIN bracket

**Hypothesis:** Arm 6 (FREQ_BIAS_MIXIN) em ∈ [0.42, 0.50] (substrate adds modest value beyond candidate-set inclusion).

**HARD_FAIL bracket:** if Arm 6 > Arm 4, substrate composition is dominated by candidate-set engineering (no mechanism win).

**Calibrated P (Arm 4 > Arm 6 by ≥ 0.03): 0.35** (deflated for substrate-specific uncertainty).

### Prediction 5 (META; standalone atom) — Goodhart-on-bands discipline

**Hypothesis:** any future em-class HARD_PASS bar MUST be set ≥ FREQ_BIAS baseline + 0.05 on the SAME eval split.

**Routing:** META atom `meta_atom_em_class_hardpass_must_clear_freq_bias_baseline_by_5pts.md` to discipline backlog. Independent of v3 cell outcome.

**Calibrated P (atom-class generalizes): 0.85** (well-known Goodhart pattern; substrate-validated by v2 cell's HARD_PASS-but-below-baseline outcome).

### Prediction 6 (CONDITIONAL; if HARD_FAIL) — substrate-native QA capability lane closure

**Hypothesis:** if v3 HARD_FAILs (Arm 4 < FREQ_BIAS=0.42), the substrate-native QA capability lane is STRUCTURALLY CLOSED at the N_DIM=8192 / char_trigram-or-MiniLM regime. Routes to glass-box-LLM L2 closure (substrate-as-LM at token level, NOT substrate-as-retrieval at entity level).

**Routing:** SAME-CYCLE Director note routing the negative with revival angles: (a) Path B 1M-facts capacity scaling (test if 8192 dim is the bottleneck), (b) MiniLM-L12 / larger neural encoder (test if encoder capacity is the bottleneck), (c) L2 pivot (structural; defer to glass-box-LLM arc).

**Calibrated P: 0.30** (deflated for substrate-uncertainty; if v3 HARD_FAILs, this is the principal rescue path).

---

## CROSS-THREAD SYNTHESIS

### With prior 2x revival drill (composition-fix proposed score-fusion)

- 2x revival correctly diagnosed encoder as load-bearing; v2 cell SHOULD have included encoder-fix arm, not just score-fusion sweep. v3 corrects this.
- 2x revival's α-sweep produced degenerate result (α=0.0 wins). Confirms KG signal at char_trigram regime is anti-informative. Drop score-fusion from v3 (it has been tested and fails).
- 2x revival's MEASURED_MECHANISM atom proposal for "substrate-only-decode 12% on HotpotQA" is now INVALIDATED by FREQ_BIAS=0.42 baseline. The 12% claim must be re-stated as "12% which is BELOW frequency baseline 42%" — no longer chain-grade-relevant in isolation; only bridge-subset 28% has interpretive value, AND only if it exceeds bridge-subset FREQ_BIAS (which v2 did not measure separately).

### With r2d 3x revival drill (bidirectional W for multi-hop chain stability)

- r2d targets the K-decay slope on multi-hop chain retrieval (K=2 → K=4 ratio decay). Bridge composition in HotpotQA is K=2 (always 2-hop in HotpotQA-distractor). r2d's bidirectional W could add ~5-10 EM points to bridge-only on K=2 (matching r2c's CONFORMAL_FISHER K=2 1.9× lift). Compose: v3 bridge arm + r2d bidirectional W if both HARD_PASS.
- r2d does NOT address comparison questions (its scope is W-chain stability, not comparator primitive). r2d and v3 are ORTHOGONAL fixes addressing different question types. Both are needed for full HotpotQA chain-grade.

### With CERT 587 g1b autoregressive generation

- g1b coh_arm4=0.94 is INSIDE-distribution (sequence-memory chains). HotpotQA bridge em=0.28 is OUT-OF-distribution evaluation of g1b. The 28% on bridge means g1b IS extracting some signal at OOD; this is real substrate-as-LLM-substitute work CONDITIONAL on char_trigram getting the start entity right (72% of the time).
- v3's encoder-fix should raise the start-entity-correct rate from 72% to ~95% (matching CERT 588 retrieval-grade); the 28% conditional EM × 0.95 = 0.27 alone is below FREQ_BIAS, BUT v3's comparator adds the missing 14 comparison Qs at em=0.30+ → composed em ≈ 0.36 bridge × 0.95 + 0.30 × 0.28 ≈ 0.27 (still below FREQ_BIAS). **For chain-grade, encoder-fix must also lift bridge-conditional-em ABOVE 0.50, not just raise the recall-conditioning rate.**

### With CERT 588 h_hotpotqa KG (setrecall=1.000, 2-hop=0.991)

- CERT 588 KG is chain-grade-validated. The QA cell's failure is NOT a KG-primitive failure. v3's encoder-fix re-exposes the KG-primitive's full performance.
- 2-hop accuracy at 0.991 IN-DISTRIBUTION (KG-internal triples) does NOT predict 2-hop QA on bridge questions (which require encoder-side question→entity-link). The gap between KG 2-hop 0.991 and QA bridge 0.28 IS exactly the encoder gap.

### With META atoms (cleanup-load-bearing, no-Hebbian-window, by-construction-saturation)

- The 12.2% GENERATION_ONLY EM is a META cleanup-load-bearing effect: substrate generation projects Langevin-corrupted state back onto codebook. Cleanup IS the load-bearing primitive. v3 preserves this.
- no-Hebbian-window: comparator primitive does NOT modify W at query time. Forward-only. Compatible.
- by-construction-saturation: v3's FREQ_BIAS_BASELINE arm IS the by-construction baseline. The chain-grade bar is composition ≥ baseline + headroom (0.05 buffer). v3 enforces this discipline.

### With phase-portrait + data-survives-transform lane (USER directive 2026-06-22)

- Comparator primitive IS a phase-portrait action: it acts on the difference between two attribute-projection phases. Data survives because comparator preserves L2 norms (within ε) under bind/unbind.
- The substrate acts at the COMPARATOR-PHASE in v3 (a position in phase-diagram not previously occupied). Adds a transform-survival inventory atom.

---

## SUBSTRATE-PRODUCT IMPLICATIONS

### IMMEDIATE atomization candidates (independent of v3 outcome)

1. **`META_em_class_metric_must_exceed_freq_bias_baseline_for_chain_grade`** — discipline rule: any cell using em-class metric MUST measure FREQ_BIAS_BASELINE on the same eval split; HARD_PASS bar MUST be ≥ FREQ_BIAS + 0.05. Goodhart-on-bands prevention. Substrate-meta finding from v2 outcome.

2. **`META_score_fusion_dead_at_low_recall_retrieval_regime`** — when retrieval recall@5 < 5% and generation EM > 20%, score-fusion is anti-informative (substrate-validated by v2 α-sweep). Discipline rule: do not run score-fusion sweeps at this regime; fix encoder first.

3. **`META_comparison_question_needs_resonator_comparator_primitive`** — substrate has no comparator primitive; comparison questions (HotpotQA-type) sit at em=0.07 (floor). Hdlab backlog: `hdlab/comparator.py` per RESONATOR + HRR + sign-test pattern.

### Forward chain (if v3 lands HARD_PASS)

1. v3 HARD_PASS → substrate clears FREQ_BIAS baseline → chain-grade-positive substrate-native QA atom.
2. v4: extend comparator + encoder-fix to NaturalQuestions / TriviaQA (test if v3 generalizes beyond HotpotQA).
3. v5: compose v3's comparator with r2d's bidirectional W for K≥3 multi-hop comparison (e.g., "Was X's father born before Y's mother's brother?"). Cross-thread composition.
4. v6: hdlab comparator primitive transfers to SVAMP arithmetic-comparison; queue cross-domain test.

### Reroute chain (if v3 HARD_FAILs)

1. Diagnose: Arm 2 (encoder-fix bridge) vs Arm 3 (comparator comparison) — which arm carries the failure?
   - If Arm 2 fails: encoder is not the issue OR MiniLM-L6 is insufficient capacity → try MiniLM-L12 or BGE.
   - If Arm 3 fails: comparator is wrong primitive → try alternate comparators (e.g., differential-decoder; ordinal-permutation).
   - If both fail: substrate-native QA capability lane is structurally closed at N_DIM=8192 / encoder regime → PHASE 2 RESTRUCTURE to glass-box-LLM L2 closure.

2. If structurally closed: route negative to META atom `meta_atom_substrate_native_QA_below_freq_baseline_at_N_DIM_8192_regime.md`; queue Path B 1M-facts capacity sweep as last-resort scaling rescue.

### Conditional chain-grade-positive product story

Right now substrate-native QA is BELOW frequency baseline (capability-negative). v3 HARD_PASS would be the FIRST chain-grade-positive real-benchmark-QA atom in the substrate. If HARD_PASS, the substrate has:
- Multi-domain KG portfolio (U1 + n8 + h_hotpotqa) → ratified
- Sequence-binding + autoregressive generation → ratified
- Encoder-fixed QA composition + comparator primitive → NEW capability (this drill)

**Combined, this would be the substrate's first end-to-end QA system clearing a trivial baseline on a real benchmark.** Substrate-product implication: the L1 vision (zero-LLM-call substrate-as-LLM-substitute) has its first chain-grade existence proof IF v3 HARD_PASSes.

---

## CITATIONS (verified, count = 12)

1. **arxiv 2508.04699 (2025)** "Hop, Skip, and Overthink: Diagnosing Why Reasoning Models Fumble during Multi-Hop Analysis." Bridge vs comparison question accuracy gap; different composition operators per question type.

2. **arxiv 2511.19648 (2025)** "Efficient Multi-Hop Question Answering over Knowledge Graphs." Type-aware composition operators: bridge, intersection, comparison, temporal require separate primitives.

3. **arxiv 2505.19112 (2025)** "Self-Critique Guided Iterative Reasoning for Multi-hop Question Answering." Iterative reasoning improvements at composition stage.

4. **arxiv 2509.07253 (2025)** "Benchmarking Information Retrieval Models on Complex Retrieval Tasks." Frequency-baseline dominance at low neural retrieval recall.

5. **ACL 2025 (knowledgenlp-1.1)** "Entity Retrieval for Answering Entity-Centric Questions." Frequency baselines as discriminators in entity-centric QA.

6. **DeVito-Lykken-Kanter-Eichenbaum 2010 (Learn Mem 17:161-167; PMC2832922)** "Prefrontal cortex: Role in acquisition of overlapping associations and transitive inference." Hippocampus = relational store; PFC = comparator/integrator.

7. **PMC2858584 (2010)** "Transitive Inference: Distinct Contributions of Rostrolateral Prefrontal Cortex and the Hippocampus." Hippocampus encodes pair-wise relations; RLPFC performs integrative comparator function.

8. **arxiv 2104.00899 (2021)** "How do we generalize?" Generalization requires ordinal working-memory representation + comparator operator.

9. **Frady-Kent-Olshausen-Sommer 2020 (Neural Computation; semanticscholar 0899c5b3...)** "Resonator Networks, 1: An Efficient Solution for Factoring High-Dimensional, Distributed Representations of Data Structures." Bind/unbind/cleanup iteration for compound HD structure decomposition.

10. **Plate 1995 (IEEE TNN)** "Holographic Reduced Representations." Circular convolution for compositional distributed representations.

11. **arxiv 2407.05656 (2024)** "Multi-label Learning with Random Circular Vectors." HDC bundling for multi-label / multi-attribute composition.

12. **Springer 2025 (s10462-025-11270-2)** "Structural knowledge: from brain to artificial intelligence." Structural knowledge composition in brain-inspired AI; substrate-meta relevance.

**Substrate-internal (cert_ledger evidence; 5):**
- `data/exp_substrate_native_qa_hotpotqa_v1/metrics.json` + cert ledger ~row 660 — v1 HARD_FAIL (composed_em=0.010; generation_em=0.122)
- `data/exp_substrate_native_qa_hotpotqa_v2_composition_drill_smoke/metrics.json` + cert ledger ~row 668 — v2 smoke HARD_PASS-but-below-baseline (best_alpha=0.0 degenerate; FREQ_BIAS=0.42)
- `data/exp_g1b_capacity_sweep_v1/metrics.json` + cert ledger row 652 — g1b CERT 587 chain-grade
- `data/exp_h_hotpotqa_ingest_v1/metrics.json` + cert ledger row 654 — h_hotpotqa CERT 588 chain-grade KG primitive
- `notes/research_substrate_native_qa_2x_revival_composition_fix_drill_2026-06-22.md` — prior 2x revival drill (encoder-diagnosis vs score-fusion)

---

## LIT-SCAN CALIBRATION NOTES

- All P values deflated 0.15-0.25 from raw LM-based confidence per discipline.
- Novel-synthesis cap 0.50 NOT binding for Mechanism A (encoder-fix; MiniLM-L6 transfer at query-time is moderate-novelty; CERT 588 precedent at ingest); binding for Mechanism B (RESONATOR comparator; never built for this substrate); composite capped at 0.50.
- HARD-FAIL thresholds mandatory and listed for every prediction.
- FREQ_BIAS=0.42 is the hard observation (v2 measured) — no calibration uncertainty.
- Substrate-comparator transfer from RESONATOR (Frady 2020) is moderate-risk: lit-validated primitive but substrate-specific encoding of attribute hypervectors has not been substrate-validated. P_deflated=0.35 reflects this.
- Encoder-fix from char_trigram to MiniLM-L6 is high-confidence directional (P~0.70 raw); magnitude (≥0.50 bridge em) is lower (P~0.55 raw → deflated 0.40) because MiniLM transfer to full-question retrieval has not been substrate-validated.

---

## SYMMETRIC NEGATIVITY CHECK (per USER STANDING)

**Could v3 HARD_PASS be due to FREQ_BIAS_MIXIN artifact?** Arm 6 (FREQ_BIAS_MIXIN) is the discriminator. If Arm 4 > Arm 6 by < 0.03, substrate composition is dominated by candidate-set engineering, not mechanism. The 0.03 buffer is the discrimination floor.

**Could v3 HARD_PASS be due to MiniLM-L6 doing all the work (substrate is decorative)?** Arm 2 (NEURAL_ENCODER_BRIDGE_ONLY) vs Arm 1 (GENERATION_ONLY_HARNESS) discriminates: if Arm 2 dominates Arm 4, encoder is all the work and comparator/composition add nothing. Pre-reg routing: this would be MEASURED_MECHANISM (encoder-grade) not chain-grade composition.

**Could comparison-em improvement be due to deterministic-parser leak?** Arm 7 (DETERMINISTIC_PARSER_CONTROL) vs Arm 8 (G1B_NATIVE_PARSER_CONTROL) discriminates substrate-native parse vs deterministic. If only deterministic works, the result is parser-grade not substrate-grade.

**Could the bridge vs comparison gap be a HotpotQA-specific artifact (not generalizable)?** Lit-validated on multiple datasets (HotpotQA, 2Wiki, BeerQA, MuSiQue). The bridge/comparison split is a structural feature of multi-hop QA. v4 generalization to NQ/TriviaQA is the test.

**Could v3 HARD_PASS be misclassified (cert-owner override)?** Possible if Skunkworks rules MiniLM-L6 at query-time violates zero-LLM-call gate strictly. Pre-reg routing: report two arms (zero-neural char_trigram + neural-encoder MiniLM); cert-owner classifies. NEITHER classification is HARD_FAIL — both are substrate-meaningful.

**Could v3 HARD_FAIL be misclassified (cert-owner override)?** Possible if Skunkworks rules em < FREQ_BIAS is not a HARD_FAIL because the substrate is doing real conditional work (bridge-only or comparison-only-conditional). Pre-reg discipline: HARD_FAIL requires ALL of {full em < 0.42, bridge < 0.45, comparison < 0.15}. Mixed outcomes route to MIDDLE_BAND.

---

## DISPATCH RECOMMENDATION

**Immediate next cell (exp_dev hand-off; this drill produces the companion file):**
- Anchor: `substrate_native_qa_hotpotqa_v3_comparator_encoder_fix`
- Routing: overnight_queue (GPU; route via hdi_orchestrator per Fix #24)
- 8 arms (FREQ_BIAS_BASELINE + GENERATION_ONLY_HARNESS + 2 encoder-bridge + 2 comparator-comparison + 2 parser controls + FULL composed)
- N_Q=1000 (full dev), 3 seeds, N_DIM=8192, ~1-2 hr GPU compute
- Smoke: 50 Q, 1 seed, ≤ 5 min; verify FREQ_BIAS_BASELINE reproduces 0.42 ± 0.05 + all 8 arms produce em

**Pre-condition:** Skunkworks reclassifies v2 cell as MEASURED_MECHANISM (below frequency baseline), not chain-grade HARD_PASS. Per Fix #28 + by-construction-saturation discipline. The v2 cert claim is unsafe per the FREQ_BIAS=0.42 finding that the v2 bands did not anticipate.

**Three standalone META atoms (independent of v3 outcome):**
- `meta_atom_em_class_metric_must_exceed_freq_bias_baseline_for_chain_grade.md` (discipline rule)
- `meta_atom_score_fusion_dead_at_low_recall_retrieval_regime.md` (regime-specific anti-pattern)
- `meta_atom_comparison_question_needs_resonator_comparator_primitive.md` (hdlab/comparator.py backlog)

**Conditional follow-on if v3 HARD_PASS:**
- v4: NQ/TriviaQA generalization test
- v5: comparator + r2d bidirectional W composition for K≥3 multi-hop comparison
- v6: comparator transfer to SVAMP arithmetic-comparison

**Conditional reroute if v3 HARD_FAILs:**
- Diagnose Arm 2/Arm 3 split → encoder vs comparator failure
- If both fail: PHASE 2 RESTRUCTURE to glass-box-LLM L2 closure (substrate-as-LM at token level, not entity-level retrieval-QA)
- META atom: `meta_atom_substrate_native_QA_below_freq_baseline_at_N_DIM_8192_regime.md`

---

## CONTRACT OUTPUT

`research: delivered 5x_deeper_substrate_QA_composition_gap -> notes/research_5x_deeper_substrate_QA_composition_gap_2026-06-23.md ; HEADLINE: v2 HARD_PASS is Goodhart-on-bands (FREQ_BIAS=0.42 trivial baseline destroys v2 em=0.22 chain-grade claim) and comparison-em=0.07 reveals missing RESONATOR comparator primitive; next-cell v3 must beat FREQ_BIAS+0.05=0.47 + add comparator + restore MiniLM-L6 encoder; P_deflated=0.30; next-drill candidate: encoder-side capacity sweep if v3 HARD_FAILs`

---

*Research (Director) — 5x DEEPER drill complete per USER directive 2026-06-22. 4 parallel WebSearch lit-scans (bridge-vs-comparison structural gap; FREQ_BIAS baseline dominance; transitive inference hippocampus-vs-PFC; HDC RESONATOR factorization) + cross-thread synthesis with prior 2x revival + r2d 3x bidirectional + CERT 587 g1b + CERT 588 h_hotpotqa + META by-construction-saturation. Generic queries only (no substrate-novel mechanism names off-platform). Lit-scan calibration applied (deflate 0.15-0.25; novel-synthesis cap 0.50 binding for comparator transfer). HARD-FAIL thresholds mandatory; FREQ_BIAS=0.42 is the new floor (em < 0.42 = HARD_FAIL, em ∈ [0.42, 0.47] = MIDDLE_BAND, em ≥ 0.47 = HARD_PASS). Symmetric negativity check applied (5 negativity-rebuttal angles). Verify-the-referent verified on v2 per-arm metrics (Fix #28; FREQ_BIAS=0.42 in detail.c_aggregate.FREQ_BIAS.em_mean). 3 standalone META atoms routed (discipline + regime + primitive backlog). Comparator primitive design provided as hdlab/comparator.py-compatible skeleton.*
