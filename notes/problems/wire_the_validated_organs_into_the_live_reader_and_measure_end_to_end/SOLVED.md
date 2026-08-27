---
problem: wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end
status: PARTIAL
bar: "On a REAL reading/comprehension task (not a synthetic organ instrument), inputs held identical between arms, floor recomputed on its population: the composed pipeline (2-3 validated organs wired ON) must beat the current live baseline (organs OFF) CI-separated over the strongest floor's UPPER bound, with the info-free twin (scrambled wiring / shuffled organ outputs) LOSING CI-separated, CI half-width + null p95 reported. Attribute the effect PER ORGAN (ablate each). DECISIVE EITHER WAY: WIN -> the parts compose into comprehension; RIGOROUS NEGATIVE (a full PASS) -> the composition does NOT beat baseline, then DIAGNOSE (is the front-end the binding constraint that swamps the organs -- feed the organs CLEAN/oracle inputs and show they help THERE but not through the noisy front-end)."
result: "RIGOROUS NEGATIVE, well-attributed = a full PASS per the bar. End-to-end through the LIVE front-end the composed reader answers entity-role queries at 0.483 [0.410,0.556] (hit@1, n=178 target queries, 57 real McGuffey passages) -- BELOW the trivial majority-role floor 0.781 [0.719,0.843]; in-scope (agent/patient) 0.562 [0.484,0.641] vs in-scope majority floor 0.908 [0.863,0.948]. On CLEAN/oracle inputs the SAME pipeline works: content-addressable retrieval recovers the right event hit@1 1.000 and the right role 0.983 [0.961,1.000] (half-width 0.020), beating the majority floor AND the exact-key live baseline (recency 0.730 [0.663,0.798]) CI-separated, info-free twin event hit@1 0.202 [0.140,0.264] LOSING CI-separated. So the organs are not broken -- the front-end is the wall. Front-end error taxonomy: MISASSIGNMENT-dominant (136 misassign vs 30 miss; miss-share-of-errors 0.181 CI [0.120,0.247], excludes 50%), split ROLE-label 86 / ENTITY 50, plus 104 gold roles OUT-OF-SCOPE (the agent/patient front-end structurally cannot emit theme/recipient/experiencer). STAGE 4 (the front-end lever, tested): a brain-faithful VERB-ARGUMENT-STRUCTURE role assigner (verb-class speech-verb + quotative-inversion + animacy prominence) lifts front-end in-scope accuracy 0.359 -> 0.822 (role-label errors 86 -> 10) and END-TO-END role answering 0.483 -> 0.736 [0.669,0.803] (all) / 0.562 -> 0.856 [0.797,0.908] (in-scope), CI-separated over the position baseline AND over an info-free twin (randomised roles, 0.438) -- but it does NOT clear the brutal in-scope majority floor (0.908; it ties it), because the residual is now the 104 OUT-OF-SCOPE roles (25 queries auto-fail) + ~26 two-animate who-did-what cases needing verb selectional preference. So the front-end is not just the diagnosed wall -- a brain-faithful front-end demonstrably RECOVERS most of it. STAGE 5 (core question re-asked on the FIXED front-end): with the good vargs front-end, content-addressable retrieval beats the organs-OFF recency baseline CI-separated (event hit@1 0.865 [0.815,0.916] vs 0.404) and the info-free twin loses (0.157), but STILL ties trivial counting (0.865) -- BUT the surface cue makes that a non-discriminating test. STAGE 6 (correction, incl. a self-retraction): on a lexically-DISJOINT paraphrase cue (WordNet synonyms) counting COLLAPSES to 0.253, so the surface task genuinely could NOT test recognition -- therefore Stage 5's 'front-end is the SOLE lever, organs add nothing' is UNSUPPORTED (artifact). Content-addressable MEANING retrieval also fails on this instrument (0.264-0.275, ties twin), BUT the cause is CONFOUNDED (auto-synonym quality / my phase-lift code / whitened space); good synonyms are actually CLOSE in raw grounded (~0.84), so 'meaning supply is the wall' is NOT established either. STAGE 7 (the clean instrument, delivered): removing all three confounds -- CURATED synonyms verified close in RAW grounded space (mean cosine 0.84), the PINNED mechanism run DIRECTLY as additive resonance over grounded-cosine (no phase-lift), raw (non-whitened) space -- content-addressable MEANING retrieval recovers lexically-disjoint synonym-paraphrase cues at 0.528 [0.434,0.623] (n=106), CI-SEPARATED over both the collapsed surface count (0.217) and the info-free twin (0.179). SO THE ORGAN DOES WORK on recognition -- refuting BOTH my overreaches (Stage-5 'organs add nothing' AND the first Stage-6 'meaning supply fails'). Honest scope: 0.528 << the exact-word ceiling 0.783, so meaning-based recognition is real but PARTIAL."
floor: "Strongest floor actually run = FLOOR_COUNT (content-lemma-overlap counting), role 0.983 [0.961,1.000] on clean inputs -- TIES content-addressable retrieval (no organ-specific advantage over trivial counting on discriminative real cues; reproduces the content-addressable audit's own honest scope). Trivial majority-role floor 0.781 [0.719,0.843] (live end-to-end 0.483 falls BELOW it); in-scope majority 0.908 [0.863,0.948]; exact-key live baseline recency 0.730 [0.663,0.798]; ambiguous-subset majority 0.800 [0.600,0.950]; info-free twin event hit@1 0.202 [0.140,0.264] / role 0.657 [0.590,0.725]."
controls: "FLOOR_MAJORITY (0.781) excludes 'the score is just the agent prior'. FLOOR_COUNT (0.983) excludes 'content-addressable retrieval beats trivial content matching' -- it TIES, so the organ adds nothing over counting on clean cues. BASE_COMPOSITE multiplicative-key (0.983) excludes 'additive beats composite on real cues' -- ties (audit honest scope). FLOOR_RECENCY (0.730) = the organs-OFF exact-key register under a content cue (the live baseline). TWIN_DERANGED (event 0.202 << CAR 1.000, CI-separated) = info-free retrieval twin LOSES. ORACLE-vs-LIVE contrast excludes 'the organs are broken' -- they hit 1.000 clean and collapse only through the noisy front-end, localising the wall. Error taxonomy (MISS vs MISASSIGN_ROLE vs MISASSIGN_ENTITY) excludes 'the wall is undiagnosed' -- misassignment-dominant, role-labeling (86) > entity (50), so top-down rescue is in scope but centrality-merge targets the smaller entity slice. Late-MERGE info-free twin (shuffled coherence) MERGE 0.600 > TWIN 0.375 on the ambiguous subset (not CI-separated). Noise sweep (miss-rate x misassign-rate, 9 cells) excludes 'fails for an unknown reason' -- maps degradation to error TYPE. STAGE-4 vargs front-end: info-free twin (SAME extracted heads, roles assigned by coin-flip) 0.438 LOSES CI-separated -> the role-assignment logic, not head extraction, carries the gain; position-baseline arm (identical downstream, only the assigner changes) isolates the front-end as the causal variable; verb-class scramble was rejected as too weak a twin and replaced."
files_changed: "experiments/exp_wire_organs_endtoend_v1.py (new), experiments/exp_meaning_cued_retrieval_v1.py (new, Stage-6 paraphrase test) + experiments/exp_recognise_cued_retrieval_v2.py (new, Stage-7 clean confound-free instrument), verification/test_wire_organs_endtoend.py (new, witness PASS 8/8), data/exp_wire_organs_endtoend_v1/metrics.json (new), notes/research_feedforward_vs_interactive_composition_2026-08-26.md (dispatched lit dive), notes/problems/wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end/SOLVED.md. hdlab/ UNTOUCHED (proposed diff below, Q111)."
reverify: ".venv/Scripts/python.exe verification/test_wire_organs_endtoend.py"
---

