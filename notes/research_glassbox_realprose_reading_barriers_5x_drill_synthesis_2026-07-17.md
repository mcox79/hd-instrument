# Glass-box no-LLM real-prose reading: what are the REAL barriers? (5x drill synthesis)

**USER STEER (2026-07-17):** real-prose glass-box no-LLM reading is DEFINITELY doable (BRAIN = existence-proof). Test hypothesis: is the barrier JUST foundation-SIZE and/or WORKING-MEMORY? Drill brain + ML + classic. This note = the Director's own synthesis of the 5x drill sweep (parent synthesizers were flaky under API instability; raw lane content captured from the reports and synthesized here).

Deflation: lane reports were snippet-level (few full-text reads); treat magnitudes as approximate, directional conclusions as the load-bearing part.

---

## DRILL 1 — FOUNDATION / WORLD-KNOWLEDGE SIZE (3 lanes: biology + ML/IE + classical AI) — LANDED

**VERDICT: CONTRIBUTING, but NOT the primary barrier in the naive "just build a bigger KB" sense. The refined lever = the RIGHT KIND of knowledge (selectional-preference / thematic-fit disambiguation statistics), LEARNED from exposure (not hand-built), and USED for disambiguation.**

- **Biology (a97f7ad6):** world knowledge does REAL, EARLY parsing work -- modern constraint-based / Generalized-Event-Knowledge / referential-theory models beat the old "syntax-first, semantics-only-repairs" view. Garden-path severity, PP-attachment, thematic-role assignment are all shaped rapidly by lexical-frequency + thematic-fit + event-schema + discourse cues (functionally compressed world knowledge). N400 AND P600 both respond to pure world-knowledge violations. Background knowledge measurably SUBSTITUTES for generic reading skill (Recht & Leslie baseball study; expert-novice d~2.0) -- strongest for recall, weaker for inference. Size anchors: ~42k lemmas / ~11k word families (Brysbaert 2016). KEY: Landauer/LSA -- this knowledge is STATISTICALLY LEARNABLE from co-occurrence at human acquisition rates. NO study found asserting comprehension is BOUNDED by knowledge-size rather than machinery (gap).
- **ML/IE (a533c4db):** KB-augmentation (gazetteers/WordNet/ontologies) delta is a SUBSTITUTION / THRESHOLD effect, NOT monotonic "bigger = better": LARGE when the base model is weak (low-resource NER +4 to +31 F1) but SMALL-to-NEGATIVE when the base is strong (+0.3-0.5 F1; knowledge-based WSD LOSES to a dumb most-frequent-sense frequency baseline by ~6 pts). Auto-INDUCED statistical classes BEAT hand-built-KB augmentation on PP-attachment (maxent 81.6% vs WordNet-classes 76% vs 72% baseline; human ceiling 88-93%). Correct UTILIZATION of a fixed KB (UKB config) mattered more than KB size. No controlled KB-size sweep exists (gap).
- **Classical AI (acbdb94a):** the "big knowledge base = understanding" hypothesis was classical AI's CENTRAL BET (Schank scripts/CD, Minsky frames, Feigenbaum/Lenat Cyc ~10^8 axioms) and was NOT vindicated. Three failure modes: (a) knowledge-ACQUISITION cost (Feigenbaum bottleneck -- expensive to formalize each fact, not raw insufficiency); (b) combinatorial/brittleness (scripts don't scale -- selection + interaction explode); (c) Winograd's philosophical objection (understanding != an enumerable set of explicit facts). The Winograd Schema Challenge (built to REQUIRE commonsense) was ultimately "solved" by statistical/neural scaling over text, NOT by Cyc-style hand-built KBs.

**=> For our substrate:** foundation must be GROWN (read->grow), statistically, and provide DISAMBIGUATION statistics (selectional/thematic-fit) -- not merely be large or hand-built. Raw foundation SIZE is not the lever; grown-disambiguation-knowledge-used-for-parsing is. This directly connects the reading pipeline to the ingest-gate + grounding work.

---

## DRILL 2 — WORKING MEMORY / CAPACITY (a7c2eaa7) — LANDED = SWEEP COMPLETE (note: research_wm_barrier_glassbox_parsing_2026-07-17.md)

