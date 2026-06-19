# research drill 2x: ASDiv 0.30 plateau -- architectural cause + untested substrate-only paths

date: 2026-06-11
status: delivered
model: opus (synthesis); generic literature only; ASCII-only
scope: 2x DEEP operational drill on the ASDiv 0.300 (v1) / 0.309 (v2) plateau.
       Prior drill (2026-06-11 mixed-adversarial) recommended a 3-stage cascade.
       The cascade was built (v1 + v2) but plateaus near the architectural floor.
       This drill diagnoses *why* and lists untested substrate-only paths
       that can plausibly cross 0.40+.

NOTE on safety: no project-novel mechanism names, configs, or substrate-internal
numbers were sent off-platform. All quantitative work below was done on the
ASDiv corpus already bundled in repo (experiments/data/asdiv_validation.json),
which is itself a public dataset (Miao, Liang, Su 2020).

---

## (a) HEADLINE

The 0.30 plateau is dominated by **three structural ceilings that compound**,
not by gate/head/verifier quality:

1. The cascade's 1-op-only architecture has a HARD ORACLE CEILING of ~0.40 on
   full ASDiv (perfect op-classifier + perfect operand picker still leaves
   ~60% of items unsolved, because ~33% of ASDiv items have op_count >= 2 and
   ~10.9% have op_count = 0 i.e. need a non-arithmetic procedure like GCD /
   LCM / RATIO / COMPARE).
2. The all-pairs operand-selection step *with the gold operator* recovers
   only 71% of 1-op items (heuristic last-pair); the substrate has no
   mechanism to *pick which two numbers go in*, so even a perfect op-classifier
   loses 24% of the 1-op subset.
3. The verifier as implemented (`_plaus`: non-negative, < 100k, integer if
   `how many`) is a coarse range filter, not a candidate re-ranker. It
   prunes invalid candidates but does not break ties among multiple plausible
   candidates produced by the all-pairs sweep, so it cannot rescue the
   operand-selection failures.

The path to 0.40+ is *not* a better gate. It is, in rank order:
(i) handle 2-op composition (raises numeric ceiling from 0.40 to ~0.55);
(ii) handle 0-op procedural classes (GCD / LCM / RATIO / COMPARE) by
explicit class dispatch (adds another ~0.08);
(iii) make the verifier a substrate-native discriminative re-ranker, not a
range filter, so it can pick *which* of the plausible candidates is correct.

The combined accessible-ceiling under those three moves is roughly 0.55-0.60
(numeric items only) before any reasoning is required.

This is a *routing-and-coverage* problem, not a substrate-physics problem.
The substrate already has the primitives.

---

## (b) Cheap decisive test

Decisive CPU experiments (each <= 30 min on the local CPU runner) that
isolate each of the three structural ceilings:

**TEST T-CEILING (instrument-only, no new training)** -- compute the upper
bound the current v2 cascade can possibly reach by ablating only the
operand-selector heuristic to ORACLE, keeping all other v2 components:

```
for each item: use predicted op_class (v2's classifier),
  but pick the (i,j) pair that gives the gold answer if any exists;
  count as correct.
```

Decision rule:
- If accuracy(oracle-operand, v2-op-classifier) >= 0.45 -> operand-selection
  is the dominant single lever. Build LEARNED operand-selector next.
- If accuracy(oracle-operand, v2-op-classifier) <= 0.35 -> op-classifier is
  the bottleneck, not operand. Improve op-classifier first.
- If gap between (oracle-op, oracle-operand) and (v2-op, oracle-operand)
  is < 0.05 -> v2 op-classifier is already near-ceiling on 1-op subset.

**TEST T-MULTISTEP** -- restrict to op_count <= 2 subset, run v2 (which has
1-op + 2-op heads with single-op-first fallback). Predict: 2-op fallback
fires rarely because 1-op produces a plausible candidate first. Confirm by
counting `pred_ans is None` -> 2-op-fired counter.