# Wire the validated organs into the live reader, measured end-to-end

## The one-line answer
Plugged three validated organs (content-addressable additive retrieval, the distinctive-feature meaning
read-out, and a top-down coherence merge; N400/segmentation and the DG/CA3 gate examined as ablations)
into a live entity-role reading task on 57 real McGuffey passages (178 gold queries), organs OFF vs ON,
identical inputs. **On clean inputs the composition works and beats the current exact-key live baseline
CI-separated; through the live front-end it collapses below the trivial "always say agent" floor.
The front-end (event/role extraction) is the binding constraint, and its errors are misassignment- and
out-of-scope-dominated, not miss-dominated -- so the fix is a better front-end (richer thematic roles +
plausibility-based role assignment), not more downstream organs.** This is the brief's named
"single most valuable finding available right now," delivered with the error taxonomy that makes it
trustworthy.

## What I built
A real end-to-end reading task, not a synthetic organ bench. Each McGuffey passage is read clause by
clause; entity-role bindings are written to a situation-model store; each `target_query` asks the role
an entity played at a non-final clause, cued by a PARTIAL content cue (the clause's participants, with
its verb dropped -- you ask about an event by what/who was in it, not by a slot index). This is the exact
gold the situation-model register was validated on (`exp_situation_model_accumulate_vs_overwrite_v1`,
atom 29609) but now measured (a) END-TO-END through a live front-end and (b) under a PARTIAL cue -- the two
things the isolated construction proof never did. Everything is behind flags so organs-OFF (baseline) and
organs-ON (treatment) run on identical inputs; the only variable is the wiring.

Stages (all in `experiments/exp_wire_organs_endtoend_v1.py`):
- **Stage 0 -- front-end error taxonomy.** Run the live POS-rule role extractor on all passages; classify
  each gold (entity, clause, role) as CORRECT / MISS (nothing extracted) / MISASSIGN_ROLE (right entity,
  wrong agent/patient) / MISASSIGN_ENTITY (clause bound to another plausible entity) / OUT_OF_SCOPE (a
  role the agent/patient front-end cannot emit). This routes everything (see the brain frame below).
- **Stage 1 -- ORACLE content-cued retrieval.** The organs' clean-input best case: floors, the exact-key
  live baseline, the multiplicative-composite baseline, content-addressable additive retrieval (surface
  and grounded-meaning content codes), and a deranged-cue info-free twin, with bootstrap 95% CIs.
- **Stage 2 -- LIVE front-end + a 9-cell corruption sweep** (miss-rate x misassign-rate), end-to-end.
- **Stage 3 -- the late-MERGE arm:** top-down topical centrality (Centering) re-resolves ambiguous entity
  links at write time, tested on the misassignment-eligible subset with its own recomputed majority floor
  and an info-free twin (shuffled coherence).

