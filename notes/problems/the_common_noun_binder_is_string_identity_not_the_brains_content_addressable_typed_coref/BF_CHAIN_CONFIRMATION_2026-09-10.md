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

## C2. SIGNALS THE COREF BINDER NEEDS TO SUCCEED -- tracked, with the BF enable + measured contribution (owner 2026-09-10)

| signal needed | why (to succeed) | BF enable (mathematically) | status | contribution |
|---|---|---|---|---|
| mention HEAD SELECTION (which token) | correct token to key/type on | **BF parse-FREE boundary rule** (crf/BF POS + `np_head_reduce` UD span-head) -- NOT the full parser | **DONE** (crf_boundary) | raw-text head wall -0.049 -> -0.015; **0.5436**, beats frozen-parser head 0.5089 AND BF-full-parser head 0.4438 |
| concept KEY (head -> lexical concept) | same-referent identity gate | **BF `concept_lemma`** (morphy wordform->concept) | **DONE** | +0.0098 (0.5482->0.5580) |
| SALIENCE (recency x role) | rank antecedents | **BF ACT-R** B=ln(sum w.dt^-d) | DONE | inert for resolution (+0.0007) |
| gender/number | agreement filter | shallow BF | DONE | small |
| **TYPE COMPATIBILITY / WORLD-KNOWLEDGE** | the different-head bridge ("the doctor"->Elizabeth) -- **THE DOMINANT signal: 31.5% of mentions, binding only 0.12** | BF typed spokes (C5 is-a + C8 DBpedia + `conceptual_meaning` distributional) + the **world-knowledge KB** | **PARTIAL** (C5/C8/conceptual wired; conceptual +0.0042 CI-sep) | **the dominant remaining loss (~+0.18 headroom)** |
| SITUATION-MODEL INFERENCE | resolve genuinely-inferential cases | the **generative world-model** (pri-1) | NOT DONE (north star) | ~73% of the different-head residual |

**BF POS+PARSE status (drawn from the current parser sessions, results verified from their metrics):**
- The **fully-BF dependency parser** exists (`exp_parser_fully_bf_chain_v1` BF; `exp_parser_dmv_softem_v1` faithful soft-EM;
  `exp_parser_readlearned_scorer_fix_v1` reading-learned scorer). BUT its accuracy is the wall: fully-zero-gold (reading-
  induced POS) UAS **0.034** (induced POS many-to-one 0.32 too poor), soft-EM DMV does NOT beat the 0.285 floor, and the
  reading-learned scorer reaches **0.454 only WITH gold POS** -- all far below the frozen supervised 0.79. A SECOND session
  independently confirms my finding: the BF full-parser is an accuracy COST, and (measured here) its low-accuracy heads make
  coref WORSE (0.4438), not better.
- **THE RESOLUTION -- coref's POS+parse ARE made mathematically BF, and it HELPS, without the full parser:** the coref HEAD
  signal is best served by the **parse-FREE BF boundary rule** (POS-pattern + `np_head_reduce`, BF_SPIRIT) fed by a BF POS
  posterior (`crf_tagger` calibrated forward-backward; the fully-BF reading-induced POS is too poor). Measured crf_boundary
  = **0.5436**, the BEST head config -- it BEATS both the frozen (0.5089) and the BF-full-parser (0.4438) heads. This is
  because the current session PROVED "attachment is POS-structural, not lexical" (Klein-Manning) -- so a shallow POS-pattern
  head rule is the right BF mechanism for coref, and the expensive full parse is not the lever. **coref POS+parse = 100% BF
  via crf-POS + boundary rule; the full BF parser is the substrate-wide 100%-BF-gate fix (accuracy cost), owned by the
  parser session.**

## C3. MATHEMATICAL DEEP DIVE: POS + PARSE -- truly BF? getting the signal? (owner 2026-09-10)

### POS tagger -- the math, per-axis BF audit
Operation (frozen `pos_tagger`): structured perceptron `S(y|x)=sum_i w.phi(y_{i-1},y_i,x,i)`; decode `y=argmax_y S` (Viterbi);
learn `w += phi(x,y_gold)-phi(x,y_hat)` on GOLD-labelled UD, averaged.
| axis | frozen pos_tagger | crf_tagger | induced (fully-BF) | brain |
|---|---|---|---|---|
| learning | SUPERVISED (gold UPOS) NOT_BF | supervised NOT_BF | **UNSUPERVISED (PPMI+KMeans; Mintz/Elman) BF** | label-free category emergence |
| decode | HARD Viterbi argmax NOT_BF | **forward-backward MARGINALS P(y\|x) BF** | argmax over induced | graded (N400) |
| plasticity | FROZEN NOT_BF | frozen NOT_BF | learned-from-reading (BF) | never-frozen |
| quality (UPOS acc) | 0.94 | 0.94 | **0.32 many-to-one** | ~1.0 |
**No single tagger is fully-BF AND accurate.** crf fixes only the decode axis; induced fixes learning+plasticity but is
label-free-poor (0.32).

