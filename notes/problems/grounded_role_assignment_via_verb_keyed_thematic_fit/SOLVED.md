---
problem: grounded_role_assignment_via_verb_keyed_thematic_fit
status: PARTIAL
bar: "On the MODERN UD-EWT role gold, scored on the HELD-OUT NON-CANONICAL subset (NOT the canonical-dominated aggregate): PASS = the gated verb-keyed thematic-fit role assigner beats BOTH the strongest floors -- naive-first-noun (word order) AND the current grammatical-function assigner -- on the non-canonical subset, CI-separated (bootstrap; CI half-width + null p95), with the info-free structure-shuffled twin LOSING; AND it does NOT regress canonical order or the reversible-ambiguous subset (the gate must stay OUT when order and fit do not conflict -- a fused-always control that hurts canonical FAILS). A rigorous NEGATIVE is a full PASS: if a faithfully-built conflict gate cannot separate override-when-conflicting from leave-alone-when-not without hurting canonical/reversibles, that is a real result -- name why (the gate's estimator, the fit vector quality, or the meaning-channel dependency), enumerated."
result: "TWO regimes. CLEAN-PARSE regime (modern UD-EWT core-arg gold, sentence-level held-out, n_test=3591): on clean parses the achievable non-canonical fix is STRUCTURAL ROUTING, not thematic fit (route_only 0.9858 beats word order +0.0493 [0.0418,0.0563] and graded_role +0.0810 [0.0718,0.0911], CI-sep, canonical/reversible unregressed); the fit gate does NOT CI-separate from graded_role on non-canonical because a gold parse removes the uncertainty fit resolves and graded_role hides an animacy plausibility cue -- the brief's premise is REFUTED for clean parses, exactly as noisy-channel theory predicts. WEAK-PARSER DEPLOYMENT regime (modern QA-SRL role-balanced comprehension gold read through the reader's OWN noisy live front-end, held-out; non-canonical/pre-verbal n=1224, positional floor 0.5): the fit gate DOES beat BOTH named floors on the non-canonical subset -- word order 0.1487 (paired +0.126 [0.102,0.149]) AND the landed graded_role 0.1176 (+0.157 [0.130,0.186]) -- CI-separated, with the info-free twin LOSING (0.2222, +0.052 [0.025,0.078]); AND it GENERALISES to held-out UNSEEN (verb,noun) pairs (n=299: gate 0.2308 beats word order +0.067 [0.020,0.114] and graded_role +0.054 [0.003,0.107], CI-sep; the twin edge does NOT survive to unseen, +0.023 [-0.027,0.074], so the count-fit signal is largely seen-pair memorisation). BUT the gate REGRESSES canonical (0.6552 vs word order 0.8358) and a full tau sweep shows the tradeoff is IRREDUCIBLE (no threshold beats the non-canonical floor while preserving canonical). So P1 (beat both floors + NO canonical regression) FAILS; the bar's P2 clause (a faithfully-built conflict gate cannot separate override-when-conflicting from leave-alone-when-not without hurting canonical, reason enumerated -> a full PASS) IS met, with power. The clean dominant fix is a better PARSER (spaCy structural roles 0.9959, no LLM)."
floor: "TWO strongest real floors, both recomputed on this population/subset: (a) naive-first-noun / word order = 0.9365 ALL, 0.0420 raw non-canonical, 0.0219 BALANCED non-canonical; (b) the landed grammatical-function assigner hdlab.graded_role_assigner = 0.9048 ALL, 0.9034 raw non-canonical, 0.4715 balanced non-canonical. Also reported: the degenerate always-patient constant = 0.958 raw non-canonical (the subset is ~96% patient), which is why the primary non-canonical metric is BALANCED accuracy (always-patient -> 0.5). Label-permutation null p95: route_only ALL 0.5837."
controls: "(1) info-free STRUCTURE-SHUFFLED twin (thematic-fit model trained on permuted role labels): LOSES CI-separated on balanced non-canonical (+0.150 [0.002,0.321]) and on the residual (+0.24 [0.08,0.40]) -- EXCLUDES 'any conflict signal helps'. (2) FUSED-ALWAYS control (fit overrides order whenever they disagree, no gate): HURTS canonical (0.752) and loses -- EXCLUDES 'skip the gate'; confirms conflict-validity must be a GATE not a weight (matches the fenced precision-weighted / linear-sum negatives). (3) ROUTING control (strong-passive routing with NO fit) beats both floors on the aggregate -- EXCLUDES 'the aggregate gain is from thematic fit' (it is not; it is structural routing). (4) canonical + reversible no-regression split -- EXCLUDES 'the fit gate trades canonical for non-canonical' (it does: composed fit gate canonical 0.886, reversible 0.571 -> the fused/low-tau fit arm FAILS the no-regression clause, the routing arm PASSES it). (5) noisy-channel CORRUPTION CURVE: masking passive morphology at prob p, the fit-gate-minus-structure gap grows monotonically (-0.103 -> -0.070) as structure degrades and the info-free twin never recovers -- the Gibson-2013 signature; EXCLUDES 'fit's value is regime-independent'. (6) independent derivation: gold roles from the UD GOLD parse; the gate's structure cues + fit are surface-derived -> no circularity."
files_changed: "experiments/_grounded_role_data.py; experiments/_grounded_role_gate.py; experiments/_grounded_role_protofit.py; experiments/exp_grounded_role_baseline_v1.py; experiments/exp_grounded_role_opportunity_v1.py; experiments/exp_grounded_role_uncertainty_curve_v1.py; experiments/exp_grounded_role_gate_v1.py; experiments/exp_grounded_role_noisy_parse_v1.py; experiments/exp_grounded_role_weak_parser_v1.py; experiments/exp_grounded_role_protofit_generalize_v1.py; experiments/exp_grounded_role_knn_fit_v1.py; experiments/exp_grounded_role_feature_fit_v1.py; verification/test_grounded_role_gate_organ.py; notes/problems/grounded_role_assignment_via_verb_keyed_thematic_fit/{research_thematic_fit_disambiguation_regime_2026-08-30.md, research_feature_based_role_generalization_2026-08-30.md, research_thematic_fit_ceiling_reconciliation_2026-08-30.md, SOLVED.md}. NO hdlab/ modified (Q111)."
reverify: ".venv/Scripts/python.exe verification/test_grounded_role_gate_organ.py"
---

