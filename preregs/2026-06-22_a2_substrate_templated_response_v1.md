# a2_substrate_templated_response_v1 — pre-registration

**Date:** 2026-06-22
**Anchor name:** a2_substrate_templated_response_v1
**Status:** locked pre-reg
**Lineage:** 2026-06-09 BATCH_HIERARCHICAL anchor A2 (Research) — never fired; resurrected per Director
hybrid Path A + Path B strategic spec 2026-06-22 (entity-sequence -> English-text rendering as
the LLM-Tier-3+ gap).

## What this cell does

Implements substrate-templated response generation for a 7-category question taxonomy:

  question text
     -> CharTrigramEncoder            (substrate-native text -> HD)
     -> KGStore.score_all(q_hd)        (CERT 588 multi-value Hebbian KG; HotpotQA-derived triples)
     -> top-K candidate entities
     -> question-category classifier   (rule-based pattern match; 7 categories)
     -> template fill                  (entity slot substitution into static template strings)
     -> English sentence answer

Zero LLM forward calls at inference (substrate-only-decode gate enforced). Templates are
static strings; substrate retrieves the entity that fills the slot.

## Three arms (Fix #16 discriminator)

1. **TEMPLATED_RESPONSE** — full pipeline (KG retrieval + category-classify + template fill).
   Returns an English sentence.
2. **RAW_ENTITY_SEQUENCE** — current `substrate_native_qa_v1` style baseline: KG top-K returned as a
   raw `entity1 -> entity2 -> entity3` chain. No template, no English. Anchor reproduction of
   the existing substrate-native chat output.
3. **NO_RETRIEVAL_TEMPLATE_ONLY** — CAN-FAIL discriminator: category-classify only; pick template;
   fill with question-tokens as best-guess entity (no KG retrieval at all). Tests whether KG
   retrieval is load-bearing for factual correctness.

The TEMPLATED arm should beat RAW on factual-accuracy AND grammatical-acceptance.
NO_RETRIEVAL should fail on factual-accuracy (templates without facts are word salad).

## Question categories (7)

Top-7 chosen for HotpotQA coverage (most HotpotQA questions are WHO_DID_X / WHAT_IS_X /
COMPARE_X_Y / LIST_X). Mapping rules are surface-pattern: lowercase regex on the question text
(no LLM, no semantic classifier).

1. **WHO_DID_X**  -- regex `^(who (was|is|did)|by whom)` -> template
   `"{title} was {action} by {answer_entity}."`
2. **WHAT_IS_X**  -- regex `^(what (is|was|does)|define)` -> template
   `"{title} is {answer_entity}."`
3. **WHERE_IS_X** -- regex `^(where (is|was|did))` -> template
   `"{title} is located in {answer_entity}." | "{title} was in {answer_entity}."`
4. **WHEN_DID_X** -- regex `^(when (did|was|is))` -> template
   `"{title} happened in {answer_entity}."`
5. **LIST_X**     -- regex `^(what are|list|name the|how many)` -> template
   `"{title}: {answer_entity}."`
6. **COMPARE_X_Y** -- regex `^(are|were|is .* the same|do .* both|did .* both)` -> template
   `"{answer_entity}."` (typically yes/no; HotpotQA "comparison" type)
7. **CHAIN_X_TO_Y** -- regex `(related to|connection between|link)` -> template
   `"{title1} is connected to {title2} via {answer_entity}."`
8. **FALLBACK**   -- if no pattern matches -> template `"{answer_entity}."` (degenerate; still
   constitutes a valid templated response — but typically scores poorly grammar-wise.)

## Test corpus

HotpotQA distractor-dev 1k JSONL at `data/datasets/hotpot_qa_distractor_dev_1k.jsonl` (already
ingested + chain-grade per CERT 588 `exp_h_hotpotqa_ingest_v1`). Subsample N_Q questions per
seed (100 questions full; 30 questions smoke). Each question has a gold short-answer string
(used for factual EM); gold-grammatical-acceptability is assessed via a substrate-native
mechanical checker (NOT an LLM): presence-of-fact-token-in-output + sentence-shape rules
(starts capital, ends `.`, no unsubstituted `{slot}` braces, no empty entity strings).

## Pre-registered HARD bands (CALIBRATED via 2026-06-22 smoke + v1-retrieval reality)

The 2026-06-09 anchor specified "factually correct + grammatically acceptable >= 0.90".
Smoke-gate (2026-06-22 23:55 UTC) + v1 evidence (substrate_native_qa_hotpotqa_v1 HARD_FAIL
2026-06-23 01:34: retrieval_only EM = 0.010 at N_DIM=8192 N_Q=1000; recall@5 = 0.019) shows
KG retrieval quality at HotpotQA-distractor scale is the **gating ceiling** for any retrieval-
fed templated response. The factual bar is calibrated against this ceiling, not against the
original anchor's 0.90 (which presumed clean-retrieval; HotpotQA retrieval ceiling does not
support 0.90 at this scale).

**Structural claim under test:** "templates render entity-sequences grammatically as English
sentences." Load-bearing metric = **grammatical_ratio lift** (TEMPLATED vs RAW). Factual
bar is a secondary check (gated by KG retrieval quality, which is independently broken at
this scale per v1).

