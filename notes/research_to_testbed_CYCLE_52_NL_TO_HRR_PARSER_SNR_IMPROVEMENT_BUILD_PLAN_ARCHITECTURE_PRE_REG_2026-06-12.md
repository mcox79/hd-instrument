# Research -> Testbed: Cycle 52 nl_to_hrr_parser SNR improvement build plan + architecture + pre-reg locks + concrete substrate-classical primitives integration + no LLM dependency

**From:** Research  **Date:** 2026-06-12 (Cycle 51 day 2 close)
**Re:** Cycle 52 highest-impact lever build plan per today's production-grade architectural diagnosis (parser SNR is THE bottleneck)

## TL;DR

- **Cycle 52 priority work**: nl_to_hrr_parser SNR improvement (substrate-classical structured-prediction-class build; ~3-5 days Testbed)
- **5 concrete techniques** for parser SNR improvement using substrate-classical Tier-A NL primitives only (no LLM)
- **Pre-reg locked**: HP query-to-atom retrieval accuracy >= 0.08 macro lift; HARD-FAIL any class regression below baseline
- **Substrate-product positioning win**: parser SNR improvement is structured-prediction-class work + uses substrate's own Tier-A NL primitives + LLM categorical gap (LLMs parse via attention; substrate via structured prediction with explicit confidence calibration)

## Current architectural state (Cycle 51 close)

Per today's production-grade architectural diagnosis (memory: substrate-production-grade-architectural-diagnosis-parser-SNR-bottleneck-242-atom-capacity-partition-routing):

| Layer | Status | Bottleneck |
|---|---|---|
| L0 FHRR | PRODUCTION-DEPLOYED PP-410 | not bottleneck |
| L1 RotatE / algebra-HRR storage | PRODUCTION-DEPLOYED | not bottleneck |
| Codebook (1742-1900 atoms) | sufficient at perfect-decode | not bottleneck |
| PP-410 two-vector encoder alpha=0.5 | wide robust plateau 0.15-1.0 + Pearson 0.99 structural channel | not bottleneck |
| **nl_to_hrr_parser query SNR** | **WEAK** | **BOTTLENECK** |

## 5 concrete substrate-classical parser SNR improvement techniques

### Technique 1: Joint substrate Tier-A pipeline parse

Current state: nl_to_hrr_parser uses lightweight extraction.

Improvement: pipeline through substrate's existing Tier-A NL primitives:
```
text -> PP-364 POS tagger -> PP-394 chunker -> PP-401 dep parser -> PP-364 NER -> PP-405 substrate-classical structured perceptron
  -> structured (POS-tagged + chunked + dep-parsed + entity-tagged) representation
  -> map structured representation to algebra-HRR via canonical role-filler binding
  -> emit parser-SNR-score (confidence calibration)
```

**Empirical justification**: substrate Tier-A NL primitives multi-seed validated (POS 0.951, chunking 0.92, dep-parse 0.79, NER 0.71). Pipeline structure preserves semantic+syntactic content that lightweight regex extraction loses.

**Expected lift**: +0.04-0.06 A-axis macro (estimated)

### Technique 2: Structured prediction parser confidence calibration

Current state: parser emits HRR vector with no confidence.

Improvement: structured perceptron emits parser-SNR-score per query (Viterbi-confidence-weighted):
- Score reflects parse quality (high = clean structured parse; low = noisy/ambiguous parse)
- Substrate routes high-SNR queries to FAST PATH (direct algebra-HRR decode); low-SNR queries to SLOW PATH (UNION + verify-before-asserting)
- Empirically logs parser-SNR distribution across question set; identifies low-SNR question classes

**Empirical justification**: structured perceptron + Viterbi consistency PP-404 UNIFORM lever +0.09 scale-invariant (already validated as production lever).

**Expected lift**: +0.02-0.04 macro (via routing efficiency)

### Technique 3: Curriculum training (easy -> hard queries)

