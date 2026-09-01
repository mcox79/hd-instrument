---
problem: the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise
status: SOLVED
bar: "PASS = the predict-and-revise parse pass RECOVERS who-did-what (and the arguments the batch parse drops) CI-SEPARATED over the strongest REAL floor — the batch parse-as-truth / positional-default reader at EQUAL inputs — on held-out + MODERN real prose, with the info-free TWIN (revise at the same rate at RANDOM loci, or with a shuffled prior) LOSING CI-separated, AND a positive control that revision fires exactly where the prediction is violated (not everywhere). Report CI half-width + null p95 beside every margin. A rigorous NEGATIVE is a full PASS if located: if predict-and-revise, faithfully built, does not beat parse-as-truth (the residual is irreducible recall — the structure is simply not recoverable from the available signal), name it precisely (which constructions, why the prior cannot disambiguate them) and localize the ceiling — that tells the assembly where the true front-end limit is."
result: "A parse-RECALL pass that recovers the DROPPED patient the batch parse left empty ('?') — a structural coverage-violation trigger, recall-scoped (fill-a-drop or promote a PRE-VERBAL head; NO post-verbal re-selection) — RECOVERS who-did-what CI-separated over the strongest real floor on BOTH eras (who-did-what patient recall through the LIVE SituationReader.read(), scorer = pick==gold head, bootstrap CI by sentence cluster). MODERN QA-SRL v2 dev+test, n=2737 non-pronoun-gold patient items: the pass 0.5407 vs the wired parse-router 0.4808 = +0.0599 [+0.0395,+0.0889] (half 0.0247, frac<=0 0.000); on the positional floor 0.4417 vs 0.3858 = +0.0559 [+0.0350,+0.0827]. 19c LitBank narrative, n=5999: 0.2879 vs the (there-strongest) positional floor 0.2287 = +0.0592 [+0.0525,+0.0659] (half 0.0067, frac<=0 0.000). Gains localize to non-canonical constructions: QA-SRL passive 0.287->0.567, pre-verbal-gap 0.023->0.511; canonical recall PROTECTED 0.509->0.526. DRILLED: the entire gain is DROP-FILLING — firing on dropped patients ONLY (no surprisal reanalysis of committed picks) reaches 0.5433 (+0.0625 over wired, CI-sep) and TIES the surprisal-gated pass (gated-vs-dropped_only -0.0026 n.s.); the 391/704 surprisal-triggered revisions of COMMITTED picks add nothing (confirming p2's refuted re-selection from the recall side)."
floor: "the batch parse-as-truth reader at equal inputs, BOTH routes actually run: positional-default (QA-SRL 0.3858 / LitBank 0.2287) and the stronger wired parse-router (QA-SRL 0.4808 / LitBank 0.1852). The pass beats WHICHEVER is stronger per era CI-separated (QA-SRL strongest = wired, beaten by +0.0599; LitBank strongest = positional because the modern-trained arc_parser DEGRADES on 19c prose, beaten by +0.0592). It also beats the OTHER floor in both eras."
controls: "(1) info-free RANDOM-LOCI twin (fire at the same rate at random loci) LOSES CI-sep: QA-SRL +0.0442 [+0.0284,+0.0642], LitBank +0.0395 [+0.0343,+0.0448] = EXCLUDES 'any extra re-parsing at this rate helps' (firing on the DROPPED-slot events, not random ones, is what carries it). (2) info-free UNIFORM (random-vector) PRIOR twin LOSES CI-sep: QA-SRL +0.0325 [+0.0134,+0.0594], LitBank +0.0492 [+0.0426,+0.0558] = EXCLUDES 'any prior-shaped candidate scorer helps' (the fill TARGET uses real animacy/position). (3) revise-EVERYWHERE positive control: the recall-scoped pass BEATS revise-everywhere CI-sep (QA-SRL +0.0106 [+0.0040,+0.0173], LitBank +0.0083 [+0.0060,+0.0107]); it fires on only ~28-30% of eligible events = it does NOT fire everywhere (revising committed picks breaks as many as it fixes). (4) recall_only scope = no post-verbal re-selection (p2's REFUTED route) -> canonical recall PROTECTED, not eroded (QA-SRL 0.509->0.526). (5) DROP-FILL localisation (the decisive drill): firing on DROPPED patients ONLY (a purely STRUCTURAL trigger, NO surprisal) reaches 0.5433 and TIES the surprisal-gated pass (gated-vs-dropped_only -0.0026 [-0.0076,+0.0027] n.s.) while beating wired +0.0625 CI-sep = EXCLUDES 'the surprisal signal is needed for RECALL'; the 391/704 surprisal-triggered revisions of COMMITTED picks add nothing. (6) LOCATED-LEVER: a verb-SHUFFLED prior loses only slightly (QA-SRL +0.0142, LitBank +0.0022 n.s.) and a NO-PRIOR STRUCTURAL fill TIES on modern QA-SRL (+0.0026 n.s.) though the prior BEATS it on 19c prose (+0.0217 [+0.0129,+0.0307]) = the lever is the STRUCTURAL drop-fill; the VERB-SPECIFIC selectional prior is a MINOR cue (position carries modern recall; the prior adds only where the parser degrades)."
files_changed: "experiments/exp_predict_revise_recall_v1.py (the mechanism + full control battery incl. the dropped-only DROP-FILL drill + sweep + LitBank); experiments/exp_predict_revise_recall_diagnostic_v1.py (the could-it-succeed recall decomposition + oracle headroom); experiments/_drill_animacy_fill_v1.py (the ANIMACY-vs-POSITION cue drill + scrambled-animacy twin); experiments/_drill_ceiling_and_ambiguity_v1.py (drop-fill ceiling + animacy-under-position-conflict); experiments/_drill_agent_recall_v1.py (AGENT-role recall + why drop-fill is patient-specific); experiments/_drill_construction_fill_v1.py (construction-cued filler-gap PROTOTYPE for the residual 45% + interference-scaling); experiments/_drill_reuse_relcl_resolver_v1.py (REUSE the validated hdlab.relcl_resolver organ on the drops — +0.0066 overall); experiments/_drill_ditransitive_frame_v1.py + _drill_construction_role_v2.py + _drill_construction_role_v3.py (OWNER-DIRECTED wrong-bind blowout: the double-object construction fix, verb + 19c-era generalization, construction-gate control); experiments/_drill_integrated_pass_v1.py (integrated drop-fill + double-object + preverbal, both eras — the era-robustness finding); experiments/_drill_cue_integration_role_v1.py (the PARALLEL CUE-INTEGRATION role assigner — Competition Model, era-robust, +0.098/+0.027 over position both eras) + data/predict_revise_recall_v1/_population_litbank.json; experiments/_drill_reuse_graded_role_v1.py (REUSE the validated hdlab.graded_role_assigner routed Competition-Model organ — 0.6076 modern, beats the flat integrator); experiments/_drill_agent_patient_contrast_v1.py (research fix #1 prototyped — agent/patient contrast HURTS in the coarse grounded space -> needs a distributional asset); experiments/_drill_distributional_role_fit_v1.py (the brain-foundational role-separated DISTRIBUTIONAL fit with a GloVe foundation asset — DECISIVE negative: ties grounded on modern, fails 19c; the ceiling is position/parse, not fit-quality); verification/test_predict_revise_recall.py (scaffold-free witness, 8/8); data/predict_revise_recall_v1/metrics.json + _population.json + _drill_dropped_only.json; data/predict_revise_recall_diagnostic_v1_smoke/. hdlab/ UNTOUCHED (Q111 — proposed default-off predict_revise flag stated below)."
reverify: ".venv/Scripts/python.exe verification/test_predict_revise_recall.py"
---

