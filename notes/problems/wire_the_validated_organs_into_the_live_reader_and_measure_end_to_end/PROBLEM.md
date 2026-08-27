---
priority:
review: EXCELLENT
review_text: "Integrated PARTIAL/EXCELLENT 2026-08-26 (owner-DONE) -- the DECISIVE result that picks the next stage. A rigorous, well-attributed NEGATIVE = a full PASS per the bar. Re-verified scaffold-free first-hand (test_wire_organs_endtoend.py, 9/9 PASS). Composed 3 validated organs into a real McGuffey entity-role reading task, organs OFF vs ON, identical inputs. VERDICT: the FRONT-END (event/role extraction) is the binding constraint -- end-to-end 0.483 [0.410,0.556] BELOW the trivial majority floor 0.781, while the SAME organs on CLEAN/oracle inputs hit event 1.000 / role 0.983 CI-separated over the majority floor AND the exact-key live baseline (twin loses) -- the oracle-vs-live contrast localises the wall to the front-end, not the organs. Error taxonomy: MISASSIGNMENT-dominant (role 86 > entity 50 > miss 30; 104 OUT-OF-SCOPE roles). Stage 4 PROVED the lever: a brain-faithful verb-argument role assigner lifts end-to-end 0.483->0.736 CI-separated (biggest error class = quotative/dialogue postverbal speaker). TWO caught+RETRACTED overreaches (Stage 5 'organs add nothing'; first Stage 6 'meaning supply fails') -> Stage 7 clean instrument shows content-addressable MEANING retrieval DOES recover lexically-disjoint paraphrase cues (0.528 CI-sep vs collapsed count 0.217) -- REAL but PARTIAL. Composition is a late algebraic MERGE (Norris) not a feedforward cascade. FHRR CONFIRMED FAITHFUL (SEM/Franklin 2020 uses HRR+bundling+CLS = our machinery) -> keep it; store-organization (sparse/indexed) + case-frame content are the FHRR-compatible fidelity gaps. KEY: the learned front-end organ (hdlab/thematic_role_labeler.py, Competition Model, richer roles) ALREADY EXISTS + is ISLANDED since 08-10 -- the fix is WIRE+MEASURE it, not build new. Grade EXCELLENT (decisive attribution, error taxonomy, self-retractions, brain-fidelity drills). NO hdlab landed (the decision-shaping negative: do NOT wire the swamped organs as a comprehension lift). Branch B fired -> front-end packaged as the new top problem."
---

# PROBLEM: we have a SHELF of validated brain organs proven only in ISOLATION -- compose them into the LIVE reader and measure END-TO-END, because a functional brain is the parts WORKING TOGETHER, not a pile of parts that each pass alone

**slug:** `wire_the_validated_organs_into_the_live_reader_and_measure_end_to_end` - **opened:** 2026-08-26 by the strategy session
(owner-directed 2026-08-26: *"is everything integrated, tied together, and have we tested it end to end?"* -> the honest
answer is NO -- everything is landed off-path / default-off / synthetic-proof-only. This begins the WIRE-AND-MEASURE phase.)
**status:** OPEN - **a PHASE PIVOT: from building isolated parts to composing + measuring the whole reader**

