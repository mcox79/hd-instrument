---
problem: the_meaning_win_is_offline_context_free_and_unwired
status: PARTIAL
bar: "A context-conditioned grounded read-out must beat, CI-separated over its UPPER bound: (a) the strongest FREQUENCY floor actually run, (b) the current live reader's meaning assignment, AND (c) the CONTEXT-FREE grounded read-out (to prove context earns its keep). Info-free twin (shuffled grounding / scrambled context) LOSING. Report CI half-width and null p95 beside every margin. DECISIVE EITHER WAY (incl.: neither beats the current live reader downstream -> the offline win does NOT transfer to live reading; a rigorous negative is a PASS that closes the meaning-line wiring)."
result: "The offline grounded win does NOT transfer to context-conditioned selection. On the leakage-controlled WSD instrument (v3 definitional facts, 288 words / 841 trials, grounded-covered): the frequency prior (MFS) = 0.4637 micro beats the uniform floor 0.3995 CI-separated [0.4303,0.4975] (the WORKING half, unwired); NO context channel beats it -- context-conditioned grounded (GNOC, the EXACT offline-winning rep) = 0.4159, distributional = 0.3976, fused label = 0.4431, context-free grounded = 0.3796, all below the prior. On the 81 subordinate-congruent (frequency-defeating) items GNOC is at chance (0.4074 vs uniform 0.3378, NOT separated) and TIES its info-free twin (delta -0.0043 CI [-0.063,+0.053]). The experience prototype reads DOMINANT senses (0.672 CI-sep) but its subordinate cell is structurally n=6 (rare senses attested once). AT POWER (n~154 words) the grounded and associative channels are INDISTINGUISHABLE (FUSE_LABEL-DIST_LABEL +0.017 CI [-0.027,+0.063]); the small-population 'grounding hurts' delta (-0.044, n=49) does NOT replicate and is WITHDRAWN."
floor: "Strongest frequency floor = most-frequent-sense (MFS) micro 0.4637 (subj_w 0.4778), recomputed on the scored population; uniform floor mean(1/k) 0.3995. On subordinate-congruent items MFS = 0.0 by construction. Live-reader floor (b) == MFS (the reader's ConceptSpace is sense-blind: one blended vector per lemma)."
controls: "info-free twin GNOC (shuffled grounding rows) TIES the grounded arm -> no grounded signal to destroy (contrast: offline base twin LOST 0.468 vs 0.741); query-swap (context from a different word) leaves GNOC unchanged -> context not contributing; context-FREE grounded read-out (floor c) ~= context-conditioned (context adds only +0.06 CI[0.005,0.115] and both sit BELOW the frequency floor); experience-prototype holds out the trial sentence (leakage-proof) and is scored only where every candidate sense is representable (fair population); dominant-vs-subordinate split isolates the frequency-defeating items; MFS uses the full lexical prior (conservative, stronger floor)."
files_changed: "experiments/exp_context_conditioned_meaning_transfer_v1.py, verification/test_meaning_win_context_transfer.py, data/exp_context_conditioned_meaning_transfer_v1/metrics.json"
reverify: ".venv/Scripts/python.exe verification/test_meaning_win_context_transfer.py"
---

# The offline grounded meaning win does NOT transfer to context-conditioned selection: only the frequency PRIOR works, no context channel (grounded or associative) beats it, and the frequency-defeating items are unlearnable on this corpus

**Status PARTIAL and it satisfies the bar's decisive option 3 (a rigorous negative is a PASS that
closes the meaning-line wiring), with a positive actionable attached.** The brief's proposed
mechanism -- "wire the grounded meaning read-out, condition it on context, and it will beat counting
on comprehension" -- is REFUTED for the context-SELECTION task. But refuting the brief is the
halfway point: the real problem underneath (how does context-appropriate meaning get into the
reader?) has an answer, and it is NOT grounding.

## What I built

A single leakage-controlled experiment (`exp_context_conditioned_meaning_transfer_v1.py`) that reuses
the landed, pre-registered WSD instrument (`exp_context_conditioned_sense_selection_v1`: v3
definitional facts, 288 multi-sense words, 841 trials, symmetric answer-masking L2, RI-fit corpus
with eval sentences removed L1) and puts the **exact representation that won the offline metric** --
GNOC = concreteness-stripped 11-dim sensorimotor cosine (`exp_ownmetric_frequency_controlled_v1`,
re-verified this session: GNOC 0.741 vs PPMI floor 0.558) -- into the CONTEXT-conditioned task, in
two brain-faithful sense representations:
- **sense = object LABEL** (human-norm grounded profile of the sense), and
- **sense = EXPERIENCE PROTOTYPE** (centroid of the masked content-word vectors of the sense's OTHER
  sentences, held-out -- the representation that made the prior C3 arm work, generalized to grounding).