# Predict-and-revise recovers who-did-what the batch parse DROPS — and the recovery is a STRUCTURAL DROP-FILL, not surprisal-gated reanalysis or the selectional prior

## What was asked
The reader takes its ONE batch parse AS TRUTH; the brain infers the INTENDED structure by fusing the noisy
parse (evidence) with a plausibility PRIOR and RE-PARSING where a forward prediction is violated (Levy 2008
noisy-channel; Gibson/Bergen/Piantadosi 2013; the P600/LIFG reanalysis stream, gated by the violation and
distinct from the N400 thematic-fit stream). p2 proved the reader's who-did-what errors are structural (the
reader binds the grammatically-default entity) and validated the forward-prediction VIOLATION signal live
(`predict_surprisal` -> `EventRecord.patient_surprisal`). The missing half was the REVISION: recover the
structure the single batch parse DROPPED. Build it, prove it recovers who-did-what CI-separated over parse-
as-truth, or enumerate that the residual is irreducible recall.

## Verdict: SOLVED — the pass recovers, all controls clean, both eras; and the mechanism is LOCATED
The predict-and-revise pass is a POST-READ parse-RECALL pass over the reader's own extraction (we may not
touch hdlab; Q111). The reader's stock role rule is POSITIONAL — patient = nearest nominal STRICTLY AFTER the
predicate, else '?'. That rule STRUCTURALLY DROPS the patient in non-canonical constructions (passive /
object-relative / fronting), where the patient is PRE-VERBAL. The pass:
1. the positional (or parse-router) pick = the batch-parse EVIDENCE (the floor);
2. the VIOLATION that triggers a re-parse is a STRUCTURAL COVERAGE violation: the parse left the patient
   EMPTY ('?') — a transitive verb with no bound patient. (I also tested a surprisal gate on COMMITTED picks
   — revise iff `patient_surprisal` > tau — and it adds NOTHING to recall; see the drill below.)
3. on the trigger, over the FULL nominal candidate set (incl. the PRE-VERBAL heads the positional rule
   excludes) pick the recall-scoped MAP `score(c) = fit(c) - beta*position_penalty(c)` (fill a drop, or promote
   a PRE-VERBAL head on a sharp verb — never re-select a post-verbal candidate, which is p2's REFUTED move).
   `fit` = cos(grounded(c), verb-PATIENT centroid) = the selectional prior; `position_penalty` = 0 post-verbal
   / 1 pre-verbal = the word-order likelihood.

The scaffold-free witness reproduces the headline + both located findings on a FRESH independent n=613 read
(built from source through the live reader, not the cached population): **8/8 checks pass** — revise-on-wired
beats wired CI-sep, revise-on-positional beats the floor CI-sep, the random-loci twin loses CI-sep, the
uniform-prior twin does not beat the real pass, the pre-verbal gap is recovered (0.025 -> 0.487), a no-prior
structural fill TIES the prior pass, and DROP-FILLING captures the gain (dropped-only beats wired +0.062 CI-sep
while the surprisal gate on committed picks is not load-bearing).

**The recovery is real and beats the STRONGEST floor CI-separated on both eras** (numbers in the frontmatter),
concentrated exactly where the positional rule fails: QA-SRL pre-verbal-gap 0.023 -> 0.511, passive 0.287 ->
0.567, while CANONICAL recall is PROTECTED (0.509 -> 0.526). It generalizes to 19c LitBank (+0.059 CI-sep over
the there-strongest floor) — not a modern-vocabulary artifact.

### Per-construction recall (floor_positional / wired / revise_pos / revise_wired)
| stratum | QA-SRL n | positional | wired | revise_pos | revise_wired |
|---|---|---|---|---|---|
| canonical | 1286 | 0.509 | 0.480 | 0.523 | 0.526 |
| passive | 1385 | 0.287 | 0.494 | 0.382 | **0.567** |
| pre-verbal-gap | 753 | 0.023 | 0.456 | 0.147 | **0.511** |
| non-canonical (all) | 1451 | 0.276 | 0.482 | 0.370 | 0.553 |

19c LitBank (n=5999; voice unlabeled so only pre-verbal-gap non-canonicality is detected): canonical 0.260 ->
revise_pos 0.325; pre-verbal-gap 0.001 -> 0.045. The wired parse-router DEGRADES on 19c prose (0.185 < the
0.229 positional floor), and the pass is ROBUST to it (revise-on-wired still +0.081 over wired).

## THE LOCATED FINDING (the drills the owner asks for — two NEGATIVES nested in the POSITIVE)
The pass WORKS, but the control battery LOCALISES what carries it, and it is NOT what the brief hypothesized.

**(A) The gain is DROP-FILLING, not surprisal-gated reanalysis of committed picks — the DECISIVE drill.**
Firing on DROPPED patients ONLY (the parse left '?'; a purely STRUCTURAL coverage-violation trigger, NO
surprisal) reaches 0.5433 — it BEATS wired +0.0625 CI-sep AND TIES the full surprisal-gated pass
(gated-vs-dropped_only -0.0026 [-0.0076,+0.0027] n.s.). Of the 704 gated fires, 313 are drops and 391 are
surprisal-triggered revisions of COMMITTED picks — and those 391 add NOTHING net. So the surprisal signal
(`predict_surprisal`, the p2 landing) is NOT needed for the RECALL gain: recovering the DROPPED argument is
the whole story, and revising a pick the parse already committed is p2's refuted re-selection (confirmed here
from the recall side). This SHARPENS the brief's own load-bearing distinction — "recover DROPPED structure,
do NOT re-choose among the KEPT" — into a measured result. It also SIMPLIFIES the hdlab landing: the recall
pass needs no fitted predictor asset, only the structural drop trigger + candidate promotion.

**(B) Within drop-filling, the TARGET cue is POSITION — not the selectional prior, and NOT animacy.** A
NO-PRIOR structural fill (nearest nominal to the verb) TIES the grounded-prior fill on modern QA-SRL (+0.0026
n.s.); a verb-SHUFFLED prior loses only marginally. I then research-drilled the obvious brain-foundational
alternative — the Competition Model / eADM (Bornkessel-Schlesewsky) PIN ANIMACY as the primary undergoer cue
(patients are prototypically inanimate), so "position" might be a STAND-IN for animacy. It is NOT: an
ANIMACY-cued fill (prefer the inanimate candidate; the substrate's `animacy_lexicon`, 88% candidate coverage)
gives 0.5473 vs position 0.5440 = +0.0033 (NOT CI-sep) AND TIES its own SCRAMBLED-animacy twin exactly
(+0.0000 [-0.0038,+0.0041]) — the animacy INFORMATION does nothing; the position tie-break carries it. Forcing
a pre-verbal preference is WORSE than nearest-to-verb (-0.0088 CI-sep) — many wired DROPS are the router
failing on a POST-verbal object, recovered by proximity. So all three meaning/animacy cues (verb-specific
prior, grounded fit, animacy) FAIL to beat linear POSITION. **This is exactly the Competition Model's
cue-validity ranking for English: word-order >> animacy >> lexical-plausibility** (English is the word-order-
dominant extreme; animacy is a high-validity cue in case-rich languages, a low-validity one here). The prior
earns its keep ONLY on 19c prose, where the parser degrades and word-order is less reliable (+0.0217 CI-sep) —
consistent with the same account (when the dominant cue weakens, a subordinate cue surfaces).

Both drills CONVERGE with p2 and with the audit: English who-did-what is word-order-dominant (MacWhinney
Competition Model), so the recoverable signal is the STRUCTURAL argument the parse DROPPED (the LIKELIHOOD /
parser-RECALL term the audit named), recovered by a coverage-violation-triggered recall — NOT by re-ranking
committed picks on plausibility. `predictive_reader` remains a good VIOLATION FLAG (p2) but is not needed to
DRIVE the recall.

## DISK-OUTRANKS-BRIEF (a correction the brief invites)
The brief (inheriting the SPACE dimension) states "the LEVER is the predict-and-revise PRIOR, not raw parser
strength." For WHO-DID-WHAT the disk says: the lever is the STRUCTURAL DROP-FILL (recover the argument the
parse left empty), triggered by the coverage violation — NOT the surprisal gate (adds nothing) and NOT the
verb-specific selectional prior (a minor cue on modern text). The noisy-channel LEVER is DIMENSION-SPECIFIC:
for SPACE it is a PERSISTENCE prior (a strong, cheap dynamical prior — the lever); for who-did-what it is a
SELECTIONAL-plausibility prior (weak in the coarse space, fighting structure-dominant English — NOT the lever;
the LIKELIHOOD / parser-RECALL term is). The brief's GOAL (recover the dropped structure CI-sep) is MET; its
proposed MECHANISM EMPHASIS (the prior + surprisal-gated reanalysis) is corrected to the structural drop-fill.