## The brain-foundational frame (this is where the deep work went)
The opening move was "how does the brain COMPOSE these reading stages?" -- and the brief's own §3 answer
("the brain reads as a feedforward PIPELINE, each stage feeds the next") is, per the literature, INCOMPLETE.
I dispatched a focused neuroscience/psycholinguistics dive (`notes/research_feedforward_vs_interactive_
composition_2026-08-26.md`) that adjudicated it:

- The faithful composition is **NEITHER a pure feedforward cascade NOR biological recurrence** -- it is a
  **late algebraic MERGE of independently forward-computed streams** (Norris, McQueen & Cutler 2000,
  "Merge", *BBS*) plus bounded single-pass revision. Apparent "top-down correction" is reproduced by
  combining forward streams at a decision point, not by backward editing.
- **Whether top-down rescue is even IN SCOPE is decided by the front-end error TYPE.** A MISS (nothing
  extracted) is a detection ceiling no feedback fixes; a MISASSIGNMENT (wrong PLAUSIBLE filler -- the
  Gibson, Bergen & Piantadosi 2013 noisy-channel / Ferreira good-enough pattern) is rescuable by a "does
  this fit the story so far?" merge. **So the cheapest decisive move is the error taxonomy, done first.**
- `AdditiveCueRetrieval` is the **pinned** mechanism (Myers & O'Brien 1998 resonance; McKoon & Ratcliff
  minimalist), not an invented convenience -- keep it as-is.
- **New fidelity gap found in a landed organ:** the N400 monitor segments on a running-mean CONTENT gist
  only, with no schema/goal term -- but Zacks et al. 2007 state boundary PLACEMENT is top-down-laden
  (schemas, goals). Logged as an AUDIT UPDATE below; not blocking here.

I folded this straight into the experiment: the taxonomy (Stage 0), the misassignment-subset MERGE
(Stage 3), and the corruption sweep that separates miss-rate from misassign-rate (Stage 2) all exist
because of this dive. The composition I measured is the brain-faithful late-merge, not a naive cascade.

