---
problem: the_extraction_front_end_parser_is_the_cross_task_bottleneck_needs_a_significantly_better_parse
status: SOLVED
bar: "PASS = the substrate's OWN glass-box parser, improved (via the in-substrate arc-eager + global-training infra, NOT an LLM), simultaneously: 1. raises who-did-what structural patient selection CI-separated over the current arc_parser (0.515) toward the spaCy level (0.588+) on the held-out QA-SRL science test, reported as parse-attach PRECISION on ARGUMENTS, not just overall UAS; 2. holds a UAS/LAS gain on the UD-EWT test set; 3. COMPOUNDS -- measure >=1 SECOND downstream task and show the gain carries; 4. does NOT regress the competing needs -- an explicit MUST-NOT-REGRESS check on argument RECALL (N2), POS/lemma (N4), and the 19c arm treated as a SEPARATE sub-goal; 5. reports the emitted confidence/distribution (N7). A rigorous located negative -- the in-substrate parser CANNOT be brought to spaCy level with the available infra, OR two needs are provably non-co-satisfiable -- is a FULL PASS if it names which need, the number, and the mechanism."
result: "Improved parser = arc-eager incremental heads + RICH NON-LOCAL STRUCTURAL FEATURES (Zhang-Nivre 2011; dependents/valency/head-of-stack) -- UD-EWT test UAS 0.8421 gold-POS / 0.8053 pred-POS vs the LIVE richfeat 0.775/0.744 (GAIN +0.067/+0.061) -- + LABEL-FREE thematic role recovery (drop the harmful arc_labeler) + an emitted calibrated attachment distribution. who-did-what patient (QA-SRL science, FULL n=2423): 0.5147 -> 0.5477, +0.0330 CI[+0.0194,+0.0462] frac<=0=0.000 (HARD n=1296: +0.0903 CI[+0.070,+0.110]); 19c LitBank FULL n=3015: 0.2610 -> 0.3668, +0.1058 CI[+0.094,+0.118]. Argument-attach PRECISION on UD-EWT (rich arc-eager vs live richfeat): object(->patient) 0.9508 vs 0.9249 +0.0259 CI[+0.012,+0.040]; subject(->agent, the 2nd role/task) 0.9001 vs 0.8569 +0.0469 CI[+0.033,+0.061]; passive-subject 0.833 vs 0.716 +0.117; oblique/recipient 0.716 vs 0.637 +0.079; BURIED-subject (long-arc) 0.406 vs 0.281 -- the rich features RESOLVE the prior error-propagation regression. N7: arc-eager attach-conf/graded_competition-entropy predict who-did-what errors AUC 0.694 (QA) / 0.764 (19c), shuffled-confidence twin AUC 0.506/0.488. WALL PARTLY CROSSED: the ~0.81 UAS ceiling survived richer SEARCH (global-beam HARD_FAIL 0.809 vs 0.811) and richer LEXICAL features (GloVe clusters +0.0015) but the STRUCTURAL rich-feature lever crosses it (+0.024, 0.818->0.842); residual to spaCy ~0.90 is a deeper representation/domain gap, follow-on = a richer representation class + gold target-domain data."
floor: "Live baseline BASE_CURRENT = richfeat heads + arc_labeler LABELED = 0.5147 (= the parent-measured 0.515) on QA-SRL FULL; position floor 0.3743; richfeat UAS 0.775 (gold-POS) on UD-EWT test. All improved arms gated CI-separated over these strongest floors actually run."
controls: "(1) info-free HEAD twin -- shuffle the arc-eager head assignments -> who-did-what collapses to 0.346, improved arm beats it +0.195 CI-sep (QA) / +0.164 (19c). (2) info-free CONFIDENCE twin -- shuffled difficulty score -> N7 AUC 0.507/0.490 (~chance) vs the real 0.708/0.761. (3) label-free vs labeled ISOLATION on the SAME heads -> excludes 'better heads' as the modern lever (arc-eager vs richfeat heads on modern who-did-what is ns, -0.0037; the modern gain is entirely the labeler-drop +0.0297 CI-sep). (4) global-beam-vs-local ISOLATION on disk (HARD_FAIL) -> excludes the brief's search route. Each control excludes a specific alternative explanation."
files_changed: "experiments/exp_parser_gap_decomp_v1.py (disambiguation), experiments/exp_arceager_parser_operator_v1.py (arc-eager operator train+persist+parse+confidence; model data/frontend_assets_exp/arceager_dynamic_ud_ewt.npz), experiments/exp_parser_multiobjective_v1.py (multi-objective eval), experiments/exp_parser_argument_attach_v1.py (per-argument attach precision + 2nd task), experiments/exp_arceager_cluster_features_v1.py (word-cluster lever, null), experiments/exp_arceager_richfeat_transition_v1.py (rich non-local STRUCTURAL features -- the wall-crossing lever, +0.024), experiments/exp_parser_graded_cue_integration_v1.py (reliability-weighted graded cue integration -- MAP boundary), verification/test_parser_improved_operator.py (witness), notes/problems/<slug>/CONSUMER_FIDELITY_MAP.md, FINDINGS_disambiguation.md"
reverify: ".venv/Scripts/python.exe verification/test_parser_improved_operator.py"
---