## KEY REALIZATIONS (the enabling moves)
1. **Measure the recall DECOMPOSITION before building.** p2 scored RE-SELECTION on the COMMITTED subset (65%
   of gold) and EXCLUDED the dropped structure. Parse-RECALL IS the excluded population, so the first move was
   to re-open it: full recall over ALL non-pronoun gold, an error taxonomy (extraction_miss / dropped /
   wrong_bind), and an ORACLE headroom (is the gold head even a candidate?). That showed the recoverable gap is
   the PRE-VERBAL bucket (the positional rule only looks post-verbal), not the post-verbal wrong-binds (p2's
   irreducible territory). *"Ask whether the experiment could have succeeded before asking why it did not."*
2. **recall_only was the load-bearing scope.** Restricting the revision to fill-a-drop or promote-a-PRE-VERBAL
   candidate (never post-verbal re-selection) is what separates this from p2's refuted re-selection and PROTECTS
   canonical picks. Without it the mechanism re-enters p2's wall and breaks as many as it fixes.
3. **Test ON TOP OF the stronger parse, not just the weak floor.** Revising the positional floor alone is a
   strawman; the decisive test is whether the pass adds recall over the WIRED parse-router. It does (+0.060
   CI-sep) — real structure the best parse still drops.
4. **Isolate the lever with a NO-PRIOR twin and a verb-SHUFFLED twin.** These converted "the prior is the lever"
   (assumed) into "position is the lever on modern text; the prior earns its keep only on degraded/archaic
   parses" (measured). The negative-within-the-positive is the deliverable.
5. **Split the trigger to isolate DROP-FILL from surprisal reanalysis (the decisive drill).** Adding a
   `dropped_only` arm (fire only where the parse left '?') showed it captures the ENTIRE gain and ties/beats the
   surprisal-gated pass — the 391/704 surprisal-triggered revisions of committed picks add nothing. That turned
   "predict-and-revise recovers structure" (true) into the sharper "the recovery is DROP-FILLING; the p2 surprisal
   asset is not needed to drive it" — which both confirms the brief's own dropped-vs-kept distinction empirically
   and simplifies the landing to an asset-free structural pass. *A control that removes a candidate ingredient is
   worth more than one more arm that adds recall.*
6. **ENUMERATE the substrate before claiming a NEW BUILD — the brain reuses circuits, so should we (owner
   catch).** I initially called the residual filler-gap a "new build"; enumerating hdlab (not searching) found
   `relcl_resolver.py` ALREADY does it (validated), and the SAME cue-based retrieval primitive
   (`content_addressable_retrieval` / the E3 coref organ) underlies BOTH coref and filler-gap — reuse lifted
   recall for free (+0.0066). The lesson: filler-gap ≡ coreference ≡ cue-based content-addressable retrieval
   (Lewis & Vasishth; McElree) — one primitive, many surface tasks; an "we need to build X" claim demands a disk
   ENUMERATION first, because the substrate has usually already built the primitive under another task's name.

## FURTHER DRILLS (completeness push — every avenue I could think of, tested)
- **DROP-FILL CEILING.** Of the 313 wired-dropped patients, the gold head IS a candidate in **313/313
  (100%)** — so every drop is recoverable in principle; NONE is gold-absent. Position captures **0.553** of
  them. So ~45% of recoverable drops are LEFT ON THE TABLE — the residual is NOT irreducible, it is a NAMED
  buildable gap (below).
- **ANIMACY SURFACES UNDER POSITION-CONFLICT (the Competition-Model cue-interaction).** Globally animacy ties
  position (and its own scramble). But on the subset where position is ambiguous — drops with MIXED-animacy
  candidates (n=80) — ANIMACY beats position **+0.088** (CI[-0.027,+0.211], frac<=0 0.095: ~90% of bootstraps
  positive; underpowered at n=80), and the gold patient is genuinely inanimate in **82%** of those. This is
  exactly the Competition-Model signature: the subordinate cue (animacy) surfaces precisely under dominant-cue
  (word-order) CONFLICT. So the faithful fill is POSITION-primary with an ANIMACY tie-break under conflict; the
  global "position wins" masks a real cue-interaction. (Small overall: ~+0.003, but brain-faithful and it
  conveys the cue-integration benefit.)
- **THE RESIDUAL 45% IS ENTIRELY RETRIEVAL INTERFERENCE — MEASURED, then PROTOTYPED (owner: "prototype getting
  that last 45% here?").** The literature (Van Dyke & McElree cue-based retrieval interference; Wagers & Phillips
  2014) predicts position fails where an INTERVENING distractor NP sits between the true filler and the gap.
  DIRECT TEST — position-fill recall on the 313 drops, stratified by # intervening candidate nominals between
  the gold filler and the verb: **0 intervening -> 0.754 (n=228); 1 -> 0.000 (n=53); 2 -> 0.000 (n=24); 3+ ->
  0.125 (n=8).** Position NAILS it with no distractor and COLLAPSES TO EXACTLY 0% the moment one intervenes — it
  grabs the distractor every time. So the whole residual is the ~85 interference drops (recoverable in
  principle: ORACLE 1.000). PROTOTYPE of the brain's fix (construction-cued filler-gap: a relativizer/passive
  signals a gap -> jump OVER the distractor to the antecedent / surface subject; Crain & Fodor 1985; Stowe 1986)
  — a NEGATIVE, and diagnostic: a string-heuristic detector fires on only 14/85 interference cases (and 0.024 vs
  position 0.012 on them, overall +0.0004). The cheap heuristic CANNOT crack it — the other 71 are reduced
  relatives / coordination / appositives that need REAL syntactic filler-gap resolution (the antecedent
  identified by structure, not a string match). Target for whatever owns it: 85 interference drops, position 0%,
  oracle 1.0.
