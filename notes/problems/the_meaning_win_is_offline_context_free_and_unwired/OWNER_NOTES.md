---
owner_verdict: DONE
---

SUBMISSION -- SOLVER RESULT: the_meaning_win_is_offline_context_free_and_unwired
STATUS: PARTIAL  (bar's decisive option 3 = a rigorous negative is a PASS that closes the meaning-line
                  wiring; also refutes the brief's grounded-context mechanism + gives a positive
                  redirection) | ledger malformed/incomplete: 0
REVERIFY: .venv/Scripts/python.exe verification/test_meaning_win_context_transfer.py  (PASS)
NO hdlab/ MODIFIED (Q111: proposed diff below; strategy lands it).
NOTE: PROBLEM.md body says "filed at priority 1" but its frontmatter says priority: 6 -- the GUI reads
the frontmatter; please reconcile.

THE ANSWER IN ONE LINE
The offline grounded meaning win does NOT survive contact with real reading. On a context-conditioned
sense-selection task, the ONLY thing that works is the frequency PRIOR (which the reader currently
ignores); NO context channel -- grounded OR associative -- beats it, and the one place context could
add value (picking the RARER, context-appropriate meaning against frequency) is UNLEARNABLE on our
archaic corpus. Wire the frequency prior; do NOT wire any context channel for selection yet; the
capability that defines the problem needs a modern benchmark we do not have.

THE BAR (verbatim, PROBLEM.md S7)
A context-conditioned grounded read-out must beat, CI-separated over its UPPER bound: (a) the strongest
FREQUENCY floor, (b) the current live reader's meaning assignment, AND (c) the CONTEXT-FREE grounded
read-out (to prove context earns its keep). Info-free twin (shuffled grounding / scrambled context)
LOSING. Report CI half-width and null p95. DECISIVE EITHER WAY, incl.: "Neither beats the current live
reader downstream -> the offline win does NOT transfer to live reading; a rigorous negative is a PASS
that closes the meaning-line wiring rather than leaving it perpetually re-opened."

=====================================================================================================
WHAT I BUILT
=====================================================================================================
One leakage-controlled experiment (exp_context_conditioned_meaning_transfer_v1.py) that REUSES the
landed, pre-registered WSD instrument (exp_context_conditioned_sense_selection_v1: v3 definitional
facts, 288 multi-sense words, 841 trials; L1 = eval sentences removed from the RI-fit corpus; L2 =
symmetric answer-masking) and puts the EXACT representation that won the offline metric -- GNOC =
concreteness-stripped 11-dim sensorimotor cosine (exp_ownmetric_frequency_controlled_v1, re-verified
this session: GNOC 0.741 vs PPMI floor 0.558) -- into the CONTEXT-conditioned task, in two
brain-faithful sense representations: sense=LABEL (human-norm grounded profile) and sense=EXPERIENCE
PROTOTYPE (centroid of the sense's OTHER, held-out sentences -- the representation that made the prior
C3 arm work, generalized to grounding). Floors recomputed on each population; paired bootstrap over
words; the DOMINANT-vs-SUBORDINATE split isolates the frequency-defeating items.

=====================================================================================================
WHAT I MEASURED (micro accuracy; split by whether the true sense is most frequent)
=====================================================================================================
  arm                         DOM n / acc / >uniform        SUB n / acc / >uniform
  MFS_PRIOR (floor a & b)     708 / 0.551 / YES             133 / 0.000 / no (by construction)
  CTXFREE_GNOC (floor c)      411 / 0.404 / no               79 / 0.253 / no
  CTX_GNOC_LABEL (offline rep)383 / 0.418 / no               81 / 0.407 / NO
  CTX_GNOC_PROTO (grounded)   119 / 0.672 / YES               6 / 0.500 / no
  CTX_DIST_LABEL (associative)408 / 0.409 / no               85 / 0.341 / no
  CTX_DIST_PROTO (associative)121 / 0.719 / YES               6 / 0.667 / no

Overall: MFS 0.4637 beats uniform 0.3995 CI-sep [0.4303,0.4975]. Every context arm sits BELOW the
prior (CTX_GNOC_LABEL 0.4159, CTX_DIST_LABEL 0.3976, CTX_FUSE_LABEL 0.4431, CTXFREE_GNOC 0.3796).

