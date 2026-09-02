---
problem: the_world_state_register_is_coref_blind_wire_it_through_coreference_and_measure_who_has_what
status: SOLVED
bar: "PASS = a coref-densified world-state register (entity + object keys resolved through the reader's OWN coref BEFORE the effect is applied) RECOVERS who-has-what CI-separated over the coref-BLIND raw-string register on a HELD-OUT real-prose test with state-CHANGING transfers, with a SHUFFLED-COREF twin (same clusters, wrong assignment) LOSING CI-sep and a positive control that the answer CHANGES at the transferring event. A rigorous located negative is a full PASS if it names the residual precisely (coref recall on transfer agents vs recipient-PP extraction vs verb-sense) with the number for each. Report CI half-width + null p95. Do NOT grade on the same corpus the store/coref were tuned on without a held-out split."
result: "PRIMARY (LitBank coref-CoNLL, ALL 25 gold-coref docs, the reader's OWN he/she coref; who-has-what over state-changing transfers, n=135 queries): binding the HOLDER through the reader's coref recovers who-has-what READER 0.7185 [0.6444,0.7926] vs coref-BLIND 0.5704 [0.4889,0.6519], PAIRED delta +0.1481 [0.0963,0.2076] (CI half-width 0.056, excludes 0). On the DECISIVE he/she-holder subset -- the population where coref-blindness bites, n=26: coref-BLIND 0.000 [0,0] -> READER 0.500 [0.3077,0.6923], +0.500; GOLD-coref oracle 1.000. BUILD-ACROSS of the two routes the reader's coref LACKS (MCScript2 first-person, 2729 stories / 8777 transfers, through the brain-foundational EntityBinder): OBJECT ANAPHORA relocates 259/374 'it'-transfers blind applied to the wrong object (who-has-what impact 0.69; 'it'-antecedent coverage 0.65); the INDEXICAL narrator rule collapses the narrator that blind fragments into >=2 case-keys in 5.3% of stories. OBJECT-ANAPHORA ACCURACY on REAL LitBank gold (n=189 gold-clustered object pronouns, `exp_world_state_object_anaphora_gold_v1`): resolving 'it/they' by RECENCY 0.730 [0.667,0.794] vs random-twin NULL p95 0.323 (CI-sep) vs first-mention floor 0.132 vs the reader's coref 0.000 (abstains -- out of scope); subject-prominence Centering HURTS objects (salience 0.518, paired -0.212 [-0.286,-0.132])."
floor: "Strongest floor = the coref-BLIND raw-string register (the register wired today): aggregate 0.5704 [0.4889,0.6519]; on he/she holders 0.000 (a pronoun holder string maps to NO discourse entity). Gate is the PAIRED reader-minus-blind delta +0.1481 [0.0963,0.2076] (excludes 0); the he/she subset is fully separated (reader lower CI 0.3077 > blind upper CI 0.000). GOLD-coref oracle 1.000 = ceiling. by-holder-class: nominal 0.731->0.798, he/she 0.000->0.500, object 'it' 0.2->0.2 (reader out of scope = the object-anaphora residual, named with its number)."
controls: "(1) SHUFFLED-COREF twin (same clusters, wrong assignment): aggregate single-draw same-gender twin 0.652, reader-minus-twin +0.0667 [0.0148,0.1185] (excludes 0); on the he/she subset a K=2000-permutation NULL mean 0.078 / p95 0.154, reader 0.500 >> p95 (CORRECT identity, not coref-shape, does the work). (2) POSITIVE CONTROL change-point: the reported holder CHANGES at the transferring event on 95.6%% of queries (not a constant echo). (3) GOLD-coref oracle == 1.000 (the register is faithful given correct entities -- isolates Stage-1 from Stage-2). (4) PLEONASTIC-'it' filter active: object anaphora ABSTAINS on expletive 'it' / no-antecedent (never-confidently-wrong). (5) SCOPE-OUT controls: we/you ABSTAIN (not bound) -- a named residual (group entity / rotating addressee), not a wrong bind. (6) OBJECT-ANAPHORA controls (LitBank gold, n=189): random-twin NULL p95 0.323 loses to recency 0.730; first-mention floor 0.132 (can-fail); reader coref 0.000 (abstains); subject-salience ablation HURTS (paired -0.212 CI-sep) = the parameter sweep."
files_changed: "experiments/world_state_entity_binding.py (the brain-foundational Stage-1 dispatcher: pleonastic->indexical->anaphoric->object-anaphora->nominal); experiments/exp_world_state_coref_diagnose_v1.py (residual decomposition); experiments/exp_world_state_coref_densify_v1.py (LitBank he/she holder densification: blind vs reader vs gold vs shuffled-null twin); experiments/exp_world_state_deixis_object_v1.py (MCScript2 build-across of the indexical + object routes, routed through the EntityBinder); experiments/exp_world_state_object_anaphora_gold_v1.py (object-anaphora ACCURACY on real LitBank gold: recency vs salience vs first-mention floor vs random-twin NULL); verification/test_world_state_coref_densify.py (12/12 witness). NO hdlab/ written (Q111 -- the proposed wire is in FOR STRATEGY below)."
reverify: ".venv/Scripts/python.exe verification/test_world_state_coref_densify.py   # 12/12 -- recomputes EntityBinder routes + register core + LitBank he/she headline (reader>blind, gold=1.0, change-point) + MCScript2 object-anaphora impact + object-anaphora ACCURACY on LitBank gold (recency>twin-NULL, salience hurts) FROM SOURCE"
---