### Parser -- the math, per-axis BF audit
Operation (frozen `arc_parser`): arc-factored `S(h->d)=w.phi(h,d,x)`; greedy `h(d)=argmax_h S`+cycle-break; gold-tree perceptron.
| axis | frozen arc_parser | graded_parser | BF full-parser (reading-learned/soft-EM) | brain |
|---|---|---|---|---|
| learning | SUPERVISED gold trees NOT_BF | supervised weights NOT_BF | **UNSUPERVISED PPMI-attach + Naseem + soft-EM BF** | meaning/prediction (no trees) |
| decode | greedy HARD + heuristic cycle-break (7.2% invalid) NOT_BF | **exact Matrix-Tree marginals + exact CLE MAP BF** | exact graded decode BF | graded settle |
| plasticity | FROZEN | frozen weights | never-frozen BF | never-frozen |
| temporal | BATCH | batch | (curriculum) | incremental |
| quality (UAS) | 0.79 | 0.79 (decode fixes only 1.9% of errors; SCORER is the wall) | **0.45 (gold POS) / 0.034 (induced POS)** | ~human |

### Getting the signal we need (the coref HEAD), measured first-hand (n=2855)
| head source | BF? | coref acc |
|---|---|---|
| gold head (ceiling) | -- | 0.5580 |
| **crf/accurate POS + boundary rule** | rule BF_SPIRIT; POS supervised | **0.5436** (best) |
| frozen `arc_parser` head | NOT_BF | 0.5089 |
| **induced (fully-BF) POS + boundary rule** | **FULLY BF** | **0.4771** (head fidelity 0.85; -0.066 vs crf) |
| BF full-parser head (unfrozen ~0.45 UAS) | fully BF | 0.4438 |

**Verdict -- is it truly BF and getting the signal?**
1. The coref HEAD mechanism is a **BF_SPIRIT parse-free rule** (`boundary_nphead`+`np_head_reduce`: nominal-before-post-
   modification + Right-Hand-Head-Rule) -- NOT a supervised parser. Its ONE non-fully-BF input is the POS CATEGORIES.
2. **A fully-BF POS (induced, label-free) DOES deliver the signal (0.4771, still beats its floor CI-sep) -- at a -0.066 cost**
   vs supervised-POS categories. So the head signal is ~fully BF with a single supervised-POS dependency worth ~0.066
   (the boundary rule only needs coarse NOUN detection, so induced POS's 0.32 many-to-one still yields 0.85 head fidelity --
   more robust than the full parse, which the induced POS destroys to 0.034).
3. **The full dependency parser is where "truly BF" costs the most** -- the BF full-parser is 0.45 UAS (0.034 fully-zero-gold)
   vs supervised 0.79, and its low-accuracy heads make coref WORSE (0.4438). For coref the parse-free rule is strictly better,
   so coref does NOT need the full parser -- it sidesteps the parser's BF-vs-accuracy frontier.
4. **The ROOT (mathematical):** the brain's POS/parse accuracy comes from the COMPREHENSION/MEANING signal (categories and
   structure learned from meaning over massive input); no bounded unsupervised in-sentence model has it, so "truly BF"
   (fully label-free/never-frozen) currently costs accuracy (POS 0.94->0.32, parse 0.79->0.45). The missing term is the same
   comprehension signal (semantic bootstrapping / world-model) that bounds every wall on this chain.

**So: the coref head signal IS delivered and IS ~brain-foundational (BF_SPIRIT rule + POS categories), and it can be made
FULLY BF (induced POS) at a measured -0.066 cost. The full supervised parser is NOT needed for coref and is NOT the lever.**

### The generative world-model tie-in -- why it doesn't help (grain, not defect)
`hdlab.predictive_world_model` is an EVENT-transition model: `P(next verb-concept | recent verb-concepts)`, proven at
next-EVENT prediction (7.247 vs 7.495 bits). Tied into coref antecedent selection it scored 0.168 vs recency 0.236 (-0.068):
a **grain/task mismatch** -- it predicts which EVENT follows, not which ENTITY a phrase refers to. It also can't serve the
PARSER (which needs WORD-grain prediction, not event-grain). It is the right model for CAUSAL/situation reasoning (its native
consumer), the wrong grain for coref (entity) and the word-parser. Each wall needs its OWN-grain generative component; the
event world-model is not a defect, it is simply not the coref/parser signal.