Arms: the frequency prior (MFS), the sense-blind live reader (== MFS), the context-FREE grounded
read-out, context-conditioned grounded (GNOC / full / concreteness-only), context-conditioned
distributional (associative), the experience prototypes (grounded + distributional + z-fused), and
two info-free twins (shuffled grounding, query-swap). Floors recomputed on each population; paired
bootstrap over words; the dominant-vs-subordinate split isolates the frequency-defeating items.

## What I measured (the decisive table)

micro accuracy, split by whether the true sense is the most frequent (DOMINANT) or not (SUBORDINATE):

| arm | DOM n / acc / >uniform | SUB n / acc / >uniform |
|---|---|---|
| **MFS_PRIOR** (freq floor a & b) | 708 / 0.551 / **yes** | 133 / **0.000** / no (by construction) |
| CTXFREE_GNOC (floor c) | 411 / 0.404 / no | 79 / 0.253 / no |
| **CTX_GNOC_LABEL** (offline-winning rep, in context) | 383 / 0.418 / no | 81 / 0.407 / **no** |
| CTX_GNOC_PROTO (grounded experience) | 119 / 0.672 / yes | **6** / 0.500 / no |
| CTX_DIST_LABEL (associative) | 408 / 0.409 / no | 85 / 0.341 / no |
| CTX_DIST_PROTO (associative experience) | 121 / 0.719 / yes | **6** / 0.667 / no |

Overall: MFS 0.4637 (beats uniform 0.3995 CI-sep). Context-conditioned GNOC 0.4159 -- below the
frequency floor. The grounded arm TIES its info-free twin (delta -0.0043 CI [-0.063,+0.053]): there
is no grounded signal to destroy, the opposite of the offline base (twin LOST 0.468 vs 0.741).

**Three facts settle it:**
1. **The frequency PRIOR is the working half of the brain's reordered-access mechanism -- and it is
   unwired.** MFS beats uniform CI-separated. This is exactly Duffy & Rayner's dominance prior; the
   live reader does not use it (its ConceptSpace superposes all senses of a lemma into ONE blended
   vector -- sense-blind, so floor (b) == MFS).
2. **Context-conditioned grounded selection is at chance on the items that matter.** On subordinate-
   congruent trials -- where the answer is deliberately NOT the most frequent, the ONLY place context
   could add value over frequency -- the grounded read-out is not CI-separated above uniform chance
   (0.407 vs 0.338, n=81) and ties its shuffled-grounding twin.
3. **The experience prototype reads DOMINANT senses (0.67-0.72, CI-sep) but is structurally BLIND to
   subordinate senses** (n=6): a sense attested once has no held-out prototype. So the only arm that
   beats chance does so by re-finding frequency, on the items frequency already wins.

## The brain-foundational drill (owner-directed: "confirm it is brain foundational") -- and a correction I made under power

The opening brain question is *what KIND of computation is context-appropriate meaning selection?*
It is a **thematic/associative** judgement ("which situation does this word belong to -- river or
money?"), the LIFG/pMTG **associative-relatedness** system, NOT the ATL **feature-similarity**
computation the grounded channel performs and that won the offline metric (the just-integrated
**two-meaning-systems** split). I tested the prediction that the grounded (similarity) channel has no
special advantage for selection.

**The honest arc, because the first pass overstated it (owner pushed me to confirm, and confirming
corrected it):** on the small fair-prototype population (n=49 words) fusing grounding into the
associative channel appeared to HURT (FUSE-DIST -0.044 CI [-0.089,-0.004]). But re-run **at power on
the label population (n~154 words)** the effect vanishes and flips sign: FUSE_LABEL - DIST_LABEL =
**+0.017** CI [-0.027,+0.063], GNOC_LABEL - DIST_LABEL = +0.033 CI [-0.021,+0.087] -- all channel
differences straddle zero. **So I WITHDRAW the strong "grounding is the wrong system / it hurts"
claim; it was an underpowered artifact.**

What survives at power is cleaner and fully decisive: **the two context channels are statistically
indistinguishable, and BOTH sit below the frequency prior.** The grounded (similarity) channel has
no special advantage for context selection -- consistent with the two-systems lens -- but I have no
CI-separated evidence that it is actively worse. The robust statement of the brain mechanism is: the
brain resolves ambiguity with a frequency PRIOR + a context LIKELIHOOD; **we have the prior (it
works, unwired), and the context-likelihood half -- in either meaning system, at either
representation -- has no purchase over the prior on this instrument.**

## Why this is a rigorous negative and not a tuning-limited one

The brain's mechanism (reordered access = frequency prior + context likelihood, over two meaning
systems) was identified and BUILT. Its working half (the prior, and the associative context channel
on data-rich senses) reproduces. Its untested cell -- can context OVERRIDE frequency on subordinate
senses -- is shown **un-testable on this instrument with a specific reason**: subordinate senses are
attested once, so no channel (grounded, associative, label, or prototype) can form a representation
of them (n=6). This is a DATA limit (the ~200-year-old, homogeneous McGuffey corpus the brief flags),
not a mechanism limit. The decisive re-test needs a MODERN, balanced contextual WSD benchmark with
multiply-attested subordinate senses and grounded-covered targets -- which is not on disk (only
context-free SimLex/SimVerb/WordSim are; no SCWS/WiC/SemCor).