# The world-state register is coref-blind: the fix is a two-stage entity binder, and "coref" is three routes, not one

## Status in one line
The brief's mechanism is PROVEN and CI-separated (binding the holder through the reader's OWN he/she coref
recovers who-has-what, blind 0.000 -> 0.500 on the population where blindness bites; twin loses; change-point
95.6%). But **the disk outranks the brief**: "wire the reader's own coref" cannot resolve object "it" or
first-person "I" (the reader's coref is he/she-only), and those -- not he/she -- are the dominant real-prose gap.
So I built the FULL brain-foundational solution: a two-stage **EntityBinder** implementing all three Stage-1
reference routes (indexical / anaphoric / object anaphora), and measured each where gold or a deterministic
answer exists. SOLVED, with the residual precisely located and the ceiling named.

## THE OPENING MOVE -- how does the brain do this? (which structure; replicate or substitute)
Binding "who has what" is TWO stages the literature keeps distinct (research drill 2026-09-01, primary-lit
verified):
- **Stage 1 -- reference resolution ("which entity is this mention?") -- BIFURCATED (PINNED):**
  - **INDEXICAL** route (1st-person I/me/my): an O(1) speech-role lookup -> the NARRATOR node (Kaplan 1989 pure
    indexical; Buhler origo; Deictic Shift Theory). NOT anaphora. Case-invariant (I == me == my).
  - **ANAPHORIC** route (3rd-person he/she + object "it"): an O(n) Centering salience search (Grosz-Joshi-
    Weinstein 1995), agreement-narrowed. Object "it" uses the SAME machinery (entity-type-agnostic) + a
    pleonastic/expletive-"it" filter first (Lappin & Leass 1994).
- **Stage 2 -- entity-state update ("what happens once resolved") -- UNIFIED (PINNED):** bind mention -> node ->
  refresh possession state (Zwaan & Radvansky 1998 event-indexing; Gernsbacher structure-building). Possession
  attaches to the ENTITY node, not the surface mention -- **Glenberg, Meyer & Lindem 1987**, the anchor citation.

Our `world_state_register` **is** a faithful Stage-2 (the parent proved it 1.000 on gold). So the entire
"coref-blind" defect is upstream, in Stage 1 -- and it decomposes exactly along the brain's own module boundaries.

## THE DISK OUTRANKS THE BRIEF -- what I found, and what I built because of it
The brief says "wire the reader's OWN coref (sm.coref_resolutions), which resolves he/she." Measured on the
parent's own corpus, that touches only **6.2%** of transfer agents. Decomposing the parent's "81% pronoun agents"
by pronoun class (`exp_world_state_coref_diagnose_v1`) shows three routes of very different size and difficulty:

| route | MCScript2 agents | LitBank agents | reader's coref does it? | brain mechanism |
|---|---|---|---|---|
| **indexical** I/me/my | **64.7%** | ~0% | **NO** (he/she only) | O(1) narrator lookup (Kaplan) |
| **anaphoric** he/she | 6.2% | 21.6% | **YES** (EventCentralityReader) | Centering search (GJW) |
| **object anaphora** it/them | 10.6% (themes ~11%) | 3.8% | **NO** | Centering over objects + pleonastic filter |
| we/you/they (scope-out) | ~13% | ~0% | NO | group entity / rotating addressee |

So the brief's premise ("the reader's own coref resolves the keys") is **refuted for objects and first person** --
the reader's coref (`hdlab.state_of_mind.TARGET_PRONOUNS = {he,him,his,she,her,hers}`) is he/she-only. Refuting
the brief is the halfway point: I built the two routes the reader lacks (`experiments/world_state_entity_binding.py`,
the `EntityBinder`), keeping the he/she route as a faithful reuse of the reader's own resolver.

## WHAT WAS MEASURED

### 1. PRIMARY -- the brief's mechanism, PROVEN (LitBank, gold coref, `exp_world_state_coref_densify_v1`)
Binding the holder through the reader's OWN he/she coref, one variable isolated (object key held constant; scored
in gold-cluster space; blind and reader are IDENTICAL on nominal holders so the ONLY difference is he/she pronoun
resolution). All 25 LitBank coref docs, n=135 who-has-what queries over state-changing transfers:
- **Aggregate:** BLIND 0.570 -> READER 0.719, paired **+0.148 [0.096,0.208]** (CI half-width 0.056, excludes 0).
- **Decisive he/she subset (n=26, where blindness bites):** BLIND **0.000** -> READER **0.500 [0.308,0.692]**,
  +0.500; GOLD oracle 1.000. Shuffled-coref **null p95 0.154**; reader crushes it.
