---
priority:
review: EXCELLENT
review_text: "Integrated SOLVED/EXCELLENT 2026-08-27 (owner-DONE). Re-verified scaffold-free first-hand (test_context_override_frequency.py PASS). VINDICATES the SemCor acquisition (owner-directed): CONTEXT overrides the frequency prior on MODERN data -- exactly the McGuffey data-limit the meaning_win result hypothesized. On held-out SUBORDINATE-congruent SemCor items (gold sense strictly less frequent; MFS=0 by construction), a structured context-likelihood read (held-out sense prototypes over BAG + local positional collocations) recovers the rarer sense at 0.39-0.46 vs MFS 0.0000, and beats UNIFORM chance (0.17-0.25) + both info-free twins (SHUFFLE/SCRAMBLE) CI-separated, SURVIVING leave-one-DOCUMENT-out (not topic memorization). THE MISSING ORGAN BUILT = SEMANTIC CONTROL (LIFG/pMTG): a GOLD-BLIND two-sided conflict trigger (coherence of best non-dominant minus dominant) predicts 'the prior is wrong' at AUC 0.79-0.81 (shuffled-context twin 0.58); conflict-gated GRADED suppression of the dominant sense is NET-POSITIVE CI-separated and lifts the frequency-OVERRIDE cases +0.007-0.033 (gain attributable to the real trigger -- shuffled-trigger twin loses). The reader was 'a brain with look-up but no CONTROL'. RETIRED FOUR wrong turns (all HARD-FAILED/null, honestly): grounded read-out for selection; SETTLING (formally IDENTICAL to argmax, McClelland 2013 -- a tautology, not a finding); DIAGNOSTICITY word-weighting; FUSION of associative+conceptual (routing not fusion); compositional role-binding (sense is topical/collocational, the bag captures it). HONEST: numbers are on the SemCor instrument (naturalistic-context ceiling ~0.39); the semantic-control NET gain is modest (63% dominant, trigger-quality-limited) -- quote the TRIGGER (AUC 0.79 gold-blind) + the override-case gain, not the net. Grade EXCELLENT (resolves the data-blocked question, builds the semantic-control organ, retires 4 levers with strong controls + self-corrections). hdlab landing EARNED -> QUEUED proven-ready (default-off reordered-access read + the semantic-control conflict-trigger+suppression organ; NO settling/grounding-for-selection/diagnosticity). Successor packaged = the #0 highest-priority next step: the ATL CONCEPTUAL/DEFINITIONAL meaning channel (the reader is at CHANCE on human meaning-identity because it only has the associative system; demand-ROUTED, not fused)."
---

# PROBLEM: can CONTEXT override the frequency habit and pick a word's RARER, context-appropriate meaning? -- now testable, because the modern data that was missing is on disk

**slug:** `context_override_of_the_frequency_prior_on_a_modern_wsd_benchmark` - **opened:** 2026-08-26 by the strategy session
(the forward path the integrated `the_meaning_win_is_offline_context_free_and_unwired` named as the ONE thing its
instrument could not test; the blocking data -- SemCor + WiC -- was acquired + VETTED 2026-08-26 at owner direction).
**status:** OPEN - **LOWEST priority on purpose (behind p1 retrieval-first wire-and-measure and p7 front-end): DATA-READY, but the sequencing holds -- do NOT jump it ahead of the retrieval work.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `8` (lowest). This is DATA-READY and genuinely
> brain-foundational, but the programme is WIRE-AND-MEASURE, retrieval-first (see `BRAIN_FOUNDATIONAL_AUDIT.md` §8): the
> retrieval architecture is the #1 live deviation and comes first. This brief exists so the meaning-context lane is a
> real, well-scoped, ready problem the moment sequencing reaches it -- not to pull effort off the retrieval work now.
> Re-rank UP only if the retrieval wire-and-measure stalls or the owner directs it.

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

