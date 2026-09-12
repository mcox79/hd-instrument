# RESEARCH: harm/help appraisal, selectional preference, and POS-posterior math -- literature scan
Date: 2026-09-12. Method: direct WebSearch by the research role (no sub-agent fan-out, generic math
terms only, no substrate-novel config/mechanism names sent off-platform). Cross-checked against the
repo's own existing citations in hdlab/force_dynamics_typer.py, patient_tendency.py,
thematic_role_labeler.py, np_head_reduce.py before writing.

## HEADLINE
All three computations are real, field-documented phenomena at the BEHAVIORAL/COMPUTATIONAL-LEVEL;
none is PINNED at the neural-mechanism level for THIS exact composite equation. The biggest honest
gap: Resnik's (1996) class-based KL-divergence selectional-association formula is the WEAKEST of the
three -- the field has since shown (Bicknell et al. 2010; McRae/Ferretti/Amyote 1997) that human
thematic-fit expectation is joint/event-specific (agent+verb together predict the patient), which a
pairwise verb-class KL term structurally cannot represent. Items 1 and 3 are each composites of
well-supported PARTS that have never been tested together as one multiplicative equation in any paper
found. Item 4 is mostly a grammatical fact, not an open empirical question.

## (A) One-paragraph answer
Force dynamics (Talmy 1988; Wolff 2007) is the right descriptive frame for CAUSE/ENABLE/PREVENT and is
already the repo's landed basis (force_dynamics_typer.py, patient_tendency.py) -- status
COMPUTATIONAL-LEVEL with strong behavioral support, not neurally pinned as a force-vector
representation during READING (Wolff's own tests used animations, not text). Multiplying that by a
patient-valence term (Warriner et al. 2013 norms) and an affectedness/thematic-fit gate (Beavers 2011;
McRae-style graded fit, ERP-pinned via Bicknell et al. 2010) is a defensible novel SYNTHESIS of three
independently-supported pieces, each at a different evidence tier -- cap P(novel-synthesis) at 0.50 per
standing calibration rule. Resnik's (1996) selectional-association formula is a reasonable
COMPUTATIONAL-LEVEL approximation but is the one the field has most directly superseded: joint
agent-verb-specific expectation (Bicknell et al. 2010, N400-pinned) is the better-supported form, and
contextual surprisal (Levy 2008; Smith & Levy 2013) is the better-pinned general currency. A Bayesian
(multiplicative, not additive) combination of lexical-category prior and syntactic likelihood for
POS/DP-head disambiguation is well supported behaviorally (MacDonald, Pearlmutter & Seidenberg 1994;
Trueswell, Tanenhaus & Garnsey 1994; Jurafsky 1996; Gibson, Bergen & Piantadosi 2013) -- multiplicative
form specifically is favored over additive race/weighted-sum models by the interaction pattern in
garden-path data, though the neural mechanism that performs the "multiply" (candidate: divisive
normalization / gain modulation, Carandini & Heeger 2011) is itself only a computational-level
candidate, not imaged doing this specific job. Deterministic passive-voice detection (be/get-aux + past
participle) is mostly just grammar, not a contested hypothesis; the eADM (Bornkessel-Schlesewsky &
Schlesewsky 2009) predicts comprehenders use voice morphology EARLY for actor/undergoer assignment, but
the online process is graded/error-prone (reduced-relative garden paths), so "deterministic" describes
the correct STRUCTURAL rule, not the moment-by-moment human computation.

## (B) Per-item detail

### 1. HARM/HELP appraisal: force structure x patient valence x affectedness gate
**Equation (as specified):** Outcome = ForceType(agonist_tendency, antagonist_force, endstate_reached)
in {CAUSE, ENABLE, PREVENT}; Appraisal = Valence(outcome, patient) x AffectednessGate(verb, patient);
psych verbs (frighten/fear-class) excluded from the force computation.

**Status, by sub-claim:**
- Force-dynamic typing of CAUSE/ENABLE/PREVENT = COMPUTATIONAL-LEVEL, well-supported. Wolff's Vector
  Model (Wolff 2007, J. Exp. Psychol: Gen.; Wolff & Song 2003, Cognitive Psychology 47:276-332) showed
  participants' verb choice for 3D physics-engine animations (boat + wind + fan forces) tracks the
  force-vector algebra almost exactly. This is PINNED at the behavioral-linguistic level (verb choice
  = f(forces)), but NOT shown as a neural force-vector representation during comprehension -- no study
  found that images force vectors while people READ causal sentences (as opposed to watching physical
  scenes). Kuhnmuench & Beller (2005) note CAUSE-vs-ENABLE is partly linguistically (not purely
  physically) constructed, a real caveat already flagged in patient_tendency.py.
- Outcome valuation in OFC/amygdala = PINNED as the brain's general value-computation machinery (decades
  of primate/human work, e.g. Rolls; review: Emotion/OFC/amygdala literature surveyed 2023-2024) for
  experienced or directly observed outcomes. Applying it to "valuing a THIRD PARTY's outcome as narrated
  in text" is an ANALOGY/extension -- no study found that specifically tests OFC/amygdala valence coding
  against sentence-level harm/help narratives (vs. e.g. Warriner-type word-level valence norms, which are
  rating-based, not neuroimaging-based).
