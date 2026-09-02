# Research: the neural/cognitive mechanism of pronoun-antecedent resolution — full fidelity audit against the DEV-supervised conditional-softmax cue-integrator

Date: 2026-09-02. Scope: comprehensive lit-scan (4 parallel Sonnet sub-agents, ~110 tool-calls, ~70 distinct
citations) answering the 7 questions verbatim, to extend and correct the "HOW THE IDEAL DIFFERS FROM THE BRAIN"
section already in `SOLVED.md` for this problem (7 deltas prototyped 2026-09-02, same day). This note does not
repeat that prototyping — it is the deep literature backing for the deltas, and it CORRECTS two of them.

**Comparison target (the prototype):** a supervised, DEV-trained conditional-softmax reranker over candidate
antecedents. Features: (a) recency/topicality (ACT-R-style decayed base-level activation), (b) lexical/content-
cohesion, (c) a coarse 12-dim distributional "grounded event" similarity, (d) exact predicate-identity match,
(e) pairwise confidence-margin interaction terms. Combination is mostly LINEAR (interaction terms are the only
nonlinearity and contribute little). Trained by conditional-MLE on GOLD antecedent labels. Runs FEED-FORWARD,
ONE-SHOT, argmax-commits per pronoun, no capacity-limited candidate pool, no explicit defer state (entropy is
read out post-hoc only).

## HEADLINE

**The single most consequential correction this drill makes: the existing prototype's biggest named gap
("supervised vs. self-supervised learning, DELTA 1") is real but its proposed fix (predict-and-update via the
N400) rests on a WEAKER evidence base than the prior note implied — the one direct test of exactly this
mechanism at the (easier) lexical level came back NEGATIVE (van Wonderen & Nieuwland 2023), and the flagship
result for fine-grained predictive pre-activation (DeLong et al. 2005) partially failed a large pre-registered
9-lab replication (Nieuwland et al. 2018, eLife) at precisely the mechanistically-loaded pre-nominal level.**
Second most consequential: Kehler & Rohde (2013), read in full text, explicitly REJECT flat weighted-cue
integration ("bag of cues") as the right computational shape for pronoun interpretation — not just "coherence
is an extra cue," but a specific architectural claim that production-likelihood cues (topicality/subjecthood)
and next-mention-prior cues (coherence relation) belong to two DIFFERENT, non-interchangeable Bayesian terms.
This reframes the prototype's flat linear blend as mis-shaped, not merely mis-weighted, and is a NEW,
architecturally-actionable delta (DELTA 8 below) that the existing SOLVED.md's delta list did not have.

## SOURCING DISCIPLINE
Every claim below is flagged **[FULL-TEXT]** (the sub-agent fetched and read the actual paper/PDF) or
**[ABSTRACT]** (search-engine snippet / publisher abstract page / secondary-source synthesis only — most
target journals are paywalled). Of ~70 distinct citations surfaced, **9 are FULL-TEXT-VERIFIED**: Kehler &
Rohde (2013) target article + reply, Chow/Lewis/Phillips (2014), Kazanina et al. (2007), Pablos et al. (2015),
Laurinavichyute et al. (2017), Grosz/Joshi/Weinstein (1995, partial), Kush/Johns/Van Dyke (2018), Brodbeck/
Gwilliams/Pylkkänen (2015). Everything else is ABSTRACT-level and should be treated as a weaker, directionally-
useful signal, not a citable number, until independently re-verified. Per the lit-scan calibration penalty: all
confidence language below is already deflated 0.15-0.25 from what the raw abstracts would suggest, and no
novel-synthesis claim in this note (the cross-thread reconciliations, e.g. DELTA 8) is asserted above P=0.50.

---

## Q1 — Weighted cue integration (Competition Model) vs. Bayesian generative (Kehler & Rohde) vs. other

**Mechanism.** [FULL-TEXT] Kehler & Rohde (2013, *Theoretical Linguistics* 39:1-37, target article + reply
"Aspects of a Theory of Pronoun Interpretation," same issue) is not a compromise between the two accounts — it
is an explicit argument AGAINST flat weighted-cue integration ("bag of cues" / SMASH-style models, which they
name-check as the Competition-Model-lineage approach, citing Stevenson/Nelson/Stenning 1995 and Arnold 2001).
Their model: P(referent | pronoun) ∝ P(pronoun | referent) × P(referent). The two terms are causally distinct:
- P(referent) — the coherence-driven **next-mention prior** — is set by which discourse-coherence relation
  (Explanation, Result, Occasion, Parallel...) the comprehender expects, and is active even with NO pronoun
  present (it is a property of the discourse, not of anaphora resolution per se).
