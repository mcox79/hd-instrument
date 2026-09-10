# DEVIATION LEDGER -- every signal loss, chased top-down to its exact non-BF deviation (or missing input)

Owner's mandate: if a component loses signal, something is not mathematically BF -- chase it and understand it,
top-down. Rigorous refinement, held throughout: a loss is ONE of three things, and each is pinned with a number:
- **(D) fixable non-BF DEVIATION** -- a component computes something OTHER than the brain's operation; making it
  BF RECOVERS the signal.
- **(M) MISSING INPUT** -- every operation is BF, but the chain lacks a signal the brain has (grounding, meaning);
  no operation-fix recovers it; the BF-from-text alternative is actually WORSE than the non-BF foundation.
- **(0) masked deviation** -- the operation deviates from the brain's, but it costs ~0 signal here (the input
  already carries the answer, or the posterior is peaked so hard==graded).

## The trace, top-down

### 1. TOKENIZE -- deviation type (0)
Whitespace/regex split (not the brain's Saffran statistical segmentation). LOSS ~0. WHY: spaced English text
PRE-ENCODES the word boundaries in the input, so the deviation costs nothing on the actual input (verified:
the BF TP-segmenter recovers boundaries F1 0.64 from UNSPACED text, i.e. the info is there; on spaced text
the boundaries are given). **Understood: a non-BF operation that loses no signal because the input carries the answer.**

### 2a. POS -- DECODE (hard Viterbi) -- deviation type (0)
Hard-Viterbi max-product discards the posterior (a real deviation from the brain's graded category belief).
Chased (`exp_parser_deviation_chase_v1`): UAS(exact marginal-argmax POS) - UAS(Viterbi POS) = **+0.0002** ~ 0;
POS token acc identical (0.9443 vs 0.9444). WHY: the POS posterior is PEAKED (87% of mistags are CONFIDENT,
margin>=0.5), so hard == graded. **Understood: BF-equivalent here; the hard decode is NOT the deviation that
loses signal.** (The exact graded posterior is still built + BF; it just doesn't change the point estimate.)

### 2b. POS -- ACQUISITION (frozen supervised weights) -- deviation type (M, mostly) + (D, small)
The whole POS-link loss (**2.97 UAS pts**) is here: the supervised weights confidently mis-tag 5.6% of tokens.
Split: 87% CONFIDENT-wrong (OOD/rare-word coverage) + 13% low-margin (genuine ambiguity).
- The 13% low-margin = (M) MISSING INPUT: needs sentence MEANING/context to disambiguate; the top-down
  parse-synergy recovers ~4% of the link, no more (a graded consumer cannot fix a CONFIDENTLY-wrong tag).
- The 87% confident-wrong = a COVERAGE limit of frozen supervised acquisition. The BF alternative
  (reading-learned Brown categories) is 0.745 many-to-one << the supervised 0.944 -- so making this operation
  "BF" today LOSES MORE signal, not less. The deviation (supervised POS) currently SUPPLIES more signal than
  text-only BF acquisition can. It grows with reading (the brain keeps learning), so it is (D)-fixable only in
  the limit of much more reading -- not at current volume. **Understood: the loss is an acquisition-coverage +
  missing-context ceiling, NOT the hard-decode; the non-BF supervised foundation is currently the strongest option.**

### 3a. DECODE (greedy hard-decode) -- deviation type (D), FIXED
Greedy per-token argmax + heuristic cycle-break discards the globally-normalized posterior. LOSS **0.2 UAS pts**.
FIXED by the exact Chu-Liu/Edmonds MAP + single-root Matrix-Tree marginals (brute-verified) -- BF, recovers it.
**Understood: a genuine fixable deviation; made BF; the residual (99% of head error) is NOT decode -> it is the scorer.**

### 3b. SCORER -- REPRESENTATION (arc-factored) -- deviation type (D), PARTIALLY FIXED
The scorer scores each arc INDEPENDENTLY; the brain builds structure incrementally (Now-or-Never left-corner),
which is non-arc-factored. This IS a deviation, and closing it RECOVERS signal: injecting the BF incremental
left-corner structure (OPP-2) lifts verb-argument recall **0.627 -> 0.740** (+0.113), UAS 0.464 -> 0.472, twin
loses. **Understood: a real fixable deviation; the structural (non-arc-factored) BF mechanism recovers signal
the arc-factored representation lost -- the one place in the whole chase where making it BF measurably helps the scorer.**

### 3c. SCORER -- ACQUISITION (supervised gold-tree) -- deviation type (M)
With gold POS + exact decode, the supervised scorer still errs on **20.7% of arcs** (the dominant chain loss).
Chased exhaustively: NOT lexical (adding lexical/distributed features HURTS), NOT valence (faithful soft-EM DMV
verified, underperforms), NOT grounding-of-PP (GEK over-attaches to verbs), NOT bootstrapping (drifts). The BF
alternative (reading-learned scorer) is 0.46 << supervised 0.78. So this deviation, like POS, SUPPLIES more
signal than any text-only BF acquisition. Its residual to a competent human (0.96) is (M) MISSING INPUT: the
brain learns a better grammar than gold trees from GROUNDING + prediction + interaction -- signal a text corpus
does not carry. **Understood: the loss is the text-only acquisition ceiling + missing grounding, NOT a fixable
operation-deviation; the grounded world model is the only lever, and it is a separate program.**

## The honest verdict on the thesis
"Signal loss = non-BF deviation" is TRUE in the refined sense (every loss traces to D, M, or 0), and the chase
found EXACTLY where each kind lives:
- **Fixable non-BF deviations that cost signal (D):** the greedy DECODE (0.2 pts, FIXED -> BF exact) and the
  arc-factored REPRESENTATION (OPP-2, +0.113 verb-arg, PARTIALLY FIXED). These are the wins: non-BF was losing
  signal, and making it BF recovered it.
- **Masked deviations (0):** the tokenizer (input pre-encodes boundaries) and the POS hard-decode (peaked
  posterior) -- non-BF operations that cost ~0.
- **The two BIGGEST losses (M):** POS-acquisition coverage (2.97 pts) and scorer-acquisition (20.7 pts) trace to
  a MISSING INPUT -- the brain's grounded/interactive learning -- NOT to a fixable operation-deviation. There the
  non-BF supervised FOUNDATION currently supplies MORE signal than any text-only BF acquisition (reading-learned
  POS 0.745<0.944, reading-learned scorer 0.46<0.78). Making them "BF" from text today loses more, not less.
So: the decode + representation deviations are found and (partly) fixed; the dominant losses are the text-only
acquisition ceiling + missing grounding, whose ONLY brain-foundational lever is the grounded world model.

## Reverify
`.venv/Scripts/python.exe verification/test_parser_graded_route_through.py` (60 checks) -- incl. the POS-link
decode-vs-acquisition decomposition, the OPP-2 structure win, and the located negatives.