> **PRIORITY NOTE (the call is the strategy session's):** filed at `1`. Every recent submission ends with the same
> caveat in its own words -- *"synthetic construction proof; measure on the LIVE task before any capability claim."* We
> have accumulated many validated brain-faithful organs (event-segmentation, feature-similarity meaning, content-
> addressable retrieval, a recollection gate) and NONE is wired into the live reader; the composed system's comprehension
> has never been measured. That is the accumulating WIRE-DON'T-ISLAND debt, and closing it is now the highest-leverage
> work -- more valuable than another isolated part. Relates to p6 (`the_meaning_win...`, a narrower meaning-read-out
> wiring); this brief is the general composition + end-to-end measurement.

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

We have built a shelf of brain-faithful organs and proven each one WORKS -- but each on its own little test bench, never
plugged into the actual reader, and never measured together. A brain is not a parts bin; it is the parts WORKING
TOGETHER. So the honest question, unanswered: **when we plug the validated organs into the live reader and read a real
passage, does comprehension actually get better?** This brief composes 2-3 validated organs into the live reading
pipeline (behind flags) and measures the WHOLE reader end-to-end against today's baseline. A clear win means the parts
compose into comprehension. A clear, well-diagnosed LOSS is just as valuable -- it tells us whether the reader's weak
front-end (event extraction ~0.32) is the wall that swamps everything downstream, which is the single most important
thing we could learn right now.

## 2. WHY THIS ONE

- **It is the phase we are actually in.** The deep-foundational PARTS are largely built and validated; the mission
  (a functional brain) now needs them COMPOSED and MEASURED, not more isolated pieces.
- **It closes the WIRE-DON'T-ISLAND debt directly.** Every organ is landed default-off / off-path with an explicit
  "measure on the live task before any capability claim." This is that measurement.
- **The answer is decision-shaping either way.** WIN -> wire it into the live substrate (strategy lands it, Q111).
  LOSS -> we learn the binding constraint (almost certainly the front-end), which re-points the whole programme.

## 3. HOW THE BRAIN DOES THIS (frame + discipline)

**PINNED:** the brain reads as a PIPELINE of these operations composed, not in isolation -- perceive/parse -> assign
meaning (ATL feature-similarity + associative) -> segment events at prediction-error boundaries (N400 / EST) -> write
the event's bindings to a situation-model store -> retrieve by a partial cue (content-addressable / cue-based). The
COMPOSITION (each stage feeds the next) is the brain's architecture; the organs you are wiring each already replicate
their stage's operation.
**OUR-INVENTION-UNDER-TEST:** the exact wiring points, the flags, and WHICH subset composes best first. COPY the
COMPUTATION (compose the validated stages into one live pipeline); SWEEP the PARAMETER (which organs, wiring points,
flag settings, and the end-to-end task).

**Corpus-age note (MIND IT):** the live reading corpus (McGuffey) is ~200 years old; archaic-learned meaning scored on
modern gold is a mismatch. Prefer a graded-reader / modern-text comprehension harness, or hold corpus era fixed across
baseline and treatment so the composition -- not the corpus -- is what varies.

## 4. MEASURED vs INFERRED

**MEASURED (re-verified, per organ, in ISOLATION):** each organ beats its own floor on its own synthetic instrument --
N400 segmentation (within-event recovery 0.988 vs 0.52/0.44), feature-similarity whitening (SimLex/SimVerb, distinctive
beats raw CI-separated), content-addressable additive retrieval (0.991 vs 0.287 under a partial cue), the DG/CA3
recollection gate (self-certifies, beats the counting floor). These are construction proofs on purpose-built benches.
**INFERRED (the deliverable, decisive either way):** whether COMPOSING 2-3 of them into the LIVE reader improves
comprehension END-TO-END over today's baseline on identical inputs -- untested for every organ. The live reader's
front-end (event-extraction recall ~0.32) may be the binding constraint that swamps the downstream organs; that is the
hypothesis this brief must confront and attribute, not assume.

## 4b. THE VALIDATED ORGANS ON THE SHELF (LANDED + importable unless noted)

- `hdlab/n400_coherence_monitor.py` -- **event segmentation** (graded content prediction error vs a running gist, EST
  boundary). Wire: post an N400 boundary -> advance the situation-model event slot, vs the current fixed segmentation.
- `hdlab/grounded_similarity.py::distinctive_grounded_similarity` -- **feature-similarity ("alike-in-kind") meaning
  read-out** (distinctive-feature whitening). Wire: use it (or a FIXED fusion with the associative rep -- NOT a
  task-switch gate, which was refuted) where the reader assigns/compares word meaning.
- `hdlab/dg_ca3_recollection_gate.py` -- **self-certifying recollection gate** (DG separation + CA3 completion
  confidence). Wire: route which memory to trust / when to accept a retrieval.
- `hdlab/content_addressable_retrieval.py::AdditiveCueRetrieval` -- **content-addressable ADDITIVE retrieval** (LANDED
  2026-08-26): add items as per-feature FHRR codes, retrieve by a PARTIAL cue via additive Lewis-Vasishth activation
  (argmax). Import it and feed it the register's per-feature slot codes (entity/event/role). Use ADDITIVE activation, NOT
  a multiplicative composite-key match (which orthogonalises on one wrong feature); fan penalty DEFAULT-OFF (regime-
  specific). *(Extending the live register to STORE per-feature codes + a `decode_cue` on the register itself is the
  separate downstream wiring strategy still owes; this organ is the algorithm, ready to compose.)*
- **THE FREQUENCY PRIOR (most-frequent-sense) as the reader's sense default -- NOT-YET-LANDED, needs a build first**
  (added 2026-08-26 from `the_meaning_win_is_offline_context_free_and_unwired`, integrated PARTIAL). That submission
  proved the frequency prior (Duffy & Rayner reordered-access) beats the uniform floor CI-separated on the WSD
  instrument (MFS 0.4637 vs 0.3995) and is the ONLY meaning-selection signal that works -- but it is UNWIRED because the
  live reader is SENSE-BLIND (`ConceptSpace` superposes all senses of a lemma into ONE blended vector, so it has no
  per-sense representation to default over). Wiring it is therefore a real BUILD (give the reader per-sense
  representations + an MFS default), NOT a flag flip -- and it must be MEASURED downstream here before any capability
  claim (measure-before-capability-claim; the WSD-instrument win does NOT transfer automatically). ⚠️ Do NOT wire any
  CONTEXT-conditioning channel for sense-selection (grounded or associative): none beat the prior on this corpus, and
  context OVERRIDING frequency is DATA-limited (needs a modern WSD benchmark, none on disk). This is the disciplined
  home for that wiring -- captured here, gated on this brief's end-to-end number, rather than spawned as one more
  isolated-part problem.
- **THE FILLER-GAP ROLE-ASSIGNMENT FIX (front-end) -- validated 2026-08-26 (`the_relcl...` integrated SOLVED), NOT-YET-LANDED.**
  For reversible non-canonical clauses ("the doctor that the lawyer chased") the current front-end fails: the two-line
  rule gets ~half wrong and the general `arc_parser` is HARMFUL (0.198 < a random twin). The fix is a specialised
  incremental filler-gap resolver over UPOS + closed-class relativizers (NO arc graph, ~30 lines), gated by two
  conditions (attached relativizer + empty object slot) so it never fires on canonical clauses -- 0.953 on the hard
  regime, oracle-level. **Wire it AROUND `arc_parser` (do not route role assignment through the arc parse), as TWO
  ALWAYS-ON competing scorers + a route-CONFLICT term (not an if/else gate -- the conflict is a gold-free "am I in
  trouble" signal), NOT the naive gate.** ⚠️ Its aggregate real-text lift is ~0 (genuine reversibles are <1% of text) --
  land it for CORRECTNESS on the rare hard sentences a situation model needs, and the center-embedding residual is the
  RETRIEVAL half (route to the same content-addressable mechanism above -- filler-gap role binding IS cue-based retrieval).
- Existing subsystems it plugs into: `hdlab/situation_model_multibank.py` / `situation_model_accumulate.py` (the register),
  `hdlab/reading_grounding_loop.py` (the live read loop), `hdlab/meaning_fusion.py` (the general meaning read-out),
  `hdlab/situation_reader.py` / `thematic_role_labeler.py` (stage-1 role assignment — the filler-gap wiring target).

## 4c. THE SEQUENCING PRIOR (strategy, brain-foundational -- START HERE, then sweep)

You may compose any subset, but the strategy session gives you a grounded ORDER rather than a blind sweep, because the
brain-foundational audit already ranks the deviations. **LEAD WITH THE RETRIEVAL ARCHITECTURE.** It is the audit's
**#1 LIVE deviation** (`BRAIN_FOUNDATIONAL_AUDIT.md` §5 #3: *"we query the WRONG memory"* -- the live reader stores +
retrieves by EXACT-KEY HASH and has NO partial-cue path; the brain separates into slots (DG) and retrieves
CONTENT-ADDRESSABLY from a partial cue (CA3), then reads the CONSOLIDATED store). **THREE independent integrations
(binding, content_addressable, cortical_store) each re-located their fix to this SAME cluster** -- it has the widest
blast radius on the shelf. Concretely, the FIRST end-to-end measurement:
- Extend the live register to STORE per-feature slot codes and RETRIEVE via `content_addressable_retrieval.AdditiveCueRetrieval`
  (additive Lewis-Vasishth), replacing the exact-key hash route -- measured on a CROSS-EVENT / PARTIAL-CUE query task
  (answer a question whose cue is degraded / spans events), vs the exact-key baseline on identical inputs.
- Route which retrieval to trust through `dg_ca3_recollection_gate` (the self-certifying confidence).
**This ALSO doubles as the front-end attribution test:** if wiring brain-faithful retrieval onto the current ~0.32
event-extraction front-end shows NO end-to-end gain, that is the decisive evidence that the FRONT-END is the binding
constraint (the single most important thing to learn) -- a well-diagnosed loss, not a failure. THEN, as follow-on
compositions: N400 segmentation -> event-slot advance; the feature-similarity / frequency-prior meaning read-out.
**COUPLED PROBLEM — NOW INTEGRATED (2026-08-26, SOLVED/EXCELLENT):** `resolve_retrieval_interference_among_similar_memories`
(the fan effect) is the SAME content-addressable machinery from the interference side, and it delivered the concrete
retrieval detail you need: **add the encoding CONTEXT as one more per-item feature to `AdditiveCueRetrieval`** (it is
already feature-agnostic — no organ change). On the synthetic instrument, `content + w_ctx·context` resolves
similar-competitor interference CI-separated (0.928 vs 0.400 at 8 competitors), leak-safe, while still EXHIBITING the
residual fan effect and correctly COLLAPSING when context is non-separable. **So the retrieval composition you wire is:
per-feature slot codes {entity,event,role,CONTEXT} → additive Lewis-Vasishth retrieve, with the CONTEXT sourced from
the situation-model / reading-loop context vector in its GRADED form (`context_vector(graded=True)`, NOT the sign()
default — sign makes context lossy).** THE LOAD-BEARING OPEN QUESTION this brief must answer: is the substrate's ACTUAL
context separable across genuinely similar memories? (the synthetic boundary shows the mechanism collapses when it is
not — so measure it, do not assume it). A fixed w_ctx; NO multiplicative gate, NO ACT-R fan penalty, NO per-trial
diagnosticity weighting (a soft oracle). Do the mechanism (done); prove it end-to-end HERE.

## 5. ALREADY TRIED / KNOWN (do not re-derive)

- Each organ's ISOLATED win is DONE and re-verified -- do NOT re-run the synthetic construction proofs; this brief is the
  COMPOSITION + the LIVE end-to-end measurement, which none of them did.
- Known rigorous negatives to NOT re-open: a semantic-control task-SWITCH loses to fixed fusion (use fusion); DG pairing +
  CA3 iterative settle are un-earned for retrieval (1-step additive match suffices); selective replay does not beat plain
  replay; the sign()/format read-out family is refuted. (See BRAIN_FOUNDATIONAL_AUDIT.md §2b.)
- The live reader's event-extraction recall is ~0.32 and is the suspected binding constraint -- prior isolation tests
  avoided it deliberately. Here you must CONFRONT it: measure end-to-end AND attribute where the signal is lost.
- `tools/experiment_index.py query "<kw>"` (single keywords) for prior end-to-end reading measurements; read
  `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (all the organ entries) + `notes/STATUS.md` first.

## 6. VERIFY BEFORE YOU START (the disk outranks this brief)

- Confirm the organs import and run on the live read path, and find the exact CURRENT baseline: what the live reader does
  today at each stage (fixed segmentation? exact-key retrieval? which meaning read-out?), and its current end-to-end
  number on your chosen comprehension harness.
- Pick a comprehension task where the composed organs SHOULD help and the front-end does NOT wholly determine the score
  (e.g. cross-event / cross-sentence query answering, coreference-under-partial-cue, or a situation-model probe) -- and
  recompute the strongest floor on that task's population.
- Build the composition behind FLAGS so baseline (organs off) and treatment (organs on) run on the IDENTICAL inputs, so
  only the wiring varies (the attributable design).

## 7. THE BAR

On a REAL reading/comprehension task (not a synthetic organ instrument), inputs held identical between arms, floor
recomputed on its population: **the composed pipeline (2-3 validated organs wired ON) must beat the current live baseline
(organs OFF) CI-separated over the strongest floor's UPPER bound, with the info-free twin (scrambled wiring / shuffled
organ outputs) LOSING CI-separated**, CI half-width + null p95 reported. Attribute the effect PER ORGAN (ablate each).
**DECISIVE EITHER WAY:**
- **WIN** -> the parts compose into comprehension; strategy wires it into the live substrate (default-off flags first),
  and we have our first end-to-end capability number. Name which organs carried it.
- **RIGOROUS NEGATIVE (a full PASS)** -> the composition does NOT beat baseline. Then DIAGNOSE it with controls: is the
  front-end (event extraction ~0.32) the binding constraint that swamps the organs (feed the organs CLEAN/oracle inputs
  and show they help THERE but not through the noisy front-end)? Is one organ's contribution real but masked by another?
  A well-attributed "the parts are validated but the front-end is the wall, here is the evidence" is the single most
  valuable finding available right now -- it re-points the whole programme to the front-end. **State the denominator and
  do not cross scorers/populations.**

## 8. FILES AND ENTRY POINTS

- The organs in §4; the live read loop `hdlab/reading_grounding_loop.py`; the register
  `hdlab/situation_model_multibank.py` / `situation_model_accumulate.py`; `hdlab/meaning_fusion.py`.
- `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b (every organ's entry + the "measure on the live task" caveats) + the tiers it
  touches (Tier 2 meaning, Tier 3 register/N400, Tier 4 memory). Report any correction as an **AUDIT UPDATE**.
- Build the composition + measurement in `experiments/` + a scaffold-free witness in `verification/`; propose the hdlab
  wiring diff in `SOLVED.md` (strategy lands it, Q111). Do NOT write `hdlab/`.

## DO NOT QUOTE / DO NOT REDO

- Do NOT re-run the isolated construction proofs as if they were the deliverable -- the deliverable is the LIVE end-to-end
  composition number.
- Do NOT wire a semantic-control task-SWITCH (refuted -> fixed fusion), the ACT-R fan penalty (regime-specific), DG-by-
  default, or an attractor on a flat read (all un-earned/refuted).
- Do NOT claim a capability from a synthetic arm -- the number that counts is measured through the LIVE reader on the
  identical inputs as the baseline.
- No number crosses the isolated instruments and the live task -- recompute the floor on the live population.

---

## SOLVER REVIEW (strategy session, 2026-08-26 — INTEGRATED, owner-DONE — the DECISIVE result)

**Grade EXCELLENT. Verdict PARTIAL** (a rigorous, well-attributed negative that DIAGNOSES + PROVES the lever = a full
PASS per the bar). Re-verified scaffold-free first-hand — `test_wire_organs_endtoend.py` 9/9 PASS, every load-bearing
claim reproduced (organs 1.000 clean / 0.483 end-to-end below the 0.781 floor; misassignment-dominant; the verb-argument
front-end moves 0.483→0.736; meaning retrieval recovers paraphrase cues where counting is blind).

**Why EXCELLENT — this is the model of what a wire-and-measure should be.** (1) It answered the brief's "single most
valuable finding" decisively: the oracle-vs-live contrast LOCALISES the wall to the front-end (the organs are not broken;
they hit 1.000 clean and collapse only through the noisy front-end). (2) The error taxonomy (miss vs misassign-role vs
misassign-entity vs out-of-scope) — a re-labelling of output already produced — turned "the front-end is the wall" from
an assertion into an attributed finding, and named the mechanism (quotative/dialogue postverbal speaker → verb-argument
structure). (3) It didn't stop at the diagnosis — Stage 4 BUILT the fix and moved the end-to-end number +0.253
CI-separated. (4) It caught and RETRACTED **two** of its own overreaches (Stage 5 "organs add nothing"; first Stage 6
"meaning supply fails"), each killed by a can-fail control, not by re-reading its own numbers — and Stage 7's clean
instrument recovered the real, partial meaning-recognition capability. (5) A literature dive OVERTURNED the brief's own
PINNED composition claim (reading is a late algebraic MERGE, Norris, not a feedforward cascade). (6) A machinery-fidelity
drill CONFIRMED FHRR faithful (SEM/Franklin 2020 — a peer-reviewed brain event-memory model — binds role→filler with
HRR + bundling + a CLS split: our exact machinery), and found the real FHRR-compatible gaps (sparse/indexed store,
case-frame content). (7) WIRE-DON'T-ISLAND discipline exposed that the learned front-end organ ALREADY EXISTS
(`hdlab/thematic_role_labeler.py`, Competition Model, richer roles) and is islanded — so the fix is wire+measure, not
rebuild; its Stage-4 hand-cascade honestly re-derived a worse subset.

**Effect on the programme — this SELECTS the next stage (Branch B, `NEXT_STAGE_after_wire_and_measure.md`).** The
front-end is the measured binding constraint; the downstream memory organs are validated (partial on meaning cues) but
do not move the aggregate on this task. So the next build is the FRONT-END: wire + measure the existing learned
Competition-Model role labeler (richer roles for the 104 out-of-scope; graded constraint-satisfaction over its
animacy-dominance HARD_FAIL), composing the already-integrated verb-selectional-preference (predictive reader) and the
filler-gap resolver (relcl) for the two-animate residual. Packaged as the new top-priority problem.

**No hdlab landed this integration** (Q111) — the decision-shaping negative is explicit: do NOT wire the swamped organs
as a comprehension lift. AudIT UPDATEs folded into `notes/BRAIN_FOUNDATIONAL_AUDIT.md` §2b + the binding/§8/§1 corrections.
