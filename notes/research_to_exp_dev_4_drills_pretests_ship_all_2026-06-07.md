# Research -> Exp-Dev: ship all 4-drill recommended pre-tests (8 cells, ~15 hr CPU, $0)

**From:** Research session
**To:** Exp-Dev
**Date:** 2026-06-07
**Re:** User directive "ship all recommended" — routing all pre-tests from the 4 drills
that examined frontier-LLM-wins capabilities.

All Tier A: CPU only, no cloud. Decision rules autonomous unless flagged BORDER.

---

## From parametric knowledge + synthesis 2x drill

### 1. NQ + TriviaQA Wikipedia substrate vs bare Qwen pre-test
(Already routed separately at notes/research_to_exp_dev_nq_triviaqa_wikipedia_pretest_2026-06-07.md;
flagging for explicit queue position)

Wall: 1-2 hr CPU.

---

## From reasoning + math + code 2x drill (3 cells)

### 2. K-hop audit replay (highest priority; demo asset)
20 multi-hop questions; substrate K-hop produces auditable chain with Merkle proofs per
step; replay each chain (re-run same inputs; verify same outputs); verify each Merkle
proof; compare to LLM chain-of-thought which is known non-deterministic.

HARD-PASS: 100% deterministic chain replay; 100% Merkle verification; LLM CoT shows
divergence between runs.

Wall: ~30 min CPU.

Why highest priority: demo asset for regulated-industries pitch. The chain-replay
showcase is the "look at this" moment.

### 3. HumanEval stdlib-class split
Index Python stdlib docs + common code patterns in substrate; split HumanEval into
stdlib-class vs novel-algorithm-class; substrate-augmented Qwen vs bare Qwen on
stdlib-class subset.

HARD-PASS: substrate-augmented Qwen pass@1 >= bare + 0.10 on stdlib-class.

Wall: ~2 hr CPU.

### 4. GSM8K formula-class split
Index 200 math identities + derivation patterns; split GSM8K into formula-class vs
novel-problem; substrate-augmented Qwen vs bare on formula-class.

HARD-PASS: substrate-augmented Qwen accuracy >= bare + 0.10 on formula-class.

Wall: ~3 hr CPU.

---

## From multimodal + multilingual 2x drill (1 cell)

### 5. Bipolar quantization quality for dense vision/multilingual embeddings at N=1024
The drill identified this as the SOLE empirical gate for "substrate matches frontier on
multimodal/multilingual STORAGE + RETRIEVAL." If bipolar quantization preserves
sentence-transformer embedding quality at N=1024 substrate dim, substrate + CLIP /
multilingual-e5 wins on retrieval the same as text.

Method: generate 1000 dense vision embeddings via CLIP and 1000 multilingual embeddings
via multilingual-e5; quantize to bipolar at varying substrate N values {512, 1024, 2048,
4096}; measure cosine retrieval quality vs full-precision baseline.

HARD-PASS: bipolar at N=1024 preserves recall@10 within 5% of full-precision baseline
for BOTH vision and multilingual.

Wall: ~2 hr CPU.

---

## From long context + ICL + UX 2x drill (3 cells)

### 6. Pattern B ICL N-scaling pre-test
Pattern B analogy mode failed at acc=0.041 at k=4 at toy N=1024. Test at production N
{8192, 32768, 65536} for 5-way classification with k=5.

HARD-PASS: acc >= 0.40 at production N (Pattern B ICL parity claim survives).
HARD-FAIL: acc < 0.15 at production N (Pattern B's ICL analog doesn't transfer; sparse-
KEY vocab injection becomes the backup ICL claim).

Wall: ~1-2 hr CPU.

### 7. Ingestion latency for 390-chunk document
The "long context vs stored facts" crossover depends on ingestion cost. Measure substrate
ingestion time for a representative 100K-token document chunked into 390 ~250-token
passages.

HARD-PASS: ingestion < 30 seconds.
HARD-FAIL: ingestion > 5 minutes (substrate not viable for per-session document workloads).

Wall: ~30 min CPU.

### 8. Cost crossover at 20 queries on 100K-token doc
At what query density does substrate become cheaper than long-context LLM? Drill predicted
crossover ~10 queries / 100K ctx; verify with concrete cost numbers.

Method: 100K-token document; 20 queries; compute substrate cost (ingestion + 20 retrievals
+ 20 small-LLM generations) vs long-context LLM cost (20 calls with 100K ctx each); use
published pricing.

HARD-PASS: substrate < 50% of long-context LLM cost at 20 queries.

Wall: ~30 min CPU (mostly arithmetic + a couple of test queries).

---

## Sequencing

Tier 1 (highest demo value; ~30 min CPU each):
- K-hop audit replay (demo asset for regulated)
- Ingestion latency (gates long-context-vs-substrate cost crossover claim)
- Cost crossover (~30 min)

Tier 2 (benchmark / coverage validation; 1-3 hr each):
- NQ + TriviaQA Wikipedia (1-2 hr; tests the 70-85% encyclopedic coverage claim)
- HumanEval stdlib-class (2 hr)
- GSM8K formula-class (3 hr)
- Bipolar quantization for vision/multilingual (2 hr)

Tier 3 (Pattern B production-N; 1-2 hr):
- Pattern B ICL N-scaling (gates the ICL parity claim)

Total wall if parallelized: ~3-5 hours; $0.

## What this battery validates

- Substrate covers 70-85% of encyclopedic queries (NQ + TriviaQA)
- K-hop audit replay is a categorical regulated-industries win (demo asset)
- Substrate-augmented small LLM competitive on stdlib code (HumanEval)
- Substrate-augmented small LLM competitive on formula-class math (GSM8K)
- Substrate handles multimodal + multilingual via bipolar quantization
- Pattern B ICL parity at production N (or definitively closed)
- Substrate ingestion is fast enough for per-session document workloads
- Substrate cost crossover with long-context LLM at sensible query density

After this battery, the customer pitch can be confidently revised across all 9 capability
axes the user pushed back on.

## Cross-references

- Parametric knowledge + synthesis 2x: notes/research_drill_parametric_knowledge_synthesis_2x_2026-06-07.md
- Reasoning + math + code 2x: notes/research_drill_reasoning_math_code_2x_2026-06-07.md
- Multimodal + multilingual 2x: notes/research_drill_multimodal_multilingual_2x_2026-06-07.md
- Long context + ICL + UX 2x: notes/research_drill_longctx_icl_ux_2x_2026-06-07.md
- NQ + TriviaQA pre-test (already routed): notes/research_to_exp_dev_nq_triviaqa_wikipedia_pretest_2026-06-07.md
- Reasoning + code 3 pretests (already routed): notes/research_to_exp_dev_reasoning_code_3_pretests_2026-06-07.md

---

**END.**

**Exp-Dev:** ship all 8 cells per Tier 1/2/3 sequencing. K-hop audit replay (demo asset)
is highest priority. Apply HARD-PASS / HARD-FAIL decision rules autonomously per cell.
File synthesis when batches complete.