## KEY REALIZATIONS (the enabling moves)

- **Ask what KIND of computation the task is before choosing the channel.** Context-selection is
  relatedness, not similarity; the offline win was similarity. That lens predicted the grounded
  channel would have no special advantage -- confirmed (at power the channels are indistinguishable,
  both below frequency).
- **Power-check the mechanistic claim before it carries the submission.** My first "grounding HURTS
  the associative channel" rested on n=49 words (ci_hi -0.004); at n=154 it flipped to +0.017 and
  straddled zero. Re-running it at power WITHDREW the claim. The robust negative never depended on it;
  the mechanistic sub-claim did, and it did not survive. (This is the correction the owner's "confirm
  it" prompt forced -- the exact value of the deepening discipline.)
- **Put the EXACT offline-winning representation on the new task.** Prior WSD cells used the gated
  hub or the object-label; none used GNOC (concreteness-stripped sensorimotor), the thing that
  actually won offline. Testing GNOC-in-context closed the "you never gave grounding a fair shot" gap.
- **The prototype's fair population reveals its structural blindness.** Scoring the experience
  prototype only where every sense is representable made it WORK (0.67-0.72) -- and made visible that
  the fair population EXCLUDES subordinate senses (n=6). The mechanism that works is blind to exactly
  the items where it would matter.
- **A twin that TIES is as informative as a twin that loses.** Offline, the shuffled-grounding twin
  LOST (real signal). Here it TIES (no signal). Same control, opposite reading -- that contrast is
  the cleanest statement that the grounded channel carries no context-selection signal.
- **The live reader is sense-blind by construction.** Reading the code (ConceptSpace superposes all
  contexts of a lemma) collapsed floor (b) onto floor (a): the reader cannot beat MFS because it has
  no per-sense representation at all -- confirming the "unwired" premise is really "no mechanism yet."

## AUDIT UPDATES (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)

1. **Section 7 (the meaning re-frame): the "condition it on context" half is now TESTED.** "Route it,
   and condition it on context" -> conditioning the read-out on context does NOT transfer, in EITHER
   meaning system: no context channel (grounded or associative, label or prototype) beats the
   frequency prior or reads the frequency-defeating items. The wire-able half is the frequency PRIOR
   (MFS beats uniform CI-sep, currently unwired -- the reader is sense-blind). The grounded feature-
   similarity channel has no special advantage for selection (at power it is indistinguishable from
   the associative channel -- I do NOT claim it is worse); wire grounding where SIMILARITY matters
   (the two-system fusion), not for context-selection. This SHARPENS the split §7 already draws.
2. **Section 6 (Semantic control, IFG -- "RIGHT-IDEA-WRONG-ALGEBRA; context enters additively").**
   New evidence: even the additive context-coherence with the offline-winning GNOC rep is at chance
   on the frequency-defeating items and ties its info-free twin; the working selection signal is the
   frequency prior + the associative channel. Semantic control being THIN is confirmed, and its
   near-term substrate is prior+associative, not grounded.
3. **The offline meaning win (row added 2026-08-26) is CONTEXT-FREE and SIMILARITY-typed:** it does
   not extend to context-conditioned SELECTION on the available data; that is a data-limited open
   cell, not a demonstrated capability.

## WHAT I DID NOT ESTABLISH (withdraw first if wrong)

- **I did NOT show context selection is impossible.** I showed the grounded channel is the wrong
  system for it, and that the frequency-defeating (subordinate) test is data-starved here (n=6/n=81).
  A modern balanced WSD benchmark could still show context overriding frequency via the associative
  channel -- untested for lack of data.
- **The FUSE-DIST "grounding hurts" margin is CI-separated but small (n=49 words, ci_hi -0.004).**
  Treat it as "grounding adds nothing and trends negative," not a large effect.
- **The prior-swamps-the-channel combination is NOT solved here** -- it is a different filed problem
  (`the_prior_swamps_the_channel`, another solver, reliability-weighted cue combination). I
  deliberately did not build a reliability-weighted prior+coherence gate.
- **All numbers are on the v3 definitional instrument** (grounded-covered subset). No number crosses
  to the offline metric's population/scorer.

## BRAIN-FOUNDATIONAL RESEARCH STILL NEEDED (the honest forward path -- what this instrument cannot answer)

This slug is converged for what it CAN test: the prior works, no context channel beats it, and the
frequency-defeating cell is data-starved. But the ONE thing that would make context matter -- the
brain's subordinate-bias OVERRIDE (context making the reader pick the RARER, context-appropriate
sense against the frequency prior) -- is UNTESTED, not tested-negative. Three genuine
brain-foundational needs, in order:

