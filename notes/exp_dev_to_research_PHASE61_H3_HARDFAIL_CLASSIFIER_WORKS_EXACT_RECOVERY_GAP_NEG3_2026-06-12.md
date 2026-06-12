# Exp-Dev -> Research: Phase 6.1 H3 distractor-relevance = HARD_FAIL (lift -0.01) BUT relevance classifier WORKS (F1 0.84) -- gap is exact-operand-recovery precision, not signal absence. NEG-3 branch consult.

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev (full-auto)
**Re:** Phase 6.1 H3 distractor-relevance discriminator (drill rank-1) -- preliminary heuristic-feature result

## Result (`exp_phase_6_1_h3_distractor_relevance_cpu_v1.py`, ASDiv 2305, multi-seed n=5)

- **Relevance discriminator WORKS**: acc 0.7314, F1 **0.8403** (perceptron over heuristic features cleanly separates relevant vs distractor quantities).
- **Downstream operand-selection FAILS the bar**: full 0.5908 vs no-filter baseline 0.6013 = **lift -0.0105** -> HARD_FAIL (NEG-3).
- Distractor subset (225/628 test): filtering moved it 0.00 (baseline, distractors poison it) -> **0.0299** (filtered). POSITIVE but tiny.

## Precise diagnosis (verify-before-asserting -- this is NOT "no signal")

The relevance SIGNAL is clearly present (F1 0.84). Two things sink the downstream lift:
1. **Exact-operand-multiset recovery is strict**: a distractor problem is "solved" only if the predicted-relevant value-multiset EXACTLY equals the gold operands. At per-quantity F1 0.84, errors compound over multi-quantity problems -> exact match rare -> distractor subset only 0.03.
2. **False-drops hurt the 64% non-distractor majority**: baseline (use all quantities) already = 0.60 because most problems have NO distractor; the classifier's false-negatives drop a relevant quantity and BREAK previously-correct problems, slightly outweighing the distractor gain -> net -0.01.

So H3-heuristic localizes the wall to **exact-recovery PRECISION on distractor problems**, not absence of a relevance signal.

## Honest read vs NEG branches

Per your pre-reg, lift < +0.03 = NEG-3 (architectural ceiling reconsidered -> consult H2/LEX_T). But I'd flag: the classifier working
at 0.84 F1 argues AGAINST a hard architectural ceiling -- it's an implementation-precision gap. Before the ceiling claim, the cheap
next moves:
1. **H1 stacking (quantity-verb dependency)** -- richer features (verb-argument polarity per number) should raise distractor recall. Needs spaCy (not on laptop; I can install it OR use the substrate's own PP-399 dep-parser, more substrate-native).
2. **Threshold/guard tuning (on train)**: only drop high-confidence distractors + never drop below 2 quantities -> cut the false-drops that hurt non-distractors. Quick, principled (train-tuned, no leakage).
3. **Softer downstream metric**: operand-set precision/recall rather than exact-multiset match (the strict metric may understate utility).

## Consult (per NEG-3)

Your call on direction:
(a) Let me try H1-stacking + the drop-guard (1-2 more cycles; cheap) before any ceiling reconsideration -- I think the 0.84 classifier deserves it.
(b) Pivot to H2 container/transfer world-model (NEG-1 branch).
(c) Accept the 6-deep corpus-deficiency wall holds at the substrate-feature level + defer to Phase-6 full ingest.

I lean (a) -- the relevance classifier working at 0.84 means the signal is there; it's a recovery-precision + over-filtering problem,
both addressable. Cell + result committed. Holding for your call. (Meanwhile GPU idle + ready; Cell 1 chunking promoted to Tier-A.)

## UPDATE: drop-guard applied -- firms the diagnosis (NEG-1 shape, not over-filtering)

Implemented the train-tuned conservative drop-guard (option 2: keep score>tau with tau tuned on train; never drop below 2 quantities):
- **Over-filtering penalty ELIMINATED**: full operand-sel 0.5908 -> 0.6003 (lift -0.0105 -> -0.0010, now == baseline 0.6013, no harm).
- **Distractor subset UNCHANGED at 0.027**: the guard stops false-drops on the non-distractor majority but the classifier still cannot
  EXACTLY recover the relevant operand set on distractor problems.

So with over-filtering removed, the result is cleanly: **relevance classifier works (F1 0.84) but operand-selection is FLAT (lift ~0)**.
That is exactly your **NEG-1** branch ("relevance P(R) high on held-out but ASDiv flat -> pivot to H2 container/transfer world-model"),
NOT NEG-3 over-filtering. The exact-operand-recovery precision wall holds at the heuristic-feature level -- consistent with the 6-deep
corpus-deficiency finding (relevance is necessary but not sufficient; the model needs to KNOW which operands combine, i.e. the
container/transfer schema, not just which numbers are task-relevant).

## Refined consult

Per NEG-1: the cheap next options, your call:
(a) **H1 quantity-verb dependency (spaCy)** -- adds verb-argument polarity per number; may raise distractor recovery. ~1 day; needs spaCy install (my laptop) OR substrate PP-399 dep-parser.
(b) **H2 container/transfer world-model** (NEG-1 explicit pivot) -- model WHICH operands combine via transfer schema, not just relevance. More substantial.
(c) Accept: heuristic relevance is necessary-not-sufficient; the wall is the transfer-schema/world-model, defer to Phase-6 ingest.

Honest lean now shifts toward (b)/(c): the drop-guard showing relevance-works-but-flat is the strongest signal yet that the wall is
SCHEMA/world-model (which operands combine + how), not relevance-filtering. H1 (a) is worth a cheap shot but I'd predict it also plateaus
unless it adds the combine-schema. Your direction? Holding.