- **REUSE, NOT A NEW BUILD (owner-prompted ENUMERATION — I had overstated "new build").** Enumerating hdlab (not
  searching) surfaced the reusable organs: **`relcl_resolver.py`** — the VALIDATED active-filler filler-gap
  resolver (`resolve_patient(toks,pos,v)`, landed 2026-08-27, 8/8 witness; does the object-relative
  jump-over-the-distractor + passive-subject routes, glass-box over UPOS, NO arc graph); `content_addressable_
  retrieval.py` + `coreference_resolver.py` — the SAME cue-based content-addressable RETRIEVAL primitive (Lewis &
  Vasishth 2005; McElree) the brain reuses for BOTH coreference AND filler-gap; plus `graded_competition`,
  `salience_binder`, `coref_distractor_suppress`. REUSING `relcl_resolver.resolve_patient` as the drop-fill
  TARGET (instead of my position heuristic) lifts OVERALL who-did-what recall **0.5440 -> 0.5506 (+0.0066)** and
  the drop-subset recall **0.5527 -> 0.6102 (+0.057)** — a free, MORE brain-faithful improvement from an existing
  validated organ, and it recovers the object-relative interference cases position gets 0% on (0.00 -> 0.25 on
  the object-gap fires). The genuinely-unbuilt remainder is NARROW and the SUBSTRATE ITSELF names it:
  `content_addressable_retrieval`'s docstring states "interference RESOLUTION is a separate open problem" —
  graded retrieval under SIMILAR competitors (reduced relatives / coordination with no overt relativizer), which
  EXTENDS the existing retrieval primitive, not a from-scratch build. HONEST ANSWER to "is this a new build?":
  the object-relative/passive filler-gap is ALREADY an organ (reuse it — see the proposal); the residual
  unmarked-interference is ONE acknowledged open problem that reuses the same cue-based retrieval primitive.
- **AGENT recall (the 'who' half) — the mechanism structurally DOES NOT apply, and I measured why.** Non-pronoun
  agent recall through the wired reader is 0.567 (n=826; 27% of agent gold is pronoun, excluded), but agents are
  **DROPPED only 1.2%** of the time — because the positional rule looks PRE-verbal for the subject, which is
  exactly where English agents sit. So there is almost nothing to drop-fill; agent errors are WRONG-BINDS (31%)
  = p2's refuted re-selection territory (structural), and a nearest-pre-verbal fill recovers 0/10 dropped agents.
  The drop-fill is thus specific to the role whose canonical position the parser MISSES (the pre-verbal patient);
  this is a property of English structure, measured not assumed.
- **precise_voice floor fairness — resolved by ENUMERATION (reading the code, not a search).** The reader's
  `precise_voice` positional passive-swap is NOT in the live `_read_events` path; the WIRED floor already routes
  passives through the parse (`_read_events_wired`, "ROUTER agent fixes passive/ditransitive"). So the +0.073
  passive headroom is measured over the reader's actual passive-capable path — fair.

## WHERE THIS SITS IN THE WHO-DID-WHAT CEILING (owner: "not a blowout — how well does the brain do, and why?")
Honest framing so the +0.06 is not oversold. Decomposing the wired reader's who-did-what on n=2737:
correct 0.481 / **wrong-bind 0.309** / **dropped 0.114 (MINE)** / extraction-miss 0.096. EVERY error is
recoverable in principle (the gold head is present as a candidate in ALL buckets: 846/846, 313/313, 262/262),
so the ORACLE ceiling is **1.000**. QA-SRL gold IS human annotation -> the BRAIN sits at **~0.90-0.95**; our
reader at ~0.48-0.55. The ~0.40-point gap decomposes, and MY problem is the SMALLEST slice:
- **wrong-bind 0.309 — THE BIGGEST, and NOT this problem.** The reader confidently binds the WRONG post-verbal
  nominal (the positional default). Fixing it is p2's REFUTED re-selection wall: English is word-order-dominant,
  so a plausibility re-rank cannot override the structural default (MacWhinney Competition Model). It needs the
  brain's FULL cue-integration + real hierarchical syntax + world knowledge — the concurrent graded-role /
  incremental-parser problems, not a drop-fill. Ceiling stage: 0.595 -> 0.904 (+0.309).
- **dropped 0.114 — MINE.** Drop-fill (+ relcl_resolver reuse) recovers ~0.61 of it (to ~0.55 overall); the
  rest is the interference residual (the retrieval-resolution open problem). Ceiling stage: 0.481 -> 0.595.
- **extraction-miss 0.096 — event DETECTION, a separate front-end organ.** Ceiling stage: 0.904 -> 1.000.
**WHY the brain does ~0.95 and we do ~0.5:** it (a) detects essentially all events; (b) assigns roles by
INTEGRATING cues (word-order + animacy + agreement + verb-specific selectional structure + world knowledge +
real hierarchical syntax) instead of our "nearest post-verbal nominal" default, which alone loses 31%; (c)
resolves interference by cue-based retrieval. My pass faithfully closes the DROP slice; a blowout requires the
wrong-bind slice, which is the harder, DIFFERENT problem. This is not a ceiling of the drop-fill — it is the
drop-fill being one (well-executed) slice of a three-slice gap.

## OWNER-DIRECTED EXTENSION — attacking the WRONG-BIND bucket (the +31-point lever; "I want the blowout")
Beyond the drop-fill (this problem's scope), the owner directed attacking the biggest bucket — wrong-binds
(0.309). DIAGNOSIS: 63% of wrong-binds are the DOUBLE-OBJECT/theme signature — the reader grabs the NEAREST
post-verbal noun (the recipient) but the patient is a FARTHER post-verbal noun (the theme): "gave Mary a book"
-> reader picks *Mary*, gold is *book*. This is STRUCTURAL (verb argument structure), NOT p2's refuted
plausibility re-selection — a door p2 never opened.
- **THE FIX (brain-foundational + generalizing): the DOUBLE-OBJECT CONSTRUCTION (Goldberg 1995).** "V NP1 NP2"
  with NO dative/oblique preposition assigns NP1=recipient, NP2=theme(patient) CONSTRUCTIONALLY — independent
  of the verb (so it generalizes to novel verbs, "she faxed him the report"). Re-assigning patient = the 2nd
  post-verbal nominal when the no-prep construction holds: **QA-SRL +0.0457 [+0.0301,+0.0621]** (fires 746,
  0.4808 -> 0.5265) and it GENERALIZES: across VERBS (22+ distinct, 21 NOT in the substrate's hand-authored
  DITRANS_VERBS list — the hand list alone fires 43 / +0.0073, so the CONSTRUCTION generalization is the win)
  and across ERAS (**19c LitBank +0.0222**, fires 1315). NO tuning (a fixed construction rule) — held-out +
  cross-era by design.
- **THE CONSTRUCTION GATE IS PROVEN LOAD-BEARING (not "pick the 2nd noun").** Control: picking the 2nd noun
  when there IS a preposition (V NP *to/for* NP — prepositional dative, where the 1st noun is the theme) LOSES
  **-0.0574 [-0.0773,-0.0391]**. The no-prep/with-prep FLIP is exactly the double-object vs prepositional-dative
  distinction — the preposition gate is the brain-faithful discriminator (Goldberg), and it carries the effect.
- **HONEST BOUNDS.** (a) The eADM ANIMACY discriminator (recipient animate / theme inanimate — the guard against
  predicatives "called it nonsense") does NOT help: the substrate's `animacy_lexicon` is too coarse and
  mis-handles proper NAMES ("John"->object), so it fires ~47× and ties its scramble — an ADJACENT-ORGAN gap
  (fix PROPN animacy), not a blocker (predicatives are rare enough that the bare construction nets +0.046).
  (b) This recovers ~15% of the wrong-bind bucket (the double-object sub-pattern), NOT all of it — the remaining
  wrong-binds are PP-attachment / coordination / genuine parse errors. So it is a REAL chunk of the blowout, not
  the whole 0.31: combined with drop-fill the reader moves ~0.48 -> ~0.57, still short of the brain's ~0.95.
- **INTEGRATED PASS + the era-robustness finding (the load-bearing honesty result).** Composing the levers and
  measuring cumulatively, both eras: DROP-FILL (reusing relcl_resolver) is the robust WORKHORSE — QA-SRL
  0.4808 -> 0.5506 (+0.070), 19c LitBank 0.1852 -> **0.2949 (+0.110)** — and it BEATS my original grounded
  drop-fill on both eras (reuse wins again). But the RE-SELECTION levers are FRAGILE across eras: the
  double-object fix adds +0.023 on modern but slightly HURTS 19c (-0.007); a preverbal-gap RE-BIND of committed
  picks HURTS BOTH (-0.006 / -0.015) and is DROPPED. Integrated (all three) = 0.5681 QA / 0.2757 LitBank — on
  19c, drop-fill ALONE (0.2949) BEATS the integrated pass, because re-selection adds noise where the parse is
  unreliable. **This re-confirms the core finding at the integrated/era level: recovering a MISSING answer
  (drop-fill) generalizes robustly; RE-SELECTING a COMMITTED pick (double-object / preverbal re-bind) does not
  — it is era-sensitive and can hurt.** So the robust, generalizing blowout is the drop-fill (reader -> ~0.55
  modern / ~0.295 19c, +0.07-0.11); double-object is a MODERN-ONLY add; preverbal re-bind is a negative.
- **SCOPE:** this is the WRONG-BIND / role-assignment problem (converges with the concurrent graded-role lane),
  prototyped here at owner direction — NOT part of this problem's drop-fill PASS. It is brain-foundational
  (Goldberg constructional role assignment; the preposition/construction gate proven), generalizing (verbs +
  eras), and reuses the substrate's own frame lexicon; the full wrong-bind fix (other constructions + a fixed
  PROPN-aware animacy guard) is the role-assignment problem's build.