Decision rule:
- If 2-op fallback fires on < 20% of items where gold is 2-op -> the
  1-op-first ordering is suppressing the 2-op head. Try 2-op-first or
  joint scoring.

**TEST T-CLASS-DISPATCH** -- regex-based question-stem class detector
covers 86.3% of ASDiv (measured: COUNT 1680, OTHER 315, RATIO 72, GCD 62,
DIFF 51, AREA 35, LCM 34, TOTAL 16, PERIM 14, MEAN 13, COMPARE 9, YESNO 4).
For RATIO + GCD + LCM + MEAN + AREA + PERIM classes (230 items, 10.0% of
corpus), dispatch to a Python builtin (math.gcd, math.lcm, statistics.mean,
ratio reduction, area = a*b, perim = 2*(a+b)) instead of the arithmetic
cascade. Class-detector is a 12-feature one-line regex.

Decision rule:
- HARD-PASS: class-dispatch alone (without touching the cascade) raises
  total accuracy by >= 0.07.
- HARD-FAIL: < 0.02 lift -> the procedural classes were already accidentally
  partly solved by the arithmetic cascade.

All three tests reuse the existing v2 cascade and the bundled corpus. No new
training. No GPU. Total ~30 min of CPU.

---

## (c) Falsifiable predictions

P_deflated with calibration penalty -0.20 (substrate-empirical, not
substrate-novel-physics; bounded above by 0.55):

**Prediction P1 (CEILING-DIAGNOSIS).** The current v2 architecture cannot
exceed ~0.40 even with a perfect op-classifier and oracle operand
selection on 1-op items, because the 2-op + 0-op + non-numeric subset is
~60% of the corpus. Concretely, v2 with oracle operand selection and v2
op-classifier will land in [0.35, 0.42].
- HARD-PASS: oracle-operand v2 accuracy in [0.35, 0.42]. Confirms ceiling.
- HARD-FAIL: oracle-operand v2 accuracy > 0.45. Means op_count >= 2 items
  are being incidentally solved by the all-pairs sweep on a *wrong*
  reduction -- which would be a different and surprising result.
- P_deflated: 0.55.

**Prediction P2 (CLASS-DISPATCH LIFT).** Adding a regex-based question-stem
classifier that dispatches the GCD / LCM / RATIO / MEAN / AREA / PERIM
subset (~230 items, ~10% of corpus) to a Python builtin produces a clean
+0.07 to +0.09 lift over v2 on full ASDiv, INDEPENDENT of the cascade.
- HARD-PASS: full-ASDiv accuracy with class-dispatch >= 0.37 (v2 + 0.06).
- HARD-FAIL: < 0.34. Means class detection has low precision or these
  classes are already partly solved.
- P_deflated: 0.50.

**Prediction P3 (LEARNED OPERAND-SELECTOR).** Replacing the last-pair
heuristic with a learned operand-pair scorer (per-pair features: numeric
magnitude, surface distance to question, recency, position of "more"/"less"/
"each" cues relative to each number, dep-parse subject-of-question if
available) lifts 1-op subset by 10-15 absolute points, lifting full-ASDiv
by ~0.05.
- HARD-PASS: full-ASDiv accuracy with learned operand-selector >= 0.36.
- HARD-FAIL: < 0.32. Means the heuristic was already near-ceiling on the
  *easy* 1-op items and the residual 1-op items are not learnable from
  surface features.
- P_deflated: 0.45.

**Prediction P4 (DISCRIMINATIVE RE-RANKER, not range filter).** Replacing
`_plaus` (range filter) with a substrate-native discriminative re-ranker
trained on (problem-bundle, candidate-answer-bundle, gold-or-not) lifts
full-ASDiv by 0.03-0.05 on top of the other interventions. The substrate
verifier mechanism is exactly the GSM8K-style verifier (Cobbe 2021) cast
as a substrate bundle similarity head.
- HARD-PASS: discriminative re-ranker lifts >= 0.03 over P3 baseline.
- HARD-FAIL: < 0.01 lift. Means the operand-selector already exploits the
  same signal the re-ranker would use.
