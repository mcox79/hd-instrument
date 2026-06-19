# exp_dev hand-off -- research: substrate vs Tier-4 competitors (BABILong + CLUTRR gaps)

Filed-by: research sub-agent
Trigger: notes/research_drill_substrate_vs_competitors_tier4_2x_2026-06-07.md (2x competitive drill; two benchmark gaps identified as v1 demo blockers)
Pause state: check data/orchestrator_paused.flag before dispatching

Per [[feedback-no-experiment-design-in-prompts]]: this file provides TASK + WHY + CONTRACT + AUTONOMY. Exp_dev designs anchors, sweep parameters, thresholds, and queue placement -- NOT this file.

---

## WHY NOW

The 2x competitive drill (cycles 154-162 empirical state) identified two concrete benchmark gaps that must close before v1 demo:

1. BABILong few-shot: Titans published a score beating GPT-4 and models 70x larger. Substrate + Llama-1B has not been tested on this benchmark. Until this gap is closed, substrate cannot claim long-context competitive parity.

2. CLUTRR 3-hop kinship inference: Pattern B compositional structure (cycle 162) is directly suited for this benchmark. No competitor (Titans, Hebbian-FW, VSA-attention) has published a result here. A strong substrate score establishes the compositional moat concretely.

Both tests are ~2h GPU each, and they are the two highest-leverage pre-demo benchmarks per the competitive analysis.

---

## ANCHOR CANDIDATES (rank-ordered)

### Anchor 1 -- BABILong few-shot with Llama-1B + substrate retrieval (GPU, ~2h)
Pointer: research note Section "Benchmarks where Titans likely beats substrate today"
Substrate-product reading: BABILong tests multi-hop reasoning over long contexts with few-shot examples. Running Llama-1B + substrate retrieval on the published BABILong tasks measures whether the long-context competitive gap with Titans is real or a framing artifact. Titans achieved state-of-the-art on BABILong; substrate + Llama-1B may match via structured retrieval where Titans uses window-based memory.
Tier hint: remote GPU runner; ~2h wall; Llama-1B already validated at cycle 162
Why now: Highest-priority unknown benchmark gap. If substrate scores within 15 points of Titans MAC, the long-context competitive narrative is defensible. If substrate scores >15 points below, this becomes an engineering priority, not a product claim.

### Anchor 2 -- CLUTRR 3-hop kinship inference with Pattern B (GPU, ~1h)
Pointer: research note Section "Benchmarks where substrate wins definitively"
Substrate-product reading: CLUTRR tests systematic compositional generalization for kinship chains. Pattern B at N=4096 stores role-filler bindings for kinship triples; 3-hop inference tests whether the substrate can chain three bindings to answer unseen combinations. No competitor has a published CLUTRR result. A substrate score >60% at 3-hop establishes the compositional moat with a concrete number.
Tier hint: remote GPU runner; ~1h wall; N=4096 (already validated scale)
Why now: Second-highest-priority gap. CLUTRR is the natural benchmark for Pattern B; running it produces competitive differentiation data that no competitor can counter.

### Anchor 3 -- GDPR Art.17 erasure round-trip compliance demo (CPU, ~30 min)
Pointer: research note Section "Cheap decisive tests"
Substrate-product reading: Insert a known fact, verify it appears in retrieval, execute EDPB-3 surgical erasure, verify the fact no longer appears and the audit log records the erasure event with timestamp. This produces a compliance certificate artifact. Not a novel experiment -- validates the production compliance pipeline end-to-end.
Tier hint: laptop CPU; ~30 min wall; no GPU needed; data artifact for sales/regulatory use
Why now: August 2026 EU AI Act Art.12 deadline is 8 weeks away. A compliance demo artifact produced now gives lead time for regulatory review.

---

## CONTEXT POINTERS

Research note: d:/AI/hd-instrument/notes/research_drill_substrate_vs_competitors_tier4_2x_2026-06-07.md
Pattern B validation: cycle 162 (data/exp_*/metrics.json)
Llama-1B BASE validation: cycle 162 (per production_architecture_locked memory)
Continual learning validation: cycles 154, 162
BABILong benchmark: https://arxiv.org/abs/2406.10149 (Kuratov et al., 2024)
CLUTRR benchmark: EMNLP 2019 (Sinha et al.); HuggingFace dataset at huggingface.co/CLUTRR
Titans paper for comparison: arXiv:2501.00663 (BABILong results in Table 3 or equivalent)

---

## CONTRACT

- Exp_dev designs ALL anchor parameters, sweep grids, threshold formulas, queue placement, and ETA
- Exp_dev verifies formula self-tests before coding (per [[feedback-strategy-spec-formula-selftests]])
- Exp_dev checks queue.json for name collisions before shipping (per [[feedback-ship-name-collision]])
- ASCII-only in print()/verdict_msg (per [[feedback-ascii-only-in-scripts]])
- Progress logging for any run > 5 min wall (per [[feedback-testbed-progress-logging-and-restart]])
- Anchor 3 (erasure demo) runs on LAPTOP CPU -- numpy-only script, no GPU runner
- Anchor 1 and 2 are GPU tasks; batch them on the same cloud instance if dispatching cloud

## AUTONOMY DECLARATION

Exp_dev has full autonomy to:
- Design the exact CLUTRR loading, Pattern B query format, and accuracy metric
- Choose the BABILong subset (task types, context lengths) for the initial probe
- Set HARD-PASS / MID / HARD-FAIL bands for each anchor
- Order the anchors based on current queue depth and runner availability
- Skip Anchor 3 if queue is full and prioritize the benchmark anchors
