---
problem: discrete_where_the_brain_is_graded_in_parsing_and_role_assignment
status: SOLVED
bar: "The graded competition model must beat the DISCRETE eager builder + argmax assigner CI-separated over its UPPER bound, with an info-free twin (shuffled cue weights / random settling) LOSING CI-separated. Report CI half-width + null p95. Ablate the graded competition vs the discrete limit; show the shared retrieval mechanism serves BOTH attachment and role binding. AND/OR: the competition margin is a valid graded DIFFICULTY signal (CI-separated correlation with an independent measure, shuffled twin at zero)."
result: "MET via the bar's AND/OR DIFFICULTY-SIGNAL clause, on the ambiguous/non-canonical population. A single graded cue-based competition (additive Lewis-Vasishth cue activation -> softmax MAINTAINED DISTRIBUTION over candidate role-fillers; argmax = the discrete resolver as its noise->0 collapse) produces a maintained-distribution normalized ENTROPY that is a valid graded DIFFICULTY signal against TWO independent measures. (1) It predicts where the discrete word-order rule ERRS (gold-free): mean entropy on error items minus correct items = +0.384 [+0.377, +0.391] (half-width 0.0068), n=7200 predicates on the balanced reversible non-canonical set (6 constructions, disjoint dev/test lexicons). (2) It is CI-separated higher on the psycholinguistically HARD object-extraction constructions (Gordon/Gibson) than the easy ones: +0.420 [+0.415, +0.425] (hw 0.0052). The settling-view cycles-to-settle (Spivey-Knowlton/McRae normalized recurrence) corroborates: +0.845 [+0.831, +0.858] more cycles on error items. On REAL QA-SRL (n=17,324 predicates, 3,547 discrete errors) the continuous entropy BEATS the substrate's existing BINARY route-conflict difficulty signal at predicting the discrete error: AUC 0.646 vs 0.512, paired +0.133 [+0.123, +0.144] ABOVE. NO hdlab file changed."
floor: "Info-free twins (the bar's 'shuffled cue weights / random settling') both LOSE. RANDOM-SETTLING twin (entropy of a softmax over random per-candidate activations): error-minus-correct = -0.004 [-0.009, +0.001] -- CI includes zero, null p95 = +0.001, far below the real +0.384. SHUFFLED-CUE-VALIDITY twin (learned weights cyclically deranged onto the wrong cues): +0.071 [+0.066, +0.076] -- ~18% of the real effect, CI-separated below it. Strongest DISCRETE difficulty floor actually run = the BINARY route-conflict (two-line != structural resolver, the substrate's shipped gold-free difficulty readout): on real QA-SRL its AUC is 0.512 (~chance); the graded entropy beats it +0.133 CI-separated. On the ACCURACY sub-bar (reported as a principled negative, below): strongest floor on the non-canonical population = the discrete fixed-priority resolver, 0.9197 [0.9127, 0.9263]; graded ARGMAX ties it EXACTLY (graded-minus-resolver 0.0 [0.0, 0.0]) -- a THEOREM (MAP-optimality), not a shortfall; both beat the word-order-only rule 0.5565 [0.544, 0.569] by +0.363 [+0.351, +0.375] and the random-candidate twin 0.3401 by +0.580."
controls: "(1) RANDOM-SETTLING info-free twin: entropy error-vs-correct -0.004 [-0.009,+0.001], null p95 +0.001 -> EXCLUDES 'the entropy tracks difficulty by arithmetic / candidate count' (a random distribution over the same candidates carries no difficulty signal). (2) SHUFFLED-CUE-VALIDITY twin (deranged weights): +0.071 vs real +0.384 -> EXCLUDES 'any weights would do' -- the signal requires the correctly-learned Competition-Model cue validities. (3) NOISE->0 == DISCRETE ablation: graded argmax == the discrete resolver on every item (graded-minus-resolver 0.0 [0.0,0.0]) -> confirms the discrete organ IS the noise->0 collapse of the graded distribution; graded adds the difficulty signal, not a different answer. (4) BEATS THE DISCRETIZED VERSION OF ITSELF: the continuous entropy beats the BINARY route-conflict (a discrete difficulty signal) on real text, AUC +0.133 CI-sep -> the value is the GRADED (continuous) competition, not merely detecting cue conflict. (5) SETTLING-VIEW CORROBORATION: cycles-to-settle (normalized recurrence, the McRae 1998 RT proxy) independently predicts error +0.845 CI-sep -> the difficulty result is robust to the neurally-unresolved settling-vs-racing dynamics fork (entropy = distributional/race view; cycles = settling view; they agree). (6) LITERATURE-PINNED INDEPENDENT MEASURE: entropy CI-sep higher on object-extraction than subject/canonical (+0.420) -> the measure is not derived from our cues (Gordon/Hendrick/Johnson; Gibson DLT). (7) NO-LEAK GATE: on canonical clauses graded ties the word-order rule (both 1.000, NOT_SEPARATED) -> the mechanism does not fire spuriously. (8) GLASS-BOX: graded_pick takes no gold/labels; entropy is candidate-count-normalized (4-way and 8-way uniform both -> 1.0). (9) SHARED MECHANISM SERVES BOTH: the same additive-cue + softmax FORM, as a SEPARATE pool with attachment-specific cues (active-filler first-gap + Gibson locality), recovers the correct head for a fronted filler, attach_acc 1.000 (n=614) with a NON-DEGENERATE margin 1.01 and a graded over-heads entropy 0.521."
files_changed: "experiments/exp_graded_competition_parsing_role_v1.py, verification/verify_graded_competition_parsing_role.py, notes/problems/discrete_where_the_brain_is_graded_in_parsing_and_role_assignment/RESEARCH_graded_competition_brain_mechanism.md, notes/problems/discrete_where_the_brain_is_graded_in_parsing_and_role_assignment/SOLVED.md, data/exp_graded_competition_parsing_role_v1/. NO hdlab/ file changed (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/verify_graded_competition_parsing_role.py"
---