## What was asked and what I found (the short version)

The brief: role assignment collapses on non-canonical order (passive / fronting / inversion); build a
verb-keyed grounded thematic-fit assigner with a conflict-recruitment GATE that overrides misleading word
order ONLY when order and plausibility conflict, and show it beats word order AND the current structural
assigner on the held-out non-canonical subset without hurting canonical/reversible.

I built the brain-faithful gate. The honest result is a PARTIAL with three findings, and the bar's own
"rigorous NEGATIVE is a full PASS -- name why" clause is the one that applies:

1. **The achievable non-canonical fix on clean parses is STRUCTURAL ROUTING, not thematic fit.** Recruiting
   the structural override cue ONLY when its validity is high (reliable strong-passive morphology: be/get/
   being + participle, or participle + by-PP), and using word order everywhere else, beats BOTH named floors
   on the aggregate, CI-separated, with canonical and reversible untouched. This needs no thematic fit.
2. **Grounded thematic fit's genuine contribution is confined to the structure-silent / uncertainty
   residual** -- the exact regime the brain recruits it for. There it beats word order and its own info-free
   twin CI-separated. But it does NOT CI-separate from the landed structural assigner, and it net-hurts
   canonical when applied indiscriminately.
3. **The brief's premise -- that thematic fit beats structure on non-canonical -- is REFUTED for clean gold
   parses,** and this is exactly what the brain-faithful theory predicts (see below). It is a regime
   artifact of scoring on gold parses, not a ceiling.

## HOW THE BRAIN DOES THIS (the opening move, and it reframed the whole problem)

I ran a literature drill (`research_thematic_fit_disambiguation_regime_2026-08-30.md`) before committing to a
design. The decisive, PINNED finding:

**Thematic fit is a DISAMBIGUATION-UNDER-UNCERTAINTY mechanism, not an override of certain structure.**
- Trueswell/Tanenhaus/Garnsey 1994: plausibility/animacy affects parsing AT THE POINT OF AMBIGUITY; with a
  morphologically UNAMBIGUOUS verb ("stolen") the ambiguity -- and the plausibility effect -- disappears.
- Gibson/Bergen/Piantadosi 2013 (noisy-channel): role-reversal (plausibility-driven) interpretation rises
  MONOTONICALLY with the noise/uncertainty in the surface signal; at zero noise (a gold parse) the posterior
  collapses onto the literal parse and plausibility contributes ~nothing. **The model literally predicts a
  null on clean parses.**
- MacWhinney Competition Model: a cue is recruited in proportion to its validity GIVEN THE CONFLICT; a
  high-validity unambiguous cue (clear morphology) suppresses reliance on lower-validity cues AND on
  plausibility.

