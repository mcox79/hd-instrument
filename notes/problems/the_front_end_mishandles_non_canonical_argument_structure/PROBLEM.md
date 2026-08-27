---
priority:
review: EXCELLENT
review_text: "Bar MET; re-verified FIRST-HAND (test_noncanonical_role_assigner.py 6/6 PASS). A HYBRID graded cue-competition assigner (MacWhinney/Bates Competition Model over the landed graded_competition organ; learned cue validities) beats the composed front-end on the non-canonical slice CI-separated (0.6000 vs 0.5758, +0.0242 CI[0.0146,0.0343]), NET-POSITIVE overall (+0.0113 CI[0.0064,0.0162]) with CANONICAL PRESERVED (-0.001 NOT_SEP), shuffled-validity twin LOSING (+0.3843), seed-robust. Gain attributed to graded integration (COMPETITION-DISCRETE +0.051; drop-robust-voice -0.439 = the dominant lever; drop-gap -0.020). KEY ARCHITECTURAL FINDING: a FLAT integrator is NET-NEGATIVE (canonical -0.041, relcl 0.85->0.55) -> the faithful Competition Model ROUTES (word-order stays high-validity, overridden only on marked cues), it does NOT replace the cascade. Deep drills (past the brief, all controlled): the 408 bucket is 95.6% REACHABLE (mechanism gap, ~60% relativizer-less reduced object-relatives, not noise); verb-subcat SUPPLY bound CI-proven (transitivity cue monotone in corpus exposure, +0.108 on well-attested) then BROKEN with WordNet verb frames (coverage 30->99%); the incremental-parser+reanalysis architecture route is a RIGOROUS NEGATIVE, root-caused to (a) meaning-representation quality (the reanalysis trigger; oracle-trigger restores canonical -> operation right, signal weak = 12-dim grounded ceiling), (b) parser sophistication on long sentences (NOT a memory/buffer bound), (c) an unwired coref organ (~25%). Exemplary honesty: WITHDREW its own '~7 points from coref' claim when the anti-gaming twin showed real coref BELOW a random-antecedent twin. HONEST modest magnitude (slice 0.576->0.600, overall 0.739->0.751). NO hdlab landed; the v2 HYBRID graded_role_assigner (default-off, routed) is EARNED proven-ready."
---

> ## SOLVER REVIEW -- EXCELLENT (integrated 2026-08-27 by the strategy session)
> **Re-verified FIRST-HAND, scaffold-free:** strategy ran `verification/test_noncanonical_role_assigner.py` -> 6/6 PASS
> (held-out test n=4078, split by sentence). Confirmed: HYBRID 0.6000 beats the front-end 0.5758 on the non-canonical
> slice (+0.0242 CI-sep, paired lo 0.0146), shuffled-validity twin loses (0.2157, +0.3843), canonical preserved
> (-0.001 NOT_SEP), net-positive overall (+0.0113 CI-sep), robust voice recall 0.73->0.76, `passive_weak` learned NEGATIVE
> (-2.99). **Bar MET.** **Adversarial audit passed and the submission is a model of rigor:** (1) the brain-faithful
> mechanism is the routed Competition Model (graded learned cue integration over the landed `graded_competition`, where
> morphology/voice override word order ONLY on marked cues) -- the FLAT-integrator net-negative control proves routing is
> the fidelity lever, not "replace the cascade"; (2) attribution is clean (graded integration +0.051 over the discrete
> rule; robust voice is the dominant lever); (3) the deep drills localise the true residual with rigorous negatives -- the
> reduced-relative ceiling is a verb-subcat SUPPLY bound (CI-proven, monotone in exposure) BROKEN with WordNet frames, and
> the remaining wall is ARCHITECTURE (incremental predictive parsing + reanalysis) whose bottleneck is meaning-rep quality
> (the reanalysis trigger), parser sophistication, and an unwired coref organ; (4) the incremental-reanalysis route was
> tested and is a rigorous root-caused NEGATIVE (net-negative, not shipped); (5) **the solver WITHDREW its own '~7 points
> from coref' overclaim when the anti-gaming twin caught it (real coref below a random-antecedent twin)** -- the discipline
> working exactly as intended. **Honest modest magnitude** (not inflated). **hdlab:** NO file landed (Q111); the DEPLOYABLE
> v2 HYBRID `graded_role_assigner` (robust graded voice + relativizer-less gap + cue-support builder + graded competition
> over `graded_competition.net_activation`/`map_pick` with offline-fit validities; wired as a HYBRID route inside
> `resolve_patient`, default-OFF, canonical byte-identical on confident routes) is EARNED proven-ready. Do NOT: flat-replace
> the cascade; wire the incremental-reanalysis route or blind pronoun resolution (both net-negative); trust the weak
> participle cue; claim coref recovery without a cross-sentence gold. AUDIT UPDATE folded. Completes the FRONT-END fix (p1);
> the true residual routes to meaning-supply + coref + the incremental structure-builder (existing lines).