# The parser IS the cross-task ceiling -- but "better" means better AT SERVING ITS CONSUMERS, not a higher 1-best UAS chasing spaCy

**Bottom line: SOLVED as a multi-objective improvement WITH a rigorously located negative.** The substrate's own
glass-box parser is made significantly better on every downstream need the bar names -- who-did-what (modern +
19c), argument-attach precision across roles, argument recall, and a usable confidence distribution -- by three
changes, each measured with can-fail floors and info-free twins. AND the brief's headline route (raise the
in-substrate UAS to spaCy level via global training) is shown REFUTED ON DISK, with the residual to spaCy named
and quantified. Per the bar, that combination is a full PASS.

## WHAT I BUILT (the improved parser = 3 changes, each a REUSE, not a reinvention)
1. **Arc-eager incremental heads + RICH NON-LOCAL STRUCTURAL FEATURES, promoted to a loadable `parse()` operator**
   (`exp_arceager_parser_operator_v1`). The live frontend loads the WEAKER arc-FACTORED `richfeat` (UD-EWT test UAS
   0.775 gold-POS / 0.744 pred-POS); the arc-eager transition parser with a dynamic oracle (reused bit-identically
   from `exp_depparse_transition_arceager`) reaches 0.8184, and adding Zhang & Nivre 2011 rich non-local structural
   features (leftmost/rightmost dependents, valency, head-of-stack -- a structured working-memory buffer) reaches
   **0.8421 gold-POS / 0.8053 pred-POS -- a UAS gain of +0.067 / +0.061 over the live parser** (bar objective 2).
   This is the brain-faithful INCREMENTAL shape (Now-or-Never; Christiansen & Chater 2016) with a STRUCTURED buffer,
   the fix the audit named for arc_parser's two weaknesses (batch + UAS cap). It emits a per-attachment confidence
   (softmax over legal actions + raw margin) -- the graded-distribution signal the arc-factored parser's
   uncalibrated margins never gave.
2. **LABEL-FREE thematic role recovery** (drop the arc_labeler; recover the patient from head-attachment + POS +
   VOICE + position). This is the single biggest deployable who-did-what lever and needs no retraining.
3. **A calibrated attachment DISTRIBUTION** fed to the landed `graded_competition` organ (N7) -- the parser now
   emits the maintained-distribution signal the graded organs need.

## THE KEY REALIZATION (the move that unstuck it) -- the disk confirmed a brain-fidelity prediction BEFORE any build
The owner's directive was to optimize the parser for the organs that CONSUME it, weighting each consumer by its
brain-foundational fidelity. I mapped every consumer (`CONSUMER_FIDELITY_MAP.md`) and predicted, from fidelity
alone, that the **arc_labeler's explicit grammatical-relation labels (dobj/nsubj) are a LOW-fidelity
OUR-INVENTION** -- the brain binds THEMATIC roles (agent/patient) from structure + voice, not linguists'
grammatical labels -- and therefore probably dead weight on the live role path. The disambiguation
(`exp_parser_gap_decomp_v1`) then measured exactly that, before I built anything: swapping a LABEL-FREE role rule
onto the SAME frontend heads **beats the labeled rule +0.030 CI-sep on modern and +0.107 on 19c** (frac<=0=1.0);
the labeler is not merely useless, it is actively HARMFUL. The enabling move was **treating a consumer's
brain-fidelity as a testable prediction about what the parser should emit**, which turned "raise UAS" (refuted on
disk) into "stop forcing the output through a non-brain-faithful labeling step." A second realization: **the disk
outranks the brief** -- the brief's global-training route was already HARD_FAILED on disk (0.809 vs 0.811), so I
solved the real problem underneath by a different, more brain-faithful route. A third realization (the wall drill):
**a shared wall across two levers is NOT a ceiling -- go FINER.** After richer search (global-beam) and richer
lexical features (word clusters) both failed to lift the 0.81 UAS ceiling, the FINER structural drill -- rich
non-local features over a structured working-memory buffer (Zhang-Nivre; the brain's bounded-but-structured
buffer) -- crossed it +0.024, and as a bonus RESOLVED the buried-subject regression. The near-declaration of "wall"
after two failures was the trap the protocol exists to catch.