THREE FACTS SETTLE IT:
1. THE FREQUENCY PRIOR IS THE WORKING HALF OF THE BRAIN'S REORDERED-ACCESS MECHANISM -- AND UNWIRED.
   MFS beats uniform CI-separated (this is Duffy & Rayner's dominance prior). The live reader's
   ConceptSpace superposes all senses of a lemma into ONE blended vector -> sense-blind, so floor (b)
   == MFS (the reader has NO sense mechanism at all).
2. CONTEXT-CONDITIONED GROUNDED SELECTION IS AT CHANCE ON THE ITEMS THAT MATTER. On subordinate-
   congruent trials (answer NOT the most frequent -- the only place context could beat frequency),
   GNOC is not CI-separated above uniform chance (0.407 vs 0.338, n=81) and TIES its info-free
   (shuffled-grounding) twin (paired-word delta -0.0043 CI [-0.063,+0.053]) -- no grounded signal,
   the OPPOSITE of the offline base where the twin LOST decisively (0.468 vs 0.741).
3. THE EXPERIENCE PROTOTYPE READS DOMINANT SENSES (0.67-0.72 CI-sep) BUT IS STRUCTURALLY BLIND TO
   SUBORDINATE SENSES (n=6): a sense attested once has no held-out prototype. The only arm that beats
   chance does so by re-finding frequency, on the items frequency already wins.

=====================================================================================================
BRAIN-FOUNDATIONAL DRILL -- AND A CLAIM I WITHDREW UNDER POWER (the honest arc)
=====================================================================================================
Opening brain question: what KIND of computation is context-appropriate meaning selection? It is a
THEMATIC/ASSOCIATIVE judgement ("which situation does this word belong to -- river or money?"), the
LIFG/pMTG associative-relatedness system, NOT the ATL feature-SIMILARITY computation that won offline
(the just-integrated two-meaning-systems split). Prediction: the grounded (similarity) channel has no
special advantage for selection.

FIRST PASS (small fair-prototype population, n=49 words): fusing grounding into the associative channel
appeared to HURT -- FUSE-DIST -0.044 CI [-0.089,-0.004], CI-separated. RE-RUN AT POWER (label
population, n~154 words): FUSE_LABEL-DIST_LABEL = +0.017 CI [-0.027,+0.063]; GNOC_LABEL-DIST_LABEL =
+0.033 CI [-0.021,+0.087] -- ALL channel differences straddle zero. THE "GROUNDING HURTS / IS THE
WRONG SYSTEM" CLAIM DID NOT REPLICATE AND IS WITHDRAWN. (The owner's "confirm it is brain foundational"
prompt forced this power-check -- the exact value of the deepening discipline.)

WHAT SURVIVES AT POWER (robust): the two context channels are statistically INDISTINGUISHABLE and BOTH
sit below the frequency prior. The grounded channel has no special advantage for selection (consistent
with the two-systems LENS) but I have NO CI-separated evidence it is worse. The robust mechanism
statement: the brain resolves ambiguity with a frequency PRIOR + a context LIKELIHOOD; we have the
prior (works, unwired), and the context-likelihood half -- in either meaning system, at either
representation -- has no purchase over the prior on this instrument.

=====================================================================================================
WHY THIS IS A RIGOROUS NEGATIVE, NOT A TUNING-LIMITED ONE
=====================================================================================================
The brain's mechanism (reordered access = prior + context likelihood, over two meaning systems) was
identified and BUILT. Its working half reproduces. Its untested cell -- can context OVERRIDE frequency
on subordinate senses -- is shown un-testable on this instrument with a SPECIFIC reason: subordinate
senses are attested once, so no channel (grounded/associative/label/prototype) can represent them
(prototype n=6; label subordinate n=81 at chance). This is a DATA limit (the ~200-year-old homogeneous
McGuffey corpus the brief flags), not a mechanism limit. The decisive re-test needs a MODERN balanced
contextual WSD benchmark -- NOT on disk (only context-free SimLex/SimVerb/WordSim; no SCWS/WiC/SemCor).

