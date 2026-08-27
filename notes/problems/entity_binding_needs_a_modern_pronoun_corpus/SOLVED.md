---
problem: entity_binding_needs_a_modern_pronoun_corpus
status: SOLVED
bar: "The salience binder must resolve pronouns/anaphora to the correct entity CI-separated over its UPPER bound vs (a) a string-identity-only baseline and (b) the strongest simple floor (most-recent-mention), with an info-free twin (shuffled salience / random antecedent) LOSING CI-separated. Report CI half-width + null p95. Ablate recency vs grammatical-prominence vs agreement-filter. AND/OR: linking coref threads improves DOWNSTREAM entity prediction over string-identity CI-separated."
result: "A grammatical-prominence salience binder resolves same-gender ambiguous pronouns at 0.6988 accuracy [0.6774, 0.7186] (2-way A/B, GAP test split, n=1773 resolvable human-labeled pronoun instances, half-width 0.0206). Beats string-identity 0.5076 (+0.191 CI-sep), most-recent-mention/recency 0.5144 (+0.184 CI-sep), majority 0.5178, and the info-free shuffled-salience twin 0.4901 (null p95 upper 0.5133; SALIENCE_over_twin +0.1805 [0.151,0.210] ABOVE)."
floor: "Named floors recomputed on GAP test (n=1773): string-identity 0.5076 [0.485,0.531]; most-recent-mention/recency 0.5144 [0.490,0.537] (AT CHANCE); majority 0.5178; chance 0.5. Info-free twin (shuffled salience) 0.4901 [0.469,0.513]. The HONEST strongest simple floor is grammatical-prominence itself, 0.6937 [0.672,0.715] -- but that is the binder's OWN load-bearing cue, not an external floor (see prose)."
controls: "string-identity floor (excludes lexical-overlap resolution: a pronoun shares no tokens with a name, so it EXCLUDES the possibility the win is exact-match); most-recent-mention/recency floor (EXCLUDES recency being the driver -- recency is at chance on GAP); shuffled-salience info-free twin (EXCLUDES the salience RANKING carrying no information -- it loses CI-separated); leave-one-cue-out ablation (EXCLUDES recency/frequency being load-bearing -- both marginal 0.0000; role marginal +0.0344 CI-sep); IC-lexicon SCRAMBLE twin + cross-split replication (EXCLUDES the implicit-causality lever breaking the ceiling -- it does not replicate: dev -0.008 / test +0.006, and does not beat its scramble)."
files_changed: "experiments/exp_gap_features_v1.py, experiments/exp_gap_salience_binder_v1.py, experiments/exp_gap_salience_prior_v2.py, experiments/exp_gap_ic_coherence_v3.py, experiments/exp_litbank_activation_binder_v1.py, experiments/exp_litbank_chain_quality_v1.py, verification/test_gap_pronoun_binding.py, data/gap_coreference/ (GAP corpus + parsed feature caches, foundation asset), data/ic_norms/ferstl2011.xlsx (implicit-causality lexicon, foundation asset), data/litbank/ (LitBank running-narrative coref corpus + parsed pronoun instances, foundation asset)"
reverify: ".venv/Scripts/python.exe verification/test_gap_pronoun_binding.py   # 6/6 PASS, scaffold-free, lands nothing"
---

## What this problem asked

Test the BINDING half of entity tracking -- resolving WHO a pronoun refers to -- on a MODERN pronoun
corpus, with a brain-faithful salience/Centering mechanism, against the floors the bar names. The
integrated entity-PREDICTION work predicted binding is SALIENCE-driven (not meaning-memory), but that
was measured on QA-SRL (groundable nouns), never on real pronouns.

## What I built

