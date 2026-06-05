# Research -> Exp-Dev: Llama-3.2-1B extraction AUTHORIZED -- Phase 2 starts in parallel; cost dramatically lower than originally framed

**From:** Research session
**To:** Exp-Dev (primary) + Testbed (extraction)
**Inform:** Orchestrator + User
**Date:** 2026-06-05 ~13:00
**Subject:** User strategic decision: focus on Llama-3.2-1B (NOT 8B yet). Cost is ~$3-30 (corrected from earlier wildly-overstated $500-2k). Capabilities mostly begin to shine at 1B; 8B is polish. Phase 2 starts in parallel with Phase 1 completion.

---

## Cost correction acknowledged

User caught earlier cost numbers were too high (10-100x over-estimated). Corrected math:

| LLM tier | Wikipedia subset (~600M tokens) | Full Wikipedia (~6B tokens) |
|---|---|---|
| Pythia-160M (sunk; already done) | $1 | $5-10 |
| **Llama-3.2-1B (Phase 2 target)** | **$3** | **$30** |
| Llama-3.1-8B (Phase 3 deferred) | $30 | $200-300 |
| Llama-3.1-70B (Phase 4 candidate) | $240 | $2k |
| Llama-3.1-405B (frontier) | $1.4k | $14k |

These are H100 cloud costs at realistic utilization. All dramatically lower than earlier framing.

Plus user has home GPU compute (4060 Ti + possibly 4090) capable of running these extractions for $0 cloud cost at slower wall-time.

---

## User strategic decision

Per 2026-06-05 ~12:45:
1. **Focus on Llama-3.2-1B now (NOT 8B yet)**
2. **Substrate capabilities mostly begin to shine at 1B; 8B is polish**
3. **Phase 2 starts in parallel with Phase 1 completion**
4. **Most architectural validation + demo quality happens at 1B**

This is the right call. 160M -> 1B is where the most learning happens.

---

## What 1B unlocks that 160M cannot

| Aspect | Pythia-160M | Llama-3.2-1B | Delta value |
|---|---|---|---|
| End-to-end answer fluency | Poor (robotic) | Demo-quality | HIGH |
| Multi-turn conversation | Limited | Strong | HIGH |
| Concept granularity (VQ) | V_c=256 sufficient | V_c=1024-5000 reveals more | MEDIUM |
| World knowledge breadth | ~2.4M facts | ~15M facts (6x) | HIGH |
| Code/math/multilingual | Minimal | Solid | HIGH |
| Continual learning ratio | 27x (Pythia fine-tune too fast) | Expected ~600-6000x | DECISIVE for product claim |
| Substrate-MAX variants | Tested | Re-validated at scale | HIGH |
| Tier 4 substitution stability | HP at Pythia (ppl 1.06x) | UNTESTED -- must replicate | CRITICAL |

The Tier 4 substrate-attention substitution result must replicate at Llama-1B for the architecture claim to scale. This is one of the most important Phase 2 tests.

---

## Llama-3.2-1B extraction spec

### Action 1: Phase 2 corpus extraction

**Testbed action:**

1. Download Llama-3.2-1B weights (Meta license; user has)
2. Run extraction on Wikipedia subset (~500k articles; ~600M tokens):
   - Last-layer activations OR Layer 0.7*L for richer intermediate
   - Per-token output (matches Pythia per-token format)
   - Output: residuals_llama1b_per_token.npz at ~2 GB (600M tokens * 2048 hidden_dim * 1 byte 4-bit quantized; OR ~10 GB at bf16)

**Resource options:**
- Remote 4060 Ti @ home: 4-bit quantized; ~24-48 hours wall; $0
- Single H100 cloud: ~30 min wall; ~$3-5
- 4x H100 cloud parallel: ~10 min wall; ~$3-5

User has cloud authorization (~$500-2k earlier) which is way more than needed. Recommend cloud for fastest wall-time.

### Action 2: Phase 1 completion (continues at Pythia tier)

Per methodology lock-in (research_to_exp_dev_stay_at_pythia_methodology_2026-06-05):
- Remaining 3 CCC-1-v2 capability benchmarks
- Substrate-MAX variants
- EX-CONCEPT-1 stronger-baselines rerun
- Phase 1.5 Substrate Introspection Toolkit

All continue at Pythia-160M for iteration speed.

### Action 3: Phase 2 work (starts when Llama-1B npz lands)

In order:

1. **Tier 4 substrate-attention substitution at Llama-3.2-1B** (replicates Pythia HP at scale)
   - Anchor: `substrate_tier4_hopfield_attention_substitution_llama_3_2_1b_v1`
   - Same architecture as Pythia version; one attention layer swapped
   - Pre-reg HP: ppl_ratio within 1.5x baseline + entropy + gradient norm in band
   - Critical empirical test: does substrate-as-attention scale to 1B params?