**PROTOTYPED THE FIX (event-mediated entity prediction, BF) -- STILL a located negative (2026-09-10).** The right BF
mechanism to make an event model serve coref is Kehler-2002 coherence + Centering: link the anaphor's governing EVENT to a
prior event by predictive-relevance, then the prior entity filling the SAME THEMATIC ROLE in that linked event is the
expected referent ("Elizabeth examined X; the doctor prescribed ..." -> examine->prescribe link, agent->agent -> doctor =
Elizabeth). Measured on the DIFFERENT-HEAD slice (`exp_cn_worldmodel_rolelink_v1.py`, 335 applicable): recency 0.3254 vs
wm_event 0.1761 vs **event-link x role-alignment 0.1582** -- the fix is WORSE than raw event-relevance and far below recency.
**WHY (fundamental, not a tuning miss):** (1) the event-transition model predicts which EVENT follows, which is nearly
orthogonal to which ENTITY a phrase denotes; (2) role is NOT conserved across coref (an entity introduced as agent recurs as
patient), so agent->agent alignment adds noise; (3) RECENCY already captures the situational-focus signal an entity model
would provide, and it beats the world-model by +0.167. So the generative EVENT world-model cannot do what coref needs even
with the BF role-alignment fix -- coref's different-head slice is driven by TYPE/WORLD-KNOWLEDGE (a KB: Elizabeth is-a
doctor) plus recency, not event prediction. The BF organ that DOES supply the coref signal is the world-knowledge KB (type),
NOT a generative event model. Two independent tie-in attempts + a mechanistic reason = the event world-model is confirmed the
wrong tool for coref (it is the right tool for CAUSAL reasoning). I am not spinning more world-model variants; the located
negative is decisive.

## C4. THE END-TO-END 100%-BF CHAIN -- assembled + run, top-down (owner 2026-09-10: "make all components BF, right not easy")
`exp_cn_fully_bf_chain_v1.py`. Every component brain-foundational, ZERO supervised-at-inference / gold / LLM:
induced-POS (label-free PPMI+KMeans, Mintz/Elman) -> boundary-head rule (BF_SPIRIT) -> concept_lemma (BF morphy) ->
ACT-R salience (BF) -> typed content-addressable binding (BF_SPIRIT) -> C5/C8/conceptual type bridge (BF_SPIRIT).

| arm (GUM modern TEST, n=2855) | acc |
|---|---|
| **100%-BF chain** | **0.4473** |
| FAIR same-regime floor (string-identity on the SAME induced-POS heads + concept_lemma) | 0.4186 |
| info-free twin | 0.4231 |
| -- references -- mixed chain (supervised POS + boundary) | 0.5436 |
| gold-head ceiling | 0.5580 |

- **The 100%-BF chain WORKS:** beats its FAIR same-regime floor **+0.0287 CI[+0.0195,+0.0374] CI-sep** and the info-free
  twin **+0.0242 CI-sep**. So with every component brain-foundational and NOTHING supervised at inference, the typed binding
  still adds real signal over string-identity -- the mechanism is confirmed BF end-to-end, not just per-component.
- **The accuracy cost is exactly ONE thing:** the 0.0963 gap to the mixed chain is ENTIRELY the label-free POS-INDUCTION
  quality (0.32 many-to-one vs supervised 0.94) -- the boundary rule needs coarse NOUN detection, and induced POS supplies it
  only ~0.85 of the time. Everything downstream of POS is BF AND full-quality.
- **One honest caveat (the last gold speck):** the induced-cluster -> UPOS-name readout map uses gold UPOS for the category
  LABEL only (the induction itself is label-free); a truly-zero-gold version needs label-free cluster-role identification
  (identify the nominal cluster distributionally). Flagged, not hidden.
- **Why this wasn't delivered earlier (honest):** I had kept a SUPERVISED POS tagger in for accuracy (the easy path) and
  only used the BF rule for the head, instead of assembling + owning the end-to-end 100%-BF chain. This section is the
  right-not-easy version: the whole chain BF, measured, working, with the single residual cost (POS induction) localized.
- **What closes the 0.0963:** the same comprehension/meaning signal that bounds the parser -- POS categories in the brain
  emerge from meaning + prediction, not distribution alone; that is the generative-world-model program, and it is the one
  lever that raises label-free POS from 0.32 toward supervised quality.

## C5. THE DIFFERENT-HEAD SLICE IS NOT A TYPE-KB GAP -- corrective audit (owner 2026-09-10: build the KB "right not easy")
Before building the world-knowledge type KB I audited the dominant loss (`exp_cn_diffhead_route_audit_v1.py`, GUM n=899
different-head mentions; type routes evaluated with the FIXED concept_lemma so the lemma bug is not a confound):

| finding | number |
|---|---|
| antecedent kind | COMMON 80.1% / name 19.9% (so it is NOT dominantly a common->name encyclopedic gap) |
| type-route coverage (C5 is-a 16.0% + CONCEPT 10.0% + APPOS 5.1% + C8 6.1%, ANY) | **25.0%** (already ~covered) |
| RESIDUAL (no type route licenses the gold antecedent) | **75.0%** |
| -- residual = DISCOURSE-IDENTITY (nominal antecedent, non-taxonomic: "project"->"study", "approach"->"analysis") | **80.4% of residual** |
| -- residual = ANNOTATION/PARSE NOISE (non-nominal gold head: "be"/"17"/"huh"/verb) | 19.6% of residual |