## CUE-INTEGRATION ROLE ASSIGNER — the era-robust wrong-bind lever (owner: "research-drill + achieve the blowout")
The single-cue re-selections don't generalize (double-object modern-only; preverbal negative). The brain doesn't
take one parse as truth (this problem's thesis) — it assigns roles by PARALLEL CUE-INTEGRATION / constraint
satisfaction (Competition Model, MacWhinney/Bates; McRae-Spivey-Tanenhaus 1998; cue-based retrieval, Lewis &
Vasishth). I BUILT that: assign patient = argmax over candidates of `w_pos*POSITION + w_anim*INANIMACY(name-
aware) + w_fit*SELECTIONAL_FIT + w_constr*DOUBLE_OBJECT`, one competition handling both the parse's drops AND its
wrong-binds. Weights swept (OUR-INVENTION); best = pos 1.0 / anim 0.0 / fit 0.3 / constr 0.6. (Research drills to
ground this were dispatched but died on a transient API outage — built from the known literature; retry pending.)
- **RESULT (honest, controlled). The reader reaches 0.575 (modern QA-SRL) / 0.455 (19c LitBank)**, up from the
  wired parse-router 0.481 / 0.185. Against the DEGRADED wired parser: +0.094 / +0.270. But the fair floor is a
  SAME-CANDIDATE POSITION baseline (position over the pos-tagger's full nominal inventory): pos-only = 0.477
  (modern) / **0.428 (19c)**. So the honest gain the CUES add over position is **QA-SRL +0.0976 [+0.0802,+0.1152]
  and 19c LitBank +0.0272 [+0.0178,+0.0368]** — CI-separated on BOTH eras (it generalizes).
- **ERA-ROBUSTNESS THESIS VALIDATED (the deep win).** On 19c the arc_parser COLLAPSES (wired 0.185) but a
  cue-integration that does NOT depend on the parse holds up (0.455, 2.5x better). The huge +0.27-vs-wired is
  MOSTLY clean-position beating the degraded parser — which is exactly the point: parse-as-truth is fragile
  across eras; cue-integration is robust. This is the Competition-Model prediction, measured.
- **CONTROLS.** Verb-specific SELECTIONAL FIT is load-bearing on MODERN (cue - fit-scrambled +0.0172
  [+0.0084,+0.0263]) but NOT on 19c (-0.0040, ties — the centroids are fit on modern QA-SRL and don't transfer to
  19c vocabulary; the 19c cue-gain is the construction, not fit). ANIMACY swept to weight 0 (the coarse,
  name-broken animacy organ doesn't help — the adjacent-organ gap again). Construction no-prep gate proven
  earlier (with-prep loses -0.057).
- **HONEST CEILING — why this is NOT yet 0.90.** Cue-integration is the right brain-foundational, era-robust
  direction and it generalizes, but it lands at ~0.575 / 0.455, not the human ~0.95, because (a) the SELECTIONAL-
  FIT cue is COARSE (p2's grounded-space ceiling; adds only +0.017 modern, 0 on 19c) — a RICHER verb-role event
  store (Phase-1) is the lever; (b) EXTRACTION-MISS (~0.10) is untouched (event detection); (c) many wrong-binds
  need cues we can't yet compute glass-box (fine thematic fit, real agreement). The blowout is CUE-QUALITY-bound
  and EVENT-DETECTION-bound — both large builds the ceiling analysis already named — NOT another rule on the
  current parse. What I proved: the ARCHITECTURE (parse-as-evidence + parallel cue-integration, not parse-as-
  truth) is right and era-robust; the remaining gap is cue QUALITY + event recall.

## REUSE THE VALIDATED ORGAN + THE RESEARCH-DIRECTED FIXES (owner: "look at the organs + prototype the fix")
Enumerating the substrate (my own discipline, owner-held) surfaced that I HAND-ROLLED an organ that already
exists: **`hdlab/graded_role_assigner.py`** — the Competition-Model routed cue-integration role assigner (landed
2026-08-27, 6/6 witness), encoding the fidelity lesson my flat integrator VIOLATED: "the lever is ROUTING, NOT
REPLACEMENT — a flat integrator wrecks canonical cases." `hybrid_role_patient` keeps the word-order default on
confident cases and invokes the graded competition (`hdlab.graded_competition`; cues order/adjacency/passive/
gap/unacc/by-agent/animacy by LEARNED validities) only on the non-canonical residual.
- **REUSE WINS.** The validated organ ALONE reaches **0.6076 (modern QA-SRL, +0.1268 over wired)** — BEATING my
  flat integrator (0.575), exactly as its docstring predicted. (19c: 0.4104; neither the organ nor the flat
  version dominates both eras — the organ is stronger on modern, the flat cue-set on 19c.) This is the BEST
  who-did-what result, from a VALIDATED organ, not a hack.
- **RESEARCH FIX #1 (agent/patient centroid CONTRAST) — PROTOTYPED, HONEST NEGATIVE.** A 2-drill research retry
  (which validated the design: structured role-separated distributional models discriminate agent/patient at
  62-72%; a single patient centroid caps near chance — Chersoni/Santus/Lenci 2017) named the agent-centroid as
  the top fit fix. I built it by reusing `extract_triples` (already yields AGENT+PATIENT triples) + grounded
  centroids. Result: patient-only fit HELPS (+0.039 modern), but the CONTRAST (patient_fit − agent_fit) HURTS
  (-0.0124 modern [-0.022,-0.004]; -0.0223 on 19c) — because in the COARSE 12-d grounded space the agent and
  patient centroids are too similar (subtracting removes shared signal). This CONFIRMS the research's caveat and
  p2's coarse-space ceiling: the contrast needs a DISTRIBUTIONAL (PPMI role-filler) space, not the grounded
  centroid — a FOUNDATION build, not a free add.
- **THE BLOWOUT IS GATED ON TWO NAMED FOUNDATION BUILDS (ceiling analysis + research CONVERGE).** (1) A
  DISTRIBUTIONAL agent+patient role-filler space from a large MODERN parsed corpus (DM/TypeDM + Weighted-Overlap
  scoring; ρ≈0.50, agent/patient 62-72%), applied at inference by LEMMA lookup (no parse → era-robust) — the
  research's decisive test: does it transfer to 19c? (2) A NOMINALIZATION / light-verb / copula lexicon (NOMLEX-
  style, glass-box) for the ~10% EXTRACTION-MISS bucket (missed events are largely non-verbal predicates). Both
  are the "foundation is free to build" regime, NOT more heuristics on the noisy parse. WHAT IS PROVEN HERE: the
  ARCHITECTURE (parse-as-evidence + routed parallel cue-integration, era-robust) is right and the validated organ
  delivers it (0.61 modern); the remaining gap to ~0.95 is cue QUALITY (distributional role-filler space) +
  event RECALL (nominalization lexicon) — two bounded foundation assets, precisely localized.

## THE BRAIN-FOUNDATIONAL FIT FIX, PROTOTYPED IN FULL — a DECISIVE negative that relocates the ceiling
(owner: "prototype the brain-foundational correct fix, using organs where available"). The research's
highest-ceiling recommendation was a ROLE-SEPARATED DISTRIBUTIONAL selectional-preference model (Baroni & Lenci
DM; McRae thematic fit): per verb, PATIENT-centroid = mean vector of nouns that ACTUALLY occur as its object,
AGENT-centroid = its subjects; score candidates by the contrast in a RICH distributional space. I built exactly
this, reusing organs (`extract_triples` for the role-filler experience, `graded_role_assigner` as the routing
base) and a large-corpus DISTRIBUTIONAL FOUNDATION ASSET (GloVe-wiki-gigaword-300, 6B tokens, 400k vocab, 300-d
— a static offline lookup, NOT an LLM; admissible per "foundation is free to build"; the substrate's own
`random_indexing`/`ppmi_sparse_encoder` organ would build the production version). GloVe separates roles sharply
(cos(food,bread)=0.51 vs cos(food,man)=0.17) where the 12-d grounded space could not.
- **RESULT — the rich distributional fit does NOT deliver the blowout.** QA-SRL: +grounded-fit 0.567,
  +GloVe-CONTRAST 0.575 = **+0.0080 [-0.0049,+0.0211] (n.s.)** — a 6-billion-token role-separated model TIES the
  coarse 12-d grounded centroid. 19c LitBank: +grounded 0.448, +GloVe 0.428 = **-0.0192 [-0.0295,-0.0091]** —
  the distributional fit is WORSE on 19c (era-transfer FAILS: modern centroids don't match 19c vocabulary — the
  research's flagged #1 risk, now measured). Either fit cue adds only ~+0.03-0.04 over position on modern, ~0 on
  19c.
- **THE CEILING IS RELOCATED (the decisive finding of the whole blowout push).** who-did-what is NOT
  fit-quality-bound. English weights WORD ORDER so heavily (Competition Model cue validity) that even the best
  possible selectional cue — a billion-token role-separated distributional model — is MARGINAL over position and
  does not transfer across eras. So the gap from ~0.61 (the validated graded organ, modern) to human ~0.95 is
  NOT closable with richer meaning cues; it is bound by (1) STRUCTURAL PARSE errors on the residual wrong-binds
  (a better parser — which itself degrades on 19c, so the era-robust substitute IS the cue-integration I built),
  and (2) EVENT-DETECTION recall (~10%, the nominalization lexicon — the one remaining untested lever). This
  CORRECTS the research's fit-first hypothesis for THIS task, evidenced by building the rich version and
  measuring it tie/lose. The brain-foundational ARCHITECTURE (routed parallel cue-integration, era-robust) is
  right and delivered (0.61 modern via the validated organ); a richer selectional cue is NOT the lever.

## EVENT-DETECTION (the last untested lever) — and it EXPOSES the deep mechanism gap
Diagnosing the ~10% EXTRACTION-MISS bucket (owner: do the last lever): it is NOT nominalizations (QA-SRL
predicates are verbal). **71% are the gold VERB mis-tagged as a NOUN, 15% as an ADJ** by the pos-tagger —
verb/noun homographs in SVO clauses ("Wet clay FORMS mud", "The atmosphere SUPPORTS life", "The Sun HEATS
Earth's surface"). A STRUCTURE-AWARE predicate detector (a nominal-tagged token in an unambiguous
subject-_-object predicate slot with no other finite verb IS the predicate) would recover the event: 51% of
misses sit in such a slot; recovering them lifts who-did-what +0.0234 overall. Modest, but it EXPOSES the deep
problem the owner named: we run a BOTTOM-UP PIPELINE (tag -> detect -> assign), and it fails on the homographs
precisely because it commits POS before structure. **The brain does NOT tag-then-parse; it infers the clause
structure JOINTLY / GENERATIVELY — the predicate slot between a subject and an object DEMANDS a verb, so
"forms" is never a noun there.** This is the SAME reason cue-integration plateaus: both are piecewise
approximations of a JOINT GENERATIVE computation we have not yet replicated. (This is the honest answer to
"do we understand EXACTLY how the brain does this?" — NO, not yet; see the mechanism drill dispatched at submit.)

## BRAIN-FUNCTION BENEFIT AUDIT (literature-grounded — what we replicate vs FORGO)
A research drill (18 sources) grounds exactly which benefits of the brain's predictive / noisy-channel /
revising comprehension function this pass conveys. It is NOT "all of them" — and honestly naming the gap is
the point. The pass faithfully conveys the ONE benefit that lifts who-did-what recall; the rest are either
inapplicable to this task, captured in a sibling organ, or a NAMED separate problem.

| Brain-function benefit (theory) | This pass (sentence-local, position-primary + animacy-under-conflict drop-fill) |
|---|---|
| Recover a DROPPED argument via a DELETION-type edit (Levy 2008 noisy-channel; Gibson/Bergen/Piantadosi 2013). The Bayesian size principle makes deletion cheaper than insertion — which independently explains why the parser DROPS rather than mis-inserts. | **CONVEYS** — the core operation; matches the deletion>insertion asymmetry. |
| Plausibility/world-knowledge-WEIGHTED posterior over candidate fillers (noisy-channel). | **MOSTLY FORGOES** — the grounded selectional prior loses globally; plausibility re-selection failed (p2). Reconciled: noisy-channel plausibility effects are TASK-DEPENDENT (Ryskin et al. 2018) — strong under explicit correction, weak in the implicit reading/coverage regime this pass probes. Stated as a DISCREPANCY, not glossed. |
| Cue-validity / cue-cost integration: cheap DOMINANT cue first, costlier SUBORDINATE cue under CONFLICT (Bates & MacWhinney 1984; eADM Bornkessel-Schlesewsky). | **CONVEYS — the strongest match.** Global word-order dominance + conflict-subset animacy is a near-textbook replication; Weckerly & Kutas 1999 shows animacy intruding on English object-relatives precisely under non-canonical conflict. (Caveat: the classic paradigms test PRESENT NPs, not gap-filling — our extension is literature-CONSISTENT, not directly replicated; confidence ~0.45.) |
| Construction-cued, structurally-licensed GAP identification + case/grammatical-cue retrieval of the displaced filler (Crain & Fodor 1985; Stowe 1986; Wagers & Phillips 2014). | **PARTIALLY** — finds the right SLOT (acts on parser-flagged drops) but resolves WHICH filler by a linear-position PROXY that free-rides on English SVO (the true filler is usually also nearest). Predicted to fail where INTERVENING distractor NPs sit between filler and gap (Van Dyke & McElree interference) — the literature-sharp characterization of our residual 45%. |
| Online PREDICTIVE gap-positing before bottom-up confirmation; incrementality (Active Filler Strategy; filled-gap effect). | **FORGOES** — this is an offline post-parse pass, no real-time predictive timing. (The incremental parser is a separate organ / concurrent problem.) |
| REANALYSIS / overwrite of an actively-wrong committed structure, limiting lingering misinterpretation (Ferreira 2003; Christianson et al. 2001; P600/LIFG). | **FORGOES — by design, correctly for THIS corpus.** Tested null; expected because a DROP is the parser correctly declining to commit (no false commitment to overwrite). Falsifiable prediction: reanalysis SHOULD show a benefit on a GARDEN-PATH-heavy corpus (reduced-relative / NP-S ambiguities) — a named follow-on, not a gap here. |
| GRADED / distributional confidence over multiple parses -> cheap CROSS-SENTENCE reweighting + metacognitive comparison (MacDonald 1994; Kuperberg & Jaeger 2016). | **FORGOES** — a single discrete commit, sentence-local. This is the substrate's standing "discrete where the brain is graded" theme (a concurrent problem). |
| Online-ADAPTIVE noise model tuned to local error statistics (Ryskin/Poppels/Gibson). | **FORGOES** — a fixed heuristic; no adaptation to genre/era error rates (relevant to the 19c degradation). |

**Verdict on "fully brain-foundational / all benefits":** the pass is a FAITHFUL instantiation of the specific
benefit it targets — noisy-channel DELETION-recovery of a dropped argument, resolved by the Competition-Model
cue hierarchy (word-order dominant, animacy under conflict). It does NOT convey the broader function's other
benefits (plausibility-weighted posterior, construction-cued retrieval, reanalysis, graded distribution,
incrementality, adaptive noise) — and each of those is now NAMED with its owning theory and its status
(inapplicable-here / sibling-organ / separate-problem). That IS the complete honest fidelity picture for a
bounded who-did-what-RECALL problem; conveying the forgone benefits means building the named separate organs.

## Brain-fidelity labeling (PINNED vs OUR-INVENTION)
- **PINNED (replicated / CONFIRMED):** noisy-channel comprehension = parse-as-EVIDENCE + a plausibility prior,
  NOT parse-as-truth (Levy 2008; Gibson 2013); the FILLED-GAP / active gap-filling reflex (Crain & Fodor 1985;
  Stowe 1986) — recover the argument at the empty slot — which the DROP-FILL directly instantiates. **The
  Competition Model cue-validity ranking for English (MacWhinney; Bates & MacWhinney) is EMPIRICALLY CONFIRMED
  here: word-order/POSITION >> animacy >> lexical-plausibility** — all three meaning/animacy cues fail to beat
  linear position for the drop-fill, and animacy ties its own scramble (English is the word-order-dominant
  extreme). This is why the plausibility prior is not the target-selector on modern edited prose.
- **OUR-INVENTION-UNDER-TEST (swept, not adopted):** the surprisal threshold tau (swept {0.5,1,1.5,2}), the
  word-order likelihood weight beta (swept {0.1,0.2,0.35,0.5}), the precision floor for pre-verbal promotion
  (swept {0,0.3,0.5}); the grounded 12-d space as the prior basis (its coarseness is p2's measured ceiling).
  Selected point tau=2.0 beta=0.35 prec_floor=0.3 by the wired-vs-wired lower-CI bound; the effect is robust
  across the frontier (reported in metrics.json `sweep`).

## What I did NOT establish (and would withdraw first if wrong)
- **First to withdraw:** that the grounded selectional PRIOR matters at all on modern text — a no-prior
  structural fill TIES it on QA-SRL; if the 19c margin (+0.022) also fails to replicate, the honest claim is
  "the pass is a STRUCTURAL drop-fill (recover the missing argument by position)," full stop, needing no
  grounded space and no fitted asset. (The DROP-FILL recovery itself — the headline — is the robust result.)
- EXTRACTION-MISS is OUT OF SCOPE: where the reader never detected the event (~16% of gold), there is no event
  to revise; those stay errors for every arm (baked into the recall denominator). Event-detection recall is a
  separate front-end gap.
- The population is non-pronoun gold PATIENTS bound through the live read(); AGENT recall (agents are often
  pronouns the binder cannot bind) is untested. Voice is unlabeled in the LitBank gold, so its non-canonical
  stratum is pre-verbal-gap only (no passive slice there).
- The selected params are tuned on QA-SRL dev+test pooled; the 19c LitBank result uses the SAME params (a
  genuine transfer), and the sweep frontier shows the effect is not a single-point artifact.

## AUDIT UPDATE (fold into notes/BRAIN_FOUNDATIONAL_AUDIT.md sec 2b)
E2 situation_reader / predictive_reader: the parse-recall ceiling that caps who-did-what/SPACE/belief is now
CHARACTERIZED. A parse-RECALL pass RECOVERS who-did-what CI-separated over the strongest real floor on modern
QA-SRL (+0.060 over the wired parse-router) and 19c LitBank (+0.059 over the positional floor), concentrated in
non-canonical (passive / pre-verbal-gap) constructions. NEW MEASURED (converges with p2 from the recall side):
the entire gain is DROP-FILLING — recovering the patient the parse left EMPTY ('?') — triggered by a STRUCTURAL
coverage violation; a surprisal gate on COMMITTED picks adds nothing (dropped-only ties the surprisal-gated
pass, +0.0625 over wired). So `predict_surprisal` is NOT needed to DRIVE this recall (it remains p2's validated
error-RISK FLAG, but the recall pass is asset-free). Within drop-filling the TARGET cue is POSITION,
not the VERB-SPECIFIC selectional prior AND not ANIMACY — a no-prior structural fill ties on modern text, and
an animacy-cued fill (the Competition-Model/eADM primary undergoer cue, via `animacy_lexicon`) ties BOTH
position and its own scrambled twin (the animacy info is inert here). This EMPIRICALLY CONFIRMS the Competition
Model cue-validity ranking for English (word-order >> animacy >> lexical-plausibility). The prior earns its
keep only where the parser degrades (19c prose, +0.022). The "prior is the lever" verdict inherited
from SPACE does NOT transfer to who-did-what: the lever is the structural drop-fill (the likelihood/parser-RECALL
term the audit named). The noisy-channel LEVER is dimension-specific (SPACE persistence: lever; who-did-what
selectional: not).

## PROPOSED hdlab CHANGE (Q111 — strategy lands; a proposed diff, not a landed one)
A default-off flag `predict_revise=False` on SituationReader (byte-identical when off; the additive-metadata
pattern of causation/timeline). When ON, AFTER the role read, run a post-read parse-RECALL pass over sm.events:
for each event whose patient is '?' (DROPPED — the structural coverage violation), fill it by REUSING the
already-validated `hdlab.relcl_resolver.resolve_patient(toks, pos, v)` (the active-filler filler-gap resolver:
passive-subject / object-gap-filler / word-order routes) as the fill TARGET, writing the recovered head to
`EventRecord.patient` and preserving the original as `EventRecord.patient_prerevise` (glass-box, inspectable).
Reusing that organ beats a raw position heuristic (+0.0066 overall / +0.057 on drops) and is more brain-faithful
(measured). **The recall pass needs NO fitted PredictiveReader asset and NO surprisal gate** (drop-filling
captures the full gain; the surprisal-triggered revision of committed picks adds nothing and slightly hurts).
NO external LLM, NO spaCy (the reader's own pos_tagger + relcl_resolver). Compose with `role_route='wired'`.
Register `predict_revise_live_reader_v1` at land; witness required. Do NOT wire a post-verbal re-selection OR a
surprisal-gated reanalysis of committed picks (p2's proven NEGATIVE, re-confirmed here) — the pass is DROP-FILL
/ recall-scoped only. The unmarked-interference remainder (reduced relatives / coordination) is left to the
substrate's own named "interference resolution" open problem (a graded extension of `content_addressable_
retrieval` / `graded_competition`), NOT this wire.

## ADJACENT COMPONENTS — fidelity / opportunity (seeds the next problems)
| Component | Brain role | Fidelity now | Opportunity -> next problem |
|---|---|---|---|
| `arc_parser` (UD-EWT-trained) | the parse EVIDENCE/likelihood | GENERALIZES POORLY to 19c prose (0.185 < 0.229 positional there) | An era-robust / self-supervised parse, or the predict-and-revise pass AS the robustness layer (it already recovers the parser's 19c degradation). |
| `predictive_reader` (12-d grounded centroid) | the plausibility prior + violation gate | valid GATE, coarse target-SELECTOR (p2 + here) | The Phase-1 STRUCTURED verb-role exemplar/event store is the ONLY route that could make the verb-specific prior a WHICH-argument lever; the coarse space cannot. |
| positional role binder | who-did-what | parse-as-TRUTH; drops pre-verbal patients | THIS pass augments its RECALL (the proposed wire). |
| `animacy_lexicon` (WordNet-backed) | the Competition Model / eADM animacy cue | PINNED cue, 88% candidate coverage, BUT a name-homograph bug (PROPN "John"->object; PROPER_NOUN_OVERRIDES empty) | Fix PROPN handling (names default animate); measured here to be a LOW-VALIDITY cue for English who-did-what (ties its scramble) — high validity would show on a case-rich language or a genuinely position-ambiguous slice. |
| `relcl_resolver.py` (active-filler filler-gap; landed 2026-08-27, validated) | the brain's actual gap-resolution (filled-gap effect, Stowe 1986; Frazier & Flores d'Arcais) | EXISTS + validated (0.953 vs 0.499 floor); glass-box, no arc graph | **REUSE it as the drop-fill target** (measured +0.0066 overall / +0.057 on drops) — the proposed wire below. Handles object-relative + passive; unmarked reduced-relatives are out of its construction gate. |
| `content_addressable_retrieval` / `graded_competition` / `coreference_resolver` | cue-based content-addressable RETRIEVAL — the SAME primitive for coref AND filler-gap (Lewis & Vasishth 2005; McElree) | primitive PRESENT; `content_addressable_retrieval` states "interference RESOLUTION is a separate open problem" | The unmarked-interference residual (reduced relatives / coordination) is a GRADED EXTENSION of this existing primitive — the brain's reuse, not a new build. |
| event detector | which predicates fire | ~16% extraction-miss ceiling (measured) | Event-DETECTION recall — a separate front-end gap this pass cannot reach. |

## FOLLOW-ONS (precisely scoped)
1. **ANSWERED by the drill:** the surprisal gate is NOT needed for RECALL — a purely structural DROP trigger
   captures the full gain, so the hdlab wire needs no fitted `predictive_reader` asset. (Remaining sub-question:
   is the grounded-prior fill worth its cost over a position-only fill? Only on 19c prose, +0.022.)
2. Event-DETECTION recall (the ~16% extraction-miss ceiling — where the reader never detected the event, so
   there is no dropped slot to fill) — a separate front-end organ.
3. A RICHER (structured verb-role exemplar/event) prior — the only route to a verb-specific WHICH-argument
   lever (p2's Phase-1 meaning-supply build); the coarse grounded space cannot (confirmed here + p2's 4-way
   negative). Would help the drop-fill TARGET selection where position is ambiguous (multiple pre-verbal
   nominals), most on degraded parses / archaic prose.
4. AGENT-role recall — ANSWERED by the drill: agents are dropped only 1.2% (canonically pre-verbal, so the
   positional rule catches them); the drop-fill is structurally patient-specific. Agent errors are wrong-binds
   (re-selection territory, refuted). No cross-role generalization to build.
5. **INTERVENING-NP interference test — DONE (above):** position recall collapses 0.754 -> 0.000 the moment a
   distractor NP intervenes; the residual IS retrieval interference, and a cheap construction heuristic can't
   crack it. The real filler-gap resolver (concurrent relcl problem) is required, now with a measured target.
6. **Reanalysis on a GARDEN-PATH corpus (falsifiable):** the null reanalysis result here is expected for a
   coverage-drop corpus; the literature (Ferreira 2003; Christianson 2001) predicts reanalysis SHOULD show a
   CI-separated benefit on reduced-relative / NP-S garden-path items — worth a targeted test to EARN the claim
   "reanalysis is task-specifically null, not universally null."
7. GRADED / distributional drop-fill (keep alternatives for cross-sentence reweighting) — the substrate's
   "discrete where the brain is graded" theme; a concurrent problem.

## TLDR (plain English)
Our reader runs one grammar-parse of each sentence and trusts it, so when the thing being acted upon comes
BEFORE the verb (as in "the book that the man read" or "the door was opened") it simply drops it — it ends up
with no answer for "acted on what?". Brains don't stop there; they notice the gap and go back to fill it. I
built that step: whenever the reader has NO patient for a verb, it goes back over the whole sentence and picks
up the dropped word. On thousands of real modern sentences it recovers who-did-what noticeably more often than
the best single parse (about six more correct answers per hundred), the gains land exactly on the hard
before-the-verb sentences, and the easy ones are left untouched. It also works on 200-year-old novels. Two
honest surprises from drilling it: (1) the whole benefit comes from FILLING THE BLANKS — going back to
"second-guess" answers the reader already committed does not help at all (and slightly hurts), which matches
what an earlier study found; so we don't need the reader's "surprise" detector to drive this. (2) What picks
the right word to fill the blank is mostly its POSITION, not the reader's sense of what's "plausible" — the
plausibility sense only earns its keep on the old prose where the grammar-parser is shakier. So the fix is
simple and cheap to build, and we now know precisely where the reader's who-did-what ceiling is and how to lift
part of it.

## QUESTIONS
None.

## NEXT STEPS
Strategy lands the proposed default-off `predict_revise` wire (Q111, witness required) — and the drill already
answers how heavy it needs to be: an ASSET-FREE structural DROP-FILL (no fitted predictor, no surprisal gate)
captures the full modern-era gain, with the grounded-prior fill an optional add worth only its 19c-robustness
margin. Beyond the wire, the highest-value follow-on is #3 (a structured verb-role exemplar/event store) — the
only route to a verb-specific WHICH-argument lever for the drop-fill target where position is ambiguous, and
the same Phase-1 meaning-supply build p2 named.