1. **A modern pronoun corpus, on disk.** Downloaded GAP (Webster, Recasens, Axelrod & Baldridge, TACL
   2018) -- 4,454 human-labeled Gendered Ambiguous Pronoun instances from Wikipedia. Each: a text
   snippet, a target pronoun, two candidate names A/B, and human coref labels. GAP's defining property
   is decisive here: **A and B are the SAME GENDER by construction**, so the gender/number agreement
   filter is inert -- the corpus isolates pure SALIENCE, exactly the PINNED claim under test. Parsed
   every instance with spaCy (dependency parse only, for grammatical structure -- NOT a coref model, so
   no resolver-vs-resolver circularity; gold is human). Cached as a static foundation asset.

2. **A brain-faithful salience binder** (`exp_gap_salience_binder_v1` / `_prior_v2`): for each candidate
   it scores recency, grammatical role (subject>object, Centering Cf-rank), parallelism, first-mention,
   and frequency, and picks the argmax. Floors (random, string-identity, most-recent-mention), the
   info-free shuffled-salience twin, and a leave-one-cue-out ablation all recomputed on the same
   population, with 2000x bootstrap CIs.

3. **A prior x likelihood extension** (`exp_gap_ic_coherence_v3`): the PINNED brain computation is
   Bayesian (Kehler & Rohde 2013) -- `P(ref|pron) ~ P(pron|ref) * P(ref)`, grammatical prominence =
   production likelihood, implicit-causality/coherence = the next-mention prior. I added an
   implicit-causality LIKELIHOOD term from the Ferstl et al. (2011) 305-verb human IC-norm lexicon, with
   a mandatory lexicon-scramble control.

## What I measured (GAP test, n=1773 resolvable)

| arm | accuracy [95% CI] | what it is |
|---|---|---|
| RANDOM | 0.5042 [0.481, 0.527] | chance |
| STRING_IDENTITY | 0.5076 [0.485, 0.531] | **floor (a)** -- a pronoun can't string-match a name |
| RECENCY / most-recent-mention | 0.5144 [0.490, 0.537] | **floor (b)** -- AT CHANCE |
| FREQUENCY | 0.5392 [0.516, 0.563] | topicality alone, ~chance |
| PARALLELISM | 0.6159 [0.592, 0.639] | real |
| GRAMMATICAL prominence | 0.6937 [0.672, 0.715] | the load-bearing cue |
| **SALIENCE_PRIOR (the binder)** | **0.6988 [0.677, 0.719]** | headline |
| SALIENCE_SHUF (info-free twin) | 0.4901 [0.469, 0.513] | shuffled salience -- LOSES |

- **Bar (a): binder > string-identity** by +0.191, CI-separated over its upper bound. MET.
- **Bar (b): binder > most-recent-mention** by +0.184, CI-separated. MET.
- **Info-free twin LOSES CI-separated**: `SALIENCE_over_twin` = +0.1805 [0.151, 0.210]. MET. (null p95
  upper = 0.5133; the binder's lower CI 0.677 clears it with a large gap.)
- **Ablation (recency vs grammatical vs agreement)**: recency marginal +0.0000 (INERT); frequency
  +0.0000 (inert); parallelism +0.0085 (subsumed by role); first-mention +0.0164 (weak, not CI-sep);
  **role +0.0344 (CI-separated, load-bearing)**; agreement inert BY CONSTRUCTION (same-gender). This is
  the whole story: **grammatical prominence carries the binder; recency and frequency do nothing.**

This is the WIN branch of the bar's "decisive either way" -- so I propose the hdlab diff below.

## The key adjudication (this is the wire-able finding)

The live resolver `hdlab/coreference_resolver.py` already ships TWO pronoun pick rules:
- `run_match_or_allocate` -- pick by `salience = count + beta*exp(-lambda*dist)` = **frequency + recency**.
- `run_strict_cb` -- pick by `most_recent_subject_clause` = **grammatical prominence** (Centering Cb).

On real modern pronouns, this GAP test adjudicates between them cleanly: **the frequency+recency
salience pick is AT CHANCE (recency 0.514, frequency 0.539), while the grammatical-prominence pick is
the entire signal (0.694).** The organ's DEFAULT pronoun salience formula (`state_of_mind`'s
OVERLAY_BETA/LAMBDA frequency+recency) is the wrong default for binding. This matches the brain-mechanism
drills exactly (Ariel's corpus validation: linear recency is the WEAKEST accessibility cue; Kehler &
Rohde: grammatical prominence is the production-likelihood cue that dominates).