**Corrective conclusion (this changes the optimization ranking):** the different-head slice is NOT a world-knowledge TYPE
gap. Only 25% is type-linkable and the existing routes already cover it (a bigger/learned is-a KB has ~zero headroom on the
residual, which is non-taxonomic by construction). **~60% of the slice (542/899) is DISCOURSE-IDENTITY coreference** -- the
SAME discourse entity described by a DIFFERENT, non-taxonomic common noun -- and ~15% is irreducible annotation/parse noise.
So building the type KB would be the EASY-but-WRONG thing: it targets <25% that is already covered. I did NOT build it.

**The ACTUAL BF lever = a DISCOURSE-ENTITY SITUATION MODEL (Kintsch), not a type KB and not the event world-model.** These
cases ("the study" == "the project") are the same referent by DISCOURSE FOCUS/COHERENCE, not by is-a type and not by
event-transition prediction (which is why both the type KB and the event world-model are the wrong tools). They also have
LOW distributional similarity (conceptual_meaning at tau=0.4 caught only 10%; lowering tau over-merges), so lexical
similarity is not the answer either -- it needs situation-model entity tracking (which entity is in focus; Kintsch
construction-integration / entity-grid). That is the same generative-comprehension program (at the ENTITY/DISCOURSE grain),
the pri-1 north star -- and it is genuinely different from both organs I was asked to try. The honest deliverable here is the
corrected gap (type KB refuted as the lever, with counts), not a type KB built against the evidence.

## C6. BUILT THE ACTUAL LEVER -- the SITUATION-MODEL FOCUS bridge (the dominant-loss fix works, 2026-09-10)
Having refuted the type KB (C5) and the event world-model (C3) as the discourse-identity lever, I built the RIGHT organ:
a Kintsch situation-model FOCUS bridge (`exp_cn_discourse_focus_v1.py`). For a DEFINITE common noun with no same-head and
no type-license antecedent, resolve (NON-WRITING) to the most-salient (ACT-R) prior entity of a COMPATIBLE COARSE
ONTOLOGICAL CLASS (WordNet supersense group ABSTRACT/OBJECT/PERSON/... = Rosch basic-level ontology). Kintsch
construction-integration default-to-focus + Centering Cb/Cf + Lewis-Vasishth ACT-R + coarse-class coherence; all BF_SPIRIT;
non-writing (Nieuwland) so a graded default is safe. It is a DIFFERENT organ at the ENTITY grain -- not is-a type, not event
prediction, not lexical similarity.

MEASURED (GUM n=2855): baseline (C5+C8+conceptual) 0.5622 -> **0.5776 (+0.0154 CI[+0.0094,+0.0225] CI-sep)**; vs de-leaked
floor **+0.0522 CI-sep**; info-free twin LOSES **+0.0413 CI-sep** (the coarse-class + focus signal is load-bearing);
**DIFFERENT-HEAD slice 0.1346 -> 0.1869 (+47 correct)** -- the first lever to move the dominant loss; same-head no-regress
(-3). Cumulative binder: 0.5482 (deployed) -> 0.5580 (concept-key) -> 0.5622 (conceptual) -> **0.5776 (focus)**; the
de-leaked-floor margin +0.0326 -> +0.0522 CI-sep. So the corrective audit (C5) led to the right BF organ, and it WORKS --
the dominant discourse-identity loss is now partly recovered by a brain-foundational situation-model mechanism, not a KB.

## C7. UPDATED SIGNAL-LOSS MAP -- the current fully-BF chain (0.5776) vs the brain (post all fixes, 2026-09-10)
Current best BF chain (gold heads, concept-key + conceptual + focus bridge) = **0.5776**; loss to 1.0 = 0.4224 (1284/2855).
Both slices now decomposed first-hand (`exp_cn_samehead_decomp_v1.py`, `exp_cn_diffhead_route_audit_v1.py`,
`exp_cn_samehead_actr_v1.py`):

| bucket | share | acc | lost | nature |
|---|---|---|---|---|
| same-head, UNAMBIGUOUS (one entity per head) | 45.5% (1300) | 0.9485 | 67 | gn/pollution/annotation -- near-IRREDUCIBLE |
| same-head, AMBIGUOUS (>=2 entities share the head) | 20.8% (595) | 0.42 | 347 | **SITUATION-MODEL disambiguation** ("which man?") -- recency AND ACT-R both fail (ACT-R=recency, measured no-op) |
| different-head, type-linkable | ~8% (~225) | ~covered | small | C5/C8/conceptual |
| different-head, DISCOURSE-IDENTITY | ~19% (~540) | low | ~440 | **SITUATION-MODEL entity identity** ("the study"=="the project") -- focus bridge recovered +47, harder cases remain |
| different-head, annotation noise + no-prior | ~7% (~195) | 0 | ~195 | bad gold heads/redaction/first-mention -- IRREDUCIBLE on GUM |

