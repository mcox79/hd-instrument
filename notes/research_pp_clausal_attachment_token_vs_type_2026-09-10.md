---
topic: PP-attachment / clausal-attachment residual (content-UAS 0.54 vs supervised 0.77) -- is there a TOKEN/EVENT-level lever the prior TYPE-level negatives did not test, or is the ceiling PINNED (text lacks the signal)?
requested_by: Director, 2026-09-10 -- direct literature+reasoning drill, no sub-agent fan-out (self-read)
date: 2026-09-10
calibration: lit-scan calibration penalty applied (deflate 0.15-0.25; novel-synthesis capped P<=0.50)
prior_threads_checked: notes/problems/the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse/SOLVED.md (the original x4 semantic-rescoring refutation: DMV valence, GEK, thematic-fit type expectation, coarse supersense coherence, world-model rescoring on uncertain arcs -- ALL twin-controlled, ALL HURT or null); notes/problems/scale_the_reading_learned_arc_scorer_the_brain_foundational_parser_acquisition/SOLVED.md (content-UAS 0.5444 vs supervised 0.7677; lexical PPMI -0.151, distributed embedding affinity best-weight=0; per-relation table: nmod/obl 0.18-0.57, advcl/acl/xcomp/ccomp 0.01-0.12); notes/problems/type_generalized_selectional_preference_densifies_coverage_but_the_who_affected_wall_is_ambiguity/SOLVED.md (Resnik type-generalized selectional preference: densifies coverage 40%->85% but does NOT beat the syntax floor on the full hard set -- only helps net-positive under a margin gate on the clean-signal subset, +0.07 to +0.156); notes/research_register_general_argument_attachment_mechanism_2026-09-04.md (categorical valency + closed-class scaffold as the register-invariant backbone; frequency/semantic tie-break is a documented MINORITY contributor, McRae et al. 1998 weights ~0.51/0.37/0.12); notes/problems/the_parser_is_a_frozen_supervised_hard_decode_not_the_brains_graded_probabilistic_parse/RESEARCH_bf_acquisition.md (field-level 40-65% unsupervised dependency-accuracy ceiling, Klein & Manning 2004; Yedetore et al. 2023 poverty-of-stimulus). Read GEK source (hdlab/generalized_event_knowledge.py) directly -- confirmed it is a bag-of-lemma DIRECTED FORWARD PPMI store (type-level, marginal, corpus-frozen), not a joint agent+verb-conditioned event model.
---

# Research: is PP/clausal attachment's residual a token-level lever or a pinned text-only ceiling?

## HEADLINE

**The four already-refuted "semantic rescoring" mechanisms (GEK, thematic-fit type expectation, coarse supersense
coherence, world-model rescoring) are ALL, verifiably on inspection of the actual code, TYPE-level / marginal /
pairwise-association computations -- none of them implement the joint agent+verb-conditioned event computation that
Bicknell, Elman, Hare, McRae & Kutas (2010, *J. Memory & Language* 63:489-505) and Metusalem, Kutas, Urbach, Hare,
McRae & Elman (2012, *J. Memory & Language* 66:545-567) show is a REAL, independently-documented, non-pairwise-
decomposable computation in human sentence processing (Metusalem's norming explicitly rules out pairwise word
association as the explanation for their effect). So the type/token distinction is real and under-tested. BUT the
honest, calibrated answer is a DECOMPOSED one, not a single lever: (a) the cheapest, most field-precedented,
genuinely-untried retry is not "go token-level" but "use the RIGHT type-level statistic at the RIGHT grain, scoped
and margin-gated" -- Hindle & Rooth's (1993, *Computational Linguistics* 19:103-120) preposition-specific
verb-vs-noun association reaches ~80% on the classic PP-attachment task (near the 88.2% human ceiling, Ratnaparkhi,
Reynar & Roukos 1994, HLT), and the substrate never built that exact statistic -- it built a domain-mismatched
(ROCStories-trained) generic bag-of-lemma association and a coarse 26-way supersense class fit instead; (b) a
genuine joint/event-conditioned (token-level) mechanism has real theoretical headroom per Bicknell/Metusalem but
ZERO field precedent showing it moves PP-attachment ACCURACY specifically (its evidence base is plausibility
ratings / N400, not parsing benchmarks) -- rank it second, prototype cheap, expect a small, uncertain yield; (c) the
catastrophic clausal-attachment residual (advcl/acl/xcomp/ccomp recall 0.01-0.12) is a bigger prize than PP-
attachment and is NOT primarily a selectional-knowledge problem at all -- Altmann & Steedman's (1988, *Cognition*
30:191-238) referential-context theory and the discourse-entity tracking it requires is TEXT-REACHABLE (the
substrate's own named "generative situation model"); (d) prosodic phrase-boundary cues (Kjelgaard & Speer 1999,
*J. Memory & Language* 40:153-194; Snedeker & Trueswell 2003, *J. Memory & Language* 48:103-130) are genuinely,
provably PINNED-ABSENT from text -- and Snedeker & Trueswell's own finding that speakers deploy prosody exactly
when referential context alone leaves the ambiguity unresolved means prosody's contribution is concentrated
precisely in the hardest residual cases, bounding how far even a perfect token-level + discourse model can go.

