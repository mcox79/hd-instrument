# Pre-reg: reader_grade3_envelope_readtogrow_v1

Filed: 2026-07-18. Author: exp_dev. Status: CLAIM-VET-pending. Local/foreground; NO push / NO remote-persist.

## Question
Does the VET-confirmed grade-2 reader HOLD on the harder 3rd McGuffey Reader (envelope / scope-expansion
toward CG), and does READING it GROW a correct relation foundation (first read-to-grow measurement)?

## One variable
GRADE / SYNTAX = the input corpus (2nd-reader baseline vs 3rd-reader). The reader pipeline (handrule
mentions + agreement+topical fixed coref + learned role-assigner + relation emission + Q-engine) is
BYTE-IDENTICAL across arms. Anti-copy-divergence self-test: dataset-parameterized extract ==
`CFX.extract_passage_cfg_mm` byte-identical on the 2nd-reader data (28 passage x mode checks). The
reader is NOT re-tuned for the 3rd reader (no new names in the grounding dict; no coref/mention/extractor
changes).

## Arms
- `second_reader` (BASELINE / POSITIVE CONTROL): `CFX.run_arm("handrule_mentions")` on the confirmed
  2nd-reader data. MUST reproduce all=0.7419, ref=0.8529, RELF1 F1=0.488, R=0.833
  (CITED@data/exp_reader_mention_source_gold_vs_handrule_corefixed_v1/metrics.json:arms.handrule_mentions;
  confirmed 4ec1a4c20, VET a237d1f3).
- `third_reader` (THE ENVELOPE TEST): the same reader on 11 REAL 3rd-reader passages (verbatim;
  provenance-verified) + INDEPENDENT hand-authored gold (15 comprehension Qs, 24 antecedents, 14 gold
  relations).

## Pre-registered bands (HYPOTHESIZED; can-fail both ways; BOUND-first)
- HOLDS: 3rd `all` >= 0.80*2nd `all` AND RELF1 micro-recall >= 0.65 AND ref_acc >= 0.70.
- DEGRADES: 3rd `all` <= 0.55*2nd `all` OR RELF1 recall <= 0.40 (toward the 0.44 hand-rule wall) OR
  ref_acc <= 0.45.
- PARTIAL: otherwise (holds some axes, degrades others).
- POSITIVE-CONTROL must pass (2nd reproduces baseline within 0.005) else INVALID.
- Telemetry: corpus swap must move a metric >= 0.02 (arms are not identical) else INVALID.

## Design-gate (fair test; verified at self-test BEFORE full interpretation)
1. POSITIVE-CONTROL: 2nd-reader arm reproduces the confirmed baseline (all/ref/RELF1). [PASS]
2. REAL 3rd-reader passages: every clause a verbatim substring of the cleaned corpus (29 clauses). [PASS]
3. INDEPENDENT gold: comprehension + antecedents + relations hand-authored by reading (anti-circular;
   NOT copied from extractor output; gold-sanity: all heads are real passage token lemmas). [PASS]
4. ONE variable = grade; reader byte-identical (anti-copy-divergence vs CFX, 28 checks). [PASS]
5. CAN-FAIL: 3rd could collapse (harder syntax) -- genuinely reachable. [PASS]
6. DIFFICULTY-ON: real coordinated multi-clause 3rd-reader syntax; more entities; natural coref.
7. Determinism OMP=1, fixed seed 12345, sorted(set); read-to-grow quality = honest coverage-limited
   lower bound (micro-precision on gold-annotated passages).

## Honest scope caveat (load-bearing)
3rd-reader passages SELECTED mostly-in-vocab (protagonist names already grounded OR common person-nouns)
to isolate SYNTAX as the one variable. This BIASES toward HOLDS: out-of-scope 3rd-reader material (new
ungrounded names, poetry, 100+word sentences) is EXCLUDED BY SELECTION and remains UNTESTED. HOLDS =
"holds on the in-vocab narrative slice", NOT "generalizes to the whole 3rd reader". Vocab coverage
(grounded_frac) is reported. CMP slice n=3 is underpowered; corroborate via ref_acc + RELF1 recall.

## Read-to-grow (secondary)
Accumulate extracted svo/loc/poss relations across the 3rd-reader passages into a foundation (from an
empty start); report growth (# relations / # entities) + quality (micro-precision on gold-annotated
passages = COVERAGE-LIMITED LOWER BOUND; true quality higher; RECALL = relf1 micro_recall).

## Compute architecture
sequential-CPU (POS-tag + tiny averaged-perceptron fit + symbolic coref/query); wall < 120s; no HD/torch/
GPU at runtime (glass-box). COMPUTE-PROPORTIONALITY: a directional envelope diagnostic. Local/foreground.
final_metrics_atomicity: tmp_replace. crash_diagnostic + start_marker present; heartbeat EXEMPT (<120s).
CRLB n/a (no HD noise floor). cardinality n/a (no sweep axis).
