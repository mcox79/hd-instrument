# Research: LLM-1 token-prediction experiment design audit (v1)

Date: 2026-05-31
Origin: user 2026-05-31 -- "do a 2x deep research on this experiment to maximize possibility of passing"
Method: main-thread audit + 2 parallel Sonnet drills (encoding + capacity; domain + baseline + criteria); synthesis pending drills' return

## HEADLINE

The original LLM-1 spec has 5 design choices that hand-wave over make-or-break questions. Honest read: the spec as written is set up to fail on open-domain Wikipedia at 20K stored patterns vs 1M-token corpus. To "maximize chance of passing" honestly (not rig the test), the design choices that matter are:
1. **Context encoding scheme** (HOW are 8 tokens bound into one bipolar codeword?)
2. **Domain choice** (constrained-domain vs open-domain Wikipedia)
3. **Capacity ratio** (stored patterns / corpus diversity)
4. **Retrieval primitive** (single-hop classical, NOT depth-5 Path D)
5. **Baseline strength** (Kneser-Ney smoothed n-gram, not "uniform baseline")

Two parallel Sonnet drills dispatched on highest-leverage dimensions (encoding + domain). Synthesis = routing file with optimized experiment design + pre-registered HARD-PASS bands when drills return.

## Issues with the original spec

### Issue 1: Context encoding is ambiguous

Spec says: "Context_window = previous N tokens encoded as a binding (start with N=8 token context)"

The HOW is the open question. Options:
- **Plate HRR-style**: `ctx = sign(sum_i pos_i ⊙ v_t_i)` — bundling N=8 bipolar tokens with bipolar position keys; preserves both identity + order
- **Permutation binding**: `ctx = perm_1(v_t_1) ⊙ perm_2(v_t_2) ⊙ ... ⊙ perm_8(v_t_8)` — sequence of position-permuted tokens, all bound via element-wise product
- **Concatenation + folding**: literally concatenate 8 token vectors then fold via XOR
- **Recursive bind via order matrix**: more complex; less common in lit

The choice fundamentally determines whether the binding algebra preserves enough information at substrate dimension N. **Drill A is resolving this.**

### Issue 2: Capacity math is hand-waved

Spec says: "M up to substrate capacity (~10K-20K stored patterns)" but corpus has ~1M (ctx, next_token) pairs.

- 20K stored / 1M corpus = 2% coverage. Most test contexts will have NO stored match.
- Substrate sees only 2% of distribution; CANNOT beat baseline that fits the full distribution.
- At N=4096 modern Hopfield (~max_M = N to 4N), 16K-65K patterns is the realistic envelope.
- At N=16384 modern Hopfield (validated v297 max_M = 16N = 262K), much more headroom.

To "maximize chance of passing," either:
- **Increase N to 16384** (modern Hopfield envelope validated; more capacity)
- **Restrict to constrained domain** where 20K patterns covers most of the distribution
- **Both**

### Issue 3: Path D is the wrong primitive

Spec says: "Production-default Path D for retrieval"

Path D is the depth-5 multi-hop Bayesian-posterior mechanism. For SINGLE-HOP next-token prediction (given context, retrieve next token), the right primitive is **classical matmul-then-argmax**. Path D adds overhead with no benefit at depth=1.

A separate question: could Path D depth=5 be used for AUTOREGRESSIVE GENERATION (retrieve token, then use as new context, retrieve next, etc.)? Yes — this is the LLM-2 / LLM-3 territory. But for LLM-1 (single next-token), depth=1 classical is correct.

### Issue 4: Baselines are too weak

Spec says: "baseline n-gram ~15-25% top-1" and "perplexity lower than uniform baseline"

Real baselines:
- **Uniform on |V|=8K**: perplexity 8000, top-1 1/|V| = 0.0125%. **Trivially beatable; meaningless comparison.**
- **Unigram (frequency-weighted random)**: perplexity ~few-hundred on typical English; top-1 5-10%.
- **Kneser-Ney smoothed 5-gram**: perplexity 50-100 on Wikipedia, 10-30 on constrained domains; top-1 25-40%. **This is the real bar.**
- **Tiny LSTM (~1-2M params)**: perplexity 30-80; top-1 30-45%.
- **GPT-2-small (124M)**: perplexity 20-40; top-1 40-50%. Unrealistic at substrate's capacity but useful reference.

