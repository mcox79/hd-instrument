---
priority:
review: EXCELLENT
review_text: "Integrated SOLVED/EXCELLENT 2026-08-26 (owner-DONE). Re-verified scaffold-free first-hand (verify_predictive_reader.py, 8/8 PASS). BOTH bar routes met: a brain-faithful forward predictor -- the verb (+role) pre-activates the expected argument's GROUNDED semantic features (Altmann-Kamide/McRae thematic fit), read out as -log P surprisal under softmax competition -- beats an identical REACTIVE reader AND an info-free WRONG-VERB twin on held-out REAL QA-SRL anticipation (surprisal +0.199 vs reactive, +0.095 vs twin; pseudo-disambiguation 0.589 vs twin 0.514 AT CHANCE; only the verb-conditioned arm clears top-1 chance); and its surprisal is a valid graded difficulty signal (Spearman 0.239 vs distributional thematic-fit, twin ~0; reversibility AUC 0.619 -- UNIFIES with relcl: the margin flags the reversible cases syntax must carry). THE FREQUENCY CONFOUND (the central trap) is controlled three ways -- frequency-matched distractors, train-only base rates, and a twin with IDENTICAL frequency structure sitting at chance. Glass-box (grounded features + a verb key only; no word-form, no external model). DEEP: five literature drills PINNED the finer choices (predict MEANING features not word-FORM, Nieuwland; precision-weighting, Friston -- built, high-precision verbs +0.157 vs low +0.046 CI-sep; hierarchical top-down -- BUILT within-clause AND the full CROSS-SENTENCE discourse version composing the real n400_coherence_monitor across reconstructed documents, discourse beats local +0.088, twin HURTS). HONEST: effect is CI-separated but MODEST, ceiling'd by the 12-dim grounded space (the p1 representation-quality coupling) -- the machinery is correct now, the payoff scales with representation. NO hdlab landed: the forward-prediction organ (verb x role -> centroid table + -log P surprisal + a per-verb precision scalar, offline-built) is QUEUED as a proven-ready default-off landing; the live value is a difficulty/anticipation SIGNAL, measure on the live reader first. AUDIT UPDATEs folded (2b + tier-5 predictive/predictive_coding hierarchy + ATL/AG locus + relcl cross-link + precision-weighting PINNED-and-built)."
---

# PROBLEM: the reader only REACTS to each word; the brain PREDICTS the next one -- the verb pre-activates its expected argument before it arrives, and surprisal (prediction error) is the brain's core processing signal we do not compute

**slug:** `the_reader_is_feed_forward_where_the_brain_is_predictive` - **opened:** 2026-08-26 by the strategy session
(the #1 architecture-fidelity gap the `the_relcl_parser...` SOLVED surfaced in its whole-pipeline drill: "FEED-FORWARD
where the brain is PREDICTIVE -- the biggest gap, architecture-wide; arguably higher-value than anything left in that
problem").
**status:** OPEN - **BEHIND p1 retrieval-first (do NOT jump it): the programme is WIRE-AND-MEASURE, retrieval-first. This is the highest-BLAST-RADIUS remaining fidelity gap, packaged as a real, ready problem -- work it when a solver is free and the owner directs, not ahead of the retrieval wire-and-measure.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `2` -- BELOW p1 (retrieval-first wire-and-measure)
> but above the data-gated meaning lane (p8), because PREDICTION is architecture-WIDE (it touches every reading stage)
> and the relcl drill ranked it the highest-value remaining gap. It is NOT on the immediate retrieval critical path, so
> it must not pull effort off p1; re-rank UP only if the retrieval work stalls or the owner directs.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant,
> and do not silently proceed without the denied step.**

> ## ⚙️ SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **🧠 THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do. If you have
> not identified the brain's mechanism and attempted to build it, you have not started the real work,
> whatever else you have measured.
>
> **🚀 YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> You are NOT boxed in -- not by this brief, not by the existing organs, not by the integration points you
> would tie into: if a MORE brain-foundational method conflicts with any of them, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful). Exploring
> the brain's true method is the work we most want from you; a bold, well-argued brain-faithful direction --
> even unfinished -- beats a tidy engineering result that never asked the question.
>
> **🧱 A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several of your angles hit the
> SAME wall, that is strong evidence that NONE of them was the brain's mechanism -- the faithful method is
> probably DIFFERENT IN KIND, not another variation of what you already tried. A wall is a FIDELITY GAP TO
> BUILD ACROSS, never a ceiling. Hitting one is exactly the moment to LEAVE the family of methods you were
> sweeping and ask the biology again.
>
> **⛔ "CONVERGED" HAS A HIGH BAR, AND EXHAUSTING ENGINEERING VARIATIONS DOES NOT MEET IT.** Claim
> convergence ONLY when you have (a) identified how the brain actually performs this computation AND (b)
> replicated that operation as faithfully as you can and tested it, OR shown with a SPECIFIC reason why it
> cannot be replicated here. "I tried several combining / gating / scoring angles and they all plateaued at
> the same wall" is NOT converged -- it is tuning-limited, and it means the brain's mechanism is still
> UN-TRIED. That is a reason to explore harder, not to submit.
>
> **🔁 THE 30-MIN DEEPENING IS HOW YOU FORCE THIS -- IT IS NOT OPTIONAL BUSYWORK.** Run your own cron
> (`CronCreate "13,43 * * * *"`); each fire asks "how does the brain REALLY do this, one level deeper than
> my current mechanism?" -> implement -> test (can-fail, strongest real floor, info-free twin LOSING) ->
> iterate. Its whole purpose is to make you ask the brain question several more times than your own sense of
> "done" would. CANCEL it (`CronDelete`) and submit ONLY when the brain-mechanism bar above is met.
> Declining it because "my angles converged" is precisely the case it exists to catch.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully
> built.** A negative on a family of convenient engineering methods is not a negative on the capability; it
> is a report that you have not yet found how the brain does it.
>
> **📖 REFERENCE THE BRAIN-FOUNDATIONAL AUDIT, AND HELP KEEP IT TRUE.** Before you start, read the entry for the
> system you are touching in `notes/BRAIN_FOUNDATIONAL_AUDIT.md` -- it gives the brain structure, whether the
> brain's equation is PINNED or something we are INVENTING, our current fidelity, and the known deviation, so you
> inherit that instead of re-deriving it. If your work shows a verdict there is WRONG, STALE, or INCOMPLETE, or you
> find a NEW deviation, put a short **AUDIT UPDATE** note in your submission -- the strategy session folds it into
> the audit at integration. The audit is a living, shared map and you help maintain it.