## Part 1 -- event/token-level selectional preference: brain structure, math, reachability

**Brain structure:** the anterior temporal lobe (ATL) hub-and-spoke model (Lambon Ralph, Jefferies, Patterson &
Rogers 2017, *Nature Reviews Neuroscience* 18:42-55; Patterson, Nestor & Rogers 2007, *Nature Reviews Neuroscience*
8:976-987) -- a bilateral ATL "hub" combines modality-specific "spoke" features (agent, verb, patient, instrument)
into one heteromodal event/situation representation, not a lookup table keyed by any single word. The
online-integration signature is the N400: Kutas & Federmeier (2011, *Annu. Rev. Psychol.* 62:621-647) review N400
amplitude as indexing ease of semantic integration into the running message-level representation; Rabovsky, Hansen
& McClelland (2018, *Nature Human Behaviour* 2:693-705) give the most direct computational-level model -- their
Sentence Gestalt connectionist network's hidden-state UPDATE magnitude on each incoming word (an implicit,
continuously-computed semantic prediction error over the whole developing event representation, not a per-word
surprisal) tracks N400 amplitude across 16 published experimental paradigms. This is the best current mechanistic
account of "attachment-via-event-expectation": the PP's object is evaluated against the ALREADY-INTEGRATED
event-gestalt (verb + already-bound arguments), not against the verb or the noun in isolation.