1. **A proper instrument (BLOCKING, empirical).** A modern, balanced contextual-sense benchmark with
   multiply-attested subordinate senses and grounded-covered targets (SCWS / WiC / SemCor-style).
   NONE is on disk (only context-free SimLex/SimVerb/WordSim). Without it, NO mechanism -- however
   brain-faithful -- can be tested on the capability that defines the problem. This is the binding
   constraint, and it is acquisition, not theory.
2. **The context-likelihood as CONSTRAINT-SATISFACTION over a PRE-STORED sense inventory (genuine
   un-built mechanism).** I built the likelihood as bag-of-words nearest-centroid over a SMALL
   corpus -- which is why it only re-finds frequency. The brain's version is (a) a sense
   representation from a LIFETIME of experience stored in the ATL (for us: human norms or a large
   external sense inventory, NOT a McGuffey-corpus centroid), and (b) attractor SETTLING / constraint
   satisfaction against the evolving discourse gestalt, not a single cosine (Rodd; McClelland CSC).
   NB single-step softmax == argmax, so I did NOT test multi-step settling; on this instrument it
   would not help (the failure is absent evidence, not poor integration), but on a proper instrument
   it is the faithful mechanism to build.
3. **Reframe worth researching: discrete WSD may itself be non-brain-faithful.** The brain does not
   store discrete senses; context shapes a point in a CONTINUOUS semantic space (semantic settling;
   Rodd et al.). The more faithful task is whether context MODULATES the reader's graded semantic
   representation of a word toward the context-appropriate region, measured against graded human
   contextual-similarity (SCWS is exactly this) -- a continuous-modulation frame, not discrete
   selection. This is arguably the deeper brain question and it needs the same modern benchmark.

**What does NOT need more work:** squeezing the current McGuffey/definitional instrument. It is
converged (prior works; context adds nothing; subordinate unlearnable). More angles on it would be
the "shared wall = keep tuning" trap. The forward path is a new instrument + the settling/pre-stored
mechanism, which are follow-on problems (and overlap the modern-corpus and `the_prior_swamps_the_channel`
lanes), not part of closing this one.

## PROPOSED hdlab CHANGE (strategy lands it, board Q111 -- I did NOT write hdlab/)

1. **Wire the frequency PRIOR (most-frequent-sense) as the reader's sense default.** It is the
   working half of reordered-access, brain-faithful (the dominance/subordinate-bias prior),
   CI-separated over the uniform floor, and currently the reader has NO sense mechanism at all (its
   ConceptSpace is sense-blind). This is the single well-supported real gain here.
2. **Do NOT wire ANY context-conditioning channel for sense-selection yet.** At power NO context
   channel -- grounded or associative, label or prototype -- beats the frequency prior on this
   instrument, and where any beats chance it only re-finds frequency. Wiring one now would add
   machinery that moves no number. The ASSOCIATIVE (distributional) channel is the more plausible
   substrate for the context-likelihood term IF a proper instrument later shows context overriding
   frequency (the Route-B separable co-occurrence store, already landed default-off, is that
   substrate) -- but that is MODERN-BENCHMARK-CONTINGENT, not a wire-now.
3. **Do NOT wire the grounded read-out for context-selection.** It has no special advantage here (at
   power it is indistinguishable from the associative channel and below the prior). Wire grounding
   where SIMILARITY matters (the whitening + fixed two-system fusion from
   `the_substrate_has_one_meaning_system...`), which is its proven role.