So the gate is the noisy-channel decision: adopt the ORDER (canonical) reading unless the meaning it yields
is implausible enough that a non-canonical generation is the better explanation -- and that only bites when
the structural signal is weak/absent. I implemented exactly this: a JOINT clause-level decision comparing the
order reading against the role-swap reading by the RELATIVE thematic fit of the arguments, with a
construction-prior threshold tau that is WAIVED where reliable surface markedness licenses the non-canonical
reading (`_grounded_role_gate.assign_clause`). PINNED: thematic fit as a graded plausibility prior; conflict-
validity recruitment (gate, not weight); order as the default cue. OUR-INVENTION-UNDER-TEST (swept): the
recruitment threshold tau, the fit-estimator form.

## What I measured (all on the modern UD-EWT core-arg gold, sentence-level held-out, n_test=3591)

Reverify: `.venv/Scripts/python.exe verification/test_grounded_role_gate_organ.py` (9/9), which recomputes
every number below from source.

| arm | ALL | canonical | non-canon RAW | non-canon BALANCED | reversible | struct-silent residual (n=50) |
|---|---|---|---|---|---|---|
| word order (floor 1) | 0.9365 | 1.000 | 0.042 | 0.022 | 1.000 | 0.20 |
| graded_role (floor 2) | 0.9048 | 0.905 | 0.903 | 0.472 | 1.000 | 0.54 |
| **route_only (routing, NO fit)** | **0.9858** | 0.9967 | 0.832 | 0.434 | 1.000 | 0.20 |
| gate (count fit) | 0.881 | 0.887 | 0.803 | **0.610** | 0.571 | **0.68** |
| gate (prototype fit) | 0.948 | 0.976 | 0.550 | 0.479 | 0.857 | 0.36 |
| info-free twin | 0.835 | 0.838 | 0.790 | 0.460 | 0.429 | 0.44 |

Paired bootstrap (2000x), CI-separated where the lower bound clears 0:
- routing beats word order on ALL: **+0.0493 [0.0418, 0.0563]**; beats graded_role: **+0.0810 [0.0718, 0.0911]**.
- fit beats word order on BALANCED non-canonical: **+0.588 [0.435, 0.760]**; on the residual: **+0.48 [0.34, 0.62]**.
- fit beats its INFO-FREE TWIN on balanced non-canonical: **+0.150 [0.002, 0.321]**; on residual: **+0.24 [0.08, 0.40]**.
- fit vs graded_role: **NOT CI-separated** (residual +0.14 [-0.02, 0.30]; balanced +0.139 [-0.014, 0.307]).

## THE WALL, UNDERSTOOD (this is the deliverable the owner asked for -- why, deeply)

Two structural facts about clean gold parses of modern text make the brief's target unreachable, and both are
PREDICTED by the brain-faithful account, not accidents:

1. **Where a construction is surface-MARKED (strong passive morphology), the structural cue already resolves
   it** -- the landed graded_role scores 0.995 on morphology-marked non-canonical (207 of 238 items). Thematic
   fit has nothing to add there; the brain doesn't use it there either (Trueswell: unambiguous morphology
   removes the plausibility effect). This is the "regime where counting wins".
2. **The structural assigner is NOT structure-only: it contains an ANIMACY cue** -- a coarse but robust form
   of thematic fit (inanimate -> patient). Animacy does most of the disambiguation that richer verb-keyed
   fit would, and it is CLEANER than sparse selectional-preference counts, so richer fit cannot CI-separate
   from it on this data. (In the corruption curve, graded_role stays at 0.88 even when all passive morphology
   is masked -- that residual robustness is the animacy cue.)

The residual where fit CAN help -- structure-SILENT non-canonical -- is only ~50 of 3591 items on clean
parses (and only 10 of them are agent-role, the class the structural assigner misses entirely). It is far too
small, and too class-imbalanced (the non-canonical subset is ~96% patient, so the degenerate always-patient
constant scores 0.958 on raw accuracy), to CI-separate a richer-fit gate from graded_role on RAW accuracy.
On BALANCED accuracy (which neutralises the imbalance) fit's contribution is visible and beats word order and
its twin -- but not graded_role's animacy cue.

**The corruption curve is the falsifiable confirmation.** Masking the passive morphology at probability p
(Gibson's exact manipulation), the fit-gate-minus-structure gap grows monotonically (-0.103 -> -0.070 as
p: 0 -> 1) and the info-free twin never recovers -- i.e. thematic fit's relative value rises as structural
certainty falls, exactly the noisy-channel prediction. It does not CROSS structure because graded_role's
animacy cue survives corruption. A flat gap, or a recovering twin, would have been the real negative; neither
happened.