**The decisive empirical result (why this is a REAL token/event-level computation, not relabeled type-level):**
Bicknell et al. (2010) crossed agent x verb x patient ("the mechanic checked the brakes/spelling" vs "the
journalist checked the brakes/spelling") and found congruent combinations produce faster reading times and reduced
N400 AT THE PATIENT NOUN ITSELF, immediately -- and their own norming study explicitly ruled out any account built
from direct pairwise agent-patient or verb-patient association. Formally: the plausibility of a candidate PP
attachment site's filler cannot be decomposed as g(verb, filler) + h(other-head, filler) -- it requires a genuine
three-way interaction term P(filler | agent, verb) that is NOT recoverable from the marginals P(filler|verb) and
P(filler|agent) alone. Metusalem et al. (2012) independently confirm generalized event knowledge activates words
related to the OVERALL DESCRIBED EVENT even controlling for the word's individual association with every word in
the preceding context -- ruling out "it's just a bigger pairwise-association table" as an explanation.

**Is this what the refuted mechanisms tested?** No -- confirmed by reading `hdlab/generalized_event_knowledge.py`
directly this session: `GEKProjector.score()` computes a directed forward PPMI over a frozen bag-of-content-lemma
transition table built once from ROCStories (a 98k-story, 5-sentence-per-story corpus, domain-mismatched to
UD-EWT/GUM) -- i.e. `score = mean_i PPMI(ctx_lemma_i -> ending_lemma)`, a pairwise/marginal computation with NO
joint agent+verb conditioning term, evaluated on a domain-shifted corpus. The Resnik-style "thematic-fit type
expectation" and "coarse supersense coherence" mechanisms (from the sibling `type_generalized_selectional_
preference...` SOLVED.md) are `A(v,c) = P(c|v) log(P(c|v)/P(c)) / SPS(v)` -- a verb-class marginal, also with no
joint-argument conditioning. So: **the type/token distinction is real, documented independently in the
psycholinguistic literature, and genuinely untested in-repo** -- but see the honest counter-evidence below.

**Reachability:** YES, in principle, from a text corpus alone -- Bicknell/Metusalem's effect is measured from
reading plain sentences; no embodiment or prosody is required to LEARN the joint agent-verb-patient association,
only enough co-occurring (agent, verb, patient/instrument) triples read from text. The substrate's own reading-grown
directional-context channel (`reading_grounding_loop.py`) already accumulates typed co-occurrence and could in
principle be extended to a 3-slot joint count (or a low-rank/HD-bound joint representation) rather than 2-slot
pairwise counts -- a concrete, buildable extension, not a new organ class.

**Honest counter-evidence (why P should be deflated, not just capped):** the refuted "world-model rescoring on
uncertain arcs" mechanism (per the parent SOLVED.md's DO-NOT-REDO list) was ALREADY scoped to uncertain/ambiguous
arcs specifically -- i.e., a margin/ambiguity gate was already tried for at least one of the four mechanisms, and it
still did not help. This means the type/token grain is not the ONLY plausible explanation for the negative results;
domain mismatch (ROCStories vs UD-EWT/GUM) and under-tuned gating are live alternative explanations that a cheap
ablation should rule out BEFORE committing to building a new joint-conditioning mechanism. P(a token/event-
conditioned re-test of PP-attachment specifically beats the structural floor CI-separated): **0.30** (deflated;
theoretically well-supported by Bicknell/Metusalem but zero direct field precedent for moving a PP-attachment
accuracy number, only plausibility/N400 measures).

## Part 2 -- psycholinguistic evidence: structural defaults vs constraint-based lexicalism vs referential context vs prosody

- **Frazier (1978; Frazier & Fodor 1978, *Cognition* 6:291-325) minimal attachment / late closure:** a fast,
  syntax-only STRUCTURAL DEFAULT (attach with fewest nodes; attach low/local) fires before lexical-semantic
  information is available -- Frazier & Clifton's (1996, *Construal*, MIT Press) later revision restricts strict
  structural-first processing to a verb's PRIMARY (subcategorized) relations; adjuncts (most PP-attachment and
  clausal-attachment cases) are only loosely associated and resolved later, non-structurally. **This matches
  in-repo evidence exactly:** the reading-learned scorer's POS-category+valence signal (the closest thing it has to
  a structural default) is what carries parity-class relations (aux/mark/det/amod), while nmod/obl/advcl/acl are
  precisely the non-primary, adjunct-class relations Frazier & Clifton predict would NOT be resolved by structure
  alone.
- **MacDonald, Pearlmutter & Seidenberg (1994, *Psychological Review* 101:676-703) constraint-based lexicalism /
  Trueswell, Tanenhaus & Kello (1993, *JEP:LMC* 19:528-553):** ambiguity resolution is graded, parallel, lexically-
  driven (verb-specific subcategorization frequency, immediately available). McRae, Spivey-Knowlton & Tanenhaus
  (1998, *J. Memory & Language* 38:283-312) supply the ONE fully-quantified weighting scheme in this literature:
  fitted weights split main-clause-bias-prior ~0.51, thematic-fit-plausibility ~0.37, item-specific lexical
  frequency ~0.12 (normalized-recurrence competition-integration network) for one ambiguity type -- i.e. even where
  a frequency/semantic effect is real and measurable, it is the MINORITY contributor next to a structural/frequency
  PRIOR. This directly predicts that bolting semantic rescoring onto an arc-factored scorer that already encodes
  the structural prior should yield only a SMALL, easily-swamped-by-noise gain -- consistent with the in-repo HURT
  results if the added statistic was noisier than the ~0.37-weight signal it was trying to add.
- **Altmann & Steedman (1988, *Cognition* 30:191-238) referential theory:** attachment preference is NOT fixed by
  structure or lexical bias alone -- it flips based on the REFERENTIAL CONTEXT already established in discourse
  (how many candidate referents a modifying phrase could restrict among). Spivey & Tanenhaus (1998, *JEP:HPP*
  24:1521-1543) and the visual-world eyetracking program (Tanenhaus, Spivey-Knowlton, Eberhard & Sedivy 1995,
  *Science* 268:1632-1634) confirm referential/scene context resolves attachment essentially immediately, on par
  with or ahead of lexical bias. **This is the mechanism most directly relevant to the catastrophic clausal-
  attachment residual** (advcl/acl/xcomp/ccomp 0.01-0.12): it requires tracking how many discourse entities/
  situations are already established (a running situation/entity model), which IS recoverable from text (prior
  sentences ARE text), unlike prosody.
- **What is PINNED as NOT recoverable from text:** prosodic phrase-boundary placement. Kjelgaard & Speer (1999,
  *J. Memory & Language* 40:153-194) show prosodic boundaries causally shift attachment preference in comprehension.
  Snedeker & Trueswell (2003, *J. Memory & Language* 48:103-130) show, decisively for this question, that SPEAKERS
  only produce disambiguating prosody when the referential scene leaves genuine ambiguity for the LISTENER -- i.e.
  prosody is deployed by the language production system precisely to resolve the residual that referential/lexical
  context does not already resolve. This means the written-text residual after a perfect referential/lexical model
  is exactly the population prosody exists to solve in speech -- a structural argument (not just an absence
  argument) for why some fraction of the gap is genuinely unrecoverable from text at any corpus scale.

## Part 3 -- the honest ceiling question

**Neither fully PINNED nor fully reachable -- it decomposes by relation class:**
- **nmod/obl (PP-attachment), recall 0.18-0.57:** partially reachable. The field's own best type-level result
  (Hindle & Rooth 1993, 80% on 880 test items from a 13M-word corpus; human ceiling 88.2%, Ratnaparkhi, Reynar &
  Roukos 1994, HLT) proves a CORRECTLY-SCOPED type-level lexical statistic gets most of the way there without any
  token/event conditioning -- meaning most of this residual is a MISSING STATISTIC (the substrate never built the
  preposition-specific verb-vs-noun contrast), not a missing GRAIN (type vs token). A genuine token/event-
  conditioned residual likely remains on top, per Bicknell/Metusalem, but is unmeasured and untested for accuracy
  impact anywhere in the literature.
- **advcl/acl/xcomp/ccomp (clausal attachment), recall 0.01-0.12:** this is the field-documented right-branching-
  trap / DMV ceiling territory (Klein & Manning 2004, *ACL*: DMV 43.2% vs right-branching-baseline 33.6% on WSJ10;
  in-repo `RESEARCH_bf_acquisition.md` already names this PINNED at the field level for structure induction
  generally). The specific fix this drill identifies is NOT more selectional/semantic knowledge (already tried,
  null -- "the clausal cue was NULL" per the construction-stack experiment) but discourse-referential tracking
  (Altmann & Steedman mechanism) -- reachable from text, not yet built or tested for this relation class
  specifically. Prosody (Kjelgaard & Speer; Snedeker & Trueswell) bounds the ceiling of even that fix.

## Cheap decisive test (ranked, do in this order)

1. **(Cheapest, highest field-precedent, ~1 day)** Build the classic Hindle & Rooth (1993) preposition-specific
   directed association -- `LR(p) = log[ P(p | v) / P(p | head-noun) ]` from unambiguous training instances --
   scored ONLY on the nmod/obl subpopulation (not blended into full UAS), with a margin gate (reuse the
   `typed_selectional_preference` win's tau approx 0.3 pattern: fire only when the syntax-only marginal leaves a
   near-tied verb-vs-noun attachment). **HARD-PASS:** beats the syntax-only floor on the nmod/obl subpopulation,
   CI-separated, shuffled-pair twin loses. **HARD-FAIL:** no margin beats the floor even restricted to this
   narrower, field-matched statistic -- this would be a much stronger, field-anomalous negative than what exists
   today (today's refutations used a domain-mismatched generic association, not this one), and would meaningfully
   raise confidence that the substrate's specific text/register combination genuinely lacks the signal even where
   the general field does not.
2. **(Medium cost, ~2-3 days, theory-driven, uncertain yield)** Prototype a joint agent+verb-conditioned instrument/
   patient expectation (3-slot co-occurrence or an HD-bound joint representation) for the INSTRUMENT-vs-MODIFIER PP
   subtype specifically, gated the same way. **HARD-PASS:** beats step 1's result CI-separated on the subset where
   step 1 leaves genuine residual ambiguity. **HARD-FAIL:** no improvement over step 1 -- names the joint-
   conditioning lever as a real psycholinguistic effect with no measurable engineering payoff at this data scale,
   a legitimate located negative.
3. **(Larger build, the actual proven-relevant lever for the bigger prize)** Prototype a minimal discourse-entity
   counter (how many candidate referents/situations are already established) as an attachment feature for advcl/
   acl/xcomp/ccomp, per Altmann & Steedman. **HARD-PASS:** clausal-attachment recall improves CI-separated over the
   0.01-0.12 floor. **HARD-FAIL:** null -- names the clausal residual as ALSO needing signal beyond referential
   tracking (a stronger, more surprising negative given the theory's strength).

## Cross-thread synthesis

Directly extends (does not duplicate): the parent x4 refutation (`the_parser_is_a_frozen_supervised_hard_decode...
/SOLVED.md`), the full-scale scorer result (`scale_the_reading_learned_arc_scorer.../SOLVED.md`, the exact 0.54/0.77
numbers this drill was asked about), the typed-selectional margin-gate precedent (`type_generalized_selectional_
preference.../SOLVED.md`, the reusable "gate on discriminating signal" pattern), and the register-general attachment
mechanism spec (`research_register_general_argument_attachment_mechanism_2026-09-04.md`, whose McRae et al. 1998
weighting table this drill reuses to explain WHY noisy semantic add-ons net-negative against an already-accurate
structural prior).

## Substrate-product implications

Do not build a new "generative world model" organ as the first move for this specific residual -- that is the
right long-term destination for the clausal-attachment prize (already named as such in two prior SOLVED docs) but
is NOT the cheapest next step for PP-attachment specifically. The cheapest, most field-precedented, genuinely
untested-in-repo move is narrower and cheaper than either "more semantics" or "a whole situation model": the right
STATISTIC (preposition-specific, not generic-lemma; domain-matched, not ROCStories-trained) at the right SCOPE
(nmod/obl subpopulation only) with the already-proven GATING pattern (margin-gated, not blanket-applied). Only after
that is measured should the joint-event-conditioned (token-level) mechanism or the discourse-entity model be built.

## Citations (verified count: 13 external, all author/year/venue confirmed via direct search this session; plus 6
in-repo citations re-confirmed by direct code/doc read)

Bicknell, Elman, Hare, McRae & Kutas 2010 (*J. Memory & Language* 63:489-505); Metusalem, Kutas, Urbach, Hare, McRae
& Elman 2012 (*J. Memory & Language* 66:545-567); Lambon Ralph, Jefferies, Patterson & Rogers 2017 (*Nature Reviews
Neuroscience* 18:42-55); Patterson, Nestor & Rogers 2007 (*Nature Reviews Neuroscience* 8:976-987); Kutas &
Federmeier 2011 (*Annu. Rev. Psychol.* 62:621-647); Rabovsky, Hansen & McClelland 2018 (*Nature Human Behaviour*
2:693-705); Hindle & Rooth 1993 (*Computational Linguistics* 19:103-120); Ratnaparkhi, Reynar & Roukos 1994 (HLT
Workshop, Plainsboro NJ); Altmann & Steedman 1988 (*Cognition* 30:191-238); Spivey & Tanenhaus 1998 (*JEP:HPP*
24:1521-1543); Tanenhaus, Spivey-Knowlton, Eberhard & Sedivy 1995 (*Science* 268:1632-1634); Kjelgaard & Speer 1999
(*J. Memory & Language* 40:153-194); Snedeker & Trueswell 2003 (*J. Memory & Language* 48:103-130). Re-confirmed
in-repo: Frazier & Fodor 1978, Frazier & Clifton 1996, MacDonald/Pearlmutter/Seidenberg 1994, Trueswell/Tanenhaus/
Kello 1993, McRae/Spivey-Knowlton/Tanenhaus 1998, Klein & Manning 2004.

## P (deflated per lit-scan-calibration; novel-synthesis capped at 0.50)

- P(the type/token distinction is a real, literature-documented, independently-verified computational gap, not a
  relabeling): **0.70** (directly supported by Bicknell 2010 + Metusalem 2012's explicit ruling-out of pairwise
  association).
- P(a narrowly-scoped, correctly-matched type-level retry, per step 1, beats the floor CI-separated on nmod/obl):
  **0.40** (field-precedented at 80-88% for the general task; deflated for domain/scope mismatch risk).
- P(a genuine joint/event-conditioned token-level mechanism, per step 2, beats step 1's result CI-separated):
  **0.30** (theoretically motivated, zero direct engineering precedent, novel-synthesis cap applies).
- P(a discourse-entity referential-tracking feature, per step 3, improves clausal-attachment recall CI-separated):
  **0.35** (theoretically the strongest-supported mechanism for this specific relation class, but unbuilt and
  unmeasured in this substrate).

## TLDR

We asked: when the reading-taught parser struggles with sentences like "eat pizza with a fork" (does "with a fork"
belong to the eating or the pizza?), is the fix a smarter kind of word-knowledge we have not tried, or is that
information simply not present in plain text at all? Answer: both, but not in equal measure. Four earlier attempts
to use general word-meaning knowledge to fix this all made things WORSE, and we found the specific reason: all four
were "on average, across every use of this word" knowledge, not "given exactly what is happening in THIS sentence"
knowledge -- and brain-science evidence shows people really do use the second, richer kind. But there is a cheaper
fix to try first: the classic, well-proven old-school method for exactly this problem (which prepositions like
"with" or "of" tend to attach to which specific verbs versus which specific nouns) was never actually built the
right way here -- what was built was a much blunter, mismatched-source version of that idea. Try the sharp, well-
proven version first; it is cheap and already known to work well elsewhere. Separately, a different and bigger
problem -- sentences with confusing extra clauses -- is not really a word-knowledge problem at all; it needs the
reader to keep track of how many people/things a story has already introduced, which IS available from plain text
(earlier sentences), just not yet built. And some real fraction of both problems will never be fully fixable from
text alone -- speech carries pauses and tone of voice that text does not, and science shows people specifically use
those cues exactly in the hardest, most ambiguous cases -- so we should expect a real, permanent, honest gap even
after every text-based fix above is built.

## QUESTIONS

None.

## NEXT STEPS

1. Run the cheap decisive test, step 1 (Hindle & Rooth-style preposition-specific, domain-matched, margin-gated
   association, scored only on nmod/obl) before building anything new -- this is a genuinely different statistic
   from what was already refuted, not a re-test.
2. If step 1 clears the floor: file step 2 (joint agent+verb-conditioned instrument expectation) as the token-level
   follow-on, scoped to the instrument-vs-modifier PP subtype specifically.
3. Independently of 1-2, file step 3 (discourse-entity referential-tracking feature for clausal attachment) as its
   own cell -- it targets the bigger, currently near-zero-recall residual (advcl/acl/xcomp/ccomp) and is motivated
   by a different, stronger mechanism (Altmann & Steedman referential theory) than anything tried against it so far
   (only a simple matrix-verb structural cue was tried and went NULL).