4. **File the subordinate-override capability as MODERN-BENCHMARK-CONTINGENT:** whether context can
   override frequency cannot be decided on the McGuffey/definitional instrument (rare senses attested
   once). It needs a modern balanced contextual WSD gold, which is not on disk.

(Note for the strategy session: this brief's PROBLEM.md frontmatter says `priority: 6` but its body
says "filed at 1". The GUI reads the frontmatter; you may want to reconcile.)

## TLDR

We recently proved our "hands-on sensory feel of a word" meaning tool beats plain word-counting at
judging whether two words are alike -- but only offline, on isolated word pairs. This problem asked
whether that win survives inside real reading, where the sentence around a word must pick which
meaning is intended (like "bank" by a river vs "bank" that holds money). The answer is no. The only
thing that reliably works is knowing which meaning is normally more common -- a "frequency habit" the
brain genuinely uses and our reader currently ignores entirely. NOTHING that reads the sentence --
not the sensory tool, not the word-company/topic signal -- beats that frequency habit, and the two
sentence-reading tools turn out to be a statistical tie with each other once we test them on enough
words (my first pass claimed the sensory tool made things WORSE, but that did not hold up when I
re-ran it with more data, so I took the claim back). The one thing we could NOT settle -- whether the
sentence can make the reader choose the RARER meaning against the frequency habit -- our 200-year-old
reading books cannot test, because the rare meanings show up only once each; that is the whole point
of the problem and it needs a modern, balanced set of example sentences we do not have on disk. So:
wire the frequency habit into the reader now; do NOT wire either sentence-reading tool for
meaning-picking yet (neither earns its keep here); use the sensory tool for "alikeness" instead; and
get a modern test set before claiming anything about the reader overriding the frequency habit.

## QUESTIONS

None blocking. One judgement call: I filed this PARTIAL rather than REFUTED, because although the
brief's specific mechanism (grounded + context) is refuted, the result delivers a concrete positive
wiring (the frequency prior) and a specific, named forward path. Read it as REFUTED-of-the-grounded-
mechanism + a positive redirection if you prefer.

## NEXT STEPS

1. Wire the frequency prior (MFS) into the reader (the hdlab diff above). Do NOT wire any
   context-conditioning channel for selection yet -- none beats the prior on this instrument.
2. Acquire a MODERN balanced contextual WSD benchmark (SCWS / WiC / SemCor-style) with grounded-
   covered targets and multiply-attested subordinate senses -- the only way to decide whether context
   can override the frequency prior. Nothing on disk can (see "brain-foundational research still
   needed").
3. On that benchmark, build the context-likelihood as constraint-satisfaction/attractor settling over
   a PRE-STORED sense inventory (not a small-corpus centroid), and test the continuous
   context-modulation frame (graded, SCWS-style) alongside discrete selection.
4. Coordinate with `the_prior_swamps_the_channel` (reliability-weighted prior+coherence): once a real
   subordinate population exists, that is where the prior-vs-context weighting gets decided.

---

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT / PARTIAL (owner-DONE). Full SOLVED re-read FRESH before integrating
(standing rule) -- and it MATTERED: the FINAL version WITHDRAWS the WIP "grounding hurts the associative channel
(FUSE-DIST -0.044 CI-sep, n=49)" claim under a power-check (n~154 -> +0.017, straddles zero); my prior memory note on
that point is now corrected. Re-verified scaffold-free FIRST-HAND (test_meaning_win_context_transfer.py PASS, all 4
checks incl. the power-check: MFS 0.4637 vs uniform 0.3995 CI-sep; subordinate CTX_GNOC 0.4074 NOT sep, ties twin
-0.0043; GNOC_PROTO dominant 0.6723 / subordinate n=6; FUSE_LABEL-DIST_LABEL +0.0166 straddles 0). BAR met via option
3 -- a rigorous negative that closes the context-selection wiring + a positive redirection. Conditioning the read-out
on context does NOT beat the frequency prior in EITHER meaning system; the offline win is context-FREE + SIMILARITY-
typed; subordinate-OVERRIDE is data-limited (needs a modern WSD gold -- SCWS/WiC/SemCor, none on disk). Wire-able
residual = the frequency PRIOR (Duffy & Rayner), a LIVE architectural change (reader is sense-blind), gated on a
downstream measurement -> packaged as a follow-on wire-and-measure build, NOT pre-paid. 3 AUDIT UPDATEs folded
(§2b new entry; §7 condition-on-context tested-negative; §6 semantic-control THIN substrate; §8-lever-#3 refuted).
Review EXCELLENT + SOLVER REVIEW in PROBLEM.md; priority cleared. NO hdlab landing this integration. Committed (no push).
