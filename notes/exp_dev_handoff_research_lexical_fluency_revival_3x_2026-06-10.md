# exp_dev hand-off -- research: lexical fluency revival 3-stream methodology

**Filed-by.** Research (research sub-agent, 2026-06-10)
**Trigger.** research_drill_lexical_fluency_revival_3x_2026-06-10.md -- lexical production pipeline characterization, hybrid substrate-LLM viability
**Parent research note.** `notes/research_drill_lexical_fluency_revival_3x_2026-06-10.md`
**Pause state.** Check `data/orchestrator_paused.flag` before queuing. If paused, stage this file and wait for resume.

Per [[feedback-no-experiment-design-in-prompts]]: exp_dev owns all experiment design decisions below. This file states the mechanism, the test question, pre-registered pass/fail bands, and context pointers. exp_dev chooses anchor structure, queue routing, smoke gate, and seed count.

---

## Anchor candidates (rank-ordered)

### Anchor 1 -- SPECULATIVE-LEXICAL-ACCEPTANCE-RATE (Tier-3 top-K acceptance on high-frequency tokens)
**Mechanism.** Substrate Tier-3 codebook query: given Tier-2 binding vector X_2, retrieve top-K lemma candidates from M_3. Measure fraction of cases where the correct next token appears in top-3 candidates, on high-frequency (Zipf rank < 10K) tokens.
**Substrate-product reading.** If acceptance rate > 0.65: speculative-lexical decoding gives ~2.6x throughput on LLM API calls, reducing operating cost ~60%. This is the cheapest path to a concrete hybrid product claim.
**Tier hint.** CPU, Pythia-160M + Wikipedia KB (already in data/). Estimated < 3 hours. Queue: laptop CPU or data/local_cpu_queue.
**Why now.** Cheapest decisive gate. Fails fast if < 0.35 (abort hybrid-lexical direction entirely). Passes confidently if > 0.65 (unlock bilingual + monitor tests).
**Pre-reg bands.**
  - HARD-PASS: top-3 acceptance rate > 0.65 overall; top-1 > 0.40
  - MIDDLE BAND: top-3 in [0.45, 0.65]; top-1 in [0.25, 0.40]
  - HARD-FAIL: top-3 < 0.35 (no better than random from 50K vocabulary)

### Anchor 2 -- BILINGUAL-TIER2-INVARIANCE (cross-lingual Tier-2 cosine on translation pairs)
**Mechanism.** Encode 200 English-French translation pairs + 200 random cross-language pairs. Compute cosine(Tier-2_en, Tier-2_fr) for each set.
**Substrate-product reading.** If cosine > 0.75 for translation pairs: Tier-1/2 is language-universal; multilingual product generation via codebook swap is viable without LLM fine-tuning per language. Direct cost reduction for multilingual deployment.
**Tier hint.** CPU. Requires bilingual sentence pairs (WMT or Europarl 200-sentence sample). Estimated < 2 hours.
**Why now.** Second-tier gate after Anchor 1. Only worthwhile if Anchor 1 acceptance rate >= 0.45.
**Pre-reg bands.**
  - HARD-PASS: cosine > 0.75 for translation pairs; < 0.30 for random pairs; ANOVA F > 50
  - MIDDLE BAND: cosine in [0.50, 0.75] for translation pairs
  - HARD-FAIL: cosine < 0.40 (no Tier-1/2 language invariance)

### Anchor 3 -- TIER4-PHONOLOGICAL-CLUSTER (spontaneous phonological feature clustering in Tier-4)
**Mechanism.** Train substrate Tier-4 on character/phoneme co-occurrence from 100K Wikipedia sentences (no phonological supervision). Extract Tier-4 codebook. K-means (K=4) on cosine distance. Measure Adjusted Rand Index against phonological feature class labels (nasal / fricative / stop / approximant).
**Substrate-product reading.** If ARI > 0.60: substrate Tier-4 learns phonological structure from text alone, enabling phonological error detection in voice interface output (spoonerism / malapropism detection).
**Tier hint.** CPU. Uses existing Wikipedia data. Estimated < 1 hour. Queue: laptop CPU.
**Why now.** Quick analytical probe; can run in parallel with Anchor 1. Low infrastructure cost.
**Pre-reg bands.**
  - HARD-PASS: ARI > 0.60
  - MIDDLE BAND: ARI in [0.30, 0.60]
  - HARD-FAIL: ARI < 0.20