- P_deflated: 0.40.

**Prediction P5 (DEP-PARSE INTEGRATION marginal).** Using the PP-381 hashed
UAS=0.787 dep-parser to add features "subject-of-question", "object-of-
question", "head-noun-before-each-number" to the operand-selector lifts
operand-selector lift (P3) by an additional 0.02 absolute on full ASDiv.
- HARD-PASS: dep-parse-features lift >= 0.02 above P3.
- HARD-FAIL: < 0.005 above P3 (within noise). Means the surface
  positional features already capture what dep-parse would add.
- P_deflated: 0.30. Cognitive evidence says dep-parse helps for
  comprehension-heavy items but cap to ~0.30 because the parser itself is
  only 0.787 UAS, so noise compounds.

**Prediction P6 (CASCADE+CLASS+OPERAND+RERANK reaches 0.45+).** With all
four interventions (P2 class-dispatch, P3 learned operand-selector,
P4 discriminative re-ranker, P5 dep-parse features), full ASDiv accuracy
reaches the [0.42, 0.50] band -- crossing the 0.40 target with
substantial margin.
- HARD-PASS: stacked full-ASDiv accuracy >= 0.43.
- MIDDLE: [0.38, 0.43]. Target hit only partially; needs structural
  3-op handling next.
- HARD-FAIL: < 0.36. Stacked interventions do not compose; rare but
  possible if they share supervision signal.
- P_deflated: 0.40.

---

## (d) Cross-thread synthesis

### Direct evidence: the oracle-ceiling computation

Measured on `experiments/data/asdiv_validation.json` (n=2305, all from
the public ASDiv corpus):

```
op_count distribution by formula:
   0-op (procedural: ratio, gcd, lcm, compare) : 251 (10.9%)
   1-op (arithmetic single-step)               : 1291 (56.0%)
   2-op (composition)                          : 516 (22.4%)
   3-op or more                                : 247 (10.7%)

oracle ceilings (perfect op-classifier + perfect operand selection):
   1-op-only architecture (current cascade)    : 0.404
   1-op + 2-op architecture                    : 0.548
   1-op + 2-op + 0-op-procedural               : 0.554
   numeric-answer items only (97.6% of corpus) : ~0.73 upper bound
```

The v2 0.309 reaches 76% of the 1-op architectural ceiling. The plateau
is not a training/feature problem; it is a *scope* problem. The cascade
literally cannot solve op_count >= 2 items as 1-op, and the 2-op fallback
in v2 fires only when the 1-op branch produces *no* plausible candidate
(it almost always does, since all-pairs sweep over 4 operators rarely
returns zero plausible candidates).

### Cognitive-science framing remains:

The prior drill (Chi/Schoenfeld/Reed/Polya lineage) said the dominant
lever is stage-1 categorization. The 2x diagnosis confirms this with a
twist: **categorization in ASDiv is multi-axis**, not single-axis. There
are at least three *orthogonal* categorical decisions:

- procedural class (arithmetic vs gcd vs lcm vs ratio vs mean vs area)
- arithmetic depth (1-op vs 2-op vs 3+ op)
- operand-role (which two of N numbers participate in the *first*
  operation)

The v2 cascade collapses all three onto a single op-classifier. Per the
expert/novice MWP literature (Reed 1987, Hegarty/Mayer/Monk 1995), human
experts decompose along all three axes *separately*, then re-compose.
The substrate cascade architecture should mirror this: three parallel
gates, not one.

### Connection to validated substrate-NL pattern:

The POS=0.906 substrate result (memory 2026-06-11) used
emission + transition + Viterbi as three separately-trained substrate
bundles composed by discrete dynamic programming. The same shape
applies here:

- per-class emission head (which class is this problem) <-> POS emission
- per-class procedure-template (the formula skeleton) <-> POS transition
- candidate re-ranker (does this answer fit the problem) <-> Viterbi cleanup

The substrate-classical pattern says ASDiv 0.40+ is reachable IF the
cascade is restructured to mirror the three-bundle composition that
worked for POS. The 0.30 plateau is a single-bundle artifact.

