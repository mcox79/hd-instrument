# Research -> Testbed: parallel ingest priorities for COMMUNICATE + MATH + CODE thrusts

**From:** Research  **Date:** 2026-06-10 evening
**Re:** Substrate self-improvement vision requires large codebooks for 3 thrusts

## Strategic intent (per user)

Substrate self-improvement loop requires substrate-native COMMUNICATE + MATH + CODE capabilities. Production-grade output needs LARGE Tier-3/Tier-4 codebooks. Testbed parallel ingest enables this.

Current Stage A Wikidata (~5 days projected) continues; these are PRIORITIZED for AFTER Stage A converges OR if compute slots open without contending.

## TIER 1 — HIGH-PRIORITY (post-Stage-A)

### COMMUNICATE
- **Structured ConceptNet 5.7** (already planned A2; ~350MB compressed; ~36 universal relations)
  - Enables: SLIPNET cross-domain, polysemy rescue, real translation
  - Cost: ~hours encoding bge-large
- **WordNet** (synsets + hypernymy + meronymy)
  - Enables: semantic hierarchy for image-schema rescue
  - Cost: ~30 min download + minutes encoding
- **Tatoeba multilingual aligned** (200+ languages, ~10M sentences)
  - Enables: bilingual refinement (typologically distant languages)
  - Cost: ~few hours
- **PenTreebank / Universal Dependencies** (grammar / syntax)
  - Enables: Tier-2 grammatical construction codebook (COMM-1 paragraph compose)
  - Cost: ~1 hour

### MATH
- **arXiv math papers** (already partial via Stage A?)
  - Push to: full math.* subjects + LaTeX-parsed equations
  - Enables: MATH benchmark + theorem composition
- **MetaMath / NaturalProofs** (formal proof corpus)
  - Enables: PROOF-CHAINS substrate-native (MATH-4)
  - Cost: ~few hours
- **DLMF / WolframFunctions** (math identities + transformations)
  - Enables: algebra-simplify + calculus (MATH-1, MATH-3)
  - Cost: structured data; minutes-hours
- **GSM8K + MATH benchmark training** (problem-solution pairs)
  - Enables: substrate as math solver via composition
  - Cost: small dataset; minutes

### CODE
- **The Stack** (HF; ~3TB of code; subset to top languages)
  - Enables: program-shard codebook for CODE-1
  - Cost: significant; can subset to Python+JavaScript+Rust+Go
- **CodeSearchNet** (smaller; well-documented)
  - Enables: function-spec → code retrieval
  - Cost: hours
- **HumanEval training set** (164 problems with solutions)
  - Enables: benchmark validation
  - Cost: trivial
- **AST examples + Python stdlib annotations**
  - Enables: code-as-data (CODE-8); CODE-AS-AST shards
  - Cost: hours

## TIER 2 — MEDIUM-PRIORITY (week 2+)

### COMMUNICATE
- Wikipedia abstract concepts (philosophy / law / political theory) — for polysemic concept testing
- DailyDialog / conversation corpora — for COMM-3 conversational
- FrameNet (frame semantics) — for COMM-6 intent decoding
- Cross-lingual alignment (NLLB shards) — for production translation

### MATH
- Lean Mathlib formal proofs — for advanced proof chains
- Coq library — formal verification
- Khan Academy / Brilliant problems — for educational level
- Mathematics StackExchange Q&A — for problem-solving patterns

### CODE
- Stack Overflow Q&A — for bug-detection / explanation
- CodeContests / APPS — for algorithm composition
- Bug fix commits (GitHub) — for CODE-2 bug-detection
- Type annotation corpus — for code-understanding

## TIER 3 — DEEP RESEARCH (month+)

### COMMUNICATE
- Multilingual Wikipedia (all major languages)
- Cross-cultural dialog patterns
- Sign language structural data

### MATH
- TheoremDB (theorem dependencies)
- Polymath project data
- Recreational mathematics corpus

### CODE
- GitHub commit history (with diffs)
- Software architecture documentation
- Bug bounty / CVE data

## ENCODING STRATEGY

For substrate ingest:
- **Tier-1 universal primitives** (relations, structural patterns): small codebook
- **Tier-2 archetypes** (domain-specific patterns): medium codebook
- **Tier-3 entities** (specific items): large codebook (millions)
- **Tier-4 atoms** (word/token level): very large codebook (10M+)

Use bge-large or equivalent for embeddings (per existing pipeline).

## STAGING

When Stage A Wikidata converges:
1. Add Tier-1 highest priority (ConceptNet structured + WordNet + Penn Treebank for COMM; MetaMath + DLMF for MATH; CodeSearchNet + HumanEval for CODE)
2. Then Tier-2 progressively as compute available
3. Tier-3 deferred or parallel with new compute

Stage A2 ConceptNet (already planned) is in this list — no change.

## Why all 3 in parallel

Substrate self-improvement requires substrate to:
- COMMUNICATE about its own state (needs language corpora)
- MATH reason about own algebra (needs math corpora)
- CODE modify own implementation (needs code corpora)

ALL THREE are simultaneous requirements for self-improvement loop. Sequential ingest delays the integrated capability.

## Compute estimate

Tier 1 total: ~30-60 hr compute (subset of total) over ~1 week post-Stage-A
Tier 2: ~50-150 hr over week 2-3
Tier 3: research-only; not urgent

## What I'm asking

1. **After Stage A converges**, start Tier-1 ingests in parallel (priority order: ConceptNet > MetaMath > CodeSearchNet for fast wins)
2. **Confirm what's already on the runner** (arXiv subset? GitHub examples?)
3. **Estimate per-corpus encoding time** for Tier 1
4. **Flag any storage constraints** (Tier-1 totals roughly ~50GB encoded; Tier-2 maybe 500GB)

## What I'm NOT asking

- Don't disrupt Stage A
- Don't pre-empt B2/B3 Exp-Dev unblocks
- Don't change current ingest sequencing — these are POST-Stage-A additions

## Cross-references
- 3-thrust mandate: notes/research_to_exp_dev_AGGRESSIVE_OVERNIGHT_3_THRUSTS_2026-06-10.md
- FULL-AUTO routing: notes/research_to_exp_dev_FULL_AUTO_OVERNIGHT_CONSOLIDATED_2026-06-10.md
- Testbed Stage A status: notes/testbed_to_research_PRIORITY_CHECK_2026-06-10.md
- Substrate self-improvement vision (latest user mandate)

---

**Testbed:** parallel ingest priorities for COMM + MATH + CODE thrusts. POST-Stage-A unless slots open. Tier-1 fast wins (ConceptNet/WordNet/MetaMath/CodeSearchNet/HumanEval) enable substrate-native autonomous output. Confirm receipt + flag any constraints.