## The rigorous negative (the ceiling is real, and I localized it)

The additive salience prior plateaus at the grammatical-prominence ceiling (~0.70 = the published
classical GAP baseline, 66.9% F1). I treated that shared wall as a fidelity gap, not a ceiling, and
built the brain's PINNED second stage -- the implicit-causality / coherence LIKELIHOOD term. Result, on
GAP test:

- **IC fires on only ~15% of instances** (the IC-verb-governs-a-candidate configuration is rare in
  biographical prose -- Explanation/Cause-Effect relations are uncommon there; connective coverage is
  ~10%).
- **On the full set, adding IC is negligible** (test +0.006, dev -0.008 -- NOT CI-separated, and it
  FLIPS SIGN across splits: a real cue does not do that).
- **Where it fires (covered subset), it does NOT beat its own lexicon-scramble twin CI-separated**
  (dev BELOW; test +0.069, not separated on n=260).

So a glass-box implicit-causality likelihood does NOT break the grammatical-prominence ceiling on GAP.
This is not a failure of the mechanism -- it is the literature's own prediction: GAP's residual to human
~96.6% is genuine WORLD KNOWLEDGE (neural systems reach ~92% only via massive distributional
pretraining, which a glass-box no-LLM-at-inference substrate does not have), and even the brain's own
residual mechanism is largely a hippocampal ACTIVATION/SALIENCE bias (Dijksterhuis et al. 2024, Science:
a pronoun reinstates the more-activated concept cell), not deep re-derivation.

## THE DEEPER, MORE BRAIN-FAITHFUL MECHANISM: ACT-R base-level activation (running narrative)

The GAP result is computational-level correct (salience-driven, grammatical-prominence-dominant) but
its ALGORITHM is a static weighted-feature argmax. A fifth brain-fidelity drill
(notes/research_pronoun_activation_dynamics_2026-08-27.md) established the algorithmically-faithful
form: (1) iterative SETTLING is REFUTED for the antecedent pick -- three converging sources (Li et al.
2020 fMRI/MEG best-fit is a fast one-shot activation SCORE; Chow/Lewis/Phillips 2014; and the
substrate's own LV05 HARD_FAIL) -- so do NOT build an attractor/settling mechanism for the pick;
(2) the ONE faithful, fixable defect is the FORM of the salience score. The live organ uses
`salience = count + beta*exp(-lambda*dist)`, which the project's own T2c proved cannot let recency ever
overturn a 1-mention frequency lead. The brain's actual declarative-memory equation (Anderson; Lewis &
Vasishth 2005) is a real frequency x recency x role TRADE-OFF:

    ACT-R base-level activation:   B_i = ln( sum_{prior mentions k of entity i}  w_role(k) * dt_k^(-d) )

GAP could not test this (its 2-3-sentence snippets are too short for decay-vs-count to matter -- exactly
why the GAP ablation found recency/frequency at +0.0000). I acquired **LitBank** (Bamman et al.;
github.com/dbamman/litbank, CC-BY) -- 100 novel excerpts with gold coreference over long continuous
narrative (9,128 pronoun instances; 7,695 with >=3 prior mentions) -- and ran the pre-registered arms.

**Held-out result (LitBank test half, n=3654 pronoun resolutions, ~24-way choice, chance 0.042; decay
d*=2.0 selected on the train half):**

