---
slug: replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals
status: INTEGRATED
review:
review_text:
---

# PROBLEM: the reader's dependency parser -- the deepest shared upstream of every extraction / role / relation read -- is a GREEDY, hard-1-best, LOCALLY-normalized arc-eager transition parser that commits one analysis before the situation model exists and exposes no recoverable 2nd-best (so half its errors are unrecoverable SEARCH failures and the who-did-what PATIENT is capped ~0.08 below its gold-parse ceiling); build a glass-box GLOBALLY-NORMALIZED / graded parser that emits a real distribution over parses (edge marginals + a genuine 2nd-best) and prove those marginals beat the greedy 1-best on MODERN gold AND lift a live downstream consumer, with a shuffled-marginals info-free twin LOSING.

**slug:** `replace_the_greedy_arc_eager_with_a_globally_normalized_graded_parser_with_marginals` -- **opened:** 2026-09-06
by the strategy session. This is the wall-map's dominant NON-brain-foundational decision at the SYNTAX level: we built a
FEED-FORWARD PIPELINE OF HARD-COMMITTING SILOS (tag -> parse -> assign-role) where the brain runs a GRADED, ranked-parallel
competition with revision. The parser is the deepest shared upstream -- roles, relations, extraction, attachment, temporal
and spatial reads all sit on its heads -- and it throws the graded parse away before any of them run. The precision-defer
SOLVED measured the cost directly (half the parser's errors are unrecoverable SEARCH failures; a wider beam does NOT fix a
LOCALLY-normalized model) and named the fix verbatim: "a globally-normalized parser with exact Matrix-Tree marginals".
**status:** CANDIDATE -- a BUILD + VALIDATION problem. You build + validate in `experiments/`; strategy lands any hdlab
change (Q111). Glass-box, a static offline-built parser asset is admissible, NO external LLM at inference (the invariant).