## 1. THE PROBLEM IN PLAIN LANGUAGE

When you read "the waiter brought the...", your brain has ALREADY pre-activated "meal / plate / bill" before your eyes
reach the word -- reading is PREDICTION, not reaction. When the next word violates the prediction, that surprise (the
N400) is the brain's core signal: it flags difficulty, drives learning, and tells the reader where to slow down. Our
reader has none of this: it processes each word only AFTER it arrives, in a fixed feed-forward pass, and never forms an
expectation to be violated. So it cannot tell an easy, expected continuation from a hard, surprising one -- it has no
notion of processing difficulty at all.

This problem asks: **build the reader's forward-prediction loop** -- the current context (especially a verb) pre-activates
the expected next word / next argument-role BEFORE it arrives -- and use the resulting per-word SURPRISAL (prediction
error) as a graded difficulty signal. Then test whether that makes the reader better (or provides a usable difficulty
signal), against a reactive baseline.

## 2. WHY THIS ONE

- **It is the brain's single most central language principle, and we lack it end-to-end.** Prediction is architecture-wide
  (every stage): the relcl drill ranked it the biggest remaining fidelity gap and "likely also an accuracy/robustness win."
- **We have the PRIMITIVES but not the reading LOOP.** `hdlab/predictive_coding.py` exists and the N400 EVENT-SEGMENTATION
  organ is built (`n400_coherence_monitor`) -- but that is a running-GIST coherence monitor for event boundaries, NOT a
  top-down predictor that pre-activates the next word/role. The forward-prediction reading loop is the missing piece.
- **Surprisal is a free, gold-relevant signal.** Human reading time and the N400 are both predicted by surprisal
  (Hale 2001; Levy 2008; Michaelov 2024). A per-word surprisal signal feeds difficulty-gating, learning, and the
  route-conflict readout the relcl SOLVED surfaced -- it is infrastructure many downstream organs want.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED (do not invent around it):** language comprehension is PREDICTIVE. The context pre-activates upcoming input:
a verb pre-activates its expected arguments/fillers BEFORE they arrive (Altmann & Kamide 1999, anticipatory eye
movements; DeLong et al. 2005, pre-activation down to the article). The N400 is graded PREDICTION ERROR against that
expectation (Kutas & Federmeier 2011); SURPRISAL (−log P(word|context)) is the processing-cost currency (Hale 2001
surprisal theory; Levy 2008; and modern LM surprisal predicts the N400, Michaelov et al. 2024). Prediction is
hierarchical predictive coding: each level predicts the level below and passes the ERROR up (Rao & Ballard 1999; Friston).