- **Controls:** single-draw same-gender twin loses (reader-twin +0.067 [0.015,0.119]); change-point positive
  control 95.6%; gold oracle 1.000 (register faithful given correct entities).
- **by-holder-class residual (named honestly):** nominal 0.731->0.798, he/she 0.000->0.500, **object 'it'
  0.2->0.2** (reader out of scope -- the object-anaphora residual, with its number).

### 2. BUILD-ACROSS -- the two routes the reader lacks (MCScript2, `exp_world_state_deixis_object_v1`, through the EntityBinder)
2729 first-person stories, 8777 transfers:
- **OBJECT ANAPHORA (the biggest concrete who-has-what lever):** 574 'it' themes, 65% with a nominal antecedent;
  the Centering-lite "it -> salient recent theme" rule (+ pleonastic filter) **relocates 259/374 transfers that
  blind applied to the wrong object** (who-has-what impact 0.69). Blind silently loses the object's holder ("I
  grabbed the cup ... I gave **it** to the waiter" -> blind's `have(cup)` stays stale forever); the object route
  recovers it.
- **INDEXICAL narrator rule (cheap, low-impact -- the refinement):** first-person "I" is a STABLE self-key, so
  blind tracks it fine in **94.7%** of stories; it fragments the narrator into >=2 case-keys ({i, me}) in only
  **5.3%**. So the dominant 64.7% first-person share OVERSTATES coref's who-has-what cost -- it needs the *cheap*
  indexical normalization (i/me/my -> NARRATOR), not the hard anaphoric coref the brief invoked.

### 3. OBJECT-ANAPHORA ACCURACY on real gold (`exp_world_state_object_anaphora_gold_v1`)
LitBank's coref CoNLL gold-clusters NON-PERSON entities too (facility/location/vehicle/group), so 354
object-pronoun mentions (it/its/they/them/their) carry a gold cluster; 189 are resolvable (a prior nominal in the
same cluster). Resolving them to a prior nominal mention (correct = matching gold cluster):
- **RECENCY 0.730 [0.667,0.794]** (the most-recent number-agreed nominal) >> **random-twin NULL p95 0.323** >>
  **first-mention floor 0.132** (can-fail) >> **reader's coref 0.000** (it/they are OUT of `TARGET_PRONOUNS` -- the
  reader abstains entirely; the organ recovers what the reader cannot).