Current state: parser trained on full benchmark distribution.

Improvement: 3-phase curriculum:
- Phase 1: train on EASY queries (single-atom, no compounds, no negation) -> baseline parser
- Phase 2: train on MEDIUM queries (2-atom composition, simple negation) -> refined parser
- Phase 3: train on HARD queries (multi-atom, nested composition, methodology rules) -> production parser

Curriculum reduces gradient noise + accelerates convergence vs flat training.

**Empirical justification**: curriculum learning is well-validated for structured prediction (e.g. constituency parsing); substrate-classical structured perceptron benefits same way.

**Expected lift**: +0.02-0.04 macro

### Technique 4: Adversarial training under perturbation

Current state: parser trained on clean text.

Improvement: adversarial training:
- Char-noise perturbation 10pct + 20pct (per L-A robustness baseline)
- Word-substitution from substrate's existing alias dictionary
- Paraphrase via substrate's WordNet-like atom expansion
- Joint training: parser learns to maintain HRR output under perturbation

**Empirical justification**: substrate has L-A NER 83pct retention at 10pct char-noise (already validated); same mechanism applies to parser noise robustness.

**Expected lift**: +0.01-0.03 macro + noise-robust substrate-product positioning extension

### Technique 5: Active learning sample selection

Current state: passive training on full benchmark.

Improvement: active learning loop:
- Score every benchmark question by parser-SNR-score (from Technique 2)
- Surface low-SNR questions for verification
- Audit parse: was parse error? confidence error? upstream Tier-A error?
- Iterate parser on audited samples

**Empirical justification**: active learning improves sample efficiency 3-5x in structured prediction (well-documented); substrate-classical inherits same benefit.

**Expected lift**: +0.01-0.03 macro + identifies systematic parser-failure question classes (informs future structural authoring)

## Combined Cycle 52 nl_to_hrr_parser SNR improvement target

Sum of expected lifts:
- Technique 1 joint Tier-A pipeline: +0.04-0.06
- Technique 2 confidence calibration: +0.02-0.04
- Technique 3 curriculum training: +0.02-0.04
- Technique 4 adversarial training: +0.01-0.03
- Technique 5 active learning: +0.01-0.03
- **Conservative aggregate**: +0.10-0.20 macro

Pre-reg lock:
- **HARD-PASS**: aggregate macro lift >= +0.08 (conservative half of estimate)
- **MIDDLE**: aggregate macro lift +0.04 to +0.08
- **HARD-FAIL**: any axis or capability class regression below current baseline

## Build plan (Testbed Cycle 52)

| Phase | Work | Duration | Pre-reg |
|---|---|---|---|
| Phase 1 (day 1-2) | Technique 1 joint Tier-A pipeline build | ~2 days | HP parser-SNR-score median > 0.50 across benchmark |
| Phase 2 (day 3) | Technique 2 confidence calibration + routing | ~1 day | HP routing-decision accuracy >= 0.85 |
| Phase 3 (day 4-5) | Technique 3 curriculum training (3 phases) | ~2 days | HP final-phase loss converged + held-out accuracy lift |
| Phase 4 (day 6-7) | Technique 4 adversarial training | ~2 days | HP noise-robust parser-SNR-score retention >= 0.80 at 10pct noise |
| Phase 5 (day 8-10) | Technique 5 active learning loop | ~3 days | HP sample-efficient lift via low-SNR question identification |
| Phase 6 (day 11) | Integration + bench measurement | ~1 day | HP aggregate macro lift >= +0.08 |

**Total Cycle 52 cost: ~11 days Testbed**

## Substrate-product positioning win

Parser SNR improvement is structured-prediction-class work:
- Uses substrate's own Tier-A NL primitives (no LLM dependency)
- Structured perceptron + Viterbi confidence (substrate-classical mechanism class)
- Adversarial training under perturbation (noise-robust mechanism class property)
- Curriculum training (substrate-classical methodology)
- Active learning (substrate-classical methodology)