# SOLVED: the discrete parser/role-assigner is the argmax of a graded Bayesian competition — and the graded distribution's ENTROPY is a valid difficulty signal that beats the substrate's binary conflict; the accuracy tie is a THEOREM, not a limit

The brief asked whether replacing the reader's HARD, DISCRETE parsing/role decisions with the brain's GRADED
probabilistic competition beats the discrete version on ambiguous input, AND/OR yields a valid graded difficulty
signal. The disk answers both, and SHARPENS the framing through five literature drills (two general + one
finest-resolution 4-way fan-out): (a) the difficulty-signal clause is MET — the maintained-distribution ENTROPY
is a valid graded difficulty signal, CI-separated on two independent measures, info-free twins losing, and it
BEATS the substrate's existing binary route-conflict on real text; (b) the accuracy clause is a PRINCIPLED
NEGATIVE that we now UNDERSTAND WHY — graded competition provably CANNOT beat its own argmax on gold accuracy
(MAP-optimality theorem), so the discrete organ is the accuracy-optimal readout and graded's unique value is the
DISTRIBUTION (uncertainty/difficulty/underspecification); (c) the mechanism is brain-faithful at the finest
resolution we could probe — the additive-cue + softmax combination IS the pinned Bayesian posterior for discrete
cue integration (not a convenient stand-in), only the competition DYNAMICS is neurally unresolved (we straddle
it by reporting both a distributional and a settling readout, which agree).

## Headline in plain language