Words have more than one meaning, and one is usually the common one ("bank" = money). The brain leans on that common
meaning as a HABIT -- but when the sentence points the other way ("the bank was muddy after the flood"), it can OVERRIDE
the habit and pick the rarer, context-appropriate meaning. Our reader has neither half: it has no per-word meaning habit
at all (it blends all of a word's meanings into one), and it has never been shown to let the sentence override that
habit.

The just-integrated `the_meaning_win...` result proved the frequency HABIT works (it beats a coin-flip) and is worth
wiring -- but it could NOT test the OVERRIDE, because our ~200-year-old reading books show each rare meaning only once,
so there was nothing to learn a rare meaning from. **That data gap is now closed:** SemCor (real sentences where rare
meanings appear many times) and WiC (a modern, balanced "same meaning?" test) are on disk and verified. So the open
question is finally answerable: **can a brain-faithful context mechanism make the reader pick the rarer,
context-appropriate meaning against the frequency habit -- on data that can actually test it?**

## 2. WHY THIS ONE

- **It is the decisive test the meaning line has been unable to run.** Every prior meaning result bottomed out at "the
  frequency prior wins / context adds nothing" -- but always on data that could not test the override. This removes that
  excuse: either context genuinely overrides frequency on real data (a first) or it genuinely cannot (a clean, publishable
  negative that finally closes the lane).
- **The mechanism to build is a real, un-built brain computation**, not another scoring tweak: context-likelihood as
  CONSTRAINT-SATISFACTION / attractor SETTLING over a PRE-STORED sense inventory (the `the_meaning_win...` forward path #2).
- **Data-ready, at owner direction.** SemCor + WiC were acquired + VETTED 2026-08-26; the loader exists. No acquisition risk.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED (do not invent around it):** lexical-ambiguity resolution is REORDERED ACCESS -- a frequency PRIOR over senses
that CONTEXT can override (Duffy & Rayner; the subordinate-bias effect: a subordinate meaning wins when the prior
context supports it, against frequency). The resolution itself is CONSTRAINT SATISFACTION / semantic SETTLING: the
context and the candidate senses mutually constrain a settling process toward the context-appropriate sense (Rodd et al.;
McClelland CSC), over senses stored from a LIFETIME of experience (the ATL semantic hub), NOT re-estimated from a tiny
corpus.

**OUR-INVENTION-UNDER-TEST (mark each choice, sweep don't adopt):** (a) HOW the context-likelihood is computed --
a single cosine to a sense centroid is the weak default the prior work found "only re-finds frequency"; the faithful
candidate is a multi-step SETTLING / constraint-satisfaction read (note: a single softmax step == argmax, so a genuine
settling test needs >1 step or an explicit mutual-constraint update). (b) WHAT the PRE-STORED sense inventory is: SemCor
experience prototypes (held-out sentences of each sense), human grounded profiles, or an external inventory -- NOT a
McGuffey-corpus centroid. (c) the context representation + window. COPY the OPERATION (prior + context-likelihood
settling toward the context-appropriate sense); SWEEP the parameters.

**Corpus-age note (THE POINT OF THIS BRIEF):** SemCor + WiC are MODERN and balanced -- this brief EXISTS to remove the
McGuffey-age confound that limited every prior meaning test. BUT SemCor's sense labels are WordNet (taxonomic); GRADE on
WiC's HUMAN same/different labels (and any graded-human signal), NOT WordNet taxonomic distance -- the standing rule
(grade meaning on human judgement, not WordNet) still holds. SemCor is the sense INVENTORY + the source of
multiply-attested contexts, not the scorer.

## 4. MEASURED vs INFERRED

**MEASURED (`the_meaning_win...`, integrated PARTIAL, re-verified scaffold-free):** on the McGuffey/definitional
instrument the frequency prior (MFS) beats uniform CI-separated (0.4637 vs 0.3995) and is the ONLY selection signal that
works; NO context channel (grounded OR associative, label OR experience-prototype) beats it; on subordinate-congruent
items every context arm is at chance and ties its info-free twin; the experience prototype reads DOMINANT senses only
(subordinate cell n=6, data-starved). The grounded feature-similarity channel has NO special advantage for selection (at
power indistinguishable from associative -- do NOT re-quote "grounding hurts", withdrawn). **The single reason it could
not settle the override: subordinate senses attested ~once.**

**INFERRED / OPEN (this problem, decisive either way):**
- On SemCor + WiC, where subordinate senses are attested MANY times (VET: `point` 9 / `field` 10 / `light` 8 subordinate
  senses each attested >=2x), can a context-likelihood mechanism (constraint-satisfaction settling over a pre-stored
  inventory) recover the CONTEXT-APPROPRIATE sense on SUBORDINATE-congruent items -- i.e. beat the frequency prior where
  the answer is deliberately NOT the most frequent?
- Does the SETTLING/constraint-satisfaction read beat the single-cosine read (does the brain-faithful mechanism earn its
  extra machinery)?

## 5. ALREADY TRIED / DO NOT RE-RUN

- The McGuffey/definitional instrument is CONVERGED (prior works; context adds nothing; subordinate unlearnable). Do NOT
  squeeze it further -- that is the shared-wall tuning trap. The whole point is to move to the MODERN data.
- Single-cosine nearest-centroid context-likelihood -- done (`the_meaning_win...`); it only re-finds frequency. Do NOT
  re-run it as the headline; it is the FLOOR the settling mechanism must beat.
- Grounded read-out for SELECTION -- refuted (no special advantage). Wire grounding for SIMILARITY, not selection.
- `experiment_index.py query "wsd"`, `query "sense"`, `query "context"`, and check
  `exp_context_conditioned_sense_selection_v1/_v2`, `exp_learned_context_wsd_semcor_verbs_v1`,
  `exp_reader_sense_selection_bayesian_hub_v1`, `the_prior_swamps_the_channel_instead_of_combining_with_it` (REFUTED),
  and `reader_meaning_channel` (HARD_FAILED on homonym WSD) BEFORE building -- a WSD harness and prior negatives exist to
  reuse and not repeat.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Load the data through the VETTED loader `tools/load_wsd_benchmarks.py` (`load_wic`, `semcor_sense_contexts`) -- do NOT
  re-derive the SemCor parse (the label must be `.label()` then `.synset()`; a hand-rolled parse silently returns 0
  mentions). Read `data/wsd_benchmarks/MANIFEST.md`.
- Confirm the GROUNDED-COVERED target subset first (overlap of WiC/SemCor targets with the grounded norms vocab) and
  recompute EVERY floor on the scored population; the frequency prior (MFS) is the floor to beat, defined on the same
  counts as the dominant/subordinate split (so MFS is 0 on subordinate by construction -- a conservative, strong floor).
- Reproduce the `the_meaning_win...` frequency-prior result once so you trust the floor you are beating.

## 7. THE BAR

On SUBORDINATE-congruent items (the true sense is NOT the most frequent -- the only place context can beat frequency),
grounded-covered, held-out, floors recomputed on that population:

- **A context-likelihood mechanism (constraint-satisfaction / settling over a pre-stored sense inventory) must recover
  the context-appropriate sense CI-separated over the UPPER bound of the strongest FREQUENCY floor (MFS), with the
  info-free twin (SHUFFLED / scrambled context sentence) LOSING CI-separated.** Report CI half-width and null p95 beside
  every margin. AND show the SETTLING read beats (or CI-ties, honestly reported) the single-cosine read (does context's
  brain-faithful machinery earn its keep?).
- **DECISIVE EITHER WAY:**
  - Context overrides frequency on subordinate items CI-separated -> the override capability is REAL on modern data;
    propose the hdlab wiring (strategy lands it; it composes on the frequency-prior sense default).
  - Context does NOT beat the prior even with multiply-attested subordinate senses + a settling mechanism -> a rigorous
    negative that FINALLY closes the meaning-context-selection lane (context-likelihood is not a wire-now for this
    substrate) -- as valuable as the win, and only trustworthy BECAUSE the data can now test it. State the settling
    mechanism you built and why it is the brain's, so the negative is on the mechanism, not on a convenient method.

## 8. FILES AND ENTRY POINTS

- `tools/load_wsd_benchmarks.py` (VETTED loaders), `data/wsd_benchmarks/` (WiC in-repo; SemCor via nltk -- see MANIFEST).
- `hdlab/grounded_similarity.py` (grounded sensorimotor spoke, `distinctive_grounded_similarity` for the similarity axis),
  `hdlab/meaning_fusion.py`, `hdlab/reading_grounding_loop.py` (the reader's sense-blind `ConceptSpace` -- the thing that
  needs a per-sense representation), `hdlab/modern_hopfield_readout.py` (softmax sharpen/blend -- a settling substrate to
  reuse), and any `context_vector` / constraint-satisfaction primitives (check before building a settling loop).
- Prove in `experiments/` + `verification/`; propose the hdlab WIRING diff in `SOLVED.md` (strategy lands it, board Q111).
  **Do NOT write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT grade on WordNet taxonomic distance -- grade on WiC HUMAN labels / graded human judgement.
- Do NOT carry any McGuffey/definitional number onto the modern benchmark -- different scorer and population; no number
  crosses. Recompute every floor on the modern population.
- Do NOT re-quote "grounding hurts the associative channel" (withdrawn under power) or "counting beats the read-outs"
  (the retired frequency-unfair metric).
- Do NOT test the override on McGuffey (the confound this brief exists to remove); do NOT re-run the single-cosine
  context-likelihood as the headline (it is the floor).

---

## SOLVER REVIEW (strategy session, 2026-08-27 — INTEGRATED, owner-DONE)

**Grade EXCELLENT. Verdict SOLVED** (the bar met and strengthened, plus a deeper brain-foundational advance).
Re-verified scaffold-free first-hand — `test_context_override_frequency.py` PASS (context 0.46 vs MFS 0 and chance 0.25;
twins lose; leave-one-doc-out survives; trigger AUC 0.81 vs twin 0.58; suppression lifts the override cases CI-sep).

**Why EXCELLENT — and strategically important.** It answers the meaning-line question that had been stuck: on our old
200-year-old corpus no context channel could beat the frequency habit, and this proves that was a DATA limit, not a
mechanism one — on modern sense-labelled text, context *does* override frequency and pick the rarer meaning (~0.39–0.46
vs 0% for the habit, 16–25% for scrambled context), and it survives hiding the whole source document (real understanding,
not topic memorising). It **vindicates the SemCor acquisition** (the owner-directed data grab). Then, on the owner's
fidelity challenge ("if we were truly copying the brain, wouldn't it work better?"), it found + built the genuinely
MISSING organ: **semantic control** — the reader had the look-up part but not the LIFG/pMTG control that actively
SUPPRESSES the habitual meaning when the sentence disagrees. A gold-blind two-sided conflict trigger spots when the
prior is wrong (AUC 0.79, vs a scrambled-context twin at 0.59) and gates graded suppression, lifting the hard
rarer-meaning cases by up to ~a quarter at a tiny cost on the easy ones — the same trade-off the brain makes.

**Rigor:** it retired FOUR plausible levers with strong controls and self-corrections — grounded-read-out-for-selection
(refuted), settling (formally identical to the argmax read — a tautology, not a finding, McClelland 2013), diagnosticity
word-weighting (null), fusion of the associative + conceptual channels (hard-failed → the brain-faithful design is demand
ROUTING, not fusion), and compositional role-binding (sense is resolved by topical/collocational context the bag already
captures). Honest scope throughout (all numbers on the SemCor instrument; the net semantic-control gain is modest and
trigger-quality-limited — quote the trigger AUC and the override-case gain, not the aggregate).

**hdlab landing EARNED, QUEUED proven-ready** (Q111): a default-off per-sense reordered-access read (frequency prior +
structured-context log-likelihood) + the **semantic-control organ** (the gold-blind conflict trigger + conflict-gated
graded suppression — the substrate's missing semantic-control network). Do NOT wire settling / grounding-for-selection /
diagnosticity. A live-wiring composition — measure on the live reading/coref task before any capability claim. AUDIT
UPDATE folded (§2b + the meaning re-frame / semantic-control entries). **Successor packaged** = the #0 highest-priority
next step the solver named: the ATL CONCEPTUAL/DEFINITIONAL meaning channel (the reader is at CHANCE on human
meaning-identity because it only has the associative co-occurrence system; add the conceptual hub as a second,
demand-ROUTED channel — not fused).