- P(pronoun | referent) — the **production/form likelihood** — is set by Centering-style topicality/subjecthood
  (a SPEAKER's tendency to pronominalize a topical referent), independent of coherence semantics.
Quote (full text, verified): *"[Our model] stands in opposition to the sort of 'bag of cues' models often found
in the pronoun literature, which use a discriminative model (e.g., regression) to estimate P(referent | pronoun)
directly."* And: many apparent "cues" (grammatical role, parallelism, aspect) are explicitly called
"epiphenomenal" — their predictive power in a flat regression is a byproduct of correlation with ONE of the two
real terms, not because the mind computes and pools them as independent weighted evidence.

**Key citations.** Kehler & Rohde (2013) target + reply [FULL-TEXT]; Kehler & Rohde (2019), *Journal of
Pragmatics* 154:63-78, "Prominence and coherence in a Bayesian theory of pronoun interpretation" [ABSTRACT] —
extends the split, states interpretation biases (but not production biases) are pragmatically enrichable;
Rohde & Kehler (2014), *Language, Cognition and Neuroscience* 29(8):912-927 [ABSTRACT] — the archival production
study. Discriminating evidence [FULL-TEXT]: pronominalization RATE is driven by topicality/voice (e.g. active-
subject 62% vs. passive-subject 87% pronominalized — a large, purely structural swing) and is statistically FLAT
under semantic/implicit-causality manipulations that shift 20-40 points of INTERPRETATION bias (Fukumura & van
Gompel 2010 cited: 76% vs 74% production rate across IC-verb bias conditions that produce large interpretation
shifts). K&R explicitly test and reject Arnold's Expectancy Hypothesis (Arnold 2001/2010) — a weighted-
cue/accessibility account in the Competition-Model lineage — on exactly this dissociation.

**Effect direction.** Production rate tracks topicality/grammatical-role structure; interpretation bias tracks
coherence-relation/semantic content; the two are dissociable and NOT explained by one shared "accessibility"
scalar. Model fit: predicted vs. observed interpretation-bias correlation 0.81/0.59 predicted vs. 0.74/0.60
observed (active/passive) [FULL-TEXT].

**PROTOTYPE MUST THEREFORE:** stop pooling recency/topicality features with content-cohesion/event-similarity
features into one flat conditional-softmax as if they were interchangeable evidence for the same latent
variable. Split into two causally distinct stages — a next-mention PRIOR (coherence/event/predicate features,
active independent of whether a pronoun is even present) times a production-plausibility LIKELIHOOD term
(recency/topicality/grammatical-role, "how pronoun-worthy is this candidate"), combined multiplicatively.

---

## Q2 — How is cue weighting/validity LEARNED (self-supervised vs. gold-label supervision)?

**Mechanism, and the honest verdict.** [ABSTRACT throughout — no full text obtained for this cluster] The
theoretical pieces all exist separately: (i) discourse-level anticipatory ERP effects exist (Van Berkum et al.
2005, *J. Cognitive Neuroscience*, gender pre-activation from discourse content before the noun appears); (ii)
the Competition Model (Bates & MacWhinney 1989) claims cue validity = availability × reliability, acquired from
the INPUT DISTRIBUTION (frequency-driven), cross-linguistically confirmed for case/word-order/agreement cues
(not tested for pronoun-antecedent cues specifically); (iii) error-driven delta-rule connectionist models
reproduce human cue-weight profiles for OTHER cue systems (case marking, word order) — architecturally the
right learning rule, but not demonstrated for anaphora; (iv) developmentally, Arnold/Song & Fisher-line work
shows HIGH-reliability categorical cues (gender agreement) come online early/adult-like by age 3, while GRADED
cues (order-of-mention/discourse-prominence) lag well past preschool (Song & Fisher 2005 *JML* 52:29-57; 2007
*Lingua* 117:1959-1987; Arnold, Brown-Schmidt & Trueswell 2007) — an ordering CONSISTENT with reliability-driven
statistical acquisition but not proof of it (equally consistent with a maturational/computational-complexity
account). Individual differences in print exposure predict cue-use strategy, which is more direct (if still
correlational) support for an input-driven account.

**The crux, and the negative result the existing SOLVED.md's DELTA 1 did not have.** The one DIRECT test of
"does predictive strength rationally adapt to the historical rate of prediction error" — van Wonderen &
Nieuwland (2023), *J. Memory and Language* 132:104435, N≈200, pre-nominal-article ERP — found **NO evidence**
that predictive strength adapts to how often past predictions were disconfirmed ("inconsistent with the
rational adaptation hypothesis"). This is at the LEXICAL level, which should be the easiest case for this
mechanism to show up. Separately, the single biggest piece of evidence for fine-grained, N400-indexed
probabilistic pre-activation — DeLong, Urbach & Kutas (2005), *Nature Neuroscience* 8:1117-1121, graded N400 at
pre-nominal ARTICLES scaling with cloze probability — **partially failed** a large pre-registered 9-lab
replication (Nieuwland et al. 2018, *eLife* 7:e33468): the noun-level effect replicated, the more theoretically
load-bearing article-level pre-activation effect did NOT (contested by the original authors on baseline-
correction grounds, an active dispute).

**PROTOTYPE MUST THEREFORE:** treat "self-supervised, prediction-error-driven cue reweighting" as a real,
motivated, but NOT-YET-EMPIRICALLY-DEMONSTRATED hypothesis for reference resolution specifically — the
mechanism has a documented negative direct test at the easier lexical level. Do not claim closing this gap is
just an engineering exercise (wire predictive_reader + n400_coherence_monitor and it will work); pre-register
that this specific self-supervised design might ALSO show the null "no rational adaptation" pattern, and design
the eventual experiment to be able to detect that outcome, not just a positive one. This deflates the existing
SOLVED.md's framing of DELTA 1 as "the #1 fidelity gap to build across" from a confident engineering target to
a genuinely open, two-sided empirical question.

---

## Q3 — Feed-forward one-shot vs. recurrent/interactive settling; does a later cue revise an earlier commitment?

**Mechanism.** [FULL-TEXT] Chow, Lewis & Phillips (2014), *Frontiers in Psychology* 5:630 (PMC4073625) — five
reading experiments show a genuine TWO-PHASE temporal profile: structural/grammaticality constraints act
immediately (pronoun+1 region); feature-matching-but-structurally-illicit antecedents produce measurable
interference only ONE TO TWO WORDS LATER, and *only* when the initial grammatical search fails — i.e. a real,
temporally-staged SECOND search pass triggered by failure of the first. This is the most direct evidence found
of a later cue genuinely revising/extending an earlier resolution attempt, not merely re-weighting within one
computation. [FULL-TEXT] Kazanina, Lau, Lieberman, Yoshida & Phillips (2007), *JML* 56:384-409, and Pablos,
Doetjes, Ruijgrok & Cheng (2015), *Frontiers in Psychology* (PMC4627476) establish the **Active Search
Mechanism** for cataphora: on encountering a cataphoric pronoun, the parser predictively and immediately opens a
search for an antecedent at the next syntactically-licensed position (gated by Principle C — no search cost at
positions binding theory rules out); a later gender mismatch produces a real-time COST, not a costless silent
revision — i.e. predictive commitments are "sticky," resisted rather than freely overwritten.

**Does resolution feed back into a live entity representation that constrains the next pronoun?** [Mostly
ABSTRACT, mechanism partially FULL-TEXT via Grosz/Joshi/Weinstein 1995 centering formalism] Yes, on convergent
grounds: Centering Theory's Cf(Un)/Cb(Un) update is a literal read-modify-write loop — the ranked forward-
looking-center list computed AFTER resolving utterance Un's pronouns becomes the candidate set utterance Un+1's
pronouns are resolved against, and the CONTINUE/RETAIN/SHIFT transition (computed from that update) is itself
used as a preference signal for the next resolution. Gernsbacher's enhancement/suppression mechanism
(Gernsbacher, Hargreaves & Beeman 1989, *JML* 28:735-755; Gernsbacher 1989 *Cognition*) specifies the update is
ASYMMETRIC — resolving a pronoun ACTIVELY BOOSTS the resolved entity and ACTIVELY SUPPRESSES competitors (not
merely lets them passively decay), and pronouns trigger this more slowly/weakly than full repeated-name
anaphors. Laurinavichyute, Jäger, Akinina, Roß & Dragoy (2017), *Frontiers in Psychology* 8:965 [FULL-TEXT]
frame this within a general memory encoding/retrieval-interference architecture (cross-linguistic, Russian/
German) where what got encoded from one resolution episode measurably shapes retrieval on the next.

**Effect direction.** Structural constraints act first (~immediately); feature-matching interference from a
failed-search fallback appears 1-2 words later. Cataphoric antecedent search is predictive and immediate;
mismatch produces a processing cost, evidence of resistance to revision rather than free overwrite. Resolved
entities get an ACTIVE salience boost; competitors get an ACTIVE salience cut (not just "no boost").

**PROTOTYPE MUST THEREFORE:** (1) implement a genuine two-pass mechanism — an initial constrained pass, and a
SECOND pass over previously-excluded candidates triggered specifically by first-pass failure (not a single flat
scoring); (2) turn the "entity maintenance chain" from a passive history LOG into a read-modify-write ranked
salience state, updated asymmetrically (winner enhanced, losers actively suppressed, not merely un-boosted)
after every resolution, and feed that ranked state back as an input feature to the NEXT pronoun's softmax; (3)
for cataphora specifically (not currently handled at all — one-shot backward-only design), add a syntax-gated
predictive-search state that opens before the antecedent's identity is known and imposes a mismatch cost rather
than silently discarding a wrong early guess.

---

## Q4 — Linear-additive vs. multiplicative/nonlinear cue combination; super-additivity/deferral

**Mechanism, and an important correction.** [ABSTRACT-ONLY, and flagged accordingly] Parker, D. (2019),
*Cognitive Science* 43:e12715, "Cue Combinatorics in Memory Retrieval for Anaphora" — full text could not be
obtained (Wiley/ResearchGate/institutional repository all blocked this session); everything here is
abstract/summary-level. **Important scope correction to the existing SOLVED.md's framing:** Parker's paradigm is
**REFLEXIVE**-antecedent retrieval (binding-constrained, e.g. "herself"), not free-pronoun discourse-antecedent
choice — architecturally adjacent (same ACT-R-style cue-based retrieval family) but a narrower empirical
population than "he/she resolves to a prior character." The result itself is also more precisely a MISMATCH
super-additivity, not necessarily a MATCH super-additivity: single-feature mismatch (e.g. gender alone) produces
little/no interference cost; TWO simultaneous mismatches (e.g. gender AND animacy together) produce a
disproportionately LARGE cost — bigger than the (near-zero) sum of the two single-feature costs. This is still
a genuine nonlinearity/discontinuity signature (rules out additive combination), but the existing SOLVED.md's
phrasing ("full-cue-match favored more than a linear model predicts") describes the MATCH side of the same
coin, which is a plausible but not identically-demonstrated dual claim — flag this as needing full-text
confirmation before quoting an exact statistic, and note the sign/direction (penalty on joint mismatch vs.
bonus on joint match) matters for how the interaction term should be built.

**Interactive-activation / parallel-constraint mechanism.** [Background/secondary-source characterization, not
newly fetched] McClelland-style competitive-inhibition-plus-normalization architectures implement nonlinear
combination structurally: a candidate's *effective* weight depends on the current activation state of its
competitors (mutual inhibition + normalization = softmax-like sharpening), not on fixed per-cue coefficients —
mathematically kin to divisive normalization (Louie, Khaw & Glimcher 2013, *PNAS*, general decision-making
normalization; [ABSTRACT]). Whether this settling process is empirically distinguishable from a static one-shot
nonlinear function is NOT cleanly resolved for pronoun resolution specifically — the best empirical handle found
(Farmer, Cargill, Hindy, Dale & Spivey 2007, mouse-trajectory curvature toward a rejected competitor,
*Cognitive Science*, [ABSTRACT]) is from syntactic garden-path paradigms, not antecedent choice, and is itself
contested (aggregate curvature could arise from a MIXTURE of discrete ballistic trajectories rather than
single-trial continuous settling).

**Deferral/flat-posterior under conflict.** This sub-question came back the WEAKEST evidenced of the whole
scan — no clean pronoun-specific reading-time/ERP/choice-probability study explicitly reporting a
non-averaging conflict signature was found this session (a targeted follow-up on visual-world eye-tracking
under cue conflict — Kaiser, Brown-Schmidt — is recommended and NOT yet done).

**PROTOTYPE MUST THEREFORE:** replace the smooth cue-value × own-confidence interaction terms (currently weak
contributors) with an explicit discontinuity feature — "how many cues simultaneously disagree with this
candidate" (a step/threshold feature, ≥2-simultaneous-mismatch), which is the shape of nonlinearity the
(abstract-level) evidence actually supports, rather than assuming smooth multiplicative interaction throughout
the space; and make each candidate's softmax score depend on competitors' CURRENT evidence (proper competitive
normalization, recomputed as evidence accrues) rather than a one-shot final normalization over independently-
computed scores.

---

## Q5 — Similarity-based interference in pronoun retrieval; integration with cue weighting

**Mechanism.** [ABSTRACT for the formula; general ACT-R architecture] Lewis & Vasishth (2005), *Cognitive
Science* 29:375-419 — chunk activation A_i = B_i + Σ_k W_k·S_ki + noise; the associative strength S_ki from
cue k to chunk i is attenuated by that cue's "fan" (how many OTHER chunks it is also associated with):
S_ki = S − ln(fan_i) — a discrete, competitor-COUNT-dependent penalty baked into each candidate's OWN activation,
computed BEFORE any cross-candidate comparison. Retrieval choice then follows a Boltzmann/softmax rule over
activations, and latency follows T_i = F·e^(−A_i) — i.e. a race-to-threshold process with its own time course.

**Pronoun-specific evidence.** [ABSTRACT] Badecker & Straub (2002), *JEP:LMC* 28:748-769 — six self-paced
reading experiments: reading times at/after a pronoun are RELIABLY LONGER when a structurally-INACCESSIBLE
distractor shares gender with the pronoun, even though that distractor could never legally serve as antecedent
— structurally-irrelevant but feature-matching information intrudes. They also report a graded "multiple-match"
cost: RTs longer when BOTH the legal antecedent and the illegal distractor match gender than when only the legal
one does. [ABSTRACT] Sturt (2003), *JML* 48:542-562, reports a boundary condition/asymmetry: REFLEXIVES show NO
early intrusion from a gender-matching but structurally-illicit antecedent, while SUBJECT-VERB AGREEMENT does —
i.e. interference is not uniform across dependency types, and personal pronouns pattern with agreement (showing
intrusion), not with the shielded-early reflexive pattern (consistent with Nicol & Swinney 1989's classic
"structural constraints filter early" result for reflexives).

**Integration with cue weighting.** [ABSTRACT, reconstructed from the ACT-R formalism] The literature's own
answer is "both, at different stages, not either/or": (1) a DISCRETE fan-based penalty is subtracted inside each
candidate's own activation as a function of competitor count sharing that cue (explicit, not emergent); (2) the
FINAL choice among candidates is ALSO a normalized/competitive process (softmax over activations) that
mechanically depresses each candidate's probability as more non-negligible competitors exist, independent of
the fan term — a second, genuinely emergent layer. No study was found that cleanly decomposes how much of a
given human interference effect is attributable to each layer separately — this looks like an open modeling
question, not a settled decomposition.

**PROTOTYPE MUST THEREFORE:** because the reranker already uses a shared softmax denominator, it already has
HALF the brain's mechanism (emergent normalization-based interference) for free — the missing half is the
DISCRETE, cue-specific competitor-count penalty computed per-candidate BEFORE normalization (an explicit "how
many other live candidates also match cue k" feature, subtracted proportional to log(fan)), which is currently
absent since cues are computed per-candidate with no cross-candidate competitor-count term feeding the score.

---

## Q6 — Two-stage bonding/resolution (Garrod & Sanford) and the Nref defer/hold-both signature

**Mechanism.** [ABSTRACT] Sanford & Garrod (1989), *Language and Cognitive Processes* 4:235-262; Garrod &
Sanford (1994), in Gernsbacher (ed.) *Handbook of Psycholinguistics*; the key TIMING evidence is Garrod &
Terras (2000), *JML* 42:526-544 — eye-tracking directly separating the two mechanisms: lexical-semantic
"bonding" information dominates the EARLIEST fixations; broader discourse/situational "resolution" information
emerges only LATER in the eye-movement record. BONDING = fast, automatic, gender/number/case agreement +
salience/focus reactivation (roughly what the prototype's recency/topicality cues already are). RESOLUTION =
slow, effortful, knowledge-driven, invoked only when bonding under-determines a referent.

**The Nref effect.** [ABSTRACT] Originating paper: Van Berkum, Brown, Hagoort & Zwitserlood (2003),
*Psychophysiology* 40:235-248. Trigger: a pronoun/definite NP with TWO+ EQUALLY PLAUSIBLE antecedents already
established (vs. a matched unambiguous control). Signature: frontally-dominant, SUSTAINED (no clear peak,
distinguishing it from the centro-parietal-peaked N400) negativity, onset ~300-400ms, sustained ~500-2000ms.

**Is deferral driven by posterior flatness (graded), or all-or-none?** [ABSTRACT] Nieuwland & Van Berkum (2006),
*Brain Research* 1118:155-167 — the Nref is LARGER under weak contextual bias and SMALLER under strong
contextual bias, and its magnitude correlates with reading-span (working-memory) score — i.e. it scales with
how genuinely close the competing candidates are, not a binary ambiguous/unambiguous switch. This is the best
graded-deferral evidence found, though it manipulates bias STRENGTH as a proxy for evidence gap rather than a
fully parametric multi-level ambiguity sweep (no such sweep was found).

**Important caveat NOT in the existing SOLVED.md's DELTA 2.** There is a genuine, NOT-fully-settled interpretive
debate over what the Nref actually indexes: the standard reading (Van Berkum/Nieuwland) is deferral/hold-both;
but alternative readings in the literature include a general "integration cost" of under-specified reference
(not a distinct commitment-holding state) and a "discourse-updating" component that may be confusable with
ambiguity-driven deferral. [ABSTRACT, and this specific sub-question is the thinnest-evidenced in the whole
scan.] Eventual resolution: the negativity is reported to sometimes PERSIST for several hundred ms even after
later disambiguating information arrives, suggesting new information (not just more processing time on the same
cues) drives eventual commitment, but this was not cleanly isolated in any single study found.

**PROTOTYPE MUST THEREFORE:** keep entropy-based deferral (already present as a post-hoc readout, and already
independently validated within this problem's own prototyping — entropy AUC 0.796 for predicting the
integrator's own errors, per SOLVED.md) as the graded, evidence-gap-sensitive part — this is well-aligned with
Nieuwland & Van Berkum's graded finding. But do NOT over-claim the Nref as unambiguous "brain declines to
commit" ground truth when writing up the mechanism — the debate about integration-cost vs. genuine deferral
readings means the target signature itself is contested, which should soften any claim that matching the Nref
qualitatively "proves" brain-fidelity of a deferral mechanism.

---

## Q7 — What else is missing: working memory, attention, ATL hub, timing

**Working memory: focus-of-attention vs. cue-based retrieval, pronoun-specific.** [FULL-TEXT] Kush, Johns & Van
Dyke (2018), *JEP:LMC* 45:1234-1251 (PMC7133391) — full speed-accuracy-tradeoff decomposition, PRONOUN
resolution specifically vs. non-anaphoric controls: prominent (main-clause-subject) antecedents show BOTH higher
asymptotic accuracy (d′ diff 0.91, 95% CI [0.63,1.12], t=7.10, p<.001) AND a FASTER retrieval rate (B=−0.84,
t=2.54, p=.021) — and the speed effect is specific to pronoun/coreference trials, absent in non-anaphoric
controls. Crucially, the authors interpret this as favoring **cue-based retrieval with prominence as a heavily-
weighted retrieval cue in a single-step PARALLEL search**, explicitly arguing AGAINST literal single-item
focal-attention storage (maintaining a main-clause subject "in focus" across intervening clauses would violate
known attentional-capacity limits). This SUPERSEDES the older Foraker & McElree (2007) [ABSTRACT] finding
(prominence raised accuracy/asymptote only, not speed) with a newer, full-text-verified, pronoun-specific
correction: prominence affects BOTH speed and accuracy, via cue weight, not via a discrete attention-slot
architecture.

**Attention/salience as a distinct, graded, continuously-updated dimension.** [ABSTRACT] von Heusinger &
Schumacher (2019), *Lingua*, define discourse prominence as a RELATIONAL, multiply-determined ranking
(information structure + referring form + role + world knowledge), recomputed at every utterance — not a static
per-mention feature. Centering's Cb/Cf (Gordon, Grosz & Gilliom 1993, *Cognitive Science* 17:311-347, [ABSTRACT]
mechanism corroborated FULL-TEXT via Grosz/Joshi/Weinstein 1995) formalizes the same idea as an explicit
per-utterance attentional-state update.

**ATL semantic hub and entity individuation.** [ABSTRACT throughout] The hub-and-spoke PDP account (Rogers,
Lambon Ralph et al. 2004, *Psychological Review* 111:205-235; Patterson, Nestor & Rogers 2007, *Nat Rev
Neurosci* 8:976-987; Lambon Ralph et al. 2017, *Nat Rev Neurosci* 18:42-55) is a model of GENERIC category
semantics ("what is a dog"), NOT individuation ("which specific dog/character") — it does not by itself justify
using one shared representation type for both. A SEPARATE, more directly relevant literature exists: left ATL/
temporal pole for proper-NAME retrieval, right ATL for person-specific biographical knowledge (Semenza's work,
[ABSTRACT]); the anterior temporal face area (ATFA, near perirhinal cortex) shows repetition-suppression
selective to individual face IDENTITY, invariant across pose/lighting, and carries person-specific attributes in
its multivoxel pattern (PNAS 2007; Cerebral Cortex 2016, [ABSTRACT]); the broader AT/PM framework (Ranganath &
Ritchey 2012, *Nat Rev Neurosci* 13:713-726, [ABSTRACT]) assigns perirhinal cortex to individual-ITEM encoding
and hippocampus to associative/contextual binding, with hippocampal involvement specifically demonstrated for
person/place-SPECIFIC semantic knowledge beyond generic category knowledge (J. Neurosci 2021, [ABSTRACT]).

**Timing: incremental, word-by-word commitment.** [FULL-TEXT] Brodbeck, Gwilliams & Pylkkänen (2015), *Frontiers
in Psychology* 6:1787 — MEG evidence of a lateralized negativity as early as ~333-379ms (adjectives) and
~383-454ms (nouns) post-word-onset during reference resolution, converging with the Nref literature's ~300-400ms
window. Resolution is computed essentially WORD-BY-WORD, within a few hundred ms of the referring expression, not
deferred to clause/sentence/document boundaries.

**Other findings.** Individual-differences: Just & Carpenter (1992) capacity theory [ABSTRACT] — lower-span
readers show more interference susceptibility; treat as a tunable-parameter design note, not a core mechanism.
Binding format (synchrony vs. conjunctive/distributed coding) is theoretically unresolved [ABSTRACT] but leans
toward supporting a distributed/superposed vector code for entity individuation (compatible with, does not force
abandoning, a vector-based design — but argues the vector should be built for CONJUNCTIVE individuation, not
stay a fixed low-dimensional category-semantics summary). The situation model tracks protagonist identity as ONE
of five obligatorily-monitored dimensions alongside time/space/causality/intentionality (Zwaan, Langston &
Graesser 1995, *Psychological Science*; Zwaan & Radvansky 1998, [ABSTRACT]) — "which character" resolution is
naturally one output of a shared multi-dimensional situation-model state, not an isolated task.

**PROTOTYPE MUST THEREFORE:** (1) do NOT build a discrete 1-item "focus slot" architecture — the newer,
full-text-verified pronoun-specific evidence favors a SINGLE continuous cue-weighted parallel search where
prominence is simply the most heavily-weighted cue (closer to what the softmax already does structurally; the
gap is weighting, not architecture); (2) add an explicit, separately-updated discourse-prominence/salience state
(Centering-style, recomputed every clause) distinct from raw recency-decay; (3) give each discourse entity a
SEPARATE, persistent individuation code (accumulating discourse-specific, person-identifying facts) distinct
from the shared category-semantics vector — the current 12-dim "grounded" vector is doing double duty it is not
neuroanatomically motivated to do; (4) move from batch/end-of-context scoring toward incremental, word-by-word
resolution commitment (~300-450ms after the pronoun in the brain) with a running ambiguity/commitment state.

---

## Cross-thread synthesis — how this extends and CORRECTS the existing SOLVED.md deltas

The prototype's own SOLVED.md (`notes/problems/who_has_what_needs_a_coherence_next_mention_prior_kehler_rohde/
SOLVED.md`, filed same day) already names 7 fidelity deltas. This drill:

- **CONFIRMS + SHARPENS Delta 3 (feed-forward vs. recurrent):** Chow/Lewis/Phillips 2014 gives full-text
  evidence for a genuine two-pass revision mechanism, not just "a settling loop would be nice"; Centering's
  Cf/Cb gives the exact read-modify-write update rule (asymmetric enhance-winner/suppress-losers, per
  Gernsbacher), sharper than "wire the integrator into the recurrent maintenance loop."
- **CORRECTS Delta 4 (linear vs. multiplicative):** Parker (2019) is about REFLEXIVE mismatch super-additivity,
  not confirmed (only abstract-level) to be about pronoun match super-additivity as the existing note implies —
  flag before building the exact interaction-term sign.
- **TEMPERS Delta 1 (supervised vs. self-supervised), the biggest correction:** the existing note calls this
  "the #1 fidelity gap to build across" as though it just needs wiring; this drill surfaces a DIRECT negative
  test (van Wonderen & Nieuwland 2023) of the exact "predict, then reweight on error" mechanism at the easier
  lexical level, plus a partial replication failure of the flagship supporting result (Nieuwland et al. 2018
  eLife vs. DeLong et al. 2005). Recommend downgrading this from "build it, it's known to work" to "build it as
  a genuinely open empirical test, with a pre-registered null hypothesis in play."
- **TEMPERS Delta 2 (commit vs. defer):** confirms graded/uncertainty-sensitive deferral (Nieuwland & Van Berkum
  2006, contextual-bias-strength scaling) but surfaces the unresolved Nref interpretive debate (deferral vs.
  integration cost) that the existing note did not carry — soften any claim that matching Nref "proves"
  brain-faithful deferral.
- **SHARPENS Delta 6 (coarse cue set / representation):** gives a specific neuroanatomical target — a separate
  perirhinal/ATL-style individuation code, not a denser version of the existing category-semantics vector.
- **SHARPENS Delta 7 (no similarity-based interference):** gives the exact mechanism split (discrete fan
  penalty pre-normalization + emergent softmax normalization) and the pronoun-specific citation (Badecker &
  Straub 2002) the existing note lacked.
- **NEW Delta 8 (architecture shape, not just weighting):** Kehler & Rohde explicitly reject flat bag-of-cues
  integration; the prototype's single flat softmax over 5 pooled feature types is the wrong SHAPE, independent
  of how well its weights are learned. This is arguably higher-leverage than any single feature/nonlinearity
  fix, because it is a restructuring, not an addition.
- **NEW Delta 9 (real-time incrementality):** the brain commits within ~300-450ms per referring expression
  (Brodbeck et al. 2015, full-text); the prototype scores once per pronoun with full context already assembled
  and no running commitment/ambiguity state across the document.

## Cheap decisive test

Before any architectural rebuild: re-score the EXISTING held-out struct-dominated bucket (n=695, from the
parent's harness) with the SAME learned features, but (a) split into the two-stage form — likelihood
(recency+topicality) × prior (content+grounded+predicate) instead of one flat softmax over all five — and (b)
add ONE discrete feature: count of OTHER live candidates matching the top-1 candidate's strongest single cue
(a crude fan/competitor-count proxy). If DELTA 8 (architecture shape) is the real lever, the two-stage
restructuring alone should beat the existing flat-linear result (0.6682) CI-separated, with a shuffled-stage
twin (recombine likelihood/prior from mismatched items) losing. If DELTA 9's fan-penalty is real, adding the
competitor-count feature should recover some of Badecker & Straub's "multiple-match" cost pattern (items with
2+ same-gender competitors should show a bigger score gap between the linear and two-stage+fan models than
items with 0-1 competitors).

## Falsifiable predictions

**HARD-PASS** (any one is sufficient to justify the rebuild): the two-stage likelihood×prior restructuring
beats the current flat-linear integrator (0.6682, [0.0077,0.1100] CI-sep floor-relative) by a further CI-
separated margin on the SAME held-out struct-dominated bucket, with a shuffled-stage twin losing; OR the
fan/competitor-count feature shows a CI-separated interaction (bigger benefit on 2+-competitor items than
0-1-competitor items), replicating Badecker & Straub's graded multiple-match signature in the substrate's own
data.

**HARD-FAIL** (either establishes the correction is not worth the engineering cost here): the two-stage
restructuring is NOT CI-separated from the flat-linear baseline (i.e., K&R's architectural claim, real in
humans, does not transfer to this feature set/population — plausible if the features already collinearly
encode the split, which the learned betas in SOLVED.md hint at: net/recency dominates at 1.63 vs content 0.69);
OR the fan/competitor-count feature shows NO interaction with competitor count (i.e., this population's
struct-dominated bucket does not have enough same-gender competitor variance to express interference, which the
residual anatomy in SOLVED.md — ~6 gendered competitors on average, 89.5% have 2+ — suggests is UNLIKELY, making
a null here more diagnostic than a floor effect).

## Substrate-product implications

For the reading/coreference product: the two highest-leverage, lowest-cost next builds are (1) the two-stage
likelihood-times-prior restructuring (an architecture change to existing wired features, not new representation
work — cheap, testable this week against the existing held-out bucket) and (2) the discrete fan/competitor-count
feature (one new engineered feature from data already on hand — the animacy-filtered candidate pool). Both are
composable with the already-landed `phi_agreement_keep` + `situation_model_accumulate` wire. The two BIG,
expensive items this drill surfaces — a genuine two-pass revision mechanism with a live salience state, and a
separate per-entity individuation code distinct from category-semantics — are exactly the priority-1 North
Star's remit (the generative world-knowledge situation model) and should NOT be built standalone here; this note
gives that organ two additional, specific, neuroanatomically-grounded design constraints (asymmetric
enhance/suppress salience update; ATL/perirhinal-style individuation code) to carry forward. The self-supervised
learning question (Delta 1) should be down-ranked in urgency given the negative direct test found — it is a
genuine open research question, not a known-good target to build toward immediately.

## Citations (verified count)

~70 distinct citations surfaced across the 4 sub-agent scans. **9 FULL-TEXT-VERIFIED**: Kehler & Rohde (2013,
target + reply, *Theoretical Linguistics*); Chow, Lewis & Phillips (2014, *Frontiers in Psychology*); Kazanina
et al. (2007, *JML*); Pablos et al. (2015, *Frontiers in Psychology*); Laurinavichyute et al. (2017, *Frontiers
in Psychology*); Grosz, Joshi & Weinstein (1995, mechanism partially verified); Kush, Johns & Van Dyke (2018,
*JEP:LMC*); Brodbeck, Gwilliams & Pylkkänen (2015, *Frontiers in Psychology*). Remaining ~60 are ABSTRACT-ONLY
or secondary-source-synthesized (paywalled full texts) — every empirical number quoted above from this set is
individually flagged [ABSTRACT] and should be independently re-verified before being used to set a numeric
target. Full per-question source lists are preserved in the 4 sub-agent transcripts (session-local; not
persisted separately — the citations above are the complete extraction).

---

## TLDR (plain language)

We asked four researchers to independently dig into how real brains figure out who "he" or "she" means, to
compare against the reranker we already built and tested today. Two findings matter most. First: the biggest
gap we already knew about — our system is taught the right answer during training, but a real brain has to
figure out cue reliability on its own from everyday reading — turns out to be a genuinely open scientific
question, not a solved recipe we can just wire up; the one direct experiment testing whether the brain
re-calibrates itself from its own prediction mistakes came back with no evidence for it, even in the easiest
case researchers have tried. So we should treat that fix as a real experiment to run, not a known-good
upgrade to install. Second, and newly found today: the leading scientific model of how people interpret
pronouns explicitly argues that mixing every clue (who was just mentioned, who fits the sentence's meaning,
whose turn it "should" be) into one blended score is the WRONG shape — the brain keeps two genuinely separate
questions (who's likely to be talked about next, and how likely is a given character to become "he/she" at
all) and multiplies them, rather than averaging everything together. That is a free, cheap restructuring we can
test on data we already have this week, before touching anything expensive. The other real findings — the
brain revises an early guess when a later clue disagrees, keeps an active "spotlight" on the current character
that gets boosted when confirmed and dimmed for rivals, gets confused by similar-sounding rival characters in a
specific measurable way, and needs a way to tell two similar characters apart that is different from just
knowing what a word means in general — are all real, useful design targets, but belong to the bigger
"understand the world from reading" project already queued as this program's top priority, not to be
rebuilt piecemeal here.

## QUESTIONS
None — this was a literature drill, not a build; open empirical questions are named above (Delta 1, Delta 4's
match-vs-mismatch sign, the deferral-vs-integration-cost debate) rather than questions for the reader.

## NEXT STEPS
1. (Solver) Run the "cheap decisive test" above — two-stage likelihood×prior restructuring + one fan/competitor-
   count feature — on the existing held-out struct-dominated bucket before any bigger rebuild; both are cheap,
   reuse existing wired features, and directly test this drill's two highest-leverage NEW findings (Delta 8, 9).
2. (Solver) Fold DELTA 8 and DELTA 9 into the SOLVED.md's delta list, and add the Delta-1 and Delta-4 caveats
   from this note (temper "self-supervised learning is the known fix"; correct Parker 2019's scope/sign).
3. (Priority-1 organ) Carry forward two specific design constraints for the generative situation model: (a) an
   asymmetric enhance-winner/suppress-losers salience update (not passive decay) on every entity mention; (b) a
   separate, persistent per-entity individuation code (ATL/perirhinal-style), distinct from the shared
   category-semantics channel.
4. (Follow-up drill, not done here) Targeted lit-scan for visual-world eye-tracking under parametric cue
   conflict (Kaiser, Brown-Schmidt) to close the still-open "flat/deferred posterior under conflict" question
   (Q4's weakest-evidenced sub-part); and an attempt to obtain full text of Parker (2019) before committing to
   an exact interaction-term design.