**OUR-INVENTION-UNDER-TEST (mark each; sweep don't adopt):** (a) the PREDICTION TARGET in our substrate -- next content
word, next argument ROLE/filler, or the next situation-model update; a role/filler predictor is the most tractable and
the most brain-motivated (verb → expected filler). (b) HOW the predictor is built over our VSA/grounded reps (a learned
forward map? role-expectation vectors bound to the verb? a settling/attractor pre-activation?). (c) HOW surprisal is
computed from the prediction-vs-actual mismatch and normalised. COPY the OPERATION (pre-activate the expectation; the
error is the signal); SWEEP the parameters (target, window, representation, weight).

**Corpus-age note (MIND IT):** the reading corpus (McGuffey) is ~200 years old -- archaic continuations scored on modern
expectations mismatch. Prefer a modern-text or graded-reader harness, or hold corpus era fixed across the predictive and
reactive arms so the PREDICTION, not the corpus, is what varies.

## 4. MEASURED vs INFERRED

**MEASURED (`the_relcl_parser...` architecture-fidelity drill, integrated 2026-08-26; and on disk):** the reader is
FEED-FORWARD/reactive -- it only reacts to each word, forms no expectation, and computes no processing-difficulty signal;
this is architecture-wide, not specific to one stage. The predictive PRIMITIVES exist (`hdlab/predictive_coding.py`; the
N400 event-SEGMENTATION organ `n400_coherence_monitor`, integrated -- a running-gist coherence monitor, NOT a top-down
next-item predictor) and 58 experiment cells touch "predictive" (49 landed) -- so this is BUILD-ON, not virgin territory.

**INFERRED / OPEN (this problem, decisive either way):**
- Whether a forward-prediction loop (verb/context pre-activates the expected next word / next role / next filler) improves
  a downstream comprehension or role-assignment number over an identical REACTIVE reader on the same inputs.
- Whether the per-word SURPRISAL it produces is a valid graded difficulty signal (correlates with an INDEPENDENT
  difficulty measure -- e.g. the relcl route-CONFLICT signal, garden-path items, or a human reading-time proxy), with a
  shuffled-surprisal twin LOSING.

## 5. ALREADY TRIED / DO NOT RE-RUN (BUILD ON THESE, DO NOT RE-DERIVE)

- `hdlab/predictive_coding.py` (the predictive-coding primitive + `running_avg_update`) and `hdlab/n400_coherence_monitor.py`
  (the integrated N400 event-segmentation organ) EXIST -- REUSE them; do NOT rebuild the running-gist coherence monitor.
  This problem is the TOP-DOWN forward predictor + surprisal signal they do not provide.
- `the_substrate_does_not_learn_or_update_by_prediction_error` (SOLVED/integrated) established the UPDATE/segmentation
  half (graded content prediction error vs a running gist segments events) and rigorously found the LEARNING half (cloze
  vs forward-PC on paradigmatic meaning) did NOT beat cloze -- do NOT re-open that negative; this problem is FORWARD
  PRE-ACTIVATION during reading + surprisal-as-difficulty, a different claim.
- `experiment_index.py query "predictive"` (58 cells), `query "surprisal"`, and check
  `exp_agreement_word_predictive_hierarchy_fair_v1` and the DOP/construction-induction cells BEFORE building -- a forward
  predictor or a surprisal harness may partly exist to reuse.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Read `hdlab/predictive_coding.py`, `hdlab/n400_coherence_monitor.py`, and the `the_substrate_does_not_learn...` SOLVED,
  so you inherit the existing prediction machinery and its known negative rather than re-deriving them.
- Confirm on disk how the live reader currently processes a word (`hdlab/reading_grounding_loop.py` / `situation_reader.py`):
  where a top-down expectation could be injected before the next token, and what representation the prediction would live in.
- Pick a downstream task where prediction SHOULD help and recompute every floor on its population; if you use the route-
  conflict / difficulty validation, reuse the relcl harness rather than rebuilding it.

## 7. THE BAR

Build the reader's forward-prediction loop (context/verb pre-activates the expected next word / role / filler before it
arrives) and compute per-word surprisal. On a held-out population, floors recomputed on it:

- **The PREDICTIVE reader must beat an identical REACTIVE reader CI-separated over its UPPER bound on a downstream
  comprehension / role-assignment / next-item task, with an info-free twin (shuffled predictions / scrambled context)
  LOSING** -- OR, if the accuracy is a wash, **the per-word SURPRISAL must be a valid graded difficulty signal:
  CI-separated correlation with an INDEPENDENT difficulty measure (the relcl route-conflict, garden-path vs control
  items, or a human reading-time proxy), with a shuffled-surprisal twin at zero.** Report CI half-width + null p95 beside
  every margin.
- **DECISIVE EITHER WAY:**
  - Prediction improves a downstream number and/or surprisal is a valid difficulty signal -> the forward-prediction loop
    is a real organ; propose the hdlab wiring (strategy lands it; it composes into the live reader and feeds difficulty-
    gating / the route-conflict readout).
  - A faithfully-built forward predictor moves NO downstream number AND its surprisal carries no usable difficulty signal
    -> a rigorous negative (prediction, as buildable over our reps, does not earn its machinery in this reader) -- as
    valuable as the win. State the predictor you built and why it is the brain's, so the negative is on the mechanism.