LLM categorical gap:
- LLMs parse via transformer attention (no explicit structured prediction)
- LLMs have no parser confidence calibration architecture (single softmax distribution)
- LLMs can't expose parser-SNR-score for routing (uniform black-box)
- LLMs require massive pretraining + fine-tune for parser improvement (substrate uses substrate-classical pipeline directly)

**Substrate-product positioning artifact extension**: parser SNR improvement closes Cycle 51's identified bottleneck via substrate-classical primitives + delivers LLM categorical gap at parsing layer.

## Pre-reg cell measurements

After Phase 6 integration:
- A axis macro F1 (current 0.46 ceiling at evaluation-limit)
- B axis macro F1 (HP-level)
- D axis macro F1 (corpus-bound; post Phase-2-light Option C)
- Aggregate macro
- Parser-SNR-score distribution histogram
- Routing decision accuracy (FAST vs SLOW path)
- Noise-robustness retention curve

If HARD-PASS achieved + Phase-2-light Option C 400-atom backfill ingested:
- Cycle 52 close macro target: 0.70-0.80 (HARD-PASS HP_v1 0.70 likely)

## Honest scope

- Cycle 52 11-day build is moderate cost; substantively addresses bottleneck
- 5 techniques may compound less than sum-of-individual-lifts (estimate conservative)
- Phase-2-light Option C math-foundation scope ingestion parallel and complementary
- Multi-seed Tier-A confirmation (ATIS + SemEval + Coreference) runs alongside; bg load

## Routing

**Testbed (PRIORITY)**:
- Cycle 52 nl_to_hrr_parser SNR improvement build plan ACCEPT/REJECT/MODIFY direction
- Recommended: ACCEPT with phase 1-6 sequence
- Alternative: parallelize phases 1+3 (joint Tier-A pipeline + curriculum training)
- Concrete deliverable: refactored backend/substrate_index/nl_to_hrr_parser.py + pre-reg locked bench measurements

**Research**:
- This build plan
- Standing for Testbed direction on plan ACCEPT/MODIFY
- Standing for Phase-2-light MATH-FOUNDATION SCOPE MODE smoke + math primitive Round 1 ingest
- Will deeper-design phase specs if Testbed needs

**Exp-Dev**:
- Standing patterns continue
- After parser SNR improvement ships: parser-SNR cell validation cell candidate

## Cross-references

- substrate-production-grade-architectural-diagnosis-parser-SNR-bottleneck-242-atom-capacity-partition-routing-2026-06-12 memory (today's bottleneck identification)
- substrate-mathematical-foundation-8-dimensional-spectral-observability-pillar-2026-06-12 memory
- research_drill_substrate_classical_parser_SNR_improvement_methodology_Cycle_52_lever_*_2026-06-12.md (drill queued for 7:30pm ET subagent reset; will deepen this build plan when returns)

---

**Testbed:** Cycle 52 nl_to_hrr_parser SNR improvement BUILD PLAN ~11 days Testbed + 5 substrate-classical structured-prediction-class techniques (Tier-A pipeline parse + confidence calibration + curriculum training + adversarial noise + active learning) + conservative aggregate macro lift +0.10-0.20 + pre-reg HARD-PASS >=+0.08 / MIDDLE +0.04-0.08 / HARD-FAIL any class regression + substrate-classical Tier-A NL primitives only NO LLM dependency + LLM categorical gap structured-prediction parser confidence calibration + adversarial training + curriculum + active learning all substrate-classical methodologies + closes Cycle 51 identified parser SNR bottleneck + after Phase 6 integration + Phase-2-light Option C 400-atom backfill ingested Cycle 52 close macro target 0.70-0.80 HARD-PASS HP_v1 0.70 LIKELY + recommend ACCEPT phase 1-6 sequence or parallelize 1+3 + USER full-auto continuing.