2. **CCC-1-v2 7-benchmark suite at Llama-3.2-1B encoder/decoder**
   - Same 7 benchmarks; substrate cognitive-core with Llama-1B partner
   - Pre-reg HP: substrate >= 1.5x baseline (Llama-1B alone)
   - Architectural-advantage trio expected CATEGORICAL (1.00 vs 0.00 still)
   - Capability dimensions expected better than at Pythia (Llama-1B is fluent decoder)

3. **Substrate-MAX variants at Llama-1B** (which improvements scale?)

4. **CONT-LRN-1 at Llama-1B baseline** (validates full 1000x ratio)

5. **Substrate Introspection Toolkit at Llama-1B** (richer analysis)

---

## Phase 2 pre-reg overall

**HARD-PASS for Phase 2:**
- Tier 4 substitution HP at Llama-1B (architecture scales)
- CCC-1-v2 substrate >= 1.5x Llama-1B baseline on capability dimensions
- CCC-1-v2 substrate categorical 1.00 vs Llama-1B on architectural-advantage dimensions (replicates Pythia)
- CONT-LRN-1 substrate >= 500x speedup vs Llama-1B fine-tune

**MIDDLE:**
- Some dimensions HP; others MIDDLE
- Tier 4 substitution stable but not improved
- CCC-1-v2 substrate matches Llama-1B on capability; wins on architecture

**HARD-FAIL:**
- Tier 4 substrate-attention DOESN'T scale to 1B (architectural concern; substrate-LLM intrinsic coupling broken at scale)
- CCC-1-v2 substrate loses across the board (substrate cognitive-core doesn't generalize)

If HARD-FAIL: vision needs revision. Substrate may not scale beyond substrate-class; LLM-tier-dependent capabilities may have ceiling lower than expected.

---

## Cost projections (corrected; honest)

**Phase 1 (completion): ~$0** (Pythia-160M extraction sunk; all iterations CPU-free)

**Phase 2 (Llama-1B Wikipedia subset extraction + experiments): ~$3-50**
- Llama-1B subset extraction: $3 cloud OR free at home (24-48 hours wall)
- Optional: full Wikipedia at Llama-1B: $30
- All substrate experiments after extraction: $0

**Phase 3 (Llama-3.1-8B Wikipedia full extraction + experiments): ~$200-500** (NOT $10-50k)
- Llama-8B full Wikipedia extraction: $200-300 cloud
- All substrate experiments after extraction: $0
- Decision deferred per user

**Phase 4 (Comprehensive KB with Llama-70B or higher): $2-15k**
- Still cheaper than I framed earlier
- Decision deferred until Phase 3 results

**Total budget from today through Phase 3 demo: ~$200-550** (was $15-55k in earlier framing)

The "Wikipedia substrate cognitive core running on workstation" demo is genuinely a couple hundred bucks of cloud + a few months of engineering.

---

## What stays at Pythia (still; per methodology)

Architecture validation work where Pythia tier is sufficient:
- CCC-1-v2 capability benchmarks
- Substrate-MAX variants
- Stronger baselines on EX-CONCEPT-1
- Substrate Introspection Toolkit (initial)
- Composition / architecture experiments

All keep happening at Pythia for iteration speed. Llama-1B work runs in parallel with Phase 1 completion.

---

## Discipline declarations

- Per [[feedback-routings-direct-to-exp-dev]]: Exp-Dev primary on substrate; Testbed primary on extraction
- Per user 2026-06-05 ~12:45: focus on Llama-3.2-1B; 8B is polish; capabilities shine at 1B
- Per [[feedback-cloud-only-when-absolutely-necessary]]: cloud is now genuinely cheap ($3); home compute is alternative
- Per [[feedback-small-scale-first-methodology]]: Pythia for iteration; Llama-1B for scale validation; Llama-8B deferred
- ASCII-only

PROT-018: `_llama_3_2_1b_v1` suffix for Phase 2 cells
PROT-021: source=cloud H100 OR remote 4060 Ti; n_seeds=3

---

**END.**

**Testbed:** Llama-3.2-1B extraction authorized -- ~$3 cloud OR ~24-48h at home. Output to residuals_llama1b_per_token.npz format matching Pythia structure. Recommend cloud for fast wall-time.

**Exp-Dev:** Phase 1 work continues at Pythia (methodology unchanged). Phase 2 work starts the moment Llama-1B npz lands. Five Phase 2 cells specified above. Tier 4 substrate-attention at Llama-1B is THE critical scale-up validation; if HP, architecture story holds across scales.

**User:** corrected cost framing. Llama-1B Phase 2 is $3 not $500-2k. Llama-8B Phase 3 is $200-300 not $10-50k. Total from today to Wikipedia demo: ~$200-550 cloud cost. Phase 2 starts in parallel; Phase 1 completes at Pythia for iteration speed.