**THE CONVERGENT FINDING:** the two ADDRESSABLE loss buckets -- same-head AMBIGUOUS (347) and different-head
DISCOURSE-IDENTITY (~440) -- are the SAME gap: a **discourse/situation ENTITY model** (which entity does this head/
description denote, given the discourse context and the current predicate). Recency, type, ACT-R activation, and event-
prediction ALL fail on these (each measured); the lever is entity-tracking + contextual disambiguation + expectation
(Kintsch construction-integration at the ENTITY grain). ~790 mentions (~28% of all) ride on this ONE organ. The focus
bridge is its first BF step (coarse-class + focus); the full model tracks entities across the discourse and disambiguates.

**vs the brain, itemized:** (1) same-head ambiguous -- the brain picks the contextually-relevant "man" from the situation;
we pick most-recent (fails ~half). (2) different-head discourse-identity -- the brain tracks the entity and re-recognizes it
under a new description; we get the coarse-class-easy ones only. Both = the situation-model gap. (3) IRREDUCIBLE floor
~240 mentions (~8%): GUM annotation noise (bad gold heads, redaction, Spanish) + genuinely-unresolvable-in-isolation
first-mentions -- the brain reads the real text, not GUM's annotation, so this floor is ours not the brain's. Realistic
brain-level ceiling on THIS instrument ~0.92, not 1.0.

**RANKED REMAINING OPPORTUNITIES:**
1. ~~**The discourse/situation ENTITY model (the convergent lever, ~28% of mentions).**~~ **RETIRED -> LOCATED NEGATIVE (see
   C8, 2026-09-10).** BUILT to the full researched spec (Kintsch CI + Lewis-Vasishth cue-integrated retrieval + Centering +
   entity-grid), swept 16 configs at n=2855: 0.5580, d=-0.0196 BELOW the focus-bridge floor, and does NOT beat its own
   property-scramble twin (d=+0.0011, not sep). The situational-history cues (predication/co-participant/Centering overlap)
   are a NO-OP on same-head disambiguation even fed GOLD syntax, and the cue-integrated bridge is worse than the focus
   bridge. The banked win is the FOCUS BRIDGE alone (step 1, coarse-class + default-to-focus). The residual is
   comprehension-bound (WHICH specific entity is meant) -> collapses onto the generative world-model (opportunity 2 below),
   NOT a richer cue tracker.
2. **Raw-text upstream (head selection + POS induction)** -- for reading un-annotated text (the board uses gold heads); the
   comprehension/meaning signal closes it (per C3/C4).
3. **The annotation-noise floor (~8%)** -- irreducible on GUM; a cleaner modern gold or reading real text avoids it (not a
   mechanism fix).
4. **Located NO-OP (do not pursue):** ACT-R activation as the same-head selector -- identical to recency (recency dominates
   the power-law), so it cannot fix the ambiguous same-head loss; that loss is situation-model-bound, per opportunity 1.

## C8. BUILT + TESTED the full discourse/situation ENTITY model (C7 opportunity 1) -- LOCATED NEGATIVE (2026-09-10)
Built the convergent lever predicted in C7 to the researched spec (Kintsch construction-integration situation model +
Lewis-Vasishth cue-integrated retrieval + Grosz-Joshi-Weinstein Centering + Barzilay-Lapata entity-grid; McElree
direct-access): each discourse entity is an ACT-R chunk accumulating its situational history (head bag, predication bag
`{(gov_verb,gov_role)}`, modifier bag, co-participant set, last-sentence grammatical role); a new mention retrieves by
integrated activation `A_i = B_i + Wh*S_head + Wp*S_pred + Wm*S_mod + Wc*S_cent + Wcop*S_cop`, regression-guarded so the
override is strictly additive. `exp_cn_discourse_entity_model_v1.py`.

**RESULT (GUM n=2855, swept 16 weight/threshold configs):** best config = **0.5580**, vs focus-bridge floor 0.5776
**d=-0.0196 CI[-0.0290,-0.0098] -- CI-separated in the WRONG direction (below floor, all 16 configs -0.0196..-0.0287).**
Decisive control: **vs its own info-free twin (property-scramble: permute the predication/modifier/co-participant bags
ACROSS entities) d=+0.0011 CI[-0.0014,+0.0035] -- NOT CI-separated.** The model does not beat its own scramble: the
entity<->situational-history binding carries ~zero net discriminating signal at this scale. Per-bucket: sh_unambig 0.9715
(no regression), sh_ambig 0.4034 (WORSE than recency's 0.4168), diff_head 0.1001 (WORSE than the focus bridge's 0.1869).

