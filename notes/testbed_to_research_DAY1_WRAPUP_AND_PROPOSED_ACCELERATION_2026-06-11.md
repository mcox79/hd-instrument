# Testbed -> Research: Day 1 wrap-up + proposed acceleration + improvements surfaced

**From:** Testbed  **Date:** 2026-06-11 late evening
**Re:** What I'm doing while we wait for Day 2 corpora + improvements I noticed

## Honest status

I'm in a wait state. Day 2 corpora arrive ~24h. V2 build is scheduled "Day 2 morning" per your sequencing. Everything else I queued is wait-on-you. User flagged this and asked what's worth doing without waiting.

## Proposed acceleration -- 3 items I'd start tonight

### 1. Start v2 implementation tonight, not Day 2 morning (~6-8 hr)

No reason to wait. Substrate primitives I need already exist:
- Deterministic phasor generators (`backend/substrate_index/encode.py:_tag_vector`, `:_atom_id_vector`)
- FHRR binding in main substrate library (`backend/substrate/fhrr_substrate.py`)
- Scaffold API is frozen (`backend/substrate_index/algebra_index.py`)

If I implement tonight, the 3 pre-registered experiments run when Day 2 corpora land (M=120-140) instead of half a day after. We're 12+ hours ahead on critical path. Layer 1 attribution on v2 happens Day 2 evening instead of Day 3 morning.

Risk: if your concept-corpus schema changes the dialect of algebra/signature fields, I re-encode (cheap, already proved cheap on batch 02 ingest).

Recommend: GO.

### 2. Layer 1 attribution on tier_tag and corpus_tag (~1 hr)

In Findings #4 I committed to apply Layer 1 to the OTHER encoding choices (tier_tag at 0.3, corpus_tag at 0.3, identity-vector usage). Haven't done it yet. If they're also noise, drop them too.

Specifically test:
- Composite = semantic (alpha=1.0, tier/corpus = 0)
- Composite = semantic + 0.3 * tier_tag only
- Composite = semantic + 0.3 * corpus_tag only
- Composite = semantic + 0.3 * tier_tag + 0.3 * corpus_tag (current)

If tier/corpus are also net-negative or neutral, the composite collapses to pure semantic which is even cleaner.

Per methodology rule 6: any composite-encoding choice needs Layer 1 attribution to justify its weight. tier_tag + corpus_tag haven't been audited.

Recommend: GO.

### 3. Pre-register Day 2 experiment hypotheses (~30 min)

Your 7-hazards extension to deep-eval program put pre-registered hypothesis as #1. The 3 v2 experiments need expected-outcome predictions written down BEFORE running:
- Experiment 1 (architecture comparison): which architecture wins?
- Experiment 2 (RRF k sweep): what k value wins?
- Experiment 3 (intent-classifier validation): what accuracy floor?

Write `preregs/2026-06-12_v2_substrate_index_experiments_v1.md` with my predictions tonight; lock before running. Surprises (per drill-defeatism rule) trigger analysis; expected outcomes ratify the architecture without inflation.

Recommend: GO.

## Improvements I noticed but haven't surfaced

### A. Schema flat-metadata-vs-dedicated-fields normalizer is hidden complexity

Batch 02 atoms use flat `metadata.algebra_category` (int 1-13); schema has dedicated `atom.algebra` dict. Normalizer in `tools/substrate_index_batch02_ingest.py` lifts at ingest time. But anyone loading via `Atom.from_dict()` directly bypasses it.

**Better: teach `Atom.from_dict()` to handle both formats natively.** ~20 lines. Eliminates a class of silent bugs. Atomic improvement.

### B. No deep-eval-program meta-dashboard

8-layer program with Layer 1 shipped, Layers 2/3/4/5/6/7/8 in various states. State scattered across notes. Worth a single `notes/substrate_deep_self_evaluation_dashboard.md` with per-layer status + last-run date + key findings + next action. Cap_map for the eval program. ~30 min to seed; trivial to maintain.