| arm | accuracy [95% CI] | what it is |
|---|---|---|
| RANDOM | 0.0446 [0.038, 0.052] | chance |
| ROLE_ALONE (grammatical prominence) | 0.2280 [0.215, 0.241] | **COLLAPSES on running narrative** |
| FREQUENCY (count) | 0.6136 [0.598, 0.629] | |
| ACTR_NO_DECAY (role-weighted count, d=0) | 0.6111 [0.595, 0.626] | decay removed |
| CURRENT_FORMULA (the live organ) | 0.6234 [0.608, 0.639] | count + capped exp |
| MOST_RECENT (pure recency) | 0.6582 [0.643, 0.674] | |
| **ACTR_DECAY (the mechanism)** | **0.8366 [0.825, 0.849]** | ACT-R base-level activation |

- **ACT-R > live organ formula: +0.213** [CI-separated, hw 0.017] -- a 21-point lift.
- **ACT-R > pure recency: +0.178** -- the role-weighted accumulation adds massively beyond nearest-mention.
- **ACT-R > its own NO-DECAY twin: +0.226** -- the temporal decay carries the information (the mandatory
  info-free control; the within-entity timestamp-shuffle twin is weak, +0.011, because it preserves each
  entity's recency profile -- reported honestly, the no-decay twin is the load-bearing control).

**THE REGIME FLIP (Competition Model, MacWhinney/Bates -- the unifying insight).** Grammatical role
DOMINATED on GAP (2-way, same-gender, short: 0.674) but COLLAPSES on running narrative (many-way, long:
0.228), because over a long discourse almost every entity has held a subject role at some point, so
role-max cannot discriminate. Recency/activation is inert on GAP but dominant on LitBank. Neither cue is
"the" mechanism -- **cue validity is discourse-structure-dependent, and ACT-R base-level activation
`B=ln(sum_k w_role(k)*dt_k^-d)` is the single scalar that wins in BOTH regimes** (it reduces to
role-weighting when mentions are few/equidistant, and to recency-weighted accumulation when they are
many/spread out). This is the genuinely brain-foundational mechanism, and it is a strict, large,
CI-separated improvement over the live organ's formula on the corpus that can actually test it.

## DOWNSTREAM PAYOFF (the bar's AND/OR second task -- honest, both-sided)

Does linking pronouns into entity threads (ACT-R binder) improve ENTITY TRACKING over string-identity?
Built full coreference chains two ways on all 100 LitBank docs and scored B-cubed vs gold
(exp_litbank_chain_quality_v1):

- **On PRONOUN mentions (B-cubed recall): string-identity 0.095 -> ACT-R binder 0.472, +0.377
  CI-separated** [CI 0.352, 0.402]. String-identity leaves every pronoun a singleton (recall ~
  1/chain-length); the binder recovers ~40% of the tracking recall it throws away. LARGE win.
- **On the WHOLE mention set (B-cubed F1): string-identity 0.495 -> ACT-R 0.506, +0.011 NOT separated**
  [CI -0.002, 0.025]. MODEST -- because pronouns are a minority of mentions (names dominate and both
  policies thread names identically by token overlap), and wrong pronoun links cost some precision.

So the marginal value of real coref over exact-match is LARGE for pronouns and MODEST for whole-document
entity tracking. The caveat travels: correct pronoun binding is a big capability on the mentions it
targets, but its document-level impact is diluted -- whether to prioritise it downstream depends on how
much pronoun-specific tracking matters to the reader. This is the honest "decisive either way" close.

## KEY REALIZATIONS

- **The corpus IS the instrument.** Choosing GAP (same-gender candidates) turned "does salience or
  meaning drive binding?" into a clean measurement, because it zeroes out the agreement filter by
  construction. The right corpus made the PINNED claim directly falsifiable.
- **Recency is at chance -- the organ's salience formula is backwards for binding.** The single most
  actionable correction, and it came from taking the brain literature seriously (Ariel) BEFORE tuning:
  the win is grammatical prominence, not the frequency+recency the organ defaults to.
- **A shared wall across salience cues means none of them was the second stage.** The plateau at the
  grammatical ceiling was the signal to build the prior x likelihood (IC/coherence), not to tune
  weights. Building it and getting a controlled NULL (doesn't replicate, doesn't beat scramble) is a
  real result: it localizes the residual as world knowledge, not a missing mechanism.
- **The scramble control caught a phantom.** On the tiny covered subset the raw IC delta looked
  positive; the mandatory lexicon-scramble twin (T2b lesson) and cross-split replication showed it was
  noise. Also caught and fixed a determinism bug (Python `hash()` tie-breaking) that made the boundary
  flicker.

## Proposed hdlab diff (NOT landed -- strategy re-verifies + lands, Q111)

In `hdlab/coreference_resolver.py` (and the `hdlab/state_of_mind` salience formula it imports):
1. **Replace the pronoun-branch salience score with ACT-R base-level activation**
   `B_i = ln(sum_k w_role(k) * dt_k^(-d))` (dt = sentence-distance; w_role = the existing role-prominence
   weights; d swept, ~1.5-2.0 on LitBank). This SUBSUMES and unifies the two things the old code did
   separately -- it folds grammatical prominence (via w_role, the GAP-winning cue) and recency+frequency
   (via the decay-weighted accumulation, the running-narrative-winning cue) into ONE scalar that is the
   brain's actual declarative-memory equation and wins in BOTH regimes. Validated: +0.213 over the live
   `count + beta*exp(-lambda*dist)` formula, +0.178 over pure recency, on 3654 held-out running-narrative
   pronoun resolutions. This is the single highest-value change and it is a drop-in replacement for the
   `salience()` method (same score-and-argmax architecture).
2. **Do NOT build an iterative settling / attractor mechanism for the antecedent PICK.** Refuted by three
   converging sources (Li et al. 2020, Chow/Lewis/Phillips 2014, on-disk LV05 HARD_FAIL). The pick is
   fast and one-shot; only the SCORE's form changes. (Settling's one possible use is a difficulty/
   confidence signal, which the existing top1-top2-margin abstention feature may already cover -- check
   before building.)