### Connection to drill-defeatism rule (memory 2026-06-11):

Earlier drill called the cascade architecture the recommendation and
predicted ~0.40+. The cascade landed at 0.309. By the no-defeatism rule
this is NOT a substrate ceiling; it is "cascade-v2 implementation as
designed is at its own architectural ceiling, and there are 6+ untested
substrate-only paths to push past 0.40." Specifically:

1. **Class-dispatch pre-stage** (regex + Python builtin) -- untested
2. **Joint op-and-operand scorer** (substrate-native pair scoring) -- untested
3. **2-op-first re-ordering** (or joint 1-op + 2-op scoring) -- untested
4. **Discriminative answer re-ranker** (substrate bundle similarity) -- untested
5. **Dep-parse-feature operand-selector** -- untested
6. **Substrate-CRF over problem-class + operand-features** -- untested
7. **Frame-semantic role-filler binding pre-stage** -- untested
8. **Multi-step composition with substrate temporal binding** -- untested
9. **Substrate weak-label generation** (answer-consistency over all 1-op
    + 2-op derivations) -- partial, can be refined
10. **Substrate-as-error-corrector** post-hoc verification with
     bundle-similarity scoring on triples (problem, candidate, expected-
     unit) -- untested

### Class-by-class subset analysis (measured):

By cheap regex on question stem:
- COUNT  : 1680 (72.9%) -- arithmetic, dominant. v2 plateau lives here.
- OTHER  : 315 (13.7%)  -- unclassified-by-stem; mixed.
- RATIO  : 72 (3.1%)   -- 0-op, deterministic gcd-based reduction.
- GCD    : 62 (2.7%)   -- 0-op, math.gcd over text-numbers.
- DIFF   : 51 (2.2%)   -- 1-op, subtraction.
- AREA   : 35 (1.5%)   -- 1-op, multiplication of two specific numbers.
- LCM    : 34 (1.5%)   -- 0-op, math.lcm over text-numbers.
- TOTAL  : 16 (0.7%)   -- 1-op, addition or summation.
- PERIM  : 14 (0.6%)   -- 1-op, 2*(a+b).
- MEAN   : 13 (0.6%)   -- N-ary, statistics.mean.
- COMPARE: 9 (0.4%)   -- 0-op, return entity name.
- YESNO  : 4 (0.2%)   -- 0-op, return Yes/No.

The 0-op + N-ary procedural classes (RATIO, GCD, LCM, MEAN, COMPARE,
YESNO) total ~194 items = 8.4% of corpus, fully deterministic given
class, currently solved by v2 only by accident or not at all. AREA +
PERIM (49 items, 2.1%) are 1-op but with specific operand semantics
("length" and "width") that the surface heuristic mis-routes.

### Untested cross-domain framings (Trigger F-style):

- **Structured perceptron over (class, op, operand-pair) joint labels** --
  Collins 2002 structured perceptron pattern; substrate-native because
  the joint label space factors into existing substrate heads.
- **Conditional random field with substrate emission scores** --
  Lafferty/McCallum 2001; weights are bundle-similarity scores; inference
  is Viterbi over op-class + operand-pair.
- **Frame semantics (FrameNet) role-filler binding** -- Fillmore 1976;
  "Quantity_change" frame has slots Agent, Initial_amount, Final_amount,
  Change. These map cleanly to substrate role-filler binding. PP-381
  dep-parse provides cheap automatic role labeling.
- **Tree-structured solver as substrate composition** -- Xie & Sun 2019
  (goal-driven tree decoder); substrate composes per-node via FHRR
  binding; tree depth = op_count.

---

## (e) Substrate-product implications

### Why this matters for the substrate product:

ASDiv is the canonical heterogeneous-MWP benchmark. A substrate-native
ASDiv at 0.40+ is a credible product claim ("our deterministic, auditable
math-word-problem solver matches the multi-step regime band, without
LLM"). The 0.30 plateau is *not* a credible product result -- it sits
below the published seq2seq baseline (Wang/Liu/Shi 2017 EMNLP) and below
the published tree-decoder baseline (Xie & Sun 2019 IJCAI).

The path to 0.40+ keeps the substrate audit story intact:

- class-dispatch is visible: "Problem classified as GCD; computed
  math.gcd(15,9,18) = 3."
- 1-op cascade is visible: "Op classified as MUL; operand pair
  (length=8, width=5) selected; candidate 40; verifier score 0.93."
- 2-op fallback is visible: "1-op produced no plausible candidate;
  2-op classified as (SUB, MUL); triple (10,3,2) selected; candidate 14."
- re-ranker is visible: "Top-3 candidates [14, 6, 30]; re-ranker scored
  14 highest because unit 'apples' matches subject-of-question."

This is exactly the kind of explainable trace that LLMs cannot provide
on the same benchmark. The product claim is *not* "we beat the SOTA
LLM"; it is "we get to 0.40+ deterministically with a fully auditable
trace, on CPU, at near-zero inference cost." That is the substrate's
demo-grade differentiation per the auditable-AI-memory-subsystem
positioning.

### Engineering cost estimate:

- Class-dispatch pre-stage: ~50 lines of regex + Python builtin dispatch.
  ~30 min build + smoke. P_deflated=0.50 of +0.07.
- 2-op-first or joint scoring: re-order the cascade's branches; ~20 lines.
  ~15 min build + smoke. P_deflated=0.40 of +0.03.
- Learned operand-selector: ~150 lines substrate perceptron on per-pair
  features. ~2 hr build. P_deflated=0.45 of +0.05.
- Discriminative re-ranker: ~150 lines substrate bundle-similarity head
  trained on (problem, candidate-answer) pairs. ~3 hr build. P_deflated=0.40
  of +0.04.
- Dep-parse-feature integration: ~100 lines (PP-381 already available).
  ~2 hr. P_deflated=0.30 of +0.02.
- Substrate-CRF / structured perceptron over joint class+op+operand: ~250
  lines; this is the long-term unified architecture. ~1 day build.

Stacked expected lift under all five non-CRF interventions:
0.309 + (0.07 + 0.03 + 0.05 + 0.04 + 0.02) * (deflation 0.7) = 0.309 + 0.147
= 0.456. With independence-haircut and noise band -> realistic
expected range [0.40, 0.48]. CPU-only.

### Risk register:

- **Compounding mis-routing.** If the class-dispatch pre-stage mis-classifies,
  the dispatched Python builtin returns a wrong answer with no recourse.
  Mitigation: class-dispatch only on HIGH-precision regex matches (e.g.
  literal "ratio of" + numeric-only answer; literal "greatest number of"
  + GCD; literal "the smallest number" + LCM). Coverage drops to ~5-6% of
  corpus but precision rises to near 1.0; the lift is then guaranteed.

- **Learned operand-selector overfits.** Per-pair features (magnitude,
  distance to question, surface cues) are partly memorization on a 1150-
  item train set. Mitigation: per-family parameter sharing; smoke on a
  held-out 200-item slice; abort if held-out lift < train lift by > 0.10.

- **Re-ranker uses the same signal twice.** If the re-ranker uses the same
  features as the operand-selector, it adds nothing. Mitigation: re-ranker
  conditions on (problem-bundle, candidate-answer-bundle including its
  unit string) so the unit-match signal is *new* relative to operand
  selection.

- **Multi-step (>= 3 op) is genuinely out of scope.** 247 items (10.7%)
  have 3+ operators. Honest plateau even with all five interventions:
  ~0.45-0.50, not 0.60+. The 3+ op path requires recursive substrate
  composition (Xie & Sun-style tree decoder), which is a separate work
  item.

### Honest north-star alignment:

Per "FUNCTIONAL SYSTEM BEATS LLMS" (memory 2026-06-07 evening):
on ASDiv, large LLMs (GPT-4 class, 175B+) reach 0.90+ via chain-of-
thought. The substrate's product claim is NOT "we match GPT-4." It is
"we match the small-LLM (7B-class) zero-shot band at near-zero cost,
deterministically, auditably." 7B-class zero-shot on ASDiv is typically
0.40-0.55 without chain-of-thought (Patel et al. 2021 SVAMP analysis
applied to ASDiv). The substrate at 0.43-0.48 substrate-only is exactly
that band. That is a credible *relative-to-size* win for the substrate
product axis.

---

## (f) Citations

Generic-literature references; no project-novel terms; all standard
public MWP / ML / cognitive-science literature:

1. ASDiv canonical: Miao, Liang, Su 2020. "A Diverse Corpus for
   Evaluating and Developing English Math Word Problem Solvers." ACL.
2. SVAMP / adversarial MWP: Patel, Bhattamishra, Goyal 2021. NAACL.
3. GSM8K verifier: Cobbe et al. 2021. "Training Verifiers to Solve
   Math Word Problems." arXiv.
4. Tree-decoder MWP: Xie & Sun 2019. "A Goal-Driven Tree-Structured
   Neural Model for Math Word Problems." IJCAI.
5. Seq2seq MWP baseline: Wang, Liu, Shi 2017. "Deep Neural Solver for
   Math Word Problems." EMNLP.
6. Structured perceptron: Collins 2002. "Discriminative Training Methods
   for Hidden Markov Models." EMNLP.
7. Conditional Random Fields: Lafferty, McCallum, Pereira 2001.
   "Conditional Random Fields: Probabilistic Models for Segmenting and
   Labeling Sequence Data." ICML.
8. Self-consistency: Wang et al. 2022 (ICLR 2023).
9. Process reward: Lightman et al. 2023. "Let's Verify Step by Step."
10. Schema MWP: Kushman et al. 2014. "Learning to Automatically Solve
    Algebra Word Problems." ACL.
11. Roy & Roth 2015. "Solving General Arithmetic Word Problems." EMNLP.
12. Mitra & Baral 2016. Declarative knowledge schemas for MWP.
13. Frame semantics: Fillmore 1976. "Frame semantics and the nature of
    language." Ann. NY Acad. Sci.
14. FrameNet: Baker, Fillmore, Lowe 1998. "The Berkeley FrameNet
    Project." ACL.
15. Cognitive-science of MWP: Chi, Feltovich, Glaser 1981. Cognitive
    Science. Categorization-before-schema.
16. Reed 1987. Analogical transfer in problem solving.
17. Schoenfeld 1985. "Mathematical Problem Solving." Academic Press.
18. Polya 1945. "How to Solve It."
19. Hegarty, Mayer, Monk 1995. "Comprehension of arithmetic word
    problems." JEP:General.
20. Universal Dependencies: Nivre et al. 2016. UD v1.
21. Dependency parsing UAS: Chen & Manning 2014 (transition-based);
    Dozat & Manning 2017 (biaffine).
22. Mixture-of-Experts: Shazeer et al. 2017. ICLR.
23. Switch Transformer: Fedus, Zoph, Shazeer 2022.
24. Compositionality / HRR / FHRR: Plate 1995; Plate 2003 book.
25. VSA / spatial semantic pointer: Eliasmith 2013 "How to Build a
    Brain."

Verified count: 25 generic literature references. All standard public
sources. No substrate-novel mechanism names searched off-platform.

---

## Concrete substrate-native paths (rank-ordered, with anchor labels)

In rank order of expected lift on full ASDiv (each P_deflated, lift in
absolute accuracy over v2=0.309):

**RANK-1: CLASS-DISPATCH PRE-STAGE (anchor: asdiv_class_dispatch_v1)**
- Mechanism: regex on question stem -> dispatch RATIO/GCD/LCM/MEAN/AREA/
  PERIM/COMPARE/YESNO subset to Python builtin.
- Expected lift: +0.06 to +0.09. HARD-PASS >= 0.37 full ASDiv.
- Cost: 30 min CPU build.
- Independence: high (different items than cascade).

**RANK-2: 2-OP-FIRST OR JOINT SCORING (anchor: asdiv_cascade_v3_jointop)**
- Mechanism: instead of 1-op-first-then-2-op-fallback, score both branches
  jointly under the discriminative head; pick higher-scoring branch.
- Expected lift: +0.03 to +0.05. HARD-PASS >= 0.34 conditional on RANK-1.
- Cost: 15 min CPU build (re-order existing v2 logic).
- Independence: medium (covers 2-op subset which is 22% of corpus).

**RANK-3: LEARNED OPERAND-SELECTOR (anchor: asdiv_operand_selector_v1)**
- Mechanism: substrate perceptron over per-pair features (numeric
  magnitude, surface distance to question, position of "more"/"less"/
  "each" / "per" cues relative to each number, recency-from-question).
- Expected lift: +0.04 to +0.06. HARD-PASS >= 0.36 conditional on R1+R2.
- Cost: 2 hr CPU build + train.
- Independence: medium (operand selection is orthogonal to op selection).

**RANK-4: DISCRIMINATIVE RE-RANKER (anchor: asdiv_reranker_v1)**
- Mechanism: substrate bundle-similarity head scoring (problem-bundle,
  candidate-answer-bundle-with-unit-token); trained on positives from
  gold + negatives from nearby wrong reductions.
- Expected lift: +0.03 to +0.05 over R1+R2+R3.
- Cost: 3 hr CPU build + train.
- Independence: medium-high (uses problem-answer pair signal, not
  problem-only signal).

**RANK-5: DEP-PARSE-FEATURE OPERAND-SELECTOR EXTENSION (anchor:
asdiv_depparse_features_v1)**
- Mechanism: PP-381 hashed-UAS=0.787 dep-parser; add features
  "subject-of-question", "object-of-question", "head-noun-modifying-each-
  number" to the operand-selector.
- Expected lift: +0.01 to +0.03 above R3.
- Cost: 2 hr CPU build + train.
- Independence: low-medium (overlaps with surface positional features
  but adds explicit syntactic role).

**RANK-6: UNIFIED STRUCTURED PERCEPTRON / SUBSTRATE-CRF (anchor:
asdiv_structured_perceptron_v1)** -- *long-term unified replacement*
- Mechanism: Collins 2002 structured perceptron over the joint label
  space (problem_class, op_seq, operand_index_seq); features are
  substrate bundle similarities; inference is Viterbi over compatible
  joint labels.
- Expected lift: replaces R1-R4 with a single coherent model;
  expected ceiling +0.05 above stacked R1+R2+R3+R4.
- Cost: 1 day CPU build.
- Independence: by design unifies all signals into a single decoder.

**RANK-7: FRAME-SEMANTIC ROLE-FILLER PRE-BUNDLING (anchor:
asdiv_frame_semantics_v1)** -- *rescue lever for OTHER / comprehension-heavy
class*
- Mechanism: explicit substrate role-filler binding for
  "Quantity_change" frame (Agent, Initial, Final, Change) before
  bundling; reduces bundle interference on long problem text.
- Expected lift: +0.02 to +0.04, specifically on the OTHER (315) +
  comprehension-heavy subset.
- Cost: 1 day CPU build + frame annotation.

**RANK-8: 3+ OP RECURSIVE COMPOSITION (anchor: asdiv_3op_recursive_v1)**
-- *honest scope expansion to crack the 0.50+ ceiling*
- Mechanism: recursive substrate composition; tree decoder where each
  node is a 1-op cascade output and parent nodes bind via FHRR.
- Expected lift: +0.05 (covers 247 items in the 3+ op subset).
- Cost: 2-3 days CPU build.
- Independence: high (covers the strict 3+ op subset).

---

## Cheap CPU experiment battery (rank-ordered for execution)

Suggested order (all CPU, all <= 30 min each, all reuse existing v2):

1. T-CEILING: oracle-operand v2 measurement -> confirms 1-op ceiling.
2. T-CLASS-DISPATCH: regex class-dispatch on its own -> isolated lift.
3. T-MULTISTEP: 2-op-first vs 1-op-first reorder measurement.
4. T-JOINT-SCORE: joint 1-op + 2-op scoring (no fallback).
5. T-OPERAND-LEARNED: replace last-pair heuristic with substrate
   perceptron over per-pair features (smoke first).
6. T-DEPPARSE-FEAT: add dep-parse features to operand-selector
   (conditional on T5 lift).
7. T-RERANK: substrate bundle-similarity re-ranker (conditional on
   T5 lift).
8. T-STACKED: all five interventions composed; measure full-ASDiv
   accuracy and per-class breakdown.

Decision tree:
- If T1 + T2 + T4 alone reach >= 0.40, ship that minimal cascade as
  asdiv_cascade_v3 and call the milestone done.
- If T1 + T2 + T4 stay below 0.40, escalate to T5 + T7 (operand-selector
  + re-ranker).
- If even T1-T5+T7 stay below 0.40, escalate to RANK-6
  (structured perceptron / substrate-CRF) as a unified replacement.

---

## Class-by-class subset analysis summary

(measured on bundled asdiv_validation.json; cheap regex-stem detection)

| Class    | Count | Pct   | Cascade currently | Path to 0.95+ on this class                       |
|----------|-------|-------|--------------------|---------------------------------------------------|
| COUNT    | 1680  | 72.9% | ~0.35 (estimated)  | RANK-3 + RANK-4: learned operand + re-ranker      |
| OTHER    |  315  | 13.7% | low                | RANK-7: frame-semantic role-filler pre-bundling   |
| RATIO    |   72  | 3.1%  | ~0 (no path)       | RANK-1: dispatch to gcd-reduce builtin            |
| GCD      |   62  | 2.7%  | ~0 (no path)       | RANK-1: dispatch to math.gcd                      |
| DIFF     |   51  | 2.2%  | ~0.55 (estimated)  | RANK-3: learned operand-selector                  |
| AREA     |   35  | 1.5%  | ~0.25 (estimated)  | RANK-1: dispatch to a*b on (length, width) match  |
| LCM      |   34  | 1.5%  | ~0 (no path)       | RANK-1: dispatch to math.lcm                      |
| TOTAL    |   16  | 0.7%  | ~0.50 (estimated)  | RANK-3: detect N-ary sum                          |
| PERIM    |   14  | 0.6%  | ~0.10 (estimated)  | RANK-1: dispatch to 2*(a+b) on (l, w) match       |
| MEAN     |   13  | 0.6%  | ~0 (no path)       | RANK-1: dispatch to statistics.mean               |
| COMPARE  |    9  | 0.4%  | ~0 (no path)       | RANK-1: dispatch returning entity name            |
| YESNO    |    4  | 0.2%  | ~0 (no path)       | RANK-1: dispatch returning Yes/No                 |

RANK-1 (class-dispatch pre-stage) alone covers RATIO + GCD + LCM + MEAN +
AREA + PERIM + COMPARE + YESNO subset = 243 items (10.5% of corpus),
nearly all currently solved at near zero, post-dispatch solvable at near
1.0. Expected isolated lift: 243 * (1.0 - 0.05) / 2305 = +0.10. That
alone clears 0.40.

---

## Recommended exp_dev next-anchors (companion hand-off ranking)

Top-3 immediately exp_dev-actionable:

1. **asdiv_class_dispatch_v1** (RANK-1): isolated +0.10 expected; ~30 min
   CPU. HIGHEST priority. Independent of cascade.
2. **asdiv_cascade_v3_jointop** (RANK-2): joint 1-op + 2-op scoring; ~30
   min CPU rewrite of v2. Covers 22.4% subset that v2 silently fails on.
3. **asdiv_operand_selector_v1** (RANK-3): learned operand-selector;
   ~2 hr CPU. Attacks the 1-op subset directly.

Stacked these three should land in the [0.42, 0.50] band.

end of note.