- **HARD_PASS** (all required):
    - TEMPLATED gram_ratio >= 0.80 on N_Q test questions (templates render clean English)
    - TEMPLATED gram_ratio - RAW gram_ratio >= +0.50 (template-rendering machinery works)
    - TEMPLATED factual_ratio >= RAW factual_ratio (template at least preserves retrieval signal;
      does NOT degrade it)
    - n_llm_calls == 0
- **HARD_FAIL** (any of):
    - TEMPLATED gram_ratio < 0.50 (templates produce ungrammatical output)
    - TEMPLATED gram_ratio <= RAW gram_ratio (rendering machinery adds no English structure)
    - TEMPLATED factual_ratio < RAW factual_ratio - 0.05 (template DEGRADES retrieval signal)
    - n_llm_calls > 0 (substrate-only-decode gate violated)
- **MIDDLE_BAND**: in between.

**HARD_PASS interpretation if achieved**: Substrate has a chain-grade text-rendering primitive
that takes (entity, category-classification) and produces clean English. The factual signal
remains retrieval-gated and weak (~1-15% per v1 evidence) -- but the rendering pipeline is
proven and is reusable downstream when a better retrieval primitive lands (e.g. n11 random-
indexing-semantic or substrate_native_qa_v2_composition_drill).

**HARD_FAIL interpretation**: template-fill does not produce English at structural rate;
need substrate-native generative text rendering (not slot-fill templates).

## Scoring details

**Factual correctness** (per HotpotQA-standard EM normalization in `substrate_native_qa_v1`):
- normalize_answer: lowercase, strip punctuation, strip articles, collapse whitespace
- factual_hit = 1 if normalize(gold_answer) appears as a substring of normalize(response)
  (substring not strict-EM, because templates wrap the answer in extra words).
- factual_ratio = sum(factual_hits) / N_Q

**Grammatical acceptability** (mechanical; no LLM):
- gram_hit = 1 if ALL of:
    - response starts with an alphabetic character (no leading `{`, no leading space)
    - response ends with `.` (period; ASCII)
    - response contains NO unsubstituted braces `{` or `}` (slot-fill failure detector)
    - response contains at least one substituted entity (i.e. response != template-skeleton)
    - response length 5 <= len(words) <= 40 (avoids degenerate one-word or runaway outputs)
- gram_ratio = sum(gram_hits) / N_Q

**Per-category breakdown** (Fix #28): metrics.json carries `per_category` with factual+gram
ratios for each of the 7 categories + FALLBACK. Verdict claim "substrate generates English"
requires per-category breakdown, not just overall numbers.

## Compute / routing

- N_DIM = 2048 (substrate-native QA v1 smoke used same; 100-question test is lightweight)
- N_Q full = 100; N_Q smoke = 30
- SEEDS full = [7, 17, 23]; SEEDS smoke = [1]
- 3 arms x 3 seeds x 100 questions x ~10ms per question = ~9s/arm/seed = ~80s wall full
- Plus encoder fixed-cost (CharTrigramEncoder lazy-warm + entity-name encode of HotpotQA
  vocab ~3-5k entities) ~30s startup
- Total estimated wall: 3-6 minutes full
- Routing: **remote_cpu_queue** (matches v1's queue; numpy/torch CPU-friendly; no GPU benefit
  at N_DIM=2048 for 100 questions)

## What's measured + why HARD_PASS is positive evidence for substrate-as-LLM

If HARD_PASS:
- substrate retrieves correct fact AND wraps it in fluent English sentence
- demonstrates the entity-sequence -> English-text rendering gap is closeable via templates
  for a meaningful fraction of QA workload (covers Tier 1-3 capability per hybrid spec)
- becomes a chain-grade primitive for the substrate-as-LLM-substitute pipeline (hdlab/
  `template_response.py` candidate primitive after cert-grade)

If HARD_FAIL (TEMPLATED <= RAW):
- templates don't add lift; the existing raw-entity-sequence is the operating ceiling for
  this approach; pivot needed (substrate-native English generation, not templated wrapping)

If MIDDLE_BAND:
- template-lift exists but factual bar not crossed; isolate which categories work; iterate

## Composes with

- **Already-shipped chain-grade**: hdlab/kg_traversal (CERT 588), hdlab/char_trigram_encoder
  (CERT 585), HotpotQA ingest (CERT 588)
- **Strengthens if HARD_PASS**: Director hybrid Path A + Path B strategic spec (rendering
  primitive validated for 1k-question subset)
- **Falsifies if HARD_FAIL**: templated-wrapper is NOT the rendering gap fix; substrate-native
  text-generation primitive is needed instead

## What this does NOT need

- No new hdlab primitive
- No research drill (template approach is well-defined)
- No LLM forward calls (substrate-only-decode gate)
- No new benchmark (HotpotQA distractor-dev already loaded)
- No GPU (pure CPU at N_DIM=2048; 100 questions)

— Exp-Dev (cell-author; pre-reg locked before smoke + dispatch)