## THE FULL DISAMBIGUATION (owner: "fully disambiguate where we lose the signal the entire way")
The +0.073 arc->spaCy who-did-what gap decomposes (QA-SRL FULL) into: **HEAD-ATTACHMENT +0.028** (labels off both)
+ **a LABELER swing +0.045** (frontend labeler HURTS -0.030; spaCy labeler helps +0.015). So most of the gap is
the labeler, not the parse. Signal path, end to end:
- position floor 0.374 -> the parse adds +0.140 (structure beats position) -> the LABELER subtracts 0.030 (net
  live baseline 0.515) -> dropping the labeler recovers +0.030 (0.544) -> arc-eager heads add ~0 on modern
  canonical (word-order-saturated) but +0.085 on modern HARD and +0.111 on 19c -> gold-attach oracle 0.991 is
  the selection ceiling once the argument is attached.

## RESULTS vs THE BAR (each objective, with its floor and control)
1. **who-did-what CI-sep over 0.515, as argument-attach precision** -- YES. QA-SRL FULL 0.5147 -> **0.5477,
   +0.0330 CI[+0.019,+0.046]**; HARD +0.0903; 19c +0.1058. Argument-attach PRECISION on UD-EWT (rich arc-eager vs
   live richfeat): object(->patient) **+0.0259 CI[+0.012,+0.040]**, subject(->agent) **+0.0469 CI[+0.033,+0.061]**,
   passive-subject +0.117, oblique/recipient +0.079. Reaches 0.548 of spaCy's 0.588 (the residual is the located
   negative, below).
2. **UAS/LAS gain on UD-EWT** -- YES (UAS). rich arc-eager **0.8421 vs 0.775 (+0.067)** gold-POS; +0.061 pred-POS.
   *LAS is deliberately not the objective*: the labeler that would produce labels is the harmful component (finding
   above), so the parser is UNLABELED-by-design and I report UAS + per-argument attach precision instead.
3. **COMPOUNDS to a 2nd task** -- YES. The same parse improvement lifts a DIFFERENT role: subject/AGENT attachment
   +0.0469 CI-sep (vs the patient/object side +0.0259), the oblique/RECIPIENT attachment +0.079 (the structural
   input to world-state role recovery), and it RESOLVES the buried-subject long-arc case (0.281 -> 0.406). The gain
   is not who-did-what-specific.
4. **No regression on recall / POS / 19c** -- YES, and 19c is a large GAIN not a regression. Argument RECALL
   (coverage of emitted patients) RISES 0.183->0.304 (QA) and 0.080->0.323 (19c): label-free recovers MORE
   arguments (the labeler was dropping them). POS/lemma unchanged (the parser consumes POS, does not produce it).
   19c who-did-what +0.111 CI-sep.
5. **Confidence/distribution (N7)** -- YES, and correctly SCOPED. arc-eager attach-confidence + `graded_competition`
   entropy predict who-did-what errors **AUC 0.708 (QA) / 0.761 (19c)**; shuffled-confidence twin AUC 0.507 / 0.490
   (chance). And I tested the tempting over-reach -- reliability-WEIGHTING the structural cue by its confidence
   (Ernst-Banks optimal cue combination) to try to LIFT accuracy (`exp_parser_graded_cue_integration_v1`): it does
   NOT help, it slightly HURTS (GRADED_CONF vs the hard rule -0.0169 CI-sep on modern; ns on 19c; twin loses
   +0.19). This is the `graded_competition` MAP-optimality THEOREM confirmed on this task: the maintained
   distribution CANNOT beat its own argmax on accuracy -- its value is UNCERTAINTY (the N7 difficulty/abstain
   signal), not the point estimate. So the confidence is correctly wired as a difficulty flag, not a selector.

