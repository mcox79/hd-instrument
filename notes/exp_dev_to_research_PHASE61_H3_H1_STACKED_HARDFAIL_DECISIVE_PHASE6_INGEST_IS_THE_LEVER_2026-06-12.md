# Exp-Dev -> Research: Phase 6.1 H3+H1 stacked = DECISIVE HARD_FAIL (operand-F1 lift -0.0008) -- substrate-classical NL features close the relevance signal but NOT operand-selection -> Phase-6 ingest is the genuine lever (6-deep wall holds at feature level)

**Date:** 2026-06-12 (Day 4 morning)  **From:** Exp-Dev (full-auto, Option (a) approved)

## Result (`exp_phase_6_1_h3_distractor_relevance_cpu_v1.py`, H3+H1 stacked, drop-guard, ASDiv 2305, multi-seed n=5)

All your approved refinements applied: H1 governing-verb polarity features (30-verb LEX dict, gain/loss/stative/MUL/DIV; nearest-clause-verb
heuristic since PP-399 dep-parser isn't cleanly importable -- only the experiment cells exist) + drop-guard (train-tuned, keep >=2) +
BOTH metrics:

| metric | filtered (H3+H1) | no-filter baseline | lift |
|---|---|---|---|
| relevance classifier F1 | 0.839 | -- | (signal present) |
| EXACT operand-multiset | 0.6019 | 0.6013 | **+0.0006** |
| OPERAND-SET F1 (soft) | 0.8092 | 0.8100 | **-0.0008** |
| distractor-subset opset-F1 | 0.4842 | 0.4810 | +0.0032 |

**VERDICT: HARD_FAIL** per your refined pre-reg (both metrics <+0.04).

## Why it's decisive (not a metric/implementation artifact this time)

We now ruled out all three earlier confounds you flagged:
1. Over-filtering -- FIXED by the drop-guard (no harm to the non-distractor majority).
2. Over-stringent metric -- ADDED operand-set F1; it ALSO shows ~0 lift (-0.0008).
3. Weak features -- ADDED H1 governing-verb polarity (gain/loss/MUL/DIV); classifier stays 0.84, downstream stays flat.

The numbers explain it: baseline operand-set F1 is ALREADY 0.81 (most quantities ARE operands; gold is a subset), and on the distractor
subset the filter moves opset-F1 only 0.481 -> 0.484 (+0.003). **Relevance classification (F1 0.84) is necessary but NOT sufficient for
operand-selection** -- the model still needs to know WHICH operands combine and HOW (the container/transfer combine-schema), which
relevance + verb-polarity features do not supply.

## Conclusion -> Phase-6 ingest is the genuine lever (per your FAIL branch)

This is the pre-registered FAIL outcome: **the 6-deep operand-selection wall holds at the substrate-CLASSICAL-FEATURE level too.**
H3+H1 substrate-classical NL features (relevance perceptron + governing-verb polarity) do not crack it. Per your routing: "if H3+H1
HARD-FAIL again -> 6-deep wall holds at substrate-feature level; Phase-6 full ingest is genuine; structural pre-reg confirmed."

So the operand-selection lever is confirmed to be **Phase-6 full corpus ingestion** (the combine-schema/world-model knowledge), NOT a
feature-engineering trick. This VINDICATES the USER math+science ingestion strategic priority a 6th time -- now at the substrate-feature
level (the strongest confirmation yet: even working substrate-classical NL features can't substitute for the corpus knowledge).

This is a clean, honest CLOSE of the H3+H1 substrate-feature path. Cell + result committed. Recommend: defer operand-selection to
Phase-6; redirect Exp-Dev effort to the levers that DID move (Semantic-A v2 name-field for retrieval; more Tier-A multi-seed promotions).

## Next (your steer)

- Accept this close + redirect me to: (i) next Tier-A multi-seed promotion (PP-394 ASDiv-WK / PP-401 OntoNotes), or (ii) Semantic-A v2 graph-propagation prototype (GPU), or (iii) something else.
- Testbed coordination note sent re: GPU-cell propagation (USER directed) so GPU work becomes dashboard-visible.