**VERDICT: WM hypothesis REFUTED IN ITS NAIVE (capacity) FORM -- confirms #4 + reinforces #1. P_defl 0.30-0.45.**
- Bio: "bounded WM buffer capacity" (Just&Carpenter) is CONTESTED not consensus; general WM span correlates WEAKLY with ONLINE incremental parsing; best-supported mechanism = Lewis&Vasishth cue-based content-addressable RETRIEVAL-WITH-INTERFERENCE, NOT a slot-count/capacity construct.
- ML: incremental structural memory (dependency parser / Stack-LSTM 93.1 vs flat feedforward 91.8 UAS) beats flat-window -- **BUT this IS the barrier-#1 dependency-parser fix, NOT a separate WM intervention.** Beam search alone = modest.
- Classical: chart-parsing memoization = pure EFFICIENCY (extensionally == backtracking), NOT an accuracy/capacity lever.
- **=> the USEFUL part of "WM" (incremental structural memory) FOLDS INTO the #1 broad-parser fix -- adopting the parser delivers it for free. WM-as-CAPACITY (the user's hypothesis) is NOT the barrier.**
- ONE genuinely DISTINCT surviving WM lever: content-addressable INTERFERENCE-AWARE RETRIEVAL for long-distance / COREFERENCE argument resolution (connects to our coref resolver; cheap separate test, gates before building more coref).
- Do NOT copy the human ~2-3-deep center-embedding bound (a limitation, not a capability).

---