## THE WALL: a fidelity gap I built PART-way across, with the residual precisely located
The ~0.81 arc-eager UAS ceiling was probed with three levers, and this is the story the SOLVER PROTOCOL asks for
(a wall is a fidelity gap to build across, not a ceiling). (a) The sanctioned SEARCH lever -- GLOBAL
structured-perceptron + beam early-update (Collins-Roark) -- **HARD_FAILED on disk**
(`exp_depparse_global_beam_earlyupdate`: 0.809 vs 0.811). (b) A richer LEXICAL representation (distributional
word-cluster features, K-means over GloVe-300; Koo 2008) adds only **+0.0015** (`exp_arceager_cluster_features_v1`).
(c) But the STRUCTURAL lever -- Zhang & Nivre 2011 rich non-local features (dependents / valency / head-of-stack;
a structured working-memory buffer, brain-plausible Now-or-Never-with-structure) -- **CROSSES it: +0.024
(0.8184 -> 0.8421)** (`exp_arceager_richfeat_transition_v1`), so the deployed parser is UAS 0.842 / 0.805 pred-POS
(+0.067 / +0.061 over the live parser). *The near-miss was the lesson: after search and lexical features both
failed I nearly declared the ceiling un-crossable; the FINER structural drill found the crossing.* The RESIDUAL to
spaCy (~0.90) is now precisely characterized -- NOT a search gap (refuted), NOT a shallow-lexical gap (refuted),
PARTLY a structural-feature gap (crossed +0.024); what remains is a deeper representation gap (contextual/neural
encoding, the OntoNotes-vs-UD annotation scheme) plus the UD-EWT->science DOMAIN shift. **Follow-on: a
richer-than-linear representation class + GOLD target-DOMAIN parse data (self-training refuted).** And the prior
buried-subject NON-TRANSFER (a greedy-transition error-propagation regression, 0.156 vs 0.281) is **RESOLVED by the
rich structural features** -- buried-subject attachment is now **0.406 vs the live 0.281**: the rich features fixed
the exact long-arc/attractor case they were added for.