## 8. FILES AND ENTRY POINTS

- `hdlab/predictive_coding.py`, `hdlab/n400_coherence_monitor.py` (the existing prediction machinery -- build on them),
  `hdlab/reading_grounding_loop.py` / `hdlab/situation_reader.py` (the live reader -- where the forward expectation is
  injected), `hdlab/binding.py` / `hdlab/atoms.py` (to bind role-expectation vectors to the verb, if that is the target).
- `verification/verify_relcl_incremental_fillergap_parser.py` / the relcl cells (the route-CONFLICT difficulty signal to
  validate surprisal against).
- Prove in `experiments/` + `verification/`; propose the hdlab WIRING diff in `SOLVED.md` (strategy lands it, Q111).
  **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT rebuild the N400 event-segmentation / running-gist monitor -- it is integrated (`n400_coherence_monitor`); this
  problem is the TOP-DOWN forward predictor it does not provide.
- Do NOT re-open the `the_substrate_does_not_learn...` forward-PC-vs-cloze LEARNING negative; this is forward
  PRE-ACTIVATION + surprisal-as-difficulty, a different claim.
- Do NOT score on the ~200-year-old McGuffey continuations without holding corpus era fixed across the predictive and
  reactive arms (the age confound); prefer modern text.
- No number crosses populations/scorers -- recompute every floor on the scored population.

---

## SOLVER REVIEW (strategy session, 2026-08-26 — INTEGRATED, owner-DONE)

**Grade EXCELLENT. Verdict SOLVED** (both bar routes met; the live-reading capability is a separate gate, shared with
every organ). Re-verified scaffold-free first-hand — `verify_predictive_reader.py` 8/8 PASS, every direction + CI-separation
reproduced (anticipation surprisal +0.138 vs twin; pseudo-disambiguation 0.575 vs 0.512 at-chance twin; Spearman 0.231
vs 0 twin; reversibility AUC 0.585; Bicknell agent+verb sharpens; precision high vs low +0.106; hierarchical L0→L3
monotone; the cross-sentence discourse build beats local + twin loses; the honest reset<no-reset dissociation).

**Why EXCELLENT.** (1) The literature drills changed a build choice *before* a wrong version was written — Nieuwland's
failed FORM-prediction replication said predict MEANING FEATURES, not the word, so our coarse 12-dim grounded space is
aligned with the *robust* level (its coarseness a virtue). (2) The primary control is the right one: a WRONG-VERB twin
(identical machinery, only the verb→expectation binding scrambled, IDENTICAL frequency structure) sitting AT CHANCE —
which airtightly excludes the field's central confound (that anticipation is a frequency effect) and "any centroid wins."
(3) It didn't stop at the win — it BUILT the brain-foundational architecture: precision-weighting (Friston constraint
strength — the predictive benefit scales with the verb's selectional-preference sharpness, CI-separated), hierarchical
top-down prediction, and the full CROSS-SENTENCE discourse hierarchy composing the *actual* `n400_coherence_monitor`
across reconstructed real documents (finding 9, "the real build"). (4) It is honest to a fault about size (modest,
representation-ceiling'd — the p1 coupling) and about every residual (the reversibility twin isn't fully at chance; the
precision per-verb Spearman is weak; validated against proxies not human RT/ERP).

**The unification (why this matters for the programme).** One forward predictor produces BOTH an anticipation win on
IRREVERSIBLE role assignment AND a "hand-to-syntax" difficulty flag on REVERSIBLE cases — exactly the regime the relcl
filler-gap parser exists for. Semantics predicts what it can; its surprisal margin flags what only syntax can resolve;
and the same surprisal feeds write-gating and the N400 confidence. It is the missing WORD/FEATURE level of the
predictive hierarchy, complementary to (not competing with) the backward-looking event coherence monitor.

**No hdlab landed this integration** (Q111). The forward-prediction organ is a genuinely NEW, design-settled,
self-contained organ (a verb×role→grounded-centroid table + −log P softmax surprisal + a per-verb precision scalar,
offline-built from a predicate-argument corpus — a static asset, admissible per the pivot). It EARNS a default-off
landing, but building the offline table + module + witness properly is a focused build, not a heartbeat-cram — so it is
**QUEUED as a proven-ready deliberate landing** (scoped in STATUS/audit), to compose into the p1 wire-and-measure and
feed the relcl route-conflict. Its value is a difficulty/anticipation SIGNAL — measure on the live reader before any
capability claim. AUDIT UPDATEs folded into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b + the Tier-5 entries. The solver's
named next foundational build — ENTITY-LEVEL discourse tracking (wire coref into the situation model) — is packaged as a
new problem.
