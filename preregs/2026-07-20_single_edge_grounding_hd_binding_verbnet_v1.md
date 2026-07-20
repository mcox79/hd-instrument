# PRE-REG: Single-edge substrate-native grounding via HD binding (VerbNet-sourced), v1

Date: 2026-07-20
Cell: experiments/exp_single_edge_grounding_hd_binding_verbnet_v1.py
Anchor: single_edge_grounding_hd_binding_verbnet_v1
Author: hdi_exp_dev (USER's proposed minimal definitive existence proof of grounding)
Queue: LOCAL foreground-to-completion (deterministic closed-form measurement, <1s wall; NO queue;
  NO push; NO remote-persist; DESIGN + SMOKE ONLY per task contract -- no full dispatch requested or
  possible beyond what smoke already runs, see Compute architecture)

## WHAT / WHY

The atomic single-EDGE plausibility proof (USER framing). Take a documented reader failure mode
(who-is-affected / thematic-role ambiguity between a creation-verb's true patient and a locative
PP-adjunct), look up ONE structured fact that resolves it (real NLTK VerbNet class membership +
thematic-role evidence for the creation-verb class), STORE that fact SUBSTRATE-NATIVE as an HD
binding (`hdlab.binding.bind`, NOT a dict), and show the ambiguity resolves via UNBIND + CLEANUP --
AND generalizes to held-out same-verb-class sentences never stored, while a wrong/irrelevant edge
does NOT resolve it, and a sentence-specific (memorization-style) key does NOT generalize the way a
verb-class key does.

## PRIOR-WORK CHECK (mandatory, USER-locked 2026-07-01)

`bash tools/substrate_query.sh "single-edge grounding HD binding role-filler VerbNet selectional
preference generalization creation-verb patient PP-attachment"` -> top hit cosine=0.3096
(`notes/research_drill_natural_analog_immune_DEEPER_3x_2026-06-07.md`, a two-class surface-vs-
load-bearing BINDING-DECAY architecture for immune-system OAS mitigation -- about binding
*persistence/decay tagging*, not role-filler storage or verb-class selectional preference).
Second hit cosine=0.3057 is the generic WordNet concept "sectionalization" (irrelevant). Both read
in full; neither is a prior instance of this design. **No prior arc cell at cosine>0.30 tests
single-edge role-filler HD-binding grounding with a VerbNet-sourced lookup + generalization/must-fail
guards. Genuinely novel synthesis of already-adopted machinery (binding/cleanup primitives +
VerbNet lookup already used in the 29375 affectedness cell), not a rediscovery.**

## RELATION TO PRIOR ATOMS (context, not duplication)

- Atom 29375 (`exp_affectedness_change_of_state_patient_selection_design_gate_v1`) VET'd that
  NO self-supervised TEXT-INTERNAL signal correlates with gold patient-correctness for this exact
  reader failure class (6 signal families failed the same residual). That result licenses the
  premise here: "the reader" has ZERO selectional-preference signal pre-storage (a VET'd null, not
  an assumption) -- operationalized below as an exact-zero-margin baseline, not a strawman.
  Note: 29375 measured signals scored OVER THE READER's OWN candidate extraction (NEST pipeline);
  this cell does not re-invoke that heavy pipeline (sklearn clause-classifier, McGuffey corpus) --
  it isolates the STORAGE+RECALL+GENERALIZATION question on a small hand-authored sentence set with
  the identical failure structure (WITHIN-FRAME over-extraction: true created-object patient vs a
  locative PP-adjunct), which is the atomic question this task asks for.
- 29368 (learned codebook) / 29376-78 (reliability gate / common-mode) establish the "reshape
  concepts into codebook, bind facts into the web" split (`notes/research_plausibility_web_
  engineering_resources_adoptable_foundation_2026-07-20.md` REPRESENTATION MAPPING section). This
  cell IS that "bind facts into the web" half, at the smallest possible scale (one edge).
- 29379-82 (novel-atom generalization): established that FORMAT-only random codes suffice for
  algebraic bind/unbind (the binding step is free once encoded), and that generalization to unseen
  ATOMS is the genuine open question. This cell's filler-TYPE codes are hand-assigned (stipulated,
  not learned) -- deliberately: this cell isolates STORAGE-FORMAT + RECALL + verb-CLASS
  generalization, not novel-noun generalization (a separate, already-tracked question in 29379-82).

## THE LOOKED-UP EDGE (real, inspectable, independent of eval gold)

Source: NLTK VerbNet (`nltk.corpus.verbnet`, already used and confirmed working in the 29375 cell).
`vn.classids('build') == ['build-26.1-1']` (Levin ch.26 Create+Transform). `vn.vnclass('build-26.1')`
THEMROLES lists a `Product` role (the created object) alongside `Agent`/`Material`/`Beneficiary`/
`Asset` -- **the existence of a distinct "Product" role, together with the class's own frame
semantics (`made_of(result(E), Product, Material)`, i.e. the created thing comes into existence as a
concrete made-of-material object) is the real, inspectable, VerbNet-sourced fact under test: build-
class (creation) verbs license a created-ARTIFACT direct-object role, structurally distinct from a
locative/path role.** Honest caveat: VerbNet's own `SELRESTRS` field on `Product` is empty in this
frame (VerbNet does not numerically tag "concrete artifact" on the created-object role); the
"artifact-type" interpretation is the standard Dowty(1991)/Levin(1993) reading of a creation-class
Product role, not a literal VerbNet selrestr value -- stated here so this is not overclaimed as a raw
VerbNet field. `eat-39.1` (used ONLY as a different-class wrong-edge control) is looked up the same
way (`vn.classids('eat') == ['eat-39.1-1']`) but its THEMROLES in this NLTK dump list only
`Agent`/`Source` (no explicit `Patient`/theme role in this particular frame) -- so the eat-edge's
"food/ingestible" filler-type preference is asserted from ordinary lexical semantics (an ingestion
verb's direct object is edible substance), NOT fetched from a VerbNet selrestr field. This is stated
explicitly so the two edges are not conflated in rigor: **the PRIMARY edge under test (build ->
created-artifact) is VerbNet-role-sourced; the CONTROL edge (eat -> food) is common-sense-sourced**,
used only to test specificity/superposition, not as a second instance of "the" claim.

## SENTENCE SET (hand-authored, clean, small; independent of the lookup source -- no ground-by-X)

Gold judgment (which NP is the TRUE patient in each sentence) is the annotator's own reading of
ordinary English argument structure (agent-verb-direct-object vs locative PP-adjunct) -- a
structural/semantic fact about the SENTENCE, independent of the noun-type lexicon used to build
filler-type codes (a general VOCABULARY classification, not a per-sentence answer key). These are two
different information sources; their empirical correlation is exactly the claim under test, not a
circularity.

BUILD-CLASS (creation, build-26.1):
- **T1 (stored/train item):** "The girl built a fort by the river." true_patient=fort (ARTIFACT),
  false_candidate=river (LOCATION).
- **G1 (held-out, never stored):** "He built a cabin near the lake." true=cabin (ARTIFACT),
  false=lake (LOCATION).
- **G2 (held-out, never stored):** "They built a bridge across the valley." true=bridge (ARTIFACT),
  false=valley (LOCATION).

EAT-CLASS (ingestion, eat-39.1 -- used ONLY for the wrong-edge / cross-verb specificity check; NEVER
used to train the build-edge):
- **X1:** "She ate the soup in the kitchen." true=soup (FOOD), false=kitchen (LOCATION).
- **X2:** "He ate the bread near the barn." true=bread (FOOD), false=barn (LOCATION).

Noun -> filler-TYPE lexicon (independent, general-vocabulary; disjoint concern from per-sentence
gold): {fort, cabin, bridge, dam, house, hut} -> ARTIFACT; {river, lake, valley, kitchen, barn,
garden} -> LOCATION; {soup, bread, cake} -> FOOD.

## STORAGE ENCODING (substrate-native HD binding -- the crux; proof-of-not-a-dict below)

FHRR (complex64, unit-modulus phasors, `hdlab.atoms.make_atom_fhrr`; bind = elementwise complex mul,
unbind = elementwise mul by conjugate, both via UNMODIFIED `hdlab.binding.bind/unbind`). N_DIM=1024
(project default), fixed seed 20260720, `torch.Generator().manual_seed(...)` (no `hash()`-derived
seeding, PROT-023 compliant).

Atoms (all via `atoms.make_atom_fhrr`): `ROLE_PATIENT`, `VC_BUILD`, `VC_EAT` (verb-CLASS atoms),
`TYPE_ARTIFACT`, `TYPE_LOCATION`, `TYPE_FOOD` (filler-type atoms -- the cleanup codebook), plus 5
per-sentence identity atoms `SENT_KEY_{T1,G1,G2,X1,X2}` (used ONLY by the memorization-control arm
below, representing "if we keyed storage by sentence identity instead of verb-class").

Keys (bound once, reused everywhere a verb-class is queried):
`KEY_BUILD = bind(VC_BUILD, ROLE_PATIENT)`; `KEY_EAT = bind(VC_EAT, ROLE_PATIENT)`;
`KEY_SENT_x = bind(SENT_KEY_x, ROLE_PATIENT)` for each sentence x (memorization-control only).

Storage WEBS (each a single `torch.Tensor` shape `(N_DIM,)` dtype `complex64` -- NEVER a dict; a
`safe_append_atom`/dict-lookup implementation is structurally impossible here since the only object
type in the storage/recall path is a bound/bundled HD vector; self-test asserts `type(web) is
torch.Tensor` for every arm):
- `WEB_EMPTY = zeros(N_DIM, complex64)` -- the pre-storage / no-edge condition.
- `WEB_BUILD_EDGE = bind(KEY_BUILD, TYPE_ARTIFACT)` -- the single stored edge under test.
- `WEB_EAT_EDGE_ONLY = bind(KEY_EAT, TYPE_FOOD)` -- wrong/irrelevant-edge control (no build edge at
  all).
- `WEB_BOTH_EDGES = WEB_BUILD_EDGE + WEB_EAT_EDGE_ONLY` -- genuine SUPERPOSITION (bundle) of two
  facts in ONE vector; the decisive "not a single-slot dict" proof (a dict has O(1) exact per-key
  storage by definition; a bundle must tolerate cross-talk noise from co-stored facts, which is
  measured explicitly below).
- `WEB_MEMORIZATION = bind(KEY_SENT_T1, TYPE_ARTIFACT)` -- sentence-specific key control (T1's own
  identity atom, not its verb-class) -- the memorization-vs-generalization contrast arm.

## RECALL + SOLVE (unbind + cleanup, real substrate primitives, no invented math)

For sentence item i with verb-class key `K_i` (either `KEY_BUILD`/`KEY_EAT` for the class-keyed arms,
or `KEY_SENT_i` for the memorization arm) and web `W`:
`recovered = unbind(W, K_i)` (unmodified `hdlab.binding.unbind`).
For each candidate noun c (true or false), `type_vec(c)` = its TYPE atom per the lexicon.
`score(c) = hdlab.atoms.similarity(recovered, type_vec(c))` (unmodified `hdlab.atoms.similarity` --
real part of the normalized conjugate inner product; this IS the cosine-cleanup readout, applied via
the existing complex-safe primitive rather than `hdlab.cleanup_family.k_NN_lookup`, whose PRIMITIVES
cast to float32 and would silently drop FHRR's imaginary part -- using `atoms.similarity` keeps the
cleanup step correct for complex64 while remaining 100% existing substrate machinery, zero invented
math). `margin(i) = score(true) - score(false)`; `predicted = argmax`. An explicit k=1 nearest-
neighbor cleanup against the 3-entry TYPE codebook (`{TYPE_ARTIFACT, TYPE_LOCATION, TYPE_FOOD}`) is
also run and logged (same `atoms.similarity` primitive, argmax over the full codebook, not just the
2 candidates) as the "verified substrate binding op" recall step.

FHRR analytical prediction (declared before running, `THEORETICAL@`): since FHRR atoms are exactly
unit-modulus per component, `unbind(bind(a,b), a) = a * b * conj(a) = |a|^2 * b = b` EXACTLY (up to
float32 rounding) for a single-fact web -- so `WEB_BUILD_EDGE` queried with `KEY_BUILD` recovers
`TYPE_ARTIFACT` exactly, giving `score(true=ARTIFACT)~1.0`, and `score(false=LOCATION)` ~ a random
near-orthogonal cross term with expected magnitude ~0, std ~`1/sqrt(N_DIM)`~0.03 at N_DIM=1024 ->
`margin ~ 0.94-1.03`. For `WEB_BOTH_EDGES`, an additional independent cross-talk term of similar
magnitude (~0.03) is added from the co-stored eat-fact -> margin still expected ~0.9-1.06. Querying
the WRONG class-key against a web that doesn't contain that class's fact recovers pure noise
(expected `margin ~ 0 +/- 0.03-0.06`). These are wide, well-separated predictions (not close calls);
MEASURED values are printed and logged at self-test/smoke, not assumed.

## DESIGN-GATE (verified at smoke, BEFORE any full; this cell has no separate full -- see Compute
architecture)

1. **difficulty_on:** `WEB_EMPTY` margin == 0.0 EXACTLY on all 5 items (zero signal; the reader
   genuinely cannot resolve any of the 5 ambiguities without a stored edge -- not a strawman: this
   operationalizes the VET'd null from atom 29375, "no self-sup text signal for patient selection").
2. **store_is_real_binding_not_dict:** every web is `type(...) is torch.Tensor`, shape `(N_DIM,)`,
   dtype `complex64`; `arms_differ_verified` hash-check across all 5 webs (bit-distinct); the ONLY
   functions touching storage/recall are `hdlab.binding.bind/unbind` + `hdlab.atoms.similarity`
   (grep-verified in self-test: no `dict`/`{}` keyed by verb-string appears in the store/recall path).
3. **generalization_is_genuine:** G1/G2's sentences/nouns are NEVER used to construct any web (only
   T1 contributes to `WEB_BUILD_EDGE`'s TYPE_ARTIFACT value; G1/G2 are queried post-hoc with the SAME
   `KEY_BUILD`, which only exists because it encodes the verb CLASS, not sentence identity).
4. **wrong_edge_must_fail_fires:** `WEB_EAT_EDGE_ONLY` (irrelevant edge) must NOT resolve T1/G1/G2;
   `WEB_BUILD_EDGE` must NOT resolve X1/X2 (specificity, both directions).
5. **lookup_independent_of_gold:** the VerbNet class-membership lookup and the noun-type lexicon are
   both independent of the per-sentence "which NP is the patient" gold judgments (see SENTENCE SET
   section); no field of one is derived from the other.
6. **one_variable:** the ONLY thing that differs between arms is the CONTENTS of the web (which
   edge(s) are stored, and whether the key is class- or sentence-scoped); the recall procedure
   (`unbind` + `atoms.similarity` argmax) is byte-identical code across all 5 arms.

## BANDS (pre-registered; NOT tuned to pass -- FHRR unbind is exact single-fact recovery, so these
thresholds have wide analytical headroom per the THEORETICAL prediction above)

`MARGIN_THRESH = 0.10` (a candidate is "resolved correct" iff `predicted == true_patient AND
margin >= MARGIN_THRESH`; note the analytical prediction puts true margins near 0.9-1.0, so 0.10 is a
conservative floor, not a tuned-to-pass threshold).

**HARD_PASS_SINGLE_EDGE_GROUNDING (ALL must hold):**
1. `WEB_EMPTY` margin == 0.0 on all 5 items (difficulty genuinely on).
2. `WEB_BUILD_EDGE` resolves T1 (the stored item) correct, margin >= 0.10.
3. `WEB_BUILD_EDGE` resolves BOTH G1 and G2 (held-out, never-stored, same verb-class) correct, margin
   >= 0.10 each (**generalization** -- the decisive USER-requested guard).
4. `WEB_BUILD_EDGE` does NOT resolve X1 or X2 correct-with-margin (specificity: build-edge does not
   leak into eat-sentences) AND `WEB_EAT_EDGE_ONLY` does NOT resolve T1/G1/G2 correct-with-margin
   (irrelevant-edge control: storing eat->food does not help build sentences) (**wrong-edge
   must-fail** -- the decisive USER-requested guard).
5. `WEB_BOTH_EDGES` resolves ALL 5 items correct, margin >= 0.10 each (genuine multi-fact
   superposition tolerates cross-talk; this is the "not a single-slot dict" proof in outcome, not
   just in object-type).
6. `WEB_MEMORIZATION` resolves T1 correct (margin >= 0.10) but FAILS G1 AND G2 (margin < 0.10 or
   incorrect) (**memorization-vs-generalization contrast**: sentence-scoped key reuse does NOT
   transfer to new sentences the way class-scoped key reuse does -- directly operationalizes "if it
   only solves the exact stored sentence, that's memorization").
7. Recall verified as a genuine binding/unbind/cleanup op (design-gate item 2 above), not a dict.

**HARD_FAIL_SINGLE_EDGE_GROUNDING (ANY ONE is sufficient):**
1. `WEB_EMPTY` margin != 0 on any item, OR any item is already resolved pre-storage (difficulty not
   on -- test-design flaw, not a capability result).
2. `WEB_BUILD_EDGE` fails to resolve T1 (the store/recall mechanism itself is broken).
3. `WEB_BUILD_EDGE` fails BOTH G1 and G2 (zero generalization -- pure sentence memorization, the
   USER's named decisive failure mode).
4. `WEB_EAT_EDGE_ONLY` DOES resolve any of T1/G1/G2 correct-with-margin (any-storage-helps -- storing
   an unrelated fact "solves" an unrelated ambiguity, meaning the mechanism is not selective) OR
   `WEB_BUILD_EDGE` DOES resolve X1 or X2 correct-with-margin (specificity violated).
5. Any web is found to be, or to route through, a Python `dict`/hash-map keyed by verb or sentence
   identity rather than a bound HD vector (mechanism-integrity failure -- "secretly a dict lookup").

**MIDDLE_BAND:** exactly one of G1/G2 generalizes (not both), or a margin lands in [0.05, 0.10)
(borderline resolution) on an otherwise-passing item -- informative partial capability, not a clean
HARD_PASS.

## CELL-TEMPLATE MANDATORY declarations

- `arms_differ_verified: true` (hash-check across the 5 webs, computed at self-test + smoke).
- `final_metrics_atomicity: "tmp_replace"` (os.replace).
- `except SystemExit: raise` BEFORE `except Exception` (no bare/`BaseException`).
- `crlb_n/a`: "categorical resolved/not-resolved margin-threshold metric over an exact-recovery FHRR
  binding; no argmax-capacity CRLB formula applies (this is not a bundle-capacity sweep). The
  THEORETICAL section above is the applicable closed-form analysis (exact single-fact recovery +
  O(1/sqrt(N_DIM)) cross-talk bound) and is reported as such."
- `baseline_in_band` (adapted from META_RULE_AG for a margin-metric, not a [0,1] score): `WEB_EMPTY`
  margin must be EXACTLY 0.0 (a genuine, verified zero-signal null), not merely "low" -- this is a
  stronger, more falsifiable version of the usual 0.05-0.95 in-band check, appropriate because this
  arm is a deliberately-constructed no-information control, not a difficulty-tuned baseline.
- `discriminator survives scale`: N/A in the usual smoke-vs-full sense (this cell has no scale axis;
  option (A) applies trivially -- smoke runs at the ONLY regime that exists, N_DIM=1024, the project
  default, not a reduced toy dimension).
- `cardinality_ok`: `EXPECTED_N_UNITS = 5 arms x 5 items x 2 candidates = 50` scored candidate-margins
  (not a sweep-axis cell in the K/depth/M/N sense, but the count is declared and checked).
- per-unit failure-class instrumentation: no bare `except`; a missing lexicon entry for any candidate
  noun raises (fails loud), never silently scores None/0.
- `deterministic_seeding: true` -- fixed int seed 20260720 via `torch.Generator().manual_seed()`; no
  `hash()`/`list(set())` ordering anywhere in the cell (PROT-023 compliant).
- all numbers in the cell/report tagged MEASURED@ / THEORETICAL@ / CITED@.

## Compute architecture

Class: (b) sequential-CPU with justification -- 5 webs x 5 items x 2 candidates = 50 similarity
scores over N_DIM=1024 complex64 vectors; wall time is sub-second (a handful of elementwise complex
multiplies and dot products, no training, no sweep, no GPU benefit at this scale). Storage:
`no_storage` in the PartitionedStore sense (in-memory HD vectors only, not persisted to
`data/substrate_index`). LOCAL foreground-to-completion. NO queue; NO push; NO remote-persist.
**This cell has no separate FULL mode**: it is a closed-form existence-proof measurement, not a
statistical sweep needing more seeds/scale to be decisive (FHRR recovery is exact; margins are
governed by an analytical bound, not sampling noise) -- `--smoke` runs the entire item set and IS the
decisive result. Per the task contract (design + smoke only, no full run, no queue_add, no push),
no further dispatch is requested.

## Deflated confidence

This is an ENGINEERING RECOMBINATION of already-adopted, already-VET'd machinery (FHRR bind/unbind,
`atoms.similarity`, real NLTK VerbNet lookup used identically in atom 29375), not novel research --
per the standing lit-scan/novel-synthesis calibration this does not need the 0.15-0.25 deflation
applied to a literature-scan P estimate; the analytical FHRR-exact-recovery prediction is a
closed-form guarantee, not a hypothesis. The open empirical question is narrowly: does the
hand-authored sentence set's structural properties (candidate word choices, lexicon coverage)
actually realize the design as specified, and does the memorization-contrast arm behave as predicted
-- both are MEASURED at smoke, not assumed.