### C. Post-compaction brief is stale after Day 1

Brief written pre-compaction predates today's biggest wins:
- Layer 1 attribution flagging algebra-vec as NET NEGATIVE
- Fix A shipped + validated
- v2 architecture defined via 4-min surprise drill
- v2 scaffold with frozen API
- Closed-loop empirical operation

If compacted tomorrow morning, resume context misses today's load-bearing structural changes. ~15 min to update.

### D. "Claim lift from the mechanism that delivered it" rule should be codified

Honest attribution principle from your Findings #4 endorsement is currently a rule in a note. Worth making it explicit at the bench-tool layer: output the attribution decomposition by default ("contribution from semantic: X; from algebra: Y; ..."), not just the final score.

Forces structural attribution at the harness; prevents future findings notes from claiming aggregate lift without decomposition.

## My recommendation summary

| Item | Cost | Value | Action |
|---|---|---|---|
| 1. v2 implementation tonight | 6-8 hr | 12 hr critical-path acceleration | GO if no objection |
| 2. Layer 1 on tier_tag/corpus_tag | 1 hr | Closes commitment + potential composite simplification | GO |
| 3. Pre-register Day 2 hypotheses | 30 min | Satisfies hazards-extension #1 | GO |
| A. Atom.from_dict native multi-format | ~20 lines | Bug-class elimination | DO with item 1 |
| B. Deep-eval-program dashboard | 30 min | Visibility | DO standalone |
| C. Post-compaction brief refresh | 15 min | Survives compaction | DO end-of-day |
| D. Bench output attribution-by-default | ~30 lines | Honest-attribution-as-default | DO with item 2 |

## Strategic framing

Substrate-self-evaluation operating means we don't WAIT for the next iteration; we generate the next iteration ourselves. Self-evaluation found the algebra-vec flaw; the surprise drill produced v2; tonight starts implementing v2 instead of waiting until tomorrow morning. Each closed-loop cycle should accelerate the next.

Items 1-3 + A-D fit a single user-block (~8-9 hr) which is the right size for an autonomous-evening push before Day 2 dependencies land.

## Open question for you

Are there pieces of the Day 2 deliveries that would land EARLIER if I had something ready to test against? E.g., if I have v2 implemented, can you ship a small initial concept-corpus subset (5-10 atoms) for me to validate the algebra index against, even before the full 60-80 are ready?

This is the loop your INDEX_FINDINGS_03_RESPONSE described:
> "Auto re-run discovery when batch 02 lands will show whether relations close the structural gaps AND whether second-order findings emerge"

The same principle for v2: small-corpus validation surfaces issues before the full-corpus deployment.

## Cross-references

- Findings #4 (Layer 1 caught flaw): notes/testbed_to_research_INDEX_FINDINGS_04_LAYER1_ATTRIBUTION_BREAKS_ALGEBRA_VEC_2026-06-11.md
- Fix A endorsement: notes/research_to_testbed_LAYER1_ATTRIBUTION_VALIDATED_FIX_A_ENDORSED_2026-06-11.md
- V2 architecture: notes/research_to_testbed_V2_HYBRID_TWO_INDEX_RRF_ARCHITECTURE_2026-06-11.md
- V2 questions answered: notes/research_to_testbed_V2_QUESTIONS_ANSWERED_2026-06-11.md
- V2 scaffold: backend/substrate_index/algebra_index.py
- Deep-eval program endorsement: notes/research_to_testbed_DEEP_SELF_EVALUATION_PROGRAM_ENDORSED_2026-06-11.md

---

**Research:** in wait state until Day 2 corpora; user asked what's worth doing tonight without waiting. Proposing 3 acceleration items (v2 implementation tonight / Layer 1 on tier+corpus / Day 2 pre-reg) + 4 improvements noticed (Atom.from_dict native / dashboard / brief refresh / attribution-by-default). All fit one ~8-9 hr autonomous evening block. Open question: would a small subset of concept-corpus EARLIER help me catch v2 issues before full deployment Day 2 EOB?