**The NATURAL noisy-parse test settles the redirect (`exp_grounded_role_noisy_parse_v1.py`).** I re-ran the
whole task through a REAL dependency parser (spaCy en_core_web_sm -- substrate-native, no LLM) instead of gold
parses: parse the raw clause text, use spaCy's structural roles (nsubj->agent, obj/nsubjpass->patient) as the
realistic "grammatical-function assigner", and transfer gold roles by lemma. Result: **spaCy's structural role
accuracy is 0.9959 aggregate and 0.9915 BALANCED on non-canonical (error rate 0.0041, 12 of 2962 items)** --
it essentially SOLVES non-canonical role assignment, dominating word order (0.938), the landed graded_role,
AND the fit gate (0.885, which HURTS here too). On the tiny natural parse-error subset (n=12) the fit gate does
recover (0.5 vs spaCy-structure 0.0, +0.5 [0.25,0.75]), but n is far too small for a twin-separated claim.
**So the non-canonical collapse the brief cites (0.288, measured on the reader's crude nltk front-end) is a
PARSE-QUALITY problem, not a thematic-fit problem: a modern parser resolves it without any plausibility cue.**
Thematic fit is decisive only when the parser is BOTH weak AND the item is structure-silent -- a small
intersection.

## THE WEAK-PARSER DEPLOYMENT REGIME (route A -- the powered result, and where the mechanism lives)

The clean-parse null is a regime artifact, so I tested the gate in the regime the brief's own 0.288 collapse
was measured in: role assignment read through the reader's OWN crude live front-end (noisy tokens/POS), on a
MODERN, ROLE-BALANCED gold (`role_balanced_comprehension_gold_v1`, built from QA-SRL EXPLICITLY because the
McGuffey gold is ~200 years old -- so NO age confound; positional floor 0.5). Patient-detection accuracy,
held-out by sentence, non-canonical (pre-verbal patient) n=1224 (`exp_grounded_role_weak_parser_v1.py`):

| arm | non-canonical (PRE) | canonical (POST) |
|---|---|---|
| word order (floor 1) | 0.1487 | 0.8358 |
| landed graded_role (floor 2) | 0.1176 | 0.8154 |
| **fit gate** | **0.2745** | 0.6552 |
| info-free twin | 0.2222 | 0.7042 |

**Here the fit gate DOES what the brief asked, with power:** on the non-canonical subset it beats BOTH named
floors CI-separated -- word order +0.126 [0.102, 0.149] and the structural assigner +0.157 [0.130, 0.186] --
with the info-free twin LOSING +0.052 [0.025, 0.078]. On the noisy front-end the structural assigner COLLAPSES
on non-canonical (0.118, its passive detection needs clean participle/aux tokens the front-end mangles), so
thematic fit is the only signal that recovers those roles -- exactly the disambiguation-under-uncertainty
prediction, now demonstrated on modern text with n=1224.

**But the no-regression clause fails, and the failure is IRREDUCIBLE.** The gate regresses canonical (0.655 vs
word order 0.836), and a full tau sweep (0.5..3.0) shows NO threshold that beats the non-canonical floor while
preserving canonical: at tau=1.0 non-canonical +0.157 over structure but canonical -0.16; at tau=3.0 canonical
recovers to 0.809 but non-canonical drops below the structural floor. **Reason (enumerated, per the bar):
thematic fit ALONE cannot distinguish "word order is misleading here" (a real non-canonical clause) from "word
order is right but the agent is atypical" (a canonical clause with an unusual-but-correct agent). The reliable
disambiguator between those two is the PARSE -- which on the weak front-end is exactly what is broken. So the
gate trades canonical for non-canonical at a fixed rate; it cannot separate the two populations without the
structural signal it is trying to compensate for.** This is the bar's P2 (rigorous-negative) full-PASS
condition, met with power. The clean fix is not a better gate -- it is a better parser (see spaCy, above).

## GENERALIZATION (asked explicitly; measured in BOTH regimes -- the honest, quantified answer)

**In the weak-parser regime the gate GENERALISES to held-out UNSEEN (verb,noun) pairs** (the OOV regime the
owner names as where the brain wins), n=299: gate 0.2308 beats word order (+0.067 [0.020, 0.114]) and the
structural assigner (+0.054 [0.003, 0.107]) CI-separated -- a pure memoriser would collapse to chance on unseen
pairs; it does not. HONEST bound: the gate's edge over its INFO-FREE TWIN does NOT survive to unseen pairs
(+0.023 [-0.027, 0.074], CI includes 0) -- i.e. the count-based fit's genuine signal is largely seen-pair
memorisation.

**I then pushed HARD on WHY the fit signal generalises poorly -- 8 fit-vector methods, TWO brain-research
drills, and a MEASUREMENT-ARTIFACT correction against myself. The reconciled truth (this is the fully-understood
version; `exp_grounded_role_protofit_generalize_v1.py`, `exp_grounded_role_knn_fit_v1.py`,
`exp_grounded_role_feature_fit_v1.py`, `research_feature_based_role_generalization` + `research_thematic_fit_ceiling_reconciliation`):**

- **A MEASUREMENT ARTIFACT I caught and corrected.** An intermediate probe reported "GloVe predicts role at
  0.51 = chance on OOV nouns, so distributional CANNOT generalise role". That was wrong two ways: the gate eval
  has a swap-helps-on-passives confound, and the direct probe used an UNBALANCED logistic on 22%-agent data
  (it predicted the majority class -> artificial 0.5 balanced accuracy). With a BALANCED classifier and
  balanced accuracy on held-out OOV nouns, GloVe verb-conditioned generalises role at **0.65** (noun-only
  0.59), beating its info-free twin (0.48). **Distributional DOES carry generalising role signal** (largely
  animacy/semantic-type, which GloVe encodes). I withdraw the earlier "distributional is role-inaccurate" claim.
- **A quick WordNet FEATURE vector (animacy + IS-A concreteness + supersenses) did NOT beat GloVe** on OOV
  (0.51-0.57 vs 0.65). So the second drill's STRONG claim -- "grounded features >> distributional, bag-of-words
  is weak" -- is OVERSTATED: the MECHANISM (McRae feature/prototype, verb-keyed, generalises via inferred type;
  GEK; ATL feature integration) is PINNED and stands, but no published result (and not my data) shows grounded
  norms beat 300-d embeddings on OOV role, and LREC-2020's actual conclusion is that reliable SYNTAX is the
  determinant, not grounded features. GloVe-0.65 is CONSISTENT with the field's modest thematic-fit ceiling
  (graded benchmarks sit ~0.4-0.7 for tuned embeddings, structured DMs, and BERT alike).

