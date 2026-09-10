# Step-by-step brain-foundational confirmation of the common-noun coref chain (math + signal-loss + optimization)

**2026-09-10, solver.** Owner: "go step by step and confirm BF mathematically; where are we losing signal; optimization
opportunities now?" Every verdict is down to the operation; every signal-loss number is measured first-hand this session
(GUM modern TEST, n=2855 anaphoric common-noun mentions; the honest de-leaked floor). Chain = raw text -> resolution.

## A. The chain, step by step (operation -> BF verdict -> signal loss -> optimization)

| # | stage | operation (math) | BF verdict | signal loss (measured) | optimization |
|---|---|---|---|---|---|
| 1 | tokenize | whitespace/rule split | neutral | ~0 | -- |
| 2 | POS tag (`pos_tagger`) | Collins averaged perceptron + **Viterbi hard-decode** argmax | **NOT_BF** (frozen supervised; discards the tag posterior) | head-NEUTRAL for coref (~0) | swap `crf_tagger` (forward-backward MARGINALS) -> graded posterior = confidence signal (BF) |
| 3 | parse / span-HEAD (`arc_parser`) | arc-factored perceptron, **greedy hard-decode + cycle-break** | **NOT_BF** (frozen supervised; discards Matrix-Tree marginals) | **-0.049 CI-sep on coref (raw-text head errors on post-modified NPs)** | `boundary_nphead` (parser-free UD span-head + `np_head_reduce`) recovers -> **-0.015**; graded_parser marginals for confidence |
| 4 | lemma / concept KEY | `commonnoun_binder.head_lemma` crude regex -> **FIXED** `concept_lemma` = morphy wordform->lemma-concept | **BF** (fixed; was NOT_BF: empty-collapse + over-strip) | was -0.0098; **RECOVERED +0.0098** (0.5482->0.5580), beats de-leaked floor +0.0326 CI-sep | landed-ready; fold into `np_head_reduce`/live wire |
| 5 | gender/number | morphological `_num_of` + name-gazetteer lookup | shallow BF | small (part of the same-head residual) | -- |
| 6 | salience (`salience_binder`) | **B = ln( sum_k w(role_k) . dt_k^(-decay) )** (Anderson-Schooler power-law x Centering Cf) | **BF** (the brain's declarative-retrieval activation, verbatim) | ~0 (role cue is inert for resolution, measured +0.0007) | params (decay, role weights) swept, not adopted |
| 7 | BINDING (`typed_coref`) | argmax over gn-compatible, concept/type-matched prior referents by ACT-R B; NON-WRITING Nref hold | **BF_SPIRIT** (Lewis-Vasishth cue-based retrieval + Ariel accessibility + Nieuwland hold) | **NOT a loss** -- beats string-identity CI-sep at EVERY head-quality level (gold/frozen/boundary/unfrozen) | robust; the correct organ |
| 8 | TYPE bridge + knowledge (`typed_spokes` C5+C8 + `conceptual_meaning`) | type-license: shared synset / is-a hypernym closure / part-whole (C5) + DBpedia InstanceOf (C8) + IDF-weighted gloss cosine (conceptual) | **operation BF_SPIRIT** (ATL content-addressed typed spokes); **KNOWLEDGE incomplete** | **DOMINANT loss (see B)**; conceptual bridge recovered +0.0042 CI-sep | world-knowledge KB (encyclopedic coverage + ConceptNet schema) = the biggest lever |

**Confirmation:** stages 4-8 (the semantic core: concept key, gn, salience, binding, type operation) are BF / BF_SPIRIT
down to the math. The two NOT_BF components are the frozen supervised PARSE STACK (2,3) -- and their coref cost is either
fixed (head selection -> boundary rule) or neutral (POS). **Nothing in the semantic core is where the signal is lost.**

## B. Where the signal is lost (first-hand decomposition, `exp_cn_signal_loss_decomp_v1.py`, n=2855)

| slice | share | binding acc | mentions lost | interpretation |
|---|---|---|---|---|
| **SAME-HEAD** (a prior same-entity mention shares the concept-lemma) | 66.4% | **0.7831** | 411 (14.4% of all) | the signal we HAVE; residual = gn/parse/salience errors (some recoverable via stage 3/4 fixes) |
| **DIFFERENT-HEAD** (prior same-entity mention, NO shared head: "the doctor"->Elizabeth, "the vehicle"->a car) | 31.5% | **0.1212** | **790 (27.7% of ALL)** | **the DOMINANT loss -- world-knowledge + situation-model inference; the binding gets only 12%** |
| NO-PRIOR (edge: redaction/cross-sentence) | 2.1% | 0.0 | 61 | first-mention/unlinkable in this framing |

**The dominant signal loss is the DIFFERENT-HEAD slice: 27.7% of ALL mentions, where the binding scores only 0.12.** This
is the type-comparator/world-knowledge + generative-inference wall, confirmed first-hand (matches the prior oracle's +0.18
type-comparator headroom). It DWARFS the parse-chain losses (head -0.049, lemma -0.0098). The same-head residual (14.4%) is
the smaller, partly-parse-recoverable loss.

## C. Optimization opportunities NOW (ranked by leverage x readiness)

1. **LAND the proven BF fixes (immediate, measured, no-regress):** concept-lemma key (+0.0098, beats de-leaked floor
   CI-sep), the `boundary_nphead` raw-text head selector (-0.049 -> -0.015), the conceptual-meaning bridge (+0.0042 CI-sep),
   and the crf/graded decode as the confidence signal. All in `SOLVED.md 6`; strategy lands (Q111).
2. **WORLD-KNOWLEDGE KB for the type comparator (the DOMINANT lever, ~+0.18 headroom on the 31.5% diff-head slice):**
   encyclopedic InstanceOf coverage (C8 DBpedia is wired but coverage-bound) + ConceptNet schema/associative anaphora.
   Filed as `world_knowledge_common_noun_to_name_bridge`. Static-offline, invariant-safe. Biggest single accuracy lever.
3. **SEMANTIC BOOTSTRAPPING for the parser (the comprehension learning signal):** derive a coarse who-did-what MEANING
   target from animacy (parse-free) + verb-argument structure; train the parser toward the meaning, not gold or
   predictability. The named next step for the raw-text parser (its unsupervised ceiling is proven at 0.41-0.52 vs 0.775).
4. **THE GENERATIVE WORLD-MODEL (situation-model inference):** the ~73% of the diff-head residual that is not a KB lookup
   but genuine inference ("who is expected here"). The pri-1 north star; the biggest long-horizon lever.
5. **SAME-HEAD residual (14.4%, smaller):** better gn agreement + the head/lemma fixes recover a slice; parser accuracy
   (stage 3) bounds the rest on the raw-text path.

## D. Honest bottom line
The common-noun binder and its semantic core (concept key, salience, typed binding, type operation) are confirmed
brain-foundational to the math. The signal is lost in exactly two places, both now quantified: (i) the frozen supervised
PARSE STACK (fixed for coref by the parser-free boundary rule; the raw-text UAS gap is the comprehension-signal wall), and
(ii) DOMINANTLY the world-knowledge + situation-inference behind the 31.5% different-head slice (binding 0.12). The
highest-leverage optimization is the world-knowledge KB, then the generative world-model -- both already on the map.