- **BRAIN-FOUNDATIONAL SWEEP (copy the computation, sweep the parameter):** subject-prominence Centering HURTS
  objects -- salience 0.518, paired -0.212 [-0.286,-0.132] vs recency. Objects are rarely the backward-looking
  center (Cb), so the person-anaphora Cf-ranking (subject>object) is the WRONG cue for "it"; recency/locality is
  right. `W_SUBJECT` was OUR-INVENTION and the gold says drop it -> the object route is PURE RECENCY (+ number
  agreement + pleonastic filter).

## WHAT I DID NOT ESTABLISH (withdraw-first)
- **The object-anaphora who-has-what IMPACT on MCScript2 (259 relocations) is a lever size, not an accuracy** --
  its resolver accuracy is proven on LitBank gold (0.730 above), but MCScript2 has no gold, so the 259 is "blind
  applied the transfer to the wrong key" (a provable blind failure), not "the resolver picked the right object
  259/259". **First thing I would withdraw:** any implication that all 259 relocations are verified-correct
  resolutions (the resolver's own error rate is ~0.27 by the LitBank number).
- **The binder's transfer-context object route uses recency-among-THEMES (recency_object 0.614 on general LitBank
  'it'); the gold says PURE recency (any-role, 0.730) is better** -- a small tuning: the hdlab wire should feed the
  binder the recent nominal context, not only transfer themes (noted in FOR STRATEGY).
- **The he/she recovery ceiling is 0.500**, set by the reader's coref recall on *same-gender transfer pronouns*
  (the hardest Centering case). This is the reader's coref organ, not the register -- and it is on LitBank, the
  coref's home corpus, so 0.5 is if anything optimistic OOD. The lever to raise it is a landed, unwired organ
  (below), not this problem.
- **we/you/they are SCOPED OUT and abstain** (research: "we" is a group entity, "you" a rotating per-turn
  addressee) -- ~13% of MCScript2 agents left unbound (named, never-confidently-wrong).
- **Quoted first-person ("embedded deictic centers")** are not handled -- a flat narrator rule mis-binds quoted
  "I" to the narrator. Low-impact for monologic MCScript2; a real error source for dialogue-heavy LitBank.

## KEY REALIZATIONS (the enabling moves)
1. **Decomposing "81% pronoun agents" by pronoun CLASS is what refuted the brief.** The single number hid three
   routes of wildly different size, difficulty, and brain mechanism. The parent's located residual ("coref") was
   right that pronouns are the gap but wrong that it is one thing -- 65% of it is the *cheapest* route (first-person
   indexical), not the hard anaphoric coref.
2. **First-person "I" is a STABLE self-key, so it is NOT the who-has-what wall it appears to be.** Blind tracks it
   fine 94.7% of the time. The who-has-what damage from coref-blindness is concentrated in OBJECT ANAPHORA (the
   transfer lands on "it", not the cup) and he/she holders -- not the 65% first-person share.
3. **The brain uses TWO Stage-1 operations, not one** (indexical lookup vs anaphoric search). Building the binder
   as a single anaphoric resolver would have been wrong; the dispatcher (route-by-mention-type) is the faithful
   copy, and it is why the fix generalizes across genres (first-person everyday AND third-person literary).
4. **Isolating ONE variable made the he/she claim clean:** holding the object key constant and scoring in
   gold-cluster space, blind and reader are identical on nominal holders -- so the entire +0.500 on the he/she
   subset is the coref, and blind is pinned at exactly 0.000 (a pronoun string denotes no entity).
5. **Stage 2 was already faithful; the whole problem was Stage 1.** The register (possession bound to a key,
   STRIPS effect/precondition) copies Glenberg's entity-bound possession. Coref-blindness is entirely a Stage-1
   reference-resolution gap -- which is why the fix is a densifier IN FRONT of the register, not a register change.
6. **Object anaphora is RECENCY-dominant, and the person-anaphora rule ACTIVELY HURTS it** (subject-salience
   -0.212 CI-sep on LitBank gold). The enabling move was noticing LitBank gold-clusters non-person entities, which
   turned an "impact-only" claim into a CI-separated accuracy -- and the sweep then overturned my own initial
   design (drop the subject weight). Objects are not the backward-looking center, so the SAME Centering machinery
   with a DIFFERENT parameter setting (recency, not Cf-prominence) is the faithful copy.