=====================================================================================================
CONTROLS (what each excluded)
=====================================================================================================
info-free twin (shuffled grounding rows) TIES the grounded arm -> no grounded signal to destroy
(contrast: offline base twin LOST); query-swap (context from a DIFFERENT word) leaves GNOC unchanged
-> context not contributing; context-FREE grounded read-out (floor c) ~= context-conditioned (context
adds only +0.06 CI[0.005,0.115] over context-free, and BOTH sit below the frequency floor); experience
prototype holds out the trial sentence (leakage-proof) and is scored only where every candidate is
representable (fair, label-free population); dominant-vs-subordinate split isolates the
frequency-defeating items; MFS uses the FULL lexical prior (conservative -- a STRONGER floor to beat,
and defined by the same counts as the dominance split so MFS is exactly 0 on subordinate by
construction); paired bootstrap over WORDS for every margin.

=====================================================================================================
AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
=====================================================================================================
1. Section 7 (meaning re-frame) -- the "condition it on context" half is now TESTED: conditioning the
   read-out on context does NOT transfer in EITHER meaning system; no context channel beats the
   frequency prior or reads the frequency-defeating items. The wire-able half is the frequency PRIOR
   (MFS beats uniform CI-sep; the reader is sense-blind, so this is a real unwired gain). The grounded
   channel has no special advantage for selection (at power indistinguishable from associative -- do
   NOT record "grounding hurts"); wire grounding where SIMILARITY matters, not selection.
2. Section 6 (Semantic control, IFG -- "RIGHT-IDEA-WRONG-ALGEBRA; context enters additively; THIN"):
   new evidence -- even the additive context-coherence with the offline-winning GNOC rep is at chance
   on the frequency-defeating items and ties its info-free twin; the working selection signal is the
   frequency prior. Semantic-control being THIN is confirmed; its near-term substrate is the prior.
3. The offline meaning-win row is CONTEXT-FREE and SIMILARITY-typed: it does NOT extend to
   context-conditioned SELECTION on the available data -- a data-limited open cell, not a capability.

=====================================================================================================
PROPOSED hdlab CHANGE (strategy lands it, Q111 -- I did NOT write hdlab/)
=====================================================================================================
1. WIRE THE FREQUENCY PRIOR (most-frequent-sense) as the reader's sense default. It is the working
   half of reordered-access, brain-faithful (the dominance/subordinate-bias prior), CI-separated over
   the uniform floor, and the reader currently has NO sense mechanism. The single well-supported gain.
2. Do NOT wire ANY context-conditioning channel for sense-selection yet -- none beats the prior on
   this instrument; wiring one adds machinery that moves no number. The ASSOCIATIVE (distributional)
   channel is the more plausible substrate IF a proper instrument later shows context overriding
   frequency (the Route-B separable co-occurrence store, landed default-off, is that substrate) --
   MODERN-BENCHMARK-CONTINGENT, not a wire-now.
3. Do NOT wire the grounded read-out for context-selection (no advantage here, below the prior). Wire
   grounding where SIMILARITY matters (the whitening + fixed two-system fusion from
   the_substrate_has_one_meaning_system...), its proven role.
4. File the subordinate-OVERRIDE capability as MODERN-BENCHMARK-CONTINGENT.

=====================================================================================================
BRAIN-FOUNDATIONAL RESEARCH STILL NEEDED (the forward path -- this instrument cannot answer it)
=====================================================================================================
1. A PROPER INSTRUMENT (BLOCKING, empirical): a modern balanced contextual-sense benchmark with
   multiply-attested subordinate senses + grounded-covered targets (SCWS / WiC / SemCor). None on
   disk. Without it, no mechanism can be tested on the defining capability.
2. THE CONTEXT-LIKELIHOOD AS CONSTRAINT-SATISFACTION / ATTRACTOR SETTLING over a PRE-STORED sense
   inventory (lifetime experience -> human norms / a large external inventory, NOT a small-corpus
   centroid). I built small-corpus nearest-centroid -- which is why it only re-finds frequency.
   (Single-step softmax == argmax, so multi-step settling is untested; it would not help HERE -- the
   failure is absent evidence, not poor integration -- but is the faithful mechanism on a real bench.)
3. REFRAME: discrete WSD may itself be non-brain-faithful; the brain shapes a point in a CONTINUOUS
   semantic space (Rodd semantic settling). The more faithful task is graded context-MODULATION vs
   human contextual-similarity (SCWS), not discrete selection.