# PROBLEM: the composed front-end reads who-did-what well on canonical sentences but COLLAPSES on non-canonical argument structure (reduced relatives, fronting, and ~26% of passives it fails to detect) -- the reversible cases where word order misleads

**slug:** `the_front_end_mishandles_non_canonical_argument_structure` - **opened:** 2026-08-27 by the strategy session
(surfaced by the CONSOLIDATION measurement: the composed front-end scores 0.739 vs a 0.519 positional floor on the
role-balanced gold, CI-separated -- BUT the pre-verbal/reversible slice is only 0.582, and a per-construction drill
localised WHY).
**status:** OPEN - **a NEW-MECHANISM problem (parallel-solver-appropriate): how does the brain assign roles when word
order is misleading? The consolidation's WIRING is the strategy session's job; discovering the faithful assigner for
non-canonical structure is yours.**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. This is the measured headroom on the front-end
> (the proven binding constraint), and it is a genuine brain-mechanism gap (not wiring). Re-rank per the owner.

> **If a tool call is denied, STOP and report the exact denial text verbatim. Do not retry a variant.**

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

When a sentence is in the normal order ("the lawyer chased the doctor"), our reader works out who-did-what well. But when
the order is REVERSED or the structure is unusual -- a passive ("the doctor WAS chased"), a reduced relative ("the doctor
CHASED by the lawyer collapsed"), a relative clause ("the doctor that the lawyer chased"), or a fronted object -- it often
picks the wrong participant, because it falls back to "the thing after the verb is the patient." On a fair, role-balanced
modern test the reader hits 74% overall but only 58% on these reversed cases, and on a specific bucket of ~400 odd
constructions it is almost always wrong (8%). The question is: how does the BRAIN correctly assign who-did-what when word
order is misleading, and can we build that operation?

## 2. WHY THIS ONE

- **It is the measured headroom on the front-end, the PROVEN binding constraint.** The composed front-end already beats
  the positional floor CI-separated (0.739 vs 0.519); the remaining loss is concentrated in non-canonical structure.
- **It is a genuine brain-mechanism gap, not wiring** -- exactly what a parallel solver should own while the strategy
  session composes the landed organs.
- **The lever is known in KIND (learned graded cue integration -- MacWhinney's Competition Model), but the faithful
  mechanism for reduced relatives / fronting / robust voice is UN-BUILT here** -- the current substrate uses hand rules
  (a strict BE-aux+participle passive detector, a narrow relativizer gate) that miss these constructions.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** role assignment is GRADED, PARALLEL cue integration (MacWhinney/Bates Competition Model: cues -- word order,
morphology/voice, animacy, agreement -- compete by LEARNED validity; English is order-dominant BUT morphology/voice
OVERRIDE order on non-canonical structure). The discrete rule is the noise->0 limit of this graded competition (the
substrate's `hdlab/graded_competition.py`). Non-canonical structure is detected by MORPHOLOGY (participle -ed/-en, aux)
and FUNCTION WORDS (relativizers), NOT by position -- posit the gap/patient where the morphology says, overriding order.

**OUR-INVENTION-UNDER-TEST (mark each; sweep, don't adopt):** the exact cue set + learned validities; how morphology/voice
detection is made robust (the current `precise_passive` requires BE-aux+participle and misses got/being/reduced passives --
recall 0.742); the coverage of reduced relatives ("the book WRITTEN by...") and fronting. COPY the operation (graded
learned cue competition where morphology overrides order); SWEEP the params. Reuse `hdlab/graded_competition.py`
(the graded competition) + `hdlab/thematic_role_labeler.py` (the learned Competition-Model labeler); do NOT hand-patch
`precise_passive` with more if/else (that is the cheap thing -- the faithful method is learned graded cue validity).

## 4. MEASURED vs INFERRED

**MEASURED (consolidation, 2026-08-27; `data/role_balanced_comprehension_gold_v1/`):** the composed front-end
(`resolve_patient`: voice + word-order + relcl) on the role-balanced gold (n=8225, positional floor 0.5191) = **0.7387
[0.729,0.748], +0.2118 CI-sep over the floor**, twin 0.296 losing. **The pre-verbal (reversible) slice = 0.582** (post
0.875). Per-construction drill: gold-passive pre-verbal (n=3595) -- `precise_passive` RECALL only 0.742, acc 0.626 (0.802
where detected); relcl-gate object-relatives (n=44) acc 0.773 (the relcl organ WORKS where it fires); **"other pre-verbal"
(n=408) acc 0.076** (reduced relatives, fronting, missed relativizers -> defaults to the wrong post-verbal pick).

**INFERRED / OPEN (this problem):**
- Does a brain-faithful LEARNED graded cue-integration assigner (morphology/voice overriding order, Competition Model)
  beat the current composed front-end on the pre-verbal / non-canonical slice CI-separated, with an info-free twin
  (shuffled cue validities) LOSING?
- What is the faithful detector for reduced passives / reduced relatives / fronting (the 408 + the 26% undetected
  passives)?

## 5. ALREADY TRIED / DO NOT RE-RUN

- Do NOT hand-patch `precise_passive` with more surface rules -- that is the cheap thing; the faithful method is learned
  graded cue validity (Competition Model). A rule pile is not the mechanism.
- Word order DOMINATES canonical English role assignment (the_live_front_end SOLVED, MacWhinney/Bates/Kliegl PINNED) --
  do NOT re-derive that; the gap is specifically NON-canonical structure where morphology/voice must OVERRIDE order.
- The relcl object-gap resolver WORKS where it fires (0.773) -- do NOT rebuild it; extend COVERAGE (reduced relatives,
  missed relativizers) and the voice-recall.
- Query `experiment_index.py query "role"`, `query "competition"`, `query "passive"`; read `the_live_front_end...` +
  `discrete_where_the_brain_is_graded...` SOLVEDs + `hdlab/thematic_role_labeler.py` + `hdlab/graded_competition.py`
  + `hdlab/relcl_resolver.py` BEFORE building.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Reproduce the headroom: run `experiments/exp_composed_reader_role_balanced_measure_v2.py --smoke` and the STEP-10
  per-construction drill (LOG STEP 10) -- confirm the pre-verbal slice + the 408-case bucket + the 0.742 passive recall.
- Read `hdlab/relcl_resolver.py::precise_passive` (the strict BE-aux+participle voice cue) and `resolve_patient` (the
  arms) -- confirm WHERE non-canonical structure falls through to the two-line default.
- Recompute every floor on the role-balanced gold's OWN population (positional 0.519; the composed front-end 0.739;
  the pre-verbal slice 0.582). NO number crosses populations.

## 7. THE BAR

A brain-faithful LEARNED graded cue-integration assigner (morphology/voice overriding word order; Competition Model)
must, on the role-balanced gold's PRE-VERBAL / non-canonical slice:

- **Beat the current composed front-end (`resolve_patient`, 0.582 on the pre-verbal slice) CI-separated over its UPPER
  bound, with an info-free twin (SHUFFLED cue validities / deranged weights) LOSING CI-separated.** Report CI half-width
  + null p95. Attribute the gain to the graded cue integration (ablate to the discrete order+voice rule).
- **AND/OR** raise voice-detection RECALL (currently 0.742 for passives) and reduced-relative/fronting coverage
  (the 408-case bucket at 0.076) CI-separated, twin losing.
- **DECISIVE EITHER WAY:** it beats the current front-end on non-canonical structure -> propose the hdlab wiring
  (strategy lands it). It does NOT -> a rigorous negative that localises whether the residual is data (annotation noise
  in the pre-verbal slice) or a deeper representation gap.

## 8. FILES AND ENTRY POINTS

- `hdlab/thematic_role_labeler.py` (the learned Competition-Model labeler) + `hdlab/graded_competition.py` (graded cue
  competition) + `hdlab/relcl_resolver.py` (voice + object-gap). `data/role_balanced_comprehension_gold_v1/` (the fair
  gold) + `experiments/exp_composed_reader_role_balanced_measure_v2.py` (the measurement to beat).
- Prove in `experiments/` + `verification/`; propose the hdlab diff in `SOLVED.md` (strategy lands it, Q111). **Do NOT
  write `hdlab/`.**

## DO NOT QUOTE / DO NOT REDO

- Do NOT hand-patch surface passive rules; the mechanism is learned graded cue validity.
- No number crosses populations -- recompute floors on the role-balanced gold's pre-verbal slice.
- Word-order dominance on CANONICAL English is settled; this is about NON-canonical structure.
