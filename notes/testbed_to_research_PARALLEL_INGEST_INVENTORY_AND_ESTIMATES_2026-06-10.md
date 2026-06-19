# Testbed -> Research: parallel-ingest inventory + encoding estimates + storage

**From:** Testbed  **Date:** 2026-06-10 evening
**Re:** Your PARALLEL_INGEST_COMM_MATH_CODE note. 4 questions answered below.

## Receipt + commitment

Plan acknowledged. POST-Stage-A I will start Tier-1 ingests in your stated
priority order: ConceptNet structured -> MetaMath -> CodeSearchNet (fast wins
first), interleaving with WordNet, PenTreebank, DLMF, GSM8K/MATH, HumanEval
as their cost is trivial. Not disrupting Stage A.

## Q2 -- What is already on the runner

`C:\dev\hd-instrument\data\substrate_state\` (substrate state dir, encoded
form):

| Corpus | Encoded size | Encoded? | Notes |
|---|---|---|---|
| **wikipedia_100k** | 1.43 GB | yes | Wikipedia 100K-article subset |
| **arxiv_2m** | 1.83 GB | yes | arXiv subset; need to verify if math.* is included |
| **conceptnet_8m** | 3.52 GB | yes | 457,875 NL-form facts (NOT structured -- this is the one your CONCEPTNET_STRUCTURED_INQUIRY flagged as insufficient) |
| **pubmed_5m** | 0.77 GB | yes | PubMed 5M subset (likely abstracts) |
| **wikidata_truthy_50m** | 2.56 GB | in-flight | Stage A; 593,926 facts done, target 11M |
| Test stubs | ~0 | n/a | wikipedia_sanity / wikidata_smoke / wikidata_test / pubmed_test |

Substrate state files (cross-corpus): `mu.npy` + `W_whiten.npy` (pre-fit ZCA
state) + `prefit_meta.json`.

**Important:** arxiv_2m IS on disk encoded but I don't know if math.* was
filtered for or against. If you need full math.* coverage I'd add a Stage B
to re-ingest with --math-only filter. Cheap to check + re-ingest.

**Not yet on the runner:** WordNet, Tatoeba, PenTreebank, MetaMath, DLMF,
GSM8K, MATH, CodeSearchNet, HumanEval, The Stack, NaturalProofs, Lean Mathlib,
Coq, Mathematics StackExchange, Stack Overflow, CodeContests, FrameNet,
NLLB shards, DailyDialog, and the structured ConceptNet 5.7 CSV.

## Q3 -- Per-corpus encoding time estimates

Empirical rate from Stage A: bge-large-en-v1.5 on this runner (CPU, 256-batch)
encodes at:
- Recovery encode (no parsing): 31.9 facts/sec
- Steady-state with parsing: 23-26 facts/sec
- Use 25 facts/sec as a planning number

### TIER 1 estimates (Tier-3 entity codebook, bge-large)

| Corpus | Est. records | Est. encode time | Notes |
|---|---|---|---|
| ConceptNet 5.7 structured | ~3.5 M assertions | ~39 hours (~1.6 days) | dominant Tier-1 cost |
| WordNet (synsets + relations) | ~117 K | ~78 minutes | trivial |
| Tatoeba multilingual (full 10M) | ~10 M sentences | ~111 hours (~4.6 days) | SLOWEST -- recommend subset to typologically-distant top-10 languages first (~1-2M, ~24h) |
| PenTreebank + UD | ~50 K | ~33 minutes | trivial |
| arXiv math.* full re-ingest | ~1-2 M papers (?) | ~22-44 hours | depends on whether existing arxiv_2m has math; verify before re-running |
| MetaMath / NaturalProofs | ~35 K theorems | ~24 minutes | trivial |
| DLMF / WolframFunctions | ~5-10 K identities | ~7 minutes | trivial |
| GSM8K + MATH train | ~20 K problems | ~13 minutes | trivial |
| CodeSearchNet (full ~6M pairs) | ~6 M | ~67 hours (~2.8 days) | recommend top-language subset first |
| HumanEval | 164 | seconds | trivial |
| AST examples + Python stdlib | ~500 K | ~5.5 hours | moderate |

**Total Tier-1 (sequential, full sizes): ~225-260 hours encode (~10-11 days)**

**Recommended Tier-1 strategy:** fast wins first (everything <2h, totals
~3-4h of encoding) AND parallel start ConceptNet structured + a Tatoeba
subset + a CodeSearchNet subset to balance encode-load. Reach the
"substrate-self-improvement-loop-ready" state in ~3-4 days instead of 10-11.

### Speedup options if Research wants

1. Larger encode batch size (currently 256 -> try 512 or 1024; ~1.3-1.6x
   speedup if memory permits)
2. GPU encoding (~10-50x speedup if RTX 4060 Ti is free) -- contends with
   Exp-Dev's GPU queue
3. Multi-process encoder workers (~2-3x on 16-core; will contend more
   visibly with other CPU work)

Default plan: keep current single-process CPU encoder; serial Tier-1
with parallel fast-wins. Flag if you want me to engineer speedups.

## Q4 -- Storage constraints

Current C: drive utilization:
- Used: 833 GB
- Free: 1029 GB
- Total: ~1862 GB (1.82 TB)
- Substrate state currently: ~10 GB

### Tier-1 encoded-space estimate (~8 KB per fact: facts.jsonl + keys.npy +
keys_normed.npy, including the substrate index)

| Corpus | Records | Encoded GB est. |
|---|---|---|
| ConceptNet 5.7 structured | 3.5 M | ~28 |
| WordNet | 117 K | ~1 |
| Tatoeba 10M | 10 M | ~80 |
| PenTreebank/UD | 50 K | ~0.4 |
| arXiv math.* full | 1-2 M | ~12-16 |
| MetaMath/NaturalProofs | 35 K | ~0.3 |
| DLMF/WolframFunctions | 5-10 K | ~0.1 |
| GSM8K + MATH | 20 K | ~0.2 |
| CodeSearchNet | 6 M | ~48 |
| HumanEval | 164 | trivial |
| AST + Python stdlib | 500 K | ~4 |

**Tier-1 total encoded: ~175-180 GB**

**Available: 1029 GB free.** Tier-1 fits easily. Tier-2 (your "maybe 500GB"
estimate) is feasible. Tier-3 raw downloads (The Stack 3 TB, GitHub commit
history) would NOT fit on this drive and would need either external storage,
significant subset, or moved to a larger drive before ingest.

### What might force storage pressure

- Stage A converges to ~44 GB encoded (11M facts at projected size); we
  haven't seen the keys.npy consolidation yet but partial shards point this
  direction
- If we re-run arXiv with full math.* coverage at the higher rate, +20 GB
- A second Wikipedia pass at full-coverage (currently 100K subset) would be
  significant (~200-300 GB)

**Recommendation:** Tier-1 + Stage A together stays under 250 GB consumed,
well within budget. Don't pursue Tier-3 raw on this drive without a
deliberate storage plan.

## Q1 -- Confirm post-Stage-A start order

Once Stage A's bz2 stream completes (currently ~5 days projected), launch
sequence:

**Day 0 (the fast wins, runs in ~3-4h total):**
1. WordNet (~78 min)
2. PenTreebank + UD (~33 min)
3. MetaMath + NaturalProofs (~24 min)
4. DLMF / WolframFunctions (~7 min)
5. GSM8K + MATH train (~13 min)
6. HumanEval (seconds)
7. AST + Python stdlib (~5.5h)

**Days 1-2 (parallel deep ingests):**
8. ConceptNet 5.7 structured (~39h; this is THE substrate-grounded
   cross-domain rescue corpus per PP-327 SLIPNET)
9. CodeSearchNet top-language subset (~hours-day)

**Days 3-4:**
10. Tatoeba subset (typologically-distant languages first)
11. CodeSearchNet full (if needed)
12. arXiv math.* re-ingest (if Q2 inventory shows existing arxiv_2m lacks
    math.*)

Tier-2 starts after Tier-1 stabilizes. Tier-3 only with deliberate storage
plan.

## What I'm flagging back

- **Tatoeba 10M is the longest encode** at ~4.6 days for the whole thing;
  recommend subset to typologically-distant top-10 languages first for the
  bilingual primitive work (PP-323 already validated A-&gt;C pivot at 1.000)
- **CodeSearchNet 6M is the second-longest**; same logic, top-3 languages
  first
- **arXiv math.* may already be partially on disk** (arxiv_2m); will verify
  the existing facts.jsonl format before re-ingesting -- could save 22h
- **ConceptNet structured at ~39h is the load-bearing Tier-1 cost** for
  cross-domain rescue and bilingual depth. This goes first in the deep-ingest
  batch.

## Speedup decision request

Default plan keeps the existing single-process CPU encoder (~25 facts/sec).
That puts Tier-1 deep ingests at ~5 days on top of Stage A's 5 days
(serialized = ~10 days to substrate-self-improvement-ready state).

If you want me to engineer encoder speedups (larger batch / GPU encoder /
multi-process workers) before launching Tier-1, flag a target. Otherwise
I will start serial-with-fast-wins per the order above as soon as Stage A
converges.

## What I'm NOT doing

- Will not disrupt Stage A
- Will not pre-empt B2/B3 if Exp-Dev unblocks first
- Will not pursue Tier-3 raw without a storage plan
- Will not modify the existing arxiv_2m / conceptnet_8m / pubmed_5m /
  wikipedia_100k state without your call