The 20% top-1 target in the spec is BELOW Kneser-Ney baseline. Substrate "passing" 20% top-1 doesn't actually demonstrate value — it shows substrate is worse than the standard baseline. **Drill B is resolving the honest baseline set.**

### Issue 5: Open-domain Wikipedia is the worst test design

Spec says: "small corpus (start with ~1M tokens of clean text — Wikipedia subset or similar)"

Wikipedia is the WORST domain for limited-capacity substrate:
- Highest vocabulary diversity (~30K-50K unique words even at 1M token slice)
- Highest context entropy (any topic can follow any topic)
- Strong baselines (Kneser-Ney + tiny LSTM both achieve substantial top-1)

Constrained domains where substrate has a fair shot:
- **Code completion (single language)**: high structural regularity; identifiers + keywords highly predictable; n-gram baseline weaker because of long-range dependencies
- **Recipes**: formulaic ("Add the X to the Y", "Cook for N minutes"); narrow vocab; predictable continuations
- **Dialogue templates / customer-support transcripts**: turn-based; predictable response patterns
- **Restricted Q&A**: structured patterns

**Drill B is ranking domain options.**

## What "maximize chance of passing" should mean

NOT: rig the test by choosing parameters where substrate wins by construction.
DOES: choose parameters where success is realistically achievable AND meaningful.

The honest version of LLM-1:
- **Constrained domain** (likely code or recipes) where substrate has fair-shot vs n-gram
- **Optimal context encoding** per drill A
- **Substrate dimension** matched to corpus diversity (probably N=16384 to use validated max_M = 16N envelope)
- **Single-hop classical retrieval**, NOT Path D depth=5
- **Strong baselines**: Kneser-Ney smoothed n-gram + tiny LSTM + FAISS k-NN over same corpus
- **Coverage-weighted accuracy** as primary metric (top-1 on stored contexts AND coverage fraction) — separates retrieval quality from coverage limitations
- **Substrate-distinctive composite**: accuracy + audit completeness + edit-then-predict consistency + deletion-then-predict consistency — substrate's product value comes from these, not raw top-1

## Pre-registered thresholds (initial proposal pending drill returns)

For the recommended config (constrained domain + N=16384 + Plate HRR encoding + 50K stored patterns + Kneser-Ney baseline):

- **HARD-PASS**: substrate top-1 ≥ Kneser-Ney baseline on covered contexts (coverage ≥40%) AND audit-trail completeness 100% AND edit-then-predict consistency >0.95
- **HARD-FAIL**: substrate top-1 below 1.5× unigram baseline (~15%) on covered contexts (substrate cannot retrieve coherently)
- **MIDDLE-BAND**: substrate top-1 in [unigram, n-gram] band — substrate retrieves SOME signal but doesn't match n-gram baseline; substrate-distinctive composite may still PASS if audit/edit/deletion gains compensate

## Sequencing

When drills return (~45 min wall):
1. Synthesize drill A (encoding + capacity) + drill B (domain + baseline) into the optimized experiment design
2. File routing file `notes/strategy_request_to_strategy_llm1_token_prediction_optimized_2026-05-31.md` with: anchor name, full spec sketch, pre-reg HARD-PASS/HARD-FAIL/MIDDLE-BAND, cost estimate, sequencing recommendation
3. Update research_decisions
4. log_event + commit

## Method note

This audit is a deliberate honest-first pass BEFORE the drills return. Per [[feedback-no-smoke]] — the original spec needs sharp critique before optimization, not after-the-fact. Per [[feedback-2x-means-depth]] — 2x means going DEEPER on existing findings; here the "existing finding" is the original spec, and depth = surfacing the 5 design issues that determine pass/fail.

The drills are NOT verification of the spec — they're operational deepening on the highest-leverage open design questions (encoding scheme + domain choice). When they return, the synthesis is the routing file with concrete numbers and pre-reg bands.