## ✅ SWEEP COMPLETE (all 5 drills). UNIFIED PRESCRIPTION:
Adopt the **broad-construction dependency / clause-typology parser** (delivers barrier #1 AND the useful part of #4-WM) + **integrate subcat/selectional lexicons** (VerbNet-first; barrier #2) + **reuse the surprise-gate for graded disambiguation** of ambiguity residuals (barrier #3) + **interference-aware retrieval for coreference** (the one distinct WM lever). Foundation-size (#5) is later / for grounding, not for parsing. The user's "just foundation-size and/or WM" is refuted by ALL FIVE drills + the Rung-9 empirical tail-confirmation.

## DRILL 3 — PREDICTION vs HARD-RULE disambiguation (a78aeb72) — LANDED (note: research_hardrule_vs_predictive_parsing_barrier_2026-07-17.md)

**VERDICT: confirms barrier #3 (prediction is a REAL, DISTINCT axis, NOT the same as rule-coverage) + maps it to OUR data. P_defl 0.62-0.70 (bio/ML/history).**
- Bio: surprisal / parallel-constraint-satisfaction. ML history: glass-box PCFG/CRF/supertagging BEAT hard structural heuristics by ~25 pts on identical disambiguation decisions.
- **DIRECT to our data: the Rung-5b/8 residuals (reduced-relative-clause-on-subject, compound-noun-head) are UN-FIXABLE BY ANY HARD RULE -- they need GRADED FREQUENCY/log-odds scoring.** => part of the onion-peeling tail isn't "more hard rules" (coverage) but "needs a graded scorer" (prediction).
- **Glass-box predictive parsing IS achievable + we ALREADY HAVE THE PRIMITIVE: named, auditable log-odds counts = the SAME quantity as our existing surprise/ingest-gate KL.** But it's a MINORITY TAIL, not the dominant bottleneck (consistent w/ Drill 5's #3). Reuse the surprise-gate machinery for graded parse disambiguation.

## DRILL 4 — GROUNDED / RICH LEXICON (a0111119) — LANDED (note: research_lexicon_richness_subcategorization_barrier_real_prose_parsing_2026-07-17.md)

**VERDICT: confirms + sharpens barrier #2. The lexicon barrier is SYNTACTIC richness (SUBCATEGORIZATION frames + selectional restrictions), DISTINCT from foundation/world-knowledge SIZE (#5) -- and it is an INTEGRATION problem NOT a research problem: VerbNet/FrameNet/PropBank/WordNet already exist, free, symbolic, non-LLM => a MATERIALLY CHEAPER lever than foundation scale-up. VerbNet uniquely FUSES syntactic frames + thematic-roles/selectional-restrictions in one entry -> first resource to ingest for BOTH the syntactic (word->subcat) AND semantic (word->concept) lexicons.**
- METHODOLOGICAL WARNING (load-bearing): needs a 3-ARM test -- NO-LEXICON / LEXICON-ONLY / LEXICON+GRAMMAR -- to avoid the Klein&Manning-2003 attribution error (some apparent "lexicon" gain is really grammar/category-granularity). A 2-arm test repeats a 20-yr field-level mistake.
- CHEAPEST first step (no build): COVERAGE-AUDIT -- what fraction of real-prose verb tokens fall inside subcat/selectional resource coverage, and does lexicon-richness genuinely SEPARATE from foundation-size (Prediction 2)? Gates whether the subcat-table build is worth it.
- Handoff (anchors: coverage-audit -> 3-arm parse test -> glass-box-purity check) archived to routed_completed.

## DRILL 5 — EXISTENCE-PROOF + achievable glass-box architecture + RANKED barriers (a416afcf) — LANDED = THE CANONICAL SYNTHESIS

**Full note: `notes/research_glassbox_reading_synthesis_ranked_barriers_2026-07-17.md` (read it -- comprehensive: human-parser decomposition, glass-box systems table incl. CCG, minimal architecture, 5-arm ablation test, falsifiable predictions). P_deflated=0.45.**

**RANKED BARRIERS (most->least load-bearing for ACHIEVING a glass-box parse of real prose):**
1. **CORE-SYNTAX / CONSTRUCTION COVERAGE** -- EMPIRICALLY confirmed the dominant bottleneck by TODAY's HARD_FAIL (58.6% unhandled constructions, precision collapse). The ONLY barrier with a direct same-week MEASUREMENT (not just literature). Fix = adopt the published ClausIE-class clause-typology toolchain (known, benchmarked, diagnosed).
2. **LEXICON QUALITY** (word-meaning ATTACHMENT / disambiguation, NOT raw vocab size) -- Perfetti Lexical Quality Hypothesis names the lexicon (not syntax/reasoning) as humans' deepest comprehension bottleneck; the word->meaning LEARNING RULE is genuine unsolved novel-synthesis for us.
3. **PREDICTION / probabilistic disambiguation** -- real quality/robustness lever (surprisal reanalysis) but literature CONTESTED (Nieuwland 2018 non-replication of pre-activation); not shown to be a hard precondition.
4. **WORKING MEMORY / incremental-parse capacity** -- real + brain-matched (N/16 cliff, F=3-4, ~2-3 nesting) but NOT binding at the current stage (today's HARD_FAIL was on ordinary-length sentences well within WM budget); a LATER-stage concern.
5. **FOUNDATION / world-knowledge SIZE** -- LEAST load-bearing for parse achievability ("the cat sat on the mat" parses with zero world knowledge); matters for what the parse GROUNDS TO, not for parsing itself.

**=> DIRECT VERDICT ON THE USER HYPOTHESIS: NO, it is NOT "just foundation-size and/or working memory" -- those rank LAST (#5 and #4). The dominant, empirically-confirmed barrier is CORE-SYNTAX / CONSTRUCTION COVERAGE (#1), with LEXICON-MEANING-ATTACHMENT (#2) a close second. THREE independent traditions converge (developmental-linguistics curriculum ladder + comp-linguistics clause typology + reading-comprehension individual-differences: inference/lexical-quality deficits, NOT WM/knowledge-size, discriminate poor comprehenders).**

BRAIN NUANCE (load-bearing): the human parser does NOT gracefully abstain -- "good-enough parsing" commits to confident WRONG parses (SAME failure as our spurious-firing) -> the strict abstain gate is a substrate-NATIVE precision advantage (beat the brain), consistent with the earlier brain-check drill.

MINIMAL GLASS-BOX ARCHITECTURE (Drill 5 sec c): ClausIE-class clause-typology parser (on a classical/narrow-neural-closed-output-space dep parse) + CALM coordination pre-split + RELNOUN + Hearst + OPEN relation vocab + strict abstain-on-partial-match gate + Hobbs/centering coreference + learned lexicon lookup table (on the SHARED role-filler binding scaffold = structure-content unification) + hierarchical-chunking WM + two-tier CORE+MODULE foundation + small structured-grammar surprisal signal. CCG-to-logical-form flagged as an alternative unifying parse+binding (next-drill candidate).

---

## DRILLS 2/3/4 STATUS: re-dispatched/pending -- will DEEPEN the individual positions (#4 WM, #3 prediction, #2 lexicon) but Drill 5 (empirically anchored by the HARD_FAIL) already delivers the ranked verdict; 2/3/4 confirm-or-refine mid-rankings, won't overturn #1/#5.

---

## RANKED-BARRIERS VERDICT: SEE DRILL 5 ABOVE. BUILD PLAN (Director, from the sweep):
1. **Adopt the classical clause-typology toolchain (ClausIE-class) FIRST** = attack barrier #1 (construction coverage), the empirically-confirmed dominant wall. This CONVERGES with the earlier "classical-toolchain fork" -- the sweep RESOLVES that fork: it is NOT optional, it is the #1 lever. (The interpretive Q for USER -- "rule-based IE" vs a trained-but-inspectable statistical/narrow-neural-closed-output parser -- still stands, but the sweep says a broad-construction parser is REQUIRED to get past the wall; ReVerb-class pure-POS-pattern is structurally blind to ~15% of relations.)
2. **Lexicon learning-rule SECOND** (barrier #2; cheap decisive test, 8-12 Dolch words, parallel to #1).
3. **DEFER further WM + foundation-size investment** (barriers #4/#5, not binding now) pending the 5-arm ablation (Drill 5's cheap decisive test) -- confirm they're not-yet-binding before more investment there.
4. Run Drill 5's **5-ARM SINGLE-LEVER ABLATION** on the same HARD_FAIL eval set to empirically CONFIRM the ranking (core-syntax lever should give the largest single-lever gain).

## EMPIRICAL CONFIRMATION OF THE #1 VERDICT (Rung-9, bf86a67fa, claim/VET-pending)
The hand-peeling arc's latest rung landed a DUAL result that INDEPENDENTLY confirms barrier #1: (a) POSITIVE -- first high-coverage-high-precision milestone (precision 0.526->0.747 at coverage 0.307; 4 general/nonce-verified additive bug fixes; guardrail 0/32; neural-free) => the glass-box pieces CAN reach the envelope on constrained register; (b) CONFIRMING -- the 26 still-wrong rows surfaced TWO BRAND-NEW construction patterns (bare-adjunct over-extraction; modal-mistagged-as-matrix-verb) that were NOT among the 4 fixed bugs => the "fix a batch, next batch surfaces" ONION-PEELING CONTINUES. => the empirical arc and the barrier sweep now agree INDEPENDENTLY: hand-peeling reaches a milestone but has a persistent CONSTRUCTION-COVERAGE tail (barrier #1) -> a BROAD-CONSTRUCTION PARSER is the fix, not more hand-rules. This is the on-disk empirical anchor for adopting the clause-typology parser.

## FRONTIER MEASUREMENT (ReVerb, read_grow_realprose_reverb_classical_v1 8bc24448e, claim/VET-pending) -- BREADTH CONFIRMED, DISAMBIGUATION MISSING
JVM unavailable on host -> ClausIE/MaltParser (Java) blocked; measured the LIGHTEST glass-box-legal option = pure-Python ReVerb (nltk POS-patterns + RegexpParser, NON-NEURAL confirmed, NO dependency parse). Head-to-head vs toy grammar on the SAME UD-EWT 210-slice: coverage 0.119->0.714 (6x), recall 0.068->0.297 (4.4x), precision 0.179->0.083 (DROP). HARD_FAIL its bands. => BREADTH is decisively the COVERAGE lever (confirms barrier #1), BUT breadth via flat POS-patterns OVERGENERATES (precision drops -- coordination-scope / embedded-clause / non-"by"-passive errors; excluding the zero-gold other_unhandled bucket precision still only 0.158 = real overgeneration, not just a scoring artifact). This measured the classical FLOOR (ReVerb, no parse), NOT the parse-based frontier (ClausIE, JVM-blocked). **CONVERGENCE with the brain synthesis: ReVerb = breadth WITHOUT disambiguation -> overgenerates; the brain gets breadth AND precision because its construction inventory is used PREDICTIVELY (surprisal-scored) with feedback = prediction IS the disambiguation. So the measurement empirically shows the exact gap the brain-faithful design fills: breadth NEEDS structural/predictive disambiguation for precision.** Two follow-ups IN FLIGHT: (1) ENGINEERING-bridge = real-parse frontier via a pure-Python non-neural trainable transition parser (ac3da775 -- does a real PARSE recover precision over ReVerb while keeping coverage?); (2) BRAIN-FAITHFUL = grow-constructions-from-reading feasibility probe (adbcddeba -- does a grown surprisal-scored inventory get breadth+precision?). These run HEAD-TO-HEAD = the adopt-parser-vs-grow-from-reading decision.

## GROW-FROM-READING v2 (schema abstraction + predictive precision, f9dfd7f27, claim/VET-pending) -- SPLIT: abstraction WORKS, precision needs SEMANTICS not frequency
ARM A (ABSTRACTION) = HARD_PASS (VET a8b5a3f8 in flight): schematization (function-word-dropping) GENERALIZES to genuinely UNSEEN construction shapes (~0.28 vs ~0.17 scramble on shapes flat covers 0), SAMPLE-EFFICIENT (flat's ceiling at 41% exposure), NON-PLATEAU => the multi-level/abstraction architecture (USER steer: higher levels abstracted from exemplars) is REAL: flat fragments plateau, abstract schemas generalize. (VET-crux: does it beat a FAIR random-same-size baseline, not just scramble -- v1's lesson; margin may ~halve.)
ARM B (PREDICTIVE PRECISION) = HARD_FAIL, and STRATEGICALLY the key redirect: grown+predictive-use precision peaks 0.128 (> ReVerb 0.083 but < toy 0.179, << 0.30 target); SURPRISAL-disambiguation margin over random-tiebreak = -0.0017 = surprisal NOT load-bearing (confirms v1 VET: "surprisal"=relabeled frequency); more frequency-gating makes precision WORSE. => **PRECISION does NOT come from prediction/frequency (barrier #3 as raw-induction-frequency) -- it needs a SEMANTIC/SELECTIONAL-PLAUSIBILITY signal = BARRIER #2 (subcat/selectional lexicon, VerbNet).** So: BREADTH = entrenchment (v1) + abstraction (v2 ARM A) [working]; PRECISION = selectional semantics [next lever, barrier #2, NOT frequency-surprisal]. Re-run the coverage-audit (outage casualty) + build a selectional-precision signal = the precision path. (Also: local_cpu_queue runner is DOWN post-infra-cleanup -- cells run inline/foreground fine; restart the runner only if queue dispatch is wanted.)

## #1-BUILD HEAD-TO-HEAD COMPLETE (precision, same UD-EWT slice/gold; all claim/VET-pending):
| approach | prec | cov | read |
| toy hand-rules | 0.179 | 0.119 | baseline |
| ReVerb (breadth, no parse) | 0.083 | 0.714 | breadth, OVERGENERATES |
| REAL PARSE (trained transition, LinearSVC non-neural; 74f8de97a; VET aedf80eb leak-check) | **0.347** | 0.310 | precision QUADRUPLES ReVerb, beats toy; MIDDLE_BAND partial (short of 0.40/0.40; passive 0/15 gap) |
| grown+predictive (v2 ARM B) | 0.128 | 0.533 | breadth, precision SHORT (surprisal not load-bearing) |
**STRATEGIC READ: (1) PRECISION lever = STRUCTURAL/SELECTIONAL disambiguation (real parse recovers it 0.083->0.347; grown-frequency does NOT) -> confirms precision needs structure/semantics (barrier #2 selectional), NOT frequency (barrier #3 as raw-freq). (2) BREADTH lever = entrenchment + ABSTRACTION (grown v2 ARM A generalizes to unseen). (3) NEITHER hits the classical envelope (0.40/0.40) ALONE -- both honest MIDDLE/partial. => #1 BUILD = COMBINE: grown/abstracted inventory (breadth) + structural/selectional disambiguation (precision). Engineering real-parse = a working glass-box-legal BRIDGE (0.347, inspectable LinearSVC, treebank-trained="installed"); brain-faithful grown-inventory = breadth + needs the selectional-semantic precision signal. NEXT precision levers: passive-detection fix (cheap, parser 0/15) + SELECTIONAL semantics (VerbNet, barrier #2 = the outage-casualty coverage-audit re-run).**