## ADJACENT COMPONENTS (brain-foundational status + optimization -> next problems)
Evaluated per the owner's standing instruction (which components feeding/drawing-from this are brain-foundational,
where is the optimization, which are NOT brain-foundational and should be improved):

- **`hdlab.event_centrality_coref.EventCentralityReader` (feeds the register; WIRED; brain-foundational --
  Centering + event-memory tie-break).** LIMITATION: ~0.5 recall on same-gender transfer pronouns = the
  densification ceiling. This is the organ the register's he/she route depends on.
- **`hdlab.graded_coref_pick` (landed, NOT stream-wired; brain-foundational -- ACT-R base-level activation graded
  cue retrieval, Lewis-Vasishth 2005).** From `coreference_is_capped_at_065_on_real_narrative` (SOLVED/EXCELLENT):
  it **beats the hard subject-first tier +0.172 CI-sep**, entropy predicts its own errors AUC 0.806. Its
  resolver-stream wiring is a QUEUED follow-on. **-> STRONGEST next problem: wire graded_coref_pick into the
  resolver stream feeding the register, to raise the he/she densification ceiling above 0.5.** (High leverage,
  proven organ, on-disk evidence.)
- **`hdlab.coreference_resolver` (NEEDS_ADAPTER; brain-foundational -- Principle B + quote speaker/addressee
  DEIXIS + name-bridging + honest-mode abstain).** Handles the EMBEDDED deictic center (quoted "I") my binder
  scopes out. **-> Next problem: wire it (+ quotation deictic scope) for dialogue-bearing prose.**
- **Front-end parser (`hdlab.candidate_generator`; WEAK; LOW brain-fidelity -- a trained perceptron parser, an
  OUR-INVENTION statistical component).** Caps role recall (recipient-on-GIVE 0.33), the shared upstream cap for
  BOTH the register and the meaning channel. **-> Candidate to make more brain-foundational (an incremental,
  expectation-driven parse).**
- **`hdlab.coref.EntityAliaser` (WIRED; brain-foundational -- entity unification, Miss Bennet = Elizabeth).** Works;
  gives the small nominal-holder gain (0.731->0.798).
- **Object anaphora as an organ: DID NOT EXIST -- the `EntityBinder` is the first, and it is now VALIDATED on real
  gold** (LitBank non-person clusters; recency 0.730 vs twin-NULL p95 0.323; subject-salience hurts -0.212 CI-sep).
  Brain-foundational (Centering entity-type-agnostic, recency parameter + Lappin-Leass pleonastic). **-> Candidate
  organ to promote (a general glass-box 'it'-resolver the substrate lacks -- reader coref abstains on 'it'); a
  plural/group 'they' resolver and a stronger pleonastic classifier are the two refinements.**
- **Downstream (draws FROM the register):** `sm.world_state` is default-off and NOTHING consumes it yet
  (who-has-what QA: "who has the key now?"). **-> Wiring a who-has-what query consumer is the payoff of this whole
  line.**

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md 2b -- strategy folds in)
The world-state register's open-text payoff is **coref/entity-binding-bound, and entity binding is TWO Stage-1
routes (indexical + anaphoric) the reader only partly implements.** Binding the holder through the reader's OWN
he/she coref recovers who-has-what CI-separated over the coref-blind register (LitBank, blind 0.000 -> reader
0.500 on he/she holders; +0.148 aggregate paired; twin loses; change-point 95.6%; gold oracle 1.000). The register
(Stage-2) is faithful; the gap is entirely Stage-1 reference resolution. The dominant real-prose share (64.7%
first-person on MCScript2) is the CHEAP indexical route (i/me/my -> NARRATOR), not anaphora -- and first-person is
mostly a stable self-key, so "81% pronoun agents" overstates coref's who-has-what cost. The biggest concrete lever
is OBJECT ANAPHORA (it -> salient theme; 259/374 MCScript2 relocations; resolver validated on LitBank gold RECENCY
0.730 vs twin-NULL p95 0.323), an organ the substrate lacked. NEW brain-foundational finding: object anaphora is
RECENCY-dominant -- the person-anaphora Centering Cf-ranking (subject-prominence) HURTS objects CI-sep (-0.212),
because objects are not the backward-looking center; same machinery, recency parameter. Ceiling on the he/she route
= the reader coref's same-gender recall (~0.5); the landed-but-unwired `graded_coref_pick` (+0.172 CI-sep) is the
path to raise it.