- Affectedness gate: Beavers (2011, NLLT 29:335-370) "On Affectedness" is a LINGUISTIC-THEORETIC
  two-dimensional scale (type x degree of change), not itself a behavioral/neural claim. McRae-style
  graded thematic fit IS behaviorally/ERP-pinned: Bicknell, Elman, Hare, Kutas & McRae (2010, JML
  63:489-505) showed N400 amplitude at the patient noun is modulated by agent+verb-specific typicality
  (mechanic checked brakes vs. journalist checked spelling) within ~200-600ms -- this is the strongest
  PINNED evidence in the whole composite.
- Psych-verb exclusion: grounded in Dowty's (1991, Language 67:547-619) Proto-Agent/Proto-Patient
  entailment clusters (volition, causation, sentience vs. change-of-state, causal affectedness) and the
  broader unaccusative-psych-predicate literature -- a well-established linguistic-theoretic carve-out,
  descriptively PINNED by consensus, not itself a new neural claim.

**What would be more brain-faithful:** (i) replace "OFC/amygdala valuation" framing with the weaker,
honest claim that Warriner-norm valence is a RATING-BASED proxy for that machinery, not direct evidence
of it firing during reading; (ii) get a direct ERP/fMRI test of force-vector representations using TEXT
stimuli (Wolff's own paradigm redone as sentences, not animations) before calling force-dynamics
"pinned for reading"; (iii) test the affectedness gate against Bicknell's joint-expectation paradigm
directly rather than Beavers' scale alone.

### 2. Typed selectional preference: Resnik (1996) class-based KL-divergence
**Equation:** A(v,c) = P(c|v) log(P(c|v)/P(c)) ; SPS(v) = sum_c A(v,c) (relative entropy of the
class-conditional distribution from the class prior), over WordNet-style semantic classes.

**Status: COMPUTATIONAL-LEVEL, weakly-to-moderately supported, and the most field-superseded of the
three.** Resnik (1996, Cognition 61:127-159) himself validated the measure against human plausibility
and disambiguation judgments -- real but modest support. Since then:
- McRae, Ferretti & Amyote (1997, Lang. & Cog. Proc. 12:137-176) showed thematic roles are VERB-SPECIFIC
  feature-based concepts (typicality ratings like "how common is it for a monster to frighten someone"),
  not class-level slot fillers -- already partly incompatible with a single class-based KL term per verb.
- Bicknell et al. (2010, above) is the decisive piece: patient-noun fit depends on the AGENT+VERB
  JOINTLY (same verb "checked," different expectation for mechanic vs. journalist) -- this is explicitly
  NOT decomposable into a pairwise verb-class association, which is exactly Resnik's formula's shape.
  That is a structural, not just quantitative, mismatch.
- Warren & Paczynski (2010/2011, Lang. Cogn. Neurosci. 26:1403-1434) found animacy-hierarchy violations
  drive a robust P600 largely independent of thematic-role-specific fit -- a coarser, earlier-acting
  signal than class-based selectional association, suggesting the brain's real computation is layered
  (coarse animacy gate + finer event-specific fit), not one flat KL term.
- Levy (2008, Cognition 106:1126-1177) and the broader surprisal literature (Hale 2001; Smith & Levy
  2013, Cognition 128:302-319, log-linear surprisal-reading-time fit) offer a more general, better
  reading-time-validated currency: processing cost as -log P(word | context). Selectional fit is more
  defensibly framed as ONE contributor to that surprisal than as a free-standing KL gate.

**More-pinned alternative:** joint, event/situation-specific expectation P(patient | agent, verb)
(Bicknell-style) fit by feature-overlap/exemplar methods, reported as a contribution to contextual
surprisal, rather than Resnik's per-verb class-KL divergence in isolation.

### 3. Bayesian lexical-category posterior at a DP-head
**Equation:** P(NOUN | word, DP-head) is proportional to LexicalPrior(NOUN | word) x
SyntacticLikelihood(DP-head-context | NOUN) -- a multiplicative (Bayesian) combination.

**Status: COMPUTATIONAL-LEVEL, well-supported behaviorally, multiplicative form specifically favored
over additive.** MacDonald, Pearlmutter & Seidenberg (1994, Psych. Rev. 101:676-703) showed lexical and
syntactic ambiguity are resolved by the SAME constraint-satisfaction mechanism (parallel activation,
weighted by frequency/context), not separate modules -- this is the behavioral backbone for treating
category choice as one weighted-evidence computation. Trueswell, Tanenhaus & Garnsey (1994, JML
33:285-318) showed thematic/semantic fit is used EARLY, during the ambiguity itself, not as late repair.
Jurafsky (1996, Cognitive Science) gave the actual Bayesian formalization -- an explicit prior x
likelihood probabilistic model of lexical/syntactic access that quantitatively matches garden-path
reading-time magnitudes, a direct precedent for the exact equation form requested. Gibson, Bergen &
Piantadosi (2013, PNAS 110:8051-8056) is the strongest direct pin for MULTIPLICATIVE Bayesian
integration specifically (noisy evidence x prior semantic expectation, tested against alternative
combination rules and behaviorally confirmed as rational/Bayesian, not ad hoc). Levy (2008) supplies the
general information-theoretic read-out (difficulty = -log P(word|context)) consistent with this family.
Multiplicative vs. additive: the field favors multiplicative/Bayesian because it reproduces the
super-additive interaction seen when two cues both point the SAME wrong way (stronger garden-path than
either cue predicts alone) -- an additive weighted-sum model under-predicts this interaction.

**Neural mechanism for "multiply" itself:** not directly imaged for this task. The standing
computational-level candidate in the broader cortex literature is divisive normalization / gain
modulation (Carandini & Heeger 2011, Nat. Rev. Neurosci.), which can implement near-multiplicative
combination of two input streams -- cite as the candidate mechanism, not as evidence FOR this specific
POS computation.

**More faithful:** directly test EEG/MEG decoding of a lexical-category posterior at the moment of a
DP-head ambiguity (e.g., "the fly/VERB-bias-but-NOUN-context" items) against the multiplicative
prediction vs. an additive weighted-sum baseline, rather than relying on aggregate reading-time fits.

### 4. Deterministic voice correction (be/get-aux + past participle = passive subject)
**Status: mostly a grammatical fact, not a contested empirical hypothesis -- ENGINEERING HEURISTIC
dressed as grammar, and that's fine, but don't claim it as a neural-pinning win.** The STRUCTURAL rule
(passive morphology demotes the logical object to surface subject) is definitional English grammar.
The eADM (Bornkessel-Schlesewsky & Schlesewsky 2009, Behav. Brain Sci. / their "extended Argument
Dependency Model" papers, 2006 Brain & Language review) predicts comprehenders use morphosyntactic voice
marking EARLY, as a fast low-level cue for actor/non-actor (undergoer) role assignment, organized around
actor-centrality -- so applying the rule early and with priority is consistent with what the model says
the brain does. But the actual online process is not error-free: the classic reduced-relative /
passive-participle garden path ("the horse raced past the barn fell"; MacDonald et al. 1994 discuss this
class directly) shows comprehenders can transiently MISparse participles, meaning the real-time human
computation is a graded, probabilistic-constraint process that EVENTUALLY lands on the deterministic
grammatical analysis, not a lookup that is deterministic at every millisecond. Net: keep the rule (it's
correct grammar, early-acting per eADM), but label it what it is -- a deterministic ENGINEERING encoding
of a PINNED grammatical fact, not itself a brain-mechanism finding.

## (C) What the literature does not settle
- No study found that tests force-vector representations (Wolff's model) using TEXT/reading stimuli
  rather than animated physical scenes -- the "reads during comprehension" extension is untested.
- No study found that directly measures OFC/amygdala (or any specific brain region) valuation signal
  while participants read third-party harm/help narratives matched for affectedness -- the item-1
  composite's neural-valuation leg is an analogy from decision-making/primary-reward work, not a reading
  study.
- No paper found that tests the EXACT three-way product (force-type x valence x affectedness-gate) as
  one multiplicative equation against human harm/help judgments -- each piece is separately supported,
  the SPECIFIC combination is this project's own novel synthesis (P capped at 0.50).
- The Resnik-vs-joint-event-expectation question is fairly well settled AGAINST Resnik's exact form for
  fine-grained fit, but it is not settled whether a COARSER class-based signal (Resnik-style) is still
  useful as a fast first-pass gate layered under a finer joint-expectation signal (Warren & Paczynski's
  animacy-first result hints at a layered architecture, but no paper directly tests Resnik-class-KL as
  that first layer).
- Whether the cortical "multiply" for category-posterior integration is literally divisive
  normalization, or some other mechanism, is open -- Carandini & Heeger (2011) is a plausible general
  candidate, not a tested answer for this specific computation.
- No paper found that quantifies how often eADM's "early voice-cue use" is overridden/garden-pathed at
  the RATE the substrate would need for a decisive falsification test; existing reduced-relative studies
  give qualitative, not the needed quantitative, error-rate baseline.

## Cross-thread synthesis (prior repo entries)
- hdlab/force_dynamics_typer.py and patient_tendency.py already cite Wolff & Song (2003) and
  Kuhnmuench & Beller (2005) and are marked PINNED for the CAUSE/ENABLE/PREVENT truth-table itself --
  this scan confirms that citation chain is sound and extends it (Wolff 2007 Vector Model behavioral
  match; Feng et al. 2021 ALE meta-analysis already in-repo is honestly scoped there as NOT
  dissociating CAUSE/ENABLE/PREVENT, consistent with this note's "not neurally pinned for reading" call).
- notes/research_pp_clausal_attachment_token_vs_type_2026-09-10.md already established, from a direct
  code read, that the repo's existing semantic-rescoring mechanisms are TYPE-level/averaged, and that
  Bicknell et al. (2010) + Metusalem et al. (2012) pin a real joint/non-pairwise event computation --
  this note independently arrives at the identical Bicknell-over-Resnik conclusion from the selectional-
  preference angle, which strengthens rather than duplicates that finding (same citation, two separate
  drill paths converging).
- notes/RESEARCH_one_semantic_hub_many_readouts_2026-09-11.md argues for ONE graded amodal-ish hub fed
  by multiple spokes; Warriner valence norms and McRae/Beavers-style feature ratings are exactly the
  kind of spoke-like graded input that note flags as hub-mergeable -- the harm/help appraisal gate
  should probably read FROM that same merged hub rather than being its own separate lookup table.

## Cheap decisive test (pre-registered)
Build a small discriminator set (20-30 items) of harm/help verb+patient pairs drawn from existing
gold (QA-SRL/GUM sentences already in the substrate's corpora) where (a) Beavers-affectedness-gate
value and (b) Warriner-valence sign DISAGREE in at least one direction (e.g., a low-affectedness but
high-negative-valence outcome, or vice versa). Score with: (i) the full multiplicative composite,
(ii) valence-only, (iii) affectedness-only, (iv) force-type-only. HARD-PASS: composite beats all three
single-term ablations on human-judgment agreement, CI-separated, on this disagreement subset (the
subset is specifically chosen to be uninformative to any single term alone). HARD-FAIL: composite ties
or loses to the single best term -- the multiplication is adding noise, not signal, and the gate should
revert to whichever single term wins.

## Falsifiable predictions
1. HARM/HELP composite: HARD-PASS if the 3-way product CI-beats each 1-term and each 2-term ablation on
   the disagreement subset above; HARD-FAIL if any 1-term ablation matches or beats the full product.
2. Selectional preference: HARD-PASS if a joint agent+verb expectation signal (Bicknell-style, even a
   crude co-occurrence proxy) CI-beats a Resnik-class-KL signal on a thematic-fit-violation detection
   task; HARD-FAIL if Resnik-class-KL matches or beats the joint signal (would mean the class-level
   simplification loses nothing here and the theoretically-motivated replacement isn't worth the cost).
3. POS posterior: HARD-PASS if multiplicative (prior x likelihood) combination CI-beats an additive
   (weighted-sum) combination specifically on items where BOTH cues point the same WRONG way (the
   interaction-diagnostic subset); HARD-FAIL if additive matches multiplicative there (would mean the
   super-additive prediction doesn't hold in this substrate's data and the simpler additive form should
   be kept).
4. Voice correction: not falsifiable as framed (it's a grammatical definition); the only testable claim
   is EARLY-AND-RELIABLE use -- HARD-PASS if treating voice as a hard deterministic cue never loses to a
   graded/probabilistic version of the same cue on held-out passive sentences; HARD-FAIL if any
   passive-participle-ambiguous sentence class (reduced-relative-style) is measurably present in the
   substrate's corpora and the deterministic rule mis-assigns it where a graded cue would not.

## Substrate-product implications
In plain terms: the three new calculations the team is about to build are each a reasonable combination
of well-studied pieces, but no scientist has ever tested the exact combined formula end-to-end -- each
piece alone has solid support, the COMBINATION is this project's own idea and should be graded as such
(capped confidence), not assumed proven by citing the parts. The clearest actionable fix without new
research: for "was the patient helped or harmed," replace the general brain-reward-circuit framing with
the plainer, better-evidenced claim -- word-level pleasant/unpleasant ratings plus how much the person
was actually changed by the event, multiplied by a well-tested force-direction signal already built into
the system. For "what nouns does this verb expect," the literature says move away from a single
per-verb-class score toward a score that also looks at WHO is doing the action, which other project
notes already independently recommended -- this is a second, independent confirmation, not a new idea.
For picking a word's part of speech near "the ___," the literature supports multiplying (not adding)
two pieces of evidence -- how common each reading of the word is, and how much the surrounding words
favor noun versus verb -- and specifically predicts it should do the most extra work exactly when both
pieces of evidence are misleading in the same direction.

## Citations (verified count: 19 distinct, dated works located via search; all have at least one
direct bibliographic confirmation from the search results above)
Talmy 1988; Wolff & Song 2003; Wolff 2007; Kuhnmuench & Beller 2005; Dowty 1991; Beavers 2011;
Warriner, Kuperman & Brysbaert 2013; McRae, Ferretti & Amyote 1997; Resnik 1996; Bicknell, Elman, Hare,
Kutas & McRae 2010; Warren & Paczynski 2010/2011; Metusalem et al. 2012 (cited via cross-thread note);
MacDonald, Pearlmutter & Seidenberg 1994; Trueswell, Tanenhaus & Garnsey 1994; Jurafsky 1996; Gibson,
Bergen & Piantadosi 2013; Levy 2008; Smith & Levy 2013; Bornkessel-Schlesewsky & Schlesewsky
2006/2009 (eADM); Carandini & Heeger 2011 (neural-mechanism candidate, not a direct pin).

P_deflated: item 1 (novel 3-way synthesis) = 0.45 (capped 0.50, minus 0.05 for zero direct tests of the
combined form). Item 2 (Resnik replacement) = 0.55 deflated from an undeflated ~0.75 (strong, convergent,
field-confirmed direction, but deflate per standing calibration rule since the fix itself is untested
in-substrate). Item 3 (multiplicative POS posterior) = 0.50 deflated from ~0.70 (well-pinned BEHAVIORAL
form, but the interaction-diagnostic test proposed here has not been run). Item 4 = not a P-estimate
target (grammatical fact, not a falsifiable novel claim).