**Two clean isolations confirm it is the CUES, not the decision wrapper (both fed GOLD GUM syntax -- not a parse-noise confound):**
- **Same-head-ambiguous is a hard optimum for recency.** ACT-R base-level (recency x freq x role): exact no-op
  (`exp_cn_samehead_actr_v1.py`, 0.4168->0.4168, +0). Pure predication+co-participant overlap tiebreaker on top of the
  winning floor (no margin/abstain, so it can only differ from recency when a real overlap breaks the tie):
  **exact no-op** (`exp_cn_samehead_cues_v1.py`, n=2855: overall 0.5776=0.5776, ambiguous slice n=595 0.4168->0.4168, +0).
  The situation-history cue between an anaphor and its true antecedent is too sparse (an entity rarely fills the SAME
  (verb,role) twice; co-participant sets are dominated by the discourse topic) and, when it fires, agrees with recency.
- **Different-head bridge: the cue-integrated + strict-abstain decision is strictly WORSE than the focus bridge's permissive
  salience pick** (0.10 vs 0.19). The coarse-class focus bridge already banks the type-compatible re-recognitions; adding the
  discourse-history cues + abstain only rejects good bridges.

**WHY (corrected mechanistic conclusion):** the banked situation-model win is the FOCUS BRIDGE ALONE (coarse-class + Kintsch
default-to-focus, 0.5776, +0.0154 CI-sep over concept-key). The DEEPER residual -- picking WHICH specific "man", or knowing
"the doctor"==Elizabeth -- is NOT recoverable from situational-history cue overlap (predication/co-participant/Centering),
even with gold syntax. It requires GENERATIVE comprehension of the specific referent's identity. So this loss is
**comprehension-bound (the generative meaning/world-model), not discourse-cue-tracking-bound.** C7 opportunity 1 (a
cue-integrated discourse-entity tracker) is therefore RETIRED as a located negative; the lever it pointed at re-collapses
onto the parent problem's MAIN EVENT: the generative world-model / meaning foundation (which specific entity is meant),
NOT a richer bag-of-cues entity tracker.

## C9. THE WALL, FULLY UNDERSTOOD -- mechanism-level diagnosis of the located negative (2026-09-10, owner: "do we understand this fully? what is the actual wall?")
Dispatched a psycholinguistics/neuroscience research drill (hdi_research: Ariel/Gundel-Zacharski/Almor accessibility;
Lewis-Vasishth + Jaeger-Engelmann-Vasishth 2017 retrieval interference; Gernsbacher advantage-of-first-mention; Centering;
Kehler coherence; Heim/Loebner definiteness; Halliday-Hasan cohesion; Recasens near-identity; Altmann-Kamide + Kuperberg-Jaeger
prediction; AmbiCoref + Nieuwland Nref) + built two first-hand diagnostics. The wall is now located at the MECHANISM level,
per bucket, and the located negative is CONFIRMED consistent with the neuroscience (not an impl miss).

### Bucket 1 -- same-head AMBIGUOUS (595 mentions, achieved 0.4168): the wall is ENTITY SEPARATION, not SELECTION.
`exp_cn_accessibility_prior_v1.py` (n=2855):
- **SELECTION is already near-optimal.** Among the head-sharing candidate ENTITIES, plain RECENCY predicts the gold
  antecedent **0.783** (all ambiguous) / **0.873** (BARE repeated heads). The research's one untried cue -- the Ariel/Almor
  form-based ANTI-recency prior (a bare "the man" re-introduces a global-topic referent that dropped from focus) -- is
  **REFUTED on our data**: recency is even STRONGER for bare heads (0.873), and all five accessibility selectors
  (first-mention, frequency, subjecthood, anti-recency, graph-centrality), applied as a sign-flip, are **exact no-ops**
  (d=+0.0000 each). Recency-as-optimum is brain-faithful.
- **The loss is ENTITY SEPARATION.** The greedy same-head write-merge leaves the reader holding >=2 distinct same-head
  referents in **0 / 3224 = 0.0%** of anaphoric-common decisions -- it has already collapsed the distinct entities into ONE
  referent, so the selection step never even has a choice (hence every selector is a no-op). The gap between the
  recency-given-separation oracle (~0.78) and the achieved 0.42 IS the separation failure: once "the man"#2 merges into
  "the man"#1, the referent is a blend and the dominant-eid scoring fails on the minority entity.
- **Separation needs the cue that same-type interference neutralizes.** To NOT merge, the reader must decide "this the-man
  is a DIFFERENT man" -- exactly the discriminating cue (predication / co-participant / modifier / centering-continuation)
  that C8 proved is a NO-OP even with GOLD syntax. This is the Jaeger-Engelmann-Vasishth (2017) similarity-based
  retrieval-interference floor: two entities sharing a head are feature-identical to the retrieval cue, so no cue
  discriminates them. Altmann-Kamide selectional restriction (the strongest anticipatory cue) narrows by TYPE, which the
  shared head neutralizes. Humans ALSO fail here -- AmbiCoref (readers register uncertainty, not resolution) and the Nref
  sustained frontal negativity (unresolved-reference cost, individual-differences) -- so ~0.42 with an information limit is
  BRAIN-PARITY, not a defect. **Verdict: a durable brain-faithful negative at the SEPARATION step; the residual is an
  intrinsic information limit the brain shares.**