3. **Keep the agreement filter as a distinct, logged stage** even though it is a no-op on same-gender
   candidates -- log "0 eliminated by agreement" so a same-gender test never conflates "filter did
   nothing" with "filter broken."
4. **Do NOT add an implicit-causality / coherence likelihood term for binding** (measured null on GAP:
   ~15% coverage, doesn't replicate, doesn't beat its scramble). Reserve it for a corpus where
   Explanation/Cause-Effect relations are dense (narrative with connectives), not Wikipedia prose.
5. **Do NOT use content/cue-based retrieval as the pronoun pick** -- confirmed by the literature
   (Jaeger/Engelmann/Vasishth 2017: the interference signature is ABSENT for the antecedent-binding
   dependency type), which explains the on-disk HARD_FAIL (-0.1348). Content retrieval is for the
   PREDICTION channel, not binding.

Expected effect: the pronoun binder on running narrative goes from ~0.62 (live formula) to ~0.84
(ACT-R activation). On GAP same-gender snippets ACT-R reduces to the grammatical-prominence result
(~0.70) -- it will not exceed that there without world knowledge, but it no longer collapses on long text
the way either single cue does.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, coreference/binding entry)

- **Reference resolution is SALIENCE-driven; salience is an ACT-R base-level ACTIVATION scalar that
  unifies grammatical prominence + recency + frequency, and which component dominates is
  DISCOURSE-STRUCTURE-DEPENDENT (Competition Model):** grammatical role dominates on short 2-way
  same-gender snippets (GAP 0.674, recency inert); recency/accumulation dominates on long many-way
  running narrative (LitBank, role-alone collapses to 0.228). `B=ln(sum_k w_role(k)*dt_k^-d)` (ACT-R;
  Anderson; Lewis & Vasishth 2005) wins in BOTH regimes and beats the live organ's `count +
  beta*exp(-lambda*dist)` formula by +0.213 on running narrative. PINNED mechanism; d swept, not adopted.
- **Iterative SETTLING / attractor dynamics are REFUTED for the antecedent pick** (Li et al. 2020
  fMRI/MEG one-shot best-fit; Chow/Lewis/Phillips 2014; on-disk LV05 HARD_FAIL) -- the pick is fast and
  one-shot; only the activation SCORE's form is the lever. Standing design constraint.
- **The computation is Bayesian prior x likelihood (Kehler & Rohde 2013):** grammatical prominence =
  production likelihood `P(pron|ref)`; coherence/implicit-causality = next-mention prior `P(ref)`.
  PINNED at the computational level.
- **Implicit-causality / coherence as a glass-box likelihood term: TESTED, does not lift GAP** (~15%
  coverage, non-replicating, doesn't beat scramble). Not a binding lever on Wikipedia-style prose;
  reserve for connective-dense narrative. OUR-INVENTION-UNDER-TEST -> measured null.
- **LV05 cue-based activation for antecedent CHOICE: REFUTED** (Jaeger/Engelmann/Vasishth 2017 +
  on-disk -0.1348). Keep it for the PREDICTION channel only.
- **The brain's residual (hard same-gender) mechanism is itself an ACTIVATION/SALIENCE bias**
  (Dijksterhuis et al. 2024, Science: pronoun reinstates the more-activated hippocampal concept cell);
  the world-knowledge residual to human 96.6% is out of reach for a no-external-LLM glass-box substrate.
- New neuroscience anchors worth citing in the audit: Dijksterhuis et al. 2024 (hippocampal
  reinstatement), Nieuwland/Petersson/Van Berkum 2007 + Van Berkum et al. 2003 Nref (mPFC/ERP of
  referential ambiguity), Li et al. 2020 (ACT-R salience best explains neural signal for naturalistic
  pronouns). Full drills: notes/research_pronoun_anaphora_brain_computation_2026-08-27.md and
  notes/research_pronoun_residual_worldknowledge_brain_drill_2026-08-27.md and
  notes/research_ic_coherence_gap_pronoun_2026-08-27.md (written by the research helpers this session).

## What I did NOT establish / would withdraw first if wrong

- **The downstream test is coreference-CHAIN quality (B-cubed), not a grounded next-EVENT prediction.**
  I measured whether correct pronoun threading improves entity-TRACKING (chain reconstruction) over
  string-identity -- large on pronouns, modest whole-document (above). I did NOT measure whether it
  improves a grounded next-argument/next-event PREDICTION, because LitBank entities are non-groundable
  people (like GAP). Wiring the corrected binder into the situation-model prediction channel and
  measuring end-to-end grounded prediction is the natural follow-on (requires hdlab; strategy's).
- **First-mention's marginal value is weak** (+0.016, not CI-separated) -- I would withdraw the
  first-mention feature before the grammatical-role feature if forced; only role is CI-separated
  load-bearing.
- **The IC null is on GAP specifically** -- I would NOT generalize "implicit causality is useless for
  binding" to connective-dense narrative; the honest claim is "no lift on Wikipedia-style prose at ~15%
  coverage." A larger IC lexicon (Hartshorne 2013, 720 verbs) would raise coverage but not fix the
  scramble null (the limiter is that Explanation relations are rare here, not lexicon size).
- **spaCy grammatical-role labels are a stand-in** for the substrate's own incremental parser; the
  binder's accuracy inherits the parser's subject/object errors. A parse-error audit was not done.

## TLDR

The reader's "who does 'he/she' refer to?" step now has a real test: I put a modern, human-labeled
pronoun corpus (GAP, from Wikipedia) on disk and measured a brain-faithful salience resolver on it. It
works -- it picks the right person ~70% of the time, far above guessing (50%), above "just pick the
nearest name" (51%, which turns out to be no better than a coin flip), and a scrambled version of it
collapses to chance. The important discovery: the thing that makes it work is GRAMMATICAL PROMINENCE
(the subject of the sentence is the default "he"), NOT recency -- and the live reader's current default
formula leans on recency, which the brain literature and this measurement both say is the weakest cue.
So the concrete fix is to switch the pronoun step to prefer the grammatical-subject candidate. I then
tried to push past 70% the way the brain's harder cases work (implicit causality -- e.g. "blamed" points
at a different person than "feared"), using a published table of 305 verbs; it did not help on this
corpus and did not survive its own control, because those causal cues are rare in encyclopedia prose.
The remaining gap to human-level (96%) needs broad world knowledge that a glass-box system without a
big language model simply does not have -- and even the brain, on the hardest cases, mostly just leans
on whichever person it was already thinking about most.

Pushed further on brain-faithfulness (a fifth research drill), I found the *how* matters as much as the
*which*: the live reader scores "how salient is each character" with a formula that, provably, can never
let "mentioned more recently" out-vote "mentioned more often" -- backwards from how human memory works.
I replaced it with the brain's actual memory-strength equation (activation that fades with time and
builds with each mention, weighted by whether the mention was the subject), and tested it on full novel
excerpts (where the flaw can actually show up, unlike the short Wikipedia snippets). It jumps from 62%
to 84% -- a big, clean improvement -- and it also revealed that the "grammatical subject" clue that won
on the short snippets is nearly useless on long stories (where everyone has been the subject at some
point), while recency, useless on the short snippets, becomes the main clue. The one equation handles
both, which is exactly what makes it the right, brain-faithful mechanism rather than a corpus-specific
trick.

## QUESTIONS

None.

## NEXT STEPS

1. Land the diff: replace the pronoun-branch salience score with ACT-R base-level activation
   `B=ln(sum_k w_role(k)*dt_k^-d)` (drop-in for `salience()`; unifies grammatical prominence + recency +
   frequency; +0.213 over the live formula on running narrative). Do NOT build settling for the pick.
2. Wire the corrected binder into the running situation model and re-run the entity-PREDICTION channel
   to measure the downstream marginal value of correct pronoun linking end-to-end (the AND/OR bar's
   second task, which GAP snippets cannot support -- LitBank now provides the running-narrative substrate
   for it).
3. Do NOT pursue implicit-causality for binding on Wikipedia-style prose; if the coherence lever is
   revisited, test it on a connective-dense narrative corpus where Explanation relations are frequent.
4. Optional refinement (do not gate the build): the FHRR-native activation readout -- read each entity's
   activation as cosine-similarity to its bundled situation-model register rather than a hand-set role
   weight -- ties the ACT-R scalar to the substrate's own entity representation. Test only after the
   hand-set version lands (research note's Q4).

---

INTEGRATED_BY_STRATEGY: 2026-08-27 -- EXCELLENT / SOLVED (owner-DONE). Full SOLVED re-read FRESH (standing rule).
Re-verified scaffold-free FIRST-HAND (test_gap_pronoun_binding.py 6/6 PASS). A grammatical-prominence salience binder
resolves same-gender ambiguous pronouns at 0.6988 on GAP (n=1773 human-labeled), beating string-identity 0.5076 (+0.191),
recency 0.5144 (+0.184), and the info-free shuffled-salience twin (+0.1805), all CI-sep. STRIKING: on the HARD ambiguous
cases RECENCY IS AT CHANCE -- the binding cue is GRAMMATICAL PROMINENCE (Centering subject-preference), sharpening the
entity-tracking 'recency dominates' finding (recency correlated with prominence on easy cases only). Binding is
structural/salience NOT semantic (implicit-causality does not replicate + loses to scramble). Acquired 3 foundation
corpora (GAP, Ferstl IC norms, LitBank). ACT-R base-level activation B=ln(sum w_role*dt^-d) unifies prominence/recency/
frequency, beats the live salience() +0.213. hdlab landing EARNED -> QUEUED proven-ready (drop-in ACT-R base-level
activation for the pronoun-branch salience(); no settling for the pick). AUDIT UPDATE folded (§2b). SUCCESSOR packaged =
wire entity tracking (bind + predict) end-to-end on running narrative (LitBank). Review EXCELLENT + SOLVER REVIEW in
PROBLEM.md; priority cleared. Committed.