WHAT DOES NOT NEED MORE WORK: squeezing the McGuffey/definitional instrument -- it is converged (prior
works; context adds nothing; subordinate unlearnable); more angles would be the shared-wall tuning trap.

=====================================================================================================
KEY REALIZATIONS (the enabling moves)
=====================================================================================================
- Ask what KIND of computation the task is before choosing the channel. Context-selection is
  relatedness, not similarity; the offline win was similarity. That lens predicted grounded would have
  no special advantage -- confirmed (channels indistinguishable, both below frequency).
- POWER-CHECK the mechanistic claim before it carries the submission. "Grounding hurts" held on n=49
  (ci_hi -0.004) and flipped to +0.017 at n=154 -> withdrawn. The robust negative never depended on it.
- The prototype's FAIR population reveals its structural blindness: scoring it only where every sense
  is representable made it WORK (0.67-0.72) AND made visible that the fair population EXCLUDES rare
  senses (n=6). The mechanism that works is blind to exactly the items where it would matter.
- A twin that TIES is as informative as a twin that loses. Offline the shuffled-grounding twin LOST
  (real signal); here it TIES (no signal). Same control, opposite reading.
- The live reader is sense-blind by construction (one blended vector per lemma) -> floor (b) collapses
  onto floor (a); "unwired" is really "no sense mechanism yet."

=====================================================================================================
WHAT I DID NOT ESTABLISH / DO NOT QUOTE
=====================================================================================================
- I did NOT show context selection is impossible -- only that no channel beats frequency here and the
  subordinate test is data-starved (n=6/n=81). A modern benchmark could still show context overriding
  frequency via the associative channel -- untested for lack of data.
- DO NOT quote "grounding hurts the associative channel" / "grounding is the wrong system" -- that was
  an n=49 artifact, WITHDRAWN; at power the channels are indistinguishable.
- The prior-swamps-the-channel combination is NOT solved here -- different filed problem
  (the_prior_swamps_the_channel, another solver, reliability-weighted cue combination); I did not build
  a reliability-weighted prior+coherence gate.
- All numbers are on the v3 definitional instrument (grounded-covered subset); NO number crosses to the
  offline metric's population/scorer.

FILES: experiments/exp_context_conditioned_meaning_transfer_v1.py;
verification/test_meaning_win_context_transfer.py; data/exp_context_conditioned_meaning_transfer_v1/metrics.json.
NO hdlab/.

=====================================================================================================
PLAIN-LANGUAGE TLDR
=====================================================================================================
We recently proved our "hands-on sensory feel of a word" tool beats plain word-counting at judging
whether two words are alike -- but only offline, on isolated pairs. This asked whether that survives
inside real reading, where the sentence must pick which meaning is intended ("bank" by a river vs
"bank" that holds money). The answer is no. The only thing that reliably works is knowing which
meaning is normally more common -- a "frequency habit" the brain genuinely uses and our reader ignores
entirely. Nothing that reads the sentence -- not the sensory tool, not the word-company/topic signal
-- beats that habit, and the two sentence-reading tools are a statistical tie with each other. (My
first pass claimed the sensory tool made things WORSE; that did not hold up with more data, so I took
it back.) The one thing we could NOT settle -- whether the sentence can make the reader pick the RARER
meaning against the frequency habit -- our 200-year-old reading books cannot test, because rare
meanings appear once each; that is the whole point of the problem and it needs a modern, balanced set
of example sentences we do not have. So: wire the frequency habit now; do NOT wire either
sentence-reading tool for meaning-picking yet; use the sensory tool for "alikeness" instead; and get a
modern test set before claiming anything about overriding the frequency habit from context.

QUESTIONS: none blocking. One call: filed PARTIAL (the brief's grounded+context mechanism is refuted,
but there is a concrete positive wiring + a specific forward path). Read as REFUTED-of-the-mechanism +
redirection if you prefer.

NEXT STEPS: (1) wire the frequency prior (MFS); do NOT wire any context channel for selection yet.
(2) Acquire a modern balanced contextual WSD benchmark (SCWS/WiC/SemCor) with grounded-covered targets
and multiply-attested subordinate senses -- the only way to decide whether context can override
frequency. (3) On it, build the context-likelihood as attractor settling over a PRE-STORED sense
inventory, and test the continuous context-modulation frame. (4) Coordinate with
the_prior_swamps_the_channel once a real subordinate population exists.