## What I measured (the numbers)
**On CLEAN/oracle inputs -- the organs are not broken.** Content-addressable retrieval recovers the right
event (hit@1 1.000) and role (0.983 [0.961,1.000]); it beats the majority floor (0.781) and the exact-key
live baseline (recency 0.730) CI-separated; the info-free twin loses CI-separated (event 0.202). **But it
TIES trivial content-lemma counting (0.983) and the multiplicative-composite key (0.983)** -- so on
discriminative real cues the additive resonance organ has no accuracy advantage over counting (this
reproduces the content-addressable problem's own honest scope: "with real graded features the
additive-vs-composite gap is mostly a TIE").

**End-to-end through the LIVE front-end -- the wall.** The composed reader answers at 0.483 [0.410,0.556]
(all queries) / 0.562 [0.484,0.641] (in-scope agent/patient) -- BOTH far below the trivial majority floor
(0.781 / 0.908). A reader that ignored the front-end and always said "agent" would score higher. Every
downstream organ is swamped.

**Why (attribution).** Front-end in-scope accuracy is 0.359. Errors are MISASSIGNMENT-dominant (136 vs 30
miss; miss-share 0.181, CI [0.120,0.247] excludes 50%), and the misassignments split 86 ROLE-label
(right entity, wrong agent/patient) vs 50 ENTITY, with a further 104 gold roles OUT-OF-SCOPE. So: (a)
top-down rescue IS mechanistically in scope (misassignment-dominant), but (b) the dominant slice is
ROLE-labeling, and (c) 123/149 entities are animate persons -- so the role errors are person-vs-person
("who did what to whom"), where animacy/plausibility on a single argument cannot disambiguate; they need
full verb-argument structure. The minimal late-MERGE (topical centrality) only touches the smaller
ENTITY slice: on the ambiguous subset MERGE 0.600 vs recency 0.550 (not CI-separated) and it still loses
to the subset majority floor (0.800). It beats its info-free twin (0.600 vs 0.375) -- the direction is
right, the lever is too small.

## Stage 4 -- the front-end lever, TESTED (owner-directed: "do what's right, not what's cheap")
Rather than stop at the diagnosis, I diagnosed the 86 role errors and BUILT the brain-faithful fix. The
errors were mostly a VERB-ARGUMENT-STRUCTURE problem, not an inventory one: ~48 were quotative/dialogue
attribution ("said Harry", "answered the boatman") where the speaker is POSTVERBAL, so a "subject = agent"
rule brands the speaker a patient; 26 were genuine two-animate who-did-what; 12 passive. So I built a
verb-argument role assigner -- speech-verb class (VerbNet say/tell) takes an AGENT speaker, quotative
inversion puts it postverbally, animacy prominence (eADM proto-actor) breaks ties -- swapping ONLY the role
assigner, identical downstream. Result: front-end in-scope accuracy 0.359 -> 0.822, role-label errors
86 -> 10 (and misses 30 -> 4, entity errors 50 -> 32 as a side-effect of correct speaker linking);
end-to-end 0.483 -> 0.736 (all) / 0.562 -> 0.856 (in-scope), CI-separated over both the position baseline
and the info-free (randomised-role) twin (0.438). It does NOT clear the 0.908 in-scope majority floor -- it
ties it -- because the residual is the 104 out-of-scope roles + the 26 two-animate cases. **So the composed
system's binding constraint is the front-end, AND a brain-faithful front-end recovers most of the wall; the
lever is proven, and the remaining gap is now specifically scoped (role inventory + verb selectional
preference).**

BRAIN-FIDELITY of this front-end (my assessment; the owner-requested literature drill hit the account's
WEEKLY LIMIT and returned no report, so this is reasoning-pending-lit-VET, NOT freshly verified): verb-class
argument structure is faithful in KIND (VerbNet/FrameNet; pMTG/IFG) but a HAND lexicon is a convenience for
what the brain LEARNS distributionally; quotative-inversion special-casing is defensible (construction
grammar, Goldberg) but a full parser would subsume it; animacy prominence is pinned (eADM); the
RULE-PRIORITY cascade is my clearest divergence -- the faithful form is GRADED parallel constraint-
satisfaction (log-linear / normalised-recurrence; McRae/Spivey-Knowlton/Tanenhaus 1998; Levy 2008), which I
should adopt before claiming full fidelity. The info-free twin controls for spurious signal, but a HELD-OUT
verb set would be a stronger test that the hand lexicon is not overfit.

## Stage 5 -- the brief's CORE question re-asked on the FIXED front-end (does fixing it make the organs pay off?)
The obvious follow-up: I showed the organs are swamped by the WEAK front-end -- but once the front-end is
FIXED (Stage 4 vargs), do the downstream memory organs finally contribute? Re-ran the content-cued retrieval
arms on the vargs-committed store. **Answer: no.** Content-addressable retrieval beats the organs-OFF
recency baseline CI-separated (event hit@1 0.865 [0.815,0.916] vs recency 0.404) and the info-free twin
loses (0.157) -- so content-addressability IS a real capability the exact-key register lacks -- **but it
STILL ties trivial content counting (0.865 = 0.865) and the multiplicative composite (0.865), and the
MEANING organ adds nothing over surface codes (0.865).** Exactly the oracle-input result, reproduced with
the good front-end. **So fixing the front-end does not make the FHRR/additive/meaning organs valuable --
they provide no accuracy edge over word-counting even end-to-end on a good front-end.** This CONFIRMS the
verdict rather than overturning it: the only lever that moves comprehension is the front-end; the downstream
memory organs compose correctly but add nothing over trivial counting on this real task. (Witnessed:
`test_organs_still_tie_counting_on_the_fixed_frontend`.)

## Stage 6 -- CORRECTION of the Stage-5 interpretation (the "tie" was an artifact; the real wall is MEANING SUPPLY)
Stage 5's numbers are right but its READING -- "the front-end is the SOLE lever, the memory organs add nothing"
-- OVERREACHED, and was not brain-foundational. The retrieval cue in Stages 1-5 was each event's OWN content
words, so surface counting already points at the right event and there is NO headroom for meaning: `CAR_SURFACE`
(random per-lemma codes) IS lemma-counting, so of course it ties. That task cannot test what content-addressable
memory is FOR in the brain -- RECOGNISE not RECITE (Myers/O'Brien resonance): recover an event from a cue that
does NOT share surface words. `exp_meaning_cued_retrieval_v1.py` runs THAT test: cue each event with a fully
lexically-disjoint, meaning-preserving WordNet-synonym paraphrase (chosen independent of the grounded space;
disjoint fraction 1.00). Result (n=178): EXACT_COUNT 0.798 -> PARA_COUNT COLLAPSES to 0.253 (near chance -- so
the surface task genuinely could NOT test recognition), and content-addressable MEANING retrieval also fails on
this instrument (0.264-0.275, ties the twin 0.219). **THE DEFENSIBLE CORRECTION: Stage 5's "front-end is the
SOLE lever, the organs add nothing" is UNSUPPORTED -- it was an artifact of a surface-matchable task that cannot
test what content-addressable memory is FOR (recognise-not-recite).** What I did NOT cleanly establish (a
second over-correction I caught and retract): that "meaning SUPPLY is the wall". The meaning-cued FAILURE is
CONFOUNDED -- (i) WordNet's auto-selected first synonym is often obscure; (ii) my phase-lift code (theta = R.g)
may not preserve grounded cosine; (iii) I first measured similarity in the WHITENED space (0.343), which is
BUILT to separate related words. In the RAW grounded space, GOOD synonyms are actually CLOSE (cry/weep,
gate/door ~0.84), so the meaning representation is NOT obviously too weak. **HONEST STATE: the composed
downstream organs are neither shown worthless (Stage 5 artifact) nor shown to win -- a clean recognise-cued
retrieval instrument (good synonyms + a faithful meaning code + the right space) is the required follow-on
before ANY claim about meaning supply.** (Witnessed: `test_meaning_cued_retrieval_diagnosis_is_open` -- good
synonyms ARE close in raw grounded, so the v1 failure is instrument-confounded, not a clean supply-wall.)

## Stage 7 -- the clean recognise-cued instrument (RESOLUTION: the organ DOES work)
`exp_recognise_cued_retrieval_v2.py` removes all three Stage-6 confounds at once: (i) CURATED synonym pairs,
each verified to clear a RAW grounded-cosine threshold (87 pairs used, mean cosine 0.84 -- genuinely
meaning-close); (ii) the PINNED mechanism computed DIRECTLY -- additive Lewis-Vasishth resonance as
activation(event)=sum over cue words of max over event words of RAW grounded cosine, argmax -- NO invented
phase-lift; (iii) the RAW (non-whitened) grounded space. On real McGuffey event pools, cued with a fully
lexically-disjoint curated-synonym paraphrase (n=106): PARA_COUNT collapses to 0.217 (chance) but
**PARA_MEANING_GROUNDED = 0.528 [0.434,0.623], CI-SEPARATED over both the collapsed count (0.217) and the
info-free twin (0.179)** -- ~2.4x chance. **RESOLUTION: content-addressable MEANING retrieval genuinely
recovers paraphrased events -- the organ is NOT worthless (Stage-5 was a surface-task artifact) and meaning
supply does NOT simply fail (the first Stage-6 correction was the confounds).** Honest scope: 0.528 is well
below the exact-word ceiling (0.783), so meaning-based recognition is REAL but PARTIAL -- the grounded
representation supports it imperfectly, and the pool is per-passage. **NET for the whole problem: the composed
downstream organs DO add value on the task they are actually FOR (recognise-not-recite), which the original
surface end-to-end task could not show; the front-end remains the dominant lever for the recite task, but
'the organs add nothing / the front-end is the sole lever' is RETRACTED.** (Witnessed:
`test_recognise_cued_meaning_retrieval_works`.)

## KEY REALIZATION (added at Stage 7)
- **A null result is only as good as the task's ability to show a win.** I twice concluded the memory organs
  were valueless -- once from a task where surface counting already sufficed (no headroom), once by blaming
  a confounded instrument. The organ's value only appeared when I (a) tested the capability it actually has
  (recognise from a lexically-different cue), (b) with a fair signal (curated close synonyms), and (c) the
  pinned mechanism itself (additive resonance over the representation, not an invented code). Each overreach
  was caught by a can-fail control or an external challenge, not by me re-reading my own numbers.

## What I did NOT establish (and would withdraw first)
- **NOT a capability win.** The composition does not beat the strongest floor end-to-end; it does not even
  beat "always agent." I am NOT claiming the parts compose into comprehension on this task.
- **The organ-specific retrieval advantage is nil on clean cues** -- content-addressable additive retrieval
  ties trivial counting and the multiplicative composite. First thing I'd withdraw: any suggestion that
  swapping in the additive organ improves accuracy per se. Its value is architectural (pinned resonance,
  native partial-cue handling, composes with the FHRR register), not an accuracy lift here.
- **The live front-end is a SIMPLE POS-rule extractor I wrote**, not the full `situation_reader` pipeline
  (which needs CoNLL mentions the McGuffey gold does not carry). It is representative of the ~0.32-class
  front-end and its every error is measured, not tuned -- but the exact 0.359 number is this extractor's,
  and a stronger extractor would move it. The QUALITATIVE finding (front-end is the wall; misassignment-
  and role-dominated) is what I stand behind, and it is robust across the oracle-vs-live contrast and the
  9-cell sweep.
- **The MERGE arm is the minimal centrality version.** A negative on it is NOT a negative on the late-merge
  IDEA -- it is a report that the coherence term that matters for the dominant error (thematic-role
  plausibility / verb-argument structure) is not topical centrality, and building it is a front-end job.

## KEY REALIZATIONS
- **The composition question, not the organ question, was the real work.** Re-asking "how does the brain
  COMPOSE these stages" (via the lit dive) overturned the brief's own PINNED claim: reading is a late
  algebraic MERGE, not a feedforward cascade -- which reframed the whole experiment around the error
  taxonomy and a merge arm rather than a binary oracle-vs-live check.
- **The error taxonomy is the cheapest, most decisive control, and it must come FIRST.** Classifying
  front-end errors MISS vs MISASSIGNMENT (and role vs entity) is what turns "the front-end is the wall"
  from an assertion into an attributed finding -- and it is a re-labelling of output already produced, not
  a new experiment. It told me top-down rescue is in scope AND why the minimal rescue can't clear it.
- **Ties are findings.** Content-addressable retrieval tying trivial counting on clean real cues is not a
  failure to report around -- it is the honest, reproduced scope of the organ, and it localises the value
  to the noisy-front-end regime (which the task then shows is dominated by a different error entirely).
- **A metric can be gamed by its own majority class -- so recompute the floor on the population and check
  the live system against it.** The live end-to-end (0.483) falling BELOW the majority floor (0.781) is
  the entire story in one comparison; without recomputing that floor on the query population the 0.483
  would have looked like "moderate performance" instead of "worse than a trivial prior."
- **Diagnose the errors BEFORE building the fix -- it named the mechanism.** Categorising the 86 role
  errors showed ~48 were quotative inversion ("said X"), pointing straight at verb-argument structure as
  the lever. Building blind (e.g. a generic animacy patch) would have missed it -- 123/149 entities are
  animate, so animacy alone can't separate person-from-person; the diagnostic is what turned "the front-end
  is the wall" into "the front-end needs VERB-CLASS argument structure," which then doubled the number
  (front-end 0.36 -> 0.82, end-to-end 0.48 -> 0.74).

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md)
1. **Composition fidelity (NEW, spans §3/§5).** The reading pipeline's brain-faithful COMPOSITION is a
   late algebraic MERGE of forward-computed streams (Norris/McQueen/Cutler 2000) + bounded revision --
   NOT the pure feedforward cascade the p1 brief's §3 states as PINNED, and NOT recurrence. This converges
   with the WSD argmax thread and the p6 context-conditioning negative (top-down correction is narrow-scope,
   not a blanket override). Source: `notes/research_feedforward_vs_interactive_composition_2026-08-26.md`.
2. **F5 (N400 coherence monitor) has a fidelity gap.** It segments on a running-mean CONTENT gist with no
   schema/goal term; Zacks et al. 2007 establish boundary PLACEMENT is top-down-laden (schemas, goals,
   reader instructions). The isolated 0.988 result is not refuted (its synthetic items likely never tested
   schema violations) but is UNTESTED on the dimension that matters. Queue: seed the "expected content"
   prior from a coarse discourse/genre signal, re-test boundary placement.
3. **E2 register retrieval, measured END-TO-END on real text.** Content-addressable additive retrieval
   works on clean inputs (event hit@1 1.000) and beats the exact-key live baseline CI-separated, but TIES
   trivial content counting and the multiplicative composite on discriminative real cues -- confirming the
   content-addressable entry's "mostly a TIE with real graded features" honest scope on a NEW population.
   Keep additive as the default (native partial-cue, no collapse) but do not claim an accuracy lift.
4. **The binding constraint for end-to-end reading comprehension is the FRONT-END (event/role extraction),
   not the memory/retrieval stages** -- measured: every downstream organ is swamped; live end-to-end falls
   below the trivial majority floor. The front-end errors are misassignment- and out-of-scope-dominated
   (role-labeling 86 > entity 50 > miss 30; 104 out-of-scope roles), so the re-pointed next build is a
   richer-role, plausibility-aware front-end (verb-argument structure), NOT more downstream organs. This
   sharpens §6 (READ THE TEXT is WEAK) into the programme's current bottleneck. **DEMONSTRATED (Stage 4):
   a brain-faithful verb-argument role assigner (verb-class + quotative inversion + animacy) recovers most
   of the wall -- front-end 0.36 -> 0.82, end-to-end 0.48 -> 0.74 CI-separated -- so §6 is not just weak, it
   is the highest-leverage BUILDABLE lever, and the biggest single error class is quotative/dialogue
   attribution (postverbal speaker). Residual: out-of-scope role inventory + verb selectional preference.**
5. **MACHINERY FIDELITY AUDIT (owner-requested deep drill, 4-scan literature dive; the substrate the
   organs run ON, not just the composition).**
   - **The FHRR binding basis is CONFIRMED faithful -- do NOT replace it (owner-locked 2026-08-26).** The
     binding problem is genuinely OPEN (no neural mechanism is pinned); binding-by-synchrony is partly
     DISCONFIRMED (Thiele & Stoner 2003; Ray & Maunsell 2010/11); conjunctive/mixed-selectivity coding is
     pinned as a CODING principle (Rigotti & Fusi 2013; Quiroga 2005) but not a dynamic binding operation;
     VSA/circular-convolution is the best-specified COMPUTATIONAL-level theory with a neural existence-proof
     (Eliasmith SPA/Spaun 2012). Decisively, **SEM (Franklin, Norman, Ranganath, Zacks & Gershman 2020,
     Psych Review) -- a peer-reviewed brain model of event memory -- binds role->filler with HRR circular
     convolution + bundling and a hippocampus/cortex CLS split**: our exact machinery. FHRR is not a
     convenience; it is what the state-of-the-art faithful model uses. ("VSA binding unpinned" bites only
     at the neural-IMPLEMENTATION level.) This CORRECTS the "central binding op UNPINNED -> our-invention"
     framing in the audit's leverage ranking: unpinned at implementation, but a defensible, published model.
   - **Real, FHRR-COMPATIBLE fidelity gaps (do not move THIS task's number; matter at scale / the read-half):**
     (a) the situation-model STORE is a dense superposition bundle per entity; the faithful design is a
     sparse INDEX + pattern-separated, boundary-gated slots + small local bundles (Teyler-Rudy indexing;
     DG/Marr/Treves-Rolls/Leutgeb/Yassa-Stark pattern separation; Baldassano/Michelmann boundary-gated
     storage; Kanerva SDM = the VSA bridge) -- store FHRR codes in DG-separated slots (wires the shelved
     dg_ca3 gate + N400 segmentation; same sparse-code lever as consolidation p2). (b) CONTENT is a
     bag-of-words bundle; the faithful unit is a role-labeled CASE-FRAME (predicate + bound role slots),
     McRae/Ferretti/Amyote 1997 role x filler asymmetry is the behavioural disproof of bag-of-words, SEM
     confirms. Honest scope check: both are genuine fidelity + capacity wins but would NOT move the measured
     end-to-end number, which is front-end-bound -- flag them, do not chase them as a comprehension fix.
   - **The front-end mechanism is now specified (the one lever that DOES move the number):** the brain does
     incremental, weighted-cue constraint-satisfaction, best-formalised as Bayesian log-linear (noisy-channel
     / surprisal): score each NP x role by exp(sum w_i log P_i) over word-order/voice + verb argument-structure
     (PropBank/VerbNet) + animacy + case + thematic-fit (McRae selectional preference) + discourse, graded and
     revisable (MacDonald 1994; McRae/Spivey-Knowlton/Tanenhaus 1998; Levy 2008; Gibson/Bergen/Piantadosi 2013;
     eADM Bornkessel-Schlesewsky). This is the concrete spec for the re-pointed successor problem.
6. **THE LEARNED FRONT-END ORGAN ALREADY EXISTS AND IS ISLANDED (WIRE-DON'T-ISLAND, found while checking
   "are the learning systems integrated?").** `hdlab/thematic_role_labeler.py` is a LEARNED (averaged-
   perceptron) cue-integration role labeler per MacWhinney's Competition Model -- the exact GRADED, LEARNED
   form my hand-built cascade should become -- with a RICHER inventory (AGENT/PATIENT/EXPERIENCER/RECIPIENT/
   GOAL, addressing much of the 104 out-of-scope residual), a real animacy lexicon (`hdlab/animacy_lexicon`),
   228 verb frames, and built-in scramble/ablate controls. It is registered `validated_hard_pass_realderived_
   islanded_2026-08-10` and grep finds ZERO wirings into the live reader -- so the learning IS built, NOT
   integrated. **My hand-built Stage-4 vargs assigner re-derived a worse subset of an organ the substrate
   already has.** HONEST CAVEAT (from its own `exp_thematic_role_labeler_qasrl_modern_revalidation_v1`,
   verdict HARD_FAIL): on MODERN prose (QA-SRL) it is a "disguised single-cue (animacy) rule" -- cue
   integration collapses to animacy alone (best_single_cue animacy_only 0.7127 == full model), strong on
   canonical (0.90) + experiencer (0.89) but failing the hard non-canonical (agent_by_phrase 0.35,
   ditrans_recipient 0.16, passive 0.73). So wiring it is a genuine wire-AND-MEASURE test, not a slam-dunk:
   it should add richer roles + experiencer coverage, but is animacy-dominated and may not beat the hand
   vargs on quotative-heavy McGuffey. The p1 recommendation SHARPENS: the front-end fix is to WIRE + MEASURE
   the EXISTING learned labeler (+ the `hdlab/learner/` package for learned selectional preference), NOT
   build a new extractor. Other islanded learning organs to check for the same debt: `hdlab/learner/*`,
   `role_slot_summarizer.py`, `selection_weighted_sharded_typer.py`, `word_learning_tool.py`.
7. **ACTIVE-INFERENCE UNIFICATION -- HANDOFF to `the_reader_is_feed_forward_where_the_brain_is_predictive`
   (reasoning-pending-lit-VET; the confirming drill is queued for the Aug-28 limit reset).** Probing the
   orphaned foraging gap yielded a cross-cutting finding: reading is ONE active-inference loop (Friston) --
   the brain predicts, and ACTS (chooses what to read) to reduce its own uncertainty -- with a single
   currency: prediction-error reduction = LEARNING PROGRESS (Oudeyer/Gottlieb intrinsic motivation). Under
   it, the apparent zoo of organs are facets at different grains: N400 segmentation (error spikes),
   learning (update where error is high-but-reducible), COMPREHENSIBLE-INPUT/ZPD (read where learning
   progress is maximal), FORAGING/Charnov-MVT (leave when the learning-progress RATE drops below the
   environment average), WSD (resolve to minimise error). **Comprehensible-input and foraging are NOT
   competitors -- the same computation at two grains, and both are the ACTION half of the predictive
   reader's loop.** DIAGNOSIS of why foraging "lost" to the fixed schedule on yield (0.0617 vs 0.0743): it
   was fed the WRONG currency -- words-grounded-per-step (a COUNT) instead of uncertainty-reduction; the
   organ's own docstring pins the currency as value/uncertainty and ships `assert_gain_is_not_a_count` for
   exactly this failure. So foraging cannot be measured correctly until the predictive reader supplies the
   learning-progress signal -- it is DOWNSTREAM of that problem, not a standalone gap. ROUTE: this whole
   cluster (foraging + comprehensible-input + curiosity currency) belongs to the predictive-reader problem;
   do not wire foraging in isolation. `hdlab/information_foraging.py` is correct and brain-pinned (Charnov
   1976; Constantino&Daw 2015; Hayden 2011) -- it is starved of its currency, not broken.

## PROPOSED hdlab CHANGE (NOT landed -- strategy re-verifies + lands, Q111)
Ordered by evidence:
1. **Do NOT wire the downstream organs into the live reader as a comprehension lift yet.** The measured
   end-to-end result says they are swamped by the front-end; wiring them now buys no comprehension and
   would look like progress. (This is the decision-shaping negative the brief asked for.)
2. **If/when content-addressable retrieval IS wired** (it is the pinned resonance mechanism and the right
   default), wire `hdlab/content_addressable_retrieval.py::AdditiveCueRetrieval` as a default-off
   read-path over the situation-model register, and expose the register's per-feature slot codes so it can
   be cued. Land it as capability-neutral infrastructure (native partial-cue, no unphysical collapse), NOT
   as an accuracy claim -- it ties trivial counting on clean cues.
3. **The late-MERGE architecture is validated as the right SHAPE** (forward-computed coherence combined at
   a decision point). But its load-bearing coherence term for the dominant error is thematic-role
   PLAUSIBILITY / verb-argument structure, not topical centrality -- which is a FRONT-END rebuild. File it
   as the re-pointed next problem: a richer-role, plausibility-aware event/role extractor.
4. **N400 monitor:** add a schema/goal prior term to boundary placement (see AUDIT UPDATE 2) before wiring
   segmentation live.

## TLDR
We finally plugged the brain "organs" we'd each proven on their own workbench into the actual reader and
tested whether reading a real passage and answering "who did what" gets better. Answer: on clean,
hand-checked inputs the memory-and-retrieval organs work perfectly -- but run through the reader's own
first step (working out who did what to whom from raw text), the whole thing scores WORSE than a dumb
"just say the most common answer" guess. So the parts are fine; the bottleneck is the first reading step,
and we now know exactly what kind of wrong it is: not "found nothing" but "found something and mislabelled
it" -- mostly getting the doer-vs-done-to backwards between two people. That kind of error needs a smarter
first-read step that understands verbs and plausibility, not more memory machinery bolted on after. We
also confirmed, by reading the actual neuroscience, that the brain does NOT read in one straight pass and
does NOT rewrite everything either -- it does a cheap late "does this fit the story?" check, which we
built and tested; it nudges the right way but is too weak to overcome the mislabelling, for a specific
reason. This is the single most useful thing we could have learned right now: it tells us to invest in a
better first-read step, and the check to find that out cost one experiment.

## QUESTIONS
None.

## NEXT STEPS
1. **THE FRONT-END LEVER IS DEMONSTRATED (Stage 4), AND THE LEARNED ORGAN ALREADY EXISTS -- but the
   front-end/predictive build is ANOTHER SESSION'S ACTIVE PROBLEM: HAND OFF, do not compete.** The problem
   `the_reader_is_feed_forward_where_the_brain_is_predictive` is being worked now and owns the predictive
   front-end AND the QA-SRL data. So p1 does NOT build the front-end fix here. HAND OFF to that problem: (i)
   the front-end is the measured binding constraint (this SOLVED, Stages 0-2); (ii) the Stage-4 vargs
   construction proof that a verb-argument assigner recovers most of the wall (0.48->0.74 CI-separated),
   with the quotative-inversion error class as the biggest single win; (iii) **the learned organ already
   exists and is ISLANDED -- `hdlab/thematic_role_labeler.py` (learned Competition Model, roles incl.
   EXPERIENCER/RECIPIENT/GOAL), with its HARD_FAIL-on-modern-prose animacy-dominance caveat and the
   `hdlab/learner/` package for selectional preference**; (iv) the "batch, not incremental/predictive" +
   "nothing learns" meta-gaps (this SOLVED's machinery audit) are that problem's core. Do NOT run
   QA-SRL/predictive experiments in the p1 lane.
2. Land `AdditiveCueRetrieval` as default-off register infrastructure (pinned resonance, native partial-cue)
   -- capability-neutral, not an accuracy claim. **KEEP FHRR** as the basis (confirmed faithful; SEM/Franklin).
3. **Fidelity + SCALE upgrades (flag, do not chase as a comprehension fix -- they do NOT move this number):**
   sparse/indexed + boundary-gated STORE of FHRR codes (wire the shelved dg_ca3 gate + N400; the consolidation
   p2 sparse-code lever) and a role-labeled CASE-FRAME content unit. Act on these when event-count-bound or
   working the read-half (p2), not for this task.
4. Fold the FIVE AUDIT UPDATEs into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` (composition = late-merge; F5 schema
   gap; E2 end-to-end tie; front-end is the binding constraint; MACHINERY FIDELITY -- FHRR confirmed-keep,
   store/content the FHRR-compatible gaps). Correct the audit's "central binding op unpinned -> our-invention"
   framing to "unpinned at implementation; a defensible published model (SEM)".
5. (Optional, later) Add the schema/goal term to the N400 monitor and re-test boundary PLACEMENT.

---

INTEGRATED_BY_STRATEGY: 2026-08-26 -- EXCELLENT / PARTIAL (owner-DONE). THE DECISIVE result -- picks the next stage.
Full SOLVED re-read FRESH (standing rule). Re-verified scaffold-free FIRST-HAND (test_wire_organs_endtoend.py, 9/9 PASS:
CAR clean event 1.000/role 0.983 > maj 0.781 & ties COUNT; live end-to-end 0.483 < floor 0.781; front-end
misassignment-dominant role 86/entity 50/miss 30/OOS 104; verb-argument front-end 0.483->0.736 > twin 0.438; organs tie
counting on fixed front-end; meaning-cued paraphrase retrieval 0.528 CI-sep vs count 0.217). VERDICT = rigorous
well-attributed NEGATIVE = full PASS: the FRONT-END (event/role extraction) is the binding constraint; the organs work
on CLEAN inputs (localised by the oracle-vs-live contrast) + PARTIAL on meaning/paraphrase cues (Stage 7, after two
caught+retracted overreaches). Stage 4 PROVED the front-end lever (+0.253 end-to-end CI-sep; biggest error = quotative
postverbal speaker). Composition is a late algebraic MERGE (Norris), not a feedforward cascade. FHRR CONFIRMED FAITHFUL
(SEM/Franklin 2020 = HRR+bundling+CLS = our machinery) -> keep; store-organization + case-frame content are the
FHRR-compatible gaps. The learned front-end organ (hdlab/thematic_role_labeler.py, Competition Model, richer roles)
ALREADY EXISTS + is ISLANDED since 08-10 -> the fix is WIRE+MEASURE it, not build new. NO hdlab landed (decision-shaping
negative: do NOT wire the swamped organs as a comprehension lift). 5 AUDIT UPDATEs folded (composition=late-merge; F5
N400 schema gap; E2 end-to-end tie; front-end = binding constraint; machinery -- FHRR confirmed-keep + the correction of
the "binding op unpinned->our-invention" framing to "unpinned at implementation; a published model SEM"). Branch B
(NEXT_STAGE doc) FIRED -> the FRONT-END packaged as the new top-priority problem (wire+measure the existing learned
role labeler; compose the predictive-reader verb-selectional-preference + the relcl filler-gap). Review EXCELLENT +
SOLVER REVIEW in PROBLEM.md; priority cleared. Committed. NOTE: this SOLVED's "hand off to the predictive-reader problem"
is now stale -- that problem was integrated earlier this session; the front-end gets its OWN new problem.