**THE LOAD-BEARING, CONVERGENT FINDING: most thematic-role information is STRUCTURAL, not noun-intrinsic.**
Animacy-alone 0.54, the best noun-side representation (GloVe) 0.65 -- the argument-alone signal is near a
MODEST CEILING regardless of representation (feature or distributional). This is not a fit-vector engineering
gap; it is a fact about where role information lives, and it converges with the Competition Model (English is
order/structure-dominant), the reversible-sentence literature, this problem's own parser result (spaCy
structural roles 0.996), and the weak-parser result (fit earns its keep only as a competition-gated TIE-BREAKER
where structure is silent). So: verb-conditioned GloVe is an ADEQUATE fit signal near its ceiling; the lever is
STRUCTURE (a better parser + the conflict gate), NOT a richer fit vector. This is CONVERGENCE with a specific
reason (the noun-side ceiling), not engineering exhaustion -- and it withdraws the earlier "build a grounded
role-tuned space to close the gap" recommendation as low-headroom (a flat result over GloVe is the likely
outcome; if ever tried, the SOTA axis is a syntax-TYPED distributional prototype, not a hand-built grounded vector).

The count-based selectional-preference fit MEMORISES (verb,noun) pairs. The McRae-faithful generalising form
is similarity-to-role-PROTOTYPE (centroid of typical role-fillers), which should transfer to unseen arguments
by distributional similarity. I built it (`_grounded_role_protofit.py`: PPMI+SVD embeddings from UD-EWT ->
per-(verb,role) prototype centroids -> cosine-difference fit). Findings:
- The prototype fit is MUCH cleaner on canonical (0.976 vs the count gate's 0.887) -- it false-conflicts far
  less on plausible-but-atypical agents, so it preserves word order where it should.
- BUT on UNSEEN (verb,noun) non-canonical pairs it did NOT beat the count model (0.36 vs 0.68) with the
  current small in-domain embeddings. **The fit-vector QUALITY is the bottleneck** -- exactly the brief's own
  dependency note (fit vectors are supplied best by `distributional_meaning_channel`; the PoC/this work use a
  weaker in-domain proxy). This is a named, buildable next step, not a ceiling.

## What I would WITHDRAW FIRST if it turned out to be wrong

The thinnest claim is the gate's edge over its info-free twin ON UNSEEN pairs (+0.023 [-0.027,0.074]) -- it
does not survive, and I report it as not surviving, not as a win. On clean parses the thinnest positive was
fit>twin on balanced non-canonical (+0.150, lower bound 0.002, resting on 10 agent items) -- also not something
I would defend hard. The STURDIEST results, which I would defend hardest: (a) the weak-parser non-canonical
wins -- fit gate beats word order +0.126 [0.102,0.149] and the structural assigner +0.157 [0.130,0.186],
n=1224, twin losing +0.052 [0.025,0.078]; (b) the irreducible canonical tradeoff (a full tau sweep, not one
point); (c) the clean-parse routing aggregate win (+0.049/+0.081, n=3591); (d) spaCy structural roles 0.9959.

## KEY REALIZATIONS (the moves that unstuck this)

- **The gold-parse null is a regime artifact PREDICTED by the theory, not a ceiling.** Reading the brain
  literature BEFORE grinding gate variants told me thematic fit is a disambiguation-under-uncertainty
  mechanism; a gold parse removes the uncertainty, so measuring fit on clean parses measures the wrong
  regime. This reframed a "failure" into an expected null and produced the corruption-curve test.
- **The strongest floor on a passive-dominated non-canonical subset is the majority-class CONSTANT
  (always-patient 0.958), not word order.** The named floors are almost unbeatable on RAW accuracy for a
  degenerate reason; BALANCED accuracy is the honest metric.
- **The "structural" assigner is not structure-only -- it hides an animacy plausibility cue.** The right
  control is not "structure vs fit" but "coarse plausibility (animacy) vs rich plausibility (thematic fit)",
  and on clean parses the coarse cue is already good enough that rich fit cannot CI-separate from it.
- **The aggregate win is ROUTING, not fit** -- caught by the decisive route_only control (strong-passive
  routing with the fit deleted still scored 0.986). Without that control I would have wrongly credited the
  fit gate for a win that came from cue-recruitment precision.
- **Conflict-validity must be a GATE, not a weight, AND its recruitment trigger must be a HIGH-VALIDITY cue.**
  A fit gate whose trigger is "any fit-vs-order conflict" hurts canonical because structure-silent canonical
  vastly outnumbers structure-silent non-canonical; a trigger of "reliable strong markedness" does not.
- **Test the mechanism in the regime it is FOR.** Switching from clean gold parses to the reader's own weak
  front-end flipped the fit gate from "adds nothing" to "beats both floors on non-canonical, CI-separated,
  n=1224, and generalises to unseen pairs" -- the same gate, a different regime. The clean-parse null was not
  a property of the gate; it was a property of the test.
- **Thematic fit cannot SUBSTITUTE for a parse; the canonical/non-canonical tradeoff is irreducible for a
  gate-alone.** Fit can't tell "order is misleading" from "order is right, agent is atypical" -- only the parse
  can -- so a fit gate compensating for a broken parser trades canonical for non-canonical at a fixed rate. The
  lesson: fix the PARSE (a modern parser scores 0.996) and reserve thematic fit for the residual it genuinely
  disambiguates, rather than asking it to do the parser's job.

## AUDIT UPDATE (for notes/BRAIN_FOUNDATIONAL_AUDIT.md, CAUSATION/role + Competition-Model entries)

- The landed `graded_role_assigner` is correctly a Competition-Model conflict-gated assigner, BUT it embeds an
  ANIMACY cue that functions as a coarse thematic-fit / plausibility signal. Any future "add thematic fit"
  work must be scored against structure+ANIMACY, not structure-only, or it will over-credit fit.
- `graded_role_assigner` over-recruits its structural override on CLEAN gold parses: it false-fires on 319 of
  3353 canonical items (all wrong), driving its aggregate BELOW pure word order (0.905 vs 0.937). The false
  fires are dominated by `gap_config` firing on a subject-with-modifier + a clausal complement, and by the
  weak bare-participle path. Restricting the override trigger to RELIABLE strong-passive markedness
  (route_only) recovers this (+0.081 aggregate, CI-sep) -- a landable precision fix (proposed diff below).
- PINNED update: thematic fit is a disambiguation-under-UNCERTAINTY cue (Trueswell 1994; Gibson 2013), not an
  override-certain-structure cue. Its measured value here is confined to the structure-silent residual and
  scales with structural corruption (monotone gap). Evaluating role organs on GOLD PARSES structurally hides
  this cue's contribution.

## PROPOSED hdlab CHANGE (Q111: strategy lands it; a proposed diff, not a landed one)

Two independent, separable changes:

1. **Precision fix to `hdlab/graded_role_assigner.hybrid_role_patient` (high-confidence, CI-backed).** Gate
   the structural override on RELIABLE markedness only. Concretely: keep the override for `precise_passive` /
   strong `voice_cues` (vc_strong/get/being/bypp) and a genuine object gap, but do NOT let the weak/ambiguous
   paths flip a canonical order-reading. Measured effect on this gold: aggregate 0.905 -> 0.986, CI-separated,
   canonical 0.905 -> 0.997, no reversible regression. This is the `route_only` arm. It is the brain-faithful
   move (recruit a cue in proportion to its validity) and it is the real fix for the non-canonical collapse
   that does NOT depend on thematic fit.
2. **Thematic-fit cue: DEFER pending better fit vectors.** Do NOT add the verb-keyed count fit as an always-on
   cue -- it net-hurts (canonical/reversible regression) and does not CI-separate from the existing animacy
   cue. It should be added ONLY as a residual-recruited cue AND only once the fit vectors come from the built
   `distributional_meaning_channel` (or a stronger embedding), which the generalization result shows is the
   bottleneck. Re-evaluate against structure+animacy, on BALANCED accuracy, and ideally in a structure-
   degraded (noisy-parse) regime where the residual is large enough to power a CI-separated test.

## ADJACENT COMPONENTS (evaluated for brain-fidelity + optimization, per the deepening checklist)

- **`hdlab/animacy_lexicon` (the hidden plausibility cue).** Brain-fidelity: animacy IS a pinned, early role
  cue -- legitimate. Optimization: it is a LOOKUP (the migration SOLVED notes it collapses 0.706 -> 0.124 on
  modern entities). It is doing coarse thematic-fit work; a graded, generalizing animacy/concreteness read
  (from the grounded hub) would both raise its own coverage and be the natural carrier for richer thematic
  fit. Candidate follow-on.
- **`hdlab/distributional_meaning_channel` (the fit-vector source).** Brain-fidelity: it is substitutability-
  scoped and explicitly NOT a general similarity read-out; my prototype fit needs role-filler SIMILARITY, a
  different projection. The generalization bottleneck here is that we lack a clean, general noun-similarity
  space for role prototypes. Candidate follow-on: a role-fit-tuned embedding.
- **The parse front-end.** The whole finding is that fit's value lives where the PARSE is uncertain. The live
  reader's noisy front-end (where the 0.288 collapse was measured) is that regime; a gold parse is not. The
  highest-value next test is the fit gate ON THE NOISY READER PARSE, where structure-silent non-canonical is
  common enough to power the CI-separated test the clean gold cannot.

## TLDR (plain language)

Our reader works out "who did what to whom" mostly from word order, which breaks on sentences like "the town
was surrounded by troops." The obvious human fix is to also use plausibility -- a town cannot surround. I built
that plausibility "gate" the way the brain does it, and I checked it carefully. Two honest findings. First,
most of the fixable damage is repaired by a simpler change: only trust the grammar-based override when the
grammatical evidence is genuinely strong (a clear passive), and otherwise trust word order -- that alone lifts
the reader from 91-94% to 98.6% correct, with the plain sentences untouched. Second, the plausibility signal
itself only helps in the narrow set of hard sentences where the grammar gives no clear signal, and even there
the reader ALREADY had a crude plausibility cue (living-vs-nonliving) that does most of the job -- so the
richer plausibility signal I added is not yet measurably better than what was there, on clean textbook-quality
input. Crucially, this is exactly what the brain science predicts: people only lean on plausibility when the
grammar is unclear, so testing it on perfectly-parsed sentences hides its value. And the single most useful
thing I found: the reader's failure on these sentences is really a WEAK-GRAMMAR-READER problem -- when I ran
the same sentences through a good off-the-shelf sentence grammar-reader (no AI model, already allowed), it got
who-did-what right about 99.6% of the time and the whole problem nearly vanished. So the biggest win here is to
upgrade the reader's grammar front-end, not to bolt plausibility onto the weak one.

## QUESTIONS

None. (One judgment call flagged for the strategy session: I graded this PARTIAL rather than SOLVED because
the specific mechanism in the brief -- verb-keyed thematic fit beating the structural assigner on non-canonical
-- does not CI-separate on clean parses; the related routing fix DOES clear both floors on the aggregate. If
you read the bar's "rigorous NEGATIVE is a full PASS -- name why" clause as the operative one, this meets it.)

## NEXT STEPS (for the strategy session; I do not file problems -- Q113)

1. **HIGHEST LEVERAGE -- upgrade the reader's PARSE FRONT-END, not its role logic** (a ready-to-file
   brief is packaged at `FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md` in this folder; strategy lifts it into a
   new problem, Q113). The natural noisy-parse
   test shows a modern substrate-native parser (spaCy, no LLM) scores 0.9959 on this task and 0.9915 balanced
   on non-canonical -- it essentially solves the non-canonical collapse (0.288 -> ~0.99) that this whole
   problem line targets, dominating word order, the landed graded_role, AND the thematic-fit gate. The
   reader's crude nltk front-end is the actual bottleneck. This is admissible (spaCy is not an LLM) and is a
   far larger win than any role-assignment tweak. Candidate flagship follow-on.
2. Land the precision fix to `graded_role_assigner` (route_only: reliable-markedness-only override). CI-backed
   (+0.081 aggregate), independent of thematic fit -- worthwhile if the nltk front-end is kept.
3. Re-test the thematic-fit gate ONLY in a genuinely WEAK-parser regime (the reader's nltk front-end), where
   the structure-silent residual is large enough to power a CI-separated non-canonical test -- but note (1):
   if the parser is upgraded, that residual shrinks to ~0.4% and thematic fit is largely redundant.
4. Do NOT invest in a richer fit vector as the lever. The reconciled generalization study (8 methods + 2
   drills) shows the noun-side thematic-fit signal is near a MODEST ceiling (~0.65 balanced OOV) regardless of
   representation, because most role information is STRUCTURAL, not noun-intrinsic; grounded features have no
   proven headroom over verb-conditioned GloVe. Keep verb-conditioned GloVe as an adequate tie-breaker fit
   signal; spend effort on structure (parser + conflict gate). If a fit upgrade is ever tried, the evidence
   points to a syntax-TYPED distributional prototype (SDM-style), not a hand-built grounded feature vector.

---

## INTEGRATED_BY_STRATEGY — 2026-08-30 (grade: STRONG; SOLVED owner-DONE)

Integrated by strategy. Reverified FIRST-HAND: `verification/test_grounded_role_gate_organ.py` **14/14 PASS** (scaffold-free). A rigorous NEGATIVE + strategic REDIRECT: the brain-faithful noisy-channel gate was built, and the TWO-REGIME result refutes the brief's thematic-fit premise with power — CLEAN-PARSE: structural ROUTING owns the aggregate (route_only 0.9858 beats word-order +0.049 / graded_role +0.081 CI-sep, no canonical/reversible regression; fit does not CI-separate from graded_role); WEAK-PARSER deployment: the fit gate beats both floors on non-canonical (+0.126/+0.157) + generalizes to unseen pairs, twin losing, BUT the canonical tradeoff is IRREDUCIBLE (P1 fails, the P2 rigorous-negative clause met with power). Real fix = PARSE QUALITY (spaCy structural roles 0.9959 dominate; the brain-faithful target is the incremental cue-integrated predictive structure-builder). Honest self-correction (count-fit = seen-pair memorization, twin edge doesn't survive to unseen). Strong controls (structure-shuffle twin loses; the Gibson corruption-curve signature; independent derivation).

**STRATEGY ACTIONS:**
1. **hdlab landing QUEUED (Q111):** the routing PRECISION FIX to `graded_role_assigner` — restrict the structural override to RELIABLE strong-passive markedness only (drop the weak bare-participle override) → +0.081 aggregate CI-sep, fit-independent, no regression. ⚠️ Needs an END-TO-END live-reader validation FIRST (the solver's own phase-gate trap: measure on the live reader, not in isolation) — a careful default-safe landing, not inline. Recorded in the wire-don't-island debt.
2. **The PARSE-QUALITY REDIRECT + `FOLLOW_ON_PROPOSAL_parse_frontend_upgrade.md` FEED p1 `the_extraction_front_end_recovers_only_a_third_of_events_and_roles`** (in-progress). The p3 finding IS p1's diagnosis: the non-canonical role collapse is PARSE-QUALITY, spaCy (no LLM) is the admissible-interim ceiling (0.9959), and the brain-faithful target is the incremental cue-integrated predictive structure-builder (Lewis-Vasishth/MacDonald/Levy — order+morphology+fit competing DURING attachment). NOT packaged as a separate problem (overlaps p1; queue healthy); the FOLLOW_ON_PROPOSAL is ready-to-lift IF p1's diagnosis confirms the incremental parser is a distinct build.

**Audit §2b folded** (thematic-fit role assignment is a REGIME artifact — on clean parses structure/routing owns it, on weak parses the post-hoc fit gate has an irreducible canonical tradeoff; the non-canonical collapse is PARSE-QUALITY; the brain-faithful fix is the incremental cue-integrated predictive structure-builder — relocate fit to ONLINE attachment). FENCED dead-ends (do NOT re-open): thematic-fit fit-vector work, the post-hoc fit gate, fused-always/linear-sum/precision-weighted. Review (STRONG) + `> ## ✅ SOLVER REVIEW` block in PROBLEM.md; `priority:` cleared.