> **PRIORITY NOTE (the call is the strategy session's; provisional -- RE-RANK per the owner):** filed at `3` because it is
> the wall-map's load-bearing syntax-level wall and the single highest-leverage parser build named by two independent
> drills, BUT it is a real MODEL build (not a wiring job), it sits behind the recurrent-loop closure that is the higher
> north-star (that loop wants THIS graded parse to feed it), and its downstream payoff is bounded by how much of the
> residual is parse-recoverable vs the char-vs-char two-valid-agents slice that routes elsewhere. It stays CANDIDATE until
> its own premise -- that a globally-normalized distribution recovers the search-failure errors the greedy parser forfeits
> AND lifts a live read -- is measured. Set the real priority when promoted from CANDIDATE to OPEN.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

> ## SOLVER OPERATING PROTOCOL (standing -- owner 2026-08-25, strengthened 2026-08-26; in EVERY problem)
> **DO THE RIGHT THING, NOT THE CHEAP OR EASY THING** -- the mission is the most brain-faithful substrate,
> not the fastest green check.
>
> **THE OPENING MOVE, BEFORE ANY METHOD: how does the BRAIN actually do THIS?** Name the structure /
> circuit and the computation it performs, and try to replicate that OPERATION as exactly as you can. This
> is NOT a tiebreaker you reach for after your tools plateau -- it is the FIRST thing you do.
>
> **YOU ARE ENABLED -- AND EXPECTED -- TO EXPLORE FAR AND WIDE FOR THAT MECHANISM.** Go read the
> neuroscience. Cross domains. Propose something that looks NOTHING like this brief or the current substrate.
> If a MORE brain-foundational method conflicts with this brief or the existing organs, SUBMIT that alternative
> solution or DIRECTION instead (say what is incompatible and why yours is more brain-faithful).
>
> **A SHARED WALL IS A SIGNAL TO GO DEEPER, NOT A REASON TO STOP.** If several angles hit the SAME wall,
> the faithful method is probably DIFFERENT IN KIND. A wall is a FIDELITY GAP TO BUILD ACROSS, never a ceiling.
>
> **"CONVERGED" HAS A HIGH BAR.** Claim it ONLY when you have (a) identified how the brain performs this
> computation AND (b) replicated that operation as faithfully as you can and tested it, OR shown a SPECIFIC
> reason it cannot be replicated here. Exhausting engineering variations is NOT convergence.
>
> **THE 30-MIN DEEPENING CRON (`CronCreate "13,43 * * * *"`) -- RUN THIS CHECKLIST EACH FIRE AND ACT ON IT
> (owner 2026-08-28; this is how you keep pushing without being told):**
> (1) DO THE RIGHT THING, not the cheap one -- and if there is high-value ADJACENT info we can gather that raises
> fidelity OR PROVES THE POINT (a control, a distance/robustness curve, an ablation, a second gold), GO GET IT.
> (2) What is LEFT that rationally fits THIS problem? Enumerate + do it. If ADJACENT components bottleneck it, MAP
> THEM OUT (name the component, the on-disk evidence, the leverage) as candidate follow-ons, never silent gaps -- AND
> EVALUATE each for BRAIN-FOUNDATIONAL FIDELITY + OPTIMIZATION POTENTIAL (is it the brain's actual mechanism or an
> OUR-INVENTION placeholder? a higher-fidelity / higher-yield version worth building?) -- that evaluation seeds the next problem.
> (3) Any OPTIMIZATIONS left for this module, or brain-foundational FIDELITY to look at more closely with another
> research drill? If yes, RUN it.
> (4) Hit an UNEXPECTED WALL? Run a FINER brain-foundational research drill -- do NOT stop. If the BRAIN can do this
> and WE can't, UNDERSTAND why (the brain succeeds where our mechanism fails) then BUILD across -- never a ceiling.
> Each fire: implement -> test (can-fail, strongest real floor, info-free twin LOSING) -> iterate. CANCEL
> (`CronDelete`) + submit ONLY when the brain-mechanism bar is met AND this checklist yields nothing more of value.
>
> **A rigorous negative is a PASS -- but only if what failed was the brain's actual mechanism, faithfully built.**
>
> **REFERENCE `notes/BRAIN_FOUNDATIONAL_AUDIT.md`** for the systems you touch; inherit its PINNED/INVENTED verdicts;
> put a short **AUDIT UPDATE** in your submission for any verdict you find wrong/stale or any new deviation.

> ## BRAIN-FOUNDATIONAL CHECKLIST (the owner's standing bar -- work through IN ORDER; the solution is not done until every box holds)
> 1. **OPEN -- how does the BRAIN do THIS?** Name the specific structure + computation and replicate that OPERATION as the FIRST move; mark each choice PINNED vs OUR-INVENTION. RESEARCH AGGRESSIVELY wherever you are unsure -- do not build the tractable thing and cite neuroscience after.
> 2. **REUSE -- does an existing organ already do what you need?** Check `tools/substrate_map.py` / `tools/reader_capabilities.py` / `hdlab/` FIRST; extend a matching organ rather than re-deriving it.
> 3. **GENERALIZE -- does this need to generalize, and HOW does the brain generalize it?** Build for that (register / novelty / transfer), not for the single test.
> 4. **HIT A WALL? GO DEEPER, DON'T STOP.** Research-drill WHY. If the brain can do it, it IS possible and we can too, once we understand it. A located NEGATIVE counts only if the brain's ACTUAL mechanism, faithfully built, is what failed (fair test: can-fail, one-variable, real baseline).
> 5. **OPTIMIZE BY EXACT REPLICATION.** Evaluate aggressively, with great precision, EXACTLY how the brain does it, and replicate it exactly -- copy the computation, SWEEP (never adopt) the parameters. No half-effort: the closer we are, the better we do.
> 6. **PERFORMANCE vs THE BRAIN.** How does our performance compare to a competent brain/reader on this task? WHERE ALONG THE CHAIN do we lose signal? What EXACTLY differs between our implementation and the brain's mechanism (an itemized mechanism-diff)?
> 7. **ADJACENT COMPONENTS.** Map the capabilities, limitations, opportunities, and brain-foundational status of the adjacent components -- that seeds the next problems to address.
> 8. **COMPLETION BAR.** Is this a COMPLETE, EXCELLENT solved problem? Is it FULLY brain-foundational, conveying ALL the benefits of the brain function we replicate? If not, keep pushing toward a fully complete, exceptional solution.
>
> **(PHASE DIAGRAM -- the substrate is not locked to one regime.)** The substrate's operating point -- store DENSITY vs SPARSITY, dimensionality, binding regime, capacity, decay/gain, indexed-vs-superposed organization -- is FREE to change at ANY time, PER ORGAN. These are parameters to SWEEP, never fixed constraints. A wall "at this configuration" is a cue to MOVE the operating point on the phase diagram BEFORE ever calling it a ceiling.
>
> **(FULL-STACK UPSTREAM -- prototype THIS component AND its upstream, to EXCEL and EXCEED.)** Fully prototype THIS component AND the upstream brain-foundational component it depends on (and ALL the way upstream if the chain is deeper), and SHOW the capability can EXCEL and EXCEED -- make it happen. Then: (a) CONFIRM no other downstream consumer of the upstream optimization REGRESSES; (b) CONFIRM whether those other consumers should be REVISITED to be more brain-foundational, now making use of the newly-optimized upstream capabilities; (c) make SURE, VIA RESEARCH, that what you implement upstream is genuinely brain-foundational. **THE ONLY WAY YOU OVERCOME THIS WALL IS FOR EVERY COMPONENT -- YOU AND UPSTREAM -- TO BE BRAIN-FOUNDATIONAL.** Any wall you encounter must be FULLY RESEARCHED: the brain does it, so we can too -- and to do so we must UNDERSTAND it fully.

## 1. THE PROBLEM IN PLAIN LANGUAGE
When a sentence is grammatically ambiguous, a good reader keeps several possible readings alive at once and lets later
words -- and the sense of the story so far -- decide between them; and if the first reading turns out wrong, they still have
the next-best one to fall back on. Our reader's grammar engine does the opposite. It marches left to right making one snap
decision at each word and never looks back, so it ends up committed to a single skeleton of the sentence with no runner-up
recorded. When that snap decision is wrong -- and about half the time it is wrong because the right reading was thrown away
early, not merely mis-scored -- nothing downstream can recover it: the part that works out who did what to whom is reading
off a skeleton that is silently broken, and there is no second-best skeleton to try. Worse, the engine fixes the grammar of
a sentence before it has any sense of the story, so it cannot use "which reading actually makes sense here" to break a tie.
Build a grammar engine that instead keeps a genuine spread of possible analyses -- a real "how likely is each attachment"
number for every word -- so the reader gets both a runner-up to fall back on and a graded confidence the rest of the reader
can lean on. Prove the spread-of-analyses engine is more accurate than the one-snap-decision engine on modern writing and
that it makes the who-did-what step measurably better, with a scrambled-confidence version failing so we know the real
spread is carrying the load.

## 2. WHY THIS ONE
This is the wall-map's load-bearing NON-brain-foundational decision at the syntax level. `notes/WALL_MAP_non_brain_
foundational_decisions_2026-09-06.md` (DOMINANT FINDING + Wall 2) drills the who-did-what wall to exactly this: "the greedy,
bottom-up, hard-1-best arc-eager parser with a distribution-free score, computed BEFORE and INDEPENDENT of the situation
model." It is the DEEPEST shared upstream -- the same heads feed roles, relations, extraction, attachment, and the temporal
/ spatial reads (the ledger lists the parser as `upstream_needed` for several capped consumers, e.g. bare-purpose
attachment parse-gated 0.33 vs oracle). Two independent measurements say the hard-commit itself is the loss: the AGENT
(read by `graded_competition`, which KEEPS alternatives) has reliability margin AUC 0.76, while the PATIENT (read off the
greedy arc) has AUC 0.50 -- SAME precision-weight move, the only difference is the hard commit; and half the parser's
errors are unrecoverable SEARCH failures (the correct analysis fell off before any reweighting could reach it). The
who-did-what PATIENT is stranded at 0.831 live against a 0.913 gold-parse CEILING (~0.08 the 1-best forfeits). Test 4 (does
a NUMBER show the DEFECT costs us, not merely that an alternative exists?): YES -- the +0.08 patient cap, the AUC 0.76 vs
0.50 gap, and the ~half-of-errors-unrecoverable figure are costs of the current parser, measured. This is not a hypothesis
in a problem's clothes.

## 3. HOW THE BRAIN DOES THIS (frame -- PINNED vs OUR-INVENTION)
- **PINNED (the computation).** The brain parses with GRADED, ranked-parallel COMPETITION plus revision, not hard serial
  commitment. Multiple syntactic analyses are co-active and compete continuously as evidence arrives (MacDonald,
  Pearlmutter & Seidenberg 1994 constraint-satisfaction; Spivey-Knowlton & Sedivy / McRae 1998); recovery from a wrong
  commitment is the P600 reanalysis signal (Osterhout & Holcomb 1992); the process is ranked-parallel within a BOUNDED
  beam and a garden path is precisely the correct analysis pruned from that beam (Gibson dependency locality; Lewis &
  Vasishth 2005 activation-based retrieval; Jurafsky 1996 probabilistic parsing = the beam-pruning account). The
  computational-level object is a GLOBALLY-NORMALIZED distribution over parses -- an exact posterior over trees whose
  per-EDGE MARGINALS are computable in closed form for the arc-factored (spanning-tree) case via the Matrix-Tree Theorem
  (McDonald & Satta 2007; Koo et al. 2007 / Smith & Smith 2007). Precision-weighting a downstream commitment by that
  posterior's concentration is Friston 2010 / Ernst & Banks 2002 (already PINNED and landed as `parse_confidence`).
- **OUR-INVENTION-UNDER-TEST (sweep, don't adopt).** The BEAM WIDTH (top-2/3, P600-bounded -- SWEEP); the softmax
  TEMPERATURE that turns edge scores into marginals (SWEEP); the NORMALIZATION regime (exact Matrix-Tree partition
  function for an arc-factored scorer vs Andor et al. 2016 beam-in-the-loop GLOBAL training for the transition parser);
  the 2nd-best fallback policy; and the mapping from marginal concentration onto the `graded_competition` cue. These are
  the free phase-diagram knobs -- sweep them, never adopt a number.
- **NOT brain-faithful (do NOT do).** The greedy hard-1-best local-argmax decode (the incumbent this must beat); a LOCALLY-
  normalized action scorer (label bias -- Andor 2016 proves globally-normalized > locally-normalized AND that beam width
  does not fix it -- the settled cause of the small-beam negative); an external LLM at inference; a trained DEEP parser
  that loses OOD (the wall-map explicitly rejects "train a better parser"); and optimizing UAS as the objective (a
  better-UAS parser moves who-did-what ~+0.00 -- the target is the graded distribution + the downstream role read, not UAS).

## 4. MEASURED vs INFERRED
- **MEASURED (on disk, REUSE -- do not re-derive):**
  - The LIVE parser is a GREEDY arc-eager transition parser, UAS 0.842, LOCALLY normalized: `hdlab/arceager_parser.py`
    (`parse_with_conf -> (heads, conf, marg)`; softmax over legal actions at each step, then argmax-commit). The reader
    reads ROLE heads off it via `situation_reader._cached_parse_conf` / `_cached_parse_heads` -> `structural_patient_pick`
    + obl/nmod attachment (a SINGLE shared per-read parse after the 2026-09-06 fold). Hard-1-best; no 2nd-best over PARSES.
  - The hard-commit is the loss (wall-map Wall 2 / modern-board 6c): the role assigner picks the same as raw position 84%
    of the time; on position's FAILURES it recovers gold only 0.137, BELOW random 0.155; AGENT (via `graded_competition`,
    keeps alternatives) reliability AUC 0.76 vs PATIENT (greedy arc) AUC 0.50.
  - HALF the parser's errors are unrecoverable SEARCH failures + a wider beam does NOT fix a locally-normalized model
    (precision-defer SOLVED sec 3b): gold-in-beam-when-wrong 0.492 on wrong obl arcs; a faithful small-beam decode's
    readouts (agreement / margin / Hale-entropy) are all <= the greedy raw conf across k=6/8/16; root cause = LOCAL
    normalization / label bias (Andor 2016). North-star, verbatim: "a globally-normalized parse scorer with an EXACT
    posterior (edge-factored Matrix-Tree marginals -- McDonald-Satta 2007 / Koo et al. 2007; or Andor-style
    beam-in-the-loop global training)."
  - The MISSING lever is the parse's OWN 2nd-best (precision-defer SOLVED sec 3a): no head-independent prior beats the
    parse even on its shakiest confidence-quartile, so FALL-BACK adds nothing; the fall-back that WOULD beat the parse on
    its shaky arcs is the parse's 2nd alternative -- which the greedy parser cannot expose.
  - The PATIENT headroom (`notes/INTEGRATION_LEDGER.md`): live 0.831 (clean UD-EWT n=1255) vs gold-parse ceiling 0.913
    (residual +0.15 to ceiling = the parser verb->argument attachment); a register-native parse is `upstream_needed` for
    other consumers.
  - An ARC-FACTORED scorer already exists (the natural Matrix-Tree substrate): `hdlab/arc_parser.py` (hashed arc-factored
    averaged perceptron) -- BUT it also decodes GREEDILY (per-token argmax head + cycle-break, `decode_from_scores`), with
    NO tree constraint and NO marginals today. Its per-arc score margins are exactly the edge potentials a Matrix-Tree
    marginal / partition-function computation consumes.
- **INFERRED (you must prove):** that a glass-box GLOBALLY-NORMALIZED / graded parser emitting a real distribution over
  parses (edge marginals + a genuine 2nd-best) EITHER (a) beats the greedy 1-best on attachment CI-separated on modern
  UD-EWT, OR (b) yields a CALIBRATED 2nd-best / marginal that recovers the SEARCH-failure errors the greedy parser
  forfeits; AND that it lifts a LIVE downstream consumer (patient selective-accuracy toward the 0.913 ceiling, and/or the
  obl attachment defer path), with a SHUFFLED-marginals info-free twin LOSING and NO live-consumer regress; OR a rigorous
  LOCATED NEGATIVE with the cause named + counted (e.g. exact Matrix-Tree marginals over our arc-factored scores calibrate
  no better than the landed confidence and recover only N of M search-failure arcs, because the arc-factored FEATURES
  under-separate right-from-wrong -- the wall is the SCORER, not the normalization; or the residual is the two-valid-agents
  char-vs-char slice that routes to grounded event-knowledge, not the parse).

## 5. ALREADY TRIED / DO NOT RE-RUN
- Do NOT re-run the small-beam decode of the greedy arc-eager parser -- it is the precision-defer SOLVED's LOCATED NEGATIVE
  (beam readouts <= raw greedy conf across k=6/8/16; gold-in-beam-when-wrong 0.492). A WIDER BEAM is not the fix; the
  parser's LOCAL NORMALIZATION is (Andor 2016). The lever is a globally-normalized MODEL, not a bigger decoder.
- Do NOT re-derive the calibrated per-arc confidence -- `hdlab/parse_confidence.py` is landed (AUC 0.858 UD patient) and the
  defer-consumer is LIVE default-ON at ZERO extra parse cost. This problem gives that consumer a real distribution + a
  2nd-best to consume; it does not rebuild the calibrator.
- Do NOT wire a post-hoc RE-ATTACHMENT of the parse (it hurts UAS -- settled). Precision-WEIGHT / keep-alternatives only.
- Do NOT chase UAS -- a better-UAS parser moves who-did-what ~+0.00 (wall-map Wall 2). The target is the graded distribution
  + the downstream role read.
- Do NOT "train a better parser" as a deep model -- trained loses OOD (wall-map Wall 2 fix line). Glass-box, offline-fit
  static asset only.
- **Do NOT repair attachment with a permissive lexical heuristic -- this is the p9 negation/quantifier SOLVED's fully-drilled
  LOCATED NEGATIVE (integrated 2026-09-07, `hdlab/polarity_operator.py`).** That solver built a glass-box parse-repair
  (WordNet lexical-category + Frazier coordination-parallelism + verb subcategorization + shared-subject constraints, NO
  training) that matched the surface operator on its negation gold (structural resolver 0.8864 -> 0.9318) -- but the HONEST
  GENERALITY CHECK on GOLD UPOS (UD-EWT test, n=2000 sents / 24,185 tokens) proved it **NET-NEGATIVE on general text**: POS
  0.9443 -> 0.9375, of 188 retags only 7 FIXED vs 172 BROKE (precision 0.04). The culprit is the "any-WordNet-verb-sense"
  signal (most nouns/adjectives have a verb sense). A precise PREDOMINANT-verb signal (upgrade D) cut the damage 12x
  (precision 0.037 -> 0.208, POS damage -165 -> -14 tokens) but was STILL marginally net-negative. **DIRECT EVIDENCE FOR
  THIS PROBLEM: the genuinely-general fix needs (a) a PRECISE lexical resource -- VerbNet subcategorization frames + frequency
  priors -- and (b) TAGGER-CONFIDENCE GATING (override a tag ONLY when the tagger is unconfident), NOT a permissive
  heuristic and NOT training. An isolation win on a construction-enriched gold is not a general capability -- measure the
  fix for GENERALITY on gold UPOS before deploying it (that measurement is what PREVENTED landing an overfit repair).**
- Run `python tools/before_you_start.py "<what you are about to do>"` and `tools/experiment_index.py query "parser"` /
  `"marginal"` / `"beam"` / `"attachment"` / `"global"` (SINGLE keywords) before building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)
- FIRST STEPS: run `python tools/substrate_map.py` and `python tools/reader_capabilities.py`; skim `hdlab/` so you build ON
  the two existing parsers + the landed calibrator, not beside them.
- READ IN FULL (build ON it, credit it): `notes/problems/wire_a_defer_consumer_for_calibrated_confidence_and_realize_
  precision_weighting/SOLVED.md` (the north-star statement + the two located negatives: fall-back has no prior, small-beam
  is label-bias-bound) and `notes/problems/precision_weight_the_head_driven_readers_on_calibrated_parse_confidence/
  SOLVED.md` (the landed calibrator). Read `notes/WALL_MAP_non_brain_foundational_decisions_2026-09-06.md` Wall 2 + THE
  DOMINANT FINDING.
- INSPECT what you REUSE: `hdlab/arceager_parser.py` (the greedy transition parser + `parse_with_conf`); `hdlab/arc_parser.py`
  (the ARC-FACTORED scorer -- the natural Matrix-Tree substrate; note it decodes greedily via `decode_from_scores`, no
  tree / marginal today); `hdlab/graded_competition.py` (the additive-cue -> softmax competition the AGENT already uses --
  feed the parse distribution INTO it); `hdlab/parse_confidence.py` + the live defer-consumer in `hdlab/situation_reader.py`
  (`_cached_parse_conf`, `_patient_arc_confidence`, `structural_patient_pick`).
- READ the audit: `notes/BRAIN_FOUNDATIONAL_AUDIT.md` parser entries (the greedy arc-eager / label-bias / Matrix-Tree
  north-star entry -- search "Matrix-Tree" / "label bias" / "1-best").
- ENUMERATE the consumers (an absence claim requires an enumeration, not a search): grep every live read of the parse heads
  (`grep -rin "structural_patient_pick\|_cached_parse_heads\|_cached_parse_conf\|arceager_parser\|arc_parser" hdlab/
  experiments/ verification/`) so you know exactly which downstream reads a swap / precision-weight touches, and can prove
  no-regress. State how you enumerated in your submission.
- GOLD: MODERN UD-EWT is the load-bearing gold (attachment / UAS-LAS + the who-did-what patient read); QA-SRL patient is
  the OOD companion. You are PRE-AUTHORIZED to acquire an open modern treebank under `data/corpora/<name>/` with a
  REPRODUCIBLE pinned fetch script in `experiments/` + a provenance note (source, version, license, n). Do NOT lean on 19c
  (banned as load-bearing gold); a 19c number is informational only.

## 7. THE BAR
PASSES only with ALL of:
1. **A glass-box GLOBALLY-NORMALIZED / graded parser emitting a real distribution over parses (edge marginals + a genuine
   2nd-best), built + validated in `experiments/` (strategy lands the hdlab change, Q111).** COPY the computation
   (globally-normalized posterior / Matrix-Tree edge marginals for the arc-factored case -- McDonald-Satta 2007 / Koo 2007;
   OR Andor-2016 beam-in-the-loop global training for the transition parser). SWEEP the beam width, the softmax
   temperature, the normalization regime (the free phase-diagram knobs). Offline-fit STATIC asset; NO external LLM.
2. **The marginals BEAT the greedy 1-best on MODERN UD-EWT, CI-separated over the floor recomputed on the SAME population,
   in ONE of two forms:** EITHER (a) the marginal / global decode's ATTACHMENT accuracy beats the greedy 1-best argmax head
   CI-separated; OR (b) a CALIBRATED 2nd-best / marginal RECOVERS the SEARCH-failure errors the greedy parser forfeits --
   on the wrong-arc population the correct head is exposed AND rankable-above-the-1-best by the marginal on a CI-separated
   fraction above the greedy parser (which exposes gold ~0.49 of the time and cannot rank it). Report CI half-width + null
   p95; the floor is the LIVE greedy parser recomputed per population; NO number crosses populations.
3. **A LIVE DOWNSTREAM LIFT.** The distribution / 2nd-best lifts a live consumer: who-did-what PATIENT selective-accuracy
   toward the 0.913 gold-parse ceiling (floor = the live greedy-arc reader 0.831 on clean UD-EWT n=1255), and/or the
   obl/spatial attachment defer path -- CI-separated over the live incumbent recomputed on that population.
4. **The info-free twin LOSES CI-separated.** SHUFFLE the marginals (give each arc a random other arc's marginal / a random
   2nd-best of matched shape), keeping shapes / balance -- the gain must come from THIS parse's distribution, not from
   "keeping any alternative helps." (This is the exact control the precision-defer SOLVED used to prove the calibration was
   load-bearing.)
5. **NO-regress.** The reader stays byte-identical where the graded parse is off; enumerate every live consumer of the parse
   heads and confirm none regress (UAS/LAS not down, existing scored dims unchanged). A can-fail POSITIVE control the greedy
   1-best CANNOT pass: a garden-path / non-projective attachment where the greedy decode prunes the gold head early but the
   global marginal keeps it exposed and rankable.
6. **One-screen summary:** parser type + normalization -> modern gold + provenance -> greedy-1-best floor -> attachment /
   2nd-best-recovery margin (CI half-width + null p95) -> live-consumer lift -> twin -> what breaks -> verdict. Heavy -> REMOTE.
A rigorous NEGATIVE is a FULL PASS (e.g. "exact Matrix-Tree marginals over our arc-factored scores calibrate no better than
the landed confidence and recover only N of M search-failure arcs, because the arc-factored FEATURES under-separate
right-from-wrong -- the wall is the SCORER's features, not the normalization, a distinct upstream organ"; OR "the global
decode beats greedy on attachment CI-sep but the PATIENT read does NOT move because the residual is the two-valid-agents
char-vs-char slice that routes to grounded event-knowledge, not the parse -- located and counted, per wall-map Wall 2").

## 8. FILES AND ENTRY POINTS
- **REUSE (do NOT rebuild):** `hdlab/arceager_parser.py` (the greedy transition parser + `parse_with_conf` -- the incumbent
  to beat); `hdlab/arc_parser.py` (the arc-FACTORED scorer -- the natural Matrix-Tree substrate; today decodes greedily,
  no marginals); `hdlab/graded_competition.py` (feed the parse distribution in); `hdlab/parse_confidence.py` + the live
  defer-consumer in `hdlab/situation_reader.py` (`_cached_parse_conf`, `_patient_arc_confidence`, `structural_patient_pick`).
- **CONSUME (the measured cap -- do NOT re-derive):** `notes/INTEGRATION_LEDGER.md` (patient 0.831 live / 0.913 gold-parse
  ceiling; parser named `upstream_needed` for other consumers); the precision-defer SOLVED (search-failure + label-bias
  evidence).
- **Gold:** modern UD-EWT on disk / a pinned fetch under `data/corpora/<name>/` (attachment + patient); QA-SRL OOD companion.
- **Motivation + fence:** `notes/WALL_MAP_non_brain_foundational_decisions_2026-09-06.md` Wall 2 + THE DOMINANT FINDING; the
  audit parser entry. Build in `experiments/` + `verification/`; strategy lands any hdlab change (Q111). Heavy -> REMOTE
  (`notes/problems/REMOTE_RUNS_SOLVER_BRIEF.md`). Fold an **AUDIT UPDATE** into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (the
  parser is now globally-normalized / graded with marginals + a 2nd-best, or a located negative naming the
  scorer-vs-normalization bottleneck).

## DO NOT QUOTE / DO NOT REDO
- Do NOT quote the small-beam readout numbers (beam <= raw conf; gold-in-beam-when-wrong 0.492) as evidence the graded
  direction FAILS -- they are the precision-defer SOLVED's proof that a wider DECODER over a LOCALLY-normalized model fails.
  The deliverable is a globally-normalized MODEL (exact marginals or global training), a DIFFERENT object.
- Do NOT quote UAS 0.842 as the thing to beat -- UAS is the WRONG target (better UAS moves who-did-what ~+0.00). Beat the
  greedy 1-best on the graded / 2nd-best object + the live downstream read.
- Do NOT quote the patient 0.831 / 0.913 across scorers or populations -- it is clean UD-EWT n=1255; recompute the floor on
  your own population. No number crosses scorers / populations.
- Do NOT wire post-hoc re-attachment, train a deep OOD-losing parser, or use an external LLM at inference (the invariant).
  Do NOT lean on a 19c corpus as load-bearing gold (BANNED 2026-09-06). Strategy owns any hdlab landing (Q111).

---

**TLDR (plain English):** Our reader's grammar engine makes one snap decision per word and never keeps a runner-up, so when
it guesses the sentence structure wrong -- which about half the time happens because it threw the right structure away early
-- the part that works out who did what is reading off a silently-broken skeleton with nothing to fall back on, and it makes
that guess before it has any sense of the story. Build a grammar engine that keeps a real spread of possible structures with
a genuine "how likely" number for each, giving both a runner-up to fall back on and a confidence the rest of the reader can
trust. Prove it is more accurate than the snap-decision engine on modern writing and that it makes who-did-what measurably
better -- with a scrambled-confidence version failing, so we know the real spread is carrying the load.

**QUESTIONS:** none.

**NEXT STEPS:** the solver runs VERIFY BEFORE YOU START (confirm the live reader reads role heads off the greedy
`arceager_parser` and that `arc_parser` is arc-factored but decodes greedily with no marginals), reads the two SOLVEDs + the
wall-map in full, builds a glass-box globally-normalized / graded parser (exact Matrix-Tree edge marginals over the landed
arc-factored scorer, or Andor-style global training of the transition parser) that emits edge marginals + a genuine 2nd-best,
and reports the attachment / 2nd-best-recovery margin over the greedy 1-best PLUS the live patient / obl lift with the
shuffled-marginals twin (CI half-width + null p95) -- or a located negative naming the scorer-vs-normalization bottleneck.
The deeper prize (named, not required): feed this graded parse into the recurrent top-down loop so the situation model
constrains attachment as it reads.