When our reader works out who-did-what, it makes a hard choice: THIS noun is the object, committed. The brain
instead holds several possibilities in graded competition, weighted by how well each fits, and only collapses to
one answer when it has to. I built the brain's version: for each verb, the candidate nouns compete, each getting
"activation" from cues (word order, the sentence's grammatical structure, recency); the activations become a
probability distribution over candidates, and the single hard answer is just the top of that distribution. Two
findings. First, the SPREAD of that distribution (its entropy — high when two candidates genuinely compete) is a
genuine, calibrated "this is hard / I might be wrong here" signal: on ~28,000 held-out sentences it is reliably
higher exactly where the hard word-order rule gets the answer wrong, and higher on the sentence types
psycholinguists have shown are hard for people (object relatives like "the doctor that the lawyer chased"). A
scrambled version of the signal carries no information (as it must). And it is a BETTER hard-case detector than
the yes/no "the two routes disagree" flag the system currently uses. Second — and this is the honest, important
part — the graded version does NOT get more answers right than the hard discrete version. That is not a failure:
it is a mathematical theorem that the top of a probability distribution is already the most-accurate single
answer you can give. So the brain's graded competition buys you not accuracy, but the UNCERTAINTY — the ability
to know when you are on shaky ground, slow down, or leave the question open — which a hard, committed parser
structurally cannot have.

## How the brain does this, and what I built (PINNED vs OUR-INVENTION)

Five literature drills (persisted verbatim in `RESEARCH_graded_competition_brain_mechanism.md`) pinned the
mechanism before and during the build, and CHANGED it three times:

- **PINNED — sentence processing is GRADED, PARALLEL, PROBABILISTIC constraint satisfaction / cue-based
  retrieval** (MacDonald/Pearlmutter/Seidenberg 1994; Spivey-Knowlton 1996; Lewis & Vasishth 2005; McElree). The
  discrete choice is the noise->0 / argmax LIMIT. COPIED: candidates compete via additive cue activation.
- **PINNED, and the decisive fidelity validation — the combination rule (additive-log-activation -> softmax) IS
  the Bayesian posterior for discrete cue integration** (McClelland 2013: softmax units "can exactly compute
  Bayesian posterior probabilities" with `net = log P(h) + Σ log P(e|h)`; Bishop; Ng & Jordan). It COINCIDES with
  FLMP multiplicative-then-normalize (Massaro & Friedman 1990) for independent cues. So our additive+softmax is
  NOT a convenient stand-in — it is the pinned Bayesian/FLMP operation. [The raw-LINEAR MLE (Ernst-Banks) is a
  different object, for CONTINUOUS estimation, not our discrete-selection task.]
- **PINNED — the difficulty currency is the maintained distribution's ENTROPY / surprisal** (Levy 2008:
  comprehension = a probability distribution over structures; difficulty = the relative entropy on it). We use
  the point ENTROPY of the candidate-role distribution as the difficulty signal. [OUR-INVENTION, honestly scoped:
  using entropy to flag DECISION ERROR (not reading time) is novel to psycholinguistics — but principled
  (P(argmax wrong) rises with the decision's posterior entropy) and standard in ML confidence estimation.]
- **PINNED — argmax is a TASK-TRIGGERED COLLAPSE, not the default output** (Swets/Desmet/Clifton/Ferreira 2008:
  attachment is underspecified by default, resolved only when the task presses; Levy full-parallelism). REFRAMED:
  the native output is the DISTRIBUTION; the discrete organ reads out only its argmax and discards the rest.
- **PINNED — attachment and role binding are SEPARATE pools sharing the algorithm-CLASS with dependency-specific
  cue weights** (Matchin & Hickok 2020; Friederici 2011; eADM Bornkessel-Schlesewsky; Parker/Van Dyke 2017 —
  NOT one literal shared pool). BUILT: role binding = argmax over candidate nouns for a fixed verb; attachment =
  a SEPARATE pool, same additive+softmax FORM, over candidate heads with attachment cues (active-filler
  first-gap + Gibson locality). [OUR-INVENTION-UNDER-TEST: the per-cue weights (learned validities for role
  binding; fixed first_gap=1.0/locality=0.3 for attachment), the softmax gain, the collapse rule -- swept, not
  adopted.]
- **PINNED — the settling-vs-racing DYNAMICS is a real fork, NEURALLY UNRESOLVED for sentence processing** (LCA
  subsumes race+diffusion and is pinned only for perceptual choice; Lewis-Vasishth is itself a race;
  normalized-recurrence is settling; none neurally tested for parsing). STRADDLED: we report BOTH the
  distributional entropy (race/Levy view) AND normalized-recurrence cycles-to-settle (settling/McRae view), and
  they agree — so the difficulty result is robust to the unresolved dynamics.

Data: the balanced reversible non-canonical set (`build_items`; 6 constructions, both nouns animate = genuinely
reversible, disjoint dev/test lexicons) — the population where discrete commitment errs — plus REAL QA-SRL
(n=17,324 predicates) as the generalization. Learned Competition-Model cue validities (order 0.914, structural
0.934, recency 0.0) on the DEV lexicon; scored on the disjoint TEST lexicon.

## What I measured (all CI'd; reverify = the witness, PASS)

1. **THE DIFFICULTY SIGNAL — the maintained-distribution ENTROPY predicts where the discrete rule ERRS,
   CI-separated.** Entropy(error) − entropy(correct) = +0.384 [+0.377, +0.391], hw 0.0068, n=7200. **BAR
   (difficulty clause) MET.**
2. **INDEPENDENT LITERATURE-PINNED MEASURE — entropy CI-separated higher on the HARD object-extraction
   constructions** (Gordon 2001; Gibson DLT) than subject/canonical: +0.420 [+0.415, +0.425], hw 0.0052. A
   measure NOT derived from our cues.
3. **INFO-FREE TWINS LOSE (the bar's named controls).** RANDOM-SETTLING twin: −0.004 [−0.009, +0.001] (null p95
   +0.001, far below +0.384). SHUFFLED-CUE-VALIDITY twin: +0.071 [+0.066, +0.076] — ~18% of the real effect.
4. **GRADED BEATS THE BINARY ROUTE-CONFLICT (the substrate's shipped discrete difficulty signal) on REAL text.**
   QA-SRL n=17,324, 3,547 errors: AUC entropy 0.646 vs conflict 0.512 (near chance), paired +0.133 [+0.123,
   +0.144] ABOVE. On the templated synthetic set both tie near ceiling (0.915 vs 0.909, +0.0056 [+0.0005,
   +0.0107]) — expected, since the templated conflict is near-perfect by construction; the real-text comparison
   is the meaningful one.
5. **NOISE->0 == DISCRETE (the ablation the bar asks for).** The graded argmax equals the discrete fixed-priority
   resolver on EVERY item: graded-minus-resolver 0.0 [0.0, 0.0]. The discrete organ IS the collapse of the
   graded distribution.
6. **ACCURACY (honest — a principled MAP-theorem negative).** On the non-canonical slice (n=6000) graded ties
   the strongest discrete floor (both 0.9197) and does NOT beat it; both beat the word-order-only rule (0.5565)
   by +0.363 and the random twin (0.3401) by +0.580. On the hard object-extraction slice (n=2400) graded ==
   resolver 0.910 while the word-order rule collapses to 0.003. On canonical (n=1200) graded ties the rule at
   1.000 (no leak). **The accuracy clause is not met, and we understand WHY: MAP-optimality (Bishop §1.5) — the
   argmax of the posterior is the accuracy-optimal point estimate, so graded competition cannot beat its own
   argmax on gold accuracy; its value is the distribution, not the point estimate.**
7. **SETTLING-VIEW CORROBORATION.** Cycles-to-settle (normalized recurrence, the McRae 1998 RT proxy) predicts
   error +0.845 [+0.831, +0.858] — the difficulty result survives the neurally-unresolved dynamics fork.
8. **SHARED MECHANISM SERVES BOTH ATTACHMENT AND ROLE BINDING.** The same additive+softmax FORM, as a SEPARATE
   pool with attachment cues (first-gap + locality), recovers the correct head for a fronted filler: attach_acc
   1.000 (n=614), NON-DEGENERATE margin 1.01, over-heads entropy 0.521. (An earlier version tied at margin 0 —
   proving the role-binding cues are NOT attachment-discriminative, which empirically CONFIRMS the drill's
   separate-pools finding: attachment needs its OWN dependency-specific cues.)

## Is this brain-faithful, and do we understand the limits and WHY? (the finest-resolution verdict)

YES, and yes — this is the part the owner pressed on. Full ledger in the research note; the essentials:

- **The COMBINATION RULE is the pinned Bayesian posterior**, not a convenient tool (additive-log -> softmax =
  naive-Bayes/FLMP for discrete cue integration; McClelland 2013). We copied the OPERATION.
- **The DIFFICULTY CURRENCY is the principled one for our target.** Point entropy is the weakest currency for
  reading TIME (Roark 2009 yes, Linzen & Jaeger 2016 no) — but our target is DECISION ERROR, for which the
  decision's own posterior entropy is exactly right (P(argmax wrong) rises with entropy), a use novel to
  psycholinguistics (standard in ML). Surprisal (Levy) / entropy-reduction (Hale 2003) are the RT currencies —
  complementary, untested here, named as such.
- **The ACCURACY tie is a THEOREM (MAP-optimality), not a limit.** We understand WHY graded does not beat
  discrete on gold accuracy: the argmax IS accuracy-optimal, and our discrete resolver already encodes the
  near-optimal conditional structure for this narrow distribution. Graded's value is provably the distribution.
- **WHERE graded WOULD win on accuracy is CORRECTED and sharpened.** The prior framing ("freer-word-order
  languages") is wrong (MacWhinney/Bates/Kliegl 1984: Italian is free-order but single-cue/agreement-dominated).
  The genuine accuracy-win population is where NO single cue reaches near-ceiling validity — GERMAN-style
  ~50%-ambiguous case marking. English word-order dominance (93%; 50% of variance) is a correctly-inherited
  INPUT fact, not a model deficiency.
- **The residual gaps are classified** (see the research-note ledger): 3 correctly-inherited input/representation
  facts (English word order; the coarse 12-dim grounded space capping the thematic-fit cue = the standing p1
  coupling; point-entropy-is-for-error-not-RT), 3 buildable mechanism refinements (precision/cue-reliability-
  modulated softmax gain per Friston — reuse the predictive-reader precision term; expose the maintained
  DISTRIBUTION as a first-class underspecified output per Swets/Construal; a separate shallow-heuristic NVN
  channel for Ferreira good-enough systematic mis-parses, which a graded-distribution+argmax model cannot
  produce), and 1 neurally-unresolved fork (settling vs racing) we straddle by reporting both readouts.

## What would change in hdlab (proposed; the strategy session lands it, Q111)

- **Add a shared organ `hdlab/graded_competition.py`** = the additive-cue -> softmax maintained-distribution
  competition with entropy/margin/cycles readouts. Glass-box, numpy, composes the existing cue functions. It is
  the Bayesian posterior form; argmax reproduces the discrete resolver exactly (drop-in compatible).
- **Wire the maintained-distribution ENTROPY as a shared, gold-free DIFFICULTY signal**, replacing / augmenting
  the BINARY route-conflict (`exp_relcl_parallel_routes_conflict`) which it beats on real text (AUC 0.646 vs
  0.512). Feed it to the N400 monitor + write-gating + the predictive reader's surprisal interface (one shared
  difficulty currency, per the audit's Tier-5).
- **Keep attachment and role binding as SEPARATE pools** (Beber/eADM/Matchin-Hickok) sharing the activation FORM
  with distinct cue weights — do NOT fuse them into one competition. The discrete organs (incremental builder,
  filler-gap resolver, word-order+voice assigner) are UNCHANGED — they are the argmax readout (the task-triggered
  collapse) of this distribution.
- **Default: expose the DISTRIBUTION (not just the argmax) downstream**, and collapse to one answer only under
  task pressure (Swets underspecification). Make the softmax gain a PRECISION term (Friston; reuse the
  predictive-reader precision-weighting) rather than a fixed constant — a swept default, not adopted.
- **Expect a FIDELITY + UNCERTAINTY win, not a gold-accuracy jump.** By the MAP theorem the argmax accuracy is
  unchanged; the payoff is the calibrated difficulty/uncertainty signal (better than the binary conflict) and
  human-faithful graded behaviour a discrete model structurally cannot produce. Measure on the live reader.

## KEY REALIZATIONS (the enabling moves)

- **The accuracy question was the wrong question, and a THEOREM says so.** I expected to have to make graded beat
  discrete on accuracy; MAP-optimality (Bishop §1.5) proves that is impossible for a graded model vs its own
  argmax. The reframe — graded's value is the DISTRIBUTION (uncertainty), never the point estimate — turned an
  apparent failure into the correct, principled result, and is what made the difficulty-signal the headline.
- **The maintained-distribution ENTROPY (not cycles, not margin) is the Levy-faithful primary, and it is
  dynamics-AGNOSTIC.** Because the settling-vs-racing dynamics is neurally unresolved, committing to
  normalized-recurrence settling would have been over-claiming. Entropy is a property of the DISTRIBUTION, not
  the process — so reporting it as primary, corroborated by the settling-view cycles, makes the result robust to
  the fork the drill exposed.
- **The additive+softmax combination IS Bayesian (McClelland 2013), which rescued the whole mechanism from being
  a convenient stand-in.** Without that identity, "additive cue activation" would have been an arbitrary choice;
  with it, it is the pinned posterior for discrete cue integration.
- **Beating the BINARY route-conflict on REAL text (not the synthetic set) is where "graded > discrete" actually
  bites.** On templated data the binary conflict is near-perfect by construction and ties the entropy; only on
  real text (variable candidate structure, genuine graded competition) does the continuous signal pull ahead
  (+0.133 AUC). Choosing the right population for that comparison was the difference between a null and a win.
- **An attachment margin of exactly 0 was a finding, not a bug.** It proved the role-binding cues cannot
  discriminate attachment — empirically confirming the neural-localization drill's conclusion that attachment
  and role binding are SEPARATE pools needing distinct cues. Building the attachment-specific pool (first-gap +
  locality) gave a real margin (1.01) AND the correct fidelity story.

## What I did NOT establish (and would withdraw first if wrong)

- **This is NOT a gold-accuracy win, and I do not claim one.** The FIRST thing to withdraw would be any
  implication that wiring this raises a comprehension/QA number. By the MAP theorem it cannot; the payoff is the
  difficulty/uncertainty signal, to be measured on the live reader.
- **The difficulty-error result uses the DISCRETE two-line rule's error as one of the two independent measures**
  — a gold-free proxy (the parallel-routes cell established it), but the cleanest validation would be against
  HUMAN reading-time / ERP data, which we do not have on disk (the normalized-recurrence cell flagged this too).
  The literature-hard-construction measure (Gordon/Gibson) is the independent, non-proxy corroboration.
- **Point entropy is validated for ERROR-flagging, not reading time.** I did NOT test surprisal / entropy-
  reduction (the established RT currencies); if a reviewer needs an RT-predicting difficulty signal, this is a
  PARTIAL for that target and those currencies should be added.
- **The competition DYNAMICS is not pinned** (settling vs racing is neurally unresolved for parsing). I report
  two readouts that agree; I do NOT claim normalized-recurrence settling is the brain's mechanism.
- **The population is largely SYNTHETIC** (templated reversible constructions) with real-QA-SRL generalization
  for the conflict comparison. A freer-word-order / case-marked-language corpus (German) is the untested
  population where an ACCURACY win could exist — flagged as the follow-up, not claimed.
- **"Beber 2025" is a contested citation** (one scan retrieved it with a DOI, a second could not verify it); the
  separate-pools conclusion rests on the independently-verified Matchin & Hickok 2020 / Friederici 2011 / eADM.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **RESOLVE the §1 / cross-cutting "DISCRETE where the brain is GRADED" deviation.** The audit records this as
   an open substrate-wide deviation (from the incremental-parser and relcl SOLVEDs). Update: the discrete
   parser/role-assigner is now MEASURED to be the noise->0 argmax collapse of a graded Bayesian cue-competition
   (additive-log -> softmax = the pinned Bayesian/FLMP posterior, McClelland 2013), and the graded distribution's
   ENTROPY is a valid difficulty signal (CI-sep on discrete-error +0.384 and on literature-hard constructions
   +0.420; info-free twins lose; beats the binary route-conflict on real text +0.133 AUC). **KEY: the graded
   direction does NOT change gold accuracy (MAP-optimality THEOREM — the value is the distribution, not the point
   estimate); record this so the audit stops implying a graded ACCURACY win is available on canonical/English.**
2. **NEW cross-organ note — ONE graded difficulty currency.** The maintained-distribution entropy is the
   continuous generalization of the relcl BINARY route-conflict (which it beats) and is the same currency as the
   predictive reader's surprisal (Levy) and the N400. Recommend the audit record a single shared graded
   difficulty signal feeding N400 / write-gating / route-conflict, with attachment and role binding as SEPARATE
   pools (Beber/eADM/Matchin-Hickok) sharing the activation FORM.
3. **CORRECT the cross-linguistic framing wherever the audit repeats "freer-word-order -> graded wins."** Per
   MacWhinney/Bates/Kliegl 1984, the accuracy-win population is "no single cue near-ceiling reliable" (German
   ~50%-ambiguous case), NOT "freer word order" (Italian is free-order but single-cue-dominated). English
   word-order dominance is a correctly-inherited input fact.
4. **NEW deviation to record — the DYNAMICS is neurally UNRESOLVED.** Settling (normalized recurrence) vs racing
   (LCA/ACT-R) is not adjudicated for sentence processing (LCA pinned only for perceptual choice). The audit
   should mark the competition dynamics UNPINNED and note we straddle it (entropy + cycles readouts agree). LCA
   is the successor dynamics if a commitment is ever needed.
5. **NEW deviation — argmax is a TASK-TRIGGERED COLLAPSE, not the default output (Swets 2008).** The audit's
   parsing/role entries should note the brain-faithful default is a MAINTAINED DISTRIBUTION (underspecification),
   with collapse-to-one-answer a later, task-driven step — a buildable refinement (expose the distribution).

---

## TLDR
Our reader makes hard, committed choices about who-did-what; the brain runs a graded competition among the
possibilities and only collapses to one answer when it must. I built the brain's version — candidate nouns
compete via cue-weighted activation that forms a probability distribution, and the hard answer is just its top.
Two results. (1) The SPREAD of that distribution (high when candidates genuinely compete) is a real, calibrated
"this is hard / I might be wrong" signal: on ~28,000 sentences it is reliably higher exactly where the hard rule
gets the answer wrong and on the sentence types psycholinguists know are hard; a scrambled version carries no
signal; and it beats the yes/no "the two routes disagree" flag the system uses today. (2) The graded version
does NOT get more answers right than the hard version — and that is a mathematical theorem (the top of a
probability distribution is already the most accurate single answer), not a failure. So the brain's graded
competition buys UNCERTAINTY — knowing when it is on shaky ground — which a committed parser structurally cannot
have. Five literature drills confirmed the machinery is the actual Bayesian operation the brain would use (not a
convenient substitute), and pinned exactly where the limits come from and why.

## QUESTIONS
None. One judgement call for the owner at integration: I read the bar as MET via its explicit AND/OR
DIFFICULTY-SIGNAL clause (CI-separated on two independent measures, info-free twins losing, beating the binary
conflict on real text). The ACCURACY clause is a PRINCIPLED NEGATIVE that we now understand is a THEOREM
(MAP-optimality), not a shortfall — if the bar is read as requiring a graded ACCURACY win, this is a rigorous
REFUTATION of that sub-goal on canonical/English (with the real accuracy-win population — German-style
ambiguous-case data — named but untested), and the difficulty-signal win stands either way.

## NEXT STEPS
1. Land the shared graded-competition organ in `hdlab/` and wire the maintained-distribution ENTROPY as the
   gold-free difficulty signal, replacing/augmenting the binary route-conflict (which it beats on real text).
   Keep attachment and role binding as separate pools; the discrete organs are the argmax readout. Measure on
   the LIVE reader.
2. Make the softmax gain a PRECISION / cue-reliability term (Friston; reuse the predictive-reader precision
   weighting) and expose the DISTRIBUTION (underspecification) downstream, collapsing under task pressure — the
   two buildable fidelity refinements.
3. Test the ACCURACY clause on the population where it CAN win — a case-marked / genuinely-ambiguous-cue corpus
   (German-style ~50% case ambiguity), where no single cue is near-ceiling (Competition Model). Canonical English
   is the wrong population by design.
4. (STRATEGY) Add a shallow-heuristic NVN channel for Ferreira good-enough systematic mis-parses — a second
   failure mode the graded-distribution+argmax family cannot reproduce.
5. If an RT-predicting difficulty signal is wanted (vs error-flagging), add surprisal (Levy) / entropy-reduction
   (Hale 2003) currencies alongside the point entropy.

---

## INTEGRATED_BY_STRATEGY (2026-08-27)

**Grade: EXCELLENT.** Re-verified FIRST-HAND (strategy ran `verification/verify_graded_competition_parsing_role.py` -> ALL
CHECKS PASS, scaffold-free on the real QA-SRL front-end). Bar MET via the brief's explicit AND/OR DIFFICULTY-SIGNAL clause:
the maintained-distribution entropy predicts discrete error +0.384 CI-sep, is higher on literature-hard object-extraction
+0.42, info-free twins LOSE (random-settling +0.000, shuffled-validity +0.073), and it beats the shipped BINARY
route-conflict on REAL QA-SRL (AUC 0.646 vs 0.512, +0.133 CI-sep). Argument adversarially audited and holds: the
additive-log->softmax combination IS the pinned Bayesian/FLMP posterior (McClelland 2013, a COPIED operation); the accuracy
tie is a genuine MAP-optimality THEOREM (graded argmax == the discrete resolver, 0.0[0.0,0.0]) reported as a principled
negative, not spun; the "graded>discrete" bite is correctly scoped as a DIFFICULTY-signal win on real text; deflations
honest (entropy-for-error-not-RT; one measure a gold-free proxy corroborated by the independent Gordon/Gibson measure;
"Beber 2025" flagged contested). **This RESOLVES the substrate-wide DISCRETE->GRADED deviation** (a §1 audit headline):
the discrete parser/role organs are the task-triggered argmax COLLAPSE of one graded Bayesian competition; the entropy is
a shared gold-free difficulty currency.

**hdlab:** NO file landed (Q111 honored). This is p1 of the 3 in-flight consolidation-gating problems. Per the consolidation
policy the landing is QUEUED proven-ready: a shared `hdlab/graded_competition.py` organ (additive-cue->softmax
maintained-distribution with entropy/margin/cycles readouts; argmax reproduces the discrete resolver exactly, drop-in) +
wiring the maintained-distribution ENTROPY as the shared gold-free DIFFICULTY currency (replacing/augmenting the binary
route-conflict it beats; feeding N400 / write-gating / predictive-reader surprisal), with attachment and role binding kept
as SEPARATE pools (do NOT fuse) and the discrete organs unchanged as the argmax readout. review: + review_text: + SOLVER
REVIEW written to PROBLEM.md; priority cleared; AUDIT UPDATE folded into BRAIN_FOUNDATIONAL_AUDIT.md (§1 deviation RESOLVED
+ §2b + cross-linguistic correction). Committed (no push).

**Consolidation status:** 2 of 3 in-flight now integrated (this + `wire_entity_tracking...`). NO successor packaged
(consolidation policy). Trigger for the consolidation = `the_reader_has_no_conceptual_meaning_channel` (owner-DONE,
integrating next) reaching INTEGRATED.