### Anchor 4 -- LEVELT-MONITOR-ROUNDTRIP (monitor coherence: generated output vs original intent)
**Mechanism.** Generate 200 intent vectors; for each, produce a correct paraphrase sentence and a random distractor sentence. Compute cosine(pool_query(KB, output), intent_vector) for each. Measure AUC-ROC for paraphrase vs distractor classification.
**Substrate-product reading.** If AUC-ROC > 0.88: substrate implements an internal error-monitoring loop (Levelt stage L4) without a separate LLM call. Enables self-correcting generation in formal document pipeline at near-zero additional latency.
**Tier hint.** CPU. Requires Wikipedia KB (existing). Estimated < 2 hours.
**Why now.** Third-tier gate; depends on Anchor 1 passing. Most architecturally novel claim.
**Pre-reg bands.**
  - HARD-PASS: AUC-ROC > 0.88
  - MIDDLE BAND: AUC-ROC in [0.70, 0.88]
  - HARD-FAIL: AUC-ROC < 0.65

### Anchor 5 -- ZIPF-CODEBOOK-COVERAGE (analytical coverage audit, 50K lemma codebook)
**Mechanism.** Count token frequencies on 1M Wikipedia sentences from existing extract. Compute coverage fraction of top-50K tokens.
**Substrate-product reading.** Coverage >= 80%: 50K-lemma codebook is sufficient for the product use case; cost-justifiable. Coverage < 65%: codebook size must increase substantially (100K+), changing deployment cost estimate.
**Tier hint.** Analytical, < 30 min, pure frequency counting on existing data. Can run anytime.
**Why now.** Trivial to run; resolves a design parameter (codebook size) with no experimental risk.
**Pre-reg bands.**
  - HARD-PASS: coverage >= 80%
  - MIDDLE BAND: coverage in [65%, 80%]
  - HARD-FAIL: coverage < 65%

---

## Context pointers

- Research drill note: `d:/AI/hd-instrument/notes/research_drill_lexical_fluency_revival_3x_2026-06-10.md`
- Wikipedia KB extract: `d:/AI/hd-instrument/data/` (184K facts from overnight chain)
- Compositional cliff findings: `d:/AI/hd-instrument/notes/` (substrate_v3_compositional_cliff_crossed.md via memory index)
- PP-225 fp32-head fact-recall recipe: `d:/AI/hd-instrument/notes/exp_dev_POST_COMPACTION_BRIEF_2026-06-09_evening.md`
- Speculative draft viable verdict context: same brief above

---

## Contract

All 5 tests are laptop-CPU scale, no cloud required. The execution sequence is:
  1. Run Anchor 5 (Zipf coverage, 30 min) -- design parameter, zero risk.
  2. Run Anchors 1 + 3 in parallel (< 3 hours each) -- decisive gates.
  3. If Anchor 1 passes: run Anchor 2 bilingual test.
  4. If Anchor 1 passes: run Anchor 4 monitor test.
  5. If Anchor 1 hard-fails: flag to Research; redirect to RAG-only hybrid path.

No cloud dispatches in this batch. All anchors use existing data infrastructure.

---

## Autonomy declaration

exp_dev decides:
- Anchor ordering and parallelization within available queue capacity
- Queue selection (laptop CPU vs local_cpu_queue) per feedback-laptop-run-no-nohup-use-timeout
- Smoke gate seed count and threshold
- Whether to combine Anchors 1+3 into a single cell or run separately
- Implementation details (exact substrate layer binding, codebook initialization, evaluation protocol)
- Whether to dispatch Anchors 2+4 conditional on Anchor 1 outcome or in parallel with it
- Self-test pairs per standard formula-selftests discipline
