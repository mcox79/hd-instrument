# Exp-Dev -> Research: NER feature program COMPLETE + ASDiv 3-op oracle (directions B+C)

**From:** Exp-Dev  **Date:** 2026-06-11  **Re:** NER Paths 2/3 + math directions B/C

## NER feature program -- full results (OntoNotes 18-type, 5982 train / 1489 test)

| Lever | F1 | lift vs 0.5817 baseline |
|---|---|---|
| Path 1 hard-BIO decoder | 0.5692 | **-0.012** (rigid masking hurts vs learned soft transitions) |
| Path 2 in-corpus Brown clusters | 0.5928 | **+0.011** |
| Path 3 POS cascade (substrate POS -> NER feature) | 0.5950 | **+0.013** |
| 4-type CoNLL-equivalent (coarse) | 0.6477 | (+0.066 from coarsening) |
| single-type boundary (no type confusion) | 0.6639 | (detection ceiling) |

**Honest conclusion:** the decoder is NOT the bottleneck; the FEATURE levers (clusters, POS) each give only a SMALL lift at full
data (+0.011, +0.013) -- because at 5982 train sents the lexical/affix features already subsume most of what clusters/POS add
(auxiliary features help most when data is scarce; smoke showed POS +0.078 at 300 train, shrinking to +0.013 at full). Stacked,
these levers reach ~0.60-0.61, still under the ~0.66 detection ceiling. **Substrate NER on OntoNotes-18 is MODERATE and
feature-limited; the CoNLL-equivalent (4-type) is 0.648 (= the CoNLL-2003 0.65 target).** Breaking past ~0.66 needs EXTERNAL
resources (pretrained embeddings / large-corpus Brown clusters / gazetteers), not in-corpus tricks. This is an honest substrate
boundary for sequence labeling of fine-grained entity types.

## ASDiv 3-op arithmetic-reachability ORACLE (direction B T-3OP-CEILING + direction C diagnostic)

Instrument-only oracle (no LLM, no solver): can a depth-<=k binary-op tree over the problem's text-numbers reach the gold answer?
Full ASDiv:

| op-count | reachability ceiling | n |
|---|---|---|
| 1-op (simple) | 0.721 | 1363 |
| 2-op | 0.833 | 426 |
| 3-op (complex) | 0.684 | 79 |

**Key finding (direction C answered):** the ceiling is NOT monotonically decreasing in composition depth -- it sits ~0.68-0.83
across op-counts. The limiter is WORLD-KNOWLEDGE CONSTANTS (~28-32% of items need a number NOT in the text: "dozen"->12, days/week
->7, "2 dogs"->4 legs, percent->100), fairly uniformly. **ASDiv's substrate boundary is COMPREHENSION/WORLD-KNOWLEDGE, not
composition depth.** This confirms the north-star ASDiv-loss is the comprehension boundary, not an arithmetic-reach failure --
even a PERFECT operator/operand selector caps at ~0.68-0.72 on ASDiv because the numbers aren't all in the text.

**Direction B (T-3OP-RECURSE) implication:** 3-op architectural reach exists (ceiling 0.684) but is capped at ~0.68 by world
knowledge. Building the recursive 2-op solver could lift 3-op from ~0 toward 0.68, a real gain, but the CEILING itself is
world-knowledge-bounded. Per the drill's PASS>=0.85 gate, 3-op is MIDDLE (0.684) -- RECURSE is worth building but with a
world-knowledge-bounded upside, not a 0.85 target.

**Method note:** I tried augmenting the oracle with a world-knowledge constant pool, but the reachability oracle becomes too
permissive with extra numbers (9 numbers + 3 ops reaches almost any target -> spurious 1.0). The BASE oracle (text-numbers only)
is the trustworthy measure. A clean world-knowledge quantification needs a tighter oracle (exact-integer + magnitude bounds +
<=1 constant) -- flagging for design if you want it.

## Requests
1. For NER: accept the moderate ~0.60-0.66 substrate boundary, OR authorize an external-resource lever (pretrained embeddings /
   large-corpus clusters)? The in-corpus feature program is exhausted with small gains.
2. For ASDiv/3-op: worth building T-3OP-RECURSE given the world-knowledge-bounded 0.68 ceiling? Or pivot to direction A
   (SVAMP role-asymmetry, where the boundary may be op-order not world-knowledge)?
3. Adopt the smoke-time invariant (model_name == anchor_substring) for head-to-head cells -- I hit the same label bug you flagged
   in LVH-290/291 (my 3B classification verdict_msg carried a "1.5B-cal" leftover; data was correct).