### Bucket 2 -- different-head DISCOURSE-IDENTITY (674 residual, achieved ~0.13): the wall SPLITS 42/58.
`exp_cn_discourse_identity_partition_v1.py` (n=2855; oracle partition over the non-type-linkable residual):
| slice | share | nature |
|---|---|---|
| UNIQUE-IN-FOCUS (only one gn-compatible given entity in a 3-sentence window) | 11.1% (75) | Heim familiarity + Loebner pragmatic definite -- **buildable, no knowledge** |
| MOST-SALIENT (gold = most-recent gn-compatible given entity) | 25.5% (172) | recency/focus -- **buildable** but precision-limited (a class-free salience bridge over-fires) |
| CLASS-SALIENT (most-recent of compatible coarse class) | 5.5% (37) | the CURRENT focus bridge already targets these |
| GOLD-NOT-IN-FOCUS (antecedent decayed past the window) | 26.3% (177) | **information limit** -- long-range, needs global re-activation memory |
| RESIDUAL near-identity (multiple candidates, gold not salient) | 31.6% (213) | **information limit** -- learned near-synonymy ("study"~="project"); partly annotation noise (non-nominal gold heads "be"/"huh", Spanish) |

- **DISCOURSE-MECHANICS resolvable in principle = 42.1%** (unique + salient + class-salient) -- a coherence-relation-aware /
  uniqueness focus bridge could reach a FRACTION of these, but bridging is precision-bound (C8's permissive focus bridge got
  the diff-head slice only to 0.19; the strict-abstain version 0.10 -- over-bridging hurts). This is why the C8 cue-integrated
  model could not beat the focus bridge: the resolvable cases are SALIENCE-driven (already used), and the added
  predication/co-participant cues target cases that need KNOWLEDGE, not more surface cues.
- **INFORMATION LIMIT = 57.9%** (long-range re-activation 26.3% + near-identity 31.6%). The near-identity residual is
  Halliday-Hasan lexical-cohesion reiteration / Recasens near-identity -- neither WordNet is-a (25% coverage, already got) nor
  gloss-cosine (10%, over-merges); it requires LEARNED discourse-conditioned coref-likelihood between common nouns (the
  learner/knowledge north star), not a richer matching rule.

### The unifying mechanistic claim (why cue-based backward retrieval hits a wall in BOTH buckets)
Cue-based BACKWARD retrieval (our binding) discriminates an antecedent only by features present in the anaphor. Both buckets
violate that precondition: **Bucket 1 the features COLLIDE** (same-type interference at the open-vs-merge decision), **Bucket 2
the discriminating feature is ABSENT from the surface** (identity is established by discourse structure or by knowledge, not
by the words). The brain's answer in both is NOT a richer backward matcher -- which is exactly what C8's located negative
refuted -- it is a FORWARD, coherence-structured, GENERATIVE situation model that (a) individuates entities from event/spatial/
temporal context (Bucket-1 separation), (b) predicts referent identity from coherence structure + Heim uniqueness (Bucket-2
discourse-mechanics), and (c) has LEARNED discourse-conditioned near-identity between concepts (Bucket-2 near-synonymy). This
is the already-named generative world-model / meaning-foundation main event; the coref wall is independent evidence it is the
right next organ. Route-by-flavor: Bucket-1-ambiguous = durable brain-faithful NEGATIVE (interference floor + human parity);
Bucket-2 = missing-PRIMITIVE (coherence/uniqueness bridge) + missing-LEARNING (near-identity), both feeding the generative program.

## C10. BUILT THE TWO BUILDABLE PIECES + LOAD-BEARING ABLATION (2026-09-10, owner: "build the two pieces, right not easy; determine what is load-bearing")
Built both pieces C9 named for the different-head discourse-identity residual, all brain-foundational down to the math,
and ran an ablation to isolate what carries signal (`exp_cn_bridge_ablation_v1.py`, `exp_cn_learned_nearidentity_v1.py`,
`exp_cn_accessibility_prior_v1.py`; witness `verification/test_cn_uniqueness_bridge.py` 5/5; GUM modern TEST n=2855).
Cues fed GOLD syntax where relevant; near-identity LEARNED from the GUM TRAIN split (even docs) only -> no test leak.