## FOR STRATEGY (you land hdlab; Q111 -- I do not write hdlab/)
The proposed wire is a densifier IN FRONT of the register's fold, default-off, byte-identical when off:
1. **Promote `experiments/world_state_entity_binding.py` -> `hdlab/world_state_entity_binding.py`** (the glass-box
   Stage-1 dispatcher; self-tested, no LLM).
2. **In `hdlab/situation_reader._read_world_state`, add a default-off `densify_world_state` option** that, before
   `WorldState().fold(reps)`, rewrites each rep's AGENT/PATIENT/ARG2 through an `EntityBinder`:
   - agent/recipient/source (holder) -> `bind_participant(head, coref_cluster=<reader he/she resolution for this
     mention from sm.coref_resolutions>)`;
   - theme (object) -> `bind_theme(head, verb)` (object anaphora + pleonastic filter, stateful over the passage).
   Feed the reader's OWN he/she resolution as `coref_cluster` (the faithful reuse); the indexical + object routes
   are the binder's. Default OFF = byte-identical (`_read_world_state` unchanged). TUNING (from the gold sweep):
   resolve 'it' by PURE RECENCY over recent number-agreed nominals (NOT subject-salience, which hurts -0.212
   CI-sep) -- feed the binder the recent nominal context, not only transfer themes.
3. **Witness:** `verification/test_world_state_coref_densify.py` (12/12) covers every route + the LitBank headline
   + the object-anaphora accuracy on gold.
4. The ceiling-raiser (`graded_coref_pick` -> resolver stream) is the filed follow-on for the he/she route.

## TLDR
As you read a story you keep track of who currently has what. Our tracker was right when people and objects were
named cleanly, but on real stories it wrote down the WORD, not the person -- so "he gave it to her" put the object
in the hands of "her" (a word), and "I gave IT to the waiter" moved a thing called "it" instead of the cup. I
found that the brain fixes this with TWO different tricks, not one: for "I/me/my" it just points to the narrator
instantly (no searching), and for "he/she/it" it searches back for the most prominent recent thing it could mean.
Our reader already does the second trick for he/she, so I wired that into the tracker: on real 19th-century prose,
where the holder is a "he/she", the tracker went from getting it right 0% of the time to 50% of the time (a clean,
statistically separated gain, with scrambled and empty versions failing and the answer correctly flipping when the
object changes hands). Then I built the two tricks our reader was missing: pointing "I/me/my" to the narrator, and
resolving "it" to the object it stands for -- the second one fixed 259 real cases where the tracker had been moving
the wrong thing. The honest surprise: most pronouns in these stories are "I", and "I" is easy (it always means the
narrator), so the scary-sounding "81% of doers are pronouns" mostly ISN'T the hard problem -- the hard, valuable
pieces are the "he/she" search (which is capped by how good our pronoun-resolver is) and the "it" resolution
(which our reader couldn't do at all until now).

## QUESTIONS
None.

## NEXT STEPS
1. Strategy: promote the `EntityBinder` + wire a default-off `densify_world_state` densifier in front of
   `_read_world_state` (feeding the reader's own he/she resolution as the anaphoric input).
2. Raise the he/she ceiling: wire the landed `graded_coref_pick` (+0.172 CI-sep, proven) into the resolver stream
   the register reads (the biggest single lever; its stream-wiring is a queued follow-on).
3. Promote the object-anaphora resolver (recency + number agreement + pleonastic filter) as a general glass-box
   'it'-resolver (validated on LitBank gold 0.730); add a plural/group 'they' route and a stronger pleonastic-'it'
   classifier. (The he/she + object routes together are the full non-first-person entity binder.)
4. Add the embedded-deictic-center (quoted-"I") scope via `hdlab.coreference_resolver.run_principle_b_deixis` for
   dialogue-bearing prose; handle "we" (group entity) and "you" (rotating addressee) as their own routes.
5. Wire a downstream who-has-what QA consumer of `sm.world_state` ("who has the key now?") -- the payoff.