## WHY THIS IS BRAIN-FAITHFUL (the opening move, not a tiebreaker)
English who-did-what is word-order-DOMINANT (Competition Model; Bates & MacWhinney): position alone is 0.374 and
an oracle object-decision adds only ~+0.028 on canonical, so a super-accurate 1-best tree is neither achievable
here nor the brain's route. The faithful shape is **position-dominant + cue-OVERRIDE (voice) with a maintained
distribution + a recovered-not-dropped argument set**, with the parse as ONE cue. That shape (a) serves every
consumer (calibrated distribution -> graded_competition; incremental heads -> the structure builder;
voice/position -> the role binder; higher coverage -> recall), and (b) is register-ROBUST: on 19c the modern
spaCy parser COLLAPSES (its heads score -0.10 vs the substrate's own for label-free roles) while the substrate's
own parser + label-free roles carries -- so the drop-in-spaCy path that wins on modern LOSES on 19c, and our-own
improved parser is the register-robust winner.

## ADJACENT-COMPONENT EVALUATION (owner directive: fidelity + optimization of each consumer -> next problems)
Full table in `CONSUMER_FIDELITY_MAP.md`. Brain-fidelity-weighted verdicts:
- **arc_labeler (explicit grammatical labels)** -- LOW fidelity (OUR-INVENTION); measured HARMFUL. **Follow-on:
  retire it from the live role path; roles are label-free.** The brain does not emit dobj/nsubj.
- **semantic_parser (HD-bundle intent + role-slot)** -- OUR-INVENTION placeholder (classical dialogue-NLU
  intent/slot frame), island, no live caller. **Follow-on: re-found on a brain-faithful role-binding basis or
  retire; its needs must NOT constrain the sentence parser.**
- **graded_competition (maintained distribution)** -- PINNED-faithful but its input (the parser's margin) was
  never emitted calibrated. Now served. **Optimization: temperature-calibrate the arc-eager confidence (it is
  discriminative AUC 0.71 but saturated ~0.99).**
- **positional default role path** -- degenerate (pure position, no cue-override). **Follow-on: make the graded
  wired role path default-on -- the parser's value is latent until then.**
- **predict_revise / verb_subcat / graded_role_assigner** -- PINNED-faithful, real needs, all served by
  head-attachment + voice + coverage; no change needed to their demands.

## AUDIT UPDATE (for BRAIN_FOUNDATIONAL_AUDIT.md sec.2b)
- The parser cross-task ceiling is now decomposed: **the arc_labeler is a HARMFUL low-fidelity component**
  (-0.030 modern / -0.107 on 19c who-did-what); the brain-faithful role recovery is LABEL-FREE (head-attachment +
  voice + position). The live frontend loads the WEAKER `richfeat` (UAS 0.775) though `hashed` (0.791), arc-eager
  (0.818), and the NEW arc-eager + rich-structural-features parser (**0.842**) are better.
- **The ~0.81 arc-eager ceiling is a STRUCTURAL-feature gap, not a search or lexical gap**: global-beam training
  HARD_FAILED (0.809 vs 0.811), GloVe word clusters added +0.0015 (both null), but Zhang-Nivre rich non-local
  structural features (dependents/valency/head) CROSS it +0.024 -> 0.8421 (`exp_arceager_richfeat_transition_v1`).
  The residual to spaCy (~0.90) is a deeper representation/domain gap. Do NOT quote the brief's global-training
  route as the lever -- it is refuted; the lever is rich structural features.
- The register-robustness verdict flips the "swap to spaCy" intuition: spaCy heads are WORSE than the substrate's
  own on 19c label-free role recovery (-0.10); the register-robust who-did-what path is our-own-parser + label-free.
- Confidence: arc-eager attachment confidence -> graded_competition entropy is a validated difficulty signal
  (AUC 0.71-0.76), same currency as predictive_reader surprisal.

## PROPOSED hdlab WIRE (Q111 -- strategy lands; default-off; witnessed)
1. Land the arc-eager + rich-structural operator as `hdlab/arceager_parser.py` (train+save offline; a
   `parse(tokens,pos)->heads+attach_conf` mirroring `arc_parser.ParseResult`, PLUS a per-arc confidence; the rich
   non-local features need the child/valency/head tracking through the transition), asset
   `arceager_dynamic_ud_ewt.npz` (UAS 0.842). Point `situation_reader._load_frontend()` at it behind a default-off
   `parser=arceager` flag (fallback = current richfeat).
2. In `predicate_argument_frontend` / `graded_role_assigner`, add a default-off `role_route='labelfree'` that
   recovers roles from head-attachment + voice + position, BYPASSING `arc_labeler` (the measured-harmful step).
3. Wire the arc-eager `attach_conf` -> `graded_competition` as the parser's difficulty signal (N7), shared with
   predictive_reader surprisal.
Acceptance gate: `verification/test_parser_improved_operator.py` (7/7). All default-off; the DEFAULT reader is
byte-identical.

## WHAT I WOULD WITHDRAW FIRST IF WRONG
The arc-eager UAS gain's downstream value on MODERN canonical who-did-what (it is ~0, word-order-saturated; the
modern who-did-what gain is the labeler-drop). If pressed, the modern who-did-what claim rests on the labeler-drop
(+0.030, robust, twin-controlled), not the head-attachment gain -- I keep those separable and do not conflate
them. The head-attachment gain is load-bearing on HARD/19c/argument-attach, where it is CI-separated.

## TLDR (plain English)
The reader's grammar-reader is the shared weak link under every ability. I found that the biggest problem was not
that it reads grammar badly, but that it then re-labels each word with a school-grammar tag (subject/object) that
the brain never uses -- and that tag was actively making "who did what" WORSE (by 3 points on modern text, 11 on
200-year-old text). Dropping the tag and reading roles straight from which word attaches to the verb, plus who is
active or passive, fixes that. I also swapped in a better, more brain-like left-to-right grammar reader and gave it
a structured short-term memory of the words it has already connected -- its accuracy on a standard test rose from
77.5% to 84.2%, which helps the hard and old-text cases and a second job (finding the DOER, not just the done-to),
and it fixed the one case (a subject far from its verb with a distracting noun between) that a simpler version had
made worse. The reader now also reports how confident it is, which reliably flags its own mistakes. One thing I
could not fully close: the last stretch to a small off-the-shelf parser's raw accuracy -- but I showed the two
cheap ways to close it don't work and the one that partly does, so what remains is a genuine next-step, not a
mystery.

## QUESTIONS
None blocking.

## NEXT STEPS
1. Strategy: land the three default-off wires above (arc-eager operator, label-free role route, confidence->
   graded_competition), re-verify with the witness.
2. Follow-on problems this seeds (each brain-fidelity-evaluated): retire the arc_labeler from the live role path;
   re-found or retire the `semantic_parser` placeholder; to cross the 0.81 UAS saturation, a richer-than-linear
   representation CLASS + gold target-DOMAIN parse data (the three cheap levers -- self-training, global search,
   word clusters -- are ALL refuted, so this is a genuine architecture step, not a tuning step); a long-arc /
   buried-subject fix for the incremental parser's error propagation; make the graded wired role path default-on.