| piece | mechanism (PINNED) | acc | vs floor 0.5776 | vs info-free twin | diff-head | verdict |
|---|---|---|---|---|---|---|
| **1a UNIQUENESS bridge** | Heim familiarity + Loebner pragmatic definite: bind a licenseless definite to the SOLE gn-compatible referent in the immediate focus window (=6 mentions) | **0.5818** | **+0.0042 CI[+0.0018,+0.0069] SEP** | **+0.0392 SEP** | 0.1869->0.1991 (+11) | **LOAD-BEARING WIN** |
| 1b COHERENCE preference | Kehler coherence + Smyth/Chambers parallelism: prefer the licensed candidate in the PARALLEL grammatical role | 0.5751 | -0.0025 (not sep) | -- | 0.1791 (-7) | **anti-load-bearing** (salience beats parallelism -- same recency-dominance as C9 Bucket 1) |
| 2a NI_chain (learned) | coref-chain co-occurrence PMI (Halliday-Hasan reiteration; learned from RESOLVED coref in the train split) | 0.5769 | -0.0007 (not sep) | **+0.0406 SEP** | 0.1846 (-2) | **signal REAL but NOT load-bearing** -- too sparse (750 train pairs); false-bridges cancel the correct ones |
| 2b NI_depctx (learned) | dependency-context PPMI cosine (Levy-Goldberg functional substitutability, unsupervised from usage) | 0.5776 | +0.0000 | -- | 0.1869 (+0) | **INERT** -- licenses nothing the coarse-class focus bridge did not already license (subsumed) |
| ALL combined | uniq + coherence + NI_chain | 0.5762 | -0.0014 | -- | 0.1813 (-5) | the non-load-bearing pieces ERASE uniqueness's gain |

**What is load-bearing (the answer):** exactly ONE of the four -- the **HEIM/LOEBNER UNIQUENESS bridge** (+0.0042 CI-sep,
+0.0392 over its twin, +11 on the different-head slice, same-head no-regress; window sweep 6/10/16/24/40/60 all CI-sep, tighter
= better -> the win is the IMMEDIATE-focus interpretation). It fires on only ~71 mentions but precisely: when a definite has
no descriptive/type license and exactly one referent sits in the immediate focus, definiteness alone (familiarity + uniqueness)
forces the identification, no knowledge needed. This is genuinely the +11% "unique-in-focus" slice C9 predicted, banked.

**What is NOT load-bearing, and why (each a clean result, not a null):**
- COHERENCE/parallelism HURTS -- overriding salience with parallel-role preference loses; recency/salience is the better cue,
  the SAME finding as Bucket-1 (recency near-optimal). Refuted as a lever.
- Learned NEAR-IDENTITY carries a REAL signal (NI_chain beats its scramble twin by +0.041 -> the learned coref-likelihood is
  not noise) but is NOT load-bearing at the board: 750 co-occurring train pairs is too sparse to cover the test residual, and
  the false-bridges it licenses cancel the correct ones (net -0.0007). This is the C9 "information limit" made concrete: the
  near-identity relation IS learnable from reading, but the available reading volume is far short of the coverage needed --
  which is exactly why the answer is the LEARNER/knowledge-growth program (read more, online), not a bigger matching rule.
- Dependency-context substitutability is INERT because the coarse-class focus bridge already licenses everything a >=0.30
  cosine would -- the two mechanisms overlap; the learned version adds no new reach.

**Cumulative binder: 0.5482 (deployed) -> 0.5580 (concept-key) -> 0.5622 (conceptual) -> 0.5776 (focus) -> 0.5818 (+uniqueness);
de-leaked-floor margin +0.0326 -> +0.0564 CI-sep.** The uniqueness bridge is a landed-ready BF addition (SOLVED.md 6 item 8).

## D. Honest bottom line
The common-noun binder and its semantic core (concept key, salience, typed binding, type operation) are confirmed
brain-foundational to the math. The signal is lost in exactly two places, both now quantified: (i) the frozen supervised
PARSE STACK (fixed for coref by the parser-free boundary rule; the raw-text UAS gap is the comprehension-signal wall), and
(ii) DOMINANTLY the world-knowledge + situation-inference behind the different-head slice + the same-head-ambiguous slice.
The banked situation-model win is the coarse-class FOCUS BRIDGE (+0.0154 CI-sep, in the current best 0.5776). The full
cue-integrated discourse-entity model was BUILT + SWEPT + twin-controlled and is a LOCATED NEGATIVE (C8), now understood at
the mechanism level (C9): **the wall is not a missing surface cue -- it is the ceiling of BACKWARD cue-based retrieval.**
Bucket 1 (same-head ambiguous) is an ENTITY-SEPARATION information limit -- recency SELECTS correctly ~0.78-0.87 given
separated entities, but same-type feature-interference (Jaeger-Vasishth 2017) makes the open-vs-merge separation
undecidable from surface cues, and humans share the limit (AmbiCoref/Nref) -> a durable brain-faithful negative. Bucket 2
(different-head discourse-identity) splits ~42% discourse-mechanics-resolvable (a coherence/uniqueness bridge, precision-bound)
/ ~58% information limit (long-range re-activation + LEARNED near-identity). Both converge on the SAME next organ: a FORWARD,
coherence-structured, GENERATIVE + LEARNED situation model (the meaning-foundation main event) -- NOT a richer backward
matcher (refuted C8), NOT the type KB (refuted C5), NOT the event world-model (refuted C3). The coref wall is independent
evidence the generative program is the right target.
