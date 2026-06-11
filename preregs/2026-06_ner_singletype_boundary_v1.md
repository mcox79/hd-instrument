# Prereg: ner_singletype_boundary_cpu_v1

**Date:** 2026-06-11
**Lane:** CPU (local_cpu_queue)
**Routing:** follow-up to NER Path 1 refutation (exp_ner_bio_viterbi); supports exp_dev_to_research_NER_PATH1_REFUTED note.

## Motivation
NER Path 1 (hard BIO decoder) refuted (lift -0.0125). Decoder is not the bottleneck. Separate the remaining two confounds:
18-WAY TYPE CONFUSION vs BOUNDARY/FEATURE detection. Collapse all 18 entity types to ONE ("ENTITY"), re-run the same structured
perceptron; span-F1 = pure boundary detection without type confusion. Compare to 18-type F1=0.5817.

## Method
Every B-* -> B-ENT, I-* -> I-ENT, O stays O. Same features + structured-perceptron Viterbi. OntoNotes (bundled). 1 seed.

## Pre-registered verdict (diagnostic; NO defeat)
- HARD_PASS boundary-F1 >= 0.72: type confusion is the dominant cost; boundary detection strong; lever = type discrimination
  (features); OntoNotes-18 harder than CoNLL-4 (the note's 0.65 target was apples-to-oranges).
- MIDDLE_BAND 0.62-0.72: both matter.
- HARD_FAIL < 0.62: boundary/feature limited, not type confusion; richer span features needed.

Smoke (300 train): boundary-F1=0.645 vs 0.5817 (gap +0.063); full run decisive.
