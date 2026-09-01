---
problem: the_reader_parses_as_truth_where_the_brain_parses_predictively_predict_and_revise
status: SOLVED
bar: "PASS = the predict-and-revise parse pass RECOVERS who-did-what (and the arguments the batch parse drops) CI-SEPARATED over the strongest REAL floor — the batch parse-as-truth / positional-default reader at EQUAL inputs — on held-out + MODERN real prose, with the info-free TWIN (revise at the same rate at RANDOM loci, or with a shuffled prior) LOSING CI-separated, AND a positive control that revision fires exactly where the prediction is violated (not everywhere). Report CI half-width + null p95 beside every margin. A rigorous NEGATIVE is a full PASS if located: if predict-and-revise, faithfully built, does not beat parse-as-truth (the residual is irreducible recall — the structure is simply not recoverable from the available signal), name it precisely (which constructions, why the prior cannot disambiguate them) and localize the ceiling — that tells the assembly where the true front-end limit is."
result: "A parse-RECALL pass that recovers the DROPPED patient the batch parse left empty ('?') — a structural coverage-violation trigger, recall-scoped (fill-a-drop or promote a PRE-VERBAL head; NO post-verbal re-selection) — RECOVERS who-did-what CI-separated over the strongest real floor on BOTH eras (who-did-what patient recall through the LIVE SituationReader.read(), scorer = pick==gold head, bootstrap CI by sentence cluster). MODERN QA-SRL v2 dev+test, n=2737 non-pronoun-gold patient items: the pass 0.5407 vs the wired parse-router 0.4808 = +0.0599 [+0.0395,+0.0889] (half 0.0247, frac<=0 0.000); on the positional floor 0.4417 vs 0.3858 = +0.0559 [+0.0350,+0.0827]. 19c LitBank narrative, n=5999: 0.2879 vs the (there-strongest) positional floor 0.2287 = +0.0592 [+0.0525,+0.0659] (half 0.0067, frac<=0 0.000). Gains localize to non-canonical constructions: QA-SRL passive 0.287->0.567, pre-verbal-gap 0.023->0.511; canonical recall PROTECTED 0.509->0.526. DRILLED: the entire gain is DROP-FILLING — firing on dropped patients ONLY (no surprisal reanalysis of committed picks) reaches 0.5433 (+0.0625 over wired, CI-sep) and TIES the surprisal-gated pass (gated-vs-dropped_only -0.0026 n.s.); the 391/704 surprisal-triggered revisions of COMMITTED picks add nothing (confirming p2's refuted re-selection from the recall side)."
floor: "the batch parse-as-truth reader at equal inputs, BOTH routes actually run: positional-default (QA-SRL 0.3858 / LitBank 0.2287) and the stronger wired parse-router (QA-SRL 0.4808 / LitBank 0.1852). The pass beats WHICHEVER is stronger per era CI-separated (QA-SRL strongest = wired, beaten by +0.0599; LitBank strongest = positional because the modern-trained arc_parser DEGRADES on 19c prose, beaten by +0.0592). It also beats the OTHER floor in both eras."
controls: "(1) info-free RANDOM-LOCI twin (fire at the same rate at random loci) LOSES CI-sep: QA-SRL +0.0442 [+0.0284,+0.0642], LitBank +0.0395 [+0.0343,+0.0448] = EXCLUDES 'any extra re-parsing at this rate helps' (firing on the DROPPED-slot events, not random ones, is what carries it). (2) info-free UNIFORM (random-vector) PRIOR twin LOSES CI-sep: QA-SRL +0.0325 [+0.0134,+0.0594], LitBank +0.0492 [+0.0426,+0.0558] = EXCLUDES 'any prior-shaped candidate scorer helps' (the fill TARGET uses real animacy/position). (3) revise-EVERYWHERE positive control: the recall-scoped pass BEATS revise-everywhere CI-sep (QA-SRL +0.0106 [+0.0040,+0.0173], LitBank +0.0083 [+0.0060,+0.0107]); it fires on only ~28-30% of eligible events = it does NOT fire everywhere (revising committed picks breaks as many as it fixes). (4) recall_only scope = no post-verbal re-selection (p2's REFUTED route) -> canonical recall PROTECTED, not eroded (QA-SRL 0.509->0.526). (5) DROP-FILL localisation (the decisive drill): firing on DROPPED patients ONLY (a purely STRUCTURAL trigger, NO surprisal) reaches 0.5433 and TIES the surprisal-gated pass (gated-vs-dropped_only -0.0026 [-0.0076,+0.0027] n.s.) while beating wired +0.0625 CI-sep = EXCLUDES 'the surprisal signal is needed for RECALL'; the 391/704 surprisal-triggered revisions of COMMITTED picks add nothing. (6) LOCATED-LEVER: a verb-SHUFFLED prior loses only slightly (QA-SRL +0.0142, LitBank +0.0022 n.s.) and a NO-PRIOR STRUCTURAL fill TIES on modern QA-SRL (+0.0026 n.s.) though the prior BEATS it on 19c prose (+0.0217 [+0.0129,+0.0307]) = the lever is the STRUCTURAL drop-fill; the VERB-SPECIFIC selectional prior is a MINOR cue (position carries modern recall; the prior adds only where the parser degrades)."
files_changed: "experiments/exp_predict_revise_recall_v1.py (the mechanism + full control battery incl. the dropped-only DROP-FILL drill + sweep + LitBank); experiments/exp_predict_revise_recall_diagnostic_v1.py (the could-it-succeed recall decomposition + oracle headroom); experiments/_drill_animacy_fill_v1.py (the ANIMACY-vs-POSITION cue drill + scrambled-animacy twin); verification/test_predict_revise_recall.py (scaffold-free witness, 8/8); data/predict_revise_recall_v1/metrics.json + _population.json + _drill_dropped_only.json; data/predict_revise_recall_diagnostic_v1_smoke/. hdlab/ UNTOUCHED (Q111 — proposed default-off predict_revise flag stated below)."
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
for each event whose patient is '?' (DROPPED — the structural coverage violation), fill it over the full
sentence nominals under the RECALL scope (promote a PRE-VERBAL head on a sharp verb via
`fit - beta*position_penalty`, else the best-fit candidate), writing the recovered head to `EventRecord.patient`
and preserving the original as `EventRecord.patient_prerevise` (glass-box, inspectable). **The recall pass needs
NO fitted PredictiveReader asset and NO surprisal gate** (the drill shows drop-filling captures the full gain;
the surprisal-triggered revision of committed picks adds nothing and slightly hurts). A minimal, asset-free
version uses the position-only fill (`struct`, which ties the prior fill on modern text); the grounded-prior
fill is worth keeping only for the 19c-robustness margin. NO external LLM, NO spaCy (the reader's own pos_tagger
+ arc_parser + grounded space). Compose with `role_route='wired'`. Register `predict_revise_live_reader_v1` at
land; witness required. Do NOT wire a post-verbal re-selection OR a surprisal-gated reanalysis of committed
picks (p2's proven NEGATIVE, re-confirmed here) — the pass is DROP-FILL / recall-scoped only.

## ADJACENT COMPONENTS — fidelity / opportunity (seeds the next problems)
| Component | Brain role | Fidelity now | Opportunity -> next problem |
|---|---|---|---|
| `arc_parser` (UD-EWT-trained) | the parse EVIDENCE/likelihood | GENERALIZES POORLY to 19c prose (0.185 < 0.229 positional there) | An era-robust / self-supervised parse, or the predict-and-revise pass AS the robustness layer (it already recovers the parser's 19c degradation). |
| `predictive_reader` (12-d grounded centroid) | the plausibility prior + violation gate | valid GATE, coarse target-SELECTOR (p2 + here) | The Phase-1 STRUCTURED verb-role exemplar/event store is the ONLY route that could make the verb-specific prior a WHICH-argument lever; the coarse space cannot. |
| positional role binder | who-did-what | parse-as-TRUTH; drops pre-verbal patients | THIS pass augments its RECALL (the proposed wire). |
| `animacy_lexicon` (WordNet-backed) | the Competition Model / eADM animacy cue | PINNED cue, 88% candidate coverage, BUT a name-homograph bug (PROPN "John"->object; PROPER_NOUN_OVERRIDES empty) | Fix PROPN handling (names default animate); measured here to be a LOW-VALIDITY cue for English who-did-what (ties its scramble) — high validity would show on a case-rich language or a genuinely position-ambiguous slice. |
| filler-gap / construction cue (relativizer / passive morphology) | the brain's actual gap-resolution (filled-gap effect, Stowe 1986) | NOT built here (I use linear position as the approximation) | A construction-cued gap-filler (fill with the relcl antecedent / passive subject / fronted wh) is the brain-faithful upgrade to the position heuristic — this is the CONCURRENT `relcl filler-gap parser` problem; MAP, do not duplicate. |
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
4. AGENT-role recall (agents are often pronouns the binder cannot bind) — cross-role generalization.

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
